# Overdrive BYD Command Support

This update adds Home Assistant command entities that publish JSON commands to MQTT.

## Command topic

Default:

```text
overdrive/vehicle/command
```

If the telemetry topic ends with `/telemetry`, the integration can derive the command topic by replacing `/telemetry` with `/command`.

## Payload format

```json
{
  "command": "climate_on",
  "source": "home_assistant"
}
```

With temperature:

```json
{
  "command": "set_climate_temperature",
  "temperature": 22,
  "source": "home_assistant"
}
```

## Commands published by the integration

```text
climate_on
climate_off
set_climate_temperature
lock
unlock
open_trunk
honk
flash_lights
open_windows
close_windows
start_charging
stop_charging
```

## What Overdrive app needs to add

Overdrive needs to subscribe to the command topic and map the `command` value to its existing internal vehicle control functions.
