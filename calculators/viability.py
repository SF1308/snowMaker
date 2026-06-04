from dataclasses import dataclass


@dataclass(frozen=True)
class ViabilityResult:
    can_make_snow: bool
    zone: str  # "optimal" | "marginal" | "impossible"
    label: str  # human-readable label
    description: str


class ViabilityCalculator:
    """
    Determines snowmaking viability from wet-bulb temperature.

    Industry thresholds (Tw):
        Tw > -2°C      → impossible
        -5°C < Tw ≤ -2°C → marginal (wet, heavy snow)
        Tw ≤ -5°C      → optimal (dry, high-quality snow)
    """

    THRESHOLD_IMPOSSIBLE = -2.0
    THRESHOLD_MARGINAL = -5.0

    def calculate(self, wet_bulb: float) -> ViabilityResult:
        if wet_bulb > self.THRESHOLD_IMPOSSIBLE:
            return ViabilityResult(
                can_make_snow=False,
                zone="impossible",
                label="No viable",
                description="La temperatura de bulbo húmedo es demasiado alta para producir nieve.",
            )
        elif wet_bulb > self.THRESHOLD_MARGINAL:
            return ViabilityResult(
                can_make_snow=True,
                zone="marginal",
                label="Producción marginal",
                description="Nieve húmeda y pesada. Rendimiento reducido.",
            )
        else:
            return ViabilityResult(
                can_make_snow=True,
                zone="optimal",
                label="Producción óptima",
                description="Condiciones ideales. Nieve seca y de alta calidad.",
            )
