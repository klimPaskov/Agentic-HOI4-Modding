"""Blender side of the secondary-chain stage (the rules are in lib/tripo_chains.py): add chain bones to a region, rebind it, bake the motion.

`tripo/prepare_tripo_unit.py --chains cloak wings` calls `add_chains` once, after the kit's bones and weights are in place and the parts are
joined, and `bake_chains` once per role clip, after the arm level and before the snap easing (which then eases a chain bone a collision
turned fast). Nothing here takes a per-unit number.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

try:  # the planning functions are plain numpy, so tests and offline replays import this module without Blender
    import bpy
except ImportError:  # pragma: no cover - outside Blender
    bpy = None

from lib import tripo_chains as C

# Body capsules the cloth is kept out of: (name, from bone head, to bone head). The torso capsule runs from the hips to the neck.
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


# ---------------------------------------------------------------------------------------------
# Reading the rig
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


def body_frame(armature, heads: Dict[str, np.ndarray]):
    """(up, front, down): world up is +Z in Blender; front runs from the heels to the toes, made horizontal."""

    up = np.array([0.0, 0.0, 1.0])
    front = np.zeros(3)
    for side in ("Left", "Right"):
        front += heads[f"{side}ToeBase"] - heads[f"{side}Foot"]
    front -= (front @ up) * up
    return up, C.unit(front), -up


# ---------------------------------------------------------------------------------------------
# Planning the regions
# ---------------------------------------------------------------------------------------------


# Limb capsules for the cloak's "loose cloth" rule: (from bone head, to bone head, bones whose skin gives the radius). A hand runs on past
# its head by half its forearm.
LIMBS = tuple(
    (f"{side}{start}", f"{side}{end}", (f"{side}{start}",))
    for side in ("Left", "Right")
    for start, end in (("UpLeg", "Leg"), ("Leg", "Foot"), ("Arm", "ForeArm"), ("ForeArm", "Hand"), ("Hand", "Hand"))
)


def limb_capsules(ctx, excluded):
    """(a, b, radius) per limb in the rest pose, the radius from the limb's own skin outside `excluded`."""

    heads = ctx["heads"]
    out = []
    for start, end, bones in LIMBS:
        a, b = heads[start], heads[end]
        if start == end:  # the hand: on past its head by half the forearm
            forearm = heads[start] - heads[start.replace("Hand", "ForeArm")]
            b = a + 0.5 * forearm
        own = np.isin(ctx["dominant"], bones) & ~excluded
        out.append((a, b, C.capsule_radius(ctx["positions"][own], a, b)))
    return out


def plan_cloak(ctx):
    positions, heads, up, front = ctx["positions"], ctx["heads"], ctx["up"], ctx["front"]
    check = C.cloak_mask(positions, ctx["dominant"], heads["Hips"], front, up, ctx["height"])
    mask = C.cloak_rebind_mask(check, positions, ctx["edges"], ctx["dominant"], heads["Hips"], front, up, ctx["height"], limb_capsules(ctx, check))
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
        "layout": "fan", "check_vertices": int(check.sum()),
        "shape_inputs": {"length": round(length, 4), "width": round(width, 4), "segment": round(ctx["segment"], 4), "budget": ctx["budget"]},
    }]


def plan_wings(ctx):
    positions, heads, up, front = ctx["positions"], ctx["heads"], ctx["up"], ctx["front"]
    centre = heads["Hips"]
    lateral = C.unit(np.cross(up, front))
    left, right = C.wing_masks(positions, ctx["dominant"], centre, front, up)
    if left.sum() < 50 or right.sum() < 50:
        raise SystemExit(f"--chains wings found no pair of wings ({int(left.sum())} and {int(right.sum())} vertices beyond {C.WING_LATERAL_SHARE:.0%} of the width)")
    points = positions[left]
    root = C.wing_root(points, heads[C.CHAIN_PARENT])
    u, s, plane = C.wing_coordinates(points, root, front, up)
    low, high = np.percentile(u, [2.0, 98.0])
    length = float(np.percentile(s, 99))
    width = float(high - low) * float(np.median(s))
    chains, bones = C.chain_shape(length, width, ctx["segment"], ctx["budget"])
    chain_u, layout = C.ridge_angles(u, s, chains)
    joints, stations = C.sheet_layout(points, u, s, chain_u, bones)
    joints[:, 0] = root  # every finger chain starts at the wing root
    right_joints = np.stack([C.mirror_points(chain, centre, lateral) for chain in joints])
    common = {"chain_u": chain_u, "stations": stations, "layout": layout, "root": root, "plane": plane, "front": front,
              "points": points, "body_points": positions[~(left | right)], "height": ctx["height"],
              "shape_inputs": {"length": round(length, 4), "width": round(width, 4), "segment": round(ctx["segment"], 4), "budget": ctx["budget"]}}
    return [
        dict(common, region="wings", side="L", mask=left, joints=joints, coords=lambda pts: _fan_coordinates(pts, root, plane)),
        dict(common, region="wings", side="R", mask=right, joints=right_joints,
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


# ---------------------------------------------------------------------------------------------
# Adding bones and weights
# ---------------------------------------------------------------------------------------------


def bone_names(sheet) -> List[List[str]]:
    prefix = C.REGION_PREFIX[sheet["region"]] + sheet["side"]
    chains, bones = sheet["joints"].shape[0], sheet["joints"].shape[1] - 1
    return [[f"{prefix}{c + 1}_{b + 1}" for b in range(bones)] for c in range(chains)]


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


def chain_rows(rows, positions, edges, sheets, dominant):
    """Give each sheet's region its chains' weights whole, blended into the body's over one chain bone outward from the region's border
    (`lib.tripo_chains.blend_alpha`) but never into a forearm, hand, shin or foot (`lib.tripo_chains.is_limb_end`), at most 4
    influences. Returns the new rows and how many vertices changed."""

    changed = 0
    new_rows = list(rows)
    for sheet in sheets:
        names = [name for chain in bone_names(sheet) for name in chain]
        joints = sheet["joints"]
        blend = C.blend_length_for(joints, positions, edges, sheet["mask"])
        alpha = C.blend_alpha(positions, edges, sheet["mask"], blend, np.array([C.is_limb_end(name) for name in dominant]))
        sheet["blend_length"] = blend
        bound = np.where(alpha > 0)[0]
        u, s = sheet["coords"](positions[bound])
        chain_rows = C.sheet_weights(u, s, sheet["chain_u"], sheet["stations"])
        sheet["bound_vertices"] = int(len(bound))
        for vertex, chain_row in zip(bound, chain_rows):
            named = {names[index]: weight for index, weight in chain_row.items()}
            new_rows[vertex] = C.mix_weights(new_rows[vertex], named, float(alpha[vertex]))
            changed += 1
    return new_rows, changed


def write_groups(body, new_rows, changed: int) -> Dict[str, int]:
    """Replace the mesh's vertex groups with `new_rows`."""

    groups = sorted({name for row in new_rows for name in row} | {g.name for g in body.vertex_groups})
    for group in list(body.vertex_groups):
        body.vertex_groups.remove(group)
    made = {name: body.vertex_groups.new(name=name) for name in groups}
    for index, row in enumerate(new_rows):
        for name, weight in row.items():
            made[name].add([index], weight, "REPLACE")
    return {"vertices_rebound": changed, "max_influences": max(len(row) for row in new_rows)}


# ---------------------------------------------------------------------------------------------
# The plan the bake reads
# ---------------------------------------------------------------------------------------------


def capsule_radii(positions, dominant, heads, sheets):
    excluded = np.zeros(len(positions), bool)
    for sheet in sheets:
        excluded |= sheet["mask"]
    radii = {}
    for name, start, end in CAPSULES:
        own = np.isin(dominant, CAPSULE_BONES[name]) & ~excluded
        radii[name] = C.capsule_radius(positions[own], heads[start], heads[end])
    return radii


def wing_limits(sheet, heads, radii, up) -> Dict[str, float]:
    """The wing's pose room by rule (lib/tripo_chains.py): back swing, the side floor (the least back swing that keeps the wing off the
    body in the side views), the face turn of a retreat, down-stroke and death sag, from the torso's radius, the body and the wing's own
    chains. Computed once from the left wing (the right one is its mirror)."""

    plane, joints, chain_u = sheet["plane"], sheet["joints"], np.asarray(sheet["chain_u"])
    first = C.unit(joints[:, 1] - joints[:, 0])
    normal = C.unit(np.cross(plane[0], plane[1]))
    sweep = C.wing_sweep_degrees(float(sheet["shape_inputs"]["length"]), radii["Torso"])
    points, body, root, front, height = sheet["points"], sheet["body_points"], sheet["root"], sheet["front"], sheet["height"]
    side, _ceiling = C.wing_side_floor(points, body, root, front, up, height, sweep)
    # the face turn keeps the floor's swing and only tilts: a retreat swung further back (72 and 82 degrees on the demon) squashed its
    # beating membrane past UNIT-ANIM-STRETCH in the clip's first beats
    face_sweep, face_tilt = C.face_turn(normal, front, up, side, side)
    low = int(np.argmin(chain_u))
    low_rest = C.unit(np.diff(joints[low], axis=0))
    if sheet["side"] == "R":  # the pose rules work on the left wing; the right one is its mirror
        low_rest = C.mirror_directions(low_rest, C.unit(np.cross(up, front)))
    return {
        "low_rest": low_rest, "low_lengths": np.linalg.norm(np.diff(joints[low], axis=0), axis=1), "low_u": float(chain_u[low]),
        "root": np.asarray(joints[low, 0], float),
        "u_min": float(np.min(chain_u)), "normal": normal, "sweep": sweep, "side": side, "face_sweep": face_sweep, "face_tilt": face_tilt,
        "down": C.wing_down_degrees(first[int(np.argmin(chain_u))], -up),
        "droop": C.wing_droop_degrees(first[int(np.argmax(chain_u))], up),
    }


def chain_plan(armature, sheets, heads, radii, height, up) -> List[dict]:
    """Per chain: its bones, rest matrices, spring rates, collision radii and the bones each tail follows (the cloak rule)."""

    margin = C.COLLISION_MARGIN_SHARE * height
    plans = []
    for sheet in sheets:
        for c, chain in enumerate(bone_names(sheet)):
            joints = sheet["joints"][c]
            lengths = np.linalg.norm(np.diff(joints, axis=0), axis=1)
            parent = rest_matrix(armature, C.CHAIN_PARENT)
            relative, previous = [], parent
            for name in chain:
                own = rest_matrix(armature, name)
                relative.append(np.linalg.inv(previous) @ own)
                previous = own
            capsules = [(heads[start], heads[end], radii[name]) for name, start, end in CAPSULES]
            follow = C.torso_follow_weights(joints[1:], heads[C.CHAIN_PARENT], heads["Hips"], up) if sheet["region"] == "cloak" else []
            wing = None
            if sheet["region"] == "wings":
                wing = wing_limits(sheet, heads, radii, up)
            plans.append({
                "region": sheet["region"], "side": sheet["side"], "chain": c, "bones": chain, "lengths": lengths,
                "rest_relative": np.stack(relative), "omegas": C.pendulum_omegas(lengths, height), "rest_joints": joints,
                "radii": C.clearance_radii(joints[1:], capsules, margin), "chain_u": float(sheet["chain_u"][c]),
                "chains": len(sheet["chain_u"]), "tails": joints[1:], "follow": follow, "wing": wing,
                "rest_directions": C.unit(np.diff(joints, axis=0)), "parent_rest": parent,
            })
    return plans


def bone_parents(armature) -> Dict[str, str]:
    return {bone.name: (bone.parent.name if bone.parent else None) for bone in armature.data.bones}


def apply_plates(armature, rows, positions, edges, heads, dominant, up, front):
    """The `plates` region: each armour plate bound rigidly to its bone (`lib.tripo_chains.rigid_plates`). Returns the new rows and a report."""

    torso = np.isin(dominant, CAPSULE_BONES["Torso"])
    radius = C.capsule_radius(positions[torso], heads["Hips"], heads["neck"])
    masks = C.plate_masks(positions, heads, front, up, radius)
    return C.rigid_plates(rows, positions, edges, masks, C.bone_depths(bone_parents(armature)))


def add_chains(armature, body, regions: List[str]) -> dict:
    """Add the chains for `regions`, rebind their vertices and return the plan (`bake_chains` reads it) with a report."""

    unknown = [region for region in regions if region not in C.REGIONS]
    if unknown:
        raise SystemExit(f"--chains names unknown regions {unknown}; known: {list(C.REGIONS)}")
    heads = rest_heads(armature)
    up, front, down = body_frame(armature, heads)
    positions = body_positions(body)
    height = body_height(positions, up)
    edges = C.with_seams(positions, body_edges(body), height)
    rows = read_rows(body)
    dominant = dominant_names(rows)
    thigh = 0.5 * sum(float(np.linalg.norm(heads[f"{s}UpLeg"] - heads[f"{s}Leg"])) for s in ("Left", "Right"))
    segment = 0.5 * thigh
    budget = C.bone_budget(len(armature.data.bones), regions)
    ctx = {"positions": positions, "edges": edges, "dominant": dominant, "heads": heads, "up": up, "front": front,
           "height": height, "segment": segment, "budget": budget}
    sheets = []
    for region in regions:
        if region != "plates":
            sheets += (plan_cloak if region == "cloak" else plan_wings)(ctx)
    add_bones(armature, sheets, front)
    new_rows, changed = chain_rows(rows, positions, edges, sheets, dominant)
    plates = {}
    if "plates" in regions:
        # after the chains, so a chain's blend ring never reaches into a plate: the plate stays rigid
        new_rows, plates = apply_plates(armature, new_rows, positions, edges, heads, dominant, up, front)
    weights = write_groups(body, new_rows, changed)
    heads = rest_heads(armature)
    radii = capsule_radii(positions, dominant, heads, sheets)
    plans = chain_plan(armature, sheets, heads, radii, height, up)
    ground = float((positions @ up).min()) + C.GROUND_MARGIN_SHARE * height
    report = {
        "regions": regions, "bones_after": len(armature.data.bones), "segment": round(segment, 4), "budget_per_side": budget,
        "weights": weights, "capsule_radii": {k: round(v, 4) for k, v in radii.items()}, "plates": plates,
        "sheets": [{"region": s["region"], "side": s["side"], "vertices": int(s["mask"].sum()), "chains": int(s["joints"].shape[0]),
                    "bones_per_chain": int(s["joints"].shape[1] - 1), "layout": s["layout"], "check_vertices": s.get("check_vertices"), "shape_inputs": s["shape_inputs"],
                    "blend_length": round(s.get("blend_length", 0.0), 4), "bound_vertices": s.get("bound_vertices")} for s in sheets],
    }
    if len(armature.data.bones) > C.MAX_BONES:
        raise SystemExit(f"The chains bring the rig to {len(armature.data.bones)} bones (HOI4 allows {C.MAX_BONES})")
    return {"plans": plans, "sheets": sheets, "up": up, "front": front, "down": down, "height": height, "ground": ground, "report": report}


# ---------------------------------------------------------------------------------------------
# Baking
# ---------------------------------------------------------------------------------------------


def assign(armature, action) -> None:
    armature.animation_data_create()
    armature.animation_data.action = action
    slots = getattr(action, "slots", None)
    if slots is not None and len(slots):
        armature.animation_data.action_slot = slots[0]


def sample_body(armature, frames, skinned) -> Dict[str, np.ndarray]:
    """Per frame: the chain parent's world matrix (rotation and translation), the capsule axes and, for each bone in `skinned`, its
    skinning matrix (posed world matrix times the inverse of its rest world matrix)."""

    scene = bpy.context.scene
    world = as_array(armature.matrix_world)
    bones = armature.pose.bones
    parents = np.zeros((len(frames), 4, 4))
    axes = np.zeros((len(frames), len(CAPSULES), 2, 3))
    skinned = sorted(set(skinned) | {"Hips"})
    rest_inverse = {name: np.linalg.inv(world @ as_array(armature.data.bones[name].matrix_local)) for name in skinned}
    skinning = {name: np.zeros((len(frames), 4, 4)) for name in skinned}
    for i, frame in enumerate(frames):
        scene.frame_set(frame)
        parents[i] = C.orthonormal(world @ as_array(bones[C.CHAIN_PARENT].matrix))
        for c, (_name, start, end) in enumerate(CAPSULES):
            for e, bone in enumerate((start, end)):
                axes[i, c, e] = world[:3, :3] @ np.array(bones[bone].head) + world[:3, 3]
        for name in skinned:
            skinning[name][i] = world @ as_array(bones[name].matrix) @ rest_inverse[name]
    return {"parents": parents, "axes": axes, "skinning": skinning}


def body_track(body: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """Per frame, the world positions of the hips, the feet and the two knees (frames, 2, 3), read off the capsule axes (the wing rule
    times a death's fold by the hips, keeps a dying wing above the knees and times a move's beats by the feet)."""

    names = [name for name, _start, _end in CAPSULES]
    return {"Hips": body["axes"][:, names.index("Torso"), 0], "LeftFoot": body["axes"][:, names.index("LeftShin"), 1],
            "RightFoot": body["axes"][:, names.index("RightShin"), 1],
            "knees": np.stack([body["axes"][:, names.index("LeftShin"), 0], body["axes"][:, names.index("RightShin"), 0]], axis=1)}


def back_directions(body: Dict[str, np.ndarray], front: np.ndarray) -> np.ndarray:
    """Per frame, the rest pose's backward direction carried by the hips: the way a collision pushes cloth off the legs and body."""

    return np.stack([C.unit(C.orthonormal(matrix)[:3, :3] @ -front) for matrix in body["skinning"]["Hips"]])


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


def bake_cloak(plans, body, stage, dt, looping) -> List[np.ndarray]:
    """The cloak rule for all its chains at once (`lib.tripo_chains.simulate_sheet`): each tail follows the upper spine and the hips by
    its height, through the spring, and the sheet is pushed off the legs and torso along the hips' back direction."""

    chains = [dict(plan, follow_points=C.follow_targets(plan["tails"], plan["follow"], body["skinning"])) for plan in plans]
    return C.simulate_sheet(body["parents"], chains, dt, body["axes"], stage["ground"], stage["up"], back_directions(body, stage["front"]),
                            passes=C.LOOP_PASSES if looping else 1)


def bake_chains(armature, action, stage: dict, role: str) -> dict:
    """Key every chain bone of `stage` in `action` at every frame of the clip, by the rule of its region."""

    assign(armature, action)
    start, end = int(action.frame_range[0]), int(action.frame_range[1])
    frames = list(range(start, end + 1))
    fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
    dt = 1.0 / fps
    looping = role in C.LOOPING_ROLES
    skinned = sorted({name for plan in stage["plans"] for row in plan.get("follow", []) for name in row})
    body = sample_body(armature, frames, skinned)
    report = {"frames": len(frames), "fps": round(fps, 3), "looping": looping, "chains": {}}
    cloak = [plan for plan in stage["plans"] if plan["region"] == "cloak"]
    track = body_track(body)
    baked = dict(zip((id(plan) for plan in cloak), bake_cloak(cloak, body, stage, dt, looping))) if cloak else {}
    for plan in stage["plans"]:
        if plan["region"] == "wings":
            quaternions = C.wing_quaternions(plan, body["parents"], role, stage, body["axes"], track)
        else:
            quaternions = baked[id(plan)]
        if looping:
            quaternions = C.close_loop(quaternions)
        for k, name in enumerate(plan["bones"]):
            write_rotation_keys(armature, action, name, frames, quaternions[:, k])
        report["chains"][plan["bones"][0].rsplit("_", 1)[0]] = {"fastest_step_degrees": round(C.fastest_step(quaternions), 1)}
    bpy.context.scene.frame_set(start)
    return report


def plan_summary(stage: dict) -> dict:
    out = dict(stage["report"])
    out["chains"] = [{"bones": p["bones"], "omegas": [round(float(v), 2) for v in p["omegas"]],
                      "wing": {k: round(float(v), 2) for k, v in (p.get("wing") or {}).items() if np.ndim(v) == 0},
                      "follow": [{k: round(v, 3) for k, v in row.items()} for row in p.get("follow", [])]} for p in stage["plans"]]
    return out
