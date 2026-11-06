"""Measure a four-legged model and lay out its rig, weights and gait poses.

Pure numpy, no Blender: `quadruped_rig.py` applies the results inside Blender,
and the unit tests run this module on synthetic point clouds. Coordinates are
the HOI4 working frame the candidate preparation produces: +Z up, ground at the
lowest point, the animal facing -Y, its left side toward +X.

The rig has 27 bones (the engine skins at most 50): a non-deforming Root on the
ground, Pelvis, Spine, Chest, two neck bones, Head, three tail bones when the
model has a tail, four bones per leg (upper, lower, cannon, hoof) and the
non-deforming Saddle_Node a rider entity attaches to, as vanilla
`cavalry_horse.mesh` does.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

LEGS = (("Front", "Left"), ("Front", "Right"), ("Rear", "Left"), ("Rear", "Right"))
LEG_SEGMENTS = ("Upper", "Lower", "Cannon", "Hoof")
SADDLE_NODE = "Saddle_Node"
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

    ground = float(points[:, 2].min())
    height = float(points[:, 2].max()) - ground
    hooves = points[points[:, 2] < ground + 0.07 * height]
    if len(hooves) < 8:
        raise LandmarkError("fewer than 8 vertices near the ground; the legs may not reach it")
    low, high = float(hooves[:, 1].min()), float(hooves[:, 1].max())
    length = float(np.ptp(points[:, 1]))
    minus_end = points[points[:, 1] < low - 0.02 * length]
    plus_end = points[points[:, 1] > high + 0.02 * length]
    top_minus = float(minus_end[:, 2].max()) if len(minus_end) else ground
    top_plus = float(plus_end[:, 2].max()) if len(plus_end) else ground
    return top_plus > top_minus


def detect_landmarks(points: np.ndarray) -> Dict[str, object]:
    """Find the hooves, belly, back, head, tail and saddle of a standing quadruped."""

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

    hooves = p[p[:, 2] < 0.07 * height]
    if len(hooves) < 8:
        raise LandmarkError("fewer than 8 vertices near the ground; the legs may not reach it")
    split_y = _largest_gap_split(hooves[:, 1])
    hoof_centres: Dict[str, np.ndarray] = {}
    for end, side in LEGS:
        mask = (hooves[:, 1] < split_y) if end == "Front" else (hooves[:, 1] >= split_y)
        mask &= (hooves[:, 0] >= cx) if side == "Left" else (hooves[:, 0] < cx)
        if not mask.any():
            raise LandmarkError(f"no ground contact for the {end.lower()} {side.lower()} leg")
        hoof_centres[f"{end}_{side}"] = hooves[mask].mean(axis=0)
    front_y = float((hoof_centres["Front_Left"][1] + hoof_centres["Front_Right"][1]) / 2)
    rear_y = float((hoof_centres["Rear_Left"][1] + hoof_centres["Rear_Right"][1]) / 2)
    if front_y >= rear_y:
        raise LandmarkError("the front legs are not in front (toward -Y) of the rear legs")
    span = rear_y - front_y
    column = p[(np.abs(p[:, 0] - cx) < 0.12 * width) & (p[:, 1] > front_y + 0.15 * span) & (p[:, 1] < rear_y - 0.15 * span)]
    if len(column) < 10:
        raise LandmarkError("no body between the front and rear legs")
    belly_z = float(np.percentile(column[:, 2], 2))
    back_z = float(np.percentile(column[:, 2], 98))
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

    tail_region = p[(p[:, 1] > rear_y + 0.06 * length) & (p[:, 2] > 0.2 * height)]
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
    }


def _t(vector: np.ndarray, ground: float) -> Tuple[float, float, float]:
    return (float(vector[0]), float(vector[1]), float(vector[2] + ground))


def build_layout(landmarks: Dict[str, object]) -> Layout:
    """Place the 27 bones from the landmarks, back in the model's own coordinates."""

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
    add(Bone(SADDLE_NODE, _t(saddle, g), _t(saddle + v([0.0, 0.1 * h, 0.0]), g), "Spine", deform=False))
    return layout


def _segment_distance(points: np.ndarray, head: np.ndarray, tail: np.ndarray) -> np.ndarray:
    direction = tail - head
    length2 = float(direction @ direction) or 1e-12
    t = np.clip(((points - head) @ direction) / length2, 0.0, 1.0)
    closest = head + t[:, None] * direction
    return np.linalg.norm(points - closest, axis=1)


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
    for index, bone in enumerate(bones):
        if not bone.deform:
            continue
        name = bone.name
        if name.startswith(("Front_", "Rear_")):
            key = "_".join(name.split("_")[:2])
            mask = in_leg & (nearest_leg == leg_keys.index(key))
            if not name.endswith("_Upper"):
                mask &= q[:, 2] < belly_z
            allowed[:, index] = mask
        elif name.startswith("Tail_"):
            tail_root_y = float(np.asarray(lm["tail"][0])[1]) if lm.get("tail") else rear_y
            allowed[:, index] = (q[:, 1] > tail_root_y - 0.02 * length) & in_body
        elif name in {"Neck_01", "Neck_02", "Head"}:
            allowed[:, index] = q[:, 1] < front_y + 0.06 * length
        elif name == "Pelvis":
            allowed[:, index] = in_body & (q[:, 1] > mid_y - 0.12 * length)
        elif name == "Chest":
            allowed[:, index] = in_body & (q[:, 1] < mid_y + 0.12 * length)
        elif name == "Spine":
            allowed[:, index] = in_body
    orphans = ~allowed.any(axis=1)
    if orphans.any():
        for index, bone in enumerate(bones):
            if bone.deform and bone.name in {"Pelvis", "Spine", "Chest"}:
                allowed[orphans, index] = True
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
ROLE_FRAMES = {"quadruped_idle": 72, "quadruped_charge": 36, "quadruped_rear": 48, "quadruped_collapse": 48}
DEFAULT_STYLE = {
    "idle": "quadruped_idle",
    "move": "quadruped_trot",
    "attack": "quadruped_charge",
    "defend": "quadruped_rear",
    "retreat": "quadruped_gallop",
    "death": "quadruped_collapse",
}
LOOPING = {"quadruped_idle", "quadruped_walk", "quadruped_trot", "quadruped_gallop"}

Rotation = Tuple[Tuple[float, float, float], float]


def frame_count(style: str) -> int:
    return GAITS[style].cycle_frames if style in GAITS else ROLE_FRAMES[style]


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


def pose_at(style: str, frame: int, layout: Layout) -> Dict[str, List[Rotation]]:
    """Each bone's armature-space rotations (axis, degrees) at `frame`; the key `__root_offset__` moves the Root.

    Looping styles return the same pose at frame 0 and at `frame_count(style)`.
    """

    names = set(layout.names())
    total = frame_count(style)
    t = (frame % total) / total if style in LOOPING else min(1.0, frame / max(total - 1, 1))
    pose: Dict[str, List[Rotation]] = {}
    has_tail = "Tail_01" in names
    if style in GAITS:
        gait = GAITS[style]
        for end, side in LEGS:
            pose.update(_leg_rotations(gait, t, end, side))
        wave = math.sin(4 * math.pi * t)
        pose["Spine"] = [(X_AXIS, gait.spine_degrees * math.sin(2 * math.pi * t))]
        pose["Neck_01"] = [(X_AXIS, gait.head_degrees * wave)]
        pose["Head"] = [(X_AXIS, -0.5 * gait.head_degrees * wave)]
        if has_tail:
            pose["Tail_01"] = [(Z_AXIS, 8.0 * math.sin(2 * math.pi * t)), (X_AXIS, -10.0)]
            pose["Tail_02"] = [(Z_AXIS, 6.0 * math.sin(2 * math.pi * t - 0.6))]
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
        gallop = GAITS["quadruped_gallop"]
        cycle = (t * 2.5) % 1.0
        for end, side in LEGS:
            pose.update(_leg_rotations(gallop, cycle, end, side))
        lunge = math.sin(math.pi * t)
        pose["Spine"] = [(X_AXIS, 6.0 * math.sin(2 * math.pi * cycle))]
        pose["Neck_01"] = [(X_AXIS, 18.0 * lunge)]
        pose["Neck_02"] = [(X_AXIS, 10.0 * lunge)]
        pose["Head"] = [(X_AXIS, 8.0 * lunge)]
    elif style == "quadruped_rear":
        rise = _smooth(min(1.0, t / 0.35)) * (1 - _smooth(max(0.0, (t - 0.7) / 0.3)))
        pose["__root_pitch__"] = [(X_AXIS, -32.0 * rise)]
        for side in ("Left", "Right"):
            kick = 1 + 0.25 * math.sin(6 * math.pi * t + (0 if side == "Left" else 1.5))
            pose[leg_name("Front", side, "Upper")] = [(X_AXIS, -55.0 * rise * kick)]
            pose[leg_name("Front", side, "Lower")] = [(X_AXIS, 40.0 * rise)]
            pose[leg_name("Front", side, "Cannon")] = [(X_AXIS, 85.0 * rise)]
            pose[leg_name("Rear", side, "Upper")] = [(X_AXIS, 32.0 * rise - 12.0 * rise)]
            pose[leg_name("Rear", side, "Lower")] = [(X_AXIS, 15.0 * rise)]
            pose[leg_name("Rear", side, "Cannon")] = [(X_AXIS, -15.0 * rise)]
        pose["Neck_01"] = [(X_AXIS, -12.0 * rise)]
        pose["Head"] = [(X_AXIS, 10.0 * rise)]
        if has_tail:
            pose["Tail_01"] = [(X_AXIS, 20.0 * rise)]
    elif style == "quadruped_collapse":
        buckle = _smooth(min(1.0, t / 0.3))
        fall = _smooth(max(0.0, min(1.0, (t - 0.2) / 0.45)))
        settle = _smooth(max(0.0, (t - 0.65) / 0.35))
        for end, side in LEGS:
            fold = 1.0 if end == "Front" else 0.7
            pose[leg_name(end, side, "Upper")] = [(X_AXIS, (-25.0 if end == "Front" else 20.0) * buckle * fold)]
            pose[leg_name(end, side, "Lower")] = [(X_AXIS, 50.0 * buckle * fold)]
            pose[leg_name(end, side, "Cannon")] = [(X_AXIS, (70.0 if end == "Front" else -50.0) * buckle * fold * (1 - 0.6 * settle))]
        pose["__root_roll__"] = [(Y_AXIS, 82.0 * fall)]
        pose["Neck_01"] = [(X_AXIS, 25.0 * buckle - 30.0 * settle)]
        pose["Neck_02"] = [(Z_AXIS, 20.0 * settle)]
        pose["Head"] = [(X_AXIS, -10.0 * settle)]
        if has_tail:
            pose["Tail_01"] = [(X_AXIS, 25.0 * settle)]
    else:
        raise ValueError(f"Unknown quadruped action style: {style}")
    return {name: rows for name, rows in pose.items() if name in names or name.startswith("__")}
