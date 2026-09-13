"""Client for the repository-owned allowlisted Blender MCP adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from lib.mcp_stdio import MCPRouteError, call_stdio
from lib.paths import resolve_job_root


def _structured(result: Dict[str, Any]) -> Dict[str, Any]:
    structured = result.get("structuredContent", {})
    if isinstance(structured, dict):
        if isinstance(structured.get("result"), dict):
            return structured["result"]
        if structured:
            return structured
    for block in result.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text", "")
            try:
                value = json.loads(text)
            except (TypeError, json.JSONDecodeError):
                continue
            if isinstance(value, dict):
                return value
    return result


class BlenderAdapterClient:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.wrapper = self.repo_root / ".tools" / "3d_pipeline" / "wrappers" / "run_blender_hoi4_adapter.cmd"
        if not self.wrapper.exists():
            raise FileNotFoundError(self.wrapper)

    def call(self, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        arguments = dict(arguments)
        raw_job_id = arguments.get("job_id")
        if isinstance(raw_job_id, str) and Path(raw_job_id).name == raw_job_id:
            config = json.loads(
                (self.repo_root / ".tools/3d_pipeline/config/blender_hoi4_adapter.json").read_text(
                    encoding="utf-8"
                )
            )
            configured_root = Path(config["job_root"]).resolve()
            arguments["job_id"] = resolve_job_root(raw_job_id).relative_to(configured_root).as_posix()
        command = ["cmd.exe", "/d", "/c", "call", str(self.wrapper)]
        result: Optional[Dict[str, Any]] = None
        read_only_tools = {"hoi4_blender_health", "hoi4_blender_inspect_scene", "hoi4_blender_inspect_mesh_landmarks", "hoi4_blender_inspect_mesh_winding", "hoi4_blender_inspect_fitted_humanoid_source", "hoi4_blender_review_humanoid_components", "hoi4_blender_inspect_animation_source", "hoi4_blender_preview_explicit_skin_selection"}
        attempt_limit = 3 if tool in read_only_tools else 1
        for attempt in range(attempt_limit):
            try:
                result = call_stdio(
                    command,
                    tool=tool,
                    arguments=arguments,
                    timeout_seconds=1800,
                    cwd=self.repo_root,
                )
                break
            except MCPRouteError as exc:
                if attempt == attempt_limit - 1:
                    if tool not in read_only_tools:
                        receipts = self._matching_mutation_receipts(tool, arguments)
                        raise MCPRouteError(f"Mutation response uncertain; no automatic retry for {tool}. Inspect saved checkpoint/report before any new call. Matching adapter request evidence: {receipts}. Transport: {exc}") from exc
                    raise
        if result is None:
            raise RuntimeError(f"Blender adapter returned no result for {tool}.")
        if result.get("isError"):
            raise RuntimeError(str(_structured(result)))
        value = _structured(result)
        if "error" in value:
            raise RuntimeError(str(value))
        return value

    def _matching_mutation_receipts(self, tool: str, arguments: Dict[str, Any]) -> list[dict[str, Any]]:
        """Read bounded matching job-local request headers; never replay a mutation."""
        try:
            config = json.loads((self.repo_root / ".tools/3d_pipeline/config/blender_hoi4_adapter.json").read_text(encoding="utf-8"))
            job_id = arguments.get("job_id", "")
            if not isinstance(job_id, str) or not job_id or Path(job_id).is_absolute() or ":" in job_id or ".." in Path(job_id).parts:
                return []
            root = Path(config["job_root"]).resolve()
            overrides = config.get("job_overrides", {})
            job = Path(overrides.get(job_id, root / job_id)).resolve()
            if job_id not in overrides:
                job.relative_to(root)
            directory = job / "logs/adapter"
            candidates = sorted((p for p in directory.glob("*.json") if not p.name.endswith(".result.json")), key=lambda p: p.stat().st_mtime, reverse=True)[:16]
            expected = {k: v for k, v in arguments.items() if k != "job_id"}
            result = []
            for path in candidates:
                path.resolve().relative_to(job)
                if path.stat().st_size > 16_000_000:
                    continue
                request = json.loads(path.read_text(encoding="utf-8"))
                payload = request.get("payload", {})
                if request.get("operation") == tool.removeprefix("hoi4_blender_") and all(payload.get(k) == v for k, v in expected.items()):
                    result.append({"request_id": request.get("request_id", path.stem), "request_rel": path.relative_to(job).as_posix(), "worker_result_exists": path.with_suffix(".result.json").exists()})
            return result
        except (OSError, ValueError, KeyError, TypeError):
            return []

    def health(self, job_id: str) -> Dict[str, Any]:
        return self.call("hoi4_blender_health", {"job_id": job_id})

    def prepare_candidate(
        self,
        job_id: str,
        *,
        source_rel: str,
        asset_kind: str,
        target_height_m: float,
        runtime_stem: str,
        runtime_entity_scale: float = 1.0,
        target_triangles: int = 0,
        excluded_provider_objects: Optional[list[str]] = None,
        vanilla_reference: Optional[Dict[str, Any]] = None,
        texture_source_rels: Optional[Dict[str, str]] = None,
        geometry_source_rel: Optional[str] = None,
        geometry_object_name: str = "",
        dual_source_base_rig: bool = False,
        geometry_weight_mode: Literal[
            "four_nearest",
            "nearest_face_interpolated",
            "automatic_bone_heat",
            "bone_distance",
        ] = "four_nearest",
        source_armature_name: str = "",
        source_mesh_names: Optional[list[str]] = None,
        preserve_geometry_topology: bool = False,
        repair_before_reduction: bool = False,
        topology_weld_distance: float = 1e-5,
        max_runtime_footprint_m: Optional[float] = None,
        runtime_footprint_policy: str = "reject",
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_prepare_candidate",
            {
                "job_id": job_id,
                "source_rel": source_rel,
                "asset_kind": asset_kind,
                "target_height_m": target_height_m,
                "runtime_entity_scale": runtime_entity_scale,
                "runtime_stem": runtime_stem,
                "target_triangles": target_triangles,
                "excluded_provider_objects": excluded_provider_objects or [],
                "vanilla_reference": vanilla_reference or {},
                "texture_source_rels": texture_source_rels or {},
                "geometry_source_rel": geometry_source_rel or "",
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
            },
        )

    def process_textures(
        self,
        job_id: str,
        blend_rel: str,
        *,
        rewrite_to_dds: bool = False,
        dds_map: Optional[Dict[str, str]] = None,
        rename_images: bool = False,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_process_textures",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "rewrite_to_dds": rewrite_to_dds,
                "dds_map": dds_map or {},
                "rename_images": rename_images,
            },
        )

    def promote_accepted_reimport(
        self,
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
        return self.call("hoi4_blender_promote_accepted_reimport", {
            "job_id": job_id, "blend_rel": blend_rel, "expected_source_sha256": expected_source_sha256,
            "validation_rel": validation_rel, "expected_validation_sha256": expected_validation_sha256,
            "checkpoint_rel": checkpoint_rel, "target_armature_name": target_armature_name,
            "target_mesh_names": list(target_mesh_names), "mesh_rel": mesh_rel,
            "expected_mesh_sha256": expected_mesh_sha256, "anim_rel": anim_rel,
            "expected_anim_sha256": expected_anim_sha256,
        })

    def author_locator(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        target_armature_name: str,
        parent_bone: str,
        locator_name: str,
        bone_local_position: tuple[float, float, float],
        bone_local_rotation_xyzw: tuple[float, float, float, float],
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_author_locator",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "target_armature_name": target_armature_name,
                "parent_bone": parent_bone,
                "locator_name": locator_name,
                "bone_local_position": list(bone_local_position),
                "bone_local_rotation_xyzw": list(bone_local_rotation_xyzw),
            },
        )

    def export_mesh(self, job_id: str, blend_rel: str, output_rel: str, split_verts: bool = False) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_export_mesh",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "output_rel": output_rel,
                "split_verts": split_verts,
            },
        )

    def export_animation(
        self,
        job_id: str,
        blend_rel: str,
        action_name: str,
        output_rel: str,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_export_animation",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "action_name": action_name,
                "output_rel": output_rel,
            },
        )

    def author_locomotion_action(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        action_name: str = "Armature|Move|baselayer_WORKING",
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_author_locomotion_action",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_name": action_name,
            },
        )

    def author_humanoid_rig(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        rig_name: str = "",
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_author_humanoid_rig",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "rig_name": rig_name,
            },
        )

    def patch_existing_humanoid_action_phases(
        self, job_id: str, blend_rel: str, checkpoint_rel: str,
        expected_source_sha256: str, expected_action_sha256: str,
        target_armature_name: str, source_action_name: str, target_action_name: str,
        semantic_role: str, source_fps: int, source_fps_base: float,
        frame_start: int, frame_end: int, phase_frames: Dict[str, int],
        allowed_bones: list[str], motion_bone_chain: list[str], bone_patches: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self.call("hoi4_blender_patch_existing_humanoid_action_phases", {
            "job_id": job_id, "blend_rel": blend_rel, "checkpoint_rel": checkpoint_rel,
            "expected_source_sha256": expected_source_sha256, "expected_action_sha256": expected_action_sha256,
            "target_armature_name": target_armature_name, "source_action_name": source_action_name, "target_action_name": target_action_name,
            "semantic_role": semantic_role, "source_fps": source_fps, "source_fps_base": source_fps_base,
            "frame_start": frame_start, "frame_end": frame_end, "phase_frames": phase_frames,
            "allowed_bones": allowed_bones, "motion_bone_chain": motion_bone_chain, "bone_patches": bone_patches,
        })

    def author_humanoid_actions(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        action_names: Optional[Dict[str, str]] = None,
        fps: int = 24,
        fused_weapon_grip: bool = False,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_author_humanoid_actions",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_names": action_names or {},
                "fps": fps,
                "fused_weapon_grip": fused_weapon_grip,
            },
        )




    def isolate_humanoid_weapon(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        weapon_component_indices: list[int],
        component_prefix: str,
        *,
        stock_component_indices: Optional[list[int]] = None,
        stock_link_component_indices: Optional[list[int]] = None,
        body_object_name: str = "humanoid_body",
        weapon_object_name: str = "humanoid_weapon",
        stock_x_fraction: float = 0.03,
        stock_y_front_offset_fraction: float = -0.18,
        stock_z_fraction: float = 0.64,
        aim_down_degrees: float = 2.0,
        stock_advance_m: float = 1.25,
        stock_link_advance_m: float = 0.55,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_isolate_humanoid_weapon",
            {
                "job_id": job_id,
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


    def attach_rigid_weapon_from_checkpoint(
        self,
        job_id: str,
        source_blend_rel: str,
        target_blend_rel: str,
        output_blend_rel: str,
        source_object_name: str,
        target_object_name: str,
        target_armature_name: str,
        parent_bone_name: str,
        *,
        create_weapon_bone_name: str = "",
        translation: Optional[list[float]] = None,
        rotation_euler_degrees: Optional[list[float]] = None,
        scale: Optional[list[float]] = None,
        collision_policy: str = "reject",
        action_name: str = "",
        render_views: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_attach_rigid_weapon_from_checkpoint",
            {
                "job_id": job_id,
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


    def bake_static_mesh_transforms(
        self,
        job_id: str,
        blend_rel: str,
        output_blend_rel: str,
        *,
        asset_kind: str,
        bounds_tolerance: float = 1e-5,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_bake_static_mesh_transforms",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "output_blend_rel": output_blend_rel,
                "asset_kind": asset_kind,
                "bounds_tolerance": bounds_tolerance,
            },
        )

    def partition_skeletal_mesh_export_batches(
        self, *, job_id: str, blend_rel: str, expected_source_sha256: str,
        checkpoint_rel: str, target_armature_name: str, target_mesh_names: list[str],
        max_export_vertices_per_batch: int = 24000,
    ) -> Dict[str, Any]:
        return self.call("hoi4_blender_partition_skeletal_mesh_export_batches", {
            "job_id": job_id, "blend_rel": blend_rel,
            "expected_source_sha256": expected_source_sha256, "checkpoint_rel": checkpoint_rel,
            "target_armature_name": target_armature_name, "target_mesh_names": target_mesh_names,
            "max_export_vertices_per_batch": max_export_vertices_per_batch,
        })

    def partition_static_mesh_export_batches(
        self,
        job_id: str,
        blend_rel: str,
        output_blend_rel: str,
        *,
        asset_kind: str,
        max_export_vertices_per_batch: int = 60000,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_partition_static_mesh_export_batches",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "output_blend_rel": output_blend_rel,
                "asset_kind": asset_kind,
                "max_export_vertices_per_batch": max_export_vertices_per_batch,
            },
        )

    def import_animation_action(
        self,
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
        bone_chains: Optional[Dict[str, list[str]]] = None,
        promote_audited_target: bool = False,
        source_armature_name: str = "",
        root_scale_reference: Optional[Dict[str, list[str]]] = None,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_import_animation_action",
            {
                "job_id": job_id,
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

    def retime_animation_action(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        action_name: str,
        target_armature_name: str,
        source_fps: float,
        target_fps: float,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_retime_animation_action",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_name": action_name,
                "target_armature_name": target_armature_name,
                "source_fps": source_fps,
                "target_fps": target_fps,
            },
        )

    def segment_creature_components(
        self,
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
        return self.call(
            "hoi4_blender_segment_creature_components",
            {
                "job_id": job_id,
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

    def calibrate_creature_scale(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        rider_component_names: list[str],
        target_rider_runtime_height_m: float,
        runtime_entity_scale: float = 0.8,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_calibrate_creature_scale",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "rider_component_names": rider_component_names,
                "target_rider_runtime_height_m": target_rider_runtime_height_m,
                "runtime_entity_scale": runtime_entity_scale,
            },
        )

    def author_creature_rig(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        rider_component_names: Optional[list[str]] = None,
        weight_mode: str = "semantic",
        rig_name: str = "",
        creature_rig_family: str = "elephant",
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_author_creature_rig",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "rider_component_names": rider_component_names or [],
                "weight_mode": weight_mode,
                "rig_name": rig_name,
                "creature_rig_family": creature_rig_family,
            },
        )

    def author_creature_action(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        action_role: str,
        action_name: str,
        creature_rig_family: str = "elephant",
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_author_creature_action",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_role": action_role,
                "action_name": action_name,
                "creature_rig_family": creature_rig_family,
            },
        )

    def correct_action_grounding(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        action_name: str,
        target_armature_name: str = "",
        grounding_policy: Literal["per_frame_root_contact_zero_clearance"] = "per_frame_root_contact_zero_clearance",
        root_bone: str = "Hips",
        excluded_contact_bones: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_correct_action_grounding",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_name": action_name,
                "target_armature_name": target_armature_name,
                "grounding_policy": grounding_policy,
                "root_bone": root_bone,
                "excluded_contact_bones": excluded_contact_bones or [],
            },
        )

    def import_bvh_animation_action(
        self,
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
        return self.call(
            "hoi4_blender_import_bvh_animation_action",
            {
                "job_id": job_id,
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

    def prepare_export_coordinate_checkpoint(
        self,
        job_id: str,
        blend_rel: str,
        checkpoint_rel: str,
        action_name: str,
        target_armature_name: str,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_prepare_export_coordinate_checkpoint",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_name": action_name,
                "target_armature_name": target_armature_name,
            },
        )

    def sanitize_runtime_candidate(
        self,
        job_id: str,
        blend_rel: str,
        output_blend_rel: str = "blender/checkpoints/07_runtime_candidate_sanitized.blend",
        target_height_m: Optional[float] = None,
        weight_only: bool = False,
        max_influences_per_vertex: int = 4,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_sanitize_runtime_candidate",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "output_blend_rel": output_blend_rel,
                "target_height_m": target_height_m,
                "weight_only": weight_only,
                "max_influences_per_vertex": max_influences_per_vertex,
            },
        )

    def reimport_export(
        self,
        job_id: str,
        mesh_rel: str,
        anim_rel: str = "",
        proof_name: str = "",
        stage_default_textures: bool = True,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_reimport_export",
            {
                "job_id": job_id,
                "mesh_rel": mesh_rel,
                "anim_rel": anim_rel,
                "proof_name": proof_name,
                "stage_default_textures": stage_default_textures,
            },
        )

    def inspect_scene(
        self,
        job_id: str,
        blend_rel: str,
        render_previews: bool = False,
        runtime_stem: str = "",
        action_name: str = "",
        target_armature_name: str = "",
        preview_frame: int = -1,
        preview_view_names: Optional[list[str]] = None,
        mesh_region: Optional[Dict[str, Any]] = None,
        material_visibility: Optional[Dict[str, Any]] = None,
        include_action_channels: bool = False,
        expected_source_sha256: str = "",
        preview_region: Optional[Dict[str, Any]] = None,
        preview_resolution: int = 512,
        evaluated_frames: Optional[list[int]] = None,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_inspect_scene",
            {
                "job_id": job_id,
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
                **({"material_visibility": material_visibility} if material_visibility is not None else {}),
                **({"include_action_channels": True, "expected_source_sha256": expected_source_sha256} if include_action_channels else {}),
            },
        )

    def review_humanoid_components(
        self,
        job_id: str,
        blend_rel: str,
        expected_source_sha256: str,
        mesh_name: str,
        render_group: bool = True,
        component_ids: Optional[list[str]] = None,
        component_offset: int = 0,
        component_limit: int = 16,
        preview_view_names: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_review_humanoid_components",
            {
                "job_id": job_id,
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

    def save_checkpoint(self, job_id: str, blend_rel: str, stage: str) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_save_checkpoint",
            {"job_id": job_id, "blend_rel": blend_rel, "stage": stage},
        )
