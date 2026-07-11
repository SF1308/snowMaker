# ui/weather.py

import streamlit as st

from models.weather import Weather

# All user-facing text lives here. A future i18n layer only needs to
# swap this dict (e.g. import a STRINGS_ES instead) — the render
# logic below never changes.
STRINGS = {
    "subheader": "Weather Conditions",
    "temperature_label": "Temperature (°C)",
    "temperature_display": "Temperature: {value} °C",
    "humidity_label": "Relative Humidity (%)",
    "humidity_display": "Humidity: {value} %",
    "wind_label": "Wind Speed (m/s)",
    "wind_display": "Wind Speed: {value} m/s",
}


def render_weather() -> Weather:
    st.subheader(STRINGS["subheader"])

    temperature = st.slider(
        STRINGS["temperature_label"],
        min_value=-20.0,
        max_value=10.0,
        value=-5.0,
    )
    st.write(STRINGS["temperature_display"].format(value=temperature))

    humidity = st.slider(
        STRINGS["humidity_label"],
        min_value=0.0,
        max_value=100.0,
        value=50.0,
    )
    st.write(STRINGS["humidity_display"].format(value=humidity))

    wind_speed = st.slider(
        STRINGS["wind_label"],
        min_value=0.0,
        max_value=20.0,
        value=0.0,
    )
    st.write(STRINGS["wind_display"].format(value=wind_speed))

    return Weather(
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
    )
