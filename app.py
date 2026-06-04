import streamlit as st

from ui.weather import render_weather
from ui.snowgun import render_snowgun

from engine import SnowEngine


st.title("Snow Maker Simulator")

left_col, right_col = st.columns(2)

with left_col:
    weather = render_weather()

with right_col:
    snowgun = render_snowgun()

engine = SnowEngine()

result = engine.simulate(
    weather=weather,
    snowgun=snowgun,
)

st.divider()

st.subheader("Simulation")

st.write(f"Wet Bulb Temperature: {result.wet_bulb:.2f} °C")

if result.can_make_snow:
    st.success("Snow production is possible.")
else:
    st.error("Snow production is not possible.")
