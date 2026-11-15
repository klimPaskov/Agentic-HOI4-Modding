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
    start = deep_share(weapon_points, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE)
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
            share = deep_share(moved, body_positions, body_triangles, height, CLEAR_MARGIN_SHARE)
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


def _clip_shares(free, pivots, vectors, body_frames, body_triangles, height, last):
    """The deep share per frame with each frame's rotation applied; frames from `last` on (the weapon let go) count 0."""

    out = []
    for i in range(len(free)):
        if i >= last:
            out.append(0.0)
            continue
        moved = (free[i] - pivots[i]) @ rotvec_matrix(vectors[i]).T + pivots[i]
        out.append(deep_share(moved, body_frames[i], body_triangles, height, CLEAR_MARGIN_SHARE))
    return out


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
    free = _clip_free_points(weapon_frames, pivots, height, rest_weapon, rest_grip)
    before = [deep_share(free[i], body_frames[i], body_triangles, height, CLEAR_MARGIN_SHARE) if i < last else 0.0 for i in range(count)]
    raw = np.zeros((count, 3))
    for i in range(last):
        if before[i] > target:
            raw[i], _left = solve_frame(free[i], pivots[i], body_frames[i], body_triangles, height, target, max_angle)
    rotvecs = smooth_rotations(_hold_neighbours(raw, last), radius=1)
    # from the release on the weapon is free: the hand's rotation fades out over the next frames, so it does not snap back
    if skip_from is not None and 0 < last < count:
        for k in range(count - last):
            rotvecs[last + k] = rotvecs[last - 1] * max(0.0, 1.0 - (k + 1) / 5.0)
    else:
        rotvecs[last:] = 0.0
    after = _clip_shares(free, pivots, rotvecs, body_frames, body_triangles, height, last)
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
        after = _clip_shares(free, pivots, rotvecs, body_frames, body_triangles, height, last)
    # What smoothing could not keep: a frame takes its own solved rotation (frames are independent, so it passes if its own solve did).
    for i in [i for i in range(last) if after[i] > limit]:
        if np.linalg.norm(raw[i]) > 0:
            rotvecs[i] = raw[i]
    after = _clip_shares(free, pivots, rotvecs, body_frames, body_triangles, height, last)
    failed = [i for i in range(last) if after[i] > limit]
    return {
        "rotvecs": rotvecs, "before": before, "after": after, "failed": failed,
        "max_degrees": float(np.degrees(np.linalg.norm(rotvecs, axis=1).max())) if count else 0.0,
        "frames_changed": int((np.linalg.norm(rotvecs, axis=1) > 1e-6).sum()),
    }


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
