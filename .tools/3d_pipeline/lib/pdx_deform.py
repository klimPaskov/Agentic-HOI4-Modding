"""Measure a unit's surface and its skinned deformation from the exported `.mesh` and `.anim` bytes.

No Blender: the mesh, skin weights, skeleton and animation samples are decoded with
`pdx_binary` and skinned with numpy the way `gfx/FX/pdxmesh.shader` does (linear blend
skinning, at most four influences). Everything is measured in the file's own space (Y up).

- `load_mesh` combines every stream of every shape into one vertex and triangle list.
- `surface_report` welds coincident vertices and measures open loops, non-manifold edges,
  winding flips and inside-out closed parts.
- `bridge_edges` finds rest-pose edges whose two vertices follow bones that are far apart in
  the skeleton (an arm joined to a thigh). Skinning tears such edges when the clip moves.
- `deformation_report` skins every frame of an `.anim` and measures stretched and squashed
  edges and the lowest point against the rest pose's ground.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from .pdx_binary import PdxFormatError, PdxNode, read

# An edge counts as deformed when its length changes by this factor and by this share of the
# unit's height. The share keeps tiny edges (a few millimetres on a 2 m soldier) from counting.
STRETCH_RATIO = 1.5
SQUASH_RATIO = 1.0 / STRETCH_RATIO
SIGNIFICANT_SHARE = 0.005
# Bones this many parent steps apart or more do not share a joint, so an edge between their
# regions bridges two body parts (hand to thigh, left leg to right leg).
BRIDGE_HOPS = 3


@dataclass
class SkinnedMesh:
    positions: np.ndarray  # (V, 3)
    triangles: np.ndarray  # (T, 3) indices into positions
    joints: np.ndarray  # (V, 4) global bone indices, -1 for none
    weights: np.ndarray  # (V, 4)
    bones: List[str]
    parents: List[int]  # global index of each bone's parent, -1 for a root
    inverse_bind: np.ndarray  # (B, 4, 4)
    skinned: bool = True

    @property
    def height(self) -> float:
        return float(np.ptp(self.positions[:, 1])) if len(self.positions) else 0.0


def _matrix_from_tx(tx: List[float]) -> np.ndarray:
    """The 12 `tx` floats are a column-major 3x4 inverse bind matrix (io_pdx_mesh's layout)."""

    values = np.asarray(tx, dtype=float)
    matrix = np.eye(4)
    matrix[:3, :4] = values.reshape(4, 3).T
    return matrix


class _Skeleton:
    """Bones gathered across a file's shapes, in first-seen order."""

    def __init__(self) -> None:
        self.bones: List[str] = []
        self.parent_names: Dict[str, Optional[str]] = {}
        self.inverse: Dict[str, np.ndarray] = {}

    def add_shape(self, skeleton: Optional[PdxNode]) -> Dict[int, str]:
        """Record a shape's joints; return its local joint index -> bone name."""

        if skeleton is None:
            return {}
        local = {int(joint.properties["ix"][0]): joint.name for joint in skeleton.children if joint.properties.get("ix")}
        for joint in skeleton.children:
            if joint.name in self.inverse or not joint.properties.get("ix"):
                continue
            self.bones.append(joint.name)
            tx = joint.properties.get("tx")
            self.inverse[joint.name] = _matrix_from_tx(tx) if tx and len(tx) == 12 else np.eye(4)
            parent = joint.properties.get("pa")
            self.parent_names[joint.name] = local.get(int(parent[0])) if parent else None
        return local


def _stream_skin(mesh: PdxNode, count: int, local: Dict[int, str]) -> tuple[np.ndarray, np.ndarray]:
    """One stream's (V, 4) bone names ("" for none) and weights."""

    names = np.full((count, 4), "", dtype=object)
    weights = np.zeros((count, 4))
    skin = mesh.child("skin")
    if skin is None or not skin.properties.get("ix") or not local:
        return names, weights
    per = int(skin.properties.get("bones", [4])[0])
    ix = np.asarray(skin.properties["ix"], dtype=np.int64).reshape(count, 4)[:, :per]
    ww = np.asarray(skin.properties["w"], dtype=float).reshape(count, 4)[:, :per]
    for column in range(per):
        for vertex in np.nonzero(ix[:, column] >= 0)[0]:
            names[vertex, column] = local.get(int(ix[vertex, column]), "")
        weights[:, column] = np.where(ix[:, column] >= 0, ww[:, column], 0.0)
    return names, weights


def load_mesh(path: Path) -> SkinnedMesh:
    objects = read(path).child("object")
    if objects is None:
        raise PdxFormatError("the file has no object block")
    skeleton = _Skeleton()
    positions, triangles, names, weights = [], [], [], []
    offset = 0
    for shape in objects.children:
        local = skeleton.add_shape(shape.child("skeleton"))
        for mesh in (node for node in shape.children if node.name == "mesh"):
            p = np.asarray(mesh.properties.get("p", []), dtype=float).reshape(-1, 3)
            stream_names, stream_weights = _stream_skin(mesh, len(p), local)
            positions.append(p)
            triangles.append(np.asarray(mesh.properties.get("tri", []), dtype=np.int64).reshape(-1, 3) + offset)
            names.append(stream_names)
            weights.append(stream_weights)
            offset += len(p)
    if not positions:
        raise PdxFormatError("the file has no mesh streams")
    index_of = {name: i for i, name in enumerate(skeleton.bones)}
    joints = np.vectorize(lambda name: index_of.get(name, -1), otypes=[np.int64])(np.concatenate(names))
    weight = np.where(joints >= 0, np.concatenate(weights), 0.0)
    total = weight.sum(axis=1, keepdims=True)
    bones = skeleton.bones
    return SkinnedMesh(
        positions=np.concatenate(positions),
        triangles=np.concatenate(triangles),
        joints=joints,
        weights=np.divide(weight, total, out=np.zeros_like(weight), where=total > 0),
        bones=bones,
        parents=[index_of.get(skeleton.parent_names[name] or "", -1) for name in bones],
        inverse_bind=np.stack([skeleton.inverse[name] for name in bones]) if bones else np.zeros((0, 4, 4)),
        skinned=bool(bones) and bool((total > 0).any()),
    )


def weld(positions: np.ndarray, tolerance: float) -> np.ndarray:
    """Map each vertex to the first vertex at the same position (split normals and UV seams)."""

    if len(positions) == 0:
        return np.zeros(0, dtype=np.int64)
    keys = np.round(positions / max(tolerance, 1e-12)).astype(np.int64)
    _, first, inverse = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    return first[inverse.ravel()]


@dataclass
class SurfaceReport:
    triangles: int
    open_edges: int
    open_loops: List[int]  # edge count of each open loop, largest first
    nonmanifold_edges: int
    winding_flips: int
    parts: int
    inside_out_parts: List[int]  # triangle count of each closed part whose volume is negative

    @property
    def largest_open_loop(self) -> int:
        return self.open_loops[0] if self.open_loops else 0


def _edges(triangles: np.ndarray) -> np.ndarray:
    return np.concatenate([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]])


def surface_report(mesh: SkinnedMesh, tolerance_share: float = 1e-5) -> SurfaceReport:
    canon = weld(mesh.positions, max(mesh.height, 1e-6) * tolerance_share)
    tris = canon[mesh.triangles]
    tris = tris[(tris[:, 0] != tris[:, 1]) & (tris[:, 1] != tris[:, 2]) & (tris[:, 2] != tris[:, 0])]
    directed = _edges(tris)
    undirected = np.sort(directed, axis=1)
    keys, inverse, counts = np.unique(undirected, axis=0, return_inverse=True, return_counts=True)
    inverse = inverse.ravel()
    open_mask = counts == 1
    nonmanifold = int((counts > 2).sum())
    # A manifold edge whose two triangles walk it in the same direction is a winding flip.
    forward = directed[:, 0] < directed[:, 1]
    same = np.zeros(len(keys), dtype=np.int64)
    np.add.at(same, inverse, np.where(forward, 1, -1))
    flips = int(((counts == 2) & (np.abs(same) == 2)).sum())
    # Open loops: connected components of open edges.
    loops: List[int] = []
    open_edges = keys[open_mask]
    if len(open_edges):
        parent = {}

        def find(a: int) -> int:
            while parent.setdefault(a, a) != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for a, b in open_edges:
            ra, rb = find(int(a)), find(int(b))
            if ra != rb:
                parent[ra] = rb
        sizes: Dict[int, int] = {}
        for a, _ in open_edges:
            root = find(int(a))
            sizes[root] = sizes.get(root, 0) + 1
        loops = sorted(sizes.values(), reverse=True)
    # Parts: connected components of triangles over shared welded vertices.
    vertex_parent = np.arange(len(mesh.positions))

    def vfind(a: int) -> int:
        while vertex_parent[a] != a:
            vertex_parent[a] = vertex_parent[vertex_parent[a]]
            a = vertex_parent[a]
        return a

    for a, b in np.unique(undirected, axis=0):
        ra, rb = vfind(int(a)), vfind(int(b))
        if ra != rb:
            vertex_parent[ra] = rb
    part_of = np.array([vfind(int(t[0])) for t in tris]) if len(tris) else np.zeros(0, dtype=np.int64)
    part_ids = np.unique(part_of)
    # Inside-out: a closed part (no open or non-manifold edge) with negative signed volume.
    edge_part = part_of[np.arange(len(directed)) % len(tris)] if len(tris) else np.zeros(0, dtype=np.int64)
    bad_edge = (counts[inverse] != 2)
    broken_parts = set(np.unique(edge_part[bad_edge]).tolist()) if len(tris) else set()
    p = mesh.positions
    volume = np.einsum("ij,ij->i", p[tris[:, 0]], np.cross(p[tris[:, 1]], p[tris[:, 2]])) / 6.0 if len(tris) else np.zeros(0)
    inside_out: List[int] = []
    for part in part_ids:
        if int(part) in broken_parts:
            continue
        members = part_of == part
        if volume[members].sum() < 0:
            inside_out.append(int(members.sum()))
    return SurfaceReport(
        triangles=len(mesh.triangles),
        open_edges=int(open_mask.sum()),
        open_loops=loops,
        nonmanifold_edges=nonmanifold,
        winding_flips=flips,
        parts=len(part_ids),
        inside_out_parts=sorted(inside_out, reverse=True),
    )


def bone_hops(parents: List[int]) -> np.ndarray:
    """Number of parent steps between every pair of bones."""

    count = len(parents)
    depth = []
    for index in range(count):
        chain, node = [], index
        while node >= 0 and node not in chain:
            chain.append(node)
            node = parents[node]
        depth.append(chain)
    hops = np.zeros((count, count), dtype=np.int64)
    for a in range(count):
        position = {node: i for i, node in enumerate(depth[a])}
        for b in range(count):
            common = next((i for i, node in enumerate(depth[b]) if node in position), None)
            hops[a, b] = position[depth[b][common]] + common if common is not None else count
    return hops


def dominant_bones(mesh: SkinnedMesh) -> np.ndarray:
    best = np.argmax(mesh.weights, axis=1)
    return np.where(mesh.weights.max(axis=1) > 0, mesh.joints[np.arange(len(best)), best], -1)


def mesh_edges(mesh: SkinnedMesh) -> np.ndarray:
    """Unique undirected edges over welded vertices, as pairs of one original vertex each."""

    canon = weld(mesh.positions, max(mesh.height, 1e-6) * 1e-5)
    edges = np.sort(canon[_edges(mesh.triangles)], axis=1)
    edges = edges[edges[:, 0] != edges[:, 1]]
    return np.unique(edges, axis=0)


@dataclass
class BridgeReport:
    edges: int
    pairs: Dict[str, int] = field(default_factory=dict)  # "BoneA-BoneB" -> edges, largest first


def bridge_edges(mesh: SkinnedMesh, hops: int = BRIDGE_HOPS) -> BridgeReport:
    if not mesh.skinned:
        return BridgeReport(0)
    edges = mesh_edges(mesh)
    dominant = dominant_bones(mesh)
    a, b = dominant[edges[:, 0]], dominant[edges[:, 1]]
    valid = (a >= 0) & (b >= 0) & (a != b)
    distance = bone_hops(mesh.parents)
    far = np.zeros(len(edges), dtype=bool)
    far[valid] = distance[a[valid], b[valid]] >= hops
    # A vertex that already blends the other bone is a soft join, not a tear.
    def weight_of(vertex: np.ndarray, bone: np.ndarray) -> np.ndarray:
        return (mesh.weights[vertex] * (mesh.joints[vertex] == bone[:, None])).sum(axis=1)

    shared = np.zeros(len(edges))
    if far.any():
        shared[far] = np.maximum(
            weight_of(edges[far, 0], b[far]), weight_of(edges[far, 1], a[far])
        )
    hard = far & (shared < 0.1)
    pairs: Dict[str, int] = {}
    for x, y in zip(a[hard], b[hard]):
        key = "-".join(sorted((mesh.bones[x], mesh.bones[y])))
        pairs[key] = pairs.get(key, 0) + 1
    return BridgeReport(int(hard.sum()), dict(sorted(pairs.items(), key=lambda item: -item[1])))


@dataclass
class Animation:
    fps: float
    frames: int
    channels: Dict[str, Dict[str, np.ndarray]]  # joint -> {"t": (F,3), "q": (F,4), "s": (F,)}


def load_anim(path: Path) -> Animation:
    root = read(path)
    info = root.child("info")
    samples = root.child("samples")
    if info is None:
        raise PdxFormatError("the file has no info block")
    frames = int((info.properties.get("sa") or [0])[0])
    fps = float((info.properties.get("fps") or [0.0])[0])
    data = {key: np.asarray((samples.properties.get(key) if samples else None) or [], dtype=float) for key in "tqs"}
    cursor = {"t": 0, "q": 0, "s": 0}
    width = {"t": 3, "q": 4, "s": 1}
    keyed = []
    channels: Dict[str, Dict[str, np.ndarray]] = {}
    for joint in info.children:
        flags = str((joint.properties.get("sa") or [""])[0])
        rest = {
            "t": np.asarray(joint.properties.get("t", [0, 0, 0]), dtype=float),
            "q": np.asarray(joint.properties.get("q", [0, 0, 0, 1]), dtype=float),
            "s": np.asarray(joint.properties.get("s", [1])[:1], dtype=float),
        }
        channels[joint.name] = {key: np.tile(rest[key], (max(frames, 1), 1)) for key in "tqs"}
        keyed.append((joint.name, flags))
    for frame in range(frames):
        for name, flags in keyed:
            for key in "sqt":
                if key in flags:
                    size = width[key]
                    start = cursor[key]
                    if start + size > len(data[key]):
                        raise PdxFormatError(f"the {key} samples end early at frame {frame}")
                    channels[name][key][frame] = data[key][start : start + size]
                    cursor[key] = start + size
    for name in channels:
        channels[name]["s"] = channels[name]["s"][:, 0]
    return Animation(fps=fps, frames=frames, channels=channels)


def _quaternion_matrices(q: np.ndarray) -> np.ndarray:
    """(N,4) quaternions as x, y, z, w (PDX order) to (N,3,3) rotation matrices."""

    q = q / np.maximum(np.linalg.norm(q, axis=1, keepdims=True), 1e-12)
    x, y, z, w = q.T
    return np.stack(
        [
            np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], axis=1),
            np.stack([2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], axis=1),
            np.stack([2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)], axis=1),
        ],
        axis=1,
    )


def _bind_locals(mesh: SkinnedMesh) -> np.ndarray:
    world = np.linalg.inv(mesh.inverse_bind)
    local = np.empty_like(world)
    for index, parent in enumerate(mesh.parents):
        local[index] = world[index] if parent < 0 else np.linalg.inv(world[parent]) @ world[index]
    return local


def skinning_matrices(mesh: SkinnedMesh, anim: Animation) -> np.ndarray:
    """(F, B, 4, 4) matrices that move bind-pose vertices to each frame."""

    frames = max(anim.frames, 1)
    count = len(mesh.bones)
    local = np.tile(_bind_locals(mesh), (frames, 1, 1, 1))
    for index, name in enumerate(mesh.bones):
        channel = anim.channels.get(name)
        if channel is None:
            continue
        matrix = np.zeros((frames, 4, 4))
        matrix[:, :3, :3] = _quaternion_matrices(channel["q"]) * channel["s"][:, None, None]
        matrix[:, :3, 3] = channel["t"]
        matrix[:, 3, 3] = 1.0
        local[:, index] = matrix
    order = []
    seen = set()

    def visit(index: int) -> None:
        if index in seen:
            return
        if mesh.parents[index] >= 0:
            visit(mesh.parents[index])
        seen.add(index)
        order.append(index)

    for index in range(count):
        visit(index)
    world = np.empty_like(local)
    for index in order:
        parent = mesh.parents[index]
        world[:, index] = local[:, index] if parent < 0 else world[:, parent] @ local[:, index]
    return world @ mesh.inverse_bind[None]


def skin(mesh: SkinnedMesh, matrices: np.ndarray) -> np.ndarray:
    """Positions of every vertex for one frame's (B, 4, 4) skinning matrices."""

    joints = np.clip(mesh.joints, 0, None)
    moved = np.zeros_like(mesh.positions)
    # One influence at a time keeps memory at a few (V, 3) arrays, even for dense meshes.
    for k in range(joints.shape[1]):
        weight = mesh.weights[:, k]
        used = weight > 0
        if not used.any():
            continue
        m = matrices[joints[used, k]]
        moved[used] += weight[used, None] * (np.einsum("vij,vj->vi", m[:, :3, :3], mesh.positions[used]) + m[:, :3, 3])
    unweighted = mesh.weights.sum(axis=1) == 0
    moved[unweighted] = mesh.positions[unweighted]
    return moved


@dataclass
class DeformationReport:
    frames: int
    worst_frame: int
    stretched_edges: int  # most edges stretched in one frame
    squashed_edges: int  # most edges squashed in one frame
    worst_stretch_share: float  # largest edge growth, as a share of the unit's height
    lowest: float  # lowest point in any frame, as a share of height above the rest pose's ground
    highest_lowest: float  # highest "lowest point" in any frame (the unit hovering)
    worst_pairs: Dict[str, int] = field(default_factory=dict)
    lowest_frame: int = 0
    highest_frame: int = 0


def deformation_report(mesh: SkinnedMesh, anim: Animation) -> DeformationReport:
    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    edges = mesh_edges(mesh)
    rest = np.linalg.norm(mesh.positions[edges[:, 0]] - mesh.positions[edges[:, 1]], axis=1)
    usable = rest > 1e-9
    dominant = dominant_bones(mesh)
    report = DeformationReport(anim.frames, 0, 0, 0, 0.0, 9.0, -9.0)
    if not mesh.skinned:
        return report
    matrices = skinning_matrices(mesh, anim)
    worst_mask = None
    for frame in range(matrices.shape[0]):
        moved = skin(mesh, matrices[frame])
        length = np.linalg.norm(moved[edges[:, 0]] - moved[edges[:, 1]], axis=1)
        growth = (length - rest) / height
        ratio = np.where(usable, length / np.where(usable, rest, 1.0), 1.0)
        stretched = (ratio > STRETCH_RATIO) & (growth > SIGNIFICANT_SHARE)
        squashed = (ratio < SQUASH_RATIO) & (-growth > SIGNIFICANT_SHARE)
        if stretched.sum() > report.stretched_edges:
            report.stretched_edges = int(stretched.sum())
            report.worst_frame = frame
            worst_mask = stretched
        report.squashed_edges = max(report.squashed_edges, int(squashed.sum()))
        report.worst_stretch_share = max(report.worst_stretch_share, float(growth.max()))
        lowest = (float(moved[:, 1].min()) - ground) / height
        if lowest < report.lowest:
            report.lowest, report.lowest_frame = lowest, frame
        if lowest > report.highest_lowest:
            report.highest_lowest, report.highest_frame = lowest, frame
    if worst_mask is not None:
        pairs: Dict[str, int] = {}
        for x, y in zip(dominant[edges[worst_mask, 0]], dominant[edges[worst_mask, 1]]):
            if x < 0 or y < 0:
                continue
            key = "-".join(sorted({mesh.bones[x], mesh.bones[y]})) if x != y else mesh.bones[x]
            pairs[key] = pairs.get(key, 0) + 1
        report.worst_pairs = dict(sorted(pairs.items(), key=lambda item: -item[1])[:5])
    return report
