# Control Systems Methods

How to make a machine do what you command despite disturbances, noise, and imperfect models. Prerequisites per topic are listed in [topic-map.md](topic-map.md); the underlying mathematics is in [mathematics-modeling.md](mathematics-modeling.md) and plant models come from [mechanics-dynamics.md](mechanics-dynamics.md).

## Open loop vs closed loop; feedback vs feedforward

**Open loop** commands without measuring the outcome (a stepper stepping a light load): cheap, sensorless, but it cannot correct output errors from the missing feedback; whether errors accumulate depends on the system. **Closed loop** measures, compares to the target, and corrects: it rejects disturbances and model error, at the price of sensors and the new possibility of instability. **Feedforward** uses what you *know* to command proactively — gravity-compensation torque on an arm, velocity feedforward on a trajectory — leaving feedback to clean up only what you *don't* know. The working principle: feedforward the predictable, feedback the residual; a validated combination can improve tracking and disturbance rejection; an incorrect feedforward model can make performance worse.

## PID, anti-windup, derivative filtering

u = K_p·e + K_i·∫e·dt + K_d·de/dt: proportional acts on present error, integral removes steady-state error, derivative anticipates and damps. Two practical additions are near-mandatory:

- **Anti-windup:** when the actuator saturates, the integral keeps accumulating error it cannot act on, producing large overshoot when saturation ends. Clamp the integrator during saturation or use back-calculation — actuator limits always exist, so this always matters.
- **Derivative filtering:** a pure derivative amplifies sensor noise without bound. Implement it filtered, K_d·s/(τ_f·s + 1) with τ_f chosen from noise spectra, bandwidth and phase-loss tradeoffs (a fraction of derivative time is only a starting heuristic), and take the derivative of the *measurement*, not the error, to avoid a kick at every setpoint step.

**Limitations:** one PID handles one dominant dynamic well; strong cross-coupling, long delays, or strongly nonlinear plants call for the later sections.

## Cascade control

Nested loops: a fast inner loop (motor current or velocity) inside a slower outer loop (position). The inner loop linearizes and speeds up what the outer loop sees. Practice: tune the inner loop first and make it substantially faster — commonly 5–10× — than the outer loop's intended bandwidth. If the outer loop is pushed up toward the inner loop's bandwidth, the loops interact, the timescale-separation argument that justified the structure collapses, and both degrade together.

## Frequency-domain tools and fundamental limits

These work on the transfer function G(s), defined with zero initial conditions ([mathematics-modeling.md](mathematics-modeling.md)).

- **Bode plot:** gain and phase versus frequency. Stability margins use the loop transfer L = C G H, including sensing H and delay, under a stated negative-feedback convention; a plant-only plot does not give closed-loop margins. Phase margins of roughly 30–60° are a common target range — plant-dependent design targets, not guarantees.
- **Root locus:** how closed-loop poles migrate as one gain varies; shows exactly when raising gain drives the system unstable.
- **Nyquist criterion:** counts encirclements of −1 to decide closed-loop stability, valid even for open-loop-unstable plants where casual Bode reasoning fails.
- **Sensitivity and the waterbed:** S(s) = 1/(1 + G·C) measures how much feedback attenuates disturbances at each frequency. The Bode sensitivity integral imposes a waterbed tradeoff under specified conditions (for example a stable closed loop with a rational continuous-time loop transfer of sufficient relative degree); its value depends on unstable open-loop poles. Check the theorem's assumptions before asserting a particular integral. Nonminimum-phase zeros and delay impose additional performance limits. Disturbance location matters: S maps output disturbances; input disturbances involve G S, and measurement-noise transmission involves complementary sensitivity T = L/(1+L). Any promise of perfect tracking at all frequencies violates this limit.

## State space, controllability, observability, observers, Kalman

ẋ = A·x + B·u, y = C·x + D·u puts many states, inputs, and outputs in one notation. **Controllability** asks whether the inputs can steer every state; **observability** whether the measurements can reveal every state. Check both before designing: an uncontrollable unstable mode is a hardware redesign problem, not a tuning problem. **Observers** (Luenberger) reconstruct unmeasured states from a model corrected by measurements; the **Kalman filter** is a minimum-variance linear estimator under appropriate linear-model, initial-state and noise assumptions; with Gaussian distributions it has stronger posterior-mean optimality. It balances model and measurements using their covariances — the standard tool for fusing an IMU with encoders. Warning: wrong covariances produce confidently wrong estimates. Sanity-check by comparing innovation (residual) magnitudes against their predicted statistics; persistent excess means the filter is lying to you.

## Digital implementation

When implementing a controller digitally, specify its sample period T_s. Analog implementations instead require circuit/component bandwidth and tolerance analysis.

- **Discretization:** convert the continuous design (Tustin's method preserves frequency response well below Nyquist) or design directly in z.
- **Delay:** the zero-order hold plus computation adds effective delay of roughly T_s/2 plus compute time, which consumes phase margin — a paper design with 45° margin can lose 10–20° here. Re-check margins *after* discretization.
- **Sample rate:** a common starting heuristic is 10–30× the intended closed-loop bandwidth. This is a heuristic, not a rule: delay-sensitive or resonant plants need explicit analysis, and no single rate suits all systems.
- **Jitter:** irregular sample timing behaves like a time-varying delay; run control from a fixed-priority timer, never best-effort scheduling.
- **Aliasing:** filter before the ADC ([mathematics-modeling.md](mathematics-modeling.md) sampling section).

## MIMO: coupling, decoupling, LQR/LQG, MPC

When several inputs affect several outputs — drone attitude, multi-joint arms — tuning loops one at a time can fail because each loop disturbs the others. Screen the coupling first (the relative gain array is the classic check). Options in escalating effort: sensible input–output pairing with detuned loops; a static decoupling matrix; full multivariable design. **LQR** chooses state/control quadratic cost weights and yields u = −K x under stabilizability/detectability and suitable Q/R conditions. Check units/scaling and reference tracking; state regulation alone does not automatically track arbitrary setpoints. Classical margin results depend on the precise loop structure and assumptions. **LQG** (LQR plus a Kalman filter) is one option when states are not directly measured, but LQR's margin guarantees no longer carry over — verify robustness explicitly. **MPC** re-optimizes a trajectory over a horizon every step and represents constraints (actuator limits, keep-out states) explicitly, with actual satisfaction depending on feasibility, model error, state estimation and implementation: the natural choice when constraints dominate the problem, at the cost of modeling effort, compute, and a required safe fallback for when the optimizer fails to converge in time.

## Robust, adaptive, and nonlinear methods

- **Robust / H-infinity:** design against a *specified* set of model errors; the resulting guarantees hold only for that specified set.
- **Gain scheduling:** linear designs across operating points with scheduled/blended gains; validate transitions and scheduling-rate effects because stable frozen designs do not prove stability while switching.
- **Adaptive control:** adjusts parameters online; powerful when parameters drift slowly and the input stays persistently exciting, hazardous without those safeguards.
- **Lyapunov methods:** prove stability by exhibiting an energy-like function that always decreases along trajectories — the proof language for nonlinear designs.
- **Passivity:** a passive subsystem cannot generate net energy beyond its initial storage. A well-posed negative-feedback interconnection preserves passivity; stronger convergence/boundedness conclusions need appropriate strictness, storage and detectability assumptions. Check sampling, delay and saturation in impedance/contact control.
- **Sliding mode:** drives a defined state function toward a switching surface with robustness under specified matched uncertainty and actuator assumptions. Chattering can excite hardware; boundary layers or higher-order designs trade tracking/robustness against switching and sampling limits.
- **Fuzzy control:** encodes operator heuristics as interpolated rules; useful when expertise exists but no model does, and it carries no inherent stability guarantee.

## Machine learning: role and limits

ML earns its place in perception (recognizing objects and terrain), residual modeling (fitting the friction the physics missed), and tuning assistance — all feeding a conventional, analyzable control loop. A learned inner-loop policy does not inherit stability or robustness guarantees merely from training success. Some constrained learning methods support proofs under stated assumptions; verify those assumptions, out-of-distribution behaviour and implementation before relying on them. The preferred architecture: model-based inner control for stability, learning at outer or supervisory layers, and hard safety limits enforced outside anything learned. Platform-level training practice lives in [robotics-autonomy.md](robotics-autonomy.md).

## Decision matrix

| Situation | Start with | Escalate to |
|---|---|---|
| Single axis, mild dynamics | PI/PID with anti-windup | Cascade P/PI |
| Position atop fast velocity dynamics | Cascade loops | State feedback |
| Multiple coupled axes | Paired PIDs + coupling screen | LQR / LQG |
| Hard actuator or state constraints | Saturation-aware PID | MPC |
| Key states unmeasured or noisy | PID on filtered signal | Observer/Kalman + state feedback |
| Wide operating range | Gain scheduling | Adaptive or nonlinear design |
| Large model uncertainty | Conservative PID | H-infinity or sliding mode |
| Contact with people or environment | Passivity-based impedance control | Force / hybrid control |

Escalate only when the simpler design measurably misses a requirement: each step rightward costs modeling, compute, and validation effort, and the reuse > extend > integrate > build > buy preference ([topic-map.md](topic-map.md)) applies to controllers as much as hardware.

## Tuning and validation recipe

1. **Identify:** use a bounded identification experiment (steps/chirps when appropriate), with stabilising feedback retained for an unstable or otherwise unsuitable open-loop plant, and fit a low-order model ([mathematics-modeling.md](mathematics-modeling.md) system identification).
2. **Design in simulation** against that model with explicit margin targets (for example ≥ 45° phase margin — a design target, not a guarantee of real-world stability).
3. **Discretize** and re-check margins including hold and compute delay at the actual sample period.
4. **Test progressively:** simulation → bench with emulated load → hardware at reduced gains and limits → full envelope. Software limits on torque, speed, and position, plus an independent stop path, are active from the first hardware run.
5. **Validate against requirements:** settling time, overshoot, disturbance recovery, steady-state error, and behavior during saturation — each measured, not assumed.
6. **Re-verify after any mechanical change:** stability margins belong to the plant-plus-controller pair, not to the controller alone.

Nothing in this guide constitutes hardware-validated performance. Every design must be validated on the specific system it will run on, no sample rate suits every plant, and no controller is universally stable.

## Worked example: motor position control, end to end

**Assumed illustrative plant:** a DC gearmotor whose voltage-to-speed response is G_v(s) = 8/(0.15·s + 1) (rad/s per volt, time constant 0.15 s). **Inner velocity loop:** PI, C(s) = K_p·(1 + 1/(T_i·s)). Choosing T_i = 0.15 s cancels the plant pole, leaving loop gain 8·K_p/(0.15·s); K_p = 0.4 places crossover near 21 rad/s — assumed comfortably below unmodeled drive and electrical dynamics, an assumption to verify during identification. **Outer position loop:** position integrates velocity, so a pure proportional gain K_pos = 3 gives an outer bandwidth near 3 rad/s — about 7× separation from the inner loop, satisfying the cascade rule. **Digital:** T_s = 5 ms is roughly 60× the inner bandwidth — deliberately generous because delay margin is cheap here, not because 5 ms is a universal answer. Tustin-discretize the PI, clamp the integrator at the drive's voltage limit, and filter any derivative term ever added. **Analytical check:** exact cancellation in this ideal model gives L(s) = 21.333/s and 90° phase margin before delay; a 2.5 ms hold-delay approximation contributes about 3.06° at crossover. This excludes computation delay, discretisation details and imperfect cancellation. The ideal outer characteristic polynomial is s² + 21.333s + 64, with two real negative poles, consistent with a monotonic zero-initial-condition step in this simplified model. **Checks still required:** discrete loop margins, parameter variation, saturation/antiwindup, sensor noise and measured drive dynamics. Pole cancellation is fragile if the fitted pole changes. **Status:** original illustrative calculation with assumed parameters; no measured motor identification, simulation of this cascade example or hardware validation is claimed.
