"""Declarative, job-bounded repair of an existing posed humanoid.

No caller-provided Python, expressions, URLs, or absolute paths are accepted.
The source inspection is read-only. Rigging duplicates one approved static
mesh, preserves its world-space geometry/UVs, and applies explicit region skin
rules. Actions use authored pose keys and optional native two-bone hand IK,
then retain a baked skeletal action for the locked PDX exporter.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path


SCHEMA_VERSION = "1.0.0"
ROLES = {
    "idle": ("start", "quarter", "middle", "three_quarter", "end"),
    "move": ("left_contact", "left_pass", "right_contact", "right_pass", "loop"),
    "attack": ("ready", "aim", "discharge", "recoil", "recovery"),
    "defend": ("guard_start", "guard_hold", "guard_release"),
    "support_attack": ("ready", "aim", "discharge", "recoil", "recovery"),
    "retreat": ("disengage", "withdrawal", "recovery"),
    "portal_arrival": ("entry", "descent", "landing", "settle"),
    "wounded": ("ready", "impact", "reaction", "recovery"),
    "death": ("ready", "collapse", "impact", "settle"),
    "training": ("ready", "present", "inspect", "recover"),
}


def digest(path):
    with Path(path).open("rb") as stream:
        h = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def _name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,95}", value):
        raise ValueError("Names must be bounded plain identifiers.")
    return value


def _sha(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError("An explicit SHA-256 is required.")
    return value.upper()


def _vector(value, size=3, limit=1000.0):
    if not isinstance(value, list) or len(value) != size:
        raise ValueError("Incorrect vector size.")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or abs(x) > limit for x in value):
        raise ValueError("Vectors must contain finite bounded numbers.")
    return [float(x) for x in value]


def _exact(value, required, optional=()):
    if not isinstance(value, dict) or not set(required).issubset(value) or set(value) - set(required) - set(optional):
        raise ValueError("Missing or unsupported declarative fields.")


def _path(job, relative, suffix, *, new=False):
    if not isinstance(relative, str) or not relative or ":" in relative or "\\" in relative or relative.startswith("/") or ".." in relative.split("/"):
        raise ValueError("Only forward-slash job-relative paths are accepted.")
    path = (job / relative).resolve()
    path.relative_to(job)
    if path.suffix.lower() != suffix:
        raise ValueError("Incorrect file suffix.")
    if new:
        if path.exists():
            raise ValueError("New output already exists; source preservation is mandatory.")
    elif not path.is_file():
        raise FileNotFoundError(path)
    return path


def _inputs(req, with_spec=False):
    payload = req["payload"]
    required = {"blend_rel", "expected_source_sha256"}
    required |= {"spec_rel", "expected_spec_sha256", "checkpoint_rel"} if with_spec else {"mesh_name", "report_rel"}
    _exact(payload, required)
    job = Path(req["job_root"]).resolve()
    source = _path(job, payload["blend_rel"], ".blend")
    if digest(source) != _sha(payload["expected_source_sha256"]):
        raise ValueError("Source checkpoint SHA-256 mismatch.")
    spec, output = None, None
    if with_spec:
        spec_path = _path(job, payload["spec_rel"], ".json")
        if spec_path.stat().st_size > 16 * 1024 * 1024 or digest(spec_path) != _sha(payload["expected_spec_sha256"]):
            raise ValueError("Spec SHA-256/size gate failed.")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        output = _path(job, payload["checkpoint_rel"], ".blend", new=True)
        if output.parent != source.parent:
            raise ValueError("Repair checkpoints must be new siblings of their source.")
    return job, source, spec, output


def validate_rig_spec(spec):
    _exact(spec, {"schema_version", "author", "acceptance_basis", "source_mesh_name", "output_mesh_name", "rig_name", "bones", "weight_regions", "ik_chains"})
    if spec["schema_version"] != SCHEMA_VERSION or not isinstance(spec["author"], str) or not 1 <= len(spec["author"].strip()) <= 128 or not isinstance(spec["acceptance_basis"], str) or not 1 <= len(spec["acceptance_basis"]) <= 2048:
        raise ValueError("Explicit version, author and acceptance basis are required.")
    for key in ("source_mesh_name", "output_mesh_name", "rig_name"):
        _name(spec[key])
    bones = spec["bones"]
    if not isinstance(bones, list) or not 16 <= len(bones) <= 64:
        raise ValueError("Fitted humanoids require 16-64 explicitly placed bones.")
    known = set()
    roots = 0
    for bone in bones:
        _exact(bone, {"name", "head", "tail", "parent", "roll"})
        name = _name(bone["name"])
        if name in known or (bone["parent"] is not None and bone["parent"] not in known):
            raise ValueError("Bones require unique names and parent-first ordering.")
        head, tail = _vector(bone["head"]), _vector(bone["tail"])
        if math.dist(head, tail) < 0.001:
            raise ValueError("Bone length is too small.")
        _vector([bone["roll"]], 1, math.pi * 2)
        roots += bone["parent"] is None
        known.add(name)
    if roots != 1:
        raise ValueError("Exactly one root is required.")
    regions = spec["weight_regions"]
    if not isinstance(regions, list) or not 1 <= len(regions) <= 128:
        raise ValueError("Require 1-128 explicit ordered weight regions.")
    region_names = set()
    for region in regions:
        _exact(region, {"name", "selection", "skin"})
        name = _name(region["name"])
        if name in region_names:
            raise ValueError("Duplicate weight-region name.")
        region_names.add(name)
        selection = region["selection"]
        if not isinstance(selection, dict) or len(selection) != 1:
            raise ValueError("Each region uses exactly one AABB or explicit index selector.")
        if "aabb" in selection:
            box = selection["aabb"]
            _exact(box, {"min", "max"})
            if any(a > b for a, b in zip(_vector(box["min"]), _vector(box["max"]))):
                raise ValueError("Inverted AABB.")
        elif "vertex_indices" in selection:
            values = selection["vertex_indices"]
            if not isinstance(values, list) or not 1 <= len(values) <= 100000 or len(set(values)) != len(values) or any(type(x) is not int or not 0 <= x < 100000 for x in values):
                raise ValueError("Invalid explicit vertex indices.")
        else:
            raise ValueError("Unsupported weight selector.")
        skin = region["skin"]
        if not isinstance(skin, dict) or len(skin) != 1:
            raise ValueError("Choose one explicit or segment-distance skin policy.")
        if "weights" in skin:
            weights = skin["weights"]
            if not isinstance(weights, dict) or not 1 <= len(weights) <= 4 or set(weights) - known:
                raise ValueError("Weights require 1-4 existing bones.")
            values = _vector(list(weights.values()), len(weights), 1)
            if min(values) <= 0 or abs(sum(values) - 1) > 1e-6:
                raise ValueError("Weights must be positive and sum to one.")
        elif "nearest_segments" in skin:
            rule = skin["nearest_segments"]
            _exact(rule, {"bones", "influences", "softening", "power"})
            names = rule["bones"]
            if not isinstance(names, list) or not 1 <= len(names) <= 16 or len(set(names)) != len(names) or set(names) - known:
                raise ValueError("Nearest-segment policy requires a bounded explicit bone set.")
            if type(rule["influences"]) is not int or not 1 <= rule["influences"] <= min(4, len(names)):
                raise ValueError("Invalid influence limit.")
            if not 0.001 <= _vector([rule["softening"]], 1)[0] <= 2 or not 1 <= _vector([rule["power"]], 1)[0] <= 8:
                raise ValueError("Invalid skin falloff parameters.")
        else:
            raise ValueError("Unsupported skin policy.")
    chains = spec["ik_chains"]
    if not isinstance(chains, list) or len(chains) > 2:
        raise ValueError("At most two explicit hand IK chains are supported.")
    parents = {bone["name"]: bone["parent"] for bone in bones}
    def ancestors(name):
        values = set()
        while parents[name] is not None:
            name = parents[name]
            values.add(name)
        return values
    for chain in chains:
        _exact(chain, {"forearm", "target_hand", "pole", "pole_angle"}, {"pole_parent_bone"})
        if chain["forearm"] not in known or chain["target_hand"] not in known:
            raise ValueError("IK bones are absent.")
        if chain["forearm"] == chain["target_hand"] or chain["forearm"] in ancestors(chain["target_hand"]):
            raise ValueError("Hand IK target cannot depend on its own solved chain.")
        _vector(chain["pole"])
        _vector([chain["pole_angle"]], 1, math.pi * 2)
        if "pole_parent_bone" in chain and chain["pole_parent_bone"] not in known:
            raise ValueError("The declared pole parent must be an existing fitted bone.")
        if "pole_parent_bone" in chain and chain["pole_parent_bone"] not in ancestors(chain["forearm"]) & ancestors(chain["target_hand"]):
            raise ValueError("Pole parent must be a common ancestor outside the solved arm chain.")
    return spec


def validate_action_spec(spec):
    _exact(spec, {"schema_version", "author", "acceptance_basis", "rig_name", "mesh_name", "action_name", "role", "fps", "frame_start", "frame_end", "loop", "phases", "bone_keys", "grounding", "contact_bones"})
    if spec["schema_version"] != SCHEMA_VERSION or not isinstance(spec["author"], str) or not 1 <= len(spec["author"].strip()) <= 128 or not isinstance(spec["acceptance_basis"], str) or not 1 <= len(spec["acceptance_basis"]) <= 2048:
        raise ValueError("Explicit version, author and acceptance basis are required.")
    for key in ("rig_name", "mesh_name", "action_name"):
        _name(spec[key])
    role = spec["role"]
    if role not in ROLES or type(spec["fps"]) is not int or not 12 <= spec["fps"] <= 60:
        raise ValueError("Unsupported role/FPS.")
    start, end = spec["frame_start"], spec["frame_end"]
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= 600 or end - start < 12:
        raise ValueError("Action range must contain 13-601 bounded frames.")
    if type(spec["loop"]) is not bool or (role in {"death", "portal_arrival", "wounded"} and spec["loop"]):
        raise ValueError("Invalid loop policy.")
    phases = spec["phases"]
    _exact(phases, set(ROLES[role]))
    ordered = [phases[name] for name in ROLES[role]]
    if any(type(x) is not int or not start <= x <= end for x in ordered) or any(a >= b for a, b in zip(ordered, ordered[1:])):
        raise ValueError("Role-specific phases must be strictly ordered.")
    if spec["grounding"] not in {"none", "per_frame_lowest_vertex", "feet_only"}:
        raise ValueError("Unsupported explicit grounding policy.")
    if not isinstance(spec["contact_bones"], list) or len(spec["contact_bones"]) > 8:
        raise ValueError("Invalid contact-bone list.")
    for name in spec["contact_bones"]:
        _name(name)
    keys = spec["bone_keys"]
    if not isinstance(keys, dict) or not 2 <= len(keys) <= 64:
        raise ValueError("Real multi-bone skeletal keys are required.")
    total = 0
    for name, rows in keys.items():
        _name(name)
        if not isinstance(rows, list) or not 2 <= len(rows) <= 128:
            raise ValueError("Each bone requires 2-128 authored keys.")
        frames = []
        for row in rows:
            _exact(row, {"frame", "rotation_xyz_deg", "location"})
            if type(row["frame"]) is not int or not start <= row["frame"] <= end:
                raise ValueError("Action key outside range.")
            frames.append(row["frame"])
            _vector(row["rotation_xyz_deg"], 3, 180)
            _vector(row["location"], 3, 20)
        if frames[0] != start or frames[-1] != end or any(a >= b for a, b in zip(frames, frames[1:])):
            raise ValueError("Every bone requires ordered endpoint keys.")
        if spec["loop"] and (rows[0]["rotation_xyz_deg"] != rows[-1]["rotation_xyz_deg"] or rows[0]["location"] != rows[-1]["location"]):
            raise ValueError("Loop endpoints must be equal.")
        total += len(rows)
    if total > 4096:
        raise ValueError("Action exceeds the authored-key cap.")
    distinct = sum(len({tuple(row["rotation_xyz_deg"] + row["location"]) for row in rows}) > 1 for rows in keys.values())
    if distinct < 2:
        raise ValueError("Static/whole-root-only aliases are forbidden.")
    return spec


def _mesh_fingerprint(obj):
    rows = {"vertices": [[float(x) for x in obj.matrix_world @ v.co] for v in obj.data.vertices],
            "polygons": [list(p.vertices) for p in obj.data.polygons],
            "uv_layers": {layer.name: [list(item.uv) for item in layer.data] for layer in obj.data.uv_layers},
            "materials": [slot.material.name if slot.material else None for slot in obj.material_slots]}
    return rows


def inspect_source(req):
    import bpy
    import bmesh
    job, source, _, _ = _inputs(req)
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    mesh = bpy.data.objects.get(_name(req["payload"]["mesh_name"]))
    if mesh is None or mesh.type != "MESH" or mesh.library or mesh.data.library or len(mesh.data.vertices) > 100000:
        raise ValueError("One local bounded mesh is required.")
    report = _mesh_fingerprint(mesh)
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()
    boundary = [e for e in bm.edges if e.is_boundary]
    report["boundary_edges"] = [[e.verts[0].index, e.verts[1].index] for e in boundary]
    bm.free()
    if digest(source) != req["payload"]["expected_source_sha256"].upper():
        raise RuntimeError("Read-only source inspection changed protected source bytes.")
    report.update(schema_version=SCHEMA_VERSION, source=req["payload"]["blend_rel"], source_sha256=digest(source), mesh_name=mesh.name,
                  source_immutable=True, world_coordinates=True, geometry_mutated=False)
    path = _path(job, req["payload"]["report_rel"], ".json", new=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, separators=(",", ":")), encoding="utf-8")
    return {"report": path.relative_to(job).as_posix(), "report_sha256": digest(path), "vertices": len(report["vertices"]),
            "polygons": len(report["polygons"]), "boundary_edges": len(report["boundary_edges"]), "source_sha256": digest(source), "source_immutable": True}


def _save_report(job, output, report):
    path = job / "blender" / "reports" / (output.stem + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    report["checkpoint"] = output.relative_to(job).as_posix()
    report["checkpoint_sha256"] = digest(output)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def author_rig(req):
    import bpy
    from mathutils import Matrix, Vector
    job, source, spec, output = _inputs(req, True)
    validate_rig_spec(spec)
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    original = bpy.data.objects.get(spec["source_mesh_name"])
    if original is None or original.type != "MESH" or original.library or original.data.library or original.data.shape_keys or original.modifiers or original.parent:
        raise ValueError("Fitted rigging requires one unparented static local source mesh with no modifiers or shape keys.")
    if not original.get("hoi4_working") or len(original.data.vertices) > 100000 or any(v <= 0 for v in original.scale):
        raise ValueError("Source must be an approved bounded working mesh with positive transforms.")
    if bpy.data.objects.get(spec["output_mesh_name"]) or bpy.data.objects.get(spec["rig_name"]):
        raise ValueError("Output names already exist.")
    before = _mesh_fingerprint(original)
    collection = original.users_collection[0]
    mesh = original.copy()
    mesh.data = original.data.copy()
    mesh.name = spec["output_mesh_name"]
    collection.objects.link(mesh)
    world = original.matrix_world.copy()
    mesh.data.transform(world)
    mesh.matrix_world = Matrix.Identity(4)
    original["hoi4_working"] = False
    original.hide_set(True)
    original.hide_render = True
    mesh["hoi4_working"] = True
    mesh["hoi4_source_object"] = original.name
    mesh.hide_set(False)
    mesh.hide_render = False
    data = bpy.data.armatures.new(spec["rig_name"])
    rig = bpy.data.objects.new(spec["rig_name"], data)
    collection.objects.link(rig)
    rig.matrix_world = Matrix.Identity(4)
    rig["hoi4_working"] = True
    rig["hoi4_humanoid_rig"] = True
    rig["hoi4_fitted_rig_spec_sha256"] = req["payload"]["expected_spec_sha256"]
    rig["hoi4_fitted_ik_json"] = json.dumps(spec["ik_chains"])
    rig["hoi4_manual_author"] = spec["author"]
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for row in spec["bones"]:
        bone = data.edit_bones.new(row["name"])
        bone.head, bone.tail, bone.roll = row["head"], row["tail"], row["roll"]
        if row["parent"]:
            bone.parent = data.edit_bones[row["parent"]]
        bone.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    assignments = [None] * len(mesh.data.vertices)
    counts = []
    points = [v.co.copy() for v in mesh.data.vertices]
    for region in spec["weight_regions"]:
        selector, skin = region["selection"], region["skin"]
        if "vertex_indices" in selector:
            indices = selector["vertex_indices"]
            if max(indices) >= len(points):
                raise ValueError("Weight-region source vertex outside mesh.")
        else:
            box = selector["aabb"]
            indices = [i for i, p in enumerate(points) if all(a <= x <= b for a, x, b in zip(box["min"], p, box["max"]))]
        if not indices:
            raise ValueError(f"Empty measured weight region: {region['name']}")
        for i in indices:
            if "weights" in skin:
                weights = dict(skin["weights"])
            else:
                policy = skin["nearest_segments"]
                ranked = []
                for name in policy["bones"]:
                    bone = data.bones[name]
                    segment = bone.tail_local - bone.head_local
                    t = max(0, min(1, (points[i] - bone.head_local).dot(segment) / segment.length_squared))
                    distance = (points[i] - bone.head_local - t * segment).length
                    ranked.append((distance, name))
                raw = {name: 1 / (distance + policy["softening"]) ** policy["power"] for distance, name in sorted(ranked)[:policy["influences"]]}
                total = sum(raw.values())
                weights = {name: value / total for name, value in raw.items()}
            assignments[i] = weights
        counts.append({"region": region["name"], "matched_vertices": len(indices), "overrides_previous_regions": True})
    if any(item is None for item in assignments):
        raise ValueError("Uncovered deforming vertices; explicit region coverage must be complete.")
    for group in list(mesh.vertex_groups):
        mesh.vertex_groups.remove(group)
    groups = {row["name"]: mesh.vertex_groups.new(name=row["name"]) for row in spec["bones"]}
    for i, row in enumerate(assignments):
        for name, weight in row.items():
            groups[name].add([i], weight, "REPLACE")
    mesh.parent = rig
    mesh.matrix_parent_inverse = Matrix.Identity(4)
    modifier = mesh.modifiers.new("HOI4_FITTED_SKIN", "ARMATURE")
    modifier.object = rig
    after = _mesh_fingerprint(mesh)
    max_error = max(math.dist(a, b) for a, b in zip(before["vertices"], after["vertices"]))
    if max_error > 1e-5 or any(before[key] != after[key] for key in ("polygons", "uv_layers", "materials")):
        raise RuntimeError("Fitted-rig geometry/UV/material preservation failed.")
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    if digest(source) != req["payload"]["expected_source_sha256"].upper():
        raise RuntimeError("Protected source changed.")
    return _save_report(job, output, {"schema_version": SCHEMA_VERSION, "status": "authored_requires_visual_qa", "author": spec["author"], "source_sha256": digest(source),
        "spec_sha256": req["payload"]["expected_spec_sha256"].upper(), "mesh": mesh.name, "rig": rig.name, "bone_count": len(data.bones), "geometry_world_max_error": max_error,
        "vertices": len(points), "polygons": len(mesh.data.polygons), "uv_and_materials_unchanged": True, "source_immutable": True, "regions": counts,
        "zero_weight_vertices": 0, "max_influences": max(len(row) for row in assignments), "weight_assignment_sha256": hashlib.sha256(json.dumps(assignments, sort_keys=True).encode()).hexdigest().upper()})


def author_action(req):
    import bpy
    from mathutils import Euler, Matrix, Vector
    job, source, spec, output = _inputs(req, True)
    validate_action_spec(spec)
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    rig, mesh = bpy.data.objects.get(spec["rig_name"]), bpy.data.objects.get(spec["mesh_name"])
    if rig is None or rig.type != "ARMATURE" or mesh is None or mesh.type != "MESH" or mesh.parent != rig or not rig.get("hoi4_fitted_rig_spec_sha256"):
        raise ValueError("Action requires the exact fitted mesh and rig.")
    if rig.library or rig.constraints or rig.animation_data and (rig.animation_data.drivers or rig.animation_data.nla_tracks) or any(pb.constraints for pb in rig.pose.bones):
        raise ValueError("Unsupported rig dependencies.")
    if any(abs(rig.matrix_world[r][c] - (1.0 if r == c else 0.0)) > 1e-6 for r in range(4) for c in range(4)):
        raise ValueError("Fitted action authoring requires the identity world transform guaranteed by author_rig.")
    if set(spec["bone_keys"]) - set(rig.pose.bones.keys()) or set(spec["contact_bones"]) - set(rig.pose.bones.keys()):
        raise ValueError("Action references absent bones.")
    if bpy.data.actions.get(spec["action_name"]) or bpy.data.actions.get(spec["action_name"] + "_authored"):
        raise ValueError("Action names already exist.")
    before = _mesh_fingerprint(mesh)
    scene = bpy.context.scene
    scene.render.fps, scene.render.fps_base = spec["fps"], 1.0
    scene.frame_start, scene.frame_end = spec["frame_start"], spec["frame_end"]
    rig.animation_data_create()
    authored = bpy.data.actions.new(spec["action_name"] + "_authored")
    authored.use_fake_user = True
    authored["source_route"] = "manual_blender_gpt6_astra_explicit_role_keys"
    authored["role"] = spec["role"]
    authored["spec_sha256"] = req["payload"]["expected_spec_sha256"]
    rig.animation_data.action = authored
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.matrix_basis = Matrix.Identity(4)
        for f in (spec["frame_start"], spec["frame_end"]):
            pb.keyframe_insert(data_path="location", frame=f, group=pb.name)
            pb.keyframe_insert(data_path="rotation_quaternion", frame=f, group=pb.name)
    for name, rows in spec["bone_keys"].items():
        pb = rig.pose.bones[name]
        for row in rows:
            pb.location = row["location"]
            pb.rotation_quaternion = Euler([math.radians(x) for x in row["rotation_xyz_deg"]], "XYZ").to_quaternion()
            pb.keyframe_insert(data_path="location", frame=row["frame"], group=name)
            pb.keyframe_insert(data_path="rotation_quaternion", frame=row["frame"], group=name)
    # Uniformly linear interpolation is deliberate and recorded; keys are
    # role-authored rather than emitted by a sinusoidal motion template.
    for layer in authored.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for point in curve.keyframe_points:
                        point.interpolation = "LINEAR"
    constraints, poles = [], []
    scene.frame_set(spec["frame_start"])
    bpy.context.view_layer.update()
    for chain in json.loads(rig["hoi4_fitted_ik_json"]):
        pole = bpy.data.objects.new("HOI4_FITTED_POLE_" + chain["forearm"], None)
        mesh.users_collection[0].objects.link(pole)
        pole.location = chain["pole"]
        if chain.get("pole_parent_bone"):
            parent_name = chain["pole_parent_bone"]
            if parent_name not in rig.data.bones:
                raise ValueError("Saved IK pole-parent bone is absent.")
            # Input pole points are explicitly measured in rest world space.
            # Preserve that bone-head-local point through Blender's tail-offset
            # parenting convention, using the same verified route as locators.
            local_point = rig.data.bones[parent_name].matrix_local.inverted() @ Vector(chain["pole"])
            pole.parent, pole.parent_type, pole.parent_bone = rig, "BONE", parent_name
            pole.matrix_parent_inverse = Matrix.Identity(4)
            pole.matrix_basis = Matrix.Identity(4)
            bpy.context.view_layer.update()
            parent_world = rig.matrix_world @ rig.pose.bones[parent_name].matrix
            intended = parent_world @ Matrix.Translation(local_point)
            pole.matrix_world = intended
            bpy.context.view_layer.update()
            if max(abs(pole.matrix_world[r][c] - intended[r][c]) for r in range(4) for c in range(4)) > 1e-5:
                raise RuntimeError("IK pole-parent bone-local transform roundtrip failed.")
        poles.append(pole)
        con = rig.pose.bones[chain["forearm"]].constraints.new("IK")
        con.target, con.subtarget, con.chain_count = rig, chain["target_hand"], 2
        con.use_stretch = False
        con.pole_target, con.pole_angle = pole, chain["pole_angle"]
        constraints.append((rig.pose.bones[chain["forearm"]], con))
    poses, contacts, grounds = {}, [], []
    contact_indices = [v.index for v in mesh.data.vertices if any(mesh.vertex_groups[g.group].name in spec["contact_bones"] and g.weight > 0.25 for g in v.groups)]
    if spec["grounding"] == "feet_only" and not contact_indices:
        raise ValueError("Feet-only grounding requires weighted contact vertices.")
    for frame in range(spec["frame_start"], spec["frame_end"] + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        evaluated = mesh.evaluated_get(dg)
        evaluated_rig = rig.evaluated_get(dg)
        geom = evaluated.to_mesh()
        world_points = [evaluated.matrix_world @ v.co for v in geom.vertices]
        indices = contact_indices if spec["grounding"] == "feet_only" else range(len(world_points))
        low = min(world_points[i].z for i in indices)
        correction = -low if spec["grounding"] != "none" else 0.0
        # Root-bone local offset is computed from the evaluated pose, then all
        # bones are baked in the same common translation without object keys.
        offset = Vector((0, 0, correction))
        poses[frame] = {pb.name: pb.matrix.copy() for pb in evaluated_rig.pose.bones}
        for matrix in poses[frame].values():
            matrix.translation += offset
        contacts.append({"frame": frame, "hand_errors": {chain["forearm"]: (evaluated_rig.pose.bones[chain["forearm"]].tail - evaluated_rig.pose.bones[chain["target_hand"]].head).length for chain in json.loads(rig["hoi4_fitted_ik_json"])}})
        grounds.append({"frame": frame, "raw_min_z": min(p.z for p in world_points), "contact_min_z": low, "correction_z": correction})
        evaluated.to_mesh_clear()
    for pb, con in constraints:
        pb.constraints.remove(con)
    for pole in poles:
        bpy.data.objects.remove(pole, do_unlink=True)
    baked = bpy.data.actions.new(spec["action_name"])
    baked.use_fake_user = True
    baked["source_route"] = "manual_blender_gpt6_astra_explicit_role_keys_baked_native_ik"
    baked["role"], baked["spec_sha256"] = spec["role"], req["payload"]["expected_spec_sha256"]
    rig.animation_data.action = baked
    previous_quaternions = {}
    for frame, matrices in poses.items():
        for pb in rig.pose.bones:
            local = pb.bone.convert_local_to_pose(matrices[pb.name], pb.bone.matrix_local,
                parent_matrix=matrices[pb.parent.name] if pb.parent else Matrix.Identity(4),
                parent_matrix_local=pb.parent.bone.matrix_local if pb.parent else Matrix.Identity(4), invert=True)
            location, rotation, scale = local.decompose()
            if max(abs(v - 1) for v in scale) > 1e-3:
                raise ValueError("IK bake would require scale channels.")
            if pb.name in previous_quaternions and rotation.dot(previous_quaternions[pb.name]) < 0:
                rotation.negate()
            previous_quaternions[pb.name] = rotation.copy()
            pb.location, pb.rotation_quaternion = location, rotation
            pb.keyframe_insert(data_path="location", frame=frame, group=pb.name)
            pb.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=pb.name)
    bake_errors = []
    for frame, matrices in poses.items():
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        evaluated_rig = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
        error = max(abs(evaluated_rig.pose.bones[name].matrix[r][c] - target[r][c])
                    for name, target in matrices.items() for r in range(4) for c in range(4))
        bake_errors.append({"frame": frame, "matrix_max_error": error})
        if error > 2e-4:
            raise RuntimeError(f"Baked skeletal matrices failed evaluated roundtrip at frame {frame}: {error}")
    scene.frame_set(spec["frame_start"])
    bpy.context.view_layer.update()
    after = _mesh_fingerprint(mesh)
    if before != after:
        raise RuntimeError("Action authoring changed static geometry/UV/materials.")
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    if digest(source) != req["payload"]["expected_source_sha256"].upper():
        raise RuntimeError("Action source checkpoint changed.")
    return _save_report(job, output, {"schema_version": SCHEMA_VERSION, "status": "authored_requires_deformation_and_semantic_qa", "source_sha256": digest(source),
        "spec_sha256": req["payload"]["expected_spec_sha256"].upper(), "author": spec["author"], "role": spec["role"], "authored_action": authored.name,
        "baked_action": baked.name, "frame_start": spec["frame_start"], "frame_end": spec["frame_end"], "fps": spec["fps"], "loop": spec["loop"],
        "phases": spec["phases"], "root_policy": "in_place_xy_bounded_skeletal_vertical_contact_correction", "contacts": contacts,
        "ik_chains": json.loads(rig["hoi4_fitted_ik_json"]),
        "grounding": grounds, "baked_matrix_roundtrip": bake_errors, "geometry_uv_materials_unchanged": True, "source_immutable": True, "scale_channels_authored": False})
