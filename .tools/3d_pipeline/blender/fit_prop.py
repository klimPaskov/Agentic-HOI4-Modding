"""Blender side of `fit_prop.py`: fit a held prop to a unit's clips, bind it to the hand and export. Do not run directly.

blender -b --python fit_prop.py -- <request.json>

Ported from the ZIN 3D session's `fit_weapon.py` (2026-11-06), which fitted the yeti's club after a
fixed grip hit the ground and clipped the body.

1. The unit and its clips are imported from the exported bytes.
2. The prop is the source's longest piece, closed: thin loose bits dropped, welded, open loops capped,
   winding made consistent. It is scaled to `length` of the unit's height.
3. The palm is the rest-pose centre of the vertices weighted mostly to `bone`. The grip point sits
   `grip` of the prop's length from its butt, and the butt points up (`butt: high`) or down.
4. Each of 42 directions in the hand bone's own frame is scored over every `step`-th frame of every
   clip: prop sample points inside the deformed body (the nearest surface faces away) or below the
   ground count against it, the ground `ground_weight` times, since a prop in the ground shows at
   every zoom. Points within the fist are held, not clipping, so the first 12 % from the grip is not
   scored.
5. The best direction is attached in the rest pose, bound fully to the hand bone as its own shape
   (replacing a shape of the same name that an earlier fit left),
   given a `PdxMeshAdvanced` material on `<prop>_{diffuse,specular,normal}.dds`, and exported.

A JSON report holds the palm, the score of the best, the worst and the top five directions, and the
best direction's clipping per clip.
"""

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
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

request = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))

for module in addon_utils.modules():
    if module.__name__.endswith("io_pdx_mesh"):
        addon_utils.enable(module.__name__, default_set=False)
        bie = importlib.import_module(module.__name__ + ".pdx_blender.blender_import_export")
        break
else:
    raise SystemExit("io_pdx_mesh is not installed for this Blender; run bootstrap_3d_workflow.py")

bpy.ops.wm.read_factory_settings(use_empty=True)
mesh_path = Path(request["mesh"])
bie.import_meshfile(str(mesh_path), imp_mesh=True, imp_skel=True, imp_locs=True, join_materials=True, bonespace=False)
rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
# A prop fitted before is replaced, not doubled; its vertices, bound to the hand, would also move the palm.
replaced = [o.name for o in bpy.data.objects if o.type == "MESH" and (o.name == request["prop_stem"] or o.name.startswith(request["prop_stem"] + "."))]
for name in replaced:
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
body = [o for o in bpy.data.objects if o.type == "MESH" and "collision" not in o.name.lower()]
for o in body:
    o.parent = rig
    o.matrix_parent_inverse = rig.matrix_world.inverted()
heights = [(o.matrix_world @ v.co).z for o in body for v in o.data.vertices]
height, ground = max(heights) - min(heights), min(heights)
if request["bone"] not in rig.data.bones:
    raise SystemExit(f"The unit has no bone {request['bone']}; its bones are {', '.join(b.name for b in rig.data.bones)}")
bone = rig.data.bones[request["bone"]]

# The palm: the rest-pose centre of the vertices weighted mostly to the hand bone.
palm_points = []
for o in body:
    group = o.vertex_groups.get(request["bone"])
    if group is None:
        continue
    for v in o.data.vertices:
        weights = {g.group: g.weight for g in v.groups}
        if weights.get(group.index, 0.0) >= 0.5 and weights[group.index] >= max(weights.values()):
            palm_points.append(o.matrix_world @ v.co)
if not palm_points:
    raise SystemExit(f"No vertex is weighted mostly to {request['bone']}.")
palm = sum(palm_points, Vector()) / len(palm_points)

actions = []
for path in request["anims"]:
    if rig.animation_data:
        rig.animation_data.action = None
    bie.import_animfile(path, frame_start=1)
    action = rig.animation_data.action
    action.name = Path(path).stem
    action.use_fake_user = True
    actions.append(action)
if rig.animation_data:
    rig.animation_data.action = None
for pose_bone in rig.pose.bones:
    pose_bone.matrix_basis = Matrix()
bpy.context.view_layer.update()

# The prop, closed.
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=request["prop"])
imported = [o for o in bpy.data.objects if o not in before]
parts = [o for o in imported if o.type == "MESH"]
if not parts:
    raise SystemExit(f"{request['prop']} holds no mesh")
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
if len(parts) > 1:
    bpy.ops.object.join()
prop = bpy.context.view_layer.objects.active
prop.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in imported:
    if o != prop and o.name in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)


def components(bm):
    seen, out = set(), []
    for start in bm.verts:
        if start.index in seen:
            continue
        stack, part = [start], []
        seen.add(start.index)
        while stack:
            vertex = stack.pop()
            part.append(vertex.index)
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other.index not in seen:
                    seen.add(other.index)
                    stack.append(other)
        out.append(part)
    return out


bm = bmesh.new()
bm.from_mesh(prop.data)
bm.verts.ensure_lookup_table()
# A sheet of several props: group overlapping pieces along X and keep the tallest group.
spans = sorted(([min(bm.verts[i].co.x for i in p), max(bm.verts[i].co.x for i in p), p] for p in components(bm)), key=lambda s: s[0])
groups = []
for low, high, part in spans:
    if groups and low <= groups[-1][1]:
        groups[-1][1] = max(groups[-1][1], high)
        groups[-1][2].extend(part)
    else:
        groups.append([low, high, list(part)])
chosen = max((g[2] for g in groups), key=lambda g: max(bm.verts[i].co.z for i in g) - min(bm.verts[i].co.z for i in g))
keep = set(chosen)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in keep], context="VERTS")
bm.verts.ensure_lookup_table()
pieces = components(bm)
largest = max(len(p) for p in pieces)
bmesh.ops.delete(bm, geom=[bm.verts[i] for p in pieces if len(p) < 0.15 * largest for i in p], context="VERTS")
span_z = max(v.co.z for v in bm.verts) - min(v.co.z for v in bm.verts)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-3 * max(span_z, 1e-6))
bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
seen = set()
for start in [e for e in bm.edges if e.is_boundary]:
    if start in seen:
        continue
    loop, edge, vertex = [start.verts[0]], start, start.verts[1]
    seen.add(start)
    while vertex is not loop[0]:
        loop.append(vertex)
        following = [e for e in vertex.link_edges if e.is_boundary and e is not edge and e not in seen]
        if not following:
            break
        edge = following[0]
        seen.add(edge)
        vertex = edge.other_vert(vertex)
    if vertex is loop[0] and len(loop) >= 3:
        centre = bm.verts.new(sum((v.co for v in loop), Vector()) / len(loop))
        for a, b in zip(loop, loop[1:] + loop[:1]):
            try:
                bm.faces.new((a, b, centre))
            except ValueError:
                pass
bmesh.ops.triangulate(bm, faces=list(bm.faces))
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
open_edges = sum(1 for e in bm.edges if e.is_boundary)
bm.verts.ensure_lookup_table()
points = np.array([list(v.co) for v in bm.verts])
points *= request["length"] * height / max(np.ptp(points[:, 2]), 1e-6)
for vertex, point in zip(bm.verts, points):
    vertex.co = Vector(point)
centre = points.mean(axis=0)
axis = np.linalg.svd(points - centre, full_matrices=False)[2][0]
if (axis[2] < 0) == (request["butt"] == "high"):
    axis = -axis  # from the butt toward the head
along = (points - centre) @ axis
butt = centre + axis * along.min()
prop_length = float(np.ptp(along))
grip = butt + axis * prop_length * request["grip"]
local = points - grip
free = local[np.linalg.norm(local, axis=1) > 0.12 * prop_length]
sample = free[np.linspace(0, len(free) - 1, min(160, len(free))).astype(int)] if len(free) else local[:1]

hand_rest = rig.matrix_world @ bone.matrix_local
hand_rest_inverse = hand_rest.inverted()


def directions():
    """42 directions: an icosahedron's 12 vertices and its 30 edge midpoints."""

    t = (1 + math.sqrt(5)) / 2
    vertices = [Vector(v).normalized() for v in [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]]
    out = list(vertices)
    for i in range(12):
        for j in range(i + 1, 12):
            if (vertices[i] - vertices[j]).length < 1.1:
                out.append((vertices[i] + vertices[j]).normalized())
    return out


candidates = []
for direction in directions():
    world_direction = (hand_rest.to_3x3() @ direction).normalized()
    turn = Vector(axis).rotation_difference(world_direction).to_matrix().to_4x4()
    in_hand = hand_rest_inverse @ (Matrix.Translation(palm) @ turn)
    candidates.append({"direction": list(direction), "in_hand": in_hand, "score": 0.0, "inside": 0, "under": 0, "per_clip": {}})

homogeneous = np.c_[sample, np.ones(len(sample))]
epsilon = 0.002 * height
frames_checked = 0
for action in actions:
    rig.animation_data_create()
    rig.animation_data.action = action
    try:
        if action.slots and rig.animation_data.action_slot is None:
            rig.animation_data.action_slot = action.slots[0]
    except AttributeError:
        pass
    first, last = (int(round(x)) for x in action.frame_range)
    death = action.name.endswith("death")
    for frame in range(first, last + 1, max(1, int(request["step"]))):
        bpy.context.scene.frame_set(frame)
        graph = bpy.context.evaluated_depsgraph_get()
        trees = []
        for o in body:
            evaluated = o.evaluated_get(graph)
            mesh = evaluated.to_mesh()
            trees.append(BVHTree.FromPolygons([o.matrix_world @ v.co for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons]))
            evaluated.to_mesh_clear()
        hand_pose = rig.matrix_world @ rig.pose.bones[request["bone"]].matrix
        floor = ground - (0.02 * height if death else 0.0)
        for candidate in candidates:
            world = (np.array(hand_pose @ candidate["in_hand"]) @ homogeneous.T)[:3].T
            for point in world:
                position = Vector(point)
                if any(
                    location is not None and (position - location).dot(normal) < -epsilon
                    for location, normal, _index, _distance in (tree.find_nearest(position) for tree in trees)
                ):
                    candidate["inside"] += 1
                    candidate["per_clip"][action.name] = candidate["per_clip"].get(action.name, 0) + 1
                if point[2] < floor - epsilon:
                    candidate["under"] += 1
            candidate["score"] = candidate["inside"] + request["ground_weight"] * candidate["under"]
        frames_checked += 1

ranked = sorted(candidates, key=lambda c: c["score"])
best = ranked[0]
keys = ("direction", "score", "inside", "under")
report = {
    "frames_checked": frames_checked,
    "samples_per_frame": len(sample),
    "palm": list(palm),
    "prop_open_edges": open_edges,
    "prop_length_share": round(prop_length / height, 4),
    "replaced_prop": replaced,
    "best": {**{k: best[k] for k in keys}, "per_clip": best["per_clip"]},
    "worst": {k: ranked[-1][k] for k in keys},
    "top5": [{k: c[k] for k in keys} for c in ranked[:5]],
}

# Attach the best fit in the rest pose, bound fully to the hand bone, and export.
if rig.animation_data:
    rig.animation_data.action = None
for pose_bone in rig.pose.bones:
    pose_bone.matrix_basis = Matrix()
bpy.context.view_layer.update()
rest = hand_rest @ best["in_hand"]
for vertex in bm.verts:
    vertex.co = rest @ (Vector(vertex.co) - Vector(grip))
bm.to_mesh(prop.data)
bm.free()
prop.matrix_world = Matrix()
prop.data.update()
prop.name = prop.data.name = request["prop_stem"]
prop.data.materials.clear()
material = SimpleNamespace(
    shader=["PdxMeshAdvanced"],
    diff=[f"{request['prop_stem']}_diffuse.dds"],
    spec=[f"{request['prop_stem']}_specular.dds"],
    n=[f"{request['prop_stem']}_normal.dds"],
)
prop.data.materials.append(bie.create_shader(material, f"PDXmat_{request['prop_stem']}", str(Path(request["out"]).parent)))
group = prop.vertex_groups.new(name=request["bone"])
group.add(list(range(len(prop.data.vertices))), 1.0, "REPLACE")
prop.modifiers.new("Armature", "ARMATURE").object = rig
prop.parent = rig
prop.matrix_parent_inverse = rig.matrix_world.inverted()
bpy.ops.object.select_all(action="DESELECT")
for o in body + [prop] + [o for o in bpy.data.objects if o.type == "EMPTY"]:
    o.select_set(True)
Path(request["out"]).parent.mkdir(parents=True, exist_ok=True)
bie.export_meshfile(request["out"], exp_mesh=True, exp_skel=True, exp_locs=True, exp_selected=True, as_blendshape=False,
                    split_verts=False, sort_verts="+", plain_txt=False)
report["prop_triangles"] = sum(len(p.vertices) - 2 for p in prop.data.polygons)
Path(request["report"]).write_text(json.dumps(report, indent=1), encoding="utf-8")
print("PROP_FITTED", request["out"])
