"""Numerical/export/schema checks; no ROS, Scilab or Xcos execution implied."""
import ast
import copy
import csv
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

from export_interfaces import (ASSETS, BLOCKS, ROOT, PlantSimulator, export_bundle,
                               load_diagram, sample_count, select_plant, validate_diagram)


def example(kind="massSpring", params=None):
    value = json.loads((ASSETS / "example-diagram.json").read_text())
    value["settings"] = {"dt": .01, "duration": 1}
    value["nodes"][1]["type"] = kind
    value["nodes"][1]["params"] = params or {}
    return value


class ModelTests(unittest.TestCase):
    def test_mass_spring_matrix_mapping_and_initial_conditions(self):
        config = select_plant(example(params={"m": 2, "b": 3, "k": 8,
                                              "initialPosition": .4, "initialVelocity": -.2}), "plant")
        self.assertEqual(config["A"], [[0, 1], [-4, -1.5]])
        self.assertEqual(config["B"], [[0], [.5]])
        self.assertEqual(config["C"], [[1, 0]])
        self.assertEqual(config["D"], [[0]])
        self.assertEqual(config["x0"], [.4, -.2])
        derivative = PlantSimulator(config).derivative([.4, -.2], 6)
        self.assertAlmostEqual(derivative[0], -.2)
        self.assertAlmostEqual(derivative[1], (6 - 3*(-.2) - 8*.4)/2)

    def test_first_order_mapping_and_exact_response(self):
        diagram = example("firstOrder", {"gain": 2, "tau": .5, "initial": 3})
        config = select_plant(diagram, "plant", "W", "K")
        self.assertEqual(config["A"], [[-2]])
        self.assertEqual(config["B"], [[4]])
        self.assertEqual(config["state_units"], ["K"])
        sim = PlantSimulator(config)
        for _ in range(50):
            sim.advance(4)
        self.assertAlmostEqual(sim.x[0], 8 + (3-8)*math.exp(-1), places=7)

    def test_critical_damping_analytical_step_and_dt_convergence(self):
        errors = []
        for dt in (.1, .025):
            diagram = example(params={"m": 1, "b": 2, "k": 1})
            diagram["settings"]["dt"] = dt
            sim = PlantSimulator(select_plant(diagram, "plant"))
            while not sim.done:
                sim.advance(1)
            self.assertAlmostEqual(sim.x[0], 1-2*math.exp(-1), places=6)
            self.assertAlmostEqual(sim.x[1], math.exp(-1), places=6)
            errors.append(abs(sim.x[0] - (1-2*math.exp(-1))))
        self.assertLess(errors[1], errors[0])

    def test_receipt_watchdog_and_no_wall_time_catchup(self):
        config = select_plant(example("firstOrder"), "plant", watchdog_s=.5)
        sim = PlantSimulator(config)
        sim.tick(10)
        self.assertEqual(sim.x, [0])
        self.assertTrue(sim.receive(2, 10.1))
        fresh = sim.tick(10.2)
        self.assertEqual(fresh["applied_input"], 2)
        self.assertFalse(fresh["input_stale"])
        stale = sim.tick(1000)
        self.assertEqual(stale["applied_input"], 0)
        self.assertTrue(stale["input_stale"])
        self.assertAlmostEqual(stale["simulation_time_s"], .03)
        self.assertLess(stale["state"][0], fresh["state"][0])

    def test_invalid_input_clears_command_and_backwards_clock(self):
        sim = PlantSimulator(select_plant(example(), "plant"))
        sim.receive(2, 1)
        self.assertFalse(sim.receive(math.nan, 1.1))
        self.assertEqual(sim.tick(1.2)["applied_input"], 0)
        sim.receive(2, 1.3)
        self.assertEqual(sim.tick(1.4)["applied_input"], 2)
        self.assertEqual(sim.tick(1.0)["applied_input"], 0)
        self.assertIsNone(sim.last_receipt)
        self.assertFalse(sim.receive(1e7, 1.5))

    def test_bounded_duration_and_edited_matrix_rejection(self):
        config = select_plant(example(), "plant")
        sim = PlantSimulator(config)
        for _ in range(150):
            sim.advance(1)
        self.assertTrue(sim.done)
        self.assertEqual(sim.index, 100)
        config["A"][0][0] = 1000
        with self.assertRaisesRegex(ValueError, "differs"):
            PlantSimulator(config)


class SchemaTests(unittest.TestCase):
    def test_explicit_selection_and_unsupported_block(self):
        for identifier in (None, "missing", "input"):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                select_plant(example(), identifier)
        with self.assertRaisesRegex(ValueError, "no implicit unit conversion"):
            select_plant(example(), "plant", "kgf", "m")

    def test_unknown_fields_nonfinite_bounds_and_reserved_id(self):
        diagrams = []
        raw = example(); raw["unexpected"] = 1; diagrams.append(raw)
        raw = example(); raw["nodes"][1]["params"]["fake"] = 1; diagrams.append(raw)
        raw = example(); raw["nodes"][1]["params"]["m"] = math.nan; diagrams.append(raw)
        raw = example(); raw["nodes"][1]["params"]["m"] = .001; diagrams.append(raw)
        raw = example(); raw["nodes"][1]["params"]["m"] = 10**400; diagrams.append(raw)
        raw = example(); raw["settings"]["dt"] = True; diagrams.append(raw)
        raw = example(); raw["nodes"][0]["id"] = "constructor"; diagrams.append(raw)
        for raw in diagrams:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                validate_diagram(raw)

    def test_duplicate_unconnected_and_ambiguous_graph(self):
        diagrams = []
        raw = example(); raw["nodes"].append(copy.deepcopy(raw["nodes"][0])); diagrams.append(raw)
        raw = example(); raw["edges"].pop(0); diagrams.append(raw)
        raw = example(); edge = copy.deepcopy(raw["edges"][0]); edge["id"] = "duplicate_driver"; raw["edges"].append(edge); diagrams.append(raw)
        raw = example(); raw["nodes"][1]["type"] = "gain"; raw["nodes"][1]["params"] = {}; raw["edges"][0]["from"]["node"] = "plant"; diagrams.append(raw)
        for raw in diagrams:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                validate_diagram(raw)

    def test_json_duplicate_keys_and_nonfinite_tokens(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for payload in ('{"schema":"a","schema":"b"}', '{"value":NaN}', '{"value":Infinity}'):
                path.write_text(payload)
                with self.assertRaises(ValueError):
                    load_diagram(path)

    def test_sample_count_rounding(self):
        self.assertEqual(sample_count(.3, .1), 3)
        self.assertEqual(sample_count(.3 + 1e-14, .1), 3)
        self.assertEqual(sample_count(.301, .1), 4)

    @unittest.skipUnless(shutil.which("node"), "optional Node parity check; exporter itself is standard-library Python")
    def test_browser_schema_bounds_presets_and_reserved_id_parity(self):
        command = '''const B=require(process.argv[1]);
const presets=[B.createDefaultDiagram(),B.createThermalDiagram(),B.createTankDiagram()];
const cases=[...presets];
for(const settings of [{dt:.1,duration:.3},{dt:.1,duration:.301}]){const d=B.createDefaultDiagram();d.settings=settings;cases.push(d);}
const bad=B.createDefaultDiagram();bad.nodes[0].id='constructor';cases.push(bad);
const badBound=B.createDefaultDiagram();badBound.nodes.find(n=>n.type==='massSpring').params.m=.001;cases.push(badBound);
process.stdout.write(JSON.stringify({schema:B.SCHEMA,library:B.library,bounds:B.bounds,cases:cases.map(d=>{try{const v=B.validateDiagram(d);return {d,ok:true,stepCount:v.stepCount};}catch(e){return {d,ok:false};}})}));'''
        process = subprocess.run(["node", "-e", command, str(ROOT / "assets/browser-lab/block-engine.js")],
                                 check=True, capture_output=True, text=True, timeout=10)
        browser = json.loads(process.stdout)
        self.assertEqual(browser["schema"], "mechatronics-block-diagram/v1")
        self.assertEqual(set(browser["library"]), set(BLOCKS))
        for kind, (inputs, defaults, bounds) in BLOCKS.items():
            self.assertEqual(browser["library"][kind]["inputs"], inputs)
            self.assertEqual(browser["library"][kind]["defaults"], defaults)
            self.assertEqual(browser["bounds"][kind], {k: list(v) for k, v in bounds.items()})
        for case in browser["cases"]:
            if case["ok"]:
                result = validate_diagram(case["d"])
                self.assertEqual(sample_count(result["settings"]["duration"], result["settings"]["dt"]), case["stepCount"])
                for node in result["nodes"]:
                    if node["type"] in ("massSpring", "firstOrder"):
                        config = select_plant(case["d"], node["id"])
                        self.assertEqual(config["parameters"], node["params"])
            else:
                with self.assertRaises(ValueError):
                    validate_diagram(case["d"])


class ExportTests(unittest.TestCase):
    def test_export_numeric_files_generated_python_xml_and_core(self):
        config = select_plant(example(), "plant")
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "export"
            report = export_bundle(config, out)
            self.assertEqual(report["reference_rows"], 101)
            with (out / "reference.csv").open() as stream:
                rows = [[float(v) for v in row] for row in csv.reader(stream)]
            self.assertEqual(rows[0], [0, 1, 0, 0, 0])
            self.assertAlmostEqual(rows[-1][0], 1)
            self.assertTrue(all(math.isfinite(v) for row in rows for v in row))
            data = (out / "plant_data.sce").read_text()
            for key in ("A", "B", "C", "D"):
                literal = re.search(r"^"+key+r" = \[([^\]]+)\];", data, re.M).group(1)
                self.assertEqual([[float(value) for value in row.split()] for row in literal.split(";")], config[key])
            analysis = (out / "scilab_analysis.sce").read_text()
            self.assertIn("csim(mech_unit_input, t, plant, x0", analysis)
            self.assertIn("bode(plant", analysis)
            self.assertIn("reference(:, 4:$)", analysis)
            self.assertIn("xcos();", (out / "xcos_setup.sce").read_text())
            self.assertFalse(list(out.glob("*.zcos")))
            atoms = [line for line in (out / "atoms_setup.sce").read_text().splitlines() if not line.lstrip().startswith("//")]
            self.assertNotIn("atomsInstall", "\n".join(atoms))
            self.assertNotIn("atomsLoad", "\n".join(atoms))
            package = out / "ros2_ws/src/mechatronics_sim"
            for source in package.rglob("*.py"):
                ast.parse(source.read_text(), filename=str(source))
            manifest = ET.parse(package / "package.xml").getroot()
            self.assertEqual(manifest.findtext("export/build_type"), "ament_python")
            self.assertEqual({el.text for el in manifest.findall("exec_depend")}, {"rclpy", "std_msgs"})
            spec = importlib.util.spec_from_file_location("generated_interface_core", package / "mechatronics_sim/sim_core.py")
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            with (package / "mechatronics_sim/plant.json").open() as stream:
                sim = module.PlantSimulator(json.load(stream))
            while not sim.done:
                sample = sim.advance(1)
            self.assertAlmostEqual(sample["output"], rows[-1][2])
            with self.assertRaisesRegex(ValueError, "not overwritten"):
                export_bundle(config, out)

    def test_cli_smoke(self):
        with tempfile.TemporaryDirectory() as temporary:
            diagram = Path(temporary) / "diagram.json"
            diagram.write_text(json.dumps(example("firstOrder", {"gain": .2, "tau": 100, "initial": 0})))
            process = subprocess.run([__import__("sys").executable, "-B", str(ROOT / "scripts/export_interfaces.py"),
                                      "--diagram", str(diagram), "--plant-node", "plant", "--out", str(Path(temporary)/"kit"),
                                      "--input-unit", "W", "--output-unit", "K"],
                                     capture_output=True, text=True, check=True, timeout=20)
            report = json.loads(process.stdout)
            self.assertEqual(report["plant_id"], "plant")
            self.assertEqual(report["reference_rows"], 101)


if __name__ == "__main__":
    unittest.main()
