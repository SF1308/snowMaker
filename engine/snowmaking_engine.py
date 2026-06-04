from models.weather import Weather
from models.snowgun import SnowGun
from outputs.snowmaking_result import SnowmakingResult


class SnowmakingEngine:
    def run(
        self,
        weather: Weather,
        snowgun: SnowGun,
    ) -> SnowmakingResult:

        can_create_snow = weather.temperature <= 0

        production_rate = (
            snowgun.water_flow
            if can_create_snow
            else 0
        )

        quality = "GOOD" if weather.temperature < -5 else "WET"

        return SnowmakingResult(
            can_create_snow=can_create_snow,
            production_rate=production_rate,
            quality=quality,
        )
