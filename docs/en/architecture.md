# Architecture: how the simulator calculates

This page explains which formula each step uses, which parameters are involved, and in what order the engine (`SnowEngine`) chains them.

## 1. Wet bulb — Stull formula (2011)

The simulator does not use psychrometric tables or require atmospheric pressure: it approximates the wet bulb temperature (Tw) directly from dry bulb temperature (T, °C) and relative humidity (RH, %) using the empirical Stull formula:

```
Tw = T·atan(0.151977·√(RH + 8.313659))
   + atan(T + RH)
   − atan(RH − 1.676331)
   + 0.00391838·RH^1.5·atan(0.023101·RH)
   − 4.686035
```

This is a regression fit, not a physical derivation — it works well in normal meteorological ranges, but loses precision at extremes (RH near 0% or 100%, very extreme temperatures). It also does not correct for altitude: it was calibrated at standard sea-level pressure, so at high-altitude ski resorts it introduces an error margin the simulator does not currently compensate.

This Tw value is the main input for almost everything that follows.

## 2. Viability thresholds

From Tw, the simulator decides whether operation is possible and in what regime:

| Wet bulb (Tw) | Zone | Can snow be made? | Expected result |
|---|---|---|---|
| Tw > −2°C | `impossible` | No | — |
| −5°C < Tw ≤ −2°C | `marginal` | Yes | Wet, heavy snow; reduced output |
| Tw ≤ −5°C | `optimal` | Yes | Dry snow, high quality |

These thresholds are industry standards, not manufacturer-specific — they represent the point at which evaporation no longer cools the droplets enough to freeze them well in the air.

## 3. Snow production

Production depends on the water flow, which in turn depends on pressure and the number of gun nozzles:

```
Q (L/min) = K × nozzles × √(pressure in bar)
```

where `K = 2.8` is an empirical coefficient (liters per minute per nozzle at 1 bar reference).

From there:

- **Snow volume per hour:** assumes 1 L of water produces ~3 L of compacted snow (`WATER_TO_SNOW_VOLUME = 3.0`).
- **Snow mass per hour:** the volume is multiplied by a typical artificial snow density of **350 kg/m³**.

Note that this part of the calculation depends on the **gun** (nozzles, pressure), not directly on the weather — a very cold day does not automatically produce more snow; it produces **better snow quality**, while volume depends on how much water you are pumping.

## 4. Snow quality

Here Tw comes back into play. The logic is: the colder the wet bulb, the smaller the ice crystals formed and the denser/more compact the snow:

```
grain_mm  ≈ 0.8 − 0.06 × |Tw|     (clamped between 0.2 and 0.8 mm)
density   ≈ 280 + 12 × |Tw|       (clamped between 280 and 450 kg/m³)
```

Quality grade is assigned directly using the same viability thresholds:

| Grade | Condition | Description |
|---|---|---|
| **A** | Tw ≤ −5°C | Dry snow, fine crystals, high density |
| **B** | −5°C < Tw ≤ −2°C | Wet snow, medium crystals |
| **C** | Tw > −2°C (marginal zone) | Marginal snow |

## 5. Energy consumption

Two independent consumptions are modeled:

**Water pump** (always present):
```
P_pump = (Q_water × ΔP) / η_pump,   η_pump = 0.75
```
where `Q_water` is flow in m³/s and `ΔP` is working pressure in Pa.

**Air compressor** (only for bi-fluid guns that use compressed air):
```
P_comp = (Q_air × P_air) / η_comp,   η_comp = 0.70
```
where the air flow is approximated as `0.06 m³/s per bar of air pressure`.

The sum of both yields total power, and an energy intensity (`kWh per m³ of snow produced`) is also calculated to compare efficiency across configurations.

## 6. How SnowEngine chains everything

Order matters because there are dependencies between steps. The engine follows this sequence:

```
1. Weather (T, RH) ────────────► wet bulb (Tw)
2. Tw ────────────────────────► viability (can it operate?)
3. Gun (nozzles, pressure) ► production (flow, volume, mass)
4. Tw ────────────────────────► quality (grain, density, grade)
5. Gun + production ────────► energy (power, intensity)
```

In other words: **Tw is calculated only once** and feeds both viability and quality. Production depends solely on the gun (not the weather). Energy depends on both the gun and the production result (because it needs to know how much water is moving to estimate pump power).

This explains a behavior that may seem counterintuitive: **you can have high production with poor quality** if the gun has high pressure but the weather is marginal. Production and quality are independent axes.

## 7. Parameters by gun type

Before seeing the numbers, a terminology clarification: the snow industry has two different classifications of guns, and it’s best not to mix them.

- **Fan gun vs. lance (lance/stick)** classifies **how the water is projected**: with a fan, or using the height of a static tower.
- **Mono-fluid vs. bi-fluid** classifies **how the water is atomized**: only by water pressure, or by mixing it with compressed air in the nozzle.

These are independent axes — in reality there are mono-fluid fan guns, bi-fluid fan guns, mono-fluid lances, and bi-fluid lances. This simulator models only the **mono-fluid / bi-fluid** axis (`GunType` in the code), because that is what determines the `minimum_wet_bulb` — the minimum weather threshold to operate each system:

| Parameter | Mono-fluid | Bi-fluid |
|---|---|---|
| Nozzles | 6 | 4 |
| Height | 12 m | 8 m |
| Water pressure | 20–40 bar | 5–10 bar |
| Air pressure | None | 4–7 bar |
| Minimum wet bulb to operate | −2.5°C | −0.5°C |

The bi-fluid can operate in less demanding weather conditions (−0.5°C vs. −2.5°C) because compressed air expansion provides additional cooling during nucleation, without relying as much on ambient air evaporating and cooling the water. In exchange, it consumes extra compressor energy that the mono-fluid does not.

> If the project ever wanted to model the fan gun / lance axis as well (for example, to vary reach or snow distribution on the terrain), it would be a second `enum` independent of `GunType`, not an extension of it — they are two distinct dimensions of the gun, not a hierarchy.

## References

- Stull, R. (2011). *Wet-Bulb Temperature from Relative Humidity and Air Temperature*. Journal of Applied Meteorology and Climatology.
- Lavanchy & Brun (2002). *Guns and Snow*.
- Fierz et al. (2009). *International Classification for Seasonal Snow*.
- TechnoAlpin technical specifications.

---

Interested in how this is implemented in code (folders, classes, stack)? Go to **Technical**.
