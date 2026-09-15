# Selected-plant interfaces: Scilab, Xcos, ATOMS and ROS 2

This kit moves one **massSpring** or **firstOrder** plant from the browser's `mechatronics-block-diagram/v1` JSON into other engineering tools. It exports continuous state-space matrices, initial conditions and a unit-input comparison. The original diagram's controllers, other plants, wiring, sources, delays and nonlinear blocks are excluded from the exported model. Validate the entire diagram first so malformed or ambiguous inputs cannot be silently accepted.

The Xcos adapter constructs native diagrams from the installed blocks and can run a recorded batch comparison. GUI-capable Scilab can save/reload native `.zcos` files and open the scope diagram. This remains selected-plant conversion; no hardware driver or robot controller connection is included.

## 1. Generate an interface bundle

From the installed skill folder (or the repository's `skills/mechatronics-engineering` folder), using Python 3:

```sh
python3 -B scripts/export_interfaces.py \
  --diagram assets/interfaces/example-diagram.json \
  --plant-node plant \
  --out work/interface-example
```

Use a new or empty output folder. To use your own browser model, save its diagram JSON, find the plant node's `id`, and substitute those values. Explicit selection is required even if there is only one plant. Invalid JSON, duplicate keys/IDs, unknown fields, invalid parameters, missing/multiply-driven ports and instantaneous algebraic loops are rejected.

For a first-order thermal-rise model, declare the physical units explicitly:

```sh
python3 -B scripts/export_interfaces.py \
  --diagram work/thermal-diagram.json --plant-node thermal \
  --input-unit W --output-unit K --out work/thermal-interfaces
```

The exporter declares units; it does not convert them or infer them from labels. A thermal **rise** state in K does not include the ambient-temperature addition elsewhere in a browser graph. First-order units default to visibly unspecified values. Mass-spring input is N and output is m.

Optional `--watchdog-s` sets the ROS receipt-age timeout (default 0.5 s); `--input-limit` sets a symmetric simulation input envelope (default 1000 in the declared input unit, minimum 1 to permit the comparison). These are educational numerical limits, not actuator ratings.

### Exported files

| File | Purpose |
|---|---|
| `plant.json` | Plant parameters; A, B, C, D, x0; units; fixed dt; requested/effective duration; integration bounds; excluded graph boundary |
| `plant_data.sce` | Numeric Scilab assignments and continuous `syslin` plant |
| `reference.csv` | Python RK4 unit-input reference, no header: time_s, input, output, state_1, optional state_2 |
| `scilab_analysis.sce` | `csim` response, CSV output, numerical difference report and plant Bode plot |
| `xcos_build.sce` | Construct native STEP_FUNCTION/CLSS/CLOCK_c diagrams with recording and scope variants; save them as Scilab `.sod` data |
| `xcos_batch.sce` | Run native `scicos_simulate`, write output CSV and report error against Python |
| `xcos_setup.sce` | Save/reload both native `.zcos` files and open the scope diagram in GUI-capable Scilab |
| `atoms_setup.sce` | Inspect installed modules; optional installation/loading lines remain commented |
| `ros2_ws/src/mechatronics_sim/` | Buildable `ament_python` simulation package with configuration and a pure Python core |

State order for massSpring is `[position, velocity]`: A = `[0 1; -k/m -b/m]`, B = `[0; 1/m]`, C = `[1 0]`, D = `[0]`. For firstOrder, the state is its output: A = `[-1/tau]`, B = `[gain/tau]`, C = `[1]`, D = `[0]`. Initial conditions come from the selected node.

## 2. Scilab: simulate and compare

In an installed Scilab GUI, run:

```scilab
exec("/absolute/path/to/interface-example/scilab_analysis.sce", -1);
```

The script defines a continuous system using `syslin('c', A, B, C, D, x0)`. The exported realization preserves the meaning of the initial state. [Scilab syslin documentation](https://help.scilab.org/syslin)

For numerical execution in `scilab-cli`, set `interface_plots=%f` before executing the script. GUI plotting stays enabled by default. For example, put the following in a small runner script and pass that script with `scilab-cli -nb -nouserstartup -noatomsautoload -f runner.sce -quit`:

```scilab
interface_plots = %f;
exec("/absolute/path/to/interface-example/scilab_analysis.sce", -1);
```

It supplies a constant unit-input function to `csim` and uses the CSV time grid, then writes `scilab_response.csv` with the same columns as `reference.csv`. A function input is intentional: Scilab documents the string `"step"` shortcut for zero initial state. The script prints maximum output/state differences rather than asserting that two solvers or tools were already validated. [Scilab csim documentation](https://help.scilab.org/csim), [CSV reading](https://help.scilab.org/csvRead), [CSV writing](https://help.scilab.org/csvWrite)

The Bode plot is the selected **plant** frequency response. Its default comparison bounds are 0.001–1000 Hz; change them for the plant's relevant modes. Scilab's frequency arguments are Hz, including when choosing an angular-frequency display option. A plant Bode plot alone is not closed-loop stability margin evidence. A zero input gain skips the logarithmic zero-gain plot. [Scilab Bode documentation](https://help.scilab.org/bode)

Use the numerical difference with an engineering acceptance tolerance in the output's units. Halve the browser/export sample interval and compare again; match input amplitude, initial conditions, output definition and time grid. The Python reference is an independently runnable numerical model, not a physical measurement. Its unit input starts at t=0 and does not reproduce an original graph's PID or delayed step.

## 3. Xcos: native construction, batch validation and saved diagrams

Run native simulation from either Scilab CLI or its GUI:

```scilab
exec("/absolute/path/to/interface-example/xcos_batch.sce", -1);
```

The builder uses the installed `STEP_FUNCTION`, `CLSS`, `CLOCK_c`, `TOWS_c` and `CSCOPE` define functions plus native `scicos_link` connections. It creates two `scicos_diagram` objects: a workspace-recording model for batch verification and a scope model for interactive viewing. The input is a unit step at t=0; the plant has the exported initial state. No original browser controller is added. [Native diagram structure](https://help.scilab.org/scicos_diagram), [native links](https://help.scilab.org/scicos_link), [workspace recorder](https://help.scilab.org/TOWS_c)

The batch script calls `scicos_simulate(...,"nw")`, writes `xcos_response.csv` (two numeric columns, time_s and output) and compares matching sampled times with the Python reference. An event exactly at the final simulation time can be excluded; the scripts report the actual first/last sample and do not invent the missing endpoint. Both diagrams also save as `selected-plant.sod`, which is Scilab data rather than an Xcos interchange file. [Native batch simulation](https://help.scilab.org/scicos_simulate)

In GUI-capable Scilab, run:

```scilab
exec("/absolute/path/to/interface-example/xcos_setup.sce", -1);
```

This constructs, saves and reloads `selected-plant-batch.zcos` and `selected-plant-scope.zcos`, then opens the scope diagram. Set `interface_open_xcos=%f` beforehand to save/reload without opening a window, including in Java-enabled `scilab -nw` mode. `.zcos` serialization is disabled by Scilab in `-nwni`/`scilab-cli` mode; use the batch script there. [Native diagram save/load](https://help.scilab.org/xcosDiagramToScilab), [Xcos editor](https://help.scilab.org/xcos)

The scripts use a continuous solver with absolute tolerance 1e-10, relative tolerance 1e-8, time tolerance 1e-10 and maximum integration step `sample_dt`. Scope/recording events occur every `sample_dt`; those observations are separate from the solver's internal steps. Review these choices and perform convergence checks before extending the plant.

### Manual fallback and learning exercise

If an installed Xcos release has incompatible block APIs, start an empty Xcos editor and follow this equivalent construction recipe. The installed version's actual source/help takes precedence over untested field assumptions.

1. Copy the numeric assignments for A, B, C, D, x0, sample_dt, final_time and comparison_input from `plant_data.sce` into the diagram's Context editor. This keeps a saved native diagram independent of a previous interactive console session. Alternatively enter the numeric values directly in each dialog.
2. Add **STEP_FUNCTION** from Sources. Set Step Time = `0`, Initial Value = `0`, Final Value = `comparison_input` (1). Its regular output is the isolated plant input. [Step block parameters](https://help.scilab.org/STEP_FUNCTION)
3. Add **CLSS** from Continuous time systems. Enter A, B, C, D and x0 in its five corresponding fields. Wire the step's regular output to CLSS's regular input. [Continuous state-space block](https://help.scilab.org/CLSS)
4. Add **CSCOPE** from Sinks and wire CLSS's regular output to its regular input. Set Ymin/Ymax to cover the reference output, Refresh period = `final_time`, and a suitable positive buffer size, for example 1 for a short teaching run. Set inherited-events option to 0 because an explicit clock will activate the scope. [Scope parameters and event input](https://help.scilab.org/CSCOPE)
5. Add **CLOCK_c** from Sources. Set Period = `sample_dt`, Initialisation Time = `0`. Connect its event output to the scope's event input, using the event connection rather than a regular signal wire. [Clock parameters](https://help.scilab.org/CLOCK_c)
6. Set final simulation time to `final_time`. Choose the continuous solver and tolerances for the plant's stiffness; begin with relative tolerance 1e-8, absolute tolerance 1e-10 and a maximum step no larger than `sample_dt`, then check convergence.
7. Run, inspect the trace, and save using the native format offered by your installed Xcos version. Record its version, solver, tolerances, context and observed result before claiming Xcos execution succeeded.

For the included example, m=1 kg, b=2 N·s/m, k=4 N/m and a 1 N constant input give a steady position of 0.25 m. This analytical check is more useful than judging a curve only by its appearance. To recreate a browser feedback controller, model its sampled timing, derivative convention, filtering, saturation and anti-windup explicitly; this exporter does not do that conversion.

## 4. ATOMS: explicit optional toolboxes

Run `exec("/absolute/path/to/interface-example/atoms_setup.sce", -1);` to list locally installed modules. The generated examples use core Scilab/Xcos functionality and request no extra toolbox. [atomsGetInstalled](https://help.scilab.org/atomsGetInstalled)

If a later engineering task needs an ATOMS module, verify its exact name, version, platform compatibility and licence first. Edit and uncomment the supplied `atomsInstall([requested_module requested_version])` line only when installation is intended. To execute an already installed module's loader, use the separate commented `atomsLoad` line. There are no automatic module downloads or loads in this kit. [atomsInstall](https://help.scilab.org/atomsInstall), [atomsLoad](https://help.scilab.org/atomsLoad)

## 5. ROS 2: simulation topics

The generated package requires an existing compatible ROS 2 Python environment with `rclpy`, `std_msgs`, `ament_python`, setuptools and colcon. The adapter follows the official Jazzy Python publisher/subscriber APIs and package layout; other distributions require local verification. These are declared runtime dependencies, not installed by the exporter. [ROS 2 Python package structure](https://docs.ros.org/en/jazzy/How-To-Guides/Developing-a-ROS-2-Package.html), [official publisher example](https://github.com/ros2/examples/blob/jazzy/rclpy/topics/minimal_publisher/examples_rclpy_minimal_publisher/publisher_member_function.py), [official subscriber example](https://github.com/ros2/examples/blob/jazzy/rclpy/topics/minimal_subscriber/examples_rclpy_minimal_subscriber/subscriber_member_function.py)

Example on a Linux host where Jazzy is already installed, replacing the export path:

```sh
source /opt/ros/jazzy/setup.bash
cd /absolute/path/to/interface-example/ros2_ws
colcon build --packages-select mechatronics_sim
source install/setup.bash
ros2 run mechatronics_sim plant_sim
```

In other sourced terminals during the configured run:

```sh
ros2 topic echo /mechatronics_sim/state
ros2 topic echo /mechatronics_sim/metadata
ros2 topic pub --rate 10 /mechatronics_sim/force_n std_msgs/msg/Float64 '{data: 1.0}'
```

For firstOrder, publish to `/mechatronics_sim/input` instead. Stop the publisher and observe zero applied input after the receipt timeout. The state continues evolving under the zero-input plant dynamics until the configured duration. Restart the node to reset its state and run again. A different compatible generated config may be supplied with `--ros-args -p config:=/absolute/path/plant.json`; no live parameter changes are implemented.

| Topic | Type | Meaning |
|---|---|---|
| `/mechatronics_sim/force_n` | `std_msgs/msg/Float64` | massSpring force magnitude with sign, in N |
| `/mechatronics_sim/input` | `std_msgs/msg/Float64` | firstOrder scalar in the declared input unit |
| `/mechatronics_sim/state` | `std_msgs/msg/String` containing JSON | Simulation time, step index, x, y, applied input, units, stale/completed indicators |
| `/mechatronics_sim/metadata` | `std_msgs/msg/String` containing JSON | Complete selected model, topic and timing contract; republished once per wall second |

The adapter uses `time.monotonic()` for **local receipt age**. Input messages have no sender timestamp; age before local receipt is unknown. Queue depth is one. Each simulation timer callback advances exactly one fixed dt with bounded RK4 substeps, so slow execution makes the simulation run slower instead of integrating a large catch-up interval. The state timestamp is **simulation time**, separate from wall time; the node does not publish `/clock` or claim hard real-time behavior. Invalid/nonfinite or out-of-envelope input clears the command to zero. A numerical envelope fault stops integration and reports a fault.

The topics and dynamics are simulation-only. There is no hardware bridge, actuator command topic, robot joint controller or live commissioning behavior. A zero simulation input may let a simulated state coast or decay; it is not a physical emergency-stop design.

### Pure-core smoke test without ROS installed

From the export folder:

```sh
PYTHONPATH=ros2_ws/src/mechatronics_sim python3 -B - <<'PY'
import json
from mechatronics_sim.sim_core import PlantSimulator
with open("plant.json", encoding="utf-8") as stream:
    sim = PlantSimulator(json.load(stream))
for _ in range(10):
    sample = sim.advance(1.0)
print(json.dumps(sample, indent=2, allow_nan=False))
PY
```

This exercises only the numerical core. It does not prove `colcon build`, middleware discovery, ROS topic exchange or execution in another runtime. Run and record those checks on the actual target environment before describing that interface as working.

## Evidence and maintenance

On 2026-09-15, Scilab 2026.1.0 on macOS executed the exported numerical scripts and native Xcos batch models for mass-spring and first-order plants, including nonzero initial state. Java-enabled batch mode also saved/reloaded native `.zcos` diagrams. These tests establish those bounded software paths on that installed release; interactive scope rendering, ROS middleware and hardware behavior remain separate checks. ATOMS inspection performed no downloads or module loading.

The optional native test in `scripts/test_interfaces.py` runs when `scilab-cli` is available (or when `SCILAB_CLI` points to it). It uses an isolated Scilab profile, disables user startup/ATOMS autoload, checks two plant responses and enforces a bounded runtime. Without Scilab, it reports an explicit skipped runtime test. The Python schema mirror must be reviewed alongside browser `block-engine.js` changes. A future block type needs a deliberate model mapping and validation before export support is added.


The repository also provides a [ROS 2 Docker test environment](https://github.com/ShaunPrice/mechatronics-skill/tree/main/integrations/ros2-docker). On 2026-09-15, its generated package built successfully in ROS 2 Jazzy on Linux arm64, and seven live middleware checks passed between separate processes, including command receipt, state/metadata, stale/invalid input handling and simulation-clock behavior. The container was left stopped for reuse. See that guide and its recorded evidence for exact scope, versions and start/test/stop commands; this does not establish hardware operation.
