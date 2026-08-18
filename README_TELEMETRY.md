# Overdrive BYD Extended Telemetry

This update adds Home Assistant entities for the larger Overdrive telemetry payload.

Telemetry topic:

```text
overdrive/vehicle/telemetry
```

Added coverage includes:

- HV battery pack voltage and cell voltage min/max/delta
- Cell temperature min/max/average/delta
- Inside temperature and 12V battery voltage
- Charging state, charging mode, charger state, charging gun, V2L
- Tyre pressures, tyre temperatures, tyre leak and signal states
- Door lock raw values
- Window open binary sensors
- Light states
- AC status, AC fan, AC cycle and AC wind
- Seatbelt, seat heat and seat cool values
- Sunroof state and position
- Steering, accelerator and brake values
- Radar distance values
- VIN, operation modes, MCU status and other diagnostic fields

Invalid BYD placeholder values like `-10011`, `-2147482648`, and `65535` are converted to unavailable/unknown where possible.

## MQTT compatibility

OverDrive currently publishes individual telemetry values on subtopics such as:

```text
overdrive/vehicle/telemetry/soc
overdrive/vehicle/telemetry/ev_range_km
overdrive/vehicle/telemetry/location
```

The integration subscribes to both the legacy aggregate JSON topic and the current one-value-per-subtopic format. The `location` object is normalized to `lat` / `lon` for the Home Assistant device tracker.

