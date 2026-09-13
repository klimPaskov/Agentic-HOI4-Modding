"""Exact, caller-approved coincident-vertex seam plus proven outward winding.

No positions, faces, caps, materials, rigs or actions are invented. Index topology
changes only at an explicit tiny face allowlist. Only the locked worker calls
the native entry point; the numeric planner has no Blender dependency.
"""
from __future__ import annotations

from collections import defaultdict, deque
import hashlib
import json
import math
from pathlib import Path
import re


FIELDS = {"FLOAT": "value", "INT": "value", "INT8": "value", "BOOLEAN": "value", "FLOAT_VECTOR": "vector", "FLOAT2": "vector", "FLOAT_COLOR": "color", "BYTE_COLOR": "color", "QUATERNION": "value", "FLOAT4X4": "value", "INT16_2D": "value", "INT32_2D": "value", "STRING": "value"}
INTERNAL = {".corner_vert", ".corner_edge", ".edge_verts", "custom_normal", ".custom_normal"}


def _sub(a, b): return tuple(x-y for x, y in zip(a, b))
def _cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def _dot(a, b): return sum(x*y for x, y in zip(a, b))
def _length(a): return math.sqrt(_dot(a, a))
def _unit(a):
    size = _length(a)
    if size <= 1e-14:
        raise ValueError("Ambiguous zero-area orientation reference.")
    return tuple(x/size for x in a)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest().upper()


def _indices(values, count, maximum, field):
    if not isinstance(values, list) or not 1 <= len(values) <= maximum or any(type(v) is not int or not 0 <= v < count for v in values) or values != sorted(set(values)):
        raise ValueError(f"{field} requires bounded, sorted, unique in-range indices.")
    return set(values)


def _orient_component(positions, triangles, ids):
    # Exact-position aliases are diagnostic only, independently within each
    # side of the specifically approved seam. No final vertex welding occurs.
    lookup, points, aliases = {}, [], []
    for p in positions:
        key = tuple(p)
        if key not in lookup:
            lookup[key] = len(points)
            points.append(key)
        aliases.append(lookup[key])
    edges, face_ids = defaultdict(list), set()
    for i in ids:
        f = tuple(aliases[v] for v in triangles[i])
        identity = tuple(sorted(f))
        if len(set(f)) != 3 or identity in face_ids:
            raise ValueError("Degenerate or duplicate positional face in seam component.")
        face_ids.add(identity)
        for a, b in zip(f, f[1:] + f[:1]):
            edges[tuple(sorted((a, b)))].append((i, a, b))
    adjacency = defaultdict(list)
    for rows in edges.values():
        if len(rows) > 2:
            raise ValueError("Nonmanifold positional edge inside an approved seam side.")
        if len(rows) == 2:
            a, b = rows
            parity = int(a[1:] == b[1:])
            adjacency[a[0]].append((b[0], parity))
            adjacency[b[0]].append((a[0], parity))
    flips, queue = {min(ids): False}, deque([min(ids)])
    while queue:
        f = queue.popleft()
        for neighbor, parity in adjacency[f]:
            wanted = bool(flips[f] ^ parity)
            if neighbor in flips and flips[neighbor] != wanted:
                raise ValueError(f"Approved seam leaves a genuine orientation conflict: {f}/{neighbor}.")
            if neighbor not in flips:
                flips[neighbor] = wanted
                queue.append(neighbor)
    if len(flips) != len(ids):
        raise ValueError("Each approved seam side must be one exact-position face component.")
    oriented = {i: tuple(reversed(triangles[i])) if flips[i] else triangles[i] for i in ids}
    used = {v for f in oriented.values() for v in f}
    low = [min(positions[v][axis] for v in used) for axis in range(3)]
    high = [max(positions[v][axis] for v in used) for axis in range(3)]
    origin = tuple((a+b)/2 for a, b in zip(low, high))
    normals = {i: _cross(_sub(positions[f[1]], positions[f[0]]), _sub(positions[f[2]], positions[f[0]])) for i, f in oriented.items()}
    if any(_length(n) <= 1e-14 for n in normals.values()):
        raise ValueError("Near-zero area face is ambiguous for winding repair.")
    area = sum(_length(n)/2 for n in normals.values())
    volume = sum(_dot(_sub(positions[f[0]], origin), _cross(_sub(positions[f[1]], origin), _sub(positions[f[2]], origin)))/6 for f in oriented.values())
    boundary = []
    for rows in edges.values():
        if len(rows) == 1:
            f, a, b = rows[0]
            boundary.append((b, a) if flips[f] else (a, b))
    incoming, outgoing, graph = defaultdict(list), defaultdict(list), defaultdict(set)
    for a, b in boundary:
        outgoing[a].append(b)
        incoming[b].append(a)
        graph[a].add(b)
        graph[b].add(a)
    if any(len(outgoing[v]) != len(incoming[v]) for v in graph):
        raise ValueError("Open component boundary is not balanced and cyclic.")
    unseen, records, area_bound, volume_bound = set(graph), [], 0., 0.
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        group, queue = {seed}, deque([seed])
        while queue:
            for neighbor in graph[queue.popleft()]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    group.add(neighbor)
                    queue.append(neighbor)
        local = [points[v] for v in group]
        low = [min(p[axis] for p in local) for axis in range(3)]
        high = [max(p[axis] for p in local) for axis in range(3)]
        diameter = _length(_sub(high, low))
        perimeter = sum(_length(_sub(points[a], points[b])) for a, b in boundary if a in group)
        cap_area = perimeter*diameter/2
        cap_volume = cap_area*max(_length(_sub(p, origin)) for p in local)/3
        area_bound += cap_area
        volume_bound += cap_volume
        records.append({"vertices": len(group), "edges": sum(a in group for a, b in boundary), "branched_vertices": sum(len(graph[v]) > 2 for v in group), "cap_area_bound": cap_area, "cap_volume_bound": cap_volume})
    return flips, normals, {"faces": len(ids), "surface_area": area, "oriented_volume_about_bbox_center": volume, "boundary_edges": len(boundary), "boundary_components": records, "cap_area_upper_bound": area_bound, "cap_area_bound_ratio": area_bound/area, "cap_volume_absolute_upper_bound": volume_bound, "closed_volume_interval": [volume-volume_bound, volume+volume_bound]}


def plan_seam_winding(positions, triangles, seam_face_indices, neighbor_reference_face_indices):
    if not 4 <= len(positions) <= 1000000 or not 4 <= len(triangles) <= 200000:
        raise ValueError("Seam winding requires bounded nonempty triangle geometry.")
    if any(len(p) != 3 or any(type(x) not in (int, float) or not math.isfinite(x) for x in p) for p in positions):
        raise ValueError("Positions must be exact finite triples.")
    if any(len(f) != 3 or any(type(v) is not int or not 0 <= v < len(positions) for v in f) for f in triangles):
        raise ValueError("Faces must be indexed triangles.")
    selected = _indices(seam_face_indices, len(triangles), 8, "seam_face_indices")
    neighbors = _indices(neighbor_reference_face_indices, len(triangles), 16, "neighbor_reference_face_indices")
    if selected & neighbors:
        raise ValueError("Patch orientation references must lie in the body.")
    inside = {v for i in selected for v in triangles[i]}
    outside = {v for i, f in enumerate(triangles) if i not in selected for v in f}
    duplicate = sorted(inside & outside)
    if len(duplicate) > 24:
        raise ValueError("Seam exceeds the tiny duplicated-vertex budget.")
    patch_edges = {frozenset((tuple(positions[a]), tuple(positions[b]))) for i in selected for a, b in zip(triangles[i], triangles[i][1:]+triangles[i][:1])}
    for i in neighbors:
        edges = {frozenset((tuple(positions[a]), tuple(positions[b]))) for a, b in zip(triangles[i], triangles[i][1:]+triangles[i][:1])}
        if not patch_edges & edges:
            raise ValueError("Every orientation reference must share an exact spatial edge with the patch.")
    body_flips, body_normals, body = _orient_component(positions, triangles, [i for i in range(len(triangles)) if i not in selected])
    if body["cap_area_bound_ratio"] > 0.005:
        raise ValueError("Body hypothetical cap bound exceeds 0.5 percent of the surface; no outward assumption.")
    lower, upper = body["closed_volume_interval"]
    if lower <= 0 <= upper:
        raise ValueError("Body outward volume sign is not robust to local hypothetical caps.")
    if upper < 0:
        body_flips = {i: not flip for i, flip in body_flips.items()}
        body_normals = {i: tuple(-v for v in n) for i, n in body_normals.items()}
    body["outward_sign_basis"] = "entire_conservative_local_cap_volume_interval_has_one_sign; no_final_caps"
    patch_flips, patch_normals, patch = _orient_component(positions, triangles, sorted(selected))
    reference = _unit(tuple(sum(body_normals[i][axis] for i in sorted(neighbors)) for axis in range(3)))
    patch_vector = _unit(tuple(sum(n[axis] for n in patch_normals.values()) for axis in range(3)))
    alignment = _dot(reference, patch_vector)
    if alignment < 0:
        patch_flips = {i: not flip for i, flip in patch_flips.items()}
        patch_normals = {i: tuple(-v for v in n) for i, n in patch_normals.items()}
    per_face = {str(i): _dot(reference, _unit(n)) for i, n in patch_normals.items()}
    if abs(alignment) < 0.95 or min(per_face.values()) < 0.5:
        raise ValueError("Patch does not unambiguously align to the explicit outward neighboring faces.")
    patch.update(neighbor_reference_faces=sorted(neighbors), neighbor_reference_direction=list(reference), area_weighted_reference_alignment=abs(alignment), per_face_reference_alignment=per_face)
    flips = sorted(i for mapping in (body_flips, patch_flips) for i, flip in mapping.items() if flip)
    return {"duplicate_vertex_indices": duplicate, "duplicate_vertex_map": {old: len(positions)+i for i, old in enumerate(duplicate)}, "body": body, "patch": patch, "flip_face_indices": flips, "flip_face_indices_sha256": _digest(flips)}


def _attributes(api, mesh):
    result = {}
    for attr in mesh.attributes:
        if attr.name in INTERNAL:
            continue
        if attr.data_type not in FIELDS or attr.domain not in {"POINT", "EDGE", "FACE", "CORNER"}:
            raise ValueError("Unsupported attribute in exact seam retention proof.")
        result[attr.name] = {"domain": attr.domain, "type": attr.data_type, "values": [api._promotion_value(getattr(item, FIELDS[attr.data_type])) for item in attr.data]}
    return result


def _surface_record(api, obj, original_vertices, original_edges, reverse_vertices, reverse_edges):
    mesh = obj.data
    attrs = _attributes(api, mesh)
    corner = [(f.index, reverse_vertices.get(mesh.loops[i].vertex_index, mesh.loops[i].vertex_index), i) for f in mesh.polygons for i in f.loop_indices]
    for row in attrs.values():
        values = row["values"]
        if row["domain"] == "CORNER":
            row["values"] = sorted((face, vertex, values[i]) for face, vertex, i in corner)
        elif row["domain"] in {"POINT", "EDGE"}:
            reverse, length = (reverse_vertices, original_vertices) if row["domain"] == "POINT" else (reverse_edges, original_edges)
            if len(values) != length+len(reverse) or any(values[new] != values[old] for new, old in reverse.items()):
                raise RuntimeError("A seam duplicate failed exact attribute-copy retention.")
            row["values"] = values[:length]
    positions = [list(v.co) for v in mesh.vertices]
    weights = [[(g.group, g.weight) for g in v.groups] for v in mesh.vertices]
    if len(positions) != original_vertices+len(reverse_vertices) or any(positions[new] != positions[old] or weights[new] != weights[old] for new, old in reverse_vertices.items()):
        raise RuntimeError("A seam duplicate changed spatial coordinates or deform weights.")
    edges = [(sorted(reverse_vertices.get(v, v) for v in e.vertices), e.use_seam, e.use_edge_sharp) for e in mesh.edges]
    if len(edges) != original_edges+len(reverse_edges) or any(edges[new] != edges[old] for new, old in reverse_edges.items()):
        raise RuntimeError("A seam duplicate changed edge association/settings.")
    face_edges = []
    for face in mesh.polygons:
        ids = list(face.loop_indices)
        rows = []
        for i, next_i in zip(ids, ids[1:]+ids[:1]):
            loop, next_loop = mesh.loops[i], mesh.loops[next_i]
            if set(mesh.edges[loop.edge_index].vertices) != {loop.vertex_index, next_loop.vertex_index}:
                raise RuntimeError("Native seam loop references an incoherent edge.")
            rows.append(reverse_edges.get(loop.edge_index, loop.edge_index))
        face_edges.append(sorted(rows))
    return {"positions": positions[:original_vertices], "weights": weights[:original_vertices], "edges": edges[:original_edges], "faces": [(sorted(reverse_vertices.get(v, v) for v in f.vertices), f.material_index, f.use_smooth) for f in mesh.polygons], "face_edge_associations": face_edges, "uv_associations": {layer.name: sorted((face, vertex, list(layer.data[i].uv)) for face, vertex, i in corner) for layer in mesh.uv_layers}, "attributes": attrs}


def _fingerprint(api, job, obj, nv, ne, reverse_vertices, reverse_edges):
    result = api._promotion_fingerprint(job, [obj.name], include_sections=True)
    sections = result.pop("sections")
    row = sections["geometry"][obj.name]
    for key in ("vertices", "positions_normals", "edges", "topology", "loops_normals", "uvs", "weights", "attributes"):
        row.pop(key)
    row["exact_surface_corner_attribute_invariants"] = api._promotion_digest(_surface_record(api, obj, nv, ne, reverse_vertices, reverse_edges))
    result["mesh_counts"][obj.name]["vertices"] = nv
    result["sha256"] = {key: api._promotion_digest(value) for key, value in sections.items()}
    return result


def _duplicate_seam(api, obj, selected, duplicate_map):
    mesh = obj.data
    attrs = _attributes(api, mesh)
    coords = {old: tuple(mesh.vertices[old].co) for old in duplicate_map}
    weights = {old: [(g.group, g.weight) for g in mesh.vertices[old].groups] for old in duplicate_map}
    edges = [(tuple(e.vertices), e.use_seam, e.use_edge_sharp) for e in mesh.edges]
    consumers = defaultdict(set)
    for f in mesh.polygons:
        for i in f.loop_indices:
            consumers[mesh.loops[i].edge_index].add(f.index)
    shared = sorted(e for e, faces in consumers.items() if faces & selected and faces-selected)
    duplicate_edges = {old: len(edges)+i for i, old in enumerate(shared)}
    mesh.vertices.add(len(duplicate_map))
    for old, new in duplicate_map.items():
        mesh.vertices[new].co = coords[old]
        for group, weight in weights[old]:
            obj.vertex_groups[group].add([new], weight, "REPLACE")
    mesh.edges.add(len(duplicate_edges))
    for old, row in enumerate(edges):
        vertices, seam, sharp = row
        if consumers[old] & selected:
            target = duplicate_edges.get(old, old)
            mesh.edges[target].vertices = [duplicate_map.get(v, v) for v in vertices]
            mesh.edges[target].use_seam = seam
            mesh.edges[target].use_edge_sharp = sharp
    for name, row in attrs.items():
        mapping = duplicate_map if row["domain"] == "POINT" else duplicate_edges if row["domain"] == "EDGE" else {}
        for old, new in mapping.items():
            setattr(mesh.attributes[name].data[new], FIELDS[row["type"]], row["values"][old])
    for face_id in sorted(selected):
        for i in mesh.polygons[face_id].loop_indices:
            loop = mesh.loops[i]
            loop.vertex_index = duplicate_map.get(loop.vertex_index, loop.vertex_index)
            loop.edge_index = duplicate_edges.get(loop.edge_index, loop.edge_index)
    mesh.update()
    return duplicate_edges


def _normal_record(mesh, reverse_vertices):
    return {(f.index, reverse_vertices.get(mesh.loops[i].vertex_index, mesh.loops[i].vertex_index)): tuple(mesh.corner_normals[i].vector) for f in mesh.polygons for i in f.loop_indices}


def _normal_proof(mesh, original, flipped, reverse):
    current = _normal_record(mesh, reverse)
    if set(current) != set(original):
        raise RuntimeError("Normal correction changed face-corner identity.")
    maximum = max(_length(_sub(value, tuple((-1 if key[0] in flipped else 1)*x for x in original[key]))) for key, value in current.items())
    if maximum > 0.001:
        raise RuntimeError(f"Normal sign retention failed beyond native custom-normal quantization: {maximum}.")
    return {"corners": len(current), "maximum_vector_error": maximum, "tolerance": 0.001}


def _deformation_proof(api, obj, rig, duplicate_map):
    bpy, scene = api.bpy, api.bpy.context.scene
    animation = rig.animation_data
    if animation is None or animation.drivers or animation.nla_tracks:
        raise ValueError("Seam deformation requires existing action binding without drivers/NLA.")
    old_action, old_slot = animation.action, getattr(animation, "action_slot", None)
    old_frame, old_subframe = scene.frame_current, scene.frame_subframe
    actions = list(bpy.data.actions)
    ranges = {a.name: (int(a.frame_range[0]), int(a.frame_range[1])) for a in actions}
    if not actions or any(len(getattr(a, "slots", [])) > 1 for a in actions) or sum(end-start+1 for start, end in ranges.values()) > 3600:
        raise ValueError("Seam deformation action inventory exceeds the bounded exact-slot frame contract.")
    result = []
    try:
        for action in actions:
            animation.action = action
            if getattr(action, "slots", []):
                animation.action_slot = action.slots[0]
            start, end = ranges[action.name]
            maximum = 0.
            for frame in range(start, end+1):
                scene.frame_set(frame)
                bpy.context.view_layer.update()
                graph = bpy.context.evaluated_depsgraph_get()
                evaluated_obj = obj.evaluated_get(graph)
                evaluated = evaluated_obj.to_mesh(preserve_all_data_layers=True, depsgraph=graph)
                try:
                    if len(evaluated.vertices) != len(obj.data.vertices):
                        raise RuntimeError("Seam deformation changed vertex-index correspondence.")
                    for old, new in duplicate_map.items():
                        delta = _length(_sub(evaluated.vertices[old].co, evaluated.vertices[new].co))
                        maximum = max(maximum, delta)
                finally:
                    evaluated_obj.to_mesh_clear()
            if maximum != 0:
                raise RuntimeError("Coincident copied seam vertices diverge during skeletal deformation.")
            result.append({"action": action.name, "native_action_sha256": api._mesh_region_action_hash(action), "frames": [start, end], "every_integer_frame": True, "duplicate_pairs": len(duplicate_map), "maximum_position_delta": maximum})
    finally:
        animation.action = old_action
        if old_slot is not None:
            animation.action_slot = old_slot
        scene.frame_set(old_frame, subframe=old_subframe)
        bpy.context.view_layer.update()
    return result


def repair_mesh_winding_seam(req, api):
    payload, job = req["payload"], Path(req["job_root"]).resolve()
    fields = {"blend_rel", "expected_source_sha256", "checkpoint_rel", "target_armature_name", "target_mesh_name", "seam_face_indices", "expected_duplicate_vertex_indices", "neighbor_reference_face_indices", "expected_flip_face_indices_sha256"}
    if set(payload) != fields:
        raise ValueError("Seam repair accepts only its explicitly approved source/face/reference/hash contract.")
    source = api._promotion_path(job, payload["blend_rel"], ".blend")
    output = api._promotion_path(job, payload["checkpoint_rel"], ".blend", missing=True)
    for key in ("expected_source_sha256", "expected_flip_face_indices_sha256"):
        if not isinstance(payload[key], str) or re.fullmatch(r"[A-Fa-f0-9]{64}", payload[key]) is None:
            raise ValueError("Seam repair requires exact source and approved flip-list SHA256 values.")
    expected = payload["expected_source_sha256"].upper()
    if api.file_sha256(source) != expected or source.parent != output.parent or output.exists():
        raise ValueError("Seam repair requires matching immutable source and a new sibling checkpoint.")
    for key in ("target_armature_name", "target_mesh_name"):
        api._locator_exact_name(payload[key], key)
    report_path = job/"blender"/"reports"/f"{output.stem}_seam_winding.json"
    if report_path.exists():
        raise ValueError("Seam report already exists; use a new checkpoint name.")
    report = {"operation": "repair_mesh_winding_seam", "status": "fail", "source": payload["blend_rel"], "source_sha256": expected, "checkpoint": payload["checkpoint_rel"], "policy": "approved_coincident_attribute_vertex_seam_and_face_winding; spatial_surface_preserved; index_topology_not_byte_identical", "no_final_caps": True, "new_provider_call": False}
    try:
        bpy = api.bpy
        bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
        obj, rig = (bpy.context.scene.objects.get(payload[key]) for key in ("target_mesh_name", "target_armature_name"))
        if obj is None or rig is None or obj.type != "MESH" or rig.type != "ARMATURE" or set(o.name for o in api.mesh_objects()) != {obj.name}:
            raise ValueError("Seam repair requires exactly the named working mesh and existing rig.")
        for block in (obj, rig):
            if block.library or block.override_library or block.data.library or block.get("hoi4_source_protected") or block.get("hoi4_reference_read_only") or block.matrix_world.determinant() <= 0:
                raise ValueError("Seam repair rejects linked/protected/nonpositive target data.")
        mesh = obj.data
        if mesh.users != 1 or mesh.shape_keys or len(obj.modifiers) != 1 or obj.modifiers[0].type != "ARMATURE" or obj.modifiers[0].object != rig:
            raise ValueError("Seam repair requires unshared triangular data and one exact existing armature modifier.")
        positions, faces = [tuple(obj.matrix_world @ v.co) for v in mesh.vertices], [tuple(f.vertices) for f in mesh.polygons]
        plan = plan_seam_winding(positions, faces, payload["seam_face_indices"], payload["neighbor_reference_face_indices"])
        report["plan"] = plan
        if payload["expected_duplicate_vertex_indices"] != plan["duplicate_vertex_indices"] or plan["flip_face_indices_sha256"] != payload["expected_flip_face_indices_sha256"].upper():
            raise ValueError("Native source seam/flip plan differs from the explicitly approved numerical proposal.")
        nv, ne = len(mesh.vertices), len(mesh.edges)
        report["counts_before"] = {"vertices": nv, "edges": ne, "triangles": len(faces), "unique_positions": len(set(positions))}
        before = _fingerprint(api, job, obj, nv, ne, {}, {})
        report["fingerprints_before"] = before
        original_normals = _normal_record(mesh, {})
        original_faces = [tuple(f.vertices) for f in mesh.polygons]
        duplicate_map = plan["duplicate_vertex_map"]
        reverse = {new: old for old, new in duplicate_map.items()}
        selected = set(payload["seam_face_indices"])
        duplicate_edges = _duplicate_seam(api, obj, selected, duplicate_map)
        reverse_edges = {new: old for old, new in duplicate_edges.items()}
        report["duplicate_edge_map"] = duplicate_edges
        if any(tuple(f.vertices) != original_faces[f.index] for f in mesh.polygons if f.index not in selected):
            raise RuntimeError("Seam changed nonselected face indices before winding correction.")
        report["fingerprints_after_seam"] = _fingerprint(api, job, obj, nv, ne, reverse, reverse_edges)
        if report["fingerprints_after_seam"] != before:
            raise RuntimeError("Native seam violated exact pre-orientation corner/attribute/rig/action/material invariants.")
        flipped = set(plan["flip_face_indices"])
        for index in sorted(flipped):
            mesh.polygons[index].flip()
        mesh.update()
        desired = [None]*len(mesh.loops)
        for f in mesh.polygons:
            for i in f.loop_indices:
                old = reverse.get(mesh.loops[i].vertex_index, mesh.loops[i].vertex_index)
                desired[i] = tuple((-1 if f.index in flipped else 1)*v for v in original_normals[(f.index, old)])
        mesh.normals_split_custom_set(desired)
        mesh.update()
        report["normal_sign_proof"] = _normal_proof(mesh, original_normals, flipped, reverse)
        after_plan = plan_seam_winding([tuple(obj.matrix_world @ v.co) for v in mesh.vertices], [tuple(f.vertices) for f in mesh.polygons], payload["seam_face_indices"], payload["neighbor_reference_face_indices"])
        if after_plan["flip_face_indices"] or after_plan["duplicate_vertex_indices"]:
            raise RuntimeError("Repaired mesh is not outward or its exact seam remains joined.")
        report["verified_outward_plan"] = after_plan
        report["deformation_continuity"] = _deformation_proof(api, obj, rig, duplicate_map)
        changed = _fingerprint(api, job, obj, nv, ne, reverse, reverse_edges)
        report["fingerprints_after"] = changed
        if changed != before:
            raise RuntimeError("Seam/winding correction changed protected data beyond approved index topology and normal signs.")
        if api.file_sha256(source) != expected or output.exists():
            raise RuntimeError("Immutable seam source/output guard changed.")
        if "FINISHED" not in bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, relative_remap=False):
            raise RuntimeError("Seam checkpoint save failed.")
        bpy.ops.wm.open_mainfile(filepath=str(output), use_scripts=False)
        obj, rig = bpy.data.objects[payload["target_mesh_name"]], bpy.data.objects[payload["target_armature_name"]]
        reopened = _fingerprint(api, job, obj, nv, ne, reverse, reverse_edges)
        report["fingerprints_reopened"] = reopened
        report["reopen_comparison"] = api._promotion_reopen_comparison(changed, reopened)
        if not report["reopen_comparison"]["accepted"]:
            raise RuntimeError("Saved/reopened seam invariants differ.")
        report["reopened_normal_sign_proof"] = _normal_proof(obj.data, original_normals, flipped, reverse)
        report["reopened_deformation_continuity"] = _deformation_proof(api, obj, rig, duplicate_map)
        report["counts_after"] = {"vertices": len(obj.data.vertices), "edges": len(obj.data.edges), "triangles": len(obj.data.polygons), "unique_positions": len({tuple(obj.matrix_world @ v.co) for v in obj.data.vertices})}
        if api.file_sha256(source) != expected:
            raise RuntimeError("Seam immutable source changed.")
        report.update(status="pass", source_immutable=True, checkpoint_sha256=api.file_sha256(output), checkpoint_bytes=output.stat().st_size)
    except Exception as exc:
        report.update(error=str(exc), output_approved=False)
        raise
    finally:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    return report
