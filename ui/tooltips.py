import streamlit as st

# ── Icon SVG ───────────────────────────────────────────────────
_ICON = (
    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="12" cy="12" r="10"/>'
    '<line x1="12" y1="8" x2="12" y2="8" stroke-linecap="round" stroke-width="2.5"/>'
    '<line x1="12" y1="12" x2="12" y2="16" stroke-linecap="round" stroke-width="2"/>'
    "</svg>"
)


# ── Rendering helpers ──────────────────────────────────────────


def tip(label: str, title: str, body: str) -> str:
    """Return an HTML snippet: label text + hoverable ⓘ icon with bubble."""
    bubble = f'<div class="info-bubble"><strong>{title}</strong>{body}</div>'
    icon = f'<span class="info-icon">{_ICON}{bubble}</span>'
    return f'<div class="info-wrap">{label}&nbsp;{icon}</div>'


def metric_card(col, label: str, value: str, tip_title: str, tip_body: str) -> None:
    """Render a dark metric card with a tooltip-labelled heading into *col*."""
    html = f"""
    <div class="metric-card">
      {tip(label, tip_title, tip_body)}
      <p class="metric-value">{value}</p>
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)


def section_header(label: str, tip_title: str, tip_body: str) -> None:
    """Render a full-width section divider with an inline tooltip."""
    bubble = f'<div class="info-bubble"><strong>{tip_title}</strong>{tip_body}</div>'
    icon_html = (
        f'<span class="info-icon" style="vertical-align:middle">{_ICON}{bubble}</span>'
    )
    st.markdown(
        f'<div class="section-header" style="display:flex;align-items:center;gap:6px">'
        f"{label}&nbsp;{icon_html}</div>",
        unsafe_allow_html=True,
    )


def chart_label(label: str, tip_title: str, tip_body: str) -> None:
    """Render a small uppercase label above a chart with a tooltip."""
    st.markdown(tip(label, tip_title, tip_body), unsafe_allow_html=True)


# ── Tooltip content ────────────────────────────────────────────
# Each entry: key → (title, body)
# Body is plain text; newlines render as-is inside the bubble.
# This dict is the single place to swap in a translated copy later.

TIPS: dict[str, tuple[str, str]] = {
    # ── Inputs ────────────────────────────────────────────────
    "temperature": (
        "Air Temperature (T)",
        "Dry-bulb temperature measured in the environment. "
        "This is what a regular thermometer reads. "
        "Typical operating range: −20 °C to +10 °C.",
    ),
    "humidity": (
        "Relative Humidity (RH)",
        "Percentage of water vapor in the air relative to the maximum possible at that temperature. "
        "Higher humidity means less evaporation of the atomized water → higher wet bulb → worse snowmaking conditions.",
    ),
    "wind": (
        "Wind Speed",
        "Affects the dispersion of snow particles and cooling efficiency. "
        "Strong winds can reduce gun coverage.",
    ),
    # ── Result ────────────────────────────────────────────────
    "simulation": (
        "Simulation",
        "Result calculated in real time by the simulation engine "
        "from the atmospheric conditions and gun configuration.",
    ),
    "wet_bulb": (
        "Wet-Bulb Temperature (Tw)",
        "Key meteorological variable in snowmaking. "
        "Calculated with the Stull (2011) formula from temperature and humidity. "
        "Always ≤ dry-bulb temperature. Thresholds: "
        "Tw > −2 °C → not viable · "
        "−5 °C < Tw ≤ −2 °C → marginal · "
        "Tw ≤ −5 °C → optimal.",
    ),
    "viability": (
        "Production Viability",
        "Determines whether conditions allow artificial snow production. "
        "Based exclusively on wet-bulb temperature (Tw), not dry-bulb temperature. "
        "A cold but very humid day can be non-viable.",
    ),
    # ── Production ────────────────────────────────────────────
    "production": (
        "Snow Production",
        "Estimates of how much water is consumed and how much snow is generated, "
        "based on water pressure and the gun's nozzle type.",
    ),
    "flow": (
        "Water Flow (Q)",
        "Liters of water per minute flowing through the nozzles. "
        "Model: Q = K × nozzles × √P, where K = 2.8, "
        "nozzles is the nozzle count and P the pressure in bar.",
    ),
    "snow_volume": (
        "Snow Volume Produced",
        "Cubic meters of artificial snow generated per hour. "
        "Conversion: 1 L water → ~3 L of snow (expansion factor). "
        "Assumed density: 350 kg/m³.",
    ),
    "snow_mass": (
        "Snow Mass Produced",
        "Kilograms of artificial snow per hour. "
        "Calculated as: volume (m³/h) × density (350 kg/m³). "
        "Useful for estimating slope coverage.",
    ),
    # ── Quality ───────────────────────────────────────────────
    "quality": (
        "Snow Quality",
        "Quality estimate based on wet-bulb temperature. "
        "Empirical models based on Fierz et al. (2009).",
    ),
    "quality_grade": (
        "Quality Grade (A / B / C)",
        "Overall rating: "
        "A → Tw ≤ −5 °C, dry snow with fine crystals. "
        "B → −5 °C < Tw ≤ −2 °C, wet snow. "
        "C → marginal condition.",
    ),
    "crystal": (
        "Snow Crystal Size",
        "Estimated grain diameter in mm. "
        "Model: grain = 0.8 − 0.06 × |Tw| (clamped 0.2–0.8 mm). "
        "Smaller crystals → harder, more compactable snow.",
    ),
    "density": (
        "Snow Density",
        "Mass per unit volume in kg/m³. "
        "Model: density = 280 + 12 × |Tw| (clamped 280–450 kg/m³). "
        "Higher density = firmer snow, ideal for alpine ski slopes.",
    ),
    # ── Energy ────────────────────────────────────────────────
    "energy": (
        "Energy Consumption",
        "Estimated electrical power draw of the system. "
        "Model based on the hydraulic power equation "
        "with typical pump (η = 0.75) and compressor (η = 0.70) efficiencies.",
    ),
    "pump": (
        "Pump Power",
        "Estimated electrical draw of the water pump. "
        "Model: P = (Q × ΔP) / η, with Q in m³/s, ΔP in Pa, η = 0.75. "
        "Depends directly on the configured water pressure.",
    ),
    "compressor": (
        "Compressor Power",
        "Only applies to bi-fluid (lance) guns. "
        "Model: P = (Q_air × P_air) / η, with η = 0.70 "
        "and estimated flow = 0.06 m³/s per bar.",
    ),
    "total_power": (
        "Total System Power",
        "Sum of pump + compressor (if applicable). "
        "Represents the actual electrical draw of the gun in operation.",
    ),
    "energy_intensity": (
        "Energy Intensity",
        "Kilowatt-hours consumed per cubic meter of snow produced (kWh/m³). "
        "Measures the energy efficiency of the operation. "
        "Typical values: 2–6 kWh/m³ for modern guns.",
    ),
    # ── Charts ────────────────────────────────────────────────
    "chart_gauge": (
        "Wet-Bulb Gauge",
        "Visualizes wet-bulb temperature across the three operating ranges. "
        "Green: optimal (≤ −5 °C) · Yellow: marginal · Red: not viable (> −2 °C).",
    ),
    "chart_prod": (
        "Production Bars",
        "Compares the three production metrics in their natural units: "
        "flow (L/min), volume (m³/h) and mass (kg/h). Scales are independent.",
    ),
    "chart_radar": (
        "Quality Radar",
        "Normalizes two attributes to their real scales for visual comparison. "
        "Crystal size is inverted: smaller crystals are better. "
        "Bars closer to the green end indicate better snow quality.",
    ),
    "chart_pie": (
        "Consumption Breakdown",
        "Breaks down total power between pump and compressor (if any). "
        "The center number is the total power in kW.",
    ),
}
