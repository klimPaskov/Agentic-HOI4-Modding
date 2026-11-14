"""Render evenly spaced frames of one clip from a fixed side camera (Blender script).

    blender -b <file.blend|file.glb> --python clip_frames.py -- --out DIR --count 6 [--action NAME] [--view side|front|back]

The camera frames the whole clip (the union of the body's extent over all rendered frames) and is the same in every
frame, so a floating or sinking body shows. A ground line at z=0 is drawn. Writes `frame_<n>.png` and `frames.json`
(the frame numbers and, per frame, the lowest and highest point of the mesh).
"""

import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--count", type=int, default=6)
parser.add_argument("--action", default="")
parser.add_argument("--view", default="side")
parser.add_argument("--size", type=int, default=520)
args = parser.parse_args(argv)
args.out.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
arm = max(armatures, key=lambda o: len(o.data.bones))
meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() is not None and len(o.vertex_groups)]
actions = list(bpy.data.actions)
action = next((a for a in actions if args.action and a.name.startswith(args.action)), None) or actions[0]
arm.animation_data_create()
arm.animation_data.action = action
slots = getattr(action, "slots", None)
if slots is not None and len(slots):
    arm.animation_data.action_slot = slots[0]
f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
frames = [int(round(f0 + (f1 - f0) * i / (args.count - 1))) for i in range(args.count)]

scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "TEXTURE"
scene.view_settings.view_transform = "Standard"
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.55, 0.55, 0.6)
for o in meshes:
    o.hide_render = False


def bounds():
    graph = bpy.context.evaluated_depsgraph_get()
    points = []
    for o in meshes:
        ev = o.evaluated_get(graph)
        mesh = ev.to_mesh()
        data = np.empty(len(mesh.vertices) * 3)
        mesh.vertices.foreach_get("co", data)
        pts = data.reshape(-1, 3)
        m = np.array(o.matrix_world)
        points.append(pts @ m[:3, :3].T + m[:3, 3])
        ev.to_mesh_clear()
    return np.concatenate(points)


info = []
lo, hi = np.array([1e9] * 3), np.array([-1e9] * 3)
for frame in frames:
    scene.frame_set(frame)
    pts = bounds()
    lo, hi = np.minimum(lo, pts.min(axis=0)), np.maximum(hi, pts.max(axis=0))
    info.append({"frame": frame, "lowest_z": round(float(pts[:, 2].min()), 4), "highest_z": round(float(pts[:, 2].max()), 4),
                 "y_range": [round(float(pts[:, 1].min()), 3), round(float(pts[:, 1].max()), 3)],
                 "x_range": [round(float(pts[:, 0].min()), 3), round(float(pts[:, 0].max()), 3)]})
direction = {"side": Vector((-1, 0, 0)), "front": Vector((0, -1, 0)), "back": Vector((0, 1, 0))}[args.view]
horizontal = 1 if args.view == "side" else 0
centre = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
span = max(hi[horizontal] - lo[horizontal], hi[2] - lo[2], 0.5) * 1.12
camera_data = bpy.data.cameras.new("cam")
camera_data.type = "ORTHO"
camera_data.ortho_scale = span
camera = bpy.data.objects.new("cam", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera.location = centre + direction * 6
camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
scene.render.resolution_x = scene.render.resolution_y = args.size
# ground line: a thin dark slab at z = 0
bpy.ops.mesh.primitive_cube_add(size=1, location=(centre.x, centre.y, -0.004))
slab = bpy.context.active_object
slab.scale = (3.0, 3.0, 0.008)
for frame in frames:
    scene.frame_set(frame)
    scene.render.filepath = str(args.out / f"frame_{frame:03d}.png")
    bpy.ops.render.render(write_still=True)
(args.out / "frames.json").write_text(json.dumps({"action": action.name, "frames": info}, indent=1))
print("FRAMES_DONE")
