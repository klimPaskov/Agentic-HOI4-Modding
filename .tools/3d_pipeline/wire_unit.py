"""Wire a finished 3D unit into a mod, and say what the mod still lacks.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/wire_unit.py <job_root_or_job_id> --mod-root <mod> [--dry-run] [--json]

Reads the job's `runtime/registration.md`, `runtime/files/` and `job.yaml`, then:

1. writes the `pdxmesh`, animation and entity blocks into the mod between marker comments
   (`# wire_unit begin <stem> <kind>` and `# wire_unit end ...`), replacing only its own block on a
   rerun, and copies the mesh, animation and DDS files into the model folder the registration names
   (a file whose SHA-256 already matches is skipped). Default targets are `gfx/entities/<prefix>_units.gfx`
   and `.asset` (the mod's one `*_units.gfx`, else the stem's first word), the model folder's `<stem>.asset`,
   or the file that already holds the job's marked block. `--gfx-file` and `--entity-file` override them.
2. checks that a sub-unit in `common/units` has `sprite = <stem>` and that its localisation keys
   (`<id>`, `<id>_desc`) exist. It lists what is missing and never writes either.
3. lists the counter sprites the unit needs (`GFX_unit_<sprite>_icon_medium` and `_medium_white`) and whether
   the mod or only the game defines each. Report only.
4. writes `event = { time = <frame> sound = { soundeffect = "..." } }` lines for the job's `sound_plan`
   (a list in job.yaml of `{role, soundeffect, frame}`). Without a plan it warns "no sound plan". Sound is
   never generated.
5. runs `check_unit_files.py --mod-root` and `.tools/audits/audit_asset_wiring_static.py --root` on the mod
   and prints one verdict, PASS or FAIL with the list. The audit's errors count when they name this unit or
   a file this tool wrote, because a mod may carry older errors of its own (`--strict-audit` counts all).

`--dry-run` prints the plan and the mod checks (2, 3 and 4) and changes nothing; it runs no checks of step 5
because the files are not in the mod yet. Exit 0 for PASS (or a clean dry run), 1 for FAIL, 2 for bad input.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

PIPELINE = Path(__file__).resolve().parent
KIT_ROOT = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))

from lib.paths import load_unit_types, read_job_document, resolve_job_root
from lib import unit_wiring as wiring

JOB_ID_PREFIX = "hoi4_3d_model_jobs_"
CHECK_TIMEOUT_SECONDS = 900
SOUND_TIME_WARNING = (
    "sound events: the unit of `time` in an entity event is unverified (vanilla uses values like 0.1 and 14, see .tools/wiki/kit/entity_modding.md); "
    "the tool writes the plan's frame number as it is, so check the timing in the game"
)


def resolve_job(value: str) -> Path:
    path = Path(value)
    if path.is_dir():
        return path.resolve()
    slug = value[len(JOB_ID_PREFIX) :] if value.startswith(JOB_ID_PREFIX) else value
    try:
        root = resolve_job_root(slug)
    except Exception as error:  # any refusal means this is not a job
        raise wiring.WiringError(f"{value} is neither a folder nor a job id ({error})") from error
    if not root.is_dir():
        raise wiring.WiringError(f"no job folder at {root}")
    return root


def game_dir() -> Optional[Path]:
    """The installed game folder, found by the kit's own `.tools/lib/game.py` (loaded by path: `lib` here is the pipeline's)."""

    try:
        spec = importlib.util.spec_from_file_location("kit_game_locator", KIT_ROOT / ".tools" / "lib" / "game.py")
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        found = module.game_dir()
        return Path(found) if found and Path(found).is_dir() else None
    except Exception:  # noqa: BLE001 - no game folder means no vanilla comparison
        return None


def load_audit_module() -> Optional[object]:
    try:
        import check_unit_files

        audit, _reason = check_unit_files._registration_audit()
    except Exception as error:  # the import runs the kit's audit module, which can fail in many ways
        raise wiring.WiringError(f"cannot load the kit's checks (check_unit_files.py): {error}") from error
    return audit


def run_check_unit_files(mod_root: Path, folder: Path, unit_type: Optional[str]) -> Dict[str, Any]:
    command = [sys.executable, "-B", str(PIPELINE / "check_unit_files.py"), str(folder), "--mod-root", str(mod_root), "--json"]
    if unit_type:
        command += ["--unit-type", unit_type]
    done = subprocess.run(command, capture_output=True, text=True, timeout=CHECK_TIMEOUT_SECONDS, cwd=str(mod_root))
    try:
        payload = json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"exit": done.returncode, "errors": [f"check_unit_files.py gave no JSON (exit {done.returncode}): {(done.stderr or done.stdout).strip()[-300:]}"], "warnings": []}
    findings = payload.get("findings", [])
    return {
        "exit": done.returncode,
        "errors": [f"{item['rule']} {item['file']}: {item['message']}" for item in findings if item["severity"] == "error"],
        "warnings": [f"{item['rule']} {item['file']}: {item['message']}" for item in findings if item["severity"] != "error"],
    }


def run_audit(mod_root: Path) -> Dict[str, Any]:
    script = KIT_ROOT / ".tools" / "audits" / "audit_asset_wiring_static.py"
    with tempfile.TemporaryDirectory(prefix="wire_unit_") as scratch:
        report = Path(scratch) / "audit.json"
        command = [sys.executable, "-B", str(script), "--root", str(mod_root), "--json", str(report), "--fail-on", "none"]
        done = subprocess.run(command, capture_output=True, text=True, timeout=CHECK_TIMEOUT_SECONDS, cwd=str(mod_root))
        if not report.is_file():
            return {"exit": done.returncode, "unavailable": f"audit_asset_wiring_static.py wrote no report (exit {done.returncode}): {(done.stderr or done.stdout).strip()[-300:]}", "findings": []}
        return {"exit": done.returncode, "findings": json.loads(report.read_text(encoding="utf-8")).get("findings", [])}


def relevant(finding: Dict[str, Any], stem: str, written: Sequence[str]) -> bool:
    path = str(finding.get("path", "")).replace("\\", "/")
    return stem in str(finding.get("message", "")) or stem in path or path in written


def read_input_text(path: Path) -> str:
    """A job file's text; a file that cannot be read as UTF-8 is a bad input (exit 2), not a crash."""

    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise wiring.WiringError(f"cannot read {path}: {error}") from error


def load_registration(job: Path) -> wiring.Registration:
    registration_path = job / "runtime" / "registration.md"
    if not registration_path.is_file():
        raise wiring.WiringError(f"{registration_path} does not exist; the job has not finished its runtime stage")
    return wiring.parse_registration(read_input_text(registration_path))


def load_spec(job: Path) -> Dict[str, Any]:
    """The job's `job.yaml` as a mapping ({} when the job has none)."""

    path = job / "job.yaml"
    if not path.is_file():
        return {}
    try:
        return read_job_document(path)
    except Exception as error:  # the reader raises JSON, YAML, decoding and missing-package errors alike
        raise wiring.WiringError(f"cannot read {path}: {error}") from error


def plan_section(spec: Dict[str, Any]) -> Dict[str, Any]:
    section = spec.get("blender_plan")
    return section if isinstance(section, dict) else {}


def load_clip_samples(job: Path) -> Dict[str, int]:
    """clip file name -> sample count, from the job's `runtime/files.json` (empty when the job has none)."""

    path = job / "runtime" / "files.json"
    if not path.is_file():
        return {}
    try:
        document = json.loads(read_input_text(path))
    except json.JSONDecodeError as error:
        raise wiring.WiringError(f"{path} is not valid JSON: {error}") from error
    facts = document.get("facts") if isinstance(document, dict) else None
    animations = facts.get("animations") if isinstance(facts, dict) else None
    if not isinstance(animations, dict):
        return {}
    return {name: item["samples"] for name, item in animations.items() if isinstance(item, dict) and isinstance(item.get("samples"), int)}


def plan_sound(spec: Dict[str, Any], registration: wiring.Registration, clip_samples: Dict[str, int], errors: List[str], warnings: List[str]) -> Tuple[str, Dict[str, Any]]:
    """The entity block with the job's sound events written in, and what the sound plan said."""

    sound: Dict[str, Any] = {"plan": False, "events": [], "problems": []}
    entity_block = registration.entity_block
    try:
        events = wiring.parse_sound_plan(spec.get("sound_plan") or plan_section(spec).get("sound_plan"))
        if not events:
            warnings.append("no sound plan: the unit's entity has no sound events (sounds are never generated; add a sound_plan to job.yaml or write them by hand)")
            return entity_block, sound
        sound["plan"] = True
        entity_block = wiring.apply_sound_events(entity_block, events, clip_samples, registration.stem)
        sound["events"] = [{"role": e.role, "soundeffect": e.soundeffect, "frame": e.frame} for e in events]
        warnings.append(SOUND_TIME_WARNING)
    except wiring.WiringError as error:
        errors.append(f"sound plan: {error}")
        sound["problems"].append(str(error))
    return entity_block, sound


def check_subunits(mod_root: Path, registration: wiring.Registration, errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    """The sub-unit and localisation report; adds what is missing to `errors`."""

    audit = load_audit_module()
    sprite = wiring.sprite_token(registration)
    subunits: List[Any] = []
    if audit is None:
        warnings.append("the kit's registration audit could not be imported, so the sub-unit sprite was not checked")
    else:
        subunits = wiring.find_subunits(mod_root, sprite, audit)
    missing_loc = wiring.missing_localisation(mod_root, [unit for unit, _file in subunits])
    if audit is not None and not subunits:
        errors.append(f"no sub-unit in common/units has sprite = {sprite}, so the entity is never used (write the sub-unit in the mod)")
    errors += [f"localisation key {key} is not defined (write it in the mod's localisation)" for key in missing_loc]
    return {"sprite": sprite, "subunits": [{"id": unit, "file": file} for unit, file in subunits], "missing_localisation": missing_loc}


def report_counters_and_sounds(mod_root: Path, sprite: str, sound: Dict[str, Any], result: Dict[str, Any], warnings: List[str]) -> None:
    game = game_dir()
    counters = wiring.counter_tokens(mod_root, game, sprite)
    result["counters"] = [{"token": c.token, "role": c.role, "status": c.status, "detail": c.detail} for c in counters]
    for counter in counters:
        if counter.status != "mod":
            warnings.append(f"counter {counter.token} ({counter.role}): {counter.status}. {counter.detail}".rstrip(". ") + ".")
    for event in sound["events"]:
        if not wiring.soundeffect_defined(mod_root, game, event["soundeffect"]):
            warnings.append(f"soundeffect {event['soundeffect']} is defined in no sound .asset file of the mod or the game")


def run_written_checks(args: argparse.Namespace, mod_root: Path, registration: wiring.Registration, spec: Dict[str, Any], plan: wiring.Plan, result: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    """Write the plan, then run check_unit_files and the static audit on the mod."""

    stem = registration.stem
    wiring.apply_plan(mod_root, plan)
    written = [item.path for item in plan.items if item.status != "unchanged"]
    unit_type = spec.get("unit_type") if spec.get("unit_type") in load_unit_types() else None
    files_check = run_check_unit_files(mod_root, mod_root / wiring.model_folder(registration), unit_type)
    result["checks"]["check_unit_files"] = {"exit": files_check["exit"], "errors": files_check["errors"], "warnings": files_check["warnings"]}
    errors += [f"check_unit_files: {line}" for line in files_check["errors"]]
    warnings += [f"check_unit_files: {line}" for line in files_check["warnings"]]
    audited = run_audit(mod_root)
    if audited.get("unavailable"):
        errors.append(f"audit: {audited['unavailable']}")
        result["checks"]["audit"] = {"exit": audited["exit"], "unavailable": audited["unavailable"]}
        return
    all_errors = [f for f in audited["findings"] if f.get("level") == "error"]
    counted = all_errors if args.strict_audit else [f for f in all_errors if relevant(f, stem, written)]
    other = len(all_errors) - len(counted)
    result["checks"]["audit"] = {"exit": audited["exit"], "errors": len(counted), "other_errors_in_mod": other}
    errors += [f"audit {f['rule']} {f['path']}: {f['message']}" for f in counted]
    if other:
        warnings.append(f"audit: {other} error(s) in the mod are not about this unit (rerun with --strict-audit to count them)")


def collect(args: argparse.Namespace) -> Dict[str, Any]:
    job = resolve_job(args.job)
    mod_root = args.mod_root.resolve()
    if not mod_root.is_dir():
        raise wiring.WiringError(f"--mod-root {mod_root} is not a folder")
    registration = load_registration(job)
    stem = registration.stem
    spec = load_spec(job)
    spec_stem = plan_section(spec).get("runtime_stem") or spec.get("runtime_stem")
    errors: List[str] = []
    warnings: List[str] = []
    if spec_stem and spec_stem != stem:
        errors.append(f"job.yaml's runtime stem {spec_stem} differs from the registration's {stem}")
    entity_block, sound = plan_sound(spec, registration, load_clip_samples(job), errors, warnings)
    plan = wiring.build_plan(
        mod_root=mod_root,
        registration=registration,
        entity_block=entity_block,
        runtime_files=job / "runtime" / "files",
        gfx_file=args.gfx_file,
        entity_file=args.entity_file,
        prefix=args.prefix,
    )
    errors += plan.errors
    blocking = bool(errors)  # errors found before any write: the job, the sound plan and the plan itself
    result: Dict[str, Any] = {
        "job": str(job),
        "stem": stem,
        "mod_root": str(mod_root),
        "dry_run": bool(args.dry_run),
        "plan": [item.as_dict() for item in plan.items],
        "sound": sound,
        "checks": {},
    }
    result["subunit"] = check_subunits(mod_root, registration, errors, warnings)
    report_counters_and_sounds(mod_root, result["subunit"]["sprite"], sound, result, warnings)
    if blocking:
        warnings.append("checks not run: the job or plan has errors, so nothing was written")
    elif args.dry_run:
        warnings.append("dry run: nothing was written and check_unit_files and the audit were not run")
    else:
        run_written_checks(args, mod_root, registration, spec, plan, result, errors, warnings)
    result["errors"] = errors
    result["warnings"] = warnings
    if args.dry_run:
        result["verdict"] = "DRY-RUN-FAIL" if errors else "DRY-RUN"
    else:
        result["verdict"] = "FAIL" if errors else "PASS"
    return result


def print_text(result: Dict[str, Any]) -> None:
    mode = "dry run" if result["dry_run"] else "run"
    print(f"wire_unit {mode}: {result['stem']} into {result['mod_root']}")
    print("plan:")
    for item in result["plan"]:
        print(f"  {item['status']:9} {item['kind']:5} {item['path']}  ({item['detail']})")
    sub = result["subunit"]
    ids = ", ".join(f"{u['id']} ({u['file']})" for u in sub["subunits"]) or "none"
    print(f"sub-unit with sprite = {sub['sprite']}: {ids}")
    for key in sub["missing_localisation"]:
        print(f"  missing localisation: {key}")
    print("counters:")
    for counter in result["counters"]:
        print(f"  {counter['status']:19} {counter['token']} ({counter['role']})")
    sound = result["sound"]
    print("sound events: " + (", ".join(f"{e['role']}@{e['frame']} {e['soundeffect']}" for e in sound["events"]) if sound["events"] else "none"))
    for line in result["warnings"]:
        print(f"WARNING: {line}")
    for line in result["errors"]:
        print(f"ERROR: {line}")
    print(f"VERDICT: {result['verdict']}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("job", help="a job root folder, or a job id (hoi4_3d_model_jobs_<slug> or <slug>)")
    parser.add_argument("--mod-root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true", help="print the plan and change nothing")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("--gfx-file", help="mod-relative .gfx file for the pdxmesh block (default gfx/entities/<prefix>_units.gfx)")
    parser.add_argument("--entity-file", help="mod-relative .asset file for the entity block (default gfx/entities/<prefix>_units.asset)")
    parser.add_argument("--prefix", help="the <prefix> of the default target names")
    parser.add_argument("--strict-audit", action="store_true", help="count every error of the mod's audit, not only those about this unit")
    args = parser.parse_args(argv)
    try:
        result = collect(args)
    except wiring.WiringError as error:
        print(f"wire_unit: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 1 if result["verdict"] in ("FAIL", "DRY-RUN-FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
