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
First of all, the hand bleed (`unbleed_hands`): hand weight on skin outside the hand's own part (cut from the arm across the
   middle of the forearm) goes to that skin's other bones, so cloth a resting hand lay against no longer rises with the hand.
   Every later step measures from these weights.
0. Before the smoothing, on a two-legged unit: the thigh split (`SPLIT_SHARES`). Cloth between the legs that Tripo weighted to both
   thighs gives part of the share both hold to the bone the legs hang from, kept on the same terms as a strength in step 4. The
   smoothing then starts from the split weights.

Only the `ix`, `w` and `bones` values of the `skin` blocks change, in place: positions, triangles, the skeleton and the clips stay as they
were, so every clip still plays.
"""

from __future__ import annotations

import math
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
# A vertex is locked when this share of its weight is on one prefix's chain bones (any other prefix: any weight). A cloak stays locked
# whole (smoothing its blend let the orc's dying cloak sink into the body); a wing's blend into the back may smooth, which cut the
# demon's root-zone stretch by about a fifth (attack 9.3% to 8.0%, idle 4.1% to 3.3%).
PREFIX_LOCK_SHARES = {"Wing": 0.5}
# Thigh split, tried before the smoothing on a two-legged unit: a vertex weighted to both thighs (a kilt or coat skirt between the legs)
# gives this share of the part both thighs hold equally (2 x the smaller thigh weight) to the bone the legs hang from, so a stride no
# longer tears it in two. Kept only when no clip gets worse. Offline on the orc at 0.5: retreat 234 to 158 stretched edges between the
# legs, death 188 to 116.
SPLIT_SHARES = (0.5, 1.0)
SPLIT_MIN = 0.05
# Hand bleed, first of all (`unbleed_hands`): the hand's own part is cut from the arm across the middle of the forearm. On the orc a cut
# at the upper arm reached the whole body (the forearm touches the torso), while the forearm cut kept each hand apart (528 and 738 of
# 18,375 vertices). A hand whose part is larger than this share of its shape touches the body and is left as it is.
HAND_CUT = (0.35, 0.65)
HAND_PART_MAX_SHARE = 0.2


@dataclass
class SmoothResult:
    changed: bool
    passes: int = 0
    seeds: int = 0
    region: int = 0
    vertices_changed: int = 0
    before: Dict[str, Dict[str, float]] = field(default_factory=dict)
    after: Dict[str, Dict[str, float]] = field(default_factory=dict)
    trials: Dict[str, int] = field(default_factory=dict)  # by passes, or "split <share>"
    note: str = ""
    hand_bleed: int = 0  # vertices whose hand weight went to their other bones (`unbleed_hands`)


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
    bled = write_unbled(mesh, mesh_path, out_path, canon, edges, locked_bones)
    if bled:
        mesh_path = out_path
        mesh = pdx_deform.load_mesh(mesh_path)
        data = Path(mesh_path).read_bytes()
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
        return SmoothResult(bool(bled), before=before, after=before, note="no clip deforms an edge", hand_bleed=bled)
    region = grow(seeds, edges, RINGS) & ~locked & ~unskinned
    best, trials = None, {}
    total_before = sum(b["stretched"] + b["squashed"] for b in before.values())
    split = best_split(mesh, dense, locked, clips, edges, before, trials)
    base_joints, base_weights, base_rows, split_note = mesh.joints, mesh.weights, np.zeros(len(dense), bool), ""
    if split is not None:
        best, dense, base_rows, split_note = split
        base_joints, base_weights = best[2], best[3]
    for passes in steps:
        joints, weights, changed_rows = smoothed_rows(mesh, dense, canon, edges, region, passes, base_joints, base_weights)
        changed_rows = changed_rows | base_rows
        after = {name: clips.summary(name, changed_rows[edges].any(axis=1), joints, weights) for name in anims}
        total = sum(a["stretched"] + a["squashed"] for a in after.values())
        trials[str(passes)] = int(total)
        if not any(worse(before[n], after[n]) for n in anims) and total < total_before and (best is None or total < best[0]):
            best = (total, int(passes), joints, weights, after, int(changed_rows.sum()))
    if best is None:
        Path(out_path).write_bytes(data)
        return SmoothResult(bool(bled), seeds=int(seeds.sum()), region=int(region.sum()), before=before, after=before, trials=trials,
                            note="no strength lowered the deformed edges without making a clip worse", hand_bleed=bled)
    _total, passes, joints, weights, after, count = best
    write_weights(mesh_path, out_path, joints, weights, mesh.bones)
    return SmoothResult(True, passes, int(seeds.sum()), int(region.sum()), count, before, after, trials, split_note, bled)



def write_unbled(mesh: pdx_deform.SkinnedMesh, mesh_path: Path, out_path: Path, canon: np.ndarray, edges: np.ndarray,
                 locked_bones: Sequence[str]) -> int:
    """Write `out_path` with the hand bleed removed (`unbleed_hands`) when there is any; return how many vertices changed."""

    dense = dense_weights(mesh)
    unbled, bled = unbleed_hands(mesh, dense, canon, edges, locked_bones)
    if bled:
        joints, weights = sparse_rows(unbled)
        rows = np.abs(unbled - dense).sum(axis=1) > 1e-9
        write_weights(mesh_path, out_path, np.where(rows[:, None], joints, mesh.joints), np.where(rows[:, None], weights, mesh.weights),
                      mesh.bones)
    return bled


def best_split(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, locked: np.ndarray, clips: "_Clips", edges: np.ndarray,
               before: Dict[str, Dict[str, float]], trials: Dict[str, int]) -> Optional[tuple]:
    """The kept thigh split (`SPLIT_SHARES`): ((total, 0, joints, weights, after, rows changed), split dense weights, changed rows, note),
    or None when no share lowers the deformed edges without making a clip worse. Each share's total goes into `trials`."""

    kept, base_total = None, sum(b["stretched"] + b["squashed"] for b in before.values())
    for share in SPLIT_SHARES:
        split = split_thighs(mesh, dense, locked, share)
        if split is None:
            break
        rows = np.abs(split - dense).sum(axis=1) > 1e-6
        joints, weights = sparse_rows(split)
        joints, weights = np.where(rows[:, None], joints, mesh.joints), np.where(rows[:, None], weights, mesh.weights)
        after = {name: clips.summary(name, rows[edges].any(axis=1), joints, weights) for name in before}
        total = sum(a["stretched"] + a["squashed"] for a in after.values())
        trials[f"split {share}"] = int(total)
        if not any(worse(before[n], after[n]) for n in before) and total < base_total:
            base_total = total
            kept = ((total, 0, joints, weights, after, int(rows.sum())), split, rows, f"thigh split {share} on {int(rows.sum())} vertices")
    return kept


def hand_parts(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, canon: np.ndarray, edges: np.ndarray) -> Dict[str, Tuple[np.ndarray, List[int]]]:
    """Per side with a forearm and a hand: (the hand's own part, the hand bones). The part is every vertex the hand's most weighted vertex
    reaches over the welded edges with the forearm's middle band (`HAND_CUT` of the forearm, within its length of the bone) cut out, plus
    that band. A side whose part holds more than `HAND_PART_MAX_SHARE` of its shape is joined to the body there and is left out."""

    from . import pdx_motion

    names = list(mesh.bones)
    joints = pdx_motion.rest_joints(mesh)
    positions = mesh.positions
    out: Dict[str, Tuple[np.ndarray, List[int]]] = {}
    for side in ("Left", "Right"):
        forearm, hand = f"{side}ForeArm", f"{side}Hand"
        if forearm not in names or hand not in names:
            continue
        f, h = names.index(forearm), names.index(hand)
        bones = [i for i, name in enumerate(names) if name.startswith(hand)]
        if not (dense[:, bones].sum(axis=1) > 0).any():
            continue
        span = joints[h] - joints[f]
        length2 = float(span @ span)
        if length2 < 1e-12:
            continue
        t = (positions - joints[f]) @ span / length2
        distance = np.linalg.norm(positions - (joints[f] + np.clip(t, 0, 1)[:, None] * span), axis=1)
        band = (t > HAND_CUT[0]) & (t < HAND_CUT[1]) & (distance < math.sqrt(length2))
        cut = np.zeros(len(positions), bool)
        cut[canon[band]] = True
        kept = edges[~cut[edges].any(axis=1)]
        start = int(canon[np.argmax(dense[:, bones].sum(axis=1))])
        reached = _reach(len(positions), kept, start)
        part = reached[canon] | cut[canon]
        shape = mesh.shape == mesh.shape[start]
        if part[shape].sum() > HAND_PART_MAX_SHARE * shape.sum():
            continue
        out[side] = (part, bones)
    return out


def _reach(count: int, edges: np.ndarray, start: int) -> np.ndarray:
    neighbours: List[List[int]] = [[] for _ in range(count)]
    for a, b in edges.tolist():
        neighbours[a].append(b)
        neighbours[b].append(a)
    seen = np.zeros(count, bool)
    seen[start] = True
    stack = [start]
    while stack:
        for nxt in neighbours[stack.pop()]:
            if not seen[nxt]:
                seen[nxt] = True
                stack.append(nxt)
    return seen


def hand_bleed(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, canon: np.ndarray, edges: np.ndarray, at_least: float = 0.0) -> Dict[str, np.ndarray]:
    """Per side: the vertices outside the hand's own part (`hand_parts`) with more than `at_least` of their weight on the hand bones."""

    return {side: ~part & (dense[:, bones].sum(axis=1) > at_least) for side, (part, bones) in hand_parts(mesh, dense, canon, edges).items()}


def unbleed_hands(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, canon: np.ndarray, edges: np.ndarray,
                  locked_bones: Sequence[str] = ()) -> Tuple[np.ndarray, int]:
    """(dense weights, vertices changed): the hand bones' weight on vertices outside the hand's own part goes to each vertex's other
    bones, in proportion. Tripo's rig gives the skin a resting hand lies against part of the hand's weight: the orc's cloak at the right
    hip held 44% of the axe hand's weight and rose with it by a quarter of the height in the attack (a fresh review: the cloak dragged
    up the right flank, a stiff fin at the hip). A vertex with no other bone, or on a locked bone, keeps its weights."""

    out = dense.copy()
    names = set(locked_bones)
    locked = dense[:, [i for i, name in enumerate(mesh.bones) if name in names]].sum(axis=1) > 0 if names else np.zeros(len(dense), bool)
    changed = np.zeros(len(dense), bool)
    for part, bones in hand_parts(mesh, dense, canon, edges).values():
        on_hand = dense[:, bones].sum(axis=1)
        other = dense.sum(axis=1) - on_hand
        fix = ~part & (on_hand > 0) & (other > 1e-6) & ~locked
        if not fix.any():
            continue
        out[np.ix_(fix, bones)] = 0.0
        out[fix] *= (dense[fix].sum(axis=1) / out[fix].sum(axis=1))[:, None]
        changed |= fix
    return out, int(changed.sum())


def split_thighs(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, locked: np.ndarray, share: float) -> Optional[np.ndarray]:
    """The dense weights with the thigh split moved (`SPLIT_SHARES`), or None when the unit has not two legs hanging from one bone or no
    unlocked vertex is weighted to both thighs."""

    from . import pdx_motion

    legs = pdx_motion.find_legs(mesh)
    if not legs.biped or legs.pelvis < 0:
        return None
    left, right = legs.legs[0].hip, legs.legs[1].hip
    both = np.minimum(dense[:, left], dense[:, right])
    zone = (both > SPLIT_MIN) & ~locked
    if not zone.any():
        return None
    moved = np.where(zone, share * both, 0.0)
    out = dense.copy()
    out[:, left] -= moved
    out[:, right] -= moved
    out[:, legs.pelvis] += 2 * moved
    return out


def locked_vertices(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, canon: np.ndarray, locked_bones: Sequence[str],
                    locked_prefixes: Sequence[str]) -> np.ndarray:
    """Vertices with any weight on a locked bone, or with weight on a locked prefix's bones (at least `PREFIX_LOCK_SHARES[prefix]` of it);
    a welded point is locked when any of its copies is."""

    names = set(locked_bones)
    index = [i for i, name in enumerate(mesh.bones) if name in names]
    locked = dense[:, index].sum(axis=1) > 0 if index else np.zeros(len(dense), bool)
    for prefix in locked_prefixes:
        prefixed = [i for i, name in enumerate(mesh.bones) if name.startswith(prefix)]
        if prefixed:
            locked = locked | (dense[:, prefixed].sum(axis=1) >= PREFIX_LOCK_SHARES.get(prefix, 1e-9))
    np.logical_or.at(locked, canon, locked.copy())
    return locked[canon]


def smoothed_rows(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, canon: np.ndarray, edges: np.ndarray, region: np.ndarray,
                  passes: int, base_joints: Optional[np.ndarray] = None,
                  base_weights: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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
    base_joints = mesh.joints if base_joints is None else base_joints
    base_weights = mesh.weights if base_weights is None else base_weights
    return np.where(changed[:, None], joints, base_joints), np.where(changed[:, None], weights, base_weights), changed


def worse(before: Dict[str, float], after: Dict[str, float]) -> bool:
    """A clip is worse when its worst-frame stretched or squashed count rises by more than `WORSEN_SHARE`, or one edge grows further."""

    return (after["stretched"] > before["stretched"] * (1 + WORSEN_SHARE) + 1
            or after["squashed"] > before["squashed"] * (1 + WORSEN_SHARE) + 1
            or after["worst"] > max(before["worst"], 0.0) * (1 + WORSEN_SHARE) + 1e-6)
