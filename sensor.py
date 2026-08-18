from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfLength,
    UnitOfEnergy,
    UnitOfPower,
)

from .const import DOMAIN
from .entity import OverdriveBYDEntity, clean_value, get_array_value


@dataclass(frozen=True)
class OverdriveBYDSensorEntityDescription(SensorEntityDescription):
    array_key: str | None = None
    array_index: int | None = None


SENSORS: tuple[OverdriveBYDSensorEntityDescription, ...] = (
    OverdriveBYDSensorEntityDescription(
        key="soc",
        name="Battery Percentage",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="power",
        name="Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="speed",
        name="Speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="elevation",
        name="Elevation",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="ev_range_km",
        name="EV Range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="odometer",
        name="Odometer",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    OverdriveBYDSensorEntityDescription(
        key="ext_temp",
        name="Outside Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="inside_temp",
        name="Inside Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="batt_temp",
        name="Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="soh",
        name="Battery Health",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="capacity",
        name="Battery Capacity",
        native_unit_of_measurement="kWh",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="hv_pack_v",
        name="HV Pack Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="volt_12v",
        name="12V Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="cell_v_max",
        name="Max Cell Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="cell_v_min",
        name="Min Cell Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="cell_v_delta",
        name="Cell Voltage Delta",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="cell_t_max",
        name="Max Cell Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="cell_t_min",
        name="Min Cell Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="cell_t_avg",
        name="Average Cell Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="cell_t_delta",
        name="Cell Temperature Delta",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(key="gear", name="Gear"),
    OverdriveBYDSensorEntityDescription(key="vin", name="VIN"),
    OverdriveBYDSensorEntityDescription(
        key="consumption_50km",
        name="Consumption Last 50km",
        native_unit_of_measurement="kWh/100km",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="driving_time_hours",
        name="Driving Time",
        native_unit_of_measurement="h",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    OverdriveBYDSensorEntityDescription(
        key="total_elec_con",
        name="Total Electric Consumption",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    OverdriveBYDSensorEntityDescription(
        key="accel_pct",
        name="Accelerator Pedal",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="brake_pct",
        name="Brake Pedal",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="steering_deg",
        name="Steering Angle",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_p_fl",
        name="Front Left Tyre Pressure",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_p_fr",
        name="Front Right Tyre Pressure",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_p_rl",
        name="Rear Left Tyre Pressure",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_p_rr",
        name="Rear Right Tyre Pressure",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_t_fl",
        name="Front Left Tyre Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_t_fr",
        name="Front Right Tyre Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_t_rl",
        name="Rear Left Tyre Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(
        key="tyre_t_rr",
        name="Rear Right Tyre Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    OverdriveBYDSensorEntityDescription(key="charging_state", name="Charging State"),
    OverdriveBYDSensorEntityDescription(key="charger_state", name="Charger State"),
    OverdriveBYDSensorEntityDescription(key="charging_mode", name="Charging Mode"),
    OverdriveBYDSensorEntityDescription(key="charging_gun", name="Charging Gun"),
    OverdriveBYDSensorEntityDescription(key="charging_type", name="Charging Type"),
    OverdriveBYDSensorEntityDescription(key="charging_v2l", name="V2L Charging"),
    OverdriveBYDSensorEntityDescription(key="ac_fan", name="AC Fan"),
    OverdriveBYDSensorEntityDescription(key="ac_cycle", name="AC Cycle"),
    OverdriveBYDSensorEntityDescription(key="ac_wind", name="AC Wind Mode"),
    OverdriveBYDSensorEntityDescription(key="sunroof_state", name="Sunroof State"),
    OverdriveBYDSensorEntityDescription(key="sunroof_pos", name="Sunroof Position"),
    OverdriveBYDSensorEntityDescription(key="power_level", name="Power Level"),
    OverdriveBYDSensorEntityDescription(key="mcu_status", name="MCU Status"),
    OverdriveBYDSensorEntityDescription(key="energy_mode", name="Energy Mode"),
    OverdriveBYDSensorEntityDescription(key="op_mode", name="Operation Mode"),
    OverdriveBYDSensorEntityDescription(key="key_start_state", name="Key Start State"),
    OverdriveBYDSensorEntityDescription(key="key_detection_reminder", name="Key Detection Reminder"),
    OverdriveBYDSensorEntityDescription(key="smart_key_warn", name="Smart Key Warning"),
    OverdriveBYDSensorEntityDescription(key="vd_timestamp", name="Vehicle Data Timestamp"),
    OverdriveBYDSensorEntityDescription(key="utc", name="Telemetry UTC"),
)


ARRAY_SENSORS: tuple[OverdriveBYDSensorEntityDescription, ...] = (
    OverdriveBYDSensorEntityDescription(key="radar_front_left", name="Radar Front Left", array_key="radar_distances", array_index=0),
    OverdriveBYDSensorEntityDescription(key="radar_front_mid_left", name="Radar Front Mid Left", array_key="radar_distances", array_index=1),
    OverdriveBYDSensorEntityDescription(key="radar_front_mid_right", name="Radar Front Mid Right", array_key="radar_distances", array_index=2),
    OverdriveBYDSensorEntityDescription(key="radar_front_right", name="Radar Front Right", array_key="radar_distances", array_index=3),
    OverdriveBYDSensorEntityDescription(key="radar_rear_left", name="Radar Rear Left", array_key="radar_distances", array_index=4),
    OverdriveBYDSensorEntityDescription(key="radar_rear_mid_left", name="Radar Rear Mid Left", array_key="radar_distances", array_index=5),
    OverdriveBYDSensorEntityDescription(key="radar_rear_mid_right", name="Radar Rear Mid Right", array_key="radar_distances", array_index=6),
    OverdriveBYDSensorEntityDescription(key="radar_rear_right", name="Radar Rear Right", array_key="radar_distances", array_index=7),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [OverdriveBYDSensor(coordinator, description) for description in SENSORS]
    entities += [OverdriveBYDSensor(coordinator, description) for description in ARRAY_SENSORS]

    async_add_entities(entities)


class OverdriveBYDSensor(OverdriveBYDEntity, SensorEntity):
    def __init__(self, coordinator, description: OverdriveBYDSensorEntityDescription) -> None:
        super().__init__(coordinator, description)

        self._attr_unique_id = f"overdrive_byd_{description.key}"

    @property
    def native_value(self):
        description = self.entity_description

        if description.array_key is not None and description.array_index is not None:
            return get_array_value(
                self.coordinator.data,
                description.array_key,
                description.array_index,
            )

        return clean_value(self.coordinator.data.get(description.key))
