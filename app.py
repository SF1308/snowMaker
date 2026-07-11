import streamlit as st

from engine import SnowEngine
from ui.footer import render_footer
from ui.weather import render_weather
from ui.snowgun import render_snowgun
from ui.styles import inject
from ui.tooltips import TIPS, chart_label
from ui.charts import wet_bulb_gauge, production_bar, quality_bars, energy_pie
from ui.simulation import (
    render_start_button,
    run_simulation_sequence,
    render_status_card,
    render_results_dashboard,
)

# All page-level text lives here. A future i18n layer only needs to
# swap this dict — the layout/logic below never changes.
STRINGS = {
    "page_title": "Snow Maker Simulator",
    "heading": "# ❄️ SNOW MAKER SIMULATOR",
    "subtitle": "Physics-based artificial snow production engine · Stull (2011) wet-bulb model",
    "sidebar_sim_title": "#### 🎮 You are on: Simulator",
    "sidebar_sim_caption": (
        "Configure weather and gun, then press "
        "**❄️ Start Simulation** to see the results."
    ),
    "sidebar_docs_title": "#### 📚 Documentation",
    "sidebar_docs_caption": (
        "The other pages in the menu above (Snowmaking, Architecture, "
        "Technical) are reference guides for the project — they are "
        "not part of the simulator."
    ),
    "section_start": "// 1. Start Simulation",
    "section_weather": "// 2. Weather Conditions",
    "section_snowgun": "// 3. Snow Gun Configuration",
    "section_progress": "// 4. Simulation Progress",
    "section_results": "// 5. Simulation Results",
    "tabs": ["📋  Dashboard", "📊  Charts"],
    "no_snow_warning": (
        "⚠ Current conditions do not allow artificial snow production.<br>"
        "Lower the temperature or relative humidity to enable operation."
    ),
    "no_snow_charts_note": "⚠ No production — the other charts activate when Tw ≤ −2 °C.",
    "empty_state_hint": (
        "Adjust the weather and gun parameters, then press "
        "**❄️ START SNOWMAKING** to run the simulation."
    ),
    "chart_labels": {
        "wet_bulb": "Wet Bulb Temperature",
        "production": "Hourly Production",
        "quality": "Snow Quality",
        "energy": "Consumption Breakdown",
    },
    "footer_note": (
        "Wet-bulb model: Stull (2011) · "
        "Artificial snow density: 350 kg/m³ · "
        "Pump efficiency η=0.75 · "
        "Estimated values — do not use for critical operations"
    ),
}

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title=STRINGS["page_title"],
    page_icon="❄️",
    layout="wide",
)
inject()

# ── Sidebar legend ─────────────────────────────────────────────
# Streamlit renders the auto-generated page navigation (this app +
# everything in pages/) at the very top of the sidebar, above anything
# we add here. This block acts as a caption/legend right below it so
# it's clear which entry is the simulator and which are documentation.
with st.sidebar:
    st.markdown("---")
    st.markdown(STRINGS["sidebar_sim_title"])
    st.caption(STRINGS["sidebar_sim_caption"])
    st.markdown(STRINGS["sidebar_docs_title"])
    st.caption(STRINGS["sidebar_docs_caption"])

# ── Session state ──────────────────────────────────────────────
# The simulation no longer runs on every widget change. Inputs are
# only "committed" and simulated when the user presses the CTA button.
st.session_state.setdefault("result", None)
st.session_state.setdefault("simulating", False)
st.session_state.setdefault("pending_weather", None)
st.session_state.setdefault("pending_snowgun", None)

# ── Title ──────────────────────────────────────────────────────
st.markdown(STRINGS["heading"])
st.markdown(
    f'<p class="mono">{STRINGS["subtitle"]}</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── 1. Start simulation (top CTA) ─────────────────────────────
st.markdown(
    f'<p class="section-header">{STRINGS["section_start"]}</p>',
    unsafe_allow_html=True,
)

cta_col, _spacer_l, _spacer_r = st.columns([2, 1, 1])
with cta_col:
    top_start_clicked = render_start_button()

st.markdown("---")

# ── 2. Weather + Snowgun — single row, two columns ─────────────
left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.markdown(
        f'<p class="section-header">{STRINGS["section_weather"]}</p>',
        unsafe_allow_html=True,
    )
    weather = render_weather()

with right_col:
    st.markdown(
        f'<p class="section-header">{STRINGS["section_snowgun"]}</p>',
        unsafe_allow_html=True,
    )
    snowgun = render_snowgun()

st.markdown("---")

if top_start_clicked and not st.session_state.simulating:
    # Snapshot the current inputs so the animation/calc use exactly
    # what the user had configured at the moment of the click.
    st.session_state.pending_weather = weather
    st.session_state.pending_snowgun = snowgun
    st.session_state.simulating = True
    st.rerun()

# ── 4. Simulation progress ────────────────────────────────────
if st.session_state.simulating:
    st.markdown(
        f'<p class="section-header">{STRINGS["section_progress"]}</p>',
        unsafe_allow_html=True,
    )
    result = run_simulation_sequence(
        SnowEngine(),
        st.session_state.pending_weather,
        st.session_state.pending_snowgun,
    )
    st.session_state.result = result
    st.session_state.simulating = False
    st.rerun()

# ── 5. Results ─────────────────────────────────────────────────
result = st.session_state.result

if result is not None:
    v = result.viability
    p = result.production
    q = result.quality
    e = result.energy

    st.markdown("---")
    st.markdown(
        f'<p class="section-header">{STRINGS["section_results"]}</p>',
        unsafe_allow_html=True,
    )

    render_status_card(result)

    metrics_tab, charts_tab = st.tabs(STRINGS["tabs"])

    # ── Metrics tab ────────────────────────────────────────────
    with metrics_tab:
        if not v.can_make_snow:
            st.markdown(
                f'<p class="mono" style="color:#f85149; padding: 2rem 0;">'
                f"{STRINGS['no_snow_warning']}</p>",
                unsafe_allow_html=True,
            )
        else:
            render_results_dashboard(result)

    # ── Charts tab ─────────────────────────────────────────────
    with charts_tab:
        cl = STRINGS["chart_labels"]
        if not v.can_make_snow:
            g_col, _ = st.columns([1, 1])
            with g_col:
                chart_label(cl["wet_bulb"], *TIPS["chart_gauge"])
                st.plotly_chart(
                    wet_bulb_gauge(result.wet_bulb), use_container_width=True
                )
            st.markdown(
                f'<p class="mono" style="color:#f85149; padding: 1rem 0;">'
                f"{STRINGS['no_snow_charts_note']}</p>",
                unsafe_allow_html=True,
            )
        else:
            gauge_col, prod_col = st.columns(2, gap="large")
            with gauge_col:
                chart_label(cl["wet_bulb"], *TIPS["chart_gauge"])
                st.plotly_chart(
                    wet_bulb_gauge(result.wet_bulb), use_container_width=True
                )
            with prod_col:
                chart_label(cl["production"], *TIPS["chart_prod"])
                st.plotly_chart(production_bar(p), use_container_width=True)

            qual_col, ener_col = st.columns(2, gap="large")
            with qual_col:
                chart_label(cl["quality"], *TIPS["chart_radar"])
                st.plotly_chart(quality_bars(q), use_container_width=True)
            with ener_col:
                chart_label(cl["energy"], *TIPS["chart_pie"])
                st.plotly_chart(energy_pie(e), use_container_width=True)
else:
    st.info(STRINGS["empty_state_hint"])

# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<p class="mono" style="font-size:0.7rem">{STRINGS["footer_note"]}</p>',
    unsafe_allow_html=True,
)

render_footer()
