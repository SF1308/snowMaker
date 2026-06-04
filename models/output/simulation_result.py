from dataclasses import dataclass


@dataclass
class SimulationResult:
    wet_bulb: float
    can_make_snow: bool
    #production_rate: float
    #quality: str
