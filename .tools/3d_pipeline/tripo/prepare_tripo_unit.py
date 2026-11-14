"""Turn one Tripo rigged GLB into the Meshy-shaped provider files the unit route reads.

Run it headless, through the Blender the pipeline discovers (tripo_intake.py does this)::

    blender -b --factory-startup --python prepare_tripo_unit.py -- <rigged.glb> --out-dir <dir>
        --roles idle=idle move=walk attack=chop defend=hit_to_body_01 retreat=flee_01 death=fall
        [--rigid-part tripo_part_1=RightHand | --rigid-from-twin <segmented.glb> tripo_part_1=RightHand]

What it does, with no new keyframes (only the clips Tripo exported):

1. Drops meshes without vertex groups (Blender's glTF import adds a stray bone-shape Icosphere).
2. Renames the `mixamorig:*` bones to the names the kit expects (Spine1 -> Spine01, Spine2 -> Spine02,
   Neck -> neck) and merges every other bone (fingers, `*_End`) into its nearest kept parent: the weights
   are added to that parent and the bone and its channels are dropped. HOI4 allows 50 bones; 23 remain.
3. Binds a held weapon rigidly: every weapon vertex gets weight 1.0 on one hand bone. The weapon is a
   whole part (`--rigid-part`, for a segmented rigged export) or the vertices whose nearest vertex in a
   segmented twin of the same pose belongs to that part (`--rigid-from-twin`; both are first normalised
   to the same height, ground and centre). Every vertex keeps at most 4 weights, normalised to 1.
4. Writes `<base-name>.glb` (mesh only, the rest pose), `<base-name>_textures/{base_color,normal,
   metallic_roughness}.png` and one `<role-name>.glb` per role (mesh, the shared armature, exactly one
   animation: the Tripo clip named in `--roles`, in the clip's own frames).

It prints one JSON line (it starts with `{"tool": "prepare_tripo_unit"`) and, with `--report`, writes
the same data plus the weapon vertex coordinates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
import tempfile
import zlib
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector, kdtree

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib.texture_lineage import ROLE_FILES, _SLOTS, _image_bytes, _read_glb, embedded_images  # noqa: E402
from lib.tripo import atlas_layout, resolve_clip_name, safe_animation_name  # noqa: E402

MAX_BONES = 50
# Texels of every atlas cell kept as a gutter: the tile is resampled inside it and its edge pixels are repeated
# into it, so filtering and mipmaps never mix a part's edge with its neighbour's cell.
ATLAS_GUTTER = 4
MAX_INFLUENCES = 4

# Mixamo name (without the `mixamorig:` prefix) -> the kit's name. Every bone not named here is merged.
KIT_BONES = {"Hips": "Hips", "Spine": "Spine", "Spine1": "Spine01", "Spine2": "Spine02", "Neck": "neck", "Head": "Head"}
for _side in ("Left", "Right"):
    for _part in ("Shoulder", "Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot", "ToeBase"):
        KIT_BONES[f"{_side}{_part}"] = f"{_side}{_part}"
KIT_NAMES = set(KIT_BONES.values())


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("rigged", type=Path, help="Tripo GLB with a skin and named animations")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--base-name", default="generation_model")
    parser.add_argument("--role-name", default="animation_{role}_provider", help="file stem per role; {role} is replaced")
    parser.add_argument("--roles", nargs="+", required=True, metavar="ROLE=CLIP")
    parser.add_argument("--rigid-part", action="append", default=[], metavar="PART=BONE")
    parser.add_argument("--rigid-from-twin", nargs=2, metavar=("GLB", "PART=BONE"))
    parser.add_argument("--trim", action="append", default=[], metavar="ROLE=MAX_FRAMES",
                        help="cut a long clip to at most MAX_FRAMES frames, ending on the frame whose pose is closest to frame 0")
    parser.add_argument("--report", type=Path)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def split_pair(text: str, what: str):
    left, sep, right = text.partition("=")
    if not sep or not left or not right:
        raise SystemExit(f"{what} must look like NAME=VALUE, got {text!r}")
    return left, right


def short_name(name: str) -> str:
    return re.sub(r"^mixamorig\d*:", "", name)


def action_fcurves(action):
    """Yield (fcurve, container) for legacy and Blender 5 layered actions."""

    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        for fcurve in list(legacy):
            yield fcurve, legacy
        return
    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            for channelbag in getattr(strip, "channelbags", []):
                fcurves = getattr(channelbag, "fcurves", None)
                if fcurves is not None:
                    for fcurve in list(fcurves):
                        yield fcurve, fcurves


def bone_of_path(data_path: str):
    match = re.match(r'pose\.bones\["([^"]+)"\]', data_path)
    return match.group(1) if match else None


def select_only(objects, active):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active


def import_glb(path: Path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [obj for obj in bpy.data.objects if obj not in before]


def kept_ancestor(bone, kept):
    while bone is not None and bone.name not in kept:
        bone = bone.parent
    return bone


def skinned_meshes(armature):
    return sorted(
        (o for o in bpy.data.objects if o.type == "MESH" and len(o.vertex_groups) > 0 and o.parent == armature),
        key=lambda o: o.name,
    )


def read_weights(obj):
    names = {group.index: group.name for group in obj.vertex_groups}
    return [{names[g.group]: g.weight for g in v.groups if g.group in names} for v in obj.data.vertices]


def world_points(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


def normaliser(points):
    low = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    high = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    height = max(high.z - low.z, 1e-9)
    centre = Vector(((low.x + high.x) / 2, (low.y + high.y) / 2, low.z))
    return (lambda p: (p - centre) / height), height, (low, high)


def classify_from_twin(armature_meshes, twin_path: Path, part: str):
    """Per object, a list of booleans: the vertex's nearest twin vertex belongs to `part`."""

    twin_objects = [o for o in import_glb(twin_path) if o.type == "MESH"]
    in_part = lambda o: o.name == part or o.name.startswith(part + ".") or o.data.name == part  # noqa: E731
    if not any(in_part(o) for o in twin_objects):
        raise SystemExit(f"The twin {twin_path.name} has no part named {part}; it has {[o.name for o in twin_objects]}")
    twin_points, twin_flags = [], []
    for obj in twin_objects:
        for point in world_points(obj):
            twin_points.append(point)
            twin_flags.append(in_part(obj))
    own_points = {obj.name: world_points(obj) for obj in armature_meshes}
    everything = [p for points in own_points.values() for p in points]
    own_norm, own_height, own_box = normaliser(everything)
    twin_norm, twin_height, twin_box = normaliser(twin_points)
    tree = kdtree.KDTree(len(twin_points))
    for index, point in enumerate(twin_points):
        tree.insert(twin_norm(point), index)
    tree.balance()
    flags, distances = {}, []
    for name, points in own_points.items():
        row = []
        for point in points:
            _co, index, distance = tree.find(own_norm(point))
            row.append(twin_flags[index])
            distances.append(distance)
        flags[name] = row
    distances.sort()
    for obj in twin_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    report = {
        "twin": twin_path.name,
        "part": part,
        "twin_vertices": len(twin_points),
        "twin_part_vertices": sum(twin_flags),
        "own_height_m": round(own_height, 5),
        "twin_height_m": round(twin_height, 5),
        "own_normalised_box_xy": [round(v, 4) for v in ((own_box[1].x - own_box[0].x) / own_height, (own_box[1].y - own_box[0].y) / own_height)],
        "twin_normalised_box_xy": [round(v, 4) for v in ((twin_box[1].x - twin_box[0].x) / twin_height, (twin_box[1].y - twin_box[0].y) / twin_height)],
        "nearest_distance_mean_in_heights": round(sum(distances) / len(distances), 5),
        "nearest_distance_p95_in_heights": round(distances[int(len(distances) * 0.95)], 5),
        "nearest_distance_max_in_heights": round(distances[-1], 5),
    }
    return flags, report


def separate_coincident_weapon_vertices(meshes, rigid_for):
    """Move every weapon vertex that sits on a body vertex 0.02 % of the height along its own normal.

    Tripo's Segment cuts a part with some of its boundary vertices on the neighbour's (the axe shaft
    inside the fist). They are separate vertices, but tools that weld by position (the kit's deformation
    check, and the winding repair's weld) join them, and then a rigid weapon vertex is skinned like the
    forearm vertex it coincides with. A 0.4 mm shift keeps them apart and cannot be seen.
    Returns the number of vertices moved.
    """

    points = [m.matrix_world @ v.co for m in meshes for v in m.data.vertices]
    height = max(p.z for p in points) - min(p.z for p in points)
    tolerance, shift = height * 3e-5, height * 2e-4
    body = [m.matrix_world @ v.co for m in meshes for i, v in enumerate(m.data.vertices)
            if not (m.name in rigid_for and rigid_for[m.name][1][i])]
    tree = kdtree.KDTree(len(body))
    for index, point in enumerate(body):
        tree.insert(point, index)
    tree.balance()
    moved = 0
    for obj in meshes:
        if obj.name not in rigid_for:
            continue
        for index, flag in enumerate(rigid_for[obj.name][1]):
            if not flag:
                continue
            vertex = obj.data.vertices[index]
            if tree.find_range(obj.matrix_world @ vertex.co, tolerance):
                vertex.co = vertex.co + vertex.normal * shift
                moved += 1
    return moved


def connected_weapon_parts(obj, flags):
    """Number of edge-connected groups among the flagged vertices (a clean weapon is one)."""

    parent = list(range(len(obj.data.vertices)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for edge in obj.data.edges:
        a, b = edge.vertices
        if flags[a] and flags[b]:
            parent[find(a)] = find(b)
    roots = {}
    for i, flag in enumerate(flags):
        if flag:
            roots[find(i)] = roots.get(find(i), 0) + 1
    return sorted(roots.values(), reverse=True)


def rewrite_weights(obj, weights, kept_names, merge_into, rigid_bone, weapon_flags):
    """Replace the vertex groups: merge dropped bones, rigid weapon, at most 4 influences, normalised."""

    rows = []
    for index, row in enumerate(weights):
        if weapon_flags[index]:
            rows.append({rigid_bone: 1.0})
            continue
        merged = {}
        for name, weight in row.items():
            target = merge_into.get(name)
            if target is not None and weight > 0.0:
                merged[target] = merged.get(target, 0.0) + weight
        ranked = sorted(merged.items(), key=lambda item: (-item[1], item[0]))[:MAX_INFLUENCES]
        total = sum(w for _, w in ranked) or 1.0
        rows.append({name: w / total for name, w in ranked})
    for group in list(obj.vertex_groups):
        obj.vertex_groups.remove(group)
    groups = {name: obj.vertex_groups.new(name=name) for name in kept_names}
    for index, row in enumerate(rows):
        for name, weight in row.items():
            groups[name].add([index], weight, "REPLACE")
    return rows


def write_png(path: Path, width: int, height: int, pixels) -> None:
    """Write 8-bit rows (top row first) as a PNG: a uint8 array of shape (height, width, 3), or (height, width) for gray."""

    channels = 1 if pixels.ndim == 2 else 3

    def chunk(kind: bytes, payload: bytes) -> bytes:
        body = kind + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    rows = np.zeros((height, width * channels + 1), dtype=np.uint8)
    rows[:, 1:] = pixels.reshape(height, width * channels)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2 if channels == 3 else 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows.tobytes(), 6))
        + chunk(b"IEND", b"")
    )


def write_rm_siblings(folder: Path, packed) -> None:
    """The kit packs metallic.png and roughness.png (Meshy's separate maps) into the PDX specular map.

    Tripo's metallic-roughness map is glTF's: roughness in green, metallic in blue.
    """

    height, width = packed.shape[:2]
    write_png(folder / "metallic.png", width, height, np.ascontiguousarray(packed[:, :, 2]))
    write_png(folder / "roughness.png", width, height, np.ascontiguousarray(packed[:, :, 1]))


def write_textures(source_glb: Path, folder: Path):
    """Extract the embedded maps as PNG sidecars (base_color, normal, metallic_roughness).

    Blender's decoded pixels equal Pillow's for the same bytes (checked), so the sidecar passes the
    kit's texture lineage gate by decoded pixels against every GLB that embeds the original bytes.
    """

    images = embedded_images(source_glb)
    folder.mkdir(parents=True, exist_ok=True)
    written = {}
    for role, filename in ROLE_FILES.items():
        found = images.get(role) or []
        if len(found) > 1:
            raise SystemExit(f"{source_glb.name} uses {len(found)} different {role} maps; one material per unit is supported")
        if not found:
            continue
        raw = found[0]
        with tempfile.TemporaryDirectory() as scratch:
            temporary = Path(scratch) / ("source.png" if raw[:4] == bytes([0x89]) + b"PNG" else "source.jpg")
            temporary.write_bytes(raw)
            image = bpy.data.images.load(str(temporary))
            width, height = image.size
            buffer = np.empty(width * height * 4, dtype=np.float32)
            image.pixels.foreach_get(buffer)
            bpy.data.images.remove(image)
        pixels = np.clip(np.rint(buffer * 255.0), 0, 255).astype(np.uint8).reshape(height, width, 4)
        write_png(folder / filename, width, height, pixels[::-1, :, :3])
        if role == "specular":
            write_rm_siblings(folder, pixels[::-1, :, :3])
        written[role] = filename
    if "diffuse" not in written:
        raise SystemExit(f"{source_glb.name} embeds no base color map")
    return written


def decode_rgb(raw: bytes):
    """Decode PNG or JPEG bytes with Blender (pixel-identical to Pillow's decode, checked) as (h, w, 3) uint8."""

    with tempfile.TemporaryDirectory() as scratch:
        temporary = Path(scratch) / ("source.png" if raw[:4] == bytes([0x89]) + b"PNG" else "source.jpg")
        temporary.write_bytes(raw)
        image = bpy.data.images.load(str(temporary))
        width, height = image.size
        buffer = np.empty(width * height * 4, dtype=np.float32)
        image.pixels.foreach_get(buffer)
        bpy.data.images.remove(image)
    pixels = np.clip(np.rint(buffer * 255.0), 0, 255).astype(np.uint8).reshape(height, width, 4)
    return pixels[::-1, :, :3]


def part_images(glb: Path):
    """{node name: {role: bytes}} for every mesh node of a GLB, from the material its primitive uses."""

    document, binary = _read_glb(glb)
    materials, textures = document.get("materials") or [], document.get("textures") or []
    result = {}
    for node in document.get("nodes", []):
        if "mesh" not in node:
            continue
        material = materials[document["meshes"][node["mesh"]]["primitives"][0].get("material", 0)]
        found = {}
        for role, (scope, key) in _SLOTS.items():
            holder = material.get("pbrMetallicRoughness", {}) if scope == "pbr" else material
            slot = holder.get(key)
            if isinstance(slot, dict) and isinstance(slot.get("index"), int):
                source = textures[slot["index"]].get("source")
                raw = _image_bytes(document, binary, glb, source) if isinstance(source, int) else None
                if raw:
                    found[role] = raw
        result[node["name"]] = found
    return result


def resize_rgb(tile, width: int, height: int):
    """Resample an (h, w, 3) uint8 tile to width x height with Blender's image scaler."""

    if tile.shape[1] == width and tile.shape[0] == height:
        return tile
    source_h, source_w = tile.shape[:2]
    image = bpy.data.images.new("tripo_resize", source_w, source_h, alpha=False)
    try:
        rgba = np.ones((source_h, source_w, 4), dtype=np.float32)
        rgba[:, :, :3] = tile[::-1].astype(np.float32) / 255.0
        image.pixels.foreach_set(rgba.ravel())
        image.scale(width, height)
        buffer = np.empty(width * height * 4, dtype=np.float32)
        image.pixels.foreach_get(buffer)
    finally:
        bpy.data.images.remove(image)
    pixels = np.clip(np.rint(buffer * 255.0), 0, 255).astype(np.uint8).reshape(height, width, 4)
    return pixels[::-1, :, :3]


def pack_atlas(meshes, source_glb: Path, folder: Path):
    """Put the parts' texture sets into one square atlas and remap each part's UVs into its cell.

    The part with the largest texture (the body) keeps seven eighths of the atlas side, and every
    other part (a weapon) gets a one-eighth cell at the edge (`lib.tripo.atlas_layout`). Tiles are
    resampled to their cells and nothing is baked. One material with the three atlas maps replaces
    the parts' materials.
    """

    images = part_images(source_glb)
    names = [obj.name for obj in meshes]
    missing = [name for name in names if name not in images]
    if missing:
        raise SystemExit(f"No texture set found for {missing}; the GLB meshes are {sorted(images)}")
    folder.mkdir(parents=True, exist_ok=True)
    # Empty atlas area: black, a flat normal, and matte (roughness 1) so it never counts as glossy in the packed specular map.
    written, tiles, fill = {}, {}, {"diffuse": (0, 0, 0), "normal": (128, 128, 255), "specular": (0, 255, 0)}
    for role in ROLE_FILES:
        have = [role in images[name] for name in names]
        if not any(have):
            continue
        if not all(have):
            raise SystemExit(f"Not every part has a {role} map: {dict(zip(names, have))}")
        tiles[role] = [decode_rgb(images[name][role]) for name in names]
    if "diffuse" not in tiles:
        raise SystemExit(f"{source_glb.name} embeds no base color map")
    sizes = [tile.shape[:2] for tile in tiles["diffuse"]]
    if any([tile.shape[:2] for tile in row] != sizes for row in tiles.values()):
        raise SystemExit("A part's maps differ in size between roles")
    layout = atlas_layout(sizes)
    side, rects = layout["size"], layout["rects"]
    for role, row in tiles.items():
        atlas = np.empty((side, side, 3), dtype=np.uint8)
        atlas[:, :] = fill[role]
        for tile, (x, y, width, height) in zip(row, rects):
            inner = resize_rgb(tile, width - 2 * ATLAS_GUTTER, height - 2 * ATLAS_GUTTER)
            padded = np.pad(inner, ((ATLAS_GUTTER, ATLAS_GUTTER), (ATLAS_GUTTER, ATLAS_GUTTER), (0, 0)), mode="edge")
            atlas[side - y - height : side - y, x : x + width] = padded
        write_png(folder / ROLE_FILES[role], side, side, atlas)
        if role == "specular":
            write_rm_siblings(folder, atlas)
        written[role] = ROLE_FILES[role]
    uv_ranges = {}
    for obj, (x, y, width, height) in zip(meshes, rects):
        layer = obj.data.uv_layers.active
        values = np.empty(len(layer.data) * 2, dtype=np.float32)
        layer.data.foreach_get("uv", values)
        us, vs = values[0::2], values[1::2]
        if min(us.min(), vs.min()) < -1e-4 or max(us.max(), vs.max()) > 1.0001:
            raise SystemExit(f"{obj.name} UVs leave [0, 1] ({us.min():.3f}..{us.max():.3f}, {vs.min():.3f}..{vs.max():.3f}); cannot pack an atlas")
        inner_w, inner_h = width - 2 * ATLAS_GUTTER, height - 2 * ATLAS_GUTTER
        values[0::2] = (x + ATLAS_GUTTER + np.clip(us, 0.0, 1.0) * inner_w) / side
        values[1::2] = (y + ATLAS_GUTTER + np.clip(vs, 0.0, 1.0) * inner_h) / side
        layer.data.foreach_set("uv", values)
        uv_ranges[obj.name] = [round(float(v), 5) for v in (values[0::2].min(), values[0::2].max(), values[1::2].min(), values[1::2].max())]
    material = bpy.data.materials.new("unit_atlas")
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = nodes["Principled BSDF"]

    def texture(role, colour):
        image = bpy.data.images.load(str(folder / ROLE_FILES[role]))
        image.colorspace_settings.name = "sRGB" if colour else "Non-Color"
        image.pack()
        node = nodes.new("ShaderNodeTexImage")
        node.image = image
        return node

    links.new(texture("diffuse", True).outputs["Color"], shader.inputs["Base Color"])
    if "normal" in written:
        normal = nodes.new("ShaderNodeNormalMap")
        links.new(texture("normal", False).outputs["Color"], normal.inputs["Color"])
        links.new(normal.outputs["Normal"], shader.inputs["Normal"])
    if "specular" in written:
        split = nodes.new("ShaderNodeSeparateColor")
        links.new(texture("specular", False).outputs["Color"], split.inputs["Color"])
        links.new(split.outputs["Green"], shader.inputs["Roughness"])
        links.new(split.outputs["Blue"], shader.inputs["Metallic"])
    for obj in meshes:
        obj.data.materials.clear()
        obj.data.materials.append(material)
        for polygon in obj.data.polygons:
            polygon.material_index = 0
    return {"textures": written, "parts": names, "atlas_size": [side, side], "part_sizes": [list(size) for size in sizes], "rects": [list(rect) for rect in rects], "uv_ranges_u_min_max_v_min_max": uv_ranges}


def trimmed_copy(action, cap: int):
    """A copy of `action` cut to at most `cap` frames. It ends on the frame in [cap/2, cap] whose pose is
    closest to frame 0 (the best loop point); keys after it are dropped, none are added or moved."""

    curves = [fcurve for fcurve, _container in action_fcurves(action)]
    first = int(action.frame_range[0])
    if action.frame_range[1] - first <= cap:
        return action, None
    start = [fcurve.evaluate(first) for fcurve in curves]
    best, best_error = cap, None
    for frame in range(max(cap // 2, 1), cap + 1):
        error = sum((fcurve.evaluate(first + frame) - value) ** 2 for fcurve, value in zip(curves, start))
        if best_error is None or error < best_error:
            best, best_error = frame, error
    cut = action.copy()
    cut.name = action.name + ".trim"
    for fcurve, _container in action_fcurves(cut):
        points = fcurve.keyframe_points
        for index in reversed(range(len(points))):  # from the end: a removal invalidates later references
            if points[index].co.x > first + best + 1e-6:
                points.remove(points[index])
    return cut, {"from_frames": int(action.frame_range[1] - first), "to_frames": best, "loop_pose_error": round(best_error, 6)}


def export_glb(path: Path, objects, active, *, animated: bool):
    select_only(objects, active)
    properties = bpy.ops.export_scene.gltf.get_rna_type().properties
    options = {
        "filepath": str(path),
        "export_format": "GLB",
        "use_selection": True,
        "export_skins": animated,
        "export_animations": animated,
        "export_animation_mode": "ACTIVE_ACTIONS",
        # The base model carries the maps; a clip's GLB only needs mesh, skin and animation (as Meshy's rig GLBs).
        "export_image_format": "AUTO" if not animated else "NONE",
    }
    bpy.ops.export_scene.gltf(**{key: value for key, value in options.items() if key in properties})


def glb_animations(path: Path):
    data = path.read_bytes()
    document = json.loads(data[20 : 20 + int.from_bytes(data[12:16], "little")])
    frames = []
    for animation in document.get("animations", []):
        counts = [document["accessors"][s["input"]]["count"] for s in animation["samplers"]]
        frames.append({"name": animation.get("name"), "frames": max(counts) if counts else 0})
    skins = document.get("skins", [])
    return frames, (len(skins[0]["joints"]) if skins else 0)


def name_glb_animation(path: Path, name: str):
    """Give the single animation of a GLB the Tripo clip's name (the exporter calls every one "Animation")."""

    data = path.read_bytes()
    json_length = int.from_bytes(data[12:16], "little")
    document = json.loads(data[20 : 20 + json_length])
    document["animations"][0]["name"] = name
    text = json.dumps(document, separators=(",", ":"), sort_keys=True).encode("utf-8")
    text += b" " * (-len(text) % 4)
    rest = data[20 + json_length :]
    total = 12 + 8 + len(text) + len(rest)
    path.write_bytes(data[:8] + total.to_bytes(4, "little") + len(text).to_bytes(4, "little") + data[16:20] + text + rest)


def main():
    args = parse_args()
    roles = dict(split_pair(item, "--roles item") for item in args.roles)
    rigid_parts = dict(split_pair(item, "--rigid-part") for item in args.rigid_part)
    twin = None
    if args.rigid_from_twin:
        twin_part, twin_bone = split_pair(args.rigid_from_twin[1], "--rigid-from-twin")
        twin = (Path(args.rigid_from_twin[0]), twin_part, twin_bone)
    for bone in list(rigid_parts.values()) + ([twin[2]] if twin else []):
        if bone not in KIT_NAMES:
            raise SystemExit(f"Weapon bone {bone!r} is not a kit bone name: {sorted(KIT_NAMES)}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_glb(args.rigged)
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(armatures) != 1:
        raise SystemExit(f"Expected one armature in {args.rigged.name}, found {len(armatures)}")
    armature = armatures[0]
    meshes = skinned_meshes(armature)
    if not meshes:
        raise SystemExit(f"{args.rigged.name} has no skinned mesh")
    ignored = []
    for obj in [o for o in bpy.data.objects if o.type == "MESH" and o not in meshes]:
        ignored.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)

    # Weapon vertices, decided on the untouched mesh.
    twin_report, twin_flags = None, {}
    if twin:
        twin_flags, twin_report = classify_from_twin(meshes, twin[0], twin[1])
    rigid_for = {}  # object name -> (kit bone, per-vertex weapon flags)
    for obj in meshes:
        count = len(obj.data.vertices)
        for part, bone in rigid_parts.items():
            if obj.name == part or obj.name.startswith(part + "."):
                rigid_for[obj.name] = (bone, [True] * count)
        if twin and obj.name not in rigid_for:
            rigid_for[obj.name] = (twin[2], twin_flags[obj.name])
    unmatched = [part for part in rigid_parts if not any(o.name == part or o.name.startswith(part + ".") for o in meshes)]
    if unmatched:
        raise SystemExit(f"--rigid-part names no mesh: {unmatched}; meshes are {[o.name for o in meshes]}")

    # Bones: keep the kit's, merge the rest into their nearest kept parent, then rename.
    bones_before = len(armature.data.bones)
    keep = {b.name: KIT_BONES[short_name(b.name)] for b in armature.data.bones if short_name(b.name) in KIT_BONES}
    if len(keep) != len(KIT_NAMES):
        raise SystemExit(f"The rig lacks kit bones: {sorted(KIT_NAMES - set(keep.values()))}")
    merge_into = {}
    for bone in armature.data.bones:
        target = kept_ancestor(bone, keep)
        if target is None:
            raise SystemExit(f"Bone {bone.name} has no kept ancestor")
        merge_into[bone.name] = keep[target.name]
    dropped = sorted(name for name in merge_into if name not in keep)
    all_weights = {obj.name: read_weights(obj) for obj in meshes}

    clip_names = {action.name for action in bpy.data.actions}
    print("TRIPO_CLIPS " + json.dumps(sorted(clip_names)), file=sys.stderr)
    try:
        roles = {role: resolve_clip_name(clip, clip_names) for role, clip in roles.items()}
    except ValueError as problem:
        raise SystemExit(str(problem))
    for action in bpy.data.actions:
        for fcurve, container in action_fcurves(action):
            if bone_of_path(fcurve.data_path) in set(dropped):
                container.remove(fcurve)

    select_only([armature], armature)
    bpy.ops.object.mode_set(mode="EDIT")
    for name in dropped:
        edit_bones = armature.data.edit_bones
        edit_bones.remove(edit_bones[name])
    bpy.ops.object.mode_set(mode="OBJECT")
    for old, new in keep.items():
        armature.data.bones[old].name = new
    for action in bpy.data.actions:
        for fcurve, _container in action_fcurves(action):
            old = bone_of_path(fcurve.data_path)
            if old in keep:
                fcurve.data_path = fcurve.data_path.replace(f'pose.bones["{old}"]', f'pose.bones["{keep[old]}"]', 1)
    bone_names = [b.name for b in armature.data.bones]
    if len(bone_names) > MAX_BONES or set(bone_names) != KIT_NAMES:
        raise SystemExit(f"Bone set wrong after the merge: {bone_names}")

    weapon_summary = []
    weapon_points = []
    for obj in meshes:
        bone, flags = rigid_for.get(obj.name, ("", [False] * len(obj.data.vertices)))
        rewrite_weights(obj, all_weights[obj.name], bone_names, merge_into, bone, flags)
        if bone:
            weapon_points.extend(obj.matrix_world @ v.co for v, flag in zip(obj.data.vertices, flags) if flag)
            weapon_summary.append({
                "object": obj.name, "bone": bone, "vertices": sum(flags), "of": len(flags),
                "connected_groups": connected_weapon_parts(obj, flags)[:5],
            })

    separated = separate_coincident_weapon_vertices(meshes, rigid_for) if rigid_for else 0

    # Several parts (a segmented export): one atlas and one material, then join into one mesh.
    body = meshes[0]
    atlas = None
    if len(meshes) > 1:
        atlas = pack_atlas(meshes, args.rigged, args.out_dir / f"{args.base_name}_textures")
        select_only(meshes, body)
        bpy.ops.object.join()
    body.name = "unit"
    materials = [slot.material.name for slot in body.material_slots if slot.material]

    # Base model: the mesh alone in the rest pose.
    armature.data.pose_position = "REST"
    if armature.animation_data:
        armature.animation_data.action = None
    textures = atlas["textures"] if atlas else write_textures(args.rigged, args.out_dir / f"{args.base_name}_textures")
    base_path = args.out_dir / f"{args.base_name}.glb"
    export_glb(base_path, [body], body, animated=False)
    armature.data.pose_position = "POSE"

    # One GLB per role: mesh, the shared armature and exactly one clip.
    clips = {}
    trims = dict(split_pair(item, "--trim") for item in args.trim)
    for role, clip in roles.items():
        action, trimmed = bpy.data.actions[clip], None
        if role in trims:
            action, trimmed = trimmed_copy(action, int(trims[role]))
        armature.animation_data_create()
        armature.animation_data.action = action
        slots = getattr(action, "slots", None)
        if slots is not None and len(slots):
            armature.animation_data.action_slot = slots[0]
        role_path = args.out_dir / (args.role_name.format(role=role) + ".glb")
        export_glb(role_path, [armature, body], armature, animated=True)
        name_glb_animation(role_path, safe_animation_name(clip))
        animations, joints = glb_animations(role_path)
        if len(animations) != 1:
            raise SystemExit(f"{role_path.name} holds {len(animations)} animations, expected exactly one")
        clips[role] = {
            "clip": clip,
            "file": role_path.name,
            "animation_name": animations[0]["name"],
            "frames": animations[0]["frames"],
            "action_frame_range": [float(v) for v in action.frame_range],
            "trimmed": trimmed,
            "joints": joints,
        }

    report = {
        "tool": "prepare_tripo_unit",
        "blender": bpy.app.version_string,
        "input": args.rigged.name,
        "ignored_objects": ignored,
        "clips_in_file": sorted(clip_names),
        "bones_before": bones_before,
        "bones_after": len(bone_names),
        "bone_names": bone_names,
        "dropped_bones": len(dropped),
        "weapon": weapon_summary,
        "weapon_vertices_separated_from_body": separated,
        "twin": twin_report,
        "materials": materials,
        "atlas": atlas,
        "triangles": sum(len(p.vertices) - 2 for p in body.data.polygons),
        "vertices": len(body.data.vertices),
        "base": base_path.name,
        "textures": textures,
        "clips": clips,
    }
    print(json.dumps(report, sort_keys=True))
    if args.report:
        detail = dict(report, weapon_points=[[round(c, 6) for c in p] for p in weapon_points])
        args.report.write_text(json.dumps(detail, indent=1, sort_keys=True) + "\n", encoding="utf-8")


try:
    main()
except SystemExit as failure:
    if failure.code not in (None, 0):
        # Blender exits 0 after a script's SystemExit; make the failure visible to the caller.
        sys.stdout.flush()
        print(f"prepare_tripo_unit failed: {failure.code}", file=sys.stderr)
        sys.stderr.flush()
        os._exit(1)
    raise
