"""Blender-side test of the live authoring helpers (`authoring/live_helpers.py`) on a small synthetic unit.

Run with the lock-selected Blender:
    blender --background --factory-startup --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_live_helpers_integration.py
`test_live_helpers.py` runs it when a Blender is installed. It writes renders only to a temporary folder.
"""

from __future__ import annotations

import math
import os
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
SHOTS = tempfile.mkdtemp(prefix="live_helpers_")
os.environ["HOI4_LIVE_SHOTS"] = SHOTS
sys.path.insert(0, str(PIPELINE_ROOT / "authoring"))

import live_helpers as h

# (name, parent, head, tail); the unit faces -Y, as the kit's units do.
BONES = [
    ("Hips", None, (0.0, 0.0, 1.0), (0.0, 0.0, 1.2)),
    ("Spine", "Hips", (0.0, 0.0, 1.2), (0.0, 0.0, 1.45)),
    ("Spine1", "Spine", (0.0, 0.0, 1.45), (0.0, 0.0, 1.7)),
    ("LeftUpLeg", "Hips", (0.15, 0.0, 0.95), (0.15, 0.0, 0.5)),
    ("LeftLeg", "LeftUpLeg", (0.15, 0.0, 0.5), (0.15, 0.0, 0.08)),
    ("LeftFoot", "LeftLeg", (0.15, 0.0, 0.08), (0.15, -0.15, 0.0)),
    ("LeftToe", "LeftFoot", (0.15, -0.15, 0.0), (0.15, -0.22, 0.0)),
    ("RightUpLeg", "Hips", (-0.15, 0.0, 0.95), (-0.15, 0.0, 0.5)),
    ("RightLeg", "RightUpLeg", (-0.15, 0.0, 0.5), (-0.15, 0.0, 0.08)),
    ("RightFoot", "RightLeg", (-0.15, 0.0, 0.08), (-0.15, -0.15, 0.0)),
    ("LeftArm", "Spine1", (0.25, 0.0, 1.6), (0.5, 0.0, 1.35)),
    ("LeftForeArm", "LeftArm", (0.5, 0.0, 1.35), (0.7, 0.0, 1.15)),
    ("LeftHand", "LeftForeArm", (0.7, 0.0, 1.15), (0.78, 0.0, 1.08)),
    ("weapon", "Hips", (0.75, -0.1, 1.05), (0.75, -0.2, 1.05)),
    ("muzzle", "weapon", (0.75, -0.7, 1.05), (0.75, -0.8, 1.05)),
]


def build():
    bpy.ops.wm.read_homefile(use_empty=True)
    data = bpy.data.armatures.new("rig")
    rig = bpy.data.objects.new("rig", data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name, parent, head, tail in BONES:
        bone = data.edit_bones.new(name)
        bone.head, bone.tail = head, tail
        if parent:
            bone.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    for pose_bone in rig.pose.bones:
        pose_bone.rotation_mode = "QUATERNION"
    # Two leg columns, a torso and a crotch strip whose sides follow one thigh each (a hard seam).
    verts, faces, groups = [], [], []

    def column(x, levels, bones):
        start = len(verts)
        for z, bone in zip(levels, bones):
            verts.extend([(x - 0.05, -0.05, z), (x + 0.05, -0.05, z), (x + 0.05, 0.05, z), (x - 0.05, 0.05, z)])
            groups.extend([bone] * 4)
        for ring in range(len(levels) - 1):
            a = start + 4 * ring
            for side in range(4):
                faces.append((a + side, a + (side + 1) % 4, a + 4 + (side + 1) % 4, a + 4 + side))

    column(0.15, [0.0, 0.08, 0.5, 0.95], ["LeftFoot", "LeftFoot", "LeftLeg", "LeftUpLeg"])
    column(-0.15, [0.0, 0.08, 0.5, 0.95], ["RightFoot", "RightFoot", "RightLeg", "RightUpLeg"])
    column(0.0, [1.0, 1.4, 1.75], ["Hips", "Spine", "Spine1"])
    start = len(verts)
    for x, bone in ((0.1, "LeftUpLeg"), (0.03, "LeftUpLeg"), (-0.03, "RightUpLeg"), (-0.1, "RightUpLeg")):
        verts.extend([(x, 0.0, 0.92), (x, 0.0, 0.86)])
        groups.extend([bone, bone])
    for step in range(3):
        a = start + 2 * step
        faces.append((a, a + 2, a + 3, a + 1))
    mesh = bpy.data.meshes.new("body")
    mesh.from_pydata(verts, [], faces)
    body = bpy.data.objects.new("body", mesh)
    bpy.context.scene.collection.objects.link(body)
    for name, _parent, _head, _tail in BONES:
        body.vertex_groups.new(name=name)
    for index, bone in enumerate(groups):
        body.vertex_groups[bone].add([index], 1.0, "REPLACE")
    modifier = body.modifiers.new("Armature", "ARMATURE")
    modifier.object = rig
    # A prop shaft along the weapon bone, bound rigidly to it.
    prop_mesh = bpy.data.meshes.new("gun")
    prop_mesh.from_pydata([(0.73, -0.1, 1.03), (0.77, -0.1, 1.03), (0.77, -0.7, 1.07), (0.73, -0.7, 1.07)], [], [(0, 1, 2, 3)])
    gun = bpy.data.objects.new("gun", prop_mesh)
    bpy.context.scene.collection.objects.link(gun)
    gun.vertex_groups.new(name="weapon").add([0, 1, 2, 3], 1.0, "REPLACE")
    gun.modifiers.new("Armature", "ARMATURE").object = rig
    bpy.context.view_layer.update()
    return rig, body


def close(a, b, tolerance=2e-3):
    return (Vector(a) - Vector(b)).length < tolerance


def legs() -> None:
    forward = h.rest_forward("LeftFoot", "LeftToe")
    assert close(forward, (0.0, -1.0, 0.0)), forward
    # A raised, tucked foot: the ankle reaches the target and the knee bends toward the toes.
    target = (0.15, 0.05, 0.3)
    ankle, _knee = h.solve_leg("LeftUpLeg", "LeftLeg", "LeftFoot", target, toe="LeftToe")
    assert close(ankle, target), (ankle, target)
    bend = h.knee_bend("LeftUpLeg", "LeftLeg", "LeftFoot")
    assert bend > 0.05, f"knee should point forward, bend {bend}"
    # The same target with the knee pushed backward is what UNIT-ANIM-KNEE fails.
    h.clear_pose()
    h.place_limb("LeftUpLeg", "LeftLeg", "LeftFoot", target, (0.0, 1.0, 0.0))
    assert h.knee_bend("LeftUpLeg", "LeftLeg", "LeftFoot") < -0.05


def temporary_ik(rig) -> None:
    # A temporary IK leaves no constraint behind and keeps its pose.
    h.clear_pose()
    hand_target = (0.6, -0.3, 1.2)
    reached = h.reach("LeftHand", "LeftArm", "LeftForeArm", hand_target)
    assert close(reached, hand_target, 5e-3), reached
    assert not any(bone.constraints for bone in rig.pose.bones)


def planting(rig) -> None:
    # A key whose foot floats (knee bent, ankle raised), then plant it back on the ground.
    h.clear_pose()
    h.new_action("idle", 10)
    h.move("Hips", dz=-0.05)
    h.solve_leg("LeftUpLeg", "LeftLeg", "LeftFoot", (0.15, 0.0, 0.16), toe="LeftToe")
    h.key(["Hips", "LeftUpLeg", "LeftLeg", "LeftFoot"], 1)
    floating = h.group_low("body", ["LeftFoot"])
    assert floating > 0.05, floating
    gap = h.plant(1, "LeftUpLeg", "LeftLeg", "LeftFoot", ["LeftFoot"], "body", toe="LeftToe")
    assert abs(gap) < 2e-3, gap
    bpy.context.scene.frame_set(1)
    assert abs(h.group_low("body", ["LeftFoot"])) < 2e-3
    assert h.knee_bend("LeftUpLeg", "LeftLeg", "LeftFoot") >= -1e-3
    fcurves = [fc for layer in rig.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    assert any('"LeftLeg"' in fc.data_path for fc in fcurves), "plant keys the leg"


def lean_and_seam(rig) -> None:
    # Spreading a lean: the top of the chain turns by the whole angle.
    h.clear_pose()
    rig.animation_data.action = None
    top_before = Vector(h.bone_world("Spine1", tail=True)) - Vector(h.bone_world("Spine1"))
    h.lean(["Hips", "Spine", "Spine1"], -12.0, (0.3, 0.35, 0.35))
    top_after = Vector(h.bone_world("Spine1", tail=True)) - Vector(h.bone_world("Spine1"))
    angle = math.degrees(top_before.angle(top_after))
    assert abs(angle - 12.0) < 0.5, angle
    # A crotch whose sides follow one thigh each is a seam; weighting it across the pelvis clears it.
    seam = h.seam_vertices("body", "LeftUpLeg", "RightUpLeg")
    assert len(seam) == 4, seam
    assert h.weight_seam("body", seam, "Hips", ("LeftUpLeg", "RightUpLeg")) == 4
    assert h.seam_vertices("body", "LeftUpLeg", "RightUpLeg") == []


def grips_and_renders() -> None:
    # A grip recorded in the prop's frame follows the prop when it moves.
    h.clear_pose()
    h.reach("LeftHand", "LeftArm", "LeftForeArm", (0.75, -0.25, 1.05))
    grip = h.grip_record("LeftHand", "weapon", "muzzle")
    h.rot("weapon", (1.0, 0.0, 0.0), 20.0)
    h.move("weapon", dz=0.05)
    error = h.seat_grip(grip, "LeftHand", "LeftArm", "LeftForeArm", frame=3)
    assert error < 5e-3, error
    origin, axes = h.prop_frame("weapon", "muzzle")
    assert close(Vector(h.bone_world("LeftHand")), origin + axes @ Vector(grip["position"]), 5e-3)
    # The review shot and a flat-colour close-up both write a sheet.
    h.setup_scene(96)
    h.flat_colours(True, props=["gun"])
    path = h.shot("check", views=("front", "hoi4"))
    assert Path(path).is_file(), path
    h.flat_colours(False)


def main() -> None:
    rig, _body = build()
    legs()
    temporary_ik(rig)
    planting(rig)
    lean_and_seam(rig)
    grips_and_renders()
    print("LIVE_HELPERS_INTEGRATION_OK")


main()
