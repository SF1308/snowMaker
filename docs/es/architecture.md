# Architecture: cómo calcula el simulador

Acá está el detalle de qué fórmula usa cada paso del cálculo, con qué parámetros, y en qué orden el motor (`SnowEngine`) los encadena.

## 1. Bulbo húmedo — fórmula de Stull (2011)

El simulador no usa tablas psicrométricas ni necesita presión atmosférica: aproxima el bulbo húmedo (Tw) directamente a partir de temperatura seca (T, °C) y humedad relativa (RH, %) con la fórmula empírica de Stull:

```
Tw = T·atan(0.151977·√(RH + 8.313659))
   + atan(T + RH)
   − atan(RH − 1.676331)
   + 0.00391838·RH^1.5·atan(0.023101·RH)
   − 4.686035
```

Es un ajuste por regresión, no una derivación física — funciona bien en rangos meteorológicos normales, pero pierde precisión en extremos (RH cercano a 0% o 100%, temperaturas muy extremas). Tampoco corrige por altitud: fue calibrada a presión atmosférica estándar a nivel del mar, así que en pistas de esquí a gran altura introduce un margen de error que hoy el simulador no compensa.

Este valor de Tw es la entrada principal de casi todo lo que sigue.

## 2. Umbrales de viabilidad

A partir de Tw, se decide si se puede operar y en qué régimen:

| Bulbo húmedo (Tw) | Zona | ¿Se puede fabricar nieve? | Resultado esperado |
|---|---|---|---|
| Tw > −2°C | `impossible` | No | — |
| −5°C < Tw ≤ −2°C | `marginal` | Sí | Nieve húmeda y pesada, rendimiento reducido |
| Tw ≤ −5°C | `optimal` | Sí | Nieve seca, alta calidad |

Estos umbrales son estándares de industria, no específicos de un fabricante — representan el punto en que la evaporación ya no compensa lo suficiente como para congelar bien las gotas en el aire.

## 3. Producción de nieve

La producción depende del caudal de agua, que a su vez depende de la presión y de la cantidad de boquillas del cañón:

```
Q (L/min) = K × nozzles × √(presión en bar)
```

donde `K = 2.8` es un coeficiente empírico (litros por minuto por boquilla a 1 bar de referencia).

A partir de ahí:

- **Volumen de nieve por hora:** se asume que 1 L de agua produce ~3 L de nieve compactada (`WATER_TO_SNOW_VOLUME = 3.0`).
- **Masa de nieve por hora:** el volumen se multiplica por una densidad típica de nieve artificial de **350 kg/m³**.

Notá que esta parte del cálculo depende del **cañón** (boquillas, presión), no directamente del clima — es decir, un día muy frío no produce automáticamente más nieve; produce **mejor calidad** de nieve, pero el volumen depende de cuánta agua estés bombeando.

## 4. Calidad de la nieve

Acá sí vuelve a entrar Tw. La lógica es: cuanto más frío el bulbo húmedo, más chicos son los cristales de hielo formados y más densa/compacta resulta la nieve:

```
grain_mm  ≈ 0.8 − 0.06 × |Tw|     (acotado entre 0.2 y 0.8 mm)
density   ≈ 280 + 12 × |Tw|       (acotado entre 280 y 450 kg/m³)
```

Y el grado de calidad se asigna directamente por los mismos umbrales de viabilidad:

| Grado | Condición | Descripción |
|---|---|---|
| **A** | Tw ≤ −5°C | Nieve seca, cristales finos, alta densidad |
| **B** | −5°C < Tw ≤ −2°C | Nieve húmeda, cristales medianos |
| **C** | Tw > −2°C (zona marginal) | Nieve marginal |

## 5. Consumo energético

Se modelan dos consumos independientes:

**Bomba de agua** (siempre presente):
```
P_pump = (Q_agua × ΔP) / η_bomba,   η_bomba = 0.75
```
donde Q_agua es el caudal en m³/s y ΔP es la presión de trabajo en Pa.

**Compresor de aire** (solo en cañones bi-fluido, que usan aire comprimido):
```
P_comp = (Q_aire × P_aire) / η_comp,   η_comp = 0.70
```
donde el caudal de aire se aproxima como `0.06 m³/s por cada bar de presión de aire`.

La suma de ambos da la potencia total, y se calcula además una intensidad energética (`kWh por m³ de nieve producida`) para comparar eficiencia entre configuraciones.

## 6. Cómo el SnowEngine encadena todo

El orden importa porque hay dependencias entre pasos. El motor sigue esta secuencia:

```
1. Clima (T, RH) ────────────► bulbo húmedo (Tw)
2. Tw ────────────────────────► viabilidad (¿se puede operar?)
3. Cañón (boquillas, presión) ► producción (caudal, volumen, masa)
4. Tw ────────────────────────► calidad (grano, densidad, grado)
5. Cañón + producción ────────► energía (potencia, intensidad)
```

Es decir: **Tw se calcula una sola vez** y alimenta tanto a viabilidad como a calidad. Producción depende únicamente del cañón (no del clima). Y energía depende tanto del cañón como del resultado de producción (porque necesita saber cuánta agua se está moviendo para estimar la potencia de bombeo).

Esto explica un comportamiento que puede parecer contraintuitivo: **podés tener alta producción con mala calidad**, si el cañón tiene mucha presión pero el clima está en zona marginal. Producción y calidad son ejes independientes.

## 7. Parámetros por tipo de cañón

Antes de ver los números, una aclaración de terminología: en la industria hay dos clasificaciones distintas de cañones de nieve, y conviene no mezclarlas.

- **Fan gun vs. lanza (lance/stick)** clasifica **cómo se proyecta** el agua: con ventilador, o aprovechando la altura de una torre estática.
- **Mono-fluido vs. bi-fluido** clasifica **cómo se atomiza** el agua: solo con presión de agua, o mezclándola con aire comprimido en la boquilla.

Son ejes independientes — en la realidad existen fan guns mono-fluidos, fan guns bi-fluidos, lanzas mono-fluidas y lanzas bi-fluidas. Este simulador modela únicamente el eje **mono-fluido / bi-fluido** (`GunType` en el código), porque es el que determina el `minimum_wet_bulb` — el umbral climático mínimo para operar cada sistema:

| Parámetro | Mono-fluido | Bi-fluido |
|---|---|---|
| Boquillas | 6 | 4 |
| Altura | 12 m | 8 m |
| Presión de agua | 20–40 bar | 5–10 bar |
| Presión de aire | No usa | 4–7 bar |
| Bulbo húmedo mínimo para operar | −2.5°C | −0.5°C |

El bi-fluido puede operar con condiciones climáticas menos exigentes (−0.5°C vs. −2.5°C) porque la expansión del aire comprimido genera un enfriamiento adicional en el momento de la nucleación, sin depender tanto de que el aire ambiente evapore y enfríe el agua por sí solo. A cambio, consume energía extra en el compresor que el mono-fluido no necesita.

> Si en algún momento el proyecto quisiera modelar también el eje fan gun / lanza (por ejemplo, para variar el alcance o la distribución de la nieve en el terreno), sería un segundo `enum` independiente de `GunType`, no una extensión del mismo — son dos dimensiones distintas del cañón, no una jerarquía.

## Referencias

- Stull, R. (2011). *Wet-Bulb Temperature from Relative Humidity and Air Temperature*. Journal of Applied Meteorology and Climatology.
- Lavanchy & Brun (2002). *Guns and Snow*.
- Fierz et al. (2009). *International Classification for Seasonal Snow*.
- Especificaciones técnicas TechnoAlpin.

---

¿Te interesa cómo está implementado esto en código (carpetas, clases, stack)? Pasá a **Technical**.
