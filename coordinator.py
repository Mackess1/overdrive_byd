from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_TELEMETRY_TOPIC,
    CONF_AVAILABILITY_TOPIC,
    DEFAULT_TELEMETRY_TOPIC,
    DEFAULT_AVAILABILITY_TOPIC,
)

_LOGGER = logging.getLogger(__name__)


class OverdriveBYDCoordinator(DataUpdateCoordinator):
    """Receive OverDrive telemetry from MQTT.

    OverDrive has used two telemetry layouts:
      1. Legacy: one JSON object on ``<base>``.
      2. Current: one value per ``<base>/<key>`` topic.

    Supporting both keeps existing installs working while correctly handling
    current OverDrive MQTT publishing / Home Assistant discovery behaviour.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN)

        self.entry = entry
        self.telemetry_topic = entry.data.get(
            CONF_TELEMETRY_TOPIC,
            DEFAULT_TELEMETRY_TOPIC,
        ).rstrip("/")
        self.availability_topic = entry.data.get(
            CONF_AVAILABILITY_TOPIC,
            DEFAULT_AVAILABILITY_TOPIC,
        )

        self.data: dict[str, Any] = {}
        self.available = False
        self._unsub_telemetry: list[Any] = []
        self._unsub_availability = None

    async def async_setup(self) -> None:
        # Legacy aggregate JSON payload.
        self._unsub_telemetry.append(
            await mqtt.async_subscribe(
                self.hass,
                self.telemetry_topic,
                self._message_received,
                qos=0,
            )
        )

        # Current OverDrive format: <base>/<key> with one value per topic.
        # Use '+' instead of '#' so command topics such as
        # <base>/climate/mode/set are not mistaken for telemetry.
        self._unsub_telemetry.append(
            await mqtt.async_subscribe(
                self.hass,
                f"{self.telemetry_topic}/+",
                self._message_received,
                qos=0,
            )
        )

        self._unsub_availability = await mqtt.async_subscribe(
            self.hass,
            self.availability_topic,
            self._availability_received,
            qos=0,
        )

    async def async_unsubscribe(self) -> None:
        for unsub in self._unsub_telemetry:
            if unsub:
                unsub()
        self._unsub_telemetry.clear()

        if self._unsub_availability:
            self._unsub_availability()
            self._unsub_availability = None

    @staticmethod
    def _decode_payload(payload: Any) -> Any:
        """Decode JSON numbers/objects/arrays, while accepting plain strings."""
        text = str(payload).strip()
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return text

    @callback
    def _message_received(self, msg) -> None:
        topic = str(msg.topic).rstrip("/")

        # Availability is also one level below the telemetry base in the
        # default configuration, so ignore it here; its dedicated callback
        # handles online/offline state.
        if topic == self.availability_topic.rstrip("/"):
            return

        payload = self._decode_payload(msg.payload)

        if topic == self.telemetry_topic:
            # Backwards-compatible aggregate payload.
            if not isinstance(payload, dict):
                _LOGGER.warning(
                    "Overdrive BYD aggregate payload is not a JSON object: %s",
                    msg.payload,
                )
                return
            self.data.update(payload)
        else:
            prefix = f"{self.telemetry_topic}/"
            if not topic.startswith(prefix):
                return

            key = topic[len(prefix):]
            if not key or "/" in key:
                return

            # Current OverDrive publishes GPS as a location object:
            # {"latitude": ..., "longitude": ...}.  The tracker entity uses
            # the historical lat/lon keys, so normalize it here.
            if key == "location" and isinstance(payload, dict):
                latitude = payload.get("latitude", payload.get("lat"))
                longitude = payload.get("longitude", payload.get("lon"))
                if latitude is not None:
                    self.data["lat"] = latitude
                if longitude is not None:
                    self.data["lon"] = longitude
                self.data["location"] = payload
            else:
                self.data[key] = payload

            # Some OverDrive builds expose the vehicle distance using the
            # ev_mileage_km field rather than odometer. Only use it as a
            # fallback when it is a plausible value; placeholder values are
            # filtered later by clean_value().
            if key == "ev_mileage_km" and "odometer" not in self.data:
                self.data["odometer"] = payload

        self.available = True
        self.async_set_updated_data(dict(self.data))

    @callback
    def _availability_received(self, msg) -> None:
        payload = str(msg.payload).strip().lower()
        self.available = payload == "online"
        self.async_update_listeners()
