import json
import logging
from datetime import datetime, timezone

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfTemperature
from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .const import CONF_NAME, CONF_TOPIC, DOMAIN

_LOGGER = logging.getLogger(__name__)

INVALID_VALUES = {
    -10011,
    -2147482648,
    -2147482647,
    1048575,
    104857.5,
    65535,
}


# key, label, unit, device_class, entity_category, array_index
SENSORS = [
    # Core vehicle data
    ("utc", "Last Update", None, None, EntityCategory.DIAGNOSTIC, None),
    ("vd_timestamp", "Vehicle Data Timestamp", None, None, EntityCategory.DIAGNOSTIC, None),
    ("soc", "Battery Percentage", PERCENTAGE, SensorDeviceClass.BATTERY, None, None),
    ("power", "Power", "kW", SensorDeviceClass.POWER, None, None),
    ("speed", "Speed", "km/h", None, None, None),
    ("gear", "Gear", None, None, None, None),
    ("lat", "Latitude", None, None, EntityCategory.DIAGNOSTIC, None),
    ("lon", "Longitude", None, None, EntityCategory.DIAGNOSTIC, None),
    ("elevation", "Elevation", UnitOfLength.METERS, None, EntityCategory.DIAGNOSTIC, None),
    ("odometer", "Odometer", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, None, None),
    ("ev_range_km", "EV Range", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, None, None),
    ("consumption_50km", "Consumption 50km", "kWh/100km", None, None, None),
    ("driving_time_hours", "Driving Time", "h", None, EntityCategory.DIAGNOSTIC, None),
    ("vin", "VIN", None, None, EntityCategory.DIAGNOSTIC, None),

    # Temperatures and battery health
    ("ext_temp", "Outside Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None),
    ("inside_temp", "Inside Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None),
    ("batt_temp", "Battery Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None),
    ("cell_t_max", "Cell Temperature Max", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, EntityCategory.DIAGNOSTIC, None),
    ("cell_t_min", "Cell Temperature Min", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, EntityCategory.DIAGNOSTIC, None),
    ("cell_t_avg", "Cell Temperature Average", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, EntityCategory.DIAGNOSTIC, None),
    ("cell_t_delta", "Cell Temperature Delta", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, EntityCategory.DIAGNOSTIC, None),
    ("soh", "Battery Health", PERCENTAGE, None, EntityCategory.DIAGNOSTIC, None),
    ("capacity", "Battery Capacity", "kWh", None, EntityCategory.DIAGNOSTIC, None),
    ("hv_pack_v", "HV Pack Voltage", "V", SensorDeviceClass.VOLTAGE, EntityCategory.DIAGNOSTIC, None),
    ("cell_v_max", "Cell Voltage Max", "V", SensorDeviceClass.VOLTAGE, EntityCategory.DIAGNOSTIC, None),
    ("cell_v_min", "Cell Voltage Min", "V", SensorDeviceClass.VOLTAGE, EntityCategory.DIAGNOSTIC, None),
    ("cell_v_delta", "Cell Voltage Delta", "V", SensorDeviceClass.VOLTAGE, EntityCategory.DIAGNOSTIC, None),
    ("volt_12v", "12V Battery Voltage", "V", SensorDeviceClass.VOLTAGE, EntityCategory.DIAGNOSTIC, None),
    ("batt_12v_level", "12V Battery Level", None, None, EntityCategory.DIAGNOSTIC, None),

    # Driving controls and modes
    ("accel_pct", "Accelerator", PERCENTAGE, None, EntityCategory.DIAGNOSTIC, None),
    ("brake_pct", "Brake", PERCENTAGE, None, EntityCategory.DIAGNOSTIC, None),
    ("steering_deg", "Steering Angle", "°", None, EntityCategory.DIAGNOSTIC, None),
    ("energy_mode", "Energy Mode", None, None, EntityCategory.DIAGNOSTIC, None),
    ("op_mode", "Operation Mode", None, None, EntityCategory.DIAGNOSTIC, None),
    ("power_level", "Power Level", None, None, EntityCategory.DIAGNOSTIC, None),
    ("mcu_status", "MCU Status", None, None, EntityCategory.DIAGNOSTIC, None),
    ("drift_mode", "Drift Mode", None, None, EntityCategory.DIAGNOSTIC, None),
    ("speed_limit_warning", "Speed Limit Warning", None, None, EntityCategory.DIAGNOSTIC, None),
    ("key_start_state", "Key Start State", None, None, EntityCategory.DIAGNOSTIC, None),
    ("key_detection_reminder", "Key Detection Reminder", None, None, EntityCategory.DIAGNOSTIC, None),
    ("smart_key_warn", "Smart Key Warning", None, None, EntityCategory.DIAGNOSTIC, None),
    ("key_bt_low_power", "Key Bluetooth Low Power", None, None, EntityCategory.DIAGNOSTIC, None),

    # Charging
    ("charging_state", "Charging State", None, None, EntityCategory.DIAGNOSTIC, None),
    ("charger_state", "Charger State", None, None, EntityCategory.DIAGNOSTIC, None),
    ("charging_mode", "Charging Mode", None, None, EntityCategory.DIAGNOSTIC, None),
    ("charging_type", "Charging Type", None, None, EntityCategory.DIAGNOSTIC, None),
    ("charging_v2l", "V2L State", None, None, EntityCategory.DIAGNOSTIC, None),
    ("wireless_charging_left", "Wireless Charging Left", None, None, EntityCategory.DIAGNOSTIC, None),
    ("wireless_charging_right", "Wireless Charging Right", None, None, EntityCategory.DIAGNOSTIC, None),
    ("wireless_charging_status", "Wireless Charging Status", None, None, EntityCategory.DIAGNOSTIC, None),

    # Lifetime counters
    ("total_elec_con", "Total Electric Consumption", "kWh", None, EntityCategory.DIAGNOSTIC, None),
    ("total_fuel_con", "Total Fuel Consumption", None, None, EntityCategory.DIAGNOSTIC, None),
    ("ev_mileage_km", "EV Mileage", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, EntityCategory.DIAGNOSTIC, None),

    # Climate
    ("ac_cycle", "AC Cycle", None, None, EntityCategory.DIAGNOSTIC, None),
    ("ac_wind", "AC Wind", None, None, EntityCategory.DIAGNOSTIC, None),
    ("ac_fan", "AC Fan", None, None, None, None),
    ("temp_unit", "Temperature Unit", None, None, EntityCategory.DIAGNOSTIC, None),

    # Tyres
    ("tyre_p_fl", "Tyre Pressure Front Left", "kPa", SensorDeviceClass.PRESSURE, None, None),
    ("tyre_p_fr", "Tyre Pressure Front Right", "kPa", SensorDeviceClass.PRESSURE, None, None),
    ("tyre_p_rl", "Tyre Pressure Rear Left", "kPa", SensorDeviceClass.PRESSURE, None, None),
    ("tyre_p_rr", "Tyre Pressure Rear Right", "kPa", SensorDeviceClass.PRESSURE, None, None),
    ("tyre_t_fl", "Tyre Temperature Front Left", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None),
    ("tyre_t_fr", "Tyre Temperature Front Right", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None),
    ("tyre_t_rl", "Tyre Temperature Rear Left", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None),
    ("tyre_t_rr", "Tyre Temperature Rear Right", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None, None),
    ("tyre_p_state_fl", "Tyre Pressure State Front Left", None, None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_p_state_fr", "Tyre Pressure State Front Right", None, None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_p_state_rl", "Tyre Pressure State Rear Left", None, None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_p_state_rr", "Tyre Pressure State Rear Right", None, None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_system_state", "Tyre System State", None, None, EntityCategory.DIAGNOSTIC, None),
    ("tyre_temp_state", "Tyre Temperature State", None, None, EntityCategory.DIAGNOSTIC, None),

    # Doors, seatbelt, seat heating/cooling, sunroof
    ("door_lock", "Door Lock 1 Raw", None, None, EntityCategory.DIAGNOSTIC, 0),
    ("door_lock", "Door Lock 2 Raw", None, None, EntityCategory.DIAGNOSTIC, 1),
    ("door_lock", "Door Lock 3 Raw", None, None, EntityCategory.DIAGNOSTIC, 2),
    ("door_lock", "Door Lock 4 Raw", None, None, EntityCategory.DIAGNOSTIC, 3),
    ("door_lock", "Door Lock 5 Raw", None, None, EntityCategory.DIAGNOSTIC, 4),
    ("door_lock", "Door Lock 6 Raw", None, None, EntityCategory.DIAGNOSTIC, 5),
    ("door_lock", "Door Lock 7 Raw", None, None, EntityCategory.DIAGNOSTIC, 6),
    ("seatbelt", "Seatbelt 1 Raw", None, None, EntityCategory.DIAGNOSTIC, 0),
    ("seatbelt", "Seatbelt 2 Raw", None, None, EntityCategory.DIAGNOSTIC, 1),
    ("seatbelt", "Seatbelt 3 Raw", None, None, EntityCategory.DIAGNOSTIC, 2),
    ("seatbelt", "Seatbelt 4 Raw", None, None, EntityCategory.DIAGNOSTIC, 3),
    ("seatbelt", "Seatbelt 5 Raw", None, None, EntityCategory.DIAGNOSTIC, 4),
    ("seat_heat", "Seat Heat Driver", None, None, None, 0),
    ("seat_heat", "Seat Heat Passenger", None, None, None, 1),
    ("seat_cool", "Seat Cool Driver", None, None, None, 0),
    ("seat_cool", "Seat Cool Passenger", None, None, None, 1),
    ("sunroof_state", "Sunroof State", None, None, EntityCategory.DIAGNOSTIC, None),
    ("sunroof_pos", "Sunroof Position", None, None, None, None),

    # Lights and misc engine/status values
    ("light_left_turn", "Left Turn Light Raw", None, None, EntityCategory.DIAGNOSTIC, None),
    ("light_right_turn", "Right Turn Light Raw", None, None, EntityCategory.DIAGNOSTIC, None),
    ("engine_coolant_level", "Engine Coolant Level", None, None, EntityCategory.DIAGNOSTIC, None),
    ("oil_level", "Oil Level", None, None, EntityCategory.DIAGNOSTIC, None),
    ("engine_code", "Engine Code", None, None, EntityCategory.DIAGNOSTIC, None),
    ("emergency_alarm", "Emergency Alarm", None, None, EntityCategory.DIAGNOSTIC, None),

    # Radar distances
    ("radar_distances", "Radar Distance 1", "cm", None, EntityCategory.DIAGNOSTIC, 0),
    ("radar_distances", "Radar Distance 2", "cm", None, EntityCategory.DIAGNOSTIC, 1),
    ("radar_distances", "Radar Distance 3", "cm", None, EntityCategory.DIAGNOSTIC, 2),
    ("radar_distances", "Radar Distance 4", "cm", None, EntityCategory.DIAGNOSTIC, 3),
    ("radar_distances", "Radar Distance 5", "cm", None, EntityCategory.DIAGNOSTIC, 4),
    ("radar_distances", "Radar Distance 6", "cm", None, EntityCategory.DIAGNOSTIC, 5),
    ("radar_distances", "Radar Distance 7", "cm", None, EntityCategory.DIAGNOSTIC, 6),
    ("radar_distances", "Radar Distance 8", "cm", None, EntityCategory.DIAGNOSTIC, 7),
    ("radar_distances", "Radar Distance 9", "cm", None, EntityCategory.DIAGNOSTIC, 8),
]


async def async_setup_entry(hass, entry, async_add_entities):
    topic = entry.data[CONF_TOPIC]
    name = entry.data[CONF_NAME]
    signal = f"{DOMAIN}_{entry.entry_id}_update"

    async def message_received(msg):
        try:
            payload = json.loads(msg.payload)
        except Exception:
            _LOGGER.warning("Invalid Overdrive JSON payload: %s", msg.payload)
            return

        hass.data[DOMAIN][entry.entry_id]["data"] = payload
        hass.data[DOMAIN][entry.entry_id]["last_seen"] = datetime.now(timezone.utc)

        async_dispatcher_send(hass, signal)

    unsub = await mqtt.async_subscribe(hass, topic, message_received, 0)
    hass.data[DOMAIN][entry.entry_id]["listeners"].append(unsub)

    async_add_entities(
        [
            OverdriveBYDSensor(entry, name, signal, key, label, unit, device_class, entity_category, index)
            for key, label, unit, device_class, entity_category, index in SENSORS
        ]
    )


class OverdriveBYDSensor(SensorEntity):
    def __init__(self, entry, vehicle_name, signal, key, label, unit, device_class, entity_category, index=None):
        self.entry = entry
        self.vehicle_name = vehicle_name
        self.signal = signal
        self.key = key
        self.index = index

        suffix = f"_{index}" if index is not None else ""
        self._attr_name = f"{vehicle_name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{key}{suffix}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_entity_category = entity_category

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.vehicle_name,
            manufacturer="BYD",
            model="Overdrive MQTT Vehicle",
        )

    @property
    def native_value(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]
        value = data.get(self.key)

        if self.index is not None:
            if not isinstance(value, list) or len(value) <= self.index:
                return None
            value = value[self.index]

        if value in INVALID_VALUES:
            return None

        if self.key in ("utc", "vd_timestamp") and value:
            try:
                return datetime.fromtimestamp(value, timezone.utc).strftime("%Y-%m-%d %I:%M:%S %p")
            except Exception:
                return value

        if isinstance(value, float):
            return round(value, 3)

        return value

    @property
    def extra_state_attributes(self):
        data = self.hass.data[DOMAIN][self.entry.entry_id]["data"]

        if self.key == "vin":
            return None

        if self.index is None and isinstance(data.get(self.key), list):
            return {"raw": data.get(self.key)}

        return None

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.signal,
                self.async_write_ha_state,
            )
        )
