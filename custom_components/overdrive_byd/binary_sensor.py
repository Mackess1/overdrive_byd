from datetime import datetime, timezone

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .const import CONF_NAME, DOMAIN

INVALID_VALUES = {
    -10011,
    -2147482648,
    -2147482647,
    65535,
}


# key, label, device_class, entity_category, array_index
BINARY_SENSORS = [
    ("is_charging", "Charging", BinarySensorDeviceClass.BATTERY_CHARGING, None, None),
    ("is_dcfc", "DC Fast Charging", None, None, None),
    ("is_parked", "Parked", None, None, None),

    ("key_battery", "Key Battery Low", BinarySensorDeviceClass.BATTERY, EntityCategory.DIAGNOSTIC, None),
    ("key_bt_low_power", "Key Bluetooth Low Power", BinarySensorDeviceClass.BATTERY, EntityCategory.DIAGNOSTIC, None),

    ("charging_gun", "Charging Gun Connected", BinarySensorDeviceClass.PLUG, None, None),
    ("charging_v2l", "V2L Active", None, None, None),

    ("light_low_beam", "Low Beam", BinarySensorDeviceClass.LIGHT, None, None),
    ("light_high_beam", "High Beam", BinarySensorDeviceClass.LIGHT, None, None),
    ("light_rear_fog", "Rear Fog Light", BinarySensorDeviceClass.LIGHT, None, None),
    ("light_front_fog", "Front Fog Light", BinarySensorDeviceClass.LIGHT, None, None),
    ("light_hazard", "Hazard Lights", BinarySensorDeviceClass.LIGHT, None, None),
    ("light_drl", "Daytime Running Lights", BinarySensorDeviceClass.LIGHT, None, None),

    ("ac_on", "AC On", None, None, None),

    ("tyre_leak_fl", "Tyre Leak Front Left", BinarySensorDeviceClass.PROBLEM, None, None),
    ("tyre_leak_fr", "Tyre Leak Front Right", BinarySensorDeviceClass.PROBLEM, None, None),
    ("tyre_leak_rl", "Tyre Leak Rear Left", BinarySensorDeviceClass.PROBLEM, None, None),
    ("tyre_leak_rr", "Tyre Leak Rear Right", BinarySensorDeviceClass.PROBLEM, None, None),
    ("tyre_signal_fl", "Tyre Signal Front Left", None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_signal_fr", "Tyre Signal Front Right", None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_signal_rl", "Tyre Signal Rear Left", None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_signal_rr", "Tyre Signal Rear Right", None, EntityCategory.DIAGNOSTIC, None),

    ("window_open", "Window 1 Open", BinarySensorDeviceClass.WINDOW, None, 0),
    ("window_open", "Window 2 Open", BinarySensorDeviceClass.WINDOW, None, 1),
    ("window_open", "Window 3 Open", BinarySensorDeviceClass.WINDOW, None, 2),
    ("window_open", "Window 4 Open", BinarySensorDeviceClass.WINDOW, None, 3),
    ("window_open", "Window 5 Open", BinarySensorDeviceClass.WINDOW, None, 4),
    ("window_open", "Window 6 Open", BinarySensorDeviceClass.WINDOW, None, 5),

    ("seatbelt", "Seatbelt 1 Fastened", None, None, 0),
    ("seatbelt", "Seatbelt 2 Fastened", None, None, 1),
    ("seatbelt", "Seatbelt 3 Fastened", None, None, 2),
    ("seatbelt", "Seatbelt 4 Fastened", None, None, 3),
    ("seatbelt", "Seatbelt 5 Fastened", None, None, 4),

    ("emergency_alarm", "Emergency Alarm", BinarySensorDeviceClass.SAFETY, None, None),
    ("speed_limit_warning", "Speed Limit Warning", BinarySensorDeviceClass.PROBLEM, None, None),
]


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    entities = [
        OverdriveBYDBinarySensor(entry, name, signal, key, label, device_class, entity_category, index)
        for key, label, device_class, entity_category, index in BINARY_SENSORS
    ]

    entities.append(OverdriveBYDOnlineSensor(entry, name, signal))

    async_add_entities(entities)


class OverdriveBYDBinarySensor(BinarySensorEntity):
    def __init__(self, entry, vehicle_name, signal, key, label, device_class, entity_category, index=None):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal
        self.key = key
        self.index = index

        suffix = f"_{index}" if index is not None else ""
        self._attr_name = f"{vehicle_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{key}{suffix}"
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
        value = data.get(self.key)

        if self.index is not None:
            if not isinstance(value, list) or len(value) <= self.index:
                return None
            value = value[self.index]

        if value in INVALID_VALUES:
            return None

        return value == 1 or value is True

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
