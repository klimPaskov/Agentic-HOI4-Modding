"""Extra joints that Tripo's auto-rig adds to the Mixamo skeleton, and what the intake does with them.

The route keeps the 22 Mixamo bones the kit names (`KIT_BONES` in tripo/prepare_tripo_unit.py) and merges every other bone (fingers,
toe ends) into its nearest kept ancestor. A joint with no kept ancestor at all has nothing to merge into. Tripo's auto-rig began adding
one in November 2026: `neutral_bone`, a childless joint directly under the armature, with no animation channel, turned -90 degrees
about X, and listed in the skin's joints. The exports made on 2026-11-13 to 15 do not have it, so the intake stopped on the first
export made after that with "Bone neutral_bone has no kept ancestor".

The rule: a leaf joint with no kept ancestor and no animation channel is an extra joint. The intake drops it. Whatever vertex weight it
carries moves to the kept kit bone nearest to the vertex (its distance to the bone's head-to-tail segment), or to the hips when no
kit bone lies within `NEAR_SHARE` of the body's largest extent. A joint with no kept ancestor that has children or an animation
channel is not an extra joint: it stops the intake with a message that names it, because dropping it would drop motion.

This module is plain Python with numpy, so the rule is tested without Blender. `tripo/prepare_tripo_unit.py` calls the same functions on
the bones and weights Blender imported, and `plan_from_glb` applies them to a GLB file for the tests and for a look before a run.
"""

from __future__ import annotations

import json
import math
import re
import struct
from pathlib import Path
from typing import Any, Collection, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

# Mixamo name (without the `mixamorig:` prefix) -> the kit's name. Every bone not named here is merged.
MIXAMO_KIT_BONES = {"Hips": "Hips", "Spine": "Spine", "Spine1": "Spine01", "Spine2": "Spine02", "Neck": "neck", "Head": "Head"}
for _side in ("Left", "Right"):
    for _part in ("Shoulder", "Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot", "ToeBase"):
        MIXAMO_KIT_BONES[f"{_side}{_part}"] = f"{_side}{_part}"
# The bones the grip and shield stages add later (tripo/grip_weapon.py, tripo/shield_stage.py): kept when a rig has them.
OPTIONAL_SHORT_NAMES = ("Weapon", "Shield")
# A vertex whose nearest kept bone is farther than this share of the body's largest extent goes to the hips instead.
NEAR_SHARE = 0.25
FALLBACK_BONE = "Hips"

Point = Tuple[float, float, float]


class ExtraJointError(ValueError):
    """A joint without a kept ancestor that cannot be dropped (it has children or an animation channel)."""


def short_name(name: str) -> str:
    return re.sub(r"^mixamorig\d*:", "", name)


def is_kit_bone(name: str) -> bool:
    return short_name(name) in MIXAMO_KIT_BONES or short_name(name) in OPTIONAL_SHORT_NAMES


def find_extra_joints(parents: Mapping[str, Optional[str]], kept: Collection[str], animated: Collection[str]) -> List[str]:
    """The joints to drop: no kept ancestor, no child, no animation channel. `parents` maps every bone to its parent's name (None for a
    root), `kept` is the set of kit bone names and `animated` the bones some clip keys. A joint with no kept ancestor that has children
    or channels raises ExtraJointError. A bone with a kept ancestor is never listed: it merges into that ancestor as before."""

    has_child = {parent for parent in parents.values() if parent is not None}
    extras: List[str] = []
    stuck: List[str] = []
    for name in parents:
        if name in kept:
            continue
        ancestor = parents[name]
        while ancestor is not None and ancestor not in kept:
            ancestor = parents.get(ancestor)
        if ancestor is not None:
            continue
        (stuck if name in has_child or name in animated else extras).append(name)
    if stuck:
        raise ExtraJointError(
            f"Bone {', '.join(sorted(stuck))} has no kept ancestor, and it has children or animation, so the intake cannot drop it. "
            "Tripo's Mixamo rig should hold only a childless, unanimated extra joint outside the Hips chain (neutral_bone). Export the rig again."
        )
    return sorted(extras)


def _distance_to_segment(point: Point, head: Point, tail: Point) -> float:
    p, a, b = np.asarray(point, float), np.asarray(head, float), np.asarray(tail, float)
    edge = b - a
    length = float(edge @ edge)
    along = 0.0 if length < 1e-18 else min(max(float((p - a) @ edge) / length, 0.0), 1.0)
    return float(np.linalg.norm(p - (a + along * edge)))


def nearest_kept_bone(point: Point, segments: Mapping[str, Tuple[Point, Point]], fallback: str, limit: float) -> str:
    """The kept bone whose head-to-tail segment is nearest to `point`, or `fallback` (the hips) when none is within `limit`."""

    best, best_distance = None, math.inf
    for name in sorted(segments):
        distance = _distance_to_segment(point, *segments[name])
        if distance < best_distance - 1e-12:
            best, best_distance = name, distance
    return best if best is not None and best_distance <= limit else fallback


def move_extra_weights(
    rows: List[Dict[str, float]],
    extras: Iterable[str],
    points: Sequence[Point],
    segments: Mapping[str, Tuple[Point, Point]],
    fallback: str,
    limit: float,
) -> int:
    """Move the weight of the extra joints in every vertex row (`{bone name: weight}`, changed in place) to the nearest kept bone of the
    vertex's own position. Returns how many (vertex, joint) weights moved. A zero weight is dropped without a move."""

    extra_set = set(extras)
    moved = 0
    for row, point in zip(rows, points):
        hit = {name: row.pop(name) for name in list(row) if name in extra_set}
        carried = [weight for weight in hit.values() if weight > 0.0]
        if not carried:
            continue
        target = nearest_kept_bone(point, segments, fallback, limit)
        row[target] = row.get(target, 0.0) + sum(carried)
        moved += len(carried)
    return moved


def near_limit(points: Sequence[Point]) -> float:
    """`NEAR_SHARE` of the body's largest extent over every axis."""

    if not len(points):
        return 0.0
    box = np.ptp(np.asarray(points, float), axis=0)
    return NEAR_SHARE * float(box.max())


def report_line(extras: Sequence[str], moved: int) -> str:
    """The one line the intake prints."""

    if not extras:
        return "extra joints dropped: none"
    return (f"extra joints dropped: {', '.join(extras)} ({len(extras)} joint{'s' if len(extras) != 1 else ''}, "
            f"{moved} vertex weight{'s' if moved != 1 else ''} moved to the nearest kit bone)")


# ---------------------------------------------------------------------------------------------
# A GLB file read without Blender
# ---------------------------------------------------------------------------------------------

_DTYPES = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _read_glb(path: Path) -> Tuple[dict, bytes]:
    data = Path(path).read_bytes()
    if data[:4] != b"glTF":
        raise ValueError(f"{path} is not a binary glTF file")
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    offset = 20 + length
    blob = b""
    if offset + 8 <= len(data):
        size = struct.unpack("<I", data[offset:offset + 4])[0]
        blob = data[offset + 8:offset + 8 + size]
    return doc, blob


def _accessor(doc: dict, blob: bytes, index: int) -> np.ndarray:
    accessor = doc["accessors"][index]
    view = doc["bufferViews"][accessor["bufferView"]]
    dtype = np.dtype(_DTYPES[accessor["componentType"]])
    width = _WIDTH[accessor["type"]]
    stride = view.get("byteStride") or dtype.itemsize * width
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    return np.ndarray(shape=(accessor["count"], width), dtype=dtype, buffer=blob, offset=start, strides=(stride, dtype.itemsize))


def _local_matrix(node: dict) -> np.ndarray:
    if "matrix" in node:
        return np.array(node["matrix"], float).reshape(4, 4).T
    x, y, z, w = node.get("rotation", [0.0, 0.0, 0.0, 1.0])
    rotation = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])
    out = np.eye(4)
    out[:3, :3] = rotation * np.array(node.get("scale", [1.0, 1.0, 1.0]), float)
    out[:3, 3] = node.get("translation", [0.0, 0.0, 0.0])
    return out


def read_skeleton(path: Path) -> Dict[str, Any]:
    """The first skin of a rigged GLB: `parents` ({joint name: parent joint name or None, the parent being the nearest ancestor node that
    is a joint}), `animated` (joints some clip keys), `heads` ({joint name: rest position}), `children`, and the first mesh's `points` and
    per-vertex `weights` ({joint name: weight}) rows."""

    doc, blob = _read_glb(path)
    nodes = doc["nodes"]
    parent_node: Dict[int, int] = {}
    for index, node in enumerate(nodes):
        for child in node.get("children", []):
            parent_node[child] = index
    joints = doc["skins"][0]["joints"]
    names = {index: nodes[index].get("name", str(index)) for index in joints}
    world: Dict[int, np.ndarray] = {}

    def resolve(index: int) -> np.ndarray:
        if index not in world:
            local = _local_matrix(nodes[index])
            world[index] = resolve(parent_node[index]) @ local if index in parent_node else local
        return world[index]

    def joint_parent(index: int) -> Optional[int]:
        parent = parent_node.get(index)
        while parent is not None and parent not in names:
            parent = parent_node.get(parent)
        return parent

    parents = {names[i]: (names[joint_parent(i)] if joint_parent(i) is not None else None) for i in joints}
    heads = {names[i]: tuple(float(v) for v in resolve(i)[:3, 3]) for i in joints}
    animated = {
        names[channel["target"]["node"]]
        for animation in doc.get("animations", []) for channel in animation.get("channels", [])
        if channel.get("target", {}).get("node") in names
    }
    children: Dict[str, List[str]] = {name: [] for name in names.values()}
    for name, parent in parents.items():
        if parent is not None:
            children[parent].append(name)
    out: Dict[str, Any] = {"parents": parents, "animated": animated, "heads": heads, "children": children, "points": [], "weights": []}
    for mesh_node in (node for node in nodes if node.get("skin") == 0 and "mesh" in node):
        for primitive in doc["meshes"][mesh_node["mesh"]]["primitives"]:
            attributes = primitive["attributes"]
            if "JOINTS_0" not in attributes:
                continue
            positions = _accessor(doc, blob, attributes["POSITION"]).astype(float)
            ids = _accessor(doc, blob, attributes["JOINTS_0"]).astype(int)
            weights = _accessor(doc, blob, attributes["WEIGHTS_0"]).astype(float)
            for point, row_ids, row_weights in zip(positions, ids, weights):
                row: Dict[str, float] = {}
                for joint, weight in zip(row_ids, row_weights):
                    if weight > 0.0:
                        name = names[joints[int(joint)]]
                        row[name] = row.get(name, 0.0) + float(weight)
                out["points"].append(tuple(float(v) for v in point))
                out["weights"].append(row)
        break
    return out


def plan_from_glb(path: Path) -> Dict[str, Any]:
    """What the intake does with the extra joints of a rigged GLB: `extras` (the joints it drops), `moved` (the weights it moves),
    `rows` (the vertex rows after the move) and `targets` ({extra joint: {bone that took its weight: count}}). Raises ExtraJointError for
    a joint that cannot be dropped."""

    skeleton = read_skeleton(path)
    kept = {name for name in skeleton["parents"] if is_kit_bone(name)}
    extras = find_extra_joints(skeleton["parents"], kept, skeleton["animated"])
    segments: Dict[str, Tuple[Point, Point]] = {}
    for name in sorted(kept):
        head = np.asarray(skeleton["heads"][name], float)
        below = [np.asarray(skeleton["heads"][child], float) for child in skeleton["children"][name]]
        tail = np.mean(below, axis=0) if below else head
        segments[name] = (tuple(head), tuple(tail))
    fallback = next((name for name in sorted(kept) if short_name(name) == FALLBACK_BONE), "")
    before = [dict(row) for row in skeleton["weights"]]
    rows = [dict(row) for row in skeleton["weights"]]
    moved = move_extra_weights(rows, extras, skeleton["points"], segments, fallback, near_limit(skeleton["points"]))
    targets: Dict[str, Dict[str, int]] = {}
    for old, new in zip(before, rows):
        for extra in extras:
            if old.get(extra, 0.0) > 0.0:
                gained = next((name for name in new if new[name] > old.get(name, 0.0) + 1e-12), "")
                targets.setdefault(extra, {})[gained] = targets.setdefault(extra, {}).get(gained, 0) + 1
    return {"extras": extras, "moved": moved, "rows": rows, "targets": targets, "line": report_line(extras, moved)}
