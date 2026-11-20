#!/usr/bin/env python3
"""Generate and validate the verified Mad Mallard README badge block."""
from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path
from urllib.parse import quote

START="<!-- madmallard-badges:start -->"
END="<!-- madmallard-badges:end -->"
LICENSE_FILES=("LICENSE","LICENSE.md","LICENSE.txt","COPYING")

def read(path: Path) -> str:
    try: return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError): return ""

def cmd(*args: str, cwd: Path) -> str:
    try:
        p=subprocess.run(args,cwd=cwd,text=True,capture_output=True,timeout=10,check=False)
        return p.stdout.strip() if p.returncode==0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""

def repo_slug(root: Path) -> str|None:
    origin=cmd("git","remote","get-url","origin",cwd=root)
    m=re.search(r"(?:github\.com[:/])([\w.-]+/[\w.-]+?)(?:\.git)?$",origin)
    return m.group(1) if m else None

def req_version(text: str, package: str) -> str|None:
    m=re.search(rf"(?im)^\s*{re.escape(package)}(?:\[[^\]]+\])?\s*~?=+\s*([0-9]+(?:\.[0-9]+){{1,2}})",text)
    return m.group(1) if m else None

def tech(root: Path):
    out=[]
    dockerfile=read(root/"Dockerfile")
    m=re.search(r"(?im)^FROM\s+python:([0-9]+(?:\.[0-9]+){1,2})(?:[-@]|\s|$)",dockerfile)
    if m: out.append(("Python","3776AB","python",m.group(1)))
    req=read(root/"requirements.txt")
    dv=req_version(req,"Django")
    if dv: out.append(("Django","092E20","django",dv))
    compose=read(root/"compose.yaml")+read(root/"compose.yml")
    settings=read(root/"videoshare"/"settings.py")
    if "sqlite3" in settings.lower() or "DJANGO_DB_PATH" in compose:
        out.append(("SQLite","003B57","sqlite",None))
    if dockerfile: out.append(("Docker","2496ED","docker",None))
    if compose.strip(): out.append(("Docker Compose","2496ED","docker",None))
    tfwf=read(root/".github"/"workflows"/"terraform.yml")
    tm=re.search(r"terraform_version:\s*[\"']?v?([0-9]+(?:\.[0-9]+){1,2})",tfwf)
    if (root/"terraform").is_dir(): out.append(("Terraform","844FBA","terraform",tm.group(1) if tm else None))
    versions=read(root/"terraform"/"environments"/"dev"/"versions.tf")
    if "hashicorp/aws" in versions: out.append(("AWS target","232F3E","amazonwebservices",None))
    return out

def shield(label,color,logo,version=None):
    encoded_label=quote(label,safe="").replace("-","--")
    if version:
        encoded_version=quote(version,safe="").replace("-","--")
        path=f"{encoded_label}-{encoded_version}-{color}"
    else:
        path=f"{encoded_label}-{color}"
    return f"https://img.shields.io/badge/{path}?logo={logo}&logoColor=white"

def workflows(root: Path):
    folder=root/".github"/"workflows"
    return sorted(p for p in folder.glob("*") if p.suffix in {".yml",".yaml"} and p.is_file()) if folder.exists() else []

def generate(root: Path) -> str:
    slug=repo_slug(root)
    rows=[]
    first=[f"![{label}]({shield(label,color,logo,version)})" for label,color,logo,version in tech(root)]
    if first: rows.append(" ".join(first))
    second=[]
    if slug:
        for wf in workflows(root):
            path=quote(wf.name,safe="")
            url=f"https://github.com/{slug}/actions/workflows/{path}"
            second.append(f"[![{wf.stem}](https://github.com/{slug}/actions/workflows/{path}/badge.svg)]({url})")
        license_name=next((n for n in LICENSE_FILES if (root/n).is_file()),None)
        if license_name:
            second.append(f"[![License](https://img.shields.io/github/license/{slug})](https://github.com/{slug}/blob/HEAD/{license_name})")
        if cmd("gh","release","view","--repo",slug,"--json","tagName","--jq",".tagName",cwd=root):
            second.append(f"[![Release](https://img.shields.io/github/v/release/{slug})](https://github.com/{slug}/releases/latest)")
        second += [
            f"[![Issues](https://img.shields.io/github/issues/{slug})](https://github.com/{slug}/issues)",
            f"[![Pull requests](https://img.shields.io/github/issues-pr/{slug})](https://github.com/{slug}/pulls)",
        ]
    if second: rows.append(" ".join(second))
    return START+"\n"+"\n\n".join(rows)+"\n"+END

def apply(root: Path, write: bool):
    target=root/"README.md"
    if not target.is_file(): raise ValueError(f"{root}: README.md missing")
    original=read(target); block=generate(root)
    if original.count(START)!=original.count(END) or original.count(START)>1:
        raise ValueError(f"{root}: malformed or duplicate badge markers")
    if START in original:
        updated=original[:original.index(START)]+block+original[original.index(END)+len(END):]
    else:
        lines=original.splitlines(keepends=True)
        idx=next((i for i,line in enumerate(lines) if line.startswith("# ")),None)
        if idx is None: raise ValueError(f"{root}: README has no H1")
        lines.insert(idx+1,"\n"+block+"\n")
        updated="".join(lines)
    if updated==original: return False,"unchanged"
    if write: target.write_text(updated,encoding="utf-8")
    return True,("updated" if write else "would update")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--repo",action="append",default=[]); p.add_argument("--mode",choices=("dry-run","write","check"),default="dry-run")
    args=p.parse_args(); failed=False
    for path in args.repo or ["."]:
        root=Path(path).expanduser().resolve()
        try:
            changed,outcome=apply(root,args.mode=="write"); print(f"{root}: {outcome}")
            if changed and args.mode=="check": failed=True
        except ValueError as exc:
            print(f"ERROR: {exc}",file=sys.stderr); failed=True
    return int(failed)

if __name__=="__main__": raise SystemExit(main())
