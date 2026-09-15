# Materials, manufacturing and assembly

Use this guide when selecting a physical construction or turning a prototype into repeatable units. Material name alone is insufficient: specify grade, condition, process, geometry, finish and environment. Start from loads, temperature, lifetime, fluid/chemical exposure, wear, electrical needs, mass, volume and available processes.

## Materials selection

| Family | Useful properties and applications | Check before choosing |
|---|---|---|
| Steels, stainless steels and cast irons | Stiff structures, shafts, gears, wear surfaces | Grade/heat treatment, fatigue, corrosion mechanism, density, weld distortion; stainless is not universally corrosion-proof |
| Aluminium/magnesium alloys | Low-mass housings/frames and heat paths | Lower elastic modulus than steel, fatigue, galvanic couples, thread wear and machining/finishing hazards |
| Copper/brass/bronze/titanium | Conductors, bearings, marine or mass-sensitive structures as appropriate | Conductivity/strength/cost tradeoff, galling, galvanic effects and fabrication difficulty |
| Thermoplastics: ABS, PC, PA, POM, PE, PEEK etc. | Enclosures, insulation, sliding parts and lightweight mechanisms | Creep, moisture uptake, UV, temperature, chemical compatibility, flammability requirements and anisotropy |
| Elastomers: silicone, EPDM, nitrile, FKM etc. | Seals, compliance, vibration isolation | Fluid-specific compatibility, compression set, swelling, permeability and temperature; use compound-specific data |
| Ceramics and glasses | Wear, insulation, high temperature, optical windows | Brittleness, impact/thermal shock, machining, dielectric properties and flaw-sensitive strength |
| Fibre composites: carbon/glass/aramid | High directional stiffness-to-mass, shells and arms | Layup, fibre direction, joints, delamination, moisture, inspection; carbon conducts electricity and can cause galvanic corrosion |
| Adhesives, coatings and sealants | Bonding, corrosion protection, sealing and surface function | Surface preparation, cure process, bond-line thickness, peel versus shear, ageing, reparability and compatibility |

Use an Ashby-style process: translate the need into constraints and an objective, screen candidates, rank by a relevant property index, then verify supplier/process data. A stiffness-limited beam and a strength-limited tie rod have different selection criteria. Obtain certified material data when the application requires it; handbook numbers are initial estimates, not batch certification.

Strength prevents yielding/failure; stiffness limits deflection. Hardness, toughness, fatigue strength, wear and corrosion resistance are distinct. Use stress concentration and fatigue loading spectra at fillets/holes/joints. Creep matters in polymers, hot metals and sustained clamping; a print that survives one pull may relax over weeks. Thermal expansion mismatches can bind guides or preload bearings as temperature changes.

## Tribology and lubrication

Tribology covers friction, wear and lubrication. Identify contact pressure, sliding/rolling speed, temperature, cleanliness, water and maintenance interval. Select dry/boundary/mixed/hydrodynamic or elastohydrodynamic regimes as appropriate. Use oil viscosity at operating temperature, grease base oil/thickener compatibility and manufacturer relubrication guidance; NLGI grade describes grease consistency, not viscosity. Check seal/polymer compatibility, food/environmental requirements and grease mixing restrictions. More grease can increase churning and heat. Design access, exclusion seals, drains and a clean replacement process. Validate wear, torque/drag and temperature over a representative duty cycle.

For bearings/gears, check load spectrum, misalignment, lubrication, contamination, preload and life calculation assumptions. Catalogue bearing fatigue life does not include every failure mode. Belt tension, gear backlash and screw preload affect friction, resonance and controller behaviour.

## Battery chemistry and integration

Select a qualified cell/pack and charger using the actual datasheet and intended product requirements. Compare chemistry families by usable energy, power, temperature, cycle/calendar life, cost, mass and fault behaviour. Lithium-ion subfamilies (including LFP and nickel-rich chemistries) need different voltage limits and charging profiles; “lithium” is not a charger specification. Lead-acid, NiMH and sodium-ion may fit different cost/environment/supply needs. Do not infer safe operation from chemistry reputation.

Specify series/parallel configuration, cell matching, BMS functions, balancing, current limits, fuse/disconnect, temperature sensing, enclosure/venting, vibration restraint, connector interlocks and service approach. BMS presence does not establish product safety. Account for cold/hot charging restrictions, ageing, usable state-of-charge window, pack voltage sag and regeneration. Procurement/transport obligations are jurisdiction and product dependent; obtain current evidence from the supplier and the relevant authority.

Example: a nominal 24 V, 10 Ah battery represents about 240 Wh nominal. With an assumed 80% usable energy fraction and 90% conversion efficiency, a constant 60 W load would run about 240×0.8×0.9/60 = 2.88 h. Real runtime requires the load cycle, discharge curve, temperature, cell age and cut-off policy. Neither nominal Ah nor this estimate demonstrates mission endurance.

## Manufacturing method selection

| Process | Best starting use | Design-for-manufacture questions |
|---|---|---|
| FDM/SLA/SLS additive | Iteration, complex low-volume parts and fixtures | Orientation/anisotropy, supports, shrinkage, post-cure, porosity, creep and test coupons |
| CNC milling/turning | Accurate functional parts at low/medium volumes | Tool access, internal corner radii, workholding, stock, setups, thin walls and deburring |
| Laser/waterjet cutting and sheet forming | Plates, guards, brackets/enclosures | Kerf, heat affected edge, bend radius/allowance, minimum feature and edge finish |
| Casting/moulding/injection moulding | Repeated production with tooling economics | Draft, parting, gates, uniform walls, sink/warpage, shrinkage, inserts and tooling lead time |
| Welding/brazing/bonding | Frames, sealed joints and mixed constructions | Joint prep, access, sequence, distortion, heat effects, inspection and repair |
| Composite layup/pultrusion | Directional structures and shells | Ply schedule, cure, tooling, voids, inserts, cutting dust and nondestructive inspection |
| PCB/harness assembly | Repeatable electrical production | Component availability, placement/reflow constraints, test access, strain relief and traceable assembly |

For cutting/machining, choose process data from the tool and material supplier, machine rigidity and actual setup. Calculate surface speed, spindle speed and chip load consistently; do not prescribe a universal feed/speed. Explain dry versus coolant machining compatibility and required chip/dust control for the actual material. Never output machine-ready G-code without stock, tooling, machine/postprocessor, work coordinates, fixtures and simulation/verification appropriate to the job. A geometry preview does not prove collision-free cutting.

## Tolerances, metrology and joints

Establish functional datums before dimensions. Use geometric dimensioning and tolerancing (GD&T) when form/orientation/location relative to datums matter. Reference the chosen drawing standard and edition; do not mix conventions silently. Define fit, allowance, surface texture, finish/coating thickness and inspection condition. Use worst-case stack-ups for guaranteed limits; use root-sum-square/statistical methods only with justified distributions, independence and capability. Thermal, compliance and calibration errors also consume the positioning budget.

Select fasteners for clamp load, joint stiffness, fatigue, environment and service. Installation torque depends on friction and lubrication; a generic torque chart is not an engineered preload specification. Consider locking, thread engagement, inserts, access and assembly error-proofing. Dissimilar metals may need isolation; coatings and insulation change fits and heat paths.

Specify measurement method and uncertainty alongside each critical tolerance. A caliper is not a universal substitute for a CMM, surface instrument or calibrated fixture. Gauge repeatability and reproducibility (Gage R&R) separates equipment/operator variation from part variation; make the measurement system adequate before claiming process capability. See [commercial quality](commercial-delivery.md).

## Manufacturing release package

Deliver a controlled BOM with quantities, grades, approved alternates and make/buy decisions; native CAD when produced, neutral geometry (e.g. STEP) and dimensioned drawings; tolerances/finishes; PCB/harness outputs; assembly sequence with tooling, torque/adhesive/cure instructions tied to actual specifications; inspection/control plan; serial/lot traceability; firmware/config programming instructions; calibration fixture and procedure; end-of-line acceptance tests; packaging/transport/storage requirements; service/repair/spares and recycling/disposal guidance.

For each work instruction specify inputs, tools, fixture, critical settings, visual/measured acceptance, records and reaction to failure. Run a pilot with intended operators and suppliers, record touch time, yield, rework and nonconformances, then update drawings and costs. Supplier substitutions and engineering change orders require impact checks across mechanics, electronics, firmware, certification and stock already built.

Use the [project workflow](project-workflow.md) to connect released revisions to acceptance evidence. Vendor pages and material data in [sources](sources.md) are starting points; exact compatibility and process settings remain part-specific.
