from dataclasses import dataclass

from models.snowgun_type import SnowGunType
from models.snowgun_config import SNOWGUN_CONFIGS

@dataclass
class SnowGun:
    gun_type: SnowGunType # MONO_FLUID or BI_FLUID
    water_pressure_bar: float
    air_pressure_bar: float | None = None  # not used for mono-fluid guns
    minimum_wet_bulb: float | None = None  # to be filled from config

    def __post_init__(self):
        config = SNOWGUN_CONFIGS[self.gun_type]

        wp = config["water_pressure"]
        if not (wp.min_bar <= self.water_pressure_bar <= wp.max_bar):
            raise ValueError(
                f"Water pressure {self.water_pressure_bar} bar out of range "
                f"[{wp.min_bar}, {wp.max_bar}] for {self.gun_type.value}"
            )

        ap = config["air_pressure"]
        if ap is None and self.air_pressure_bar is not None:
            raise ValueError(f"{self.gun_type.value} does not use air pressure")
        if ap is not None:
            if self.air_pressure_bar is None:
                raise ValueError(f"{self.gun_type.value} requires air_pressure_bar")
            if not (ap.min_bar <= self.air_pressure_bar <= ap.max_bar):
                raise ValueError(
                    f"Air pressure {self.air_pressure_bar} bar out of range "
                    f"[{ap.min_bar}, {ap.max_bar}] for {self.gun_type.value}"
                )

        wet_bulb = config["minimum_wet_bulb"]
        if wet_bulb is not None:
            self.minimum_wet_bulb = wet_bulb

