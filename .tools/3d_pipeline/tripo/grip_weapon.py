"""The grip stage: close a rigged Tripo body's hand around a separately modelled weapon. Run in headless Blender.

    blender -b --factory-startup --python grip_weapon.py -- <body.glb> <weapon.glb> --out <gripped.glb>
        [--report report.json] [--hand RightHand] [--grip 0.60] [--length-ratio 1.06] [--roll 0]
        [--head-toward index|pinky] [--hold-clips idle,walk,hit_to_body_01,flee_01] [--hold-hand 0.257,0.07,0.61]
        [--hold-axis 0,0,1] [--check-frames 6]

The body is one GLB with the 65-joint Mixamo skeleton (open, relaxed hands) and every clip; the weapon is
an unrigged model. The stage runs while the finger bones still exist, before `prepare_tripo_unit.py` cuts the
skeleton to 22 bones and merges the fingers into the hand:

1. Place the weapon. It is scaled so its long axis is `--length-ratio` times the body's height, and its grip
   point (`--grip`, the share of its length from the butt) goes into the palm of `--hand`. The haft lies
   diagonally across the palm, from the base of the little finger to the web between thumb and index finger,
   with the head toward `--head-toward` and the blade plane turned `--roll` degrees about the haft (0: the blade
   spreads along the normal of the palm). Where the line starts and ends and how deep it sits is searched, so the
   palm pad touches it and the fingers wrap it.
2. Close the hand as a power grip (broom handle). Each of the four fingers wraps the haft with all three joints bent
   (about 70, 90 and 50 degrees, fitted to the measured radius, `lib/tripo_grip.solve_finger`) with nothing of
   the finger inside the haft. The thumb closes from the opposite side, round the haft and over the middle
   segments of the index and middle fingers (`lib/tripo_grip.solve_thumb`), with no part of it inside the haft.
   The shape is baked into the body mesh as its rest pose, the finger bones go back to rest (fingers then move
   with the hand, as the kit's later merge of the finger bones into the hand makes them anyway) and the finger
   channels of the hand are dropped from every clip (the clips pose the fingers, which would undo the fist).
3. Hold the arm up. The clips are made for an empty hand, so in the clips named in `--hold-clips` the weapon arm
   (shoulder, arm, forearm, hand) gets a constant extra rotation, found per clip so that at the clip's first frame
   the grip point sits at `--hold-hand` (out from the body, forward, up, as shares of the body height) and the
   haft points along `--hold-axis`. The offset is multiplied into every key of the four bones (`q_clip @ q_hold`),
   so the clip's own swing stays.
4. Bind the weapon rigidly to the hand (weight 1.0) as mesh `tripo_part_1`, name the body `tripo_part_0`, export
   one GLB with every clip, and measure: finger gaps to the haft on sampled frames of every clip, the weapon
   arm against the torso before and after the hold.

5. The death rule, drop before the fall (`--release-clips CLIP`, one rule for every armed unit, no per-clip numbers). The
   hand lets go of the weapon at the first frame of the fall: the first frame where the pelvis starts to descend for good,
   or the hand has dropped `--release-drop` (default 0.04) of the body height, whichever comes first
   (`lib/tripo_clearance.fall_start_frame`). The arm hold has faded out by then. The weapon falls on its own path, a short
   fixed-duration tumble under gravity (0.4 s), and lies flat on the ground (haft level, blade flat, lowest point on the
   ground plane and never under it), at least 4% of the height clear of every point the body occupies from the landing
   on, on the side away from where the body falls, and stays exactly still to the end of the clip
   (`lib/tripo_clearance.plan_drop`). The weapon bone is keyed with rotation and location in every frame from the release,
   the pose that holds the weapon on that path whatever the hand does (the retarget keeps the location keys of the job's weapon bone for
   its release roles: `location_bones` in run_pilot, `blender_worker.retarget_location_bones`). The pipeline later lifts every frame so the
   body's lowest point is on the ground, and the weapon with it, so the path is planned in that grounded world (`grounding_lifts`). The job names the clip with
   `tripo.weapon.release_roles` and check_unit_files.py then excuses a part bound wholly to that weapon bone from the
   drift test only. The run fails (exit 3, `DROP_FAILED`) when the planned or measured result has the weapon inside the
   body or under the ground. Its stillness after the landing is judged on the exported files (the GLB's measure is a diagnostic).

The result has the shape of Tripo's in-hand export, so `prepare_tripo_unit.py --rigid-part tripo_part_1=RightHand`
takes it unchanged.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from functools import partial
from pathlib import Path
from types import SimpleNamespace

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import tripo_clearance as CL
from lib import tripo_grip as G
from lib.tripo import resolve_clip_name
import assemble_separate as A
import clip_check as cc

FINGERS = ("Index", "Middle", "Ring", "Pinky", "Thumb")
PREFIX = "mixamorig:"
# Skin of these bones is kept clear like the cloak (`soft_cloth_mask`, `--soft-share` of the height): the head and the feet.
KEEP_CLEAR_BONES = ("Head", "head", "neck", "Neck", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase", "LeftToe_End", "RightToe_End")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("body", type=Path)
    parser.add_argument("weapon", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--hand", default="RightHand")
    parser.add_argument("--grip", type=float, default=0.60)
    parser.add_argument("--length-ratio", type=float, default=1.06)
    parser.add_argument("--roll", type=float, default=0.0)
    parser.add_argument("--head-toward", choices=("index", "pinky"), default="index")
    parser.add_argument("--hold-clips", default="")
    parser.add_argument("--hold-fade-clips", default="", help="clips that get the hold at full weight on their first frame, faded out as the arm starts to rise")
    parser.add_argument("--release-clips", default="", help="clips in which the weapon bone lets go of the hand and the weapon falls to the ground")
    parser.add_argument("--release-drop", type=float, default=0.04, help="a release clip lets go of the weapon at the first frame of the fall: the pelvis starts to descend for good, or the hand has dropped this share of the body height below its first-frame height, whichever comes first")
    parser.add_argument("--release-ease-frames", type=int, default=18, help="(kept for old commands, no longer used: the fall is a fixed 0.4 s tumble)")
    parser.add_argument("--dump-grip", type=Path, default=None, help="save the hand geometry the grip search works on (an .npz) for offline work")
    parser.add_argument("--diagonal-min", type=float, default=28.0, help="least angle (degrees) of the haft to the palm closing axis")
    parser.add_argument("--diagonal-max", type=float, default=55.0)
    parser.add_argument("--clearance-clips", default="", help="the clips the clearance rule works on (names or starts of names, comma separated); default every clip. Name the clips the unit uses: each frame that fails costs seconds")
    parser.add_argument("--soft-share", type=float, default=CL.SOFT_SHARE, help="cloth that a later stage swings (a cloak) is kept this share of the body height clear of the weapon, because the chain stage moves it off the pose judged here (0 switches it off)")
    parser.add_argument("--no-clearance", action="store_true", help="skip the clearance rule (see lib/tripo_clearance.py): by default every clip is checked per frame and the hand is turned about the wrist until the weapon leaves the body")
    parser.add_argument("--clearance-allow-fail", action="store_true", help="exit 0 even when a frame cannot be cleared within the cap (the report and TRIPO-WEAPON-IN-BODY still say so)")
    parser.add_argument("--weapon-bone", action="store_true", help="bind the weapon to its own bone (child of the hand) instead of the hand bone")
    parser.add_argument("--hold-hand", default="0.257,0.07,0.61", help="out, forward, up of the grip point, as shares of the body height")
    parser.add_argument("--hold-axis", default="0,0,1")
    parser.add_argument("--ease-snaps", type=float, default=14.0, help="the degrees per frame above which the unit's intake eases a joint turn (tripo_intake.DEFAULT_EASE_SNAPS, the job's `ease_snaps`): the clips are eased the same way here, so the hand the clearance rule and the drop are judged on is the hand the exported clip has")
    parser.add_argument("--check-frames", type=int, default=6)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def action_fcurves(action):
    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        for fcurve in list(legacy):
            yield fcurve, legacy
        return
    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            for channelbag in getattr(strip, "channelbags", []):
                fcurves = getattr(channelbag, "fcurves", None)
                if fcurves is not None:
                    for fcurve in list(fcurves):
                        yield fcurve, fcurves


def use_action(arm, action):
    arm.animation_data_create()
    arm.animation_data.action = action
    slots = getattr(action, "slots", None)
    if slots is not None and len(slots):
        arm.animation_data.action_slot = slots[0]


def world_array(obj, local) -> np.ndarray:
    matrix = np.array(obj.matrix_world)
    return np.asarray(local) @ matrix[:3, :3].T + matrix[:3, 3]


def mesh_coords(obj) -> np.ndarray:
    data = np.empty(len(obj.data.vertices) * 3)
    obj.data.vertices.foreach_get("co", data)
    return data.reshape(-1, 3)


def evaluated_coords(obj) -> np.ndarray:
    graph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh()
    data = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", data)
    evaluated.to_mesh_clear()
    return world_array(obj, data.reshape(-1, 3))


def body_triangles(obj) -> np.ndarray:
    mesh = obj.data
    mesh.calc_loop_triangles()
    tri = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", tri)
    return tri.reshape(-1, 3)


def dominant_groups(obj) -> np.ndarray:
    names = {g.index: g.name for g in obj.vertex_groups}
    out = np.empty(len(obj.data.vertices), dtype=object)
    for v in obj.data.vertices:
        best = max(v.groups, key=lambda g: g.weight, default=None)
        out[v.index] = names.get(best.group, "") if best else ""
    return out


def rest_head(arm, name) -> np.ndarray:
    return world_array(arm, [arm.data.bones[name].head_local])[0]


def rest_tail(arm, name) -> np.ndarray:
    return world_array(arm, [arm.data.bones[name].tail_local])[0]


def finger_names(hand: str, finger: str):
    return [f"{PREFIX}{hand}{finger}{i}" for i in (1, 2, 3, 4)]


def set_pose_matrix(arm, bone_name, axis, angle, pivot):
    """Turn a pose bone (and its children, which follow) about a world axis through a world pivot."""

    pb = arm.pose.bones[bone_name]
    inverse = arm.matrix_world.inverted()
    axis_local = (inverse.to_3x3() @ Vector(axis)).normalized()
    pivot_local = inverse @ Vector(pivot)
    rotation = Matrix.Rotation(angle, 4, axis_local)
    pb.matrix = Matrix.Translation(pivot_local) @ rotation @ Matrix.Translation(-pivot_local) @ pb.matrix
    bpy.context.view_layer.update()


def finger_activity(arm, hand):
    """The largest rotation of any finger bone of `hand` from its rest, per clip, over sampled frames."""

    names = [n for finger in FINGERS for n in finger_names(hand, finger)]
    result = {}
    for action in bpy.data.actions:
        use_action(arm, action)
        f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
        worst = 0.0
        for frame in sorted({f0, f1, *range(f0, f1 + 1, max(1, (f1 - f0) // 8))}):
            bpy.context.scene.frame_set(frame)
            for name in names:
                q = arm.pose.bones[name].rotation_quaternion
                worst = max(worst, 2 * math.degrees(math.acos(min(1.0, abs(q.w)))))
        result[action.name] = round(worst, 1)
    return result


def hand_positions(arm, hand, frames=9):
    """Where the hand sits in each clip, relative to the shoulder, as shares of the body height (mean and range)."""

    out = {}
    shoulder = f"{PREFIX}{hand.replace('Hand', 'Shoulder')}"
    for action in bpy.data.actions:
        use_action(arm, action)
        f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
        samples = []
        for frame in np.linspace(f0, f1, frames).round().astype(int):
            bpy.context.scene.frame_set(int(frame))
            hand_pos = np.array(arm.matrix_world @ arm.pose.bones[PREFIX + hand].head)
            shoulder_pos = np.array(arm.matrix_world @ arm.pose.bones[shoulder].head)
            samples.append(hand_pos - shoulder_pos)
        samples = np.array(samples)
        out[action.name] = {"mean": np.round(samples.mean(axis=0), 3).tolist(), "range": np.round(np.ptp(samples, axis=0), 3).tolist()}
    return out


def torso_inside_share(body, groups, arm_names, coords):
    """Share of the weapon arm's skin vertices that sit inside the torso (ray parity on the torso triangles)."""

    torso = np.array([any(k in g for k in ("Spine", "Hips", "Neck")) for g in groups])
    triangles = body_triangles(body)
    keep = triangles[torso[triangles].all(axis=1)]
    arm_mask = np.isin(groups, arm_names)
    if not len(keep) or not arm_mask.any():
        return 0.0
    return float(np.mean(cc.points_inside_mesh(coords[arm_mask], coords[keep])))


WEAPON_BONE = "Weapon"


def rotation_curves(action):
    """{bone: {component: fcurve}} of the quaternion rotation channels."""

    found = {}
    for fcurve, _c in action_fcurves(action):
        if fcurve.data_path.startswith("pose.bones[") and fcurve.data_path.endswith(".rotation_quaternion"):
            found.setdefault(fcurve.data_path.split('"')[1], {})[fcurve.array_index] = fcurve
    return {bone: curves for bone, curves in found.items() if len(curves) == 4}


def key_quaternions(curves):
    count = len(curves[0].keyframe_points)
    return [Quaternion([curves[i].keyframe_points[k].co.y for i in range(4)]) for k in range(count)]


def write_quaternions(curves, quaternions):
    for k, q in enumerate(quaternions):
        for i in range(4):
            point = curves[i].keyframe_points[k]
            point.co.y = q[i]
            point.handle_left.y = q[i]
            point.handle_right.y = q[i]
    for fcurve in curves.values():
        fcurve.update()


def step_degrees(a, b):
    return 2.0 * math.degrees(math.acos(min(1.0, abs(a.dot(b)))))


def step_rates(values, frames):
    """Degrees per frame between neighbouring keys."""

    return [step_degrees(values[k - 1], values[k]) / max(frames[k] - frames[k - 1], 1e-6) for k in range(1, len(values))]


def normalise_rotation_keys(action, trigger_degrees=20.0, target_degrees=15.0, max_window=16):
    """Keep every bone's quaternions on one hemisphere and ease a snap over more frames.

    A step faster than `trigger_degrees` per frame is replaced by a slerp between the keys `w` frames before and
    after it, with the smallest `w` (up to `max_window`) that brings every step in the range to `target_degrees`
    per frame or less. Returns what was found: flips fixed, and per bone the fastest step before and after
    (degrees per frame) for the bones that had a flip or a step over the trigger.
    """

    out = {"flips_fixed": 0, "snaps_eased": {}}
    for bone, curves in rotation_curves(action).items():
        quats = key_quaternions(curves)
        frames = [kp.co.x for kp in curves[0].keyframe_points]
        rates = partial(step_rates, frames=frames)
        flips = 0
        for k in range(1, len(quats)):
            if quats[k].dot(quats[k - 1]) < 0:
                quats[k].negate()
                flips += 1
        before = max(rates(quats), default=0.0)
        eased = []
        k = 1
        while k < len(quats):
            if rates(quats)[k - 1] > trigger_degrees:
                for window in range(2, max_window + 1):
                    a, b = max(k - window, 0), min(k + window - 1, len(quats) - 1)
                    trial = list(quats)
                    for m in range(a, b + 1):
                        trial[m] = quats[a].slerp(quats[b], (frames[m] - frames[a]) / max(frames[b] - frames[a], 1e-6))
                    if max(rates(trial)[max(a - 1, 0): b + 1], default=0.0) <= target_degrees or (a == 0 and b == len(quats) - 1):
                        quats = trial
                        eased.append([int(frames[a]), int(frames[b])])
                        k = b
                        break
            k += 1
        after = max(rates(quats), default=0.0)
        out["flips_fixed"] += flips
        if flips or eased or before > trigger_degrees:
            out["snaps_eased"][bone.replace(PREFIX, "")] = {"flips": flips, "per_frame_before": round(before, 1), "per_frame_after": round(after, 1), "eased_frames": eased}
        write_quaternions(curves, quats)
    return out


ARM_SCALES = (0.3, 1.0, 1.0, 1.0)  # how much of the solved rotation each of shoulder, arm, forearm and hand takes
FOUR = ("Index", "Middle", "Ring", "Pinky")


def load_body(c):
    """Import the rigged body, take its measures and put every bone at rest."""

    args, hand = c.args, c.hand
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(args.body))
    armature_objects = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    arm = max(armature_objects, key=lambda o: len(o.data.bones))
    skinned = [o for o in bpy.data.objects if o.type == "MESH" and len(o.vertex_groups) > 0]
    if len(skinned) != 1:
        raise SystemExit(f"Expected one skinned body mesh, found {[o.name for o in skinned]}")
    body = skinned[0]
    for obj in [o for o in bpy.data.objects if o.type == "MESH" and o is not body]:
        bpy.data.objects.remove(obj, do_unlink=True)  # the importer's bone-shape sphere
    c.arm, c.body, c.scene = arm, body, bpy.context.scene
    c.rest_coords = world_array(body, mesh_coords(body))
    c.height = float(np.ptp(c.rest_coords[:, 2]))
    c.ground = float(c.rest_coords[:, 2].min())
    c.centre_x = float(c.rest_coords[:, 0].mean())
    c.report["body_height"] = round(c.height, 4)
    c.report["finger_rotation_in_clips_degrees"] = finger_activity(arm, hand)
    c.report["hand_vs_shoulder_in_clips"] = hand_positions(arm, hand)
    arm.animation_data_create()
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def find_hand_frame(c):
    """The hand's frame: closing axis (index to pinky), forward, palm normal and the palm's surface."""

    arm, body, hand, height, rest_coords = c.arm, c.body, c.hand, c.height, c.rest_coords
    c.wrist = wrist = rest_head(arm, PREFIX + hand)
    c.base = base = {f: rest_head(arm, finger_names(hand, f)[0]) for f in FINGERS}
    c.closing = closing = G.unit(base["Pinky"] - base["Index"])
    knuckles = np.mean([base[f] for f in FOUR], axis=0)
    c.forward = forward = G.unit(base["Middle"] - wrist)
    normal0 = G.unit(np.cross(closing, forward))
    c.palm_centre = palm_centre = 0.5 * (knuckles + wrist) * 0.4 + 0.6 * knuckles
    thumb_side = float((base["Thumb"] - palm_centre) @ normal0)
    c.normal = normal = normal0 if thumb_side >= 0 else -normal0
    c.report["palm"] = {"closing_index_to_pinky": np.round(closing, 3).tolist(), "fingers_forward": np.round(forward, 3).tolist(),
                        "normal_to_palm_side": np.round(normal, 3).tolist(), "thumb_offset_along_normal": round(thumb_side, 4)}
    family = [g.name for g in body.vertex_groups if g.name.startswith(PREFIX + hand)]
    c.groups = groups = dominant_groups(body)
    c.hand_points = rest_coords[np.isin(groups, family)]
    # the palm itself: the vertices that follow the hand bone and no finger, near the palm (a bracer or a limb
    # that happens to be close would put the surface far out)
    own = rest_coords[groups == PREFIX + hand]
    in_plane = np.linalg.norm((own - palm_centre) - np.outer((own - palm_centre) @ normal, normal), axis=1)
    c.near_palm = near_palm = own[in_plane < 0.06 * height]
    c.palm_surface = float(np.percentile((near_palm - palm_centre) @ normal, 90)) if len(near_palm) else 0.0
    c.report["palm"]["surface_offset"] = round(c.palm_surface, 4)


def find_finger_skins(c):
    """Each finger's skin and the bone it follows."""

    arm, body, hand, height, rest_coords = c.arm, c.body, c.hand, c.height, c.rest_coords
    weights_by_group = {}
    for g in body.vertex_groups:
        if g.name.startswith(PREFIX + hand):
            column = np.zeros(len(body.data.vertices))
            for v in body.data.vertices:
                for item in v.groups:
                    if item.group == g.index:
                        column[v.index] = item.weight
            weights_by_group[g.name] = column
    c.finger_index, c.finger_level, c.finger_tip = {}, {}, {}
    for finger in FINGERS:
        names = finger_names(hand, finger)
        stack = np.array([weights_by_group.get(n, np.zeros(len(rest_coords))) for n in names])
        index = np.where(stack.sum(axis=0) > 0.5)[0]
        # only skin near the finger's own bones: a stray vertex weighted to a finger (a bracer edge, a seam) would
        # stop the curl at the first touch and sit far from the haft in every check
        chain = np.array([rest_head(arm, n) for n in names] + [rest_tail(arm, names[3])])
        near = np.linalg.norm(rest_coords[index][:, None, :] - G.segment_points(chain, 8)[None, :, :], axis=2).min(axis=1) < 0.06 * height
        c.report.setdefault("finger_skin_dropped_as_stray", {})[finger] = int((~near).sum())
        index = index[near]
        c.finger_index[finger] = index
        c.finger_level[finger] = stack[:, index].argmax(axis=0)
        base_joint = rest_head(arm, names[0])
        c.finger_tip[finger] = int(np.argmax(np.linalg.norm(rest_coords[index] - base_joint, axis=1)))  # index into `index`


def load_weapon(c):
    """Import the weapon, scale it to `--length-ratio` of the body height and measure its haft."""

    args, height = c.args, c.height
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(args.weapon))
    weapon_objects = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if len(weapon_objects) != 1:
        raise SystemExit(f"Expected one weapon mesh, found {[o.name for o in weapon_objects]}")
    c.weapon = weapon_objects[0]
    for obj in [o for o in bpy.data.objects if o not in before and o.type != "MESH"]:
        bpy.data.objects.remove(obj, do_unlink=True)
    w_world = world_array(c.weapon, mesh_coords(c.weapon))
    axes = A.weapon_axes(w_world, args.grip)
    c.scale = args.length_ratio * height / axes["length"]
    c.local = c.scale * ((w_world - axes["grip_point"]) @ axes["axes"])  # (along the haft to the head, blade, third)
    c.radius = G.haft_radius(c.local, np.zeros(3), np.array([1.0, 0.0, 0.0]), 0.0, 0.03 * args.length_ratio * height)


def haft_line(c, l0, mu, delta, back=0.0):
    """A haft line across the palm: from `l0` along wrist-to-pinky to `mu` along index-to-thumb, seated `delta` off the palm surface."""

    start_point = c.wrist + l0 * (c.base["Pinky"] - c.wrist)
    web = c.base["Index"] + mu * (c.base["Thumb"] - c.base["Index"]) - back * c.fingers_forward
    direction = G.unit(web - start_point)
    direction = G.unit(direction - (direction @ c.normal) * c.normal)
    middle = 0.5 * (start_point + web)
    middle = middle - ((middle - c.palm_centre) @ c.normal) * c.normal + c.normal * (c.palm_surface + c.radius + delta)
    return middle, direction


def palm_cost(c, point, direction):
    gap = G.signed_gaps(c.palm_skin, point, direction, c.radius)
    return 4.0 * max(float(gap.min()), 0.0) + 20.0 * max(-float(gap.min()) - 0.003 * c.height, 0.0) if len(gap) else 0.0


def solve_four(c, point, direction, step):
    results, total = {}, 0.0
    for finger in FOUR:
        results[finger] = G.solve_finger(c.joints_rest[finger], c.skin_rest[finger], c.finger_level[finger], point, direction, c.radius,
                                         c.closing, c.normal, c.tolerance, step=step)
        total += results[finger]["cost"]
    return total + palm_cost(c, point, direction), results


def dump_grip(c):
    """Save the hand geometry the grip search works on (an .npz) for offline work."""

    near = np.linalg.norm(c.rest_coords - c.palm_centre, axis=1) < 0.15 * c.height
    arrays = {"height": c.height, "radius": c.radius, "palm_surface": c.palm_surface, "palm_centre": c.palm_centre, "normal": c.normal,
              "closing": c.closing, "forward": c.forward, "wrist": c.wrist, "palm_skin": c.palm_skin, "hand_points": c.hand_points,
              "near_points": c.rest_coords[near], "near_groups": np.array(c.groups)[near]}
    for f in FINGERS:
        arrays[f"joints_{f}"], arrays[f"skin_{f}"], arrays[f"level_{f}"], arrays[f"base_{f}"] = c.joints_rest[f], c.skin_rest[f], c.finger_level[f], c.base[f]
    np.savez(c.args.dump_grip, **arrays)


def search_grip(c):
    """A power grip: the haft lies diagonally across the palm.

    From the base of the little finger to the web between thumb and index finger. The haft is seated into the palm until the palm pad touches
    it, all four fingers wrap round it with the curl spread over all three joints, and the thumb closes from the other side and rests on the
    fingers. The place of the haft is searched: where the line starts on the little-finger side, where it ends in the web, and how deep it sits.
    """

    args, hand, height = c.args, c.hand, c.height
    c.fingers_forward = G.unit(c.forward - (c.forward @ c.closing) * c.closing)
    c.joints_rest = {f: np.array([rest_head(c.arm, n) for n in finger_names(hand, f)]) for f in FINGERS}
    c.skin_rest = {f: c.rest_coords[c.finger_index[f]] for f in FINGERS}
    c.tolerance = 0.0015 * height
    c.palm_skin = c.near_palm[(c.near_palm - c.palm_centre) @ c.normal > c.palm_surface - 0.02 * height]
    if args.dump_grip:
        dump_grip(c)
    candidates = []
    for l0 in (0.1, 0.25, 0.4, 0.55):
        for mu in (0.05, 0.2, 0.35, 0.5, 0.7):
            for delta in (-0.008, -0.004, 0.0, 0.004, 0.008):
                for back in (0.0, 0.01):
                    point, direction = haft_line(c, l0, mu, delta * height, back * height)
                    diagonal = float(np.degrees(np.arccos(min(abs(float(direction @ c.closing)), 1.0))))
                    if args.diagonal_min <= diagonal <= args.diagonal_max:
                        total, _r = solve_four(c, point, direction, 15.0)
                        candidates.append((total, l0, mu, delta, back))
    if not candidates:
        raise SystemExit("No haft line across the palm lies between the diagonal limits; widen --diagonal-min/--diagonal-max")
    candidates.sort()
    c.candidates = candidates
    _total, c.best_l0, c.best_mu, c.best_delta, c.best_back = candidates[0]
    c.haft_centre, c.axis_direction = haft_line(c, c.best_l0, c.best_mu, c.best_delta * height, c.best_back * height)
    c.fit_cost, c.results = solve_four(c, c.haft_centre, c.axis_direction, 10.0)
    c.head_dir = c.axis_direction if args.head_toward == "index" else -c.axis_direction
    c.blade = G.rodrigues(c.head_dir, np.radians(args.roll)) @ c.normal
    c.third = np.cross(c.head_dir, c.blade)
    c.placed = c.haft_centre + c.local[:, 0:1] * c.head_dir + c.local[:, 1:2] * c.blade + c.local[:, 2:3] * c.third


def close_thumb(c):
    """The thumb: closes from the opposite side, round the haft and over the fingers."""

    results, finger_level = c.results, c.finger_level
    obstacle_points = np.concatenate([results[f]["skin"] for f in FOUR])
    obstacle_points = obstacle_points[:: max(1, len(obstacle_points) // 300)]
    tip_masks = {f: finger_level[f] == finger_level[f].max() for f in FOUR}
    c.fingertip_side = G.unit(np.mean([G.radial_unit(results[f]["skin"][tip_masks[f]].mean(axis=0), c.haft_centre, c.axis_direction) for f in FOUR], axis=0))
    c.middle_segments_posed = np.concatenate([results[f]["skin"][finger_level[f] == 1] for f in ("Index", "Middle")])
    results["Thumb"] = G.solve_thumb(c.joints_rest["Thumb"], c.skin_rest["Thumb"], finger_level["Thumb"], c.haft_centre, c.axis_direction, c.radius,
                                     obstacle_points, tolerance=0.003 * c.height, target_skin=c.middle_segments_posed, away_from=c.fingertip_side)
    for finger in FINGERS:
        results[finger]["why"] = ["fitted"] * 3


def describe_grip(c):
    """What the grip looks like, in numbers: for every finger the gap of its tip and its deepest skin to the haft surface."""

    results, finger_level, haft_centre, axis_direction, radius, args = c.results, c.finger_level, c.haft_centre, c.axis_direction, c.radius, c.args

    def tip_of(finger):
        return finger_level[finger] == finger_level[finger].max()

    grip_numbers = {}
    for finger in FINGERS:
        gap = G.signed_gaps(results[finger]["skin"], haft_centre, axis_direction, radius)
        tip_points_world = results[finger]["skin"][[i for i, lv in enumerate(finger_level[finger]) if lv == int(finger_level[finger].max())]]
        tip = tip_points_world.mean(axis=0) if len(tip_points_world) else results[finger]["joints"][3]
        grip_numbers[finger] = {
            "tip_gap_to_haft": round(float(gap[tip_of(finger)].min()) if (tip_of(finger)).any() else float("nan"), 4),
            "deepest_skin_in_haft": round(float(-gap.min()), 4),
            "angle_around_haft_from_palm_normal_degrees": round(G.radial_angle(tip, haft_centre, axis_direction, c.normal), 1),
            "tip_along_haft_from_grip_point": round(float((tip - haft_centre) @ axis_direction), 4),
            "tip_position_in_hand_frame": [round(float((tip - c.palm_centre) @ v), 4) for v in (c.fingers_forward, c.closing, c.normal)],
        }
    thumb_tip_pts = results["Thumb"]["skin"][tip_of("Thumb")]
    thumb_tip = thumb_tip_pts.mean(axis=0) if len(thumb_tip_pts) else results["Thumb"]["joints"][3]
    finger_tips_mean = [np.mean(results[f]["skin"][tip_of(f)], axis=0) for f in FOUR if (tip_of(f)).any()]
    middle_segments = np.concatenate([results[f]["skin"][finger_level[f] == 1] for f in ("Index", "Middle")])
    grip_numbers["thumb_opposition_degrees_from_fingers_side"] = round(G.opposite_sides(finger_tips_mean, thumb_tip, haft_centre, axis_direction), 1)
    grip_numbers["thumb_tip_to_index_middle_middle_segments"] = round(float(np.linalg.norm(thumb_tip_pts[:, None, :] - middle_segments[None, :, :], axis=2).min()), 4) if len(thumb_tip_pts) else None
    grip_numbers["palm_pad_gap_to_haft"] = round(float(G.signed_gaps(c.palm_skin, haft_centre, axis_direction, radius).min()), 4) if len(c.palm_skin) else None
    c.report["grip"] = grip_numbers
    c.report["weapon_placement"] = {"scale": round(c.scale, 4), "haft_radius": round(radius, 4), "grip_share": args.grip, "length_ratio": args.length_ratio,
                                    "haft_centre": np.round(haft_centre, 4).tolist(), "head_direction": np.round(c.head_dir, 3).tolist(), "roll_degrees": args.roll,
                                    "diagonal_from_closing_axis_degrees": round(float(np.degrees(np.arccos(abs(float(axis_direction @ c.closing))))), 1),
                                    "start_on_little_finger_side": c.best_l0, "end_in_web": c.best_mu, "depth_offset": c.best_delta, "fit_cost": round(c.fit_cost, 4),
                                    "search_best_three": [{"cost": round(k, 4), "l0": a, "mu": m, "delta": d, "back": b} for k, a, m, d, b in c.candidates[:3]]}


def pose_and_bake_fingers(c):
    """Close the fingers, bake the fist into the body's rest shape, put the finger bones back to rest and drop their channels from the clips."""

    arm, body, hand = c.arm, c.body, c.hand
    curl = {}
    for finger in FINGERS:
        names = finger_names(hand, finger)
        result = c.results[finger]
        for i in range(3):
            if abs(result["angles"][i]) > 1e-9:
                set_pose_matrix(arm, names[i], result["axes"][i], result["angles"][i], np.array(arm.matrix_world @ arm.pose.bones[names[i]].head))
        curl[finger] = {"angles_degrees": [round(math.degrees(a), 1) for a in result["angles"]], "stopped_by": result["why"]}
    c.report["curl"] = curl
    posed = evaluated_coords(body)
    moved = np.linalg.norm(posed - c.rest_coords, axis=1)
    c.report["baked"] = {"vertices_moved": int((moved > 1e-6).sum()), "largest_move": round(float(moved.max()), 4)}
    inverse = np.linalg.inv(np.array(body.matrix_world))
    body.data.vertices.foreach_set("co", (posed @ inverse[:3, :3].T + inverse[:3, 3]).ravel())
    body.data.update()
    for finger in FINGERS:
        for name in finger_names(hand, finger):
            arm.pose.bones[name].rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()
    c.report["baked"]["rest_after_reset_matches"] = bool(np.abs(evaluated_coords(body) - posed).max() < 1e-5)
    # finger channels leave the clips: the clips pose the fingers, the fist is the rest shape
    dropped = 0
    drop_names = {n for finger in FINGERS for n in finger_names(hand, finger)}
    for action in bpy.data.actions:
        for fcurve, container in action_fcurves(action):
            bone = fcurve.data_path.split('"')[1] if fcurve.data_path.startswith("pose.bones[") else None
            if bone in drop_names:
                container.remove(fcurve)
                dropped += 1
    c.report["finger_channels_dropped"] = dropped


def add_weapon_bone(c, name):
    """The weapon's own bone, a child of the hand at the grip point, so a clip can let it go."""

    arm = c.arm
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    edit_bone = arm.data.edit_bones.new(name)
    inverse_arm = np.linalg.inv(np.array(arm.matrix_world))
    head_local = inverse_arm[:3, :3] @ c.haft_centre + inverse_arm[:3, 3]
    tail_local = inverse_arm[:3, :3] @ (c.haft_centre + c.head_dir * 0.08 * c.height) + inverse_arm[:3, 3]
    edit_bone.head, edit_bone.tail = Vector(head_local), Vector(tail_local)
    edit_bone.parent = arm.data.edit_bones[PREFIX + c.hand]
    edit_bone.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.pose.bones[name].rotation_mode = "QUATERNION"
    bpy.context.view_layer.update()


def bind_weapon(c):
    """Place the weapon in the closed hand and bind it rigidly to the hand (or to its own bone)."""

    arm, body, weapon, hand = c.arm, c.body, c.weapon, c.hand
    if abs(float(arm.matrix_world.to_scale()[0]) - 1.0) > 1e-4:
        raise SystemExit("the armature object is scaled; the weapon bone keys assume unit scale")
    inverse_w = np.linalg.inv(np.array(weapon.matrix_world))
    weapon.data.vertices.foreach_set("co", (c.placed @ inverse_w[:3, :3].T + inverse_w[:3, 3]).ravel())
    weapon.data.update()
    weapon.parent = arm
    weapon.matrix_parent_inverse = arm.matrix_world.inverted()
    bind_bone = PREFIX + hand
    if c.args.weapon_bone:
        bind_bone = PREFIX + WEAPON_BONE
        add_weapon_bone(c, bind_bone)
    hand_group = weapon.vertex_groups.new(name=bind_bone)
    hand_group.add(list(range(len(weapon.data.vertices))), 1.0, "REPLACE")
    modifier = weapon.modifiers.new("Armature", "ARMATURE")
    modifier.object = arm
    weapon.name, weapon.data.name = "tripo_part_1", "tripo_part_1"
    body.name, body.data.name = "tripo_part_0", "tripo_part_0"
    # the haft's axis, carried with the hand bone: (point, direction) at rest
    c.hand_rest = np.array(arm.matrix_world @ arm.data.bones[PREFIX + hand].matrix_local)


def hold_fade_frame(c, action, drop):
    """The frame by which the arm hold has faded out in a clip that fades it.

    A clip that lets go of the weapon (`drop`) fades it by the first frame of the fall (`lib/tripo_clearance.fall_start_frame`: the pelvis
    starts to descend for good, or the hand has dropped `--release-drop` of the height, whichever comes first), which is also the frame the
    weapon is let go. A fade clip that only holds the weapon up fades it by the frame the hand starts to rise (5% of the height).
    """

    arm, scene, hand, height, args = c.arm, c.scene, c.hand, c.height, c.args
    f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
    use_action(arm, action)
    if drop:
        pelvis, hand_height = [], []
        for frame in range(f0, f1 + 1):
            scene.frame_set(frame)
            pelvis.append(float((arm.matrix_world @ arm.pose.bones[PREFIX + "Hips"].head).z))
            hand_height.append(float((arm.matrix_world @ arm.pose.bones[PREFIX + hand].head).z))
        fall = f0 + CL.fall_start_frame(pelvis, hand_height, height, args.release_drop)
        scene.frame_set(f0)
        return min(max(fall, f0 + 6), f1 - 7)
    scene.frame_set(f0)
    start_z = float((arm.matrix_world @ arm.pose.bones[PREFIX + hand].head).z)
    fade_to = f0 + 12
    for frame in range(f0, f1 + 1):
        scene.frame_set(frame)
        if float((arm.matrix_world @ arm.pose.bones[PREFIX + hand].head).z) > start_z + 0.05 * height:
            fade_to = max(frame, f0 + 6)
            break
    scene.frame_set(f0)
    return fade_to


def multiply_hold_into_keys(arm, action, offsets, fade_to):
    """Multiply each bone's hold offset into every key of its rotation channels, fading it out by `fade_to` when given."""

    f0 = int(action.frame_range[0])
    for bone, q_off in offsets.items():
        curves = {}
        for fcurve, _c in action_fcurves(action):
            if fcurve.data_path == f'pose.bones["{bone}"].rotation_quaternion':
                curves[fcurve.array_index] = fcurve
        if len(curves) != 4:
            raise SystemExit(f"{action.name}: {bone} has {len(curves)} rotation channels, expected 4")
        frames = [kp.co.x for kp in curves[0].keyframe_points]
        previous = None
        for index, frame in enumerate(frames):
            q_old = Quaternion([curves[i].keyframe_points[index].co.y for i in range(4)])
            weight = 1.0
            if fade_to is not None:
                t = min(max((frame - f0) / max(fade_to - f0, 1), 0.0), 1.0)
                weight = 1.0 - t * t * (3.0 - 2.0 * t)
            q_new = q_old @ (Quaternion().slerp(q_off, weight) if weight < 1.0 else q_off)
            if previous is not None and q_new.dot(previous) < 0:
                q_new.negate()
            previous = q_new
            for i in range(4):
                curves[i].keyframe_points[index].co.y = q_new[i]
                curves[i].keyframe_points[index].handle_left.y = q_new[i]
                curves[i].keyframe_points[index].handle_right.y = q_new[i]
        for fcurve in curves.values():
            fcurve.update()


def haft_now(c):
    """The haft's grip point and direction now: carried by the hand bone from rest."""

    pb = c.arm.pose.bones[PREFIX + c.hand]
    m = np.array(c.arm.matrix_world @ pb.matrix) @ np.linalg.inv(c.hand_rest)
    return m[:3, :3] @ c.haft_centre + m[:3, 3], m[:3, :3] @ c.head_dir


def solve_clip_hold(c, name, fade_clips, drop_clips):
    """Find the constant offsets of the weapon arm that hold the haft up in clip `name`, and multiply them into its keys."""

    arm, scene, height = c.arm, c.scene, c.height
    action = bpy.data.actions[name]
    use_action(arm, action)
    f0 = int(action.frame_range[0])
    scene.frame_set(f0)
    arm_bones = c.arm_bones
    base_q = {b: Quaternion(arm.pose.bones[b].rotation_quaternion) for b in arm_bones}
    fade_to = None
    if name in fade_clips or name in drop_clips:
        fade_to = hold_fade_frame(c, action, name in drop_clips)
    before_point, before_dir = haft_now(c)
    arm_inside_before = torso_inside_share(c.body, c.groups, c.arm_family, evaluated_coords(c.body))

    def forward_kinematics(params):
        for k, bone in enumerate(arm_bones):
            rv = params[3 * k : 3 * k + 3] * ARM_SCALES[k]
            angle = float(np.linalg.norm(rv))
            q_off = Quaternion(Vector(rv / angle), angle) if angle > 1e-9 else Quaternion()
            arm.pose.bones[bone].rotation_quaternion = base_q[bone] @ q_off
        bpy.context.view_layer.update()
        return haft_now(c)

    starts = [np.zeros(12)]
    for roll in (np.pi / 2, np.pi, -np.pi / 2):
        guess = np.zeros(12)
        guess[7] = roll  # the forearm's own axis (bone Y)
        starts.append(guess)
    solved = G.solve_hold(forward_kinematics, starts, c.hold_target, c.hold_axis, scale=height, ridge=0.01)
    params = solved["params"]
    offsets = {}
    for k, bone in enumerate(arm_bones):
        rv = params[3 * k : 3 * k + 3] * ARM_SCALES[k]
        angle = float(np.linalg.norm(rv))
        offsets[bone] = Quaternion(Vector(rv / angle), angle) if angle > 1e-9 else Quaternion()
    multiply_hold_into_keys(arm, action, offsets, fade_to)
    use_action(arm, action)
    scene.frame_set(f0)
    after_point, after_dir = haft_now(c)
    arm_inside_after = torso_inside_share(c.body, c.groups, c.arm_family, evaluated_coords(c.body))
    target_axis = c.hold_axis
    return {
        "grip_point_before": np.round(before_point, 3).tolist(), "grip_point_after": np.round(after_point, 3).tolist(),
        "haft_up_before_degrees": round(float(np.degrees(np.arccos(np.clip(G.unit(before_dir) @ target_axis, -1, 1)))), 1),
        "haft_up_after_degrees": round(float(np.degrees(np.arccos(np.clip(G.unit(after_dir) @ target_axis, -1, 1)))), 1),
        "position_error": round(float(np.linalg.norm(after_point - c.hold_target)), 4),
        "offsets_degrees": {b.replace(PREFIX, ""): round(math.degrees(q.angle), 1) for b, q in offsets.items()},
        "arm_inside_torso_share_before": round(arm_inside_before, 4), "arm_inside_torso_share_after": round(arm_inside_after, 4),
        "faded_out_by_frame": fade_to,
    }


def hold_arm(c):
    """The arm hold: in the clips named in `--hold-clips` the weapon arm gets a constant rotation that puts the grip point at `--hold-hand`."""

    args, arm, hand, height = c.args, c.arm, c.hand, c.height
    action_names = [a.name for a in bpy.data.actions]
    c.action_names = action_names
    c.fade_clips = [resolve_clip_name(n, action_names) for n in args.hold_fade_clips.split(",") if n]
    c.drop_clips = [resolve_clip_name(n, action_names) for n in args.release_clips.split(",") if n]
    hold_clips = [resolve_clip_name(n, action_names) for n in args.hold_clips.split(",") if n] + c.fade_clips + c.drop_clips
    out_f, fwd_f, up_f = (float(v) for v in args.hold_hand.split(","))
    side = -1.0 if "Right" in hand else 1.0
    hips_y = float(rest_head(arm, PREFIX + "Hips")[1])
    c.hold_target = np.array([c.centre_x + side * out_f * height, hips_y - fwd_f * height, c.ground + up_f * height])
    c.hold_axis = np.array([float(v) for v in args.hold_axis.split(",")])
    c.arm_bones = [PREFIX + hand.replace("Hand", part) for part in ("Shoulder", "Arm", "ForeArm")] + [PREFIX + hand]
    arm_groups = [PREFIX + hand.replace("Hand", "Arm"), PREFIX + hand.replace("Hand", "ForeArm"), PREFIX + hand]
    c.arm_family = [n for n in {g for g in c.groups} if n in arm_groups or n.startswith(PREFIX + hand)]
    hold = {"target_position": np.round(c.hold_target, 3).tolist(), "target_axis": c.hold_axis.tolist(), "clips": {}}
    for name in hold_clips:
        hold["clips"][name] = solve_clip_hold(c, name, c.fade_clips, c.drop_clips)
    c.report["hold"] = hold
    c.hold = hold


def soft_cloth_mask(c):
    """The vertices of the body that hang as a cloak (the region TRIPO-CLOAK-STRETCH measures), or None when the body has none.

    The unit's chain stage later gives the cloak its own bones, and the cloak then swings a few percent of the height off the rigid pose the
    clearance sees. Judged on the rigid pose alone the weapon clears the cloak by the margin only and the swing carries cloth through it
    (TRIPO-WEAPON-IN-BODY on the exported retreat). The same rule applies to every body, caped or not: a body with no such region has no mask."""

    from lib import tripo_chains

    if c.args.soft_share <= 0:
        return None
    arm, names = c.arm, [name[len(PREFIX):] if name.startswith(PREFIX) else name for name in dominant_groups(c.body)]
    heads = {n: rest_head(arm, PREFIX + n) for n in ("Hips", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase")}
    front = (heads["LeftToeBase"] - heads["LeftFoot"]) + (heads["RightToeBase"] - heads["RightFoot"])
    front[2] = 0.0
    mask = tripo_chains.cloak_mask(c.rest_coords, names, heads["Hips"], front, np.array([0.0, 0.0, 1.0]), c.height)
    if mask.sum() < 50:
        mask = np.zeros(len(names), bool)
    # The head and the feet are kept as clear as the cloak: a fresh review of the round 4 orc saw the axe haft lie across the crown in the
    # attack's wind-up and its butt end go into the boot in the defend, while both stayed under the in-body check's 1% depth.
    keep = np.isin(np.asarray(names), KEEP_CLEAR_BONES)
    c.report["soft_cloth"] = {"vertices": int(mask.sum()), "head_and_feet": int(keep.sum()), "share_of_height": c.args.soft_share}
    mask = mask | keep
    return mask if mask.any() else None


def clear_weapon_from_body(c):
    """The clearance rule: turn the hand about the wrist, frame by frame, until the weapon leaves the body (lib/tripo_clearance.py).

    A general rule for every armed unit: a frame in which more than 0.25% of the weapon's free points are deeper than 1% of the height inside
    the body gets the smallest rotation of the hand about the wrist joint (cap 60 degrees) that clears it, smoothed over time. Frames from
    the release of a release clip on are left to the fall. A frame that cannot be cleared inside the cap is reported and the run exits 3 after
    writing its files (--clearance-allow-fail to go on): the clip then fails TRIPO-WEAPON-IN-BODY, loudly.
    """

    args, arm, scene, height, weapon, body = c.args, c.arm, c.scene, c.height, c.weapon, c.body
    clearance = {}
    hand_name = PREFIX + c.hand
    triangles = body_triangles(body)
    soft = None if args.no_clearance else soft_cloth_mask(c)
    if not args.no_clearance:
        wanted = [resolve_clip_name(n, c.action_names) for n in args.clearance_clips.split(",") if n]
        for action in [a for a in bpy.data.actions if not wanted or a.name in wanted]:
            use_action(arm, action)
            first, last = int(action.frame_range[0]), int(action.frame_range[1])
            frames_list = list(range(first, last + 1))
            body_frames, weapon_frames, pivots = [], [], []
            for frame in frames_list:
                scene.frame_set(frame)
                body_frames.append(evaluated_coords(body))
                weapon_frames.append(evaluated_coords(weapon))
                pivots.append(np.array(arm.matrix_world @ arm.pose.bones[hand_name].head))
            skip = None
            if action.name in c.drop_clips:
                skip = int(c.hold["clips"].get(action.name, {}).get("faded_out_by_frame") or last + 1) - first
            result = CL.clear_clip(weapon_frames, pivots, body_frames, triangles, height, skip_from=skip, rest_weapon=c.placed, rest_grip=c.haft_centre,
                                soft=soft, soft_share=args.soft_share)
            for index, frame in enumerate(frames_list):
                vector = result["rotvecs"][index]
                angle = float(np.linalg.norm(vector))
                if angle < 1e-6:
                    continue
                scene.frame_set(frame)
                set_pose_matrix(arm, hand_name, vector / angle, angle, pivots[index])
                arm.pose.bones[hand_name].keyframe_insert("rotation_quaternion", frame=frame)
            clearance[action.name] = {
                "frames": len(frames_list), "frames_changed": result["frames_changed"], "max_degrees": round(result["max_degrees"], 1),
                "worst_share_before": round(max(result["before"]), 4), "worst_share_after": round(max(result["after"]), 4),
                "worst_share_with_soft_cloth_after": round(max(result["soft_after"]), 4),
                "failed_frames": [frames_list[i] for i in result["failed"]], "released_from_frame": None if skip is None else first + skip,
            }
    c.report["clearance"] = clearance
    c.clearance_failed = {name: row["failed_frames"] for name, row in clearance.items() if row["failed_frames"]}


def attached_and_body(c, action):
    """Per frame of `action`: the hand's motion (the matrix that carries a rest point to where the hand holds it) and the body's posed vertices."""

    arm, scene, body = c.arm, c.scene, c.body
    use_action(arm, action)
    f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
    inverse = np.linalg.inv(c.hand_rest)
    attached, body_frames = [], []
    for frame in range(f0, f1 + 1):
        scene.frame_set(frame)
        attached.append(np.array(arm.matrix_world @ arm.pose.bones[PREFIX + c.hand].matrix) @ inverse)
        body_frames.append(evaluated_coords(body))
    return f0, f1, np.array(attached), body_frames


SUBFRAMES = 4  # keys per frame from the release on: the export samples at 30 fps between 24 fps keys, and the hand turns fast in a fall


def ease_clip(c, action):
    """Ease a clip's fast turns the way the unit's intake does (`prepare_tripo_unit`, `--ease-snaps`), so the pose judged here is the exported one."""

    return normalise_rotation_keys(action, trigger_degrees=c.args.ease_snaps, target_degrees=0.75 * c.args.ease_snaps)


def smooth_rotation_keys(action):
    """Rotation keys of the clip interpolate as the retarget's keys do (Bezier with automatic clamped handles), not linearly as the glTF import
    leaves them, so the hand the weapon is planned against is the hand the exported clip has between keys."""

    for fcurve, _container in action_fcurves(action):
        if fcurve.data_path.endswith(".rotation_quaternion"):
            for point in fcurve.keyframe_points:
                point.interpolation = "BEZIER"
                point.handle_left_type = point.handle_right_type = "AUTO_CLAMPED"
            fcurve.update()


def hand_motion_at(c, frame, subframe):
    """The hand's motion (the matrix that carries a rest point to where the hand holds it) at a frame and a fraction of the next."""

    c.scene.frame_set(frame, subframe=subframe)
    return np.array(c.arm.matrix_world @ c.arm.pose.bones[PREFIX + c.hand].matrix) @ np.linalg.inv(c.hand_rest)


def plan_pose_at(plan, step, fraction):
    """The planned weapon rotation (3x3) and grip-centre position between planned frames `step` and `step + 1`."""

    last = len(plan["turns"]) - 1
    if fraction == 0.0 or step >= last:
        return plan["turns"][min(step, last)], plan["points"][min(step, last)]
    a, b = Matrix(plan["turns"][step].tolist()).to_quaternion(), Matrix(plan["turns"][step + 1].tolist()).to_quaternion()
    turn = np.array(a.slerp(b, fraction).to_matrix())
    return turn, plan["points"][step] * (1.0 - fraction) + plan["points"][step + 1] * fraction


def key_weapon_pose(c, action, f0, plan, lifts):
    """Key the weapon bone from the release on, `SUBFRAMES` times a frame: the pose that holds the weapon on its world path while the hand
    moves on (the hand's motion lifted by the grounding step, the planned path interpolated between planned frames)."""

    arm = c.arm
    bone = PREFIX + WEAPON_BONE
    bone_rest = np.array(arm.matrix_world @ arm.data.bones[bone].matrix_local)
    pb = arm.pose.bones[bone]
    pb.rotation_mode = "QUATERNION"
    release, count = plan["release"], len(lifts)
    moments = [(0, 0.0)] + [(index, k / SUBFRAMES) for index in range(max(release - 1, 0), count) for k in range(SUBFRAMES) if index < count - 1 or k == 0]
    previous = None
    for index, fraction in dict.fromkeys(moments):
        if index < release:
            quaternion, location = Quaternion(), Vector((0.0, 0.0, 0.0))
        else:
            hand = hand_motion_at(c, f0 + index, fraction)
            hand[2, 3] += lifts[index] * (1.0 - fraction) + lifts[min(index + 1, count - 1)] * fraction
            turn, point = plan_pose_at(plan, index - release, fraction)
            basis = CL.local_pose(hand, turn, point, c.haft_centre, bone_rest)
            quaternion, location = Matrix(basis[:3, :3].tolist()).to_quaternion(), Vector(basis[:3, 3].tolist())
        if previous is not None and quaternion.dot(previous) < 0:
            quaternion.negate()
        previous = quaternion
        pb.rotation_quaternion, pb.location = quaternion, location
        pb.keyframe_insert("rotation_quaternion", frame=f0 + index + fraction)
        pb.keyframe_insert("location", frame=f0 + index + fraction)
    pb.rotation_quaternion, pb.location = Quaternion(), Vector((0.0, 0.0, 0.0))
    use_action(arm, action)


def steady_weapon(c, action, f0, release, tumble, lifts):
    """After the intake-style easing of the turns, put the weapon back where the plan has it: from the landing on, its centre goes back to where
    it landed, and in every frame from the release its lowest point goes up to the ground if it is under it. Only location keys move (the intake
    does not ease those). Returns the largest correction made, a share of the height."""

    arm, scene, weapon, height = c.arm, c.scene, c.weapon, c.height
    use_action(arm, action)
    pb = arm.pose.bones[PREFIX + WEAPON_BONE]
    bone_rest = np.array(arm.matrix_world @ arm.data.bones[PREFIX + WEAPON_BONE].matrix_local)[:3, :3]
    count, largest, landed_centre = len(lifts), 0.0, None
    for index in range(release, count):
        for fraction in ((k / SUBFRAMES for k in range(SUBFRAMES)) if index < count - 1 else (0.0,)):
            scene.frame_set(f0 + index, subframe=fraction)
            lift = lifts[index] * (1.0 - fraction) + lifts[min(index + 1, count - 1)] * fraction
            points = evaluated_coords(weapon) + np.array([0.0, 0.0, lift])
            shift = np.zeros(3)
            if index >= release + tumble:
                centre = points.mean(axis=0)
                landed_centre = centre if landed_centre is None else landed_centre
                shift = landed_centre - centre
            low = float(points[:, 2].min()) + shift[2]
            if low < 0.0:
                shift[2] -= low - 0.0005 * height
            if float(np.linalg.norm(shift)) <= 0.0005 * height:
                continue
            hand = hand_motion_at(c, f0 + index, fraction)[:3, :3]
            pb.location = Vector(pb.location) + Vector((np.linalg.inv(hand @ bone_rest) @ shift).tolist())
            pb.keyframe_insert("location", frame=f0 + index + fraction)
            largest = max(largest, float(np.linalg.norm(shift)) / height)
    pb.location = Vector((0.0, 0.0, 0.0))
    use_action(arm, action)
    return round(largest, 4)


def measure_drop(c, action, f0, release, tumble, lifts):
    """The weapon as the exported frames put it, after the grounding lift of each frame: its lowest point over the ground and how far it moves
    after it has landed (shares of the height)."""

    arm, scene, weapon, height = c.arm, c.scene, c.weapon, c.height
    use_action(arm, action)
    f1 = int(action.frame_range[1])
    low, resting = np.inf, []
    for frame in range(f0 + release, f1 + 1):
        scene.frame_set(frame)
        points = evaluated_coords(weapon) + np.array([0.0, 0.0, lifts[frame - f0]])
        low = min(low, float(points[:, 2].min()))
        if frame >= f0 + release + tumble:
            resting.append(points[:: max(1, len(points) // 400)])
    moved = max((float(np.linalg.norm(p - resting[0], axis=1).max()) for p in resting), default=0.0)
    scene.frame_set(f0)
    return {"lowest_point_over_ground_share": round(low / height, 4), "moved_after_landing_share": round(moved / height, 4)}


def grounding_lifts(body_frames):
    """How far the pipeline's grounding step lifts the unit in each frame: it moves the root so the body's lowest point is on the ground (z = 0),
    weapon left out, in every frame (adapter/blender_worker.correct_action_grounding). The weapon bone is planned in that grounded world."""

    return np.array([-float(frame[:, 2].min()) for frame in body_frames])


def drop_weapon(c, action):
    """Let the weapon go in `action`: the hand drops it at the first frame of the fall and it lands flat on the ground clear of the body.

    The rule is in `lib/tripo_clearance.plan_drop`: the resting place is chosen from the body's final pose and everything the body occupies
    after the landing, the weapon tumbles to it in `TUMBLE_SECONDS` under gravity and then stays exactly where it is while the hand and the
    body fall on. The weapon bone is keyed with rotation and location in every frame from the release. The pipeline lifts each frame so the
    body's lowest point is on the ground (`grounding_lifts`), and lifts the weapon with it: the plan is made in that grounded world, so the
    weapon ends on the ground there and not on the body's own, lower, ground.
    """

    fps = c.scene.render.fps / c.scene.render.fps_base
    smooth_rotation_keys(action)
    f0, f1, attached, body_frames = attached_and_body(c, action)
    lifts = grounding_lifts(body_frames)
    attached = attached.copy()
    attached[:, 2, 3] += lifts
    grounded = [frame + np.array([0.0, 0.0, lift]) for frame, lift in zip(body_frames, lifts)]
    release = int(c.hold["clips"][action.name]["faded_out_by_frame"]) - f0
    axes = np.stack([c.head_dir, c.blade, c.third], axis=1)
    plan = CL.plan_drop(c.placed, c.haft_centre, axes, attached, grounded, body_triangles(c.body), c.height, 0.0, release, fps)
    key_weapon_pose(c, action, f0, plan, lifts)
    c.report.setdefault("drop_ease", {})[action.name] = ease_clip(c, action)  # the intake eases the weapon's turns too
    lifted = steady_weapon(c, action, f0, release, plan["tumble_frames"], lifts)
    measured = measure_drop(c, action, f0, release, plan["tumble_frames"], lifts)
    return {
        "release_frame": f0 + release, "tumble_frames": plan["tumble_frames"], "landing_grip_point": np.round(plan["land_point"], 3).tolist(),
        "landing_clearance_from_body_share": round(plan["clearance_share"], 4), "planned_weapon_inside_body_share": round(plan["in_body_share"], 4),
        "planned_weapon_inside_body_frame": f0 + plan["in_body_frame"], "planned_lowest_point_over_ground_share": round(plan["lowest_over_ground_share"], 4),
        "grounding_lift_share_first_last": [round(float(lifts[0]) / c.height, 4), round(float(lifts[-1]) / c.height, 4)],
        "measured": measured, "largest_correction_after_easing_share": lifted, "frames": f1 - f0 + 1,
    }


def release_clips(c):
    """The weapon lets go: the fall of the weapon bone in the release clips."""

    release = {}
    for name in c.drop_clips:
        if not c.args.weapon_bone:
            raise SystemExit("--release-clips needs --weapon-bone")
        release[name] = drop_weapon(c, bpy.data.actions[name])
    c.release = release
    c.report["release"] = release


def check_fingers(c):
    """The checks: fingers on the haft, on sampled frames of every clip that keeps the weapon in the hand."""

    arm, scene, body = c.arm, c.scene, c.body
    zone = 4.0 * c.radius
    gaps = {}
    for action in bpy.data.actions:
        if action.name in c.release:
            continue  # the weapon has let go of the hand
        use_action(arm, action)
        f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
        worst = {f: {"deepest": 1.0, "tip_gap": 0.0} for f in FINGERS}
        for frame in np.linspace(f0, f1, c.args.check_frames).round().astype(int):
            scene.frame_set(int(frame))
            coords = evaluated_coords(body)
            point, direction = haft_now(c)
            per_finger = G.finger_gaps({f: coords[c.finger_index[f]] for f in FINGERS},
                                       {f: coords[c.finger_index[f][c.finger_tip[f]]] for f in FINGERS}, point, direction, c.radius, zone)
            for f, row in per_finger.items():
                if row["deepest"] is not None:
                    worst[f]["deepest"] = min(worst[f]["deepest"], row["deepest"])
                    worst[f]["tip_gap"] = max(worst[f]["tip_gap"], row["tip_gap"])
        gaps[action.name] = {f: {k: (round(v, 4) if v is not None else None) for k, v in row.items()} for f, row in worst.items()}
    c.report["fingers_on_haft"] = {"zone": round(zone, 4), "haft_radius": round(c.radius, 4), "per_clip_worst": gaps}


def export_glb(c):
    """Write the GLB with every clip and the report."""

    args, arm = c.args, c.arm
    for action in bpy.data.actions:
        action.use_fake_user = True
    use_action(arm, bpy.data.actions[0])
    bpy.ops.object.select_all(action="DESELECT")
    for obj in (arm, c.body, c.weapon):
        obj.select_set(True)
    bpy.context.view_layer.objects.active = arm
    args.out.parent.mkdir(parents=True, exist_ok=True)
    properties = bpy.ops.export_scene.gltf.get_rna_type().properties
    options = {"filepath": str(args.out), "export_format": "GLB", "use_selection": True, "export_skins": True, "export_animations": True,
               "export_animation_mode": "ACTIONS", "export_image_format": "AUTO"}
    bpy.ops.export_scene.gltf(**{k: v for k, v in options.items() if k in properties})
    c.report["exported_clips"] = sorted(a.name for a in bpy.data.actions)
    print(json.dumps(c.report, sort_keys=True))
    if args.report:
        args.report.write_text(json.dumps(c.report, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def drop_failures(c):
    """Release clips whose plan or measured result breaks a rule: the weapon inside the body or under the ground.

    How far the weapon moves after it landed is only a diagnostic here (`report["release"][clip]["diagnostics"]`). This stage measures the GLB
    with the lifts of the grip stage's own body frames, and the unit's export measures differently (the retarget, the easing and the pipeline's
    grounding of each frame): the GLB said 11.9% while the exported death moved under 1% outside a few frames of the body settling. The
    judge of a dropped weapon's stillness is the check on the exported files (`tripo_checks.py` reports `moved_in_last_half_share`)."""

    failures = {}
    for name, row in c.release.items():
        problems, diagnostics = CL.drop_problems(row)
        for text in diagnostics:
            row.setdefault("diagnostics", []).append(text)
            print(f"diagnostic (grip stage GLB): {name}: {text}")
        if problems:
            failures[name] = problems
    return failures


def main():
    args = parse_args()
    c = SimpleNamespace(args=args, hand=args.hand, report={"tool": "grip_weapon", "body": args.body.name, "weapon": args.weapon.name, "hand": args.hand})
    load_body(c)
    find_hand_frame(c)
    find_finger_skins(c)
    load_weapon(c)
    search_grip(c)
    close_thumb(c)
    describe_grip(c)
    pose_and_bake_fingers(c)
    bind_weapon(c)
    hold_arm(c)
    # quaternion keys (before the fall of the weapon, which is keyed against the final motion of the hand): one hemisphere per bone
    # (a flip makes Blender turn the long way), and the biggest steps
    c.report["rotation_keys"] = {action.name: ease_clip(c, action) for action in bpy.data.actions}
    clear_weapon_from_body(c)
    c.report["rotation_keys_after_clearance"] = {action.name: ease_clip(c, action) for action in bpy.data.actions}  # its hand turns are eased too
    release_clips(c)
    check_fingers(c)
    dropped = drop_failures(c)
    export_glb(c)
    failed = c.clearance_failed
    if (failed or dropped) and not args.clearance_allow_fail:
        if failed:
            print("CLEARANCE_FAILED " + json.dumps(failed), file=sys.stderr)
        if dropped:
            print("DROP_FAILED " + json.dumps(dropped), file=sys.stderr)
        raise SystemExit(3)


try:
    main()
except SystemExit as failure:
    import os

    if failure.code not in (None, 0):
        sys.stdout.flush()
        print(f"grip_weapon failed: {failure.code}", file=sys.stderr)
        sys.stderr.flush()
        os._exit(1)
    raise
