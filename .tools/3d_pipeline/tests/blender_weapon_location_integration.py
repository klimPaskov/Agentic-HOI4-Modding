"""Blender-side regression test: a weapon bone's location keys survive the retarget's conversion and the .anim export.

Run it in Blender, as the other blender_*_integration.py scripts:

    blender -b --factory-startup --python .tools/3d_pipeline/tests/blender_weapon_location_integration.py

The retarget used to set the location of every bone but the root to zero, so a weapon let go of in a clip could not leave the hand's frame
(the weapon bone could only turn). A job now names the weapon bone and the retarget keeps its location, converted like the root's motion.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT / "adapter"))
sys.path.insert(0, str(PIPELINE_ROOT))

import blender_worker
from lib import pdx_deform


def make_rig(name: str, scale: float, roll: float = 0.0):
    """Root -> RightHand -> Weapon, in an armature object of the given scale; the weapon bone's rest axes are turned by `roll` about its length."""

    data = bpy.data.armatures.new(name + "Data")
    rig = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    root = data.edit_bones.new("Hips")
    root.head, root.tail = (0.0, 0.0, 0.5), (0.0, 0.0, 0.8)
    hand = data.edit_bones.new("RightHand")
    hand.head, hand.tail, hand.parent = (0.3, 0.0, 0.8), (0.5, 0.0, 0.8), root
    weapon = data.edit_bones.new("Weapon")
    weapon.head, weapon.tail, weapon.parent, weapon.roll = (0.4, 0.0, 0.8), (0.4, 0.0, 1.0), hand, roll
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    return rig


def check_conversion() -> None:
    """The conversion keeps a displacement: the weapon bone moves the same way in the world through the source rig and the scaled target."""

    source = make_rig("Source", 1.0)
    target = make_rig("Target", 7.35, roll=1.1)
    location = Vector((0.12, -0.3, 0.45))
    converted = blender_worker.retarget_bone_location(location, source, source.data.bones["Weapon"], target, target.data.bones["Weapon"], 7.35)
    world_source = source.matrix_world.to_3x3() @ source.data.bones["Weapon"].matrix_local.to_3x3() @ location
    world_target = target.matrix_world.to_3x3() @ target.data.bones["Weapon"].matrix_local.to_3x3() @ converted
    assert (world_target - world_source * 7.35).length < 1e-5, (world_target, world_source)
    same = blender_worker.retarget_bone_location(location, source, source.data.bones["Weapon"], source, source.data.bones["Weapon"], 1.0)
    assert (same - location).length < 1e-6, same


def check_bone_selection() -> None:
    rig = make_rig("Selection", 1.0)
    chains = {"Hips": ["Hips"], "RightHand": ["RightHand"], "Weapon": ["Weapon"]}
    assert blender_worker.retarget_location_bones(None, chains, rig, "Hips") == set()
    assert blender_worker.retarget_location_bones(["Weapon"], chains, rig, "Hips") == {"Weapon"}
    for bad in (["Hips"], ["Sword"], "Weapon"):
        try:
            blender_worker.retarget_location_bones(bad, chains, rig, "Hips")
        except ValueError:
            continue
        raise AssertionError(f"{bad!r} should have been refused")


def check_anim_keeps_the_weapon_location() -> None:
    """Key the weapon bone's location, export an .anim with the addon's own exporter and read it back: the weapon's translation varies."""

    config = json.loads((PIPELINE_ROOT / "config" / "blender_hoi4_adapter.json").read_text(encoding="utf-8"))
    pdx = blender_worker.load_pdx(config["io_pdx_mesh_root"])
    rig = make_rig("Export", 1.0)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    for frame, offset in ((1, (0.0, 0.0, 0.0)), (3, (0.2, 0.1, -0.3)), (5, (0.4, 0.3, -0.6))):
        weapon = rig.pose.bones["Weapon"]
        weapon.location = offset
        weapon.keyframe_insert(data_path="location", frame=frame, group="Weapon")
        hand = rig.pose.bones["RightHand"]
        hand.rotation_mode = "XYZ"
        hand.rotation_euler.z = 0.1 * frame
        hand.keyframe_insert(data_path="rotation_euler", frame=frame, group="RightHand")
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, 5
    with tempfile.TemporaryDirectory(prefix="hoi4_weapon_location_") as temporary:
        output = Path(temporary) / "weapon_location.anim"
        blender_worker.run_captured(pdx, "export_animfile", str(output), frame_start=1, frame_end=5, uniform_scale=True, plain_txt=True)
        anim = pdx_deform.load_anim(output)
    moved = anim.channels["Weapon"]["t"].max(axis=0) - anim.channels["Weapon"]["t"].min(axis=0)
    assert float(moved.max()) > 0.3, moved
    still = anim.channels["Hips"]["t"].max(axis=0) - anim.channels["Hips"]["t"].min(axis=0)
    assert float(still.max()) < 1e-6, still


def main() -> None:
    blender_worker.clear_scene()
    check_conversion()
    check_bone_selection()
    check_anim_keeps_the_weapon_location()
    print("WEAPON_LOCATION_OK")


main()
