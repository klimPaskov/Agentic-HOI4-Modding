"""Drop, rigidly bind or put in hand the small loose parts of a rigged unit.

Meshy rigs a prop that hangs free of the body (a maul on a belt, a quiver) with the
weights of whatever limbs are nearest, so it smears when they move. A rule selects
the loose parts whose bounds lie inside a box, measured in fractions of the unit's
height (x and y from the body's centre, z from its lowest point), and either deletes
them, gives every vertex of the part to one bone, or moves the part into a hand:
`hold` finds the part's long axis, takes the grip point `grip` of the way from its
butt end, turns the part so it points along `direction` (unit space, -Y forward, +Z
up) and puts the grip at the hand bone's palm in the rest pose, then binds it to that
bone. The largest part, the body, is never touched. A rule that matches nothing is an
error, so a wrong box cannot pass silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import bmesh
import bpy
from mathutils import Matrix, Vector

AXES = ("x", "y", "z")
MAX_EDITED_PARTS = 64


def _components(bm: bmesh.types.BMesh) -> List[List[int]]:
    seen = set()
    parts = []
    for start in bm.verts:
        if start.index in seen:
            continue
        stack, part = [start], []
        seen.add(start.index)
        while stack:
            vertex = stack.pop()
            part.append(vertex.index)
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other.index not in seen:
                    seen.add(other.index)
                    stack.append(other)
        parts.append(part)
    return parts


def _validate(rules: Any) -> List[Dict[str, Any]]:
    if not isinstance(rules, list) or not 1 <= len(rules) <= 8:
        raise ValueError("Loose part edits need 1 to 8 rules.")
    for rule in rules:
        if rule.get("action") not in {"drop", "bind", "hold"}:
            raise ValueError("Each loose part rule's action is drop, bind or hold.")
        if rule["action"] in {"bind", "hold"} and not isinstance(rule.get("bone"), str):
            raise ValueError("A bind or hold rule names its bone.")
        if rule["action"] == "hold":
            if not 0.0 <= float(rule.get("grip", 0.15)) <= 1.0 or rule.get("butt", "high") not in {"high", "low"}:
                raise ValueError("A hold rule's grip is a fraction from 0 to 1 and its butt end is high or low.")
            if len(rule.get("direction", [0.0, -1.0, 0.5])) != 3:
                raise ValueError("A hold rule's direction is three numbers.")
        box = rule.get("box", {})
        for axis in AXES:
            low, high = box.get(axis, [-10.0, 10.0])
            if not low < high:
                raise ValueError(f"Box {axis} range must be increasing.")
    return rules


def _inside(bounds: Dict[str, List[float]], box: Dict[str, List[float]]) -> bool:
    return all(
        box.get(axis, [-10.0, 10.0])[0] <= bounds[axis][0] and bounds[axis][1] <= box.get(axis, [-10.0, 10.0])[1]
        for axis in AXES
    )


def _palm(rig: bpy.types.Object, bone: str, palm: float) -> Vector:
    """The world position `palm` of the way along a bone in the rest pose."""

    data = rig.data.bones[bone]
    head, tail = rig.matrix_world @ data.head_local, rig.matrix_world @ data.tail_local
    return head + (tail - head) * palm


def _hold_part(obj: bpy.types.Object, bm: bmesh.types.BMesh, part: List[int], rule: Dict[str, Any], rig: bpy.types.Object) -> Dict[str, Any]:
    """Move one loose part into a hand: its long axis along `direction`, the grip at the palm."""

    import numpy as np

    world = obj.matrix_world
    points = np.array([list(world @ bm.verts[index].co) for index in part])
    centre = points.mean(axis=0)
    axis = np.linalg.svd(points - centre, full_matrices=False)[2][0]
    if (axis[2] < 0) == (rule.get("butt", "high") == "high"):
        axis = -axis  # axis now runs from the butt end toward the head
    along = (points - centre) @ axis
    butt = centre + axis * along.min()
    length = float(along.max() - along.min())
    grip = Vector(butt + axis * length * float(rule.get("grip", 0.15)))
    target = Vector(rule.get("direction", [0.0, -1.0, 0.5])).normalized()
    turn = Vector(axis).rotation_difference(target).to_matrix().to_4x4()
    hand = _palm(rig, rule["bone"], float(rule.get("palm", 0.6)))
    move = Matrix.Translation(hand) @ turn @ Matrix.Translation(-grip)
    local = world.inverted() @ move @ world
    for index in part:
        bm.verts[index].co = local @ bm.verts[index].co
    return {"length": length, "grip_world": list(hand), "direction": list(target)}


def edit_loose_parts(req: Dict[str, Any], h: Dict[str, Any]) -> Dict[str, Any]:
    job = Path(req["job_root"]).resolve()
    payload = req["payload"]
    blend = h["within"](job, payload["blend_rel"])
    checkpoint = h["within"](job, payload["checkpoint_rel"], allow_missing=True)
    rules = _validate(payload["rules"])
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    meshes = [obj for obj in h["mesh_objects"]() if any(mod.type == "ARMATURE" for mod in obj.modifiers)]
    if not meshes:
        raise RuntimeError("Loose part edits need a skinned mesh.")
    rigs = {mod.object for obj in meshes for mod in obj.modifiers if mod.type == "ARMATURE" and mod.object is not None}
    rig = next(iter(rigs)) if len(rigs) == 1 else None
    for rule in rules:
        if rule["action"] in {"bind", "hold"} and (rig is None or rule["bone"] not in rig.data.bones):
            raise RuntimeError(f"Bone {rule['bone']!r} is not in the unit's one armature.")
    corners = [obj.matrix_world @ vertex.co for obj in meshes for vertex in obj.data.vertices]
    low = [min(c[i] for c in corners) for i in range(3)]
    high = [max(c[i] for c in corners) for i in range(3)]
    height = high[2] - low[2]
    origin = [(low[0] + high[0]) / 2, (low[1] + high[1]) / 2, low[2]]
    matched = [0] * len(rules)
    edited: List[Dict[str, Any]] = []
    for obj in meshes:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        parts = sorted(_components(bm), key=len, reverse=True)
        drop: List[int] = []
        for part in parts[1:]:
            points = [obj.matrix_world @ bm.verts[index].co for index in part]
            bounds = {
                axis: [min(p[i] - origin[i] for p in points) / height, max(p[i] - origin[i] for p in points) / height]
                for i, axis in enumerate(AXES)
            }
            rule_index = next((i for i, rule in enumerate(rules) if _inside(bounds, rule.get("box", {}))), None)
            if rule_index is None:
                continue
            matched[rule_index] += 1
            rule = rules[rule_index]
            edited.append({"object": obj.name, "vertices": len(part), "bounds": bounds, "action": rule["action"], "bone": rule.get("bone")})
            if rule["action"] == "drop":
                drop.extend(part)
            else:
                if rule["action"] == "hold":
                    edited[-1]["hold"] = _hold_part(obj, bm, part, rule, rig)
                # Weights go through the bmesh deform layer, so the one write below keeps them with the geometry.
                group = obj.vertex_groups.get(rule["bone"]) or obj.vertex_groups.new(name=rule["bone"])
                deform = bm.verts.layers.deform.verify()
                for index in part:
                    weights = bm.verts[index][deform]
                    weights.clear()
                    weights[group.index] = 1.0
        if drop:
            bmesh.ops.delete(bm, geom=[bm.verts[index] for index in drop], context="VERTS")
        if any(item["object"] == obj.name for item in edited):
            bm.to_mesh(obj.data)
            obj.data.update()
        bm.free()
    if len(edited) > MAX_EDITED_PARTS:
        raise RuntimeError(f"Loose part edits matched {len(edited)} parts; at most {MAX_EDITED_PARTS}. Narrow the boxes.")
    unmatched = [index for index, count in enumerate(matched) if count == 0]
    if unmatched:
        raise RuntimeError(f"Loose part rules {unmatched} matched no part; measure the part and correct the box.")
    h["save_blend"](checkpoint)
    return {
        "status": "pass",
        "operation": "edit_loose_parts",
        "checkpoint": str(checkpoint.relative_to(job)).replace("\\", "/"),
        "unit_height": height,
        "edited_parts": edited,
        "geometry": h["geometry_metrics"](),
        "policy": "the largest part is kept; a part fully inside a rule's box is dropped, bound to one bone, or put in a hand and bound to it",
    }
