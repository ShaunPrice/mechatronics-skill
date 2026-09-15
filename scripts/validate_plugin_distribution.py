#!/usr/bin/env python3
"""Validate plugin source parity, metadata and installable archive layouts."""
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from build_plugin import NAME, VERSION, package_files


def validate(root):
    errors = []
    plugin = root / "plugins" / NAME
    dist = root / "dist"
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    hashes = lambda base: {p.relative_to(base).as_posix(): digest(p) for p in package_files(base)}
    if hashes(root / "skills" / NAME) != hashes(plugin / "skills" / NAME):
        errors.append("plugin skill copy differs from canonical source; rebuild")
    files = hashes(plugin)
    manifest = json.loads((dist / "plugin-manifest.json").read_text())
    if manifest.get("files") != files or manifest.get("version") != VERSION:
        errors.append("plugin distribution manifest differs from source/version")
    portable = json.loads((plugin / "plugin.json").read_text())
    compatibility = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
    claude = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
    identity = ("name", "version", "description", "author", "homepage", "repository", "license", "keywords")
    for key in identity:
        if not portable.get(key) or portable.get(key) != compatibility.get(key) or portable.get(key) != claude.get(key):
            errors.append(f"plugin manifest identity mismatch: {key}")
    if portable.get("name") != NAME or portable.get("version") != VERSION or portable.get("license") != "MIT":
        errors.append("plugin identity/version/licence mismatch")
    if portable.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        errors.append("wrong portable plugin schema")
    if set(portable) != set(identity) | {"$schema", "extensions"}:
        errors.append("unexpected portable manifest fields")
    if portable.get("extensions") != {"com.openai": {"interface": compatibility.get("interface")}}:
        errors.append("portable OpenAI metadata differs from compatibility manifest")
    if compatibility.get("skills") != "./skills/":
        errors.append("wrong compatibility skill path")
    prompts = compatibility.get("interface", {}).get("defaultPrompt", [])
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or any(not isinstance(p, str) or len(p) > 128 for p in prompts):
        errors.append("invalid plugin starter prompts")
    for actual, expected in ((plugin / "LICENSE", root / "LICENSE"),
                             (plugin / "README.md", root / "docs/CHATGPT-PLUGIN.md")):
        if actual.read_bytes() != expected.read_bytes():
            errors.append(f"generated plugin file differs: {actual.name}")
    for p in plugin.rglob("*"):
        if p.is_symlink():
            errors.append(f"plugin must be self-contained, found symlink: {p.name}")
    for p in package_files(plugin):
        if p.suffix in (".json", ".md", ".txt", ".yaml", ".py", ".js", ".html", ".sce"):
            if re.search(r"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{24,}|\[TODO:", p.read_text()):
                errors.append(f"private path/credential/placeholder pattern in plugin: {p.name}")
    catalog_path = root / ".agents/plugins/marketplace.json"
    catalog = json.loads(catalog_path.read_text())
    entry = {"name": NAME, "source": {"source": "local", "path": f"./plugins/{NAME}"},
             "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}
    if catalog.get("name") != "personal" or catalog.get("plugins") != [entry]:
        errors.append("unexpected marketplace identity/source/policy")
    if manifest.get("marketplace_sha256") != digest(catalog_path):
        errors.append("marketplace digest differs")
    bundles = {
        f"{NAME}-plugin-{VERSION}.zip": {f"{NAME}/{p}": h for p, h in files.items()},
        f"mechatronics-marketplace-{VERSION}.zip": {
            **{f"mechatronics-marketplace/plugins/{NAME}/{p}": h for p, h in files.items()},
            "mechatronics-marketplace/.agents/plugins/marketplace.json": digest(catalog_path)},
    }
    for filename, expected in bundles.items():
        with zipfile.ZipFile(dist / filename) as archive:
            names = archive.namelist()
            if archive.testzip() or len(names) != len(set(names)):
                errors.append(f"corrupt/duplicate archive entries: {filename}")
            for info in archive.infolist():
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in info.filename or stat.S_ISLNK(info.external_attr >> 16):
                    errors.append(f"unsafe plugin archive entry: {info.filename}")
            actual = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in names}
            if actual != expected:
                errors.append(f"plugin archive differs from source: {filename}")
    return errors


if __name__ == "__main__":
    errors = validate(Path(__file__).resolve().parents[1])
    if errors:
        raise SystemExit("\n".join(errors))
    print("PASS: plugin manifests, source parity, marketplace, safe archives and hashes")
