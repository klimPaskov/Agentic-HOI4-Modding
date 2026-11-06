"""Helpers for authoring a unit's animations live in Blender, through an interactive Blender MCP.

Load them inside the live Blender session (one `execute_blender_code` call):

    import importlib, sys
    sys.path.insert(0, r"<repository>/.tools/3d_pipeline/authoring")
    import live_helpers as h
    importlib.reload(h)

Keep the module on `sys.path` this way: opening a `.blend` clears `bpy.app.driver_namespace`, so
helpers stored there vanish.

What they are for (the escalation path of `docs/3d-units.md`): you choose every pose, one bone or one
limb at a time, look at a viewport render, and key it. The helpers only turn, place, measure, render
and key what you name at the call site. None of them makes keys from a table, a curve, a loop over
frames or another clip, so authoring stays live (decisions 3D-3 and 3D-5). Weight helpers correct
existing weights only.

Rules learned on the Chaos Redux and ZIN units:

- Pose, key and measure in the same call. Between calls the session evaluates the action again, so
  an unkeyed pose set in one call is gone in the next.
- Split long work (an export plus dozens of renders) into several calls; the bridge times out while
  Blender keeps working. Confirm results by file timestamps.
- Knees bend toward the toes. `place_limb` and `solve_leg` bend toward the direction you give, and
  `knee_bend` measures it, so check every leg key.
- Ground per key from the lowest skinned vertex of each foot (`plant`), not from the bone.
- Store a hand's grip in the prop's own frame (`grip_record`) and seat it from that frame at every
  key (`seat_grip`). A grip kept in world space floats off the prop as soon as the prop moves.
- Lift a hunched head by spreading the pitch down the spine (`lean`), not at the neck: a neck pitch
  tears chin fur from the chest.

Blender's axes: Z up. The kit's units face -Y.
"""

from __future__ import annotations

import math
import os
from typing import Dict, Iterable, List, Optional, Sequence

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

OUT = os.environ.get("HOI4_LIVE_SHOTS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
# Views as (azimuth, elevation) in degrees. Azimuth 0 looks at the unit's face (the unit faces -Y).
VIEWS = {"front": (0, 8), "left": (90, 8), "right": (270, 8), "back": (180, 8), "hoi4": (25, 55), "q": (35, 15)}
FORWARD = Vector((0.0, -1.0, 0.0))


# ---- scene and renders ----


def arm(name: Optional[str] = None):
    """The armature (the named one, or the first in the file)."""

    if name:
        return bpy.data.objects[name]
    return next(o for o in bpy.data.objects if o.type == "ARMATURE")


def setup_scene(size: int = 360) -> None:
    """Workbench renders like the kit's review sheets: back faces culled, magenta background, a ground disc."""

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE"
    scene.display.shading.show_backface_culling = True
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.film_transparent = False
    scene.display.shading.background_type = "VIEWPORT"
    scene.display.shading.background_color = (0.55, 0.0, 0.55)
    if "live_cam" not in bpy.data.objects:
        data = bpy.data.cameras.new("live_cam")
        data.type = "ORTHO"
        camera = bpy.data.objects.new("live_cam", data)
        scene.collection.objects.link(camera)
    scene.camera = bpy.data.objects["live_cam"]
    if "ground_disc" not in bpy.data.objects:
        mesh = bpy.data.meshes.new("ground_disc")
        points = [(4.5 * math.cos(2 * math.pi * i / 48), 4.5 * math.sin(2 * math.pi * i / 48), 0.0) for i in range(48)]
        mesh.from_pydata(points, [], [list(range(48))])
        disc = bpy.data.objects.new("ground_disc", mesh)
        material = bpy.data.materials.new("ground_mat")
        material.diffuse_color = (0.35, 0.4, 0.35, 1.0)
        mesh.materials.append(material)
        scene.collection.objects.link(disc)


def flat_colours(enable: bool = True, props: Iterable[str] = (), prop_colour=(1.0, 0.85, 0.0, 1.0)) -> None:
    """Show flat object colours instead of textures, with the named prop objects in a contrasting colour.

    Dark-coated units render nearly black with textures, so a reviewer cannot see whether a hand
    closes on a prop. Flat colours make hand and prop contact readable.
    """

    shading = bpy.context.scene.display.shading
    shading.color_type = "OBJECT" if enable else "TEXTURE"
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name != "ground_disc":
            obj.color = prop_colour if obj.name in set(props) else (0.72, 0.72, 0.75, 1.0)


def _place(view: str, centre: Vector, span: float) -> None:
    camera = bpy.data.objects["live_cam"]
    azimuth, elevation = (math.radians(v) for v in VIEWS[view])
    direction = Vector((math.sin(azimuth) * math.cos(elevation), -math.cos(azimuth) * math.cos(elevation), math.sin(elevation)))
    camera.location = centre + direction * span * 6
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera.data.ortho_scale = span * 1.45
    camera.data.clip_end = span * 20


def _render_tile(view: str, centre: Vector, span: float) -> np.ndarray:
    scene = bpy.context.scene
    _place(view, centre, span)
    path = os.path.join(OUT, f"_tile_{view}.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path, check_existing=False)
    width, height = image.size
    pixels = np.array(image.pixels[:], dtype=np.float32).reshape(height, width, 4)
    bpy.data.images.remove(image)
    return pixels


def _save(tag: str, tiles: List[np.ndarray]) -> str:
    sheet = np.concatenate(tiles, axis=1)
    height, width = sheet.shape[:2]
    image = bpy.data.images.new(tag, width, height, alpha=True)
    image.pixels = sheet.ravel()
    path = os.path.join(OUT, f"{tag}.png")
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)
    return path


def body_frame(objects: Optional[Sequence[str]] = None):
    """(centre, span) that frames the evaluated meshes, for `shot` and `strip`."""

    points = np.concatenate([eval_co(o.name) for o in bpy.data.objects if o.type == "MESH" and o.name != "ground_disc" and (not objects or o.name in objects)])
    low, high = points.min(axis=0), points.max(axis=0)
    return Vector(((low + high) / 2).tolist()), float(max(high - low)) * 1.1


def shot(tag: str, frame: Optional[int] = None, views=("front", "left", "hoi4"), centre=None, span=None, close=None) -> str:
    """Render the given views at a frame and tile them into `shots/<tag>.png`; returns the path.

    `close` maps a view to its own (centre, span), for a close-up of a hand or a foot.
    """

    os.makedirs(OUT, exist_ok=True)
    if frame is not None:
        bpy.context.scene.frame_set(frame)
    if centre is None or span is None:
        centre, span = body_frame()
    tiles = []
    for view in views:
        c, s = (Vector(close[view][0]), close[view][1]) if close and view in close else (Vector(centre), span)
        tiles.append(_render_tile(view, c, s))
    return _save(tag, tiles)


def strip(tag: str, frames: Sequence[int], view: str = "front", centre=None, span=None) -> str:
    """Render one view at several frames side by side, to judge timing."""

    os.makedirs(OUT, exist_ok=True)
    if centre is None or span is None:
        centre, span = body_frame()
    tiles = []
    for frame in frames:
        bpy.context.scene.frame_set(frame)
        tiles.append(_render_tile(view, Vector(centre), span))
    return _save(tag, tiles)


# ---- reading the rig ----


def bone_world(bone: str, tail: bool = False) -> List[float]:
    rig = arm()
    pose_bone = rig.pose.bones[bone]
    bpy.context.view_layer.update()
    return list(rig.matrix_world @ (pose_bone.tail if tail else pose_bone.head))


def rest_forward(foot: str, toe: Optional[str] = None) -> Vector:
    """The unit's forward direction from the rest pose: ankle to toe, flattened. Falls back to -Y."""

    bones = arm().data.bones
    if toe and toe in bones:
        direction = bones[toe].head_local - bones[foot].head_local
    else:
        direction = bones[foot].tail_local - bones[foot].head_local
    direction = arm().matrix_world.to_3x3() @ direction
    direction.z = 0.0
    return direction.normalized() if direction.length > 1e-6 else FORWARD.copy()


def eval_co(name: str) -> np.ndarray:
    """World positions of an object's evaluated (posed and skinned) vertices."""

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj = bpy.data.objects[name]
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    co = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", co)
    evaluated.to_mesh_clear()
    world = np.array(obj.matrix_world)
    return co.reshape(-1, 3) @ world[:3, :3].T + world[:3, 3]


def lowest_z(names: Optional[Sequence[str]] = None) -> float:
    """Lowest world height of the evaluated meshes."""

    heights = [eval_co(o.name)[:, 2].min() for o in bpy.data.objects if o.type == "MESH" and o.name != "ground_disc" and (not names or o.name in names)]
    return float(min(heights))


def group_vertices(mesh_name: str, groups: Sequence[str], threshold: float = 0.3) -> np.ndarray:
    """Indices of the vertices weighted above `threshold` to any of the named vertex groups."""

    obj = bpy.data.objects[mesh_name]
    wanted = {obj.vertex_groups[g].index for g in groups if g in obj.vertex_groups}
    return np.array([v.index for v in obj.data.vertices if any(g.group in wanted and g.weight > threshold for g in v.groups)], dtype=np.int64)


def group_low(mesh_name: str, groups: Sequence[str], threshold: float = 0.3) -> float:
    """Lowest evaluated height among vertices weighted to the named groups (one foot's ground contact)."""

    indices = group_vertices(mesh_name, groups, threshold)
    return float(eval_co(mesh_name)[indices, 2].min()) if len(indices) else math.inf


# ---- posing one bone or one limb ----


def rot(bone: str, axis, degrees: float) -> None:
    """Turn one pose bone about a world axis through its head, like R <axis> <degrees> in the viewport."""

    rig = arm()
    pose_bone = rig.pose.bones[bone]
    bpy.context.view_layer.update()
    head = rig.matrix_world @ pose_bone.head
    turn = Matrix.Translation(head) @ Matrix.Rotation(math.radians(degrees), 4, Vector(axis)) @ Matrix.Translation(-head)
    pose_bone.matrix = rig.matrix_world.inverted() @ turn @ rig.matrix_world @ pose_bone.matrix
    bpy.context.view_layer.update()


def _turn_world(bone: str, quaternion: Quaternion) -> None:
    rig = arm()
    pose_bone = rig.pose.bones[bone]
    bpy.context.view_layer.update()
    head = rig.matrix_world @ pose_bone.head
    turn = Matrix.Translation(head) @ quaternion.to_matrix().to_4x4() @ Matrix.Translation(-head)
    pose_bone.matrix = rig.matrix_world.inverted() @ turn @ rig.matrix_world @ pose_bone.matrix
    bpy.context.view_layer.update()


def move(bone: str, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
    """Move one pose bone in world space, like G in the viewport."""

    rig = arm()
    pose_bone = rig.pose.bones[bone]
    bpy.context.view_layer.update()
    matrix = pose_bone.matrix.copy()
    matrix.translation = matrix.translation + rig.matrix_world.inverted().to_3x3() @ Vector((dx, dy, dz))
    pose_bone.matrix = matrix
    bpy.context.view_layer.update()


def lean(bones: Sequence[str], degrees: float, shares: Optional[Sequence[float]] = None, axis=(1.0, 0.0, 0.0)) -> None:
    """Pitch the body by `degrees`, spread over a spine chain (lowest bone first) by `shares`.

    The ZIN yeti's head lift tore its chin fur when the whole pitch sat on the neck; spreading it
    0.3, 0.35, 0.35 over Spine02, Spine01 and Spine read just as upright without the tear.
    """

    shares = list(shares or [1.0 / len(bones)] * len(bones))
    for bone, share in zip(bones, shares):
        rot(bone, axis, degrees * share)


def key(bones: Iterable[str], frame: int) -> None:
    """Key location and rotation of the named bones at one frame (the I key)."""

    rig = arm()
    for bone in bones:
        pose_bone = rig.pose.bones[bone]
        pose_bone.keyframe_insert("location", frame=frame)
        if pose_bone.rotation_mode == "QUATERNION":
            pose_bone.keyframe_insert("rotation_quaternion", frame=frame)
        else:
            pose_bone.keyframe_insert("rotation_euler", frame=frame)


def clear_pose(bones: Optional[Iterable[str]] = None) -> None:
    rig = arm()
    chosen = set(bones) if bones is not None else None
    for pose_bone in rig.pose.bones:
        if chosen is None or pose_bone.name in chosen:
            pose_bone.location = (0.0, 0.0, 0.0)
            pose_bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
            pose_bone.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()


def new_action(name: str, frames: int):
    """Start (or reopen) an action on the armature and set the scene to its frames."""

    rig = arm()
    rig.animation_data_create()
    action = bpy.data.actions.get(name) or bpy.data.actions.new(name)
    action.use_fake_user = True
    rig.animation_data.action = action
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, frames
    return action


def snap() -> Dict[str, tuple]:
    """Every bone's local location and rotation, to restore with `load`."""

    return {b.name: (tuple(b.location), tuple(b.rotation_quaternion)) for b in arm().pose.bones}


def load(saved: Dict[str, tuple]) -> None:
    rig = arm()
    for name, (location, rotation) in saved.items():
        rig.pose.bones[name].location = location
        rig.pose.bones[name].rotation_quaternion = rotation
    bpy.context.view_layer.update()


def ikp(tip: str, target, chain: int, names: Sequence[str], pole=None, pole_angle: float = 0.0) -> None:
    """Solve one IK chain to a target once, copy the visual pose into the bones, remove the constraint."""

    rig = arm()
    collection = bpy.context.scene.collection
    empty = bpy.data.objects.get("ik_t") or bpy.data.objects.new("ik_t", None)
    if empty.name not in collection.objects:
        collection.objects.link(empty)
    empty.location = Vector(target)
    constraint = rig.pose.bones[tip].constraints.new("IK")
    constraint.target = empty
    constraint.chain_count = chain
    if pole is not None:
        pole_empty = bpy.data.objects.get("ik_p") or bpy.data.objects.new("ik_p", None)
        if pole_empty.name not in collection.objects:
            collection.objects.link(pole_empty)
        pole_empty.location = Vector(pole)
        constraint.pole_target = pole_empty
        constraint.pole_angle = math.radians(pole_angle)
    bpy.context.view_layer.update()
    posed = {name: rig.pose.bones[name].matrix.copy() for name in names}
    rig.pose.bones[tip].constraints.remove(constraint)
    bpy.context.view_layer.update()
    for name in names:
        rig.pose.bones[name].matrix = posed[name]
        bpy.context.view_layer.update()


def reach(hand: str, upper: str, fore: str, want, iterations: int = 3) -> List[float]:
    """Put a wrist (the hand bone's head) at a chosen point with a temporary two-bone IK on the arm.

    Blender's IK aims the tip bone's tail, so the solve runs on the forearm, whose tail is the wrist;
    the hand keeps its turn relative to the forearm. The residual is corrected a few times.
    """

    want = Vector(want)
    target = want.copy()
    for _ in range(iterations):
        ikp(fore, target, 2, [upper, fore])
        target = target + (want - Vector(bone_world(hand)))
    return [round(v, 4) for v in bone_world(hand)]


def place_limb(upper: str, lower: str, end: str, target, pole, keep_end: Optional[Matrix] = None):
    """Put the head of `end` at `target` by turning `upper` and `lower` only, bending toward `pole`.

    `pole` is a world direction: for a leg, the unit's forward direction (`rest_forward`), so the knee
    bends toward the toes. Segment lengths are head-to-head distances, so it works on rigs whose bone
    tails do not follow the limb. `keep_end` is an armature-space matrix whose rotation the end bone
    keeps (a flat foot), or None to let it follow.
    """

    hip = Vector(bone_world(upper))
    knee = Vector(bone_world(lower))
    ankle = Vector(bone_world(end))
    goal = Vector(target)
    first, second = (knee - hip).length, (ankle - knee).length
    along = goal - hip
    distance = min(along.length, first + second - 1e-4)
    direction = along.normalized()
    side = Vector(pole)
    side = (side - direction * side.dot(direction)).normalized()
    x = (first * first - second * second + distance * distance) / (2 * distance)
    y = math.sqrt(max(first * first - x * x, 0.0))
    middle = hip + direction * x + side * y
    _turn_world(upper, (knee - hip).rotation_difference(middle - hip))
    knee_now, ankle_now = Vector(bone_world(lower)), Vector(bone_world(end))
    _turn_world(lower, (ankle_now - knee_now).rotation_difference(hip + direction * distance - knee_now))
    if keep_end is not None:
        flat_foot(end, keep_end)
    return [round(v, 4) for v in bone_world(end)], [round(v, 4) for v in bone_world(lower)]


def flat_foot(foot: str, rest_matrix: Matrix) -> None:
    """Give a foot the rotation of `rest_matrix` (armature space) at its current position."""

    rig = arm()
    matrix = rest_matrix.copy()
    matrix.translation = rig.pose.bones[foot].matrix.translation
    rig.pose.bones[foot].matrix = matrix
    bpy.context.view_layer.update()


def solve_leg(upper: str, lower: str, foot: str, ankle_target, toe: Optional[str] = None, keep_foot: bool = True):
    """Put an ankle at a chosen point with the knee toward the toes; the foot keeps its current turn."""

    forward = rest_forward(foot, toe)
    keep = arm().pose.bones[foot].matrix.copy() if keep_foot else None
    return place_limb(upper, lower, foot, ankle_target, forward, keep)


def knee_bend(upper: str, lower: str, foot: str, forward=None) -> float:
    """How far the knee sits ahead of the hip-to-ankle line, as a share of leg length (negative is backward).

    The same measure as UNIT-ANIM-KNEE in check_unit_files.py, at the current frame; `forward` defaults
    to the rest forward turned by the pelvis (the hip bone's parent).
    """

    hip, knee, ankle = (Vector(bone_world(b)) for b in (upper, lower, foot))
    if forward is None:
        rig = arm()
        parent = rig.pose.bones[upper].parent
        forward = rest_forward(foot)
        if parent is not None:
            turn = (rig.matrix_world @ parent.matrix).to_3x3() @ (rig.matrix_world @ parent.bone.matrix_local).to_3x3().inverted()
            forward = turn @ forward
    axis = (ankle - hip).normalized()
    offset = (knee - hip) - axis * (knee - hip).dot(axis)
    facing = Vector(forward) - axis * Vector(forward).dot(axis)
    length = (knee - hip).length + (ankle - knee).length
    if facing.length < 1e-6 or length <= 0:
        return 0.0
    return offset.dot(facing.normalized()) / length


def plant(frame: int, upper: str, lower: str, foot: str, groups: Sequence[str], mesh_name: str, ground: float = 0.0, toe: Optional[str] = None) -> float:
    """At one frame, lift or lower one leg so its lowest skinned vertex sits on the ground, and key that leg.

    A ground correction of a pose you already made, not a new pose: the foot keeps its turn, the knee
    keeps bending toward the toes. Returns the remaining gap.
    """

    rig = arm()
    scene = bpy.context.scene
    scene.frame_set(frame)
    action = rig.animation_data.action if rig.animation_data else None
    if action is not None:
        rig.animation_data.action = None  # hold the evaluated pose while the leg moves
    keep = rig.pose.bones[foot].matrix.copy()
    forward = rest_forward(foot, toe)
    for _ in range(3):
        ankle = Vector(bone_world(foot))
        low = group_low(mesh_name, groups)
        place_limb(upper, lower, foot, (ankle.x, ankle.y, ankle.z - (low - ground)), forward, keep)
    remaining = group_low(mesh_name, groups) - ground
    if action is not None:
        rig.animation_data.action = action
    key([upper, lower, foot], frame)
    return round(remaining, 4)


# ---- weights ----


def seam_vertices(mesh_name: str, first: str, second: str, hard: float = 0.1) -> List[int]:
    """Vertices on edges between `first`'s and `second`'s regions whose weights do not blend across.

    For a crotch, `first` and `second` are the two thigh bones (UNIT-SEAM names the pair).
    """

    obj = bpy.data.objects[mesh_name]
    index = {group.name: group.index for group in obj.vertex_groups}
    if first not in index or second not in index:
        return []
    a, b = index[first], index[second]

    def weights(vertex) -> Dict[int, float]:
        return {g.group: g.weight for g in vertex.groups}

    found = set()
    for edge in obj.data.edges:
        v0, v1 = (obj.data.vertices[i] for i in edge.vertices)
        w0, w1 = weights(v0), weights(v1)
        if not w0 or not w1:
            continue
        top0, top1 = max(w0, key=w0.get), max(w1, key=w1.get)
        if {top0, top1} != {a, b}:
            continue
        if max(w0.get(top1, 0.0), w1.get(top0, 0.0)) < hard:
            found.update(edge.vertices)
    return sorted(found)


def weight_seam(mesh_name: str, vertices: Sequence[int], pelvis: str, near_far: Sequence[str], shares=(0.40, 0.36, 0.24)) -> int:
    """Re-weight seam vertices across the pelvis and both limbs: pelvis, the limb the vertex followed, the other.

    The portal raider's crotch tore to 20.8 % of its height while each side followed one thigh; pelvis
    0.40, near thigh 0.36 and far thigh 0.24 brought its worst stretch from 25.5 % to about 14 %.
    Returns the number of vertices changed.
    """

    obj = bpy.data.objects[mesh_name]
    groups = {name: obj.vertex_groups[name] for name in (pelvis, *near_far)}
    first, second = near_far
    changed = 0
    for index in vertices:
        vertex = obj.data.vertices[index]
        current = {obj.vertex_groups[g.group].name: g.weight for g in vertex.groups}
        near, far = (first, second) if current.get(first, 0.0) >= current.get(second, 0.0) else (second, first)
        for group in obj.vertex_groups:
            if group.name not in groups:
                group.remove([index])
        groups[pelvis].add([index], shares[0], "REPLACE")
        groups[near].add([index], shares[1], "REPLACE")
        groups[far].add([index], shares[2], "REPLACE")
        changed += 1
    obj.data.update()
    return changed


# ---- props held in the hand ----


def prop_frame(base: str, tip: str):
    """(origin, 3x3 rotation) of a prop from two of its bones or locators: base to tip is the prop's axis."""

    origin = Vector(bone_world(base))
    axis = (Vector(bone_world(tip)) - origin).normalized()
    side = axis.cross(Vector((0.0, 0.0, 1.0)))
    if side.length < 1e-6:
        side = axis.cross(Vector((0.0, 1.0, 0.0)))
    side.normalize()
    up = side.cross(axis).normalized()
    return origin, Matrix((side, axis, up)).transposed()


def grip_record(hand: str, base: str, tip: str, fingers: Sequence[str] = ()) -> dict:
    """The hand's wrist position and turn, and its fingers' rotations, in the prop's own frame.

    Make the grip once by eye (close-up shots), record it, and seat it at every key with `seat_grip`.
    """

    rig = arm()
    origin, frame = prop_frame(base, tip)
    wrist = Vector(bone_world(hand))
    world_turn = (rig.matrix_world @ rig.pose.bones[hand].matrix).to_3x3()
    return {
        "position": list(frame.inverted() @ (wrist - origin)),
        "rotation": [list(row) for row in frame.inverted() @ world_turn.normalized()],
        "fingers": {name: list(rig.pose.bones[name].rotation_quaternion) for name in fingers},
        "prop": [base, tip],
    }


def seat_grip(grip: dict, hand: str, upper: str, fore: str, frame: Optional[int] = None) -> float:
    """Put the hand back on the prop from a `grip_record`, wherever the prop is now; key it at `frame`.

    Returns the wrist's distance from the recorded grip point after the reach.
    """

    rig = arm()
    base, tip = grip["prop"]
    origin, axes = prop_frame(base, tip)
    point = origin + axes @ Vector(grip["position"])
    reach(hand, upper, fore, point)
    wanted = rig.matrix_world.to_3x3().inverted() @ (axes @ Matrix(grip["rotation"]))
    pose_bone = rig.pose.bones[hand]
    matrix = wanted.to_4x4()
    matrix.translation = pose_bone.matrix.translation
    pose_bone.matrix = matrix
    bpy.context.view_layer.update()
    for name, rotation in grip["fingers"].items():
        rig.pose.bones[name].rotation_quaternion = rotation
    bpy.context.view_layer.update()
    if frame is not None:
        key([upper, fore, hand, *grip["fingers"]], frame)
    return round((Vector(bone_world(hand)) - point).length, 4)


def knuckle_line(index_finger: str, little_finger: str) -> Vector:
    """The direction from the little finger's base to the index finger's base, from the current pose.

    Turn a main hand so this line runs up a raked grip with the fingers across it; turn a support hand
    so it runs along the barrel with the palm on the top surface.
    """

    return (Vector(bone_world(index_finger)) - Vector(bone_world(little_finger))).normalized()


def grip_gap(points, prop_name: str) -> float:
    """Smallest distance from the given world points (knuckles, a fist centre) to a prop's evaluated surface."""

    co = eval_co(prop_name)
    return float(min(np.linalg.norm(co - np.array(p), axis=1).min() for p in points))
