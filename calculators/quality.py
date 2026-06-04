from dataclasses import dataclass


@dataclass(frozen=True)
class QualityResult:
    grade: str  # "A" | "B" | "C" | "—"
    grain_size_mm: float  # estimated crystal size in mm
    density_kgm3: float  # kg/m³
    description: str


class QualityCalculator:
    """
    Estimates snow quality from wet-bulb temperature.

    Colder → smaller crystals → denser, drier, better-quality snow.

    Grain size model (empirical approximation):
        grain_mm ≈ 0.8 − 0.06 × |Tw|   (clamped 0.2–0.8 mm)

    Density model:
        density ≈ 280 + 12 × |Tw|       (clamped 280–450 kg/m³)

    References:
    - Fierz et al. (2009) International Classification for Seasonal Snow
    - Pistenbully / TechnoAlpin operator guides
    """

    def calculate(self, wet_bulb: float) -> QualityResult:
        if wet_bulb > -2.0:
            return QualityResult(
                grade="—",
                grain_size_mm=0.0,
                density_kgm3=0.0,
                description="Sin producción",
            )

        abs_tw = abs(wet_bulb)

        grain_size = max(0.2, min(0.8, 0.8 - 0.06 * abs_tw))
        density = max(280.0, min(450.0, 280.0 + 12.0 * abs_tw))

        if wet_bulb <= -5.0:
            grade = "A"
            description = "Nieve seca, cristales finos, alta densidad"
        elif wet_bulb <= -2.0:
            grade = "B"
            description = "Nieve húmeda, cristales medianos"
        else:
            grade = "C"
            description = "Nieve marginal"

        return QualityResult(
            grade=grade,
            grain_size_mm=round(grain_size, 2),
            density_kgm3=round(density, 1),
            description=description,
        )
