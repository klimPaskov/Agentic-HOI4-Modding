"""Blender side of the `quadruped` creature rig family.

`author_rig` measures the working meshes, builds the rig from `quadruped_layout`
(27 bones, a load's bone and two bones per ear that stands out beside the head,
`quadruped_ears`), binds every vertex with region-limited distance weights and
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

import quadruped_ears as qears
import quadruped_layout as ql
import quadruped_load as qload
import quadruped_wings as qwings

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


def _mesh_triangles(owners: List[Tuple[bpy.types.Object, int]]) -> np.ndarray:
    rows = []
    offset = 0
    for obj, count in owners:
        mesh = obj.data
        mesh.calc_loop_triangles()
        flat = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
        mesh.loop_triangles.foreach_get("vertices", flat)
        rows.append(flat.reshape(-1, 3) + offset)
        offset += count
    return np.concatenate(rows) if rows else np.zeros((0, 3), dtype=np.int64)


def _turn_quarter(meshes: List[bpy.types.Object], points: np.ndarray) -> None:
    """Turn the meshes a quarter turn about the vertical through their centre, so their length lies along Y."""

    centre = Vector(((points[:, 0].min() + points[:, 0].max()) / 2, (points[:, 1].min() + points[:, 1].max()) / 2, 0.0))
    turn = Matrix.Translation(centre) @ Matrix.Rotation(math.pi / 2, 4, "Z") @ Matrix.Translation(-centre)
    for obj in meshes:
        obj.data.transform(obj.matrix_world.inverted() @ turn @ obj.matrix_world)
        obj.data.update()


def _landmarks_from_payload(points: np.ndarray, payload: Dict[str, Any], back_z: Any = None) -> Dict[str, Any]:
    measured = payload.get("landmarks")
    if not measured:
        return ql.detect_landmarks(points, back_z=back_z)
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
        return round(float(value), 6) if value.ndim == 0 else _jsonable(value.tolist())
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (np.floating, float)):
        return round(float(value), 6)
    return value


def _turn_half(meshes: List[bpy.types.Object], points: np.ndarray) -> None:
    """Turn the meshes half a turn about the vertical through their centre and apply it, so they face -Y."""

    centre = Vector(((points[:, 0].min() + points[:, 0].max()) / 2, (points[:, 1].min() + points[:, 1].max()) / 2, 0.0))
    turn = Matrix.Translation(centre) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Translation(-centre)
    for obj in meshes:
        obj.data.transform(obj.matrix_world.inverted() @ turn @ obj.matrix_world)
        obj.data.update()


def _bind(
    owners: List[Tuple[bpy.types.Object, int]],
    layout: ql.Layout,
    indices: np.ndarray,
    weights: np.ndarray,
    rig: bpy.types.Object,
) -> Tuple[Dict[str, int], int]:
    """Write the weights as vertex groups, add the armature modifier and parent each mesh to the rig."""

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
    return per_bone, unweighted


def _orient(meshes: List[bpy.types.Object], payload: Dict[str, Any], options: Dict[str, Any]):
    """Turn the meshes so the animal lies along Y facing -Y, and find its load (quadruped_load.py) when the job says it carries one.

    The animal's length is its longest horizontal extent, so a model that lies along X is turned a quarter first. The load is found
    again in the turned frame (the vertex order is the same). Returns (points, owners, triangles, load or None, turned, quarter)."""

    points, owners = _mesh_points(meshes)
    triangles = _mesh_triangles(owners)
    load = qload.find_load(points, triangles) if options.get("load") else None
    turned = quarter = False
    if not payload.get("landmarks"):
        body = points[~load.mask] if load is not None else points
        # A winged body's spread wings can be wider than it is long: its four feet set its long axis (quadruped_layout.feet_axis_along_x).
        along_x = ql.feet_axis_along_x(body) if options.get("wings") else None
        if along_x if along_x is not None else float(np.ptp(body[:, 0])) > float(np.ptp(body[:, 1])):
            _turn_quarter(meshes, points)
            points, owners = _mesh_points(meshes)
            body = points[~load.mask] if load is not None else points
            quarter = True
        if ql.faces_plus_y(body):
            _turn_half(meshes, points)
            points, owners = _mesh_points(meshes)
            turned = True
    if load is not None:
        load = qload.find_load(points, triangles)
    return points, owners, triangles, load, turned, quarter


def _seat_on_load(points: np.ndarray, triangles: np.ndarray, load: Any, landmarks: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    """Place the Saddle_Node on the load's clearest floor and cap the death's roll; record both in `landmarks` and return the report."""

    rider_height = float(options.get("rider_height") or 0.0)
    if rider_height <= 0:
        raise RuntimeError("A loaded mount needs rig_options.rider_height (the rider's height in this model's units) to place its Saddle_Node.")
    ground = float(points[:, 2].min())
    seat = qload.fit_rider(points, triangles, load, rider_height, options.get("rider_footprint"))
    landmarks["saddle"] = np.asarray(seat["point"], dtype=float) - np.array([0.0, 0.0, ground])
    torso = points[:, 2] - ground > float(landmarks["belly_z"])
    axis = np.array([0.0, 1.0, 0.0])
    roll = qload.roll_limit(points, load.mask, torso, axis, ql.COLLAPSE_ROLL)
    other = qload.roll_limit(points, load.mask, torso, axis, -ql.COLLAPSE_ROLL)
    landmarks["load"] = {"roll_limit": roll, "roll_limit_other_side": other, "bone": qload.LOAD_BONE}
    return {**load.summary(float(np.ptp(points[:, 2]))), "saddle": _jsonable(seat), "roll_limit": roll, "roll_limit_other_side": other, "bone": qload.LOAD_BONE}


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
    options = dict(payload.get("rig_options") or {})
    points, owners, triangles, load, turned, quarter = _orient(meshes, payload, options)
    body = points[~load.mask] if load is not None else points
    ground = float(points[:, 2].min())
    wing_plans, wing_masks = _find_wings(points, triangles, options) if not payload.get("landmarks") else ({}, {})
    wing_any = np.zeros(len(points), bool)
    for mask in wing_masks.values():
        wing_any |= mask
    if wing_any.any():
        body = body if load is not None else points[~wing_any]
    landmarks = _landmarks_from_payload(body, payload, back_z=(load.cut_z - ground) if load is not None else None)
    if wing_plans:
        landmarks["wings"] = wing_plans
        # a winged body's neck is a thin column under a large head: the neck bones run up it (quadruped_layout.detect_neck)
        neck = ql.detect_neck(body, landmarks)
        if neck is not None:
            landmarks["neck"] = neck
    load_report = _seat_on_load(points, triangles, load, landmarks, options) if load is not None else {}
    ear_masks = _find_ears(points, triangles, landmarks, load, wing_any if wing_any.any() else None)
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
    if load is not None:
        indices, weights, bound = qload.bind_load(points, load.mask, indices, weights, layout.names(), qload.RING_SHARE * float(landmarks["height"]))
        load_report.update(bound)
    indices, weights = qears.ear_weights(points, triangles, layout, ear_masks, indices, weights, ring=qload.RING_SHARE * float(landmarks["height"]))
    if wing_plans:
        indices, weights = qwings.wing_weights(points, triangles, layout.names(), wing_plans, wing_masks, indices, weights,
                                               float(landmarks["centre_x"]), float(landmarks["ground_offset"]) + float(landmarks["belly_z"]))
    per_bone, unweighted = _bind(owners, layout, indices, weights, rig)
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
        "turned_to_face_minus_y": turned,
        "turned_quarter_to_lie_along_y": quarter,
        "load": load_report or None,
        "weighting": "region-limited inverse fourth power of the distance to each bone segment"
        + ("; the load bound wholly to the Spine, fading into the body over a ring" if load is not None else "")
        + ("; each ear on its own two bones, blending into the head at its root" if ear_masks else ""),
        "ears": {side: {"vertices": int(mask.sum())} for side, mask in ear_masks.items()},
        "wings": {side: {"vertices": int(mask.sum()), "root": _jsonable(wing_plans[side]["root"]), "length": round(float(wing_plans[side]["length"]), 5),
                         "chains": int(np.asarray(wing_plans[side]["joints"]).shape[0]), "bones_per_chain": int(np.asarray(wing_plans[side]["joints"]).shape[1] - 1)}
                  for side, mask in wing_masks.items()},
    }


def _find_wings(points: np.ndarray, triangles: np.ndarray, options: Dict[str, Any]):
    """A winged body's wings (`quadruped_wings.detect_wings`): first landmarks on the whole model give its mid-plane and belly, the wings are
    found from them and the feet, and the caller measures the body again without them. ({}, {}) without `wings` in the rig options."""

    if not options.get("wings"):
        return {}, {}
    first = ql.detect_landmarks(points)
    feet, _dragged = ql.ground_contacts(points)
    plans, masks = qwings.detect_wings(points, triangles, first, feet)
    if not plans:
        raise RuntimeError("The job asks for a winged quadruped, but no wing stands out from the body's sides (quadruped_wings.wing_masks).")
    return plans, masks


def _find_ears(points: np.ndarray, triangles: np.ndarray, landmarks: Dict[str, Any], load: Any, wings: Any = None) -> Dict[str, np.ndarray]:
    """Find the ears beside the head (`quadruped_ears.detect_ears`), record their chains in `landmarks` and return their vertex masks. A wing is
    never an ear."""

    exclude = load.mask if load is not None else None
    if wings is not None:
        exclude = wings if exclude is None else (exclude | wings)
    ears, masks = qears.detect_ears(points, triangles, landmarks, exclude=exclude)
    if ears:
        qears.assign_parents(points, landmarks, ears, masks)
        landmarks["ears"] = ears
    return masks


def _rotation(rows: List[ql.Rotation]) -> Quaternion:
    result = Quaternion((1.0, 0.0, 0.0, 0.0))
    for axis, degrees in rows:
        result = Quaternion(Vector(axis), math.radians(degrees)) @ result
    return result


TORSO = ("Pelvis", "Spine", "Chest")
EAR_PREFIX = "Ear_"
WING_PREFIX = qwings.WING_PREFIX
TAIL_PREFIX = "Tail_"


def _dominant_groups(meshes: List[bpy.types.Object]) -> List[np.ndarray]:
    """Per mesh, each vertex's strongest vertex group name ("" for none)."""

    out = []
    for obj in meshes:
        names = {group.index: group.name for group in obj.vertex_groups}
        out.append(np.array([names.get(max(v.groups, key=lambda g: g.weight).group, "") if len(v.groups) else "" for v in obj.data.vertices]))
    return out


def _lowest_by_group(meshes: List[bpy.types.Object], dominant: List[np.ndarray]) -> Dict[str, float]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    lowest: Dict[str, float] = {}
    for obj, names in zip(meshes, dominant):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            local = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
            mesh.vertices.foreach_get("co", local)
            matrix = np.array(evaluated.matrix_world, dtype=np.float64)
            z = local.reshape(-1, 3).astype(np.float64) @ matrix[2, :3] + matrix[2, 3]
            for name in set(names.tolist()):
                lowest[name] = min(lowest.get(name, math.inf), float(z[names == name].min()))
        finally:
            evaluated.to_mesh_clear()
    return lowest


def tune_collapse(rig, meshes, layout: ql.Layout, last: int, pose_frame, ground: float) -> Dict[str, Any]:
    """Pick the death's side, roll and neck lift on its final pose (`quadruped_layout.choose_collapse`), so the body ends lying on its torso:
    neither a dropped head nor a load on the back may hold the dead body off the ground, and the neck turns against the roll only when
    the head or neck is what holds it up. An ear is a thin flap that folds against the ground, so it is left out of the parts that hold it."""

    dominant = _dominant_groups(meshes)
    height = float(layout.landmarks["height"])
    winged = bool(layout.landmarks.get("wings"))
    # a wing lies on the ground beside the dead body and a dragged tail along it: neither holds it up, and the tail is laid by its own rule
    thin = (EAR_PREFIX, WING_PREFIX, TAIL_PREFIX) if winged else (EAR_PREFIX,)

    def evaluate(roll: float, lift: float):
        # a winged body's legs underneath start the search without their drop toward the ground (choose_winged_rest adds what fits): with
        # it a hoof held the Tripo dragon's body up at every roll, and the fallback rolled it only 34 degrees, the torso 17% up
        layout.landmarks["death"] = {"roll": roll, "neck_lift": lift, **({"leg_drop": 0.0, "side_search": True} if winged else {})}
        pose_frame(last, 0.0)
        lowest = {name: z for name, z in _lowest_by_group(meshes, dominant).items() if not name.startswith(thin)}
        torso = min(lowest.get(name, math.inf) for name in TORSO)
        return (torso - min(lowest.values())) / height, min(lowest, key=lowest.get)

    chosen = ql.choose_collapse(evaluate, ql.roll_limits(layout.landmarks))
    layout.landmarks["death"] = {"roll": chosen["roll"], "neck_lift": chosen["neck_lift"]}
    if winged:
        def rest(**parts: float) -> Dict[str, float]:
            layout.landmarks["death"] = {"roll": chosen["roll"], "neck_lift": chosen["neck_lift"], **parts}
            pose_frame(last, 0.0)
            lowest = _lowest_by_group(meshes, dominant)
            torso = min(lowest.get(name, math.inf) for name in TORSO)

            def gap(prefixes) -> float:
                return (min((z for name, z in lowest.items() if name.startswith(prefixes)), default=torso) - torso) / height

            outer = tuple(name for name in lowest if name.startswith(WING_PREFIX + qwings.lower_side(chosen["roll"])) and name.endswith(f"_{qwings.WING_BONES}"))
            return {"legs": gap(("Front_", "Rear_")), "wings": gap(outer) if outer else 0.0, "tail": gap(TAIL_PREFIX), "head": gap("Head")}

        laid = ql.choose_winged_rest(rest)
        layout.landmarks["death"].update(laid)
        chosen = {**chosen, **laid}
    return chosen


def _torso_x(meshes: List[bpy.types.Object], torso: List[np.ndarray]) -> float:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total, count = 0.0, 0
    for obj, mask in zip(meshes, torso):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            local = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
            mesh.vertices.foreach_get("co", local)
            matrix = np.array(evaluated.matrix_world, dtype=np.float64)
            x = local.reshape(-1, 3).astype(np.float64) @ matrix[0, :3] + matrix[0, 3]
            total, count = total + float(x[mask].sum()), count + int(mask.sum())
        finally:
            evaluated.to_mesh_clear()
    return total / max(count, 1)


def _spot_keeper(meshes: List[bpy.types.Object], pose_frame):
    """A dying body lies where it stood: a function that, for the frame just posed, gives the sideways shift that keeps the torso's
    centre over its standing spot (a fresh review saw the fallen elephant a body width aside, out of the camera)."""

    torso = [np.isin(names, TORSO) for names in _dominant_groups(meshes)]
    pose_frame(0, 0.0)
    standing = _torso_x(meshes, torso)
    return lambda: standing - _torso_x(meshes, torso)


def _body_turn(pose: Dict[str, Any], rear_pivot: Vector, root_pivot: Vector, width: float) -> Matrix:
    """The whole body's turn: a rear pitches and a defend's sweep turns about the hind hooves, and a fall rolls about the edge of the side
    it falls toward, so the body lies where it stood. A defend's step back (`__root_shift__`) moves it."""

    shift = Matrix.Translation(sum((Vector(axis) * distance for axis, distance in pose.get("__root_shift__", [])), Vector((0.0, 0.0, 0.0))))
    if "__root_pitch__" in pose or "__root_yaw__" in pose:
        turn = _rotation(pose.get("__root_pitch__", []) + pose.get("__root_yaw__", [])).to_matrix().to_4x4()
        return shift @ Matrix.Translation(rear_pivot) @ turn @ Matrix.Translation(-rear_pivot)
    if "__root_roll__" in pose:
        degrees = pose["__root_roll__"][0][1]
        edge = root_pivot + Vector((math.copysign(0.5 * width, degrees), 0.0, 0.0))
        turn = _rotation(pose["__root_roll__"]).to_matrix().to_4x4()
        return shift @ Matrix.Translation(edge) @ turn @ Matrix.Translation(-edge)
    return shift


def _whole_turn(pose: Dict[str, Any], rear_pivot: Vector, root_pivot: Vector, width: float) -> Matrix:
    """`_body_turn`, then a turn about the vertical through the body's middle (`__root_turn__`: a winged retreat turns away and back)."""

    body = _body_turn(pose, rear_pivot, root_pivot, width)
    if "__root_turn__" not in pose:
        return body
    turn = _rotation(pose["__root_turn__"]).to_matrix().to_4x4()
    return Matrix.Translation(root_pivot) @ turn @ Matrix.Translation(-root_pivot) @ body


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
    asked, style = style, ql.stance_style(style, landmarks)  # a graviportal animal never gallops
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

    def pose_frame(frame: int, lift: float, shift: float = 0.0) -> None:
        pose = ql.pose_at(style, frame, layout)
        for bone in rig.pose.bones:
            bone.rotation_mode = "QUATERNION"
            bone.location = (0.0, 0.0, 0.0)
            rows = pose.get(bone.name)
            if rows and bone.name != "Root":
                bone.rotation_quaternion = rest[bone.name].inverted() @ _rotation(rows) @ rest[bone.name]
            else:
                bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        body = _whole_turn(pose, rear_pivot, root_pivot, float(landmarks["width"]))
        rig.pose.bones["Root"].matrix = Matrix.Translation((shift, 0.0, lift)) @ body @ root_rest
        bpy.context.view_layer.update()

    dying = style in ("quadruped_collapse", "winged_collapse")
    tuned = tune_collapse(rig, meshes, layout, last, pose_frame, ground) if dying else None
    keep_spot = _spot_keeper(meshes, pose_frame) if dying else None
    contact_before, contact_after = [], []
    for frame in range(0, last + 1):
        scene.frame_set(frame)
        pose_frame(frame, 0.0)
        lowest, shift = _evaluated_min_z(meshes) - ground, keep_spot() if keep_spot else 0.0
        contact_before.append(lowest)
        pose_frame(frame, -lowest, shift)
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
        "collapse": tuned,
        "asked_style": asked,
        "stance": ql.leg_stance(landmarks),
    }
