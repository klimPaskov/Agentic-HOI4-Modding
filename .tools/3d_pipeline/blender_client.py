"""Client for the repository-owned allowlisted Blender MCP adapter."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from lib.mcp_stdio import MCPRouteError, call_stdio
from lib.paths import resolve_job_root
from meshy_client import require_meshy_key


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
        require_meshy_key()
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
        for attempt in range(3):
            try:
                result = call_stdio(
                    command,
                    tool=tool,
                    arguments=arguments,
                    timeout_seconds=1800,
                    cwd=self.repo_root,
                )
                break
            except MCPRouteError:
                if attempt == 2:
                    raise
        if result is None:
            raise RuntimeError(f"Blender adapter returned no result for {tool}.")
        if result.get("isError"):
            raise RuntimeError(str(_structured(result)))
        value = _structured(result)
        if "error" in value:
            raise RuntimeError(str(value))
        return value

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

    def export_mesh(self, job_id: str, blend_rel: str, output_rel: str) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_export_mesh",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "output_rel": output_rel,
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

    def review_humanoid_components(
        self,
        job_id: str,
        blend_rel: str,
        component_indices: list[int],
        runtime_stem: str = "humanoid_component_review",
        view_names: Optional[list[str]] = None,
        render_group: bool = False,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_review_humanoid_components",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "component_indices": component_indices,
                "runtime_stem": runtime_stem,
                "view_names": view_names or ["rear"],
                "render_group": render_group,
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
        checkpoint_rel: str,
        action_name: str,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_import_animation_action",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "source_rel": source_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_name": action_name,
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
        root_bone: str = "Hips",
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_correct_action_grounding",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "checkpoint_rel": checkpoint_rel,
                "action_name": action_name,
                "root_bone": root_bone,
            },
        )

    def reimport_export(
        self,
        job_id: str,
        mesh_rel: str,
        anim_rel: str = "",
        proof_name: str = "",
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_reimport_export",
            {
                "job_id": job_id,
                "mesh_rel": mesh_rel,
                "anim_rel": anim_rel,
                "proof_name": proof_name,
            },
        )

    def inspect_scene(
        self,
        job_id: str,
        blend_rel: str,
        render_previews: bool = False,
        runtime_stem: str = "",
        action_name: str = "",
        preview_frame: int = -1,
        preview_view_names: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_inspect_scene",
            {
                "job_id": job_id,
                "blend_rel": blend_rel,
                "render_previews": render_previews,
                "runtime_stem": runtime_stem,
                "action_name": action_name,
                "preview_frame": preview_frame,
                "preview_view_names": preview_view_names or [],
            },
        )

    def save_checkpoint(self, job_id: str, blend_rel: str, stage: str) -> Dict[str, Any]:
        return self.call(
            "hoi4_blender_save_checkpoint",
            {"job_id": job_id, "blend_rel": blend_rel, "stage": stage},
        )
