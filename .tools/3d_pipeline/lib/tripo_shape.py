"""Shape check for a part that was reduced to a triangle budget (no Blender needed).

A weapon reduced by collapse decimation can fall apart: a mesh split along its UV seams has one shell per UV
island, and the collapse shrinks each island's border, so the pieces separate. `shape_report` compares the
original and the reduced part in two ways and `shape_problems` turns the numbers into refusals:

- shells: connected pieces of the surface after welding vertices that share a position. The count must not
  grow and no piece may sit far from the biggest one (`max_gap`, a share of the part's longest side).
- silhouettes: both parts are rasterised from three orthographic views (front, side, top) into masks of one
  shared frame (the original's bounding box), and the intersection over union of each pair must reach `min_iou`.

Positions are (N, 3) float arrays and triangles (T, 3) integer indices, in any common space.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

VIEWS = {"front": (0, 2), "side": (1, 2), "top": (0, 1)}  # the two axes kept from each view
MIN_IOU = 0.97
MAX_GAP = 0.02
MASK_SIZE = 384
TOLERANCE_PIXELS = 1


def weld(positions: np.ndarray, tolerance: float) -> np.ndarray:
    """For each vertex the index of the welded vertex (positions within `tolerance` share one)."""

    keys = np.round(positions / max(tolerance, 1e-12)).astype(np.int64)
    _unique, inverse = np.unique(keys, axis=0, return_inverse=True)
    return inverse.ravel()


def shells(positions: np.ndarray, triangles: np.ndarray, tolerance: float) -> List[np.ndarray]:
    """The welded connected pieces, each as the array of its welded vertex ids, biggest first."""

    welded = weld(positions, tolerance)
    count = int(welded.max()) + 1 if len(welded) else 0
    parent = np.arange(count)

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for a, b, c in welded[triangles]:
        for left, right in ((a, b), (b, c), (c, a)):
            root_left, root_right = find(left), find(right)
            if root_left != root_right:
                parent[root_left] = root_right
    used = np.unique(welded[triangles])
    groups: Dict[int, List[int]] = {}
    for node in used:
        groups.setdefault(find(int(node)), []).append(int(node))
    return sorted((np.array(group) for group in groups.values()), key=len, reverse=True)


def box_gap(a_low: np.ndarray, a_high: np.ndarray, b_low: np.ndarray, b_high: np.ndarray) -> float:
    """Distance between two axis-aligned boxes (0 when they touch or overlap)."""

    separation = np.maximum(0.0, np.maximum(a_low - b_high, b_low - a_high))
    return float(np.linalg.norm(separation))


def shell_summary(positions: np.ndarray, triangles: np.ndarray, tolerance: float) -> dict:
    """Shell count, the sizes of the biggest ones and the largest gap from a small shell to the biggest shell."""

    pieces = shells(positions, triangles, tolerance)
    welded = weld(positions, tolerance)
    representative = np.zeros((int(welded.max()) + 1, 3)) if len(welded) else np.zeros((0, 3))
    representative[welded] = positions
    boxes = [(representative[piece].min(axis=0), representative[piece].max(axis=0)) for piece in pieces]
    length = float(np.ptp(positions, axis=0).max()) if len(positions) else 0.0
    gap = max((box_gap(*boxes[0], *box) for box in boxes[1:]), default=0.0)
    return {"shells": len(pieces), "largest": [len(p) for p in pieces[:5]], "max_gap": gap, "max_gap_share": gap / length if length else 0.0}


def rasterize(points: np.ndarray, triangles: np.ndarray, size: int) -> np.ndarray:
    """Fill the triangles of a 2D point set (coordinates already in [0, 1]) into a size x size boolean mask."""

    mask = np.zeros((size, size), dtype=bool)
    pixels = points * (size - 1)
    for triangle in triangles:
        a, b, c = pixels[triangle]
        x0, x1 = int(np.floor(min(a[0], b[0], c[0]))), int(np.ceil(max(a[0], b[0], c[0])))
        y0, y1 = int(np.floor(min(a[1], b[1], c[1]))), int(np.ceil(max(a[1], b[1], c[1])))
        if x1 < 0 or y1 < 0 or x0 >= size or y0 >= size:
            continue
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, size - 1), min(y1, size - 1)
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        determinant = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(determinant) < 1e-12:
            # A sliver: mark the pixels its three corners fall in so thin parts do not vanish.
            for corner in (a, b, c):
                mask[int(round(corner[1])), int(round(corner[0]))] = True
            continue
        w1 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / determinant
        w2 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / determinant
        inside = (w1 >= -0.5 / size) & (w2 >= -0.5 / size) & (1 - w1 - w2 >= -0.5 / size)
        mask[y0 : y1 + 1, x0 : x1 + 1] |= inside
    return mask


def silhouettes(positions: np.ndarray, triangles: np.ndarray, low: np.ndarray, high: np.ndarray, size: int = MASK_SIZE) -> Dict[str, np.ndarray]:
    """Front, side and top masks of a part in the frame of the box (low, high), one pixel scale for both axes of a view."""

    masks = {}
    for name, (u, v) in VIEWS.items():
        # Each view is framed on its own extent (the original's), so a slim part is not a few pixels in its end-on view.
        span = float(max(high[u] - low[u], high[v] - low[v])) or 1.0
        margin = 0.02
        scale = (1.0 - 2 * margin) / span
        flat = np.stack([(positions[:, u] - low[u]) * scale + margin, (positions[:, v] - low[v]) * scale + margin], axis=1)
        masks[name] = rasterize(flat, triangles, size)
    return masks


def dilate(mask: np.ndarray, pixels: int) -> np.ndarray:
    """Grow a mask by `pixels` in every direction (square neighbourhood)."""

    grown = mask.copy()
    for _ in range(pixels):
        padded = np.pad(grown, 1)
        grown = np.zeros_like(grown)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                grown |= padded[dy : dy + mask.shape[0], dx : dx + mask.shape[1]]
    return grown


def iou(a: np.ndarray, b: np.ndarray, tolerance: int = TOLERANCE_PIXELS) -> float:
    """Intersection over union of two masks, each grown by `tolerance` pixels first.

    A thin part (a haft, a blade tip) changes by a pixel when its outline moves a fraction of a pixel, so
    the raw overlap of even the same mesh shifted by a quarter pixel is 0.94 to 0.97. Growing both masks by
    a pixel keeps a missing spike, a thinner blade or a moved part visible and drops that rasterising noise.
    """

    if tolerance:
        a, b = dilate(a, tolerance), dilate(b, tolerance)
    union = int((a | b).sum())
    return float((a & b).sum() / union) if union else 1.0


def shape_report(original: Tuple[np.ndarray, np.ndarray], reduced: Tuple[np.ndarray, np.ndarray], size: int = MASK_SIZE) -> dict:
    """Shell and silhouette numbers for an original part and its reduction, both as (positions, triangles)."""

    low, high = original[0].min(axis=0), original[0].max(axis=0)
    tolerance = float(np.max(high - low)) * 1e-5
    before, after = silhouettes(*original, low, high, size), silhouettes(*reduced, low, high, size)
    return {
        "shells_before": shell_summary(*original, tolerance),
        "shells_after": shell_summary(*reduced, tolerance),
        "iou": {view: round(iou(before[view], after[view]), 4) for view in VIEWS},
        "triangles_before": int(len(original[1])),
        "triangles_after": int(len(reduced[1])),
        "mask_size": size,
    }


def shape_problems(report: dict, min_iou: float = MIN_IOU, max_gap: float = MAX_GAP) -> List[str]:
    """What is wrong with a reduced part, one sentence each; an empty list means the shape holds."""

    problems = []
    before, after = report["shells_before"], report["shells_after"]
    if after["shells"] > before["shells"]:
        problems.append(f"the reduction split the part into {after['shells']} shells (it had {before['shells']})")
    if after["max_gap_share"] > max_gap and after["max_gap_share"] > before["max_gap_share"]:
        problems.append(f"a shell sits {after['max_gap_share']:.1%} of the part's length from the main body (limit {max_gap:.1%})")
    for view, value in report["iou"].items():
        if value < min_iou:
            problems.append(f"the {view} silhouette agrees only {value:.3f} with the original (needs {min_iou})")
    return problems
