from datetime import datetime, timezone

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .const import CONF_NAME, DOMAIN

BINARY_SENSORS = [
    ("is_charging", "Charging", BinarySensorDeviceClass.BATTERY_CHARGING, None),
    ("is_dcfc", "DC Fast Charging", None, None),
    ("is_parked", "Parked", None, None),
    ("key_battery", "Key Battery Low", BinarySensorDeviceClass.BATTERY, EntityCategory.DIAGNOSTIC),
]


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    entities = [
        OverdriveBYDBinarySensor(entry, name, signal, key, label, device_class, entity_category)
        for key, label, device_class, entity_category in BINARY_SENSORS
    ]

    entities.append(OverdriveBYDOnlineSensor(entry, name, signal))

    async_add_entities(entities)


class OverdriveBYDBinarySensor(BinarySensorEntity):
    def __init__(self, entry, vehicle_name, signal, key, label, device_class, entity_category):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal
        self.key = key

        self._attr_name = f"{vehicle_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_class = device_class
        self._attr_entity_category = entity_category

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


class OverdriveBYDOnlineSensor(BinarySensorEntity):
    def __init__(self, entry, vehicle_name, signal):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal

        self._attr_name = f"{vehicle_name} Online"
        self._attr_unique_id = f"{entry.entry_id}_online"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

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
        last_seen = self.hass.data[DOMAIN][self.entry.entry_id].get("last_seen")

        if last_seen is None:
            return False

        age = datetime.now(timezone.utc) - last_seen
        return age.total_seconds() < 600

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )
