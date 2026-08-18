from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)

from .const import DOMAIN, INVALID_VALUES
from .entity import OverdriveBYDEntity, get_array_value


@dataclass(frozen=True)
class OverdriveBYDBinarySensorEntityDescription(BinarySensorEntityDescription):
    array_key: str | None = None
    array_index: int | None = None


BINARY_SENSORS: tuple[OverdriveBYDBinarySensorEntityDescription, ...] = (
    OverdriveBYDBinarySensorEntityDescription(
        key="is_charging",
        name="Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="is_dcfc",
        name="DC Fast Charging",
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="is_parked",
        name="Parked",
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="ac_on",
        name="AC On",
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="light_hazard",
        name="Hazard Lights",
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="light_low_beam",
        name="Low Beam",
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="light_high_beam",
        name="High Beam",
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="light_drl",
        name="Daytime Running Lights",
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="light_front_fog",
        name="Front Fog Lights",
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="light_rear_fog",
        name="Rear Fog Lights",
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="key_battery",
        name="Key Battery Low",
        device_class=BinarySensorDeviceClass.BATTERY,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="key_bt_low_power",
        name="Bluetooth Key Low Power",
        device_class=BinarySensorDeviceClass.BATTERY,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="speed_limit_warning",
        name="Speed Limit Warning",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="emergency_alarm",
        name="Emergency Alarm",
        device_class=BinarySensorDeviceClass.SAFETY,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="tyre_leak_fl",
        name="Front Left Tyre Leak",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="tyre_leak_fr",
        name="Front Right Tyre Leak",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="tyre_leak_rl",
        name="Rear Left Tyre Leak",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="tyre_leak_rr",
        name="Rear Right Tyre Leak",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


ARRAY_BINARY_SENSORS: tuple[OverdriveBYDBinarySensorEntityDescription, ...] = (
    OverdriveBYDBinarySensorEntityDescription(
        key="window_open_fl",
        name="Front Left Window",
        device_class=BinarySensorDeviceClass.WINDOW,
        array_key="window_open",
        array_index=0,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="window_open_fr",
        name="Front Right Window",
        device_class=BinarySensorDeviceClass.WINDOW,
        array_key="window_open",
        array_index=1,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="window_open_rl",
        name="Rear Left Window",
        device_class=BinarySensorDeviceClass.WINDOW,
        array_key="window_open",
        array_index=2,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="window_open_rr",
        name="Rear Right Window",
        device_class=BinarySensorDeviceClass.WINDOW,
        array_key="window_open",
        array_index=3,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="seatbelt_driver",
        name="Driver Seatbelt",
        device_class=BinarySensorDeviceClass.SAFETY,
        array_key="seatbelt",
        array_index=0,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="seatbelt_passenger",
        name="Passenger Seatbelt",
        device_class=BinarySensorDeviceClass.SAFETY,
        array_key="seatbelt",
        array_index=1,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="seatbelt_rear_left",
        name="Rear Left Seatbelt",
        device_class=BinarySensorDeviceClass.SAFETY,
        array_key="seatbelt",
        array_index=2,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="seatbelt_rear_middle",
        name="Rear Middle Seatbelt",
        device_class=BinarySensorDeviceClass.SAFETY,
        array_key="seatbelt",
        array_index=3,
    ),
    OverdriveBYDBinarySensorEntityDescription(
        key="seatbelt_rear_right",
        name="Rear Right Seatbelt",
        device_class=BinarySensorDeviceClass.SAFETY,
        array_key="seatbelt",
        array_index=4,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [OverdriveBYDBinarySensor(coordinator, description) for description in BINARY_SENSORS]
    entities += [OverdriveBYDBinarySensor(coordinator, description) for description in ARRAY_BINARY_SENSORS]

    async_add_entities(entities)


class OverdriveBYDBinarySensor(OverdriveBYDEntity, BinarySensorEntity):
    def __init__(self, coordinator, description: OverdriveBYDBinarySensorEntityDescription) -> None:
        super().__init__(coordinator, description)

        self._attr_unique_id = f"overdrive_byd_{description.key}"

    @property
    def is_on(self):
        description = self.entity_description

        if description.array_key is not None and description.array_index is not None:
            value = get_array_value(
                self.coordinator.data,
                description.array_key,
                description.array_index,
            )
        else:
            value = self.coordinator.data.get(description.key)

        if value in INVALID_VALUES or value is None:
            return None

        try:
            return int(value) == 1
        except (TypeError, ValueError):
            return None
