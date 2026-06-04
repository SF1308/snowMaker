from dataclasses import dataclass
from calculators.viability import ViabilityResult
from calculators.production import ProductionResult
from calculators.quality import QualityResult
from calculators.energy import EnergyResult


@dataclass
class SimulationResult:
    wet_bulb: float
    viability: ViabilityResult
    production: ProductionResult
    quality: QualityResult
    energy: EnergyResult

    # Convenience properties for backward compatibility
    @property
    def can_make_snow(self) -> bool:
        return self.viability.can_make_snow
