"""
ui/tooltips.py
Tooltip rendering helpers and all tooltip content for the simulator.

Public API
----------
TIPS        — dict[str, tuple[str, str]]  key → (title, body)
tip()       — returns an HTML string: label + hover icon
metric_card()    — renders a styled card with tooltip into a Streamlit column
section_header() — renders a section divider with tooltip via st.markdown
chart_label()    — renders a small label above a chart with tooltip
"""

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

TIPS: dict[str, tuple[str, str]] = {
    # ── Inputs ────────────────────────────────────────────────
    "temperatura": (
        "Temperatura del aire (T)",
        "Temperatura de bulbo seco medida en el ambiente. "
        "Es la que marca un termómetro convencional. "
        "Rango operativo típico: −20 °C a +10 °C.",
    ),
    "humedad": (
        "Humedad relativa (HR)",
        "Porcentaje de vapor de agua en el aire respecto al máximo posible a esa temperatura. "
        "A mayor humedad, menos evaporación del agua atomizada → bulbo húmedo más alto → peor condición para nevar.",
    ),
    "viento": (
        "Velocidad del viento",
        "Afecta la dispersión de las partículas de nieve y la eficiencia de enfriamiento. "
        "Vientos fuertes pueden reducir la cobertura del cañón.",
    ),
    # ── Resultado ─────────────────────────────────────────────
    "simulacion": (
        "Simulación",
        "Resultado calculado en tiempo real por el motor de simulación "
        "a partir de las condiciones atmosféricas y la configuración del cañón.",
    ),
    "wet_bulb": (
        "Temperatura de bulbo húmedo (Tw)",
        "Variable meteorológica clave en la fabricación de nieve. "
        "Calculada con la fórmula de Stull (2011) a partir de temperatura y humedad. "
        "Siempre es ≤ temperatura seca. Umbrales: "
        "Tw > −2 °C → no viable · "
        "−5 °C < Tw ≤ −2 °C → marginal · "
        "Tw ≤ −5 °C → óptimo.",
    ),
    "viabilidad": (
        "Viabilidad de producción",
        "Determina si las condiciones permiten producir nieve artificial. "
        "Se basa exclusivamente en el bulbo húmedo (Tw), no en la temperatura seca. "
        "Un día frío pero muy húmedo puede ser inviable.",
    ),
    # ── Producción ────────────────────────────────────────────
    "produccion": (
        "Producción de nieve",
        "Estimaciones de cuánta agua se consume y cuánta nieve se genera, "
        "basadas en la presión de agua y el tipo de boquillas del cañón.",
    ),
    "caudal": (
        "Caudal de agua (Q)",
        "Litros de agua por minuto que fluyen por las boquillas. "
        "Modelo: Q = K × nozzles × √P, donde K = 2.8, "
        "nozzles es el número de boquillas y P la presión en bar.",
    ),
    "volumen_nieve": (
        "Volumen de nieve producido",
        "Metros cúbicos de nieve artificial generados por hora. "
        "Conversión: 1 L agua → ~3 L de nieve (factor de expansión). "
        "Densidad asumida: 350 kg/m³.",
    ),
    "masa_nieve": (
        "Masa de nieve producida",
        "Kilogramos de nieve artificial por hora. "
        "Calculado como: volumen (m³/h) × densidad (350 kg/m³). "
        "Útil para estimar cobertura de pistas.",
    ),
    # ── Calidad ───────────────────────────────────────────────
    "calidad": (
        "Calidad de nieve",
        "Estimación de la calidad según la temperatura de bulbo húmedo. "
        "Modelos empíricos basados en Fierz et al. (2009).",
    ),
    "grado_calidad": (
        "Calificación de calidad (A / B / C)",
        "Evaluación global: "
        "A → Tw ≤ −5 °C, nieve seca y cristales finos. "
        "B → −5 °C < Tw ≤ −2 °C, nieve húmeda. "
        "C → condición marginal.",
    ),
    "cristal": (
        "Tamaño de cristal de nieve",
        "Diámetro estimado de los granos en mm. "
        "Modelo: grain = 0.8 − 0.06 × |Tw| (acotado 0.2–0.8 mm). "
        "Cristales más pequeños → nieve más dura y compactable.",
    ),
    "densidad": (
        "Densidad de la nieve",
        "Masa por unidad de volumen en kg/m³. "
        "Modelo: densidad = 280 + 12 × |Tw| (acotado 280–450 kg/m³). "
        "Mayor densidad = nieve más sólida, ideal para pistas de esquí alpino.",
    ),
    # ── Energía ───────────────────────────────────────────────
    "energia": (
        "Consumo energético",
        "Potencia eléctrica estimada del sistema. "
        "Modelo basado en la ecuación de potencia hidráulica "
        "con rendimientos típicos de bomba (η = 0.75) y compresor (η = 0.70).",
    ),
    "bomba": (
        "Potencia de la bomba",
        "Consumo eléctrico estimado de la bomba de agua. "
        "Modelo: P = (Q × ΔP) / η, con Q en m³/s, ΔP en Pa, η = 0.75. "
        "Depende directamente de la presión de agua configurada.",
    ),
    "compresor": (
        "Potencia del compresor",
        "Solo aplica a cañones bi-fluido (lanza). "
        "Modelo: P = (Q_aire × P_aire) / η, con η = 0.70 "
        "y caudal estimado = 0.06 m³/s por bar.",
    ),
    "potencia_total": (
        "Potencia total del sistema",
        "Suma de bomba + compresor (si aplica). "
        "Representa el consumo eléctrico real del cañón en operación.",
    ),
    "intensidad_energetica": (
        "Intensidad energética",
        "Kilowatios-hora consumidos por metro cúbico de nieve producido (kWh/m³). "
        "Mide la eficiencia energética de la operación. "
        "Valores típicos: 2–6 kWh/m³ para cañones modernos.",
    ),
    # ── Gráficos ──────────────────────────────────────────────
    "chart_gauge": (
        "Gauge de bulbo húmedo",
        "Visualiza la temperatura de bulbo húmedo sobre los tres rangos operativos. "
        "Verde: óptimo (≤ −5 °C) · Amarillo: marginal · Rojo: no viable (> −2 °C).",
    ),
    "chart_prod": (
        "Barras de producción",
        "Compara las tres métricas de producción en sus unidades naturales: "
        "caudal (L/min), volumen (m³/h) y masa (kg/h). Las escalas son independientes.",
    ),
    "chart_radar": (
        "Radar de calidad",
        "Normaliza tres atributos a escala 0–100 para comparación visual. "
        "Tamaño de cristal está invertido: más área = cristales más pequeños (mejor). "
        "Mayor área total indica mejor calidad de nieve.",
    ),
    "chart_pie": (
        "Distribución de consumo",
        "Desglosa la potencia total entre bomba y compresor (si hay). "
        "El número central es la potencia total en kW.",
    ),
}
