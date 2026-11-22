"""Blender stage of the static-model route: one Tripo GLB to a HOI4 `.mesh` and its role `.anim` files.

Run by `tripo/static_model.py`, never by hand::

    blender -b --factory-startup --python static_model_blender.py -- <request.json>

The request carries the kind's contract (`config/static_kinds.json`), the vanilla role clips as each bone's
motion relative to its parent (`lib.static_kinds.local_motion`), and where to write. In order:

1. Imports the GLB, joins its meshes, turns it so the front faces -y (`facing_quarter_turns`, or the job's `front`)
   and gives it vanilla's size and place (`placement`). A ship's hull is cut at vanilla's draft below the waterline
   and the cut is closed.
2. Welds by position and collapse-decimates to the kind's triangle budget, checking the silhouettes (`lib.tripo_shape`).
3. Cuts the rigid parts on planes found by rule (`turret_cut`, `barrel_cut`, `propeller_cut`), splits them apart and
   closes each cut with a cap that takes its colours from the faces around it, so a turning turret shows no hole. The
   caps on a tank's turret cut (the ring on the hull, the turret's underside) are flat and take the atlas's darkest
   patch (`hole_uv` from static_model.py), so the ring reads as a hole when the death blows the turret off.
4. Builds the kind's skeleton (vanilla's bone names; rest places from the parts or from vanilla's shares of the box),
   binds each part rigidly to its bone, adds the `Collision` box and the locators, and gives every rendered shape the
   kind's PDX material. The shading is smooth only across faces within `CREASE_DEGREES` of each other, and no corner
   leans further from its own face (`static_mesh_ops.crease_shading`).
5. Keys each role: vanilla's motion about the model's own pivots, displacements scaled by size, plus the turn of a
   tank's turret before the shot and a propeller's spin; exports each at 30 frames a second and the mesh.

It prints `STATIC_MODEL_DONE` and writes the report the request names.
"""

from __future__ import annotations

import importlib
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import addon_utils
import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import static_kinds as sk
from lib import static_parts
from lib import static_slab
from lib import tripo_shape
from tripo.static_mesh_ops import CARD_GROUP, CREASE_DEGREES, card_cost, crease_shading, double_inside_out_walls, hull_crumpled_pieces, remove_slivers, snap_to_source, thicken_cards

request = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
# Faces within this angle of each other count as one flat plate in the first reduction step (kit rule: a degree or two
# of a generated plate's waviness, well under the 40-degree crease the shading keeps sharp).
PLANAR_DEGREES = 3.0
SMALL_HOLE_EDGES = 32
SLIT_SHARE = 1e-3
CUT_CLEARANCE = 5e-4
HULL_LEVEL = "hull_level"  # a face attribute marking the faces of hull roof the turret cut only clipped (they stay on the hull)
RING_CAP = "ring_cap"  # a face attribute marking the caps on a tank's turret cut until they are shaded
contract = request["contract"]
kind = contract["kind"]
name = request["name"]
out = Path(request["out"])
report: dict = {"kind": kind, "name": name}

for module in addon_utils.modules():
    if module.__name__.endswith("io_pdx_mesh"):
        addon_utils.enable(module.__name__, default_set=False)
        bie = importlib.import_module(module.__name__ + ".pdx_blender.blender_import_export")
        break
else:
    raise SystemExit("io_pdx_mesh is not installed for this Blender; run bootstrap_3d_workflow.py")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def arrays(obj):
    return mesh_arrays(obj.data)


def mesh_arrays(mesh):
    mesh.calc_loop_triangles()
    positions = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", positions)
    triangles = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", triangles)
    return positions.reshape(-1, 3), triangles.reshape(-1, 3)


def triangle_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def _island(start, seen):
    """The faces edge-connected to `start` that `seen` does not hold yet (they are added to it)."""

    island, stack = [], [start]
    seen.add(start)
    while stack:
        face = stack.pop()
        island.append(face)
        for edge in face.edges:
            for other in edge.link_faces:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
    return island


def _conflicts(faces):
    """Edges of `faces` whose two faces walk them the same way (one of the two faces is turned)."""

    edges = {e for f in faces for e in f.edges}
    return sum(1 for e in edges if len(e.link_loops) == 2 and e.link_loops[0].vert == e.link_loops[1].vert)


def _recalc_if_better(bm, island):
    """Blender's recalc on a piece, kept only when it leaves fewer conflicted edges: on a piece with edges shared by
    three faces it can turn more faces wrong than it mends (the Smart Mesh monument's base went from 17 to 123)."""

    before = _conflicts(island)
    facing = {f: f.normal.copy() for f in island}
    bmesh.ops.recalc_face_normals(bm, faces=island)
    bm.normal_update()
    if _conflicts(island) < before:
        _turn_lone_faces(bm, island)  # the recalc can leave a face or two at odds with its neighbours (a factory's 3)
        return True
    turned = [f for f in island if f.normal.dot(facing[f]) < 0]
    bmesh.ops.reverse_faces(bm, faces=turned)
    bm.normal_update()
    _turn_lone_faces(bm, island)
    return False


def _turn_lone_faces(bm, island, rounds=8):
    """Turn the faces at odds with most of their neighbours (two or more of their edges conflicted), a round at a
    time, while each round leaves fewer conflicted edges."""

    for _ in range(rounds):
        before = _conflicts(island)
        odd = [f for f in island if sum(1 for e in f.edges if len(e.link_loops) == 2 and e.link_loops[0].vert == e.link_loops[1].vert) >= 2]
        if not odd:
            return
        bmesh.ops.reverse_faces(bm, faces=odd)
        if _conflicts(island) >= before:
            bmesh.ops.reverse_faces(bm, faces=odd)
            return
    bm.normal_update()


def _drop_doubled_faces(bm):
    bm.verts.index_update()
    doubles, seen_faces = [], {}
    for face in bm.faces:
        key = tuple(sorted(v.index for v in face.verts))
        other = seen_faces.get(key)
        if other is not None and other.normal.dot(face.normal) > 0.99:
            doubles.append(face)
        else:
            seen_faces[key] = face
    if doubles:
        bmesh.ops.delete(bm, geom=doubles, context="FACES_ONLY")
    return len(doubles)


def _turn_inside_out_pieces(bm):
    turned, done = 0, set()
    for start in list(bm.faces):
        if start in done:
            continue
        island = _island(start, done)
        if not all(len(e.link_faces) == 2 for f in island for e in f.edges):
            continue
        volume = sum(f.verts[0].co.dot(f.verts[1].co.cross(f.verts[2].co)) for f in island if len(f.verts) == 3)
        if volume < 0:
            bmesh.ops.reverse_faces(bm, faces=island)
            turned += 1
    return turned


def consistent_winding(bm):
    """Winding: a piece with an edge its two faces walk the same way (a face turned against its neighbours, which the
    game culls) is turned consistent with Blender's recalc; only such pieces are touched (a Smart Mesh plane's wings had
    them). A face lying exactly on another one, facing the same way (a doubled face that flickers), is dropped, and a
    closed piece whose faces all point inward (UNIT-INSIDE-OUT) is turned outward. It runs after the weld and again
    after the slits and small holes are closed, because joining a slit can bring two pieces of opposite winding together
    (a Smart Mesh factory's roof gables)."""

    doubles = _drop_doubled_faces(bm)
    conflicted = [e for e in bm.edges if len(e.link_loops) == 2 and e.link_loops[0].vert == e.link_loops[1].vert]
    fixed, kept, seen = 0, 0, set()
    for edge in conflicted:
        if edge.link_faces[0] in seen:
            continue
        island = _island(edge.link_faces[0], seen)
        if _recalc_if_better(bm, island):
            fixed += len(island)
        else:
            kept += 1
    return {"conflicted_edges": len(conflicted), "faces_reoriented_in_pieces": fixed, "pieces_kept_as_they_were": kept,
            "conflicted_after": _conflicts(bm.faces), "doubled_faces_dropped": doubles, "inside_out_pieces_turned": _turn_inside_out_pieces(bm)}


def scrolling_tracks(track_vertices, rule):
    """The track runs as vanilla draws them: their own material with vanilla's scrolling shader on a tread texture
    (`<name>_tracks_*.dds`, written by static_model.py from the run's own colour), and UVs whose v runs along the hull at
    vanilla's density, so the entity's texture_anim_speed scrolls the tread along the run. The atlas UVs the runs had
    are reported, so the tread takes their colour."""

    mesh = model.data
    track_material = bie.create_shader(SimpleNamespace(shader=[rule["shader"]], diff=[f"{name}_tracks_diffuse.dds"], n=[f"{name}_tracks_normal.dds"],
                                                       spec=[f"{name}_tracks_specular.dds"]), f"PDXmat_{name}Tracks", str(out))
    # the tread files are written after Blender (static_model.py), so io_pdx_mesh made named placeholders with no path, and
    # the exporter writes a texture's path: give each its file name, or the mesh's material names an empty file
    for node in track_material.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image is not None and not node.image.filepath:
            node.image.filepath = str(Path(out) / node.image.name)
    mesh.materials.append(track_material)
    slot = len(mesh.materials) - 1
    members_set = set(int(i) for i in track_vertices)
    faces = [p for p in mesh.polygons if all(v in members_set for v in p.vertices)]
    uv = mesh.uv_layers.active.data
    atlas = [tuple(uv[i].uv) for p in faces for i in p.loop_indices]
    report["track_atlas_uvs"] = [[round(a, 4), round(b, 4)] for a, b in atlas[:: max(1, len(atlas) // 2000)]]
    order = sorted(members_set)
    where = {v: k for k, v in enumerate(order)}
    points = np.array([mesh.vertices[v].co[:] for v in order])
    corners = sk.track_face_uvs(points, [[where[mesh.loops[i].vertex_index] for i in p.loop_indices] for p in faces],
                                rule["v_per_measure"] / measure, rule["v_sign"])
    for polygon, face_uvs in zip(faces, corners):
        polygon.material_index = slot
        for loop_index, (u, v) in zip(polygon.loop_indices, face_uvs):
            uv[loop_index].uv = (float(u), 1.0 - float(v))  # io_pdx_mesh writes v as 1 - the Blender v
    v_all = np.concatenate([c[:, 1] for c in corners]) if corners else np.zeros(1)
    report["tracks"] = {"faces": len(faces), "material_index": slot, "v_span": round(float(np.ptp(v_all)), 3), "v_round_the_loop": True}


# ---- 1. import, join, face front, size and place ----
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=request["glb"])
imported = [o for o in bpy.data.objects if o not in before]
meshes = [o for o in imported if o.type == "MESH" and len(o.data.polygons)]
if not meshes:
    raise SystemExit(f"{request['glb']} has no mesh")
for obj in meshes:
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = world
    for modifier in list(obj.modifiers):
        obj.modifiers.remove(modifier)
    obj.vertex_groups.clear()
for obj in imported:
    if obj not in meshes:
        bpy.data.objects.remove(obj, do_unlink=True)
# A model made in parts (Tripo's Generate in Parts) has one mesh a part. Each face keeps its part (static_parts.PART_LAYER,
# counted from 1), so the parts are welded and reduced on their own and a tank's part goes whole onto its bone.
source_parts = [obj.name for obj in meshes] if request.get("parts", "auto") is not False and len(meshes) > 1 else []
for k, obj in enumerate(meshes if source_parts else []):
    layer = obj.data.attributes.new(static_parts.PART_LAYER, "INT", "FACE")
    layer.data.foreach_set("value", [k + 1] * len(obj.data.polygons))
bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
model = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
model.name = name
model.data.name = f"{name}Shape"
report["source_triangles"] = triangle_count(model)

positions, triangles = arrays(model)
samples = sk.surface_samples(positions, triangles)
turns = sk.FRONT_TURNS[request["front"]] if request.get("front") else sk.facing_quarter_turns(samples, kind, contract.get("rules", {}).get("turret"))
model.data.transform(Matrix.Rotation(turns * math.pi / 2, 4, "Z"))
samples = sk.rotate_quarter_turns(samples, turns)
scale, offset = sk.placement(samples, kind, contract)
model.data.transform(Matrix.Translation(Vector(offset)) @ Matrix.Scale(scale, 4))
report["placement"] = {"quarter_turns": turns, "front_from_job": bool(request.get("front")), "scale": round(scale, 6), "offset": [round(float(v), 4) for v in offset]}

measure = contract["size"]["source"]
draft = contract["waterline"]["draft_share"] * measure if kind == "ship" else 0.0
# A hull is cut at vanilla's draft only when its keel goes deeper by more than 1 % of the length: a cut along the keel
# itself leaves slivers and nothing a player sees.
if kind == "ship" and float(arrays(model)[0][:, 2].min()) < -draft - 0.01 * measure:
    bm = bmesh.new()
    bm.from_mesh(model.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -draft), plane_no=(0, 0, 1), clear_inner=True)
    rim = [e for e in bm.edges if e.is_boundary and all(abs(v.co.z + draft) < 1e-4 * measure for v in e.verts)]
    filled = bmesh.ops.holes_fill(bm, edges=rim, sides=0)
    bm.to_mesh(model.data)
    bm.free()
    report["hull_cut"] = {"draft": round(draft, 4), "rim_edges": len(rim), "cap_faces": len(filled["faces"])}

# ---- 2. weld and decimate to vanilla's budget ----
original = arrays(model)
# The cut planes are found on the full model, before the reduction thins its small parts (a barrel, a blade).
cut_samples = sk.surface_samples(*original)
bm = bmesh.new()
bm.from_mesh(model.data)
size = float(np.ptp(original[0], axis=0).max())
welded = len(bm.verts)


def part_verts(bm):
    """The vertices of each source part (one group of every vertex for a model not in parts)."""

    layer = bm.faces.layers.int.get(static_parts.PART_LAYER)
    if layer is None:
        return [list(bm.verts)]
    groups = {}
    for face in bm.faces:
        if face[layer]:
            groups.setdefault(face[layer], set()).update(face.verts)
    return [list(group) for group in groups.values()]


for group in part_verts(bm):  # parts that only touch stay apart
    bmesh.ops.remove_doubles(bm, verts=group, dist=size * 1e-5)
welded -= len(bm.verts)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
report["winding"] = consistent_winding(bm)
# Needle slivers and loose open flakes go before anything is judged or reduced, and the triangles the flat cards will
# take when thickened (after the holes are closed, below) are kept back from the reduction's target.
report["slivers"] = remove_slivers(bm, size)
cards_cost = card_cost(bm, size)
bm.to_mesh(model.data)
bm.free()
# the welded, unreduced mesh, for moving the reduction's stray vertices back onto its surface (snap_to_source below)
source_mesh = model.data.copy()
budget = contract["triangle_budget"]["value"]
# The cuts and caps add triangles, so the mesh is reduced to 94 % of the budget first, less what the cards will add.
target = int(budget * 0.94) - cards_cost
current = triangle_count(model)
planar = None
part_iou = float(request.get("part_shape_iou") or tripo_shape.MIN_IOU)


def planar_then_collapse(obj, wanted):
    """First merge the faces that lie flat together (within PLANAR_DEGREES), keeping UV island borders, then collapse
    what is left to `wanted` triangles. Collapsing a generated hard-surface mesh straight to a vanilla budget crumples
    flat plates into folds and smears the texture across them; flat plates cost almost nothing once merged. Returns the
    count after the planar step."""

    bpy.context.view_layer.objects.active = obj
    decimate = obj.modifiers.new("planar", "DECIMATE")
    decimate.decimate_type = "DISSOLVE"
    decimate.angle_limit = math.radians(PLANAR_DEGREES)
    decimate.delimit = {"UV"}
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    after = triangle_count(obj)
    if after > wanted:
        decimate = obj.modifiers.new("decimate", "DECIMATE")
        decimate.decimate_type = "COLLAPSE"
        decimate.ratio = wanted / after
        decimate.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=decimate.name)
    return after


def reduce_in_parts(wanted):
    """Each source part reduced on its own to its share of `wanted` (lib/static_parts.reduce_parts), the shares by need and
    every part's shape checked as the unit route checks a reduced part; the parts are joined back into the model."""

    sources = []
    for k in range(len(source_parts)):
        mesh = model.data.copy()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        layer = bm.faces.layers.int.get(static_parts.PART_LAYER)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[layer] != k + 1], context="FACES")
        bm.to_mesh(mesh)
        bm.free()
        sources.append(mesh)
    objects = []
    for k, mesh in enumerate(sources):
        obj = bpy.data.objects.new(f"{name}_part_{k + 1}", mesh.copy())
        scene.collection.objects.link(obj)
        objects.append(obj)

    def reduce(k, triangles):
        obj = objects[k]
        old = obj.data
        obj.data = sources[k].copy()
        bpy.data.meshes.remove(old)
        if triangles < triangle_count(obj):
            planar_then_collapse(obj, triangles)
        return arrays(obj)

    try:
        receipt = static_parts.reduce_parts(source_parts, [mesh_arrays(m) for m in sources], wanted, reduce, part_iou)
    except static_parts.PartsBudgetError as problem:
        raise SystemExit(f"STATIC-PARTS: {problem}") from None
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    old = model.data
    model.data = objects[0].data
    bpy.data.objects.remove(objects[0], do_unlink=True)
    bpy.data.meshes.remove(old)
    for mesh in sources:
        bpy.data.meshes.remove(mesh)
    model.data.name = f"{name}Shape"
    return receipt


parts_receipt = None
if source_parts and current > target:
    parts_receipt = reduce_in_parts(target)
elif current > target:
    planar = planar_then_collapse(model, target)
if current > target:
    bm = bmesh.new()
    bm.from_mesh(model.data)
    report["snap"] = snap_to_source(bm, source_mesh, size, static_parts.PART_LAYER)
    bm.to_mesh(model.data)
    bm.free()
bpy.data.meshes.remove(source_mesh)
# STATIC-SHAPE judges the reduction alone, before the holes below are closed: a cap over an opening adds to the outline
# by design (the Smart Mesh monument's base had wedge openings through it, and their caps read as a 0.91 top outline)
shape = tripo_shape.shape_report(original, arrays(model))
reduced_to = triangle_count(model)
# Parts that only touched come apart in their own reductions, so a model in parts is judged whole by its silhouettes alone
# (each part's shells and closure were checked on their own).
shape_problems = static_parts.silhouette_problems(shape) if parts_receipt else tripo_shape.shape_problems(shape)
# Small open loops a reviewer sees as specks of the background (the kit closes loops up to 32 edges without a seam,
# check_unit_files.SMALL_HOLE_EDGES); larger ones stay for UNIT-HOLE to report.
bm = bmesh.new()
bm.from_mesh(model.data)
# Slits first: open-edge vertices within a thousandth of the model's size of each other are one point. A reviewer saw
# such a crack on the ship's deck as a cyan rim; the weld tolerance above (a hundred-thousandth) leaves it open.
slits = len(bm.verts)
for group in part_verts(bm):
    rim_verts = [v for v in group if any(e.is_boundary for e in v.link_edges)]
    bmesh.ops.remove_doubles(bm, verts=rim_verts, dist=size * SLIT_SHARE)
slits -= len(bm.verts)
report["slit_vertices_merged"] = slits
closed = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=SMALL_HOLE_EDGES)["faces"]
# An open rim of any size lying flat at the model's lowest height (a paved disc or a plinth with no underside) is
# closed too: seen from below it was a missing floor, and the cap sits on the ground where nothing is lost.
if kind in ("building", "landmark"):
    floor = min(v.co.z for v in bm.verts)
    reach = 0.01 * (max(v.co.z for v in bm.verts) - floor)
    rim = [e for e in bm.edges if e.is_boundary and all(v.co.z <= floor + reach for v in e.verts)]
    bottoms = bmesh.ops.holes_fill(bm, edges=rim, sides=0)["faces"] if rim else []
    closed = list(closed) + list(bottoms)
    report["ground_rims_closed"] = len(bottoms)
# like a cut's cap, a closed hole is one flat colour: the rim's UVs copied across it swirl the texture (a reviewer saw
# the Smart Mesh factory's window bays as pinched spirals)
uv_layer = bm.loops.layers.uv.active
if uv_layer is not None:
    for face in closed:
        first = face.loops[0][uv_layer].uv.copy()
        for loop in face.loops:
            loop[uv_layer].uv = first
bmesh.ops.triangulate(bm, faces=closed)
report["winding_after_holes"] = consistent_winding(bm)
# Flat one-sided cards get a thickness, then their winding is made consistent like any piece (a closed shell facing
# inward is turned out).
model.vertex_groups.clear()
model.vertex_groups.new(name="thickened_cards")  # index CARD_GROUP of the deform layer thicken_cards writes
assert model.vertex_groups["thickened_cards"].index == CARD_GROUP
report["cards"] = thicken_cards(bm, size)
report["cards"]["triangles_kept_back"] = cards_cost
report["winding_after_cards"] = consistent_winding(bm)
# A tank's small fittings that the reduction crumpled into lumps become their convex hull (static_mesh_ops.hull_crumpled_pieces).
# A model under its target was not reduced, so nothing was crumpled: its fittings stay as made. On the M2A4 Smart Mesh tank
# (6,257 triangles, target 7,095) the hulls turned 35 clean fittings (vision flaps, hinges) into jumbled blocks and left
# 29 edges between faces facing opposite ways (UNIT-WINDING).
if kind == "vehicle" and current > target:
    report["crumpled_pieces"] = hull_crumpled_pieces(bm, contract["rules"].get("wheels"))
    report["winding_after_hulls"] = consistent_winding(bm)
elif kind == "vehicle":
    report["crumpled_pieces"] = {"skipped": "not reduced", "triangles": current, "target": target}
if kind == "vehicle":
    # A wall that faces into the hull (nothing behind its back) shows the inside through it from outside: it gets a reversed copy
    report["inside_out_walls"] = double_inside_out_walls(bm)
bm.to_mesh(model.data)
bm.free()
report["small_holes_closed"] = len(closed)
report["reduction"] = {"welded_vertices": welded, "from": len(original[1]), "after_planar": planar, "to": reduced_to, "budget": budget,
                       "iou": shape["iou"], "shells_before": shape["shells_before"]["shells"], "shells_after": shape["shells_after"]["shells"],
                       "problems": shape_problems}
if parts_receipt:
    report["reduction"]["parts"] = parts_receipt
elif source_parts:
    report["reduction"]["parts"] = {"within_target": True, "parts": source_parts}

# ---- 3. rigid parts ----
positions, triangles = arrays(model)
samples = cut_samples
low, high = positions.min(axis=0), positions.max(axis=0)
parts_report = {}
pivots = {}
cuts = []  # (plane point, plane normal) of each cut, for the caps

bm = bmesh.new()
bm.from_mesh(model.data)


def bisect(faces, co, no):
    geom = list({e for f in faces for e in f.edges}) + list({v for f in faces for v in f.verts}) + list(faces)
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, dist=1e-6 * size)
    cuts.append((Vector(co), Vector(no)))


def centre(face):
    return face.calc_center_median()


hull_layer = bm.faces.layers.int.new(HULL_LEVEL) if kind == "vehicle" else None  # (before the cuts: a new layer removes the face references)
part_layer = bm.faces.layers.int.get(static_parts.PART_LAYER)
whole_region = {}  # a source part that lies wholly on one side of the cuts -> the rigid part it goes to whole


def whole_sides(faces, side):
    """static_parts.whole_parts on these faces: {part id: True when the part lies wholly on the side `side` marks}."""

    if part_layer is None or not faces:
        return {}
    return static_parts.whole_parts(np.array([f[part_layer] for f in faces]), np.array([f.calc_area() for f in faces]),
                                    np.array([bool(side(f)) for f in faces]))


def uncut(faces, decided):
    return [f for f in faces if part_layer is None or f[part_layer] not in decided]
if kind == "vehicle":
    turret = sk.turret_cut(samples, contract["rules"]["turret"])
    barrel = sk.barrel_cut(samples, turret["cut_z"], contract["rules"]["barrel"])
    # The collar: a Smart Mesh's sunk ring leaves a faceted skirt of small faces standing a hair out of the roof round the
    # turret's base, which the turret covers. Uncovered (the turret gone, or the light low) it shows as a bright thin ring.
    # Its faces (small, sloping, in the ring's band) are snapped down into the roof plane.
    above = samples[(samples[:, 2] >= turret["cut_z"]) & (samples[:, 1] >= barrel["cut_y"])]
    axis = (above.min(axis=0) + above.max(axis=0)) / 2
    ring_radius = sk.ring_footprint(positions, triangles, turret["cut_z"], axis)
    turret_height = float(samples[:, 2].max()) - turret["cut_z"]
    bm.normal_update()
    in_band = lambda c, lo, hi: lo <= math.hypot(c.x - axis[0], c.y - axis[1]) / ring_radius <= hi and turret["cut_z"] - 0.1 * turret_height <= c.z <= turret["cut_z"] + 0.04 * turret_height
    roof_levels = [centre(f).z for f in bm.faces if abs(f.normal.z) > 0.95 and in_band(centre(f), 0.85, 1.5)]
    collar = [f for f in bm.faces if in_band(centre(f), 0.85, 1.15) and abs(f.normal.z) < math.cos(math.radians(30))
              and max(v.co.z for v in f.verts) - min(v.co.z for v in f.verts) <= 0.04 * turret_height]
    snapped = 0
    if roof_levels and collar:
        roof_z = min(float(np.median(roof_levels)), turret["cut_z"] - 1e-3 * turret_height)
        moved = {v for f in collar for v in f.verts if v.co.z > roof_z}
        for v in moved:
            v.co.z = roof_z
        snapped = len(moved)
    collar_report = {"faces": len(collar), "vertices_snapped": snapped}
    # A source part (a model in parts) lying wholly over or under a cut goes whole to that side and is not sliced: a
    # turret part sunk a little into the hull stays one closed turret.
    over_turret = whole_sides(bm.faces[:], lambda f: centre(f).z > turret["cut_z"])
    bisect(uncut(bm.faces[:], over_turret), (0, 0, turret["cut_z"]), (0, 0, 1))
    is_upper = lambda f: over_turret[f[part_layer]] if part_layer is not None and f[part_layer] in over_turret else centre(f).z > turret["cut_z"]
    upper = [f for f in bm.faces if is_upper(f)]
    # (only a part wholly over the turret cut may also go whole past the barrel cut: a part the turret cut slices is
    # sliced by the barrel cut too, so no face of it crosses a plane without a cut there)
    before_barrel = whole_sides([f for f in upper if part_layer is not None and over_turret.get(f[part_layer])], lambda f: centre(f).y < barrel["cut_y"])
    bisect(uncut(upper, before_barrel), (0, barrel["cut_y"], 0), (0, 1, 0))
    for part, over in over_turret.items():
        # (a part wholly over the turret cut but cut by the barrel's goes by the barrel cut alone: "upper")
        whole_region[part] = "body" if not over else ("barrel" if before_barrel.get(part) else "turret" if part in before_barrel else "upper")
    part_of = {}
    for face in bm.faces:
        c = centre(face)
        known = whole_region.get(face[part_layer]) if part_layer is not None else None
        part_of[face] = known if known in ("body", "turret", "barrel") else ("body" if not is_upper(face) else ("barrel" if c.y < barrel["cut_y"] else "turret"))
    # Hull roof the cut only clipped (a Smart Mesh's roof plates and bolts lie a hair above it, outside the turret's ring)
    # is not the turret's: carried off with it, it leaves a hole in the roof and hangs beside the flying turret.
    bm.verts.index_update()
    link = list(range(len(bm.verts)))

    def root(i):
        while link[i] != i:
            link[i] = link[link[i]]
            i = link[i]
        return i

    roof_faces = [f for f in bm.faces if part_of[f] != "body"]
    for face in roof_faces:
        for v in face.verts[1:]:
            link[root(v.index)] = root(face.verts[0].index)
    shells = {}
    for face in roof_faces:
        shells.setdefault(root(face.verts[0].index), []).append(face)
    shell_faces = list(shells.values())
    shell_points = [np.array([v.co[:] for v in {v for f in fs for v in f.verts}]) for fs in shell_faces]
    flat = sk.hull_level_pieces(shell_points, turret["cut_z"], float(samples[:, 2].max()), axis, ring_radius)
    for k in flat:
        for face in shell_faces[k]:
            part_of[face] = "body"
            face[hull_layer] = 1
    parts_report_hull = {"ring_radius": round(float(ring_radius), 4), "pieces": len(flat), "faces": sum(len(shell_faces[k]) for k in flat)}
    above = samples[samples[:, 2] >= turret["cut_z"]]
    above = above[above[:, 1] >= barrel["cut_y"]]
    pivots["turret"] = [float((above[:, 0].min() + above[:, 0].max()) / 2), float((above[:, 1].min() + above[:, 1].max()) / 2), turret["cut_z"]]
    pivots["barrel_base"] = barrel["pivot"]
    pivots["barrel_tip"] = barrel["pivot"]
    parts_report = {"turret_cut": turret, "barrel_cut": barrel, "hull_level_roof": parts_report_hull, "collar": collar_report}
elif kind == "plane":
    propeller = sk.propeller_cut(samples, contract["rules"]["propeller"])
    bisect(bm.faces[:], (0, propeller["cut_y"], 0), (0, 1, 0))
    part_of = {face: ("propeller" if centre(face).y < propeller["cut_y"] else "body") for face in bm.faces}
    pivots["propeller"] = propeller["hub"]
    parts_report = {"propeller_cut": propeller}
else:
    part_of = {face: "body" for face in bm.faces}

# Each moving part is split off with its own vertices (no vertex may follow two bones), then every loop the cuts
# opened is closed; holes_fill copies the neighbouring faces' UVs, so a cap takes the colours around it.
for part in sorted({p for p in part_of.values() if p != "body"}):
    faces = [f for f in bm.faces if part_of.get(f) == part]
    if faces:
        bmesh.ops.split(bm, geom=faces, use_only_faces=True)
caps = 0
if cuts:
    on_cut = lambda v: any(abs((v.co - co).dot(no)) < 1e-4 * size for co, no in cuts)
    # the caps on a tank's turret cut are marked, so the ring can be told from a deck lying at the cut's height (the
    # layer first: adding a layer reallocates the face data, which removes every face reference taken before)
    ring_layer = bm.faces.layers.int.new(RING_CAP) if kind == "vehicle" else None
    rim = [e for e in bm.edges if e.is_boundary and all(on_cut(v) for v in e.verts)]
    filled = bmesh.ops.holes_fill(bm, edges=rim, sides=0)["faces"]
    caps = len(filled)
    if ring_layer is not None:
        # Only the turret's underside (facing down) takes the dark hole texel below. The hull's lid over the ring keeps
        # its rim's colour, the roof's, as a vanilla hull keeps its roof when the turret flies off: on the M2A4 a dark
        # lid followed the faceted cut and two strict reviewers saw "a jagged black blob" on the roof in the death.
        for face in filled:
            if face.normal.z < -0.99 and abs(centre(face).z - turret["cut_z"]) < 1e-4 * size:
                face[ring_layer] = 1
    # holes_fill copies the rim's UVs across the cap, which smears the texture into a swirl a reviewer sees when the
    # turret is gone (the death clip): every corner of a cap takes one rim UV, so the cap is one flat colour
    uv = bm.loops.layers.uv.active
    if uv is not None:
        for face in filled:
            first = face.loops[0][uv].uv.copy()
            for loop in face.loops:
                loop[uv].uv = first
# A sheet the model's own surface leaves open along a long edge (a track's inner wall, a fender plate) is one-sided: seen
# from the open side it is culled and the background shows through (a magenta gap between the road wheels from below).
# Each such sheet (the faces joined to the open edge's face that lie within 15 degrees of it) gets a reversed copy.
sheet_edges = [e for e in bm.edges if e.is_boundary and e.calc_length() >= 0.03 * size] if kind == "vehicle" else []
hull_side = lambda f: centre(f).z <= turret["cut_z"]  # (the faces were split and rebuilt: part_of no longer holds them)
sheet_seeds = [e.link_faces[0] for e in sheet_edges if hull_side(e.link_faces[0])]
sheet, queue = set(), list(sheet_seeds)
while queue:
    f = queue.pop()
    if f in sheet:
        continue
    sheet.add(f)
    for edge in f.edges:
        for g in edge.link_faces:
            if g not in sheet and hull_side(g) and g.normal.dot(f.normal) >= math.cos(math.radians(15)):
                queue.append(g)
if sheet:
    copies = [g for g in bmesh.ops.duplicate(bm, geom=list(sheet))["geom"] if isinstance(g, bmesh.types.BMFace)]
    bmesh.ops.reverse_faces(bm, faces=copies)
parts_report["double_sided_sheets"] = {"open_edges": len(sheet_edges), "faces_copied": len(sheet) if sheet else 0}
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(model.data)
bm.free()
# The caps can take the model past the budget: reduce once more (the parts are separate pieces now, so they stay apart).
if triangle_count(model) > budget:
    decimate = model.modifiers.new("decimate", "DECIMATE")
    decimate.decimate_type = "COLLAPSE"
    decimate.ratio = budget / triangle_count(model) * 0.995
    decimate.use_collapse_triangulate = True
    if model.vertex_groups.get("thickened_cards"):
        # a thickened card's rim edges are the shortest in the model: the collapse would fold the card flat again
        decimate.vertex_group = "thickened_cards"
        decimate.invert_vertex_group = True
        decimate.vertex_group_factor = 1000.0
    bpy.context.view_layer.objects.active = model
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    parts_report["second_reduction"] = triangle_count(model)
for group in list(model.vertex_groups):
    model.vertex_groups.remove(group)
# The parts on the final faces. A face off the cut planes belongs to the region its centre lies in. The parts were
# split apart, so each is its own set of vertex-connected pieces: a cap (a face on a cut plane) and any piece take the
# part most of their piece's other faces have, so a cap closes the part it is joined to whichever way it faces.
bm = bmesh.new()
bm.from_mesh(model.data)


def region(c, upper=False):
    if kind == "vehicle":
        if c.z <= parts_report["turret_cut"]["cut_z"] and not upper:
            return "body"
        return "barrel" if c.y < parts_report["barrel_cut"]["cut_y"] else "turret"
    if kind == "plane":
        return "propeller" if c.y < parts_report["propeller_cut"]["cut_y"] else "body"
    return "body"


def on_cut_plane(face):
    c = centre(face)
    return any(abs((c - co).dot(no)) < 1e-4 * size and abs(face.normal.dot(no)) > 0.99 for co, no in cuts)


parent = list(range(len(bm.verts)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


for face in bm.faces:
    first = face.verts[0].index
    for v in face.verts[1:]:
        parent[find(v.index)] = find(first)
hull_layer = bm.faces.layers.int.get(HULL_LEVEL)
part_layer = bm.faces.layers.int.get(static_parts.PART_LAYER)


def region_of(face):
    if hull_layer is not None and face[hull_layer]:
        return "body"
    known = whole_region.get(face[part_layer]) if part_layer is not None else None
    return region(centre(face), upper=True) if known == "upper" else known or region(centre(face))


votes = {}
for face in bm.faces:
    if not on_cut_plane(face):
        votes.setdefault(find(face.verts[0].index), []).append(region_of(face))
face_part = []
for face in bm.faces:
    piece = votes.get(find(face.verts[0].index))
    face_part.append("body" if hull_layer is not None and face[hull_layer] else (max(set(piece), key=piece.count) if piece else region(centre(face))))
if HULL_LEVEL in model.data.attributes:
    model.data.attributes.remove(model.data.attributes[HULL_LEVEL])
# The caps on a tank's turret cut close the turret ring on the hull and the turret's underside. When the death blows the
# turret off, the ring must read as a hole, not a neat lid: these faces are shaded flat and take one dark texel (below).
ring_layer = bm.faces.layers.int.get(RING_CAP)
ring_caps = [i for i, face in enumerate(bm.faces) if face[ring_layer]] if ring_layer is not None else []
if RING_CAP in model.data.attributes:
    model.data.attributes.remove(model.data.attributes[RING_CAP])
# The clipped tops of hull fittings the turret cut sliced (pieces lying just above the cut) stay on the hull.
if kind == "vehicle":
    turret_pieces = {}
    for i, face in enumerate(bm.faces):
        if face_part[i] == "turret":
            turret_pieces.setdefault(find(face.verts[0].index), []).append(i)
    if turret_pieces:
        keys = list(turret_pieces)
        faces_list = list(bm.faces)
        heights = [[v.co.z for i in turret_pieces[k] for v in faces_list[i].verts] for k in keys]
        top = max(max(h) for h in heights)
        slivers = sk.cut_slivers(heights, parts_report["turret_cut"]["cut_z"], top)
        for k in slivers:
            for i in turret_pieces[keys[k]]:
                face_part[i] = "body"
        parts_report["cut_slivers_kept_on_hull"] = len(slivers)
# A tank's road wheels and track runs (separate pieces in a Smart Mesh) leave the hull: each wheel gets its own bone
# under vanilla's wheel_suspention and spins, the tracks follow wheel_suspention as vanilla's do.
wheel_parts = {}
if kind == "vehicle" and contract["rules"].get("wheels"):
    bm.verts.ensure_lookup_table()
    final_points = np.array([v.co[:] for v in bm.verts])
    final_triangles = np.array([[v.index for v in face.verts] for face in bm.faces])
    gear = sk.running_gear(final_points, final_triangles, contract["rules"]["wheels"])
    owner = {}
    for k, wheel in enumerate(gear["wheels"]):
        name_k = f"wheel_{k + 1:02d}"
        wheel_parts[name_k] = {"centre": [float(v) for v in wheel["centre"]], "radius": wheel["radius"]}
        for index in wheel["vertices"]:
            owner[int(index)] = name_k
    for index in gear["tracks"]:
        owner.setdefault(int(index), "tracks")
    for i, face in enumerate(bm.faces):
        if face_part[i] != "body":
            continue
        owners = {owner.get(v.index) for v in face.verts}
        if len(owners) == 1 and None not in owners:
            face_part[i] = owners.pop()
    parts_report["wheels"] = {k: {"centre": [round(v, 3) for v in w["centre"]], "radius": round(w["radius"], 3)} for k, w in wheel_parts.items()}
vertex_part = {}
for face, part in zip(bm.faces, face_part):
    for v in face.verts:
        vertex_part.setdefault(v.index, set()).add(part)
shared = sum(1 for parts in vertex_part.values() if len(parts) > 1)
if part_layer is not None:
    # which rigid part each source part ended on (triangles), and the parts that went whole onto their bone
    landed = {}
    for face, part in zip(bm.faces, face_part):
        if face[part_layer]:
            where = landed.setdefault(source_parts[face[part_layer] - 1], {})
            where[part] = where.get(part, 0) + 1
    parts_report["source_parts"] = landed
    parts_report["whole_parts"] = {source_parts[k - 1]: where for k, where in sorted(whole_region.items())}
bm.free()
if static_parts.PART_LAYER in model.data.attributes:
    model.data.attributes.remove(model.data.attributes[static_parts.PART_LAYER])
parts_report["caps"] = caps
parts_report["vertices_in_two_parts"] = shared
parts_report["triangles_per_part"] = {p: face_part.count(p) for p in sorted(set(face_part))}
report["parts"] = parts_report

# A spinning propeller sweeps a disc: when the disc reaches below the plane's ground, the plane is lifted by the
# difference, so no blade passes under it (a reviewer saw a blade tip dip below the ground in idle).
if kind == "plane" and "propeller_cut" in parts_report:
    hub = Vector(pivots["propeller"])
    blades = [Vector(v) for v in arrays(model)[0] if v[1] < parts_report["propeller_cut"]["cut_y"]]
    radius = max(((v - hub) - (v - hub).project(Vector((0, 1, 0)))).length for v in blades) if blades else 0.0
    ground = contract["size"]["ground_share"] * measure
    lift = max(0.0, ground - (hub.z - radius))
    if lift > 0:
        model.data.transform(Matrix.Translation((0, 0, lift)))
        pivots["propeller"] = [hub.x, hub.y, hub.z + lift]
    parts_report["propeller_sweep"] = {"radius": round(radius, 4), "lift": round(lift, 4)}

# ---- 3b. the base slab of a building or landmark: flat top, square outline (lib/static_slab.py) ----
slab, report["slab"] = static_slab.square_mesh(model.data, kind)

# ---- 4. skeleton, weights, collision, locators, material ----
positions, triangles = arrays(model)
low, high = positions.min(axis=0), positions.max(axis=0)
textures = request["textures"]
material = bie.create_shader(SimpleNamespace(shader=[contract["shader"]], diff=[textures["diffuse"]], n=[textures["normal"]], spec=[textures["specular"]]),
                             f"PDXmat_{name}Shape", str(out))
model.data.materials.clear()
model.data.materials.append(material)
while len(model.data.uv_layers) > 1:
    model.data.uv_layers.remove(model.data.uv_layers[-1])
bpy.context.view_layer.objects.active = model
model.select_set(True)
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(CREASE_DEGREES))
mesh = model.data
# The shading keeps every face within the crease angle of its own normal (static_mesh_ops.crease_shading); the ring
# caps are flat.
report["shading"] = crease_shading(mesh, CREASE_DEGREES, flat=ring_caps)
if ring_caps:
    hole = request.get("hole_uv")
    uv = mesh.uv_layers.active.data
    if hole:
        for p in ring_caps:
            for loop_index in mesh.polygons[p].loop_indices:
                uv[loop_index].uv = (float(hole[0]), float(hole[1]))
    parts_report["ring_caps"] = {"faces": len(ring_caps), "hole_uv": hole}
if slab is not None:
    report["slab"]["faces_shaded_flat"] = static_slab.shade_flat(mesh, slab)  # a corner shared with its sides must not lean

bone_specs = list(contract["skeleton"]["bones"]) + [{"name": b, "parent": "root", "head_share": None} for b in contract.get("extra_bones", [])]
bone_specs += [{"name": k, "parent": "wheel_suspention", "head_share": None} for k in wheel_parts]
for k, wheel in wheel_parts.items():
    pivots[k] = wheel["centre"]
rig = None
heads = {}
if bone_specs:
    for spec in bone_specs:
        heads[spec["name"]] = pivots.get(spec["name"]) or sk.box_point(low, high, spec["head_share"])
    armature = bpy.data.armatures.new(f"{name}_rig")
    rig = bpy.data.objects.new(f"{name}_rig", armature)
    scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for spec in bone_specs:
        bone = armature.edit_bones.new(spec["name"])
        bone.head = Vector(heads[spec["name"]])
        bone.tail = bone.head + Vector((0, 0.03 * measure, 0))
        bone.roll = 0.0
    for spec in bone_specs:
        if spec.get("parent"):
            armature.edit_bones[spec["name"]].parent = armature.edit_bones[spec["parent"]]
            armature.edit_bones[spec["name"]].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    part_bone = {**contract["parts"], **{k: k for k in wheel_parts}}
    groups = {part: model.vertex_groups.new(name=bone) for part, bone in part_bone.items()}
    bm = bmesh.new()
    bm.from_mesh(model.data)
    members = {part: set() for part in part_bone}
    for face, part in zip(bm.faces, face_part):
        for v in face.verts:
            members.setdefault(part, set()).add(v.index)
    bm.free()
    for part, indices in members.items():
        if part in groups and indices:
            groups[part].add(sorted(indices), 1.0, "REPLACE")
    # A part cut off the body is set off its cut by a hair (CUT_CLEARANCE of the height, under a millimetre at game
    # size), so its rim and the body's do not share positions: the file checks weld shared positions, and a turret
    # blown off in a death then read as a seam torn across the hull.
    clearance = CUT_CLEARANCE * float(np.ptp(positions[:, 2]))
    away = {"turret": (0.0, 0.0, clearance), "barrel": (0.0, -clearance, 0.0), "propeller": (0.0, -clearance, 0.0)}
    for part, vector in away.items():
        for index in members.get(part, ()):
            model.data.vertices[index].co += Vector(vector)
    if any(members.get(part) for part in away):
        parts_report["cut_clearance"] = round(clearance, 5)
    model.parent = rig
    model.modifiers.new("Armature", "ARMATURE").object = rig
    track_rule = contract.get("rules", {}).get("tracks")
    if track_rule and members.get("tracks"):
        scrolling_tracks(members["tracks"], track_rule)
report["bones"] = {b: [round(float(v), 4) for v in h] for b, h in heads.items()}

if contract.get("collision"):
    box = contract["collision"]
    span = high - low
    extent = np.asarray(box["size_share"]) * span
    middle = low + np.asarray(box["centre_share"]) * span
    bottom = low[2] + box["bottom_share"] * span[2]
    x0, x1 = middle[0] - extent[0] / 2, middle[0] + extent[0] / 2
    y0, y1 = middle[1] - extent[1] / 2, middle[1] + extent[1] / 2
    z0, z1 = bottom, bottom + extent[2]
    corners = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    box_mesh = bpy.data.meshes.new(box["name"])
    box_mesh.from_pydata(corners, [], faces)
    uv = box_mesh.uv_layers.new(name="UVMap")
    for loop in uv.data:  # one UV for every corner, so the exporter keeps the box's 8 vertices (vanilla's boxes have 8)
        loop.uv = (0.0, 0.0)
    collision = bpy.data.objects.new(box["name"].replace("Shape", "") or "collision", box_mesh)
    scene.collection.objects.link(collision)
    for polygon in box_mesh.polygons:
        polygon.use_smooth = True
    box_mesh.materials.append(bie.create_shader(SimpleNamespace(shader=["Collision"]), "PDXmat_collision", str(out)))
    if rig:
        collision.vertex_groups.new(name="root").add(list(range(8)), 1.0, "REPLACE")
        collision.parent = rig
        collision.modifiers.new("Armature", "ARMATURE").object = rig
    report["collision"] = {"low": [round(v, 4) for v in (x0, y0, z0)], "high": [round(v, 4) for v in (x1, y1, z1)]}
else:
    collision = None

locators = []
for spec in contract.get("locators", []):
    if spec["name"] == "barrel" and "barrel_cut" in parts_report:
        where = parts_report["barrel_cut"]["muzzle"]
    else:
        where = sk.box_point(low, high, spec["share"])
    empty = bpy.data.objects.new(spec["name"], None)
    empty.empty_display_type = "PLAIN_AXES"
    scene.collection.objects.link(empty)
    if spec.get("parent") and rig is not None:
        empty.parent = rig
        empty.parent_type = "BONE"
        empty.parent_bone = spec["parent"]
    bpy.context.view_layer.update()
    empty.matrix_world = Matrix.Translation(Vector(where))
    locators.append(empty)
report["locators"] = {e.name: [round(float(v), 4) for v in e.matrix_world.translation] for e in locators}

# ---- 5. clips ----
clip_reports = {}
if rig is not None and request.get("motion"):
    rest = {bone.name: bone.matrix_local.copy() for bone in rig.data.bones}
    order = [spec["name"] for spec in bone_specs]
    scene.render.fps, scene.render.fps_base = sk.HOI4_FPS, 1.0
    barrel_scale = 1.0
    if "barrel_cut" in parts_report and request.get("vanilla_barrel_length"):
        # A barrel recoils by the share of its own length vanilla's does, not by the share of the hull.
        barrel_scale = parts_report["barrel_cut"]["length"] / request["vanilla_barrel_length"]
    parents = {spec["name"]: spec.get("parent") for spec in bone_specs}
    # rest positions of each bone's vertices (at most 600 a bone, for speed), for the landing and ground rules
    rest_points = {}
    for part, indices in members.items():
        bone = part_bone.get(part) or part
        if bone in parents and indices:
            chosen = np.array(sorted(indices))[:: max(1, len(indices) // 600)]
            rest_points[bone] = np.vstack([rest_points.get(bone, np.zeros((0, 3))), positions[chosen]])

    def subtree(top):
        found = {top}
        changed = True
        while changed:
            changed = False
            for bone, parent in parents.items():
                if parent in found and bone not in found:
                    found.add(bone)
                    changed = True
        return found

    def moved(world, bones):
        points = [rest_points[b] @ world[b][:3, :3].T + world[b][:3, 3] for b in bones if b in rest_points]
        return np.vstack(points) if points else np.zeros((0, 3))

    def translate(world, bones, vector):
        for b in bones:
            m = np.eye(4)
            m[:3, 3] = vector
            world[b] = m @ world[b]

    # A tank's turret turns only as far as it clears the hull (sk.turret_clear_yaw, measured on this model): vanilla's
    # idle traverse swept the M2A4's anti-aircraft post through a deck fitting. Each clip but the death keeps its turns'
    # shape and timing, scaled toward rest on the side that went past the clear angle (sk.scaled_turns).
    turret_bone = (contract.get("parts") or {}).get("turret")
    clear_yaw = None
    if kind == "vehicle" and turret_bone in parents and "turret" in pivots:
        mounted = sk._mounted_on("turret", contract.get("mounts", {}))
        part_of_face = np.array(face_part)
        turning = triangles[np.isin(part_of_face, sorted(mounted))]
        hull = triangles[part_of_face == "body"]
        clear_yaw = sk.turret_clear_yaw(positions, turning, hull, pivots["turret"], up=2)
        parts_report["turret_clear_yaw"] = [round(clear_yaw[0], 1), round(clear_yaw[1], 1)]

    def twist_degrees(q):
        """The turn of a channel's rotation about the up axis (its twist), in degrees."""
        return math.degrees(2.0 * math.atan2(q[3], q[0]))

    for role, clip in request["motion"].items():
        turret_channel = clip["bones"].get(turret_bone) if turret_bone else None
        turret_turns = None
        if clear_yaw is not None and role != "death" and turret_channel:
            raw = np.unwrap(np.radians([twist_degrees(q) for q in turret_channel["q"]]))
            turns, shares = sk.scaled_turns(np.degrees(raw), clear_yaw)
            if shares != (1.0, 1.0):
                turret_turns = turns
            clip_reports.setdefault(role, {})["turret_traverse"] = {"clip": [round(float(np.degrees(raw).min()), 1), round(float(np.degrees(raw).max()), 1)],
                                                                    "shares": [round(shares[0], 3), round(shares[1], 3)]}
        action = bpy.data.actions.new(f"{name}_{role}")
        rig.animation_data_create()
        rig.animation_data.action = action
        frames = clip["frames"]
        worlds = []
        for f in range(frames):
            world = {}
            for bone in order:
                c = Vector(heads[bone])
                # a wheel turns only by the spin: vanilla's wheel channels also park its spare wheel bones far away
                channel = None if bone in wheel_parts else clip["bones"].get(bone)
                rotation = Quaternion(channel["q"][f]) if channel else Quaternion()
                if turret_turns is not None and bone == turret_bone:
                    # keep the channel's swing, replace its twist about the up axis by the scaled turn
                    twist = Quaternion(Vector((0.0, 0.0, 1.0)), math.radians(twist_degrees(channel["q"][f])))
                    rotation = Quaternion(Vector((0.0, 0.0, 1.0)), math.radians(float(turret_turns[f]))) @ twist.inverted() @ rotation
                shift = Vector(channel["d"][f]) * (barrel_scale / clip["scale"] if bone.startswith("barrel") and channel else 1.0) if channel else Vector()
                spin = clip.get("wheel_spin")
                if spin and bone in wheel_parts:
                    # vanilla's road wheel turn, scaled so the rim moves as far as vanilla's: a smaller wheel turns faster
                    turn = spin["degrees"][f] * spin["radius"] / max(wheel_parts[bone]["radius"], 1e-6)
                    rotation = rotation @ Quaternion(Vector((1.0, 0.0, 0.0)), math.radians(turn))
                for extra in clip.get("extras", {}).get(bone, []):
                    if extra["type"] == "turn":
                        rotation = rotation @ Quaternion(Vector(extra["axis"]), math.radians(extra["degrees"][f]))
                    elif extra["type"] == "spin":
                        rotation = rotation @ Quaternion(Vector(extra["axis"]), math.radians(extra["degrees_per_frame"] * f))
                local = np.array(Matrix.Translation(c + shift) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-c))
                world[bone] = (world[parents[bone]] if parents.get(bone) else np.eye(4)) @ local
            worlds.append(world)
        rules = {}
        # A tank's tracks and wheels stay on the ground in every clip but its death: vanilla's move bounces the whole tank
        # through tank_base, and the ground rule below lifted its dips and kept its rises, so the tank hopped. Each frame
        # the running gear keeps only its turn about z (sk.grounding), and the hull keeps its own bob on its suspension.
        gear_root = part_bone.get("tracks") if kind == "vehicle" else None
        if kind == "vehicle" and role != "death" and gear_root in parents:
            gear = [b for b in order if b == gear_root or parents.get(b) == gear_root]
            gear = gear if any(b in rest_points for b in gear) else [b for b in order if b in rest_points]
            rest_world = {b: np.eye(4) for b in order}
            ground = float(moved(rest_world, gear)[:, 2].min())
            # the correction goes on the bone under root that carries the running gear (vanilla's tank_base) and all
            # below it: root keeps its own motion (the idle's turn), and with it the Collision box, which follows root
            carrier = gear_root
            while parents.get(carrier) and parents.get(parents[carrier]):
                carrier = parents[carrier]
            corrected = subtree(carrier)
            heave = []
            for w in worlds:
                correction = sk.grounding(w[gear_root], moved(w, gear), ground)
                heave.append(abs(float(correction[2, 3])))
                for b in corrected:
                    w[b] = correction @ w[b]
            rules["gear_grounded_bones"] = carrier
            rules["gear_grounded_max_heave"] = round(max(heave), 4)
        # In a death, a mounted part that flies off (a tank's turret) is free: it lands clear of the hull and on the ground.
        free = set()
        if role == "death":
            gap = (contract.get("rigid") or {}).get("max_gap_share", 0.01) * measure
            for bone in contract.get("mounts", {}):
                channel = clip["bones"].get(bone)
                if channel and float(np.linalg.norm(np.array(channel["d"]), axis=1).max()) > gap:
                    if not any(bone in subtree(other) for other in free):
                        free |= subtree(bone)
        body = [b for b in order if b not in free]
        if free:
            centres = np.array([moved(w, free).mean(axis=0) for w in worlds])
            progress = sk.flight_progress(centres)
            # it lands on its flat base: the turn that sets its up axis back to world up is eased in over the flight
            top = next(bone for bone in order if bone in free)
            settle = sk.upright_turn(worlds[-1][top])
            settle_q = sk._quaternion_from_matrix(settle)
            for w, share, centre in zip(worlds, progress, centres):
                turn = np.eye(4)
                turn[:3, :3] = sk.quaternion_matrix(sk._slerp(np.array([1.0, 0.0, 0.0, 0.0]), settle_q, float(share)))
                about = np.eye(4)
                about[:3, 3] = centre
                back = np.eye(4)
                back[:3, 3] = -centre
                for bone in free:
                    w[bone] = about @ turn @ back @ w[bone]
            rules["landing_turn_degrees"] = round(sk.rotation_angle(settle_q), 1)
            # it comes down on the ground: vanilla's flight ends where vanilla's turret lay, which after the turn upright
            # left the Smart Mesh turret's base a third of the height in the air; the drop is eased in with the flight
            drop = max(0.0, float(moved(worlds[-1], free)[:, 2].min()))
            for w, share in zip(worlds, progress):
                translate(w, free, (0.0, 0.0, -drop * float(share) ** 2))
            rules["landing_drop"] = round(drop, 4)
            shift = sk.landing_shift(moved(worlds[-1], free), moved(worlds[-1], body))
            for w, share in zip(worlds, progress):
                translate(w, free, shift * share)
            rules["landing_shift"] = [round(float(v), 4) for v in shift]
        # A land model never sinks below the ground. In a death the wreck keeps vanilla's settling, but its free parts
        # do not go into the ground.
        if kind == "vehicle":
            lifts = np.zeros(frames) if role == "death" else sk.ground_lift([moved(w, body)[:, 2].min() for w in worlds])
            for w, lift in zip(worlds, lifts):
                translate(w, order, (0.0, 0.0, lift))
            rules["body_lift_max"] = round(float(lifts.max()), 4)
            if free:
                free_lifts = sk.ground_lift([moved(w, free)[:, 2].min() for w in worlds])
                for w, lift in zip(worlds, free_lifts):
                    translate(w, free, (0.0, 0.0, lift))
                rules["free_lift_max"] = round(float(free_lifts.max()), 4)
        previous = {}
        for f, world in enumerate(worlds):
            for bone in order:
                parent = parents.get(bone)
                local = np.linalg.inv(world[parent]) @ world[bone] if parent else world[bone]
                basis = rest[bone].inverted() @ Matrix(local.tolist()) @ rest[bone]
                location, quaternion, _scale = basis.decompose()
                if bone in previous and previous[bone].dot(quaternion) < 0:
                    quaternion.negate()
                previous[bone] = quaternion.copy()
                pose = rig.pose.bones[bone]
                pose.rotation_mode = "QUATERNION"
                pose.location, pose.rotation_quaternion = location, quaternion
                pose.keyframe_insert("location", frame=f + 1)
                pose.keyframe_insert("rotation_quaternion", frame=f + 1)
        path = out / f"{name}_{role}.anim"
        bpy.context.view_layer.objects.active = rig
        scene.frame_start, scene.frame_end = 1, frames
        bie.export_animfile(str(path), frame_start=1, frame_end=frames, uniform_scale=True)
        clip_reports[role] = {**clip_reports.get(role, {}), "frames": frames, "file": path.name, **rules}
    for pose in rig.pose.bones:
        pose.location, pose.rotation_quaternion = Vector(), Quaternion()
    rig.animation_data.action = None
report["clips"] = clip_reports

# ---- export the mesh ----
if rig is not None:
    rig.data.pose_position = "REST"
bpy.context.view_layer.update()
bpy.ops.object.select_all(action="DESELECT")
for obj in [model] + ([collision] if collision else []) + locators:
    obj.select_set(True)
bpy.context.view_layer.objects.active = model
mesh_path = out / f"{name}.mesh"
bie.export_meshfile(str(mesh_path), exp_mesh=True, exp_skel=rig is not None, exp_locs=True, exp_selected=True, as_blendshape=False,
                    split_verts=False, sort_verts="+", plain_txt=False)
report["mesh"] = mesh_path.name
report["triangles"] = triangle_count(model)
final_points, final_triangles = arrays(model)
report["open_edges_final"] = sk.open_edge_count(tripo_shape.weld(final_points, size * 1e-5)[final_triangles])
report["box"] = {"low": [round(float(v), 4) for v in low], "high": [round(float(v), 4) for v in high]}
if request.get("blend"):
    bpy.ops.wm.save_as_mainfile(filepath=request["blend"])
Path(request["report"]).write_text(json.dumps(report, indent=1), encoding="utf-8")
print("STATIC_MODEL_DONE", mesh_path)
