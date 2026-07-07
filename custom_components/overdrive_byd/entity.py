from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, INVALID_VALUES


def clean_value(value):
    if value in INVALID_VALUES:
        return None

    if isinstance(value, float):
        return round(value, 3)

    return value


def get_array_value(data: dict, key: str, index: int):
    value = data.get(key)

    if not isinstance(value, list):
        return None

    if index >= len(value):
        return None

    return clean_value(value[index])


class OverdriveBYDEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, description=None) -> None:
        super().__init__(coordinator)

        self.entity_description = description

        vin = coordinator.data.get("vin", "unknown")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, vin)},
            "name": coordinator.entry.data.get("name", "BYD Vehicle"),
            "manufacturer": "BYD",
            "model": "Yuan Plus / Atto 3",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.available
