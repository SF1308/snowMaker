import streamlit as st

from ui.weather import render_weather
from ui.snowgun import render_snowgun

from calculators.wet_bulb_calculator import WetBulbCalculator

st.title("Snow Maker Simulator")

left_col, right_col = st.columns(2)

with left_col:
    weather = render_weather()

with right_col:
    snowgun = render_snowgun()

calculator = WetBulbCalculator()

wet_bulb = calculator.calculate(weather)

if "samples" not in st.session_state:
    st.session_state.samples = []

if st.button("Add Sample"):
    st.session_state.samples.append(
        {
            "temperature": weather.temperature,
            "humidity": weather.humidity,
            "wet_bulb": wet_bulb,
        }
    )

st.table(st.session_state.samples)
