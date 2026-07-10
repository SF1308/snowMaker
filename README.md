# ❄️ Snow Maker Simulator

A physics-based simulator that models artificial snow production from real weather conditions and snow gun configuration, built with Streamlit.

> This README covers the technical side of the project (stack, structure, how to run it). For the domain explanation (what snowmaking is, why it's done) or the calculation details (formulas, thresholds), see the in-app documentation pages: **Snowmaking** and **Architecture**.

## Stack

- **Python 3.10+** (uses `float | None` syntax, available since 3.10)
- **Streamlit** — UI framework
- **Plotly** — charts (wet-bulb gauge, production/quality/energy visualizations)
- **dataclasses** (stdlib) — data modeling
- **math** (stdlib) — trigonometric functions for the Stull formula

> 🔧 **Planned:** an `i18n/` module (ES/EN toggle) is scaffolded but not yet wired into `app.py`, `ui/weather.py`, or `ui/snowgun.py`. See "Known Issues" below.

The domain logic (`calculators/`, `engine/`, `models/`) has no dependency on Streamlit or any third-party library — only `app.py` and `ui/` do. This is intentional: it allows testing or reusing the calculation engine without spinning up a UI.

## Getting Started

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

Using `python -m streamlit` instead of just `streamlit` avoids common issues on Windows when the Streamlit executable isn't properly resolved on `PATH` — it runs the module directly with the active Python interpreter, so it always uses the same virtual environment you have activated.

Opens at `http://localhost:8501` by default.

### Run the engine via CLI (no UI)

```bash
python main.py
```

Computes the wet-bulb temperature for fixed conditions (currently hardcoded in `main.py`) and prints it to the console. Useful for quick debugging of the formula without launching Streamlit.

### Codespaces / Devcontainer

The project includes `.devcontainer/devcontainer.json` based on `python:3.11-bookworm`. Opening it in GitHub Codespaces automatically installs dependencies and launches the app on port `8501` with an automatic preview.

## Project Structure

```
snowMaker/
│
├── models/                     # Pure data, no business logic
│   ├── weather.py              # Weather: temperature, humidity, wind_speed
│   ├── snowgun.py              # SnowGun: spec + pressures, validates ranges
│   ├── gun_spec.py             # GunSpec: technical config for a gun type
│   ├── gun_type.py             # GunType: enum mono_fluid | bi_fluid
│   ├── primitives.py           # Range: reusable generic min/max
│   ├── snowgun_config.py       # GUN_CONFIGS: lookup GunType → GunSpec
│   └── output/
│       └── simulation_result.py  # SimulationResult: final aggregated result
│
├── calculators/                 # One calculator = one question, no cross-dependencies
│   ├── wet_bulb_calculator.py   # What's the wet-bulb temperature?
│   ├── viability.py             # Can we operate?
│   ├── production.py            # How much snow per hour?
│   ├── quality.py               # What snow quality?
│   ├── energy.py                # How much energy does it consume?
│   └── efficiency.py            # (pending)
│
├── engine/
│   ├── snowEngine.py            # SnowEngine.simulate() — orchestrates the calculators
│   └── __init__.py              # re-exports SnowEngine
│
├── presets/                     # Manufacturer-specific configs (pending)
│   ├── fan_basic.py
│   ├── lance_basic.py
│   └── technoalpin_tf10.py
│
├── ui/                           # Streamlit — inputs that return domain models
│   ├── weather.py                # render_weather() → Weather
│   ├── snowgun.py                # render_snowgun() → SnowGun
│   ├── charts.py                 # Plotly visualizations
│   └── footer.py                 # Social links footer
│
├── i18n/                         # UI translations scaffold — NOT yet wired in (see Known Issues)
│   ├── strings.py                # Translation dictionary
│   └── translator.py             # t() helper + language selector
│
├── docs/                         # In-app documentation content (Snowmaking/Architecture/Technical)
├── pages/                        # Streamlit multipage entries for the docs above
├── tests/                        # (pending)
├── app.py                        # UI entry point
└── main.py                       # Minimal CLI entry point
```

## Design Principle: Single Responsibility per Layer

```
INPUTS (models)  →  CALCULATORS  →  ENGINE  →  RESULT  →  UI (Streamlit)
```

Each `calculator` answers **one single question** and doesn't know about the others. `WetBulbCalculator` has no idea `ViabilityCalculator` exists — it just returns a `float`. `SnowEngine` is the only piece that knows the dependency order and chains outputs from one calculator into the next:

```python
wet_bulb   = wet_bulb_calculator.calculate(weather)
viability  = viability_calculator.calculate(wet_bulb)
production = production_calculator.calculate(snowgun)
quality    = quality_calculator.calculate(wet_bulb)
energy     = energy_calculator.calculate(snowgun, production.water_flow_lpm, production.snow_volume_m3h)
```

Practical benefit: each calculator can be tested in isolation, without mocking Streamlit or other calculators. The Stull formula could be swapped for a real psychrometric table without touching `viability.py`, `quality.py`, or the UI — they all consume `wet_bulb: float`, not the formula itself.

On the UI side, each `render_*` function in `ui/` returns a domain model directly (`Weather`, `SnowGun`), not a loose dict of values — `app.py` doesn't know about sliders or defaults, it just orchestrates. This means Streamlit could be swapped for another interface (CLI, REST API) while reusing 100% of `models/`, `calculators/`, and `engine/`.

> Result labels and descriptions are currently generated as hardcoded Spanish strings inside `viability.py` and `quality.py`. Once `i18n/` is wired in, this text should move to the presentation layer (see Known Issues), so calculators only return codes (`zone`, `grade`) and stay language-agnostic.

## Why dataclasses

All models are `@dataclass`:

- **Less boilerplate:** no need to hand-write `__init__` for classes that are, essentially, data containers.
- **Free `__eq__` and `__repr__`:** useful for tests and debugging.
- **Optional immutability:** `@dataclass(frozen=True)` on `GunSpec`, `Range`, and every calculator `*Result` — once created, they can't be accidentally mutated mid-simulation.
- **Explicit validation where needed:** `SnowGun` is the only non-frozen model, because it needs `__post_init__` to validate that the given pressures fall within the range allowed by its `GunSpec`. That's validation logic, not calculation — which is why it lives in the model, not in a calculator.

## Configuration Pattern: Lookup Table

`models/snowgun_config.py` maps `GunType → GunSpec` via a simple dictionary (equivalent to `Record<GunType, GunSpec>` in TypeScript):

```python
GUN_CONFIGS: dict[GunType, GunSpec] = {
    GunType.MONO_FLUID: GunSpec(...),
    GunType.BI_FLUID: GunSpec(...),
}
```

Today the key is the generic gun type. The design anticipates that in the future the key could become a specific manufacturer model (e.g. `"TechnoAlpin TF10"`) without needing to touch `GunSpec` — only the dictionary would change. The empty files in `presets/` are placeholders for that path.

## Imports

The project uses absolute imports from the root (`from models.weather import Weather`), except for `engine/__init__.py` and `models/__init__.py`, which re-export using relative imports. Because of this, always run commands **from the project root**.

`models/__init__.py` centralizes public exports:

```python
from models import Weather, SnowGun, GUN_CONFIGS
```

## Empirical Constants by Module

Quick reference for where each "magic number" used in the calculations comes from:

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

If any of these values change, update only the corresponding calculator — there's no duplication across other layers.

## Testing

`tests/` exists but is currently empty. Given the decoupled design, the recommended pattern is to test each calculator in isolation:

```python
def test_wet_bulb_matches_known_value():
    weather = Weather(temperature=-5, humidity=50)
    result = WetBulbCalculator().calculate(weather)
    assert result == pytest.approx(-9.9, abs=0.5)
```

No calculator needs Streamlit, a full `SnowGun`, or `SnowEngine` to be tested — just its own minimal input.

## Known Issues / Technical Debt

- `main.py` imports `from engine.snowmaking_engine import SnowmakingEngine`, but the actual file is `engine/snowEngine.py` with the class `SnowEngine`. This import is currently broken.
- `calculators/efficiency.py` is pending implementation.
- `presets/fan_basic.py`, `presets/lance_basic.py`, and `presets/technoalpin_tf10.py` are empty — intentional placeholders for manufacturer-specific configurations.
- The Stull formula doesn't correct for atmospheric pressure / altitude.
- `i18n/` (ES/EN toggle) is scaffolded (`strings.py`, `translator.py`) but not yet integrated — `app.py`, `ui/weather.py`, and `ui/snowgun.py` still use hardcoded strings, and `viability.py`/`quality.py` still return hardcoded Spanish `label`/`description` text instead of language-agnostic codes.

## Deploy

- Entry point: `app.py` (not `main.py`, which is CLI-only).
- `requirements.txt` must include at least `streamlit` and `plotly`.
- Pages under `pages/` are automatically detected by Streamlit, no extra configuration needed.

## Author

Santiago Fernández

- [LinkedIn](https://www.linkedin.com/in/santiago-fernandez-7471a1153/)
- [GitHub](https://github.com/SF1308)
- [Instagram](https://www.instagram.com/santiago.fz96/)
