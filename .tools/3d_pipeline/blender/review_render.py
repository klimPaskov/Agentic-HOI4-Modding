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

With `diagnostic_views`, each clip's `diagnostic_frames` (its worst-stretch, lowest and highest frames)
are rendered again in flat colours that show what the checks measure: grey is fine, yellow to red is
surface stretched or squashed by 1.3 to 1.5 times or more, cyan is an open edge, blue is below the
ground. Back faces stay culled on magenta. Those tiles end in `_diag.png`.
"""

import json
import math
import sys
from pathlib import Path

import addon_utils
import bpy
import numpy as np
from mathutils import Matrix, Vector

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
def is_collision(o):
    # the selection box: named for it in our units, a plain "pCube1" with the Collision shader in vanilla's
    return "collision" in o.name.lower() or any(slot.material and slot.material.get("shader") == "Collision" for slot in o.material_slots)


meshes = [o for o in scene.objects if o.type == "MESH" and not is_collision(o)]
for o in scene.objects:
    if o.type == "MESH" and o not in meshes:
        o.hide_render = True

# A mount's rider (`attach`): the rider entity's mesh, drawn on the mount's node at the rider entity's scale, playing its own clip per
# mount clip. io_pdx_mesh finds the armature to animate by bone name, and the two rigs can share names (Spine, Head), so while one rig's
# clip is imported the other rig's armature data is swapped for an empty one.
ATTACH = request.get("attach") or {}
rider_rig = None
_empty_armature = bpy.data.armatures.new("review_empty")
if ATTACH:
    before = set(scene.objects)
    # The importer looks for an existing armature by bone name too, so the mount's is hidden while the rider comes in.
    mount_data = rig.data if rig is not None else None
    if rig is not None:
        rig.data = _empty_armature
    try:
        bpy.ops.io_pdx_mesh.import_mesh(filepath=ATTACH["mesh"], chk_locs=True)
    finally:
        if rig is not None:
            rig.data = mount_data
    added = [o for o in scene.objects if o not in before]
    rider_rig = next((o for o in added if o.type == "ARMATURE"), None)
    for o in added:
        if o.type == "MESH":
            if is_collision(o):
                o.hide_render = True
            else:
                o["hoi4_rider"] = True
                meshes.append(o)
    if rider_rig is not None:
        # The rider's skin follows the rider's own rig (the importer can bind it to the first rig that has a bone of the same name).
        for o in added:
            if o.type == "MESH":
                for modifier in o.modifiers:
                    if modifier.type == "ARMATURE":
                        modifier.object = rider_rig
                if o.parent is not rider_rig:
                    world = o.matrix_world.copy()
                    o.parent = rider_rig
                    o.matrix_world = world
    if rig is not None and rider_rig is not None:
        RIDER_REST = rider_rig.matrix_world.copy()
        print("REVIEW_RIDER", rider_rig.name, "node found:", ATTACH.get("node") in rig.data.bones)


def place_rider():
    """Put the rider entity on the mount's node in the current frame: the node's posed matrix, then the rider's entity scale."""

    if rider_rig is None or rig is None or ATTACH.get("node") not in rig.pose.bones:
        return
    bpy.context.view_layer.update()
    node = rig.pose.bones[ATTACH["node"]]
    # Both rigs come in with io_pdx_mesh's own object transform: the rider's rest is taken into the mount's armature space first.
    rider_rig.matrix_world = rig.matrix_world @ node.matrix @ Matrix.Diagonal((ATTACH["scale"],) * 3 + (1.0,)) @ rig.matrix_world.inverted() @ RIDER_REST
    bpy.context.view_layer.update()


def import_clip(target, path):
    """Import one .anim onto `target` (the mount's or the rider's rig), the other rig hidden from io_pdx_mesh's bone-name lookup."""

    other = rider_rig if target is rig else rig
    saved = other.data if other is not None else None
    if other is not None:
        other.data = _empty_armature
    try:
        target.animation_data_create()
        target.animation_data.action = bpy.data.actions.new(Path(path).stem)
        bpy.ops.io_pdx_mesh.import_anim(filepath=path, int_start=1)
    finally:
        if other is not None:
            other.data = saved

# A stream on vanilla's scrolling shader (a tank's track runs, `PdxMeshAdvancedAnim`) keeps the textures its own
# material names (io_pdx_mesh loaded them beside the mesh), not the shape's body map. Its tread scrolls in a move
# clip as the game scrolls it, by the entity's `texture_anim_speed` UV units a second.
SCROLLING = "PdxMeshAdvancedAnim"
OWN_MAP_MARK = "_ash_"  # lib/tripo_burn.ASH_MARK
own_maps = {}
for o in meshes:
    for slot in o.material_slots:
        material = slot.material
        found = [n.image for n in material.node_tree.nodes if n.type == "TEX_IMAGE" and n.image] if material is not None and material.node_tree else []
        # A stream whose material names its own diffuse map (a burn death's ash heap, lib/tripo_burn.py) keeps it too, not the shape's
        own_diffuse = any(OWN_MAP_MARK in i.name.lower() for i in found)
        if material is not None and (material.get("shader") == SCROLLING or own_diffuse) and material.node_tree:
            own_maps[material.name] = {
                "diffuse": next((i for i in found if "diff" in i.name.lower()), found[0] if found else None),
                "specular": next((i for i in found if "spec" in i.name.lower()), None),
            }
scrollers = []  # (mapping node) of every scrolling material, moved per frame in a move clip


def scroll_node(tree, image_node):
    """A UV mapping in front of `image_node`, kept to scroll the tread."""

    coordinates = tree.nodes.new("ShaderNodeTexCoord")
    mapping = tree.nodes.new("ShaderNodeMapping")
    tree.links.new(coordinates.outputs["UV"], mapping.inputs["Vector"])
    tree.links.new(mapping.outputs["Vector"], image_node.inputs["Vector"])
    scrollers.append(mapping)


# A `.mesh` usually names no texture: the `.gfx` meshsettings do. Give each shape its diffuse map
# as the active image node, which Workbench's texture colour mode draws.
images = {}
for o in meshes:
    # Imported objects are named after their shape, with a ".001"-style or "-001" suffix when repeated.
    maps = ATTACH["diffuse"] if o.get("hoi4_rider") else request["diffuse"]
    shapes = [shape for shape in maps if shape != "*" and o.name.startswith(shape)]
    path = maps[max(shapes, key=len)] if shapes else maps.get("*")
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
        own = own_maps.get(slot.material.name, {}).get("diffuse")
        node.image = own or images[path]
        if slot.material.name in own_maps:
            scroll_node(slot.material.node_tree, node)
        slot.material.node_tree.nodes.active = node

PBR = bool(request.get("pbr", True))  # the default: shaded from the packed PDX specular. "pbr": false keeps the old Workbench studio light
if PBR:
    # Shade from the packed PDX specular the game gets: green = specular level, alpha = glossiness, blue = metalness
    # (roughness = 1 - glossiness). Workbench cannot read a texture for these, so this mode renders with EEVEE.
    scrollers.clear()  # the trees are rebuilt below, so the Workbench mappings are gone (a removed node has no inputs)
    spec_images = {}
    for o in meshes:
        maps = ATTACH["diffuse"] if o.get("hoi4_rider") else request["diffuse"]
        speculars = ATTACH.get("specular", {}) if o.get("hoi4_rider") else request.get("specular", {})
        shapes = [shape for shape in maps if shape != "*" and o.name.startswith(shape)]
        key = max(shapes, key=len) if shapes else "*"
        spec_path = speculars.get(key) or speculars.get("*")
        diffuse_path = maps.get(key) or maps.get("*")
        if not diffuse_path:
            continue
        if spec_path and spec_path not in spec_images:
            spec_images[spec_path] = bpy.data.images.load(spec_path)
            spec_images[spec_path].colorspace_settings.name = "Non-Color"
            spec_images[spec_path].alpha_mode = "CHANNEL_PACKED"
        for slot in o.material_slots:
            material = slot.material
            if material is None:
                continue
            material.use_nodes = True
            material.use_backface_culling = True
            tree = material.node_tree
            tree.nodes.clear()
            out_node = tree.nodes.new("ShaderNodeOutputMaterial")
            bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
            diffuse = tree.nodes.new("ShaderNodeTexImage")
            diffuse.image = own_maps.get(material.name, {}).get("diffuse") or images[diffuse_path]
            spec = tree.nodes.new("ShaderNodeTexImage")
            if spec_path:
                spec.image = spec_images[spec_path]
            if material.name in own_maps:
                own_spec = own_maps[material.name].get("specular")
                if own_spec is not None:
                    own_spec.colorspace_settings.name = "Non-Color"
                    own_spec.alpha_mode = "CHANNEL_PACKED"
                    spec.image = own_spec
                scroll_node(tree, diffuse)
                scroll_node(tree, spec)
            split = tree.nodes.new("ShaderNodeSeparateColor")
            invert = tree.nodes.new("ShaderNodeMath")
            invert.operation = "SUBTRACT"
            invert.inputs[0].default_value = 1.0
            level = tree.nodes.new("ShaderNodeMath")
            level.operation = "MULTIPLY"
            level.inputs[1].default_value = 2.0
            level.use_clamp = True
            links = tree.links
            links.new(diffuse.outputs["Color"], bsdf.inputs["Base Color"])
            if spec_path:
                links.new(spec.outputs["Color"], split.inputs["Color"])
                links.new(spec.outputs["Alpha"], invert.inputs[1])
                links.new(invert.outputs["Value"], bsdf.inputs["Roughness"])
                links.new(split.outputs["Blue"], bsdf.inputs["Metallic"])
                links.new(split.outputs["Green"], level.inputs[0])
                links.new(level.outputs["Value"], bsdf.inputs["Specular IOR Level"])
            else:  # no packed specular beside the mesh: matte, not metal
                bsdf.inputs["Roughness"].default_value = 0.75
                bsdf.inputs["Metallic"].default_value = 0.0
            links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    scene.render.engine = "BLENDER_EEVEE"
    # The world lights the unit grey and shows magenta to the camera; one sun gives the form.
    world = bpy.data.worlds.new("review")
    world.use_nodes = True
    wt = world.node_tree
    wt.nodes.clear()
    light_path = wt.nodes.new("ShaderNodeLightPath")
    grey = wt.nodes.new("ShaderNodeBackground")
    grey.inputs["Color"].default_value = (0.55, 0.55, 0.57, 1.0)
    grey.inputs["Strength"].default_value = float(request.get("ambient", 1.0))
    magenta = wt.nodes.new("ShaderNodeBackground")
    magenta.inputs["Color"].default_value = (1.0, 0.0, 1.0, 1.0)
    mix = wt.nodes.new("ShaderNodeMixShader")
    world_out = wt.nodes.new("ShaderNodeOutputWorld")
    wt.links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
    wt.links.new(grey.outputs["Background"], mix.inputs[1])
    wt.links.new(magenta.outputs["Background"], mix.inputs[2])
    wt.links.new(mix.outputs["Shader"], world_out.inputs["Surface"])
    scene.world = world
    sun_data = bpy.data.lights.new("sun", "SUN")
    sun_data.energy = float(request.get("sun", 3.0))
    sun_data.use_shadow = bool(request.get("sun_shadow", True))  # off: no part casts a shadow on another (static review sheets)
    sun = bpy.data.objects.new("sun", sun_data)
    sun.rotation_euler = (math.radians(55), 0.0, math.radians(-25))
    scene.collection.objects.link(sun)
else:
    scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = scene.render.resolution_y = int(request["size"])
scene.view_settings.view_transform = "Standard"
# Workbench's studio light leaves a unit about 40% darker than its own diffuse map (vanilla's ENG infantry measured 95 unlit,
# 55 lit; the game shows it near the diffuse map's brightness). One stop and a bit of exposure puts the lit tiles back near the
# texture (lit 85 against unlit 86 on that unit). The flat-colour diagnostic tiles keep exposure 0 so their colours read as before.
EXPOSURE = float(request.get("exposure", 0.0 if PBR else 1.1))
scene.view_settings.exposure = EXPOSURE
shading = scene.display.shading
shading.light = request.get("light", "STUDIO")  # "FLAT" shows the diffuse map alone, unlit (`tripo/colour_compare.py`)
shading.color_type = "TEXTURE"
shading.show_backface_culling = True
shading.show_cavity = False
if not PBR:
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


place_rider()
rest_low, rest_high = bounds()
span = max(rest_high.x - rest_low.x, rest_high.y - rest_low.y, rest_high.z - rest_low.z, 1e-3)

disc = bpy.data.meshes.new("ground")
# The disc sits at the rest pose's lowest point, or at `ground_z` when the request names it (a ship's waterline is z = 0,
# with its keel below).
ground_z = float(request["ground_z"]) if request.get("ground_z") is not None else rest_low.z
rim = [(math.cos(k * math.tau / 48) * span * 1.4, math.sin(k * math.tau / 48) * span * 1.4, ground_z) for k in range(48)]
disc.from_pydata([(0.0, 0.0, ground_z)] + rim, [], [(0, k + 1, (k + 1) % 48 + 1) for k in range(48)])
ground_material = bpy.data.materials.new("ground")
ground_material.diffuse_color = (0.08, 0.16, 0.08, 1.0)
if PBR:
    # unlit, so the disc has no shadows and its colour is the same wherever the unit stands
    ground_material.use_nodes = True
    gt = ground_material.node_tree
    gt.nodes.clear()
    emission = gt.nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (0.08, 0.16, 0.08, 1.0)
    gt_out = gt.nodes.new("ShaderNodeOutputMaterial")
    alpha = float(request.get("ground_alpha", 1.0))
    if alpha < 1.0:
        # see-through water (`ground_alpha`): a sinking ship's hull shows under the surface instead of seeming cut off
        clear = gt.nodes.new("ShaderNodeBsdfTransparent")
        mix = gt.nodes.new("ShaderNodeMixShader")
        mix.inputs["Fac"].default_value = alpha
        gt.links.new(clear.outputs["BSDF"], mix.inputs[1])
        gt.links.new(emission.outputs["Emission"], mix.inputs[2])
        gt.links.new(mix.outputs["Shader"], gt_out.inputs["Surface"])
        if hasattr(ground_material, "surface_render_method"):
            ground_material.surface_render_method = "BLENDED"
        else:
            ground_material.blend_method = "BLEND"
    else:
        gt.links.new(emission.outputs["Emission"], gt_out.inputs["Surface"])
# The disc faces up, so with back faces culled the `below` view looks up through it. The PBR material needs this
# set as well, or the disc hides the whole unit from below.
ground_material.use_backface_culling = True
disc.materials.append(ground_material)
scene.collection.objects.link(bpy.data.objects.new("ground", disc))

camera_data = bpy.data.cameras.new("review")
camera_data.type = "ORTHO"
camera = bpy.data.objects.new("review", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
# io_pdx_mesh imports units facing -Y with Z up. (azimuth, elevation) in degrees; azimuth 0 faces the unit.
VIEWS = {"front": (0, 8), "left": (90, 8), "back": (180, 8), "right": (270, 8), "hoi4": (25, 55), "below": (200, -25)}
# A request may add views (`view_angles`: name -> [azimuth, elevation]) and zoom (`ortho_share`: the frame is that
# many times the unit's largest extent; default 1.45), as `weapon_sheets.py` does for close-ups.
VIEWS.update({name: tuple(angles) for name, angles in request.get("view_angles", {}).items()})


def aim(view):
    azimuth, elevation = (math.radians(value) for value in VIEWS[view])
    direction = Vector((math.sin(azimuth) * math.cos(elevation), -math.cos(azimuth) * math.cos(elevation), math.sin(elevation)))
    camera.location = (rest_low + rest_high) / 2 + direction * span * 6
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera_data.ortho_scale = span * float(request.get("ortho_share", 1.45))
    camera_data.clip_end = span * 20


index = {"mesh": request["mesh"], "views": request["views"], "clips": []}


def scroll(clip, frame):
    """Move every scrolling tread to where the game has it at this frame of a move clip (still in any other clip)."""

    speed = float(request.get("texture_anim_speed") or 0.0)
    offset = -(frame - 1) / 30.0 * speed if clip.endswith("_move") else 0.0  # Blender's v is 1 - the game's
    for mapping in scrollers:
        mapping.inputs["Location"].default_value[1] = offset


def render(clip, frames):
    rows = []
    prepare_tracks(clip, frames)
    for frame in frames:
        scene.frame_set(frame)
        scroll(clip, frame)
        place_rider()
        row = {"frame": frame, "tiles": {}}
        if update_standin(clip, frame):
            row["standin"] = True
        for view in request["views"]:
            aim(view)
            bpy.context.view_layer.update()
            path = out / f"{clip}_{frame:04d}_{view}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            row["tiles"][view] = path.name
        rows.append(row)
    index["clips"].append({"name": clip, "rows": rows})


# ---- particles drawn as a stand-in (lib/tripo_burn.py's burn, lib/unit_effects.py's effects) ----
# The game draws particles; Blender cannot. When the unit's burn plan (`<stem>_burn.json`) or effects plan (`<stem>_effects.json`) lies
# beside the mesh, the tiles of each clip that fires one get billboards at its locator: a flash that blooms and dies at once, fire rising
# fast and fading, grey smoke rising slowly and growing, a spell's glow in its own colour, a blast that swells. Each starts at its event's
# `time` and emits for its `duration_s`, at the game's 30 frames a second. Every tile that shows one is stamped "particles: stand-in",
# since only the game shows the real ones.
STANDIN = {"fire": {"count": 24, "life": 0.8, "rise": 0.45, "size": (0.10, 0.05), "colour": (1.0, 0.45, 0.08), "alpha": 0.9, "strength": 6.0},
           "smoke": {"count": 20, "life": 2.5, "rise": 0.22, "size": (0.12, 0.42), "colour": (0.22, 0.21, 0.2), "alpha": 0.55, "strength": 0.0},
           "gunsmoke": {"count": 10, "life": 1.5, "rise": 0.06, "size": (0.05, 0.16), "colour": (0.42, 0.41, 0.4), "alpha": 0.6, "strength": 0.0},
           "flash": {"count": 4, "life": 0.1, "rise": 0.0, "size": (0.09, 0.05), "colour": (1.0, 0.62, 0.2), "alpha": 1.0, "strength": 3.0},
           "spell": {"count": 14, "life": 0.45, "rise": 0.08, "size": (0.07, 0.02), "colour": (0.47, 0.59, 1.0), "alpha": 0.95, "strength": 8.0},
           "blast": {"count": 18, "life": 1.0, "rise": 0.12, "size": (0.22, 0.45), "colour": (1.0, 0.5, 0.12), "alpha": 0.85, "strength": 5.0},
           # vanilla's leaflet fall: 3 subsystems emitting 2 a second, each feather living 4 s, size 1.0 (0.15 of a unit's height at scale 1)
           "feather": {"count": 18, "rate": 2.0, "life": 4.0, "rise": 0.0, "to_ground": True, "spread": 0.015, "drift": 0.6, "roll": True, "size": (0.15, 0.13),
                       "colour": (0.92, 0.91, 0.88), "alpha": 1.0, "strength": 0.0}}
# A rule with `to_ground` falls from its birth point to the ground over its life, as vanilla's leaflets fall 8 units to the ground in
# their 4 s (a slow drift read as feathers glued to the wing in a fresh review). `roll` turns each billboard by its own angle in its
# plane, so the sprites do not read as a row of identical streaks.
# A rule with `rate` emits like the game: billboard k is born at start + k / rate and lives `life`. The rate is per kept subsystem of
# the particle (`keep_subsystems`): vanilla's leaflet fall emits 2 a second from each. Otherwise `count` billboards cycle
# through the emission at evenly spread phases. A particle released into the world (`reset_placement`, local_space no) starts where its
# locator was at its birth and then falls on its own: a first try drew it at the locator's current place, and two fresh reviews read the
# feathers as glued to the beating wing.
# The burn's fire and smoke are sized on the model's largest extent, as they were reviewed. An effect is sized on the model's height: a
# demon's wingspan made a claw's flame rise far above its head as a string of beads (fresh review of the first effects sheet).
_mesh_path = Path(request["mesh"])
_plan_path = _mesh_path.with_name(f"{_mesh_path.stem}_burn.json")
burn_plan = json.loads(_plan_path.read_text(encoding="utf-8")) if _plan_path.is_file() else None
_effects_path = _mesh_path.with_name(f"{_mesh_path.stem}_effects.json")
effects_plan = json.loads(_effects_path.read_text(encoding="utf-8")) if _effects_path.is_file() else None
emitters = []  # {clip, locator, bone, time, duration_s, kind, colour, scale}
for particle in (burn_plan or {}).get("particles", []):
    emitters.append({"clip": burn_plan.get("clip"), "locator": burn_plan.get("locator"), "bone": burn_plan.get("locator_bone"),
                     "time": float(particle["time"]), "duration_s": float(particle["duration_s"]), "kind": particle["standin"], "colour": None, "scale": 1.0})
_scales = {p["name"]: float(p.get("scale", 1) or 1) for p in (effects_plan or {}).get("particles", [])}
_sprites = {p["name"]: p["sprite"]["source"] for p in (effects_plan or {}).get("particles", []) if p.get("sprite")}
_released = {p["name"] for p in (effects_plan or {}).get("particles", []) if p.get("reset_placement")}
_subsystems = {p["name"]: len(p.get("keep_subsystems") or [1]) for p in (effects_plan or {}).get("particles", [])}
for event in (effects_plan or {}).get("events", []):
    if event.get("standin") in STANDIN:
        kind = "gunsmoke" if event["standin"] == "smoke" and event.get("role") != "death" else event["standin"]  # a shot's puff, not a wreck's plume
        emitters.append({"clip": event["clip"], "locator": event["node"], "bone": event.get("bone"), "time": float(event["time"]),
                         "duration_s": float(event["duration_s"]), "kind": kind, "height": True, "still": bool(event.get("loop")),
                         "sprite": _sprites.get(event["particle"]), "world": event["particle"] in _released,
                         "streams": _subsystems.get(event["particle"], 1),
                         "colour": [c / 255.0 for c in event["colour"]] if event.get("colour") else None, "scale": _scales.get(event["particle"], 1.0)})
_unique = {}
for emitter in emitters:  # one set of billboards for a locator, clip, kind and start
    _unique.setdefault((emitter["clip"], emitter["locator"], emitter["kind"], emitter["time"]), emitter)
emitters = list(_unique.values())
standin = []  # (emitter, object, phase, offset)


def _sprite_nodes(tree, coords, alpha, emission, sprite, colour):
    """Draw the particle's own sprite (a feather) on the billboard, tinted by its colour: the sprite's alpha shapes the billboard and its
    colour times the tint lights it. Each billboard carries a UV layer over its corners, so a rolled quad rolls its sprite (mapping by
    object coordinates kept every sprite upright, and the feathers read as a row of identical streaks). Nothing changes without a sprite."""

    if not sprite or not Path(sprite).is_file():
        return
    try:
        image = bpy.data.images.load(str(sprite), check_existing=True)
    except RuntimeError:
        return
    texture = tree.nodes.new("ShaderNodeTexImage")
    texture.image = image
    tree.links.new(coords.outputs["UV"], texture.inputs["Vector"])
    texture.extension = "CLIP"
    tree.links.new(texture.outputs["Alpha"], alpha.inputs[0])
    tint = tree.nodes.new("ShaderNodeMix") if bpy.app.version >= (3, 4, 0) else tree.nodes.new("ShaderNodeMixRGB")
    tint.blend_type = "MULTIPLY"
    if tint.bl_idname == "ShaderNodeMix":
        tint.data_type = "RGBA"
        tint.inputs["Factor"].default_value = 1.0
        tree.links.new(texture.outputs["Color"], tint.inputs[6])
        tint.inputs[7].default_value = (*colour, 1.0)
        tree.links.new(tint.outputs[2], emission.inputs["Color"])
    else:
        tint.inputs["Fac"].default_value = 1.0
        tree.links.new(texture.outputs["Color"], tint.inputs["Color1"])
        tint.inputs["Color2"].default_value = (*colour, 1.0)
        tree.links.new(tint.outputs["Color"], emission.inputs["Color"])


def _standin_material(kind, colour=None, sprite=None):
    """A soft round billboard, or the particle's own sprite (a feather) tinted by its colour when it has one."""

    rule = STANDIN[kind]
    colour = tuple(colour) if colour else rule["colour"]
    material = bpy.data.materials.new(f"standin_{kind}")
    material.diffuse_color = (*colour, rule["alpha"])
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    coords = tree.nodes.new("ShaderNodeTexCoord")
    gradient = tree.nodes.new("ShaderNodeTexGradient")
    gradient.gradient_type = "SPHERICAL"
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (2.0, 2.0, 2.0)  # the plane's corners are past the gradient's rim: a soft round puff
    tree.links.new(coords.outputs["Object"], mapping.inputs["Vector"])
    tree.links.new(mapping.outputs["Vector"], gradient.inputs["Vector"])
    alpha = tree.nodes.new("ShaderNodeMath")
    alpha.operation = "MULTIPLY"
    alpha.inputs[1].default_value = rule["alpha"]
    tree.links.new(gradient.outputs["Fac"], alpha.inputs[0])
    material["standin_alpha"] = alpha.name
    emission = tree.nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*colour, 1.0)
    _sprite_nodes(tree, coords, alpha, emission, sprite, colour)
    emission.inputs["Strength"].default_value = max(rule["strength"], 1.0)
    clear = tree.nodes.new("ShaderNodeBsdfTransparent")
    mix = tree.nodes.new("ShaderNodeMixShader")
    tree.links.new(alpha.outputs["Value"], mix.inputs["Fac"])
    tree.links.new(clear.outputs["BSDF"], mix.inputs[1])
    tree.links.new(emission.outputs["Emission"], mix.inputs[2])
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "BLENDED"
    else:
        material.blend_method = "BLEND"
    return material


def _locator_world(emitter):
    empty = next((o for o in scene.objects if o.type == "EMPTY" and o.name.split(".")[0] == emitter.get("locator")), None)
    if empty is not None:
        return empty.matrix_world.translation.copy()
    bone = emitter.get("bone")
    if rig is not None and bone in rig.pose.bones:
        return rig.matrix_world @ rig.pose.bones[bone].head
    return (rest_low + rest_high) / 2


if emitters:
    import random

    chance = random.Random(11)
    for number, emitter in enumerate(emitters):
        rule = STANDIN[emitter["kind"]]
        material = _standin_material(emitter["kind"], emitter.get("colour"), emitter.get("sprite"))
        for k in range(rule["count"]):
            plane = bpy.data.meshes.new(f"standin_{emitter['kind']}_{number}_{k}")
            corners = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
            if rule.get("roll"):
                turn = chance.uniform(0.0, math.tau)
                corners = [(x * math.cos(turn) - y * math.sin(turn), x * math.sin(turn) + y * math.cos(turn)) for x, y in corners]
            plane.from_pydata([(x, y, 0.0) for x, y in corners], [], [(0, 1, 2, 3)])
            # the sprite follows the corners through their UVs, so a rolled quad shows a rolled sprite
            layer = plane.uv_layers.new(name="UVMap")
            for loop, (u, v) in zip(layer.data, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
                loop.uv = (u, v)
            plane.materials.append(material)
            obj = bpy.data.objects.new(f"standin_{emitter['kind']}_{number}_{k}", plane)
            scene.collection.objects.link(obj)
            track = obj.constraints.new("TRACK_TO")
            track.target = camera
            track.track_axis = "TRACK_Z"
            track.up_axis = "UP_Y"
            obj.hide_render = True
            offset = Vector((chance.uniform(-1, 1), chance.uniform(-1, 1), chance.uniform(-0.3, 0.3)))
            standin.append((emitter, obj, k / rule["count"], offset))


tracks = {}  # (clip, locator) -> {frame: the locator's world point}, for particles released into the world


def prepare_tracks(clip, frames):
    """Record where each released emitter's locator is on every frame of `clip` up to the last rendered one, so a particle can start at
    its locator's place at its birth. Runs before the clip's tiles, which set their own frames again."""

    for emitter in emitters:
        if emitter.get("world") and emitter["clip"] == clip and (clip, emitter["locator"]) not in tracks:
            track = {}
            for frame in range(1, max(frames) + 1):
                scene.frame_set(frame)
                track[frame] = _locator_world(emitter)
            tracks[(clip, emitter["locator"])] = track


def _billboard_age(rule, phase, number, seconds, start, duration, streams=1):
    """(age as a share of life, birth second) of one billboard at `seconds`, or None when it is not alive."""

    if rule.get("rate"):
        born = start + number / (rule["rate"] * streams)
    else:
        age = ((seconds - start) / rule["life"] + phase) % 1.0
        born = seconds - age * rule["life"]
    if born < start or born > start + duration or not born <= seconds <= born + rule["life"]:
        return None
    return (seconds - born) / rule["life"], born


def update_standin(clip, frame):
    """Place the stand-in particles for this frame of `clip`; True when any is shown (the tile is then stamped)."""

    shown = False
    seconds = (frame - 1) / 30.0
    centres = {}
    counted = {}
    for emitter, obj, phase, offset in standin:
        rule = STANDIN[emitter["kind"]]
        number = counted.get(id(emitter), 0)
        counted[id(emitter)] = number + 1
        start, duration = emitter["time"], emitter["duration_s"]
        alive = _billboard_age(rule, phase, number, seconds, start, duration, emitter.get("streams", 1)) if clip == emitter["clip"] else None
        if alive is None:
            obj.hide_render = True
            continue
        age, born = alive
        key = emitter["locator"]
        if emitter.get("world") and (clip, key) in tracks:
            track = tracks[(clip, key)]
            centre = track.get(1 + int(round(born * 30.0)), track[max(track)]).copy()
        else:
            if key not in centres:
                centres[key] = _locator_world(emitter)
            centre = centres[key]
        grow = emitter.get("scale", 1.0)
        measure = (rest_high.z - rest_low.z) if emitter.get("height") else span
        size = measure * grow * (rule["size"][0] + (rule["size"][1] - rule["size"][0]) * age)
        spread = rule.get("spread", 0.06) + rule.get("drift", 0.0) * age
        if rule.get("to_ground"):
            # gathering speed, on the ground three quarters into its life (a slow drift read as feathers stuck to the wing)
            fall = -(centre.z - ground_z) * min(1.0, 1.6 * age * (0.6 + 0.4 * age))
        else:
            fall = 0.0 if emitter.get("still") else rule["rise"] * measure * grow * age * rule["life"]
        obj.location = centre + offset * measure * spread * grow + Vector((0.0, 0.0, fall))
        obj.scale = (size, size, size)
        obj.hide_render = False
        shown = True
    stamp = scene.render
    stamp.use_stamp = shown
    if shown:
        for name in dir(stamp):
            if name.startswith("use_stamp_") and name != "use_stamp_note" and isinstance(getattr(stamp, name), bool):
                try:
                    setattr(stamp, name, False)
                except (AttributeError, TypeError):
                    pass
        stamp.use_stamp_note = True
        stamp.stamp_note_text = f"particles: stand-in, frame {frame - 1}"  # the sheet's own frame label sits under the stamp
        stamp.stamp_font_size = max(8, int(scene.render.resolution_y / 30))
    return shown


# ---- diagnostics: colour what the checks measure, so a reviewer sees where it is ----
# Grey is fine. Yellow to red: an edge around the vertex is stretched or squashed by 1.3 to 1.5 times
# or more. Cyan: an open edge (a hole's rim). Blue: below the ground. Back faces stay culled on magenta.
# The same edges UNIT-ANIM-STRETCH counts: a change of more than 0.5 % of the unit's height.
DIAG_START, DIAG_FULL, SIGNIFICANT = 1.3, 1.5, 0.005
height = max(rest_high.z - rest_low.z, 1e-6)
rest_data = {}
for o in meshes:
    data = o.data
    count = len(data.vertices)
    co = np.empty(count * 3, dtype=np.float64)
    data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    edges = np.empty(len(data.edges) * 2, dtype=np.int64)
    data.edges.foreach_get("vertices", edges)
    edges = edges.reshape(-1, 2)
    # Weld split seams by position, then an edge with one face is open.
    keys = np.round(co / (height * 1e-5)).astype(np.int64)
    _unique, canon = np.unique(keys, axis=0, return_inverse=True)
    canon = canon.ravel()
    loops = np.empty(len(data.loops), dtype=np.int64)
    data.loops.foreach_get("vertex_index", loops)
    starts = np.empty(len(data.polygons), dtype=np.int64)
    data.polygons.foreach_get("loop_start", starts)
    totals = np.empty(len(data.polygons), dtype=np.int64)
    data.polygons.foreach_get("loop_total", totals)
    face_edges = []
    for start, total in zip(starts, totals):
        ring = canon[loops[start : start + total]]
        face_edges.extend(zip(ring, np.roll(ring, -1)))
    face_edges = np.sort(np.asarray(face_edges, dtype=np.int64).reshape(-1, 2), axis=1) if face_edges else np.zeros((0, 2), dtype=np.int64)
    pairs, counts = np.unique(face_edges, axis=0, return_counts=True) if len(face_edges) else (np.zeros((0, 2), dtype=np.int64), np.zeros(0))
    open_canon = set(pairs[counts == 1].ravel().tolist())
    rest_data[o.name] = {
        "edges": edges,
        "rest": np.linalg.norm(co[edges[:, 0]] - co[edges[:, 1]], axis=1),
        "open": np.isin(canon, list(open_canon)) if open_canon else np.zeros(count, dtype=bool),
    }
    attribute = data.color_attributes.get("review_diag") or data.color_attributes.new("review_diag", "FLOAT_COLOR", "POINT")
    data.color_attributes.active_color = attribute


def paint_diagnostics():
    graph = bpy.context.evaluated_depsgraph_get()
    worst = 0.0
    for o in meshes:
        info = rest_data[o.name]
        evaluated = o.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        co = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
        mesh.vertices.foreach_get("co", co)
        evaluated.to_mesh_clear()
        co = co.reshape(-1, 3) @ np.array(o.matrix_world)[:3, :3].T + np.array(o.matrix_world)[:3, 3]
        length = np.linalg.norm(co[info["edges"][:, 0]] - co[info["edges"][:, 1]], axis=1)
        usable = info["rest"] > height * 1e-6
        ratio = np.where(usable, length / np.where(usable, info["rest"], 1.0), 1.0)
        factor = np.maximum(ratio, 1.0 / np.maximum(ratio, 1e-6))
        factor[np.abs(length - info["rest"]) < SIGNIFICANT * height] = 1.0
        per_vertex = np.ones(len(co))
        np.maximum.at(per_vertex, info["edges"][:, 0], factor)
        np.maximum.at(per_vertex, info["edges"][:, 1], factor)
        growth = np.where(factor > 1.0, np.abs(length - info["rest"]) / height, 0.0)
        worst = max(worst, float(growth.max()) if len(growth) else 0.0)
        t = np.clip((per_vertex - DIAG_START) / (DIAG_FULL - DIAG_START), 0.0, 1.0)
        colour = np.tile([0.72, 0.72, 0.74, 1.0], (len(co), 1))
        hot = per_vertex > DIAG_START
        colour[hot] = np.stack([np.ones(hot.sum()), 0.9 * (1.0 - t[hot]), np.zeros(hot.sum()), np.ones(hot.sum())], axis=1)
        colour[co[:, 2] < ground_z - 0.01 * height] = [0.1, 0.3, 1.0, 1.0]
        colour[info["open"]] = [0.0, 1.0, 1.0, 1.0]
        o.data.color_attributes["review_diag"].data.foreach_set("color", colour.astype(np.float32).ravel())
        o.data.update()
    return worst


def render_diagnostics(clip, frames, views):
    rows = []
    # The flat colours need Workbench (EEVEE does not draw vertex colours without a material), on a magenta world.
    previous_engine, previous_world = scene.render.engine, scene.world
    scene.render.engine = "BLENDER_WORKBENCH"
    diagnostic_world = bpy.data.worlds.new("diagnostic")
    diagnostic_world.color = (1.0, 0.0, 1.0)
    scene.world = diagnostic_world
    shading.color_type = "VERTEX"
    shading.light = "STUDIO"
    scene.view_settings.exposure = 0.0
    for _kind, obj, _phase, _offset in standin:
        obj.hide_render = True
    scene.render.use_stamp = False
    for frame in frames:
        scene.frame_set(frame)
        place_rider()
        worst = paint_diagnostics()
        row = {"frame": frame, "tiles": {}, "worst_share": round(worst, 4)}
        for view in views:
            aim(view)
            path = out / f"{clip}_{frame:04d}_{view}_diag.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            row["tiles"][view] = path.name
        rows.append(row)
    shading.color_type = "TEXTURE"
    scene.render.engine, scene.world = previous_engine, previous_world
    scene.view_settings.exposure = 0.0 if PBR else EXPOSURE
    next(item for item in index["clips"] if item["name"] == clip)["diagnostic_rows"] = rows


if rig is not None:
    rig.animation_data_create()
render("rest", [scene.frame_current])
if request.get("diagnostic_views"):
    render_diagnostics("rest", [scene.frame_current], request["diagnostic_views"])
for clip in request["clips"]:
    if rig is None:
        break
    import_clip(rig, clip["path"])
    if rider_rig is not None and ATTACH.get("clips", {}).get(clip["name"]):
        import_clip(rider_rig, ATTACH["clips"][clip["name"]])
    # `.anim` sample k plays at Blender frame k + 1.
    render(clip["name"], [frame + 1 for frame in clip["frames"]])
    if request.get("diagnostic_views") and clip.get("diagnostic_frames"):
        render_diagnostics(clip["name"], [frame + 1 for frame in clip["diagnostic_frames"]], request["diagnostic_views"])

(out / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
print("REVIEW_RENDERED", out)
