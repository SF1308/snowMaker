from dataclasses import dataclass
from models.snowgun_type import SnowGunType

@dataclass(frozen=True)
class PressureRange:
    min_bar: float
    max_bar: float

SNOWGUN_CONFIGS: dict[SnowGunType, dict] = {
    SnowGunType.MONO_FLUID: {
        "water_pressure": PressureRange(min_bar=20.0, max_bar=40.0),
        "air_pressure":   None,   # no usa aire
    },
    SnowGunType.BI_FLUID: {
        "water_pressure": PressureRange(min_bar=5.0,  max_bar=10.0),
        "air_pressure":   PressureRange(min_bar=4.0,  max_bar=7.0),
    },
}
