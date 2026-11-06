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

Rules learned while authoring units this way:

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

import importlib
import math
import os
import sys
from typing import Dict, Iterable, List, Optional, Sequence

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

# One definition of "stretched": the kit's own constants (UNIT-ANIM-STRETCH), not a copy.
PIPELINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PIPELINE_ROOT not in sys.path:
    sys.path.insert(0, PIPELINE_ROOT)
from lib import pdx_deform
from lib.pdx_deform import SIGNIFICANT_SHARE, SQUASH_RATIO, STRETCH_RATIO

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
    if not bpy.data.actions:
        # Author at HOI4's rate from the start; a factory scene runs at 24 (export_clip retimes otherwise).
        scene.render.fps, scene.render.fps_base = 30, 1.0
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

    A yeti's head lift tore its chin fur when the whole pitch sat on the neck; spreading it 0.3, 0.35,
    0.35 over Spine02, Spine01 and Spine read just as upright without the tear.
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


# ---- measuring and repairing a pose ----


def _action_fcurves(action):
    """Every F-curve of an action: layered actions (Blender 4.4 and later) first, then the flat list."""

    found = []
    for layer in getattr(action, "layers", ()):
        for action_strip in layer.strips:
            for bag in getattr(action_strip, "channelbags", ()):
                found.extend(bag.fcurves)
    return found or list(getattr(action, "fcurves", ()))


def _quaternion_flips(keys: Sequence[Sequence[float]]) -> List[bool]:
    """Which quaternions in a time-ordered list to negate so each is in the same hemisphere as the one before.

    The decision compares with the previous key after its own flip, so a run of flipped keys stays
    consistent. Negating all four components is the same rotation.
    """

    flips: List[bool] = []
    previous = None
    for quaternion in keys:
        current = [float(v) for v in quaternion]
        flip = previous is not None and sum(a * b for a, b in zip(previous, current)) < 0.0
        if flip:
            current = [-v for v in current]
        flips.append(bool(flip))
        previous = current
    return flips


def normalize_quaternion_keys(action_name: str) -> int:
    """Flip quaternion keys that sit in the opposite hemisphere from the key before, so interpolation takes the short way.

    A key and its negation are the same rotation, but blending between keys whose dot product is
    negative swings the long way round (a polearm's blade sweeps through the ground). For every pose
    bone's `rotation_quaternion` curves in the action, each key whose quaternion has a negative dot
    with the previous key's is negated in all four components. Run it before export. Returns the
    number of keys flipped.
    """

    action = bpy.data.actions[action_name]
    curves: Dict[str, Dict[int, object]] = {}
    for curve in _action_fcurves(action):
        if curve.data_path.endswith(".rotation_quaternion") and 0 <= curve.array_index <= 3:
            curves.setdefault(curve.data_path, {})[curve.array_index] = curve
    flipped = 0
    for channels in curves.values():
        if len(channels) != 4 or len({len(c.keyframe_points) for c in channels.values()}) != 1:
            continue  # a partly keyed quaternion has no sign to compare
        count = len(channels[0].keyframe_points)
        order = sorted(range(count), key=lambda i: channels[0].keyframe_points[i].co.x)
        quaternions = [[channels[c].keyframe_points[i].co.y for c in range(4)] for i in order]
        for index, flip in zip(order, _quaternion_flips(quaternions)):
            if not flip:
                continue
            for channel in channels.values():
                point = channel.keyframe_points[index]
                point.co.y = -point.co.y
                point.handle_left.y = -point.handle_left.y
                point.handle_right.y = -point.handle_right.y
            flipped += 1
    for channels in curves.values():
        for channel in channels.values():
            channel.update()
    return flipped


def _welded_edges(rest: np.ndarray, raw_edges: np.ndarray, height: float) -> np.ndarray:
    """Unique undirected edges over welded vertices, the way the kit builds them (`pdx_deform.mesh_edges`)."""

    canon = pdx_deform.weld(rest, max(height, 1e-6) * 1e-5)
    edges = np.sort(canon[raw_edges], axis=1)
    edges = edges[edges[:, 0] != edges[:, 1]]
    return np.unique(edges, axis=0)


def _stretch_edge_share(rest: np.ndarray, moved: np.ndarray, edges: np.ndarray, height: float) -> float:
    """The kit's UNIT-ANIM-STRETCH test on one posed frame: the share of edges stretched or squashed."""

    if len(edges) == 0:
        return 0.0
    rest_length = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
    length = np.linalg.norm(moved[edges[:, 0]] - moved[edges[:, 1]], axis=1)
    usable = rest_length > 1e-9
    growth = (length - rest_length) / max(height, 1e-6)
    ratio = np.where(usable, length / np.where(usable, rest_length, 1.0), 1.0)
    stretched = (ratio > STRETCH_RATIO) & (growth > SIGNIFICANT_SHARE)
    squashed = (ratio < SQUASH_RATIO) & (-growth > SIGNIFICANT_SHARE)
    return float((stretched | squashed).sum()) / len(edges)


def stretch_share(mesh_name: str, frame: Optional[int] = None) -> float:
    """The share of a mesh's edges that the kit's UNIT-ANIM-STRETCH counts as stretched or squashed at a frame.

    It is the kit's own measure, not a lookalike: the same constants (`STRETCH_RATIO`, `SQUASH_RATIO`,
    `SIGNIFICANT_SHARE`), the same welding of rest positions (height times 1e-5) and the same unique
    edges. An edge counts when its length is over `STRETCH_RATIO` times (or under `SQUASH_RATIO` times)
    its rest length and it changed by more than `SIGNIFICANT_SHARE` of the mesh's rest height. A hand
    made gauge read about 0.8 times this number, so use this one and keep it under the kit's limit.
    """

    if frame is not None:
        bpy.context.scene.frame_set(frame)
    obj = bpy.data.objects[mesh_name]
    world = np.array(obj.matrix_world)
    count = len(obj.data.vertices)
    rest = np.empty(count * 3, dtype=np.float32)
    obj.data.vertices.foreach_get("co", rest)
    rest = rest.reshape(-1, 3).astype(np.float64) @ world[:3, :3].T + world[:3, 3]
    moved = eval_co(mesh_name).astype(np.float64)
    if len(moved) != count:
        raise RuntimeError(f"{mesh_name} changes its vertex count when evaluated, so its edges cannot be compared")
    raw = np.empty(len(obj.data.edges) * 2, dtype=np.int64)
    obj.data.edges.foreach_get("vertices", raw)
    height = float(np.ptp(rest[:, 2])) if count else 0.0
    return _stretch_edge_share(rest, moved, _welded_edges(rest, raw.reshape(-1, 2), height), height)


def _region_for_bone(bone: str) -> str:
    """The body region a bone name belongs to: head, chest, hips, arms, hands, legs, feet, tail, wings or other."""

    name = bone.lower()
    for region, words in (
        ("tail", ("tail",)),
        ("wings", ("wing",)),
        ("feet", ("foot", "toe", "ankle", "hoof", "paw")),
        ("hands", ("hand", "finger", "thumb", "palm")),
        ("head", ("head", "neck", "jaw", "skull")),
        ("legs", ("leg", "thigh", "shin", "calf", "knee")),
        ("arms", ("arm", "shoulder", "clavicle", "elbow")),
        ("chest", ("spine", "chest", "rib")),
        ("hips", ("hip", "pelvis")),
    ):
        if any(word in name for word in words):
            return region
    return "other"


def lowest_regions(frame: Optional[int] = None, top: int = 3) -> List[tuple]:
    """For a lying or falling body, the lowest world point of each body region at a frame, lowest first.

    Returns `[(region, height), ...]`, at most `top` long. The body is the armature-bound mesh with the
    most vertices. Its vertices are grouped by their dominant deform bone, and the bone's name gives the
    region (head, chest, hips, arms, hands, legs, feet, tail, wings, other). Every other mesh object
    (not the ground disc) is a separate prop and is its own region, named after the object. A body
    propped up on a limb or a prop does not lie dead: lift or lower the lowest group, not the hips.
    """

    if frame is not None:
        bpy.context.scene.frame_set(frame)
    meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name != "ground_disc" and not o.hide_get()]
    if not meshes:
        return []
    body = max(meshes, key=lambda o: len(o.data.vertices))
    heights: Dict[str, float] = {}
    bones = {b.name for b in arm().data.bones}
    names = {group.index: group.name for group in body.vertex_groups}
    z = eval_co(body.name)[:, 2]
    for vertex in body.data.vertices:
        owned = [(g.weight, names.get(g.group, "")) for g in vertex.groups if names.get(g.group, "") in bones]
        region = _region_for_bone(max(owned)[1]) if owned else "other"
        height = float(z[vertex.index])
        if height < heights.get(region, math.inf):
            heights[region] = height
    for prop in meshes:
        if prop is not body and len(prop.data.vertices):
            heights[prop.name] = float(eval_co(prop.name)[:, 2].min())
    return sorted(heights.items(), key=lambda item: item[1])[: max(top, 0)]


def clear_sharp_faces(mesh_name: str) -> int:
    """Remove the per-face `sharp_face` flags an import leaves and smooth every polygon. Returns how many faces were sharp.

    io_pdx_mesh splits every corner of a flat-shaded face, so a mesh edited after import can export
    with far more than 65,535 vertices in one stream (UNIT-STREAM-VERTICES fails after export). Clearing
    the flags brings the count back to the source count. Custom corner normals stay as they are.
    """

    mesh = bpy.data.objects[mesh_name].data
    sharp = 0
    attribute = mesh.attributes.get("sharp_face")
    if attribute is not None:
        values = np.zeros(len(attribute.data), dtype=bool)
        attribute.data.foreach_get("value", values)
        sharp = int(values.sum())
    if len(mesh.polygons):
        mesh.polygons.foreach_set("use_smooth", np.ones(len(mesh.polygons), dtype=bool))
    # Smoothing can write the attribute back as all-false, so drop it last.
    attribute = mesh.attributes.get("sharp_face")
    if attribute is not None:
        mesh.attributes.remove(attribute)
    mesh.update()
    return sharp


# ---- export ----


def export_clip(action_name: str, path: str) -> int:
    """Export one action as a `.anim` at 30 fps with exactly its own frames, and check the file. Returns the sample count.

    Never export with `bpy.ops.io_pdx_mesh.export_anim`: it ignores its start and end frames unless the
    scene's custom-range setting is on, and exports the scene's frame range, so clips came out padded
    or cut short. This calls io_pdx_mesh's `export_animfile` with the action's range, restores the
    scene's range afterwards, and raises when the written sample count is not the action's frame count.

    HOI4 units play at 30 frames a second, and io_pdx_mesh writes the scene's rate. A scene started
    from factory settings runs at 24. When the scene is not at 30, the action's keys are scaled first so
    the clip lasts as long in game as it played in the scene (24 to 30 is 1.25 times the frames), and
    the scene is left at 30 so later previews match the game. The written rate is checked too.
    """

    import addon_utils

    module = next((m for m in addon_utils.modules() if m.__name__.endswith("io_pdx_mesh")), None)
    if module is None:
        raise RuntimeError("io_pdx_mesh is not installed for this Blender")
    addon_utils.enable(module.__name__, default_set=False)
    pdx = importlib.import_module(module.__name__ + ".pdx_blender.blender_import_export")
    rig = arm()
    action = bpy.data.actions[action_name]
    rig.animation_data_create()
    rig.animation_data.action = action
    start, end = (int(round(value)) for value in action.frame_range)
    scene = bpy.context.scene
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "adapter"))
    from anim_frame_range import HOI4_FPS, retime_action, verify_fps, verify_frame_range

    source_fps = scene.render.fps / scene.render.fps_base
    if abs(source_fps - HOI4_FPS) > 1e-6:
        old_end = end
        start, end = retime_action(action, start, end, source_fps, HOI4_FPS)
        print(f"export_clip: the scene ran at {source_fps:g} fps; {action_name} was retimed from frames {start}-{old_end} to {start}-{end} so it keeps its length at {HOI4_FPS} fps")
    scene.render.fps, scene.render.fps_base = HOI4_FPS, 1.0
    saved = (scene.frame_start, scene.frame_end, scene.frame_current)
    bpy.context.view_layer.objects.active = rig  # the exporter takes the active object as the rig
    try:
        scene.frame_start, scene.frame_end = start, end
        pdx.export_animfile(str(path), frame_start=start, frame_end=end, uniform_scale=True)
    finally:
        scene.frame_start, scene.frame_end = saved[0], saved[1]
        scene.frame_set(saved[2])
    verify_fps(path, HOI4_FPS)
    return verify_frame_range(path, start, end)


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

    A soldier's crotch tore to 20.8 % of its height while each side followed one thigh; pelvis 0.40,
    near thigh 0.36 and far thigh 0.24 brought its worst stretch from 25.5 % to about 14 %.
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
