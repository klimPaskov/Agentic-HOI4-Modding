"""Blender side of the secondary-chain stage (the rules are in lib/tripo_chains.py): add chain bones to a region, rebind it, bake the motion.

`tripo/prepare_tripo_unit.py --chains cloak wings` calls `add_chains` once, after the kit's bones and weights are in place and the parts are
joined, and `bake_chains` once per role clip, after the arm level and before the snap easing (which then eases a chain bone a collision
turned fast). Nothing here takes a per-unit number.

The work is split so it runs without Blender as well: `stage_inputs` and `sample_worlds` read the rig, `plan_stage`, `finish_stage` and
`bake_numpy` are plain numpy. With the environment variable `TRIPO_CHAIN_DUMP` set to a folder, the stage writes what it read there
(`chain_inputs.npz` and one `chain_role_<role>.npz` per clip), so the same rules can be replayed and measured offline on a real rig.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

try:  # the planning functions are plain numpy, so tests and offline replays import this module without Blender
    import bpy
except ImportError:  # pragma: no cover - outside Blender
    bpy = None

from lib import tripo_chains as C

DUMP_ENV = "TRIPO_CHAIN_DUMP"

# Body capsules the chains are kept out of: (name, from bone head, to bone head). The torso runs from the hips to the neck, the head from
# the neck to the head's joint (its radius, from the head's own skin, covers the face). The arms were added after the orc's cloak went
# into a swinging upper arm in the attack and into the forearm and hand in the death.
CAPSULES = (
    ("LeftThigh", "LeftUpLeg", "LeftLeg"), ("LeftShin", "LeftLeg", "LeftFoot"),
    ("RightThigh", "RightUpLeg", "RightLeg"), ("RightShin", "RightLeg", "RightFoot"),
    ("Torso", "Hips", "neck"), ("Head", "neck", "Head"),
    ("LeftUpperArm", "LeftArm", "LeftForeArm"), ("LeftForeArm", "LeftForeArm", "LeftHand"),
    ("RightUpperArm", "RightArm", "RightForeArm"), ("RightForeArm", "RightForeArm", "RightHand"),
)
CAPSULE_BONES = {
    "LeftThigh": ("LeftUpLeg",), "LeftShin": ("LeftLeg",), "RightThigh": ("RightUpLeg",), "RightShin": ("RightLeg",),
    "Torso": ("Hips", "Spine", "Spine01", "Spine02"), "Head": ("Head", "neck"),
    "LeftUpperArm": ("LeftArm",), "LeftForeArm": ("LeftForeArm", "LeftHand"),
    "RightUpperArm": ("RightArm",), "RightForeArm": ("RightForeArm", "RightHand"),
}
# The bones whose swing over the clips the regions keep clear of (lib/tripo_chains.swing_zone): each arm's upper arm, forearm and hand.
SWING_BONES = tuple(f"{side}{part}" for side in ("Left", "Right") for part in ("Arm", "ForeArm", "Hand"))
SWING_FRAME_STEP = 2  # every second frame of every clip is enough: an arm moves less than its radius in two frames
# The regions that carve the arms' swing room (`keep_clear`) out of their skin and fade their chains before it. None does: on the orc the
# carved cloak bridged to the legs (UNIT-BRIDGE), and on the demon, replayed offline (tripo/chain_replay.py, root zone of the wings at each
# clip's worst frame), dropping it took the stretched root edges from 196 to 104 in the retreat, 119 to 37 in the walk, 184 to 133 in the
# death and 199 to 184 in the attack. The arms are capsules the chains collide with instead.
ARM_ROOM_REGIONS: tuple = ()
# The regions whose blend gives its arm weights to the torso (lib/tripo_chains.loosen_row): the wings, bound by Tripo to the arms.
LOOSEN_REGIONS = ("wings",)


# ---------------------------------------------------------------------------------------------
# Reading the rig (Blender)
# ---------------------------------------------------------------------------------------------


def as_array(matrix) -> np.ndarray:
    return np.array([list(row) for row in matrix], float)


def body_positions(body) -> np.ndarray:
    count = len(body.data.vertices)
    flat = np.empty(count * 3)
    body.data.vertices.foreach_get("co", flat)
    world = as_array(body.matrix_world)
    return flat.reshape(-1, 3) @ world[:3, :3].T + world[:3, 3]


def body_edges(body) -> np.ndarray:
    flat = np.empty(len(body.data.edges) * 2, dtype=np.int64)
    body.data.edges.foreach_get("vertices", flat)
    return flat.reshape(-1, 2)


def body_triangles(body) -> np.ndarray:
    out = []
    for polygon in body.data.polygons:
        loop = list(polygon.vertices)
        out += [(loop[0], loop[k], loop[k + 1]) for k in range(1, len(loop) - 1)]
    return np.array(out, dtype=np.int64).reshape(-1, 3)


def read_rows(body) -> List[Dict[str, float]]:
    names = {group.index: group.name for group in body.vertex_groups}
    return [{names[g.group]: g.weight for g in v.groups if g.group in names and g.weight > 0} for v in body.data.vertices]


def dominant_names(rows: List[Dict[str, float]]) -> np.ndarray:
    return np.array([max(row.items(), key=lambda item: item[1])[0] if row else "" for row in rows])


def rest_heads(armature) -> Dict[str, np.ndarray]:
    world = as_array(armature.matrix_world)
    return {bone.name: world[:3, :3] @ np.array(bone.head_local) + world[:3, 3] for bone in armature.data.bones}


def rest_matrix(armature, name: str) -> np.ndarray:
    return C.orthonormal(as_array(armature.matrix_world) @ as_array(armature.data.bones[name].matrix_local))


def bone_parents(armature) -> Dict[str, Optional[str]]:
    return {bone.name: (bone.parent.name if bone.parent else None) for bone in armature.data.bones}


def stage_inputs(armature, body) -> dict:
    """What the stage reads from the rig, as plain arrays: the body's vertices, edges, triangles and weights in world space, and every
    bone's rest head, rest matrix and parent."""

    return {
        "positions": body_positions(body), "edges": body_edges(body), "triangles": body_triangles(body), "rows": read_rows(body),
        "heads": rest_heads(armature), "rest": {bone.name: rest_matrix(armature, bone.name) for bone in armature.data.bones},
        "parents": bone_parents(armature), "bone_count": len(armature.data.bones),
    }


def sample_worlds(armature, frames: Sequence[int], names: Sequence[str]) -> Dict[str, np.ndarray]:
    """Per bone in `names`, its posed world matrix (frames, 4, 4) in each of `frames` of the assigned action."""

    scene = bpy.context.scene
    world = as_array(armature.matrix_world)
    bones = armature.pose.bones
    out = {name: np.zeros((len(frames), 4, 4)) for name in names}
    for i, frame in enumerate(frames):
        scene.frame_set(frame)
        for name in names:
            out[name][i] = world @ as_array(bones[name].matrix)
    return out


def action_frames(action) -> List[int]:
    start, end = int(action.frame_range[0]), int(action.frame_range[1])
    return list(range(start, end + 1))


# ---------------------------------------------------------------------------------------------
# Planning the regions (numpy)
# ---------------------------------------------------------------------------------------------


def body_frame(heads: Dict[str, np.ndarray]):
    """(up, front, down): world up is +Z in Blender; front runs from the heels to the toes, made horizontal."""

    up = np.array([0.0, 0.0, 1.0])
    front = np.zeros(3)
    for side in ("Left", "Right"):
        front += heads[f"{side}ToeBase"] - heads[f"{side}Foot"]
    front -= (front @ up) * up
    return up, C.unit(front), -up


# Limb capsules for the "loose cloth" rule: (from bone head, to bone head, bones whose skin gives the radius). A hand runs on past its head
# by half its forearm.
LIMBS = tuple(
    (f"{side}{start}", f"{side}{end}", (f"{side}{start}",))
    for side in ("Left", "Right")
    for start, end in (("UpLeg", "Leg"), ("Leg", "Foot"), ("Arm", "ForeArm"), ("ForeArm", "Hand"), ("Hand", "Hand"), ("Shoulder", "Arm"))
)


def limb_segment(heads, start: str, end: str):
    a, b = heads[start], heads[end]
    if start == end:  # the hand: on past its head by half the forearm
        b = a + 0.5 * (heads[start] - heads[start.replace("Hand", "ForeArm")])
    return a, b


def mirror_name(name: str) -> str:
    return name.replace("Left", "\0").replace("Right", "Left").replace("\0", "Right")


def limb_capsules(ctx, excluded):
    """(a, b, radius) per limb in the rest pose. The radius is the limb's own skin outside `excluded` (`lib.tripo_chains.capsule_radius`),
    the smaller of the limb's and its mirror's: Tripo binds a wing or a cloak to one arm whole, which makes that arm's skin read as twice
    the other's (the demon's upper arms: 0.12 and 0.04 of the height)."""

    heads = ctx["heads"]

    def radius(start, end, bones):
        a, b = limb_segment(heads, start, end)
        own = np.isin(ctx["dominant"], bones) & ~excluded
        return C.capsule_radius(ctx["positions"][own], a, b)

    out = []
    for start, end, bones in LIMBS:
        mirrored = radius(mirror_name(start), mirror_name(end), tuple(mirror_name(b) for b in bones))
        own = radius(start, end, bones)
        a, b = limb_segment(heads, start, end)
        out.append((a, b, min(own, mirrored) if mirrored > 0 else own))
    return out


def torso_capsule(ctx, excluded):
    heads = ctx["heads"]
    own = np.isin(ctx["dominant"], CAPSULE_BONES["Torso"]) & ~excluded
    return heads["Hips"], heads["neck"], C.capsule_radius(ctx["positions"][own], heads["Hips"], heads["neck"])


def plan_cloak(ctx):
    positions, heads, up, front = ctx["positions"], ctx["heads"], ctx["up"], ctx["front"]
    check = C.cloak_mask(positions, ctx["dominant"], heads["Hips"], front, up, ctx["height"])
    grown = C.cloak_rebind_mask(check, positions, ctx["edges"], ctx["dominant"], heads["Hips"], front, up, ctx["height"], limb_capsules(ctx, check))
    collar = C.collar_zone(positions, up, float(min(heads["LeftArm"] @ up, heads["RightArm"] @ up)))
    # The cloak does not carve out the arms' swing room (`keep_clear`, kept for wings): on the round 4 orc the carved skin kept Tripo's
    # thigh weights beside skin on the chains, which bridged the cloak to the legs (UNIT-BRIDGE, 28 edges) and stretched the attack's
    # right thigh from 169 to 456 edges. The arms are capsules the cloak's chains collide with instead (`CAPSULES`).
    mask = grown & ~collar
    points = positions[mask]
    u, s, radius = C.cloak_coordinates(points, heads["Hips"], front, up)
    low, high = np.percentile(u, [2.0, 98.0])
    length, width = float(np.percentile(s, 99) - np.percentile(s, 1)), float(high - low) * radius
    chains, bones = C.chain_shape(length, width, ctx["segment"], ctx["budget"])
    chain_u = C.even_angles(u, chains)
    joints, stations = C.sheet_layout(points, u, s, chain_u, bones)
    return [{
        "region": "cloak", "side": "", "mask": mask, "chain_u": chain_u, "joints": joints, "stations": stations,
        "coords": cloak_coords(heads["Hips"], front, up, float((points @ up).max())),
        "layout": "fan", "check_vertices": int(check.sum()), "kept_clear": int((grown & collar).sum()), "blocked": collar,
        "shape_inputs": {"length": round(length, 4), "width": round(width, 4), "segment": round(ctx["segment"], 4), "budget": ctx["budget"]},
    }]


def plan_wings(ctx):
    positions, heads, up, front = ctx["positions"], ctx["heads"], ctx["up"], ctx["front"]
    centre = heads["Hips"]
    lateral = C.unit(np.cross(up, front))
    far_left, far_right = C.wing_masks(positions, ctx["dominant"], centre, front, up)
    if far_left.sum() < 50 or far_right.sum() < 50:
        raise SystemExit(f"--chains wings found no pair of wings ({int(far_left.sum())} and {int(far_right.sum())} vertices beyond {C.WING_LATERAL_SHARE:.0%} of the width)")
    far = far_left | far_right
    limbs = limb_capsules(ctx, far)
    torso = torso_capsule(ctx, far)
    head = (heads["neck"], heads["Head"], C.capsule_radius(positions[np.isin(ctx["dominant"], CAPSULE_BONES["Head"]) & ~far], heads["neck"], heads["Head"]))
    shoulders = 0.5 * (heads["LeftArm"] + heads["RightArm"])
    grown = C.wing_rebind_mask(far, positions, ctx["edges"], ctx["dominant"], shoulders, front, [limb for limb in limbs] + [torso, head])
    side = (positions - centre) @ lateral
    room = ctx["keep_clear"] if "wings" in ARM_ROOM_REGIONS else np.zeros(len(positions), bool)
    left = grown & (side > 0) & ~room
    right = grown & (side < 0) & ~room
    points = positions[left]
    root = C.wing_root(points, heads[C.CHAIN_PARENT])
    u, s, plane = C.wing_coordinates(points, root, front, up)
    low, high = np.percentile(u, [2.0, 98.0])
    length = float(np.percentile(s, 99))
    width = float(high - low) * float(np.median(s))
    chains, bones = C.chain_shape(length, width, ctx["segment"], ctx["budget"])
    chain_u, layout = C.ridge_angles(u, s, chains)
    chain_u, leading = C.leading_edge_angles(u, s, chain_u)
    joints, stations = C.sheet_layout(points, u, s, chain_u, bones, ridge=leading)
    joints[:, 0] = root  # every finger chain starts at the wing root
    right_joints = np.stack([C.mirror_points(chain, centre, lateral) for chain in joints])
    arm = C.ridge_band(u, chain_u, leading)
    common = {"chain_u": chain_u, "stations": stations, "layout": layout, "root": root, "plane": plane, "front": front,
              "points": points, "body_points": positions[~(left | right)], "height": ctx["height"], "leading": leading,
              "ridge_halfwidth": arm, "far_vertices": int(far.sum()),
              "shape_inputs": {"length": round(length, 4), "width": round(width, 4), "segment": round(ctx["segment"], 4), "budget": ctx["budget"]}}
    return [
        # each wing's blend stops at the mid-plane, so the two rings never meet on the spine
        dict(common, region="wings", side="L", mask=left, joints=joints, coords=lambda pts: _fan_coordinates(pts, root, plane), blocked=side <= 0),
        dict(common, region="wings", side="R", mask=right, joints=right_joints, blocked=side >= 0,
             coords=lambda pts: _fan_coordinates(C.mirror_points(pts, centre, lateral), root, plane)),
    ]


def cloak_coords(hips, front, up, top):
    """(u, s) of any points on the cloak's sheet: the angle round the hips' vertical axis and the drop below the region's top."""

    def coords(points):
        u, _s, _radius = C.cloak_coordinates(points, hips, front, up)
        return u, top - np.asarray(points, float) @ up

    return coords


def _fan_coordinates(points, root, plane):
    rel = np.asarray(points, float) - root
    x, y = rel @ plane[0], rel @ plane[1]
    return np.arctan2(y, x), np.sqrt(x * x + y * y)


def body_height(positions, up) -> float:
    return float(np.ptp(positions @ up))


def thighs(heads):
    """(left, right) thigh heads for the cloak's side follow (lib/tripo_chains.SIDE_THIGH_SHARE), or None when the rig has no thighs."""

    if "LeftUpLeg" in heads and "RightUpLeg" in heads:
        return heads["LeftUpLeg"], heads["RightUpLeg"]
    return None


def bone_names(sheet) -> List[List[str]]:
    prefix = C.REGION_PREFIX[sheet["region"]] + sheet["side"]
    chains, bones = sheet["joints"].shape[0], sheet["joints"].shape[1] - 1
    return [[f"{prefix}{c + 1}_{b + 1}" for b in range(bones)] for c in range(chains)]


def chain_rows(rows, positions, edges, sheets, limb_ends, arm_room):
    """Give each sheet's region its chains' weights whole, blended into the body's over one chain bone outward from the region's border
    (`lib.tripo_chains.blend_alpha`) but never into blocked skin (a forearm, hand, shin or foot, `limb_ends` from
    `lib.tripo_chains.is_limb_end`; for wings also `arm_room`, the room an arm swings through, `lib.tripo_chains.arm_room`; and the sheet's
    own `blocked`: a cloak's collar, the far side of a wing's mid-plane),
    at most 4 influences. The region and its blend first give their limb weights to the torso by the chains' share
    (`lib.tripo_chains.loosen_row`). Returns the new rows and how many vertices changed."""

    changed = 0
    new_rows = list(rows)
    for sheet in sheets:
        names = [name for chain in bone_names(sheet) for name in chain]
        joints = sheet["joints"]
        blend = C.blend_length_for(joints, positions, edges, sheet["mask"])
        # the chains fade out over a few rings before a limb end or an arm's room, and over the whole blend before the sheet's own stop
        stop_length = C.BLEND_MIN_RINGS * C.ring_length(positions, edges, sheet["mask"])
        own = C.fade_from(positions, edges, sheet["blocked"], blend) if sheet.get("blocked") is not None and np.any(sheet["blocked"]) else 1.0
        blocked = limb_ends | arm_room if sheet["region"] in ARM_ROOM_REGIONS else limb_ends
        alpha = C.blend_alpha(positions, edges, sheet["mask"], blend, blocked, stop_length) * own
        # skin the chains move loses its limb weights to the torso by the chains' own share (lib/tripo_chains.loosen_row). Never beyond the
        # blend: a ring loosened there carried no chain weight, so thigh and arm skin stayed with the torso while the limb swung (the round 4
        # orc's attack: thigh stretch 169 to 254 edges, UNIT-ANIM-STRETCH failed in attack and death).
        # Wings only: in a cloak's blend the loosened hand weight left the cloak side of a hand-thigh join without the hand while its
        # neighbour kept 43% of it, and the orc's attack grew one edge by 25.7% of the height (UNIT-ANIM-STRETCH, limit 23.8%; replayed
        # without the cloak's loosening 21.0%, the cloak stretch unchanged).
        if sheet["region"] in LOOSEN_REGIONS:
            for vertex in np.where(alpha > 0)[0]:
                new_rows[vertex] = C.loosen_row(new_rows[vertex], float(alpha[vertex]))
        sheet["blend_length"] = blend
        bound = np.where(alpha > 0)[0]
        u, s = sheet["coords"](positions[bound])
        rows_here = C.sheet_weights(u, s, sheet["chain_u"], sheet["stations"], ridge=sheet.get("leading"),
                                    ridge_halfwidth=sheet.get("ridge_halfwidth", 0.0))
        sheet["bound_vertices"] = int(len(bound))
        for vertex, chain_row in zip(bound, rows_here):
            named = {names[index]: weight for index, weight in chain_row.items()}
            new_rows[vertex] = C.mix_weights(new_rows[vertex], named, float(alpha[vertex]))
            changed += 1
    return new_rows, changed


def capsule_radii(positions, dominant, heads, sheets):
    excluded = np.zeros(len(positions), bool)
    for sheet in sheets:
        excluded |= sheet["mask"]
    radii = {}
    for name, start, end in CAPSULES:
        own = np.isin(dominant, CAPSULE_BONES[name]) & ~excluded
        radii[name] = C.capsule_radius(positions[own], heads[start], heads[end])
    # an arm's capsule is the smaller of its own and its mirror's (see `limb_capsules`)
    for name in list(radii):
        twin = mirror_name(name)
        if twin != name and twin in radii and radii[twin] > 0:
            radii[name] = min(radii[name], radii[twin])
    return radii


def swing_segments(clips: Sequence[Dict[str, np.ndarray]], rest: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Per limb part (`LeftArm` for the left upper arm, `LeftForeArm`, `LeftHand`, and the right ones): every pose it takes in `clips`,
    as segments (N, 2, 3) carried back into the rest pose by the chain parent (the upper spine). `clips` holds, per clip, each bone's
    posed world matrices (frames, 4, 4) (`sample_worlds`). A region kept clear of these is kept clear of the arm in every frame."""

    out: Dict[str, List[np.ndarray]] = {}
    carrier_rest = rest[C.CHAIN_PARENT]
    for worlds in clips:
        back = carrier_rest @ np.linalg.inv(np.stack([C.orthonormal(m) for m in worlds[C.CHAIN_PARENT]]))
        heads = {name: np.einsum("fij,fj->fi", back, np.concatenate([worlds[name][:, :3, 3], np.ones((len(back), 1))], axis=1))[:, :3]
                 for name in SWING_BONES}
        for side in ("Left", "Right"):
            for part, (start, end) in (("Arm", ("Arm", "ForeArm")), ("ForeArm", ("ForeArm", "Hand")), ("Hand", ("Hand", None))):
                a = heads[side + start]
                b = heads[side + end] if end else a + 0.5 * (heads[side + "Hand"] - heads[side + "ForeArm"])
                out.setdefault(side + part, []).append(np.stack([a, b], axis=1))
    return {name: np.concatenate(parts) for name, parts in out.items()}


def keep_clear(ctx, swing: Optional[Dict[str, np.ndarray]]) -> np.ndarray:
    """The vertices the chains keep off (`lib.tripo_chains.arm_room`): the room each arm swings through in the clips (its rest pose when
    there are no clips)."""

    heads, positions = ctx["heads"], ctx["positions"]
    parts = []
    radii = {(start, end): radius for (start, end, _bones), (_a, _b, radius) in zip(LIMBS, ctx["limbs"])}
    for side in ("Left", "Right"):
        for part, (start, end) in (("Arm", ("Arm", "ForeArm")), ("ForeArm", ("ForeArm", "Hand")), ("Hand", ("Hand", "Hand"))):
            segments = swing.get(side + part) if swing else None
            rest = np.stack(limb_segment(heads, side + start, side + end))[None]
            segments = rest if segments is None or not len(segments) else np.concatenate([rest, segments])
            parts.append((segments, radii[(side + start, side + end)]))
    return C.arm_room(positions, parts)


def plan_stage(inputs: dict, regions: Sequence[str], swing: Optional[Dict[str, np.ndarray]] = None) -> dict:
    """The numpy part of `add_chains`: the regions, their chains and the new weights (plates bound after the chains)."""

    unknown = [region for region in regions if region not in C.REGIONS]
    if unknown:
        raise SystemExit(f"--chains names unknown regions {unknown}; known: {list(C.REGIONS)}")
    heads = inputs["heads"]
    up, front, down = body_frame(heads)
    positions = np.asarray(inputs["positions"], float)
    height = body_height(positions, up)
    edges = C.with_seams(positions, inputs["edges"], height)
    rows = list(inputs["rows"])
    dominant = dominant_names(rows)
    thigh = 0.5 * sum(float(np.linalg.norm(heads[f"{s}UpLeg"] - heads[f"{s}Leg"])) for s in ("Left", "Right"))
    segment = 0.5 * thigh
    budget = C.bone_budget(inputs["bone_count"], regions)
    ctx = {"positions": positions, "edges": edges, "dominant": dominant, "heads": heads, "up": up, "front": front,
           "height": height, "segment": segment, "budget": budget}
    ctx["limbs"] = limb_capsules(ctx, np.zeros(len(positions), bool))
    ctx["keep_clear"] = keep_clear(ctx, swing)
    sheets = []
    for region in regions:
        if region != "plates":
            sheets += (plan_cloak if region == "cloak" else plan_wings)(ctx)
    limb_ends = np.array([C.is_limb_end(name) for name in dominant])
    new_rows, changed = chain_rows(rows, positions, edges, sheets, limb_ends, ctx["keep_clear"])
    plates = {}
    if "plates" in regions:
        # after the chains, so a chain's blend ring never reaches into a plate: the plate stays rigid
        torso = np.isin(dominant, CAPSULE_BONES["Torso"])
        radius = C.capsule_radius(positions[torso], heads["Hips"], heads["neck"])
        masks = C.plate_masks(positions, heads, front, up, radius)
        new_rows, plates = C.rigid_plates(new_rows, positions, edges, masks, C.bone_depths(inputs["parents"]))
    radii = capsule_radii(positions, dominant, heads, sheets)
    return {"ctx": ctx, "sheets": sheets, "rows": new_rows, "changed": changed, "plates": plates, "radii": radii, "up": up, "front": front,
            "down": down, "height": height, "regions": list(regions)}


# ---------------------------------------------------------------------------------------------
# The plan the bake reads (numpy)
# ---------------------------------------------------------------------------------------------


def chain_bone_rest(head: np.ndarray, tail: np.ndarray, roll_axis: np.ndarray) -> np.ndarray:
    """The world rest matrix Blender gives a new bone from `head` to `tail` rolled toward `roll_axis` (`align_roll`): +Y along the bone,
    +Z toward the roll axis. The offline replay uses it for the chain bones Blender would add."""

    y = C.unit(np.asarray(tail, float) - np.asarray(head, float))
    z = np.asarray(roll_axis, float) - (np.asarray(roll_axis, float) @ y) * y
    z = C.unit(z) if np.linalg.norm(z) > 1e-9 else C.unit(np.cross(y, [1.0, 0.0, 0.0]))
    out = np.eye(4)
    out[:3, 0], out[:3, 1], out[:3, 2], out[:3, 3] = np.cross(y, z), y, z, head
    return out


def wing_limits(sheet, heads, radii, up) -> Dict[str, float]:
    """The wing's pose room by rule (lib/tripo_chains.py): back swing, the side floor (the least back swing that keeps the wing off the
    body in the side views), the face turn of a retreat, the fan's close and the down-stroke, from the torso's radius, the body and the
    wing's own chains. Computed once from the left wing (the right one is its mirror)."""

    plane, joints, chain_u = sheet["plane"], sheet["joints"], np.asarray(sheet["chain_u"])
    first = C.unit(joints[:, 1] - joints[:, 0])
    normal = C.unit(np.cross(plane[0], plane[1]))
    points, body, root, front, height = sheet["points"], sheet["body_points"], sheet["root"], sheet["front"], sheet["height"]
    lateral = C.unit(np.cross(up, front))
    sweep = C.wing_sweep_degrees(float(sheet["shape_inputs"]["length"]), radii["Torso"])
    side, _ceiling = C.wing_side_floor(points, body, root, front, up, height, sweep)
    sweep = float(sheet.get("fold", {}).get("sweep", sweep))
    # the face turn keeps the floor's swing and only tilts: a retreat swung further back (72 and 82 degrees on the demon) squashed its
    # beating membrane past UNIT-ANIM-STRETCH in the clip's first beats
    face_sweep, face_tilt = C.face_turn(normal, front, up, side, side)
    low = int(np.argmin(chain_u))
    low_rest = C.unit(np.diff(joints[low], axis=0))
    if sheet["side"] == "R":  # the pose rules work on the left wing; the right one is its mirror
        low_rest = C.mirror_directions(low_rest, lateral)
    return {
        "low_rest": low_rest, "low_lengths": np.linalg.norm(np.diff(joints[low], axis=0), axis=1), "low_u": float(chain_u[low]),
        "root": np.asarray(joints[low, 0], float),
        "u_min": float(np.min(chain_u)), "normal": normal, "sweep": sweep, "side": side, "face_sweep": face_sweep, "face_tilt": face_tilt,
        "close": float(sheet.get("fold", {}).get("close", C.FAN_CLOSE_SHARE)),
        "down": C.wing_down_degrees(first[int(np.argmin(chain_u))], -up),
        "droop": 0.0,
    }


def chain_plan(rest_of: Callable[[str], np.ndarray], sheets, heads, radii, height, up) -> List[dict]:
    """Per chain: its bones, rest matrices (`rest_of(name)`, world), spring rates, collision radii and the bones each tail follows (the cloak
    rule)."""

    margin = C.COLLISION_MARGIN_SHARE * height
    plans = []
    for sheet in sheets:
        wing = wing_limits(sheet, heads, radii, up) if sheet["region"] == "wings" else None
        for c, chain in enumerate(bone_names(sheet)):
            joints = sheet["joints"][c]
            lengths = np.linalg.norm(np.diff(joints, axis=0), axis=1)
            parent = rest_of(C.CHAIN_PARENT)
            relative, previous = [], parent
            for name in chain:
                own = rest_of(name)
                relative.append(np.linalg.inv(previous) @ own)
                previous = own
            capsules = [(heads[start], heads[end], radii[name]) for name, start, end in CAPSULES]
            follow = C.torso_follow_weights(joints[1:], heads[C.CHAIN_PARENT], heads["Hips"], up, thighs(heads)) if sheet["region"] == "cloak" else []
            follow_torso = C.torso_follow_weights(joints[1:], heads[C.CHAIN_PARENT], heads["Hips"], up) if sheet["region"] == "cloak" else []
            plans.append({
                "region": sheet["region"], "side": sheet["side"], "chain": c, "bones": chain, "lengths": lengths,
                "rest_relative": np.stack(relative), "omegas": C.pendulum_omegas(lengths, height), "rest_joints": joints,
                "radii": C.clearance_radii(joints[1:], capsules, margin), "chain_u": float(sheet["chain_u"][c]),
                "chains": len(sheet["chain_u"]), "tails": joints[1:], "follow": follow, "follow_torso": follow_torso, "wing": wing,
                "rest_directions": C.unit(np.diff(joints, axis=0)), "parent_rest": parent,
                "leading": bool(sheet.get("leading") is not None and c == int(sheet["leading"])),
            })
    return plans


def finish_stage(planned: dict, rest_of: Callable[[str], np.ndarray], bones_after: int) -> dict:
    """The stage `bake_chains` reads, from `plan_stage`'s result once the chain bones exist (`rest_of(name)` gives any bone's world rest
    matrix)."""

    ctx, sheets, up, height = planned["ctx"], planned["sheets"], planned["up"], planned["height"]
    heads = dict(ctx["heads"])
    for sheet in sheets:
        for c, chain in enumerate(bone_names(sheet)):
            for b, name in enumerate(chain):
                heads[name] = sheet["joints"][c, b]
    for sheet in sheets:
        if sheet["region"] == "wings" and sheet["side"] == "L":
            # the fold swings back and closes the fan only as far as the skin allows; the right wing is the left one's mirror
            chains = [{"bones": chain, "rest": [rest_of(name) for name in chain], "rest_directions": C.unit(np.diff(sheet["joints"][c], axis=0)),
                       "chain_u": float(sheet["chain_u"][c])} for c, chain in enumerate(bone_names(sheet))]
            room = C.fold_room(chains, wing_limits(sheet, heads, planned["radii"], up), planned["rows"], ctx["positions"], ctx["edges"],
                               rest_of(C.CHAIN_PARENT), up, planned["front"], height)
            for other in sheets:
                if other["region"] == "wings":
                    other["fold"] = room
    plans = chain_plan(rest_of, sheets, heads, planned["radii"], height, up)
    ground = float((ctx["positions"] @ up).min()) + C.GROUND_MARGIN_SHARE * height
    report = {
        "regions": planned["regions"], "bones_after": bones_after, "segment": round(ctx["segment"], 4), "budget_per_side": ctx["budget"],
        "weights": {"vertices_rebound": planned["changed"], "max_influences": max(len(row) for row in planned["rows"])},
        "capsule_radii": {k: round(v, 4) for k, v in planned["radii"].items()}, "plates": planned["plates"],
        "kept_clear_vertices": int(ctx["keep_clear"].sum()),
        "sheets": [{"region": s["region"], "side": s["side"], "vertices": int(s["mask"].sum()), "chains": int(s["joints"].shape[0]),
                    "bones_per_chain": int(s["joints"].shape[1] - 1), "layout": s["layout"], "check_vertices": s.get("check_vertices"),
                    "kept_clear": s.get("kept_clear"), "far_vertices": s.get("far_vertices"), "leading_chain": s.get("leading"),
                    "fold": {k: round(float(v), 3) for k, v in s.get("fold", {}).items()}, "shape_inputs": s["shape_inputs"],
                    "blend_length": round(s.get("blend_length", 0.0), 4), "bound_vertices": s.get("bound_vertices")} for s in sheets],
    }
    if bones_after > C.MAX_BONES:
        raise SystemExit(f"The chains bring the rig to {bones_after} bones (HOI4 allows {C.MAX_BONES})")
    return {"plans": plans, "sheets": sheets, "up": up, "front": planned["front"], "down": planned["down"], "height": height, "ground": ground,
            "report": report}


# ---------------------------------------------------------------------------------------------
# Adding bones and weights (Blender)
# ---------------------------------------------------------------------------------------------


def add_bones(armature, sheets, front) -> None:
    world_inverse = np.linalg.inv(as_array(armature.matrix_world))
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode="EDIT")
    edit = armature.data.edit_bones
    roll_axis = world_inverse[:3, :3] @ front
    for sheet in sheets:
        names = bone_names(sheet)
        for c, chain in enumerate(names):
            parent = edit[C.CHAIN_PARENT]
            for b, name in enumerate(chain):
                head = world_inverse[:3, :3] @ sheet["joints"][c, b] + world_inverse[:3, 3]
                tail = world_inverse[:3, :3] @ sheet["joints"][c, b + 1] + world_inverse[:3, 3]
                if np.linalg.norm(tail - head) < 1e-5:
                    tail = head + np.array([0.0, 0.0, -1e-3])
                bone = edit.new(name)
                bone.head, bone.tail = tuple(head), tuple(tail)
                bone.align_roll(tuple(roll_axis))
                bone.parent = parent
                bone.use_connect = b > 0
                bone.use_deform = True
                parent = bone
    bpy.ops.object.mode_set(mode="OBJECT")
    for sheet in sheets:
        for chain in bone_names(sheet):
            for name in chain:
                armature.pose.bones[name].rotation_mode = "QUATERNION"


def write_groups(body, new_rows) -> None:
    """Replace the mesh's vertex groups with `new_rows`."""

    groups = sorted({name for row in new_rows for name in row} | {g.name for g in body.vertex_groups})
    for group in list(body.vertex_groups):
        body.vertex_groups.remove(group)
    made = {name: body.vertex_groups.new(name=name) for name in groups}
    for index, row in enumerate(new_rows):
        for name, weight in row.items():
            made[name].add([index], weight, "REPLACE")


def dump_folder() -> Optional[Path]:
    folder = os.environ.get(DUMP_ENV)
    if not folder:
        return None
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)
    return path


def dump_inputs(folder: Path, inputs: dict, regions: Sequence[str]) -> None:
    names = sorted(inputs["rest"])
    index = {name: i for i, name in enumerate(names)}
    row_bones = np.full((len(inputs["rows"]), 8), -1, dtype=np.int64)
    row_weights = np.zeros((len(inputs["rows"]), 8))
    for v, row in enumerate(inputs["rows"]):
        for k, (name, weight) in enumerate(sorted(row.items(), key=lambda item: -item[1])[:8]):
            row_bones[v, k], row_weights[v, k] = index[name], weight
    np.savez_compressed(folder / "chain_inputs.npz", positions=inputs["positions"], edges=inputs["edges"], triangles=inputs["triangles"],
                        row_bones=row_bones, row_weights=row_weights, names=np.array(names),
                        rest=np.stack([inputs["rest"][n] for n in names]), heads=np.stack([inputs["heads"][n] for n in names]),
                        parents=np.array([inputs["parents"][n] or "" for n in names]), bone_count=inputs["bone_count"], regions=np.array(list(regions)))


def add_chains(armature, body, regions: List[str], clips: Sequence = ()) -> dict:
    """Add the chains for `regions`, rebind their vertices and return the plan (`bake_chains` reads it) with a report. `clips` are the role
    clips' actions: the regions keep clear of the room the arms swing through in them."""

    inputs = stage_inputs(armature, body)
    folder = dump_folder()
    if folder is not None:
        dump_inputs(folder, inputs, regions)
    swing = None
    if clips:
        sampled = []
        for action in clips:
            assign(armature, action)
            sampled.append(sample_worlds(armature, action_frames(action)[::SWING_FRAME_STEP], (C.CHAIN_PARENT,) + SWING_BONES))
        swing = swing_segments(sampled, inputs["rest"])
        armature.animation_data.action = None
        import mathutils

        for bone in armature.pose.bones:  # back to the rest pose the clips left behind
            bone.matrix_basis = mathutils.Matrix.Identity(4)
        bpy.context.scene.frame_set(bpy.context.scene.frame_start)
    planned = plan_stage(inputs, regions, swing)
    add_bones(armature, planned["sheets"], planned["front"])
    write_groups(body, planned["rows"])
    return finish_stage(planned, lambda name: rest_matrix(armature, name), len(armature.data.bones))


# ---------------------------------------------------------------------------------------------
# Baking
# ---------------------------------------------------------------------------------------------


def assign(armature, action) -> None:
    armature.animation_data_create()
    armature.animation_data.action = action
    slots = getattr(action, "slots", None)
    if slots is not None and len(slots):
        armature.animation_data.action_slot = slots[0]


def body_from_worlds(worlds: Dict[str, np.ndarray], rest: Dict[str, np.ndarray], skinned: Sequence[str]) -> Dict[str, np.ndarray]:
    """Per frame: the chain parent's world matrix (rotation and translation), the capsule axes and, for each bone in `skinned`, its
    skinning matrix (posed world matrix times the inverse of its rest world matrix), from each bone's posed world matrices."""

    parents = np.stack([C.orthonormal(m) for m in worlds[C.CHAIN_PARENT]])
    frames = len(parents)
    axes = np.zeros((frames, len(CAPSULES), 2, 3))
    for c, (_name, start, end) in enumerate(CAPSULES):
        axes[:, c, 0] = worlds[start][:, :3, 3]
        axes[:, c, 1] = worlds[end][:, :3, 3]
    skinning = {name: worlds[name] @ np.linalg.inv(rest[name]) for name in sorted(set(skinned) | {"Hips"})}
    return {"parents": parents, "axes": axes, "skinning": skinning}


def body_bones(stage: dict) -> List[str]:
    """The bones `bake_numpy` reads per frame."""

    follow = {name for plan in stage["plans"] for row in plan.get("follow", []) for name in row}
    capsule = {bone for _name, start, end in CAPSULES for bone in (start, end)}
    return sorted(follow | capsule | {C.CHAIN_PARENT, "Hips"})


def body_track(body: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Per frame, the world positions of the hips, the feet, the two knees (frames, 2, 3) and the neck and head, read off the capsule
    axes (the wing rule times a death's fold by the hips, keeps a wing above the knees and off the head, and times a move's beats by the
    feet)."""

    names = [name for name, _start, _end in CAPSULES]
    return {"Hips": body["axes"][:, names.index("Torso"), 0], "LeftFoot": body["axes"][:, names.index("LeftShin"), 1],
            "RightFoot": body["axes"][:, names.index("RightShin"), 1],
            "knees": np.stack([body["axes"][:, names.index("LeftShin"), 0], body["axes"][:, names.index("RightShin"), 0]], axis=1),
            "neck": body["axes"][:, names.index("Head"), 0], "Head": body["axes"][:, names.index("Head"), 1]}


def back_directions(body: Dict[str, np.ndarray], front: np.ndarray) -> np.ndarray:
    """Per frame, the rest pose's backward direction carried by the hips: the way a collision pushes cloth off the legs and body."""

    return np.stack([C.unit(C.orthonormal(matrix)[:3, :3] @ -front) for matrix in body["skinning"]["Hips"]])


# Roles whose cloak follows the torso alone, without the side chains' thigh share (lib/tripo_chains.SIDE_THIGH_SHARE): in a death the
# thighs swing forward as the body kneels, and on the round 4 orc the side chains following them went into the body (TRIPO-CHAIN-IN-BODY
# 4.8% against 4.5% in the death, frame 84).
TORSO_ONLY_ROLES = ("death",)


def bake_cloak(plans, body, stage, dt, looping, role: str = "") -> List[np.ndarray]:
    """The cloak rule for all its chains at once (`lib.tripo_chains.simulate_sheet`): each tail follows the upper spine and the hips by
    its height (a side chain below the hips also a little of its thigh, except in `TORSO_ONLY_ROLES`), through the spring, and the sheet is
    pushed off the legs and torso along the hips' back direction; once the torso lies down, it drapes by gravity onto the body."""

    key = "follow_torso" if role in TORSO_ONLY_ROLES else "follow"
    chains = [dict(plan, follow_points=C.follow_targets(plan["tails"], plan.get(key, plan["follow"]), body["skinning"])) for plan in plans]
    track = body_track(body)
    lying = C.lying_share(track["Hips"], body["parents"][:, :3, 3], stage["up"])
    return C.simulate_sheet(body["parents"], chains, dt, body["axes"], stage["ground"], stage["up"], back_directions(body, stage["front"]),
                            passes=C.LOOP_PASSES if looping else 1, lying=lying)


def bake_numpy(stage: dict, body: Dict[str, np.ndarray], role: str, dt: float, looping: bool) -> List[np.ndarray]:
    """Each plan's local quaternions (frames, bones, 4) for one role clip, by the rule of its region."""

    cloak = [plan for plan in stage["plans"] if plan["region"] == "cloak"]
    track = body_track(body)
    baked = dict(zip((id(plan) for plan in cloak), bake_cloak(cloak, body, stage, dt, looping, role))) if cloak else {}
    out = []
    for plan in stage["plans"]:
        if plan["region"] == "wings":
            quaternions = C.wing_quaternions(plan, body["parents"], role, stage, body["axes"], track)
        else:
            quaternions = baked[id(plan)]
        if looping:
            quaternions = C.close_loop(quaternions)
        out.append(quaternions)
    return out


def channelbag(armature, action):
    from bpy_extras import anim_utils

    return anim_utils.action_ensure_channelbag_for_slot(action, armature.animation_data.action_slot)


def write_rotation_keys(armature, action, name: str, frames, quaternions: np.ndarray) -> None:
    bag = channelbag(armature, action)
    path = f'pose.bones["{name}"].rotation_quaternion'
    for index in range(4):
        fcurve = bag.fcurves.find(path, index=index) or bag.fcurves.new(path, index=index)
        fcurve.keyframe_points.clear()
        fcurve.keyframe_points.add(len(frames))
        coordinates = np.empty(len(frames) * 2)
        coordinates[0::2] = frames
        coordinates[1::2] = quaternions[:, index]
        fcurve.keyframe_points.foreach_set("co", coordinates)
        for point in fcurve.keyframe_points:
            point.interpolation = "LINEAR"
        fcurve.update()


def bake_chains(armature, action, stage: dict, role: str) -> dict:
    """Key every chain bone of `stage` in `action` at every frame of the clip, by the rule of its region."""

    assign(armature, action)
    frames = action_frames(action)
    fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
    looping = role in C.LOOPING_ROLES
    folder = dump_folder()
    chain_names = {name for plan in stage["plans"] for name in plan["bones"]}
    wanted = [bone.name for bone in armature.data.bones if bone.name not in chain_names] if folder is not None else body_bones(stage)
    worlds = sample_worlds(armature, frames, wanted)
    if folder is not None:
        np.savez_compressed(folder / f"chain_role_{role}.npz", names=np.array(wanted), worlds=np.stack([worlds[n] for n in wanted], axis=1), fps=fps,
                            looping=looping)
    body = body_from_worlds(worlds, {name: rest_matrix(armature, name) for name in worlds}, body_bones(stage))
    report = {"frames": len(frames), "fps": round(fps, 3), "looping": looping, "chains": {}}
    for plan, quaternions in zip(stage["plans"], bake_numpy(stage, body, role, 1.0 / fps, looping)):
        for k, name in enumerate(plan["bones"]):
            write_rotation_keys(armature, action, name, frames, quaternions[:, k])
        report["chains"][plan["bones"][0].rsplit("_", 1)[0]] = {"fastest_step_degrees": round(C.fastest_step(quaternions), 1)}
    bpy.context.scene.frame_set(frames[0])
    return report


def plan_summary(stage: dict) -> dict:
    out = dict(stage["report"])
    out["chains"] = [{"bones": p["bones"], "omegas": [round(float(v), 2) for v in p["omegas"]],
                      "wing": {k: round(float(v), 2) for k, v in (p.get("wing") or {}).items() if np.ndim(v) == 0},
                      "follow": [{k: round(v, 3) for k, v in row.items()} for row in p.get("follow", [])]} for p in stage["plans"]]
    return out
