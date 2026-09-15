# Topic Map and Decision Aid

This is the entry point for the whole skill. Use it three ways: (1) you know the topic — find it in the topic groups and follow the link; (2) you know what you mean but not what engineers call it — use the terminology table; (3) you have a problem or symptom — use the routing table to reach a method directly. Then read only the prerequisites the teaching ladder lists for your goal, not a whole subject. Everything here explains plainly first, then gives the precise term so you can search datasheets, papers, and forums with the vocabulary professionals use.

## Topic groups

- **Mathematics and modeling** — [mathematics-modeling.md](mathematics-modeling.md): algebra/trigonometry, complex numbers, dimensional analysis, calculus, differential equations, linear and tensor algebra, Laplace/Fourier/Z transforms, sampling and aliasing, statistics and uncertainty, system identification, numerical methods and optimization.
- **Mechanics and dynamics** — [mechanics-dynamics.md](mechanics-dynamics.md): statics and free-body diagrams, momentum, work and energy, rigid-body dynamics and inertia tensors, reference frames, rotating-frame (Coriolis/centrifugal) effects, Lagrangian and Hamiltonian mechanics, kinematics and inverse kinematics, Jacobians and singularities, oscillators and phase space, plus pointers to contact, friction, fatigue, thermal, fluid, and buoyancy topics.
- **Control systems** — [control-systems.md](control-systems.md): open/closed loop, feedback and feedforward, PID with anti-windup and derivative filtering, cascade loops, frequency-domain tools and their fundamental limits, state space, observers and Kalman filtering, digital implementation, MIMO methods (LQR/LQG/MPC), robust/adaptive/nonlinear control, the role and limits of machine learning.
- **Electronics and embedded** — [electronics-embedded.md](electronics-embedded.md): actuators, instrumentation and advanced sensors, MCU and FPGA platforms, analog, digital, power, and radio electronics.
- **Robotics and autonomy** — [robotics-autonomy.md](robotics-autonomy.md): robot classes (wheeled, arms, Cartesian, aerial/drones, surface-water and submersible, legged, swarm), ROS, robot training and learning.
- **Materials and manufacturing** — [materials-manufacturing.md](materials-manufacturing.md): metals, nonmetals, ceramics, composites, lubricants, batteries, machining, and manufacturing processes.
- **Simulation and validation** — [simulation-validation.md](simulation-validation.md): numerical simulation software and how to trust (or distrust) its outputs.
- **Commercial delivery** — [commercial-delivery.md](commercial-delivery.md): costing, financing, new product development, quality, sales and marketing, complete design handoff packages.
- **Project workflow** — [project-workflow.md](project-workflow.md): how a project moves from idea through design, build, validation, and delivery.
- **Sources** — [sources.md](sources.md): the verified authoritative references behind these guides.

- **Manufacturing operations** — [manufacturing-operations.md](manufacturing-operations.md): queueing theory/Little’s law/M/M/1/M/M/c/Kingman, Kanban sizing, JIT, takt/cycle time, WIP, line balancing/SMED/pull systems, SPC/control charts/capability/acceptance sampling.
- **Browser simulation** — [browser-simulation.md](browser-simulation.md): runnable editable 2D/3D models, live charts, root locus/Bode/Nyquist interpretation and validation.

## Teaching ladder: what you actually need first

Principle: learn only the prerequisites the immediate job needs, then deepen when a real problem demands it. Each row is a common goal with its genuine minimum.

| Goal | Minimum prerequisites | Then read |
|---|---|---|
| Size a motor for an arm joint | Algebra, trigonometry, free-body diagrams | [mechanics-dynamics.md](mechanics-dynamics.md) statics section |
| Tune a PID on one axis | First-order response intuition (time constant, damping) | [mathematics-modeling.md](mathematics-modeling.md) ODEs; [control-systems.md](control-systems.md) PID and recipe |
| Read frequency specs correctly | rad/s vs Hz, complex numbers | [mathematics-modeling.md](mathematics-modeling.md) conventions |
| Fuse an IMU with encoders | Basic linear algebra, statistics | [mathematics-modeling.md](mathematics-modeling.md); [control-systems.md](control-systems.md) observers |
| Derive equations of motion for a linkage | Calculus, energy methods | [mechanics-dynamics.md](mechanics-dynamics.md) Lagrangian section |
| Put control on a microcontroller | Sampling, Z-transform basics | [mathematics-modeling.md](mathematics-modeling.md) sampling; [control-systems.md](control-systems.md) digital section |
| Coordinate multiple coupled axes | State-space form, matrices | [control-systems.md](control-systems.md) MIMO section |
| Predict behavior before building | Numerical integration, system identification | [mathematics-modeling.md](mathematics-modeling.md); [simulation-validation.md](simulation-validation.md) |
| Deliver a costed, documented product | Customer problem, provisional technical scope and cost assumptions | [commercial-delivery.md](commercial-delivery.md); [project-workflow.md](project-workflow.md) |

## Novice-to-engineer terminology

Your words are a fine starting point — this table just gives you the searchable term.

| You might say | Engineers say | Where |
|---|---|---|
| "reverse kinematics" | inverse kinematics (IK) — same concept, standard name | [mechanics-dynamics.md](mechanics-dynamics.md) |
| "it wobbles / rings" | underdamped oscillation, resonance | [mechanics-dynamics.md](mechanics-dynamics.md), [control-systems.md](control-systems.md) |
| "it drifts over time" | sensor bias, thermal drift, accumulated integration error; diagnose from data | [control-systems.md](control-systems.md) |
| "twitchy, jittery" | excess gain, noise amplification | [control-systems.md](control-systems.md) |
| "how strong a motor I need" | torque sizing via statics | [mechanics-dynamics.md](mechanics-dynamics.md) |
| "gearing it down" | speed reduction / torque multiplication | [mechanics-dynamics.md](mechanics-dynamics.md), [electronics-embedded.md](electronics-embedded.md) |
| "the maths of spinning things" | rigid-body dynamics, inertia tensor | [mechanics-dynamics.md](mechanics-dynamics.md) |
| "smoothing the sensor" | low-pass filtering, state estimation (Kalman) | [control-systems.md](control-systems.md) |
| "the speed where it shakes worst" | resonant response near a mode; forcing and damping shift the peak | [mechanics-dynamics.md](mechanics-dynamics.md) |
| "making it follow a path" | trajectory tracking, feedforward + feedback | [control-systems.md](control-systems.md), [robotics-autonomy.md](robotics-autonomy.md) |
| "the arm locks up at full stretch" | kinematic singularity | [mechanics-dynamics.md](mechanics-dynamics.md) |
| "wiggle room in the parts" | tolerance (allowed) vs uncertainty (unknown) | [mathematics-modeling.md](mathematics-modeling.md) |
| "fast readings that look slow and wrong" | aliasing | [mathematics-modeling.md](mathematics-modeling.md) |
| "teaching the robot" | learned policies, training | [robotics-autonomy.md](robotics-autonomy.md) |

## Symptom-to-method routing

| Symptom | Likely cause family | First method | Guide |
|---|---|---|---|
| Oscillates around the target | Excess gain / low phase margin | Inspect response/saturation and mechanical condition; analyse loop margins | [control-systems.md](control-systems.md) |
| Big overshoot after hitting a limit | Integrator windup | Anti-windup | [control-systems.md](control-systems.md) |
| Steady error that never closes | Missing integral action, or stiction | Measure saturation, bias and friction before adding integral action | [control-systems.md](control-systems.md), [mechanics-dynamics.md](mechanics-dynamics.md) |
| Joint speeds explode near one pose | Singularity | Jacobian analysis, path margin | [mechanics-dynamics.md](mechanics-dynamics.md) |
| Motor stalls or overheats holding still | Undersized holding torque; thermal limit | Static torque analysis | [mechanics-dynamics.md](mechanics-dynamics.md), [electronics-embedded.md](electronics-embedded.md) |
| Violent vibration at one speed only | Resonance | Measure spectrum/modal response; inspect imbalance, looseness and mounting | [mechanics-dynamics.md](mechanics-dynamics.md) |
| Sensor shows a slow signal that should be fast | Aliasing | Anti-alias filter, raise sample rate | [mathematics-modeling.md](mathematics-modeling.md) |
| Simulation disagrees with bench | Parameters, timing, boundary conditions or model form | Reconcile inputs/units and compare residuals before identification | [mathematics-modeling.md](mathematics-modeling.md), [simulation-validation.md](simulation-validation.md) |
| Part cracks after weeks of fine service | Fatigue, creep, corrosion or assembly damage | Inspect fracture and load/environment history | [materials-manufacturing.md](materials-manufacturing.md) |
| Two axes fight each other | Cross-coupling | Coupling assessment, MIMO design | [control-systems.md](control-systems.md) |
| Stable slow, unstable fast | Delay/unmodeled dynamics eating margin | Frequency-domain + digital delay analysis | [control-systems.md](control-systems.md) |
| Estimator confident but wrong | Bias, frames, timestamps, model or covariance mismatch | Innovation and calibration checks | [control-systems.md](control-systems.md) |
| Floats or sinks wrongly | Buoyancy/ballast balance | Buoyancy first cut | [mechanics-dynamics.md](mechanics-dynamics.md), [robotics-autonomy.md](robotics-autonomy.md) |
| Works on the desk, fails in the field | Validation gap | Structured validation plan | [simulation-validation.md](simulation-validation.md), [project-workflow.md](project-workflow.md) |

## Choosing a build strategy

Before designing anything, apply the preference order **reuse > extend > integrate > build > buy**, judged against suitability and total cost (purchase price plus integration, maintenance, and replacement effort). A reused proven module beats a fresh design of equal function; a bought subsystem can still beat building when integration cost is honestly counted — the order sets the default, suitability decides the exception. Costing and sourcing detail lives in [commercial-delivery.md](commercial-delivery.md).

## Risk routing

Real hazards in this domain are specific: stored mechanical energy (springs, raised loads, flywheels), lithium battery abuse, pinch and crush points on actuated joints, high-voltage sections of drives, and autonomous motion starting unexpectedly. Each guide flags its hazards where the method creates them; the validation progression in [control-systems.md](control-systems.md) and [project-workflow.md](project-workflow.md) exists chiefly to manage them. Treat any energized, mobile, or load-bearing test as a hazard review trigger, not a formality.

## Scene interchange and production flow

- [OpenUSD workflow](openusd-workflow.md): connect the small browser prototype to composed robot/cell scenes using explicit units, transforms, sampled animation and asset structure. Add physical properties and validate engine support before dynamics.
- [Manufacturing operations](manufacturing-operations.md): map production flow, estimate queueing/wait/WIP, size Kanban, implement JIT with justified buffers and apply statistical quality controls. Use these when a working prototype must become repeatable production.

- [Visual system builder](system-builder.md): assemble scalar signal blocks, connect feedback, edit parameters and run deterministic experiments with scopes; choose a different solver for acausal/stiff/multibody systems when necessary.

- [Thermal and fluid systems](thermal-fluid-systems.md): derive energy/mass/momentum balances, choose heat-transfer/pipe-flow models, size cooling/pumping and progress to CFD with boundary/mesh/conservation validation.

- [Toolchain interfaces](toolchain-interfaces.md): export a selected browser plant to Scilab/Xcos configuration and a ROS 2 simulation package, manage ATOMS explicitly, and verify equations/time/units at each boundary.
