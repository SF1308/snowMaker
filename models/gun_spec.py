from dataclasses import dataclass
from models.gun_type import GunType
from models.primitives import Range as PressureRange


@dataclass(frozen=True)
class GunSpec:
    gun_type: GunType
    nozzle_count: int
    height_m: float
    water_pressure: PressureRange
    air_pressure: PressureRange | None
    minimum_wet_bulb: float
