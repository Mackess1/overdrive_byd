import json
import logging
from datetime import datetime, timezone

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature, UnitOfLength, PERCENTAGE
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send, async_dispatcher_connect

from .const import DOMAIN, CONF_TOPIC, CONF_NAME

_LOGGER = logging.getLogger(__name__)


SENSORS = [
    ("utc", "UTC", None, None),
    ("soc", "Battery Percentage", PERCENTAGE, SensorDeviceClass.BATTERY),
    ("power", "Power", "kW", SensorDeviceClass.POWER),
    ("speed", "Speed", "km/h", None),
    ("lat", "Latitude", None, None),
    ("lon", "Longitude", None, None),
    ("elevation", "Elevation", UnitOfLength.METERS, None),
    ("ext_temp", "Outside Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    ("batt_temp", "Battery Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    ("odometer", "Odometer", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
    ("soh", "Battery Health", PERCENTAGE, None),
    ("capacity", "Battery Capacity", "kWh", None),
    ("gear", "Gear", None, None),
    ("consumption_50km", "Consumption 50km", "kWh/100km", None),
    ("driving_time_hours", "Driving Time", "h", None),
    ("ev_range_km", "EV Range", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
]


async def async_setup_entry(hass, entry, async_add_entities):
    topic = entry.data[CONF_TOPIC]
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    async def message_received(msg):
        try:
            payload = json.loads(msg.payload)
        except Exception:
            _LOGGER.warning("Invalid Overdrive JSON payload: %s", msg.payload)
            return

        hass.data[DOMAIN][entry.entry_id]["data"] = payload
        async_dispatcher_send(hass, signal)

    unsub = await mqtt.async_subscribe(hass, topic, message_received, 0)
    hass.data[DOMAIN][entry.entry_id]["listeners"].append(unsub)

    async_add_entities(
        [OverdriveBYDSensor(entry, name, signal, key, label, unit, device_class) for key, label, unit, device_class in SENSORS]
    )


class OverdriveBYDSensor(SensorEntity):
    def __init__(self, entry, vehicle_name, signal, key, label, unit, device_class):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal
        self.key = key
        self._attr_name = f"{vehicle_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.vehicle_name,
            manufacturer="BYD",
            model="Overdrive MQTT Vehicle",
        )

    @property
    def native_value(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]
        value = data.get(self.key)

        if self.key == "utc" and value:
            try:
                return datetime.fromtimestamp(value, timezone.utc).isoformat()
            except Exception:
                return value

        if isinstance(value, float):
            return round(value, 2)

        return value

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )