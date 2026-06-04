import streamlit as st

from models.snowgun import SnowGun
from models.snowgun_type import SnowGunType
from models.snowgun_config import SNOWGUN_CONFIGS


def render_snowgun() -> SnowGun:
    st.subheader("Snow Gun")

    gun_type = st.selectbox(
        "Snow Gun Type",
        options=list(SnowGunType),
        format_func=lambda t: t.value,
    )

    config = SNOWGUN_CONFIGS[gun_type]

    water_pressure = st.slider(
        "Water Pressure (bar)",
        min_value=float(config["water_pressure"].min_bar),
        max_value=float(config["water_pressure"].max_bar),
        value=float(config["water_pressure"].min_bar),
    )

    air_pressure = None

    if config["air_pressure"] is not None:
        air_pressure = st.slider(
            "Air Pressure (bar)",
            min_value=float(config["air_pressure"].min_bar),
            max_value=float(config["air_pressure"].max_bar),
            value=float(config["air_pressure"].min_bar),
        )


    return SnowGun(
        gun_type=gun_type,
        water_pressure_bar=water_pressure,
        air_pressure_bar=air_pressure,
        minimum_wet_bulb=config["minimum_wet_bulb"],
    )
