from dataclasses import dataclass
from .gun_spec import GunSpec


@dataclass
class SnowGun:
    spec: GunSpec
    water_pressure_bar: float
    air_pressure_bar: float | None = None

    def __post_init__(self):
        # validar agua
        wp = self.spec.water_pressure
        if not (wp.min <= self.water_pressure_bar <= wp.max):
            raise ValueError(
                f"Water pressure {self.water_pressure_bar} bar out of range "
                f"[{wp.min}, {wp.max}]"
            )

        # validar aire
        ap = self.spec.air_pressure
        if ap is None and self.air_pressure_bar is not None:
            raise ValueError("This gun type does not use air pressure")
        if ap is not None:
            if self.air_pressure_bar is None:
                raise ValueError("This gun type requires air_pressure_bar")
            if not (ap.min <= self.air_pressure_bar <= ap.max):
                raise ValueError(
                    f"Air pressure {self.air_pressure_bar} bar out of range "
                    f"[{ap.min}, {ap.max}]"
                )
