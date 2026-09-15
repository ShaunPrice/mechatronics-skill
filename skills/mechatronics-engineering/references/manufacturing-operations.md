# Manufacturing flow, queueing, Kanban, JIT and statistical quality

Use this guide to design and improve the production system around a mechatronic product: how work arrives, waits, gets built/tested, is replenished and is accepted. Pair it with [materials and manufacturing](materials-manufacturing.md), [commercial delivery](commercial-delivery.md) and [simulation](simulation-validation.md). A fast robot at one station can increase queues downstream without improving shipped output.

## 1. Map flow before buying automation

Draw a value-stream map from customer order to shipment, including suppliers, queues, fabrication, assembly, programming, calibration, test, rework and information flow. Record touch time, setup/changeover, uptime, yield, routing, transfer batch, available shift time, WIP and demand variability. Separate processing time from elapsed lead time; a part may receive 20 minutes of work but wait two days.

Find the constraint/bottleneck and analyse its usable capacity. Improve first-pass quality and downtime at the constraint before optimising a station that already waits. Use time studies with representative operators/conditions, ergonomic assessment and appropriate sample sizes. Distinguish planned breaks from unplanned losses when defining available time.

| Technique | When useful | Output and check |
|---|---|---|
| Standard work and visual management | Repeated assembly/test with operator variation | Sequence, standard WIP, critical settings and acceptance; verify usability and actual cycle variation |
| 5S and point-of-use storage | Searching, motion or missing tooling slows work | Organised accessible workspace and replenishment ownership; measure search/motion reduction |
| Poka-yoke | Repeated assembly/configuration errors | Keyed fixture/connector or validated error detection; challenge with realistic wrong parts/settings |
| SMED/changeover reduction | Small batches are blocked by long setup | Separate internal machine-stopped from external preparation; verify first-good-part setup time |
| Cellular layout and line balancing | Product families share routes/processes | Workstation grouping and task allocation under precedence/ergonomic constraints; check variability and walking |
| Heijunka/production levelling | Product-mix spikes destabilise supply | Feasible levelled sequence with stated buffers; account for setup and actual demand |
| CONWIP / drum-buffer-rope | System-wide WIP or constraint scheduling dominates | WIP release limit or constraint-paced schedule; measure throughput and starvation/blocking |
| Total productive maintenance / condition monitoring | Downtime at key equipment affects delivery | Failure/maintenance plan, spares and performance trend; validate sensors against actual failure mechanisms |

Takt time = available production time / required good units. It is the demand pace, not a measured station cycle time. Example: 420 available minutes and demand 280 good units imply takt = 1.5 min/unit. Balance work content and capacity including setup, yield, downtime and variability; average cycle time below takt alone may not prevent queues. OEE = availability × performance × quality using consistent definitions; do not double-count its losses when calculating capacity or costs.

## 2. Queueing mathematics

### Little's law: inventory, throughput and lead time

L = λ W, where L is average items in a defined system, λ its average throughput (items/time), and W mean time in that system. This relationship needs consistent boundaries and long-run flow balance; it does not require exponential arrival/service times. For the waiting queue alone, Lq = λ Wq. Separate waiting from service and count rework/scrap consistently. A growing unstable backlog does not have the steady finite averages assumed by a capacity calculation.

Example: 24 assemblies in a stable process with throughput 6 good assemblies/hour imply mean lead time 4 h only if the WIP and throughput populations/boundaries match. Little's law alone does not prove that arbitrarily removing inventory preserves throughput; it may starve the bottleneck.

### M/M/1: a useful baseline, not every factory

Assume Poisson arrivals rate λ, independent exponentially distributed service times with rate μ, one server, FIFO, unlimited queue and no abandonment. For ρ = λ/μ < 1:

- Utilisation ρ; mean number in system L = ρ/(1−ρ).
- Mean queue length Lq = ρ²/(1−ρ).
- Mean system time W = 1/(μ−λ).
- Mean waiting time Wq = ρ/(μ−λ), and W = Wq + 1/μ.

At λ = 6 parts/h and μ = 8 parts/h, utilisation is 75%, mean wait 0.375 h = 22.5 min, total time 0.5 h = 30 min, Lq = 2.25 and L = 3. Operating close to full utilisation can make waits very large under variability. If λ ≥ μ, this steady-state model is unstable; reject finite-wait outputs.

### M/M/c: pooled identical servers

Use for one queue feeding c identical independent exponential servers at μ each, with Poisson arrivals and ρ = λ/(cμ) < 1. Let a = λ/μ:

P0 = [Σ(n=0 to c−1) aⁿ/n! + aᶜ/(c!(1−ρ))]⁻¹.

Probability an arrival waits (Erlang C): Pw = [aᶜ/(c!(1−ρ))] P0. Then Wq = Pw/(cμ−λ), W = Wq + 1/μ, Lq = λWq, L = λW. Pooled identical stations differ from separate dedicated queues, batch ovens, unreliable testers or product-dependent service; choose a different model if those effects dominate. Use numerically stable recurrences for very large c/a rather than naive powers/factorials.

### Variable arrivals/service: Kingman's approximation

For a stable single-server G/G/1 queue, a useful approximation is Wq ≈ [(ca²+cs²)/2] × [ρ/(1−ρ)] × te, where ca and cs are coefficients of variation (standard deviation/mean) of interarrival and service times, and te is mean service time. It highlights three causes of waiting: variability, utilisation and processing time. It is approximate and excludes many blocking/batching/failure effects unless properly represented.

Example: λ = 6/h, te = 0.125 h, ca = 1, cs = 0.5 yields ρ = 0.75 and Wq ≈ 0.234375 h = 14.0625 min. Lower service variability reduces predicted waiting relative to M/M/1 at the same mean rates. Verify arrival/service distributions and correlations from timestamps before accepting the result.

Use a discrete-event simulation for re-entrant routes, finite buffers, failures/repairs, batching, setups, calendars, priorities or mixed products. Model arrivals, resource seize/release, processing, movement, inspection and rework as events. Include warm-up, multiple seeds, run length, confidence intervals and conservation checks. Compare simple special cases against queue formulas; do not trust a single animation or seed as a production forecast.

## 3. Kanban and replenishment

Kanban is a pull signal authorising replenishment or production when material is consumed. A card/bin limit controls inventory/WIP; it does not create supplier capacity. Define part/container, route, replenishment trigger, full/empty locations, ownership, replenishment lead time and response to abnormal conditions.

A basic sizing rule is N = ceil[D × T × (1+s) / C], with D demand rate (units/time), T replenishment lead time (same time unit), safety allowance s (dimensionless), and C units/container. It assumes a reasonably stable flow and that the allowance appropriately covers uncertainty. Do not use a universal 10% or 20% buffer without evidence; model demand-during-lead-time distribution and required service level when consequential.

Example: D = 12 units/h, T = 1.5 h, C = 6, s = 0.2 gives ceil(3.6) = 4 containers/cards, holding up to 24 units. The 20% is illustrative. Measure actual replenishment time including waiting, transport, setup, inspection and supplier delay; using touch time alone undersizes the loop. Separate production and withdrawal Kanban where needed. Include yield/gross demand explicitly if losses occur before use.

Pilot one stable part family, make signals visible, establish a shortage/escalation rule, and measure stockouts, lead time, inventory and excess replenishment. Tune after data; reducing cards blindly may starve the constraint.

## 4. Just-in-time production

JIT means synchronising delivery/production with consumption while reducing waste and variability. It is not “zero inventory regardless of risk.” It depends on reliable quality, short predictable setups/lead times, capable suppliers, maintenance, usable signals and an appropriate production rhythm.

Apply by reducing changeovers, improving first-pass yield, leveling feasible demand/mix, shrinking transfer batches and using pull release. Preserve deliberate buffers for critical imported parts, uncertain demand, long lead times or high outage consequence. Compare working-capital/storage savings against expedite costs, stockout probability, downtime and customer commitments. Supplier consignment or moving inventory offsite does not eliminate system inventory or risk.

Deliver a replenishment policy with trigger, quantity, owner, calendar, lead-time assumptions, buffer justification and exception recovery. Connect it to BOM revisions: obsolete parts cannot be replenished into a new configuration accidentally.

## 5. Statistical quality control (SQC)

Begin with an adequate measurement system: calibration, bias, repeatability/reproducibility and traceability. Form rational subgroups so within-subgroup and between-subgroup variation mean what the analysis assumes. SPC detects process changes; acceptance sampling decides a lot; capability compares stable variation to specifications. They answer different questions.

| Data/problem | Technique | Check |
|---|---|---|
| Continuous measurements in repeated subgroups | X̄–R or X̄–S charts | Appropriate subgrouping and chart constants for actual subgroup size |
| Individual continuous observations | Individuals/moving-range chart | Independence/autocorrelation and measurement resolution |
| Fraction defective with varying sample count ni | p chart | Binomial assumptions; varying control limits and overdispersion |
| Defect counts per constant opportunity | c chart | Poisson-like counts, equal opportunity; defects differ from defective units |
| Defects per varying opportunity | u chart | Correct exposure ni and rate units; overdispersion |
| Small sustained mean shifts | EWMA/CUSUM | Baseline estimates, tuning and false-alarm/run-length tradeoff |
| Process versus drawing/customer limits | Cp/Cpk (or appropriate alternatives) | Stable process, suitable distribution, valid σ estimate, measurement capability |

For a p chart, pooled p̄ = total defectives / total inspected. Approximate three-sigma limits at sample size ni are p̄ ± 3√[p̄(1−p̄)/ni], clipped to [0,1]. With rare defects/small samples use suitable exact or specialist charts. Control limits are estimated from a stable baseline, not chosen to match specification limits. A point outside limits is a signal to investigate; predefine additional run rules and their false-alarm effects rather than adding rules until a desired answer appears.

For approximately normal stable dimensional data, Cp = (USL−LSL)/(6σ) and Cpk = min(USL−μ, μ−LSL)/(3σ). Example: LSL = 9.8 mm, USL = 10.2 mm, μ = 10.05 mm, σ = 0.04 mm gives Cp ≈ 1.667 and Cpk = 1.25. The process spread and centering tell different stories. Target indices depend on customer/product requirements; a calculated value is not certification. Distinguish within-process capability estimates from overall performance indices and account for autocorrelation/nonnormality.

### Sampling and confidence

For n independent representative trials and zero failures, an exact one-sided binomial upper confidence bound for failure probability at confidence 1−α is p_upper = 1 − α^(1/n). At 95% confidence, zero failures in 10 trials still permits p ≈ 25.9%; zero in 59 permits p ≈ 4.95%. This is not a guarantee for correlated trials or changed conditions. It explains why a 10-unit pilot cannot establish 95% long-run yield with high confidence.

For a binomial lot-acceptance plan with sample n and accept up to c defectives, Pa(p) = Σ(i=0 to c) choose(n,i) pⁱ(1−p)^(n−i). Choose the plan using producer/consumer risk and the relevant contract/standard; finite lot sampling without replacement may require the hypergeometric model. Acceptance does not establish every unit conforms. Critical functions may need complete inspection and process controls.

## Runnable calculations and handoff

Run `python3 scripts/manufacturing_calcs.py --demo` from the skill folder for the examples above. Helpers reject unstable queues/invalid inputs and label model assumptions. Tests check Little's law, M/M/c reduction to M/M/1, Kanban rounding, capability and binomial bounds. These are analytical examples, not measured factory throughput.

Deliver a process/value-stream map; routing and capacity/WIP/lead-time model; takt/cycle/setup/yield definitions; measured arrival/service data; pull/Kanban/replenishment policy; JIT buffer rationale; supplier and configuration controls; SPC/control plan with chart assumptions and reaction plan; acceptance-sampling/measurement plan; and updated cost/cash sensitivities. Validate predicted improvement with a bounded representative pilot before claiming production capacity.
