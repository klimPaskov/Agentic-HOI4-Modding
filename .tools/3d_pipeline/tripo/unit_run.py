"""Run a Tripo unit from its export to its review sheets in steps that resume: a step killed by a pause, a crash or a restart starts again
from the last finished step, not from the intake.

    py -3.13 -B .tools/3d_pipeline/tripo/unit_run.py --jobs-config <3d_jobs.json> <unit> --rigged <export.glb> --run <run folder>
        [--weapon-bone <bone>] [--unit-type <type>] [--gate "<command prefix>"] [--only STEP ...] [--again STEP ...] [--status]

The steps are the route's steps 8 to 10 (`docs/3d-units.md`): `intake`, `pilot` (run_pilot), `files` (the runtime files copied into
`<run>/unit_files`), `tripo_checks`, `unit_checks` (check_unit_files, with `--unit-type`), `review` (review_unit), `preview` (the
designer-size sheet), `game` (the game-size sheet) and `death` (the death from the side). The heavy ones (those that start Blender) run
behind `--gate` when it is given (or `HOI4_KIT_GATE`), a machine's own gate script such as one that waits for a free slot of a heavy-job
pool. Every kit command that starts Blender waits for the machine by itself as well (`lib/heavy_job.py`).

What makes a run resumable:

- **Inputs live in the run.** On the first start the jobs file and the export are copied into `<run>/inputs/`, with their SHA-256 in
  `<run>/inputs/inputs.json`, and every step reads those copies. A cleanup that moves the files the run started from cannot break it. On
  every start the tool checks that each input is there with its recorded hash, and refuses to start, naming the file, when one is missing
  or changed. A changed export is a new run: give a new `--run` folder.
- **Each finished step is recorded.** `<run>/run_state.json` holds, per step, its command, its exit code and its key: a hash of the inputs
  and the keys of the steps before it. A start skips every step whose key still matches and runs the first that does not, then the rest. A
  step killed half way has no record, so it runs again, and the intake's own receipt makes a second intake of the same files do nothing.
  The record is written only after the step ends, so a kill never leaves a step marked finished.
- **The run says it is live.** `<run>/STATUS.md` names the unit, the inputs and the next step while the run is unfinished, and says
  `finished` at the end. A cleanup must never move or delete a run folder whose STATUS.md does not say `finished`.

A check that finds faults (tripo_checks or check_unit_files exiting 1) is a finished step: its report is the result. Any other failure stops
the run at that step, and the next start runs it again. `--again <step>` forgets that step and every step after it. The jobs file is an
input, so a changed `tripo` block is a new run in a new folder, whose intake takes `--reingest` when the job already has a receipt for
the same export.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

PIPELINE = Path(__file__).resolve().parents[1]
REPO = PIPELINE.parents[1]
PY = [sys.executable, "-B"]
GATE_ENV = "HOI4_KIT_GATE"
STATE = "run_state.json"
FINDINGS_EXIT = 1  # a check that found faults: the step finished, its report is the result
CHECK_STEPS = ("tripo_checks", "unit_checks")


class RunRefused(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class Step:
    name: str
    command: List[str]
    heavy: bool = False
    cwd: Optional[Path] = None
    action: Optional[Callable[[], None]] = None  # a step done in this process (copying files) instead of a command
    env: Dict[str, str] = field(default_factory=dict)


def job_root(jobs_config: Path, unit: str) -> Path:
    sys.path.insert(0, str(PIPELINE))
    from lib.paths import resolve_job_root

    job = json.loads(jobs_config.read_text(encoding="utf-8"))["jobs"][unit]
    return resolve_job_root(job["asset_id"].rsplit(".", 1)[-1])


def take_inputs(run: Path, sources: Dict[str, Path]) -> Dict[str, dict]:
    """Copy the inputs into `<run>/inputs/` on the first start, and check them on every start. Returns the manifest."""

    folder = run / "inputs"
    manifest_path = folder / "inputs.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name, record in manifest.items():
            copy = folder / record["file"]
            if not copy.is_file():
                raise RunRefused(f"the run's input {name} ({copy}) is missing: restore it, or start a new run in a new --run folder")
            if sha256(copy) != record["sha256"]:
                raise RunRefused(f"the run's input {name} ({copy}) changed since the run started: start a new run in a new --run folder")
        for name, source in sources.items():
            if name in manifest and Path(source).is_file() and sha256(Path(source)) != manifest[name]["sha256"]:
                raise RunRefused(f"{source} differs from the {name} this run started with: a new export or job file is a new run "
                                 "(give a new --run folder)")
        return manifest
    missing = [f"{name} ({source})" for name, source in sources.items() if not Path(source).is_file()]
    if missing:
        raise RunRefused("the run cannot start, inputs are missing: " + ", ".join(missing))
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, source in sources.items():
        target = folder / Path(source).name
        shutil.copy2(source, target)
        manifest[name] = {"file": target.name, "sha256": sha256(target), "from": str(source)}
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8", newline="\n")
    return manifest


def step_keys(steps: Sequence[Step], manifest: Dict[str, dict]) -> Dict[str, str]:
    """Each step's key: a hash of the inputs, its command and the key of the step before it."""

    keys, previous = {}, json.dumps({name: record["sha256"] for name, record in sorted(manifest.items())})
    for step in steps:
        previous = hashlib.sha256((previous + "\n" + step.name + "\n" + json.dumps(step.command)).encode("utf-8")).hexdigest()
        keys[step.name] = previous
    return keys


def load_state(run: Path) -> Dict[str, dict]:
    path = run / STATE
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_state(run: Path, state: Dict[str, dict]) -> None:
    path = run / STATE
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)  # never a half-written state


def write_status(run: Path, unit: str, manifest: Dict[str, dict], next_step: Optional[str], note: str = "") -> None:
    lines = [f"# Unit run {unit}", ""]
    lines.append("State: finished" if next_step is None else f"State: in progress, next step `{next_step}`. Do not move or delete this folder.")
    lines += ["", "Inputs (in inputs/):"] + [f"- {name}: {record['file']} sha256 {record['sha256'][:12]}" for name, record in sorted(manifest.items())]
    if note:
        lines += ["", note]
    (run / "STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def run_steps(run: Path, unit: str, steps: Sequence[Step], manifest: Dict[str, dict], gate: Sequence[str] = (),
              runner: Callable[..., int] = None, again: Sequence[str] = (), log: Callable[[str], None] = print) -> int:
    """Run the steps whose key is not recorded as finished, in order. Returns 0 when every step finished, else the failed step's code."""

    runner = runner or _subprocess_runner
    keys = step_keys(steps, manifest)
    state = load_state(run)
    names = [step.name for step in steps]
    if again:
        unknown = sorted(set(again) - set(names))
        if unknown:
            raise RunRefused(f"no such step: {', '.join(unknown)}")
        first = min(names.index(name) for name in again)
        for name in names[first:]:
            state.pop(name, None)
        save_state(run, state)
    for step in steps:
        record = state.get(step.name)
        if record and record.get("key") == keys[step.name]:
            log(f"unit run: {step.name} finished before (exit {record['exit']}), skipped")
            continue
        for later in names[names.index(step.name):]:
            state.pop(later, None)  # a step that runs again makes every later step run again
        save_state(run, state)
        write_status(run, unit, manifest, step.name)
        started = time.time()
        log(f"unit run: {step.name} starting")
        if step.action is not None:
            step.action()
            code = 0
        else:
            command = (list(gate) if step.heavy else []) + step.command
            code = runner(command, cwd=step.cwd, log_path=run / "logs" / f"{step.name}.log", env=step.env)
        finished = code == 0 or (code == FINDINGS_EXIT and step.name in CHECK_STEPS)
        if not finished:
            log(f"unit run: {step.name} failed with exit {code} (log: logs/{step.name}.log). The next start runs it again.")
            write_status(run, unit, manifest, step.name, f"Step `{step.name}` failed with exit {code}, see logs/{step.name}.log.")
            return code or 1
        state[step.name] = {"key": keys[step.name], "exit": code, "seconds": round(time.time() - started, 1), "command": step.command}
        save_state(run, state)
        log(f"unit run: {step.name} finished (exit {code}, {state[step.name]['seconds']} s)")
    write_status(run, unit, manifest, None)
    return 0


def _subprocess_runner(command: Sequence[str], cwd: Optional[Path], log_path: Path, env: Dict[str, str]) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        return subprocess.run(list(command), cwd=cwd, stdout=handle, stderr=subprocess.STDOUT, env={**os.environ, **env}).returncode


def build_steps(args: argparse.Namespace, run: Path, manifest: Dict[str, dict]) -> List[Step]:
    inputs = run / "inputs"
    jobs = inputs / manifest["jobs"]["file"]
    unit = args.unit
    inbox = run / "inbox"
    files = run / "unit_files"
    review = run / "review"
    root = job_root(jobs, unit)
    tool = lambda *parts: PY + [str(PIPELINE.joinpath(*parts))]  # noqa: E731

    def fill_inbox() -> None:
        inbox.mkdir(parents=True, exist_ok=True)
        shutil.copy2(inputs / manifest["rigged"]["file"], inbox / f"{unit}__rigged.glb")

    def copy_files() -> None:
        source = root / "runtime" / "files"
        if not source.is_dir():
            raise RunRefused(f"run_pilot left no runtime files in {source}")
        if files.exists():
            shutil.rmtree(files)
        shutil.copytree(source, files)

    intake = tool("tripo_intake.py") + ["--jobs-config", str(jobs), unit, "--inbox", str(inbox)]
    if args.blender:
        intake += ["--blender", str(args.blender)]
    if args.reingest:
        intake.append("--reingest")
    weapon = ["--weapon-bone", args.weapon_bone] if args.weapon_bone else []
    steps = [
        Step("inbox", [], action=fill_inbox),
        Step("intake", intake, heavy=True, cwd=REPO),
        Step("pilot", tool("run_pilot.py") + ["--jobs-config", str(jobs), unit], heavy=True, cwd=REPO),
        Step("files", [], action=copy_files),
        Step("tripo_checks", tool("tripo", "tripo_checks.py") + [str(files), *weapon, "--jobs-config", str(jobs), "--slug", unit,
                                                                   "--json", str(run / "tripo_checks.json")], cwd=REPO),
    ]
    if args.unit_type:
        steps.append(Step("unit_checks", tool("check_unit_files.py") + [str(files), "--unit-type", args.unit_type, *weapon,
                                                                        "--verdict", str(run / "check_unit_files.json")], cwd=REPO))
    steps += [
        Step("review", tool("review_unit.py") + [str(files), "--out", str(review)], heavy=True, cwd=REPO),
        Step("preview", tool("tripo", "weapon_sheets.py") + [str(files), "--out", str(review), "--sheet", "preview", "--jobs-config", str(jobs),
                                                            "--unit", unit], heavy=True, cwd=REPO),
        Step("game", tool("tripo", "weapon_sheets.py") + [str(files), "--out", str(review), "--sheet", "game"], heavy=True, cwd=REPO),
        Step("death", tool("tripo", "clip_sheet.py") + [str(files), "--roles", "death", "--frames", "6", "--views", "left", "--out",
                                                        str(review / "sheets" / "death_six_frames_side.png")], heavy=True, cwd=REPO),
    ]
    if args.only:
        unknown = sorted(set(args.only) - {step.name for step in steps})
        if unknown:
            raise RunRefused(f"no such step: {', '.join(unknown)}")
    return steps


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("unit")
    parser.add_argument("--jobs-config", type=Path, required=True)
    parser.add_argument("--rigged", type=Path, required=True, help="the unit's export (the armed unit's arm_unit output)")
    parser.add_argument("--run", type=Path, required=True, help="the run's own folder, where its inputs, state, logs and results live")
    parser.add_argument("--weapon-bone", default="")
    parser.add_argument("--unit-type", default="", help="check_unit_files' unit type; leave out to skip that step")
    parser.add_argument("--blender", type=Path)
    parser.add_argument("--gate", default=os.environ.get(GATE_ENV, ""), help=f"a command prefix for the heavy steps (default ${GATE_ENV})")
    parser.add_argument("--again", nargs="*", default=[], help="forget these steps and every step after them, and run them again")
    parser.add_argument("--reingest", action="store_true", help="pass --reingest to the intake (after the job's tripo block changed)")
    parser.add_argument("--only", nargs="*", default=[], help="run only up to the last of these steps")
    parser.add_argument("--status", action="store_true", help="print which steps are finished and stop")
    args = parser.parse_args(argv)
    run = args.run.resolve()
    run.mkdir(parents=True, exist_ok=True)
    try:
        manifest = take_inputs(run, {"jobs": args.jobs_config.resolve(), "rigged": args.rigged.resolve()})
        steps = build_steps(args, run, manifest)
    except (RunRefused, KeyError, FileNotFoundError) as error:
        print(f"unit run: refused: {error}")
        return 2
    if args.only:
        last = max(i for i, step in enumerate(steps) if step.name in args.only)
        steps = steps[: last + 1]
    if args.status:
        keys, state = step_keys(steps, manifest), load_state(run)
        for step in steps:
            done = state.get(step.name, {}).get("key") == keys[step.name]
            print(f"{step.name}: {'finished' if done else 'to run'}")
        return 0
    try:
        return run_steps(run, args.unit, steps, manifest, shlex.split(args.gate), again=args.again)
    except RunRefused as error:
        print(f"unit run: refused: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
