"""Blender-side test: provider meshes split at UV seams are wound as one surface.

Run with the lock-selected Blender:
    blender --background --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_winding_integration.py
`test_winding_regression.py` runs it when a Blender is installed. It creates no files.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT / "adapter"))

import blender_worker

CORNERS = [Vector((x, y, z)) for x in (-1.0, 1.0) for y in (-0.05, 0.05) for z in (0.0, 2.0)]
# A thin card (a fur or leaf card with thickness): six quads, each its own UV island.
QUADS = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
INWARD = {1, 3, 4}  # these islands arrive wound inward


def split_card() -> bmesh.types.BMesh:
    bm = bmesh.new()
    for index, quad in enumerate(QUADS):
        verts = [bm.verts.new(CORNERS[corner]) for corner in quad]  # no shared vertices: split at every seam
        bm.faces.new(list(reversed(verts)) if index in INWARD else verts)
    bm.normal_update()
    return bm


CENTRE = sum(CORNERS, Vector()) / len(CORNERS)


def outward(face: bmesh.types.BMFace) -> bool:
    return face.normal.dot(face.calc_center_median() - CENTRE) > 0


def main() -> None:
    bm = split_card()
    assert sum(not outward(face) for face in bm.faces) == len(INWARD), "fixture: the inward islands are inward"
    vertices = len(bm.verts)
    flips = blender_worker.wind_like_welded_copy(bm)
    bm.normal_update()
    assert flips == len(INWARD), f"expected {len(INWARD)} flips, got {flips}"
    assert all(outward(face) for face in bm.faces), "every island faces outward after winding on the welded copy"
    assert len(bm.verts) == vertices, "the split seams stay split"
    assert not bm.faces.layers.int.get("hoi4_winding_face"), "the helper removes its face marker"

    # The full step on a scene object: triangulated, wound outward, flips reported.
    mesh = bpy.data.meshes.new("card")
    split_card().to_mesh(mesh)
    obj = bpy.data.objects.new("card", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj["hoi4_working"] = True
    result = blender_worker.triangulate_and_normals()
    assert result["faces_flipped"].get("card", 0) >= len(INWARD), result
    check = bmesh.new()
    check.from_mesh(obj.data)
    check.normal_update()
    assert len(check.faces) == 12 and all(outward(face) for face in check.faces), "triangulated card faces outward"
    print("WINDING_INTEGRATION_OK")


main()
