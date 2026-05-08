from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .command import async_send_command
from .const import DOMAIN, CONF_NAME


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    async_add_entities([OverdriveBYDWindows(entry, name, signal)])


class OverdriveBYDWindows(CoverEntity):
    def __init__(self, entry, vehicle_name, signal):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal

        self._attr_name = f"{vehicle_name} Windows"
        self._attr_unique_id = f"{entry.entry_id}_windows"
        self._attr_icon = "mdi:car-door"
        self._attr_supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
        )

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.vehicle_name,
            manufacturer="BYD",
            model="Overdrive MQTT Vehicle",
        )

    @property
    def is_closed(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]

        if "windows_closed" in data:
            return data.get("windows_closed") == 1 or data.get("windows_closed") is True

        return None

    async def async_open_cover(self, **kwargs):
        await async_send_command(self.hass, self.entry, "open_windows")

    async def async_close_cover(self, **kwargs):
        await async_send_command(self.hass, self.entry, "close_windows")

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )
