"""Render close-ups of the gripping hand from five sides (Blender script), for the grip stage's review sheet.

    blender -b --factory-startup --python hand_views.py -- <gripped.glb> --out DIR [--poses rest,idle] [--hand RightHand]

For every pose (`rest` is the bind pose, anything else a clip name or the start of one, shown on its first frame)
it renders five views of the hand, each from a direction fixed by the hand's own frame at that pose: the back of
the hand, the palm side, the thumb side, the little-finger side and a three-quarter view from the palm and thumb
sides. Files: `<pose>_<view>.png`. `tripo/hand_sheet.py` joins them into one sheet. The camera has the fingers up.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

PREFIX = "mixamorig:"
VIEWS = ("back_of_hand", "palm_side", "thumb_side", "little_finger_side", "three_quarter")


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def head(arm, name):
    return np.array(arm.matrix_world @ arm.pose.bones[name].head)


def main():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("glb", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--poses", default="rest,idle")
    parser.add_argument("--hand", default="RightHand")
    parser.add_argument("--size", type=int, default=520)
    parser.add_argument("--scale", type=float, default=0.2)
    parser.add_argument("--studio", action="store_true", help="Workbench studio light instead of the default EEVEE render")
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(args.glb))
    arm = max((o for o in bpy.data.objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))
    for o in list(bpy.data.objects):
        if o.type == "MESH" and len(o.vertex_groups) == 0:
            bpy.data.objects.remove(o, do_unlink=True)
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    if args.studio:
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "TEXTURE"
        scene.world = bpy.data.worlds.new("w")
        scene.world.color = (0.5, 0.5, 0.55)
    else:
        # The review default: EEVEE with the materials the GLB carries (Tripo's own metal and roughness maps) under a grey world and one sun.
        scene.render.engine = "BLENDER_EEVEE"
        world = bpy.data.worlds.new("w")
        world.use_nodes = True
        background = world.node_tree.nodes["Background"]
        background.inputs["Color"].default_value = (0.55, 0.55, 0.57, 1.0)
        background.inputs["Strength"].default_value = 1.0
        scene.world = world
        sun_data = bpy.data.lights.new("sun", "SUN")
        sun_data.energy = 3.0
        sun = bpy.data.objects.new("sun", sun_data)
        sun.rotation_euler = (math.radians(55), 0.0, math.radians(-25))
        scene.collection.objects.link(sun)
    camera_data = bpy.data.cameras.new("c")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = args.scale
    camera = bpy.data.objects.new("c", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    scene.render.resolution_x = scene.render.resolution_y = args.size

    def names(finger):
        return [f"{PREFIX}{args.hand}{finger}{i}" for i in (1, 2, 3, 4)]

    # the sign of the palm normal: at the bind pose the thumb base lies on the palm side of the metacarpals
    def frame():
        wrist = head(arm, PREFIX + args.hand)
        index, middle, pinky, thumb = (head(arm, names(f)[0]) for f in ("Index", "Middle", "Pinky", "Thumb"))
        closing = unit(pinky - index)
        forward = unit(middle - wrist)
        normal = unit(np.cross(closing, forward))
        return wrist, closing, forward, normal, thumb, index, pinky

    arm.animation_data_create()
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    wrist, closing, forward, normal, thumb, index, pinky = frame()
    palm_centre = 0.5 * (wrist + 0.5 * (index + pinky))
    sign = 1.0 if float((thumb - palm_centre) @ normal) >= 0 else -1.0  # same rule as grip_weapon.py
    sign_reference = sign

    for pose in [p for p in args.poses.split(",") if p]:
        if pose == "rest":
            arm.animation_data.action = None
            for pb in arm.pose.bones:
                pb.rotation_quaternion = (1, 0, 0, 0)
                pb.location = (0, 0, 0)
            scene.frame_set(1)
        else:
            action = next(a for a in bpy.data.actions if a.name.startswith(pose))
            arm.animation_data.action = action
            slots = getattr(action, "slots", None)
            if slots is not None and len(slots):
                arm.animation_data.action_slot = slots[0]
            scene.frame_set(int(action.frame_range[0]))
        bpy.context.view_layer.update()
        wrist, closing, forward, normal, thumb, index, pinky = frame()
        normal = normal * sign_reference
        centre = 0.5 * (wrist + 0.5 * (index + pinky))
        toward_thumb = unit(index - pinky)
        directions = {
            "back_of_hand": -normal,
            "palm_side": normal,
            "thumb_side": toward_thumb,
            "little_finger_side": -toward_thumb,
            "three_quarter": unit(0.6 * normal + 0.6 * toward_thumb + 0.35 * forward),
        }
        tag = pose[:12].replace(" ", "_")
        for view, direction in directions.items():
            d = Vector(direction)
            camera.location = Vector(centre) + d * 3.0
            up = np.array(forward) - float(forward @ direction) * direction
            if np.linalg.norm(up) < 0.2:
                up = np.array([0.0, 0.0, 1.0])
            y_axis = Vector(unit(up))
            x_axis = y_axis.cross(d).normalized()
            y_axis = d.cross(x_axis).normalized()
            from mathutils import Matrix

            camera.matrix_world = Matrix(((x_axis.x, y_axis.x, d.x, camera.location.x), (x_axis.y, y_axis.y, d.y, camera.location.y),
                                          (x_axis.z, y_axis.z, d.z, camera.location.z), (0, 0, 0, 1)))
            scene.render.filepath = str(args.out / f"{tag}_{view}.png")
            bpy.ops.render.render(write_still=True)
    print("HAND_VIEWS_DONE")


if __name__ == "__main__":
    main()
