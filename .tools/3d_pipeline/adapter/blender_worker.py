"""Blender-side implementation for structured adapter operations.

This file is invoked only by the allowlisted adapter. It receives a validated
request file and emits one JSON result line for the adapter to return.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import bpy
import bmesh
from mathutils import Euler, Matrix, Quaternion, Vector
from mathutils.kdtree import KDTree


PREVIEW_LIGHT_REFERENCE_HEIGHT = 7.3518242835
CREATURE_GROUND_CONTACT_TOLERANCE_M = 0.01
CREATURE_GROUND_CONTACT_CLEARANCE_M = 0.001


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", default=os.environ.get("HOI4_WORKER_REQUEST"))
    parser.add_argument("--io-pdx-root", default=os.environ.get("HOI4_IO_PDX_ROOT"))
    args, _ = parser.parse_known_args()
    return args


def safe_name(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    if not result:
        raise ValueError("A non-empty safe name is required.")
    return result


def within(root: Path, value: str, *, allow_missing: bool = False) -> Path:
    if not value or Path(value).is_absolute() or ":" in value:
        raise ValueError("Worker paths must be relative to the job root.")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Worker path escaped the job root: {value}") from exc
    if not allow_missing and not path.exists():
        raise FileNotFoundError(path)
    return path


def load_pdx(io_pdx_root: str) -> Dict[str, Any]:
    """Load the locked addon without relying on a UI context."""

    addon_root = Path(io_pdx_root).resolve()
    if not (addon_root / "blender_manifest.toml").exists():
        raise FileNotFoundError(addon_root / "blender_manifest.toml")
    package_parent = addon_root.parent
    if str(package_parent) not in sys.path:
        sys.path.insert(0, str(package_parent))
    try:
        import io_pdx_mesh  # type: ignore
    except ImportError:
        raise RuntimeError(f"Unable to import io_pdx_mesh from {addon_root}")
    if not hasattr(bpy.ops, "io_pdx_mesh") or not hasattr(bpy.ops.io_pdx_mesh, "import_mesh"):
        io_pdx_mesh.register()
    from io_pdx_mesh.pdx_blender.blender_import_export import (  # type: ignore
        PDX_MESHINDEX,
        PDX_SHADER,
        export_animfile,
        export_meshfile,
        import_animfile,
        import_meshfile,
        set_mesh_index,
    )

    return {
        "module": io_pdx_mesh,
        "PDX_MESHINDEX": PDX_MESHINDEX,
        "PDX_SHADER": PDX_SHADER,
        "export_animfile": export_animfile,
        "export_meshfile": export_meshfile,
        "import_animfile": import_animfile,
        "import_meshfile": import_meshfile,
        "set_mesh_index": set_mesh_index,
        "manifest": str(addon_root / "blender_manifest.toml"),
    }


def save_blend(path: Path) -> None:
    # Checkpoints are the source of truth for the complete runtime action set.
    # Keep every authored or transferred action across later saves even when
    # Blender's single active action slot is switched during the pipeline.
    for action in bpy.data.actions:
        action.use_fake_user = True
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def new_collection(name: str) -> bpy.types.Collection:
    existing = bpy.data.collections.get(name)
    if existing is not None:
        for obj in list(existing.objects):
            existing.objects.unlink(obj)
        if existing in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.unlink(existing)
        bpy.data.collections.remove(existing)
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    default = bpy.data.collections.get("Collection")
    if default is not None:
        for obj in list(default.objects):
            default.objects.unlink(obj)
        bpy.data.collections.remove(default)


def import_candidate(source: Path) -> List[bpy.types.Object]:
    before = set(bpy.data.objects)
    suffix = source.suffix.lower()
    if suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(source))
    elif suffix == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(source))
    else:
        raise ValueError(f"Unsupported provider source format: {source.suffix}")
    imported = [obj for obj in bpy.data.objects if obj not in before]
    if not imported:
        imported = list(bpy.context.selected_objects)
    if not imported:
        raise RuntimeError(f"Blender imported no objects from {source}")
    return imported


def import_vanilla_reference(
    job: Path,
    payload: Dict[str, Any],
    pdx: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    reference = payload.get("vanilla_reference") or {}
    if not reference:
        if payload.get("asset_kind") == "humanoid":
            raise RuntimeError("Humanoid preparation requires an imported vanilla scale reference.")
        return None

    mesh_rel = str(reference.get("mesh_rel", ""))
    reference_path = within(job, mesh_rel)
    before = set(bpy.data.objects)
    pdx["import_meshfile"](
        str(reference_path),
        imp_mesh=True,
        imp_skel=False,
        imp_locs=True,
        join_materials=True,
    )
    imported = [obj for obj in bpy.data.objects if obj not in before]
    if not imported:
        raise RuntimeError(f"io_pdx_mesh imported no objects from vanilla reference {reference_path}.")

    collection = new_collection("00_REFERENCE_VANILLA")
    for obj in imported:
        move_to_collection(obj, collection)
        obj["hoi4_reference_read_only"] = True
        obj.hide_render = True
        obj.hide_set(True)

    main_names = {str(name) for name in reference.get("mesh_object_names", [])}
    excluded_patterns = [str(value).casefold() for value in reference.get("exclude_name_patterns", [])]
    meshes = [obj for obj in imported if obj.type == "MESH"]
    if main_names:
        selected = [obj for obj in meshes if obj.name in main_names]
    else:
        selected = meshes
    selected = [
        obj
        for obj in selected
        if not any(pattern in obj.name.casefold() for pattern in excluded_patterns)
    ]
    if not selected:
        raise RuntimeError(
            "Vanilla reference selection produced no mesh objects: "
            + json.dumps(
                {
                    "available_meshes": [obj.name for obj in meshes],
                    "requested_meshes": sorted(main_names),
                    "excluded_patterns": excluded_patterns,
                },
                sort_keys=True,
            )
        )

    minimum, maximum = world_bounds(selected)
    source_height = maximum.z - minimum.z
    expected_height = float(reference["mesh_height"])
    entity_scale = float(reference["entity_scale"])
    expected_runtime_height = float(reference["runtime_height"])
    measurement_tolerance = max(0.01, expected_height * 0.01)
    if abs(source_height - expected_height) > measurement_tolerance:
        raise RuntimeError(
            f"Vanilla reference height changed: measured {source_height:.6f}, "
            f"expected {expected_height:.6f}, tolerance {measurement_tolerance:.6f}."
        )
    return {
        "mesh_rel": mesh_rel,
        "objects": [obj.name for obj in imported],
        "selected_meshes": [obj.name for obj in selected],
        "excluded_patterns": excluded_patterns,
        "bounds_min": list(minimum),
        "bounds_max": list(maximum),
        "source_mesh_height": source_height,
        "entity_scale": entity_scale,
        "effective_runtime_height": source_height * entity_scale,
        "expected_mesh_height": expected_height,
        "expected_runtime_height": expected_runtime_height,
        "forward_axis": reference.get("forward_axis"),
        "up_axis": reference.get("up_axis"),
        "ground_contact_z": minimum.z,
        "reference_policy": "read_only_vanilla_source_measurement; pilot mesh target may bake its calibrated runtime scale",
        "status": "passed",
    }


def duplicate_hierarchy(
    source_objects: List[bpy.types.Object],
    source_collection: bpy.types.Collection,
    working_collection: bpy.types.Collection,
) -> List[bpy.types.Object]:
    mapping: Dict[bpy.types.Object, bpy.types.Object] = {}
    for source in source_objects:
        duplicate = source.copy()
        if source.data is not None:
            try:
                duplicate.data = source.data.copy()
            except AttributeError:
                pass
        working_collection.objects.link(duplicate)
        mapping[source] = duplicate
        duplicate["hoi4_working"] = True
        duplicate["hoi4_source_object"] = source.name
    for source, duplicate in mapping.items():
        if source.parent in mapping:
            duplicate.parent = mapping[source.parent]
        if duplicate.parent is not None:
            duplicate.matrix_parent_inverse = source.matrix_parent_inverse.copy()
        if source.animation_data and source.animation_data.action:
            duplicate.animation_data_create()
            duplicate.animation_data.action = source.animation_data.action.copy()
            duplicate.animation_data.action.name = f"{source.animation_data.action.name}_WORKING"
    for duplicate in mapping.values():
        for modifier in duplicate.modifiers:
            if modifier.type == "ARMATURE" and modifier.object in mapping:
                modifier.object = mapping[modifier.object]
    for source in source_objects:
        source["hoi4_source_protected"] = True
        source.hide_render = True
        source.hide_set(True)
    return list(mapping.values())


def bind_geometry_to_existing_rig(
    source_mesh: bpy.types.Object,
    target_mesh: bpy.types.Object,
    target_armature: bpy.types.Object,
) -> Dict[str, Any]:
    """Transfer rest-pose weights from the provider rig mesh to a closed mesh candidate."""

    source_minimum, source_maximum = world_bounds([source_mesh])
    target_minimum, target_maximum = world_bounds([target_mesh])
    source_height = source_maximum.z - source_minimum.z
    target_height = target_maximum.z - target_minimum.z
    if source_height <= 0 or target_height <= 0:
        raise RuntimeError("Dual-source rig transfer requires positive source and target heights.")

    target_mesh.scale *= source_height / target_height
    bpy.context.view_layer.update()
    target_minimum, target_maximum = world_bounds([target_mesh])
    source_center = (source_minimum + source_maximum) * 0.5
    target_center = (target_minimum + target_maximum) * 0.5
    target_mesh.location += source_center - target_center
    bpy.context.view_layer.update()

    for group in list(target_mesh.vertex_groups):
        target_mesh.vertex_groups.remove(group)
    target_groups = {
        group.name: target_mesh.vertex_groups.new(name=group.name)
        for group in source_mesh.vertex_groups
    }
    if not target_groups:
        raise RuntimeError("Dual-source rig transfer found no provider vertex groups.")

    tree = KDTree(len(source_mesh.data.vertices))
    for vertex in source_mesh.data.vertices:
        tree.insert(source_mesh.matrix_world @ vertex.co, vertex.index)
    tree.balance()
    source_groups = list(source_mesh.vertex_groups)
    transferred_vertices = 0
    for vertex in target_mesh.data.vertices:
        nearest = tree.find_n(target_mesh.matrix_world @ vertex.co, 4)
        accumulated: Dict[str, float] = {}
        for _, source_index, distance in nearest:
            influence = 1.0 / max(distance, 1e-6)
            for source_group in source_groups:
                try:
                    weight = source_group.weight(source_index)
                except RuntimeError:
                    continue
                if weight > 0:
                    accumulated[source_group.name] = accumulated.get(source_group.name, 0.0) + weight * influence
        total = sum(accumulated.values())
        if total <= 1e-8:
            continue
        for name, weight in accumulated.items():
            target_groups[name].add([vertex.index], weight / total, "REPLACE")
        transferred_vertices += 1

    mesh_world_scale = target_mesh.matrix_world.to_scale()
    rig_world_scale = target_armature.matrix_world.to_scale()
    if (
        max(mesh_world_scale) - min(mesh_world_scale) > 1e-5
        or max(rig_world_scale) - min(rig_world_scale) > 1e-5
        or min(mesh_world_scale) <= 0.0
        or min(rig_world_scale) <= 0.0
    ):
        raise RuntimeError(
            "Dual-source rig transfer requires positive uniform mesh and armature transforms."
        )
    export_scale_ratio = float(mesh_world_scale[0] / rig_world_scale[0])
    for vertex in target_mesh.data.vertices:
        vertex.co *= export_scale_ratio
    target_mesh.data.update()
    target_mesh.scale = rig_world_scale
    bpy.context.view_layer.update()
    world_matrix = target_mesh.matrix_world.copy()
    target_mesh.parent = target_armature
    target_mesh.parent_type = "OBJECT"
    target_mesh.matrix_world = world_matrix
    modifier = target_mesh.modifiers.new("HOI4_RIG_TRANSFER", type="ARMATURE")
    modifier.object = target_armature
    modifier.use_deform_preserve_volume = True
    return {
        "method": "four-nearest-provider-vertex inverse-distance weight transfer",
        "source_mesh": source_mesh.name,
        "target_mesh": target_mesh.name,
        "armature": target_armature.name,
        "source_vertices": len(source_mesh.data.vertices),
        "target_vertices": len(target_mesh.data.vertices),
        "transferred_vertices": transferred_vertices,
        "alignment_scale": source_height / target_height,
        "source_height": source_height,
        "target_height_before_alignment": target_height,
        "export_transform_policy": "bake mesh/armature scale agreement into mesh data before parenting",
        "mesh_world_scale_before_bake": list(mesh_world_scale),
        "armature_world_scale": list(rig_world_scale),
        "mesh_data_scale_ratio": export_scale_ratio,
        "mesh_world_scale_after_bake": list(target_mesh.matrix_world.to_scale()),
    }


def mesh_objects(working_only: bool = True) -> List[bpy.types.Object]:
    result = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if working_only and not obj.get("hoi4_working", False):
            continue
        result.append(obj)
    return result


def armatures(working_only: bool = True) -> List[bpy.types.Object]:
    result = []
    for obj in bpy.context.scene.objects:
        if obj.type != "ARMATURE":
            continue
        if working_only and not obj.get("hoi4_working", False):
            continue
        result.append(obj)
    return result


def prepare_pdx_export_transforms() -> Dict[str, Any]:
    """Bake the rig object scale into armature data before io_pdx_mesh export."""

    rigs = armatures()
    if not rigs:
        return require_identity_static_mesh_transforms()
    if len(rigs) != 1:
        raise RuntimeError(
            f"PDX export requires exactly one working armature, found {len(rigs)}."
        )
    rig = rigs[0]
    rig_scale = rig.matrix_world.to_scale()
    if (
        max(rig_scale) - min(rig_scale) > 1e-5
        or min(rig_scale) <= 0.0
    ):
        raise RuntimeError(
            "PDX export requires a positive uniform armature world scale, "
            f"got {tuple(rig_scale)}."
        )
    source_scale = float(sum(rig_scale) / 3.0)
    mesh_world_matrices = {
        obj.name: obj.matrix_world.copy()
        for obj in mesh_objects()
    }
    if abs(source_scale - 1.0) > 1e-6:
        rig.data.transform(Matrix.Scale(source_scale, 4))
        animation_translations = scale_action_location_channels(rig, source_scale)
        rig.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()
        for obj in mesh_objects():
            obj.matrix_world = mesh_world_matrices[obj.name]
        bpy.context.view_layer.update()
    else:
        animation_translations = scale_action_location_channels(rig, 1.0)
    return {
        "policy": "bake_uniform_armature_object_scale_into_armature_data_and_preserve_mesh_world_transform",
        "armature": rig.name,
        "armature_world_scale_before": list(rig_scale),
        "armature_data_scale_factor": source_scale,
        "animation_translation_channels": animation_translations,
        "armature_world_scale_after": list(rig.matrix_world.to_scale()),
        "mesh_world_scales_after": {
            obj.name: list(obj.matrix_world.to_scale())
            for obj in mesh_objects()
        },
    }


def ensure_material_nodes(material: bpy.types.Material) -> None:
    material.use_nodes = True
    nodes = material.node_tree.nodes
    output = next((node for node in nodes if node.bl_idname == "ShaderNodeOutputMaterial"), None)
    if output is None:
        output = nodes.new("ShaderNodeOutputMaterial")
    shader = next((node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if shader is None:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
    if not output.inputs["Surface"].is_linked:
        material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])


TEXTURE_IMAGE_NAMES = {
    "diffuse": "texture_0",
    "specular": "texture_specular",
    "normal": "texture_normal",
}

STATIC_TEXTURE_IMAGE_NAMES = {
    "diffuse": "Image_0",
    "specular": "Image_1",
    "normal": "Image_2",
}


def _principled_shader(material: bpy.types.Material) -> bpy.types.Node:
    ensure_material_nodes(material)
    shader = next(
        (node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"),
        None,
    )
    if shader is None:
        raise RuntimeError(f"Material has no Principled shader after node setup: {material.name}")
    return shader


def _load_texture_image(path: Path, name: str, *, non_color: bool) -> bpy.types.Image:
    # glTF imports often leave packed images with the same conventional names
    # used by the runtime handoff (Image_0/Image_1/Image_2). Reusing one keeps
    # the old packed pixels even after changing its filepath, so the export can
    # silently retain the provider's unprocessed normal/spec layout. Replace
    # the name collision and load the explicit source file instead.
    image = bpy.data.images.get(name)
    if image is not None:
        bpy.data.images.remove(image, do_unlink=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    image.name = name
    try:
        image.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    except (AttributeError, TypeError):
        pass
    return image


def _sanitize_pdx_material(material: bpy.types.Material) -> None:
    """Remove glTF-only PBR/emission wiring from the PDX working material."""

    shader = _principled_shader(material)
    for input_name in ("Metallic", "Emission Color", "Emission Strength", "Alpha"):
        socket = shader.inputs.get(input_name)
        if socket is None:
            continue
        for link in list(socket.links):
            material.node_tree.links.remove(link)
        if input_name == "Metallic":
            socket.default_value = 0.0
        elif input_name == "Emission Strength":
            socket.default_value = 0.0
    allowed_nodes = {
        "HOI4_DIFFUSE_TEXTURE",
        "HOI4_SPECULAR_TEXTURE",
        "HOI4_NORMAL_TEXTURE",
    }
    for node in list(material.node_tree.nodes):
        if node.bl_idname == "ShaderNodeTexImage" and node.name not in allowed_nodes:
            material.node_tree.nodes.remove(node)


def bind_texture_sources(job: Path, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Bind explicit provider maps to the working materials before export."""

    source_rels = payload.get("texture_source_rels") or {}
    if payload.get("asset_kind") in {"humanoid", "creature"} and source_rels:
        required = {"diffuse", "specular", "normal"}
        missing = sorted(required - set(source_rels))
        if missing:
            raise RuntimeError(
                "Humanoid export requires explicit diffuse, specular, and normal texture sources; "
                f"missing {missing}."
            )

    working_meshes = mesh_objects()
    if not working_meshes:
        raise RuntimeError("Texture binding found no working mesh objects.")
    image_names = (
        STATIC_TEXTURE_IMAGE_NAMES
        if payload.get("asset_kind") in {"static", "building", "static_building"}
        else TEXTURE_IMAGE_NAMES
    )
    records: List[Dict[str, Any]] = []
    for role, rel in sorted(source_rels.items()):
        if role not in TEXTURE_IMAGE_NAMES:
            raise RuntimeError(f"Unsupported texture source role: {role}")
        source = within(job, str(rel))
        if not source.exists():
            raise FileNotFoundError(source)
        image = _load_texture_image(
            source,
            image_names[role],
            non_color=role in {"specular", "normal"},
        )
        node_count = 0
        for obj in working_meshes:
            if not obj.data.materials:
                obj.data.materials.append(bpy.data.materials.new("HOI4_PdxMeshAdvanced"))
            for material in obj.data.materials:
                if material is None:
                    continue
                _sanitize_pdx_material(material)
                shader = _principled_shader(material)
                node = material.node_tree.nodes.get(f"HOI4_{role.upper()}_TEXTURE")
                if node is None:
                    node = material.node_tree.nodes.new("ShaderNodeTexImage")
                    node.name = f"HOI4_{role.upper()}_TEXTURE"
                node.image = image
                node.label = f"HOI4 {role} texture"
                node_count += 1
                if role == "diffuse":
                    target = shader.inputs.get("Base Color")
                    if target is not None:
                        for link in list(target.links):
                            material.node_tree.links.remove(link)
                        material.node_tree.links.new(node.outputs["Color"], target)
                elif role == "normal":
                    normal_node = material.node_tree.nodes.get("HOI4_NORMAL_MAP")
                    if normal_node is None:
                        normal_node = material.node_tree.nodes.new("ShaderNodeNormalMap")
                        normal_node.name = "HOI4_NORMAL_MAP"
                    normal_node.inputs["Strength"].default_value = 1.0
                    for link in list(normal_node.inputs["Color"].links):
                        material.node_tree.links.remove(link)
                    material.node_tree.links.new(node.outputs["Color"], normal_node.inputs["Color"])
                    target = shader.inputs.get("Normal")
                    if target is not None:
                        for link in list(target.links):
                            material.node_tree.links.remove(link)
                        material.node_tree.links.new(normal_node.outputs["Normal"], target)
                elif role == "specular":
                    # io_pdx_mesh 0.91 reads the Blender Roughness input when
                    # emitting the PDX material's `spec` texture slot. The
                    # engine-side specular map is therefore bound here, not to
                    # Blender's scalar specular-IOR control.
                    target = shader.inputs.get("Roughness")
                    if target is not None:
                        for link in list(target.links):
                            material.node_tree.links.remove(link)
                        material.node_tree.links.new(node.outputs["Color"], target)
        records.append(
            {
                "role": role,
                "image": image.name,
                "source": str(source.relative_to(job)).replace("\\", "/"),
                "node_bindings": node_count,
                "size": [int(image.size[0]), int(image.size[1])],
            }
        )
    return records


def tag_pdx_materials(pdx: Dict[str, Any]) -> Dict[str, Any]:
    material_names: List[str] = []
    for index, obj in enumerate(mesh_objects()):
        pdx["set_mesh_index"](obj.data, index)
        for material in obj.data.materials:
            if material is None:
                continue
            ensure_material_nodes(material)
            material[pdx["PDX_SHADER"]] = "PdxMeshAdvanced"
            material["hoi4_pdx_shader"] = "PdxMeshAdvanced"
            if material.name not in material_names:
                material_names.append(material.name)
        obj["hoi4_export_approved"] = True
    return {"materials": material_names, "shader": "PdxMeshAdvanced"}


def action_fcurves(action: bpy.types.Action) -> Iterable[Tuple[Any, Any]]:
    """Yield action F-curves from both legacy and Blender 5 layered actions."""

    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        for fcurve in legacy:
            yield fcurve, legacy
        return
    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            for channelbag in getattr(strip, "channelbags", []):
                fcurves = getattr(channelbag, "fcurves", None)
                if fcurves is None:
                    continue
                for fcurve in fcurves:
                    yield fcurve, fcurves


def scale_action_location_channels(rig: bpy.types.Object, factor: float) -> Dict[str, Any]:
    """Scale keyed local bone translations when armature data is rescaled."""

    action = rig.animation_data.action if rig.animation_data else None
    if action is None or abs(factor - 1.0) <= 1e-6:
        return {
            "action": action.name if action is not None else None,
            "factor": factor,
            "location_fcurves": 0,
            "keyframes": 0,
            "policy": "no_action_scale_required",
        }
    changed_curves = 0
    changed_keyframes = 0
    for fcurve, _ in action_fcurves(action):
        if "pose.bones[" not in fcurve.data_path or ".location" not in fcurve.data_path:
            continue
        changed_curves += 1
        for keyframe in fcurve.keyframe_points:
            keyframe.co[1] *= factor
            keyframe.handle_left[1] *= factor
            keyframe.handle_right[1] *= factor
            changed_keyframes += 1
        fcurve.update()
    return {
        "action": action.name,
        "factor": factor,
        "location_fcurves": changed_curves,
        "keyframes": changed_keyframes,
        "policy": "scale_local_bone_translation_channels_with_armature_data_bake",
    }


def sanitize_root_translation_channels() -> Dict[str, Any]:
    """Keep the active humanoid action in place by locking Hips location."""

    records: List[Dict[str, Any]] = []
    for rig in armatures():
        action = rig.animation_data.action if rig.animation_data else None
        if action is None:
            continue
        root_curves = [
            fcurve
            for fcurve, _ in action_fcurves(action)
            if fcurve.data_path == 'pose.bones["Hips"].location'
        ]
        if not root_curves:
            records.append(
                {
                    "armature": rig.name,
                    "action": action.name,
                    "location_fcurves": 0,
                    "changed_keyframes": 0,
                    "policy": "no_hips_location_channels_found",
                }
            )
            continue
        fixed_values: Dict[int, float] = {}
        changed_keyframes = 0
        for fcurve in root_curves:
            if not fcurve.keyframe_points:
                continue
            first = min(fcurve.keyframe_points, key=lambda point: point.co[0])
            fixed_values[fcurve.array_index] = float(first.co[1])
            for keyframe in fcurve.keyframe_points:
                if abs(keyframe.co[1] - first.co[1]) > 1e-8:
                    changed_keyframes += 1
                keyframe.co[1] = first.co[1]
                keyframe.handle_left[1] = first.co[1]
                keyframe.handle_right[1] = first.co[1]
            fcurve.update()
        first_frame = int(math.floor(float(action.frame_range[0])))
        bpy.context.scene.frame_set(first_frame)
        bpy.context.view_layer.update()
        before_minimum, _ = evaluated_world_bounds(mesh_objects())
        ground_correction = 0.0
        armature_scale = float(rig.matrix_world.to_scale().z)
        z_curve = next(
            (fcurve for fcurve in root_curves if fcurve.array_index == 2),
            None,
        )
        if z_curve is not None and armature_scale > 1e-8:
            test_step = 1.0
            for keyframe in z_curve.keyframe_points:
                keyframe.co[1] += test_step
                keyframe.handle_left[1] += test_step
                keyframe.handle_right[1] += test_step
            z_curve.update()
            bpy.context.view_layer.update()
            test_minimum, _ = evaluated_world_bounds(mesh_objects())
            for keyframe in z_curve.keyframe_points:
                keyframe.co[1] -= test_step
                keyframe.handle_left[1] -= test_step
                keyframe.handle_right[1] -= test_step
            z_curve.update()
            bpy.context.view_layer.update()
            derivative = float(test_minimum.z - before_minimum.z) / test_step
            if abs(derivative) > 1e-8:
                ground_correction = -float(before_minimum.z) / derivative
                for keyframe in z_curve.keyframe_points:
                    keyframe.co[1] += ground_correction
                    keyframe.handle_left[1] += ground_correction
                    keyframe.handle_right[1] += ground_correction
                z_curve.update()
                bpy.context.view_layer.update()
        after_minimum, _ = evaluated_world_bounds(mesh_objects())
        records.append(
            {
                "armature": rig.name,
                "action": action.name,
                "location_fcurves": len(root_curves),
                "changed_keyframes": changed_keyframes,
                "fixed_values": fixed_values,
                "ground_correction_source_units": ground_correction,
                "ground_contact_before": float(before_minimum.z),
                "ground_contact_after": float(after_minimum.z),
                "policy": "in_place_root_translation_locked_to_first_keyframe",
            }
        )
    return {
        "policy": "remove_provider_root_motion_for_in_place_unit_actions",
        "actions": records,
    }


def sanitize_action_scale_channels() -> Dict[str, Any]:
    """Remove provider scale channels that rescale the whole unit in HOI4."""

    records: List[Dict[str, Any]] = []

    for rig in armatures():
        action = rig.animation_data.action if rig.animation_data else None
        if action is None:
            continue
        all_fcurves = list(action_fcurves(action))
        removable = [
            (fcurve, owner)
            for fcurve, owner in all_fcurves
            if "scale" in fcurve.data_path.casefold()
        ]
        paths = [fcurve.data_path for fcurve, _ in removable]
        for fcurve, owner in removable:
            owner.remove(fcurve)
        reset_bones = []
        for pose_bone in rig.pose.bones:
            if any(abs(value - 1.0) > 1e-5 for value in pose_bone.scale):
                reset_bones.append(pose_bone.name)
            pose_bone.scale = (1.0, 1.0, 1.0)
        records.append(
            {
                "armature": rig.name,
                "action": action.name,
                "removed_fcurves": len(removable),
                "removed_paths": paths,
                "reset_pose_scale_bones": reset_bones,
            }
        )
    return {
        "policy": "remove_all_working_action_scale_fcurves",
        "actions": records,
        "remaining_scale_fcurves": sum(
            1
            for rig in armatures()
            if rig.animation_data
            and rig.animation_data.action
            for fcurve, _ in action_fcurves(rig.animation_data.action)
            if "scale" in fcurve.data_path.casefold()
        ),
    }


def world_bounds(objects: Iterable[bpy.types.Object]) -> Tuple[Vector, Vector]:
    corners: List[Vector] = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        # Blender's Object.bound_box can remain stale after provider geometry
        # is triangulated or decimated. Measure the actual mesh vertices so
        # normalization and preview framing cannot silently use old extents.
        corners.extend(obj.matrix_world @ vertex.co for vertex in obj.data.vertices)
    if not corners:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    minimum = Vector((min(item.x for item in corners), min(item.y for item in corners), min(item.z for item in corners)))
    maximum = Vector((max(item.x for item in corners), max(item.y for item in corners), max(item.z for item in corners)))
    return minimum, maximum


def vector_record(value: Vector) -> List[float]:
    return [float(component) for component in value]


def bounds_record(objects: Iterable[bpy.types.Object]) -> Dict[str, List[float]]:
    minimum, maximum = world_bounds(objects)
    return {
        "minimum": vector_record(minimum),
        "maximum": vector_record(maximum),
        "dimensions": vector_record(maximum - minimum),
    }


def object_transform_record(obj: bpy.types.Object) -> Dict[str, Any]:
    return {
        "location": [float(value) for value in obj.location],
        "rotation_euler": [float(value) for value in obj.rotation_euler],
        "scale": [float(value) for value in obj.scale],
        "matrix_world": [[float(value) for value in row] for row in obj.matrix_world],
    }


def require_identity_static_mesh_transforms(tolerance: float = 1e-7) -> Dict[str, Any]:
    """Fail closed when a static export retains any object-space transform."""

    meshes = mesh_objects()
    if not meshes:
        raise RuntimeError("Static mesh validation found no approved hoi4_working mesh objects.")
    failures = []
    records = []
    for obj in meshes:
        transform = object_transform_record(obj)
        flat_values = [
            *transform["location"],
            *transform["rotation_euler"],
            *transform["scale"],
            *(value for row in transform["matrix_world"] for value in row),
        ]
        if not all(math.isfinite(value) for value in flat_values):
            failures.append(f"{obj.name}: non-finite transform")
        if any(value <= 0.0 for value in transform["scale"]):
            failures.append(f"{obj.name}: non-positive or negative scale {transform['scale']}")
        if any(abs(value) > tolerance for value in transform["location"]):
            failures.append(f"{obj.name}: non-identity location {transform['location']}")
        if any(abs(value) > tolerance for value in transform["rotation_euler"]):
            failures.append(f"{obj.name}: non-identity rotation {transform['rotation_euler']}")
        if any(abs(value - 1.0) > tolerance for value in transform["scale"]):
            failures.append(f"{obj.name}: non-identity scale {transform['scale']}")
        records.append({"object": obj.name, "transform": transform})
    if failures:
        raise RuntimeError("Static PDX export transform validation failed: " + "; ".join(failures))
    return {
        "policy": "static_mesh_identity_transform_required",
        "tolerance": tolerance,
        "objects": records,
    }


def evaluated_world_bounds(objects: Iterable[bpy.types.Object]) -> Tuple[Vector, Vector]:
    """Measure evaluated, armature-deformed mesh vertices at the current frame."""

    corners: List[Vector] = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            corners.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    if not corners:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    minimum = Vector((min(item.x for item in corners), min(item.y for item in corners), min(item.z for item in corners)))
    maximum = Vector((max(item.x for item in corners), max(item.y for item in corners), max(item.z for item in corners)))
    return minimum, maximum


def root_objects(objects: List[bpy.types.Object]) -> List[bpy.types.Object]:
    object_set = set(objects)
    return [obj for obj in objects if obj.parent not in object_set]


def normalize_geometry(target_height: float) -> Dict[str, Any]:
    objects = [obj for obj in bpy.context.scene.objects if obj.get("hoi4_working", False)]
    meshes = mesh_objects()
    minimum, maximum = world_bounds(meshes)
    before_height = maximum.z - minimum.z
    if before_height <= 0:
        raise RuntimeError("Candidate has no positive vertical extent.")
    scale = target_height / before_height
    for obj in root_objects(objects):
        obj.scale *= scale
    bpy.context.view_layer.update()
    minimum, maximum = world_bounds(meshes)
    for obj in root_objects(objects):
        obj.location.z -= minimum.z
    bpy.context.view_layer.update()
    return {
        "target_height_m": target_height,
        "scale_factor": scale,
        "bounds_min": list(world_bounds(meshes)[0]),
        "bounds_max": list(world_bounds(meshes)[1]),
        "ground_contact_z": world_bounds(meshes)[0].z,
    }


def constrain_runtime_footprint(
    max_runtime_footprint_m: Optional[float],
    runtime_entity_scale: float,
    policy: str,
) -> Dict[str, Any]:
    """Enforce a map-building footprint after source-height calibration.

    A building's height and map footprint are separate runtime contracts. The
    old pipeline checked only height, which allowed a compound-sized Meshy
    result to be rendered as one ordinary HOI4 building. The fit operation is
    explicit and uniform in X/Y; the default is a hard rejection so future
    work cannot silently distort a model.
    """

    if policy not in {"reject", "fit_to_budget"}:
        raise RuntimeError(f"Unsupported runtime footprint policy: {policy}")
    if max_runtime_footprint_m is None:
        return {
            "status": "not_configured",
            "policy": policy,
            "max_runtime_footprint_m": None,
        }
    maximum = float(max_runtime_footprint_m)
    if maximum <= 0.0:
        raise RuntimeError("The runtime building footprint budget must be positive.")
    if runtime_entity_scale <= 0.0:
        raise RuntimeError("Runtime entity scale must be positive for footprint validation.")
    minimum, maximum_bounds = world_bounds(mesh_objects())
    source_dimensions = maximum_bounds - minimum
    runtime_dimensions = source_dimensions * runtime_entity_scale
    current_footprint = max(float(runtime_dimensions.x), float(runtime_dimensions.y))
    record: Dict[str, Any] = {
        "policy": policy,
        "max_runtime_footprint_m": maximum,
        "source_dimensions_before_fit_m": list(source_dimensions),
        "runtime_dimensions_before_fit_m": list(runtime_dimensions),
        "runtime_footprint_before_fit_m": current_footprint,
        "fit_factor_xy": 1.0,
    }
    if current_footprint > maximum + 1e-6:
        if policy != "fit_to_budget":
            raise RuntimeError(
                "Building footprint exceeds its runtime budget: "
                f"{current_footprint:.6f}m > {maximum:.6f}m. "
                "Use an explicit fit_to_budget decision after visual review."
            )
        factor = maximum / current_footprint
        for obj in root_objects(
            [obj for obj in bpy.context.scene.objects if obj.get("hoi4_working", False)]
        ):
            obj.scale.x *= factor
            obj.scale.y *= factor
        bpy.context.view_layer.update()
        minimum, maximum_bounds = world_bounds(mesh_objects())
        source_dimensions = maximum_bounds - minimum
        runtime_dimensions = source_dimensions * runtime_entity_scale
        record["fit_factor_xy"] = factor
        record["fit_applied"] = True
    else:
        record["fit_applied"] = False
    record["source_dimensions_after_fit_m"] = list(source_dimensions)
    record["runtime_dimensions_after_fit_m"] = list(runtime_dimensions)
    record["runtime_footprint_after_fit_m"] = max(
        float(runtime_dimensions.x), float(runtime_dimensions.y)
    )
    if record["runtime_footprint_after_fit_m"] > maximum + 1e-5:
        raise RuntimeError("The explicit building footprint fit did not meet its budget.")
    return record


def triangulate_and_normals() -> Dict[str, Any]:
    changed = []
    for obj in mesh_objects():
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=list(bm.faces))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        changed.append(obj.name)
    return {"triangulated_objects": changed}


def controlled_decimate(target_triangles: int) -> Dict[str, Any]:
    """Reduce dense provider geometry only to the profile's approved target."""

    before = geometry_metrics()
    if target_triangles <= 0 or before["triangles"] <= target_triangles:
        return {
            "applied": False,
            "target_triangles": target_triangles,
            "before_triangles": before["triangles"],
            "after_triangles": before["triangles"],
            "reason": "within_target_or_disabled",
        }
    objects = mesh_objects()
    if not objects:
        raise RuntimeError("Controlled decimation found no working mesh.")
    target_for_object = max(100, int(target_triangles / len(objects)))
    details = []
    for obj in objects:
        before_object = sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons)
        current = before_object
        if current <= target_for_object:
            continue
        passes = []
        while current > target_for_object and len(passes) < 8:
            ratio = max(0.01, min(1.0, target_for_object / current))
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new("HOI4_BOUNDED_DECIMATE", type="DECIMATE")
            modifier.ratio = ratio
            modifier.use_collapse_triangulate = False
            while obj.modifiers.find(modifier.name) > 0:
                bpy.ops.object.modifier_move_up(modifier=modifier.name)
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            reduced = sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons)
            passes.append(
                {
                    "before_triangles": current,
                    "after_triangles": reduced,
                    "ratio": ratio,
                }
            )
            if reduced >= current:
                raise RuntimeError(
                    f"Controlled decimation stalled for {obj.name}: {current} -> {reduced} triangles."
                )
            current = reduced
        if current > target_for_object:
            raise RuntimeError(
                f"Controlled decimation did not reach the approved target for {obj.name}: "
                f"{current} > {target_for_object} triangles after {len(passes)} passes."
            )
        details.append(
            {
                "object": obj.name,
                "before_triangles": before_object,
                "target_triangles": target_for_object,
                "after_triangles": current,
                "passes": passes,
            }
        )
    triangulate_and_normals()
    after = geometry_metrics()
    if after["triangles"] > target_triangles:
        raise RuntimeError(
            "Controlled decimation exceeded its aggregate approved target: "
            f"{after['triangles']} > {target_triangles} triangles."
        )
    return {
        "applied": True,
        "target_triangles": target_triangles,
        "before_triangles": before["triangles"],
        "after_triangles": after["triangles"],
        "objects": details,
        "method": "bounded iterative Blender DECIMATE collapse followed by explicit triangulation",
    }


def repair_open_surface_boundaries(weld_distance: float = 1e-5) -> Dict[str, Any]:
    """Weld coincident provider seams, then cap only bounded small loops."""

    records: List[Dict[str, Any]] = []
    for obj in mesh_objects():
        before = geometry_metrics_for_object(obj)
        original_data = obj.data.copy()
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        vertices_before_weld = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=weld_distance)
        welded_vertices = max(0, vertices_before_weld - len(bm.verts))
        bm.verts.index_update()
        bm.edges.index_update()
        duplicate_faces = set()
        for edge in bm.edges:
            if len(edge.link_faces) > 2:
                duplicate_faces.update(edge.link_faces[2:])
        if duplicate_faces:
            bmesh.ops.delete(bm, geom=list(duplicate_faces), context="FACES")
        duplicate_faces_removed = len(duplicate_faces)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        obj.data.update()
        welded_metrics = geometry_metrics_for_object(obj)
        welded_data = obj.data.copy()
        weld_rolled_back = welded_metrics["non_manifold_edges"] > before["non_manifold_edges"]
        if weld_rolled_back:
            repaired_data = obj.data
            obj.data = original_data
            if repaired_data.users == 0:
                bpy.data.meshes.remove(repaired_data)
            if welded_data.users == 0:
                bpy.data.meshes.remove(welded_data)
            records.append(
                {
                    "object": obj.name,
                    "boundary_edges_before": before["loose_boundary_edges"],
                    "boundary_edges_after": before["loose_boundary_edges"],
                    "welded_vertices": welded_vertices,
                    "duplicate_faces_removed": duplicate_faces_removed,
                    "welded_boundary_edges": welded_metrics["loose_boundary_edges"],
                    "welded_non_manifold_edges": welded_metrics["non_manifold_edges"],
                    "weld_rolled_back": True,
                    "faces_added": 0,
                    "skipped_components": 0,
                    "rolled_back_non_manifold": True,
                    "non_manifold_edges_before": before["non_manifold_edges"],
                    "non_manifold_edges_after": before["non_manifold_edges"],
                    "triangles_after": before["triangles"],
                }
            )
            continue

        bm.clear()
        bm.from_mesh(obj.data)
        boundary_edges = [edge for edge in bm.edges if len(edge.link_faces) == 1]
        edge_by_id = {id(edge): edge for edge in boundary_edges}
        edges_by_vertex: Dict[int, List[Any]] = {}
        for edge in boundary_edges:
            for vertex in edge.verts:
                edges_by_vertex.setdefault(vertex.index, []).append(edge)
        unvisited = set(edge_by_id)
        components: List[List[Any]] = []
        while unvisited:
            seed_id = next(iter(unvisited))
            stack = [edge_by_id[seed_id]]
            component: List[Any] = []
            while stack:
                edge = stack.pop()
                edge_id = id(edge)
                if edge_id not in unvisited:
                    continue
                unvisited.remove(edge_id)
                component.append(edge)
                for vertex in edge.verts:
                    stack.extend(
                        neighbour
                        for neighbour in edges_by_vertex.get(vertex.index, [])
                        if id(neighbour) in unvisited
                    )
            components.append(component)

        filled_face_count = 0
        skipped_components = 0
        max_bounded_loop_edges = 96
        cap_methods: Dict[str, int] = {}
        component_specs = [
            [tuple(sorted(vertex.index for vertex in edge.verts)) for edge in component]
            for component in components
        ]

        component_rejections = 0
        for component_spec in component_specs:
            vertices = {vertex for edge in component_spec for vertex in edge}
            if (
                len(component_spec) < 3
                or len(component_spec) > max_bounded_loop_edges
                or any(len(edges_by_vertex.get(vertex, [])) != 2 for vertex in vertices)
            ):
                skipped_components += 1
                continue
            candidate_bm = bm.copy()
            candidate_bm.verts.index_update()
            candidate_bm.edges.index_update()
            candidate_edges_by_vertices = {
                frozenset(vertex.index for vertex in edge.verts): edge
                for edge in candidate_bm.edges
            }
            candidate_edges = [
                candidate_edges_by_vertices.get(frozenset(edge))
                for edge in component_spec
            ]
            if any(edge is None for edge in candidate_edges):
                candidate_bm.free()
                skipped_components += 1
                continue
            result = bmesh.ops.holes_fill(
                candidate_bm,
                edges=candidate_edges,
                sides=0,
            ) or {}
            candidate_faces = [face for face in result.get("faces", []) if face.is_valid]
            fill_method = "holes_fill"
            if not candidate_faces:
                result = bmesh.ops.triangle_fill(
                    candidate_bm,
                    edges=candidate_edges,
                    use_beauty=True,
                ) or {}
                candidate_faces = [face for face in result.get("faces", []) if face.is_valid]
                fill_method = "triangle_fill"
            candidate_non_manifold_edges = sum(
                1 for edge in candidate_bm.edges if len(edge.link_faces) > 2
            )
            if candidate_non_manifold_edges > welded_metrics["non_manifold_edges"]:
                candidate_bm.free()
                component_rejections += 1
                skipped_components += 1
                continue
            for face in candidate_faces:
                face.material_index = 0
            bm.free()
            bm = candidate_bm
            filled_face_count += len(candidate_faces)
            cap_methods[fill_method] = cap_methods.get(fill_method, 0) + 1

        degenerate_faces = [face for face in bm.faces if face.calc_area() <= 1e-10]
        if degenerate_faces:
            bmesh.ops.delete(bm, geom=degenerate_faces, context="FACES")
        if filled_face_count or degenerate_faces:
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        after = geometry_metrics_for_object(obj)
        rolled_back_non_manifold = after["non_manifold_edges"] > welded_metrics["non_manifold_edges"]
        if rolled_back_non_manifold:
            # Keep a valid weld when the optional cap pass creates a bad edge.
            repaired_data = obj.data
            obj.data = welded_data
            if repaired_data.users == 0:
                bpy.data.meshes.remove(repaired_data)
            after = geometry_metrics_for_object(obj)
            filled_face_count = 0
        elif welded_data.users == 0:
            bpy.data.meshes.remove(welded_data)
        if original_data.users == 0:
            bpy.data.meshes.remove(original_data)
        records.append(
            {
                "object": obj.name,
                "boundary_edges_before": before["loose_boundary_edges"],
                "boundary_edges_after": after["loose_boundary_edges"],
                "welded_vertices": welded_vertices,
                "duplicate_faces_removed": duplicate_faces_removed,
                "welded_boundary_edges": welded_metrics["loose_boundary_edges"],
                "welded_non_manifold_edges": welded_metrics["non_manifold_edges"],
                "weld_rolled_back": False,
                "faces_added": filled_face_count,
                "skipped_components": skipped_components,
                "component_rejections": component_rejections,
                "cap_methods": cap_methods,
                "rolled_back_non_manifold": rolled_back_non_manifold,
                "non_manifold_edges_before": before["non_manifold_edges"],
                "degenerate_faces_removed": len(degenerate_faces),
                "non_manifold_edges_after": after["non_manifold_edges"],
                "triangles_after": after["triangles"],
            }
        )
    return {
        "applied": any(record["welded_vertices"] or record["faces_added"] for record in records),
        "method": f"bmesh remove_doubles at {weld_distance:g}, remove duplicate-overlap faces, then bounded holes_fill/triangle_fill on loops up to 96 edges with cap-only non-manifold rollback",
        "objects": records,
    }


def topology_metrics_from_bmesh(bm: bmesh.types.BMesh) -> Dict[str, Any]:
    boundary_edges = [edge for edge in bm.edges if len(edge.link_faces) == 1]
    loose_edges = len(boundary_edges)
    non_manifold_edges = sum(1 for edge in bm.edges if len(edge.link_faces) > 2)
    degenerate_faces = sum(1 for face in bm.faces if face.calc_area() <= 1e-10)
    edges_by_vertex: Dict[int, List[Any]] = {}
    boundary_by_id = {id(edge): edge for edge in boundary_edges}
    for edge in boundary_edges:
        for vertex in edge.verts:
            edges_by_vertex.setdefault(vertex.index, []).append(edge)
    unvisited = set(boundary_by_id)
    boundary_components = []
    while unvisited:
        seed_id = next(iter(unvisited))
        stack = [boundary_by_id[seed_id]]
        component = []
        while stack:
            edge = stack.pop()
            edge_id = id(edge)
            if edge_id not in unvisited:
                continue
            unvisited.remove(edge_id)
            component.append(edge)
            for vertex in edge.verts:
                stack.extend(
                    neighbour
                    for neighbour in edges_by_vertex.get(vertex.index, [])
                    if id(neighbour) in unvisited
                )
        vertices = {vertex.index for edge in component for vertex in edge.verts}
        degrees = [len(edges_by_vertex.get(vertex, [])) for vertex in vertices]
        boundary_components.append(
            {
                "edges": len(component),
                "vertices": len(vertices),
                "closed_simple_cycle": bool(degrees) and all(degree == 2 for degree in degrees),
                "endpoint_vertices": sum(degree == 1 for degree in degrees),
                "branch_vertices": sum(degree > 2 for degree in degrees),
                "max_vertex_degree": max(degrees, default=0),
                "perimeter": sum(edge.calc_length() for edge in component),
            }
        )
    zero_length_normals = sum(1 for face in bm.faces if face.normal.length <= 1e-8)
    return {
        "loose_boundary_edges": loose_edges,
        "non_manifold_edges": non_manifold_edges,
        "degenerate_faces": degenerate_faces,
        "triangles": sum(max(0, len(face.verts) - 2) for face in bm.faces),
        "boundary_component_count": len(boundary_components),
        "closed_boundary_component_count": sum(
            1 for component in boundary_components if component["closed_simple_cycle"]
        ),
        "branched_boundary_component_count": sum(
            1 for component in boundary_components if component["branch_vertices"]
        ),
        "max_boundary_component_edges": max(
            (component["edges"] for component in boundary_components), default=0
        ),
        "zero_length_normals": zero_length_normals,
    }


def geometry_metrics_for_object(obj: bpy.types.Object) -> Dict[str, Any]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = topology_metrics_from_bmesh(bm)
    bm.free()
    return result


def position_welded_geometry_metrics_for_object(
    obj: bpy.types.Object,
    weld_distance: float,
) -> Dict[str, Any]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vertices_before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=weld_distance)
    bm.verts.ensure_lookup_table()
    result = topology_metrics_from_bmesh(bm)
    result["vertices_before"] = vertices_before
    result["vertices_after_position_weld"] = len(bm.verts)
    result["weld_distance"] = weld_distance
    bm.free()
    return result


def geometry_metrics(
    working_only: bool = True,
    position_weld_distance: Optional[float] = None,
) -> Dict[str, Any]:
    meshes = mesh_objects(working_only=working_only)
    vertices = sum(len(obj.data.vertices) for obj in meshes)
    polygons = sum(len(obj.data.polygons) for obj in meshes)
    triangles = sum(sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons) for obj in meshes)
    loose_edges = 0
    non_manifold_edges = 0
    degenerate_faces = 0
    boundary_component_count = 0
    closed_boundary_component_count = 0
    branched_boundary_component_count = 0
    max_boundary_component_edges = 0
    zero_length_normals = 0
    position_welded = []
    for obj in meshes:
        object_metrics = geometry_metrics_for_object(obj)
        loose_edges += object_metrics["loose_boundary_edges"]
        non_manifold_edges += object_metrics["non_manifold_edges"]
        degenerate_faces += object_metrics["degenerate_faces"]
        zero_length_normals += object_metrics["zero_length_normals"]
        boundary_component_count += object_metrics["boundary_component_count"]
        closed_boundary_component_count += object_metrics["closed_boundary_component_count"]
        branched_boundary_component_count += object_metrics["branched_boundary_component_count"]
        max_boundary_component_edges = max(
            max_boundary_component_edges, object_metrics["max_boundary_component_edges"]
        )
        if position_weld_distance is not None:
            position_welded.append(
                {
                    "object": obj.name,
                    **position_welded_geometry_metrics_for_object(obj, position_weld_distance),
                }
            )
    minimum, maximum = world_bounds(meshes)
    result = {
        "objects": len(meshes),
        "vertices": vertices,
        "polygons": polygons,
        "triangles": triangles,
        "loose_boundary_edges": loose_edges,
        "non_manifold_edges": non_manifold_edges,
        "degenerate_faces": degenerate_faces,
        "boundary_component_count": boundary_component_count,
        "closed_boundary_component_count": closed_boundary_component_count,
        "branched_boundary_component_count": branched_boundary_component_count,
        "max_boundary_component_edges": max_boundary_component_edges,
        "zero_length_normals": zero_length_normals,
        "bounds_min": list(minimum),
        "bounds_max": list(maximum),
        "dimensions": list(maximum - minimum),
        "negative_scale_objects": [
            obj.name for obj in bpy.context.scene.objects
            if (not working_only or obj.get("hoi4_working", False)) and any(value < 0 for value in obj.scale)
        ],
        "uv_layers": {
            obj.name: [layer.name for layer in obj.data.uv_layers]
            for obj in meshes
        },
    }
    if position_weld_distance is not None:
        result["position_welded_topology"] = {
            "policy": "diagnostic_position_weld_only; exported UV and normal seams remain unchanged",
            "weld_distance": position_weld_distance,
            "objects": position_welded,
            "loose_boundary_edges": sum(item["loose_boundary_edges"] for item in position_welded),
            "non_manifold_edges": sum(item["non_manifold_edges"] for item in position_welded),
            "degenerate_faces": sum(item["degenerate_faces"] for item in position_welded),
        }
    return result


def action_metrics() -> Dict[str, Any]:
    values: List[Dict[str, Any]] = []

    def action_fcurve_count(action: bpy.types.Action) -> int:
        legacy = getattr(action, "fcurves", None)
        if legacy is not None:
            return sum(1 for fcurve in legacy if "scale" in fcurve.data_path.casefold())
        return sum(
            1
            for layer in getattr(action, "layers", [])
            for strip in getattr(layer, "strips", [])
            for channelbag in getattr(strip, "channelbags", [])
            for fcurve in getattr(channelbag, "fcurves", [])
            if "scale" in fcurve.data_path.casefold()
        )

    for action in bpy.data.actions:
        start, end = action.frame_range
        values.append(
            {
                "name": action.name,
                "frame_start": int(math.floor(start)),
                "frame_end": int(math.ceil(end)),
                "frame_count": int(math.ceil(end) - math.floor(start) + 1),
                "fps": bpy.context.scene.render.fps,
                "scale_fcurves": action_fcurve_count(action),
            }
        )
    return {
        "armatures": [
            {"name": obj.name, "bones": len(obj.data.bones)}
            for obj in armatures()
        ],
        "actions": values,
    }


def evaluated_action_metrics() -> List[Dict[str, Any]]:
    """Measure evaluated bounds at representative frames for deformation QA."""

    meshes = mesh_objects()
    rigs = armatures()
    if not meshes or not rigs:
        return []
    scene = bpy.context.scene
    original_frame = scene.frame_current
    records: List[Dict[str, Any]] = []
    for rig in rigs:
        rig.animation_data_create()
        original_action = rig.animation_data.action
        actions = [
            action
            for action in bpy.data.actions
            if (
                ("WORKING" in action.name and action.name.startswith("Armature|"))
                or action.name.startswith("creature_")
                or action.name.startswith("black_plague_rat_")
            )
        ]
        for action in actions:
            rig.animation_data.action = action
            start, end = action.frame_range
            frames = sorted({int(math.floor(start)), int(math.ceil((start + end) * 0.5)), int(math.ceil(end))})
            frame_records = []
            for frame in frames:
                scene.frame_set(frame)
                depsgraph = bpy.context.evaluated_depsgraph_get()
                corners: List[Vector] = []
                for obj in meshes:
                    evaluated = obj.evaluated_get(depsgraph)
                    evaluated_mesh = evaluated.to_mesh()
                    try:
                        corners.extend(
                            evaluated.matrix_world @ vertex.co
                            for vertex in evaluated_mesh.vertices
                        )
                    finally:
                        evaluated.to_mesh_clear()
                if corners:
                    minimum = Vector((min(point.x for point in corners), min(point.y for point in corners), min(point.z for point in corners)))
                    maximum = Vector((max(point.x for point in corners), max(point.y for point in corners), max(point.z for point in corners)))
                    frame_records.append(
                        {
                            "frame": frame,
                            "bounds_min": list(minimum),
                            "bounds_max": list(maximum),
                            "dimensions": list(maximum - minimum),
                        }
                    )
            records.append(
                {
                    "armature": rig.name,
                    "action": action.name,
                    "frames": frame_records,
                }
            )
        rig.animation_data.action = original_action
    scene.frame_set(original_frame)
    return records


def weight_metrics() -> List[Dict[str, Any]]:
    """Report skinning coverage before a runtime export is trusted."""

    records: List[Dict[str, Any]] = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        armature_modifiers = [
            modifier
            for modifier in obj.modifiers
            if modifier.type == "ARMATURE" and modifier.object is not None
        ]
        bone_names = set()
        armature_names = []
        for modifier in armature_modifiers:
            armature = modifier.object
            armature_names.append(armature.name)
            bone_names.update(bone.name for bone in armature.data.bones)

        group_names = {group.index: group.name for group in obj.vertex_groups}
        influence_histogram: Dict[str, int] = {}
        zero_weight_vertices = 0
        vertices_over_four = 0
        vertices_with_non_bone_groups = 0
        min_weight_sum = None
        max_weight_sum = None
        for vertex in obj.data.vertices:
            weights = []
            has_non_bone_group = False
            for assignment in vertex.groups:
                group_name = group_names.get(assignment.group)
                if group_name is None:
                    continue
                weights.append(float(assignment.weight))
                if bone_names and group_name not in bone_names:
                    has_non_bone_group = True
            influence_count = len(weights)
            influence_key = str(influence_count)
            influence_histogram[influence_key] = influence_histogram.get(influence_key, 0) + 1
            if influence_count > 4:
                vertices_over_four += 1
            if has_non_bone_group:
                vertices_with_non_bone_groups += 1
            weight_sum = sum(weights)
            if weight_sum <= 1e-8:
                zero_weight_vertices += 1
            min_weight_sum = weight_sum if min_weight_sum is None else min(min_weight_sum, weight_sum)
            max_weight_sum = weight_sum if max_weight_sum is None else max(max_weight_sum, weight_sum)

        records.append(
            {
                "object": obj.name,
                "vertices": len(obj.data.vertices),
                "armature_modifiers": armature_names,
                "vertex_groups": len(obj.vertex_groups),
                "influence_histogram": dict(sorted(influence_histogram.items(), key=lambda item: int(item[0]))),
                "vertices_over_four_influences": vertices_over_four,
                "zero_weight_vertices": zero_weight_vertices,
                "vertices_with_non_bone_groups": vertices_with_non_bone_groups,
                "weight_sum_min": min_weight_sum,
                "weight_sum_max": max_weight_sum,
            }
        )
    return records


def sanitize_working_weights() -> Dict[str, Any]:
    """Keep PDX-compatible skinning influences without altering provider geometry."""

    records: List[Dict[str, Any]] = []
    for obj in mesh_objects():
        armature_modifier = next(
            (
                modifier
                for modifier in obj.modifiers
                if modifier.type == "ARMATURE" and modifier.object is not None
            ),
            None,
        )
        if armature_modifier is None:
            continue
        armature = armature_modifier.object
        bone_names = {bone.name for bone in armature.data.bones}
        root_bone = next(
            (bone for bone in armature.data.bones if bone.parent is None),
            None,
        )
        if root_bone is None:
            raise RuntimeError(f"Armature {armature.name} has no root bone for zero-weight repair.")
        root_group = obj.vertex_groups.get(root_bone.name)
        if root_group is None:
            root_group = obj.vertex_groups.new(name=root_bone.name)

        over_four_before = 0
        zero_before = 0
        removed_influences = 0
        normalized_vertices = 0
        zero_weight_repaired = 0
        for vertex in obj.data.vertices:
            assignments = []
            for assignment in list(vertex.groups):
                group = obj.vertex_groups.get(obj.vertex_groups[assignment.group].name)
                if group is None or group.name not in bone_names:
                    if group is not None:
                        group.remove([vertex.index])
                    removed_influences += 1
                    continue
                weight = max(0.0, float(assignment.weight))
                if weight > 0.0:
                    assignments.append((group, weight))

            if len(assignments) > 4:
                over_four_before += 1
                kept = sorted(assignments, key=lambda item: (-item[1], item[0].name))[:4]
                kept_names = {group.name for group, _ in kept}
                removed = [
                    (group, weight)
                    for group, weight in assignments
                    if group.name not in kept_names
                ]
                for group, _ in removed:
                    group.remove([vertex.index])
                removed_influences += len(removed)
                assignments = kept

            total = sum(weight for _, weight in assignments)
            if total <= 1e-8:
                zero_before += 1
                root_group.add([vertex.index], 1.0, "REPLACE")
                zero_weight_repaired += 1
                continue

            for group, weight in assignments:
                group.add([vertex.index], weight / total, "REPLACE")
            normalized_vertices += 1

        records.append(
            {
                "object": obj.name,
                "armature": armature.name,
                "root_bone": root_bone.name,
                "vertices_over_four_before": over_four_before,
                "zero_weight_vertices_before": zero_before,
                "removed_influences": removed_influences,
                "normalized_vertices": normalized_vertices,
                "zero_weight_vertices_repaired": zero_weight_repaired,
            }
        )
    return {
        "policy": "keep_four_strongest_bone_influences_and_renormalize",
        "objects": records,
        "weights_after": weight_metrics(),
    }


def sanitize_working_materials() -> Dict[str, Any]:
    """Remove glTF-only emission and metallic state from PDX runtime materials."""

    allowed_nodes = {
        "HOI4_DIFFUSE_TEXTURE",
        "HOI4_SPECULAR_TEXTURE",
        "HOI4_NORMAL_TEXTURE",
        "HOI4_NORMAL_MAP",
    }
    records: List[Dict[str, Any]] = []
    for obj in mesh_objects():
        for material in obj.data.materials:
            if material is None or not material.get("hoi4_pdx_shader"):
                continue
            ensure_material_nodes(material)
            changed = []
            for node in material.node_tree.nodes:
                if node.bl_idname != "ShaderNodeBsdfPrincipled":
                    continue
                for input_name in ("Metallic", "Emission", "Emission Color", "Emission Strength", "Alpha"):
                    socket = node.inputs.get(input_name)
                    if socket is None:
                        continue
                    for link in list(socket.links):
                        material.node_tree.links.remove(link)
                    if input_name == "Metallic":
                        socket.default_value = 0.0
                    elif input_name in {"Emission", "Emission Color"}:
                        socket.default_value = (0.0, 0.0, 0.0, 1.0)
                    elif input_name == "Emission Strength":
                        socket.default_value = 0.0
                    elif input_name == "Alpha":
                        socket.default_value = 1.0
                    changed.append(input_name)
            removed_nodes = []
            for node in list(material.node_tree.nodes):
                if node.bl_idname == "ShaderNodeTexImage" and node.name not in allowed_nodes:
                    removed_nodes.append(node.name)
                    material.node_tree.nodes.remove(node)
            records.append(
                {
                    "material": material.name,
                    "object": obj.name,
                    "changed_inputs": sorted(set(changed)),
                    "removed_nodes": sorted(removed_nodes),
                }
            )
    return {"policy": "pdx_mesh_advanced_opaque_non_emissive", "materials": records}


def image_nodes() -> List[Tuple[bpy.types.Material, bpy.types.Image]]:
    values: List[Tuple[bpy.types.Material, bpy.types.Image]] = []
    seen = set()
    for material in bpy.data.materials:
        if not material.get("hoi4_pdx_shader"):
            continue
        for node in material.node_tree.nodes:
            image = getattr(node, "image", None)
            if image is None or image.name in seen:
                continue
            seen.add(image.name)
            values.append((material, image))
    return values


def camera_point_at(camera: bpy.types.Object, target: Vector) -> None:
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_previews(
    job: Path,
    runtime_stem: str,
    view_names: List[str] | None = None,
    *,
    working_only: bool = True,
) -> List[str]:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.015, 0.02, 0.03)

    meshes = mesh_objects(working_only=working_only)
    if not meshes:
        object_class = "working" if working_only else "imported runtime-proof"
        raise RuntimeError(f"Preview rendering found no {object_class} mesh objects.")
    minimum, maximum = world_bounds(meshes)
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    object_height = max(float(dimensions.z), 0.1)
    ground_extent = max(8.0, float(max(dimensions.x, dimensions.y)) * 2.0)

    evidence_collection = new_collection("QA_EVIDENCE")
    ground_mesh = bpy.data.meshes.new("QA_Ground_Mesh")
    ground_mesh.from_pydata(
        [
            (-ground_extent, -ground_extent, minimum.z),
            (ground_extent, -ground_extent, minimum.z),
            (ground_extent, ground_extent, minimum.z),
            (-ground_extent, ground_extent, minimum.z),
        ],
        [],
        [(0, 1, 2, 3)],
    )
    ground = bpy.data.objects.new("QA_Ground", ground_mesh)
    evidence_collection.objects.link(ground)
    ground.hide_render = False
    ground_mat = bpy.data.materials.new("QA_Ground_Material")
    ground_mat.diffuse_color = (0.02, 0.025, 0.03, 1.0)
    ground.data.materials.append(ground_mat)

    lights = []
    light_energy_scale = max(
        0.02,
        min(1.0, (object_height / PREVIEW_LIGHT_REFERENCE_HEIGHT) ** 2),
    )
    for name, location, energy, size in (
        ("QA_Key", (object_height * 0.8, -object_height * 0.8, object_height * 1.2), 1200.0, object_height * 0.7),
        ("QA_Fill", (-object_height * 0.8, -object_height * 0.4, object_height * 0.7), 700.0, object_height * 0.7),
        ("QA_Rim", (0.0, object_height * 0.8, object_height * 1.0), 900.0, object_height * 0.6),
    ):
        light_data = bpy.data.lights.new(name, type="AREA")
        light_data.energy = energy * light_energy_scale
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(name, light_data)
        evidence_collection.objects.link(light)
        light.location = location
        camera_point_at(light, center)
        lights.append(light)

    camera_data = bpy.data.cameras.new("QA_Camera")
    camera = bpy.data.objects.new("QA_Camera", camera_data)
    evidence_collection.objects.link(camera)
    scene.camera = camera
    camera_data.lens = 55

    # Frame the whole object regardless of whether it is a 1.5 m prop or a
    # vanilla-calibrated 7.35-unit source mesh.
    preview_angle = math.radians(38.0)
    fit_distance = object_height / (2.0 * math.tan(preview_angle * 0.5) * 0.78)
    fit_distance = max(fit_distance, float(max(dimensions.x, dimensions.y)) * 1.5, 4.0)

    available_views = [
            ("front", (center.x, center.y - fit_distance, center.z)),
            ("rear", (center.x, center.y + fit_distance, center.z)),
            ("left", (center.x - fit_distance, center.y, center.z)),
            ("right", (center.x + fit_distance, center.y, center.z)),
            ("top", (center.x, center.y - fit_distance * 0.7, maximum.z + fit_distance * 0.7)),
            ("underside", (center.x, center.y - fit_distance * 0.7, minimum.z - fit_distance * 0.35)),
            ("three_quarter", (center.x + fit_distance * 0.75, center.y - fit_distance * 0.75, center.z + object_height * 0.08)),
        ]
    selected_views = set(view_names or [])
    for index, location in enumerate(
        [item for item in available_views if not selected_views or item[0] in selected_views]
    ):
        name, location = location
        camera.location = location
        camera_point_at(camera, center)
        scene.render.filepath = str(job / "blender" / "previews" / f"{runtime_stem}_{name}.png")
        output = Path(scene.render.filepath)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            try:
                output.unlink()
            except OSError:
                # OneDrive or an image viewer can briefly hold the previous
                # preview. Keep the existing evidence and write this pass to
                # a deterministic sibling so the Blender checkpoint remains
                # reviewable instead of failing the whole export.
                output = output.with_name(f"{output.stem}_rerender.png")
                scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)

    light_data = [light.data for light in lights]
    for obj in list(evidence_collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(evidence_collection)
    if ground_mesh.users == 0:
        bpy.data.meshes.remove(ground_mesh)
    if ground_mat.users == 0:
        bpy.data.materials.remove(ground_mat)
    for data in light_data:
        if data and data.users == 0:
            bpy.data.lights.remove(data)
    if camera_data.users == 0:
        bpy.data.cameras.remove(camera_data)
    return sorted(
        str(path.relative_to(job)).replace("\\", "/")
        for path in (job / "blender" / "previews").glob(f"{runtime_stem}_*.png")
    )


def prepare(req: Dict[str, Any], pdx: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    source = within(job, payload["source_rel"])
    runtime_stem = safe_name(payload["runtime_stem"])
    clear_scene()
    source_collection = new_collection("PROVIDER_SOURCE")
    working_collection = new_collection("WORKING")
    vanilla_reference = import_vanilla_reference(job, payload, pdx)
    imported = import_candidate(source)
    excluded_names = {str(name) for name in payload.get("excluded_provider_objects", [])}
    geometry_source = None
    geometry_transfer = None
    if payload.get("geometry_source_rel"):
        geometry_source = within(job, str(payload["geometry_source_rel"]))
        imported_geometry = import_candidate(geometry_source)
        imported_rig = imported
        imported = imported_geometry + imported_rig
        geometry_candidates = [
            obj for obj in imported_geometry
            if obj.type == "MESH" and obj.name not in excluded_names
        ]
        rig_mesh_candidates = [
            obj for obj in imported_rig
            if obj.type == "MESH" and obj.name not in excluded_names
        ]
        armature_candidates = [obj for obj in imported_rig if obj.type == "ARMATURE"]
        if len(geometry_candidates) != 1 or len(rig_mesh_candidates) != 1 or len(armature_candidates) != 1:
            raise RuntimeError(
                "Dual-source humanoid preparation requires one geometry mesh, one rig mesh, and one armature."
            )
        working_source = [geometry_candidates[0], armature_candidates[0]]
        for obj in imported:
            move_to_collection(obj, source_collection)
        working = duplicate_hierarchy(working_source, source_collection, working_collection)
        working_by_source = {
            str(obj.get("hoi4_source_object")): obj
            for obj in working
        }
        target_mesh = working_by_source[geometry_candidates[0].name]
        target_armature = working_by_source[armature_candidates[0].name]
        geometry_transfer = bind_geometry_to_existing_rig(
            rig_mesh_candidates[0],
            target_mesh,
            target_armature,
        )
    else:
        for obj in imported:
            move_to_collection(obj, source_collection)
        working_source = [obj for obj in imported if obj.name not in excluded_names]
        if not working_source:
            raise RuntimeError("Provider-object exclusion removed the entire candidate.")
        working = duplicate_hierarchy(working_source, source_collection, working_collection)
    for obj in imported:
        if obj not in working_source:
            obj["hoi4_provider_excluded"] = True
            obj.hide_render = True
            obj.hide_set(True)

    source_blend = job / "blender" / "source" / f"{runtime_stem}_provider_source.blend"
    save_blend(source_blend)
    imported_metrics = geometry_metrics()
    imported_checkpoint = job / "blender" / "checkpoints" / "00_imported_candidate.blend"
    save_blend(imported_checkpoint)

    target_height = float(payload["target_height_m"])
    runtime_entity_scale = float(payload.get("runtime_entity_scale", 1.0))
    if runtime_entity_scale <= 0.0:
        raise RuntimeError("Candidate preparation requires a positive runtime entity scale.")
    normalize = normalize_geometry(target_height)
    footprint = constrain_runtime_footprint(
        payload.get("max_runtime_footprint_m"),
        runtime_entity_scale,
        str(payload.get("runtime_footprint_policy", "reject")),
    )
    triangulation = triangulate_and_normals()
    weld_distance = float(payload.get("topology_weld_distance", 1e-5))
    pre_reduction_topology_repair = None
    if payload.get("repair_before_reduction", False):
        pre_reduction_topology_repair = repair_open_surface_boundaries(weld_distance)
    reduction = controlled_decimate(int(payload.get("target_triangles", 0)))
    topology_repair = repair_open_surface_boundaries(weld_distance)
    if pre_reduction_topology_repair is not None:
        topology_repair = {
            "applied": bool(
                pre_reduction_topology_repair.get("applied") or topology_repair.get("applied")
            ),
            "method": "pre-reduction seam weld followed by post-reduction bounded repair",
            "weld_distance": weld_distance,
            "pre_reduction": pre_reduction_topology_repair,
            "post_reduction": topology_repair,
        }
    geometry = geometry_metrics()
    if vanilla_reference:
        final_height = float(geometry["dimensions"][2])
        vanilla_reference["final_mesh_height"] = final_height
        vanilla_reference["pilot_entity_scale"] = runtime_entity_scale
        vanilla_reference["pilot_target_runtime_height"] = target_height * runtime_entity_scale
        vanilla_reference["final_effective_runtime_height"] = final_height * runtime_entity_scale
        vanilla_reference["final_runtime_height_delta"] = (
            vanilla_reference["final_effective_runtime_height"]
            - vanilla_reference["pilot_target_runtime_height"]
        )
    geometry_checkpoint = job / "blender" / "checkpoints" / "01_geometry_approved.blend"
    save_blend(geometry_checkpoint)

    materials = tag_pdx_materials(pdx)
    texture_bindings = bind_texture_sources(job, payload)
    materials["texture_bindings"] = texture_bindings
    if payload["asset_kind"] in {"humanoid", "creature"} and payload.get("texture_source_rels") and not image_nodes():
        raise RuntimeError(
            "Humanoid preparation produced no image-backed material. Refusing to export a black unit."
        )
    material_checkpoint = job / "blender" / "checkpoints" / "02_materials_approved.blend"
    save_blend(material_checkpoint)

    scale_sanitization = (
        sanitize_action_scale_channels()
        if payload["asset_kind"] == "humanoid"
        else {"policy": "not_applicable", "actions": [], "remaining_scale_fcurves": 0}
    )
    actions = action_metrics()
    actions["scale_sanitization"] = scale_sanitization
    actions["root_translation_sanitization"] = (
        sanitize_root_translation_channels()
        if payload["asset_kind"] == "humanoid"
        else {"policy": "not_applicable", "actions": []}
    )
    if payload["asset_kind"] == "humanoid" and scale_sanitization["remaining_scale_fcurves"]:
        raise RuntimeError("Humanoid action export still contains scale channels after sanitization.")
    rig_checkpoint = None
    if payload["asset_kind"] == "humanoid":
        rig_checkpoint = job / "blender" / "checkpoints" / "03_rig_approved.blend"
        save_blend(rig_checkpoint)
        action_checkpoint = job / "blender" / "checkpoints" / "04_actions_approved.blend"
        save_blend(action_checkpoint)
    pre_export = job / "blender" / "checkpoints" / "05_pre_export.blend"
    previews = render_previews(job, runtime_stem) if payload.get("render_previews", True) else []
    save_blend(pre_export)

    report = {
        "asset_kind": payload["asset_kind"],
        "source": str(source.relative_to(job)).replace("\\", "/"),
        "geometry_source": (
            str(geometry_source.relative_to(job)).replace("\\", "/")
            if geometry_source
            else None
        ),
        "source_objects": len(imported),
        "excluded_provider_objects": sorted(excluded_names),
        "vanilla_reference": vanilla_reference,
        "working_source_objects": len(working_source),
        "working_objects": len(working),
        "geometry_transfer": geometry_transfer,
        "imported_geometry": imported_metrics,
        "normalization": normalize,
        "runtime_footprint": footprint,
        "runtime_calibration": {
            "mesh_target_height_m": target_height,
            "entity_scale": runtime_entity_scale,
            "effective_runtime_height_m": target_height * runtime_entity_scale,
            "policy": "bake the calibrated pilot source height into mesh coordinates and preserve the specified vanilla entity scale",
        },
        "triangulation": triangulation,
        "controlled_reduction": reduction,
        "topology_repair": topology_repair,
        "geometry": geometry,
        "materials": materials,
        "rig_and_actions": actions,
        "checkpoints": {
            "source": str(source_blend.relative_to(job)).replace("\\", "/"),
            "imported": str(imported_checkpoint.relative_to(job)).replace("\\", "/"),
            "geometry": str(geometry_checkpoint.relative_to(job)).replace("\\", "/"),
            "materials": str(material_checkpoint.relative_to(job)).replace("\\", "/"),
            "rig": str(rig_checkpoint.relative_to(job)).replace("\\", "/") if rig_checkpoint else None,
            "pre_export": str(pre_export.relative_to(job)).replace("\\", "/"),
        },
        "previews": previews,
        "io_pdx_mesh_manifest": pdx["manifest"],
    }
    report_path = job / "blender" / "reports" / f"{runtime_stem}_prepare.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def inspect(req: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    blend = within(job, req["payload"]["blend_rel"])
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    materials = []
    for material in bpy.data.materials:
        if not material.use_nodes or material.node_tree is None:
            continue
        shader = next(
            (node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"),
            None,
        )
        input_links = {}
        surface_links = []
        principled_defaults = {}
        output = next(
            (node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeOutputMaterial"),
            None,
        )
        if output is not None:
            surface_links = [
                {
                    "node": link.from_node.name,
                    "socket": link.from_socket.name,
                }
                for link in output.inputs["Surface"].links
            ]
        if shader is not None:
            for input_name in (
                "Base Color",
                "Metallic",
                "Roughness",
                "IOR",
                "Alpha",
                "Normal",
                "Emission Color",
                "Emission Strength",
            ):
                socket = shader.inputs.get(input_name)
                if socket is None:
                    continue
                input_links[input_name] = [
                    {
                        "node": link.from_node.name,
                        "socket": link.from_socket.name,
                    }
                    for link in socket.links
                ]
            for input_name in ("Metallic", "Specular IOR Level", "Emission Color", "Emission Strength"):
                socket = shader.inputs.get(input_name)
                if socket is not None and not socket.is_linked:
                    value = socket.default_value
                    principled_defaults[input_name] = list(value) if hasattr(value, "__len__") else value
        materials.append(
            {
                "name": material.name,
                "principled_inputs": input_links,
                "principled_defaults": principled_defaults,
                "surface_links": surface_links,
                "images": [
                    {
                        "node": node.name,
                        "image": node.image.name if node.image else None,
                        "filepath": node.image.filepath if node.image else None,
                    }
                    for node in material.node_tree.nodes
                    if node.bl_idname == "ShaderNodeTexImage"
                ],
            }
        )
    def object_transform(obj: bpy.types.Object) -> Dict[str, Any]:
        return {
            "location": [float(value) for value in obj.location],
            "rotation_euler": [float(value) for value in obj.rotation_euler],
            "scale": [float(value) for value in obj.scale],
            "dimensions": [float(value) for value in obj.dimensions],
            "matrix_world": [
                [float(value) for value in row]
                for row in obj.matrix_world
            ],
            "hidden": bool(obj.hide_get()),
            "hoi4_working": bool(obj.get("hoi4_working", False)),
            "hoi4_source_object": obj.get("hoi4_source_object"),
        }

    preview_paths = []
    action_name = str(req["payload"].get("action_name") or "")
    if action_name:
        rigs = armatures()
        action = bpy.data.actions.get(action_name)
        if len(rigs) != 1 or action is None:
            raise RuntimeError(f"Action inspection selection failed for {action_name}.")
        rigs[0].animation_data_create()
        rigs[0].animation_data.action = action
        requested_frame = int(req["payload"].get("preview_frame", -1))
        if requested_frame < 0:
            start, end = action.frame_range
            requested_frame = int(round((start + end) * 0.5))
        bpy.context.scene.frame_set(requested_frame)
        bpy.context.view_layer.update()
    if req["payload"].get("render_previews"):
        runtime_stem = safe_name(str(req["payload"].get("runtime_stem") or blend.stem))
        preview_paths = render_previews(job, runtime_stem, req["payload"].get("preview_view_names") or None)
    return {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "objects": [
            {
                "name": obj.name,
                "type": obj.type,
                "parent": obj.parent.name if obj.parent else None,
                "parent_type": obj.parent_type if obj.parent else None,
                "transform": object_transform(obj),
                "modifiers": [
                    {
                        "name": modifier.name,
                        "type": modifier.type,
                        "object": modifier.object.name if getattr(modifier, "object", None) else None,
                    }
                    for modifier in obj.modifiers
                ],
            }
            for obj in bpy.context.scene.objects
        ],
        "geometry": geometry_metrics(),
        "rig_and_actions": action_metrics(),
        "evaluated_actions": evaluated_action_metrics(),
        "weights": weight_metrics(),
        "materials": materials,
        "pose_bones": [
            {
                "armature": rig.name,
                "bone": bone.name,
                "head": list(rig.matrix_world @ bone.head),
                "tail": list(rig.matrix_world @ bone.tail),
            }
            for rig in armatures()
            for bone in rig.pose.bones
        ],
        "previews": preview_paths,
    }


def extract_textures(req: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    processed = job / "textures" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    records = []
    image_paths: Dict[str, str] = {}
    if not payload.get("rewrite_to_dds"):
        for material, image in image_nodes():
            filename = safe_name(Path(image.name).stem) + ".png"
            output = processed / filename
            if image.packed_file is not None or image.source == "GENERATED":
                image.save_render(filepath=str(output))
            else:
                original = Path(bpy.path.abspath(image.filepath))
                if original.exists() and original.suffix.lower() in {".png", ".jpg", ".jpeg", ".tga", ".tif", ".tiff"}:
                    if original.resolve() != output.resolve():
                        if output.exists():
                            if not output.is_file():
                                raise RuntimeError(f"Processed texture target is not a file: {output}")
                            output.unlink()
                        shutil.copy2(original, output)
                else:
                    image.save_render(filepath=str(output))
            image.filepath = str(output)
            image.source = "FILE"
            image_paths[image.name] = str(output.relative_to(job)).replace("\\", "/")
            records.append(
                {
                    "material": material.name,
                    "image": image.name,
                    "processed_png": image_paths[image.name],
                    "bytes": output.stat().st_size,
                }
            )
    if payload.get("rewrite_to_dds"):
        dds_map = payload.get("dds_map", {})
        rename_images = bool(payload.get("rename_images", False))
        for _, image in list(image_nodes()):
            original_name = image.name
            dds_rel = dds_map.get(original_name)
            if dds_rel:
                image.filepath = str(within(job, dds_rel))
                image.source = "FILE"
                if rename_images:
                    image.name = Path(dds_rel).stem
    save_blend(blend)
    report = {"blend": str(blend.relative_to(job)).replace("\\", "/"), "textures": records}
    report_path = job / "blender" / "reports" / "textures.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def bake_static_mesh_transforms(req: Dict[str, Any]) -> Dict[str, Any]:
    """Bake approved static-building object transforms into mesh data."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    output = within(job, payload["output_blend_rel"], allow_missing=True)
    asset_kind = str(payload.get("asset_kind") or "")
    if asset_kind not in {"building", "static_building"}:
        raise RuntimeError("Static transform baking accepts only building or static_building profiles.")
    tolerance = float(payload.get("bounds_tolerance", 1e-5))
    if not math.isfinite(tolerance) or tolerance <= 0.0 or tolerance > 1e-3:
        raise RuntimeError("bounds_tolerance must be finite and within (0, 0.001].")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    if not working:
        raise RuntimeError("Static transform baking found no approved hoi4_working mesh objects.")
    if armatures(working_only=False) or bpy.data.actions:
        raise RuntimeError("Static transform baking rejects scenes containing armatures or actions.")
    if any(obj.parent is not None for obj in working):
        raise RuntimeError("Static transform baking rejects parented working mesh objects.")
    if any(obj.modifiers for obj in working):
        raise RuntimeError("Static transform baking requires applied working mesh modifiers.")

    protected = [obj for obj in mesh_objects(working_only=False) if not obj.get("hoi4_working", False)]
    protected_data = {obj.data for obj in protected}
    if any(obj.data in protected_data for obj in working):
        raise RuntimeError("Working mesh data is shared with a protected source or reference object.")
    protected_before = {
        obj.name: {"transform": object_transform_record(obj), "bounds": bounds_record([obj])}
        for obj in protected
    }
    scene_before = bounds_record(working)
    object_records = []
    for obj in working:
        before_transform = object_transform_record(obj)
        matrix = obj.matrix_world.copy()
        flat_matrix = [float(value) for row in matrix for value in row]
        if not all(math.isfinite(value) for value in flat_matrix):
            raise RuntimeError(f"{obj.name} has a non-finite world transform.")
        if any(not math.isfinite(float(value)) or float(value) <= 0.0 for value in obj.scale):
            raise RuntimeError(f"{obj.name} has a non-positive or negative scale: {list(obj.scale)}")
        if matrix.to_3x3().determinant() <= 0.0:
            raise RuntimeError(f"{obj.name} has a negative or singular world transform.")

        object_before = bounds_record([obj])
        uv_layers_before = [layer.name for layer in obj.data.uv_layers]
        material_slots_before = [slot.material.name if slot.material else None for slot in obj.material_slots]
        mesh_name = obj.data.name
        object_name = obj.name
        obj.data.transform(matrix)
        obj.matrix_world = Matrix.Identity(4)
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        obj.data.update()
        bpy.context.view_layer.update()

        object_after = bounds_record([obj])
        deltas = {
            key: [object_after[key][index] - object_before[key][index] for index in range(3)]
            for key in ("minimum", "maximum", "dimensions")
        }
        max_drift = max(abs(value) for values in deltas.values() for value in values)
        if max_drift > tolerance:
            raise RuntimeError(f"{obj.name} bounds drift {max_drift} exceeded tolerance {tolerance}.")
        if obj.name != object_name or obj.data.name != mesh_name:
            raise RuntimeError(f"{object_name} name changed during static transform baking.")
        if [layer.name for layer in obj.data.uv_layers] != uv_layers_before:
            raise RuntimeError(f"{obj.name} UV layers changed during static transform baking.")
        if [slot.material.name if slot.material else None for slot in obj.material_slots] != material_slots_before:
            raise RuntimeError(f"{obj.name} material slots changed during static transform baking.")
        object_records.append(
            {
                "object": obj.name,
                "before_transform": before_transform,
                "after_transform": object_transform_record(obj),
                "before_bounds": object_before,
                "after_bounds": object_after,
                "bounds_delta": deltas,
                "maximum_bounds_drift": max_drift,
                "ground_contact_delta": object_after["minimum"][2] - object_before["minimum"][2],
                "uv_layers": uv_layers_before,
                "material_slots": material_slots_before,
            }
        )

    identity_validation = require_identity_static_mesh_transforms()
    scene_after = bounds_record(working)
    scene_delta = {
        key: [scene_after[key][index] - scene_before[key][index] for index in range(3)]
        for key in ("minimum", "maximum", "dimensions")
    }
    maximum_scene_drift = max(abs(value) for values in scene_delta.values() for value in values)
    if maximum_scene_drift > tolerance:
        raise RuntimeError(f"Static working-scene bounds drift {maximum_scene_drift} exceeded tolerance {tolerance}.")
    protected_after = {
        obj.name: {"transform": object_transform_record(obj), "bounds": bounds_record([obj])}
        for obj in protected
    }
    if protected_after != protected_before:
        raise RuntimeError("A protected provider/source or vanilla reference object changed during baking.")

    save_blend(output)
    report = {
        "asset_kind": asset_kind,
        "source_blend": str(blend.relative_to(job)).replace("\\", "/"),
        "output_blend": str(output.relative_to(job)).replace("\\", "/"),
        "bounds_tolerance": tolerance,
        "scene_before_bounds": scene_before,
        "scene_after_bounds": scene_after,
        "scene_bounds_delta": scene_delta,
        "maximum_scene_bounds_drift": maximum_scene_drift,
        "protected_objects_verified_unchanged": sorted(protected_before),
        "objects": object_records,
        "identity_validation": identity_validation,
    }
    report_path = job / "blender" / "reports" / "static_transform_bake.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def partition_static_mesh_export_batches(req: Dict[str, Any]) -> Dict[str, Any]:
    """Partition static geometry into material batches without changing its shape."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    output = within(job, payload["output_blend_rel"], allow_missing=True)
    asset_kind = str(payload.get("asset_kind") or "")
    if asset_kind not in {"building", "static_building"}:
        raise RuntimeError("Static export batching accepts only building or static_building profiles.")
    maximum_vertices = int(payload.get("max_export_vertices_per_batch", 60000))
    if maximum_vertices < 3 or maximum_vertices > 65535:
        raise RuntimeError("max_export_vertices_per_batch must be within [3, 65535].")
    maximum_triangles = maximum_vertices // 3
    if maximum_triangles < 1:
        raise RuntimeError("The export batch vertex ceiling cannot contain one triangle.")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    if not working:
        raise RuntimeError("Static export batching found no approved hoi4_working mesh objects.")
    if armatures(working_only=False) or bpy.data.actions:
        raise RuntimeError("Static export batching rejects scenes containing armatures or actions.")
    if any(obj.parent is not None for obj in working):
        raise RuntimeError("Static export batching rejects parented working mesh objects.")
    if any(obj.modifiers for obj in working):
        raise RuntimeError("Static export batching requires applied working mesh modifiers.")
    identity_before = require_identity_static_mesh_transforms()
    scene_before = bounds_record(working)
    geometry_before = geometry_metrics()
    object_records = []

    for obj in working:
        mesh = obj.data
        if any(len(poly.vertices) != 3 for poly in mesh.polygons):
            raise RuntimeError(f"{obj.name} must be triangulated before static export batching.")
        original_slot_count = len(mesh.materials)
        if original_slot_count == 0:
            raise RuntimeError(f"{obj.name} has no material slots to partition.")
        bounds_before = bounds_record([obj])
        transforms_before = object_transform_record(obj)
        uv_layers_before = [layer.name for layer in mesh.uv_layers]
        object_name = obj.name
        mesh_name = mesh.name
        batches = []

        for material_index in range(original_slot_count):
            polygons = [poly for poly in mesh.polygons if poly.material_index == material_index]
            if not polygons:
                continue
            material = mesh.materials[material_index]
            if material is None:
                raise RuntimeError(f"{obj.name} material slot {material_index} is empty.")
            polygons.sort(
                key=lambda poly: (
                    float(poly.center.x),
                    float(poly.center.y),
                    float(poly.center.z),
                    int(poly.index),
                )
            )
            batch_count = max(1, math.ceil(len(polygons) / maximum_triangles))
            slot_indices = [material_index]
            for batch_number in range(1, batch_count):
                batch_material = material.copy()
                batch_material.name = f"{material.name}_export_batch_{batch_number + 1:02d}"
                mesh.materials.append(batch_material)
                slot_indices.append(len(mesh.materials) - 1)
            for batch_number, start in enumerate(range(0, len(polygons), maximum_triangles)):
                batch_polygons = polygons[start:start + maximum_triangles]
                slot_index = slot_indices[batch_number]
                for poly in batch_polygons:
                    poly.material_index = slot_index
                triangle_count = len(batch_polygons)
                batches.append(
                    {
                        "source_material_index": material_index,
                        "source_material": material.name,
                        "batch_number": batch_number + 1,
                        "material_slot_index": slot_index,
                        "material": mesh.materials[slot_index].name,
                        "triangles": triangle_count,
                        "worst_case_export_vertices": triangle_count * 3,
                    }
                )

        mesh.update()
        bpy.context.view_layer.update()
        bounds_after = bounds_record([obj])
        maximum_drift = max(
            abs(bounds_after[key][axis] - bounds_before[key][axis])
            for key in ("minimum", "maximum", "dimensions")
            for axis in range(3)
        )
        if maximum_drift > 1e-7:
            raise RuntimeError(f"{obj.name} bounds changed during static export batching.")
        if obj.name != object_name or mesh.name != mesh_name:
            raise RuntimeError(f"{object_name} name changed during static export batching.")
        if object_transform_record(obj) != transforms_before:
            raise RuntimeError(f"{obj.name} transform changed during static export batching.")
        if [layer.name for layer in mesh.uv_layers] != uv_layers_before:
            raise RuntimeError(f"{obj.name} UV layers changed during static export batching.")
        if any(batch["worst_case_export_vertices"] > maximum_vertices for batch in batches):
            raise RuntimeError(f"{obj.name} produced an oversized static export batch.")
        object_records.append(
            {
                "object": obj.name,
                "source_material_slots": original_slot_count,
                "final_material_slots": len(mesh.materials),
                "maximum_bounds_drift": maximum_drift,
                "batches": batches,
            }
        )

    geometry_after = geometry_metrics()
    for key in ("objects", "vertices", "polygons", "triangles", "bounds_min", "bounds_max", "dimensions"):
        if geometry_after[key] != geometry_before[key]:
            raise RuntimeError(f"Static export batching changed geometry metric {key}.")
    identity_after = require_identity_static_mesh_transforms()
    scene_after = bounds_record(working)
    if scene_after != scene_before:
        raise RuntimeError("Static export batching changed working-scene bounds.")

    save_blend(output)
    report = {
        "asset_kind": asset_kind,
        "source_blend": str(blend.relative_to(job)).replace("\\", "/"),
        "output_blend": str(output.relative_to(job)).replace("\\", "/"),
        "max_export_vertices_per_batch": maximum_vertices,
        "max_triangles_per_batch": maximum_triangles,
        "geometry_before": geometry_before,
        "geometry_after": geometry_after,
        "scene_bounds_before": scene_before,
        "scene_bounds_after": scene_after,
        "identity_before": identity_before,
        "identity_after": identity_after,
        "objects": object_records,
    }
    report_path = job / "blender" / "reports" / "static_export_batch_partition.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def exported_mesh_streams(text_path: Path) -> List[Dict[str, int]]:
    """Read per-material PDX mesh stream sizes from the exporter text proof."""

    streams: List[Dict[str, int]] = []
    current: Optional[Dict[str, int]] = None
    for line in text_path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*mesh:\s*$", line):
            if current is not None:
                streams.append(current)
            current = {"stream_index": len(streams)}
            continue
        if current is None:
            continue
        position_match = re.search(r"\bp \(float,\s*(\d+)\)", line)
        if position_match:
            components = int(position_match.group(1))
            if components % 3:
                raise RuntimeError("PDX export position stream is not divisible by three.")
            current["vertices"] = components // 3
        triangle_match = re.search(r"\btri \(int,\s*(\d+)\)", line)
        if triangle_match:
            indices = int(triangle_match.group(1))
            if indices % 3:
                raise RuntimeError("PDX export triangle stream is not divisible by three.")
            current["triangles"] = indices // 3
    if current is not None:
        streams.append(current)
    streams = [stream for stream in streams if "vertices" in stream or "triangles" in stream]
    if not streams or any("vertices" not in stream or "triangles" not in stream for stream in streams):
        raise RuntimeError("Unable to prove complete per-stream vertex and triangle counts from PDX text export.")
    return streams


def export_mesh(req: Dict[str, Any], pdx: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    output = within(job, payload["output_rel"], allow_missing=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    pdx = load_pdx(req["io_pdx_root"])
    export_transforms = prepare_pdx_export_transforms()
    bpy.ops.object.select_all(action="DESELECT")
    working = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.get("hoi4_working", False)
    ]
    if not working:
        raise RuntimeError("Mesh export found no approved hoi4_working mesh objects.")
    for obj in working:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = working[0]
    for old_output in (output, output.with_suffix(".txt")):
        if old_output.exists():
            if not old_output.is_file():
                raise RuntimeError(f"Mesh export target is not a file: {old_output}")
            old_output.unlink()
    pdx["export_meshfile"](
        str(output),
        exp_mesh=True,
        exp_skel=True,
        exp_locs=True,
        exp_selected=True,
        as_blendshape=False,
        debug_mode=True,
        # The HOI4 renderer's supported vertex/index envelope is materially
        # lower than the per-loop vertex stream produced by split_verts=True.
        # The pinned 0.91 exporter has an O(n^2) de-duplication pass when this
        # is false, but the shared-vertex route is required for runtime-safe
        # humanoid exports. A diagnostic may opt into split vertices explicitly.
        split_verts=bool(payload.get("split_verts", False)),
        sort_verts="+",
        plain_txt=True,
    )
    text_output = output.with_suffix(".txt")
    streams = exported_mesh_streams(text_output)
    oversized_streams = [stream for stream in streams if stream["vertices"] > 65535]
    if oversized_streams:
        raise RuntimeError(f"PDX export exceeded the 65,535-vertex per-stream limit: {oversized_streams}")
    exported_checkpoint = job / "blender" / "checkpoints" / "06_exported.blend"
    save_blend(exported_checkpoint)
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "mesh": str(output.relative_to(job)).replace("\\", "/"),
        "mesh_bytes": output.stat().st_size,
        "mesh_text": str(output.with_suffix(".txt").relative_to(job)).replace("\\", "/")
        if output.with_suffix(".txt").exists()
        else None,
        "mesh_streams": streams,
        "maximum_stream_vertices": max(stream["vertices"] for stream in streams),
        "vertex_stream_limit": 65535,
        "exported_checkpoint": str(exported_checkpoint.relative_to(job)).replace("\\", "/"),
        "geometry": geometry_metrics(),
        "export_transforms": export_transforms,
        "warnings": [],
    }
    report = job / "blender" / "reports" / "export_mesh.json"
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def select_armature_and_action(action_name: str) -> Tuple[bpy.types.Object, bpy.types.Action, int, int]:
    rigs = armatures()
    if not rigs:
        raise RuntimeError("Animation export requires a working armature.")
    rig = rigs[0]
    action = bpy.data.actions.get(action_name)
    if action is None:
        action = next(
            (
                candidate for candidate in bpy.data.actions
                if candidate.name.casefold() == action_name.casefold()
            ),
            None,
        )
    if action is None:
        raise RuntimeError(f"Requested Blender action was not found: {action_name}")
    rig.animation_data_create()
    rig.animation_data.action = action
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    start, end = action.frame_range
    return rig, action, int(math.floor(start)), int(math.ceil(end))


def import_animation_action(req: Dict[str, Any]) -> Dict[str, Any]:
    """Transfer one provider skeletal action onto the approved working rig.

    Provider animation files are imported only long enough to read their real
    bone channels. The source armature and mesh are removed after the action
    is copied onto the calibrated candidate, so the runtime scene retains one
    model and one armature. This is deliberately a named adapter operation,
    rather than an arbitrary Blender script, because the action transfer is a
    repeatable part of the locked HOI4 asset pipeline.
    """

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    source = within(job, payload["source_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    action_name = str(payload.get("action_name") or "hoi4_runtime_action")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", action_name):
        raise ValueError("Imported runtime action names must use stable alphanumeric, dot, dash, or underscore identifiers.")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    target_rigs = armatures()
    if len(target_rigs) != 1:
        raise RuntimeError(
            "Animation transfer requires exactly one calibrated working armature; "
            f"found {len(target_rigs)}."
        )
    target_rig = target_rigs[0]
    before_objects = set(bpy.data.objects)
    before_actions = set(bpy.data.actions)
    imported = import_candidate(source)
    imported_rigs = [obj for obj in imported if obj.type == "ARMATURE"]
    if len(imported_rigs) != 1:
        raise RuntimeError(
            "Provider animation import must expose exactly one source armature; "
            f"found {len(imported_rigs)} from {source.name}."
        )
    source_rig = imported_rigs[0]
    source_armature_name = source_rig.name
    source_action = source_rig.animation_data.action if source_rig.animation_data else None
    if source_action is None:
        source_actions = [action for action in bpy.data.actions if action not in before_actions]
        if len(source_actions) == 1:
            source_action = source_actions[0]
    if source_action is None:
        raise RuntimeError(f"Provider animation import exposed no action: {source}")
    source_action_name = source_action.name

    source_curves = list(action_fcurves(source_action))
    if not source_curves:
        raise RuntimeError(f"Provider animation action contains no F-curves: {source_action.name}")
    bone_names = sorted(
        {
            match.group(1)
            for fcurve, _ in source_curves
            for match in [re.search(r'pose\.bones\["([^"]+)"\]', fcurve.data_path)]
            if match is not None
        }
    )
    target_bone_names = {bone.name for bone in target_rig.data.bones}
    missing_bones = sorted(set(bone_names) - target_bone_names)
    if len(bone_names) < 6:
        raise RuntimeError(
            f"Provider animation action is not a usable skeletal action: only {len(bone_names)} driven bones."
        )
    if missing_bones:
        raise RuntimeError(
            "Provider animation bone channels do not match the calibrated rig: "
            + json.dumps({"missing_bones": missing_bones, "source_action": source_action.name}, sort_keys=True)
        )

    source_rig.animation_data_create()
    source_rig.animation_data.action = source_action
    source_start, source_end = source_action.frame_range
    frame_start = int(math.floor(float(source_start)))
    frame_end = int(math.ceil(float(source_end)))
    if frame_end <= frame_start:
        raise RuntimeError(f"Provider animation action has no usable frame span: {source_action.name}")
    source_lengths = {
        name: max(float(source_rig.data.bones[name].length), 1e-8)
        for name in bone_names
    }
    length_ratios = sorted(
        float(target_rig.data.bones[name].length) / source_lengths[name]
        for name in bone_names
    )
    location_scale = length_ratios[len(length_ratios) // 2]
    source_pose_cache: Dict[int, Dict[str, Tuple[Vector, Quaternion]]] = {}
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        frame_pose: Dict[str, Tuple[Vector, Quaternion]] = {}
        for bone_name in bone_names:
            location, rotation, _ = source_rig.pose.bones[bone_name].matrix_basis.decompose()
            frame_pose[bone_name] = (location.copy(), rotation.copy())
        source_pose_cache[frame] = frame_pose

    existing = bpy.data.actions.get(action_name)
    if existing is not None:
        for obj in bpy.context.scene.objects:
            if obj.animation_data and obj.animation_data.action == existing:
                obj.animation_data.action = None
        bpy.data.actions.remove(existing)
    transferred = bpy.data.actions.new(action_name)
    transferred.use_fake_user = True
    target_rig.animation_data_create()
    target_rig.animation_data.action = transferred
    bpy.context.view_layer.objects.active = target_rig
    target_rig.select_set(True)
    source_hips_location = source_pose_cache[frame_start].get("Hips", (Vector(), Quaternion()))[0]
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        for bone_name in bone_names:
            target_bone = target_rig.pose.bones[bone_name]
            source_location, source_rotation = source_pose_cache[frame][bone_name]
            target_bone.rotation_mode = "QUATERNION"
            if bone_name == "Hips":
                root_delta = source_location - source_hips_location
                target_bone.location = Vector((0.0, 0.0, root_delta.z * location_scale))
            else:
                target_bone.location = source_location * location_scale
            target_bone.rotation_quaternion = source_rotation
            target_bone.scale = (1.0, 1.0, 1.0)
            target_bone.keyframe_insert(data_path="location", frame=frame, group=bone_name)
            target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=bone_name)
        bpy.context.view_layer.update()

    scale_cleanup = sanitize_action_scale_channels()
    root_cleanup = {
        "action": transferred.name,
        "policy": "provider pose baked to target rig; Hips X/Y root motion removed; provider Hips Z motion retained",
        "location_scale": location_scale,
        "source_root_location": list(source_hips_location),
    }
    bpy.context.scene.frame_start = frame_start
    bpy.context.scene.frame_end = frame_end
    sample_frames = sorted(
        {
            frame_start,
            int(round(frame_start + (frame_end - frame_start) * 0.25)),
            int(round(frame_start + (frame_end - frame_start) * 0.50)),
            int(round(frame_start + (frame_end - frame_start) * 0.75)),
            frame_end,
        }
    )
    sampled_bones = [
        name for name in ("Hips", "Spine02", "LeftHand", "RightHand", "LeftFoot", "RightFoot")
        if name in bone_names
    ]
    source_reference = source_pose_cache[frame_start]
    motion_crosscheck = []
    source_motion_peak = 0.0
    target_motion_peak = 0.0
    for frame in sample_frames:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        source_motion = 0.0
        target_motion = 0.0
        bones_report = []
        for bone_name in sampled_bones:
            source_location, source_rotation = source_pose_cache[frame][bone_name]
            source_base_location, source_base_rotation = source_reference[bone_name]
            target_location, target_rotation, _ = target_rig.pose.bones[bone_name].matrix_basis.decompose()
            target_rig.animation_data.action = transferred
            bpy.context.view_layer.update()
            target_base_location = (
                Vector((0.0, 0.0, 0.0))
                if bone_name == "Hips"
                else source_base_location * location_scale
            )
            target_base_rotation = source_base_rotation
            source_delta = float((source_location - source_base_location).length) + float(
                source_rotation.rotation_difference(source_base_rotation).angle
            )
            target_delta = float((target_location - target_base_location).length) + float(
                target_rotation.rotation_difference(target_base_rotation).angle
            )
            source_motion += source_delta
            target_motion += target_delta
            bones_report.append(
                {
                    "bone": bone_name,
                    "source_delta_from_start": source_delta,
                    "target_delta_from_start": target_delta,
                }
            )
        source_motion_peak = max(source_motion_peak, source_motion)
        target_motion_peak = max(target_motion_peak, target_motion)
        motion_crosscheck.append(
            {
                "frame": frame,
                "source_motion_total": source_motion,
                "target_motion_total": target_motion,
                "bones": bones_report,
            }
        )
    if source_motion_peak > 1e-4 and target_motion_peak < max(1e-4, source_motion_peak * 0.10):
        raise RuntimeError(
            "Provider action has source motion but the transferred target action remained static: "
            + json.dumps(
                {
                    "source_motion_peak": source_motion_peak,
                    "target_motion_peak": target_motion_peak,
                    "samples": motion_crosscheck,
                },
                sort_keys=True,
            )
        )
    bpy.context.scene.frame_set(frame_start)
    bpy.context.view_layer.update()

    imported_object_names = [obj.name for obj in imported]
    for obj in list(imported):
        if obj.name in {item.name for item in bpy.context.scene.objects if item is target_rig}:
            continue
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    removed_provider_actions: List[str] = []
    for action in list(bpy.data.actions):
        if action == transferred or action == existing:
            continue
        if action == source_action or action.name.startswith("Armature.002|"):
            removed_provider_actions.append(action.name)
            action.user_clear()
            bpy.data.actions.remove(action)

    save_blend(checkpoint)
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "source": str(source.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "target_armature": target_rig.name,
        "source_armature": source_armature_name,
        "source_action": source_action_name,
        "action": transferred.name,
        "frame_start": frame_start,
        "frame_end": frame_end,
        "fps": bpy.context.scene.render.fps,
        "source_fcurves": len(source_curves),
        "driven_bones": bone_names,
        "imported_objects_removed": imported_object_names,
        "provider_actions_removed": removed_provider_actions,
        "scale_cleanup": scale_cleanup,
        "root_cleanup": root_cleanup,
        "location_scale": location_scale,
        "source_target_motion_crosscheck": {
            "sample_frames": sample_frames,
            "source_motion_peak": source_motion_peak,
            "target_motion_peak": target_motion_peak,
            "samples": motion_crosscheck,
            "status": "pass",
        },
        "policy": "provider_skeletal_action_transferred_to_single_calibrated_working_rig",
        "new_provider_call": False,
        "warnings": [],
    }
    report = job / "blender" / "reports" / f"import_animation_{safe_name(action_name)}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def explicit_safe_name(value: Any, field: str) -> str:
    """Require a caller-supplied Blender identifier without sanitizing it."""

    name = str(value or "")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,127}", name):
        raise ValueError(
            f"{field} must be an explicit safe Blender identifier containing only "
            "letters, digits, underscores, periods, or hyphens."
        )
    return name


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def retime_animation_action(req: Dict[str, Any]) -> Dict[str, Any]:
    """Retiming an existing action changes sample time, not skeletal motion."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    action_name = str(payload.get("action_name") or "")
    source_fps = float(payload.get("source_fps") or 0.0)
    target_fps = float(payload.get("target_fps") or 0.0)
    if source_fps <= 0.0 or target_fps <= 0.0:
        raise ValueError("Animation retiming requires positive source and target FPS values.")
    if not action_name:
        raise ValueError("Animation retiming requires an action name.")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError(f"Animation retiming requires exactly one working armature, found {len(rigs)}.")
    rig = rigs[0]
    action = bpy.data.actions.get(action_name)
    if action is None:
        action = next(
            (
                candidate
                for candidate in bpy.data.actions
                if candidate.name.casefold() == action_name.casefold()
            ),
            None,
        )
    if action is None:
        raise RuntimeError(f"Requested action was not found: {action_name}")

    old_start = float(action.frame_range[0])
    old_end = float(action.frame_range[1])
    frame_ratio = target_fps / source_fps
    moved_keyframes = 0
    moved_handles = 0
    for fcurve, _ in action_fcurves(action):
        for keyframe in fcurve.keyframe_points:
            keyframe.co.x *= frame_ratio
            keyframe.handle_left.x *= frame_ratio
            keyframe.handle_right.x *= frame_ratio
            moved_keyframes += 1
            moved_handles += 2
        fcurve.update()

    scene = bpy.context.scene
    scene.render.fps = int(round(target_fps))
    start = int(math.floor(float(action.frame_range[0])))
    end = int(math.ceil(float(action.frame_range[1])))
    if end <= start:
        raise RuntimeError(f"Retimed action has no usable frame span: {action.name}")
    scene.frame_start = start
    scene.frame_end = end
    rig.animation_data_create()
    rig.animation_data.action = action
    scene.frame_set(start)
    bpy.context.view_layer.update()
    save_blend(checkpoint)
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "action": action.name,
        "source_fps": source_fps,
        "target_fps": target_fps,
        "frame_ratio": frame_ratio,
        "frame_start_before": old_start,
        "frame_end_before": old_end,
        "frame_start": start,
        "frame_end": end,
        "moved_keyframes": moved_keyframes,
        "moved_handles": moved_handles,
        "fps": scene.render.fps,
        "policy": "existing_provider_action_time_rescaled_to_required_runtime_fps",
        "body_motion_replaced": False,
        "new_model_created": False,
        "new_rig_created": False,
        "new_provider_call": False,
        "warnings": [],
    }
    report = job / "blender" / "reports" / f"retime_animation_{safe_name(action.name)}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def normalize_exported_animation_scales(
    output: Path,
    pdx: Dict[str, Any],
    translation_scale: float,
) -> Dict[str, Any]:
    """Keep animation samples from changing the authored unit scale at runtime."""

    from io_pdx_mesh import pdx_data  # type: ignore

    root_xml = pdx_data.read_meshfile(str(output))
    info_xml = root_xml.find("info")
    samples_xml = root_xml.find("samples")
    initial_values_changed = 0
    sample_values_changed = 0
    initial_translation_values_changed = 0
    sample_translation_values_changed = 0

    if info_xml is not None:
        for bone_xml in info_xml:
            values = bone_xml.get("s")
            if values is None:
                continue
            initial_values_changed += sum(1 for value in values if abs(float(value) - 1.0) > 1e-6)
            bone_xml.set("s", [1.0 for _ in values])
        if abs(translation_scale - 1.0) > 1e-6:
            for bone_xml in info_xml:
                values = bone_xml.get("t")
                if values is None:
                    continue
                initial_translation_values_changed += len(values)
                bone_xml.set("t", [float(value) * translation_scale for value in values])

    if samples_xml is not None:
        values = samples_xml.get("s")
        if values:
            sample_values_changed = sum(1 for value in values if abs(float(value) - 1.0) > 1e-6)
            samples_xml.set("s", [1.0 for _ in values])
        values = samples_xml.get("t")
        if values and abs(translation_scale - 1.0) > 1e-6:
            sample_translation_values_changed = len(values)
            samples_xml.set("t", [float(value) * translation_scale for value in values])

    if (
        initial_values_changed
        or sample_values_changed
        or initial_translation_values_changed
        or sample_translation_values_changed
    ):
        pdx_data.write_animfile(str(output), root_xml)
        text_path = output.with_suffix(".txt")
        text_path.write_text(f"{pdx_data.PDXData(root_xml)}\n", encoding="utf-8")

    return {
        "policy": "normalize_exported_bone_scales_and_preserve_mesh_unit_translations",
        "translation_scale": translation_scale,
        "initial_scale_values_changed": initial_values_changed,
        "sample_scale_values_changed": sample_values_changed,
        "initial_translation_values_changed": initial_translation_values_changed,
        "sample_translation_values_changed": sample_translation_values_changed,
        "remaining_non_unit_initial_scales": 0,
        "remaining_non_unit_sample_scales": 0,
    }


def export_animation(req: Dict[str, Any], pdx: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    output = within(job, payload["output_rel"], allow_missing=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    pdx = load_pdx(req["io_pdx_root"])
    rig, action, start, end = select_armature_and_action(payload["action_name"])
    export_transforms = prepare_pdx_export_transforms()
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = end
    for old_output in (output, output.with_suffix(".txt")):
        if old_output.exists():
            if not old_output.is_file():
                raise RuntimeError(f"Animation export target is not a file: {old_output}")
            old_output.unlink()
    pdx["export_animfile"](
        str(output),
        frame_start=start,
        frame_end=end,
        uniform_scale=True,
        plain_txt=True,
    )
    scale_normalization = normalize_exported_animation_scales(output, pdx, 1.0)
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "action": action.name,
        "armature": rig.name,
        "frame_start": start,
        "frame_end": end,
        "fps": bpy.context.scene.render.fps,
        "armature_world_scale": export_transforms["armature_world_scale_after"],
        "export_transforms": export_transforms,
        "anim": str(output.relative_to(job)).replace("\\", "/"),
        "anim_bytes": output.stat().st_size,
        "anim_text": str(output.with_suffix(".txt").relative_to(job)).replace("\\", "/")
        if output.with_suffix(".txt").exists()
        else None,
        "scale_normalization": scale_normalization,
        "warnings": [],
    }
    report = job / "blender" / "reports" / f"export_anim_{safe_name(action.name)}.json"
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


HUMANOID_BONE_NAMES = (
    "Hips",
    "Spine",
    "Spine01",
    "Spine02",
    "neck",
    "Head",
    "headfront",
    "head_end",
    "LeftShoulder",
    "LeftArm",
    "LeftForeArm",
    "LeftHand",
    "RightShoulder",
    "RightArm",
    "RightForeArm",
    "RightHand",
    "LeftUpLeg",
    "LeftLeg",
    "LeftFoot",
    "LeftToeBase",
    "RightUpLeg",
    "RightLeg",
    "RightFoot",
    "RightToeBase",
)


def _humanoid_bone_name_for_vertex(
    world_position: Vector,
    minimum: Vector,
    maximum: Vector,
) -> str:
    """Choose a deterministic HOI4 humanoid influence from the mesh silhouette."""

    dimensions = maximum - minimum
    centre = (minimum + maximum) * 0.5
    height = max(float(dimensions.z), 1e-6)
    width = max(float(dimensions.x), 1e-6)
    length = max(float(dimensions.y), 1e-6)
    z_fraction = (world_position.z - minimum.z) / height
    x_fraction = (world_position.x - centre.x) / width
    y_fraction = (world_position.y - centre.y) / length
    abs_x = abs(x_fraction)
    side = "Left" if x_fraction < 0.0 else "Right"

    if z_fraction > 0.91:
        return "head_end"
    if z_fraction > 0.84 and y_fraction < -0.08:
        return "headfront"
    if z_fraction > 0.79:
        return "Head"
    if z_fraction > 0.69 and abs_x < 0.18:
        return "neck"
    if z_fraction > 0.58 and abs_x > 0.12:
        return f"{side}Shoulder"
    if z_fraction > 0.43 and abs_x > 0.13:
        return f"{side}Arm"
    if z_fraction > 0.27 and abs_x > 0.10:
        return f"{side}ForeArm"
    if z_fraction > 0.16 and abs_x > 0.08:
        return f"{side}Hand"
    if z_fraction < 0.13 and abs_x > 0.07:
        return f"{side}ToeBase" if y_fraction < -0.04 else f"{side}Foot"
    if z_fraction < 0.46 and abs_x > 0.08:
        return f"{side}Leg" if z_fraction < 0.28 else f"{side}UpLeg"
    if z_fraction > 0.63:
        return "Spine02"
    if z_fraction > 0.49:
        return "Spine01"
    if z_fraction > 0.33:
        return "Spine"
    return "Hips"


def _humanoid_weight_candidates(primary: str) -> List[str]:
    """Return a small same-region chain for bounded blended weights."""

    if primary in {"Head", "headfront", "head_end", "neck"}:
        return ["neck", "Head", "headfront", "head_end"]
    if primary.startswith("Left"):
        if primary in {"LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand"}:
            return ["LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand"]
        if primary in {"LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase"}:
            return ["LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase"]
    if primary.startswith("Right"):
        if primary in {"RightShoulder", "RightArm", "RightForeArm", "RightHand"}:
            return ["RightShoulder", "RightArm", "RightForeArm", "RightHand"]
        if primary in {"RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"}:
            return ["RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"]
    if primary == "Spine02":
        return ["Spine01", "Spine02", "neck"]
    if primary == "Spine01":
        return ["Spine", "Spine01", "Spine02"]
    if primary == "Spine":
        return ["Hips", "Spine", "Spine01"]
    return ["Hips", "Spine", "Spine01"]


def _point_segment_distance(point: Vector, start: Vector, end: Vector) -> float:
    segment = end - start
    length_squared = float(segment.length_squared)
    if length_squared <= 1e-12:
        return float((point - start).length)
    factor = max(0.0, min(1.0, float((point - start).dot(segment)) / length_squared))
    return float((point - (start + factor * segment)).length)


def author_humanoid_rig(req: Dict[str, Any]) -> Dict[str, Any]:
    """Create the repository's bounded HOI4 humanoid rig on approved geometry."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    rig_name = safe_name(str(payload.get("rig_name") or "hoi4_humanoid_armature"))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    if not working:
        raise RuntimeError("Humanoid rigging found no approved working meshes.")
    weapon_objects = [obj for obj in working if bool(obj.get("hoi4_humanoid_weapon", False))]
    body_objects = [obj for obj in working if obj not in weapon_objects]
    if not body_objects:
        raise RuntimeError("Humanoid rigging found no body meshes after excluding reviewed weapons.")
    if len(weapon_objects) > 1:
        raise RuntimeError("Humanoid rigging accepts at most one explicitly isolated weapon object.")
    armed_route = bool(weapon_objects)
    for rig in armatures():
        bpy.data.objects.remove(rig, do_unlink=True)

    minimum, maximum = world_bounds(body_objects)
    dimensions = maximum - minimum
    centre = (minimum + maximum) * 0.5
    height = max(float(dimensions.z), 1e-6)
    width = max(float(dimensions.x), 1e-6)
    length = max(float(dimensions.y), 1e-6)
    z0 = minimum.z
    y_front = centre.y - length * 0.08
    y_rear = centre.y + length * 0.04
    armature_data = bpy.data.armatures.new(rig_name)
    rig = bpy.data.objects.new(rig_name, armature_data)
    _working_collection().objects.link(rig)
    rig["hoi4_working"] = True
    rig["hoi4_humanoid_rig"] = True
    rig["hoi4_humanoid_rig_route"] = (
        "blender_failure_recovery_armed_humanoid_v2"
        if armed_route
        else "blender_failure_recovery_humanoid_v1"
    )
    rig["hoi4_skeleton_contract"] = (
        "hoi4_standard_humanoid_24_bone_plus_weapon"
        if armed_route
        else "hoi4_standard_humanoid_24_bone"
    )
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bones: Dict[str, bpy.types.EditBone] = {}

    def add_bone(name: str, head: Vector, tail: Vector, parent: Optional[str] = None) -> None:
        bone = armature_data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        if parent:
            bone.parent = bones[parent]
            bone.use_connect = False
        bones[name] = bone

    add_bone("Hips", Vector((centre.x, centre.y, z0 + height * 0.34)), Vector((centre.x, centre.y, z0 + height * 0.43)))
    add_bone("Spine", Vector((centre.x, centre.y, z0 + height * 0.41)), Vector((centre.x, centre.y, z0 + height * 0.51)), "Hips")
    add_bone("Spine01", Vector((centre.x, centre.y, z0 + height * 0.49)), Vector((centre.x, centre.y, z0 + height * 0.61)), "Spine")
    add_bone("Spine02", Vector((centre.x, centre.y, z0 + height * 0.59)), Vector((centre.x, centre.y, z0 + height * 0.70)), "Spine01")
    add_bone("neck", Vector((centre.x, y_front, z0 + height * 0.68)), Vector((centre.x, y_front, z0 + height * 0.78)), "Spine02")
    add_bone("Head", Vector((centre.x, y_front, z0 + height * 0.76)), Vector((centre.x, y_front, z0 + height * 0.87)), "neck")
    add_bone("headfront", Vector((centre.x, y_front, z0 + height * 0.82)), Vector((centre.x, y_front - length * 0.08, z0 + height * 0.84)), "Head")
    add_bone("head_end", Vector((centre.x, y_front, z0 + height * 0.86)), Vector((centre.x, y_front, z0 + height * 0.96)), "Head")

    for side, sign in (("Left", -1.0), ("Right", 1.0)):
        shoulder = Vector((centre.x + sign * width * 0.16, centre.y - length * 0.01, z0 + height * 0.66))
        if armed_route:
            elbow = Vector((centre.x + sign * width * 0.29, centre.y - length * 0.015, z0 + height * 0.66))
            wrist = Vector((centre.x + sign * width * 0.41, centre.y - length * 0.02, z0 + height * 0.66))
            hand = Vector((centre.x + sign * width * 0.47, centre.y - length * 0.025, z0 + height * 0.66))
        else:
            elbow = Vector((centre.x + sign * width * 0.32, centre.y - length * 0.04, z0 + height * 0.50))
            wrist = Vector((centre.x + sign * width * 0.38, centre.y - length * 0.07, z0 + height * 0.33))
            hand = Vector((centre.x + sign * width * 0.39, centre.y - length * 0.10, z0 + height * 0.22))
        add_bone(f"{side}Shoulder", shoulder, elbow, "Spine02")
        add_bone(f"{side}Arm", elbow, wrist, f"{side}Shoulder")
        add_bone(f"{side}ForeArm", wrist, hand, f"{side}Arm")
        hand_tail = (
            hand + Vector((sign * width * 0.04, -length * 0.015, 0.0))
            if armed_route
            else hand + Vector((0.0, -length * 0.06, -height * 0.04))
        )
        add_bone(f"{side}Hand", hand, hand_tail, f"{side}ForeArm")

        hip = Vector((centre.x + sign * width * 0.10, centre.y + length * 0.01, z0 + height * 0.35))
        knee = Vector((centre.x + sign * width * 0.12, centre.y + length * 0.01, z0 + height * 0.20))
        ankle = Vector((centre.x + sign * width * 0.12, centre.y - length * 0.02, z0 + height * 0.08))
        toe = Vector((centre.x + sign * width * 0.12, centre.y - length * 0.13, z0 + height * 0.035))
        add_bone(f"{side}UpLeg", hip, knee, "Hips")
        add_bone(f"{side}Leg", knee, ankle, f"{side}UpLeg")
        add_bone(f"{side}Foot", ankle, toe, f"{side}Leg")
        add_bone(f"{side}ToeBase", toe, toe + Vector((0.0, -length * 0.07, 0.0)), f"{side}Foot")

    if armed_route:
        weapon = weapon_objects[0]
        weapon_minimum, weapon_maximum = world_bounds([weapon])
        weapon_stock = Vector(
            (
                (weapon_minimum.x + weapon_maximum.x) * 0.5,
                weapon_maximum.y,
                (weapon_minimum.z + weapon_maximum.z) * 0.5,
            )
        )
        weapon_length = max(float(weapon_maximum.y - weapon_minimum.y), length)
        add_bone(
            "weapon",
            weapon_stock,
            weapon_stock + Vector((0.0, -weapon_length * 0.12, 0.0)),
            "Spine02",
        )

    bpy.ops.object.mode_set(mode="OBJECT")
    rig.show_in_front = True
    armature_data.display_type = "BBONE"
    segments = {
        bone.name: (Vector(bone.head_local), Vector(bone.tail_local))
        for bone in armature_data.bones
    }
    records = []
    for obj in body_objects:
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        groups = {name: obj.vertex_groups.new(name=name) for name in HUMANOID_BONE_NAMES}
        counts: Dict[str, int] = {name: 0 for name in groups}
        influence_histogram: Dict[str, int] = {"1": 0, "2": 0, "3": 0}
        for vertex in obj.data.vertices:
            world_position = obj.matrix_world @ vertex.co
            primary = _humanoid_bone_name_for_vertex(world_position, minimum, maximum)
            candidates = [name for name in _humanoid_weight_candidates(primary) if name in segments]
            if armed_route:
                ranked = sorted(
                    (
                        _point_segment_distance(world_position, *segments[name]),
                        name,
                    )
                    for name in HUMANOID_BONE_NAMES
                    if name in segments
                )[:3]
                primary = ranked[0][1] if ranked else "Hips"
                candidates = [name for _, name in ranked]
            else:
                ranked = sorted(
                    (
                        _point_segment_distance(world_position, *segments[name]),
                        name,
                    )
                    for name in candidates
                )[:3]
            names = [name for _, name in ranked]
            if primary not in names:
                names = [primary] + names[:2]
            names = list(dict.fromkeys(name for name in names if name in groups))[:3]
            if not names:
                names = ["Hips"]
            if primary in names:
                names.remove(primary)
            primary_weight = 0.90 if armed_route and primary.endswith("Hand") else 0.68
            remaining_weight = 1.0 - primary_weight
            weights = {primary: primary_weight}
            if names:
                inverse = [1.0 / max(next((distance for distance, name in ranked if name == item), 1.0), 1e-4) for item in names]
                inverse_total = sum(inverse)
                for name, value in zip(names, inverse):
                    weights[name] = remaining_weight * value / max(inverse_total, 1e-8)
            total = sum(weights.values())
            for name, weight in weights.items():
                groups[name].add([vertex.index], weight / max(total, 1e-8), "REPLACE")
                counts[name] += 1
            influence_histogram[str(len(weights))] = influence_histogram.get(str(len(weights)), 0) + 1
        modifier = next((item for item in obj.modifiers if item.type == "ARMATURE"), None)
        if modifier is None:
            modifier = obj.modifiers.new("HOI4_HUMANOID_ARMATURE", "ARMATURE")
        modifier.object = rig
        world_matrix = obj.matrix_world.copy()
        obj.parent = rig
        obj.parent_type = "OBJECT"
        obj.matrix_world = world_matrix
        records.append(
            {
                "object": obj.name,
                "vertices": len(obj.data.vertices),
                "vertex_group_counts": {name: count for name, count in counts.items() if count},
                "influence_histogram": influence_histogram,
            }
        )
    weapon_bindings = []
    if armed_route:
        weapon = weapon_objects[0]
        for group in list(weapon.vertex_groups):
            weapon.vertex_groups.remove(group)
        weapon_group = weapon.vertex_groups.new(name="weapon")
        weapon_group.add([vertex.index for vertex in weapon.data.vertices], 1.0, "REPLACE")
        modifier = next((item for item in weapon.modifiers if item.type == "ARMATURE"), None)
        if modifier is None:
            modifier = weapon.modifiers.new("HOI4_HUMANOID_ARMATURE", "ARMATURE")
        modifier.object = rig
        world_matrix = weapon.matrix_world.copy()
        weapon.parent = rig
        weapon.parent_type = "OBJECT"
        weapon.matrix_world = world_matrix
        weapon_bindings.append(
            {
                "object": weapon.name,
                "vertices": len(weapon.data.vertices),
                "bone": "weapon",
                "weight": 1.0,
                "policy": "rigid recovered weapon binding on a dedicated Spine02 child bone",
            }
        )
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "armature": rig.name,
        "bones": [bone.name for bone in armature_data.bones],
        "bone_count": len(armature_data.bones),
        "component_bindings": records,
        "weapon_bindings": weapon_bindings,
        "rig_route": rig["hoi4_humanoid_rig_route"],
        "rig_map": (
            f"{rig_name}_hoi4_standard_humanoid_24_bones_plus_weapon_v2"
            if armed_route
            else f"{rig_name}_hoi4_standard_humanoid_24_bones_v1"
        ),
        "weight_policy": (
            "nearest three humanoid bone segments for the body; rigid one-bone reviewed weapon binding; no unweighted vertices"
            if armed_route
            else "bounded same-region blended weights with at most three influences per vertex; no unweighted vertices"
        ),
        "source_policy": "Meshy 7 geometry retained; provider rig is not used",
        "status": "pass" if len(armature_data.bones) == len(HUMANOID_BONE_NAMES) + (1 if armed_route else 0) else "failed",
    }
    report_path = job / "blender" / "reports" / "humanoid_rig.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def author_humanoid_actions(req: Dict[str, Any]) -> Dict[str, Any]:
    """Author the required in-place HOI4 humanoid skeletal actions."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError(f"Humanoid action authoring requires exactly one armature, found {len(rigs)}.")
    rig = rigs[0]
    fused_weapon_grip = bool(payload.get("fused_weapon_grip", False))
    isolated_weapon_route = any(bool(obj.get("hoi4_humanoid_weapon", False)) for obj in mesh_objects())
    armed_route = isolated_weapon_route or fused_weapon_grip
    if fused_weapon_grip:
        if isolated_weapon_route:
            raise RuntimeError("Fused weapon-grip action authoring cannot also use an isolated weapon object.")
        required_grip_bones = {"Hips", "Spine02", "RightHand", "LeftHand"}
        missing_grip_bones = sorted(required_grip_bones - {bone.name for bone in rig.pose.bones})
        if missing_grip_bones:
            raise RuntimeError(f"Fused weapon-grip action authoring is missing bones: {missing_grip_bones}")
        if len(mesh_objects()) != 1:
            raise RuntimeError("Fused weapon-grip action authoring requires exactly one accepted character mesh.")
    rig.animation_data_create()
    scene = bpy.context.scene
    scene.render.fps = int(payload.get("fps") or 24)
    base_rig_location = rig.location.copy()
    action_reports: Dict[str, Dict[str, Any]] = {}
    weapon_objects = [obj for obj in mesh_objects() if bool(obj.get("hoi4_humanoid_weapon", False))]
    weapon_grip_targets: Dict[str, List[float]] = {}
    if isolated_weapon_route:
        if len(weapon_objects) != 1:
            raise RuntimeError("Armed humanoid action authoring requires exactly one isolated weapon.")
        weapon_minimum, weapon_maximum = world_bounds(weapon_objects)
        weapon_dimensions = weapon_maximum - weapon_minimum
        weapon_center_x = (weapon_minimum.x + weapon_maximum.x) * 0.5
        weapon_center_z = (weapon_minimum.z + weapon_maximum.z) * 0.5
        weapon_rear_y = weapon_maximum.y
        weapon_length = float(weapon_maximum.y - weapon_minimum.y)
        weapon_grip_targets = {
            "right": [weapon_center_x + 0.08, weapon_rear_y - weapon_length * 0.25, weapon_center_z - 0.12],
            "left": [weapon_center_x - 0.16, weapon_rear_y - weapon_length * 0.30, weapon_center_z - 0.15],
        }

    def make_ik_target(
        collection: bpy.types.Collection,
        name: str,
        world_location: Vector,
        parent_bone: str,
    ) -> bpy.types.Object:
        target = bpy.data.objects.new(name, None)
        collection.objects.link(target)
        target.empty_display_type = "SPHERE"
        target.empty_display_size = 0.08
        target.hide_render = True
        world_matrix = Matrix.Translation(world_location)
        target.parent = rig
        target.parent_type = "BONE"
        target.parent_bone = parent_bone
        target.matrix_world = world_matrix
        return target

    def install_armed_ik(action_name: str) -> Tuple[bpy.types.Collection, List[bpy.types.Constraint]]:
        collection = new_collection(f"IK_{safe_name(action_name)}")
        body_objects = [obj for obj in mesh_objects() if not bool(obj.get("hoi4_humanoid_weapon", False))]
        body_minimum, body_maximum = world_bounds(body_objects)
        body_dimensions = body_maximum - body_minimum
        body_center = (body_minimum + body_maximum) * 0.5
        targets = {
            "Right": make_ik_target(collection, "RightGripTarget", Vector(weapon_grip_targets["right"]), "weapon"),
            "Left": make_ik_target(collection, "LeftForegripTarget", Vector(weapon_grip_targets["left"]), "weapon"),
        }
        poles = {
            "Right": make_ik_target(
                collection,
                "RightElbowPole",
                Vector((body_center.x + body_dimensions.x * 0.42, body_center.y - body_dimensions.y * 0.20, body_minimum.z + body_dimensions.z * 0.50)),
                "Spine02",
            ),
            "Left": make_ik_target(
                collection,
                "LeftElbowPole",
                Vector((body_center.x - body_dimensions.x * 0.42, body_center.y - body_dimensions.y * 0.20, body_minimum.z + body_dimensions.z * 0.50)),
                "Spine02",
            ),
        }
        constraints = []
        for side in ("Right", "Left"):
            forearm = rig.pose.bones.get(f"{side}ForeArm")
            if forearm is None:
                raise RuntimeError(f"Armed IK could not find {side}ForeArm.")
            constraint = forearm.constraints.new("IK")
            constraint.name = f"HOI4_{side.upper()}_WEAPON_IK"
            constraint.target = targets[side]
            constraint.pole_target = poles[side]
            constraint.chain_count = 3
            constraint.use_tail = True
            constraint.influence = 1.0
            constraints.append(constraint)
        return collection, constraints

    def remove_ik_collection(collection: bpy.types.Collection) -> None:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        if bpy.data.collections.get(collection.name) is not None:
            bpy.data.collections.remove(collection)

    def role_frames(role: str) -> List[int]:
        frames = {
            "idle": [0, 12, 24, 36, 48],
            "move": [0, 6, 12, 18, 24],
            "attack": [0, 8, 16, 24, 32],
            "laser_attack": [0, 6, 12, 18, 24],
            "defend": [0, 8, 16, 24, 32],
            "support_attack": [0, 6, 12, 18, 24],
            "retreat": [0, 6, 12, 18, 24],
            "training": [0, 8, 16, 24, 32, 40],
            "death": [0, 12, 19, 24, 30, 36],
        }
        return frames[role]

    def phase(role: str, frame: int, frames: List[int]) -> float:
        normalized = (frame - frames[0]) / max(frames[-1] - frames[0], 1)
        if role in {"idle", "move", "defend", "retreat"}:
            return math.sin(2.0 * math.pi * normalized)
        if role in {"attack", "laser_attack", "support_attack", "training"}:
            return math.sin(math.pi * normalized)
        return normalized

    if fused_weapon_grip:
        roles = ("idle", "move", "laser_attack", "defend", "support_attack", "retreat", "training", "death")
    elif isolated_weapon_route:
        roles = ("idle", "move", "laser_attack", "defend", "support_attack", "retreat", "training", "death")
    else:
        roles = ("idle", "move", "attack", "death")
    for role in roles:
        frames = role_frames(role)
        action_name = safe_name(str(payload.get("action_names", {}).get(role) or f"hoi4_humanoid_{role}"))
        old_action = bpy.data.actions.get(action_name)
        if old_action is not None:
            bpy.data.actions.remove(old_action)
        action = bpy.data.actions.new(action_name)
        action.use_fake_user = True
        rig.animation_data.action = action
        use_ik = isolated_weapon_route and role != "death"
        ik_collection = None
        if use_ik:
            ik_collection, _ = install_armed_ik(action_name)
        scene.frame_start = frames[0]
        scene.frame_end = frames[-1]
        base = {}
        for bone in rig.pose.bones:
            bone.rotation_mode = "QUATERNION"
            base[bone.name] = (bone.location.copy(), bone.rotation_quaternion.copy())

        def rotate(name: str, axis: str, degrees: float, value: float) -> None:
            bone = rig.pose.bones.get(name)
            if bone is None:
                return
            bone.rotation_mode = "QUATERNION"
            bone.rotation_quaternion = base[name][1] @ _action_delta(axis, degrees * value)

        def rotate_many(name: str, rotations: List[Tuple[str, float, float]]) -> None:
            bone = rig.pose.bones.get(name)
            if bone is None:
                return
            rotation = base[name][1].copy()
            for axis, degrees, value in rotations:
                rotation = rotation @ _action_delta(axis, degrees * value)
            bone.rotation_mode = "QUATERNION"
            bone.rotation_quaternion = rotation

        for frame in frames:
            scene.frame_set(frame)
            p = phase(role, frame, frames)
            for bone in rig.pose.bones:
                bone.rotation_mode = "QUATERNION"
                bone.location = base[bone.name][0].copy()
                bone.rotation_quaternion = base[bone.name][1].copy()
                bone.scale = (1.0, 1.0, 1.0)
            if isolated_weapon_route and not use_ik:
                readiness = max(0.0, 1.0 - p) if role == "death" else 1.0
                right_yaw = -78.0
                left_yaw = 78.0
                if role == "defend":
                    right_yaw = -68.0
                    left_yaw = 68.0
                rotate_many("RightShoulder", [("z", right_yaw, readiness), ("x", -5.0, readiness)])
                rotate_many("RightArm", [("z", -8.0, readiness), ("y", -5.0, readiness)])
                rotate_many("RightForeArm", [("z", -5.0, readiness)])
                rotate_many("LeftShoulder", [("z", left_yaw, readiness), ("x", 5.0, readiness)])
                rotate_many("LeftArm", [("z", 18.0, readiness), ("y", 7.0, readiness)])
                rotate_many("LeftForeArm", [("z", 12.0, readiness)])
                rotate_many("RightHand", [("z", -4.0, readiness)])
                rotate_many("LeftHand", [("z", 4.0, readiness)])

            if fused_weapon_grip:
                hips = rig.pose.bones.get("Hips")
                if hips is None:
                    raise RuntimeError("Fused weapon-grip actions require the Hips root bone.")
                if role == "idle":
                    hips.location = base["Hips"][0] + Vector((0.0, 0.0, 0.008 * p))
                    rotate_many("Hips", [("x", 0.35, p), ("z", 0.25, p)])
                elif role == "move":
                    hips.location = base["Hips"][0] + Vector((0.0, 0.0, 0.018 * abs(p)))
                    rotate_many("Hips", [("x", 1.0, 1.0), ("z", 0.8, p)])
                    for side, sign in (("Left", 1.0), ("Right", -1.0)):
                        gait = sign * p
                        rotate(f"{side}UpLeg", "x", 20.0, gait)
                        rotate(f"{side}Leg", "x", -9.0, gait)
                        rotate(f"{side}Foot", "x", 7.0, gait)
                elif role == "laser_attack":
                    hips.location = base["Hips"][0] + Vector((0.0, 0.12 * p, -0.012 * p))
                    rotate_many("Hips", [("x", -2.8, p), ("z", 0.8, p)])
                    rotate("Spine01", "x", -0.12, p)
                    rotate("Spine02", "x", -0.10, p)
                    for side, sign in (("Left", 1.0), ("Right", -1.0)):
                        rotate(f"{side}Shoulder", "y", 0.05, sign * p)
                        rotate(f"{side}Arm", "y", -0.04, sign * p)
                        rotate(f"{side}ForeArm", "y", 0.03, sign * p)
                        rotate(f"{side}Hand", "y", -0.02, sign * p)
                    rotate("RightUpLeg", "x", -3.0, p)
                    rotate("LeftUpLeg", "x", 2.0, p)
                elif role == "support_attack":
                    hips.location = base["Hips"][0] + Vector((0.025 * p, 0.10 * p, -0.010 * p))
                    rotate_many("Hips", [("x", -2.3, p), ("z", 2.0, p)])
                    rotate_many("Spine01", [("x", -0.10, p), ("z", 0.05, p)])
                    rotate_many("Spine02", [("x", -0.08, p), ("z", 0.04, p)])
                    for side, sign in (("Left", 1.0), ("Right", -1.0)):
                        rotate_many(f"{side}Shoulder", [("y", 0.04, sign * p), ("z", 0.02, p)])
                        rotate(f"{side}Arm", "y", -0.03, sign * p)
                        rotate(f"{side}ForeArm", "y", 0.025, sign * p)
                        rotate(f"{side}Hand", "y", -0.015, sign * p)
                    rotate("RightUpLeg", "x", -4.0, p)
                    rotate("LeftUpLeg", "x", 3.0, p)
                elif role == "defend":
                    hips.location = base["Hips"][0] + Vector((0.0, 0.0, -0.035 + 0.008 * p))
                    rotate_many("Hips", [("x", 2.5, 1.0), ("z", 0.6, p)])
                    rotate("RightUpLeg", "x", -10.0, 1.0)
                    rotate("LeftUpLeg", "x", 8.0, 1.0)
                    rotate("RightLeg", "x", 12.0, 1.0)
                    rotate("LeftLeg", "x", -8.0, 1.0)
                elif role == "retreat":
                    hips.location = base["Hips"][0] + Vector((0.0, 0.0, 0.014 * abs(p)))
                    rotate_many("Hips", [("x", 4.0, 1.0), ("z", 1.0, p)])
                    for side, sign in (("Left", -1.0), ("Right", 1.0)):
                        gait = sign * p
                        rotate(f"{side}UpLeg", "x", 16.0, gait)
                        rotate(f"{side}Leg", "x", -7.0, gait)
                        rotate(f"{side}Foot", "x", 5.0, gait)
                elif role == "training":
                    hips.location = base["Hips"][0] + Vector((0.0, -0.04 * p, -0.020 * p))
                    rotate_many("Hips", [("x", -3.0, p), ("z", 2.0, p)])
                    rotate("RightUpLeg", "x", -8.0, p)
                    rotate("LeftUpLeg", "x", 6.0, p)
                    rotate("RightLeg", "x", 6.0, p)
                    rotate("LeftLeg", "x", -4.0, p)
                    rotate("neck", "x", -3.0, p)
                    rotate("Head", "z", -5.0, p)
                else:
                    first_contact_phase = 19.0 / 36.0
                    death_fall_phase = min(p / first_contact_phase, 1.0)
                    death_settle_phase = max(0.0, (p - first_contact_phase) / (1.0 - first_contact_phase))
                    hips.location = base["Hips"][0] + Vector(
                        (
                            -0.25 * death_settle_phase,
                            -0.22 * death_fall_phase - 0.08 * death_settle_phase,
                            -0.08 * death_fall_phase - 0.60 * death_settle_phase,
                        )
                    )
                    rotate_many(
                        "Hips",
                        [
                            ("x", 78.0, death_fall_phase),
                            ("x", 12.0, death_settle_phase),
                            ("y", 48.0, death_settle_phase),
                            ("z", -6.0, death_fall_phase),
                            ("z", -8.0, death_settle_phase),
                        ],
                    )
                    rotate_many(
                        "RightUpLeg",
                        [("x", -28.0, death_fall_phase), ("x", -35.0, death_settle_phase)],
                    )
                    rotate_many(
                        "LeftUpLeg",
                        [("x", -20.0, death_fall_phase), ("x", -45.0, death_settle_phase)],
                    )
                    rotate_many(
                        "RightLeg",
                        [("x", 48.0, death_fall_phase), ("x", 65.0, death_settle_phase)],
                    )
                    rotate_many(
                        "LeftLeg",
                        [("x", 38.0, death_fall_phase), ("x", 55.0, death_settle_phase)],
                    )
                    rotate_many(
                        "RightFoot",
                        [("x", -22.0, death_fall_phase), ("x", -20.0, death_settle_phase)],
                    )
                    rotate_many(
                        "LeftFoot",
                        [("x", -18.0, death_fall_phase), ("x", -25.0, death_settle_phase)],
                    )
            elif role == "idle":
                rotate("Spine01", "x", 1.0, p)
                rotate("Spine02", "x", 1.5, p)
                rotate("neck", "x", 2.0, p)
                rotate("Head", "z", 1.0, p)
                if not armed_route:
                    rotate("LeftForeArm", "x", 1.0, p)
                    rotate("RightForeArm", "x", -1.0, p)
            elif role == "move":
                for side, sign in (("Left", 1.0), ("Right", -1.0)):
                    gait = sign * p
                    rotate(f"{side}UpLeg", "x", 24.0, gait)
                    rotate(f"{side}Leg", "x", -10.0, gait)
                    rotate(f"{side}Foot", "x", 8.0, gait)
                    if not armed_route:
                        rotate(f"{side}Arm", "x", -16.0, gait)
                        rotate(f"{side}ForeArm", "x", -6.0, gait)
                rotate("Spine01", "x", 2.0, p)
                rotate("Spine02", "x", 1.5, p)
                rotate("neck", "x", -1.0, p)
                rotate("Head", "z", 1.0, p)
                hips = rig.pose.bones.get("Hips")
                if hips is not None:
                    hips.location = base["Hips"][0] + Vector((0.0, 0.0, 0.001 * p))
            elif role in {"attack", "laser_attack"}:
                rotate("Spine01", "x", -4.0, p)
                rotate("Spine02", "x", -3.0, p)
                rotate("neck", "x", -3.0, p)
                rotate("Head", "x", -4.0, p)
                if armed_route:
                    rotate_many("RightShoulder", [("z", -78.0, 1.0), ("x", -5.0, 1.0), ("y", -7.0, p)])
                    rotate_many("LeftShoulder", [("z", 78.0, 1.0), ("x", 5.0, 1.0), ("y", 6.0, p)])
                    rotate("RightUpLeg", "x", -5.0, p)
                    rotate("LeftUpLeg", "x", -5.0, p)
                else:
                    for side, sign in (("Left", 1.0), ("Right", -1.0)):
                        rotate(f"{side}Shoulder", "x", -22.0, p)
                        rotate(f"{side}Arm", "x", -30.0, p)
                        rotate(f"{side}ForeArm", "x", -18.0, p)
                        rotate(f"{side}Hand", "z", 8.0 * sign, p)
                        rotate(f"{side}UpLeg", "x", -5.0, p)
            elif role == "support_attack":
                rotate_many("Spine01", [("z", 8.0, 1.0), ("x", -7.0, p)])
                rotate_many("Spine02", [("z", 10.0, 1.0), ("x", -6.0, p)])
                rotate("neck", "z", -8.0, 1.0)
                rotate("Head", "z", -10.0, 1.0)
                rotate_many("RightShoulder", [("z", -78.0, 1.0), ("x", -5.0, 1.0), ("y", -5.0, p)])
                rotate_many("LeftShoulder", [("z", 78.0, 1.0), ("x", 5.0, 1.0), ("y", 5.0, p)])
                rotate("RightUpLeg", "x", -7.0, 1.0)
                rotate("LeftUpLeg", "x", 4.0, 1.0)
            elif role == "defend":
                rotate("Spine", "x", 8.0, 1.0)
                rotate("Spine01", "x", 10.0, 1.0)
                rotate("Spine02", "x", 5.0, p)
                rotate("RightUpLeg", "x", -16.0, 1.0)
                rotate("LeftUpLeg", "x", 12.0, 1.0)
                rotate("RightLeg", "x", 18.0, 1.0)
                rotate("LeftLeg", "x", -12.0, 1.0)
            elif role == "retreat":
                for side, sign in (("Left", -1.0), ("Right", 1.0)):
                    gait = sign * p
                    rotate(f"{side}UpLeg", "x", 18.0, gait)
                    rotate(f"{side}Leg", "x", -8.0, gait)
                    rotate(f"{side}Foot", "x", 6.0, gait)
                rotate("Spine01", "x", 6.0, 1.0)
                rotate("Spine02", "x", 4.0, p)
                rotate("Head", "z", -4.0, p)
            elif role == "training":
                rotate_many("Spine01", [("x", -5.0, p), ("z", 3.0, p)])
                rotate_many("Spine02", [("x", -4.0, p), ("z", 4.0, p)])
                rotate("neck", "x", -3.0, p)
                rotate_many("Head", [("x", -5.0, p), ("z", -4.0, p)])
                rotate("RightUpLeg", "x", -7.0, p)
                rotate("LeftUpLeg", "x", 5.0, p)
                rotate("RightLeg", "x", 5.0, p)
                rotate("LeftLeg", "x", -3.0, p)
                weapon_bone = rig.pose.bones.get("weapon")
                if weapon_bone is not None:
                    weapon_bone.location = base["weapon"][0] + Vector((0.0, -0.03 * p, 0.12 * p))
                    weapon_bone.rotation_mode = "QUATERNION"
                    weapon_bone.rotation_quaternion = base["weapon"][1] @ _action_delta("x", -18.0 * p)
            else:
                rotate("Spine", "x", -34.0, p)
                rotate("Spine01", "x", -38.0, p)
                rotate("Spine02", "x", -28.0, p)
                rotate("neck", "x", -24.0, p)
                rotate("Head", "x", -18.0, p)
                for side, sign in (("Left", 1.0), ("Right", -1.0)):
                    rotate(f"{side}Shoulder", "z", 20.0 * sign, p)
                    rotate(f"{side}Arm", "z", 28.0 * sign, p)
                    rotate(f"{side}ForeArm", "z", 20.0 * sign, p)
                    rotate(f"{side}UpLeg", "x", 8.0, p)
                    rotate(f"{side}Leg", "x", 12.0, p)
            if isolated_weapon_route and role in {"laser_attack", "support_attack"}:
                weapon_bone = rig.pose.bones.get("weapon")
                if weapon_bone is not None:
                    weapon_bone.location = base["weapon"][0] + Vector((0.0, 0.16 * p, 0.0))
                    weapon_bone.rotation_quaternion = base["weapon"][1] @ _action_delta("x", -3.0 * p)
            for bone in rig.pose.bones:
                bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
                bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=bone.name)

        if use_ik:
            bpy.ops.object.select_all(action="DESELECT")
            rig.select_set(True)
            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.mode_set(mode="POSE")
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.nla.bake(
                frame_start=frames[0],
                frame_end=frames[-1],
                step=1,
                only_selected=False,
                visual_keying=True,
                clear_constraints=True,
                clear_parents=False,
                use_current_action=True,
                bake_types={"POSE"},
            )
            bpy.ops.object.mode_set(mode="OBJECT")
            remove_ik_collection(ik_collection)

        for fcurve, _ in action_fcurves(action):
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "LINEAR"

        death_contact_clearance = {
            "LeftToeBase": 0.18,
            "RightToeBase": 0.18,
            "LeftFoot": 0.53,
            "RightFoot": 0.53,
            "LeftLeg": 0.38,
            "RightLeg": 0.38,
            "Hips": 0.48,
            "Spine": 0.45,
            "Spine01": 0.45,
            "Spine02": 0.45,
        }

        def death_body_contact_samples() -> List[Dict[str, Any]]:
            samples = []
            for bone_name, clearance in death_contact_clearance.items():
                bone = rig.pose.bones.get(bone_name)
                if bone is None:
                    raise RuntimeError(f"Death body-contact proxy is missing {bone_name}.")
                head = rig.matrix_world @ bone.head
                samples.append(
                    {
                        "bone": bone_name,
                        "head_z": float(head.z),
                        "clearance_z": clearance,
                        "contact_gap_m": float(head.z) - clearance,
                    }
                )
            return samples

        death_terminal_frames = list(range(30, 37))
        death_terminal_contact_tolerance_m = 0.12
        death_terminal_penetration_tolerance_m = 0.05
        death_terminal_grounding = []
        if role == "death":
            hips = rig.pose.bones.get("Hips")
            if hips is None:
                raise RuntimeError("Death terminal grounding requires the Hips root bone.")
            for frame in (30, 36):
                scene.frame_set(frame)
                rig.location = base_rig_location.copy()
                bpy.context.view_layer.update()
                contacts_before = death_body_contact_samples()
                knee_gap = min(
                    item["contact_gap_m"]
                    for item in contacts_before
                    if item["bone"] in {"LeftLeg", "RightLeg"}
                )
                torso_gap = min(
                    item["contact_gap_m"]
                    for item in contacts_before
                    if item["bone"] in {"Hips", "Spine", "Spine01", "Spine02"}
                )
                correction = -0.5 * (knee_gap + torso_gap)
                hips.location.z += correction
                hips.keyframe_insert(data_path="location", index=2, frame=frame, group=hips.name)
                scene.frame_set(frames[0])
                scene.frame_set(frame)
                bpy.context.view_layer.update()
                contacts_after = death_body_contact_samples()
                death_terminal_grounding.append(
                    {
                        "frame": frame,
                        "hips_root_vertical_correction_m": correction,
                        "knee_gap_before_m": knee_gap,
                        "torso_gap_before_m": torso_gap,
                        "body_contact_proxy_after": contacts_after,
                    }
                )

        ground_samples_before = []
        ground_samples_after = []
        corrections = []
        for frame in range(frames[0], frames[-1] + 1):
            scene.frame_set(frame)
            rig.location = base_rig_location.copy()
            bpy.context.view_layer.update()
            minimum, maximum = evaluated_world_bounds(mesh_objects())
            body_contact_before = death_body_contact_samples() if role == "death" else []
            ground_samples_before.append(
                {
                    "frame": frame,
                    "ground_contact_z": float(minimum.z),
                    "bounds_max_z": float(maximum.z),
                    "bounds_center_z": float((minimum.z + maximum.z) * 0.5),
                    "body_contact_proxy": body_contact_before,
                }
            )
            correction = 0.0 if role == "death" else max(0.0, -float(minimum.z))
            rig.location.z = base_rig_location.z + correction
            if role != "death":
                rig.keyframe_insert(data_path="location", index=2, frame=frame, group=rig.name)
            bpy.context.view_layer.update()
            corrected_minimum, corrected_maximum = evaluated_world_bounds(mesh_objects())
            body_contact_after = death_body_contact_samples() if role == "death" else []
            ground_samples_after.append(
                {
                    "frame": frame,
                    "ground_contact_z": float(corrected_minimum.z),
                    "bounds_max_z": float(corrected_maximum.z),
                    "bounds_center_z": float((corrected_minimum.z + corrected_maximum.z) * 0.5),
                    "body_contact_proxy": body_contact_after,
                    "body_contact_minimum_gap_m": (
                        min(item["contact_gap_m"] for item in body_contact_after)
                        if body_contact_after
                        else None
                    ),
                }
            )
            corrections.append(correction)

        scene.frame_set(frames[0])
        rig.location = base_rig_location.copy()
        metrics = action_metrics()
        fused_grip_lock: Dict[str, Any] = {}
        fused_grip_pass = True
        if fused_weapon_grip:
            grip_samples = []
            baseline_distances: Optional[Tuple[float, float, float]] = None
            baseline_axis: Optional[Vector] = None
            maximum_distance_drift = 0.0
            maximum_axis_drift = 0.0
            for sample_frame in frames:
                scene.frame_set(sample_frame)
                bpy.context.view_layer.update()
                right_hand = rig.matrix_world @ rig.pose.bones["RightHand"].head
                left_hand = rig.matrix_world @ rig.pose.bones["LeftHand"].head
                stock_proxy = rig.matrix_world @ rig.pose.bones["Spine02"].head
                grip_axis = left_hand - right_hand
                if grip_axis.length <= 1e-8:
                    raise RuntimeError("Fused weapon-grip muzzle proxy collapsed to zero length.")
                distances = (
                    float((left_hand - right_hand).length),
                    float((right_hand - stock_proxy).length),
                    float((left_hand - stock_proxy).length),
                )
                if baseline_distances is None:
                    baseline_distances = distances
                    baseline_axis = grip_axis.normalized()
                distance_drift = max(abs(value - baseline) for value, baseline in zip(distances, baseline_distances))
                axis_drift = math.degrees(grip_axis.normalized().angle(baseline_axis))
                maximum_distance_drift = max(maximum_distance_drift, distance_drift)
                maximum_axis_drift = max(maximum_axis_drift, axis_drift)
                grip_samples.append(
                    {
                        "frame": sample_frame,
                        "right_hand": list(right_hand),
                        "left_hand": list(left_hand),
                        "stock_proxy": list(stock_proxy),
                        "right_to_left_grip_distance_m": distances[0],
                        "right_grip_to_stock_proxy_distance_m": distances[1],
                        "left_foregrip_to_stock_proxy_distance_m": distances[2],
                        "distance_drift_from_bind_m": distance_drift,
                        "muzzle_proxy_angular_drift_degrees": axis_drift,
                    }
                )
            muzzle_axis_limit = 90.0 if role == "death" else 5.0
            fused_grip_pass = maximum_distance_drift <= 0.005 and maximum_axis_drift <= muzzle_axis_limit
            fused_grip_lock = {
                "mode": "single_fused_character_mesh_preserve_bind_grip",
                "measurement": "RightHand-to-LeftHand grip axis plus both hand distances to Spine02 stock proxy",
                "maximum_distance_drift_m": maximum_distance_drift,
                "maximum_muzzle_proxy_angular_drift_degrees": maximum_axis_drift,
                "distance_drift_limit_m": 0.005,
                "muzzle_proxy_angular_drift_limit_degrees": muzzle_axis_limit,
                "muzzle_axis_policy": (
                    "intentional full-body fall may rotate the held assembly while contact distances remain locked"
                    if role == "death"
                    else "combat and locomotion actions retain a stable forward grip axis"
                ),
                "samples": grip_samples,
                "status": "pass" if fused_grip_pass else "failed",
            }
            scene.frame_set(frames[0])
        death_center_samples = [item["bounds_center_z"] for item in ground_samples_after]
        death_center_monotonic = all(
            later <= earlier + 0.02
            for earlier, later in zip(death_center_samples, death_center_samples[1:])
        )
        death_center_drop = death_center_samples[0] - death_center_samples[-1]
        death_peak_rise = max(death_center_samples) - death_center_samples[0]
        death_terminal_rebound = death_center_samples[-1] - min(death_center_samples)
        death_minimum_drop_m = 0.4
        death_maximum_anticipation_rise_m = 0.3
        death_maximum_terminal_rebound_m = 0.15
        death_collapse_pass = role != "death" or (
            death_center_drop >= death_minimum_drop_m
            and death_peak_rise <= death_maximum_anticipation_rise_m
            and death_terminal_rebound <= death_maximum_terminal_rebound_m
            and death_center_monotonic
        )
        body_contact_minimum_gap = (
            min(item["body_contact_minimum_gap_m"] for item in ground_samples_after)
            if role == "death"
            else None
        )
        terminal_ground_samples = (
            [item for item in ground_samples_after if item["frame"] in death_terminal_frames]
            if role == "death"
            else []
        )
        terminal_contact_samples = []
        terminal_contact_pass = True
        if role == "death":
            for sample in terminal_ground_samples:
                proxies = sample["body_contact_proxy"]
                knee_gap = min(
                    item["contact_gap_m"]
                    for item in proxies
                    if item["bone"] in {"LeftLeg", "RightLeg"}
                )
                torso_gap = min(
                    item["contact_gap_m"]
                    for item in proxies
                    if item["bone"] in {"Hips", "Spine", "Spine01", "Spine02"}
                )
                sample_pass = (
                    -death_terminal_penetration_tolerance_m <= knee_gap <= death_terminal_contact_tolerance_m
                    and -death_terminal_penetration_tolerance_m <= torso_gap <= death_terminal_contact_tolerance_m
                )
                terminal_contact_pass = terminal_contact_pass and sample_pass
                terminal_contact_samples.append(
                    {
                        "frame": sample["frame"],
                        "knee_minimum_gap_m": knee_gap,
                        "torso_minimum_gap_m": torso_gap,
                        "status": "pass" if sample_pass else "failed",
                    }
                )
        corrected_terminal_bounds_nonrising = (
            terminal_ground_samples[-1]["bounds_center_z"]
            <= terminal_ground_samples[0]["bounds_center_z"] + 0.02
            if role == "death" and terminal_ground_samples
            else True
        )
        ground_contact_pass = (
            terminal_contact_pass and corrected_terminal_bounds_nonrising
            if role == "death"
            else min(item["ground_contact_z"] for item in ground_samples_after) >= -0.01
        )
        report = {
            "action": action.name,
            "role": role,
            "frame_start": frames[0],
            "frame_end": frames[-1],
            "fps": scene.render.fps,
            "loop": role in {"idle", "move", "defend", "retreat"},
            "keyed_bones": len(rig.pose.bones) * len(frames),
            "keyed_channels": len(rig.pose.bones) * len(frames) * 2,
            "ground_contact": {
                "minimum_z": min(item["ground_contact_z"] for item in ground_samples_after),
                "maximum_z": max(item["ground_contact_z"] for item in ground_samples_after),
                "body_contact_minimum_gap_m": body_contact_minimum_gap,
                "terminal_contact_frames": death_terminal_frames if role == "death" else [],
                "terminal_contact_tolerance_m": death_terminal_contact_tolerance_m if role == "death" else None,
                "terminal_penetration_tolerance_m": death_terminal_penetration_tolerance_m if role == "death" else None,
                "terminal_contact_samples": terminal_contact_samples,
                "corrected_terminal_bounds_nonrising": corrected_terminal_bounds_nonrising,
                "policy": (
                    "terminal post-grounding knee plus hips/spine contact; fused rifle and muzzle excluded"
                    if role == "death"
                    else "evaluated full-mesh minimum"
                ),
                "samples_before": ground_samples_before,
                "samples_after": ground_samples_after,
            },
            "grounding_correction": {
                "applied": (
                    any(abs(value) > 1e-8 for value in corrections)
                    or any(
                        abs(item["hips_root_vertical_correction_m"]) > 1e-8
                        for item in death_terminal_grounding
                    )
                ),
                "minimum_translation_m": min(corrections, default=0.0),
                "maximum_translation_m": max(corrections, default=0.0),
                "maximum_absolute_translation_m": max((abs(value) for value in corrections), default=0.0),
                "terminal_hips_root_corrections": death_terminal_grounding,
            },
            "death_collapse": (
                {
                    "bounds_center_z_samples": death_center_samples,
                    "monotonic_nonincreasing_tolerance_m": 0.02,
                    "monotonic_nonincreasing": death_center_monotonic,
                    "final_center_drop_m": death_center_drop,
                    "minimum_final_center_drop_m": death_minimum_drop_m,
                    "maximum_anticipation_rise_m": death_peak_rise,
                    "maximum_allowed_anticipation_rise_m": death_maximum_anticipation_rise_m,
                    "terminal_rebound_m": death_terminal_rebound,
                    "maximum_allowed_terminal_rebound_m": death_maximum_terminal_rebound_m,
                    "acceptance_policy": "bounded silhouette-aware collapse with limited anticipation and terminal settling",
                    "status": "pass" if death_collapse_pass else "failed",
                }
                if role == "death"
                else {}
            ),
            "policy": (
                "blender-authored-hoi4-fused-weapon-grip-skeletal-action-in-place-no-scale-channels"
                if fused_weapon_grip
                else (
                    "blender-authored-hoi4-armed-humanoid-skeletal-action-in-place-no-scale-channels"
                    if armed_route
                    else "blender-authored-hoi4-humanoid-skeletal-action-in-place-no-scale-channels"
                )
            ),
            "weapon_grip_targets": weapon_grip_targets if armed_route else {},
            "weapon_ik_baked": use_ik,
            "fused_weapon_grip_lock": fused_grip_lock,
            "rig_and_actions": metrics,
            "status": (
                "pass"
                if ground_contact_pass and fused_grip_pass
                and death_collapse_pass
                else (
                    "failed_grip_lock"
                    if not fused_grip_pass
                    else ("failed_death_collapse" if not death_collapse_pass else "needs_grounding_review")
                )
            ),
        }
        report_path = job / "blender" / "reports" / f"humanoid_action_{role}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        action_reports[role] = report

    save_blend(checkpoint)
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "armature": rig.name,
        "actions": action_reports,
        "required_roles": list(roles),
        "source_policy": (
            "Meshy 7 fused armed geometry and accepted provider rig retained; seven grip-locked actions authored locally"
            if fused_weapon_grip
            else "Meshy 7 geometry retained; actions authored locally only after provider-rig recovery failure"
        ),
        "status": "pass" if all(item.get("status") == "pass" for item in action_reports.values()) else "needs_grounding_review",
    }
    report_path = job / "blender" / "reports" / "humanoid_actions.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def author_locomotion_action(req: Dict[str, Any]) -> Dict[str, Any]:
    """Author a small in-place walk cycle on the approved humanoid rig."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if not rigs:
        raise RuntimeError("Locomotion authoring requires a working armature.")
    rig = rigs[0]
    if not rig.animation_data or rig.animation_data.action is None:
        raise RuntimeError("Locomotion authoring requires the approved base action.")
    base_action = rig.animation_data.action
    frames = [0, 6, 12, 18, 24]
    scene = bpy.context.scene
    scene.frame_set(0)
    base_snapshot: Dict[str, Tuple[Vector, Any]] = {
        bone.name: (bone.location.copy(), bone.rotation_quaternion.copy())
        for bone in rig.pose.bones
    }

    action_name = str(payload.get("action_name") or "Armature|Move|baselayer_WORKING")
    old_action = bpy.data.actions.get(action_name)
    if old_action is not None:
        bpy.data.actions.remove(old_action)
    action = bpy.data.actions.new(action_name)
    rig.animation_data.action = action

    phase_values = {0: 1.0, 6: 0.0, 12: -1.0, 18: 0.0, 24: 1.0}
    root_bob_amplitude = 0.001
    walk_angles = {
        "LeftUpLeg": 24.0,
        "RightUpLeg": -24.0,
        "LeftArm": -16.0,
        "RightArm": 16.0,
        "LeftForeArm": -6.0,
        "RightForeArm": 6.0,
        "Spine01": 2.0,
        "Spine02": 1.5,
        "neck": -1.0,
        "Head": -1.0,
    }
    knee_angles = {
        "LeftLeg": -10.0,
        "RightLeg": -10.0,
        "LeftFoot": 8.0,
        "RightFoot": 8.0,
    }
    keyed_bones = 0
    for frame in frames:
        scene.frame_set(frame)
        phase = phase_values[frame]
        for bone in rig.pose.bones:
            base_location, base_rotation = base_snapshot[bone.name]
            bone.rotation_mode = "QUATERNION"
            if bone.name == "Hips":
                bone.location = base_location + Vector((0.0, 0.0, root_bob_amplitude * phase))
            else:
                bone.location = base_location
            angle_degrees = walk_angles.get(bone.name, 0.0) * phase
            if bone.name in knee_angles:
                angle_degrees += knee_angles[bone.name] * (0.5 + 0.5 * abs(phase))
            if bone.name == "Hips":
                angle_degrees += 1.5 * phase
            delta = Quaternion((1.0, 0.0, 0.0), math.radians(angle_degrees))
            bone.rotation_quaternion = base_rotation @ delta
            bone.scale = (1.0, 1.0, 1.0)
            bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
            bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=bone.name)
            keyed_bones += 1

    scene.frame_start = 0
    scene.frame_end = 24
    scene.frame_set(0)
    for fcurve, _ in action_fcurves(action):
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "LINEAR"
    move_ground_before, _ = evaluated_world_bounds(mesh_objects())
    move_ground_correction = 0.0
    move_root_curves = [
        fcurve
        for fcurve, _ in action_fcurves(action)
        if fcurve.data_path == 'pose.bones["Hips"].location'
    ]
    move_z_curve = next(
        (fcurve for fcurve in move_root_curves if fcurve.array_index == 2),
        None,
    )
    if move_z_curve is not None:
        test_step = 1.0
        for keyframe in move_z_curve.keyframe_points:
            keyframe.co[1] += test_step
            keyframe.handle_left[1] += test_step
            keyframe.handle_right[1] += test_step
        move_z_curve.update()
        bpy.context.view_layer.update()
        move_test_minimum, _ = evaluated_world_bounds(mesh_objects())
        for keyframe in move_z_curve.keyframe_points:
            keyframe.co[1] -= test_step
            keyframe.handle_left[1] -= test_step
            keyframe.handle_right[1] -= test_step
        move_z_curve.update()
        bpy.context.view_layer.update()
        derivative = float(move_test_minimum.z - move_ground_before.z) / test_step
        if abs(derivative) > 1e-8:
            move_ground_correction = -float(move_ground_before.z) / derivative
            for keyframe in move_z_curve.keyframe_points:
                keyframe.co[1] += move_ground_correction
                keyframe.handle_left[1] += move_ground_correction
                keyframe.handle_right[1] += move_ground_correction
            move_z_curve.update()
            bpy.context.view_layer.update()
    move_ground_after, _ = evaluated_world_bounds(mesh_objects())
    save_blend(checkpoint)
    metrics = action_metrics()
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "base_action": base_action.name,
        "action": action.name,
        "frame_start": 0,
        "frame_end": 24,
        "fps": scene.render.fps,
        "keyed_bones": keyed_bones,
        "keyed_channels": keyed_bones * 2,
        "root_translation_channel": "forced_with_submillimeter_in_place_bob",
        "root_bob_amplitude": root_bob_amplitude,
        "ground_contact_before": float(move_ground_before.z),
        "ground_contact_after": float(move_ground_after.z),
        "ground_correction_source_units": move_ground_correction,
        "policy": "blender_authored_in_place_walk_no_scale_channels",
        "rig_and_actions": metrics,
    }
    report_path = job / "blender" / "reports" / "author_locomotion_action.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _working_collection() -> bpy.types.Collection:
    collection = bpy.data.collections.get("WORKING")
    if collection is None:
        raise RuntimeError("Creature operation requires the WORKING collection.")
    return collection


def _component_record(obj: bpy.types.Object, index: int) -> Dict[str, Any]:
    minimum, maximum = world_bounds([obj])
    dimensions = maximum - minimum
    return {
        "index": index,
        "name": obj.name,
        "bounds_min": list(minimum),
        "bounds_max": list(maximum),
        "center": list((minimum + maximum) * 0.5),
        "dimensions": list(dimensions),
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "volume_proxy": float(max(dimensions.x, 0.0) * max(dimensions.y, 0.0) * max(dimensions.z, 0.0)),
        "materials": [material.name for material in obj.data.materials if material is not None],
    }


def _creature_spatial_profile(obj: bpy.types.Object, z_bins: int = 20, xy_bins: int = 8) -> Dict[str, Any]:
    """Return a deterministic face-centroid profile for a fused creature mesh.

    Meshy can return a single topologically connected shell even when the image
    clearly contains an elephant, howdah, and rider.  A profile lets the parent
    choose an explicit, reviewable spatial rider mask instead of silently
    treating the whole shell as a miniature.  This is diagnostic only; it does
    not infer a rider from a machine-learning classifier.
    """

    minimum, maximum = world_bounds([obj])
    dimensions = maximum - minimum
    safe_z = max(float(dimensions.z), 1e-9)
    safe_x = max(float(dimensions.x), 1e-9)
    safe_y = max(float(dimensions.y), 1e-9)
    profile_z = [0 for _ in range(max(1, z_bins))]
    profile_xy = [[0 for _ in range(max(1, xy_bins))] for _ in range(max(1, xy_bins))]
    z_area = [0.0 for _ in range(max(1, z_bins))]
    z_min = [float("inf") for _ in range(max(1, z_bins))]
    z_max = [float("-inf") for _ in range(max(1, z_bins))]
    high_centers: List[Vector] = []
    high_slices: Dict[int, List[Vector]] = {}
    high_face_counts: Dict[str, int] = {}
    for polygon in obj.data.polygons:
        center = obj.matrix_world @ polygon.center
        fraction_z = min(0.999999, max(0.0, (center.z - minimum.z) / safe_z))
        fraction_x = min(0.999999, max(0.0, (center.x - minimum.x) / safe_x))
        fraction_y = min(0.999999, max(0.0, (center.y - minimum.y) / safe_y))
        zi = min(len(profile_z) - 1, int(fraction_z * len(profile_z)))
        xi = min(len(profile_xy) - 1, int(fraction_x * len(profile_xy)))
        yi = min(len(profile_xy) - 1, int(fraction_y * len(profile_xy)))
        area = float(polygon.area)
        profile_z[zi] += 1
        profile_xy[xi][yi] += 1
        z_area[zi] += area
        z_min[zi] = min(z_min[zi], float(center.z))
        z_max[zi] = max(z_max[zi], float(center.z))
        if fraction_z >= 0.70:
            high_centers.append(center)
            high_bin = f"z_{int(fraction_z * 10):02d}"
            high_face_counts[high_bin] = high_face_counts.get(high_bin, 0) + 1
            high_slices.setdefault(int(fraction_z * 10), []).append(center)
    high_minimum = Vector((
        min((point.x for point in high_centers), default=minimum.x),
        min((point.y for point in high_centers), default=minimum.y),
        min((point.z for point in high_centers), default=minimum.z),
    ))
    high_maximum = Vector((
        max((point.x for point in high_centers), default=maximum.x),
        max((point.y for point in high_centers), default=maximum.y),
        max((point.z for point in high_centers), default=maximum.z),
    ))
    high_mean = Vector((
        sum(point.x for point in high_centers) / max(1, len(high_centers)),
        sum(point.y for point in high_centers) / max(1, len(high_centers)),
        sum(point.z for point in high_centers) / max(1, len(high_centers)),
    ))
    return {
        "object": obj.name,
        "bounds_min": list(minimum),
        "bounds_max": list(maximum),
        "dimensions": list(dimensions),
        "z_bins": [
            {
                "index": index,
                "fraction_min": index / max(1, len(profile_z)),
                "fraction_max": (index + 1) / max(1, len(profile_z)),
                "face_count": profile_z[index],
                "surface_area": z_area[index],
                "center_z_min": None if z_min[index] == float("inf") else z_min[index],
                "center_z_max": None if z_max[index] == float("-inf") else z_max[index],
            }
            for index in range(len(profile_z))
        ],
        "xy_face_bins": profile_xy,
        "face_count": len(obj.data.polygons),
        "high_region_centroid_stats": {
            "threshold_fraction_z": 0.70,
            "face_count": len(high_centers),
            "bounds_min": list(high_minimum),
            "bounds_max": list(high_maximum),
            "mean": list(high_mean),
            "z_decile_face_counts": high_face_counts,
            "z_decile_bounds": {
                str(decile): {
                    "face_count": len(points),
                    "bounds_min": [
                        min(point.x for point in points),
                        min(point.y for point in points),
                        min(point.z for point in points),
                    ],
                    "bounds_max": [
                        max(point.x for point in points),
                        max(point.y for point in points),
                        max(point.z for point in points),
                    ],
                    "mean": [
                        sum(point.x for point in points) / len(points),
                        sum(point.y for point in points) / len(points),
                        sum(point.z for point in points) / len(points),
                    ],
                }
                for decile, points in sorted(high_slices.items())
                if points
            },
        },
    }


def _duplicate_spatial_region(
    source: bpy.types.Object,
    name: str,
    keep_face,
) -> Dict[str, Any]:
    """Copy a fused mesh and retain only faces accepted by a bounded mask."""

    data = source.data.copy()
    region = bpy.data.objects.new(name, data)
    _working_collection().objects.link(region)
    region.matrix_world = source.matrix_world.copy()
    region["hoi4_working"] = True
    region["hoi4_creature_component"] = True
    bm = bmesh.new()
    bm.from_mesh(data)
    bm.faces.ensure_lookup_table()
    removed_faces = [face for face in bm.faces if not keep_face(source.matrix_world @ face.calc_center_median())]
    if removed_faces:
        bmesh.ops.delete(bm, geom=removed_faces, context="FACES")
    bm.verts.ensure_lookup_table()
    loose_vertices = [vertex for vertex in bm.verts if not vertex.link_faces]
    if loose_vertices:
        bmesh.ops.delete(bm, geom=loose_vertices, context="VERTS")
    bm.to_mesh(data)
    bm.free()
    data.update()
    region.hide_set(False)
    return {
        "object": region,
        "removed_faces": len(removed_faces),
        "kept_faces": len(data.polygons),
        "geometry": geometry_metrics_for_object(region),
    }


def segment_creature_components(req: Dict[str, Any]) -> Dict[str, Any]:
    """Separate a provider creature into loose or explicitly spatial components."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    component_prefix = safe_name(str(payload.get("component_prefix") or "elephant_component"))
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    if not working:
        raise RuntimeError("Creature segmentation found no working meshes.")
    region_mode = str(payload.get("region_mode") or "loose").casefold()
    if region_mode == "profile":
        profiles = [_creature_spatial_profile(obj) for obj in working]
        report_path = job / "blender" / "reports" / "creature_components.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "blend": str(blend.relative_to(job)).replace("\\", "/"),
            "checkpoint": None,
            "source_working_objects": sorted(obj.name for obj in working),
            "component_count": len(working),
            "components": [_component_record(obj, index) for index, obj in enumerate(working)],
            "spatial_profiles": profiles,
            "method": "diagnostic polygon-centroid spatial profile; no geometry mutation",
            "status": "profile_only",
        }
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report
    before_names = {obj.name for obj in working}
    spatial_mask_applied = False
    spatial_mask = None
    if region_mode in {"spatial_rider", "spatial_semantic"}:
        if len(working) != 1:
            raise RuntimeError("Spatial rider segmentation requires exactly one fused source mesh.")
        source = working[0]
        minimum, maximum = world_bounds([source])
        dimensions = maximum - minimum
        z_min_fraction = float(payload.get("rider_z_min_fraction", 0.72))
        z_max_fraction = float(payload.get("rider_z_max_fraction", 1.0))
        x_center_fraction = float(payload.get("rider_x_center_fraction", 0.5))
        x_half_fraction = float(payload.get("rider_x_half_fraction", 0.38))
        y_center_fraction = float(payload.get("rider_y_center_fraction", 0.5))
        y_half_fraction = float(payload.get("rider_y_half_fraction", 0.42))
        if not (0.0 <= z_min_fraction < z_max_fraction <= 1.0):
            raise ValueError("Rider z fractions must satisfy 0 <= min < max <= 1.")
        if x_half_fraction <= 0.0 or y_half_fraction <= 0.0:
            raise ValueError("Rider spatial half-width fractions must be positive.")
        x_center = minimum.x + dimensions.x * x_center_fraction
        y_center = minimum.y + dimensions.y * y_center_fraction
        z_min = minimum.z + dimensions.z * z_min_fraction
        z_max = minimum.z + dimensions.z * z_max_fraction
        x_half = dimensions.x * x_half_fraction
        y_half = dimensions.y * y_half_fraction

        def is_rider(center: Vector) -> bool:
            return (
                z_min <= center.z <= z_max
                and abs(center.x - x_center) <= x_half
                and abs(center.y - y_center) <= y_half
            )

        rider_name = str(payload.get("rider_object_name") or "elephant_rider_region")
        body_name = str(payload.get("body_object_name") or "elephant_body_region")
        if region_mode == "spatial_semantic":
            def semantic_region(center: Vector) -> str:
                if is_rider(center):
                    return rider_name
                fx = (center.x - minimum.x) / max(float(dimensions.x), 1e-9)
                fy = (center.y - minimum.y) / max(float(dimensions.y), 1e-9)
                fz = (center.z - minimum.z) / max(float(dimensions.z), 1e-9)
                side = "left" if fx < 0.5 else "right"
                if fy > 0.82 and 0.20 <= fz <= 0.68:
                    return "tail"
                if fy < 0.24 and fz < 0.30 and 0.28 <= fx <= 0.72:
                    return "trunk_02"
                if fy < 0.30 and 0.30 <= fz < 0.54 and 0.25 <= fx <= 0.75:
                    return "trunk_01"
                if fy < 0.34 and fz >= 0.48:
                    return "head"
                if fz < 0.52 and (fx < 0.38 or fx > 0.62):
                    end = "front" if fy < 0.5 else "rear"
                    section = "lower" if fz < 0.25 else "upper"
                    return f"{end}_{side}_{section}"
                if fz > 0.68 and 0.25 <= fy <= 0.78:
                    return "howdah"
                return body_name

            semantic_names = [
                rider_name,
                body_name,
                "head",
                "trunk_01",
                "trunk_02",
                "tail",
                "howdah",
                "front_left_upper",
                "front_left_lower",
                "front_right_upper",
                "front_right_lower",
                "rear_left_upper",
                "rear_left_lower",
                "rear_right_upper",
                "rear_right_lower",
            ]
            semantic_components = []
            semantic_records = {}
            for semantic_name in semantic_names:
                record = _duplicate_spatial_region(
                    source,
                    semantic_name,
                    lambda center, expected=semantic_name: semantic_region(center) == expected,
                )
                if record["kept_faces"]:
                    semantic_components.append(record["object"])
                    semantic_records[semantic_name] = {
                        "faces": record["kept_faces"],
                        "geometry": record["geometry"],
                    }
                else:
                    bpy.data.objects.remove(record["object"], do_unlink=True)
            if rider_name not in semantic_records or body_name not in semantic_records:
                raise RuntimeError("Spatial semantic segmentation produced an empty rider or body region; adjust the explicit mask.")
            rider = {"object": next(obj for obj in semantic_components if obj.name == rider_name), "kept_faces": semantic_records[rider_name]["faces"], "geometry": semantic_records[rider_name]["geometry"]}
            body = {"object": next(obj for obj in semantic_components if obj.name == body_name), "kept_faces": semantic_records[body_name]["faces"], "geometry": semantic_records[body_name]["geometry"]}
            components = semantic_components
        else:
            rider = _duplicate_spatial_region(source, rider_name, is_rider)
            body = _duplicate_spatial_region(source, body_name, lambda center: not is_rider(center))
            if rider["kept_faces"] == 0 or body["kept_faces"] == 0:
                raise RuntimeError("Spatial rider segmentation produced an empty rider or body region; adjust the explicit mask.")
            components = [rider["object"], body["object"]]
        bpy.data.objects.remove(source, do_unlink=True)
        spatial_mask_applied = True
        spatial_mask = {
            "region_mode": region_mode,
            "rider_z_min_fraction": z_min_fraction,
            "rider_z_max_fraction": z_max_fraction,
            "rider_x_center_fraction": x_center_fraction,
            "rider_x_half_fraction": x_half_fraction,
            "rider_y_center_fraction": y_center_fraction,
            "rider_y_half_fraction": y_half_fraction,
            "rider_object": rider_name,
            "body_object": body_name,
            "rider_faces": rider["kept_faces"],
            "body_faces": body["kept_faces"],
            "rider_geometry": rider["geometry"],
            "body_geometry": body["geometry"],
            "semantic_regions": semantic_records if region_mode == "spatial_semantic" else None,
        }
    elif len(working) == 1:
        target = working[0]
        bpy.ops.object.select_all(action="DESELECT")
        target.select_set(True)
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type="LOOSE")
        bpy.ops.object.mode_set(mode="OBJECT")
    collection = _working_collection()
    if not spatial_mask_applied:
        components = [obj for obj in collection.objects if obj.type == "MESH"]
    if not components:
        raise RuntimeError("Creature segmentation produced no mesh components.")
    discarded_degenerate_components = []
    retained_components = []
    for obj in components:
        if len(obj.data.polygons) == 0:
            discarded_degenerate_components.append(
                {
                    "object": obj.name,
                    "vertices": len(obj.data.vertices),
                    "polygons": 0,
                    "reason": "zero_face_component_cannot_be_reimported_as_a_runtime_mesh_node",
                }
            )
            bpy.data.objects.remove(obj, do_unlink=True)
        else:
            retained_components.append(obj)
    components = retained_components
    if not components:
        raise RuntimeError("Creature segmentation retained no renderable mesh components.")
    for obj in components:
        obj["hoi4_working"] = True
        obj["hoi4_creature_component"] = True
        obj.hide_set(False)
    components.sort(key=lambda obj: _component_record(obj, 0)["volume_proxy"], reverse=True)
    records = []
    for index, obj in enumerate(components):
        if not spatial_mask_applied:
            obj.name = f"{component_prefix}_{index:03d}"
        records.append(_component_record(obj, index))
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "source_working_objects": sorted(before_names),
        "component_count": len(records),
        "components": records,
        "discarded_degenerate_components": discarded_degenerate_components,
        "method": (
            "explicit polygon-centroid spatial rider/semantic mask on a fused approved working mesh"
            if spatial_mask_applied
            else "Blender mesh separate by loose parts on the approved working mesh"
        ),
        "spatial_mask": spatial_mask,
        "status": "review_required",
    }
    report_path = job / "blender" / "reports" / "creature_components.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _trailing_component_index(name: str) -> Optional[int]:
    match = re.search(r"_(\d+)$", name)
    return int(match.group(1)) if match else None


def _join_mesh_objects(objects: List[bpy.types.Object], name: str) -> bpy.types.Object:
    if not objects:
        raise RuntimeError(f"Cannot join an empty mesh group for {name}.")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.hide_render = False
        obj.select_set(True)
    active = objects[0]
    bpy.context.view_layer.objects.active = active
    if len(objects) > 1:
        bpy.ops.object.join()
    active.name = safe_name(name)
    active.data.name = f"{active.name}_mesh"
    active["hoi4_working"] = True
    return active


def _component_review_material(name: str, color: Tuple[float, float, float, float], emission: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = next(
        (node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"),
        None,
    )
    if principled is None:
        raise RuntimeError("Component review could not create a Principled material.")
    base = principled.inputs.get("Base Color")
    if base is not None:
        base.default_value = color
    roughness = principled.inputs.get("Roughness")
    if roughness is not None:
        roughness.default_value = 0.72
    emission_color = principled.inputs.get("Emission Color") or principled.inputs.get("Emission")
    if emission_color is not None:
        emission_color.default_value = color
    emission_strength = principled.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = emission
    return material


def review_humanoid_components(req: Dict[str, Any]) -> Dict[str, Any]:
    """Render explicit loose-component ids over a dim whole-body reference."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    requested = sorted({int(value) for value in payload.get("component_indices", [])})
    if not requested:
        raise RuntimeError("Humanoid component review requires at least one explicit component index.")
    if len(requested) > 96:
        raise RuntimeError("Humanoid component review is bounded to 96 explicit indices per request.")
    views = [str(value) for value in payload.get("view_names", ["rear"])]
    allowed_views = {"front", "rear", "left", "right", "top", "underside", "three_quarter"}
    if not views or any(value not in allowed_views for value in views):
        raise RuntimeError(f"Component review views must be selected from {sorted(allowed_views)}.")
    runtime_stem = safe_name(str(payload.get("runtime_stem") or "humanoid_component_review"))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    by_index = {
        index: obj
        for obj in working
        if (index := _trailing_component_index(obj.name)) is not None
    }
    missing = sorted(set(requested) - set(by_index))
    if missing:
        raise RuntimeError(f"Requested humanoid component indices were not found: {missing}")

    dim = _component_review_material("QA_Component_Dim", (0.035, 0.045, 0.055, 1.0), 0.0)
    highlight = _component_review_material("QA_Component_Highlight", (0.02, 0.85, 1.0, 1.0), 1.8)
    for obj in working:
        obj.data.materials.clear()
        obj.data.materials.append(dim)
    previews: Dict[str, List[str]] = {}
    if bool(payload.get("render_group", False)):
        for index in requested:
            by_index[index].data.materials.clear()
            by_index[index].data.materials.append(highlight)
        previews["group"] = render_previews(job, f"{runtime_stem}_group", views)
    else:
        for index in requested:
            candidate = by_index[index]
            candidate.data.materials.clear()
            candidate.data.materials.append(highlight)
            paths = render_previews(
                job,
                f"{runtime_stem}_component_{index:03d}",
                views,
            )
            previews[str(index)] = paths
            candidate.data.materials.clear()
            candidate.data.materials.append(dim)

    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "component_indices": requested,
        "views": views,
        "render_group": bool(payload.get("render_group", False)),
        "previews": previews,
        "policy": "explicit-index visual review only; source checkpoint is not mutated",
        "status": "review_required",
    }
    report_path = job / "blender" / "reports" / f"{runtime_stem}_component_review.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _principal_axis(points: List[Vector]) -> Tuple[Vector, Vector, float, float]:
    if len(points) < 3:
        raise RuntimeError("Weapon isolation requires at least three reviewed vertices.")
    centroid = sum(points, Vector()) / len(points)
    covariance = Matrix(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
    for point in points:
        delta = point - centroid
        covariance[0][0] += delta.x * delta.x
        covariance[0][1] += delta.x * delta.y
        covariance[0][2] += delta.x * delta.z
        covariance[1][0] += delta.y * delta.x
        covariance[1][1] += delta.y * delta.y
        covariance[1][2] += delta.y * delta.z
        covariance[2][0] += delta.z * delta.x
        covariance[2][1] += delta.z * delta.y
        covariance[2][2] += delta.z * delta.z
    axis = Vector((1.0, 0.0, -1.0)).normalized()
    for _ in range(32):
        candidate = covariance @ axis
        if candidate.length <= 1e-9:
            break
        axis = candidate.normalized()
    if axis.z > 0.0:
        axis.negate()
    projections = [(point - centroid).dot(axis) for point in points]
    return centroid, axis, min(projections), max(projections)


def isolate_humanoid_weapon(req: Dict[str, Any]) -> Dict[str, Any]:
    """Join reviewed loose parts, preserve the body, and shoulder the recovered weapon."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    prefix = safe_name(str(payload["component_prefix"]))
    requested = sorted({int(value) for value in payload.get("weapon_component_indices", [])})
    if not requested:
        raise RuntimeError("Humanoid weapon isolation requires explicit reviewed component indices.")
    if len(requested) > 128:
        raise RuntimeError("Humanoid weapon isolation is bounded to 128 component indices.")
    stock_x_fraction = float(payload.get("stock_x_fraction", 0.03))
    stock_y_offset_fraction = float(payload.get("stock_y_front_offset_fraction", -0.18))
    stock_z_fraction = float(payload.get("stock_z_fraction", 0.64))
    aim_down_degrees = float(payload.get("aim_down_degrees", 2.0))
    stock_indices = sorted({int(value) for value in payload.get("stock_component_indices", [])})
    stock_link_indices = sorted({int(value) for value in payload.get("stock_link_component_indices", [])})
    stock_advance = float(payload.get("stock_advance_m", 1.25))
    stock_link_advance = float(payload.get("stock_link_advance_m", 0.55))
    if not (-0.5 <= stock_x_fraction <= 0.5):
        raise ValueError("Weapon stock x fraction must be between -0.5 and 0.5.")
    if not (-0.5 <= stock_y_offset_fraction <= 1.0):
        raise ValueError("Weapon stock front offset fraction must be between -0.5 and 1.")
    if not (0.35 <= stock_z_fraction <= 0.85):
        raise ValueError("Weapon stock z fraction must be between 0.35 and 0.85.")
    if not (-20.0 <= aim_down_degrees <= 20.0):
        raise ValueError("Weapon aim-down angle must remain between -20 and 20 degrees.")
    if set(stock_indices) - set(requested) or set(stock_link_indices) - set(requested):
        raise ValueError("Weapon stock and stock-link indices must be subsets of the reviewed weapon selection.")
    if set(stock_indices) & set(stock_link_indices):
        raise ValueError("Weapon stock and stock-link component groups must not overlap.")
    if not (0.0 <= stock_advance <= 2.0 and 0.0 <= stock_link_advance <= 2.0):
        raise ValueError("Weapon stock assembly advances must remain between 0 and 2 metres.")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    by_name = {obj.name: obj for obj in working}
    weapon_names = [f"{prefix}_{index:03d}" for index in requested]
    missing = [name for name in weapon_names if name not in by_name]
    if missing:
        raise RuntimeError(f"Reviewed weapon components were not found: {missing}")
    weapon_parts = [by_name[name] for name in weapon_names]
    body_parts = [obj for obj in working if obj.name not in set(weapon_names)]
    if not body_parts:
        raise RuntimeError("Weapon isolation cannot consume every humanoid mesh component.")

    initial_points = [obj.matrix_world @ vertex.co for obj in weapon_parts for vertex in obj.data.vertices]
    _, initial_axis, _, _ = _principal_axis(initial_points)

    def advance_components(indices: List[int], distance: float) -> None:
        for index in indices:
            obj = by_name[f"{prefix}_{index:03d}"]
            inverse = obj.matrix_world.inverted()
            translation = initial_axis * distance
            for vertex in obj.data.vertices:
                vertex.co = inverse @ ((obj.matrix_world @ vertex.co) + translation)
            obj.data.update()

    advance_components(stock_indices, stock_advance)
    advance_components(stock_link_indices, stock_link_advance)
    body = _join_mesh_objects(body_parts, str(payload.get("body_object_name") or "humanoid_body"))
    weapon = _join_mesh_objects(weapon_parts, str(payload.get("weapon_object_name") or "humanoid_weapon"))
    body["hoi4_humanoid_body"] = True
    weapon["hoi4_humanoid_weapon"] = True
    weapon["hoi4_weapon_binding_bone"] = "weapon"
    body_minimum, body_maximum = world_bounds([body])
    body_dimensions = body_maximum - body_minimum
    body_center = (body_minimum + body_maximum) * 0.5
    points = [weapon.matrix_world @ vertex.co for vertex in weapon.data.vertices]
    centroid, source_axis, stock_projection, muzzle_projection = _principal_axis(points)
    source_stock = centroid + source_axis * stock_projection
    radians = math.radians(aim_down_degrees)
    target_axis = Vector((0.0, -math.cos(radians), -math.sin(radians))).normalized()
    rotation = source_axis.rotation_difference(target_axis)
    target_stock = Vector(
        (
            body_center.x + body_dimensions.x * stock_x_fraction,
            body_minimum.y - body_dimensions.y * stock_y_offset_fraction,
            body_minimum.z + body_dimensions.z * stock_z_fraction,
        )
    )
    inverse_weapon_matrix = weapon.matrix_world.inverted()
    for vertex in weapon.data.vertices:
        world = weapon.matrix_world @ vertex.co
        transformed = rotation @ (world - source_stock) + target_stock
        vertex.co = inverse_weapon_matrix @ transformed
    weapon.data.update()
    bpy.context.view_layer.update()
    weapon_minimum, weapon_maximum = world_bounds([weapon])
    save_blend(checkpoint)

    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "component_prefix": prefix,
        "weapon_component_indices": requested,
        "weapon_component_names": weapon_names,
        "stock_component_indices": stock_indices,
        "stock_link_component_indices": stock_link_indices,
        "stock_advance_m": stock_advance,
        "stock_link_advance_m": stock_link_advance,
        "body_object": body.name,
        "weapon_object": weapon.name,
        "weapon_binding_bone": "weapon",
        "source_principal_axis_stock_to_muzzle": list(source_axis),
        "source_axis_extent": [stock_projection, muzzle_projection],
        "source_stock": list(source_stock),
        "target_stock": list(target_stock),
        "target_axis": list(target_axis),
        "aim_down_degrees": aim_down_degrees,
        "body_bounds_min": list(body_minimum),
        "body_bounds_max": list(body_maximum),
        "weapon_bounds_min": list(weapon_minimum),
        "weapon_bounds_max": list(weapon_maximum),
        "policy": "explicit visually reviewed loose-component selection; rigid recovered-weapon geometry; no generated replacement",
        "status": "pass",
    }
    report_path = job / "blender" / "reports" / "humanoid_weapon_isolation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _finite_vector3(payload: Dict[str, Any], key: str, default: Tuple[float, float, float]) -> Vector:
    raw = payload.get(key, default)
    if not isinstance(raw, (list, tuple)) or len(raw) != 3:
        raise ValueError(f"{key} must contain exactly three numeric values.")
    try:
        value = Vector(tuple(float(item) for item in raw))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must contain exactly three numeric values.") from exc
    if not all(math.isfinite(component) for component in value):
        raise ValueError(f"{key} must contain only finite values.")
    return value


def _action_retention_snapshot() -> Dict[str, Any]:
    actions: Dict[str, Any] = {}
    for action in bpy.data.actions:
        curves = []
        for fcurve, _ in action_fcurves(action):
            curves.append(
                {
                    "data_path": str(fcurve.data_path),
                    "array_index": int(fcurve.array_index),
                    "keyframes": [
                        {
                            "co": [float(point.co[0]), float(point.co[1])],
                            "interpolation": str(point.interpolation),
                        }
                        for point in fcurve.keyframe_points
                    ],
                }
            )
        payload = json.dumps(sorted(curves, key=lambda item: (item["data_path"], item["array_index"])), sort_keys=True)
        actions[action.name] = {
            "frame_range": [float(action.frame_range[0]), float(action.frame_range[1])],
            "fcurve_count": len(curves),
            "keyframe_count": sum(len(item["keyframes"]) for item in curves),
            "curve_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest().upper(),
        }
    return actions


def _bone_retention_snapshot(rig: bpy.types.Object) -> Dict[str, Any]:
    return {
        bone.name: {
            "parent": bone.parent.name if bone.parent else None,
            "use_deform": bool(bone.use_deform),
            "head_local": vector_record(bone.head_local),
            "tail_local": vector_record(bone.tail_local),
            "matrix_local": [[float(value) for value in row] for row in bone.matrix_local],
        }
        for bone in rig.data.bones
    }


def _matrix_record(matrix: Matrix) -> List[List[float]]:
    return [[float(value) for value in row] for row in matrix]


def _matrix_max_delta(left: Matrix, right: Matrix) -> float:
    return max(abs(float(left[row][column] - right[row][column])) for row in range(4) for column in range(4))


def attach_rigid_weapon_from_checkpoint(req: Dict[str, Any]) -> Dict[str, Any]:
    """Append one named mesh and rigidly bone-parent it without changing target actions."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    source = within(job, str(payload["source_blend_rel"]))
    target = within(job, str(payload["target_blend_rel"]))
    output = within(job, str(payload["output_blend_rel"]), allow_missing=True)
    for field, path in (
        ("source_blend_rel", source),
        ("target_blend_rel", target),
        ("output_blend_rel", output),
    ):
        if path.suffix.casefold() != ".blend":
            raise ValueError(f"{field} must name a job-root-bounded .blend checkpoint.")
    if source == target or output in {source, target}:
        raise ValueError("Source, target, and output checkpoints must be three distinct .blend paths.")

    source_object_name = explicit_safe_name(payload.get("source_object_name"), "source_object_name")
    target_object_name = explicit_safe_name(payload.get("target_object_name"), "target_object_name")
    armature_name = explicit_safe_name(payload.get("target_armature_name"), "target_armature_name")
    parent_bone_name = explicit_safe_name(payload.get("parent_bone_name"), "parent_bone_name")
    create_bone_raw = str(payload.get("create_weapon_bone_name") or "")
    create_bone_name = explicit_safe_name(create_bone_raw, "create_weapon_bone_name") if create_bone_raw else ""
    collision_policy = str(payload.get("collision_policy", "reject"))
    if collision_policy not in {"reject", "replace_prior_attachment"}:
        raise ValueError("collision_policy must be reject or replace_prior_attachment.")
    translation = _finite_vector3(payload, "translation", (0.0, 0.0, 0.0))
    rotation_degrees = _finite_vector3(payload, "rotation_euler_degrees", (0.0, 0.0, 0.0))
    scale = _finite_vector3(payload, "scale", (1.0, 1.0, 1.0))
    if any(abs(value) > 10000.0 for value in translation):
        raise ValueError("translation components must remain within 10000 Blender units.")
    if any(abs(value) > 36000.0 for value in rotation_degrees):
        raise ValueError("rotation_euler_degrees components must remain within 36000 degrees.")
    if any(value <= 0.0 or value > 1000.0 for value in scale):
        raise ValueError("scale components must be finite, positive, and at most 1000.")
    action_name_raw = str(payload.get("action_name") or "")
    if action_name_raw and not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.|:-]{0,255}", action_name_raw):
        raise ValueError("action_name contains unsafe characters.")
    action_name = action_name_raw
    render_views = [str(value) for value in payload.get("render_views", ["three_quarter"])]
    allowed_views = {"front", "rear", "left", "right", "top", "underside", "three_quarter"}
    if not render_views or any(view not in allowed_views for view in render_views):
        raise ValueError(f"render_views must be selected from {sorted(allowed_views)}.")

    # Inspect the source checkpoint independently before any append. Linked data,
    # parents, constraints, animation, and object-referencing modifiers would turn
    # the single-object append into an implicit dependency import and are rejected.
    bpy.ops.wm.open_mainfile(filepath=str(source))
    if bpy.data.libraries:
        raise RuntimeError("Source weapon checkpoint contains linked Blender libraries.")
    source_matches = [obj for obj in bpy.data.objects if obj.name == source_object_name]
    if len(source_matches) != 1:
        raise RuntimeError(
            f"Source checkpoint must contain exactly one object named {source_object_name!r}; found {len(source_matches)}."
        )
    source_object = source_matches[0]
    if source_object.type != "MESH":
        raise RuntimeError(f"Source object {source_object_name!r} is {source_object.type}, not MESH.")
    if source_object.library is not None or source_object.data.library is not None:
        raise RuntimeError("Source weapon object or mesh data is linked from a Blender library.")
    if source_object.parent is not None or source_object.children:
        raise RuntimeError("Source weapon object must not have a parent or child object dependency.")
    if source_object.constraints:
        raise RuntimeError("Source weapon object must not carry object constraints.")
    if source_object.animation_data is not None or getattr(source_object.data, "shape_keys", None) is not None:
        raise RuntimeError("Source weapon object must not carry animation data or shape keys.")
    referenced_modifiers = []
    for modifier in source_object.modifiers:
        for attribute in ("object", "target"):
            dependency = getattr(modifier, attribute, None)
            if dependency is not None:
                referenced_modifiers.append({"modifier": modifier.name, "attribute": attribute, "object": dependency.name})
    if referenced_modifiers:
        raise RuntimeError("Source weapon modifiers reference nested objects: " + json.dumps(referenced_modifiers, sort_keys=True))
    source_geometry = {
        "vertices": len(source_object.data.vertices),
        "polygons": len(source_object.data.polygons),
        "materials": [material.name for material in source_object.data.materials if material is not None],
        "bounds": bounds_record([source_object]),
    }

    bpy.ops.wm.open_mainfile(filepath=str(target))
    if bpy.data.libraries:
        raise RuntimeError("Target rig checkpoint contains linked Blender libraries.")
    target_rigs = [obj for obj in bpy.data.objects if obj.name == armature_name]
    if len(target_rigs) != 1 or target_rigs[0].type != "ARMATURE":
        raise RuntimeError(f"Target checkpoint must contain exactly one ARMATURE named {armature_name!r}.")
    rig = target_rigs[0]
    if rig.library is not None or rig.data.library is not None:
        raise RuntimeError("Target armature or armature data is linked from a Blender library.")
    if parent_bone_name not in rig.data.bones:
        raise RuntimeError(f"Target armature does not contain the explicit parent bone {parent_bone_name!r}.")
    existing = bpy.data.objects.get(target_object_name)
    replaced_object = None
    if existing is not None:
        if collision_policy != "replace_prior_attachment":
            raise RuntimeError(f"Target object name already exists: {target_object_name!r}.")
        if existing.type != "MESH" or not bool(existing.get("hoi4_rigid_weapon_attachment", False)):
            raise RuntimeError("replace_prior_attachment may replace only a mesh previously created by this operation.")
        replaced_object = existing.name
        bpy.data.objects.remove(existing, do_unlink=True)

    actions_before = _action_retention_snapshot()
    bones_before = _bone_retention_snapshot(rig)
    active_action_before = rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None
    target_object_count_before_append = len(bpy.data.objects)
    with bpy.data.libraries.load(str(source), link=False) as (data_from, data_to):
        matches = [name for name in data_from.objects if name == source_object_name]
        if len(matches) != 1:
            raise RuntimeError(f"Append source contains {len(matches)} matches for {source_object_name!r}.")
        data_to.objects = [source_object_name]
    appended = [obj for obj in data_to.objects if obj is not None]
    if len(appended) != 1 or len(bpy.data.objects) != target_object_count_before_append + 1:
        raise RuntimeError("Rigid weapon attachment must append exactly one Blender object.")
    weapon = appended[0]
    if weapon.type != "MESH" or weapon.library is not None or weapon.data.library is not None:
        raise RuntimeError("Appended weapon must be one local MESH object with local mesh data.")
    if weapon.name in bpy.context.scene.objects:
        raise RuntimeError("Appended weapon unexpectedly collided with a linked scene object.")
    weapon.name = target_object_name
    weapon.data.name = f"{target_object_name}_mesh"
    collection = rig.users_collection[0] if rig.users_collection else bpy.context.scene.collection
    collection.objects.link(weapon)
    weapon["hoi4_working"] = True
    weapon["hoi4_rigid_weapon_attachment"] = True
    weapon["hoi4_weapon_source_object"] = source_object_name
    weapon["hoi4_weapon_parent_armature"] = armature_name

    created_bone = False
    attachment_bone_name = parent_bone_name
    if create_bone_name:
        existing_bone = rig.data.bones.get(create_bone_name)
        if existing_bone is not None:
            if collision_policy != "replace_prior_attachment" or not bool(existing_bone.get("hoi4_rigid_weapon_bone", False)):
                raise RuntimeError(f"Requested weapon bone already exists: {create_bone_name!r}.")
            if existing_bone.parent is None or existing_bone.parent.name != parent_bone_name:
                raise RuntimeError("Existing prior attachment bone is not parented to the requested hand bone.")
        else:
            bpy.context.view_layer.objects.active = rig
            rig.select_set(True)
            bpy.ops.object.mode_set(mode="EDIT")
            parent_edit = rig.data.edit_bones.get(parent_bone_name)
            if parent_edit is None:
                bpy.ops.object.mode_set(mode="OBJECT")
                raise RuntimeError(f"Unable to edit explicit parent bone {parent_bone_name!r}.")
            edit_bone = rig.data.edit_bones.new(create_bone_name)
            edit_bone.parent = parent_edit
            edit_bone.use_connect = False
            edit_bone.head = parent_edit.tail
            direction = parent_edit.tail - parent_edit.head
            if direction.length <= 1e-6:
                direction = Vector((0.0, -1.0, 0.0))
            edit_bone.tail = edit_bone.head + direction.normalized() * max(float(parent_edit.length) * 0.5, 0.05)
            edit_bone.use_deform = True
            bpy.ops.object.mode_set(mode="OBJECT")
            rig.data.bones[create_bone_name]["hoi4_rigid_weapon_bone"] = True
            rig.data.bones[create_bone_name]["hoi4_parent_hand_bone"] = parent_bone_name
            created_bone = True
        attachment_bone_name = create_bone_name

    weapon.parent = rig
    weapon.parent_type = "BONE"
    weapon.parent_bone = attachment_bone_name
    weapon.matrix_parent_inverse = Matrix.Identity(4)
    weapon.location = translation
    weapon.rotation_mode = "XYZ"
    weapon.rotation_euler = Euler(tuple(math.radians(value) for value in rotation_degrees), "XYZ")
    weapon.scale = scale
    weapon["hoi4_weapon_parent_bone"] = attachment_bone_name
    bpy.context.view_layer.update()

    actions_after = _action_retention_snapshot()
    if actions_after != actions_before:
        raise RuntimeError("Rigid weapon attachment changed target action data.")
    bones_after = _bone_retention_snapshot(rig)
    retained_bones_after = {name: value for name, value in bones_after.items() if name != create_bone_name or name in bones_before}
    if retained_bones_after != bones_before:
        raise RuntimeError("Rigid weapon attachment changed existing target rig bone data.")

    sample_records = []
    preview_paths: List[str] = []
    relative_reference: Optional[Matrix] = None
    rigid_edge_reference: Optional[List[float]] = None
    max_relative_delta = 0.0
    max_edge_delta = 0.0
    sample_frames: List[int] = []
    if action_name:
        action = bpy.data.actions.get(action_name)
        if action is None:
            raise RuntimeError(f"Requested proof action was not found: {action_name!r}.")
        rig.animation_data_create()
        rig.animation_data.action = action
        start, end = action.frame_range
        sample_frames = sorted({int(math.floor(start)), int(round((float(start) + float(end)) * 0.5)), int(math.ceil(end))})
        if len(sample_frames) != 3:
            raise RuntimeError("Action proof requires distinct start, middle, and end frames.")
        if len(weapon.data.vertices) < 2:
            raise RuntimeError("Rigid proof requires at least two weapon vertices.")
        vertex_indices = sorted({0, len(weapon.data.vertices) // 2, len(weapon.data.vertices) - 1})
        for label, frame in zip(("start", "middle", "end"), sample_frames):
            bpy.context.scene.frame_set(frame)
            bpy.context.view_layer.update()
            pose_bone = rig.pose.bones.get(attachment_bone_name)
            if pose_bone is None:
                raise RuntimeError(f"Attachment pose bone disappeared: {attachment_bone_name!r}.")
            bone_world = rig.matrix_world @ pose_bone.matrix
            relative = bone_world.inverted_safe() @ weapon.matrix_world
            if relative_reference is None:
                relative_reference = relative.copy()
            relative_delta = _matrix_max_delta(relative_reference, relative)
            max_relative_delta = max(max_relative_delta, relative_delta)
            points = [weapon.matrix_world @ weapon.data.vertices[index].co for index in vertex_indices]
            edge_lengths = [float((points[index + 1] - points[index]).length) for index in range(len(points) - 1)]
            if rigid_edge_reference is None:
                rigid_edge_reference = edge_lengths
            edge_delta = max(abs(left - right) for left, right in zip(rigid_edge_reference, edge_lengths)) if edge_lengths else 0.0
            max_edge_delta = max(max_edge_delta, edge_delta)
            stem = safe_name(f"{target_object_name}_{action_name}_{label}_frame_{frame}")
            preview_paths.extend(render_previews(job, stem, render_views))
            sample_records.append(
                {
                    "phase": label,
                    "frame": frame,
                    "world_transform": object_transform_record(weapon),
                    "world_bounds": bounds_record([weapon]),
                    "bone_world_matrix": _matrix_record(bone_world),
                    "weapon_relative_to_bone_matrix": _matrix_record(relative),
                    "relative_matrix_delta_from_start": relative_delta,
                    "rigid_edge_lengths": edge_lengths,
                    "rigid_edge_delta_from_start": edge_delta,
                }
            )
        if max_relative_delta > 1e-5 or max_edge_delta > 1e-5:
            raise RuntimeError(
                "Weapon failed rigid action sampling: "
                + json.dumps({"max_relative_matrix_delta": max_relative_delta, "max_edge_length_delta": max_edge_delta}, sort_keys=True)
            )
    if rig.animation_data:
        rig.animation_data.action = bpy.data.actions.get(active_action_before) if active_action_before else None
    bpy.context.scene.frame_set(bpy.context.scene.frame_start)
    bpy.context.view_layer.update()

    output.parent.mkdir(parents=True, exist_ok=True)
    save_blend(output)
    report = {
        "operation": "attach_rigid_weapon_from_checkpoint",
        "source_blend": str(source.relative_to(job)).replace("\\", "/"),
        "target_blend": str(target.relative_to(job)).replace("\\", "/"),
        "output_checkpoint": str(output.relative_to(job)).replace("\\", "/"),
        "hashes": {
            "source_blend_sha256": file_sha256(source),
            "target_blend_sha256": file_sha256(target),
            "output_blend_sha256": file_sha256(output),
        },
        "source_object": source_object_name,
        "target_object": target_object_name,
        "source_geometry": source_geometry,
        "collision_policy": collision_policy,
        "replaced_object": replaced_object,
        "armature": armature_name,
        "parent_hand_or_weapon_bone": parent_bone_name,
        "attachment_bone": attachment_bone_name,
        "created_weapon_bone": created_bone,
        "alignment": {
            "translation": vector_record(translation),
            "rotation_euler_degrees": vector_record(rotation_degrees),
            "scale": vector_record(scale),
        },
        "weapon_world_transform": object_transform_record(weapon),
        "weapon_world_bounds": bounds_record([weapon]),
        "retention_metrics": {
            "actions_before": actions_before,
            "actions_after": actions_after,
            "actions_retained_exactly": actions_after == actions_before,
            "existing_bones_before": len(bones_before),
            "existing_bones_after": len(retained_bones_after),
            "existing_bones_retained_exactly": retained_bones_after == bones_before,
            "bone_count_after": len(bones_after),
            "new_bone_count": len(bones_after) - len(bones_before),
        },
        "action_proof": {
            "action": action_name or None,
            "sample_frames": sample_frames,
            "samples": sample_records,
            "previews": sorted(set(preview_paths)),
            "max_relative_matrix_delta": max_relative_delta,
            "max_rigid_edge_length_delta": max_edge_delta,
            "status": "pass" if action_name else "not_requested",
        },
        "animation_policy": "no body or weapon keys authored; target action datablocks retained byte-for-byte at the fcurve/value level",
        "status": "pass",
    }
    report_path = job / "blender" / "reports" / f"{target_object_name}_rigid_attachment.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report"] = str(report_path.relative_to(job)).replace("\\", "/")
    return report


def calibrate_creature_scale(req: Dict[str, Any]) -> Dict[str, Any]:
    """Scale the complete creature around its ground centre so the rider is infantry-sized."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    rider_names = [str(name) for name in payload.get("rider_component_names", [])]
    if not rider_names:
        raise RuntimeError("Creature scale calibration requires rider component names.")
    target_runtime = float(payload["target_rider_runtime_height_m"])
    entity_scale = float(payload.get("runtime_entity_scale", 0.8))
    if target_runtime <= 0.0 or entity_scale <= 0.0:
        raise RuntimeError("Creature scale calibration requires positive target and entity scale.")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    by_name = {obj.name: obj for obj in working}
    missing = sorted(set(rider_names) - set(by_name))
    if missing:
        raise RuntimeError(f"Rider component names were not found: {missing}")
    rider_objects = [by_name[name] for name in rider_names]
    rider_minimum, rider_maximum = world_bounds(rider_objects)
    rider_source_height = float(rider_maximum.z - rider_minimum.z)
    if rider_source_height <= 0.0:
        raise RuntimeError("Rider component height is not positive.")
    target_source_height = target_runtime / entity_scale
    scale_factor = target_source_height / rider_source_height
    all_minimum, all_maximum = world_bounds(working)
    pivot = Vector(((all_minimum.x + all_maximum.x) * 0.5, (all_minimum.y + all_maximum.y) * 0.5, all_minimum.z))
    scale_matrix = Matrix.Translation(pivot) @ Matrix.Scale(scale_factor, 4) @ Matrix.Translation(-pivot)
    for obj in working:
        obj.matrix_world = scale_matrix @ obj.matrix_world
    bpy.context.view_layer.update()
    for obj in working:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.update()
    rider_minimum_after, rider_maximum_after = world_bounds(rider_objects)
    final_minimum, final_maximum = world_bounds(working)
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "rider_components": rider_names,
        "rider_source_height_before_m": rider_source_height,
        "target_rider_source_height_m": target_source_height,
        "target_rider_runtime_height_m": target_runtime,
        "runtime_entity_scale": entity_scale,
        "uniform_scale_factor": scale_factor,
        "pivot": list(pivot),
        "rider_source_height_after_m": float(rider_maximum_after.z - rider_minimum_after.z),
        "rider_runtime_height_after_m": float(rider_maximum_after.z - rider_minimum_after.z) * entity_scale,
        "final_bounds_min": list(final_minimum),
        "final_bounds_max": list(final_maximum),
        "final_dimensions": list(final_maximum - final_minimum),
        "policy": "rider-calibrated-uniform-creature-scale-around-ground-centre",
        "status": "pass" if abs(float(rider_maximum_after.z - rider_minimum_after.z) * entity_scale - target_runtime) <= 0.01 else "fail",
    }
    report_path = job / "blender" / "reports" / "creature_scale.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError("Rider runtime height did not meet the requested infantry calibration.")
    return report


def _creature_bone_name_for_component(
    center: Vector,
    dimensions: Vector,
    bounds_minimum: Vector,
    bounds_maximum: Vector,
    rider_names: set[str],
    object_name: str,
    total_minimum: Vector,
    total_maximum: Vector,
) -> str:
    semantic_object_names = {
        "body",
        "head",
        "trunk_01",
        "trunk_02",
        "tail",
        "howdah",
        "front_left_upper",
        "front_left_lower",
        "front_right_upper",
        "front_right_lower",
        "rear_left_upper",
        "rear_left_lower",
        "rear_right_upper",
        "rear_right_lower",
    }
    if object_name in semantic_object_names:
        return object_name
    if object_name == "elephant_body_region":
        return "body"
    total_dimensions = total_maximum - total_minimum
    total_height = max(total_dimensions.z, 1e-6)
    total_length = max(total_dimensions.y, 1e-6)
    centre = (total_minimum + total_maximum) * 0.5
    if object_name in rider_names or center.z > total_minimum.z + total_height * 0.86:
        return "rider"
    if center.z > total_minimum.z + total_height * 0.72 and dimensions.z < total_height * 0.35:
        return "howdah"
    if center.y < centre.y - total_length * 0.23:
        if center.z > total_minimum.z + total_height * 0.45:
            return "head"
        return "trunk_02"
    if center.y > centre.y + total_length * 0.25:
        return "tail"
    if center.z < total_minimum.z + total_height * 0.45 and dimensions.z < total_height * 0.55:
        side = "left" if center.x < centre.x else "right"
        end = "front" if center.y < centre.y else "rear"
        return f"{end}_{side}_lower"
    return "body"


def _creature_bone_name_for_vertex(
    world_position: Vector,
    minimum: Vector,
    maximum: Vector,
    rider_names: set[str],
    object_name: str,
) -> str:
    """Assign one deterministic semantic bone to a creature vertex.

    The provider is a fused shell, so object-level rigid binding would leave
    every leg, trunk, and tail action inert.  This spatial rigid weighting is
    intentionally conservative: each vertex receives one full influence, with
    body fallback at ambiguous seams.  It is a real skeletal rig, not a
    transform-only animation substitute.
    """

    if object_name in rider_names:
        return "rider"
    dimensions = maximum - minimum
    centre = (minimum + maximum) * 0.5
    height = max(float(dimensions.z), 1e-6)
    length = max(float(dimensions.y), 1e-6)
    width = max(float(dimensions.x), 1e-6)
    z_fraction = (world_position.z - minimum.z) / height
    y_fraction = (world_position.y - centre.y) / length
    x_fraction = (world_position.x - centre.x) / width
    # Highest forward geometry is the head and trunk.  The trunk is divided
    # into two bones to give attack/impact/deploy actions visible articulation.
    if y_fraction < -0.23:
        if z_fraction > 0.47:
            return "head"
        return "trunk_02"
    if y_fraction < -0.10 and z_fraction > 0.44:
        return "trunk_01"
    # The rearward elevated geometry is the tail/harness area.
    if y_fraction > 0.30 and z_fraction > 0.35:
        return "tail"
    if z_fraction > 0.70 and abs(x_fraction) < 0.28:
        return "howdah"
    # Legs are split into four quadrants, then upper/lower sections.  Use the
    # wider body fallback for belly vertices so no thin sliver is assigned to a
    # leg bone by accident.
    if z_fraction < 0.43 and abs(x_fraction) > 0.16:
        side = "left" if x_fraction < 0.0 else "right"
        end = "front" if y_fraction < 0.0 else "rear"
        if z_fraction < 0.22:
            return f"{end}_{side}_lower"
        return f"{end}_{side}_upper"
    return "body"


WINGED_BIPED_BONE_NAMES = (
    "root",
    "pelvis",
    "spine",
    "neck",
    "head",
    "upper_arm_left",
    "lower_arm_left",
    "hand_left",
    "upper_arm_right",
    "lower_arm_right",
    "hand_right",
    "upper_leg_left",
    "lower_leg_left",
    "foot_left",
    "upper_leg_right",
    "lower_leg_right",
    "foot_right",
    "wing_root_left",
    "wing_mid_left",
    "wing_tip_left",
    "wing_root_right",
    "wing_mid_right",
    "wing_tip_right",
)


def _winged_biped_bone_name_for_vertex(
    world_position: Vector,
    minimum: Vector,
    maximum: Vector,
    object_name: str,
) -> str:
    """Assign one full semantic influence to a winged/digitigrade biped vertex."""

    if object_name in WINGED_BIPED_BONE_NAMES:
        return object_name
    dimensions = maximum - minimum
    centre = (minimum + maximum) * 0.5
    height = max(float(dimensions.z), 1e-6)
    length = max(float(dimensions.y), 1e-6)
    width = max(float(dimensions.x), 1e-6)
    z_fraction = (world_position.z - minimum.z) / height
    y_fraction = (world_position.y - centre.y) / length
    x_fraction = (world_position.x - centre.x) / width
    side = "left" if x_fraction < 0.0 else "right"
    abs_x = abs(x_fraction)

    # The reference and the HOI4 unit axes use -Y as forward. Rearward,
    # elevated geometry is therefore the folded wing plane, not a tail.
    if abs_x > 0.25 and y_fraction > 0.06 and z_fraction > 0.48:
        if abs_x > 0.58:
            return f"wing_tip_{side}"
        if abs_x > 0.38:
            return f"wing_mid_{side}"
        return f"wing_root_{side}"
    if z_fraction > 0.82:
        return "head"
    if z_fraction > 0.67 and y_fraction < 0.04:
        return "neck"
    if 0.28 < z_fraction < 0.72 and 0.13 < abs_x < 0.58:
        return f"upper_arm_{side}" if z_fraction > 0.48 else f"lower_arm_{side}"
    if z_fraction < 0.13 and abs_x > 0.08:
        return f"foot_{side}"
    if z_fraction < 0.48 and abs_x > 0.09:
        return f"upper_leg_{side}" if z_fraction > 0.22 else f"lower_leg_{side}"
    if z_fraction > 0.45:
        return "spine"
    return "pelvis"


def author_winged_biped_rig(req: Dict[str, Any]) -> Dict[str, Any]:
    """Create a custom rigid-semantic rig for a winged/digitigrade biped."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    rig_name = safe_name(str(payload.get("rig_name") or "winged_biped_armature"))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    if not working:
        raise RuntimeError("Winged biped rigging found no working meshes.")
    for rig in armatures():
        bpy.data.objects.remove(rig, do_unlink=True)
    minimum, maximum = world_bounds(working)
    dimensions = maximum - minimum
    centre = (minimum + maximum) * 0.5
    height = max(float(dimensions.z), 1e-6)
    length = max(float(dimensions.y), 1e-6)
    width = max(float(dimensions.x), 1e-6)
    z0 = minimum.z
    y_front = centre.y - length * 0.06
    y_rear = centre.y + length * 0.10
    armature_data = bpy.data.armatures.new(rig_name)
    rig = bpy.data.objects.new(rig_name, armature_data)
    _working_collection().objects.link(rig)
    rig["hoi4_working"] = True
    rig["hoi4_custom_creature_rig"] = True
    rig["hoi4_creature_rig_family"] = "winged_biped"
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bones: Dict[str, bpy.types.EditBone] = {}

    def add_bone(name: str, head: Vector, tail: Vector, parent: str | None = None) -> None:
        bone = armature_data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        if parent:
            bone.parent = bones[parent]
            bone.use_connect = False
        bones[name] = bone

    add_bone("root", Vector((centre.x, centre.y, z0)), Vector((centre.x, centre.y, z0 + height * 0.12)))
    add_bone("pelvis", Vector((centre.x, centre.y, z0 + height * 0.30)), Vector((centre.x, centre.y, z0 + height * 0.46)), "root")
    add_bone("spine", Vector((centre.x, centre.y, z0 + height * 0.44)), Vector((centre.x, centre.y, z0 + height * 0.67)), "pelvis")
    add_bone("neck", Vector((centre.x, y_front, z0 + height * 0.64)), Vector((centre.x, y_front, z0 + height * 0.76)), "spine")
    add_bone("head", Vector((centre.x, y_front, z0 + height * 0.74)), Vector((centre.x, y_front - length * 0.10, z0 + height * 0.84)), "neck")
    for side, sign in (("left", -1.0), ("right", 1.0)):
        shoulder = Vector((centre.x + sign * width * 0.20, centre.y - length * 0.01, z0 + height * 0.64))
        elbow = Vector((centre.x + sign * width * 0.34, centre.y - length * 0.04, z0 + height * 0.46))
        wrist = Vector((centre.x + sign * width * 0.40, centre.y - length * 0.07, z0 + height * 0.28))
        hand = Vector((centre.x + sign * width * 0.41, centre.y - length * 0.11, z0 + height * 0.20))
        add_bone(f"upper_arm_{side}", shoulder, elbow, "spine")
        add_bone(f"lower_arm_{side}", elbow, wrist, f"upper_arm_{side}")
        add_bone(f"hand_{side}", wrist, hand, f"lower_arm_{side}")
        hip = Vector((centre.x + sign * width * 0.13, centre.y + length * 0.01, z0 + height * 0.43))
        knee = Vector((centre.x + sign * width * 0.16, centre.y - length * 0.02, z0 + height * 0.23))
        ankle = Vector((centre.x + sign * width * 0.16, centre.y - length * 0.08, z0 + height * 0.08))
        foot = Vector((centre.x + sign * width * 0.16, centre.y - length * 0.16, z0 + height * 0.04))
        add_bone(f"upper_leg_{side}", hip, knee, "pelvis")
        add_bone(f"lower_leg_{side}", knee, ankle, f"upper_leg_{side}")
        add_bone(f"foot_{side}", ankle, foot, f"lower_leg_{side}")
        wing_root = Vector((centre.x + sign * width * 0.17, y_rear, z0 + height * 0.63))
        wing_mid = Vector((centre.x + sign * width * 0.40, y_rear + length * 0.03, z0 + height * 0.73))
        wing_tip = Vector((centre.x + sign * width * 0.68, y_rear + length * 0.06, z0 + height * 0.80))
        add_bone(f"wing_root_{side}", wing_root, wing_mid, "spine")
        add_bone(f"wing_mid_{side}", wing_mid, wing_tip, f"wing_root_{side}")
        add_bone(f"wing_tip_{side}", wing_tip, wing_tip + Vector((sign * width * 0.12, length * 0.02, height * 0.02)), f"wing_mid_{side}")
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.show_in_front = True
    armature_data.display_type = "BBONE"
    records = []
    for obj in working:
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        groups = {bone.name: obj.vertex_groups.new(name=bone.name) for bone in armature_data.bones}
        counts: Dict[str, int] = {name: 0 for name in groups}
        for vertex in obj.data.vertices:
            bone_name = _winged_biped_bone_name_for_vertex(
                obj.matrix_world @ vertex.co,
                minimum,
                maximum,
                obj.name,
            )
            if bone_name not in groups:
                bone_name = "spine"
            groups[bone_name].add([vertex.index], 1.0, "REPLACE")
            counts[bone_name] += 1
        modifier = next((item for item in obj.modifiers if item.type == "ARMATURE"), None)
        if modifier is None:
            modifier = obj.modifiers.new("HOI4_CREATURE_ARMATURE", "ARMATURE")
        modifier.object = rig
        world_matrix = obj.matrix_world.copy()
        obj.parent = rig
        obj.parent_type = "OBJECT"
        obj.matrix_world = world_matrix
        records.append(
            {
                "object": obj.name,
                "bone": "spatial_semantic_weights",
                "vertices": len(obj.data.vertices),
                "vertex_group_counts": {name: count for name, count in counts.items() if count},
            }
        )
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "armature": rig.name,
        "bones": [bone.name for bone in armature_data.bones],
        "component_bindings": records,
        "creature_rig_family": "winged_biped",
        "rig_map": f"{rig_name}_winged_biped_semantic_bones_v1",
        "weight_policy": "one full influence per vertex; spatial semantic wings, limbs, head, spine, and pelvis",
        "status": "pass",
    }
    report_path = job / "blender" / "reports" / "creature_rig.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def author_creature_rig(req: Dict[str, Any]) -> Dict[str, Any]:
    """Create a bounded creature armature and bind the approved mesh to semantic bones."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    if str(payload.get("creature_rig_family") or "elephant").casefold() == "winged_biped":
        return author_winged_biped_rig(req)
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    rider_names = {str(name) for name in payload.get("rider_component_names", [])}
    weight_mode = str(payload.get("weight_mode") or "semantic").casefold()
    rig_name = safe_name(str(payload.get("rig_name") or "elephant_shared_base_armature"))
    if weight_mode not in {"semantic", "automatic_body", "automatic_semantic"}:
        raise ValueError(f"Unsupported creature rig weight mode: {weight_mode}")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    working = mesh_objects()
    if not working:
        raise RuntimeError("Creature rigging found no working meshes.")
    existing = armatures()
    for rig in existing:
        bpy.data.objects.remove(rig, do_unlink=True)
    minimum, maximum = world_bounds(working)
    dimensions = maximum - minimum
    centre = (minimum + maximum) * 0.5
    height = max(dimensions.z, 1e-6)
    length = max(dimensions.y, 1e-6)
    width = max(dimensions.x, 1e-6)
    armature_data = bpy.data.armatures.new(rig_name)
    rig = bpy.data.objects.new(rig_name, armature_data)
    _working_collection().objects.link(rig)
    rig["hoi4_working"] = True
    rig["hoi4_custom_creature_rig"] = True
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bones: Dict[str, bpy.types.EditBone] = {}

    def add_bone(name: str, head: Vector, tail: Vector, parent: str | None = None) -> None:
        bone = armature_data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        if parent:
            bone.parent = bones[parent]
            bone.use_connect = False
        bones[name] = bone

    z0 = minimum.z
    add_bone("root", Vector((centre.x, centre.y, z0)), Vector((centre.x, centre.y, z0 + height * 0.18)))
    add_bone("body", Vector((centre.x, centre.y, z0 + height * 0.38)), Vector((centre.x, centre.y, z0 + height * 0.68)), "root")
    add_bone("neck", Vector((centre.x, minimum.y + length * 0.17, z0 + height * 0.62)), Vector((centre.x, minimum.y + length * 0.06, z0 + height * 0.79)), "body")
    add_bone("head", Vector((centre.x, minimum.y + length * 0.06, z0 + height * 0.76)), Vector((centre.x, minimum.y - length * 0.12, z0 + height * 0.73)), "neck")
    add_bone("trunk_01", Vector((centre.x, minimum.y - length * 0.10, z0 + height * 0.71)), Vector((centre.x, minimum.y - length * 0.22, z0 + height * 0.47)), "head")
    add_bone("trunk_02", Vector((centre.x, minimum.y - length * 0.22, z0 + height * 0.47)), Vector((centre.x, minimum.y - length * 0.27, z0 + height * 0.16)), "trunk_01")
    add_bone("tail", Vector((centre.x, maximum.y - length * 0.12, z0 + height * 0.56)), Vector((centre.x, maximum.y + length * 0.08, z0 + height * 0.48)), "body")
    for end, y in (("front", minimum.y + length * 0.30), ("rear", maximum.y - length * 0.28)):
        for side, x in (("left", centre.x - width * 0.30), ("right", centre.x + width * 0.30)):
            upper = f"{end}_{side}_upper"
            lower = f"{end}_{side}_lower"
            add_bone(upper, Vector((x, y, z0 + height * 0.48)), Vector((x, y, z0 + height * 0.20)), "body")
            add_bone(lower, Vector((x, y, z0 + height * 0.20)), Vector((x, y, z0 + height * 0.04)), upper)
    add_bone("howdah", Vector((centre.x, centre.y, z0 + height * 0.75)), Vector((centre.x, centre.y, z0 + height * 0.90)), "body")
    add_bone("rider", Vector((centre.x, centre.y, z0 + height * 0.88)), Vector((centre.x, centre.y, z0 + height * 1.08)), "howdah")
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.show_in_front = True
    armature_data.display_type = "BBONE"
    records = []
    rigid_semantic_objects = {
        "elephant_body_region", "head", "trunk_01", "trunk_02", "tail", "howdah",
        "front_left_upper", "front_left_lower", "front_right_upper", "front_right_lower",
        "rear_left_upper", "rear_left_lower", "rear_right_upper", "rear_right_lower",
    }
    for obj in working:
        obj_minimum, obj_maximum = world_bounds([obj])
        obj_center = (obj_minimum + obj_maximum) * 0.5
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        groups = {
            bone.name: obj.vertex_groups.new(name=bone.name)
            for bone in armature_data.bones
        }
        counts: Dict[str, int] = {name: 0 for name in groups}
        if weight_mode in {"automatic_body", "automatic_semantic"} and obj.name == "elephant_body_region":
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            rig.select_set(True)
            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.parent_set(type="ARMATURE_AUTO")
            for vertex in obj.data.vertices:
                influence_map = {item.group: float(item.weight) for item in vertex.groups if item.weight > 0.0}
                if weight_mode == "automatic_semantic":
                    primary_name = _creature_bone_name_for_vertex(
                        obj.matrix_world @ vertex.co,
                        minimum,
                        maximum,
                        rider_names,
                        obj.name,
                    )
                    primary_group = obj.vertex_groups.get(primary_name)
                    influence_map = {group_index: weight * 0.30 for group_index, weight in influence_map.items()}
                    if primary_group is not None:
                        influence_map[primary_group.index] = influence_map.get(primary_group.index, 0.0) + 0.70
                influences = sorted(influence_map.items(), key=lambda item: item[1], reverse=True)[:4]
                total_weight = sum(weight for _, weight in influences)
                keep = {group_index for group_index, _ in influences}
                for group in obj.vertex_groups:
                    if group.index not in keep:
                        group.remove([vertex.index])
                if total_weight > 0.0:
                    for group_index, weight in influences:
                        obj.vertex_groups[group_index].add([vertex.index], weight / total_weight, "REPLACE")
            counts = {
                group.name: sum(1 for vertex in obj.data.vertices if any(item.group == group.index and item.weight > 0.0 for item in vertex.groups))
                for group in obj.vertex_groups
            }
            binding_policy = "blender_automatic_body_weights"
        elif obj.name in rigid_semantic_objects or obj.name in rider_names:
            bone_name = _creature_bone_name_for_component(
                obj_center,
                obj_maximum - obj_minimum,
                obj_minimum,
                obj_maximum,
                rider_names,
                obj.name,
                minimum,
                maximum,
            )
            if bone_name not in groups:
                bone_name = "body"
            groups[bone_name].add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
            counts[bone_name] = len(obj.data.vertices)
            binding_policy = "rigid_semantic_component"
        else:
            for vertex in obj.data.vertices:
                world_position = obj.matrix_world @ vertex.co
                bone_name = _creature_bone_name_for_vertex(
                    world_position,
                    minimum,
                    maximum,
                    rider_names,
                    obj.name,
                )
                if bone_name not in groups:
                    bone_name = "body"
                groups[bone_name].add([vertex.index], 1.0, "REPLACE")
                counts[bone_name] += 1
            binding_policy = "spatial_semantic_weights"
        modifier = next((item for item in obj.modifiers if item.type == "ARMATURE"), None)
        if modifier is None:
            modifier = obj.modifiers.new("HOI4_CREATURE_ARMATURE", "ARMATURE")
        modifier.object = rig
        world_matrix = obj.matrix_world.copy()
        obj.parent = rig
        obj.parent_type = "OBJECT"
        obj.matrix_world = world_matrix
        records.append(
            {
                "object": obj.name,
                "bone": binding_policy,
                "vertices": len(obj.data.vertices),
                "vertex_group_counts": {name: count for name, count in counts.items() if count},
            }
        )
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "armature": rig.name,
        "bones": [bone.name for bone in armature_data.bones],
        "component_bindings": records,
        "rider_components": sorted(rider_names),
        "rig_map": f"{rig_name}_semantic_bones_v1",
        "requested_weight_mode": weight_mode,
        "weight_policy": "one full influence per vertex; explicitly segmented semantic objects use rigid component bindings and rider remains distinct",
        "status": "pass",
    }
    report_path = job / "blender" / "reports" / "creature_rig.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _action_delta(axis: str, degrees: float) -> Quaternion:
    vector = {"x": Vector((1.0, 0.0, 0.0)), "y": Vector((0.0, 1.0, 0.0)), "z": Vector((0.0, 0.0, 1.0))}[axis]
    return Quaternion(vector, math.radians(degrees))


def author_winged_biped_action(req: Dict[str, Any]) -> Dict[str, Any]:
    """Author a real skeletal action on the winged/digitigrade biped rig."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    role = str(payload.get("action_role") or "").casefold()
    action_name = safe_name(str(payload.get("action_name") or f"winged_biped_{role}"))
    if role not in {"idle", "move", "attack", "death"}:
        raise ValueError(f"Unsupported winged biped action role: {role}")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError(f"Winged biped action authoring requires exactly one armature, found {len(rigs)}.")
    rig = rigs[0]
    rig.animation_data_create()
    action = bpy.data.actions.get(action_name)
    if action is not None:
        bpy.data.actions.remove(action)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    rig.animation_data.action = action
    if role == "idle":
        frames = [0, 12, 24, 36, 48]
    elif role == "move":
        frames = [0, 6, 12, 18, 24]
    elif role == "attack":
        frames = [0, 8, 16, 24, 32]
    else:
        frames = [0, 12, 24, 36]
    scene = bpy.context.scene
    scene.render.fps = int(payload.get("fps") or 30)
    scene.frame_start = frames[0]
    scene.frame_end = frames[-1]
    base = {
        bone.name: (bone.location.copy(), bone.rotation_quaternion.copy())
        for bone in rig.pose.bones
    }

    def phase(frame: int) -> float:
        span = max(frames[-1] - frames[0], 1)
        if role in {"idle", "move"}:
            return math.sin(2.0 * math.pi * (frame - frames[0]) / span)
        return (frame - frames[0]) / span

    def rotate(name: str, axis: str, degrees: float, value: float) -> None:
        bone = rig.pose.bones.get(name)
        if bone is None:
            return
        bone.rotation_mode = "QUATERNION"
        bone.rotation_quaternion = base[name][1] @ _action_delta(axis, degrees * value)

    keyed = 0
    for frame in frames:
        scene.frame_set(frame)
        p = phase(frame)
        for bone in rig.pose.bones:
            bone.rotation_mode = "QUATERNION"
            bone.location = base[bone.name][0].copy()
            bone.rotation_quaternion = base[bone.name][1].copy()
        if role == "idle":
            rotate("spine", "x", 1.5, p)
            rotate("neck", "x", 2.5, p)
            rotate("head", "z", 1.5, p)
            for side in ("left", "right"):
                rotate(f"wing_mid_{side}", "z", 2.0, p)
                rotate(f"wing_tip_{side}", "z", 3.0, p)
        elif role == "move":
            for side, sign in (("left", 1.0), ("right", -1.0)):
                gait = sign * p
                rotate(f"upper_leg_{side}", "x", 8.0, gait)
                rotate(f"lower_leg_{side}", "x", -5.0, gait)
                rotate(f"foot_{side}", "x", 2.5, gait)
                rotate(f"upper_arm_{side}", "x", -5.5, gait)
                rotate(f"lower_arm_{side}", "x", 3.0, gait)
                rotate(f"wing_mid_{side}", "z", 1.0, p)
                rotate(f"wing_tip_{side}", "z", 1.5, p)
            rotate("spine", "x", 2.0, p)
            rotate("head", "z", 1.0, p)
        elif role == "attack":
            rotate("spine", "x", -10.0, p)
            rotate("neck", "x", -8.0, p)
            rotate("head", "x", -12.0, p)
            for side, sign in (("left", 1.0), ("right", -1.0)):
                rotate(f"upper_arm_{side}", "x", -28.0, p)
                rotate(f"lower_arm_{side}", "x", -20.0, p)
                rotate(f"hand_{side}", "z", 8.0 * sign, p)
                rotate(f"wing_root_{side}", "z", 12.0 * sign, p)
                rotate(f"wing_mid_{side}", "z", 20.0 * sign, p)
                rotate(f"wing_tip_{side}", "z", 25.0 * sign, p)
            rotate("upper_leg_left", "x", -5.0, p)
            rotate("upper_leg_right", "x", -5.0, p)
        else:
            rotate("spine", "x", -42.0, p)
            rotate("neck", "x", -28.0, p)
            rotate("head", "x", -22.0, p)
            for side, sign in (("left", 1.0), ("right", -1.0)):
                rotate(f"upper_arm_{side}", "z", 24.0 * sign, p)
                rotate(f"lower_arm_{side}", "z", 18.0 * sign, p)
                rotate(f"wing_root_{side}", "z", -18.0 * sign, p)
                rotate(f"wing_mid_{side}", "z", -26.0 * sign, p)
                rotate(f"wing_tip_{side}", "z", -32.0 * sign, p)
                rotate(f"upper_leg_{side}", "x", 10.0, p)
                rotate(f"lower_leg_{side}", "x", 12.0, p)
        for bone in rig.pose.bones:
            bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
            bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=bone.name)
            keyed += 1
    for fcurve, _ in action_fcurves(action):
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "LINEAR"

    if rig.pose.bones.get("root") is None:
        raise RuntimeError("Winged biped action authoring requires a root bone.")
    base_rig_location = rig.location.copy()
    ground_samples_before = []
    for frame in range(frames[0], frames[-1] + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        minimum, maximum = evaluated_world_bounds(mesh_objects())
        ground_samples_before.append({"frame": frame, "ground_contact_z": float(minimum.z), "bounds_max_z": float(maximum.z)})
    corrections = []
    for frame in range(frames[0], frames[-1] + 1):
        scene.frame_set(frame)
        # Measure each pose from the uncorrected armature location.  Without
        # this reset, previously keyed offsets are included in the next sample
        # and the correction drifts instead of remaining an absolute offset.
        rig.location = base_rig_location.copy()
        bpy.context.view_layer.update()
        minimum, _ = evaluated_world_bounds(mesh_objects())
        correction = max(
            0.0,
            -float(minimum.z) + CREATURE_GROUND_CONTACT_CLEARANCE_M,
        )
        # Mesh objects are parented to the armature object in the custom route.
        # Keying the root pose bone alone does not translate the evaluated object
        # bounds, so ground correction must be authored on the armature object.
        rig.location = base_rig_location.copy()
        rig.location.z = base_rig_location.z + correction
        rig.keyframe_insert(data_path="location", index=2, frame=frame, group=rig.name)
        corrections.append(correction)
    for fcurve, _ in action_fcurves(action):
        if fcurve.data_path.endswith(".location") and fcurve.array_index == 2:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "LINEAR"
            fcurve.update()
    ground_samples_after = []
    for frame in range(frames[0], frames[-1] + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        minimum, maximum = evaluated_world_bounds(mesh_objects())
        ground_samples_after.append({"frame": frame, "ground_contact_z": float(minimum.z), "bounds_max_z": float(maximum.z)})
    minimum_ground = min(item["ground_contact_z"] for item in ground_samples_after)
    maximum_ground = max(item["ground_contact_z"] for item in ground_samples_after)
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "armature": rig.name,
        "action": action.name,
        "role": role,
        "frame_start": frames[0],
        "frame_end": frames[-1],
        "fps": scene.render.fps,
        "loop": role in {"idle", "move"},
        "keyed_bones": keyed,
        "keyed_channels": keyed * 2,
        "ground_contact": {
            "minimum_z": minimum_ground,
            "maximum_z": maximum_ground,
            "sample_count": len(ground_samples_after),
            "samples_before": ground_samples_before,
            "samples_after": ground_samples_after,
        },
        "grounding_correction": {
            "applied": any(value > 0.0 for value in corrections),
            "maximum_translation_m": max(corrections, default=0.0),
            "samples_before": ground_samples_before,
            "samples_after": ground_samples_after,
        },
        "creature_rig_family": "winged_biped",
        "policy": "blender-authored-winged-biped-semantic-skeletal-action-no-scale-channels",
        "status": (
            "pass"
            if minimum_ground >= -CREATURE_GROUND_CONTACT_TOLERANCE_M
            else "needs_grounding_review"
        ),
    }
    report_path = job / "blender" / "reports" / f"creature_action_{safe_name(role)}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def author_creature_action(req: Dict[str, Any]) -> Dict[str, Any]:
    """Author one semantic skeletal action for the custom creature rig."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    if str(payload.get("creature_rig_family") or "elephant").casefold() == "winged_biped":
        return author_winged_biped_action(req)
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    role = str(payload.get("action_role") or "").casefold()
    action_name = safe_name(str(payload.get("action_name") or f"creature_{role}"))
    allowed_roles = {"idle", "move", "retreat", "deploy", "supply_load", "attack", "impact", "death"}
    if role not in allowed_roles:
        raise ValueError(f"Unsupported creature action role: {role}")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError(f"Creature action authoring requires exactly one armature, found {len(rigs)}.")
    rig = rigs[0]
    rig.animation_data_create()
    action = bpy.data.actions.get(action_name)
    if action is not None:
        bpy.data.actions.remove(action)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    rig.animation_data.action = action
    if role == "idle":
        frames = [0, 12, 24, 36, 48]
    elif role in {"move", "retreat"}:
        frames = [0, 6, 12, 18, 24]
    elif role == "deploy":
        frames = [0, 12, 24, 36]
    elif role == "supply_load":
        frames = [0, 10, 20, 30, 40]
    elif role == "attack":
        frames = [0, 8, 16, 24, 32]
    elif role == "death":
        frames = [0, 12, 24, 36]
    else:
        frames = [0, 6, 12, 18, 24]
    scene = bpy.context.scene
    scene.frame_start = frames[0]
    scene.frame_end = frames[-1]
    base = {
        bone.name: (bone.location.copy(), bone.rotation_quaternion.copy())
        for bone in rig.pose.bones
    }

    def phase(frame: int) -> float:
        if role in {"idle", "move", "retreat"}:
            return math.sin(2.0 * math.pi * (frame - frames[0]) / max(frames[-1] - frames[0], 1))
        if role == "deploy":
            return (frame - frames[0]) / max(frames[-1] - frames[0], 1)
        if role == "supply_load":
            return math.sin(math.pi * (frame - frames[0]) / max(frames[-1] - frames[0], 1))
        if role == "attack":
            return math.sin(math.pi * (frame - frames[0]) / max(frames[-1] - frames[0], 1))
        if role == "death":
            return (frame - frames[0]) / max(frames[-1] - frames[0], 1)
        return math.sin(math.pi * (frame - frames[0]) / max(frames[-1] - frames[0], 1))

    keyed = 0
    for frame in frames:
        scene.frame_set(frame)
        p = phase(frame)
        for bone in rig.pose.bones:
            location, rotation = base[bone.name]
            bone.rotation_mode = "QUATERNION"
            bone.location = location.copy()
            bone.rotation_quaternion = rotation.copy()
            if role == "idle":
                if bone.name in {"body", "neck"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 0.6 * p)
                if bone.name in {"trunk_01", "trunk_02"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 1.2 * p)
            elif role in {"move", "retreat"}:
                cycle_phase = p if role == "move" else -p
                if bone.name == "body":
                    bone.rotation_quaternion = rotation @ _action_delta("x", 0.5 * cycle_phase)
                if bone.name in {"front_left_lower", "rear_right_lower"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -1.0 * cycle_phase)
                if bone.name in {"front_right_lower", "rear_left_lower"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 1.0 * cycle_phase)
                if bone.name in {"front_left_upper", "rear_right_upper"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 1.5 * cycle_phase)
                if bone.name in {"front_right_upper", "rear_left_upper"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -1.5 * cycle_phase)
                if bone.name in {"neck", "trunk_01", "trunk_02"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 0.8 * cycle_phase)
            elif role == "deploy":
                if bone.name == "body":
                    bone.rotation_quaternion = rotation @ _action_delta("x", -0.05 * p)
                if bone.name in {"neck", "head"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 0.20 * p)
                if bone.name in {"trunk_01", "trunk_02"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -0.50 * p)
            elif role == "supply_load":
                if bone.name in {"neck", "head", "trunk_01", "trunk_02"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 1.00 * p)
                if bone.name == "body":
                    bone.rotation_quaternion = rotation @ _action_delta("x", 0.05 * p)
            elif role == "attack":
                if bone.name in {"body", "neck", "head"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -1.0 * p)
                if bone.name in {"trunk_01", "trunk_02"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -2.0 * p)
                if bone.name in {"front_left_lower", "front_right_lower"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -1.0 * p)
            elif role == "death":
                if bone.name in {"body", "neck", "head"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -1.5 * p)
                if bone.name in {"trunk_01", "trunk_02"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -2.5 * p)
                if bone.name in {"front_left_upper", "rear_right_upper"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", -1.0 * p)
                if bone.name in {"front_right_upper", "rear_left_upper"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 1.0 * p)
                if bone.name in {"front_left_lower", "front_right_lower", "rear_left_lower", "rear_right_lower"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 1.5 * p)
            elif role == "impact":
                if bone.name in {"body", "neck", "head"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 0.04 * p)
                if bone.name in {"trunk_01", "trunk_02"}:
                    bone.rotation_quaternion = rotation @ _action_delta("x", 0.08 * p)
                if bone.name.startswith("front_"):
                    bone.rotation_quaternion = rotation @ _action_delta("x", -0.05 * p)
            bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
            bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=bone.name)
            keyed += 1
    for fcurve, _ in action_fcurves(action):
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "LINEAR"
    scene.frame_set(frames[0])
    bpy.context.view_layer.update()
    ground_samples = []
    for frame in range(frames[0], frames[-1] + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        minimum, maximum = evaluated_world_bounds(mesh_objects())
        ground_samples.append({"frame": frame, "ground_contact_z": float(minimum.z), "bounds_max_z": float(maximum.z)})
    minimum_ground = min(item["ground_contact_z"] for item in ground_samples)
    maximum_ground = max(item["ground_contact_z"] for item in ground_samples)
    grounding_correction = {
        "applied": False,
        "root_bone": "root",
        "epsilon_m": CREATURE_GROUND_CONTACT_TOLERANCE_M,
        "clearance_m": CREATURE_GROUND_CONTACT_CLEARANCE_M,
        "maximum_translation_m": 0.0,
        "samples_before": ground_samples,
    }
    root = rig.pose.bones.get("root") or rig.pose.bones.get("body")
    if root is None:
        raise RuntimeError("Creature action authoring requires a semantic root bone.")
    # Ground every sampled frame with an explicit root translation channel.
    # This preserves the authored rotations and avoids feet/underside sinking
    # below the map plane after large elephant rotations.
    for frame in range(frames[0], frames[-1] + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        current_minimum, _ = evaluated_world_bounds(mesh_objects())
        # Treat one centimetre as the contact tolerance used by the report.
        # Do not claim a lift when the semantic body channel cannot move the
        # rigidly separated shell in Blender's evaluated armature; such a case
        # remains visible as a failed contact sample instead of a silent fix.
        correction = max(
            0.0,
            -float(current_minimum.z) + CREATURE_GROUND_CONTACT_CLEARANCE_M,
        )
        if correction:
            # Lift the common root so the correction is represented once in
            # the exported skeleton and is not multiplied down child bones.
            root.location.z = base[root.name][0].z + correction
            root.keyframe_insert(data_path="location", index=2, frame=frame, group=root.name)
            grounding_correction["applied"] = True
            grounding_correction["maximum_translation_m"] = max(
                float(grounding_correction["maximum_translation_m"]), correction
            )
        root.keyframe_insert(data_path="location", index=2, frame=frame, group=root.name)
    for fcurve, _ in action_fcurves(action):
        if fcurve.data_path.endswith(".location") and fcurve.array_index == 2:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "LINEAR"
            fcurve.update()
    scene.frame_set(frames[0])
    bpy.context.view_layer.update()
    corrected_samples = []
    for frame in range(frames[0], frames[-1] + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        current_minimum, current_maximum = evaluated_world_bounds(mesh_objects())
        corrected_samples.append(
            {
                "frame": frame,
                "ground_contact_z": float(current_minimum.z),
                "bounds_max_z": float(current_maximum.z),
            }
        )
    ground_samples = corrected_samples
    minimum_ground = min(item["ground_contact_z"] for item in ground_samples)
    maximum_ground = max(item["ground_contact_z"] for item in ground_samples)
    grounding_correction["samples_after"] = ground_samples
    grounding_correction["minimum_after_m"] = minimum_ground
    grounding_correction["maximum_after_m"] = maximum_ground
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "armature": rig.name,
        "action": action.name,
        "role": role,
        "frame_start": frames[0],
        "frame_end": frames[-1],
        "fps": scene.render.fps,
        "loop": role in {"idle", "move", "retreat"},
        "keyed_bones": keyed,
        "keyed_channels": keyed * 2,
        "ground_contact": {
            "minimum_z": minimum_ground,
            "maximum_z": maximum_ground,
            "sample_count": len(ground_samples),
            "samples": ground_samples,
        },
        "grounding_correction": grounding_correction,
        "policy": "blender-authored-semantic-skeletal-action-no-scale-channels",
        "status": (
            "pass"
            if minimum_ground >= -CREATURE_GROUND_CONTACT_TOLERANCE_M
            else "needs_grounding_review"
        ),
    }
    report_path = job / "blender" / "reports" / f"creature_action_{safe_name(role)}.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def correct_action_grounding(req: Dict[str, Any]) -> Dict[str, Any]:
    """Correct one existing skeletal action's root contact, preserving body keys."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    action_name = str(payload.get("action_name") or "")
    root_bone_name = str(payload.get("root_bone") or "Hips")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError(f"Grounding correction requires exactly one working armature, found {len(rigs)}.")
    rig = rigs[0]
    rig.animation_data_create()
    action = bpy.data.actions.get(action_name)
    if action is None:
        action = next(
            (
                candidate
                for candidate in bpy.data.actions
                if candidate.name.casefold() == action_name.casefold()
            ),
            None,
        )
    if action is None:
        raise RuntimeError(f"Requested action was not found: {action_name}")
    rig.animation_data.action = action
    root = rig.pose.bones.get(root_bone_name)
    if root is None:
        raise RuntimeError(f"Grounding correction root bone was not found: {root_bone_name}")
    meshes = mesh_objects()
    if not meshes:
        raise RuntimeError("Grounding correction found no working mesh objects.")

    start = int(math.floor(float(action.frame_range[0])))
    end = int(math.ceil(float(action.frame_range[1])))
    if end < start:
        raise RuntimeError("Grounding correction requires a non-empty action frame range.")
    scene = bpy.context.scene
    scene.frame_start = start
    scene.frame_end = end

    # Blender pose-bone location channels use bone-local axes. Detect which
    # local channel produces the strongest world-Z response, then key that
    # channel at every integer frame so no sparse-key overshoot is introduced.
    scene.frame_set(start)
    bpy.context.view_layer.update()
    baseline_minimum, _ = evaluated_world_bounds(meshes)
    axis_responses = []
    for axis_index in range(3):
        original_axis_value = float(root.location[axis_index])
        root.location[axis_index] = original_axis_value + 1.0
        bpy.context.view_layer.update()
        test_minimum, _ = evaluated_world_bounds(meshes)
        root.location[axis_index] = original_axis_value
        bpy.context.view_layer.update()
        axis_responses.append(float(test_minimum.z - baseline_minimum.z))
    correction_axis = max(range(3), key=lambda index: abs(axis_responses[index]))
    if abs(axis_responses[correction_axis]) <= 1e-8:
        raise RuntimeError("Grounding correction found no usable pose-location response on any local axis.")
    for frame in range(start, end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        root.keyframe_insert(data_path="location", index=correction_axis, frame=frame, group=root_bone_name)

    z_path = f'pose.bones["{root_bone_name}"].location'
    correction_curve = next(
        (
            fcurve
            for fcurve, _ in action_fcurves(action)
            if fcurve.data_path == z_path and fcurve.array_index == correction_axis
        ),
        None,
    )
    if correction_curve is None or len(correction_curve.keyframe_points) < end - start + 1:
        raise RuntimeError("Grounding correction could not create the selected root location channel.")
    for keyframe in correction_curve.keyframe_points:
        keyframe.interpolation = "LINEAR"
    correction_curve.update()

    frame_records: List[Dict[str, Any]] = []
    max_correction = 0.0
    before_values: List[float] = []
    after_values: List[float] = []

    def write_root_z(frame: int, value: float) -> None:
        root.location[correction_axis] = value
        root.keyframe_insert(data_path="location", index=correction_axis, frame=frame, group=root_bone_name)
        correction_curve.update()
        bpy.context.view_layer.update()

    for frame in range(start, end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        before_minimum, _ = evaluated_world_bounds(meshes)
        original_value = float(root.location[correction_axis])
        test_step = 1.0
        write_root_z(frame, original_value + test_step)
        test_minimum, _ = evaluated_world_bounds(meshes)
        write_root_z(frame, original_value)
        derivative = float(test_minimum.z - before_minimum.z) / test_step
        if abs(derivative) <= 1e-8:
            raise RuntimeError(f"Grounding correction found no usable root-Z response at frame {frame}.")
        correction = -float(before_minimum.z) / derivative
        write_root_z(frame, original_value + correction)
        after_minimum, _ = evaluated_world_bounds(meshes)
        before_values.append(float(before_minimum.z))
        after_values.append(float(after_minimum.z))
        max_correction = max(max_correction, abs(correction))
        frame_records.append(
            {
                "frame": frame,
                "ground_contact_before": float(before_minimum.z),
                "ground_contact_after": float(after_minimum.z),
                "derivative": derivative,
                "correction_source_units": correction,
            }
        )

    scene.frame_set(start)
    bpy.context.view_layer.update()
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "action": action.name,
        "root_bone": root_bone_name,
        "root_location_axis_index": correction_axis,
        "root_location_axis_world_z_responses": axis_responses,
        "frame_start": start,
        "frame_end": end,
        "fps": scene.render.fps,
        "corrected_frames": len(frame_records),
        "max_absolute_correction_source_units": max_correction,
        "ground_contact_before": {
            "minimum": min(before_values),
            "maximum": max(before_values),
        },
        "ground_contact_after": {
            "minimum": min(after_values),
            "maximum": max(after_values),
        },
        "action_preservation": {
            "policy": "existing_action_root_z_only",
            "body_motion_replaced": False,
            "new_model_created": False,
            "new_rig_created": False,
            "new_provider_call": False,
        },
        "frames": frame_records,
        "status": "pass" if max(after_values) <= 0.001 and min(after_values) >= -0.001 else "fail",
    }
    report_path = job / "blender" / "reports" / f"correct_action_grounding_{safe_name(action.name)}.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError(
            "Grounding correction did not satisfy the per-frame contact tolerance: "
            f"{report['ground_contact_after']}"
        )
    return report


def offset_action_root(req: Dict[str, Any]) -> Dict[str, Any]:
    """Apply a bounded source-space root offset to an existing action frame range."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    action_name = str(payload.get("action_name") or "")
    frame_start = int(payload.get("frame_start"))
    frame_end = int(payload.get("frame_end"))
    offset_source_units = float(payload.get("offset_source_units") or 0.0)
    axis_index = int(payload.get("axis_index", 1))
    if not action_name:
        raise ValueError("Root offset requires an action name.")
    if frame_end < frame_start:
        raise ValueError("Root offset frame_end must not precede frame_start.")
    if axis_index not in {0, 1, 2}:
        raise ValueError("Root offset axis_index must be 0, 1, or 2.")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError(f"Root offset requires exactly one working armature, found {len(rigs)}.")
    rig = rigs[0]
    action = bpy.data.actions.get(action_name)
    if action is None:
        action = next(
            (
                candidate
                for candidate in bpy.data.actions
                if candidate.name.casefold() == action_name.casefold()
            ),
            None,
        )
    if action is None:
        raise RuntimeError(f"Requested action was not found: {action_name}")
    root_bone_name = str(payload.get("root_bone") or "Hips")
    rig.animation_data_create()
    rig.animation_data.action = action
    root = rig.pose.bones.get(root_bone_name)
    if root is None:
        raise RuntimeError(f"Root offset bone was not found: {root_bone_name}")

    scene = bpy.context.scene
    scene.frame_start = frame_start
    scene.frame_end = frame_end
    correction_curve = None
    path = f'pose.bones["{root_bone_name}"].location'
    for fcurve, _ in action_fcurves(action):
        if fcurve.data_path == path and fcurve.array_index == axis_index:
            correction_curve = fcurve
            break
    for frame in range(frame_start, frame_end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        root.location[axis_index] = float(root.location[axis_index]) + offset_source_units
        root.keyframe_insert(data_path="location", index=axis_index, frame=frame, group=root_bone_name)
    if correction_curve is None:
        for fcurve, _ in action_fcurves(action):
            if fcurve.data_path == path and fcurve.array_index == axis_index:
                correction_curve = fcurve
                break
    if correction_curve is not None:
        correction_curve.update()
    scene.frame_set(frame_start)
    bpy.context.view_layer.update()
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "action": action.name,
        "root_bone": root_bone_name,
        "axis_index": axis_index,
        "frame_start": frame_start,
        "frame_end": frame_end,
        "offset_source_units": offset_source_units,
        "corrected_frames": frame_end - frame_start + 1,
        "policy": "bounded_existing_action_root_frame_offset_for_export_reimport_contact",
        "body_motion_replaced": False,
        "new_model_created": False,
        "new_rig_created": False,
        "new_provider_call": False,
        "warnings": [],
    }
    report_path = job / "blender" / "reports" / f"offset_action_root_{safe_name(action.name)}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def reimport_export(req: Dict[str, Any], pdx: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    mesh = within(job, payload["mesh_rel"])
    anim = within(job, payload["anim_rel"]) if payload.get("anim_rel") else None
    texture_staging = []
    requested_texture_names = tuple(
        str(name)
        for name in (payload.get("texture_names") or [])
        if str(name).casefold().endswith(".dds")
    )
    default_texture_names = (
        "texture_0.dds",
        "texture_specular.dds",
        "texture_normal.dds",
        "elephant_shared_base_diff.dds",
        "elephant_shared_base_spec.dds",
        "elephant_shared_base_n.dds",
        "Image_0.dds",
        "Image_1.dds",
        "Image_2.dds",
        "Image_3.dds",
        "normal.dds",
    )
    for texture_name in tuple(dict.fromkeys(requested_texture_names + default_texture_names)):
        source = job / "textures" / "dds" / texture_name
        if not source.is_file():
            continue
        destination = mesh.parent / texture_name
        already_staged = (
            destination.is_file()
            and destination.stat().st_size == source.stat().st_size
            and destination.read_bytes() == source.read_bytes()
        )
        if not already_staged:
            shutil.copy2(source, destination)
        texture_staging.append(
            {
                "source": str(source.relative_to(job)).replace("\\", "/"),
                "staged": str(destination.relative_to(job)).replace("\\", "/"),
                "bytes": destination.stat().st_size,
                "copied": not already_staged,
            }
        )
    clear_scene()
    pdx = load_pdx(req["io_pdx_root"])
    pdx["import_meshfile"](
        str(mesh),
        imp_mesh=True,
        imp_skel=True,
        imp_locs=True,
        join_materials=True,
        bonespace=False,
    )
    if anim is not None:
        pdx["import_animfile"](str(anim), frame_start=1)
    proof_name = safe_name(
        payload.get("proof_name")
        or f"{mesh.stem}_{Path(payload['anim_rel']).stem if payload.get('anim_rel') else 'mesh'}"
    )
    animation_bounds = []
    preview_paths = []
    if anim is not None:
        actions = [action for action in bpy.data.actions if action.frame_range[1] >= action.frame_range[0]]
        if actions:
            action = max(actions, key=lambda candidate: candidate.frame_range[1] - candidate.frame_range[0])
            rigs = armatures(working_only=False)
            if len(rigs) == 1:
                rigs[0].animation_data_create()
                rigs[0].animation_data.action = action
            first = int(math.floor(float(action.frame_range[0])))
            last = int(math.ceil(float(action.frame_range[1])))
            span = last - first
            sample_frames = sorted(
                {
                    first,
                    int(round(first + span * 0.25)),
                    int(round(first + span * 0.5)),
                    int(round(first + span * 0.75)),
                    last,
                }
            )
            for frame in sample_frames:
                bpy.context.scene.frame_set(frame)
                bpy.context.view_layer.update()
                minimum, maximum = evaluated_world_bounds(mesh_objects(working_only=False))
                animation_bounds.append(
                    {
                        "frame": frame,
                        "bounds_min": list(minimum),
                        "bounds_max": list(maximum),
                        "ground_contact_z": float(minimum.z),
                        "dimensions": list(maximum - minimum),
                    }
                )
                preview_paths.extend(
                    render_previews(
                        job,
                        f"reimport_{proof_name}_frame_{frame:03d}",
                        ["front", "left", "three_quarter"],
                        working_only=False,
                    )
                )
            bpy.context.scene.frame_set(first)
            bpy.context.view_layer.update()
    else:
        preview_paths.extend(
            render_previews(
                job,
                f"reimport_{proof_name}",
                working_only=False,
            )
        )
    proof = job / "blender" / "checkpoints" / f"reimport_{proof_name}.blend"
    save_blend(proof)
    report = {
        "mesh": str(mesh.relative_to(job)).replace("\\", "/"),
        "anim": str(anim.relative_to(job)).replace("\\", "/") if anim else None,
        "runtime_texture_staging": texture_staging,
        "proof_blend": str(proof.relative_to(job)).replace("\\", "/"),
        "objects": [
            {"name": obj.name, "type": obj.type}
            for obj in bpy.context.scene.objects
        ],
        "meshes": [
            {
                "name": obj.name,
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
                "materials": [mat.name for mat in obj.data.materials],
            }
            for obj in bpy.context.scene.objects
            if obj.type == "MESH"
        ],
        "geometry": geometry_metrics(working_only=False, position_weld_distance=1e-6),
        "animation_bounds": animation_bounds,
        "previews": sorted(set(preview_paths)),
        "armatures": [
            {"name": obj.name, "bones": len(obj.data.bones)}
            for obj in bpy.context.scene.objects
            if obj.type == "ARMATURE"
        ],
        "actions": [action.name for action in bpy.data.actions],
    }
    report_path = job / "validation" / f"reimport_{proof_name}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def sanitize_runtime_candidate(req: Dict[str, Any]) -> Dict[str, Any]:
    """Create a reviewable runtime checkpoint with bounded skin/material cleanup."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    output = within(
        job,
        payload.get("output_blend_rel", "blender/checkpoints/07_runtime_candidate_sanitized.blend"),
        allow_missing=True,
    )
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    geometry_normalization = (
        normalize_geometry(float(payload["target_height_m"]))
        if payload.get("target_height_m") is not None
        else {"policy": "preserve_checkpoint_geometry"}
    )
    weights_before = weight_metrics()
    weights = sanitize_working_weights()
    materials = sanitize_working_materials()
    output.parent.mkdir(parents=True, exist_ok=True)
    save_blend(output)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(output.relative_to(job)).replace("\\", "/"),
        "geometry_normalization": geometry_normalization,
        "weights_before": weights_before,
        "weights": weights,
        "materials": materials,
        "geometry": geometry_metrics(),
        "rig_and_actions": action_metrics(),
    }
    report_path = job / "blender" / "reports" / "weights_sanitized.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def save_checkpoint_operation(req: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    source = within(job, payload["blend_rel"])
    stage = safe_name(payload["stage"])
    destination = job / "blender" / "checkpoints" / f"{stage}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    save_blend(destination)
    return {
        "source": str(source.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(destination.relative_to(job)).replace("\\", "/"),
    }


def health(req: Dict[str, Any]) -> Dict[str, Any]:
    pdx = load_pdx(req["io_pdx_root"])
    manifest = Path(req["io_pdx_root"]).resolve() / "blender_manifest.toml"
    return {
        "blender_version": ".".join(str(part) for part in bpy.app.version),
        "blender_binary": bpy.app.binary_path,
        "io_pdx_mesh_manifest": str(manifest),
        "io_pdx_mesh_loaded": True,
        "io_pdx_mesh_operators": [
            hasattr(bpy.ops.io_pdx_mesh, "import_mesh"),
            hasattr(bpy.ops.io_pdx_mesh, "export_mesh"),
            hasattr(bpy.ops.io_pdx_mesh, "import_anim"),
            hasattr(bpy.ops.io_pdx_mesh, "export_anim"),
        ],
        "export_functions": [
            pdx["export_meshfile"].__name__,
            pdx["export_animfile"].__name__,
        ],
    }


def run(req: Dict[str, Any]) -> Dict[str, Any]:
    operation = req["operation"]
    pdx = None
    if operation not in {"health", "inspect_scene", "save_checkpoint", "sanitize_runtime_candidate", "retime_animation_action", "offset_action_root", "bake_static_mesh_transforms", "partition_static_mesh_export_batches", "attach_rigid_weapon_from_checkpoint"}:
        pdx = load_pdx(req["io_pdx_root"])
    if operation == "health":
        return health(req)
    if operation == "prepare_candidate":
        return prepare(req, pdx)
    if operation == "inspect_scene":
        return inspect(req)
    if operation == "process_textures":
        return extract_textures(req)
    if operation == "bake_static_mesh_transforms":
        return bake_static_mesh_transforms(req)
    if operation == "partition_static_mesh_export_batches":
        return partition_static_mesh_export_batches(req)
    if operation == "export_mesh":
        return export_mesh(req, pdx)
    if operation == "export_animation":
        return export_animation(req, pdx)
    if operation == "import_animation_action":
        return import_animation_action(req)
    if operation == "retime_animation_action":
        return retime_animation_action(req)
    if operation == "author_humanoid_rig":
        return author_humanoid_rig(req)
    if operation == "author_humanoid_actions":
        return author_humanoid_actions(req)
    if operation == "review_humanoid_components":
        return review_humanoid_components(req)
    if operation == "isolate_humanoid_weapon":
        return isolate_humanoid_weapon(req)
    if operation == "attach_rigid_weapon_from_checkpoint":
        return attach_rigid_weapon_from_checkpoint(req)
    if operation == "author_locomotion_action":
        return author_locomotion_action(req)
    if operation == "segment_creature_components":
        return segment_creature_components(req)
    if operation == "calibrate_creature_scale":
        return calibrate_creature_scale(req)
    if operation == "author_creature_rig":
        return author_creature_rig(req)
    if operation == "author_creature_action":
        return author_creature_action(req)
    if operation == "correct_action_grounding":
        return correct_action_grounding(req)
    if operation == "offset_action_root":
        return offset_action_root(req)
    if operation == "reimport_export":
        return reimport_export(req, pdx)
    if operation == "sanitize_runtime_candidate":
        return sanitize_runtime_candidate(req)
    if operation == "save_checkpoint":
        return save_checkpoint_operation(req)
    raise ValueError(f"Unknown worker operation: {operation}")


def main() -> int:
    args = parse_args()
    if not args.request or not args.io_pdx_root:
        print(json.dumps({"error": "worker request or io_pdx_root was not provided"}, sort_keys=True))
        return 2
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    request["io_pdx_root"] = args.io_pdx_root
    try:
        result = run(request)
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        traceback.print_exc()
        print(json.dumps({"error": str(exc), "operation": request.get("operation")}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
