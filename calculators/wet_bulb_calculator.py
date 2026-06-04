import math

from models.weather import Weather


class WetBulbCalculator:
  def calculate(self, weather: Weather) -> float:
        temperature = weather.temperature
        relative_humidity = weather.humidity

        return (
            temperature
            * math.atan(
                0.151977
                * math.sqrt(relative_humidity + 8.313659)
            )
            + math.atan(
                temperature + relative_humidity
            )
            - math.atan(
                relative_humidity - 1.676331
            )
            + (
                0.00391838
                * relative_humidity**1.5
                * math.atan(
                    0.023101 * relative_humidity
                )
            )
            - 4.686035
        )

