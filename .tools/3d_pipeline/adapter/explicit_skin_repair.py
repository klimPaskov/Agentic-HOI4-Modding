"""SHA-bound exact-index skin repair; no geometric or procedural selection."""
import hashlib
import json
import math
import re
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest().upper()


def validate_spec(spec):
    if not isinstance(spec, dict) or set(spec) != {"mesh", "rig", "topology_sha256", "review_evidence", "vertices"}:
        raise ValueError("Require exact mesh/rig/topology_sha256/review_evidence/vertices.")
    for key in ("mesh", "rig"):
        if not isinstance(spec[key], str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", spec[key]):
            raise ValueError("Require exact safe target names.")
    if not isinstance(spec["topology_sha256"], str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", spec["topology_sha256"]):
        raise ValueError("Require inspected topology SHA-256.")
    if not isinstance(spec["review_evidence"], str) or not 10 <= len(spec["review_evidence"]) <= 4096:
        raise ValueError("Require explicit visual ownership review evidence.")
    rows = spec["vertices"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 20000:
        raise ValueError("Require 1-20000 explicitly reviewed vertices.")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"index", "expected", "replacement"}:
            raise ValueError("Vertex requires index, expected and replacement weights.")
        index = row["index"]
        if type(index) is not int or not 0 <= index < 1000000 or index in seen:
            raise ValueError("Require unique bounded exact indices.")
        seen.add(index)
        for key in ("expected", "replacement"):
            weights = row[key]
            if not isinstance(weights, dict) or not 1 <= len(weights) <= 4:
                raise ValueError("Require 1-4 named weights.")
            if any(not isinstance(b, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", b) or type(w) not in (int, float) or not math.isfinite(w) or not 0 < w <= 1 for b, w in weights.items()):
                raise ValueError("Weights must be positive finite values on named bones.")
            if abs(sum(weights.values()) - 1) > 1e-6:
                raise ValueError("Weights must sum to one; automatic normalization is forbidden.")
        if row["expected"] == row["replacement"]:
            raise ValueError("No-op rows are forbidden.")
    return spec


def weights(mesh):
    return [{mesh.vertex_groups[g.group].name: float(g.weight) for g in v.groups} for v in mesh.data.vertices]


def invariant(bpy, h, job, selected_mesh=None, selected_indices=()):
    """Everything this weight-only operation must leave intact, excluding weights."""
    sections = h["_promotion_fingerprint"](job, [], include_sections=True)["sections"]
    if selected_mesh is not None:
        mesh = bpy.context.scene.objects[selected_mesh]
        selected = set(selected_indices)
        sections["geometry"][selected_mesh]["weights"] = digest([None if i in selected else w for i, w in enumerate(weights(mesh))])
        # Deformed bounds can intentionally change after a skin repair.
        # Immutable positions/topology/normals, object matrices and every
        # other fingerprint field remain protected without normalization.
        sections["objects"][selected_mesh].pop("dimensions", None)
        sections["objects"][selected_mesh].pop("bounds", None)
    return digest(sections)


def repair_explicit_skin(req, h):
    bpy = h["bpy"]
    p = req["payload"]
    job = Path(req["job_root"]).resolve()
    source = h["within"](job, p["blend_rel"])
    output = h["within"](job, p["checkpoint_rel"], allow_missing=True)
    spec_path = h["within"](job, p["skin_spec_rel"])
    for path, expected in ((source, p["expected_source_sha256"]), (spec_path, p["expected_skin_spec_sha256"])):
        if not isinstance(expected, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", expected) or h["file_sha256"](path) != expected.upper():
            raise ValueError("Source/spec SHA-256 mismatch.")
    if source.suffix != ".blend" or output.suffix != ".blend" or output.parent != source.parent or output == source or output.exists() or spec_path.suffix != ".json" or spec_path.stat().st_size > 12000000:
        raise ValueError("Require bounded JSON and new sibling .blend.")
    report_path = job / "blender" / "reports" / (output.stem + ".json")
    if report_path.exists():
        raise FileExistsError("Repair report already exists; choose a new sibling name.")
    spec = validate_spec(json.loads(spec_path.read_text(encoding="utf-8")))
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    mesh = bpy.context.scene.objects.get(spec["mesh"])
    rig = bpy.context.scene.objects.get(spec["rig"])
    if mesh is None or mesh.type != "MESH" or rig is None or rig.type != "ARMATURE":
        raise ValueError("Exact existing mesh and rig required.")
    for obj in (mesh, rig):
        if not obj.get("hoi4_working") or obj.library or obj.override_library or obj.data.library or obj.data.users != 1 or obj.constraints or obj.get("hoi4_source_protected") or obj.get("hoi4_reference_read_only"):
            raise ValueError("Require unique local approved working targets.")
    if mesh.parent != rig or mesh.parent_type != "OBJECT" or rig.parent or mesh.data.shape_keys or mesh.animation_data or any(b.constraints for b in rig.pose.bones):
        raise ValueError("Unsupported rig/mesh dependency.")
    if len(mesh.modifiers) != 1 or mesh.modifiers[0].type != "ARMATURE" or mesh.modifiers[0].object != rig:
        raise ValueError("Require one exact Armature modifier.")
    if rig.animation_data and (rig.animation_data.drivers or rig.animation_data.nla_tracks):
        raise ValueError("Drivers/NLA require separate review.")
    if h["_mesh_region_topology"](mesh.data) != spec["topology_sha256"].upper():
        raise ValueError("Topology SHA-256 mismatch.")
    old = weights(mesh)
    selected = {r["index"] for r in spec["vertices"]}
    bone_names = {b.name for b in rig.data.bones}
    group_names = {g.name for g in mesh.vertex_groups}
    for row in spec["vertices"]:
        if row["index"] >= len(old) or not set(row["replacement"]) <= bone_names & group_names or not set(row["expected"]) <= bone_names & group_names:
            raise ValueError("Unknown vertex/bone or missing existing vertex group.")
        actual = old[row["index"]]
        if set(actual) != set(row["expected"]) or any(abs(actual[b] - w) > 1e-7 for b, w in row["expected"].items()):
            raise ValueError("Prior weights differ from explicit reviewed expectation.")
    untouched = digest([w for i, w in enumerate(old) if i not in selected])
    before = invariant(bpy, h, job, spec["mesh"], selected)
    for row in spec["vertices"]:
        index = row["index"]
        for group_index in [group.group for group in mesh.data.vertices[index].groups]:
            mesh.vertex_groups[group_index].remove([index])
        for bone, weight in row["replacement"].items():
            mesh.vertex_groups[bone].add([index], weight, "REPLACE")
    def verify():
        if invariant(bpy, h, job, spec["mesh"], selected) != before:
            raise RuntimeError("Protected geometry/material/rig/action/locator invariant changed.")
        actual = weights(bpy.context.scene.objects[spec["mesh"]])
        if digest([w for i, w in enumerate(actual) if i not in selected]) != untouched:
            raise RuntimeError("Unselected weights changed.")
        for row in spec["vertices"]:
            result = actual[row["index"]]
            if set(result) != set(row["replacement"]) or any(abs(result[b] - w) > 1e-7 for b, w in row["replacement"].items()) or abs(sum(result.values()) - 1) > 1e-6:
                raise RuntimeError("Explicit replacement weights failed verification.")
    verify()
    h["save_blend"](output)
    bpy.ops.wm.open_mainfile(filepath=str(output), use_scripts=False)
    verify()
    if h["file_sha256"](source) != p["expected_source_sha256"].upper() or h["file_sha256"](spec_path) != p["expected_skin_spec_sha256"].upper():
        raise RuntimeError("Immutable source/spec changed.")
    report = {"operation": "repair_explicit_skin", "status": "reopened_invariants_passed_requires_visual_export_review", "source": p["blend_rel"], "source_sha256": h["file_sha256"](source), "checkpoint": p["checkpoint_rel"], "checkpoint_sha256": h["file_sha256"](output), "skin_spec": p["skin_spec_rel"], "skin_spec_sha256": h["file_sha256"](spec_path), "mesh": spec["mesh"], "rig": spec["rig"], "topology_sha256": spec["topology_sha256"].upper(), "changed_vertices": len(selected), "protected_invariant_sha256": before, "untouched_weights_sha256": untouched, "reopened_verified": True, "new_provider_call": False}
    report["fingerprint_policy"] = "full_promotion_sections_only_selected_weights_and_derived_target_deformed_bounds_excluded"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report["report"] = report_path.relative_to(job).as_posix()
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def validate_selection(spec):
    if not isinstance(spec, dict) or set(spec) != {"mesh", "topology_sha256", "indices"}:
        raise ValueError("Selection requires exact mesh/topology_sha256/indices.")
    if not isinstance(spec["mesh"], str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", spec["mesh"]):
        raise ValueError("Invalid exact mesh.")
    if not isinstance(spec["topology_sha256"], str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", spec["topology_sha256"]):
        raise ValueError("Invalid topology hash.")
    indices = spec["indices"]
    if not isinstance(indices, list) or not 1 <= len(indices) <= 20000 or any(type(i) is not int or not 0 <= i < 1000000 for i in indices) or len(set(indices)) != len(indices):
        raise ValueError("Require 1-20000 unique exact source indices.")
    return spec


def preview_explicit_skin_selection(req, h):
    """Render copied rest geometry only; originals, actions and weights unchanged."""
    bpy = h["bpy"]
    p = req["payload"]
    job = Path(req["job_root"]).resolve()
    source = h["within"](job, p["blend_rel"])
    spec_path = h["within"](job, p["selection_spec_rel"])
    for path, expected in ((source, p["expected_source_sha256"]), (spec_path, p["expected_selection_spec_sha256"])):
        if not isinstance(expected, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", expected) or h["file_sha256"](path) != expected.upper():
            raise ValueError("Source/selection SHA mismatch.")
    request_id = req.get("request_id")
    if source.suffix != ".blend" or spec_path.suffix != ".json" or spec_path.stat().st_size > 1000000 or not isinstance(request_id, str) or not re.fullmatch(r"[0-9a-f]{32}", request_id):
        raise ValueError("Require bounded JSON, Blend and adapter request ID.")
    spec = validate_selection(json.loads(spec_path.read_text(encoding="utf-8")))
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    mesh = bpy.context.scene.objects.get(spec["mesh"])
    if mesh is None or mesh.type != "MESH" or mesh.library or mesh.data.library or mesh.override_library:
        raise ValueError("Require exact local mesh.")
    if h["_mesh_region_topology"](mesh.data) != spec["topology_sha256"].upper() or max(spec["indices"]) >= len(mesh.data.vertices):
        raise ValueError("Topology/indices mismatch.")
    selected = set(spec["indices"])
    full, mixed = [], []
    for face in mesh.data.polygons:
        count = sum(i in selected for i in face.vertices)
        if count == len(face.vertices):
            full.append(face.index)
        elif count:
            mixed.append(face.index)
    if not full:
        raise ValueError("No fully selected faces; revise explicit ownership selection.")
    path = job / "blender" / "reports" / ("explicit_skin_selection_" + request_id + ".json")
    if path.exists():
        raise FileExistsError(path)
    before = invariant(bpy, h, job)
    before_weights = weights(mesh)
    def component(label, faces):
        ids = sorted({i for f in faces for i in mesh.data.polygons[f].vertices})
        points = [mesh.matrix_world @ mesh.data.vertices[i].co for i in ids]
        return {"component_id": label, "polygon_indices": faces, "world_centroid": [sum(v[k] for v in points) / len(points) for k in range(3)]}
    components = [component("RED_FULLY_SELECTED", full)]
    if mixed:
        components.append(component("CYAN_MIXED_BOUNDARY", mixed))
    previews = h["_render_component_group"](job, request_id, mesh, components, ["front", "right", "three_quarter"])
    if invariant(bpy, h, job) != before or weights(mesh) != before_weights or h["file_sha256"](source) != p["expected_source_sha256"].upper() or h["file_sha256"](spec_path) != p["expected_selection_spec_sha256"].upper():
        raise RuntimeError("Read-only preview changed source or original scene.")
    report = {"operation": "preview_explicit_skin_selection", "source": p["blend_rel"], "source_sha256": p["expected_source_sha256"].upper(), "selection_spec": p["selection_spec_rel"], "selection_spec_sha256": p["expected_selection_spec_sha256"].upper(), "mesh": spec["mesh"], "topology_sha256": spec["topology_sha256"].upper(), "view_policy": "rest_mesh_copy_no_pose_deformation", "selected_indices": sorted(selected), "selected_expected_weights": {str(i): before_weights[i] for i in sorted(selected)}, "fully_selected_faces": full, "mixed_boundary_faces": mixed, "protected_invariant_sha256": before, "previews": previews, "source_immutable": True, "checkpoint_saved": False, "semantic_ownership_accepted": False}
    report["highlight_palette_rgba"] = {"RED_FULLY_SELECTED": [0.95, 0.20, 0.12, 1.0], "CYAN_MIXED_BOUNDARY": [0.15, 0.75, 1.0, 1.0]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return {k: v for k, v in report.items() if k not in {"selected_indices", "selected_expected_weights", "fully_selected_faces", "mixed_boundary_faces"}} | {"report": path.relative_to(job).as_posix(), "report_sha256": h["file_sha256"](path), "selected_vertex_count": len(selected), "fully_selected_face_count": len(full), "mixed_boundary_face_count": len(mixed)}
