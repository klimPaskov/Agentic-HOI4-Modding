"""Blender side of `review_unit.py`: render review tiles of an exported unit. Do not run directly.

blender -b --python review_render.py -- <request.json>

The request names the `.mesh`, the diffuse map of each mesh shape, the `.anim` files with the
frames to render, the views and the tile size. Every tile is written as
`<clip>_<frame>_<view>.png` next to an `index.json` that lists them.

The renders show what the game shows and nothing kinder:
- back faces are culled, as `PdxMeshAdvanced` does, and the world is flat magenta, so a hole,
  a one-sided face seen from behind or an inside-out part shows magenta;
- a dark disc at the rest pose's ground shows floating and sinking;
- the camera frames the rest pose, so a unit that drifts away from its spot leaves the frame.
"""

import json
import math
import sys
from pathlib import Path

import addon_utils
import bpy
from mathutils import Vector

request = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text(encoding="utf-8"))
out = Path(request["out"])
out.mkdir(parents=True, exist_ok=True)

for module in addon_utils.modules():
    if module.__name__.endswith("io_pdx_mesh"):
        addon_utils.enable(module.__name__, default_set=False)
        break
else:
    raise SystemExit("io_pdx_mesh is not installed for this Blender; run bootstrap_3d_workflow.py")

bpy.ops.wm.read_homefile(use_empty=True)
scene = bpy.context.scene
bpy.ops.io_pdx_mesh.import_mesh(filepath=request["mesh"], chk_locs=True)
rig = next((o for o in scene.objects if o.type == "ARMATURE"), None)
meshes = [o for o in scene.objects if o.type == "MESH" and "collision" not in o.name.lower()]
for o in scene.objects:
    if o.type == "MESH" and o not in meshes:
        o.hide_render = True

# A `.mesh` usually names no texture: the `.gfx` meshsettings do. Give each shape its diffuse map
# as the active image node, which Workbench's texture colour mode draws.
images = {}
for o in meshes:
    # Imported objects are named after their shape, with a ".001"-style or "-001" suffix when repeated.
    shapes = [shape for shape in request["diffuse"] if shape != "*" and o.name.startswith(shape)]
    path = request["diffuse"][max(shapes, key=len)] if shapes else request["diffuse"].get("*")
    if not path:
        continue
    if path not in images:
        images[path] = bpy.data.images.load(path)
        images[path].alpha_mode = "NONE"
    for slot in o.material_slots:
        if slot.material is None:
            continue
        slot.material.use_nodes = True
        node = slot.material.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = images[path]
        slot.material.node_tree.nodes.active = node

scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = scene.render.resolution_y = int(request["size"])
scene.view_settings.view_transform = "Standard"
shading = scene.display.shading
shading.light = "STUDIO"
shading.color_type = "TEXTURE"
shading.show_backface_culling = True
shading.show_cavity = False
scene.world = bpy.data.worlds.new("review")
scene.world.color = (1.0, 0.0, 1.0)


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


rest_low, rest_high = bounds()
span = max(rest_high.x - rest_low.x, rest_high.y - rest_low.y, rest_high.z - rest_low.z, 1e-3)

disc = bpy.data.meshes.new("ground")
rim = [(math.cos(k * math.tau / 48) * span * 1.4, math.sin(k * math.tau / 48) * span * 1.4, rest_low.z) for k in range(48)]
disc.from_pydata([(0.0, 0.0, rest_low.z)] + rim, [], [(0, k + 1, (k + 1) % 48 + 1) for k in range(48)])
ground_material = bpy.data.materials.new("ground")
ground_material.diffuse_color = (0.08, 0.16, 0.08, 1.0)
disc.materials.append(ground_material)
scene.collection.objects.link(bpy.data.objects.new("ground", disc))

camera_data = bpy.data.cameras.new("review")
camera_data.type = "ORTHO"
camera = bpy.data.objects.new("review", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
# io_pdx_mesh imports units facing -Y with Z up. (azimuth, elevation) in degrees; azimuth 0 faces the unit.
VIEWS = {"front": (0, 8), "left": (90, 8), "back": (180, 8), "right": (270, 8), "hoi4": (25, 55), "below": (200, -25)}


def aim(view):
    azimuth, elevation = (math.radians(value) for value in VIEWS[view])
    direction = Vector((math.sin(azimuth) * math.cos(elevation), -math.cos(azimuth) * math.cos(elevation), math.sin(elevation)))
    camera.location = (rest_low + rest_high) / 2 + direction * span * 6
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera_data.ortho_scale = span * 1.45
    camera_data.clip_end = span * 20


index = {"mesh": request["mesh"], "views": request["views"], "clips": []}


def render(clip, frames):
    rows = []
    for frame in frames:
        scene.frame_set(frame)
        row = {"frame": frame, "tiles": {}}
        for view in request["views"]:
            aim(view)
            path = out / f"{clip}_{frame:04d}_{view}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            row["tiles"][view] = path.name
        rows.append(row)
    index["clips"].append({"name": clip, "rows": rows})


if rig is not None:
    rig.animation_data_create()
render("rest", [scene.frame_current])
for clip in request["clips"]:
    if rig is None:
        break
    rig.animation_data.action = bpy.data.actions.new(clip["name"])
    bpy.ops.io_pdx_mesh.import_anim(filepath=clip["path"], int_start=1)
    # `.anim` sample k plays at Blender frame k + 1.
    render(clip["name"], [frame + 1 for frame in clip["frames"]])

(out / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
print("REVIEW_RENDERED", out)
