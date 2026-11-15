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

MARGIN_SHARE = 0.01  # a weapon point counts as through the body when this deep (share of the body height), as in TRIPO-WEAPON-IN-BODY
CHECK_LIMIT = 0.01  # the check's limit: share of the weapon's free points
LIMIT = 0.006  # what a solved clip must stay under: a margin for the baked keys, the eased snaps and the check's own sampling
TARGET = 0.0015  # what each frame's solve aims for
GRIP_RADIUS_SHARE = 0.12  # points this near the hand joint are the grip and are not judged
MAX_ANGLE_DEGREES = 60.0
ANGLES_DEGREES = (4.0, 8.0, 12.0, 17.0, 23.0, 30.0, 38.0, 46.0, 53.0, 60.0)
HOLD_FRAMES = 4  # a solved frame's rotation fades out over this many frames either side, so smoothing does not dilute it
MAX_POINTS = 600


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


def deep_share(points: np.ndarray, body_positions: np.ndarray, body_triangles: np.ndarray, height: float, margin: float = MARGIN_SHARE) -> float:
    """Share of `points` inside the body (ray parity) and deeper than `margin` of `height` from its nearest vertex."""

    if not len(points):
        return 0.0
    cc = _clip_check()
    low, high = body_positions.min(axis=0), body_positions.max(axis=0)
    near = np.all((points >= low) & (points <= high), axis=1)
    if not near.any():
        return 0.0
    inside = np.zeros(len(points), dtype=bool)
    inside[near] = cc.points_inside_mesh(points[near], body_positions[body_triangles])
    if not inside.any():
        return 0.0
    depth = cc.nearest_vertex_distance(points[inside], body_positions) / height
    return float((depth > margin).sum()) / len(points)


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
) -> Tuple[np.ndarray, float]:
    """The smallest rotation about `pivot` (a rotation vector, radians) that brings the weapon's deep share to `target` or less, and the share left.

    `weapon_points` are the free points (outside the grip zone). Angles are tried in increasing order, every axis at each; the first angle at
    which some axis meets the target wins (the axis with the smallest share at that angle). With none, the best found within `max_angle`.
    """

    axes = fibonacci_axes() if axes is None else axes
    start = deep_share(weapon_points, body_positions, body_triangles, height)
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
            share = deep_share(moved, body_positions, body_triangles, height)
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
) -> Dict[str, object]:
    """Solve a whole clip. Per frame i: `weapon_frames[i]` (all weapon points), `pivots[i]` (the wrist joint), `body_frames[i]` (the body's posed vertices).

    Frames from `skip_from` on (the weapon has been let go) are left alone. Returns the rotation vector per frame ("rotvecs"), the deep share
    per frame before and after, the frames still over `limit` ("failed") and the largest angle used in degrees.
    """

    count = len(weapon_frames)
    last = count if skip_from is None else min(skip_from, count)
    if rest_weapon is not None and rest_grip is not None:
        # the check's own choice: the points evenly sampled from the weapon, those outside the grip zone around the grip point at REST
        indices = np.linspace(0, len(rest_weapon) - 1, min(MAX_POINTS, len(rest_weapon))).astype(int)
        keep = indices[np.linalg.norm(np.asarray(rest_weapon)[indices] - rest_grip, axis=1) > GRIP_RADIUS_SHARE * height]
        free = [np.asarray(weapon_frames[i])[keep] for i in range(count)]
    else:
        free = [free_points(weapon_frames[i], pivots[i], height) for i in range(count)]
    before = [deep_share(free[i], body_frames[i], body_triangles, height) if i < last else 0.0 for i in range(count)]
    raw = np.zeros((count, 3))
    for i in range(last):
        if before[i] > target:
            raw[i], _left = solve_frame(free[i], pivots[i], body_frames[i], body_triangles, height, target, max_angle)
    # the frames around a solved one hold its rotation, fading out, where they have none of their own: the smoothing then leaves it nearly whole
    held = raw.copy()
    for i in range(last):
        if np.linalg.norm(raw[i]) > 0:
            for k in range(1, HOLD_FRAMES + 1):
                for j in (i - k, i + k):
                    if 0 <= j < last and np.linalg.norm(held[j]) < np.linalg.norm(raw[i]) * (1 - k / (HOLD_FRAMES + 1)):
                        held[j] = raw[i] * (1 - k / (HOLD_FRAMES + 1))
    rotvecs = smooth_rotations(held, radius=1)
    # from the release on the weapon is free: the hand's rotation fades out over the next frames, so it does not snap back
    if skip_from is not None and 0 < last < count:
        for k in range(count - last):
            rotvecs[last + k] = rotvecs[last - 1] * max(0.0, 1.0 - (k + 1) / 5.0)
    else:
        rotvecs[last:] = 0.0

    def shares(vectors):
        out = []
        for i in range(count):
            if i >= last:
                out.append(0.0)
                continue
            moved = (free[i] - pivots[i]) @ rotvec_matrix(vectors[i]).T + pivots[i]
            out.append(deep_share(moved, body_frames[i], body_triangles, height))
        return out

    after = shares(rotvecs)
    cap = np.radians(max_angle)
    for _ in range(rounds):
        over = [i for i in range(last) if after[i] > limit]
        if not over:
            break
        for i in over:
            # smoothing took away some of what the frame needed: ask for what its own solve found, a quarter more
            rotvecs[i] = raw[i] if np.linalg.norm(raw[i]) > 0 else rotvecs[i] * 1.25
            size = float(np.linalg.norm(rotvecs[i]))
            if size > cap:
                rotvecs[i] *= cap / size
        rotvecs = smooth_rotations(rotvecs, radius=1)
        after = shares(rotvecs)
    # What smoothing could not keep: a frame takes its own solved rotation (frames are independent, so it passes if its own solve did).
    for i in [i for i in range(last) if after[i] > limit]:
        if np.linalg.norm(raw[i]) > 0:
            rotvecs[i] = raw[i]
    after = shares(rotvecs)
    failed = [i for i in range(last) if after[i] > limit]
    return {
        "rotvecs": rotvecs, "before": before, "after": after, "failed": failed,
        "max_degrees": float(np.degrees(np.linalg.norm(rotvecs, axis=1).max())) if count else 0.0,
        "frames_changed": int((np.linalg.norm(rotvecs, axis=1) > 1e-6).sum()),
    }
