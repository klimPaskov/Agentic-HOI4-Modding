"""Seat a Meshy humanoid action on horseback.

The rider entity attaches to the mount's Saddle_Node, so its origin is the
saddle. For every keyed frame of an imported clip this keeps the upper body as
the clip moves it, puts the pelvis on the origin (lifted by `seat_lift` of the
rider's height), damps the hip sway and holds both legs astride: thighs forward
and out, shins down along the flank, feet forward. `slump` adds a forward
collapse over the clip for the death role. Bone names are the Meshy rig's.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict

import bpy
from mathutils import Matrix, Quaternion, Vector

LEGS = {
    "Left": ("LeftUpLeg", "LeftLeg", "LeftFoot"),
    "Right": ("RightUpLeg", "RightLeg", "RightFoot"),
}
SPINE = ("Spine02", "Spine01", "Spine", "neck", "Head")


def _smooth(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def _aim(rig: bpy.types.Object, name: str, target: Vector) -> None:
    """Rotate one posed bone about its head so it points along `target` (armature space)."""

    bone = rig.pose.bones[name]
    bpy.context.view_layer.update()
    matrix = bone.matrix.copy()
    current = (bone.tail - bone.head).normalized()
    turn = current.rotation_difference(target.normalized())
    head = matrix.to_translation()
    bone.matrix = Matrix.Translation(head) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-head) @ matrix


def seat_rider_action(req: Dict[str, Any], h: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = h["within"](job, payload["blend_rel"])
    checkpoint = h["within"](job, payload["checkpoint_rel"], allow_missing=True)
    action_name = str(payload["action_name"])
    seat_lift = float(payload.get("seat_lift", 0.06))
    slump = bool(payload.get("slump", False))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = [rig for rig in h["armatures"]() if rig.name == payload.get("target_armature_name", rig.name)]
    if len(rigs) != 1:
        raise RuntimeError(f"Rider seating needs exactly one target armature, found {len(rigs)}.")
    rig = rigs[0]
    missing = [name for chain in LEGS.values() for name in chain if name not in rig.pose.bones] + [n for n in ("Hips",) if n not in rig.pose.bones]
    if missing:
        raise RuntimeError(f"Rider seating needs the Meshy leg bones; missing {missing}.")
    action = bpy.data.actions.get(action_name)
    if action is None:
        raise RuntimeError(f"No action named {action_name}.")
    rig.animation_data_create()
    rig.animation_data.action = action
    start, end = (int(round(value)) for value in action.frame_range)
    to_armature = rig.matrix_world.inverted().to_3x3()
    forward = (to_armature @ Vector((0.0, -1.0, 0.0))).normalized()
    up = (to_armature @ Vector((0.0, 0.0, 1.0))).normalized()
    side_axis = forward.cross(up).normalized()
    rest_heights = [bone.head_local.dot(up) for bone in rig.data.bones]
    height = max(rest_heights) - min(rest_heights)
    hips_rest = rig.data.bones["Hips"].matrix_local.to_quaternion()
    seat = up * (seat_lift * height)
    scene = bpy.context.scene
    keyed = 0
    for frame in range(start, end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        hips = rig.pose.bones["Hips"]
        clip_rotation = hips.matrix.to_quaternion()
        damped = hips_rest.slerp(clip_rotation, 0.35)
        if slump:
            fall = _smooth((frame - start) / max(end - start, 1))
            damped = Quaternion(forward, math.radians(-14.0 * fall)) @ damped
        hips.matrix = Matrix.Translation(seat) @ damped.to_matrix().to_4x4()
        bpy.context.view_layer.update()
        hips_world_x = hips.head.dot(side_axis)
        for side, (thigh, shin, foot) in LEGS.items():
            outward = side_axis if rig.pose.bones[thigh].head.dot(side_axis) >= hips_world_x else -side_axis
            # Knees about 0.21 of the rider's height out from the centre clear a horse's barrel
            # (measured on the ZIN knights' warhorse); the feet hang just outside them.
            _aim(rig, thigh, 0.55 * forward + 0.62 * outward - 0.56 * up)
            _aim(rig, shin, -0.2 * forward + 0.12 * outward - 1.0 * up)
            _aim(rig, foot, 1.0 * forward - 0.35 * up)
        if slump:
            for index, name in enumerate(SPINE):
                if name in rig.pose.bones:
                    bone = rig.pose.bones[name]
                    bpy.context.view_layer.update()
                    head = bone.head.copy()
                    bend = Quaternion(side_axis, math.radians(-(10.0 + 4.0 * index) * fall))
                    bone.matrix = Matrix.Translation(head) @ bend.to_matrix().to_4x4() @ Matrix.Translation(-head) @ bone.matrix
        bpy.context.view_layer.update()
        for name in ("Hips", *LEGS["Left"], *LEGS["Right"], *(SPINE if slump else ())):
            if name not in rig.pose.bones:
                continue
            bone = rig.pose.bones[name]
            bone.keyframe_insert("rotation_quaternion" if bone.rotation_mode == "QUATERNION" else "rotation_euler", frame=frame, group=name)
            if name == "Hips":
                bone.keyframe_insert("location", frame=frame, group=name)
            keyed += 1
    h["save_blend"](checkpoint)
    return {
        "status": "pass",
        "action": action_name,
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "frame_start": start,
        "frame_end": end,
        "seat_lift_fraction": seat_lift,
        "rider_height_armature_units": height,
        "slump": slump,
        "keyed_bone_frames": keyed,
        "policy": "upper body from the clip; pelvis on the attach origin; legs astride; hip sway damped to 35 percent",
    }
