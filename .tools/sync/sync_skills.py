#!/usr/bin/env python3
"""Mirror the canonical `.claude/skills/` library for runtimes that read another folder.

Claude Code, Cursor, and OpenCode read `.claude/skills/` directly. Codex and
DeepSeek Harness read `.agents/skills/`, and Qoder reads `.qoder/skills/`.
This tool keeps those folders identical to the canonical library.

    python .tools/sync/sync_skills.py                 # refresh every mirror that exists
    python .tools/sync/sync_skills.py --target agents # create or refresh .agents/skills
    python .tools/sync/sync_skills.py --check         # report drift, write nothing

Copies are the default because HOI4 Mod Setup tracks the mirrored files it
installs. `--mode link` replaces a mirror folder with a directory junction
(Windows) or symbolic link (elsewhere) for a project that does not use the app.
A skill folder that exists only in a mirror is reported, never deleted.

Standard library only; runs on Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

MOD_ROOT = Path(__file__).resolve().parents[2]
CANONICAL = MOD_ROOT / ".claude" / "skills"
TARGETS: Dict[str, Path] = {
    "agents": MOD_ROOT / ".agents" / "skills",
    "qoder": MOD_ROOT / ".qoder" / "skills",
}
IGNORED = {"__pycache__", ".DS_Store"}


def canonical_skills() -> List[Path]:
    if not CANONICAL.is_dir():
        raise SystemExit(f"ERROR: canonical skill folder not found: {CANONICAL.relative_to(MOD_ROOT)}")
    return sorted(path for path in CANONICAL.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())


def is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    if os.name == "nt" and path.exists():
        try:
            return bool(os.lstat(path).st_file_attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
        except (AttributeError, OSError):
            return False
    return False


def files_under(root: Path) -> Dict[str, Path]:
    found: Dict[str, Path] = {}
    for path in root.rglob("*"):
        if path.is_file() and not any(part in IGNORED for part in path.relative_to(root).parts) and path.suffix != ".pyc":
            found[path.relative_to(root).as_posix()] = path
    return found


def drift_for(skill: Path, mirror: Path) -> List[str]:
    source = files_under(skill)
    target = files_under(mirror) if mirror.is_dir() else {}
    problems = [f"missing {name}" for name in sorted(source.keys() - target.keys())]
    problems += [f"extra {name}" for name in sorted(target.keys() - source.keys())]
    problems += [f"changed {name}" for name in sorted(source.keys() & target.keys()) if not filecmp.cmp(source[name], target[name], shallow=False)]
    return problems


def copy_skill(skill: Path, mirror: Path) -> int:
    written = 0
    source = files_under(skill)
    target = files_under(mirror) if mirror.is_dir() else {}
    for name, path in source.items():
        destination = mirror / name
        if name in target and filecmp.cmp(path, target[name], shallow=False):
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        written += 1
    for name in sorted(target.keys() - source.keys()):
        target[name].unlink()
        written += 1
    return written


def link_folder(mirror_root: Path) -> None:
    if mirror_root.exists() and not is_link(mirror_root):
        shutil.rmtree(mirror_root)
    elif is_link(mirror_root):
        return
    mirror_root.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(mirror_root), str(CANONICAL)], check=True, stdout=subprocess.DEVNULL)
    else:
        mirror_root.symlink_to(os.path.relpath(CANONICAL, mirror_root.parent), target_is_directory=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror .claude/skills for runtimes that read another skill folder.")
    parser.add_argument("--target", action="append", choices=sorted(TARGETS), help="mirror to create or refresh (repeatable); default: every mirror that already exists")
    parser.add_argument("--mode", choices=("copy", "link"), default="copy")
    parser.add_argument("--check", action="store_true", help="report drift without writing; exit 1 when a mirror is out of date")
    args = parser.parse_args()

    targets = args.target or [key for key, path in TARGETS.items() if path.exists()]
    if not targets:
        print("No skill mirrors exist. Claude Code, Cursor, and OpenCode read .claude/skills directly; pass --target agents for Codex or DSH, or --target qoder for Qoder.")
        return 0
    skills = canonical_skills()
    names = {skill.name for skill in skills}
    failures = 0
    for key in targets:
        mirror_root = TARGETS[key]
        label = mirror_root.relative_to(MOD_ROOT).as_posix()
        if is_link(mirror_root):
            print(f"{label}: linked to the canonical library.")
            continue
        if args.mode == "link" and not args.check:
            link_folder(mirror_root)
            print(f"{label}: now linked to .claude/skills.")
            continue
        extra = sorted(path.name for path in mirror_root.iterdir() if path.is_dir() and path.name not in names) if mirror_root.is_dir() else []
        for name in extra:
            print(f"NOTE: {label}/{name} has no canonical source in .claude/skills and was left alone.")
        if args.check:
            problems = {skill.name: drift_for(skill, mirror_root / skill.name) for skill in skills}
            problems = {name: items for name, items in problems.items() if items}
            for name, items in problems.items():
                print(f"DRIFT: {label}/{name}: {', '.join(items[:5])}{' ...' if len(items) > 5 else ''}")
            if problems:
                failures += 1
            else:
                print(f"{label}: {len(skills)} skills in sync.")
            continue
        written = sum(copy_skill(skill, mirror_root / skill.name) for skill in skills)
        print(f"{label}: {len(skills)} skills; {written} file(s) written or removed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
