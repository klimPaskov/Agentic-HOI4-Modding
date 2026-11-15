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
   closes each cut with a cap that takes its colours from the faces around it, so a turning turret shows no hole.
4. Builds the kind's skeleton (vanilla's bone names; rest places from the parts or from vanilla's shares of the box),
   binds each part rigidly to its bone, adds the `Collision` box and the locators, and gives every rendered shape the
   kind's PDX material.
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
from lib import tripo_shape

request = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
# Faces within this angle of each other count as one flat plate in the first reduction step (kit rule: a degree or two
# of a generated plate's waviness, well under the 40-degree crease the shading keeps sharp).
PLANAR_DEGREES = 3.0
SMALL_HOLE_EDGES = 32
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
    mesh = obj.data
    mesh.calc_loop_triangles()
    positions = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", positions)
    triangles = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", triangles)
    return positions.reshape(-1, 3), triangles.reshape(-1, 3)


def triangle_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


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
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=size * 1e-5)
welded -= len(bm.verts)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(model.data)
bm.free()
budget = contract["triangle_budget"]["value"]
# The cuts and caps add triangles, so the mesh is reduced to 94 % of the budget first.
target = int(budget * 0.94)
current = triangle_count(model)
planar = None
if current > target:
    # First merge the faces that lie flat together (within PLANAR_DEGREES), keeping UV island borders, then collapse
    # what is left. Collapsing a generated hard-surface mesh straight to a vanilla budget crumples flat plates into
    # folds and smears the texture across them; flat plates cost almost nothing once merged.
    decimate = model.modifiers.new("planar", "DECIMATE")
    decimate.decimate_type = "DISSOLVE"
    decimate.angle_limit = math.radians(PLANAR_DEGREES)
    decimate.delimit = {"UV"}
    bpy.context.view_layer.objects.active = model
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    bm = bmesh.new()
    bm.from_mesh(model.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(model.data)
    bm.free()
    planar = triangle_count(model)
    current = planar
if current > target:
    decimate = model.modifiers.new("decimate", "DECIMATE")
    decimate.decimate_type = "COLLAPSE"
    decimate.ratio = target / current
    decimate.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = model
    bpy.ops.object.modifier_apply(modifier=decimate.name)
# Small open loops a reviewer sees as specks of the background (the kit closes loops up to 32 edges without a seam,
# check_unit_files.SMALL_HOLE_EDGES); larger ones stay for UNIT-HOLE to report.
bm = bmesh.new()
bm.from_mesh(model.data)
closed = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=SMALL_HOLE_EDGES)["faces"]
bmesh.ops.triangulate(bm, faces=closed)
bm.to_mesh(model.data)
bm.free()
report["small_holes_closed"] = len(closed)
shape = tripo_shape.shape_report(original, arrays(model))
report["reduction"] = {"welded_vertices": welded, "from": len(original[1]), "after_planar": planar, "to": triangle_count(model), "budget": budget,
                       "iou": shape["iou"], "shells_before": shape["shells_before"]["shells"], "shells_after": shape["shells_after"]["shells"],
                       "problems": tripo_shape.shape_problems(shape)}

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


if kind == "vehicle":
    turret = sk.turret_cut(samples, contract["rules"]["turret"])
    barrel = sk.barrel_cut(samples, turret["cut_z"], contract["rules"]["barrel"])
    bisect(bm.faces[:], (0, 0, turret["cut_z"]), (0, 0, 1))
    upper = [f for f in bm.faces if centre(f).z > turret["cut_z"]]
    bisect(upper, (0, barrel["cut_y"], 0), (0, 1, 0))
    part_of = {}
    for face in bm.faces:
        c = centre(face)
        part_of[face] = "body" if c.z <= turret["cut_z"] else ("barrel" if c.y < barrel["cut_y"] else "turret")
    above = samples[samples[:, 2] >= turret["cut_z"]]
    above = above[above[:, 1] >= barrel["cut_y"]]
    pivots["turret"] = [float((above[:, 0].min() + above[:, 0].max()) / 2), float((above[:, 1].min() + above[:, 1].max()) / 2), turret["cut_z"]]
    pivots["barrel_base"] = barrel["pivot"]
    pivots["barrel_tip"] = barrel["pivot"]
    parts_report = {"turret_cut": turret, "barrel_cut": barrel}
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
    rim = [e for e in bm.edges if e.is_boundary and all(on_cut(v) for v in e.verts)]
    caps = len(bmesh.ops.holes_fill(bm, edges=rim, sides=0)["faces"])
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(model.data)
bm.free()
# The caps can take the model past the budget: reduce once more (the parts are separate pieces now, so they stay apart).
if triangle_count(model) > budget:
    decimate = model.modifiers.new("decimate", "DECIMATE")
    decimate.decimate_type = "COLLAPSE"
    decimate.ratio = budget / triangle_count(model) * 0.995
    decimate.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = model
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    parts_report["second_reduction"] = triangle_count(model)
# The parts on the final faces. A face off the cut planes belongs to the region its centre lies in. The parts were
# split apart, so each is its own set of vertex-connected pieces: a cap (a face on a cut plane) and any piece take the
# part most of their piece's other faces have, so a cap closes the part it is joined to whichever way it faces.
bm = bmesh.new()
bm.from_mesh(model.data)


def region(c):
    if kind == "vehicle":
        if c.z <= parts_report["turret_cut"]["cut_z"]:
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
votes = {}
for face in bm.faces:
    if not on_cut_plane(face):
        votes.setdefault(find(face.verts[0].index), []).append(region(centre(face)))
face_part = []
for face in bm.faces:
    piece = votes.get(find(face.verts[0].index))
    face_part.append(max(set(piece), key=piece.count) if piece else region(centre(face)))
vertex_part = {}
for face, part in zip(bm.faces, face_part):
    for v in face.verts:
        vertex_part.setdefault(v.index, set()).add(part)
shared = sum(1 for parts in vertex_part.values() if len(parts) > 1)
bm.free()
parts_report["caps"] = caps
parts_report["vertices_in_two_parts"] = shared
parts_report["triangles_per_part"] = {p: face_part.count(p) for p in sorted(set(face_part))}
report["parts"] = parts_report

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
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
# A corner whose shading normal points against its own face shades as a pale facet (UNIT-NORMALS): it takes the
# face's normal. Folded or very thin parts of a generated mesh leave a few.
mesh = model.data
corner = [Vector(c.vector) for c in mesh.corner_normals]
flipped = 0
for polygon in mesh.polygons:
    for index in polygon.loop_indices:
        if corner[index].dot(polygon.normal) <= 0.0:
            corner[index] = polygon.normal.copy()
            flipped += 1
if flipped:
    mesh.normals_split_custom_set(corner)
report["normals_set_to_face"] = flipped

bone_specs = list(contract["skeleton"]["bones"]) + [{"name": b, "parent": "root", "head_share": None} for b in contract.get("extra_bones", [])]
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
    part_bone = contract["parts"]
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
    model.parent = rig
    model.modifiers.new("Armature", "ARMATURE").object = rig
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
    for role, clip in request["motion"].items():
        action = bpy.data.actions.new(f"{name}_{role}")
        rig.animation_data_create()
        rig.animation_data.action = action
        frames = clip["frames"]
        previous = {}
        for f in range(frames):
            for bone in order:
                c = Vector(heads[bone])
                channel = clip["bones"].get(bone)
                rotation = Quaternion(channel["q"][f]) if channel else Quaternion()
                shift = Vector(channel["d"][f]) * (barrel_scale / clip["scale"] if bone.startswith("barrel") and channel else 1.0) if channel else Vector()
                for extra in clip.get("extras", {}).get(bone, []):
                    if extra["type"] == "turn":
                        rotation = rotation @ Quaternion(Vector(extra["axis"]), math.radians(extra["degrees"][f]))
                    elif extra["type"] == "spin":
                        rotation = rotation @ Quaternion(Vector(extra["axis"]), math.radians(extra["degrees_per_frame"] * f))
                local = Matrix.Translation(c + shift) @ rotation.to_matrix().to_4x4() @ Matrix.Translation(-c)
                basis = rest[bone].inverted() @ local @ rest[bone]
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
        clip_reports[role] = {"frames": frames, "file": path.name}
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
report["box"] = {"low": [round(float(v), 4) for v in low], "high": [round(float(v), 4) for v in high]}
if request.get("blend"):
    bpy.ops.wm.save_as_mainfile(filepath=request["blend"])
Path(request["report"]).write_text(json.dumps(report, indent=1), encoding="utf-8")
print("STATIC_MODEL_DONE", mesh_path)
