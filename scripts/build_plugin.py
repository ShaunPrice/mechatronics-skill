#!/usr/bin/env python3
"""Assemble reproducible plugin distributions from the canonical skill source."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

NAME = "mechatronics-engineering"
VERSION = "0.1.1"


def package_files(folder):
    return sorted(p for p in folder.rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts and p.name != ".DS_Store"
                  and p.suffix not in (".pyc", ".pyo"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def archive(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name, source in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, source.read_bytes())


def build(root, dist, skill_files):
    plugin = root / "plugins" / NAME
    canonical = root / "skills" / NAME
    target = plugin / "skills" / NAME
    # This directory is a generated copy; prune stale files when sources change.
    if target.is_symlink():
        raise ValueError("generated skill target must not be a symlink")
    if target.exists():
        shutil.rmtree(target)
    for source in skill_files:
        output = target / source.relative_to(canonical)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(source.read_bytes())
    for source, name in ((root / "LICENSE", "LICENSE"),
                         (root / "docs/CHATGPT-PLUGIN.md", "README.md")):
        (plugin / name).write_bytes(source.read_bytes())

    compatibility = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
    if compatibility["name"] != NAME or compatibility["version"] != VERSION:
        raise ValueError("plugin identity/version differs from builder")
    portable = {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"}
    identity = ("name", "version", "description", "author", "homepage",
                "repository", "license", "keywords")
    portable.update({key: compatibility[key] for key in identity})
    portable["extensions"] = {"com.openai": {"interface": compatibility["interface"]}}
    write_json(plugin / "plugin.json", portable)
    write_json(plugin / ".claude-plugin/plugin.json",
               {key: compatibility[key] for key in identity})

    files = package_files(plugin)
    archive(dist / f"{NAME}-plugin-{VERSION}.zip",
            [(f"{NAME}/{p.relative_to(plugin).as_posix()}", p) for p in files])
    marketplace = root / ".agents/plugins/marketplace.json"
    entries = [(f"mechatronics-marketplace/plugins/{NAME}/{p.relative_to(plugin).as_posix()}", p)
               for p in files]
    entries.append(("mechatronics-marketplace/.agents/plugins/marketplace.json", marketplace))
    archive(dist / f"mechatronics-marketplace-{VERSION}.zip", entries)
    write_json(dist / "plugin-manifest.json", {
        "name": NAME, "version": VERSION, "skill_version": "0.1.0",
        "files": {p.relative_to(plugin).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in files},
        "marketplace_sha256": hashlib.sha256(marketplace.read_bytes()).hexdigest(),
    })
    return {"plugin_files": len(files), "plugin_version": VERSION,
            "plugin_zip": f"{NAME}-plugin-{VERSION}.zip",
            "marketplace_zip": f"mechatronics-marketplace-{VERSION}.zip"}
