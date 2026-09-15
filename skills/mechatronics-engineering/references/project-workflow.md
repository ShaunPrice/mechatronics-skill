# From problem to delivered system

Use this reference for substantial design, retrofit, build or product requests. Scale it to project size: a hobby fixture needs fewer records than an industrial robot, but both need clear interfaces and evidence. Use the [dossier template](../assets/project-dossier-template.md) as an editable handoff.

## 1. Discover and specify

Ask what work the system performs, who uses/maintains it, where and how often. Capture normal use, foreseeable misuse, environment, existing infrastructure, accessibility and operator workflow. Separate goals from constraints and assumptions. Ask the user to describe a successful cycle and a bad day. Obtain photos, dimensions, logs or device revisions only when they resolve a decision.

Translate wishes into requirements:

| Everyday request | Engineering requirement pattern | Evidence |
|---|---|---|
| “Put it exactly here” | Absolute position error ≤ X mm over workspace W, load L and temperature range T; report uncertainty | Calibrated independent metrology at representative positions |
| “Always goes back” | Bidirectional repeatability within X mm over N repeated cycles | Repeat runs from both directions; backlash and warm-up evaluated |
| “Move quickly” | Stroke S, cycle time C, peak speed/acceleration/jerk under load | Position/time log, no saturation or missed deadlines |
| “Run all day” | Duty cycle profile, ambient, runtime, lifetime cycles and service interval | Thermal soak and mission energy measurement |
| “Affordable” | Target unit cost at quantity, NRE limit and whole-life cost | Quotes, build time, yield and support assumptions |
| “Safe when it fails” | Explicit safe state for each credible fault, maximum stopping distance/time | Fault injection and independent stop verification |

Give every requirement an ID, rationale, units, conditions, threshold, verification method and owner. A high-resolution encoder does not prove end-effector accuracy. Avoid specifying precision tighter than process capability or measurement uncertainty supports.

## 2. Partition the system

Draw energy and information flows separately. Identify boundaries, environment, operator, service personnel and external systems. Partition mission planning, trajectory generation, fast control, power stage and independent protective functions. Place hard real-time duties where worst-case timing can be established.

Use an interface control table: producer/consumer; signal or load; units/frame; voltage and logic level; connector and pin; protocol; message fields; update rate; allowed delay/jitter; freshness rule; failure behaviour; power-up/default state; document revision. Include mechanical datums, mating surfaces, tolerances, thermal paths, sealing and cable bend radii.

Example: the planner sends a velocity command in m/s with monotonic timestamp; the MCU converts it using the verified wheel radius and gearbox ratio, rejects stale commands after a specified interval and applies bounded deceleration. “Stop on timeout” must explain what happens on a slope or when the drive loses power; a gravity load may need a brake and a controlled release sequence.

## 3. Compare concepts and close budgets

Compare two or three credible architectures only when the choice is meaningful. Eliminate concepts that cannot meet hard constraints before scoring preferences. A weighted matrix is a decision aid, not mathematical proof: state weights, evidence and sensitivity to uncertain scores.

Budget payload/mass/inertia; torque/force and acceleration; peak/continuous/RMS current; heat rejection; battery energy; stiffness/error; sensor uncertainty; bus bandwidth; compute/memory; latency; cost; production time. Assign reserve to uncertainty, then explain its basis; do not hide arbitrary safety factors. Recalculate coupled changes: a larger battery adds mass, affecting acceleration, motor heat and runtime.

A complete control design includes the mechanism and sensing. Moving an encoder from motor to load may expose gearbox backlash; increasing bandwidth can excite structural modes; adding a filter adds phase lag. Revisit the architecture before tuning around an unsuitable mechanism.

## 4. Design reviews and evidence gates

| Stage | Work product | Exit evidence |
|---|---|---|
| Feasibility | Mission profile, requirements, concept comparison, major unknowns | First-order physical bounds and hardest assumption tested |
| Preliminary design | Layout, budgets, interfaces, model, risk treatment | Adequate reserve and prototype experiment plan |
| Detailed design | Revision-controlled CAD/drawings, circuits, firmware, BOM, test fixtures | Peer checks, simulated/analytical results, manufacturability feedback |
| Engineering verification | Instrumented integrated prototype | Requirements tested under defined conditions; defects recorded |
| Design validation | Representative users and environment | Intended use demonstrated; usability/service needs validated |
| Production validation | Pilot build with real process and fixtures | Yield, process capability where applicable, traceability and work instructions |
| Release/service | Frozen baseline, acceptance records, manuals, spares and rollback | Named release authority and open deviations accepted |

Distinguish verification (“built to specification”) from validation (“solves the user's problem”). Do not certify a prototype by renaming its test phase.

## 5. Configuration and commissioning handoff

Record hardware assembly/revision/serial IDs, bootloader, firmware/source commit, toolchain, libraries, build flags, OS and drivers. Store configuration in a versioned schema with units and valid ranges. Record encoder counts per motor/load revolution and quadrature convention, gear ratios, sensor polarity, homing direction, travel limits, torque/current limits, control sample period, filter coefficients, gains, bus IDs, safety timeouts and calibration coefficients. Keep credentials separate.

Provide backup/export and rollback procedures before changing a commissioned baseline. Check configuration belongs to the actual hardware revision; a valid file for another gear ratio can still cause a crash. Explain persistence across reboot and how to detect defaults or corrupt settings.

Commission in bounded stages selected for the machine: visual/mechanical inspection → continuity/isolation as applicable → current-limited supply with actuators disabled → sensor readings and polarity → stop/interlock checks → restrained or unloaded low-energy motion → homing/limits → control tuning → incremental load and speed → thermal endurance → fault/restart tests → acceptance. Define personnel, fixture, instrument, start conditions, stop limits, pass/fail criterion and evidence for each test. Never command an unverified drive from a document example.

## 6. Fault diagnosis and change control

Preserve the last known working configuration and collect reproducible logs before edits. Rank hypotheses by probability, consequence and cost of a discriminating test. Separate mechanical looseness/backlash, power droop/EMI, sensor/clock faults, model errors, control tuning and software scheduling. Change one causal factor at a time where feasible. For intermittent problems synchronise voltage, current, command, measured response and event timestamps.

For every released change record reason, affected parts/interfaces, revisions, recalibration needs and regression tests. A replacement “equivalent” component requires checking ratings, dynamics, connector pinout, software support and quality documentation. Maintain a field issue and corrective-action loop that updates design and manufacturing records.

## 7. Close the job

Supply files actually created, not names of imagined deliverables. If native CAD or a PCB tool is unavailable, provide dimensioned requirements, parameter tables and an explicit pending export task. A design package can be complete for review while physical validation remains pending; state both. Separate quote estimates from purchase orders and shipped goods from customer acceptance. Transfer the latest dossier and configuration baseline between sessions or platforms; do not assume their memory is shared.
