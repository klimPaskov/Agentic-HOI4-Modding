"""Weapon clearance: turn a held weapon about the wrist, frame by frame, until it leaves the body.

Tripo's clips are made for an empty hand or for the weapon the clip's prompt names, so a separately modelled weapon rides the
hand through the body (an axe haft across the belly in an attack, through the legs in a stagger). The kit measures that
(`TRIPO-WEAPON-IN-BODY`: more than `LIMIT` of the weapon's points deeper than `MARGIN` of the height inside the body, in any frame)
and, for every armed unit, fixes it here: for each frame that fails, the smallest rotation of the hand about the wrist joint
(any axis, up to `MAX_ANGLE_DEGREES`) that brings the weapon's share under `TARGET`; the rotations are smoothed over time and the
frames that still fail are pushed a little farther, within the cap. A frame that cannot be cleared inside the cap keeps the best
rotation found and is reported, so the clip fails the check loudly instead of being hidden.

Maths only (numpy). `tripo/grip_weapon.py` applies the result to the hand bone; `tripo/clip_check.py` supplies the inside test.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from lib import tripo_grip as G

CLEAR_MARGIN_SHARE = 0.003  # what the clearance rule and the drop judge with: the exported unit's pose differs from the grip stage's by about 1% of the height (the retarget drops the location keys of every bone but the root, the mesh is remeshed), so a frame that passes the check's 1% margin here can fail it there
MARGIN_SHARE = 0.01  # a weapon point counts as through the body when this deep (share of the body height), as in TRIPO-WEAPON-IN-BODY
CHECK_LIMIT = 0.01  # the check's limit: share of the weapon's free points
LIMIT = 0.006  # what a solved clip must stay under: a margin for the baked keys, the eased snaps and the check's own sampling
TARGET = 0.0015  # what each frame's solve aims for
GRIP_RADIUS_SHARE = 0.12  # points this near the hand joint are the grip and are not judged
MAX_ANGLE_DEGREES = 60.0
ANGLES_DEGREES = (4.0, 8.0, 12.0, 17.0, 23.0, 30.0, 38.0, 46.0, 53.0, 60.0, 68.0, 76.0, 84.0, 90.0)  # past 60 only for a caller that asks for a larger `max_angle`
HOLD_FRAMES = 4  # a solved frame's rotation fades out over this many frames either side, so smoothing does not dilute it
MAX_POINTS = 600
SOFT_SHARE = 0.04  # a weapon keeps this far (share of the height) from cloth that a later stage swings (the cloak's chains), see `deep_share`
# The up axis of the poses the clearance solve sees (the grip stage's Blender world is Z-up): a held weapon below the body's lowest point counts as
# in the body, so the wrist turns it out of the ground too. The round 4 orc's guard crouch held its axe 3.3% under the feet (TRIPO-WEAPON-BELOW-GROUND).
# None switches it off. The drop after a release has its own ground rule.
GROUND_AXIS: Optional[int] = 2
# `clear_clip(coherent=True)`: a frame's solve tries the axes (of `COHERENT_AXES` spread over the sphere) within this cosine of the previous solved frame's axis
# first, if that frame is at most `COHERENT_GAP` frames back.
COHERENT_AXES = 120
COHERENT_COSINE = 0.8
COHERENT_GAP = 3


def _clip_check():
    path = str(Path(__file__).resolve().parents[1] / "tripo")
    if path not in sys.path:
        sys.path.insert(0, path)
    import clip_check

    return clip_check


def fibonacci_axes(count: int = 30) -> np.ndarray:
    """Unit vectors spread over the sphere."""

    k = np.arange(count) + 0.5
    phi = np.arccos(1.0 - 2.0 * k / count)
    theta = np.pi * (1.0 + 5.0 ** 0.5) * k
    return np.stack([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)], axis=1)


def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    x, y, z = np.asarray(axis, float) / max(float(np.linalg.norm(axis)), 1e-12)
    k = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + np.sin(angle) * k + (1.0 - np.cos(angle)) * (k @ k)


def rotvec_matrix(rotvec: np.ndarray) -> np.ndarray:
    angle = float(np.linalg.norm(rotvec))
    return np.eye(3) if angle < 1e-12 else rotation_matrix(np.asarray(rotvec, float), angle)


def sample_points(points: np.ndarray, count: int = MAX_POINTS) -> np.ndarray:
    """At most `count` evenly spaced points (the sampling the check uses)."""

    points = np.asarray(points, float)
    if len(points) <= count:
        return points
    return points[np.linspace(0, len(points) - 1, count).astype(int)]


def deep_share(points: np.ndarray, body_positions: np.ndarray, body_triangles: np.ndarray, height: float, margin: float = MARGIN_SHARE,
               soft: Optional[np.ndarray] = None, soft_share: float = 0.0, ground_axis: Optional[int] = None) -> float:
    """Share of `points` inside the body (ray parity) and deeper than `margin` of `height` from its nearest vertex.

    `soft` (a mask over `body_positions`) names cloth that a later stage swings (a cloak given its own bone chains moves a few percent of
    the height off the pose this stage sees, and may then sweep into a weapon that only just cleared it). A point within `soft_share` of
    the height of a soft vertex counts too, so the weapon is cleared of the cloth by its swing and not by the margin of the rigid pose."""

    if not len(points):
        return 0.0
    cc = _clip_check()
    bad = np.zeros(len(points), dtype=bool)
    low, high = body_positions.min(axis=0), body_positions.max(axis=0)
    near = np.all((points >= low) & (points <= high), axis=1)
    if near.any():
        inside = np.zeros(len(points), dtype=bool)
        inside[near] = cc.points_inside_mesh(points[near], body_positions[body_triangles])
        if inside.any():
            bad[inside] = cc.nearest_vertex_distance(points[inside], body_positions) / height > margin
    if soft is not None and soft_share > 0 and np.any(soft):
        bad |= cc.nearest_vertex_distance(points, body_positions[soft]) / height < soft_share
    if ground_axis is not None:
        # a held weapon under the body's lowest point is in the ground (TRIPO-WEAPON-BELOW-GROUND judges the same way)
        bad |= points[:, ground_axis] < body_positions[:, ground_axis].min()
    return float(bad.sum()) / len(points)


def free_points(weapon_points: np.ndarray, hand_joint: np.ndarray, height: float) -> np.ndarray:
    """The weapon points the check judges: the sampled ones, outside the grip zone around the hand joint."""

    sampled = sample_points(weapon_points)
    return sampled[np.linalg.norm(sampled - hand_joint, axis=1) > GRIP_RADIUS_SHARE * height]


def solve_frame(
    weapon_points: np.ndarray,
    pivot: np.ndarray,
    body_positions: np.ndarray,
    body_triangles: np.ndarray,
    height: float,
    target: float = TARGET,
    max_angle: float = MAX_ANGLE_DEGREES,
    axes: Optional[np.ndarray] = None,
    soft: Optional[np.ndarray] = None,
    soft_share: float = 0.0,
    ground_axis: Optional[int] = GROUND_AXIS,
) -> Tuple[np.ndarray, float]:
    """The smallest rotation about `pivot` (a rotation vector, radians) that brings the weapon's deep share to `target` or less, and the share left.

    `weapon_points` are the free points (outside the grip zone). Angles are tried in increasing order, every axis at each; the first angle at
    which some axis meets the target wins (the axis with the smallest share at that angle). With none, the best found within `max_angle`.
    """

    axes = fibonacci_axes() if axes is None else axes
    start = deep_share(weapon_points, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis)
    if start <= target:
        return np.zeros(3), start
    best = (start, np.zeros(3))
    offsets = weapon_points - pivot
    for degrees in ANGLES_DEGREES:
        if degrees > max_angle + 1e-9:
            break
        angle = np.radians(degrees)
        found = None
        for axis in axes:
            moved = offsets @ rotation_matrix(axis, angle).T + pivot
            share = deep_share(moved, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis)
            if share < best[0]:
                best = (share, axis * angle)
            if share <= target and (found is None or share < found[0]):
                found = (share, axis * angle)
        if found is not None:
            return found[1], found[0]
    return best[1], best[0]


def smooth_rotations(rotvecs: np.ndarray, radius: int = 3) -> np.ndarray:
    """Triangular smoothing of the rotation vectors over time (edges padded with the end values)."""

    rotvecs = np.asarray(rotvecs, float)
    if radius <= 0 or len(rotvecs) < 3:
        return rotvecs.copy()
    weights = np.array([radius + 1 - abs(k) for k in range(-radius, radius + 1)], float)
    weights /= weights.sum()
    padded = np.concatenate([np.repeat(rotvecs[:1], radius, axis=0), rotvecs, np.repeat(rotvecs[-1:], radius, axis=0)])
    return np.stack([np.convolve(padded[:, k], weights, mode="valid") for k in range(3)], axis=1)


def _clip_free_points(weapon_frames, pivots, height, rest_weapon, rest_grip):
    """The weapon points each frame is judged on: the check's own choice when the rest pose is given, else the points outside the grip zone."""

    count = len(weapon_frames)
    if rest_weapon is None or rest_grip is None:
        return [free_points(weapon_frames[i], pivots[i], height) for i in range(count)]
    # the check's own choice: the points evenly sampled from the weapon, those outside the grip zone around the grip point at REST
    indices = np.linspace(0, len(rest_weapon) - 1, min(MAX_POINTS, len(rest_weapon))).astype(int)
    keep = indices[np.linalg.norm(np.asarray(rest_weapon)[indices] - rest_grip, axis=1) > GRIP_RADIUS_SHARE * height]
    return [np.asarray(weapon_frames[i])[keep] for i in range(count)]


def _hold_neighbours(raw, last):
    """The frames around a solved one hold its rotation, fading out, where they have none of their own: the smoothing then leaves it nearly whole."""

    held = raw.copy()
    for i in range(last):
        if np.linalg.norm(raw[i]) > 0:
            for k in range(1, HOLD_FRAMES + 1):
                for j in (i - k, i + k):
                    if 0 <= j < last and np.linalg.norm(held[j]) < np.linalg.norm(raw[i]) * (1 - k / (HOLD_FRAMES + 1)):
                        held[j] = raw[i] * (1 - k / (HOLD_FRAMES + 1))
    return held


def _clip_shares(free, pivots, vectors, body_frames, body_triangles, height, last, soft=None, soft_share=0.0, ground_axis=GROUND_AXIS):
    """The deep share per frame with each frame's rotation applied; frames from `last` on (the weapon let go) count 0."""

    out = []
    for i in range(len(free)):
        if i >= last:
            out.append(0.0)
            continue
        moved = (free[i] - pivots[i]) @ rotvec_matrix(vectors[i]).T + pivots[i]
        out.append(deep_share(moved, body_frames[i], body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis))
    return out


def _solve_frames(free, pivots, body_frames, body_triangles, height, wanted, last, target, max_angle, coherent, soft, soft_share, ground_axis) -> np.ndarray:
    """Each frame's own solve (`solve_frame`) where the part is in the body; with `coherent`, the axes near the frame before's first."""

    raw = np.zeros((len(free), 3))
    previous, previous_at = None, -10
    cone = fibonacci_axes(COHERENT_AXES)
    for i in range(last):
        if wanted[i] <= target:
            continue
        near = cone[cone @ previous > COHERENT_COSINE] if coherent and previous is not None and i - previous_at <= COHERENT_GAP else None
        near = near if near is not None and len(near) else None
        raw[i], left = solve_frame(free[i], pivots[i], body_frames[i], body_triangles, height, target, max_angle, near,
                                   soft=soft, soft_share=soft_share, ground_axis=ground_axis)
        if near is not None and left > target:
            raw[i], left = solve_frame(free[i], pivots[i], body_frames[i], body_triangles, height, target, max_angle, soft=soft, soft_share=soft_share, ground_axis=ground_axis)
        if np.linalg.norm(raw[i]) > 0:
            previous, previous_at = raw[i] / np.linalg.norm(raw[i]), i
    return raw


def _cut_back(points, pivot, vector, body_positions, body_triangles, height, limit, soft, soft_share, ground_axis) -> np.ndarray:
    """A frame clear without a turn of its own that the turn held in from its neighbours puts in the body: the largest share of that turn
    that keeps it clear (the round 4 dwarf's shield, clear without a turn in the attack's frames 20 to 24, was turned 63 to 81 degrees into
    the torso by the turn its frames 14 to 17 needed)."""

    for share in (0.75, 0.5, 0.25):
        moved = (points - pivot) @ rotvec_matrix(vector * share).T + pivot
        if deep_share(moved, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis) <= limit:
            return vector * share
    return vector * 0.0


def clear_clip(
    weapon_frames: Sequence[np.ndarray],
    pivots: Sequence[np.ndarray],
    body_frames: Sequence[np.ndarray],
    body_triangles: np.ndarray,
    height: float,
    limit: float = LIMIT,
    target: float = TARGET,
    max_angle: float = MAX_ANGLE_DEGREES,
    skip_from: Optional[int] = None,
    rounds: int = 4,
    rest_weapon: Optional[np.ndarray] = None,
    rest_grip: Optional[np.ndarray] = None,
    soft: Optional[np.ndarray] = None,
    soft_share: float = 0.0,
    ground_axis: Optional[int] = GROUND_AXIS,
    coherent: bool = False,
) -> Dict[str, object]:
    """Solve a whole clip. Per frame i: `weapon_frames[i]` (all weapon points), `pivots[i]` (the wrist joint), `body_frames[i]` (the body's posed vertices).

    With `coherent`, a frame's solve first tries only the axes within `COHERENT_CONE` of the previous solved frame's axis (and the full set when none of
    them clears it), so the hand's added turn changes smoothly from frame to frame and does not fail a spin check where the axis flips.
    Frames from `skip_from` on (the weapon has been let go) are left alone. `soft` and `soft_share` (see `deep_share`) keep the weapon clear of
    swinging cloth: the solve aims at them, but only the hard test (the check's own) decides which frames "failed". Returns the rotation vector per frame ("rotvecs"), the deep share
    per frame before and after, the frames still over `limit` ("failed") and the largest angle used in degrees.
    """

    count = len(weapon_frames)
    last = count if skip_from is None else min(skip_from, count)
    free = _clip_free_points(weapon_frames, pivots, height, rest_weapon, rest_grip)
    before = [deep_share(free[i], body_frames[i], body_triangles, height, CLEAR_MARGIN_SHARE, ground_axis=ground_axis) if i < last else 0.0 for i in range(count)]
    wanted = before if soft is None else [deep_share(free[i], body_frames[i], body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis) if i < last else 0.0 for i in range(count)]
    raw = _solve_frames(free, pivots, body_frames, body_triangles, height, wanted, last, target, max_angle, coherent, soft, soft_share, ground_axis)
    rotvecs = smooth_rotations(_hold_neighbours(raw, last), radius=1)
    # from the release on the weapon is free: the hand's rotation fades out over the next frames, so it does not snap back
    if skip_from is not None and 0 < last < count:
        for k in range(count - last):
            rotvecs[last + k] = rotvecs[last - 1] * max(0.0, 1.0 - (k + 1) / 5.0)
    else:
        rotvecs[last:] = 0.0
    after = _clip_shares(free, pivots, rotvecs, body_frames, body_triangles, height, last, soft, soft_share, ground_axis)
    cap = np.radians(max_angle)

    def cut_back(i, vector):
        return _cut_back(free[i], pivots[i], vector, body_frames[i], body_triangles, height, limit, soft, soft_share, ground_axis)

    for _ in range(rounds):
        over = [i for i in range(last) if after[i] > limit]
        if not over:
            break
        for i in over:
            if np.linalg.norm(raw[i]) > 0:
                # smoothing took away some of what the frame needed: ask for what its own solve found
                rotvecs[i] = raw[i]
            else:
                rotvecs[i] = cut_back(i, rotvecs[i])
            size = float(np.linalg.norm(rotvecs[i]))
            if size > cap:
                rotvecs[i] *= cap / size
        rotvecs = smooth_rotations(rotvecs, radius=1)
        after = _clip_shares(free, pivots, rotvecs, body_frames, body_triangles, height, last, soft, soft_share, ground_axis)
    # What smoothing could not keep: a frame takes its own solved rotation (frames are independent, so it passes if its own solve did), and a
    # frame that needed none has the turn carried into it cut back.
    for i in [i for i in range(last) if after[i] > limit]:
        rotvecs[i] = raw[i] if np.linalg.norm(raw[i]) > 0 else cut_back(i, rotvecs[i])
    after = _clip_shares(free, pivots, rotvecs, body_frames, body_triangles, height, last, ground_axis=ground_axis)  # the check's own test, soft cloth left out
    failed = [i for i in range(last) if after[i] > limit]
    soft_after = after if soft is None else _clip_shares(free, pivots, rotvecs, body_frames, body_triangles, height, last, soft, soft_share, ground_axis)
    return {
        "rotvecs": rotvecs, "before": before, "after": after, "failed": failed, "soft_after": soft_after,
        "max_degrees": float(np.degrees(np.linalg.norm(rotvecs, axis=1).max())) if count else 0.0,
        "frames_changed": int((np.linalg.norm(rotvecs, axis=1) > 1e-6).sum()),
    }


# ---- the order of the turns: the weapon in the hand first, the arm last, and a raised hand is never lowered ----------------------
#
# `clear_clip` turns the hand about the wrist. A frame it cannot clear within its cap goes on to two more turns, in this order, each only
# for the frames the turns before it left in the body (`clear_clip_staged`):
#
# 1. the roll: the held part turns about its own long axis (the haft, the shield's bar) through the grip, as a fist turns a bar it holds
#    (`roll_frame`). It moves nothing of the arm. A club's head is round about its haft, so this does little for a club, and much for a
#    shield, whose crescent reaches out sideways from the bar;
# 2. the arm: the upper arm turns about the shoulder (`arm_frame`), the smallest turn up to `ARM_MAX_DEGREES` that clears the part. It is
#    the last resort because it changes the clip's own motion. A hand the clip raises above the shoulder is never lowered by it (a turn
#    that would bring the wrist down more than `RAISE_KEEP_SHARE` of the height is not taken), and no turn may put the elbow or the wrist
#    inside the body.
#
# The dwarf's crescent shield (2026-11-17) stayed 4.9% in the body in the attack with the wrist at its cap (84 degrees and four passes
# on the exported files reached only 10% less), because a turn about the wrist swings the crescent round the fist and through the torso
# again: it is the roll that moves it out.

ROLL_ANGLES_DEGREES = (15.0, 30.0, 45.0, 60.0, 75.0, 90.0, 120.0, 150.0, 180.0)
ARM_ANGLES_DEGREES = (4.0, 8.0, 12.0, 17.0, 23.0, 30.0)
ARM_MAX_DEGREES = 30.0
ARM_AXES = 60
RAISE_KEEP_SHARE = 0.01
STAGE_RAMP_DEGREES = 8.0  # a roll or an arm turn grows and fades by at most this much a frame (`ramp_turns`), as the final clearance's hand turn


def roll_frame(points: np.ndarray, grip: np.ndarray, axis: np.ndarray, body_positions: np.ndarray, body_triangles: np.ndarray, height: float,
               target: float = TARGET, soft: Optional[np.ndarray] = None, soft_share: float = 0.0, ground_axis: Optional[int] = GROUND_AXIS,
               prefer: float = 1.0) -> Tuple[float, float]:
    """(the smallest turn of the held part about its own long `axis` through `grip`, radians, signed; the deep share left) that brings the
    part to `target`, or the best one found. `points` are the part's free points as the wrist turn left them. At each angle the `prefer`
    side (the sign the frame before took) is taken when it clears, so the roll does not flip from one side to the other between frames."""

    start = deep_share(points, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis)
    if start <= target:
        return 0.0, start
    best = (start, 0.0)
    offsets = np.asarray(points, float) - grip
    for degrees in ROLL_ANGLES_DEGREES:
        found = None
        for sign in ((1.0, -1.0) if prefer >= 0 else (-1.0, 1.0)):
            angle = sign * np.radians(degrees)
            share = deep_share(offsets @ rotation_matrix(axis, angle).T + grip, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis)
            if share < best[0]:
                best = (share, angle)
            if share <= target and found is None:
                found = (share, angle)
        if found is not None:
            return found[1], found[0]
    return best[1], best[0]


def arm_frame(points: np.ndarray, shoulder: np.ndarray, joints: np.ndarray, body_positions: np.ndarray, body_triangles: np.ndarray, height: float,
              up_axis: int, raised: bool, target: float = TARGET, soft: Optional[np.ndarray] = None, soft_share: float = 0.0,
              ground_axis: Optional[int] = GROUND_AXIS, axes: Optional[np.ndarray] = None) -> Tuple[np.ndarray, float]:
    """(the smallest turn of the upper arm about `shoulder`, a rotation vector; the deep share left) that brings the part to `target`, or the
    best one found. `joints` are the elbow and the wrist (the wrist last): no turn may put either inside the body, and when the hand is
    `raised` (above the shoulder in the clip) no turn may lower the wrist by more than `RAISE_KEEP_SHARE` of the height. `axes` are tried
    first when given (those near the frame before's axis, as `clear_clip(coherent=True)` does), then every axis."""

    cc = _clip_check()
    start = deep_share(points, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis)
    if start <= target:
        return np.zeros(3), start
    every = fibonacci_axes(ARM_AXES)
    best = (start, np.zeros(3))
    offsets = np.asarray(points, float) - shoulder
    joint_offsets = np.asarray(joints, float) - shoulder
    wrist_up = float(joints[-1][up_axis])
    for degrees in ARM_ANGLES_DEGREES:
        found = None
        for axis in (every if axes is None or not len(axes) else np.concatenate([axes, every])):
            if found is not None:
                break
            rotation = rotation_matrix(axis, np.radians(degrees))
            moved_joints = joint_offsets @ rotation.T + shoulder
            if raised and moved_joints[-1][up_axis] < wrist_up - RAISE_KEEP_SHARE * height:
                continue
            if cc.points_inside_mesh(moved_joints, body_positions[body_triangles]).any():
                continue
            share = deep_share(offsets @ rotation.T + shoulder, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE, soft, soft_share, ground_axis)
            if share < best[0]:
                best = (share, axis * np.radians(degrees))
            if share <= target and (found is None or share < found[0]):
                found = (share, axis * np.radians(degrees))
        if found is not None:
            return found[1], found[0]
    return best[1], best[0]


def staged_points(points: np.ndarray, pivot: np.ndarray, wrist: np.ndarray, grip: Optional[np.ndarray] = None, roll: Optional[np.ndarray] = None,
                  shoulder: Optional[np.ndarray] = None, arm: Optional[np.ndarray] = None) -> np.ndarray:
    """The part's points after the three turns, as `clear_clip_staged` composes them: the wrist (`wrist`, a rotation vector about `pivot`),
    the roll (`roll`, a world rotation vector about the grip as the wrist turn carries it: `grip` is the grip before any turn) and the upper
    arm (`arm`, about `shoulder`). Applied in that order to the pose, each about the joint as the turns before it left it, the arm last."""

    turn = rotvec_matrix(wrist)
    out = (np.asarray(points, float) - pivot) @ turn.T + pivot
    if roll is not None and grip is not None and float(np.linalg.norm(roll)) > 1e-12:
        carried = turn @ (np.asarray(grip, float) - pivot) + pivot
        out = (out - carried) @ rotvec_matrix(roll).T + carried
    if arm is not None and shoulder is not None and float(np.linalg.norm(arm)) > 1e-12:
        out = (out - shoulder) @ rotvec_matrix(arm).T + shoulder
    return out


def ramp_turns(rotvecs: np.ndarray, step_degrees: float = STAGE_RAMP_DEGREES, clear=None, last: Optional[int] = None) -> np.ndarray:
    """Per-frame turns (rotation vectors) with each one carried into the frames around it, fading by `step_degrees` a frame, wherever a
    frame has less: a solved turn grows in and fades out instead of starting and ending in one frame, which the unit's spin check
    fails (UNIT-ANIM-SPIN). A frame keeps at least its own turn. `clear(frame, vector)` says whether the part stays out of the body with a
    carried turn (a share of it is tried when not). Frames from `last` on keep none."""

    step = np.radians(step_degrees)
    out = np.array(rotvecs, float)
    end = len(out) if last is None else min(last, len(out))
    for order, side in ((range(1, end), -1), (range(end - 2, -1, -1), 1)):
        for i in order:
            j = i + side
            size = float(np.linalg.norm(out[j]))
            if size <= step or float(np.linalg.norm(out[i])) >= size - step:
                continue
            wanted = out[j] * ((size - step) / size)
            for share in (1.0, 0.75, 0.5, 0.25):
                if float(np.linalg.norm(wanted * share)) <= float(np.linalg.norm(out[i])):
                    break
                if clear is None or clear(i, wanted * share):
                    out[i] = wanted * share
                    break
    out[end:] = 0.0
    return out


def turn_between(a: np.ndarray, b: np.ndarray) -> float:
    """Degrees between two turns given as rotation vectors."""

    relative = rotvec_matrix(a).T @ rotvec_matrix(b)
    return float(np.degrees(np.arccos(np.clip((np.trace(relative) - 1.0) / 2.0, -1.0, 1.0))))


BRIDGE_SWEEPS = 4
BRIDGE_AXES = 24
# Bounds on the searches past the wrist, counted in tests of the part against the body (each about a millisecond or more on a full body), so a
# clip costs the same on every machine. The round 4 dwarf's grip stage ran over an hour with the bridge unbounded (every step of a solved
# stretch searched about 250 turns, four sweeps over a 369 frame idle). Past a bound the best turns found so far are kept, and the frames still
# in the body are reported (`failed`) as for any frame the cap leaves.
# A test costs about 60 ms on the round 4 dwarf's exported mesh (an unbounded solve of its 171 frame attack made 5,947 of them, six minutes).
BRIDGE_TESTS = 2000  # per call of `bridge_turns` (the final clearance, about two minutes at most)
WRIST_BRIDGE_TESTS = 500  # per clip (over all its passes in the grip stage), for the grip stage's bridge of the wrist (`wrist_room`)
STAGE_TESTS = 1000  # per clip (over all its passes in the grip stage), for the roll and the arm searches together


class Budget:
    """A count of tests a search may still make."""

    def __init__(self, tests: int):
        self.left = int(tests)
        self.spent_out = False

    def spend(self, tests: int = 1) -> bool:
        """Take `tests` from the count; False (and spent out) when not that many are left."""

        if self.left < tests:
            self.spent_out = True
            return False
        self.left -= tests
        return True


def matrix_rotvec(matrix: np.ndarray) -> np.ndarray:
    """The rotation vector of a rotation matrix."""

    angle = float(np.arccos(np.clip((np.trace(matrix) - 1.0) / 2.0, -1.0, 1.0)))
    if angle < 1e-9:
        return np.zeros(3)
    if angle > np.pi - 1e-6:
        values, vectors = np.linalg.eigh((matrix + matrix.T) / 2.0)
        return vectors[:, int(np.argmax(values))] * angle
    axis = np.array([matrix[2, 1] - matrix[1, 2], matrix[0, 2] - matrix[2, 0], matrix[1, 0] - matrix[0, 1]]) / (2.0 * np.sin(angle))
    return axis * angle


def _near_turns(keep: np.ndarray, own: np.ndarray, step: float) -> List[np.ndarray]:
    """Turns within `step` degrees of `keep`, nearest to `own` first: the straight line toward `own` and turns about every axis."""

    out = [keep + (own - keep) * t for t in np.linspace(1.0, 0.0, 9)]
    base = rotvec_matrix(keep)
    for share in (1.0, 0.5):
        for axis in fibonacci_axes(BRIDGE_AXES):
            out.append(matrix_rotvec(rotation_matrix(axis, np.radians(step * share)) @ base))
    out = [v for v in out if turn_between(v, keep) <= step + 1e-6]
    return sorted(out, key=lambda v: turn_between(v, own))


def bridge_turns(rotvecs: np.ndarray, clear, max_steps: Sequence[float], sweeps: int = BRIDGE_SWEEPS, budget: Optional[Budget] = None) -> np.ndarray:
    """Per-frame turns with every jump between neighbouring frames brought under `max_steps[i]` degrees (the step from frame i to i + 1)
    where a frame can take a turn nearer its neighbour's and stay clear (`clear(frame, vector)`).

    For a jump, one frame keeps its turn and the other takes the turn within the step of it that is nearest its own and clear: on the
    straight line toward its own, or about another axis when the straight way sweeps the part through the body. The frame whose own turn is
    smaller moves first (it needed less), then the other, and a moved frame can pass the jump on to the next. A jump no move clears is
    left, for the smoothing after it. The dwarf's shield needed 68 degrees of wrist in the attack's frame 19 and none in frame 20, where the
    same turn put it back in the torso: one frame of 62 degrees, which the spin rule smoothed over five frames, and three frames went back
    in the body. The straight way between the two turns is 11% in the body halfway. At most `budget` tests (`BRIDGE_TESTS` by default) are made: the jumps not reached by then are left."""

    budget = Budget(BRIDGE_TESTS) if budget is None else budget
    out = np.array(rotvecs, float)
    for _ in range(sweeps):
        moved = False
        for i in range(len(out) - 1):
            if turn_between(out[i], out[i + 1]) <= max_steps[i]:
                continue
            order = (i, i + 1) if np.linalg.norm(out[i]) <= np.linalg.norm(out[i + 1]) else (i + 1, i)
            for move in order:
                keep = i + 1 if move == i else i
                found = next((v for v in _near_turns(out[keep], out[move], max_steps[i]) if budget.spend() and clear(move, v)), None)
                if budget.spent_out:
                    return out
                if found is not None:
                    out[move] = found
                    moved = True
                    break
        if not moved:
            break
    return out


class _Staged:
    """What the stages after the wrist share for one clip: the poses, the wrist's turns and the test of a frame with a roll and an arm turn."""

    def __init__(self, free, pivots, body_frames, body_triangles, height, rotvecs, grips, shoulders, arm_joints, up_axis, last, options):
        self.free, self.pivots, self.body_frames, self.body_triangles, self.height = free, pivots, body_frames, body_triangles, height
        self.rotvecs, self.grips, self.shoulders, self.arm_joints, self.up_axis, self.last = rotvecs, grips, shoulders, arm_joints, up_axis, last
        self.limit = options.get("limit", LIMIT)
        self.target = options.get("target", TARGET)
        self.soft, self.soft_share = options.get("soft"), options.get("soft_share", 0.0)
        self.ground_axis = options.get("ground_axis", GROUND_AXIS)
        self.count = len(free)
        self.budget = Budget(STAGE_TESTS)

    def points(self, i, roll, arm=None):
        return staged_points(self.free[i], self.pivots[i], self.rotvecs[i], self.grips[i] if self.grips is not None else None, roll,
                             self.shoulders[i] if self.shoulders is not None else None, arm)

    def share(self, i, roll, arm, with_soft=False):
        if i >= self.last:
            return 0.0
        return deep_share(self.points(i, roll, arm), self.body_frames[i], self.body_triangles, self.height, CLEAR_MARGIN_SHARE,
                          self.soft if with_soft else None, self.soft_share if with_soft else 0.0, self.ground_axis)

    def shares(self, rolls, arms, with_soft=False):
        return [self.share(i, rolls[i], arms[i], with_soft) for i in range(self.count)]

    def over(self, after):
        return [i for i in range(self.last) if after[i] > self.limit]

    def raised(self, i):
        return float(np.asarray(self.arm_joints[i])[-1][self.up_axis]) > float(np.asarray(self.shoulders[i])[self.up_axis])

    def arm_allowed(self, i, vector):
        """A carried arm turn keeps the arm's own rules: a raised wrist is not lowered, the elbow and the wrist stay out of the body."""

        joints = np.asarray(self.arm_joints[i], float)
        moved = (joints - self.shoulders[i]) @ rotvec_matrix(vector).T + self.shoulders[i]
        if self.raised(i) and moved[-1][self.up_axis] < joints[-1][self.up_axis] - RAISE_KEEP_SHARE * self.height:
            return False
        return not bool(_clip_check().points_inside_mesh(moved, self.body_frames[i][self.body_triangles]).any())


def _roll_stage(st: _Staged, haft_axes, after, arms) -> Tuple[np.ndarray, List[int]]:
    """The roll of the part about its haft for the frames over the limit, ramped (`ramp_turns`)."""

    raw = np.zeros((st.count, 3))
    rolled, prefer = [], 1.0
    for i in st.over(after):
        if not st.budget.spend(2 * len(ROLL_ANGLES_DEGREES)):
            break
        wrist = rotvec_matrix(st.rotvecs[i])
        axis = wrist @ G.unit(haft_axes[i])
        grip = wrist @ (st.grips[i] - st.pivots[i]) + st.pivots[i]
        angle, _left = roll_frame(st.points(i, None), grip, axis, st.body_frames[i], st.body_triangles, st.height, st.target, st.soft,
                                  st.soft_share, st.ground_axis, prefer)
        raw[i] = axis * angle
        if angle:
            rolled.append(i)
            prefer = float(np.sign(angle))
    return ramp_turns(raw, clear=lambda i, vector: st.share(i, vector, arms[i]) <= st.limit, last=st.last), rolled


def _arm_stage(st: _Staged, after, rolls) -> Tuple[np.ndarray, List[int]]:
    """The upper arm's turn about the shoulder for the frames over the limit, ramped, never lowering a raised hand."""

    raw = np.zeros((st.count, 3))
    armed, cone, previous = [], fibonacci_axes(COHERENT_AXES), None
    for i in st.over(after):
        if not st.budget.spend(ARM_AXES * len(ARM_ANGLES_DEGREES) // 2):
            break
        near = cone[cone @ previous > COHERENT_COSINE] if previous is not None else None
        raw[i], _left = arm_frame(st.points(i, rolls[i]), st.shoulders[i], np.asarray(st.arm_joints[i], float), st.body_frames[i], st.body_triangles,
                                  st.height, st.up_axis, st.raised(i), st.target, st.soft, st.soft_share, st.ground_axis, near)
        if float(np.linalg.norm(raw[i])) > 0:
            armed.append(i)
            previous = raw[i] / np.linalg.norm(raw[i])
    return ramp_turns(raw, clear=lambda i, vector: st.share(i, rolls[i], vector) <= st.limit and st.arm_allowed(i, vector), last=st.last), armed


def clear_clip_staged(
    weapon_frames: Sequence[np.ndarray],
    pivots: Sequence[np.ndarray],
    body_frames: Sequence[np.ndarray],
    body_triangles: np.ndarray,
    height: float,
    grips: Optional[Sequence[np.ndarray]] = None,
    haft_axes: Optional[Sequence[np.ndarray]] = None,
    shoulders: Optional[Sequence[np.ndarray]] = None,
    arm_joints: Optional[Sequence[np.ndarray]] = None,
    up_axis: int = 2,
    wrist_room: Optional[Sequence[float]] = None,
    budgets: Optional[Dict[str, Budget]] = None,
    **options,
) -> Dict[str, object]:
    """`clear_clip` (the wrist), then for the frames it leaves over the limit the roll of the part about its haft (when `grips` and `haft_axes`,
    the grip point and the haft's direction per frame before any turn, are given), then the upper arm (when `shoulders` and `arm_joints`, the
    elbow and the wrist per frame, are given). Returns `clear_clip`'s result with "rolls" (radians per frame, about the haft as the wrist turn
    carries it), "arm_rotvecs" (per frame, about the shoulder), "after" and "failed" over all three, the frames each stage worked on, and
    whether a search stopped at its bound (`STAGE_TESTS`, `WRIST_BRIDGE_TESTS`).

    `wrist_room` (degrees per step between frames i and i + 1) bridges the wrist's turns first (`bridge_turns`), so the hand turns no faster
    than that more than the clip already does: the grip stage passes what its easing allows, because the easing of a turn that snaps
    retimes it and carries the weapon back into the body (the ogre's chop: 29% in frames 68 to 72 after an 85 degree snap).
    `budgets` ({"bridge": Budget, "stage": Budget}) lets a caller that clears one clip in several passes share one bound across them."""

    result = clear_clip(weapon_frames, pivots, body_frames, body_triangles, height, **options)
    count = len(weapon_frames)
    skip_from = options.get("skip_from")
    last = count if skip_from is None else min(skip_from, count)
    free = _clip_free_points(weapon_frames, pivots, height, options.get("rest_weapon"), options.get("rest_grip"))
    st = _Staged(free, pivots, body_frames, body_triangles, height, result["rotvecs"], grips, shoulders, arm_joints, up_axis, last, options)
    budgets = budgets or {}
    bridged = budgets.get("bridge") or Budget(WRIST_BRIDGE_TESTS)
    st.budget = budgets.get("stage") or st.budget
    rolls, arm = np.zeros((count, 3)), np.zeros((count, 3))
    if wrist_room is not None:
        room = [float(wrist_room[i]) if i + 1 < last else np.inf for i in range(count - 1)]
        st.rotvecs = result["rotvecs"] = bridge_turns(result["rotvecs"], lambda i, vector: deep_share(
            (free[i] - pivots[i]) @ rotvec_matrix(vector).T + pivots[i], body_frames[i], body_triangles, height, CLEAR_MARGIN_SHARE,
            ground_axis=st.ground_axis) <= st.limit, room, budget=bridged)
        result["after"] = _clip_shares(free, pivots, result["rotvecs"], body_frames, body_triangles, height, last, ground_axis=st.ground_axis)
    after = list(result["after"])
    rolled_frames, armed_frames = [], []
    if grips is not None and haft_axes is not None and st.over(after):
        rolls, rolled_frames = _roll_stage(st, haft_axes, after, arm)
        after = st.shares(rolls, arm)
    if shoulders is not None and arm_joints is not None and st.over(after):
        arm, armed_frames = _arm_stage(st, after, rolls)
        after = st.shares(rolls, arm)
    result.update({
        "rolls": rolls, "arm_rotvecs": arm, "after": after, "failed": st.over(after),
        "soft_after": after if st.soft is None else st.shares(rolls, arm, with_soft=True),
        "rolled_frames": rolled_frames, "armed_frames": armed_frames, "search_bound_reached": bool(st.budget.spent_out or bridged.spent_out),
        "max_roll_degrees": float(np.degrees(np.linalg.norm(rolls, axis=1).max())) if count else 0.0,
        "max_arm_degrees": float(np.degrees(np.linalg.norm(arm, axis=1).max())) if count else 0.0,
    })
    return result


# ---- the drop: a weapon is let go at the first frame of a fall and laid on the ground clear of the body --------------------------
#
# A general rule for every armed unit's death (no per-clip numbers). The hand lets go of the weapon at the first frame of the fall: the
# first frame where the pelvis starts to descend for good, or where the hand has dropped `HAND_DROP_SHARE` of the height, whichever comes
# first. The weapon then falls on its own path in `TUMBLE_SECONDS` (it crosses sideways at a steady speed, accelerates down under gravity and
# turns on the way) and lies flat on the ground at a resting place chosen from the body's final pose: at least `LANDING_CLEAR_SHARE` of the
# height from every point the body occupies after the weapon lands (so the falling body never sweeps through it), on the ground and never
# below it.
#
# The weapon has its own bone, a child of the hand. In every frame from the release the bone gets the one rigid pose (`local_pose`, rotation
# and translation keys) that holds the weapon on its world path whatever the hand does, so once it has landed it stays exactly still while the
# hand and body fall on.

TUMBLE_SECONDS = 0.4
HAND_DROP_SHARE = 0.04
FALL_NOISE_SHARE = 0.001  # pelvis jitter this small does not end a descent
FALL_MIN_DESCENT_SHARE = 0.08  # a death has to bring the pelvis down at least this far
LANDING_CLEAR_SHARE = 0.04
GROUND_LIFT_SHARE = 0.0015  # a weapon lies this far above the ground plane (its lowest point)


def fall_start_frame(pelvis: Sequence[float], hand: Sequence[float], height: float, hand_drop_share: float = HAND_DROP_SHARE) -> int:
    """The first frame of a fall: where the pelvis starts its last descent, or where the hand has dropped `hand_drop_share` of `height`, whichever comes first.

    `pelvis` and `hand` are heights (up axis) per frame. The last descent is the one that ends with the pelvis down: the first frame it is
    within 2% of `height` of its final height is the landing, the last frame before it at which the pelvis was still within a tenth of the
    descent from its highest level is where the pelvis was leaving that level, and the frame the descent started is found by walking back
    from there to the last frame the pelvis was not coming down (it fell by no more than `FALL_NOISE_SHARE` of `height` in that frame). A
    stagger or bounce lower down does not matter, and a crouch that rose again before the fall is not the start. A clip whose pelvis never comes down by `FALL_MIN_DESCENT_SHARE` has no fall of that
    kind, so only the hand counts. Returns the last frame's index when neither happens.
    """

    pelvis, hand = np.asarray(pelvis, float), np.asarray(hand, float)
    found = len(pelvis) - 1
    below = np.nonzero(hand < hand[0] - hand_drop_share * height)[0]
    if len(below):
        found = int(below[0])
    if pelvis.max() - pelvis[-1] >= FALL_MIN_DESCENT_SHARE * height:
        landed = int(np.nonzero(pelvis <= pelvis[-1] + 0.02 * height)[0][0])
        top_level = float(pelvis[: landed + 1].max())
        drop = top_level - float(pelvis[landed])
        leaving = int(np.nonzero(pelvis[: landed + 1] >= top_level - 0.1 * drop)[0][-1])
        noise = FALL_NOISE_SHARE * height
        while leaving > 0 and pelvis[leaving] < pelvis[leaving - 1] - noise:
            leaving -= 1
        found = min(found, leaving)
    return int(found)


def lying_orientations(axes: np.ndarray, steps: int = 24) -> List[np.ndarray]:
    """Rotations that lay a weapon flat: its head axis (column 0 of `axes`) horizontal, its third axis (column 2, the thin one) vertical.

    `axes` has the weapon's head, blade and third directions as columns, at rest. Every heading about the up axis (z) in `steps` steps,
    head either way, blade either way.
    """

    out = []
    for flip_head in (1.0, -1.0):
        for flip_blade in (1.0, -1.0):
            base = np.stack([[flip_head, 0.0, 0.0], [0.0, flip_blade, 0.0], [0.0, 0.0, flip_head * flip_blade]], axis=1)
            for k in range(steps):
                psi = 2.0 * np.pi * k / steps
                c, s = np.cos(psi), np.sin(psi)
                spin = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
                out.append(spin @ base @ np.asarray(axes, float).T)
    return out


def distance_grid(points_xy: np.ndarray, low: np.ndarray, size: Tuple[int, int], cell: float) -> np.ndarray:
    """Distance from each grid cell centre to the nearest of `points_xy`."""

    xs = low[0] + cell * np.arange(size[0])
    ys = low[1] + cell * np.arange(size[1])
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    cells = np.stack([gx.ravel(), gy.ravel()], axis=1)
    out = np.empty(len(cells))
    for start in range(0, len(cells), 2048):
        block = cells[start : start + 2048]
        out[start : start + 2048] = np.sqrt(((block[:, None, :] - points_xy[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    return out.reshape(size)


def _shifted(grid: np.ndarray, dx: int, dy: int, fill: float) -> np.ndarray:
    """`out[i, j] = grid[i + dx, j + dy]`, `fill` outside."""

    out = np.full_like(grid, fill)
    if abs(dx) >= grid.shape[0] or abs(dy) >= grid.shape[1]:
        return out
    sx = slice(max(dx, 0), grid.shape[0] + min(dx, 0))
    sy = slice(max(dy, 0), grid.shape[1] + min(dy, 0))
    tx = slice(max(-dx, 0), grid.shape[0] + min(-dx, 0))
    ty = slice(max(-dy, 0), grid.shape[1] + min(-dy, 0))
    out[tx, ty] = grid[sx, sy]
    return out


def landing_places(
    rest_relative: np.ndarray,
    orientations: Sequence[np.ndarray],
    occupied_xy: np.ndarray,
    release_xy: np.ndarray,
    height: float,
    clear: float = LANDING_CLEAR_SHARE,
    keep: int = 24,
) -> List[Dict[str, object]]:
    """Resting places on the ground for a weapon, best first: one per orientation at most, none nearer than `clear` of `height` to the body.

    `rest_relative` are weapon points relative to the grip centre, `occupied_xy` the ground footprint of every point the body occupies
    from the landing on (all frames, so a falling body never sweeps the weapon), `release_xy` where the weapon is let go. A place is a
    position of the grip centre on the ground plane at which no weapon point (seen from above) is nearer to the body's footprint than
    `clear * height`. The cost is the distance from the release point, plus a penalty for lying on the side the body falls toward (the
    body's mean footprint seen from the release point).
    """

    cell = 0.03 * height
    margin = 2.5 * height
    low = occupied_xy.min(axis=0) - margin
    high = occupied_xy.max(axis=0) + margin
    size = (int(np.ceil((high[0] - low[0]) / cell)) + 1, int(np.ceil((high[1] - low[1]) / cell)) + 1)
    distance = distance_grid(occupied_xy, low, size, cell)
    xs = low[0] + cell * np.arange(size[0])
    ys = low[1] + cell * np.arange(size[1])
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    travel = np.hypot(gx - release_xy[0], gy - release_xy[1])
    toward = occupied_xy.mean(axis=0) - release_xy
    norm = float(np.linalg.norm(toward))
    side = np.zeros_like(travel)
    if norm > 1e-9:
        side = np.maximum(0.0, ((gx - release_xy[0]) * toward[0] + (gy - release_xy[1]) * toward[1]) / norm)
    cost = travel + 0.5 * side
    sample = rest_relative[:: max(1, len(rest_relative) // 60)]
    places = []
    for index, rotation in enumerate(orientations):
        offsets = (sample @ np.asarray(rotation).T)[:, :2]
        worst = np.full(size, np.inf)
        for q in offsets:
            worst = np.minimum(worst, _shifted(distance, int(round(q[0] / cell)), int(round(q[1] / cell)), float(distance.max())))
        feasible = worst >= clear * height
        if not feasible.any():
            continue
        masked = np.where(feasible, cost, np.inf)
        i, j = np.unravel_index(int(np.argmin(masked)), masked.shape)
        places.append({"cost": float(masked[i, j]), "orientation": index, "xy": np.array([xs[i], ys[j]]), "clearance": float(worst[i, j])})
    places.sort(key=lambda row: row["cost"])
    return places[:keep]



def tumble_path(
    start_turn: np.ndarray,
    start_point: np.ndarray,
    land_turn: np.ndarray,
    land_point: np.ndarray,
    relative: np.ndarray,
    ground: float,
    frames: int,
    tumble: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """The weapon's world path from the frame it is let go: one (rotation, grip-centre position) per frame, `frames` of them.

    It leaves the hand with the hand's pose (`start_*`), crosses sideways at a steady speed and falls under gravity (height follows the
    square of the time), turning at a steady rate to the lying pose (`land_*`) in `tumble` frames, then stays exactly where it is.
    `relative` are the weapon's points relative to its grip centre. A frame in which a turning end would dip under `ground` is lifted until
    its lowest point touches it, so the weapon never goes below the ground plane.
    """

    axis, angle = G.rotation_axis_angle(np.asarray(start_turn).T @ np.asarray(land_turn))
    turns, points = [], []
    for k in range(frames):
        s = min(k / max(tumble, 1), 1.0)
        turn = np.asarray(start_turn) @ G.rodrigues(axis, angle * s)
        point = np.array(start_point, float) + (np.asarray(land_point, float) - start_point) * s
        point[2] = start_point[2] + (land_point[2] - start_point[2]) * s * s
        lowest = float((relative @ turn.T)[:, 2].min()) + point[2]
        if s < 1.0 and lowest < ground:
            point[2] += ground - lowest
        turns.append(turn)
        points.append(point)
    return np.stack(turns), np.stack(points)


def _drop_row(place: Dict[str, object], orientations: Sequence[np.ndarray], start: Tuple[np.ndarray, np.ndarray], relative: np.ndarray,
              judged: np.ndarray, body_frames: Sequence[np.ndarray], body_triangles: np.ndarray, height: float, ground: float,
              release: int, tumble: int) -> Dict[str, object]:
    """One resting place made into a world path and judged on it: the weapon inside the body, under the ground, and its clearance."""

    start_turn, start_point = start
    land_turn = orientations[place["orientation"]]
    lowest = float((relative @ land_turn.T)[:, 2].min())
    land_point = np.array([place["xy"][0], place["xy"][1], ground + GROUND_LIFT_SHARE * height - lowest])
    frames = len(body_frames) - release
    turns, points = tumble_path(start_turn, start_point, land_turn, land_point, relative, ground, frames, tumble)
    shares = [0.0]  # frame 0 is the weapon still in the hand (the clearance rule judged it)
    low = float((relative @ turns[0].T)[:, 2].min() + points[0][2])
    for k in range(1, frames):
        shares.append(deep_share(judged @ turns[k].T + points[k], body_frames[release + k], body_triangles, height, CLEAR_MARGIN_SHARE))
        low = min(low, float((relative @ turns[k].T)[:, 2].min() + points[k][2]))
    return {
        "turns": turns, "points": points, "land_point": land_point, "land_turn": land_turn, "clearance_share": place["clearance"] / height,
        "lowest_over_ground_share": (low - ground) / height, "in_body_share": max(shares), "in_body_frame": release + int(np.argmax(shares)),
        "cost": place["cost"], "release": release, "tumble_frames": tumble,
    }


GROUND_FAIL_SHARE = 0.002  # a dropped weapon this far under the ground fails the stage
GLB_MOVE_SHARE = 0.01  # a dropped weapon that moves this far after landing, in the stage's own GLB, is only a diagnostic


def drop_problems(row: Dict[str, object]) -> Tuple[List[str], List[str]]:
    """(problems that fail the grip stage, diagnostics) for one release clip's report row.

    The weapon inside the body or under the ground fails: both are the plan's own geometry and the exported files agree with it. How far it moves
    after landing does not. The stage measures the GLB with the lifts of its own body frames, and the exported unit differs (retarget, easing,
    the pipeline's grounding of each frame): the GLB said 11.9% of the height where the exported death held the weapon still but for three
    frames. The check on the exported files is the judge of stillness, so here it is a diagnostic."""

    problems, diagnostics = [], []
    if row["planned_weapon_inside_body_share"] > LIMIT:
        problems.append(f"weapon inside the body in frame {row['planned_weapon_inside_body_frame']} ({row['planned_weapon_inside_body_share']:.1%} of its points)")
    low = row["measured"]["lowest_point_over_ground_share"]
    if low < -GROUND_FAIL_SHARE:
        problems.append(f"weapon {-low:.1%} of the height under the ground")
    moved = row["measured"]["moved_after_landing_share"]
    if moved > GLB_MOVE_SHARE:
        diagnostics.append(f"on the GLB the weapon moves {moved:.1%} of the height after landing (not a failure here: the exported files are judged)")
    return problems, diagnostics


def plan_drop(
    rest: np.ndarray,
    centre: np.ndarray,
    axes: np.ndarray,
    attached: np.ndarray,
    body_frames: Sequence[np.ndarray],
    body_triangles: np.ndarray,
    height: float,
    ground: float,
    release: int,
    fps: float,
    candidates: int = 10,
) -> Dict[str, object]:
    """Plan the fall of a weapon let go at frame `release`: where it lands and its world pose in every frame from then on.

    `rest` are the weapon's points at rest (world, z up), `centre` its grip point, `axes` its head, blade and third directions (columns).
    `attached[i]` (4x4) carries a rest point to where the hand holds it in frame i. The body's posed vertices are `body_frames[i]`, `ground`
    the ground plane's height. The resting places come from `landing_places`, judged on everything the body occupies from the landing on;
    the `candidates` best are made into paths (`tumble_path`) and judged frame by frame, and the one with the weapon least inside the body,
    then least under the ground, then nearest the release point wins. Returns "turns" and "points" (the weapon's rotation and grip-centre
    position per frame from `release`), the landing pose and the numbers (weapon points inside the body, lowest point over the ground,
    clearance of the landing place from the body).
    """

    tumble = max(2, int(round(TUMBLE_SECONDS * fps)))
    relative = rest - centre
    sample = relative[:: max(1, len(relative) // 150)]
    start_turn = attached[release][:3, :3]
    start_point = attached[release][:3, :3] @ centre + attached[release][:3, 3]
    after = body_frames[min(release + tumble, len(body_frames) - 1) :]
    stride = max(1, int(sum(len(f) for f in after) // 1500))
    occupied = np.concatenate([f[::stride, :2] for f in after])
    orientations = lying_orientations(axes)
    places = landing_places(relative, orientations, occupied, start_point[:2], height, keep=candidates)
    if not places:
        raise ValueError("no resting place on the ground is clear of the body")
    judged = sample[np.linalg.norm(sample, axis=1) > GRIP_RADIUS_SHARE * height]
    best = None
    for rank, place in enumerate(places):
        row = _drop_row(place, orientations, (start_turn, start_point), relative, judged, body_frames, body_triangles, height, ground, release, tumble)
        key = (round(max(0.0, row["in_body_share"] - 0.003), 3), round(max(0.0, -row["lowest_over_ground_share"] - 0.002), 3), rank)
        if best is None or key < best[0]:
            best = (key, row)
    return best[1]


def local_pose(attached: np.ndarray, turn: np.ndarray, point: np.ndarray, centre: np.ndarray, bone_rest: np.ndarray) -> np.ndarray:
    """The pose-bone transform that puts the weapon in the world pose (`turn`, grip centre at `point`) while its parent moves by `attached`.

    The skinned weapon moves by `attached @ bone_rest @ basis @ inverse(bone_rest)` (`bone_rest` is the bone's rest matrix in the world), so the
    basis is `inverse(bone_rest) @ inverse(attached) @ world @ bone_rest`, with `world` the rigid motion of the rest points that
    turns them by `turn` about `centre` and puts `centre` at `point`.
    """

    world = np.eye(4)
    world[:3, :3] = turn
    world[:3, 3] = point - turn @ centre
    return np.linalg.inv(bone_rest) @ np.linalg.inv(attached) @ world @ bone_rest
