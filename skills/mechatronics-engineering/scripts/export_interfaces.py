#!/usr/bin/env python3
"""Export one browser plant to Scilab/Xcos setup and a simulation-only ROS 2 kit.

Standard library only. This is not full-graph/controller conversion. No runtimes
are installed or invoked. Existing nonempty output directories are rejected.
"""
import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "interfaces"
_spec = importlib.util.spec_from_file_location("mechatronics_interface_core", ASSETS / "sim_core.py")
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)
PlantSimulator, plant_matrices, number = _core.PlantSimulator, _core.plant_matrices, _core.number
sample_count = _core.sample_count

SCHEMA = "mechatronics-block-diagram/v1"
# Deliberate Python mirror of browser block-engine.js v1 schema/defaults/bounds.
# Test parity when that browser schema changes; unsupported fields fail closed.
BLOCKS = {
    "constant": ([], {"value": 1}, {"value": (-1e6, 1e6)}),
    "step": ([], {"initial": 0, "final": 1, "at": .5}, {"initial": (-1e6, 1e6), "final": (-1e6, 1e6), "at": (0, 60)}),
    "sine": ([], {"amplitude": 1, "frequency": 1, "offset": 0, "phase": 0}, {"amplitude": (0, 1e5), "frequency": (0, 100), "offset": (-1e6, 1e6), "phase": (-36000, 36000)}),
    "sum": (["a", "b"], {"signA": 1, "signB": -1}, {"signA": (-1, 1), "signB": (-1, 1)}),
    "gain": (["in"], {"gain": 1}, {"gain": (-1e5, 1e5)}),
    "saturation": (["in"], {"min": -10, "max": 10}, {"min": (-1e6, 1e6), "max": (-1e6, 1e6)}),
    "pid": (["setpoint", "measurement"], {"kp": 18, "ki": 8, "kd": 4, "tf": .04, "limit": 30}, {"kp": (0, 1e4), "ki": (0, 1e4), "kd": (0, 1e4), "tf": (.001, 10), "limit": (.01, 1e6)}),
    "integrator": (["in"], {"initial": 0}, {"initial": (-1e5, 1e5)}),
    "delay": (["in"], {"initial": 0}, {"initial": (-1e5, 1e5)}),
    "firstOrder": (["in"], {"gain": 1, "tau": .5, "initial": 0}, {"gain": (-1e4, 1e4), "tau": (.001, 100), "initial": (-1e5, 1e5)}),
    "massSpring": (["in"], {"m": 1, "b": 1.2, "k": 4, "initialPosition": 0, "initialVelocity": 0}, {"m": (.02, 1000), "b": (.001, 100), "k": (.001, 1000), "initialPosition": (-100, 100), "initialVelocity": (-1000, 1000)}),
    "scope": (["in"], {}, {}),
}
STATE_ONLY = {"integrator", "delay", "firstOrder", "massSpring"}
RESERVED_IDS = {"constructor", "toString", "toLocaleString", "valueOf", "hasOwnProperty",
                "isPrototypeOf", "propertyIsEnumerable", "__defineGetter__", "__defineSetter__",
                "__lookupGetter__", "__lookupSetter__", "__proto__"}


def object_fields(value, allowed, name, required=()):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    if set(value) - set(allowed):
        raise ValueError(f"unknown {name} fields: {sorted(set(value)-set(allowed))}")
    if set(required) - set(value):
        raise ValueError(f"missing {name} fields: {sorted(set(required)-set(value))}")
    return value


def identifier(value, name):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,39}", value):
        raise ValueError(f"{name} must be a 1-40 character browser identifier")
    if value in RESERVED_IDS:
        raise ValueError(f"{name} uses a reserved browser identifier")
    return value


def printable_text(value, name, length=60):
    if not isinstance(value, str) or not 1 <= len(value) <= length or re.search(r"[\x00-\x1f\x7f]", value):
        raise ValueError(f"{name} must be 1-{length} printable characters")
    return value


def validate_diagram(raw):
    object_fields(raw, ("schema", "settings", "nodes", "edges"), "diagram",
                  ("schema", "settings", "nodes", "edges"))
    if raw["schema"] != SCHEMA:
        raise ValueError("expected browser schema " + SCHEMA)
    settings = object_fields(raw["settings"], ("dt", "duration"), "settings", ("dt", "duration"))
    dt = number(settings["dt"], "dt", .001, .1)
    duration = number(settings["duration"], "duration", .1, 60)
    if not isinstance(raw["nodes"], list) or not 1 <= len(raw["nodes"]) <= 50:
        raise ValueError("diagram needs 1-50 nodes")
    if not isinstance(raw["edges"], list) or len(raw["edges"]) > 100:
        raise ValueError("diagram supports at most 100 edges")
    steps = sample_count(duration, dt)
    if steps*len(raw["nodes"]) > 1e6:
        raise ValueError("diagram exceeds one million block samples")
    nodes, by_id = [], {}
    for raw_node in raw["nodes"]:
        object_fields(raw_node, ("id", "type", "x", "y", "params", "label"), "node",
                      ("id", "type", "x", "y"))
        ident = identifier(raw_node["id"], "node id")
        kind = raw_node["type"]
        if not isinstance(kind, str) or kind not in BLOCKS:
            raise ValueError("unsupported block type")
        if ident in by_id:
            raise ValueError("duplicate node id: " + ident)
        _, defaults, bounds = BLOCKS[kind]
        given = object_fields(raw_node.get("params", {}), defaults, "parameters")
        params = {**defaults, **given}
        params = {key: number(value, ident+"."+key, *bounds[key]) for key, value in params.items()}
        if kind == "sum" and any(value not in (-1, 1) for value in params.values()):
            raise ValueError("sum signs must be +1 or -1")
        if kind == "saturation" and params["min"] >= params["max"]:
            raise ValueError("saturation min must be below max")
        node = {"id": ident, "type": kind, "params": params,
                "x": number(raw_node["x"], "x", -10000, 10000),
                "y": number(raw_node["y"], "y", -10000, 10000),
                "label": printable_text(raw_node.get("label", kind), "label")}
        nodes.append(node)
        by_id[ident] = node
    substeps = 0
    for node in nodes:
        p = node["params"]
        if node["type"] == "massSpring":
            substeps += max(1, math.ceil(dt*max(math.sqrt(p["k"]/p["m"]), p["b"]/p["m"])/.2))
        elif node["type"] == "firstOrder":
            substeps += max(1, math.ceil(dt/(p["tau"]*.4)))
        else:
            substeps += 1
    if substeps > 25000 or substeps*steps > 20000000:
        raise ValueError("diagram exceeds browser integration workload limit")
    destinations, edge_ids, edges = set(), set(), []
    for edge in raw["edges"]:
        object_fields(edge, ("id", "from", "to"), "edge", ("id", "from", "to"))
        ident = identifier(edge["id"], "edge id")
        if ident in edge_ids:
            raise ValueError("duplicate edge id")
        edge_ids.add(ident)
        for end in ("from", "to"):
            endpoint = object_fields(edge[end], ("node", "port"), "edge endpoint", ("node", "port"))
            node_id = identifier(endpoint["node"], "endpoint node")
            if node_id not in by_id:
                raise ValueError("edge references missing node")
            kind = by_id[node_id]["type"]
            ports = BLOCKS[kind][0] if end == "to" else ([] if kind == "scope" else ["out"])
            if endpoint["port"] not in ports:
                raise ValueError("invalid edge port")
        destination = (edge["to"]["node"], edge["to"]["port"])
        if destination in destinations:
            raise ValueError("ambiguous input: more than one driver")
        destinations.add(destination)
        edges.append(edge)
    for node in nodes:
        for port in BLOCKS[node["type"]][0]:
            if (node["id"], port) not in destinations:
                raise ValueError("unconnected required input: " + node["id"]+"."+port)
    # State-only destinations break instantaneous dependence exactly as in browser.
    degree = {n["id"]: 0 for n in nodes}
    children = {n["id"]: [] for n in nodes}
    for edge in edges:
        src, dst = edge["from"]["node"], edge["to"]["node"]
        if by_id[dst]["type"] not in STATE_ONLY:
            degree[dst] += 1
            children[src].append(dst)
    queue, count = [key for key, value in degree.items() if value == 0], 0
    while queue:
        item = queue.pop()
        count += 1
        for child in children[item]:
            degree[child] -= 1
            if degree[child] == 0:
                queue.append(child)
    if count != len(nodes):
        raise ValueError("algebraic loop in direct-feedthrough blocks")
    return {"schema": SCHEMA, "settings": {"dt": dt, "duration": duration}, "nodes": nodes, "edges": edges}


def select_plant(raw, plant_node, input_unit=None, output_unit=None, watchdog_s=.5, input_limit=1000):
    diagram = validate_diagram(raw)
    if plant_node is None:
        raise ValueError("an explicit plant-node id is required; no automatic/ambiguous selection")
    matches = [node for node in diagram["nodes"] if node["id"] == plant_node]
    if len(matches) != 1:
        raise ValueError("selected plant node was not found")
    node = matches[0]
    matrix = plant_matrices(node["type"], node["params"])
    mechanical = node["type"] == "massSpring"
    if mechanical and ((input_unit is not None and input_unit != "N") or
                       (output_unit is not None and output_unit != "m")):
        raise ValueError("massSpring uses N input and m output; no implicit unit conversion")
    in_unit = printable_text(input_unit or ("N" if mechanical else "unspecified_input_unit"), "input unit", 40)
    out_unit = printable_text(output_unit or ("m" if mechanical else "unspecified_output_unit"), "output unit", 40)
    config = {"schema": _core.SCHEMA, "plant_id": node["id"], "plant_type": node["type"],
              "parameters": node["params"], **{key: matrix[key] for key in ("A", "B", "C", "D", "x0")},
              "state_order": ["position", "velocity"] if mechanical else ["output_state"],
              "state_units": ["m", "m/s"] if mechanical else [out_unit],
              "input_unit": in_unit, "output_unit": out_unit,
              "dt_s": diagram["settings"]["dt"], "requested_duration_s": diagram["settings"]["duration"],
              "watchdog_s": number(watchdog_s, "watchdog_s", .001, 10),
              "input_limit": number(input_limit, "input_limit", .001, 1e6),
              "comparison_input": 1.0,
              "boundary": "selected continuous plant only; original wiring/controllers/sources are excluded",
              "unit_note": "firstOrder units require user declaration; labels do not enforce dimensions",
              "evidence": "exported analytical model; external runtime and hardware execution not established"}
    if config["input_limit"] < 1:
        raise ValueError("input_limit must allow the unit-input comparison (>=1)")
    simulator = PlantSimulator(config)
    config["effective_duration_s"] = simulator.max_steps*simulator.dt
    config["substeps_per_tick"] = simulator.substeps
    return config


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load_diagram(path):
    path = Path(path)
    if path.stat().st_size > 1_000_000:
        raise ValueError("diagram exceeds 1 MB input limit")
    def invalid_constant(value):
        raise ValueError("nonfinite JSON value: " + value)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates,
                      parse_constant=invalid_constant)


def sci_matrix(rows):
    return "[" + "; ".join(" ".join(format(float(value), ".17g") for value in row) for row in rows) + "]"


def export_bundle(config, output):
    # Complete analytical/reference work before making the output concrete.
    sim = PlantSimulator(config)
    rows = [[0.0, 1.0, sim.snapshot()["output"], *sim.x]]
    while not sim.done:
        state = sim.advance(1.0)
        rows.append([state["simulation_time_s"], 1.0, state["output"], *state["state"]])
    out = Path(output)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("output must be a new or empty directory; existing exports are not overwritten")
    out.mkdir(parents=True, exist_ok=True)
    config_json = json.dumps(config, indent=2, allow_nan=False) + "\n"
    (out / "plant.json").write_text(config_json, encoding="utf-8")
    with (out / "reference.csv").open("w", newline="", encoding="utf-8") as stream:
        csv.writer(stream).writerows(rows)
    definitions = ["// Selected plant only. SI/declared units are recorded in plant.json."]
    for key in ("A", "B", "C", "D"):
        definitions.append(key + " = " + sci_matrix(config[key]) + ";")
    definitions += ["x0 = " + sci_matrix([[v] for v in config["x0"]]) + ";",
                    "sample_dt = " + format(config["dt_s"], ".17g") + ";",
                    "final_time = " + format(config["effective_duration_s"], ".17g") + ";",
                    "comparison_input = 1;",
                    "plant = syslin('c', A, B, C, D, x0);", ""]
    (out / "plant_data.sce").write_text("\n".join(definitions), encoding="utf-8")
    analysis = '''// Run in Scilab: exec("/absolute/export/path/scilab_analysis.sce", -1);
// Isolated plant under unit constant input from t=0; original graph excluded.
export_dir = get_absolute_file_path("scilab_analysis.sce");
exec(export_dir + "plant_data.sce", -1);
reference = csvRead(export_dir + "reference.csv", ",", ".");
t = reference(:, 1)';
function value = mech_unit_input(time)
    value = 1;
endfunction
// Use function input so supplied nonzero initial conditions retain their meaning.
[y, x] = csim(mech_unit_input, t, plant, x0, [1d-10, 1d-8]);
csvWrite([t', ones(t)', y', x'], export_dir + "scilab_response.csv", ",", ".", "%.17g");
output_error = max(abs(y' - reference(:, 3)));
state_error = max(abs(x' - reference(:, 4:$)));
mprintf("Maximum output difference versus Python RK4: %.9g\\n", output_error);
mprintf("Maximum state difference versus Python RK4: %.9g\\n", state_error);
// These differences require interpretation with units and a dt-convergence check.
scf(); plot(t, y); xtitle("Selected plant: unit-input response", "Time / s", "Output / declared unit");
// Frequency arguments are Hz. This is plant response, not closed-loop margins.
if norm(B) > 0 then
    scf(); bode(plant, 1d-3, 1d3);
else
    mprintf("B=0: input has no effect; skipped logarithmic zero-gain Bode plot.\\n");
end
'''
    (out / "scilab_analysis.sce").write_text(analysis, encoding="utf-8")
    xcos_setup = '''// Documented GUI construction workflow, not a generated native diagram.
export_dir = get_absolute_file_path("xcos_setup.sce");
exec(export_dir + "plant_data.sce", -1);
disp("Use the Xcos steps in README.md: STEP_FUNCTION -> CLSS -> CSCOPE; CLOCK_c -> scope event port.");
disp("Copy plant_data.sce numeric assignments into diagram context for a portable saved diagram.");
xcos();
'''
    (out / "xcos_setup.sce").write_text(xcos_setup, encoding="utf-8")
    atoms_setup = '''// Local inspection only. Core Scilab/Xcos functions need no extra ATOMS module here.
installed_modules = atomsGetInstalled();
disp(installed_modules);
// OPTIONAL: first verify a specific module, version, platform support and licence.
// Explicit user opt-in only: uncomment/edit the next lines to download/install it.
// requested_module = "REPLACE_WITH_REVIEWED_MODULE_NAME";
// requested_version = "REPLACE_WITH_REVIEWED_VERSION";
// atomsInstall([requested_module requested_version]);
// For an already installed reviewed module, explicitly load its code:
// atomsLoad([requested_module requested_version]);
'''
    (out / "atoms_setup.sce").write_text(atoms_setup, encoding="utf-8")
    shutil.copyfile(ASSETS / "README.md", out / "README.md")
    package = out / "ros2_ws" / "src" / "mechatronics_sim"
    module = package / "mechatronics_sim"
    module.mkdir(parents=True)
    (package / "resource").mkdir()
    (package / "resource" / "mechatronics_sim").write_text("", encoding="utf-8")
    (module / "__init__.py").write_text("", encoding="utf-8")
    (module / "plant.json").write_text(config_json, encoding="utf-8")
    shutil.copyfile(ASSETS / "sim_core.py", module / "sim_core.py")
    shutil.copyfile(ASSETS / "ros_node.py", module / "node.py")
    shutil.copyfile(ROOT / "LICENSE", package / "LICENSE")
    (package / "setup.py").write_text('''from setuptools import setup

setup(name="mechatronics_sim", version="0.1.0", packages=["mechatronics_sim"],
      package_data={"mechatronics_sim": ["plant.json"]},
      data_files=[("share/ament_index/resource_index/packages", ["resource/mechatronics_sim"]),
                  ("share/mechatronics_sim", ["package.xml", "LICENSE"])],
      install_requires=["setuptools"], zip_safe=False,
      maintainer="Mechatronics skill user", maintainer_email="maintainer@example.invalid",
      description="Selected plant educational simulation; no hardware bridge", license="MIT",
      entry_points={"console_scripts": ["plant_sim = mechatronics_sim.node:main"]})
''', encoding="utf-8")
    (package / "setup.cfg").write_text("[develop]\nscript_dir=$base/lib/mechatronics_sim\n[install]\ninstall_scripts=$base/lib/mechatronics_sim\n", encoding="utf-8")
    (package / "package.xml").write_text('''<?xml version="1.0"?>
<package format="3">
  <name>mechatronics_sim</name><version>0.1.0</version>
  <description>Selected plant educational simulation; no hardware bridge</description>
  <maintainer email="maintainer@example.invalid">Mechatronics skill user</maintainer>
  <license>MIT</license>
  <buildtool_depend>ament_python</buildtool_depend>
  <exec_depend>rclpy</exec_depend><exec_depend>std_msgs</exec_depend>
  <export><build_type>ament_python</build_type></export>
</package>
''', encoding="utf-8")
    return {"output_directory": str(out.resolve()), "plant_id": config["plant_id"],
            "reference_rows": len(rows), "xcos_mode": "documented GUI setup; no native diagram generated",
            "evidence": "files generated and Python reference computed; external runtime execution not established"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagram", required=True, type=Path)
    parser.add_argument("--plant-node", required=True, help="explicit browser node id")
    parser.add_argument("--out", required=True, type=Path, help="new or empty output directory")
    parser.add_argument("--input-unit", help="firstOrder input unit; declares, does not convert")
    parser.add_argument("--output-unit", help="firstOrder output unit; declares, does not convert")
    parser.add_argument("--watchdog-s", type=float, default=.5)
    parser.add_argument("--input-limit", type=float, default=1000, help="symmetric simulation-only input envelope")
    args = parser.parse_args(argv)
    try:
        config = select_plant(load_diagram(args.diagram), args.plant_node, args.input_unit,
                              args.output_unit, args.watchdog_s, args.input_limit)
        result = export_bundle(config, args.out)
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
