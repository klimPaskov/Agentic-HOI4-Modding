"""A death that burns away where the unit stands (`"death_kind": "burn"` in a job's `tripo` block). No Blender.

The death clip is a standing reaction (a hit that doubles the body over, `hit_to_stomach` for the demon, maintainer decision D-85). The
route then makes it a burn on the exported files, which the game reads as vanilla does:

1. The reaction plays to its peak (the frame farthest from its first pose, `peak_frame`) and holds there, so the body never stands up again.
2. From the peak the whole body shrinks by bone scale toward the ground point under its feet (`BURN_FRAMES`, a smoothstep), the hips coming
   down so the feet stay on the ground, to `END_SCALE`. Vanilla hides parts of a destroyed landmark the same way: in
   `landmark_hakko_ichiu_destroyed_destroy.anim` the bone `hide` scales from 1.0 to 0.07, and the landmark's `destroy` state fires
   `building_explode_effect` and `factory_smoke_particle` at timed events. Every bone shrinks with the hips, wings included, so nothing is
   left over the ashes.
3. A low ash heap, its own part on its own bone (`HEAP_BONE`, a child of the hips), grows from nothing over the last `HEAP_SHARE` of the
   burn and stays (`HOLD_FRAMES`). In every other clip the bone keeps its rest pose, where the heap is bound `HIDE` of its size inside the
   pelvis, so it is never seen. Its colour is the darkest texels of the unit's own diffuse map (`dark_uvs`): the unit's ash.
4. A locator (`LOCATOR`, parented to `LOCATOR_BONE`, the upper spine) carries the fire and the smoke. Vanilla's GER rifle infantry's death
   state fires `blood_particle` at its `head` locator, parented to the bone `head`, at `time = 0`. The particle events are written by
   `wire_unit.py` from the plan this module writes beside the files (`<stem>_burn.json`).

The checks for this death (`burn_findings`) replace the lying-body ones: BURN-STANDS, BURN-IN-PLACE, BURN-SHRINK, BURN-GROUNDED,
BURN-NO-FLYOFF, BURN-END, BURN-PARTICLE and BURN-WINGS. The kit's deformation checks read the clip up to the burn's start: after it the
pose is held and only scaled.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from . import pdx_deform, pdx_motion, tripo_pose
from .pdx_binary import PdxNode, read, summarize_mesh
from .pdx_write import write

KIND = "burn"
BURN_FRAMES = 75  # 2.5 s at the game's 30 frames a second
HEAP_SHARE = 0.4  # kept for older plans; the heap now grows from `HEAP_FROM`
HEAP_FROM = 0.15  # the heap grows from the feet from this share of the burn on, as the body goes
BODY_DELAY = 0.25  # the torso and head start to shrink at this share of the burn
LIMB_SHARE = 0.5  # the wings and limbs are down to `LIMB_SCALE` by this share of the burn
LIMB_SCALE = 0.15
HOLD_FRAMES = 30  # the end state, 1 s
END_SCALE = 0.07  # vanilla's hide scale (landmark_hakko_ichiu_destroyed_destroy.anim, bone `hide`)
HIDE = 1e-3  # the heap is bound at this share of its size, inside the pelvis
HEAP_BONE = "Ash"
LOCATOR = "burn"
LOCATOR_BONE = "Spine02"
HEAP_RADIUS_HIPS = 2.1  # the heap's radius, in hip-to-hip distances (inside the standing footprint, BURN-END)
HEAP_RINGS, HEAP_SIDES = 6, 24  # a smooth dome, not a polygon
HEAP_LUMP = 0.08  # its gentle lumps, a share of the radius and height
HEAP_RAGGED = 0.16  # the rim's ragged in and out, a share of the radius
ASH_MARK = "_ash_"  # the heap's maps are <stem>_ash_diffuse.dds and so on (blender/review_render.py keeps a stream's own maps by it)
ASH_TEXTURE_SIZE = 64
ASH_COLOUR = (34.0, 32.0, 31.0)  # dark grey to black ash
EMBER_COLOUR = (150.0, 52.0, 18.0)  # a faint ember tint
EMBER_SHARE = 0.04  # of the texels
FLAT_NORMAL_RGBA = (0, 128, 0, 128)  # the packed layout of the kit's normal maps: x in alpha, y in green, blue black (blue is emissive)
ASH_SPECULAR_RGBA = (0, 16, 0, 24)  # the kit's packed layout (pack_pdx_material.py): low specular level, not metal, matte
HEAP_HEIGHT_SHARE = 0.16  # its height, a share of its radius: a low heap, not a dome
DARK_PERCENTILE = 3.0  # the heap takes the UVs of the body's darkest 3% of vertices
GROUND_TOLERANCE = 0.01  # BURN-GROUNDED: share of the height off or under the ground
SHRINK_SLACK = 0.01  # BURN-SHRINK and BURN-NO-FLYOFF: share of the height a measure may grow by between frames
STAND_LEAN_DEGREES = 60.0  # BURN-STANDS: the torso's lean from upright (the kit's untwist reads a torso past 60 degrees as not standing)
TRAVEL_LIMIT = 0.1  # BURN-IN-PLACE: hip travel, hip heights (lib/glb_root.MAX_ROOT_TRAVEL_SHARE)
END_FRAMES = 15  # BURN-END: the last frames judged
SMOKE_AFTER_S = 1.0  # the smoke goes on this long after the clip's last frame
# The body shrinks toward the ground point, so the hips slide by their distance from it times (1 - END_SCALE). A reaction that doubles the
# body over holds the hips behind the feet at its peak: the demon's own made death held them 0.13 hip heights back and slid 0.12, past
# BURN-IN-PLACE (2026-11-23). The point moves from under the feet toward under the hips until the slide is this share of the limit.
HELD_TRAVEL_SHARE = 0.75


def held_point(feet_point: np.ndarray, hips: np.ndarray, rest_hips: float) -> np.ndarray:
    """The ground point under the feet, moved toward the point under the hips just far enough that the hips slide at most
    `HELD_TRAVEL_SHARE` of `TRAVEL_LIMIT` hip heights while the body shrinks. Unchanged when the hips are already that close."""

    point = np.asarray(feet_point, float).copy()
    offset = np.array([float(hips[0]) - point[0], float(hips[2]) - point[2]])
    distance = float(np.linalg.norm(offset))
    allowed = HELD_TRAVEL_SHARE * TRAVEL_LIMIT * max(rest_hips, 1e-6) / (1.0 - END_SCALE)
    if distance <= allowed:
        return point
    shift = offset * (1.0 - allowed / distance)
    point[0] += shift[0]
    point[2] += shift[1]
    return point


def plan_path(folder: Path, stem: str) -> Path:
    return Path(folder) / f"{stem}_burn.json"


def read_plan(folder: Path, stem: str) -> Optional[dict]:
    path = plan_path(folder, stem)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(x, float), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


# ---- the heap's shape --------------------------------------------------------------------------------------------------

def heap_geometry(radius: float, height: float, rings: int = HEAP_RINGS, sides: int = HEAP_SIDES, seed: int = 7):
    """(points (V, 3) with the base at y 0 round the origin, triangles (T, 3) wound outward, closed with a flat base): a soft, low, rounded
    mound. Its profile is a smooth dome, `height * (1 - r^2)^1.5`, with gentle lumps (`HEAP_LUMP`) that fade to the rim, so its outline has
    no corners: a fresh review read the first heap, three rings of ten points, as a hard seven-sided slab."""

    rng = np.random.default_rng(seed)
    lumps = rng.uniform(0.0, 2.0 * math.pi, 3)
    points = [[0.0, height, 0.0]]
    for ring in range(1, rings + 1):
        share = ring / rings
        for side in range(sides):
            angle = 2.0 * math.pi * side / sides
            wobble = 1.0 + HEAP_LUMP * sum(math.sin(k * angle + phase) for k, phase in zip((2, 3, 5), lumps)) / 3.0
            ragged = 1.0 + HEAP_RAGGED * share ** 3 * (rng.uniform(-1.0, 1.0) * 0.6 + 0.4 * math.sin(7 * angle + lumps[1]))
            r = radius * share * ragged
            y = height * (1.0 - share ** 4) * wobble if ring < rings else 0.0  # flat on top, falling off at the edge
            points.append([r * math.cos(angle), y, r * math.sin(angle)])
    base = len(points)
    points.append([0.0, 0.0, 0.0])
    triangles = []
    for side in range(sides):
        triangles.append([0, 1 + (side + 1) % sides, 1 + side])
    for ring in range(1, rings):
        inner, outer = 1 + (ring - 1) * sides, 1 + ring * sides
        for side in range(sides):
            a, b = inner + side, inner + (side + 1) % sides
            c, d = outer + side, outer + (side + 1) % sides
            triangles += [[a, b, d], [a, d, c]]
    rim = 1 + (rings - 1) * sides
    for side in range(sides):
        triangles.append([base, rim + side, rim + (side + 1) % sides])
    points, triangles = np.asarray(points, float), np.asarray(triangles, int)
    centre = points.mean(axis=0)
    for t in range(len(triangles)):  # wind every face outward from the mound's centre
        a, b, c = points[triangles[t]]
        if float(np.cross(b - a, c - a) @ ((a + b + c) / 3.0 - centre)) < 0:
            triangles[t] = triangles[t][[0, 2, 1]]
    return points, triangles


def ash_textures(folder: Path, stem: str, seed: int = 5) -> Dict[str, str]:
    """Write the heap's own maps beside the mesh (DXT5 with mips, as the kit's unit textures): diffuse dark grey to black ash with a faint
    ember tint (`ASH_COLOUR`, `EMBER_COLOUR`, `EMBER_SHARE`), a flat normal map and a matte, non-metal specular map. Returns their names."""

    from PIL import Image

    from . import model_dds

    rng = np.random.default_rng(seed)
    size = ASH_TEXTURE_SIZE
    noise = rng.normal(0.0, 1.0, (size, size))
    for _ in range(3):  # soft grain, wrapped so the texture tiles
        noise = (noise + np.roll(noise, 1, 0) + np.roll(noise, -1, 0) + np.roll(noise, 1, 1) + np.roll(noise, -1, 1)) / 5.0
    noise = (noise - noise.min()) / max(float(np.ptp(noise)), 1e-9)
    colour = np.asarray(ASH_COLOUR, float)[None, None, :] * (0.55 + 0.9 * noise[..., None])
    embers = noise > 1.0 - EMBER_SHARE
    colour[embers] = colour[embers] * 0.5 + np.asarray(EMBER_COLOUR, float) * 0.5
    rgba = np.dstack([np.clip(colour, 0, 255), np.full((size, size), 255.0)]).astype(np.uint8)
    names = {"diffuse": f"{stem}{ASH_MARK}diffuse.dds", "normal": f"{stem}{ASH_MARK}normal.dds", "specular": f"{stem}{ASH_MARK}specular.dds"}
    flat = np.zeros((size, size, 4), np.uint8)
    flat[...] = FLAT_NORMAL_RGBA
    spec = np.zeros((size, size, 4), np.uint8)
    spec[...] = ASH_SPECULAR_RGBA
    for key, array in (("diffuse", rgba), ("normal", flat), ("specular", spec)):
        (Path(folder) / names[key]).write_bytes(model_dds.dxt5_bytes(Image.fromarray(array, "RGBA")))
    return names


def vertex_normals(points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    normals = np.zeros_like(points)
    for tri in triangles:
        a, b, c = points[tri]
        normals[tri] += np.cross(b - a, c - a)
    return normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)


def dark_uvs(uvs: np.ndarray, diffuse: Optional[Path], count: int) -> np.ndarray:
    """`count` UVs taken from the body's darkest vertices on its diffuse map (its own ash colour); the body's own UVs in turn without a map."""

    uvs = np.asarray(uvs, float)
    order = np.arange(len(uvs))
    if diffuse is not None and Path(diffuse).is_file():
        from PIL import Image

        image = np.asarray(Image.open(diffuse).convert("RGB"), float).mean(axis=2)
        h, w = image.shape
        px = np.clip((uvs[:, 0] % 1.0) * (w - 1), 0, w - 1).astype(int)
        py = np.clip((uvs[:, 1] % 1.0) * (h - 1), 0, h - 1).astype(int)
        light = image[py, px]
        order = np.nonzero(light <= np.percentile(light, DARK_PERCENTILE))[0]
    picks = order[np.linspace(0, len(order) - 1, count).astype(int)] if len(order) else np.zeros(count, int)
    return uvs[picks]


# ---- the mesh: heap, bone and locator ----------------------------------------------------------------------------------

def _shape(root: PdxNode) -> PdxNode:
    obj = root.child("object")
    return next(child for child in obj.children if child.child("mesh") is not None)


def add_heap(mesh_path: Path, diffuse: Optional[Path] = None) -> dict:
    """Add the heap to the `.mesh`, in place: its own stream in the first shape, with its own ash material (`ash_textures`, written beside
    the mesh), bound wholly to a new `HEAP_BONE` under the hips, and the `LOCATOR`. The unit's own maps are not touched (D-86). Returns
    the heap's numbers (bone, bind point, radius, height). `diffuse` is unused and kept for callers."""

    mesh = pdx_deform.load_mesh(mesh_path)
    if HEAP_BONE in mesh.bones:
        raise ValueError(f"{Path(mesh_path).name} already has a {HEAP_BONE} bone")
    legs = pdx_motion.find_legs(mesh)
    rest = pdx_motion.rest_joints(mesh)
    hips = legs.pelvis
    # The heap's bone sits just inside the body's skin nearest the hips joint, half a percent of the height in: a part bound there never
    # floats apart from the body at rest (the kit's loose-part rule allows 2%), and at its bound size it is never seen.
    nearest = mesh.positions[int(np.argmin(np.linalg.norm(mesh.positions - rest[hips], axis=1)))]
    inward = rest[hips] - nearest
    anchor = nearest + inward / max(float(np.linalg.norm(inward)), 1e-12) * min(0.005 * mesh.height, float(np.linalg.norm(inward)))
    width = float(np.linalg.norm((rest[legs.legs[0].hip] - rest[legs.legs[1].hip])[[0, 2]])) if len(legs.legs) == 2 else 0.1 * mesh.height
    radius = HEAP_RADIUS_HIPS * width
    points, triangles = heap_geometry(radius, HEAP_HEIGHT_SHARE * radius)
    root = read(mesh_path)
    shape = _shape(root)
    body = shape.child("mesh")
    skeleton = shape.child("skeleton")
    names = ash_textures(Path(mesh_path).parent, Path(mesh_path).stem)
    bound = anchor + HIDE * points
    normals = vertex_normals(points, triangles)
    tangents = np.cross(normals, [0.0, 0.0, 1.0])
    tangents[np.linalg.norm(tangents, axis=1) < 1e-6] = [1.0, 0.0, 0.0]
    tangents = tangents / np.linalg.norm(tangents, axis=1, keepdims=True)
    uvs = np.c_[points[:, 0] / (2.0 * radius) + 0.5, points[:, 2] / (2.0 * radius) + 0.5] * 2.0  # the ash grain tiles twice across the heap
    index = len(skeleton.children)
    per = int(body.child("skin").properties["bones"][0])
    properties = {"p": [float(v) for v in bound.ravel()]}
    if "n" in body.properties:
        properties["n"] = [float(v) for v in normals.ravel()]
    if "ta" in body.properties:
        properties["ta"] = [float(v) for row in tangents for v in (*row, 1.0)]
    if "u0" in body.properties:
        properties["u0"] = [float(v) for v in uvs.ravel()]
    properties["tri"] = [int(v) for v in triangles.ravel()]
    centre = bound.mean(axis=0)
    properties["boundingsphere"] = [float(centre[0]), float(centre[1]), float(centre[2]), float(np.linalg.norm(bound - centre, axis=1).max())]
    depth = body.depth
    stream = PdxNode("mesh", depth, properties, [
        PdxNode("aabb", depth + 1, {"min": [float(v) for v in bound.min(axis=0)], "max": [float(v) for v in bound.max(axis=0)]}),
        PdxNode("material", depth + 1, {"shader": ["PdxMeshAdvanced"], "diff": [names["diffuse"]], "n": [names["normal"]], "spec": [names["specular"]]}),
        PdxNode("skin", depth + 1, {"bones": [per], "ix": ([index] + [-1] * (per - 1)) * len(points), "w": ([1.0] + [0.0] * (per - 1)) * len(points)}),
    ])
    shape.children.insert(shape.children.index(skeleton), stream)
    parent_name = mesh.bones[hips]
    skeleton.children.append(PdxNode(HEAP_BONE, skeleton.children[0].depth, {
        "ix": [index], "pa": [int(next(c.properties["ix"][0] for c in skeleton.children if c.name == parent_name))],
        "tx": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, float(-anchor[0]), float(-anchor[1]), float(-anchor[2])]}))
    locators = root.child("locator")
    if locators is None:
        locators = PdxNode("locator", 1)
        root.children.append(locators)
    if LOCATOR_BONE in mesh.bones and not any(c.name == LOCATOR for c in locators.children):
        locators.children.append(PdxNode(LOCATOR, 2, {"p": [0.0, 0.0, 0.0], "q": [0.0, 0.0, 0.0, 1.0], "pa": [LOCATOR_BONE]}))
    write(mesh_path, root)
    return {"bone": HEAP_BONE, "parent": parent_name, "bind_point": [round(float(v), 4) for v in anchor], "radius": round(radius, 4),
            "height": round(HEAP_HEIGHT_SHARE * radius, 4), "vertices": len(points), "triangles": len(triangles), "maps": names,
            "locator": LOCATOR if LOCATOR_BONE in mesh.bones else None, "locator_bone": LOCATOR_BONE}


# ---- the clips ---------------------------------------------------------------------------------------------------------

def _rest_local(mesh: pdx_deform.SkinnedMesh, bone: str) -> np.ndarray:
    bind = np.linalg.inv(mesh.inverse_bind)
    index = mesh.bones.index(bone)
    parent = mesh.parents[index]
    return np.linalg.inv(bind[parent]) @ bind[index] if parent >= 0 else bind[index]


def _decompose(matrix: np.ndarray):
    scale = float(np.cbrt(abs(np.linalg.det(matrix[:3, :3]))))
    rotation = matrix[:3, :3] / max(scale, 1e-12)
    return matrix[:3, 3].copy(), tripo_pose._quaternion_from_matrix(rotation), scale


def write_anim(path: Path, channels: Dict[str, Dict[str, np.ndarray]], frames: int, rest: Optional[Dict[str, Dict[str, list]]] = None) -> None:
    """Rewrite `path` with every joint of its info block keyed as `channels` says (each joint keeps its own keyed channels), `frames` long.
    `rest` adds joints (name: their rest t, q, s), keyed in every channel."""

    root = read(path)
    info, samples = root.child("info"), root.child("samples")
    depth = info.children[0].depth if info.children else 2
    for name, values in (rest or {}).items():
        if not any(c.name == name for c in info.children):
            info.children.append(PdxNode(name, depth, {"sa": ["tqs"], "t": list(map(float, values["t"])), "q": list(map(float, values["q"])),
                                                         "s": [float(values["s"][0])]}))
    info.properties["sa"] = [int(frames)]
    info.properties["j"] = [len(info.children)]
    out = {"t": [], "q": [], "s": []}
    for joint in info.children:  # a channel that now moves is keyed (a burn scales the hips of a clip that never scaled them)
        flags = str((joint.properties.get("sa") or [""])[0])
        for key in "tqs":
            rest_value = np.asarray(joint.properties.get(key, [1.0] if key == "s" else [0.0, 0.0, 0.0, 1.0][: 3 if key == "t" else 4]), float)
            if key not in flags and joint.name in channels and not np.allclose(np.asarray(channels[joint.name][key][:frames], float).reshape(frames, -1), rest_value.reshape(1, -1)):
                flags += key
        joint.properties["sa"] = ["".join(k for k in "tqs" if k in flags)]
    keyed = [(joint.name, str((joint.properties.get("sa") or [""])[0])) for joint in info.children]
    for frame in range(frames):
        for name, flags in keyed:
            for key in "sqt":
                if key in flags:
                    value = channels[name][key][frame]
                    out[key] += [float(value)] if key == "s" else [float(v) for v in value]
    for key in "tqs":
        if key in samples.properties or out[key]:
            samples.properties[key] = out[key]
    write(path, root)


def add_rest_joint(mesh_path: Path, anim_path: Path) -> None:
    """Key the heap bone at its rest pose in a clip that does not burn (it stays hidden inside the pelvis)."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    t, q, s = _decompose(_rest_local(mesh, HEAP_BONE))
    channels = dict(anim.channels)
    channels[HEAP_BONE] = {"t": np.tile(t, (anim.frames, 1)), "q": np.tile(q, (anim.frames, 1)), "s": np.full(anim.frames, s)}
    write_anim(anim_path, channels, anim.frames, {HEAP_BONE: {"t": t, "q": q, "s": [s]}})


def _hips_world(channel: Dict[str, np.ndarray], frame: int) -> np.ndarray:
    world = np.eye(4)
    world[:3, :3] = pdx_deform._quaternion_matrices(channel["q"][frame][None])[0] * channel["s"][frame]
    world[:3, 3] = channel["t"][frame]
    return world


def peak_frame(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> int:
    """The frame whose pose is farthest from the first (the mean joint distance): the reaction's peak, where the burn starts."""

    joints = pdx_motion.posed_joints(mesh, anim)
    distance = np.linalg.norm(joints - joints[:1], axis=2).mean(axis=1)
    return int(np.argmax(distance))


def limb_roots(mesh: pdx_deform.SkinnedMesh) -> List[str]:
    """The bones that shrink first in a burn: each arm's upper arm, each leg's thigh and each wing chain's root."""

    names = [name for name in ("LeftArm", "RightArm", "LeftUpLeg", "RightUpLeg") if name in mesh.bones]
    chains = [name for i, name in enumerate(mesh.bones) if name.startswith("Wing") and (mesh.parents[i] < 0 or not mesh.bones[mesh.parents[i]].startswith("Wing"))]
    return names + chains


def _sink(mesh: pdx_deform.SkinnedMesh, channels, frames: int, ground: float, start: int) -> np.ndarray:
    """Per frame, how far the hips come down so the body's lowest point (the heap left out) stays on the ground while the legs shrink under it."""

    anim = pdx_deform.Animation(30.0, frames, channels)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    body = pdx_deform.dominant_bones(mesh) != (mesh.bones.index(HEAP_BONE) if HEAP_BONE in mesh.bones else -2)
    lift = np.zeros(frames)
    for frame in range(start, frames):
        lift[frame] = max(0.0, float(pdx_deform.skin(mesh, matrices[frame])[body, 1].min()) - ground)
    return lift


def burn_death(mesh_path: Path, anim_path: Path) -> dict:
    """Make the exported death clip a burn (see the module text), in place. Returns the plan's numbers."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    legs = pdx_motion.find_legs(mesh)
    hips = mesh.bones[legs.pelvis]
    if mesh.parents[legs.pelvis] >= 0:
        raise ValueError("the hips are not the skeleton's root")
    start = peak_frame(mesh, anim)
    frames = start + BURN_FRAMES + HOLD_FRAMES + 1
    channels: Dict[str, Dict[str, np.ndarray]] = {}
    for name, channel in anim.channels.items():
        held = {key: np.concatenate([value[: start + 1], np.repeat(value[start : start + 1], frames - start - 1, axis=0)]) for key, value in channel.items()}
        channels[name] = held
    held_anim = pdx_deform.Animation(anim.fps, frames, channels)
    joints = pdx_motion.posed_joints(mesh, held_anim)
    ground = float(mesh.positions[:, 1].min())
    feet = [leg.ankle for leg in legs.legs]
    point = np.array([float(joints[start, feet, 0].mean()), ground, float(joints[start, feet, 2].mean())])
    point = held_point(point, joints[start, legs.pelvis], float(pdx_motion.rest_joints(mesh)[legs.pelvis, 1] - ground))
    t = (np.arange(frames) - start) / float(BURN_FRAMES)
    # The burn breaks the body up: the wings and limbs shrink first and fastest (`LIMB_SCALE` by `LIMB_SHARE` of the burn), the torso and
    # head last (from `BODY_DELAY` of the burn), while the body sinks so its lowest point stays on the ground. An even shrink left a whole
    # half-size demon standing in the fire (run demon_d, frames 47 to 61), and a fresh review read it as a miniature.
    scale = 1.0 - (1.0 - END_SCALE) * smoothstep((t - BODY_DELAY) / (1.0 - BODY_DELAY))
    limb = 1.0 - (1.0 - LIMB_SCALE) * smoothstep(t / LIMB_SHARE)
    grow = smoothstep((t - HEAP_FROM) / (1.0 - HEAP_FROM))
    hips_t = channels[hips]["t"].copy()
    channels[hips]["t"] = point + scale[:, None] * (hips_t - point)
    channels[hips]["s"] = channels[hips]["s"] * scale
    for name in limb_roots(mesh):
        channels[name]["s"] = channels[name]["s"] * limb
    channels[hips]["t"][:, 1] -= _sink(mesh, channels, frames, ground, start)
    rest_t, rest_q, rest_s = _decompose(_rest_local(mesh, HEAP_BONE))
    heap = {"t": np.tile(rest_t, (frames, 1)), "q": np.tile(rest_q, (frames, 1)), "s": np.full(frames, rest_s)}
    # From the burn's start the hidden heap moves from where the hips carry it to the ground point and turns upright (a smoothstep up to the
    # heap's start, no faster than the settle rate), then grows there: a jump between the two would turn its bone in one frame.
    rest_local = _rest_local(mesh, HEAP_BONE)
    carried = _hips_world(channels[hips], start) @ rest_local
    carried_q = tripo_pose._quaternion_from_matrix(carried[:3, :3] / np.cbrt(abs(np.linalg.det(carried[:3, :3]))))
    upright_q = np.array([0.0, 0.0, 0.0, 1.0])
    move = smoothstep(t / max(HEAP_FROM, 1e-6))
    for frame in range(start, frames):
        hips_world = _hips_world(channels[hips], frame)
        heap_world = np.eye(4)
        turn = tripo_pose.slerp(carried_q, upright_q, float(move[frame]))
        hidden = HIDE * float(channels[hips]["s"][frame]) if grow[frame] <= 0 else max(float(grow[frame]), HIDE)
        heap_world[:3, :3] = pdx_deform._quaternion_matrices(np.asarray(turn)[None])[0] * hidden / HIDE
        heap_world[:3, 3] = (1.0 - move[frame]) * (hips_world @ rest_local)[:3, 3] + move[frame] * point
        heap["t"][frame], heap["q"][frame], heap["s"][frame] = _decompose(np.linalg.inv(hips_world) @ heap_world)
    channels[HEAP_BONE] = heap
    write_anim(anim_path, channels, frames, {HEAP_BONE: {"t": rest_t, "q": rest_q, "s": [rest_s]}})
    return {"kind": KIND, "burn_start": start, "burn_frames": BURN_FRAMES, "heap_start": int(start + round(HEAP_FROM * BURN_FRAMES)),
            "frames": frames, "fps": anim.fps, "end_scale": END_SCALE, "ground_point": [round(float(v), 4) for v in point]}


def write_plan(folder: Path, stem: str, heap: dict, death: dict) -> dict:
    """The plan beside the files: what wire_unit writes as particle events and the review renders draw as a stand-in."""

    fps = max(death["fps"], 1.0)
    plan = dict(death, clip=f"{stem}_death", heap=heap, locator=heap.get("locator"), locator_bone=heap.get("locator_bone"),
                particles=[
                    {"name": f"{stem}_burn_fire_particle", "source": "gfx/particles/environment/building_fire.asset", "source_name": "building_fire_file",
                     "time": 0, "duration_s": round((death["burn_start"] + BURN_FRAMES) / fps, 2), "scale": 1,
                     "standin": "fire"},
                    {"name": f"{stem}_burn_smoke_particle", "source": "gfx/particles/environment/city_smoke.asset", "source_name": "city_smoke",
                     "time": 0, "duration_s": round(death["frames"] / fps + SMOKE_AFTER_S, 2), "scale": 1, "standin": "smoke"}])
    plan_path(folder, stem).write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8", newline="\n")
    return plan


def truncated(anim: pdx_deform.Animation, frames: int) -> pdx_deform.Animation:
    """The first `frames` frames of a clip: what the kit's deformation checks read of a burn (after its start the pose is only scaled)."""

    frames = max(1, min(int(frames), anim.frames))
    return pdx_deform.Animation(anim.fps, frames, {name: {key: value[:frames] for key, value in channel.items()} for name, channel in anim.channels.items()})


# ---- the checks --------------------------------------------------------------------------------------------------------

LYING_RULES = ("TRIPO-NOT-DOWN", "TRIPO-DEATH-REST", "TRIPO-DEATH-FEET", "TRIPO-DEATH-HOVER", "TRIPO-DEATH-LEG-KICK", "TRIPO-DEATH-SPLAY")


def _finding(rule: str, clip: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": clip, "message": message, **numbers}


def _world_scales(skinning: np.ndarray, mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """(F, B) each bone's world scale."""

    world = skinning @ np.linalg.inv(mesh.inverse_bind)[None]
    return np.cbrt(np.abs(np.linalg.det(world[..., :3, :3])))


def _map_extent(points: np.ndarray) -> float:
    """The area of the points' outline box in the review sheets' map view (25 degrees round, 55 down): what the map shows of the body."""

    from . import tripo_chains

    up = np.array([0.0, 1.0, 0.0])
    view = tripo_chains.review_view(np.array([0.0, 0.0, -1.0]), up, *tripo_chains.REVIEW_VIEWS["map"])
    first = tripo_chains.unit(np.cross(up, view))
    second = np.cross(view, first)
    return float(np.ptp(points @ first) * np.ptp(points @ second))


def _stands(mesh, joints, hips: int, clip: str, out: List[dict], numbers: dict) -> None:
    head = next((i for i, n in enumerate(mesh.bones) if n.lower() == "head"), None)
    lean = 0.0
    if head is not None:
        axis = joints[:, head] - joints[:, hips]
        lean = float(np.degrees(np.arccos(np.clip(axis[:, 1] / np.maximum(np.linalg.norm(axis, axis=1), 1e-12), -1.0, 1.0))).max())
    numbers["lean_degrees"] = round(lean, 1)
    if lean > STAND_LEAN_DEGREES:
        out.append(_finding("BURN-STANDS", clip, f"the torso leans {lean:.0f} degrees from upright (limit {STAND_LEAN_DEGREES:g}): a burn stays standing and never lies down", degrees=round(lean, 1)))


def _shrinks(series: Dict[str, list], scales: np.ndarray, start: int, hips: int, clip: str, out: List[dict], numbers: dict) -> None:
    tops, cells, reach = series["tops"], series["cells"], series["reach"]
    growth = max([tops[i + 1] - tops[i] for i in range(len(tops) - 1)] + [0.0])
    cell_growth = max([(cells[i + 1] - cells[i]) / max(cells[0], 1) for i in range(len(cells) - 1)] + [0.0])
    scale_growth = max(float(np.diff(scales[start:, hips]).max(initial=0.0)), 0.0)
    numbers.update(top_growth=round(growth, 4), map_growth=round(cell_growth, 4), scale_growth=round(scale_growth, 4))
    if growth > SHRINK_SLACK or cell_growth > SHRINK_SLACK or scale_growth > 1e-4:
        out.append(_finding("BURN-SHRINK", clip, f"after the burn starts the body grows again (its top by {growth:.1%} of the height, its map outline by {cell_growth:.1%}, "
                            f"the hips' scale by {scale_growth:.3f}, limit {SHRINK_SLACK:.0%}): a burn only shrinks"))
    flyoff = max([reach[i + 1] - reach[i] for i in range(len(reach) - 1)] + [0.0])
    numbers["reach_growth"] = round(flyoff, 4)
    if flyoff > SHRINK_SLACK:
        out.append(_finding("BURN-NO-FLYOFF", clip, f"a part moves {flyoff:.1%} of the height farther from where the body burns between two frames (limit {SHRINK_SLACK:.0%}): nothing flies off"))


def _end_state(mesh, skinning, scales, plan, masks, end: int, start: int, hips: int, clip: str, out: List[dict], numbers: dict) -> None:
    heap, body, wings = masks
    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    point = np.asarray(plan["ground_point"], float)
    body_end = float(scales[max(end - END_FRAMES, start):end, hips].max())
    numbers["end_scale"] = round(body_end, 4)
    problems = []
    if body_end > END_SCALE * 1.01:
        problems.append(f"the body is still {body_end:.2f} of its size (limit {END_SCALE:g})")
    if heap.any():
        last = pdx_deform.skin(mesh, skinning[end - 1])[heap]
        radius = float(np.linalg.norm((last - point)[:, [0, 2]], axis=1).max())
        heap_low = float(last[:, 1].min() - ground) / height
        standing = pdx_deform.skin(mesh, skinning[0])[body & ~wings]
        footprint = float(np.linalg.norm((standing - point)[:, [0, 2]], axis=1).max())
        full = float(plan.get("heap", {}).get("radius", radius))
        numbers.update(heap_radius=round(radius, 4), heap_lowest=round(heap_low, 4), footprint=round(footprint, 4))
        if radius < 0.95 * full:
            problems.append(f"the ash heap is {radius / max(full, 1e-9):.0%} grown")
        if abs(heap_low) > GROUND_TOLERANCE:
            problems.append(f"the heap is {heap_low:.1%} of the height off the ground")
        if radius > footprint:
            problems.append("the heap is wider than the standing body")
    else:
        problems.append(f"the mesh has no {HEAP_BONE} heap")
    if problems:
        out.append(_finding("BURN-END", clip, "the burn's end state is wrong: " + ", ".join(problems)))


def burn_findings(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, plan: dict, clip: str, locators: Sequence[str] = ()) -> tuple:
    """The burn death's rules on the exported clip (see the module text). Returns (findings, numbers)."""

    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    start, end = int(plan["burn_start"]), anim.frames
    dominant = pdx_deform.dominant_bones(mesh)
    heap = dominant == (mesh.bones.index(HEAP_BONE) if HEAP_BONE in mesh.bones else -2)
    wing_bones = [i for i, name in enumerate(mesh.bones) if name.startswith("Wing")]
    body = ~heap
    legs = pdx_motion.find_legs(mesh)
    joints = pdx_motion.posed_joints(mesh, anim)
    skinning = pdx_deform.skinning_matrices(mesh, anim)
    scales = _world_scales(skinning, mesh)
    hips = legs.pelvis
    point = np.asarray(plan["ground_point"], float)
    rest_hips = float(pdx_motion.rest_joints(mesh)[hips, 1] - ground)
    out: List[dict] = []
    numbers: Dict[str, float] = {}
    _stands(mesh, joints, hips, clip, out, numbers)
    travel = float(np.ptp(joints[:, hips][:, [0, 2]], axis=0).max()) / max(rest_hips, 1e-6)
    numbers["hip_travel"] = round(travel, 3)
    if travel > TRAVEL_LIMIT:
        out.append(_finding("BURN-IN-PLACE", clip, f"the hips travel {travel:.2f} hip heights (limit {TRAVEL_LIMIT:g}): a burn stays where it stands", share=round(travel, 3)))
    series: Dict[str, list] = {"tops": [], "cells": [], "reach": []}
    lows = []
    for frame in range(end):
        posed = pdx_deform.skin(mesh, skinning[frame])
        lows.append(float(posed[:, 1].min() - ground) / height)
        if frame >= start:
            own = posed[body]
            series["tops"].append(float(own[:, 1].max() - ground) / height)
            series["cells"].append(_map_extent(own))
            series["reach"].append(float(np.linalg.norm(own - point, axis=1).max()) / height)
    _shrinks(series, scales, start, hips, clip, out, numbers)
    low, high = min(lows), max(lows)
    numbers.update(lowest=round(low, 4), highest_lowest=round(high, 4))
    if low < -GROUND_TOLERANCE or high > GROUND_TOLERANCE:
        out.append(_finding("BURN-GROUNDED", clip, f"the lowest point goes from {low:.1%} to {high:.1%} of the height off the ground (limit {GROUND_TOLERANCE:.0%} either way): it floats or sinks"))
    _end_state(mesh, skinning, scales, plan, (heap, body, np.isin(dominant, wing_bones)), end, start, hips, clip, out, numbers)
    locator_ok = plan.get("locator") in set(locators)
    timed = particles_cover(plan)
    if not locator_ok or not timed:
        out.append(_finding("BURN-PARTICLE", clip, f"the burn's locator {plan.get('locator')!r} is {'in' if locator_ok else 'missing from'} the mesh and its fire and smoke "
                            f"{'cover' if timed else 'do not cover'} the burn"))
    if wing_bones:
        over = float((scales[start:][:, wing_bones] - scales[start:, hips][:, None]).max())
        numbers["wing_over_body_scale"] = round(over, 4)
        if over > 1e-3:
            out.append(_finding("BURN-WINGS", clip, f"a wing is {over:.2f} larger in scale than the body during the burn: the wings shrink no later than the body"))
    return out, numbers


def particles_cover(plan: dict) -> bool:
    """The fire starts no later than the burn and the smoke lasts past the clip's end (`time` in seconds from the state's start)."""

    fps = max(float(plan.get("fps", 30.0)), 1.0)
    fire = [p for p in plan.get("particles", []) if p.get("standin") == "fire"]
    smoke = [p for p in plan.get("particles", []) if p.get("standin") == "smoke"]
    if not fire or not smoke:
        return False
    return min(p["time"] for p in fire) <= plan["burn_start"] / fps and max(p["time"] + p["duration_s"] for p in smoke) >= plan["frames"] / fps


def mesh_locators(mesh_path: Path) -> List[str]:
    return list(summarize_mesh(read(mesh_path)).locators)
