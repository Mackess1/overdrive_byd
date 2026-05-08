import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_TOPIC,
    CONF_COMMAND_TOPIC,
    CONF_NAME,
    DEFAULT_TOPIC,
    DEFAULT_COMMAND_TOPIC,
    DEFAULT_NAME,
)


class OverdriveBYDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_TOPIC])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_TOPIC, default=DEFAULT_TOPIC): str,
                vol.Required(CONF_COMMAND_TOPIC, default=DEFAULT_COMMAND_TOPIC): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
