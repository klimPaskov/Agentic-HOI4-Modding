#!/usr/bin/env python3
"""Build a curated, flat HOI4 project bundle without changing project sources."""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

DEFAULT_INCLUDE = [
    "AGENTS.md", "CLAUDE.md", "README.md", "descriptor.mod", "*.mod",
    ".claude/skills/*/SKILL.md", ".claude/agents/*.md",
    "docs/**/*.md", "docs/**/*.csv", "common/**/*.txt", "events/**/*.txt",
    "history/**/*.txt", "localisation/**/*.yml", "interface/**/*.gui",
    "interface/**/*.gfx", "map/*.txt",
]
DEFAULT_EXCLUDE = [
    "**/.git/**", "**/.env*", "**/*credential*", "**/*secret*", "**/*token*",
    "**/*.pem", "**/*.key", "**/node_modules/**", "**/__pycache__/**",
    "**/.venv/**", "**/.tmp/**", "**/logs/**", "**/backups/**",
    "chatgpt_project_sources/**", ".chatgpt_project_sources/**",
]


def matches(path: str, patterns: list[str]) -> bool:
    # **/ also matches zero directories; * never crosses a directory boundary.
    parts = path.casefold().split("/")
    def match(items: list[str], glob: list[str]) -> bool:
        if not glob:
            return not items
        if glob[0] == "**":
            return match(items, glob[1:]) or bool(items and match(items[1:], glob))
        return bool(items and fnmatch.fnmatchcase(items[0], glob[0]) and match(items[1:], glob[1:]))
    return any(match(parts, pattern.casefold().split("/")) for pattern in patterns)


def linked(path: Path) -> bool:
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def collect(root: Path, include: list[str], exclude: list[str]) -> dict[str, bytes]:
    files = {}
    destinations = set()
    total = 0
    for directory, folders, names in os.walk(root, followlinks=False):
        parent = Path(directory)
        folders[:] = sorted(name for name in folders
                            if not linked(parent / name)
                            and not matches((parent / name).relative_to(root).as_posix() + "/_", exclude))
        for name in sorted(names):
            source = parent / name
            relative = source.relative_to(root).as_posix()
            if not matches(relative, include) or matches(relative, exclude):
                continue
            if linked(source) or not source.resolve().is_relative_to(root):
                raise ValueError(f"Linked source is not allowed: {relative}")
            if source.stat().st_size > 8 * 1024 * 1024:
                raise ValueError(f"Source exceeds 8 MiB: {relative}")
            raw = source.read_bytes()
            total += len(raw)
            if total > 128 * 1024 * 1024 or len(files) >= 10000:
                raise ValueError("Bundle exceeds 128 MiB or 10,000 files; narrow the include list")
            if "\0" in raw.decode("utf-8-sig"):
                raise ValueError(f"Binary source is not allowed: {relative}")
            # Encode nested paths injectively; preserve familiar root filenames.
            destination = relative.replace("%", "%25").replace("/", "%2F")
            key = destination.casefold()
            if key in destinations or key in {"all-project-sources.zip", "subagents.zip"}:
                raise ValueError(f"Bundle filename collision: {relative}")
            destinations.add(key)
            files[destination] = raw
    if not files:
        raise ValueError("No sources matched; review the include list")
    return dict(sorted(files.items()))


def archive(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, raw in sorted(files.items()):
            bundle.writestr(name, raw)
    with zipfile.ZipFile(path) as bundle:
        if bundle.namelist() != sorted(files) or any(bundle.read(name) != raw for name, raw in files.items()):
            raise OSError("Archive verification failed")


def build(root: Path, output: Path, include: list[str], exclude: list[str], dry_run: bool = False) -> None:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    output = output.expanduser().absolute()
    resolved = output.resolve()
    if resolved.is_relative_to(root) or root.is_relative_to(resolved):
        raise ValueError("Output must be outside the project and cannot contain the project")
    if output.exists() or linked(output):
        raise ValueError("Output already exists; choose a new folder")
    files = collect(root, include, exclude)
    if dry_run:
        print("\n".join(files))
        print(f"Would package {len(files)} sources into {output}")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".chatgpt-sources-", dir=output.parent))
    try:
        for name, raw in files.items():
            (staging / name).write_bytes(raw)
        agents = {name: raw for name, raw in files.items() if name.startswith(".claude%2Fagents%2F")}
        if agents:
            archive(staging / "subagents.zip", agents)
            files["subagents.zip"] = (staging / "subagents.zip").read_bytes()
        archive(staging / "all-project-sources.zip", files)
        # Never replace an existing destination, including one created during staging.
        if output.exists() or linked(output):
            raise ValueError("Output was created during packaging; choose a new folder")
        staging.rename(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(f"Packaged {len(files)} bundle files into {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--config", type=Path, help="JSON object with include and exclude glob lists")
    parser.add_argument("--include", action="append", help="Replace default includes; repeat for each glob")
    parser.add_argument("--exclude", action="append", default=[], help="Add an exclusion glob")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--open", action="store_true", help="Open output on Windows; print its path elsewhere")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8")) if args.config else {}
        if not isinstance(config, dict) or set(config) - {"include", "exclude"}:
            raise ValueError("Config accepts only include and exclude lists")
        for patterns in config.values():
            if not isinstance(patterns, list) or not all(isinstance(item, str) and item for item in patterns):
                raise ValueError("Config patterns must be nonempty strings in a list")
        output = args.output or Path.home() / "Downloads" / (args.root.resolve().name + "-chatgpt-project-sources")
        build(args.root, output, args.include or config.get("include", DEFAULT_INCLUDE),
              DEFAULT_EXCLUDE + config.get("exclude", []) + args.exclude, args.dry_run)
        if args.open and not args.dry_run and sys.platform == "win32":
            os.startfile(output)
        return 0
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Packaging failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
