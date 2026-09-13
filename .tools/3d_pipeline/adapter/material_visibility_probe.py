"""Hash-bound, unsaved material-visibility evidence for the locked Blender worker.

This helper has no CLI and does not save or export Blender data.
The shared worker owns route registration and supplies its existing preview renderer.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path, PureWindowsPath
from typing import Any, Callable


VIEWS = {"front", "rear", "left", "right", "top", "underside", "three_quarter"}


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _name(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 256 or any(ord(char) < 32 for char in value):
        raise ValueError(f"{field} requires one exact bounded name.")
    return value


def validate_visibility_request(req: dict[str, Any]) -> dict[str, Any]:
    payload = req["payload"]
    probe = payload.get("material_visibility")
    if not isinstance(probe, dict) or set(probe) - {"target_mesh_names", "expected_action_sha256"} or "target_mesh_names" not in probe:
        raise ValueError("material_visibility requires target_mesh_names and accepts only expected_action_sha256 in addition.")
    if payload.get("mesh_region") is not None or payload.get("include_action_channels") is not None:
        raise ValueError("Material visibility cannot combine with other inspection modes.")
    names = probe["target_mesh_names"]
    if not isinstance(names, list) or not 1 <= len(names) <= 32:
        raise ValueError("target_mesh_names requires 1-32 exact names.")
    names = [_name(name, "target_mesh_names") for name in names]
    if len(set(names)) != len(names):
        raise ValueError("target_mesh_names must be unique.")
    expected = payload.get("expected_source_sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", expected):
        raise ValueError("Material visibility requires expected_source_sha256.")
    frame = payload.get("preview_frame")
    if type(frame) is not int or not 0 <= frame <= 1000000:
        raise ValueError("Material visibility requires one exact bounded preview_frame.")
    stem = payload.get("runtime_stem")
    if not isinstance(stem, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,95}", stem):
        raise ValueError("Material visibility requires a safe runtime_stem.")
    views = payload.get("preview_view_names")
    if not isinstance(views, list) or not 1 <= len(views) <= 3 or any(not isinstance(view, str) or view not in VIEWS for view in views) or len(set(views)) != len(views):
        raise ValueError("Material visibility requires 1-3 unique known preview views.")
    if payload.get("render_previews") is not True:
        raise ValueError("Material visibility requires render_previews=true for the paired evidence.")
    relative = payload.get("blend_rel")
    if not isinstance(relative, str) or not relative or PureWindowsPath(relative).is_absolute() or PureWindowsPath(relative).drive or Path(relative).is_absolute() or ".." in PureWindowsPath(relative).parts:
        raise ValueError("blend_rel must remain job-relative without traversal.")
    job = Path(req["job_root"]).resolve()
    source = (job / relative).resolve()
    if not source.is_relative_to(job) or source.suffix.lower() != ".blend" or not source.is_file() or source.stat().st_size < 1:
        raise ValueError("Material visibility requires an existing job-local .blend.")
    if _sha(source) != expected.upper():
        raise ValueError("Material visibility source SHA-256 mismatch.")
    rig = payload.get("target_armature_name")
    action = payload.get("action_name")
    action_sha = probe.get("expected_action_sha256")
    if action:
        rig = _name(rig, "target_armature_name")
        action = _name(action, "action_name")
        if not isinstance(action_sha, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", action_sha):
            raise ValueError("Action visibility requires expected_action_sha256.")
        action_sha = action_sha.upper()
    elif rig or action_sha:
        raise ValueError("Rig/action hash selectors require an exact action_name.")
    return {"job": job, "source": source, "source_sha256": expected.upper(), "mesh_names": names, "frame": frame, "stem": stem, "views": views, "rig_name": rig, "action_name": action, "action_sha256": action_sha}


def _value(value: Any) -> Any:
    if isinstance(value, (str, bool, int, float)) or value is None:
        return value
    try:
        return list(value)
    except TypeError:
        return str(value)


def material_visibility_record(material: Any) -> dict[str, Any]:
    record = {"name": material.name, "settings": {name: _value(getattr(material, name)) for name in ("use_nodes", "use_backface_culling", "use_backface_culling_shadow", "use_backface_culling_lightprobe_volume", "surface_render_method", "blend_method", "alpha_threshold", "show_transparent_back", "use_transparent_shadow", "diffuse_color") if hasattr(material, name)}, "nodes": [], "links": []}
    tree = material.node_tree if material.use_nodes else None
    if tree is None:
        return record
    if len(tree.nodes) > 256 or len(tree.links) > 512:
        raise ValueError("Visibility material graph exceeds the bounded diagnostic budget.")
    for node in tree.nodes:
        entry = {"name": node.name, "type": node.bl_idname, "mute": bool(node.mute)}
        if node.bl_idname in {"ShaderNodeBsdfPrincipled", "ShaderNodeNormalMap", "ShaderNodeOutputMaterial", "ShaderNodeBump", "ShaderNodeMixShader", "ShaderNodeBsdfTransparent"}:
            entry["inputs"] = {socket.name: {"default": _value(getattr(socket, "default_value", None)), "linked": bool(socket.is_linked)} for socket in node.inputs}
        if node.bl_idname == "ShaderNodeNormalMap":
            entry["space"] = node.space
            entry["uv_map"] = node.uv_map
        if node.bl_idname == "ShaderNodeTexImage":
            image = node.image
            entry["image"] = None if image is None else {"name": image.name, "filepath": image.filepath, "source": image.source, "alpha_mode": image.alpha_mode, "color_space": image.colorspace_settings.name, "size": list(image.size), "channels": image.channels, "packed": bool(image.packed_file), "has_data": bool(image.has_data)}
        record["nodes"].append(entry)
    record["links"] = [{"from_node": link.from_node.name, "from_socket": link.from_socket.name, "to_node": link.to_node.name, "to_socket": link.to_socket.name} for link in tree.links]
    return record


def directional_face_counts(obj: Any, bpy: Any) -> dict[str, Any]:
    """Count posed world-space faces toward six declared orthographic directions.

    These counts are directional evidence, not a claim that normals are outward.
    They do not include camera occlusion or claim a perspective pixel count.
    """
    from mathutils import Vector

    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        if len(mesh.vertices) > 1000000 or len(mesh.polygons) > 200000:
            raise ValueError("Visibility geometry exceeds the bounded face-count budget.")
        mesh.calc_loop_triangles()
        directions = {"front_minus_y": Vector((0, -1, 0)), "rear_plus_y": Vector((0, 1, 0)), "left_minus_x": Vector((-1, 0, 0)), "right_plus_x": Vector((1, 0, 0)), "top_plus_z": Vector((0, 0, 1)), "underside_minus_z": Vector((0, 0, -1))}
        counts = {name: {"front_facing": 0, "back_facing": 0, "edge_on_or_degenerate": 0} for name in directions}
        for triangle in mesh.loop_triangles:
            a, b, c = [evaluated.matrix_world @ mesh.vertices[index].co for index in triangle.vertices]
            normal = (b - a).cross(c - a)
            if normal.length > 1e-12:
                normal.normalize()
            for name, direction in directions.items():
                dot = normal.dot(direction)
                key = "front_facing" if dot > 1e-7 else "back_facing" if dot < -1e-7 else "edge_on_or_degenerate"
                counts[name][key] += 1
        return {"triangles": len(mesh.loop_triangles), "policy": "posed world-space geometric winding; six named orthographic viewer directions; no occlusion test or outward-normal inference", "directions": counts}
    finally:
        evaluated.to_mesh_clear()


def run_material_visibility_probe(req: dict[str, Any], *, bpy: Any, render_previews: Callable[..., list[str]], action_hash: Callable[[Any], str]) -> dict[str, Any]:
    """Render original/clay pairs, then reopen source even if rendering raises.

    The source checksum is checked both before and after; no checkpoint is saved.
    All material overrides, object visibility, frame, bindings and render settings
    exist only in the unsaved diagnostic scene and are discarded by reopening.
    """
    selected = validate_visibility_request(req)
    framing = {"preview_region": req["payload"].get("preview_region"), "preview_resolution": req["payload"].get("preview_resolution", 512)}
    source, job = selected["source"], selected["job"]
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    result: dict[str, Any] = {}
    try:
        meshes = []
        for name in selected["mesh_names"]:
            obj = bpy.data.objects.get(name)
            if obj is None or obj.type != "MESH" or obj.name not in bpy.context.scene.objects:
                raise ValueError(f"Visibility mesh selection failed for {name}.")
            meshes.append(obj)
        if selected["action_name"]:
            rig = bpy.data.objects.get(selected["rig_name"])
            action = bpy.data.actions.get(selected["action_name"])
            if rig is None or rig.type != "ARMATURE" or action is None:
                raise ValueError("Visibility rig/action selection failed.")
            if action_hash(action) != selected["action_sha256"]:
                raise ValueError("Visibility action SHA-256 mismatch.")
            if not action.frame_range[0] <= selected["frame"] <= action.frame_range[1]:
                raise ValueError("Visibility frame is outside the selected action range.")
            if any(not any(mod.type == "ARMATURE" and mod.object == rig for mod in obj.modifiers) and obj.parent != rig for obj in meshes):
                raise ValueError("Every visibility mesh must consume the exact selected armature.")
            rig.animation_data_create()
            for track in rig.animation_data.nla_tracks:
                track.mute = True
            rig.animation_data.action = action
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                obj.hide_render = obj not in meshes
                obj["hoi4_working"] = obj in meshes
                if obj in meshes:
                    obj.hide_set(False)
        bpy.context.scene.frame_set(selected["frame"])
        bpy.context.view_layer.update()
        materials = {slot.material.name: slot.material for obj in meshes for slot in obj.material_slots if slot.material is not None}
        result = {"read_only": True, "checkpoint_saved": False, "blend": str(source.relative_to(job)).replace("\\", "/"), "source_sha256_before": selected["source_sha256"], "frame": selected["frame"], "action": selected["action_name"], "action_sha256": selected["action_sha256"], "target_armature": selected["rig_name"], "meshes": [{"name": obj.name, "vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons), "material_slots": [slot.material.name if slot.material else None for slot in obj.material_slots], "world_determinant": float(obj.matrix_world.determinant()), "directional_face_counts": directional_face_counts(obj, bpy)} for obj in meshes], "materials": [material_visibility_record(material) for material in materials.values()], "previews": {}, "clay_binding": "temporary per-object material-slot binding; no view-layer override dependency", "render_engine": "BLENDER_EEVEE"}
        bpy.context.view_layer.material_override = None
        result["preview_framing"] = framing
        result["previews"]["original"] = render_previews(job, selected["stem"] + "_original", selected["views"], **framing)
        clay = bpy.data.materials.new("QA_Visibility_Opaque_Clay")
        clay.use_nodes = True
        shader = next(node for node in clay.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = (0.45, 0.45, 0.45, 1.0)
        shader.inputs["Metallic"].default_value = 0.0
        shader.inputs["Roughness"].default_value = 0.8
        shader.inputs["Alpha"].default_value = 1.0
        transmission = shader.inputs.get("Transmission Weight") or shader.inputs.get("Transmission")
        if transmission is not None:
            transmission.default_value = 0.0
        for obj in meshes:
            if len(obj.material_slots) == 0:
                obj.data.materials.append(clay)
            else:
                for slot in obj.material_slots:
                    slot.material = clay
        for culling in (True, False):
            clay.use_backface_culling = culling
            mode = "opaque_clay_culling_on" if culling else "opaque_clay_culling_off"
            result["previews"][mode] = render_previews(job, selected["stem"] + "_" + mode, selected["views"], **framing)
            if bpy.context.scene.render.engine != "BLENDER_EEVEE" or bpy.context.view_layer.material_override is not None or clay.use_backface_culling != culling:
                raise RuntimeError("Paired visibility proof requires EEVEE, exact culling and direct clay bindings.")
        result["preview_sha256"] = {relative: _sha(job / relative) for group in result["previews"].values() for relative in group}
        return result
    finally:
        actual = _sha(source)
        bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
        if actual != selected["source_sha256"]:
            raise RuntimeError("Visibility probe source changed on disk; no read-only acceptance is possible.")
        result["source_sha256_after"] = actual
        result["source_reloaded"] = True
