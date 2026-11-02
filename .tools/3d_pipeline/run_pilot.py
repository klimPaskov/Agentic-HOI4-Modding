"""Run explicitly configured 3D model jobs through Meshy and Blender."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import Image


PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_ROOT.parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from blender_client import BlenderAdapterClient  # noqa: E402
from lib.paths import (  # noqa: E402
    append_history,
    dds_converter,
    ensure_job_layout,
    file_record,
    read_job_document,
    read_json,
    resolve_job_root,
    utc_now,
    write_json,
)
from lib.credits import (
    CreditStop,
    PaidRequest,
    UnreconciledSubmission,
    attempt_limit,
    attempt_scope,
    budget_state,
    check_attempt_limit,
    check_budget,
    consumption,
    credits_report,
    find_job_roots,
    format_report,
    already_reused,
    ledger_entries,
    open_reservation,
    read_ledger,
    record_local_repair,
    record_reuse,
    request_fingerprint,
    reject,
    reserve,
    settle,
)
from lib.generation import (
    generation_estimate,
    load_contract,
    load_pricing,
    operation_credits,
    validate_generation,
)
from lib.texture_lineage import (
    dds_header,
    provider_texture_rels,
    verify_texture_lineage,
)
from lib.reuse import (
    block_message,
    copy_artifacts,
    find_other_job_result,
    sibling_jobs,
    unreconciled_submissions,
)
from meshy_client import (  # noqa: E402
    REQUIRED_KEY_MESSAGE,
    MeshyClient,
    MeshyTaskFailed,
    _first_key,
    _payload,
    animate_arguments,
    image_to_3d_arguments,
    remesh_arguments,
    rig_arguments,
    server_version,
    status_from,
    task_id_from,
)
from pack_pdx_material import (  # noqa: E402
    pack_pdx_normal_map,
    pack_pdx_specular_map,
    prepare_texture_source_rels,
)


STATIC_ASSET_KINDS = {"static", "building", "static_building"}
CREATURE_ASSET_KINDS = {"creature"}
REFERENCE_CALIBRATED_ASSET_KINDS = {"humanoid", "creature", "building", "static_building"}
SUCCEEDED_STATUSES = {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}


def task_file(job: Path, stage: str) -> Path:
    return job / "provider" / "tasks" / f"{stage}.json"


def read_job(job: Path) -> Dict[str, Any]:
    return read_job_document(job / "job.yaml")


def stage_vanilla_reference(job: Path, spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Stage the named installed vanilla reference inside the bounded job root."""

    asset_kind = spec.get("asset_kind")
    if asset_kind not in REFERENCE_CALIBRATED_ASSET_KINDS:
        return None
    reference = spec.get("vanilla_scale_reference") or {}
    if asset_kind in {"building", "static_building"} and not reference:
        raise RuntimeError(
            "Static building preparation requires a named installed vanilla scale reference; "
            "height-only calibration is not permitted."
        )
    source = Path(str(reference.get("mesh", ""))).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Installed vanilla scale reference is missing: {source}")
    destination = job / "blender" / "reference" / source.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_record = file_record(source)
    if not destination.exists() or file_record(destination)["sha256"] != source_record["sha256"]:
        shutil.copy2(source, destination)
    staged_record = file_record(destination, relative_to=job)
    write_json(
        job / "blender" / "reports" / "vanilla_reference_stage.json",
        {
            "source_path": str(source),
            "source_sha256": source_record["sha256"],
            "staged_file": staged_record,
            "read_only_source": True,
        },
    )
    return {
        "mesh_rel": staged_record["relative_path"],
        "entity": reference.get("entity"),
        "mesh_object_names": reference.get("mesh_object_names", []),
        "exclude_name_patterns": reference.get("exclude_name_patterns", []),
        "forward_axis": reference.get("forward_axis"),
        "up_axis": reference.get("up_axis"),
        "mesh_height": reference["mesh_height"],
        "entity_scale": reference["entity_scale"],
        "runtime_height": reference["runtime_height"],
    }


def update_job(job: Path, **changes: Any) -> Dict[str, Any]:
    value = read_job(job)
    value.update(changes)
    value["updated_at"] = utc_now()
    (job / "job.yaml").write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return value


def require_api_key() -> None:
    """Hard gate before any provider or downstream work."""

    if not os.environ.get("MESHY_API_KEY", "").strip():
        print(REQUIRED_KEY_MESSAGE)
        raise SystemExit(2)


def load_profile(name: str) -> Dict[str, Any]:
    return read_json(PIPELINE_ROOT / "config" / "asset_profiles.json")["profiles"][name]


def resolve_generation(spec: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """The profile's validated generation settings, ready to send.

    A job may restate the model it expects but never change it, and may override only the
    target face count. Any disagreement stops the run before a paid call.
    """

    generation = dict(profile.get("generation") or {})
    expected = str(generation.get("ai_model", "")).lower()
    for key in ("meshy_ai_model", "resolved_meshy_ai_model"):
        stated = spec.get(key)
        if stated and str(stated).lower() != expected:
            raise RuntimeError(
                f"The job states {key}={stated!r}, but profile {spec.get('profile')!r} generates with "
                f"{expected!r}. A model never changes silently: edit the profile's generation block."
            )
    if spec.get("target_polycount"):
        generation["target_polycount"] = int(spec["target_polycount"])
    return validate_generation(generation)


def provider_animated_roles(spec: Dict[str, Any]) -> List[str]:
    return [
        str(action["role"])
        for action in spec.get("required_actions", [])
        if action.get("provider_action_id") is not None
        and action.get("task_type") != "blender_authored_skeletal"
    ]


def planned_stages(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The paid stages a job plans, in order, each with its price-table estimate."""

    def stage(name: str, operation: str, role: Optional[str], estimate: Any) -> Dict[str, Any]:
        return {"stage": name, "operation": operation, "role": role, "estimate_credits": int(estimate)}

    stages = [stage(generation_stage_for(spec), "image_to_3d", None, spec["image_to_3d_estimate_credits"])]
    if spec.get("asset_kind") != "humanoid" or uses_local_humanoid_route(spec):
        return stages
    generation = spec["generation"]
    if generation["model_type"] == "standard" and not generation["should_remesh"]:
        # Meshy ignores target_polycount here, so the rig source is usually over the rig limit.
        stages.append(stage(continuation_stage_for(spec, "rig_remesh"), "remesh", None, spec["remesh_estimate_credits"]))
    stages.append(stage(rig_stage_for(spec), "rig", None, spec["rig_estimate_credits"]))
    for role in provider_animated_roles(spec):
        stages.append(stage(animation_stage_for(spec, role), "animation", role, spec["animation_estimate_credits"]))
    return stages


def require_credit_budget(spec: Dict[str, Any]) -> int:
    budget = spec.get("credit_budget")
    if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
        raise RuntimeError(
            f"{spec['asset_id']} has no credit_budget. Paid Meshy stages need one whole number of "
            f"credits in the job spec and job.yaml; the plan costs {spec['planned_total_credits']} credits "
            "at config/meshy_pricing.json prices. Ask the user for the budget once."
        )
    return budget


def prepare_spec(spec: Dict[str, Any], *, require_budget: bool = True) -> Dict[str, Any]:
    """Fill in generation settings, price-table estimates and the job budget before any provider call.

    Idempotent. Estimates always come from config/meshy_pricing.json, never from the job.
    A path that makes no provider call passes `require_budget=False` and gets estimates only.
    """

    if spec.get("_credits_prepared"):
        return spec
    generation = resolve_generation(spec, load_profile(spec["profile"]))
    pricing = load_pricing()
    spec["generation"] = generation
    spec["meshy_ai_model"] = spec["resolved_meshy_ai_model"] = generation["ai_model"]
    spec["target_polycount"] = generation["target_polycount"]
    spec["image_to_3d_estimate_credits"] = generation_estimate(generation, pricing=pricing)
    for operation in ("remesh", "rig", "animation"):
        spec[f"{operation}_estimate_credits"] = operation_credits(operation, pricing=pricing)
    spec["planned_total_credits"] = sum(item["estimate_credits"] for item in planned_stages(spec))
    spec["pricing_source"] = {key: pricing[key] for key in ("source_url", "retrieved")}
    if not require_budget:
        return spec
    spec["credit_budget"] = require_credit_budget(spec)
    spec["_credits_prepared"] = True
    return spec


def initialize_job(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the job and keep its budget, generation settings and estimates in job.yaml."""

    from init_pilot_jobs import initialize_one  # imported here: that module gates on the API key at import

    result = initialize_one(prepare_spec(spec))
    update_job(
        ensure_job_layout(resolve_job_root(spec["asset_id"].rsplit(".", 1)[-1])),
        credit_budget=spec["credit_budget"],
        generation=spec["generation"],
        image_to_3d_estimate_credits=spec["image_to_3d_estimate_credits"],
        remesh_estimate_credits=spec["remesh_estimate_credits"],
        rig_estimate_credits=spec["rig_estimate_credits"],
        animation_estimate_credits=spec["animation_estimate_credits"],
        estimated_credits=spec["planned_total_credits"],
    )
    return result


def result_value(result: Dict[str, Any], key: str) -> Optional[Any]:
    value = _first_key(result, (key.lower(),))
    return value


def balance_value(result: Dict[str, Any]) -> Optional[int]:
    value = result_value(_payload(result), "balance")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def record_balance(
    job: Path,
    stage: str,
    result: Dict[str, Any],
    estimate: int,
    budget: Optional[Dict[str, int]] = None,
) -> int:
    balance = balance_value(result)
    if balance is None:
        raise RuntimeError("Meshy balance response did not contain a numeric balance.")
    write_json(
        job / "provider" / "credits" / f"{stage}_preflight.json",
        {
            "timestamp": utc_now(),
            "stage": stage,
            "balance_before_paid_call": balance,
            "estimated_credits": estimate,
            "hard_limit": estimate,
            "job_budget": budget,
            "paid_call_authorized_by": "job_credit_budget",
        },
    )
    if balance < estimate:
        raise RuntimeError(
            f"Meshy balance {balance} is below the {estimate}-credit gate for {stage}; short by {estimate - balance}."
        )
    return balance


def save_task(
    job: Path,
    stage: str,
    *,
    task_id: str,
    task_type: str,
    initial: Dict[str, Any],
    final: Dict[str, Any],
    estimate: int,
    input_stage: Optional[str] = None,
    request: Optional[PaidRequest] = None,
) -> None:
    consumed = _first_key(final, ("consumed_credits", "credits_used", "credit_cost"))
    record = {
        "schema_version": "1.0.0",
        "stage": stage,
        "task_id": task_id,
        "task_type": task_type,
        "initial_response": _payload(initial),
        "final_response": _payload(final),
        "status": status_from(final),
        "estimated_credits": estimate,
        "consumed_credits": consumed,
        "input_stage": input_stage,
        "provider": {
            "server_package": "@meshy-ai/meshy-mcp-server",
            "server_version": server_version(),
        },
        "recorded_at": utc_now(),
    }
    if request is not None:
        record.update(fingerprint=request.fingerprint, operation=request.operation, model=request.model)
    write_json(task_file(job, stage), record)
    append_history(
        job,
        state="provider_task_completed",
        event=stage,
        actor="meshy_mcp",
        details={
            "task_id": task_id,
            "task_type": task_type,
            "status": record["status"],
            "estimated_credits": estimate,
            "consumed_credits": consumed,
        },
    )


def record_paid_reconciliation(
    job: Path,
    stage: str,
    *,
    balance_before: Optional[int],
    balance_after: Optional[int],
    final: Dict[str, Any],
    estimate: int,
) -> Dict[str, Any]:
    """Persist provider-reported cost and the observed account balance delta."""

    consumed = _first_key(final, ("consumed_credits", "credits_used", "credit_cost"))
    try:
        observed_delta = (
            int(balance_before) - int(balance_after)
            if balance_before is not None and balance_after is not None
            else None
        )
    except (TypeError, ValueError):
        observed_delta = None
    try:
        provider_consumed = int(consumed) if consumed is not None else None
    except (TypeError, ValueError):
        provider_consumed = None
    if balance_before is None or balance_after is None:
        status = "missing_balance_boundary"
    elif provider_consumed is None:
        status = "missing_provider_consumption"
    elif observed_delta != provider_consumed:
        status = "balance_delta_mismatch"
    else:
        status = "reconciled"
    record = {
        "timestamp": utc_now(),
        "stage": stage,
        "status": status,
        "estimate_credits": estimate,
        "provider_consumed_credits": provider_consumed,
        "balance_before_paid_call": balance_before,
        "balance_after_task": balance_after,
        "observed_balance_delta": observed_delta,
    }
    write_json(job / "provider" / "credits" / f"{stage}_reconciliation.json", record)
    return record


def paid_request(
    spec: Dict[str, Any],
    operation: str,
    tool: str,
    arguments: Dict[str, Any],
    *,
    role: Optional[str] = None,
) -> PaidRequest:
    """What the credit gates need to know about one paid create, built from the exact arguments it sends."""

    return PaidRequest(
        operation=operation,
        tool=tool,
        model=spec["generation"]["ai_model"] if operation == "image_to_3d" else None,
        fingerprint=request_fingerprint(tool, arguments),
        scope=attempt_scope(operation, generation_stage_for(spec), role),
        attempt_limit=attempt_limit(operation, load_contract(), spec.get("provider_paid_attempts")),
        credit_budget=spec["credit_budget"],
    )


def stage_succeeded(job: Path, stage: str) -> bool:
    task = existing_task(job, stage)
    return bool(task and task.get("status") in SUCCEEDED_STATUSES)


def balance_after_task(client: MeshyClient) -> Optional[int]:
    """The account balance once a task ended; None when it cannot be read (the ledger then says unknown)."""

    try:
        return balance_value(client.check_balance())
    except (RuntimeError, ValueError, OSError):
        return None


def settle_attempt(
    job: Path,
    stage: str,
    request: PaidRequest,
    final: Dict[str, Any],
    *,
    outcome: str,
    estimate: int,
    task_id: str,
    balance_before: Optional[int],
    balance_after: Optional[int],
) -> None:
    """Write the reconciliation record and close the stage's ledger reservation with what it cost."""

    record = record_paid_reconciliation(
        job,
        stage,
        balance_before=balance_before,
        balance_after=balance_after,
        final=final,
        estimate=estimate,
    )
    reservation = open_reservation(read_ledger(job), stage)
    attempt_id = (
        reservation["attempt_id"]
        if reservation
        else reserve(job, request, stage=stage, estimate=estimate, reason="task recorded without a reservation")
    )
    consumed, source = consumption(record["provider_consumed_credits"], record["observed_balance_delta"])
    settle(
        job,
        attempt_id,
        outcome=outcome,
        consumed=consumed,
        source=source,
        reason=f"Meshy task {task_id} ended {status_from(final)}",
        task_id=task_id,
        reconciliation=record["status"],
        balance_before=balance_before,
        balance_after=balance_after,
    )


def gate_paid_call(
    client: MeshyClient,
    job: Path,
    stage: str,
    request: PaidRequest,
    estimate: int,
    reuse_checks: Dict[str, str],
) -> Tuple[int, str]:
    """Stop before submission unless attempts, the job budget and the live balance allow this call.

    Returns the balance before the call and the attempt id of the credits reserved for it.
    """

    entries = ledger_entries(job)
    try:
        check_attempt_limit(entries, request, stage)
        budget = check_budget(entries, request, stage, estimate)
        balance_before = record_balance(job, stage, client.check_balance(), estimate, budget)
    except (CreditStop, RuntimeError) as stop:
        reject(job, request, stage=stage, estimate=estimate, reason=str(stop), reuse_checks=reuse_checks)
        raise
    attempt_id = reserve(
        job, request, stage=stage, estimate=estimate, reason="paid create about to be submitted", reuse_checks=reuse_checks
    )
    return balance_before, attempt_id


def existing_task(job: Path, stage: str) -> Optional[Dict[str, Any]]:
    path = task_file(job, stage)
    return read_json(path) if path.exists() else None


def task_model_url(job: Path, stage: str, format_name: str) -> str:
    """Read one official signed artifact URL from an immutable completed task record."""

    task = existing_task(job, stage)
    if not task or task.get("status") not in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
        raise RuntimeError(f"Cannot resolve a provider artifact URL from incomplete stage {stage!r}.")
    final = task.get("final_response")
    model_urls = final.get("model_urls") if isinstance(final, dict) else None
    url = model_urls.get(format_name) if isinstance(model_urls, dict) else None
    if not isinstance(url, str) or not url.startswith("https://assets.meshy.ai/"):
        raise RuntimeError(
            f"Completed provider stage {stage!r} did not expose a valid Meshy artifact URL for {format_name!r}."
        )
    return url


def generation_stage_for(spec: Dict[str, Any]) -> str:
    """Return the immutable provider stage selected for this geometry attempt."""

    stage = str(spec.get("generation_stage") or "generation").strip()
    if (stage != "generation" and not stage.startswith("generation_")) or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789_" for character in stage
    ):
        raise ValueError(f"Invalid generation stage {stage!r}.")
    return stage


def generation_download_name(spec: Dict[str, Any], extension: str) -> str:
    """Keep every accepted or rejected provider attempt as a separate artifact."""

    return f"{generation_stage_for(spec)}_model.{extension.lstrip('.')}"


def continuation_stage_for(spec: Dict[str, Any], base_stage: str) -> str:
    """Keep every downstream paid provider stage bound to its generation attempt."""

    generation_stage = generation_stage_for(spec)
    if generation_stage == "generation":
        return base_stage
    return f"{generation_stage}_{base_stage}"


def continuation_download_name(spec: Dict[str, Any], filename: str) -> str:
    """Prevent a new provider attempt from overwriting earlier downloaded lineage."""

    generation_stage = generation_stage_for(spec)
    if generation_stage == "generation":
        return filename
    return f"{generation_stage}_{filename}"


def rig_stage_for(spec: Dict[str, Any]) -> str:
    """Resolve an explicitly authorized rig recovery without reusing a failed task."""

    return str(spec.get("rig_stage") or continuation_stage_for(spec, "rig"))


def rig_download_name(spec: Dict[str, Any], extension: str) -> str:
    rig_stage = rig_stage_for(spec)
    default_stage = continuation_stage_for(spec, "rig")
    if rig_stage == default_stage:
        return continuation_download_name(spec, f"rigged_provider_model.{extension}")
    return f"{rig_stage}_provider_model.{extension}"


def animation_stage_for(spec: Dict[str, Any], role: str) -> str:
    rig_stage = rig_stage_for(spec)
    default_rig_stage = continuation_stage_for(spec, "rig")
    if rig_stage == default_rig_stage:
        return continuation_stage_for(spec, f"animation_{role}")
    return f"{rig_stage}_animation_{role}"


def animation_download_name(spec: Dict[str, Any], role: str, extension: str) -> str:
    stage = animation_stage_for(spec, role)
    default_stage = continuation_stage_for(spec, f"animation_{role}")
    if stage == default_stage:
        return continuation_download_name(spec, f"animation_{role}_provider.{extension}")
    return f"{stage}_provider.{extension}"


def recover_unrecorded_task(
    job: Path,
    *,
    stage: str,
    task_type: str,
    estimate: int,
    response_name_fragment: str,
) -> Optional[Dict[str, Any]]:
    """Recover a paid task created before a process crash wrote its task file."""

    if task_file(job, stage).exists():
        return read_json(task_file(job, stage))
    candidates = sorted(
        path for path in (job / "provider" / "responses").glob("*.json")
        if response_name_fragment in path.name
    )
    if len(candidates) != 1:
        return None
    response = read_json(candidates[0])
    try:
        task_id = task_id_from(response)
    except Exception:
        return None
    recovered = {
        "schema_version": "1.0.0",
        "stage": stage,
        "task_id": task_id,
        "task_type": task_type,
        "status": "PENDING",
        "initial_response": _payload(response),
        "estimated_credits": estimate,
        "recovered_from_response": str(candidates[0].relative_to(job)).replace("\\", "/"),
        "recovered_at": utc_now(),
    }
    write_json(task_file(job, stage), recovered)
    append_history(
        job,
        state="provider_task_recovered",
        event=stage,
        actor="hoi4_3d_model_pipeline",
        details={"task_id": task_id, "response": recovered["recovered_from_response"]},
    )
    return recovered


def finish_task(
    client: MeshyClient,
    job: Path,
    stage: str,
    request: PaidRequest,
    *,
    task_id: str,
    task_type: str,
    initial: Dict[str, Any],
    estimate: int,
    input_stage: Optional[str],
    balance_before: Optional[int],
) -> str:
    """Wait for a created task, save its record and settle the ledger reservation."""

    common = {"task_id": task_id, "estimate": estimate, "balance_before": balance_before}
    try:
        final = client.wait_for_task(task_id, task_type=task_type)
    except MeshyTaskFailed as exc:
        save_task(
            job, stage, task_id=task_id, task_type=task_type, initial=initial, final=exc.final,
            estimate=estimate, input_stage=input_stage, request=request,
        )
        settle_attempt(
            job, stage, request, exc.final, outcome="failed", balance_after=balance_after_task(client), **common
        )
        raise
    save_task(
        job, stage, task_id=task_id, task_type=task_type, initial=initial, final=final,
        estimate=estimate, input_stage=input_stage, request=request,
    )
    settle_attempt(job, stage, request, final, outcome="success", balance_after=balance_after_task(client), **common)
    return task_id


def provider_task(
    client: MeshyClient,
    job: Path,
    stage: str,
    *,
    task_type: str,
    estimate: int,
    create,
    request: PaidRequest,
    input_stage: Optional[str] = None,
) -> str:
    existing = existing_task(job, stage)
    if existing:
        if existing.get("status") in SUCCEEDED_STATUSES:
            note_stage_reuse(job, stage, request, estimate, existing)
            return str(existing["task_id"])
        if existing.get("task_id") and existing.get("status") in {"PENDING", "IN_PROGRESS", "UNKNOWN"}:
            return finish_task(
                client, job, stage, request, task_id=str(existing["task_id"]), task_type=task_type,
                initial=existing.get("initial_response", {}), estimate=estimate,
                input_stage=input_stage, balance_before=None,
            )
        raise RuntimeError(
            f"Paid stage {stage} already has a non-success record. "
            "No paid retry is permitted: " + str(task_file(job, stage))
        )
    adopted, reuse_checks = reuse_before_paying(job, stage, request, estimate)
    if adopted:
        return adopted
    balance_before, _ = gate_paid_call(client, job, stage, request, estimate, reuse_checks)
    initial = create()
    task_id = task_id_from(initial)
    write_json(
        task_file(job, stage),
        {
            "schema_version": "1.0.0",
            "stage": stage,
            "task_id": task_id,
            "task_type": task_type,
            "status": "PENDING",
            "initial_response": _payload(initial),
            "estimated_credits": estimate,
            "input_stage": input_stage,
            "fingerprint": request.fingerprint,
            "operation": request.operation,
            "model": request.model,
            "provider": {
                "server_package": "@meshy-ai/meshy-mcp-server",
                "server_version": server_version(),
            },
            "created_at": utc_now(),
        },
    )
    append_history(
        job,
        state="provider_task_created",
        event=stage,
        actor="meshy_mcp",
        details={"task_id": task_id, "task_type": task_type, "estimated_credits": estimate},
    )
    return finish_task(
        client, job, stage, request, task_id=task_id, task_type=task_type, initial=initial,
        estimate=estimate, input_stage=input_stage, balance_before=balance_before,
    )


def adopt_other_job_result(
    job: Path,
    stage: str,
    request: PaidRequest,
    estimate: int,
    match: Dict[str, Any],
) -> str:
    """Continue from another job's succeeded task: copy its record and downloads, pay nothing."""

    source_job, source = match["job"], match["record"]
    task_id = str(source["task_id"])
    copied = copy_artifacts(source_job, job, task_id)
    origin = {"tier": "other_job", "job": source_job.name, "stage": source.get("stage"), "task_id": task_id}
    write_json(
        task_file(job, stage),
        {
            **source,
            "stage": stage,
            "estimated_credits": estimate,
            "consumed_credits": 0,
            "fingerprint": request.fingerprint,
            "reused_from": {**origin, "source_consumed_credits": source.get("consumed_credits"), "files": copied},
            "recorded_at": utc_now(),
        },
    )
    record_reuse(
        job,
        stage=stage,
        operation=request.operation,
        estimate=estimate,
        reason=f"the same request already succeeded in job {source_job.name} (stage {source.get('stage')})",
        model=request.model,
        fingerprint=request.fingerprint,
        scope=request.scope,
        task_id=task_id,
        reused_from=origin,
    )
    append_history(
        job,
        state="provider_task_reused",
        event=stage,
        actor="hoi4_3d_model_pipeline",
        details={**origin, "files": copied, "saved_credits": estimate},
    )
    return task_id


def reuse_before_paying(
    job: Path,
    stage: str,
    request: PaidRequest,
    estimate: int,
) -> Tuple[Optional[str], Dict[str, str]]:
    """The checks that come before paying, after this job's own succeeded stage.

    A succeeded result for the same request in another job is adopted (returns its task id). An
    unreconciled submission for the same request blocks the call. Otherwise the call may be paid, and
    the checks are returned to be written into its reservation.
    """

    checks = {"job_stage": "no succeeded task for this stage"}
    found = find_other_job_result(job, request.fingerprint)
    if found["match"]:
        return adopt_other_job_result(job, stage, request, estimate, found["match"]), checks
    skipped = f"; {len(found['expired'])} expired" if found["expired"] else ""
    checks["other_jobs"] = f"no usable succeeded result with this fingerprint in {found['jobs_checked']} other job(s){skipped}"
    blockers = unreconciled_submissions([job] + sibling_jobs(job), request.fingerprint)
    if blockers:
        message = block_message(stage, request.operation, blockers)
        checks["submission_journal"] = f"{len(blockers)} unreconciled submission(s)"
        reject(job, request, stage=stage, estimate=estimate, reason=message, reuse_checks=checks)
        raise UnreconciledSubmission(message)
    checks["submission_journal"] = "no unreconciled submission for this request"
    checks["meshy_lookup"] = "not searched: meshy_list_tasks cannot identify the input image"
    append_history(
        job,
        state="provider_reuse_decision",
        event=stage,
        actor="hoi4_3d_model_pipeline",
        details={"decision": "pay", "checks": checks},
    )
    return None, checks


def note_stage_reuse(job: Path, stage: str, request: PaidRequest, estimate: int, task: Dict[str, Any]) -> None:
    """Record, once per task, that a succeeded stage in this job spared a new paid call."""

    if already_reused(read_ledger(job), stage, str(task["task_id"])):
        return
    record_reuse(
        job,
        stage=stage,
        operation=request.operation,
        estimate=estimate,
        reason="the stage already succeeded in this job",
        model=request.model,
        fingerprint=request.fingerprint,
        scope=request.scope,
        task_id=str(task["task_id"]),
        reused_from={"tier": "job_stage", "job": job.name, "stage": stage},
    )


def download_once(
    client: MeshyClient,
    job: Path,
    *,
    stage: str,
    task_id: str,
    task_type: str,
    format_name: str,
    filename: str,
    include_textures: bool = True,
    allow_url_only: bool = False,
    fetch_provider_url: bool = False,
) -> Dict[str, Any]:
    destination = job / "provider" / "downloads" / filename
    manifest = job / "provider" / "downloads" / f"{destination.name}.manifest.json"
    url_manifest = job / "provider" / "downloads" / f"{destination.name}.url.json"
    if destination.exists() and manifest.exists():
        return read_json(manifest)
    if fetch_provider_url and url_manifest.exists():
        url_record = read_json(url_manifest)
        return client.fetch_provider_artifact(
            task_id=task_id,
            task_type=task_type,
            format_name=format_name,
            url=url_record["url"],
            destination=destination,
            include_textures=include_textures,
        )
    if allow_url_only and url_manifest.exists():
        return read_json(url_manifest)
    if destination.exists():
        record = {
            "timestamp": utc_now(),
            "task_id": task_id,
            "task_type": task_type,
            "format": format_name,
            "include_textures": include_textures,
            "file": file_record(destination, relative_to=job),
            "recovered_manifest": True,
        }
        write_json(manifest, record)
        return record
    result = client.download(
        task_id=task_id,
        task_type=task_type,
        format_name=format_name,
        destination=destination,
        include_textures=include_textures,
        allow_url_only=allow_url_only,
    )
    if result.get("url_only") and fetch_provider_url:
        return client.fetch_provider_artifact(
            task_id=task_id,
            task_type=task_type,
            format_name=format_name,
            url=result["url"],
            destination=destination,
            include_textures=include_textures,
        )
    if result.get("url_only"):
        return result
    append_history(
        job,
        state="provider_artifact_downloaded",
        event=stage,
        actor="meshy_mcp",
        details={"task_id": task_id, "format": format_name, "file": result["file"]},
    )
    return result


def candidate_gate(
    job: Path,
    prep: Dict[str, Any],
    *,
    hard_max: int,
    stage: str,
    max_runtime_footprint_m: Optional[float] = None,
    runtime_entity_scale: float = 1.0,
    profile: Optional[Dict[str, Any]] = None,
    weights_after: Any = None,
) -> None:
    """Block a candidate that fails a measured check.

    The profile checks (non-manifold and boundary edges, loose parts, preferred
    triangle range, material slots, residual zero-weight vertices) come from the
    job's asset profile and block unless the profile records an exception with a
    reason. A measurement missing from the report blocks too.
    """

    # Imported here so this gate stays self-contained.
    from lib.profile_gates import ProfileGateError, evaluate_candidate, job_profile

    geometry = prep.get("geometry", {})
    failures = []
    if geometry.get("triangles", 0) <= 0:
        failures.append("no triangles")
    if geometry.get("triangles", 0) > hard_max:
        failures.append(f"triangles exceed hard maximum {hard_max}")
    if geometry.get("degenerate_faces", 0):
        failures.append("degenerate faces remain")
    if geometry.get("negative_scale_objects"):
        failures.append("negative scale remains")
    if max_runtime_footprint_m is not None:
        dimensions = geometry.get("dimensions", [0.0, 0.0, 0.0])
        runtime_footprint = max(float(dimensions[0]), float(dimensions[1])) * runtime_entity_scale
        if runtime_footprint > float(max_runtime_footprint_m) + 1e-5:
            failures.append(
                f"runtime footprint {runtime_footprint:.4f}m exceeds "
                f"budget {float(max_runtime_footprint_m):.4f}m"
            )
    profile_name: Optional[str] = None
    evaluation: Dict[str, Any] = {"checks": {}, "exceptions_applied": []}
    try:
        if profile is None:
            profile_name, profile = job_profile(job)
        evaluation = evaluate_candidate(profile, prep, weights_after=weights_after)
        failures.extend(evaluation["failures"])
    except ProfileGateError as exc:
        failures.append(f"asset profile checks could not run: {exc}")
    record = {
        "failures": failures,
        "geometry": geometry,
        "runtime_footprint": prep.get("runtime_footprint"),
        "profile": profile_name,
        "checks": evaluation["checks"],
        "exceptions_applied": evaluation["exceptions_applied"],
    }
    if failures:
        write_json(job / "validation" / f"{stage}_gate.json", {"status": "blocked", **record})
        raise RuntimeError(f"Geometry gate failed for {stage}: {failures}")
    write_json(
        job / "validation" / f"{stage}_gate.json",
        {
            "status": "passed_with_exceptions" if evaluation["exceptions_applied"] else "passed",
            **record,
            "visual_review_required": True,
            "visual_review": "pending_parent_review",
        },
    )


def action_name_for_role(prep: Dict[str, Any], role: str) -> str:
    """Resolve a provider animation's actual Blender action name."""

    actions = prep.get("rig_and_actions", {}).get("actions", [])
    if not actions:
        raise RuntimeError(f"No Blender actions were imported for required role {role!r}.")
    aliases = {
        "death": ("death", "dead", "dying"),
        "move": ("move", "walk", "run", "locomotion"),
        "attack": ("attack", "strike", "combat"),
        "idle": ("idle", "stand"),
    }
    role_terms = aliases.get(role.casefold(), (role.casefold(),))
    matches = [
        action for action in actions
        if any(term in str(action.get("name", "")).casefold() for term in role_terms)
    ]
    working_matches = [
        action for action in matches
        if "working" in str(action.get("name", "")).casefold()
    ]
    if len(working_matches) == 1:
        return str(working_matches[0]["name"])
    if len(matches) == 1:
        return str(matches[0]["name"])
    if len(actions) == 1:
        return str(actions[0]["name"])
    raise RuntimeError(
        f"Could not unambiguously map provider action role {role!r}: "
        + json.dumps(actions, sort_keys=True)
    )


def exported_animation_path(report: Dict[str, Any]) -> str:
    """Return the recorded animation path from either adapter response shape."""

    export = report.get("export", {})
    for key in ("anim", "animation", "output_rel"):
        value = export.get(key)
        if isinstance(value, str) and value:
            return value
    fallback = report.get("output_rel")
    if isinstance(fallback, str) and fallback:
        return fallback
    raise ValueError(f"Animation export response did not contain an output path: {export!r}")


def prepare_pilot_texture_sources(
    job: Path,
    spec: Dict[str, Any],
    *,
    exported_rels: Sequence[str] = (),
    geometry_source_rel: Optional[str] = None,
) -> Dict[str, str]:
    """Create and select the engine-compatible material source maps.

    Each GLB in `exported_rels` is a model whose geometry reaches the export (or
    `geometry_source_rel` when that supplies the geometry). The provider maps must
    pass the texture lineage gate against it before anything is prepared for Blender.
    """

    # The provider sources are chosen once (the spec default or
    # `select_geometry_textures`). A second call must not mistake the prepared
    # bindings (roughness.png) for the provider maps.
    provider_sources = dict(
        spec.get("_provider_texture_source_rels") or spec.get("texture_source_rels", {})
    )
    spec["_provider_texture_source_rels"] = provider_sources
    for exported_rel in exported_rels:
        gate_texture_lineage(
            job, spec, source_rel=exported_rel, geometry_source_rel=geometry_source_rel
        )
    sources = prepare_texture_source_rels(job, provider_sources)
    if sources:
        spec["texture_source_rels"] = sources
    return sources


def select_geometry_textures(job: Path, spec: Dict[str, Any], model_rel: str) -> Dict[str, str]:
    """Bind the provider maps downloaded with `model_rel`, the model whose UV layout is exported.

    Meshy stages have different UV layouts. Remesh, rig and animation output
    keeps the remesh layout, so its maps are `remesh_model_textures/*`, never the
    earlier generation model's.
    """

    rels = provider_texture_rels(model_rel)
    missing = [rel for rel in rels.values() if not (job / rel).is_file()]
    if missing:
        raise FileNotFoundError(
            f"The textures downloaded with {model_rel} are missing: {missing}. "
            "Do not substitute another stage's maps; they use a different UV layout."
        )
    spec["texture_source_rels"] = rels
    spec.pop("_provider_texture_source_rels", None)
    spec["texture_lineage_model_rel"] = model_rel
    return rels


def gate_texture_lineage(
    job: Path,
    spec: Dict[str, Any],
    *,
    source_rel: str,
    geometry_source_rel: Optional[str] = None,
) -> Dict[str, Any]:
    """Fail before export unless the bound maps belong to the exported geometry's model."""

    provider_sources = dict(
        spec.get("_provider_texture_source_rels") or spec.get("texture_source_rels") or {}
    )
    if not provider_sources:
        return {}
    geometry_rel = geometry_source_rel or source_rel
    stem = Path(geometry_rel).stem
    report = verify_texture_lineage(
        job,
        geometry_rel,
        provider_sources,
        report_rel=f"blender/reports/texture_lineage_{stem}.json",
    )
    spec.setdefault("_texture_lineage", {})[stem] = report
    return report


def _finalize_pdx_runtime_texture(
    job: Path,
    spec: Dict[str, Any],
    textures: Dict[str, Any],
    *,
    source_rel: str,
    image_name: str,
    packer: Any,
    report_key: str,
    layout: Dict[str, str],
) -> Dict[str, Any]:
    """Replace one extracted working map with its final PDX-layout DDS."""

    pack_report = packer(job, source_rel)
    if pack_report.get("status") not in {"packed", "already_packed"}:
        return textures
    output_rel = pack_report["output"]["path"]
    packed_source = job / output_rel
    conversion = next(
        (
            item
            for item in textures.get("conversions", [])
            if item.get("image") == image_name
        ),
        None,
    )
    if conversion is None:
        raise RuntimeError(f"No extracted normal texture conversion for {image_name}.")
    processed_rel = f"textures/processed/{image_name}.png"
    processed = job / processed_rel
    if processed.exists():
        if not processed.is_file():
            raise RuntimeError(f"Processed texture target is not a file: {processed}")
        processed.unlink()
    shutil.copy2(packed_source, processed)
    dds_rel = str(conversion["dds"])
    dds = job / dds_rel
    if dds.exists():
        try:
            dds.unlink()
        except OSError as exc:
            raise RuntimeError(f"Unable to replace existing DDS output: {dds}") from exc
    converter = dds_converter()
    converter_args = [
        sys.executable,
        str(converter),
        "--input",
        str(processed),
        "--output",
        str(dds),
    ]
    width = conversion.get("width")
    height = conversion.get("height")
    if width and height:
        converter_args.extend(["--width", str(width), "--height", str(height)])
    completed = subprocess.run(
        converter_args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=600,
        check=False,
    )
    if completed.returncode != 0 or not dds.exists():
        raise RuntimeError(f"PDX runtime DDS conversion failed for {dds}.")
    conversion["png"] = processed_rel
    conversion["layout"] = layout
    textures[report_key] = pack_report
    return textures


def _apply_runtime_diffuse_grade(
    job: Path,
    spec: Dict[str, Any],
    textures: Dict[str, Any],
) -> Dict[str, Any]:
    """Make a deliberately dark provider diffuse map readable in the engine.

    The provider source remains immutable. The runtime-derived diffuse map is
    rebuilt from that source on every continuation, so repeated runs never
    compound the grade. A gamma below one lifts near-black cloth without
    flattening the authored seams and hardware detail.
    """

    gamma = float(spec.get("runtime_diffuse_gamma", 1.0))
    if gamma <= 0.0:
        raise ValueError("runtime_diffuse_gamma must be greater than zero.")
    if abs(gamma - 1.0) < 1e-9 or spec["asset_kind"] not in {"humanoid", "creature"}:
        return textures

    provider_sources = dict(
        spec.get("_provider_texture_source_rels")
        or spec.get("texture_source_rels")
        or {}
    )
    source_rel = provider_sources.get("diffuse")
    if not source_rel:
        raise RuntimeError("Runtime diffuse grading requires a provider diffuse source.")
    source = (job / source_rel).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Runtime diffuse source is missing: {source}")
    conversion = next(
        (
            item
            for item in textures.get("conversions", [])
            if item.get("image") == "texture_0"
        ),
        None,
    )
    if conversion is None:
        raise RuntimeError("No extracted diffuse texture conversion was recorded.")

    width = int(conversion.get("width") or 1024)
    height = int(conversion.get("height") or 1024)
    processed_rel = f"textures/processed/{conversion['image']}.png"
    processed = job / processed_rel
    with Image.open(source) as source_image:
        rgba = source_image.convert("RGBA")
        if rgba.size != (width, height):
            rgba = rgba.resize((width, height), Image.Resampling.LANCZOS)
        lut = [
            int(round(255.0 * ((value / 255.0) ** gamma)))
            for value in range(256)
        ]
        graded_rgb = Image.merge(
            "RGB",
            tuple(channel.point(lut) for channel in rgba.convert("RGB").split()),
        )
        graded = Image.merge("RGBA", (*graded_rgb.split(), rgba.getchannel("A")))
        graded.save(processed, format="PNG", optimize=True)

    dds = job / str(conversion["dds"])
    if dds.exists():
        if not dds.is_file():
            raise RuntimeError(f"Runtime diffuse DDS target is not a file: {dds}")
        dds.unlink()
    converter = dds_converter()
    converter_args = [
        sys.executable,
        str(converter),
        "--input",
        str(processed),
        "--output",
        str(dds),
        "--width",
        str(width),
        "--height",
        str(height),
    ]
    completed = subprocess.run(
        converter_args,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=600,
        check=False,
    )
    if completed.returncode != 0 or not dds.exists():
        raise RuntimeError(f"Runtime diffuse DDS conversion failed for {dds}.")
    conversion["png"] = processed_rel
    textures["runtime_diffuse_grade"] = {
        "source": source_rel,
        "processed": processed_rel,
        "dds": str(conversion["dds"]),
        "gamma": gamma,
        "policy": "provider_source_rebuilt_each_run_with_single_gamma_lift",
    }
    return textures


def _dds_header_report(job: Path, textures: Dict[str, Any]) -> Dict[str, Any]:
    """Report each shipped DDS's size and mip count.

    The repository converter writes one mip level (`convert_to_dds.py` fixes
    `-m 1` and offers no option), so this reports `mip_chain_present: false`
    instead of failing every export. The game then samples the full-size map at
    every distance, which shows as shimmer on the zoomed-out map.
    """

    report: Dict[str, Any] = {}
    for item in textures.get("conversions") or []:
        path = job / item["dds"]
        if path.is_file():
            report[item["dds"]] = dds_header(path)
    return report


def finalize_pdx_runtime_textures(
    job: Path,
    spec: Dict[str, Any],
    textures: Dict[str, Any],
) -> Dict[str, Any]:
    """Keep Blender previews conventional while installing PDX runtime DDS maps."""

    textures = _apply_runtime_diffuse_grade(job, spec, textures)
    provider_sources = dict(
        spec.get("_provider_texture_source_rels")
        or spec.get("texture_source_rels")
        or {}
    )
    if spec["asset_kind"] in {"humanoid", "creature"}:
        # The preview binding deliberately uses roughness.png. The runtime
        # binding must always go back to the provider metallic/roughness source
        # so the PDX packed channels cannot silently be replaced by gray RGB.
        specular_source = provider_sources.get("specular")
        if not specular_source:
            raise RuntimeError("Humanoid runtime material finalization requires a specular source.")
        if Path(specular_source).name.casefold() == "roughness.png":
            # Stay in the bound model's own folder; never assume the generation stage.
            candidate = job / Path(specular_source).with_name("metallic_roughness.png")
            if not candidate.is_file():
                raise FileNotFoundError(
                    "Humanoid runtime material finalization requires the provider metallic_roughness.png"
                    f" map next to {specular_source}."
                )
            provider_sources["specular"] = str(candidate.relative_to(job)).replace("\\", "/")
    image_names = {
        "diffuse": "texture_0" if spec["asset_kind"] in {"humanoid", "creature"} else "Image_0",
        "specular": "texture_specular" if spec["asset_kind"] in {"humanoid", "creature"} else "Image_1",
        "normal": "texture_normal" if spec["asset_kind"] in {"humanoid", "creature"} else "Image_2",
    }
    specular_rel = provider_sources.get("specular")
    if specular_rel:
        textures = _finalize_pdx_runtime_texture(
            job,
            spec,
            textures,
            source_rel=specular_rel,
            image_name=image_names["specular"],
            packer=pack_pdx_specular_map,
            report_key="pdx_specular_pack",
            layout={
                "red": "unused_mask_zero",
                "green": "specular_level_32",
                "blue": "metallic",
                "alpha": "roughness",
            },
        )
    normal_rel = provider_sources.get("normal")
    if normal_rel:
        textures = _finalize_pdx_runtime_texture(
            job,
            spec,
            textures,
            source_rel=normal_rel,
            image_name=image_names["normal"],
            packer=pack_pdx_normal_map,
            report_key="pdx_normal_pack",
            layout={
                "red": "unused_zero",
                "green": "source_normal_red_tangent_x",
                "blue": "unused_zero",
                "alpha": "source_normal_green_tangent_y",
            },
        )
    report = job / "blender" / "reports" / "textures_dds.json"
    textures["runtime_texture_sources"] = provider_sources
    if spec.get("_texture_lineage"):
        textures["texture_lineage"] = {
            stem: {
                "status": item["status"],
                "geometry_source_rel": item["geometry_source_rel"],
                "geometry_source_sha256": item["geometry_source_sha256"],
                "roles": {
                    role: {
                        "bound_sha256": entry["bound_sha256"],
                        "matched_via": entry["matched_via"],
                        "geometry_embedded_sha256": entry["geometry_embedded_sha256"],
                        "geometry_downloaded_sha256": entry["geometry_downloaded_sha256"],
                    }
                    for role, entry in item["roles"].items()
                },
            }
            for stem, item in spec["_texture_lineage"].items()
        }
    textures["dds_headers"] = _dds_header_report(job, textures)
    report.write_text(json.dumps(textures, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return textures


def run_candidate(spec: Dict[str, Any]) -> Dict[str, Any]:
    prepare_spec(spec)
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    client = MeshyClient(REPO_ROOT, job)
    blender = BlenderAdapterClient(REPO_ROOT)
    vanilla_reference = stage_vanilla_reference(job, spec)
    generation_stage = generation_stage_for(spec)
    # The legacy unrecorded-task recovery scans response names that do not
    # contain a logical attempt id. Restrict it to the original stage so a
    # rejected response can never be mistaken for an explicitly authorised
    # recovery attempt.
    if generation_stage == "generation":
        recover_unrecorded_task(
            job,
            stage=generation_stage,
            task_type="image-to-3d",
            estimate=spec["image_to_3d_estimate_credits"],
            response_name_fragment="image_to_3d",
        )
    reference = job / spec["reference_path"]
    generation_id = provider_task(
        client,
        job,
        generation_stage,
        task_type="image-to-3d",
        estimate=spec["image_to_3d_estimate_credits"],
        create=lambda: client.image_to_3d(
            image_path=reference,
            generation=spec["generation"],
            pose_mode=spec["meshy_pose_mode"],
            estimate_credits=spec["image_to_3d_estimate_credits"],
        ),
        request=paid_request(
            spec,
            "image_to_3d",
            "meshy_image_to_3d",
            image_to_3d_arguments(reference.resolve(), spec["generation"], spec["meshy_pose_mode"]),
        ),
    )
    generation_glb = download_once(
        client,
        job,
        stage=f"{generation_stage}_glb",
        task_id=generation_id,
        task_type="image-to-3d",
        format_name="glb",
        filename=generation_download_name(spec, "glb"),
    )
    download_once(
        client,
        job,
        stage=f"{generation_stage}_fbx",
        task_id=generation_id,
        task_type="image-to-3d",
        format_name="fbx",
        filename=generation_download_name(spec, "fbx"),
    )
    profile = read_json(PIPELINE_ROOT / "config" / "asset_profiles.json")["profiles"][spec["profile"]]
    footprint_config = profile.get("footprint", {})
    max_runtime_footprint_m = footprint_config.get("max_runtime_footprint_m")
    runtime_footprint_policy = spec.get("runtime_footprint_policy", "reject")
    texture_sources = (
        prepare_pilot_texture_sources(
            job, spec, exported_rels=[generation_glb["file"]["relative_path"]]
        )
        if spec["asset_kind"] in STATIC_ASSET_KINDS | {"humanoid", "creature"}
        else {}
    )
    prep = blender.prepare_candidate(
        slug,
        source_rel=generation_glb["file"]["relative_path"],
        asset_kind=spec["asset_kind"],
        target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
        runtime_stem=f"{spec['runtime_stem']}_candidate",
        target_triangles=profile["triangle_range"]["working_triangle_target"],
        vanilla_reference=vanilla_reference,
        texture_source_rels=texture_sources,
        max_runtime_footprint_m=max_runtime_footprint_m,
        runtime_footprint_policy=runtime_footprint_policy,
    )
    candidate_gate(
        job,
        prep,
        hard_max=profile["triangle_range"]["hard_max"],
        stage="provider_candidate",
        max_runtime_footprint_m=max_runtime_footprint_m,
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
    )
    update_job(job, status="candidate_qa", selected_provider_task=generation_id)
    append_history(
        job,
        state="candidate_qa",
        event="blender_candidate_prepared",
        actor="hoi4_3d_model_pipeline",
        details={
            "generation_task_id": generation_id,
            "checkpoint": prep["checkpoints"]["pre_export"],
            "previews": prep["previews"],
        },
    )
    return {
        "slug": slug,
        "job_root": str(job),
        "generation_task_id": generation_id,
        "generation_glb": generation_glb,
        "prepare": prep,
    }


def continue_static(spec: Dict[str, Any]) -> Dict[str, Any]:
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    blender = BlenderAdapterClient(REPO_ROOT)
    prep_report = read_json(job / "blender" / "reports" / f"{spec['runtime_stem']}_candidate_prepare.json")
    pre_export = prep_report["checkpoints"]["pre_export"]
    textures = finalize_pdx_runtime_textures(
        job,
        spec,
        blender.process_textures(slug, pre_export),
    )
    mesh_rel = f"export/mesh/{spec['runtime_stem']}.mesh"
    exported = blender.export_mesh(slug, pre_export, mesh_rel)
    reimport = blender.reimport_export(slug, mesh_rel)
    mesh_file = job / mesh_rel
    update_job(job, status="pdx_exported", exports={"mesh": mesh_rel})
    append_history(
        job,
        state="pdx_exported",
        event="static_pilot_exported",
        actor="hoi4_3d_model_pipeline",
        details={"mesh": file_record(mesh_file, relative_to=job), "reimport": reimport},
    )
    return {"textures": textures, "export": exported, "reimport": reimport}


def continue_creature(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Build, rig, animate, export, and reimport a custom nonhumanoid unit."""

    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    blender = BlenderAdapterClient(REPO_ROOT)
    candidate_report = read_json(
        job / "blender" / "reports" / f"{spec['runtime_stem']}_candidate_prepare.json"
    )
    source_checkpoint = candidate_report["checkpoints"]["pre_export"]
    component_checkpoint = "blender/checkpoints/creature_components.blend"
    components = blender.segment_creature_components(
        slug,
        source_checkpoint,
        component_checkpoint,
        region_mode="loose",
        component_prefix=f"{spec['runtime_stem']}_component",
    )
    rig_checkpoint = "blender/checkpoints/creature_rig_approved.blend"
    rig = blender.author_creature_rig(
        slug,
        component_checkpoint,
        rig_checkpoint,
        creature_rig_family=str(spec["creature_rig_family"]),
        weight_mode="semantic",
        rig_name=f"{spec['runtime_stem']}_armature",
    )
    current_checkpoint = rig_checkpoint
    action_reports: Dict[str, Dict[str, Any]] = {}
    for action in spec["required_actions"]:
        role = str(action["role"])
        checkpoint = f"blender/checkpoints/{role}_pre_export.blend"
        action_name = f"{spec['runtime_stem']}_{role}"
        authored = blender.author_creature_action(
            slug,
            current_checkpoint,
            checkpoint,
            role,
            action_name,
            creature_rig_family=str(spec["creature_rig_family"]),
        )
        if authored.get("status") != "pass":
            raise RuntimeError(
                f"Creature action {role} failed the grounding gate: "
                f"{authored.get('status', 'unknown')}"
            )
        action_reports[role] = {
            "required_role": role,
            "action_name": authored["action"],
            "source_checkpoint": current_checkpoint,
            "checkpoint": checkpoint,
            "authoring": authored,
            "loop": bool(action.get("loop", role in {"idle", "move"})),
            "frame_policy": action.get("frame_policy", "blender_authored_semantic_skeletal"),
        }
        current_checkpoint = checkpoint

    prepare_pilot_texture_sources(job, spec)
    textures = finalize_pdx_runtime_textures(
        job,
        spec,
        blender.process_textures(slug, current_checkpoint),
    )
    mesh_rel = f"export/mesh/{spec['runtime_stem']}.mesh"
    mesh_export = blender.export_mesh(slug, current_checkpoint, mesh_rel)
    animation_exports: Dict[str, Dict[str, Any]] = {}
    reimports: Dict[str, Any] = {}
    for role, report in action_reports.items():
        anim_rel = f"export/anim/{spec['runtime_stem']}_{role}.anim"
        exported = blender.export_animation(
            slug,
            current_checkpoint,
            str(report["action_name"]),
            anim_rel,
        )
        animation_exports[role] = {"output_rel": anim_rel, "export": exported}
        report["output_rel"] = anim_rel
        report["export"] = exported
        reimports[role] = blender.reimport_export(
            slug,
            mesh_rel,
            anim_rel,
            proof_name=f"{spec['runtime_stem']}_{role}",
        )
    mesh_file = job / mesh_rel
    update_job(
        job,
        status="pdx_exported",
        exports={
            "mesh": mesh_rel,
            "animations": {role: report["output_rel"] for role, report in action_reports.items()},
        },
    )
    append_history(
        job,
        state="pdx_exported",
        event="creature_mesh_exported",
        actor="hoi4_3d_model_pipeline",
        details={
            "creature_rig_family": spec["creature_rig_family"],
            "components": components,
            "rig": rig,
            "mesh": file_record(mesh_file, relative_to=job),
            "reimport": reimports,
        },
    )
    return {
        "components": components,
        "rig": rig,
        "textures": textures,
        "mesh_export": mesh_export,
        "animation_exports": animation_exports,
        "action_reports": action_reports,
        "reimport": reimports,
    }


def record_local_rig_saving(job: Path, spec: Dict[str, Any]) -> None:
    """Record that the Blender rig and actions replaced the provider rig and its provider actions."""

    spec = prepare_spec(spec)
    roles = provider_animated_roles(spec)
    saved = int(spec["rig_estimate_credits"]) + int(spec["animation_estimate_credits"]) * len(roles)
    reason = f"Blender humanoid rig and {len(roles)} action(s) replace the provider rig and animations"
    if not any(row["outcome"] == "local_repair" and row["reason"] == reason for row in read_ledger(job)):
        record_local_repair(job, stage="local_humanoid_rig", operation="rig_and_animation", estimate=saved, reason=reason)


def continue_humanoid_local(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Finish a Meshy humanoid geometry package through the local rig route."""

    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    blender = BlenderAdapterClient(REPO_ROOT)
    generation_stage = generation_stage_for(spec)
    generation = existing_task(job, generation_stage)
    if not generation or generation.get("status") not in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
        raise RuntimeError("Local humanoid continuation requires a completed Meshy geometry task.")
    candidate_report = read_json(
        job / "blender" / "reports" / f"{spec['runtime_stem']}_candidate_prepare.json"
    )
    source_checkpoint = candidate_report["checkpoints"]["pre_export"]
    rig_checkpoint = "blender/checkpoints/humanoid_rig_approved.blend"
    rig = blender.author_humanoid_rig(
        slug,
        source_checkpoint,
        rig_checkpoint,
        rig_name=f"{spec['runtime_stem']}_armature",
    )
    if rig.get("status") != "pass":
        raise RuntimeError(f"Local humanoid rig failed: {rig.get('status', 'unknown')}")

    action_checkpoint = "blender/checkpoints/humanoid_actions_approved.blend"
    action_names = {
        role: f"{spec['runtime_stem']}_{role}"
        for role in ("idle", "move", "attack", "death")
    }
    actions = blender.author_humanoid_actions(
        slug,
        rig_checkpoint,
        action_checkpoint,
        action_names=action_names,
        fps=24,
    )
    if actions.get("status") != "pass":
        raise RuntimeError(f"Local humanoid actions failed: {actions.get('status', 'unknown')}")

    textures = finalize_pdx_runtime_textures(
        job,
        spec,
        blender.process_textures(slug, action_checkpoint),
    )
    mesh_rel = f"export/mesh/{spec['runtime_stem']}.mesh"
    mesh_export = blender.export_mesh(slug, action_checkpoint, mesh_rel)
    action_reports: Dict[str, Dict[str, Any]] = {}
    reimports: Dict[str, Any] = {}
    for role in ("idle", "move", "attack", "death"):
        anim_rel = f"export/anim/{spec['runtime_stem']}_{role}.anim"
        exported = blender.export_animation(
            slug,
            action_checkpoint,
            action_names[role],
            anim_rel,
        )
        action_reports[role] = {
            "required_role": role,
            "action_name": action_names[role],
            "source_checkpoint": action_checkpoint,
            "output_rel": anim_rel,
            "authoring": actions["actions"][role],
            "export": exported,
            "loop": role in {"idle", "move"},
            "frame_policy": "24fps_in_place_blender_authored_skeletal",
        }
        reimports[role] = blender.reimport_export(
            slug,
            mesh_rel,
            anim_rel,
            proof_name=f"{spec['runtime_stem']}_{role}",
        )

    mesh_file = job / mesh_rel
    record_local_rig_saving(job, spec)
    update_job(
        job,
        status="pdx_exported",
        humanoid_rig_route="blender_failure_recovery_humanoid_v1",
        provider_rig_task=None,
        exports={
            "mesh": mesh_rel,
            "animations": {role: report["output_rel"] for role, report in action_reports.items()},
        },
        runtime_source={
            "geometry_generation_stage": generation_stage,
            "geometry_generation_task_id": generation.get("task_id"),
            "geometry_source_policy": "Meshy generated geometry (the profile generation model)",
            "rig_source_policy": "repository-owned Blender humanoid recovery route after failed provider rig attempts",
            "distinct_geometry_package": True,
            "distinct_runtime_animations": True,
        },
    )
    append_history(
        job,
        state="pdx_exported",
        event="humanoid_local_recovery_exported",
        actor="hoi4_3d_model_pipeline",
        details={
            "generation_stage": generation_stage,
            "generation_task_id": generation.get("task_id"),
            "rig": rig,
            "actions": actions,
            "mesh": file_record(mesh_file, relative_to=job),
            "reimport": reimports,
        },
    )
    return {
        "generation_stage": generation_stage,
        "generation_task_id": generation.get("task_id"),
        "rig": rig,
        "actions": actions,
        "textures": textures,
        "mesh_export": mesh_export,
        "action_reports": action_reports,
        "reimport": reimports,
        "route": "blender_failure_recovery_humanoid_v1",
    }


def continue_humanoid(spec: Dict[str, Any]) -> Dict[str, Any]:
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    client = MeshyClient(REPO_ROOT, job)
    blender = BlenderAdapterClient(REPO_ROOT)
    vanilla_reference = stage_vanilla_reference(job, spec)
    generation_stage = generation_stage_for(spec)
    generation = existing_task(job, generation_stage)
    if not generation:
        raise RuntimeError("Humanoid generation must be completed before continuation.")
    generation_id = str(generation["task_id"])
    remesh_stage = continuation_stage_for(spec, "rig_remesh")
    rig_stage = rig_stage_for(spec)

    candidate_report = read_json(
        job / "blender" / "reports" / f"{spec['runtime_stem']}_candidate_prepare.json"
    )
    rig_input_id = generation_id
    rig_input_url: Optional[str] = None
    remesh_id: Optional[str] = None
    remesh_estimate = int(prepare_spec(spec)["remesh_estimate_credits"])
    source_triangles = int(candidate_report.get("imported_geometry", {}).get("triangles", 0))
    if source_triangles > 300000:
        remesh_id = provider_task(
            client,
            job,
            remesh_stage,
            task_type="remesh",
            estimate=remesh_estimate,
            input_stage=generation_stage,
            create=lambda: client.remesh(
                input_task_id=generation_id,
                target_polycount=spec["rig_source_target_polycount"],
                estimate_credits=remesh_estimate,
            ),
            request=paid_request(
                spec,
                "remesh",
                "meshy_remesh",
                remesh_arguments(generation_id, spec["rig_source_target_polycount"]),
            ),
        )
        remesh_glb = download_once(
            client,
            job,
            stage=continuation_stage_for(spec, "rig_remesh_glb"),
            task_id=remesh_id,
            task_type="remesh",
            format_name="glb",
            filename=continuation_download_name(spec, "remesh_model.glb"),
        )
        download_once(
            client,
            job,
            stage=continuation_stage_for(spec, "rig_remesh_fbx"),
            task_id=remesh_id,
            task_type="remesh",
            format_name="fbx",
            filename=continuation_download_name(spec, "remesh_model.fbx"),
        )
        rig_input_id = remesh_id

    # Rig and animation output keeps the UV layout of the model it was built
    # from: the remesh when there is one, else the generation model. Bind that
    # model's maps (fixes the generation maps being paired with remesh UVs).
    select_geometry_textures(
        job,
        spec,
        remesh_glb["file"]["relative_path"]
        if remesh_id
        else f"provider/downloads/{generation_download_name(spec, 'glb')}",
    )

    rig_input_mode = str(spec.get("rig_input_mode") or "input_task_id").casefold()
    if rig_input_mode not in {"input_task_id", "model_url"}:
        raise RuntimeError(f"Unsupported humanoid rig input mode: {rig_input_mode!r}.")
    if rig_input_mode == "model_url":
        source_stage = remesh_stage if remesh_id else generation_stage
        rig_input_url = task_model_url(job, source_stage, "glb")

    rig_id = provider_task(
        client,
        job,
        rig_stage,
        task_type="rigging",
        estimate=spec["rig_estimate_credits"],
        input_stage=remesh_stage if remesh_id else generation_stage,
        create=lambda: client.rig(
            input_task_id=rig_input_id if rig_input_url is None else None,
            model_url=rig_input_url,
            height_meters=spec["target_height_m"],
            estimate_credits=spec["rig_estimate_credits"],
        ),
        request=paid_request(
            spec,
            "rig",
            "meshy_rig",
            rig_arguments(
                rig_input_id if rig_input_url is None else None, rig_input_url, spec["target_height_m"]
            ),
        ),
    )
    rig_glb = download_once(
        client,
        job,
        stage=f"{rig_stage}_provider_glb",
        task_id=rig_id,
        task_type="rigging",
        format_name="glb",
        filename=rig_download_name(spec, "glb"),
        include_textures=False,
        allow_url_only=True,
        fetch_provider_url=True,
    )
    download_once(
        client,
        job,
        stage=f"{rig_stage}_provider_fbx",
        task_id=rig_id,
        task_type="rigging",
        format_name="fbx",
        filename=rig_download_name(spec, "fbx"),
        include_textures=False,
        allow_url_only=True,
        fetch_provider_url=True,
    )

    animation_downloads: Dict[str, Dict[str, Any]] = {}
    for action in spec["required_actions"]:
        role = action["role"]
        if action.get("task_type") == "blender_authored_skeletal":
            continue
        if action.get("provider_action_id") is None:
            raise RuntimeError(
                f"Required action {role} has no provider action id or Blender authoring route."
            )
        stage = animation_stage_for(spec, role)
        animation_id = provider_task(
            client,
            job,
            stage,
            task_type="animation",
            estimate=spec["animation_estimate_credits"],
            input_stage=rig_stage,
            create=lambda action_id=action["provider_action_id"]: client.animate(
                rig_task_id=rig_id,
                action_id=action_id,
                estimate_credits=spec["animation_estimate_credits"],
            ),
            request=paid_request(
                spec,
                "animation",
                "meshy_animate",
                animate_arguments(rig_id, action["provider_action_id"], None),
                role=role,
            ),
        )
        animation_downloads[role] = download_once(
            client,
            job,
            stage=f"{stage}_provider_glb",
            task_id=animation_id,
            task_type="animation",
            format_name="glb",
            filename=animation_download_name(spec, role, "glb"),
            include_textures=False,
            allow_url_only=True,
            fetch_provider_url=True,
        )
        download_once(
            client,
            job,
            stage=f"{stage}_provider_fbx",
            task_id=animation_id,
            task_type="animation",
            format_name="fbx",
            filename=animation_download_name(spec, role, "fbx"),
            include_textures=False,
            allow_url_only=True,
            fetch_provider_url=True,
        )

    profile = read_json(PIPELINE_ROOT / "config" / "asset_profiles.json")["profiles"][spec["profile"]]

    final_source = animation_downloads["attack"]["file"]["relative_path"]
    texture_sources = prepare_pilot_texture_sources(
        job,
        spec,
        exported_rels=[item["file"]["relative_path"] for item in animation_downloads.values()],
        geometry_source_rel=spec.get("geometry_source_rel"),
    )
    prep = blender.prepare_candidate(
        slug,
        source_rel=final_source,
        asset_kind="humanoid",
        target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
        runtime_stem=f"{spec['runtime_stem']}_attack",
        target_triangles=profile["triangle_range"]["working_triangle_target"],
        excluded_provider_objects=spec.get("excluded_provider_objects"),
        vanilla_reference=vanilla_reference,
        texture_source_rels=texture_sources,
        geometry_source_rel=spec.get("geometry_source_rel"),
        repair_before_reduction=True,
        topology_weld_distance=0.0,
    )
    candidate_gate(
        job,
        prep,
        hard_max=profile["triangle_range"]["hard_max"],
        stage="animated_candidate_attack",
    )
    textures = finalize_pdx_runtime_textures(
        job,
        spec,
        blender.process_textures(slug, prep["checkpoints"]["pre_export"]),
    )
    blender.save_checkpoint(
        slug,
        prep["checkpoints"]["pre_export"],
        "attack_pre_export",
    )
    attack_blend = "blender/checkpoints/attack_pre_export.blend"
    mesh_rel = f"export/mesh/{spec['runtime_stem']}.mesh"
    mesh_export = blender.export_mesh(slug, attack_blend, mesh_rel)
    action_reports: Dict[str, Dict[str, Any]] = {}
    attack_action_name = action_name_for_role(prep, "attack")
    attack_anim_rel = f"export/anim/{spec['runtime_stem']}_attack.anim"
    attack_anim_export = blender.export_animation(
        slug,
        attack_blend,
        attack_action_name,
        attack_anim_rel,
    )
    action_reports["attack"] = {
        "required_role": "attack",
        "action_name": attack_action_name,
        "source_checkpoint": attack_blend,
        "export": attack_anim_export,
        "output_rel": attack_anim_rel,
        "loop": False,
        "frame_policy": next(
            item.get("frame_policy", "provider_native_fps_in_place")
            for item in spec["required_actions"]
            if item["role"] == "attack"
        ),
    }
    attack_reimport = blender.reimport_export(
        slug,
        mesh_rel,
        attack_anim_rel,
        proof_name=f"{spec['runtime_stem']}_attack",
    )

    idle_source = animation_downloads["idle"]["file"]["relative_path"]
    idle_prep = blender.prepare_candidate(
        slug,
        source_rel=idle_source,
        asset_kind="humanoid",
        target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
        runtime_stem=f"{spec['runtime_stem']}_idle",
        target_triangles=profile["triangle_range"]["working_triangle_target"],
        excluded_provider_objects=spec.get("excluded_provider_objects"),
        vanilla_reference=vanilla_reference,
        texture_source_rels=texture_sources,
        geometry_source_rel=spec.get("geometry_source_rel"),
        repair_before_reduction=True,
        topology_weld_distance=0.0,
    )
    candidate_gate(
        job,
        idle_prep,
        hard_max=profile["triangle_range"]["hard_max"],
        stage="animated_candidate_idle",
    )
    blender.save_checkpoint(
        slug,
        idle_prep["checkpoints"]["pre_export"],
        "idle_pre_export",
    )
    idle_blend = "blender/checkpoints/idle_pre_export.blend"
    idle_action_name = action_name_for_role(idle_prep, "idle")
    idle_anim_rel = f"export/anim/{spec['runtime_stem']}_idle.anim"
    idle_anim_export = blender.export_animation(
        slug,
        idle_blend,
        idle_action_name,
        idle_anim_rel,
    )
    action_reports["idle"] = {
        "required_role": "idle",
        "action_name": idle_action_name,
        "source_checkpoint": idle_blend,
        "export": idle_anim_export,
        "output_rel": idle_anim_rel,
        "loop": True,
        "frame_policy": next(
            item.get("frame_policy", "provider_native_fps_in_place")
        for item in spec["required_actions"]
            if item["role"] == "idle"
        ),
    }
    idle_reimport = blender.reimport_export(
        slug,
        mesh_rel,
        idle_anim_rel,
        proof_name=f"{spec['runtime_stem']}_idle",
    )
    move_action_name = "Armature|Move|baselayer_WORKING"
    move_blend = "blender/checkpoints/move_pre_export.blend"
    move_authoring = blender.author_locomotion_action(
        slug,
        idle_blend,
        move_blend,
        move_action_name,
    )
    move_anim_rel = f"export/anim/{spec['runtime_stem']}_move.anim"
    move_anim_export = blender.export_animation(
        slug,
        move_blend,
        move_action_name,
        move_anim_rel,
    )
    move_reimport = blender.reimport_export(
        slug,
        mesh_rel,
        move_anim_rel,
        proof_name=f"{spec['runtime_stem']}_move",
    )
    action_reports["move"] = {
        "required_role": "move",
        "action_name": move_action_name,
        "source_checkpoint": move_blend,
        "authoring": move_authoring,
        "export": move_anim_export,
        "output_rel": move_anim_rel,
        "loop": True,
        "frame_policy": next(
            item.get("frame_policy", "24fps_in_place_blender_authored")
            for item in spec["required_actions"]
            if item["role"] == "move"
        ),
    }
    required_roles = {item["role"] for item in spec["required_actions"]}

    if "death" in required_roles:
        death_source = animation_downloads.get("death", {}).get("file", {}).get("relative_path")
        if not death_source:
            raise RuntimeError("Required death animation was not downloaded from the provider.")
        death_prep = blender.prepare_candidate(
            slug,
            source_rel=death_source,
            asset_kind="humanoid",
            target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
            runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
            runtime_stem=f"{spec['runtime_stem']}_death",
            target_triangles=profile["triangle_range"]["working_triangle_target"],
            excluded_provider_objects=spec.get("excluded_provider_objects"),
            vanilla_reference=vanilla_reference,
            texture_source_rels=texture_sources,
            geometry_source_rel=spec.get("geometry_source_rel"),
            repair_before_reduction=True,
            topology_weld_distance=0.0,
        )
        candidate_gate(
            job,
            death_prep,
            hard_max=profile["triangle_range"]["hard_max"],
            stage="animated_candidate_death",
        )
        blender.save_checkpoint(
            slug,
            death_prep["checkpoints"]["pre_export"],
            "death_pre_export",
        )
        death_blend = "blender/checkpoints/death_pre_export.blend"
        death_action_name = action_name_for_role(death_prep, "death")
        death_anim_rel = f"export/anim/{spec['runtime_stem']}_death.anim"
        death_anim_export = blender.export_animation(
            slug,
            death_blend,
            death_action_name,
            death_anim_rel,
        )
        action_reports["death"] = {
            "required_role": "death",
            "action_name": death_action_name,
            "source_checkpoint": death_blend,
            "export": death_anim_export,
            "output_rel": death_anim_rel,
            "loop": False,
            "frame_policy": next(
                item.get("frame_policy", "provider_native_fps_in_place")
                for item in spec["required_actions"]
                if item["role"] == "death"
            ),
        }
        death_reimport = blender.reimport_export(
            slug,
            mesh_rel,
            death_anim_rel,
            proof_name=f"{spec['runtime_stem']}_death",
        )
    else:
        death_reimport = None

    missing_roles = required_roles.difference(action_reports)
    if missing_roles:
        raise RuntimeError(
            "Required skeletal actions were not produced: "
            + ", ".join(sorted(missing_roles))
        )
    mesh_file = job / mesh_rel
    update_job(
        job,
        status="pdx_exported",
        exports={
            "mesh": mesh_rel,
            "animations": {
                role: exported_animation_path(report)
                for role, report in action_reports.items()
            },
        },
    )
    append_history(
        job,
        state="pdx_exported",
        event="humanoid_mesh_exported",
        actor="hoi4_3d_model_pipeline",
        details={
            "rig_task_id": rig_id,
            "animation_downloads": animation_downloads,
            "mesh": file_record(mesh_file, relative_to=job),
            "reimport": {
                "attack": attack_reimport,
                "idle": idle_reimport,
                "move": move_reimport,
                "death": death_reimport,
            },
        },
    )
    return {
        "rig_task_id": rig_id,
        "animation_downloads": animation_downloads,
        "prepare": {"attack": prep, "idle": idle_prep},
        "textures": textures,
        "mesh_export": mesh_export,
        "action_reports": action_reports,
        "reimport": {
            "attack": attack_reimport,
            "idle": idle_reimport,
            "move": move_reimport,
            "death": death_reimport,
        },
    }


def _copy_shared_provider_artifact(source: Path, destination: Path) -> Dict[str, Any]:
    """Copy one immutable provider artifact while refusing lineage drift."""

    if not source.is_file():
        raise FileNotFoundError(f"Shared provider artifact is missing: {source}")
    source_record = file_record(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination_record = file_record(destination)
        if destination_record["sha256"] != source_record["sha256"]:
            raise RuntimeError(
                "Refusing to overwrite a shared provider artifact with a different checksum: "
                f"{destination}"
            )
    else:
        shutil.copy2(source, destination)
    return file_record(destination)


def prepare_shared_humanoid_lineage(
    owner_spec: Dict[str, Any],
    recipient_specs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Distribute one verified humanoid rig/action set to distinct geometries.

    Meshy is used once for the standard humanoid rig and its three provider
    actions. Each recipient still receives its own generated geometry, its own
    weighted mesh, its own exported four-action package, and its own reimport
    proofs. Sharing the standard skeleton/action source is an explicit HOI4
    unit-family optimization, not a static or unanimated fallback.
    """

    owner_slug = owner_spec["asset_id"].rsplit(".", 1)[-1]
    owner_job = ensure_job_layout(resolve_job_root(owner_slug))
    artifact_names = {
        "rig_glb": f"provider/downloads/{rig_download_name(owner_spec, 'glb')}",
        "rig_fbx": f"provider/downloads/{rig_download_name(owner_spec, 'fbx')}",
        "idle_glb": f"provider/downloads/{animation_download_name(owner_spec, 'idle', 'glb')}",
        "idle_fbx": f"provider/downloads/{animation_download_name(owner_spec, 'idle', 'fbx')}",
        "attack_glb": f"provider/downloads/{animation_download_name(owner_spec, 'attack', 'glb')}",
        "attack_fbx": f"provider/downloads/{animation_download_name(owner_spec, 'attack', 'fbx')}",
        "death_glb": f"provider/downloads/{animation_download_name(owner_spec, 'death', 'glb')}",
        "death_fbx": f"provider/downloads/{animation_download_name(owner_spec, 'death', 'fbx')}",
    }
    owner_artifacts = {
        key: file_record(owner_job / relative_path, relative_to=owner_job)
        for key, relative_path in artifact_names.items()
    }
    task_lineage = {
        "owner": owner_slug,
        "rig_task": existing_task(owner_job, rig_stage_for(owner_spec)),
        "animation_tasks": {
            role: existing_task(
                owner_job,
                animation_stage_for(owner_spec, role),
            )
            for role in ("idle", "attack", "death")
        },
    }
    for key, record in owner_artifacts.items():
        if not (owner_job / record["relative_path"]).is_file():
            raise FileNotFoundError(
                f"Shared humanoid source {key} is missing from owner job: "
                f"{owner_job / record['relative_path']}"
            )

    recipients: Dict[str, Any] = {}
    for recipient_spec in recipient_specs:
        recipient_slug = recipient_spec["asset_id"].rsplit(".", 1)[-1]
        recipient_job = ensure_job_layout(resolve_job_root(recipient_slug))
        destination_root = recipient_job / "provider" / "shared_humanoid"
        copied: Dict[str, Any] = {}
        for key, relative_path in artifact_names.items():
            source = owner_job / relative_path
            destination = destination_root / Path(relative_path).name
            copied[key] = _copy_shared_provider_artifact(source, destination)
            copied[key]["relative_path"] = str(destination.relative_to(recipient_job)).replace("\\", "/")
        lineage = {
            "schema_version": "1.0.0",
            "policy": "shared_standard_humanoid_rig_and_provider_actions_bound_to_distinct_recipient_geometry",
            "owner_job": str(owner_job),
            "owner_slug": owner_slug,
            "owner_task_lineage": task_lineage,
            "owner_artifacts": owner_artifacts,
            "recipient_slug": recipient_slug,
            "copied_artifacts": copied,
            "paid_calls_for_recipient": 0,
            "forbidden_substitutes": ["static_mesh_only", "missing_actions", "reused_geometry"],
            "recorded_at": utc_now(),
        }
        write_json(recipient_job / "provider" / "shared_humanoid_lineage.json", lineage)
        update_job(
            recipient_job,
            shared_humanoid_lineage=lineage,
            provider_lineage={
                "rig_owner": owner_slug,
                "rig_task_id": task_lineage["rig_task"].get("task_id")
                if isinstance(task_lineage["rig_task"], dict)
                else None,
                "animation_task_ids": {
                    role: record.get("task_id") if isinstance(record, dict) else None
                    for role, record in task_lineage["animation_tasks"].items()
                },
            },
        )
        append_history(
            recipient_job,
            state="shared_humanoid_lineage_ready",
            event="shared_humanoid_provider_sources_copied",
            actor="hoi4_3d_model_pipeline",
            details={"owner": owner_slug, "artifacts": copied},
        )
        recipients[recipient_slug] = lineage
    return {"owner": owner_slug, "recipients": recipients, "owner_artifacts": owner_artifacts}


def rebuild_runtime_textures(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Rebuild a finished humanoid job's three runtime DDS from files already on disk.

    Repairs jobs exported before the texture lineage gate existed, whose maps came
    from the generation model while the exported mesh used the remesh UV layout.
    Makes no Meshy call and starts no Blender: the DDS are derived from the
    provider maps (graded diffuse, packed specular and normal) at the sizes the
    earlier export recorded in `blender/reports/textures_dds.json`. The mesh and
    animations do not embed textures, so they stay as they are.
    """

    prepare_spec(spec, require_budget=False)
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    if spec["asset_kind"] != "humanoid":
        raise RuntimeError("Runtime texture rebuild covers the humanoid continuation route only.")
    report = job / "blender" / "reports" / "textures_dds.json"
    if not report.is_file():
        raise FileNotFoundError(f"No earlier texture export to rebuild (missing {report}).")
    remesh = existing_task(job, continuation_stage_for(spec, "rig_remesh"))
    model_name = (
        continuation_download_name(spec, "remesh_model.glb")
        if remesh and remesh.get("status") in SUCCEEDED_STATUSES
        else generation_download_name(spec, "glb")
    )
    select_geometry_textures(job, spec, f"provider/downloads/{model_name}")
    exported = f"provider/downloads/{animation_download_name(spec, 'attack', 'glb')}"
    prepare_pilot_texture_sources(
        job,
        spec,
        exported_rels=[exported],
        geometry_source_rel=spec.get("geometry_source_rel"),
    )
    return finalize_pdx_runtime_textures(job, spec, read_json(report))


def continue_humanoid_shared(
    spec: Dict[str, Any],
    lineage: Dict[str, Any],
) -> Dict[str, Any]:
    """Build a distinct humanoid package from a shared verified rig/action source."""

    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    blender = BlenderAdapterClient(REPO_ROOT)
    shared_rig_rel = "provider/shared_humanoid/rigged_provider_model.glb"
    generation_rel = f"provider/downloads/{generation_download_name(spec, 'glb')}"
    if not (job / shared_rig_rel).is_file():
        raise FileNotFoundError(f"Shared humanoid rig source is missing: {job / shared_rig_rel}")
    if not (job / generation_rel).is_file():
        raise FileNotFoundError(f"Recipient generation geometry is missing: {job / generation_rel}")
    vanilla_reference = stage_vanilla_reference(job, spec)
    profile = read_json(PIPELINE_ROOT / "config" / "asset_profiles.json")["profiles"][spec["profile"]]
    texture_sources = prepare_pilot_texture_sources(
        job, spec, exported_rels=[shared_rig_rel], geometry_source_rel=generation_rel
    )
    prep = blender.prepare_candidate(
        slug,
        source_rel=shared_rig_rel,
        geometry_source_rel=generation_rel,
        asset_kind="humanoid",
        target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
        runtime_stem=f"{spec['runtime_stem']}_shared_rigged",
        target_triangles=profile["triangle_range"]["working_triangle_target"],
        excluded_provider_objects=spec.get("excluded_provider_objects"),
        vanilla_reference=vanilla_reference,
        texture_source_rels=texture_sources,
        repair_before_reduction=True,
        topology_weld_distance=0.0,
        max_runtime_footprint_m=spec.get("max_runtime_footprint_m"),
        runtime_footprint_policy=spec.get("runtime_footprint_policy", "reject"),
    )
    candidate_gate(
        job,
        prep,
        hard_max=profile["triangle_range"]["hard_max"],
        stage="shared_humanoid_candidate",
        max_runtime_footprint_m=spec.get("max_runtime_footprint_m"),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
    )

    action_reports: Dict[str, Dict[str, Any]] = {}
    verified_actions = spec.get("verified_actions")
    target_armature_name = str(spec.get("target_armature_name") or "")
    if not isinstance(verified_actions, dict) or not target_armature_name:
        raise RuntimeError(
            "Humanoid continuation requires verified_actions receipts and an explicit target_armature_name."
        )

    def import_verified_action(
        role: str,
        source_checkpoint: str,
        checkpoint: str,
        target_action_name: str,
    ) -> Dict[str, Any]:
        receipt = verified_actions.get(role)
        if not isinstance(receipt, dict):
            raise RuntimeError(f"Missing verified animation-source receipt for role: {role}")
        required = (
            "source_rel",
            "provenance_rel",
            "source_action_name",
            "source_kind",
            "source_reference_id",
            "source_sha256",
        )
        missing = [key for key in required if not str(receipt.get(key) or "")]
        if missing:
            raise RuntimeError(
                f"Verified animation-source receipt for {role} is missing fields: {missing}"
            )
        return blender.import_animation_action(
            slug,
            source_checkpoint,
            str(receipt["source_rel"]),
            str(receipt["provenance_rel"]),
            checkpoint,
            str(receipt["source_action_name"]),
            target_armature_name,
            target_action_name,
            str(receipt["source_kind"]),
            str(receipt["source_reference_id"]),
            str(receipt["source_sha256"]),
            source_armature_name=str(receipt.get("source_armature_name") or ""),
        )

    idle_checkpoint = "blender/checkpoints/shared_idle_pre_export.blend"
    idle_action_name = f"{spec['runtime_stem']}_idle"
    idle = import_verified_action(
        "idle",
        prep["checkpoints"]["pre_export"],
        idle_checkpoint,
        idle_action_name,
    )
    action_reports["idle"] = {
        "required_role": "idle",
        "action_name": idle["action"],
        "source_checkpoint": prep["checkpoints"]["pre_export"],
        "checkpoint": idle_checkpoint,
        "import": idle,
        "loop": True,
    }

    move_checkpoint = "blender/checkpoints/shared_move_pre_export.blend"
    move_action_name = f"{spec['runtime_stem']}_move"
    move = import_verified_action(
        "move",
        idle_checkpoint,
        move_checkpoint,
        move_action_name,
    )
    action_reports["move"] = {
        "required_role": "move",
        "action_name": move["action"],
        "source_checkpoint": idle_checkpoint,
        "checkpoint": move_checkpoint,
        "import": move,
        "loop": True,
    }

    attack_checkpoint = "blender/checkpoints/shared_attack_pre_export.blend"
    attack_action_name = f"{spec['runtime_stem']}_attack"
    attack = import_verified_action(
        "attack",
        move_checkpoint,
        attack_checkpoint,
        attack_action_name,
    )
    action_reports["attack"] = {
        "required_role": "attack",
        "action_name": attack["action"],
        "source_checkpoint": move_checkpoint,
        "checkpoint": attack_checkpoint,
        "import": attack,
        "loop": False,
    }

    death_checkpoint = "blender/checkpoints/shared_death_pre_export.blend"
    death_action_name = f"{spec['runtime_stem']}_death"
    death = import_verified_action(
        "death",
        attack_checkpoint,
        death_checkpoint,
        death_action_name,
    )
    action_reports["death"] = {
        "required_role": "death",
        "action_name": death["action"],
        "source_checkpoint": attack_checkpoint,
        "checkpoint": death_checkpoint,
        "import": death,
        "loop": False,
    }

    textures = finalize_pdx_runtime_textures(
        job,
        spec,
        blender.process_textures(slug, death_checkpoint),
    )
    mesh_rel = f"export/mesh/{spec['runtime_stem']}.mesh"
    mesh_export = blender.export_mesh(slug, death_checkpoint, mesh_rel)
    reimports: Dict[str, Any] = {}
    for role, report in action_reports.items():
        anim_rel = f"export/anim/{spec['runtime_stem']}_{role}.anim"
        report["output_rel"] = anim_rel
        report["export"] = blender.export_animation(
            slug,
            str(report["checkpoint"]),
            str(report["action_name"]),
            anim_rel,
        )
        reimports[role] = blender.reimport_export(
            slug,
            mesh_rel,
            anim_rel,
            proof_name=f"{spec['runtime_stem']}_{role}",
        )

    mesh_file = job / mesh_rel
    update_job(
        job,
        status="pdx_exported",
        exports={
            "mesh": mesh_rel,
            "animations": {role: report["output_rel"] for role, report in action_reports.items()},
        },
        shared_humanoid_runtime={
            "lineage_owner": lineage.get("owner_slug"),
            "recipient_geometry": generation_rel,
            "distinct_runtime_mesh": mesh_rel,
            "distinct_runtime_animations": True,
        },
    )
    append_history(
        job,
        state="pdx_exported",
        event="shared_humanoid_mesh_exported",
        actor="hoi4_3d_model_pipeline",
        details={
            "lineage_owner": lineage.get("owner_slug"),
            "mesh": file_record(mesh_file, relative_to=job),
            "actions": action_reports,
            "reimport": reimports,
        },
    )
    return {
        "lineage_owner": lineage.get("owner_slug"),
        "prepare": prep,
        "textures": textures,
        "mesh_export": mesh_export,
        "action_reports": action_reports,
        "reimport": reimports,
    }


def _shared_humanoid_spec(slug: str, job_root: Path, job: Dict[str, Any]) -> Dict[str, Any]:
    """Build a pilot spec from a repository-owned shared humanoid job manifest.

    The spec still needs prepare_spec, which adds the profile's generation settings, the
    price-table estimates and the job's credit_budget.
    """

    asset_profiles = read_json(PIPELINE_ROOT / "config" / "asset_profiles.json")["profiles"]
    job_profile_name = str(job.get("profile") or "humanoid_unit")
    is_creature = job_profile_name.startswith("nonhumanoid")
    profile_name = (
        "nonhumanoid_winged_biped"
        if job_profile_name in {"nonhumanoid_winged_creature", "nonhumanoid_winged_biped"}
        else "nonhumanoid_creature"
        if is_creature
        else "humanoid_unit"
    )
    profile = asset_profiles[profile_name]
    manifest_path = job_root / "refs" / "original" / "input_manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {}
    brief_path = job_root / "refs" / "briefs" / "meshy_input_prompt.md"
    brief = brief_path.read_text(encoding="utf-8") if brief_path.exists() else str(job.get("brief", ""))
    provider_plan = job.get("provider_plan", {})
    blender_plan = job.get("blender_plan", {})
    vanilla_plan = blender_plan.get("vanilla_scale_reference", {})
    vanilla_root = Path("C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")
    raw_vanilla_mesh = vanilla_plan.get("mesh") or profile["vanilla_reference"]["mesh"]
    vanilla_mesh = Path(str(raw_vanilla_mesh))
    if not vanilla_mesh.is_absolute():
        vanilla_mesh = vanilla_root / vanilla_mesh
    raw_vanilla_height = (
        job.get("vanilla_height")
        or blender_plan.get("target_height_m")
        or profile["vanilla_reference"]["mesh_height"]
    )
    raw_entity_scale = (
        job.get("entity_scale")
        or blender_plan.get("runtime_entity_scale")
        or profile["vanilla_reference"]["entity_scale"]
    )
    reference_path = str(
        job.get("reference")
        or job.get("meshy_input_gate", {}).get("image")
        or "refs/original/meshy_input.png"
    )
    try:
        vanilla_height = float(raw_vanilla_height)
        entity_scale = float(raw_entity_scale)
    except (TypeError, ValueError):
        if not is_creature:
            raise ValueError(
                f"{slug} has a non-numeric humanoid scale crosswalk: "
                f"vanilla_height={raw_vanilla_height!r}, entity_scale={raw_entity_scale!r}"
            )
        return {
            "asset_id": f"hoi4.model.job.{slug}",
            "asset_kind": "creature",
            "profile": profile_name,
            "reference_path": reference_path,
            "reference_generator_output": None,
            "reference_source_mode": manifest.get("source_mode", "native_imagegen_portrait_reference"),
            "asset_brief": brief,
            "runtime_stem": str(
                job.get("runtime_stem")
                or blender_plan.get("runtime_stem")
                or f"hoi4_{slug}"
            ),
            "proposed_runtime_identifiers": {
                "entity": str(
                    job.get("entity")
                    or job.get("runtime", {}).get("proposed_identifiers", {}).get("entity")
                    or f"hoi4_{slug}_entity"
                ),
                "consumer": "land-unit entity",
                "route": "custom creature rig",
            },
            "scale_crosswalk": job.get("scale_crosswalk"),
            "_requires_reference_approval": True,
            "_route_status": "pending_creature_scale_crosswalk",
            "_route_blocker": (
                "The job manifest intentionally has no numeric creature scale crosswalk. "
                "Measure the approved creature against the installed infantry runtime reference "
                "before enabling paid generation or export."
            ),
            "_job_root": str(job_root),
        }
    runtime_stem = str(job.get("runtime_stem") or blender_plan.get("runtime_stem") or f"hoi4_{slug}")
    entity = str(
        job.get("entity")
        or job.get("runtime", {}).get("proposed_identifiers", {}).get("entity")
        or f"{runtime_stem}_entity"
    )
    target_triangles = int(
        job.get("target_triangles")
        or provider_plan.get("target_polycount")
        or profile["triangle_range"]["working_triangle_target"]
    )
    rig_source_target_polycount = int(
        job.get("rig_source_target_polycount")
        or provider_plan.get("rig_source_target_polycount")
        or target_triangles
    )
    vanilla_reference = {
        "mesh": str(vanilla_mesh),
        "entity": profile["vanilla_reference"]["entity"],
        "mesh_object_names": profile["vanilla_reference"]["mesh_object_names"],
        "exclude_name_patterns": profile["vanilla_reference"]["exclude_name_patterns"],
        "forward_axis": profile["vanilla_reference"]["forward_axis"],
        "up_axis": profile["vanilla_reference"]["up_axis"],
        "mesh_height": vanilla_height,
        "entity_scale": entity_scale,
        "runtime_height": vanilla_height * entity_scale,
    }
    creature_rig_family = (
        str(
            job.get("creature_rig_family")
            or ("winged_biped" if job_profile_name in {"nonhumanoid_winged_creature", "nonhumanoid_winged_biped"} else "quadruped")
        )
        if is_creature
        else "humanoid"
    )
    if is_creature and creature_rig_family != "winged_biped":
        route_status = "pending_creature_rig_route"
        route_blocker = (
            f"The selected creature rig family {creature_rig_family!r} has no enabled generic pilot route."
        )
    else:
        route_status = "ready"
        route_blocker = None
    required_components = (
        [
            "complete portrait-matched nonhumanoid body",
            "attached wings and stable digitigrade silhouette",
            "custom creature rig with rigid semantic components",
        ]
        if is_creature
        else [
            "complete portrait-matched humanoid body",
            "distinctive shared humanoid silhouette",
            "grounded riggable infantry proportions",
        ]
    )
    required_actions = (
        [
            {"role": role, "provider_action_id": None, "task_type": "blender_authored_skeletal", "fps": int(job.get("fps", 30)), "loop": role in {"idle", "move"}, "root_policy": "in_place"}
            for role in ("idle", "move", "attack", "death")
        ]
        if is_creature
        else [
            {"role": "idle", "provider_action_id": 0, "fps": 24, "loop": True, "root_policy": "in_place"},
            {"role": "move", "provider_action_id": None, "task_type": "blender_authored_skeletal", "fps": 24, "loop": True, "root_policy": "in_place"},
            {"role": "attack", "provider_action_id": 4, "fps": 24, "loop": False, "root_policy": "in_place"},
            {"role": "death", "provider_action_id": 8, "fps": 24, "loop": False, "root_policy": "in_place"},
        ]
    )
    generation_stage = str(job.get("generation_stage") or "generation")
    return {
        "asset_id": f"hoi4.model.job.{slug}",
        "asset_kind": "creature" if is_creature else "humanoid",
        "profile": profile_name,
        "reference_path": reference_path,
        "reference_generator_output": None,
        "reference_source_mode": manifest.get("source_mode", "native_imagegen_portrait_reference"),
        "asset_brief": brief,
        "required_components": required_components,
        "forbidden_additions": [
            "weapons",
            "extra characters",
            "floating disconnected geometry",
            "multi-view board",
            "turnaround collage",
            "text or watermark",
        ],
        "excluded_provider_objects": list(
            job.get("excluded_provider_objects")
            or (["Icosphere"] if not is_creature else [])
        ),
        "target_height_m": vanilla_height,
        "blender_target_height_m": vanilla_height,
        "blender_effective_runtime_height_m": vanilla_height * entity_scale,
        "runtime_entity_scale": entity_scale,
        "runtime_diffuse_gamma": profile.get("runtime_diffuse_gamma"),
        "vanilla_scale_reference": vanilla_reference,
        "target_polycount": target_triangles,
        "rig_source_target_polycount": rig_source_target_polycount,
        # A job may restate the model it expects; prepare_spec refuses any other than the profile's.
        "meshy_ai_model": job.get("provider_model") or provider_plan.get("ai_model"),
        "resolved_meshy_ai_model": job.get("resolved_provider_model") or provider_plan.get("resolved_ai_model"),
        "meshy_pose_mode": provider_plan.get("pose_mode"),
        "credit_budget": job.get("credit_budget"),
        "generation_stage": generation_stage,
        "rig_stage": job.get("rig_stage"),
        "rig_input_mode": str(job.get("rig_input_mode") or "input_task_id"),
        "humanoid_rig_route": str(job.get("humanoid_rig_route") or ""),
        "provider_paid_attempts": int(provider_plan.get("paid_attempts") or 1),
        "provider_retry_paid_calls": bool(provider_plan.get("retry_paid_calls", False)),
        "texture_source_rels": {
            "diffuse": f"provider/downloads/{generation_stage}_model_textures/base_color.png",
            "normal": f"provider/downloads/{generation_stage}_model_textures/normal.png",
            "specular": f"provider/downloads/{generation_stage}_model_textures/metallic_roughness.png",
        },
        "required_actions": required_actions,
        "creature_rig_family": creature_rig_family,
        "scale_crosswalk": job.get(
            "scale_crosswalk",
            "overall_creature_height_matches_western_european_infantry_runtime"
            if is_creature
            else None,
        ),
        "runtime_stem": runtime_stem,
        "shared_humanoid_batch": job.get("shared_humanoid_batch"),
        "shared_humanoid_rig_owner": job.get("shared_humanoid_rig_owner"),
        "shared_humanoid_role": job.get("shared_humanoid_role"),
        "proposed_runtime_identifiers": {
            "pdxmesh": f"{runtime_stem}_mesh",
            "entity": entity,
            "consumer": "land-unit entity",
            "entity_scale": entity_scale,
        },
        "_requires_reference_approval": True,
        "_route_status": route_status,
        "_route_blocker": route_blocker,
        "_job_root": str(job_root),
    }


def load_job_configs(config_path: Path) -> Dict[str, Dict[str, Any]]:
    """Load an explicitly supplied repository-owned job registry."""

    resolved = config_path.resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError("--jobs-config must remain inside the repository.") from exc
    payload = read_json(resolved)
    jobs = payload.get("jobs", payload.get("pilots"))
    if not isinstance(jobs, dict) or not jobs:
        raise ValueError("--jobs-config must contain a non-empty jobs mapping.")
    return jobs


def require_reference_approval(spec: Dict[str, Any]) -> None:
    """Block paid generation until the parent has accepted the exact provider image."""

    if not spec.get("_requires_reference_approval"):
        return
    job_root = resolve_job_root(spec["asset_id"].rsplit(".", 1)[-1])
    manifest_path = job_root / "refs" / "original" / "input_manifest.json"
    manifest = read_json(manifest_path)
    status = str(manifest.get("candidate_status", "needs_user_visual_approval"))
    if status not in {"user_accepted", "accepted", "approved"}:
        raise RuntimeError(
            f"{job_root.name} reference status is {status!r}; paid generation requires explicit user visual approval."
        )


def require_route_ready(spec: Dict[str, Any]) -> None:
    """Refuse a job whose asset class has not completed its calibrated route design."""

    status = str(spec.get("_route_status", "ready"))
    if status == "ready":
        return
    blocker = str(spec.get("_route_blocker") or "The selected asset route is not ready.")
    raise RuntimeError(
        f"{spec['asset_id']} is blocked before provider work: route_status={status}; {blocker}"
    )


def pending_stages(spec: Dict[str, Any], phase: str = "full") -> List[Dict[str, Any]]:
    """Planned paid stages that have not succeeded yet; a candidate phase plans only the generation."""

    job = ensure_job_layout(resolve_job_root(spec["asset_id"].rsplit(".", 1)[-1]))
    stages = planned_stages(spec)[: 1 if phase == "candidate" else None]
    return [{**item, "job": job.name} for item in stages if not stage_succeeded(job, item["stage"])]


def require_budget_headroom(pending: List[Dict[str, Any]], specs: List[Dict[str, Any]]) -> None:
    """Stop before the first paid call when a job's remaining budget cannot cover its pending stages."""

    for spec in specs:
        job = ensure_job_layout(resolve_job_root(spec["asset_id"].rsplit(".", 1)[-1]))
        needed = sum(int(item["estimate_credits"]) for item in pending if item["job"] == job.name)
        state = budget_state(ledger_entries(job), spec["credit_budget"])
        if needed > state["remaining"]:
            shortfall = needed - state["remaining"]
            raise RuntimeError(
                f"Credit budget stop before any paid call: {job.name} still plans {needed} credits but only "
                f"{state['remaining']} of its {state['credit_budget']}-credit budget remain "
                f"({state['consumed']} consumed, {state['reserved']} reserved). Short by {shortfall}. "
                f"Ask the user once to raise credit_budget to at least {state['credit_budget'] + shortfall}."
            )


def vet_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Refuse a job before any provider call: route blockers, reference approval, then settings and budget."""

    require_route_ready(spec)
    require_reference_approval(spec)
    return prepare_spec(spec)


def preflight_selected_credits(specs: List[Dict[str, Any]], phase: str) -> None:
    """Check the full selected tranche before any paid provider call."""

    if not specs:
        return
    require_budget_headroom([item for spec in specs for item in pending_stages(spec, phase)], specs)
    estimates = []
    for spec in specs:
        if not spec.get("_requires_reference_approval"):
            continue
        estimate = (
            int(spec["image_to_3d_estimate_credits"])
            if phase == "candidate"
            else int(spec["planned_total_credits"])
        )
        estimates.append((spec["asset_id"], estimate))
    total = sum(value for _, value in estimates)
    if total == 0:
        return
    result = MeshyClient(REPO_ROOT).check_balance()
    balance = balance_value(result)
    if balance is None:
        raise RuntimeError("Meshy balance preflight returned no numeric balance.")
    if balance < total:
        breakdown = ", ".join(f"{asset}={estimate}" for asset, estimate in estimates)
        raise RuntimeError(
            f"Meshy batch gate refused paid work: balance={balance}, required={total}; {breakdown}"
        )


def uses_local_humanoid_route(spec: Dict[str, Any]) -> bool:
    """Return whether a job explicitly selected the failure-driven local rig route."""

    return (
        spec.get("asset_kind") == "humanoid"
        and str(spec.get("humanoid_rig_route") or "").casefold()
        == "blender_failure_recovery_humanoid_v1"
    )


def run_shared_humanoid_batch(
    batch_id: str,
    configs: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Produce a configured specialized-unit batch with explicit per-job rig routes.

    The batch always keeps one distinct Meshy geometry task per unit. Jobs
    that explicitly select the local failure-recovery route receive their own
    locally authored rig and four skeletal actions. Provider-rig jobs retain the
    shared-humanoid lineage route. Creature jobs stay on their custom Blender
    route.
    """

    selected = [
        (slug, spec)
        for slug, spec in configs.items()
        if spec.get("shared_humanoid_batch") == batch_id
    ]
    if not selected:
        raise RuntimeError(f"No configured specialized 3D jobs belong to batch {batch_id!r}.")
    selected.sort(key=lambda item: item[0])
    for _, spec in selected:
        vet_spec(spec)

    owner_slugs = {
        str(spec.get("shared_humanoid_rig_owner") or "")
        for _, spec in selected
        if spec.get("asset_kind") == "humanoid"
    }
    owner_slugs.discard("")
    if len(owner_slugs) != 1:
        raise RuntimeError(
            f"Shared humanoid batch {batch_id!r} must declare exactly one rig owner; "
            f"found {sorted(owner_slugs)}."
        )
    owner_slug = next(iter(owner_slugs))
    specs_by_slug = dict(selected)
    owner_spec = specs_by_slug.get(owner_slug)
    if owner_spec is None or owner_spec.get("asset_kind") != "humanoid":
        raise RuntimeError(f"Shared humanoid rig owner {owner_slug!r} is not a selected humanoid job.")
    recipient_specs = [
        spec
        for slug, spec in selected
        if slug != owner_slug and spec.get("asset_kind") == "humanoid"
    ]
    creature_specs = [spec for _, spec in selected if spec.get("asset_kind") == "creature"]
    humanoid_specs = [owner_spec] + recipient_specs
    local_humanoid_batch = bool(humanoid_specs) and all(
        uses_local_humanoid_route(spec) for spec in humanoid_specs
    )

    for _, spec in selected:
        initialize_job(spec)

    def current_status(spec: Dict[str, Any]) -> str:
        slug = spec["asset_id"].rsplit(".", 1)[-1]
        return str(read_job(ensure_job_layout(resolve_job_root(slug))).get("status", "preflight"))

    def saved_candidate_ready(spec: Dict[str, Any]) -> bool:
        slug = spec["asset_id"].rsplit(".", 1)[-1]
        job = ensure_job_layout(resolve_job_root(slug))
        task = existing_task(job, generation_stage_for(spec))
        report = job / "blender" / "reports" / f"{spec['runtime_stem']}_candidate_prepare.json"
        return bool(
            task
            and task.get("status") in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}
            and report.is_file()
            and (job / "provider" / "downloads" / generation_download_name(spec, "glb")).is_file()
        )

    owner_job = ensure_job_layout(resolve_job_root(owner_slug))
    pending_estimates: List[Dict[str, Any]] = []

    def add_pending(job: Path, stage: str, estimate: int) -> None:
        if existing_task(job, stage) is None:
            pending_estimates.append({"job": job.name, "stage": stage, "estimate_credits": estimate})

    add_pending(
        owner_job,
        generation_stage_for(owner_spec),
        int(owner_spec["image_to_3d_estimate_credits"]),
    )
    for spec in recipient_specs + creature_specs:
        job = ensure_job_layout(resolve_job_root(spec["asset_id"].rsplit(".", 1)[-1]))
        add_pending(
            job,
            generation_stage_for(spec),
            int(spec["image_to_3d_estimate_credits"]),
        )
    if not local_humanoid_batch:
        # Meshy image-to-3D can return a source above the rig endpoint's
        # triangle limit even when the requested target is lower. Reserve the
        # owner's conditional provider postprocess stages before generation so
        # the batch cannot spend the balance needed to finish its own rig path.
        add_pending(
            owner_job,
            continuation_stage_for(owner_spec, "rig_remesh"),
            int(owner_spec["remesh_estimate_credits"]),
        )
        add_pending(
            owner_job,
            rig_stage_for(owner_spec),
            int(owner_spec["rig_estimate_credits"]),
        )
        for role in ("idle", "attack", "death"):
            add_pending(
                owner_job,
                animation_stage_for(owner_spec, role),
                int(owner_spec["animation_estimate_credits"]),
            )

    required_credits = sum(int(item["estimate_credits"]) for item in pending_estimates)
    require_budget_headroom(pending_estimates, [owner_spec] + recipient_specs + creature_specs)
    balance: Optional[int] = None
    if required_credits:
        balance_result = MeshyClient(REPO_ROOT).check_balance()
        balance = balance_value(balance_result)
        if balance is None:
            raise RuntimeError("Shared humanoid batch preflight returned no numeric balance.")
    write_json(
        owner_job / "provider" / "credits" / "specialized_batch_preflight.json",
        {
            "schema_version": "1.0.0",
            "batch_id": batch_id,
            "owner": owner_slug,
            "selected_jobs": [slug for slug, _ in selected],
            "balance_before_paid_work": balance,
            "balance_probe_status": (
                "passed" if required_credits else "not_required_no_pending_paid_stages"
            ),
            "required_credits_for_missing_paid_stages": required_credits,
            "pending_stages": pending_estimates,
            "humanoid_policy": (
                "distinct Meshy geometry plus per-job local Blender rig and four skeletal actions"
                if local_humanoid_batch
                else "one verified standard provider rig and three provider actions; distinct geometry and exports per unit"
            ),
            "local_humanoid_batch": local_humanoid_batch,
            "paid_call_authorized_by": "user_task",
            "recorded_at": utc_now(),
        },
    )
    if required_credits and balance is not None and balance < required_credits:
        breakdown = ", ".join(
            f"{item['job']}:{item['stage']}={item['estimate_credits']}"
            for item in pending_estimates
        )
        raise RuntimeError(
            f"Shared humanoid batch gate refused paid work: balance={balance}, "
            f"required={required_credits}; {breakdown}"
        )

    results: List[Dict[str, Any]] = []
    if current_status(owner_spec) == "pdx_exported":
        results.append({"asset": owner_slug, "status": "reused_pdx_exported"})
    else:
        owner_candidate = (
            {"status": "reused_saved_candidate"}
            if saved_candidate_ready(owner_spec)
            else run_candidate(owner_spec)
        )
        results.append({"asset": owner_slug, "candidate": owner_candidate})
        owner_continuation = (
            continue_humanoid_local(owner_spec)
            if local_humanoid_batch
            else continue_humanoid(owner_spec)
        )
        results.append({"asset": owner_slug, "continuation": owner_continuation})

    for spec in recipient_specs + creature_specs:
        slug = spec["asset_id"].rsplit(".", 1)[-1]
        candidate = (
            {"status": "reused_saved_candidate"}
            if saved_candidate_ready(spec)
            else run_candidate(spec)
        )
        results.append({"asset": slug, "candidate": candidate})

    if local_humanoid_batch:
        for spec in recipient_specs:
            slug = spec["asset_id"].rsplit(".", 1)[-1]
            if current_status(spec) == "pdx_exported":
                results.append({"asset": slug, "status": "reused_pdx_exported"})
                continue
            results.append(
                {
                    "asset": slug,
                    "continuation": continue_humanoid_local(spec),
                }
            )
        for spec in creature_specs:
            slug = spec["asset_id"].rsplit(".", 1)[-1]
            if current_status(spec) == "pdx_exported":
                results.append({"asset": slug, "status": "reused_pdx_exported"})
                continue
            results.append({"asset": slug, "continuation": continue_creature(spec)})
        return results

    lineage = prepare_shared_humanoid_lineage(owner_spec, recipient_specs)
    for spec in recipient_specs:
        slug = spec["asset_id"].rsplit(".", 1)[-1]
        if current_status(spec) == "pdx_exported":
            results.append({"asset": slug, "status": "reused_pdx_exported"})
            continue
        results.append(
            {
                "asset": slug,
                "continuation": continue_humanoid_shared(
                    spec,
                    lineage["recipients"][slug],
                ),
            }
        )
    for spec in creature_specs:
        slug = spec["asset_id"].rsplit(".", 1)[-1]
        if current_status(spec) == "pdx_exported":
            results.append({"asset": slug, "status": "reused_pdx_exported"})
            continue
        results.append({"asset": slug, "continuation": continue_creature(spec)})
    return results


def print_credits_report(location: str) -> int:
    """Print credits per model and stage, failed and wasted credits, and credits avoided, for one job or a root."""

    path = Path(location) if location else resolve_job_root("report").parent
    jobs = find_job_roots(path)
    if not jobs:
        print(f"No job folders with a provider folder under {path}.")
        return 1
    print(format_report(credits_report(jobs)))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-config", type=Path, help="repository-owned job registry (required for provider work)")
    parser.add_argument(
        "--credits-report",
        nargs="?",
        const="",
        metavar="PATH",
        help="print the credits report for one job folder or every job under a root (default: this repository's "
        "jobs root); needs no API key and makes no provider call",
    )
    parser.add_argument(
        "--rebuild-runtime-textures",
        action="store_true",
        help="rebuild the finished humanoid job's runtime DDS from the remesh maps on disk; "
        "needs no API key and makes no provider call or Blender run",
    )
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--phase", choices=("full", "candidate"), default="full")
    parser.add_argument("--shared-humanoid-batch")
    parser.add_argument("assets", nargs="*")
    args = parser.parse_args()
    if args.credits_report is not None:
        return print_credits_report(args.credits_report)
    if args.jobs_config is None:
        parser.error("--jobs-config is required unless --credits-report is given")
    if args.rebuild_runtime_textures:
        configs = load_job_configs(args.jobs_config)
        assets = list(configs) if args.all or not args.assets else args.assets
        missing = sorted(set(assets) - set(configs))
        if missing:
            raise KeyError(f"Unknown configured 3D jobs: {missing}")
        rebuilt = {asset: rebuild_runtime_textures(configs[asset]) for asset in assets}
        print(json.dumps(rebuilt, indent=2, sort_keys=True))
        return 0
    require_api_key()
    configs = load_job_configs(args.jobs_config)
    if args.shared_humanoid_batch:
        batch_id = args.shared_humanoid_batch
        print(json.dumps(run_shared_humanoid_batch(batch_id, configs), indent=2, sort_keys=True))
        return 0
    assets = list(configs) if args.all or not args.assets else args.assets
    phase = args.phase
    results = []
    missing = sorted(set(assets) - set(configs))
    if missing:
        raise KeyError(f"Unknown configured 3D jobs: {missing}")
    selected_specs = [configs[item] for item in assets]
    for spec in selected_specs:
        vet_spec(spec)
    if phase in {"full", "candidate"}:
        preflight_selected_credits(selected_specs, phase)
    for asset in assets:
        spec = configs[asset]
        initialize_job(spec)
        if phase in {"full", "candidate"}:
            candidate = run_candidate(spec)
            results.append({"asset": asset, "candidate": candidate})
        if phase == "candidate":
            continue
        if spec["asset_kind"] in STATIC_ASSET_KINDS:
            results.append({"asset": asset, "continuation": continue_static(spec)})
        elif spec["asset_kind"] in CREATURE_ASSET_KINDS:
            results.append({"asset": asset, "continuation": continue_creature(spec)})
        else:
            continuation = (
                continue_humanoid_local(spec)
                if uses_local_humanoid_route(spec)
                else continue_humanoid(spec)
            )
            results.append({"asset": asset, "continuation": continuation})
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
