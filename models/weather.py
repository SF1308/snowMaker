from dataclasses import dataclass

@dataclass
class Weather:
    temperature: float
    humidity: float
    wind_speed: float = 0.0

