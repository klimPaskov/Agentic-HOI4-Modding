"""Fit a Tripo unit's skin weights to its own clips, without Blender (the weight fit, after the `stretch` smoothing).

Tripo's automatic weights carry bones a vertex should not follow, and the smoothing (`lib/stretch_smooth.py`) only blends what is there.
Two fresh reviews still failed the zombie and the orc on skin: the chest and armpits stretched under raised arms, a hump rose on the upper
back in a crouch, the kneeling thighs were crushed, and on the orc the free forearm bent like a hose with no elbow (its upper arm and
forearm held 30% to 90% of the upper spine's weight, the blend ring of the chest and shoulder plates). This rule reads the exported
`.mesh` and every `.anim` of the unit, as the game plays them, and solves for the weights that keep the edges' lengths in those clips:

1. Region: the vertices of every edge the kit's measure (UNIT-ANIM-STRETCH, `lib/pdx_deform`: 1.5 times and 0.5% of the height) counts
   as stretched or squashed in some frame of some clip, grown `RINGS` edge rings. Locked vertices never change: weight on a locked bone
   (a held weapon), on a chain prefix (`stretch_smooth.locked_vertices`), or a vertex in `locked_mask` (the plates rule's armour plates).
2. Candidates: each region vertex may take the `CANDIDATES` bones most weighted within two edge rings of it, of its own shape's skeleton.
   A locked bone it does not already hold is never added.
3. Fit: `FRAMES_PER_CLIP` evenly spaced frames of every clip. The penalty is the squared log strain of every edge the region touches,
   beyond `TOLERANCE` (an edge may change its length by 10% at no cost), summed over the frames. `ITERATIONS` steps of projected gradient
   descent (Adam, `RATE`), each row kept on the simplex of its candidates, with a pull of `PULL` toward the starting weights and a
   smoothness term `SMOOTH` over the region's edges. Vertices outside the region keep their weights and anchor the fit.
4. Choice: the fitted weights are blended in at each of `STEPS`, cut to `MAX_INFLUENCES` and normalised, and measured on every frame of
   every clip by `stretch_smooth`'s rescoring. The kept step lowers the deformed edges most, provided no clip gets worse by the kit's rule
   (`stretch_smooth.worse`: a worst-frame stretched or squashed count up by more than 2%, or any edge growing further than before). When
   no step helps, nothing changes.

Measured offline in November 2026 on the round-4 zombie (unarmed) and orc (axe, cloak chains, plates), on their exported files after
the smoothing, every frame of every clip, each count summed over the clips' worst frames. Deformed edges by the kit's measure (stretched
plus squashed): zombie 2385 to 1619 (step 0.5), orc 7199 to 4536 (step 1.0). In the regions the reviewers named, the kit's count and
then the count of edges changed by 1.3 times or more (their sheets' colour):

    region                     zombie                     orc
    chest under the arms       517 / 1729 to 394 / 1455   254 / 521 to 40 / 243
    upper back                 277 / 857 to 182 / 651     246 / 865 to 114 / 523
    forearm and elbow          149 / 760 to 84 / 573      1100 / 2285 to 209 / 924
    thighs and kilt            1078 / 3976 to 725 / 3126  667 / 1838 to 230 / 865
    waist                      325 / 1402 to 204 / 1015   13 / 26 to 3 / 8

No clip got worse, the weapon, cloak and plate vertices kept their rows, the plates still stretch 0%, and after the stage's per-frame
grounding both units pass every Tripo check (the orc's TRIPO-CLOAK-STRETCH in the defend fell from 5.1% to 4.8%). The rule took 90 s on
the zombie (6435 region vertices) and 60 s on the orc (4692). Tried on the same files and dropped, each making every clip or most clips
worse: bone-heat weights (a Laplacian solve with each bone segment as the source of its nearest vertices) blended in where the clips
stretch or everywhere (orc at half strength 7199 to 9300, the chest under the arms 254 to 1319, though the forearm fell to 345), the
foreign bones removed from each limb past its root (a worst edge grew from 2.5% to 23% of the height on the zombie), and the joint
bands, each joint's two bones re-split over a band of 0.5 to 2 limb radii (zombie 2385 to 2545 at 2 radii, orc 7199 to 7452 at 1).

Only the `ix`, `w` and `bones` values of the `skin` blocks change, in place, so every clip still plays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Sequence

import numpy as np

from . import pdx_deform, stretch_smooth

RINGS = 3
CANDIDATES = 8
FRAMES_PER_CLIP = 24
ITERATIONS = 100
RATE = 0.02
TOLERANCE = float(np.log(1.1))
PULL = 0.02
SMOOTH = 0.01
STEPS = (0.25, 0.5, 0.75, 1.0)
# An edge growing past this share of its clip's worst growth before (as a share of the height) is penalised as well, so the longest edge
# of a clip does not grow further (the kit's rule keeps a step only when no edge grows past the clip's worst).
CAP_SHARE = 0.9
GROWTH_WEIGHT = 1.0
# From this share of the iterations on, each row keeps only its `MAX_INFLUENCES` largest candidates, so cutting to four changes nothing.
SPARSE_FROM = 0.6
# Guard: an edge the fit makes grow past its clip's worst growth before, or newly deformed in a clip whose count rose, gets the weights its
# two vertices (and one ring around them) had before. At most this many rounds per step.
GUARD_ROUNDS = 6
# Repeated fits (`fit_rounds`): one fit leaves the strain it could not remove in one go, and its best step is often the full one, so a second
# fit from the fitted weights goes on. The round-4 ogre's attack kept 6.5% of its back's edges stretched at frame 40 (limit 5%, TRIPO-CLOAK-STRETCH)
# after one fit (2185 deformed edges of 5382); two more rounds took the unit to 1688 and 1501 (attack 6.5% to 3.9%, no clip's cloak share higher,
# every clip's deformed count lower). A round must lower the total by `ROUND_GAIN` for another to start, at most `MAX_ROUNDS` in all; every round
# keeps the rule's own guard (no clip worse), so a round that helps nothing changes nothing.
MAX_ROUNDS = 3
ROUND_GAIN = 0.10
MAX_INFLUENCES = stretch_smooth.MAX_INFLUENCES


@dataclass
class FitResult:
    changed: bool
    step: float = 0.0
    region: int = 0
    vertices_changed: int = 0
    before: Dict[str, Dict[str, float]] = field(default_factory=dict)
    after: Dict[str, Dict[str, float]] = field(default_factory=dict)
    trials: Dict[str, int] = field(default_factory=dict)  # deformed edges by step
    note: str = ""
    rounds: int = 1  # the fits that were kept (`fit_rounds`)
    round_totals: Sequence[int] = ()  # deformed edges before the first round and after each kept one


def _project_simplex(values: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Each row projected onto the simplex over its True entries (the others 0)."""

    v = np.where(mask, values, -1e9)
    ordered = -np.sort(-v, axis=1)
    sums = np.cumsum(ordered, axis=1) - 1.0
    index = np.arange(1, v.shape[1] + 1)
    support = ordered - sums / index > 0
    last = v.shape[1] - 1 - np.argmax(support[:, ::-1], axis=1)
    theta = sums[np.arange(len(v)), last] / (last + 1)
    return np.where(mask, np.maximum(v - theta[:, None], 0.0), 0.0)


def _ring_mean(dense: np.ndarray, edges: np.ndarray, rings: int) -> np.ndarray:
    out = dense.copy()
    degree = np.zeros(len(dense))
    np.add.at(degree, edges.ravel(), 1.0)
    for _ in range(rings):
        total = np.zeros_like(out)
        np.add.at(total, edges[:, 0], out[edges[:, 1]])
        np.add.at(total, edges[:, 1], out[edges[:, 0]])
        out = 0.5 * out + 0.5 * total / np.maximum(degree, 1.0)[:, None]
    return out


class _Gather:
    """Sums per-edge rows onto the region's vertices: +row onto an edge's first vertex, -row onto its second (numpy only)."""

    def __init__(self, first: np.ndarray, second: np.ndarray, count: int):
        targets = np.r_[first[first >= 0], second[second >= 0]]
        self.rows = np.r_[np.nonzero(first >= 0)[0], np.nonzero(second >= 0)[0]]
        self.signs = np.r_[np.ones((first >= 0).sum()), -np.ones((second >= 0).sum())].astype(np.float32)
        order = np.argsort(targets, kind="stable")
        self.rows, self.signs, targets = self.rows[order], self.signs[order], targets[order]
        self.targets, self.starts = np.unique(targets, return_index=True)
        self.count = count

    def __call__(self, values: np.ndarray) -> np.ndarray:
        out = np.zeros((self.count,) + values.shape[1:], np.float32)
        if len(self.rows):
            signed = values[self.rows] * self.signs.reshape((-1,) + (1,) * (values.ndim - 1))
            out[self.targets] = np.add.reduceat(signed, self.starts, axis=0)
        return out


def _candidates(dense: np.ndarray, edges: np.ndarray, rows: np.ndarray, allowed: Optional[np.ndarray]):
    """(order, usable, start): per region row the `CANDIDATES` bone indices, which of them may hold weight, and its normalised weights."""

    candidate = dense > 0
    for _ in range(2):
        near = np.zeros_like(candidate)
        np.logical_or.at(near, edges[:, 0], candidate[edges[:, 1]])
        np.logical_or.at(near, edges[:, 1], candidate[edges[:, 0]])
        candidate |= near
    if allowed is not None:
        candidate &= allowed | (dense > 0)
    score = np.where(candidate, _ring_mean(dense, edges, 2) + 1e-6, -1.0)
    order = np.argsort(-score[rows], axis=1)[:, :min(CANDIDATES, dense.shape[1])]
    usable = np.take_along_axis(score[rows], order, axis=1) > 0
    start = np.take_along_axis(dense[rows], order, axis=1)
    return order, usable, start / np.maximum(start.sum(axis=1, keepdims=True), 1e-12)


class _Problem:
    """The fit's fixed data: the region's edges, each candidate bone's placement of each region vertex in every frame, and the placement
    of the vertices outside the region that anchor it."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, matrices: Sequence[np.ndarray], edges: np.ndarray, rows: np.ndarray,
                 order: np.ndarray, caps: Optional[np.ndarray]):
        positions = mesh.positions
        self.height = max(mesh.height, 1e-6)
        self.caps, self.order, self.bones = caps, order, len(mesh.bones)
        slot = np.full(len(positions), -1)
        slot[rows] = np.arange(len(rows))
        touched = edges[(slot[edges] >= 0).any(axis=1)]
        rest = np.linalg.norm(positions[touched[:, 0]] - positions[touched[:, 1]], axis=1)
        self.touched, self.rest = touched[rest > 1e-9], rest[rest > 1e-9]
        self.first, self.second = slot[self.touched[:, 0]], slot[self.touched[:, 1]]
        self.gather = _Gather(self.first, self.second, len(rows))
        inner = self.touched[(self.first >= 0) & (self.second >= 0)]
        self.inner = (slot[inner[:, 0]], slot[inner[:, 1]])
        self.smooth_gather = _Gather(self.inner[0], self.inner[1], len(rows))
        self.frames = len(matrices)
        self.moved = np.empty((self.frames, len(rows), order.shape[1], 3), np.float32)
        outside = np.unique(self.touched[slot[self.touched] < 0])
        self.fixed = np.zeros((self.frames, len(positions), 3), np.float32)
        for f, frame in enumerate(matrices):
            m = frame[order]
            self.moved[f] = np.einsum("rkij,rj->rki", m[..., :3, :3], positions[rows]) + m[..., :3, 3]
            if len(outside):
                self.fixed[f, outside] = stretch_smooth._skin_subset(positions[outside], mesh.joints[outside], mesh.weights[outside], frame)

    def gradient(self, weights: np.ndarray, start: np.ndarray) -> np.ndarray:
        """The penalty's gradient with respect to the region's candidate weights (step 3 of the rule)."""

        placed = np.einsum("rk,frkc->frc", weights.astype(np.float32), self.moved)
        a = np.where((self.first >= 0)[None, :, None], placed[:, np.clip(self.first, 0, None)], self.fixed[:, self.touched[:, 0]])
        b = np.where((self.second >= 0)[None, :, None], placed[:, np.clip(self.second, 0, None)], self.fixed[:, self.touched[:, 1]])
        span = a - b
        length = np.linalg.norm(span, axis=2) + 1e-12
        strain = np.log(length / self.rest)
        excess = np.maximum(np.abs(strain) - TOLERANCE, 0.0)
        pull = 2.0 * excess * np.sign(strain) / (length * length)
        if self.caps is not None:
            over = np.maximum((length - self.rest) / self.height - self.caps[:, None], 0.0)
            pull += 2.0 * GROWTH_WEIGHT * over / (self.caps[:, None] ** 2) / self.height / length
        per_edge = np.ascontiguousarray((pull[..., None] * span / self.frames).transpose(1, 0, 2))  # (edges, frames, 3)
        grad = np.einsum("rfc,frkc->rk", self.gather(per_edge), self.moved).astype(float)
        grad += 2.0 * PULL * (weights - start)
        full = np.zeros((len(weights), self.bones))  # smoothness over the region's own edges, in the shared bone space
        np.put_along_axis(full, self.order, weights, axis=1)
        return grad + 2.0 * SMOOTH * np.take_along_axis(self.smooth_gather(full[self.inner[0]] - full[self.inner[1]]), self.order, axis=1)


def fit_dense(mesh: pdx_deform.SkinnedMesh, matrices: Sequence[np.ndarray], edges: np.ndarray, region: np.ndarray,
              allowed: Optional[np.ndarray] = None, iterations: int = ITERATIONS, caps: Optional[np.ndarray] = None) -> np.ndarray:
    """(V, B) dense weights with the `region` rows (canonical vertices, the ends of `edges`) fitted to the frames in `matrices` (a list
    of (B, 4, 4) skinning matrices) by step 3 of the rule. `allowed` (V, B) marks the bones each row may take. `caps` (one per frame)
    is the growth, as a share of the height, past which an edge is penalised for growing (`CAP_SHARE` of its clip's worst before)."""

    dense = stretch_smooth.dense_weights(mesh)
    rows = np.nonzero(region)[0]
    if not len(rows) or not len(matrices):
        return dense
    order, usable, start = _candidates(dense, edges, rows, allowed)
    problem = _Problem(mesh, matrices, edges, rows, order, caps)
    weights = start.copy()
    mean, square = np.zeros_like(weights), np.zeros_like(weights)
    for step in range(iterations):
        if step == int(SPARSE_FROM * iterations):
            # the game blends at most four bones: from here each row keeps only its four largest candidates
            rank = np.argsort(np.argsort(-np.where(usable, weights, -1.0), axis=1), axis=1)
            usable = usable & (rank < MAX_INFLUENCES)
            weights = _project_simplex(weights, usable)
            mean, square = np.zeros_like(weights), np.zeros_like(weights)
        grad = problem.gradient(weights, start)
        live = np.maximum(usable.sum(axis=1, keepdims=True), 1)
        grad = np.where(usable, grad - (grad * usable).sum(axis=1, keepdims=True) / live, 0.0)  # moves along the simplex only
        mean = 0.9 * mean + 0.1 * grad
        square = 0.999 * square + 0.001 * grad * grad
        move = RATE * (mean / (1 - 0.9 ** (step + 1))) / (np.sqrt(square / (1 - 0.999 ** (step + 1))) + 1e-8)
        weights = _project_simplex(weights - move, usable)
    out = dense.copy()
    full = np.zeros((len(rows), dense.shape[1]))
    np.put_along_axis(full, order, weights, axis=1)
    out[rows] = np.where(usable.any(axis=1)[:, None], full, dense[rows])
    return out


def sampled_matrices(clips: "stretch_smooth._Clips", before: Dict[str, Dict[str, float]], per_clip: int = FRAMES_PER_CLIP):
    """(frames, caps): `per_clip` evenly spaced frames' skinning matrices of every clip, and each frame's growth cap (`CAP_SHARE` of its
    clip's worst growth before, at least the kit's significant share)."""

    out, caps = [], []
    for name, matrices in clips.matrices.items():
        pick = np.unique(np.linspace(0, matrices.shape[0] - 1, min(per_clip, matrices.shape[0])).round().astype(int))
        out.extend(matrices[pick])
        caps += [max(CAP_SHARE * before[name]["worst"], pdx_deform.SIGNIFICANT_SHARE)] * len(pick)
    return out, np.asarray(caps)


def fit(mesh_path: Path, anim_paths: Sequence[Path], out_path: Path, locked_bones: Sequence[str] = (),
        locked_prefixes: Sequence[str] = (), locked_mask: Optional[np.ndarray] = None, steps: Sequence[float] = STEPS,
        iterations: int = ITERATIONS) -> FitResult:
    """Write `out_path` (the mesh with its weights fitted to `anim_paths` by the rule above) and return what changed. `locked_mask` (V,)
    marks further vertices that keep their weights (the armour plates)."""

    mesh = pdx_deform.load_mesh(mesh_path)
    data = Path(mesh_path).read_bytes()
    if not mesh.skinned or not anim_paths:
        Path(out_path).write_bytes(data)
        return FitResult(False, note="no skin or no clips")
    anims = {Path(p).stem: pdx_deform.load_anim(p) for p in anim_paths}
    canon = pdx_deform.weld(mesh.positions, max(mesh.height, 1e-6) * 1e-5)
    edges = pdx_deform.mesh_edges(mesh)
    clips = stretch_smooth._Clips(mesh, anims, edges)
    before = {name: clips.summary(name) for name in anims}
    dense = stretch_smooth.dense_weights(mesh)
    locked = stretch_smooth.locked_vertices(mesh, dense, canon, locked_bones, locked_prefixes)
    if locked_mask is not None:
        extra = np.asarray(locked_mask, bool).copy()
        np.logical_or.at(extra, canon, extra.copy())
        locked |= extra[canon]
    bad = np.zeros(len(edges), bool)
    for stretched, squashed, _growth in clips.masks.values():
        bad |= (stretched | squashed).any(axis=0)
    seeds = np.zeros(len(dense), bool)
    seeds[edges[bad].ravel()] = True
    is_canon = np.zeros(len(dense), bool)
    is_canon[np.unique(canon)] = True
    free = ~locked & (dense.sum(axis=1) > 0)
    region = stretch_smooth.grow(seeds & free, edges, RINGS) & free & is_canon
    if not region.any():
        Path(out_path).write_bytes(data)
        return FitResult(False, before=before, after=before, note="no clip deforms an edge")
    allowed = _allowed(mesh, dense, locked_bones, locked_prefixes)
    frames, caps = sampled_matrices(clips, before)
    fitted = fit_dense(mesh, frames, edges, region, allowed, iterations, caps)[canon]
    rows = region[canon]
    total_before = sum(b["stretched"] + b["squashed"] for b in before.values())
    best, trials = None, {}
    for share in steps:
        joints, weights, after = _guard(mesh, clips, before, edges, canon, dense, (1.0 - share) * dense + share * fitted, rows)
        changed = np.abs(weights - mesh.weights).sum(axis=1) + (joints != mesh.joints).sum(axis=1) > 1e-6
        total = sum(a["stretched"] + a["squashed"] for a in after.values())
        trials[str(share)] = int(total)
        if not any(stretch_smooth.worse(before[n], after[n]) for n in anims) and total < total_before and (best is None or total < best[0]):
            best = (total, share, joints, weights, after, int(changed.sum()))
    if best is None:
        Path(out_path).write_bytes(data)
        return FitResult(False, region=int(region.sum()), before=before, after=before, trials=trials,
                         note="no step lowered the deformed edges without making a clip worse")
    _total, share, joints, weights, after, count = best
    stretch_smooth.write_weights(mesh_path, out_path, joints, weights, mesh.bones)
    return FitResult(True, share, int(region.sum()), count, before, after, trials)


def _changed_rows(mesh: pdx_deform.SkinnedMesh, joints: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return np.abs(weights - mesh.weights).sum(axis=1) + (joints != mesh.joints).sum(axis=1) > 1e-6


def _frame_masks(clips: "stretch_smooth._Clips", name: str, affected: np.ndarray, joints: np.ndarray, weights: np.ndarray):
    """(stretched, squashed, growth), each (frames, affected edges), of the `affected` edges skinned by the new rows in every frame."""

    pick = clips.edges[affected]
    vertices, local = np.unique(pick, return_inverse=True)
    local = local.reshape(-1, 2)
    out = ([], [], [])
    for matrices in clips.matrices[name]:
        moved = stretch_smooth._skin_subset(clips.mesh.positions[vertices], joints[vertices], weights[vertices], matrices)
        length = np.linalg.norm(moved[local[:, 0]] - moved[local[:, 1]], axis=1)
        for into, values in zip(out, stretch_smooth._deformed(clips.rest[affected], length, clips.height)):
            into.append(values)
    return tuple(np.array(values) for values in out)


def _guard(mesh: pdx_deform.SkinnedMesh, clips: "stretch_smooth._Clips", before: Dict[str, Dict[str, float]], edges: np.ndarray,
           canon: np.ndarray, dense: np.ndarray, target: np.ndarray, rows: np.ndarray):
    """(joints, weights, per-clip summary) of `target` (dense) on `rows` after the guard (`GUARD_ROUNDS`): wherever the new rows make an
    edge grow past its clip's worst growth before, or newly deform in a clip that got worse, its two vertices and one ring around them
    take half as much of the change each round, so the fit fades out there instead of leaving a new hard border."""

    share = rows.astype(float)
    for _round in range(GUARD_ROUNDS + 1):
        joints, weights = stretch_smooth.sparse_rows((1.0 - share[:, None]) * dense + share[:, None] * target, MAX_INFLUENCES)
        keep = share > 0
        joints, weights = np.where(keep[:, None], joints, mesh.joints), np.where(keep[:, None], weights, mesh.weights)
        affected = _changed_rows(mesh, joints, weights)[edges].any(axis=1)
        after = {name: clips.summary(name, affected, joints, weights) for name in before}
        if _round == GUARD_ROUNDS or not affected.any():
            break
        offending = np.zeros(len(edges), bool)
        for name in before:
            stretched, squashed, growth = _frame_masks(clips, name, affected, joints, weights)
            limit = max(before[name]["worst"], 0.0) * (1 + stretch_smooth.WORSEN_SHARE)
            bad = (growth > limit).any(axis=0)
            if stretch_smooth.worse(before[name], after[name]):
                old_s, old_q, _old_g = clips.masks[name]
                bad |= ((stretched & ~old_s[:, affected]) | (squashed & ~old_q[:, affected])).any(axis=0)
            offending[np.nonzero(affected)[0][bad]] = True
        if not offending.any():
            break
        back = np.zeros(len(share), bool)
        back[edges[offending].ravel()] = True
        back = stretch_smooth.grow(back, edges, 1)[canon]
        share = np.where(back, 0.5 * share, share)
        share[share < 0.05] = 0.0
    return joints, weights, after


def _allowed(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, locked_bones: Sequence[str], locked_prefixes: Sequence[str]) -> np.ndarray:
    """(V, B): the bones a row may take, those of its own shape's skeleton that are not locked."""

    names = set(locked_bones)
    blocked = np.array([name in names or any(name.startswith(prefix) for prefix in locked_prefixes) for name in mesh.bones])
    shapes = np.unique(mesh.shape)
    per_shape = {s: dense[mesh.shape == s].sum(axis=0) > 0 for s in shapes}
    return np.stack([per_shape[s] for s in mesh.shape]) & ~blocked[None, :]


def plate_vertices(mesh: pdx_deform.SkinnedMesh) -> Optional[np.ndarray]:
    """(V,) the armour plates found by the plates rule (`tripo_chains.plate_masks`, as TRIPO-PLATE-STRETCH finds them), or None when the
    rig lacks the kit's shoulder, spine or neck bones. A plate is bound whole to one bone, so the fit leaves it alone."""

    from . import pdx_motion, tripo_chains

    index = {name: i for i, name in enumerate(mesh.bones)}
    needed = ("Hips", "Spine01", "Spine02", "neck", "LeftArm", "RightArm", "LeftShoulder", "RightShoulder", "LeftForeArm", "RightForeArm")
    if not all(name in index for name in needed):
        return None
    joints = pdx_motion.rest_joints(mesh)
    heads = {name: joints[i] for name, i in index.items()}
    names = np.array(mesh.bones)
    dominant = names[np.clip(pdx_deform.dominant_bones(mesh), 0, None)]
    torso = np.isin(dominant, ["Hips", "Spine", "Spine01", "Spine02"])
    radius = tripo_chains.capsule_radius(mesh.positions[torso], heads["Hips"], heads["neck"])
    feet = [joints[index[f"{side}ToeBase"]] - joints[index[f"{side}Foot"]] for side in ("Left", "Right")
            if f"{side}ToeBase" in index and f"{side}Foot" in index]
    front = np.mean(feet, axis=0) if feet else np.array([0.0, 0.0, 1.0])
    front[1] = 0.0
    masks = tripo_chains.plate_masks(mesh.positions, heads, tripo_chains.unit(front), np.array([0.0, 1.0, 0.0]), radius)
    out = np.zeros(len(mesh.positions), bool)
    for mask in masks.values():
        out |= mask
    return out


def _total(summary: Dict[str, Dict[str, float]]) -> int:
    return int(sum(clip["stretched"] + clip["squashed"] for clip in summary.values()))


def fit_rounds(mesh_path: Path, anim_paths: Sequence[Path], out_path: Path, locked_bones: Sequence[str] = (),
               locked_prefixes: Sequence[str] = (), locked_mask: Optional[np.ndarray] = None, steps: Sequence[float] = STEPS,
               iterations: int = ITERATIONS, max_rounds: int = MAX_ROUNDS, round_gain: float = ROUND_GAIN) -> FitResult:
    """`fit`, repeated from its own result while a round lowered the deformed edges by at least `round_gain` of what it started with, at most
    `max_rounds` times. The result's `before` is the first round's, its `after`, `step` and `trials` the last kept round's."""

    first = fit(mesh_path, anim_paths, out_path, locked_bones, locked_prefixes, locked_mask, steps, iterations)
    if not first.changed:
        return first
    result, totals = first, [_total(first.before), _total(first.after)]
    while result.rounds < max_rounds and totals[-2] > 0 and (totals[-2] - totals[-1]) / totals[-2] >= round_gain:
        nxt = fit(out_path, anim_paths, out_path, locked_bones, locked_prefixes, locked_mask, steps, iterations)
        if not nxt.changed:
            break
        totals.append(_total(nxt.after))
        result = FitResult(True, nxt.step, nxt.region, result.vertices_changed + nxt.vertices_changed, first.before, nxt.after, nxt.trials,
                           nxt.note, result.rounds + 1, tuple(totals))
    result.round_totals = tuple(totals)
    return result
