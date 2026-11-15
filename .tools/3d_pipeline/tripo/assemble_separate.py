"""Assemble Tripo's "separate weapon" export into one rigged GLB, with no Blender.

    py -3.13 .tools/3d_pipeline/tripo/assemble_separate.py --body-clips <folder or GLBs...> --weapon <weapon.glb>
        --length-ratio 1.06 --grip 0.60 --grip-range 0.45,0.70 --hand RightHand --out <assembled.glb>
        [--report report.json] [--max-tilt 25] [--tilt-from idle] [--roles idle=idle,walk=move,...]
        [--trade-tilts 15,25,40] [--fit-frames 16] [--weapon-triangles N]

Tripo's separate route gives a weaponless rigged body, exported once per animation clip, and the weapon
as its own unrigged model. The "in-hand" route gives one GLB with a body mesh node `tripo_part_0`, a
weapon mesh node `tripo_part_1`, one skin and every clip. This tool builds that same shape from the
separate files, so `prepare_tripo_unit.py --rigid-part tripo_part_1=RightHand` takes it unchanged:

1. Merge. Mesh, skin, materials and images come from the first body file, the animation of every other
   file is appended (channels re-pointed to the same joints by node NAME, sampler data copied into the
   output buffer). The files must hold the same rig: joint names, inverse bind matrices, rest pose, vertex
   data. Any difference stops the run with the numbers. The body mesh node is renamed `tripo_part_0`.
2. Weapon. Tripo normalises every model to one size, so the real size comes from a recorded ratio: the
   weapon's long axis (PCA) is scaled to `--length-ratio` times the body's rest height. The head end is
   the end whose cross-section is wider. The weapon becomes mesh node `tripo_part_1` under the same skin,
   every vertex weighted 1.0 to the hand joint, with its own material and images, its positions stored
   in the body's bind space at the fitted grip pose.
3. Pose fit. The palm is the centroid of the body vertices mostly weighted to the hand joint and its
   finger joints in the rest pose. The pose is the haft direction, the roll about it and the grip share
   (`--grip` is the recorded value and preferred, `--grip-range` lets the hand slide along the haft).
   The score is read from the posed body of every sampled frame of the clips in `--roles`: the body is
   voxelised per frame (surface samples, flood fill from outside, erosion for depth), so one candidate
   costs a few array lookups. Order of the score:
   (a) hard: in the tilt clip (`--tilt-from`, idle) the mean haft direction, butt to head, is within
       `--max-tilt` degrees of world up (so the head is up), and no weapon point is below the lowest
       body vertex of the frame, so the butt does not sink;
   (b) the clips failing the clip_check verdict, weighted by role (idle > move > attack > defend >
       retreat > death, a role counts as met when any of its clips passes);
   (c) the total deep penetration, then a weak pull to the recorded grip and to the fist's hole axis
       (the line through the four finger base joints).
   Coarse search in the allowed cone, pattern search around the best few, then the best candidates
   are re-ranked by real clip_check runs (ray-parity inside test). ONE pose serves all clips, because
   the game cannot change it per clip. Clips not in `--roles` (defeat_03) are only checked.
4. Verify. The assembled GLB is written and `clip_check` measures it at full sampling with per-frame
   ground, for the chosen pose and for a naive pose (haft along the fist axis, roll 0, recorded
   grip). The report also holds the best pose at other max tilts (`--trade-tilts`) and, per role, the
   best passing clip.

Decimation is not done here. `--weapon-triangles N` only flags in the report whether the weapon is above
N triangles, which the Blender stage then has to reduce.
"""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import clip_check as cc

BODY_NODE = "tripo_part_0"
WEAPON_NODE = "tripo_part_1"
FLOAT, UBYTE, USHORT, UINT = 5126, 5121, 5123, 5125
ARRAY_BUFFER, ELEMENT_ARRAY_BUFFER = 34962, 34963
TOLERANCE = 1e-5
HEAD_WEIGHT_SHARE = 0.5  # a vertex belongs to the hand when this share of its weight is on the hand joint family
FINGER_BASES = ("Index1", "Middle1", "Ring1", "Pinky1")
PENETRATION_ERODE = 4  # voxels of depth that count as through the body in the fit (about the clip_check margin)


class AssembleError(ValueError):
    """The inputs cannot be assembled."""


# ---------------------------------------------------------------------------------------------
# GLB writing
# ---------------------------------------------------------------------------------------------


class Glb:
    """A glTF document plus a growing binary chunk."""

    def __init__(self, doc: dict, binary: bytes):
        self.doc = copy.deepcopy(doc)
        self.binary = bytearray(binary)
        self.doc.setdefault("bufferViews", [])
        self.doc.setdefault("accessors", [])

    def add_view(self, data: bytes, target: Optional[int] = None) -> int:
        while len(self.binary) % 4:
            self.binary.append(0)
        view = {"buffer": 0, "byteOffset": len(self.binary), "byteLength": len(data)}
        if target:
            view["target"] = target
        self.binary += data
        self.doc["bufferViews"].append(view)
        return len(self.doc["bufferViews"]) - 1

    def add_accessor(self, array: np.ndarray, kind: str, component: int, target: Optional[int] = None, bounds: bool = False) -> int:
        dtype = {FLOAT: np.float32, UBYTE: np.uint8, USHORT: np.uint16, UINT: np.uint32}[component]
        data = np.ascontiguousarray(array, dtype=dtype)
        accessor = {"bufferView": self.add_view(data.tobytes(), target), "componentType": component, "count": int(data.shape[0]), "type": kind}
        if bounds:
            flat = data.reshape(len(data), -1)
            accessor["min"] = [float(x) for x in flat.min(axis=0)]
            accessor["max"] = [float(x) for x in flat.max(axis=0)]
        self.doc["accessors"].append(accessor)
        return len(self.doc["accessors"]) - 1

    def to_bytes(self) -> bytes:
        while len(self.binary) % 4:
            self.binary.append(0)
        self.doc["buffers"] = [{"byteLength": len(self.binary)}]
        text = json.dumps(self.doc, separators=(",", ":")).encode("utf-8")
        text += b" " * (-len(text) % 4)
        total = 12 + 8 + len(text) + 8 + len(self.binary)
        return b"glTF" + struct.pack("<II", 2, total) + struct.pack("<I4s", len(text), b"JSON") + text + struct.pack("<I4s", len(self.binary), b"BIN\0") + bytes(self.binary)


# ---------------------------------------------------------------------------------------------
# Step 1: merge the per-clip body files
# ---------------------------------------------------------------------------------------------


def _node_names(doc: dict) -> List[str]:
    """Node names, with the skinned mesh node (Tripo names it after the export id) as one fixed label."""

    return ["<body mesh>" if "skin" in n and "mesh" in n else n.get("name", str(i)) for i, n in enumerate(doc["nodes"])]


def _skinned_node(doc: dict, label: str) -> int:
    found = [i for i, n in enumerate(doc["nodes"]) if "mesh" in n and "skin" in n]
    if len(found) != 1:
        raise AssembleError(f"{label}: expected exactly one skinned mesh node, found {len(found)}")
    return found[0]


def _body_arrays(doc: dict, binary: bytes, label: str) -> dict:
    node = doc["nodes"][_skinned_node(doc, label)]
    prims = doc["meshes"][node["mesh"]]["primitives"]
    if len(prims) != 1:
        raise AssembleError(f"{label}: expected one mesh primitive, found {len(prims)}")
    attr = prims[0]["attributes"]
    skin = doc["skins"][node["skin"]]
    out = {
        "positions": cc.read_accessor(doc, binary, attr["POSITION"]),
        "joints": cc.read_accessor(doc, binary, attr["JOINTS_0"]),
        "weights": cc.read_accessor(doc, binary, attr["WEIGHTS_0"]),
        "indices": cc.read_accessor(doc, binary, prims[0]["indices"]).ravel(),
        "ibm": cc.read_accessor(doc, binary, skin["inverseBindMatrices"]),
    }
    return out


def compare_rigs(ref: Tuple[dict, bytes], other: Tuple[dict, bytes], label: str) -> Dict[str, float]:
    """Raise AssembleError unless `other` holds the same rig, mesh and rest pose as `ref`. Returns the largest differences."""

    rd, rb = ref
    od, ob = other
    problems: List[str] = []
    worst: Dict[str, float] = {}

    def note(what: str, value: float, limit: float = TOLERANCE) -> None:
        worst[what] = max(worst.get(what, 0.0), float(value))
        if value > limit:
            problems.append(f"{what} differs by {value:.3g} (limit {limit:g})")

    if len(rd["nodes"]) != len(od["nodes"]):
        raise AssembleError(f"{label}: {len(od['nodes'])} nodes, the first file has {len(rd['nodes'])}")
    if _node_names(rd) != _node_names(od):
        raise AssembleError(f"{label}: node names or their order differ from the first file")
    for index, (a, b) in enumerate(zip(rd["nodes"], od["nodes"])):
        name = _node_names(rd)[index]
        if a.get("children", []) != b.get("children", []):
            problems.append(f"node {name}: children differ")
        if a.get("skin") != b.get("skin") or a.get("mesh") != b.get("mesh"):
            problems.append(f"node {name}: mesh or skin reference differs")
        if "matrix" in a or "matrix" in b:
            continue
        t_a, t_b = np.array(a.get("translation", [0, 0, 0]), float), np.array(b.get("translation", [0, 0, 0]), float)
        s_a, s_b = np.array(a.get("scale", [1, 1, 1]), float), np.array(b.get("scale", [1, 1, 1]), float)
        q_a, q_b = np.array(a.get("rotation", [0, 0, 0, 1]), float), np.array(b.get("rotation", [0, 0, 0, 1]), float)
        note("rest translation", np.abs(t_a - t_b).max())
        note("rest scale", np.abs(s_a - s_b).max())
        note("rest rotation", 1.0 - abs(float(q_a @ q_b)) / max(np.linalg.norm(q_a) * np.linalg.norm(q_b), 1e-12), 1e-9)
    if len(rd["skins"]) != len(od["skins"]) or [rd["nodes"][j].get("name") for j in rd["skins"][0]["joints"]] != [od["nodes"][j].get("name") for j in od["skins"][0]["joints"]]:
        problems.append("skin joint names or their order differ")
    else:
        A, B = _body_arrays(rd, rb, "first file"), _body_arrays(od, ob, label)
        if len(A["positions"]) != len(B["positions"]) or len(A["indices"]) != len(B["indices"]):
            problems.append(f"vertex or index count differs ({len(B['positions'])} / {len(B['indices'])} against {len(A['positions'])} / {len(A['indices'])})")
        else:
            note("inverse bind matrix", np.abs(A["ibm"] - B["ibm"]).max())
            note("vertex position", np.abs(A["positions"] - B["positions"]).max())
            note("vertex weight", np.abs(A["weights"] - B["weights"]).max())
            if not np.array_equal(A["joints"], B["joints"]):
                problems.append("vertex joint indices differ")
            if not np.array_equal(A["indices"], B["indices"]):
                problems.append("triangle indices differ")
    if problems:
        raise AssembleError(f"{label} is not the same rig as the first file:\n  " + "\n  ".join(dict.fromkeys(problems)))
    return worst


def _append_clips(glb: Glb, other_doc: dict, other_bin: bytes, label: str, index_of: Dict[str, int], seen: Dict[str, str]) -> None:
    """Copy every animation of one clip file into `glb`, re-pointing its channels at the first file's nodes by name."""

    doc = glb.doc
    cache: Dict[int, int] = {}

    def copy_accessor(index: int) -> int:
        if index not in cache:
            acc = other_doc["accessors"][index]
            comp = acc["componentType"]
            array = cc.read_accessor(other_doc, other_bin, index)
            if acc.get("normalized"):
                raise AssembleError(f"{label}: normalised animation accessors are not supported")
            cache[index] = glb.add_accessor(array, acc["type"], comp, None, bounds="min" in acc)
        return cache[index]

    other_names = _node_names(other_doc)
    for anim in other_doc.get("animations", []):
        if anim["name"] in seen:
            raise AssembleError(f"animation {anim['name']!r} of {label} is already in {seen[anim['name']]}")
        seen[anim["name"]] = label
        samplers = [{"input": copy_accessor(s["input"]), "output": copy_accessor(s["output"]), "interpolation": s.get("interpolation", "LINEAR")} for s in anim["samplers"]]
        channels = []
        for channel in anim["channels"]:
            target = other_names[channel["target"]["node"]]
            channels.append({"sampler": channel["sampler"], "target": {"node": index_of[target], "path": channel["target"]["path"]}})
        doc.setdefault("animations", []).append({"name": anim["name"], "samplers": samplers, "channels": channels})


def merge_body_clips(paths: Sequence[Path]) -> Tuple[Glb, dict]:
    """One GLB from per-clip body files: mesh and skin of the first, every file's animation. Returns it and a report."""

    if not paths:
        raise AssembleError("no body files")
    loaded = [cc.load_glb(p) for p in paths]
    ref_doc, ref_bin = loaded[0]
    glb = Glb(ref_doc, ref_bin)
    doc = glb.doc
    skinned = _skinned_node(doc, Path(paths[0]).name)
    doc["nodes"][skinned]["name"] = BODY_NODE
    names = _node_names(ref_doc)
    index_of = {name: i for i, name in enumerate(names)}
    if len(index_of) != len(names):
        raise AssembleError("the body file has duplicate node names, channels cannot be re-pointed by name")
    seen: Dict[str, str] = {}
    for anim in doc.get("animations", []):
        seen[anim["name"]] = Path(paths[0]).name
    if not seen:
        raise AssembleError(f"{Path(paths[0]).name} has no animation")
    report = {"files": [Path(p).name for p in paths], "rest_differences": {}, "images_identical": True}
    ref_images = _image_blobs(ref_doc, ref_bin)
    for path, (other_doc, other_bin) in zip(paths[1:], loaded[1:]):
        label = Path(path).name
        for key, value in compare_rigs(loaded[0], (other_doc, other_bin), label).items():
            report["rest_differences"][key] = max(report["rest_differences"].get(key, 0.0), value)
        if _image_blobs(other_doc, other_bin) != ref_images:
            report["images_identical"] = False
        _append_clips(glb, other_doc, other_bin, label, index_of, seen)
    report["clips"] = [a["name"] for a in doc["animations"]]
    return glb, report


def _image_blobs(doc: dict, binary: bytes) -> List[bytes]:
    blobs = []
    for image in doc.get("images", []):
        if "bufferView" in image:
            view = doc["bufferViews"][image["bufferView"]]
            start = view.get("byteOffset", 0)
            blobs.append(bytes(binary[start : start + view["byteLength"]]))
        else:
            blobs.append(str(image.get("uri", "")).encode())
    return blobs


# ---------------------------------------------------------------------------------------------
# Step 2: the weapon
# ---------------------------------------------------------------------------------------------


def read_weapon(path: Path) -> dict:
    doc, binary = cc.load_glb(path)
    mesh_nodes = [n for n in doc["nodes"] if "mesh" in n]
    if len(mesh_nodes) != 1:
        raise AssembleError(f"{Path(path).name}: expected one mesh node, found {len(mesh_nodes)}")
    node = mesh_nodes[0]
    if "skin" in node:
        raise AssembleError(f"{Path(path).name}: the weapon is expected to be unrigged")
    prims = doc["meshes"][node["mesh"]]["primitives"]
    if len(prims) != 1:
        raise AssembleError(f"{Path(path).name}: expected one mesh primitive, found {len(prims)}")
    prim = prims[0]
    if prim.get("mode", 4) != 4:
        raise AssembleError(f"{Path(path).name}: the weapon is not a triangle list")
    attr = prim["attributes"]
    positions = cc.read_accessor(doc, binary, attr["POSITION"])
    if "matrix" in node:
        m = np.array(node["matrix"], float).reshape(4, 4).T
    else:
        m = cc.local_matrix(node.get("translation", [0, 0, 0]), node.get("rotation", [0, 0, 0, 1]), node.get("scale", [1, 1, 1]))
    positions = positions @ m[:3, :3].T + m[:3, 3]
    normals = cc.read_accessor(doc, binary, attr["NORMAL"]) if "NORMAL" in attr else None
    if normals is not None:
        normals = normals @ np.linalg.inv(m[:3, :3]).T
        normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    indices = cc.read_accessor(doc, binary, prim["indices"]).astype(np.int64).ravel() if "indices" in prim else np.arange(len(positions))
    return {
        "doc": doc,
        "binary": binary,
        "positions": positions,
        "normals": normals,
        "uv": cc.read_accessor(doc, binary, attr["TEXCOORD_0"]) if "TEXCOORD_0" in attr else None,
        "triangles": indices.reshape(-1, 3),
        "material": doc["materials"][prim["material"]] if "material" in prim else None,
        "name": Path(path).name,
    }


def weapon_axes(positions: np.ndarray, grip: float) -> dict:
    """Long axis (head end positive), blade-plane axis and the grip point of the weapon, in its own file space."""

    mean = positions.mean(axis=0)
    centred = positions - mean
    values, vectors = np.linalg.eigh(centred.T @ centred)
    order = np.argsort(values)[::-1]
    e1, e2 = vectors[:, order[0]], vectors[:, order[1]]
    t = centred @ e1
    low, high = float(t.min()), float(t.max())
    length = high - low

    def spread(mask: np.ndarray) -> float:
        pts = centred[mask]
        radial = pts - np.outer(pts @ e1, e1)
        return float(np.sqrt((radial * radial).sum(axis=1).mean())) if len(pts) else 0.0

    s_low, s_high = spread(t < low + 0.15 * length), spread(t > high - 0.15 * length)
    flipped = s_low > s_high
    if flipped:
        e1, t = -e1, -t
        low, high = -high, -low
        s_low, s_high = s_high, s_low
    e2 = e2 - (e2 @ e1) * e1
    e2 /= np.linalg.norm(e2)
    e3 = np.cross(e1, e2)
    return {
        "mean": mean,
        "axes": np.stack([e1, e2, e3], axis=1),  # columns
        "length": float(length),
        "butt_spread": s_low,
        "head_spread": s_high,
        "head_was_at_negative_end": bool(flipped),
        "grip_point": mean + e1 * (low + grip * length),
    }


def weapon_local(positions: np.ndarray, axes: dict, scale: float) -> np.ndarray:
    """Weapon vertices as (along the haft toward the head, blade direction, third) from the grip point, scaled to metres."""

    return scale * ((positions - axes["grip_point"]) @ axes["axes"])


def _perpendicular_basis(d: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    helper = np.zeros_like(d)
    helper[np.arange(len(d)), np.argmin(np.abs(d), axis=1)] = 1.0
    u = np.cross(d, helper)
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    return u, np.cross(d, u)


def pose_matrices(directions: np.ndarray, rolls_deg: np.ndarray) -> np.ndarray:
    """(K, 3, 3) rotations: weapon (haft, blade, third) axes to a world haft direction and a roll about it."""

    d = np.asarray(directions, float).reshape(-1, 3)
    d = d / np.linalg.norm(d, axis=1, keepdims=True)
    rolls = np.radians(np.broadcast_to(np.asarray(rolls_deg, float), (len(d),)))
    u, v = _perpendicular_basis(d)
    r = np.cos(rolls)[:, None] * u + np.sin(rolls)[:, None] * v
    return np.stack([d, r, np.cross(d, r)], axis=2)


def _copy_weapon_material(glb: Glb, weapon: dict) -> int:
    """Copy the weapon's material, with its sampler and textures, into `glb`. Returns the new material index."""

    doc = glb.doc
    material = copy.deepcopy(weapon["material"])
    src = weapon["doc"]
    material.pop("extensions", None)
    sampler_index = None
    if src.get("samplers"):
        doc.setdefault("samplers", []).append(copy.deepcopy(src["samplers"][0]))
        sampler_index = len(doc["samplers"]) - 1
    new_texture: Dict[int, int] = {}

    def remap(slot: dict) -> None:
        old = slot["index"]
        if old not in new_texture:
            texture = src["textures"][old]
            image = copy.deepcopy(src["images"][texture["source"]])
            if "bufferView" in image:
                view = src["bufferViews"][image["bufferView"]]
                start = view.get("byteOffset", 0)
                image["bufferView"] = glb.add_view(bytes(weapon["binary"][start : start + view["byteLength"]]))
            doc.setdefault("images", []).append(image)
            entry = {"source": len(doc["images"]) - 1}
            if sampler_index is not None:
                entry["sampler"] = sampler_index
            doc.setdefault("textures", []).append(entry)
            new_texture[old] = len(doc["textures"]) - 1
        slot["index"] = new_texture[old]

    for holder in (material, material.get("pbrMetallicRoughness", {})):
        for slot in list(holder.values()):
            if isinstance(slot, dict) and isinstance(slot.get("index"), int):
                remap(slot)
    doc.setdefault("materials", []).append(material)
    return len(doc["materials"]) - 1


def add_weapon(glb: Glb, weapon: dict, world_positions: np.ndarray, world_normals: Optional[np.ndarray], joint_slot: int) -> int:
    """Append the weapon as mesh node `tripo_part_1` under the skin, every vertex weighted 1.0 to skin joint `joint_slot`."""

    doc = glb.doc
    count = len(world_positions)
    attributes = {"POSITION": glb.add_accessor(world_positions, "VEC3", FLOAT, ARRAY_BUFFER, bounds=True)}
    if world_normals is not None:
        attributes["NORMAL"] = glb.add_accessor(world_normals, "VEC3", FLOAT, ARRAY_BUFFER)
    if weapon["uv"] is not None:
        attributes["TEXCOORD_0"] = glb.add_accessor(weapon["uv"], "VEC2", FLOAT, ARRAY_BUFFER)
    joints = np.zeros((count, 4), np.uint8)
    joints[:, 0] = joint_slot
    weights = np.zeros((count, 4), np.float32)
    weights[:, 0] = 1.0
    attributes["JOINTS_0"] = glb.add_accessor(joints, "VEC4", UBYTE, ARRAY_BUFFER)
    attributes["WEIGHTS_0"] = glb.add_accessor(weights, "VEC4", FLOAT, ARRAY_BUFFER)
    flat = weapon["triangles"].ravel()
    indices = glb.add_accessor(flat, "SCALAR", USHORT if count < 65535 else UINT, ELEMENT_ARRAY_BUFFER)
    primitive = {"attributes": attributes, "indices": indices, "mode": 4}

    if weapon["material"] is not None:
        primitive["material"] = _copy_weapon_material(glb, weapon)

    doc.setdefault("meshes", []).append({"name": "tripo_mesh_weapon", "primitives": [primitive]})
    doc["nodes"].append({"name": WEAPON_NODE, "mesh": len(doc["meshes"]) - 1, "skin": 0})
    node_index = len(doc["nodes"]) - 1
    skinned = next(i for i, n in enumerate(doc["nodes"]) if n.get("name") == BODY_NODE)
    parent = next((n for n in doc["nodes"] if skinned in n.get("children", [])), None)
    if parent is not None:
        parent["children"].append(node_index)
    else:
        doc["scenes"][doc.get("scene", 0)]["nodes"].append(node_index)
    return node_index


# ---------------------------------------------------------------------------------------------
# Step 3: the grip fit
# ---------------------------------------------------------------------------------------------


def surface_samples(points: np.ndarray, triangles: np.ndarray, voxel: float) -> np.ndarray:
    """Points on every triangle, dense enough that no voxel the surface crosses is skipped."""

    a, b, c = points[triangles[:, 0]], points[triangles[:, 1]], points[triangles[:, 2]]
    edge = np.maximum.reduce([np.linalg.norm(a - b, axis=1), np.linalg.norm(b - c, axis=1), np.linalg.norm(c - a, axis=1)])
    n = np.clip(np.ceil(edge / (0.5 * voxel)).astype(int), 1, 256)
    out = []
    for k in np.unique(n):
        sel = n == k
        lattice = np.array([(i / k, j / k) for i in range(k + 1) for j in range(k + 1 - i)])
        wb, wc = lattice[:, 0], lattice[:, 1]
        wa = 1.0 - wb - wc
        out.append((a[sel][:, None, :] * wa[None, :, None] + b[sel][:, None, :] * wb[None, :, None] + c[sel][:, None, :] * wc[None, :, None]).reshape(-1, 3))
    return np.concatenate(out)


def _neighbours_or(x: np.ndarray) -> np.ndarray:
    out = x.copy()
    out[1:] |= x[:-1]
    out[:-1] |= x[1:]
    out[:, 1:] |= x[:, :-1]
    out[:, :-1] |= x[:, 1:]
    out[:, :, 1:] |= x[:, :, :-1]
    out[:, :, :-1] |= x[:, :, 1:]
    return out


def _erode(x: np.ndarray) -> np.ndarray:
    out = x.copy()
    out[1:] &= x[:-1]
    out[0] = False
    out[:-1] &= x[1:]
    out[-1] = False
    out[:, 1:] &= x[:, :-1]
    out[:, 0] = False
    out[:, :-1] &= x[:, 1:]
    out[:, -1] = False
    out[:, :, 1:] &= x[:, :, :-1]
    out[:, :, 0] = False
    out[:, :, :-1] &= x[:, :, 1:]
    out[:, :, -1] = False
    return out


class FrameGrid:
    """The body of one frame as voxels: bit 0 = inside or on the surface, bit 1 = deeper than the fit margin."""

    def __init__(self, points: np.ndarray, triangles: np.ndarray, voxel: float, erode: int):
        pad = erode + 3
        self.voxel = voxel
        self.origin = points.min(axis=0) - pad * voxel
        shape = np.ceil((points.max(axis=0) + pad * voxel - self.origin) / voxel).astype(int) + 1
        self.shape = tuple(int(x) for x in shape)
        idx = np.floor((surface_samples(points, triangles, voxel) - self.origin) / voxel).astype(int)
        occupied = np.zeros(self.shape, dtype=bool)
        occupied[idx[:, 0], idx[:, 1], idx[:, 2]] = True
        occupied = _neighbours_or(occupied)
        reach = np.zeros(self.shape, dtype=bool)
        reach[0, 0, 0] = True
        count = 1
        while True:
            reach = _neighbours_or(reach) & ~occupied
            now = int(reach.sum())
            if now == count:
                break
            count = now
        solid = ~reach
        deep = solid
        for _ in range(erode):
            deep = _erode(deep)
        self.flags = solid.astype(np.uint8) | (deep.astype(np.uint8) << 1)
        self.lowest = float(points[:, 1].min())

    def lookup(self, world: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """(inside, deep) booleans for world points of any shape (..., 3)."""

        idx = np.floor((world - self.origin) / self.voxel).astype(np.int64)
        shape = np.array(self.shape)
        valid = np.all((idx >= 0) & (idx < shape), axis=-1)
        idx = np.clip(idx, 0, shape - 1)
        flags = self.flags[idx[..., 0], idx[..., 1], idx[..., 2]]
        flags = np.where(valid, flags, 0)
        return (flags & 1).astype(bool), ((flags >> 1) & 1).astype(bool)


def fibonacci_sphere(count: int) -> np.ndarray:
    i = np.arange(count) + 0.5
    phi = math.pi * (3.0 - math.sqrt(5.0)) * i
    y = 1.0 - 2.0 * i / count
    r = np.sqrt(np.maximum(1.0 - y * y, 0.0))
    return np.stack([np.cos(phi) * r, y, np.sin(phi) * r], axis=1)


def fibonacci_cap(count: int, half_angle_deg: float) -> np.ndarray:
    """Directions spread over the cap of half angle `half_angle_deg` around +z."""

    i = np.arange(count) + 0.5
    z = 1.0 - (1.0 - math.cos(math.radians(half_angle_deg))) * i / count
    phi = math.pi * (3.0 - math.sqrt(5.0)) * i
    r = np.sqrt(np.maximum(1.0 - z * z, 0.0))
    return np.stack([np.cos(phi) * r, np.sin(phi) * r, z], axis=1)


def pca_axis(points: np.ndarray) -> np.ndarray:
    centred = points - points.mean(axis=0)
    values, vectors = np.linalg.eigh(centred.T @ centred)
    return vectors[:, int(np.argmax(values))]


def joint_family(names: Sequence[str], hand: int) -> List[int]:
    base = names[hand]
    return [i for i, name in enumerate(names) if name.startswith(base)]


def grip_geometry(rig: "cc.Rig", hand: int, rest_body: np.ndarray, rest_worlds: np.ndarray) -> dict:
    """The palm point and the fist's hole axis in the rest pose."""

    family = joint_family(rig.joint_names, hand)
    on_hand = np.zeros(len(rest_body))
    for slot in range(4):
        on_hand += rig.body["weights"][:, slot] * np.isin(rig.body["joint_ids"][:, slot], family)
    mask = on_hand >= HEAD_WEIGHT_SHARE
    if mask.sum() < 4:
        raise AssembleError(f"fewer than 4 body vertices are weighted to {rig.joint_names[hand]} and its fingers")
    palm = rest_body[mask].mean(axis=0)
    # Fingers only, no thumb: the fist's hole axis is the row of the finger bases.
    bases = [i for i in family if rig.joint_names[i].endswith(FINGER_BASES)]
    finger_ids = [i for i in family if i != hand and "Thumb" not in rig.joint_names[i]]
    on_fingers = np.zeros(len(rest_body))
    for slot in range(4):
        on_fingers += rig.body["weights"][:, slot] * np.isin(rig.body["joint_ids"][:, slot], finger_ids)
    finger_axis = pca_axis(rest_body[on_fingers >= HEAD_WEIGHT_SHARE]) if (on_fingers >= HEAD_WEIGHT_SHARE).sum() >= 4 else None
    knuckle_axis = pca_axis(rest_worlds[bases, :3, 3]) if len(bases) >= 3 else None
    axis = knuckle_axis if knuckle_axis is not None else finger_axis
    if axis is None:
        raise AssembleError("cannot estimate the fist axis: no finger base joints and no finger vertices")
    angle = None
    if knuckle_axis is not None and finger_axis is not None:
        angle = float(np.degrees(np.arccos(min(1.0, abs(float(knuckle_axis @ finger_axis))))))
    return {
        "palm": palm,
        "hand_vertices": int(mask.sum()),
        "fist_axis": axis,
        "fist_axis_source": "finger base joints" if knuckle_axis is not None else "finger vertices PCA",
        "fist_axis_from_finger_vertices": finger_axis,
        "knuckle_vs_finger_vertex_axis_deg": angle,
    }


ROLE_MAP = {"idle": "idle", "walk": "move", "hit_to_body_01": "defend", "flee_01": "retreat", "defeat_02": "death", "chop": "attack", "pitch_baseball": "attack", "box_01": "attack"}
ROLE_WEIGHTS = {"idle": 6.0, "move": 5.0, "attack": 4.0, "defend": 3.0, "retreat": 2.0, "death": 1.0}
SOFT_DEEP, SOFT_GROUND = 0.05, 0.04  # proxy shares at which a clip counts as fully failed in the fit (the proxy over-reports depth)
# An attack moves the weapon: the head tip must travel at least this many body heights over the clip. The old sideways swing
# and the idle breathing are far below it, a real chop or swing is 2 to 4.
ATTACK_MIN_HEAD_TRAVEL = 1.0
# A death ends with the body on the ground: its vertical extent in the last frame is under this share of the standing height.
FALLEN_MAX_EXTENT = 0.45
# Below-ground tolerance of a clip that really falls, as a share of the body height. The weapon lies beside or under the
# fallen body, its haft held by a fist that itself rests on the floor, and a haft is about 3 % of the height thick, plus the
# fist radius (3 to 4 %). Half of that again would be hidden by the body's own lowest vertex. 5 % lets a weapon rest on the
# ground and still refuses one that is pushed a hand's width into it. The other clips keep 2 %.
DEATH_GROUND_TOLERANCE_SHARE = 0.05
PATH_SAMPLES = 60  # frames per clip for the weapon head path


def resolve_clip(wanted: str, names: Sequence[str]) -> Optional[str]:
    """The clip a name or an unambiguous prefix stands for, None when no clip matches. Several matches stop the run."""

    names = sorted(set(names))
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from lib.tripo import resolve_clip_name

        try:
            return resolve_clip_name(wanted, names)
        except ValueError as problem:
            if "several" in str(problem):
                raise AssembleError(str(problem)) from problem
            return None
    except ImportError:
        pass
    if wanted in names:
        return wanted
    found = [n for n in names if n.startswith(wanted)]
    if len(found) > 1:
        raise AssembleError(f"The clip name {wanted!r} matches several clips. The file has these clips: {names}")
    return found[0] if found else None


def role_groups(role_map: Dict[str, str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for clip, role in role_map.items():
        groups.setdefault(role, []).append(clip)
    return groups


def role_summary(clips: Dict[str, dict], role_map: Dict[str, str], eligible: Optional[Dict[str, Tuple[bool, str]]] = None) -> Tuple[float, Dict[str, dict]]:
    """Weighted cost of the roles no clip of which passes, and per role the best passing clip (lowest deep share).

    A clip that passes the clip_check verdict but is not eligible (an attack that does not move the weapon,
    a death that does not fall) does not meet its role."""

    eligible = eligible or {}
    cost, summary = 0.0, {}
    for role, names in role_groups(role_map).items():
        have = [n for n in names if n in clips]
        if not have:
            continue
        status = {}
        for n in have:
            ok, why = eligible.get(n, (True, ""))
            status[n] = ("pass" if clips[n]["verdict"] == "pass" else "fail") if ok else why
        passing = [n for n in have if status[n] == "pass"]
        best = min(passing, key=lambda n: (clips[n]["weapon_deep_in_body_pct"], clips[n]["weapon_below_ground_pct"])) if passing else None
        weight = ROLE_WEIGHTS.get(role, 1.0)
        failing = len(have) - len(passing)
        cost += weight * ((0.0 if passing else 1.0) + 0.1 * failing / len(have))
        summary[role] = {"best_passing_clip": best, "clips": status}
    return cost, summary


# ---------------------------------------------------------------------------------------------
# The fist
# ---------------------------------------------------------------------------------------------


def _unit(v: np.ndarray) -> np.ndarray:
    return v / max(float(np.linalg.norm(v)), 1e-12)


def fist_hole_axis(names: Sequence[str], hand_name: str, joint_pos: np.ndarray) -> Tuple[Optional[np.ndarray], dict]:
    """The axis a closed fist wraps around, from the finger joints (any pose).

    Two estimates that should agree. The knuckle line: the finger base joints (Index1 to Pinky1) lie in a
    row across the hand, and a rod held in the fist runs along that row. The flexion planes: each finger's
    joints 1 to 4 curl in a plane, and a rod gripped by the curled fingers is perpendicular to every one of
    those planes, so the smallest singular vector of a finger's joint positions is the rod direction. The
    result is the knuckle line plus the mean flexion normal (sign aligned). `spread_deg` is how far the
    estimates disagree, the measure of how much the estimate can be trusted."""

    index = {n: i for i, n in enumerate(names)}
    fingers = ("Index", "Middle", "Ring", "Pinky")
    bases = [joint_pos[index[f"{hand_name}{f}1"]] for f in fingers if f"{hand_name}{f}1" in index]
    knuckle = pca_axis(np.array(bases)) if len(bases) >= 3 else None
    normals = []
    for f in fingers:
        chain = [index[f"{hand_name}{f}{k}"] for k in (1, 2, 3, 4) if f"{hand_name}{f}{k}" in index]
        if len(chain) >= 3:
            p = joint_pos[chain]
            normals.append(np.linalg.svd(p - p.mean(axis=0))[2][-1])
    reference = knuckle if knuckle is not None else (normals[0] if normals else None)
    if reference is None:
        return None, {}
    normals = [n if float(n @ reference) >= 0 else -n for n in normals]
    flexion = _unit(np.mean(normals, axis=0)) if normals else None
    axis = _unit(reference + (flexion if flexion is not None else 0.0)) if knuckle is not None and flexion is not None else _unit(reference)
    ang = lambda a, b: float(np.degrees(np.arccos(min(1.0, abs(float(a @ b))))))
    details = {
        "knuckle_vs_flexion_deg": None if knuckle is None or flexion is None else ang(knuckle, flexion),
        "flexion_normals_spread_deg": None if flexion is None else max(ang(n, flexion) for n in normals),
        "fingers_used": len(normals),
    }
    return axis, details


def fist_geometry(rig: "cc.Rig", hand: int, rest_body: np.ndarray, rest_worlds: np.ndarray) -> dict:
    """The right fist in the rest pose: finger vertices, their centroid, the fist radius and the hole axis with its reliability."""

    names = rig.joint_names
    family = joint_family(names, hand)
    fingers = [i for i in family if i != hand]
    share = np.zeros(len(rest_body))
    for slot in range(4):
        share += rig.body["weights"][:, slot] * np.isin(rig.body["joint_ids"][:, slot], fingers)
    mask = share >= HEAD_WEIGHT_SHARE
    if mask.sum() < 4:
        raise AssembleError(f"fewer than 4 body vertices are weighted to the fingers of {names[hand]}")
    centroid = rest_body[mask].mean(axis=0)
    radius = float(np.median(np.linalg.norm(rest_body[mask] - centroid, axis=1)))
    axis, details = fist_hole_axis(names, names[hand], rest_worlds[:, :3, 3])
    pca = pca_axis(rest_body[mask])
    if axis is None:
        axis = pca
    details["finger_vertex_pca_vs_axis_deg"] = float(np.degrees(np.arccos(min(1.0, abs(float(pca @ axis))))))
    return {"mask": mask, "centroid": centroid, "radius": radius, "axis": axis, "details": details, "vertices": int(mask.sum()), "hand_name": names[hand]}


REFINE_STEPS = [(6.0, 0.03), (3.0, 0.015), (1.5, 0.0075)]  # (degrees, grip share) of the pattern search, coarse to fine


def _distinct_poses(a: dict, b: dict) -> bool:
    """True when two candidate poses differ enough to both be kept (haft angle, grip share or roll)."""

    return np.degrees(np.arccos(np.clip(a["direction"] @ b["direction"], -1, 1))) > 8 or abs(a["grip"] - b["grip"]) > 0.05 or abs(((a["roll_deg"] - b["roll_deg"]) + 180) % 360 - 180) > 60


class Fit:
    """Scores weapon poses against the posed body of many frames.

    A pose is the haft direction (butt to head, in the rest world), the roll about it and the grip share
    (where along the weapon the palm sits). Hard rules: in the tilt clip (idle) the haft is within the
    maximum tilt of world up with the head up, no weapon point is below the lowest body vertex of the
    frame, and the haft axis passes within the fist radius of the finger vertices' centroid in the rest
    pose and in idle. The soft score weighs the clips by role (an attack that does not move the weapon
    and a death that does not fall count as failed), then the total deep penetration, then the angle
    between haft and the fist's hole axis."""

    def __init__(self, rig, hand: int, geometry: dict, fist: dict, local_points: np.ndarray, length: float, grip_ref: float, role_map: Dict[str, str], frames: int, voxel_share: float, tilt_from: str = "idle", grip_radius: float = cc.GRIP_RADIUS_SHARE, log=print):
        rest_worlds = rig.joint_worlds({})
        rest_body = rig.skin(rig.body, rig.skin_mats(rest_worlds))
        self.height = float(rest_body[:, 1].max() - rest_body[:, 1].min())
        self.palm = geometry["palm"]
        self.hand_rest = rest_worlds[hand][:3, 3]
        self.free_radius = grip_radius * self.height
        self.length, self.grip_ref, self.tilt_from = length, grip_ref, tilt_from
        self.fist = fist
        self._pick_points(local_points)
        voxel = voxel_share * self.height
        self.available = [name for name, _t, _e in rig.clips()]
        self._map_roles(role_map, log)
        self.roles = role_groups(self.role_map)
        tilt_clip = resolve_clip(tilt_from, self.available) if tilt_from else None
        wanted = list(self.role_map) + ([tilt_clip] if tilt_clip and tilt_clip not in self.role_map else [])
        started = time.time()
        fist_c, fist_h = self._voxelise_frames(rig, hand, wanted, frames, voxel)
        self.clips = list(dict.fromkeys(self.frame_clip))
        self._set_tilt_reference(tilt_clip, rest_body, fist_c, fist_h, log)
        self._sample_head_paths(rig, hand, wanted)
        self.falls = {c: self.extent.get(c, 1.0) < FALLEN_MAX_EXTENT for c, r in self.role_map.items() if r == "death"}
        self.ground_tolerance = {c: DEATH_GROUND_TOLERANCE_SHARE for c, ok in self.falls.items() if ok}
        log(f"  voxelised {len(self.grids)} frames of {len(self.clips)} clips in {time.time() - started:.0f} s, voxel {voxel:.4f}")

    def _pick_points(self, local_points: np.ndarray) -> None:
        """The weapon points the score uses: an even pick along the cloud plus its two extremes."""

        pick = np.linspace(0, len(local_points) - 1, min(cc.MAX_WEAPON_POINTS, len(local_points))).astype(int)
        extremes = [int(np.argmin(local_points[:, 0])), int(np.argmax(local_points[:, 0]))]
        self.points = local_points[np.unique(np.concatenate([pick, extremes]))]
        self.tip_local = local_points[int(np.argmax(local_points[:, 0]))].copy()

    def _map_roles(self, role_map: Dict[str, str], log) -> None:
        """`self.role_map`: the role map with each clip name resolved against the file's clips."""

        self.role_map = {}
        for clip, role in role_map.items():
            found = resolve_clip(clip, self.available)
            if found is None:
                log(f"  clip {clip!r} of the role map is not in the file, skipped")
            else:
                self.role_map[found] = role
        if not self.role_map:
            raise AssembleError(f"none of the role map clips {list(role_map)} is in the file; the clips are {self.available}")

    def _voxelise_frames(self, rig, hand: int, wanted: Sequence[str], frames: int, voxel: float) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Pose the body at `frames` steps of each wanted clip and voxelise it. Returns the fist centroid and hole axis per frame."""

        self.grids: List[FrameGrid] = []
        self.mats: List[np.ndarray] = []
        self.frame_clip: List[str] = []
        fist_c: List[np.ndarray] = []
        fist_h: List[np.ndarray] = []
        self.extent: Dict[str, float] = {}
        tri = rig.body["triangles"]
        fist = self.fist
        for name, tracks, end in rig.clips():
            if name not in wanted:
                continue
            for step in range(frames):
                t = end * step / max(frames - 1, 1)
                worlds = rig.joint_worlds(rig.pose_for(tracks, t))
                mats = rig.skin_mats(worlds)
                body = rig.skin(rig.body, mats)
                if step == frames - 1:
                    self.extent[name] = float(body[:, 1].max() - body[:, 1].min()) / self.height
                self.grids.append(FrameGrid(body, tri, voxel, PENETRATION_ERODE))
                self.mats.append(mats[hand])
                self.frame_clip.append(name)
                inv = np.linalg.inv(mats[hand])
                fist_c.append((inv @ np.append(body[fist["mask"]].mean(axis=0), 1.0))[:3])
                axis, _ = fist_hole_axis(rig.joint_names, fist["hand_name"], worlds[:, :3, 3])
                fist_h.append(_unit(np.linalg.inv(mats[hand][:3, :3]) @ axis) if axis is not None else fist["axis"])
        return fist_c, fist_h

    def _set_tilt_reference(self, tilt_clip: Optional[str], rest_body: np.ndarray, fist_c: Sequence[np.ndarray], fist_h: Sequence[np.ndarray], log) -> None:
        """The frames the tilt rules measure against (the tilt clip, else the rest pose) and the fist measures taken on them."""

        fist = self.fist
        ref = [i for i, c in enumerate(self.frame_clip) if c == tilt_clip]
        if ref:
            self.ref_mats = [self.mats[i] for i in ref]
            self.ref_lowest = [self.grids[i].lowest for i in ref]
            self.ref_name = tilt_clip
        else:
            log(f"  tilt clip {self.tilt_from!r} is not in the file: the rest pose is used")
            self.ref_mats, self.ref_lowest, self.ref_name = [np.eye(4)], [float(rest_body[:, 1].min())], "rest pose"
        # The fist measures: the rest pose first, then the tilt clip's frames, all in the hand's rest frame.
        self.fist_c = np.array([fist["centroid"]] + [fist_c[i] for i in ref])
        self.fist_h = np.array([fist["axis"]] + [fist_h[i] for i in ref])
        self.fist_labels = ["rest"] + [f"{self.ref_name} frame {k}" for k in range(len(ref))]

    def _sample_head_paths(self, rig, hand: int, wanted: Sequence[str]) -> None:
        """Weapon head path: hand matrices of dense frames per clip."""

        self.path: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
        for name, tracks, end in rig.clips():
            if name not in wanted:
                continue
            times = end * np.arange(PATH_SAMPLES) / (PATH_SAMPLES - 1)
            self.path[name] = (times, np.array([rig.skin_mats(rig.joint_worlds(rig.pose_for(tracks, t)))[hand] for t in times]))

    # -- measures of one pose -------------------------------------------------------------------

    def _tip_rest(self, d: np.ndarray, r: np.ndarray, g: np.ndarray) -> np.ndarray:
        local = np.broadcast_to(self.tip_local, (len(d), 3)).copy()
        local[:, 0] += -(g - self.grip_ref) * self.length
        return self.palm + np.einsum("kij,kj->ki", pose_matrices(d, r), local)

    def head_path(self, d: np.ndarray, r: np.ndarray, g: np.ndarray, clip: str) -> np.ndarray:
        """(K, F, 3) world positions of the head tip over the sampled frames of a clip."""

        times, mats = self.path[clip]
        tip = self._tip_rest(d, r, g)
        return np.einsum("fij,kj->kfi", mats[:, :3, :3], tip) + mats[None, :, :3, 3]

    def head_motion(self, direction: np.ndarray, grip: float, roll_deg: float, clip: str) -> dict:
        """Path length and top speed of the head tip over a clip, in body heights and body heights per second, and its highest and lowest frames."""

        d = np.asarray(direction, float)[None]
        path = self.head_path(d, np.array([roll_deg]), np.array([grip]), clip)[0]
        times = self.path[clip][0]
        steps = np.linalg.norm(np.diff(path, axis=0), axis=1)
        return {
            "head_travel_body_heights": float(steps.sum() / self.height),
            "head_max_speed_body_heights_per_s": float((steps / np.maximum(np.diff(times), 1e-9)).max() / self.height),
            "highest_head_time": float(times[int(np.argmax(path[:, 1]))]),
            "lowest_head_time": float(times[int(np.argmin(path[:, 1]))]),
        }

    def eligibility(self, direction: np.ndarray, grip: float, roll_deg: float) -> Dict[str, Tuple[bool, str]]:
        out: Dict[str, Tuple[bool, str]] = {}
        for clip, role in self.role_map.items():
            if role == "attack":
                travel = self.head_motion(direction, grip, roll_deg, clip)["head_travel_body_heights"]
                out[clip] = (travel >= ATTACK_MIN_HEAD_TRAVEL, f"not an attack: the head travels {travel:.2f} body heights, under {ATTACK_MIN_HEAD_TRAVEL:g}")
            elif role == "death":
                out[clip] = (self.falls[clip], f"not a death: the body is {100 * self.extent.get(clip, 1.0):.0f}% of its height in the last frame, not under {100 * FALLEN_MAX_EXTENT:.0f}%")
        return out

    def tilt_and_margin(self, direction: np.ndarray, grip: float, roll_deg: float) -> Tuple[float, float]:
        """Tilt from world up (degrees, mean haft direction over the tilt clip) and the lowest weapon point above the ground (metres)."""

        res = self._hard(np.asarray(direction, float)[None], np.array([roll_deg]), np.array([grip]))
        return float(res["tilt"][0]), float(res["margin"][0])

    def fist_numbers(self, direction: np.ndarray) -> dict:
        """Distance (cm) from the haft axis to the finger centroid and the angle (degrees) to the fist's hole axis, per frame set."""

        res = self._hard(np.asarray(direction, float)[None], np.array([0.0]), np.array([self.grip_ref]))
        dist, ang = res["fist_dist_each"][0], res["fist_angle_each"][0]
        idle = [i for i, label in enumerate(self.fist_labels) if label != "rest"]
        out = {"fist_radius_cm": round(100 * self.fist["radius"], 2), "rest": {"distance_cm": round(100 * float(dist[0]), 2), "angle_deg": round(float(ang[0]), 1)}}
        if idle:
            out[self.ref_name] = {"distance_cm_worst": round(100 * float(dist[idle].max()), 2), "angle_deg_mean": round(float(ang[idle].mean()), 1)}
        return out

    def _rest_points(self, d: np.ndarray, r: np.ndarray, g: np.ndarray) -> np.ndarray:
        Q = pose_matrices(d, r)
        local = np.broadcast_to(self.points, (len(d),) + self.points.shape).copy()
        local[:, :, 0] += (-(g - self.grip_ref) * self.length)[:, None]
        return self.palm + np.einsum("kij,knj->kni", Q, local)

    def _hard(self, d: np.ndarray, r: np.ndarray, g: np.ndarray, X: Optional[np.ndarray] = None) -> dict:
        d = d / np.linalg.norm(d, axis=1, keepdims=True)
        if X is None:
            X = self._rest_points(d, r, g)
        mean = np.mean([d @ m[:3, :3].T for m in self.ref_mats], axis=0)
        tilt = np.degrees(np.arccos(np.clip(mean[:, 1] / np.linalg.norm(mean, axis=1), -1, 1)))
        margin = np.min([((X @ m[:3, :3].T + m[:3, 3])[..., 1].min(axis=1) - low) for m, low in zip(self.ref_mats, self.ref_lowest)], axis=0)
        rel = self.fist_c - self.palm  # (F, 3)
        along = d @ rel.T  # (K, F)
        dist = np.linalg.norm(rel[None] - along[..., None] * d[:, None, :], axis=2)
        angle = np.degrees(np.arccos(np.clip(np.abs(d @ self.fist_h.T), 0, 1)))
        return {"tilt": tilt, "margin": margin, "fist_dist": dist.max(axis=1), "fist_angle": angle.mean(axis=1), "fist_dist_each": dist, "fist_angle_each": angle}

    def evaluate(self, directions: np.ndarray, rolls: np.ndarray, grips: np.ndarray, max_tilt: float, batch: int = 64) -> dict:
        directions = np.asarray(directions, float).reshape(-1, 3)
        directions = directions / np.linalg.norm(directions, axis=1, keepdims=True)
        rolls = np.broadcast_to(np.asarray(rolls, float), (len(directions),))
        grips = np.broadcast_to(np.asarray(grips, float), (len(directions),))
        parts = []
        for start in range(0, len(directions), batch):
            parts.append(self._batch(directions[start : start + batch], rolls[start : start + batch], grips[start : start + batch], max_tilt))
        return {key: np.concatenate([p[key] for p in parts]) for key in parts[0]}

    def _batch(self, d: np.ndarray, r: np.ndarray, g: np.ndarray, max_tilt: float) -> dict:
        X = self._rest_points(d, r, g)
        hard = self._hard(d, r, g, X)
        violation = np.maximum(0.0, hard["tilt"] - max_tilt) * 0.1 + np.maximum(0.0, -hard["margin"]) * 10.0 + np.maximum(0.0, hard["fist_dist"] - self.fist["radius"]) * 10.0
        free = np.linalg.norm(X - self.hand_rest, axis=2) > self.free_radius
        nfree = np.maximum(free.sum(axis=1), 1)
        values = {c: {"deep": [], "ground": []} for c in self.clips}
        for grid, mat, clip in zip(self.grids, self.mats, self.frame_clip):
            world = X @ mat[:3, :3].T + mat[:3, 3]
            _inside, deep = grid.lookup(world)
            tolerance = self.ground_tolerance.get(clip, cc.FRAME_GROUND_TOLERANCE_SHARE)
            values[clip]["deep"].append((deep & free).sum(axis=1) / nfree)
            values[clip]["ground"].append((world[..., 1] < grid.lowest - tolerance * self.height).mean(axis=1))
        soft, deep_total, ground_total = {}, np.zeros(len(d)), np.zeros(len(d))
        for clip, v in values.items():
            fd, fg = np.stack(v["deep"]).max(0), np.stack(v["ground"]).max(0)
            soft[clip] = np.minimum(1.0, fd / SOFT_DEEP) + np.minimum(1.0, fg / SOFT_GROUND)
            deep_total += fd
            ground_total += fg
            role = self.role_map.get(clip)
            if role == "attack":
                steps = np.linalg.norm(np.diff(self.head_path(d, r, g, clip), axis=1), axis=2).sum(axis=1) / self.height
                soft[clip] = np.where(steps < ATTACK_MIN_HEAD_TRAVEL, 2.0, soft[clip])
            elif role == "death" and not self.falls[clip]:
                soft[clip] = np.full(len(d), 2.0)
        cost = np.zeros(len(d))
        for role, names in self.roles.items():
            s = np.stack([soft[n] for n in names])
            cost += ROLE_WEIGHTS.get(role, 1.0) * (s.min(0) + 0.1 * s.mean(0))
        score = np.where(violation > 0, 1000.0 + 100.0 * violation, 0.0) + cost + 0.2 * deep_total + 0.02 * ground_total + 0.05 * np.abs(g - self.grip_ref) + 0.004 * hard["fist_angle"]
        return {"score": score, "violation": violation, "tilt": hard["tilt"], "margin": hard["margin"], "fist_dist": hard["fist_dist"], "fist_angle": hard["fist_angle"]}

    # -- search -----------------------------------------------------------------------------------

    def up_in_rest(self) -> np.ndarray:
        up = np.array([0.0, 1.0, 0.0])
        d = np.mean([m[:3, :3].T @ up for m in self.ref_mats], axis=0)
        return d / np.linalg.norm(d)

    def _search_grid(self, max_tilt: float, grip_range: Tuple[float, float], directions: int, rolls: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """The coarse grid of poses: every direction of the cone, every roll, every grip."""

        lo, hi = grip_range
        d0 = self.up_in_rest()
        u, v = _perpendicular_basis(d0[None])
        frame = np.stack([u[0], v[0], d0], axis=1)
        cone = fibonacci_cap(directions, max_tilt) @ frame.T
        grips = np.unique(np.concatenate([np.linspace(lo, hi, 6), [min(max(self.grip_ref, lo), hi)]]))
        roll_set = np.arange(rolls) * 360.0 / rolls
        D = np.repeat(cone, rolls * len(grips), axis=0)
        R = np.tile(np.repeat(roll_set, len(grips)), len(cone))
        G = np.tile(grips, len(cone) * rolls)
        return D, R, G

    def _refine_seed(self, seed: dict, max_tilt: float, grip_range: Tuple[float, float]) -> dict:
        """Pattern search around one seed with shrinking steps; stops a step size as soon as no neighbour is better."""

        lo, hi = grip_range
        d, roll, grip, score = seed["direction"], seed["roll_deg"], seed["grip"], seed["score"]
        for angle_step, grip_step in REFINE_STEPS:
            for _ in range(6):
                pu, pv = _perpendicular_basis(d[None])
                cd, cr, cg = [], [], []
                for a, b, c, e in itertools.product((-1, 0, 1), repeat=4):
                    nd = d + math.tan(math.radians(angle_step)) * (a * pu[0] + b * pv[0])
                    cd.append(nd / np.linalg.norm(nd))
                    cr.append(roll + c * angle_step)
                    cg.append(min(max(grip + e * grip_step, lo), hi))
                res = self.evaluate(np.array(cd), np.array(cr), np.array(cg), max_tilt)
                k = int(np.argmin(res["score"]))
                if res["score"][k] >= score - 1e-9:
                    break
                d, roll, grip, score = cd[k], cr[k], cg[k], float(res["score"][k])
        return {"direction": d, "roll_deg": roll % 360.0, "grip": grip, "score": score}

    def search(self, max_tilt: float, grip_range: Tuple[float, float], directions: int = 120, rolls: int = 8, keep: int = 6, log=print) -> List[dict]:
        """Local optima of the proxy score, best first. Raises AssembleError when the hard rules cannot be met."""

        lo, hi = grip_range
        D, R, G = self._search_grid(max_tilt, grip_range, directions, rolls)
        started = time.time()
        coarse = self.evaluate(D, R, G, max_tilt)
        order = np.argsort(coarse["score"])
        if coarse["violation"][order[0]] > 0:
            i = order[0]
            raise AssembleError(
                f"no pose meets the hard rules (haft within {max_tilt:g} degrees of up in {self.ref_name}, weapon above the ground, "
                f"haft axis within the fist radius {100 * self.fist['radius']:.1f} cm) with the grip between {lo:g} and {hi:g}: "
                f"the closest has tilt {coarse['tilt'][i]:.1f}, its lowest point {coarse['margin'][i] * 100:.1f} cm from the ground "
                f"and the axis {coarse['fist_dist'][i] * 100:.1f} cm from the finger centroid"
            )
        seeds: List[dict] = []
        for i in order:
            if coarse["violation"][i] > 0:
                break
            cand = {"direction": D[i], "roll_deg": float(R[i]), "grip": float(G[i]), "score": float(coarse["score"][i])}
            if all(_distinct_poses(cand, s) for s in seeds):
                seeds.append(cand)
            if len(seeds) >= keep:
                break
        log(f"  coarse search of {len(D)} poses in {time.time() - started:.0f} s, best proxy score {coarse['score'][order[0]]:.4f}")
        refined: List[dict] = []
        for seed in seeds:
            cand = self._refine_seed(seed, max_tilt, grip_range)
            if all(_distinct_poses(cand, s) for s in refined):
                refined.append(cand)
        refined.sort(key=lambda c: c["score"])
        log(f"  refined {len(refined)} candidates, best proxy score {refined[0]['score']:.4f}, search {time.time() - started:.0f} s")
        return refined

    def naive_pose(self) -> dict:
        """Haft along the fist's hole axis (the sense that points up in the tilt clip), roll 0, the recorded grip."""

        d = self.fist["axis"] / np.linalg.norm(self.fist["axis"])
        if np.mean([(m[:3, :3] @ d)[1] for m in self.ref_mats]) < 0:
            d = -d
        return {"direction": d, "roll_deg": 0.0, "grip": self.grip_ref}


# ---------------------------------------------------------------------------------------------
# Putting it together
# ---------------------------------------------------------------------------------------------


def place_weapon(weapon: dict, axes: dict, scale: float, palm: np.ndarray, pose: dict, grip_ref: float) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Weapon vertices and normals in the body's bind space for one pose."""

    Q = pose_matrices(pose["direction"][None], np.array([pose["roll_deg"]]))[0]
    local = weapon_local(weapon["positions"], axes, scale)
    local[:, 0] -= (pose["grip"] - grip_ref) * axes["length"] * scale
    positions = palm + local @ Q.T
    normals = None
    if weapon["normals"] is not None:
        normals = (weapon["normals"] @ axes["axes"]) @ Q.T
    return positions, normals


def build_output(merged: Glb, weapon: dict, axes: dict, scale: float, palm: np.ndarray, pose: dict, hand_slot: int, grip_ref: float) -> bytes:
    glb = Glb(merged.doc, bytes(merged.binary))
    positions, normals = place_weapon(weapon, axes, scale, palm, pose, grip_ref)
    add_weapon(glb, weapon, positions, normals, hand_slot)
    return glb.to_bytes()


def clip_table(result: dict) -> Dict[str, dict]:
    keys = ("stretched_pct", "weapon_in_body_pct", "weapon_deep_in_body_pct", "deepest_penetration_pct_of_height", "weapon_below_ground_pct", "weapon_below_rest_ground_pct", "verdict", "reasons")
    return {name: {k: c[k] for k in keys} for name, c in result["clips"].items()}


def parse_roles(text: str) -> Dict[str, str]:
    out = {}
    for item in text.split(","):
        clip, _, role = item.rpartition("=")
        if not clip or not role:
            raise AssembleError(f"--roles item {item!r} is not clip=role")
        out[clip.strip()] = role.strip()
    return out


def _select_role_map(roles: Optional[Dict[str, str]], fit_clips: Optional[Sequence[str]], clip_names: Sequence[str]) -> Dict[str, str]:
    """The role map the fit scores: `roles` (else the default), cut down to `fit_clips` when given."""

    role_map = dict(ROLE_MAP if roles is None else roles)
    if fit_clips:
        keep = {resolve_clip(c, clip_names) for c in fit_clips}
        if None in keep:
            raise AssembleError(f"--fit-clips names no clip: {list(fit_clips)}; the clips are {list(clip_names)}")
        role_map = {c: r for c, r in role_map.items() if resolve_clip(c, clip_names) in keep}
    return role_map


@dataclass
class _Run:
    """What the steps of one `assemble` call share: the merged body, the weapon, its fit and the search options."""

    merged: Glb
    weapon: dict
    axes: dict
    scale: float
    geometry: dict
    hand_slot: int
    hand: str
    grip: float
    fit: "Fit"
    grip_range: Tuple[float, float]
    directions: int
    rolls: int
    candidates: int
    selection_samples: int
    verify: bool
    log: Callable[[str], None]

    @property
    def check_clips(self) -> List[str]:
        return list(self.fit.role_map)

    def to_bytes(self, pose: dict) -> bytes:
        return build_output(self.merged, self.weapon, self.axes, self.scale, self.geometry["palm"], pose, self.hand_slot, self.grip)

    def _clip_roles(self, pose: dict, elig: Dict[str, Tuple[bool, str]]) -> dict:
        fit = self.fit
        clip_roles = {}
        for clip, role in fit.role_map.items():
            entry = {"role": role}
            if role == "attack":
                entry.update({k: round(v, 3) for k, v in fit.head_motion(pose["direction"], pose["grip"], pose["roll_deg"], clip).items()})
                entry["eligible"] = elig[clip][0]
            elif role == "death":
                entry["last_frame_extent_pct_of_standing_height"] = round(100 * fit.extent.get(clip, 1.0), 1)
                entry["eligible"] = elig[clip][0]
                entry["ground_tolerance_pct"] = 100 * fit.ground_tolerance.get(clip, cc.FRAME_GROUND_TOLERANCE_SHARE)
            clip_roles[clip] = entry
        if fit.ref_name in fit.path:
            baseline = fit.head_motion(pose["direction"], pose["grip"], pose["roll_deg"], fit.ref_name)
            clip_roles["_" + fit.ref_name + "_baseline"] = {k: round(v, 3) for k, v in baseline.items() if k.startswith("head_")}
        return clip_roles

    def describe(self, pose: dict, result: dict) -> dict:
        fit = self.fit
        elig = fit.eligibility(pose["direction"], pose["grip"], pose["roll_deg"])
        cost, summary = role_summary(result["clips"], fit.role_map, elig)
        tilt, margin = fit.tilt_and_margin(pose["direction"], pose["grip"], pose["roll_deg"])
        ref = fit.ref_name.replace(" ", "_")
        return {
            "haft_direction_butt_to_head_rest_world": pose["direction"].round(4).tolist(),
            "roll_deg": round(pose["roll_deg"], 2),
            "grip": round(pose["grip"], 4),
            "tilt_from_up_deg_in_" + ref: round(tilt, 2),
            "lowest_weapon_point_above_ground_cm_in_" + ref: round(margin * 100, 2),
            "fist": fit.fist_numbers(pose["direction"]),
            "role_cost": round(cost, 3),
            "roles": summary,
            "clip_roles": self._clip_roles(pose, elig),
            "deep_total_pct": round(sum(result["clips"][c]["weapon_deep_in_body_pct"] for c in self.check_clips), 2),
        }

    def best_for(self, tilt: float) -> Tuple[dict, dict]:
        fit = self.fit
        self.log(f"fit at max tilt {tilt:g}")
        found = fit.search(tilt, self.grip_range, self.directions, self.rolls, log=self.log)
        if not self.verify:
            return found[0], {}
        scored = []
        for cand in found[: self.candidates]:
            res = cc.check(self.to_bytes(cand), BODY_NODE, WEAPON_NODE, self.hand, self.selection_samples, per_frame_ground=True, only=self.check_clips, ground_tolerance_by_clip=fit.ground_tolerance)
            cost, _ = role_summary(res["clips"], fit.role_map, fit.eligibility(cand["direction"], cand["grip"], cand["roll_deg"]))
            deep = sum(res["clips"][c]["weapon_deep_in_body_pct"] for c in self.check_clips)
            fist_angle = fit.fist_numbers(cand["direction"])["rest"]["angle_deg"]
            scored.append(((round(cost, 6), round(deep * 2) / 2, fist_angle, abs(cand["grip"] - self.grip)), cand, res))
        scored.sort(key=lambda s: s[0])
        self.log(f"  checked {len(scored)} candidates with clip_check: role costs {[s[0][0] for s in scored]}")
        return scored[0][1], scored[0][2]

    def search_tilts(self, trade_tilts: Sequence[float], max_tilt: float) -> Tuple[Dict[float, Tuple[dict, dict]], Dict[float, str]]:
        """The best pose at every max tilt asked for. Only the main `max_tilt` may fail the run; the others are reported infeasible."""

        found_by_tilt: Dict[float, Tuple[dict, dict]] = {}
        infeasible: Dict[float, str] = {}
        for t in sorted(set(float(t) for t in trade_tilts) | {float(max_tilt)}):
            try:
                found_by_tilt[t] = self.best_for(t)
            except AssembleError as problem:
                if t == float(max_tilt):
                    raise
                infeasible[t] = str(problem)
                self.log(f"  max tilt {t:g}: {problem}")
        return found_by_tilt, infeasible

    def naive_report(self, naive: dict) -> dict:
        fit = self.fit
        n_tilt, n_margin = fit.tilt_and_margin(naive["direction"], self.grip, 0.0)
        return {
            "haft_direction_butt_to_head_rest_world": naive["direction"].round(4).tolist(),
            "roll_deg": 0.0,
            "grip": self.grip,
            "tilt_from_up_deg": round(n_tilt, 2),
            "lowest_weapon_point_above_ground_cm_in_" + fit.ref_name.replace(" ", "_"): round(n_margin * 100, 2),
            "fist": fit.fist_numbers(naive["direction"]),
        }

    def trade_table(self, found_by_tilt: Dict[float, Tuple[dict, dict]], infeasible: Dict[float, str]) -> dict:
        trade = {}
        for t, (pose, res) in found_by_tilt.items():
            entry = self.describe(pose, res)
            entry["clips_passing_of_fit_clips"] = [c for c in self.check_clips if res["clips"][c]["verdict"] == "pass"]
            entry["samples"] = self.selection_samples
            trade["max_tilt_%g" % t] = entry
        for t, why in infeasible.items():
            trade["max_tilt_%g" % t] = {"feasible": False, "reason": why}
        return dict(sorted(trade.items(), key=lambda kv: float(kv[0].split("_")[-1])))

    def verified_report(self, out: Path, best: dict, naive: dict, samples: int, found_by_tilt: Dict[float, Tuple[dict, dict]], infeasible: Dict[float, str]) -> dict:
        """Check the chosen and the naive pose at full sampling and describe both, with the trade table."""

        fit = self.fit
        self.log("verifying the chosen pose with clip_check at full sampling")
        fitted = cc.check(out, BODY_NODE, WEAPON_NODE, self.hand, samples, per_frame_ground=True, ground_tolerance_by_clip=fit.ground_tolerance)
        naive_path = out.with_name(out.stem + "._naive_tmp.glb")
        try:
            naive_path.write_bytes(self.to_bytes(naive))
            naive_check = cc.check(naive_path, BODY_NODE, WEAPON_NODE, self.hand, samples, per_frame_ground=True, ground_tolerance_by_clip=fit.ground_tolerance)
        finally:
            naive_path.unlink(missing_ok=True)
        clip_check = {"ground": "per-frame", "samples": samples, "thresholds": fitted["thresholds"], "fitted": clip_table(fitted), "naive": clip_table(naive_check)}
        clip_check["fitted_passes"] = [n for n, c in fitted["clips"].items() if c["verdict"] == "pass"]
        clip_check["naive_passes"] = [n for n, c in naive_check["clips"].items() if c["verdict"] == "pass"]
        return {
            "pose": self.describe(best, fitted),
            "naive_pose": self.naive_report(naive),
            "clip_check": clip_check,
            "trade": self.trade_table(found_by_tilt, infeasible),
        }


def _weapon_report(weapon: dict, axes: dict, scale: float, height: float, length_ratio: float, grip: float, weapon_triangles: Optional[int], bound_to: str) -> dict:
    triangles = int(len(weapon["triangles"]))
    return {
        "triangles": triangles,
        "vertices": int(len(weapon["positions"])),
        "file_length": round(axes["length"], 5),
        "length_ratio": length_ratio,
        "scaled_length": round(length_ratio * height, 5),
        "scale": round(scale, 5),
        "recorded_grip_share": grip,
        "head_spread_vs_butt_spread": [round(axes["head_spread"], 5), round(axes["butt_spread"], 5)],
        "head_was_at_negative_end_of_pca_axis": axes["head_was_at_negative_end"],
        "above_triangle_target": None if weapon_triangles is None else triangles > weapon_triangles,
        "triangle_target": weapon_triangles,
        "bound_to": bound_to,
    }


def _grip_geometry_report(geometry: dict, fist: dict) -> dict:
    return {
        "palm_rest_world": geometry["palm"].round(5).tolist(),
        "hand_vertices": geometry["hand_vertices"],
        "finger_vertices": fist["vertices"],
        "finger_centroid_rest_world": fist["centroid"].round(5).tolist(),
        "fist_radius_cm": round(100 * fist["radius"], 2),
        "fist_hole_axis_rest_world": fist["axis"].round(4).tolist(),
        "fist_hole_axis_reliability": {k: (None if v is None else round(v, 1) if isinstance(v, float) else v) for k, v in fist["details"].items()},
    }


def _fit_report(fit: "Fit", clip_names: Sequence[str], max_tilt: float, grip_range: Tuple[float, float], voxel: float) -> dict:
    return {
        "frames": len(fit.grids),
        "clips": fit.clips,
        "role_map": fit.role_map,
        "role_weights": ROLE_WEIGHTS,
        "tilt_clip": fit.ref_name,
        "max_tilt_deg": max_tilt,
        "grip_range": list(grip_range),
        "voxel": round(voxel, 5),
        "attack_min_head_travel_body_heights": ATTACK_MIN_HEAD_TRAVEL,
        "fallen_max_extent": FALLEN_MAX_EXTENT,
        "death_ground_tolerance_share": DEATH_GROUND_TOLERANCE_SHARE,
        "excluded_from_fit_but_checked": [name for name in clip_names if name not in fit.clips],
    }


def assemble(
    body_files: Sequence[Path],
    weapon_file: Path,
    out: Path,
    length_ratio: float = 1.06,
    grip: float = 0.60,
    hand: str = "RightHand",
    grip_range: Tuple[float, float] = (0.45, 0.70),
    max_tilt: float = 25.0,
    tilt_from: str = "idle",
    roles: Optional[Dict[str, str]] = None,
    trade_tilts: Sequence[float] = (15.0, 25.0, 40.0),
    fit_frames: int = 16,
    voxel_share: float = 0.01,
    directions: int = 120,
    rolls: int = 8,
    candidates: int = 8,
    weapon_triangles: Optional[int] = None,
    verify: bool = True,
    selection_samples: int = 12,
    samples: int = 24,
    fit_clips: Optional[Sequence[str]] = None,
    log=print,
) -> dict:
    started = time.time()
    log(f"merging {len(body_files)} body file(s)")
    merged, merge_report = merge_body_clips(body_files)
    weapon = read_weapon(weapon_file)
    rig = cc.Rig(merged.to_bytes(), BODY_NODE, None)
    clip_names = [name for name, _t, _e in rig.clips()]
    log(f"clips in the body: {clip_names}")
    rest_worlds = rig.joint_worlds({})
    rest_body = rig.skin(rig.body, rig.skin_mats(rest_worlds))
    height = float(rest_body[:, 1].max() - rest_body[:, 1].min())
    hand_slot = cc.resolve_weapon_joint(rig.joint_names, np.zeros((1, 3)), np.zeros((len(rig.joint_names), 3)), hand)
    log(f"body height {height:.4f}, hand joint {rig.joint_names[hand_slot]}")

    axes = weapon_axes(weapon["positions"], grip)
    scale = length_ratio * height / axes["length"]
    geometry = grip_geometry(rig, hand_slot, rest_body, rest_worlds)
    fist = fist_geometry(rig, hand_slot, rest_body, rest_worlds)
    geometry["fist_axis"] = fist["axis"]
    log(f"weapon file length {axes['length']:.4f} -> {length_ratio * height:.4f} (scale {scale:.4f}), head spread {axes['head_spread']:.4f} vs butt {axes['butt_spread']:.4f}")
    role_map = _select_role_map(roles, fit_clips, clip_names)
    if not grip_range[0] <= grip_range[1]:
        raise AssembleError(f"--grip-range {grip_range[0]},{grip_range[1]} is empty")
    fit = Fit(rig, hand_slot, geometry, fist, weapon_local(weapon["positions"], axes, scale), axes["length"] * scale, grip, role_map, fit_frames, voxel_share, tilt_from, log=log)
    run = _Run(merged, weapon, axes, scale, geometry, hand_slot, hand, grip, fit, grip_range, directions, rolls, candidates, selection_samples, verify, log)
    found_by_tilt, infeasible = run.search_tilts(trade_tilts, max_tilt)
    best, _ = found_by_tilt[float(max_tilt)]
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(run.to_bytes(best))
    report = {
        "output": str(out),
        "clips_in_body": clip_names,
        "inputs": {"body_files": merge_report["files"], "weapon": weapon["name"]},
        "merge": merge_report,
        "body": {"height": round(height, 5), "triangles": int(len(rig.body["triangles"])), "vertices": int(len(rig.body["positions"])), "joints": len(rig.joint_names)},
        "weapon": _weapon_report(weapon, axes, scale, height, length_ratio, grip, weapon_triangles, rig.joint_names[hand_slot]),
        "grip_geometry": _grip_geometry_report(geometry, fist),
        "fit": _fit_report(fit, clip_names, max_tilt, grip_range, voxel_share * height),
    }
    if verify:
        report.update(run.verified_report(out, best, fit.naive_pose(), samples, found_by_tilt, infeasible))
    else:
        report["pose"] = {"haft_direction_butt_to_head_rest_world": best["direction"].round(4).tolist(), "roll_deg": round(best["roll_deg"], 2), "grip": round(best["grip"], 4)}
    report["seconds"] = round(time.time() - started, 1)
    return report


def gather_body_files(items: Sequence[str]) -> List[Path]:
    files: List[Path] = []
    for item in items:
        p = Path(item)
        if p.is_dir():
            for candidate in sorted(p.glob("*.glb")):
                if cc.load_glb(candidate)[0].get("skins"):
                    files.append(candidate)
                else:
                    print(f"skipping {candidate.name}: no skin, so not a rigged body file")
        elif p.is_file():
            files.append(p)
        else:
            raise AssembleError(f"{item} is neither a folder nor a file")
    return files


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--body-clips", nargs="+", required=True, help="a folder of per-clip body GLBs, or the GLBs")
    parser.add_argument("--weapon", type=Path, required=True)
    parser.add_argument("--length-ratio", type=float, required=True, help="weapon length as a multiple of the body height")
    parser.add_argument("--grip", type=float, required=True, help="recorded grip point as a share of the weapon length from the butt (preferred)")
    parser.add_argument("--grip-range", default="0.45,0.70", help="lowest,highest grip share the fit may slide the hand to")
    parser.add_argument("--hand", default="RightHand")
    parser.add_argument("--max-tilt", type=float, default=25.0, help="largest angle between the haft and world up in the tilt clip, degrees")
    parser.add_argument("--tilt-from", default="idle", help="clip the upright rule is measured in (the rest pose when absent)")
    parser.add_argument("--roles", default=",".join(f"{c}={r}" for c, r in ROLE_MAP.items()), help="clip=role list: the clips the fit scores and the role each serves")
    parser.add_argument("--fit-clips", help="comma-separated clips (names or unambiguous prefixes) the fit is restricted to; default: every clip in --roles")
    parser.add_argument("--trade-tilts", default="15,25,40", help="also report the best pose at these max tilts")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--fit-frames", type=int, default=16, help="frames sampled per clip in the fit")
    parser.add_argument("--weapon-triangles", type=int, help="only flags in the report a weapon above this triangle count")
    parser.add_argument("--samples", type=int, default=24, help="frames per clip in the final clip_check verification")
    parser.add_argument("--no-verify", action="store_true")
    args = parser.parse_args(argv)
    try:
        lo, _, hi = args.grip_range.partition(",")
        report = assemble(
            gather_body_files(args.body_clips),
            args.weapon,
            args.out,
            args.length_ratio,
            args.grip,
            args.hand,
            (float(lo), float(hi)),
            args.max_tilt,
            args.tilt_from,
            parse_roles(args.roles),
            [float(t) for t in args.trade_tilts.split(",") if t],
            args.fit_frames,
            weapon_triangles=args.weapon_triangles,
            fit_clips=[c for c in args.fit_clips.split(",") if c] if args.fit_clips else None,
            verify=not args.no_verify,
            samples=args.samples,
        )
    except AssembleError as problem:
        print(f"assemble_separate: {problem}", file=sys.stderr)
        return 2
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")
    if "clip_check" in report:
        print(f"{'clip':<20}{'fitted':>8}{'naive':>8}   (deep% of free points / below-ground%)")
        for name, c in report["clip_check"]["fitted"].items():
            n = report["clip_check"]["naive"][name]
            print(f"{name:<20}{c['verdict']:>8}{n['verdict']:>8}   fitted {c['weapon_deep_in_body_pct']:.2f}/{c['weapon_below_ground_pct']:.2f}  naive {n['weapon_deep_in_body_pct']:.2f}/{n['weapon_below_ground_pct']:.2f}")
        pose = report["pose"]
        print("grip", pose["grip"], "roles", json.dumps({r: v["best_passing_clip"] for r, v in pose["roles"].items()}))
    print(f"wrote {args.out} in {report['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
