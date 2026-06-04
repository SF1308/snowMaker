import streamlit as st

from ui.weather import render_weather
from ui.snowgun import render_snowgun
from engine import SnowEngine

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Snow Maker Simulator",
    page_icon="❄️",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
}

/* Dark industrial background */
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}

/* Header */
h1, h2, h3 {
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.05em;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 1rem 1.2rem;
}

[data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #58a6ff !important;
}

[data-testid="stMetricLabel"] {
    color: #8b949e !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Sliders */
[data-testid="stSlider"] > div {
    color: #8b949e;
}

/* Subheader style */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #58a6ff;
    border-bottom: 1px solid #21262d;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Status badge */
.status-optimal {
    background: #0d4429;
    border: 1px solid #238636;
    color: #3fb950;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    display: inline-block;
}
.status-marginal {
    background: #2d1a00;
    border: 1px solid #9e6a03;
    color: #d29922;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    display: inline-block;
}
.status-impossible {
    background: #2d0d0d;
    border: 1px solid #8b1a1a;
    color: #f85149;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    display: inline-block;
}

/* Divider */
hr {
    border-color: #21262d !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
}

/* Quality grade badge */
.grade-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.5rem;
    font-weight: bold;
    line-height: 1;
}
.grade-A { color: #3fb950; }
.grade-B { color: #d29922; }
.grade-C { color: #f0883e; }
.grade-none { color: #8b949e; }

.mono {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #8b949e;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── Title ──────────────────────────────────────────────────────
st.markdown("# ❄️ SNOW MAKER SIMULATOR")
st.markdown(
    '<p class="mono">Physics-based artificial snow production engine · Stull (2011) wet-bulb model</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Inputs ─────────────────────────────────────────────────────
left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.markdown(
        '<p class="section-header">// Condiciones atmosféricas</p>',
        unsafe_allow_html=True,
    )
    weather = render_weather()

with right_col:
    st.markdown(
        '<p class="section-header">// Configuración del cañón</p>',
        unsafe_allow_html=True,
    )
    snowgun = render_snowgun()

st.markdown("---")

# ── Engine ─────────────────────────────────────────────────────
engine = SnowEngine()
result = engine.simulate(weather=weather, snowgun=snowgun)

v = result.viability
p = result.production
q = result.quality
e = result.energy

# ── Status header ──────────────────────────────────────────────
st.markdown(
    '<p class="section-header">// Resultado de la simulación</p>',
    unsafe_allow_html=True,
)

status_col, wb_col, desc_col = st.columns([1, 1, 2], gap="large")

with status_col:
    badge_class = f"status-{v.zone}"
    st.markdown(
        f'<div class="{badge_class}">{v.label.upper()}</div>', unsafe_allow_html=True
    )

with wb_col:
    st.metric("Bulbo Húmedo (Tw)", f"{result.wet_bulb:.2f} °C")

with desc_col:
    st.markdown(
        f'<p class="mono" style="margin-top:0.8rem">{v.description}</p>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Metrics grid ───────────────────────────────────────────────
if v.can_make_snow:
    # Row 1 — Production
    st.markdown('<p class="section-header">// Producción</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Caudal de agua", f"{p.water_flow_lpm:.1f} L/min")
    c2.metric("Volumen de nieve", f"{p.snow_volume_m3h:.2f} m³/h")
    c3.metric("Masa de nieve", f"{p.snow_mass_kgh:.0f} kg/h")

    st.markdown("---")

    # Row 2 — Quality + Energy
    q_col, e_col = st.columns(2, gap="large")

    with q_col:
        st.markdown(
            '<p class="section-header">// Calidad de nieve</p>', unsafe_allow_html=True
        )
        grade_class = f"grade-{q.grade}" if q.grade != "—" else "grade-none"
        st.markdown(
            f'<span class="grade-badge {grade_class}">{q.grade}</span>',
            unsafe_allow_html=True,
        )
        qc1, qc2 = st.columns(2)
        qc1.metric("Tamaño de cristal", f"{q.grain_size_mm:.2f} mm")
        qc2.metric("Densidad", f"{q.density_kgm3:.0f} kg/m³")
        st.markdown(f'<p class="mono">{q.description}</p>', unsafe_allow_html=True)

    with e_col:
        st.markdown(
            '<p class="section-header">// Consumo energético</p>',
            unsafe_allow_html=True,
        )
        ec1, ec2 = st.columns(2)
        ec1.metric("Potencia bomba", f"{e.pump_power_kw:.2f} kW")
        if e.compressor_power_kw > 0:
            ec2.metric("Potencia compresor", f"{e.compressor_power_kw:.2f} kW")
        else:
            ec2.metric("Compresor", "N/A")
        ec3, ec4 = st.columns(2)
        ec3.metric("Potencia total", f"{e.total_power_kw:.2f} kW")
        ec4.metric("Intensidad", f"{e.kwh_per_m3_snow:.2f} kWh/m³")

else:
    st.markdown(
        '<p class="mono" style="color:#f85149; padding: 2rem 0;">⚠ Las condiciones actuales no permiten producción de nieve artificial.<br>'
        "Reducir la temperatura o la humedad relativa para habilitar la operación.</p>",
        unsafe_allow_html=True,
    )

# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p class="mono" style="font-size:0.7rem">Modelo de bulbo húmedo: Stull (2011) · '
    "Densidad de nieve artificial: 350 kg/m³ · "
    "Rendimiento de bomba η=0.75 · "
    "Valores estimados — no usar para operaciones críticas</p>",
    unsafe_allow_html=True,
)
