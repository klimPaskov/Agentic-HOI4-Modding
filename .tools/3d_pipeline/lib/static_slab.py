"""Ground slab rule for static models (buildings and landmarks): find a thin base slab, flatten its top, square its outline.

A generated building often stands on a thin slab of ground that reaches past its walls. Tripo draws it a little off: a
corner out of line, a top that tilts, an edge that bows. The rule works on the model's arrays in Blender space (z up,
ground at the bottom) and leaves the model alone when it finds no slab.

A base slab is a plate of up-facing triangles that

- lies in the lowest band of the model (`SLAB_BAND` of its height) and is thin (its thickness fits that band),
- is a rectangle in the building's own frame: its outline fills `RECT_FILL` of the bounding rectangle of its vertices
  (a round base is not a slab),
- reaches past the building: the model above it stays inside the outline by `INSET_SHARE` of the slab's width on every
  side, and
- is not a stepped base: when a second up-facing plate of `TIER_SHARE` of the slab's area lies within `TIER_RISE`
  thicknesses above its top (a landmark's stairs, tiers one above another), the rule leaves the model alone.

`square_slab` flattens the plate's vertices to the plate's median height and moves the slab's own vertices (those in
its thickness) onto the sides of a rectangle in the principal frame of its outline (a yaw about z). Each side sits
where most of the vertices in the outer `SIDE_BAND` of the slab's width lie, so one outlier corner is pulled back in. No
vertex is added, removed or re-mapped, so the UVs stay.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

SLAB_BAND = 0.12  # the slab lies in the lowest share of the model's height
UP_DEGREES = 20.0  # a triangle faces up within this of straight up
FLAT_SHARE = 1.5  # slab thicknesses above its top that still belong to it (a skirt, a worn edge)
INSET_SHARE = 0.03  # the model above stays inside the slab's outline by this share of the slab's width
RECT_FILL = 0.9  # a slab fills this share of the bounding rectangle of its vertices
TIER_SHARE = 0.25  # a second tier (a stair) carries this share of the slab's area, a ledge or a flat roof near the ground does not
TIER_RISE = 3.0  # and lies within this many slab thicknesses above its top
MIN_AREA_SHARE = 0.15  # a slab's top is at least this share of the model's footprint area
SIDE_BAND = 0.1  # the outer share of the slab's width whose vertices set one side of the rectangle
SNAP_BAND = 0.015  # vertices this close inside a side (and every vertex outside it) go onto it (under the inset)
TILT_DEGREES = 8.0  # the check: a slab-top corner's shading normal leans at most this from straight up


def to_frame(xy: np.ndarray, yaw: float) -> np.ndarray:
    """Points in the frame whose x axis points along `yaw`: u = x cos + y sin, v = -x sin + y cos."""

    c, s = np.cos(yaw), np.sin(yaw)
    xy = np.asarray(xy, dtype=float)
    return np.stack([xy[:, 0] * c + xy[:, 1] * s, -xy[:, 0] * s + xy[:, 1] * c], axis=1)


def from_frame(uv: np.ndarray, yaw: float) -> np.ndarray:
    c, s = np.cos(yaw), np.sin(yaw)
    uv = np.asarray(uv, dtype=float)
    return np.stack([uv[:, 0] * c - uv[:, 1] * s, uv[:, 0] * s + uv[:, 1] * c], axis=1)


def convex_hull(points: np.ndarray) -> np.ndarray:
    pts = sorted(set(map(tuple, np.round(np.asarray(points, dtype=float), 9))))
    if len(pts) < 3:
        return np.array(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list = []
    upper: list = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1])


def polygon_area(poly: np.ndarray) -> float:
    if len(poly) < 3:
        return 0.0
    x, y = poly[:, 0], poly[:, 1]
    return float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)


def principal_yaw(xy: np.ndarray) -> float:
    """The yaw that turns the outline's sides onto the axes (modulo a quarter turn): the convex hull's edges vote, by
    length, for a direction."""

    hull = convex_hull(xy)
    if len(hull) < 3:
        return 0.0
    edges = np.roll(hull, -1, axis=0) - hull
    length = np.linalg.norm(edges, axis=1)
    angle = np.arctan2(edges[:, 1], edges[:, 0])
    return float(np.angle((length * np.exp(4j * angle)).sum()) / 4.0)


def face_normals(points: np.ndarray, triangles: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """(unit normals turned outward by the mesh's signed volume, so the winding convention does not matter, areas)."""

    a, b, c = points[triangles[:, 0]], points[triangles[:, 1]], points[triangles[:, 2]]
    cross = np.cross(b - a, c - a)
    length = np.linalg.norm(cross, axis=1)
    normal = cross / np.maximum(length, 1e-18)[:, None]
    if float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) < 0:
        normal = -normal
    return normal, length / 2.0


def find_slab(points: np.ndarray, triangles: np.ndarray) -> Optional[dict]:
    """The base slab of a model, or None. {top_z, thickness, yaw, lo, hi (frame bounds of the plate), width, plate
    (triangle mask), own (vertex indices the squaring may move), inset}."""

    points = np.asarray(points, dtype=float)
    triangles = np.asarray(triangles, dtype=np.int64)
    if not len(triangles):
        return None
    used = points[np.unique(triangles)]  # vertices no triangle uses (a collision box's) do not count
    low, high = float(used[:, 2].min()), float(used[:, 2].max())
    height = high - low
    if height <= 0:
        return None
    normal, area = face_normals(points, triangles)
    corner_z = points[triangles][:, :, 2]
    mid_z = corner_z.mean(axis=1)
    up = (normal[:, 2] >= np.cos(np.radians(UP_DEGREES))) & (area > 0)
    candidate = up & (corner_z.max(axis=1) <= low + SLAB_BAND * height)
    if not candidate.any():
        return None
    # the plate: the up-facing triangles of the band that share the height of the largest of them
    bucket = SLAB_BAND * height / 10.0
    levels = np.round((mid_z - low) / bucket).astype(int)
    best_mask, best_area = None, 0.0
    for level in np.unique(levels[candidate]):
        mask = candidate & (np.abs(levels - level) <= 1)
        total = float(area[mask].sum())
        if total > best_area:
            best_mask, best_area = mask, total
    top_z = float(np.median(mid_z[best_mask]))
    plate_vertices = np.unique(triangles[best_mask])
    plate_xy = points[plate_vertices][:, :2]
    footprint = polygon_area(convex_hull(used[:, :2]))
    if best_area < MIN_AREA_SHARE * footprint:
        return None
    yaw = principal_yaw(plate_xy)
    frame = to_frame(plate_xy, yaw)
    lo, hi = frame.min(axis=0), frame.max(axis=0)
    width = float(max(hi - lo))
    if width <= 0 or polygon_area(convex_hull(frame)) < RECT_FILL * float(np.prod(hi - lo)):
        return None
    thickness = max(top_z - low, 1e-9)
    if thickness > SLAB_BAND * height:
        return None
    flat = FLAT_SHARE * thickness
    above = used[:, 2] > top_z + flat
    inset = 0.0
    if above.any():
        a = to_frame(used[above][:, :2], yaw)
        inset = min(float((a.min(axis=0) - lo).min()), float((hi - a.max(axis=0)).min()))
        if inset < INSET_SHARE * width:
            return None
    tier = up & (mid_z > top_z + flat) & (mid_z <= top_z + flat + TIER_RISE * thickness)
    if float(area[tier].sum()) >= TIER_SHARE * best_area:
        return None
    # the slab's own vertices: its top plate, its bottom, and its side faces (vertical faces that span its whole
    # thickness, from the model's lowest point to the plate), so a wall's base or a chimney's foot is never moved
    eps = 0.02 * thickness
    span = (corner_z.min(axis=1) <= low + eps) & (corner_z.max(axis=1) >= top_z - eps) & (corner_z.max(axis=1) <= top_z + eps)
    side = span & (np.abs(normal[:, 2]) < 0.5) & (area > 0)
    bottom = (normal[:, 2] <= -np.cos(np.radians(UP_DEGREES))) & (corner_z.max(axis=1) <= low + eps) & (area > 0)
    own = np.unique(np.concatenate([plate_vertices, triangles[side].ravel(), triangles[bottom].ravel()]))
    return {"top_z": top_z, "thickness": thickness, "yaw": yaw, "lo": lo, "hi": hi, "width": width, "plate": best_mask,
            "plate_vertices": plate_vertices, "own": own, "inset": inset}


def robust_bounds(slab: dict, points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """The rectangle (frame lo, hi) of the slab's sides: each side where most of the vertices in the outer
    `SIDE_BAND` of the width lie (a high percentile on a low side), so an outlier corner pulled out does not set it."""

    frame = to_frame(points[slab["own"]][:, :2], slab["yaw"])
    lo, hi = frame.min(axis=0), frame.max(axis=0)
    band = SIDE_BAND * slab["width"]
    new_lo, new_hi = lo.copy(), hi.copy()
    for axis in (0, 1):
        near_lo = frame[frame[:, axis] <= lo[axis] + band, axis]
        near_hi = frame[frame[:, axis] >= hi[axis] - band, axis]
        # a corner pulled out is an outlier on the outside: the side is where most of its vertices lie, inside it
        new_lo[axis], new_hi[axis] = float(np.percentile(near_lo, 70)), float(np.percentile(near_hi, 30))
    return new_lo, new_hi


def outline_error(slab: dict, points: np.ndarray) -> float:
    """How far (in model units) the farthest slab vertex lies outside the robust rectangle."""

    lo, hi = robust_bounds(slab, points)
    frame = to_frame(points[slab["own"]][:, :2], slab["yaw"])
    outside = np.maximum(np.maximum(lo - frame, frame - hi), 0.0)
    return float(outside.max()) if len(frame) else 0.0


def top_spread(slab: dict, points: np.ndarray) -> float:
    """The height spread of the plate's vertices."""

    z = points[slab["plate_vertices"]][:, 2]
    return float(z.max() - z.min())


def square_slab(points: np.ndarray, slab: dict) -> Tuple[np.ndarray, dict]:
    """(the points with the slab flattened and squared, a report)."""

    out = np.array(points, dtype=float, copy=True)
    before = {"outline_error": outline_error(slab, points), "top_spread": top_spread(slab, points)}
    lo, hi = robust_bounds(slab, points)
    own = slab["own"]
    frame = to_frame(out[own][:, :2], slab["yaw"])
    snap = SNAP_BAND * slab["width"]
    for axis in (0, 1):
        frame[frame[:, axis] <= lo[axis] + snap, axis] = lo[axis]
        frame[frame[:, axis] >= hi[axis] - snap, axis] = hi[axis]
    out[own, :2] = from_frame(frame, slab["yaw"])
    out[slab["plate_vertices"], 2] = slab["top_z"]
    moved = np.linalg.norm(out - points, axis=1)
    after_slab = dict(slab)
    report = {"before": before, "after": {"outline_error": outline_error(after_slab, out), "top_spread": top_spread(after_slab, out)},
              "top_z": round(slab["top_z"], 5), "width": round(slab["width"], 4), "yaw_degrees": round(float(np.degrees(slab["yaw"])), 3),
              "vertices_moved": int((moved > 1e-9).sum()), "largest_move": round(float(moved.max()), 5)}
    return out, report


def tilted_corner_normals(points: np.ndarray, triangles: np.ndarray, normals: np.ndarray, slab: dict) -> List[float]:
    """The lean (degrees from straight up) of each slab-top corner's shading normal that leans more than `TILT_DEGREES`."""

    plate = np.nonzero(slab["plate"])[0]
    leans = []
    for t in plate:
        for corner in triangles[t]:
            n = normals[corner]
            length = float(np.linalg.norm(n))
            if length < 1e-9:
                continue
            lean = float(np.degrees(np.arccos(np.clip(abs(n[2]) / length, -1.0, 1.0))))
            if lean > TILT_DEGREES:
                leans.append(lean)
    return leans


def slab_findings(points: np.ndarray, triangles: np.ndarray, normals: Optional[np.ndarray] = None) -> List[Tuple[str, str, str]]:
    """STATIC-SLAB: the exported model's base slab is warped (its top is not one plane, an outline vertex is out of line
    with its side, or a top corner shades tilted). (rule, severity, message) for each."""

    slab = find_slab(points, triangles)
    if slab is None:
        return []
    findings = []
    spread = top_spread(slab, points)
    if spread > 0.01 * slab["thickness"] + 1e-6:
        findings.append(("STATIC-SLAB", "error", f"the base slab's top is not flat: its corners differ by {spread:.3f} in height"))
    error = outline_error(slab, points)
    if error > 0.005 * slab["width"]:
        findings.append(("STATIC-SLAB", "error", f"a corner of the base slab sticks out {error:.3f} past its straight edge ({100 * error / slab['width']:.1f} % of its width)"))
    if normals is not None and len(normals) == len(points):
        leans = tilted_corner_normals(points, triangles, normals, slab)
        if leans:
            findings.append(("STATIC-SLAB", "error", f"{len(leans)} corners of the base slab's top shade tilted up to {max(leans):.0f} degrees off flat, so the slab shows a pale facet"))
    return findings


def slab_triangles(slab: dict, points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """Mask of the triangles that make up the slab: its top plate, its side faces and its bottom (those whose vertices
    are all the slab's own). They shade flat."""

    own = np.zeros(len(points), dtype=bool)
    own[slab["own"]] = True
    return own[triangles].all(axis=1)


# Blender side (duck-typed on a bpy Mesh, so this module imports no bpy) -------------------------------------------

KINDS = ("building", "landmark")


def _mesh_arrays(mesh) -> Tuple[np.ndarray, np.ndarray]:
    mesh.calc_loop_triangles()
    positions = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", positions)
    triangles = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", triangles)
    return positions.reshape(-1, 3), triangles.reshape(-1, 3)


def square_mesh(mesh, kind: str) -> Tuple[Optional[dict], dict]:
    """Find the base slab of a building's or landmark's mesh and square it in place. (the slab or None, a report)."""

    if kind not in KINDS:
        return None, {"slab": "not a kind with a base slab"}
    positions, triangles = _mesh_arrays(mesh)
    slab = find_slab(positions, triangles)
    if slab is None:
        return None, {"slab": "none found (no thin rectangular base reaching past the building, or a stepped or round base)"}
    squared, report = square_slab(positions, slab)
    mesh.vertices.foreach_set("co", squared.ravel())
    mesh.update()
    return slab, report


def shade_flat(mesh, slab: dict) -> int:
    """Give the slab's faces flat shading normals: their edges are sharp and every corner takes its face's normal.
    A corner shared with the slab's sides must not lean (it shades the slab top with a pale tilted facet). Returns the
    number of faces."""

    positions, triangles = _mesh_arrays(mesh)
    flat = slab_triangles(slab, positions, triangles)
    polygons = sorted({mesh.loop_triangles[int(i)].polygon_index for i in np.nonzero(flat)[0]})
    keys = {key for p in polygons for key in mesh.polygons[p].edge_keys}
    for edge in mesh.edges:
        if tuple(sorted(edge.vertices)) in keys:
            edge.use_edge_sharp = True
    corner = [tuple(c.vector) for c in mesh.corner_normals]
    for p in polygons:
        polygon = mesh.polygons[p]
        for loop in polygon.loop_indices:
            corner[loop] = tuple(polygon.normal)
    mesh.normals_split_custom_set(corner)
    return len(polygons)
