"""
ui/charts.py
Plotly figure factories for the Snow Maker Simulator.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


def quality_bars(q: QualityResult) -> go.Figure:
    """
    Two horizontal bullet bars on their real scales:
      - Tamaño de cristal: 0.2 mm (fino/mejor) → 0.8 mm (grueso/peor)  [invert=True]
      - Densidad:        280 kg/m³ (blanda/peor) → 450 kg/m³ (densa/mejor)
    Each metric has its own x-axis via make_subplots so scales don't interfere.
    """
    # (label, value, vmin, vmax, left_label, right_label, invert)
    # invert=True → lower value is better; bar fills from the right
    subplot_rows = [
        (
            "Tamaño de cristal",
            q.grain_size_mm,
            0.2,
            0.8,
            "0.2 mm  fino",
            "grueso  0.8 mm",
            True,
        ),
        (
            "Densidad",
            q.density_kgm3,
            280,
            450,
            "280 kg/m³  blanda",
            "densa  450 kg/m³",
            False,
        ),
    ]

    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.32)

    for row_idx, (label, value, vmin, vmax, lt, rt, invert) in enumerate(
        subplot_rows, start=1
    ):
        span = vmax - vmin
        pct = (value - vmin) / span
        good_pct = (1 - pct) if invert else pct
        bar_color = (
            "#3fb950"
            if good_pct > 0.66
            else ("#d29922" if good_pct > 0.33 else "#f85149")
        )
        xref = "x" if row_idx == 1 else "x2"
        yref = "y" if row_idx == 1 else "y2"

        # background track
        fig.add_trace(
            go.Bar(
                x=[span],
                base=vmin,
                orientation="h",
                marker=dict(color="#1c2230", line=dict(width=0)),
                showlegend=False,
                hoverinfo="skip",
            ),
            row=row_idx,
            col=1,
        )

        # filled bar
        if invert:
            fig.add_trace(
                go.Bar(
                    x=[vmax - value],
                    base=value,
                    orientation="h",
                    marker=dict(color=bar_color, line=dict(width=0)),
                    showlegend=False,
                    hovertemplate=f"<b>{label}</b>: {value:.2f}<extra></extra>",
                ),
                row=row_idx,
                col=1,
            )
        else:
            fig.add_trace(
                go.Bar(
                    x=[value - vmin],
                    base=vmin,
                    orientation="h",
                    marker=dict(color=bar_color, line=dict(width=0)),
                    showlegend=False,
                    hovertemplate=f"<b>{label}</b>: {value:.2f}<extra></extra>",
                ),
                row=row_idx,
                col=1,
            )

        # value marker line
        fig.add_shape(
            type="line",
            x0=value,
            x1=value,
            y0=-0.45,
            y1=0.45,
            line=dict(color="#e6edf3", width=2),
            xref=xref,
            yref=yref,
        )

        # value label above the marker
        fig.add_annotation(
            x=value,
            y=0.52,
            xref=xref,
            yref=yref,
            text=f"<b>{value:.2f}</b>",
            showarrow=False,
            font=dict(family=_FONT, size=12, color="#e6edf3"),
            xanchor="center",
        )

        # row label (top-left)
        fig.add_annotation(
            x=vmin,
            y=0.52,
            xref=xref,
            yref=yref,
            text=label.upper(),
            showarrow=False,
            font=dict(family=_FONT, size=9, color=_TEXT),
            xanchor="left",
        )

        # scale endpoint labels (below bar)
        fig.add_annotation(
            x=vmin,
            y=-0.58,
            xref=xref,
            yref=yref,
            text=lt,
            showarrow=False,
            font=dict(family="Barlow, sans-serif", size=9, color=_TEXT),
            xanchor="left",
        )
        fig.add_annotation(
            x=vmax,
            y=-0.58,
            xref=xref,
            yref=yref,
            text=rt,
            showarrow=False,
            font=dict(family="Barlow, sans-serif", size=9, color=_TEXT),
            xanchor="right",
        )

        # per-subplot axis config
        axis_key = "xaxis" if row_idx == 1 else "xaxis2"
        yaxis_key = "yaxis" if row_idx == 1 else "yaxis2"
        fig.update_layout(
            **{
                axis_key: dict(
                    range=[vmin, vmax],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                ),
                yaxis_key: dict(
                    range=[-0.7, 0.7],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                ),
            }
        )

    fig.update_layout(
        paper_bgcolor=_PAPER,
        plot_bgcolor=_BG,
        font=dict(family=_FONT, color=_TEXT, size=11),
        margin=dict(t=40, b=20, l=10, r=10),
        height=260,
        barmode="overlay",
        title={
            "text": "CALIDAD DE NIEVE",
            "font": {"size": 11, "color": _TEXT},
            "x": 0,
        },
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
