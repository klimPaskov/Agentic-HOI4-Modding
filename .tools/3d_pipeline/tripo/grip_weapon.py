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

5. The death rule (`--release-clips CLIP`, one scripted rule, no per-unit tuning). In a release clip the weapon stays
   in the hand, held up like in the other clips (the hold fades out as the hand falls), until the frame the hand
   has dropped `--release-drop` (default 0.04) of the body height below its first-frame height. Then the weapon bone
   turns about a pivot to a resting place the kit computes: haft level, blade flat, on the ground (lowest point
   0.3% of the height above the body's lowest vertex), clear of the body by at least 1% of the height, on the
   side and at the angle whose fall (12, 18 or 26 frames eased, started 0, 4 or 8 frames after the release)
   stays highest over the ground. A turn is all the kit's animation import keeps of a bone, so the pivot is
   solved (`lib/tripo_grip.pivot_for_motion`). The job names the clip with `tripo.weapon.release_roles` and
   check_unit_files.py then excuses a part bound wholly to that weapon bone from the drift test only. If the
   rule does not pass the checks, leave `release_roles` out: the weapon then stays in the hand through the fall.

The result has the shape of Tripo's in-hand export, so `prepare_tripo_unit.py --rigid-part tripo_part_1=RightHand`
takes it unchanged.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import tripo_clearance as CL  # noqa: E402
from lib import tripo_grip as G  # noqa: E402
from lib.tripo import resolve_clip_name  # noqa: E402
import assemble_separate as A  # noqa: E402
import clip_check as cc  # noqa: E402

FINGERS = ("Index", "Middle", "Ring", "Pinky", "Thumb")
PREFIX = "mixamorig:"


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
    parser.add_argument("--release-drop", type=float, default=0.04, help="a release clip lets go of the weapon when the hand has dropped this share of the body height below its first-frame height")
    parser.add_argument("--release-ease-frames", type=int, default=18, help="(kept for old commands; the fall length is chosen from 12, 18 and 26 frames)")
    parser.add_argument("--dump-grip", type=Path, default=None, help="save the hand geometry the grip search works on (an .npz) for offline work")
    parser.add_argument("--diagonal-min", type=float, default=28.0, help="least angle (degrees) of the haft to the palm closing axis")
    parser.add_argument("--diagonal-max", type=float, default=55.0)
    parser.add_argument("--clearance-clips", default="", help="the clips the clearance rule works on (names or starts of names, comma separated); default every clip. Name the clips the unit uses: each frame that fails costs seconds")
    parser.add_argument("--no-clearance", action="store_true", help="skip the clearance rule (see lib/tripo_clearance.py): by default every clip is checked per frame and the hand is turned about the wrist until the weapon leaves the body")
    parser.add_argument("--clearance-allow-fail", action="store_true", help="exit 0 even when a frame cannot be cleared within the cap (the report and TRIPO-WEAPON-IN-BODY still say so)")
    parser.add_argument("--weapon-bone", action="store_true", help="bind the weapon to its own bone (child of the hand) instead of the hand bone")
    parser.add_argument("--hold-hand", default="0.257,0.07,0.61", help="out, forward, up of the grip point, as shares of the body height")
    parser.add_argument("--hold-axis", default="0,0,1")
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

        def rates(values):
            return [step_degrees(values[k - 1], values[k]) / max(frames[k] - frames[k - 1], 1e-6) for k in range(1, len(values))]

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


def rotation_z(angle):
    c, sn = math.cos(angle), math.sin(angle)
    return np.array([[c, -sn, 0.0], [sn, c, 0.0], [0.0, 0.0, 1.0]])


def release_weapon(arm, body, bone, hand, action, placed, centre, head_dir, blade, third, hand_rest, height, ease_frames, release_at=None):
    """Let the weapon go in `action`: it turns about a pivot in the hand's frame and ends lying flat on the ground.

    The kit's animation import drops the location keys of every bone but the root, so the weapon bone can only
    turn. A turn about a pivot far enough from the weapon carries it a long way, so: the place the weapon should
    end in (lying flat, haft level, blade flat, beside the body, touching the ground) is searched, the pivot
    and axis of the turn that carry the weapon from the hand to that place are solved for
    (`lib.tripo_grip.pivot_for_motion`), the bone is moved to the pivot with its axis along the turn, and the
    clip keys the turn: nothing until `release_at` (the frame the hand starts to fall), then an eased turn. Of
    several fall lengths and delays the one whose path stays highest above the ground is kept.
    """

    scene = bpy.context.scene
    use_action(arm, action)
    f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
    frames = list(range(f0, f1 + 1))
    hand_inverse = np.linalg.inv(hand_rest)
    attached, body_low, body_frames_all = [], [], []
    for frame in frames:
        scene.frame_set(frame)
        attached.append(np.array(arm.matrix_world @ arm.pose.bones[PREFIX + hand].matrix) @ hand_inverse)
        coords = evaluated_coords(body)
        body_low.append(float(coords[:, 2].min()))
        body_frames_all.append(coords)
        last = coords
    release = int(release_at) - f0 if release_at is not None else int(0.35 * (len(frames) - 1))
    release = max(1, min(release, len(frames) - 8))
    ground = body_low[-1] + 0.003
    a_end = attached[-1]
    r_a, t_a = a_end[:3, :3], a_end[:3, 3]
    r0 = np.stack([head_dir, blade, third], axis=1)  # rest directions of the weapon's head, blade, third axes
    offsets = placed - centre
    weapon_sample = offsets[:: max(1, len(offsets) // 150)]
    path_sample = offsets[:: max(1, len(offsets) // 120)]
    body_sample = last[:: max(1, len(last) // 1500)]
    candidates = []
    # first a place well clear of the body (4% of the height: the body goes on moving after the landing), then, failing that, 1%
    for clear_by in (0.04, 0.01):
        for fh in (1.0, -1.0):
            for b in (1.0, -1.0):
                for psi in np.linspace(0.0, 2.0 * math.pi, 36, endpoint=False):
                    basis = rotation_z(psi) @ np.stack([[fh, 0.0, 0.0], [0.0, b, 0.0], [0.0, 0.0, fh * b]], axis=1)
                    r_w = basis @ r0.T
                    r_d = r_a.T @ r_w
                    axis, angle = G.rotation_axis_angle(r_d)
                    if angle < 0.2:
                        continue
                    lying = offsets @ r_w.T
                    zc = ground - float(lying[:, 2].min())
                    u = r_a @ axis
                    norm_xy = float(np.hypot(u[0], u[1]))
                    if norm_xy < 0.05:
                        continue
                    rhs = float(u @ (r_w @ centre + t_a)) - float(u[2]) * zc
                    base_xy = rhs * u[:2] / norm_xy ** 2
                    line = np.array([-u[1], u[0]]) / norm_xy
                    sample_lying = weapon_sample @ r_w.T
                    found = None
                    for step_s in np.arange(-1.0, 1.0, 0.02):
                        cxy = base_xy + step_s * line
                        points = sample_lying + np.array([cxy[0], cxy[1], zc])
                        nearest = float(cc.nearest_vertex_distance(points, body_sample).min())
                        if nearest < clear_by * height:
                            continue
                        if found is None or nearest < found[0]:
                            found = (nearest, np.array([cxy[0], cxy[1], zc]))
                    if found is not None:
                        candidates.append((found[0], r_w, axis, angle, found[1], r_d))
        if candidates:
            break
    if not candidates:
        raise SystemExit("release_weapon: no resting place of the weapon on the ground can be reached by a turn about a pivot")
    # The body goes on moving after the weapon lands: a resting place the body later sweeps through fails the check for the rest of the clip.
    # Keep the places the body leaves alone for the frames after the landing (every third frame, about as clear as the clearest).
    rest_judged = CL.sample_points(offsets[np.linalg.norm(offsets, axis=1) > CL.GRIP_RADIUS_SHARE * height], 100)
    rest_frames = list(range(release + 6, len(frames), 3))
    all_triangles = body_triangles(body)

    def rest_penetration(candidate):
        points = rest_judged @ candidate[1].T + candidate[4]
        return max((CL.deep_share(points, body_frames_all[i], all_triangles, height) for i in rest_frames), default=0.0)

    ranked = sorted((round(rest_penetration(c), 3), k) for k, c in enumerate(candidates))
    candidates = [candidates[k] for value, k in ranked if value <= ranked[0][0] + 0.002][:40]

    def path_clearance(axis, angle, pivot, delay, ease):
        worst = 1e9
        for index in range(len(frames)):
            t = min(max((index - release - delay) / ease, 0.0), 1.0)
            smooth = t * t * (3.0 - 2.0 * t)
            r_t = G.rodrigues(axis, angle * smooth)
            moved = ((path_sample + centre - pivot) @ r_t.T + pivot) @ attached[index][:3, :3].T + attached[index][:3, 3]
            worst = min(worst, float(moved[:, 2].min()) - body_low[index])
        return worst

    # the resting place and the fall: prefer a path that never goes under the ground, then the place nearest the body
    scored = []
    for nearest, r_w, axis, angle, c_final, r_d in candidates:
        t_d = r_a.T @ (c_final - r_w @ centre - t_a)
        pivot = G.pivot_for_motion(r_d, t_d, centre)
        if pivot is None:
            continue
        for ease in (12, 18, 26):
            for delay in (0,):  # the weapon is let go at the release frame: the clearance rule judged the hand only up to it
                if release + delay + ease > len(frames) - 1:
                    continue
                clearance = path_clearance(axis, angle, pivot, delay, ease)
                scored.append((max(0.0, -0.004 - clearance), nearest, clearance, ease, delay, r_w, axis, angle, c_final, pivot))
    if not scored:
        raise SystemExit("release_weapon: no resting place has a pivot")
    scored.sort(key=lambda row: (round(row[0], 3), row[1]))
    # The fall must not cut through the body either (TRIPO-WEAPON-IN-BODY judges every frame): of the best options by ground clearance, the one
    # whose path has the smallest share of weapon points deeper than 1% of the height inside the body.
    judged = offsets[np.linalg.norm(offsets, axis=1) > CL.GRIP_RADIUS_SHARE * height]
    judged = CL.sample_points(judged, 120)
    body_triangles_all = body_triangles(body)

    def path_in_body(row):
        _p, _n, _c, ease_, delay_, _r, axis_, angle_, _cf, pivot_ = row
        worst_share = 0.0
        for index in range(release + delay_, len(frames)):
            t = min(max((index - release - delay_) / ease_, 0.0), 1.0)
            smooth_ = t * t * (3.0 - 2.0 * t)
            r_t = G.rodrigues(axis_, angle_ * smooth_)
            moved = ((judged + centre - pivot_) @ r_t.T + pivot_) @ attached[index][:3, :3].T + attached[index][:3, 3]
            worst_share = max(worst_share, CL.deep_share(moved, body_frames_all[index], body_triangles_all, height))
        return worst_share

    best_row, best_key = scored[0], None
    # only options about as clear of the ground as the best (a fall that sinks into the floor is not an answer to one that cuts the body)
    near_best = [row for row in scored if row[0] <= scored[0][0] + 0.02][:60]
    for rank, row in enumerate(near_best):
        key = (round(path_in_body(row), 3), rank)
        if best_key is None or key < best_key:
            best_key, best_row = key, row
    _pen, nearest_at_rest, clearance, ease, delay, r_w, axis, angle, c_final, pivot = best_row

    # the bone: head at the pivot, axis along the turn
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    inverse_arm = np.linalg.inv(np.array(arm.matrix_world))
    edit_bone = arm.data.edit_bones[bone]
    edit_bone.head = Vector(inverse_arm[:3, :3] @ pivot + inverse_arm[:3, 3])
    edit_bone.tail = Vector(inverse_arm[:3, :3] @ (pivot + axis * 0.08 * height) + inverse_arm[:3, 3])
    edit_bone.roll = 0.0
    bpy.ops.object.mode_set(mode="OBJECT")
    pb = arm.pose.bones[bone]
    pb.rotation_mode = "QUATERNION"
    bpy.context.view_layer.update()
    for index, frame in enumerate(frames):
        if 0 < index < release + delay - 1:
            continue
        scene.frame_set(frame)
        t = min(max((index - release - delay) / ease, 0.0), 1.0)
        smooth = t * t * (3.0 - 2.0 * t)
        pb.rotation_quaternion = Quaternion((0.0, 1.0, 0.0), angle * smooth)  # about the bone's own axis, which lies along the turn
        pb.keyframe_insert("rotation_quaternion", frame=frame)
    pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
    scene.frame_set(f1)
    tri = body_triangles(body)
    final_points = (offsets + centre - pivot) @ G.rodrigues(axis, angle).T + pivot
    final_points = final_points @ r_a.T + t_a
    sample = final_points[:: max(1, len(final_points) // 600)]
    inside = float(np.mean(cc.points_inside_mesh(sample, last[tri])))
    nearest = float(cc.nearest_vertex_distance(sample, last[:: max(1, len(last) // 3000)]).min())
    return {
        "release_frame": frames[release + delay], "fall_frames": ease, "turn_degrees": round(math.degrees(angle), 1),
        "pivot_in_rest_frame": np.round(pivot, 3).tolist(), "axis": np.round(axis, 3).tolist(),
        "rest_position_of_grip_point": np.round(c_final, 3).tolist(),
        "lowest_weapon_point_at_rest_minus_ground": round(float(final_points[:, 2].min()) - body_low[-1], 4),
        "least_clearance_over_body_lowest_during_fall": round(clearance, 4),
        "weapon_points_inside_body_at_rest_share": round(inside, 4), "nearest_to_body_at_rest": round(nearest, 4),
        "body_lowest_first_last": [round(body_low[0], 3), round(body_low[-1], 3)],
    }


def main():
    args = parse_args()
    hand = args.hand
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
    scene = bpy.context.scene
    report = {"tool": "grip_weapon", "body": args.body.name, "weapon": args.weapon.name, "hand": hand}

    rest_coords = world_array(body, mesh_coords(body))
    height = float(np.ptp(rest_coords[:, 2]))
    ground = float(rest_coords[:, 2].min())
    centre_x = float(rest_coords[:, 0].mean())
    report["body_height"] = round(height, 4)
    report["finger_rotation_in_clips_degrees"] = finger_activity(arm, hand)
    report["hand_vs_shoulder_in_clips"] = hand_positions(arm, hand)
    arm.animation_data_create()
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()

    # ---- the hand's frame -----------------------------------------------------------------------
    wrist = rest_head(arm, PREFIX + hand)
    base = {f: rest_head(arm, finger_names(hand, f)[0]) for f in FINGERS}
    closing = G.unit(base["Pinky"] - base["Index"])
    knuckles = np.mean([base[f] for f in ("Index", "Middle", "Ring", "Pinky")], axis=0)
    forward = G.unit(base["Middle"] - wrist)
    normal0 = G.unit(np.cross(closing, forward))
    palm_centre = 0.5 * (knuckles + wrist) * 0.4 + 0.6 * knuckles
    thumb_side = float((base["Thumb"] - palm_centre) @ normal0)
    normal = normal0 if thumb_side >= 0 else -normal0
    report["palm"] = {"closing_index_to_pinky": np.round(closing, 3).tolist(), "fingers_forward": np.round(forward, 3).tolist(),
                      "normal_to_palm_side": np.round(normal, 3).tolist(), "thumb_offset_along_normal": round(thumb_side, 4)}

    family = [g.name for g in body.vertex_groups if g.name.startswith(PREFIX + hand)]
    groups = dominant_groups(body)
    hand_mask = np.isin(groups, family)
    hand_points = rest_coords[hand_mask]
    # the palm itself: the vertices that follow the hand bone and no finger, near the palm (a bracer or a limb
    # that happens to be close would put the surface far out)
    own = rest_coords[groups == PREFIX + hand]
    in_plane = np.linalg.norm((own - palm_centre) - np.outer((own - palm_centre) @ normal, normal), axis=1)
    near_palm = own[in_plane < 0.06 * height]
    palm_surface = float(np.percentile((near_palm - palm_centre) @ normal, 90)) if len(near_palm) else 0.0
    report["palm"]["surface_offset"] = round(palm_surface, 4)

    # ---- each finger's skin and the bone it follows ---------------------------------------------------
    weights_by_group = {}
    for g in body.vertex_groups:
        if g.name.startswith(PREFIX + hand):
            column = np.zeros(len(body.data.vertices))
            for v in body.data.vertices:
                for item in v.groups:
                    if item.group == g.index:
                        column[v.index] = item.weight
            weights_by_group[g.name] = column
    finger_index, finger_level, finger_tip = {}, {}, {}
    for finger in FINGERS:
        names = finger_names(hand, finger)
        stack = np.array([weights_by_group.get(n, np.zeros(len(rest_coords))) for n in names])
        share = stack.sum(axis=0)
        index = np.where(share > 0.5)[0]
        # only skin near the finger's own bones: a stray vertex weighted to a finger (a bracer edge, a seam) would
        # stop the curl at the first touch and sit far from the haft in every check
        chain = np.array([rest_head(arm, n) for n in names] + [rest_tail(arm, names[3])])
        near = np.linalg.norm(rest_coords[index][:, None, :] - G.segment_points(chain, 8)[None, :, :], axis=2).min(axis=1) < 0.06 * height
        report.setdefault("finger_skin_dropped_as_stray", {})[finger] = int((~near).sum())
        index = index[near]
        stack = stack[:, index]
        finger_index[finger] = index
        finger_level[finger] = stack.argmax(axis=0)
        base_joint = rest_head(arm, names[0])
        finger_tip[finger] = int(np.argmax(np.linalg.norm(rest_coords[index] - base_joint, axis=1)))  # index into `index`

    # ---- the weapon -------------------------------------------------------------------------------
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(args.weapon))
    weapon_objects = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if len(weapon_objects) != 1:
        raise SystemExit(f"Expected one weapon mesh, found {[o.name for o in weapon_objects]}")
    weapon = weapon_objects[0]
    for obj in [o for o in bpy.data.objects if o not in before and o.type != "MESH"]:
        bpy.data.objects.remove(obj, do_unlink=True)
    w_world = world_array(weapon, mesh_coords(weapon))
    axes = A.weapon_axes(w_world, args.grip)
    scale = args.length_ratio * height / axes["length"]
    local = scale * ((w_world - axes["grip_point"]) @ axes["axes"])  # (along the haft to the head, blade, third)
    radius = G.haft_radius(local, np.zeros(3), np.array([1.0, 0.0, 0.0]), 0.0, 0.03 * args.length_ratio * height)

    # ---- a power grip: the haft lies diagonally across the palm ------------------------------------------
    # From the base of the little finger to the web between thumb and index finger. The haft is seated into the palm
    # until the palm pad touches it, all four fingers wrap round it with the curl spread over all three joints,
    # and the thumb closes from the other side and rests on the fingers. The place of the haft is searched:
    # where the line starts on the little-finger side, where it ends in the web, and how deep it sits.
    fingers_forward = G.unit(forward - (forward @ closing) * closing)
    joints_rest = {f: np.array([rest_head(arm, n) for n in finger_names(hand, f)]) for f in FINGERS}
    skin_rest = {f: rest_coords[finger_index[f]] for f in FINGERS}
    tolerance = 0.0015 * height
    four = ("Index", "Middle", "Ring", "Pinky")
    palm_skin = near_palm[(near_palm - palm_centre) @ normal > palm_surface - 0.02 * height]

    if args.dump_grip:
        arrays = {"height": height, "radius": radius, "palm_surface": palm_surface, "palm_centre": palm_centre, "normal": normal, "closing": closing,
                  "forward": forward, "wrist": wrist, "palm_skin": palm_skin, "hand_points": hand_points,
                  "near_points": rest_coords[np.linalg.norm(rest_coords - palm_centre, axis=1) < 0.15 * height],
                  "near_groups": np.array(groups)[np.linalg.norm(rest_coords - palm_centre, axis=1) < 0.15 * height]}
        for f in FINGERS:
            arrays[f"joints_{f}"], arrays[f"skin_{f}"], arrays[f"level_{f}"], arrays[f"base_{f}"] = joints_rest[f], skin_rest[f], finger_level[f], base[f]
        np.savez(args.dump_grip, **arrays)

    def haft_line(l0, mu, delta, back=0.0):
        start_point = wrist + l0 * (base["Pinky"] - wrist)
        web = base["Index"] + mu * (base["Thumb"] - base["Index"]) - back * fingers_forward
        direction = G.unit(web - start_point)
        direction = G.unit(direction - (direction @ normal) * normal)
        middle = 0.5 * (start_point + web)
        middle = middle - ((middle - palm_centre) @ normal) * normal + normal * (palm_surface + radius + delta)
        return middle, direction

    def palm_cost(point, direction):
        gap = G.signed_gaps(palm_skin, point, direction, radius)
        return 4.0 * max(float(gap.min()), 0.0) + 20.0 * max(-float(gap.min()) - 0.003 * height, 0.0) if len(gap) else 0.0

    def solve_four(point, direction, step):
        results, total = {}, 0.0
        for finger in four:
            results[finger] = G.solve_finger(joints_rest[finger], skin_rest[finger], finger_level[finger], point, direction, radius,
                                             closing, normal, tolerance, step=step)
            total += results[finger]["cost"]
        return total + palm_cost(point, direction), results

    candidates = []
    for l0 in (0.1, 0.25, 0.4, 0.55):
        for mu in (0.05, 0.2, 0.35, 0.5, 0.7):
            for delta in (-0.008, -0.004, 0.0, 0.004, 0.008):
                for back in (0.0, 0.01):
                    point, direction = haft_line(l0, mu, delta * height, back * height)
                    diagonal = float(np.degrees(np.arccos(min(abs(float(direction @ closing)), 1.0))))
                    if not (args.diagonal_min <= diagonal <= args.diagonal_max):
                        continue
                    total, _r = solve_four(point, direction, 15.0)
                    candidates.append((total, l0, mu, delta, back))
    if not candidates:
        raise SystemExit("No haft line across the palm lies between the diagonal limits; widen --diagonal-min/--diagonal-max")
    candidates.sort()
    _total, best_l0, best_mu, best_delta, best_back = candidates[0]
    haft_centre, axis_direction = haft_line(best_l0, best_mu, best_delta * height, best_back * height)
    cost, results = solve_four(haft_centre, axis_direction, 10.0)
    head_dir = axis_direction if args.head_toward == "index" else -axis_direction
    blade = G.rodrigues(head_dir, np.radians(args.roll)) @ normal
    third = np.cross(head_dir, blade)
    placed = haft_centre + local[:, 0:1] * head_dir + local[:, 1:2] * blade + local[:, 2:3] * third

    # the thumb: closes from the opposite side, round the haft and over the fingers
    obstacle_points = np.concatenate([results[f]["skin"] for f in four])
    obstacle_points = obstacle_points[:: max(1, len(obstacle_points) // 300)]
    tip_masks = {f: finger_level[f] == finger_level[f].max() for f in four}
    fingertip_side = G.unit(np.mean([G.radial_unit(results[f]["skin"][tip_masks[f]].mean(axis=0), haft_centre, axis_direction) for f in four], axis=0))
    middle_segments_posed = np.concatenate([results[f]["skin"][finger_level[f] == 1] for f in ("Index", "Middle")])
    results["Thumb"] = G.solve_thumb(joints_rest["Thumb"], skin_rest["Thumb"], finger_level["Thumb"], haft_centre, axis_direction, radius,
                                     obstacle_points, tolerance=0.003 * height, target_skin=middle_segments_posed, away_from=fingertip_side)
    for finger in FINGERS:
        results[finger]["why"] = ["fitted"] * 3

    # what the grip looks like, in numbers: for every finger the gap of its tip and its deepest skin to the haft surface
    def tip_of(finger):
        return finger_level[finger] == finger_level[finger].max()

    def radial_from_palm(point):
        return G.radial_angle(point, haft_centre, axis_direction, normal)

    grip_numbers = {}
    for finger in FINGERS:
        gap = G.signed_gaps(results[finger]["skin"], haft_centre, axis_direction, radius)
        tip_points_world = results[finger]["skin"][[i for i, lv in enumerate(finger_level[finger]) if lv == int(finger_level[finger].max())]]
        tip = tip_points_world.mean(axis=0) if len(tip_points_world) else results[finger]["joints"][3]
        grip_numbers[finger] = {
            "tip_gap_to_haft": round(float(gap[tip_of(finger)].min()) if (tip_of(finger)).any() else float("nan"), 4),
            "deepest_skin_in_haft": round(float(-gap.min()), 4),
            "angle_around_haft_from_palm_normal_degrees": round(radial_from_palm(tip), 1),
            "tip_along_haft_from_grip_point": round(float((tip - haft_centre) @ axis_direction), 4),
            "tip_position_in_hand_frame": [round(float((tip - palm_centre) @ v), 4) for v in (fingers_forward, closing, normal)],
        }
    thumb_tip_pts = results["Thumb"]["skin"][tip_of("Thumb")]
    thumb_tip = thumb_tip_pts.mean(axis=0) if len(thumb_tip_pts) else results["Thumb"]["joints"][3]
    finger_tips_mean = [np.mean(results[f]["skin"][tip_of(f)], axis=0) for f in four if (tip_of(f)).any()]
    middle_segments = np.concatenate([results[f]["skin"][finger_level[f] == 1] for f in ("Index", "Middle")])
    grip_numbers["thumb_opposition_degrees_from_fingers_side"] = round(G.opposite_sides(finger_tips_mean, thumb_tip, haft_centre, axis_direction), 1)
    grip_numbers["thumb_tip_to_index_middle_middle_segments"] = round(float(np.linalg.norm(thumb_tip_pts[:, None, :] - middle_segments[None, :, :], axis=2).min()), 4) if len(thumb_tip_pts) else None
    grip_numbers["palm_pad_gap_to_haft"] = round(float(G.signed_gaps(palm_skin, haft_centre, axis_direction, radius).min()), 4) if len(palm_skin) else None
    report["grip"] = grip_numbers
    report["weapon_placement"] = {"scale": round(scale, 4), "haft_radius": round(radius, 4), "grip_share": args.grip, "length_ratio": args.length_ratio,
                                  "haft_centre": np.round(haft_centre, 4).tolist(), "head_direction": np.round(head_dir, 3).tolist(), "roll_degrees": args.roll,
                                  "diagonal_from_closing_axis_degrees": round(float(np.degrees(np.arccos(abs(float(axis_direction @ closing))))), 1),
                                  "start_on_little_finger_side": best_l0, "end_in_web": best_mu, "depth_offset": best_delta, "fit_cost": round(cost, 4),
                                  "search_best_three": [{"cost": round(c, 4), "l0": a, "mu": m, "delta": d, "back": b} for c, a, m, d, b in candidates[:3]]}
    tip_points, curl = {}, {}
    for finger in FINGERS:
        names = finger_names(hand, finger)
        result = results[finger]
        for i in range(3):
            if abs(result["angles"][i]) > 1e-9:
                set_pose_matrix(arm, names[i], result["axes"][i], result["angles"][i], np.array(arm.matrix_world @ arm.pose.bones[names[i]].head))
        curl[finger] = {"angles_degrees": [round(math.degrees(a), 1) for a in result["angles"]], "stopped_by": result["why"]}
        tip_points[finger] = None
    report["curl"] = curl

    # ---- bake the fist into the body's rest shape, finger bones back to rest ------------------------------
    posed = evaluated_coords(body)
    moved = np.linalg.norm(posed - rest_coords, axis=1)
    report["baked"] = {"vertices_moved": int((moved > 1e-6).sum()), "largest_move": round(float(moved.max()), 4)}
    inverse = np.linalg.inv(np.array(body.matrix_world))
    local_baked = posed @ inverse[:3, :3].T + inverse[:3, 3]
    body.data.vertices.foreach_set("co", local_baked.ravel())
    body.data.update()
    for finger in FINGERS:
        for name in finger_names(hand, finger):
            pb = arm.pose.bones[name]
            pb.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()
    again = evaluated_coords(body)
    report["baked"]["rest_after_reset_matches"] = bool(np.abs(again - posed).max() < 1e-5)
    fist_world = posed

    # finger channels leave the clips: the clips pose the fingers, the fist is the rest shape
    dropped = 0
    drop_names = {n for finger in FINGERS for n in finger_names(hand, finger)}
    for action in bpy.data.actions:
        for fcurve, container in action_fcurves(action):
            bone = fcurve.data_path.split('"')[1] if fcurve.data_path.startswith("pose.bones[") else None
            if bone in drop_names:
                container.remove(fcurve)
                dropped += 1
    report["finger_channels_dropped"] = dropped

    # ---- place the weapon, bind it rigidly to the hand --------------------------------------------
    inverse_w = np.linalg.inv(np.array(weapon.matrix_world))
    weapon.data.vertices.foreach_set("co", (placed @ inverse_w[:3, :3].T + inverse_w[:3, 3]).ravel())
    weapon.data.update()
    weapon.parent = arm
    weapon.matrix_parent_inverse = arm.matrix_world.inverted()
    bind_bone = PREFIX + hand
    if args.weapon_bone:
        # The weapon gets its own bone, a child of the hand at the grip point, so a clip can let it go.
        bind_bone = PREFIX + WEAPON_BONE
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="EDIT")
        edit_bone = arm.data.edit_bones.new(bind_bone)
        inverse_arm = np.linalg.inv(np.array(arm.matrix_world))
        head_local = inverse_arm[:3, :3] @ haft_centre + inverse_arm[:3, 3]
        tail_local = inverse_arm[:3, :3] @ (haft_centre + head_dir * 0.08 * height) + inverse_arm[:3, 3]
        edit_bone.head, edit_bone.tail = Vector(head_local), Vector(tail_local)
        edit_bone.parent = arm.data.edit_bones[PREFIX + hand]
        edit_bone.use_connect = False
        bpy.ops.object.mode_set(mode="OBJECT")
        arm.pose.bones[bind_bone].rotation_mode = "QUATERNION"
        bpy.context.view_layer.update()
    hand_group = weapon.vertex_groups.new(name=bind_bone)
    hand_group.add(list(range(len(weapon.data.vertices))), 1.0, "REPLACE")
    modifier = weapon.modifiers.new("Armature", "ARMATURE")
    modifier.object = arm
    weapon.name, weapon.data.name = "tripo_part_1", "tripo_part_1"
    body.name, body.data.name = "tripo_part_0", "tripo_part_0"

    # the haft's axis, carried with the hand bone: (point, direction) at rest
    hand_bone = arm.data.bones[PREFIX + hand]
    hand_rest = np.array(arm.matrix_world @ hand_bone.matrix_local)

    def haft_now(frame_pose=True):
        pb = arm.pose.bones[PREFIX + hand]
        m = np.array(arm.matrix_world @ pb.matrix) @ np.linalg.inv(hand_rest)
        return m[:3, :3] @ haft_centre + m[:3, 3], m[:3, :3] @ head_dir

    # ---- the arm hold ------------------------------------------------------------------------------
    action_names = [a.name for a in bpy.data.actions]
    fade_clips = [resolve_clip_name(n, action_names) for n in args.hold_fade_clips.split(",") if n]
    drop_clips = [resolve_clip_name(n, action_names) for n in args.release_clips.split(",") if n]
    hold_clips = [resolve_clip_name(n, action_names) for n in args.hold_clips.split(",") if n] + fade_clips + drop_clips
    out_f, fwd_f, up_f = (float(v) for v in args.hold_hand.split(","))
    side = -1.0 if "Right" in hand else 1.0
    target = np.array([centre_x + side * out_f * height, float(wrist[1]) * 0 + (float(rest_head(arm, PREFIX + "Hips")[1]) - fwd_f * height), ground + up_f * height])
    target_axis = np.array([float(v) for v in args.hold_axis.split(",")])
    arm_bones = [PREFIX + hand.replace("Hand", "Shoulder"), PREFIX + hand.replace("Hand", "Arm"), PREFIX + hand.replace("Hand", "ForeArm"), PREFIX + hand]
    arm_scales = (0.3, 1.0, 1.0, 1.0)
    arm_groups = [PREFIX + hand.replace("Hand", "Arm"), PREFIX + hand.replace("Hand", "ForeArm"), PREFIX + hand]
    arm_family = [n for n in {g for g in groups} if n in arm_groups or n.startswith(PREFIX + hand)]
    hold = {"target_position": np.round(target, 3).tolist(), "target_axis": target_axis.tolist(), "clips": {}}
    for name in hold_clips:
        action = bpy.data.actions[name]
        use_action(arm, action)
        f0 = int(action.frame_range[0])
        scene.frame_set(f0)
        base_q = {b: Quaternion(arm.pose.bones[b].rotation_quaternion) for b in arm_bones}
        fade_to = None
        if name in fade_clips or name in drop_clips:
            # full weight on the first frame, none by the time the hand starts to rise (a clip that lets go of the
            # weapon: to fall, 4% of the height), which is also the frame the weapon is let go
            f1_clip = int(action.frame_range[1])
            start_z = float((arm.matrix_world @ arm.pose.bones[PREFIX + hand].head).z)
            fade_to = f0 + 12
            for frame in range(f0, f1_clip + 1):
                scene.frame_set(frame)
                z_now = float((arm.matrix_world @ arm.pose.bones[PREFIX + hand].head).z)
                if (name in drop_clips and z_now < start_z - args.release_drop * height) or (name not in drop_clips and z_now > start_z + 0.05 * height):
                    fade_to = max(frame, f0 + 6)
                    break
            scene.frame_set(f0)
        before_point, before_dir = haft_now()
        arm_inside_before = torso_inside_share(body, groups, arm_family, evaluated_coords(body))

        def forward_kinematics(params):
            for k, bone in enumerate(arm_bones):
                rv = params[3 * k : 3 * k + 3] * arm_scales[k]
                angle = float(np.linalg.norm(rv))
                q_off = Quaternion(Vector(rv / angle), angle) if angle > 1e-9 else Quaternion()
                arm.pose.bones[bone].rotation_quaternion = base_q[bone] @ q_off
            bpy.context.view_layer.update()
            point, direction = haft_now()
            return point, direction

        starts = [np.zeros(12)]
        for roll in (np.pi / 2, np.pi, -np.pi / 2):
            guess = np.zeros(12)
            guess[7] = roll  # the forearm's own axis (bone Y)
            starts.append(guess)
        solved = G.solve_hold(forward_kinematics, starts, target, target_axis, scale=height, ridge=0.01)
        params = solved["params"]
        offsets = {}
        for k, bone in enumerate(arm_bones):
            rv = params[3 * k : 3 * k + 3] * arm_scales[k]
            angle = float(np.linalg.norm(rv))
            offsets[bone] = Quaternion(Vector(rv / angle), angle) if angle > 1e-9 else Quaternion()
        # multiply the offsets into every key of the four bones
        for bone, q_off in offsets.items():
            curves = {}
            for fcurve, _c in action_fcurves(action):
                if fcurve.data_path == f'pose.bones["{bone}"].rotation_quaternion':
                    curves[fcurve.array_index] = fcurve
            if len(curves) != 4:
                raise SystemExit(f"{name}: {bone} has {len(curves)} rotation channels, expected 4")
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
        use_action(arm, action)
        scene.frame_set(f0)
        after_point, after_dir = haft_now()
        arm_inside_after = torso_inside_share(body, groups, arm_family, evaluated_coords(body))
        hold["clips"][name] = {
            "grip_point_before": np.round(before_point, 3).tolist(), "grip_point_after": np.round(after_point, 3).tolist(),
            "haft_up_before_degrees": round(float(np.degrees(np.arccos(np.clip(G.unit(before_dir) @ target_axis, -1, 1)))), 1),
            "haft_up_after_degrees": round(float(np.degrees(np.arccos(np.clip(G.unit(after_dir) @ target_axis, -1, 1)))), 1),
            "position_error": round(float(np.linalg.norm(after_point - target)), 4),
            "offsets_degrees": {b.replace(PREFIX, ""): round(math.degrees(q.angle), 1) for b, q in offsets.items()},
            "arm_inside_torso_share_before": round(arm_inside_before, 4), "arm_inside_torso_share_after": round(arm_inside_after, 4),
            "faded_out_by_frame": fade_to,
        }
    report["hold"] = hold

    # ---- quaternion keys (before the fall of the weapon, which is keyed against the final motion of the hand): one hemisphere per bone (a flip makes Blender turn the long way), and the biggest steps ----
    report["rotation_keys"] = {action.name: normalise_rotation_keys(action) for action in bpy.data.actions}

    # ---- clearance: turn the hand about the wrist, frame by frame, until the weapon leaves the body ----------------
    # A general rule for every armed unit (lib/tripo_clearance.py): a frame in which more than 0.25% of the weapon's free points are deeper than
    # 1% of the height inside the body gets the smallest rotation of the hand about the wrist joint (cap 50 degrees) that clears it, smoothed over
    # time. Frames from the release of a release clip on are left to the fall. A frame that cannot be cleared inside the cap is reported and the
    # run exits 3 after writing its files (--clearance-allow-fail to go on): the clip then fails TRIPO-WEAPON-IN-BODY, loudly.
    clearance = {}
    hand_name = PREFIX + hand
    triangles = body_triangles(body)
    if not args.no_clearance:
        wanted = [resolve_clip_name(n, action_names) for n in args.clearance_clips.split(",") if n]
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
            if action.name in drop_clips:
                skip = int(hold["clips"].get(action.name, {}).get("faded_out_by_frame") or last + 1) - first
            result = CL.clear_clip(weapon_frames, pivots, body_frames, triangles, height, skip_from=skip, rest_weapon=placed, rest_grip=haft_centre)
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
                "failed_frames": [frames_list[i] for i in result["failed"]], "released_from_frame": None if skip is None else first + skip,
            }
    report["clearance"] = clearance
    clearance_failed = {name: row["failed_frames"] for name, row in clearance.items() if row["failed_frames"]}

    # ---- the weapon lets go: the fall of the weapon bone in the release clips -------------------------------
    release = {}
    for name in [resolve_clip_name(n, action_names) for n in args.release_clips.split(",") if n]:
        if not args.weapon_bone:
            raise SystemExit("--release-clips needs --weapon-bone")
        release[name] = release_weapon(arm, body, bind_bone, hand, bpy.data.actions[name], placed, haft_centre, head_dir, blade, third,
                                       np.array(arm.matrix_world @ hand_bone.matrix_local), height, args.release_ease_frames,
                                       release_at=hold["clips"].get(name, {}).get("faded_out_by_frame"))
    report["release"] = release

    # ---- the checks: fingers on the haft, on sampled frames of every clip -----------------------------
    zone = 4.0 * radius
    gaps = {}
    for action in bpy.data.actions:
        if action.name in release:
            continue  # the weapon has let go of the hand
        use_action(arm, action)
        f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
        worst = {f: {"deepest": 1.0, "tip_gap": 0.0} for f in FINGERS}
        for frame in np.linspace(f0, f1, args.check_frames).round().astype(int):
            scene.frame_set(int(frame))
            coords = evaluated_coords(body)
            point, direction = haft_now()
            hand_pb = arm.pose.bones[PREFIX + hand]
            m = np.array(arm.matrix_world @ hand_pb.matrix) @ np.linalg.inv(hand_rest)
            per_finger = G.finger_gaps({f: coords[finger_index[f]] for f in FINGERS},
                                       {f: coords[finger_index[f][finger_tip[f]]] for f in FINGERS}, point, direction, radius, zone)
            for f, row in per_finger.items():
                if row["deepest"] is not None:
                    worst[f]["deepest"] = min(worst[f]["deepest"], row["deepest"])
                    worst[f]["tip_gap"] = max(worst[f]["tip_gap"], row["tip_gap"])
        gaps[action.name] = {f: {k: (round(v, 4) if v is not None else None) for k, v in row.items()} for f, row in worst.items()}
    report["fingers_on_haft"] = {"zone": round(zone, 4), "haft_radius": round(radius, 4), "per_clip_worst": gaps}

    # ---- export ----------------------------------------------------------------------------------
    for action in bpy.data.actions:
        action.use_fake_user = True
    use_action(arm, bpy.data.actions[0])
    bpy.ops.object.select_all(action="DESELECT")
    for obj in (arm, body, weapon):
        obj.select_set(True)
    bpy.context.view_layer.objects.active = arm
    args.out.parent.mkdir(parents=True, exist_ok=True)
    properties = bpy.ops.export_scene.gltf.get_rna_type().properties
    options = {"filepath": str(args.out), "export_format": "GLB", "use_selection": True, "export_skins": True, "export_animations": True,
               "export_animation_mode": "ACTIONS", "export_image_format": "AUTO"}
    bpy.ops.export_scene.gltf(**{k: v for k, v in options.items() if k in properties})
    report["exported_clips"] = sorted(a.name for a in bpy.data.actions)
    text = json.dumps(report, sort_keys=True)
    print(text)
    if args.report:
        args.report.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if clearance_failed and not args.clearance_allow_fail:
        print("CLEARANCE_FAILED " + json.dumps(clearance_failed), file=sys.stderr)
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
