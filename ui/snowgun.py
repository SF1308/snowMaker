import streamlit as st

from models.snowgun import SnowGun
from models.gun_type import GunType
from models.snowgun_config import GUN_CONFIGS

# All user-facing text lives here. A future i18n layer only needs to
# swap this dict — the render logic below never changes.
STRINGS = {
    "subheader": "Snow Gun",
    "gun_type_label": "Snow Gun Type",
    "gun_type_names": {
        GunType.MONO_FLUID: "Mono-fluid (water only)",
        GunType.BI_FLUID: "Bi-fluid (water + air)",
    },
    "water_pressure_label": "Water Pressure (bar)",
    "air_pressure_label": "Air Pressure (bar)",
}


def render_snowgun() -> SnowGun:
    st.subheader(STRINGS["subheader"])

    gun_type = st.selectbox(
        STRINGS["gun_type_label"],
        options=list(GunType),
        format_func=lambda t: STRINGS["gun_type_names"].get(t, t.value),
    )

    spec = GUN_CONFIGS[gun_type]

    water_pressure = st.slider(
        STRINGS["water_pressure_label"],
        min_value=float(spec.water_pressure.min),
        max_value=float(spec.water_pressure.max),
        value=float(spec.water_pressure.min),
    )

    air_pressure = None

    if spec.air_pressure is not None:
        air_pressure = st.slider(
            STRINGS["air_pressure_label"],
            min_value=float(spec.air_pressure.min),
            max_value=float(spec.air_pressure.max),
            value=float(spec.air_pressure.min),
        )

    return SnowGun(
        spec=spec,
        water_pressure_bar=water_pressure,
        air_pressure_bar=air_pressure,
    )
