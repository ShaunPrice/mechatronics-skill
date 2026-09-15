# Robot architectures, autonomy and training

Start from the mission and environment, then choose embodiment and autonomy. More degrees of freedom or a learned controller do not automatically improve task success. Use [mechanics](mechanics-dynamics.md) for sizing and frames, [controls](control-systems.md) for motion, and [simulation](simulation-validation.md) for evidence.

## Robot types and engineering implications

| Robot class | Typical mission and useful techniques | Critical design/validation questions |
|---|---|---|
| Wheeled: differential, Ackermann, omnidirectional | Indoor/outdoor transport; odometry, path planning and tracking | Traction, wheel slip, turning envelope, slopes, braking distance, payload stability and ground clearance |
| Tracked | Rough/soft terrain; skid steering and terrain interaction | Turning resistance, drivetrain heat, ground pressure, track tension and odometry error |
| Articulated arm, SCARA, collaborative application | Assembly, inspection, handling; IK, trajectory and impedance/force control | Payload inertia versus reach, singularities, tooling, collision, cycle time, guarding and application-specific interaction forces |
| Cartesian/gantry | Repeatable rectangular workspace, CNC/pick-and-place | Axis orthogonality, racking, backlash, screw/belt sizing, cable management and travel limits |
| Parallel/delta/hexapod | High acceleration or platform positioning | Workspace/collision constraints, coupled dynamics, calibration and singularities |
| Legged/humanoid | Traversal and interaction; contact planning, whole-body control | Balance, friction cones, contact impacts, energy, falls and recovery envelope |
| Drone/multirotor/fixed wing/VTOL | Aerial sensing and transport | Thrust/weight, aerodynamics, state estimation, wind, energy reserve, link loss and lawful operating environment |
| Surface vessel/sail robot | Water monitoring and transport | Buoyancy, stability/righting, drag, wind/current, waterproofing, corrosion, navigation and recovery |
| ROV/submersible/AUV | Underwater inspection/science | Hydrostatic pressure, sealing, buoyancy trim, added mass, hydrodynamic damping, acoustic/optical navigation, tether drag or autonomous recovery |
| Swarm/multi-robot fleet | Coverage, transport or distributed sensing | Task allocation, consensus assumptions, communication limits, collision avoidance, deadlock and loss of members |
| Soft/continuum/cable-driven | Confined access, compliant manipulation | Shape sensing, material hysteresis, cable tension, contact modelling and calibration |
| Wearable/exoskeleton/medical application | Assistive motion or clinical tasks | Human variability, alignment, contact/force limits and applicable specialist validation obligations |
| Hybrid/amphibious/climbing | Transitions across environments | Adhesion/contact, mode transitions, recovery and combined environmental constraints |

“Water robot” needs a distinction between surface and underwater operation. Pressure grows with depth as approximately ρ g h relative to the surface; an enclosure splash rating does not establish depth capability. Most ordinary radio links perform poorly through water; evaluate tether, acoustics and local autonomy using the actual mission.

## Kinematics, motion and manipulation

Define world/map, odometry, base, joint, tool and sensor frames with a consistent handedness. Use homogeneous transforms or quaternions/rotation matrices, with explicit active/passive and multiplication conventions. Normalise quaternions and account for the q/−q equivalence when comparing orientations. Check a known pose through the entire transform chain before tuning a controller.

Forward kinematics maps joint positions to tool pose; inverse kinematics finds joint positions for a target pose. IK can have zero, one or multiple solutions. Respect joint limits, self-collision, obstacles, singularities and task priorities. Jacobians map joint rates to tool twist and transpose-map suitable wrenches to joint torques under consistent frames. Use damped least squares near singularity while reporting the resulting tracking compromise. A numerical IK result is not a collision-free trajectory.

Plan a geometric path, time-parameterise it under velocity/acceleration/jerk/torque limits, then track it with feedback. Choose trapezoidal or S-curve profiles for industrial moves; trajectory optimisation/MPC when coupled constraints justify it. Include stopping distance and dynamic obstacles. For manipulation, separate grasp geometry, payload uncertainty, contact force, slip detection and release verification. Use impedance/admittance control when compliant interaction is needed and sensing/actuator bandwidth permit it; analyse interaction stability with environment stiffness and delay.

## Perception, localisation and navigation

Choose detection/segmentation/tracking/pose estimation based on task success, not generic benchmark accuracy. Calibrate camera intrinsics/extrinsics and timing. Test lighting, weather, dust, reflective/transparent objects, motion blur and unusual objects. Preserve confidence and quality indicators; model confidence is not guaranteed probability of correctness.

Odometry integrates relative motion and drifts. Localisation estimates pose against a reference; SLAM jointly estimates pose and a map. Fuse IMU/encoder/GNSS/vision/range data only after units, frames, bias, delay and covariance are checked. Evaluate innovation/residual distributions and recovery after outages. Ground-truth quality bounds what the evaluation can establish.

For planning, use graph search such as Dijkstra/A* on an appropriate representation, sampling planners for complex configuration spaces, or optimisation for dynamic constraints. Select global route plus local obstacle handling when appropriate. Define reachable free space including robot footprint, payload, uncertainty and braking envelope. A map cell being free does not prove a suspended load or tall robot clears the space.

## ROS and operating architecture

ROS 2 is middleware and tooling for component communication, not by itself a hard real-time operating system or certified safety controller. Choose a supported distribution and compatible packages for the target OS/hardware; verify current support and maintain a lockfile/container or reproducible environment. Avoid silently choosing Rolling for a production baseline.

Separate nodes by coherent responsibility: drivers, state estimation, planning, control interface, diagnostics and mission coordination. Use topics for streams, services for bounded request/reply, actions for long-running cancellable tasks. Configure frames, timestamp source, message units, namespaces, robot descriptions (URDF/Xacro), inertias, joint limits and sensor extrinsics. Use tf2 and recorded datasets to diagnose transforms and timing. Package names such as Nav2, MoveIt 2, ros2_control and micro-ROS are starting points; verify their current compatibility and actual hardware support.

DDS/ROS QoS must match the communication need and publisher/subscriber compatibility. Decide reliability, history/depth, durability, deadlines and liveliness from message semantics and network limits. Old reliable commands can be worse than dropped data if freshness is not enforced. Inspect offered/requested policies when a topic exists but no messages arrive. Official [ROS QoS and interface sources](sources.md) support these distinctions.

Keep fast current/velocity loops and immediate fault reactions local to suitable hardware. Measure end-to-end sensor-to-actuator delay, not only node execution time. Bound command authority and implement watchdogs, state transitions, cancellation, safe restarts and logging. Connected robots also require identity, access control, update integrity, secrets handling and a threat model for the actual interfaces.

## Machine learning and robotics training

| Technique | Use when | Inputs, output and validation |
|---|---|---|
| Supervised learning | Labels represent desired perception/prediction | Curated labelled data → model; split by scene/site/time/robot to avoid leakage; evaluate task-level failures and distribution shift |
| Self-supervised/representation learning | Large unlabelled streams with usable pretext signal | Sensor sequences → representations; validate downstream benefit and robustness |
| Imitation/behaviour cloning | Demonstrations describe useful behaviour | Expert trajectories → policy; test compounding errors and recovery outside demonstrations |
| DAgger-style iterative data collection | Policy visits states absent from demonstrations | Reviewed intervention labels → expanded dataset; constrain collection and expert authority |
| Reinforcement learning | Sequential decisions with meaningful reward and safe training environment | Simulator/environment/reward → policy; evaluate reward hacking, constraints, seed variation and independent scenarios |
| Residual learning / learned dynamics | Physics model works but misses repeatable effects | Residual data → bounded correction; retain baseline/fallback and uncertainty-aware limits |
| Bayesian optimisation / design of experiments | Expensive tuning with bounded parameters | Safe parameter bounds and objective → tested candidate; account for noise and experimental budget |
| Foundation/vision-language-action models | High-level semantic tasks or demonstrated applicable skills | Task/context → action proposal; verify grounding, latency, feasible action set and recoverable execution |

Start with a non-ML baseline and a metric tied to the requirement. State why data-driven behaviour may improve it. Define dataset provenance/permission, label quality, class balance, train/validation/test separation, preprocessing and model version. Collect rare-but-important conditions deliberately. Evaluate calibration, precision/recall or regression error where relevant, but also mission completion, collision/near-miss, intervention rate, energy, timing and recovery.

For sim-to-real, calibrate dynamics and sensor models from measurements, randomise plausible mass/friction/delay/noise/lighting ranges, use curriculum learning where helpful and test withheld environments and parameters. Domain randomisation does not prove transfer; parameter ranges must reflect reality. Hardware-in-loop and guarded physical trials establish successive evidence levels. Record seeds, simulator versions, hyperparameters, training duration and evaluation episodes; running inference is not training and exporting a model is not deploying it.

Use a bounded deployment ladder: offline replay → simulation stress cases → shadow/advisory mode → restricted trials with an independent stop/fallback → monitored expansion after acceptance. High-level language-model plans must pass feasibility, authority and freshness checks before becoming actuator commands. Explain the permitted action envelope and what happens when confidence or communication is lost.

## Fleet and service

For swarms, distinguish central scheduling from distributed coordination. State graph connectivity assumptions, local sensing limits, clock synchronisation, collision constraints and convergence conditions before invoking consensus theory. Test partitions, lost robots, contradictory maps and task reassignment. Optimise throughput without hiding congestion, charging, maintenance and service costs. Deliver fleet identity/configuration, telemetry retention, update/rollback, operator procedures and recovery tools with the engineering package.
