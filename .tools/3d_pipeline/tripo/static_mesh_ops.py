"""Surface cleanup of the static-model route, on a bmesh in Blender (`tripo/static_model_blender.py` uses them).

- `remove_slivers`: needle slivers and tiny loose open flakes (`lib.static_kinds.needle_triangles`, `loose_flakes`) go.
- `thicken_cards`: flat one-sided cards (`lib.static_kinds.flat_cards`) are solidified, centred on the sheet, as thick as
  `lib.static_kinds.card_thickness` allows, and marked in the deform layer's group `CARD_GROUP`.
- `card_cost`: the triangles `thicken_cards` will add, for the triangle budget.
- `crease_shading`: on the Blender mesh, shading normals that never lean past the crease angle from their own face.

`size` is the model's size (its largest side). The rules themselves are in `lib/static_kinds.py`, where the tests reach them.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bmesh
import numpy as np
from mathutils import Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from lib import static_kinds as sk

CARD_GROUP = 0  # the vertex group index that marks thickened cards until the last reduction
CREASE_DEGREES = 40.0  # faces meeting at more than this shade apart (kit rule, the route's smooth-by-angle limit)


def bm_arrays(bm):
    """A triangulated bmesh's vertex positions and triangles (indices into them), in bmesh order."""

    bm.verts.index_update()
    bm.faces.index_update()
    points = np.array([v.co[:] for v in bm.verts]) if len(bm.verts) else np.zeros((0, 3))
    triangles = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=np.int64).reshape(-1, 3)
    return points, triangles


def remove_slivers(bm, size):
    """Needle slivers sticking out of a surface (`sk.needle_triangles`, removed a round at a time while any are left,
    since taking one off can leave the next) and tiny loose open flakes (`sk.loose_flakes`) are deleted. A reviewer saw
    them on a Smart Mesh tank as thin stray spikes along the hull, the glacis, the skirts and the rear deck."""

    points, triangles = bm_arrays(bm)
    open_before = sk.open_edge_count(triangles)
    triangles_before = len(triangles)
    needles = 0
    for _ in range(4):
        points, triangles = bm_arrays(bm)
        found = sk.needle_triangles(points, triangles, size)
        if not found:
            break
        faces = list(bm.faces)
        bmesh.ops.delete(bm, geom=[faces[i] for i in found], context="FACES")
        needles += len(found)
    points, triangles = bm_arrays(bm)
    flakes = sk.loose_flakes(points, triangles, size)
    faces = list(bm.faces)
    doomed = [faces[i] for piece in flakes for i in piece]
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context="FACES")
    points, triangles = bm_arrays(bm)
    return {"needles_removed": needles, "flakes_removed": len(flakes), "flake_triangles": len(doomed), "triangles_before": triangles_before,
            "triangles_after": len(triangles), "open_edges_before": open_before, "open_edges_after": sk.open_edge_count(triangles)}


HULL_PIECE_SHARE = 0.10  # a piece whose bounding box diagonal is at most this share of the model's is small (kit rule: a bolt, a hook, a fitting)
HULL_BOX_FILL = 0.6  # a hull filling less than this share of the piece's oriented bounding box is a wedge, so the box stands in (kit rule: fittings are boxes)
HULL_PLATE_FLAT = 0.2  # a piece thinner than this share of its longest side is a plate: its hull (a slanted wedge) stands in only above HULL_PLATE_FILL
HULL_PLATE_FILL = 0.75
HULL_WEDGE_FILL = 0.55  # a piece whose hull fills less than this of its box and whose faces mostly lean off the box's axes (under HULL_WEDGE_ALIGNED
HULL_WEDGE_ALIGNED = 0.5  # of the area within 20 degrees of an axis) is a pinched wedge, a box a reduction cut into a prism: the box stands in
HULL_AXIS_COS = math.cos(math.radians(20.0))
HULL_PIECE_CONVEX = (0.9, 1.05)  # a small closed piece whose volume is outside this share of its convex hull's is crumpled (kit rule)


def _nearest_uv(faces, samples, uv_layer):
    """Each face takes the UV of the nearest sample (centre, normal, uv) that faces the same way."""

    for f in faces:
        centre, normal = f.calc_center_median(), f.normal
        best = min(samples, key=lambda s: (s[0] - centre).length * (1.0 if s[1].dot(normal) > 0 else 4.0))
        if uv_layer and best[2] is not None:
            for loop in f.loops:
                loop[uv_layer].uv = (float(best[2][0]), float(best[2][1]))


def _box_corners(mid, axes, spans):
    """The eight corners of the oriented box (axes through mid) that holds spans, the points' coordinates along the axes."""

    lo, hi = spans.min(axis=0), spans.max(axis=0)
    return [mid + np.array([x, y, z]) @ axes for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


def hull_crumpled_pieces(bm):
    """Small separate pieces whose surface is crumpled (their volume is not within `HULL_PIECE_CONVEX` of their convex
    hull's, or they are not closed) become their convex hull, in the colour they had. A Smart Mesh tank's small fittings
    (tow hooks, brackets) come out of the reduction as lumps of scattered facets: a reviewer saw "a crumpled blob under the
    rear deck". The hull's faces take the UV (one texel) of the nearest of the piece's own faces facing the same way.
    Returns what was replaced."""

    points, triangles = bm_arrays(bm)
    faces = list(bm.faces)
    uv_layer = bm.loops.layers.uv.active
    replaced = []
    groups = [[faces[i] for i in piece] for piece in sk.small_pieces(points, triangles, HULL_PIECE_SHARE)]
    for group in groups:
        closed = all(len(e.link_faces) == 2 for f in group for e in f.edges)
        if not closed:
            continue  # an open sheet is not a crumpled solid
        verts = list({v for f in group for v in f.verts})
        scratch = bmesh.new()
        copies = {v: scratch.verts.new(v.co) for v in verts}
        hull = bmesh.ops.convex_hull(scratch, input=list(copies.values()))
        for f in [g for g in hull["geom_interior"] if isinstance(g, bmesh.types.BMFace)]:
            scratch.faces.remove(f)
        hull_faces = [f for f in scratch.faces]
        if not hull_faces:
            scratch.free()
            continue
        hull_volume = abs(scratch.calc_volume(signed=False)) if hasattr(scratch, "calc_volume") else 0.0
        hv = np.array([v.co[:] for v in verts])
        mid = hv.mean(axis=0)
        axes = np.linalg.svd(hv - mid, full_matrices=False)[2]
        spans = (hv - mid) @ axes.T
        extent = spans.max(axis=0) - spans.min(axis=0)
        obb_volume = float(np.prod(extent))
        centre_at = [round(float(x), 3) for x in mid]
        scratch.free()
        own_volume = abs(sum(f.calc_area() * (f.calc_center_median().dot(f.normal)) for f in group)) / 3.0
        ratio = own_volume / hull_volume if hull_volume > 1e-12 else 1.0
        low, high = HULL_PIECE_CONVEX
        fill = hull_volume / obb_volume if obb_volume > 1e-12 else 1.0
        areas = np.array([f.calc_area() for f in group])
        aligned = float(sum(a for a, f in zip(areas, group) if np.abs(axes @ np.array(f.normal[:])).max() > HULL_AXIS_COS) / max(areas.sum(), 1e-12))
        pinched = bool(fill < HULL_WEDGE_FILL and aligned < HULL_WEDGE_ALIGNED)
        if low <= ratio <= high and not pinched:
            continue
        samples = [(f.calc_center_median().copy(), f.normal.copy(), np.mean([l[uv_layer].uv[:] for l in f.loops], axis=0) if uv_layer else None) for f in group]
        bmesh.ops.delete(bm, geom=group, context="FACES_ONLY")
        flat = bool(extent.min() < HULL_PLATE_FLAT * extent.max())
        boxed = bool(pinched or fill < HULL_BOX_FILL or (flat and fill < HULL_PLATE_FILL))
        if boxed:
            corners = _box_corners(mid, axes, spans)
            bmesh.ops.delete(bm, geom=[v for v in verts if v.is_valid], context="VERTS")
            verts = [bm.verts.new(Vector(c.tolist())) for c in corners]
        made = bmesh.ops.convex_hull(bm, input=verts)
        bmesh.ops.delete(bm, geom=[g for g in made["geom_interior"] if isinstance(g, bmesh.types.BMVert)], context="VERTS")
        bmesh.ops.delete(bm, geom=[e for e in {e for v in verts if v.is_valid for e in v.link_edges} if not e.link_faces], context="EDGES")
        _nearest_uv({f for v in verts if v.is_valid for f in v.link_faces}, samples, uv_layer)
        replaced.append({"triangles": len(group), "volume_share": round(float(ratio), 3), "box": boxed, "pinched": pinched, "aligned": round(aligned, 3), "hull_volume": float(hull_volume), "obb_volume": obb_volume, "own_volume": float(own_volume), "centre": centre_at, "extent": [round(float(x), 4) for x in extent]})
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return {"pieces": len(replaced), "replaced": replaced}


def double_inside_out_walls(bm):
    """Each wall that faces into the model (`sk.inside_out_walls`) gets a reversed copy, so it shows from the outside too.
    Returns the count."""

    points, triangles = bm_arrays(bm)
    found = sk.inside_out_walls(points, triangles)
    faces = list(bm.faces)
    walls = [faces[i] for i in found]
    if walls:
        copies = [g for g in bmesh.ops.duplicate(bm, geom=walls)["geom"] if isinstance(g, bmesh.types.BMFace)]
        bmesh.ops.reverse_faces(bm, faces=copies)
    return {"walls": len(walls)}


def thicken_cards(bm, size):
    """Flat one-sided cards (`sk.flat_cards`: a drive sprocket, a bogie arm modelled as one open sheet) are given a
    thickness (`sk.card_thickness`, bounded by the gap to their neighbours), centred on the sheet, so they are no
    longer paper cutouts with open rims. The new rim faces take one colour from the rim (as a cap does)."""

    # the deform layer first: adding a layer reallocates the vertex data, which removes every vertex reference taken before
    deform = bm.verts.layers.deform.verify()
    points, triangles = bm_arrays(bm)
    cards = sk.flat_cards(points, triangles, size)
    faces = list(bm.faces)
    uv_layer = bm.loops.layers.uv.active
    done = []
    for card in cards:
        thickness = sk.card_thickness(card, points, triangles, size)
        own = [faces[i] for i in card["triangles"]]
        if thickness <= 1e-6 * size or not all(f.is_valid for f in own):
            done.append({"triangles": len(own), "thickness": 0.0})
            continue
        before_verts = {v for f in own for v in f.verts}
        before_faces = set(bm.faces)
        bmesh.ops.solidify(bm, geom=own, thickness=thickness)
        new_faces = [f for f in bm.faces if f not in before_faces]
        shell = before_verts | {v for f in new_faces for v in f.verts}
        added = [v for v in shell if v not in before_verts]
        if added:
            # solidify offsets one way; the shell is moved back by half, so the card's middle stays where Tripo put it
            shift = (sum((v.co for v in added), Vector()) / len(added) - sum((v.co for v in before_verts), Vector()) / len(before_verts)) / 2
            for v in shell:
                v.co -= shift
        if uv_layer is not None:
            for face in new_faces:
                if all(v in before_verts for v in face.verts) or not any(v in before_verts for v in face.verts):
                    continue  # the sheet's own two sides keep their texture; only the rim faces are one colour
                first = face.loops[0][uv_layer].uv.copy()
                for loop in face.loops:
                    loop[uv_layer].uv = first
        for v in shell:
            v[deform][CARD_GROUP] = 1.0  # the reduction after the cuts leaves these alone (its shortest edges are their rims)
        done.append({"triangles": len(own), "thickness": round(thickness, 4), "faces_added": len(new_faces)})
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    points, triangles = bm_arrays(bm)
    return {"cards": done, "thickened": sum(1 for c in done if c["thickness"] > 0), "open_edges_after": sk.open_edge_count(triangles)}


def _corner_leans(mesh, limit):
    """Per polygon, whether any of its corners' shading normals leans more than `limit` (a cosine) from its normal."""

    corner = mesh.corner_normals
    return [any(corner[i].vector.dot(p.normal) < limit for i in p.loop_indices) for p in mesh.polygons]


def _clear_custom_normals(mesh):
    """Drop custom split normals (a glTF import sets the file's own normals as custom ones). True when there were any."""

    if not mesh.has_custom_normals:
        return False
    layer = mesh.attributes.get("custom_normal")
    if layer is not None:
        mesh.attributes.remove(layer)
    if mesh.has_custom_normals:
        mesh.normals_split_custom_set([(0.0, 0.0, 0.0)] * len(mesh.loops))  # zero keeps Blender's own normal
    return True


def crease_shading(mesh, degrees=CREASE_DEGREES, flat=()):
    """Shading normals that never lean past the crease angle from their own face, on a mesh shaded smooth by angle.

    0. The normals the GLB brought (a glTF import keeps them as custom normals) are dropped. Tripo writes one smooth
       normal a vertex, averaged across hard corners, and the weld averaged them further: on a Smart Mesh tank, factory
       and landmark 75 to 82 % of the exported surface had a corner leaning past 45 degrees from its face.
    1. An edge is sharp where its faces meet at more than `degrees`, and wherever smoothing across it is not defined:
       an edge with one face or more than two, or one of whose faces has no area.
    2. A face with a corner whose normal still leans more than `degrees` from the face (a smooth fan that wraps round a
       tip or a fold, mixing faces that point apart) is shaded flat: its edges are sharp and its corners take its
       normal. So are the `flat` polygons (indices).
    A reviewer saw such leaning corners as smeared streaks and an X across a plain wall (the Smart Mesh factory's annex)
    and as a cone on a flat lid (a tank's empty turret ring). Returns what was found and changed."""

    limit = math.cos(math.radians(degrees))
    # the GLB's own normals (Tripo writes one smooth normal a vertex, averaged across hard corners) go first
    imported_leaning = int(sum(_corner_leans(mesh, limit))) if mesh.has_custom_normals else 0
    imported = _clear_custom_normals(mesh)
    polygons = mesh.polygons
    tiny = 1e-12 * max(1.0, max((p.area for p in polygons), default=1.0))
    faces_of = {}
    for p in polygons:
        for key in p.edge_keys:
            faces_of.setdefault(key, []).append(p.index)
    sharp = set()
    for key, faces in faces_of.items():
        if len(faces) != 2 or any(polygons[f].area <= tiny for f in faces) or polygons[faces[0]].normal.dot(polygons[faces[1]].normal) < limit:
            sharp.add(key)
    for edge in mesh.edges:
        edge.use_edge_sharp = tuple(sorted(edge.vertices)) in sharp
    mesh.update()
    leaning = _corner_leans(mesh, limit)
    flat_faces = set(int(i) for i in flat) | {i for i, lean in enumerate(leaning) if lean}
    keys = {key for i in flat_faces for key in polygons[i].edge_keys}
    for edge in mesh.edges:
        if tuple(sorted(edge.vertices)) in keys:
            edge.use_edge_sharp = True
    mesh.update()
    corner = [c.vector.copy() for c in mesh.corner_normals]
    for i in flat_faces:
        for loop in polygons[i].loop_indices:
            corner[loop] = polygons[i].normal.copy()
    mesh.normals_split_custom_set(corner)
    after = _corner_leans(mesh, limit)
    return {"crease_degrees": degrees, "imported_normals_cleared": imported, "faces_leaning_imported": imported_leaning,
            "sharp_edges": sum(1 for e in mesh.edges if e.use_edge_sharp), "faces_leaning": int(sum(leaning)),
            "faces_shaded_flat": len(flat_faces), "faces_leaning_after": int(sum(after))}


def card_cost(bm, size):
    """The triangles thickening the cards will add (each sheet's triangles again, two a rim edge), for the budget."""

    points, triangles = bm_arrays(bm)
    cost = 0
    for card in sk.flat_cards(points, triangles, size):
        chosen = triangles[card["triangles"]]
        rim = sum(1 for faces in sk._edge_faces(chosen).values() if len(faces) == 1)
        cost += len(chosen) + 2 * rim
    return cost
