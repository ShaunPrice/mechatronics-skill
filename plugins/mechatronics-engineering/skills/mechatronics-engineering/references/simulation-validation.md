# Simulation, computation and experimental validation

Use this guide to select a model and solver, build reproducible evidence and decide what must be measured next. **Verification** asks whether the equations/code were solved correctly. **Validation** asks whether the model represents the real system well enough for its intended decision. Neither is replaced by an attractive animation.

## Select fidelity by the decision

| Question | Smallest useful model | Escalate when |
|---|---|---|
| Can the actuator meet load/speed/runtime? | Static loads, inertia, torque-speed and energy budget | Duty/thermal behaviour, compliance or transient limits matter |
| Is the feedback design plausible? | Transfer function/state space at a stated operating point | Saturation, contact, hysteresis, nonlinear geometry or mode transitions affect results |
| Will a structure deflect/fail? | Beam/shaft equations and load cases | Complex geometry/contact/load path requires finite element analysis (FEA) |
| Does flow/cooling work? | Pressure-loss and thermal resistance network | Complex turbulent flow, conjugate heat transfer or local hot spots justify CFD |
| Can a robot complete a mission? | Kinematic model and scenario logic | Contact, perception, vehicle dynamics or sensor artefacts dominate |
| What is production throughput? | Cycle-time and queue estimate | Shared resources, variability, failures and batching need discrete-event simulation |
| How sensitive is the decision? | Local derivatives and bounded parameter sweep | Nonlinear uncertainty/dependence requires Monte Carlo or global sensitivity |

Inputs include equations, geometry, material/plant parameters, initial/boundary conditions, disturbances, controller, sensor model, units, random seeds and solver settings. Identify each parameter as measured, vendor-stated, fitted or assumed. Calibrate on one dataset and validate on another. Avoid adjusting a model until it matches the same dataset used to claim success.

## Numerical methods and failure checks

Use explicit Runge–Kutta methods for many nonstiff ODEs; implicit Radau/BDF-type methods for stiffness when supported and justified. State error tolerances and provide a Jacobian when useful. Use fixed steps when emulating a deterministic control period; integrate continuous plant dynamics between samples separately. A smaller plant integration step does not remove controller sampling delay. Use events for impacts, switching and limits; do not silently step through discontinuities. [SciPy's solver documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) describes these solver choices and tolerances.

For long conservative mechanical simulations, consider symplectic or variational integrators and monitor energy behaviour; numerical damping or energy growth can imitate real physics. For DAEs/multibody constraints, choose a suitable solver and consistent initial conditions; track constraint residuals. For contact, examine penetration, restitution/friction assumptions and timestep sensitivity.

Perform step-size/mesh/time-horizon convergence on the quantity that drives the decision. Compare dt and dt/2, or successive mesh refinements, until the change is small against the acceptance tolerance; report the comparison, not just “converged”. Keep temporal discretisation, spatial discretisation, parameter uncertainty and model-form error separate. An FEA colour plot needs boundary-condition justification, mesh quality and peak-stress interpretation; singular point loads can make stress diverge under refinement.

For Monte Carlo, document distributions, correlations, truncation and sample count. Use convergence/confidence estimates and examine failure tails. Random samples are not exhaustive worst-case proof; bounded safety constraints need a suitable worst-case analysis. Use designed experiments to distinguish effects efficiently, randomise run order and account for blocking/drift.

## Software selection

Choose tools already supported in the user's environment where practical. Verify versions, licences, hardware and interoperability before committing a commercial workflow. The following are tool families to evaluate, not claims of installation:

| Work | Candidate tools | Decision factors |
|---|---|---|
| Algebra, numerical methods and plots | Python/NumPy/SciPy/SymPy, Julia, GNU Octave, MATLAB | Team skills, validation, solver features, licensing and reproducibility |
| Control design | python-control, MATLAB/Simulink and relevant toolboxes | MIMO/discrete/robust support, model/code generation, hardware integration |
| Multiphysics/system models | Modelica/OpenModelica, Simscape | Physical libraries, DAEs, parameter identification and FMI/FMU exchange |
| Robot dynamics/training | MuJoCo, Gazebo, PyBullet, Isaac Sim/Lab, Drake | Contact accuracy, sensors, determinism, GPU needs, ROS integration and task suitability |
| CAD/FEA/CFD | FreeCAD, Onshape, Fusion, SolidWorks, CalculiX, Code_Aster, OpenFOAM, ANSYS, COMSOL | Geometry/process needs, boundary-condition support, solver validation and export/licence limits |
| Electronics/PCB | KiCad, ngspice/LTspice, manufacturer simulators | Supported device models, mixed-signal/power fidelity, parasitics and fabrication outputs |
| FPGA | Vendor toolchain, Verilator/GHDL/cocotb where compatible | Device support, HDL semantics, simulation coverage, synthesis/timing analysis |
| Embedded/real-time testing | Native compiler/unit tests, RTOS tooling, processor/HIL equipment | Timing fidelity, instrumentation, fault injection and target behaviour |
| Production/logistics | SimPy or established discrete-event suites | Queue/resource/shift modelling, input data and statistical output analysis |

Reproduce an environment using version records/lockfiles, input data hashes and an executable run recipe. Do not silently install licensed products or download large models. A text-only environment can deliver equations, code and expected checks while marking unexecuted results. See [sources](sources.md) for verified primary entry points; check exact current support before selecting a stack.

## Practical test ladder

1. **Analytical bounds:** check units, force/energy balance, signs, zero-load/zero-input limits and plausible magnitudes. Use an independent formulation for key quantities.
2. **Software tests:** test meaningful properties such as saturation bounds, stale-command rejection, round-trip frame transformations or IK → FK reconstruction. Use known analytical solutions to check numerical routines.
3. **Model simulation:** nominal and disturbed cases, parameter variation, unreachable commands, quantisation, delay, jitter, noise and actuator limits. Check metrics and full traces.
4. **SIL/PIL/HIL:** software-in-loop runs the actual software against a model; processor-in-loop uses target computation; hardware-in-loop incorporates relevant physical I/O/timing. Record what hardware is actually included and what remains simulated.
5. **Bench:** instrumented tests with known loads, independent references and defined stop criteria. Verify supply/polarity/stop functions before energetic motion. Record equipment/revision/calibration and environmental conditions.
6. **Application/field:** representative missions/users, environmental extremes, endurance, restart/recovery and service. Assess transfer from bench results and open deviations.

For control, measure rise/settling time, overshoot, steady error, saturation duration, disturbance rejection, noise amplification and robust stability evidence as appropriate. State definitions: settling time is entry into a band that remains satisfied for the observation interval, not the first crossing. A 10-second trace says nothing directly about hour-long thermal drift.

For reliability, define mission and failure, sample exposure and confidence before interpreting “zero failures”. Do not extrapolate a short trial to a large MTBF without a justified model. Accelerated testing must preserve relevant failure mechanisms. Trace defects to corrective action and retest the affected requirements.

## Included computational lab

[control_lab.py](../scripts/control_lab.py) implements an original sampled PID driving a mass–spring–damper through a saturated force command, integrated with RK4 and held input. It includes derivative-on-measurement, filtering and conditional integral antiwindup. It also exports plant frequency response. It writes CSV, a JSON result and a standalone HTML chart using only Python's standard library. It does not control hardware or provide universal gains.

[engineering_calcs.py](../scripts/engineering_calcs.py) contains transparent helpers for screw sizing, a simple rover traction bound, battery runtime, planar 2R inverse kinematics and contribution-margin break-even. Each has explicit assumptions and input checks; the [worked examples](worked-examples.md) explain their use and limits. Use these as reproducible starting points; expand the model when the real decision requires it.
