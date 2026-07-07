from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_TELEMETRY_TOPIC,
    DEFAULT_AVAILABILITY_TOPIC,
    CONF_TELEMETRY_TOPIC,
    CONF_AVAILABILITY_TOPIC,
)


class OverdriveBYDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id("overdrive_byd")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input["name"],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("name", default=DEFAULT_NAME): str,
                vol.Required(
                    CONF_TELEMETRY_TOPIC,
                    default=DEFAULT_TELEMETRY_TOPIC,
                ): str,
                vol.Required(
                    CONF_AVAILABILITY_TOPIC,
                    default=DEFAULT_AVAILABILITY_TOPIC,
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
