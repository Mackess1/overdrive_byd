from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from .const import CONF_NAME, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    async_add_entities([OverdriveBYDTracker(entry, name, signal)])


class OverdriveBYDTracker(TrackerEntity):
    def __init__(self, entry, vehicle_name, signal):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal

        self._attr_name = f"{vehicle_name} Location"
        self._attr_unique_id = f"{entry.entry_id}_location"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.vehicle_name,
            manufacturer="BYD",
            model="Overdrive MQTT Vehicle",
        )

    @property
    def latitude(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]
        return data.get("lat")

    @property
    def longitude(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]
        return data.get("lon")

    @property
    def battery_level(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]
        return data.get("soc")

    @property
    def source_type(self):
        return "gps"

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )
