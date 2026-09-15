# OpenUSD for Mechatronics: Kinematic Interchange and Physics Description

OpenUSD (Universal Scene Description) is a scene description, composition and interchange system, originally developed at Pixar and now widely used in robotics visualisation and industrial digital-twin pipelines. It lets several tools contribute non-destructively to one 3D scene. It is not a physics solver, a CAD kernel or a universal file converter: it *describes* scenes, and compatible applications consume the data for rendering or simulation. Retain the appropriate CAD and manufacturing outputs for fabrication. Keep that separation in mind for every claim about what a USD file "does" (see the [OpenUSD introduction](https://openusd.org/release/intro.html)).

## Core data model

- **Stage**: the composed, in-memory view of a scene assembled from one or more layers. You open a stage; you edit layers.
- **Prim**: a node in the stage's namespace hierarchy with a type such as `Xform` (transform group), `Mesh` (tessellated geometry) or `Scope`. A robot arm typically becomes a tree of `Xform` prims (base, links), each carrying `Mesh` children.
- **Layer**: a file or resource holding *opinions* — authored values. Stronger layers override weaker ones, which is how teams collaborate without overwriting each other's files.
- **Attribute**: a typed, named value on a prim, e.g. `points` or `xformOp:rotateZ`. Attributes hold a single default and/or **time samples** — values keyed by time code, which is how joint animation is stored.
- **Relationship**: a named pointer from one prim to others, used for material binding and, in physics schemas, to state which two bodies a joint connects.

## File formats

`.usda` is human-readable text — ideal for reviewing, diffing and hand-inspecting an exporter's output. `.usdc` is the binary "crate" format — smaller and faster for large geometry. `.usd` may be either. `.usdz` is an uncompressed zip package bundling a scene with its textures for delivery (e.g. AR viewers); it is a distribution wrapper, not a different data model.

## Conventions: units, axes, time and angles

Interchange fails on conventions more often than on geometry. Declare them and check them on import ([units and conventions](https://docs.nvidia.com/learn-openusd/latest/beyond-basics/units.html)):

- **Linear units**: stage metadata `metersPerUnit`. UsdGeom uses a 0.01 m (centimetre) fallback if the stage has no authored linear-unit metadata — so declare it explicitly. This skill's exporter authors metres (`metersPerUnit = 1`).
- **Up axis**: `upAxis = "Z"` (the robotics/ROS convention, used by this exporter) or `"Y"` (common in content-creation tools).
- **Time**: `timeCodesPerSecond` plus `startTimeCode`/`endTimeCode` map time codes to seconds. Author timing explicitly for a reproducible handoff instead of relying on a consumer or schema fallback.
- **Angles**: rotation xformOps (`xformOp:rotateX/Y/Z` and Euler triples) are authored in **degrees**. Convert from radians at the boundary: deg = rad × 180/π.
- **Transforms**: each prim carries an ordered `xformOpOrder` of translate/rotate/scale/matrix ops; order matters, and ops compose child-under-parent down the tree. Time-varying joint motion is authored by time-sampling a rotate op ([transformations tutorial](https://openusd.org/release/tut_xforms.html)).

A one-line dimensional check catches most unit errors: pick a feature with a known drawing dimension — a 300 mm link — and confirm the imported points span 0.300 stage units at `metersPerUnit = 1`. A missed mm→m conversion is a factor of 1000. Renderers can hide it because everything scales together; physics cannot, because gravity and inertia do not rescale with your mistake.

## Composition: layers, references, payloads, variants

USD composes scenes rather than copying data. **Sublayers** stack whole layers by strength. A **reference** brings a component asset (one arm, one gripper) into an assembly many times without duplication. A **payload** is a reference whose loading can be deferred — useful when a cell layout contains heavy CAD-derived meshes you do not always need. **Variant sets** store named alternatives inside one asset — e.g. `gripper = {vacuum, twoFinger}` or `lod = {visual, collision}` — so a configuration choice is data, not a forked file. A practical asset structure keeps geometry, materials and (if authored) physics in separate layers composed by a small assembly layer, so a physics layer can be added later without touching exported geometry.

## CAD tessellation versus manufacturing solids

USD `Mesh` prims are tessellated approximations. Your CAD system's B-rep solid (STEP or native) remains the manufacturing authority: tolerances, threads, exact radii and mass properties live there. When you tessellate for USD, record the chordal tolerance; a coarse mesh that visibly facets a 40 mm cylinder may be fine for visualisation but wrong for clearance checks. For this workflow, keep CAD as the source of exact dimensions and use USD for visual/simulation proxies. A mesh-based additive workflow can be valid when its tessellation and process tolerances are specified; do not imply it retains the original parametric solid. Collision geometry usually needs its own simplified (often convex) meshes, distinct from visual meshes.

## URDF/ROS mapping

URDF describes a robot as a single-rooted tree of links (with inertials) and joints (with axes, limits, dynamics), in metres and radians. The natural mapping: link → rigid-body prim, visual/collision geometry → mesh children, joint → UsdPhysics joint prim relating two bodies, inertial → mass/inertia attributes. Three traps: radians (URDF) versus degrees (USD rotate ops); joint frames expressed differently (URDF joint origin versus USD local positions/rotations on each body); and URDF's strict tree topology versus USD's more general structure. Converters exist in several ecosystems, but fidelity varies by tool and version — verify a converted model's frames and inertias against the source rather than assuming any converter is complete.

## UsdPhysics: describing dynamics, not computing them

The [UsdPhysics schema](https://openusd.org/release/api/usd_physics_page_front.html) lets a stage *describe* physical properties that a downstream engine consumes; The USD scene/composition library does not itself advance rigid-body dynamics.

- **Rigid bodies**: PhysicsRigidBodyAPI describes a body; enabled and kinematic flags affect how an engine treats it. A physics scene sets gravity.
- **Collision**: applied per geometry prim; engines differ in supported approximations (convex hull, triangle mesh, primitives) — support is engine- and version-dependent.
- **Mass properties**: mass (kg), centre of mass, diagonal inertia with a principal-axes orientation. Author these from CAD with real material densities; otherwise engines estimate from geometry and default density.
- **Joints**: fixed, revolute, prismatic, spherical, distance and a general D6 form — each represented by a joint prim with body relationships, local frames and appropriate limits. A missing body relationship can represent the world where the schema permits.
- **Articulations**: mark a jointed chain for reduced-coordinate solving, usually the right choice for serial arms.
- **Drives**: per-joint actuation with target position/velocity, stiffness and damping — effectively a PD law, τ = kₚ(θ* − θ) + k_d(ω* − ω), capped by a maximum force; drive type, angular units, gearing and force/acceleration semantics must match the engine. Do not copy gains expressed per radian into a degree-based attribute without conversion.

Units need care: linear quantities follow stage units, mass follows a kilograms-per-unit convention, and referenced assets carrying different unit metadata must be reconciled stage-wide before simulation, not per file.

Vendor engines that consume UsdPhysics add extension attributes for solver settings, friction models and sensors. Treat all such extensions — and even which core schema features a given engine honours — as **version-dependent**; check the documentation for the specific engine release you run.

## Validation: what a scene proves and does not

A USDA file that loads and animates provides parsing/playback evidence, but can still contain incorrectly scaled geometry or wrong joint transforms. It does not establish that particular software is installed on someone else's machine, that hardware achieved the motion, or that physical behaviour is correct. Build evidence in steps:

1. **Static checks**: open in `usdview` and run validation tooling where your build provides it ([toolset](https://openusd.org/release/toolset.html) — tool availability depends on how USD was built or installed); confirm units, up axis and time metadata.
2. **Kinematic cross-check**: compute tool-frame world transforms with independent forward kinematics and compare against the composed USD transforms at several sampled times. Agreement validates the export, not the mechanism.
3. **Mass-property check**: compare authored mass/inertia against CAD mass properties.
4. **Simulation**: only after physics is authored, and label results *simulated*.
5. **Bench/field measurement**: physical evidence under the recorded load, configuration and test conditions; it does not automatically cover other conditions.

## Worked dimensional example

A link modelled as a solid aluminium rod, length L = 300 mm = 0.300 m, diameter 40 mm (r = 0.020 m), density ρ = 2700 kg/m³:

- Volume V = πr²L = π(0.020)²(0.300) ≈ 3.77 × 10⁻⁴ m³
- Mass m = ρV ≈ 1.02 kg
- Transverse inertia through the centre of mass: I = m(3r² + L²)/12 ≈ 1.02 × (0.0012 + 0.090)/12 ≈ 7.7 × 10⁻³ kg·m²

These are SI mass and transverse-inertia values appropriate to a metre/kilogram stage. Author all three principal moments and their orientation, including the axial moment I_axis = m r²/2, rather than treating one scalar as the full inertia tensor. These calculations describe an idealised shape; verified CAD mass properties for the actual part supersede them.

## When lighter formats suffice

One static part for printing or quoting: STL or STEP. A visual model for the web: glTF. A ROS-only robot description: URDF/Xacro directly. OpenUSD earns its complexity when you need layered multi-tool collaboration, configuration variants, time-sampled animation interchange, or a path toward a physics-described digital twin.

## Deliverable checklist

- [ ] `metersPerUnit`, `upAxis`, `timeCodesPerSecond` declared and stated in the handoff note
- [ ] A known dimension verified after import into the receiving tool
- [ ] `xformOpOrder` and frame conventions documented
- [ ] STEP/native CAD retained as manufacturing authority; tessellation tolerance recorded
- [ ] Visual and collision geometry separated
- [ ] If physics is authored: masses/inertias traced to CAD densities; joint limits traced to verified hardware data and drive gains to a documented model/tuning procedure
- [ ] Independent FK cross-check of sampled poses recorded
- [ ] Consuming engine name, version and honoured schema features recorded
- [ ] Evidence labels applied (exported / validated / simulated / bench-tested)

## Prompts that get useful work

- "Check this USDA header and tell me what units and axes a consumer will assume."
- "My arm export animates in tool X but is 1000× too large — walk me through the unit fix."
- "Author a UsdPhysics layer skeleton for this 3-DOF arm and list every value I must supply from CAD or datasheets."
- "Compare the exported tool-frame trajectory against forward kinematics at t = 0, 1 and 2 s."
- "Should this project use USD, glTF or URDF? Here is the toolchain."

## Sources

- [OpenUSD introduction](https://openusd.org/release/intro.html) — stage, prim, layer, composition; USD as scene interchange.
- [Transformations tutorial](https://openusd.org/release/tut_xforms.html) — xformOps and time-sampled animation.
- [UsdPhysics schema](https://openusd.org/release/api/usd_physics_page_front.html) — rigid bodies, mass/inertia, joints, articulations; physics data consumed by an engine; unit reconciliation.
- [Toolset](https://openusd.org/release/toolset.html) — usdview, usdcat and validation tools; availability varies by build.
- [Units and conventions](https://docs.nvidia.com/learn-openusd/latest/beyond-basics/units.html) — metersPerUnit, up axis, time and mass conventions.


## Use the browser export now

Open the included browser workbench's **3D robot kinematics** view. Adjust link lengths and joint angles, then export the current pose as `.usda`. Run the joint demonstration to record a path and export its animation. The root is `/Robot`; the tool origin is `/Robot/YawJoint/ShoulderJoint/ElbowJoint/Tool`. Yaw is a Z rotation; positive shoulder/elbow elevation uses negative USD Y rotations in this hierarchy. The export uses metre geometry, Z-up, degrees for rotate ops and 60 time codes per second; time code 30 means 0.5 s. The optional path curve is a static visual trace of the recorded tool positions.

No collision, mass, inertia, joints/drives or physics scene is authored. Before adding dynamic bodies, decide how to remove or disable prescribed animation on bodies the solver should move; otherwise transform animation and dynamics may compete. Keep a visual reference layer and a separately authored physics/configuration layer, recording which owns each body's motion.

With a compatible OpenUSD installation, open the exported file in `usdview`. In this repository, the optional `scripts/validate_openusd.py` check uses the OpenUSD Python SDK to parse generated examples and compare composed world transforms with independent FK. This does not require adding an OpenUSD runtime to the browser. General USD import, arbitrary CAD conversion and external-engine commissioning remain separate work.
