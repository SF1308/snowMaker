# Snow Maker Simulator

A physics-based snowmaking simulation engine that models artificial snow production based on real weather conditions and snow gun configuration.

## Overview

This simulator takes real-world inputs — atmospheric conditions and snow gun settings — and calculates whether artificial snow production is viable, how much snow can be produced, and what quality to expect. The core calculation is based on the **Stull formula** for wet-bulb temperature, the key meteorological variable in snowmaking.

## Project Structure

```
snow-maker-simulator/
│
├── models/                     # Data models (inputs)
│   ├── weather.py              # Weather conditions (temperature, humidity)
│   ├── snowgun.py              # Snow gun hardware config (flow, pressure)
│   └── operation.py            # Operational settings (nozzles, fan, compressor)
│
├── calculators/                # Single-responsibility calculation services
│   ├── wet_bulb_calculator.py  # Wet-bulb temperature via Stull formula ✓
│   ├── viability.py            # Can snow be made? (wet-bulb threshold check)
│   ├── production.py           # How much snow per hour?
│   ├── quality.py              # Snow quality (grain size, hardness)
│   ├── efficiency.py           # Energy and water efficiency
│   └── energy.py               # Energy consumption estimation
│
├── engine/
│   └── snowmaking_engine.py    # Orchestrates all calculators → SnowmakingResult
│
├── outputs/
│   └── snowmaking_result.py    # Output data model
│
├── app.py                      # Streamlit UI
├── main.py                     # CLI entry point
└── README.md
```

## Architecture

The project follows a layered architecture with clear separation of concerns:

```
Inputs (models)  →  Calculators (services)  →  Engine  →  Result  →  UI
```

Each layer has a single responsibility:

- **Models** — pure data containers, no logic
- **Calculators** — each answers one specific question (viability, production rate, quality)
- **Engine** — orchestrates calculators, produces the final result
- **Output** — structured result passed to the UI

This design means each service can be developed, tested, and improved independently.

## Core Concept: Wet-Bulb Temperature

The critical variable in snowmaking is not air temperature — it's **wet-bulb temperature (Tw)**. Wet-bulb temperature accounts for evaporative cooling and is always equal to or lower than the dry-bulb temperature.

General thresholds:

| Wet-bulb temp | Snowmaking |
|---|---|
| Tw > -2°C | Not viable |
| -2°C ≥ Tw > -5°C | Marginal — wet, heavy snow |
| Tw ≤ -5°C | Optimal — dry, high-quality snow |

The simulator uses the **Stull (2011)** empirical formula to calculate wet-bulb temperature from dry-bulb temperature and relative humidity.

## Getting Started

### Requirements

- Python 3.10+
- `streamlit` (for the UI)

### Installation

```bash
pip install streamlit
```

### Run the CLI

```bash
python main.py
```

### Run the Streamlit app

```bash
streamlit run app.py
```

## Status

This project is in early development. The wet-bulb calculator is functional; remaining services are under construction.

| Component | Status |
|---|---|
| `WetBulbCalculator` | ✅ Done |
| `ViabilityCalculator` | 🔧 In progress |
| `ProductionCalculator` | 🔧 In progress |
| `QualityCalculator` | 🔧 In progress |
| `SnowmakingEngine` | 🔧 In progress |
| Streamlit UI | 🔧 In progress |

## References

- Stull, R. (2011). *Wet-Bulb Temperature from Relative Humidity and Air Temperature*. Journal of Applied Meteorology and Climatology.
