# Use the skill

Start with what you want the machine to do. You do not need to know the engineering terminology. Include whatever you know about load, size, speed, environment, available hardware, budget and whether this is one prototype or a product.

## Choose a working mode

| Mode | Example request | Useful output |
|---|---|---|
| Learn a concept | “Explain Laplace transforms using a motor example; I know basic calculus.” | Intuition, notation, small calculation and when to use it |
| Diagnose | “My axis rings after stopping; here are position/current logs.” | Competing causes, discriminating measurements, bounded fix/test sequence |
| Design | “Move a 2 kg camera smoothly over 0.5 m at 0.2 m/s.” | Requirements, mechanism/actuator options, budgets, control/sensing and evidence gaps |
| Simulate | “Write a browser model where I can change mass, damping and gains.” | Runnable 2D/3D code, live charts, equations, controls, exports and tests |
| Understand controls | “Compare root locus, Bode and Nyquist for this plant.” | Actual loop model, plotted methods, stability/performance interpretation and limitations |
| Implement | “Build a tested controller prototype for this MCU and driver revision.” | Verified pin/interface map, code/build/config, state machine and test plan |
| Manufacture | “Prepare 50 units from this tested prototype.” | Drawings/process/BOM/configuration, assembly/inspection/calibration and release records |
| Commercialise | “Who should buy this robot and can I make a margin?” | Ranked segments, customer evidence, cost/cash/pricing and pilot plan |

## A good project prompt

> Use Mechatronics Engineering. I am comfortable with basic algebra but new to controls. I need a small indoor wheeled robot to carry 5 kg over a flat floor, stop within a defined zone and run for two hours. I have these motors, encoders and controller revisions: [supply actual details]. Compare feasible architectures, explain the terms, calculate the first budgets, build a browser simulation and prepare a test/manufacturing/configuration plan. Label assumptions and ask only questions that change the next decision.

Replace bracketed examples with your actual details; omit unknowns and let the skill identify them. Do not invent specifications to complete a form.

## From explanation to advanced solution

The intended progression is: understand the symptom/job → agree measurable success → choose a simple model → calculate and simulate → implement a bounded prototype → verify progressively → prepare manufacture/configuration → validate the intended use and commercial case. It need not run every step for a short question.

Ask for deeper topics when a problem needs them: “Show the Lagrangian derivation,” “Explain observability before choosing a sensor,” “Use MPC because actuator and state constraints dominate,” or “Use Monte Carlo with correlated parameter uncertainty.” The assistant should explain why the added complexity is useful and how its assumptions will be checked.

## Save the project state

Copy the [project dossier](../skills/mechatronics-engineering/assets/project-dossier-template.md) into your project. Keep requirements, assumptions, interfaces, revisions, configuration, tests and next decisions there. Carry this file and actual design assets when moving between Claude and ChatGPT. Installed skills provide the method; they do not automatically share every conversation or file across accounts.

## Understand the evidence labels

**Calculated** means equations were evaluated under stated inputs. **Simulated** means a model was run. **Software-tested** means software checks passed. **Bench/field-tested** require actual physical evidence. **Vendor-stated** is a sourced claim. **Certified** requires the appropriate certification evidence. An attractive 3D scene is not proof of torque, collision clearance, manufacturability or safety.

## Reuse the browser example

See [the browser guide](BROWSER-SIMULATION.md). Ask the assistant to change the actual model and geometry for your mechanism, retain parameter controls and charts, and run numerical plus UI checks. If a browser preview is unavailable, download the files and open the entrypoint locally. The bundle is self-contained and does not connect to a motor controller.

## Visual diagrams, thermal/fluid models and tool interfaces

- “Open the system builder and help me wire a position controller to a mass–spring plant. Explain each signal, check the units and compare two sample periods.”
- “Use the thermal preset for C=500 J/K, UA=5 W/K and a50 W heater at25°C. Show why the30 s temperature is27.5918°C and identify the evidence needed to justify a lumped model.”
- “Use the fluid-tank preset, then explain when its linear outflow assumption differs from a real orifice.”
- “Export this arm pose and recorded trajectory as OpenUSD. Check metres, Z-up, joint angles and time samples; list what is needed for physical motor sizing.”
- “Export plant node `plant` from my saved diagram to Scilab analysis, Xcos setup and a ROS2 simulation package. Identify the blocks omitted from this handoff and supply the native-runtime checks.”
- “Show my installed ATOMS modules and help choose a reviewed package for this specific Scilab task; distinguish installation from loading.”

Use the [interface workflow](../skills/mechatronics-engineering/references/toolchain-interfaces.md), [adapter kit](../skills/mechatronics-engineering/assets/interfaces/README.md), [thermal/fluid guide](../skills/mechatronics-engineering/references/thermal-fluid-systems.md) and [visual builder guide](../skills/mechatronics-engineering/references/system-builder.md).
