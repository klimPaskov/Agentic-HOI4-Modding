"""Blender-side test of the quadruped rig family on a procedural horse.

Run with the lock-selected Blender:
    blender --background --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_quadruped_integration.py
It writes only temporary .blend files and fails on the first unmet expectation.
"""

from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT / "adapter"))

import blender_worker  # noqa: E402
import quadruped_layout  # noqa: E402


def _cylinder(bm: bmesh.types.BMesh, start: Vector, end: Vector, radius: float) -> None:
    direction = end - start
    matrix = Matrix.Translation((start + end) / 2) @ direction.to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=radius, radius2=radius, depth=direction.length, matrix=matrix)


def make_horse(path: Path) -> None:
    blender_worker.clear_scene()
    working = bpy.data.collections.new("WORKING")
    bpy.context.scene.collection.children.link(working)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0, matrix=Matrix.Translation((0, 0, 1.45)) @ Matrix.Diagonal((0.32, 1.05, 0.35, 1.0)))
    for x in (-0.2, 0.2):
        for y in (-0.75, 0.75):
            _cylinder(bm, Vector((x, y, 0.0)), Vector((x, y, 1.35)), 0.08)
    _cylinder(bm, Vector((0, -0.85, 1.6)), Vector((0, -1.25, 2.25)), 0.13)
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0, matrix=Matrix.Translation((0, -1.45, 2.2)) @ Matrix.Diagonal((0.12, 0.28, 0.13, 1.0)))
    _cylinder(bm, Vector((0, 1.05, 1.6)), Vector((0, 1.3, 0.85)), 0.05)
    mesh = bpy.data.meshes.new("test_horse")
    bm.to_mesh(mesh)
    bm.free()
    horse = bpy.data.objects.new("test_horse", mesh)
    working.objects.link(horse)
    horse["hoi4_working"] = True
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="hoi4_quadruped_test_") as temporary:
        job = Path(temporary)
        make_horse(job / "horse.blend")
        rig = blender_worker.author_creature_rig({
            "job_root": str(job),
            "payload": {"blend_rel": "horse.blend", "checkpoint_rel": "rigged.blend", "creature_rig_family": "quadruped", "rig_name": "test_horse_armature"},
        })
        expect(rig["status"] == "pass", f"rig status {rig['status']}")
        expect(rig["bone_count"] == 27, f"27 bones expected, got {rig['bone_count']}")
        expect(rig["unweighted_vertices"] == 0, "every vertex must be weighted")
        expect(rig["turned_to_face_minus_y"] is False, "the test horse already faces -Y")
        landmarks = rig["landmarks"]
        expect(abs(landmarks["front_y"] + 0.75) < 0.05 and abs(landmarks["rear_y"] - 0.75) < 0.05, f"hooves at {landmarks['front_y']}, {landmarks['rear_y']}")
        expect(landmarks["tail"] is not None, "the tail was not found")
        expect(all(math.isfinite(value) for point in landmarks["tail"] for value in point), "tail joints must be finite")
        expect(rig["vertices_per_bone"]["Front_Left_Cannon"] > 0 and rig["vertices_per_bone"]["Head"] > 0, "legs and head must be weighted")
        source = "rigged.blend"
        for role, style in quadruped_layout.DEFAULT_STYLE.items():
            result = blender_worker.author_creature_action({
                "job_root": str(job),
                "payload": {
                    "blend_rel": source,
                    "checkpoint_rel": f"{role}.blend",
                    "action_role": role,
                    "action_name": f"test_horse_{role}",
                    "creature_rig_family": "quadruped",
                },
            })
            expect(result["status"] == "pass", f"{role} grounding failed: {result['ground_contact_after']}")
            expect(result["style"] == style, f"{role} used {result['style']}")
            expect(result["loop"] == (style in quadruped_layout.LOOPING), f"{role} loop flag")
            source = f"{role}.blend"
        make_horse(job / "backwards.blend")
        horse = bpy.data.objects["test_horse"]
        horse.data.transform(Matrix.Rotation(3.141592653589793, 4, "Z"))
        bpy.ops.wm.save_as_mainfile(filepath=str(job / "backwards.blend"))
        turned = blender_worker.author_creature_rig({
            "job_root": str(job),
            "payload": {"blend_rel": "backwards.blend", "checkpoint_rel": "backwards_rigged.blend", "creature_rig_family": "quadruped"},
        })
        expect(turned["turned_to_face_minus_y"] is True, "a horse facing +Y must be turned")
        expect(turned["landmarks"]["muzzle"][1] < turned["landmarks"]["front_y"], "after the turn the head is toward -Y")
        bpy.ops.wm.open_mainfile(filepath=str(job / source))
        expect(len([action for action in bpy.data.actions if action.name.startswith("test_horse_")]) == 6, "six actions must survive the saves")
    print("quadruped integration: pass")


main()
