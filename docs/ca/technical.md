# Technical: stack, estructura i com executar el projecte

> Aquesta pàgina no assumeix cap coneixement sobre nivocultiu. Si t’interessa el domini (què és fabricar neu, com funciona) o el detall de les fórmules, mira **Snowmaking** i **Architecture**.

## Stack

- **Python 3.10+** (usa sintaxi `float | None`, disponible des de 3.10)
- **Streamlit** — framework d’interfície d’usuari
- **Plotly** — gràfics (gauge de bulb humit, visualitzacions de producció/qualitat/energia)
- **dataclasses** (stdlib) — modelatge de dades
- **math** (stdlib) — funcions trigonomètriques per a la fórmula de Stull

> 🔧 **Pendent:** existeix un mòdul `i18n/` (toggle ES/EN) ja creat però encara no integrat a `app.py`, `ui/weather.py` ni `ui/snowgun.py`. Mira "Known issues" més avall.

La lògica de domini (`calculators/`, `engine/`, `models/`) no depèn de Streamlit ni de cap biblioteca externa — només `app.py` i `ui/` ho fan. Això és intencional: permet provar o reutilitzar el motor de càlcul sense necessitat d’aixecar una UI.

## Installation and execution

```bash
git clone https://github.com/SF1308/snowMaker
cd snowMaker
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Streamlit app

```bash
python -m streamlit run app.py
```

Using `python -m streamlit` instead of just `streamlit` avoids common Windows issues when the Streamlit executable is not resolved correctly in `PATH` — it runs the module directly with the active Python interpreter, so it always uses the same virtual environment.

It opens at `http://localhost:8501` by default.

### Run the engine from CLI (no UI)

```bash
python main.py
```

It calculates the wet bulb for fixed conditions (currently hardcoded in `main.py`) and prints it to the console. Useful for quick debugging of the formula without launching Streamlit.

> ⚠️ Currently `main.py` has a broken import (see the "Known issues" section below).

### Codespaces / Devcontainer

The project includes `.devcontainer/devcontainer.json` based on `python:3.11-bookworm`. Opening it in GitHub Codespaces installs dependencies automatically and starts the app on port `8501` with auto preview.

## Project structure

```
snow-maker-simulator/
│
├── models/                     # Pure data models, no business logic
│   ├── weather.py              # Weather: temperature, humidity, wind_speed
│   ├── snowgun.py              # SnowGun: spec + pressures, validates ranges
│   ├── gun_spec.py             # GunSpec: technical config for a gun type
│   ├── gun_type.py             # GunType: enum mono_fluid | bi_fluid
│   ├── primitives.py           # Range: reusable min/max wrapper
│   ├── snowgun_config.py       # GUN_CONFIGS: lookup GunType → GunSpec
│   └── output/
│       └── simulation_result.py  # SimulationResult: aggregated final result
│
├── calculators/                 # One calculator = one question, no cross-dependencies
│   ├── wet_bulb_calculator.py   # What is the wet bulb?
│   ├── viability.py             # Can it operate?
│   ├── production.py            # How much snow per hour?
│   ├── quality.py               # What snow quality?
│   ├── energy.py                # How much energy does it consume?
│   └── efficiency.py            # (empty — pending)
│
├── engine/
│   ├── snowEngine.py            # SnowEngine.simulate() — orchestrates the calculators
│   └── __init__.py              # re-exports SnowEngine
│
├── presets/                     # Manufacturer-specific configs (empty — pending)
│   ├── fan_basic.py
│   ├── lance_basic.py
│   └── technoalpin_tf10.py
│
├── ui/                          # Streamlit — inputs that return domain models
│   ├── weather.py                # render_weather() → Weather
│   ├── snowgun.py                # render_snowgun() → SnowGun
│   ├── charts.py                 # Plotly visualizations
│   └── footer.py                 # Footer with social links
│
├── i18n/                        # Translation scaffold — NOT integrated yet (see Known issues)
│   ├── strings.py                # Translation dictionary
│   └── translator.py             # Helper t() + language selector
│
├── docs/                        # This documentation
├── pages/                       # Streamlit multipage pages (Snowmaking/Architecture/Technical)
├── tests/                       # (empty — pending)
├── app.py                       # UI entry point
└── main.py                      # Minimal CLI entry point
```

## Design principle: single responsibility per layer

```
INPUTS (models)  →  CALCULATORS  →  ENGINE  →  RESULT  →  UI (Streamlit)
```

Each `calculator` answers **one question** and does not know about the others. `WetBulbCalculator` does not know `ViabilityCalculator` exists — it returns a `float` and that’s it. `SnowEngine` is the only component that knows the dependency order and chains outputs from one step into inputs for the next:

```python
wet_bulb   = wet_bulb_calculator.calculate(weather)
viability  = viability_calculator.calculate(wet_bulb)
production = production_calculator.calculate(snowgun)
quality    = quality_calculator.calculate(wet_bulb)
energy     = energy_calculator.calculate(snowgun, production.water_flow_lpm, production.snow_volume_m3h)
```

Practical benefit: each calculator can be tested in isolation, without mocking Streamlit or other calculators. And the Stull formula could be replaced by a real psychrometric table without touching `viability.py`, `quality.py`, or the UI — they all consume `wet_bulb: float`, not the formula itself.

On the UI side, each `render_*` in `ui/` returns a domain model (`Weather`, `SnowGun`), not a loose dict of values — `app.py` does not know sliders or defaults, it only orchestrates. This means Streamlit could be replaced by another interface (CLI, REST API) while reusing 100% of `models/`, `calculators/`, and `engine/`.

> Today `viability.py` and `quality.py` still generate `label`/`description` as Spanish hardcoded text inside the calculator. When `i18n/` is integrated, that text should move to the presentation layer (see Known issues) so calculators return only codes (`zone`, `grade`) and become language-agnostic.

## Why dataclasses?

All models are `@dataclass`:

- **Less boilerplate:** no need to write `__init__` by hand for classes that are essentially data containers.
- **`__eq__` and `__repr__` for free:** useful for tests and debugging.
- **Optional immutability:** `@dataclass(frozen=True)` on `GunSpec`, `Range`, and all calculator `*Result` classes — once created, they cannot be mutated by accident during a simulation.
- **Explicit validation when needed:** `SnowGun` is the only non-frozen model because it needs `__post_init__` to validate that supplied pressures are within the allowed range for its `GunSpec`. This is validation logic, not calculation logic — that’s why it lives in the model and not in a calculator.

## Configuration pattern: lookup table

`models/snowgun_config.py` maps `GunType → GunSpec` with a simple dictionary (equivalent to `Record<GunType, GunSpec>` in TypeScript):

```python
GUN_CONFIGS: dict[GunType, GunSpec] = {
    GunType.MONO_FLUID: GunSpec(...),
    GunType.BI_FLUID: GunSpec(...),
}
```

Today the key is the generic gun type. The design anticipates that in the future the key may become a manufacturer-specific model (e.g. `"TechnoAlpin TF10"`) without touching `GunSpec` — only the dictionary changes. The empty files in `presets/` are placeholders for that path.

## Imports

The project uses absolute imports from the root (`from models.weather import Weather`), except `engine/__init__.py` and `models/__init__.py`, which re-export with relative imports. That’s why commands must always run from the project root.

`models/__init__.py` centralizes public exports:

```python
from models import Weather, SnowGun, GUN_CONFIGS
```

## Empirical constants by module

Quick reference for where each magic number used in the calculations comes from:

| Constant | Value | Location |
|---|---|---|
| Stull coefficients | `0.151977`, `8.313659`, `1.676331`, `0.00391838`, `0.023101`, `4.686035` | `wet_bulb_calculator.py` |
| `THRESHOLD_IMPOSSIBLE` | −2.0 °C | `viability.py` |
| `THRESHOLD_MARGINAL` | −5.0 °C | `viability.py` |
| `SNOW_DENSITY_KGM3` | 350.0 kg/m³ | `production.py` |
| `WATER_TO_SNOW_VOLUME` | 3.0 | `production.py` |
| `NOZZLE_K` | 2.8 | `production.py` |
| `ETA_PUMP` | 0.75 | `energy.py` |
| `ETA_COMP` | 0.70 | `energy.py` |
| `AIR_FLOW_PER_BAR` | 0.06 m³/s | `energy.py` |
| Grain size range | 0.2–0.8 mm | `quality.py` |
| Snow density range | 280–450 kg/m³ | `quality.py` |

If these values change, modify only the calculator responsible — there is no duplication in other layers.

## Testing

`tests/` exists but is empty. Given the decoupled design, the recommended pattern is to test each calculator in isolation:

```python
def test_wet_bulb_matches_known_value():
    weather = Weather(temperature=-5, humidity=50)
    result = WetBulbCalculator().calculate(weather)
    assert result == pytest.approx(-9.9, abs=0.5)
```

No calculator needs Streamlit, a full `SnowGun`, or `SnowEngine` to be tested — only its own minimal input.

## Known issues / technical debt

- `main.py` imports `from engine.snowmaking_engine import SnowmakingEngine`, but the real file is `engine/snowEngine.py` with class `SnowEngine`. The import is broken.
- `calculators/efficiency.py` is empty — pending implementation.
- `presets/fan_basic.py`, `presets/lance_basic.py`, and `presets/technoalpin_tf10.py` are empty — intentional placeholders for manufacturer-specific configs.
- The Stull formula does not correct for atmospheric pressure/altitude.
- `i18n/` (ES/EN toggle) is scaffolded (`strings.py`, `translator.py`) but not integrated yet — `app.py`, `ui/weather.py`, and `ui/snowgun.py` still use hardcoded strings, and `viability.py`/`quality.py` still return `label`/`description` in Spanish instead of language-agnostic codes.

## Deploy

- Entry point: `app.py` (not `main.py`, which is only CLI).
- `requirements.txt` should include at least `streamlit` and `plotly`.
- The pages in `pages/` are automatically detected by Streamlit without additional configuration.
