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
import json
import math
import struct
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import clip_check as cc  # noqa: E402

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

    material = copy.deepcopy(weapon["material"]) if weapon["material"] is not None else None
    if material is not None:
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
            for key, slot in list(holder.items()):
                if isinstance(slot, dict) and isinstance(slot.get("index"), int):
                    remap(slot)
        doc.setdefault("materials", []).append(material)
        primitive["material"] = len(doc["materials"]) - 1

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


def role_groups(role_map: Dict[str, str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for clip, role in role_map.items():
        groups.setdefault(role, []).append(clip)
    return groups


def role_summary(clips: Dict[str, dict], role_map: Dict[str, str]) -> Tuple[float, Dict[str, dict]]:
    """Weighted cost of the roles no clip of which passes, and per role the best passing clip (lowest deep share)."""

    cost, summary = 0.0, {}
    for role, names in role_groups(role_map).items():
        have = [n for n in names if n in clips]
        if not have:
            continue
        passing = [n for n in have if clips[n]["verdict"] == "pass"]
        best = min(passing, key=lambda n: (clips[n]["weapon_deep_in_body_pct"], clips[n]["weapon_below_ground_pct"])) if passing else None
        weight = ROLE_WEIGHTS.get(role, 1.0)
        failing = len(have) - len(passing)
        cost += weight * ((0.0 if passing else 1.0) + 0.1 * failing / len(have))
        summary[role] = {"best_passing_clip": best, "clips": {n: clips[n]["verdict"] for n in have}}
    return cost, summary


class Fit:
    """Scores weapon poses against the posed body of many frames.

    A pose is the haft direction (butt to head, in the rest world), the roll about it and the grip share
    (where along the weapon the palm sits). Hard rules: in the tilt clip (idle) the haft is within the
    maximum tilt of world up with the head up, and no weapon point is below the lowest body vertex of
    the frame. The soft score weighs the clips by their role and then the total deep penetration."""

    def __init__(self, rig, hand: int, geometry: dict, local_points: np.ndarray, length: float, grip_ref: float, role_map: Dict[str, str], frames: int, voxel_share: float, tilt_from: str = "idle", grip_radius: float = cc.GRIP_RADIUS_SHARE, log=print):
        rest_worlds = rig.joint_worlds({})
        rest_mats = rig.skin_mats(rest_worlds)
        rest_body = rig.skin(rig.body, rest_mats)
        self.height = float(rest_body[:, 1].max() - rest_body[:, 1].min())
        self.palm, self.fist_axis = geometry["palm"], geometry["fist_axis"]
        self.hand_rest = rest_worlds[hand][:3, 3]
        self.free_radius = grip_radius * self.height
        self.length, self.grip_ref, self.tilt_from = length, grip_ref, tilt_from
        pick = np.linspace(0, len(local_points) - 1, min(cc.MAX_WEAPON_POINTS, len(local_points))).astype(int)
        extremes = [int(np.argmin(local_points[:, 0])), int(np.argmax(local_points[:, 0]))]
        self.points = local_points[np.unique(np.concatenate([pick, extremes]))]
        voxel = voxel_share * self.height
        available = [name for name, _t, _e in rig.clips()]
        self.role_map = {c: r for c, r in role_map.items() if c in available}
        for clip in role_map:
            if clip not in available:
                log(f"  clip {clip!r} of the role map is not in the file, skipped")
        if not self.role_map:
            raise AssembleError(f"none of the role map clips {list(role_map)} is in the file; the clips are {available}")
        self.roles = role_groups(self.role_map)
        wanted = list(self.role_map) + ([tilt_from] if tilt_from in available and tilt_from not in self.role_map else [])
        self.grids: List[FrameGrid] = []
        self.mats: List[np.ndarray] = []
        self.frame_clip: List[str] = []
        started = time.time()
        tri = rig.body["triangles"]
        for name, tracks, end in rig.clips():
            if name not in wanted:
                continue
            for step in range(frames):
                t = end * step / max(frames - 1, 1)
                mats = rig.skin_mats(rig.joint_worlds(rig.pose_for(tracks, t)))
                body = rig.skin(rig.body, mats)
                self.grids.append(FrameGrid(body, tri, voxel, PENETRATION_ERODE))
                self.mats.append(mats[hand])
                self.frame_clip.append(name)
        self.clips = list(dict.fromkeys(self.frame_clip))
        ref = [i for i, c in enumerate(self.frame_clip) if c == tilt_from]
        if ref:
            self.ref_mats = [self.mats[i] for i in ref]
            self.ref_lowest = [self.grids[i].lowest for i in ref]
            self.ref_name = tilt_from
        else:
            log(f"  tilt clip {tilt_from!r} is not in the file: the rest pose is used")
            self.ref_mats, self.ref_lowest, self.ref_name = [np.eye(4)], [float(rest_body[:, 1].min())], "rest pose"
        log(f"  voxelised {len(self.grids)} frames of {len(self.clips)} clips in {time.time() - started:.0f} s, voxel {voxel:.4f}")

    # -- measures of one pose -------------------------------------------------------------------

    def tilt_and_margin(self, direction: np.ndarray, grip: float, roll_deg: float) -> Tuple[float, float]:
        """Tilt from world up (degrees, mean haft direction over the tilt clip) and the lowest weapon point above the ground (metres)."""

        res = self._hard(np.asarray(direction, float)[None], np.array([roll_deg]), np.array([grip]))
        return float(res["tilt"][0]), float(res["margin"][0])

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
        return {"tilt": tilt, "margin": margin}

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
        violation = np.maximum(0.0, hard["tilt"] - max_tilt) * 0.1 + np.maximum(0.0, -hard["margin"]) * 10.0
        free = np.linalg.norm(X - self.hand_rest, axis=2) > self.free_radius
        nfree = np.maximum(free.sum(axis=1), 1)
        values = {c: {"deep": [], "ground": []} for c in self.clips}
        for grid, mat, clip in zip(self.grids, self.mats, self.frame_clip):
            world = X @ mat[:3, :3].T + mat[:3, 3]
            _inside, deep = grid.lookup(world)
            values[clip]["deep"].append((deep & free).sum(axis=1) / nfree)
            values[clip]["ground"].append((world[..., 1] < grid.lowest - cc.FRAME_GROUND_TOLERANCE_SHARE * self.height).mean(axis=1))
        soft, deep_total, ground_total = {}, np.zeros(len(d)), np.zeros(len(d))
        for clip, v in values.items():
            fd, fg = np.stack(v["deep"]).max(0), np.stack(v["ground"]).max(0)
            soft[clip] = np.minimum(1.0, fd / SOFT_DEEP) + np.minimum(1.0, fg / SOFT_GROUND)
            deep_total += fd
            ground_total += fg
        cost = np.zeros(len(d))
        for role, names in self.roles.items():
            s = np.stack([soft[n] for n in names])
            cost += ROLE_WEIGHTS.get(role, 1.0) * (s.min(0) + 0.1 * s.mean(0))
        angle = np.degrees(np.arccos(np.clip(np.abs(d @ self.fist_axis), 0, 1)))
        score = np.where(violation > 0, 1000.0 + 100.0 * violation, 0.0) + cost + 0.2 * deep_total + 0.02 * ground_total + 0.05 * np.abs(g - self.grip_ref) + 0.0005 * angle
        return {"score": score, "violation": violation, "tilt": hard["tilt"], "margin": hard["margin"], "angle": angle}

    # -- search -----------------------------------------------------------------------------------

    def up_in_rest(self) -> np.ndarray:
        up = np.array([0.0, 1.0, 0.0])
        d = np.mean([m[:3, :3].T @ up for m in self.ref_mats], axis=0)
        return d / np.linalg.norm(d)

    def search(self, max_tilt: float, grip_range: Tuple[float, float], directions: int = 120, rolls: int = 8, keep: int = 6, log=print) -> List[dict]:
        """Local optima of the proxy score, best first. Raises AssembleError when the hard rules cannot be met."""

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
        started = time.time()
        coarse = self.evaluate(D, R, G, max_tilt)
        order = np.argsort(coarse["score"])
        if coarse["violation"][order[0]] > 0:
            raise AssembleError(
                f"no pose meets the hard rules (haft within {max_tilt:g} degrees of up in {self.ref_name}, weapon above the ground) "
                f"with the grip between {lo:g} and {hi:g}: the closest has tilt {coarse['tilt'][order[0]]:.1f} and its lowest point {coarse['margin'][order[0]] * 100:.1f} cm from the ground"
            )

        def distinct(a: dict, b: dict) -> bool:
            return np.degrees(np.arccos(np.clip(a["direction"] @ b["direction"], -1, 1))) > 8 or abs(a["grip"] - b["grip"]) > 0.05 or abs(((a["roll_deg"] - b["roll_deg"]) + 180) % 360 - 180) > 60

        seeds: List[dict] = []
        for i in order:
            if coarse["violation"][i] > 0:
                break
            cand = {"direction": D[i], "roll_deg": float(R[i]), "grip": float(G[i]), "score": float(coarse["score"][i])}
            if all(distinct(cand, s) for s in seeds):
                seeds.append(cand)
            if len(seeds) >= keep:
                break
        log(f"  coarse search of {len(D)} poses in {time.time() - started:.0f} s, best proxy score {coarse['score'][order[0]]:.4f}")
        refined: List[dict] = []
        steps = [(6.0, 0.03), (3.0, 0.015), (1.5, 0.0075)]
        for seed in seeds:
            d, roll, grip, score = seed["direction"], seed["roll_deg"], seed["grip"], seed["score"]
            for angle_step, grip_step in steps:
                for _ in range(6):
                    pu, pv = _perpendicular_basis(d[None])
                    cd, cr, cg = [], [], []
                    for a in (-1, 0, 1):
                        for b in (-1, 0, 1):
                            for c in (-1, 0, 1):
                                for e in (-1, 0, 1):
                                    nd = d + math.tan(math.radians(angle_step)) * (a * pu[0] + b * pv[0])
                                    cd.append(nd / np.linalg.norm(nd))
                                    cr.append(roll + c * angle_step)
                                    cg.append(min(max(grip + e * grip_step, lo), hi))
                    res = self.evaluate(np.array(cd), np.array(cr), np.array(cg), max_tilt)
                    k = int(np.argmin(res["score"]))
                    if res["score"][k] < score - 1e-9:
                        d, roll, grip, score = cd[k], cr[k], cg[k], float(res["score"][k])
                    else:
                        break
            cand = {"direction": d, "roll_deg": roll % 360.0, "grip": grip, "score": score}
            if all(distinct(cand, s) for s in refined):
                refined.append(cand)
        refined.sort(key=lambda c: c["score"])
        log(f"  refined {len(refined)} candidates, best proxy score {refined[0]['score']:.4f}, search {time.time() - started:.0f} s")
        return refined

    def naive_pose(self) -> dict:
        """Haft along the fist axis (the sense that points up in the tilt clip), roll 0, the recorded grip."""

        d = self.fist_axis / np.linalg.norm(self.fist_axis)
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
        clip, _, role = item.partition("=")
        if not clip or not role:
            raise AssembleError(f"--roles item {item!r} is not clip=role")
        out[clip.strip()] = role.strip()
    return out


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
    log=print,
) -> dict:
    started = time.time()
    log(f"merging {len(body_files)} body files")
    merged, merge_report = merge_body_clips(body_files)
    weapon = read_weapon(weapon_file)
    rig = cc.Rig(merged.to_bytes(), BODY_NODE, None)
    rest_worlds = rig.joint_worlds({})
    rest_body = rig.skin(rig.body, rig.skin_mats(rest_worlds))
    height = float(rest_body[:, 1].max() - rest_body[:, 1].min())
    hand_slot = cc.resolve_weapon_joint(rig.joint_names, np.zeros((1, 3)), np.zeros((len(rig.joint_names), 3)), hand)
    log(f"body height {height:.4f}, hand joint {rig.joint_names[hand_slot]}")

    axes = weapon_axes(weapon["positions"], grip)
    scale = length_ratio * height / axes["length"]
    local = weapon_local(weapon["positions"], axes, scale)
    geometry = grip_geometry(rig, hand_slot, rest_body, rest_worlds)
    log(f"weapon file length {axes['length']:.4f} -> {length_ratio * height:.4f} (scale {scale:.4f}), head spread {axes['head_spread']:.4f} vs butt {axes['butt_spread']:.4f}")
    role_map = dict(ROLE_MAP if roles is None else roles)
    lo, hi = grip_range
    if not lo <= hi:
        raise AssembleError(f"--grip-range {lo},{hi} is empty")
    fit = Fit(rig, hand_slot, geometry, local, axes["length"] * scale, grip, role_map, fit_frames, voxel_share, tilt_from, log=log)
    fit_role_map = fit.role_map
    check_clips = list(fit_role_map)

    def to_bytes(pose: dict) -> bytes:
        return build_output(merged, weapon, axes, scale, geometry["palm"], pose, hand_slot, grip)

    def describe(pose: dict, result: dict) -> dict:
        cost, summary = role_summary(result["clips"], fit_role_map)
        tilt, margin = fit.tilt_and_margin(pose["direction"], pose["grip"], pose["roll_deg"])
        return {
            "haft_direction_butt_to_head_rest_world": pose["direction"].round(4).tolist(),
            "roll_deg": round(pose["roll_deg"], 2),
            "grip": round(pose["grip"], 4),
            "tilt_from_up_deg_in_" + fit.ref_name.replace(" ", "_"): round(tilt, 2),
            "lowest_weapon_point_above_ground_cm_in_" + fit.ref_name.replace(" ", "_"): round(margin * 100, 2),
            "angle_to_fist_axis_deg": round(float(np.degrees(np.arccos(min(1.0, abs(float(pose["direction"] @ geometry["fist_axis"])))))), 1),
            "role_cost": round(cost, 3),
            "roles": summary,
            "deep_total_pct": round(sum(result["clips"][c]["weapon_deep_in_body_pct"] for c in check_clips), 2),
        }

    def best_for(tilt: float) -> Tuple[dict, dict]:
        log(f"fit at max tilt {tilt:g}")
        found = fit.search(tilt, (lo, hi), directions, rolls, log=log)
        if not verify:
            return found[0], {}
        scored = []
        for cand in found[:candidates]:
            res = cc.check(to_bytes(cand), BODY_NODE, WEAPON_NODE, hand, selection_samples, per_frame_ground=True, only=check_clips)
            cost, _ = role_summary(res["clips"], fit_role_map)
            deep = sum(res["clips"][c]["weapon_deep_in_body_pct"] for c in check_clips) / 100.0
            angle = float(np.degrees(np.arccos(min(1.0, abs(float(cand["direction"] @ geometry["fist_axis"]))))))
            scored.append(((round(cost, 6), deep + 0.05 * abs(cand["grip"] - grip) + 0.0005 * angle), cand, res))
        scored.sort(key=lambda s: s[0])
        log(f"  checked {len(scored)} candidates with clip_check: role costs {[s[0][0] for s in scored]}")
        return scored[0][1], scored[0][2]

    tilts = sorted(set(float(t) for t in trade_tilts) | {float(max_tilt)})
    found_by_tilt: Dict[float, Tuple[dict, dict]] = {}
    infeasible: Dict[float, str] = {}
    for t in tilts:
        try:
            found_by_tilt[t] = best_for(t)
        except AssembleError as problem:
            if t == float(max_tilt):
                raise
            infeasible[t] = str(problem)
            log(f"  max tilt {t:g}: {problem}")
    best, _ = found_by_tilt[float(max_tilt)]
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(to_bytes(best))
    naive = fit.naive_pose()
    triangles = int(len(weapon["triangles"]))
    report = {
        "output": str(out),
        "inputs": {"body_files": merge_report["files"], "weapon": weapon["name"]},
        "merge": merge_report,
        "body": {"height": round(height, 5), "triangles": int(len(rig.body["triangles"])), "vertices": int(len(rig.body["positions"])), "joints": len(rig.joint_names)},
        "weapon": {
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
            "bound_to": rig.joint_names[hand_slot],
        },
        "grip_geometry": {
            "palm_rest_world": geometry["palm"].round(5).tolist(),
            "hand_vertices": geometry["hand_vertices"],
            "fist_axis_rest_world": geometry["fist_axis"].round(4).tolist(),
            "fist_axis_source": geometry["fist_axis_source"],
            "knuckle_vs_finger_vertex_axis_deg": None if geometry["knuckle_vs_finger_vertex_axis_deg"] is None else round(geometry["knuckle_vs_finger_vertex_axis_deg"], 1),
        },
        "fit": {
            "frames": len(fit.grids),
            "clips": fit.clips,
            "role_map": fit_role_map,
            "role_weights": ROLE_WEIGHTS,
            "tilt_clip": fit.ref_name,
            "max_tilt_deg": max_tilt,
            "grip_range": [lo, hi],
            "voxel": round(voxel_share * height, 5),
            "excluded_from_fit_but_checked": [name for name, _t, _e in rig.clips() if name not in fit.clips],
        },
    }
    if verify:
        log("verifying the chosen pose with clip_check at full sampling")
        fitted = cc.check(out, BODY_NODE, WEAPON_NODE, hand, samples, per_frame_ground=True)
        naive_path = out.with_name(out.stem + "._naive_tmp.glb")
        try:
            naive_path.write_bytes(to_bytes(naive))
            naive_check = cc.check(naive_path, BODY_NODE, WEAPON_NODE, hand, samples, per_frame_ground=True)
        finally:
            naive_path.unlink(missing_ok=True)
        report["pose"] = describe(best, fitted)
        n_tilt, n_margin = fit.tilt_and_margin(naive["direction"], grip, 0.0)
        report["naive_pose"] = {
            "haft_direction_butt_to_head_rest_world": naive["direction"].round(4).tolist(),
            "roll_deg": 0.0,
            "grip": grip,
            "tilt_from_up_deg": round(n_tilt, 2),
            "lowest_weapon_point_above_ground_cm_in_" + fit.ref_name.replace(" ", "_"): round(n_margin * 100, 2),
        }
        report["clip_check"] = {"ground": "per-frame", "samples": samples, "thresholds": fitted["thresholds"], "fitted": clip_table(fitted), "naive": clip_table(naive_check)}
        report["clip_check"]["fitted_passes"] = [n for n, c in fitted["clips"].items() if c["verdict"] == "pass"]
        report["clip_check"]["naive_passes"] = [n for n, c in naive_check["clips"].items() if c["verdict"] == "pass"]
        trade = {}
        for t, (pose, res) in found_by_tilt.items():
            entry = describe(pose, res)
            entry["clips_passing_of_fit_clips"] = [c for c in check_clips if res["clips"][c]["verdict"] == "pass"]
            entry["samples"] = selection_samples
            trade["max_tilt_%g" % t] = entry
        for t, why in infeasible.items():
            trade["max_tilt_%g" % t] = {"feasible": False, "reason": why}
        report["trade"] = dict(sorted(trade.items(), key=lambda kv: float(kv[0].split("_")[-1])))
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
