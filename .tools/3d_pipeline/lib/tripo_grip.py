"""The maths of the grip stage (numpy only, no Blender): curl a hand around a haft and hold the arm up.

`tripo/grip_weapon.py` runs these inside Blender on a rigged Tripo body that has open, relaxed hands:

- `curl_chain` closes one finger (three joints) onto a haft, joint by joint, each until its phalanx touches
  the haft's surface and not a degree further.
- `solve_hold` finds constant rotation offsets of the weapon arm's joints that bring the hand to a recorded
  hold position with the haft pointing a recorded way.
- `finger_gaps` and `haft_radius` measure the result.

Points are (N, 3) arrays or 3-vectors. A haft is an infinite cylinder: a point on its axis, a direction, a radius.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

MAX_JOINT_DEGREES = (80.0, 100.0, 80.0)  # a finger's three joints: knuckle, middle, tip
THUMB_MAX_JOINT_DEGREES = (60.0, 80.0, 80.0)
SEGMENT_SAMPLES = 6


def unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, float)
    length = float(np.linalg.norm(vector))
    return vector / length if length > 1e-12 else vector


def rodrigues(axis: np.ndarray, angle: float) -> np.ndarray:
    """The rotation matrix of `angle` radians about the unit `axis`."""

    x, y, z = unit(axis)
    k = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + np.sin(angle) * k + (1.0 - np.cos(angle)) * (k @ k)


def rotate_about(points: np.ndarray, pivot: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    return (np.asarray(points, float) - pivot) @ rodrigues(axis, angle).T + pivot


def line_distance(points: np.ndarray, origin: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Distance of each point from the infinite line through `origin` along `direction`."""

    d = unit(direction)
    offset = np.asarray(points, float) - origin
    return np.linalg.norm(offset - np.outer(offset @ d, d), axis=-1)


def segment_points(chain: np.ndarray, samples: int = SEGMENT_SAMPLES) -> np.ndarray:
    """Points along every segment of a polyline, ends included."""

    steps = np.linspace(0.0, 1.0, samples)[:, None]
    return np.concatenate([chain[i] + steps * (chain[i + 1] - chain[i]) for i in range(len(chain) - 1)])


def haft_radius(vertices: np.ndarray, origin: np.ndarray, direction: np.ndarray, centre_along: float, window: float) -> float:
    """The haft's radius near the grip: the median distance from the axis of vertices within `window` along it."""

    d = unit(direction)
    along = (vertices - origin) @ d
    near = vertices[np.abs(along - centre_along) <= window]
    if len(near) < 8:
        raise ValueError("too few weapon vertices near the grip point to measure the haft")
    return float(np.median(line_distance(near, origin, d)))


def contact_angle(
    chain: np.ndarray,
    axis: np.ndarray,
    haft_point: np.ndarray,
    haft_direction: np.ndarray,
    clearance: float,
    max_degrees: float,
    step_degrees: float = 0.25,
) -> Tuple[float, str]:
    """How far to turn `chain` (joint, then every point beyond it) about `axis` through the joint.

    The result is the largest angle in [0, max_degrees], in radians, at which no point of the chain's
    segments is closer than `clearance` to the haft's axis, so the finger touches the haft's surface and
    does not enter it. Returns (angle, why): "contact", "open" (the limit came first) or "inside" (the chain
    already was closer than `clearance` at angle 0, so it cannot turn).
    """

    pivot = chain[0]
    axis = unit(axis)

    def nearest(angle: float) -> float:
        turned = rotate_about(chain, pivot, axis, angle)
        return float(line_distance(segment_points(turned), haft_point, haft_direction).min())

    if nearest(0.0) < clearance:
        return 0.0, "inside"
    last = 0.0
    for degrees in np.arange(step_degrees, max_degrees + step_degrees / 2, step_degrees):
        angle = np.radians(degrees)
        if nearest(angle) < clearance:
            return last, "contact"
        last = angle
    return last, "open"


def curl_chain(
    joints: np.ndarray,
    haft_point: np.ndarray,
    haft_direction: np.ndarray,
    haft_radius_value: float,
    finger_radius: Sequence[float],
    limits_degrees: Sequence[float] = MAX_JOINT_DEGREES,
    extra_clearance: float = 0.0,
    toward: Optional[np.ndarray] = None,
) -> Dict[str, object]:
    """Close a finger onto a haft, joint by joint from the knuckle to the tip.

    `joints` is (4, 3): the three joint positions and the tip. For each joint the hinge axis is the one that
    swings the rest of the finger toward the haft (the axis perpendicular to the segment and to the line from
    the joint to its nearest point on the haft's axis, or toward `toward` when given), and the finger turns
    until its segment capsule touches the haft (`contact_angle`). Returns the joint positions after the
    curl, each joint's world axis and angle, and why each stopped.
    """

    chain = np.array(joints, float)
    result = {"axes": [], "angles": [], "why": []}
    for i in range(3):
        segment = unit(chain[i + 1] - chain[i])
        middle = 0.5 * (chain[i] + chain[i + 1]) if toward is None else toward
        foot = haft_point + unit(haft_direction) * float((middle - haft_point) @ unit(haft_direction))
        aim = unit(foot - chain[i])
        axis = np.cross(segment, aim)
        if np.linalg.norm(axis) < 1e-9:
            result["axes"].append(np.zeros(3))
            result["angles"].append(0.0)
            result["why"].append("aligned")
            continue
        axis = unit(axis)
        touch = haft_radius_value + finger_radius[i]
        # `extra_clearance` (the thumb's room for the fingers under it) only applies while the joint starts
        # farther from the haft than that; otherwise the joint simply closes to the haft's surface.
        start = float(line_distance(segment_points(chain[i:]), haft_point, haft_direction).min())
        clearance = touch + extra_clearance if start >= touch + extra_clearance else touch
        angle, why = contact_angle(chain[i:], axis, haft_point, haft_direction, clearance, limits_degrees[i])
        chain[i:] = rotate_about(chain[i:], chain[i], axis, angle)
        result["axes"].append(axis)
        result["angles"].append(float(angle))
        result["why"].append(why)
    result["joints"] = chain
    return result


def finger_gaps(points_by_finger: Dict[str, np.ndarray], tips: Dict[str, np.ndarray], haft_point: np.ndarray, haft_direction: np.ndarray, radius: float, zone: float) -> Dict[str, dict]:
    """How each finger sits on the haft: the deepest it goes into it and how far its tip is from the surface.

    `points_by_finger` are the finger's skin vertices; only those within `zone` along the haft of the grip
    point count. A negative `deepest` is penetration (the surface is `-deepest` inside the haft); `tip_gap`
    is the distance from the finger's tip vertices to the surface.
    """

    d = unit(haft_direction)
    report = {}
    for name, points in points_by_finger.items():
        near = points[np.abs((points - haft_point) @ d) <= zone]
        if not len(near):
            report[name] = {"deepest": None, "tip_gap": None, "vertices": 0}
            continue
        gaps = line_distance(near, haft_point, d) - radius
        tip = tips[name]
        tip_gap = float(line_distance(tip[None, :], haft_point, d)[0] - radius)
        report[name] = {"deepest": float(gaps.min()), "tip_gap": tip_gap, "vertices": int(len(near))}
    return report


def solve_hold(
    forward: Callable[[np.ndarray], Tuple[np.ndarray, np.ndarray]],
    starts: Sequence[np.ndarray],
    target_position: np.ndarray,
    target_direction: np.ndarray,
    scale: float,
    ridge: float = 0.02,
    iterations: int = 60,
) -> Dict[str, object]:
    """Find rotation parameters that bring a hand to a target position with a haft pointing a target way.

    `forward(params)` returns the hand position and the haft direction for a parameter vector (rotation
    vectors of the arm's joints, in the order the caller chose). The least squares is a damped
    Gauss-Newton with a ridge on the parameters, so the smallest rotation that does it wins. Every start in
    `starts` is tried and the cheapest result kept. Residuals: position error over `scale`, and the haft
    direction error.
    """

    target_direction = unit(target_direction)

    def residual(params: np.ndarray) -> np.ndarray:
        position, direction = forward(params)
        return np.concatenate([(position - target_position) / scale, unit(direction) - target_direction])

    best = None
    for start in starts:
        params = np.array(start, float)
        damping = 1e-2
        current = residual(params)
        cost = float(current @ current + ridge * params @ params)
        for _ in range(iterations):
            jacobian = np.empty((len(current), len(params)))
            for k in range(len(params)):
                step = np.zeros_like(params)
                step[k] = 1e-4
                jacobian[:, k] = (residual(params + step) - current) / 1e-4
            gradient = jacobian.T @ current + ridge * params
            hessian = jacobian.T @ jacobian + ridge * np.eye(len(params))
            improved = False
            for _try in range(8):
                update = np.linalg.solve(hessian + damping * np.eye(len(params)), gradient)
                trial = params - update
                trial_residual = residual(trial)
                trial_cost = float(trial_residual @ trial_residual + ridge * trial @ trial)
                if trial_cost < cost:
                    params, current, cost, improved = trial, trial_residual, trial_cost, True
                    damping = max(damping / 3.0, 1e-6)
                    break
                damping *= 4.0
            if not improved or float(np.linalg.norm(update)) < 1e-7:
                break
        if best is None or cost < best["cost"]:
            best = {"params": params, "cost": cost, "residual": current}
    position, direction = forward(best["params"])
    best["position_error"] = float(np.linalg.norm(position - target_position))
    best["direction_error_degrees"] = float(np.degrees(np.arccos(np.clip(unit(direction) @ target_direction, -1.0, 1.0))))
    return best


def contact_angle_points(
    points: np.ndarray,
    pivot: np.ndarray,
    axis: np.ndarray,
    haft_point: np.ndarray,
    haft_direction: np.ndarray,
    clearance: float,
    max_degrees: float,
    step_degrees: float = 0.5,
) -> Tuple[float, str]:
    """`contact_angle` for a cloud of skin points turned about `axis` through `pivot`."""

    axis = unit(axis)

    def nearest(angle: float) -> float:
        return float(line_distance(rotate_about(points, pivot, axis, angle), haft_point, haft_direction).min())

    if nearest(0.0) < clearance:
        return 0.0, "inside"
    last = 0.0
    for degrees in np.arange(step_degrees, max_degrees + step_degrees / 2, step_degrees):
        angle = np.radians(degrees)
        if nearest(angle) < clearance:
            return last, "contact"
        last = angle
    return last, "open"


def curl_skin(
    joints: np.ndarray,
    skin: np.ndarray,
    level: np.ndarray,
    haft_point: np.ndarray,
    haft_direction: np.ndarray,
    haft_radius_value: float,
    limits_degrees: Sequence[float] = MAX_JOINT_DEGREES,
    extra_clearance: float = 0.0,
) -> Dict[str, object]:
    """Close a finger onto a haft, judged on its skin: each joint turns until a skin point touches the haft.

    `joints` is (4, 3): the pivots of the knuckle, middle and tip joints and the tip bone's head. `skin` is
    the finger's vertices and `level` (0 to 3) the bone each follows (a vertex of level k moves with the
    turns of joints 0..min(k, 2); level 3 is the tip bone). Joint i turns the vertices of level >= i about the
    axis that swings them toward the haft, until the nearest of them reaches the haft's surface (plus
    `extra_clearance` while the finger starts farther out than that). The joints go knuckle first, so the
    knuckle bends the whole finger until its skin meets the haft, then the middle joint bends what is beyond
    it, then the tip joint.
    """

    joints = np.array(joints, float)
    skin = np.array(skin, float)
    out = {"axes": [], "angles": [], "why": []}
    d = unit(haft_direction)
    for i in range(3):
        mover = level >= i
        if not mover.any():
            out["axes"].append(np.zeros(3))
            out["angles"].append(0.0)
            out["why"].append("no skin")
            continue
        centroid = skin[mover].mean(axis=0)
        foot = haft_point + d * float((centroid - haft_point) @ d)
        aim = unit(foot - joints[i])
        segment = unit(joints[i + 1] - joints[i])
        axis = np.cross(segment, aim)
        if np.linalg.norm(axis) < 1e-6:
            axis = np.cross(centroid - joints[i], aim)
        if np.linalg.norm(axis) < 1e-9:
            out["axes"].append(np.zeros(3))
            out["angles"].append(0.0)
            out["why"].append("aligned")
            continue
        axis = unit(axis)
        start = float(line_distance(skin[mover], haft_point, d).min())
        touch = haft_radius_value
        clearance = touch + extra_clearance if start >= touch + extra_clearance else touch
        angle, why = contact_angle_points(skin[mover], joints[i], axis, haft_point, d, clearance, limits_degrees[i])
        skin[mover] = rotate_about(skin[mover], joints[i], axis, angle)
        joints[i + 1 :] = rotate_about(joints[i + 1 :], joints[i], axis, angle)
        out["axes"].append(axis)
        out["angles"].append(float(angle))
        out["why"].append(why)
    out["joints"] = joints
    out["skin"] = skin
    return out


# ---- a power grip: the fingers wrap the haft, the thumb closes from the other side ---------------------
#
# A broom-handle grip: the haft lies diagonally across the palm, from the base of the little finger to the web
# between thumb and index finger. All four fingers wrap around it, the curl spread over all three joints. The
# thumb closes from the opposite side, round the haft and over the middle segments of the index and middle
# fingers. `grip_weapon.py` searches the place of the haft with `solve_finger` (a curl profile fitted to the
# radius of the haft) and then closes the thumb with `solve_thumb`.

FINGER_PROFILE_DEGREES = (70.0, 90.0, 50.0)  # knuckle, middle, tip: what a hand does on a broom handle
FINGER_RANGE_DEGREES = ((30.0, 90.0), (40.0, 110.0), (10.0, 70.0))


def apply_chain(joints: np.ndarray, skin: np.ndarray, level: np.ndarray, rotations: Sequence[Tuple[np.ndarray, float]]):
    """Turn the three joints of a finger in order. `rotations[i]` is (world axis, radians) about joint i, where it is now.

    Skin of level >= i follows joint i (level 0 is the proximal bone, 3 the tip bone). Returns the new joint
    positions (4, 3) and skin.
    """

    joints = np.array(joints, float)
    skin = np.array(skin, float)
    for i, (axis, angle) in enumerate(rotations):
        if angle == 0.0 or np.linalg.norm(axis) < 1e-12:
            continue
        mover = level >= i
        skin[mover] = rotate_about(skin[mover], joints[i], axis, angle)
        joints[i + 1 :] = rotate_about(joints[i + 1 :], joints[i], axis, angle)
    return joints, skin


def signed_gaps(skin: np.ndarray, haft_point: np.ndarray, haft_direction: np.ndarray, radius: float) -> np.ndarray:
    """Distance of each skin point from the surface of the haft: negative inside it."""

    return line_distance(skin, haft_point, haft_direction) - radius


def wrap_cost(skin: np.ndarray, level: np.ndarray, haft_point: np.ndarray, haft_direction: np.ndarray, radius: float, tolerance: float) -> float:
    """How badly a posed finger fails to wrap the haft: the gap of each bone nearest skin, and the depth inside the haft."""

    gap = signed_gaps(skin, haft_point, haft_direction, radius)
    cost = 20.0 * float(np.maximum(-gap - tolerance, 0.0).max())
    for bone, weight in ((0, 0.3), (1, 1.0), (2, 1.0), (3, 1.0)):
        mask = level == bone
        if mask.any():
            cost += 4.0 * weight * max(float(gap[mask].min()), 0.0)
    return cost


def curl_axis_candidates(closing: np.ndarray, haft_direction: np.ndarray, toward_palm: np.ndarray, joints: np.ndarray) -> List[np.ndarray]:
    """Axes a finger can bend about: along the haft, across the hand, and between. Each is signed to bend toward the palm."""

    tip = joints[3]
    out = []
    for raw in (haft_direction, closing, unit(haft_direction) + unit(closing), unit(haft_direction) - unit(closing)):
        axis = unit(raw)
        moved = rotate_about(tip[None, :], joints[0], axis, np.radians(20.0))[0]
        out.append(axis if float((moved - tip) @ toward_palm) > 0.0 else -axis)
    return out


def solve_finger(
    joints: np.ndarray,
    skin: np.ndarray,
    level: np.ndarray,
    haft_point: np.ndarray,
    haft_direction: np.ndarray,
    radius: float,
    closing: np.ndarray,
    toward_palm: np.ndarray,
    tolerance: float,
    profile: Sequence[float] = FINGER_PROFILE_DEGREES,
    ranges: Sequence[Sequence[float]] = FINGER_RANGE_DEGREES,
    step: float = 10.0,
) -> Dict[str, object]:
    """Wrap one finger round the haft with all three joints bent, close to `profile` degrees each.

    Searches the joint angles on a grid over `ranges` (then refines in 2.5 degree steps) and the axis the joints
    bend about. The cost is `wrap_cost` plus a small pull toward the profile, so the fingertip and the middle
    segments lie on the haft and nothing goes deeper into it than `tolerance`.
    """

    best = None

    def total(angles, axis):
        rotations = [(axis, float(np.radians(a))) for a in angles]
        _j, posed = apply_chain(joints, skin, level, rotations)
        prior = 0.002 * sum(((a - p) / 30.0) ** 2 for a, p in zip(angles, profile))
        return wrap_cost(posed, level, haft_point, haft_direction, radius, tolerance) + prior

    for axis in curl_axis_candidates(closing, haft_direction, toward_palm, joints):
        grids = [np.arange(lo, hi + 1e-6, step) for lo, hi in ranges]
        for a0 in grids[0]:
            for a1 in grids[1]:
                for a2 in grids[2]:
                    cost = total((a0, a1, a2), axis)
                    if best is None or cost < best[0]:
                        best = (cost, (a0, a1, a2), axis)
    cost, angles, axis = best
    angles = list(angles)
    for _round in range(3):
        for i in range(3):
            for delta in (-2.5, 2.5):
                trial = list(angles)
                trial[i] = min(max(trial[i] + delta, ranges[i][0]), ranges[i][1])
                c = total(trial, axis)
                if c < cost:
                    cost, angles = c, trial
    rotations = [(axis, float(np.radians(a))) for a in angles]
    posed_joints, posed_skin = apply_chain(joints, skin, level, rotations)
    return {"cost": float(cost), "angles": [float(np.radians(a)) for a in angles], "axes": [axis, axis, axis], "joints": posed_joints, "skin": posed_skin}


def radial_angle(point: np.ndarray, haft_point: np.ndarray, haft_direction: np.ndarray, reference: np.ndarray) -> float:
    """Degrees (-180 to 180) of `point` around the axis of the haft, measured from `reference` (made perpendicular to the axis)."""

    d = unit(haft_direction)
    base = unit(reference - (reference @ d) * d)
    offset = np.asarray(point, float) - haft_point
    radial = offset - (offset @ d) * d
    side = np.cross(d, base)
    return float(np.degrees(np.arctan2(radial @ side, radial @ base)))


def opposite_sides(finger_points: Sequence[np.ndarray], thumb_point: np.ndarray, haft_point: np.ndarray, haft_direction: np.ndarray) -> float:
    """Degrees between the side of the haft the thumb is on and the side the fingers are on (180 is exactly opposite)."""

    d = unit(haft_direction)

    def radial(p):
        offset = np.asarray(p, float) - haft_point
        return unit(offset - (offset @ d) * d)

    fingers = unit(np.mean([radial(p) for p in finger_points], axis=0))
    return float(np.degrees(np.arccos(np.clip(fingers @ radial(thumb_point), -1.0, 1.0))))


def thumb_rotations(params: np.ndarray, limits_degrees: Sequence[float]) -> List[Tuple[np.ndarray, float]]:
    """A parameter vector (three rotation vectors, radians) as (axis, angle) per joint, each angle clipped to its limit."""

    out = []
    for i in range(3):
        vector = np.asarray(params[3 * i : 3 * i + 3], float)
        angle = float(np.linalg.norm(vector))
        if angle < 1e-12:
            out.append((np.array([0.0, 0.0, 1.0]), 0.0))
            continue
        out.append((vector / angle, min(angle, float(np.radians(limits_degrees[i])))))
    return out


def radial_unit(point: np.ndarray, haft_point: np.ndarray, haft_direction: np.ndarray) -> np.ndarray:
    """Unit vector from the axis of the haft to `point`, perpendicular to the axis."""

    d = unit(haft_direction)
    offset = np.asarray(point, float) - haft_point
    return unit(offset - (offset @ d) * d)


def thumb_cost(skin, level, haft_point, haft_direction, radius, finger_skin: np.ndarray, tolerance: float,
               target_skin: Optional[np.ndarray] = None, away_from: Optional[np.ndarray] = None) -> float:
    """Fit of the thumb: the pad (outer two bones) on the haft, the tip on `target_skin` (the middle segments of
    the index and middle fingers), the tip on the side of the haft away from `away_from` (the side of the
    fingertips), nothing inside the haft and nothing through the fingers (`finger_skin`).
    """

    gap = signed_gaps(skin, haft_point, haft_direction, radius)
    cost = 40.0 * float(np.maximum(-gap - 0.0003, 0.0).max())  # no part of the thumb inside the haft
    top = int(level.max())
    pad = level >= max(top - 1, 0)  # the outer two bones that have skin
    if pad.any():
        cost += 4.0 * max(float(gap[pad].min()), 0.0)
    tip = level == top
    target = finger_skin if target_skin is None else target_skin
    if len(target) and tip.any():
        diff = skin[tip][:, None, :] - target[None, :, :]
        nearest = np.sqrt((diff * diff).sum(axis=2)).min(axis=1)
        cost += 4.0 * max(float(nearest.min()) - tolerance, 0.0)
    if len(finger_skin):
        sample = skin[:: max(1, len(skin) // 80)]
        diff = sample[:, None, :] - finger_skin[None, :, :]
        nearest = np.sqrt((diff * diff).sum(axis=2)).min(axis=1)
        cost += 10.0 * float(np.maximum(0.0008 - nearest, 0.0).max())  # not through the fingers either
    if away_from is not None and tip.any():
        side = radial_unit(skin[tip].mean(axis=0), haft_point, haft_direction)
        cost += 0.08 * 0.5 * (1.0 + float(side @ unit(away_from)))  # 0 when exactly opposite, 0.08 on the fingertips' side
    return cost


def solve_thumb(
    joints: np.ndarray,
    skin: np.ndarray,
    level: np.ndarray,
    haft_point: np.ndarray,
    haft_direction: np.ndarray,
    radius: float,
    finger_skin: np.ndarray,
    limits_degrees: Sequence[float] = (90.0, 90.0, 80.0),
    tolerance: float = 0.003,
    target_skin: Optional[np.ndarray] = None,
    away_from: Optional[np.ndarray] = None,
    seed: int = 7,
    starts: int = 600,
    refine: int = 2500,
) -> Dict[str, object]:
    """Close the thumb round the haft from the side opposite the fingers: random starts, then a shrinking random search.

    The first joint turns about any axis (opposition: toward the palm and across), the other two bend after it.
    Returns the (axis, angle) per joint and the posed skin and joints.
    """

    rng = np.random.default_rng(seed)

    def evaluate(params):
        rotations = thumb_rotations(params, limits_degrees)
        posed_joints, posed = apply_chain(joints, skin, level, rotations)
        return thumb_cost(posed, level, haft_point, haft_direction, radius, finger_skin, tolerance, target_skin, away_from), rotations, posed_joints, posed

    limit = np.radians(np.repeat(np.asarray(limits_degrees, float), 3))
    best_params, best_cost = np.zeros(9), evaluate(np.zeros(9))[0]
    for _ in range(starts):
        trial = rng.uniform(-1.0, 1.0, 9) * limit
        cost = evaluate(trial)[0]
        if cost < best_cost:
            best_params, best_cost = trial, cost
    scale = 0.3
    for iteration in range(refine):
        trial = best_params + rng.normal(0.0, scale, 9) * limit * 0.3
        cost = evaluate(trial)[0]
        if cost < best_cost:
            best_params, best_cost = trial, cost
        if iteration % 500 == 499:
            scale *= 0.5
    cost, rotations, posed_joints, posed = evaluate(best_params)
    return {"cost": float(cost), "rotations": rotations, "angles": [a for _axis, a in rotations], "axes": [axis for axis, _a in rotations], "joints": posed_joints, "skin": posed}


# ---- a weapon that falls by turning about a pivot ----------------------------------------------------
#
# The kit's animation import keeps rotation keys for every bone but the root (a bone's own location keys are
# dropped), so the weapon bone cannot slide away from the hand. A rotation about a pivot far enough from the
# weapon moves it all the same: `pivot_for_motion` finds the pivot (a static point in the hand's frame, where
# the weapon bone sits) and the axis of the turn that carries the weapon from its place in the hand to a
# given place on the ground.


def rotation_axis_angle(matrix: np.ndarray) -> Tuple[np.ndarray, float]:
    """The unit axis and the angle (0 to pi) of a rotation matrix. The identity has no axis: (z, 0)."""

    matrix = np.asarray(matrix, float)
    cosine = float(np.clip((np.trace(matrix) - 1.0) / 2.0, -1.0, 1.0))
    angle = float(np.arccos(cosine))
    if angle < 1e-9:
        return np.array([0.0, 0.0, 1.0]), 0.0
    if angle > np.pi - 1e-6:
        values, vectors = np.linalg.eigh((matrix + matrix.T) / 2.0 + np.eye(3))  # a half turn is 2 n nT - I: R + I is 2 n nT
        return unit(vectors[:, int(np.argmax(values))]), angle
    axis = np.array([matrix[2, 1] - matrix[1, 2], matrix[0, 2] - matrix[2, 0], matrix[1, 0] - matrix[0, 1]])
    return unit(axis), angle


def pivot_for_motion(rotation: np.ndarray, translation: np.ndarray, near: np.ndarray) -> Optional[np.ndarray]:
    """A point P with `rotation @ (x - P) + P == rotation @ x + translation` for every x, nearest to `near`, or None.

    A turn about an axis through P moves the points by `(I - R) P`: only translations perpendicular to the axis
    can be had. A translation with a component along the axis (more than 1e-6) has no pivot.
    """

    axis, angle = rotation_axis_angle(rotation)
    if angle < 1e-6:
        return None
    if abs(float(np.asarray(translation, float) @ axis)) > 1e-6:
        return None
    solution, *_ = np.linalg.lstsq(np.eye(3) - np.asarray(rotation, float), np.asarray(translation, float), rcond=None)
    along = float((np.asarray(near, float) - solution) @ axis)
    return solution + along * axis
