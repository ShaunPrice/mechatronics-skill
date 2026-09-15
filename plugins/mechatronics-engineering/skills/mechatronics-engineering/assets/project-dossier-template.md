# Engineering project dossier

Copy this template for a real project. Replace prompts with evidence; mark genuinely inapplicable sections and explain why. Keep unknowns explicit.

## Identity and status

Project / revision / date / owner / intended user and market / current stage / approved scope / evidence level / decision needed.

## Mission and requirements

Mission profile, operating environment, payload/load, workspace, duty cycle, life, maintainers and constraints.

| ID | Requirement and units | Conditions | Threshold | Verification method | Owner | Evidence/status |
|---|---|---|---|---|---|---|

## Terminology and assumptions

Everyday term → precise engineering term → implication. Define units, frames and signs.

| ID | Assumption/unknown | Value/range and units | Source/confidence | Decision affected | Measurement/owner |
|---|---|---|---|---|---|

## Architecture and alternatives

System boundary; energy/information block diagrams; control/protection partition; concept comparison; selected rationale; make/buy/reuse decisions.

## Budgets and calculations

Loads/torque/inertia; structural stiffness/error; power/energy/thermal; sensor uncertainty; timing/compute/network; cost/mass. State equations, inputs, margins and independent checks.

## Interfaces

| ID | From/to | Mechanical datum or connector/pin | Quantity/unit/frame or voltage | Protocol/rate/timing | Default/failure behaviour | Revision |
|---|---|---|---|---|---|---|

## Design files and parts

Actual CAD/drawing/PCB/harness/source paths and revisions; export/analysis status; manufacturing constraints.

| Part | Function | Qty | Required specification | MPN/grade/revision | Alternate | Unit cost/currency/date/source | Lead time | Verified status |
|---|---|---|---|---|---|---|---|---|

## Software and configuration

Source/firmware/OS/toolchain versions; build/run commands; hardware mapping; dependencies; state machine; watchdog/fault policy; update and rollback.

| Parameter | Value | Unit/encoding | Allowed range | Hardware revision | Source/calibration | Persistence |
|---|---|---|---|---|---|---|

## Simulation and test plan

Model assumptions, solver/timestep/tolerances, initial/boundary conditions, seeds, inputs and reproduction commands. Define bench/field scope separately.

| Test ID / requirement | Fixture/instrument | Initial conditions and method | Stop limits | Expected/pass criterion | Actual result and uncertainty | Evidence level/link |
|---|---|---|---|---|---|---|

## Manufacturing and inspection

Process/fixtures; tolerances/datums/finish; material/lot controls; assembly sequence; critical settings; programming/calibration; end-of-line test; yield/rework plan; packaging/storage; serial traceability.

## Commissioning and operations

Site readiness; competent personnel; safe state and stored energy; staged enablement; homing/limits; tuning and incremental loads; acceptance record; operator guide; service interval; spares and recovery.

## Business and release

Customer/value evidence; NRE and unit costs; yield/sensitivity; quotes versus estimates; pricing/contribution; monthly cash/funding; NPD/pilot milestones; sales/channel/support; applicable requirements and release authority.

## Decisions, deviations and next steps

| Decision/issue | Evidence and rationale | Consequence | Owner | Due/next action | Status |
|---|---|---|---|---|---|

Conclude with what is designed, calculated, simulated, software-tested, physically verified and still pending. Include the exact configuration baseline and files needed to resume elsewhere.
