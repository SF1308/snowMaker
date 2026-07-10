# Introduction to snowmaking

**Snowmaking** is the process of producing snow using water and favorable weather conditions.

Although it is commonly called "artificial snow," it is actually made of frozen water, just like natural snow. The difference lies in **how it forms**.

While natural snow forms inside clouds through atmospheric processes, manufactured snow is produced by spraying water into very small droplets using guns or lances. During their flight through the air, those droplets lose heat, freeze, and land on the ground as snow.

Today, snowmaking is a key tool for most ski resorts around the world.

---

# Why make snow?

The amount of natural snow depends entirely on the weather conditions each winter.

In seasons with low precipitation, warm temperatures, or early thawing, many pistes cannot open or must close early.

Snowmaking reduces that dependence on weather and offers several benefits:

* Guaranteeing season opening.
* Keeping pistes in good condition throughout winter.
* Repairing heavily used or worn areas.
* Extending the ski season.
* Improving piste safety and quality.

It is important to note that, in most cases, manufactured snow **complements** natural snow rather than replacing it.

---

# How is snow made?

The process can be summarized in four stages:

1. Water is taken from a reservoir, lake, or storage system.
2. The water is pressurized and sent to a snow gun or lance.
3. The equipment sprays the water as millions of tiny droplets.
4. If the weather conditions are right, those droplets freeze before reaching the ground and form snow.

Although the process looks simple, snow quality depends on many environmental factors and the type of equipment used.

---

# Basic principles of snowmaking

Although different types of equipment exist, all snowmaking systems rely on two fundamental processes: **atomization** and **nucleation**.

## Atomization

Atomization transforms a continuous stream of water into millions of tiny droplets.

The smaller the droplets:

* the greater their surface area in contact with the air;
* the faster they lose heat;
* the more likely they are to freeze before reaching the ground.

Atomization quality depends on equipment design, water pressure, and in some systems, the use of compressed air.

---

## Nucleation

A water droplet does not become an ice crystal instantly. To start the process, it needs an **ice nucleus** — a tiny particle around which ice can form.

In nature, these nuclei are usually small particles in the atmosphere, like dust or aerosols.

In snowmaking systems, some equipment deliberately generates small ice particles during spraying. These particles act as nuclei over which the remaining droplets can freeze more easily, improving production efficiency, especially when the weather is less favorable.

---

## Flight time

Once atomized and nucleated, droplets travel several meters before reaching the ground.

During that time, they exchange heat with the air and continue freezing.

For this reason, the gun’s throw distance, droplet size, and weather conditions directly affect the amount and quality of snow produced.

In general terms, the goal of any snowmaking system is to ensure that as many droplets as possible finish freezing before impacting the ground.

---

# What conditions are needed?

Lower-than-freezing air temperature alone is not enough to make snow.

The most important factors are:

* Air temperature.
* Relative humidity.
* Wind.
* Water quality and availability.
* Type of gun used.

Of all these, the most important parameter is **wet bulb temperature**, because it combines the effects of air temperature and humidity.

---

# What is wet bulb temperature?

**Wet bulb temperature (Tw)** represents the air’s ability to cool water through evaporation.

When a snow gun sprays water, a small portion of the droplets evaporates. That evaporation consumes energy and cools the remaining droplets.

The drier the air, the greater that cooling effect and the easier it is for droplets to freeze before reaching the ground.

For that reason, two days with the same air temperature can have completely different outcomes:

* A cold, dry day is usually ideal for making snow.
* A cold but very humid day may prevent production.

That is why the snowmaking industry uses **wet bulb** as the main reference instead of air temperature.

---

# When can snow be made?

In simplified terms, there are three scenarios:

| Condition      | Wet bulb             | Expected result                         |
| ----------- | --------------------- | ---------------------------------------- |
| ❌ Impossible | Above -2 °C         | No quality snow forms.                   |
| ⚠️ Marginal | Between -5 °C and -2 °C | Wet, heavy snow may be produced.         |
| ✅ Optimal    | Equal or below -5 °C | Dry, high-quality snow is produced.      |

These values are approximate and may vary depending on the equipment type and location-specific conditions.

---

# Types of equipment

When talking about snow guns, there are actually **two different questions** you should not mix, because each describes a different aspect of the equipment.

## How is the water projected?

* **Fan guns:** use a large fan to project water over a long distance. They are the most common equipment in large ski resorts due to their high production capacity.
* **Snow lances:** are tall static structures without a fan that spray water from a series of nozzles. They use tower height to give droplets flight time. Their energy use is usually lower, although they typically produce less snow per unit than a fan gun.

## How is the water atomized?

* **Mono-fluid:** the water is atomized using only water pressure, without compressed air.
* **Bi-fluid:** the water is mixed with compressed air in the nozzle. The air expansion generates additional cooling that helps form the first ice nuclei, allowing operation in somewhat less favorable conditions (higher wet bulb) than a mono-fluid system.

These two axes are independent: a fan gun can be mono-fluid or bi-fluid, and a lance can be either as well. This simulator models specifically the mono-fluid/bi-fluid axis, because it determines the minimum weather conditions required to operate each system.

---

# Is manufactured snow different?

Yes.

Although both are made of frozen water, manufactured snow usually has:

* smaller crystals;
* higher density;
* greater resistance to wear;
* better performance under skier traffic.

These characteristics help keep pistes in good condition longer.

---

# Environmental impact

Snowmaking requires water and energy, so it must be planned and managed responsibly.

The main aspects to consider are:

* water consumption;
* electricity consumption;
* water capture, pumping, and distribution infrastructure;
* temporary changes during thaw.

It is important to clarify that **manufactured snow does not contain chemicals or additives**. Under normal conditions, the process simply sprays **water** and, depending on the equipment, mixes it with **compressed air** to help create small droplets. Both components already exist in the environment and do not introduce pollutants into the snow.

When the system is properly designed and operated, the water used is not lost. It remains stored as snow during the winter and, as it melts, returns to the hydrological cycle, feeding streams, rivers, lakes, or aquifers just like natural snow.

The main environmental impact of snowmaking is associated with energy consumption and responsible water resource management. That is why modern ski resorts use monitoring systems, reservoirs, and regulated extraction plans to minimize impacts on the surroundings.

In many countries where snowmaking is widely developed, water capture and system operation are subject to environmental regulations and controls to ensure sustainable resource use.

---

# What does this project simulate?

This project has an **educational** purpose.

Its goal is to show how different variables influence snow production, including:

* air temperature;
* relative humidity;
* wet bulb temperature;
* gun type;
* water pressure;
* energy consumption;
* estimated snow quality.

The models used are simplified approximations that help understand the general behavior of snowmaking.

They do not replace professional tools used by ski resorts for daily operation of their snowmaking systems.

---

Want to know exactly how these conditions are calculated (formulas, parameters, thresholds)? Go to **Architecture**. Are you a developer interested in how the project is built? Go to **Technical**.
