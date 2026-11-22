"""A map building's ground yard as a thin skirt close to its footprint.

Tripo often stands a building on a wide earth or paved yard with a raised rim. On the map that reads as a tile or a
mud pancake under the building, where vanilla's facilities stand on the terrain with at most a small yard. This step
keeps the yard's own ragged outline and everything on it, and only

- pulls the yard in toward the building: along rays from the building's centre, a yard point past the building's own
  outline in that direction (the structure: every piece that is not the yard or a small loose piece) moves to
  `outline + reach * tanh(distance / reach)`, so no point ends more than `reach` past the outline and the order of
  points along a ray is kept (the outline is not folded);
- lowers the yard's rim to the ground: past the outline, the yard's height falls off to zero at the reach, so its edge
  sinks into the terrain;
- moves the small loose pieces lying on the yard (barrels, a stack of bars, a heap) with it, rigidly: each keeps its
  shape, shifts by the move of its own centre and rests on the yard under it again.

It changes no faces and no UVs, only positions. Pieces are found on positions welded at a tolerance, so a vertex split
for its normals or UVs moves with its twins. `yard_skirt` returns the new positions and a report; a model with no yard
(no flat piece over a quarter of the plan area) is left as it is.
"""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

# The ground band: a yard is a piece that stays within this share of the model's height.
YARD_BAND = 0.12
# A yard covers at least this share of the model's plan (its bounding rectangle).
YARD_MIN_PLAN = 0.25
# How far a yard may reach past the building's outline, as a share of the building's own largest plan side (the yard
# left out, so the rule gives the same answer before and after it is applied).
REACH = 0.06
# The yard's height reaches the ground at this share of the reach.
RIM_FLAT = 0.75
# Loose pieces on the yard that move with it: at most this share of the height tall, this share of the plan side wide.
LOOSE_HEIGHT = 0.25
LOOSE_WIDTH = 0.12
# Angular bins for the building's outline seen from its centre.
BINS = 120


def _weld(points: np.ndarray, size: float) -> np.ndarray:
    keys = np.round(points / (size * 1e-5)).astype(np.int64)
    _, inverse = np.unique(keys, axis=0, return_inverse=True)
    return inverse.ravel()


def _pieces(welded: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """A piece label for every vertex (vertices in no triangle get their own)."""

    parent = np.arange(welded.max() + 1)

    def find(a: int) -> int:
        root = a
        while parent[root] != root:
            root = parent[root]
        while parent[a] != root:
            parent[a], a = root, parent[a]
        return root

    for a, b, c in welded[triangles]:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    roots = np.array([find(v) for v in range(len(parent))])
    return roots[welded]


def _outline(xy: np.ndarray, centre: np.ndarray) -> np.ndarray:
    """The structure's largest radius in each angular bin, with empty bins filled from their neighbours and each bin
    raised to its neighbours' maximum, so a thin gap between two posts does not pull the yard in behind them."""

    d = xy - centre
    angle = np.mod(np.arctan2(d[:, 1], d[:, 0]), 2 * np.pi)
    radius = np.linalg.norm(d, axis=1)
    bins = np.minimum((angle / (2 * np.pi) * BINS).astype(int), BINS - 1)
    outline = np.full(BINS, np.nan)
    for b in range(BINS):
        hit = radius[bins == b]
        if len(hit):
            outline[b] = hit.max()
    if np.isnan(outline).all():
        return np.zeros(BINS)
    known = np.flatnonzero(~np.isnan(outline))
    tiled = np.concatenate([known - BINS, known, known + BINS])
    values = np.tile(outline[known], 3)
    outline = np.interp(np.arange(BINS), tiled, values)
    return np.maximum.reduce([np.roll(outline, k) for k in (-1, 0, 1)])


def _outline_at(outline: np.ndarray, angle: np.ndarray) -> np.ndarray:
    position = np.mod(angle, 2 * np.pi) / (2 * np.pi) * BINS - 0.5
    index = np.floor(position).astype(int)
    t = position - index
    return outline[index % BINS] * (1 - t) + outline[(index + 1) % BINS] * t


def _classify(points: np.ndarray, triangles: np.ndarray, z: np.ndarray, height: float, plan: np.ndarray) -> Tuple[np.ndarray, np.ndarray, int, list]:
    """Each vertex's piece is the yard (flat and wide), a small loose piece lying low, or neither."""

    size = float(plan.max())
    piece = _pieces(_weld(points, max(size, height)), triangles)
    yard_labels, loose_labels = [], []
    for label in np.unique(piece):
        member = piece == label
        top = float(z[member].max())
        extent = np.ptp(points[member][:, :2], axis=0)
        if top <= YARD_BAND * height and extent[0] * extent[1] >= YARD_MIN_PLAN * plan[0] * plan[1]:
            yard_labels.append(label)
        elif top <= LOOSE_HEIGHT * height and float(extent.max()) <= LOOSE_WIDTH * size and float(z[member].min()) <= YARD_BAND * height:
            loose_labels.append(label)
    return np.isin(piece, yard_labels), piece, len(yard_labels), loose_labels


class _Pull:
    """The radial pull toward the building's outline, capped at `span` past it."""

    def __init__(self, structure: np.ndarray, span: float):
        self.centre = (structure.min(axis=0) + structure.max(axis=0)) / 2
        self.outline = _outline(structure, self.centre)
        self.span = span

    def __call__(self, xy: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        d = xy - self.centre
        radius = np.linalg.norm(d, axis=1)
        edge = _outline_at(self.outline, np.arctan2(d[:, 1], d[:, 0]))
        past = np.maximum(radius - edge, 0.0)
        pulled = np.where(radius > edge, edge + self.span * np.tanh(past / self.span), radius)
        scale = np.divide(pulled, radius, out=np.ones_like(radius), where=radius > 1e-12)
        return self.centre + d * scale[:, None], past, np.maximum(pulled - edge, 0.0)


def _move_loose(new: np.ndarray, points: np.ndarray, piece: np.ndarray, loose_labels: list, is_yard: np.ndarray, pull: _Pull) -> int:
    """Move each loose piece out past the outline in with the yard, rigidly, and rest it on the yard under it."""

    yard_points = new[is_yard]
    moved = 0
    for label in loose_labels:
        member = piece == label
        centre_before = points[member][:, :2].mean(axis=0)
        centre_after, gone, _ = pull(centre_before[None, :])
        if gone[0] <= 0:
            continue
        new[member, 0:2] += centre_after[0] - centre_before
        nearest = np.argmin(np.linalg.norm(yard_points[:, :2] - centre_after[0], axis=1))
        new[member, 2] += yard_points[nearest, 2] - points[member][:, 2].min()
        moved += 1
    return moved


def yard_skirt(points: np.ndarray, triangles: np.ndarray, reach: float = REACH) -> Tuple[np.ndarray, Dict]:
    """New positions with the yard pulled in and its rim lowered (z up, the ground at the model's lowest point)."""

    points = np.asarray(points, dtype=float)
    triangles = np.asarray(triangles, dtype=np.int64)
    low, high = points.min(axis=0), points.max(axis=0)
    height = float(high[2] - low[2])
    plan = high[:2] - low[:2]
    report: Dict = {"yard": False}
    if height <= 0 or float(plan.max()) <= 0 or not len(triangles):
        report["reason"] = "empty model"
        return points, report
    ground = float(low[2])
    z = points[:, 2] - ground
    is_yard, piece, yard_count, loose_labels = _classify(points, triangles, z, height, plan)
    if not yard_count:
        report["reason"] = f"no flat piece within {YARD_BAND:.0%} of the height covering {YARD_MIN_PLAN:.0%} of the plan"
        return points, report
    # Everything that is not the yard or a small loose piece holds the yard under it: the building, and low but large
    # pieces such as a long stack of bars or a tail race's walls, which a pull would otherwise leave hanging off the edge.
    standing = ~is_yard & ~np.isin(piece, loose_labels)
    if not (standing & (z > YARD_BAND * height)).any():
        report["reason"] = "no structure stands above the yard"
        return points, report
    structure = points[standing][:, :2]
    footprint = float(np.ptp(structure, axis=0).max())
    pull = _Pull(structure, reach * footprint)
    new = points.copy()
    yard_xy, past_before, past_after = pull(points[is_yard][:, :2])
    # the height falls to the ground at three quarters of the reach, so the skirt's outer quarter lies on the terrain
    fall = np.clip(1.0 - past_after / (RIM_FLAT * pull.span), 0.0, 1.0)
    new[is_yard, 0:2] = yard_xy
    new[is_yard, 2] = ground + z[is_yard] * np.where(past_after > 0, fall, 1.0)
    moved_loose = _move_loose(new, points, piece, loose_labels, is_yard, pull) if loose_labels else 0
    # the rim: the outer half of the skirt after the pull (the part that should meet the terrain)
    rim = past_after >= 0.5 * pull.span
    report.update({
        "yard": True,
        "yard_pieces": yard_count,
        "reach_share": reach,
        "reach_before": round(float(past_before.max()) / footprint, 4),
        "reach_after": round(float(past_after.max()) / footprint, 4),
        "rim_height_before": round(float(z[is_yard][rim].max()) / height, 4) if rim.any() else 0.0,
        "rim_height_after": round(float((new[is_yard, 2][rim] - ground).max()) / height, 4) if rim.any() else 0.0,
        "yard_vertices_moved": int(rim.sum()),
        "loose_pieces_moved": moved_loose,
    })
    return new, report


def yard_findings(points: np.ndarray, triangles: np.ndarray, reach: float = REACH) -> list:
    """STATIC-YARD: a building's yard reaches no further past its outline than the skirt rule leaves it (with a margin
    of a fifth for the reduction's moves)."""

    _new, report = yard_skirt(points, triangles, reach)
    if report.get("yard") and report["reach_before"] > reach * 1.2:
        return [("STATIC-YARD", "error", f"the yard reaches {report['reach_before']:.0%} of the building's size past it, over the {reach:.0%} a map building may have")]
    return []
