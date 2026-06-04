from dataclasses import dataclass


@dataclass
class SnowmakingResult:
    can_create_snow: bool
    production_rate: float
    quality: str
