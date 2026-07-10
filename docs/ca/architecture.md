# Architecture: com calcula el simulador

Aquí hi ha el detall de quina fórmula usa cada pas del càlcul, amb quins paràmetres i en quin ordre el motor (`SnowEngine`) els encadena.

## 1. Bulb humit — fórmula de Stull (2011)

El simulador no fa servir taules psicromètriques ni necessita pressió atmosfèrica: aproxima el bulb humit (Tw) directament a partir de la temperatura seca (T, °C) i la humitat relativa (RH, %) amb la fórmula empírica de Stull:

```
Tw = T·atan(0.151977·√(RH + 8.313659))
   + atan(T + RH)
   − atan(RH − 1.676331)
   + 0.00391838·RH^1.5·atan(0.023101·RH)
   − 4.686035
```

És un ajust per regressió, no una derivació física — funciona bé en intervals meteorològics normals, però perd precisió en extrems (RH proper a 0% o 100%, temperatures molt extremes). Tampoc corregeix per altitud: es va calibrar a pressió atmosfèrica estàndard a nivell del mar, així que a pistes d’esquí d’alta muntanya introdueix un marge d’error que avui el simulador no compensa.

Aquest valor de Tw és l’entrada principal de gairebé tot el que segueix.

## 2. Llindars de viabilitat

A partir de Tw, es decideix si es pot operar i en quin règim:

| Bulb humit (Tw) | Zona | Es pot fabricar neu? | Resultat esperat |
|---|---|---|---|
| Tw > −2°C | `impossible` | No | — |
| −5°C < Tw ≤ −2°C | `marginal` | Sí | Neu humida i pesada, rendiment reduït |
| Tw ≤ −5°C | `optimal` | Sí | Neu seca, alta qualitat |

Aquests llindars són estàndards de la indústria, no específics d’un fabricant — representen el punt en què l’evaporació ja no compensa prou com per congelar bé les gotes a l’aire.

## 3. Producció de neu

La producció depèn del cabal d’aigua, que al seu torn depèn de la pressió i de la quantitat de boquilles del canó:

```
Q (L/min) = K × nozzles × √(pressió en bar)
```

on `K = 2.8` és un coeficient empíric (litres per minut per boquilla a 1 bar de referència).

A partir d’aquí:

- **Volum de neu per hora:** s’assumeix que 1 L d’aigua produeix ~3 L de neu compactada (`WATER_TO_SNOW_VOLUME = 3.0`).
- **Massa de neu per hora:** el volum es multiplica per una densitat típica de neu artificial de **350 kg/m³**.

Fixeu-vos que aquesta part del càlcul depèn del **canó** (boquilles, pressió), no directament del clima — és a dir, un dia molt fred no produeix automàticament més neu; produeix **millor qualitat** de neu, però el volum depèn de quanta aigua s’està bombejant.

## 4. Qualitat de la neu

Aquí sí que torna a entrar Tw. La lògica és: com més fred és el bulb humit, més petits són els cristalls de gel formats i més densa/compacta resulta la neu:

```
grain_mm  ≈ 0.8 − 0.06 × |Tw|     (acotat entre 0.2 i 0.8 mm)
density   ≈ 280 + 12 × |Tw|       (acotat entre 280 i 450 kg/m³)
```

I el grau de qualitat s’assigna directament pels mateixos llindars de viabilitat:

| Grau | Condició | Descripció |
|---|---|---|
| **A** | Tw ≤ −5°C | Neu seca, cristalls fins, alta densitat |
| **B** | −5°C < Tw ≤ −2°C | Neu humida, cristalls mitjans |
| **C** | Tw > −2°C (zona marginal) | Neu marginal |

## 5. Consum energètic

Es modelen dos consums independents:

**Bomba d’aigua** (sempre present):
```
P_pump = (Q_aigua × ΔP) / η_bomba,   η_bomba = 0.75
```
on `Q_aigua` és el cabal en m³/s i `ΔP` és la pressió de treball en Pa.

**Compressor d’aire** (només en canons bi-fluid, que fan servir aire comprimit):
```
P_comp = (Q_aire × P_aire) / η_comp,   η_comp = 0.70
```
on el cabal d’aire s’aproxima com `0.06 m³/s per cada bar de pressió d’aire`.

La suma d’ambdós dóna la potència total, i també es calcula una intensitat energètica (`kWh per m³ de neu produïda`) per comparar l’eficiència entre configuracions.

## 6. Com el SnowEngine encadena tot

L’ordre importa perquè hi ha dependències entre passos. El motor segueix aquesta seqüència:

```
1. Clima (T, RH) ────────────► bulb humit (Tw)
2. Tw ────────────────────────► viabilitat (es pot operar?)
3. Canó (boquilles, pressió) ► producció (cabal, volum, massa)
4. Tw ────────────────────────► qualitat (gra, densitat, grau)
5. Canó + producció ────────► energia (potència, intensitat)
```

És a dir: **Tw es calcula una sola vegada** i alimenta tant la viabilitat com la qualitat. La producció depèn únicament del canó (no del clima). I l’energia depèn tant del canó com del resultat de la producció (perquè cal saber quanta aigua s’està movent per estimar la potència de bombeig).

Això explica un comportament que pot semblar contraintuïtiu: **pots tenir alta producció amb mala qualitat**, si el canó té molta pressió però el clima està en zona marginal. Producció i qualitat són eixos independents.

## 7. Paràmetres per tipus de canó

Abans de veure els números, una aclaració de terminologia: en la indústria hi ha dues classificacions diferents de canons de neu, i convé no barrejar-les.

- **Fan gun vs. llança (lance/stick)** classifica **com es projecta** l’aigua: amb ventilador, o aprofitant l’altura d’una torre estàtica.
- **Mono-fluid vs. bi-fluid** classifica **com s’atomitza** l’aigua: només amb pressió d’aigua, o barrejant-la amb aire comprimit a la boquilla.

Són eixos independents — en la realitat existeixen fan guns mono-fluids, fan guns bi-fluids, llançes mono-fluids i llançes bi-fluids. Aquest simulador modela únicament l’eix **mono-fluid / bi-fluid** (`GunType` en el codi), perquè és el que determina el `minimum_wet_bulb` — el llindar climàtic mínim per operar cada sistema:

| Paràmetre | Mono-fluid | Bi-fluid |
|---|---|---|
| Boquilles | 6 | 4 |
| Alçada | 12 m | 8 m |
| Pressió d’aigua | 20–40 bar | 5–10 bar |
| Pressió d’aire | No en fa servir | 4–7 bar |
| Bulb humit mínim per operar | −2.5°C | −0.5°C |

El bi-fluid pot operar amb condicions climàtiques menys exigents (−0.5°C vs. −2.5°C) perquè l’expansió de l’aire comprimit genera un refredament addicional en el moment de la nucleació, sense dependre tant de l’aire ambient per evaporar i refredar l’aigua per si sol. A canvi, consumeix energia extra al compressor que el mono-fluid no necessita.

> Si en algun moment el projecte volgués modelar també l’eix fan gun / llança (per exemple, per variar l’abast o la distribució de la neu al terreny), seria un segon `enum` independent de `GunType`, no una extensió del mateix — són dues dimensions diferents del canó, no una jerarquia.

## Referències

- Stull, R. (2011). *Wet-Bulb Temperature from Relative Humidity and Air Temperature*. Journal of Applied Meteorology and Climatology.
- Lavanchy & Brun (2002). *Guns and Snow*.
- Fierz et al. (2009). *International Classification for Seasonal Snow*.
- Especificacions tècniques TechnoAlpin.

---

Et interessa com està implementat això en codi (carpetes, classes, stack)? Ves a **Technical**.
