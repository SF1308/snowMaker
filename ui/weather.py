# ui/weather.py

import streamlit as st

from models.weather import Weather


def render_weather() :
    st.subheader("Weather Conditions")

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

    wind_speed = st.slider(
        "Wind Speed (m/s)",
        min_value=0.0,
        max_value=20.0,
        value=0.0,
    )

    st.write(f"Wind Speed: {wind_speed} m/s")

    return Weather(
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
    )
