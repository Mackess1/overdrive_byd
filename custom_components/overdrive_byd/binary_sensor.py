from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, CONF_NAME


BINARY_SENSORS = [
    ("is_charging", "Charging", BinarySensorDeviceClass.BATTERY_CHARGING),
    ("is_dcfc", "DC Fast Charging", None),
    ("is_parked", "Parked", None),
    ("key_battery", "Key Battery Low", BinarySensorDeviceClass.BATTERY),
]


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    async_add_entities(
        [OverdriveBYDBinarySensor(entry, name, signal, key, label, device_class) for key, label, device_class in BINARY_SENSORS]
    )


class OverdriveBYDBinarySensor(BinarySensorEntity):
    def __init__(self, entry, vehicle_name, signal, key, label, device_class):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal
        self.key = key
        self._attr_name = f"{vehicle_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
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
    def is_on(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]
        return data.get(self.key) == 1

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )