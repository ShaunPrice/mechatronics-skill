# Build a system by connecting simulation blocks

Use the [visual system builder](../assets/browser-lab/builder.html) to test a causal signal-flow model: each wire carries one numerical signal from a block's output to another block's input. This is the same broad block-diagram idea used by tools such as Xcos. The included editor is an original bounded simulator; it does not import Xcos files, execute Modelica, or solve arbitrary physical connector networks.

## Build the model before tuning it

Start with the engineering question, state variables, inputs, outputs, parameter units and acceptance measures. A wire means information flow; it does not automatically represent a shaft, electrical net, hydraulic pipe or conservation equation. Derive the force/current/energy balances first and express them as signal blocks. Keep the units beside the equations and parameter definitions; the editor does not infer or verify dimensional compatibility.

For a translating mechanism, m ẍ + b ẋ + k x = F has displacement x in metres, force F in newtons, mass m in kg, damping b in N·s/m and stiffness k in N/m. The mass–spring block encapsulates this equation. Connect a controller force command to the plant input and its displacement output to the controller measurement input. A reference position enters the setpoint input. A scope on position and one on force reveal tracking and actuator effort together.

A visual loop is not evidence of stability. Establish plausible physical values, limits and timing; compare against analytic cases and measurements. Do not turn an animation's apparent smoothness into a torque, current or structural rating.

## Editing and running

1. Open the builder from the main browser lab or open `builder.html` in the same local folder.
2. Start with the default feedback diagram. Run it, inspect the scope results, then reset before a comparison.
3. Drag a component from the palette to the canvas; the palette's click-to-add option also supports keyboard/touch workflows. Move a block by dragging its title/header, keeping the IN and OUT circles available for wiring.
4. Press and hold a block's **OUT** circle, drag the dashed wire preview onto the destination **IN** circle, then release when the input highlights teal. You can also click OUT, release, then click the input; Tab and Enter/Space activate the same buttons by keyboard. One input takes one wire; an output may feed several inputs. Select a block to inspect its parameter values and change them in the parameter editor.
5. Validate before running. Complete missing connections and resolve invalid parameters. Remove a connection before replacing it; remove unused nodes or connect their required inputs.
6. Set the sample period and duration. Run/pause/reset, inspect live scopes and the mechanical-state illustration, and save the diagram as JSON. Load only a diagram in this editor's schema; a JSON file is data, not executable code.
7. Compare runs by saving diagram versions and result exports with their settings. Editing starts a new experiment so a result cannot silently mix different models.

### If a wire will not connect

- Start at the **OUT circle**, not the block body or title. Dragging the title moves the block.
- Watch the connection message above the diagram: a free input highlights teal; an input that already has a driver is outlined red. Select the existing wire and choose **Remove wire** before replacing it. A rejected drop preserves existing connections.
- Release on empty space or press **Esc** to cancel a drag. Moving outside the canvas, losing pointer capture, or hiding the tab must not create a wire. A drop on another output is not a valid connection.
- On a touch screen, hold and move from OUT to IN, or use two separate taps. If a destination is off screen, scroll to arrange a visible route first; the drag gesture does not automatically scroll the diagram. The two-click/tap method lets you scroll between selecting OUT and the input.
- Teal means an input is unoccupied. The graph validator can still reject a connection that creates an algebraic loop. Read the reported reason; do not insert an artificial delay merely to dismiss it.

A quick check is **Constant = 3 → Gain = 2 → Scope**. Add and arrange these blocks, edit the two values, connect both wires, then run: every scope sample should equal **6**.

Use the visible interface labels as the authority for current controls and limits. The builder supports bounded node/wire counts and finite runs to keep a local browser responsive.

## Block library and applications

| Block | Meaning and example use | Main check |
|---|---|---|
| Constant | Fixed source, bias, operating point or disturbance | Define its signal unit |
| Step | Command change at a stated time | Initial/final values, step time and transient conditions |
| Sine | Periodic command/disturbance for response exploration | Frequency in Hz, amplitude and sample rate; do not alias a fast input |
| Sum | Combine two signed inputs, e.g. command minus measurement | Signs and matching units |
| Gain | y = K u, calibration or unit conversion | Gain units/sign and physical operating range |
| Saturation | Clamp signal to min/max | Limits reflect the actual modeled actuator/sensor; clipping alone does not model thermal/current dynamics |
| PID | Sampled error-based controller with filtered derivative, integral state and output bounds | Use the documented implementation, sample period, derivative behaviour and antiwindup; tuning is model-specific |
| Integrator | State accumulation, ẋ = u | Initial condition, signal/time units and integration accuracy |
| Unit delay | Previous sample value | One whole sample of delay; it changes the model and is not free numerical repair |
| First-order plant | τ ẏ + y = K u | Positive time constant, static gain and validity of the first-order approximation |
| Mass–spring–damper | Coupled position/velocity from applied force | Mass/damping/stiffness and initial state; linear lumped approximation |
| Scope | Record/plot a signal over time | Signal name/unit, initial conditions, limits and full timescale |

## More than one domain

**Thermal control:** from C_th Ṫ = P − (T−T_ambient)/R_th, use temperature rise θ = T−T_ambient. Then τ = R_th C_th and K = R_th in a first-order plant from power to θ. Add ambient temperature through a sum if displaying absolute temperature. Add heater saturation and a controller; this approximation omits spatial temperature gradients and nonlinear losses.

**A simple DC motor model:** electrical current obeys L i̇ = V − R i − K_e ω; shaft speed obeys J ω̇ = K_t i − b ω − τ_load. Build the two equations with sums/gains/integrators, or derive a justified reduced first-order speed model. Use voltage/current/torque units consistently and include limits. The model's inductance can create a fast timescale; a coarse sample interval may be unsuitable. A brushless drive needs its own commutation/current-control model when those effects matter.

**Two interacting axes:** several scalar state/plant blocks may share signals. Write the coupled equations explicitly and use gains/sums for cross terms. This can explore a small MIMO model, but the included builder does not automatically design a MIMO controller or certify multivariable stability.

**Manufacturing flow:** continuous signal blocks are generally a poor fit for discrete jobs, setup, queues and resource contention. Use [manufacturing operations](manufacturing-operations.md) and a discrete-event model for those questions. Select the solver by the underlying mathematics.

## Algebraic loops and timing

A combinational cycle means an output depends immediately on itself through only direct-feedthrough blocks, e.g. a gain wired into its own input. Solving that requires an algebraic equation solver and may have no unique solution. The builder rejects this cycle. A physical plant's state, an integrator or a genuine modeled sample delay can break immediate dependence. Add a delay only when the hardware/model has that delay; otherwise simplify the equations or use a suitable algebraic/DAE solver.

State outputs are read for the current sample; direct signal equations are evaluated in dependency order; state updates are then performed synchronously. Continuous plant blocks advance under held inputs while controllers update on the sample clock. Browser redraw frequency is separate from simulation time. Hidden tabs pause, and long frames are capped so resuming a tab does not create a huge integration step.

This is an explicit sampled coupling between blocks. Even if each plant block has an accurate internal step, a loop assembled from several blocks may change with the sample period. Halve the period and compare key outputs; repeat until the decision is insensitive within a stated tolerance. Resolve the fastest relevant time constant and controller dynamics. Overflow/nonfinite state should stop a run, not draw a falsely stable trace.

## Acceptance tests for a new diagram

- Constant → gain → scope must give the expected signed constant.
- A unit first-order plant with a unit step follows y(t) = 1 − exp(−t/τ) from zero initial state, under the stated gain/step timing.
- An unforced damped mechanical plant should lose energy; constant force at equilibrium yields x = F/k when k > 0.
- Check feedback sign by the initial correction direction before tuning gains.
- Check actuator bounds and integrator behaviour under a large unreachable setpoint.
- Compare multiple coupled states with an independent equation implementation and timestep refinement.
- Save/reload a diagram and reproduce the same run. Test missing inputs, duplicate connections and algebraic loops explicitly.

Use root locus/Bode/Nyquist in the [control lab](browser-simulation.md) when the loop matches its stated plant/controller family, or derive/implement analysis of the new diagram's actual linear model. The block builder does not automatically transfer arbitrary diagrams into those plots. For spatial scene export use the separate [OpenUSD workflow](openusd-workflow.md); a signal diagram JSON is not a USD scene.

## Deliver the user's idea as an experiment

Return the diagram JSON, equations and units, parameter sources, runnable browser files, expected results, recorded results, sample/convergence settings, and an explanation of what the result does and does not establish. Offer an extension only when a required physical effect cannot be represented by the existing blocks. For advanced stiff/contact/multibody or acausal models, export the equations/requirements into a suitable dedicated solver and verify the handoff.

## Related tool

[Scilab Xcos](https://www.scilab.org/software/xcos) is an established graphical dynamic-system modeler with its own libraries and file formats. Use its official documentation when a user needs its supported hybrid/acausal workflows. This repository implements its own smaller browser signal-flow editor and does not bundle Xcos.

## Included presets and model files

Choose PID feedback, Thermal heating or Linear fluid tank in **Example model**, then **Load selected example**. The heater preset implements C=500 J/K, UA=5 W/K, P=50 W and ambient25°C; it reaches27.5918178°C after30s from ambient. The tank has area0.05m², inflow0.001m³/s and linear outflow q=0.001h, giving τ=50s and level0.451188364m after30s from empty. This linear drain is a modeling assumption; it is not the square-root Torricelli orifice law.

Equivalent JSON files are under `assets/browser-lab/examples/` for loading and version control. The canvas scrolls horizontally and vertically to expose large diagrams. Parameter and timing changes commit immediately for valid input; an invalid active draft must be corrected before Run. Runs round up to a whole sample and report their effective final time.

For Scilab/Xcos and ROS2 handoff, save the model and use [toolchain interfaces](toolchain-interfaces.md). That adapter exports one supported plant with its equations and initial state; it does not convert the entire feedback diagram.
