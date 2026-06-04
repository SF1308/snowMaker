from enum import Enum


class GunType(Enum):
    MONO_FLUID = "mono_fluid"  # fan gun — alta presión agua, sin aire
    BI_FLUID = "bi_fluid"  # lance   — agua + aire comprimido
