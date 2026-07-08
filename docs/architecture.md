# Arquitectura del proyecto

## Filosofía general

El proyecto sigue una arquitectura en capas con **responsabilidad única por módulo**. La idea central: cada calculador responde **una sola pregunta**, no conoce a los demás calculadores, y el motor (`engine`) es el único que los orquesta. Esto permite testear, reemplazar o extender cada pieza sin tocar el resto.

```
INPUTS (models)  →  CALCULATORS  →  ENGINE  →  RESULT  →  UI (Streamlit)
```

## Capas

### 1. Models — datos puros, sin lógica

```
models/
├── weather.py          # Weather: temperature, humidity, wind_speed
├── snowgun.py           # SnowGun: spec + presiones actuales, valida rangos
├── gun_spec.py          # GunSpec: configuración técnica de un tipo de cañón
├── gun_type.py          # GunType: enum mono_fluid | bi_fluid
├── primitives.py        # Range: min/max genérico reusable
├── snowgun_config.py    # GUN_CONFIGS: lookup GunType → GunSpec
└── output/
    └── simulation_result.py   # SimulationResult: resultado final agregado
```

Todos son `@dataclass`. La razón (ver también `docs/docs.txt`):

- **Menos código repetitivo**: no hace falta escribir `__init__` a mano para clases que son, en esencia, contenedores de datos.
- **Comparación e impresión gratis**: `__eq__` y `__repr__` autogenerados, útil para tests y debugging.
- **Inmutabilidad opcional**: `@dataclass(frozen=True)` en `GunSpec`, `Range` y los resultados de calculadores — una vez creado un `GunSpec`, no se puede mutar por accidente en medio de una simulación.
- **Validación explícita**: `SnowGun` no es `frozen` porque necesita `__post_init__` para validar que las presiones ingresadas estén dentro del rango permitido por su `GunSpec`. Es el único modelo con lógica, y esa lógica es *solo* validación, no cálculo.

### 2. Calculators — una pregunta cada uno

```
calculators/
├── wet_bulb_calculator.py   # ¿Cuál es el bulbo húmedo? (Stull)
├── viability.py             # ¿Se puede hacer nieve con este Tw?
├── production.py            # ¿Cuánta nieve por hora?
├── quality.py               # ¿Qué calidad de nieve?
└── energy.py                # ¿Cuánta energía consume el sistema?
```

Ningún calculator importa a otro. `WetBulbCalculator` no sabe que existe `ViabilityCalculator`; simplemente devuelve un `float`. Es el `engine` quien encadena las salidas de uno como entrada del siguiente (por ejemplo, `wet_bulb` es entrada tanto de `viability` como de `quality`).

Cada calculator devuelve su propio `*Result` (dataclass frozen), no un dict genérico — esto da autocompletado y chequeo de tipos en el resto del código.

> `calculators/efficiency.py` existe como archivo pero está vacío — es el próximo calculator a implementar (probablemente eficiencia hídrica/energética combinada, a diferenciar de `energy.py` que ya calcula consumo eléctrico puro).

### 3. Engine — el orquestador

```
engine/
├── snowEngine.py         # SnowEngine.simulate(weather, snowgun) → SimulationResult
└── __init__.py           # re-exporta SnowEngine
```

`SnowEngine` instancia todos los calculators en su `__init__` y en `simulate()` los llama en orden, pasando los resultados intermedios donde corresponde:

```python
wet_bulb   = wet_bulb_calculator.calculate(weather)
viability  = viability_calculator.calculate(wet_bulb)
production = production_calculator.calculate(snowgun)
quality    = quality_calculator.calculate(wet_bulb)
energy     = energy_calculator.calculate(snowgun, production.water_flow_lpm, production.snow_volume_m3h)
```

Es la **única** clase que conoce el orden de dependencias entre calculators. Si mañana `quality` necesitara también `production`, el cambio se hace acá y en ningún otro lado.

> Existe también `main.py` que instancia `WetBulbCalculator` directamente, sin pasar por `SnowEngine` — es el punto de entrada mínimo por CLI, útil para debugging rápido de la fórmula de Stull sin levantar Streamlit. Nota: hoy importa `SnowmakingEngine` desde `engine.snowmaking_engine`, que no coincide con el archivo real `engine/snowEngine.py` — es un import a corregir.

### 4. UI — Streamlit

```
ui/
├── weather.py    # render_weather() → Weather (sliders de temp/humedad/viento)
└── snowgun.py    # render_snowgun() → SnowGun (selectbox de tipo + sliders de presión)

app.py            # arma la página, llama a los render_*, instancia SnowEngine, muestra resultado
```

Cada `render_*` de `ui/` devuelve directamente un modelo de dominio (`Weather`, `SnowGun`), no un dict de valores sueltos. `app.py` no conoce sliders ni valores por defecto — solo orquesta: "pedile a la UI un Weather y un SnowGun, pasáselos al engine, mostrá el resultado". Esto significa que se podría reemplazar Streamlit por otra interfaz (CLI, API REST) reutilizando el 100% de `models/`, `calculators/` y `engine/`.

## Patrón de configuración: lookup table

`models/snowgun_config.py` mapea `GunType → GunSpec` mediante un diccionario simple:

```python
GUN_CONFIGS: dict[GunType, GunSpec] = {
    GunType.MONO_FLUID: GunSpec(...),
    GunType.BI_FLUID: GunSpec(...),
}
```

Equivalente conceptual a `Record<GunType, GunSpec>` en TypeScript. Hoy la clave es el tipo genérico de cañón (mono/bi-fluid); el diseño está pensado para que el día de mañana la clave pase a ser un modelo específico de fabricante (ej. `"TechnoAlpin TF10"`) **sin tener que tocar `GunSpec`** — solo cambia el diccionario y quién arma las claves.

De hecho, `presets/technoalpin_tf10.py`, `presets/fan_basic.py` y `presets/lance_basic.py` existen como archivos (hoy vacíos) anticipando ese camino: presets concretos de fabricante que en algún momento poblarán configuraciones más específicas que las genéricas de `snowgun_config.py`.

## Diagrama de flujo completo

```
┌─────────────────────────────────────────────────────────────┐
│                          INPUTS                              │
│   Weather (temp, humedad)   SnowGun (spec + presiones)       │
└──────────────┬────────────────────────┬───────────────────────┘
               ▼                        ▼
     WetBulbCalculator          ProductionCalculator
               │                        │
       ┌───────┴───────┐                │
       ▼               ▼                ▼
ViabilityCalculator  QualityCalculator  EnergyCalculator
       │               │                │
       └───────┬────────┴────────┬──────┘
               ▼
          SnowEngine.simulate()
               ▼
        SimulationResult
               ▼
        Streamlit UI (app.py)
```

## Por qué esta separación importa

- **Testeable**: cada calculator se testea aislado, sin mocks de Streamlit ni de otros calculators (ver `tests/`).
- **Extensible**: agregar un nuevo calculator (ej. `efficiency.py`) no rompe a los existentes.
- **Reemplazable**: la fórmula de Stull podría cambiarse por una tabla psicrométrica real sin tocar `viability.py`, `quality.py` ni la UI — todos consumen `wet_bulb: float`, no la fórmula en sí.
