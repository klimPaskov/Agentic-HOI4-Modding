"""Orientation-only repair; geometry seams, positions and attributes are retained.

Only the locked repository Blender worker invokes the native entry point.
The pure planner never adds final faces or merges final vertices.
"""
from __future__ import annotations

from collections import defaultdict, deque
import json
import math
from pathlib import Path
import re


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _area(a, b, c):
    normal = _cross(_sub(b, a), _sub(c, a))
    return math.sqrt(_dot(normal, normal)) / 2


def plan_consistent_outward_winding(positions, triangles, *, adjacency_mode="exact_positions"):
    """Use exact coincident positions for adjacency, never a final weld.

    Open shells are oriented only when every boundary is a simple 3/4-edge
    loop and virtual cap area is at most 0.5% of the component surface.
    Diagnostic cap fans close these tiny holes for a translation-independent
    signed-volume test; no cap is written to the model.
    All other open/zero-volume/nonorientable cases fail closed with evidence.
    """
    if not 1 <= len(positions) <= 1000000 or not 1 <= len(triangles) <= 200000:
        raise ValueError("Winding planner requires bounded nonempty geometry.")
    if any(len(p) != 3 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in p) for p in positions):
        raise ValueError("Winding positions must be finite numeric triples.")
    if adjacency_mode not in {"exact_positions", "source_vertex_indices"}:
        raise ValueError("Unknown winding adjacency mode.")
    aliases, welded, lookup = [], [], {}
    for point in positions:
        key = tuple(point)
        if key not in lookup:
            lookup[key] = len(welded)
            welded.append(key)
        aliases.append(lookup[key])
    exact_position_count = len(welded)
    if adjacency_mode == "source_vertex_indices":
        aliases, welded = list(range(len(positions))), [tuple(point) for point in positions]
    faces, edges, face_sets = [], defaultdict(list), set()
    for index, tri in enumerate(triangles):
        if len(tri) != 3 or any(type(v) is not int or not 0 <= v < len(positions) for v in tri):
            raise ValueError("Winding faces must be indexed triangles.")
        face = tuple(aliases[v] for v in tri)
        identity = tuple(sorted(face))
        if len(set(face)) != 3 or identity in face_sets or _area(*(welded[v] for v in face)) <= 1e-14:
            raise ValueError("Degenerate or duplicate positional triangle is ambiguous for orientation repair.")
        face_sets.add(identity)
        faces.append(face)
        for a, b in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((a, b)))].append((index, a, b))
    if any(len(rows) > 2 for rows in edges.values()):
        raise ValueError("Non-manifold positional edges are ambiguous for orientation repair.")
    adjacency = [[] for _ in faces]
    boundary_by_face = defaultdict(list)
    same = opposed = 0
    for rows in edges.values():
        if len(rows) == 1:
            face_id, a, b = rows[0]
            boundary_by_face[face_id].append((a, b))
        if len(rows) == 2:
            left, right = rows
            parity = int(left[1:] == right[1:])
            same += parity
            opposed += 1 - parity
            adjacency[left[0]].append((right[0], parity))
            adjacency[right[0]].append((left[0], parity))
    assigned, components, flips = {}, [], []
    ambiguous = []
    for seed in range(len(faces)):
        if seed in assigned:
            continue
        assigned[seed], queue, group = 0, deque([seed]), []
        contradictions = set()
        while queue:
            current = queue.popleft()
            group.append(current)
            for neighbor, parity in adjacency[current]:
                wanted = assigned[current] ^ parity
                if neighbor in assigned and assigned[neighbor] != wanted:
                    contradictions.add(tuple(sorted((current, neighbor))))
                if neighbor not in assigned:
                    assigned[neighbor] = wanted
                    queue.append(neighbor)
        oriented = {i: tuple(reversed(faces[i])) if assigned[i] else faces[i] for i in group}
        used = set(v for i in group for v in faces[i])
        low = [min(welded[v][axis] for v in used) for axis in range(3)]
        high = [max(welded[v][axis] for v in used) for axis in range(3)]
        center = tuple((a+b)/2 for a, b in zip(low, high))
        volume = sum(_dot(_sub(welded[f[0]], center), _cross(_sub(welded[f[1]], center), _sub(welded[f[2]], center))) / 6 for f in oriented.values())
        area = sum(_area(*(welded[v] for v in f)) for f in oriented.values())
        boundary = []
        for face_id in group:
            for a, b in boundary_by_face[face_id]:
                boundary.append((b, a) if assigned[face_id] else (a, b))
        loops, cap_area, cap_volume, reasons = [], 0.0, 0.0, []
        if contradictions:
            reasons.append("component_is_not_coherently_orientable")
        if boundary:
            outgoing, incoming = defaultdict(list), defaultdict(list)
            for a, b in boundary:
                outgoing[a].append(b)
                incoming[b].append(a)
            if any(len(outgoing[v]) != 1 or len(incoming[v]) != 1 for v in set(outgoing) | set(incoming)):
                reasons.append("branched_or_noncyclic_open_boundary")
            else:
                remaining = set(outgoing)
                while remaining:
                    start = current = min(remaining)
                    loop = []
                    while current in remaining:
                        remaining.remove(current)
                        loop.append(current)
                        current = outgoing[current][0]
                    if current != start or not 3 <= len(loop) <= 4:
                        reasons.append("open_boundary_is_not_a_tiny_3_or_4_edge_loop")
                    loops.append(loop)
                for loop in loops:
                    midpoint = tuple(sum(welded[v][axis] for v in loop)/len(loop) for axis in range(3))
                    for a, b in zip(loop, loop[1:] + loop[:1]):
                        cap_area += _area(midpoint, welded[b], welded[a])
                        cap_volume += _dot(_sub(midpoint, center), _cross(_sub(welded[b], center), _sub(welded[a], center))) / 6
                if cap_area / area > 0.005:
                    reasons.append("virtual_cap_area_exceeds_0.5_percent_of_surface")
        enclosed_volume = volume + cap_volume
        diagonal = math.sqrt(sum((a-b)**2 for a, b in zip(low, high)))
        if abs(enclosed_volume) <= max(1e-12, diagonal**3 * 1e-10):
            reasons.append("zero_or_numerically_ambiguous_enclosed_volume")
        component = {"component": len(components), "triangles": len(group), "positional_vertices": len(used), "boundary_edges": len(boundary), "boundary_loop_lengths": [len(loop) for loop in loops], "surface_area": area, "virtual_cap_area": cap_area, "virtual_cap_area_ratio": cap_area/area, "virtual_closed_signed_volume_before_outward_choice": enclosed_volume, "orientation_basis": "closed_signed_volume" if not boundary else "tiny_boundary_virtual_caps_for_diagnostic_signed_volume_only", "ambiguous_reasons": reasons, "orientation_conflict_count": len(contradictions), "orientation_conflict_examples": [{"face_indices": list(pair), "shared_positions": [list(welded[v]) for v in sorted(set(faces[pair[0]]) & set(faces[pair[1]]))]} for pair in sorted(contradictions)[:16]]}
        if reasons:
            ambiguous.append(component["component"])
        else:
            invert = enclosed_volume < 0
            chosen = [i for i in group if bool(assigned[i]) != invert]
            flips.extend(chosen)
            component.update(reversed_triangles=len(chosen), final_virtual_closed_volume=abs(enclosed_volume))
        components.append(component)
    return {"status": "blocked" if ambiguous else "pass", "policy": "coherent_outward_component_orientation; no final weld or virtual caps retained", "adjacency_mode": adjacency_mode, "vertices": len(positions), "exact_positional_vertices": exact_position_count, "triangles": len(faces), "edges": len(edges), "boundary_edges": sum(len(rows) == 1 for rows in edges.values()), "same_direction_shared_edges_before": same, "opposed_shared_edges_before": opposed, "components": components, "ambiguous_components": ambiguous, "flip_face_indices": sorted(flips)}


def inspect_mesh_winding(req, api):
    """Read original indexed topology and exact-position adjacency separately."""
    payload, job = req["payload"], Path(req["job_root"]).resolve()
    if set(payload) != {"blend_rel", "expected_source_sha256", "target_mesh_names"}:
        raise ValueError("Winding inspection requires only source/hash/exact mesh names.")
    source = api._promotion_path(job, payload["blend_rel"], ".blend")
    expected = payload["expected_source_sha256"]
    if not isinstance(expected, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", expected) or api.file_sha256(source) != expected.upper():
        raise ValueError("Winding inspection source SHA-256 mismatch.")
    names = payload["target_mesh_names"]
    if not isinstance(names, list) or not 1 <= len(names) <= 16 or any(not isinstance(n, str) for n in names) or len(set(names)) != len(names):
        raise ValueError("Winding inspection requires 1-16 exact unique mesh names.")
    for name in names:
        api._locator_exact_name(name, "target_mesh_names")
    api.bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    result = {"read_only": True, "checkpoint_saved": False, "source": payload["blend_rel"], "source_sha256_before": expected.upper(), "meshes": []}
    for name in names:
        obj = api.bpy.context.scene.objects.get(name)
        if obj is None or obj.type != "MESH":
            raise ValueError("Winding inspection exact mesh selection failed.")
        positions = [tuple(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices]
        faces = [tuple(face.vertices) for face in obj.data.polygons]
        row = {"name": name, "positions_sha256": api._promotion_digest(positions), "source_face_indices_sha256": api._promotion_digest(faces), "source_data_name": obj.data.name, "modifiers": [{"type": mod.type, "object": mod.object.name if getattr(mod, "object", None) else None} for mod in obj.modifiers], "plans": {}}
        for mode in ("source_vertex_indices", "exact_positions"):
            row["plans"][mode] = plan_consistent_outward_winding(positions, faces, adjacency_mode=mode)
        result["meshes"].append(row)
    result["source_sha256_after"] = api.file_sha256(source)
    if result["source_sha256_after"] != expected.upper():
        raise RuntimeError("Winding inspection source changed.")
    return result


def _geometry_invariants(api, obj):
    mesh = obj.data
    faces = list(mesh.polygons)
    corners = [(face.index, mesh.loops[index].vertex_index, index) for face in faces for index in face.loop_indices]
    fields = {"FLOAT": "value", "INT": "value", "INT8": "value", "BOOLEAN": "value", "FLOAT_VECTOR": "vector", "FLOAT2": "vector", "FLOAT_COLOR": "color", "BYTE_COLOR": "color", "QUATERNION": "value", "FLOAT4X4": "value", "INT16_2D": "value", "INT32_2D": "value", "STRING": "value"}
    attributes = {}
    for attribute in mesh.attributes:
        if attribute.name in {".corner_vert", ".corner_edge", "custom_normal", ".custom_normal"}:
            continue  # Independently checked through exact faces/edges and oriented corner normals.
        field = fields.get(attribute.data_type)
        if field is None:
            raise ValueError("Unsupported attribute in winding retention proof.")
        values = [api._promotion_value(getattr(item, field)) for item in attribute.data]
        if attribute.domain == "CORNER":
            values = sorted((face, vertex, values[index]) for face, vertex, index in corners)
        attributes[attribute.name] = {"domain": attribute.domain, "type": attribute.data_type, "data": values}
    return {"positions": [list(v.co) for v in mesh.vertices], "faces": [(sorted(f.vertices), f.material_index, f.use_smooth) for f in faces], "uv_associations": {layer.name: sorted((face, vertex, list(layer.data[index].uv)) for face, vertex, index in corners) for layer in mesh.uv_layers}, "attributes": attributes}


def _retention_fingerprint(api, job, names):
    result = api._promotion_fingerprint(job, names, include_sections=True)
    sections = result.pop("sections")
    for name in names:
        row = sections["geometry"][name]
        for key in ("positions_normals", "topology", "loops_normals", "uvs", "attributes"):
            row.pop(key)
        row["orientation_invariant_geometry"] = api._promotion_digest(_geometry_invariants(api, api.bpy.data.objects[name]))
    result["sha256"] = {key: api._promotion_digest(value) for key, value in sections.items()}
    return result


def _corner_normals(mesh):
    return {(face.index, mesh.loops[index].vertex_index): tuple(mesh.corner_normals[index].vector) for face in mesh.polygons for index in face.loop_indices}


def _verify_normal_signs(mesh, original, flipped, *, angular_tolerance_degrees=0.25):
    actual = _corner_normals(mesh)
    if set(actual) != set(original):
        raise RuntimeError("Winding correction changed corner-to-vertex associations.")
    maximum = 0.0
    maximum_angle = 0.0
    worst = None
    lengths = []
    for key, value in actual.items():
        sign = -1 if key[0] in flipped else 1
        wanted = tuple(sign*x for x in original[key])
        source_length = math.sqrt(sum(x*x for x in wanted))
        target_length = math.sqrt(sum(x*x for x in value))
        if source_length < 1e-12 or target_length < 1e-12:
            raise RuntimeError(f"Undefined corner normal requires explicit selected-face geometric replacement: {key}.")
        lengths.append(source_length)
        direction = tuple(x/source_length for x in wanted)
        target = tuple(x/target_length for x in value)
        angle = math.degrees(math.acos(max(-1.0,min(1.0,sum(a*b for a,b in zip(direction,target))))))
        error = math.sqrt(sum((x-y)**2 for x,y in zip(direction,target)))
        if angle > maximum_angle:
            worst = {"face_vertex":key,"wanted":wanted,"actual":value,"source_length":source_length,"target_length":target_length,"selected_face":key[0] in flipped,"angle_degrees":angle}
        maximum_angle = max(maximum_angle,angle)
        maximum = max(maximum,error)
    if maximum_angle > angular_tolerance_degrees:
        raise RuntimeError(f"Winding native normal serialization exceeds {angular_tolerance_degrees} degrees: {maximum_angle}; worst_corner={worst!r}.")
    return {"corners":len(actual),"maximum_vector_error":maximum,"maximum_angle_degrees":maximum_angle,"angular_tolerance_degrees":angular_tolerance_degrees,"worst_corner":worst,"source_normal_length_min":min(lengths) if lengths else None,"source_normal_length_max":max(lengths) if lengths else None,"source_nonunit_normal_count":sum(abs(x-1)>1e-5 for x in lengths),"policy":"source direction times exact face sign; measured native normalization and encode/decode angular tolerance; no broad normal reset"}


def repair_mesh_winding(req, api):
    """Exact hash/allowlist guard; new sibling checkpoint; fail-closed evidence."""
    payload, job = req["payload"], Path(req["job_root"]).resolve()
    if set(payload) != {"blend_rel", "expected_source_sha256", "checkpoint_rel", "target_armature_name", "target_mesh_names"}:
        raise ValueError("Winding repair accepts only its exact source/output/target contract.")
    source = api._promotion_path(job, payload["blend_rel"], ".blend")
    output = api._promotion_path(job, payload["checkpoint_rel"], ".blend", missing=True)
    expected = payload["expected_source_sha256"]
    if not isinstance(expected, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", expected) or api.file_sha256(source) != expected.upper():
        raise ValueError("Winding source SHA-256 mismatch.")
    if source.parent != output.parent or output.exists():
        raise ValueError("Winding repair requires a new sibling checkpoint without overwrites.")
    names = payload["target_mesh_names"]
    if not isinstance(names, list) or not 1 <= len(names) <= 16 or any(not isinstance(n, str) for n in names) or len(set(names)) != len(names):
        raise ValueError("Winding repair requires 1-16 exact unique mesh names.")
    for name in names:
        api._locator_exact_name(name, "target_mesh_names")
    api._locator_exact_name(payload["target_armature_name"], "target_armature_name")
    report_path = job / "blender" / "reports" / f"{output.stem}_winding.json"
    if report_path.exists():
        raise ValueError("Winding evidence exists; choose a new checkpoint name.")
    report = {"operation": "repair_mesh_winding", "status": "fail", "source": payload["blend_rel"], "source_sha256": expected.upper(), "checkpoint": payload["checkpoint_rel"], "new_provider_call": False, "final_geometry_added_deleted_or_welded": False, "meshes": []}
    bpy = api.bpy
    try:
        bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
        rig = bpy.context.scene.objects.get(payload["target_armature_name"])
        if rig is None or rig.type != "ARMATURE" or rig.library or rig.override_library:
            raise ValueError("Winding repair requires the exact local armature.")
        if set(obj.name for obj in api.mesh_objects()) != set(names):
            raise ValueError("Winding targets must cover exactly all approved working meshes.")
        targets = [bpy.context.scene.objects.get(name) for name in names]
        for obj in targets:
            if obj is None or obj.type != "MESH" or obj.library or obj.override_library or obj.data.library or obj.data.users != 1 or obj.get("hoi4_source_protected") or obj.get("hoi4_reference_read_only"):
                raise ValueError("Winding repair rejects missing, shared, linked or protected meshes.")
            if obj.data.shape_keys or len(obj.modifiers) != 1 or obj.modifiers[0].type != "ARMATURE" or obj.modifiers[0].object != rig or obj.matrix_world.determinant() <= 0:
                raise ValueError("Winding repair requires one exact armature modifier, no shape keys and positive transforms.")
        before = _retention_fingerprint(api, job, names)
        report["fingerprints_before"] = before
        originals, selected_faces = {}, {}
        for obj in targets:
            mesh = obj.data
            plan = plan_consistent_outward_winding([tuple(obj.matrix_world @ vertex.co) for vertex in mesh.vertices], [tuple(face.vertices) for face in mesh.polygons])
            report["meshes"].append({"name": obj.name, "plan": plan})
            if plan["status"] != "pass":
                raise RuntimeError("Ambiguous open component; no arbitrary global inversion or output approval.")
            originals[obj.name] = _corner_normals(mesh)
            selected_faces[obj.name] = set(plan["flip_face_indices"])
        for obj, row in zip(targets, report["meshes"]):
            mesh, flipped = obj.data, selected_faces[obj.name]
            for index in sorted(flipped):
                mesh.polygons[index].flip()
            mesh.update()
            desired = [None] * len(mesh.loops)
            for face in mesh.polygons:
                sign = -1 if face.index in flipped else 1
                for index in face.loop_indices:
                    source_normal = originals[obj.name][(face.index, mesh.loops[index].vertex_index)]
                    magnitude = math.sqrt(sum(x*x for x in source_normal))
                    if magnitude < 1e-12:
                        raise RuntimeError("Undefined source normal requires explicit local repair.")
                    desired[index] = tuple(sign*x/magnitude for x in source_normal)
            mesh.normals_split_custom_set(desired)
            mesh.update()
            row["normal_sign_proof"] = _verify_normal_signs(mesh, originals[obj.name], flipped)
            verification = plan_consistent_outward_winding([tuple(obj.matrix_world @ vertex.co) for vertex in mesh.vertices], [tuple(face.vertices) for face in mesh.polygons])
            row["after_plan"] = verification
            if verification["status"] != "pass" or verification["same_direction_shared_edges_before"] or verification["flip_face_indices"]:
                raise RuntimeError("Winding output is not coherently outward after correction.")
        bpy.context.view_layer.update()
        changed = _retention_fingerprint(api, job, names)
        report["fingerprints_after"] = changed
        if before != changed:
            raise RuntimeError("Winding repair changed protected data beyond permitted orientation/normal signs.")
        if api.file_sha256(source) != expected.upper() or output.exists():
            raise RuntimeError("Winding source or output guard changed during repair.")
        saved = bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, relative_remap=False)
        if "FINISHED" not in saved:
            raise RuntimeError("Winding checkpoint save failed.")
        bpy.ops.wm.open_mainfile(filepath=str(output), use_scripts=False)
        reopened = _retention_fingerprint(api, job, names)
        report["fingerprints_reopened"] = reopened
        report["reopen_comparison"] = api._promotion_reopen_comparison(changed, reopened)
        if not report["reopen_comparison"]["accepted"]:
            raise RuntimeError("Winding saved/reopened protected invariants differ.")
        for row in report["meshes"]:
            row["reopened_normal_sign_proof"] = _verify_normal_signs(bpy.data.objects[row["name"]].data, originals[row["name"]], selected_faces[row["name"]])
        if api.file_sha256(source) != expected.upper():
            raise RuntimeError("Winding immutable source changed.")
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
