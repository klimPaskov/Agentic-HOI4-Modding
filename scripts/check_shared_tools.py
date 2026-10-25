"""Check that the tools shared with the upstream repository have not drifted.

`shared_tools.json` lists every file this package carries as a byte-identical copy of an upstream
tool (Chaos Redux is the upstream). Content is compared after normalising line endings to LF, so
a Windows checkout and a CI checkout hash the same.

	python scripts/check_shared_tools.py                      # copies match their recorded hashes
	python scripts/check_shared_tools.py --upstream <mod>     # copies also match an upstream checkout
	python scripts/check_shared_tools.py --upstream <mod> --write   # copy upstream files in and record them

A changed copy fails: change the upstream tool, then copy it here with `--write`. Project-specific
values belong in each tool's settings file (`project_settings.json`, `.tools/gfx/settings.json`),
which is not shared. Exit status: 0 in sync, 1 drift, 2 bad arguments or a missing file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = Path(__file__).with_name("shared_tools.json")


def normalised_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--upstream", type=Path, help="root of an upstream checkout to compare with")
    parser.add_argument("--write", action="store_true", help="copy the upstream files in and record their hashes")
    args = parser.parse_args(argv)
    if args.write and not args.upstream:
        parser.error("--write needs --upstream")
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    problems: list[str] = []
    for local, entry in sorted(lock["files"].items()):
        target = ROOT / local
        if args.upstream:
            source = args.upstream / entry["upstream"]
            if not source.is_file():
                print(f"MISSING upstream {entry['upstream']}", file=sys.stderr)
                return 2
            if args.write:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                entry["sha256"] = normalised_sha256(target)
            elif normalised_sha256(source) != normalised_sha256(target):
                problems.append(f"DRIFT: {local} differs from upstream {entry['upstream']}")
        if not target.is_file():
            print(f"MISSING {local}", file=sys.stderr)
            return 2
        if normalised_sha256(target) != entry["sha256"]:
            problems.append(f"DRIFT: {local} differs from its recorded upstream copy")
    if args.write:
        LOCK.write_text(json.dumps(lock, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Recorded {len(lock['files'])} shared files from {args.upstream}.")
        return 0
    for problem in problems:
        print(problem)
    if problems:
        print("Change the upstream tool, then copy it here with --upstream <checkout> --write.")
        return 1
    print(f"{len(lock['files'])} shared tool files match their upstream copies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
