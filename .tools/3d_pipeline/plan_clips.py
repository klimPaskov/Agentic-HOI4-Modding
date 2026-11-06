"""Give every unit in a job registry its own library clips before any clip is paid for (decision 3D-6).

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/plan_clips.py --jobs-config docs/plans/<feature>/3d_jobs.json
    py -3.13 -B .tools/3d_pipeline/plan_clips.py --jobs-config docs/plans/<feature>/3d_jobs.json --write

A unit type lists one or more library clips per role (`config/unit_types.json`). Two units of one type
would otherwise get the same clips. Decision 3D-6 allows an identical set only for reskins of one base
unit (same body and rig, a different look); every other unit gets its own. The plan:

- goes through the jobs in the registry's order and gives each role the first candidate clip that no
  other unit already plays, in any role;
- gives a job with `"reskin_of": "<base job>"` exactly its base's clips;
- keeps a job's own `required_actions` as they are, and counts their clips as taken;
- reports a role whose every candidate is taken ("runs out"): that unit needs a clip of its own, authored
  live in Blender or added to the unit type's candidates, or the user's approval to share.

`--write` writes each planned job's `required_actions` into the registry, which `run_pilot.py` then uses
as they are. Without it nothing changes. A registry may set `"animation_policy": "authored"` (Chaos
Redux authors every animation live): then no library clip is planned and every library role is
reported for live authoring. Reads files only; no provider call, no cost.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import stage_verdict

POLICIES = ("presets", "authored")


def default_actions(job: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The rows `run_pilot.apply_unit_type` builds for the job's unit type."""

    import run_pilot

    spec = run_pilot.apply_unit_type({key: value for key, value in job.items() if key != "required_actions"})
    return copy.deepcopy(spec.get("required_actions", []))


def paid_clips(actions: List[Dict[str, Any]]) -> Set[int]:
    return {int(row["provider_action_id"]) for row in actions if row.get("provider_action_id") is not None}


def choose(row: Dict[str, Any], taken: Set[int]) -> Tuple[Dict[str, Any], bool]:
    """The row with its first untaken candidate moved to the front; False when every candidate is taken."""

    candidates = [list(item) for item in row.get("library_candidates") or [[row["provider_action_id"], row.get("library_key", "")]]]
    free = [item for item in candidates if int(item[0]) not in taken]
    if not free:
        return row, False
    first = free[0]
    ordered = [first] + [item for item in candidates if item is not first]
    updated = dict(row, provider_action_id=int(first[0]), library_key=first[1], library_candidates=ordered)
    return updated, True


def plan(registry: Dict[str, Any]) -> Dict[str, Any]:
    """The planned actions per job, the shared clips and the roles that ran out."""

    jobs: Dict[str, Dict[str, Any]] = registry.get("jobs") or registry.get("pilots") or {}
    policy = registry.get("animation_policy", "presets")
    if policy not in POLICIES:
        raise SystemExit(f"animation_policy must be one of {', '.join(POLICIES)}, not {policy!r}")
    planned: Dict[str, List[Dict[str, Any]]] = {}
    owner: Dict[int, str] = {}  # clip id -> the unit (or reskin group) that plays it
    ran_out: List[Dict[str, str]] = []
    authored: List[Dict[str, str]] = []
    group = {slug: job.get("reskin_of") or slug for slug, job in jobs.items()}
    for slug, job in jobs.items():
        if job.get("reskin_of") and job["reskin_of"] not in jobs:
            raise SystemExit(f"{slug}: reskin_of names {job['reskin_of']!r}, which is not a job in this registry")
    # Jobs with their own actions claim their clips first.
    for slug, job in jobs.items():
        if job.get("required_actions"):
            for clip in paid_clips(job["required_actions"]):
                owner.setdefault(clip, group[slug])
    for slug, job in sorted(jobs.items(), key=lambda item: bool(item[1].get("reskin_of"))):
        if job.get("required_actions") or not job.get("unit_type"):
            continue
        rows = default_actions(job)
        if policy == "authored":
            authored += [{"unit": slug, "role": row["role"]} for row in rows if row.get("provider_action_id") is not None]
            continue
        if job.get("reskin_of"):
            base = planned.get(job["reskin_of"]) or jobs[job["reskin_of"]].get("required_actions") or []
            planned[slug] = copy.deepcopy(base)
            continue
        taken = {clip for clip, unit in owner.items() if unit != group[slug]}
        chosen = []
        for row in rows:
            if row.get("provider_action_id") is None:
                chosen.append(row)
                continue
            updated, ok = choose(row, taken)
            if not ok:
                ran_out.append({"unit": slug, "role": row["role"], "clip": str(row["provider_action_id"]), "played_by": owner.get(int(row["provider_action_id"]), "")})
            chosen.append(updated)
            owner.setdefault(int(updated["provider_action_id"]), group[slug])
            taken.add(int(updated["provider_action_id"]))
        planned[slug] = chosen
    return {"policy": policy, "planned": planned, "ran_out": ran_out, "authored": authored}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--jobs-config", type=Path, required=True, help="the job registry (3d_jobs.json)")
    parser.add_argument("--write", action="store_true", help="write each planned job's required_actions into the registry")
    parser.add_argument("--verdict", type=Path, help="also write the verdict to this file")
    args = parser.parse_args(argv)
    registry = json.loads(args.jobs_config.read_text(encoding="utf-8"))
    result = plan(registry)
    clips = {slug: {row["role"]: row.get("provider_action_id") for row in rows} for slug, rows in result["planned"].items()}
    outputs = {"policy": result["policy"], "clips": clips, "ran_out": result["ran_out"], "authored": result["authored"]}
    if result["authored"]:
        escalate = {
            "rules": ["CLIPS-AUTHORED"],
            "why": ["this project authors every animation live (animation_policy authored)"],
            "how": f"Author each listed role live in Blender ({stage_verdict.LIVE_GUIDE}).",
        }
        payload = stage_verdict.verdict("plan", False, args.jobs_config.stem, outputs=outputs, escalate=escalate)
    elif result["ran_out"]:
        escalate = {
            "rules": ["CLIPS-RAN-OUT"],
            "why": [f"{item['unit']} {item['role']}: every candidate clip is already played by another unit ({item['played_by']})" for item in result["ran_out"]],
            "how": f"Give those roles clips of their own: author them live ({stage_verdict.LIVE_GUIDE}), add another candidate to the unit type, or ask the user whether the units may share (only reskins of one base unit should).",
        }
        payload = stage_verdict.verdict("plan", False, args.jobs_config.stem, outputs=outputs, escalate=escalate)
    else:
        steps = [] if args.write else [f"{stage_verdict.PY} {stage_verdict.PIPELINE}/plan_clips.py --jobs-config {stage_verdict.quote(args.jobs_config.as_posix())} --write"]
        payload = stage_verdict.verdict("plan", True, args.jobs_config.stem, outputs=outputs, next_steps=steps)
    if args.write and not result["authored"]:
        for slug, rows in result["planned"].items():
            registry_jobs = registry.get("jobs") or registry.get("pilots")
            registry_jobs[slug]["required_actions"] = rows
        args.jobs_config.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8", newline="\n")
    stage_verdict.write(payload, args.verdict)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
