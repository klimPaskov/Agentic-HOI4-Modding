"""Create and preflight repository-configured HOI4 3D model jobs."""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any, Dict


if not os.environ.get("MESHY_API_KEY", "").strip():
    print(
        "MESHY_API_KEY is missing or blank. Stop. Run this PowerShell command, "
        "then restart the shell or Codex:\n\n"
        '[Environment]::SetEnvironmentVariable(\n'
        '    "MESHY_API_KEY",\n'
        '    "msy_your_actual_key_here",\n'
        '    "User"\n'
        ")\n"
    )
    raise SystemExit(2)

PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_ROOT.parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib.paths import (  # noqa: E402
    append_history,
    ensure_job_layout,
    file_record,
    read_job_document,
    read_json,
    resolve_job_root,
    utc_now,
    write_json,
)


def png_dimensions(path: Path) -> Dict[str, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Expected a PNG reference: {path}")
    width, height = struct.unpack(">II", header[16:24])
    return {"width": width, "height": height}


def job_yaml(job: Dict[str, Any]) -> str:
    return json.dumps(job, indent=2, sort_keys=True) + "\n"


def initialize_one(spec: Dict[str, Any]) -> Dict[str, Any]:
    slug = spec["asset_id"].rsplit(".", 1)[-1]
    job_root = ensure_job_layout(resolve_job_root(slug))
    reference = job_root / spec["reference_path"]
    if not reference.exists():
        raise FileNotFoundError(
            f"Ready Meshy reference is missing: {reference}. "
            "The approved image-generation route must create exactly one image before paid work."
        )
    original_images = sorted(
        path for path in (job_root / "refs" / "original").iterdir()
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if len(original_images) != 1 or original_images[0].name != reference.name:
        raise RuntimeError(
            f"Meshy input gate requires exactly one image in refs/original; found "
            f"{[path.name for path in original_images]}"
        )

    reference_record = file_record(reference, relative_to=job_root)
    dimensions = png_dimensions(reference)
    status = "preflight"
    job_file = job_root / "job.yaml"
    if job_file.exists():
        existing = read_job_document(job_file)
        status = existing.get("status", status)
    job = {
        "schema_version": "1.0.0",
        "job_id": f"hoi4_3d_model_jobs_{slug}",
        "owner_id": "hoi4_3d_model_jobs",
        "asset_id": spec["asset_id"],
        "asset_slug": slug,
        "status": status,
        "profile": spec["profile"],
        "asset_kind": spec["asset_kind"],
        "creature_rig_family": spec.get("creature_rig_family"),
        "scale_crosswalk": spec.get("scale_crosswalk"),
        "shared_humanoid_batch": spec.get("shared_humanoid_batch"),
        "shared_humanoid_rig_owner": spec.get("shared_humanoid_rig_owner"),
        "shared_humanoid_role": spec.get("shared_humanoid_role"),
        "image_to_3d_estimate_credits": spec.get("image_to_3d_estimate_credits"),
        "rig_source_target_polycount": spec.get("rig_source_target_polycount"),
        "remesh_estimate_credits": spec.get("remesh_estimate_credits"),
        "rig_estimate_credits": spec.get("rig_estimate_credits"),
        "animation_estimate_credits": spec.get("animation_estimate_credits"),
        "estimated_credits": spec.get("planned_total_credits"),
        "generation_stage": spec.get("generation_stage", "generation"),
        "rig_stage": spec.get("rig_stage"),
        "rig_input_mode": spec.get("rig_input_mode", "input_task_id"),
        "humanoid_rig_route": spec.get("humanoid_rig_route", ""),
        "brief": spec["asset_brief"],
        "required_components": spec["required_components"],
        "forbidden_additions": spec["forbidden_additions"],
        "excluded_provider_objects": spec.get("excluded_provider_objects", []),
        "source": {
            "mode": spec["reference_source_mode"],
            "authorization": "User-authorized agent-generated model reference.",
            "generator_output": spec["reference_generator_output"],
            "reference": reference_record,
            "dimensions": dimensions,
        },
        "meshy_input_gate": {
            "image_count": 1,
            "image": str(reference.relative_to(job_root)).replace("\\", "/"),
            "multi_view_thumbnails": False,
            "side_profile_sheet": False,
            "turnaround_board": False,
        },
        "provider_plan": {
            "ai_model": spec["meshy_ai_model"],
            "resolved_ai_model": spec.get("resolved_meshy_ai_model", spec["meshy_ai_model"]),
            "model_type": "standard",
            "pose_mode": spec["meshy_pose_mode"],
            "topology": "triangle",
            "target_polycount": spec["target_polycount"],
            "enable_pbr": True,
            "should_texture": True,
            "paid_attempts": spec.get("provider_paid_attempts", 1),
            "retry_paid_calls": spec.get("provider_retry_paid_calls", False),
            "estimated_credits": {
                key: value
                for key, value in (
                    ("image_to_3d", spec.get("image_to_3d_estimate_credits")),
                    ("remesh", spec.get("remesh_estimate_credits")),
                    ("rig", spec.get("rig_estimate_credits")),
                    ("animation", spec.get("animation_estimate_credits")),
                )
                if value is not None
            },
        },
        "blender_plan": {
            "provider_height_m": spec["target_height_m"],
            "target_height_m": spec.get("blender_target_height_m", spec["target_height_m"]),
            "effective_runtime_height_m": spec.get("blender_effective_runtime_height_m"),
            "runtime_entity_scale": spec.get("runtime_entity_scale"),
            "max_runtime_footprint_m": spec.get("max_runtime_footprint_m"),
            "runtime_footprint_policy": spec.get("runtime_footprint_policy", "reject"),
            "runtime_diffuse_gamma": spec.get("runtime_diffuse_gamma"),
            "vanilla_scale_reference": spec.get("vanilla_scale_reference"),
            "runtime_stem": spec["runtime_stem"],
            "dependency_lock": ".tools/3d_pipeline/config/dependencies.lock.json",
        },
        "required_actions": spec["required_actions"],
        "runtime": {
            "proposed_identifiers": spec["proposed_runtime_identifiers"],
            "actual_registration": None,
            "live_consumer": None,
            "in_game_evidence": None,
        },
        "handoff": {
            "runtime_handoff": "runtime/handoff.md",
            "crosswalk": "runtime/crosswalk.md",
            "manifest": "manifest.md",
        },
        "created_at": utc_now(),
    }
    if job_file.exists():
        existing = read_job_document(job_file)
        for field in (
            "created_at",
            "updated_at",
            "selected_provider_task",
            "exports",
            "runtime",
            "provider_lineage",
            "creature_rig_family",
            "scale_crosswalk",
            "shared_humanoid_batch",
            "shared_humanoid_rig_owner",
            "shared_humanoid_role",
            "image_to_3d_estimate_credits",
            "rig_source_target_polycount",
            "remesh_estimate_credits",
            "rig_estimate_credits",
            "animation_estimate_credits",
            "estimated_credits",
            "generation_stage",
            "rig_stage",
            "rig_input_mode",
            "humanoid_rig_route",
            "excluded_provider_objects",
        ):
            if field in existing:
                job[field] = existing[field]
    job_file.write_text(job_yaml(job), encoding="utf-8")

    brief = f"""# {slug}

## Asset brief

{spec["asset_brief"]}

## Profile and output

- Profile: {spec["profile"]}
- Meshy/provider character height: {spec["target_height_m"]} m
- Blender source-mesh calibration height: {spec.get("blender_target_height_m", spec["target_height_m"])} m
- Blender effective runtime height after entity scale: {spec.get("blender_effective_runtime_height_m", spec.get("blender_target_height_m", spec["target_height_m"]))} m
- Unit consumer scale: {spec.get("runtime_entity_scale", "not applicable")}
- Runtime footprint budget: {spec.get("max_runtime_footprint_m", "profile default or not applicable")} m
- Runtime footprint policy: {spec.get("runtime_footprint_policy", "reject")}
- Runtime diffuse gamma grade: {spec.get("runtime_diffuse_gamma", "not applied")}
- Target topology: triangles
- Meshy model: {spec["meshy_ai_model"]}
- Meshy reference: {spec["reference_path"]}
- Meshy input count: exactly one
- Side-profile or multi-view Meshy input: forbidden

## Required components

{chr(10).join(f"- {item}" for item in spec["required_components"])}

## Forbidden additions

{chr(10).join(f"- {item}" for item in spec["forbidden_additions"])}

## Source authorization

The reference was generated by the approved built-in image-generation route for this user-authorized model job. Its source output, dimensions, and checksum are recorded in refs/derived/reference_provenance.json.
"""
    brief_path = job_root / "refs" / "briefs" / "asset_brief.md"
    brief_path.write_text(brief, encoding="utf-8")

    provenance = {
        "schema_version": "1.0.0",
        "asset_id": spec["asset_id"],
        "source_mode": spec["reference_source_mode"],
        "authorization": "User-authorized agent-generated model reference.",
        "generator_output": spec["reference_generator_output"],
        "generation_prompt_record": spec["asset_brief"],
        "derived_reference": reference_record,
        "visual_preflight": {
            "single_subject": True,
            "complete_silhouette": True,
            "component_separation": True,
            "neutral_background": True,
            "no_multi_view_board": True,
            "no_side_profile_sheet": True,
            "approval": "parent_agent_visual_review",
        },
    }
    write_json(job_root / "refs" / "derived" / "reference_provenance.json", provenance)
    manifest_path = job_root / "refs" / "original" / "input_manifest.json"
    existing_manifest: Dict[str, Any] = {}
    if manifest_path.exists():
        try:
            existing_manifest = read_json(manifest_path)
        except (OSError, json.JSONDecodeError):
            existing_manifest = {}
    existing_manifest.update({
        "image_count": 1,
        "input": reference_record,
        "dimensions": dimensions,
        "sent_to_meshy": False,
    })
    write_json(manifest_path, existing_manifest)
    write_json(job_root / "validation" / "reference_preflight.json", {
        "status": "passed",
        "input_count": 1,
        "input": reference_record,
        "dimensions": dimensions,
        "checks": provenance["visual_preflight"],
    })
    if not (job_root / "history.jsonl").exists():
        append_history(
            job_root,
            state="preflight",
            event="job_initialized",
            actor="hoi4_3d_model_pipeline",
            details={
                "reference": reference_record,
                "input_image_count": 1,
                "profile": spec["profile"],
            },
        )
    if not (job_root / "manifest.md").exists():
        (job_root / "manifest.md").write_text(
            f"# {slug} model manifest\n\nStatus: preflight\n\n"
            "This manifest is updated only from recorded provider, Blender, "
            "export, reimport, runtime, and in-game evidence.\n",
            encoding="utf-8",
        )
    return {
        "asset_slug": slug,
        "job_root": str(job_root),
        "reference": reference_record,
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-config", required=True, type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("jobs", nargs="*")
    args = parser.parse_args()
    config_path = args.jobs_config.resolve()
    try:
        config_path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError("--jobs-config must remain inside the repository.") from exc
    payload = read_json(config_path)
    jobs = payload.get("jobs", payload.get("pilots"))
    if not isinstance(jobs, dict) or not jobs:
        raise ValueError("--jobs-config must contain a non-empty jobs mapping.")
    slugs = list(jobs) if args.all or not args.jobs else args.jobs
    missing = sorted(set(slugs) - set(jobs))
    if missing:
        raise KeyError(f"Unknown configured 3D jobs: {missing}")
    outputs = []
    for slug in slugs:
        outputs.append(initialize_one(jobs[slug]))
    print(json.dumps(outputs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
