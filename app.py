import streamlit as st
from models.weather import Weather

from calculators.wet_bulb_calculator import WetBulbCalculator

st.title("Snow Maker Simulator")

temperature = st.slider(
    "Temperature (°C)",
    min_value=-20.0,
    max_value=10.0,
    value=-5.0,
)
st.write(f"Temperature: {temperature} °C")

humidity = st.slider(
    "Relative Humidity (%)",
    min_value=0.0,
    max_value=100.0,
    value=50.0,
)

st.write(f"Humidity: {humidity} %")

calculator = WetBulbCalculator()

weather = Weather(
    temperature=temperature,
    humidity=humidity,
)

wet_bulb = calculator.calculate(weather)

if "samples" not in st.session_state:
    st.session_state.samples = []

if st.button("Add Sample"):
    st.session_state.samples.append(
        {
            "temperature": temperature,
            "humidity": humidity,
            "wet_bulb": wet_bulb,
        }
    )

st.table(st.session_state.samples)
