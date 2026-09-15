# Thermal and Fluid Systems

Use this reference when a mechatronic design must move heat or fluid: cooling electronics, motors or batteries; sizing pumps, fans, pipes or pneumatic lines; or building thermal models for control. Each method below states its assumptions and when it applies — checking those assumptions **is** the engineering. For deriving low-order thermal models as block diagrams from energy balances, see [system builder](system-builder.md). Runnable versions of the calculations here are in `scripts/thermal_fluid_calcs.py` (Python standard library; each function documents its assumptions and units).

## Units and conventions that prevent wrong answers

**Kelvin vs Celsius.** A temperature *difference* of 1 K equals 1 °C, so conduction and convection equations (which use ΔT) accept either. Radiation and ideal-gas equations use *absolute* temperature: convert with T[K] = T[°C] + 273.15. Using 25 instead of 298.15 in T⁴ is a classic silent error.

**Gauge vs absolute pressure.** Gauge pressure is measured relative to local atmosphere; absolute is relative to vacuum: p_abs = p_gauge + p_atm (≈ 101.325 kPa at sea level). Pipe-loss and pump-head calculations use pressure *differences*, so gauge is fine. Ideal-gas density, compressed-air energy, choked-flow and cavitation (NPSH) calculations need absolute pressure. A "0 bar" gauge reading on an air receiver still means ~1 bar absolute inside.

Work in SI throughout (Pa, K, W, kg/m³, Pa·s) and convert at interfaces. Distinguish dynamic viscosity μ (Pa·s) from kinematic ν = μ/ρ (m²/s).

## Thermodynamics: the accounting rules

**First law (control volume, steady flow):** for a device with one inlet and outlet,

Q̇ − Ẇ = ṁ (h₂ − h₁ + (V₂² − V₁²)/2 + g(z₂ − z₁)) [W]

Q̇ is heat in, Ẇ is shaft work out, ṁ mass flow (kg/s), h **enthalpy** (J/kg) — internal energy plus flow work pv, the natural energy currency for flowing fluids. Draw the control volume boundary first; every term is defined by what crosses it. Use this to budget any thermal system before detailed design: a 100 W processor in a sealed box *must* reject 100 W through the walls at steady state, regardless of internal fans.

**Second law:** heat flows spontaneously from hot to cold; every real process generates entropy. Practical consequences: a heat engine's efficiency η = W/Q_in is bounded by the Carnot limit 1 − T_cold/T_hot (absolute temperatures); a refrigerator or heat pump is rated by **COP** = useful heat moved ÷ work input, which can exceed 1 because it moves heat rather than converting work directly into heat. COP depends on the temperature lift, operating point and technology; it is not guaranteed above 1 for cooling. For example, a cooling COP of 3 means 3 W removed per watt of work, while the hot side rejects 4 W. Compare thermoelectric and vapour-compression systems at the required temperatures and load. Never accept a claimed efficiency without asking "of what, between which temperatures."

## Heat transfer: three mechanisms, one resistance network

**Conduction (Fourier's law):** q = −k A dT/dx; through a slab, Q̇ = kA ΔT / L. Thermal conductivity k [W/(m·K)] depends on material, temperature and construction. Composites and PCBs can be **anisotropic**: conductivity differs by direction. Use measured/vendor directional properties or a tensor/layered model reflecting the actual copper layup and interfaces.

**Thermal resistance** R = ΔT/Q̇ [K/W] lets you treat heat paths like electrical circuits: series resistances add, parallel paths combine as reciprocals. Include often-dominant terms novices miss: **contact resistance** at imperfect joints (mitigated by thermal interface material — use the vendor's measured resistance at your clamping pressure, not the bulk k) and **spreading resistance** when a small heat source feeds a large plate (a 10 mm chip on a 100 mm heatsink does not use the full base area; use a spreading correlation or FEA).

**Convection:** Q̇ = h A (T_surface − T_fluid), with coefficient h [W/(m²·K)] found from correlations built on dimensionless groups:

- **Reynolds** Re = ρVL/μ — inertia vs viscosity; selects laminar vs turbulent.
- **Prandtl** Pr = μc_p/k — momentum vs thermal diffusion (air ≈ 0.7, water ≈ 7).
- **Nusselt** Nu = hL/k_fluid — the answer; correlations give Nu = f(Re, Pr) for *forced* convection or Nu = f(Ra, Pr) for *natural* (buoyancy-driven) convection.

Each correlation is valid only for its stated geometry, Re/Ra range and boundary condition — cite which one you used and its range. Do not pick h solely from the words “air” or “water”; geometry, flow, properties and thermal boundary conditions determine it.

**Radiation:** Q̇ = εσA(T₁⁴ − T₂⁴) with σ = 5.670×10⁻⁸ W/(m²·K⁴), emissivity ε (0–1), temperatures in **kelvin**. This form describes a diffuse-grey surface exchanging with a large isothermal black surrounding under the stated assumptions. For multiple finite surfaces, use **view factors** (fraction of leaving radiation reaching another surface) and emissivity/radiosity equations to account for reflections. Estimate radiation alongside convection; vacuum suppresses convection, while conduction through mounts can remain substantial.

**Lumped capacitance:** if internal conduction is much faster than surface convection — checked by **Biot number** Bi = hL_c/k_solid ≲ 0.1 as a common screening criterion (L_c = volume/area) — the body has one temperature obeying

C dT/dt = P − UA (T − T_amb), τ = C/UA [s]

with heat capacity C = mc_p [J/K] and overall conductance UA [W/K]. This first-order approximation can describe a dominant thermal mode; windings, cells and enclosure air may require separate coupled thermal nodes to capture hot spots, and maps directly onto a gain-plus-time-constant block in the [system builder](system-builder.md). You cannot assert Bi < 0.1 without geometry and conductivity — state it as an assumption to verify.

**Heat exchangers:** with both terminal temperatures known, use **LMTD**: Q̇ = F UA·ΔT_lm with a configuration correction F where required, and ΔT_lm = (ΔT₁ − ΔT₂)/ln(ΔT₁/ΔT₂). When outlet temperatures are unknown (the usual design case), use **ε–NTU**: NTU = UA/C_min, effectiveness ε = Q̇/Q̇_max from charts or formulas per flow arrangement, Q̇_max = C_min(T_hot,in − T_cold,in). Compare arrangements at the same inlet conditions, heat-capacity rates and UA; counterflow generally improves effectiveness, with limiting cases where they coincide. Use the equal-terminal-difference limit when the LMTD expression becomes 0/0.

### Cooling requirements by application

- **Electronics:** requirement is junction temperature, not case: T_j = T_amb + P·(R_jc + R_interface + R_sink-amb) for a justified single series heat path, below the applicable limit at the worst-case environment. Board conduction and parallel paths can require a network; datasheet thermal metrics from one test board do not universally describe another assembly.
- **Motors:** verify winding, magnet, bearing and encoder temperature limits for the actual motor. Copper loss is I²R with temperature-dependent R; iron, drive and mechanical losses also matter. Continuous torque needs a duty/cooling model and measurements, with enough thermal nodes to capture the limiting hot spot.
- **Batteries:** use the actual cell chemistry and manufacturer charge/discharge/storage temperature-current envelope; a generic “lithium-ion” range is not sufficient. Design for cell-to-cell uniformity, BMS sensing and fault response. Evaluate **thermal runaway**, propagation and venting under the relevant failure scenario; temperature or voltage monitoring alone does not guarantee early detection or containment.
- **Environment:** cooling below the local **dew point** condenses water onto electronics. Compute dew point from worst-case humidity; select an appropriate combination of enclosure sealing/dry air, insulation, drainage, heaters or dew-point tracking, and validate it. Conformal coating alone does not eliminate condensation or protect every connector.

## Fluid mechanics: from conservation to pipe sizing

**Reynolds transport theorem** converts "follow the particles" laws into control-volume statements: the rate of change inside the volume plus the net flux out equals the source. From it: **mass conservation**: storage rate = mass inflow − mass outflow. For steady incompressible flow with no accumulation, ΣQ_in = ΣQ_out; for a filling constant-area tank, A dh/dt = Q_in − Q_out. The momentum balance includes unsteady storage and momentum flux plus pressure, gravity and wall forces; ṁ(V_out−V_in) is only the steady flux contribution, not automatically the complete pipe-anchor force.

**Navier–Stokes** (incompressible Newtonian fluid with constant density and viscosity, vector form; also require ∇·V = 0):

ρ(∂**V**/∂t + (**V**·∇)**V**) = −∇p + μ∇²**V** + ρ**g**

Read it as ma = pressure force + viscous force + gravity per unit volume. You will rarely solve it by hand; you *will* rely on its exact solutions (Poiseuille pipe flow), its dimensionless scaling (Re, Mach), and CFD, which solves it numerically.

**Flow regimes:** in pipes, laminar below Re ≈ 2300, transitional to ~4000, turbulent above; the transition band is unreliable — avoid designing in it. **Compressibility** matters when Mach = V/c exceeds ~0.3 (air: c ≈ 343 m/s at 20 °C); a low Mach number alone does not justify constant density if pressure or temperature changes appreciably through a gas system. Check both speed and the expected density variation; long pneumatic lines can need compressible models even at low local Mach number. **Multiphase** flow (cavitation bubbles, condensate in air lines, boiling coolant) invalidates single-phase correlations — flag it and use dedicated methods.

**Bernoulli** (p/ρ + V²/2 + gz = const) in this form applies along a streamline in steady, incompressible, inviscid flow with gravity as the relevant body force and no machines. An engineering energy balance adds pump/loss terms; include turbine head and kinetic-energy correction factors when relevant:

p₁/ρg + V₁²/2g + z₁ + h_pump = p₂/ρg + V₂²/2g + z₂ + h_loss [m of head]

**Pipe losses:** major loss h_loss = f (L/D)(V²/2g) with the **Darcy** friction factor f. Laminar: f = 64/Re (exact). Turbulent: Colebrook or Haaland from Re and relative roughness ε/D (Moody chart). Beware the **Fanning** factor used in chemical-engineering texts: f_Darcy = 4·f_Fanning — check which convention a source uses before trusting its number. **Minor losses** from fittings use h = K V²/2g with tabulated K per fitting; in short runs with many elbows and valves they dominate.

**Hydrostatics and immersed bodies:** pressure grows with depth as p = ρgh (5 m of water ≈ 49 kPa gauge — sizes underwater housings). Buoyancy = ρ_fluid·g·V_displaced. Drag F = ½ρV²C_dA and lift F = ½ρV²C_lA, with coefficients that depend on shape *and* Re — quote the Re at which your C_d applies.

## Pumps, fans and fluid power

A typical centrifugal pump/fan has a head-versus-flow **curve**; the system demands static head plus flow-dependent losses. Turbulent losses often vary approximately with flow squared over a useful range, while laminar losses are linear in flow. Positive-displacement machines and nonmonotonic curves require their actual operating characteristics. The machine runs where they intersect — change either curve to change the flow. Hydraulic power P = ρgQH; shaft input P/η.

**Affinity rules** for speed change on the same impeller: Q ∝ N, H ∝ N², P ∝ N³ — excellent for modest speed ratios, degrading for large changes because efficiency shifts; never extrapolate far or across different impellers.

**NPSH and cavitation:** if absolute pressure at the impeller eye falls below vapor pressure, bubbles form and collapse, eroding metal. Require NPSH_available (from *absolute* suction pressure, elevation, losses, vapor pressure) > NPSH_required (vendor curve) with margin, at the hottest fluid temperature (vapor pressure rises steeply with temperature).

**Pneumatics:** flow through a valve or orifice **chokes** when downstream/upstream absolute pressure ratio falls below the critical ratio (2/(γ+1))^(γ/(γ−1)), about 0.528 for ideal air with γ=1.4 in the ideal isentropic nozzle model. Real valves need their rated compressible-flow data. At fixed upstream stagnation conditions, further lowering downstream pressure does not increase the ideal choked mass flow — size valves by their flow coefficient at your actual pressures. **Hydraulic fluid power** (P = p·Q) delivers high force density; select valves by rated flow and pressure, use **accumulators** to absorb transients and store energy, and manage **water hammer** — fast valve closure in liquid lines produces pressure spikes Δp = ρcΔV (using an illustrative wave speed c = 1400 m/s and ΔV = 2 m/s gives 2.8 MPa ≈ 28 bar at ρ = 1000 kg/m³; actual c depends on pipe compliance, constraints and entrained gas, and the closure time relative to wave travel matters) — mitigated by slower actuation or accumulators.

## Worked example 1 — enclosure heater (lumped thermal)

An electronics box: C = 500 J/K, UA = 5 W/K to ambient at 25 °C, internal dissipation P = 50 W switching on at t = 0 with T(0) = 25 °C. Assumptions: lumped (Bi < 0.1 must be verified once geometry and k are known — do not assert it), constant properties, constant ambient.

- Time constant τ = C/UA = 500/5 = **100 s**.
- Steady-state rise ΔT_ss = P/UA = 50/5 = 10 K → **T_ss = 35 °C**.
- T(t) = 25 + 10(1 − e^(−t/100)). At t = 100 s: 25 + 10(1 − e⁻¹) = **31.3212056 °C**. At t = 30 s: 25 + 10(1 − e⁻⁰·³) = **27.5918178 °C**.

*Browser implementation:* in the [system builder](system-builder.md), model this as a first-order block with gain 1/UA = 0.2 K/W and τ = 100 s; its output is the temperature **rise**, so add the 25 °C ambient at a summing junction for absolute temperature. If the editor's run duration is capped at 60 s, verify against the 30 s value above rather than the 100 s one. Reproduce numerically with `lumped_temperature()` in `scripts/thermal_fluid_calcs.py`.

## Worked example 2 — pipe flow and pump power

Water (ρ = 1000 kg/m³, μ = 0.001 Pa·s) in a smooth pipe, D = 0.01 m, L = 2 m, Q = 1×10⁻⁵ m³/s. Assumptions: fully developed, isothermal; no entrance length or fittings counted.

- Area A = πD²/4 = 7.854×10⁻⁵ m²; V = Q/A = 0.12732 m/s.
- Re = ρVD/μ = 1000 × 0.12732 × 0.01 / 0.001 = **1273.2395** → laminar (< 2300), so f = 64/Re = 0.050265.
- Δp = f (L/D)(ρV²/2) = 0.050265 × 200 × 8.1057 = **81.4873 Pa**. Cross-check via Hagen–Poiseuille Δp = 128 μLQ/(πD⁴) = 81.4873 Pa — agreement confirms both.

This friction drop alone **cannot size the final pump**: a real system adds static lift, fittings, entrance effects, filter/heat-exchanger drops and margin, all evaluated at the operating point against a vendor curve.

*Pump power illustration (separate duty):* delivering Q = 0.001 m³/s against H = 1 m of water at η = 0.6: hydraulic power ρgQH = 1000 × 9.81 × 0.001 × 1 = 9.81 W; using g = 9.81 m/s² explicitly, input power = 9.81/0.6 = **16.35 W**. Both examples are in `scripts/thermal_fluid_calcs.py` (`pipe_pressure_loss()`, `pump_power()`).

## Simulation: CFD, conjugate heat transfer and checks

Use hand correlations first; escalate to CFD when geometry defeats them. **Conjugate heat transfer** solves solid conduction and fluid convection together — needed for heatsinks and cold plates. Key controls: **turbulence model** (k-ω SST is a common general choice; each model has documented validity limits), **mesh** resolution — check the near-wall **y+** matches the wall treatment (y+ ≈ 1 for resolved boundary layers; 30–300 for wall functions), **boundary conditions** that reflect the actual controlled wall, heat flux or coupled thermal path, and time step for transients (Courant number near 1 as a starting point). Mandatory checks: energy/mass balances close across the domain, mesh-refinement convergence, and comparison against a correlation or measurement — a numerical prediction still requires physical validation for its intended use. Values such as y+ or Courant number are solver/model-dependent design choices, not universal pass criteria. The browser tools in this skill run low-order models and visualisations, **not** CFD. When selecting CFD/FEA software, verify current versions, licensing and solver capabilities against the vendor's current documentation at decision time; do not rely on remembered feature lists or roadmap promises, and confirm installation requirements on the target machine.

## Delivering a cooling or fluid system

**Staged validation:** (1) analytical budget and resistance network with stated assumptions; (2) low-order simulation of transients and control; (3) CFD only where correlations fail, with the checks above; (4) bench test of the thermal path at controlled power and ambient — measured temperatures vs prediction, instrument accuracy stated; (5) environmental test at worst-case ambient, humidity and duty; (6) fault trials (fan failure, pump loss, blocked filter) with the safe state demonstrated. Label every figure by its evidence status (calculated / simulated / bench-tested).

**Production and configuration deliverables:** coolant specification and fill/bleed procedure; fan/pump part numbers with curves and derating; TIM type, thickness and clamping torque; assembly and leak-test instructions with pass criteria; sensor placement and calibration; versioned controller configuration (setpoints, fan curves, alarm and shutdown thresholds); acceptance test procedure; and a maintenance schedule (filter, coolant, fan-bearing life).

**Hazards — match precautions to what is actually present:** hot surfaces and fluids (risk depends on temperature, contact duration, material and exposure); stored pressure in receivers, accumulators and heated sealed loops (thermal expansion needs relief provision); battery faults (runaway propagation, venting gases); glycol coolant handling; condensation onto live circuits. Specify safe states and test limits as requirements. Nothing here constitutes a certification claim — pressure equipment, battery systems and safety functions have their own regulatory pathways to be confirmed against current requirements for the target market.

## Sources

Introductory teaching material — useful for concepts and derivations, **not** for device ratings, current standards or legal requirements:

- [MIT OCW 2.051 Introduction to Heat Transfer](https://ocw.mit.edu/courses/2-051-introduction-to-heat-transfer-fall-2015/) — conduction, convection, radiation, fins, transient methods.
- [MIT OCW 16.050 Thermal Energy](https://ocw.mit.edu/courses/16-050-thermal-energy-fall-2002/pages/syllabus/) — thermodynamic cycles, first/second law.
- [NASA Beginner's Guide: Navier–Stokes](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/navier-strokes-equation/) and [Bernoulli's equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/bernoullis-equation/) — governing equations and their restrictions.
- [DOE Fundamentals Handbook: Thermodynamics, Heat Transfer and Fluid Flow (DOE-HDBK-1012/3-92)](https://www.energy.gov/ehss/articles/doe-hdbk-10123-92) — pipe flow, pumps, two-phase basics.
- [DOE pump systems reference](https://www.energy.gov/sites/prod/files/2014/05/f16/pump.pdf) — pump curves, system curves, efficiency.

For component selection, always use the manufacturer's current datasheet and curves at your actual operating conditions.
