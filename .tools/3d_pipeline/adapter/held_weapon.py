"""Put a weapon from a Meshy prop sheet into a unit's hand.

A sheet is one Meshy model of a culture's weapons standing side by side. Its loose parts
are grouped into weapons by their left-to-right extent, so a guard or a pommel that is
its own island stays with its blade. The chosen weapon is scaled to `length` of the
unit's height, reduced to `max_triangles`, placed in the hand by the same rule as a held
loose part (`loose_parts._hold_part`: long axis along `direction`, the grip `grip` of the
way from the butt end at the hand bone's palm, in the rest pose) and bound fully to that
bone. It stays its own object, `<stem>_weapon`, with the sheet's material, so it exports
as a second shape with its own textures.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import bmesh
import bpy

from loose_parts import _components, _hold_part


def _weapon_groups(bm: bmesh.types.BMesh) -> List[List[int]]:
    """Loose parts merged into weapons wherever their x extents overlap, ordered left to right."""

    spans = []
    for part in _components(bm):
        xs = [bm.verts[index].co.x for index in part]
        spans.append([min(xs), max(xs), list(part)])
    spans.sort(key=lambda item: item[0])
    groups: List[List[Any]] = []
    for low, high, part in spans:
        if groups and low <= groups[-1][1]:
            groups[-1][1] = max(groups[-1][1], high)
            groups[-1][2].extend(part)
        else:
            groups.append([low, high, part])
    return [group[2] for group in groups]


def attach_held_weapon(req: Dict[str, Any], h: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    p = req["payload"]
    blend = h["within"](job, p["blend_rel"])
    sheet = h["within"](job, p["sheet_rel"])
    checkpoint = h["within"](job, p["checkpoint_rel"], allow_missing=True)
    stem = h["safe_name"](str(p["stem"]))
    index = int(p["weapon_index"])
    rule = {
        "bone": str(p.get("bone", "RightHand")),
        "grip": float(p.get("grip", 0.15)),
        "butt": str(p.get("butt", "low")),
        "direction": list(p.get("direction", [0.0, -1.0, 0.5])),
        "palm": float(p.get("palm", 0.6)),
    }
    length_fraction = float(p["length"])
    max_triangles = int(p.get("max_triangles", 2000))
    if not 0.05 <= length_fraction <= 2.5 or not 100 <= max_triangles <= 20000:
        raise ValueError("A held weapon's length is 0.05 to 2.5 of the unit's height and its budget 100 to 20000 triangles.")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    meshes = [obj for obj in h["mesh_objects"]() if any(mod.type == "ARMATURE" for mod in obj.modifiers)]
    rigs = {mod.object for obj in meshes for mod in obj.modifiers if mod.type == "ARMATURE" and mod.object is not None}
    if len(rigs) != 1:
        raise RuntimeError(f"A held weapon needs the unit's one skinned armature, found {len(rigs)}.")
    rig = next(iter(rigs))
    if rule["bone"] not in rig.data.bones:
        raise RuntimeError(f"Bone {rule['bone']!r} is not in the unit's armature.")
    if bpy.data.objects.get(f"{stem}_weapon"):
        raise RuntimeError(f"The unit already holds {stem}_weapon.")
    zs = [(obj.matrix_world @ v.co).z for obj in meshes for v in obj.data.vertices]
    height = max(zs) - min(zs)

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(sheet))
    imported = [obj for obj in bpy.data.objects if obj not in before]
    parts = [obj for obj in imported if obj.type == "MESH"]
    if not parts:
        raise RuntimeError("The prop sheet holds no mesh.")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    weapon = bpy.context.view_layer.objects.active
    weapon.parent = None
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for obj in imported:
        if obj != weapon and obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

    bm = bmesh.new()
    bm.from_mesh(weapon.data)
    bm.verts.ensure_lookup_table()
    groups = _weapon_groups(bm)
    if not 0 <= index < len(groups):
        raise RuntimeError(f"The sheet holds {len(groups)} weapons; weapon_index {index} is not one of them.")
    keep = set(groups[index])
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index not in keep], context="VERTS")
    bm.verts.ensure_lookup_table()
    span = max(v.co.z for v in bm.verts) - min(v.co.z for v in bm.verts)
    for v in bm.verts:
        v.co *= length_fraction * height / max(span, 1e-6)
    hold = _hold_part(weapon, bm, [v.index for v in bm.verts], rule, rig)
    bm.to_mesh(weapon.data)
    bm.free()
    weapon.data.update()

    triangles = sum(len(poly.vertices) - 2 for poly in weapon.data.polygons)
    if triangles > max_triangles:
        decimate = weapon.modifiers.new("HOI4_WEAPON_BUDGET", "DECIMATE")
        decimate.ratio = max_triangles / triangles
        bpy.context.view_layer.objects.active = weapon
        bpy.ops.object.modifier_apply(modifier=decimate.name)
    weapon.name = weapon.data.name = f"{stem}_weapon"
    for material in weapon.data.materials:
        if material is not None:
            material.name = f"{stem}_weapon"
    group = weapon.vertex_groups.new(name=rule["bone"])
    group.add(list(range(len(weapon.data.vertices))), 1.0, "REPLACE")
    armature = weapon.modifiers.new("Armature", "ARMATURE")
    armature.object = rig
    weapon["hoi4_working"] = True
    weapon["hoi4_held_weapon"] = True
    h["save_blend"](checkpoint)
    return {
        "status": "pass",
        "operation": "attach_held_weapon",
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "weapon": weapon.name,
        "weapons_on_sheet": len(groups),
        "weapon_index": index,
        "unit_height": height,
        "length": length_fraction * height,
        "triangles": sum(len(poly.vertices) - 2 for poly in weapon.data.polygons),
        "hold": hold,
        "bone": rule["bone"],
        "policy": "one weapon from the sheet, scaled to the unit, gripped at the palm in the rest pose, bound to the hand bone",
    }
