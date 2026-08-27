"""Structured, job-root-bounded Blender MCP adapter.

The adapter intentionally exposes named operations instead of an arbitrary
Blender-Python tool. All caller paths are job-relative and all Blender work is
delegated to the checked-in worker with a locked executable and extension root.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from mcp.server.fastmcp import FastMCP


MODULE_ROOT = Path(__file__).resolve().parent
PIPELINE_ROOT = MODULE_ROOT.parent
REPO_ROOT = PIPELINE_ROOT.parents[1]
CONFIG_PATH = Path(
    os.environ.get(
        "HOI4_3D_CONFIG",
        str(PIPELINE_ROOT / "config" / "blender_hoi4_adapter.json"),
    )
).resolve()
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
JOB_ROOT = Path(CONFIG["job_root"]).resolve()
JOB_OVERRIDES = {
    job_id: Path(path).resolve()
    for job_id, path in CONFIG.get("job_overrides", {}).items()
}
BLENDER = Path(CONFIG["blender_executable"]).resolve()
ADAPTER_VERSION = CONFIG["adapter_version"]
ALLOWED_OPERATIONS = set(CONFIG["operations"])
PROFILE_CONFIG_PATH = PIPELINE_ROOT / "config" / "asset_profiles.json"

mcp = FastMCP("hoi4-blender-adapter")


def _job(job_id: str) -> Path:
    if not job_id or Path(job_id).is_absolute() or ":" in job_id or ".." in Path(job_id).parts:
        raise ValueError("job_id must be a job-root-relative path without traversal.")
    if job_id in JOB_OVERRIDES:
        candidate = JOB_OVERRIDES[job_id]
    else:
        candidate = (JOB_ROOT / Path(job_id.replace("/", os.sep))).resolve()
        try:
            candidate.relative_to(JOB_ROOT)
        except ValueError as exc:
            raise ValueError("job_id escaped the configured job root.") from exc
    if not candidate.exists():
        raise FileNotFoundError(candidate)
    return candidate


def _relative(value: str, root: Path) -> Path:
    if not value or Path(value).is_absolute() or ":" in value:
        raise ValueError("Adapter paths must be relative to the job root.")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("Adapter path escaped the job root.") from exc
    return path


def _validate_payload(payload: Dict[str, Any]) -> None:
    def walk(value: Any) -> Iterable[str]:
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str) and (
                    key.endswith("_path")
                    or key.endswith("_rel")
                    or key in {"filepath", "save_to", "source", "destination"}
                ):
                    yield item
                yield from walk(item)
        elif isinstance(value, list):
            for item in value:
                yield from walk(item)

    for item in walk(payload):
        if Path(item).is_absolute() or ":" in item or ".." in Path(item).parts:
            raise ValueError("Absolute or traversal paths are not accepted by the adapter.")


def _run(job_id: str, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    job = _job(job_id)
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(f"Unsupported allowlisted operation: {operation}")
    _validate_payload(payload)
    request_id = uuid.uuid4().hex
    request_path = job / "logs" / "adapter" / f"{request_id}.json"
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request = {
        "request_id": request_id,
        "adapter_id": CONFIG["adapter_id"],
        "adapter_version": ADAPTER_VERSION,
        "job_id": job_id,
        "job_root": str(job),
        "operation": operation,
        "payload": payload,
    }
    request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    command = [
        str(BLENDER),
        "--factory-startup",
        "--background",
        "--python",
        str(MODULE_ROOT / "blender_worker.py"),
        "--",
        "--request",
        str(request_path),
        "--io-pdx-root",
        CONFIG["io_pdx_mesh_root"],
    ]
    worker_env = os.environ.copy()
    worker_env["HOI4_WORKER_REQUEST"] = str(request_path)
    worker_env["HOI4_IO_PDX_ROOT"] = CONFIG["io_pdx_mesh_root"]
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        text=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=worker_env,
        timeout=1800,
        check=False,
    )
    output_path = job / "logs" / "adapter" / f"{request_id}.result.json"
    output_path.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(
            f"Blender worker failed with {completed.returncode}; "
            f"evidence: {output_path}"
        )
    result_lines = [line.strip() for line in completed.stdout.splitlines() if line.strip().startswith("{")]
    if not result_lines:
        raise RuntimeError(f"Blender worker returned no JSON result; evidence: {output_path}")
    try:
        # Blender can append its version banner to the same physical line as
        # the worker's JSON result. Decode the first complete JSON value and
        # ignore that non-JSON trailer instead of rejecting a successful job.
        result, _ = json.JSONDecoder().raw_decode(result_lines[-1])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Blender worker returned invalid JSON; evidence: {output_path}") from exc
    result["adapter"] = {
        "id": CONFIG["adapter_id"],
        "version": ADAPTER_VERSION,
        "request_id": request_id,
        "worker_log": str(output_path.relative_to(job)).replace("\\", "/"),
    }
    return result


def _texture_resize_for_job(job: Path, png: Path) -> tuple[int | None, int | None]:
    """Return a profile-bounded size while preserving the source aspect ratio."""

    if not PROFILE_CONFIG_PATH.exists():
        return None, None
    try:
        job_record = json.loads((job / "job.yaml").read_text(encoding="utf-8"))
        profile_name = job_record.get("profile")
        profiles = json.loads(PROFILE_CONFIG_PATH.read_text(encoding="utf-8")).get("profiles", {})
        max_dimension = profiles.get(profile_name, {}).get("texture_max_dimension")
        if not max_dimension:
            return None, None
        probe = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0:s=x",
                str(png),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=True,
        )
        width, height = (int(value) for value in probe.stdout.strip().split("x", 1))
        largest = max(width, height)
        if largest <= int(max_dimension):
            return None, None
        ratio = int(max_dimension) / largest
        return max(1, round(width * ratio)), max(1, round(height * ratio))
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError):
        return None, None


def _process_textures(job_id: str, blend_rel: str) -> Dict[str, Any]:
    """Extract PNGs in Blender, convert through the repo DDS tool, then relink."""

    extracted = _run(job_id, "process_textures", {"blend_rel": blend_rel})
    job = _job(job_id)
    converter = REPO_ROOT / ".agents" / "skills" / "hoi4-event-assets" / "tools" / "convert_to_dds.py"
    if not converter.exists():
        raise FileNotFoundError(converter)
    dds_map: Dict[str, str] = {}
    conversions = []
    for item in extracted.get("textures", []):
        png_rel = item["processed_png"]
        png = _relative(png_rel, job)
        dds_rel = f"textures/dds/{png.stem}.dds"
        dds = _relative(dds_rel, job)
        dds.parent.mkdir(parents=True, exist_ok=True)
        if dds.exists():
            try:
                dds.unlink()
            except OSError as exc:
                raise RuntimeError(f"Unable to replace existing DDS output: {dds}") from exc
        width, height = _texture_resize_for_job(job, png)
        converter_args = [
            sys.executable,
            str(converter),
            "--input",
            str(png),
            "--output",
            str(dds),
        ]
        if width is not None and height is not None:
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
        log = job / "logs" / "adapter" / f"dds_{len(conversions):03d}.log"
        log.write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0 or not dds.exists():
            raise RuntimeError(f"DDS conversion failed; evidence: {log}")
        dds_map[item["image"]] = dds_rel
        conversions.append(
            {
                "image": item["image"],
                "png": png_rel,
                "dds": dds_rel,
                "log": str(log.relative_to(job)).replace("\\", "/"),
                "width": width,
                "height": height,
            }
        )
    if dds_map:
        relinked = _run(
            job_id,
            "process_textures",
            {
                "blend_rel": blend_rel,
                "rewrite_to_dds": True,
                "dds_map": dds_map,
            },
        )
    else:
        relinked = {"textures": []}
    result = {
        "extracted": extracted,
        "conversions": conversions,
        "relinked": relinked,
        "backend": "repository convert_to_dds.py",
    }
    report = job / "blender" / "reports" / "textures_dds.json"
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


@mcp.tool()
def hoi4_blender_health(job_id: str) -> Dict[str, Any]:
    """Verify the locked Blender executable, addon, and job boundary."""

    return _run(job_id, "health", {})


@mcp.tool()
def hoi4_blender_prepare_candidate(
    job_id: str,
    source_rel: str,
    asset_kind: str,
    target_height_m: float,
    runtime_stem: str,
    runtime_entity_scale: float = 1.0,
    target_triangles: int = 0,
    excluded_provider_objects: list[str] | None = None,
    vanilla_reference: Dict[str, Any] | None = None,
    texture_source_rels: Dict[str, str] | None = None,
    geometry_source_rel: str = "",
    repair_before_reduction: bool = False,
    topology_weld_distance: float = 1e-5,
    max_runtime_footprint_m: float | None = None,
    runtime_footprint_policy: str = "reject",
) -> Dict[str, Any]:
    """Import, preserve, normalize, triangulate, material-tag, and checkpoint a candidate."""

    return _run(
        job_id,
        "prepare_candidate",
        {
            "source_rel": source_rel,
            "asset_kind": asset_kind,
            "target_height_m": target_height_m,
            "runtime_entity_scale": runtime_entity_scale,
            "runtime_stem": runtime_stem,
            "target_triangles": target_triangles,
            "excluded_provider_objects": excluded_provider_objects or [],
            "vanilla_reference": vanilla_reference or {},
            "texture_source_rels": texture_source_rels or {},
            "geometry_source_rel": geometry_source_rel,
            "repair_before_reduction": repair_before_reduction,
            "topology_weld_distance": topology_weld_distance,
            "max_runtime_footprint_m": max_runtime_footprint_m,
            "runtime_footprint_policy": runtime_footprint_policy,
        },
    )


@mcp.tool()
def hoi4_blender_inspect_scene(
    job_id: str,
    blend_rel: str,
    render_previews: bool = False,
    runtime_stem: str = "",
    action_name: str = "",
    preview_frame: int = -1,
    preview_view_names: list[str] | None = None,
) -> Dict[str, Any]:
    """Inspect a saved checkpoint, optionally writing review previews."""

    return _run(
        job_id,
        "inspect_scene",
        {
            "blend_rel": blend_rel,
            "render_previews": render_previews,
            "runtime_stem": runtime_stem,
            "action_name": action_name,
            "preview_frame": preview_frame,
            "preview_view_names": preview_view_names or [],
        },
    )


@mcp.tool()
def hoi4_blender_process_textures(
    job_id: str,
    blend_rel: str,
    rewrite_to_dds: bool = False,
    dds_map: Dict[str, str] | None = None,
    rename_images: bool = False,
) -> Dict[str, Any]:
    """Extract textures, or relink approved DDS maps in a bounded saved scene."""

    if not rewrite_to_dds:
        return _process_textures(job_id, blend_rel)
    return _run(
        job_id,
        "process_textures",
        {
            "blend_rel": blend_rel,
            "rewrite_to_dds": True,
            "dds_map": dds_map or {},
            "rename_images": rename_images,
        },
    )


@mcp.tool()
def hoi4_blender_bake_static_mesh_transforms(
    job_id: str,
    blend_rel: str,
    output_blend_rel: str,
    asset_kind: str,
    bounds_tolerance: float = 1e-5,
) -> Dict[str, Any]:
    """Bake transforms for approved static-building working meshes only."""

    return _run(
        job_id,
        "bake_static_mesh_transforms",
        {
            "blend_rel": blend_rel,
            "output_blend_rel": output_blend_rel,
            "asset_kind": asset_kind,
            "bounds_tolerance": bounds_tolerance,
        },
    )


@mcp.tool()
def hoi4_blender_partition_static_mesh_export_batches(
    job_id: str,
    blend_rel: str,
    output_blend_rel: str,
    asset_kind: str,
    max_export_vertices_per_batch: int = 60000,
) -> Dict[str, Any]:
    """Partition a static building into bounded material-backed PDX mesh streams."""

    return _run(
        job_id,
        "partition_static_mesh_export_batches",
        {
            "blend_rel": blend_rel,
            "output_blend_rel": output_blend_rel,
            "asset_kind": asset_kind,
            "max_export_vertices_per_batch": max_export_vertices_per_batch,
        },
    )


@mcp.tool()
def hoi4_blender_export_mesh(
    job_id: str,
    blend_rel: str,
    output_rel: str,
) -> Dict[str, Any]:
    """Export the approved collection through io_pdx_mesh."""

    return _run(
        job_id,
        "export_mesh",
        {"blend_rel": blend_rel, "output_rel": output_rel},
    )


@mcp.tool()
def hoi4_blender_export_animation(
    job_id: str,
    blend_rel: str,
    action_name: str,
    output_rel: str,
) -> Dict[str, Any]:
    """Export one audited Blender action through io_pdx_mesh."""

    return _run(
        job_id,
        "export_animation",
        {
            "blend_rel": blend_rel,
            "action_name": action_name,
            "output_rel": output_rel,
        },
    )


@mcp.tool()
def hoi4_blender_import_animation_action(
    job_id: str,
    blend_rel: str,
    source_rel: str,
    provenance_rel: str,
    checkpoint_rel: str,
    source_action_name: str,
    target_armature_name: str,
    target_action_name: str,
    source_kind: str,
    source_reference_id: str,
    source_sha256: str,
    source_armature_name: str = "",
) -> Dict[str, Any]:
    """Transfer one receipt-verified provider/professional action by exact source id."""

    return _run(
        job_id,
        "import_animation_action",
        {
            "blend_rel": blend_rel,
            "source_rel": source_rel,
            "provenance_rel": provenance_rel,
            "checkpoint_rel": checkpoint_rel,
            "source_action_name": source_action_name,
            "source_armature_name": source_armature_name,
            "target_armature_name": target_armature_name,
            "target_action_name": target_action_name,
            "source_kind": source_kind,
            "source_reference_id": source_reference_id,
            "source_sha256": source_sha256,
        },
    )


@mcp.tool()
def hoi4_blender_retime_animation_action(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_name: str,
    source_fps: float,
    target_fps: float,
) -> Dict[str, Any]:
    """Retiming one existing skeletal action between explicit frame rates."""

    return _run(
        job_id,
        "retime_animation_action",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_name": action_name,
            "source_fps": source_fps,
            "target_fps": target_fps,
        },
    )


@mcp.tool()
def hoi4_blender_author_locomotion_action(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_name: str = "Armature|Move|baselayer_WORKING",
) -> Dict[str, Any]:
    """Author and checkpoint an in-place locomotion action on the approved rig."""

    return _run(
        job_id,
        "author_locomotion_action",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_name": action_name,
        },
    )


@mcp.tool()
def hoi4_blender_author_humanoid_rig(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    rig_name: str = "",
) -> Dict[str, Any]:
    """Create the bounded HOI4 24-bone humanoid rig on approved geometry."""

    return _run(
        job_id,
        "author_humanoid_rig",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "rig_name": rig_name,
        },
    )


@mcp.tool()
def hoi4_blender_author_humanoid_actions(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_names: Dict[str, str] | None = None,
    fps: int = 24,
    fused_weapon_grip: bool = False,
) -> Dict[str, Any]:
    """Author humanoid actions, optionally preserving a fused two-hand weapon grip."""

    return _run(
        job_id,
        "author_humanoid_actions",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_names": action_names or {},
            "fps": fps,
            "fused_weapon_grip": fused_weapon_grip,
        },
    )


@mcp.tool()
def hoi4_blender_review_humanoid_components(
    job_id: str,
    blend_rel: str,
    component_indices: list[int],
    runtime_stem: str = "humanoid_component_review",
    view_names: list[str] | None = None,
    render_group: bool = False,
) -> Dict[str, Any]:
    """Render explicit loose-component indices highlighted over a dim humanoid."""

    return _run(
        job_id,
        "review_humanoid_components",
        {
            "blend_rel": blend_rel,
            "component_indices": component_indices,
            "runtime_stem": runtime_stem,
            "view_names": view_names or ["rear"],
            "render_group": render_group,
        },
    )


@mcp.tool()
def hoi4_blender_isolate_humanoid_weapon(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    weapon_component_indices: list[int],
    component_prefix: str,
    stock_component_indices: list[int] | None = None,
    stock_link_component_indices: list[int] | None = None,
    body_object_name: str = "humanoid_body",
    weapon_object_name: str = "humanoid_weapon",
    stock_x_fraction: float = 0.03,
    stock_y_front_offset_fraction: float = -0.18,
    stock_z_fraction: float = 0.64,
    aim_down_degrees: float = 2.0,
    stock_advance_m: float = 1.25,
    stock_link_advance_m: float = 0.55,
) -> Dict[str, Any]:
    """Isolate reviewed loose components and place the recovered weapon at the right shoulder."""

    return _run(
        job_id,
        "isolate_humanoid_weapon",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "weapon_component_indices": weapon_component_indices,
            "component_prefix": component_prefix,
            "stock_component_indices": stock_component_indices or [],
            "stock_link_component_indices": stock_link_component_indices or [],
            "body_object_name": body_object_name,
            "weapon_object_name": weapon_object_name,
            "stock_x_fraction": stock_x_fraction,
            "stock_y_front_offset_fraction": stock_y_front_offset_fraction,
            "stock_z_fraction": stock_z_fraction,
            "aim_down_degrees": aim_down_degrees,
            "stock_advance_m": stock_advance_m,
            "stock_link_advance_m": stock_link_advance_m,
        },
    )


@mcp.tool()
def hoi4_blender_attach_rigid_weapon_from_checkpoint(
    job_id: str,
    source_blend_rel: str,
    target_blend_rel: str,
    output_blend_rel: str,
    source_object_name: str,
    target_object_name: str,
    target_armature_name: str,
    parent_bone_name: str,
    create_weapon_bone_name: str = "",
    translation: list[float] | None = None,
    rotation_euler_degrees: list[float] | None = None,
    scale: list[float] | None = None,
    collision_policy: str = "reject",
    action_name: str = "",
    render_views: list[str] | None = None,
) -> Dict[str, Any]:
    """Append one named mesh checkpoint object and rigidly parent it to one explicit rig bone."""

    return _run(
        job_id,
        "attach_rigid_weapon_from_checkpoint",
        {
            "source_blend_rel": source_blend_rel,
            "target_blend_rel": target_blend_rel,
            "output_blend_rel": output_blend_rel,
            "source_object_name": source_object_name,
            "target_object_name": target_object_name,
            "target_armature_name": target_armature_name,
            "parent_bone_name": parent_bone_name,
            "create_weapon_bone_name": create_weapon_bone_name,
            "translation": translation or [0.0, 0.0, 0.0],
            "rotation_euler_degrees": rotation_euler_degrees or [0.0, 0.0, 0.0],
            "scale": scale or [1.0, 1.0, 1.0],
            "collision_policy": collision_policy,
            "action_name": action_name,
            "render_views": render_views or ["three_quarter"],
        },
    )


@mcp.tool()
def hoi4_blender_segment_creature_components(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    region_mode: str = "loose",
    rider_z_min_fraction: float = 0.72,
    rider_z_max_fraction: float = 1.0,
    rider_x_center_fraction: float = 0.5,
    rider_x_half_fraction: float = 0.38,
    rider_y_center_fraction: float = 0.5,
    rider_y_half_fraction: float = 0.42,
    rider_object_name: str = "elephant_rider_region",
    body_object_name: str = "elephant_body_region",
    component_prefix: str = "elephant_component",
) -> Dict[str, Any]:
    """Split a nonhumanoid candidate into loose, rider-region, or semantic spatial components."""

    return _run(
        job_id,
        "segment_creature_components",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "region_mode": region_mode,
            "rider_z_min_fraction": rider_z_min_fraction,
            "rider_z_max_fraction": rider_z_max_fraction,
            "rider_x_center_fraction": rider_x_center_fraction,
            "rider_x_half_fraction": rider_x_half_fraction,
            "rider_y_center_fraction": rider_y_center_fraction,
            "rider_y_half_fraction": rider_y_half_fraction,
            "rider_object_name": rider_object_name,
            "body_object_name": body_object_name,
            "component_prefix": component_prefix,
        },
    )


@mcp.tool()
def hoi4_blender_calibrate_creature_scale(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    rider_component_names: list[str],
    target_rider_runtime_height_m: float,
    runtime_entity_scale: float = 0.8,
) -> Dict[str, Any]:
    """Scale a creature and rider together so the rider matches the measured infantry runtime height."""

    return _run(
        job_id,
        "calibrate_creature_scale",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "rider_component_names": rider_component_names,
            "target_rider_runtime_height_m": target_rider_runtime_height_m,
            "runtime_entity_scale": runtime_entity_scale,
        },
    )


@mcp.tool()
def hoi4_blender_author_creature_rig(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    rider_component_names: list[str] | None = None,
    weight_mode: str = "semantic",
    rig_name: str = "",
    creature_rig_family: str = "elephant",
) -> Dict[str, Any]:
    """Create and checkpoint a bounded custom rig for a nonhumanoid creature candidate."""

    return _run(
        job_id,
        "author_creature_rig",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "rider_component_names": rider_component_names or [],
            "weight_mode": weight_mode,
            "rig_name": rig_name,
            "creature_rig_family": creature_rig_family,
        },
    )


@mcp.tool()
def hoi4_blender_author_creature_action(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_role: str,
    action_name: str,
    creature_rig_family: str = "elephant",
) -> Dict[str, Any]:
    """Author one real skeletal creature action and checkpoint its contact-checked result."""

    return _run(
        job_id,
        "author_creature_action",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_role": action_role,
            "action_name": action_name,
            "creature_rig_family": creature_rig_family,
        },
    )


@mcp.tool()
def hoi4_blender_correct_action_grounding(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_name: str,
    root_bone: str = "Hips",
) -> Dict[str, Any]:
    """Correct per-frame ground contact on one existing skeletal action."""

    return _run(
        job_id,
        "correct_action_grounding",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_name": action_name,
            "root_bone": root_bone,
        },
    )


@mcp.tool()
def hoi4_blender_offset_action_root(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_name: str,
    frame_start: int,
    frame_end: int,
    offset_source_units: float,
    axis_index: int = 1,
) -> Dict[str, Any]:
    """Apply one bounded root-location offset to an existing action frame range."""

    return _run(
        job_id,
        "offset_action_root",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_name": action_name,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "offset_source_units": offset_source_units,
            "axis_index": axis_index,
        },
    )


@mcp.tool()
def hoi4_blender_sanitize_runtime_candidate(
    job_id: str,
    blend_rel: str,
    output_blend_rel: str = "blender/checkpoints/07_runtime_candidate_sanitized.blend",
    target_height_m: Optional[float] = None,
) -> Dict[str, Any]:
    """Create a reviewable runtime checkpoint with bounded skin and material cleanup."""

    return _run(
        job_id,
        "sanitize_runtime_candidate",
        {
            "blend_rel": blend_rel,
            "output_blend_rel": output_blend_rel,
            "target_height_m": target_height_m,
        },
    )


@mcp.tool()
def hoi4_blender_reimport_export(
    job_id: str,
    mesh_rel: str,
    anim_rel: str = "",
    proof_name: str = "",
) -> Dict[str, Any]:
    """Reimport exported PDX assets and save proof into the job."""

    return _run(
        job_id,
        "reimport_export",
        {"mesh_rel": mesh_rel, "anim_rel": anim_rel, "proof_name": proof_name},
    )


@mcp.tool()
def hoi4_blender_save_checkpoint(
    job_id: str,
    blend_rel: str,
    stage: str,
) -> Dict[str, Any]:
    """Copy a verified checkpoint to a named stage without changing source data."""

    return _run(
        job_id,
        "save_checkpoint",
        {"blend_rel": blend_rel, "stage": stage},
    )


def main() -> None:
    if not os.environ.get("MESHY_API_KEY", "").strip():
        raise SystemExit("MESHY_API_KEY is missing; restart the shell or Codex after setting it.")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
