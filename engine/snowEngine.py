from calculators.wet_bulb_calculator import WetBulbCalculator
from models.output.simulation_result import SimulationResult


class SnowEngine:
    def __init__(self):
        self.wet_bulb_calculator = WetBulbCalculator()

    def simulate(self, weather, snowgun):

        wet_bulb = self.wet_bulb_calculator.calculate(weather)

        can_make_snow = wet_bulb <= snowgun.spec.minimum_wet_bulb

        return SimulationResult(
            wet_bulb=wet_bulb,
            can_make_snow=can_make_snow,
        )
