"""Blender-side test of `live_helpers.export_clip`: a 10-frame action exports 10 samples while the scene spans 85.

Run with a Blender that has io_pdx_mesh installed (not --factory-startup):
    blender --background --python-exit-code 1 --python .tools/3d_pipeline/tests/blender_export_clip_integration.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import bpy

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
OUT = tempfile.mkdtemp(prefix="export_clip_")
os.environ["HOI4_LIVE_SHOTS"] = OUT
sys.path.insert(0, str(PIPELINE_ROOT / "authoring"))

import live_helpers as h


def main() -> None:
    bpy.ops.wm.read_homefile(use_empty=True)
    data = bpy.data.armatures.new("rig")
    rig = bpy.data.objects.new("rig", data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    root = data.edit_bones.new("Root")
    root.head, root.tail = (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)
    arm = data.edit_bones.new("Arm")
    arm.head, arm.tail, arm.parent = (0.0, 0.0, 1.0), (0.5, 0.0, 1.0), root
    bpy.ops.object.mode_set(mode="OBJECT")
    h.new_action("wave", 10)
    for frame in (1, 10):
        rig.pose.bones["Arm"].rotation_mode = "QUATERNION"
        h.clear_pose()
        h.rot("Arm", (0.0, 0.0, 1.0), 30.0 if frame == 10 else 0.0)
        h.key(["Arm"], frame)
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, 85  # the range a previous clip left behind
    path = Path(OUT) / "u_wave.anim"
    try:
        samples = h.export_clip("wave", str(path))
    except RuntimeError as error:
        if "io_pdx_mesh is not installed" in str(error):
            print("io_pdx_mesh is not installed")
            raise SystemExit(0) from None
        raise
    assert samples == 10, samples
    assert (scene.frame_start, scene.frame_end) == (1, 85), "the scene's range is restored"
    print("EXPORT_CLIP_INTEGRATION_OK")


main()
