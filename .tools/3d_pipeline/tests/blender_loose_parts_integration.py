"""Blender-side test of loose part edits on a procedural rigged body with a prop between its feet.

Run with the lock-selected Blender:
    blender --background --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_loose_parts_integration.py
It writes only temporary .blend files and fails on the first unmet expectation.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT / "adapter"))

import blender_worker
import manual_creature_rig

BODY_VERTICES = 8


def make_unit(path: Path) -> None:
    """A 2 m box body and a small box prop standing between its feet, weighted to both feet."""

    blender_worker.clear_scene()
    working = bpy.data.collections.new("WORKING")
    bpy.context.scene.collection.children.link(working)
    rig_data = bpy.data.armatures.new("test_rig")
    rig = bpy.data.objects.new("test_rig", rig_data)
    working.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name, head, tail in (("Hips", (0, 0, 1.0), (0, 0, 1.2)), ("LeftFoot", (0.2, 0, 0.1), (0.2, -0.1, 0.0)), ("RightFoot", (-0.2, 0, 0.1), (-0.2, -0.1, 0.0)), ("RightHand", (-0.5, 0, 1.1), (-0.6, 0, 0.9))):
        bone = rig_data.edit_bones.new(name)
        bone.head, bone.tail = head, tail
    bpy.ops.object.mode_set(mode="OBJECT")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 1.0)) @ Matrix.Diagonal((0.6, 0.3, 2.0, 1.0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, -0.2, 0.25)) @ Matrix.Diagonal((0.08, 0.08, 0.5, 1.0)))
    mesh = bpy.data.meshes.new("test_unit")
    bm.to_mesh(mesh)
    bm.free()
    unit = bpy.data.objects.new("test_unit", mesh)
    working.objects.link(unit)
    unit["hoi4_working"] = True
    unit.modifiers.new("Armature", "ARMATURE").object = rig
    hips, left, right = (unit.vertex_groups.new(name=name) for name in ("Hips", "LeftFoot", "RightFoot"))
    hips.add(list(range(BODY_VERTICES)), 1.0, "REPLACE")
    prop = list(range(BODY_VERTICES, len(mesh.vertices)))
    left.add(prop, 0.5, "REPLACE")
    right.add(prop, 0.5, "REPLACE")
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(job: Path, checkpoint: str, rules: list) -> dict:
    return manual_creature_rig.edit_loose_parts(
        {"job_root": str(job), "payload": {"blend_rel": "unit.blend", "checkpoint_rel": checkpoint, "rules": rules}},
        vars(blender_worker),
    )


def main() -> None:
    between_feet = {"x": [-0.1, 0.1], "z": [-0.01, 0.3]}
    with tempfile.TemporaryDirectory(prefix="hoi4_loose_parts_test_") as temporary:
        job = Path(temporary)
        make_unit(job / "unit.blend")
        bound = run(job, "bound.blend", [{"action": "bind", "bone": "Hips", "box": between_feet}])
        expect(len(bound["edited_parts"]) == 1 and bound["edited_parts"][0]["vertices"] == 8, f"one prop expected: {bound['edited_parts']}")
        bpy.ops.wm.open_mainfile(filepath=str(job / "bound.blend"))
        unit = bpy.data.objects["test_unit"]
        names = {group.index: group.name for group in unit.vertex_groups}
        for vertex in unit.data.vertices[BODY_VERTICES:]:
            weights = {names[item.group]: item.weight for item in vertex.groups if item.weight > 0}
            expect(weights == {"Hips": 1.0}, f"prop vertex {vertex.index} weights {weights}")
        expect(len(unit.data.vertices) == 16, "binding keeps every vertex")
        dropped = run(job, "dropped.blend", [{"action": "drop", "box": between_feet}])
        expect(dropped["edited_parts"][0]["action"] == "drop", "the prop must be dropped")
        bpy.ops.wm.open_mainfile(filepath=str(job / "dropped.blend"))
        expect(len(bpy.data.objects["test_unit"].data.vertices) == BODY_VERTICES, "only the body remains")
        held = run(job, "held.blend", [{"action": "hold", "bone": "RightHand", "box": between_feet, "grip": 0.1, "butt": "high", "direction": [0, -1, 0]}])
        hold = held["edited_parts"][0]["hold"]
        expect(abs(hold["length"] - 0.5) < 0.02, f"the prop's long axis is 0.5 long, measured {hold['length']}")
        bpy.ops.wm.open_mainfile(filepath=str(job / "held.blend"))
        unit = bpy.data.objects["test_unit"]
        names = {group.index: group.name for group in unit.vertex_groups}
        prop = [unit.matrix_world @ unit.data.vertices[i].co for i in range(BODY_VERTICES, 16)]
        ys = [p.y for p in prop]
        expect(max(ys) - min(ys) > 0.45, "the prop now lies along -Y")
        palm = Vector((-0.56, 0.0, 0.98))
        expect(min((p - palm).length for p in prop) < 0.1, "the grip end sits at the palm")
        expect(max(ys) < 0.1 and min(ys) < -0.35, "the head points forward (-Y) from the grip")
        for vertex in unit.data.vertices[BODY_VERTICES:]:
            weights = {names[item.group]: item.weight for item in vertex.groups if item.weight > 0}
            expect(weights == {"RightHand": 1.0}, f"held vertex {vertex.index} weights {weights}")
        try:
            run(job, "missed.blend", [{"action": "drop", "box": {"x": [0.4, 0.5]}}])
        except RuntimeError as error:
            expect("matched no part" in str(error), str(error))
        else:
            raise AssertionError("a rule that matches nothing must fail")
    print("loose parts integration: pass")


main()
