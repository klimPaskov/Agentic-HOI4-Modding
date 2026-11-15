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
from typing import Any, Dict, List, Optional, Sequence

PIPELINE = Path(__file__).resolve().parent
KIT_ROOT = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))

from lib.paths import load_unit_types, read_job_document, resolve_job_root  # noqa: E402
from lib import unit_wiring as wiring  # noqa: E402

JOB_ID_PREFIX = "hoi4_3d_model_jobs_"
CHECK_TIMEOUT_SECONDS = 900


def resolve_job(value: str) -> Path:
    path = Path(value)
    if path.is_dir():
        return path.resolve()
    slug = value[len(JOB_ID_PREFIX) :] if value.startswith(JOB_ID_PREFIX) else value
    try:
        root = resolve_job_root(slug)
    except Exception as error:  # noqa: BLE001 - any refusal means this is not a job
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
    import check_unit_files

    audit, _reason = check_unit_files._registration_audit()
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


def collect(args: argparse.Namespace) -> Dict[str, Any]:
    job = resolve_job(args.job)
    mod_root = args.mod_root.resolve()
    if not mod_root.is_dir():
        raise wiring.WiringError(f"--mod-root {mod_root} is not a folder")
    registration_path = job / "runtime" / "registration.md"
    if not registration_path.is_file():
        raise wiring.WiringError(f"{registration_path} does not exist; the job has not finished its runtime stage")
    registration = wiring.parse_registration(registration_path.read_text(encoding="utf-8"))
    stem = registration.stem
    spec: Dict[str, Any] = read_job_document(job / "job.yaml") if (job / "job.yaml").is_file() else {}
    spec_stem = ((spec.get("blender_plan") or {}).get("runtime_stem")) or spec.get("runtime_stem")
    errors: List[str] = []
    warnings: List[str] = []
    if spec_stem and spec_stem != stem:
        errors.append(f"job.yaml's runtime stem {spec_stem} differs from the registration's {stem}")

    clip_samples: Dict[str, int] = {}
    files_json = job / "runtime" / "files.json"
    if files_json.is_file():
        for name, facts in ((json.loads(files_json.read_text(encoding="utf-8")).get("facts") or {}).get("animations") or {}).items():
            if isinstance(facts, dict) and isinstance(facts.get("samples"), int):
                clip_samples[name] = facts["samples"]

    entity_block = registration.entity_block
    sound: Dict[str, Any] = {"plan": False, "events": [], "problems": []}
    try:
        events = wiring.parse_sound_plan(spec.get("sound_plan") or (spec.get("blender_plan") or {}).get("sound_plan"))
        if events:
            sound["plan"] = True
            entity_block = wiring.apply_sound_events(registration.entity_block, events, clip_samples, stem)
            sound["events"] = [{"role": e.role, "soundeffect": e.soundeffect, "frame": e.frame} for e in events]
        else:
            warnings.append("no sound plan: the unit's entity has no sound events (sounds are never generated; add a sound_plan to job.yaml or write them by hand)")
    except wiring.WiringError as error:
        errors.append(f"sound plan: {error}")
        sound["problems"].append(str(error))

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
    blocking = list(errors)  # errors found before any write: the job, the sound plan and the plan itself
    result: Dict[str, Any] = {
        "job": str(job),
        "stem": stem,
        "mod_root": str(mod_root),
        "dry_run": bool(args.dry_run),
        "plan": [item.as_dict() for item in plan.items],
        "sound": sound,
    }
    folder_rel = wiring.mesh_file(registration).rsplit("/", 1)[0]

    audit = load_audit_module()
    sprite = wiring.sprite_token(registration)
    subunits: List[Any] = []
    if audit is None:
        warnings.append("the kit's registration audit could not be imported, so the sub-unit sprite was not checked")
    else:
        subunits = wiring.find_subunits(mod_root, sprite, audit)
    sub_info: Dict[str, Any] = {"sprite": sprite, "subunits": [{"id": unit, "file": file} for unit, file in subunits], "missing_localisation": []}
    if audit is not None and not subunits:
        errors.append(f"no sub-unit in common/units has sprite = {sprite}, so the entity is never used (write the sub-unit in the mod)")
    missing_loc = wiring.missing_localisation(mod_root, [unit for unit, _file in subunits])
    sub_info["missing_localisation"] = missing_loc
    errors += [f"localisation key {key} is not defined (write it in the mod's localisation)" for key in missing_loc]
    result["subunit"] = sub_info

    game = game_dir()
    counters = wiring.counter_tokens(mod_root, game, sprite)
    result["counters"] = [{"token": c.token, "role": c.role, "status": c.status, "detail": c.detail} for c in counters]
    for counter in counters:
        if counter.status != "mod":
            warnings.append(f"counter {counter.token} ({counter.role}): {counter.status}. {counter.detail}".rstrip(". ") + ".")
    for event in sound["events"]:
        if not wiring.soundeffect_defined(mod_root, game, event["soundeffect"]):
            warnings.append(f"soundeffect {event['soundeffect']} is defined in no sound .asset file of the mod or the game")

    result["checks"] = {}
    if blocking:
        warnings.append("checks not run: the job or plan has errors, so nothing was written")
    elif args.dry_run:
        warnings.append("dry run: nothing was written and check_unit_files and the audit were not run")
    else:
        wiring.apply_plan(mod_root, plan)
        written = [item.path for item in plan.items if item.status != "unchanged"]
        unit_type = spec.get("unit_type") if spec.get("unit_type") in load_unit_types() else None
        files_check = run_check_unit_files(mod_root, mod_root / folder_rel, unit_type)
        result["checks"]["check_unit_files"] = {"exit": files_check["exit"], "errors": files_check["errors"], "warnings": files_check["warnings"]}
        errors += [f"check_unit_files: {line}" for line in files_check["errors"]]
        warnings += [f"check_unit_files: {line}" for line in files_check["warnings"]]
        audited = run_audit(mod_root)
        if audited.get("unavailable"):
            errors.append(f"audit: {audited['unavailable']}")
            result["checks"]["audit"] = {"exit": audited["exit"], "unavailable": audited["unavailable"]}
        else:
            all_errors = [f for f in audited["findings"] if f.get("level") == "error"]
            counted = all_errors if args.strict_audit else [f for f in all_errors if relevant(f, stem, written)]
            other = len(all_errors) - len(counted)
            result["checks"]["audit"] = {"exit": audited["exit"], "errors": len(counted), "other_errors_in_mod": other}
            errors += [f"audit {f['rule']} {f['path']}: {f['message']}" for f in counted]
            if other:
                warnings.append(f"audit: {other} error(s) in the mod are not about this unit (rerun with --strict-audit to count them)")
    result["errors"] = errors
    result["warnings"] = warnings
    if args.dry_run:
        result["verdict"] = "DRY-RUN-FAIL" if blocking else "DRY-RUN"
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
