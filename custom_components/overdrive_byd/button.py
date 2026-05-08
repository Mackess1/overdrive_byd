from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo

from .command import async_send_command
from .const import DOMAIN, CONF_NAME


BUTTONS = [
    ("climate_on", "Turn On AC", "mdi:air-conditioner"),
    ("climate_off", "Turn Off AC", "mdi:air-conditioner-off"),
    ("honk", "Honk Horn", "mdi:bullhorn"),
    ("flash_lights", "Flash Lights", "mdi:car-light-high"),
    ("open_trunk", "Open Trunk", "mdi:car-back"),
    ("start_charging", "Start Charging", "mdi:ev-station"),
    ("stop_charging", "Stop Charging", "mdi:ev-station"),
]


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]

    async_add_entities(
        [
            OverdriveBYDButton(entry, name, command, label, icon)
            for command, label, icon in BUTTONS
        ]
    )


class OverdriveBYDButton(ButtonEntity):
    def __init__(self, entry, vehicle_name, command, label, icon):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.command = command

        self._attr_name = f"{vehicle_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{command}"
        self._attr_icon = icon

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.vehicle_name,
            manufacturer="BYD",
            model="Overdrive MQTT Vehicle",
        )

    async def async_press(self):
        await async_send_command(self.hass, self.entry, self.command)
