"""Drop or rigidly bind small loose parts of a rigged unit.

Meshy rigs a prop that hangs free of the body (a maul on a belt, a quiver) with the
weights of whatever limbs are nearest, so it smears when they move. A rule selects
the loose parts whose bounds lie inside a box, measured in fractions of the unit's
height (x and y from the body's centre, z from its lowest point), and either deletes
them or gives every vertex of the part to one bone. The largest part, the body, is
never touched. A rule that matches nothing is an error, so a wrong box cannot pass
silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import bmesh
import bpy

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
        if rule.get("action") not in {"drop", "bind"}:
            raise ValueError("Each loose part rule's action is drop or bind.")
        if rule["action"] == "bind" and not isinstance(rule.get("bone"), str):
            raise ValueError("A bind rule names its bone.")
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
                group = obj.vertex_groups.get(rule["bone"]) or obj.vertex_groups.new(name=rule["bone"])
                for other in obj.vertex_groups:
                    if other != group:
                        other.remove(part)
                group.add(part, 1.0, "REPLACE")
        if drop:
            bmesh.ops.delete(bm, geom=[bm.verts[index] for index in drop], context="VERTS")
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
        "policy": "the largest part is kept; a part fully inside a rule's box is dropped or bound to one bone",
    }
