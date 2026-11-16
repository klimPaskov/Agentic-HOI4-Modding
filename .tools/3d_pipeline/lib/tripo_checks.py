"""Checks that fail what a viewer fails on a Tripo unit: maths only (numpy), no file or Blender access.

`tripo/tripo_checks.py` loads a unit and calls these. Each function answers one question a reviewer asked of the
orc and returns numbers; the thresholds are named constants here, with the reason for each value.

- `enclosure_share`: how much of the haft's circumference, at the grip point and a little either side of it, has
  hand skin close to it. An open hand laid along a haft covers a third of it or less; a hand that wraps it covers
  nearly all.
- `blade_facing_degrees`: the angle between the broad face of the weapon's head and the direction the unit faces.
- `cloak_region` and `region_stretch_share`: the vertices that hang behind the body, and the share of their edges that
  a clip stretches or squashes.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

# Grip readability. Hand meshes are a few hundred vertices, so skin counts as covering a point of the haft when a vertex lies within
# 1.2% of the body height of it. Calibrated 2026-11: the orc's hand covers 0.32 of the haft's circumference at the grip; a hand lying
# open against a haft covers 0.3 or less and a synthetic wrap (280 degrees round the haft over 6 cm) 0.8 to 0.9. 0.50 sits between.
ENCLOSURE_TOLERANCE_SHARE = 0.012
MIN_ENCLOSURE_SHARE = 0.50
# The thumb closes from the other side of the haft than the fingertips: at least this many degrees apart around it.
MIN_THUMB_OPPOSITION_DEGREES = 90.0
# The broad face of a blade must face the camera within this angle in the idle pose (the front view shows the shape the
# artist drew; edge-on it reads as a stick).
MAX_BLADE_FACING_DEGREES = 50.0
# A head with no broad face has no facing to judge: the thinnest axis of a near-round head is whichever way noise points (the round 4 ogre's club
# turned about its haft by -74, 0 and +74 degrees read 85, 74 and 87 degrees off the front). The head's thinnest spread over its middle spread
# (`blade_head`) measured 0.72 on that club and 0.41 on the orc's axe blade (a real flat head), 0.18 to 0.5 on the blade of a synthetic axe.
# Above 0.55 (about their geometric mean) the head is round enough that the facing is not judged and the check reports the ratio only.
MAX_FACE_FLATNESS = 0.55


def unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, float)
    length = float(np.linalg.norm(vector))
    return vector / length if length > 1e-12 else vector


def principal_axes(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The centre of `points` and their principal axes, longest first (rows)."""

    points = np.asarray(points, float)
    centre = points.mean(axis=0)
    values, vectors = np.linalg.eigh(np.cov((points - centre).T))
    order = np.argsort(values)[::-1]
    return centre, vectors[:, order].T, values[order]


def enclosure_share(
    haft_point: np.ndarray,
    haft_direction: np.ndarray,
    radius: float,
    skin_points: np.ndarray,
    tolerance: float,
    half_length: float,
    angles: int = 36,
    rings: int = 5,
) -> float:
    """Share of sample points on the haft's surface (rings along it, angles round it) that have skin within `tolerance`."""

    d = unit(haft_direction)
    helper = np.array([1.0, 0.0, 0.0]) if abs(d[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = unit(np.cross(d, helper))
    v = np.cross(d, u)
    skin_points = np.asarray(skin_points, float)
    covered, total = 0, 0
    for z in np.linspace(-half_length, half_length, rings):
        for a in np.linspace(0.0, 2.0 * np.pi, angles, endpoint=False):
            point = haft_point + z * d + radius * (np.cos(a) * u + np.sin(a) * v)
            nearest = float(np.linalg.norm(skin_points - point, axis=1).min()) if len(skin_points) else 1e9
            covered += nearest <= tolerance
            total += 1
    return covered / max(total, 1)


def blade_head(weapon_points: np.ndarray, hand_point: np.ndarray, head_share: float = 0.25) -> Tuple[np.ndarray, np.ndarray, float]:
    """(the head's points, the head's face normal, its flatness) of a held weapon.

    The haft is the longest principal axis of the weapon's points. Each end of it is the `head_share` of the points farthest along it, and the head is the
    end with the larger cross-section (the product of its two smaller spreads): a hand may hold the weapon nearer its head than its butt, so
    "the end farthest from the hand" read the orc's axe by its butt (2026-11-16: 0.89 against the blade's 0.41). The face normal is the head's thinnest
    principal axis. The flatness is the head's thinnest spread over its middle spread (standard deviations): 0 is a plate, 1 is round.
    `hand_point` is kept for the callers' signature."""

    points = np.asarray(weapon_points, float)
    _centre, axes, _values = principal_axes(points)
    along = points @ axes[0]
    order = np.argsort(along)
    size = max(int(head_share * len(points)), 10)
    best = None
    for head in (points[order[:size]], points[order[-size:]]):
        _c, head_axes, head_values = principal_axes(head)
        spread = np.sqrt(np.clip(head_values, 0.0, None))
        area = float(spread[1] * spread[2])
        if best is None or area > best[0]:
            best = (area, head, head_axes[2], float(spread[2] / max(spread[1], 1e-12)))
    return best[1], best[2], best[3]


def blade_facing_degrees(weapon_points: np.ndarray, hand_point: np.ndarray, front: np.ndarray, head_share: float = 0.25) -> Tuple[float, np.ndarray]:
    """Angle (0 to 90 degrees) between the broad face of a weapon's head and `front`, and the face's normal (head: `blade_head`).

    0 means the face looks straight at a camera in front of the unit, 90 means edge-on."""

    _head, normal, _flatness = blade_head(weapon_points, hand_point, head_share)
    cosine = abs(float(unit(normal) @ unit(front)))
    return float(np.degrees(np.arccos(np.clip(cosine, 0.0, 1.0)))), normal


def cloak_region(
    positions: np.ndarray,
    dominant: Sequence[str],
    hips: np.ndarray,
    front: np.ndarray,
    height: float,
    bones: Sequence[str],
    behind_share: float = 0.06,
    low_share: float = 0.25,
    high_share: float = 0.85,
    ground: Optional[float] = None,
    up_axis: int = 1,
) -> np.ndarray:
    """Mask of the vertices that hang behind the body: weighted mostly to a torso, hip or thigh bone, behind the hips by
    more than `behind_share` of the height along `front`, between `low_share` and `high_share` of the height."""

    positions = np.asarray(positions, float)
    floor = float(positions[:, up_axis].min()) if ground is None else ground
    level = (positions[:, up_axis] - floor) / max(height, 1e-9)
    behind = (positions - hips) @ unit(front) < -behind_share * height
    return behind & np.isin(np.asarray(dominant), list(bones)) & (level > low_share) & (level < high_share)


def region_stretch_share(
    rest: np.ndarray,
    posed_frames: Sequence[np.ndarray],
    edges: np.ndarray,
    mask: np.ndarray,
    height: float,
    long_ratio: float = 1.5,
    short_ratio: float = 0.5,
    significant: float = 0.005,
) -> Tuple[float, int]:
    """Worst frame's share of the masked edges (both ends in `mask`) that are stretched past `long_ratio` or squashed under
    `short_ratio` of their rest length by more than `significant` of the height, and that frame's index."""

    inside = mask[edges[:, 0]] & mask[edges[:, 1]]
    selected = edges[inside]
    if not len(selected):
        return 0.0, 0
    rest_length = np.linalg.norm(rest[selected[:, 0]] - rest[selected[:, 1]], axis=1)
    usable = rest_length > 1e-9
    worst, worst_frame = 0.0, 0
    for index, posed in enumerate(posed_frames):
        length = np.linalg.norm(posed[selected[:, 0]] - posed[selected[:, 1]], axis=1)
        ratio = np.where(usable, length / np.where(usable, rest_length, 1.0), 1.0)
        change = np.abs(length - rest_length) / max(height, 1e-9)
        bad = ((ratio > long_ratio) | (ratio < short_ratio)) & (change > significant)
        share = float(bad.mean())
        if share > worst:
            worst, worst_frame = share, index
    return worst, worst_frame
