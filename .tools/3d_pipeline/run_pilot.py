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

from blender_client import BlenderAdapterClient
from lib import heavy_job
from lib.mcp_stdio import MCPRouteError
from lib.paths import (
    append_history,
    dds_converter,
    ensure_job_layout,
    file_record,
    load_unit_types,
    read_job_document,
    read_json,
    resolve_job_root,
    sha256_file,
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
from lib.tripo import animation_source_kind, held_bones, held_parts, provider_name, released_bones, uses_tripo
from lib.reuse import (
    block_message,
    copy_artifacts,
    BLOCKING_STATES,
    find_other_job_result,
    sibling_jobs,
    reconcile_submission,
    unreconciled_submissions,
)
from meshy_client import (
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
from pack_pdx_material import (
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


def installed_game_dir() -> Path:
    """The game folder of this machine, by the kit's shared rule (`.tools/lib/game.py`). That file is read by path because the pipeline has its own `lib` package."""

    import importlib.util

    spec = importlib.util.spec_from_file_location("kit_game_folder", PIPELINE_ROOT.parent / "lib" / "game.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module.game_dir()


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
    if not source.is_file() and reference.get("mesh") and not Path(str(reference["mesh"])).is_absolute():
        # A relative path, such as the profile's own `gfx/models/units/western_european_infantry.mesh`, is a file of the installed game.
        source = (installed_game_dir() / str(reference["mesh"])).resolve()
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


def require_meshy_bootstrap(lock_path: Path = PIPELINE_ROOT / "config" / "dependencies.lock.json") -> None:
    """Refuse Meshy work when the last bootstrap ran without Meshy (the Blender-only mode)."""

    try:
        route = read_json(lock_path).get("routes", {}).get("meshy_mcp", {})
    except (OSError, ValueError, AttributeError):
        return
    if isinstance(route, dict) and route.get("verified") is False:
        print(
            "The 3D workflow was bootstrapped without Meshy, so Meshy jobs are blocked. Set MESHY_API_KEY, "
            "restart the shell, and run .tools/3d_pipeline/bootstrap_3d_workflow.py again (through HOI4 Mod Setup)."
        )
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


def route_remeshes(spec: Dict[str, Any]) -> bool:
    """True when the route replaces the generation with a Meshy remesh before anything is exported."""

    generation = spec.get("generation") or {}
    if spec.get("asset_kind") == "creature":
        return bool(spec.get("creature_remesh"))
    return (
        spec.get("asset_kind") == "humanoid"
        and not uses_local_humanoid_route(spec)
        and generation.get("model_type") == "standard"
        and not generation.get("should_remesh")
    )


def planned_stages(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The paid stages a job plans, in order, each with its price-table estimate."""

    def stage(name: str, operation: str, role: Optional[str], estimate: Any) -> Dict[str, Any]:
        return {"stage": name, "operation": operation, "role": role, "estimate_credits": int(estimate)}

    stages = [stage(generation_stage_for(spec), "image_to_3d", None, spec["image_to_3d_estimate_credits"])]
    if spec.get("asset_kind") == "creature" and spec.get("creature_remesh"):
        stages.append(stage(continuation_stage_for(spec, "creature_remesh"), "remesh", None, spec["remesh_estimate_credits"]))
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


# A unit's height on the map (its mesh height times the entity scale) as a share of the vanilla reference's.
# A giant may stand three times as tall as a soldier and a goblin half as tall. Outside that band the job's
# height is almost always in the wrong unit: `target_height_m` is the mesh height in HOI4 units (vanilla
# infantry is 7.35), not metres. Three Tripo jobs set 1.8 and came out a quarter of a soldier's height.
MIN_RUNTIME_SCALE_SHARE = 0.5
MAX_RUNTIME_SCALE_SHARE = 3.0


def check_runtime_scale(spec: Dict[str, Any]) -> None:
    """Refuse a job whose unit would be far smaller or larger on the map than its vanilla scale reference."""

    reference = spec.get("vanilla_scale_reference") or {}
    if spec.get("asset_kind") not in {"humanoid", "creature"} or not reference.get("runtime_height"):
        return
    height = float(spec.get("blender_target_height_m", spec.get("target_height_m", 0)) or 0)
    runtime = height * float(spec.get("runtime_entity_scale", reference.get("entity_scale", 1.0)))
    share = runtime / float(reference["runtime_height"])
    if MIN_RUNTIME_SCALE_SHARE <= share <= MAX_RUNTIME_SCALE_SHARE:
        return
    raise ValueError(
        f"{spec.get('asset_id', 'job')}: the unit would stand {runtime:.2f} units tall on the map, {share:.2f} times its vanilla "
        f"reference ({float(reference['runtime_height']):.2f}). `target_height_m` is the mesh height in HOI4 units, not metres: "
        f"use {float(reference.get('mesh_height', reference['runtime_height'])):.4g} for a unit as tall as the reference soldier, "
        f"and scale it for a smaller or larger body."
    )


def prepare_spec(spec: Dict[str, Any], *, require_budget: bool = True) -> Dict[str, Any]:
    """Fill in generation settings, price-table estimates and the job budget before any provider call.

    Idempotent. Estimates always come from config/meshy_pricing.json, never from the job.
    A path that makes no provider call passes `require_budget=False` and gets estimates only.
    """

    if spec.get("_credits_prepared"):
        return spec
    apply_unit_type(spec)
    check_runtime_scale(spec)
    generation = resolve_generation(spec, load_profile(spec["profile"]))
    pricing = load_pricing()
    spec["generation"] = generation
    spec["meshy_ai_model"] = spec["resolved_meshy_ai_model"] = generation["ai_model"]
    spec["target_polycount"] = generation["target_polycount"]
    if uses_tripo(spec):
        # Tripo has no API and no credit estimates here; its credits are typed in at intake.
        for key in ("image_to_3d", "remesh", "rig", "animation"):
            spec[f"{key}_estimate_credits"] = 0
        spec.setdefault("meshy_pose_mode", None)
        # No diffuse gamma grade for Tripo: its basecolor is already inside vanilla infantry's luma and saturation range, and the grade desaturates it.
        spec.setdefault("runtime_diffuse_gamma", 1.0)
        # Tripo's glossiness differs from unit to unit (the orc's mean was 26 after the Meshy scale, the zombie's p95 reached 183), so
        # a scale or a cap fits one and not the other. The unit's gloss is remapped onto vanilla infantry's distribution (ENG, GER, SOV:
        # mean 60, 95th percentile 101, config/vanilla_gloss.json); the specular level (green) is 56, the SOV value.
        spec.setdefault("runtime_specular_level", 56)
        spec.setdefault("runtime_gloss_remap", "vanilla_infantry")
        # Blender's glTF import adds a bone-shape Icosphere to every rigged file; it must not count as the unit's mesh.
        spec.setdefault("excluded_provider_objects", ["Icosphere"])
        spec["planned_total_credits"] = spec["credit_budget"] = 0
        spec["_credits_prepared"] = True
        return spec
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


DEFERRABLE_TOPOLOGY = ("welded boundary edges", "welded loose components")


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
    defer_topology_reason: str = "",
) -> None:
    """Block a candidate that fails a measured check.

    `defer_topology_reason` is for a raw provider candidate that the route replaces with
    a Meshy remesh before anything is exported: its welded boundary-edge and loose-part
    counts are recorded as deferred, and the same limits block the remeshed geometry.

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
    deferred = [item for item in failures if defer_topology_reason and item.startswith(DEFERRABLE_TOPOLOGY)]
    failures = [item for item in failures if item not in deferred]
    record = {
        "failures": failures,
        "geometry": geometry,
        "runtime_footprint": prep.get("runtime_footprint"),
        "profile": profile_name,
        "checks": evaluation["checks"],
        "exceptions_applied": evaluation["exceptions_applied"],
        "deferred": {"checks": deferred, "reason": defer_topology_reason} if deferred else None,
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


def load_vanilla_gloss() -> list:
    """The 101 quantiles of vanilla infantry's glossiness (config/vanilla_gloss.json)."""

    return json.loads((Path(__file__).resolve().parent / "config" / "vanilla_gloss.json").read_text(encoding="utf-8"))["quantiles"]


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
    packer_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Replace one extracted working map with its final PDX-layout DDS."""

    pack_report = packer(job, source_rel, **(packer_options or {}))
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


def check_diffuse_look(job: Path, provider_sources: Dict[str, str], textures: Dict[str, Any]) -> Dict[str, Any]:
    """Refuse a Tripo unit whose runtime diffuse differs from the generator's export by a global colour transform (`lib/texture_look.py`).

    A model's look comes from its picture and the generator's texture. A tint, filter or recolour over that texture is never the way to change
    it: the model is regenerated. The numbers go into the texture report (`diffuse_look`)."""

    from lib import texture_look

    source_rel = provider_sources.get("diffuse")
    conversion = next((item for item in textures.get("conversions") or [] if item.get("image") == "texture_0" and item.get("png")), None)
    if not source_rel or conversion is None or not (job / source_rel).is_file() or not (job / conversion["png"]).is_file():
        return textures
    numbers = texture_look.global_transform(job / source_rel, job / conversion["png"])
    textures["diffuse_look"] = {"source": source_rel, "runtime": conversion["png"], **numbers}
    reason = texture_look.refusal(numbers)
    if reason:
        raise RuntimeError(reason)
    return textures


def compress_runtime_textures(job: Path, spec: Dict[str, Any], textures: Dict[str, Any]) -> Dict[str, Any]:
    """Rewrite each runtime DDS as DXT5 with a full mip chain, the format vanilla units ship.

    The source is the processed PNG each conversion recorded (graded diffuse,
    packed specular, packed RRxG normal), resized to the recorded size. A profile
    that lists `runtime_texture_format` as `bgra_single` keeps the single-level
    BGRA files the converter wrote.
    """

    from lib.model_dds import write_dxt5

    profile = load_profile(spec["profile"])
    if profile.get("runtime_texture_format", "dxt5_mipped") != "dxt5_mipped":
        return textures
    written = {}
    for item in textures.get("conversions") or []:
        png_rel, dds_rel = item.get("png"), item.get("dds")
        if not png_rel or not dds_rel:
            continue
        source = job / png_rel
        if not source.is_file():
            raise FileNotFoundError(f"Runtime texture source is missing: {source}")
        width = int(item.get("width") or 0)
        height = int(item.get("height") or 0)
        sized = source
        with Image.open(source) as image:
            if width and height and image.size != (width, height):
                sized = job / "textures" / "processed" / f"{Path(png_rel).stem}_runtime.png"
                # Per channel: Pillow's RGBA resize premultiplies by alpha, which ruins the colour channels of a map whose alpha is
                # data (a specular map with glossiness near 26 lost a third of its green; a normal map's alpha is its tangent Y).
                channels = [band.resize((width, height), Image.Resampling.LANCZOS) for band in image.convert("RGBA").split()]
                Image.merge("RGBA", channels).save(sized, format="PNG")
        written[dds_rel] = write_dxt5(sized, job / dds_rel)
    textures["runtime_texture_format"] = {"format": "DXT5", "mips": "full chain", "files": written}
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
            packer_options={
                key: spec[name]
                for key, name in (("specular_level", "runtime_specular_level"), ("gloss_scale", "runtime_gloss_scale"), ("gloss_p95_limit", "runtime_gloss_p95_limit"))
                if spec.get(name) is not None
            } | ({"gloss_remap": load_vanilla_gloss()} if spec.get("runtime_gloss_remap") == "vanilla_infantry" else {}),
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
    if uses_tripo(spec):
        textures = check_diffuse_look(job, provider_sources, textures)
    textures = compress_runtime_textures(job, spec, textures)
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
    blender = BlenderAdapterClient(REPO_ROOT)
    vanilla_reference = stage_vanilla_reference(job, spec)
    generation_stage = generation_stage_for(spec)
    if uses_tripo(spec):
        generation_id, generation_glb = tripo_generation(job, spec)
        tripo_mount_size(job, spec)
    else:
        generation_id, generation_glb = meshy_generation(spec, job, MeshyClient(REPO_ROOT, job), generation_stage)
    return prepare_generation_candidate(spec, slug, job, blender, vanilla_reference, generation_id, generation_glb)


def tripo_generation(job: Path, spec: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """The generation task and base GLB `tripo_intake.py` placed in the job, with the maps it came with."""

    task = existing_task(job, generation_stage_for(spec))
    manifest = job / "provider" / "downloads" / f"{generation_download_name(spec, 'glb')}.manifest.json"
    if not task or not manifest.is_file():
        raise RuntimeError(
            f"{spec['asset_id']} is a Tripo job with no intake yet. Export the files from Tripo into an inbox and run: "
            f"py -3.13 -B .tools/3d_pipeline/tripo_intake.py --jobs-config <jobs.json> {job.name} --inbox <folder>"
        )
    glb = read_json(manifest)
    select_geometry_textures(job, spec, glb["file"]["relative_path"])
    return str(task["task_id"]), glb


def meshy_generation(spec: Dict[str, Any], job: Path, client: MeshyClient, generation_stage: str) -> Tuple[str, Dict[str, Any]]:
    """The paid (or reused) Meshy image-to-3D task and its GLB."""

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
    return generation_id, generation_glb


def prepare_generation_candidate(
    spec: Dict[str, Any],
    slug: str,
    job: Path,
    blender: BlenderAdapterClient,
    vanilla_reference: Optional[Dict[str, Any]],
    generation_id: str,
    generation_glb: Dict[str, Any],
) -> Dict[str, Any]:
    """Prepare and gate the provider's generation GLB in Blender (Meshy and Tripo alike)."""

    profile = read_json(PIPELINE_ROOT / "config" / "asset_profiles.json")["profiles"][spec["profile"]]
    footprint_config = profile.get("footprint", {})
    # The footprint budget is a map building's; a quadruped unit is sized by its back (tripo_mount_size).
    max_runtime_footprint_m = None if tripo_quadruped(spec) else footprint_config.get("max_runtime_footprint_m")
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
        defer_topology_reason=(
            "the route exports Meshy's remesh of this generation, never the generation itself"
            if route_remeshes(spec)
            else ""
        ),
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


def remeshed_creature_checkpoint(spec: Dict[str, Any], job: Path, blender: BlenderAdapterClient) -> str:
    """Remesh the creature's generation once with Meshy, prepare that model and gate it with the profile's limits.

    The raw generation is a high-detail mesh of many loose pieces; the rig and the export
    need one closed surface. The remesh keeps its own UV layout, so its own maps are bound.
    """

    prepare_spec(spec)
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    client = MeshyClient(REPO_ROOT, job)
    generation_stage = generation_stage_for(spec)
    generation = existing_task(job, generation_stage)
    if not generation:
        raise RuntimeError("Creature generation must be completed before the remesh.")
    generation_id = str(generation["task_id"])
    polycount = int(spec.get("creature_remesh_polycount", 30000))
    estimate = int(spec["remesh_estimate_credits"])
    remesh_id = provider_task(
        client,
        job,
        continuation_stage_for(spec, "creature_remesh"),
        task_type="remesh",
        estimate=estimate,
        input_stage=generation_stage,
        create=lambda: client.remesh(input_task_id=generation_id, target_polycount=polycount, estimate_credits=estimate),
        request=paid_request(spec, "remesh", "meshy_remesh", remesh_arguments(generation_id, polycount)),
    )
    remesh_glb = download_once(
        client,
        job,
        stage=continuation_stage_for(spec, "creature_remesh_glb"),
        task_id=remesh_id,
        task_type="remesh",
        format_name="glb",
        filename=continuation_download_name(spec, "remesh_model.glb"),
    )
    source_rel = remesh_glb["file"]["relative_path"]
    select_geometry_textures(job, spec, source_rel)
    texture_sources = prepare_pilot_texture_sources(job, spec, exported_rels=[source_rel])
    profile = load_profile(spec["profile"])
    prep = blender.prepare_candidate(
        slug,
        source_rel=source_rel,
        asset_kind="creature",
        target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
        runtime_stem=f"{spec['runtime_stem']}_remeshed",
        target_triangles=profile["triangle_range"]["working_triangle_target"],
        vanilla_reference=stage_vanilla_reference(job, spec),
        texture_source_rels=texture_sources,
        # As on the humanoid route: weld the seams before reducing, or the reduction tears the
        # mesh apart along its UV seams (the warhorse went from 4 to 241 pieces without it).
        repair_before_reduction=True,
        topology_weld_distance=0.0,
    )
    candidate_gate(job, prep, hard_max=profile["triangle_range"]["hard_max"], stage="remeshed_candidate")
    return str(prep["checkpoints"]["pre_export"])


def continue_creature(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Build, rig, animate, export, and reimport a custom nonhumanoid unit."""

    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    blender = BlenderAdapterClient(REPO_ROOT)
    candidate_report = read_json(
        job / "blender" / "reports" / f"{spec['runtime_stem']}_candidate_prepare.json"
    )
    source_checkpoint = (
        remeshed_creature_checkpoint(spec, job, blender)
        if spec.get("creature_remesh")
        else candidate_report["checkpoints"]["pre_export"]
    )
    component_checkpoint = "blender/checkpoints/creature_components.blend"
    components = blender.segment_creature_components(
        slug,
        source_checkpoint,
        component_checkpoint,
        region_mode="loose",
        component_prefix=f"{spec['runtime_stem']}_component",
    )
    rig_checkpoint = "blender/checkpoints/creature_rig_approved.blend"
    rig_options: Dict[str, Any] = {}
    size = tripo_mount_size(job, spec)
    if size and (spec.get("tripo") or {}).get("load"):
        # The load is found and bound by rule; the rider's height in this model's units places the Saddle_Node on its floor.
        rig_options = {"load": True, "rider_height": size["rider_height_in_mount_mesh"], "rider_footprint": size.get("rider_footprint")}
    if tripo_winged(spec):
        # The wings are found by rule and get their own chains (adapter/quadruped_wings.py).
        rig_options["wings"] = True
    rig = blender.author_creature_rig(
        slug,
        component_checkpoint,
        rig_checkpoint,
        creature_rig_family=str(spec["creature_rig_family"]),
        weight_mode="semantic",
        rig_name=f"{spec['runtime_stem']}_armature",
        rig_options=rig_options or None,
    )
    seat = ((rig.get("load") or {}).get("saddle") or {}) if rig_options else {}
    if seat.get("rider_share"):
        # The rider that fits the load (quadruped_load.fit_rider): its entity scale follows the share the rig found room for.
        size.update(rider_share=seat["rider_share"], rider_entity_scale=round(size["rider_entity_scale"] * float(seat["rider_share"]), 4),
                    saddle_room_load_vertices=seat.get("column_load_vertices"))
        write_json(job / "blender" / "reports" / "mount_size.json", size)
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
            action_style=str(action.get("action_style") or ""),
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
    staged = (
        stage_runtime_files(job, spec, {"mesh": mesh_rel, "animations": {role: report["output_rel"] for role, report in action_reports.items()}})
        if spec.get("unit_type")
        else None
    )
    return {
        "components": components,
        "rig": rig,
        "textures": textures,
        "mesh_export": mesh_export,
        "animation_exports": animation_exports,
        "action_reports": action_reports,
        "reimport": reimports,
        "runtime": staged["check"] if staged else None,
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


def humanoid_provider_stages(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Run (or reuse) the paid humanoid stages: remesh when needed, one rig, one clip per provider role."""

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
        if action.get("task_type") in {"blender_authored_skeletal", "reused_clip"}:
            continue
        if action.get("provider_action_id") is None:
            raise RuntimeError(
                f"Required action {role} has no provider action id or Blender authoring route."
            )
        stage = animation_stage_for(spec, role)
        animation_id = animate_library_clip(client, job, spec, action, stage, rig_stage, rig_id)
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

    return {
        "slug": slug,
        "job": job,
        "blender": blender,
        "vanilla_reference": vanilla_reference,
        "rig_id": rig_id,
        "animation_downloads": animation_downloads,
    }


def continue_humanoid(spec: Dict[str, Any]) -> Dict[str, Any]:
    stages = humanoid_provider_stages(spec)
    slug, job, blender = stages["slug"], stages["job"], stages["blender"]
    vanilla_reference = stages["vanilla_reference"]
    rig_id, animation_downloads = stages["rig_id"], stages["animation_downloads"]
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


def tripo_quadruped(spec: Dict[str, Any]) -> bool:
    """A Tripo job on a quadruped unit type (`mount`, `quadruped_beast`): Tripo's plain model, rigged and animated by the kit's quadruped rules."""

    name = spec.get("unit_type")
    return uses_tripo(spec) and bool(name) and load_unit_types().get(name, {}).get("rig") == "blender_quadruped"


def tripo_winged(spec: Dict[str, Any]) -> bool:
    """A Tripo quadruped whose unit type has wings (`winged_quadruped`): the rig finds the wings and gives them chains by rule."""

    return tripo_quadruped(spec) and bool(load_unit_types().get(spec.get("unit_type") or "", {}).get("wings"))


def tripo_mount_size(job: Path, spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Size a Tripo quadruped by the measured rule of `lib/mount_size.py` and set its `blender_target_height_m`.

    The job states `size_vs_horse` (the species' withers height over a horse's, with its source in `size_vs_horse_reason`) and, for a
    mount that carries a tower or howdah, `tripo.load: true`. A job's own `blender_target_height_m` wins. The rider is vanilla's rider
    size on the map; `rider.mesh_height` names the rider's mesh height when it is not vanilla infantry's."""

    if not tripo_quadruped(spec):
        return None
    from lib import mount_size

    manifest = job / "provider" / "downloads" / f"{generation_download_name(spec, 'glb')}.manifest.json"
    if not manifest.is_file():
        return None
    glb = job / read_json(manifest)["file"]["relative_path"]
    config = spec.get("tripo") or {}
    rider = spec.get("rider") or {}
    if tripo_winged(spec):
        # A winged quadruped has no species withers to measure against a horse: its body (wings left out) is as long on the map as
        # vanilla's longest land unit, times the job's `size_vs_longest_land_unit` (1 by default, its reason in `size_reason`).
        size = mount_size.longest_land_size(glb, float(spec.get("runtime_entity_scale", 0.8)), float(spec.get("size_vs_longest_land_unit", 1.0)))
        size["size_reason"] = spec.get("size_reason", "")
        if spec.get("_explicit_target_height"):
            size["overridden_by_job"] = spec["blender_target_height_m"]
        else:
            spec["blender_target_height_m"] = size["target_height_m"]
        check_runtime_scale(spec)
        write_json(job / "blender" / "reports" / "mount_size.json", size)
        return size
    size = mount_size.mount_size(glb, float(spec.get("runtime_entity_scale", 0.8)), float(spec.get("size_vs_horse", 1.0)),
                                 bool(config.get("load")), rider.get("mesh_height"))
    size["size_vs_horse_reason"] = spec.get("size_vs_horse_reason", "")
    if rider.get("folder"):
        # The rider's room on the load is what its own clips sweep in plan (lib/mount_size.rider_footprint).
        footprint = mount_size.rider_footprint(Path(rider["folder"]), str(rider.get("stem")), dict(rider.get("roles") or {}))
        size["rider_reach_share"] = round(footprint["reach_share"], 4)
        size["rider_footprint"] = {"cells": footprint["cells"], "cell": round(footprint["cell_share"] * size["rider_height_in_mount_mesh"], 5)}
    if spec.get("_explicit_target_height"):
        size["overridden_by_job"] = spec["blender_target_height_m"]
    else:
        spec["blender_target_height_m"] = size["target_height_m"]
    check_runtime_scale(spec)
    write_json(job / "blender" / "reports" / "mount_size.json", size)
    return size


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

    provider_name(spec)
    require_route_ready(spec)
    require_reference_approval(spec)
    prepared = prepare_spec(spec)
    if uses_tripo(spec) and spec["asset_kind"] not in STATIC_ASSET_KINDS | {"humanoid"} and not tripo_quadruped(spec):
        raise RuntimeError(f"{spec['asset_id']}: Tripo jobs cover units on a humanoid or quadruped unit_type and static models, not {spec['asset_kind']}.")
    if uses_tripo(spec) and spec["asset_kind"] == "humanoid" and not spec.get("unit_type"):
        raise RuntimeError(f"{spec['asset_id']}: a Tripo unit job needs a unit_type.")
    return prepared


def preflight_selected_credits(specs: List[Dict[str, Any]], phase: str) -> None:
    """Check the full selected tranche before any paid provider call."""

    specs = [spec for spec in specs if not uses_tripo(spec)]
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


UNIT_SCALE_REFERENCE = {"source_head_bones": ["LeftFoot", "Head"], "target_head_bones": ["LeftFoot", "Head"]}


def apply_unit_type(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Fill a job's profile, kind and actions from its `unit_type` (config/unit_types.json).

    A role whose first library clip another role already uses reuses that clip instead of
    paying for it again; a Blender role (a quadruped gait, the seated slump) costs nothing.
    Actions a job lists itself win.
    """

    name = spec.get("unit_type")
    if not name or spec.get("_unit_type_applied"):
        return spec
    types = load_unit_types()
    if name not in types:
        raise ValueError(f"Unknown unit_type {name!r}; known: {', '.join(sorted(types))}.")
    unit = types[name]
    spec.setdefault("profile", unit["profile"])
    if unit.get("validation_overrides"):
        # Measured per type (see the type's validation_calibration); the profile's other types keep its limits.
        spec.setdefault("profile_validation_overrides", dict(unit["validation_overrides"]))
    if unit["rig"] == "blender_quadruped":
        spec.setdefault("asset_kind", "creature")
        # Meshy's a-pose and t-pose are for humanoids only; a four-legged generation is sent without one.
        spec["meshy_pose_mode"] = None
        spec.setdefault("creature_rig_family", "quadruped")
        # The raw Meshy generation is hundreds of loose pieces; the rig needs one closed surface. Tripo's model is one skin.
        spec.setdefault("creature_remesh", not uses_tripo(spec))
        spec.setdefault("creature_remesh_polycount", 30000)
        # Vanilla cavalry_horse.mesh is 15.64 units to the head under pdxmesh scale 0.45 and entity
        # scale 0.65, so 4.57 on the map, smaller than vanilla infantry (5.89). A mount matches it.
        # A Tripo quadruped is sized by its back instead (tripo_mount_size, lib/mount_size.py).
        spec.setdefault("_explicit_target_height", "blender_target_height_m" in spec)
        spec.setdefault("blender_target_height_m", round(4.57 / float(spec.get("runtime_entity_scale", 0.8)), 4))
    else:
        spec.setdefault("asset_kind", "humanoid")
    if not spec.get("required_actions"):
        actions: List[Dict[str, Any]] = []
        first_role_for_clip: Dict[int, str] = {}
        for role, config in unit["roles"].items():
            row: Dict[str, Any] = {"role": role, "fps": 24, "loop": bool(config.get("loop")), "root_policy": "in_place"}
            if config.get("meshy"):
                clip_id, clip_key = config["meshy"][0]
                row["library_candidates"] = [list(item) for item in config["meshy"]]
                if clip_id in first_role_for_clip:
                    row.update(provider_action_id=None, task_type="reused_clip", reuse_role=first_role_for_clip[clip_id])
                else:
                    first_role_for_clip[clip_id] = role
                    row.update(provider_action_id=clip_id, library_key=clip_key)
            elif config.get("blender") == "seated_slump":
                row.update(provider_action_id=None, task_type="reused_clip", reuse_role="idle", slump=True)
            else:
                row.update(provider_action_id=None, task_type="blender_authored_skeletal", action_style=config["blender"])
            actions.append(row)
        spec["required_actions"] = actions
    spec["_unit_type_applied"] = True
    return spec


def verify_library_clips(spec: Dict[str, Any], client: "MeshyClient") -> Dict[str, Any]:
    """Look the paid clips up (free) and switch to the next candidate when an id no longer names its clip."""

    wanted = [action for action in spec["required_actions"] if action.get("provider_action_id") is not None]
    if not wanted:
        return {}
    ids = sorted({int(item[0]) for action in wanted for item in action.get("library_candidates", [[action["provider_action_id"], ""]])})
    listed = client.list_animations(action_ids=ids)
    keys: Dict[int, str] = {}
    for content in listed.get("content", []):
        if isinstance(content, dict) and content.get("type") == "text":
            try:
                for row in json.loads(content["text"]):
                    keys[int(row["action_id"])] = str(row.get("key"))
            except (ValueError, TypeError, KeyError):
                continue
    report = {}
    for action in wanted:
        candidates = action.get("library_candidates") or [[action["provider_action_id"], action.get("library_key", "")]]
        chosen = next((item for item in candidates if keys.get(int(item[0])) == item[1] or (not item[1] and int(item[0]) in keys)), None)
        if chosen is None:
            raise RuntimeError(
                f"No Meshy library clip for the {action['role']} role still matches its key: "
                f"{[(item[0], item[1], keys.get(int(item[0]))) for item in candidates]}. Update config/unit_types.json."
            )
        action["provider_action_id"], action["library_key"] = int(chosen[0]), chosen[1]
        report[action["role"]] = {"action_id": int(chosen[0]), "key": chosen[1]}
    return report


RETIRED_CLIP_TEXT = "animation is no longer available"


def animate_library_clip(
    client: MeshyClient, job: Path, spec: Dict[str, Any], action: Dict[str, Any], stage: str, rig_stage: str, rig_id: str
) -> str:
    """Animate one role, moving to the role's next library candidate when Meshy refuses a retired clip.

    Meshy keeps some retired clips in its library listing but refuses to animate them, so the free key
    check cannot catch them. A refusal creates no task and costs nothing; any other error is raised.
    """

    candidates = action.get("library_candidates") or [[action["provider_action_id"], action.get("library_key", "")]]
    ids = [int(item[0]) for item in candidates]
    start = ids.index(int(action["provider_action_id"])) if int(action["provider_action_id"]) in ids else 0
    retired = set()
    history = job / "history.jsonl"
    for line in history.read_text(encoding="utf-8").splitlines() if history.is_file() else []:
        row = json.loads(line)
        if row.get("state") == "provider_clip_retired" and row.get("event") == stage:
            retired.add(int(row.get("details", {}).get("refused_action_id", -1)))
    for index in range(start, len(candidates)):
        action_id, key = int(candidates[index][0]), str(candidates[index][1])
        if action_id in retired and index + 1 < len(candidates):
            continue
        request = paid_request(
            spec, "animation", "meshy_animate", animate_arguments(rig_id, action_id, None), role=action["role"]
        )
        try:
            task = provider_task(
                client,
                job,
                stage,
                task_type="animation",
                estimate=spec["animation_estimate_credits"],
                input_stage=rig_stage,
                create=lambda action_id=action_id: client.animate(
                    rig_task_id=rig_id,
                    action_id=action_id,
                    estimate_credits=spec["animation_estimate_credits"],
                ),
                request=request,
            )
        except MCPRouteError as error:
            if RETIRED_CLIP_TEXT not in str(error):
                raise
            # Meshy answered 400 Invalid request: no task exists, so release the reservation.
            for entry in unreconciled_submissions([job], request.fingerprint):
                reconcile_submission(entry["file"], note=f"Meshy refused retired library clip {action_id} ({key}); no task was created")
            if index + 1 == len(candidates):
                raise
            append_history(
                job,
                state="provider_clip_retired",
                event=stage,
                actor="meshy_mcp",
                details={"refused_action_id": action_id, "refused_key": key, "next": list(candidates[index + 1]), "credits": 0},
            )
            continue
        action["provider_action_id"], action["library_key"] = action_id, key
        return task
    raise RuntimeError(f"No library clip left for the {action['role']} role.")


def glb_animation_name(path: Path) -> str:
    """The first animation name stored in a GLB; Blender's glTF importer gives the action this name."""

    data = path.read_bytes()
    length = int.from_bytes(data[12:16], "little")
    document = json.loads(data[20 : 20 + length])
    animations = document.get("animations") or []
    if not animations or not animations[0].get("name"):
        raise RuntimeError(f"{path.name} holds no named animation.")
    return str(animations[0]["name"])


def _prepared_armature(prep: Dict[str, Any]) -> str:
    try:
        return str(prep["rig_and_actions"]["root_translation_sanitization"]["actions"][0]["armature"])
    except (KeyError, IndexError, TypeError):
        return "Armature"


def write_animation_receipt(
    job: Path,
    role: str,
    task: Dict[str, Any],
    scene_name: str,
    provider_name: str,
    source_rel: str,
    source_sha: str,
    library_clip: Any,
    source_kind: str = "meshy_animate",
) -> str:
    """Write the provenance receipt animation import requires, once per role, and return its job path."""

    receipt_rel = f"provider/animation_receipts/{role}.json"
    existing = read_json(job / receipt_rel) if (job / receipt_rel).is_file() else {}
    current = (scene_name, source_sha, task.get("task_id"))
    if (existing.get("source_action_name"), existing.get("source_sha256"), existing.get("source_reference_id")) != current:
        # A receipt from a failed attempt that named another clip is replaced, never reused.
        write_json(job / receipt_rel, {
            "verification_status": "verified",
            "source_kind": source_kind,
            "source_reference_id": task.get("task_id"),
            "source_action_name": scene_name,
            "provider_file_action_name": provider_name,
            "source_sha256": source_sha,
            "source_rel": source_rel,
            "library_clip": library_clip,
            "verified_by": "hoi4_3d_model_pipeline",
            "verified_at": utc_now(),
            "basis": (
                "Tripo's own animation exported from its app, intake-recorded with a checksum manifest."
                if source_kind == "professional_source"
                else "Completed Meshy animate task from this job's own rig task, downloaded with a checksum manifest."
            ),
        })
    return receipt_rel


def _parts(held: Any) -> List[Dict[str, Any]]:
    """The held parts as a list: the job's weapon block alone (a dict) or `lib.tripo.held_parts` (the weapon and the shield)."""

    return [part for part in (held if isinstance(held, list) else [held]) if part]


def ground_exported_clip(mesh: Path, anim: Path, role: str, weapon: Any, humanoid: bool = True) -> Dict[str, Any]:
    """The Tripo route's last grounding rule, on the exported clip itself (lib/tripo_pose.py says why): the clip is resampled at the game's 30 frames a
    second after Blender grounded it at 24, so a foot dips between keys. Every frame's lowest point is put on the ground (a death is only lifted), the
    weapon or shield the unit has let go of never deciding where it is. A death whose thighs split apart past vanilla's deaths has its knees swung together first (lib/tripo_splay.py, TRIPO-DEATH-SPLAY), one whose hips hold themselves up while it falls has them brought down in a free fall first (lib/tripo_fall.py, TRIPO-DEATH-HOVER), one whose boots hang above the ground has its legs settled next, one
    whose boot kicks up again once the hips are down has that leg laid across the kick (lib/tripo_kick.py, TRIPO-DEATH-LEG-KICK), and one whose chest, head or hands stay up once the hips are down has its upper body settled next, both judged on the body as the ground pass will lift it. In a death the wing chains never decide where the body is, and each wing sunk under the ground is turned up about its root last (lib/tripo_chain_lift.py). `weapon` is the job's weapon block or the list of held parts (`lib.tripo.held_parts`)."""

    from lib import pdx_ground, tripo_fall, tripo_kick, tripo_pose, tripo_splay

    released = released_bones(_parts(weapon), role)
    record: Dict[str, Any] = {}
    if role == "death":
        # a death's wing chains never decide where the body is: they are lifted off the ground instead (lib/tripo_chain_lift.py)
        from lib import pdx_deform, tripo_chain_lift

        released = list(released) + [name for name in tripo_chain_lift.chain_bones(pdx_deform.load_mesh(mesh)) if name not in released]
    if role == "death" and humanoid:
        splay = tripo_splay.close_death_legs(mesh, anim, anim, exclude_bones=released)
        record["splay"] = dict(splay.__dict__)
        fall = tripo_fall.settle_death_fall(mesh, anim, anim, exclude_bones=released)
        record["fall"] = {"changed": fall.changed, "frames": fall.frames, "largest_drop": fall.largest_drop, "ratio_before": fall.ratio_before,
                          "ratio_after": fall.ratio_after, "legs": fall.legs, "note": fall.note}
        legs = tripo_pose.settle_death_legs(mesh, anim, anim, exclude_bones=released)
        record["legs"] = {"changed": legs.changed, "joints": list(legs.joints), "share": round(legs.share, 3), "from_frame": legs.from_frame, "ramp_frames": legs.frames,
                          "boots_height_before": round(legs.height_before, 4), "boots_height_after": round(legs.height_after, 4), "note": legs.note}
        kick = tripo_kick.settle_death_kick(mesh, anim, anim, exclude_bones=released)
        record["kick"] = {"changed": kick.changed, "onset": kick.onset, "spans": kick.spans, "before": kick.before, "after": kick.after, "note": kick.note}
        upper = tripo_pose.settle_death_upper(mesh, anim, anim, exclude_bones=released)
        record["upper_body"] = {"changed": upper.changed, "turns_degrees": upper.turns, "from_frame": upper.from_frame, "ramp_frames": upper.frames,
                                "heights_before": upper.heights_before, "heights_after": upper.heights_after, "note": upper.note}
    if role == "death":
        lift = tripo_chain_lift.lift_death_chains(mesh, anim, anim)
        if lift.changed or lift.sunk_before:
            record["chain_lift"] = dict(lift.__dict__)
    fix = pdx_ground.ground(mesh, anim, anim, death=role == "death", tolerance=tripo_pose.GROUND_TOLERANCE, exclude_bones=released)
    record["ground"] = {"root": fix.root, "shifted": fix.corrected, "largest_shift": round(fix.largest_shift, 4), "note": fix.reason}
    return record


def guard_staged_defend(staged: Path, stem: str, spec: Dict[str, Any], roles: Any, records: Dict[str, Any]) -> None:
    """The defend posed as a guard on the staged files when the job asks (`"defend_pose": "guard"`, lib/tripo_guard.py), recorded."""

    if (spec.get("tripo") or {}).get("defend_pose") != "guard" or "defend" not in roles:
        return
    from lib import map_read, pdx_deform, tripo_guard

    mesh = staged / f"{stem}.mesh"
    records[f"{stem}_defend.anim"]["guard"] = tripo_guard.guard_defend(mesh, staged / f"{stem}_defend.anim", staged / f"{stem}_idle.anim",
                                                                         map_read.front_of(pdx_deform.load_mesh(mesh)))


def look_back_staged_retreat(staged: Path, stem: str, spec: Dict[str, Any], roles: Any, records: Dict[str, Any]) -> None:
    """The retreat turned to look back over the shoulder on the staged files when the job asks (`"retreat_pose": "look_back"`,
    lib/tripo_look_back.py), recorded."""

    if (spec.get("tripo") or {}).get("retreat_pose") != "look_back" or "retreat" not in roles:
        return
    from lib import tripo_look_back

    records[f"{stem}_retreat.anim"]["look_back"] = tripo_look_back.look_back(staged / f"{stem}.mesh", staged / f"{stem}_retreat.anim")


def pose_staged_roles(staged: Path, stem: str, spec: Dict[str, Any], roles: Any, records: Dict[str, Any]) -> None:
    """The role poses a job asks for on the staged files: the defend's guard, then the retreat's look back."""

    guard_staged_defend(staged, stem, spec, roles, records)
    look_back_staged_retreat(staged, stem, spec, roles, records)


def registration_streams(mesh: Path) -> Dict[str, List[Dict[str, str]]]:
    """Each shape's mesh streams and their material's texture names, for the registration (lib/unit_registration.mesh_streams)."""

    from lib import unit_registration

    try:
        return unit_registration.mesh_streams(mesh) if mesh.is_file() else {}
    except (OSError, ValueError):
        return {}


def burn_staged_death(staged: Path, stem: str, roles: List[str]) -> Dict[str, Any]:
    """The burn death (lib/tripo_burn.py) on the staged files: the heap, its bone and the fire's locator added to the mesh, the heap's bone
    keyed at rest in every other clip, the death held at its peak and burnt to ash, and the plan written beside the files."""

    from lib import tripo_burn

    mesh = staged / f"{stem}.mesh"
    heap = tripo_burn.add_heap(mesh, staged / f"{stem}_diffuse.dds")
    for role in roles:
        if role != "death":
            tripo_burn.add_rest_joint(mesh, staged / f"{stem}_{role}.anim")
    death = tripo_burn.burn_death(mesh, staged / f"{stem}_death.anim")
    return tripo_burn.write_plan(staged, stem, heap, death)


def clear_held_props(mesh: Path, anim: Path, role: str, weapon: Any) -> Dict[str, Any]:
    """The Tripo route's last pose step (lib/tripo_final_clearance.py): every held weapon and shield kept out of the body in every frame of the exported
    clip, by the same solve as the grip stage, on the mesh the game loads. A part the unit lets go of in this role is left to its fall."""

    from lib import tripo_final_clearance

    parts = [{"bone": part["bone"], "release_roles": part.get("release_roles") or []} for part in _parts(weapon) if part.get("bone")]
    return tripo_final_clearance.clear_clip_file(mesh, anim, anim, parts, role) if parts else {}


def clear_staged_props(job: Path, staged: Path, spec: Dict[str, Any], roles: List[str], weapon: Any, records: Dict[str, Any]) -> None:
    """`clear_held_props` on every staged clip of an armed unit, recorded with the clip's file (`"clear_props": false` in the tripo block: none)."""

    stem = spec["runtime_stem"]
    if not weapon or (spec.get("tripo") or {}).get("clear_props", True) is False:
        return
    for role in roles:
        name = f"{stem}_{role}.anim"
        records[name]["clear_props"] = clear_held_props(staged / f"{stem}.mesh", staged / name, role, weapon)
        records[name]["staged"] = file_record(staged / name, relative_to=job)


def lift_sunk_neck(mesh: Path, anim: Path, role: str) -> Dict[str, Any]:
    """The Tripo route's neck rule on a staged humanoid clip (lib/tripo_neck.py, TRIPO-NECK-SUNK): where the head sinks between the shoulders
    past vanilla's worst, the neck (or the clavicles, whichever the measure blames) is turned toward the rest pose by the smallest share that
    brings the head's base back above the shoulder line. It runs before the weights are smoothed and fitted, so they fit the lifted clip."""

    from lib import tripo_neck

    lift = tripo_neck.lift_neck(mesh, anim, anim, role)
    return {"changed": lift.changed, "group": lift.group, "joints": list(lift.joints), "share": lift.share, "frames_changed": lift.frames_changed,
            "ramp_frames": lift.ramp_frames, "neck_before": round(lift.neck_before, 3), "neck_after": round(lift.neck_after, 3), "tried": lift.tried,
            "note": lift.note}


def job_has_plates(spec: Dict[str, Any]) -> bool:
    """Whether the job's tripo block asks for armour plates (a chain with the region `plates`)."""

    return any((chain or {}).get("region") == "plates" for chain in ((spec.get("tripo") or {}).get("chains") or []))


def job_has_cloak(spec: Dict[str, Any]) -> bool:
    """Whether the job has a cape (TRIPO-CLOAK-STRETCH runs for it, as `tripo/tripo_checks.job_regions` reads it): `cape: true` or a `cloak` chain."""

    chains = {chain.get("region") if isinstance(chain, dict) else str(chain) for chain in ((spec.get("tripo") or {}).get("chains") or [])}
    return bool(spec.get("cape")) or "cloak" in chains


def ease_staged_cloak_bends(job: Path, staged: Path, spec: Dict[str, Any], roles: List[str], records: Dict[str, Any]) -> None:
    """The spine ease for a stretched back (lib/tripo_cloak_bend.py) on every staged clip of a humanoid unit with a cape or cloak chain, recorded
    with the clip's file. A job without a cape keeps its pose. `"ease_cloak_bend": false` in the job's tripo
    block switches it off."""

    from lib import tripo_cloak_bend

    if tripo_quadruped(spec) or not job_has_cloak(spec) or (spec.get("tripo") or {}).get("ease_cloak_bend", True) is False:
        return
    stem = spec["runtime_stem"]
    for role in roles:
        name = f"{stem}_{role}.anim"
        bend = tripo_cloak_bend.ease_cloak_bend(staged / f"{stem}.mesh", staged / name, staged / name, role)
        records[name]["cloak_bend"] = {key: (list(value) if isinstance(value, tuple) else value) for key, value in bend.__dict__.items()}
        records[name]["staged"] = file_record(staged / name, relative_to=job)


def ease_staged_shoulders(job: Path, staged: Path, spec: Dict[str, Any], roles: List[str], records: Dict[str, Any]) -> None:
    """The shoulder ease (lib/tripo_shoulder.py, TRIPO-SHOULDER-SWELL) on every staged clip of a humanoid unit, after the weight fit: where the
    shoulder and the upper back swell, the spine or the clavicles turn toward the unit's own stance (the idle's first frame). The idle is
    eased last, so every clip is judged against the stance it had. `"ease_shoulders": false` in the job's tripo block switches it off."""

    from lib import tripo_shoulder

    if tripo_quadruped(spec) or (spec.get("tripo") or {}).get("ease_shoulders", True) is False:
        return
    stem = spec["runtime_stem"]
    idle = staged / f"{stem}_idle.anim"
    for role in sorted(roles, key=lambda name: name == "idle"):
        name = f"{stem}_{role}.anim"
        ease = tripo_shoulder.ease_shoulders(staged / f"{stem}.mesh", staged / name, staged / name, role, idle if idle.is_file() else None)
        records[name]["shoulder_ease"] = {key: (list(value) if isinstance(value, tuple) else value) for key, value in ease.__dict__.items()}
        # Then the clavicle that still tears the girdle turns toward the stance, the upper arm keeping its direction (TRIPO-SHOULDER-TEAR).
        # `"ease_clavicles": false` switches it off.
        if (spec.get("tripo") or {}).get("ease_clavicles", True) is not False:
            lever = tripo_shoulder.ease_clavicles(staged / f"{stem}.mesh", staged / name, staged / name, role, idle if idle.is_file() else None)
            records[name]["clavicle_ease"] = {key: (list(value) if isinstance(value, tuple) else value) for key, value in lever.__dict__.items()}
        records[name]["staged"] = file_record(staged / name, relative_to=job)


def ease_staged_poses(job: Path, staged: Path, spec: Dict[str, Any], roles: List[str], records: Dict[str, Any]) -> None:
    """The pose eases after the weight fit, in order: the spine under a cloak (lib/tripo_cloak_bend.py, TRIPO-CLOAK-STRETCH), then a swollen
    shoulder (lib/tripo_shoulder.py, TRIPO-SHOULDER-SWELL), which judges the clips the first left."""

    ease_staged_cloak_bends(job, staged, spec, roles, records)
    ease_staged_shoulders(job, staged, spec, roles, records)


def _smooth_and_fit(staged: Path, stem: str, roles: List[str], weapon: Any, spec: Dict[str, Any]) -> Dict[str, Any]:
    """The smoothing (`"smooth_weights": false` switches it off) and then the fit (`"fit_weights": false`) on the staged mesh, recorded."""

    tripo = spec.get("tripo") or {}
    # A mount's load is bound wholly to one bone (adapter/quadruped_load.py): that bone is locked, so the load stays rigid.
    load_bones = ["Load"] if tripo_quadruped(spec) and tripo.get("load") else []
    out: Dict[str, Any] = {}
    if tripo.get("smooth_weights", True) is not False:
        out["stretch_smooth"] = smooth_stretched_weights(staged, stem, roles, weapon, load_bones, job_has_plates(spec))
    if tripo.get("fit_weights", True) is not False:
        out["weight_fit"] = fit_clip_weights(staged, stem, roles, weapon, load_bones, job_has_plates(spec))
    return out


def _girdle_on(spec: Dict[str, Any]) -> bool:
    # Off unless the job asks for it: two fits of nearly the same clips differ by more than the rule gains (lib/tripo_girdle.py).
    return not tripo_quadruped(spec) and (spec.get("tripo") or {}).get("girdle_weights", False) is True


def fit_staged_weights(job: Path, staged: Path, spec: Dict[str, Any], roles: List[str], weapon: Any) -> Dict[str, Any]:
    """The smoothing and the fit on the staged mesh. For a humanoid the weights they start from are kept for the girdle trial
    (`girdle_trial`), which runs after the pose eases."""

    stem = spec["runtime_stem"]
    if _girdle_on(spec):
        trial = job / "validation" / "girdle_trial"
        shutil.rmtree(trial, ignore_errors=True)
        trial.mkdir(parents=True)
        shutil.copy2(staged / f"{stem}.mesh", trial / "start.mesh")
    return _smooth_and_fit(staged, stem, roles, weapon, spec)


def girdle_trial(job: Path, staged: Path, spec: Dict[str, Any], roles: List[str], weapon: Any) -> Optional[Dict[str, Any]]:
    """The girdle rule (lib/tripo_girdle.py), after the pose eases, for a humanoid whose clips still fail TRIPO-SHOULDER-SWELL or
    TRIPO-SHOULDER-TEAR. From the weights the fit started from, two trials smooth and fit against the eased clips, one with the rule and one
    without, and the rule's weights replace the staged mesh when the bounded trade accepts them against the other. The rule is judged on the
    clips as they leave the route: tried before the shoulder ease, it could not lower what the ease left (the ogre's attack 0.198 to 0.197)."""

    from lib import pdx_deform, tripo_chains, tripo_girdle, weight_fit

    trial = job / "validation" / "girdle_trial"
    stem = spec["runtime_stem"]
    if not _girdle_on(spec) or not (trial / "start.mesh").is_file():
        return None
    mesh = staged / f"{stem}.mesh"
    anims = [staged / f"{stem}_{role}.anim" for role in roles]
    now = tripo_girdle.measures(mesh, anims)
    failing = [n for n, m in now.items() if not n.startswith("_") and (m["girdle"] > tripo_girdle.tripo_shoulder.GIRDLE_LIMIT
                                                                      or m["swell"] > tripo_girdle.tripo_shoulder.SWELL_LIMIT)]
    record: Dict[str, Any] = {"failing_before": failing}
    if not failing:
        shutil.rmtree(trial, ignore_errors=True)
        return dict(record, note="every clip passes the shoulder checks")
    results = {}
    for name in ("without", "with"):
        folder = trial / name
        folder.mkdir()
        shutil.copy2(trial / "start.mesh", folder / mesh.name)
        for anim in anims:
            shutil.copy2(anim, folder / anim.name)
        if name == "with":
            plates = weight_fit.plate_vertices(pdx_deform.load_mesh(folder / mesh.name)) if job_has_plates(spec) else None
            record["rule"] = tripo_girdle.confine_arm_weights(folder / mesh.name, folder / mesh.name, held_bones(_parts(weapon)),
                                                              tuple(tripo_chains.REGION_PREFIX.values()), plates)
        _smooth_and_fit(folder, stem, roles, weapon, spec)
        results[name] = tripo_girdle.measures(folder / mesh.name, [folder / a.name for a in anims])
    result = tripo_girdle.trade(results["without"], results["with"])
    record.update({"accepted": result.accepted, "deformed_edges_before": result.deformed_before, "deformed_edges_after": result.deformed_after,
                   "reasons": result.reasons, "clips": result.clips})
    if result.accepted:
        shutil.copy2(trial / "with" / mesh.name, mesh)
    shutil.rmtree(trial, ignore_errors=True)
    return record


def smooth_stretched_weights(staged: Path, stem: str, roles: List[str], weapon: Any, locked: Sequence[str] = (), plates: bool = False) -> Dict[str, Any]:
    """The Tripo route's weight rule on the staged mesh (lib/stretch_smooth.py): smooth the weights where the unit's own clips stretch or
    squash edges, at the strength that lowers that most without making any clip worse. A held weapon's bone is locked, so it stays rigid,
    and so are the chain stage's cloak and wing bones, whose weights that stage sets by its own rule."""

    from lib import pdx_deform, stretch_smooth, tripo_chains, weight_fit

    mesh = staged / f"{stem}.mesh"
    mask = weight_fit.plate_vertices(pdx_deform.load_mesh(mesh)) if plates else None  # the armour plates keep their weights, as in the fit
    result = stretch_smooth.smooth(mesh, [staged / f"{stem}_{role}.anim" for role in roles], mesh,
                                   locked_bones=held_bones(_parts(weapon)) + list(locked),
                                   locked_prefixes=tuple(tripo_chains.REGION_PREFIX.values()), locked_mask=mask)
    totals = {key: sum(clip["stretched"] + clip["squashed"] for clip in getattr(result, key).values()) for key in ("before", "after")}
    return {"changed": result.changed, "passes": result.passes, "seed_vertices": result.seeds, "region_vertices": result.region,
            "vertices_changed": result.vertices_changed, "deformed_edges_before": totals["before"], "deformed_edges_after": totals["after"],
            "per_clip_after": result.after, "trials": result.trials, "note": result.note,
            "hand_bleed_vertices": result.hand_bleed}


def fit_clip_weights(staged: Path, stem: str, roles: List[str], weapon: Any, locked: Sequence[str] = (), plates: bool = False) -> Dict[str, Any]:
    """The Tripo route's weight fit on the staged mesh (lib/weight_fit.py), after the smoothing: the weights where the unit's own clips
    deform it are solved for the ones that keep its edges' lengths in those clips, at the strength that lowers the deformed edges most
    without making any clip worse. The weapon, chain and load bones are locked as for the smoothing, and so are the armour plates."""

    from lib import pdx_deform, tripo_chains, weight_fit

    mesh = staged / f"{stem}.mesh"
    mask = weight_fit.plate_vertices(pdx_deform.load_mesh(mesh)) if plates else None
    result = weight_fit.fit_rounds(mesh, [staged / f"{stem}_{role}.anim" for role in roles], mesh,
                            locked_bones=held_bones(_parts(weapon)) + list(locked),
                            locked_prefixes=tuple(tripo_chains.REGION_PREFIX.values()), locked_mask=mask)
    totals = {key: sum(clip["stretched"] + clip["squashed"] for clip in getattr(result, key).values()) for key in ("before", "after")}
    return {"changed": result.changed, "step": result.step, "region_vertices": result.region, "vertices_changed": result.vertices_changed,
            "plate_vertices_locked": int(mask.sum()) if mask is not None else 0, "deformed_edges_before": totals["before"],
            "deformed_edges_after": totals["after"], "per_clip_after": result.after, "trials": result.trials, "note": result.note,
            "rounds": result.rounds, "round_totals": list(result.round_totals)}


def export_unit_roles(
    job: Path,
    spec: Dict[str, Any],
    blender: BlenderAdapterClient,
    roles: Dict[str, Dict[str, Any]],
    mesh_rel: str,
    chain: str,
    library: Dict[str, Any],
    mesh_export: Dict[str, Any],
    textures: Dict[str, Any],
) -> Dict[str, Any]:
    """Export and re-import every finished role, record the job and stage the runtime files."""

    slug = spec["asset_id"].rsplit(".", 1)[-1]
    stem = spec["runtime_stem"]
    exports: Dict[str, str] = {}
    for role, report in roles.items():
        anim_rel = f"export/anim/{stem}_{role}.anim"
        report["export"] = blender.export_animation(slug, chain, report["action"], anim_rel)
        report["reimport"] = blender.reimport_export(slug, mesh_rel, anim_rel, proof_name=f"{stem}_{role}")
        exports[role] = anim_rel
    update_job(job, status="pdx_exported", exports={"mesh": mesh_rel, "animations": exports}, unit_type=spec["unit_type"])
    append_history(
        job,
        state="pdx_exported",
        event="unit_exported",
        actor="hoi4_3d_model_pipeline",
        details={"unit_type": spec["unit_type"], "library": library, "final_checkpoint": chain, "mesh": file_record(job / mesh_rel, relative_to=job)},
    )
    write_json(job / "blender" / "reports" / "unit_roles.json", {"unit_type": spec["unit_type"], "final_checkpoint": chain, "roles": roles})
    staged = stage_runtime_files(job, spec, {"mesh": mesh_rel, "animations": exports})
    return {"unit_type": spec["unit_type"], "mesh_export": mesh_export, "textures": textures, "roles": roles, "final_checkpoint": chain, "runtime": staged["check"]}


def finish_unit_base(job: Path, slug: str, spec: Dict[str, Any], blender: BlenderAdapterClient, prep: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Gate the prepared base, pack its textures, apply the job's loose part edits and save `unit_base_pre_export`."""

    gate_profile = dict(profile, validation={**profile.get("validation", {}), **spec.get("profile_validation_overrides", {})})
    candidate_gate(job, prep, hard_max=profile["triangle_range"]["hard_max"], stage="animated_candidate_base", profile=gate_profile)
    textures = finalize_pdx_runtime_textures(job, spec, blender.process_textures(slug, prep["checkpoints"]["pre_export"]))
    base = prep["checkpoints"]["pre_export"]
    if spec.get("loose_part_edits"):
        # A prop the provider rig weighted to several limbs (a maul hanging between the legs) is dropped or bound to one bone.
        edited = blender.edit_loose_parts(slug, base, "blender/checkpoints/base_loose_parts.blend", spec["loose_part_edits"])
        write_json(job / "blender" / "reports" / "loose_part_edits.json", {**edited, "reason": spec.get("loose_part_edits_reason", "")})
        base = edited["checkpoint"]
    blender.save_checkpoint(slug, base, "unit_base_pre_export")
    return textures


def tripo_unit_stages(spec: Dict[str, Any]) -> Dict[str, Any]:
    """What `humanoid_provider_stages` returns, read from the files `tripo_intake.py` placed: no provider call."""

    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    tripo_generation(job, spec)  # binds the base model's texture maps, or says to run the intake
    downloads: Dict[str, Dict[str, Any]] = {}
    for action in spec["required_actions"]:
        role = action.get("reuse_role") or action["role"]
        if role in downloads:
            continue
        manifest = job / "provider" / "downloads" / f"{animation_download_name(spec, role, 'glb')}.manifest.json"
        if not manifest.is_file() or not existing_task(job, animation_stage_for(spec, role)):
            raise RuntimeError(f"The Tripo intake has no clip for the {role} role; add it to the job's tripo.roles and run the intake again.")
        downloads[role] = read_json(manifest)
    return {
        "slug": slug,
        "job": job,
        "blender": BlenderAdapterClient(REPO_ROOT),
        "vanilla_reference": stage_vanilla_reference(job, spec),
        "rig_id": None,
        "animation_downloads": downloads,
    }


def continue_unit_humanoid(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Finish a Meshy-rigged unit of any humanoid type: one prepared body, every role retargeted onto it.

    Each role's library clip is imported onto the single prepared rig with a provenance
    receipt, then grounded per frame (standing types) or seated on the attach origin
    (riders), exported and re-imported against the one exported mesh.
    """

    apply_unit_type(spec)
    unit = load_unit_types()[spec["unit_type"]]
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job = ensure_job_layout(resolve_job_root(slug))
    tripo = uses_tripo(spec)
    library = {} if tripo else verify_library_clips(spec, MeshyClient(REPO_ROOT, job))
    stages = tripo_unit_stages(spec) if tripo else humanoid_provider_stages(spec)
    blender = stages["blender"]
    downloads = stages["animation_downloads"]
    profile = load_profile(spec["profile"])
    stem = spec["runtime_stem"]
    base_role = "attack" if "attack" in downloads else next(iter(downloads))
    base_source = downloads[base_role]["file"]["relative_path"]
    texture_sources = prepare_pilot_texture_sources(
        job,
        spec,
        # A Tripo clip GLB carries no maps (as Meshy's rig GLBs): the base model they all share is the lineage source.
        exported_rels=[spec["texture_lineage_model_rel"]] if tripo else [item["file"]["relative_path"] for item in downloads.values()],
        geometry_source_rel=spec.get("geometry_source_rel"),
    )
    prep = blender.prepare_candidate(
        slug,
        source_rel=base_source,
        asset_kind="humanoid",
        target_height_m=spec.get("blender_target_height_m", spec["target_height_m"]),
        runtime_entity_scale=float(spec.get("runtime_entity_scale", 1.0)),
        runtime_stem=f"{stem}_base",
        target_triangles=profile["triangle_range"]["working_triangle_target"],
        excluded_provider_objects=spec.get("excluded_provider_objects"),
        vanilla_reference=stages["vanilla_reference"],
        texture_source_rels=texture_sources,
        geometry_source_rel=spec.get("geometry_source_rel"),
        repair_before_reduction=True,
        topology_weld_distance=0.0,
    )
    textures = finish_unit_base(job, slug, spec, blender, prep, profile)
    chain = "blender/checkpoints/unit_base_pre_export.blend"
    mesh_rel = f"export/mesh/{stem}.mesh"
    mesh_export = blender.export_mesh(slug, chain, mesh_rel)
    armature = _prepared_armature(prep)
    # The prepared base checkpoint keeps the base clip's own action, so Blender names that clip's
    # imported copy "<name>.001". Every other import removes its source action after the retarget,
    # so a clip that several roles reuse keeps its plain name each time.
    base_clip = glb_animation_name(job / base_source)
    # A rerun after a failure starts the roles again from the base: the role checkpoints of the
    # earlier attempt are derived from files on disk, hold no paid data, and block a new import.
    for stale in (job / "blender" / "checkpoints").glob("unit_*.blend"):
        if stale.name != "unit_base_pre_export.blend":
            stale.unlink()
    roles: Dict[str, Dict[str, Any]] = {}
    for action in spec["required_actions"]:
        role = action["role"]
        clip_role = action.get("reuse_role") or role
        source_rel = downloads[clip_role]["file"]["relative_path"]
        provider_name = glb_animation_name(job / source_rel)
        scene_name = provider_name + (".001" if provider_name == base_clip else "")
        task = existing_task(job, animation_stage_for(spec, clip_role)) or {}
        source_sha = sha256_file(job / source_rel)
        receipt_rel = write_animation_receipt(
            job, role, task, scene_name, provider_name, source_rel, source_sha,
            task.get("library_clip") if tripo else library.get(clip_role), animation_source_kind(spec),
        )
        target = f"{stem}_{role}"
        imported_rel = f"blender/checkpoints/unit_{role}.blend"
        # the weapon and the shield the unit lets go of in this role keep their own location keys (the drop's path)
        location_bones = released_bones(held_parts(spec), role) or None
        imported = blender.import_animation_action(
            slug, chain, source_rel, receipt_rel, imported_rel, scene_name, armature, target,
            animation_source_kind(spec), str(task.get("task_id")), source_sha, root_scale_reference=UNIT_SCALE_REFERENCE,
            location_bones=location_bones,
        )
        chain = imported_rel
        if unit.get("seated"):
            finished_rel = f"blender/checkpoints/unit_{role}_seated.blend"
            finishing = blender.seat_rider_action(slug, chain, finished_rel, target, armature, slump=bool(action.get("slump")))
        else:
            finished_rel = f"blender/checkpoints/unit_{role}_grounded.blend"
            # In a clip where the unit lets go of its weapon or shield (the job names the roles in tripo.weapon.release_roles and
            # tripo.shield.release_roles), that bone never decides where the ground is: the body does.
            let_go = released_bones(held_parts(spec), role)
            finishing = blender.correct_action_grounding(
                slug, chain, finished_rel, target, target_armature_name=armature,
                excluded_contact_bones=let_go or None,
            )
        chain = finished_rel
        roles[role] = {"action": target, "clip_role": clip_role, "receipt": receipt_rel, "import": imported, "finishing": finishing}
    return export_unit_roles(job, spec, blender, roles, mesh_rel, chain, library, mesh_export, textures)


def job_status(slug: str, spec: Dict[str, Any], jobs_config: Path) -> Dict[str, Any]:
    """Where one job stands and the next command to run. Reads files only; no key, no provider call."""

    job = resolve_job_root(slug)
    config = jobs_config.as_posix()
    run = f"py -3.13 -B .tools/3d_pipeline/run_pilot.py --jobs-config {config} {slug}"
    result: Dict[str, Any] = {"asset": slug, "job_root": job.as_posix(), "unit_type": spec.get("unit_type")}
    if not (job / "job.yaml").is_file():
        result.update(state="not_initialized", next=f"py -3.13 -B .tools/3d_pipeline/init_pilot_jobs.py --jobs-config {config} {slug}")
        return result
    document = read_job_document(job / "job.yaml")
    result["state"] = document.get("status")
    history = job / "history.jsonl"
    if history.is_file():
        lines = [line for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
        result["last_events"] = [
            {key: entry.get(key) for key in ("timestamp", "state", "event")}
            for entry in (json.loads(line) for line in lines[-3:])
        ]
    preflight = job / "validation" / "reference_preflight.json"
    pending = sorted(
        path.name
        for path in (job / "provider" / "submissions").glob("*.json")
        if read_json(path).get("state") in BLOCKING_STATES
    )
    ledger = read_ledger(job)
    result["credits_consumed"] = sum(int(row.get("consumed_credits") or 0) for row in ledger)
    result["credit_budget"] = spec.get("credit_budget")
    exports = document.get("exports") or {}
    if uses_tripo(spec) and not existing_task(job, generation_stage_for(spec)):
        result["next"] = (
            f"Export the files from Tripo into an inbox folder as {slug}__rigged.glb (a unit) or {slug}__model.glb "
            f"(a building or prop), then: py -3.13 -B .tools/3d_pipeline/tripo_intake.py --jobs-config {config} {slug} --inbox <folder>"
        )
    elif not preflight.is_file() or read_json(preflight).get("status") != "passed":
        result["next"] = (
            "Look at refs/original/meshy_input.png, answer the six visual checks in a JSON file, then: "
            f"py -3.13 -B .tools/3d_pipeline/init_pilot_jobs.py --jobs-config {config} --record-visual-review {slug} "
            "--reviewer <name> --review-file <answers.json>"
        )
    elif pending:
        result["next"] = (
            f"Reconcile the uncertain paid submissions first ({', '.join(pending)}): read each task in the Meshy "
            "task list and record it with lib.reuse.reconcile_submission. Never submit the stage again."
        )
    elif not exports.get("mesh"):
        candidate = job / "blender" / "reports" / f"{spec.get('runtime_stem', slug)}_candidate_prepare.json"
        result["next"] = (
            f"{run} --phase candidate   (then review the previews in blender/previews before the full run)"
            if not candidate.is_file()
            else f"{run}   (paid stages that already succeeded are reused, never paid twice)"
        )
    else:
        result["exports"] = exports
        result["next"] = (
            f"Copy {(job / 'runtime' / 'files').as_posix()} into the mod's model folder, paste runtime/registration.md, "
            "then run check_unit_files.py on that folder with --mod-root ."
        )
    return result


# Tripo meshes come with flipped triangles (UNIT-WINDING), small open loops (UNIT-HOLE) and stored normals that
# disagree with the faces (UNIT-NORMALS) on every unit measured, so the unit route repairs them for free.
TRIPO_DEFAULT_REPAIRS = ("winding", "holes", "normals")


def default_repairs(spec: Dict[str, Any]) -> List[str]:
    """The `repair_unit.py` repairs the unit route runs on its own export: Tripo's three, none for Meshy."""

    if tripo_quadruped(spec):
        # Tripo makes a quadruped and what it carries as one skin: a part fused to another that moves apart is cut and capped,
        # and a join inside one skin (a hanging tail grown into a hind leg, a leg into the belly) gets blended weights (UNIT-BRIDGE).
        return ["winding", "bridges", "holes", "weights", "normals"]
    return list(TRIPO_DEFAULT_REPAIRS) if uses_tripo(spec) else []


def tripo_default_repairs(job: Path, staged: Path, stem: str, unit: Optional[Dict[str, Any]], repairs: List[str]) -> Dict[str, Any]:
    """Repair the staged mesh in place (the unrepaired export stays in export/mesh) and record the counts."""

    import repair_unit

    out = job / "validation" / "tripo_repair"
    report = repair_unit.repair(staged, out, repairs, stem, 16, unit)
    shutil.copy2(out / "files" / f"{stem}.mesh", staged / f"{stem}.mesh")
    summary = {
        "repairs": report["repairs"],
        "rules_before": report["rules_before"],
        "rules_after": report["rules_after"],
        "mesh": {name: {key: value for key, value in entry.items()} for name, entry in report["blender"].get("objects", {}).items()},
        "unrepaired_export": f"export/mesh/{stem}.mesh",
    }
    write_json(job / "runtime" / "tripo_repair.json", summary)
    append_history(job, state="pdx_exported", event="tripo_default_repairs", actor="hoi4_3d_model_pipeline", details=summary)
    return summary


def stage_runtime_files(job: Path, spec: Dict[str, Any], exports: Dict[str, Any]) -> Dict[str, Any]:
    """Copy the selected exports into runtime/files under their final names, check them and write the registration."""

    import check_unit_files
    from lib.unit_registration import registration_text

    stem = spec["runtime_stem"]
    staged = job / "runtime" / "files"
    staged.mkdir(parents=True, exist_ok=True)
    copies = {f"{stem}.mesh": job / exports["mesh"]}
    for role, rel in exports["animations"].items():
        copies[f"{stem}_{role}.anim"] = job / rel
    for image, suffix in (("texture_0", "diffuse"), ("texture_normal", "normal"), ("texture_specular", "specular")):
        source = job / "textures" / "dds" / f"{image}.dds"
        if source.is_file():
            copies[f"{stem}_{suffix}.dds"] = source
    records = {}
    for name, source in copies.items():
        shutil.copy2(source, staged / name)
        records[name] = {"source": file_record(source, relative_to=job), "staged": file_record(staged / name, relative_to=job)}
    unit = load_unit_types().get(spec.get("unit_type") or "")
    profile = load_profile(spec["profile"])
    repairs = default_repairs(spec)
    repaired = tripo_default_repairs(job, staged, stem, unit, repairs) if repairs else None
    if repaired:
        records[f"{stem}.mesh"]["staged"] = file_record(staged / f"{stem}.mesh", relative_to=job)
        records[f"{stem}.mesh"]["repairs"] = repaired["repairs"]
    weapon_cfg = held_parts(spec)  # the weapon and the shield
    weapon_bones = [part["bone"] for part in weapon_cfg if part.get("release_roles") and part.get("bone")]
    if uses_tripo(spec):
        # First a humanoid's sunk head is lifted back above the shoulders (lib/tripo_neck.py). `"lift_neck": false` in the job's tripo block
        # switches it off.
        if not tripo_quadruped(spec) and (spec.get("tripo") or {}).get("lift_neck", True) is not False:
            for role in sorted(exports["animations"]):
                records[f"{stem}_{role}.anim"]["neck_lift"] = lift_sunk_neck(staged / f"{stem}.mesh", staged / f"{stem}_{role}.anim", role)
        # A defend posed as a guard (`"defend_pose": "guard"`, lib/tripo_guard.py): torso to the stance and leaning back, both hands before
        # the face, and a retreat that looks back over the shoulder (`"retreat_pose": "look_back"`, lib/tripo_look_back.py), before the
        # weights are fitted to the clips.
        pose_staged_roles(staged, stem, spec, exports["animations"], records)
        # After the mesh repairs, on the staged files: weights smoothed where the unit's own clips stretch it (lib/stretch_smooth.py), the
        # weapon bone locked. `"smooth_weights": false` in the job's tripo block switches it off.
        # Then the weights where the clips still deform the skin are fitted to those clips (lib/weight_fit.py), the same bones and the armour
        # plates locked. `"fit_weights": false` in the job's tripo block switches it off.
        records[f"{stem}.mesh"].update(fit_staged_weights(job, staged, spec, sorted(exports["animations"]), weapon_cfg))
        records[f"{stem}.mesh"]["staged"] = file_record(staged / f"{stem}.mesh", relative_to=job)
        # What the weights cannot keep whole is eased in the pose: a hard torso bend under a cloak, then a swollen shoulder. Then the girdle
        # rule may be tried on the weights (lib/tripo_girdle.py, off unless the job sets `"girdle_weights": true`).
        ease_staged_poses(job, staged, spec, sorted(exports["animations"]), records)
        records[f"{stem}.mesh"]["girdle_weights"] = girdle_trial(job, staged, spec, sorted(exports["animations"]), weapon_cfg)
        # Then the mesh the game loads decides where the ground is. A death that burns away (`"death_kind": "burn"`, lib/tripo_burn.py) is grounded
        # as the standing reaction it is, then burnt: its heap, bone and locator join the mesh, and its plan is written beside the files.
        burning = (spec.get("tripo") or {}).get("death_kind") == "burn" and "death" in exports["animations"]
        for role in sorted(exports["animations"]):
            records[f"{stem}_{role}.anim"]["runtime_ground"] = ground_exported_clip(staged / f"{stem}.mesh", staged / f"{stem}_{role}.anim",
                                                                                "burn_stand" if burning and role == "death" else role, weapon_cfg,
                                                                                humanoid=not tripo_quadruped(spec))
            records[f"{stem}_{role}.anim"]["staged"] = file_record(staged / f"{stem}_{role}.anim", relative_to=job)
        if burning:
            records[f"{stem}.mesh"]["burn"] = burn_staged_death(staged, stem, sorted(exports["animations"]))
            for name in [f"{stem}.mesh"] + [f"{stem}_{role}.anim" for role in sorted(exports["animations"])]:
                records[name]["staged"] = file_record(staged / name, relative_to=job)
        # Last of all, after the grounding and the death settles, no held weapon or shield is left in the body in any frame: the retarget and the
        # export put back what the grip stage cleared. `"clear_props": false` in the job's tripo block switches it off.
        clear_staged_props(job, staged, spec, sorted(exports["animations"]), weapon_cfg, records)
    findings, facts = check_unit_files.check_files(staged, unit, profile, weapon_bones=weapon_bones)
    errors = [item.__dict__ for item in findings if item.severity == "error"]
    shapes = next(iter(facts["meshes"].values()), {}).get("shapes", []) if facts["meshes"] else []
    roles = sorted(exports["animations"])
    folder = spec.get("runtime_model_folder") or f"gfx/models/units/{stem}"
    rider = mount_rider_registration(job, spec) if (unit or {}).get("entity_template") == "mount" else None
    text = registration_text(
        unit_entity=f"{stem}_entity",
        model_folder=folder,
        stem=stem,
        shapes=shapes,
        roles=roles,
        scale=float(spec.get("runtime_entity_scale", 1.0)),
        template=(unit or {}).get("entity_template", "infantry"),
        state_set=str(spec.get("entity_state_set") or {"mount": "cavalry", "rider": "cavalry"}.get((unit or {}).get("entity_template", ""), "infantry")),
        rider=rider,
        streams=registration_streams(staged / f"{stem}.mesh"),
    )
    (job / "runtime" / "registration.md").write_text(text, encoding="utf-8")
    report = {"files": records, "check": {"errors": errors, "warnings": [item.__dict__ for item in findings if item.severity != "error"]}, "facts": facts}
    write_json(job / "runtime" / "files.json", report)
    if errors:
        raise RuntimeError(f"The staged runtime files fail {len(errors)} check(s); see runtime/files.json: {errors[:3]}")
    return report


def mount_rider_registration(job: Path, spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The rider a mount job names (`rider`: the folder of an exported unit, its stem, a role map), for the registration.

    Its entity scale is the one that makes it vanilla's rider size on the map (lib/mount_size.py), and its mesh and entity get names of
    their own, so a foot unit's files can ride without clashing with that unit's own registration."""

    rider = spec.get("rider") or {}
    if not rider.get("folder"):
        return None
    from lib import pdx_binary

    folder = Path(rider["folder"])
    stem = str(rider.get("stem") or next(folder.glob("*.mesh")).stem)
    size = read_json(job / "blender" / "reports" / "mount_size.json") if (job / "blender" / "reports" / "mount_size.json").is_file() else {}
    summary = pdx_binary.summarize_mesh(pdx_binary.read(folder / f"{stem}.mesh"))
    return {
        "stem": stem,
        "model_folder": str(rider.get("model_folder") or f"gfx/models/units/{stem}"),
        "shapes": list(summary.shapes),
        "roles": sorted(path.stem[len(stem) + 1:] for path in folder.glob(f"{stem}_*.anim")),
        "role_map": dict(rider.get("roles") or {}),
        "scale": float(rider.get("scale") or size.get("rider_entity_scale") or 1.0),
        "mesh_name": f"{spec['runtime_stem']}_rider_mesh",
        "entity": f"{spec['runtime_stem']}_rider_entity",
    }


def print_credits_report(location: str) -> int:
    """Print credits per model and stage, failed and wasted credits, and credits avoided, for one job or a root."""

    path = Path(location) if location else resolve_job_root("report").parent
    jobs = find_job_roots(path)
    if not jobs:
        print(f"No job folders with a provider folder under {path}.")
        return 1
    print(format_report(credits_report(jobs)))
    return 0


def run_file_only_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> Optional[int]:
    """Run --credits-report, --status or --rebuild-runtime-textures; none needs a key or makes a provider call."""

    if args.credits_report is not None:
        return print_credits_report(args.credits_report)
    if args.jobs_config is None:
        parser.error("--jobs-config is required unless --credits-report is given")
    if not (args.status or args.rebuild_runtime_textures):
        return None
    configs = load_job_configs(args.jobs_config)
    assets = list(configs) if args.all or not args.assets else args.assets
    missing = sorted(set(assets) - set(configs))
    if missing:
        raise KeyError(f"Unknown configured 3D jobs: {missing}")
    if args.status:
        print(json.dumps([job_status(asset, configs[asset], args.jobs_config) for asset in assets], indent=2))
    else:
        print(json.dumps({asset: rebuild_runtime_textures(configs[asset]) for asset in assets}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
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
    parser.add_argument(
        "--status",
        action="store_true",
        help="print where each job stands and the next command to run; reads files only",
    )
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--phase", choices=("full", "candidate"), default="full")
    parser.add_argument("--shared-humanoid-batch")
    heavy_job.add_argument(parser)
    parser.add_argument("assets", nargs="*")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    heavy_job.apply(args)
    handled = run_file_only_command(args, parser)
    if handled is not None:
        return handled
    try:
        configs = load_job_configs(args.jobs_config)
        selected = list(configs) if args.all or not args.assets else args.assets
        needs_key = bool(args.shared_humanoid_batch) or any(not uses_tripo(configs.get(name, {})) for name in selected)
    except (OSError, ValueError):
        needs_key = True  # report the missing key first, as before
    if needs_key:
        require_api_key()
        require_meshy_bootstrap()
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
        elif spec.get("unit_type"):
            results.append({"asset": asset, "continuation": continue_unit_humanoid(spec)})
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
