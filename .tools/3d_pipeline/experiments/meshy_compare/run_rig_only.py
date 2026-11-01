"""Run exactly one Meshy rig (5 credits) on a job whose generation already succeeded. No animation.

run_pilot.py cannot do this: its humanoid continuation needs an `attack` provider animation and
then authors and exports in Blender. This script reuses run_pilot's own paid-call path, so the
rig goes through the same gates and the same ledger as every other paid stage:

  reuse of an earlier succeeded rig, unreconciled-submission block, attempt limit (one), the job's
  credit_budget, live balance check, reservation, submission journal, settlement, reconciliation.

It makes the paid call only with --submit-rig. Without it, it prints the request and the gate
state and exits without starting the Meshy launcher. There is no retry: a failed rig stops here.

  py -3.13 -B experiments/meshy_compare/run_rig_only.py zin_infantry_cmp_t25            # plan only
  py -3.13 -B experiments/meshy_compare/run_rig_only.py zin_infantry_cmp_t25 --submit-rig
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import run_pilot as rp
from lib.credits import budget_state, ledger_entries
from meshy_client import MeshyClient, rig_arguments


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job")
    parser.add_argument("--jobs-config", type=Path, default=HERE / "jobs.json")
    parser.add_argument("--submit-rig", action="store_true", help="make the paid meshy_rig call (5 credits)")
    args = parser.parse_args()

    spec = rp.load_job_configs(args.jobs_config)[args.job]
    rp.vet_spec(spec)
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = rp.ensure_job_layout(rp.resolve_job_root(slug))
    generation_stage = rp.generation_stage_for(spec)
    generation = rp.existing_task(job, generation_stage)
    if not generation or generation.get("status") not in rp.SUCCEEDED_STATUSES:
        raise SystemExit(f"{slug}: the {generation_stage} stage has not succeeded; run --phase candidate first.")
    generation_id = str(generation["task_id"])
    rig_stage = rp.rig_stage_for(spec)
    estimate = int(spec["rig_estimate_credits"])
    height = spec["target_height_m"]
    arguments = rig_arguments(generation_id, None, height)
    request = rp.paid_request(spec, "rig", "meshy_rig", arguments)
    state = budget_state(ledger_entries(job), spec["credit_budget"])
    plan = {
        "job": slug,
        "rig_stage": rig_stage,
        "input_task_id": generation_id,
        "request": arguments,
        "estimate_credits": estimate,
        "budget_state_before": state,
        "animations": "none",
    }
    if not args.submit_rig:
        print(json.dumps({"mode": "plan only, nothing submitted", **plan}, indent=2))
        return 0
    rp.require_api_key()
    client = MeshyClient(rp.REPO_ROOT, job)
    rig_id = rp.provider_task(
        client,
        job,
        rig_stage,
        task_type="rigging",
        estimate=estimate,
        input_stage=generation_stage,
        create=lambda: client.rig(input_task_id=generation_id, height_meters=height, estimate_credits=estimate),
        request=request,
    )
    downloads = {}
    for extension in ("glb", "fbx"):
        downloads[extension] = rp.download_once(
            client,
            job,
            stage=f"{rig_stage}_provider_{extension}",
            task_id=rig_id,
            task_type="rigging",
            format_name=extension,
            filename=rp.rig_download_name(spec, extension),
            include_textures=False,
            allow_url_only=True,
            fetch_provider_url=True,
        )
    print(json.dumps({**plan, "rig_task_id": rig_id, "downloads": downloads}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
