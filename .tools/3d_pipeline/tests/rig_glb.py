"""A small rigged GLB shaped like a Tripo export, for tests that need no Blender and no real model.

It follows the structure measured on a real Tripo export of November 2026 (a zombie, 66 joints, 9 clips): the armature node holds the Mixamo
hips chain, the skinned mesh node `tripo_node_<id>` (its mesh `tripo_mesh_<id>`, not `tripo_part_0`) and one more joint, `neutral_bone`: a
direct child of the armature, with no children and no animation channel, turned -90 degrees about X, listed in the skin's joints. Here the
chain is shorter (Hips, Spine, Head, LeftUpLeg, LeftLeg, LeftHand and a finger), and the mesh is one small closed shape around each joint.
"""

from __future__ import annotations

import json
import os
import struct
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

RELATIVE_EXPORT = Path(".work") / "haiku-e2e" / "inbox" / "zombie__rigged.glb"


def find_real_export() -> Path:
    """The export a small model made on 2026-11-19 (a zombie, Tripo's auto-rig after it began to add `neutral_bone`). It is not tracked, so the
    test looks for `.work/haiku-e2e/inbox/zombie__rigged.glb` above this file and beside the repository's own folder, and `TRIPO_REAL_EXPORT`
    names another export with the same defect. Where there is none, the test is skipped."""

    named = os.environ.get("TRIPO_REAL_EXPORT", "")
    if named:
        return Path(named)
    here = Path(__file__).resolve()
    repository = here.parents[3]
    for folder in [*here.parents, *(sibling for sibling in repository.parent.iterdir() if sibling.is_dir())]:
        if (folder / RELATIVE_EXPORT).is_file():
            return folder / RELATIVE_EXPORT
    return Path("zombie__rigged.glb")


REAL_EXPORT = find_real_export()

# name, parent index in this list (None: under the armature), local translation. Y is up, as in a glTF.
CHAIN: List[Tuple[str, Optional[int], Tuple[float, float, float]]] = [
    ("mixamorig:Hips", None, (0.0, 1.0, 0.0)),
    ("mixamorig:Spine", 0, (0.0, 0.3, 0.0)),
    ("mixamorig:Head", 1, (0.0, 0.4, 0.0)),
    ("mixamorig:LeftUpLeg", 0, (0.1, -0.1, 0.0)),
    ("mixamorig:LeftLeg", 3, (0.0, -0.45, 0.0)),
    ("mixamorig:LeftHand", 1, (0.35, 0.1, 0.0)),
    ("mixamorig:LeftHandIndex1", 5, (0.05, 0.0, 0.0)),
]
MESH_NAME, NODE_NAME = "tripo_mesh_0cbdda7a", "tripo_node_0cbdda7a"
LEAN = [[0.0, 0.0, 0.0, 1.0], [0.0871557, 0.0, 0.0, 0.9961947], [0.0, 0.0, 0.0, 1.0]]
BOB = [[0.0, 1.0, 0.0], [0.0, 1.04, 0.0], [0.0, 1.0, 0.0]]
TETRAHEDRON = ([0.05, 0.0, 0.0], [-0.05, 0.0, 0.05], [-0.05, 0.0, -0.05], [0.0, 0.08, 0.0])


def _pad(data: bytes) -> bytes:
    return data + b"\0" * (-len(data) % 4)


class Skeleton:
    """The armature, the Mixamo chain, the extra joint and the mesh node, as glTF nodes."""

    def __init__(self, extra_joint: Optional[str], extra_children: bool):
        self.names = [name for name, _parent, _t in CHAIN]
        self.nodes: List[dict] = [{"name": "Armature", "children": []}]
        self.index: Dict[str, int] = {}
        for name, _parent, translation in CHAIN:
            self.index[name] = len(self.nodes)
            self.nodes.append({"name": name, "translation": list(translation)})
        for name, parent, _t in CHAIN:
            holder = 0 if parent is None else self.index[self.names[parent]]
            self.nodes[holder]["children"] = self.nodes[holder].get("children", []) + [self.index[name]]
        self.joints = [self.index[name] for name in self.names]
        self.extra_index: Optional[int] = None
        if extra_joint:
            self._add_extra(extra_joint, extra_children)
        self.nodes.append({"name": NODE_NAME, "mesh": 0, "skin": 0})
        self.nodes[0]["children"].append(len(self.nodes) - 1)
        self._world: Dict[int, np.ndarray] = {}

    def _add_extra(self, name: str, with_child: bool) -> None:
        self.extra_index = len(self.nodes)
        self.nodes.append({"name": name, "rotation": [-0.7071067690849304, 0.0, 0.0, 0.7071067690849304]})
        self.nodes[0]["children"].append(self.extra_index)
        self.joints.append(self.extra_index)
        if with_child:
            self.nodes.append({"name": name + "_child", "translation": [0.0, 0.1, 0.0]})
            self.nodes[self.extra_index]["children"] = [len(self.nodes) - 1]
            self.joints.append(len(self.nodes) - 1)

    def world(self, i: int) -> np.ndarray:
        if i not in self._world:
            local = np.eye(4)
            local[:3, 3] = self.nodes[i].get("translation", [0, 0, 0])
            holder = next((p for p, node in enumerate(self.nodes) if i in node.get("children", [])), None)
            self._world[i] = self.world(holder) @ local if holder is not None else local
        return self._world[i]


class Buffer:
    """The binary chunk, with the buffer views and accessors that describe it."""

    def __init__(self) -> None:
        self.blob = b""
        self.views: List[dict] = []
        self.accessors: List[dict] = []

    def add(self, array: np.ndarray, kind: str, component: int) -> int:
        data = _pad(np.ascontiguousarray(array).tobytes())
        self.views.append({"buffer": 0, "byteOffset": len(self.blob), "byteLength": len(data)})
        self.accessors.append({"bufferView": len(self.views) - 1, "componentType": component, "count": len(array), "type": kind})
        self.blob += data
        return len(self.accessors) - 1


def _shapes(skeleton: Skeleton) -> Tuple[list, list, list, list]:
    """A tetrahedron of four vertices at every chain joint, bound to that joint alone: positions, joint ids, weights, triangles."""

    positions, joint_ids, weights, triangles = [], [], [], []
    for slot, name in enumerate(skeleton.names):
        centre = skeleton.world(skeleton.index[name])[:3, 3]
        base = len(positions)
        for corner in TETRAHEDRON:
            positions.append(centre + np.array(corner))
            joint_ids.append([slot, 0, 0, 0])
            weights.append([1.0, 0.0, 0.0, 0.0])
        triangles += [[base, base + 1, base + 2], [base, base + 3, base + 1], [base + 1, base + 3, base + 2], [base + 2, base + 3, base]]
    return positions, joint_ids, weights, triangles


def _animations(buffer: Buffer, skeleton: Skeleton, clips: Sequence[str], animate_extra: bool) -> List[dict]:
    animations = []
    for clip in clips:
        times = buffer.add(np.array([0.0, 0.5, 1.0], np.float32), "SCALAR", 5126)
        bob = buffer.add(np.array(BOB, np.float32), "VEC3", 5126)
        lean = buffer.add(np.array(LEAN, np.float32), "VEC4", 5126)
        samplers = [{"input": times, "output": bob}, {"input": times, "output": lean}]
        channels = [
            {"sampler": 0, "target": {"node": skeleton.index["mixamorig:Hips"], "path": "translation"}},
            {"sampler": 1, "target": {"node": skeleton.index["mixamorig:Spine"], "path": "rotation"}},
        ]
        if animate_extra and skeleton.extra_index is not None:
            samplers.append({"input": times, "output": lean})
            channels.append({"sampler": 2, "target": {"node": skeleton.extra_index, "path": "rotation"}})
        animations.append({"name": clip, "samplers": samplers, "channels": channels})
    return animations


def write_rig_glb(
    path: Path,
    *,
    extra_joint: Optional[str] = "neutral_bone",
    extra_animated: bool = False,
    extra_children: bool = False,
    extra_weight: float = 0.4,
    extra_vertex: int = 8,
    extra_position: Optional[Tuple[float, float, float]] = None,
    clips: Sequence[str] = ("idle", "walk"),
) -> Dict[str, object]:
    """Write the GLB. Every joint of CHAIN gets a small tetrahedron of four vertices bound to it alone. The vertex `extra_vertex` of the
    mesh (by default the first vertex of the head joint's shape, vertices 8 to 11) also carries `extra_weight` on the extra joint, taken from
    its own joint. Returns {"nodes": {name: node index}, "vertex": the index of the weighted vertex, "extra_index": the extra joint's node}."""

    skeleton = Skeleton(extra_joint, extra_children)
    positions, joint_ids, weights, triangles = _shapes(skeleton)
    if extra_joint:
        if extra_position is not None:
            positions[extra_vertex] = np.array(extra_position, float)
        joint_ids[extra_vertex] = [joint_ids[extra_vertex][0], len(skeleton.names), 0, 0]
        weights[extra_vertex] = [1.0 - extra_weight, extra_weight, 0.0, 0.0]
    buffer = Buffer()
    attributes = {
        "POSITION": buffer.add(np.array(positions, np.float32), "VEC3", 5126),
        "JOINTS_0": buffer.add(np.array(joint_ids, np.uint8), "VEC4", 5121),
        "WEIGHTS_0": buffer.add(np.array(weights, np.float32), "VEC4", 5126),
    }
    indices = buffer.add(np.array(triangles, np.uint16).ravel().reshape(-1, 1), "SCALAR", 5123)
    inverse = np.array([np.linalg.inv(skeleton.world(j)).T for j in skeleton.joints], np.float32).reshape(len(skeleton.joints), 16)
    inverse_accessor = buffer.add(inverse, "MAT4", 5126)
    buffer.accessors[inverse_accessor]["count"] = len(skeleton.joints)
    animations = _animations(buffer, skeleton, clips, extra_animated)
    doc = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"name": "Scene", "nodes": [0]}],
        "nodes": skeleton.nodes,
        "skins": [{"joints": skeleton.joints, "inverseBindMatrices": inverse_accessor}],
        "meshes": [{"name": MESH_NAME, "primitives": [{"attributes": attributes, "indices": indices}]}],
        "buffers": [{"byteLength": len(buffer.blob)}],
        "bufferViews": buffer.views,
        "accessors": buffer.accessors,
        "animations": animations,
    }
    text = _pad(json.dumps(doc).encode()).replace(b"\0", b" ")
    body = struct.pack("<I4s", len(text), b"JSON") + text + struct.pack("<I4s", len(buffer.blob), b"BIN\0") + buffer.blob
    Path(path).write_bytes(struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body)
    return {"nodes": skeleton.index, "vertex": extra_vertex, "extra_index": skeleton.extra_index}
