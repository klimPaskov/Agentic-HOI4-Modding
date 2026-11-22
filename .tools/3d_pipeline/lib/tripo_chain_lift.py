"""A death's wings never hold the body up: they are lifted off the ground instead (TRIPO-DEATH-HOVER, TRIPO-CHAIN-GROUND).

No Blender: everything reads and writes the exported `.mesh` and `.anim` with `pdx_deform`, as the game does.

A winged body's chain bones (`lib/tripo_chains.py`) carry wide membranes. In a death the chain stage sags them flat beside the body, and
while the torso kneels it lifts them above the knees, so their lowest chain reaches down past the knees to the ground. The death's own
settles then treated the wing like the rest of the body: the free fall (`lib/tripo_fall.py`) lowers the hips only as far as the lowest skin
outside the legs lets it, and the ground pass lifts the body until its lowest point meets the ground. On the round 4 demon (tripo-wings
full2, 2026-11-18) the lowest skin outside the legs in the kneel (frames 78 to 90) was the tips of both wings' lowest chains (WingL1_3,
WingR1_3), 0.0% to 0.9% of the height above the ground, while the knees and feet hung 19% up: two fresh reviewers saw a body kneeling on air
(TRIPO-DEATH-HOVER 2.53, limit 2.12).

Rule. In a death the wing chain bones never decide where the body is: the fall, the leg and upper-body settles and the ground pass leave their
skin out (`chain_bones`, passed with the dropped weapon). Then each wing is lifted (`lift_death_chains`): the chains that grow from one
point (a wing's root, `root_groups`) turn together as one rigid fan about that point, about the level axis across the wing's mean direction,
by the smallest angle (in `LIFT_STEP` steps, up to `LIFT_MAX`) that puts all of the wing's skin above the ground plus `LIFT_MARGIN`. The
angle never falls faster than `tripo_trim.SETTLE_MAX_RATE` degrees a frame on either side of a frame that needs it (each frame takes the
largest need of the frames round it less that rate times their distance), so the lift ramps in and out at the settle rate and is never
short of what a frame needs. The root's skin, where the membrane blends into the shoulders, turns with the fan, so the lift is only as
large as the ground demands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

from . import pdx_deform, tripo_pose, tripo_trim
from .pdx_binary import read

LIFT_STEP = 1.0  # degrees between the turns tried
LIFT_MAX = 120.0  # a wing lying under the ground is turned at most this far
LIFT_MARGIN = 0.002  # share of the height the wing's skin is kept above the ground (the ground pass's tolerance)
ROOT_SHARE = 0.02  # chain roots within this share of the height of each other, with one parent, grow from one point


def chain_bones(mesh: pdx_deform.SkinnedMesh) -> List[str]:
    """The wing chain bones of a mesh (`tripo_chains.chain_bones`). A cloak is left to the ground pass: on a body lying on its back the cloak
    lies under it, and turning it up would turn it into the body."""

    from . import tripo_chains

    return tripo_chains.chain_bones(mesh.bones, "wings")


def root_groups(mesh: pdx_deform.SkinnedMesh, names: Sequence[str]) -> List[List[int]]:
    """The chain roots (chain bones whose parent is not a chain bone), grouped by parent and by place: each group is one wing's fan."""

    chains = set(names)
    rest = _rest_heads(mesh)
    roots = [i for i, name in enumerate(mesh.bones) if name in chains and (mesh.parents[i] < 0 or mesh.bones[mesh.parents[i]] not in chains)]
    groups: List[List[int]] = []
    for joint in roots:
        for group in groups:
            first = group[0]
            if mesh.parents[first] == mesh.parents[joint] and np.linalg.norm(rest[first] - rest[joint]) <= ROOT_SHARE * mesh.height:
                group.append(joint)
                break
        else:
            groups.append([joint])
    return groups


def _rest_heads(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    from . import pdx_motion

    return pdx_motion.rest_joints(mesh)


def ramped_need(need: np.ndarray, rate: float = tripo_trim.SETTLE_MAX_RATE) -> np.ndarray:
    """Per frame, the largest `need` of any frame less `rate` times the distance to it: never below a frame's own need, never changing faster
    than `rate` a frame."""

    need = np.asarray(need, float)
    frames = np.arange(len(need))
    out = np.zeros(len(need))
    for frame in np.nonzero(need > 0)[0]:
        out = np.maximum(out, need[frame] - rate * np.abs(frames - frame))
    return out


def smallest_lift(points: np.ndarray, pivot: np.ndarray, axis: np.ndarray, floor: float, step: float = LIFT_STEP, limit: float = LIFT_MAX) -> float:
    """The smallest turn (degrees, a multiple of `step`) about `axis` through `pivot` that brings every point to `floor` or above. `limit`
    when none does."""

    if float(points[:, 1].min()) >= floor:
        return 0.0
    for degrees in np.arange(step, limit + step / 2, step):
        turned = pivot + (points - pivot) @ tripo_pose._axis_angle(axis, float(degrees)).T
        if float(turned[:, 1].min()) >= floor:
            return float(degrees)
    return float(limit)


@dataclass
class ChainLift:
    changed: bool
    note: str = ""
    frames: int = 0
    degrees: Dict[str, float] = field(default_factory=dict)  # wing root group (its first bone): the largest turn
    sunk_before: float = 0.0  # the wings' deepest skin under the ground, share of the height
    sunk_after: float = 0.0


def _sunk(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, mask: np.ndarray, floor: float) -> float:
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return max(0.0, max(floor - float(pdx_deform.skin(mesh, matrices[f])[mask, 1].min()) for f in range(anim.frames))) / max(mesh.height, 1e-6)


def _group_angles(mesh: pdx_deform.SkinnedMesh, matrices: np.ndarray, pivots: np.ndarray, mask: np.ndarray, floor: float) -> Tuple[np.ndarray, np.ndarray]:
    """(angles, axes) per frame for one wing: the ramped smallest lift (`smallest_lift`, `ramped_need`) about the level axis across the wing's
    mean direction from its root (`pivots`, per frame), zero axes where the wing has no level direction."""

    height = max(mesh.height, 1e-6)
    need = np.zeros(len(matrices))
    axes = np.zeros((len(matrices), 3))
    vertical = np.array([0.0, 1.0, 0.0])
    for frame in range(len(matrices)):
        points = pdx_deform.skin(mesh, matrices[frame])[mask]
        axis = np.cross(points.mean(axis=0) - pivots[frame], vertical)
        if np.linalg.norm(axis) < 1e-9 * height:
            axis = np.cross(points[np.argmin(points[:, 1])] - pivots[frame], vertical)
        if np.linalg.norm(axis) < 1e-9 * height:
            continue
        axes[frame] = axis / np.linalg.norm(axis)
        need[frame] = smallest_lift(points, pivots[frame], axes[frame], floor)
    return ramped_need(need), axes


def _turn_roots(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, channels: dict, rotations: np.ndarray, group: Sequence[int],
                angles: np.ndarray, axes: np.ndarray, weights: np.ndarray) -> None:
    """Turn each root of `group` in `channels` by `angles` about `axes` in the world, per frame, marking the frames in `weights`."""

    for joint in group:
        name = mesh.bones[joint]
        if channels[name]["q"] is anim.channels[name]["q"]:
            channels[name]["q"] = channels[name]["q"].copy()
    for frame in np.nonzero((angles > 0) & axes.any(axis=1))[0]:
        turn = tripo_pose._axis_angle(axes[frame], float(angles[frame]))
        for joint in group:
            parent = mesh.parents[joint]
            above = rotations[frame, parent] if parent >= 0 else np.eye(3)
            q = channels[mesh.bones[joint]]["q"]
            new = tripo_pose._quaternion_from_matrix(above.T @ turn @ above @ pdx_deform._quaternion_matrices(q[frame][None])[0])
            q[frame] = new if float(new @ q[frame]) >= 0 else -new
        weights[frame] = 1.0


def lift_death_chains(mesh_path: Path, anim_path: Path, out_path: Path) -> ChainLift:
    """Write `out_path`: `anim_path` with each wing's fan turned up about its root wherever its skin is under the ground (see the module text)."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)

    def unchanged(note: str, sunk: float = 0.0) -> ChainLift:
        Path(out_path).write_bytes(bytes(data))
        return ChainLift(False, note, sunk_before=sunk, sunk_after=sunk)

    names = chain_bones(mesh)
    if not names:
        return unchanged("no chain bones")
    info = read(anim_path).child("info")
    q_keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    ground = float(mesh.positions[:, 1].min())
    dominant = pdx_deform.dominant_bones(mesh)
    all_mask = np.isin(dominant, [i for i, name in enumerate(mesh.bones) if name in set(names)])
    before = _sunk(mesh, anim, all_mask, ground)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    rotations, positions = tripo_pose._world_rotations(mesh, anim)
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    weights = np.zeros(anim.frames)
    turned: Dict[str, float] = {}
    groups = [g for g in root_groups(mesh, names) if all(mesh.bones[j] in q_keyed for j in g)]
    for group in groups:
        mask = np.isin(dominant, sorted({b for j in group for b in tripo_pose._subtree(mesh.parents, j)}))
        if not mask.any():
            continue
        angles, axes = _group_angles(mesh, matrices, positions[:, group].mean(axis=1), mask, ground + LIFT_MARGIN * max(mesh.height, 1e-6))
        if (angles > 0).any():
            _turn_roots(mesh, anim, channels, rotations, group, angles, axes, weights)
            turned[mesh.bones[group[0]]] = round(float(angles.max()), 1)
    if not weights.any():
        return unchanged("no wing skin under the ground, or no wing root with rotation keys", round(before, 4))
    result = pdx_deform.Animation(anim.fps, anim.frames, channels)
    tripo_pose._write_rotations(data, q_keyed, [mesh.bones[j] for g in groups for j in g], result, weights)
    Path(out_path).write_bytes(bytes(data))
    after = _sunk(mesh, pdx_deform.load_anim(out_path), all_mask, ground)
    return ChainLift(True, "", frames=int(weights.sum()), degrees=turned, sunk_before=round(before, 4), sunk_after=round(after, 4))
