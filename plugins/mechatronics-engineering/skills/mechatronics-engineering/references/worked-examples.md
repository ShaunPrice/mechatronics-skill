# Original worked examples

All numbers here are assumed educational inputs unless stated otherwise. They demonstrate an engineering workflow and reproducible calculations, not a manufacturing release or physical validation of a particular machine.

## A. Position an inspection carriage

**Need:** move a horizontal carriage to 0.1 m and reject a −1 N load disturbance. Begin with a lumped plant m = 1 kg, b = 2 N·s/m, k = 20 N/m. Coordinate x is displacement from spring equilibrium. Equation: ẍ = (u + d − 2ẋ − 20x)/1. Its undamped natural frequency is √20 = 4.472 rad/s = 0.712 Hz; damping ratio is 2/(2√20) = 0.224. Expect underdamped open-loop behaviour.

**Controller:** sampled parallel PID with Kp = 80 N/m, Ki = 40 N/(m·s), Kd = 12 N·s/m, derivative-on-measurement filtered with 0.02 s time constant, conditional antiwindup and ±10 N actuator limit. Sample period 0.01 s; RK4 plant step 0.001 s. Reference steps at 0.5 s; disturbance begins at 4 s. These gains belong to this model only.

**Run from the skill folder:**

```sh
python3 scripts/control_lab.py --out run-results
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Open `run-results/control-lab.html`; use the legends to compare reference, closed-loop and open-loop baseline. For live editable 2D/3D and frequency/pole experiments, open [the browser workbench](../assets/browser-lab/index.html). Its parameters and discretisation are shown in that app; compare like-for-like settings before comparing numerical results.

**Observed from the bundled Python run:** at 8 s, closed-loop error ≈ 0.002728 m versus open-loop error ≈ 0.050093 m; maximum command 8.04 N; no saturation in this nominal run. Halving the plant step from 0.002 s to 0.001 s changed position by less than 10⁻⁸ m in the included test. This is simulation/software evidence. The run does not establish a 2 mm accuracy requirement or real actuator suitability; the 8 s residual is still about 2.73 mm.

**Next design work:** measure carriage friction/stiffness, mass, actuator force-current relation, supply/thermal limits, sensor delay/noise, backlash and guide alignment. Add relevant nonlinearities and run load/delay/noise sweeps. Manufacturing handoff needs carriage/rail drawings and datums, fasteners, actuator/encoder interface, travel limits, wiring, firmware/configuration and calibrated acceptance tests. Do not copy this model's gains to a real axis without those inputs.

## B. Size a small wheeled robot

Assume a 20 kg robot, four equally loaded driven wheels, radius 0.1 m, desired uphill acceleration 0.5 m/s², grade 5°, rolling coefficient 0.02, transmission efficiency 0.8 and traction coefficient 0.6. Ignore aerodynamic drag.

F = m a + m g sin θ + Crr m g cos θ ≈ 31.002 N. Wheel torque per wheel is F r/4 ≈ 0.775 N·m. At a 1:1 transmission, input torque including assumed efficiency is ≈ 0.969 N·m per wheel; for reduction G, motor torque is approximately 0.969/G with motor speed multiplied by G. Traction bound μ m g cos θ ≈ 117.232 N exceeds the required force in this simplified model.

Run `python3 scripts/engineering_calcs.py --demo` to reproduce. Next determine top speed/torque-speed curve, wheel load transfer, start/stall current, braking on slope, gearbox losses/backlash and mission heat/energy. Traction feasibility does not establish tip-over stability, stopping distance or rough-terrain performance. Use a route/duty simulation and then measured representative trials.

Deliver frame/wheel/gear mounting tolerances, ground clearance, cable protection, verified drive/encoder configuration, motion/current limits, watchdog and brake/fault policy, BOM/alternates, assembly instructions, calibration and a test plan for payload/grade/speed/temperature.

## C. Put a two-link arm at a point

Assume a planar revolute arm with link lengths 0.3 and 0.2 m and target (0.3, 0.2) m. Angles are relative joint rotations, positive counterclockwise, and q1 = 0 points along +x. The target is position-only; no tool orientation constraint is requested.

cos q2 = (x²+y²−l1²−l2²)/(2 l1 l2) = 0. Thus q2 = ±π/2. q1 = atan2(y,x) − atan2(l2 sin q2, l1+l2 cos q2) gives approximately (q1,q2) = (0,1.570796) or (1.176005,−1.570796) radians. The included helper returns both, and tests forward-kinematics reconstruction. A target 0.6 m from the base is unreachable because maximum reach is 0.5 m; choose new geometry, base location or task position rather than forcing a solver answer.

Choose the branch using joint limits, collision, cable routing and desired path continuity. Then time-parameterise the path and size torques using link/payload inertia and gravity. A 3D visualisation should show the correct frames and geometry; a model with prescribed angles is kinematic and does not establish motor performance. Manufacturing needs joint/bearing fits, link stiffness, hard stops, encoder datum/calibration, wiring through joints and an acceptance fixture.

## D. Check battery and screw arithmetic

A 100 N steady axial force with 5 mm/rev screw lead and assumed efficiency 0.9 requires about 0.08842 N·m input torque from Fp/(2πη), excluding bearing torque and inertia. Work consistency check: one revolution's input work times efficiency equals 100×0.005 = 0.5 J. Do not use this as a holding/braking specification.

A nominal 24 V/10 Ah pack, 80% usable fraction, 90% conversion efficiency and constant 60 W load gives 2.88 h. Check voltage sag, actual chemistry/discharge/charge limits, mission load, cold/hot conditions, ageing and BMS behaviour before claiming runtime or choosing charging hardware.

## E. Turn a prototype into a product

Use [the commercial worked scenario](commercial-delivery.md) and `contribution_model()` to connect per-start cost, yield, sold-unit support, net price and NRE. The base case has 180-unit contribution break-even; lower yield or price moves that threshold substantially. Pilot evidence must replace assumptions about assembly time, scrap, support and demand, with uncertainty visible. Connect the cost model to the actual manufacturing BOM and configuration baseline so an engineering change updates both technical and financial records.

## F. Prompts that exercise the skill

- “I know basic algebra. Help me stop a small wheeled robot accurately; explain encoders, odometry, closed-loop control and the tests before recommending components.”
- “Build me an offline browser simulation of this axis with editable mass, damping, gains and sample rate; show 2D/3D motion and live error/force charts.”
- “Show root locus, Bode and Nyquist for my loop; explain which model each uses and why a finite Nyquist curve may not prove stability.”
- “Design a submersible sensor platform for my mission. Compare tethered and autonomous approaches, then derive the pressure, buoyancy, energy and recovery requirements.”
- “Take this tested prototype toward 100 units. Produce the manufacturing/configuration handoff, cost sensitivities, quality plan and customer pilot.”
