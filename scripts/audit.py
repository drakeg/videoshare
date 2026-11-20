#!/usr/bin/env python3
"""Read-only audit of required Mad Mallard repository documents."""
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUIRED = ("README.md","AGENTS.md","CONTRIBUTING.md","SPRINTS.md","BACKLOG.md","RELEASES.md","SECURITY.md")

def audit(root: Path) -> dict[str, object]:
    return {"repository": str(root), "missing": [name for name in REQUIRED if not (root / name).is_file()]}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", action="append", default=[])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    reports = [audit(Path(path).expanduser().resolve()) for path in args.repo or ["."]]
    print(json.dumps(reports, indent=2))
    return int(args.check and any(report["missing"] for report in reports))

if __name__ == "__main__":
    raise SystemExit(main())
