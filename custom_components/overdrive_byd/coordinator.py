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
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )

        self.entry = entry
        self.telemetry_topic = entry.data.get(
            CONF_TELEMETRY_TOPIC,
            DEFAULT_TELEMETRY_TOPIC,
        )
        self.availability_topic = entry.data.get(
            CONF_AVAILABILITY_TOPIC,
            DEFAULT_AVAILABILITY_TOPIC,
        )

        self.data: dict[str, Any] = {}
        self.available = False
        self._unsub_telemetry = None
        self._unsub_availability = None

    async def async_setup(self) -> None:
        self._unsub_telemetry = await mqtt.async_subscribe(
            self.hass,
            self.telemetry_topic,
            self._message_received,
            qos=0,
        )

        self._unsub_availability = await mqtt.async_subscribe(
            self.hass,
            self.availability_topic,
            self._availability_received,
            qos=0,
        )

    async def async_unsubscribe(self) -> None:
        if self._unsub_telemetry:
            self._unsub_telemetry()
            self._unsub_telemetry = None

        if self._unsub_availability:
            self._unsub_availability()
            self._unsub_availability = None

    @callback
    def _message_received(self, msg) -> None:
        try:
            payload = json.loads(msg.payload)
        except json.JSONDecodeError:
            _LOGGER.warning("Invalid JSON received from Overdrive BYD: %s", msg.payload)
            return

        if not isinstance(payload, dict):
            _LOGGER.warning("Overdrive BYD payload is not a JSON object")
            return

        self.data = payload
        self.available = True
        self.async_set_updated_data(self.data)

    @callback
    def _availability_received(self, msg) -> None:
        payload = str(msg.payload).strip().lower()
        self.available = payload == "online"
        self.async_update_listeners()
