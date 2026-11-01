#!/usr/bin/env python3
"""Run the project's generators from one registry, `generators.json`.

Every generated file in this project (AGENTS.md, the agent projections for other runtimes, the
skill copies) has its generator listed in `generators.json` with the files it reads and writes.
This runner reads that list, so `check.py`, HOI4 Mod Setup's finishing step, the Claude Code
hook, the optional Git hook, CI and the release checks agree on what runs and when.

    python .tools/sync/generators.py                     # run every generator, then the checks
    python .tools/sync/generators.py --check             # report stale outputs, write nothing
    python .tools/sync/generators.py --paths CLAUDE.md   # run only what these paths affect
    python .tools/sync/generators.py --check --staged    # check what the staged changes affect
    python .tools/sync/generators.py --hook              # Claude Code PostToolUse hook (JSON on stdin)

A path that is a generator input reruns that generator; one skill folder reruns only that skill's
copies. A path that is a generated output reruns its generator, which discards a hand edit; in
`--hook` mode a hand edit is reported instead, so the agent edits the canonical file.

Exit codes: 0 in sync, 1 an output is out of date or was edited by hand, 2 a generator could not
run or the registry is invalid.

Standard library only; runs on Python 3.9 or newer.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Pattern, Sequence, Set, Tuple

REGISTRY = Path(".tools") / "sync" / "generators.json"
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 300
LOCK_WAIT_SECONDS = 60
STALE_LOCK_SECONDS = 120
KINDS = ("generate", "check")
# Exit status 1 means "out of date" only when the tool also printed one of these findings; Python itself exits
# 1 on a crash or syntax error, which must count as "could not run".
STALE_PREFIXES = ("DRIFT", "STALE", "OVER", "UNUSED")
PROBLEM_PREFIXES = STALE_PREFIXES + ("ERROR", "MISSING", "NOTE", "Traceback")


class RegistryError(RuntimeError):
    pass


@dataclass(frozen=True)
class Entry:
    id: str
    label: str
    script: str
    kind: str
    sources: Tuple[str, ...]
    inputs: Tuple[str, ...]
    outputs: Tuple[str, ...]
    needs: Tuple[str, ...]
    item_args: Tuple[str, ...]
    # Optional, for generators that predate this runner: the interpreter (default this Python), the check-mode
    # arguments, how the project root is passed, and the output prefixes that mean "out of date".
    interpreter: Tuple[str, ...] = ()
    check_args: Tuple[str, ...] = ("--check",)
    root_args: Tuple[str, ...] = ("--root", "{root}")
    stale_markers: Tuple[str, ...] = STALE_PREFIXES


@dataclass
class Selection:
    whole: bool = False
    items: Set[str] = field(default_factory=set)

    def add(self, item: Optional[str]) -> None:
        if item is None:
            self.whole = True
        else:
            self.items.add(item)


@dataclass
class Outcome:
    entry: Entry
    code: int
    lines: List[str]

    @property
    def status(self) -> int:
        """0 in sync, 1 out of date, 2 could not run."""
        if self.code == 0:
            return 0
        if self.code == 1 and any(line.startswith(self.entry.stale_markers) for line in self.lines):
            return 1
        return 2

    @property
    def state(self) -> str:
        return ("ok", "stale", "failed")[self.status]

    @property
    def problems(self) -> List[str]:
        """The finding lines with their indented details, else the last lines of output."""
        found: List[str] = []
        for line in self.lines:
            if line.startswith(PROBLEM_PREFIXES + self.entry.stale_markers) or (found and line[:1].isspace()):
                found.append(line)
        return found or self.lines[-3:] or ["no output"]


def compile_pattern(pattern: str) -> Pattern[str]:
    """Translate a registry pattern: `*` stays inside one folder, `**` crosses folders, `{item}` is one folder name."""
    parts: List[str] = []
    index = 0
    while index < len(pattern):
        if pattern.startswith("{item}", index):
            parts.append("(?P<item>[^/]+)")
            index += len("{item}")
        elif pattern.startswith("**", index):
            parts.append(".*")
            index += 2
        elif pattern[index] == "*":
            parts.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(pattern[index]))
            index += 1
    return re.compile("".join(parts) + r"\Z", re.IGNORECASE if os.name == "nt" else 0)


def load_registry(root: Path) -> List[Entry]:
    path = root / REGISTRY
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RegistryError(f"{REGISTRY.as_posix()} is missing") from None
    except json.JSONDecodeError as error:
        raise RegistryError(f"{REGISTRY.as_posix()} is not valid JSON: {error}") from error
    rows = data.get("generators") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows or data.get("version") != 1:
        raise RegistryError(f"{REGISTRY.as_posix()} needs \"version\": 1 and a non-empty \"generators\" list")
    entries: List[Entry] = []
    for row in rows:
        try:
            entry = Entry(
                id=row["id"], label=row.get("label", row["id"]), script=row["script"], kind=row.get("kind", "generate"),
                sources=tuple(row.get("sources", ())), inputs=tuple(row["inputs"]), outputs=tuple(row.get("outputs", ())),
                needs=tuple(row.get("needs", ())), item_args=tuple(row.get("item_args", ())),
                interpreter=tuple(row.get("interpreter", ())), check_args=tuple(row.get("check_args", ("--check",))),
                root_args=tuple(row.get("root_args", ("--root", "{root}"))),
                stale_markers=tuple(row.get("stale_markers", STALE_PREFIXES)))
        except (KeyError, TypeError) as error:
            raise RegistryError(f"{REGISTRY.as_posix()}: an entry lacks {error}") from error
        if entry.kind not in KINDS:
            raise RegistryError(f"{entry.id}: kind must be one of {', '.join(KINDS)}")
        if entry.kind == "check" and entry.outputs:
            raise RegistryError(f"{entry.id}: a check writes nothing, so it has no outputs")
        entries.append(entry)
    ids = [entry.id for entry in entries]
    if len(ids) != len(set(ids)):
        raise RegistryError("generator ids must be unique")
    for entry in entries:
        unknown = set(entry.needs) - set(ids)
        if unknown:
            raise RegistryError(f"{entry.id} needs unknown generator {', '.join(sorted(unknown))}")
    return ordered(entries)


def ordered(entries: List[Entry]) -> List[Entry]:
    """Return the entries so that each comes after every entry it needs (registry order otherwise)."""
    done: List[Entry] = []
    pending = list(entries)
    while pending:
        ready = [entry for entry in pending if set(entry.needs) <= {item.id for item in done}]
        if not ready:
            raise RegistryError("the needs of " + ", ".join(entry.id for entry in pending) + " form a cycle")
        done.append(ready[0])
        pending.remove(ready[0])
    return done


def match(patterns: Sequence[str], path: str) -> Tuple[bool, Optional[str]]:
    """Return whether `path` matches, and the `{item}` it names (None when the whole entry is affected)."""
    captured: Optional[str] = None
    found = False
    for pattern in patterns:
        hit = compile_pattern(pattern).match(path)
        if hit:
            item = hit.groupdict().get("item")
            if item is None:
                return True, None
            found, captured = True, item
    return found, captured


def select(entries: Sequence[Entry], paths: Optional[Sequence[str]], include_outputs: bool = True) -> Dict[str, Selection]:
    """Map changed paths to the entries they affect; no paths, or a change to this runner, means every entry."""
    chosen: Dict[str, Selection] = {}
    runner = {REGISTRY.as_posix(), (REGISTRY.parent / "generators.py").as_posix()}
    if paths is None or runner & set(paths):
        return {entry.id: Selection(whole=True) for entry in entries}
    for path in paths:
        for entry in entries:
            for patterns in (entry.inputs, entry.outputs if include_outputs else ()):
                hit, item = match(patterns, path)
                if hit:
                    chosen.setdefault(entry.id, Selection()).add(item if entry.item_args else None)
    for entry in entries:  # entries are in dependency order, so one pass reaches every dependant
        needed = [chosen[name] for name in entry.needs if name in chosen]
        for selection in needed:
            target = chosen.setdefault(entry.id, Selection())
            if selection.whole or not entry.item_args:
                target.whole = True
            else:
                target.items |= selection.items
    return chosen


def has_sources(root: Path, entry: Entry) -> bool:
    return not entry.sources or any((root / source).exists() for source in entry.sources)


def command(root: Path, entry: Entry, selection: Selection, check: bool) -> List[str]:
    line = [*(entry.interpreter or (sys.executable, "-B")), str(root / entry.script)]
    line += [argument.replace("{root}", str(root)) for argument in entry.root_args]
    if check:
        line += list(entry.check_args)
    if not selection.whole and entry.item_args:
        for item in sorted(selection.items):
            line += [argument.replace("{item}", item) for argument in entry.item_args]
    return line


def run_entry(root: Path, entry: Entry, selection: Selection, check: bool) -> Outcome:
    script = root / entry.script
    if not script.is_file():
        return Outcome(entry, 2, [f"MISSING: {entry.script} is listed in {REGISTRY.as_posix()} but does not exist"])
    try:
        completed = subprocess.run(command(root, entry, selection, check), cwd=root, capture_output=True, text=True,
            encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return Outcome(entry, 2, [f"{entry.script} did not finish within {TIMEOUT_SECONDS} s"])
    lines = [line.rstrip() for line in (completed.stdout + completed.stderr).splitlines() if line.strip()]
    return Outcome(entry, completed.returncode, lines)


def run(root: Path, paths: Optional[Sequence[str]], check: bool, entries: Optional[List[Entry]] = None) -> List[Outcome]:
    """Run the affected generators (write or check mode), then the affected checks, in dependency order."""
    entries = entries if entries is not None else load_registry(root)
    chosen = select(entries, paths)
    planned = [(entry, chosen[entry.id]) for entry in entries if entry.id in chosen and has_sources(root, entry)]
    if check:
        with ThreadPoolExecutor(max_workers=max(1, len(planned))) as pool:
            return list(pool.map(lambda pair: run_entry(root, pair[0], pair[1], True), planned))
    outcomes = [run_entry(root, entry, selection, False) for entry, selection in planned if entry.kind == "generate"]
    outcomes += [run_entry(root, entry, selection, True) for entry, selection in planned if entry.kind == "check"]
    return outcomes


def find_root(path: Path) -> Optional[Path]:
    for folder in (path, *path.parents):
        if (folder / REGISTRY).is_file():
            return folder
    return None


def relative_path(root: Path, path: str) -> Optional[str]:
    candidate = Path(path.replace("\\", "/"))
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return Path(os.path.abspath(candidate)).relative_to(Path(os.path.abspath(root))).as_posix()
    except ValueError:
        return None


def expanded_outputs(root: Path, entries: Sequence[Entry], chosen: Dict[str, Selection]) -> Dict[str, Tuple[int, int]]:
    """Size and modification time of every existing output, to report what a run changed."""
    found: Dict[str, Tuple[int, int]] = {}
    for entry in entries:
        selection = chosen.get(entry.id)
        if selection is None:
            continue
        items = [None] if selection.whole or not entry.item_args else sorted(selection.items)
        for pattern in entry.outputs:
            for item in items:
                text = (pattern if item is None else pattern.replace("{item}", item)).replace("{item}", "*")
                # A trailing `**` matches only folders before Python 3.13, so walk those folders instead.
                matches = ([path for base in root.glob(text[:-3]) for path in base.rglob("*")] if text.endswith("/**")
                    else list(root.glob(text)))
                for path in matches:
                    if path.is_file():
                        stat = path.stat()
                        found[path.relative_to(root).as_posix()] = (stat.st_size, stat.st_mtime_ns)
    return found


@contextmanager
def run_lock(root: Path) -> Iterator[None]:
    """Serialise write runs; parallel edits can start two hooks at once."""
    path = root / ".tmp" / "generators.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + LOCK_WAIT_SECONDS
    while True:
        try:
            handle = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - path.stat().st_mtime > STALE_LOCK_SECONDS:
                    path.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() > deadline:
                raise RegistryError(f"another generator run holds {path.relative_to(root).as_posix()}") from None
            time.sleep(0.1)
    try:
        os.write(handle, str(os.getpid()).encode("ascii"))
        os.close(handle)
        yield
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def describe_sources(entry: Entry, item: Optional[str]) -> str:
    canonical = [pattern for pattern in entry.inputs if not pattern.startswith(".tools/")]
    if item is not None:
        canonical = [pattern.replace("{item}", item).replace("/**", "/") for pattern in canonical]
    # An output listed by name captures no item, so name the placeholder instead of printing `{item}`.
    return " or ".join(f"`{pattern.replace('{item}', '<name>')}`" for pattern in canonical)


def edited_file(payload: Dict[str, Any]) -> Optional[Tuple[Path, str]]:
    """The project root and root-relative path of the file a tool call wrote, or None outside every project."""
    tool_input = payload.get("tool_input") or {}
    edited = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not edited:
        return None
    edited_path = Path(edited)
    if not edited_path.is_absolute():
        edited_path = Path(payload.get("cwd") or os.getcwd()) / edited_path
    # The project is found from the edited path, not from the session folder, so worktrees work.
    root = find_root(edited_path.parent)
    rel = relative_path(root, str(edited_path)) if root is not None else None
    return (root, rel) if root is not None and rel is not None else None


def refuse_hand_edit(root: Path, owners: Sequence[Entry], rel: str) -> int:
    """An output was edited: report it unless it still equals what its generator writes."""
    stale = []
    for entry in owners:
        item = match(entry.outputs, rel)[1]
        outcome = run_entry(root, entry, Selection(whole=item is None, items={item} if item else set()), True)
        if outcome.status != 0:
            stale.append((entry, item, outcome))
    for entry, item, outcome in stale:
        print(f"`{rel}` is generated by `{entry.script}` from {describe_sources(entry, item)}. Make the change in the "
            f"canonical file instead; this hook then regenerates `{rel}`. A hand edit here is overwritten by the next "
            f"sync. To discard it now, run `python .tools/sync/generators.py --paths {rel}`.", file=sys.stderr)
        if outcome.status == 2:
            print("\n".join(outcome.problems), file=sys.stderr)
    return 2 if stale else 0


def hook(payload_text: str) -> int:
    """Claude Code PostToolUse hook: regenerate after a canonical edit, report a hand edit of an output."""
    try:
        target = edited_file(json.loads(payload_text or "{}"))
    except json.JSONDecodeError as error:
        print(f"generators hook: the hook input is not JSON ({error}); generated files were not refreshed", file=sys.stderr)
        return 1
    if target is None:
        return 0
    root, rel = target
    try:
        entries = load_registry(root)
    except RegistryError as error:
        print(f"generators hook: {error}; generated files were not refreshed", file=sys.stderr)
        return 2
    owners = [entry for entry in entries if entry.kind == "generate" and match(entry.outputs, rel)[0]]
    if owners:
        return refuse_hand_edit(root, owners, rel)
    return regenerate(root, entries, rel)


def regenerate(root: Path, entries: List[Entry], rel: str) -> int:
    """A canonical file was edited: run what it affects and tell the agent which outputs to commit with it."""
    chosen = select(entries, [rel], include_outputs=False)
    if not chosen:
        return 0
    try:
        with run_lock(root):
            before = expanded_outputs(root, entries, chosen)
            outcomes = run(root, [rel], check=False, entries=entries)
            after = expanded_outputs(root, entries, chosen)
    except RegistryError as error:
        print(f"generators hook: {error}; rerun `python .tools/sync/generators.py --paths {rel}`", file=sys.stderr)
        return 2
    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
    failed = [outcome for outcome in outcomes if outcome.status != 0]
    for outcome in failed:
        print(f"{outcome.entry.label} ({outcome.entry.script}) {outcome.state} after the edit of `{rel}`:", file=sys.stderr)
        print("\n".join(f"  {line}" for line in outcome.problems), file=sys.stderr)
    if failed:
        return 2
    if changed:
        shown = ", ".join(f"`{name}`" for name in changed[:12]) + (f" and {len(changed) - 12} more" if len(changed) > 12 else "")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
            f"`{rel}` is a canonical file, so the sync hook regenerated {shown}. Commit them together with `{rel}`."}}))
    return 0


def staged_paths(root: Path) -> List[str]:
    completed = subprocess.run(["git", "-c", "core.quotePath=false", "diff", "--cached", "--name-only", "--relative", "-z"],
        cwd=root, capture_output=True, check=True)
    return sorted({name for name in completed.stdout.decode("utf-8", errors="replace").split("\0") if name})


def report(outcomes: Sequence[Outcome], check: bool) -> int:
    for outcome in outcomes:
        shown = outcome.problems if outcome.status != 0 else outcome.lines[-1:]
        for line in shown:
            print(f"{outcome.entry.id}: {line}")
    counts = {state: sum(1 for outcome in outcomes if outcome.state == state) for state in ("ok", "stale", "failed")}
    print(f"generators ({'check' if check else 'write'}): {counts['ok']} ok, {counts['stale']} stale, {counts['failed']} could not run")
    if counts["failed"]:
        return 2
    return 1 if counts["stale"] else 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="project root (default: the project holding this tool)")
    parser.add_argument("--check", action="store_true", help="report stale or hand-edited outputs without writing")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--paths", nargs="+", metavar="PATH", help="run only the entries these paths affect")
    scope.add_argument("--staged", action="store_true", help="run only the entries the staged Git changes affect")
    scope.add_argument("--hook", action="store_true", help="Claude Code PostToolUse hook: read the tool call from stdin")
    args = parser.parse_args(argv)
    if args.hook:
        return hook(sys.stdin.read())
    root = args.root.resolve()
    try:
        entries = load_registry(root)
        paths: Optional[List[str]] = None
        if args.staged:
            paths = staged_paths(root)
        elif args.paths:
            paths = [name for name in (relative_path(root, path) for path in args.paths) if name is not None]
        if paths is not None and not paths:
            print("generators: no paths to check")
            return 0
        if args.check:
            outcomes = run(root, paths, check=True, entries=entries)
        else:
            with run_lock(root):
                outcomes = run(root, paths, check=False, entries=entries)
    except (RegistryError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if not outcomes:
        if paths is None:
            print(f"ERROR: no entry in {REGISTRY.as_posix()} has its canonical sources in {root}; nothing was checked", file=sys.stderr)
            return 2
        print("generators: the paths affect no generator")
        return 0
    return report(outcomes, args.check)


if __name__ == "__main__":
    sys.exit(main())
