"""Find the load a quadruped carries (a tower, a howdah, a pack frame) and place its Saddle_Node by measured rules.

Pure numpy, no Blender: `quadruped_rig.py` applies the results inside Blender and the unit tests run this
module on synthetic meshes. Coordinates are the working frame of `quadruped_layout.py`: +Z up, the ground
at the lowest point, the animal facing -Y.

A generator such as Tripo makes the animal and what it carries as one skin. The rules here split them
without a setting:

- **Deck.** The load stands on a floor: the height band (1% of the height) with the most upward-facing
  flat surface, above the lower third of the model. Where several bands come within half of the largest,
  the lowest is the deck, so a tower's upper storey never counts as its base.
- **Cut.** The deck's own underside: the lowest band within a tenth of the height under the deck whose
  downward-facing flat surface is at least a quarter of the deck's. Without one, 3% of the height under it.
- **Load.** Every vertex above the cut that is joined, through edges between vertices above the cut, to
  the deck's footprint (the middle 96% of the deck's flat surface in plan, widened by 2% of the height).
  So stakes and a totem that rise from the deck belong to it, and an ear or a head crown that only
  reaches above the cut in front of the deck does not.
- **Saddle.** The rider entity stands on the deck at the deck point whose column (the rider's height and
  a fifth of it as radius) holds the fewest load vertices. Ties go to the point nearest the deck's centre.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

FLAT = 0.9  # |normal z| above this is a flat face
BAND = 0.01  # height band, share of the model height
LOWEST_DECK = 0.33  # a deck is above this share of the height
DECK_PEER = 0.5  # bands within this share of the largest are deck candidates; the lowest wins
UNDERSIDE_REACH = 0.10
UNDERSIDE_SHARE = 0.25
UNDERSIDE_DEFAULT = 0.03
FOOTPRINT_PERCENTILE = 2.0
FOOTPRINT_MARGIN = 0.02
RIDER_RADIUS_SHARE = 0.12
RIDER_FOOT_CLEARANCE = 0.02  # of the model height above the deck before the column starts counting


class LoadError(ValueError):
    """The model has no deck a load could stand on."""


@dataclass
class Load:
    mask: np.ndarray  # (N,) True for the load's vertices
    deck_z: float
    cut_z: float
    footprint: Tuple[float, float, float, float]  # x_min, x_max, y_min, y_max
    deck_area: float
    levels: List[Dict[str, float]] = field(default_factory=list)
    # every floor of the load a rider may stand on: (height, footprint), the deck first
    floors: List[Tuple[float, Tuple[float, float, float, float]]] = field(default_factory=list)

    def summary(self, height: float) -> Dict[str, object]:
        return {
            "vertices": int(self.mask.sum()),
            "deck_height_share": round(self.deck_z / height, 4),
            "cut_height_share": round(self.cut_z / height, 4),
            "footprint": [round(float(value), 4) for value in self.footprint],
            "deck_area": round(self.deck_area, 6),
            "flat_levels": self.levels,
        }


def faces(points: np.ndarray, triangles: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Centroids, unit normals and areas of the triangles."""

    a, b, c = points[triangles[:, 0]], points[triangles[:, 1]], points[triangles[:, 2]]
    cross = np.cross(b - a, c - a)
    double = np.linalg.norm(cross, axis=1)
    normals = cross / np.maximum(double, 1e-12)[:, None]
    return (a + b + c) / 3.0, normals, double / 2.0


def _bands(z: np.ndarray, area: np.ndarray, height: float, low: float, high: float) -> Tuple[np.ndarray, np.ndarray]:
    edges = np.arange(low, high + BAND * height, BAND * height)
    totals, edges = np.histogram(z, bins=edges, weights=area)
    return totals, edges


def components(count: int, edges: np.ndarray, allowed: np.ndarray) -> np.ndarray:
    """Connected-component labels of the allowed vertices over edges whose two ends are allowed (-1 elsewhere)."""

    labels = np.where(allowed, np.arange(count), -1)
    usable = edges[allowed[edges[:, 0]] & allowed[edges[:, 1]]]
    while len(usable):
        low = np.minimum(labels[usable[:, 0]], labels[usable[:, 1]])
        before = labels.copy()
        np.minimum.at(labels, usable[:, 0], low)
        np.minimum.at(labels, usable[:, 1], low)
        labels[allowed] = labels[labels[allowed]]  # pointer jumping
        if np.array_equal(before, labels):
            break
    return labels


def weld_edges(points: np.ndarray, triangles: np.ndarray, tolerance: float) -> np.ndarray:
    """Triangle edges between welded vertices (split UV seams joined), as indices into `points`."""

    keys = np.round(points / max(tolerance, 1e-12)).astype(np.int64)
    _unique, first = np.unique(keys, axis=0, return_index=True)
    _unique, canon = np.unique(keys, axis=0, return_inverse=True)
    canon = first[canon.ravel()]
    welded = canon[triangles]
    edges = np.concatenate([welded[:, [0, 1]], welded[:, [1, 2]], welded[:, [2, 0]]])
    # the vertices a seam split are joined to their first copy
    seam = np.flatnonzero(canon != np.arange(len(points)))
    return np.concatenate([edges, np.stack([seam, canon[seam]], axis=1)])


def find_load(points: np.ndarray, triangles: np.ndarray) -> Load:
    """The load's vertices, its deck and its cut, by the rules in the module docstring."""

    ground = float(points[:, 2].min())
    p = points - np.array([0.0, 0.0, ground])
    height = float(p[:, 2].max())
    if height <= 0:
        raise LoadError("the model is flat")
    centres, normals, area = faces(p, triangles)
    up = normals[:, 2] > FLAT
    down = normals[:, 2] < -FLAT
    totals, edges = _bands(centres[up, 2], area[up], height, LOWEST_DECK * height, (1 + BAND) * height)
    if not len(totals) or totals.max() <= 0:
        raise LoadError("no upward-facing flat surface above the lower third")
    peers = np.flatnonzero(totals >= DECK_PEER * totals.max())
    deck_band = int(peers.min())
    deck_low, deck_high = float(edges[deck_band]), float(edges[deck_band + 1])
    on_deck = up & (centres[:, 2] >= deck_low) & (centres[:, 2] < deck_high)
    deck_area = float(area[on_deck].sum())
    deck_z = float(np.average(centres[on_deck, 2], weights=area[on_deck]))
    below, below_edges = _bands(centres[down, 2], area[down], height, max(deck_low - UNDERSIDE_REACH * height, 0.0), deck_high)
    strong = np.flatnonzero(below >= UNDERSIDE_SHARE * deck_area)
    cut_z = float(below_edges[int(strong.min())]) if len(strong) else deck_z - UNDERSIDE_DEFAULT * height
    xy = p[triangles[on_deck].ravel()][:, :2]  # the deck faces' corners
    margin = FOOTPRINT_MARGIN * height
    x_min, y_min = np.percentile(xy, FOOTPRINT_PERCENTILE, axis=0) - margin
    x_max, y_max = np.percentile(xy, 100 - FOOTPRINT_PERCENTILE, axis=0) + margin
    above = p[:, 2] >= cut_z
    inside = above & (p[:, 0] >= x_min) & (p[:, 0] <= x_max) & (p[:, 1] >= y_min) & (p[:, 1] <= y_max)
    labels = components(len(p), weld_edges(p, triangles, 1e-5 * height), above)
    seeds = np.unique(labels[inside])
    mask = np.isin(labels, seeds[seeds >= 0]) & above
    # Outside the footprint, only what rises above the deck is load: a head crown or a rump that reaches above the cut
    # beside the deck stays with the body.
    outside = (p[:, 0] < x_min) | (p[:, 0] > x_max) | (p[:, 1] < y_min) | (p[:, 1] > y_max)
    mask &= ~(outside & (p[:, 2] < deck_z))
    levels = [
        {"height_share": round(float((edges[i] + edges[i + 1]) / 2 / height), 3), "area": round(float(totals[i]), 6)}
        for i in np.argsort(-totals)[:4]
    ]
    floors = [(deck_z + ground, (float(x_min), float(x_max), float(y_min), float(y_max)))]
    # Upper storeys: bands above the deck with at least a quarter of the deck's flat surface, all of it on the load.
    for index in np.flatnonzero(totals >= UNDERSIDE_SHARE * deck_area):
        if index <= deck_band + 1:  # the deck itself, and the band beside it that the same floor reaches into
            continue
        level = up & (centres[:, 2] >= edges[index]) & (centres[:, 2] < edges[index + 1])
        level &= mask[triangles].all(axis=1)
        if not level.any():
            continue
        z = float(np.average(centres[level, 2], weights=area[level]))
        if any(abs(z + ground - other) < 4 * BAND * height for other, _ in floors):
            continue
        corners = p[triangles[level].ravel()][:, :2]
        low = np.percentile(corners, FOOTPRINT_PERCENTILE, axis=0) + margin
        high = np.percentile(corners, 100 - FOOTPRINT_PERCENTILE, axis=0) - margin
        floors.append((z + ground, (float(low[0]), float(high[0]), float(low[1]), float(high[1]))))
    return Load(mask, deck_z + ground, cut_z + ground, (float(x_min), float(x_max), float(y_min), float(y_max)), deck_area, levels, floors)


def place_saddle(points: np.ndarray, triangles: np.ndarray, load: Load, rider_height: float) -> Dict[str, object]:
    """The floor point under the clearest column of a standing rider `rider_height` tall (model units).

    Every floor of the load is tried (the deck and any upper storey). The column has the rider's height and a fifth of it as radius,
    stays wholly inside its floor's footprint, and counts the load's vertices inside it. The fewest wins, then the lower floor, then
    the point nearest its floor's centre.
    """

    ground = float(points[:, 2].min())
    height = float(points[:, 2].max()) - ground
    centres, normals, area = faces(points, triangles)
    band = BAND * height
    radius = RIDER_RADIUS_SHARE * rider_height
    load_points = points[load.mask]
    rows = []
    for floor_index, (floor_z, (x_min, x_max, y_min, y_max)) in enumerate(load.floors or [(load.deck_z, load.footprint)]):
        on_floor = (
            (normals[:, 2] > FLAT) & (np.abs(centres[:, 2] - floor_z) <= band)
            & (centres[:, 0] >= x_min + radius) & (centres[:, 0] <= x_max - radius)
            & (centres[:, 1] >= y_min + radius) & (centres[:, 1] <= y_max - radius)
        )
        candidates = centres[on_floor]
        if not len(candidates):
            continue
        lifted = load_points[(load_points[:, 2] > floor_z + RIDER_FOOT_CLEARANCE * height) & (load_points[:, 2] < floor_z + rider_height)]
        if len(lifted):
            offsets = candidates[:, None, :2] - lifted[None, :, :2]
            crowd = (np.einsum("ijk,ijk->ij", offsets, offsets) < radius * radius).sum(axis=1)
        else:
            crowd = np.zeros(len(candidates), dtype=np.int64)
        centre = np.average(candidates[:, :2], axis=0, weights=area[on_floor])
        spread = np.linalg.norm(candidates[:, :2] - centre, axis=1)
        for k in range(len(candidates)):
            rows.append((int(crowd[k]), floor_index, float(spread[k]), np.array([candidates[k, 0], candidates[k, 1], floor_z])))
    if not rows:
        raise LoadError("no floor of the load has room for a rider's column")
    crowd, floor_index, _spread, point = min(rows, key=lambda row: row[:3])
    return {
        "point": point,
        "floor": floor_index,
        "floor_height_share": round((float(point[2]) - ground) / height, 4),
        "column_load_vertices": crowd,
        "column_radius": float(radius),
        "rider_height": float(rider_height),
        "candidates": len(rows),
    }


def roll_limit(points: np.ndarray, mask: np.ndarray, torso: np.ndarray, axis: np.ndarray, most_degrees: float) -> float:
    """The largest roll (degrees, up to `most_degrees`) about `axis` before the load reaches lower than the torso.

    A body that falls on its side with a tower on its back stops when the tower meets the ground: past
    that roll the grounding would lift the body off the ground onto the tower. The torso (`torso`: the body
    above the belly) is what lies on the ground, because the legs fold under a dying body.
    """

    axis = np.asarray(axis, dtype=float) / np.linalg.norm(axis)
    pivot = points.mean(axis=0)
    body, load = points[torso & ~mask] - pivot, points[mask] - pivot
    if not len(load):
        return float(most_degrees)
    sign = 1.0 if most_degrees >= 0 else -1.0
    best = 0.0
    for degrees in np.arange(0.0, abs(most_degrees) + 0.5, 1.0):
        angle = np.radians(sign * degrees)
        k = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
        turn = np.eye(3) + np.sin(angle) * k + (1 - np.cos(angle)) * (k @ k)
        if (load @ turn.T)[:, 2].min() < (body @ turn.T)[:, 2].min():
            break
        best = float(degrees)
    return sign * best


LOAD_BONE = "Spine"
RING_SHARE = 0.06  # the load's weight fades into the body over this share of the body's height


def nearest_distance(points: np.ndarray, targets: np.ndarray, chunk: int = 256) -> np.ndarray:
    """Distance from each point to the nearest target (brute force in chunks; Blender's Python has no KD-tree in numpy)."""

    result = np.full(len(points), np.inf)
    if not len(targets):
        return result
    t = targets.astype(np.float32)
    for start in range(0, len(points), chunk):
        block = points[start:start + chunk].astype(np.float32)
        d = ((block[:, None, :] - t[None, :, :]) ** 2).sum(axis=2)
        result[start:start + chunk] = np.sqrt(d.min(axis=1))
    return result


def bind_load(points: np.ndarray, mask: np.ndarray, indices: np.ndarray, weights: np.ndarray, names: List[str], ring: float) -> Tuple[np.ndarray, np.ndarray, Dict[str, int]]:
    """Bind the load wholly to the Spine and fade that into the body's own weights over `ring` from the load.

    The load is one rigid part (rigid_plates in lib/tripo_chains.py binds a plate the same way): every load vertex has
    weight 1 on one bone. A body vertex `d` from the nearest load vertex keeps `d / ring` of its own weights and takes
    the rest on the Spine, eased, so the skin under the load follows it with no seam. Rows keep at most as many
    influences as before and sum to 1.
    """

    bone = names.index(LOAD_BONE)
    out_i, out_w = indices.copy(), weights.copy()
    out_i[mask] = bone
    out_w[mask] = 0.0
    out_w[mask, 0] = 1.0
    candidates = np.flatnonzero(~mask)
    distance = nearest_distance(points[candidates], points[mask]) if mask.any() else np.full(len(candidates), np.inf)
    inside = distance < ring
    ring_rows = candidates[inside]
    share = 1.0 - distance[inside] / ring
    share = share * share * (3 - 2 * share)
    slots = indices.shape[1]
    for row, extra in zip(ring_rows, share):
        dense: Dict[int, float] = {}
        for slot in range(slots):
            if weights[row, slot] > 0:
                dense[int(indices[row, slot])] = dense.get(int(indices[row, slot]), 0.0) + (1 - extra) * float(weights[row, slot])
        dense[bone] = dense.get(bone, 0.0) + float(extra)
        kept = sorted(dense.items(), key=lambda item: -item[1])[:slots]
        total = sum(value for _, value in kept) or 1.0
        out_i[row] = [item[0] for item in kept] + [bone] * (slots - len(kept))
        out_w[row] = [item[1] / total for item in kept] + [0.0] * (slots - len(kept))
    return out_i, out_w, {"load_vertices": int(mask.sum()), "ring_vertices": int(len(ring_rows))}
