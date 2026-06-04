from dataclasses import dataclass
from models.snowgun import SnowGun


@dataclass(frozen=True)
class ProductionResult:
    water_flow_lpm: float  # litros por minuto
    snow_volume_m3h: float  # m³ de nieve por hora
    snow_mass_kgh: float  # kg de nieve por hora


class ProductionCalculator:
    """
    Estimates snow production based on water flow and gun type.

    Simplified model:
    - Water flow (L/min) is estimated from water pressure using a
      generic orifice-flow relationship: Q ∝ nozzles × sqrt(pressure)
    - Snow conversion: 1 L water → ~3.5 L snow (density ~285 kg/m³)
      This varies with conditions, here we use a fixed approximation.

    References:
    - Guns and Snow, Lavanchy & Brun (2002)
    - TechnoAlpin technical specs
    """

    WATER_DENSITY_KGL = 1.0  # kg/L
    SNOW_DENSITY_KGM3 = 350.0  # kg/m³ — typical machine-made snow
    WATER_TO_SNOW_VOLUME = 3.0  # 1 L water → ~3 L snow (compacted)

    # Nozzle flow coefficient — empirical constant (L/min per nozzle at 1 bar)
    NOZZLE_K = 2.8

    def calculate(self, snowgun: SnowGun) -> ProductionResult:
        import math

        nozzles = snowgun.spec.nozzle_count
        water_pressure = snowgun.water_pressure_bar

        # Q = K × nozzles × sqrt(P)
        water_flow_lpm = self.NOZZLE_K * nozzles * math.sqrt(water_pressure)

        # Snow volume per hour
        water_flow_lph = water_flow_lpm * 60
        snow_volume_m3h = (water_flow_lph * self.WATER_TO_SNOW_VOLUME) / 1000

        # Snow mass per hour
        snow_mass_kgh = snow_volume_m3h * self.SNOW_DENSITY_KGM3

        return ProductionResult(
            water_flow_lpm=round(water_flow_lpm, 1),
            snow_volume_m3h=round(snow_volume_m3h, 2),
            snow_mass_kgh=round(snow_mass_kgh, 1),
        )
