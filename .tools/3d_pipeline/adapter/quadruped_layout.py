"""Measure a four-legged model and lay out its rig, weights and gait poses.

Pure numpy, no Blender: `quadruped_rig.py` applies the results inside Blender,
and the unit tests run this module on synthetic point clouds. Coordinates are
the HOI4 working frame the candidate preparation produces: +Z up, ground at the
lowest point, the animal facing -Y, its left side toward +X.

The rig has 27 bones (the engine skins at most 50): a non-deforming Root on the
ground, Pelvis, Spine, Chest, two neck bones, Head, three tail bones when the
model has a tail, four bones per leg (upper, lower, cannon, hoof) and the
non-deforming Saddle_Node a rider entity attaches to, as vanilla
`cavalry_horse.mesh` does. A load adds its `Load` bone, and ears that stand
out beside the head (`quadruped_ears.py`) two bones each, children of the Head.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

LEGS = (("Front", "Left"), ("Front", "Right"), ("Rear", "Left"), ("Rear", "Right"))
LEG_SEGMENTS = ("Upper", "Lower", "Cannon", "Hoof")
SADDLE_NODE = "Saddle_Node"
LOAD_BONE = "Load"
X_AXIS = (1.0, 0.0, 0.0)
Y_AXIS = (0.0, 1.0, 0.0)
Z_AXIS = (0.0, 0.0, 1.0)


class LandmarkError(ValueError):
    """The model does not show four separate legs on the ground; pass measured landmarks instead."""


@dataclass
class Bone:
    name: str
    head: Tuple[float, float, float]
    tail: Tuple[float, float, float]
    parent: Optional[str]
    deform: bool = True


@dataclass
class Layout:
    landmarks: Dict[str, object]
    bones: List[Bone] = field(default_factory=list)

    def names(self) -> List[str]:
        return [bone.name for bone in self.bones]

    def bone(self, name: str) -> Bone:
        return next(bone for bone in self.bones if bone.name == name)


def leg_name(end: str, side: str, segment: str) -> str:
    return f"{end}_{side}_{segment}"


def ear_name(side: str, segment: int) -> str:
    return f"Ear_{side}_{segment:02d}"


WING_PARENT = "Chest"


def wing_name(side: str, chain: int, segment: int) -> str:
    """A wing chain bone (quadruped_wings.wing_name): the `Wing` prefix the weight smoothing locks and the checks find the wings by."""

    return f"Wing{side}_{chain + 1}_{segment + 1}"


def _largest_gap_split(values: np.ndarray) -> float:
    ordered = np.sort(values)
    gaps = np.diff(ordered)
    index = int(np.argmax(gaps))
    return float((ordered[index] + ordered[index + 1]) / 2)


def faces_plus_y(points: np.ndarray) -> bool:
    """True when the animal faces +Y: its neck end rises higher than its tail end.

    The ends are the vertices beyond the outermost hooves. HOI4 units face -Y, so the
    rig turns such a model half a turn about the vertical before measuring it.
    """

    feet, _dragged = ground_contacts(points)
    hooves = np.concatenate(feet) if feet else points[:0]
    if len(hooves) < 8:
        raise LandmarkError("fewer than 8 vertices near the ground; the legs may not reach it")
    low, high = float(hooves[:, 1].min()), float(hooves[:, 1].max())
    length = float(np.ptp(points[:, 1]))
    minus_end = points[points[:, 1] < low - 0.02 * length]
    plus_end = points[points[:, 1] > high + 0.02 * length]
    ground = float(points[:, 2].min())
    top_minus = float(minus_end[:, 2].max()) if len(minus_end) else ground
    top_plus = float(plus_end[:, 2].max()) if len(plus_end) else ground
    return top_plus > top_minus


# Ground contacts: pieces of the surface under GROUND_BAND of the height, joined in plan over cells CONTACT_CELL of the model's longest
# horizontal side. A piece longer than CONTACT_ELONGATION times its width is a tail lying on the ground, not a foot: on the Tripo dragon
# the dragging tail measures 4.3 and the four feet 1.2 to 1.4.
GROUND_BAND = 0.07
CONTACT_CELL = 0.02
CONTACT_ELONGATION = 2.5


def ground_contacts(points: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """(feet, dragged): the ground contacts as point arrays, the elongated ones (a tail on the ground) apart. Only when more than four
    pieces touch the ground is an elongated one set apart, so a horse's long hoof is never dropped."""

    ground = float(points[:, 2].min())
    height = float(np.ptp(points[:, 2]))
    low = points[points[:, 2] < ground + GROUND_BAND * height]
    cell = CONTACT_CELL * float(max(np.ptp(points[:, 0]), np.ptp(points[:, 1])))
    cells = np.floor(low[:, :2] / max(cell, 1e-12)).astype(np.int64)
    keys = {tuple(item) for item in cells.tolist()}
    label: Dict[Tuple[int, int], int] = {}
    for key in sorted(keys):
        if key in label:
            continue
        label[key] = len(set(label.values()))
        stack = [key]
        while stack:
            a = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    b = (a[0] + dx, a[1] + dy)
                    if b in keys and b not in label:
                        label[b] = label[key]
                        stack.append(b)
    labels = np.array([label[tuple(item)] for item in cells.tolist()]) if len(cells) else np.zeros(0, int)
    pieces = [low[labels == value] for value in sorted(set(labels.tolist()))]
    feet, dragged = [], []
    for piece in pieces:
        spread = np.linalg.svd(piece[:, :2] - piece[:, :2].mean(axis=0), compute_uv=False) if len(piece) > 2 else np.zeros(2)
        elongation = float(spread[0] / max(float(spread[1]), 1e-12)) if len(spread) > 1 else 1.0
        (dragged if elongation > CONTACT_ELONGATION else feet).append(piece)
    if len(feet) < 4:
        return pieces, []
    return feet, dragged


def feet_axis_along_x(points: np.ndarray) -> Optional[bool]:
    """Whether the four feet stand in a line along X (the front pair and the rear pair apart along X): the long axis of the feet's centres
    in plan. None when the model does not stand on four feet or they stand in a square (the long spread under 1.2 times the short)."""

    feet, _dragged = ground_contacts(points)
    if len(feet) != 4:
        return None
    centres = np.array([foot[:, :2].mean(axis=0) for foot in feet])
    values, vectors = np.linalg.eigh(np.cov((centres - centres.mean(axis=0)).T))
    if values[1] < 1.44 * values[0]:
        return None
    return bool(abs(vectors[0, 1]) > abs(vectors[1, 1]))


def _hoof_centres(hooves: np.ndarray, split_y: float, cx: float) -> Dict[str, np.ndarray]:
    """The centre of each leg's ground contact: front and rear split at the largest gap along Y, left and right at the mid-plane."""

    centres: Dict[str, np.ndarray] = {}
    for end, side in LEGS:
        mask = (hooves[:, 1] < split_y) if end == "Front" else (hooves[:, 1] >= split_y)
        mask &= (hooves[:, 0] >= cx) if side == "Left" else (hooves[:, 0] < cx)
        if not mask.any():
            raise LandmarkError(f"no ground contact for the {end.lower()} {side.lower()} leg")
        centres[f"{end}_{side}"] = hooves[mask].mean(axis=0)
    return centres


def _belly_span(hooves: np.ndarray, split_y: float, front_y: float, rear_y: float) -> Tuple[float, float]:
    """Where the belly column runs along Y: behind the hindmost ground point of the front legs and before the foremost of the
    rear legs, so pillar legs in a long stride (an elephant's) stay out of it, and never nearer the hooves' centres than 15% of
    the span."""

    span = rear_y - front_y
    front_back = float(hooves[hooves[:, 1] < split_y][:, 1].max())
    rear_front = float(hooves[hooves[:, 1] >= split_y][:, 1].min())
    start, stop = max(front_y + 0.15 * span, front_back + 0.05 * span), min(rear_y - 0.15 * span, rear_front - 0.05 * span)
    return (start, stop) if stop > start else (front_y + 0.15 * span, rear_y - 0.15 * span)


def _leg_radius(leg_points: np.ndarray, joints: Dict[str, np.ndarray], height: float, width: float) -> float:
    """The median over the leg's three joint bands of its own points' horizontal distance from the band's centre."""

    radii = []
    for joint in ("upper", "middle", "lower"):
        band = leg_points[np.abs(leg_points[:, 2] - joints[joint][2]) < 0.05 * height]
        if len(band) >= 3:
            radii.append(float(np.median(np.linalg.norm(band[:, :2] - joints[joint][:2], axis=1))))
    return float(np.median(radii)) if radii else 0.1 * width


def detect_landmarks(points: np.ndarray, back_z: Optional[float] = None) -> Dict[str, object]:
    """Find the hooves, belly, back, head, tail and saddle of a standing quadruped.

    `back_z` (above the ground) replaces the measured back: a load's cut when the points are the body without the load
    it carries, because the back under the load was cut away with it.
    """

    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 50:
        raise LandmarkError("need at least 50 vertices as an (N, 3) array")
    ground = float(points[:, 2].min())
    p = points - np.array([0.0, 0.0, ground])
    height = float(p[:, 2].max())
    width = float(np.ptp(p[:, 0]))
    length = float(np.ptp(p[:, 1]))
    if min(height, width, length) <= 0:
        raise LandmarkError("the model is flat")
    cx = float((p[:, 0].min() + p[:, 0].max()) / 2)

    feet, dragged = ground_contacts(p)
    hooves = np.concatenate(feet) if feet else p[:0]
    if len(hooves) < 8:
        raise LandmarkError("fewer than 8 vertices near the ground; the legs may not reach it")
    split_y = _largest_gap_split(hooves[:, 1])
    hoof_centres = _hoof_centres(hooves, split_y, cx)
    front_y = float((hoof_centres["Front_Left"][1] + hoof_centres["Front_Right"][1]) / 2)
    rear_y = float((hoof_centres["Rear_Left"][1] + hoof_centres["Rear_Right"][1]) / 2)
    if front_y >= rear_y:
        raise LandmarkError("the front legs are not in front (toward -Y) of the rear legs")
    span = rear_y - front_y
    start, stop = _belly_span(hooves, split_y, front_y, rear_y)
    column = p[(np.abs(p[:, 0] - cx) < 0.12 * width) & (p[:, 1] > start) & (p[:, 1] < stop)]
    if len(column) < 10:
        raise LandmarkError("no body between the front and rear legs")
    belly_z = float(np.percentile(column[:, 2], 2))
    back_z = float(np.percentile(column[:, 2], 98)) if back_z is None else float(back_z)
    if belly_z < 0.1 * height:
        raise LandmarkError("the belly reaches the ground; the legs are not separate")
    mid_y = (front_y + rear_y) / 2

    head_region = p[(p[:, 1] < front_y - 0.04 * length) & (p[:, 2] > belly_z)]
    if len(head_region):
        muzzle_y = float(np.percentile(head_region[:, 1], 1))
        tip = head_region[head_region[:, 1] < muzzle_y + 0.05 * length]
        muzzle = np.array([cx, muzzle_y, float(np.median(tip[:, 2]))])
        top = head_region[head_region[:, 2] > np.percentile(head_region[:, 2], 95)]
        poll = np.array([cx, float(np.median(top[:, 1])), float(np.percentile(head_region[:, 2], 97))])
        if poll[1] <= muzzle[1] + 0.02 * length:
            poll[1] = muzzle[1] + 0.12 * length
    else:
        muzzle = np.array([cx, front_y - 0.15 * length, back_z])
        poll = np.array([cx, front_y - 0.05 * length, back_z + 0.05 * height])

    # A tail that lies on the ground (a dragged contact) counts down to the ground behind the hindmost foot.
    low_tail = (p[:, 1] > float(hooves[:, 1].max()) + 0.02 * length) if dragged else np.zeros(len(p), bool)
    tail_region = p[(p[:, 1] > rear_y + 0.06 * length) & ((p[:, 2] > 0.2 * height) | low_tail)]
    tail: Optional[List[np.ndarray]] = None
    if len(tail_region) >= 10:
        near = tail_region[tail_region[:, 1] < tail_region[:, 1].min() + 0.08 * length]
        root = np.array([cx, float(near[:, 1].min()), float(np.percentile(near[:, 2], 90))])
        distance = np.linalg.norm(tail_region - root, axis=1)
        far = float(distance.max())
        if far > 0.08 * length:
            tip = tail_region[int(np.argmax(distance))]
            points_along = [root]
            for fraction in (1 / 3, 2 / 3):
                band = tail_region[np.abs(distance - far * fraction) < far / 6]
                # A sparse tail (vertices only at its two ends) has no band; follow the straight line.
                points_along.append(band.mean(axis=0) if len(band) >= 3 else root + fraction * (tip - root))
            points_along.append(tip)
            tail = points_along

    saddle_y = front_y + 0.3 * span
    saddle_band = column[np.abs(column[:, 1] - saddle_y) < 0.08 * span]
    saddle_z = float(np.percentile(saddle_band[:, 2], 98)) if len(saddle_band) else back_z

    legs: Dict[str, Dict[str, np.ndarray]] = {}
    for end, side in LEGS:
        key = f"{end}_{side}"
        hoof = hoof_centres[key]
        leg_points = p[
            (p[:, 2] < belly_z)
            & (((p[:, 0] >= cx) if side == "Left" else (p[:, 0] < cx)))
            & (np.abs(p[:, 1] - hoof[1]) < 0.18 * span)
        ]
        joints = {}
        fractions = {"top": None, "upper": 0.95, "middle": 0.47 if end == "Front" else 0.52, "lower": 0.13}
        for joint, fraction in fractions.items():
            if fraction is None:
                continue
            z = belly_z * fraction
            band = leg_points[np.abs(leg_points[:, 2] - z) < 0.05 * height]
            centre = band.mean(axis=0) if len(band) >= 3 else np.array([hoof[0], hoof[1], z])
            joints[joint] = np.array([centre[0], centre[1], z])
        joints["ground"] = np.array([hoof[0], hoof[1] - 0.03 * length, 0.0])
        joints["top"] = np.array([joints["upper"][0], joints["upper"][1] + (0.02 * length if end == "Rear" else 0.0), (belly_z + back_z) / 2])
        joints["radius"] = np.asarray(_leg_radius(leg_points, joints, height, width))
        legs[key] = joints

    return {
        "ground_offset": ground,
        "height": height,
        "width": width,
        "length": length,
        "centre_x": cx,
        "front_y": front_y,
        "rear_y": rear_y,
        "mid_y": mid_y,
        "belly_z": belly_z,
        "back_z": back_z,
        "muzzle": muzzle,
        "poll": poll,
        "tail": tail,
        "saddle": np.array([cx, saddle_y, saddle_z]),
        "legs": legs,
        # behind this (Y) a tail lying on the ground is tail at any height (skin_weights)
        "tail_ground_y": float(hooves[:, 1].max()) + 0.02 * length if dragged and tail else None,
    }


def _t(vector: np.ndarray, ground: float) -> Tuple[float, float, float]:
    return (float(vector[0]), float(vector[1]), float(vector[2] + ground))


def build_layout(landmarks: Dict[str, object]) -> Layout:
    """Place the bones from the landmarks, back in the model's own coordinates."""

    g = float(landmarks["ground_offset"])
    h = float(landmarks["height"])
    cx = float(landmarks["centre_x"])
    front_y, rear_y, mid_y = (float(landmarks[key]) for key in ("front_y", "rear_y", "mid_y"))
    belly_z, back_z = float(landmarks["belly_z"]), float(landmarks["back_z"])
    mid_z = (belly_z + back_z) / 2
    layout = Layout(landmarks=landmarks)
    add = layout.bones.append
    v = np.array
    add(Bone("Root", _t(v([cx, mid_y, 0.0]), g), _t(v([cx, mid_y, 0.1 * h]), g), None, deform=False))
    add(Bone("Pelvis", _t(v([cx, rear_y, mid_z]), g), _t(v([cx, mid_y, mid_z]), g), "Root"))
    add(Bone("Spine", _t(v([cx, mid_y, mid_z]), g), _t(v([cx, front_y, mid_z + 0.03 * h]), g), "Pelvis"))
    withers = v([cx, front_y - 0.04 * float(landmarks["length"]), back_z - 0.04 * h])
    add(Bone("Chest", _t(v([cx, front_y, mid_z + 0.03 * h]), g), _t(withers, g), "Spine"))
    poll = np.asarray(landmarks["poll"], dtype=float)
    neck_mid = withers + 0.5 * (poll - withers)
    add(Bone("Neck_01", _t(withers, g), _t(neck_mid, g), "Chest"))
    add(Bone("Neck_02", _t(neck_mid, g), _t(poll, g), "Neck_01"))
    add(Bone("Head", _t(poll, g), _t(np.asarray(landmarks["muzzle"], dtype=float), g), "Neck_02"))
    tail = landmarks.get("tail")
    if tail:
        parent = "Pelvis"
        for index in range(3):
            name = f"Tail_{index + 1:02d}"
            add(Bone(name, _t(np.asarray(tail[index]), g), _t(np.asarray(tail[index + 1]), g), parent))
            parent = name
    for side, ear in (landmarks.get("ears") or {}).items():
        # an ear's chain (quadruped_ears.detect_ears) is in the model's own coordinates already
        joints = [tuple(float(value) for value in ear[key]) for key in ("root", "middle", "tip")]
        add(Bone(ear_name(side, 1), joints[0], joints[1], str(ear.get("parent", "Head"))))
        add(Bone(ear_name(side, 2), joints[1], joints[2], ear_name(side, 1)))
    for side, wing in (landmarks.get("wings") or {}).items():
        # a wing's chains (quadruped_wings.detect_wings) fan from its root at the shoulder, in the model's own coordinates
        joints = np.asarray(wing["joints"], dtype=float)
        for chain in range(joints.shape[0]):
            parent = WING_PARENT
            for segment in range(joints.shape[1] - 1):
                name = wing_name(side, chain, segment)
                add(Bone(name, tuple(float(v) for v in joints[chain, segment]), tuple(float(v) for v in joints[chain, segment + 1]), parent))
                parent = name
    for end, side in LEGS:
        joints = landmarks["legs"][f"{end}_{side}"]
        chain = [joints["top"], joints["upper"], joints["middle"], joints["lower"], joints["ground"]]
        parent = "Chest" if end == "Front" else "Pelvis"
        for index, segment in enumerate(LEG_SEGMENTS):
            name = leg_name(end, side, segment)
            add(Bone(name, _t(chain[index], g), _t(chain[index + 1], g), parent))
            parent = name
    saddle = np.asarray(landmarks["saddle"], dtype=float)
    # An attach node points along +Y with no roll, so io_pdx_mesh exports it with an identity
    # rotation, as vanilla cavalry_horse.mesh stores its Saddle_Node; a node pointing up exports
    # turned 90 degrees and the engine would tip the attached rider over.
    carrier = "Spine"
    if landmarks.get("load"):
        # A carried load has its own bone, a child of the Spine that never turns: the load rides it rigidly, and the weight
        # smoothing locks it without locking the torso.
        add(Bone(LOAD_BONE, _t(saddle, g), _t(saddle + v([0.0, 0.1 * h, 0.0]), g), "Spine"))
        carrier = LOAD_BONE
    add(Bone(SADDLE_NODE, _t(saddle, g), _t(saddle + v([0.0, 0.1 * h, 0.0]), g), carrier, deform=False))
    return layout


def _segment_distance(points: np.ndarray, head: np.ndarray, tail: np.ndarray) -> np.ndarray:
    direction = tail - head
    length2 = float(direction @ direction) or 1e-12
    t = np.clip(((points - head) @ direction) / length2, 0.0, 1.0)
    closest = head + t[:, None] * direction
    return np.linalg.norm(points - closest, axis=1)


def _hanging_tail_only(allowed, q, distance, bones, behind_y: float, min_z: float) -> None:
    """Give a tail that hangs below the belly to the tail bones alone.

    Such a tail is behind the rear legs and nearer the tail chain than any leg bone. Leg weights
    there tear it when the tail lifts (the ZIN grave horse's trot).
    """

    tail_bones = [index for index, bone in enumerate(bones) if bone.deform and bone.name.startswith("Tail_")]
    leg_bones = [index for index, bone in enumerate(bones) if bone.deform and bone.name.startswith(("Front_", "Rear_"))]
    if not tail_bones or not leg_bones:
        return
    hanging = np.flatnonzero(
        (q[:, 1] > behind_y)
        & (q[:, 2] > min_z)
        & (distance[:, tail_bones].min(axis=1) < distance[:, leg_bones].min(axis=1))
    )
    allowed[np.ix_(hanging, leg_bones)] = False
    allowed[np.ix_(hanging, tail_bones)] = True


def _claim_leftovers(allowed, leg_base: Dict[int, np.ndarray], q, distance, bones, behind_y: float, min_z: float) -> None:
    """Skin no region claimed goes to its nearest leg when it is low enough for one, a hanging tail to the tail alone, and the
    rest to the torso bones."""

    unclaimed = ~allowed.any(axis=1)
    for index, base in leg_base.items():
        allowed[:, index] |= base & unclaimed
    _hanging_tail_only(allowed, q, distance, bones, behind_y, min_z)
    orphans = ~allowed.any(axis=1)
    if orphans.any():
        for index, bone in enumerate(bones):
            if bone.deform and bone.name in {"Pelvis", "Spine", "Chest"}:
                allowed[orphans, index] = True


def _near_legs(q: np.ndarray, legs: Dict[str, Dict[str, np.ndarray]], leg_keys: List[str], length: float) -> np.ndarray:
    """(N, 4): whether each point lies within LEG_REACH of a leg's radii of that leg's own line.

    A leg's bones take that skin, so a trunk hanging beside a front leg (an elephant's) or straps under the belly never follow a
    leg. On the elephant the leg skin lies within 2 radii and the nearest other skin beyond 2.5. Skin farther out that no other
    region claims (a hoof's spur) still goes to its nearest leg (`skin_weights`)."""

    near = np.ones((len(q), len(leg_keys)), dtype=bool)
    for column, key in enumerate(leg_keys):
        joints = legs[key]
        if "radius" not in joints:
            continue
        hoof = np.asarray(joints["ground"], dtype=float) + np.array([0.0, 0.03 * length, 0.0])  # the hoof's centre, not its toe
        chain = [np.asarray(joints[name], dtype=float) for name in ("top", "upper", "middle", "lower")] + [hoof]
        reach = np.min([_segment_distance(q, chain[i], chain[i + 1]) for i in range(4)], axis=0)
        near[:, column] = reach < LEG_REACH * float(joints["radius"])
    return near


def skin_weights(points: np.ndarray, layout: Layout, max_influences: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    """Return (bone indices, weights) per vertex, each row normalized, at most `max_influences` bones.

    Each vertex may only use the bones of its own region: a leg vertex its own
    leg's bones (and the body bone at the top of that leg), a head vertex the
    neck and head, a tail vertex the tail. Within that set the weight falls off
    with the fourth power of the distance to each bone segment.
    """

    lm = layout.landmarks
    g = float(lm["ground_offset"])
    h = float(lm["height"])
    q = points - np.array([0.0, 0.0, g])
    names = layout.names()
    bones = layout.bones
    distance = np.stack([
        _segment_distance(points, np.array(bone.head), np.array(bone.tail)) for bone in bones
    ], axis=1)
    allowed = np.zeros_like(distance, dtype=bool)
    belly_z = float(lm["belly_z"])
    front_y, rear_y, mid_y = (float(lm[key]) for key in ("front_y", "rear_y", "mid_y"))
    length = float(lm["length"])
    legs = lm["legs"]
    leg_keys = [f"{end}_{side}" for end, side in LEGS]
    columns = np.array([
        (legs[key]["upper"][:2] + legs[key]["lower"][:2]) / 2 for key in leg_keys
    ])
    nearest_leg = np.argmin(np.linalg.norm(q[:, None, :2] - columns[None, :, :], axis=2), axis=1)
    in_leg = q[:, 2] < belly_z + 0.02 * h
    in_body = q[:, 2] > belly_z - 0.06 * h
    near_leg = _near_legs(q, legs, leg_keys, length)
    leg_base: Dict[int, np.ndarray] = {}
    for index, bone in enumerate(bones):
        if not bone.deform:
            continue
        name = bone.name
        if name.startswith(("Front_", "Rear_")):
            key = "_".join(name.split("_")[:2])
            mask = in_leg & (nearest_leg == leg_keys.index(key))
            if not name.endswith("_Upper"):
                mask &= q[:, 2] < belly_z
            leg_base[index] = mask
            allowed[:, index] = mask & near_leg[:, leg_keys.index(key)]
        elif name.startswith("Tail_"):
            tail_root_y = float(np.asarray(lm["tail"][0])[1]) if lm.get("tail") else rear_y
            lying = q[:, 1] > float(lm["tail_ground_y"]) if lm.get("tail_ground_y") is not None else np.zeros(len(q), bool)
            allowed[:, index] = (q[:, 1] > tail_root_y - 0.02 * length) & (in_body | lying)
        elif name in {"Neck_01", "Neck_02", "Head"}:
            allowed[:, index] = q[:, 1] < front_y + 0.06 * length
        elif name == "Pelvis":
            allowed[:, index] = in_body & (q[:, 1] > mid_y - 0.12 * length)
        elif name == "Chest":
            allowed[:, index] = in_body & (q[:, 1] < mid_y + 0.12 * length)
        elif name == "Spine":
            allowed[:, index] = in_body
    _claim_leftovers(allowed, leg_base, q, distance, bones, rear_y + 0.06 * length, 0.2 * h)
    falloff = 0.02 * h
    raw = np.where(allowed, 1.0 / np.power(distance + falloff, 4), 0.0)
    order = np.argsort(-raw, axis=1)[:, :max_influences]
    picked = np.take_along_axis(raw, order, axis=1)
    picked[picked < picked[:, :1] * 0.02] = 0.0
    picked = picked / picked.sum(axis=1, keepdims=True)
    return order, picked


@dataclass
class Gait:
    cycle_frames: int
    phases: Dict[str, float]
    duty: float
    swing_degrees: float
    flex_degrees: float
    spine_degrees: float = 0.0
    head_degrees: float = 3.0


GAITS = {
    "quadruped_walk": Gait(32, {"Rear_Left": 0.0, "Front_Left": 0.25, "Rear_Right": 0.5, "Front_Right": 0.75}, 0.65, 16.0, 45.0, 1.5, 4.0),
    "quadruped_trot": Gait(20, {"Front_Left": 0.0, "Rear_Right": 0.0, "Front_Right": 0.5, "Rear_Left": 0.5}, 0.5, 22.0, 60.0, 2.0, 3.0),
    "quadruped_gallop": Gait(14, {"Rear_Left": 0.0, "Rear_Right": 0.12, "Front_Left": 0.42, "Front_Right": 0.54}, 0.4, 32.0, 75.0, 6.0, 6.0),
}
ROLE_FRAMES = {"quadruped_idle": 72, "quadruped_charge": 36, "quadruped_rear": 48, "quadruped_brace": 48, "quadruped_collapse": 48, "quadruped_flee": 40}
DEFAULT_STYLE = {
    "idle": "quadruped_idle",
    "move": "quadruped_trot",
    "attack": "quadruped_charge",
    "defend": "quadruped_rear",
    "retreat": "quadruped_gallop",
    "death": "quadruped_collapse",
}
LOOPING = {"quadruped_idle", "quadruped_walk", "quadruped_trot", "quadruped_gallop", "quadruped_flee"}
LEG_REACH = 2.2
# Pillar legs: a leg whose radius is more than GRAVIPORTAL of its length (the belly's height) is a graviportal leg, an
# elephant's (0.22 to 0.25), not a runner's (a horse's is about 0.05). Its joints bend FLEX_REFERENCE over that share of a
# runner's, it never gallops, and its attack is carried by the head.
GRAVIPORTAL = 0.15
FLEX_REFERENCE = 0.06
FLEXING = ("_Lower", "_Cannon", "_Hoof")
# A graviportal animal walks where a runner trots, flees at a trot swinging away where it gallops, attacks by rearing (a stamp, its
# forefeet up) and defends braced: a fresh review read the charge's lunging head as crushed into the chest and the full rear as the attack.
HEAVY_GAITS = {"quadruped_trot": "quadruped_walk", "quadruped_gallop": "quadruped_flee", "quadruped_charge": "quadruped_rear", "quadruped_rear": "quadruped_brace"}
HEAVY_LUNGE = 1.0
# Of a runner's rear: a loaded elephant lifts its forefeet, it does not stand up. At 0.4 the round 9 war elephant's attack read as the idle
# from the map camera (TRIPO-MAP-READ 0.15), at 0.6 it reads 0.24 (played offline on its exported mesh).
HEAVY_PITCH = 0.6
# A pillar leg lifted in a rear reaches forward from the shoulder this share of a runner's: its fold lifts the foot, and the full reach
# at HEAVY_PITCH 0.6 stretched the skin of the elbow against the chest (offline on the round 9 war elephant: 30 deformed edges, 14 at 0.6).
HEAVY_REACH = 0.6
REAR_HEAD = -10.0  # the head's turn at the top of a rear (negative raises it)
# The lifted foreleg of a rear reaches forward from the elbow and folds back at the knee as vanilla's horse attack does: in
# `cavalry_horse_charge` the leading forearm reaches 74 degrees forward of the body's down direction with the knee bent 59 degrees
# (measured on the game's files). The shoulder takes REAR_SHOULDER of the reach and the elbow the rest, and a pillar leg reaches HEAVY_REACH
# as far. Run 11 folded the cannon 85 degrees back under a forearm held upright, and a fresh review read the raised forelegs as short stubs.
# Offline on its exported mesh the whole horse reach on the pillar leg stretched 2.1% of the near foreleg's root (TRIPO-LEG-ROOT-STRETCH) and
# 25 edges by the kit's measure, HEAVY_REACH of it 0.4% and 3. The knee's bend is counted from the leg's own rest fold (knee_rest_fold): the
# war elephant's cannon slants 21 degrees forward of its forearm at rest, so run 12's fold of 35 degrees bent its knee only 14 from straight
# and the leg still read as a stub. The whole 59 from straight on the pillar leg stretched 126 edges at the knee by 1.3 times or more and 19
# by the kit's measure (offline on run 12's mesh), HEAVY_REACH of it 32 and 6.
HORSE_FOREARM_REACH = 74.0
HORSE_KNEE_FOLD = 59.0
REAR_SHOULDER = 55.0
# No whole-body turn about the vertical in a heavy move, defend or retreat: two fresh reviews of run 7 read the walk's 10 degree sway as the
# unit veering off its heading, the defend's held turn as a turn in place and the retreat's turn away and back as a turn. Under a tall load
# only the head, the forelegs and a rock of the whole body show in the map camera (lib/map_read.py has the readings). The neck cannot show
# them: on the war elephant of run 8 the tower's front is one skin with the head and neck, and 10 degrees at the first neck bone tore 29% of
# the seam's edges (TRIPO-LOAD-SEAM, limit 2%) where the head bone alone turns 30 degrees for 1.6%. So the head bone does the nodding,
# raising and shaking, the neck bones turn a few degrees, and the numbers below are nominal (the stance's neck share, 0.55 on that elephant,
# scales them).
WALK_HEAD_SWING = 22.0  # degrees the walk swings the head to each side once a stride (44 with a body rock read as turning 25 to 30 degrees)
WALK_NOD = 8.0  # degrees of the head's nod, twice a stride
GUARD_PITCH = 0.0  # degrees the defend rocks the body back about the hind feet: any lifts the forefeet (4 degrees 4% of the height), and a review read the lift as a small rear
# The defend raises the head GUARD_HEAD_UP and then lowers it GUARD_HEAD_DOWN with the tusks forward, held through most of the clip: a fresh
# review of run 11 could not tell a toss up and down from the idle at map size.
GUARD_HEAD_UP = 30.0
GUARD_HEAD_DOWN = 45.0
GUARD_NECK = 0.0  # degrees the neck's two bones turn with it (5 with the head tore the seam, 14%)
GUARD_SPREAD = 20.0  # degrees the defend spreads the forelegs apart at the shoulder
# The forequarters step back over planted feet: the body shifts back and every leg leans forward this far at the shoulder and hip, with
# the hoof turned back so it stays flat: as far as a pillar hip or shoulder turns (PILLAR_SWING, a runner's walk). On run 12's war elephant
# 12 degrees read 0.097 from the idle in the map camera and 16 0.107, with no leg root stretched.
GUARD_LEAN = GAITS["quadruped_walk"].swing_degrees
# degrees the defend spreads each ear forward about its root (no farther than its room, quadruped_ears.ear_room). Run 12 spread them 30
# degrees and tore 2.4% of the seam where the tower meets the swept-back ear (TRIPO-LOAD-SEAM, limit 2%), 20 none, for the same map reading.
GUARD_EAR_SPREAD = 20.0
# Ears (quadruped_ears.py) follow the head with a little lag: the outer bone turns back toward where the head was EAR_LAG_FRAMES ago by
# EAR_LAG_SHARE of the difference. A lag at the root (both bones) stretched the ear's root skin (offline on run 11's mesh: 121 edges changed
# by 1.3 times or more in the retreat).
EAR_LAG_FRAMES = 3  # an eighth of a second at the rig's 24 frames a second
EAR_LAG_SHARE = 0.5
EAR_HEAD_CHAIN = ("__root_pitch__", "Neck_01", "Neck_02", "Head")
EAR_ROOT_SHARE = 0.6  # of an ear's turn made at its root, the rest at its middle
RETREAT_HEAD = 40.0  # degrees the retreat raises the head in alarm, held while the legs step backward
RETREAT_TOSS = 36.0  # degrees the raised head shakes to each side, twice in the clip
RETREAT_NECK = 0.0  # degrees the neck's first bone lifts with it (any turn with the head tore the seam)
RETREAT_SPREAD = 15.0  # degrees the retreat spreads the forelegs apart at the shoulder
# A pillar leg's hip and shoulder turn no farther than a runner's walk swings them. The trot's 22 degrees at the hip stretched the
# war elephant's hind thigh and flank against the held torso in its retreat (TRIPO-LEG-ROOT-STRETCH 2.4%), and the defend's 25 degrees
# at the shoulder its foreleg's root (5.3%). At the walk's 16 degrees both measure 0.6% (offline on run 4's weights).
PILLAR_SWING = GAITS["quadruped_walk"].swing_degrees
NECK_REFERENCE = 0.3  # a runner's neck (withers to poll) over its body length; a shorter neck bends that much less
COLLAPSE_ROLL = 82.0
COLLAPSE_ROLL_STEP = 6.0
LOAD_ROLL_EXTRA = 24.0  # degrees past the load's roll limit the search for a lying tower starts
LOAD_ROLL_MOST = 110.0
# A body rolled past 90 degrees (the tower resting on the ground) points its legs sideways, locked in two stiff pairs, the lower pair 17% of
# the height in the air (run 9, a review's major). Gravity drops them: each leg bends back toward the ground about the body's long axis, the
# lower pair (on the ground side) by DEATH_LEG_DROP at the hip, knee, ankle and foot and the upper pair by DEATH_LEG_HANG_SHARE of that. Offline
# on the run 8 mesh at a roll of 98 degrees the lower pair's lowest point falls from 0.17 to 0.05 of the height. The turn is made below the hip: at
# the hip alone 16 degrees stretched 3.5% of the leg roots (TRIPO-LEG-ROOT-STRETCH, limit 2%), here 1.4%.
DEATH_LEG_DROP = {"Upper": 10.0, "Lower": 42.0, "Cannon": 42.0, "Hoof": 22.0}
# The hind legs fold half as far (COLLAPSE_HIND_FOLD) and reach the ground with less turn at the thigh: a fresh review of run 11 saw the
# hind thigh and hip squash into a lumpy mass. Offline on its exported mesh the hind skin strained by 1.3 times or more over the lying
# frames covers 2.1 square units with the thigh at 30 degrees against 3.2 at 42, and the lower hind leg ends 5.4% of the height up (limit 6%).
DEATH_HIND_DROP = {"Upper": 10.0, "Lower": 30.0, "Cannon": 42.0, "Hoof": 22.0}
DEATH_LEG_HANG_SHARE = 0.5
COLLAPSE_RELAX = 0.5  # share of the shoulders', hips' and elbows' bend a dead body relaxes once it lies
COLLAPSE_HIND_FOLD = 0.5  # the hind legs' fold in a death as a share of the forelegs'
# A dead body's legs buckle this share of a full fold: two fresh reviews of run 13 saw the shoulder, hip, thighs and knees puff up and turn
# lumpy where the legs folded under the lying body. Offline on its exported mesh the skin of the legs and torso changed by 1.3 times or
# more over the lying frames covers 7.4 square units at a full fold and 2.2 at 0.6, the lower legs still on the ground (5.2% of the
# height up, limit 6%).
DEATH_FOLD = 0.6
DOWN_TOLERANCE = 0.01  # of the body's height: how much lower than the torso another part may end in a death
# The death turns the neck back against the roll only when the head or neck is what holds the dead body up, and at most this far. Round 9
# turned it 60 degrees against an 82 degree roll to gain 0.8% of the height while the tower held the body up: the neck and the ear roots
# under the tower's front stretched into a band (TRIPO-LOAD-SEAM 6.0%).
NECK_PARTS = ("Neck_01", "Neck_02", "Head")
NECK_LIFTS = (10.0, -10.0, 20.0, -20.0, 30.0, -30.0)
LOADED_STILL = ("Pelvis", "Spine", "Chest")
# Under a load the neck and head turn half as far. The load rests against them: Tripo makes a howdah's front one skin with the ear roots and
# the top of the head, so the load's ring (quadruped_load.bind_load) reaches them, and every turn of the head against the load stretches
# that skin. On the round 9 war elephant's death (played offline on its exported mesh) the full turn stretched 1.7% of the seam's edges
# (TRIPO-LOAD-SEAM), half of it 0.4%.
LOADED_NECK = 0.5
DISPLAY_STYLES = ("quadruped_walk", "quadruped_brace", "quadruped_flee")

Rotation = Tuple[Tuple[float, float, float], float]


# A winged quadruped (a dragon, unit type `winged_quadruped`) plays its own styles: the body moves as the quadruped style it is built on
# (WINGED_BASE) and the wings follow quadruped_wings.role_pose. Frames at the rig's 24 a second.
WINGED_FRAMES = {"winged_idle": 72, "winged_walk": 32, "winged_rear": 56, "winged_guard": 48, "winged_flee": 64, "winged_collapse": 64}
WINGED_BASE = {"winged_idle": "quadruped_idle", "winged_walk": "quadruped_walk", "winged_rear": "quadruped_rear",
               "winged_guard": "quadruped_brace", "winged_flee": "quadruped_walk", "winged_collapse": "quadruped_collapse"}
WINGED_CYCLES = {"winged_walk": 1, "winged_flee": 2}  # gait strides per clip
ROLE_FRAMES.update(WINGED_FRAMES)
LOOPING |= {"winged_idle", "winged_walk", "winged_flee"}
# The retreat turns away from the unit's heading and back while it walks with beating wings: FLEE_TURN degrees about the vertical through the
# body's middle, in over the first FLEE_TURN_IN of the clip and out over its last, so the clip starts and ends at the heading (TRIPO-LOOP-HEADING).
FLEE_TURN = -30.0
FLEE_TURN_IN = 0.25
# The attack: at the top of the rear the neck and head lunge forward and down (degrees at Neck_01, Neck_02 and Head, positive pitches a
# raised neck forward), between LUNGE_START and LUNGE_END of the clip.
LUNGE = {"Neck_01": 28.0, "Neck_02": 18.0, "Head": 12.0}
LUNGE_START, LUNGE_END = 0.3, 0.8
# The defend crouches the neck forward and low under the raised wings (degrees at Neck_01, Neck_02 and Head, positive forward and down).
GUARD_NECK_LOW = {"Neck_01": 30.0, "Neck_02": 20.0, "Head": 0.0}


def frame_count(style: str) -> int:
    return GAITS[style].cycle_frames if style in GAITS else ROLE_FRAMES[style]


# How a dead winged quadruped comes to rest on its side, chosen on its final pose (`choose_winged_rest`), one part at a time. Each part is
# measured by its lowest point over the lying torso's lowest, as a share of the height:
# - legs: the legs underneath bend toward the ground by the largest of LEG_DROP_SHARES of the death's leg drop (DEATH_LEG_DROP) that keeps them
#   no lower than the torso (DOWN_TOLERANCE), so the body rests on its torso, not on a hoof;
# - wings: the wing underneath lifts from the slope `quadruped_wings.lying_pose` gives it by the least of WING_LIFTS (degrees) that keeps its
#   far bones (the last of each chain: a lift turns about the root, so the bones by the root go where the body goes) no lower than the torso,
#   so a wing never holds the body up;
# - tail: it turns at its root (degrees, positive lifts it) by the one of TAIL_LIFTS that brings its lowest point nearest the torso's without
#   going under it, so it neither holds the body up nor hangs in the air;
# - neck: it turns toward the ground by the least of NECK_DROPS that brings the head within HEAD_REST of the torso's lowest point.
LEG_DROP_SHARES = (1.0, 0.75, 0.5, 0.25, 0.0)
WING_LIFTS = tuple(float(value) for value in range(0, 65, 5))
TAIL_LIFTS = tuple(float(value) for value in range(-40, 65, 5))
NECK_DROPS = tuple(float(value) for value in range(0, 70, 10))
HEAD_REST = 0.04


def choose_winged_rest(evaluate) -> Dict[str, float]:
    """The dead body's rest. `evaluate(**chosen)` poses the final frame with the death's `leg_drop`, `wing_lift`, `tail_lift` and `neck_drop`
    and returns the lowest point over the torso's lowest of the `legs`, `wings`, `tail` and `head` (shares of the height)."""

    chosen = {"leg_drop": LEG_DROP_SHARES[-1], "wing_lift": WING_LIFTS[-1], "tail_lift": 0.0, "neck_drop": 0.0}
    for share in LEG_DROP_SHARES:
        if evaluate(**{**chosen, "leg_drop": share, "wing_lift": WING_LIFTS[-1]})["legs"] >= -DOWN_TOLERANCE:
            chosen["leg_drop"] = share
            break
    for lift in WING_LIFTS:
        if evaluate(**{**chosen, "wing_lift": lift})["wings"] >= -DOWN_TOLERANCE:
            chosen["wing_lift"] = lift
            break
    fits = [(gap, lift) for lift in TAIL_LIFTS for gap in (evaluate(**{**chosen, "tail_lift": lift})["tail"],) if gap >= -DOWN_TOLERANCE]
    chosen["tail_lift"] = min(fits)[1] if fits else TAIL_LIFTS[-1]
    best = None
    for drop in NECK_DROPS:
        head = evaluate(**{**chosen, "neck_drop": drop})["head"]
        if best is None or abs(head) < best[0]:
            best = (abs(head), drop)
        if -DOWN_TOLERANCE <= head <= HEAD_REST:
            best = (0.0, drop)
            break
    chosen["neck_drop"] = best[1]
    return chosen


def _winged_pose(style: str, frame: float, layout: Layout, ears: bool) -> Dict[str, List[Rotation]]:
    """A winged quadruped's pose: the body of its WINGED_BASE style at the same point of the clip (strides at the gait's own pace), its
    own neck, head and tail turns, and the wings (`quadruped_wings.role_rows`). A tail that lies on the ground only swings sideways or
    lifts: any turn down would sink it and lift the whole body off its feet."""

    import quadruped_wings as qw

    total = frame_count(style)
    loop = style in LOOPING
    t = (frame % total) / total if loop else min(1.0, frame / max(total - 1, 1))
    base = WINGED_BASE[style]
    base_total = frame_count(base)
    if base in GAITS:
        base_frame = (t * WINGED_CYCLES.get(style, 1) * base_total) % base_total
    elif base in LOOPING:
        base_frame = t * base_total
    else:
        base_frame = t * (base_total - 1)
    pose = dict(pose_at(base, base_frame, layout, ears=ears))
    names = set(layout.names())
    tails = [name for name in ("Tail_01", "Tail_02", "Tail_03") if name in names]
    if style in ("winged_walk", "winged_flee"):
        for index, name in enumerate(tails):
            pose[name] = [(Z_AXIS, (8.0 - 2.0 * index) * math.sin(2 * math.pi * t * WINGED_CYCLES.get(style, 1) - 0.6 * index))]
    if style == "winged_flee":
        turn = _smooth(min(1.0, t / FLEE_TURN_IN)) * (1 - _smooth(max(0.0, (t - 1 + FLEE_TURN_IN) / FLEE_TURN_IN)))
        pose["__root_turn__"] = [(Z_AXIS, FLEE_TURN * turn)]
    if style == "winged_rear":
        lunge = _smooth(max(0.0, min(1.0, (t - LUNGE_START) / 0.15))) * (1 - _smooth(max(0.0, (t - LUNGE_END + 0.15) / 0.15)))
        for name, degrees in LUNGE.items():
            if name in names:
                pose[name] = pose.get(name, []) + [(X_AXIS, degrees * lunge)]
        # the tail keeps its world pitch while the body rears about the hind feet (else it sinks and the feet lift off)
        pitch = sum(degrees for axis, degrees in pose.get("__root_pitch__", []) if tuple(axis) == X_AXIS)
        if tails:
            pose[tails[0]] = [(X_AXIS, -pitch)]
    if style == "winged_collapse":
        # The dead body lies on its side (the roll `quadruped_rig.tune_collapse` picks). The tail turns back against the roll so it lies
        # flat as it lay, lifted at its root by `tail_lift` (the least turn that keeps it off the ground, `tune_winged_collapse`), and
        # the neck turns toward the ground by `neck_drop` so the head lies on it.
        death = layout.landmarks.get("death") or {}
        roll = float(death.get("roll", COLLAPSE_ROLL))
        fall = _collapse_fall(t)
        if tails:
            pose[tails[0]] = [(X_AXIS, float(death.get("tail_lift", 0.0)) * fall), (Y_AXIS, -roll * fall)]
            for name in tails[1:]:
                pose[name] = [(X_AXIS, -0.5 * float(death.get("tail_lift", 0.0)) * fall)]
        # the legs underneath drop toward the ground only `leg_drop` of the death's full drop (`choose_winged_rest`)
        lower = "Right" if roll < 0 else "Left"
        share = float(death.get("leg_drop", 1.0))
        for end in ("Front", "Rear"):
            for segment in LEG_SEGMENTS:
                name = leg_name(end, lower, segment)
                if name in pose:
                    pose[name] = [(axis, degrees * share) if tuple(axis) == Y_AXIS else (axis, degrees) for axis, degrees in pose[name]]
        drop = math.copysign(float(death.get("neck_drop", 0.0)), roll) * fall
        if "Neck_01" in names:
            pose["Neck_01"] = pose.get("Neck_01", []) + [(Y_AXIS, 0.6 * drop)]
        if "Neck_02" in names:
            pose["Neck_02"] = pose.get("Neck_02", []) + [(Y_AXIS, 0.4 * drop)]
    if style == "winged_guard":
        envelope = _brace_envelope(t)
        # The wings and the neck carry the guard: the legs stand planted (the brace's step back and leaning legs stretched the skin where
        # the dragon's heavy shoulders and thighs meet the torso, 2.2% of the edges in the offline play).
        pose.pop("__root_shift__", None)
        pose.pop("__root_pitch__", None)
        for end, side in LEGS:
            for segment in LEG_SEGMENTS:
                pose.pop(leg_name(end, side, segment), None)
        for name, degrees in GUARD_NECK_LOW.items():
            if name in names:
                pose[name] = [(X_AXIS, degrees * envelope)]
    yaw = sum(degrees for axis, degrees in pose.get("__root_turn__", []) if tuple(axis) == Z_AXIS)
    pose.update(qw.role_rows(style, t, layout, yaw))
    return pose


def _smooth(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def _leg_rotations(gait: Gait, t: float, end: str, side: str) -> Dict[str, List[Rotation]]:
    """Armature-space X rotations (degrees) for one leg at cycle time t in [0, 1)."""

    u = (t + gait.phases[f"{end}_{side}"]) % 1.0
    if u < gait.duty:
        swing = gait.swing_degrees * (1 - 2 * u / gait.duty)
        lift = 0.0
    else:
        s = (u - gait.duty) / (1 - gait.duty)
        swing = gait.swing_degrees * (-1 + 2 * _smooth(s))
        lift = math.sin(math.pi * s)
    # A negative X rotation swings a downward bone forward (toward -Y).
    rows: Dict[str, List[Rotation]] = {}
    prefix = f"{end}_{side}_"
    rows[prefix + "Upper"] = [(X_AXIS, -swing)]
    if end == "Front":
        rows[prefix + "Lower"] = [(X_AXIS, 0.25 * gait.flex_degrees * lift)]
        rows[prefix + "Cannon"] = [(X_AXIS, gait.flex_degrees * lift)]
        rows[prefix + "Hoof"] = [(X_AXIS, 0.4 * gait.flex_degrees * lift)]
    else:
        rows[prefix + "Lower"] = [(X_AXIS, 0.35 * gait.flex_degrees * lift)]
        rows[prefix + "Cannon"] = [(X_AXIS, -0.6 * gait.flex_degrees * lift)]
        rows[prefix + "Hoof"] = [(X_AXIS, 0.3 * gait.flex_degrees * lift)]
    return rows


def leg_stance(landmarks: Dict[str, object]) -> Dict[str, float]:
    """The legs' median radius over their length (the belly's height), and the share of a runner's joint bend they get."""

    legs = landmarks.get("legs") or {}
    radii = [float(np.asarray(joints["radius"])) for joints in legs.values() if "radius" in joints]
    belly = float(landmarks.get("belly_z") or 0.0)
    ratio = float(np.median(radii)) / belly if radii and belly > 0 else 0.0
    neck = 1.0
    if landmarks.get("poll") is not None and landmarks.get("length"):
        withers = np.array([0.0, float(landmarks["front_y"]), float(landmarks["back_z"])])
        reach = float(np.linalg.norm((np.asarray(landmarks["poll"], dtype=float) - withers)[1:])) / float(landmarks["length"])
        neck = min(1.0, reach / NECK_REFERENCE)
    return {"ratio": ratio, "graviportal": ratio > GRAVIPORTAL, "flex": min(1.0, FLEX_REFERENCE / ratio) if ratio > 0 else 1.0, "neck": neck}


def stance_style(style: str, landmarks: Dict[str, object]) -> str:
    """A graviportal animal walks where a runner trots and flees at a trot (an elephant's amble) where a runner gallops."""

    return HEAVY_GAITS.get(style, style) if leg_stance(landmarks)["graviportal"] else style


def _bent(pose: Dict[str, List[Rotation]], flex: float, neck: float = 1.0, load: Optional[Dict[str, object]] = None,
          free: frozenset = frozenset()) -> Dict[str, List[Rotation]]:
    """Scale the bend of every leg joint below the shoulder and hip by `flex` (but the `free` ones), and of the neck by `neck` (a short neck
    bends less, a loaded one `LOADED_NECK` of that). Under a load the head turns by the neck's share too."""

    def share(name: str) -> float:
        if name.startswith(("Front_", "Rear_")) and name.endswith(FLEXING) and name not in free:
            return flex
        if name.startswith("Neck_") or (load and name == "Head"):
            return neck
        return 1.0

    return {name: [(axis, degrees * share(name)) for axis, degrees in rows] for name, rows in pose.items()}


def pose_at(style: str, frame: int, layout: Layout, ears: bool = True) -> Dict[str, List[Rotation]]:
    """Each bone's armature-space rotations (axis, degrees) at `frame`; the keys `__root_pitch__`, `__root_yaw__` and `__root_roll__` turn
    the whole body and `__root_shift__` moves it ((axis, distance) rows in the model's units). `ears` adds the ear bones' turns (`_ear_pose`).

    Looping styles return the same pose at frame 0 and at `frame_count(style)`.
    """

    if style in WINGED_FRAMES:
        return _winged_pose(style, frame, layout, ears)
    names = set(layout.names())
    load = layout.landmarks.get("load") or {}
    stance = leg_stance(layout.landmarks)
    total = frame_count(style)
    t = (frame % total) / total if style in LOOPING else min(1.0, frame / max(total - 1, 1))
    pose: Dict[str, List[Rotation]] = {}
    free: set = set()  # leg joints that bend as far as a runner's whatever the build
    has_tail = "Tail_01" in names
    if style in GAITS:
        _gait(pose, _pillar_gait(GAITS[style], stance), t, has_tail)
        if style == "quadruped_walk" and stance["graviportal"]:
            # A heavy walk swings the head to each side once a stride, nods it twice, and its lifted feet fold fully (they carry no
            # weight). The body keeps its heading. Under a tall load the feet barely change the map silhouette, so a plain walk read as the
            # idle (TRIPO-MAP-READ 0.01), and a sway of the whole forequarters read as veering.
            swing = math.sin(2 * math.pi * t)
            pose["Head"] = pose["Head"] + [(Z_AXIS, WALK_HEAD_SWING * swing), (X_AXIS, WALK_NOD * math.sin(4 * math.pi * t + 0.8))]
            pose["Neck_01"] = []
            free = {leg_name(end, side, segment) for end, side in LEGS for segment in ("Lower", "Cannon", "Hoof")}
    elif style == "quadruped_flee":
        # Two trot strides run backward: the legs step back, the head rises in alarm and shakes (a turn about the vertical, held or not,
        # read as a turn or as the defend's mirror in runs 5 to 7).
        reverse = 1.0 - (2.0 * t) % 1.0
        _gait(pose, _pillar_gait(GAITS["quadruped_trot"], stance), reverse, has_tail)
        alarm = _smooth(min(1.0, t / 0.2)) * (1 - _smooth(max(0.0, (t - 0.8) / 0.2)))
        toss = RETREAT_TOSS * math.sin(4 * math.pi * t) * alarm
        pose["Neck_01"] = [(X_AXIS, -RETREAT_NECK * alarm)]
        pose["Head"] = [(X_AXIS, -RETREAT_HEAD * alarm), (Z_AXIS, toss)]
        for leg_side, sign in (("Left", 1.0), ("Right", -1.0)):
            pose[leg_name("Front", leg_side, "Upper")] = pose[leg_name("Front", leg_side, "Upper")] + [(Y_AXIS, -sign * RETREAT_SPREAD * alarm)]
    elif style == "quadruped_idle":
        breath = math.sin(2 * math.pi * t * 2)
        pose["Chest"] = [(X_AXIS, 1.2 * breath)]
        pose["Neck_01"] = [(X_AXIS, 4.0 * math.sin(2 * math.pi * t)), (Z_AXIS, 5.0 * math.sin(2 * math.pi * t + 1.0))]
        pose["Head"] = [(X_AXIS, -3.0 * math.sin(2 * math.pi * t * 3)), (Z_AXIS, 4.0 * math.sin(2 * math.pi * t * 2))]
        if has_tail:
            pose["Tail_01"] = [(Z_AXIS, 12.0 * math.sin(2 * math.pi * t * 3))]
            pose["Tail_02"] = [(Z_AXIS, 10.0 * math.sin(2 * math.pi * t * 3 - 0.8))]
            pose["Tail_03"] = [(Z_AXIS, 8.0 * math.sin(2 * math.pi * t * 3 - 1.6))]
        shift = 2.0 * math.sin(2 * math.pi * t)
        for end, side in LEGS:
            pose[leg_name(end, side, "Upper")] = [(X_AXIS, shift if end == "Front" else -shift)]
    elif style == "quadruped_charge":
        heavy = stance["graviportal"]
        gallop = GAITS["quadruped_trot" if heavy else "quadruped_gallop"]
        # Two whole strides, so the clip ends in its first pose: the game loops an attack (TRIPO-LOOP-POP).
        cycle = (t * 2.0) % 1.0
        for end, side in LEGS:
            pose.update(_leg_rotations(gallop, cycle, end, side))
        lunge = math.sin(math.pi * t) * (HEAVY_LUNGE if heavy else 1.0)
        pose["Spine"] = [(X_AXIS, 6.0 * math.sin(2 * math.pi * cycle))]
        pose["Neck_01"] = [(X_AXIS, 18.0 * lunge)]
        pose["Neck_02"] = [(X_AXIS, 10.0 * lunge)]
        pose["Head"] = [(X_AXIS, 8.0 * lunge)]
    elif style == "quadruped_brace":
        free = _brace(pose, t, has_tail, (float(layout.landmarks["belly_z"]) + float(layout.landmarks["back_z"])) / 2)
    elif style == "quadruped_rear":
        _rear(pose, t, has_tail, stance["graviportal"], layout.landmarks.get("legs") or {})
        # A lifted foreleg carries no weight, so it folds as far as a runner's whatever its build.
        free = {leg_name("Front", side, segment) for side in ("Left", "Right") for segment in ("Lower", "Cannon", "Hoof")}
    elif style == "quadruped_collapse":
        death = layout.landmarks.get("death") or {}
        roll = float(death.get("roll", load.get("roll_limit", COLLAPSE_ROLL) if load else COLLAPSE_ROLL))
        _collapse(pose, t, has_tail, roll, float(death.get("neck_lift", 0.0)), bool(load))
    else:
        raise ValueError(f"Unknown quadruped action style: {style}")
    # A dying animal's legs give way whatever their build: the collapse bends them fully (a review saw pillar legs held straight read as
    # a rigid block tipping over).
    flex = 1.0 if style == "quadruped_collapse" else stance["flex"]
    # A heavy walk, defend and retreat show the head and neck under a load (they are what the map camera sees of them), so they keep the
    # whole share of the neck's bend, not LOADED_NECK of it (TRIPO-LOAD-SEAM judges the result).
    display = stance["graviportal"] and style in DISPLAY_STYLES
    neck = stance["neck"] * (LOADED_NECK if load and not display else 1.0)
    out = _held_back(_bent({name: rows for name, rows in pose.items() if name in names or name.startswith("__")}, flex, neck, load, free), load)
    return _ear_pose(out, style, frame, t, layout) if ears and layout.landmarks.get("ears") else out


def knee_rest_fold(joints: Dict[str, np.ndarray]) -> float:
    """How far a leg's knee is folded back at rest (degrees in the side view, negative when the cannon slants forward of the forearm, as
    a pillar leg's often does): the forearm's forward angle from straight down less the cannon's."""

    if not all(key in joints for key in ("upper", "middle", "lower")):
        return 0.0
    forearm = np.asarray(joints["middle"], dtype=float) - np.asarray(joints["upper"], dtype=float)
    cannon = np.asarray(joints["lower"], dtype=float) - np.asarray(joints["middle"], dtype=float)
    return math.degrees(math.atan2(-forearm[1], -forearm[2]) - math.atan2(-cannon[1], -cannon[2]))


def _rear(pose: Dict[str, List[Rotation]], t: float, has_tail: bool, heavy: bool, legs: Dict[str, Dict[str, np.ndarray]]) -> None:
    """The rear: the body pitches up about the hind feet and the forelegs lift. A heavy animal's is the whole rear at HEAVY_PITCH with the
    forelegs reaching HEAVY_REACH as far (a fresh review read the full foreleg lift under a small pitch as the elephant falling on its face).
    At the top each knee is bent HORSE_KNEE_FOLD from straight (HEAVY_REACH of it on a pillar leg), counted from the leg's own rest fold."""

    shape = _smooth(min(1.0, t / 0.35)) * (1 - _smooth(max(0.0, (t - 0.7) / 0.3)))
    rise = shape * (HEAVY_PITCH if heavy else 1.0)
    pose["__root_pitch__"] = [(X_AXIS, -32.0 * rise)]
    for side in ("Left", "Right"):
        kick = 1 + 0.25 * math.sin(6 * math.pi * t + (0 if side == "Left" else 1.5))
        reach = HEAVY_REACH if heavy else 1.0
        pose[leg_name("Front", side, "Upper")] = [(X_AXIS, -REAR_SHOULDER * reach * rise * kick)]
        pose[leg_name("Front", side, "Lower")] = [(X_AXIS, -(HORSE_FOREARM_REACH - REAR_SHOULDER) * reach * rise * kick)]
        fold = HORSE_KNEE_FOLD * reach - knee_rest_fold(legs.get(f"Front_{side}", {}))
        pose[leg_name("Front", side, "Cannon")] = [(X_AXIS, fold * shape)]
        pose[leg_name("Rear", side, "Upper")] = [(X_AXIS, 32.0 * rise - 12.0 * rise)]
        pose[leg_name("Rear", side, "Lower")] = [(X_AXIS, 15.0 * rise)]
        pose[leg_name("Rear", side, "Cannon")] = [(X_AXIS, -15.0 * rise)]
    pose["Neck_01"] = [(X_AXIS, -12.0 * rise)]
    # The head rises with the forequarters (a review read a head that dipped as the forefeet lifted as kneeling in mid-air).
    pose["Head"] = [(X_AXIS, REAR_HEAD * rise)]
    if has_tail:
        pose["Tail_01"] = [(X_AXIS, 20.0 * rise)]


def _pillar_gait(gait: Gait, stance: Dict[str, float]) -> Gait:
    """A pillar leg swings at the hip and shoulder no farther than a runner's walk (`PILLAR_SWING`) in any gait."""

    return replace(gait, swing_degrees=min(gait.swing_degrees, PILLAR_SWING)) if stance["graviportal"] else gait


def _gait(pose: Dict[str, List[Rotation]], gait: Gait, t: float, has_tail: bool) -> None:
    """One gait cycle at cycle time t: the legs (`_leg_rotations`), the back's sway, the head's nod and the tail's swing."""

    for end, side in LEGS:
        pose.update(_leg_rotations(gait, t, end, side))
    wave = math.sin(4 * math.pi * t)
    pose["Spine"] = [(X_AXIS, gait.spine_degrees * math.sin(2 * math.pi * t))]
    pose["Neck_01"] = [(X_AXIS, gait.head_degrees * wave)]
    pose["Head"] = [(X_AXIS, -0.5 * gait.head_degrees * wave)]
    if has_tail:
        pose["Tail_01"] = [(Z_AXIS, 8.0 * math.sin(2 * math.pi * t)), (X_AXIS, -10.0)]
        pose["Tail_02"] = [(Z_AXIS, 6.0 * math.sin(2 * math.pi * t - 0.6))]


def _brace_envelope(t: float) -> float:
    return _smooth(min(1.0, t / 0.25)) * (1 - _smooth(max(0.0, (t - 0.8) / 0.2)))


def _brace(pose: Dict[str, List[Rotation]], t: float, has_tail: bool, lean_length: float) -> set:
    """The defend of a graviportal animal, an elephant's threat display: the head rises briefly and then lowers with the tusks forward and
    stays low, the ears spread forward (`_ear_pose`), the forelegs spread apart and the forequarters step back over planted feet (the body
    shifts back `lean_length` times the sine of GUARD_LEAN and every leg leans forward that far, its hoof turned back to stay flat). The
    body keeps its heading and the forefeet stay on the ground (a pitch of more than about 8 degrees lifts them). Returns the joints that
    turn whatever the build (the hooves).

    A held turn read as a turn in place, not a guard (run 7), a small brace read as the idle from the map camera (0.01), and a toss of the
    head up and down could not be told from the idle at map size (run 11): the head held low, the spread ears and the forelegs are what
    show over a tall load (the neck cannot turn far, see WALK_HEAD_SWING)."""

    envelope = _brace_envelope(t)
    raised = _smooth(min(1.0, t / 0.15)) * (1 - _smooth(max(0.0, (t - 0.15) / 0.15)))
    lowered = _smooth(max(0.0, min(1.0, (t - 0.25) / 0.2))) * (1 - _smooth(max(0.0, (t - 0.85) / 0.15)))
    pose["__root_pitch__"] = [(X_AXIS, -GUARD_PITCH * envelope)]
    pose["__root_shift__"] = [(Y_AXIS, lean_length * math.sin(math.radians(GUARD_LEAN)) * envelope)]
    pose["Neck_01"] = [(X_AXIS, GUARD_NECK * (-0.5 * raised + 0.5 * lowered))]
    pose["Neck_02"] = [(X_AXIS, GUARD_NECK * (-raised + lowered))]
    pose["Head"] = [(X_AXIS, -GUARD_HEAD_UP * raised + GUARD_HEAD_DOWN * lowered)]
    for leg_side, sign in (("Left", 1.0), ("Right", -1.0)):
        pose[leg_name("Front", leg_side, "Upper")] = [(X_AXIS, -GUARD_LEAN * envelope), (Y_AXIS, -sign * GUARD_SPREAD * envelope)]
        pose[leg_name("Rear", leg_side, "Upper")] = [(X_AXIS, -GUARD_LEAN * envelope)]
    for end, side in LEGS:
        pose[leg_name(end, side, "Hoof")] = [(X_AXIS, GUARD_LEAN * envelope)]
    return {leg_name(end, side, "Hoof") for end, side in LEGS}


def _parent_chain(parent: str) -> Tuple[str, ...]:
    """The keys whose turns carry an ear hung from `parent`: EAR_HEAD_CHAIN down to it (the body's pitch alone for a torso bone)."""

    return EAR_HEAD_CHAIN[:EAR_HEAD_CHAIN.index(parent) + 1] if parent in EAR_HEAD_CHAIN else EAR_HEAD_CHAIN[:1]


def _head_turn(pose: Dict[str, List[Rotation]], chain: Sequence[str] = EAR_HEAD_CHAIN) -> Dict[Tuple[float, float, float], float]:
    """The turn about each armature axis summed down `chain` (degrees, small-angle)."""

    return {axis: sum(degrees for key in chain for row, degrees in pose.get(key, []) if tuple(row) == axis) for axis in (X_AXIS, Y_AXIS, Z_AXIS)}


def _ear_turn(style: str, t: float, ear: Dict[str, object], roll: float = 0.0) -> float:
    """An ear's own turn about its hinge (degrees, positive closes it back against the head). In a death both ears close as far as their
    room: the ear on top of the lying body falls onto the head and neck instead of standing up like a fin (two fresh reviews of run 11),
    and the ear underneath folds back off the ground. Run 13 left the lower ear where it stood, and a fresh review saw it hang below the
    lying torso to the ground (1.3% of the height below it). Its room of 10 degrees lifts it level with the torso, while a spread forward
    tore its root (54 edges by 1.3 times or more at 60 degrees, offline on run 13's mesh). A thin flap never holds the body up
    (`quadruped_rig.tune_collapse` leaves the ears out). In a defend each ear spreads forward GUARD_EAR_SPREAD (no farther than its room)."""

    close = float(ear.get("close_sign", 1.0))
    if style == "quadruped_collapse":
        return close * float(ear.get("close_room", 0.0)) * _collapse_fall(t)
    if style == "quadruped_brace":
        return -close * min(GUARD_EAR_SPREAD, float(ear.get("spread_room", 0.0))) * _brace_envelope(t)
    return 0.0


def _ear_pose(pose: Dict[str, List[Rotation]], style: str, frame: int, t: float, layout: Layout) -> Dict[str, List[Rotation]]:
    """Add the ear bones: an ear turns about its hinge (`_ear_turn`), EAR_ROOT_SHARE of it at the root and the rest at its middle, so it curls
    rather than swinging stiff, and its outer half follows the head with a little lag (EAR_LAG_FRAMES, EAR_LAG_SHARE)."""

    names = set(layout.names())
    total = frame_count(style)
    before = (frame - EAR_LAG_FRAMES) % total if style in LOOPING else max(0, frame - EAR_LAG_FRAMES)
    lagged = (pose, pose_at(style, before, layout, ears=False))
    roll = float((layout.landmarks.get("death") or {}).get("roll", 0.0))
    for side, ear in (layout.landmarks.get("ears") or {}).items():
        if ear_name(side, 1) not in names:
            continue
        chain = _parent_chain(str(ear.get("parent", "Head")))
        now, past = _head_turn(lagged[0], chain), _head_turn(lagged[1], chain)
        hinge = tuple(float(value) for value in np.asarray(ear["hinge"], dtype=float))
        turn = _ear_turn(style, t, ear, roll)
        pose[ear_name(side, 1)] = [(hinge, EAR_ROOT_SHARE * turn)]
        pose[ear_name(side, 2)] = [(axis, EAR_LAG_SHARE * (past[axis] - now[axis])) for axis in now] + [(hinge, (1 - EAR_ROOT_SHARE) * turn)]
    return pose


def roll_limits(landmarks: Dict[str, object]) -> Tuple[float, float]:
    """The largest roll toward each side (positive, then negative degrees about the body's long axis): COLLAPSE_ROLL, or less with a
    load (quadruped_load.roll_limit, `roll_limit` and `roll_limit_other_side` in the landmarks' `load`)."""

    load = landmarks.get("load") or {}
    if not load:
        return COLLAPSE_ROLL, -COLLAPSE_ROLL
    first = float(load.get("roll_limit", COLLAPSE_ROLL))
    other = float(load.get("roll_limit_other_side", -first))
    # The limit is where the tower first reaches lower than the torso on the rest pose. The dead body's folded legs and settled torso end it
    # higher: run 8's tower stuck out sideways with its outer end 5.9% of the height in the air (a review: major). The search starts
    # LOAD_ROLL_EXTRA degrees past the limit, and `choose_collapse` steps down to the largest roll that keeps no part lower than the torso
    # by more than DOWN_TOLERANCE, so the tower rests on the ground.
    return min(first + LOAD_ROLL_EXTRA, LOAD_ROLL_MOST), max(other - LOAD_ROLL_EXTRA, -LOAD_ROLL_MOST)


def choose_collapse(evaluate, start_rolls: Sequence[float]) -> Dict[str, object]:
    """The death's side, final roll and neck lift.

    On each side (`start_rolls`, the largest roll toward it, degrees with its sign) the largest roll down from it in COLLAPSE_ROLL_STEP
    steps whose final pose has no part lower than the torso by more than DOWN_TOLERANCE of the height, with the neck straight unless the
    head or neck is that part, then the smallest neck lift (NECK_LIFTS) that brings the torso down. The side whose pair rolls farther wins
    (the first side on a tie). Without such a pair, the straight-necked roll whose torso ends nearest the lowest point, unless a neck lift
    brings it nearer by more than DOWN_TOLERANCE. So the body falls onto the side where its torso reaches out farthest: a war elephant
    whose left ear spreads wider than its flank lies on its right side with its neck straight.

    `evaluate(roll, neck_lift)` poses the final frame and returns (the torso's height over the lowest point as a share of the height, the
    lowest part's bone)."""

    straight, lifted, found, tried = None, None, [], 0
    for start in start_rolls:
        sign = 1.0 if start >= 0 else -1.0
        for magnitude in np.arange(abs(float(start)), -0.1, -COLLAPSE_ROLL_STEP):
            roll = sign * float(magnitude)
            gap, part = evaluate(roll, 0.0)
            tried += 1
            if gap <= DOWN_TOLERANCE:
                found.append({"roll": roll, "neck_lift": 0.0, "torso_gap": round(gap, 4)})
                break
            if straight is None or gap < straight[0] - 1e-9:
                straight = (gap, roll, 0.0)
            if part not in NECK_PARTS:
                continue
            done = False
            for lift in NECK_LIFTS:
                gap, _part = evaluate(roll, lift)
                tried += 1
                if gap <= DOWN_TOLERANCE:
                    found.append({"roll": roll, "neck_lift": lift, "torso_gap": round(gap, 4)})
                    done = True
                    break
                if lifted is None or gap < lifted[0] - 1e-9:
                    lifted = (gap, roll, lift)
            if done:
                break
    if found:
        return {**max(found, key=lambda row: abs(row["roll"])), "tried": tried}
    best = lifted if lifted is not None and lifted[0] < straight[0] - DOWN_TOLERANCE else straight
    return {"roll": best[1], "neck_lift": best[2], "torso_gap": round(best[0], 4), "tried": tried, "note": "no pair put the torso lowest"}


def _held_back(pose: Dict[str, List[Rotation]], load: Dict[str, object]) -> Dict[str, List[Rotation]]:
    """A back strapped under a rigid load does not bend: the load rides the Spine, and Pelvis, Spine and Chest move as one."""

    return {name: rows for name, rows in pose.items() if not (load and name in LOADED_STILL)}


def _collapse_fall(t: float) -> float:
    return _smooth(max(0.0, min(1.0, (t - 0.2) / 0.45)))


def _collapse(pose: Dict[str, List[Rotation]], t: float, has_tail: bool, roll: float, neck_lift: float = 0.0, loaded: bool = False) -> None:
    """The death: the legs buckle and fold, the body rolls `roll` degrees onto its side (less with a load, quadruped_load.roll_limit),
    and once it lies the shoulders, hips and elbows relax `COLLAPSE_RELAX` of their bend while the knees and hocks stay bent.

    `neck_lift` turns the neck back against the roll as the body settles, so the head lies no lower than the torso
    (quadruped_rig.tune_collapse picks it and the roll on the final pose). Under a load (`loaded`) the head does not nod against it:
    the load rests on the head, and a war elephant's nod of 7 degrees as its legs buckled tore a band across its brow under
    the tower's front (TRIPO-LOAD-SEAM 0.44% of the seam's edges in 24 frames, 0.04% without the nod). Nor does its neck bend sideways.

    Two fresh reviews of the war elephant's lying pose saw the hind thigh, flank, shoulder and head stretched and the haunch bunched:
    the legs on top had turned 15 degrees down at the shoulder and hip, and every leg held its full fold on the ground. Played offline on
    the round 9 mesh, the edges changed by 1.3 times or more over the lying frames fell from 6,112 to 3,294 with no turn down, a relaxed
    shoulder, hip and elbow, and the hind legs folding half as far as the forelegs."""

    buckle = _smooth(min(1.0, t / 0.3))
    fall = _collapse_fall(t)
    settle = _smooth(max(0.0, (t - 0.65) / 0.35))
    ease = 1.0 - COLLAPSE_RELAX * settle
    for end, side in LEGS:
        fold = DEATH_FOLD * (1.0 if end == "Front" else COLLAPSE_HIND_FOLD)
        pose[leg_name(end, side, "Upper")] = [(X_AXIS, (-25.0 if end == "Front" else 20.0) * buckle * fold * ease)]
        pose[leg_name(end, side, "Lower")] = [(X_AXIS, 50.0 * buckle * fold * ease)]
        pose[leg_name(end, side, "Cannon")] = [(X_AXIS, (70.0 if end == "Front" else -50.0) * buckle * fold * (1 - 0.3 * settle))]
    pose["__root_roll__"] = [(Y_AXIS, roll * fall)]
    sign = -math.copysign(1.0, roll)  # the turn back toward the ground, against the roll
    lower = "Right" if roll < 0 else "Left"
    for end, side in LEGS:
        share = 1.0 if side == lower else DEATH_LEG_HANG_SHARE
        for segment, degrees in (DEATH_LEG_DROP if end == "Front" else DEATH_HIND_DROP).items():
            name = leg_name(end, side, segment)
            pose[name] = pose.get(name, []) + [(Y_AXIS, sign * degrees * share * min(1.0, abs(roll) / 90.0) * fall)]
    nod = 0.0 if loaded else 1.0
    pose["Neck_01"] = [(X_AXIS, (25.0 * buckle - 30.0 * settle) * nod), (Y_AXIS, -neck_lift * fall)]
    pose["Neck_02"] = [(Z_AXIS, 20.0 * settle * nod)]
    pose["Head"] = [(X_AXIS, -10.0 * settle * nod)]
    if has_tail:
        pose["Tail_01"] = [(X_AXIS, 25.0 * settle)]
