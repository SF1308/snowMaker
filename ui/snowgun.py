import streamlit as st

from models.snowgun import SnowGun
from models.gun_type import GunType
from models.snowgun_config import GUN_CONFIGS


def render_snowgun() -> SnowGun:
    st.subheader("Snow Gun")

    gun_type = st.selectbox(
        "Snow Gun Type",
        options=list(GunType),
        format_func=lambda t: t.value,
    )

    spec = GUN_CONFIGS[gun_type]

    water_pressure = st.slider(
        "Water Pressure (bar)",
        min_value=float(spec.water_pressure.min),
        max_value=float(spec.water_pressure.max),
        value=float(spec.water_pressure.min),
    )

    air_pressure = None

    if spec.air_pressure is not None:
        air_pressure = st.slider(
            "Air Pressure (bar)",
            min_value=float(spec.air_pressure.min),
            max_value=float(spec.air_pressure.max),
            value=float(spec.air_pressure.min),
        )

    return SnowGun(
        spec=spec,
        water_pressure_bar=water_pressure,
        air_pressure_bar=air_pressure,
    )
