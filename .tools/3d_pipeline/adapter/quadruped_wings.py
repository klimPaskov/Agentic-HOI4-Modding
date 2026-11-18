"""Find a winged quadruped's wings by rule, lay their bones out and weight them.

Pure numpy, no Blender: `quadruped_rig.author_rig` calls it inside Blender and the unit tests run it on synthetic meshes. Coordinates are
the working frame of `quadruped_layout.py` (+Z up, the animal facing -Y, its left side toward +X) unless a function says otherwise.

A dragon from Tripo is one skin: four legs, a long neck and tail, and two membrane wings grown from the shoulders. The rules:

1. Feet. The ground contacts (`quadruped_layout.ground_contacts`) are pieces of the surface under 7% of the height, joined in plan. A
   piece longer than `quadruped_layout.CONTACT_ELONGATION` times its width is a tail lying on the ground, not a foot. The four feet set
   the body's long axis (front pair to rear pair), so a model whose spread wings are wider than it is long is turned the right way.
2. Torso width. The farthest reach of the feet from the mid-plane, each foot's own half-width included: the body above the legs is no
   wider than the legs stand.
3. Wing. Surface farther from the mid-plane than `WING_REACH` times that width, joined along the mesh to such surface above the
   belly, on each side. The tail curls sideways on the ground and joins none of it, the horns and claws do not reach that far.
4. Root. Where the wing meets the body: the wing's vertices joined to skin that is not wing. The wing turns about the front of that line
   (`ROOT_FRONT_SHARE` of it, the shoulder), and the rest of it blends into the body.
5. Chains. A fan round the root in the wing's own plane (its two longest principal axes): the angle `u` from the plane's first axis and
   the distance `s` from the root. `chains` chains of `bones` bones each, at even angles over the wing's spread, the top chain moved
   onto the leading edge (the arm). Each chain's bones run from the root out along the fan, through the median of their band of the
   wing (`chain_joints`).
6. Weights. Two neighbouring chains (linear in `u`) times two bones (linear in `s` between the bones' middles): at most four bones, as
   the humanoid wing chains do (`lib/tripo_chains.sheet_weights`). The wing's weights blend into the body's own over
   `ROOT_BLEND_SHARE` of the wing's length (surface distance from the body), so the root bends where a wing bends.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import quadruped_ears as qears
from quadruped_layout import wing_name as ql_wing_name

SIDES = (("Left", 1.0), ("Right", -1.0))
WING_PREFIX = "Wing"  # lib/tripo_chains.REGION_PREFIX["wings"]: the weight smoothing locks these bones, the checks find the wing by them
# A wing reaches farther from the mid-plane than the legs stand by this share (on the dragon the body's widest point, the shoulders above
# the forelegs, is 0.93 of the feet's reach, and the wing root 1.0 to 1.3 of it).
WING_REACH = 1.15
WING_MIN_SHARE = 0.02  # of the model's vertices: a smaller piece is a spike or a claw, not a wing
ROOT_FRONT_SHARE = 0.25  # the wing turns about the front quarter of its root line, the shoulder
ROOT_BLEND_SHARE = 0.10  # of the wing's length: the wing's weights rise from the body's over this surface distance
LEAD_PERCENTILE = 92.0  # the leading edge's angle in the fan, over the wing's outer half (lib/tripo_chains.LEADING_EDGE_PERCENTILE is 90)
WING_CHAINS = 3
WING_BONES = 3


def wing_name(side: str, chain: int, bone: int) -> str:
    return ql_wing_name(side, chain, bone)


def unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, float)
    return vector / max(float(np.linalg.norm(vector)), 1e-12)


def feet_reach(contacts: Sequence[np.ndarray], cx: float) -> float:
    """The torso's half-width: the farthest any foot's points reach from the mid-plane (each foot's 98th percentile)."""

    return max(float(np.percentile(np.abs(points[:, 0] - cx), 98)) for points in contacts)


def wing_masks(points: np.ndarray, triangles: np.ndarray, landmarks: Dict[str, object], contacts: Sequence[np.ndarray]) -> Dict[str, np.ndarray]:
    """Per side, the wing's vertices (every copy of a welded vertex). Empty when the model has no wing."""

    ground = float(landmarks["ground_offset"])
    height = float(landmarks["height"])
    cx = float(landmarks["centre_x"])
    p = np.asarray(points, float) - np.array([0.0, 0.0, ground])
    canon = qears.weld(p, 1e-6 * height)
    edges = qears.welded_edges(np.asarray(triangles, int), canon)
    reach = WING_REACH * feet_reach([np.asarray(c, float) - np.array([0.0, 0.0, ground]) for c in contacts], cx)
    out: Dict[str, np.ndarray] = {}
    for side, sign in SIDES:
        far = ((p[:, 0] - cx) * sign > reach) & (canon == np.arange(len(p)))
        labels = qears.components(len(p), edges, far)
        mask = np.zeros(len(p), bool)
        for label in np.unique(labels[labels >= 0]):
            piece = labels == label
            if piece.sum() >= WING_MIN_SHARE * len(p) and float(p[piece, 2].max()) > float(landmarks["belly_z"]):
                mask |= piece
        if mask.any():
            out[side] = mask[canon]
    return out


def principal_axes(points: np.ndarray) -> np.ndarray:
    centred = points - points.mean(axis=0)
    values, vectors = np.linalg.eigh(np.cov(centred.T))
    return vectors[:, np.argsort(values)[::-1]].T


def root_line(points: np.ndarray, triangles: np.ndarray, mask: np.ndarray, height: float) -> np.ndarray:
    """The wing's vertices joined to skin that is not wing (welded), as an index array."""

    canon = qears.weld(points, 1e-6 * height)
    edges = qears.welded_edges(np.asarray(triangles, int), canon)
    wing = np.zeros(len(points), bool)
    wing[canon[mask]] = True
    touching = edges[wing[edges[:, 0]] ^ wing[edges[:, 1]]]
    inner = np.where(wing[touching[:, 0]], touching[:, 0], touching[:, 1])
    return np.unique(inner)


def fan(points: np.ndarray, root: np.ndarray, sign: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(u, s, plane): the fan round `root` in the wing's plane. `plane` rows are the first axis (from the root toward the wing's middle),
    the second (the first turned a quarter toward the wing's top, +Z) and the normal (pointing out of the body's side, `sign`)."""

    axes = principal_axes(points)
    first = axes[0] if axes[0] @ (points.mean(axis=0) - root) >= 0 else -axes[0]
    normal = unit(np.cross(axes[0], axes[1]))
    second = unit(np.cross(normal, first))
    if second[2] < 0:
        second = -second
        normal = -normal
    rel = points - root
    x, y = rel @ first, rel @ second
    return np.arctan2(y, x), np.hypot(x, y), np.stack([first, second, normal])


def chain_angles(u: np.ndarray, s: np.ndarray, count: int) -> np.ndarray:
    """Even angles over the wing's spread (2nd to 98th percentile), the top one moved onto the leading edge: `LEAD_PERCENTILE` of the
    angles of the wing's outer half, so the arm is one chain's."""

    low, high = np.percentile(u, [2.0, 98.0])
    angles = low + (np.arange(count) + 0.5) * (high - low) / count
    outer = s >= np.median(s)
    angles[-1] = max(float(np.percentile(u[outer], LEAD_PERCENTILE)), float(angles[-1]))
    return angles


def chain_joints(points: np.ndarray, u: np.ndarray, s: np.ndarray, root: np.ndarray, angles: np.ndarray, bones: int) -> Tuple[np.ndarray, np.ndarray]:
    """Joints (chains, bones + 1, 3) and their distances from the root (chains, bones + 1). A chain starts at the root and ends at the 99th
    percentile of `s` in its band (half the gap to each neighbour); joint k sits at the median of the band's points within half a bone
    of its distance."""

    gaps = np.diff(angles)
    joints = np.zeros((len(angles), bones + 1, 3))
    stations = np.zeros((len(angles), bones + 1))
    for c, angle in enumerate(angles):
        left = gaps[c - 1] / 2 if c > 0 else angle - float(u.min())
        right = gaps[c] / 2 if c < len(gaps) else float(u.max()) - angle
        band = np.abs(u - angle) <= np.where(u < angle, max(left, 1e-6), max(right, 1e-6))
        if band.sum() < 3:
            band = np.isin(np.arange(len(u)), np.argsort(np.abs(u - angle))[:8])
        end = float(np.percentile(s[band], 99.0))
        stations[c] = np.linspace(0.0, end, bones + 1)
        step = end / bones
        joints[c, 0] = root
        for k in range(1, bones + 1):
            near = band & (np.abs(s - stations[c, k]) <= step / 2)
            if near.sum() == 0:
                near = np.isin(np.arange(len(u)), np.flatnonzero(band)[np.argsort(np.abs(s[band] - stations[c, k]))[:5]])
            joints[c, k] = np.median(points[near], axis=0)
    return joints, stations


def detect_wings(points: np.ndarray, triangles: np.ndarray, landmarks: Dict[str, object], contacts: Sequence[np.ndarray],
                 chains: int = WING_CHAINS, bones: int = WING_BONES) -> Tuple[Dict[str, Dict[str, object]], Dict[str, np.ndarray]]:
    """The wings: per side the plan (`root`, `plane`, `angles`, `joints`, `stations`, `length`, `side_sign`, all in the model's own
    coordinates) and the vertex mask. Empty when the model has none."""

    height = float(landmarks["height"])
    points = np.asarray(points, float)
    masks = wing_masks(points, triangles, landmarks, contacts)
    plans: Dict[str, Dict[str, object]] = {}
    for side, sign in SIDES:
        mask = masks.get(side)
        if mask is None:
            continue
        line = root_line(points, triangles, mask, height)
        wing = points[mask]
        if len(line) < 3:
            line_points = wing[np.argsort(np.abs(wing[:, 0] - float(landmarks["centre_x"])))[: max(3, len(wing) // 20)]]
        else:
            line_points = points[line]
        front = line_points[line_points[:, 1] <= np.quantile(line_points[:, 1], ROOT_FRONT_SHARE)]
        root = front.mean(axis=0)
        u, s, plane = fan(wing, root, sign)
        angles = chain_angles(u, s, chains)
        joints, stations = chain_joints(wing, u, s, root, angles, bones)
        plans[side] = {"root": root, "plane": plane, "angles": angles, "joints": joints, "stations": stations,
                       "length": float(np.percentile(s, 99.0)), "side_sign": sign, "vertices": int(mask.sum()),
                       "root_line": line_points.mean(axis=0)}
    return plans, masks


# ---------------------------------------------------------------------------------------------
# Frames and poses
# ---------------------------------------------------------------------------------------------

X = np.array([1.0, 0.0, 0.0])
Y = np.array([0.0, 1.0, 0.0])
Z = np.array([0.0, 0.0, 1.0])


def rest_frame(plan: Dict[str, object]) -> Tuple[np.ndarray, float, np.ndarray]:
    """(frame, middle angle, fan axis): the wing's rest frame as columns (span, chord, normal), the fan's middle angle in its plane and the
    plane's own normal (the axis its chain angles turn about). The span runs from the root through the middle of the fan, the chord across
    it toward the leading edge (the arm), and the normal is `side_sign` times span x chord, so both wings' normals point the same way
    for a mirrored pose."""

    first, second, _normal = (np.asarray(row, float) for row in plan["plane"])
    angles = np.asarray(plan["angles"], float)
    middle = 0.5 * (float(angles[0]) + float(angles[-1]))
    span = math.cos(middle) * first + math.sin(middle) * second
    chord = -math.sin(middle) * first + math.cos(middle) * second
    sign = float(plan["side_sign"])
    return np.stack([span, chord, sign * np.cross(span, chord)], axis=1), middle, unit(np.cross(first, second))


def target_frame(sweep: float, rise: float, roll: float, sign: float) -> np.ndarray:
    """A wing's frame from three angles (degrees) in the body's frame: `sweep` turns the span back from straight out to the side (90 points
    it straight back), `rise` lifts it above the horizontal, and `roll` turns the chord about the span from the most upward direction
    toward the front (90 lays the membrane flat, its face up). Columns (span, chord, normal) as `rest_frame`."""

    a, e, r = (math.radians(value) for value in (sweep, rise, roll))
    span = math.cos(e) * (math.cos(a) * sign * X + math.sin(a) * Y) + math.sin(e) * Z
    up = Z - (Z @ span) * span
    up = unit(up) if np.linalg.norm(up) > 1e-6 else unit(-Y - (-Y @ span) * span)
    forward = unit(np.cross(span, up))
    if forward @ -Y < 0:
        forward = -forward
    chord = math.cos(r) * up + math.sin(r) * forward
    return np.stack([span, chord, sign * np.cross(span, chord)], axis=1)


def frame_angles(frame: np.ndarray, sign: float) -> Tuple[float, float, float]:
    """The (sweep, rise, roll) of a frame (`target_frame`'s inverse)."""

    span, chord = frame[:, 0], frame[:, 1]
    rise = math.degrees(math.asin(max(-1.0, min(1.0, float(span[2])))))
    sweep = math.degrees(math.atan2(float(span[1]), float(span[0]) * sign))
    up = Z - (Z @ span) * span
    up = unit(up)
    forward = unit(np.cross(span, up))
    if forward @ -Y < 0:
        forward = -forward
    return sweep, rise, math.degrees(math.atan2(float(chord @ forward), float(chord @ up)))


def axis_angle(matrix: np.ndarray) -> Tuple[Tuple[float, float, float], float]:
    """A rotation matrix as (axis, degrees)."""

    cosine = max(-1.0, min(1.0, (float(np.trace(matrix)) - 1.0) / 2.0))
    angle = math.acos(cosine)
    if angle < 1e-7:
        return (1.0, 0.0, 0.0), 0.0
    axis = np.array([matrix[2, 1] - matrix[1, 2], matrix[0, 2] - matrix[2, 0], matrix[1, 0] - matrix[0, 1]])
    if np.linalg.norm(axis) < 1e-6:  # a half turn: the axis is the eigenvector of +1
        values, vectors = np.linalg.eigh((matrix + matrix.T) / 2)
        axis = vectors[:, int(np.argmax(values))]
    axis = unit(axis)
    return (float(axis[0]), float(axis[1]), float(axis[2])), math.degrees(angle)


def rotation(axis: Sequence[float], degrees: float) -> np.ndarray:
    a = unit(np.asarray(axis, float))
    t = math.radians(degrees)
    k = np.array([[0.0, -a[2], a[1]], [a[2], 0.0, -a[0]], [-a[1], a[0], 0.0]])
    return np.eye(3) + math.sin(t) * k + (1 - math.cos(t)) * k @ k


def wing_rows(plan: Dict[str, object], pose: Dict[str, float], side: str) -> Dict[str, List[Tuple[Tuple[float, float, float], float]]]:
    """The wing bones' rotations (armature-space (axis, degrees) rows, `quadruped_layout.pose_at`'s format) for a pose:

    - `sweep`, `rise`, `roll`: where the whole wing points (`target_frame`), reached from its rest frame by one turn at the root;
    - `flap`: the beat, a turn about the body's long axis at the root after that (degrees, positive down on both sides), so a wing beats
      up and down whatever way its membrane faces;
    - `spread`: the fan's spread as a share of its rest spread (each chain turns about the plane's normal toward the middle);
    - `curl`: degrees each bone past the root bends across the membrane (positive toward the back of the normal), `curl_out` how much
      more each further bone bends, and `wave_<b>` the beat's wave at bone b, a turn about the long axis as the beat's.

    A child's turn is given in the rest frame and carried by its parent's, so the wave's axis is the long axis taken back through the
    chain's own turn at the root."""

    sign = float(plan["side_sign"])
    rest, middle, fan_axis = rest_frame(plan)
    target = target_frame(pose.get("sweep", 0.0), pose.get("rise", 0.0), pose.get("roll", 0.0), sign)
    if pose.get("frame") is not None and pose.get("frame_share", 0.0) > 0:
        # turn part of the way from the pose's own frame to a given one (the lying wing of a death), by the shortest turn
        axis, degrees = axis_angle(np.asarray(pose["frame"], float) @ target.T)
        target = rotation(axis, degrees * float(pose["frame_share"])) @ target
    stroke = sign * Y
    target = rotation(stroke, pose.get("flap", 0.0)) @ target
    whole_matrix = target @ rest.T
    whole = axis_angle(whole_matrix)
    angles = np.asarray(plan["angles"], float)
    joints = np.asarray(plan["joints"], float)
    spread = pose.get("spread", 1.0)
    rows: Dict[str, List[Tuple[Tuple[float, float, float], float]]] = {}
    for c in range(len(angles)):
        fan_degrees = math.degrees((float(angles[c]) - middle) * (spread - 1.0))
        rows[wing_name(side, c, 0)] = [(tuple(float(v) for v in fan_axis), fan_degrees), whole]
        carried = whole_matrix @ rotation(fan_axis, fan_degrees)
        wave_axis = unit(carried.T @ stroke)
        for b in range(1, joints.shape[1] - 1):
            direction = unit(joints[c, b + 1] - joints[c, b])
            hinge = unit(np.cross(rest[:, 2], direction))
            bend = pose.get("curl", 0.0) * (1.0 + pose.get("curl_out", 0.0) * (b - 1))
            rows[wing_name(side, c, b)] = [(tuple(float(v) for v in hinge), bend),
                                           (tuple(float(v) for v in wave_axis), pose.get(f"wave_{b}", 0.0))]
    return rows


# ---------------------------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------------------------


def sheet_rows(u: np.ndarray, s: np.ndarray, angles: np.ndarray, stations: np.ndarray) -> List[Dict[Tuple[int, int], float]]:
    """Per vertex {(chain, bone): weight}: two chains linear in `u`, two bones linear in `s` between the bones' middles."""

    chains, bones = stations.shape[0], stations.shape[1] - 1
    rows: List[Dict[Tuple[int, int], float]] = []
    for value_u, value_s in zip(u, s):
        if chains == 1 or value_u <= angles[0]:
            across = [(0, 1.0)]
        elif value_u >= angles[-1]:
            across = [(chains - 1, 1.0)]
        else:
            c = int(np.searchsorted(angles, value_u)) - 1
            g = (value_u - angles[c]) / max(float(angles[c + 1] - angles[c]), 1e-12)
            across = [(c, 1.0 - g), (c + 1, g)]
        row: Dict[Tuple[int, int], float] = {}
        for c, wc in across:
            t = value_s / max(float(stations[c, -1]), 1e-12) * bones - 0.5
            b = int(np.clip(math.floor(t), 0, bones - 1))
            f = float(np.clip(t - b, 0.0, 1.0)) if t >= 0 and b < bones - 1 else 0.0
            for bone, wb in ((b, 1.0 - f), (b + 1, f)):
                if wb > 0 and wc > 0 and bone < bones:
                    row[(c, bone)] = row.get((c, bone), 0.0) + wc * wb
        rows.append(row)
    return rows


def _smooth(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def root_blend(points: np.ndarray, edges: np.ndarray, canon: np.ndarray, mask: np.ndarray, side_ok: np.ndarray, reach: float) -> np.ndarray:
    """The wing's share of each vertex's weight: one half on the wing's border with the body, rising to one over `reach` (surface distance)
    into the wing and falling to none over `reach` into the body (only skin on the wing's side, `side_ok`)."""

    wing = np.zeros(len(points), bool)
    wing[canon[mask]] = True
    inside = qears.surface_distance(points, edges, ~wing & (canon == np.arange(len(points))), reach)
    outside = qears.surface_distance(points, edges, wing, reach)
    share = np.where(wing, 0.5 + 0.5 * _smooth(np.where(np.isfinite(inside), inside / reach, 1.0)),
                     0.5 - 0.5 * _smooth(np.where(np.isfinite(outside), outside / reach, 1.0)))
    share = np.where(wing | side_ok[canon] | ~np.isfinite(outside), share, 0.0)
    return share[canon]


def wing_weights(points: np.ndarray, triangles: np.ndarray, names: Sequence[str], plans: Dict[str, Dict[str, object]],
                 masks: Dict[str, np.ndarray], indices: np.ndarray, weights: np.ndarray, centre_x: float, belly_z: float) -> Tuple[np.ndarray, np.ndarray]:
    """Bind each wing to its chains (`sheet_rows`) and blend it into the body's own weights at its root (`root_blend`, over
    `ROOT_BLEND_SHARE` of the wing's length). `indices`, `weights` as `quadruped_layout.skin_weights` returns them, rewritten."""

    points = np.asarray(points, float)
    height = float(np.ptp(points[:, 2])) or 1.0
    canon = qears.weld(points, 1e-6 * height)
    edges = qears.welded_edges(np.asarray(triangles, int), canon)
    out_i, out_w = indices.copy(), weights.copy()
    slots = indices.shape[1]
    index = {name: k for k, name in enumerate(names)}
    for side, plan in plans.items():
        mask = masks[side]
        sign = float(plan["side_sign"])
        side_ok = ((points[:, 0] - centre_x) * sign > 0) & (points[:, 2] > belly_z)
        share = root_blend(points, edges, canon, mask, side_ok, ROOT_BLEND_SHARE * float(plan["length"]))
        rows_at = np.flatnonzero(share > 1e-4)
        first, second, _normal = (np.asarray(row, float) for row in plan["plane"])
        rel = points[rows_at] - np.asarray(plan["root"], float)
        u = np.arctan2(rel @ second, rel @ first)
        s = np.hypot(rel @ first, rel @ second)
        sheet = sheet_rows(u, s, np.asarray(plan["angles"], float), np.asarray(plan["stations"], float))
        for row, cells in zip(rows_at, sheet):
            alpha = float(share[row])
            dense: Dict[int, float] = {}
            for bone, weight in zip(out_i[row], out_w[row]):
                if weight > 0:
                    dense[int(bone)] = dense.get(int(bone), 0.0) + (1.0 - alpha) * float(weight)
            for (c, b), weight in cells.items():
                key = index[wing_name(side, c, b)]
                dense[key] = dense.get(key, 0.0) + alpha * weight
            kept = sorted(((k, v) for k, v in dense.items() if v > 1e-6), key=lambda item: -item[1])[:slots]
            total = sum(value for _, value in kept) or 1.0
            out_i[row] = [item[0] for item in kept] + [kept[0][0]] * (slots - len(kept))
            out_w[row] = [item[1] / total for item in kept] + [0.0] * (slots - len(kept))
    return out_i, out_w


# ---------------------------------------------------------------------------------------------
# Wing motion per role
# ---------------------------------------------------------------------------------------------

# Wing poses in the body's frame (`target_frame`): sweep back from straight out, rise above the horizontal, roll of the chord toward the
# front, the fan's spread as a share of its rest spread (a folded fan keeps 0.7 of it: the membrane between two chains shortens by the
# same share, and the kit's stretch measure counts an edge changed by 1.5 times, so 0.67 is the least), the bend of each bone past the
# root (curl, positive toward the back of the wing) and how much more each further bone bends (curl_out).
FOLDED = {"sweep": 80.0, "rise": 10.0, "roll": -25.0, "spread": 0.7, "curl": 25.0, "curl_out": 0.5}
HALF = {"sweep": 60.0, "rise": 22.0, "roll": -10.0, "spread": 0.85, "curl": 12.0, "curl_out": 0.5}
SPREAD = {"sweep": 35.0, "rise": 38.0, "roll": -20.0, "spread": 1.0, "curl": 0.0, "curl_out": 0.0}
SHIELD = {"sweep": 5.0, "rise": 75.0, "roll": -60.0, "spread": 0.95, "curl": -30.0, "curl_out": 0.5}
FLEE = {"sweep": 60.0, "rise": 30.0, "roll": -45.0, "spread": 0.95, "curl": 0.0, "curl_out": 0.0}
LYING = {**FOLDED, "spread": 1.0, "curl": 0.0, "curl_out": 0.0}  # the lying wing's direction comes from `lying_pose`
# Beats: (degrees at the root, beats per clip, the wave's bend per bone past the root as a share of the root's beat, its lag per bone as a
# share of a beat). The idle breathes: one slow rise and fall of the folded wings per loop.
BREATH = (4.0, 1, 0.3, 0.12)
WALK_BEAT = (14.0, 1, 0.35, 0.12)
ATTACK_BEAT = (30.0, 2, 0.35, 0.12)
FLEE_BEAT = (24.0, 3, 0.35, 0.12)
GUARD_BEAT = (6.0, 2, 0.3, 0.12)
DEATH_FOLD_END = 0.25  # the wings fold by this share of a death, then open and settle flat as the body lies


def _blend(a: Dict[str, float], b: Dict[str, float], x: float) -> Dict[str, float]:
    return {key: (1.0 - x) * a.get(key, 0.0) + x * b.get(key, 0.0) for key in set(a) | set(b)}


def _beat(pose: Dict[str, float], t: float, beat: Tuple[float, int, float, float], bones: int, envelope: float = 1.0) -> Dict[str, float]:
    amplitude, count, wave, lag = beat
    out = dict(pose)
    phase = 2 * math.pi * count * t
    out["flap"] = out.get("flap", 0.0) + amplitude * envelope * math.sin(phase)
    for b in range(1, bones):
        out[f"wave_{b}"] = wave * amplitude * envelope * math.sin(phase - 2 * math.pi * lag * b)
    return out


def _envelope(t: float, rise: float = 0.2, fall: float = 0.2) -> float:
    up = float(_smooth(np.array(min(1.0, t / rise))))
    down = float(_smooth(np.array(max(0.0, (t - 1.0 + fall) / fall))))
    return up * (1.0 - down)


def role_pose(style: str, t: float, bones: int, lying: Optional[np.ndarray] = None) -> Dict[str, object]:
    """The wing pose (`wing_rows`' keys) of a winged style at clip time t (0 to 1): idle folded and breathing, move half folded with a slow
    beat per stride, attack spread wide with two strong beats, defend raised as a shield, retreat beating hard, death folding and then
    settling flat. Clips the game loops start and end folded."""

    if style == "winged_idle":
        return _beat(FOLDED, t, BREATH, bones)
    if style == "winged_walk":
        return _beat(HALF, t, WALK_BEAT, bones)
    if style == "winged_rear":
        envelope = _envelope(t, 0.25, 0.25)
        return _beat(_blend(FOLDED, SPREAD, envelope), t, ATTACK_BEAT, bones, envelope)
    if style == "winged_guard":
        envelope = _envelope(t, 0.25, 0.25)
        return _beat(_blend(FOLDED, SHIELD, envelope), t, GUARD_BEAT, bones, envelope)
    if style == "winged_flee":
        envelope = _envelope(t, 0.15, 0.15)
        return _beat(_blend(FOLDED, FLEE, envelope), t, FLEE_BEAT, bones, envelope)
    if style == "winged_collapse":
        settle = float(_smooth(np.array(max(0.0, (t - DEATH_FOLD_END) / (1.0 - DEATH_FOLD_END)))))
        out = _blend(FOLDED, LYING, settle)
        if lying is not None:
            out.update(frame=lying, frame_share=settle)
        return out
    return dict(FOLDED)


def role_rows(style: str, t: float, layout, yaw: float = 0.0) -> Dict[str, List[Tuple[Tuple[float, float, float], float]]]:
    """Both wings' bone rows for a winged style at clip time t (`role_pose`, `wing_rows`). When the body turns about the vertical (`yaw`
    degrees, positive turns the head toward its left), the wing on the side that comes forward sweeps back by the turn, as the humanoid
    wing chains do: the review cameras stay put, and a wing carried forward by the turn crossed the head and neck in a side view (the
    retreat's turn of 30 degrees hid 17% of the legs, neck and head, offline on the Tripo dragon)."""

    rows: Dict[str, List[Tuple[Tuple[float, float, float], float]]] = {}
    for side, plan in (layout.landmarks.get("wings") or {}).items():
        bones = np.asarray(plan["joints"]).shape[1] - 1
        lying = lying_pose(plan, layout.landmarks) if style == "winged_collapse" else None
        pose = role_pose(style, t, bones, lying)
        pose["sweep"] = float(pose.get("sweep", 0.0)) + max(0.0, -float(plan["side_sign"]) * yaw)
        rows.update(wing_rows(plan, pose, side))
    return rows


# A dead dragon's wings lie flat on the ground beyond its back: the wing underneath swept LYING_SWEEP_LOWER toward the head, the one on
# top LYING_SWEEP_UPPER toward the tail so the two do not lie in one another, each sloping down from its root just enough that its far end
# reaches the ground (the root's height after the roll over the wing's length).
LYING_SWEEP_LOWER = -20.0
LYING_SWEEP_UPPER = 35.0


def lying_pose(plan: Dict[str, object], landmarks: Dict[str, object]) -> np.ndarray:
    """The wing frame (columns span, chord, normal, in the body's frame) that lays a wing flat on the ground once the dead body has rolled `landmarks["death"]["roll"]`
    degrees about its long axis (about the edge of the side it falls toward, as `quadruped_rig._body_turn` does)."""

    death = landmarks.get("death") or {}
    roll = float(death.get("roll", 82.0))
    sign = float(plan["side_sign"])
    body = rotation(Y, roll)
    lower = (roll > 0) == (sign > 0)  # a positive roll lays the body on its left side (+X goes down)
    width = float(landmarks.get("width", 0.0))
    edge = np.array([float(landmarks["centre_x"]) + math.copysign(0.5 * width, roll), 0.0, float(landmarks["ground_offset"])])
    root = np.asarray(plan["root"], float)
    # the far end reaches down to where the rolled torso lies: the lowest of the torso's landmarks (the four leg tops at its sides, the back
    # and the belly over its middle) after the roll
    ground = float(landmarks["ground_offset"])
    torso = [np.asarray(joints["top"], float) + np.array([0.0, 0.0, ground]) for joints in (landmarks.get("legs") or {}).values()]
    middle = (float(landmarks["centre_x"]), float(landmarks["mid_y"]))
    torso += [np.array([middle[0], middle[1], ground + float(landmarks[key])]) for key in ("back_z", "belly_z")]
    lowest = min(float((body @ (point - edge))[2]) for point in torso)
    height = float((body @ (root - edge))[2]) - lowest
    length = max(float(plan["length"]), 1e-9)
    droop = math.degrees(math.asin(max(0.0, min(1.0, height / length)))) - (float(death.get("wing_lift", 0.0)) if lower else 0.0)
    back = body @ Z
    out = unit(back - (back @ Z) * Z)
    sweep = math.radians(LYING_SWEEP_LOWER if lower else LYING_SWEEP_UPPER)
    # turn the outward direction toward the tail (+Y) by the sweep, whichever side it points to
    turn = rotation(Z, math.degrees(sweep) * (1.0 if out[0] > 0 else -1.0))
    span = unit(math.cos(math.radians(droop)) * (turn @ out) - math.sin(math.radians(droop)) * Z)
    chord = unit(np.cross(Z, span))
    if chord @ -Y < 0:
        chord = -chord
    chord = unit(chord - (chord @ span) * span)
    world = np.stack([span, chord, sign * np.cross(span, chord)], axis=1)
    return body.T @ world
