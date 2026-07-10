from models.weather import Weather
from calculators.wet_bulb_calculator import WetBulbCalculator


weather = Weather(
    temperature=-5,
    humidity=50,
)

calculator = WetBulbCalculator()

wet_bulb = calculator.calculate(weather)

print(wet_bulb)
