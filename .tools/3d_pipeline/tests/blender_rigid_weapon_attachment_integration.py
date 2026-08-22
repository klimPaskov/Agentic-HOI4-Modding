"""Blender-side smoke test for one-mesh rigid checkpoint attachment."""

from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

import bpy


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT / "adapter"))

import blender_worker  # noqa: E402


def make_source(path: Path) -> None:
    blender_worker.clear_scene()
    bpy.ops.mesh.primitive_cube_add(size=0.4)
    weapon = bpy.context.object
    weapon.name = "test_rigid_weapon"
    weapon.scale = (2.5, 0.25, 0.25)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def make_target(path: Path) -> None:
    blender_worker.clear_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.5))
    body = bpy.context.object
    body.name = "provider_body"
    body["hoi4_working"] = True
    armature_data = bpy.data.armatures.new("ArmatureData")
    rig = bpy.data.objects.new("Armature", armature_data)
    bpy.context.scene.collection.objects.link(rig)
    rig["hoi4_working"] = True
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    hand = armature_data.edit_bones.new("RightHand")
    hand.head = (0.25, 0.0, 0.75)
    hand.tail = (0.55, 0.0, 0.75)
    bpy.ops.object.mode_set(mode="POSE")
    pose_hand = rig.pose.bones["RightHand"]
    pose_hand.rotation_mode = "XYZ"
    for frame, angle in ((1, 0.0), (3, 0.35), (5, 0.0)):
        pose_hand.rotation_euler.z = angle
        pose_hand.keyframe_insert(data_path="rotation_euler", frame=frame, group="RightHand")
    bpy.ops.object.mode_set(mode="OBJECT")
    action = rig.animation_data.action
    action.name = "Armature|Idle|baselayer_WORKING"
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 5
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="hoi4_rigid_weapon_test_") as temporary:
        job = Path(temporary)
        source = job / "source.blend"
        target = job / "target.blend"
        output = job / "output.blend"
        make_source(source)
        make_target(target)
        result = blender_worker.attach_rigid_weapon_from_checkpoint(
            {
                "job_root": str(job),
                "payload": {
                    "source_blend_rel": source.name,
                    "target_blend_rel": target.name,
                    "output_blend_rel": output.name,
                    "source_object_name": "test_rigid_weapon",
                    "target_object_name": "test_rigid_weapon",
                    "target_armature_name": "Armature",
                    "parent_bone_name": "RightHand",
                    "create_weapon_bone_name": "weapon",
                    "translation": [0.05, 0.0, 0.0],
                    "rotation_euler_degrees": [0.0, 0.0, 0.0],
                    "scale": [1.0, 1.0, 1.0],
                    "collision_policy": "reject",
                    "action_name": "Armature|Idle|baselayer_WORKING",
                    "render_views": ["front"],
                },
            }
        )
        assert output.exists()
        assert result["status"] == "pass"
        assert result["attachment_bone"] == "weapon"
        assert result["retention_metrics"]["actions_retained_exactly"]
        assert result["retention_metrics"]["existing_bones_retained_exactly"]
        assert result["retention_metrics"]["new_bone_count"] == 1
        assert result["action_proof"]["sample_frames"] == [1, 3, 5]
        assert len(result["action_proof"]["samples"]) == 3
        assert result["action_proof"]["max_relative_matrix_delta"] <= 1e-5
        assert result["action_proof"]["max_rigid_edge_length_delta"] <= 1e-5
        assert all(math.isfinite(value) for sample in result["action_proof"]["samples"] for value in sample["world_transform"]["location"])
        print("rigid weapon Blender integration: pass")


if __name__ == "__main__":
    main()
