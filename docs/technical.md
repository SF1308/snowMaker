# Technical: stack, estructura y cómo correr el proyecto

> Esta página no asume ningún conocimiento sobre nivocultura. Si te interesa el dominio (qué es fabricar nieve, cómo funciona) o el detalle de las fórmulas, ver **Snowmaking** y **Architecture**.

## Stack

- **Python 3.10+** (usa sintaxis `float | None`, disponible desde 3.10)
- **Streamlit** — framework de UI
- **Plotly** — gráficos (gauge de bulbo húmedo, visualizaciones de producción/calidad/energía)
- **dataclasses** (stdlib) — modelado de datos
- **math** (stdlib) — funciones trigonométricas de la fórmula de Stull

> 🔧 **Pendiente:** existe un módulo `i18n/` (toggle ES/EN) armado pero todavía no integrado en `app.py`, `ui/weather.py` ni `ui/snowgun.py`. Ver "Known issues" más abajo.

La lógica de dominio (`calculators/`, `engine/`, `models/`) no depende de Streamlit ni de ninguna librería externa — solo `app.py` y `ui/` lo hacen. Esto es intencional: permite testear o reusar el motor de cálculo sin necesidad de levantar una UI.

## Instalación y ejecución

```bash
git clone https://github.com/SF1308/snowMaker
cd snowMaker
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Correr la app Streamlit

```bash
python -m streamlit run app.py
```

Usar `python -m streamlit` en vez de solo `streamlit` evita problemas comunes en Windows cuando el ejecutable de Streamlit no está bien resuelto en el `PATH` — corre el módulo directamente con el intérprete de Python activo, así que siempre usa el mismo entorno virtual que tenés activado.

Abre en `http://localhost:8501` por defecto.

### Correr el motor por CLI (sin UI)

```bash
python main.py
```

Calcula el bulbo húmedo para condiciones fijas (hoy hardcodeadas en `main.py`) y lo imprime por consola. Útil para debug rápido de la fórmula sin levantar Streamlit.

> ⚠️ Actualmente `main.py` tiene un import roto (ver sección "Known issues" más abajo).

### Codespaces / Devcontainer

El proyecto incluye `.devcontainer/devcontainer.json` basado en `python:3.11-bookworm`. Al abrir en GitHub Codespaces instala automáticamente dependencias y levanta la app en el puerto `8501` con preview automático.

## Estructura del proyecto

```
snow-maker-simulator/
│
├── models/                     # Datos puros, sin lógica de negocio
│   ├── weather.py              # Weather: temperature, humidity, wind_speed
│   ├── snowgun.py              # SnowGun: spec + presiones, valida rangos
│   ├── gun_spec.py             # GunSpec: config técnica de un tipo de cañón
│   ├── gun_type.py             # GunType: enum mono_fluid | bi_fluid
│   ├── primitives.py           # Range: min/max genérico reusable
│   ├── snowgun_config.py       # GUN_CONFIGS: lookup GunType → GunSpec
│   └── output/
│       └── simulation_result.py  # SimulationResult: resultado agregado final
│
├── calculators/                 # Un calculator = una pregunta, sin dependencias entre sí
│   ├── wet_bulb_calculator.py   # ¿Cuál es el bulbo húmedo?
│   ├── viability.py             # ¿Se puede operar?
│   ├── production.py            # ¿Cuánta nieve por hora?
│   ├── quality.py               # ¿Qué calidad de nieve?
│   ├── energy.py                # ¿Cuánta energía consume?
│   └── efficiency.py            # (vacío — pendiente)
│
├── engine/
│   ├── snowEngine.py            # SnowEngine.simulate() — orquesta los calculators
│   └── __init__.py              # re-exporta SnowEngine
│
├── presets/                     # Configs específicas de fabricante (vacío — pendiente)
│   ├── fan_basic.py
│   ├── lance_basic.py
│   └── technoalpin_tf10.py
│
├── ui/                           # Streamlit — inputs que devuelven modelos de dominio
│   ├── weather.py                # render_weather() → Weather
│   ├── snowgun.py                # render_snowgun() → SnowGun
│   ├── charts.py                 # Visualizaciones con Plotly
│   └── footer.py                 # Footer con links a redes
│
├── i18n/                         # Scaffold de traducciones — NO integrado todavía (ver Known issues)
│   ├── strings.py                # Diccionario de traducciones
│   └── translator.py             # Helper t() + selector de idioma
│
├── docs/                         # Esta documentación
├── pages/                        # Páginas Streamlit multipage (Snowmaking/Architecture/Technical)
├── tests/                        # (vacío — pendiente)
├── app.py                        # Entry point de la UI
└── main.py                       # Entry point CLI mínimo
```

## Principio de diseño: responsabilidad única por capa

```
INPUTS (models)  →  CALCULATORS  →  ENGINE  →  RESULT  →  UI (Streamlit)
```

Cada `calculator` responde **una sola pregunta** y no conoce a los demás. `WetBulbCalculator` no sabe que existe `ViabilityCalculator` — devuelve un `float` y listo. Es `SnowEngine` el único que conoce el orden de dependencias y encadena las salidas de uno como entrada del siguiente:

```python
wet_bulb   = wet_bulb_calculator.calculate(weather)
viability  = viability_calculator.calculate(wet_bulb)
production = production_calculator.calculate(snowgun)
quality    = quality_calculator.calculate(wet_bulb)
energy     = energy_calculator.calculate(snowgun, production.water_flow_lpm, production.snow_volume_m3h)
```

Ventaja práctica: cada calculator se testea aislado, sin mockear Streamlit ni otros calculators. Y la fórmula de Stull podría reemplazarse por una tabla psicrométrica real sin tocar `viability.py`, `quality.py` ni la UI — todos consumen `wet_bulb: float`, no la fórmula en sí.

Del lado de la UI, cada `render_*` de `ui/` devuelve directamente un modelo de dominio (`Weather`, `SnowGun`), no un dict de valores sueltos — `app.py` no conoce sliders ni defaults, solo orquesta. Esto significa que Streamlit se podría reemplazar por otra interfaz (CLI, API REST) reusando el 100% de `models/`, `calculators/` y `engine/`.

> Hoy `viability.py` y `quality.py` todavía generan `label`/`description` como texto en español hardcodeado dentro del propio calculator. Cuando se integre `i18n/`, ese texto debería moverse a la capa de presentación (ver Known issues) para que los calculators devuelvan solo códigos (`zone`, `grade`) y queden agnósticos del idioma.

## Por qué dataclasses

Todos los modelos son `@dataclass`:

- **Menos boilerplate:** no hace falta escribir `__init__` a mano para clases que son, en esencia, contenedores de datos.
- **`__eq__` y `__repr__` gratis:** útil para tests y debugging.
- **Inmutabilidad opcional:** `@dataclass(frozen=True)` en `GunSpec`, `Range` y todos los `*Result` de los calculators — una vez creados, no se pueden mutar por accidente en medio de una simulación.
- **Validación explícita cuando hace falta:** `SnowGun` es el único modelo no-frozen, porque necesita `__post_init__` para validar que las presiones ingresadas estén dentro del rango permitido por su `GunSpec`. Es lógica de validación, no de cálculo — por eso vive en el modelo y no en un calculator.

## Patrón de configuración: lookup table

`models/snowgun_config.py` mapea `GunType → GunSpec` con un diccionario simple (equivalente a `Record<GunType, GunSpec>` en TypeScript):

```python
GUN_CONFIGS: dict[GunType, GunSpec] = {
    GunType.MONO_FLUID: GunSpec(...),
    GunType.BI_FLUID: GunSpec(...),
}
```

Hoy la clave es el tipo genérico de cañón. El diseño anticipa que en el futuro la clave pase a ser un modelo específico de fabricante (ej. `"TechnoAlpin TF10"`) sin tener que tocar `GunSpec` — solo cambia el diccionario. Los archivos vacíos en `presets/` son placeholders para ese camino.

## Imports

El proyecto usa imports absolutos desde la raíz (`from models.weather import Weather`), excepto `engine/__init__.py` y `models/__init__.py`, que re-exportan con imports relativos. Por eso siempre hay que correr los comandos **desde la raíz del proyecto**.

`models/__init__.py` centraliza los exports públicos:

```python
from models import Weather, SnowGun, GUN_CONFIGS
```

## Constantes empíricas por módulo

Referencia rápida de dónde sale cada número mágico usado en los cálculos:

| Constante | Valor | Ubicación |
|---|---|---|
| Coeficientes de Stull | `0.151977`, `8.313659`, `1.676331`, `0.00391838`, `0.023101`, `4.686035` | `wet_bulb_calculator.py` |
| `THRESHOLD_IMPOSSIBLE` | −2.0 °C | `viability.py` |
| `THRESHOLD_MARGINAL` | −5.0 °C | `viability.py` |
| `SNOW_DENSITY_KGM3` | 350.0 kg/m³ | `production.py` |
| `WATER_TO_SNOW_VOLUME` | 3.0 | `production.py` |
| `NOZZLE_K` | 2.8 | `production.py` |
| `ETA_PUMP` | 0.75 | `energy.py` |
| `ETA_COMP` | 0.70 | `energy.py` |
| `AIR_FLOW_PER_BAR` | 0.06 m³/s | `energy.py` |
| Rango tamaño de grano | 0.2–0.8 mm | `quality.py` |
| Rango densidad de nieve | 280–450 kg/m³ | `quality.py` |

Si estos valores cambian, modificar solo en el calculator correspondiente — no hay duplicación en otras capas.

## Testing

`tests/` existe pero está vacío. Dado el diseño desacoplado, el patrón recomendado es testear cada calculator de forma aislada:

```python
def test_wet_bulb_matches_known_value():
    weather = Weather(temperature=-5, humidity=50)
    result = WetBulbCalculator().calculate(weather)
    assert result == pytest.approx(-9.9, abs=0.5)
```

Ningún calculator necesita Streamlit, un `SnowGun` completo, ni el `SnowEngine` para testearse — solo su propio input mínimo.

## Known issues / deuda técnica

- `main.py` importa `from engine.snowmaking_engine import SnowmakingEngine`, pero el archivo real es `engine/snowEngine.py` con la clase `SnowEngine`. El import está roto.
- `calculators/efficiency.py` está vacío — pendiente de implementación.
- `presets/fan_basic.py`, `presets/lance_basic.py` y `presets/technoalpin_tf10.py` están vacíos — placeholders intencionales para configuraciones de fabricante específico.
- La fórmula de Stull no corrige por presión atmosférica/altitud.
- `i18n/` (toggle ES/EN) está armado (`strings.py`, `translator.py`) pero todavía no integrado — `app.py`, `ui/weather.py` y `ui/snowgun.py` siguen usando strings hardcodeados, y `viability.py`/`quality.py` siguen devolviendo `label`/`description` en español en vez de códigos agnósticos de idioma.

## Deploy

- Entry point: `app.py` (no `main.py`, que es solo CLI).
- `requirements.txt` debe incluir al menos `streamlit` y `plotly`.
- Las páginas en `pages/` son detectadas automáticamente por Streamlit sin configuración adicional.
