"""Offline credit preflight for the Meshy model comparison. Makes no provider call.

Loads jobs.json, vets each job the way run_pilot.py does before its first paid call
(settings, price table, reference approval, credit_budget), prints what each job plans and what
`--phase candidate` would still have pending, and replays the budget gate in memory for the
B job's generation followed by its rig and one more call that must stop.

It never constructs MeshyClient (that starts the Meshy launcher), so the live balance check that
run_pilot.py also makes is not part of this script; read the balance separately (see COMMANDS.txt).

  py -3.13 -B experiments/meshy_compare/budget_preflight.py [--refresh-jobs]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE_ROOT = HERE.parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
os.environ.setdefault("MESHY_API_KEY", os.environ.get("MESHY_API_KEY", ""))

import run_pilot
from lib.credits import BudgetExceeded, PaidRequest, check_budget


def planned(spec):
    return [
        {"stage": s["stage"], "operation": s["operation"], "credits": s["estimate_credits"]}
        for s in run_pilot.planned_stages(spec)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-jobs", action="store_true", help="also run run_pilot.initialize_job (writes job.yaml only)")
    args = parser.parse_args()
    configs = run_pilot.load_job_configs(HERE / "jobs.json")
    report = {}
    for name, spec in configs.items():
        run_pilot.vet_spec(spec)
        if args.refresh_jobs:
            run_pilot.initialize_job(spec)
        full = planned(spec)
        candidate = run_pilot.pending_stages(spec, "candidate")
        report[name] = {
            "profile": spec["profile"],
            "ai_model": spec["generation"]["ai_model"],
            "model_type": spec["generation"]["model_type"],
            "target_polycount": spec["generation"]["target_polycount"],
            "should_remesh": spec["generation"]["should_remesh"],
            "credit_budget": spec["credit_budget"],
            "planned_by_runner": full,
            "planned_total": spec["planned_total_credits"],
            "image_to_3d_request": run_pilot.image_to_3d_arguments(
                (run_pilot.resolve_job_root(spec["asset_id"].rsplit(".", 1)[-1]) / spec["reference_path"]).resolve(),
                spec["generation"],
                spec["meshy_pose_mode"],
            ),
            "pending_for_phase_candidate": [
                {"stage": s["stage"], "credits": s["estimate_credits"]} for s in candidate
            ],
        }
        run_pilot.require_budget_headroom(candidate, [spec])
        report[name]["phase_candidate_headroom"] = "ok"
    # Replay the budget gate for job B in memory: generation 15, rig 5, then a call that must stop.
    spec_b = configs["zin_infantry_cmp_t25"]
    budget = spec_b["credit_budget"]
    rows = []

    def request(op, tool):
        return PaidRequest(op, tool, None, "0" * 64, op, 1, budget)

    replay = []
    for stage, op, tool, estimate in (
        ("generation", "image_to_3d", "meshy_image_to_3d", spec_b["image_to_3d_estimate_credits"]),
        ("rig", "rig", "meshy_rig", spec_b["rig_estimate_credits"]),
        ("extra_call_that_must_stop", "remesh", "meshy_remesh", spec_b["remesh_estimate_credits"]),
    ):
        try:
            state = check_budget(rows, request(op, tool), stage, estimate)
            rows.append({"attempt_id": stage, "stage": stage, "outcome": "success", "consumed_credits": estimate,
                         "estimate_credits": estimate})
            replay.append({"stage": stage, "estimate": estimate, "result": "allowed", "remaining_before": state["remaining"]})
        except BudgetExceeded as stop:
            replay.append({"stage": stage, "estimate": estimate, "result": "stopped before submission", "message": str(stop)[:160]})
    report["job_B_budget_replay"] = replay
    report["total_if_everything_runs"] = sum(
        report[n]["pending_for_phase_candidate"][0]["credits"] for n in configs
    ) + spec_b["rig_estimate_credits"]
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
