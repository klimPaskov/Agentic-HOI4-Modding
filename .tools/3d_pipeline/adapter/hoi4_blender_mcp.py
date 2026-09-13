"""Structured, job-root-bounded Blender MCP adapter.

The adapter intentionally exposes named operations instead of an arbitrary
Blender-Python tool. All caller paths are job-relative and all Blender work is
delegated to the checked-in worker with a locked executable and extension root.
"""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional

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
SOURCE_HASHES = CONFIG.get("source_files_sha256")
LOCAL_SOURCES = {path.name: path for path in MODULE_ROOT.glob("*.py")}
if not isinstance(SOURCE_HASHES, dict) or set(SOURCE_HASHES) != set(LOCAL_SOURCES):
    raise RuntimeError("Blender adapter source closure changed or is unverified; rebootstrap this target installation.")
for source_name, source_path in LOCAL_SOURCES.items():
    if hashlib.sha256(source_path.read_bytes()).hexdigest().lower() != str(SOURCE_HASHES[source_name]).lower():
        raise RuntimeError(f"Blender adapter source checksum changed: {source_name}; rebootstrap this target installation.")
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


def _prepare_namespace(job: Path, payload: Dict[str, Any]) -> tuple[Path, Dict[str, Any]]:
    """Isolate one prepare attempt; input and all fixed outputs remain in its child root."""
    namespace = payload.get("output_namespace_rel", "")
    if not namespace:
        return job, payload
    child = _relative(namespace, job)
    if child == job.resolve() or not child.is_dir():
        raise ValueError("Prepare namespace must be an existing strict child containing its input files.")
    if (child / "blender" / "checkpoints").exists() or (child / "blender" / "source").exists():
        raise ValueError("Prepare namespace already has checkpoints; choose a new attempt namespace.")
    rebased = dict(payload)
    def input_path(value: str) -> str:
        source = _relative(value, job)
        if not source.is_file():
            raise ValueError("Namespaced prepare input must be an existing file.")
        try:
            return source.relative_to(child).as_posix()
        except ValueError as exc:
            raise ValueError("Every prepare source must be inside the output namespace.") from exc
    for key in ("source_rel", "geometry_source_rel"):
        if rebased.get(key):
            rebased[key] = input_path(rebased[key])
    rebased["texture_source_rels"] = {key: input_path(value) for key, value in rebased.get("texture_source_rels", {}).items()}
    rebased.pop("output_namespace_rel", None)
    return child, rebased


def _run(job_id: str, operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    job = _job(job_id)
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(f"Unsupported allowlisted operation: {operation}")
    _validate_payload(payload)
    worker_job, worker_payload = _prepare_namespace(job, payload) if operation == "prepare_candidate" else (job, payload)
    request_id = uuid.uuid4().hex
    request_path = job / "logs" / "adapter" / f"{request_id}.json"
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request = {
        "request_id": request_id,
        "adapter_id": CONFIG["adapter_id"],
        "adapter_version": ADAPTER_VERSION,
        "job_id": job_id,
        "job_root": str(worker_job),
        "operation": operation,
        "payload": worker_payload,
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
    if worker_job != job:
        result["output_namespace_rel"] = worker_job.relative_to(job).as_posix()
        result["artifact_path_base"] = "All worker artifact paths are relative to output_namespace_rel; adapter logs remain relative to the registered job."
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
    converter = REPO_ROOT / ".agents" / "skills" / "hoi4-feature-assets" / "tools" / "convert_to_dds.py"
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
    geometry_object_name: str = "",
    dual_source_base_rig: bool = False,
    geometry_weight_mode: Literal["four_nearest", "nearest_face_interpolated", "automatic_bone_heat", "bone_distance"] = "four_nearest",
    source_armature_name: str = "",
    source_mesh_names: list[str] | None = None,
    preserve_geometry_topology: bool = False,
    repair_before_reduction: bool = False,
    topology_weld_distance: float = 1e-5,
    max_runtime_footprint_m: float | None = None,
    runtime_footprint_policy: str = "reject",
    output_namespace_rel: str = "",
) -> Dict[str, Any]:
    """Prepare a candidate; optional output_namespace_rel isolates all fixed outputs.

    All sources must lie inside that existing child, with no previous checkpoints.
    Pass input paths relative to the registered job; returned worker artifact paths
    are relative to the explicitly returned output_namespace_rel.
    """

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
            "geometry_object_name": geometry_object_name,
            "dual_source_base_rig": dual_source_base_rig,
            "geometry_weight_mode": geometry_weight_mode,
            "source_armature_name": source_armature_name,
            "source_mesh_names": source_mesh_names or [],
            "preserve_geometry_topology": preserve_geometry_topology,
            "repair_before_reduction": repair_before_reduction,
            "topology_weld_distance": topology_weld_distance,
            "max_runtime_footprint_m": max_runtime_footprint_m,
            "runtime_footprint_policy": runtime_footprint_policy,
            "output_namespace_rel": output_namespace_rel,
        },
    )


@mcp.tool()
def hoi4_blender_inspect_scene(
    job_id: str,
    blend_rel: str,
    render_previews: bool = False,
    runtime_stem: str = "",
    action_name: str = "",
    target_armature_name: str = "",
    preview_frame: int = -1,
    preview_view_names: list[str] | None = None,
    mesh_region: dict[str, Any] | None = None,
    material_visibility: dict[str, Any] | None = None,
    include_action_channels: bool = False,
    expected_source_sha256: str = "",
    preview_region: Dict[str, Any] | None = None,
    preview_resolution: int = 512,
    evaluated_frames: list[int] | None = None,
) -> Dict[str, Any]:
    """Inspect a checkpoint; optional hash-bound mesh_region or action-channel inventory remains read-only."""

    return _run(
        job_id,
        "inspect_scene",
        {
            "blend_rel": blend_rel,
            "render_previews": render_previews,
            "runtime_stem": runtime_stem,
            "action_name": action_name,
            "evaluated_frames": evaluated_frames,
            "target_armature_name": target_armature_name,
            "preview_frame": preview_frame,
            "preview_view_names": preview_view_names or [],
            "preview_region": preview_region,
            "preview_resolution": preview_resolution,
            "expected_source_sha256": expected_source_sha256,
            **({"mesh_region": mesh_region} if mesh_region is not None else {}),
            **({"material_visibility": material_visibility, "expected_source_sha256": expected_source_sha256} if material_visibility is not None else {}),
            **({"include_action_channels": True, "expected_source_sha256": expected_source_sha256} if include_action_channels else {}),
        },
    )


@mcp.tool()
def hoi4_blender_review_humanoid_components(
    job_id: str,
    blend_rel: str,
    expected_source_sha256: str,
    mesh_name: str,
    render_group: bool = True,
    component_ids: list[str] | None = None,
    component_offset: int = 0,
    component_limit: int = 16,
    preview_view_names: list[str] | None = None,
) -> Dict[str, Any]:
    """Catalog loose source-index components and render bounded labelled group evidence without changing the Blend."""

    return _run(
        job_id,
        "review_humanoid_components",
        {
            "blend_rel": blend_rel,
            "expected_source_sha256": expected_source_sha256,
            "mesh_name": mesh_name,
            "render_group": render_group,
            "component_ids": component_ids or [],
            "component_offset": component_offset,
            "component_limit": component_limit,
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
def hoi4_blender_inspect_mesh_winding(
    job_id: str, blend_rel: str, expected_source_sha256: str, target_mesh_names: list[str],
) -> Dict[str, Any]:
    """Read hashed source-index and exact-position winding diagnostics without mutation."""
    return _run(job_id, "inspect_mesh_winding", {
        "blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256, "target_mesh_names": target_mesh_names,
    })


@mcp.tool()
def hoi4_blender_repair_mesh_winding(
    job_id: str, blend_rel: str, expected_source_sha256: str, checkpoint_rel: str,
    target_armature_name: str, target_mesh_names: list[str],
) -> Dict[str, Any]:
    """Preserve geometry/weights/actions and correct only proven coherent component orientation."""
    return _run(job_id, "repair_mesh_winding", {
        "blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256,
        "checkpoint_rel": checkpoint_rel, "target_armature_name": target_armature_name, "target_mesh_names": target_mesh_names,
    })


@mcp.tool()
def hoi4_blender_inspect_fitted_humanoid_source(
    job_id: str, blend_rel: str, expected_source_sha256: str, mesh_name: str, report_rel: str,
) -> Dict[str, Any]:
    """Inspect exact world vertices/topology of one hashed existing humanoid source."""
    return _run(job_id, "inspect_fitted_humanoid_source", {
        "blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256,
        "mesh_name": mesh_name, "report_rel": report_rel,
    })


@mcp.tool()
def hoi4_blender_author_fitted_humanoid_rig(
    job_id: str, blend_rel: str, expected_source_sha256: str,
    spec_rel: str, expected_spec_sha256: str, checkpoint_rel: str,
) -> Dict[str, Any]:
    """Apply explicitly measured bones/weights from a SHA-bound declarative spec."""
    return _run(job_id, "author_fitted_humanoid_rig", {
        "blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256,
        "spec_rel": spec_rel, "expected_spec_sha256": expected_spec_sha256, "checkpoint_rel": checkpoint_rel,
    })


@mcp.tool()
def hoi4_blender_author_fitted_humanoid_action(
    job_id: str, blend_rel: str, expected_source_sha256: str,
    spec_rel: str, expected_spec_sha256: str, checkpoint_rel: str,
) -> Dict[str, Any]:
    """Author and bake explicit role keys on an existing fitted skeletal rig."""
    return _run(job_id, "author_fitted_humanoid_action", {
        "blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256,
        "spec_rel": spec_rel, "expected_spec_sha256": expected_spec_sha256, "checkpoint_rel": checkpoint_rel,
    })


@mcp.tool()
def hoi4_blender_partition_skeletal_mesh_export_batches(
    job_id: str,
    blend_rel: str,
    expected_source_sha256: str,
    checkpoint_rel: str,
    target_armature_name: str,
    target_mesh_names: list[str],
    max_export_vertices_per_batch: int = 24000,
) -> Dict[str, Any]:
    """Partition a hashed existing skeletal source using identical material copies only. Reconcile image-user additions only from transaction-created equivalent clones on exact owned mesh slots; image content, original consumers, and retention remain exact."""
    return _run(job_id, "partition_skeletal_mesh_export_batches", {
        "blend_rel": blend_rel,
        "expected_source_sha256": expected_source_sha256,
        "checkpoint_rel": checkpoint_rel,
        "target_armature_name": target_armature_name,
        "target_mesh_names": target_mesh_names,
        "max_export_vertices_per_batch": max_export_vertices_per_batch,
    })


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
def hoi4_blender_promote_accepted_reimport(
    job_id: str,
    blend_rel: str,
    expected_source_sha256: str,
    validation_rel: str,
    expected_validation_sha256: str,
    checkpoint_rel: str,
    target_armature_name: str,
    target_mesh_names: list[str],
    mesh_rel: str,
    expected_mesh_sha256: str,
    anim_rel: str,
    expected_anim_sha256: str,
) -> Dict[str, Any]:
    """Copy one hash-bound animated reimport proof with metadata-only working approval.

    Require its complete receipt and immutable source .blend/.mesh/.anim hashes,
    one exact rig and 1-512 exact meshes, and a new sibling checkpoint. Preserve
    geometry, materials, weights, bones, actions and scale through save/reopen.
    This does not import actions, author geometry, convert or approve exports.
    """
    return _run(job_id, "promote_accepted_reimport", {
        "blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256,
        "validation_rel": validation_rel, "expected_validation_sha256": expected_validation_sha256,
        "checkpoint_rel": checkpoint_rel, "target_armature_name": target_armature_name,
        "target_mesh_names": list(target_mesh_names), "mesh_rel": mesh_rel,
        "expected_mesh_sha256": expected_mesh_sha256, "anim_rel": anim_rel,
        "expected_anim_sha256": expected_anim_sha256,
    })


@mcp.tool()
def hoi4_blender_author_locator(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    target_armature_name: str,
    parent_bone: str,
    locator_name: str,
    bone_local_position: tuple[float, float, float],
    bone_local_rotation_xyzw: tuple[float, float, float, float],
) -> Dict[str, Any]:
    """Create/update one job-owned bone-parented Empty, never geometry or motion.

    Supply a measured bone-head-local position in checkpoint units and a unit
    quaternion in x,y,z,w order (Blender axes). The exact rig/bone must exist.
    The output must be a new .blend beside the input checkpoint; existing or
    foreign locator names, parents, and checkpoint outputs are rejected.
    """

    return _run(
        job_id,
        "author_locator",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "target_armature_name": target_armature_name,
            "parent_bone": parent_bone,
            "locator_name": locator_name,
            "bone_local_position": list(bone_local_position),
            "bone_local_rotation_xyzw": list(bone_local_rotation_xyzw),
        },
    )


@mcp.tool()
def hoi4_blender_export_mesh(
    job_id: str,
    blend_rel: str,
    output_rel: str,
    split_verts: bool = False,
    checkpoint_rel: str | None = None,
) -> Dict[str, Any]:
    """Export the approved collection through io_pdx_mesh."""

    return _run(
        job_id,
        "export_mesh",
        {"blend_rel": blend_rel, "output_rel": output_rel, "split_verts": split_verts, "checkpoint_rel": checkpoint_rel},
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
    source_kind: Literal["meshy_animate", "meshy_text_to_motion", "professional_source"],
    source_reference_id: str,
    source_sha256: str,
    bone_chains: Dict[str, list[str]] | None = None,
    promote_audited_target: bool = False,
    source_armature_name: str = "",
    root_scale_reference: Dict[str, list[str]] | None = None,
) -> Dict[str, Any]:
    """Transfer one receipt-verified provider/professional skeletal action by its exact source id.

    Source ids may include balanced parenthetical qualifiers used by ordinary FBX action names.
    The destination action remains a separately validated safe runtime identifier.
    """

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
            "bone_chains": bone_chains or {},
            "root_scale_reference": root_scale_reference,
            "promote_audited_target": promote_audited_target,
        },
    )


@mcp.tool()
def hoi4_blender_retime_animation_action(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_name: str,
    target_armature_name: str,
    source_fps: float,
    target_fps: float,
) -> Dict[str, Any]:
    """Retime one verified-source action without changing or replacing its skeletal motion."""

    return _run(
        job_id,
        "retime_animation_action",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_name": action_name,
            "target_armature_name": target_armature_name,
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
def hoi4_blender_patch_existing_humanoid_action_phases(
    job_id: str, blend_rel: str, checkpoint_rel: str,
    expected_source_sha256: str, expected_action_sha256: str,
    target_armature_name: str, source_action_name: str, target_action_name: str,
    semantic_role: str, source_fps: int, source_fps_base: float,
    frame_start: int, frame_end: int, phase_frames: dict[str, int],
    allowed_bones: list[str], motion_bone_chain: list[str], bone_patches: dict[str, Any],
) -> Dict[str, Any]:
    """Clone an existing action and apply explicit authorized manual bone-phase keys in a new sibling; no geometry edits or semantic approval. Reopen receipts prove exact image content and consumers; all image datablocks and packed bytes remain exact, allowing only consumer release caused by accepted removed orphan materials."""
    return _run(job_id, "patch_existing_humanoid_action_phases", {
        "blend_rel": blend_rel, "checkpoint_rel": checkpoint_rel,
        "expected_source_sha256": expected_source_sha256, "expected_action_sha256": expected_action_sha256,
        "target_armature_name": target_armature_name, "source_action_name": source_action_name, "target_action_name": target_action_name,
        "semantic_role": semantic_role, "source_fps": source_fps, "source_fps_base": source_fps_base,
        "frame_start": frame_start, "frame_end": frame_end, "phase_frames": phase_frames,
        "allowed_bones": allowed_bones, "motion_bone_chain": motion_bone_chain, "bone_patches": bone_patches,
    })


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
def hoi4_blender_inspect_mesh_landmarks(job_id: str, blend_rel: str, expected_source_sha256: str, report_rel: str, mesh_names: list[str]) -> Dict[str, Any]:
    """Write a bounded hash-bound rest-vertex/bone inventory; return compact file evidence only."""
    return _run(job_id, "inspect_mesh_landmarks", {"blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256, "report_rel": report_rel, "mesh_names": mesh_names})


@mcp.tool()
def hoi4_blender_repair_explicit_skin(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, skin_spec_rel: str, expected_skin_spec_sha256: str) -> Dict[str, Any]:
    """Repair exact reviewed vertex weights; preserve all other fingerprints and reopen proof."""
    return _run(job_id, "repair_explicit_skin", {"blend_rel": blend_rel, "checkpoint_rel": checkpoint_rel, "expected_source_sha256": expected_source_sha256, "skin_spec_rel": skin_spec_rel, "expected_skin_spec_sha256": expected_skin_spec_sha256})


@mcp.tool()
def hoi4_blender_preview_explicit_skin_selection(job_id: str, blend_rel: str, expected_source_sha256: str, selection_spec_rel: str, expected_selection_spec_sha256: str) -> Dict[str, Any]:
    """Read-only exact source-index rest-mesh highlight; red full faces, cyan mixed boundary."""
    return _run(job_id, "preview_explicit_skin_selection", {"blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256, "selection_spec_rel": selection_spec_rel, "expected_selection_spec_sha256": expected_selection_spec_sha256})


@mcp.tool()
def hoi4_blender_author_measured_creature_rig(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, rig_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Author explicit measured bones and ordered spatial weights on a new sibling checkpoint.

    rig_spec keys: name, bones [{name,parent,head,tail,roll_degrees?,deform?}],
    weight_regions [{name,min,max,bones,rigid}], body_triangle_target (0 disables),
    repair_boundaries (boolean). World-space coordinates; first matching region.
    """
    return _run(job_id, "author_measured_creature_rig", {"blend_rel": blend_rel, "checkpoint_rel": checkpoint_rel, "expected_source_sha256": expected_source_sha256, "rig_spec": rig_spec})


@mcp.tool()
def hoi4_blender_attach_rigid_component(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, target_armature_name: str, triangle_ceiling: int, component_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Add explicit closed triangular component geometry rigidly bound to one existing bone.

    component_spec: name, bone, material (existing working material), vertices
    (world coordinates), triangles (indices), loop_uvs (one UV per face corner).
    All source meshes are preserved and total triangles may not exceed ceiling.
    """
    return _run(job_id, "attach_rigid_component", {"blend_rel": blend_rel, "checkpoint_rel": checkpoint_rel, "expected_source_sha256": expected_source_sha256, "target_armature_name": target_armature_name, "triangle_ceiling": triangle_ceiling, "component_spec": component_spec})


@mcp.tool()
def hoi4_blender_author_measured_creature_action(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, target_armature_name: str, action_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new explicit articulated action from caller-authored phases; no canned motion.

    action_spec: name, role, fps, frame_start, frame_end, loop, root_bone,
    ground_contact (per_frame_lowest_point_1mm or none), phases [{name,frame}],
    keys {bone:[{frame,rotation_degrees:[x,y,z],location:[x,y,z]}]}.
    Rotations are absolute local XYZ Euler degrees converted to quaternions.
    Keys must include every phase; unlisted bones use identity. Source actions
    are retained, new actions require semantic/deformation review and reimport.
    """
    return _run(job_id, "author_measured_creature_action", {"blend_rel": blend_rel, "checkpoint_rel": checkpoint_rel, "expected_source_sha256": expected_source_sha256, "target_armature_name": target_armature_name, "action_spec": action_spec})


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
    target_armature_name: str,
    grounding_policy: Literal["per_frame_root_contact_zero_clearance"],
    root_bone: str = "Hips",
    excluded_contact_bones: list[str] | None = None,
) -> Dict[str, Any]:
    """Apply bounded root/contact correction to a verified-source action; never replace body motion."""

    return _run(
        job_id,
        "correct_action_grounding",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_name": action_name,
            "target_armature_name": target_armature_name,
            "grounding_policy": grounding_policy,
            "root_bone": root_bone,
            "excluded_contact_bones": excluded_contact_bones or [],
        },
    )


@mcp.tool()
def hoi4_blender_import_bvh_animation_action(
    job_id: str,
    blend_rel: str,
    source_rel: str,
    provenance_rel: str,
    checkpoint_rel: str,
    source_action_name: str,
    target_armature_name: str,
    target_action_name: str,
    semantic_role: str,
    source_reference_id: str,
    source_sha256: str,
    source_fps: float,
    target_fps: float,
    bone_chains: Dict[str, list[str]],
    root_motion_policy: Literal["in_place_xy_preserve_z"],
    global_scale: float = 1.0,
    axis_forward: Literal["X", "Y", "Z", "-X", "-Y", "-Z"] = "-Z",
    axis_up: Literal["X", "Y", "Z", "-X", "-Y", "-Z"] = "Y",
    promote_audited_target: bool = False,
) -> Dict[str, Any]:
    """Native-import and retarget one receipt-verified professional BVH action."""

    return _run(
        job_id,
        "import_bvh_animation_action",
        {
            "blend_rel": blend_rel,
            "source_rel": source_rel,
            "provenance_rel": provenance_rel,
            "checkpoint_rel": checkpoint_rel,
            "source_action_name": source_action_name,
            "target_armature_name": target_armature_name,
            "target_action_name": target_action_name,
            "semantic_role": semantic_role,
            "source_reference_id": source_reference_id,
            "source_sha256": source_sha256,
            "source_fps": source_fps,
            "target_fps": target_fps,
            "bone_chains": bone_chains,
            "root_motion_policy": root_motion_policy,
            "global_scale": global_scale,
            "axis_forward": axis_forward,
            "axis_up": axis_up,
            "promote_audited_target": promote_audited_target,
        },
    )


@mcp.tool()
def hoi4_blender_prepare_export_coordinate_checkpoint(
    job_id: str,
    blend_rel: str,
    checkpoint_rel: str,
    action_name: str,
    target_armature_name: str,
) -> Dict[str, Any]:
    """Checkpoint one accepted action in the existing PDX export coordinate system."""

    return _run(
        job_id,
        "prepare_export_coordinate_checkpoint",
        {
            "blend_rel": blend_rel,
            "checkpoint_rel": checkpoint_rel,
            "action_name": action_name,
            "target_armature_name": target_armature_name,
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
    weight_only: bool = False,
    max_influences_per_vertex: int = 4,
) -> Dict[str, Any]:
    """Create a runtime checkpoint; weight_only preserves geometry, rig, weapons, and materials."""

    return _run(
        job_id,
        "sanitize_runtime_candidate",
        {
            "blend_rel": blend_rel,
            "output_blend_rel": output_blend_rel,
            "target_height_m": target_height_m,
            "weight_only": weight_only,
            "max_influences_per_vertex": max_influences_per_vertex,
        },
    )


@mcp.tool()
def hoi4_blender_reimport_export(
    job_id: str,
    mesh_rel: str,
    anim_rel: str = "",
    proof_name: str = "",
    stage_default_textures: bool = True,
) -> Dict[str, Any]:
    """Reimport exported PDX assets and save proof into the job."""

    return _run(
        job_id,
        "reimport_export",
        {"mesh_rel": mesh_rel, "anim_rel": anim_rel, "proof_name": proof_name, "stage_default_textures": stage_default_textures},
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



@mcp.tool()
def hoi4_blender_repair_explicit_mesh_winding(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, mesh_name: str, face_indices: list[int], angular_tolerance_degrees: float = 0.25) -> Dict[str, Any]:
    """Flip an exact reviewed face list in a new hash-bound sibling; preserve corners, weights, rig and actions."""
    return _run(job_id, "repair_explicit_mesh_winding", {"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"mesh_name":mesh_name,"face_indices":face_indices,"angular_tolerance_degrees":angular_tolerance_degrees})

@mcp.tool()
def hoi4_blender_ground_existing_action(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, target_armature_name: str, source_action_name: str, expected_action_sha256: str, target_action_name: str, root_bone: str, excluded_contact_bones: list[str] | None = None) -> Dict[str, Any]:
    """Copy one reviewed skeletal action and correct true-root location in pure world Z."""
    return _run(job_id, "ground_existing_action", {"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"target_armature_name":target_armature_name,"source_action_name":source_action_name,"expected_action_sha256":expected_action_sha256,"target_action_name":target_action_name,"root_bone":root_bone,"excluded_contact_bones":excluded_contact_bones or []})


@mcp.tool()
def hoi4_blender_repair_explicit_mesh_patch(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, patch_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Apply an exact reviewed local face/vertex patch; no inferred fill, rig replacement or source overwrite."""
    return _run(job_id,"repair_explicit_mesh_patch",{"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"patch_spec":patch_spec})


@mcp.tool()
def hoi4_blender_edit_explicit_mesh_vertices(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, mesh_name: str, target_armature_name: str, vertex_edits: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply exact world positions/normalized existing deform-bone weights; verify readback and save/reopen."""
    return _run(job_id,"edit_explicit_mesh_vertices",{"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"mesh_name":mesh_name,"target_armature_name":target_armature_name,"vertex_edits":vertex_edits})


@mcp.tool()
def hoi4_blender_bind_existing_pdx_material(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, target_mesh_names: list[str], source_material_name: str, material_name: str, material_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Bind unique hash-bound PDX maps to exact existing slots; preserve source materials and mesh/rig/actions."""
    return _run(job_id,"bind_existing_pdx_material",{"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"target_mesh_names":target_mesh_names,"source_material_name":source_material_name,"material_name":material_name,"material_spec":material_spec})


@mcp.tool()
def hoi4_blender_repair_explicit_mesh_winding_batch(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, repair_spec_rel: str, expected_repair_spec_sha256: str) -> Dict[str, Any]:
    """Flip only hash-bound per-mesh face lists in one new sibling; exact preconditions, full scene proof and <=0.5 degree native/reopen normals."""
    return _run(job_id, "repair_explicit_mesh_winding_batch", {"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"repair_spec_rel":repair_spec_rel,"expected_repair_spec_sha256":expected_repair_spec_sha256})


@mcp.tool()
def hoi4_blender_repair_explicit_skin_batch(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, repair_spec_rel: str, expected_repair_spec_sha256: str) -> Dict[str, Any]:
    """Replace only exact hash-bound per-mesh expected/replacement weight records; one immutable-source sibling transaction, positive normalized <=4 influences."""
    return _run(job_id, "repair_explicit_skin_batch", {"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"repair_spec_rel":repair_spec_rel,"expected_repair_spec_sha256":expected_repair_spec_sha256})


@mcp.tool()
def hoi4_blender_replace_explicit_corner_normals(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, repair_spec_rel: str, expected_repair_spec_sha256: str) -> Dict[str, Any]:
    """Replace explicit mesh/face/corner/vertex unit directions with expected-before proof; preserve every unselected raw/decoded corner exactly in one new sibling."""
    return _run(job_id, "replace_explicit_corner_normals", {"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"repair_spec_rel":repair_spec_rel,"expected_repair_spec_sha256":expected_repair_spec_sha256})


@mcp.tool()
def hoi4_blender_repair_explicit_vertex_remap(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, remap_spec: Dict[str, Any], angular_tolerance_degrees: float = 0.25) -> Dict[str, Any]:
    """Exact source-vertex fan copies/coincident aliases with explicit corner remaps; no inferred weld or weights."""
    return _run(job_id,"repair_explicit_vertex_remap",{"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"remap_spec":remap_spec,"angular_tolerance_degrees":angular_tolerance_degrees})


@mcp.tool()
def hoi4_blender_rotate_existing_assembly_yaw(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, target_armature_name: str, object_names: list[str], action_names: list[str], yaw_degrees: float) -> Dict[str, Any]:
    """Rigid cardinal working-assembly yaw with every requested action frame verified; protected source objects excluded."""
    return _run(job_id,"rotate_existing_assembly_yaw",{"blend_rel":blend_rel,"checkpoint_rel":checkpoint_rel,"expected_source_sha256":expected_source_sha256,"target_armature_name":target_armature_name,"object_names":object_names,"action_names":action_names,"yaw_degrees":yaw_degrees})


@mcp.tool()
def hoi4_blender_collapse_identity_leaf_joints(job_id: str, blend_rel: str, checkpoint_rel: str, expected_source_sha256: str, target_armature_name: str, target_mesh_names: list[str], bone_aliases: Dict[str, str], action_hashes: Dict[str, str]) -> Dict[str, Any]:
    """Collapse only constant-identity leaves into direct parents, proving all-frame skin/action/locator preservation."""
    return _run(job_id, "collapse_identity_leaf_joints", {"blend_rel": blend_rel, "checkpoint_rel": checkpoint_rel, "expected_source_sha256": expected_source_sha256, "target_armature_name": target_armature_name, "target_mesh_names": target_mesh_names, "bone_aliases": bone_aliases, "action_hashes": action_hashes})


@mcp.tool()
def hoi4_blender_inspect_animation_source(job_id: str, source_rel: str, source_sha256: str) -> Dict[str, Any]:
    """Read standalone FBX skeleton/action identity in a disposable scene without a target checkpoint."""
    return _run(job_id, "inspect_animation_source", {"source_rel": source_rel, "source_sha256": source_sha256})


if __name__ == "__main__":
    main()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
