from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .command import async_send_command
from .const import DOMAIN, CONF_NAME


async def async_setup_entry(hass, entry, async_add_entities):
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    async_add_entities([OverdriveBYDClimate(entry, name, signal)])


class OverdriveBYDClimate(ClimateEntity):
    def __init__(self, entry, vehicle_name, signal):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal

        self._attr_name = f"{vehicle_name} AC"
        self._attr_unique_id = f"{entry.entry_id}_ac"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL]
        self._attr_min_temp = 16
        self._attr_max_temp = 30
        self._attr_target_temperature_step = 1

        self._target_temperature = 22
        self._hvac_mode = HVACMode.OFF

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.vehicle_name,
            manufacturer="BYD",
            model="Overdrive MQTT Vehicle",
        )

    @property
    def target_temperature(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]

        if "target_temp" in data:
            return data.get("target_temp")

        if "climate_temp" in data:
            return data.get("climate_temp")

        return self._target_temperature

    @property
    def current_temperature(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]
        return data.get("cabin_temp") or data.get("int_temp") or data.get("ext_temp")

    @property
    def hvac_mode(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]

        if data.get("climate_on") == 1 or data.get("climate_on") is True:
            return HVACMode.COOL

        return self._hvac_mode

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.COOL:
            await async_send_command(
                self.hass,
                self.entry,
                "climate_on",
                temperature=self.target_temperature,
            )
            self._hvac_mode = HVACMode.COOL

        elif hvac_mode == HVACMode.OFF:
            await async_send_command(self.hass, self.entry, "climate_off")
            self._hvac_mode = HVACMode.OFF

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if temperature is None:
            return

        self._target_temperature = int(temperature)

        await async_send_command(
            self.hass,
            self.entry,
            "set_climate_temperature",
            temperature=int(temperature),
        )

        self.async_write_ha_state()

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )
