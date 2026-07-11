"""
ui/simulation.py
Presentation-layer helpers for the manual "Start Snowmaking" flow:
the CTA button, the animated simulation sequence, the overall status
card, and the results dashboard of info cards.

None of this touches calculation logic — it only orchestrates *when*
SnowEngine.simulate() is called and *how* the result is displayed.
"""

import time
import streamlit as st

from models.output.simulation_result import SimulationResult

# All user-facing text lives here. A future i18n layer only needs to
# swap this dict — the render logic below never changes.
STRINGS = {
    "button_idle": "❄️  START SNOWMAKING",
    "button_running": "⏳  SIMULATING...",
    "sequence_steps": [
        ("❄️", "Reading weather conditions..."),
        ("💧", "Pressurizing water system..."),
        ("🌬️", "Atomizing water droplets..."),
        ("✨", "Growing snow crystals..."),
        ("🏔️", "Generating simulation results..."),
    ],
    "status": {
        "optimal": ("🟢", "Excellent Snowmaking Conditions", "status-card-optimal"),
        "marginal": ("🟡", "Marginal Conditions", "status-card-marginal"),
        "impossible": ("🔴", "Snowmaking Not Possible", "status-card-impossible"),
    },
    "status_unknown": ("⚪", "Unknown", ""),
    "cards": {
        "wet_bulb": "Wet Bulb Temp",
        "quality": "Snow Quality",
        "production": "Snow Production",
        "water_flow": "Water Flow",
        "air_consumption": "Air Consumption",
        "air_consumption_sub": "Compressor power",
        "total_power": "Total Power",
    },
}

_TOTAL_DURATION_S = 2.0


def render_start_button() -> bool:
    """Render the main call-to-action button. Returns True on click."""
    is_running = st.session_state.get("simulating", False)
    st.markdown('<div class="start-btn-wrap">', unsafe_allow_html=True)
    clicked = st.button(
        STRINGS["button_running"] if is_running else STRINGS["button_idle"],
        use_container_width=True,
        type="primary",
        disabled=is_running,
        key="start_simulation_btn",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return clicked


def run_simulation_sequence(engine, weather, snowgun) -> SimulationResult:
    """
    Play the ~2s animated sequence, then run the real (unchanged)
    simulation and return its result. The animation is cosmetic only.
    """
    text_slot = st.empty()
    progress_slot = st.progress(0)

    steps = STRINGS["sequence_steps"]
    n = len(steps)
    step_duration = _TOTAL_DURATION_S / n

    for i, (icon, message) in enumerate(steps):
        text_slot.markdown(
            f'<div class="sim-step">'
            f'<span class="sim-step-icon">{icon}</span>'
            f'<span class="sim-step-text">{message}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        progress_slot.progress(int(((i + 1) / n) * 100))
        time.sleep(step_duration)

    # The actual, unmodified calculation:
    result = engine.simulate(weather=weather, snowgun=snowgun)

    text_slot.empty()
    progress_slot.empty()

    return result


def render_status_card(result: SimulationResult) -> None:
    """Prominent overall status card shown above the results dashboard."""
    v = result.viability
    icon, title, css_class = STRINGS["status"].get(v.zone, STRINGS["status_unknown"])

    st.markdown(
        f"""
        <div class="status-card {css_class} fade-in">
            <div class="status-card-icon">{icon}</div>
            <div class="status-card-body">
                <div class="status-card-title">{title}</div>
                <div class="status-card-desc">{v.description}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _info_card_html(icon: str, label: str, value: str, subtitle: str = "") -> str:
    subtitle_html = f'<div class="info-card-sub">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="info-card fade-in">
        <div class="info-card-icon">{icon}</div>
        <div class="info-card-label">{label}</div>
        <div class="info-card-value">{value}</div>
        {subtitle_html}
    </div>
    """


def render_results_dashboard(result: SimulationResult) -> None:
    """Grid of info cards summarizing the simulation result."""
    p = result.production
    q = result.quality
    e = result.energy
    c = STRINGS["cards"]

    cards = [
        ("🌡️", c["wet_bulb"], f"{result.wet_bulb:.2f} °C", ""),
        (
            "❄️",
            c["quality"],
            q.grade if q.grade != "—" else "N/A",
            q.description,
        ),
        (
            "🏔️",
            c["production"],
            f"{p.snow_volume_m3h:.2f} m³/h",
            f"{p.snow_mass_kgh:.0f} kg/h",
        ),
        ("💧", c["water_flow"], f"{p.water_flow_lpm:.1f} L/min", ""),
    ]

    if e.compressor_power_kw > 0:
        cards.append(
            (
                "🌬️",
                c["air_consumption"],
                f"{e.compressor_power_kw:.2f} kW",
                c["air_consumption_sub"],
            )
        )

    cards.append(
        (
            "⚡",
            c["total_power"],
            f"{e.total_power_kw:.2f} kW",
            f"{e.kwh_per_m3_snow:.2f} kWh/m³",
        )
    )

    cols = st.columns(3, gap="medium")
    for i, (icon, label, value, subtitle) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(
                _info_card_html(icon, label, value, subtitle), unsafe_allow_html=True
            )
