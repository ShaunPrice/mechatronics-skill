#!/usr/bin/env python3
"""Independently validate browser exports with OpenUSD (optional usd-core SDK).

Run from the repository: python scripts/validate_openusd.py
Requires Node.js and pxr (e.g. usd-core==26.8 in a validation virtualenv).
This validates scene syntax and geometric transforms, not simulated physics.
"""
import json
import math
from pathlib import Path
import subprocess
import tempfile

from pxr import Gf, Usd, UsdGeom

ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / "skills/mechatronics-engineering/assets/browser-lab/usd.js"


def expected(p):
    yaw, shoulder, elbow = (math.radians(p[k]) for k in ("yaw", "shoulder", "elbow"))
    radius = p["l1"] * math.cos(shoulder) + p["l2"] * math.cos(shoulder + elbow)
    return (radius * math.cos(yaw), radius * math.sin(yaw),
            p["base"] + p["l1"] * math.sin(shoulder) + p["l2"] * math.sin(shoulder + elbow))


def export(mode, p, samples):
    js = """const fs=require('node:fs');
const U=require(process.argv[1]);
const x=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(x.mode==='pose' ? U.exportPose(x.p) :
 U.exportAnimation(x.p,x.samples,{timeCodesPerSecond:60}));"""
    return subprocess.run(["node", "-e", js, str(EXPORTER)],
                          input=json.dumps({"mode": mode, "p": p, "samples": samples}),
                          capture_output=True, text=True, check=True).stdout


def assert_scene(path, cases, animated=False):
    stage = Usd.Stage.Open(str(path))
    assert stage, "USD stage failed to open"
    assert stage.GetDefaultPrim().GetPath() == "/Robot"
    assert UsdGeom.GetStageMetersPerUnit(stage) == 1
    assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z
    assert stage.GetTimeCodesPerSecond() == 60
    tool = stage.GetPrimAtPath("/Robot/YawJoint/ShoulderJoint/ElbowJoint/Tool")
    assert tool, "Tool prim missing"
    assert any(prim.IsA(UsdGeom.Cube) for prim in stage.Traverse()), "No link geometry"
    for prim in stage.Traverse():
        assert not any("Physics" in api for api in prim.GetAppliedSchemas()), "Unexpected physics claim"
    error = 0
    for t, parameters in cases:
        code = Usd.TimeCode(t * 60) if animated else Usd.TimeCode.Default()
        position = UsdGeom.XformCache(code).GetLocalToWorldTransform(tool).Transform(Gf.Vec3d(0))
        error = max(error, max(abs(a-b) for a, b in zip(position, expected(parameters))))
    assert error < 1e-6, ("World transform differs from independent FK", error)
    return error


def main():
    baseline = dict(yaw=25, shoulder=30, elbow=-55, l1=1.2, l2=.9, base=.25)
    poses = [baseline, dict(yaw=-130, shoulder=-25, elbow=95, l1=.32, l2=.48, base=.12),
             dict(yaw=90, shoulder=90, elbow=-90, l1=2, l2=1, base=.5)]
    samples = [dict(t=0, yaw=25, shoulder=30, elbow=-55),
               dict(t=.5, yaw=70, shoulder=50, elbow=-15),
               dict(t=1, yaw=-20, shoulder=20, elbow=-65)]
    errors = []
    with tempfile.TemporaryDirectory(prefix="mechatronics-usd-") as td:
        for i, p in enumerate(poses):
            path = Path(td) / f"pose-{i}.usda"
            path.write_text(export("pose", p, []), encoding="utf-8")
            errors.append(assert_scene(path, [(0, p)]))
        path = Path(td) / "animation.usda"
        path.write_text(export("animation", baseline, samples), encoding="utf-8")
        cases = [(s["t"], dict(baseline, **{k: s[k] for k in ("yaw", "shoulder", "elbow")})) for s in samples]
        cases.append((.25, dict(baseline, yaw=47.5, shoulder=40, elbow=-35)))
        errors.append(assert_scene(path, cases, animated=True))
        stage = Usd.Stage.Open(str(path))
        assert stage.GetStartTimeCode() == 0 and stage.GetEndTimeCode() == 60
        rotation = stage.GetPrimAtPath("/Robot/YawJoint").GetAttribute("xformOp:rotateZ")
        assert rotation.GetTimeSamples() == [0, 30, 60]
    print(json.dumps({"status": "PASS", "usd_version": Usd.GetVersion(), "stages": 4,
                      "world_positions_checked": 7, "maximum_error_m": max(errors),
                      "scope": "USDA parsing, metadata, transform/FK parity and interpolation; no physics"}, indent=2))


if __name__ == "__main__":
    main()
