"""Wire a finished 3D unit into a mod, and say what the mod still lacks.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/wire_unit.py <job_root_or_job_id> --mod-root <mod> [--dry-run] [--json]

Reads the job's `runtime/registration.md`, `runtime/files/` and `job.yaml`, then (a static model's `static_model.py --out` folder
holds the same `runtime/` layout, so it is wired the same way):

1. writes the `pdxmesh`, animation and entity blocks into the mod between marker comments
   (`# wire_unit begin <stem> <kind>` and `# wire_unit end ...`), replacing only its own block on a
   rerun, and copies the mesh, animation and DDS files into the model folder the registration names
   (a file whose SHA-256 already matches is skipped). Default targets are `gfx/entities/<prefix>_units.gfx`
   and `.asset` (the mod's one `*_units.gfx`, else the stem's first word), the model folder's `<stem>.asset`,
   or the file that already holds the job's marked block. `--gfx-file` and `--entity-file` override them.
2. checks that a sub-unit in `common/units` has `sprite = <stem>` and that its localisation keys
   (`<id>`, `<id>_desc`) exist. It lists what is missing and never writes either.
3. lists the counter sprites the unit needs (`GFX_unit_<sprite>_icon_medium` and `_medium_white`) and whether
   the mod or only the game defines each. Report only. It writes each sub-unit's text icon `GFX_unit_<id>_icon_small` (the game
   looks it up on every counter refresh and logs "Couldnt find texticon" without it) into `interface/<prefix>_texticons.gfx`,
   borrowing the game's art for the sub-unit's `group`, unless the mod defines it already. It warns when `descriptor.mod` sets no
   `supported_version`.
4. writes `event = { time = <seconds> sound = { soundeffect = "..." } }` lines (seconds = frame / 30) for the job's `sound_plan`
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
import re
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
SUPPORTED_VERSION = "1.19.*"
CHECK_TIMEOUT_SECONDS = 900
SOUND_TIME_WARNING = (
    "sound events: each plan frame is written as time = frame / 30, the clip's seconds (vanilla's destroyed landmarks fire their first "
    "explosion within 0.2 s of the frame their clip hides the part, calibrate_effects.py); hear in the game that the sound lands on its frame"
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


def static_checks(job: Path) -> List[str]:
    """The static checks' arguments a static model's registration.md records (`Static checks: `--model-kind vehicle ...``, written by
    tripo/static_model.py), so a building is checked by the building rules and not the unit rules (UNIT-LOOSE-PART). Empty for a unit."""

    path = job / "runtime" / "registration.md"
    found = re.search(r"(?m)^Static checks: `([^`]*)`", read_input_text(path)) if path.is_file() else None
    return found.group(1).split() if found else []


def run_check_unit_files(mod_root: Path, folder: Path, unit_type: Optional[str], checks: Sequence[str] = ()) -> Dict[str, Any]:
    command = [sys.executable, "-B", str(PIPELINE / "check_unit_files.py"), str(folder), "--mod-root", str(mod_root), "--json", *checks]
    if unit_type and not checks:
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


def plan_sound(spec: Dict[str, Any], registration: wiring.Registration, clip_samples: Dict[str, int], errors: List[str], warnings: List[str],
               job: Optional[Path] = None) -> Tuple[str, Dict[str, Any]]:
    """The entity block with the job's sound events written in, and what the sound plan said."""

    sound: Dict[str, Any] = {"plan": False, "events": [], "problems": []}
    entity_block = registration.entity_block
    try:
        events = wiring.parse_sound_plan(spec.get("sound_plan") or plan_section(spec).get("sound_plan"))
        events += effect_sounds((job / "runtime" / "files") if job else None, registration.stem, events)
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


PARTICLE_TIME_WARNING = (
    "particle events: the burn's fire and smoke start at time 0 of the death state (vanilla's GER rifle infantry fires blood_particle at "
    "time = 0 the same way); check in the game how large they are at map zoom and how long the death's last frame holds"
)


def plan_particles(job: Path, registration: wiring.Registration, entity_block: str, errors: List[str], warnings: List[str]) -> Tuple[str, Dict[str, Any]]:
    """The entity block with a burn death's particle events (lib/tripo_burn.py's plan beside the runtime files), and the mod files that define
    the particles: finite copies of the vanilla fire and smoke the plan names."""

    from lib import tripo_burn

    stem = registration.stem
    plan = tripo_burn.read_plan(job / "runtime" / "files", stem)
    report: Dict[str, Any] = {"plan": bool(plan), "events": [], "files": []}
    if not plan:
        return entity_block, report
    game = game_dir()
    entries = []
    for particle in plan.get("particles", []):
        source = (game / particle["source"]) if game else None
        if source is None or not source.is_file():
            errors.append(f"burn particle {particle['name']}: the vanilla file {particle['source']} is not in the game folder")
            continue
        kind = f"{particle['name']}_file"
        text = wiring.finite_particle(source.read_text(encoding="utf-8", errors="replace"), kind, float(particle["duration_s"]))
        report["files"].append((f"gfx/particles/{stem}_{particle['standin']}.asset", text))
        entries.append({"name": particle["name"], "type": kind, "scale": particle.get("scale", 1)})
        report["events"].append({"state": "death", "time": particle["time"], "node": plan.get("locator"), "particle": particle["name"]})
    if entries:
        report["files"].append((f"gfx/entities/{stem}_burn_particles.gfx", wiring.particle_gfx(entries)))
    try:
        entity_block = wiring.apply_particle_events(entity_block, "death", report["events"])
        warnings.append(PARTICLE_TIME_WARNING)
    except wiring.WiringError as error:
        errors.append(f"burn particles: {error}")
    return entity_block, report


def effect_sounds(folder: Optional[Path], stem: str, planned: Sequence[Any]) -> List[Any]:
    """The effects plan's sounds (lib/unit_effects.py) as sound plan events, at the frames of their particles. A role the job's own
    sound_plan already gives a sound at that frame keeps the job's."""

    from lib import unit_effects

    plan = unit_effects.read_plan(folder, stem) if folder else None
    taken = {(e.role, e.frame) for e in planned}
    return [wiring.SoundEvent(s["role"], s["soundeffect"], int(s["frame"]), "") for s in (plan or {}).get("sounds", [])
            if (s["role"], int(s["frame"])) not in taken]


def plan_effects(job: Path, registration: wiring.Registration, entity_block: str, errors: List[str], warnings: List[str]) -> Tuple[str, Dict[str, Any]]:
    """The entity block with the effects layer's particle events (`<stem>_effects.json` beside the runtime files, written by
    tripo/effects_stage.py), and the adapted particle files with their `.gfx` registration."""

    from lib import unit_effects

    stem = registration.stem
    folder = job / "runtime" / "files"
    plan = unit_effects.read_plan(folder, stem)
    report: Dict[str, Any] = {"plan": bool(plan), "events": [], "files": []}
    if not plan:
        return entity_block, report
    files, problems = unit_effects.particle_files(plan, game_dir())
    errors += [f"effects: {problem}" for problem in problems]
    report["files"] = files
    report["events"] = [{"role": e["role"], "time": e["time"], "node": e["node"], "particle": e["particle"]} for e in plan["events"]]
    try:
        entity_block = wiring.apply_effect_events(entity_block, plan["events"])
    except wiring.WiringError as error:
        errors.append(f"effects: {error}")
    found = unit_effects.findings(folder, stem, plan, game=game_dir())
    errors += [f"effects {f['rule']}: {f['message']}" for f in found]
    warnings.append("effects: only the game draws the real particles; ask for the in-game checks of docs/3d-effects.md")
    return entity_block, report


def add_particle_files(mod_root: Path, particles: Dict[str, Any], plan: wiring.Plan) -> None:
    for rel, text in particles.get("files", []):
        data = text if isinstance(text, bytes) else text.encode("utf-8")
        dest = mod_root / rel
        status = "create" if not dest.is_file() else ("unchanged" if dest.read_bytes() == data else "update")
        plan.items.append(wiring.PlanItem("block", rel, status, "burn particle", payload=data))


def check_subunits(mod_root: Path, registration: wiring.Registration, errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    """The sub-unit and localisation report; adds what is missing to `errors`."""

    audit = load_audit_module()
    sprite = wiring.sprite_token(registration)
    subunits: List[Any] = []
    groups: Dict[str, str] = {}
    if audit is None:
        warnings.append("the kit's registration audit could not be imported, so the sub-unit sprite was not checked")
    else:
        subunits = wiring.find_subunits(mod_root, sprite, audit)
        groups = wiring.subunit_groups(mod_root, sprite, audit)
    missing_loc = wiring.missing_localisation(mod_root, [unit for unit, _file in subunits])
    if audit is not None and not subunits:
        errors.append(f"no sub-unit in common/units has sprite = {sprite}, so the entity is never used (write the sub-unit in the mod)")
    errors += [f"localisation key {key} is not defined (write it in the mod's localisation)" for key in missing_loc]
    return {"sprite": sprite, "subunits": [{"id": unit, "file": file} for unit, file in subunits], "missing_localisation": missing_loc, "groups": groups}


def check_descriptor(mod_root: Path, warnings: List[str]) -> None:
    """Warn when the mod's descriptor.mod sets no supported_version, which a scratch test mod needed before it ran in the game
    (2026-11-23)."""

    descriptor = mod_root / "descriptor.mod"
    if descriptor.is_file() and not re.search(r"(?m)^\s*supported_version\s*=", wiring.read_text_lenient(descriptor)):
        warnings.append(f'{descriptor.name} sets no supported_version: add supported_version="{SUPPORTED_VERSION}" (and to the launcher\'s .mod file)')


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
    files_check = run_check_unit_files(mod_root, mod_root / wiring.model_folder(registration), unit_type, static_checks(Path(result["job"])))
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
    entity_block, sound = plan_sound(spec, registration, load_clip_samples(job), errors, warnings, job)
    entity_block, particles = plan_particles(job, registration, entity_block, errors, warnings)
    entity_block, effects = plan_effects(job, registration, entity_block, errors, warnings)
    particles["files"] = particles.get("files", []) + effects.pop("files", [])
    particles["effects"] = effects
    plan = wiring.build_plan(
        mod_root=mod_root,
        registration=registration,
        entity_block=entity_block,
        runtime_files=job / "runtime" / "files",
        gfx_file=args.gfx_file,
        entity_file=args.entity_file,
        prefix=args.prefix,
    )
    add_particle_files(mod_root, particles, plan)
    subunit_errors: List[str] = []
    subunit = check_subunits(mod_root, registration, subunit_errors, warnings)
    texticons = wiring.plan_texticons(mod_root, stem, subunit.pop("groups"), args.prefix or wiring.default_prefix(mod_root, stem), plan)
    warnings += [f"text icon {row['token']} borrows the game's {row['art']} (draw the unit's own icon if it needs one)" for row in texticons if row["status"] == "written"]
    check_descriptor(mod_root, warnings)
    errors += plan.errors
    blocking = bool(errors)  # errors found before any write: the job, the sound plan and the plan itself
    errors += subunit_errors
    result: Dict[str, Any] = {
        "job": str(job),
        "stem": stem,
        "mod_root": str(mod_root),
        "dry_run": bool(args.dry_run),
        "plan": [item.as_dict() for item in plan.items],
        "sound": sound,
        "particles": {key: value for key, value in particles.items() if key != "files"},
        "checks": {},
    }
    result["subunit"] = subunit
    result["texticons"] = texticons
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
    for row in result.get("texticons", []):
        print(f"  text icon {row['token']}: {row['status']} {row['art']}".rstrip())
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
