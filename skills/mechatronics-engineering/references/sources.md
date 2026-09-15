# Sources and verification rules

Primary documentation entry points checked during preparation on **15 September 2026**. This is a curated learning and verification map, not a claim that every standard, device, package version or engineering solution has been validated. Explanations and worked examples in this skill are original synthesis; external sources retain their own licences.

## Engineering and computation

| Source | Use it for | Boundary |
|---|---|---|
| [Modern Robotics — Lynch and Park, chapter resources](https://modernrobotics.northwestern.edu/blog/) | Frames, kinematics, Jacobians, dynamics, motion/control and manipulation | Select the relevant chapter and conventions |
| [Modern Robotics — rigid-body dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-2-dynamics-of-a-single-rigid-body-part-1-of-2/) | Inertia matrices, body motion and Newton–Euler derivations | Check reference point and frame before applying equations |
| [MIT Underactuated Robotics — Tedrake](https://underactuated.mit.edu/) | Nonlinear dynamics, LQR, Lyapunov, optimisation, planning and learning | Proof assumptions and model scope matter |
| [MIT — fully actuated and underactuated systems](https://underactuated.mit.edu/intro.html) | Choosing appropriate dynamics/control formulations | Actuation rank and operating region affect applicability |
| [Python Control Systems Library](https://python-control.readthedocs.io/en/latest/) | Transfer functions, state space, plots and control analysis | Verify installed API/version and numerical conventions |
| [MathWorks Control System Toolbox](https://www.mathworks.com/help/control/index.html) | Bode, root locus, state space and controller workflows | Toolbox/licence availability is environment-specific |
| [MathWorks root locus design](https://www.mathworks.com/help/control/ug/root-locus-design.html) | Gain-dependent pole design and compensator exploration | An example model is not the user's plant |
| [SciPy solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) | ODE solvers, stiffness, tolerances and events | Solver success does not validate physical assumptions |
| [NIST measurement uncertainty](https://www.nist.gov/itl/sed/topic-areas/measurement-uncertainty) | Measurement models, uncertainty and propagation | Keep uncertainty distinct from tolerance and error |
| [NIST uncertainty budgets and sensitivity coefficients](https://www.itl.nist.gov/div898/handbook/mpc/section5/mpc56.htm) | Combining contributions through a measurement model | Correlation and sensitivity coefficients matter |
| [NIST process capability](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm) | Cp/Cpk and process-versus-specification interpretation | Establish process stability and appropriate distribution first |
| [Texas Instruments — motor driver current ratings](https://www.ti.com/lit/an/slva505a/slva505a.pdf) | Peak/continuous ratings, thermal and overcurrent limitations | Application note is guidance; use the exact part datasheet/layout |
| [ROS 2 QoS concepts](https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html) | Publisher/subscriber policy compatibility and communication tradeoffs | Humble page documents concepts, not a recommendation to select that distribution |
| [ROS 2 interfaces](https://docs.ros.org/en/ros2_documentation/rolling/Concepts/Basic/Interfaces-Topics-Services-Actions.html) | Topics, services and actions | Verify the target distribution and package versions |
| [Protolabs manufacturing design tips](https://www.protolabs.com/resources/design-tips/) | CNC, additive and moulding design considerations | Supplier-specific capabilities; obtain a quote/DFM review |
| [Protolabs injection moulding tolerances](https://www.protolabs.com/resources/blog/injection-molding-tolerances/) | Tooling/material/process effects on moulded dimensions | Do not transfer one resin's shrinkage/tolerances to another |
| [NASA — Designing Safe Batteries](https://www.nasa.gov/wp-content/uploads/2024/01/battery-failure-databank.pdf) | Battery failure mechanisms and design/test perspective | Aerospace context is not consumer certification |
| [MDN Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) | Browser drawing, scenes and chart rendering | A renderer is not a physics engine |
| [MDN requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame) | Display scheduling and background behaviour | Keep the numerical/control clock independent |

## Business and product delivery

- [MIT manufacturing/supply-chain queueing notes](https://ocw.mit.edu/courses/15-763j-manufacturing-system-and-supply-chain-design-spring-2005/22f4805864deb06eee85acc1601463ba_queueing_note.pdf): M/M/1, Little's law and a general-arrival/service approximation; check assumptions before applying to a production line.
- [Lean Enterprise Institute — Kanban](https://www.lean.org/lexicon-terms/kanban/): production and withdrawal signals in pull systems; pair sizing calculations with measured replenishment behaviour.
- [NIST — proportions control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm): binomial p-chart basis and control limits; data and subgroup assumptions matter.
- [NIST — control charts](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc31.htm): process monitoring, baseline and limits. Use the [manufacturing operations guide](manufacturing-operations.md) for original calculations and decision routing.

- [business.gov.au — start-up cost planning](https://business.gov.au/planning/new-businesses/calculate-the-start-up-costs-of-your-business): a starting structure for setup/operating costs and planning. Adapt to the actual business and currency.
- [business.gov.au — product labelling](https://business.gov.au/products-and-services/product-labelling): an Australian applicability starting point. Determine product type, intended use and all intended sales jurisdictions before identifying obligations.

For exact conformity obligations, retrieve current applicable documents from the regulator or standards publisher, and competent specialist interpretation where needed. Candidate families may include machinery risk assessment, machinery electrical systems, safety-related controls, industrial robots/mobile robots, electrical/EMC/radio, battery transport, pressure, aviation/marine, consumer and sector-specific requirements. These categories are a research route, not a completed standards assessment; no clauses or certification are asserted here.

## Platform packaging

- [Anthropic — create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills): YAML metadata, resource folders, ZIP packaging and testing.
- [Claude Code — skills](https://code.claude.com/docs/en/skills): personal/project skill discovery and invocation.
- [OpenAI — build skills](https://learn.chatgpt.com/docs/build-skills): Agent Skills format, local discovery and ChatGPT/Codex surfaces. Availability can vary by surface and workspace.
- [OpenAI — create and edit GPTs](https://help.openai.com/en/articles/8554397-creating-a-gpt): instructions versus knowledge and preview testing.
- [OpenAI — Projects](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt): shared project files and instructions.
- [MIT licence text and summary](https://choosealicense.com/licenses/mit/): permissive reuse terms; see the package/repository LICENSE for the operative notice.

## How the skill should cite and refresh

For a consequential specification, quote the exact device/software/document revision and section/page, retrieval date and applicable operating conditions. Distinguish manufacturer claim, measured evidence and inference. Re-check prices, availability, firmware interfaces, software support, laws/standards and platform installation steps at use time. If a source is inaccessible, say what was not checked and proceed with a provisional design or targeted information request; do not invent a citation or treat search snippets as a device datasheet.

## OpenUSD scene interchange

- [OpenUSD introduction](https://openusd.org/release/intro.html): stages, layers, prims and composition.
- [Transformations and sampled animation](https://openusd.org/release/tut_xforms.html): transform ordering, rotations and time samples.
- [UsdPhysics schema](https://openusd.org/release/api/usd_physics_page_front.html): physics data and units; match the consumer's supported release/features.
- [OpenUSD toolset](https://openusd.org/release/toolset.html): usdview, usdcat and validation tooling; SDK builds differ.
- [NVIDIA units tutorial](https://docs.nvidia.com/learn-openusd/latest/beyond-basics/units.html): stage units and asset conversion.

Pointers verified on 15 September 2026. This skill bundles an original USDA authoring implementation, not the OpenUSD runtime or third-party models.

## Heat transfer, thermodynamics and fluids

- [MIT heat-transfer course](https://ocw.mit.edu/courses/2-051-introduction-to-heat-transfer-fall-2015/): conduction, convection, radiation and transient models.
- [MIT thermal-energy syllabus](https://ocw.mit.edu/courses/16-050-thermal-energy-fall-2002/pages/syllabus/): energy and thermodynamics.
- [NASA Navier–Stokes introduction](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/navier-strokes-equation/) and [Bernoulli introduction](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/bernoullis-equation/): governing equations and assumptions.
- [DOE fluid-flow handbook](https://www.energy.gov/ehss/articles/doe-hdbk-10123-92) and [pump-system sourcebook](https://www.energy.gov/sites/prod/files/2014/05/f16/pump.pdf): flow, head losses, system curves and pump selection.

These are educational sources, not component ratings or current certification requirements. URLs checked 15 September 2026; refresh actual fluid/material properties, pump curves and cell temperature envelopes for the design.
