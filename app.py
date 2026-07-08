import streamlit as st

from engine import SnowEngine
from ui.footer import render_footer
from ui.weather import render_weather
from ui.snowgun import render_snowgun
from ui.styles import inject
from ui.tooltips import TIPS, tip, metric_card, section_header, chart_label
from ui.charts import wet_bulb_gauge, production_bar, quality_bars, energy_pie

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Snow Maker Simulator",
    page_icon="❄️",
    layout="wide",
)
inject()

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

# ── Simulation ─────────────────────────────────────────────────
result = SnowEngine().simulate(weather=weather, snowgun=snowgun)
v = result.viability
p = result.production
q = result.quality
e = result.energy

# ── Status row ─────────────────────────────────────────────────
section_header("// Resultado de la simulación", *TIPS["simulacion"])

status_col, wb_col, desc_col = st.columns([1, 1, 2], gap="large")

with status_col:
    st.markdown(tip("Estado", *TIPS["viabilidad"]), unsafe_allow_html=True)
    st.markdown(
        f'<div class="status-{v.zone}">{v.label.upper()}</div>', unsafe_allow_html=True
    )

with wb_col:
    metric_card(
        wb_col, "Bulbo Húmedo (Tw)", f"{result.wet_bulb:.2f} °C", *TIPS["wet_bulb"]
    )

with desc_col:
    st.markdown(
        f'<p class="mono" style="margin-top:2rem">{v.description}</p>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────
metrics_tab, charts_tab = st.tabs(["📋  Métricas", "📊  Gráficos"])

# ── Metrics tab ────────────────────────────────────────────────
with metrics_tab:
    if not v.can_make_snow:
        st.markdown(
            '<p class="mono" style="color:#f85149; padding: 2rem 0;">'
            "⚠ Las condiciones actuales no permiten producción de nieve artificial.<br>"
            "Reducir la temperatura o la humedad relativa para habilitar la operación.</p>",
            unsafe_allow_html=True,
        )
    else:
        # Production
        section_header("// Producción", *TIPS["produccion"])
        c1, c2, c3 = st.columns(3)
        metric_card(
            c1, "Caudal de agua", f"{p.water_flow_lpm:.1f} L/min", *TIPS["caudal"]
        )
        metric_card(
            c2,
            "Volumen de nieve",
            f"{p.snow_volume_m3h:.2f} m³/h",
            *TIPS["volumen_nieve"],
        )
        metric_card(
            c3, "Masa de nieve", f"{p.snow_mass_kgh:.0f} kg/h", *TIPS["masa_nieve"]
        )

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.markdown("---")

        q_col, e_col = st.columns(2, gap="large")

        # Quality
        with q_col:
            section_header("// Calidad de nieve", *TIPS["calidad"])
            grade_class = f"grade-{q.grade}" if q.grade != "—" else "grade-none"
            st.markdown(
                tip("Calificación", *TIPS["grado_calidad"]), unsafe_allow_html=True
            )
            st.markdown(
                f'<span class="grade-badge {grade_class}">{q.grade}</span>',
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            qc1, qc2 = st.columns(2)
            metric_card(
                qc1, "Tamaño de cristal", f"{q.grain_size_mm:.2f} mm", *TIPS["cristal"]
            )
            metric_card(
                qc2, "Densidad", f"{q.density_kgm3:.0f} kg/m³", *TIPS["densidad"]
            )
            st.markdown(
                f'<p class="mono" style="margin-top:0.6rem">{q.description}</p>',
                unsafe_allow_html=True,
            )

        # Energy
        with e_col:
            section_header("// Consumo energético", *TIPS["energia"])
            ec1, ec2 = st.columns(2)
            metric_card(
                ec1, "Potencia bomba", f"{e.pump_power_kw:.2f} kW", *TIPS["bomba"]
            )
            if e.compressor_power_kw > 0:
                metric_card(
                    ec2,
                    "Potencia compresor",
                    f"{e.compressor_power_kw:.2f} kW",
                    *TIPS["compresor"],
                )
            else:
                metric_card(ec2, "Compresor", "N/A", *TIPS["compresor"])
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            ec3, ec4 = st.columns(2)
            metric_card(
                ec3,
                "Potencia total",
                f"{e.total_power_kw:.2f} kW",
                *TIPS["potencia_total"],
            )
            metric_card(
                ec4,
                "Intensidad",
                f"{e.kwh_per_m3_snow:.2f} kWh/m³",
                *TIPS["intensidad_energetica"],
            )

# ── Charts tab ─────────────────────────────────────────────────
with charts_tab:
    if not v.can_make_snow:
        g_col, _ = st.columns([1, 1])
        with g_col:
            chart_label("Temperatura de bulbo húmedo", *TIPS["chart_gauge"])
            st.plotly_chart(wet_bulb_gauge(result.wet_bulb), use_container_width=True)
        st.markdown(
            '<p class="mono" style="color:#f85149; padding: 1rem 0;">'
            "⚠ Sin producción — los demás gráficos se activan cuando Tw ≤ −2 °C.</p>",
            unsafe_allow_html=True,
        )
    else:
        gauge_col, prod_col = st.columns(2, gap="large")
        with gauge_col:
            chart_label("Temperatura de bulbo húmedo", *TIPS["chart_gauge"])
            st.plotly_chart(wet_bulb_gauge(result.wet_bulb), use_container_width=True)
        with prod_col:
            chart_label("Producción horaria", *TIPS["chart_prod"])
            st.plotly_chart(production_bar(p), use_container_width=True)

        qual_col, ener_col = st.columns(2, gap="large")
        with qual_col:
            chart_label("Calidad de nieve", *TIPS["chart_radar"])
            st.plotly_chart(quality_bars(q), use_container_width=True)
        with ener_col:
            chart_label("Distribución de consumo", *TIPS["chart_pie"])
            st.plotly_chart(energy_pie(e), use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p class="mono" style="font-size:0.7rem">'
    "Modelo de bulbo húmedo: Stull (2011) · "
    "Densidad de nieve artificial: 350 kg/m³ · "
    "Rendimiento de bomba η=0.75 · "
    "Valores estimados — no usar para operaciones críticas</p>",
    unsafe_allow_html=True,
)

render_footer()
