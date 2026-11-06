"""Blender side of `repair_unit.py`: repair an exported unit's mesh and export it again. Do not run directly.

blender -b --python repair_mesh.py -- <request.json>

The request names the input `.mesh`, the output `.mesh`, the repairs to run and the bridge hop
distance. The skeleton, bone order, skin of every untouched vertex, materials, shapes and
locators are kept, so the unit's existing `.anim` files still play on the repaired mesh.

Repairs, each optional and run in this order:
- `winding`: make every connected surface face one way, outward for closed parts
  (`bmesh.ops.recalc_face_normals`). The game culls back faces, so a flipped triangle is a hole
  from one side.
- `bridges`: delete the faces that join body parts that move apart (an edge whose two vertices
  follow bones `hops` or more parent steps apart, with neither blending the other's bone), then
  close each opened loop on both sides with a flat cap. Skinning tears such faces into spikes and
  webs in every clip.
- `holes`: close open loops of at most `max_hole_edges` edges.

Every cap vertex is an existing boundary vertex, so caps inherit their neighbours' weights and no
new weight is invented. Imported corner normals are kept, and cap corners take the cap's face normal.
A JSON report lists what changed.
"""

import json
import sys
from pathlib import Path

import addon_utils
import bmesh
import bpy

request = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
repairs = set(request["repairs"])
report = {"input": request["mesh"], "output": request["out"], "objects": {}}

for module in addon_utils.modules():
    if module.__name__.endswith("io_pdx_mesh"):
        addon_utils.enable(module.__name__, default_set=False)
        break
else:
    raise SystemExit("io_pdx_mesh is not installed for this Blender; run bootstrap_3d_workflow.py")

bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.io_pdx_mesh.import_mesh(filepath=request["mesh"], chk_locs=True)
scene = bpy.context.scene
rig = next((o for o in scene.objects if o.type == "ARMATURE"), None)


def bone_hops():
    if rig is None:
        return {}
    chains = {}
    for bone in rig.data.bones:
        chain, node = [], bone
        while node is not None:
            chain.append(node.name)
            node = node.parent
        chains[bone.name] = chain
    hops = {}
    for a, chain_a in chains.items():
        position = {name: i for i, name in enumerate(chain_a)}
        for b, chain_b in chains.items():
            common = next((i for i, name in enumerate(chain_b) if name in position), None)
            hops[a, b] = position[chain_b[common]] + common if common is not None else len(chains)
    return hops


HOPS = bone_hops()


def weights_of(obj, bm):
    """Vertex index -> {bone name: weight} from the deform layer."""

    layer = bm.verts.layers.deform.verify()
    names = {group.index: group.name for group in obj.vertex_groups}
    return {v.index: {names[g]: w for g, w in v[layer].items() if g in names and w > 0} for v in bm.verts}


def bridge_edges(bm, weights):
    found = []
    for edge in bm.edges:
        a, b = (weights[v.index] for v in edge.verts)
        if not a or not b:
            continue
        bone_a, bone_b = max(a, key=a.get), max(b, key=b.get)
        if bone_a == bone_b or HOPS.get((bone_a, bone_b), 0) < request["hops"]:
            continue
        if max(b.get(bone_a, 0.0), a.get(bone_b, 0.0)) >= 0.1:
            continue
        found.append(edge)
    return found


def cap_loops(bm, edges, max_edges):
    """Close the open loops among `edges` that have at most `max_edges` edges (0: any size) and
    triangulate the caps. Returns the number of loops closed."""

    boundary = [e for e in edges if e.is_valid and e.is_boundary]
    if not boundary:
        return 0
    result = bmesh.ops.holes_fill(bm, edges=boundary, sides=max_edges)
    faces = list(result.get("faces", []))
    # holes_fill skips some loop shapes. Close what is left by walking each loop and making one
    # polygon over its own vertices.
    for loop in boundary_loops([e for e in boundary if e.is_valid and e.is_boundary]):
        if 3 <= len(loop) and (max_edges == 0 or len(loop) <= max_edges):
            try:
                faces.append(bm.faces.new(loop))
            except ValueError:
                continue  # a face over these vertices already exists
    faces = [f for f in faces if f.is_valid]
    if faces:
        result = bmesh.ops.triangulate(bm, faces=faces, quad_method="BEAUTY", ngon_method="BEAUTY")
        orient_caps(bm, set(result["faces"]))
    return len(faces)


def orient_caps(bm, caps):
    """Make every part that received a cap consistently wound and outward again.

    Only the connected parts that hold a cap are recalculated; each was consistent before the cut,
    so its old faces keep their direction and the caps follow them."""

    if not caps:
        return
    part, frontier = set(caps), list(caps)
    while frontier:
        face = frontier.pop()
        for edge in face.edges:
            for other in edge.link_faces:
                if other not in part:
                    part.add(other)
                    frontier.append(other)
    bmesh.ops.recalc_face_normals(bm, faces=list(part))


def boundary_loops(edges):
    """Ordered vertex rings of the open loops formed by `edges`.

    Walks face corners around each vertex, so two loops that touch at one vertex come out as two
    rings instead of one figure eight."""

    remaining = {e for e in edges if e.is_valid and e.is_boundary}
    loops = []
    while remaining:
        edge = remaining.pop()
        corner = edge.link_loops[0]
        ring = [corner.vert]
        while True:
            step = corner.link_loop_next
            while not step.edge.is_boundary:
                step = step.link_loop_radial_next.link_loop_next
            if step.edge is edge or step.edge not in remaining:
                break
            remaining.discard(step.edge)
            ring.append(step.vert)
            corner = step
        loops.extend(_split_at_repeats(ring))
    return loops


def _split_at_repeats(ring):
    """Split a ring that passes a vertex twice into simple rings."""

    out, stack, position = [], [], {}
    for vert in ring:
        if vert in position:
            start = position[vert]
            out.append(stack[start:])
            for gone in stack[start + 1:]:
                position.pop(gone, None)
            stack = stack[: start + 1]
        else:
            position[vert] = len(stack)
            stack.append(vert)
    out.append(stack)
    return [simple for simple in out if len(simple) >= 3]


for obj in [o for o in scene.objects if o.type == "MESH"]:
    entry = {"triangles_before": len(obj.data.polygons)}
    # io_pdx_mesh imports every face as sharp, so corner normals read back as flat face normals and
    # the exporter splits every corner: the unit would shade faceted. Clear the flag so the imported
    # smooth normals apply, then keep each corner's normal through the edits.
    if "sharp_face" in obj.data.attributes:
        obj.data.attributes.remove(obj.data.attributes["sharp_face"])
    corner_normals = [tuple(n.vector) for n in obj.data.corner_normals]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    kept = bm.loops.layers.float_vector.new("kept_normal")
    corner = 0
    for face in bm.faces:
        for loop in face.loops:
            loop[kept] = corner_normals[corner]
            corner += 1
    height = max((max(v.co.z for v in bm.verts) - min(v.co.z for v in bm.verts)), 1e-6) if bm.verts else 1.0
    # Weld split seams (UVs and normals live on face corners, so nothing is lost), so surfaces connect.
    count = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=height * 1e-5)
    entry["welded_vertices"] = count - len(bm.verts)
    if "winding" in repairs:
        before = [f.normal.copy() for f in bm.faces]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        entry["faces_flipped"] = sum(1 for f, n in zip(bm.faces, before) if f.normal.dot(n) < 0)
    if "bridges" in repairs and rig is not None:
        bm.verts.ensure_lookup_table()
        weights = weights_of(obj, bm)
        bridges = bridge_edges(bm, weights)
        faces = list({f for e in bridges for f in e.link_faces})
        pairs = {}
        for edge in bridges:
            a, b = (weights[v.index] for v in edge.verts)
            key = "-".join(sorted((max(a, key=a.get), max(b, key=b.get))))
            pairs[key] = pairs.get(key, 0) + 1
        loop_edges = {e for f in faces for e in f.edges}
        bmesh.ops.delete(bm, geom=faces, context="FACES_ONLY")
        # Edges that joined the two parts directly are now loose; drop them, keep both sides' rims.
        loose = [e for e in loop_edges if e.is_valid and not e.link_faces]
        bmesh.ops.delete(bm, geom=loose, context="EDGES")
        # A cut can open into an existing seam, so close every open loop that touches a cut vertex.
        cut = {v for e in loop_edges if e.is_valid for v in e.verts}
        touched = {v for loop in boundary_loops([e for e in bm.edges if e.is_boundary]) if cut & set(loop) for v in loop}
        rims = [e for e in bm.edges if e.is_boundary and (e.verts[0] in touched or e.verts[0] in cut)]
        entry.update({"bridge_edges": len(bridges), "bridge_faces_removed": len(faces), "bridge_pairs": pairs,
                      "caps": cap_loops(bm, rims, 0)})  # a cut rim is always closed, whatever its size
    if "holes" in repairs:
        entry["holes_closed"] = cap_loops(bm, list(bm.edges), request["max_hole_edges"])
    open_edges = [e for e in bm.edges if e.is_boundary]
    entry["open_edges_after"] = len(open_edges)
    entry["open_junctions_after"] = sum(1 for v in {v for e in open_edges for v in e.verts} if sum(1 for e in v.link_edges if e.is_boundary) > 2)
    entry["open_loops_after"] = sorted((len(loop) for loop in boundary_loops(open_edges)), reverse=True)[:10]
    for face in bm.faces:
        for loop in face.loops:
            if loop[kept].length < 0.5:  # a cap corner: no imported normal
                loop[kept] = face.normal
    bm.to_mesh(obj.data)
    bm.free()
    attribute = obj.data.attributes["kept_normal"]
    normals = [tuple(value.vector) for value in attribute.data]
    obj.data.attributes.remove(attribute)
    obj.data.normals_split_custom_set(normals)
    obj.data.update()
    entry["triangles_after"] = len(obj.data.polygons)
    report["objects"][obj.name] = entry

Path(request["out"]).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.io_pdx_mesh.export_mesh(filepath=request["out"], chk_mesh=True, chk_skel=True, chk_locs=True, chk_selected=False)
Path(request["report"]).write_text(json.dumps(report, indent=1), encoding="utf-8")
print("REPAIR_DONE", request["out"])
