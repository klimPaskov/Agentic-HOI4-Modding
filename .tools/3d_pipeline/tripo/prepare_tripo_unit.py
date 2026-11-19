"""Turn one Tripo rigged GLB into the Meshy-shaped provider files the unit route reads.

Run it headless, through the Blender the pipeline discovers (tripo_intake.py does this)::

    blender -b --factory-startup --python prepare_tripo_unit.py -- <rigged.glb> --out-dir <dir>
        --roles idle=idle move=walk attack=chop defend=hit_to_body_01 retreat=flee_01 death=fall
        [--rigid-part tripo_part_1=RightHand | --rigid-from-twin <segmented.glb> tripo_part_1=RightHand]

What it does, with no new keyframes (only the clips Tripo exported) except the chains' of step 5:

1. Drops meshes without vertex groups (Blender's glTF import adds a stray bone-shape Icosphere).
2. Renames the `mixamorig:*` bones to the names the kit expects (Spine1 -> Spine01, Spine2 -> Spine02,
   Neck -> neck) and merges every other bone (fingers, `*_End`) into its nearest kept parent: the weights
   are added to that parent and the bone and its channels are dropped. HOI4 allows 50 bones; 22 remain, and the
   `Weapon` and `Shield` bones of a separately modelled weapon and shield when the rig has them. A childless joint with no
   animation and no kept ancestor, which Tripo's auto-rig has added since November 2026 (`neutral_bone`), is dropped too and the
   weight it carries moves to the nearest kit bone by the vertex's position (lib/tripo_extra_joints.py); the report's
   `extra_joints` says which joints went and how many weights moved.
3. Binds a held weapon rigidly: every weapon vertex gets weight 1.0 on one hand bone. The weapon is a
   whole part (`--rigid-part`, for a segmented rigged export) or the vertices whose nearest vertex in a
   segmented twin of the same pose belongs to that part (`--rigid-from-twin`; both are first normalised
   to the same height, ground and centre). Every vertex keeps at most 4 weights, normalised to 1.
4. Writes `<base-name>.glb` (mesh only, the rest pose), `<base-name>_textures/{base_color,normal,
   metallic_roughness}.png` and one `<role-name>.glb` per role (mesh, the shared armature, exactly one
   animation: the Tripo clip named in `--roles`, in the clip's own frames).
5. With `--chains cloak wings`, adds bone chains to those regions after the parts are joined, rebinds them and keys them in every
   role clip after the arm level and before the snap easing (tripo/chain_stage.py; the rules are in lib/tripo_chains.py).

It prints one JSON line (it starts with `{"tool": "prepare_tripo_unit"`) and, with `--report`, writes
the same data plus the weapon vertex coordinates.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import struct
import sys
import tempfile
import zlib
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector, kdtree

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib.texture_lineage import ROLE_FILES, _SLOTS, _image_bytes, _read_glb, embedded_images
from lib import tripo_arms, tripo_extra_joints, tripo_loop, tripo_pose, tripo_shape, tripo_trim
from lib.tripo import atlas_layout, budget_list, decimate_ratio, parse_part_triangles, resolve_clip_name, safe_animation_name
from tripo import chain_stage

MAX_BONES = 50
# Texels of every atlas cell kept as a gutter: the tile is resampled inside it and its edge pixels are repeated
# into it, so filtering and mipmaps never mix a part's edge with its neighbour's cell.
ATLAS_GUTTER = 4
# A Tripo export without PBR maps (the separately modelled weapon, and a body exported without them) has no
# metallic-roughness map, which the kit's texture route requires. Its stand-in is constant: not metal, roughness 0.8.
NEUTRAL_ROUGHNESS = 204
MAX_INFLUENCES = 4

# Mixamo name (without the `mixamorig:` prefix) -> the kit's name. Every bone not named here is merged, and a joint with no kept ancestor
# (Tripo's `neutral_bone`) is dropped by the rule of lib/tripo_extra_joints.py.
KIT_BONES = dict(tripo_extra_joints.MIXAMO_KIT_BONES)
KIT_NAMES = set(KIT_BONES.values())
# The grip stage may add a bone for the separate weapon (a child of the hand), and the shield stage one for a shield held in the
# other hand (tripo/shield_stage.py); each is kept when the rig has it. With both the unit has 24 bones of HOI4's 50.
OPTIONAL_BONES = {"Weapon": "Weapon", "Shield": "Shield"}
KIT_BONES.update(OPTIONAL_BONES)


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
    parser.add_argument("--trim-end", action="append", default=[], metavar="ROLE=FRAMES",
                        help="cut a clip to exactly FRAMES frames (no loop point is searched): the end of a clip that goes still, "
                        "found by lib/tripo_trim.py")
    parser.add_argument("--loop-window", action="append", default=[], metavar="ROLE=FIRST:LAST",
                        help="cut a clip to the frames FIRST to LAST (offsets from its first frame): the window of whole strides whose end "
                        "continues into its start, found by lib/tripo_loop.py")
    parser.add_argument("--loop-close", nargs="*", default=[], metavar="ROLE",
                        help="in these roles (a looped gait: move, retreat) close the seam by adding the last-to-first turn over the last frames "
                        "on top of the motion, with no frames appended and no stop (lib/tripo_loop.py); it replaces --settle for them")
    parser.add_argument("--part-triangles", action="append", default=[], metavar="PART=N|auto",
                        help="reduce a part to about N triangles (weld, then Blender Decimate, UVs kept) before it is bound; "
                        "auto tries 1500, 2500, 4000 and keeps the first that passes the shape check")
    parser.add_argument("--shape-iou", type=float, default=tripo_shape.MIN_IOU,
                        help="the least silhouette agreement (front, side, top; intersection over union) a reduced part must keep")
    parser.add_argument("--ease-snaps", nargs="?", type=float, const=20.0, default=None, metavar="DEGREES", help="ease a joint turn faster than DEGREES per frame (default 20) over more frames, to three quarters of that, in every role clip, and keep each bone's quaternions on one hemisphere, so the kit's UNIT-ANIM-SPIN check does not fail a clip for one fast frame (the kit retimes 24 fps clips to 30 and a step can double)")
    parser.add_argument("--arm-level", nargs="*", default=[], metavar="ROLE",
                        help="in these role clips bring the hands to chest height with one constant rotation of both upper arms (lib/tripo_arms.py): "
                        "Tripo's text-to-motion attacks keep the hands over the head and hide it")
    parser.add_argument("--arm-level-high", nargs="*", default=[], metavar="ROLE",
                        help="as --arm-level, but only for a clip whose hands are high as cut (it fails TRIPO-HANDS-HIGH, lib/tripo_arms.hands_high): "
                        "an unarmed reaching walk that holds the hands over the head")
    # Default 0.85: chest height (0) read as dangling arms on the zombie; 0.85 of the way from chest to shoulder gives the arms straight forward
    # at shoulder height, the classic zombie reach.
    parser.add_argument("--arm-level-target", type=float, default=0.85, help="the hands' target height for --arm-level: 0 halfway between shoulders and hips (chest), 1 shoulder height")
    parser.add_argument("--chains", nargs="*", default=[], metavar="REGION",
                        help="add bone chains to these regions (cloak, wings), rebind them and key them per role by rule (tripo/chain_stage.py, lib/tripo_chains.py)")
    parser.add_argument("--settle", nargs="*", default=[], metavar="ROLE",
                        help="in these roles, append frames that blend every bone from the last pose back to frame 1, so the looped clip does not pop (lib/tripo_trim.py)")
    parser.add_argument("--untwist", nargs="*", default=[], metavar="ROLE",
                        help="in these roles, turn the spine back where the shoulders twist against the hips past vanilla's worst for the role (lib/tripo_pose.py)")
    parser.add_argument("--report", type=Path)
    argv =sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
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
    def in_part(o):
        return o.name == part or o.name.startswith(part + ".") or o.data.name == part

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


def part_arrays(obj):
    """World-space vertex positions (V, 3) and triangle vertex indices (T, 3) of a mesh object, as numpy arrays."""

    mesh = obj.data
    positions = np.empty(len(mesh.vertices) * 3)
    mesh.vertices.foreach_get("co", positions)
    positions = positions.reshape(-1, 3) @ np.array(obj.matrix_world)[:3, :3].T + np.array(obj.matrix_world)[:3, 3]
    mesh.calc_loop_triangles()
    triangles = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", triangles)
    return positions, triangles.reshape(-1, 3)


def weld_by_position(obj):
    """Merge vertices that share a position. UVs live on the face corners, so they are kept."""

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    size = max(max(v.co[axis] for v in bm.verts) - min(v.co[axis] for v in bm.verts) for axis in range(3))
    before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=size * 1e-5)
    merged = before - len(bm.verts)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return merged


def decimate_part(obj, armature, budget, min_iou: float):
    """Reduce `obj` to a triangle budget without breaking its shape; fail the stage when no budget keeps it.

    A mesh split along its UV seams has one shell per UV island, and collapsing the islands separately
    tears the part into floating fragments (19 shells from one on Tripo's axe at 1500 triangles). So the
    vertices are welded by position first (the UVs stay on the face corners), then collapse-decimated with
    the armature modifier off. `budget` is a number or "auto" (the first of 1500, 2500, 4000 that passes).
    Every attempt is checked by `lib.tripo_shape`: the shell count must not grow and the front, side and top
    silhouettes must agree with the original to `min_iou`. Returns the receipt, or None when the part is
    already within the (single) budget.
    """

    budgets = budget_list(budget)
    before = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if budget != "auto" and decimate_ratio(before, budgets[0]) is None:
        return None
    original = part_arrays(obj)
    for modifier in [m for m in obj.modifiers if m.type == "ARMATURE"]:
        obj.modifiers.remove(modifier)
    select_only([obj], obj)
    source = obj.data
    attempts, chosen = [], None
    for candidate in budgets:
        obj.data = source.copy()
        merged = weld_by_position(obj)
        ratio = decimate_ratio(sum(len(p.vertices) - 2 for p in obj.data.polygons), candidate)
        if ratio is not None:
            decimate = obj.modifiers.new("tripo_decimate", "DECIMATE")
            decimate.decimate_type = "COLLAPSE"
            decimate.ratio = ratio
            decimate.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=decimate.name)
        report = tripo_shape.shape_report(original, part_arrays(obj))
        problems = tripo_shape.shape_problems(report, min_iou)
        attempts.append({"budget": candidate, "triangles": report["triangles_after"], "welded_vertices": merged, "shells": report["shells_after"]["shells"],
                         "iou": report["iou"], "problems": problems})
        if not problems:
            chosen = attempts[-1]
            break
    if chosen is None:
        table = "; ".join(f"{a['budget']}: shells {a['shells']}, IoU {a['iou']}, {a['problems'][0]}" for a in attempts)
        raise SystemExit(f"Reducing {obj.name} broke its shape at every budget tried ({table}). Raise the budget or lower --shape-iou.")
    skin = obj.modifiers.new("Armature", "ARMATURE")
    skin.object = armature
    return {"from": before, "to": chosen["triangles"], "budget": chosen["budget"], "min_iou": min_iou, "shape": report, "attempts": attempts}


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


# Empty atlas area: black, a flat normal, and matte (roughness 1) so it never counts as glossy in the packed specular map.
ATLAS_FILL = {"diffuse": (0, 0, 0), "normal": (128, 128, 255), "specular": (0, 255, 0)}


def atlas_tiles(images, names):
    """Per role, each part's decoded tile (None where a part lacks that map), and the parts that get a neutral stand-in per role."""

    tiles, neutral_parts = {}, {}
    for role in ROLE_FILES:
        have = [role in images[name] for name in names]
        if not any(have):
            continue
        if not all(have) and role == "diffuse":
            raise SystemExit(f"Not every part has a base color map: {dict(zip(names, have))}")
        # A part without a normal or metallic-roughness map (a separately modelled weapon) gets the neutral
        # stand-in in its cell: a flat normal, or not metal with roughness 0.8, at the size of its base color.
        tiles[role] = [decode_rgb(images[name][role]) if images[name].get(role) else None for name in names]
        if not all(have):
            neutral_parts.setdefault(role, [n for n, ok in zip(names, have) if not ok])
    return tiles, neutral_parts


def write_atlas_maps(tiles, rects, side: int, folder: Path):
    """Write one atlas PNG per role (and the constant specular map when no part has one). Returns ({role: file}, neutral_specular)."""

    written = {}
    for role, row in tiles.items():
        atlas = np.empty((side, side, 3), dtype=np.uint8)
        atlas[:, :] = ATLAS_FILL[role]
        stand_in = (0, NEUTRAL_ROUGHNESS, 0) if role == "specular" else ATLAS_FILL[role]
        for tile, (x, y, width, height) in zip(row, rects):
            if tile is None:
                tile = np.empty((height, width, 3), dtype=np.uint8)
                tile[:, :] = stand_in
            inner = resize_rgb(tile, width - 2 * ATLAS_GUTTER, height - 2 * ATLAS_GUTTER)
            padded = np.pad(inner, ((ATLAS_GUTTER, ATLAS_GUTTER), (ATLAS_GUTTER, ATLAS_GUTTER), (0, 0)), mode="edge")
            atlas[side - y - height : side - y, x : x + width] = padded
        write_png(folder / ROLE_FILES[role], side, side, atlas)
        if role == "specular":
            write_rm_siblings(folder, atlas)
        written[role] = ROLE_FILES[role]
    neutral_specular = "specular" not in tiles
    if neutral_specular:
        constant = np.zeros((side, side, 3), dtype=np.uint8)
        constant[:, :, 1] = NEUTRAL_ROUGHNESS
        write_png(folder / ROLE_FILES["specular"], side, side, constant)
        write_rm_siblings(folder, constant)
        written["specular"] = ROLE_FILES["specular"]
    return written, neutral_specular


def remap_atlas_uvs(meshes, rects, side: int):
    """Move each part's UVs into its atlas cell (inside the gutter). Returns each part's new UV range."""

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
    return uv_ranges


def atlas_material(meshes, folder: Path, written):
    """One material with the atlas maps, given to every part."""

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
    tiles, neutral_parts = atlas_tiles(images, names)
    if "diffuse" not in tiles:
        raise SystemExit(f"{source_glb.name} embeds no base color map")
    sizes = [tile.shape[:2] for tile in tiles["diffuse"]]
    # A part's normal and metallic-roughness maps may be smaller or larger than its diffuse (a separately
    # modelled weapon often is): every tile is resampled to its cell anyway, so only the diffuse sizes lay out the atlas.
    map_sizes = {role: [list(tile.shape[:2]) if tile is not None else None for tile in row] for role, row in tiles.items()}
    layout = atlas_layout(sizes)
    side, rects = layout["size"], layout["rects"]
    written, neutral_specular = write_atlas_maps(tiles, rects, side, folder)
    uv_ranges = remap_atlas_uvs(meshes, rects, side)
    atlas_material(meshes, folder, written)
    return {"textures": written, "parts": names, "atlas_size": [side, side], "part_sizes": [list(size) for size in sizes], "map_sizes": map_sizes, "neutral_specular": neutral_specular, "neutral_map_parts": neutral_parts, "rects": [list(rect) for rect in rects], "uv_ranges_u_min_max_v_min_max": uv_ranges}


def trimmed_copy(action, cap: int, exact: bool = False):
    """A copy of `action` cut to at most `cap` frames. It ends on the frame in [cap/2, cap] whose pose is
    closest to frame 0 (the best loop point), or on frame `cap` itself when `exact`; keys after it are dropped, none are added or moved."""

    curves = [fcurve for fcurve, _container in action_fcurves(action)]
    first = int(action.frame_range[0])
    if action.frame_range[1] - first <= cap:
        return action, None
    start = [fcurve.evaluate(first) for fcurve in curves]
    best, best_error = cap, None
    for frame in range(cap if exact else max(cap // 2, 1), cap + 1):
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


def windowed_copy(action, start: int, end: int):
    """A copy of `action` cut to the frames `start` to `end` (offsets from its first frame) and moved to begin where the action began. Keys
    outside the window are dropped, the two end frames of the window are keyed with the curve value there, and no other key is changed."""

    first = int(round(action.frame_range[0]))
    total = int(round(action.frame_range[1])) - first
    start, end = max(int(start), 0), min(int(end), total)
    if end - start < 2 or (start == 0 and end == total):
        return action, None
    cut = action.copy()
    cut.name = action.name + ".loop"
    low, high = first + start, first + end
    for fcurve, _container in action_fcurves(cut):
        ends = [(frame, fcurve.evaluate(frame)) for frame in (low, high)]
        points = fcurve.keyframe_points
        for index in reversed(range(len(points))):  # from the end: a removal invalidates later references
            if points[index].co.x < low - 1e-6 or points[index].co.x > high + 1e-6:
                points.remove(points[index])
        for frame, value in ends:
            if not any(abs(point.co.x - frame) < 1e-6 for point in fcurve.keyframe_points):
                fcurve.keyframe_points.insert(frame, value, options={"FAST"}).interpolation = "LINEAR"
        fcurve.update()  # sorts the keys by frame
        for point in fcurve.keyframe_points:  # in rising order, so no key passes another on the way down
            point.handle_left.x -= start
            point.handle_right.x -= start
            point.co.x -= start
        fcurve.update()
    return cut, {"from_frames": total, "to_frames": end - start, "window": [start, end]}


def sampled_turns(curves, first: int, last: int):
    """({bone: its quaternion at every frame}, the fastest bone turn at each frame step, the largest first-to-last turn, its bone)."""

    steps = np.zeros(max(last - first, 0))
    worst_turn, worst_bone, poses = 0.0, "", {}
    for bone, c in curves.items():
        q = [Quaternion([c[i].evaluate(first + k) for i in range(4)]).normalized() for k in range(last - first + 1)]
        for k in range(1, len(q)):
            steps[k - 1] = max(steps[k - 1], step_degrees(q[k - 1], q[k]))
        poses[bone] = q
        turn = step_degrees(q[0], q[-1])
        if turn > worst_turn:
            worst_turn, worst_bone = turn, bone
    return poses, steps, worst_turn, worst_bone


def add_closing_turn(c, q, weights, first: int, last: int) -> None:
    """Key one bone's last `len(weights)` frames with its own pose times a growing share of the turn from its last pose to its first."""

    start, end = q[0].copy(), q[-1]
    if start.dot(end) < 0:
        start.negate()
    turn = end.inverted() @ start  # in the frame of the bone: the last pose times it is the first pose
    if turn.w < 0:
        turn.negate()
    identity = Quaternion((1.0, 0.0, 0.0, 0.0))
    for k, w in enumerate(weights, start=1):
        frame = last - len(weights) + k
        posed = q[frame - first] @ identity.slerp(turn, float(w))
        if posed.dot(q[frame - first]) < 0:
            posed.negate()
        for i in range(4):
            c[i].keyframe_points.insert(frame, posed[i], options={"FAST"}).interpolation = "LINEAR"


def close_loop(action):
    """Close the seam of a looped gait with no stop (rule and numbers: lib/tripo_loop.py). Over the last frames every bone gets a growing
    share of the turn from its last pose to its first, on top of its own motion, and the hips get the same share of their offset, so the last
    frame is the first pose and the stride runs through. No frame is added. Returns the record (0 frames when the clip already closes)."""

    curves = rotation_curves(action)
    if not curves:
        return None
    first = int(round(action.frame_range[0]))
    last = int(round(action.frame_range[1]))
    poses, steps, worst_turn, worst_bone = sampled_turns(curves, first, last)
    rate = tripo_trim.settle_rate(steps)
    count = tripo_loop.close_frames(worst_turn, rate, last - first)
    place = [fcurve for fcurve, _container in action_fcurves(action) if fcurve.data_path.endswith(".location")]
    offsets = [fcurve.evaluate(first) - fcurve.evaluate(last) for fcurve in place]
    # The joints close but the hips end at another place (a bob cut mid-way): the shortest blend, when the offset is over 1% of the hips' largest travel along an axis.
    spans = [max(fcurve.evaluate(first + k) for k in range(last - first + 1)) - min(fcurve.evaluate(first + k) for k in range(last - first + 1)) for fcurve in place]
    if count == 0 and any(abs(offset) > 0.01 * max(spans) for offset in offsets):
        count = min(tripo_trim.SETTLE_MIN_FRAMES, (last - first) // 2)
    if count == 0:
        return {"frames_blended": 0, "turn_degrees": round(worst_turn, 1)}
    weights = tripo_loop.close_weights(count)
    for bone, c in curves.items():
        add_closing_turn(c, poses[bone], weights, first, last)
    for fcurve, offset in zip(place, offsets):
        values = [fcurve.evaluate(last - count + k) for k in range(1, count + 1)]
        for k, w in enumerate(weights, start=1):
            fcurve.keyframe_points.insert(last - count + k, values[k - 1] + offset * float(w), options={"FAST"}).interpolation = "LINEAR"
    for fcurve, _container in action_fcurves(action):
        fcurve.update()
    return {"frames_blended": count, "turn_degrees": round(worst_turn, 1), "worst_bone": worst_bone, "rate_degrees_per_frame": round(rate, 2),
            "first_blended_frame": last - count + 1 - first}


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


PREFIX = ""  # the bones are renamed to the kit's names before the keys are eased


def rotation_curves(action):
    """{bone: {component: fcurve}} of the quaternion rotation channels."""

    found = {}
    for fcurve, _c in action_fcurves(action):
        if fcurve.data_path.startswith("pose.bones[") and fcurve.data_path.endswith(".rotation_quaternion"):
            found.setdefault(fcurve.data_path.split('"')[1], {})[fcurve.array_index] = fcurve
    return {bone: curves for bone, curves in found.items() if len(curves) == 4}


def key_quaternions(curves):
    count = len(curves[0].keyframe_points)
    return [Quaternion([curves[i].keyframe_points[k].co.y for i in range(4)]) for k in range(count)]


def write_quaternions(curves, quaternions):
    for k, q in enumerate(quaternions):
        for i in range(4):
            point = curves[i].keyframe_points[k]
            point.co.y = q[i]
            point.handle_left.y = q[i]
            point.handle_right.y = q[i]
    for fcurve in curves.values():
        fcurve.update()


def step_degrees(a, b):
    return 2.0 * math.degrees(math.acos(min(1.0, abs(a.dot(b)))))


def normalise_rotation_keys(action, trigger_degrees=20.0, target_degrees=15.0, max_window=16):
    """Keep every bone's quaternions on one hemisphere and ease a snap over more frames.

    A step faster than `trigger_degrees` per frame is retimed along the bone's own path over a window of keys (`lib/tripo_ease.ease_turns`,
    the grip stage's rule): the smallest window, up to `max_window` keys either side, in which every step comes to `target_degrees` per
    frame or less. The bone passes through the same poses, so the raise or the end of a swing inside the window stays. Returns what was
    found: flips fixed, and per bone the fastest step before and after (degrees per frame) for the bones that had a flip or a step over
    the trigger.
    """

    from lib import tripo_ease

    out = {"flips_fixed": 0, "snaps_eased": {}}
    for bone, curves in rotation_curves(action).items():
        frames = [kp.co.x for kp in curves[0].keyframe_points]
        quats, flips = tripo_ease.one_hemisphere([np.array(q) for q in key_quaternions(curves)])
        before = max(tripo_ease.turn_rates(quats, frames), default=0.0)
        eased = []
        # The grip stage eases the weapon bone itself and keys a counter-turn against the hand. Easing it again
        # here breaks that counter-turn, and a dropped weapon bounced for three frames after landing.
        if bone.replace(PREFIX, "") not in OPTIONAL_BONES:
            quats, eased = tripo_ease.ease_turns(quats, frames, trigger_degrees, target_degrees, max_window)
        after = max(tripo_ease.turn_rates(quats, frames), default=0.0)
        out["flips_fixed"] += flips
        if flips or eased or before > trigger_degrees:
            out["snaps_eased"][bone.replace(PREFIX, "")] = {"flips": flips, "per_frame_before": round(before, 1), "per_frame_after": round(after, 1), "eased_frames": eased}
        write_quaternions(curves, [Quaternion([float(v) for v in q]) for q in quats])
    return out


def settle_to_first(action):
    """Append frames that blend every bone from the last pose back to frame 1 (rule and numbers: lib/tripo_trim.py).

    Rotation keys slerp, location keys blend linearly, both with a smoothstep. The rate and the length come from the clip's own motion. Returns the
    record, or None when the clip already ends in its first pose."""

    curves = rotation_curves(action)
    if not curves:
        return None
    first = int(round(action.frame_range[0]))
    last = int(round(action.frame_range[1]))
    steps = np.zeros(max(last - first, 0))
    worst_turn, worst_bone = 0.0, ""
    for bone, c in curves.items():
        q = [Quaternion([c[i].evaluate(first + k) for i in range(4)]).normalized() for k in range(last - first + 1)]
        for k in range(1, len(q)):
            steps[k - 1] = max(steps[k - 1], step_degrees(q[k - 1], q[k]))
        turn = step_degrees(q[0], q[-1])
        if turn > worst_turn:
            worst_turn, worst_bone = turn, bone
    count = tripo_trim.settle_frames(worst_turn, tripo_trim.settle_rate(steps))
    if count == 0:
        return {"frames_added": 0, "turn_degrees": round(worst_turn, 1)}
    weights = tripo_trim.settle_weights(count)
    for c in curves.values():
        start = Quaternion([c[i].evaluate(first) for i in range(4)]).normalized()
        end = Quaternion([c[i].evaluate(last) for i in range(4)]).normalized()
        if start.dot(end) < 0:
            start.negate()
        for k, w in enumerate(weights, start=1):
            q = end.slerp(start, float(w))
            for i in range(4):
                point = c[i].keyframe_points.insert(last + k, q[i], options={"FAST"})
                point.interpolation = "LINEAR"
    for fcurve, _container in action_fcurves(action):
        if fcurve.data_path.endswith(".location"):
            start, end = fcurve.evaluate(first), fcurve.evaluate(last)
            for k, w in enumerate(weights, start=1):
                point = fcurve.keyframe_points.insert(last + k, end + (start - end) * float(w), options={"FAST"})
                point.interpolation = "LINEAR"
    for fcurve, _container in action_fcurves(action):
        fcurve.update()
    return {"frames_added": count, "turn_degrees": round(worst_turn, 1), "worst_bone": worst_bone, "rate_degrees_per_frame": round(tripo_trim.settle_rate(steps), 2)}


def held_parts(armature, args):
    """[(part bone, hand bone, the other held bones)] for each held part (the weapon, then the shield) with its own bone under a hand."""

    bones = {item.partition("=")[2] for item in args.rigid_part}
    out = []
    for part in [b for b in ("Weapon", "Shield") if b in bones and b in armature.data.bones]:
        parent = armature.data.bones[part].parent
        if parent is not None:
            out.append((part, parent.name, sorted(b for b in bones if b != part and b in armature.data.bones)))
    return out


def held_and_body(body, weapon_bone, others):
    """(the held weapon's vertex mask, the body's mask, the body's triangles renumbered over its own vertices), or None when the weapon has under 50 vertices."""

    names = {g.index: g.name for g in body.vertex_groups}
    dominant = []
    for v in body.data.vertices:
        best = max(v.groups, key=lambda g: g.weight, default=None)
        dominant.append(names.get(best.group, "") if best else "")
    held = np.array([d == weapon_bone for d in dominant])
    other = np.array([d in others for d in dominant])
    if held.sum() < 50:
        return None
    mesh = body.data
    mesh.calc_loop_triangles()
    tri = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", tri)
    tri = tri.reshape(-1, 3)
    keep = ~(held | other)
    return held, keep, (np.cumsum(keep) - 1)[tri[keep[tri].all(axis=1)]]


def evaluated_world(body) -> np.ndarray:
    """The body's vertices as the armature poses them now, in world space."""

    owner = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data = owner.to_mesh()
    out = np.empty(len(data.vertices) * 3)
    data.vertices.foreach_get("co", out)
    owner.to_mesh_clear()
    matrix = np.array(body.matrix_world)
    return out.reshape(-1, 3) @ matrix[:3, :3].T + matrix[:3, 3]


def clear_settled_weapon(armature, body, action, first_frame, last_frame, args):
    """Keep every held part out of the body in the frames `settle_to_first` appended: `clear_settled_part` for the weapon, then the shield.
    Returns the weapon's record (with the shield's under "Shield"), or None when the unit holds no part on its own bone."""

    records = {}
    for found in held_parts(armature, args):
        record = clear_settled_part(armature, body, action, first_frame, last_frame, found)
        if record is not None:
            records[found[0]] = record
    if not records:
        return None
    first = dict(records.pop(next(iter(records))))
    first.update(records)
    return first


def clear_settled_part(armature, body, action, first_frame, last_frame, found):
    """Keep one held part out of the body in the frames `settle_to_first` appended (lib/tripo_clearance.py, the grip stage's rule).

    The grip stage cleared the clip as Tripo made it. The settle then blends every bone, the hand included, from the last pose to the first, and
    the straight blend of two clear poses swings the weapon through the torso (the round 4 ogre's club: 9 frames, up to 9.1% of its points).
    So the clearance runs again on the frames from the clip's old end on, and turns the hand about the wrist where the part is inside the body.
    A shield needs it as much as a weapon: the round 4 dwarf's attack kept its shield 4.9% in the body in the last settled frame.
    `found` is (part bone, hand bone, the other held bones). Returns the record, or None when the part has under 50 vertices."""

    if last_frame <= first_frame:
        return None
    weapon_bone, hand, others = found
    from lib import tripo_clearance as CL

    split = held_and_body(body, weapon_bone, others)
    if split is None:
        return None
    held, keep, triangles = split
    scene = bpy.context.scene
    assign_action(armature, action)
    start = max(first_frame - CL.HOLD_FRAMES, int(round(action.frame_range[0])))  # a few frames of the old clip too, so the turns fade in
    frames = list(range(start, last_frame + 1))
    weapon_frames, body_frames, pivots = [], [], []
    for frame in frames:
        scene.frame_set(frame)
        points = evaluated_world(body)
        weapon_frames.append(points[held])
        body_frames.append(points[keep])
        pivots.append(np.array(armature.matrix_world @ armature.pose.bones[hand].head))
    height = float(max(f[:, 2].max() - f[:, 2].min() for f in body_frames[:1]))
    result = CL.clear_clip(weapon_frames, pivots, body_frames, triangles, height)
    inverse = armature.matrix_world.inverted()
    for index, frame in enumerate(frames):
        vector = result["rotvecs"][index]
        angle = float(np.linalg.norm(vector))
        if angle < 1e-6:
            continue
        scene.frame_set(frame)
        bone = armature.pose.bones[hand]
        axis = (inverse.to_3x3() @ Vector(vector / angle)).normalized()
        pivot = inverse @ Vector(pivots[index])
        bone.matrix = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-pivot) @ bone.matrix
        bpy.context.view_layer.update()
        bone.keyframe_insert("rotation_quaternion", frame=frame)
    for fcurve, _container in action_fcurves(action):
        fcurve.update()
    return {"hand": hand, "frames_judged": len(frames), "frames_changed": result["frames_changed"], "max_degrees": round(result["max_degrees"], 1),
            "worst_share_before": round(max(result["before"]), 4), "worst_share_after": round(max(result["after"]), 4),
            "failed_frames": [frames[i] for i in result["failed"]]}


ARM_BONES = ("LeftArm", "RightArm")
TRACKED_JOINTS = ("LeftHand", "RightHand", "LeftArm", "RightArm", "Head", "Hips")


def assign_action(armature, action):
    armature.animation_data_create()
    armature.animation_data.action = action
    slots = getattr(action, "slots", None)
    if slots is not None and len(slots):
        armature.animation_data.action_slot = slots[0]


def joint_head(armature, name):
    return np.array(armature.matrix_world @ armature.pose.bones[name].head)


def track_joints(armature, frames):
    """{joint: (frames, 3) world head positions} for the arm-level joints."""

    scene = bpy.context.scene
    tracks = {name: [] for name in TRACKED_JOINTS}
    for frame in frames:
        scene.frame_set(frame)
        for name in tracks:
            tracks[name].append(joint_head(armature, name))
    return {name: np.array(values) for name, values in tracks.items()}


def arm_levels(armature, frames, reach, front, standing, up, target_share):
    """The hand levels of the clip as it is now, plus the mean error to chest height and the forward reach over the reach phase."""

    now = track_joints(armature, frames)
    levels = tripo_arms.hand_levels(now["LeftHand"], now["RightHand"], now["LeftArm"], now["RightArm"], now["Head"], up)
    mid = 0.5 * (now["LeftHand"] + now["RightHand"])
    chest = tripo_arms.chest_height(0.5 * (now["LeftArm"] + now["RightArm"]), now["Hips"], up, target_share)
    levels["mean_error_in_reach"] = float(np.mean(mid[reach, up] - chest[reach]))
    levels["forward_in_reach"] = float(np.mean((mid[reach] - now["Hips"][reach]) @ front)) / max(standing, 1e-9)
    return levels


def turned_hand_heights(armature, frames, sample, arm_quaternions, chest, angles, axis, up):
    """Mean over the sampled reach frames of each hand's height minus the chest's, with arm k turned by angles[k] about `axis`."""

    scene = bpy.context.scene
    bones = armature.pose.bones
    out = np.zeros(2)
    for frame in sample:
        scene.frame_set(int(frames[frame]))
        for k, name in enumerate(ARM_BONES):
            bones[name].rotation_quaternion = arm_quaternions[name][frame] @ Quaternion(axis, angles[k])
        bpy.context.view_layer.update()
        for k, hand in enumerate(("LeftHand", "RightHand")):
            out[k] += joint_head(armature, hand)[up] - chest[frame]
    return out / len(sample)


def level_arms(armature, action, up=2, target_share=0.0, only_when_high=False):
    """Solve and apply the arm-level rotation to the role clip `action` (see lib/tripo_arms.py). Returns what was done.

    Both upper arms (LeftArm, RightArm) get the same constant additive rotation, about the bone-local axis that moves the hands up
    and down most (the sign per arm so a positive angle raises that hand), multiplied into every key: q_new = q_clip @ q_offset. The
    angle is solved so that the mean hand height over the reach phase equals chest height, halfway between the shoulders and the hips.
    """

    scene = bpy.context.scene
    assign_action(armature, action)
    start, end = int(action.frame_range[0]), int(action.frame_range[1])
    frames = list(range(start, end + 1))
    bones = armature.pose.bones
    arm_quaternions = {name: [] for name in ARM_BONES}
    for frame in frames:
        scene.frame_set(frame)
        for name in ARM_BONES:
            arm_quaternions[name].append(Quaternion(bones[name].rotation_quaternion))
    track = track_joints(armature, frames)
    scene.frame_set(start)
    rest_foot = np.array(armature.matrix_world @ armature.data.bones["LeftFoot"].head_local)
    rest_toe = np.array(armature.matrix_world @ armature.data.bones["LeftToeBase"].head_local)
    front = rest_toe - rest_foot
    front[up] = 0.0
    front = front / max(float(np.linalg.norm(front)), 1e-9)
    standing = float(track["Head"][0, up])
    hand_mid = 0.5 * (track["LeftHand"] + track["RightHand"])
    shoulder_mid = 0.5 * (track["LeftArm"] + track["RightArm"])
    reach = tripo_arms.reach_frames(hand_mid, track["Hips"], front)
    chest = tripo_arms.chest_height(shoulder_mid, track["Hips"], up, target_share)
    before = arm_levels(armature, frames, reach, front, standing, up, target_share)
    if only_when_high and not tripo_arms.hands_high(before):
        # --arm-level-high: a gait whose hands stay down keeps its arms
        return {"applied": False, "why": "the hands are not high (TRIPO-HANDS-HIGH passes)", "before": {k: round(v, 3) for k, v in before.items()}}
    axes = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    sample = reach[:: max(1, len(reach) // 12)]

    def heights(angles, axis):
        return turned_hand_heights(armature, frames, sample, arm_quaternions, chest, angles, axis, up)

    slopes = [(heights((0.15, 0.15), axis) - heights((-0.15, -0.15), axis)) / 0.3 for axis in axes]
    axis_index = int(np.argmax([float(np.sum(np.abs(v))) for v in slopes]))
    axis = axes[axis_index]
    signs = np.where(slopes[axis_index] >= 0, 1.0, -1.0)
    angle, left = tripo_arms.solve_arm_offset(lambda value: float(np.mean(heights(tuple(signs * value), axis))), tolerance=0.002 * max(standing, 1e-9))
    for k, name in enumerate(ARM_BONES):
        curves = rotation_curves(action).get(name)
        if curves is None:
            continue
        offset = Quaternion(axis, float(signs[k] * angle))
        write_quaternions(curves, [q @ offset for q in key_quaternions(curves)])
    scene.frame_set(start)
    after = arm_levels(armature, frames, reach, front, standing, up, target_share)
    return {
        "applied": True, "axis": axis_index, "signs": [float(v) for v in signs], "degrees": round(math.degrees(angle), 1), "error_left": round(left, 4),
        "reach_frames": [int(frames[i]) for i in (reach[0], reach[-1])], "before": {k: round(v, 3) for k, v in before.items()},
        "after": {k: round(v, 3) for k, v in after.items()},
    }


SPINE_BONES = ("Spine", "Spine01", "Spine02")
SHOULDER_JOINTS = ("LeftArm", "RightArm")
FEET = (("LeftFoot", "LeftToeBase"), ("RightFoot", "RightToeBase"))


def body_height(body, up=2):
    """The skinned body's rest-pose height in world units (its mesh data, not the posed evaluation, along the up axis)."""

    count = len(body.data.vertices)
    local = np.empty(count * 3)
    body.data.vertices.foreach_get("co", local)
    world = np.array(body.matrix_world)
    points = local.reshape(-1, 3) @ world[:3, :3].T + world[:3, 3]
    return max(float(np.ptp(points[:, up])), 1e-6) if count else 1.0


def stance_tracks(armature, frames, height, up=2):
    """The stance twist (lib/tripo_pose.stance_twist_tracks) of the assigned action at `frames`: the shoulder line against the way the
    standing feet point, NaN where a foot does not stand. Each foot's turn is its pose bone's armature-space rotation against its rest."""

    scene = bpy.context.scene
    world = armature.matrix_world
    bones = armature.data.bones
    rest = {name: np.array(world @ bones[name].head_local) for name in SHOULDER_JOINTS + tuple(j for foot in FEET for j in foot)}
    shoulders = {name: [] for name in SHOULDER_JOINTS}
    rotations = {foot: [] for foot, _toe in FEET}
    lifts = {foot: [] for foot, _toe in FEET}
    torso = []  # the hips to the chest: a body lying down has no stance (`tripo_pose.STANCE_UPRIGHT`)
    chest = "Spine02" if "Spine02" in bones else None
    rest_frames = {foot: (world @ bones[foot].matrix_local).to_3x3().normalized().inverted() for foot, _toe in FEET}
    for frame in frames:
        scene.frame_set(frame)
        for name in SHOULDER_JOINTS:
            shoulders[name].append(joint_head(armature, name))
        for foot, toe in FEET:
            posed = (world @ armature.pose.bones[foot].matrix).to_3x3().normalized()
            rotations[foot].append(np.array(posed @ rest_frames[foot]))
            lifts[foot].append(min(joint_head(armature, foot)[up] - rest[foot][up], joint_head(armature, toe)[up] - rest[toe][up]))
        if chest and "Hips" in bones:
            torso.append(np.asarray(joint_head(armature, chest)) - np.asarray(joint_head(armature, "Hips")))
    return tripo_pose.stance_twist_tracks(
        np.array(shoulders["LeftArm"]), np.array(shoulders["RightArm"]), rest["LeftArm"], rest["RightArm"],
        [np.array(rotations[foot]) for foot, _toe in FEET], [rest[toe] - rest[foot] for foot, toe in FEET],
        [np.array(lifts[foot]) for foot, _toe in FEET], up, height, np.array(torso) if torso else None)


def untwist_waist(armature, action, role, body, up=2):
    """Turn the spine back about the world up axis wherever the shoulders twist against the standing feet further than vanilla's worst
    for the role (lib/tripo_pose.VANILLA_WAIST_TWIST_DEGREES, TRIPO-WAIST-TWIST, the stance twist). Frames where a foot does not stand
    take the excess of the read frames around them (`tripo_pose.untwist_excess`). Per frame the excess is split evenly over
    `SPINE_BONES`; each bone's turn is about the up axis carried into its own pose space, so the turns add up and nothing below the waist
    moves. Returns the record, or None when the role has no target or the rig no spine."""

    target = tripo_pose.VANILLA_WAIST_TWIST_DEGREES.get(role)
    curves_of = rotation_curves(action)
    spine = [name for name in SPINE_BONES if name in curves_of]
    names = armature.data.bones
    if target is None or not spine or any(name not in names for name in SHOULDER_JOINTS + tuple(j for foot in FEET for j in foot)):
        return None
    scene = bpy.context.scene
    assign_action(armature, action)
    bones = armature.pose.bones
    keyed = [int(round(p.co.x)) for p in curves_of[spine[0]][0].keyframe_points]
    height = body_height(body, up)
    twist = stance_tracks(armature, keyed, height, up)
    read = ~np.isnan(twist)
    excess = tripo_pose.untwist_excess(twist, target)
    worst = round(float(np.nanmax(np.abs(twist))), 1) if read.any() else None
    if not np.any(excess):
        scene.frame_set(keyed[0])
        return {"target_degrees": target, "worst_before": worst, "frames_read": int(read.sum()), "frames_changed": 0}
    world_up = Vector((0.0, 0.0, 1.0))
    to_armature = armature.matrix_world.to_3x3().inverted()
    for name in spine:
        bone = bones[name]
        new = []
        for frame in (int(round(p.co.x)) for p in curves_of[name][0].keyframe_points):
            scene.frame_set(frame)
            # the bone's pose-space frame without its own key: armature-space rotation times the inverse of the key's rotation
            carrier = bone.matrix.to_3x3() @ bone.rotation_quaternion.to_matrix().inverted()
            axis = (carrier.inverted() @ (to_armature @ world_up)).normalized()
            angle = -math.radians(float(np.interp(frame, keyed, excess))) / len(spine)
            new.append(Quaternion(axis, angle) @ Quaternion(bone.rotation_quaternion))
        write_quaternions(curves_of[name], new)
    after = stance_tracks(armature, keyed, height, up)
    scene.frame_set(keyed[0])
    return {"target_degrees": target, "worst_before": worst, "frames_read": int(read.sum()), "frames_changed": int(np.count_nonzero(excess)),
            "largest_turn_back": round(float(np.abs(excess).max()), 1),
            "worst_after": round(float(np.nanmax(np.abs(after))), 1) if (~np.isnan(after)).any() else None}


def read_inputs(args):
    """The roles, the rigid parts and the twin from the command line, with the weapon bones checked against the kit's names."""

    roles = dict(split_pair(item, "--roles item") for item in args.roles)
    rigid_parts = dict(split_pair(item, "--rigid-part") for item in args.rigid_part)
    twin = None
    if args.rigid_from_twin:
        twin_part, twin_bone = split_pair(args.rigid_from_twin[1], "--rigid-from-twin")
        twin = (Path(args.rigid_from_twin[0]), twin_part, twin_bone)
    for bone in list(rigid_parts.values()) + ([twin[2]] if twin else []):
        if bone not in KIT_NAMES | set(OPTIONAL_BONES.values()):
            raise SystemExit(f"Weapon bone {bone!r} is not a kit bone name: {sorted(KIT_NAMES)}")
    return roles, rigid_parts, twin


def load_rig(path: Path):
    """Import the rigged GLB into an empty scene. Returns (armature, skinned meshes, names of the meshes dropped)."""

    bpy.ops.wm.read_factory_settings(use_empty=True)
    import_glb(path)
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(armatures) != 1:
        raise SystemExit(f"Expected one armature in {path.name}, found {len(armatures)}")
    armature = armatures[0]
    meshes = skinned_meshes(armature)
    if not meshes:
        raise SystemExit(f"{path.name} has no skinned mesh")
    ignored = []
    for obj in [o for o in bpy.data.objects if o.type == "MESH" and o not in meshes]:
        ignored.append(obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)
    return armature, meshes, ignored


def reduce_parts(meshes, armature, args):
    budgets = parse_part_triangles(args.part_triangles)
    unknown = [part for part in budgets if not any(m.name == part for m in meshes)]
    if unknown:
        raise SystemExit(f"--part-triangles names no mesh: {unknown}; meshes are {[m.name for m in meshes]}")
    return {obj.name: decimate_part(obj, armature, budgets[obj.name], args.shape_iou) for obj in meshes if obj.name in budgets}


def part_matches(obj, part: str) -> bool:
    return obj.name == part or obj.name.startswith(part + ".")


def weapon_flag_map(meshes, rigid_parts, twin):
    """{object name: (kit bone, per-vertex weapon flags)}, decided on the untouched mesh, and the twin's report."""

    twin_report, twin_flags = None, {}
    if twin:
        twin_flags, twin_report = classify_from_twin(meshes, twin[0], twin[1])
    rigid_for = {}
    for obj in meshes:
        count = len(obj.data.vertices)
        for part, bone in rigid_parts.items():
            if part_matches(obj, part):
                rigid_for[obj.name] = (bone, [True] * count)
        if twin and obj.name not in rigid_for:
            rigid_for[obj.name] = (twin[2], twin_flags[obj.name])
    unmatched = [part for part in rigid_parts if not any(part_matches(o, part) for o in meshes)]
    if unmatched:
        raise SystemExit(f"--rigid-part names no mesh: {unmatched}; meshes are {[o.name for o in meshes]}")
    return rigid_for, twin_report


def merge_plan(armature):
    """(kept bone -> kit name, every bone -> the kit bone it merges into, dropped bone names)."""

    keep = {b.name: KIT_BONES[short_name(b.name)] for b in armature.data.bones if short_name(b.name) in KIT_BONES}
    if not KIT_NAMES <= set(keep.values()):
        raise SystemExit(f"The rig lacks kit bones: {sorted(KIT_NAMES - set(keep.values()))}")
    parents = {bone.name: (bone.parent.name if bone.parent else None) for bone in armature.data.bones}
    animated = {bone_of_path(fcurve.data_path) for action in bpy.data.actions for fcurve, _container in action_fcurves(action)}
    try:
        extras = tripo_extra_joints.find_extra_joints(parents, set(keep), animated)
    except tripo_extra_joints.ExtraJointError as problem:
        raise SystemExit(str(problem)) from None
    merge_into = {}
    for bone in armature.data.bones:
        if bone.name in extras:
            continue
        target = kept_ancestor(bone, keep)
        merge_into[bone.name] = keep[target.name]
    return keep, merge_into, sorted([name for name in merge_into if name not in keep] + extras), extras


def move_extra_weights(armature, meshes, all_weights, keep, extras):
    """Move the weight of the extra joints (lib/tripo_extra_joints.py) to the kept kit bone nearest to each vertex, in the rest pose. Changes
    `all_weights` in place and returns how many vertex weights moved."""

    if not extras:
        return 0
    to_armature = armature.matrix_world.inverted()
    segments = {name: (tuple(armature.data.bones[name].head_local), tuple(armature.data.bones[name].tail_local))
                for name, kit in keep.items() if kit in KIT_NAMES}
    points = {obj.name: [tuple(to_armature @ (obj.matrix_world @ v.co)) for v in obj.data.vertices] for obj in meshes}
    limit = tripo_extra_joints.near_limit([p for rows in points.values() for p in rows])
    fallback = next(name for name, kit in keep.items() if kit == tripo_extra_joints.FALLBACK_BONE)
    return sum(tripo_extra_joints.move_extra_weights(all_weights[obj.name], extras, points[obj.name], segments, fallback, limit) for obj in meshes)


def resolve_roles(roles):
    clip_names = {action.name for action in bpy.data.actions}
    print("TRIPO_CLIPS " + json.dumps(sorted(clip_names)), file=sys.stderr)
    try:
        return clip_names, {role: resolve_clip_name(clip, clip_names) for role, clip in roles.items()}
    except ValueError as problem:
        raise SystemExit(str(problem)) from None


def drop_and_rename(armature, keep, dropped):
    """Remove the dropped bones and their channels, rename the kept ones to the kit's names. Returns the bone names."""

    dropped_set = set(dropped)
    for action in bpy.data.actions:
        for fcurve, container in action_fcurves(action):
            if bone_of_path(fcurve.data_path) in dropped_set:
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
    if len(bone_names) > MAX_BONES or set(bone_names) - set(OPTIONAL_BONES.values()) != KIT_NAMES:
        raise SystemExit(f"Bone set wrong after the merge: {bone_names}")
    return bone_names


def bind_meshes(meshes, all_weights, bone_names, merge_into, rigid_for):
    """Rewrite every mesh's weights (merged bones, rigid weapon). Returns (weapon summary, weapon vertex positions)."""

    weapon_summary, weapon_points = [], []
    for obj in meshes:
        bone, flags = rigid_for.get(obj.name, ("", [False] * len(obj.data.vertices)))
        rewrite_weights(obj, all_weights[obj.name], bone_names, merge_into, bone, flags)
        if bone:
            weapon_points.extend(obj.matrix_world @ v.co for v, flag in zip(obj.data.vertices, flags) if flag)
            weapon_summary.append({
                "object": obj.name, "bone": bone, "vertices": sum(flags), "of": len(flags),
                "connected_groups": connected_weapon_parts(obj, flags)[:5],
            })
    return weapon_summary, weapon_points


def join_parts(meshes, args):
    """Several parts (a segmented export): one atlas and one material, then join into one mesh named `unit`."""

    body = meshes[0]
    atlas = None
    if len(meshes) > 1:
        atlas = pack_atlas(meshes, args.rigged, args.out_dir / f"{args.base_name}_textures")
        select_only(meshes, body)
        bpy.ops.object.join()
    body.name = "unit"
    return body, atlas


def export_base(armature, body, args, atlas):
    """The base model: the mesh alone in the rest pose, and its texture sidecars. Returns (textures, base path)."""

    armature.data.pose_position = "REST"
    if armature.animation_data:
        armature.animation_data.action = None
    textures = atlas["textures"] if atlas else write_textures(args.rigged, args.out_dir / f"{args.base_name}_textures")
    base_path = args.out_dir / f"{args.base_name}.glb"
    export_glb(base_path, [body], body, animated=False)
    armature.data.pose_position = "POSE"
    return textures, base_path


def close_gait(armature, body, action, args, role, extras, key):
    """`close_loop` for a looped gait, then the clearance of a held weapon on the frames it turned (as after a settle)."""

    extras[key][role] = close_loop(action)
    if extras[key][role] and extras[key][role].get("frames_blended"):
        last = int(round(action.frame_range[1]))
        cleared = clear_settled_weapon(armature, body, action, last - extras[key][role]["frames_blended"], last, args)
        if cleared is not None:
            extras["settle_clearance"][role] = cleared


def export_role(armature, body, args, role, clip, trims, stage, extras, trims_end=None, windows=None):
    """One GLB for a role: the mesh, the shared armature and exactly one clip, after the trim or the loop window, the arm level, the chains
    and the snap easing. What each step did goes into `extras` (keyed by step, then role). Returns the clip's record."""

    action, trimmed, trims_end, windows = bpy.data.actions[clip], None, trims_end or {}, windows or {}
    closes = role in args.loop_close and role not in trims
    if role in trims:
        action, trimmed = trimmed_copy(action, int(trims[role]))
    elif role in windows:
        action, trimmed = windowed_copy(action, *windows[role])
    elif role in trims_end:
        action, trimmed = trimmed_copy(action, int(trims_end[role]), exact=True)
    if role in args.arm_level:
        extras["arm_level"][role] = level_arms(armature, action, target_share=args.arm_level_target)
    elif role in args.arm_level_high:
        extras["arm_level"][role] = level_arms(armature, action, target_share=args.arm_level_target, only_when_high=True)
    if role in args.untwist:
        # Before the settle, so the clip settles back to its untwisted first pose.
        extras["untwist"][role] = untwist_waist(armature, action, role, body)
    if closes:
        # A looped gait never settles: frames that ease into the first pose are a stop once per cycle (TRIPO-LOOP-STANDS).
        close_gait(armature, body, action, args, role, extras, "loop_close")
    elif role in args.settle:
        # After the arm level, before the chains: the cloth follows the settled body.
        end_before = int(round(action.frame_range[1]))
        extras["settle"][role] = settle_to_first(action)
        if extras["settle"][role] and extras["settle"][role].get("frames_added"):
            # The straight blend of the held weapon's arm can swing the weapon through the body: the grip stage's clearance runs again on those frames.
            extras["settle_clearance"][role] = clear_settled_weapon(armature, body, action, end_before, int(round(action.frame_range[1])), args)
    if stage is not None:
        # Before the easing, so a chain bone pushed fast by a collision is eased like any other joint.
        extras["chains"][role] = chain_stage.bake_chains(armature, action, stage, role)
        if closes:
            close_gait(armature, body, action, args, role, extras, "loop_close_chains")
        elif role in args.settle:
            # The cloth lags the settled body, so it may end away from its first pose: a short second settle for what is left (none when it does not).
            extras["settle_chains"][role] = settle_to_first(action)
    if args.ease_snaps:
        # The stride of a looped gait is not a snap (lib/tripo_loop.py): only a step past the kit's spin limit is eased there.
        trigger = max(args.ease_snaps, tripo_loop.GAIT_SNAP_DEGREES) if closes else args.ease_snaps
        extras["ease_snaps"][role] = dict(normalise_rotation_keys(action, trigger_degrees=trigger, target_degrees=0.75 * trigger), trigger_degrees=round(trigger, 1))
    assign_action(armature, action)
    role_path = args.out_dir / (args.role_name.format(role=role) + ".glb")
    export_glb(role_path, [armature, body], armature, animated=True)
    name_glb_animation(role_path, safe_animation_name(clip))
    animations, joints = glb_animations(role_path)
    if len(animations) != 1:
        raise SystemExit(f"{role_path.name} holds {len(animations)} animations, expected exactly one")
    return {
        "clip": clip,
        "file": role_path.name,
        "animation_name": animations[0]["name"],
        "frames": animations[0]["frames"],
        "action_frame_range": [float(v) for v in action.frame_range],
        "trimmed": trimmed,
        "joints": joints,
    }


def main():
    args = parse_args()
    roles, rigid_parts, twin = read_inputs(args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    armature, meshes, ignored = load_rig(args.rigged)
    decimated = reduce_parts(meshes, armature, args)
    rigid_for, twin_report = weapon_flag_map(meshes, rigid_parts, twin)

    # Bones: keep the kit's, merge the rest into their nearest kept parent, then rename.
    bones_before = len(armature.data.bones)
    # `extras` below is the per-step record of the role clips, so the extra joints (lib/tripo_extra_joints.py) keep their own name.
    keep, merge_into, dropped, extra_joints = merge_plan(armature)
    all_weights = {obj.name: read_weights(obj) for obj in meshes}
    weights_moved = move_extra_weights(armature, meshes, all_weights, keep, extra_joints)
    clip_names, roles = resolve_roles(roles)
    bone_names = drop_and_rename(armature, keep, dropped)
    weapon_summary, weapon_points = bind_meshes(meshes, all_weights, bone_names, merge_into, rigid_for)
    separated = separate_coincident_weapon_vertices(meshes, rigid_for) if rigid_for else 0
    body, atlas = join_parts(meshes, args)
    materials = [slot.material.name for slot in body.material_slots if slot.material]
    # Secondary chains (lib/tripo_chains.py): new bones and weights for a cloak or wings, keyed per role below. The role clips tell the
    # stage the room the arms swing through, which the chains keep clear of.
    role_clips = [bpy.data.actions[clip] for clip in dict.fromkeys(roles.values())]
    stage = chain_stage.add_chains(armature, body, list(args.chains), role_clips) if args.chains else None
    textures, base_path = export_base(armature, body, args, atlas)

    trims = dict(split_pair(item, "--trim") for item in args.trim)
    extras = {"ease_snaps": {}, "arm_level": {}, "chains": {}, "settle": {}, "settle_clearance": {}, "settle_chains": {}, "untwist": {},
              "loop_close": {}, "loop_close_chains": {}}
    trims_end = dict(split_pair(item, "--trim-end") for item in args.trim_end)
    windows = {role: tuple(int(value) for value in span.split(":")) for role, span in (split_pair(item, "--loop-window") for item in args.loop_window)}
    clips = {role: export_role(armature, body, args, role, clip, trims, stage, extras, trims_end, windows) for role, clip in roles.items()}

    report = {
        "tool": "prepare_tripo_unit",
        "blender": bpy.app.version_string,
        "input": args.rigged.name,
        "ignored_objects": ignored,
        "clips_in_file": sorted(clip_names),
        "bones_before": bones_before,
        "ease_snaps": extras["ease_snaps"],
        "arm_level": extras["arm_level"],
        "settle": extras["settle"],
        "settle_clearance": extras["settle_clearance"],
        "settle_chains": extras["settle_chains"],
        "loop_close": extras["loop_close"],
        "loop_close_chains": extras["loop_close_chains"],
        "untwist": extras["untwist"],
        "bones_after": len(armature.data.bones),
        "bone_names": [b.name for b in armature.data.bones],
        "dropped_bones": len(dropped),
        "extra_joints": {"dropped": extra_joints, "weights_moved": weights_moved},
        "weapon": weapon_summary,
        "weapon_vertices_separated_from_body": separated,
        "part_triangles": decimated,
        "twin": twin_report,
        "materials": materials,
        "atlas": atlas,
        "triangles": sum(len(p.vertices) - 2 for p in body.data.polygons),
        "vertices": len(body.data.vertices),
        "base": base_path.name,
        "textures": textures,
        "clips": clips,
    }
    if stage is not None:
        report["chains"] = {"plan": chain_stage.plan_summary(stage), "roles": extras["chains"]}
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
