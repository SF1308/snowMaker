from dataclasses import dataclass
from models.snowgun import SnowGun


@dataclass(frozen=True)
class EnergyResult:
    pump_power_kw: float  # estimated pump power draw
    compressor_power_kw: float  # compressor (0 for mono-fluid)
    total_power_kw: float  # total electrical draw
    kwh_per_m3_snow: float  # energy intensity


class EnergyCalculator:
    """
    Estimates electrical energy consumption of the snowgun system.

    Pump model:
        P_pump = (Q × ΔP) / η_pump
        where Q in m³/s, ΔP in Pa, η_pump = 0.75 (typical centrifugal pump)

    Compressor model (bi-fluid only):
        P_comp = (Q_air × P_air) / η_comp
        Approximate air flow = 0.06 m³/s per bar of pressure
        η_comp = 0.70

    All values in SI units internally, output in kW.
    """

    ETA_PUMP = 0.75
    ETA_COMP = 0.70
    AIR_FLOW_PER_BAR = 0.06  # m³/s — rough approximation

    def calculate(
        self,
        snowgun: SnowGun,
        water_flow_lpm: float,
        snow_volume_m3h: float,
    ) -> EnergyResult:
        # Convert units
        q_water_m3s = (water_flow_lpm / 1000) / 60  # L/min → m³/s
        delta_p_pa = snowgun.water_pressure_bar * 1e5  # bar → Pa

        pump_power_w = (q_water_m3s * delta_p_pa) / self.ETA_PUMP
        pump_power_kw = pump_power_w / 1000

        compressor_power_kw = 0.0
        if snowgun.air_pressure_bar is not None:
            q_air_m3s = self.AIR_FLOW_PER_BAR * snowgun.air_pressure_bar
            p_air_pa = snowgun.air_pressure_bar * 1e5
            comp_power_w = (q_air_m3s * p_air_pa) / self.ETA_COMP
            compressor_power_kw = comp_power_w / 1000

        total_kw = pump_power_kw + compressor_power_kw

        # kWh per m³ of snow produced
        if snow_volume_m3h > 0:
            kwh_per_m3 = total_kw / snow_volume_m3h
        else:
            kwh_per_m3 = 0.0

        return EnergyResult(
            pump_power_kw=round(pump_power_kw, 2),
            compressor_power_kw=round(compressor_power_kw, 2),
            total_power_kw=round(total_kw, 2),
            kwh_per_m3_snow=round(kwh_per_m3, 2),
        )
