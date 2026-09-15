# Validation report — version 0.1.0

Date: 15 September 2026. Original educational skill, code and diagrams reviewed by Codex with Claude contributions. This report distinguishes software evidence from physical or account-installation evidence.

## Executed checks

- Python engineering/control examples: 10 tests, including analytic oscillator agreement, energy/work balance, IK round trips, traction, cost/yield sensitivity, PID bounds and timestep convergence.
- Manufacturing operations: 7 tests for Little’s law, M/M/1 and Erlang C, unstable/zero-arrival queues, Kingman, Kanban rounding, capability and binomial confidence.
- Thermal/fluid helpers: 17 tests covering thermal balance/response, conduction, radiation, laminar pipe/Hagen–Poiseuille agreement, turbulent roughness, invalid/transitional regimes, hydrostatics, buoyancy, pump efficiency and nonfinite inputs.
- Browser control/OpenUSD core: 22 numerical/source checks for roots and residuals, PID/state cancellation, frequency response, margins, continuous pole stability, sampled response/convergence, saturation, mechanical energy, FK, numeric input ranges and USDA generation.
- Block editor solver: 18 checks for dependency ordering, analytic/convergence cases, PID feedback/bounds, independent plants, synchronous states, delay versus algebraic loops, deterministic reset, timing/work limits, input validation and the thermal/tank presets.
- Connector gestures: 12 checks for click/drag distinction, pointer ownership, cancellation, valid and invalid drops, unchanged rejected graphs, and a connected Constant 3 → Gain 2 → Scope result of 6.
- OpenUSD SDK 26.8: four generated stages parsed; seven world-position cases including sampled interpolation compared with independently calculated FK. Maximum difference 5.56×10⁻¹⁶ m. Metadata, hierarchy, timing, geometry and absence of physics schemas checked. The macOS SDK emitted an architecture cache-line warning; parsing and assertions completed successfully.
- Tool interfaces: 14 portable Python tests plus one executed native Scilab/Xcos test for state-space mapping, unsupported/ambiguous input rejection, schema parity with the browser, timing, generated Python/XML, reference responses and receipt-age watchdog. Node-based schema/preset parity was executed. A generated package pure-core smoke check applied 1 N then cleared it after the timeout. Native Scilab/Xcos and live ROS middleware checks are recorded separately below.
- Native skill-creator structure validator: passed. Final portable ZIP, internal links and generated manifest/source parity passed the package validator.

## Browser interaction evidence

The Codex in-app browser exercised locally served assets on loopback, with user permission. No public server was deployed.

- Main lab rendered 2D motion, root locus, Bode/Nyquist and perspective 3D geometry; default time response approached 1 m, 4 N and 2 J. Changing mass to 2 kg and target to 0.5 m produced the corresponding 0.5 m / 2 N response.
- Numeric input validation was fixed after real-browser testing exposed min/step mismatches. Invalid negative mass reports an error; valid arbitrary in-range values update the model.
- Disabling integral/derivative removes their unused states from the displayed pole calculation. 3D joint motion updates coordinates/chart; zoom and OpenUSD pose/animation export controls were exercised.
- A narrow viewport stacked the controls and kept the inspected main/3D content bounds within the viewport; the normal viewport was restored.
- Builder palette-to-canvas drag, click-to-add, port wiring, missing-input validation, run/reset and timing controls were exercised. Real-browser testing exposed change-event-only parameter edits; edits now commit on input and preserve focused fields.
- A custom Constant 3 → Gain 2 → Scope diagram displayed 6.000. Thermal and tank presets completed 30 simulated seconds and displayed 27.592°C and 0.451 m; independent engine runs yielded 27.59181779318282°C and 0.4511883639059708 m.
- Both generated standalone HTML pages were served and opened in the browser. The packaged thermal model reached 27.592°C, cross-page navigation worked, and the packaged 3D/OpenUSD controls loaded without reported JavaScript errors.
- Diagram, result JSON/CSV and USDA download handlers were clicked without reported JavaScript errors. Generated content was checked separately by numerical/package/OpenUSD tests. This does not claim a file-picker round trip or every browser/OS combination was tested.
- After the connector interaction was improved, actual mouse drags connected Constant OUT → Gain IN and Gain OUT → Scope IN. Occupied inputs rejected extra wires; empty drops and Escape cancelled without changing the graph. Removing/recreating a wire with two clicks and keyboard Enter both worked. The completed run produced 301 samples over 3 s and a scope value of 6.000, with no reported JavaScript errors. Touch gestures and automatic scrolling during a wire drag were not tested; wire dragging does not implement automatic canvas scrolling.
- Documentation screenshots and the captioned MP4 record the running browser. Capture intervals and edited scene cuts are documented in [recording metadata](../docs/media/recording.json). The local HTML player loaded, played and displayed English captions without reported JavaScript errors. These are recordings of software simulation, not generated depictions or physical hardware footage.

## Claude collaboration and behaviour tests

Claude drafted mathematics, mechanics, controls, topic routing, OpenUSD and thermal/fluid content; Codex reviewed and integrated the actual text. Review corrected frame-force signs, inertia/energy assumptions, phase-space/transform statements, controller-analysis limits and overbroad thermal/fluid operating claims.

Claude tested overhead-actuator and commercial scenarios; a targeted overhead retest followed corrections to the instructions. Claude also answered OpenUSD/motor-sizing and manufacturing-queue/yield prompts. Independent Codex forward tests covered aliasing, rotating frames and unreachable IK. See [the scenario record](SCENARIOS.md) for prompts and acceptance criteria.

Claude independently performed a static review of the block engine. It identified low-severity timing/reporting issues; the final engine uses one integer step count, labels downstream blocks affected by algebraic loops and rejects reserved prototype identifiers. This was static review, not a claim that Claude executed the JavaScript tests. No broad Claude-versus-Codex performance/cost comparison was performed.

## Interpretation limits

The main 2D axis is a sampled PID/lumped dynamic model; its root/frequency plots are an ideal continuous-time analysis. The 3D arm and its USDA exports are kinematic, with no contact, mass/inertia or joint-drive dynamics. The visual builder is a scalar signal-flow simulator, with explicit sampled coupling and model limits; it does not implement Xcos import, acausal physical-network solving, automatic unit checking or CFD.

The interface kit transfers one supported physical plant; it does not convert an entire controller diagram. External simulator import requires its actual environment. No physical machine, safety function, manufacturing process, regulatory approval or live hosted Claude/ChatGPT installation has been validated by these repository tests.

## Native Scilab, Xcos and ATOMS

Scilab 2026.1.0 on macOS executed the final exported scripts in an isolated profile with user startup and ATOMS autoload disabled. The [sanitized native results](scilab-xcos-results.json) include the exact model parameters and comparison results.

| Model, unit input from t=0 | Scilab maximum output difference vs Python RK4 | Xcos maximum output difference vs Python RK4 |
|---|---|---|
| Mass–spring, m=1 kg, b=2 N·s/m, k=4 N/m, zero initial state | 6.3433×10⁻¹⁰ m | 2.4859×10⁻⁷ m |
| First order, gain=2 K/W, tau=0.5 s, initial rise=3 K | 3.1721×10⁻⁸ K | 1.1420×10⁻⁶ K |

Both examples used dt=0.01 s over 2 s. Xcos recorded 200 samples from 0 to 1.99 s; the event at the exact final time was excluded, and comparisons used matching recorded times. The mass–spring Scilab state difference was at most 1.5661×10⁻⁹ in the corresponding state units.

The native builder created recording and scope diagrams. Java-enabled `-nw` Scilab saved and reloaded both `.zcos` variants for both models. Replaying each saved recording diagram produced the same output samples as its original native run (maximum difference 0). CLI `-nwni` supports batch simulation but disables `.zcos` serialization. Interactive scope rendering was not tested.

An isolated-profile ATOMS inventory returned an empty list. No module download or loader was executed. This is evidence about the inspected profile, not a claim that every possible user profile is empty.

The optional native unittest discovers `scilab-cli` or uses `SCILAB_CLI`; it checks both plant responses with a bounded runtime. CI explicitly skips this optional check when Scilab is absent. Native runtime evidence is separate from portable CI checks.

## Installed ROS 2 Docker environment

The [ROS 2 Docker guide](../integrations/ros2-docker/README.md) records the reusable `mechatronics-ros2-test` container, official image digest, clean-build procedure and start/test/stop commands. It was left installed and stopped after testing. Runtime networking was disabled, with no host mounts, published ports or device mappings.

Colcon successfully built one generated `mechatronics_sim` package on Linux arm64 / ROS 2 Jazzy. Seven checks exchanged actual middleware topics between separate processes: metadata/state, positive motion under 1 N, publisher-stop watchdog, NaN rejection, out-of-envelope rejection, pause/resume clock separation, and integer sample timestamps. See the [runtime report](../integrations/ros2-docker/evidence/ros2-topic-test.json) and [installation record](../integrations/ros2-docker/evidence/installation.json).

The probe received 381 states. Input became zero approximately 0.508 s after the last publish with a configured 0.5 s watchdog. A 0.784 s received-message wall-time gap advanced the numerical clock by 0.01 s. The final exporter produced nine ROS package files byte-identical to the input used for the live container test. The bounded test ended at 3.89 simulated seconds after its checks; it does not claim a complete live 20-second run, hardware operation or hard-real-time guarantees.

## Reproduce

```sh
python3 -m unittest discover -s skills/mechatronics-engineering/scripts -p 'test_*.py' -v
node skills/mechatronics-engineering/scripts/test-browser-lab.cjs
node skills/mechatronics-engineering/scripts/test-block-engine.cjs
node skills/mechatronics-engineering/scripts/test-builder-connections.cjs
python3 scripts/build_packages.py
python3 scripts/validate_package.py
```

For the optional SDK integration check, install `usd-core==26.8` in a dedicated validation environment and run `python3 scripts/validate_openusd.py`. The SDK is not required to run either browser page.
