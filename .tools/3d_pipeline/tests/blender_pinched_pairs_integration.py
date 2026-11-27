"""Blender-side test: vertex pairs the topology gate's weld would pinch are moved apart, seam copies are left (separate_pinched_pairs).

Run with the lock-selected Blender:
    blender --background --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_pinched_pairs_integration.py
`test_pinched_pairs_regression.py` runs it when a Blender is installed. It creates no files.

A Tripo knight's belt pouch met his brigandine at vertices a float's noise apart. Welded as the gate welds, they put a third face on an
edge of the brigandine. Here a fan of two triangles shares the edge v0 to v1. A pouch triangle near that edge pinches it once welded:
one pouch shares v1 exactly and sits a noise from v0, another sits a noise from both ends, so only the two pairs merged together pinch.
A seam copy (a vertex split from its neighbour across a UV seam, a noise apart) closes the surface when welded and must stay.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bpy

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT / "adapter"))

import blender_worker

GATE = 1e-6
NOISE = 2e-7


def build(name: str, vertices, faces) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def fan():
    # v0, v1 the shared edge, v2 and v3 the fan's far corners
    return [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.5, 1.0, 0.0), (0.5, -1.0, 0.0)], [(0, 1, 2), (1, 0, 3)]


def check(name: str, extra_vertices, extra_faces, expected: int) -> None:
    vertices, faces = fan()
    base = len(vertices)
    obj = build(name, vertices + extra_vertices, faces + [tuple(base + i for i in face) for face in extra_faces])
    before = [vertex.co.copy() for vertex in obj.data.vertices]
    moved = blender_worker.separate_pinched_pairs(obj, GATE)
    assert moved == expected, f"{name}: moved {moved} pair(s), expected {expected}"
    shifts = [(vertex.co - old).length for vertex, old in zip(obj.data.vertices, before)]
    assert max(shifts) < 5 * GATE, f"{name}: a vertex moved {max(shifts)}, more than a few millionths"
    if expected:
        assert blender_worker._pinched_after_weld(obj.data, _close_pairs(obj)) == 0, f"{name}: still pinched after the move"
    print(f"{name}: moved {moved}, largest shift {max(shifts):.2e}")


def _close_pairs(obj):
    vertices = obj.data.vertices
    return {(a.index, b.index) for a in vertices for b in vertices if a.index < b.index and (a.co - b.co).length <= GATE}


def main() -> None:
    # one pouch vertex a noise from v0, its other edge end v1 shared exactly through a vertex of its own at the same place as v1 plus noise 0
    check("one_pair", [(NOISE, 0.0, 0.0), (1.0, 0.0, 0.0), (0.5, 0.0, 1.0)], [(0, 1, 2)], expected=2)
    # both ends a noise off: only the two pairs welded together put a third face on v0 to v1
    check("two_pairs_together", [(NOISE, 0.0, 0.0), (1.0 - NOISE, 0.0, 0.0), (0.5, 0.0, 1.0)], [(0, 1, 2)], expected=2)
    # a seam copy: the fan's v2 split off with its own triangle beyond the fan, welding closes the surface and pinches nothing
    check("seam_copy", [(0.5, 1.0 + NOISE, 0.0), (1.0, 0.0, 0.0), (0.5, 2.0, 0.0)], [(1, 0, 2)], expected=0)
    print("PINCHED_PAIRS_INTEGRATION_OK")


main()
