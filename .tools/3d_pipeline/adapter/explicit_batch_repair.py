"""Source-bound batch winding/skin and isolated explicit corner-normal transactions.

Selections and prior values come from hash-bound reviewed JSON, never inference.
Each operation loads once, fingerprints each stage once, saves one new sibling,
and reopens once. No public route mixes repair kinds in a transaction.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import re
import struct

from explicit_skin_repair import validate_spec as validate_skin, weights
from mesh_winding_repair import _corner_normals, _geometry_invariants, _verify_normal_signs
from manual_creature_rig import winding_inventory


OPERATIONS = {"repair_explicit_mesh_winding_batch": "winding", "repair_explicit_skin_batch": "skin", "replace_explicit_corner_normals": "normals"}
MAX_MESHES = 512
MAX_ITEMS = {"winding": 200000, "skin": 200000, "normals": 4096}
SPEC_BYTE_LIMIT = 64 * 1024 * 1024


def _hash(value, label):
    if not isinstance(value, str) or re.fullmatch(r"[A-Fa-f0-9]{64}", value) is None:
        raise ValueError(label + " requires an explicit SHA-256.")
    return value.upper()


def _unit(value):
    if (not isinstance(value, list) or len(value) != 3
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in value)
            or abs(sum(v*v for v in value) - 1.0) > 1e-6):
        raise ValueError("Corner normals require explicit finite unit triples; normalization is forbidden.")
    return value


def _angle(left, right):
    la, lb = math.sqrt(sum(v*v for v in left)), math.sqrt(sum(v*v for v in right))
    if min(la, lb) < 1e-12:
        raise ValueError("Undefined normal has no verified direction.")
    return math.degrees(math.acos(max(-1.0, min(1.0, sum(a*b for a, b in zip(left, right))/(la*lb)))))


def validate_specs(spec, kind):
    if not isinstance(spec, dict) or set(spec) != {"meshes"} or not isinstance(spec["meshes"], list) or not 1 <= len(spec["meshes"]) <= MAX_MESHES:
        raise ValueError("Repair spec requires 1-512 explicitly named mesh records.")
    seen, count = set(), 0
    common = {"mesh", "rig", "topology_sha256", "selection_sha256", "review_evidence"}
    extra = {"winding": {"face_indices", "angular_tolerance_degrees"}, "skin": {"vertices"}, "normals": {"corners"}}[kind]
    for row in spec["meshes"]:
        if not isinstance(row, dict) or set(row) != common | extra:
            raise ValueError("Unexpected or missing per-mesh repair fields.")
        if not isinstance(row["mesh"], str) or row["mesh"] in seen:
            raise ValueError("Repair meshes must be explicit and unique.")
        seen.add(row["mesh"])
        for key in ("topology_sha256", "selection_sha256"):
            _hash(row[key], key)
        if not isinstance(row["review_evidence"], str) or not 10 <= len(row["review_evidence"]) <= 4096:
            raise ValueError("Require explicit reviewed selection evidence.")
        if kind == "skin":
            validate_skin({key: value for key, value in row.items() if key != "selection_sha256"})
            for entry in row["vertices"]:
                if any(struct.unpack("<f", struct.pack("<f", value))[0] <= 0 for key in ("expected", "replacement") for value in entry[key].values()):
                    raise ValueError("Explicit skin weight underflows native float32 to zero; supply a reviewed representable map.")
            count += len(row["vertices"])
        elif kind == "winding":
            ids, tolerance = row["face_indices"], row["angular_tolerance_degrees"]
            if (not isinstance(ids, list) or not 1 <= len(ids) <= 100000
                    or any(type(i) is not int or not 0 <= i < 1000000 for i in ids) or len(set(ids)) != len(ids)):
                raise ValueError("Require unique bounded explicit face indices.")
            if type(tolerance) not in (int, float) or not math.isfinite(tolerance) or not 0 < tolerance <= 0.5:
                raise ValueError("Native winding tolerance must be positive and at most 0.5 degrees.")
            count += len(ids)
        else:
            corners = row["corners"]
            if not isinstance(corners, list) or not 1 <= len(corners) <= MAX_ITEMS[kind]:
                raise ValueError("Require bounded explicit corner replacements.")
            selected = set()
            for corner in corners:
                if not isinstance(corner, dict) or set(corner) != {"face_index", "corner_index", "vertex_index", "expected_before", "requested_after"}:
                    raise ValueError("Require exact face/corner/vertex and expected/requested vectors.")
                for key in ("face_index", "corner_index", "vertex_index"):
                    if type(corner[key]) is not int or not 0 <= corner[key] < 1000000:
                        raise ValueError("Corner identifiers must be bounded integer indices.")
                key = (corner["face_index"], corner["corner_index"])
                if key in selected:
                    raise ValueError("Duplicate selected corner.")
                selected.add(key)
                if _unit(corner["expected_before"]) == _unit(corner["requested_after"]):
                    raise ValueError("No-op corner replacements are forbidden.")
            count += len(corners)
    if count > MAX_ITEMS[kind]:
        raise ValueError("Repair selection exceeds the aggregate transaction budget.")
    return spec["meshes"]


def selection_records(obj, kind, row):
    """Canonical selected precondition input; digest with _promotion_digest, no rounding."""
    mesh = obj.data
    if kind == "winding":
        return [{"face": i, "vertices": list(mesh.polygons[i].vertices),
                 "normals": [list(mesh.corner_normals[j].vector) for j in mesh.polygons[i].loop_indices]} for i in sorted(row["face_indices"])]
    if kind == "skin":
        actual = weights(obj)
        return [{"index": entry["index"], "weights": sorted(actual[entry["index"]].items())} for entry in sorted(row["vertices"], key=lambda value: value["index"])]
    result = []
    for entry in sorted(row["corners"], key=lambda value: (value["face_index"], value["corner_index"])):
        face = mesh.polygons[entry["face_index"]]
        loop = face.loop_indices[entry["corner_index"]]
        result.append({"face": face.index, "corner": entry["corner_index"], "vertex": mesh.loops[loop].vertex_index, "normal": list(mesh.corner_normals[loop].vector)})
    return result


def raw_normals(mesh):
    attributes = [a for a in mesh.attributes if a.name in {"custom_normal", ".custom_normal"}]
    if len(attributes) != 1 or attributes[0].domain != "CORNER" or attributes[0].data_type != "INT16_2D" or len(attributes[0].data) != len(mesh.loops):
        raise ValueError("Selected normal repair requires existing native CORNER INT16_2D custom-normal storage.")
    attribute = attributes[0]
    return {"name": attribute.name, "domain": attribute.domain, "type": attribute.data_type, "values": [list(item.value) for item in attribute.data]}


def _target(api, row):
    for key in ("mesh", "rig"):
        api._locator_exact_name(row[key], key)
    obj, rig = api.bpy.context.scene.objects.get(row["mesh"]), api.bpy.context.scene.objects.get(row["rig"])
    if obj is None or obj.type != "MESH" or rig is None or rig.type != "ARMATURE":
        raise ValueError("Require exact existing scene mesh and armature.")
    for target in (obj, rig):
        for block in (target, target.data):
            if (block.library or block.override_library or block.get("hoi4_source_protected") or block.get("hoi4_reference_read_only")):
                raise ValueError("Linked, overridden or protected repair targets are forbidden.")
        if not target.get("hoi4_working") or target.constraints or target.matrix_world.determinant() <= 0:
            raise ValueError("Require approved working targets with positive nonsingular transforms.")
    if obj.data.users != 1 or obj.data.shape_keys or obj.animation_data or obj.data.animation_data:
        raise ValueError("Shared, shape-key or animated mesh data requires a separate repair contract.")
    if len(obj.modifiers) != 1 or obj.modifiers[0].type != "ARMATURE" or obj.modifiers[0].object != rig:
        raise ValueError("Require the exact existing armature modifier.")
    if api._mesh_region_topology(obj.data) != row["topology_sha256"].upper():
        raise ValueError("Exact topology precondition mismatch.")
    return obj, rig


def preflight_mesh(api, row, kind):
    obj, rig = _target(api, row)
    mesh = obj.data
    original = {"spec": row, "topology_before": row["topology_sha256"].upper()}
    if kind == "skin":
        old = weights(obj)
        groups = set(obj.vertex_groups.keys())
        bones = {b.name for b in rig.data.bones if b.use_deform}
        for entry in row["vertices"]:
            if entry["index"] >= len(old) or not (set(entry["expected"]) | set(entry["replacement"])) <= (groups & bones):
                raise ValueError("Unknown selected vertex or missing existing deform group/bone.")
            actual = old[entry["index"]]
            if set(actual) != set(entry["expected"]) or any(abs(actual[b] - v) > 1e-7 for b, v in entry["expected"].items()):
                raise ValueError("Selected skin prior values differ from the reviewed expectations.")
        original.update(weights=old, selected={entry["index"] for entry in row["vertices"]})
    elif kind == "winding":
        if max(row["face_indices"]) >= len(mesh.polygons) or any(len(face.vertices) != 3 for face in mesh.polygons):
            raise ValueError("Winding requires existing selected faces and triangular topology.")
        normals = _corner_normals(mesh)
        if any(sum(v*v for v in normal) < 1e-24 for normal in normals.values()):
            raise ValueError("Undefined source corners require a separately explicit normal repair.")
        original.update(normals=normals, faces=[list(face.vertices) for face in mesh.polygons],
            geometry=_geometry_invariants(api, obj), selected=set(row["face_indices"]), winding=winding_inventory(mesh),
            edge_sharp=[edge.use_edge_sharp for edge in mesh.edges], had_sharp_edge="sharp_edge" in mesh.attributes)
    else:
        raw = raw_normals(mesh)
        selected = set()
        for entry in row["corners"]:
            if entry["face_index"] >= len(mesh.polygons):
                raise ValueError("Unknown selected face.")
            face = mesh.polygons[entry["face_index"]]
            if entry["corner_index"] >= face.loop_total:
                raise ValueError("Unknown face-corner index.")
            loop = face.loop_indices[entry["corner_index"]]
            actual = list(mesh.corner_normals[loop].vector)
            length = math.sqrt(sum(v*v for v in actual))
            if (mesh.loops[loop].vertex_index != entry["vertex_index"] or length < 1e-12
                    or max(abs(v/length-w) for v, w in zip(actual, entry["expected_before"])) > 1e-6):
                raise ValueError("Selected corner vertex or prior unit direction mismatch.")
            selected.add(loop)
        original.update(raw=raw, normals=[list(normal.vector) for normal in mesh.corner_normals], selected=selected,
                        edge_sharp=[edge.use_edge_sharp for edge in mesh.edges], had_sharp_edge="sharp_edge" in mesh.attributes)
    preconditions = selection_records(obj, kind, row)
    if api._promotion_digest(preconditions) != row["selection_sha256"].upper():
        raise ValueError("Selected precondition SHA-256 mismatch.")
    original["selected_preconditions"] = preconditions
    return original


def _apply(api, original, kind):
    row = original["spec"]
    obj = api.bpy.data.objects[row["mesh"]]
    mesh = obj.data
    if kind == "skin":
        for entry in row["vertices"]:
            index = entry["index"]
            source_groups = [group.group for group in mesh.vertices[index].groups]
            for group_index in source_groups:
                obj.vertex_groups[group_index].remove([index])
            for bone, value in entry["replacement"].items():
                obj.vertex_groups[bone].add([index], value, "REPLACE")
    elif kind == "winding":
        uv = {layer.name: {face.index: {mesh.loops[i].vertex_index: list(layer.data[i].uv) for i in face.loop_indices} for face in mesh.polygons} for layer in mesh.uv_layers}
        for i in row["face_indices"]:
            mesh.polygons[i].flip()
        desired = [None] * len(mesh.loops)
        for face in mesh.polygons:
            sign = -1 if face.index in original["selected"] else 1
            for i in face.loop_indices:
                vertex = mesh.loops[i].vertex_index
                for layer in mesh.uv_layers:
                    layer.data[i].uv = uv[layer.name][face.index][vertex]
                value = original["normals"][(face.index, vertex)]
                length = math.sqrt(sum(v*v for v in value))
                desired[i] = [sign*v/length for v in value]
        mesh.normals_split_custom_set(desired)
        for edge, sharp in zip(mesh.edges, original["edge_sharp"]):
            edge.use_edge_sharp = sharp
    else:
        desired = copy.deepcopy(original["normals"])
        for entry in row["corners"]:
            loop = mesh.polygons[entry["face_index"]].loop_indices[entry["corner_index"]]
            desired[loop] = entry["requested_after"]
        mesh.normals_split_custom_set(desired)
        # Native encoding touches the array; restore every unselected raw short pair.
        attribute = mesh.attributes[original["raw"]["name"]]
        for i, value in enumerate(original["raw"]["values"]):
            if i not in original["selected"]:
                attribute.data[i].value = value
        for edge, sharp in zip(mesh.edges, original["edge_sharp"]):
            edge.use_edge_sharp = sharp
    if kind in {"winding", "normals"} and not original["had_sharp_edge"] and "sharp_edge" in mesh.attributes:
        mesh.attributes.remove(mesh.attributes["sharp_edge"])
    mesh.update()


def verify_mesh(api, original, kind):
    row = original["spec"]
    obj = api.bpy.data.objects[row["mesh"]]
    mesh = obj.data
    proof = {"mesh": row["mesh"], "selection_sha256": row["selection_sha256"].upper(),
             "topology_before": original["topology_before"], "topology_after": api._mesh_region_topology(mesh)}
    if kind == "skin":
        actual = weights(obj)
        if any(actual[i] != value for i, value in enumerate(original["weights"]) if i not in original["selected"]):
            raise RuntimeError("Batch skin changed an unselected weight.")
        for entry in row["vertices"]:
            current = actual[entry["index"]]
            if (set(current) != set(entry["replacement"]) or not 1 <= len(current) <= 4
                    or any(not math.isfinite(v) or v <= 0 for v in current.values()) or abs(sum(current.values())-1) > 1e-6
                    or any(abs(current[b]-v) > 1e-7 for b, v in entry["replacement"].items())):
                raise RuntimeError(f"Explicit selected replacement weights failed native verification: {obj.name} vertex {entry['index']}; requested={entry['replacement']}; actual={current}.")
        proof.update(changed_vertices=len(original["selected"]), prior_weights_sha256=api._promotion_digest(original["weights"]),
            replacement_weights_sha256=api._promotion_digest([actual[i] for i in sorted(original["selected"])]),
            untouched_weights_sha256=api._promotion_digest([value for i, value in enumerate(actual) if i not in original["selected"]]))
    elif kind == "winding":
        for face, vertices in zip(mesh.polygons, original["faces"]):
            expected = vertices[:1] + list(reversed(vertices[1:])) if face.index in original["selected"] else vertices
            if list(face.vertices) != expected:
                raise RuntimeError("Batch winding changed an unselected face or a declared face membership/orientation.")
        actual_geometry = _geometry_invariants(api, obj)
        if actual_geometry != original["geometry"]:
            changed = [key for key in actual_geometry if actual_geometry[key] != original["geometry"][key]]
            changed_attributes = [key for key in set(actual_geometry["attributes"]) | set(original["geometry"]["attributes"]) if actual_geometry["attributes"].get(key) != original["geometry"]["attributes"].get(key)]
            raise RuntimeError(f"Batch winding changed positions, attributes, materials or corner UV associations: {obj.name}, {changed}, {changed_attributes}.")
        topology = winding_inventory(mesh)
        if any(topology[key] != original["winding"][key] for key in ("boundary_edges", "nonmanifold_edges")) or topology["inconsistent_shared_edges"] > original["winding"]["inconsistent_shared_edges"]:
            raise RuntimeError("Explicit winding increased inconsistent edges or changed boundaries.")
        proof.update(face_indices=row["face_indices"], face_indices_sha256=api._promotion_digest(row["face_indices"]),
            normal_sign_proof=_verify_normal_signs(mesh, original["normals"], original["selected"], angular_tolerance_degrees=row["angular_tolerance_degrees"]))
    else:
        raw, normals = raw_normals(mesh), [list(normal.vector) for normal in mesh.corner_normals]
        if (set(raw) != set(original["raw"]) or any(raw[key] != original["raw"][key] for key in ("name", "domain", "type"))
                or len(raw["values"]) != len(original["raw"]["values"])):
            raise RuntimeError("Custom-normal storage identity changed.")
        for i in range(len(normals)):
            if i not in original["selected"] and (normals[i] != original["normals"][i] or raw["values"][i] != original["raw"]["values"][i]):
                raise RuntimeError(f"Unselected raw or decoded corner normal changed: {row['mesh']} loop {i}.")
        corners = []
        for entry in row["corners"]:
            loop = mesh.polygons[entry["face_index"]].loop_indices[entry["corner_index"]]
            angle = _angle(normals[loop], entry["requested_after"])
            if raw["values"][loop] == original["raw"]["values"][loop]:
                raise RuntimeError("Selected corner request encoded to an unchanged native raw pair.")
            if angle > 0.5:
                raise RuntimeError("Selected corner native encoding exceeds the unchanged 0.5-degree ceiling.")
            corners.append({**entry, "loop_index": loop, "original": original["normals"][loop], "encoded": normals[loop], "angle_degrees": angle,
                            "raw_before": original["raw"]["values"][loop], "raw_after": raw["values"][loop]})
        proof.update(corners=corners, derived_point_normal_vertices=sorted({mesh.loops[i].vertex_index for i in original["selected"]}),
            untouched_raw_sha256=api._promotion_digest([value for i, value in enumerate(raw["values"]) if i not in original["selected"]]),
            untouched_directions_sha256=api._promotion_digest([value for i, value in enumerate(normals) if i not in original["selected"]]))
    return proof


def project_fingerprint(api, fingerprint, originals, kind):
    result = copy.deepcopy(fingerprint)
    sections = result.pop("sections")
    for original in originals:
        name = original["spec"]["mesh"]
        obj, selected = api.bpy.data.objects[name], original["selected"]
        geometry = sections["geometry"][name]
        if kind == "skin":
            geometry["weights"] = api._promotion_digest([None if i in selected else value for i, value in enumerate(weights(obj))])
            for key in ("bounds", "dimensions"):
                sections["objects"][name].pop(key, None)
            # The same derived dimension vector is also serialized through RNA.
            # Keep all transforms and every other scalar setting exact.
            sections["objects"][name]["settings"].pop("dimensions", None)
        elif kind == "winding":
            for key in ("positions_normals", "topology", "loops_normals", "uvs", "attributes", "has_custom_normals"):
                geometry.pop(key)
            geometry["orientation_invariant"] = api._promotion_digest(_geometry_invariants(api, obj))
        else:
            raw = raw_normals(obj.data)
            # Blender derives point normals from its corner directions. Only
            # points incident to an explicitly selected corner can change.
            selected_vertices = {obj.data.loops[i].vertex_index for i in selected}
            geometry["positions_normals"] = api._promotion_digest([[list(vertex.co), None if vertex.index in selected_vertices else list(vertex.normal)] for vertex in obj.data.vertices])
            geometry["attributes"][raw["name"]]["sha256"] = api._promotion_digest([None if i in selected else value for i, value in enumerate(raw["values"])])
            geometry["loops_normals"] = api._promotion_digest([[loop.vertex_index, loop.edge_index] for loop in obj.data.loops] + [None if i in selected else list(normal.vector) for i, normal in enumerate(obj.data.corner_normals)])
    result["sha256"] = {key: api._promotion_digest(value) for key, value in sections.items()}
    return result


def inputs(req, api):
    kind = OPERATIONS[req["operation"]]
    payload, job = req["payload"], Path(req["job_root"]).resolve()
    if set(payload) != {"blend_rel", "checkpoint_rel", "expected_source_sha256", "repair_spec_rel", "expected_repair_spec_sha256"}:
        raise ValueError("Batch repair accepts only its exact source/spec hash and new sibling contract.")
    source = api._promotion_path(job, payload["blend_rel"], ".blend")
    output = api._promotion_path(job, payload["checkpoint_rel"], ".blend", missing=True)
    spec_path = api._promotion_path(job, payload["repair_spec_rel"], ".json")
    if source.parent != output.parent or output.exists() or spec_path.stat().st_size > SPEC_BYTE_LIMIT:
        raise ValueError("Require a bounded spec and new sibling checkpoint without overwrite.")
    for path, key in ((source, "expected_source_sha256"), (spec_path, "expected_repair_spec_sha256")):
        if api.file_sha256(path) != _hash(payload[key], key):
            raise ValueError("Immutable source/spec hash mismatch.")
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"), object_pairs_hook=api._promotion_unique_pairs)
    api._promotion_digest(spec)
    rows = validate_specs(spec, kind)
    report_path = job / "blender/reports" / (output.stem + "_" + req["operation"] + ".json")
    if report_path.exists():
        raise FileExistsError("Repair evidence already exists; choose a new sibling.")
    return kind, job, source, output, spec_path, rows, report_path


def run_repair(req, api):
    kind, job, source, output, spec_path, rows, report_path = inputs(req, api)
    payload = req["payload"]
    report = {"operation": req["operation"], "status": "fail", "source": payload["blend_rel"], "source_sha256": api.file_sha256(source),
        "repair_spec": payload["repair_spec_rel"], "spec_sha256": api.file_sha256(spec_path), "checkpoint": payload["checkpoint_rel"], "new_provider_call": False, "mesh_count": len(rows),
        "policy": "one_explicit_kind_all_preconditions_before_mutation_full_scene_and_unselected_data_preserved", "image_cache_stats": {}}
    try:
        api.bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
        originals = [preflight_mesh(api, row, kind) for row in rows]
        def snapshot(stage):
            stats = report["image_cache_stats"][stage] = {}
            return api._promotion_fingerprint(job, (), include_sections=True, image_cache_stats=stats)
        before = snapshot("before")
        report["full_before"] = {key: value for key, value in before.items() if key != "sections"}
        protected_before = project_fingerprint(api, before, originals, kind)
        for original in originals:
            _apply(api, original, kind)
        api.bpy.context.view_layer.update()
        report["native_mesh_proofs"] = [verify_mesh(api, original, kind) for original in originals]
        after = snapshot("after")
        protected_after = project_fingerprint(api, after, originals, kind)
        if protected_before != protected_after:
            mismatches = [key for key in protected_before["sha256"] if protected_before["sha256"][key] != protected_after["sha256"][key]]
            report.update(protected_before=protected_before, protected_after=protected_after, mismatch_sections=mismatches)
            raise RuntimeError("Repair changed full-scene or unselected data outside its exact declared kind: " + str(mismatches))
        report.update(protected_before=protected_before, protected_after=protected_after,
                      full_after={key: value for key, value in after.items() if key != "sections"})
        if (api.file_sha256(source) != report["source_sha256"] or api.file_sha256(spec_path) != report["spec_sha256"] or output.exists()):
            raise RuntimeError("Source/spec/output guard changed before save.")
        saved = api.bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, relative_remap=False)
        if "FINISHED" not in saved or not output.is_file():
            raise RuntimeError("Native sibling checkpoint save did not finish.")
        api.bpy.ops.wm.open_mainfile(filepath=str(output), use_scripts=False)
        reopened = snapshot("reopened")
        report["reopened_mesh_proofs"] = [verify_mesh(api, original, kind) for original in originals]
        report["full_reopened"] = {key: value for key, value in reopened.items() if key != "sections"}
        report["reopen_comparison"] = api._promotion_reopen_comparison(report["full_after"], report["full_reopened"])
        if not report["reopen_comparison"]["accepted"]:
            raise RuntimeError("Native saved/reopened full-scene fingerprint changed.")
        if api.file_sha256(source) != report["source_sha256"] or api.file_sha256(spec_path) != report["spec_sha256"]:
            raise RuntimeError("Immutable source/spec changed during transaction.")
        report.update(status="reopened_invariants_passed_requires_visual_export_review", source_immutable=True,
                      checkpoint_sha256=api.file_sha256(output), checkpoint_bytes=output.stat().st_size,
                      report=report_path.relative_to(job).as_posix())
    except Exception as exc:
        report.update(error=str(exc), output_approved=False)
        raise
    finally:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    return report
