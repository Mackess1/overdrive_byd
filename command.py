import json
import logging

from homeassistant.components import mqtt

from .const import CONF_COMMAND_TOPIC, CONF_TOPIC, DEFAULT_COMMAND_TOPIC

_LOGGER = logging.getLogger(__name__)


def get_command_topic(entry):
    """Return command topic.

    Existing installs will not have command_topic saved in the config entry,
    so this safely falls back to the default command topic.
    """
    return entry.data.get(CONF_COMMAND_TOPIC) or _topic_from_telemetry(entry.data.get(CONF_TOPIC))


def _topic_from_telemetry(telemetry_topic):
    if not telemetry_topic:
        return DEFAULT_COMMAND_TOPIC

    if telemetry_topic.endswith("/telemetry"):
        return telemetry_topic[: -len("/telemetry")] + "/command"

    return DEFAULT_COMMAND_TOPIC


async def async_send_command(hass, entry, command, **kwargs):
    """Publish one Overdrive command to MQTT."""
    topic = get_command_topic(entry)

    payload = {
        "command": command,
        "source": "home_assistant",
    }

    payload.update({key: value for key, value in kwargs.items() if value is not None})

    _LOGGER.debug("Sending Overdrive command to %s: %s", topic, payload)

    await mqtt.async_publish(
        hass,
        topic,
        json.dumps(payload),
        qos=1,
        retain=False,
    )
