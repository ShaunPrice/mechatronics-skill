# Validation report — version 0.1.0

Date: 15 September 2026. Original educational skill, code and diagrams reviewed by Codex with Claude contributions. This report distinguishes software evidence from physical or account-installation evidence.

## Executed checks

- Python engineering/control examples: 10 tests, including analytic oscillator agreement, energy/work balance, IK round trips, traction, cost/yield sensitivity, PID bounds and timestep convergence.
- Manufacturing operations: 7 tests for Little’s law, M/M/1 and Erlang C, unstable/zero-arrival queues, Kingman, Kanban rounding, capability and binomial confidence.
- Thermal/fluid helpers: 17 tests covering thermal balance/response, conduction, radiation, laminar pipe/Hagen–Poiseuille agreement, turbulent roughness, invalid/transitional regimes, hydrostatics, buoyancy, pump efficiency and nonfinite inputs.
- Browser control/OpenUSD core: 22 numerical/source checks for roots and residuals, PID/state cancellation, frequency response, margins, continuous pole stability, sampled response/convergence, saturation, mechanical energy, FK, numeric input ranges and USDA generation.
- Block editor solver: 18 checks for dependency ordering, analytic/convergence cases, PID feedback/bounds, independent plants, synchronous states, delay versus algebraic loops, deterministic reset, timing/work limits, input validation and the thermal/tank presets.
- OpenUSD SDK 26.8: four generated stages parsed; seven world-position cases including sampled interpolation compared with independently calculated FK. Maximum difference 5.56×10⁻¹⁶ m. Metadata, hierarchy, timing, geometry and absence of physics schemas checked. The macOS SDK emitted an architecture cache-line warning; parsing and assertions completed successfully.
- Tool interfaces: 14 Python tests for state-space mapping, unsupported/ambiguous input rejection, schema parity with the browser, timing, generated Python/XML, reference responses and receipt-age watchdog. Node-based schema/preset parity was executed. A generated package pure-core smoke check applied1N then cleared it after the timeout; no ROS middleware was used.
- Native skill-creator structure validator: passed. Final portable ZIP, internal links and generated manifest/source parity passed the package validator.

## Browser interaction evidence

The Codex in-app browser exercised locally served assets on loopback, with user permission. No public server was deployed.

- Main lab rendered 2D motion, root locus, Bode/Nyquist and perspective 3D geometry; default time response approached1m,4N and2J. Changing mass to2kg and target to0.5m produced the corresponding0.5m/2N response.
- Numeric input validation was fixed after real-browser testing exposed min/step mismatches. Invalid negative mass reports an error; valid arbitrary in-range values update the model.
- Disabling integral/derivative removes their unused states from the displayed pole calculation. 3D joint motion updates coordinates/chart; zoom and OpenUSD pose/animation export controls were exercised.
- A narrow viewport stacked the controls and kept the inspected main/3D content bounds within the viewport; the normal viewport was restored.
- Builder palette-to-canvas drag, click-to-add, port wiring, missing-input validation, run/reset and timing controls were exercised. Real-browser testing exposed change-event-only parameter edits; edits now commit on input and preserve focused fields.
- A custom Constant3→Gain2→Scope diagram displayed6.000. Thermal and tank presets completed30 simulated seconds and displayed27.592°C and0.451m; independent engine runs yielded27.59181779318282°C and0.4511883639059708m.
- Both generated standalone HTML pages were served and opened in the browser. The packaged thermal model reached27.592°C, cross-page navigation worked, and the packaged3D/OpenUSD controls loaded without reported JavaScript errors.
- Diagram, result JSON/CSV and USDA download handlers were clicked without reported JavaScript errors. Generated content was checked separately by numerical/package/OpenUSD tests. This does not claim a file-picker round trip or every browser/OS combination was tested.

## Claude collaboration and behaviour tests

Claude drafted mathematics, mechanics, controls, topic routing, OpenUSD and thermal/fluid content; Codex reviewed and integrated the actual text. Review corrected frame-force signs, inertia/energy assumptions, phase-space/transform statements, controller-analysis limits and overbroad thermal/fluid operating claims.

Claude tested overhead-actuator and commercial scenarios; a targeted overhead retest followed corrections to the instructions. Claude also answered OpenUSD/motor-sizing and manufacturing-queue/yield prompts. Independent Codex forward tests covered aliasing, rotating frames and unreachable IK. See [the scenario record](SCENARIOS.md) for prompts and acceptance criteria.

Claude independently performed a static review of the block engine. It identified low-severity timing/reporting issues; the final engine uses one integer step count, labels downstream blocks affected by algebraic loops and rejects reserved prototype identifiers. This was static review, not a claim that Claude executed the JavaScript tests. No broad Claude-versus-Codex performance/cost comparison was performed.

## Interpretation limits

The main 2D axis is a sampled PID/lumped dynamic model; its root/frequency plots are an ideal continuous-time analysis. The 3D arm and its USDA exports are kinematic, with no contact, mass/inertia or joint-drive dynamics. The visual builder is a scalar signal-flow simulator, with explicit sampled coupling and model limits; it does not implement Xcos import, acausal physical-network solving, automatic unit checking or CFD.

The interface kit transfers one supported physical plant; it does not convert an entire controller diagram. Native Scilab 2026.1.0 numerical validation was subsequently performed: mass–spring maximum output difference6.3433×10⁻¹⁰ and state difference1.5661×10⁻⁹ versus the Python reference; a first-order case with nonzero initial state differed by3.1721×10⁻⁸. An isolated-profile ATOMS inventory returned an empty list without downloading modules. Native Xcos block definitions loaded; diagram execution and ROS container testing are tracked separately below. External simulator import requires its actual environment. No physical machine, safety function, manufacturing process, regulatory approval or live hosted Claude/ChatGPT installation has been validated by these repository tests.

## Reproduce

```sh
python3 -m unittest discover -s skills/mechatronics-engineering/scripts -p 'test_*.py' -v
node skills/mechatronics-engineering/scripts/test-browser-lab.cjs
node skills/mechatronics-engineering/scripts/test-block-engine.cjs
python3 scripts/build_packages.py
python3 scripts/validate_package.py
```

For the optional SDK integration check, install `usd-core==26.8` in a dedicated validation environment and run `python3 scripts/validate_openusd.py`. The SDK is not required to run either browser page.
