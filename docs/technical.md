# Documentación técnica

## Stack

- **Python 3.10+** (usa sintaxis `float | None`, disponible desde 3.10)
- **Streamlit** — única dependencia externa para la UI
- **dataclasses** (stdlib) — modelado de datos
- **math** (stdlib) — funciones trigonométricas de la fórmula de Stull

No hay dependencias de terceros para el motor de cálculo (`calculators/`, `engine/`, `models/`) — solo `app.py` y `ui/` dependen de Streamlit. Esto es intencional: la lógica de dominio queda libre de framework.

## Instalación local

```bash
git clone <repo-url>
cd snow-maker-simulator
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install streamlit
```

### Correr el motor por CLI (sin UI)

```bash
python main.py
```

Calcula el bulbo húmedo para condiciones fijas (hoy hardcodeadas en `main.py`: −5°C, 50% humedad) y lo imprime por consola. Útil para verificar rápido la fórmula de Stull sin levantar el server.

### Correr la app Streamlit

```bash
streamlit run app.py
```

Abre en `http://localhost:8501` por defecto.

### Codespaces / Devcontainer

El proyecto incluye `.devcontainer/devcontainer.json` basado en la imagen `python:3.11-bookworm`. Al abrir en GitHub Codespaces:
- Instala automáticamente `requirements.txt` (si existe) y `streamlit`.
- Levanta `streamlit run app.py` en el puerto `8501` con auto-forward y preview automático.

## Estructura de imports

El proyecto usa imports absolutos desde la raíz (`from models.weather import Weather`, no relativos), excepto dentro de `engine/__init__.py` y `models/__init__.py`, que sí re-exportan con imports relativos (`from .snowEngine import SnowEngine`). Para que esto funcione, siempre correr los comandos (`python main.py`, `streamlit run app.py`) **desde la raíz del proyecto**.

`models/__init__.py` centraliza los exports públicos del paquete:

```python
from .gun_spec import GunSpec
from .gun_type import GunType
from .primitives import Range
from .snowgun import SnowGun
from .snowgun_config import GUN_CONFIGS
from .weather import Weather
```

Esto permite `from models import Weather, SnowGun, GUN_CONFIGS` en vez de importar archivo por archivo.

## Constantes empíricas por módulo

Centralizado acá para tener una sola referencia rápida de "de dónde sale cada número mágico":

| Constante | Valor | Ubicación | Fuente/origen |
|---|---|---|---|
| Coeficientes de Stull | `0.151977`, `8.313659`, `1.676331`, `0.00391838`, `0.023101`, `4.686035` | `wet_bulb_calculator.py` | Stull (2011), ajuste empírico |
| `THRESHOLD_IMPOSSIBLE` | −2.0 °C | `viability.py` | Umbral industria snowmaking |
| `THRESHOLD_MARGINAL` | −5.0 °C | `viability.py` | Umbral industria snowmaking |
| `WATER_DENSITY_KGL` | 1.0 kg/L | `production.py` | Física estándar |
| `SNOW_DENSITY_KGM3` | 350.0 kg/m³ | `production.py` | Nieve artificial típica |
| `WATER_TO_SNOW_VOLUME` | 3.0 | `production.py` | Aprox. Lavanchy & Brun (2002) |
| `NOZZLE_K` | 2.8 | `production.py` | Empírico, L/min por boquilla @ 1 bar |
| `ETA_PUMP` | 0.75 | `energy.py` | Bomba centrífuga típica |
| `ETA_COMP` | 0.70 | `energy.py` | Compresor típico |
| `AIR_FLOW_PER_BAR` | 0.06 m³/s | `energy.py` | Aproximación |
| Rango tamaño de grano | 0.2–0.8 mm | `quality.py` | Fierz et al. (2009) |
| Rango densidad de nieve | 280–450 kg/m³ | `quality.py` | Fierz et al. (2009) |

Si estos valores cambian, **modificar solo en el calculator correspondiente** — no hay duplicación en otras capas.

## Validaciones y manejo de errores

`SnowGun.__post_init__` (`models/snowgun.py`) es el único punto de validación de datos de entrada del lado de cañón:

- Rechaza `water_pressure_bar` fuera del rango de `GunSpec.water_pressure` con `ValueError`.
- Si el `GunSpec` no soporta aire (`air_pressure is None`) pero se pasó `air_pressure_bar`, levanta `ValueError`.
- Si el `GunSpec` requiere aire y no se pasó `air_pressure_bar`, levanta `ValueError`.
- Si se pasó aire, valida que esté dentro de rango.

No hay try/except alrededor de la construcción de `SnowGun` en `ui/snowgun.py` — los sliders de Streamlit ya restringen los valores a los rangos válidos de `GunSpec`, por lo que en la práctica el `ValueError` solo se dispararía si se instancia `SnowGun` manualmente (ej. en tests o en `main.py` a futuro) con valores fuera de rango.

## Testing

`tests/` existe con `__init__.py` pero sin tests implementados aún. Dado el diseño desacoplado (cada calculator es una clase con un método `calculate()` sin dependencias externas), el patrón recomendado es:

```python
def test_wet_bulb_matches_known_value():
    weather = Weather(temperature=-5, humidity=50)
    result = WetBulbCalculator().calculate(weather)
    assert result == pytest.approx(-9.9, abs=0.5)  # verificar contra valor de referencia
```

Cada calculator puede testearse sin instanciar Streamlit, `SnowGun` completo, ni el `SnowEngine` — solo su propio input mínimo.

## Known issues / deuda técnica

- `main.py` importa `from engine.snowmaking_engine import SnowmakingEngine`, pero el archivo real es `engine/snowEngine.py` con la clase `SnowEngine`. Este import está roto y debe corregirse.
- `calculators/efficiency.py` está vacío — pendiente de implementación.
- Los tres archivos en `presets/` (`fan_basic.py`, `lance_basic.py`, `technoalpin_tf10.py`) están vacíos — son placeholders para configuraciones específicas de fabricante mencionadas en `architecture.md`.
- La fórmula de Stull no corrige por presión atmosférica/altitud (ver `docs/snowmaking.md`).

## Requisitos para correr en producción / deploy

Si se despliega en Streamlit Community Cloud u otro hosting compatible:

- Asegurar `requirements.txt` con al menos `streamlit`.
- El entry point es `app.py` (no `main.py` — ese es solo CLI).
- Si se agregan las páginas de documentación como multipage (`pages/`), Streamlit las detecta automáticamente sin configuración adicional.
