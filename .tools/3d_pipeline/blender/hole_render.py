"""Blender side of `check_holes.py`: find where a unit shows holes the way the game draws it. Do not run directly.

blender -b --python hole_render.py -- <request.json>

The game culls back faces. Each view is rendered twice with a transparent background, once with
back faces culled and once without, and the pixels that only back faces cover are a hole as the
player sees it: a missing face, a face turned the wrong way, or a one-sided sheet seen from behind.
The pixels are split into connected clusters, and the largest cluster per view and frame is
reported in pixels at the request's tile size. The camera frames the rest pose the same way for every
unit (orthographic, 1.45 times the largest extent), so clusters compare across units of any size.

The request names a `.mesh` with `.anim` clips and the frames to render, or a `.glb` (rest pose only).
The `overlays` worst views are rendered again as tiles (`worst_<n>.png`): the unit grey, the holes
red, the background white.
"""

import json
import math
import sys
from pathlib import Path

import addon_utils
import bpy
import numpy as np
from mathutils import Vector

request = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
out = Path(request["out"])
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_homefile(use_empty=True)
scene = bpy.context.scene
source = Path(request["source"])
if source.suffix.lower() == ".glb":
    bpy.ops.import_scene.gltf(filepath=str(source))
else:
    for module in addon_utils.modules():
        if module.__name__.endswith("io_pdx_mesh"):
            addon_utils.enable(module.__name__, default_set=False)
            break
    else:
        raise SystemExit("io_pdx_mesh is not installed for this Blender; run bootstrap_3d_workflow.py")
    bpy.ops.io_pdx_mesh.import_mesh(filepath=str(source), chk_locs=True)
rig = next((o for o in scene.objects if o.type == "ARMATURE"), None)
meshes = [o for o in scene.objects if o.type == "MESH" and "collision" not in o.name.lower()]
for o in scene.objects:
    if o.type == "MESH" and o not in meshes:
        o.hide_render = True

size = int(request["size"])
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = scene.render.resolution_y = size
scene.render.film_transparent = True
scene.display.render_aa = "OFF"
shading = scene.display.shading
shading.light = "FLAT"
shading.color_type = "SINGLE"
shading.show_cavity = False
shading.show_shadows = False


def bounds():
    graph = bpy.context.evaluated_depsgraph_get()
    points = []
    for o in meshes:
        evaluated = o.evaluated_get(graph)
        data = evaluated.to_mesh()
        points.extend(evaluated.matrix_world @ v.co for v in data.vertices)
        evaluated.to_mesh_clear()
    low = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    high = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return low, high


low, high = bounds()
span = max(high.x - low.x, high.y - low.y, high.z - low.z, 1e-3)
camera_data = bpy.data.cameras.new("holes")
camera_data.type = "ORTHO"
camera = bpy.data.objects.new("holes", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
VIEWS = [tuple(view) for view in request["views"]]


def aim(azimuth, elevation):
    a, e = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    camera.location = (low + high) / 2 + direction * span * 6
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera_data.ortho_scale = span * 1.45
    camera_data.clip_end = span * 20


def coverage(cull):
    shading.show_backface_culling = cull
    path = out / "_tile.png"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    alpha = np.array(image.pixels[:], dtype=np.float32).reshape(size, size, 4)[..., 3] > 0.5
    bpy.data.images.remove(image)
    return alpha


def largest_cluster(mask):
    """Pixels in the largest 8-connected cluster of the mask."""

    seen = np.zeros_like(mask)
    best = 0
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        stack, count = [(y, x)], 0
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            count += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < size and 0 <= nx < size and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        best = max(best, count)
    return best


results = []


def measure(clip, frames):
    for frame in frames:
        scene.frame_set(frame)
        for azimuth, elevation in VIEWS:
            aim(azimuth, elevation)
            only_back = coverage(False) & ~coverage(True)
            results.append({"clip": clip, "frame": frame, "view": [azimuth, elevation],
                            "largest": largest_cluster(only_back), "pixels": int(only_back.sum())})


actions = {}


def pose(clip, frame):
    """Put the unit in the clip's frame, or in its rest pose for "rest"."""

    if rig is None:
        return
    rig.animation_data.action = actions.get(clip)
    if clip not in actions:
        for bone in rig.pose.bones:
            bone.matrix_basis.identity()
    scene.frame_set(frame)


def overlay(row, index):
    pose(row["clip"], row["scene_frame"])
    aim(*row["view"])
    shown, front = coverage(False), coverage(True)
    holes = shown & ~front
    pixels = np.ones((size, size, 4), dtype=np.float32)
    pixels[shown] = (0.55, 0.55, 0.55, 1.0)
    pixels[holes] = (0.9, 0.05, 0.05, 1.0)
    image = bpy.data.images.new(f"worst_{index}", size, size, alpha=True)
    image.pixels[:] = pixels.ravel()
    image.filepath_raw = str(out / f"worst_{index}.png")
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)
    row["tile"] = f"worst_{index}.png"


if rig is not None:
    rig.animation_data_create()
rest_frame = scene.frame_current
measure("rest", [rest_frame])
for row in results:
    row["scene_frame"] = rest_frame
for clip in request.get("clips", []):
    if rig is None:
        break
    action = bpy.data.actions.new(clip["name"])
    rig.animation_data.action = action
    bpy.ops.io_pdx_mesh.import_anim(filepath=clip["path"], int_start=1)
    actions[clip["name"]] = rig.animation_data.action
    start = len(results)
    measure(clip["name"], [frame + 1 for frame in clip["frames"]])
    for row in results[start:]:
        row["scene_frame"] = row["frame"]
        row["frame"] -= 1
worst_rows = [row for row in sorted(results, key=lambda r: -r["largest"]) if row["largest"] > 0][: int(request.get("overlays", 0))]
for index, row in enumerate(worst_rows):
    overlay(row, index)
for row in results:
    row.pop("scene_frame", None)

(out / "holes.json").write_text(json.dumps({"source": str(source), "size": size, "results": results}, indent=1), encoding="utf-8")
print("HOLES_RENDERED", len(results))
