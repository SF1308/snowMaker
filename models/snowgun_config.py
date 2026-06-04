from .gun_type import GunType
from .gun_spec import GunSpec
from .primitives import Range as PressureRange

"""
Lookup table that returns a GunSpec based on the gun type.

Today the key is GunType (mono_fluid, bi_fluid).
In the future it can change to a specific manufacturer model (e.g. "TechnoAlpin TS22")
without needing to modify GunSpec — only the dictionary key would change.

Equivalent in JS/TS: Record<GunType, GunSpec>
"""

GUN_CONFIGS: dict[GunType, GunSpec] = {
    GunType.MONO_FLUID: GunSpec(
        gun_type=GunType.MONO_FLUID,
        nozzle_count=6,
        height_m=12.0,
        water_pressure=PressureRange(min=20.0, max=40.0),
        air_pressure=None,
        minimum_wet_bulb=-2.5,
    ),
    GunType.BI_FLUID: GunSpec(
        gun_type=GunType.BI_FLUID,
        nozzle_count=4,
        height_m=8.0,
        water_pressure=PressureRange(min=5.0, max=10.0),
        air_pressure=PressureRange(min=4.0, max=7.0),
        minimum_wet_bulb=-0.5,
    ),
}
