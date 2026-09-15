# Mechatronics Engineering Skill

A practical engineering companion for novices tackling advanced mechatronics and robotics. It teaches the right terminology while helping turn a problem into a model, design, runnable prototype, manufacturing/configuration package and commercial plan.

Built collaboratively with Claude and Codex. **MIT licensed.** The source, documentation and downloads are public. The MIT licence permits reuse, modification and redistribution under its terms.

## Start here

- [Download the Claude .skill bundle](https://github.com/ShaunPrice/mechatronics-skill/releases/download/v0.1.0/mechatronics-engineering-0.1.0.skill)
- [Install for Claude or ChatGPT](docs/INSTALL.md)
- [Use the skill and example prompts](docs/USAGE.md)
- [Topics and how to apply them](docs/TOPICS.md)
- [Run the interactive browser simulator](docs/BROWSER-SIMULATION.md)
- [Screenshots and recorded walkthrough](docs/WALKTHROUGH.md)
- [Scilab, Xcos, ATOMS and ROS 2 interfaces](skills/mechatronics-engineering/references/toolchain-interfaces.md)
- [ROS 2 Docker test environment](integrations/ros2-docker/README.md)
- [Validation and known limits](validation/REPORT.md)
- [Main skill](skills/mechatronics-engineering/SKILL.md)

## What it delivers

- Plain-language explanations linked to precise mechanical, electrical, mathematical and manufacturing terms.
- Method selection: when to use a technique, inputs needed, outputs produced, assumptions and checks.
- Requirements, architecture, sizing, controls, sensing, embedded systems, robotics, materials, manufacture and commissioning guidance.
- Costing, financing, new product development, quality, sales, marketing and lifecycle support.
- An editable project dossier and original worked examples.
- An offline browser workbench with parameter controls, 2D dynamics, a 3D kinematic arm, live charts, root locus, Bode and Nyquist explanations.
- A drag-and-drop block editor for custom signal-flow systems, with feedback wiring, editable parameters and live scopes.
- Interfaces for selected-plant Scilab analysis, native Xcos diagrams, ATOMS management and a ROS 2 simulation package, with a reproducible Docker test environment.
- OpenUSD USDA export of robot geometry and recorded joint motion, plus guidance for external simulation handoff.
- Thermal/fluid guidance and calculations for cooling, heat transfer, pipe losses, pumps, buoyancy and CFD model selection.
- Queueing theory, Kanban, JIT and statistical quality calculations for production planning.
- Reusable instructions and code for generating browser simulations of new designs.

## Quick browser start

Open [skills/mechatronics-engineering/assets/browser-lab/index.html](skills/mechatronics-engineering/assets/browser-lab/index.html) from your downloaded/cloned local folder. GitHub displays source rather than running HTML; download the repository or use the generated standalone HTML from `dist/`.

No account, API key, CDN, server or hardware connection is needed for the browser lab. Its 3D arm is a kinematic model; the sampled axis and continuous control-analysis plots have distinct stated assumptions. See [the browser guide](docs/BROWSER-SIMULATION.md).

## See the workbench

**[Watch or download the recorded browser demonstration (MP4)](docs/media/browser-workbench-demo.mp4)** · [Open the local video player](docs/watch-workbench.html) · [Read the illustrated walkthrough](docs/WALKTHROUGH.md)

GitHub may display a relative video link as a file/download rather than an inline player. After cloning or downloading the repository, open `docs/watch-workbench.html` for playback with controls and an English captions track. The recording uses real browser captures with cuts between scenes and no audio. It shows software simulation, not hardware operation. All media is stored in this repository.

### Tune the model and inspect its response

![Browser workbench with mass, damping, stiffness and PID inputs beside the mass–spring–damper animation, Run and Reset controls, and response chart.](docs/media/workbench-dynamics.jpg)

Edit parameters with their displayed units, run the sampled controller, and compare position with the force it requires. The [control-methods walkthrough](docs/WALKTHROUGH.md#2-read-the-control-analysis) explains the linked root-locus, Bode and Nyquist views.

### Explore a spatial robot arm

![3D robot kinematics view with editable joint angles and link lengths, an orbitable arm scene, end-effector coordinates and a live position trace.](docs/media/workbench-3d.jpg)

Change posture or geometry, run the joint demonstration, then export the pose or recorded motion as OpenUSD. This arm view computes kinematics; it does not model torque or contact dynamics.

### Connect a system from blocks

![Block library and a connected Constant 3 to Gain 2 to Scope diagram, with labeled IN/OUT ports, wire instructions and parameter inspector.](docs/media/system-builder.jpg)

Drag or click to add blocks. To wire them, drag an **OUT** circle onto an **IN** circle, or click OUT then IN; a dashed preview and highlighted inputs guide the connection. Edit parameters and run. Start with PID feedback, thermal heating or a linear fluid-tank example; save model JSON to repeat the experiment.

## Local calculations

Python 3.9+; standard library only:

```sh
python3 skills/mechatronics-engineering/scripts/engineering_calcs.py --demo
python3 skills/mechatronics-engineering/scripts/manufacturing_calcs.py --demo
python3 skills/mechatronics-engineering/scripts/thermal_fluid_calcs.py --demo
python3 skills/mechatronics-engineering/scripts/control_lab.py --out work/control-lab
python3 -m unittest discover -s skills/mechatronics-engineering/scripts -p 'test_*.py' -v
```

The browser numerical checks use Node.js with no npm dependencies:

```sh
node skills/mechatronics-engineering/scripts/test-browser-lab.cjs
node skills/mechatronics-engineering/scripts/test-block-engine.cjs
node skills/mechatronics-engineering/scripts/test-builder-connections.cjs
```

## Packaging and maintenance

The source of truth is `skills/mechatronics-engineering/`. Run `python3 scripts/build_packages.py` to regenerate the Claude `.skill` bundle, equivalent portable ZIP, hosted ChatGPT knowledge/templates and standalone browser pages; run `python3 scripts/validate_package.py` to check both archives, release checksums and internal links. `dist/` is generated and ignored by Git; build it after cloning, or download the packaged files from the repository’s [Releases page](https://github.com/ShaunPrice/mechatronics-skill/releases). The ChatGPT integration files are committed for direct download and regenerated from source where appropriate.

This is an engineering guidance and prototyping skill. It distinguishes assumptions, calculations, simulations, software tests and physical evidence. It does not claim that a generated design is commissioned or certified, or that publishing these files installs the skill into any account. [Primary sources](skills/mechatronics-engineering/references/sources.md) explain where to verify device, software and market-specific details.

## Licence

[MIT](LICENSE), copyright 2026 Shaun Price. Original code and documentation are covered by this licence. Linked third-party materials retain their respective terms. No third-party manuals, models or runtime libraries are bundled.
