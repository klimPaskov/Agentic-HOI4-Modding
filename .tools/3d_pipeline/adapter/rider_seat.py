"""Seat a humanoid action on horseback (a Meshy rig, or a Tripo rig after the intake renames its bones to the kit's).

The rider entity attaches to the mount's Saddle_Node, so its origin is the
saddle. For every keyed frame of an imported clip this keeps the upper body as
the clip moves it, puts the pelvis on the origin (lifted by `seat_lift` of the
rider's height), damps the hip sway and holds both legs astride: thighs forward
and out, shins down along the flank, feet forward. With the mount's measured
barrel (`barrel`, rows from lib/rider_fit.clip_profiles for the paired mount
clip) the legs are aimed outside it (rider_legs.py), else by a fixed aim
measured on one horse. With the mount's top ahead of the seat (`top`) a hand the
clip puts into the withers, neck or pommel is lifted at the shoulder. `slump`
adds a forward collapse over the clip for the death role. Bone names are the
kit's (Meshy's names).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict

import bpy
from mathutils import Matrix, Quaternion, Vector

import rider_legs

LEGS = {
    "Left": ("LeftUpLeg", "LeftLeg", "LeftFoot"),
    "Right": ("RightUpLeg", "RightLeg", "RightFoot"),
}
SPINE = ("Spine02", "Spine01", "Spine", "neck", "Head")
# The couched lance (D-127: a clip fits the unit's era, weapon and kind). A mounted lancer of the fifteenth century attacks with the lance
# lowered level under the right arm and the charge carrying it, never with a punch, a chop or a hammer swing. Over the clip the right upper
# arm comes down tight to the side and the forearm points forward (the lance's hold, held level by the grip stage), the left hand keeps the
# reins low in front, and the body leans into the blow. Directions are (forward, outward, up) in the rider's frame; the turn into and out of
# the pose takes COUCH_EASE of the clip at each end, so a looping attack starts and ends on the clip's own pose.
COUCH_ARMS = {
    "Right": {"Arm": (-0.15, 0.25, -0.95), "ForeArm": (1.0, -0.15, -0.12)},
    "Left": {"Arm": (0.1, 0.2, -0.95), "ForeArm": (0.9, -0.35, -0.25)},
}
COUCH_LEAN = 14.0  # degrees forward over Spine01 and Spine02 together
COUCH_EASE = 0.25
# A seated rider's hips and legs hold still on the saddle, so a clip that turns a standing body at the hips (Tripo's hit_to_side) turns
# only the chest: the zinnish lancer's defend wrung the waist 58 degrees against the astride feet (TRIPO-WAIST-TWIST, limit 47.9). Vanilla's
# riders turn at most 21.7 (GER_infantry_cavalry_rider_idle_rifle). The shoulder line is held within SEAT_TWIST_MAX of square by turning
# the lowest spine bone back by the excess, frame by frame, so the clip's motion under the cap is kept.
SEAT_TWIST_MAX = 35.0
# With the mount's top ahead of the seat (`top`, lib/rider_fit.clip_profiles), a hand the clip puts into the withers, neck or pommel is
# lifted by turning its upper arm up at the shoulder in HAND_STEP degrees, at most HAND_TURN_MAX.
HAND_STEP = 3.0
HAND_TURN_MAX = 75.0
# A held weapon on its own bone (`held`: the grip stage's Weapon bone, a child of the hand): the hand turns at the wrist so the haft points
# along the job's `carry` direction (forward, outward on the hand's side, up), and in a couched role eases to `couch` with the couch pose.
# In a role that lets go of it (the death) the hand lets go once the slump has fallen RELEASE_FALL of its way, and the weapon drops onto
# the ground through the mount clip's node path (rider_legs.plan_drop).
RELEASE_FALL = 0.1


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


def _hold_twist(rig: bpy.types.Object, side_axis: Vector, forward: Vector, up: Vector) -> int:
    """Turn the lowest spine bone back so the shoulder line lies within SEAT_TWIST_MAX of the side axis (about `up`). 1 when it turned."""

    if not all(name in rig.pose.bones for name in ("Spine", "LeftArm", "RightArm")):
        return 0

    def twist() -> float:
        bpy.context.view_layer.update()
        line = rig.pose.bones["LeftArm"].head - rig.pose.bones["RightArm"].head
        return rider_legs.shoulder_twist(tuple(line), tuple(forward), tuple(side_axis), tuple(up))

    excess = twist() - SEAT_TWIST_MAX
    if excess <= 0:
        return 0
    bone = rig.pose.bones["Spine"]
    head = bone.head.copy()
    start = bone.matrix.copy()
    for sign in (-1.0, 1.0):
        # measured, not reasoned: turn back one way and keep it when the line came square, else the other way
        back = Quaternion(up, math.radians(sign * excess))
        bone.matrix = Matrix.Translation(head) @ back.to_matrix().to_4x4() @ Matrix.Translation(-head) @ start
        if twist() <= SEAT_TWIST_MAX + 0.5:
            return 1
    bone.matrix = start
    bpy.context.view_layer.update()
    return 0


def _clear_hands(rig: bpy.types.Object, forward: Vector, side_axis: Vector, up: Vector, height: float, top: list) -> tuple:
    """Turn each upper arm up about its shoulder, HAND_STEP at a time, until the hand's wrist and fingertip clear the mount's top ahead
    of the seat (rider_legs.hand_clear). Returns the arms turned and the arms still in the mount after HAND_TURN_MAX."""

    turned, stuck = [], []
    for side in ("Left", "Right"):
        arm, hand = f"{side}Arm", f"{side}Hand"
        if arm not in rig.pose.bones or hand not in rig.pose.bones:
            continue

        def clear() -> bool:
            bpy.context.view_layer.update()
            bone = rig.pose.bones[hand]
            points = [(p.dot(forward) / height, p.dot(side_axis) / height, p.dot(up) / height) for p in (bone.head, bone.tail)]
            return rider_legs.hand_clear(points, top)

        if clear():
            continue
        bone = rig.pose.bones[arm]
        head = bone.head.copy()
        start = bone.matrix.copy()
        reach = rig.pose.bones[hand].head - head
        axis = reach.cross(up)
        if axis.length < 1e-6:
            stuck.append(arm)
            continue
        axis.normalize()
        for step in range(1, int(HAND_TURN_MAX / HAND_STEP) + 1):
            # a turn about (reach x up) lifts the hand toward up
            lift = Quaternion(axis, math.radians(step * HAND_STEP))
            bone.matrix = Matrix.Translation(head) @ lift.to_matrix().to_4x4() @ Matrix.Translation(-head) @ start
            if clear():
                turned.append(arm)
                break
        else:
            bone.matrix = start
            bpy.context.view_layer.update()
            stuck.append(arm)
    return turned, stuck


def _aim_haft(rig: bpy.types.Object, hand: str, weapon: str, target: Vector) -> None:
    """Turn the hand about its wrist so the held weapon's haft (its bone, pointing to the head) lies along `target` (armature space)."""

    bpy.context.view_layer.update()
    bone = rig.pose.bones[hand]
    held = rig.pose.bones[weapon]
    turn = (held.tail - held.head).normalized().rotation_difference(target.normalized())
    head = bone.head.copy()
    bone.matrix = Matrix.Translation(head) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-head) @ bone.matrix


def _cut(action: bpy.types.Action, start: int, end: int, seconds: float, fps: float) -> int:
    """Cut the action to `seconds` (the paired mount clip's length): the game starts a rider's clip with the mount's. Returns the end."""

    import anim_frame_range

    keep = max(2, int(round(seconds * fps)))
    if end - start + 1 <= keep:
        return end
    last = start + keep - 1
    for curve in anim_frame_range.action_fcurves(action):
        for key in [key for key in curve.keyframe_points if key.co[0] > last + 1e-6][::-1]:
            curve.keyframe_points.remove(key)
        curve.update()
    action.use_frame_range = True
    action.frame_start, action.frame_end = start, last
    return last


def _held_object(rig: bpy.types.Object, name: str, held: bool) -> list:
    """The meshes under the rig that are (`held`) or are not the part bound wholly to the bone `name`."""

    found = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.parent != rig:
            continue
        only = len(obj.vertex_groups) == 1 and obj.vertex_groups[0].name == name
        if only == held:
            found.append(obj)
    return found


def _points(rig: bpy.types.Object, objects: list, count: int = 1500) -> list:
    """The objects' skinned points now, in armature space, about `count` of them."""

    depsgraph = bpy.context.evaluated_depsgraph_get()
    to_rig = rig.matrix_world.inverted()
    points = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        matrix = to_rig @ obj.matrix_world
        vertices = list(mesh.vertices)
        stride = max(1, len(vertices) // count)
        points += [matrix @ vertex.co for vertex in vertices[::stride]]
        evaluated.to_mesh_clear()
    return points


def _drop_held(rig, held: Dict[str, Any], start: int, release: int, end: int, fps: float, forward: Vector, side_axis: Vector,
               up: Vector, height: float) -> Dict[str, Any]:
    """Let the held weapon go at frame `release` and drop it onto the ground clear of the fallen mount and rider (rider_legs.plan_drop),
    still on the ground to the end. The ground stands still in the seat's rest frame. Each frame the node path (lib/rider_fit.drop_inputs)
    carries it to the moving node's frame, where the rider's armature lives."""

    import numpy as np

    drop = held["drop"]
    path = drop["path"]
    name = held["bone"]
    scene = bpy.context.scene
    axes = Matrix((forward, side_axis, up)).transposed()  # columns: the seat's ahead, out and up in armature space

    def step(frame: int) -> Dict[str, Any]:
        return path[min(len(path) - 1, int(round((frame - start) / fps * float(drop["fps"]))))]

    def node(frame: int) -> Matrix:
        turn = axes @ Matrix(step(frame)["r"]) @ axes.transposed()
        move = axes @ Vector(step(frame)["t"]) * height
        return Matrix.Translation(move) @ turn.to_4x4()

    def to_seat(vector: Vector) -> tuple:
        return (vector.dot(forward) / height, vector.dot(side_axis) / height, vector.dot(up) / height)

    scene.frame_set(release)
    bpy.context.view_layer.update()
    bone = rig.pose.bones[name]
    held_world = node(release).inverted() @ bone.matrix.copy()
    grip_now = bone.head.copy()
    haft_now = (bone.tail - bone.head).normalized()
    along = [(point - grip_now).dot(haft_now) for point in _points(rig, _held_object(rig, name, True), 4000)] or [0.0, height]
    length = (max(along) - min(along)) / height
    grip_share = -min(along) / max(max(along) - min(along), 1e-9)
    haft_world = (held_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
    obstacles = [list(point) for point in drop["mount_end"]]
    tumble = max(1, int(round(rider_legs.DROP_SECONDS * fps)))
    body = _held_object(rig, name, False)
    for frame in sorted({end, min(end, release + tumble)}):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        r, t = np.array(step(frame)["r"]), np.array(step(frame)["t"])
        moving = np.array([to_seat(point) for point in _points(rig, body)])
        if len(moving):
            obstacles += (r.T @ (moving - t).T).T.tolist()
    plan = rider_legs.plan_drop(to_seat(held_world.translation), tuple(v * height for v in to_seat(haft_world)), length, grip_share,
                                float(drop["ground"]), obstacles)
    land_haft = axes @ Vector([float(v) for v in plan["haft"]])
    land_rotation = haft_world.rotation_difference(land_haft).to_matrix() @ held_world.to_3x3()
    start_point = held_world.translation.copy()
    end_point = axes @ Vector([float(v) for v in plan["grip"]]) * height
    start_q, end_q = held_world.to_quaternion(), land_rotation.to_quaternion()
    rise = (end_point - start_point).dot(up)
    flat = (end_point - start_point) - up * rise
    for frame in range(release, end + 1):
        share = min(1.0, (frame - release) / tumble)
        ease = _smooth(share)
        # across the ground eased, down as a fall from rest (the square of the time)
        point = start_point + flat * ease + up * (rise * share * share)
        world = Matrix.Translation(point) @ start_q.slerp(end_q, ease).to_matrix().to_4x4()
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        bone.matrix = node(frame) @ world
        bpy.context.view_layer.update()
        bone.keyframe_insert("rotation_quaternion" if bone.rotation_mode == "QUATERNION" else "rotation_euler", frame=frame, group=name)
        bone.keyframe_insert("location", frame=frame, group=name)
    return {"release_frame": release, "landed_frame": min(end, release + tumble), "found": bool(plan["found"]),
            "gap": round(float(plan["gap"]), 4), "travel": round(float(plan["travel"]), 3), "length": round(length, 4),
            "grip_share": round(grip_share, 4), "grip": [round(float(v), 4) for v in plan["grip"]],
            "haft": [round(float(v), 4) for v in plan["haft"]]}


def seat_rider_action(req: Dict[str, Any], h: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = h["within"](job, payload["blend_rel"])
    checkpoint = h["within"](job, payload["checkpoint_rel"], allow_missing=True)
    action_name = str(payload["action_name"])
    seat_lift = float(payload.get("seat_lift", 0.06))
    slump = bool(payload.get("slump", False))
    couch = bool(payload.get("couch", False))
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
    scene = bpy.context.scene
    fps = scene.render.fps / scene.render.fps_base
    full_end = end
    if payload.get("seconds"):
        end = _cut(action, start, end, float(payload["seconds"]), fps)
    to_armature = rig.matrix_world.inverted().to_3x3()
    forward = (to_armature @ Vector((0.0, -1.0, 0.0))).normalized()
    up = (to_armature @ Vector((0.0, 0.0, 1.0))).normalized()
    side_axis = forward.cross(up).normalized()
    rest_heights = [bone.head_local.dot(up) for bone in rig.data.bones]
    height = max(rest_heights) - min(rest_heights)
    hips_rest = rig.data.bones["Hips"].matrix_local.to_quaternion()
    seat = up * (seat_lift * height)
    # The mount's barrel beside the seat (lib/rider_fit.barrel_profile, rows of depth and half-width in rider heights), when known.
    barrel = payload.get("barrel") or []
    # The mount's top ahead of the seat over the paired mount clip (lib/rider_fit.clip_profiles), when known: the hands stay above it.
    top = payload.get("top") or []
    lengths = {name: rig.data.bones[name].length / height for chain in LEGS.values() for name in chain}
    fits: Dict[str, bool] = {}
    held = payload.get("held") or {}
    if held and not all(name in rig.pose.bones for name in (held.get("bone", ""), held.get("hand", ""))):
        raise RuntimeError(f"The held weapon's bones {held.get('bone')} and {held.get('hand')} are not in the rider's rig.")
    release = None
    if held.get("drop") and slump:
        release = next((frame for frame in range(start, end + 1) if _smooth((frame - start) / max(end - start, 1)) >= RELEASE_FALL), end)
    keyed = 0
    capped = 0
    hands_lifted = 0
    hands_stuck = 0
    for frame in range(start, end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        hips = rig.pose.bones["Hips"]
        clip_rotation = hips.matrix.to_quaternion()
        damped = hips_rest.slerp(clip_rotation, 0.35)
        if slump:
            fall = _smooth((frame - start) / max(end - start, 1))
            # forward over the neck, about the side axis as the spine below bends (a turn about `forward` leaned it sideways)
            damped = Quaternion(side_axis, math.radians(-14.0 * fall)) @ damped
        hips.matrix = Matrix.Translation(seat) @ damped.to_matrix().to_4x4()
        bpy.context.view_layer.update()
        hips_world_x = hips.head.dot(side_axis)
        for side, (thigh, shin, foot) in LEGS.items():
            outward = side_axis if rig.pose.bones[thigh].head.dot(side_axis) >= hips_world_x else -side_axis
            if barrel:
                # Solved for this mount (rider_legs.py): the thigh turns out only as far as clears the barrel, the shin hangs beside it.
                head = rig.pose.bones[thigh].head
                hip = (head.dot(forward) / height, head.dot(outward) / height, head.dot(up) / height)
                legs = rider_legs.solve_leg(hip, lengths[thigh], lengths[shin], barrel)
                fits[side] = fits.get(side, True) and bool(legs["clear"])
                # plain floats: a numpy float times a mathutils Vector is a numpy array, not a Vector
                (tf, to, tu), (sf, so, su) = ([float(value) for value in legs[part]] for part in ("thigh", "shin"))
                _aim(rig, thigh, tf * forward + to * outward + tu * up)
                _aim(rig, shin, sf * forward + so * outward + su * up)
            else:
                # No measured mount: knees about 0.21 of the rider's height out from the centre clear a horse's barrel
                # (measured on the ZIN knights' Meshy warhorse); the feet hang just outside them.
                _aim(rig, thigh, 0.55 * forward + 0.62 * outward - 0.56 * up)
                _aim(rig, shin, -0.2 * forward + 0.12 * outward - 1.0 * up)
            _aim(rig, foot, 1.0 * forward - 0.35 * up)
        twisted = _hold_twist(rig, side_axis, forward, up)
        capped += twisted
        if couch:
            t = (frame - start) / max(end - start, 1)
            weight = _smooth(min(t, 1.0 - t) / COUCH_EASE)
            for name in ("Spine01", "Spine02"):
                if name in rig.pose.bones:
                    bone = rig.pose.bones[name]
                    bpy.context.view_layer.update()
                    head = bone.head.copy()
                    bend = Quaternion(side_axis, math.radians(-0.5 * COUCH_LEAN * weight))
                    bone.matrix = Matrix.Translation(head) @ bend.to_matrix().to_4x4() @ Matrix.Translation(-head) @ bone.matrix
            for side, segments in COUCH_ARMS.items():
                for segment, (f, o, u) in segments.items():
                    name = f"{side}{segment}"
                    if name not in rig.pose.bones:
                        continue
                    bpy.context.view_layer.update()
                    bone = rig.pose.bones[name]
                    outward = side_axis if bone.head.dot(side_axis) >= hips.head.dot(side_axis) else -side_axis
                    current = (bone.tail - bone.head).normalized()
                    target = (f * forward + o * outward + u * up).normalized()
                    _aim(rig, name, current.lerp(target, weight).normalized() if weight < 1.0 else target)
        if slump:
            for index, name in enumerate(SPINE):
                if name in rig.pose.bones:
                    bone = rig.pose.bones[name]
                    bpy.context.view_layer.update()
                    head = bone.head.copy()
                    bend = Quaternion(side_axis, math.radians(-(10.0 + 4.0 * index) * fall))
                    bone.matrix = Matrix.Translation(head) @ bend.to_matrix().to_4x4() @ Matrix.Translation(-head) @ bone.matrix
        lifted: tuple = ()
        if top and not slump:
            lifted, stuck = _clear_hands(rig, forward, side_axis, up, height, top)
            hands_lifted += len(lifted)
            hands_stuck += len(stuck)
        aimed: tuple = ()
        if held and (release is None or frame < release):
            hand = rig.pose.bones[held["hand"]]
            outward = side_axis if hand.head.dot(side_axis) >= hips.head.dot(side_axis) else -side_axis
            f, o, u = held["carry"]
            target = f * forward + o * outward + u * up
            if couch and held.get("couch"):
                f, o, u = held["couch"]
                t = (frame - start) / max(end - start, 1)
                target = target.normalized().lerp((f * forward + o * outward + u * up).normalized(), _smooth(min(t, 1.0 - t) / COUCH_EASE))
            _aim_haft(rig, held["hand"], held["bone"], target)
            aimed = (held["hand"],)
        bpy.context.view_layer.update()
        couch_bones =("Spine01", "Spine02", "RightArm", "RightForeArm", "LeftArm", "LeftForeArm") if couch else ()
        twist_bones = ("Spine",) if twisted and not slump else ()
        for name in ("Hips", *LEGS["Left"], *LEGS["Right"], *(SPINE if slump else ()), *couch_bones, *twist_bones, *lifted, *aimed):
            if name not in rig.pose.bones:
                continue
            bone = rig.pose.bones[name]
            bone.keyframe_insert("rotation_quaternion" if bone.rotation_mode == "QUATERNION" else "rotation_euler", frame=frame, group=name)
            if name == "Hips":
                bone.keyframe_insert("location", frame=frame, group=name)
            keyed += 1
    dropped = None
    if release is not None:
        dropped = _drop_held(rig, held, start, release, end, fps, forward, side_axis, up, height)
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
        "couch": couch,
        "barrel_measured": bool(barrel),
        "legs_clear_barrel": fits if barrel else None,
        "keyed_bone_frames": keyed,
        "twist_capped_frames": capped,
        "top_measured": bool(top),
        "hands_lifted_arm_frames": hands_lifted,
        "hands_still_in_mount_arm_frames": hands_stuck,
        "cut_to_mount_clip": {"seconds": payload.get("seconds"), "frames_before": full_end - start + 1,
                              "frames_after": end - start + 1} if payload.get("seconds") else None,
        "held": {"bone": held.get("bone"), "carry": held.get("carry"), "couch": held.get("couch") if couch else None} if held else None,
        "dropped": dropped,
        "policy": "upper body from the clip; pelvis on the attach origin; legs astride (aimed outside the measured barrel when given); hip sway damped to 35 percent",
    }
