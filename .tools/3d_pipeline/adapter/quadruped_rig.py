"""Blender side of the `quadruped` creature rig family.

`author_rig` measures the working meshes, builds the 27-bone rig from
`quadruped_layout`, binds every vertex with region-limited distance weights and
saves a checkpoint. `author_action` keys one action every frame from the
layout's gait poses and then lifts the Root each frame so the lowest vertex
touches the ground. `h` is the worker's namespace (its helpers).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

import quadruped_layout as ql

FAMILY = "quadruped"
FPS = 24
GROUND_TOLERANCE = 0.01


def _mesh_points(objects: List[bpy.types.Object]) -> Tuple[np.ndarray, List[Tuple[bpy.types.Object, int]]]:
    rows = []
    owners = []
    for obj in objects:
        count = len(obj.data.vertices)
        local = np.empty(count * 3, dtype=np.float32)
        obj.data.vertices.foreach_get("co", local)
        matrix = np.array(obj.matrix_world, dtype=np.float64)
        rows.append(local.reshape(-1, 3).astype(np.float64) @ matrix[:3, :3].T + matrix[:3, 3])
        owners.append((obj, count))
    return np.concatenate(rows), owners


def _evaluated_min_z(objects: List[bpy.types.Object]) -> float:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    lowest = math.inf
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            count = len(mesh.vertices)
            if count:
                local = np.empty(count * 3, dtype=np.float32)
                mesh.vertices.foreach_get("co", local)
                matrix = np.array(evaluated.matrix_world, dtype=np.float64)
                z = local.reshape(-1, 3).astype(np.float64) @ matrix[2, :3] + matrix[2, 3]
                lowest = min(lowest, float(z.min()))
        finally:
            evaluated.to_mesh_clear()
    return lowest


def _landmarks_from_payload(points: np.ndarray, payload: Dict[str, Any]) -> Dict[str, Any]:
    measured = payload.get("landmarks")
    if not measured:
        return ql.detect_landmarks(points)
    landmarks = dict(measured)
    for key in ("muzzle", "poll", "saddle"):
        landmarks[key] = np.asarray(landmarks[key], dtype=float)
    if landmarks.get("tail"):
        landmarks["tail"] = [np.asarray(item, dtype=float) for item in landmarks["tail"]]
    landmarks["legs"] = {
        leg: {joint: np.asarray(value, dtype=float) for joint, value in joints.items()}
        for leg, joints in landmarks["legs"].items()
    }
    return landmarks


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [round(float(item), 6) for item in value.tolist()]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (np.floating, float)):
        return round(float(value), 6)
    return value


def author_rig(req: Dict[str, Any], h: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = h["within"](job, payload["blend_rel"])
    checkpoint = h["within"](job, payload["checkpoint_rel"], allow_missing=True)
    rig_name = h["safe_name"](str(payload.get("rig_name") or "quadruped_armature"))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    meshes = h["mesh_objects"]()
    if not meshes:
        raise RuntimeError("Quadruped rigging found no working meshes.")
    for existing in h["armatures"]():
        bpy.data.objects.remove(existing, do_unlink=True)
    points, owners = _mesh_points(meshes)
    landmarks = _landmarks_from_payload(points, payload)
    layout = ql.build_layout(landmarks)
    if len(layout.bones) > 50:
        raise RuntimeError(f"The quadruped rig has {len(layout.bones)} bones; the engine skins at most 50.")

    data = bpy.data.armatures.new(rig_name)
    rig = bpy.data.objects.new(rig_name, data)
    h["_working_collection"]().objects.link(rig)
    rig["hoi4_working"] = True
    rig["hoi4_custom_creature_rig"] = True
    rig["hoi4_creature_rig_family"] = FAMILY
    rig["hoi4_quadruped_landmarks"] = json.dumps(_jsonable(landmarks))
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    edit = {}
    for bone in layout.bones:
        created = data.edit_bones.new(bone.name)
        created.head = Vector(bone.head)
        created.tail = Vector(bone.tail)
        created.roll = 0.0
        created.use_deform = bone.deform
        if bone.parent:
            created.parent = edit[bone.parent]
            created.use_connect = False
        edit[bone.name] = created
    bpy.ops.object.mode_set(mode="OBJECT")
    data.display_type = "BBONE"
    rig.show_in_front = True

    indices, weights = ql.skin_weights(points, layout)
    names = layout.names()
    offset = 0
    per_bone = {name: 0 for name in names}
    unweighted = 0
    for obj, count in owners:
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        groups = {bone.name: obj.vertex_groups.new(name=bone.name) for bone in layout.bones if bone.deform}
        for vertex in range(count):
            row_weights = weights[offset + vertex]
            if row_weights.sum() <= 0:
                unweighted += 1
            for slot in range(indices.shape[1]):
                weight = float(row_weights[slot])
                if weight <= 0:
                    continue
                name = names[int(indices[offset + vertex, slot])]
                groups[name].add([vertex], weight, "REPLACE")
                per_bone[name] += 1
        modifier = next((item for item in obj.modifiers if item.type == "ARMATURE"), None) or obj.modifiers.new("HOI4_QUADRUPED_ARMATURE", "ARMATURE")
        modifier.object = rig
        world = obj.matrix_world.copy()
        obj.parent = rig
        obj.parent_type = "OBJECT"
        obj.matrix_world = world
        offset += count
    if unweighted:
        raise RuntimeError(f"{unweighted} vertices received no bone weight.")
    h["save_blend"](checkpoint)
    return {
        "status": "pass",
        "creature_rig_family": FAMILY,
        "rig": rig.name,
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "bones": [{"name": bone.name, "parent": bone.parent, "deform": bone.deform} for bone in layout.bones],
        "bone_count": len(layout.bones),
        "landmarks": _jsonable(landmarks),
        "weighted_vertices": int(points.shape[0]),
        "vertices_per_bone": per_bone,
        "max_influences": int(indices.shape[1]),
        "unweighted_vertices": unweighted,
        "weighting": "region-limited inverse fourth power of the distance to each bone segment",
    }


def _rotation(rows: List[ql.Rotation]) -> Quaternion:
    result = Quaternion((1.0, 0.0, 0.0, 0.0))
    for axis, degrees in rows:
        result = Quaternion(Vector(axis), math.radians(degrees)) @ result
    return result


def author_action(req: Dict[str, Any], h: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = h["within"](job, payload["blend_rel"])
    checkpoint = h["within"](job, payload["checkpoint_rel"], allow_missing=True)
    role = str(payload.get("action_role") or "").casefold()
    style = str(payload.get("action_style") or ql.DEFAULT_STYLE.get(role, ""))
    if style not in ql.GAITS and style not in ql.ROLE_FRAMES:
        raise ValueError(f"Unknown quadruped action style {style!r} for role {role!r}.")
    action_name = h["safe_name"](str(payload.get("action_name") or f"quadruped_{role}"))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = [rig for rig in h["armatures"]() if rig.get("hoi4_creature_rig_family") == FAMILY]
    if len(rigs) != 1:
        raise RuntimeError(f"Quadruped action authoring needs exactly one quadruped rig, found {len(rigs)}.")
    rig = rigs[0]
    landmarks = _landmarks_from_payload(np.zeros((0, 3)), {"landmarks": json.loads(rig["hoi4_quadruped_landmarks"])})
    layout = ql.build_layout(landmarks)
    meshes = h["mesh_objects"]()
    total = ql.frame_count(style)
    loop = style in ql.LOOPING
    last = total if loop else total - 1
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 0
    scene.frame_end = last
    rig.animation_data_create()
    previous = bpy.data.actions.get(action_name)
    if previous is not None:
        bpy.data.actions.remove(previous)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    rig.animation_data.action = action
    rest = {pose.name: pose.bone.matrix_local.to_quaternion() for pose in rig.pose.bones}
    ground = float(landmarks["ground_offset"])
    root_rest = rig.pose.bones["Root"].bone.matrix_local.copy()
    rear = [landmarks["legs"][f"Rear_{side}"]["ground"] for side in ("Left", "Right")]
    rear_pivot = Vector(((rear[0][0] + rear[1][0]) / 2, (rear[0][1] + rear[1][1]) / 2, ground))
    root_pivot = root_rest.to_translation()

    def pose_frame(frame: int, lift: float) -> None:
        pose = ql.pose_at(style, frame, layout)
        for bone in rig.pose.bones:
            bone.rotation_mode = "QUATERNION"
            bone.location = (0.0, 0.0, 0.0)
            rows = pose.get(bone.name)
            if rows and bone.name != "Root":
                bone.rotation_quaternion = rest[bone.name].inverted() @ _rotation(rows) @ rest[bone.name]
            else:
                bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        body = Matrix.Identity(4)
        if "__root_pitch__" in pose:
            turn = _rotation(pose["__root_pitch__"]).to_matrix().to_4x4()
            body = Matrix.Translation(rear_pivot) @ turn @ Matrix.Translation(-rear_pivot)
        elif "__root_roll__" in pose:
            turn = _rotation(pose["__root_roll__"]).to_matrix().to_4x4()
            body = Matrix.Translation(root_pivot) @ turn @ Matrix.Translation(-root_pivot)
        rig.pose.bones["Root"].matrix = Matrix.Translation((0.0, 0.0, lift)) @ body @ root_rest
        bpy.context.view_layer.update()

    contact_before = []
    contact_after = []
    for frame in range(0, last + 1):
        scene.frame_set(frame)
        pose_frame(frame, 0.0)
        lowest = _evaluated_min_z(meshes) - ground
        contact_before.append(lowest)
        pose_frame(frame, -lowest)
        contact_after.append(_evaluated_min_z(meshes) - ground)
        for bone in rig.pose.bones:
            bone.keyframe_insert("rotation_quaternion", frame=frame, group=bone.name)
            if bone.name == "Root":
                bone.keyframe_insert("location", frame=frame, group=bone.name)
    for fcurve, _slot in h["action_fcurves"](action):
        for key in fcurve.keyframe_points:
            key.interpolation = "LINEAR"
    scene.frame_set(0)
    worst = max(abs(value) for value in contact_after)
    status = "pass" if worst <= GROUND_TOLERANCE * float(landmarks["height"]) else "fail"
    h["save_blend"](checkpoint)
    return {
        "status": status,
        "creature_rig_family": FAMILY,
        "role": role,
        "style": style,
        "action": action.name,
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "fps": FPS,
        "frame_start": 0,
        "frame_end": last,
        "loop": loop,
        "keyed_every_frame": True,
        "ground_contact_before": {"min": min(contact_before), "max": max(contact_before)},
        "ground_contact_after": {"min": min(contact_after), "max": max(contact_after)},
        "ground_tolerance": GROUND_TOLERANCE * float(landmarks["height"]),
    }
