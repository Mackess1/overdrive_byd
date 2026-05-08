from homeassistant.components.lock import LockEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .command import async_send_command
from .const import DOMAIN, CONF_NAME


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    async_add_entities([OverdriveBYDDoorLock(entry, name, signal)])


class OverdriveBYDDoorLock(LockEntity):
    def __init__(self, entry, vehicle_name, signal):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal

        self._attr_name = f"{vehicle_name} Door Lock"
        self._attr_unique_id = f"{entry.entry_id}_door_lock"
        self._attr_icon = "mdi:car-door-lock"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.vehicle_name,
            manufacturer="BYD",
            model="Overdrive MQTT Vehicle",
        )

    @property
    def is_locked(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]

        if "is_locked" in data:
            return data.get("is_locked") == 1 or data.get("is_locked") is True

        if "locked" in data:
            return data.get("locked") == 1 or data.get("locked") is True

        return None

    async def async_lock(self, **kwargs):
        await async_send_command(self.hass, self.entry, "lock")

    async def async_unlock(self, **kwargs):
        await async_send_command(self.hass, self.entry, "unlock")

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )
