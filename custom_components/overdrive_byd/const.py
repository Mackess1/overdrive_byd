DOMAIN = "overdrive_byd"

CONF_TOPIC = "topic"
CONF_COMMAND_TOPIC = "command_topic"
CONF_NAME = "name"

DEFAULT_TOPIC = "overdrive/vehicle/telemetry"
DEFAULT_COMMAND_TOPIC = "overdrive/vehicle/command"
DEFAULT_NAME = "BYD Car"

PLATFORMS = [
    "sensor",
    "binary_sensor",
    "device_tracker",
    "button",
    "lock",
    "climate",
    "cover",
]
