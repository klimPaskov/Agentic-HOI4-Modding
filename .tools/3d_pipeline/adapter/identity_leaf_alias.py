"""Exact identity leaf-to-parent skin aliases for existing export-limit repairs.

This is not a general rig simplifier. Every removed leaf must have constant
identity local channels in every retained action and the same skin matrix as
its declared direct parent. Source geometry and all remaining curves persist.
"""
from __future__ import annotations

import math
import re
from array import array

from manual_creature_rig import _open, name
from mesh_vertex_material_repair import finish_verified


TOLERANCE = 2e-5


def identity_channel_value(path, index, aliases):
    match = re.fullmatch(r'pose\.bones\["([^"\\]+)"\]\.(location|rotation_quaternion|scale)', path)
    if match is None or match.group(1) not in aliases:
        raise ValueError("Alias channels must be explicit location, quaternion or scale channels.")
    field = match.group(2)
    if type(index) is not int or not 0 <= index < (4 if field == "rotation_quaternion" else 3):
        raise ValueError("Alias channel index is invalid.")
    return 1.0 if field == "scale" or (field == "rotation_quaternion" and index == 0) else 0.0


def validate_payload(payload):
    required = {"blend_rel", "checkpoint_rel", "expected_source_sha256", "target_armature_name", "target_mesh_names", "bone_aliases", "action_hashes"}
    if set(payload) != required:
        raise ValueError("Identity leaf repair accepts only its declared bounded arguments.")
    name(payload["target_armature_name"])
    meshes, aliases, actions = payload["target_mesh_names"], payload["bone_aliases"], payload["action_hashes"]
    if not isinstance(meshes, list) or not 1 <= len(meshes) <= 32 or len(set(meshes)) != len(meshes):
        raise ValueError("Require 1-32 exact unique working mesh names.")
    if not isinstance(aliases, dict) or not 1 <= len(aliases) <= 8 or set(aliases) & set(aliases.values()):
        raise ValueError("Require 1-8 direct leaf aliases with no alias chains.")
    if not isinstance(actions, dict) or not 1 <= len(actions) <= 32:
        raise ValueError("Require 1-32 hash-bound selected actions.")
    for value in meshes + list(aliases) + list(aliases.values()) + list(actions):
        name(value)
    if any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value) for value in actions.values()):
        raise ValueError("Every selected action requires its native action SHA-256.")


def collapse_identity_leaf_joints(req, h):
    p = req["payload"]
    validate_payload(p)
    job, source, output = _open(req, h)
    bpy, aliases = h["bpy"], p["bone_aliases"]
    scene = bpy.context.scene
    rig = bpy.data.objects.get(p["target_armature_name"])
    meshes = [bpy.data.objects.get(n) for n in p["target_mesh_names"]]
    if rig is None or rig.type != "ARMATURE" or rig.data.users != 1:
        raise ValueError("Require one exact local unshared working armature.")
    if any(o is None or o.library or o.override_library or o.data.library or not o.get("hoi4_working") or o.get("hoi4_source_protected") or o.get("hoi4_reference_read_only") for o in [rig] + meshes):
        raise ValueError("Linked, protected, missing or unapproved working objects are forbidden.")
    if set(o.name for o in h["mesh_objects"]()) != set(p["target_mesh_names"]):
        raise ValueError("Every approved working mesh must be explicitly declared.")
    for obj in meshes:
        if obj.type != "MESH" or obj.data.users != 1 or obj.data.shape_keys or len(obj.modifiers) != 1 or obj.modifiers[0].type != "ARMATURE" or obj.modifiers[0].object != rig:
            raise ValueError("Require unshared meshes with one existing target armature modifier.")
    if any(o not in meshes and any(m.type == "ARMATURE" and m.object == rig for m in o.modifiers) for o in bpy.data.objects if o.type == "MESH"):
        raise ValueError("Undeclared meshes also use the target rig.")
    if not rig.animation_data or rig.animation_data.drivers or rig.animation_data.nla_tracks or rig.constraints or any(b.constraints for b in rig.pose.bones):
        raise ValueError("Drivers, NLA and constraints are outside identity-alias proof.")
    for child, parent in aliases.items():
        bone = rig.data.bones.get(child)
        if bone is None or bone.parent is None or bone.parent.name != parent or bone.children:
            raise ValueError("Each alias must be an existing leaf with its exact direct parent.")
        if not bone.use_inherit_rotation or bone.inherit_scale != "FULL" or not bone.use_local_location:
            raise ValueError("Nonstandard leaf inheritance cannot be collapsed.")
        if any(o.parent == rig and o.parent_type == "BONE" and o.parent_bone == child for o in bpy.data.objects):
            raise ValueError("A locator or rigid object is attached to the proposed leaf.")
        pose = rig.pose.bones[child]
        if pose.rotation_mode != "QUATERNION" or max(abs(pose.matrix_basis[i][j] - (1.0 if i == j else 0.0)) for i in range(4) for j in range(4)) > 1e-7:
            raise ValueError("The original leaf pose must be identity.")
    selected = []
    for action_name, expected in p["action_hashes"].items():
        action = bpy.data.actions.get(action_name)
        if action is None or h["_mesh_region_action_hash"](action) != expected.upper():
            raise ValueError("Selected action native SHA-256 mismatch: " + action_name)
        start, end = map(int, action.frame_range)
        if list(action.frame_range) != [start, end] or not 1 <= end - start + 1 <= 600:
            raise ValueError("Require bounded integer action ranges.")
        selected.append((action, start, end))
    prefixes = tuple('pose.bones["' + child + '"]' for child in aliases)
    curves_to_remove, identity_evidence = [], []
    # Check all retained historical actions too; leave no dangling bone curves.
    for action in bpy.data.actions:
        checked = []
        for curve, container in h["action_fcurves"](action):
            if not curve.data_path.startswith(prefixes):
                continue
            expected = identity_channel_value(curve.data_path, curve.array_index, aliases)
            keys = list(curve.keyframe_points)
            if curve.modifiers or curve.sampled_points or not keys or any(key.interpolation not in {"LINEAR", "CONSTANT"} or float(key.co.y) != expected for key in keys):
                raise ValueError("A retained action has nonidentity or uncontrolled alias motion: " + action.name)
            curves_to_remove.append((action, curve, container))
            checked.append({"path": curve.data_path, "index": curve.array_index, "value": expected, "keys": len(keys)})
        identity_evidence.append({"action": action.name, "channels": checked})
    count = sum((end - start) * 2 + 1 for _, start, end in selected)
    if count * sum(len(o.data.vertices) for o in meshes) > 50000000:
        raise ValueError("Identity-alias deformation proof exceeds fifty million vertices.")
    old_action, old_slot = rig.animation_data.action, rig.animation_data.action_slot
    old_frame, old_subframe = scene.frame_current, scene.frame_subframe
    old_selection = [o.name for o in bpy.context.selected_objects]
    old_active = bpy.context.view_layer.objects.active
    scene.frame_set(old_frame, subframe=old_subframe)
    bpy.context.view_layer.update()
    before = h["_promotion_fingerprint"](job, [], include_sections=True)
    bone_count = len(rig.data.bones)
    retained_names = [b.name for b in rig.data.bones if b.name not in aliases]
    rest = {b.name: [list(row) for row in b.matrix_local] for b in rig.data.bones if b.name not in aliases}
    locators = [o for o in bpy.data.objects if o.type == "EMPTY" and o.parent == rig]

    def bind(action):
        rig.animation_data.action = action
        if action is not None and action.slots:
            rig.animation_data.action_slot = action.slots[0]

    def sample(frame):
        scene.frame_set(int(frame), subframe=frame % 1)
        bpy.context.view_layer.update()
        graph = bpy.context.evaluated_depsgraph_get()
        points = {}
        for obj in meshes:
            evaluated = obj.evaluated_get(graph)
            mesh = evaluated.to_mesh()
            try:
                values = array("f", [0.0]) * (len(mesh.vertices) * 3)
                mesh.vertices.foreach_get("co", values)
                points[obj.name] = values
            finally:
                evaluated.to_mesh_clear()
        matrices = {bone: array("f", [value for row in rig.pose.bones[bone].matrix for value in row]) for bone in retained_names}
        matrices.update({"locator:" + o.name: array("f", [value for row in o.matrix_world for value in row]) for o in locators})
        return points, matrices

    samples, maximum_alias_matrix_error = {}, 0.0
    for action, start, end in selected:
        bind(action)
        for half in range(start * 2, end * 2 + 1):
            frame = half / 2
            samples[(action.name, half)] = sample(frame)
            for child, parent in aliases.items():
                left = rig.pose.bones[child].matrix @ rig.data.bones[child].matrix_local.inverted()
                right = rig.pose.bones[parent].matrix @ rig.data.bones[parent].matrix_local.inverted()
                maximum_alias_matrix_error = max(maximum_alias_matrix_error, max(abs(left[i][j] - right[i][j]) for i in range(4) for j in range(4)))
        if maximum_alias_matrix_error > TOLERANCE:
            raise RuntimeError("Leaf and parent skin matrices differ; collapse rejected.")

    transfers = []
    expected_weights = {}
    for obj in meshes:
        expected_weights[obj.name] = []
        for vertex in obj.data.vertices:
            weights = {obj.vertex_groups[g.group].name: float(g.weight) for g in vertex.groups}
            merged = dict(weights)
            for child, parent in aliases.items():
                if child in merged:
                    merged[parent] = merged.get(parent, 0.0) + merged.pop(child)
            expected_weights[obj.name].append(merged)
        for child, parent in aliases.items():
            source_group = obj.vertex_groups.get(child)
            if source_group is None:
                continue
            target_group = obj.vertex_groups.get(parent)
            if target_group is None:
                raise ValueError("Alias parent must already have a vertex group.")
            affected = [v.index for v in obj.data.vertices if any(g.group == source_group.index and g.weight > 0 for g in v.groups)]
            for index in affected:
                target_group.add([index], expected_weights[obj.name][index][parent], "REPLACE")
            transfers.append({"object": obj.name, "leaf": child, "parent": parent, "affected_vertices": len(affected)})
            obj.vertex_groups.remove(source_group)
    for _, curve, container in curves_to_remove:
        container.remove(curve)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for child in aliases:
        rig.data.edit_bones.remove(rig.data.edit_bones[child])
    bpy.ops.object.mode_set(mode="OBJECT")
    if len(rig.data.bones) != bone_count - len(aliases) or list(rig.data.bones.keys()) != retained_names:
        raise RuntimeError("Native joint removal changed an undeclared joint or order.")
    for bone, matrix in rest.items():
        if max(abs(rig.data.bones[bone].matrix_local[i][j] - matrix[i][j]) for i in range(4) for j in range(4)) > TOLERANCE:
            raise RuntimeError("A retained bind matrix changed.")
    for obj in meshes:
        for vertex, expected in zip(obj.data.vertices, expected_weights[obj.name]):
            actual = {obj.vertex_groups[g.group].name: float(g.weight) for g in vertex.groups}
            if set(actual) != set(expected) or any(abs(actual[k] - expected[k]) > 2e-7 for k in actual):
                raise RuntimeError("Weight transfer changed undeclared weights.")
    proofs = []
    for action, start, end in selected:
        bind(action)
        vertex_error, matrix_error = 0.0, 0.0
        for half in range(start * 2, end * 2 + 1):
            points, matrices = sample(half / 2)
            old_points, old_matrices = samples.pop((action.name, half))
            for key, values in points.items():
                if len(values) != len(old_points[key]):
                    raise RuntimeError("Evaluated vertex count changed.")
                vertex_error = max(vertex_error, max(abs(a - b) for a, b in zip(values, old_points[key])))
            for key, values in matrices.items():
                matrix_error = max(matrix_error, max(abs(a - b) for a, b in zip(values, old_matrices[key])))
        if vertex_error > TOLERANCE or matrix_error > TOLERANCE:
            raise RuntimeError("Identity-alias deformation or locator proof failed.")
        proofs.append({"action": action.name, "frame_start": start, "frame_end": end, "sample_interval": 0.5, "samples": (end - start) * 2 + 1, "maximum_vertex_component_error": vertex_error, "maximum_retained_bone_or_locator_matrix_error": matrix_error})
    bind(old_action)
    if old_slot is not None:
        rig.animation_data.action_slot = old_slot
    scene.frame_set(old_frame, subframe=old_subframe)
    bpy.ops.object.select_all(action="DESELECT")
    for obj_name in old_selection:
        bpy.data.objects[obj_name].select_set(True)
    bpy.context.view_layer.objects.active = old_active
    bpy.context.view_layer.update()
    after = h["_promotion_fingerprint"](job, [], include_sections=True)
    for section in ("materials", "images", "scene"):
        if before["sha256"][section] != after["sha256"][section]:
            raise RuntimeError("Identity alias changed unrelated " + section)
    for obj_name, record in before["sections"]["geometry"].items():
        other = after["sections"]["geometry"][obj_name]
        ignored = {"weights", "groups"} if obj_name in p["target_mesh_names"] else set()
        if {k: v for k, v in record.items() if k not in ignored} != {k: v for k, v in other.items() if k not in ignored}:
            raise RuntimeError("Identity alias changed source geometry, UVs or normals: " + obj_name)
    for action_name, record in before["sections"]["actions"].items():
        expected = dict(record)
        expected["curves"] = [row for row in record["curves"] if not row["path"].startswith(prefixes)]
        if expected != after["sections"]["actions"][action_name]:
            raise RuntimeError("Identity alias changed retained action curves or settings: " + action_name)
    return finish_verified(req, h, job, source, output, {"operation": "collapse_identity_leaf_joints", "status": "pass", "policy": "exact_identity_leaf_to_direct_parent_only", "bone_aliases": aliases, "bones_before": bone_count, "bones_after": len(rig.data.bones), "retained_bind_matrices_preserved": True, "all_geometry_uvs_normals_materials_preserved": True, "all_nonalias_action_curves_preserved": True, "every_retained_action_identity_gate": identity_evidence, "maximum_alias_skin_matrix_error": maximum_alias_matrix_error, "weight_transfers": transfers, "evaluated_action_proofs": proofs, "provider_credits": 0})
