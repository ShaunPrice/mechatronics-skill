# Mechatronics Engineering Skill

A practical engineering companion for novices tackling advanced mechatronics and robotics. It teaches the right terminology while helping turn a problem into a model, design, runnable prototype, manufacturing/configuration package and commercial plan.

Built collaboratively with Claude and Codex. **MIT licensed.** The repository is private; the licence permits reuse by recipients but does not change repository visibility.

## Start here

- [Install for Claude or ChatGPT](docs/INSTALL.md)
- [Use the skill and example prompts](docs/USAGE.md)
- [Topics and how to apply them](docs/TOPICS.md)
- [Run the interactive browser simulator](docs/BROWSER-SIMULATION.md)
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
- Interfaces for selected-plant Scilab analysis, Xcos setup, ATOMS management and a ROS 2 simulation package.
- OpenUSD USDA export of robot geometry and recorded joint motion, plus guidance for external simulation handoff.
- Thermal/fluid guidance and calculations for cooling, heat transfer, pipe losses, pumps, buoyancy and CFD model selection.
- Queueing theory, Kanban, JIT and statistical quality calculations for production planning.
- Reusable instructions and code for generating browser simulations of new designs.

## Quick browser start

Open [skills/mechatronics-engineering/assets/browser-lab/index.html](skills/mechatronics-engineering/assets/browser-lab/index.html) from your downloaded/cloned local folder. GitHub displays source rather than running HTML; download the repository or use the generated standalone HTML from `dist/`.

No account, API key, CDN, server or hardware connection is needed for the browser lab. Its 3D arm is a kinematic model; the sampled axis and continuous control-analysis plots have distinct stated assumptions. See [the browser guide](docs/BROWSER-SIMULATION.md).

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
```

## Packaging and maintenance

The source of truth is `skills/mechatronics-engineering/`. Run `python3 scripts/build_packages.py` to regenerate the skill ZIP, hosted ChatGPT knowledge/templates and standalone browser page; run `python3 scripts/validate_package.py` to check the package and internal links. `dist/` is generated and ignored by Git; build it after cloning. The ChatGPT integration files are committed for direct download and regenerated from source where appropriate.

This is an engineering guidance and prototyping skill. It distinguishes assumptions, calculations, simulations, software tests and physical evidence. It does not claim that a generated design is commissioned or certified, or that publishing these files installs the skill into any account. [Primary sources](skills/mechatronics-engineering/references/sources.md) explain where to verify device, software and market-specific details.

## Licence

[MIT](LICENSE), copyright 2026 Shaun Price. Original code and documentation are covered by this licence. Linked third-party materials retain their respective terms. No third-party manuals, models or runtime libraries are bundled.
