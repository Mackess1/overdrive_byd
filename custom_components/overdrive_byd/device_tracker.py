from __future__ import annotations

from homeassistant.components.device_tracker.config_entry import TrackerEntity

from .const import DOMAIN
from .entity import OverdriveBYDEntity, clean_value


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OverdriveBYDDeviceTracker(coordinator)])


class OverdriveBYDDeviceTracker(OverdriveBYDEntity, TrackerEntity):
    _attr_name = "Location"

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "overdrive_byd_location"

    @property
    def latitude(self):
        return clean_value(self.coordinator.data.get("lat"))

    @property
    def longitude(self):
        return clean_value(self.coordinator.data.get("lon"))

    @property
    def source_type(self):
        return "gps"

    @property
    def extra_state_attributes(self):
        return {
            "vin": self.coordinator.data.get("vin"),
            "speed": clean_value(self.coordinator.data.get("speed")),
            "elevation": clean_value(self.coordinator.data.get("elevation")),
            "utc": clean_value(self.coordinator.data.get("utc")),
            "vd_timestamp": clean_value(self.coordinator.data.get("vd_timestamp")),
        }
