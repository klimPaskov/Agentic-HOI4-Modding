"""Surface cleanup of the static-model route, on a bmesh in Blender (`tripo/static_model_blender.py` uses them).

- `remove_slivers`: needle slivers and tiny loose open flakes (`lib.static_kinds.needle_triangles`, `loose_flakes`) go.
- `thicken_cards`: flat one-sided cards (`lib.static_kinds.flat_cards`) are solidified, centred on the sheet, as thick as
  `lib.static_kinds.card_thickness` allows, and marked in the deform layer's group `CARD_GROUP`.
- `card_cost`: the triangles `thicken_cards` will add, for the triangle budget.

`size` is the model's size (its largest side). The rules themselves are in `lib/static_kinds.py`, where the tests reach them.
"""

from __future__ import annotations

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


def card_cost(bm, size):
    """The triangles thickening the cards will add (each sheet's triangles again, two a rim edge), for the budget."""

    points, triangles = bm_arrays(bm)
    cost = 0
    for card in sk.flat_cards(points, triangles, size):
        chosen = triangles[card["triangles"]]
        rim = sum(1 for faces in sk._edge_faces(chosen).values() if len(faces) == 1)
        cost += len(chosen) + 2 * rim
    return cost
