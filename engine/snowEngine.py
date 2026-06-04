from calculators.wet_bulb_calculator import WetBulbCalculator
from calculators.viability import ViabilityCalculator
from calculators.production import ProductionCalculator
from calculators.quality import QualityCalculator
from calculators.energy import EnergyCalculator
from models.output.simulation_result import SimulationResult


class SnowEngine:
    def __init__(self):
        self.wet_bulb_calculator = WetBulbCalculator()
        self.viability_calculator = ViabilityCalculator()
        self.production_calculator = ProductionCalculator()
        self.quality_calculator = QualityCalculator()
        self.energy_calculator = EnergyCalculator()

    def simulate(self, weather, snowgun) -> SimulationResult:
        wet_bulb = self.wet_bulb_calculator.calculate(weather)

        viability = self.viability_calculator.calculate(wet_bulb)
        production = self.production_calculator.calculate(snowgun)
        quality = self.quality_calculator.calculate(wet_bulb)
        energy = self.energy_calculator.calculate(
            snowgun=snowgun,
            water_flow_lpm=production.water_flow_lpm,
            snow_volume_m3h=production.snow_volume_m3h,
        )

        return SimulationResult(
            wet_bulb=wet_bulb,
            viability=viability,
            production=production,
            quality=quality,
            energy=energy,
        )
