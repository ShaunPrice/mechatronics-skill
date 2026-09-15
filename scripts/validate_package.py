#!/usr/bin/env python3
"""Check package structure, local links, archive safety/integrity and generated parity."""
import hashlib
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from build_packages import ROOT, SKILL, NAME, VERSION, source_files, text


class LocalAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets=[]
    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for key,value in attrs if key in ("src","href","poster") and value)


def main():
    errors=[]
    body=text(SKILL/"SKILL.md")
    match=re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n",body)
    if not match or match.group(1)!=NAME: errors.append("skill name/frontmatter mismatch")
    elif len(match.group(2))>200: errors.append("description exceeds conservative 200-character cross-platform limit")
    if len(text(ROOT/"integrations/chatgpt/Instructions.txt"))>8000: errors.append("hosted instructions exceed 8000 characters")
    files=source_files()
    check_markdown=(list((ROOT/"docs").glob("*.md"))+list((ROOT/"validation").glob("*.md"))
                    +list((ROOT/"integrations/ros2-docker").rglob("*.md"))
                    +[ROOT/"README.md"]+[p for p in files if p.suffix==".md"])
    count=0
    for p in check_markdown:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)",text(p)):
            if target.startswith(("http://","https://","mailto:","#")): continue
            target=target.split("#",1)[0]
            if not (p.parent/target).exists(): errors.append(f"broken link: {p.relative_to(ROOT)} -> {target}")
            count+=1
    for p in (ROOT/"docs").glob("*.html"):
        parser=LocalAssets();parser.feed(text(p))
        for target in parser.targets:
            if target.startswith(("http://","https://","#","data:")): continue
            if not (p.parent/target.split("#",1)[0]).is_file(): errors.append(f"broken HTML asset: {p.relative_to(ROOT)} -> {target}")
            count+=1
    media=ROOT/"docs/media"
    recording=json.loads(text(media/"recording.json"))
    media_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in media.iterdir() if p.suffix in (".jpg",".mp4",".vtt")}
    if media_hashes!=recording["assets"]: errors.append("recording media hashes differ from documented assets")
    for p in files:
        if p.suffix in (".md",".txt",".yaml",".js",".html",".py",".css",".sce",".json"):
            s=text(p)
            if re.search(r"/Users/|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{24,}",s): errors.append(f"private path/credential pattern: {p.relative_to(SKILL)}")
    dist=ROOT/"dist"
    manifest=json.loads(text(dist/"manifest.json"))
    expected={p.relative_to(SKILL).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    if expected!=manifest["files"]: errors.append("manifest differs from source")
    with zipfile.ZipFile(dist/f"{NAME}-{VERSION}.zip") as z:
        if z.testzip(): errors.append("archive CRC error")
        names=z.namelist()
        if len(names)!=len(set(names)): errors.append("duplicate archive entries")
        if any(Path(n).is_absolute() or ".." in Path(n).parts or not n.startswith(NAME+"/") for n in names): errors.append("unsafe/unexpected archive layout")
        if set(names)!={NAME+"/"+p for p in expected}: errors.append("archive/source file set differs")
        for p,digest in expected.items():
            if hashlib.sha256(z.read(NAME+"/"+p)).hexdigest()!=digest: errors.append("archive mismatch: "+p)
    if text(SKILL/"LICENSE")!=text(ROOT/"LICENSE"): errors.append("licence copies differ")
    python_bundle=text(ROOT/"integrations/chatgpt/Python-examples.txt")
    for p in files:
        if p.parent==SKILL/"assets/interfaces" and p.suffix in (".py", ".sce", ".json"):
            entry=f"=== FILE: {p.relative_to(SKILL).as_posix()} ===\n{text(p)}"
            if entry not in python_bundle: errors.append(f"missing/stale hosted interface companion: {p.name}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(json.dumps({"status":"PASS","skill_files":len(files),"local_links_checked":count,"archive_and_manifest_match":True},indent=2))


if __name__=="__main__":
    main()
