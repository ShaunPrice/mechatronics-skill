#!/usr/bin/env python3
"""Build portable skill and hosted-reference packages using only the standard library."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "mechatronics-engineering"
VERSION = "0.1.0"
SKILL = ROOT/"skills"/NAME


def text(path):
    return path.read_text(encoding="utf-8")


def source_files():
    return sorted(p for p in SKILL.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store" and p.suffix not in (".pyc", ".pyo"))


def knowledge_links(content):
    def replace(match):
        label, target = match.groups()
        if target.startswith(("https://", "http://", "#")):
            return match.group(0)
        return f"{label} (source file: {target})"
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, content)


def standalone_browser(entry="index.html"):
    lab = SKILL/"assets/browser-lab"
    page = text(lab/entry)
    def local_file(rel):
        p = (lab/rel).resolve()
        if lab.resolve() not in p.parents or not p.is_file():
            raise ValueError(f"non-local/missing browser asset: {rel}")
        return p
    def style(match):
        return "<style>\n"+text(local_file(match.group(1)))+"\n</style>"
    def script(match):
        body=text(local_file(match.group(1))).replace("</script", "<\\/script")
        return "<script>\n"+body+"\n</script>"
    page = re.sub(r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>', style, page)
    page = re.sub(r'<script\s+src="([^"]+)"\s*></script>', script, page)
    if re.search(r'<script[^>]+src=|<link[^>]+stylesheet', page):
        raise ValueError("uninlined stylesheet/script in standalone browser")
    return page.replace('href="builder.html"', 'href="mechatronics-system-builder.html"').replace('href="index.html"', 'href="mechatronics-browser-workbench.html"')


def main():
    dist=ROOT/"dist"; dist.mkdir(exist_ok=True)
    integration=ROOT/"integrations/chatgpt"; integration.mkdir(parents=True,exist_ok=True)
    (SKILL/"LICENSE").write_text(text(ROOT/"LICENSE"),encoding="utf-8")
    references=sorted((SKILL/"references").glob("*.md"))
    dossier=SKILL/"assets/project-dossier-template.md"
    knowledge=[f"# Mechatronics Engineering Knowledge\n\nVersion {VERSION}. Use with Instructions.txt. Original reference material under the accompanying MIT licence.\n"]
    for p in references+[dossier,SKILL/"assets/interfaces/README.md"]:
        knowledge.append(f"\n---\n\n## Source: {p.relative_to(SKILL)}\n\n"+knowledge_links(text(p)))
    (integration/"Mechatronics-knowledge.md").write_text("\n".join(knowledge),encoding="utf-8")
    py=["Mechatronics Python examples and interface companion files — MIT licensed. Python 3.9+ standard library for numerical examples. The interface exporter also uses the standard library; generated ROS adapters require their ROS environment. Extract every required file into the shown paths under one skill folder, including the Scilab templates and example diagram; this combined text is not executable.\n"]
    interface_files=sorted(p for p in (SKILL/"assets/interfaces").iterdir() if p.is_file() and p.suffix in (".py", ".sce", ".json"))
    for p in sorted((SKILL/"scripts").glob("*.py"))+interface_files:
        py.append(f"\n=== FILE: {p.relative_to(SKILL).as_posix()} ===\n{text(p)}")
    (integration/"Python-examples.txt").write_text("\n".join(py),encoding="utf-8")
    browser=standalone_browser()
    (dist/"mechatronics-browser-workbench.html").write_text(browser,encoding="utf-8")
    (integration/"Browser-simulator-template.txt").write_text("Mechatronics Browser Workbench — MIT licensed. The source below is a complete standalone HTML application. Save the content beginning with <!doctype html> (case insensitive) as an .html file. Adapt equations and geometry to the user's problem; preserve evidence labels.\n\n"+browser,encoding="utf-8")
    builder=standalone_browser("builder.html")
    (dist/"mechatronics-system-builder.html").write_text(builder,encoding="utf-8")
    for name in ("browser-workbench-demo.mp4", "browser-workbench-demo.vtt"):
        (dist/name).write_bytes((ROOT/"docs/media"/name).read_bytes())
    (integration/"System-builder-template.txt").write_text("Mechatronics System Builder — MIT licensed. Save the source from <!doctype html> onward as mechatronics-system-builder.html. This is a scalar signal-flow simulator with a visual editor, not Xcos file compatibility or an acausal physical-network solver.\n\n"+builder,encoding="utf-8")
    zip_path=dist/f"{NAME}-{VERSION}.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for p in source_files():
            info=zipfile.ZipInfo(f"{NAME}/{p.relative_to(SKILL).as_posix()}",date_time=(2026,9,15,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644 << 16
            z.writestr(info,p.read_bytes())
    skill_path=zip_path.with_suffix(".skill")
    skill_path.write_bytes(zip_path.read_bytes())
    manifest={"name":NAME,"version":VERSION,"files":{p.relative_to(SKILL).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files()}}
    (dist/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    checksums=[]
    for p in sorted(dist.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS": checksums.append(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.name)
    (dist/"SHA256SUMS").write_text("\n".join(checksums)+"\n",encoding="utf-8")
    print(json.dumps({"skill_files":len(manifest["files"]),"reference_files":len(references),"zip":str(zip_path.relative_to(ROOT)),"claude_skill":str(skill_path.relative_to(ROOT)),"browser":str((dist/"mechatronics-browser-workbench.html").relative_to(ROOT)),"instructions_characters":len(text(integration/"Instructions.txt"))},indent=2))


if __name__=="__main__":
    main()
