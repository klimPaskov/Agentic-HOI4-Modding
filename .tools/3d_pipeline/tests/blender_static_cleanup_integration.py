"""Blender-side test of the static route's surface cleanup (tripo/static_mesh_ops.py) on a procedural model.

Run with the lock-selected Blender:
    blender --background --factory-startup --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_static_cleanup_integration.py
The model is a closed hull box with a closed thin barrel, an open wedge flake on its deck, a needle sliver hanging off an
open plate, and a flat one-sided disc card beside it. It fails on the first unmet expectation.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from tripo.static_mesh_ops import CARD_GROUP, bm_arrays, card_cost, remove_slivers, thicken_cards

from lib import static_kinds as sk


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"STATIC_CLEANUP_INTEGRATION_FAILED: {message}")


def build() -> bmesh.types.BMesh:
    bm = bmesh.new()
    bm.loops.layers.uv.new("UVMap")
    bmesh.ops.create_cube(bm, size=1.0)  # the hull: -0.5 to 0.5
    # a closed thin barrel
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.02, radius2=0.02, depth=1.0,
                          matrix=Matrix.Translation((0.0, -1.0, 0.3)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    # an open wedge flake on the deck (two side plates and the sloped strip)
    o = (0.1, 0.1, 0.5)
    v = [bm.verts.new(c) for c in [o, (o[0], o[1] + 0.04, o[2]), (o[0], o[1], o[2] + 0.04),
                                   (o[0] + 0.005, o[1], o[2]), (o[0] + 0.005, o[1] + 0.04, o[2]), (o[0] + 0.005, o[1], o[2] + 0.04)]]
    for a, b, c in [(0, 1, 2), (3, 5, 4), (1, 4, 5), (1, 5, 2)]:
        bm.faces.new((v[a], v[b], v[c]))
    # an open plate with a needle sliver hanging off its edge
    plate = [bm.verts.new(c) for c in [(1.0, 0.0, 0.0), (1.5, 0.0, 0.0), (1.5, 0.5, 0.0), (1.0, 0.5, 0.0)]]
    bm.faces.new((plate[0], plate[1], plate[2]))
    bm.faces.new((plate[0], plate[2], plate[3]))
    near = bm.verts.new((1.01, 0.0, 0.0))
    tip = bm.verts.new((1.0, -0.6, 0.3))
    bm.faces.new((near, plate[0], tip))
    # a flat one-sided card: a fan disc facing x, a little off the hull's side
    centre = bm.verts.new((-0.6, 0.0, 0.0))
    ring = [bm.verts.new((-0.6, 0.3 * math.cos(a), 0.3 * math.sin(a))) for a in [k * math.tau / 12 for k in range(12)]]
    for k in range(12):
        bm.faces.new((centre, ring[k], ring[(k + 1) % 12]))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    return bm


def main() -> None:
    bm = build()
    size = 2.6
    points, triangles = bm_arrays(bm)
    before = len(triangles)
    sliver = remove_slivers(bm, size)
    expect(sliver["needles_removed"] == 1, f"one needle removed, got {sliver}")
    expect(sliver["flakes_removed"] == 1 and sliver["flake_triangles"] == 4, f"the wedge flake removed, got {sliver}")
    expect(sliver["triangles_after"] == before - 5, f"only the needle and the flake go, got {sliver}")
    points, triangles = bm_arrays(bm)
    expect(sum(1 for p in points if abs(p[0]) < 0.03 and abs(p[2] - 0.3) < 0.03 and p[1] < -0.45) >= 16, "the closed barrel stays")
    cost = card_cost(bm, size)
    expect(cost > 0, "the card costs triangles")
    cards = thicken_cards(bm, size)
    expect(cards["thickened"] >= 1, f"the disc card is thickened, got {cards}")
    points, triangles = bm_arrays(bm)
    card = [p for p in points if abs(p[0] + 0.6) < 0.05]
    expect(len(card) > 13, "the card got a second layer")
    xs = sorted(p[0] for p in card)
    thickness = xs[-1] - xs[0]
    expect(abs(thickness - min(sk.CARD_THICKNESS_SHARE * size, sk.CARD_SIDE_SHARE * 0.6)) < 1e-4, f"the card is the rule's thickness, got {thickness}")
    expect(abs((xs[-1] + xs[0]) / 2 + 0.6) < 1e-5, "the thickness is centred on the sheet")
    open_card = [e for e in bm.edges if e.is_boundary and all(abs(v.co.x + 0.6) < 0.05 for v in e.verts)]
    expect(not open_card, f"the card has no open edge left, got {len(open_card)}")
    deform = bm.verts.layers.deform.active
    marked = [v for v in bm.verts if deform is not None and v[deform].get(CARD_GROUP, 0.0) > 0.5]
    on_disc = [v for v in marked if abs(v.co.x + 0.6) < 0.05]
    expect(len(on_disc) == len(card), f"every disc vertex is marked for the reduction, got {len(on_disc)} of {len(card)}")
    expect(all(abs(v.co.x + 0.6) < 0.05 or v.co.x > 0.9 for v in marked), "only card vertices (the disc, the open plate) are marked")
    mesh = bpy.data.meshes.new("cleanup")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("cleanup", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.vertex_groups.new(name="thickened_cards")
    weighted = sum(1 for v in mesh.vertices for g in v.groups if g.group == CARD_GROUP and g.weight > 0.5)
    expect(weighted == len(marked), "the marks reach the mesh's vertex group")
    print("STATIC_CLEANUP_INTEGRATION_OK", sliver, cards["thickened"], round(thickness, 4))


main()
