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

ADAPTER_ROOT = Path(__file__).resolve().parent
if str(ADAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(ADAPTER_ROOT))

import bpy
import bmesh
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from normalization_convergence import evaluate_convergence_step


PREVIEW_LIGHT_REFERENCE_HEIGHT = 7.3518242835
CREATURE_GROUND_CONTACT_TOLERANCE_M = 0.01
CREATURE_GROUND_CONTACT_CLEARANCE_M = 0.001
LOCATOR_REGISTRY_VERSION = 1
# Blender's single-precision bone-parent round-trip accumulates ~1.05e-5 of
# matrix error in a validated small uniform-runtime-scale round-trip.
# Keep the guard tight while allowing that measured scale
# conversion error; the locator operation still records and validates the
# actual transform matrices after the round-trip.
LOCATOR_TRANSFORM_TOLERANCE = 2e-5


def shortest_quaternion_angle(left: Quaternion, right: Quaternion) -> float:
    """Return the shortest rotation angle while treating q and -q as equivalent."""

    left_normalized = left.normalized()
    right_normalized = right.normalized()
    dot = abs(float(left_normalized.dot(right_normalized)))
    return 2.0 * math.acos(max(-1.0, min(1.0, dot)))


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
        list_scene_pdx_meshes,
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
        "list_scene_pdx_meshes": list_scene_pdx_meshes,
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
    elif suffix == ".blend":
        before_actions = set(bpy.data.actions)
        with bpy.data.libraries.load(str(source), link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if name]
            data_to.actions = [name for name in data_from.actions if name]
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.scene.collection.objects.link(obj)
        if not [action for action in bpy.data.actions if action not in before_actions]:
            raise RuntimeError(f"Blender appended no actions from provider Blend source {source}")
    else:
        raise ValueError(f"Unsupported provider source format: {source.suffix}")
    imported = [obj for obj in bpy.data.objects if obj not in before]
    if not imported:
        imported = list(bpy.context.selected_objects)
    if not imported:
        raise RuntimeError(f"Blender imported no objects from {source}")
    return imported


def import_geometry_candidate(source: Path) -> List[bpy.types.Object]:
    """Import a bounded geometry source, including an audited local Blend checkpoint.

    Provider animation/model inputs remain limited to FBX and glTF through
    ``import_candidate``.  A dual-source geometry handoff may additionally use
    a job-root-local ``.blend`` checkpoint so an already audited runtime mesh
    can receive weights from a separately licensed source rig without being
    round-tripped through an untracked interchange export.
    """

    if source.suffix.lower() != ".blend":
        return import_candidate(source)

    before = set(bpy.data.objects)
    with bpy.data.libraries.load(str(source), link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name]
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.scene.collection.objects.link(obj)
    imported = [obj for obj in bpy.data.objects if obj not in before]
    if not imported:
        raise RuntimeError(f"Blender appended no objects from geometry checkpoint {source}")
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
    source_meshes: List[bpy.types.Object],
    target_mesh: bpy.types.Object,
    target_armature: bpy.types.Object,
    weight_mode: str = "four_nearest",
) -> Dict[str, Any]:
    """Transfer rest-pose weights from the provider rig mesh to a closed mesh candidate."""

    if weight_mode not in {
        "four_nearest",
        "nearest_face_interpolated",
        "automatic_bone_heat",
        "bone_distance",
    }:
        raise ValueError(
            "geometry_weight_mode must be four_nearest, nearest_face_interpolated, "
            "automatic_bone_heat, or bone_distance."
        )

    if not source_meshes:
        raise RuntimeError("Dual-source rig transfer requires at least one source rig mesh.")
    source_minimum, source_maximum = world_bounds(source_meshes)
    target_minimum, target_maximum = world_bounds([target_mesh])
    source_height = source_maximum.z - source_minimum.z
    target_height = target_maximum.z - target_minimum.z
    if source_height <= 0 or target_height <= 0:
        raise RuntimeError("Dual-source rig transfer requires positive source and target heights.")

    target_world = target_mesh.matrix_world.copy()
    target_mesh.parent = None
    target_mesh.matrix_world = target_world
    for modifier in list(target_mesh.modifiers):
        if modifier.type == "ARMATURE":
            target_mesh.modifiers.remove(modifier)

    target_mesh.scale *= source_height / target_height
    bpy.context.view_layer.update()
    target_minimum, target_maximum = world_bounds([target_mesh])
    source_center = (source_minimum + source_maximum) * 0.5
    target_center = (target_minimum + target_maximum) * 0.5
    target_mesh.location += source_center - target_center
    bpy.context.view_layer.update()

    for group in list(target_mesh.vertex_groups):
        target_mesh.vertex_groups.remove(group)
    transferred_vertices = 0
    nearest_face_audit: Optional[Dict[str, Any]] = None
    if weight_mode in {"four_nearest", "nearest_face_interpolated"}:
        source_group_names = sorted({group.name for mesh in source_meshes for group in mesh.vertex_groups})
        target_groups = {name: target_mesh.vertex_groups.new(name=name) for name in source_group_names}
        if not target_groups:
            raise RuntimeError("Dual-source rig transfer found no provider vertex groups.")
        source_vertices = [(mesh, vertex) for mesh in source_meshes for vertex in mesh.data.vertices]
        if weight_mode == "four_nearest":
            tree = KDTree(len(source_vertices))
            for source_index, (mesh, vertex) in enumerate(source_vertices):
                tree.insert(mesh.matrix_world @ vertex.co, source_index)
            tree.balance()
            for vertex in target_mesh.data.vertices:
                nearest = tree.find_n(target_mesh.matrix_world @ vertex.co, 4)
                accumulated: Dict[str, float] = {}
                for _, source_index, distance in nearest:
                    influence = 1.0 / max(distance, 1e-6)
                    source_mesh, source_vertex = source_vertices[source_index]
                    for source_group in source_mesh.vertex_groups:
                        try:
                            weight = source_group.weight(source_vertex.index)
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
        else:
            world_coordinates: List[Vector] = []
            source_vertex_refs: List[tuple[bpy.types.Object, int]] = []
            source_triangles: List[tuple[int, int, int]] = []
            for mesh in source_meshes:
                vertex_offset = len(world_coordinates)
                world_coordinates.extend(mesh.matrix_world @ vertex.co for vertex in mesh.data.vertices)
                source_vertex_refs.extend((mesh, vertex.index) for vertex in mesh.data.vertices)
                for polygon in mesh.data.polygons:
                    polygon_vertices = list(polygon.vertices)
                    for triangle_index in range(1, len(polygon_vertices) - 1):
                        source_triangles.append(
                            (
                                vertex_offset + polygon_vertices[0],
                                vertex_offset + polygon_vertices[triangle_index],
                                vertex_offset + polygon_vertices[triangle_index + 1],
                            )
                        )
            if not source_triangles:
                raise RuntimeError("Nearest-face weight transfer found no provider triangles.")
            tree = BVHTree.FromPolygons(world_coordinates, source_triangles, all_triangles=True)
            if tree is None:
                raise RuntimeError("Nearest-face weight transfer could not construct the provider triangle BVH.")
            projection_distances: List[float] = []
            barycentric_tolerance = 1e-5
            for vertex in target_mesh.data.vertices:
                nearest = tree.find_nearest(target_mesh.matrix_world @ vertex.co)
                if nearest is None or nearest[0] is None or nearest[2] is None or nearest[3] is None:
                    raise RuntimeError(
                        f"Nearest-face weight transfer found no provider surface for target vertex {vertex.index}."
                    )
                closest, _, triangle_index, projection_distance = nearest
                triangle = source_triangles[triangle_index]
                point_a, point_b, point_c = (world_coordinates[index] for index in triangle)
                edge_ab = point_b - point_a
                edge_ac = point_c - point_a
                point_offset = closest - point_a
                dot_ab_ab = edge_ab.dot(edge_ab)
                dot_ab_ac = edge_ab.dot(edge_ac)
                dot_ac_ac = edge_ac.dot(edge_ac)
                dot_offset_ab = point_offset.dot(edge_ab)
                dot_offset_ac = point_offset.dot(edge_ac)
                denominator = dot_ab_ab * dot_ac_ac - dot_ab_ac * dot_ab_ac
                if abs(denominator) <= 1e-12:
                    raise RuntimeError(
                        f"Nearest-face weight transfer encountered degenerate provider triangle {triangle_index}."
                    )
                weight_b = (dot_ac_ac * dot_offset_ab - dot_ab_ac * dot_offset_ac) / denominator
                weight_c = (dot_ab_ab * dot_offset_ac - dot_ab_ac * dot_offset_ab) / denominator
                weight_a = 1.0 - weight_b - weight_c
                raw_barycentric = tuple(float(value) for value in (weight_a, weight_b, weight_c))
                if any(
                    not math.isfinite(value)
                    or value < -barycentric_tolerance
                    or value > 1.0 + barycentric_tolerance
                    for value in raw_barycentric
                ):
                    raise RuntimeError(
                        "Nearest-face weight transfer produced invalid barycentric coordinates: "
                        + json.dumps(
                            {
                                "target_vertex": vertex.index,
                                "source_triangle": int(triangle_index),
                                "barycentric": list(raw_barycentric),
                            },
                            sort_keys=True,
                        )
                    )
                clamped = [max(0.0, min(1.0, value)) for value in raw_barycentric]
                clamped_total = sum(clamped)
                if clamped_total <= 1e-8:
                    raise RuntimeError(
                        f"Nearest-face weight transfer produced zero barycentric mass for target vertex {vertex.index}."
                    )
                barycentric = tuple(value / clamped_total for value in clamped)
                accumulated: Dict[str, float] = {}
                for source_index, vertex_weight in zip(triangle, barycentric):
                    source_mesh, source_vertex_index = source_vertex_refs[source_index]
                    for source_group in source_mesh.vertex_groups:
                        try:
                            weight = source_group.weight(source_vertex_index)
                        except RuntimeError:
                            continue
                        if weight > 0:
                            accumulated[source_group.name] = accumulated.get(source_group.name, 0.0) + weight * vertex_weight
                total = sum(accumulated.values())
                if total <= 1e-8:
                    raise RuntimeError(
                        f"Nearest-face weight transfer found zero provider weight for target vertex {vertex.index}."
                    )
                for name, weight in accumulated.items():
                    target_groups[name].add([vertex.index], weight / total, "REPLACE")
                projection_distances.append(float(projection_distance))
                transferred_vertices += 1
            if transferred_vertices != len(target_mesh.data.vertices):
                raise RuntimeError(
                    "Nearest-face weight transfer did not bind every target vertex: "
                    f"{transferred_vertices}/{len(target_mesh.data.vertices)}."
                )
            nearest_face_audit = {
                "source_triangles": len(source_triangles),
                "projection_distance_max": max(projection_distances),
                "projection_distance_mean": sum(projection_distances) / len(projection_distances),
                "barycentric_tolerance": barycentric_tolerance,
                "failed_vertices": 0,
            }
    elif weight_mode == "bone_distance":
        deform_bones = [bone for bone in target_armature.data.bones if bone.use_deform]
        if not deform_bones:
            raise RuntimeError("Provider armature exposes no deform bones for distance weighting.")
        target_groups = {
            bone.name: target_mesh.vertex_groups.new(name=bone.name)
            for bone in deform_bones
        }
        bone_segments = []
        for bone in deform_bones:
            head = target_armature.matrix_world @ bone.head_local
            tail = target_armature.matrix_world @ bone.tail_local
            segment = tail - head
            length_squared = max(float(segment.length_squared), 1e-12)
            bone_segments.append((bone.name, head, segment, length_squared))
        for vertex in target_mesh.data.vertices:
            position = target_mesh.matrix_world @ vertex.co
            distances = []
            for bone_name, head, segment, length_squared in bone_segments:
                projection = max(0.0, min(1.0, float((position - head).dot(segment)) / length_squared))
                closest = head + segment * projection
                distances.append((float((position - closest).length), bone_name))
            nearest = sorted(distances, key=lambda item: (item[0], item[1]))[:4]
            weighted = [(bone_name, 1.0 / max(distance * distance, 1e-8)) for distance, bone_name in nearest]
            total = sum(weight for _, weight in weighted)
            for bone_name, weight in weighted:
                target_groups[bone_name].add([vertex.index], weight / total, "REPLACE")
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
    if weight_mode == "automatic_bone_heat":
        bpy.ops.object.select_all(action="DESELECT")
        target_mesh.select_set(True)
        target_armature.select_set(True)
        bpy.context.view_layer.objects.active = target_armature
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
        target_mesh.matrix_world = world_matrix
        for vertex in target_mesh.data.vertices:
            influences = sorted(
                ((item.group, float(item.weight)) for item in vertex.groups if item.weight > 0.0),
                key=lambda item: item[1],
                reverse=True,
            )[:4]
            keep = {group_index for group_index, _ in influences}
            total = sum(weight for _, weight in influences)
            for group in target_mesh.vertex_groups:
                if group.index not in keep:
                    group.remove([vertex.index])
            if total > 0.0:
                for group_index, weight in influences:
                    target_mesh.vertex_groups[group_index].add([vertex.index], weight / total, "REPLACE")
                transferred_vertices += 1
        modifier = next(
            (item for item in target_mesh.modifiers if item.type == "ARMATURE" and item.object is target_armature),
            None,
        )
        if modifier is None or transferred_vertices != len(target_mesh.data.vertices):
            raise RuntimeError(
                "Automatic bone-heat binding did not produce a complete armature binding for every target vertex."
            )
    else:
        target_mesh.parent = target_armature
        target_mesh.parent_type = "OBJECT"
        target_mesh.matrix_world = world_matrix
        modifier = target_mesh.modifiers.new("HOI4_RIG_TRANSFER", type="ARMATURE")
        modifier.object = target_armature
    modifier.use_deform_preserve_volume = True
    return {
        "method": (
            "Blender automatic bone-heat weights clamped and normalized to four influences"
            if weight_mode == "automatic_bone_heat"
            else (
                "four-nearest provider deform-bone segment inverse-square distance weights"
                if weight_mode == "bone_distance"
                else (
                    "nearest provider triangle barycentric-interpolated weight transfer"
                    if weight_mode == "nearest_face_interpolated"
                    else "four-nearest-provider-vertex inverse-distance weight transfer"
                )
            )
        ),
        "source_meshes": sorted(mesh.name for mesh in source_meshes),
        "target_mesh": target_mesh.name,
        "armature": target_armature.name,
        "source_vertices": sum(len(mesh.data.vertices) for mesh in source_meshes),
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
        "nearest_face_audit": nearest_face_audit,
    }


def prepare_dual_source_base_rig(target_armature: bpy.types.Object) -> Dict[str, Any]:
    """Reset only the working rig to an action-free rest base before normalization."""

    if target_armature.type != "ARMATURE" or not target_armature.get("hoi4_working", False):
        raise RuntimeError("Dual-source base-rig mode requires the explicit working armature.")
    detached_action = None
    detached_nla_tracks = 0
    if target_armature.animation_data is not None:
        active = target_armature.animation_data.action
        detached_action = active.name if active is not None else None
        detached_nla_tracks = len(target_armature.animation_data.nla_tracks)
        target_armature.animation_data_clear()
    for pose_bone in target_armature.pose.bones:
        pose_bone.matrix_basis = Matrix.Identity(4)
    target_armature.data.pose_position = "REST"
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    target_armature.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    removed_unused_working_actions = []
    for action in list(bpy.data.actions):
        if action.users == 0 and "WORKING" in action.name:
            removed_unused_working_actions.append(action.name)
            bpy.data.actions.remove(action)
    remaining_working_actions = []
    if target_armature.animation_data is not None:
        if target_armature.animation_data.action is not None:
            remaining_working_actions.append(target_armature.animation_data.action.name)
        remaining_working_actions.extend(track.name for track in target_armature.animation_data.nla_tracks)
    if remaining_working_actions:
        raise RuntimeError(
            "Dual-source base-rig mode retained working animation data: "
            + json.dumps(sorted(remaining_working_actions))
        )
    return {
        "policy": "working_armature_action_clear_and_identity_rest_pose",
        "detached_working_action": detached_action,
        "detached_working_nla_tracks": detached_nla_tracks,
        "removed_unused_working_actions": sorted(removed_unused_working_actions),
        "working_actions": [],
        "pose_bones_reset": len(target_armature.pose.bones),
        "provider_source_actions_preserved": sorted(
            action.name for action in bpy.data.actions if "WORKING" not in action.name
        ),
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


def _export_checkpoint_action_snapshot(action: bpy.types.Action) -> List[Dict[str, Any]]:
    """Capture every keyed value and handle used by the export-coordinate drift guard."""

    records = []
    for fcurve, _ in action_fcurves(action):
        records.append(
            {
                "data_path": fcurve.data_path,
                "array_index": int(fcurve.array_index),
                "keys": [
                    {
                        "co": [float(value) for value in key.co],
                        "handle_left": [float(value) for value in key.handle_left],
                        "handle_right": [float(value) for value in key.handle_right],
                        "interpolation": key.interpolation,
                    }
                    for key in fcurve.keyframe_points
                ],
            }
        )
    return sorted(records, key=lambda item: (item["data_path"], item["array_index"]))


def _export_checkpoint_material_snapshot() -> Dict[str, Any]:
    """Capture working material and image bindings without modifying them."""

    return {
        obj.name: [
            {
                "material": material.name if material is not None else None,
                "images": sorted(
                    [
                        {
                            "name": node.image.name,
                            "filepath": bpy.path.abspath(node.image.filepath),
                        }
                        for node in material.node_tree.nodes
                        if material is not None
                        and material.use_nodes
                        and material.node_tree is not None
                        and node.type == "TEX_IMAGE"
                        and node.image is not None
                    ],
                    key=lambda item: (item["name"], item["filepath"]),
                )
                if material is not None
                else [],
            }
            for material in obj.data.materials
        ]
        for obj in mesh_objects()
    }


def _export_checkpoint_protected_snapshot() -> Dict[str, Any]:
    """Prove that protected source/reference objects remain unchanged."""

    return {
        obj.name: {
            "type": obj.type,
            "data": obj.data.name if obj.data is not None else None,
            "transform": object_transform_record(obj),
        }
        for obj in bpy.context.scene.objects
        if not obj.get("hoi4_working", False)
    }


def _validate_export_coordinate_drift(
    *,
    geometry_before: Dict[str, Any],
    bounds_before: Dict[str, Any],
    mesh_matrices_before: Dict[str, List[List[float]]],
    materials_before: Dict[str, Any],
    protected_before: Dict[str, Any],
    bones_before: Dict[str, Dict[str, Any]],
    action_before: List[Dict[str, Any]],
    action_after: List[Dict[str, Any]],
    source_scale: float,
    tolerance: float = 1e-5,
) -> Dict[str, Any]:
    """Reject any change outside the existing PDX coordinate conversion."""

    geometry_after = geometry_metrics()
    topology_keys = (
        "objects", "vertices", "polygons", "triangles", "loose_boundary_edges",
        "non_manifold_edges", "degenerate_faces", "zero_length_normals", "uv_layers",
    )
    topology_drift = {
        key: {"before": geometry_before[key], "after": geometry_after[key]}
        for key in topology_keys
        if geometry_before[key] != geometry_after[key]
    }
    bounds_after = bounds_record(mesh_objects())
    bounds_delta = max(
        abs(float(after) - float(before))
        for key in ("minimum", "maximum", "dimensions")
        for before, after in zip(bounds_before[key], bounds_after[key])
    )
    mesh_matrix_delta = max(
        (
            abs(float(after) - float(before))
            for obj in mesh_objects()
            for before_row, after_row in zip(mesh_matrices_before[obj.name], obj.matrix_world)
            for before, after in zip(before_row, after_row)
        ),
        default=0.0,
    )
    materials_after = _export_checkpoint_material_snapshot()
    protected_after = _export_checkpoint_protected_snapshot()

    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError("Export-coordinate checkpoint lost its unique working armature.")
    rig = rigs[0]
    bones_after = {
        bone.name: {
            "parent": bone.parent.name if bone.parent else None,
            "head": [float(value) for value in bone.head_local],
            "tail": [float(value) for value in bone.tail_local],
        }
        for bone in rig.data.bones
    }
    bone_failures = []
    if set(bones_before) != set(bones_after):
        bone_failures.append("bone-name set changed")
    for name, before in bones_before.items():
        after = bones_after.get(name)
        if after is None:
            continue
        if before["parent"] != after["parent"]:
            bone_failures.append(f"{name}: parent changed")
        expected = [float(value) * source_scale for value in (*before["head"], *before["tail"])]
        observed = [float(value) for value in (*after["head"], *after["tail"])]
        if max(abs(left - right) for left, right in zip(expected, observed)) > tolerance:
            bone_failures.append(f"{name}: rest coordinates drifted outside scale conversion")

    action_failures = []
    if len(action_before) != len(action_after):
        action_failures.append("F-curve count changed")
    for before, after in zip(action_before, action_after):
        if (before["data_path"], before["array_index"]) != (after["data_path"], after["array_index"]):
            action_failures.append("F-curve identity/order changed")
            continue
        if len(before["keys"]) != len(after["keys"]):
            action_failures.append(f"{before['data_path']}[{before['array_index']}]: key count changed")
            continue
        location_curve = "pose.bones[" in before["data_path"] and ".location" in before["data_path"]
        factor = source_scale if location_curve else 1.0
        for index, (left, right) in enumerate(zip(before["keys"], after["keys"])):
            if left["interpolation"] != right["interpolation"]:
                action_failures.append(f"{before['data_path']}[{before['array_index']}]: interpolation changed")
                break
            expected = [
                left["co"][0], left["co"][1] * factor,
                left["handle_left"][0], left["handle_left"][1] * factor,
                left["handle_right"][0], left["handle_right"][1] * factor,
            ]
            observed = [*right["co"], *right["handle_left"], *right["handle_right"]]
            if max(abs(float(a) - float(b)) for a, b in zip(expected, observed)) > tolerance:
                action_failures.append(
                    f"{before['data_path']}[{before['array_index']}]: key {index} drifted"
                )
                break

    failures = []
    if topology_drift:
        failures.append("topology/UV drift")
    if bounds_delta > tolerance:
        failures.append(f"working bounds drift {bounds_delta}")
    if mesh_matrix_delta > tolerance:
        failures.append(f"working mesh matrix drift {mesh_matrix_delta}")
    if materials_before != materials_after:
        failures.append("material/image binding drift")
    if protected_before != protected_after:
        failures.append("protected source/reference drift")
    failures.extend(bone_failures)
    failures.extend(action_failures)
    if failures:
        raise RuntimeError("Export-coordinate checkpoint drift validation failed: " + "; ".join(failures))
    return {
        "status": "pass",
        "tolerance": tolerance,
        "topology_drift": topology_drift,
        "bounds_delta": bounds_delta,
        "mesh_matrix_delta": mesh_matrix_delta,
        "materials_preserved": True,
        "protected_sources_preserved": True,
        "bones_preserved_under_uniform_coordinate_conversion": len(bones_after),
        "action_fcurves_preserved_under_location_coordinate_conversion": len(action_after),
        "geometry_after": geometry_after,
        "bounds_after": bounds_after,
    }


def prepare_export_coordinate_checkpoint(req: Dict[str, Any]) -> Dict[str, Any]:
    """Save an accepted action in the exact coordinate system used by PDX export."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    requested_action = explicit_action_name(payload.get("action_name"), "action_name")
    requested_armature = explicit_safe_name(payload.get("target_armature_name"), "target_armature_name")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rig, action, frame_start, frame_end = select_armature_and_action(requested_action)
    if rig.name != requested_armature:
        raise RuntimeError(
            f"Export-coordinate checkpoint requires target armature {requested_armature}, found {rig.name}."
        )
    action_source = action_provenance(action)
    geometry_before = geometry_metrics()
    bounds_before = bounds_record(mesh_objects())
    mesh_matrices_before = {
        obj.name: [[float(value) for value in row] for row in obj.matrix_world]
        for obj in mesh_objects()
    }
    materials_before = _export_checkpoint_material_snapshot()
    protected_before = _export_checkpoint_protected_snapshot()
    bones_before = {
        bone.name: {
            "parent": bone.parent.name if bone.parent else None,
            "head": [float(value) for value in bone.head_local],
            "tail": [float(value) for value in bone.tail_local],
        }
        for bone in rig.data.bones
    }
    action_before = _export_checkpoint_action_snapshot(action)
    conversion = prepare_pdx_export_transforms()
    action_after = _export_checkpoint_action_snapshot(action)
    drift = _validate_export_coordinate_drift(
        geometry_before=geometry_before,
        bounds_before=bounds_before,
        mesh_matrices_before=mesh_matrices_before,
        materials_before=materials_before,
        protected_before=protected_before,
        bones_before=bones_before,
        action_before=action_before,
        action_after=action_after,
        source_scale=float(conversion["armature_data_scale_factor"]),
    )
    save_blend(checkpoint)
    bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
    reopened_rig, reopened_action, reopened_start, reopened_end = select_armature_and_action(requested_action)
    if reopened_rig.name != requested_armature or (reopened_start, reopened_end) != (frame_start, frame_end):
        raise RuntimeError("Export-coordinate checkpoint changed target armature or action frame range after reopen.")
    reopened_drift = _validate_export_coordinate_drift(
        geometry_before=geometry_before,
        bounds_before=bounds_before,
        mesh_matrices_before=mesh_matrices_before,
        materials_before=materials_before,
        protected_before=protected_before,
        bones_before=bones_before,
        action_before=action_before,
        action_after=_export_checkpoint_action_snapshot(reopened_action),
        source_scale=float(conversion["armature_data_scale_factor"]),
    )
    if action_provenance(reopened_action) != action_source:
        raise RuntimeError("Export-coordinate checkpoint changed verified action provenance after reopen.")
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "action": reopened_action.name,
        "action_provenance": action_source,
        "target_armature": reopened_rig.name,
        "frame_start": reopened_start,
        "frame_end": reopened_end,
        "fps": bpy.context.scene.render.fps,
        "conversion": conversion,
        "drift_guard_before_save": drift,
        "drift_guard_after_reopen": reopened_drift,
        "policy": "existing_pdx_export_coordinate_conversion_checkpoint_only",
        "body_motion_authored": False,
        "warnings": [],
    }
    report = job / "blender" / "reports" / f"export_coordinate_checkpoint_{safe_name(reopened_action.name)}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


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
                node.label = f"Chaos Redux {role} texture"
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


def evaluated_contact_bounds(
    objects: Iterable[bpy.types.Object],
    excluded_bones: Iterable[str],
) -> Tuple[Vector, Vector]:
    """Measure evaluated bounds while ignoring vertices dominated by excluded bones."""

    excluded = {str(name) for name in excluded_bones}
    if not excluded:
        return evaluated_world_bounds(objects)
    corners: List[Vector] = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            if len(mesh.vertices) != len(obj.data.vertices):
                raise RuntimeError(
                    f"Contact-filtered grounding requires topology-preserving deformation on {obj.name}."
                )
            group_names = {group.index: group.name for group in obj.vertex_groups}
            for source_vertex, evaluated_vertex in zip(obj.data.vertices, mesh.vertices):
                weighted_groups = [
                    (float(assignment.weight), group_names.get(assignment.group, ""))
                    for assignment in source_vertex.groups
                    if assignment.weight > 0.0
                ]
                dominant_bone = max(weighted_groups, default=(0.0, ""))[1]
                if dominant_bone in excluded:
                    continue
                corners.append(evaluated.matrix_world @ evaluated_vertex.co)
        finally:
            evaluated.to_mesh_clear()
    if not corners:
        raise RuntimeError("Contact-filtered grounding excluded every working mesh vertex.")
    minimum = Vector((min(item.x for item in corners), min(item.y for item in corners), min(item.z for item in corners)))
    maximum = Vector((max(item.x for item in corners), max(item.y for item in corners), max(item.z for item in corners)))
    return minimum, maximum


def root_objects(objects: List[bpy.types.Object]) -> List[bpy.types.Object]:
    object_set = set(objects)
    return [obj for obj in objects if obj.parent not in object_set]


def is_humanoid_asset_kind(asset_kind: str) -> bool:
    """Recognize both legacy and repository job-profile humanoid identifiers."""

    return asset_kind in {"humanoid", "humanoid_unit"}


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


def verify_saved_normalization(checkpoint: Path, target_height: float) -> Dict[str, Any]:
    """Reopen a checkpoint and fail if its measured height differs from its report."""

    bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
    persisted_geometry = geometry_metrics()
    persisted_height = float(persisted_geometry["dimensions"][2])
    tolerance = max(1e-5, abs(target_height) * 1e-5)
    height_delta = persisted_height - target_height
    if abs(height_delta) > tolerance:
        raise RuntimeError(
            "Saved normalization checkpoint does not preserve the requested mesh height: "
            f"target={target_height}, persisted={persisted_height}, delta={height_delta}."
        )
    return {
        "policy": "save_reopen_and_remeasure_working_world_bounds",
        "checkpoint": str(checkpoint),
        "target_height_m": target_height,
        "persisted_height_m": persisted_height,
        "height_delta_m": height_delta,
        "tolerance_m": tolerance,
        "geometry": persisted_geometry,
        "armatures": [
            {
                "name": rig.name,
                "world_scale": list(rig.matrix_world.to_scale()),
            }
            for rig in armatures()
        ],
    }


def stabilize_saved_normalization(
    checkpoint: Path,
    target_height: float,
) -> Dict[str, Any]:
    """Strictly renormalize a prepared candidate after dependency-graph reload."""

    corrections = []
    previous_delta = None
    max_corrections = 8
    for corrections_applied in range(max_corrections + 1):
        bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
        persisted_geometry = geometry_metrics()
        persisted_height = float(persisted_geometry["dimensions"][2])
        tolerance = max(1e-5, abs(target_height) * 1e-5)
        step = evaluate_convergence_step(
            target=target_height,
            persisted=persisted_height,
            tolerance=tolerance,
            previous_delta=previous_delta,
            corrections_applied=corrections_applied,
            max_corrections=max_corrections,
        )
        record = {
            "pass": corrections_applied,
            "target_height_m": target_height,
            "persisted_height_m": persisted_height,
            "height_delta_m": step["delta"],
            "correction_factor": step["correction_factor"],
        }
        corrections.append(record)
        if step["status"] == "accepted":
            return {
                "policy": "save_reopen_monotonic_convergence_and_strict_reverify",
                "checkpoint": str(checkpoint),
                "target_height_m": target_height,
                "persisted_height_m": persisted_height,
                "height_delta_m": step["delta"],
                "tolerance_m": tolerance,
                "geometry": persisted_geometry,
                "armatures": [
                    {"name": rig.name, "world_scale": list(rig.matrix_world.to_scale())}
                    for rig in armatures()
                ],
                "dependency_graph_corrections": corrections,
            }
        correction = normalize_geometry(target_height)
        record["normalization"] = correction
        save_blend(checkpoint)
        previous_delta = float(step["delta"])
    raise RuntimeError("Normalization convergence exhausted its correction cap.")


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


def validate_evaluated_frames(requested_frames, start, end):
    if requested_frames is None:
        return sorted({int(math.floor(start)), int(math.ceil((start + end) * 0.5)), int(math.ceil(end))})
    if not isinstance(requested_frames, list) or not 1 <= len(requested_frames) <= 241:
        raise ValueError("evaluated_frames requires 1..241 explicit frames.")
    if any(type(frame) is not int or frame < math.floor(start) or frame > math.ceil(end) for frame in requested_frames):
        raise ValueError("evaluated_frames must be integers within the selected action range.")
    if len(set(requested_frames)) != len(requested_frames):
        raise ValueError("evaluated_frames must not repeat frames.")
    return sorted(requested_frames)


def evaluated_action_metrics(selected_action_name="", requested_frames=None, target_armature_name="") -> List[Dict[str, Any]]:
    """Read evaluated working-mesh bounds for explicit action/frame selection."""
    if requested_frames is not None and not selected_action_name:
        raise ValueError("evaluated_frames requires an explicit selected action_name.")
    meshes = mesh_objects()
    rigs = [rig for rig in armatures() if not target_armature_name or rig.name == target_armature_name]
    if not meshes or not rigs:
        return []
    scene = bpy.context.scene
    original_frame = scene.frame_current
    original_bindings = []
    records = []
    try:
        for rig in rigs:
            rig.animation_data_create()
            original_bindings.append((rig, rig.animation_data.action, getattr(rig.animation_data, "action_slot", None)))
            if selected_action_name:
                action = bpy.data.actions.get(selected_action_name)
                if action is None: raise ValueError("Selected evaluated action does not exist.")
                actions = [action]
            else:
                actions = [action for action in bpy.data.actions if (("WORKING" in action.name and action.name.startswith("Armature|")) or action.name.startswith("creature_") or action.get("hoi4_animation_source_kind"))]
            for action in actions:
                rig.animation_data.action = action
                frames = validate_evaluated_frames(requested_frames, *action.frame_range)
                frame_records = []
                for frame in frames:
                    scene.frame_set(frame)
                    bpy.context.view_layer.update()
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    corners = []
                    mesh_bounds = []
                    for obj in meshes:
                        evaluated = obj.evaluated_get(depsgraph)
                        evaluated_mesh = evaluated.to_mesh()
                        try:
                            points = [evaluated.matrix_world @ vertex.co for vertex in evaluated_mesh.vertices]
                            corners.extend(points)
                            if points:
                                mesh_bounds.append({"name": obj.name, "bounds_min": [min(p[i] for p in points) for i in range(3)], "bounds_max": [max(p[i] for p in points) for i in range(3)]})
                        finally:
                            evaluated.to_mesh_clear()
                    if corners:
                        minimum = Vector(tuple(min(p[i] for p in corners) for i in range(3)))
                        maximum = Vector(tuple(max(p[i] for p in corners) for i in range(3)))
                        frame_records.append({"frame": frame, "bounds_min": list(minimum), "bounds_max": list(maximum), "dimensions": list(maximum-minimum), "meshes": mesh_bounds})
                records.append({"armature": rig.name, "action": action.name, "frames": frame_records})
    finally:
        for rig, action, slot in original_bindings:
            rig.animation_data.action = action
            if action is not None and slot is not None: rig.animation_data.action_slot = slot
        scene.frame_set(original_frame)
        bpy.context.view_layer.update()
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
                weight = float(assignment.weight)
                if weight <= 0.0:
                    continue
                weights.append(weight)
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


def sanitize_working_weights(
    *,
    preserve_skeleton_metadata: bool = False,
    max_influences_per_vertex: int = 4,
) -> Dict[str, Any]:
    """Keep PDX-compatible skinning influences without altering provider geometry."""

    if max_influences_per_vertex not in {1, 2, 3, 4}:
        raise ValueError("max_influences_per_vertex must be an integer from 1 through 4.")

    records: List[Dict[str, Any]] = []
    for obj in mesh_objects():
        armature_modifiers = [
            modifier
            for modifier in obj.modifiers
            if modifier.type == "ARMATURE" and modifier.object is not None
        ]
        named_transfer_modifiers = [
            modifier for modifier in armature_modifiers
            if modifier.name == "HOI4_RIG_TRANSFER"
        ]
        if len(named_transfer_modifiers) == 1:
            armature_modifier = named_transfer_modifiers[0]
        elif len(armature_modifiers) == 1:
            armature_modifier = armature_modifiers[0]
        elif armature_modifiers:
            raise RuntimeError(
                f"Weight sanitization requires one explicit working armature modifier on {obj.name}; "
                f"found {[modifier.name for modifier in armature_modifiers]}."
            )
        else:
            armature_modifier = None
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

        over_cap_before = 0
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
                else:
                    group.remove([vertex.index])
                    removed_influences += 1

            if len(assignments) > max_influences_per_vertex:
                over_cap_before += 1
                kept = sorted(assignments, key=lambda item: (-item[1], item[0].name))[:max_influences_per_vertex]
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

        weighted_bone_names = {
            obj.vertex_groups[assignment.group].name
            for vertex in obj.data.vertices
            for assignment in vertex.groups
            if assignment.weight > 0.0
            and obj.vertex_groups[assignment.group].name in bone_names
        }
        required_export_bones = set(weighted_bone_names)
        for bone_name in list(weighted_bone_names):
            bone = armature.data.bones.get(bone_name)
            while bone is not None:
                required_export_bones.add(bone.name)
                bone = bone.parent
        unignored_export_bones = []
        if not preserve_skeleton_metadata:
            for bone_name in sorted(required_export_bones):
                bone = armature.data.bones.get(bone_name)
                if bone is not None and bone.get("pdxIgnoreJoint"):
                    bone["pdxIgnoreJoint"] = False
                    unignored_export_bones.append(bone_name)

        records.append(
            {
                "object": obj.name,
                "armature": armature.name,
                "root_bone": root_bone.name,
                "vertices_over_four_before": over_cap_before if max_influences_per_vertex == 4 else 0,
                "vertices_over_cap_before": over_cap_before,
                "zero_weight_vertices_before": zero_before,
                "removed_influences": removed_influences,
                "normalized_vertices": normalized_vertices,
                "zero_weight_vertices_repaired": zero_weight_repaired,
                "weighted_bones": sorted(weighted_bone_names),
                "required_export_bones": sorted(required_export_bones),
                "unignored_export_bones": unignored_export_bones,
            }
        )
    return {
        "policy": (
            "keep_four_strongest_bone_influences_and_renormalize"
            if max_influences_per_vertex == 4
            else "keep_bounded_strongest_bone_influences_and_renormalize"
        ),
        "max_influences_per_vertex": max_influences_per_vertex,
        "skeleton_metadata_policy": (
            "preserve_checkpoint_skeleton_metadata"
            if preserve_skeleton_metadata
            else "unignore_required_export_bones"
        ),
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




def all_image_nodes() -> List[Tuple[bpy.types.Material, bpy.types.Image]]:
    """Return local node images for bounded reimport texture relinking.

    PDX reimport creates local materials without the source scene's
    ``hoi4_pdx_shader`` tag.  Keep the normal source-scene selector strict,
    but let the explicit texture-relink operation see those reimport nodes.
    """
    values: List[Tuple[bpy.types.Material, bpy.types.Image]] = []
    seen = set()
    for material in bpy.data.materials:
        if material.library or material.override_library or not material.use_nodes:
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


def validate_preview_region(region, resolution):
    if type(resolution) is not int or not 128 <= resolution <= 2048:
        raise ValueError("Preview resolution must be an integer from128 to2048.")
    if region is None:
        return None
    if not isinstance(region,dict) or set(region)!={"min","max"}:
        raise ValueError("Preview region requires exact min/max world bounds.")
    for values in region.values():
        if not isinstance(values,list) or len(values)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>10000 for v in values):
            raise ValueError("Preview world bounds must be finite bounded numeric triples.")
    if any(a>=b for a,b in zip(region['min'],region['max'])):
        raise ValueError("Preview world bounds must have positive extent on every axis.")
    return region


def render_previews(
    job: Path,
    runtime_stem: str,
    view_names: List[str] | None = None,
    *,
    working_only: bool = True,
    preview_region: Dict[str, Any] | None = None,
    preview_resolution: int = 512,
) -> List[str]:
    validate_preview_region(preview_region,preview_resolution)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = preview_resolution
    scene.render.resolution_y = preview_resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.015, 0.02, 0.03)

    meshes = mesh_objects(working_only=working_only)
    if not meshes:
        object_class = "working" if working_only else "imported runtime-proof"
        raise RuntimeError(f"Preview rendering found no {object_class} mesh objects.")
    # Pose-dependent preview framing only; source normalization retains raw bounds.
    bpy.context.view_layer.update()
    minimum, maximum = evaluated_world_bounds(meshes)
    ground_z = minimum.z
    if preview_region is not None:
        minimum,maximum=Vector(preview_region["min"]),Vector(preview_region["max"])
    center = (minimum + maximum) * 0.5
    dimensions = maximum - minimum
    object_height = max(float(max(dimensions)), 0.1)
    ground_extent = max(8.0, float(max(dimensions.x, dimensions.y)) * 2.0)

    evidence_collection = new_collection("QA_EVIDENCE")
    ground_mesh = bpy.data.meshes.new("QA_Ground_Mesh")
    ground_mesh.from_pydata(
        [
            (-ground_extent, -ground_extent, ground_z),
            (ground_extent, -ground_extent, ground_z),
            (ground_extent, ground_extent, ground_z),
            (-ground_extent, ground_extent, ground_z),
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
        light.location = center + Vector(location)
        camera_point_at(light, center)
        lights.append(light)

    camera_data = bpy.data.cameras.new("QA_Camera")
    camera = bpy.data.objects.new("QA_Camera", camera_data)
    evidence_collection.objects.link(camera)
    scene.camera = camera
    camera_data.lens = 55

    # Frame the whole object regardless of whether it is a 1.5 m prop or a
    # vanilla-calibrated 7.35-unit source mesh.
    # Fit a sphere enclosing actual evaluated bounds using the real camera FOV.
    # This also contains horizontal death poses and all selected view directions.
    preview_angle = min(camera_data.angle_x,camera_data.angle_y)
    fit_distance = max(float(dimensions.length)*0.5/(math.sin(preview_angle*0.5)*0.78),0.1)

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
    if payload.get("dual_source_base_rig", False) and not payload.get("geometry_source_rel"):
        raise ValueError("dual_source_base_rig requires geometry_source_rel.")
    if payload.get("geometry_object_name") and not payload.get("geometry_source_rel"):
        raise ValueError("geometry_object_name requires geometry_source_rel.")
    clear_scene()
    source_collection = new_collection("PROVIDER_SOURCE")
    working_collection = new_collection("WORKING")
    vanilla_reference = import_vanilla_reference(job, payload, pdx)
    imported = import_candidate(source)
    excluded_names = {str(name) for name in payload.get("excluded_provider_objects", [])}
    geometry_source = None
    geometry_transfer = None
    dual_source_base_rig = None
    base_weight_sanitization = None
    if payload.get("geometry_source_rel"):
        geometry_source = within(job, str(payload["geometry_source_rel"]))
        imported_geometry = import_geometry_candidate(geometry_source)
        imported_rig = imported
        imported = imported_geometry + imported_rig
        requested_geometry_object = explicit_safe_name(
            payload.get("geometry_object_name"),
            "geometry_object_name",
        )
        geometry_candidates = [
            obj for obj in imported_geometry
            if (
                obj.type == "MESH"
                and obj.name == requested_geometry_object
                and obj.name not in excluded_names
            )
        ]
        if len(geometry_candidates) != 1:
            raise RuntimeError(
                "Dual-source rig preparation requires exactly one explicitly selected geometry MESH: "
                + json.dumps(
                    {
                        "requested": requested_geometry_object,
                        "observed": sorted(
                            obj.name
                            for obj in imported_geometry
                            if obj.type == "MESH" and obj.name == requested_geometry_object
                        ),
                    },
                    sort_keys=True,
                )
            )
        selected_geometry = geometry_candidates[0]
        if selected_geometry.library is not None or selected_geometry.data.library is not None:
            raise RuntimeError(
                "Dual-source geometry_object_name must select a local, fully appended MESH object."
            )
        rig_mesh_candidates = [
            obj for obj in imported_rig
            if obj.type == "MESH" and obj.name not in excluded_names
        ]
        requested_source_mesh_names = {
            str(name) for name in payload.get("source_mesh_names", [])
        }
        if requested_source_mesh_names:
            rig_mesh_candidates = [
                obj for obj in rig_mesh_candidates if obj.name in requested_source_mesh_names
            ]
            observed_source_mesh_names = {obj.name for obj in rig_mesh_candidates}
            if observed_source_mesh_names != requested_source_mesh_names:
                raise RuntimeError(
                    "Dual-source rig preparation did not find every explicitly named source mesh: "
                    + json.dumps(
                        {
                            "requested": sorted(requested_source_mesh_names),
                            "observed": sorted(observed_source_mesh_names),
                        },
                        sort_keys=True,
                    )
                )
        armature_candidates = [
            obj for obj in imported_rig
            if obj.type == "ARMATURE" and obj.name not in excluded_names
        ]
        requested_source_armature = str(payload.get("source_armature_name") or "")
        if requested_source_armature:
            armature_candidates = [
                obj for obj in armature_candidates if obj.name == requested_source_armature
            ]
        if not rig_mesh_candidates or len(armature_candidates) != 1:
            raise RuntimeError(
                "Dual-source rig preparation requires one geometry mesh, one or more explicitly selected rig meshes, and one source armature."
            )
        working_source = [geometry_candidates[0], armature_candidates[0]]
        for obj in imported:
            move_to_collection(obj, source_collection)
            obj["hoi4_working"] = False
        working = duplicate_hierarchy(working_source, source_collection, working_collection)
        working_by_source = {
            str(obj.get("hoi4_source_object")): obj
            for obj in working
        }
        target_mesh = working_by_source[geometry_candidates[0].name]
        target_armature = working_by_source[armature_candidates[0].name]
        geometry_transfer = bind_geometry_to_existing_rig(
            rig_mesh_candidates,
            target_mesh,
            target_armature,
            str(payload.get("geometry_weight_mode") or "four_nearest"),
        )
        if payload.get("dual_source_base_rig", False):
            dual_source_base_rig = prepare_dual_source_base_rig(target_armature)
            base_weight_sanitization = sanitize_working_weights()
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

    asset_kind = str(payload["asset_kind"])
    humanoid_asset = is_humanoid_asset_kind(asset_kind)
    # Provider FBX files commonly key the armature object's 0.01 import scale.
    # Remove those scale curves before normalization so a later dependency-graph
    # evaluation cannot restore the provider scale after the report is measured.
    scale_sanitization = (
        {
            "policy": "dual_source_base_rig_has_no_working_actions",
            "actions": [],
            "remaining_scale_fcurves": 0,
        }
        if dual_source_base_rig is not None
        else sanitize_action_scale_channels()
        if humanoid_asset
        else {"policy": "not_applicable", "actions": [], "remaining_scale_fcurves": 0}
    )
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
    preserve_geometry_topology = bool(payload.get("preserve_geometry_topology", False))
    if preserve_geometry_topology and (
        payload.get("repair_before_reduction", False)
        or int(payload.get("target_triangles", 0)) > 0
    ):
        raise ValueError(
            "Preserved geometry topology cannot be combined with repair or decimation."
        )
    triangulation = (
        {
            "applied": False,
            "policy": "preserve_audited_geometry_topology",
            "triangulated_objects": [],
        }
        if preserve_geometry_topology
        else triangulate_and_normals()
    )
    weld_distance = float(payload.get("topology_weld_distance", 1e-5))
    pre_reduction_topology_repair = None
    if payload.get("repair_before_reduction", False):
        pre_reduction_topology_repair = repair_open_surface_boundaries(weld_distance)
    reduction = (
        {
            "applied": False,
            "policy": "preserve_audited_geometry_topology",
            "target_triangles": 0,
        }
        if preserve_geometry_topology
        else controlled_decimate(int(payload.get("target_triangles", 0)))
    )
    topology_repair = (
        {
            "applied": False,
            "policy": "preserve_audited_geometry_topology",
            "method": "skipped for audited geometry handoff",
            "objects": [],
        }
        if preserve_geometry_topology
        else repair_open_surface_boundaries(weld_distance)
    )
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
    if (humanoid_asset or asset_kind == "creature") and payload.get("texture_source_rels") and not image_nodes():
        raise RuntimeError(
            "Humanoid preparation produced no image-backed material. Refusing to export a black unit."
        )
    material_checkpoint = job / "blender" / "checkpoints" / "02_materials_approved.blend"
    save_blend(material_checkpoint)

    actions = action_metrics()
    if dual_source_base_rig is not None:
        actions["actions"] = []
        actions["base_rig"] = dual_source_base_rig
        actions["base_weight_sanitization"] = base_weight_sanitization
    actions["scale_sanitization"] = scale_sanitization
    actions["root_translation_sanitization"] = (
        sanitize_root_translation_channels()
        if humanoid_asset
        else {"policy": "not_applicable", "actions": []}
    )
    if humanoid_asset and scale_sanitization["remaining_scale_fcurves"]:
        raise RuntimeError("Humanoid action export still contains scale channels after sanitization.")
    rig_checkpoint = None
    if humanoid_asset:
        rig_checkpoint = job / "blender" / "checkpoints" / "03_rig_approved.blend"
        save_blend(rig_checkpoint)
        action_checkpoint = job / "blender" / "checkpoints" / "04_actions_approved.blend"
        save_blend(action_checkpoint)
    pre_export = job / "blender" / "checkpoints" / "05_pre_export.blend"
    previews = render_previews(job, runtime_stem) if payload.get("render_previews", True) else []
    save_blend(pre_export)
    normalization_persistence = stabilize_saved_normalization(pre_export, target_height)
    normalization_persistence["post_stabilization_verification"] = verify_saved_normalization(pre_export, target_height)
    normalization_persistence["checkpoint"] = str(pre_export.relative_to(job)).replace("\\", "/")
    geometry = normalization_persistence["geometry"]

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
        "dual_source_base_rig": dual_source_base_rig,
        "base_weight_sanitization": base_weight_sanitization,
        "imported_geometry": imported_metrics,
        "normalization": normalize,
        "normalization_persistence": normalization_persistence,
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


def _mesh_region_name(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 128 or any(ord(char) < 32 for char in value):
        raise ValueError(f"{label} must be an exact nonempty name of at most 128 characters.")
    return value


def _mesh_region_inputs(req: Dict[str, Any]) -> Dict[str, Any]:
    payload = req["payload"]
    region = payload.get("mesh_region")
    required = {"mesh_name", "bone_name", "expected_source_sha256", "expected_action_sha256"}
    allowed = required | {"aabb", "weight", "offset", "limit", "measurement"}
    if not isinstance(region, dict) or not required.issubset(region) or set(region) - allowed:
        raise ValueError("mesh_region has missing or unsupported fields.")
    if payload.get("render_previews") or payload.get("runtime_stem") or payload.get("preview_view_names"):
        raise ValueError("Mesh-region inspection does not render or write previews.")
    result = dict(region)
    for key in ("mesh_name", "bone_name"):
        result[key] = _mesh_region_name(region[key], key)
    result["rig_name"] = _mesh_region_name(payload.get("target_armature_name"), "target_armature_name")
    result["action_name"] = _mesh_region_name(payload.get("action_name"), "action_name")
    frame = payload.get("preview_frame")
    if type(frame) is not int or not 0 <= frame <= 1000000:
        raise ValueError("Mesh-region preview_frame must be an explicit nonnegative bounded integer.")
    result["frame"] = frame
    for key in ("expected_source_sha256", "expected_action_sha256"):
        if not isinstance(region[key], str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", region[key]):
            raise ValueError(f"{key} must be an explicit SHA-256.")
        result[key] = region[key].upper()
    if not any(key in region for key in ("aabb", "weight")):
        raise ValueError("Mesh-region inspection requires a spatial and/or bone-weight selector.")
    if "aabb" in region:
        box = region["aabb"]
        if not isinstance(box, dict) or set(box) != {"space", "min", "max"} or not isinstance(box["space"], str) or box["space"] not in {"WORLD", "BONE_LOCAL"}:
            raise ValueError("aabb requires WORLD or BONE_LOCAL space and exact min/max vectors.")
        low, high = _locator_numbers(box["min"], 3, "aabb min"), _locator_numbers(box["max"], 3, "aabb max")
        if any(abs(value) > 1000000 for value in low + high) or any(a > b for a, b in zip(low, high)):
            raise ValueError("AABB bounds must be ordered and inside +/-1000000 units.")
        result["aabb"] = {"space": box["space"], "min": low, "max": high}
    if "weight" in region:
        weight = region["weight"]
        if not isinstance(weight, dict) or set(weight) != {"bone_name", "min", "max"}:
            raise ValueError("weight requires an exact bone_name and inclusive min/max.")
        low, high = _locator_numbers([weight["min"], weight["max"]], 2, "weight range")
        if not 0 <= low <= high <= 1:
            raise ValueError("Weight range must be ordered inside [0,1].")
        result["weight"] = {"bone_name": _mesh_region_name(weight["bone_name"], "weight bone"), "min": low, "max": high}
    for key, default, maximum in (("offset", 0, 1000000), ("limit", 64, 256)):
        value = region.get(key, default)
        if type(value) is not int or not (0 if key == "offset" else 1) <= value <= maximum:
            raise ValueError(f"Invalid mesh-region {key}.")
        result[key] = value
    if "measurement" in region:
        measurement = region["measurement"]
        if not isinstance(measurement, dict) or set(measurement) != {"origin_vertex_indices", "endpoint_vertex_indices"}:
            raise ValueError("measurement requires origin and endpoint source-vertex index sets.")
        for name, values in measurement.items():
            if not isinstance(values, list) or not 1 <= len(values) <= 64 or any(type(value) is not int or not 0 <= value < 1000000 for value in values) or len(set(values)) != len(values):
                raise ValueError(f"{name} requires 1-64 unique bounded source vertex indices.")
        if set(measurement["origin_vertex_indices"]) & set(measurement["endpoint_vertex_indices"]):
            raise ValueError("Measurement origin and endpoint index sets must not overlap.")
    job = Path(req["job_root"]).resolve()
    source = _promotion_path(job, payload.get("blend_rel"), ".blend")
    if source.stat().st_size < 1 or file_sha256(source) != result["expected_source_sha256"]:
        raise ValueError("Mesh-region source SHA-256 mismatch.")
    result.update(job=job, source=source, source_bytes=source.stat().st_size)
    return result


def _action_channel_inventory_inputs(req: Dict[str, Any]) -> Dict[str, Any]:
    payload = req["payload"]
    if payload.get("include_action_channels") is not True:
        raise ValueError("Action-channel inventory requires include_action_channels=true.")
    if payload.get("render_previews") or payload.get("runtime_stem") or payload.get("preview_view_names") or payload.get("mesh_region") is not None:
        raise ValueError("Action-channel inventory cannot render or combine with mesh-region inspection.")
    if payload.get("preview_frame", -1) != -1:
        raise ValueError("Action-channel inventory does not evaluate a preview frame.")
    expected = payload.get("expected_source_sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", expected):
        raise ValueError("expected_source_sha256 must be an explicit SHA-256 for action-channel inventory.")
    job = Path(req["job_root"]).resolve()
    source = _promotion_path(job, payload.get("blend_rel"), ".blend")
    expected = expected.upper()
    size = source.stat().st_size
    if size < 1 or file_sha256(source) != expected:
        raise ValueError("Action-channel inventory source SHA-256 mismatch.")
    return {
        "job": job,
        "source": source,
        "source_bytes": size,
        "expected_source_sha256": expected,
        "rig_name": _mesh_region_name(payload.get("target_armature_name"), "target_armature_name"),
        "action_name": _mesh_region_name(payload.get("action_name"), "action_name"),
    }


def _action_channel_rows(action: Any, rig: Any) -> List[Dict[str, Any]]:
    curves = list(action_fcurves(action))
    if len(curves) > 4096:
        raise ValueError("Action-channel inventory exceeds the 4096-curve cap.")
    bone_owners = [(bone.path_from_id(), bone) for bone in rig.pose.bones]
    object_paths = {"location", "rotation_euler", "rotation_quaternion", "rotation_axis_angle", "scale"}
    rows = []
    total_keys = sum(len(curve.keyframe_points) for curve, _ in curves)
    if total_keys > 500000:
        raise ValueError("Action-channel key inventory exceeds 500000 keys.")
    for curve, _ in curves:
        path = str(curve.data_path)
        if not path or len(path) > 1024 or any(ord(character) < 32 for character in path):
            raise ValueError("Action-channel inventory encountered an invalid or overlong data_path.")
        index = int(curve.array_index)
        if not 0 <= index <= 1024:
            raise ValueError("Action-channel inventory encountered an invalid array_index.")
        group = getattr(curve, "group", None)
        group_name = None if group is None else str(group.name)
        if group_name is not None and (len(group_name) > 128 or any(ord(character) < 32 for character in group_name)):
            raise ValueError("Action-channel inventory encountered an invalid or overlong group name.")
        owners = [bone for prefix, bone in bone_owners if path == prefix or path.startswith(prefix + ".") or path.startswith(prefix + "[")]
        if len(owners) > 1:
            raise ValueError("Action-channel inventory found an ambiguous bone RNA owner.")
        rotation_mode = str(owners[0].rotation_mode) if owners else (str(rig.rotation_mode) if path in object_paths else None)
        rows.append({"data_path": path, "array_index": index, "group": group_name, "rotation_mode": rotation_mode,
                     "extrapolation": str(curve.extrapolation),
                     "keyframes": [{"co": list(point.co), "interpolation": str(point.interpolation),
                                    "handle_left": list(point.handle_left), "handle_right": list(point.handle_right),
                                    "handle_left_type": str(point.handle_left_type), "handle_right_type": str(point.handle_right_type)}
                                   for point in curve.keyframe_points]})
    return sorted(rows, key=lambda row: (row["data_path"], row["array_index"], row["group"] or "", row["rotation_mode"] or ""))


def _action_channel_binding_record(rig: Any) -> Dict[str, Any]:
    animation = rig.animation_data
    return {
        "frame": int(bpy.context.scene.frame_current),
        "subframe": float(bpy.context.scene.frame_subframe),
        "object_rotation_mode": str(rig.rotation_mode),
        "bone_rotation_modes": [(bone.name, str(bone.rotation_mode)) for bone in rig.pose.bones],
        "action": animation.action.name if animation and animation.action else None,
        "action_slot": getattr(getattr(animation, "action_slot", None), "identifier", None) if animation else None,
        "drivers": [(curve.data_path, int(curve.array_index)) for curve in animation.drivers] if animation else [],
        "nla": [
            {
                "name": track.name,
                "mute": bool(track.mute),
                "solo": bool(track.is_solo),
                "strips": [(strip.name, strip.action.name if strip.action else None, float(strip.frame_start), float(strip.frame_end)) for strip in track.strips],
            }
            for track in animation.nla_tracks
        ] if animation else [],
    }


def inspect_action_channels(req: Dict[str, Any]) -> Dict[str, Any]:
    context = _action_channel_inventory_inputs(req)
    try:
        bpy.ops.wm.open_mainfile(filepath=str(context["source"]), use_scripts=False)
        rig = bpy.context.scene.objects.get(context["rig_name"])
        action = bpy.data.actions.get(context["action_name"])
        if rig is None or rig.type != "ARMATURE" or action is None:
            raise ValueError("Action-channel inventory requires the exact armature and action.")
        if rig.library or rig.override_library or action.library or action.override_library:
            raise ValueError("Action-channel inventory requires local armature and action data.")
        before_actions = _mesh_region_action_integrity()
        before_binding = _action_channel_binding_record(rig)
        native_hash = _mesh_region_action_hash(action)
        rows = _action_channel_rows(action, rig)
        after_binding = _action_channel_binding_record(rig)
        if after_binding != before_binding or _mesh_region_action_integrity() != before_actions or _mesh_region_action_hash(action) != native_hash:
            raise RuntimeError("Read-only action-channel inventory changed action, frame, or rotation-mode data.")
        result = {
            "source_sha256": context["expected_source_sha256"],
            "source_bytes": context["source_bytes"],
            "source_immutable": True,
            "armature_name": rig.name,
            "action_name": action.name,
            "native_action_sha256": native_hash,
            "native_action_hash_policy": "inspect_scene_curve_slot_path_index_key_co_interpolation_v1_not_anim_file_sha256",
            "action_integrity_sha256": before_actions,
            "row_count": len(rows),
            "pose_local_snapshot": [{"name": bone.name, "location": list(bone.location),
                                     "rotation_mode": bone.rotation_mode, "rotation_quaternion": list(bone.rotation_quaternion),
                                     "rotation_euler": list(bone.rotation_euler), "scale": list(bone.scale)} for bone in rig.pose.bones],
            "rows": rows,
            "action_data_unchanged": True,
            "frame_action_rotation_modes_unchanged": True,
            "checkpoint_saved": False,
            "new_provider_call": False,
        }
        _promotion_digest(result)
        return {
            "blend": context["source"].relative_to(context["job"]).as_posix(),
            "inspected_target_armature": rig.name,
            "inspected_action_sha256": native_hash,
            "action_channels": result,
        }
    finally:
        if file_sha256(context["source"]) != context["expected_source_sha256"] or context["source"].stat().st_size != context["source_bytes"]:
            raise RuntimeError("Read-only action-channel inventory changed its source checkpoint.")


def _mesh_region_action_hash(action: bpy.types.Action) -> str:
    """The existing inspect_scene inspected_action_sha256 contract, not an .anim hash."""
    records = [{"slot": getattr(slot, "identifier", None), "data_path": curve.data_path, "array_index": int(curve.array_index),
                "keyframes": [[float(key.co.x), float(key.co.y), str(key.interpolation)] for key in curve.keyframe_points]}
               for curve, slot in action_fcurves(action)]
    return _promotion_digest(records)


def _mesh_region_action_integrity() -> str:
    records = {}
    for action in bpy.data.actions:
        curves = [{"path": curve.data_path, "index": curve.array_index, "settings": _promotion_scalars(curve),
                   "keys": [{"co": list(key.co), "left": list(key.handle_left), "right": list(key.handle_right), "settings": _promotion_scalars(key)} for key in curve.keyframe_points],
                   "samples": [list(point.co) for point in curve.sampled_points]}
                  for curve, _ in action_fcurves(action)]
        records[action.name] = {"settings": _promotion_scalars(action), "properties": _promotion_properties(action), "fake_user": action.use_fake_user, "curves": curves,
                                "slots": [_promotion_scalars(slot) for slot in getattr(action, "slots", [])]}
    return _promotion_digest(records)


def _mesh_region_topology(mesh: Any) -> str:
    return _promotion_digest({"vertices": [vertex.index for vertex in mesh.vertices],
                              "edges": [(edge.index, list(edge.vertices)) for edge in mesh.edges],
                              "loops": [(loop.index, loop.vertex_index, loop.edge_index) for loop in mesh.loops],
                              "polygons": [(face.index, face.loop_start, face.loop_total, list(face.vertices), face.material_index) for face in mesh.polygons]})


def _mesh_region_matrix(matrix: Matrix, label: str) -> Matrix:
    _locator_matrix_record(matrix)
    if matrix.determinant() <= 0:
        raise ValueError(f"{label} has a negative or singular transform.")
    try:
        inverse = matrix.inverted()
    except ValueError as exc:
        raise ValueError(f"{label} has a singular transform.") from exc
    _locator_matrix_record(inverse)
    return inverse


def _mesh_region_normal(normal: Vector, transform: Matrix) -> List[float]:
    result = transform @ normal
    if not math.isfinite(result.length) or result.length <= 1e-12:
        raise ValueError("Mesh-region normal is nonfinite or has zero length.")
    return _locator_numbers(list(result.normalized()), 3, "mesh-region normal")


def _mesh_region_measurement(specification: Dict[str, Any], matches: List[int], position: Any, bone_inverse: Matrix) -> Dict[str, Any]:
    required = set(specification["origin_vertex_indices"]) | set(specification["endpoint_vertex_indices"])
    if not required.issubset(set(matches)):
        raise ValueError("Every measurement vertex index must match the complete selector, independently of pagination.")
    def centroid(indices: List[int]) -> Vector:
        return sum((position(index) for index in indices), Vector()) / len(indices)
    origin, endpoint = centroid(specification["origin_vertex_indices"]), centroid(specification["endpoint_vertex_indices"])
    axis = endpoint - origin
    local_origin, local_endpoint = bone_inverse @ origin, bone_inverse @ endpoint
    local_axis = local_endpoint - local_origin
    if any(not math.isfinite(value.length) or value.length <= 1e-12 for value in (axis, local_axis)):
        raise ValueError("Measured centroid axis is nonfinite or zero length.")
    return {"policy": "caller_selected_vertex_centroids_no_semantic_detection_no_roll",
            "origin_vertex_indices": specification["origin_vertex_indices"], "endpoint_vertex_indices": specification["endpoint_vertex_indices"],
            "origin_count": len(specification["origin_vertex_indices"]), "endpoint_count": len(specification["endpoint_vertex_indices"]),
            "world_origin": list(origin), "world_endpoint": list(endpoint), "world_axis": list(axis.normalized()), "world_length": axis.length,
            "bone_local_origin": list(local_origin), "bone_local_endpoint": list(local_endpoint), "bone_local_axis": list(local_axis.normalized()),
            "rotation_quaternion": None, "semantic_muzzle_approval": False}


def _mesh_region_collect(mesh_obj: Any, evaluated_obj: Any, evaluated: Any, rig: Any, evaluated_rig: Any, context: Dict[str, Any]) -> Dict[str, Any]:
    source = mesh_obj.data
    if len(source.vertices) > 1000000 or len(source.loops) > 6000000 or len(source.uv_layers) > 8 or len(mesh_obj.vertex_groups) > 256:
        raise ValueError("Mesh-region source exceeds explicit vertex/loop/UV/group caps.")
    topology = _mesh_region_topology(source)
    if _mesh_region_topology(evaluated) != topology:
        raise ValueError("Evaluated topology/index correspondence changed.")
    if [layer.name for layer in source.uv_layers] != [layer.name for layer in evaluated.uv_layers]:
        raise ValueError("Evaluated UV-layer identity changed.")
    world = evaluated_obj.matrix_world.copy()
    world_inverse = _mesh_region_matrix(world, "mesh world")
    bone_world = evaluated_rig.matrix_world @ evaluated_rig.pose.bones[context["bone_name"]].matrix
    bone_inverse = _mesh_region_matrix(bone_world, "posed bone world")
    rest_bone_world = rig.matrix_world @ rig.data.bones[context["bone_name"]].matrix_local
    rest_bone_inverse = _mesh_region_matrix(rest_bone_world, "rest bone world")
    normal_world = world_inverse.to_3x3().transposed()
    normal_bone = bone_world.to_3x3().transposed()
    weight_group = None
    if "weight" in context:
        name = context["weight"]["bone_name"]
        if rig.data.bones.get(name) is None or mesh_obj.vertex_groups.get(name) is None:
            raise ValueError("Weight selector must name an existing rig bone and mesh group.")
        weight_group = mesh_obj.vertex_groups[name].index
    matches = []
    for vertex in evaluated.vertices:
        point = world @ vertex.co
        _locator_numbers(list(point), 3, "evaluated world position")
        box = context.get("aabb")
        if box:
            sample = point if box["space"] == "WORLD" else bone_inverse @ point
            if any(sample[axis] < box["min"][axis] or sample[axis] > box["max"][axis] for axis in range(3)):
                continue
        if weight_group is not None:
            value = sum(group.weight for group in source.vertices[vertex.index].groups if group.group == weight_group)
            if not context["weight"]["min"] <= value <= context["weight"]["max"]:
                continue
        matches.append(vertex.index)
    if context["offset"] > len(matches):
        raise ValueError("Mesh-region page offset exceeds total matched vertices.")
    loop_map = {}
    for face in source.polygons:
        for index in face.loop_indices:
            loop_map.setdefault(source.loops[index].vertex_index, []).append((index, face.index, face.material_index))
    selected, corner_count = [], 0
    for index in matches[context["offset"]:context["offset"] + context["limit"]]:
        count = len(loop_map.get(index, []))
        if corner_count + count > 8192:
            if not selected:
                raise ValueError("One vertex exceeds the 8192-corner page cap.")
            break
        selected.append(index)
        corner_count += count
    def position(index: int) -> Vector:
        return world @ evaluated.vertices[index].co
    records = []
    for index in selected:
        original, posed = source.vertices[index], evaluated.vertices[index]
        point = position(index)
        vertex_normal = _mesh_region_normal(posed.normal, normal_world)
        corners = []
        for loop_index, face_index, material_index in loop_map.get(index, []):
            material = mesh_obj.material_slots[material_index].material if material_index < len(mesh_obj.material_slots) else None
            posed_normal = _mesh_region_normal(evaluated.corner_normals[loop_index].vector, normal_world)
            corners.append({"loop_index": loop_index, "polygon_index": face_index, "material_index": material_index, "material_name": material.name if material else None,
                            "source_uvs": {layer.name: _locator_numbers(list(layer.data[loop_index].uv), 2, "source UV") for layer in source.uv_layers},
                            "evaluated_uvs": {layer.name: _locator_numbers(list(layer.data[loop_index].uv), 2, "evaluated UV") for layer in evaluated.uv_layers},
                            "source_normal": _locator_numbers(list(source.corner_normals[loop_index].vector), 3, "source corner normal"),
                            "evaluated_world_normal": posed_normal, "bone_local_normal": _mesh_region_normal(Vector(posed_normal), normal_bone)})
        records.append({"vertex_index": index, "source_position": list(original.co), "source_world_position": list(mesh_obj.matrix_world @ original.co),
                        "rest_bone_local_position": list(rest_bone_inverse @ (mesh_obj.matrix_world @ original.co)),
                        "evaluated_world_position": list(point), "bone_local_position": list(bone_inverse @ point),
                        "source_normal": list(original.normal), "evaluated_world_normal": vertex_normal,
                        "bone_local_normal": _mesh_region_normal(Vector(vertex_normal), normal_bone),
                        "weights": [{"group_index": group.group, "group_name": mesh_obj.vertex_groups[group.group].name, "weight": float(group.weight)} for group in original.groups],
                        "corners": corners})
    measurement = _mesh_region_measurement(context["measurement"], matches, position, bone_inverse) if "measurement" in context else None
    next_offset = context["offset"] + len(records)
    result = {"mesh_name": mesh_obj.name, "mesh_data_name": source.name, "rig_name": rig.name, "bone_name": context["bone_name"], "frame": context["frame"],
              "source_counts": {"vertices": len(source.vertices), "loops": len(source.loops), "polygons": len(source.polygons)}, "topology_sha256": topology,
              "topology_index_correspondence": True, "selector": {key: context[key] for key in ("aabb", "weight") if key in context},
              "total_matches": len(matches), "matched_vertex_indices_sha256": _promotion_digest(matches),
              "page": {"offset": context["offset"], "requested_limit": context["limit"], "returned_vertices": len(records), "returned_corners": corner_count,
                       "vertex_cap": 256, "corner_cap": 8192, "truncated": next_offset < len(matches), "corner_cap_reached": len(records) < len(matches[context["offset"]:context["offset"] + context["limit"]]),
                       "next_offset": next_offset if next_offset < len(matches) else None},
              "matrices": {"mesh_world": _locator_matrix_record(world), "mesh_world_inverse": _locator_matrix_record(world_inverse),
                           "bone_pose_world": _locator_matrix_record(bone_world), "bone_pose_world_inverse": _locator_matrix_record(bone_inverse),
                           "bone_rest_world": _locator_matrix_record(rest_bone_world), "bone_rest_world_inverse": _locator_matrix_record(rest_bone_inverse)},
              "records": records, "measurement": measurement}
    _promotion_digest(result)
    return result


def _mesh_region_object_dependencies(mesh: Any, rig: Any) -> None:
    if rig.parent is not None or (mesh.parent is not None and (mesh.parent != rig or mesh.parent_type != "OBJECT")):
        raise ValueError("Mesh-region targets have an uninspected parent dependency.")
    if mesh.data.animation_data is not None or rig.data.animation_data is not None:
        raise ValueError("Mesh-region does not support animated mesh or armature datablocks.")


def inspect_mesh_region(req: Dict[str, Any]) -> Dict[str, Any]:
    context = _mesh_region_inputs(req)
    bpy.ops.wm.open_mainfile(filepath=str(context["source"]), use_scripts=False)
    objects = bpy.context.scene.objects
    mesh, rig = objects.get(context["mesh_name"]), objects.get(context["rig_name"])
    if mesh is None or mesh.type != "MESH" or rig is None or rig.type != "ARMATURE" or rig.data.bones.get(context["bone_name"]) is None:
        raise ValueError("Mesh-region requires the exact mesh, armature, and existing bone.")
    _mesh_region_object_dependencies(mesh, rig)
    for obj in (mesh, rig):
        if obj.library or obj.override_library or obj.data.library or obj.data.override_library or obj.constraints or any(value <= 0 for value in obj.scale):
            raise ValueError("Mesh-region requires local unconstrained positive-transform targets.")
        _mesh_region_matrix(obj.matrix_world, obj.name)
    modifiers = list(mesh.modifiers)
    if len(modifiers) != 1 or modifiers[0].type != "ARMATURE" or modifiers[0].object != rig or not modifiers[0].show_viewport:
        raise ValueError("Mesh-region permits exactly one active Armature modifier consuming the named rig.")
    if mesh.data.shape_keys or mesh.animation_data or rig.data.pose_position != "POSE" or any(bone.constraints for bone in rig.pose.bones):
        raise ValueError("Mesh-region does not support shape keys, mesh animation, REST display, or pose constraints.")
    animation, action = rig.animation_data, bpy.data.actions.get(context["action_name"])
    if animation is None or animation.drivers or animation.nla_tracks or action is None or action.library or action.override_library or len(getattr(action, "slots", [])) > 1:
        raise ValueError("Mesh-region requires one explicit local action without NLA/drivers or ambiguous slots.")
    if any(curve.modifiers for curve, _ in action_fcurves(action)) or not action.frame_range[0] <= context["frame"] <= action.frame_range[1]:
        raise ValueError("Mesh-region requires an in-range frame and unmodified action curves.")
    actual_action_hash = _mesh_region_action_hash(action)
    if actual_action_hash != context["expected_action_sha256"]:
        raise ValueError("Mesh-region native action SHA-256 mismatch; obtain inspected_action_sha256 with ordinary read-only inspect_scene first.")
    before_actions = _mesh_region_action_integrity()
    old_action, old_slot = animation.action, getattr(animation, "action_slot", None)
    scene = bpy.context.scene
    old_frame, old_subframe = scene.frame_current, scene.frame_subframe
    evaluated_obj = None
    try:
        animation.action = action
        if getattr(action, "slots", []):
            animation.action_slot = action.slots[0]
        scene.frame_set(context["frame"])
        bpy.context.view_layer.update()
        if any(value <= 0 for value in rig.pose.bones[context["bone_name"]].scale):
            raise ValueError("Requested bone has negative or singular pose scale.")
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated_obj, evaluated_rig = mesh.evaluated_get(depsgraph), rig.evaluated_get(depsgraph)
        evaluated = evaluated_obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        report = _mesh_region_collect(mesh, evaluated_obj, evaluated, rig, evaluated_rig, context)
    finally:
        if evaluated_obj is not None:
            evaluated_obj.to_mesh_clear()
        animation.action = old_action
        if old_slot is not None:
            animation.action_slot = old_slot
        scene.frame_set(old_frame, subframe=old_subframe)
        bpy.context.view_layer.update()
    if animation.action != old_action or getattr(animation, "action_slot", None) != old_slot or scene.frame_current != old_frame or scene.frame_subframe != old_subframe:
        raise RuntimeError("Mesh-region frame/action binding restoration failed.")
    if _mesh_region_action_integrity() != before_actions or _mesh_region_action_hash(action) != actual_action_hash:
        raise RuntimeError("Read-only mesh-region inspection changed action data.")
    if file_sha256(context["source"]) != context["expected_source_sha256"] or context["source"].stat().st_size != context["source_bytes"]:
        raise RuntimeError("Read-only mesh-region source changed.")
    report.update(source_sha256=context["expected_source_sha256"], source_bytes=context["source_bytes"], source_immutable=True,
                  action_name=action.name, native_action_sha256=actual_action_hash, native_action_hash_policy="inspect_scene_curve_slot_path_index_key_co_interpolation_v1_not_anim_file_sha256",
                  action_integrity_sha256=before_actions, all_actions_unchanged=True, action_provenance=_promotion_properties(action),
                  source_receipt_metadata={obj.name: {key: _promotion_value(obj[key]) for key in PROMOTION_METADATA_KEYS if key in obj} for obj in (rig, mesh)},
                  frame_action_binding_restored=True, new_provider_call=False, checkpoint_saved=False)
    return {"blend": context["source"].relative_to(context["job"]).as_posix(), "inspected_target_armature": rig.name,
            "inspected_action_sha256": actual_action_hash, "mesh_region": report}


def _component_review_inputs(req: Dict[str, Any]) -> Dict[str, Any]:
    payload = req["payload"]
    required = {"blend_rel", "expected_source_sha256", "mesh_name", "render_group", "component_ids", "component_offset", "component_limit", "preview_view_names"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError("review_humanoid_components accepts only its exact read-only contract.")
    if payload["render_group"] is not True:
        raise ValueError("Humanoid component review requires render_group=true; bounds-only review is insufficient.")
    expected = payload["expected_source_sha256"]
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", expected):
        raise ValueError("expected_source_sha256 must be an explicit SHA-256.")
    ids = payload["component_ids"]
    if not isinstance(ids, list) or len(ids) > 16 or any(not isinstance(value, str) or not re.fullmatch(r"c_v[0-9]{1,7}", value) for value in ids) or len(set(ids)) != len(ids):
        raise ValueError("component_ids must contain at most 16 unique stable component IDs.")
    offset, limit = payload["component_offset"], payload["component_limit"]
    if type(offset) is not int or not 0 <= offset <= 8192 or type(limit) is not int or not 1 <= limit <= 16:
        raise ValueError("Component review offset/limit must stay inside the 8192-component and 16-component page caps.")
    if ids and (offset != 0 or limit != 16):
        raise ValueError("Explicit component_ids cannot be combined with nondefault pagination.")
    allowed_views = {"front", "left", "right", "rear", "top", "three_quarter"}
    requested_views = payload["preview_view_names"]
    if not isinstance(requested_views, list):
        raise ValueError("preview_view_names must be a list.")
    views = requested_views or ["front", "left", "right", "rear", "top", "three_quarter"]
    if not 1 <= len(views) <= 6 or any(type(value) is not str or value not in allowed_views for value in views) or len(set(views)) != len(views):
        raise ValueError("Component-review views must be unique supported named views.")
    job = Path(req["job_root"]).resolve()
    source = _promotion_path(job, payload["blend_rel"], ".blend")
    expected = expected.upper()
    source_bytes = source.stat().st_size
    if source_bytes < 1 or file_sha256(source) != expected:
        raise ValueError("Component-review source SHA-256 mismatch.")
    request_id = req.get("request_id")
    if not isinstance(request_id, str) or not re.fullmatch(r"[0-9a-f]{32}", request_id):
        raise ValueError("Component review requires the adapter's exact lowercase UUID request_id.")
    return {"job": job, "source": source, "source_bytes": source_bytes, "expected_source_sha256": expected,
            "mesh_name": _mesh_region_name(payload["mesh_name"], "mesh_name"), "component_ids": ids,
            "component_offset": offset, "component_limit": limit, "preview_view_names": views,
            "request_id": request_id}


def _component_index_catalog(vertex_count: int, edges: Iterable[Tuple[int, Iterable[int]]], polygons: Iterable[Tuple[int, Iterable[int]]]) -> List[Dict[str, Any]]:
    if type(vertex_count) is not int or not 1 <= vertex_count <= 250000:
        raise ValueError("Component review requires 1-250000 source vertices.")
    parent = list(range(vertex_count))
    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index
    def union(left: int, right: int) -> None:
        left, right = find(left), find(right)
        if left != right:
            parent[max(left, right)] = min(left, right)
    edge_rows, polygon_rows = [], []
    for edge_index, values in edges:
        values = tuple(values)
        if type(edge_index) is not int or len(values) != 2 or any(type(value) is not int or not 0 <= value < vertex_count for value in values) or values[0] == values[1]:
            raise ValueError("Component review found invalid edge topology.")
        union(values[0], values[1])
        edge_rows.append((edge_index, values))
    for polygon_index, values in polygons:
        values = tuple(values)
        if type(polygon_index) is not int or len(values) < 3 or any(type(value) is not int or not 0 <= value < vertex_count for value in values):
            raise ValueError("Component review found invalid polygon topology.")
        for value in values[1:]:
            union(values[0], value)
        polygon_rows.append((polygon_index, values))
    vertices_by_root: Dict[int, List[int]] = {}
    for vertex in range(vertex_count):
        vertices_by_root.setdefault(find(vertex), []).append(vertex)
    result = []
    for vertices in sorted(vertices_by_root.values(), key=lambda row: row[0]):
        members = set(vertices)
        component_edges = [index for index, values in edge_rows if values[0] in members]
        component_polygons = [index for index, values in polygon_rows if values[0] in members]
        if any(any(value not in members for value in values) for index, values in edge_rows if index in component_edges):
            raise ValueError("Component edge crosses a computed component boundary.")
        if any(any(value not in members for value in values) for index, values in polygon_rows if index in component_polygons):
            raise ValueError("Component polygon crosses a computed component boundary.")
        result.append({"component_id": f"c_v{vertices[0]}", "vertex_indices": vertices,
                       "edge_indices": component_edges, "polygon_indices": component_polygons})
    if len(result) > 8192:
        raise ValueError("Component review exceeds the 8192-component cap.")
    return result


def _component_boundary_record(mesh: Any, record: Dict[str, Any]) -> Dict[str, Any]:
    incidence = {index: 0 for index in record["edge_indices"]}
    for polygon_index in record["polygon_indices"]:
        for loop_index in mesh.polygons[polygon_index].loop_indices:
            edge_index = mesh.loops[loop_index].edge_index
            if edge_index not in incidence:
                raise ValueError("Polygon loop references an edge outside its component.")
            incidence[edge_index] += 1
    boundary = sorted(index for index, count in incidence.items() if count == 1)
    loose = sorted(index for index, count in incidence.items() if count == 0)
    non_manifold = sorted(index for index, count in incidence.items() if count > 2)
    adjacency: Dict[int, List[int]] = {}
    for edge_index in boundary:
        left, right = mesh.edges[edge_index].vertices
        adjacency.setdefault(left, []).append(right)
        adjacency.setdefault(right, []).append(left)
    unseen, groups = set(adjacency), []
    while unseen:
        pending, observed = [min(unseen)], set()
        while pending:
            value = pending.pop()
            if value in observed:
                continue
            observed.add(value)
            pending.extend(adjacency[value])
        unseen -= observed
        groups.append(sorted(observed))
    closed = sum(1 for group in groups if group and all(len(adjacency[index]) == 2 for index in group))
    return {"boundary_edge_indices": boundary, "loose_edge_indices": loose, "non_manifold_edge_indices": non_manifold,
            "boundary_graph_components": len(groups), "closed_boundary_loops": closed,
            "open_boundary_graphs": len(groups) - closed, "boundary_is_not_automatically_a_hole": True}


def _component_uv_record(mesh: Any, polygon_indices: List[int], layer: Any) -> Dict[str, Any]:
    polygon_indices = sorted(polygon_indices)
    owner = {value: value for value in polygon_indices}
    def find(value: int) -> int:
        while owner[value] != value:
            owner[value] = owner[owner[value]]
            value = owner[value]
        return value
    def union(left: int, right: int) -> None:
        left, right = find(left), find(right)
        if left != right:
            owner[max(left, right)] = min(left, right)
    signatures: Dict[Any, List[int]] = {}
    values = []
    for polygon_index in polygon_indices:
        polygon = mesh.polygons[polygon_index]
        loops = list(polygon.loop_indices)
        for position, loop_index in enumerate(loops):
            following = loops[(position + 1) % len(loops)]
            uv = _locator_numbers(list(layer.data[loop_index].uv), 2, "component UV")
            uv_next = _locator_numbers(list(layer.data[following].uv), 2, "component UV")
            values.append({"loop_index": loop_index, "uv": uv})
            signature = (mesh.loops[loop_index].edge_index, tuple(sorted((tuple(uv), tuple(uv_next)))))
            signatures.setdefault(signature, []).append(polygon_index)
    for polygons in signatures.values():
        for polygon in polygons[1:]:
            union(polygons[0], polygon)
    islands: Dict[int, List[int]] = {}
    for polygon in polygon_indices:
        islands.setdefault(find(polygon), []).append(polygon)
    coordinates = [coordinate for value in values for coordinate in value["uv"]]
    uv_pairs = [value["uv"] for value in values]
    return {"loop_values": sorted(values, key=lambda row: row["loop_index"]), "loop_values_sha256": _promotion_digest(values),
            "uv_bounds": {"min": [min(row[axis] for row in uv_pairs) for axis in range(2)],
                          "max": [max(row[axis] for row in uv_pairs) for axis in range(2)]} if coordinates else None,
            "uv_island_count": len(islands), "uv_islands": sorted((sorted(value) for value in islands.values()), key=lambda row: row[0])}


def _component_material_record(job: Path, material: Any) -> Dict[str, Any]:
    if material is None:
        return {"name": None}
    nodes, links, images = [], [], []
    if material.use_nodes and material.node_tree is not None:
        for node in material.node_tree.nodes:
            nodes.append({"name": node.name, "type": node.bl_idname,
                          "inputs": [(socket.identifier, _promotion_value(socket.default_value) if hasattr(socket, "default_value") else None) for socket in node.inputs],
                          "outputs": [(socket.identifier, _promotion_value(socket.default_value) if hasattr(socket, "default_value") else None) for socket in node.outputs]})
            image = getattr(node, "image", None)
            if image is not None:
                packed = [hashlib.sha256(item.packed_file.data).hexdigest().upper() for item in image.packed_files]
                path = Path(bpy.path.abspath(image.filepath)).resolve() if image.filepath else None
                inside_job = False
                if path is not None:
                    try:
                        path.relative_to(job)
                        inside_job = True
                    except ValueError:
                        pass
                images.append({"node": node.name, "name": image.name, "filepath": image.filepath,
                               "packed_sha256": packed, "same_job_file_sha256": file_sha256(path) if not packed and inside_job and path.is_file() else None,
                               "external_unpacked_reference": bool(not packed and path is not None and not inside_job)})
        links = sorted((link.from_node.name, link.from_socket.identifier, link.to_node.name, link.to_socket.identifier) for link in material.node_tree.links)
    result = {"name": material.name, "library": material.library.filepath if material.library else None,
              "use_nodes": bool(material.use_nodes), "diffuse_color": _promotion_value(material.diffuse_color),
              "properties": _promotion_properties(material), "nodes": nodes, "links": links, "images": images}
    result["graph_sha256"] = _promotion_digest(result)
    return result


def _component_source_record(job: Path, mesh_obj: Any) -> Dict[str, Any]:
    mesh = mesh_obj.data
    if (not 1 <= len(mesh.vertices) <= 250000 or len(mesh.polygons) > 500000 or len(mesh.loops) > 1500000
            or len(mesh.edges) > 1000000 or len(mesh.uv_layers) > 8 or len(mesh_obj.vertex_groups) > 256 or len(mesh.materials) > 64):
        raise ValueError("Component-review source exceeds explicit geometry, UV, group, or material caps.")
    world_inverse = _mesh_region_matrix(mesh_obj.matrix_world, "component-review mesh world")
    normal_world = world_inverse.to_3x3().transposed()
    catalog = _component_index_catalog(len(mesh.vertices),
                                       ((edge.index, tuple(edge.vertices)) for edge in mesh.edges),
                                       ((polygon.index, tuple(polygon.vertices)) for polygon in mesh.polygons))
    polygon_to_component = {polygon: row["component_id"] for row in catalog for polygon in row["polygon_indices"]}
    for row in catalog:
        loops = sorted(loop_index for polygon_index in row["polygon_indices"] for loop_index in mesh.polygons[polygon_index].loop_indices)
        row["loop_indices"] = loops
        row["triangle_count"] = sum(max(0, len(mesh.polygons[index].vertices) - 2) for index in row["polygon_indices"])
        row["degenerate_polygon_indices"] = sorted(index for index in row["polygon_indices"] if len(set(mesh.polygons[index].vertices)) < 3 or mesh.polygons[index].area <= 1e-12)
        row.update(_component_boundary_record(mesh, row))
        has_faces, has_loose = bool(row["polygon_indices"]), bool(row["loose_edge_indices"])
        row["topology_class"] = "mixed" if has_faces and has_loose else ("surface" if has_faces else ("wire" if row["edge_indices"] else "point"))
        positions = []
        for index in row["vertex_indices"]:
            vertex = mesh.vertices[index]
            point = _locator_numbers(list(vertex.co), 3, "component position")
            world_point = _locator_numbers(list(mesh_obj.matrix_world @ vertex.co), 3, "component world position")
            normal = _locator_numbers(list(vertex.normal), 3, "component normal")
            defined = Vector(normal).length > 1e-12
            world_normal = _mesh_region_normal(vertex.normal, normal_world) if defined else [0.0, 0.0, 0.0]
            weights = []
            for assignment in vertex.groups:
                if not 0 <= assignment.group < len(mesh_obj.vertex_groups) or not math.isfinite(assignment.weight):
                    raise ValueError("Component review found an invalid vertex-group assignment.")
                weights.append({"group_index": assignment.group, "group_name": mesh_obj.vertex_groups[assignment.group].name, "weight": float(assignment.weight)})
            positions.append({"vertex_index": index, "object_position": point, "world_position": world_point,
                              "object_normal": normal, "world_normal": world_normal, "normal_defined": defined, "weights": weights})
        row["vertices"] = positions
        row["object_centroid"] = [sum(value["object_position"][axis] for value in positions) / len(positions) for axis in range(3)]
        row["world_centroid"] = [sum(value["world_position"][axis] for value in positions) / len(positions) for axis in range(3)]
        row["object_bounds"] = {"min": [min(value["object_position"][axis] for value in positions) for axis in range(3)],
                                "max": [max(value["object_position"][axis] for value in positions) for axis in range(3)]}
        row["world_bounds"] = {"min": [min(value["world_position"][axis] for value in positions) for axis in range(3)],
                               "max": [max(value["world_position"][axis] for value in positions) for axis in range(3)]}
        row["edges"] = [{"edge_index": index, "vertex_indices": list(mesh.edges[index].vertices)} for index in row["edge_indices"]]
        row["polygons"] = [{"polygon_index": index, "vertex_indices": list(mesh.polygons[index].vertices),
                            "loop_indices": list(mesh.polygons[index].loop_indices), "material_index": int(mesh.polygons[index].material_index)}
                           for index in row["polygon_indices"]]
        row["loops"] = [{"loop_index": index, "vertex_index": int(mesh.loops[index].vertex_index), "edge_index": int(mesh.loops[index].edge_index),
                         "object_normal": _locator_numbers(list(mesh.corner_normals[index].vector), 3, "component corner normal"),
                         "world_normal": _mesh_region_normal(mesh.corner_normals[index].vector, normal_world),
                         "uvs": {layer.name: _locator_numbers(list(layer.data[index].uv), 2, "component UV") for layer in mesh.uv_layers}}
                        for index in loops]
        row["uv_layers"] = {layer.name: _component_uv_record(mesh, row["polygon_indices"], layer) for layer in mesh.uv_layers}
        material_counts: Dict[int, Dict[str, int]] = {}
        for polygon_index in row["polygon_indices"]:
            polygon = mesh.polygons[polygon_index]
            slot = material_counts.setdefault(int(polygon.material_index), {"polygons": 0, "loops": 0})
            slot["polygons"] += 1
            slot["loops"] += len(polygon.loop_indices)
        row["material_coverage"] = [{"material_index": index, "material_name": mesh.materials[index].name if 0 <= index < len(mesh.materials) and mesh.materials[index] else None,
                                     **counts} for index, counts in sorted(material_counts.items())]
        row["membership_sha256"] = _promotion_digest({key: row[key] for key in ("vertex_indices", "edge_indices", "polygon_indices", "loop_indices")})
    result = {"mesh_name": mesh_obj.name, "mesh_data_name": mesh.name, "source_topology_sha256": _mesh_region_topology(mesh),
              "source_counts": {"vertices": len(mesh.vertices), "edges": len(mesh.edges), "polygons": len(mesh.polygons), "loops": len(mesh.loops), "components": len(catalog)},
              "object_transform": {"matrix_world": _locator_matrix_record(mesh_obj.matrix_world), "matrix_world_inverse": _locator_matrix_record(world_inverse),
                                   "location": _locator_numbers(list(mesh_obj.location), 3, "component object location"),
                                   "rotation_euler": _locator_numbers(list(mesh_obj.rotation_euler), 3, "component object rotation"),
                                   "scale": _locator_numbers(list(mesh_obj.scale), 3, "component object scale")},
              "material_slots": [_component_material_record(job, material) for material in mesh.materials], "components": catalog,
              "polygon_component_ids_sha256": _promotion_digest(sorted(polygon_to_component.items()))}
    result["component_catalog_sha256"] = _promotion_digest(catalog)
    return result


def _component_integrity(mesh_obj: Any, source_record: Dict[str, Any]) -> Dict[str, Any]:
    inventories = {}
    for label, collection in (("objects", bpy.data.objects), ("meshes", bpy.data.meshes), ("materials", bpy.data.materials),
                              ("images", bpy.data.images), ("collections", bpy.data.collections), ("scenes", bpy.data.scenes),
                              ("actions", bpy.data.actions), ("cameras", bpy.data.cameras), ("lights", bpy.data.lights), ("curves", bpy.data.curves)):
        inventories[label] = sorted((block.name, int(block.users), block.library.filepath if block.library else None) for block in collection)
    scenes = {scene.name: {"frame": int(scene.frame_current), "subframe": float(scene.frame_subframe),
                           "camera": scene.camera.name if scene.camera else None, "objects": sorted(obj.name for obj in scene.objects),
                           "render": (scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath)}
              for scene in bpy.data.scenes}
    objects = {obj.name: {"type": obj.type, "data": obj.data.name if obj.data else None, "world": _locator_matrix_record(obj.matrix_world),
                          "hide_render": bool(obj.hide_render), "hide_viewport": bool(obj.hide_viewport), "hide_get": bool(obj.hide_get()),
                          "selected": bool(obj.select_get()), "collections": sorted(owner.name for owner in obj.users_collection), "properties": _promotion_properties(obj)}
               for obj in bpy.data.objects}
    sections = {"inventory": inventories, "scenes": scenes, "objects": objects,
                "actions": _mesh_region_action_integrity(), "selected_source": source_record,
                "context": {"active_object": bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
                            "selected_mesh": mesh_obj.name}}
    return {"sha256": _promotion_digest(sections), "sections": {key: _promotion_digest(value) for key, value in sections.items()}}


def _component_emission_material(name: str, color: Tuple[float, float, float, float]) -> Any:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    emission = shader.inputs.get("Emission Color") or shader.inputs.get("Emission")
    if emission is not None:
        emission.default_value = color
    strength = shader.inputs.get("Emission Strength")
    if strength is not None:
        strength.default_value = 1.0
    material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def _render_component_group(job: Path, request_id: str, mesh_obj: Any, components: List[Dict[str, Any]], views: List[str]) -> List[Dict[str, Any]]:
    prefix = f"HOI4_COMPONENT_REVIEW_{request_id}"
    old_scene = bpy.context.window.scene
    before_images = {image.name for image in bpy.data.images}
    scene = bpy.data.scenes.new(prefix)
    temporary_objects, temporary_meshes, temporary_curves, temporary_materials = [], [], [], []
    camera_data = bpy.data.cameras.new(prefix + "_Camera")
    camera = bpy.data.objects.new(prefix + "_Camera", camera_data)
    temporary_objects.append(camera)
    scene.collection.objects.link(camera)
    scene.camera = camera
    world = bpy.data.worlds.new(prefix + "_World")
    scene.world = world
    world.color = (0.01, 0.012, 0.016)
    palette = ((0.95, 0.20, 0.12, 1.0), (0.15, 0.75, 1.0, 1.0), (1.0, 0.72, 0.08, 1.0), (0.25, 1.0, 0.32, 1.0),
               (0.85, 0.25, 1.0, 1.0), (1.0, 0.42, 0.68, 1.0), (0.20, 1.0, 0.85, 1.0), (0.65, 0.78, 1.0, 1.0))
    dim = _component_emission_material(prefix + "_Dim", (0.055, 0.065, 0.08, 1.0))
    colors = [_component_emission_material(f"{prefix}_Color_{index}", palette[index % len(palette)]) for index in range(len(components))]
    temporary_materials.extend([dim, *colors])
    body_mesh = mesh_obj.data.copy()
    body_mesh.name = prefix + "_Mesh"
    temporary_meshes.append(body_mesh)
    body = bpy.data.objects.new(prefix + "_Body", body_mesh)
    temporary_objects.append(body)
    scene.collection.objects.link(body)
    body.matrix_world = mesh_obj.matrix_world.copy()
    body_mesh.materials.clear()
    body_mesh.materials.append(dim)
    for material in colors:
        body_mesh.materials.append(material)
    polygon_colors = {polygon: index + 1 for index, row in enumerate(components) for polygon in row["polygon_indices"]}
    for polygon in body_mesh.polygons:
        polygon.material_index = polygon_colors.get(polygon.index, 0)
    points = [mesh_obj.matrix_world @ Vector(corner) for corner in mesh_obj.bound_box]
    low = Vector([min(point[axis] for point in points) for axis in range(3)])
    high = Vector([max(point[axis] for point in points) for axis in range(3)])
    center, dimensions = (low + high) * 0.5, high - low
    span = max(float(max(dimensions)), 0.1)
    distance = span * 2.5
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = span * 1.55
    camera.data.clip_start = max(span * 0.001, 0.001)
    camera.data.clip_end = distance * 4.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    view_positions = {"front": (center.x, center.y - distance, center.z), "rear": (center.x, center.y + distance, center.z),
                      "left": (center.x - distance, center.y, center.z), "right": (center.x + distance, center.y, center.z),
                      "top": (center.x, center.y, center.z + distance),
                      "three_quarter": (center.x + distance * 0.7, center.y - distance * 0.7, center.z + distance * 0.2)}
    previews = []
    bpy.context.window.scene = scene
    try:
        for view in views:
            camera.location = view_positions[view]
            camera_point_at(camera, center)
            bpy.context.view_layer.update()
            labels, swatches, leaders = [], [], []
            for index, row in enumerate(components):
                anchor = camera.matrix_world @ Vector((-span * 0.70, span * (0.52 - index * 0.065), -span * 0.05))
                text_data = bpy.data.curves.new(f"{prefix}_{view}_{index}_Text", type="FONT")
                temporary_curves.append(text_data)
                text_data.body = row["component_id"]
                text_data.align_x = "LEFT"
                text_data.size = span * 0.035
                label = bpy.data.objects.new(f"{prefix}_{view}_{index}_Label", text_data)
                temporary_objects.append(label)
                scene.collection.objects.link(label)
                label.data.materials.append(colors[index])
                label.location = anchor
                label.rotation_mode = "QUATERNION"
                label.rotation_quaternion = camera.rotation_quaternion.copy()
                labels.append(label)
                swatch_mesh = bpy.data.meshes.new(f"{prefix}_{view}_{index}_SwatchMesh")
                temporary_meshes.append(swatch_mesh)
                size = span * 0.018
                swatch_mesh.from_pydata([(-size, -size, 0), (size, -size, 0), (size, size, 0), (-size, size, 0)], [], [(0, 1, 2, 3)])
                swatch = bpy.data.objects.new(f"{prefix}_{view}_{index}_Swatch", swatch_mesh)
                temporary_objects.append(swatch)
                scene.collection.objects.link(swatch)
                swatch.data.materials.append(colors[index])
                swatch.location = anchor + camera.matrix_world.to_quaternion() @ Vector((-span * 0.035, span * 0.008, 0))
                swatch.rotation_mode = "QUATERNION"
                swatch.rotation_quaternion = camera.rotation_quaternion.copy()
                swatches.append(swatch)
                leader_data = bpy.data.curves.new(f"{prefix}_{view}_{index}_Leader", type="CURVE")
                temporary_curves.append(leader_data)
                leader_data.dimensions = "3D"
                leader_data.bevel_depth = span * 0.0015
                spline = leader_data.splines.new("POLY")
                spline.points.add(1)
                centroid = Vector(row["world_centroid"])
                spline.points[0].co = (*centroid, 1.0)
                spline.points[1].co = (*anchor, 1.0)
                leader = bpy.data.objects.new(f"{prefix}_{view}_{index}_Leader", leader_data)
                temporary_objects.append(leader)
                scene.collection.objects.link(leader)
                leader.data.materials.append(colors[index])
                leaders.append(leader)
            output = job / "blender" / "previews" / f"component_review_{request_id}_{view}.png"
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists():
                raise FileExistsError(f"Component-review preview already exists: {output}")
            scene.render.filepath = str(output)
            bpy.ops.render.render(write_still=True)
            if not output.is_file() or output.stat().st_size < 1:
                raise RuntimeError("Component-review render did not produce a nonempty PNG.")
            previews.append({"view": view, "path": output.relative_to(job).as_posix(), "bytes": output.stat().st_size,
                             "sha256": file_sha256(output), "component_ids": [row["component_id"] for row in components],
                             "label_policy": "fixed_legend_color_swatch_and_centroid_leader", "small_or_occluded_identity_requires_visual_review": True})
            for obj in [*labels, *swatches, *leaders]:
                bpy.data.objects.remove(obj, do_unlink=True)
                temporary_objects.remove(obj)
    finally:
        bpy.context.window.scene = old_scene
        for obj in reversed(temporary_objects):
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        for data in reversed(temporary_meshes):
            if data.name in bpy.data.meshes and data.users == 0:
                bpy.data.meshes.remove(data)
        for data in reversed(temporary_curves):
            if data.name in bpy.data.curves and data.users == 0:
                bpy.data.curves.remove(data)
        for material in reversed(temporary_materials):
            if material.name in bpy.data.materials and material.users == 0:
                bpy.data.materials.remove(material)
        if camera_data.name in bpy.data.cameras and camera_data.users == 0:
            bpy.data.cameras.remove(camera_data)
        if scene.name in bpy.data.scenes:
            bpy.data.scenes.remove(scene)
        if world.name in bpy.data.worlds and world.users == 0:
            bpy.data.worlds.remove(world)
        for image in list(bpy.data.images):
            if image.name not in before_images:
                bpy.data.images.remove(image)
    return previews


def review_humanoid_components(req: Dict[str, Any]) -> Dict[str, Any]:
    context = _component_review_inputs(req)
    try:
        bpy.ops.wm.open_mainfile(filepath=str(context["source"]), use_scripts=False)
        mesh_obj = bpy.context.scene.objects.get(context["mesh_name"])
        if mesh_obj is None or mesh_obj.type != "MESH" or mesh_obj.library or mesh_obj.override_library or mesh_obj.data.library or mesh_obj.data.override_library:
            raise ValueError("Component review requires one exact local mesh object and data block.")
        if (mesh_obj.parent is not None or mesh_obj.modifiers or mesh_obj.constraints or mesh_obj.data.shape_keys
                or mesh_obj.animation_data or mesh_obj.data.animation_data):
            raise ValueError("Component review requires an unparented unrigged static mesh without modifiers, shape keys, constraints, or animation.")
        if any(value <= 0 for value in mesh_obj.scale):
            raise ValueError("Component review rejects negative or singular object scale.")
        source_record = _component_source_record(context["job"], mesh_obj)
        before = _component_integrity(mesh_obj, source_record)
        by_id = {row["component_id"]: row for row in source_record["components"]}
        if context["component_ids"]:
            missing = [value for value in context["component_ids"] if value not in by_id]
            if missing:
                raise ValueError(f"Unknown component_ids: {missing}")
            selected = [by_id[value] for value in context["component_ids"]]
            offset = None
        else:
            offset = context["component_offset"]
            if offset >= len(source_record["components"]):
                raise ValueError("Component-review page offset exceeds the component count.")
            selected = source_record["components"][offset:offset + context["component_limit"]]
        try:
            previews = _render_component_group(context["job"], context["request_id"], mesh_obj, selected, context["preview_view_names"])
        finally:
            after_record = _component_source_record(context["job"], mesh_obj)
            after = _component_integrity(mesh_obj, after_record)
            if before != after or source_record != after_record:
                changed = sorted(key for key in before["sections"] if before["sections"][key] != after["sections"].get(key))
                raise RuntimeError(f"Read-only component review changed original scene or mesh data sections: {changed}")
        next_offset = None if offset is None or offset + len(selected) >= len(source_record["components"]) else offset + len(selected)
        result = {"operation": "review_humanoid_components", "blend": context["source"].relative_to(context["job"]).as_posix(),
                  "source_sha256": context["expected_source_sha256"], "source_bytes": context["source_bytes"], "source_immutable": True,
                  "mesh_name": mesh_obj.name, "mesh_data_name": mesh_obj.data.name, "source_topology_sha256": source_record["source_topology_sha256"],
                  "component_catalog_sha256": source_record["component_catalog_sha256"], "component_count": len(source_record["components"]),
                  "component_page": {"explicit_ids": context["component_ids"], "offset": offset, "returned": len(selected), "limit": context["component_limit"],
                                     "truncated": next_offset is not None, "next_offset": next_offset, "component_ids": [row["component_id"] for row in selected]},
                  "source_record": source_record, "previews": previews, "render_group": True,
                  "component_identity_policy": "source_vertex_edge_polygon_connectivity_no_position_weld_no_semantic_classification",
                  "original_data_integrity_sha256": before["sha256"], "original_data_section_sha256": before["sections"],
                  "original_data_unchanged": True, "checkpoint_saved": False, "new_provider_call": False,
                  "semantic_component_acceptance": False, "weapon_separability_approved": False}
        # The report is evidence, not a presentation file. Compact separators
        # preserve every exact member while keeping dense production meshes
        # inside the reviewed 64 MiB ceiling without raising that ceiling.
        encoded = (json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
        if len(encoded) > 64 * 1024 * 1024:
            raise ValueError("Component-review report exceeds the 64 MiB full-membership ceiling.")
        report_path = context["job"] / "blender" / "reports" / f"component_review_{context['request_id']}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        if report_path.exists():
            raise FileExistsError(f"Component-review report already exists: {report_path}")
        report_path.write_bytes(encoded)
        result["report"] = report_path.relative_to(context["job"]).as_posix()
        result["report_bytes"] = len(encoded)
        result["report_sha256"] = file_sha256(report_path)
        return result
    finally:
        if file_sha256(context["source"]) != context["expected_source_sha256"] or context["source"].stat().st_size != context["source_bytes"]:
            raise RuntimeError("Read-only component review changed its source checkpoint.")


def inspect(req: Dict[str, Any]) -> Dict[str, Any]:
    if req["payload"].get("material_visibility") is not None:
        validate_preview_region(req["payload"].get("preview_region"), req["payload"].get("preview_resolution", 512))
        from material_visibility_probe import run_material_visibility_probe
        return run_material_visibility_probe(req, bpy=bpy, render_previews=render_previews, action_hash=_mesh_region_action_hash)
    if req["payload"].get("include_action_channels") is not None:
        return inspect_action_channels(req)
    if req["payload"].get("mesh_region") is not None:
        return inspect_mesh_region(req)
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
    inspected_target_armature = None
    inspected_action_sha256 = None
    muted_nla_tracks: List[str] = []
    if action_name:
        rigs = armatures()
        requested_target_armature = str(req["payload"].get("target_armature_name") or "")
        if requested_target_armature:
            matching_rigs = [
                rig for rig in armatures(working_only=False)
                if rig.name == requested_target_armature
            ]
            if len(matching_rigs) != 1:
                raise RuntimeError(
                    f"Action inspection requires one exact target armature named {requested_target_armature}."
                )
            inspected_target_armature = matching_rigs[0]
            inspected_target_armature["hoi4_working"] = True
            promoted_meshes = []
            for obj in mesh_objects(working_only=False):
                if obj.parent is inspected_target_armature or any(
                    modifier.type == "ARMATURE" and modifier.object is inspected_target_armature
                    for modifier in obj.modifiers
                ):
                    obj["hoi4_working"] = True
                    obj.hide_render = False
                    promoted_meshes.append(obj.name)
            if not promoted_meshes:
                raise RuntimeError(
                    f"Action inspection found no direct mesh consumers for {requested_target_armature}."
                )
            rigs = [inspected_target_armature]
        action = bpy.data.actions.get(action_name)
        if len(rigs) != 1 or action is None:
            raise RuntimeError(f"Action inspection selection failed for {action_name}.")
        rigs[0].animation_data_create()
        for track in rigs[0].animation_data.nla_tracks:
            track.mute = True
            muted_nla_tracks.append(track.name)
        rigs[0].animation_data.action = action
        action_records = []
        for fcurve, slot in action_fcurves(action):
            action_records.append(
                {
                    "slot": getattr(slot, "identifier", None),
                    "data_path": fcurve.data_path,
                    "array_index": int(fcurve.array_index),
                    "keyframes": [
                        [
                            float(point.co.x),
                            float(point.co.y),
                            str(point.interpolation),
                        ]
                        for point in fcurve.keyframe_points
                    ],
                }
            )
        inspected_action_sha256 = hashlib.sha256(
            json.dumps(action_records, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest().upper()
        requested_frame = int(req["payload"].get("preview_frame", -1))
        if requested_frame < 0:
            start, end = action.frame_range
            requested_frame = int(round((start + end) * 0.5))
        bpy.context.scene.frame_set(requested_frame)
        bpy.context.view_layer.update()
    if req["payload"].get("render_previews"):
        runtime_stem = safe_name(str(req["payload"].get("runtime_stem") or blend.stem))
        region=req['payload'].get('preview_region')
        resolution=req['payload'].get('preview_resolution',512)
        validate_preview_region(region,resolution)
        if region is not None or resolution != 512:
            expected=req['payload'].get('expected_source_sha256','')
            if not expected or file_sha256(blend)!=expected.upper():
                raise ValueError('Focused preview requires exact source SHA-256.')
            runtime_stem=runtime_stem+'_focused_'+req['request_id'][:12]
        preview_paths = render_previews(job,runtime_stem,req['payload'].get('preview_view_names') or None,preview_region=region,preview_resolution=resolution)
    return {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "inspected_target_armature": inspected_target_armature.name if inspected_target_armature else None,
        "inspected_action_sha256": inspected_action_sha256,
        "muted_nla_tracks": muted_nla_tracks,
        "objects": [
            {
                "name": obj.name,
                "type": obj.type,
                "parent": obj.parent.name if obj.parent else None,
                "parent_type": obj.parent_type if obj.parent else None,
                "parent_bone": obj.parent_bone if obj.parent_type == "BONE" else None,
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
        "locators": locator_records(),
        "rig_and_actions": action_metrics(),
        "evaluated_actions": evaluated_action_metrics(req["payload"].get("action_name", ""), req["payload"].get("evaluated_frames"), req["payload"].get("target_armature_name", "")),
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
        relink_nodes = list(image_nodes())
        if not relink_nodes:
            relink_nodes = all_image_nodes()
        if not relink_nodes:
            # io_pdx_mesh may retain image datablocks while omitting source
            # material tags; the explicit caller mapping is safe here.
            relink_nodes = [(None, image) for image in bpy.data.images if image.name in dds_map]
        for _, image in relink_nodes:
            original_name = image.name
            dds_rel = dds_map.get(original_name)
            if not dds_rel:
                image_stem = Path(original_name).stem.lower()
                for mapped_name, mapped_rel in dds_map.items():
                    if Path(mapped_name).stem.lower() in image_stem:
                        dds_rel = mapped_rel
                        break
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


def exported_mesh_streams(text_path: Path) -> List[Dict[str, Any]]:
    """Read actual arrays at object/material depth through the locked parser."""
    from skeletal_export_partition import exported_mesh_streams as read_streams
    return read_streams(text_path)


PROMOTION_METADATA_KEYS = (
    "hoi4_working", "hoi4_promotion_operation", "hoi4_promotion_source",
    "hoi4_promotion_source_sha256", "hoi4_promotion_validation",
    "hoi4_promotion_validation_sha256", "hoi4_promotion_job",
)


def _promotion_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest().upper()


def _promotion_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Promotion fingerprint contains a nonfinite value.")
        return value
    if isinstance(value, bpy.types.ID):
        return {"id_type": value.bl_rna.identifier, "name": value.name_full, "library": value.library.filepath if value.library else None}
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if isinstance(value, dict):
        return {str(key): _promotion_value(item) for key, item in value.items()}
    if isinstance(value, set):
        return sorted(_promotion_value(item) for item in value)
    # mathutils values can implement the sequence protocol without __iter__.
    # Index every element and recurse; never stringify or round numeric data.
    if hasattr(value, "__len__") and hasattr(value, "__getitem__"):
        return [_promotion_value(value[index]) for index in range(len(value))]
    if hasattr(value, "__iter__"):
        return [_promotion_value(item) for item in value]
    raise ValueError(f"Unsupported promotion fingerprint value: {type(value).__name__}")


def _promotion_properties(block: Any, exclude: Iterable[str] = ()) -> Dict[str, Any]:
    return {key: _promotion_value(block[key]) for key in sorted(block.keys()) if key not in exclude}


def _promotion_scalars(block: Any) -> Dict[str, Any]:
    """Read finite scalar RNA settings and ID references, without traversing arbitrary RNA graphs."""
    result = {}
    for prop in block.bl_rna.properties:
        if prop.identifier == "rna_type":
            continue
        if prop.type in {"BOOLEAN", "INT", "FLOAT", "STRING", "ENUM"} and not prop.is_readonly:
            result[prop.identifier] = _promotion_value(getattr(block, prop.identifier))
        elif prop.type == "POINTER":
            value = getattr(block, prop.identifier)
            if value is None or isinstance(value, bpy.types.ID):
                result[prop.identifier] = _promotion_value(value)
    return result


def _promotion_path(job: Path, value: Any, suffix: str, *, missing: bool = False) -> Path:
    if not isinstance(value, str) or not value or value != value.strip() or ".." in Path(value).parts or "\\" in value:
        raise ValueError("Promotion paths must be explicit job-relative forward-slash paths without traversal.")
    path = within(job, value, allow_missing=missing)
    if path.suffix.lower() != suffix or (not missing and not path.is_file()):
        raise ValueError(f"Promotion requires a {suffix} file: {value}")
    return path


def _promotion_unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate validation JSON key: {key}")
        result[key] = value
    return result


def _promotion_inputs(req: Dict[str, Any]) -> Dict[str, Any]:
    payload = req["payload"]
    expected = {"blend_rel", "expected_source_sha256", "validation_rel", "expected_validation_sha256", "checkpoint_rel", "target_armature_name", "target_mesh_names", "mesh_rel", "expected_mesh_sha256", "anim_rel", "expected_anim_sha256"}
    if not isinstance(payload, dict) or set(payload) != expected:
        raise ValueError("promote_accepted_reimport accepts only its exact hashed-proof contract.")
    _locator_exact_name(req.get("job_id"), "job_id", locator=True)
    job = Path(req["job_root"]).resolve()
    inputs = {}
    for role, field, hash_field, suffix in (
        ("source", "blend_rel", "expected_source_sha256", ".blend"),
        ("validation", "validation_rel", "expected_validation_sha256", ".json"),
        ("mesh", "mesh_rel", "expected_mesh_sha256", ".mesh"),
        ("anim", "anim_rel", "expected_anim_sha256", ".anim"),
    ):
        path = _promotion_path(job, payload[field], suffix)
        expected_hash = payload[hash_field]
        if not isinstance(expected_hash, str) or re.fullmatch(r"[0-9A-Fa-f]{64}", expected_hash) is None:
            raise ValueError(f"{hash_field} must be an explicit SHA-256.")
        if path.stat().st_size == 0 or file_sha256(path) != expected_hash.upper():
            raise ValueError(f"Promotion {role} checksum mismatch or empty input.")
        inputs[role] = {"path": path, "relative": path.relative_to(job).as_posix(), "sha256": expected_hash.upper(), "bytes": path.stat().st_size}
    output = _promotion_path(job, payload["checkpoint_rel"], ".blend", missing=True)
    if output.parent != inputs["source"]["path"].parent or output.exists():
        raise ValueError("Promotion output must be a new sibling checkpoint; overwrite is forbidden.")
    report_path = within(job, f"blender/reports/promote_{output.stem}.json", allow_missing=True)
    if report_path.exists():
        raise ValueError("Promotion report already exists; overwrite is forbidden.")
    rig_name = _locator_exact_name(payload["target_armature_name"], "target_armature_name")
    mesh_names = payload["target_mesh_names"]
    if not isinstance(mesh_names, (list, tuple)) or not 1 <= len(mesh_names) <= 512:
        raise ValueError("Promotion requires one to 512 exact mesh names from the complete same-rig receipt.")
    mesh_names = [_locator_exact_name(name, "target_mesh_names") for name in mesh_names]
    if len(set(mesh_names)) != len(mesh_names) or rig_name in mesh_names:
        raise ValueError("Promotion object identities must be unique.")
    receipt = json.loads(inputs["validation"]["path"].read_text(encoding="utf-8-sig"), object_pairs_hook=_promotion_unique_pairs)
    _promotion_digest(receipt)  # Reject JSON NaN/Infinity, including otherwise unused fields.
    required = {"proof_blend", "mesh", "anim", "objects", "meshes", "armatures", "actions", "geometry", "animation_bounds", "previews", "runtime_texture_staging"}
    if not isinstance(receipt, dict) or not required.issubset(receipt) or receipt.get("status", "pass") != "pass" or receipt.get("error") or receipt.get("errors"):
        raise ValueError("Validation is not a complete successful reimport_export receipt.")
    for role, key, suffix in (("source", "proof_blend", ".blend"), ("mesh", "mesh", ".mesh"), ("anim", "anim", ".anim")):
        if _promotion_path(job, receipt[key], suffix) != inputs[role]["path"]:
            raise ValueError(f"Validation {key} does not match the explicitly hashed input.")
        hash_key = "proof_blend_sha256" if role == "source" else f"{role}_sha256"
        if hash_key in receipt and str(receipt[hash_key]).upper() != inputs[role]["sha256"]:
            raise ValueError(f"Validation {hash_key} conflicts with the accepted hash.")
    def rows(key: str) -> Dict[str, Any]:
        values = receipt[key]
        if not isinstance(values, list) or not values or any(not isinstance(row, dict) or not isinstance(row.get("name"), str) for row in values):
            raise ValueError(f"Invalid validation {key} identities.")
        by_name = {row["name"]: row for row in values}
        if len(by_name) != len(values):
            raise ValueError(f"Duplicate validation {key} identities.")
        return by_name
    objects, meshes, rigs = rows("objects"), rows("meshes"), rows("armatures")
    if set(meshes) != set(mesh_names) or set(rigs) != {rig_name}:
        raise ValueError("Validation does not identify exactly the requested rig and meshes.")
    if objects.get(rig_name, {}).get("type") != "ARMATURE" or any(objects.get(name, {}).get("type") != "MESH" for name in mesh_names):
        raise ValueError("Validation object types do not match the promotion targets.")
    if {name for name, row in objects.items() if row.get("type") == "MESH"} != set(mesh_names) or {name for name, row in objects.items() if row.get("type") == "ARMATURE"} != {rig_name}:
        raise ValueError("Validation has undeclared mesh/armature identities.")
    if type(rigs[rig_name].get("bones")) is not int or rigs[rig_name]["bones"] < 1:
        raise ValueError("Validation lacks a positive bone count.")
    for row in meshes.values():
        if any(type(row.get(key)) is not int or row[key] < 1 for key in ("vertices", "polygons")) or not isinstance(row.get("materials"), list) or not row["materials"] or any(not isinstance(name, str) or not name for name in row["materials"]):
            raise ValueError("Validation lacks complete mesh counts/material bindings.")
    actions = receipt["actions"]
    if not isinstance(actions, list) or not actions or any(not isinstance(name, str) or not name for name in actions) or len(set(actions)) != len(actions):
        raise ValueError("Validation must identify a nonempty unique existing action set.")
    bounds = receipt["animation_bounds"]
    if not isinstance(bounds, list) or not bounds or any(not isinstance(row, dict) or type(row.get("frame")) is not int or any(not isinstance(row.get(key), list) or len(row[key]) != 3 for key in ("bounds_min", "bounds_max", "dimensions")) for row in bounds):
        raise ValueError("Validation lacks successful animated reimport sample evidence.")
    for row in bounds:
        for key in ("bounds_min", "bounds_max", "dimensions"):
            _locator_numbers(row[key], 3, f"validation {key}")
        if any(row["bounds_min"][index] > row["bounds_max"][index] or row["dimensions"][index] < 0 for index in range(3)):
            raise ValueError("Validation has invalid animated bounds.")
    if not isinstance(receipt["previews"], list) or not receipt["previews"] or not isinstance(receipt["runtime_texture_staging"], list) or not isinstance(receipt["geometry"], dict):
        raise ValueError("Validation lacks complete reimport geometry/preview evidence.")
    if any(type(receipt["geometry"].get(key)) is not int or receipt["geometry"][key] < 1 for key in ("objects", "vertices", "polygons", "triangles")) or receipt["geometry"]["objects"] != len(meshes):
        raise ValueError("Validation lacks complete positive geometry counts.")
    return {"job": job, "inputs": inputs, "output": output, "report_path": report_path, "receipt": receipt, "rig_name": rig_name, "mesh_names": mesh_names, "receipt_objects": objects, "receipt_meshes": meshes, "receipt_rigs": rigs}


def _promotion_targets(context: Dict[str, Any]) -> List[bpy.types.Object]:
    targets = []
    for name, kind in [(context["rig_name"], "ARMATURE")] + [(name, "MESH") for name in context["mesh_names"]]:
        matches = [obj for obj in bpy.data.objects if obj.name == name]
        if len(matches) != 1 or matches[0].type != kind or bpy.context.scene.objects.get(name) != matches[0]:
            raise ValueError(f"Promotion requires one exact local scene {kind}: {name}")
        obj = matches[0]
        for block in (obj, obj.data, *obj.users_collection):
            if block.library or getattr(block, "override_library", None) or block.get("hoi4_source_protected") or block.get("hoi4_reference_read_only"):
                raise ValueError("Linked, overridden, protected source/vanilla/reference data cannot be promoted.")
        scale = _locator_numbers(list(obj.matrix_world.to_scale()), 3, "promotion world scale")
        if min(scale) <= 0 or obj.matrix_world.determinant() <= 0:
            raise ValueError("Promotion requires positive nonsingular transforms without reflection.")
        if obj.get("hoi4_working") or any(key in obj for key in PROMOTION_METADATA_KEYS[1:]):
            raise ValueError("Promotion source is already working or has conflicting promotion metadata.")
        targets.append(obj)
    rig = targets[0]
    if len(rig.data.bones) != context["receipt_rigs"][rig.name].get("bones"):
        raise ValueError("Promotion bone count differs from the accepted receipt.")
    if {obj.name: obj.type for obj in bpy.context.scene.objects} != {name: row.get("type") for name, row in context["receipt_objects"].items()}:
        raise ValueError("Promotion scene inventory differs from the accepted receipt.")
    if sorted(action.name for action in bpy.data.actions) != sorted(context["receipt"]["actions"]):
        raise ValueError("Promotion action identities differ from the accepted receipt.")
    for obj in targets[1:]:
        modifiers = list(obj.modifiers)
        if len(modifiers) != 1 or modifiers[0].type != "ARMATURE" or modifiers[0].object != rig:
            raise ValueError("Promotion mesh must have exactly one modifier consuming the exact accepted rig.")
        row = context["receipt_meshes"][obj.name]
        if not obj.data.vertices or len(obj.data.polygons) != row.get("polygons") or [mat.name if mat else None for mat in obj.data.materials] != row.get("materials"):
            raise ValueError("Promotion topology/material identity differs from the accepted receipt.")
        if not obj.data.materials or any(mat is None or not mat.use_nodes or not mat.get("shader") for mat in obj.data.materials):
            raise ValueError("Promotion requires the accepted PDX material bindings.")
        if obj.data.shape_keys:
            raise ValueError("Promotion does not support shape-key proof scenes.")
    return targets


def _promotion_animation_state(block: Any) -> Any:
    animation = getattr(block, "animation_data", None)
    if animation is None:
        return None
    if animation.drivers or animation.nla_tracks:
        raise ValueError("Promotion does not support driver/NLA proof scenes.")
    return _promotion_scalars(animation)


def _promotion_attribute_record(attribute: Any) -> Dict[str, Any]:
    """Hash every component through the observed Blender 5.1 attribute RNA field."""
    fields = {"FLOAT": "value", "INT": "value", "INT8": "value", "BOOLEAN": "value", "FLOAT_VECTOR": "vector", "FLOAT2": "vector", "FLOAT_COLOR": "color", "BYTE_COLOR": "color", "QUATERNION": "value", "FLOAT4X4": "value", "INT16_2D": "value", "INT32_2D": "value", "STRING": "value"}
    field = fields.get(attribute.data_type)
    if field is None:
        raise ValueError(f"Unsupported promotion mesh attribute: {attribute.data_type}")
    values = [_promotion_value(getattr(item, field)) for item in attribute.data]
    return {"domain": attribute.domain, "type": attribute.data_type, "sha256": _promotion_digest(values)}


def _promotion_discardable_material(record: Dict[str, Any]) -> bool:
    """Only independently unconsumed, unretained local material IDs may disappear."""
    return (
        type(record["users"]) is int and record["users"] == 0
        and record["local"] is True and record["fake_user"] is False
        and record["extra_user"] is False and record["protected"] is False
        and record["tree_retained"] is False
        and record["id_consumers"] == [] and record["mesh_slots"] == []
        and record["object_slots"] == []
    )


def _promotion_material_retention(materials: Dict[str, Any]) -> Dict[str, Any]:
    """Record complete native ID consumers without changing any retention flag."""
    blocks = list(bpy.data.materials)
    user_map = bpy.data.user_map(subset=blocks)
    inventory = {}
    for material in blocks:
        if material not in user_map:
            raise ValueError("Promotion material is absent from the native ID user map.")
        tree = material.node_tree
        record = {
            "record_sha256": _promotion_digest(materials[material.name]),
            "users": material.users, "fake_user": material.use_fake_user,
            "extra_user": material.use_extra_user,
            "local": material.library is None and material.override_library is None,
            "protected": any(bool(block.get(key)) for block in (material, tree) for key in ("hoi4_source_protected", "hoi4_reference_read_only")),
            "tree_retained": bool(tree.use_fake_user or tree.use_extra_user or tree.library or tree.override_library),
            "id_consumers": sorted((_promotion_value(block) for block in user_map[material]), key=lambda row: json.dumps(row, sort_keys=True)),
            "mesh_slots": sorted((mesh.name, index) for mesh in bpy.data.meshes for index, slot in enumerate(mesh.materials) if slot == material),
            "object_slots": sorted((obj.name, index, slot.link) for obj in bpy.data.objects for index, slot in enumerate(obj.material_slots) if slot.material == material),
        }
        record["discardable_orphan"] = _promotion_discardable_material(record)
        inventory[material.name] = record
    retained = {name: materials[name] for name, row in inventory.items() if not row["discardable_orphan"]}
    return {"inventory": inventory, "retained_sha256": _promotion_digest(retained)}


def _promotion_orphan_image_consumers(record: Dict[str, Any], removed_materials: Iterable[str]) -> bool:
    """Only images whose complete consumers are independently removable materials."""
    materials = set(record["material_consumers"])
    bindings = record["material_nodes"]
    return (
        bool(materials) and materials <= set(removed_materials)
        and materials == {row["material"] for row in bindings}
        and type(record["users"]) is int and record["users"] == len(bindings)
        and record["local"] is True and record["fake_user"] is False
        and record["extra_user"] is False and record["protected"] is False
        and record["other_id_consumers"] == [] and record["retained_node_trees"] == []
    )


def _promotion_image_retention(images: Dict[str, Any], material_retention: Dict[str, Any]) -> Dict[str, Any]:
    """Cross-check native ID users, direct node references, and embedded tree ownership."""
    blocks = sorted(bpy.data.images, key=lambda block: block.name)
    materials = sorted(bpy.data.materials, key=lambda block: block.name)
    trees = [material.node_tree for material in materials]
    user_map = bpy.data.user_map(subset=blocks + trees)
    inventory = {}
    for image in blocks:
        if image not in user_map:
            raise ValueError("Promotion image is absent from the native ID user map.")
        bindings, owners, retained_trees = [], [], []
        for material in materials:
            tree = material.node_tree
            nodes = [node for node in tree.nodes if getattr(node, "image", None) == image]
            if not nodes:
                continue
            if tree not in user_map:
                raise ValueError("Promotion image consumer tree is absent from the native ID user map.")
            owners.append(material)
            bindings.extend({"material": material.name, "tree": tree.name, "node": node.name} for node in sorted(nodes, key=lambda node: node.name))
            # Fresh embedded trees have one internal user; loaded orphan trees
            # can have zero. Neither count is an independent retention claim.
            if (not tree.is_embedded_data or tree.users not in {0, 1} or user_map[tree]
                    or tree.use_fake_user or tree.use_extra_user or tree.library or tree.override_library
                    or any(bool(tree.get(key)) for key in ("hoi4_source_protected", "hoi4_reference_read_only"))):
                retained_trees.append({"material": material.name, "tree": _promotion_value(tree),
                                       "users": tree.users, "id_consumers": sorted((_promotion_value(block) for block in user_map[tree]), key=lambda row: json.dumps(row, sort_keys=True))})
        allowed_ids = set(owners) | {material.node_tree for material in owners}
        native_users = user_map[image]
        content = images[image.name]
        record = {
            "record_sha256": _promotion_digest(content), "users": image.users,
            "local": image.library is None and image.override_library is None,
            "fake_user": image.use_fake_user, "extra_user": image.use_extra_user,
            "protected": any(bool(image.get(key)) for key in ("hoi4_source_protected", "hoi4_reference_read_only")),
            "material_nodes": bindings, "material_consumers": sorted(material.name for material in owners),
            "id_consumers": sorted((_promotion_value(block) for block in native_users), key=lambda row: json.dumps(row, sort_keys=True)),
            "other_id_consumers": sorted((_promotion_value(block) for block in native_users if block not in allowed_ids), key=lambda row: json.dumps(row, sort_keys=True)),
            "retained_node_trees": retained_trees, "packed_hashes": content["packed_hashes"],
            "pixel_sha256": content["pixel_sha256"], "missing_data_sentinel": content["missing_data_sentinel"],
            "source_file": {"path": str(Path(bpy.path.abspath(image.filepath)).resolve()), "sha256": content["file_sha256"]} if content["file_sha256"] else None,
        }
        # A complete native user map must independently identify every observed node owner.
        record["consumer_map_complete"] = all(material in native_users or material.node_tree in native_users for material in owners)
        record["exclusive_orphan_consumers"] = record["consumer_map_complete"] and _promotion_orphan_image_consumers(record, [name for name, row in material_retention["inventory"].items() if row["discardable_orphan"] and _promotion_discardable_material(row)])
        inventory[image.name] = record
    return {"inventory": inventory, "content_sha256": _promotion_digest(images)}


def _promotion_reopen_comparison(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """Exact preservation except native disappearance of proven before-only orphans."""
    mismatches, removed = [], []
    if set(before) != set(after):
        mismatches.append("fingerprint_fields")
    for key in set(before) | set(after):
        if key not in {"sha256", "material_retention", "image_retention"} and before.get(key) != after.get(key):
            mismatches.append(key)
    left_hashes, right_hashes = before["sha256"], after["sha256"]
    if set(left_hashes) != set(right_hashes):
        mismatches.append("sha256.fields")
    for key in set(left_hashes) | set(right_hashes):
        if key != "materials" and left_hashes.get(key) != right_hashes.get(key):
            mismatches.append(f"sha256.{key}")
    left, right = before["material_retention"], after["material_retention"]
    if left["retained_sha256"] != right["retained_sha256"]:
        mismatches.append("material_retention.retained_sha256")
    old, new = left["inventory"], right["inventory"]
    for name in sorted(set(old) | set(new)):
        path = f"material_retention.inventory[{name!r}]"
        if name not in old:
            mismatches.append(path + ".added")
        elif name in new:
            if old[name] != new[name]:
                mismatches.append(path + ".changed")
        elif old[name]["discardable_orphan"] is True and _promotion_discardable_material(old[name]):
            removed.append({"name": name, "reason": "native_save_dropped_zero_user_unretained_local_unprotected_material_without_id_or_slot_consumers", "before": old[name]})
        else:
            mismatches.append(path + ".required_material_missing")
    if not removed and left_hashes["materials"] != right_hashes["materials"]:
        mismatches.append("sha256.materials")
    released_images = []
    if "image_retention" in before and "image_retention" in after:
        left, right = before["image_retention"], after["image_retention"]
        if left["content_sha256"] != right["content_sha256"]:
            mismatches.append("image_retention.content_sha256")
        old, new = left["inventory"], right["inventory"]
        for name in sorted(set(old) | set(new)):
            path = f"image_retention.inventory[{name!r}]"
            if name not in old:
                mismatches.append(path + ".added")
            elif name not in new:
                mismatches.append(path + ".required_image_missing")
            elif old[name] != new[name]:
                # The datablock and pixels survive exactly; only native release of
                # every node in already accepted removed materials may differ.
                expected = dict(old[name], users=0, material_nodes=[], material_consumers=[],
                                id_consumers=[], exclusive_orphan_consumers=False)
                if (old[name]["exclusive_orphan_consumers"] is True
                        and old[name]["consumer_map_complete"] is True
                        and _promotion_orphan_image_consumers(old[name], [row["name"] for row in removed])
                        and new[name] == expected):
                    released_images.append({"name": name,
                        "reason": "image_content_and_packed_bytes_retained_exactly_only_accepted_removed_orphan_material_consumers_released",
                        "before": old[name], "after": new[name]})
                else:
                    mismatches.append(path + ".changed")
    return {"accepted": not mismatches, "mismatches": sorted(mismatches), "removed_orphan_materials": removed,
            "retained_images_with_released_orphan_consumers": released_images,
            "policy": "exact_all_image_content_and_ids_only_proven_removed_orphan_material_consumer_release"}


def _promotion_image_record(job, image):
    """Hash local images; only truly empty paths may use persisted finite pixels."""
    import struct
    # Resolve lazy file metadata before snapshotting load state. Reading size can load a DDS.
    image_size = list(image.size)
    packed = [hashlib.sha256(item.packed_file.data).hexdigest().upper() for item in image.packed_files]
    path = Path(bpy.path.abspath(image.filepath)).resolve() if image.filepath else None
    file_hash = None
    pixel_hash = None
    if not packed and path is not None:
        try:
            path.relative_to(job)
        except ValueError as exc:
            raise ValueError("Promotion texture image must be packed or inside the same job.") from exc
        if not path.is_file():
            raise ValueError("Promotion texture image is missing.")
        file_hash = file_sha256(path)
    elif not packed and not image.has_data:
        # An existing missing image is evidence of absent data, never fabricated pixels.
        # Preserve the sentinel and actual metadata across save/reopen; final material QA remains required.
        if len(image.pixels) != 0:
            raise ValueError(f"Inconsistent empty-path image state: name={image.name!r}, source={image.source!r}, size={list(image.size)!r}, has_data={image.has_data!r}")
    elif not packed:
        # Full datablock inventory includes native viewer buffers; retain their
        # exact finite pixel bytes under the same budget as empty-path images.
        if image.source not in {"FILE", "GENERATED", "VIEWER"}:
            raise ValueError(f"Unsupported loaded empty-path image: name={image.name!r}, source={image.source!r}, size={list(image.size)!r}, has_data={image.has_data!r}")
        width,height = list(image.size)
        channels = int(image.channels)
        count = len(image.pixels)
        if not (0 < width <= 4096 and 0 < height <= 4096 and 1 <= channels <= 4 and count == width*height*channels and count <= 4194304):
            raise ValueError("Empty-path image exceeds the finite four-million-channel pixel budget.")
        hasher = hashlib.sha256()
        for offset in range(0,count,4096):
            values = list(image.pixels[offset:min(offset+4096,count)])
            if any(not math.isfinite(value) for value in values):
                raise ValueError("Empty-path image contains nonfinite pixels.")
            hasher.update(struct.pack('<'+str(len(values))+'f',*values))
        pixel_hash = hasher.hexdigest().upper()
    return {"name":image.name,"has_data":bool(image.has_data) if path is None and not packed else None,"missing_data_sentinel":bool(not packed and path is None and not image.has_data),"material_validity":"missing_pixels_requires_material_review" if not packed and path is None and not image.has_data else "not_assessed","filepath":image.filepath,"size":image_size,"source":image.source,"alpha_mode":image.alpha_mode,"colorspace":image.colorspace_settings.name,"packed_hashes":packed,"file_sha256":file_hash,"pixel_sha256":pixel_hash,"pixel_encoding":"little_endian_float32" if pixel_hash else None,"settings":{key:_promotion_value(getattr(image,key)) for key in ("channels","is_float","generated_type","generated_width","generated_height","generated_color","use_generated_float","use_view_as_render") if hasattr(image,key)},"properties":_promotion_properties(image)}


def _promotion_fingerprint(job: Path, target_names: Iterable[str], *, exclude_action_name: str = "", include_sections: bool = False, cache_image_records: bool = True, image_cache_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Exact pre/post fingerprints; no evaluated mesh, conversion, or data mutation."""
    target_names = set(target_names)
    objects, geometry, rigs, materials, images, actions = {}, {}, {}, {}, {}, {}
    # Local to this synchronous snapshot only; never shared across mutations or loads.
    import time
    image_cache, image_stats = {}, {"hits": 0, "misses": 0, "image_record_seconds": 0.0}
    def image_content(image):
        if cache_image_records and image in image_cache:
            image_stats["hits"] += 1
            return image_cache[image]
        started = time.perf_counter()
        record = _promotion_image_record(job, image)
        image_stats["image_record_seconds"] += time.perf_counter() - started
        image_stats["misses"] += 1
        if cache_image_records:
            image_cache[image] = record
        return record
    for obj in bpy.data.objects:
        if obj.library or obj.override_library or obj.constraints:
            raise ValueError("Promotion proof must contain local unconstrained objects only.")
        objects[obj.name] = {
            "type": obj.type, "data": _promotion_value(obj.data), "parent": _promotion_value(obj.parent),
            "parent_type": obj.parent_type, "parent_bone": obj.parent_bone,
            "world": _locator_matrix_record(obj.matrix_world), "basis": _locator_matrix_record(obj.matrix_basis),
            "parent_inverse": _locator_matrix_record(obj.matrix_parent_inverse), "dimensions": list(obj.dimensions),
            "bounds": [list(corner) for corner in obj.bound_box], "settings": _promotion_scalars(obj),
            "properties": _promotion_properties(obj, PROMOTION_METADATA_KEYS if obj.name in target_names else ()),
            "animation": _promotion_animation_state(obj),
            "modifiers": [_promotion_scalars(modifier) for modifier in obj.modifiers],
        }
        if obj.type == "MESH":
            mesh = obj.data
            attributes = {attribute.name: _promotion_attribute_record(attribute) for attribute in mesh.attributes}
            geometry[obj.name] = {
                "vertices": len(mesh.vertices), "polygons": len(mesh.polygons), "loops": len(mesh.loops),
                "positions_normals": _promotion_digest([[list(vertex.co), list(vertex.normal)] for vertex in mesh.vertices]),
                "edges": _promotion_digest([[list(edge.vertices), edge.use_seam, edge.use_edge_sharp] for edge in mesh.edges]),
                "topology": _promotion_digest([[list(face.vertices), face.material_index, face.use_smooth, list(face.normal)] for face in mesh.polygons]),
                "loops_normals": _promotion_digest([[loop.vertex_index, loop.edge_index] for loop in mesh.loops] + [list(normal.vector) for normal in mesh.corner_normals]),
                "uvs": _promotion_digest({layer.name: [list(item.uv) for item in layer.data] for layer in mesh.uv_layers}),
                "uv_settings": [(layer.name, layer.active_render, layer.active_clone) for layer in mesh.uv_layers],
                "uv_active_index": mesh.uv_layers.active_index, "has_custom_normals": mesh.has_custom_normals,
                "groups": [group.name for group in obj.vertex_groups],
                "weights": _promotion_digest([[(group.group, group.weight) for group in vertex.groups] for vertex in mesh.vertices]),
                "materials": [mat.name if mat else None for mat in mesh.materials], "attributes": attributes,
                "properties": _promotion_properties(mesh), "settings": _promotion_scalars(mesh),
            }
        elif obj.type == "ARMATURE":
            if any(bone.constraints for bone in obj.pose.bones):
                raise ValueError("Promotion does not support constrained pose bones.")
            rigs[obj.name] = {
                "properties": _promotion_properties(obj.data), "settings": _promotion_scalars(obj.data),
                "bones": [{"name": bone.name, "parent": bone.parent.name if bone.parent else None, "head": list(bone.head_local), "tail": list(bone.tail_local), "rest": _locator_matrix_record(bone.matrix_local), "properties": _promotion_properties(bone), "settings": _promotion_scalars(bone)} for bone in obj.data.bones],
                "pose": [{"name": bone.name, "matrix": _locator_matrix_record(bone.matrix), "basis": _locator_matrix_record(bone.matrix_basis), "properties": _promotion_properties(bone), "settings": _promotion_scalars(bone)} for bone in obj.pose.bones],
            }
    for material in bpy.data.materials:
        if material.library or material.override_library or not material.use_nodes:
            raise ValueError("Promotion requires local node-based materials.")
        tree = material.node_tree
        if tree.library or any(node.type == "GROUP" for node in tree.nodes):
            raise ValueError("Promotion does not support linked or grouped material node trees.")
        nodes = []
        for node in tree.nodes:
            nodes.append({"name": node.name, "type": node.bl_idname, "settings": _promotion_scalars(node), "properties": _promotion_properties(node), "inputs": [(socket.identifier, _promotion_value(socket.default_value) if hasattr(socket, "default_value") else None) for socket in node.inputs], "outputs": [(socket.identifier, _promotion_value(socket.default_value) if hasattr(socket, "default_value") else None) for socket in node.outputs]})
            image = getattr(node, "image", None)
            if image is not None:
                if image.library or image.override_library:
                    raise ValueError("Promotion cannot adopt linked texture images.")
                image_record = image_content(image)
                if not {"filepath", "packed_hashes", "file_sha256", "pixel_sha256"} <= set(image_record):
                    raise RuntimeError("Incomplete image fingerprint record.")
                images[image.name] = image_record
        materials[material.name] = {"properties": _promotion_properties(material), "settings": _promotion_scalars(material), "animation": _promotion_animation_state(material), "tree_properties": _promotion_properties(tree), "tree_animation": _promotion_animation_state(tree), "nodes": nodes, "links": [(link.from_node.name, link.from_socket.identifier, link.to_node.name, link.to_socket.identifier) for link in tree.links]}
    for image in bpy.data.images:
        if image.name not in images:
            images[image.name] = image_content(image)
    for action in bpy.data.actions:
        if exclude_action_name and action.name == exclude_action_name:
            continue
        if action.library or action.override_library or (action.users == 0 and not action.use_fake_user):
            raise ValueError("Promotion cannot preserve linked/overridden/unretained actions.")
        curves = []
        for curve, _ in action_fcurves(action):
            if curve.modifiers:
                raise ValueError("Promotion does not support modified action curves.")
            curves.append({"path": curve.data_path, "index": curve.array_index, "settings": _promotion_scalars(curve), "keys": [{"co": list(key.co), "left": list(key.handle_left), "right": list(key.handle_right), "settings": _promotion_scalars(key)} for key in curve.keyframe_points], "samples": [list(point.co) for point in curve.sampled_points]})
        actions[action.name] = {"range": list(action.frame_range), "fake_user": action.use_fake_user, "settings": _promotion_scalars(action), "properties": _promotion_properties(action), "curves": curves, "slots": [_promotion_scalars(slot) for slot in getattr(action, "slots", [])], "layers": [{"settings": _promotion_scalars(layer), "strips": [{"type": strip.type, "bags": [bag.slot_handle for bag in getattr(strip, "channelbags", [])]} for strip in layer.strips]} for layer in getattr(action, "layers", [])]}
    scene = bpy.context.scene
    sections = {"objects": objects, "geometry": geometry, "rigs": rigs, "materials": materials, "images": images, "actions": actions,
                "scene": {"fps": scene.render.fps, "fps_base": scene.render.fps_base, "frame": scene.frame_current, "subframe": scene.frame_subframe, "start": scene.frame_start, "end": scene.frame_end, "properties": _promotion_properties(scene), "collections": {collection.name: {"objects": sorted(obj.name for obj in collection.objects), "children": sorted(child.name for child in collection.children), "properties": _promotion_properties(collection)} for collection in bpy.data.collections}}}
    material_retention = _promotion_material_retention(materials)
    result = {"sha256": {key: _promotion_digest(value) for key, value in sections.items()}, "material_retention": material_retention, "image_retention": _promotion_image_retention(images, material_retention), "mesh_counts": {name: {key: row[key] for key in ("vertices", "polygons", "loops")} for name, row in geometry.items()}, "actions": sorted(actions), "objects": sorted(objects)}
    if include_sections:
        result["sections"] = sections
    if image_cache_stats is not None:
        image_cache_stats.update(image_stats, unique_images=len(images), cache_enabled=cache_image_records)
    return result


def promote_accepted_reimport(req: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a metadata-only working copy from four explicitly hashed immutable proof inputs."""
    context = _promotion_inputs(req)
    job, output = context["job"], context["output"]
    inputs = context["inputs"]
    result = {"operation": "promote_accepted_reimport", "status": "fail", "new_provider_call": False,
              "checkpoint": output.relative_to(job).as_posix(), "report": context["report_path"].relative_to(job).as_posix(),
              "inputs": {role: {key: value for key, value in row.items() if key != "path"} for role, row in inputs.items()},
              "receipt_policy": "complete_legacy_reimport_export_receipt_bound_to_explicit_caller_hashes",
              "comparison_policy": "exact_fingerprints_with_proven_unretained_orphan_material_disappearance_only_no_tolerance_no_export_vertex_count_assumption"}
    try:
        bpy.ops.wm.open_mainfile(filepath=str(inputs["source"]["path"]), use_scripts=False)
        targets = _promotion_targets(context)
        names = [obj.name for obj in targets]
        before = _promotion_fingerprint(job, names)
        result["fingerprints_before"] = before
        metadata = {"hoi4_working": True, "hoi4_promotion_operation": "promote_accepted_reimport",
                    "hoi4_promotion_source": inputs["source"]["relative"], "hoi4_promotion_source_sha256": inputs["source"]["sha256"],
                    "hoi4_promotion_validation": inputs["validation"]["relative"], "hoi4_promotion_validation_sha256": inputs["validation"]["sha256"], "hoi4_promotion_job": req["job_id"]}
        result["permitted_metadata"] = {"targets": names, "before": {obj.name: {key: _promotion_value(obj[key]) for key in PROMOTION_METADATA_KEYS if key in obj} for obj in targets}, "after": metadata}
        for obj in targets:
            for key, value in metadata.items():
                obj[key] = value
        if _promotion_fingerprint(job, names) != before:
            raise RuntimeError("Promotion changed protected scene data before saving.")
        if output.exists():
            raise ValueError("Promotion checkpoint appeared during processing; refusing overwrite.")
        saved = bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, relative_remap=False)
        if "FINISHED" not in saved or not output.is_file():
            raise RuntimeError("Promotion checkpoint save did not finish.")
        bpy.ops.wm.open_mainfile(filepath=str(output), use_scripts=False)
        after = _promotion_fingerprint(job, names)
        result["fingerprints_after"] = after
        result["reopen_comparison"] = _promotion_reopen_comparison(before, after)
        if not result["reopen_comparison"]["accepted"]:
            raise RuntimeError("Promotion saved/reopened invariant mismatch; output is not approved.")
        for name in names:
            obj = bpy.context.scene.objects.get(name)
            if obj is None or any(obj.get(key) != value for key, value in metadata.items()):
                raise RuntimeError("Promotion metadata did not survive reopening.")
        for role, row in inputs.items():
            if row["path"].stat().st_size != row["bytes"] or file_sha256(row["path"]) != row["sha256"]:
                raise RuntimeError(f"Immutable promotion {role} input changed during processing.")
        result.update(status="pass", source_immutable=True, all_inputs_immutable=True, checkpoint_sha256=file_sha256(output), checkpoint_bytes=output.stat().st_size)
    except Exception as exc:
        result["error"] = str(exc)
        result["output_approved"] = False
        result["input_immutability"] = {role: row["path"].is_file() and row["path"].stat().st_size == row["bytes"] and file_sha256(row["path"]) == row["sha256"] for role, row in inputs.items()}
        if output.is_file():
            result.update(checkpoint_sha256=file_sha256(output), checkpoint_bytes=output.stat().st_size)
        context["report_path"].parent.mkdir(parents=True, exist_ok=True)
        with context["report_path"].open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
        raise RuntimeError(f"Promotion failed; do not use output. Evidence: {result['report']}: {exc}") from exc
    context["report_path"].parent.mkdir(parents=True, exist_ok=True)
    with context["report_path"].open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    return result


def _locator_exact_name(value: Any, field: str, *, locator: bool = False) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError(f"{field} must be a non-empty exact name without surrounding whitespace.")
    if locator and re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value) is None:
        raise ValueError("locator_name must be stable lowercase snake_case (1-63 ASCII characters).")
    return value


def _locator_numbers(value: Any, size: int, field: str) -> List[float]:
    if not isinstance(value, (list, tuple)) or len(value) != size:
        raise ValueError(f"{field} requires exactly {size} finite numbers.")
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item) for item in value):
        raise ValueError(f"{field} requires exactly {size} finite numbers.")
    return [float(item) for item in value]


def _locator_request(req: Dict[str, Any]) -> Tuple[Path, Path, Path, str, str, str, List[float], List[float]]:
    payload = req["payload"]
    expected = {"blend_rel", "checkpoint_rel", "target_armature_name", "parent_bone", "locator_name", "bone_local_position", "bone_local_rotation_xyzw"}
    if set(payload) != expected:
        raise ValueError("author_locator accepts only its exact named, measured locator contract.")
    job = Path(req["job_root"]).resolve()
    _locator_exact_name(req.get("job_id"), "job_id", locator=True)
    for field in ("blend_rel", "checkpoint_rel"):
        value = payload[field]
        if not isinstance(value, str) or ".." in Path(value).parts:
            raise ValueError(f"{field} must be a job-relative checkpoint path without traversal.")
    source = within(job, payload["blend_rel"])
    output = within(job, payload["checkpoint_rel"], allow_missing=True)
    if not source.is_file() or source.suffix.lower() != ".blend" or output.suffix.lower() != ".blend":
        raise ValueError("author_locator requires .blend checkpoint files.")
    if source == output or output.exists():
        raise ValueError("author_locator requires a new checkpoint and never overwrites an existing path.")
    if source.parent != output.parent:
        raise ValueError("Locator checkpoints must be siblings to preserve all relative material paths.")
    armature_name = _locator_exact_name(payload["target_armature_name"], "target_armature_name")
    bone_name = _locator_exact_name(payload["parent_bone"], "parent_bone")
    name = _locator_exact_name(payload["locator_name"], "locator_name", locator=True)
    position = _locator_numbers(payload["bone_local_position"], 3, "bone_local_position")
    rotation = _locator_numbers(payload["bone_local_rotation_xyzw"], 4, "bone_local_rotation_xyzw")
    if abs(math.hypot(*rotation) - 1.0) > 1e-6:
        raise ValueError("bone_local_rotation_xyzw must be a unit quaternion; implicit normalization is forbidden.")
    return job, source, output, armature_name, bone_name, name, position, rotation


def _locator_registration(job: Path, job_id: str, name: str, rig_name: str, bone_name: str) -> Dict[str, Any]:
    return {
        "hoi4_export_locator": True,
        "hoi4_locator_registry_version": LOCATOR_REGISTRY_VERSION,
        "hoi4_locator_owner_job": job_id,
        "hoi4_locator_owner_root": hashlib.sha256(os.path.normcase(str(job.resolve())).encode("utf-8")).hexdigest(),
        "hoi4_locator_name": name,
        "hoi4_locator_armature": rig_name,
        "hoi4_locator_parent_bone": bone_name,
    }


def _locator_matrix_record(matrix: Matrix) -> List[List[float]]:
    values = [[float(value) for value in row] for row in matrix]
    if len(values) != 4 or any(len(row) != 4 for row in values) or any(not math.isfinite(value) for row in values for value in row):
        raise ValueError("Locator transforms must be finite 4x4 matrices.")
    return values


def _locator_bone_world(rig: bpy.types.Object, bone_name: str, *, rest: bool = False) -> Matrix:
    bone_matrix = rig.data.bones[bone_name].matrix_local if rest or rig.data.pose_position == "REST" else rig.pose.bones[bone_name].matrix
    matrix = rig.matrix_world @ bone_matrix
    _locator_matrix_record(matrix)
    if abs(matrix.determinant()) < 1e-12:
        raise ValueError("Locator parent has a singular transform.")
    return matrix


def _locator_parent(rig_name: str, bone_name: str) -> bpy.types.Object:
    matches = [obj for obj in bpy.data.objects if obj.name == rig_name]
    rig = matches[0] if len(matches) == 1 else None
    if rig is None or rig.type != "ARMATURE" or bpy.context.scene.objects.get(rig_name) != rig:
        raise ValueError(f"Locator requires one exact scene armature: {rig_name}")
    if rig.library or rig.override_library or rig.data.library or rig.get("hoi4_source_protected") or rig.get("hoi4_reference_read_only"):
        raise ValueError("Locator parent cannot be linked, overridden, or a protected source/reference rig.")
    if bone_name not in rig.data.bones or bone_name not in rig.pose.bones:
        raise ValueError(f"Locator parent bone does not exist: {rig_name}/{bone_name}")
    rig_scale = _locator_numbers(list(rig.matrix_world.to_scale()), 3, "locator armature world scale")
    if min(rig_scale) <= 0.0 or max(rig_scale) - min(rig_scale) > 1e-5 or rig.matrix_world.determinant() <= 0.0:
        raise ValueError("Locator authoring/export requires a positive uniform armature world scale without reflection.")
    _locator_bone_world(rig, bone_name)
    return rig


def _validate_registered_locator(obj: bpy.types.Object, rig: bpy.types.Object, bone_name: str, registration: Dict[str, Any]) -> None:
    if obj.type != "EMPTY" or obj.data is not None or obj.library or obj.override_library:
        raise ValueError("Locator name collision: only a local registered Empty may be updated/exported.")
    if bpy.context.scene.objects.get(obj.name) != obj or any(obj.get(key) != value for key, value in registration.items()):
        raise ValueError("Locator name collision or ownership/registration mismatch.")
    if obj.parent != rig or obj.parent_type != "BONE" or obj.parent_bone != bone_name:
        raise ValueError("Registered locator has a different parent; automatic reparenting is forbidden.")
    if obj.constraints or obj.modifiers or obj.animation_data or obj.children or obj.instance_type != "NONE":
        raise ValueError("Registered locator must be a non-animated, non-instancing leaf Empty without constraints or modifiers.")
    if obj.get("hoi4_source_protected") or obj.get("hoi4_reference_read_only"):
        raise ValueError("Protected source/reference locators cannot be updated/exported.")
    users = bpy.data.user_map(subset=[obj]).get(obj, set())
    if any(not isinstance(user, (bpy.types.Scene, bpy.types.Collection)) for user in users):
        raise ValueError("Locator is referenced by another data-block; non-deforming leaf ownership is required.")
    _locator_matrix_record(obj.matrix_world)
    _locator_matrix_record(obj.matrix_basis)
    _locator_matrix_record(obj.matrix_parent_inverse)


def locator_records(objects: Optional[Iterable[bpy.types.Object]] = None) -> List[Dict[str, Any]]:
    """Report true bone-head-local transforms, not Object.matrix_local (armature-relative)."""
    records = []
    for obj in bpy.context.scene.objects if objects is None else objects:
        if obj.type != "EMPTY" or obj.data is not None:
            continue
        record = {
            "name": obj.name,
            "parent": obj.parent.name if obj.parent else None,
            "parent_type": obj.parent_type if obj.parent else None,
            "parent_bone": obj.parent_bone if obj.parent_type == "BONE" else None,
            "matrix_world": _locator_matrix_record(obj.matrix_world),
            "matrix_basis": _locator_matrix_record(obj.matrix_basis),
            "matrix_parent_inverse": _locator_matrix_record(obj.matrix_parent_inverse),
            "registered_for_export": bool(obj.get("hoi4_export_locator", False)),
            "owner_job": obj.get("hoi4_locator_owner_job"),
            "frame": int(bpy.context.scene.frame_current),
        }
        if obj.parent and obj.parent.type == "ARMATURE" and obj.parent_type == "BONE" and obj.parent_bone in obj.parent.data.bones:
            record["bone_local_matrix"] = _locator_matrix_record(_locator_bone_world(obj.parent, obj.parent_bone).inverted() @ obj.matrix_world)
            record["rest_bone_relative_matrix"] = _locator_matrix_record(_locator_bone_world(obj.parent, obj.parent_bone, rest=True).inverted() @ obj.matrix_world)
        records.append(record)
    return sorted(records, key=lambda item: item["name"])


def author_locator(req: Dict[str, Any]) -> Dict[str, Any]:
    """Modify exactly one registered Empty in a new checkpoint; no mesh, bone or action editing."""
    job, source, output, rig_name, bone_name, name, position, rotation = _locator_request(req)
    source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest().upper()
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    rig = _locator_parent(rig_name, bone_name)
    if any(name in candidate.data.bones for candidate in armatures(working_only=False)):
        raise ValueError("Locator name collides with a skeleton bone.")
    registration = _locator_registration(job, req["job_id"], name, rig_name, bone_name)
    matches = [obj for obj in bpy.data.objects if obj.name == name]
    if len(matches) > 1:
        raise ValueError("Duplicate locator names are ambiguous; no object may be adopted or renamed.")
    locator = matches[0] if matches else None
    if locator is not None:
        _validate_registered_locator(locator, rig, bone_name, registration)
    # Do not change fake-user flags through save_blend. Unretained actions would
    # be lost on reopening, so fail before touching the locator instead.
    unretained = [action.name for action in bpy.data.actions if action.users == 0 and not action.use_fake_user]
    if unretained:
        raise ValueError(f"Checkpoint contains unretained actions; locator-only save cannot preserve them: {unretained}")
    actions_before = {action.name: _export_checkpoint_action_snapshot(action) for action in bpy.data.actions}
    created = locator is None
    if created:
        locator = bpy.data.objects.new(name, None)
        if locator.name != name:
            raise RuntimeError("Blender changed the requested locator name; refusing an ambiguous locator.")
        bpy.context.scene.collection.objects.link(locator)
        locator.empty_display_type = "PLAIN_AXES"
        locator.parent = rig
        locator.parent_type = "BONE"
        locator.parent_bone = bone_name
        for key, value in registration.items():
            locator[key] = value
    # Setting world space after exact bone parenting lets Blender account for
    # its bone-tail parent offset without pretending matrix_local is bone-local.
    local = Matrix.Translation(position) @ Quaternion((rotation[3], *rotation[:3])).to_matrix().to_4x4()
    locator.matrix_parent_inverse = Matrix.Identity(4)
    locator.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    locator.matrix_world = _locator_bone_world(rig, bone_name) @ local
    bpy.context.view_layer.update()
    actual = _locator_bone_world(rig, bone_name).inverted() @ locator.matrix_world
    delta = max(abs(actual[row][col] - local[row][col]) for row in range(4) for col in range(4))
    if not math.isfinite(delta) or delta > LOCATOR_TRANSFORM_TOLERANCE:
        raise RuntimeError(f"Locator bone-local transform did not round-trip through Blender parenting: {delta}")
    _validate_registered_locator(locator, rig, bone_name, registration)
    if actions_before != {action.name: _export_checkpoint_action_snapshot(action) for action in bpy.data.actions}:
        raise RuntimeError("Locator authoring altered existing action data.")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError("Locator checkpoint output appeared during processing; refusing overwrite.")
    saved = bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, relative_remap=False)
    if "FINISHED" not in saved or not output.is_file():
        raise RuntimeError("Blender did not save the requested locator checkpoint.")
    if hashlib.sha256(source.read_bytes()).hexdigest().upper() != source_sha256:
        raise RuntimeError("The input checkpoint changed during locator authoring.")
    return {
        "source": source.relative_to(job).as_posix(),
        "source_sha256": source_sha256,
        "checkpoint": output.relative_to(job).as_posix(),
        "checkpoint_sha256": hashlib.sha256(output.read_bytes()).hexdigest().upper(),
        "checkpoint_bytes": output.stat().st_size,
        "operation": "author_locator",
        "created": created,
        "locator": locator_records([locator])[0],
        "requested_bone_local_position": position,
        "requested_bone_local_rotation_xyzw": rotation,
        "bone_local_matrix_max_error": delta,
        "actions_verified_unchanged": sorted(actions_before),
        "policy": "one_registered_leaf_empty_only_no_mesh_material_weight_bone_action_or_scale_edits",
    }


def approved_export_locators(job: Path, job_id: str, working: List[bpy.types.Object]) -> List[bpy.types.Object]:
    """Select only registered locators on approved rigs exported by a mesh modifier."""
    exported_rigs = set()
    for mesh in working:
        modifiers = [modifier for modifier in mesh.modifiers if modifier.type == "ARMATURE"]
        if modifiers and modifiers[0].object is not None:
            exported_rigs.add(modifiers[0].object)  # matches io_pdx_mesh get_rig_from_mesh
    locators = []
    for obj in bpy.context.scene.objects:
        if not obj.get("hoi4_export_locator", False):
            continue
        name = _locator_exact_name(obj.name, "locator_name", locator=True)
        rig_name = _locator_exact_name(obj.get("hoi4_locator_armature"), "registered armature")
        bone_name = _locator_exact_name(obj.get("hoi4_locator_parent_bone"), "registered parent bone")
        rig = _locator_parent(rig_name, bone_name)
        registration = _locator_registration(job, job_id, name, rig_name, bone_name)
        _validate_registered_locator(obj, rig, bone_name, registration)
        if rig not in exported_rigs:
            continue
        if not rig.get("hoi4_working", False):
            raise ValueError("Registered locator parent is not an approved working export rig.")
        # The extension exports only the first root and skips pdxIgnoreJoint branches.
        bone = rig.data.bones[bone_name]
        while bone.parent is not None:
            if bone.get("pdxIgnoreJoint", False):
                raise ValueError("Locator parent is excluded from the exported skeleton.")
            bone = bone.parent
        # RNA access can produce distinct Python wrappers for the same bone.
        if bone != rig.data.bones[0]:
            raise ValueError("Locator parent is outside the exporter's first-root skeleton.")
        if any(name in candidate.data.bones for candidate in exported_rigs):
            raise ValueError("Locator name collides with an exported skeleton bone.")
        if sum(bone_name in candidate.data.bones for candidate in exported_rigs) != 1:
            raise ValueError("Locator parent bone is ambiguous across exported rigs.")
        locators.append(obj)
    return sorted(locators, key=lambda obj: obj.name)


def export_mesh(req: Dict[str, Any], pdx: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    output = within(job, payload["output_rel"], allow_missing=True)
    explicit_checkpoint = payload.get("checkpoint_rel")
    exported_checkpoint = within(job, explicit_checkpoint, allow_missing=True) if explicit_checkpoint else job / "blender" / "checkpoints" / "06_exported.blend"
    if explicit_checkpoint and (exported_checkpoint.suffix != ".blend" or exported_checkpoint.parent != blend.parent or exported_checkpoint == blend or exported_checkpoint.exists()):
        raise ValueError("Explicit export checkpoint must be a new sibling .blend; overwrite is forbidden.")
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend), use_scripts=False)
    pdx = load_pdx(req["io_pdx_root"])
    working = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.get("hoi4_working", False)
    ]
    if not working:
        raise RuntimeError("Mesh export found no approved hoi4_working mesh objects.")
    pdx_meshes = set(pdx["list_scene_pdx_meshes"]())
    locators = approved_export_locators(job, req["job_id"], [obj for obj in working if obj in pdx_meshes])
    locator_local = {obj.name: _locator_bone_world(obj.parent, obj.parent_bone).inverted() @ obj.matrix_world for obj in locators}
    export_transforms = prepare_pdx_export_transforms()
    locator_scale = float(export_transforms.get("armature_data_scale_factor", 1.0))
    if abs(locator_scale - 1.0) > 1e-6:
        for obj in locators:
            local = locator_local[obj.name]
            local.translation *= locator_scale
            obj.matrix_world = _locator_bone_world(obj.parent, obj.parent_bone) @ local
        bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    for obj in working + locators:
        obj.select_set(True)
    if {obj.name for obj in bpy.context.selected_objects} != {obj.name for obj in working + locators}:
        raise RuntimeError("Mesh export selection differs from approved meshes and registered locators.")
    bpy.context.view_layer.objects.active = working[0]
    for old_output in (output, output.with_suffix(".txt")):
        if old_output.exists():
            if not old_output.is_file():
                raise RuntimeError(f"Mesh export target is not a file: {old_output}")
            old_output.unlink()
    # Locator serialization uses rest-bone matrices in io_pdx_mesh 0.91.0.
    # Evaluate only the approved locator rigs in REST, then restore their pose
    # display state even if the exporter fails; no action keys are changed.
    locator_pose_positions = {obj.parent: obj.parent.data.pose_position for obj in locators}
    try:
        for rig in locator_pose_positions:
            rig.data.pose_position = "REST"
        bpy.context.view_layer.update()
        exported_locators = locator_records(locators)
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
    finally:
        for rig, pose_position in locator_pose_positions.items():
            rig.data.pose_position = pose_position
        bpy.context.view_layer.update()
    text_output = output.with_suffix(".txt")
    streams = exported_mesh_streams(text_output)
    from skeletal_export_partition import require_bounded_export_streams
    require_bounded_export_streams(streams)
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
        "maximum_stream_triangle_indices": max(stream["triangle_indices"] for stream in streams),
        "vertex_stream_limit": 65535,
        "conservative_triangle_index_entry_budget": 65535,
        "exported_checkpoint": str(exported_checkpoint.relative_to(job)).replace("\\", "/"),
        "geometry": geometry_metrics(),
        "export_transforms": export_transforms,
        "locators": exported_locators,
        "selected_export_objects": sorted(obj.name for obj in working + locators),
        "locator_coordinate_policy": "bone_head_local_rest_export_with_uniform_rig_scale_conversion",
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


def scale_aware_retarget_location_scale(
    source_world_scale: Vector,
    target_world_scale: Vector,
) -> float:
    """Convert source pose-basis translation units to target pose-basis units."""

    for label, scale in (
        ("source", source_world_scale),
        ("target", target_world_scale),
    ):
        if min(scale) <= 0.0 or max(scale) - min(scale) > 1e-5:
            raise ValueError(
                f"Animation transfer requires a positive uniform {label} armature world scale: "
                + json.dumps(list(scale))
            )
    source_uniform_world_scale = float(sum(source_world_scale) / 3.0)
    target_uniform_world_scale = float(sum(target_world_scale) / 3.0)
    return source_uniform_world_scale / target_uniform_world_scale


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
    provenance_path = within(job, payload["provenance_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    source_action_name = explicit_source_action_name(payload.get("source_action_name"), "source_action_name")
    requested_source_armature = (
        explicit_safe_name(payload.get("source_armature_name"), "source_armature_name")
        if payload.get("source_armature_name")
        else ""
    )
    target_armature_name = explicit_safe_name(payload.get("target_armature_name"), "target_armature_name")
    action_name = explicit_action_name(payload.get("target_action_name"), "target_action_name")
    source_kind = str(payload.get("source_kind") or "")
    if source_kind not in {"meshy_animate", "meshy_text_to_motion", "professional_source"}:
        raise ValueError("source_kind must be meshy_animate, meshy_text_to_motion or professional_source.")
    source_reference_id = explicit_reference_id(payload.get("source_reference_id"), "source_reference_id")
    expected_source_sha256 = str(payload.get("source_sha256") or "").upper()
    if not re.fullmatch(r"[0-9A-F]{64}", expected_source_sha256):
        raise ValueError("source_sha256 must be an explicit 64-character SHA-256 digest.")
    actual_source_sha256 = file_sha256(source)
    if actual_source_sha256 != expected_source_sha256:
        raise RuntimeError(
            "Animation source checksum did not match the verified provenance receipt: "
            f"expected {expected_source_sha256}, observed {actual_source_sha256}."
        )
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Animation provenance receipt is not valid JSON: {provenance_path.name}") from exc
    required_provenance = {
        "verification_status": "verified",
        "source_kind": source_kind,
        "source_reference_id": source_reference_id,
        "source_action_name": source_action_name,
        "source_sha256": expected_source_sha256,
    }
    mismatched_provenance = {
        key: {"expected": value, "observed": provenance.get(key)}
        for key, value in required_provenance.items()
        if provenance.get(key) != value
    }
    if mismatched_provenance:
        raise ValueError(
            "Animation provenance receipt does not verify the requested source action: "
            + json.dumps(mismatched_provenance, sort_keys=True)
        )

    if checkpoint == blend or checkpoint.exists():
        raise ValueError("Animation transfer requires a new sibling checkpoint.")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    if bpy.data.actions.get(action_name) is not None:
        raise ValueError("Animation transfer requires a new target action name.")
    audited_target_promotion = {
        "requested": bool(payload.get("promote_audited_target", False)),
        "applied": False,
        "target_armature": None,
        "promoted_meshes": [],
        "policy": "working objects only",
    }
    target_rigs = armatures()
    if not target_rigs and audited_target_promotion["requested"]:
        all_target_rigs = armatures(working_only=False)
        matching_audited_rigs = [rig for rig in all_target_rigs if rig.name == target_armature_name]
        if len(all_target_rigs) != 1 or len(matching_audited_rigs) != 1:
            raise RuntimeError(
                "Audited-target promotion requires exactly one scene armature with the explicit target name; "
                + json.dumps(
                    {
                        "requested_target_armature": target_armature_name,
                        "available_armatures": sorted(rig.name for rig in all_target_rigs),
                    },
                    sort_keys=True,
                )
            )
        promoted_rig = matching_audited_rigs[0]
        promoted_meshes = []
        for obj in mesh_objects(working_only=False):
            consumes_target = obj.parent is promoted_rig or any(
                modifier.type == "ARMATURE" and modifier.object is promoted_rig
                for modifier in obj.modifiers
            )
            if consumes_target:
                obj["hoi4_working"] = True
                promoted_meshes.append(obj.name)
        if not promoted_meshes:
            raise RuntimeError(
                "Audited-target promotion found no mesh parented or armature-modified to the requested rig."
            )
        promoted_rig["hoi4_working"] = True
        audited_target_promotion = {
            "requested": True,
            "applied": True,
            "target_armature": promoted_rig.name,
            "promoted_meshes": sorted(promoted_meshes),
            "policy": "promoted only the uniquely named audited armature and its direct mesh consumers",
        }
        target_rigs = [promoted_rig]
    matching_target_rigs = [rig for rig in target_rigs if rig.name == target_armature_name]
    if len(target_rigs) != 1 or len(matching_target_rigs) != 1:
        raise RuntimeError(
            "Animation transfer requires exactly one calibrated working armature with the explicit target name; "
            + json.dumps(
                {
                    "requested_target_armature": target_armature_name,
                    "available_armatures": sorted(rig.name for rig in target_rigs),
                },
                sort_keys=True,
            )
        )
    target_rig = matching_target_rigs[0]
    before_objects = set(bpy.data.objects)
    before_actions = set(bpy.data.actions)
    retained_action_hashes = {a.name: action_curve_signature(a) for a in before_actions}
    target_source_hash = file_sha256(blend)
    imported = import_candidate(source)
    imported_rigs = [obj for obj in imported if obj.type == "ARMATURE"]
    if requested_source_armature:
        matching_source_rigs = [rig for rig in imported_rigs if rig.name == requested_source_armature]
        if len(matching_source_rigs) != 1:
            raise RuntimeError(
                "Provider animation import did not expose the explicitly named source armature: "
                + json.dumps(
                    {
                        "requested_source_armature": requested_source_armature,
                        "available_source_armatures": sorted(rig.name for rig in imported_rigs),
                    },
                    sort_keys=True,
                )
            )
        source_rig = matching_source_rigs[0]
    elif len(imported_rigs) == 1:
        source_rig = imported_rigs[0]
    else:
        raise RuntimeError(
            "Provider animation import must expose exactly one source armature when source_armature_name is omitted; "
            f"found {len(imported_rigs)} from {source.name}."
        )
    source_armature_name = source_rig.name
    source_actions = [action for action in bpy.data.actions if action not in before_actions]
    source_action = next((action for action in source_actions if action.name == source_action_name), None)
    if source_action is None and source_rig.animation_data:
        active_source_action = source_rig.animation_data.action
        if active_source_action is not None and active_source_action.name == source_action_name:
            source_action = active_source_action
    if source_action is None:
        raise RuntimeError(
            "Verified animation source did not expose the explicitly named source action: "
            + json.dumps(
                {
                    "requested_source_action": source_action_name,
                    "available_source_actions": sorted(action.name for action in source_actions),
                },
                sort_keys=True,
            )
        )
    source_action_name = source_action.name

    source_curves = list(action_fcurves(source_action))
    if not source_curves:
        raise RuntimeError(f"Provider animation action contains no F-curves: {source_action.name}")
    source_bone_names = sorted(
        {
            match.group(1)
            for fcurve, _ in source_curves
            for match in [re.search(r'pose\.bones\["([^"]+)"\]', fcurve.data_path)]
            if match is not None
        }
    )
    target_bone_names = {bone.name for bone in target_rig.data.bones}
    raw_bone_chains = payload.get("bone_chains") or {}
    if not isinstance(raw_bone_chains, dict):
        raise ValueError("bone_chains must map target bone names to ordered source bone-name lists.")
    bone_chains: Dict[str, List[str]] = {}
    for raw_target, raw_sources in raw_bone_chains.items():
        target_name = explicit_safe_name(raw_target, "bone_chains target")
        if not isinstance(raw_sources, list) or not raw_sources:
            raise ValueError(f"bone_chains[{target_name!r}] must be a non-empty list.")
        source_names = [
            explicit_safe_name(source_name, f"bone_chains[{target_name!r}] source")
            for source_name in raw_sources
        ]
        bone_chains[target_name] = source_names
    if not bone_chains:
        missing_bones = sorted(set(source_bone_names) - target_bone_names)
        if missing_bones:
            raise RuntimeError(
                "Provider animation bone channels do not match the calibrated rig: "
                + json.dumps({"missing_bones": missing_bones, "source_action": source_action.name}, sort_keys=True)
            )
        bone_chains = {name: [name] for name in source_bone_names}
    missing_target_bones = sorted(set(bone_chains) - target_bone_names)
    missing_source_bones = sorted(
        {
            source_name
            for source_names in bone_chains.values()
            for source_name in source_names
            if source_name not in source_bone_names or source_rig.data.bones.get(source_name) is None
        }
    )
    if len(bone_chains) < 6:
        raise RuntimeError(
            f"Provider animation action is not a usable skeletal action: only {len(bone_chains)} mapped target bones."
        )
    if missing_target_bones or missing_source_bones:
        raise RuntimeError(
            "Provider animation bone chains do not match the source and calibrated target rigs: "
            + json.dumps(
                {
                    "missing_source_bones": missing_source_bones,
                    "missing_target_bones": missing_target_bones,
                    "source_action": source_action.name,
                },
                sort_keys=True,
            )
        )

    source_rig.animation_data_create()
    source_rig.animation_data.action = source_action
    source_start, source_end = source_action.frame_range
    frame_start = int(math.floor(float(source_start)))
    frame_end = int(math.ceil(float(source_end)))
    if frame_end <= frame_start:
        raise RuntimeError(f"Provider animation action has no usable frame span: {source_action.name}")
    source_lengths = {
        target_name: max(
            sum(float(source_rig.data.bones[name].length) for name in source_names),
            1e-8,
        )
        for target_name, source_names in bone_chains.items()
    }
    length_ratios = sorted(
        float(target_rig.data.bones[target_name].length) / source_lengths[target_name]
        for target_name in bone_chains
    )
    data_length_ratio = length_ratios[len(length_ratios) // 2]
    source_world_scale = source_rig.matrix_world.to_scale()
    target_world_scale = target_rig.matrix_world.to_scale()
    try:
        location_scale = scale_aware_retarget_location_scale(
            source_world_scale,
            target_world_scale,
        )
    except ValueError as exc:
        raise RuntimeError(
            f"{exc} Source armature: {source_rig.name}; target armature: {target_rig.name}."
        ) from exc
    from retarget_root_motion import vertical_root_basis_location, conjugate_rotation, angular_motion_retained
    target_roots = [b for b in target_rig.data.bones if b.parent is None and b.name in bone_chains]
    if len(target_roots) != 1:
        raise ValueError("Retarget requires exactly one explicitly mapped target root.")
    target_root = target_roots[0]
    if target_rig.pose.bones[target_root.name].constraints:
        raise ValueError("Root translation proof requires an unconstrained target root.")
    root_source_name = bone_chains[target_root.name][-1]
    scale_ref = payload.get("root_scale_reference")
    anatomical_scale = 1.0
    scale_evidence = {"policy": "world_units_identity", "ratio": 1.0}
    if source_kind == "meshy_text_to_motion" and not scale_ref:
        raise ValueError("Text-to-Motion requires explicit measured root_scale_reference joint-head pairs.")
    if scale_ref:
        if not isinstance(scale_ref, dict) or set(scale_ref) != {"source_head_bones", "target_head_bones"}:
            raise ValueError("root_scale_reference requires source_head_bones and target_head_bones only.")
        lengths = []
        for key, rig in (("source_head_bones", source_rig), ("target_head_bones", target_rig)):
            pair = scale_ref[key]
            if not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1] or any(name not in rig.data.bones for name in pair):
                raise ValueError("Scale reference must name two distinct existing joints per rig.")
            points = [rig.matrix_world @ rig.data.bones[name].head_local for name in pair]
            distance = (points[1] - points[0]).length
            if not math.isfinite(distance) or distance <= 1e-6:
                raise ValueError("Measured anatomical span is zero or invalid.")
            lengths.append(distance)
        anatomical_scale = lengths[1] / lengths[0]
        scale_evidence = {"policy": "measured_world_joint_head_span", "reference": scale_ref,
                          "source_world_span": lengths[0], "target_world_span": lengths[1], "ratio": anatomical_scale}
    source_object_matrix = source_rig.matrix_world.copy()
    target_object_matrix = target_rig.matrix_world.copy()
    root_world_cache = {}
    target_basis_to_world = (target_rig.matrix_world @ target_root.matrix_local).to_3x3()
    source_object_rotation = source_rig.matrix_world.to_quaternion().normalized()
    target_object_rotation = target_rig.matrix_world.to_quaternion().normalized()
    source_pose_cache: Dict[int, Dict[str, Tuple[Vector, Quaternion]]] = {}
    target_bones_by_depth = sorted(
        bone_chains,
        key=lambda name: len(target_rig.data.bones[name].parent_recursive),
    )
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        for rig, initial in ((source_rig, source_object_matrix), (target_rig, target_object_matrix)):
            error = max(abs(rig.matrix_world[row][col] - initial[row][col]) for row in range(4) for col in range(4))
            if error > 1e-6:
                raise ValueError("Animated armature object basis is unsupported; provide a static-object source/target. " + str({"rig": rig.name, "frame": frame, "matrix_error": error}))
        root_world_cache[frame] = (source_rig.matrix_world @ source_rig.pose.bones[root_source_name].matrix).translation.copy()
        source_deltas: Dict[str, Tuple[Vector, Quaternion]] = {}
        for target_name, source_names in bone_chains.items():
            first_pose_bone = source_rig.pose.bones[source_names[0]]
            last_pose_bone = source_rig.pose.bones[source_names[-1]]
            first_rest_bone = source_rig.data.bones[source_names[0]]
            last_rest_bone = source_rig.data.bones[source_names[-1]]
            pose_parent_matrix = (
                first_pose_bone.parent.matrix.copy()
                if first_pose_bone.parent is not None
                else Matrix.Identity(4)
            )
            rest_parent_matrix = (
                first_rest_bone.parent.matrix_local.copy()
                if first_rest_bone.parent is not None
                else Matrix.Identity(4)
            )
            animated_chain = pose_parent_matrix.inverted_safe() @ last_pose_bone.matrix
            rest_chain = rest_parent_matrix.inverted_safe() @ last_rest_bone.matrix_local
            delta = rest_chain.inverted_safe() @ animated_chain
            location, _, _ = delta.decompose()
            source_world_rotation = (
                last_pose_bone.matrix.to_quaternion().normalized()
                @ last_rest_bone.matrix_local.to_quaternion().normalized().inverted()
            ).normalized()
            # Conjugate the source armature-space delta through both object orientations.
            source_world_rotation = Quaternion(conjugate_rotation(
                source_world_rotation, source_object_rotation, target_object_rotation))
            source_deltas[target_name] = (location.copy(), source_world_rotation)

        frame_pose: Dict[str, Tuple[Vector, Quaternion]] = {}
        desired_target_world_rotations: Dict[str, Quaternion] = {}
        for target_name in target_bones_by_depth:
            target_rest_bone = target_rig.data.bones[target_name]
            target_rest_world_rotation = target_rest_bone.matrix_local.to_quaternion().normalized()
            source_location, source_rotation = source_deltas[target_name]
            desired_world_rotation = (source_rotation @ target_rest_world_rotation).normalized()
            target_parent = target_rest_bone.parent
            if target_parent is None:
                parent_rest_world_rotation = Quaternion()
                parent_desired_world_rotation = Quaternion()
            else:
                parent_rest_world_rotation = target_parent.matrix_local.to_quaternion().normalized()
                parent_desired_world_rotation = desired_target_world_rotations.get(
                    target_parent.name,
                    parent_rest_world_rotation,
                )
            target_rest_local_rotation = (
                parent_rest_world_rotation.inverted() @ target_rest_world_rotation
            ).normalized()
            desired_local_rotation = (
                parent_desired_world_rotation.inverted() @ desired_world_rotation
            ).normalized()
            target_basis_rotation = (
                target_rest_local_rotation.inverted() @ desired_local_rotation
            ).normalized()
            desired_target_world_rotations[target_name] = desired_world_rotation
            frame_pose[target_name] = (source_location, target_basis_rotation)
        source_pose_cache[frame] = frame_pose

    existing = bpy.data.actions.get(action_name)
    if existing is not None:
        for obj in bpy.context.scene.objects:
            if obj.animation_data and obj.animation_data.action == existing:
                obj.animation_data.action = None
        bpy.data.actions.remove(existing)
    transferred = bpy.data.actions.new(action_name)
    transferred.use_fake_user = True
    transferred["hoi4_animation_source_kind"] = source_kind
    transferred["hoi4_animation_source_reference_id"] = source_reference_id
    transferred["hoi4_animation_source_sha256"] = actual_source_sha256
    transferred["hoi4_animation_source_action"] = source_action_name
    transferred["hoi4_animation_provenance_rel"] = str(provenance_path.relative_to(job)).replace("\\", "/")
    transferred["hoi4_animation_processing_policy"] = "verified_source_transfer_only"
    target_rig.animation_data_create()
    target_rig.animation_data.action = transferred
    unmapped_target_bones = sorted(target_bone_names - set(bone_chains))
    for name in unmapped_target_bones:
        pose_bone = target_rig.pose.bones[name]
        if pose_bone.constraints:
            raise ValueError("Unmapped target control has constraints; explicit mapping is required: " + name)
        pose_bone.rotation_mode = "QUATERNION"
        pose_bone.location = (0.0, 0.0, 0.0)
        pose_bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pose_bone.scale = (1.0, 1.0, 1.0)
        for frame in (frame_start, frame_end):
            for channel in ("location", "rotation_quaternion"):
                pose_bone.keyframe_insert(data_path=channel, frame=frame, group=name)
    bpy.context.view_layer.objects.active = target_rig
    target_rig.select_set(True)
    target_root = next((bone for bone in target_rig.data.bones if bone.parent is None), None)
    target_root_name = target_root.name if target_root is not None and target_root.name in bone_chains else ""
    source_root_location = (
        source_pose_cache[frame_start][target_root_name][0]
        if target_root_name
        else Vector()
    )
    source_root_z_delta_peak = (
        max(
            abs(float(source_pose_cache[frame][target_root_name][0].z - source_root_location.z))
            for frame in range(frame_start, frame_end + 1)
        )
        if target_root_name
        else 0.0
    )
    root_world_proof = []
    target_rest_root_world = (target_rig.matrix_world @ target_root.matrix_local).translation.copy()
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        for target_name in bone_chains:
            target_bone = target_rig.pose.bones[target_name]
            source_location, source_rotation = source_pose_cache[frame][target_name]
            target_bone.rotation_mode = "QUATERNION"
            if target_name == target_root_name:
                source_world_delta = (root_world_cache[frame] - root_world_cache[frame_start]) * anatomical_scale
                target_bone.location = Vector(vertical_root_basis_location(
                    source_world_delta, (0.0, 0.0, 0.0), target_basis_to_world))
            else:
                target_bone.location = Vector((0.0, 0.0, 0.0))
            target_bone.rotation_quaternion = source_rotation
            target_bone.scale = (1.0, 1.0, 1.0)
            target_bone.keyframe_insert(data_path="location", frame=frame, group=target_name)
            target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=target_name)
        bpy.context.view_layer.update()
        actual_delta = (target_rig.matrix_world @ target_rig.pose.bones[target_root_name].matrix).translation - target_rest_root_world
        expected_delta = Vector((0.0, 0.0, (root_world_cache[frame].z - root_world_cache[frame_start].z) * anatomical_scale))
        error = (actual_delta - expected_delta).length
        if error > 2e-5:
            raise RuntimeError("Retarget root world displacement differs from scaled vertical source: " + str({"frame": frame, "error": error}))
        root_world_proof.append({"frame": frame, "source_world": list(root_world_cache[frame]),
                                 "expected_target_delta": list(expected_delta), "actual_target_delta": list(actual_delta), "error": error})

    scale_cleanup = {"action": transferred.name, "policy": "only location/quaternion authored; existing action scale channels untouched"}
    root_cleanup = {
        "action": transferred.name,
        "policy": "source hierarchy world-root delta scaled by explicit measured joint-head span; world X/Y removed; world Z converted through inverse target armature/rest-root basis; rotations conjugated through source/target object orientations",
        "anatomical_scale": scale_evidence,
        "world_root_displacement_proof": root_world_proof,
        "maximum_world_root_error": max(row["error"] for row in root_world_proof),
        "location_coordinate_space": "pose_bone_matrix_basis_translation",
        "location_scale_formula": "source_world_delta * measured_world_joint_span_ratio then inverse_target_world_rest_basis",
        "rest_data_length_ratio_applied_to_location": False,
        "data_length_ratio": data_length_ratio,
        "source_armature_world_scale": list(source_world_scale),
        "target_armature_world_scale": list(target_world_scale),
        "location_scale": location_scale,
        "target_root": target_root_name or None,
        "source_root_location": list(source_root_location),
        "source_root_z_delta_peak": source_root_z_delta_peak,
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
    sampled_bones = sorted(bone_chains)
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
            target_base_location = Vector((0.0, 0.0, 0.0))
            target_base_rotation = source_base_rotation
            # Compare like-for-like angular motion. World root translation has its
            # own exact per-frame proof; raw source pose units must not enter this gate.
            source_delta = shortest_quaternion_angle(source_rotation, source_base_rotation)
            target_delta = shortest_quaternion_angle(target_rotation, target_base_rotation)
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
    if not angular_motion_retained(source_motion_peak, target_motion_peak):
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
        if action in source_actions:
            removed_provider_actions.append(action.name)
            action.user_clear()
            bpy.data.actions.remove(action)

    if {a.name: action_curve_signature(a) for a in bpy.data.actions if a.name in retained_action_hashes} != retained_action_hashes:
        raise RuntimeError("Retarget changed a retained action.")
    if file_sha256(blend) != target_source_hash:
        raise RuntimeError("Retarget input checkpoint changed.")
    save_blend(checkpoint)
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "source": str(source.relative_to(job)).replace("\\", "/"),
        "source_sha256": actual_source_sha256,
        "provenance": str(provenance_path.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "target_armature": target_rig.name,
        "audited_target_promotion": audited_target_promotion,
        "source_armature": source_armature_name,
        "source_action": source_action_name,
        "action": transferred.name,
        "frame_start": frame_start,
        "frame_end": frame_end,
        "fps": bpy.context.scene.render.fps,
        "source_fcurves": len(source_curves),
        "source_driven_bones": source_bone_names,
        "target_driven_bones": sorted(bone_chains),
        "bone_chains": bone_chains,
        "imported_objects_removed": imported_object_names,
        "provider_actions_removed": removed_provider_actions,
        "scale_cleanup": scale_cleanup,
        "root_cleanup": root_cleanup,
        "retained_action_hashes": retained_action_hashes,
        "target_source_sha256": target_source_hash,
        "retained_actions_preserved": True,
        "unmapped_target_controls": {"names": unmapped_target_bones, "policy": "identity_local_transform_keys_at_start_and_end_inherit_animated_parent"},
        "location_coordinate_space": "pose_bone_matrix_basis_translation",
        "location_scale_formula": "source_world_delta * measured_world_joint_span_ratio then inverse_target_world_rest_basis",
        "rest_data_length_ratio_applied_to_location": False,
        "data_length_ratio": data_length_ratio,
        "source_armature_world_scale": list(source_world_scale),
        "target_armature_world_scale": list(target_world_scale),
        "location_scale": location_scale,
        "source_target_motion_crosscheck": {
            "metric": "sum_of_mapped_bone_angular_deltas_radians; world_root_translation_verified_separately_per_frame",
            "sample_frames": sample_frames,
            "source_motion_peak": source_motion_peak,
            "target_motion_peak": target_motion_peak,
            "samples": motion_crosscheck,
            "status": "pass",
        },
        "policy": "provider_skeletal_action_retargeted_by_explicit_bone_chains_and_hierarchy_aware_target_rest_bases",
        "action_provenance": action_provenance(transferred),
        "retention_evidence": {
            "source_motion_peak": source_motion_peak,
            "target_motion_peak": target_motion_peak,
            "source_driven_bones": source_bone_names,
            "target_driven_bones": sorted(bone_chains),
            "target_action_fcurves": len(list(action_fcurves(transferred))),
            "manual_or_procedural_replacement_authored": False,
            "provider_source_objects_removed_after_transfer": imported_object_names,
        },
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


def explicit_action_name(value: Any, field: str) -> str:
    """Require an exact stable Blender action identifier, including layered action separators."""

    name = str(value or "")
    if name != name.strip() or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.|: -]{0,191}", name):
        raise ValueError(
            f"{field} must be an explicit action identifier containing only letters, digits, "
            "spaces, underscores, periods, vertical bars, colons, or hyphens."
        )
    return name


def explicit_reference_id(value: Any, field: str) -> str:
    """Require an auditable provider task id or professional-source receipt id."""

    identifier = str(value or "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,191}", identifier):
        raise ValueError(f"{field} must be a stable provider task or approved source receipt identifier.")
    return identifier


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def action_provenance(action: bpy.types.Action) -> Dict[str, str]:
    """Read and validate the immutable verified-source lineage retained on an action."""

    fields = {
        "source_kind": str(action.get("hoi4_animation_source_kind", "")),
        "source_reference_id": str(action.get("hoi4_animation_source_reference_id", "")),
        "source_sha256": str(action.get("hoi4_animation_source_sha256", "")).upper(),
        "source_action_name": str(action.get("hoi4_animation_source_action", "")),
        "provenance_rel": str(action.get("hoi4_animation_provenance_rel", "")),
        "processing_policy": str(action.get("hoi4_animation_processing_policy", "")),
    }
    if fields["source_kind"] == "manual_blender_gpt6_astra":
        spec_hash = str(action.get("hoi4_manual_action_spec_sha256", "")).upper()
        if not re.fullmatch(r"[0-9A-F]{64}", spec_hash) or not re.fullmatch(r"[0-9A-F]{64}", fields["source_sha256"]):
            raise RuntimeError("Manual action requires retained source checkpoint and declarative spec SHA-256.")
        fields.update(source_reference_id=spec_hash, source_action_name=action.name, manual_spec_sha256=spec_hash,
                      processing_policy="manual_blender_gpt6_astra_hash_bound_declarative_action")
        return fields
    if fields["source_kind"] not in {"meshy_animate", "meshy_text_to_motion", "professional_source"}:
        raise RuntimeError(f"Action {action.name} is not marked as a verified provider/professional source action.")
    if not re.fullmatch(r"[0-9A-F]{64}", fields["source_sha256"]):
        raise RuntimeError(f"Action {action.name} has no retained verified source checksum.")
    if not fields["source_reference_id"] or not fields["source_action_name"] or not fields["provenance_rel"]:
        raise RuntimeError(f"Action {action.name} has incomplete retained source provenance.")
    return fields


def explicit_bvh_action_name(value: Any, field: str) -> str:
    """Allow a numeric archival motion id while retaining a bounded Blender name."""

    name = str(value or "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", name):
        raise ValueError(
            f"{field} must be an explicit BVH action identifier containing only letters, "
            "digits, underscores, periods, or hyphens."
        )
    return name


def explicit_source_action_name(value: Any, field: str) -> str:
    """Require an exact source action id while allowing balanced parenthetical qualifiers."""

    name = str(value or "")
    if name != name.strip() or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.|: ()-]{0,191}", name):
        raise ValueError(
            f"{field} must be an explicit source action identifier containing only letters, digits, "
            "spaces, underscores, periods, vertical bars, colons, hyphens, or balanced parentheses."
        )
    parenthesis_depth = 0
    for character in name:
        if character == "(":
            parenthesis_depth += 1
        elif character == ")":
            parenthesis_depth -= 1
            if parenthesis_depth < 0:
                break
    if parenthesis_depth != 0:
        raise ValueError(f"{field} must contain balanced parentheses.")
    return name


def inspect_bvh_header(source: Path) -> Dict[str, Any]:
    """Read only the bounded BVH hierarchy/header needed for an import receipt."""

    if source.suffix.casefold() != ".bvh":
        raise ValueError("Native BVH import requires a .bvh source file.")
    if source.stat().st_size <= 0 or source.stat().st_size > 256 * 1024 * 1024:
        raise ValueError("BVH source must be non-empty and no larger than 256 MiB.")
    joints: List[str] = []
    frames = None
    frame_time = None
    with source.open("r", encoding="utf-8-sig", errors="strict") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if line_number > 20000:
                raise ValueError("BVH hierarchy/header exceeded the bounded 20,000-line scan.")
            line = raw_line.strip()
            match = re.match(r"^(?:ROOT|JOINT)\s+([^\s{}]+)$", line)
            if match:
                joints.append(explicit_safe_name(match.group(1), "BVH joint name"))
            frames_match = re.match(r"^Frames:\s*(\d+)\s*$", line, re.IGNORECASE)
            if frames_match:
                frames = int(frames_match.group(1))
            time_match = re.match(
                r"^Frame\s+Time:\s*((?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[Ee][+-]?\d+)?)\s*$",
                line,
                re.IGNORECASE,
            )
            if time_match:
                frame_time = float(time_match.group(1))
                break
    if len(joints) < 6 or len(set(joints)) != len(joints):
        raise ValueError("BVH source must expose at least six uniquely named skeletal joints.")
    if frames is None or frames < 2 or frame_time is None or not math.isfinite(frame_time) or frame_time <= 0.0:
        raise ValueError("BVH source must declare at least two frames and a positive Frame Time.")
    source_fps = 1.0 / frame_time
    if not math.isfinite(source_fps) or source_fps <= 0.0:
        raise ValueError("BVH source frame rate is not finite and positive.")
    return {
        "joints": joints,
        "joint_count": len(joints),
        "frames": frames,
        "frame_time_seconds": frame_time,
        "source_fps": source_fps,
    }


def action_curve_signature(action: bpy.types.Action) -> str:
    """Hash exact curve/key identity for save-reopen verification."""

    records = []
    for fcurve, _ in sorted(
        action_fcurves(action),
        key=lambda item: (item[0].data_path, item[0].array_index),
    ):
        records.append(
            {
                "data_path": fcurve.data_path,
                "array_index": fcurve.array_index,
                "keys": [
                    [float(point.co.x), float(point.co.y), point.interpolation]
                    for point in fcurve.keyframe_points
                ],
            }
        )
    return hashlib.sha256(
        json.dumps(records, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest().upper()


def import_bvh_animation_action(req: Dict[str, Any]) -> Dict[str, Any]:
    """Native-import and retarget one receipt-verified professional BVH action."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    source = within(job, payload["source_rel"])
    provenance_path = within(job, payload["provenance_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    source_action_name = explicit_bvh_action_name(
        payload.get("source_action_name"), "source_action_name"
    )
    if source.stem != source_action_name:
        raise ValueError(
            "source_action_name must exactly match the verified BVH filename stem."
        )
    target_armature_name = explicit_safe_name(
        payload.get("target_armature_name"), "target_armature_name"
    )
    target_action_name = explicit_action_name(
        payload.get("target_action_name"), "target_action_name"
    )
    semantic_role = explicit_safe_name(payload.get("semantic_role"), "semantic_role")
    normalized_role = semantic_role.casefold().replace("-", "_").replace(".", "_")
    normalized_target = target_action_name.casefold().replace("-", "_").replace(".", "_")
    if normalized_role not in normalized_target:
        raise ValueError("target_action_name must contain the explicit semantic_role identity.")
    source_reference_id = explicit_reference_id(
        payload.get("source_reference_id"), "source_reference_id"
    )
    expected_source_sha256 = str(payload.get("source_sha256") or "").upper()
    if not re.fullmatch(r"[0-9A-F]{64}", expected_source_sha256):
        raise ValueError("source_sha256 must be an explicit 64-character SHA-256 digest.")
    actual_source_sha256 = file_sha256(source)
    if actual_source_sha256 != expected_source_sha256:
        raise RuntimeError(
            "BVH source checksum did not match the verified provenance receipt: "
            f"expected {expected_source_sha256}, observed {actual_source_sha256}."
        )
    source_fps = float(payload.get("source_fps") or 0.0)
    target_fps = float(payload.get("target_fps") or 0.0)
    if not math.isfinite(source_fps) or not math.isfinite(target_fps) or source_fps <= 0.0 or target_fps <= 0.0:
        raise ValueError("BVH import requires finite positive source_fps and target_fps.")
    if target_fps > 240.0:
        raise ValueError("BVH target_fps must not exceed 240.")
    root_motion_policy = str(payload.get("root_motion_policy") or "")
    if root_motion_policy != "in_place_xy_preserve_z":
        raise ValueError("root_motion_policy must be in_place_xy_preserve_z.")
    global_scale = float(payload.get("global_scale", 1.0))
    if not math.isfinite(global_scale) or not 0.0001 <= global_scale <= 1000000.0:
        raise ValueError("global_scale must be finite and between 0.0001 and 1000000.")
    axis_forward = str(payload.get("axis_forward") or "-Z")
    axis_up = str(payload.get("axis_up") or "Y")
    axes = {"X", "Y", "Z", "-X", "-Y", "-Z"}
    if axis_forward not in axes or axis_up not in axes or axis_forward.lstrip("-") == axis_up.lstrip("-"):
        raise ValueError("BVH forward/up axes must be distinct signed X, Y, or Z axes.")
    raw_bone_chains = payload.get("bone_chains")
    if not isinstance(raw_bone_chains, dict) or not raw_bone_chains:
        raise ValueError("bone_chains is required for fail-closed BVH retargeting.")

    header = inspect_bvh_header(source)
    fps_tolerance = max(0.01, source_fps * 0.001)
    if abs(float(header["source_fps"]) - source_fps) > fps_tolerance:
        raise ValueError(
            "Declared BVH source_fps does not match Frame Time: "
            f"declared={source_fps}, observed={header['source_fps']}."
        )
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("BVH provenance receipt is not valid JSON.") from exc
    required_provenance = {
        "verification_status": "verified",
        "source_kind": "professional_source",
        "source_format": "bvh",
        "source_reference_id": source_reference_id,
        "source_action_name": source_action_name,
        "source_sha256": expected_source_sha256,
        "source_fps": source_fps,
    }
    mismatches = {
        key: {"expected": value, "observed": provenance.get(key)}
        for key, value in required_provenance.items()
        if provenance.get(key) != value
    }
    if mismatches:
        raise ValueError(
            "BVH provenance receipt does not verify the requested source action: "
            + json.dumps(mismatches, sort_keys=True)
        )

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    matching_targets = [rig for rig in armatures() if rig.name == target_armature_name]
    if len(armatures()) != 1 or len(matching_targets) != 1:
        raise RuntimeError("BVH retarget requires exactly one explicitly named working target armature.")
    if bpy.data.actions.get(target_action_name) is not None:
        raise RuntimeError("BVH target action already exists; action aliases or replacement are forbidden.")

    clear_scene()
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    import io_anim_bvh  # type: ignore
    from io_anim_bvh import import_bvh as native_import_bvh  # type: ignore

    try:
        io_anim_bvh.register()
    except ValueError:
        pass
    scene = bpy.context.scene
    scene.render.fps = max(1, int(round(target_fps)))
    scene.render.fps_base = scene.render.fps / target_fps
    before_objects = set(bpy.data.objects)
    before_actions = set(bpy.data.actions)
    native_result = bpy.ops.import_anim.bvh(
        filepath=str(source),
        target="ARMATURE",
        global_scale=global_scale,
        frame_start=1,
        use_fps_scale=True,
        update_scene_fps=False,
        update_scene_duration=True,
        use_cyclic=False,
        rotate_mode="QUATERNION",
        axis_forward=axis_forward,
        axis_up=axis_up,
    )
    if "FINISHED" not in native_result:
        raise RuntimeError(f"Blender native BVH import failed: {sorted(native_result)}")
    imported_rigs = [obj for obj in bpy.data.objects if obj not in before_objects and obj.type == "ARMATURE"]
    imported_actions = [action for action in bpy.data.actions if action not in before_actions]
    if len(imported_rigs) != 1 or len(imported_actions) != 1:
        raise RuntimeError(
            "Native BVH import must produce exactly one armature and one action: "
            + json.dumps(
                {"armatures": [rig.name for rig in imported_rigs], "actions": [action.name for action in imported_actions]},
                sort_keys=True,
            )
        )
    source_rig = imported_rigs[0]
    source_action = imported_actions[0]
    native_action_name = source_action.name
    derived_action_name = f"BVH_{source_action_name}"
    source_action.name = derived_action_name
    source_action.use_fake_user = True
    source_rig.animation_data_create()
    source_rig.animation_data.action = source_action
    derived_rel = f"blender/source/bvh_{safe_name(target_action_name)}_{actual_source_sha256[:12]}.blend"
    derived = within(job, derived_rel, allow_missing=True)
    save_blend(derived)
    derived_sha256 = file_sha256(derived)
    derived_receipt_rel = f"blender/reports/bvh_{safe_name(target_action_name)}_derived_receipt.json"
    derived_receipt = within(job, derived_receipt_rel, allow_missing=True)
    derived_receipt.parent.mkdir(parents=True, exist_ok=True)
    derived_receipt.write_text(
        json.dumps(
            {
                "verification_status": "verified",
                "source_kind": "professional_source",
                "source_reference_id": f"{source_reference_id}.native_bvh",
                "source_action_name": derived_action_name,
                "source_sha256": derived_sha256,
                "derived_from_bvh_rel": str(source.relative_to(job)).replace("\\", "/"),
                "derived_from_bvh_sha256": actual_source_sha256,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    transfer = import_animation_action(
        {
            "job_root": str(job),
            "payload": {
                "blend_rel": str(blend.relative_to(job)).replace("\\", "/"),
                "source_rel": derived_rel,
                "provenance_rel": derived_receipt_rel,
                "checkpoint_rel": str(checkpoint.relative_to(job)).replace("\\", "/"),
                "source_action_name": derived_action_name,
                "target_armature_name": target_armature_name,
                "target_action_name": target_action_name,
                "source_kind": "professional_source",
                "source_reference_id": f"{source_reference_id}.native_bvh",
                "source_sha256": derived_sha256,
                "bone_chains": raw_bone_chains,
                "promote_audited_target": bool(payload.get("promote_audited_target", False)),
            },
        }
    )

    bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
    target_action = bpy.data.actions.get(target_action_name)
    target_rig = bpy.data.objects.get(target_armature_name)
    if target_action is None or target_rig is None or target_rig.type != "ARMATURE":
        raise RuntimeError("BVH retarget checkpoint lost the exact target armature or action identity.")
    target_action["hoi4_animation_source_kind"] = "professional_source"
    target_action["hoi4_animation_source_reference_id"] = source_reference_id
    target_action["hoi4_animation_source_sha256"] = actual_source_sha256
    target_action["hoi4_animation_source_action"] = source_action_name
    target_action["hoi4_animation_provenance_rel"] = str(provenance_path.relative_to(job)).replace("\\", "/")
    target_action["hoi4_animation_processing_policy"] = "native_bvh_import_hierarchy_retarget_source_motion_only"
    target_action["hoi4_animation_source_format"] = "bvh"
    target_action["hoi4_animation_semantic_role"] = semantic_role
    target_action["hoi4_animation_source_fps"] = source_fps
    target_action["hoi4_animation_target_fps"] = target_fps
    target_action["hoi4_animation_root_motion_policy"] = root_motion_policy
    target_action["hoi4_animation_derived_blend_sha256"] = derived_sha256
    target_rig.animation_data_create()
    target_rig.animation_data.action = target_action
    curves = list(action_fcurves(target_action))
    scale_curves = [curve.data_path for curve, _ in curves if curve.data_path.endswith(".scale")]
    driven_bones = sorted(
        {
            match.group(1)
            for curve, _ in curves
            for match in [re.search(r'pose\.bones\["([^"]+)"\]', curve.data_path)]
            if match is not None
        }
    )
    articulated_bones = set()
    for curve, _ in curves:
        if "rotation" not in curve.data_path or not curve.keyframe_points:
            continue
        values = [float(point.co.y) for point in curve.keyframe_points]
        if max(values) - min(values) > 1e-4:
            match = re.search(r'pose\.bones\["([^"]+)"\]', curve.data_path)
            if match:
                articulated_bones.add(match.group(1))
    if scale_curves or len(driven_bones) < 6 or len(articulated_bones) < 4:
        raise RuntimeError(
            "BVH semantic/curve audit rejected a static, scale-bearing, or insufficiently articulated action: "
            + json.dumps(
                {"scale_curves": scale_curves, "driven_bones": driven_bones, "articulated_bones": sorted(articulated_bones)},
                sort_keys=True,
            )
        )
    root_name = next((bone.name for bone in target_rig.data.bones if bone.parent is None), None)
    root_xy_peak = 0.0
    if root_name:
        root_path = f'pose.bones["{root_name}"].location'
        for curve, _ in curves:
            if curve.data_path == root_path and curve.array_index in {0, 1}:
                root_xy_peak = max(root_xy_peak, *(abs(float(point.co.y)) for point in curve.keyframe_points))
    if root_xy_peak > 1e-5:
        raise RuntimeError("BVH in-place root-motion audit retained X/Y displacement.")
    signature_before = action_curve_signature(target_action)
    target_action.use_fake_user = True
    save_blend(checkpoint)
    bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
    reopened_action = bpy.data.actions.get(target_action_name)
    reopened_rig = bpy.data.objects.get(target_armature_name)
    if reopened_action is None or reopened_rig is None:
        raise RuntimeError("BVH target action or armature did not survive checkpoint reopen.")
    signature_after = action_curve_signature(reopened_action)
    if signature_after != signature_before:
        raise RuntimeError("BVH target action curves changed across checkpoint save/reopen.")
    reopened_provenance = action_provenance(reopened_action)
    result = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "source": str(source.relative_to(job)).replace("\\", "/"),
        "source_sha256": actual_source_sha256,
        "provenance": str(provenance_path.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "source_action": source_action_name,
        "native_imported_action_name": native_action_name,
        "derived_action_name": derived_action_name,
        "target_action": target_action_name,
        "target_armature": target_armature_name,
        "semantic_role": semantic_role,
        "source_fps_declared": source_fps,
        "source_fps_observed": header["source_fps"],
        "target_fps": target_fps,
        "retime_policy": "Blender native BVH use_fps_scale into explicit target scene FPS",
        "root_motion_policy": root_motion_policy,
        "root_xy_peak_after": root_xy_peak,
        "bone_chains": raw_bone_chains,
        "bvh_header": header,
        "native_importer": {
            "module": "io_anim_bvh",
            "module_path": str(Path(io_anim_bvh.__file__).resolve()),
            "module_sha256": file_sha256(Path(io_anim_bvh.__file__).resolve()),
            "implementation_path": str(Path(native_import_bvh.__file__).resolve()),
            "implementation_sha256": file_sha256(Path(native_import_bvh.__file__).resolve()),
            "native_operator": "bpy.ops.import_anim.bvh",
            "axis_forward": axis_forward,
            "axis_up": axis_up,
            "global_scale": global_scale,
        },
        "derived_source": {"blend": derived_rel, "sha256": derived_sha256, "receipt": derived_receipt_rel},
        "transfer": transfer,
        "curve_audit": {
            "fcurves": len(curves),
            "driven_bones": driven_bones,
            "articulated_bones": sorted(articulated_bones),
            "scale_curves": [],
            "signature_before_save": signature_before,
            "signature_after_reopen": signature_after,
        },
        "action_provenance": reopened_provenance,
        "hoi4_animation_source_format": "bvh",
        "save_reopen_status": "pass",
        "manual_or_procedural_replacement_authored": False,
        "status": "pass",
    }
    report_path = job / "blender" / "reports" / f"import_bvh_{safe_name(target_action_name)}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def retime_animation_action(req: Dict[str, Any]) -> Dict[str, Any]:
    """Retiming an existing action changes sample time, not skeletal motion."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    target_armature_name = explicit_safe_name(payload.get("target_armature_name"), "target_armature_name")
    action_name = explicit_action_name(payload.get("action_name"), "action_name")
    source_fps = float(payload.get("source_fps") or 0.0)
    target_fps = float(payload.get("target_fps") or 0.0)
    if source_fps <= 0.0 or target_fps <= 0.0:
        raise ValueError("Animation retiming requires positive source and target FPS values.")

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    matching_rigs = [rig for rig in rigs if rig.name == target_armature_name]
    if len(rigs) != 1 or len(matching_rigs) != 1:
        raise RuntimeError(
            "Animation retiming requires exactly one explicitly named working armature: "
            + json.dumps(
                {
                    "requested_target_armature": target_armature_name,
                    "available_armatures": sorted(rig.name for rig in rigs),
                },
                sort_keys=True,
            )
        )
    rig = matching_rigs[0]
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
    provenance = action_provenance(action)

    old_start = float(action.frame_range[0])
    old_end = float(action.frame_range[1])
    fcurve_count_before = len(list(action_fcurves(action)))
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
        "target_armature": rig.name,
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
        "action_provenance": provenance,
        "retention_evidence": {
            "fcurve_count_before": fcurve_count_before,
            "fcurve_count_after": len(list(action_fcurves(action))),
            "keyframe_values_changed": False,
            "keyframe_times_rescaled": True,
            "manual_or_procedural_replacement_authored": False,
        },
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
    from animation_root_export import correct_exported_initial_roots
    initial_root_world_pose = correct_exported_initial_roots(output, rig, start, bpy)
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
        "initial_root_world_pose": initial_root_world_pose,
        "warnings": [],
    }
    report = job / "blender" / "reports" / f"export_anim_{safe_name(action.name)[:32]}_{hashlib.sha256(action.name.encode()).hexdigest()[:10]}.json"
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
    for rig in armatures():
        bpy.data.objects.remove(rig, do_unlink=True)

    minimum, maximum = world_bounds(working)
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
    rig["hoi4_humanoid_rig_route"] = "blender_failure_recovery_humanoid_v1"
    rig["hoi4_skeleton_contract"] = "hoi4_standard_humanoid_24_bone"
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
        shoulder = Vector((centre.x + sign * width * 0.18, centre.y - length * 0.01, z0 + height * 0.66))
        elbow = Vector((centre.x + sign * width * 0.32, centre.y - length * 0.04, z0 + height * 0.50))
        wrist = Vector((centre.x + sign * width * 0.38, centre.y - length * 0.07, z0 + height * 0.33))
        hand = Vector((centre.x + sign * width * 0.39, centre.y - length * 0.10, z0 + height * 0.22))
        add_bone(f"{side}Shoulder", shoulder, elbow, "Spine02")
        add_bone(f"{side}Arm", elbow, wrist, f"{side}Shoulder")
        add_bone(f"{side}ForeArm", wrist, hand, f"{side}Arm")
        add_bone(f"{side}Hand", hand, hand + Vector((0.0, -length * 0.06, -height * 0.04)), f"{side}ForeArm")

        hip = Vector((centre.x + sign * width * 0.10, centre.y + length * 0.01, z0 + height * 0.35))
        knee = Vector((centre.x + sign * width * 0.12, centre.y + length * 0.01, z0 + height * 0.20))
        ankle = Vector((centre.x + sign * width * 0.12, centre.y - length * 0.02, z0 + height * 0.08))
        toe = Vector((centre.x + sign * width * 0.12, centre.y - length * 0.13, z0 + height * 0.035))
        add_bone(f"{side}UpLeg", hip, knee, "Hips")
        add_bone(f"{side}Leg", knee, ankle, f"{side}UpLeg")
        add_bone(f"{side}Foot", ankle, toe, f"{side}Leg")
        add_bone(f"{side}ToeBase", toe, toe + Vector((0.0, -length * 0.07, 0.0)), f"{side}Foot")

    bpy.ops.object.mode_set(mode="OBJECT")
    rig.show_in_front = True
    armature_data.display_type = "BBONE"
    segments = {
        bone.name: (Vector(bone.head_local), Vector(bone.tail_local))
        for bone in armature_data.bones
    }
    records = []
    for obj in working:
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        groups = {name: obj.vertex_groups.new(name=name) for name in HUMANOID_BONE_NAMES}
        counts: Dict[str, int] = {name: 0 for name in groups}
        influence_histogram: Dict[str, int] = {"1": 0, "2": 0, "3": 0}
        for vertex in obj.data.vertices:
            world_position = obj.matrix_world @ vertex.co
            primary = _humanoid_bone_name_for_vertex(world_position, minimum, maximum)
            candidates = [name for name in _humanoid_weight_candidates(primary) if name in segments]
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
            weights = {primary: 0.68}
            if names:
                inverse = [1.0 / max(next((distance for distance, name in ranked if name == item), 1.0), 1e-4) for item in names]
                inverse_total = sum(inverse)
                for name, value in zip(names, inverse):
                    weights[name] = 0.32 * value / max(inverse_total, 1e-8)
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
    save_blend(checkpoint)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "armature": rig.name,
        "bones": [bone.name for bone in armature_data.bones],
        "bone_count": len(armature_data.bones),
        "component_bindings": records,
        "rig_route": "blender_failure_recovery_humanoid_v1",
        "rig_map": f"{rig_name}_hoi4_standard_humanoid_24_bones_v1",
        "weight_policy": "bounded same-region blended weights with at most three influences per vertex; no unweighted vertices",
        "source_policy": "Meshy 7 geometry retained; provider rig is not used",
        "status": "pass" if len(armature_data.bones) == len(HUMANOID_BONE_NAMES) else "failed",
    }
    report_path = job / "blender" / "reports" / "humanoid_rig.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _action_phase_inputs(req: Dict[str, Any]) -> Dict[str, Any]:
    payload = req["payload"]
    required = {"blend_rel", "checkpoint_rel", "expected_source_sha256", "expected_action_sha256", "target_armature_name", "source_action_name", "target_action_name", "semantic_role", "source_fps", "source_fps_base", "frame_start", "frame_end", "phase_frames", "allowed_bones", "motion_bone_chain", "bone_patches"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError("Action phase patch has missing or unsupported fields.")
    result = dict(payload)
    for key in ("target_armature_name", "source_action_name", "target_action_name"):
        result[key] = _mesh_region_name(payload[key], key)
    if result["source_action_name"] == result["target_action_name"]:
        raise ValueError("Source and new target action names must differ.")
    for key in ("expected_source_sha256", "expected_action_sha256"):
        if not isinstance(payload[key], str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", payload[key]):
            raise ValueError(f"{key} must be an explicit SHA-256.")
        result[key] = payload[key].upper()
    role_phases = {"attack": ("ready", "aim", "discharge", "recoil", "recovery"), "support_attack": ("ready", "aim", "discharge", "recoil", "recovery"), "defend": ("guard_start", "guard_hold", "guard_release"), "retreat": ("disengage", "withdrawal", "recovery"), "death": ("standing", "falling", "impact", "rebound", "settling", "terminal_hold")}
    role = payload["semantic_role"]
    if not isinstance(role, str) or role not in role_phases:
        raise ValueError("Unsupported action phase semantic role.")
    for key in ("frame_start", "frame_end"):
        if type(payload[key]) is not int or not 0 <= payload[key] <= 1000000:
            raise ValueError("Action frame endpoints must be bounded integers.")
    start, end = payload["frame_start"], payload["frame_end"]
    phases = payload["phase_frames"]
    if start >= end or not isinstance(phases, dict) or set(phases) != set(role_phases[role]):
        raise ValueError("Role requires the exact phase names and a nonempty action range.")
    ordered = [phases[name] for name in role_phases[role]]
    if any(type(frame) is not int or not start <= frame <= end for frame in ordered) or any(a >= b for a, b in zip(ordered, ordered[1:])):
        raise ValueError("Role phase frames must be strictly ordered inside the source action range.")
    result["phase_frames"] = {name: phases[name] for name in role_phases[role]}
    if type(payload["source_fps"]) is not int or not 1 <= payload["source_fps"] <= 1000:
        raise ValueError("Source FPS must be an explicit bounded positive integer.")
    fps_base = _locator_numbers([payload["source_fps_base"]], 1, "source FPS base")[0]
    if not 0 < fps_base <= 1000:
        raise ValueError("Source FPS base must be positive and bounded.")
    names = payload["allowed_bones"]
    if not isinstance(names, list) or not 1 <= len(names) <= 64:
        raise ValueError("allowed_bones requires 1-64 exact named bones.")
    names = [_mesh_region_name(name, "allowed bone") for name in names]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate allowed bone names are forbidden.")
    patches = payload["bone_patches"]
    if not isinstance(patches, dict) or set(patches) != set(names):
        raise ValueError("bone_patches must match the exact allowed bone list.")
    converted, key_count = {}, 0
    for name, channels in patches.items():
        if not isinstance(channels, dict) or not channels or set(channels) - {"location", "rotation_quaternion"}:
            raise ValueError("Bone patches accept only explicit location/quaternion channels, never scale.")
        converted[name] = {}
        for channel, rows in channels.items():
            if not isinstance(rows, list) or not 2 <= len(rows) <= 512:
                raise ValueError("A patched channel requires 2-512 explicit keys.")
            keys = []
            for row in rows:
                if not isinstance(row, dict) or set(row) != {"frame", "value"} or type(row["frame"]) is not int or not start <= row["frame"] <= end:
                    raise ValueError("Malformed or out-of-range action key.")
                values = _locator_numbers(row["value"], 4 if channel == "rotation_quaternion" else 3, "action key")
                if channel == "rotation_quaternion":
                    length = math.sqrt(sum(value * value for value in values))
                    if not math.isfinite(length) or abs(length - 1.0) > 1e-5:
                        raise ValueError("Action key must contain a finite nonzero unit quaternion within 1e-5; no normalization is performed.")
                elif any(abs(value) > 1000000 for value in values):
                    raise ValueError("Location key exceeds the bounded coordinate range.")
                keys.append({"frame": row["frame"], "value": values})
            frames = [row["frame"] for row in keys]
            if any(a >= b for a, b in zip(frames, frames[1:])) or not {start, end, *ordered}.issubset(frames):
                raise ValueError("Keys must be unique, ordered, and include every phase and both action endpoints.")
            key_count += len(keys)
            converted[name][channel] = keys
    if key_count > 4096:
        raise ValueError("Action patch exceeds 4096 vector keys.")
    chain = payload["motion_bone_chain"]
    if not isinstance(chain, list) or any(not isinstance(name, str) or name not in names for name in chain) or len(set(chain)) != len(chain):
        raise ValueError("Motion bone chain must contain unique explicitly patched bones.")
    if (role == "retreat" and not 2 <= len(chain) <= 16) or (role != "retreat" and chain):
        raise ValueError("Retreat requires a 2-16 bone chain; other roles must leave the chain empty.")
    job = Path(req["job_root"]).resolve()
    source = _promotion_path(job, payload["blend_rel"], ".blend")
    output = _promotion_path(job, payload["checkpoint_rel"], ".blend", missing=True)
    if source.parent != output.parent or output == source or output.exists():
        raise ValueError("Action patch output must be a new sibling; refusing existing output or overwrite.")
    if source.stat().st_size < 1 or file_sha256(source) != result["expected_source_sha256"]:
        raise ValueError("Action patch source SHA-256 mismatch.")
    result.update(job=job, source=source, output=output, source_bytes=source.stat().st_size, bone_patches=converted, vector_key_count=key_count)
    return result


def _action_phase_curve_records(action: Any, excluded_paths: Iterable[str] = ()) -> List[Dict[str, Any]]:
    excluded_paths = set(excluded_paths)
    return sorted([{"path": curve.data_path, "index": curve.array_index, "group": curve.group.name if curve.group else None,
                    "settings": _promotion_scalars(curve), "keys": [{"co": list(key.co), "left": list(key.handle_left), "right": list(key.handle_right), "settings": _promotion_scalars(key)} for key in curve.keyframe_points],
                    "samples": [list(point.co) for point in curve.sampled_points]}
                   for curve, _ in action_fcurves(action) if curve.data_path not in excluded_paths], key=lambda row: (row["path"], row["index"]))


def _action_phase_action_record(action: Any) -> Dict[str, Any]:
    return {"settings": _promotion_scalars(action), "properties": _promotion_properties(action), "fake_user": action.use_fake_user,
            "curves": _action_phase_curve_records(action), "slots": [_promotion_scalars(slot) for slot in getattr(action, "slots", [])],
            "layers": [{"settings": _promotion_scalars(layer), "strips": [{"type": strip.type, "bags": [bag.slot_handle for bag in getattr(strip, "channelbags", [])]} for strip in layer.strips]} for layer in getattr(action, "layers", [])]}


def _action_phase_restore(rig: Any, state: Dict[str, Any]) -> None:
    rig.animation_data.action = state["action"]
    if state["slot"] is not None:
        rig.animation_data.action_slot = state["slot"]
    for name, channels in state["pose"].items():
        for channel, values in channels.items():
            setattr(rig.pose.bones[name], channel, values)
    bpy.context.scene.frame_set(state["frame"], subframe=state["subframe"])
    bpy.context.view_layer.update()


def _action_phase_samples(rig: Any, action: Any, meshes: List[Any], context: Dict[str, Any]) -> Dict[str, Any]:
    rig.animation_data.action = action
    if getattr(action, "slots", []):
        rig.animation_data.action_slot = action.slots[0]
    samples = {}
    locators = [obj for obj in bpy.context.scene.objects if obj.type == "EMPTY" and obj.parent == rig and obj.parent_type == "BONE"]
    if len(locators) > 32:
        raise ValueError("Action phase locator count exceeds 32.")
    for phase, frame in context["phase_frames"].items():
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bones = {name: {"basis": _locator_matrix_record(rig.pose.bones[name].matrix_basis), "pose": _locator_matrix_record(rig.pose.bones[name].matrix),
                        "world": _locator_matrix_record(rig.matrix_world @ rig.pose.bones[name].matrix)} for name in context["allowed_bones"]}
        mesh_records = []
        for mesh in meshes:
            evaluated = mesh.evaluated_get(depsgraph)
            temporary = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
            try:
                if len(temporary.vertices) != len(mesh.data.vertices):
                    raise ValueError("Action evaluation changed the source vertex count.")
                points = [(vertex.index, evaluated.matrix_world @ vertex.co) for vertex in temporary.vertices]
                for _, point in points:
                    _locator_numbers(list(point), 3, "phase evaluated position")
                low = [min(point[axis] for _, point in points) for axis in range(3)]
                high = [max(point[axis] for _, point in points) for axis in range(3)]
                lowest = min(points, key=lambda item: item[1].z)
                mesh_records.append({"name": mesh.name, "bounds_min": low, "bounds_max": high, "lowest_vertex_index": lowest[0], "lowest_world_position": list(lowest[1]), "ground_contact_verified": False})
            finally:
                evaluated.to_mesh_clear()
        samples[phase] = {"frame": frame, "seconds_from_action_start": (frame - context["frame_start"]) * context["source_fps_base"] / context["source_fps"],
                          "bones": bones, "meshes": mesh_records, "locators": [{"name": obj.name, "parent_bone": obj.parent_bone, "world": _locator_matrix_record(obj.evaluated_get(depsgraph).matrix_world)} for obj in locators]}
    _promotion_digest(samples)
    return samples


def _action_phase_delta(left: Any, right: Any) -> float:
    return max(abs(left[row][column] - right[row][column]) for row in range(4) for column in range(4))


def _action_phase_motion(context: Dict[str, Any], rig: Any, source: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    changed = {name: max(_action_phase_delta(source[phase]["bones"][name]["basis"], target[phase]["bones"][name]["basis"]) for phase in target) for name in context["allowed_bones"]}
    changed = {name: delta for name, delta in changed.items() if delta > 1e-6}
    if not changed:
        raise ValueError("Action patch is identity-only at the required phases.")
    non_root = [name for name in changed if rig.data.bones[name].parent is not None]
    if not non_root:
        raise ValueError("Action patch requires genuinely changed non-root bone channels.")
    pairs = {"attack": (("ready", "aim"), ("discharge", "recoil"), ("recoil", "recovery")), "support_attack": (("ready", "aim"), ("discharge", "recoil"), ("recoil", "recovery")),
             "defend": (("guard_start", "guard_hold"), ("guard_hold", "guard_release")), "retreat": (("disengage", "withdrawal"), ("withdrawal", "recovery")),
             "death": (("standing", "falling"), ("falling", "impact"), ("impact", "rebound"), ("rebound", "settling"))}
    transitions = {}
    for start, end in pairs[context["semantic_role"]]:
        deltas = {name: _action_phase_delta(target[start]["bones"][name]["basis"], target[end]["bones"][name]["basis"]) for name in non_root}
        if max(deltas.values()) <= 1e-6:
            raise ValueError(f"Required phase transition {start}/{end} has no distinguishable non-root articulation.")
        transitions[f"{start}/{end}"] = deltas
    if context["semantic_role"] == "defend" and not any(_action_phase_delta(source["guard_hold"]["bones"][name]["basis"], target["guard_hold"]["bones"][name]["basis"]) > 1e-6 for name in non_root):
        raise ValueError("Defensive guard hold is indistinguishable from the source action.")
    if context["semantic_role"] == "retreat" and any(name not in non_root for name in context["motion_bone_chain"]):
        raise ValueError("Every declared retreat-chain bone must have genuine changed non-root channels.")
    return {"changed_bones": changed, "phase_transitions": transitions, "numerical_identity_tolerance": 1e-6, "semantic_acceptance": False}


def _action_phase_execute(req: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    job, source, output = context["job"], context["source"], context["output"]
    bpy.ops.wm.open_mainfile(filepath=str(source), use_scripts=False)
    rig = bpy.context.scene.objects.get(context["target_armature_name"])
    if rig is None or rig.type != "ARMATURE" or rig.library or rig.override_library or rig.data.library or rig.data.override_library or not rig.get("hoi4_working"):
        raise ValueError("Action phase patch requires the exact local working armature.")
    if rig.get("hoi4_source_protected") or rig.get("hoi4_reference_read_only") or rig.constraints or any(bone.constraints for bone in rig.pose.bones) or rig.data.pose_position != "POSE":
        raise ValueError("Action phase patch rejects protected/reference rigs, constraints, and REST display.")
    animation = rig.animation_data
    if animation is None or animation.drivers or animation.nla_tracks:
        raise ValueError("Action phase patch requires existing animation data without drivers/NLA.")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and any(mod.type == "ARMATURE" and mod.object == rig for mod in obj.modifiers)]
    if not 1 <= len(meshes) <= 16 or sum(len(obj.data.vertices) for obj in meshes) > 1000000:
        raise ValueError("Action phase patch requires 1-16 bound meshes within one million vertices.")
    for mesh in meshes:
        _mesh_region_object_dependencies(mesh, rig)
        if mesh.library or mesh.override_library or mesh.data.library or mesh.data.override_library or mesh.constraints or mesh.animation_data or mesh.data.shape_keys or not mesh.data.vertices or not mesh.get("hoi4_working"):
            raise ValueError("Action phase patch requires local working meshes without shape keys, constraints, or mesh animation.")
        if mesh.get("hoi4_source_protected") or mesh.get("hoi4_reference_read_only") or len(mesh.modifiers) != 1 or not mesh.modifiers[0].show_viewport:
            raise ValueError("Action phase patch rejects protected meshes or additional/disabled modifiers.")
        for obj in (mesh, rig):
            if any(value <= 0 for value in obj.scale):
                raise ValueError("Action phase patch rejects negative/singular object scale.")
            _mesh_region_matrix(obj.matrix_world, obj.name)
    action = bpy.data.actions.get(context["source_action_name"])
    if action is None or action.library or action.override_library or len(getattr(action, "slots", [])) > 1:
        raise ValueError("Action phase patch requires one exact local source action with an unambiguous slot.")
    if bpy.data.actions.get(context["target_action_name"]) is not None:
        raise ValueError("Target action already exists; refusing overwrite.")
    curves = list(action_fcurves(action))
    if not curves or len(curves) > 4096 or any(curve.modifiers or curve.sampled_points for curve, _ in curves):
        raise ValueError("Action phase patch requires bounded keyed curves without modifiers or sampled curves.")
    if any(not curve.data_path.startswith('pose.bones[') or not curve.data_path.endswith((".location", ".rotation_quaternion")) for curve, _ in curves):
        raise ValueError("Source action has unsupported object, scale, or non-quaternion bone channels.")
    if len({(curve.data_path, curve.array_index) for curve, _ in curves}) != len(curves):
        raise ValueError("Source action has duplicate/ambiguous bone channels.")
    if len(getattr(action, "layers", [])) > 1 or any(len(layer.strips) != 1 or len(layer.strips[0].channelbags) != 1 for layer in getattr(action, "layers", [])):
        raise ValueError("Action phase patch requires one unambiguous layer/strip/channel bag.")
    if list(action.frame_range) != [context["frame_start"], context["frame_end"]]:
        raise ValueError("Source action frame range mismatch; this operation never retimes.")
    scene = bpy.context.scene
    if scene.render.fps != context["source_fps"] or scene.render.fps_base != context["source_fps_base"]:
        raise ValueError("Source native FPS/FPS-base mismatch; this operation never retimes.")
    if _mesh_region_action_hash(action) != context["expected_action_sha256"]:
        raise ValueError("Source native action SHA-256 mismatch.")
    for name in context["allowed_bones"]:
        bone = rig.pose.bones.get(name)
        if bone is None or bone.rotation_mode != "QUATERNION" or any(value <= 0 for value in bone.scale):
            raise ValueError("Patched bones must exist with quaternion mode and positive pose scale.")
    chain = context["motion_bone_chain"]
    if chain and (rig.data.bones[chain[0]].parent is None or any(rig.data.bones[child].parent != rig.data.bones[parent] for parent, child in zip(chain, chain[1:]))):
        raise ValueError("Retreat motion bone chain must be contiguous and non-root.")
    before = _promotion_fingerprint(job, ())
    paths = {rig.pose.bones[name].path_from_id(channel) for name, channels in context["bone_patches"].items() for channel in channels}
    untouched = _action_phase_curve_records(action, paths)
    state = {"action": animation.action, "slot": getattr(animation, "action_slot", None), "frame": scene.frame_current, "subframe": scene.frame_subframe,
             "pose": {bone.name: {channel: list(getattr(bone, channel)) for channel in ("location", "rotation_quaternion", "rotation_euler", "rotation_axis_angle", "scale")} for bone in rig.pose.bones}}
    target = None
    try:
        source_phases = _action_phase_samples(rig, action, meshes, context)
        target = action.copy()
        target.name, target.use_fake_user = context["target_action_name"], True
        if target.name != context["target_action_name"]:
            raise ValueError("Native target action name differs from the exact requested name.")
        animation.action = target
        if getattr(target, "slots", []):
            animation.action_slot = target.slots[0]
        for curve, collection in list(action_fcurves(target)):
            if curve.data_path in paths:
                collection.remove(curve)
        expected_keys = {}
        for name, channels in context["bone_patches"].items():
            for channel, keys in channels.items():
                path = rig.pose.bones[name].path_from_id(channel)
                expected_keys[path] = []
                for key in keys:
                    setattr(rig.pose.bones[name], channel, key["value"])
                    expected_keys[path].append((key["frame"], list(getattr(rig.pose.bones[name], channel))))
                    if not rig.pose.bones[name].keyframe_insert(data_path=channel, frame=key["frame"], group=name):
                        raise RuntimeError("Native insertion rejected an explicit phase key.")
        for curve, _ in action_fcurves(target):
            if curve.data_path in paths:
                for key in curve.keyframe_points:
                    key.interpolation = "LINEAR"
                curve.update()
        for path, keys in expected_keys.items():
            written = {curve.array_index: curve for curve, _ in action_fcurves(target) if curve.data_path == path}
            if set(written) != set(range(len(keys[0][1]))):
                raise RuntimeError("Native insertion produced incomplete declared phase channels.")
            for index, curve in written.items():
                if [(point.co.x, point.co.y) for point in curve.keyframe_points] != [(frame, values[index]) for frame, values in keys]:
                    raise RuntimeError("Native stored keys differ from the explicitly supplied phase keys.")
        if _action_phase_curve_records(target, paths) != untouched:
            raise RuntimeError("Declared patch changed an undeclared source channel.")
        target_phases = _action_phase_samples(rig, target, meshes, context)
        motion = _action_phase_motion(context, rig, source_phases, target_phases)
        target_hash = _mesh_region_action_hash(target)
        if any(_mesh_region_action_hash(other) == target_hash for other in bpy.data.actions if other != target):
            raise ValueError("Patched action aliases an existing action fingerprint.")
        target["hoi4_animation_processing_policy"] = "authorized_existing_action_declarative_phase_patch"
        target["hoi4_action_phase_source_sha256"] = context["expected_source_sha256"]
        target["hoi4_action_phase_source_action"] = action.name
        target["hoi4_action_phase_source_action_sha256"] = context["expected_action_sha256"]
        target["hoi4_action_phase_role"] = context["semantic_role"]
        target["hoi4_action_phase_request_sha256"] = _promotion_digest(req["payload"])
        target["hoi4_action_phase_semantic_acceptance"] = False
    except Exception:
        _action_phase_restore(rig, state)
        if target is not None:
            bpy.data.actions.remove(target)
        raise
    _action_phase_restore(rig, state)
    if _promotion_fingerprint(job, (), exclude_action_name=target.name) != before:
        raise RuntimeError("Action patch changed original scene/action data before saving.")
    target_record = _action_phase_action_record(target)
    if output.exists():
        raise ValueError("Action patch output appeared during processing; refusing overwrite.")
    saved = bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True, relative_remap=False)
    if "FINISHED" not in saved or not output.is_file():
        raise RuntimeError("Action patch checkpoint save did not finish.")
    bpy.ops.wm.open_mainfile(filepath=str(output), use_scripts=False)
    target = bpy.data.actions.get(context["target_action_name"])
    if target is None or _action_phase_action_record(target) != target_record:
        raise RuntimeError("New target action changed during save/reopen.")
    after = _promotion_fingerprint(job, (), exclude_action_name=context["target_action_name"])
    comparison = _promotion_reopen_comparison(before, after)
    if not comparison["accepted"]:
        raise RuntimeError(f"Action patch violated original-scene preservation: {comparison['mismatches']}")
    return {"operation": "patch_existing_humanoid_action_phases", "source": source.relative_to(job).as_posix(), "checkpoint": output.relative_to(job).as_posix(),
            "source_sha256": context["expected_source_sha256"], "source_bytes": context["source_bytes"], "source_immutable": True,
            "output_sha256": file_sha256(output), "output_bytes": output.stat().st_size,
            "source_action_name": context["source_action_name"], "target_action_name": target.name,
            "source_action_sha256": context["expected_action_sha256"], "target_action_sha256": target_hash,
            "target_action_record_sha256": _promotion_digest(target_record), "target_action_reopen_exact": True, "original_actions_unchanged": True,
            "preserved_before": before, "preserved_after": after, "reopen_comparison": comparison,
            "source_fps": context["source_fps"], "source_fps_base": context["source_fps_base"],
            "frame_range": [context["frame_start"], context["frame_end"]], "semantic_role": context["semantic_role"],
            "phase_frames": context["phase_frames"], "motion_bone_chain": chain, "vector_key_count": context["vector_key_count"],
            "patched_channels": {name: list(channels) for name, channels in context["bone_patches"].items()},
            "source_phases": source_phases, "target_phases": target_phases, **motion,
            "manual_or_procedural_replacement_authored": True, "procedural_generator_used": False,
            "root_policy": "no_object_channels_authored_source_root_bone_channels_preserved_unless_explicitly_patched",
            "quaternion_norm_tolerance": 1e-5, "new_provider_call": False, "runtime_acceptance": False}


def patch_existing_humanoid_action_phases(req: Dict[str, Any]) -> Dict[str, Any]:
    """Apply explicit authorized manual phase keys to a clone; never mutate the source."""
    context = _action_phase_inputs(req)
    try:
        return _action_phase_execute(req, context)
    finally:
        if file_sha256(context["source"]) != context["expected_source_sha256"] or context["source"].stat().st_size != context["source_bytes"]:
            raise RuntimeError("Action phase patch source checkpoint changed.")


def author_humanoid_actions(req: Dict[str, Any]) -> Dict[str, Any]:
    """Author the four required in-place HOI4 humanoid skeletal actions."""

    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = within(job, payload["blend_rel"])
    checkpoint = within(job, payload["checkpoint_rel"], allow_missing=True)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    if len(rigs) != 1:
        raise RuntimeError(f"Humanoid action authoring requires exactly one armature, found {len(rigs)}.")
    rig = rigs[0]
    rig.animation_data_create()
    scene = bpy.context.scene
    scene.render.fps = int(payload.get("fps") or 24)
    base_rig_location = rig.location.copy()
    action_reports: Dict[str, Dict[str, Any]] = {}

    def role_frames(role: str) -> List[int]:
        return {
            "idle": [0, 12, 24, 36, 48],
            "move": [0, 6, 12, 18, 24],
            "attack": [0, 8, 16, 24, 32],
            "death": [0, 12, 24, 36],
        }[role]

    def phase(role: str, frame: int, frames: List[int]) -> float:
        normalized = (frame - frames[0]) / max(frames[-1] - frames[0], 1)
        if role in {"idle", "move"}:
            return math.sin(2.0 * math.pi * normalized)
        if role == "attack":
            return math.sin(math.pi * normalized)
        return normalized

    for role in ("idle", "move", "attack", "death"):
        frames = role_frames(role)
        action_name = safe_name(str(payload.get("action_names", {}).get(role) or f"hoi4_humanoid_{role}"))
        old_action = bpy.data.actions.get(action_name)
        if old_action is not None:
            bpy.data.actions.remove(old_action)
        action = bpy.data.actions.new(action_name)
        action.use_fake_user = True
        rig.animation_data.action = action
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

        for frame in frames:
            scene.frame_set(frame)
            p = phase(role, frame, frames)
            for bone in rig.pose.bones:
                bone.rotation_mode = "QUATERNION"
                bone.location = base[bone.name][0].copy()
                bone.rotation_quaternion = base[bone.name][1].copy()
                bone.scale = (1.0, 1.0, 1.0)
            if role == "idle":
                rotate("Spine01", "x", 1.0, p)
                rotate("Spine02", "x", 1.5, p)
                rotate("neck", "x", 2.0, p)
                rotate("Head", "z", 1.0, p)
                rotate("LeftForeArm", "x", 1.0, p)
                rotate("RightForeArm", "x", -1.0, p)
            elif role == "move":
                for side, sign in (("Left", 1.0), ("Right", -1.0)):
                    gait = sign * p
                    rotate(f"{side}UpLeg", "x", 24.0, gait)
                    rotate(f"{side}Leg", "x", -10.0, gait)
                    rotate(f"{side}Foot", "x", 8.0, gait)
                    rotate(f"{side}Arm", "x", -16.0, gait)
                    rotate(f"{side}ForeArm", "x", -6.0, gait)
                rotate("Spine01", "x", 2.0, p)
                rotate("Spine02", "x", 1.5, p)
                rotate("neck", "x", -1.0, p)
                rotate("Head", "z", 1.0, p)
                hips = rig.pose.bones.get("Hips")
                if hips is not None:
                    hips.location = base["Hips"][0] + Vector((0.0, 0.0, 0.001 * p))
            elif role == "attack":
                rotate("Spine01", "x", -10.0, p)
                rotate("Spine02", "x", -8.0, p)
                rotate("neck", "x", -8.0, p)
                rotate("Head", "x", -12.0, p)
                for side, sign in (("Left", 1.0), ("Right", -1.0)):
                    rotate(f"{side}Shoulder", "x", -22.0, p)
                    rotate(f"{side}Arm", "x", -30.0, p)
                    rotate(f"{side}ForeArm", "x", -18.0, p)
                    rotate(f"{side}Hand", "z", 8.0 * sign, p)
                    rotate(f"{side}UpLeg", "x", -5.0, p)
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
            for bone in rig.pose.bones:
                bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
                bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=bone.name)

        for fcurve, _ in action_fcurves(action):
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "LINEAR"

        ground_samples_before = []
        ground_samples_after = []
        corrections = []
        for frame in range(frames[0], frames[-1] + 1):
            scene.frame_set(frame)
            rig.location = base_rig_location.copy()
            bpy.context.view_layer.update()
            minimum, maximum = evaluated_world_bounds(mesh_objects())
            ground_samples_before.append({"frame": frame, "ground_contact_z": float(minimum.z), "bounds_max_z": float(maximum.z)})
            correction = max(0.0, -float(minimum.z))
            rig.location.z = base_rig_location.z + correction
            rig.keyframe_insert(data_path="location", index=2, frame=frame, group=rig.name)
            bpy.context.view_layer.update()
            corrected_minimum, corrected_maximum = evaluated_world_bounds(mesh_objects())
            ground_samples_after.append({"frame": frame, "ground_contact_z": float(corrected_minimum.z), "bounds_max_z": float(corrected_maximum.z)})
            corrections.append(correction)

        scene.frame_set(frames[0])
        rig.location = base_rig_location.copy()
        metrics = action_metrics()
        report = {
            "action": action.name,
            "role": role,
            "frame_start": frames[0],
            "frame_end": frames[-1],
            "fps": scene.render.fps,
            "loop": role in {"idle", "move"},
            "keyed_bones": len(rig.pose.bones) * len(frames),
            "keyed_channels": len(rig.pose.bones) * len(frames) * 2,
            "ground_contact": {
                "minimum_z": min(item["ground_contact_z"] for item in ground_samples_after),
                "maximum_z": max(item["ground_contact_z"] for item in ground_samples_after),
                "samples_before": ground_samples_before,
                "samples_after": ground_samples_after,
            },
            "grounding_correction": {
                "applied": any(value > 0.0 for value in corrections),
                "maximum_translation_m": max(corrections, default=0.0),
            },
            "policy": "blender-authored-hoi4-humanoid-skeletal-action-in-place-no-scale-channels",
            "rig_and_actions": metrics,
            "status": "pass" if min(item["ground_contact_z"] for item in ground_samples_after) >= -0.01 else "needs_grounding_review",
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
        "required_roles": ["idle", "move", "attack", "death"],
        "source_policy": "Meshy 7 geometry retained; actions authored locally only after provider-rig recovery failure",
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
    if str(payload.get("creature_rig_family") or "elephant").casefold() != "elephant":
        raise ValueError("Unsupported creature rig family; use explicit measured rig authoring.")
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
    if str(payload.get("creature_rig_family") or "elephant").casefold() != "elephant":
        raise ValueError("Unsupported creature action family; use explicit measured action authoring.")
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
    target_armature_name = explicit_safe_name(payload.get("target_armature_name"), "target_armature_name")
    action_name = explicit_action_name(payload.get("action_name"), "action_name")
    root_bone_name = explicit_safe_name(payload.get("root_bone"), "root_bone")
    excluded_contact_bones = sorted(
        {
            explicit_safe_name(value, "excluded_contact_bones")
            for value in payload.get("excluded_contact_bones", [])
        }
    )
    grounding_policy = str(payload.get("grounding_policy") or "")
    if grounding_policy != "per_frame_root_contact_zero_clearance":
        raise ValueError(
            "grounding_policy must be per_frame_root_contact_zero_clearance; "
            "the adapter does not author or synthesize replacement body motion."
        )

    bpy.ops.wm.open_mainfile(filepath=str(blend))
    rigs = armatures()
    matching_rigs = [rig for rig in rigs if rig.name == target_armature_name]
    if len(rigs) != 1 or len(matching_rigs) != 1:
        raise RuntimeError(
            "Grounding correction requires exactly one explicitly named working armature: "
            + json.dumps(
                {
                    "requested_target_armature": target_armature_name,
                    "available_armatures": sorted(rig.name for rig in rigs),
                },
                sort_keys=True,
            )
        )
    rig = matching_rigs[0]
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
    provenance = action_provenance(action)
    fcurve_count_before = len(list(action_fcurves(action)))
    rig.animation_data.action = action
    root = rig.pose.bones.get(root_bone_name)
    if root is None:
        raise RuntimeError(f"Grounding correction root bone was not found: {root_bone_name}")
    unknown_contact_exclusions = sorted(set(excluded_contact_bones) - {bone.name for bone in rig.data.bones})
    if unknown_contact_exclusions:
        raise RuntimeError(
            "Grounding correction received unknown excluded contact bones: "
            + json.dumps(unknown_contact_exclusions)
        )
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
    baseline_minimum, _ = evaluated_contact_bounds(meshes, excluded_contact_bones)
    axis_responses = []
    for axis_index in range(3):
        original_axis_value = float(root.location[axis_index])
        root.location[axis_index] = original_axis_value + 1.0
        bpy.context.view_layer.update()
        test_minimum, _ = evaluated_contact_bounds(meshes, excluded_contact_bones)
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
        before_minimum, _ = evaluated_contact_bounds(meshes, excluded_contact_bones)
        original_value = float(root.location[correction_axis])
        test_step = 1.0
        write_root_z(frame, original_value + test_step)
        test_minimum, _ = evaluated_contact_bounds(meshes, excluded_contact_bones)
        write_root_z(frame, original_value)
        derivative = float(test_minimum.z - before_minimum.z) / test_step
        if abs(derivative) <= 1e-8:
            raise RuntimeError(f"Grounding correction found no usable root-Z response at frame {frame}.")
        correction = -float(before_minimum.z) / derivative
        write_root_z(frame, original_value + correction)
        after_minimum, _ = evaluated_contact_bounds(meshes, excluded_contact_bones)
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
        "target_armature": rig.name,
        "excluded_contact_bones": excluded_contact_bones,
        "contact_selection_policy": "exclude_vertices_dominated_by_named_bones",
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
            "grounding_policy": grounding_policy,
            "policy": "existing_action_root_z_only",
            "body_motion_replaced": False,
            "new_model_created": False,
            "new_rig_created": False,
            "new_provider_call": False,
        },
        "action_provenance": provenance,
        "retention_evidence": {
            "fcurve_count_before": fcurve_count_before,
            "fcurve_count_after": len(list(action_fcurves(action))),
            "only_root_location_channel_corrected": True,
            "body_motion_keys_retained": True,
            "manual_or_procedural_replacement_authored": False,
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
        "target_armature": rig.name,
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
    stage_defaults = payload.get("stage_default_textures", True)
    if type(stage_defaults) is not bool:
        raise ValueError("stage_default_textures must be an explicit boolean.")
    if not stage_defaults:
        adjacent = sorted(mesh.parent.glob("*.dds"))
        if not 1 <= len(adjacent) <= 128:
            raise ValueError("Preserved candidate textures require 1-128 adjacent DDS files.")
        for path in adjacent:
            if path.stat().st_size < 128 or path.read_bytes()[:4] != b"DDS ":
                raise ValueError("Invalid prestaged candidate DDS.")
            texture_staging.append({"source":path.relative_to(job).as_posix(), "staged":path.relative_to(job).as_posix(), "bytes":path.stat().st_size, "sha256":file_sha256(path), "copied":False, "policy":"preserve_prestaged_candidate"})
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
    for texture_name in (tuple(dict.fromkeys(requested_texture_names + default_texture_names)) if stage_defaults else ()):
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
                        "locators": locator_records(),
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
            {
                "name": obj.name,
                "type": obj.type,
                "parent": obj.parent.name if obj.parent else None,
                "parent_type": obj.parent_type if obj.parent else None,
                "parent_bone": obj.parent_bone if obj.parent_type == "BONE" else None,
            }
            for obj in bpy.context.scene.objects
        ],
        "locators": locator_records(),
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
    weight_only = bool(payload.get("weight_only", False))
    if weight_only and payload.get("target_height_m") is not None:
        raise ValueError("weight_only cleanup cannot be combined with target_height_m normalization.")
    geometry_normalization = (
        normalize_geometry(float(payload["target_height_m"]))
        if payload.get("target_height_m") is not None
        else {"policy": "preserve_checkpoint_geometry"}
    )
    weights_before = weight_metrics()
    max_influences_per_vertex = int(payload.get("max_influences_per_vertex", 4))
    weights = sanitize_working_weights(
        preserve_skeleton_metadata=weight_only,
        max_influences_per_vertex=max_influences_per_vertex,
    )
    materials = (
        {
            "applied": False,
            "policy": "preserve_checkpoint_materials",
            "objects": [],
        }
        if weight_only
        else sanitize_working_materials()
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    save_blend(output)
    report = {
        "blend": str(blend.relative_to(job)).replace("\\", "/"),
        "checkpoint": str(output.relative_to(job)).replace("\\", "/"),
        "weight_only": weight_only,
        "max_influences_per_vertex": max_influences_per_vertex,
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
    if operation == "collapse_identity_leaf_joints":
        from identity_leaf_alias import collapse_identity_leaf_joints
        return collapse_identity_leaf_joints(req, globals())
    if operation in {"repair_explicit_mesh_winding_batch", "repair_explicit_skin_batch", "replace_explicit_corner_normals"}:
        import explicit_batch_repair
        return explicit_batch_repair.run_repair(req, sys.modules[__name__])
    if operation in {"repair_explicit_skin", "preview_explicit_skin_selection"}:
        import explicit_skin_repair
        return getattr(explicit_skin_repair, operation)(req, globals())
    if operation in {"edit_explicit_mesh_vertices", "bind_existing_pdx_material"}:
        import mesh_vertex_material_repair
        return getattr(mesh_vertex_material_repair, operation)(req, globals())
    if operation == "inspect_animation_source":
        from retarget_root_motion import inspect_animation_source
        return inspect_animation_source(req, globals())
    if operation == "rotate_existing_assembly_yaw":
        from assembly_yaw import rotate_existing_assembly_yaw
        return rotate_existing_assembly_yaw(req,globals())
    if operation == "repair_explicit_vertex_remap":
        from explicit_vertex_remap import repair_explicit_vertex_remap
        return repair_explicit_vertex_remap(req,globals())
    if operation == "repair_explicit_mesh_patch":
        from mesh_patch_repair import repair_explicit_mesh_patch
        return repair_explicit_mesh_patch(req, globals())
    if operation in {"inspect_mesh_winding", "repair_mesh_winding"}:
        import mesh_winding_repair
        return getattr(mesh_winding_repair, operation)(req, sys.modules[__name__])
    if operation in {"inspect_fitted_humanoid_source", "author_fitted_humanoid_rig", "author_fitted_humanoid_action"}:
        import fitted_humanoid_repair
        selected = {"inspect_fitted_humanoid_source": fitted_humanoid_repair.inspect_source, "author_fitted_humanoid_rig": fitted_humanoid_repair.author_rig, "author_fitted_humanoid_action": fitted_humanoid_repair.author_action}
        return selected[operation](req)
    if operation == "partition_skeletal_mesh_export_batches":
        from skeletal_export_partition import partition_skeletal_mesh_export_batches
        return partition_skeletal_mesh_export_batches(req, sys.modules[__name__])
    if operation in {"inspect_mesh_landmarks", "author_measured_creature_rig", "attach_rigid_component", "author_measured_creature_action", "repair_explicit_mesh_winding", "ground_existing_action"}:
        import manual_creature_rig
        return getattr(manual_creature_rig, operation)(req, globals())
    if operation == "isolate_humanoid_weapon":
        return isolate_humanoid_weapon(req)
    if operation == "attach_rigid_weapon_from_checkpoint":
        return attach_rigid_weapon_from_checkpoint(req)
    pdx = None
    if operation not in {"health", "inspect_scene", "review_humanoid_components", "save_checkpoint", "author_locator", "promote_accepted_reimport", "patch_existing_humanoid_action_phases", "sanitize_runtime_candidate", "retime_animation_action", "offset_action_root", "bake_static_mesh_transforms", "partition_static_mesh_export_batches", "prepare_export_coordinate_checkpoint"}:
        pdx = load_pdx(req["io_pdx_root"])
    if operation == "health":
        return health(req)
    if operation == "prepare_candidate":
        return prepare(req, pdx)
    if operation == "inspect_scene":
        return inspect(req)
    if operation == "review_humanoid_components":
        return review_humanoid_components(req)
    if operation == "author_locator":
        return author_locator(req)
    if operation == "promote_accepted_reimport":
        return promote_accepted_reimport(req)
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
    if operation == "import_bvh_animation_action":
        return import_bvh_animation_action(req)
    if operation == "retime_animation_action":
        return retime_animation_action(req)
    if operation == "prepare_export_coordinate_checkpoint":
        return prepare_export_coordinate_checkpoint(req)
    if operation == "author_humanoid_rig":
        return author_humanoid_rig(req)
    if operation == "author_humanoid_actions":
        return author_humanoid_actions(req)
    if operation == "patch_existing_humanoid_action_phases":
        return patch_existing_humanoid_action_phases(req)
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
