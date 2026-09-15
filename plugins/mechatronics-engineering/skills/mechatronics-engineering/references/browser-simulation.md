# Generate an engineering simulator that runs in a browser

Use this workflow when the user wants to see a solution move, change parameters, compare controllers or learn frequency/pole methods. Deliver the code and a usable browser artifact, not only an architectural suggestion. The included [workbench](../assets/browser-lab/index.html) is a starting implementation; its actual models and validation limits must remain visible.

## 1. Make the model explicit

State the engineering question and acceptance measures, then identify states, inputs, outputs, parameters, units, frames, initial conditions, disturbances and constraints. Distinguish a kinematic visualisation from a dynamic simulation. In a kinematic arm, joint angles directly determine pose; without inertia, motor torque, contact and a solver it does not predict motion under load.

Choose appropriate equations before drawing. For an axis, m ẍ + b ẋ + k x = u + d is a useful model only when lumped mass, damping and stiffness approximate the mechanism. A thermal process, nonlinear pendulum, underwater vehicle or articulated robot requires its own equations. Use a model adapter boundary such as `derivative(state, input, parameters, time)`, `measure(state)`, `controller(reference, measurement, dt)` and `geometry(state)` so drawing code cannot silently determine physics.

For an existing nonlinear design, identify the operating point and linearise using Jacobians A = ∂f/∂x, B = ∂f/∂u, C = ∂h/∂x, D = ∂h/∂u when frequency/pole analysis is meaningful. Show both the nonlinear time simulation and the local model's validity range. If the mechanism lacks a usable model, deliver a clearly labelled conceptual visualisation and an identification experiment rather than invented dynamics.

## 2. Build the interactive interface

Use labelled controls with values, units, valid bounds and sensible increments. Let the user adjust physical properties (mass, stiffness, damping, geometry/load), controller gains, sampling, force/current saturation and disturbances as relevant. Explain what each changes physically. Validate nonfinite/invalid input and show errors beside the control. Do not coerce an impossible value silently.

Provide play/pause, reset, a repeatable baseline and export. Parameter changes must have an explicit policy: reset the run for comparable experiments, or mark the change in the timeline. Use presets for contrasting behaviours such as underdamped, well-damped and saturated, but call them examples. Avoid universal “safe gain” recommendations.

Use 2D for mechanisms, planar paths and easy-to-read load/position relationships. Use a 3D scene with real coordinates, camera projection and orbit controls for spatial arms, vehicles or clearances. A projected 3D wireframe can be sufficient without a large library; label the rendering method and keep the geometry faithful. Provide ground/grid, axes, scale and visible joint/end-effector markers. Joint sliders should update forward kinematics and a pose readout. A perspective scene alone does not establish collision checking or structural simulation.

Live charts should include time, reference, measured state, error, actuator command and disturbances where useful. Label units and distinguish reference/model/measurement. Use bounded history/downsampling for long runs, hover readouts or accessible numerical summaries, independent colours/line styles, and CSV/JSON export with parameters and evidence status. Keep animation speed separate from numerical time.

## 3. Keep computation independent of rendering

Use a fixed numerical step or justified adaptive solver; sample the controller at its own specified period and hold its output between updates. `requestAnimationFrame` schedules drawing and may pause or vary with browser load; it must not define the physical timestep. Accumulate elapsed time with a bounded catch-up policy, pause intentionally on a long hidden-tab delay, and report when real-time pace cannot be maintained. More displayed frames is not a higher control sample rate. See [MDN animation scheduling](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame).

Include actuator saturation, integral antiwindup, filtered derivative, quantisation/noise/delay when the scenario requires them. Record integration method, plant step, control sample and numeric precision. Recompute derived coefficients after parameter changes. Handle numerical overflow with a stopped simulation and useful diagnostic, not a flatline that looks stable.

Prefer an offline HTML/CSS/JavaScript bundle with no build step for novice portability. Use Web Workers for expensive computations when needed. Reuse a suitable installed library for general high-order systems, 3D or optimisation, but record its version/licence and make dependency/network requirements explicit. Do not imply a browser can perform hard real-time hardware control.

## 4. Explain root locus

**Intuition:** poles are the system's natural response modes; moving them changes decay, oscillation and instability. A root locus plots closed-loop poles while one scalar loop gain varies, with the plant and controller shape fixed.

For negative feedback L(s) = g N(s)/D(s), compute roots of D(s) + g N(s) = 0 over a stated gain sweep. Mark open-loop poles/zeros, the imaginary axis and current gain. Explain that right-half-plane poles imply growing modes for a continuous-time LTI model; discrete-time poles instead require the unit-circle test. Complex-conjugate poles show oscillatory modes, and their real parts set decay/growth rate. Pole stability alone does not guarantee acceptable actuator effort or transient performance.

Check polynomial conditioning and root residuals; match branches across gain steps without joining unrelated roots. Remove absent controller factors (for example a cancelled integrator when integral gain is zero) so fake poles are not plotted. Avoid hiding physically dangerous unstable pole-zero cancellations in a general model. Provide numerical poles and gain at the selected point.

**Use it:** single-parameter gain tuning, explaining how gain affects stability, and choosing compensator poles/zeros. **Limit:** simultaneous arbitrary PID changes are a family of different loci; a fixed shape is necessary for the meaning of each plot. High-order MIMO systems need suitable multivariable analysis.

## 5. Explain Bode

**Intuition:** drive a system with sine waves of different frequencies and compare output amplitude and timing. Plot magnitude and phase against logarithmic frequency. For loop analysis use the full dimensionless L(jω), not only the physical plant. Show Hz versus rad/s explicitly (ω = 2πf) and unwrap phase consistently.

At a gain crossover |L| = 1 (0 dB), phase margin is 180° + phase for the usual negative-feedback convention and the relevant phase branch. At a −180° phase crossing, gain margin is 1/|L| (or −20 log10|L| in dB). Interpolate crossings or refine the sweep; distinguish no crossing within the sampled range from a mathematically infinite margin. Report multiple crossings and their interpretation rather than selecting a reassuring one. A Bode chart of a nonminimum-phase/open-loop-unstable system needs the appropriate stability reasoning.

**Use it:** bandwidth, noise rejection, disturbance rejection, resonances, delay effects and compensator design. Show how derivative/filter/gain changes alter the tradeoff. The simplified hold-delay phase is approximately −ω T_s/2 at low frequency; actual sampled dynamics require discrete analysis. Positive classical margins are not a universal robust-stability guarantee for MIMO, nonlinear or uncertain systems.

## 6. Explain Nyquist

**Intuition:** take the loop response at each frequency and trace its real and imaginary parts as a curve. The critical point −1 + j0 represents feedback becoming self-reinforcing at the critical magnitude/phase. Mark it, label axes, show positive/negative frequency branches and direction.

For an explicitly chosen conventional contour enclosing the right half-plane clockwise, let N be the net clockwise encirclements of −1 by the mapped complete contour, P the open-loop RHP poles and Z the closed-loop RHP poles. Then N = Z − P, so stability requires Z = 0 and N = −P. Some texts count counterclockwise instead: state the convention before counting. Poles on the imaginary axis require a contour indentation and its mapped contribution.

**Use it:** assess stability with open-loop unstable poles, delays and cases where casual Bode margin reading is inadequate. **Limit:** plotting only finite-frequency L(jω) points is not the complete contour proof. Integral control introduces a pole at zero; do not count encirclements from an unindented finite curve and claim certification. A workbench may show an educational frequency trace plus independently computed closed-loop polynomial poles; label these separately.

## 7. Validate and deliver

Check known polynomial roots, repeated/conjugate roots, cancelled controller terms, frequency limits, numerical step convergence, parameter effects, saturation and reset/export reproducibility. Compare a simple model to analytical results or an independent implementation. Exercise the actual browser controls, 2D/3D views, resizing, pausing and error states; report which browsers were tested. A screenshot alone proves rendering, not correct simulation.

Deliver HTML/JS/CSS and run instructions, equations/assumptions, parameter table, example experiments, exported baseline, test results and limitations. For hosted ChatGPT, provide downloadable code/artifacts or a supported preview; ordinary Markdown knowledge uploads do not themselves execute the simulator. Open local browser code directly or serve it on loopback for testing; do not publish a private design to a public web host without authorisation.

## 8. Exchange scenes with OpenUSD

For design review or a larger robot/factory scene, offer the browser's OpenUSD USDA exports: current arm pose or recorded joint motion. Use the [OpenUSD workflow](openusd-workflow.md) for stage units, axis conventions, transform hierarchy, sampled timing, external references and physical-model handoff. Validate exports with a real USD parser and compare world coordinates against the original FK at multiple poses/times. Exported visuals do not supply mass, inertia, collision, drives or actuator dynamics. Do not silently infer those properties or report a dynamics result from animation. A general USD viewer/importer and physics engine are separate capabilities; the included browser authors its own bounded scene.
