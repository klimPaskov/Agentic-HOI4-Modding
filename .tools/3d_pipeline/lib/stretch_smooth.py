"""Smooth a unit's skin weights where its own clips stretch the mesh, without Blender (the `stretch` repair).

Tripo's auto-rig gives each vertex the weights of a few bones with hard borders between them. Where a clip turns a joint far, the edges
across such a border stretch or squash: the zombie's armpits and back swelled, its waist stretched, the orc's thighs pulled at the cloak.
The kit's `weights` repair (repair_unit.py) blends only weight seams and leg seams, which these are not, so it changed nothing. This rule
reads the exported `.mesh` and every `.anim` of the unit, as the game plays them, and works where the clips measurably deform:

1. Seeds: the vertices of every edge that UNIT-ANIM-STRETCH's measure (`lib/pdx_deform`: 1.5 times and 0.5% of the height) counts as
   stretched or squashed in some frame of some clip. Vertices are welded by position first, so a UV seam does not cut the region.
2. Region: the seeds grown `RINGS` edge rings outward. Locked vertices never change and never seed: any vertex with weight on a locked
   bone (a held weapon, which must stay rigid, and the chain stage's cloak and wing bones, whose weights that stage sets by its own rule).
3. Smoothing: each region vertex's weights move halfway (`LAMBDA`) to the mean of its neighbours', `passes` times, with every vertex outside
   the region held fixed, so the change fades into the untouched skin. Then the `MAX_INFLUENCES` largest weights are kept and normalised.
   A vertex only ever gets bones its neighbours already have, and only bones of its own shape's skeleton.
4. Choice: each of `PASS_STEPS` is measured on every clip (the edges the region touches are skinned again, the rest keep their counts).
   The kept strength is the one with the fewest deformed edges summed over the clips' worst frames, provided no clip's worst stretched or
   squashed count rises by more than `WORSEN_SHARE` and no edge grows further than before. When no strength helps, nothing changes.

Only the `ix`, `w` and `bones` values of the `skin` blocks change, in place: positions, triangles, the skeleton and the clips stay as they
were, so every clip still plays.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform
from .pdx_binary import PdxFormatError

RINGS = 2
LAMBDA = 0.5
PASS_STEPS = (2, 4, 8, 16)
MAX_INFLUENCES = 4
WORSEN_SHARE = 0.02


@dataclass
class SmoothResult:
    changed: bool
    passes: int = 0
    seeds: int = 0
    region: int = 0
    vertices_changed: int = 0
    before: Dict[str, Dict[str, float]] = field(default_factory=dict)
    after: Dict[str, Dict[str, float]] = field(default_factory=dict)
    trials: Dict[int, int] = field(default_factory=dict)
    note: str = ""


# ---- reading and writing the skin streams in place -------------------------------------------------------------------


@dataclass
class _Stream:
    shape: int
    count: int
    ix_offset: int = -1
    w_offset: int = -1
    bones_offset: int = -1
    bones: int = 4
    local: Dict[str, int] = field(default_factory=dict)  # bone name -> the shape's local index


def _object(data: bytes, position: int) -> Tuple[int, str, int]:
    """(depth, name, next position) of the object header at `position`."""

    depth = 0
    while data[position] == ord("["):
        depth += 1
        position += 1
    end = data.index(b"\0", position)
    return depth, data[position:end].decode("latin-1"), end + 1


def _property(data: bytes, position: int) -> Tuple[str, int, int, int]:
    """(name, value count, offset of the values, next position) of the property at `position`."""

    if data[position] != ord("!"):
        raise PdxFormatError(f"unexpected byte {data[position]:#x} at {position}")
    length = data[position + 1]
    name = data[position + 2:position + 2 + length].decode("latin-1").rstrip("\0")
    start = position + 2 + length
    count = struct.unpack_from("<i", data, start + 1)[0]
    values = start + 5
    if chr(data[start]) != "s":
        return name, count, values, values + 4 * count
    position = values
    for _ in range(count):
        position += 4 + struct.unpack_from("<i", data, position)[0]
    return name, count, values, position


def _note_skin(stream: _Stream, data: bytes, name: str, values: int) -> None:
    if name == "ix":
        stream.ix_offset = values
    elif name == "w":
        stream.w_offset = values
    elif name == "bones":
        stream.bones_offset = values
        stream.bones = struct.unpack_from("<i", data, values)[0]


def _streams(data: bytes) -> List[_Stream]:
    """Every mesh stream in the order `pdx_deform.load_mesh` reads them, with the byte offsets of its skin values."""

    if data[:4] != b"@@b@":
        raise PdxFormatError("not a Paradox binary file")
    position, path = 4, []
    streams: List[_Stream] = []
    skeleton: Dict[str, int] = {}
    shape = -1
    while position < len(data):
        if data[position] == ord("["):
            depth, name, position = _object(data, position)
            del path[depth - 1:]
            path.append(name)
            if depth == 2 and path[0] == "object":
                shape += 1
                skeleton = {}  # one dict per shape, shared by its streams and filled whenever its skeleton block comes
            if depth == 3 and name == "mesh":
                streams.append(_Stream(shape, 0, local=skeleton))
            continue
        name, count, values, position = _property(data, position)
        if len(path) == 4 and path[2] == "skeleton" and name == "ix":
            skeleton[path[3]] = struct.unpack_from("<i", data, values)[0]
        elif len(path) == 3 and path[2] == "mesh" and name == "p":
            streams[-1].count = count // 3
        elif len(path) == 4 and path[2] == "mesh" and path[3] == "skin":
            _note_skin(streams[-1], data, name, values)
    return streams


def write_weights(mesh_path: Path, out_path: Path, joints: np.ndarray, weights: np.ndarray, bones: Sequence[str]) -> None:
    """Write `out_path`: `mesh_path` with every stream's skin set to (V, 4) global `joints` and `weights` (`bones` names them)."""

    data = bytearray(Path(mesh_path).read_bytes())
    offset = 0
    for stream in _streams(bytes(data)):
        rows = slice(offset, offset + stream.count)
        offset += stream.count
        if stream.ix_offset < 0 or stream.w_offset < 0:
            continue
        ix = np.full((stream.count, 4), -1, np.int32)
        ww = np.zeros((stream.count, 4), np.float32)
        used = 0
        for v, (row_j, row_w) in enumerate(zip(joints[rows], weights[rows])):
            k = 0
            for j, w in zip(row_j, row_w):
                if j < 0 or w <= 0:
                    continue
                local = stream.local.get(bones[int(j)])
                if local is None:
                    raise PdxFormatError(f"bone {bones[int(j)]} is not in shape {stream.shape}'s skeleton")
                ix[v, k], ww[v, k] = local, w
                k += 1
            used = max(used, k)
        struct.pack_into(f"<{4 * stream.count}i", data, stream.ix_offset, *ix.ravel().tolist())
        struct.pack_into(f"<{4 * stream.count}f", data, stream.w_offset, *ww.ravel().tolist())
        if stream.bones_offset >= 0 and used > stream.bones:
            struct.pack_into("<i", data, stream.bones_offset, used)
    Path(out_path).write_bytes(bytes(data))


# ---- measuring --------------------------------------------------------------------------------------------------------


def _skin_subset(positions: np.ndarray, joints: np.ndarray, weights: np.ndarray, matrices: np.ndarray) -> np.ndarray:
    out = np.zeros_like(positions)
    safe = np.clip(joints, 0, None)
    for k in range(joints.shape[1]):
        w = weights[:, k]
        used = w > 0
        if used.any():
            m = matrices[safe[used, k]]
            out[used] += w[used, None] * (np.einsum("vij,vj->vi", m[:, :3, :3], positions[used]) + m[:, :3, 3])
    still = weights.sum(axis=1) == 0
    out[still] = positions[still]
    return out


def _deformed(rest: np.ndarray, length: np.ndarray, height: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    growth = (length - rest) / height
    usable = rest > 1e-9
    ratio = np.where(usable, length / np.where(usable, rest, 1.0), 1.0)
    return (ratio > pdx_deform.STRETCH_RATIO) & (growth > pdx_deform.SIGNIFICANT_SHARE), \
        (ratio < pdx_deform.SQUASH_RATIO) & (-growth > pdx_deform.SIGNIFICANT_SHARE), growth


class _Clips:
    """Every clip's per-frame skinning matrices and the deformed edges of the unchanged mesh, kept to rescore a weight change."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation], edges: np.ndarray):
        self.mesh, self.edges = mesh, edges
        self.height = max(mesh.height, 1e-6)
        self.rest = np.linalg.norm(mesh.positions[edges[:, 0]] - mesh.positions[edges[:, 1]], axis=1)
        self.matrices = {name: pdx_deform.skinning_matrices(mesh, anim) for name, anim in anims.items()}
        self.bad: Dict[str, np.ndarray] = {}  # per clip: (frames, edges) stretched or squashed
        self.masks: Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        for name, matrices in self.matrices.items():
            stretched, squashed, growth = [], [], []
            for frame in range(matrices.shape[0]):
                moved = pdx_deform.skin(mesh, matrices[frame])
                s, q, g = _deformed(self.rest, np.linalg.norm(moved[edges[:, 0]] - moved[edges[:, 1]], axis=1), self.height)
                stretched.append(s)
                squashed.append(q)
                growth.append(g)
            self.masks[name] = (np.array(stretched), np.array(squashed), np.array(growth))

    def summary(self, name: str, affected: Optional[np.ndarray] = None, joints=None, weights=None) -> Dict[str, float]:
        """{stretched, squashed, worst}: the clip's worst-frame counts and largest growth, with `affected` edges skinned by the new rows."""

        stretched, squashed, growth = self.masks[name]
        if affected is None or not affected.any():
            return {"stretched": int(stretched.sum(axis=1).max()), "squashed": int(squashed.sum(axis=1).max()), "worst": float(growth.max())}
        pick = self.edges[affected]
        vertices, local = np.unique(pick, return_inverse=True)
        local = local.reshape(-1, 2)
        keep_s = stretched[:, ~affected].sum(axis=1)
        keep_q = squashed[:, ~affected].sum(axis=1)
        keep_g = growth[:, ~affected].max(axis=1) if (~affected).any() else np.full(len(growth), -np.inf)
        s_count, q_count, worst = 0, 0, -np.inf
        for frame, matrices in enumerate(self.matrices[name]):
            moved = _skin_subset(self.mesh.positions[vertices], joints[vertices], weights[vertices], matrices)
            s, q, g = _deformed(self.rest[affected], np.linalg.norm(moved[local[:, 0]] - moved[local[:, 1]], axis=1), self.height)
            s_count = max(s_count, int(keep_s[frame] + s.sum()))
            q_count = max(q_count, int(keep_q[frame] + q.sum()))
            worst = max(worst, float(keep_g[frame]), float(g.max()))
        return {"stretched": s_count, "squashed": q_count, "worst": worst}


# ---- smoothing --------------------------------------------------------------------------------------------------------


def dense_weights(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    out = np.zeros((len(mesh.positions), len(mesh.bones)))
    for k in range(mesh.joints.shape[1]):
        used = (mesh.joints[:, k] >= 0) & (mesh.weights[:, k] > 0)
        np.add.at(out, (np.nonzero(used)[0], mesh.joints[used, k]), mesh.weights[used, k])
    return out


def sparse_rows(dense: np.ndarray, keep: int = MAX_INFLUENCES) -> Tuple[np.ndarray, np.ndarray]:
    """(V, 4) joints and weights: the `keep` largest of each row, normalised (-1 and 0 in empty slots)."""

    order = np.argsort(-dense, axis=1)[:, :keep]
    weights = np.take_along_axis(dense, order, axis=1)
    weights = np.where(weights > 1e-6, weights, 0.0)
    total = weights.sum(axis=1, keepdims=True)
    weights = np.divide(weights, total, out=np.zeros_like(weights), where=total > 0)
    joints = np.where(weights > 0, order, -1)
    if keep < 4:
        joints = np.pad(joints, ((0, 0), (0, 4 - keep)), constant_values=-1)
        weights = np.pad(weights, ((0, 0), (0, 4 - keep)))
    return joints.astype(np.int64), weights


def grow(seeds: np.ndarray, edges: np.ndarray, rings: int) -> np.ndarray:
    region = seeds.copy()
    for _ in range(rings):
        reached = region[edges].any(axis=1)
        region[edges[reached].ravel()] = True
    return region


def smooth_dense(dense: np.ndarray, edges: np.ndarray, region: np.ndarray, passes: int, allowed: Optional[np.ndarray] = None) -> np.ndarray:
    """`passes` Laplacian passes over the welded `edges`, moving only `region` rows (`LAMBDA` toward the neighbour mean). `allowed`
    (V, B) masks the bones a row may take (its shape's skeleton)."""

    out = dense.copy()
    degree = np.zeros(len(dense))
    np.add.at(degree, edges.ravel(), 1.0)
    for _ in range(passes):
        total = np.zeros_like(out)
        np.add.at(total, edges[:, 0], out[edges[:, 1]])
        np.add.at(total, edges[:, 1], out[edges[:, 0]])
        mean = np.divide(total, degree[:, None], out=out.copy(), where=degree[:, None] > 0)
        moved = (1.0 - LAMBDA) * out + LAMBDA * mean
        if allowed is not None:
            moved = np.where(allowed, moved, 0.0)
            sums = moved.sum(axis=1, keepdims=True)
            moved = np.divide(moved, sums, out=out.copy(), where=sums > 0)
        out[region] = moved[region]
    return out


def smooth(mesh_path: Path, anim_paths: Sequence[Path], out_path: Path, locked_bones: Sequence[str] = (),
           steps: Sequence[int] = PASS_STEPS, locked_prefixes: Sequence[str] = ()) -> SmoothResult:
    """Write `out_path` (the mesh, its weights smoothed where `anim_paths` deform it by the rule above) and return what changed.

    `locked_prefixes` locks every bone whose name starts with one of them (the chain stage's `Cloak` and `Wing` bones: their weights are
    set by that stage's own rule, and smoothed on the orc they let the dying cloak sink into the body past TRIPO-CHAIN-IN-BODY)."""

    mesh = pdx_deform.load_mesh(mesh_path)
    data = Path(mesh_path).read_bytes()
    if not mesh.skinned or not anim_paths:
        Path(out_path).write_bytes(data)
        return SmoothResult(False, note="no skin or no clips")
    anims = {Path(p).stem: pdx_deform.load_anim(p) for p in anim_paths}
    canon = pdx_deform.weld(mesh.positions, max(mesh.height, 1e-6) * 1e-5)
    edges = pdx_deform.mesh_edges(mesh)  # pairs of canonical vertices
    clips = _Clips(mesh, anims, edges)
    before = {name: clips.summary(name) for name in anims}

    dense = dense_weights(mesh)
    locked = locked_vertices(mesh, dense, canon, locked_bones, locked_prefixes)
    unskinned = dense.sum(axis=1) == 0
    bad_any = np.zeros(len(edges), bool)
    for stretched, squashed, _growth in clips.masks.values():
        bad_any |= (stretched | squashed).any(axis=0)
    seeds = np.zeros(len(dense), bool)
    seeds[edges[bad_any].ravel()] = True
    seeds &= ~locked & ~unskinned
    if not seeds.any():
        Path(out_path).write_bytes(data)
        return SmoothResult(False, before=before, after=before, note="no clip deforms an edge")
    region = grow(seeds, edges, RINGS) & ~locked & ~unskinned
    best, trials = None, {}
    total_before = sum(b["stretched"] + b["squashed"] for b in before.values())
    for passes in steps:
        joints, weights, changed_rows = smoothed_rows(mesh, dense, canon, edges, region, passes)
        after = {name: clips.summary(name, changed_rows[edges].any(axis=1), joints, weights) for name in anims}
        total = sum(a["stretched"] + a["squashed"] for a in after.values())
        trials[int(passes)] = int(total)
        if not any(worse(before[n], after[n]) for n in anims) and total < total_before and (best is None or total < best[0]):
            best = (total, int(passes), joints, weights, after, int(changed_rows.sum()))
    if best is None:
        Path(out_path).write_bytes(data)
        return SmoothResult(False, seeds=int(seeds.sum()), region=int(region.sum()), before=before, after=before, trials=trials,
                            note="no strength lowered the deformed edges without making a clip worse")
    _total, passes, joints, weights, after, count = best
    write_weights(mesh_path, out_path, joints, weights, mesh.bones)
    return SmoothResult(True, passes, int(seeds.sum()), int(region.sum()), count, before, after, trials)


def locked_vertices(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, canon: np.ndarray, locked_bones: Sequence[str],
                    locked_prefixes: Sequence[str]) -> np.ndarray:
    """Vertices with any weight on a locked bone; a welded point is locked when any of its copies is."""

    names = set(locked_bones)
    index = [i for i, name in enumerate(mesh.bones) if name in names or (locked_prefixes and name.startswith(tuple(locked_prefixes)))]
    locked = dense[:, index].sum(axis=1) > 0 if index else np.zeros(len(dense), bool)
    np.logical_or.at(locked, canon, locked.copy())
    return locked[canon]


def smoothed_rows(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, canon: np.ndarray, edges: np.ndarray, region: np.ndarray,
                  passes: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(joints, weights, changed rows) after `passes` passes over `region`. The smoothing runs on the canonical vertices (welded copies are
    one point) and is copied to every copy. A vertex only takes bones of its own shape's skeleton."""

    allowed = None
    shapes = np.unique(mesh.shape)
    if len(shapes) > 1:
        per_shape = {s: dense[mesh.shape == s].sum(axis=0) > 0 for s in shapes}
        allowed = np.stack([per_shape[s] for s in mesh.shape])
    is_canon = np.zeros(len(dense), bool)
    is_canon[np.unique(canon)] = True
    smoothed = smooth_dense(dense, edges, region & is_canon, passes, allowed)[canon]
    changed = region[canon] | region
    joints, weights = sparse_rows(np.where(changed[:, None], smoothed, dense))
    return np.where(changed[:, None], joints, mesh.joints), np.where(changed[:, None], weights, mesh.weights), changed


def worse(before: Dict[str, float], after: Dict[str, float]) -> bool:
    """A clip is worse when its worst-frame stretched or squashed count rises by more than `WORSEN_SHARE`, or one edge grows further."""

    return (after["stretched"] > before["stretched"] * (1 + WORSEN_SHARE) + 1
            or after["squashed"] > before["squashed"] * (1 + WORSEN_SHARE) + 1
            or after["worst"] > max(before["worst"], 0.0) * (1 + WORSEN_SHARE) + 1e-6)
