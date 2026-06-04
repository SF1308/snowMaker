from dataclasses import dataclass


@dataclass(frozen=True)
class Range:
    min: float
    max: float
