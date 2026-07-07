# Overdrive BYD MQTT

A Home Assistant custom integration for BYD vehicles using Overdrive MQTT telemetry.

This integration automatically creates Home Assistant entities from JSON telemetry published over MQTT.

Supports:

- Battery percentage
- EV range
- GPS location
- Charging status
- DC fast charging
- Odometer
- Vehicle speed
- Gear position
- Battery temperature
- Outside temperature
- Battery SOH
- Power usage
- Elevation
- Driving time
- Consumption data

---

# Features

- MQTT based
- Local push updates
- Device Tracker support
- Home Assistant UI setup
- HACS compatible
- Real-time telemetry updates

---

# MQTT Topic

Default topic:

```text
overdrive/vehicle/telemetry
```

Example payload:

```json
{
  "utc": 1778045208,
  "soc": 63,
  "power": 0,
  "speed": 0,
  "lat": 12.03329681,
  "lon": -61.72169713,
  "is_charging": 0,
  "is_dcfc": 0,
  "is_parked": 1,
  "elevation": 14.4,
  "ext_temp": 29,
  "batt_temp": 30,
  "odometer": 4977,
  "soh": 93.3,
  "capacity": 37.6,
  "gear": "P",
  "consumption_50km": 18.1,
  "driving_time_hours": 5.1,
  "key_battery": 0,
  "ev_range_km": 316
}
```

---

# Installation

## HACS Installation

1. Open HACS
2. Go to Custom Repositories
3. Add your GitHub repository URL
4. Category: Integration
5. Install
6. Restart Home Assistant

---

# Manual Installation

Copy:

```text
custom_components/overdrive_byd
```

into:

```text
/config/custom_components/
```

Restart Home Assistant.

---

# Setup

1. Go to:

```text
Settings → Devices & Services
```

2. Click:

```text
Add Integration
```

3. Search for:

```text
Overdrive BYD MQTT
```

4. Enter:

- Vehicle Name
- MQTT Topic

---

# Created Entities

Examples:

```text
sensor.byd_car_battery_percentage
sensor.byd_car_ev_range
sensor.byd_car_speed
sensor.byd_car_odometer
binary_sensor.byd_car_charging
binary_sensor.byd_car_parked
device_tracker.byd_car_location
```

---

# Requirements

- Home Assistant
- MQTT Broker
- Overdrive telemetry publisher

---

# Future Plans

- Multi vehicle support
- Vehicle commands
- Remote control support
- Trip history
- Charging analytics
- Native dashboard cards
- Diagnostic entities

---

# Disclaimer

This project is not affiliated with BYD or Overdrive.

Use at your own risk.

---

# License

MIT License
