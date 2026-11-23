"""Re-seat a winged humanoid's arm chain from the mesh's own arm, when Tripo's auto-rig put it elsewhere (TRIPO-RIG-ARMS).

Tripo's humanoid auto-rig does not know wings. On the ZIN devil (2026-11-22) it put the shoulder, elbow and wrist joints close together
high on the chest, and the hand joint with its fingers carried both whole wings and the real arms. A paid retry of the rig was worse. This
module repairs such an export without Blender and without credits, by fixed rules:

1. Arm family: per side, the skin bound mostly to that side's upper arm, forearm, hand or fingers.
2. Wing: the arm family farther from the mid-plane than `WING_SHARE` of the model's width. Its plane is fitted (least squares), facing
   the front (+z).
3. Arm: the arm family in front of the wing's plane by more than the membrane's own thickness plus `FRONT_MARGIN_SHARE` of the body's
   height, below the shoulder. Its largest connected piece is the arm. The arm runs from its end nearest the old shoulder joint to its
   farthest point. The elbow sits at `ELBOW_SHARE` of that run and the wrist at `WRIST_SHARE` (human proportions: the hand with its
   claws is the last fifth). Skin of the arm family that lies within the arm's own radius of that line (the back of the arm bones, the
   joints) joins the arm.
4. Joints: the forearm and hand joints move to the elbow and the wrist. The upper arm joint stays where Tripo put it, at the clavicle's
   end: moved down the arm, every turn of the clavicle in the clips swung the whole arm round it (run devil_c, 2026-11-22, the shoulder
   line turned 90 to 160 degrees in every clip and the wing rules that follow the shoulders went wild). Only positions change, never
   their rest rotations, so every clip keeps its rotations. Each clip's translation keys of those joints move by the same offset, and the
   skin's inverse bind matrices are recomputed for every joint below them.
5. Weights: the arm takes its three joints by its run (a linear blend over `BLEND_SHARE` of the run at the elbow and the wrist). The rest of
   the arm family, the wing, goes to the side's shoulder (clavicle) joint, where the route's wing chains then take it (lib/tripo_chains.py).

It works on a single skinned primitive, Mixamo joint names, and node rest transforms equal to the bind pose (Tripo's exports are). It
refuses anything else. Maths only: numpy, and scipy for the connected pieces.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

WING_SHARE = 0.18  # as lib/tripo_chains.WING_LATERAL_SHARE
FRONT_MARGIN_SHARE = 0.01
ELBOW_SHARE = 0.45
WRIST_SHARE = 0.8
BLEND_SHARE = 0.06
ARM_RADIUS_FACTOR = 1.5  # skin within this many times the arm's 90th percentile radius of its line joins the arm
MIN_ARM_VERTICES = 20
_TYPES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
_DTYPES = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}


class SeatError(RuntimeError):
    pass


# ---- GLB in and out ----------------------------------------------------------------------------------


def read_glb(path: Path) -> Tuple[dict, bytearray]:
    data = Path(path).read_bytes()
    if data[:4] != b"glTF":
        raise SeatError(f"{path} is not a binary glTF file")
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    offset = 20 + length
    size = struct.unpack("<I", data[offset:offset + 4])[0]
    return doc, bytearray(data[offset + 8:offset + 8 + size])


def write_glb(path: Path, doc: dict, blob: bytes) -> None:
    text = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    text += b" " * (-len(text) % 4)
    blob = bytes(blob) + b"\0" * (-len(blob) % 4)
    total = 12 + 8 + len(text) + 8 + len(blob)
    out = b"glTF" + struct.pack("<II", 2, total) + struct.pack("<I", len(text)) + b"JSON" + text + struct.pack("<I", len(blob)) + b"BIN\0" + blob
    Path(path).write_bytes(out)


def _view(doc: dict, index: int) -> Tuple[int, int, np.dtype, int, int]:
    item = doc["accessors"][index]
    view = doc["bufferViews"][item["bufferView"]]
    dtype = np.dtype(_DTYPES[item["componentType"]])
    width = _TYPES[item["type"]]
    start = view.get("byteOffset", 0) + item.get("byteOffset", 0)
    stride = view.get("byteStride") or width * dtype.itemsize
    return start, stride, dtype, width, item["count"]


def get(doc: dict, blob: bytearray, index: int) -> np.ndarray:
    start, stride, dtype, width, count = _view(doc, index)
    out = np.empty((count, width), dtype)
    for row in range(count):
        out[row] = np.frombuffer(blob, dtype, count=width, offset=start + row * stride)
    return out


def put(doc: dict, blob: bytearray, index: int, values: np.ndarray) -> None:
    start, stride, dtype, width, count = _view(doc, index)
    values = np.asarray(values).astype(dtype).reshape(count, width)
    for row in range(count):
        blob[start + row * stride:start + row * stride + width * dtype.itemsize] = values[row].tobytes()
    item = doc["accessors"][index]
    if "min" in item and "max" in item and dtype == np.float32:
        item["min"], item["max"] = values.min(axis=0).astype(float).tolist(), values.max(axis=0).astype(float).tolist()


# ---- Skeleton --------------------------------------------------------------------------------------


def short(name: str) -> str:
    return str(name).split(":")[-1]


def trs(node: dict) -> np.ndarray:
    t = np.asarray(node.get("translation", [0.0, 0.0, 0.0]), float)
    x, y, z, w = np.asarray(node.get("rotation", [0.0, 0.0, 0.0, 1.0]), float)
    s = np.asarray(node.get("scale", [1.0, 1.0, 1.0]), float)
    r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    m = np.eye(4)
    m[:3, :3], m[:3, 3] = r * s, t
    return m


def worlds(doc: dict) -> Dict[int, np.ndarray]:
    parent = {child: i for i, node in enumerate(doc["nodes"]) for child in node.get("children", [])}
    cache: Dict[int, np.ndarray] = {}

    def world(i: int) -> np.ndarray:
        if i not in cache:
            cache[i] = (world(parent[i]) if i in parent else np.eye(4)) @ trs(doc["nodes"][i])
        return cache[i]

    for i in range(len(doc["nodes"])):
        world(i)
    return cache


# ---- Geometry ---------------------------------------------------------------------------------------


def welded_pieces(positions: np.ndarray, triangles: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """A piece label per vertex of `mask` (-1 elsewhere): its connected piece over the triangles, vertices at one position welded."""

    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    _, canon = np.unique(np.round(positions / 1e-6).astype(np.int64), axis=0, return_inverse=True)
    canon = canon.ravel()
    edges = canon[np.concatenate([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]])]
    keep = np.zeros(canon.max() + 1, bool)
    keep[canon[mask]] = True
    edges = edges[keep[edges[:, 0]] & keep[edges[:, 1]]]
    size = canon.max() + 1
    graph = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(size, size))
    _count, labels = connected_components(graph, directed=False)
    out = np.full(len(positions), -1)
    out[mask] = labels[canon[mask]]
    return out


def plane(points: np.ndarray, front: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    centre = points.mean(axis=0)
    normal = np.linalg.svd(points - centre, full_matrices=False)[2][-1]
    return centre, normal if normal @ front >= 0 else -normal


def segment_distance(points: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ab = b - a
    t = np.clip((points - a) @ ab / max(float(ab @ ab), 1e-12), 0.0, 1.0)
    return np.linalg.norm(points - (a + t[:, None] * ab), axis=1)


def body_axes(heads: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """(across, ahead): the level left-to-right axis from the thigh joints and the level way the body faces, from the heels to the toes.
    Tripo's own exports face +z with x across, but an upload Tripo was told to turn (its angle dialog) faces another way: the ZIN devil's
    upload came back with its wings along z (2026-11-22)."""

    across = np.asarray(heads["RightUpLeg"], float) - np.asarray(heads["LeftUpLeg"], float)
    across[1] = 0.0
    across /= max(float(np.linalg.norm(across)), 1e-12)
    ahead = np.cross(across, [0.0, 1.0, 0.0])
    toes = [np.asarray(heads[f"{s}ToeBase"], float) - np.asarray(heads[f"{s}Foot"], float) for s in ("Left", "Right")
            if f"{s}ToeBase" in heads and f"{s}Foot" in heads]
    if toes and float(np.mean(toes, axis=0) @ ahead) < 0:
        ahead = -ahead
    return across, ahead


def seat_side(side: str, positions: np.ndarray, triangles: np.ndarray, dominant: np.ndarray, heads: Dict[str, np.ndarray],
              body_height: float) -> dict:
    """The new arm joints and the arm and wing masks of one side, by the rules of the module docstring."""

    family = np.array([str(name).startswith(side) and ("Arm" in str(name) or "Hand" in str(name)) for name in dominant])
    across, ahead = body_axes(heads)
    lateral = (positions - heads["Hips"]) @ across
    width = float(np.ptp(lateral))
    wing = family & (np.abs(lateral) > WING_SHARE * width)
    if wing.sum() < MIN_ARM_VERTICES:
        raise SeatError(f"{side}: the arm family has no wing beyond {WING_SHARE:.0%} of the width ({int(wing.sum())} vertices): not a winged rig")
    centre, normal = plane(positions[wing], ahead)
    depth = (positions - centre) @ normal
    thickness = float(np.percentile(np.abs(depth[wing]), 95))
    shoulder_y = float(heads[f"{side}Arm"][1])
    front = family & (depth > thickness + FRONT_MARGIN_SHARE * body_height) & (positions[:, 1] < shoulder_y)
    pieces = welded_pieces(positions, triangles, front)
    labels, counts = np.unique(pieces[front], return_counts=True)
    if not len(labels) or counts.max() < MIN_ARM_VERTICES:
        raise SeatError(f"{side}: no arm in front of the wing's plane ({int(front.sum())} vertices)")
    arm = pieces == labels[np.argmax(counts)]
    points = positions[arm]
    near = np.linalg.norm(points - heads[f"{side}Arm"], axis=1)
    top = points[near <= np.percentile(near, 5)].mean(axis=0)
    run = np.linalg.norm(points - top, axis=1)
    end = points[run >= np.percentile(run, 98)].mean(axis=0)
    axis = end - top
    length = float(np.linalg.norm(axis))
    share = (positions - top) @ axis / max(length * length, 1e-12)
    radius = float(np.percentile(segment_distance(points, top, end), 90))
    arm = arm | (family & (segment_distance(positions, top, end) <= ARM_RADIUS_FACTOR * radius) & (share > -0.05) & (share < 1.05)
                 & (depth > -thickness))

    def station(target: float) -> np.ndarray:
        band = arm & (np.abs(share - target) < 0.04)
        return positions[band].mean(axis=0) if band.sum() >= 3 else top + target * axis

    return {"arm": arm, "wing": family & ~arm, "share": share, "joints": {"Arm": top, "ForeArm": station(ELBOW_SHARE), "Hand": station(WRIST_SHARE)},
            "numbers": {"arm_vertices": int(arm.sum()), "wing_vertices": int((family & ~arm).sum()), "arm_length": round(length, 4),
                        "wing_thickness": round(thickness, 4)}}


def arm_weights(share: float) -> Dict[str, float]:
    """The arm's weights at `share` of its run: upper arm, forearm, hand, blended over `BLEND_SHARE` at the elbow and the wrist."""

    def ramp(x: float, at: float) -> float:
        return float(np.clip((x - (at - BLEND_SHARE)) / (2 * BLEND_SHARE), 0.0, 1.0))

    elbow, wrist = ramp(share, ELBOW_SHARE), ramp(share, WRIST_SHARE)
    out = {"Arm": 1.0 - elbow, "ForeArm": elbow * (1.0 - wrist), "Hand": wrist}
    return {k: v for k, v in out.items() if v > 1e-6}


# ---- The repair ------------------------------------------------------------------------------------


def load_rig(doc: dict, blob: bytearray) -> dict:
    """The skin's arrays and joints, after the checks the repair needs (one primitive, nodes at the bind pose, both arm chains)."""

    skin = doc["skins"][0]
    meshes = [n for n in doc["nodes"] if "skin" in n and "mesh" in n]
    primitives = doc["meshes"][meshes[0]["mesh"]]["primitives"] if meshes else []
    if len(meshes) != 1 or len(primitives) != 1:
        raise SeatError("one skinned mesh with one primitive is needed")
    joints_index = skin["joints"]
    names = [short(doc["nodes"][j].get("name", "")) for j in joints_index]
    ibm = get(doc, blob, skin["inverseBindMatrices"]).astype(float).reshape(-1, 4, 4).transpose(0, 2, 1)
    world = worlds(doc)
    drift = max(float(np.abs(np.linalg.inv(ibm[k]) - world[j]).max()) for k, j in enumerate(joints_index))
    if drift > 1e-4:
        raise SeatError(f"the nodes' rest transforms differ from the bind pose by {drift:.2g}")
    attributes = primitives[0]["attributes"]
    rig = {"skin": skin, "attributes": attributes, "names": names, "node_of": {name: joints_index[k] for k, name in enumerate(names)},
           "positions": get(doc, blob, attributes["POSITION"]).astype(float),
           "triangles": get(doc, blob, primitives[0]["indices"]).astype(int).reshape(-1, 3),
           "joint_ids": get(doc, blob, attributes["JOINTS_0"]).astype(int), "weights": get(doc, blob, attributes["WEIGHTS_0"]).astype(float)}
    rig["dominant"] = np.array([names[j] for j in rig["joint_ids"][np.arange(len(rig["joint_ids"])), rig["weights"].argmax(axis=1)]])
    rig["heads"] = {name: world[rig["node_of"][name]][:3, 3] for name in names}
    for side in ("Left", "Right"):
        missing = [f"{side}{part}" for part in ("Shoulder", "Arm", "ForeArm", "Hand") if f"{side}{part}" not in rig["heads"]]
        if missing:
            raise SeatError(f"the rig has no {', '.join(missing)}: export a rig that has the arm chain")
    return rig


def move_joints(doc: dict, rig: dict, side: str, joints: Dict[str, np.ndarray], moved: Dict[int, np.ndarray]) -> None:
    """New local translations of one side's arm joints, parent first, each against its parent's new world matrix."""

    for part in ("ForeArm", "Hand"):  # the upper arm joint stays at the clavicle's end (module text, rule 4)
        node = rig["node_of"][f"{side}{part}"]
        parent = next(i for i, n in enumerate(doc["nodes"]) if node in n.get("children", []))
        local = np.linalg.inv(worlds(doc)[parent]) @ np.append(joints[part], 1.0)
        moved[node] = local[:3] - np.asarray(doc["nodes"][node].get("translation", [0.0, 0.0, 0.0]), float)
        doc["nodes"][node]["translation"] = local[:3].tolist()


def rebind(rig: dict, side: str, seat: dict) -> None:
    index = {name: rig["names"].index(f"{side}{name}") for name in ("Shoulder", "Arm", "ForeArm", "Hand")}
    for v in np.where(seat["arm"])[0]:
        row = arm_weights(float(seat["share"][v]))
        rig["joint_ids"][v] = [index[k] for k in row] + [0] * (4 - len(row))
        rig["weights"][v] = list(row.values()) + [0.0] * (4 - len(row))
    rig["joint_ids"][seat["wing"]] = [index["Shoulder"], 0, 0, 0]
    rig["weights"][seat["wing"]] = [1.0, 0.0, 0.0, 0.0]


def shift_translation_keys(doc: dict, blob: bytearray, moved: Dict[int, np.ndarray]) -> int:
    """Every clip's translation keys of a moved joint move by the joint's offset (each sampler output once). Returns how many moved."""

    shifted = set()
    for animation in doc.get("animations", []):
        for channel in animation["channels"]:
            node = channel["target"].get("node")
            output = animation["samplers"][channel["sampler"]]["output"]
            if channel["target"]["path"] == "translation" and node in moved and output not in shifted:
                put(doc, blob, output, get(doc, blob, output).astype(float) + moved[node])
                shifted.add(output)
    return len(shifted)


def seat_arms(source: Path, target: Path) -> dict:
    """Repair `source` into `target` by the rules of the module docstring, and report each side's numbers."""

    doc, blob = read_glb(source)
    rig = load_rig(doc, blob)
    positions, heads = rig["positions"], rig["heads"]
    body_height = float(heads["Head"][1] - positions[:, 1].min())
    report = {"source": str(source), "sides": {}}
    moved: Dict[int, np.ndarray] = {}
    for side in ("Left", "Right"):
        seat = seat_side(side, positions, rig["triangles"], rig["dominant"], heads, body_height)
        report["sides"][side] = seat["numbers"]
        move_joints(doc, rig, side, seat["joints"], moved)
        rebind(rig, side, seat)
    world = worlds(doc)
    skin, attributes = rig["skin"], rig["attributes"]
    put(doc, blob, skin["inverseBindMatrices"], np.stack([np.linalg.inv(world[j]) for j in skin["joints"]]).transpose(0, 2, 1).reshape(-1, 16))
    put(doc, blob, attributes["JOINTS_0"], rig["joint_ids"])
    put(doc, blob, attributes["WEIGHTS_0"], rig["weights"])
    report["translation_tracks_shifted"] = shift_translation_keys(doc, blob, moved)
    write_glb(target, doc, blob)
    return report
