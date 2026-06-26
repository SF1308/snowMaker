"""
ui/charts.py
Plotly figure factories for the Snow Maker Simulator.

Each function receives the relevant result dataclass and returns a go.Figure
ready to be passed to st.plotly_chart().
"""

import plotly.graph_objects as go

from calculators.production import ProductionResult
from calculators.quality import QualityResult
from calculators.energy import EnergyResult

# ── Shared theme ───────────────────────────────────────────────
_BG = "#0d1117"
_PAPER = "#0d1117"
_GRID = "#21262d"
_TEXT = "#8b949e"
_FONT = "Share Tech Mono, monospace"

_BASE = dict(
    paper_bgcolor=_PAPER,
    plot_bgcolor=_BG,
    font=dict(family=_FONT, color=_TEXT, size=11),
    margin=dict(t=40, b=20, l=20, r=20),
)


def wet_bulb_gauge(wet_bulb: float) -> go.Figure:
    """Gauge showing wet-bulb temperature against the three operational zones."""
    color = (
        "#3fb950" if wet_bulb <= -5 else ("#d29922" if wet_bulb <= -2 else "#f85149")
    )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=wet_bulb,
            number={
                "suffix": " °C",
                "font": {"size": 28, "color": "#e6edf3", "family": _FONT},
            },
            title={"text": "BULBO HÚMEDO (Tw)", "font": {"size": 11, "color": _TEXT}},
            gauge={
                "axis": {
                    "range": [-20, 5],
                    "tickvals": [-20, -15, -10, -5, -2, 0, 5],
                    "ticktext": ["-20", "-15", "-10", "-5", "-2", "0", "+5"],
                    "tickfont": {"size": 10, "color": _TEXT},
                },
                "bar": {"color": color, "thickness": 0.25},
                "bgcolor": "#161b22",
                "bordercolor": "#30363d",
                "steps": [
                    {"range": [-20, -5], "color": "#0d2414"},
                    {"range": [-5, -2], "color": "#2d1a00"},
                    {"range": [-2, 5], "color": "#2d0d0d"},
                ],
                "threshold": {
                    "line": {"color": "#58a6ff", "width": 2},
                    "thickness": 0.75,
                    "value": wet_bulb,
                },
            },
        )
    )
    fig.update_layout(**_BASE, height=260)
    return fig


def production_bar(p: ProductionResult) -> go.Figure:
    """Bar chart comparing water flow, snow volume and snow mass."""
    labels = [
        "Caudal agua<br>(L/min)",
        "Volumen nieve<br>(m³/h)",
        "Masa nieve<br>(kg/h)",
    ]
    values = [p.water_flow_lpm, p.snow_volume_m3h, p.snow_mass_kgh]
    colors = ["#58a6ff", "#79c0ff", "#cae8ff"]

    fig = go.Figure()
    for label, value, color in zip(labels, values, colors):
        fig.add_trace(
            go.Bar(
                x=[label],
                y=[value],
                name=label.replace("<br>", " "),
                marker_color=color,
                text=[f"{value:.1f}"],
                textposition="outside",
                textfont={"family": _FONT, "size": 12, "color": "#e6edf3"},
            )
        )

    fig.update_layout(
        **_BASE,
        title={"text": "PRODUCCIÓN", "font": {"size": 11, "color": _TEXT}, "x": 0},
        showlegend=False,
        height=300,
        yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID, showticklabels=False),
        xaxis=dict(gridcolor=_GRID),
        bargap=0.4,
    )
    return fig


def quality_radar(q: QualityResult) -> go.Figure:
    """Radar chart normalising crystal size (inverted), density and grade to 0–100."""
    grain_norm = max(0, (0.8 - q.grain_size_mm) / (0.8 - 0.2) * 100)
    density_norm = (q.density_kgm3 - 280) / (450 - 280) * 100
    grade_norm = {"A": 100, "B": 60, "C": 30, "—": 0}.get(q.grade, 0)

    cats = ["Tamaño cristal<br>(inv.)", "Densidad", "Calificación"]
    vals = [grain_norm, density_norm, grade_norm]

    fig = go.Figure(
        go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(88,166,255,0.15)",
            line=dict(color="#58a6ff", width=2),
            marker=dict(color="#58a6ff", size=6),
        )
    )
    fig.update_layout(
        **_BASE,
        title={
            "text": "CALIDAD DE NIEVE",
            "font": {"size": 11, "color": _TEXT},
            "x": 0,
        },
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(
                range=[0, 100],
                gridcolor=_GRID,
                tickfont={"size": 9, "color": _TEXT},
                showticklabels=True,
                tickvals=[25, 50, 75, 100],
            ),
            angularaxis=dict(
                gridcolor=_GRID, tickfont={"size": 10, "color": "#e6edf3"}
            ),
        ),
        height=300,
    )
    return fig


def energy_pie(e: EnergyResult) -> go.Figure:
    """Donut chart breaking down pump vs compressor power consumption."""
    if e.compressor_power_kw > 0:
        labels = ["Bomba", "Compresor"]
        values = [e.pump_power_kw, e.compressor_power_kw]
        colors = ["#58a6ff", "#3fb950"]
    else:
        labels, values, colors = ["Bomba"], [e.pump_power_kw], ["#58a6ff"]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#0d1117", width=2)),
            textfont=dict(family=_FONT, size=11, color="#e6edf3"),
            hovertemplate="%{label}: %{value:.2f} kW<extra></extra>",
        )
    )
    fig.update_layout(
        **_BASE,
        title={
            "text": "CONSUMO ENERGÉTICO",
            "font": {"size": 11, "color": _TEXT},
            "x": 0,
        },
        annotations=[
            dict(
                text=f"{e.total_power_kw:.1f}<br>kW",
                x=0.5,
                y=0.5,
                font=dict(size=16, color="#e6edf3", family=_FONT),
                showarrow=False,
            )
        ],
        legend=dict(font=dict(color="#e6edf3", family=_FONT), bgcolor="rgba(0,0,0,0)"),
        height=300,
    )
    return fig
