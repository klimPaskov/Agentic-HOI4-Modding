"""A shield held in a unit's free fist: where the fist closes on it, and a crescent shield for the tests.

Maths only (numpy). `tripo/shield_stage.py` runs it in headless Blender after the grip stage and hands the result to the grip stage's
own steps (`tripo/grip_weapon.py`: the grip search, the closed fingers, the arm hold, the clearance about the wrist and the drop).

The grip rule, from the model alone (no per-unit numbers):

- **Long axis.** The shield's longest principal axis. Its length is `HEIGHT_SHARE` of the body's height (0.65 for the approved dwarf),
  scaled evenly. The end with the larger cross-section is the head, the end the grip stage turns toward the index finger.
- **Outer edge.** The middle of a crescent bows out to one side of the line between its two ends. That side is the outer (convex)
  edge, the side the art puts the spikes on, and the shield's blade direction points to it. A shield whose middle does not bow
  (`BOW_SHARE`) keeps the direction of its second principal axis.
- **Grip.** The fist closes round the middle of the inner (concave) edge: on a bar along the long axis, just inside the hollow of the
  crescent, touching the edge. The bar's radius is `GRIP_RADIUS_SHARE` of the height, the haft of a held weapon (the ogre's club
  measured 1.3%, the orc's axe 1.9%). The shield then reaches out of the fist across its width, its outer edge away from the body.
- **Roll.** The grip stage turns the blade direction `ROLL_DEGREES` about the bar from the palm's normal: 180 puts the shield on the
  back of the hand, so the palm and the closed fingers stay outside it, and a hanging arm with its palm toward the thigh holds the
  outer edge away from the body, as the art does.

The clearance (`lib/tripo_clearance.clear_clip`, run by the grip stage) turns the hand about the wrist until the shield leaves the body,
as for a weapon. Points within the weapon's grip zone of the bar (12% of the height) are not judged: the fist closes on the shield there.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

SHIELD_BONE = "Shield"
SHIELD_PART = "tripo_part_2"
HEIGHT_SHARE = 0.65
GRIP_RADIUS_SHARE = 0.015
ROLL_DEGREES = 180.0
MIDDLE_SHARE = 0.05  # the middle cross-section: within this share of the length of the middle
END_SHARE = 0.15  # each end: this share of the length
BOW_SHARE = 0.02  # a middle bowed less than this share of the length is straight
EDGE_PERCENTILE = 1.0


def unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, float)
    return vector / max(float(np.linalg.norm(vector)), 1e-12)


def shield_grip(points: np.ndarray, share: float = HEIGHT_SHARE, radius_share: float = GRIP_RADIUS_SHARE) -> Dict[str, object]:
    """The grip on a shield model, in its own file space (see the module text).

    Returns "grip" (the bar's centre), "axes" (columns: the long axis toward the head, the blade direction toward the outer edge, the
    third), "length", "radius" (the bar's radius in file units, for a shield `share` of the height), "bow_share" (how far the middle
    bows toward the outer edge, a share of the length) and "inner_edge" (the point of the inner edge the fist closes on)."""

    points = np.asarray(points, float)
    mean = points.mean(axis=0)
    centred = points - mean
    values, vectors = np.linalg.eigh(centred.T @ centred)
    order = np.argsort(values)[::-1]
    e1, e2 = vectors[:, order[0]], vectors[:, order[1]]
    t = centred @ e1
    low, high = float(t.min()), float(t.max())
    length = high - low

    def spread(mask):
        part = centred[mask]
        radial = part - np.outer(part @ e1, e1)
        return float(np.sqrt((radial * radial).sum(axis=1).mean())) if len(part) else 0.0

    if spread(t < low + END_SHARE * length) > spread(t > high - END_SHARE * length):
        e1, t, low, high = -e1, -t, -high, -low
    mid = 0.5 * (low + high)
    middle = np.abs(t - mid) <= MIDDLE_SHARE * length
    ends = (t < low + END_SHARE * length) | (t > high - END_SHARE * length)
    radial = centred - np.outer(t, e1)
    bow = radial[middle].mean(axis=0) - radial[ends].mean(axis=0)
    bow_share = float(np.linalg.norm(bow)) / max(length, 1e-12)
    blade = unit(bow) if bow_share >= BOW_SHARE else unit(e2 - (e2 @ e1) * e1)
    third = np.cross(e1, blade)
    along_blade = radial[middle] @ blade
    inner = float(np.percentile(along_blade, EDGE_PERCENTILE))
    near_edge = radial[middle][along_blade <= inner + 0.02 * length]
    edge_third = float(np.median(near_edge @ third)) if len(near_edge) else 0.0
    inner_edge = mean + mid * e1 + inner * blade + edge_third * third
    radius = radius_share / share * length
    return {
        "grip": inner_edge - radius * blade, "inner_edge": inner_edge, "axes": np.stack([e1, blade, third], axis=1), "length": float(length),
        "radius": float(radius), "bow_share": bow_share, "bowed": bool(bow_share >= BOW_SHARE),
    }


def crescent(length: float = 1.0, bow_share: float = 0.25, width_share: float = 0.18, thickness_share: float = 0.08, spikes: int = 12,
             rows: int = 40, ring: int = 8) -> Dict[str, np.ndarray]:
    """A stand-in for the dwarf's shield: a closed crescent, pointed at both ends, with spikes on its outer edge.

    Its ends lie on the y axis at 0 and `length`, its middle bows toward -x by `bow_share` of the length, it is `width_share` wide
    across the middle and `thickness_share` thick (z). Returns "vertices" and "triangles"."""

    half = length / 2.0
    sagitta = bow_share * length
    radius = (half * half + sagitta * sagitta) / (2.0 * sagitta)
    centre_x = -sagitta + radius
    sweep = np.arcsin(half / radius)
    vertices, triangles = [], []
    angles = np.linspace(-sweep, sweep, rows)
    for angle in angles:
        taper = np.cos(0.5 * np.pi * (angle / sweep))
        width = max(width_share * length * taper, 1e-3 * length)
        thick = max(thickness_share * length * taper, 1e-3 * length)
        outer = np.array([centre_x - radius * np.cos(angle), half + radius * np.sin(angle)])
        inward = np.array([np.cos(angle), -np.sin(angle)])
        for j in range(ring):
            phi = 2.0 * np.pi * j / ring
            across, depth = 0.5 * (1.0 - np.cos(phi)), 0.5 * np.sin(phi)
            xy = outer + inward * width * across
            vertices.append([xy[0], xy[1], depth * thick])
    for k in range(rows - 1):
        for j in range(ring):
            a, b = k * ring + j, k * ring + (j + 1) % ring
            c, d = a + ring, b + ring
            triangles += [[a, c, d], [a, d, b]]
    tips = []
    for end in (0, rows - 1):
        tips.append(len(vertices))
        vertices.append(list(np.mean(vertices[end * ring : end * ring + ring], axis=0)))
    for j in range(ring):
        triangles.append([tips[0], (j + 1) % ring, j])
        last = (rows - 1) * ring
        triangles.append([tips[1], last + j, last + (j + 1) % ring])
    for s in range(spikes):
        k = int(round((s + 0.5) / spikes * (rows - 1)))
        base = np.array(vertices[k * ring])
        out = unit(np.array([base[0] - centre_x, base[1] - half, 0.0]))
        tip = len(vertices)
        vertices.append(list(base + out * 0.04 * length))
        triangles += [[tip, k * ring, k * ring + 1], [tip, k * ring + ring - 1, k * ring]]
    return {"vertices": np.array(vertices, float), "triangles": np.array(triangles, dtype=np.int64)}
