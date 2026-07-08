# Fabricación de nieve artificial

## Por qué el bulbo húmedo y no la temperatura del aire

La variable crítica para producir nieve artificial **no es la temperatura seca del aire**, sino la **temperatura de bulbo húmedo (Tw)**.

Cuando el agua se pulveriza en el aire, parte se evapora. Esa evaporación consume calor y enfría las gotas restantes por debajo de la temperatura del aire. Cuanto más seco esté el aire (menor humedad relativa), más evaporación ocurre y más frío efectivo se logra. Por eso, con la misma temperatura de aire, un día seco permite hacer nieve y un día húmedo no.

El bulbo húmedo es siempre **igual o menor** a la temperatura seca, y la brecha entre ambas crece cuanto más seco está el ambiente.

## Fórmula de Stull (2011)

El simulador usa la aproximación empírica de Stull para calcular Tw sin necesitar presión atmosférica ni tablas psicrométricas — solo temperatura seca (T) y humedad relativa (RH, en %):

```
Tw = T·atan(0.151977·√(RH + 8.313659))
   + atan(T + RH)
   - atan(RH − 1.676331)
   + 0.00391838·RH^1.5·atan(0.023101·RH)
   − 4.686035
```

Está implementada en `calculators/wet_bulb_calculator.py`. Es una fórmula de ajuste (curve fitting), no una derivación física directa — por eso funciona bien en rangos meteorológicos normales pero pierde precisión en extremos (RH muy cercano a 0% o a 100%, temperaturas muy extremas).

> **Nota:** la fórmula de Stull fue pensada para presión atmosférica estándar a nivel del mar. En altitudes altas (donde suele haber pistas de esquí) la presión real introduce un margen de error que este modelo no corrige. Es un punto abierto para una futura iteración (ver `docs/docs.txt` → "Presión atmosférica").

## Umbrales de viabilidad

| Bulbo húmedo (Tw) | Zona | Se puede hacer nieve | Calidad esperada |
|---|---|---|---|
| Tw > −2°C | `impossible` | No | — |
| −5°C < Tw ≤ −2°C | `marginal` | Sí | Nieve húmeda y pesada |
| Tw ≤ −5°C | `optimal` | Sí | Nieve seca de alta calidad |

Estos umbrales están centralizados en `calculators/viability.py` (`THRESHOLD_IMPOSSIBLE`, `THRESHOLD_MARGINAL`) y son los que definen el badge de estado (verde/amarillo/rojo) en la UI.

## Calidad de la nieve según temperatura

Cuanto más frío el bulbo húmedo, más pequeños son los cristales de hielo y más densa/compacta resulta la nieve:

- **Tamaño de grano:** `grain_mm ≈ 0.8 − 0.06·|Tw|` (acotado entre 0.2 y 0.8 mm)
- **Densidad:** `density ≈ 280 + 12·|Tw|` kg/m³ (acotado entre 280 y 450 kg/m³)

Esto da tres grados de calidad (`calculators/quality.py`):

| Grado | Condición | Descripción |
|---|---|---|
| **A** | Tw ≤ −5°C | Nieve seca, cristales finos, alta densidad |
| **B** | −5°C < Tw ≤ −2°C | Nieve húmeda, cristales medianos |
| **C** | Tw > −2°C (marginal) | Nieve marginal |

## Tipos de cañón: mono-fluid vs bi-fluid

El proyecto modela dos tecnologías de generación (`models/gun_type.py`):

- **Mono-fluid (fan gun):** solo agua a alta presión, sin aire comprimido. Usa un ventilador para atomizar y proyectar el agua. Requiere condiciones más frías para funcionar bien (`minimum_wet_bulb = −2.5°C` en la config actual) pero es más eficiente energéticamente a gran escala.
- **Bi-fluid (lance):** combina agua + aire comprimido para atomizar las gotas en tamaños más finos mecánicamente. Puede operar en condiciones más marginales (`minimum_wet_bulb = −0.5°C`) porque no depende tanto de la evaporación natural, a costa de necesitar un compresor de aire (energía extra, ver `calculators/energy.py`).

Estos parámetros están en `models/snowgun_config.py`, como tabla de lookup por `GunType`.

## Producción y consumo energético

- **Caudal de agua:** modelado como `Q ∝ nozzles × √(presión)` — una aproximación genérica de flujo por orificio (`calculators/production.py`).
- **Conversión agua → nieve:** 1 L de agua ≈ 3 L de nieve compactada (densidad ≈ 350 kg/m³ para el volumen estimado).
- **Energía:** la bomba de agua se modela como `P = (Q·ΔP) / η`, con η = 0.75. El compresor de aire (solo bi-fluid) usa una aproximación similar con η = 0.70 (`calculators/energy.py`).

## Referencias

- Stull, R. (2011). *Wet-Bulb Temperature from Relative Humidity and Air Temperature*. Journal of Applied Meteorology and Climatology.
- Lavanchy & Brun (2002). *Guns and Snow*.
- Especificaciones técnicas TechnoAlpin.
- Fierz et al. (2009). *International Classification for Seasonal Snow*.

---

⚠️ Los valores de producción, calidad y energía son **aproximaciones para simulación educativa**, no deben usarse para decisiones operativas reales.
