# Costing, product development, quality and go-to-market

Use this guide when an individual or company needs to justify, manufacture, finance, sell or support a mechatronic solution. Tie commercial claims to a measurable customer outcome and verified technical envelope. Use the user's currency and jurisdiction; illustrative numbers below are hypothetical currency units (CU), exclude tax, and are not supplier quotes or financial advice for a specific investment.

## 1. Define the customer and offer

Separate user, buyer, budget owner, installer, maintainer and purchasing approver. For a business customer, quantify current process cost, bottleneck, downtime, scrap, quality variation and labour redeployment. For a consumer, test ease of setup, reliability, appeal, space/noise, affordability, support and returns. Interview target customers about observed behaviour and constraints; enthusiasm is not a purchase commitment.

Use a one-page value proposition: target segment → specific job/problem → measurable outcome → credible demonstration → purchase/installation effort → price model → support promise. Compare manual process, existing automation, outsourcing and “do nothing”. Rank initial markets by problem severity, repeatability, reachable buyers, achievable evidence, delivery/support burden, sales cycle and margin. Start with a focused use case before generalising the product.

Distinguish a bespoke engineering service, a repeatable product, an integration project and an operated service. Custom contracts may fund development but accumulate unique support obligations. Standardise interfaces and configurable modules where that preserves the actual customer requirement.

## 2. Build the cost model

Separate **non-recurring engineering (NRE)** from recurring unit costs and working capital:

- NRE: discovery, design, prototypes, tooling, fixtures, test development, verification/validation, relevant conformity work, documentation and launch.
- Recurring production: materials/components, fabrication, assembly touch time, programming/calibration/test, packaging, inbound logistics, scrap and rework under a stated yield model.
- Selling/service: channel/payment fees, outbound delivery, installation/training, warranty provision, cloud/connectivity, support, field service and returns.
- Working capital: supplier deposits, inventory, work in progress, receivables less supplier credit/customer deposits. Profitability does not guarantee cash to pay suppliers.

Maintain quantity, unit price, source/date/currency, MOQ, lead time, quote validity, alternates, yield basis and confidence per BOM line. Labour = effective loaded hourly cost × touch time; elapsed machine time and labour time may differ. Avoid double-counting overhead in both loaded rates and separate allocations.

For a simple model in which every started unit incurs the same production cost and failed units are completely scrapped, production cost per good unit = cost per start / yield. If failures occur at different stages or can be reworked/recovered, model those flows explicitly. Add costs incurred only on sold units after that calculation.

Contribution per sold unit = net selling price − variable cost per sold unit. Gross margin and contribution margin depend on which costs the business includes; label definitions. Gross margin fraction = (price − defined COGS)/price; markup = (price − cost)/cost. Break-even volume = fixed costs / contribution, rounded up for indivisible units; it does not represent a cash-flow forecast. See [the calculation helper](../scripts/engineering_calcs.py).

### Worked product scenario

Illustrative benchtop positioning module: BOM 180 CU, assembly 40, test 15 and production packaging 10 gives 245 CU per start. Assuming 95% yield with all start costs lost on scrap gives 257.89 CU per good unit. Add 25 CU per sold unit for variable warranty/support allowance: total 282.89. With 450 CU net selling price, contribution is 167.11 CU (37.13% of price). At 30,000 CU fixed launch cost, contribution break-even is 180 units. At 85% yield it becomes 220 units; at 400 CU selling price and 95% yield it becomes 257 units. These are scenario arithmetic, not demand or yield evidence.

Obtain supplier quotes and a pilot time/yield study before accepting these economics. Check channel fees, taxes, financing and fixed ongoing costs separately. Validate willingness to pay using interviews, demonstrations and appropriately scoped commercial offers rather than treating calculated break-even as sales forecast.

## 3. Finance the development and cash cycle

Match financing to uncertainty and repayment capacity. Bootstrapping, paid feasibility work, milestone customer funding, grants, equity, debt, equipment lease and supplier terms have different costs/control/obligations. Early technical uncertainty is a poor fit for debt that requires repayment before predictable cash generation; equity can fund uncertainty but dilutes ownership. Customer-funded pilots need clear IP, deliverables, acceptance and support boundaries reviewed for the actual agreement.

Build a monthly cash forecast: opening cash + dated customer receipts/funding − supplier/prototype/tooling/payroll/operating/tax/finance payments = closing cash. Model base/downside/upside cases, delays, minimum orders, inventory ageing, warranty shocks and slow payment. Set explicit go/no-go milestones and cash required to reach each. Verify current financing/grant eligibility, terms and jurisdiction-specific tax/accounting rules with authoritative sources and qualified advisers when needed; do not invent available funding.

For customer ROI, separate hard savings, avoided cost and speculative upside. Simple payback = initial installed cost / annual net savings when savings are steady and positive. Include installation, training, maintenance, energy, consumables, downtime and residual value. Use NPV/discounted cash flow for multi-year alternatives with a disclosed discount rate and timing assumptions. Labour minutes saved do not necessarily become cash savings if staffing/capacity does not change.

## 4. New product development and a 90-day pilot

| Period | Engineering and customer work | Evidence to decide next stage |
|---|---|---|
| Days 1–15 | Customer interviews, mission/requirements, existing solution review, first-order budgets and major hazard/unknown assessment | Defined user/buyer, measurable acceptance, feasible physical bounds and provisional economics |
| Days 16–35 | Reuse/build bench prototype, simulate, test hardest assumption, get supplier feedback | Instrumented feasibility evidence and cost/lead-time ranges |
| Days 36–60 | Integrated prototype, user workflow, design-for-manufacture, calibration/test fixture and support concept | Requirement traceability, representative tasks, defect list and revised BOM |
| Days 61–75 | Small pilot batch with actual process/operators, packaging and installation trial | Yield/touch time, critical process evidence, usability and service observations |
| Days 76–90 | Bounded customer pilot, acceptance testing, pricing/channel test and cash forecast | Evidence-based release/rework/stop decision, supported claims and funded next stage |

Adjust the timeline for complexity, tooling and regulatory lead times. A 90-day plan is a learning schedule, not a guarantee of certified market readiness. Agree pilot scope, site readiness, responsibilities, evidence access, acceptance, exclusions, warranty/service and exit criteria. Delivery should include setup/training and a recoverable configuration baseline.

## 5. Quality control and assurance

Quality assurance designs a reliable process; quality control inspects/measures output. Map critical-to-quality characteristics from customer requirements into drawings, supplier controls, process settings and end-of-line tests. Use design/process FMEA to identify failure modes, effects, causes, controls and actions. Do not hide a severe hazard behind a low multiplied risk-priority score; address severity and detectability explicitly.

Perform incoming inspection based on supplier evidence and part risk; use first-article inspection for new designs/processes; keep calibrated gauges/fixtures. Use error-proofing (poka-yoke), clear work instructions and traceable serial/lot/programming records. Maintain nonconformance quarantine/disposition and corrective/preventive actions; root-cause methods such as 5 Whys or fishbone diagrams organise hypotheses, while experiments confirm causes.

Use statistical process control (SPC) when repeated process data supports it. Control limits describe process behaviour; specification limits express customer/design requirements. Capability indices such as Cp = (USL−LSL)/(6σ) and Cpk = min(USL−μ, μ−LSL)/(3σ) require a stable process and suitable distribution/variation estimates. Do not compute a convincing Cpk from a few hand-selected prototype units. Nonnormal data, autocorrelation and measurement error need appropriate treatment. [NIST's process capability guide](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm) explains this context.

Use acceptance sampling for its stated lot risks; inspecting a sample does not prove every item conforms. Critical functional requirements may require 100% testing with an adequate measurement system. Track first-pass yield, rework, scrap, field failures/returns, repair time, supplier defects and customer acceptance. Feed evidence into engineering changes and revised cost/warranty assumptions.

A small pilot exposes process problems but gives an uncertain yield estimate. Report the count of starts/failures and an appropriate confidence interval rather than treating, for example, 10 successful builds as proof of 95% long-run yield. Separate a target yield used in the business case from the evidence needed to accept that target.

## 6. Sales, marketing and lifecycle support

For B2B, build an application-specific demo, test report, ROI model, installation/site checklist, technical/security integration information, proposal, acceptance plan and service agreement. Partner with integrators/distributors when reach and installation/support capabilities justify margin and control tradeoffs. Measure qualified pipeline, conversion, sales cycle, acquisition cost and pilot-to-production adoption.

For consumers, prioritise clear outcome-led messaging, honest demonstration videos, setup experience, compatibility, noise/space/energy expectations, shipping, returns and accessible support. Test price and messages with small experiments; report sample/channel limitations. For both markets, tie every performance/safety/environmental claim to evidence and conditions. Do not claim certification from a supplier logo or from a passed internal test.

Choose outright sale, lease, subscription, robotics-as-a-service or service contract according to customer cash preferences and who can bear uptime/maintenance/asset risks. Define inclusions, consumption limits, spares, response targets and end-of-life obligations. A subscription is not recurring profit unless continuing support/cloud costs and churn are modelled.

Plan repairability, spares, component obsolescence, cybersecurity updates, customer data handling, recalls/service campaigns and disposal. Verify applicable product, workplace, electrical, radio, battery transport, privacy, consumer and sector rules for the intended use and market using [sources](sources.md). These are applicability questions for the actual product, not a claim that one universal standard covers all robots.

## Commercial handoff

Deliver a dated cost model with sensitivities, quote register, make/buy rationale, funding/cash plan, pilot/NPD schedule, quality/control plan, target segment and positioning, evidence-backed demo/claims, channel/pricing/service model and measured go/no-go criteria. Keep estimated, quoted, ordered, manufactured, shipped and accepted states distinct.
