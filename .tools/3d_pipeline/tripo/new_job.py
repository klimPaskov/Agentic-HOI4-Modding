"""Start a Tripo job from a preset, so nobody sets a Tripo value by hand (D-120).

    py -3.13 -B .tools/3d_pipeline/tripo/new_job.py --list
    py -3.13 -B .tools/3d_pipeline/tripo/new_job.py --jobs-config <3d_jobs.json> --preset <preset> <asset_slug>
        --source "<the subject's own reference>" [--source "<a researched reference>" ...]
        [--brief "<one sentence: what the unit is>"] [--set <key>=<value> ...]

`--list` prints each preset: what it is for, its credits and whether the route is proven for it. The second form adds one job entry to
the registry (it creates the file when it does not exist) with the preset's defaults: the unit type and its anatomy, the size reference of
the type's profile, the credit cap as the budget, the Tripo block, and for a static model the job file `static_model.py` reads. `--set`
gives what only you know, named as the card names it: `posture=hunched`, `weapon.name="wooden mallet"`, `weapon.hand=LeftHand`,
`weapon.grip_options.length_ratio=0.62`, `weapon.grip_options.grip=0.3`, `armed=true`, `tail=true`, `size_vs_horse=1.7`. A value that
reads as JSON (a number, true, false) is stored as one. Then it prints what the entry still lacks, and the next command: `make_card.py`.
Run it again with more `--set` or `--source` to add to an existing job. `--replace` starts the job again from the preset.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import tripo_card, tripo_presets
from lib.paths import resolve_job_root

CONFIG = PIPELINE_ROOT / "config"
JOB_PREFIX = "hoi4_3d_model_jobs"


def parse_value(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return text


def answers_from(pairs: List[str]) -> Dict[str, Any]:
    found: Dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"--set {pair!r}: write it as <key>=<value>, for example posture=upright")
        key, value = pair.split("=", 1)
        found[key.strip()] = parse_value(value.strip())
    return found


def profile_reference(unit_type: str) -> Dict[str, Any]:
    """The size reference and entity scale of the unit type's profile, as the job registry spells them."""

    unit_types = json.loads((CONFIG / "unit_types.json").read_text(encoding="utf-8"))["types"]
    profiles = json.loads((CONFIG / "asset_profiles.json").read_text(encoding="utf-8"))["profiles"]
    profile = profiles[unit_types[unit_type]["profile"]]
    reference = {key: value for key, value in (profile.get("vanilla_reference") or {}).items() if key != "measurement"}
    found: Dict[str, Any] = {}
    if reference:
        found["vanilla_scale_reference"] = reference
    if profile.get("runtime_entity_scale") is not None:
        found["runtime_entity_scale"] = profile["runtime_entity_scale"]
    return found


def build_entry(preset_name: str, slug: str, sources: List[str], brief: str, answers: Dict[str, Any]) -> Dict[str, Any]:
    preset = tripo_presets.get(preset_name)
    entry: Dict[str, Any] = {
        "asset_id": f"{JOB_PREFIX}.{slug}",
        "runtime_stem": slug,
        "reference_path": f"refs/original/{slug}.png",
        "reference_sources": sources,
        "reference_source_mode": "agent_generated",
        "reference_generator_output": "tripo-image",
        "asset_brief": brief,
        "proposed_runtime_identifiers": {},
    }
    job = tripo_presets.new_job(preset_name, answers)
    if preset["route"] != "static":
        entry.update(profile_reference(job["unit_type"]))
    entry.update(job)
    return entry


def describe(name: str, preset: Dict[str, Any]) -> str:
    low, high = preset["expected_credits"]
    credits = f"{low}" if low == high else f"{low} to {high}"
    return f"{name:18} {preset['label']}. {preset['for']} Credits {credits}, cap {preset['cap']}. {preset['proven']}"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="print the presets and stop")
    parser.add_argument("--jobs-config", type=Path)
    parser.add_argument("--preset")
    parser.add_argument("slug", nargs="?")
    parser.add_argument("--source", action="append", default=[], help="a reference the picture is made from (repeat for each)")
    parser.add_argument("--brief", default="", help="one sentence: what the unit is")
    parser.add_argument("--set", action="append", default=[], dest="answers", help="<key>=<value>, see the module help")
    parser.add_argument("--replace", action="store_true", help="overwrite a job of the same name")
    args = parser.parse_args(argv)
    data = tripo_presets.load()
    if args.list:
        for name, preset in data["presets"].items():
            print(describe(name, preset))
        return 0
    if not (args.jobs_config and args.preset and args.slug):
        parser.error("give --jobs-config, --preset and the job name, or --list")
    if args.preset not in data["presets"]:
        parser.error(f"no preset {args.preset!r}. The presets are: {', '.join(data['presets'])}")
    answers = answers_from(args.answers)
    registry = json.loads(args.jobs_config.read_text(encoding="utf-8")) if args.jobs_config.exists() else {"jobs": {}}
    jobs = registry.setdefault("jobs", {})
    if args.slug in jobs and not args.replace:
        # An existing job keeps what it has and takes the new answers and sources: run again with --set for each missing value.
        entry = jobs[args.slug]
        if entry.get("preset") not in (None, args.preset):
            print(f"{args.slug!r} follows the preset {entry.get('preset')!r}. Pass --replace to start it again from {args.preset!r}.",
                  file=sys.stderr)
            return 2
        tripo_presets.apply_answers(entry, {key: value for key, value in answers.items() if key not in ("armed", "unit_type")})
        if args.source:
            entry["reference_sources"] = list(dict.fromkeys([*(entry.get("reference_sources") or []), *args.source]))
        if args.brief:
            entry["asset_brief"] = args.brief
    else:
        entry = build_entry(args.preset, args.slug, args.source, args.brief, answers)
    jobs[args.slug] = entry
    args.jobs_config.parent.mkdir(parents=True, exist_ok=True)
    args.jobs_config.write_bytes((json.dumps(registry, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    job_root = resolve_job_root(args.slug)
    print(f"job written: {args.slug} in {args.jobs_config} (preset {args.preset})")
    if entry.get("model_kind"):
        static_job = job_root / "inbox" / f"{args.slug}.json"
        static_job.parent.mkdir(parents=True, exist_ok=True)
        static_job.write_bytes((json.dumps({"name": args.slug, "model_kind": entry["model_kind"]}, indent=2) + "\n").encode("utf-8"))
        print(f"static job file written: {static_job.as_posix()}")
    missing = tripo_card.problems(entry)
    if missing:
        print("Still to add before the card (run this again with --set for each, or edit the entry):")
        for item in missing:
            print(f"- {item}")
        return 3
    print(f"next: py -3.13 -B .tools/3d_pipeline/tripo/make_card.py --jobs-config {args.jobs_config.as_posix()} {args.slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
