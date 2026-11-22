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
ROOT_BLEND_SHARE = 0.20  # of the wing's length: the wing's weights rise from the body's over this surface distance
LEAD_PERCENTILE = 92.0  # the leading edge's angle in the fan, over the wing's outer half (lib/tripo_chains.LEADING_EDGE_PERCENTILE is 90)
WING_CHAINS = 4
# The trailing chain (the first, by the flank) turns this share of the wing's every turn, beat and fold, so the membrane between the wing and
# the flank it grows from follows the wing part of the way and bends across the fan's trailing quarter instead of along one seam: a fresh
# review of run 3 saw it pinned to the flank, stretched into a dragged sheet when the wings rose.
TRAIL_SHARE = 0.7
WEB = True  # the inner membrane behind the trailing chain is a web to the flank (`web_share`)
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
    # the side's own sense (`sign`), never a test against the front: a span swept past straight ahead (the defend's crossing wings) flipped
    # that test and turned the chord over in one frame (UNIT-ANIM-SPIN, 50 degrees in a frame in run 5)
    forward = sign * unit(np.cross(span, up))
    chord = math.cos(r) * up + math.sin(r) * forward
    return np.stack([span, chord, sign * np.cross(span, chord)], axis=1)


def frame_angles(frame: np.ndarray, sign: float) -> Tuple[float, float, float]:
    """The (sweep, rise, roll) of a frame (`target_frame`'s inverse)."""

    span, chord = frame[:, 0], frame[:, 1]
    rise = math.degrees(math.asin(max(-1.0, min(1.0, float(span[2])))))
    sweep = math.degrees(math.atan2(float(span[1]), float(span[0]) * sign))
    up = Z - (Z @ span) * span
    up = unit(up)
    # the side's own sense (`sign`), never a test against the front: a span swept past straight ahead (the defend's crossing wings) flipped
    # that test and turned the chord over in one frame (UNIT-ANIM-SPIN, 50 degrees in a frame in run 5)
    forward = sign * unit(np.cross(span, up))
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


def fold_line(joints: np.ndarray, bone: int, normal: np.ndarray, span: np.ndarray) -> np.ndarray:
    """The axis every chain's `bone` turns about when the wing folds: the line through that bone's joints across the fan (from the first
    chain's to the last's), in the wing's plane, signed so a positive turn carries the outer wing toward the back of the normal. One axis for
    all chains folds the membrane between them like paper along that line: a turn about each chain's own cross axis sheared it, and the folded
    wings creased and bunched at the wrist and elbow (a fresh review of run 3)."""

    line = np.asarray(joints[-1, bone], float) - np.asarray(joints[0, bone], float)
    line = unit(line - (line @ normal) * normal)
    if float(np.cross(line, span) @ normal) > 0:
        line = -line
    return line


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
        share = TRAIL_SHARE if c == 0 and len(angles) > WING_CHAINS - 1 and TRAIL_SHARE < 1.0 else 1.0
        fan_degrees = math.degrees((float(angles[c]) - middle) * (spread - 1.0))
        turn = (whole[0], whole[1] * share)
        rows[wing_name(side, c, 0)] = [(tuple(float(v) for v in fan_axis), fan_degrees), turn]
        carried = rotation(turn[0], turn[1]) @ rotation(fan_axis, fan_degrees)
        wave_axis = unit(carried.T @ stroke)
        for b in range(1, joints.shape[1] - 1):
            hinge = fold_line(joints, b, rest[:, 2], rest[:, 0])
            bend = pose.get("curl", 0.0) * (1.0 + pose.get("curl_out", 0.0) * (b - 1))
            rows[wing_name(side, c, b)] = [(tuple(float(v) for v in hinge), bend * share),
                                           (tuple(float(v) for v in wave_axis), pose.get(f"wave_{b}", 0.0) * share)]
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


def flank_line(points: np.ndarray, triangles: np.ndarray, mask: np.ndarray, u: np.ndarray, s: np.ndarray, trailing: float) -> Tuple[np.ndarray, np.ndarray]:
    """The inner membrane's line on the flank: the wing's border vertices with the body behind its trailing chain, as (radius, fan angle)
    pairs sorted by radius. Empty when the wing meets the body only at its root."""

    tm = mask[triangles]
    border = np.zeros(len(points), bool)
    border[triangles[tm.any(1) & ~tm.all(1)].ravel()] = True
    border &= mask & (u < trailing)
    order = np.argsort(s[border])
    return s[border][order], u[border][order]


def web_share(u: np.ndarray, s: np.ndarray, line_s: np.ndarray, line_u: np.ndarray, trailing: float) -> np.ndarray:
    """The trailing chain's share of the inner membrane, a web between that chain and the flank line: none on the line, all on the chain,
    linear in the fan angle between them at each radius (the line's angle at that radius, its end's beyond it). A linear share moves each
    point on the straight line between its anchor on the flank and its place on the finger, so the web shortens without wadding: the
    surface-distance blend let the far web follow the finger whole and bunched it into a skirt at the flank (fresh reviews of run 7)."""

    if len(line_s) == 0:
        return np.ones(len(u))
    anchor = np.interp(s, line_s, np.minimum.accumulate(line_u))
    width = np.maximum(trailing - anchor, 1e-6)
    return np.where(u < trailing, np.clip((u - anchor) / width, 0.0, 1.0), 1.0)


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
        trailing = float(np.asarray(plan["angles"], float)[0])
        rel_all = points - np.asarray(plan["root"], float)
        u_all = np.arctan2(rel_all @ second, rel_all @ first)
        s_all = np.hypot(rel_all @ first, rel_all @ second)
        line_s, line_u = flank_line(points, np.asarray(triangles, int), mask, u_all, s_all, trailing)
        web = web_share(u, s, line_s, line_u, trailing) if WEB else np.ones(len(u))
        for row, cells, g in zip(rows_at, sheet, web):
            alpha = min(float(share[row]), float(g))
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
# Round 5 (fresh reviews of run 9): the folded wings lie along the back and flanks behind the shoulders, the membrane turned down
# (roll -60) so from the front they stay below the head (offline the head's front silhouette under the wings' fell from 0.92 to 0). Held
# up over the back they stood as a box framing the head, and this pose starts and ends every clip. The half folded and retreat wings
# turn their membrane up toward the game camera: held upright one of the two read from it as a thin spike (its width over length on
# the screen 0.31 of its flat shape's in run 9). Turned fully level (roll -80) they stretched the wing roots 5.9% (run 10, limit 5%).
FOLDED = {"sweep": 85.0, "rise": 15.0, "roll": -60.0, "spread": 1.0, "curl": 20.0, "curl_out": 0.0}
# Round 11: the membrane rolled -62 degrees, not -55. With the neck bones on the measured neck column (quadruped_layout.detect_neck) the
# neck's base counts as neck, and from the front the half folded wings stood behind 25.3% of the head and neck in the move's first frame
# (TRIPO-WING-HEAD-FRONT, limit 25%), 12.7% at -62 (offline on run 18's files re-rigged). Its wing root then reads 5.2% offline
# (TRIPO-WING-ROOT-STRETCH, limit 5%), where run 18's own clips read 5.0% offline and 4.3% in the route: the offline fit adds about 0.6%.
# A beat of 22 degrees instead of 25 left the root as it was and moved the wings only 2.8 times as much as the idle's (TRIPO-WING-IDLE-MOVE).
HALF = {"sweep": 60.0, "rise": 25.0, "roll": -62.0, "spread": 1.0, "curl": 22.0, "curl_out": 0.0}
SPREAD = {"sweep": 35.0, "rise": 38.0, "roll": -20.0, "spread": 1.0, "curl": 0.0, "curl_out": 0.0}
# The defend no longer shields with the wings: spread forward they opened to the sides and left the head and neck exposed between them,
# a wing display that read as the attack at map size (both fresh reviews of run 9). The dragon crouches with its head drawn back and
# down (`quadruped_layout._winged_guard`) under wings half folded and mantled over the back.
# Run 10 held them half folded low on the back and read as the idle from the map camera (TRIPO-MAP-READ 4%, at least 18%): they rise and
# fold tight over the back as a hood that keeps to each wing's own side.
# Round 6: folded tight over the head the membranes crushed into creased lumps (TRIPO-WING-CRUSH 9.6% of the wing's edges on run 12, the
# poses reviewers passed 2.9% to 4.5%). Half open and mantled down on each side they stay flat (4.5% offline) and above the belly.
# Round 7: the defend is a braced recoil, not a wing shield or a display. The wings open halfway and mantle low and back, behind the
# shoulders (MANTLE): swept 45 degrees they stood out to the sides (run 14).
# Round 8: the poses that hold the wings back (MANTLE, FLEE) keep the fold's own bend (`held_back`: FOLDED's curl and spread) and differ
# from it only in where the folded wing points. `sweep` turns the middle of a fan about 120 degrees wide, so its trailing half points out
# to the side whatever the sweep, and only the bend at the wrist and elbow lays it back. Round 7's mantle (curl 8, the fold's 20) and
# retreat (14) unbent the wings out to the sides: on run 15 they reached 1.26 and 1.17 times as far to the side as the idle's fold
# (TRIPO-WING-SIDE-REACH), and both fresh reviews saw the defend's wings stand straight out like a plank, wider than the idle. Closing the
# fan instead (spread 0.7 to 0.35) crushes the membrane (TRIPO-WING-CRUSH 10% to 29%, offline). The mantle raises the fold over the back
# and sweeps it past straight back (0.97 of the idle's reach, offline), the retreat raises it a little (1.05).
def held_back(**where: float) -> Dict[str, float]:
    return {**FOLDED, **where}


# Round 9: the mantle turns the fold's membrane up toward the game camera (roll -30, the fold -60), so the defend's silhouette from the
# game camera differs from the idle's (TRIPO-GAME-READ 0.30, 0.20 with the fold's roll, offline on run 17's files). Turned down (roll -85)
# the trailing edge swings out past the idle's reach (TRIPO-WING-SIDE-REACH 1.15).
# Round 11: raised 30 degrees, not 35. With the neck bones on the measured neck column (quadruped_layout.detect_neck) the near wing's
# raised fold hid 10.8% of the legs, neck and head from the side (TRIPO-WING-FRONT, limit 10%), 8.2% at 30. Lowered to 25 or swept to 85
# it reads as the idle from the game camera (TRIPO-GAME-READ 0.25, at least 0.27).
MANTLE = held_back(sweep=95.0, rise=30.0, roll=-30.0)
# Round 7: the retreat runs with its wings half folded and swept back, beating little (FLEE, FLEE_BEAT). Held half open and beating hard
# (swept 50 degrees, raised 30, a 20 degree beat) it read as the move (fresh reviews of runs 9 and 12).
FLEE = held_back(sweep=85.0, rise=20.0)
# A dead winged quadruped lies on its side with both wings in the idle's fold (FOLDED: its curl and its spread, kept from the first frame
# to the last). Rounds 3 to 6 opened them as the body fell and laid them flat on the ground beyond the back: one stood up as a sail or
# a tent, the other spread under the body, and the head lay among them (fresh reviews of runs 7, 9 and 12). Held as the idle holds them
# against the flanks, the one on top stood 34% of the height over its join once the body lay (offline, TRIPO-DEATH-WING-HIGH), so while
# the body rolls (DEAD_WINGS_START to DEAD_WINGS_END of the clip) each folded wing turns to lie level behind the back (`lying_pose`).
# LYING_UPPER and LYING_LOWER: (degrees the lying wing's span turns from straight out beyond the back toward the tail, degrees it tips
# up from its root). Both lie well toward the tail, so the shoulders, the neck and the head laid forward stay clear of them. The wing on
# top slopes down from the upper flank, and the wing underneath, whose root is at the ground, starts lower still and is lifted by the
# rest's `wing_lift` until its far bones are off the ground (quadruped_layout.choose_winged_rest): offline on the Tripo dragon it comes
# to rest 12 degrees under level, 0.22 of the height thick, the fold's own depth.
# Round 11 (D-107): with the neck bending from the shoulders (quadruped_layout.detect_neck) the dead head lies ahead of the chest, so the
# wing underneath can lie nearly straight out beyond the back (20 degrees toward the tail, tipped 45 down and bent 50 at its joints) where
# the head lay before, and the top wing drapes down the upper flank: 0.6 of its turn at the root, the rest a bend of 40 degrees per joint,
# 60 degrees toward the tail and tipped 32 down. Offline on run 18's files re-rigged to the measured neck TRIPO-DEATH-WING-TENT reads 0.37
# (1.13 before, at most 0.45) and TRIPO-DEATH-HEAD-HIDDEN 0.64 (at least 0.5). Toward the tail (75 degrees, round 10) the wing underneath
# stood over the torso's outline (0.6 of its share alone), and the top wing tipped only 25 down read 0.54. Bent 55 per joint it crushes
# (TRIPO-WING-CRUSH 6.3%), and taken whole at the root and bent 40 it reaches under the body and lifts it (TRIPO-NOT-DOWN).
DEAD_UPPER = {**FOLDED, "curl": 40.0}
DEAD_LOWER = {**FOLDED, "curl": 50.0}
LYING_UPPER = (60.0, -32.0)
LYING_LOWER = (20.0, -45.0)
DEAD_WINGS_START, DEAD_WINGS_END = 0.2, 0.65
# The share of the turn to its lying frame each dead wing takes at its root (`lying_pose`). The rest of its change is the bend of its bones
# past the root (DEAD_UPPER's and DEAD_LOWER's curl).
LYING_UPPER_SHARE = 0.6
LYING_LOWER_SHARE = 1.0
# Beats: (degrees at the root, beats per clip, the wave's bend per bone past the root as a share of the root's beat, its lag per bone as a
# share of a beat). The idle breathes: one slow rise and fall of the folded wings per loop.
BREATH = (4.0, 1, 0.3, 0.12)  # at 8 degrees the level wings of the move moved only 1.1 times as much at map size (TRIPO-WING-IDLE-MOVE, run 10)
WALK_BEAT = (25.0, 1, 0.35, 0.12)
ATTACK_BEAT = (30.0, 2, 0.35, 0.12)
FLEE_BEAT = (10.0, 3, 0.35, 0.12)
GUARD_BEAT = (6.0, 2, 0.3, 0.12)


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


# The attack's timing (shares of the clip): it cocks (rears, neck drawn back, wings spread and raised) up to ATTACK_COCK_END, strikes (neck
# lunges, forequarters come down, wings sweep back with a down-stroke) from ATTACK_STRIKE_START to ATTACK_STRIKE_END, snaps the head down
# at the bite, and recovers by the end.
ATTACK_COCK_END = 0.32
ATTACK_STRIKE_START, ATTACK_STRIKE_END = 0.3, 0.68
ATTACK_SNAP = (0.37, 0.5)  # its peak at 0.435 of the clip, on a review sheet frame (one every half second)
# Round 8: 0.3 of the way (0.35 in round 7, whose wings both fresh reviews of run 15 saw open as wide as the move's and hiding the head
# from the game camera). Less (0.2) and the attack reads as the idle from the map camera (TRIPO-MAP-READ 17%, at least 18%, offline).
ATTACK_OPEN = 0.3
# Round 9: the wings open only while the attack gathers and close low along the back for the blow (ATTACK_FLARE of the way to
# STRIKE_WINGS), with no down-stroke, so the head's travel is the largest change from the game camera. Both fresh reviews of run 17 saw
# only the wings move: they rose 15 degrees and beat down 27 at the strike.
ATTACK_FLARE = 1.0
ATTACK_LIFT = 5.0  # degrees the cocked wings rise
ATTACK_DOWNSTROKE = 0.0  # degrees the wings beat down at the strike
ATTACK_DOWN_END, ATTACK_DOWN_EASE = 0.75, 0.15  # the clip time the down-stroke is over by, and how long it takes to ease off
# The wings flare out and up as the head strikes, a support for the lunge: swept back for the blow they filled 91% as much of the map
# view as the defend's (run 10, TRIPO-ATTACK-DEFEND-ALIKE), and level (rise 0) they hung beside the legs and hid 22% of them from the side
# cameras (run 11, TRIPO-WING-FRONT).
# Round 9: for the blow the fold sweeps past straight back and lies low (raised 10), its membrane turned 15 degrees up from the fold's.
# Held in the fold the attack read 0.09 of the idle's silhouette (TRIPO-MAP-READ, at least 0.18), lowered to 5 below level it hung
# 9% of its points under the belly (TRIPO-WING-THROUGH-BODY), and this pose reads 0.33 (offline on run 17's files).
STRIKE_WINGS = held_back(sweep=100.0, rise=10.0, roll=-45.0)


def attack_phases(t: float) -> Tuple[float, float, float]:
    """(cock, strike, snap) of the attack at clip time t, each 0 to 1."""

    cock = float(_smooth(np.array(t / 0.2))) * (1.0 - float(_smooth(np.array((t - ATTACK_COCK_END) / 0.08))))
    strike = float(_smooth(np.array((t - ATTACK_STRIKE_START) / 0.08))) * (1.0 - float(_smooth(np.array((t - ATTACK_STRIKE_END) / 0.25))))
    low, high = ATTACK_SNAP
    snap = math.sin(math.pi * (t - low) / (high - low)) if low <= t <= high else 0.0
    return cock, strike, snap


def role_pose(style: str, t: float, bones: int, lying: Optional[np.ndarray] = None, upper: bool = False) -> Dict[str, object]:
    """The wing pose (`wing_rows`' keys) of a winged style at clip time t (0 to 1): idle folded and breathing, move half folded with a slow
    beat per stride, attack opened part of the way with a down-stroke at the strike, defend half open and mantled low behind the
    shoulders, retreat half folded and swept back, death folded throughout (`lying`: the frame the wing turns to as the body rolls).
    Clips the game loops start and end folded."""

    if style == "winged_idle":
        return _beat(FOLDED, t, BREATH, bones)
    if style == "winged_walk":
        return _beat(HALF, t, WALK_BEAT, bones)
    if style == "winged_rear":
        cock, strike, _snap = attack_phases(t)
        envelope = _envelope(t, 0.25, 0.25)
        # the wings open ATTACK_OPEN of the way to the spread pose and flare as the head lands, so the head's travel leads (a fresh review of
        # run 12 read the full spread as a wing display)
        pose = _blend(_blend(FOLDED, SPREAD, ATTACK_OPEN * envelope), STRIKE_WINGS, ATTACK_FLARE * strike)
        # the down-stroke is over before the wings fold again (ATTACK_DOWN_END): beaten down while they closed, a finger dropped past the
        # belly in the recovery (0.6% of the wing points in frame 54 of run 14, TRIPO-WING-THROUGH-BODY)
        down = ATTACK_DOWNSTROKE * strike * (1.0 - float(_smooth(np.array((t - ATTACK_DOWN_END + ATTACK_DOWN_EASE) / ATTACK_DOWN_EASE))))
        pose["flap"] = pose.get("flap", 0.0) - ATTACK_LIFT * cock + down
        for b in range(1, bones):
            pose[f"wave_{b}"] = 0.35 * (down - ATTACK_LIFT * cock)
        return pose
    if style == "winged_guard":
        envelope = _envelope(t, 0.25, 0.25)
        return _beat(_blend(FOLDED, MANTLE, envelope), t, GUARD_BEAT, bones, envelope)
    if style == "winged_flee":
        envelope = _envelope(t, 0.15, 0.15)
        return _beat(_blend(FOLDED, FLEE, envelope), t, FLEE_BEAT, bones, envelope)
    if style == "winged_collapse":
        # both wings stay in the idle's fold while the body sinks and rolls, and turn only as far as DEAD_UPPER and DEAD_LOWER ask
        settle = float(_smooth(np.array(max(0.0, min(1.0, (t - DEAD_WINGS_START) / (DEAD_WINGS_END - DEAD_WINGS_START))))))
        out = _blend(FOLDED, DEAD_UPPER if upper else DEAD_LOWER, settle)
        if lying is not None:
            out.update(frame=lying, frame_share=settle * (LYING_UPPER_SHARE if upper else LYING_LOWER_SHARE))
        return out
    return dict(FOLDED)


def role_rows(style: str, t: float, layout, yaw: float = 0.0) -> Dict[str, List[Tuple[Tuple[float, float, float], float]]]:
    """Both wings' bone rows for a winged style at clip time t (`role_pose`, `wing_rows`). The two wings always take mirrored poses in the
    body's frame (`yaw` is kept for the caller's sake and turns nothing): run 4 swept the wing a retreat's turn carried forward back by the
    turn, and both fresh reviews read it as one wing frozen upright while the other beat."""

    rows: Dict[str, List[Tuple[Tuple[float, float, float], float]]] = {}
    if style == "winged_collapse" and (layout.landmarks.get("death") or {}).get("side_search"):
        # the death's side is searched with both wings in the idle's fold (`quadruped_layout.roll_limits`): the skin by a wing's root takes
        # part of the wing's weights, so each lying pose tipped the search's near tie its own way
        style, t = "winged_idle", 0.0
    for side, plan in (layout.landmarks.get("wings") or {}).items():
        bones = np.asarray(plan["joints"]).shape[1] - 1
        upper = style == "winged_collapse" and not lies_under(plan, layout.landmarks)
        lying = lying_pose(plan, layout.landmarks, upper) if style == "winged_collapse" else None
        pose = role_pose(style, t, bones, lying, upper)
        rows.update(wing_rows(plan, pose, side))
    return rows


def lower_side(roll: float) -> str:
    """The side ("Left" or "Right") of the wing underneath a body rolled `roll` degrees (`lies_under`). The death's `wing_lift` tips only that
    wing, so the rest searches it on that wing's bones alone: with the top wing's far bones in the search a top wing draped down the flank
    read as one under the torso, and the search lifted the wing underneath to its most (60 degrees) for nothing."""

    return "Left" if roll > 0 else "Right"


def lies_under(plan: Dict[str, object], landmarks: Dict[str, object]) -> bool:
    """Whether the wing is the one underneath the dead body (a positive roll lays the body on its left side)."""

    return (float((landmarks.get("death") or {}).get("roll", 82.0)) > 0) == (float(plan["side_sign"]) > 0)


def lying_pose(plan: Dict[str, object], landmarks: Dict[str, object], upper: bool) -> np.ndarray:
    """The frame (columns span, chord, normal, in the body's frame) of a dead body's wing once the body has rolled `landmarks["death"]["roll"]`
    degrees onto its side: the wing's plane level with the ground, the fold's ridge up, its span out beyond the back, turned toward the
    tail and tipped from its root as LYING_UPPER or LYING_LOWER says. The wing underneath tips up by the death's `wing_lift` more."""

    death = landmarks.get("death") or {}
    roll = float(death.get("roll", 82.0))
    sign = float(plan["side_sign"])
    body = rotation(Y, roll)
    back = body @ Z
    out = unit(back - (back @ Z) * Z)
    sweep, tip, *more = (LYING_UPPER if upper else LYING_LOWER)
    stand = float(more[0]) if more else 0.0
    tip += 0.0 if upper else float(death.get("wing_lift", 0.0))
    # turn the outward direction toward the tail (+Y) by the sweep, whichever side it points to
    turn = rotation(Z, sweep * (1.0 if out[0] > 0 else -1.0))
    span = unit(math.cos(math.radians(tip)) * (turn @ out) + math.sin(math.radians(tip)) * Z)
    chord = unit(np.cross(Z, span))
    if chord @ -Y < 0:
        chord = -chord
    normal = np.cross(span, chord)
    if normal[2] < 0:  # the fold's ridge points up: `wing_rows` bends the outer bones toward the back of the normal
        chord = -chord
    if stand:  # the plane turns about the span by `stand` degrees
        chord = unit(math.cos(math.radians(stand)) * chord + math.sin(math.radians(stand)) * np.cross(span, chord))
    world = np.stack([span, chord, sign * np.cross(span, chord)], axis=1)
    return body.T @ world
