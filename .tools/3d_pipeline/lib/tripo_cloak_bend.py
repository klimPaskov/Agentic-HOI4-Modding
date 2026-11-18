"""A hard torso bend that stretches the back skin: the last of the cloak stretch (TRIPO-CLOAK-STRETCH), eased on the exported clips.

The weight smoothing and the weight fit (`lib/stretch_smooth.py`, `lib/weight_fit.py`) lower the deformed edges as far as the unit's own weights
can, and a skin bound to Spine, Spine01 and the hips cannot keep its back edges whole when the clip bends the torso hard at one pose. Measured on
the round-4 ogre's chop (attack, 2026-11-17): frame 66 has the three spine bones turned 71, 85 and 109 degrees, 7.1% of the back's edges stretched
(limit 5%), the earlier run's 6.0%. One more fit round, a fit that also counted the clip's six worst frames, and one that weighted them four
times as much took it only to 6.8% and 7.0%, so the lever is the pose, not the weights. The orc and the zombie never needed it.

The rule, run on the staged clips after the weight fit: a clip whose cloak region (the back skin the check measures, behind the hips and weighted
to the torso, hip and thigh bones) is stretched or squashed in more than `TRIGGER_SHARE` of its edges in any frame has the spine bones (the
`SPINE` names the unit has) turned toward their rest rotations, in each frame by the smallest share of `SHARES` that brings that frame to
`TARGET_SHARE`. The need is spread to the neighbouring frames by a smoothstep (round the loop for a looping role, so the seam stays), so the
spine never turns faster than the settle rule allows. A clip under the trigger is not touched, and a result that does not lower the worst
frame is not kept. Only the spine joints' rotation samples change, so no other clip is affected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, tripo_chains, tripo_pose, tripo_trim
from . import tripo_checks as T
from .pdx_binary import read

CHECK_LIMIT = 0.05  # TRIPO-CLOAK-STRETCH's limit
TRIGGER_SHARE = 0.045
TARGET_SHARE = 0.043
SHARES = np.round(np.arange(0.0, 0.5001, 0.05), 2)
MIN_RAMP_FRAMES = 6
SPINE = ("Spine", "Spine01", "Spine02")
HIP_BONES = ("Hip", "back_mid")  # the check's extra names for a rig's own hips and back


@dataclass
class CloakBend:
    changed: bool
    joints: Tuple[str, ...] = ()
    share: float = 0.0  # the largest share used in any frame
    frames_changed: int = 0
    worst_before: float = 0.0
    worst_after: float = 0.0
    ramp_frames: int = 0
    note: str = ""
    tried: Dict[str, float] = field(default_factory=dict)


def front_direction(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The direction the unit faces (horizontal, y up): from the heels to the toes in the rest pose (`tripo/tripo_checks.front_direction`)."""

    joints = pdx_motion.rest_joints(mesh)
    names = {name: index for index, name in enumerate(mesh.bones)}
    vectors = [joints[names[f"{side}ToeBase"]] - joints[names[f"{side}Foot"]] for side in ("Left", "Right")
               if f"{side}Foot" in names and f"{side}ToeBase" in names]
    if not vectors:
        return np.array([0.0, 0.0, 1.0])
    front = np.mean(vectors, axis=0)
    front[1] = 0.0
    return T.unit(front)


class Region:
    """The cloak region and its edges, as the check finds them, with each frame's stretched or squashed share of those edges."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh):
        names = np.array(mesh.bones)
        dominant = pdx_deform.dominant_bones(mesh)
        dominant_names = np.where(dominant >= 0, names[np.clip(dominant, 0, None)], "")
        index = {name: i for i, name in enumerate(mesh.bones)}
        hips = pdx_motion.rest_joints(mesh)[index["Hips"]] if "Hips" in index else mesh.positions.mean(axis=0)
        bones = tuple(tripo_chains.CLOAK_BONES) + HIP_BONES + tuple(tripo_chains.chain_bones(mesh.bones, "cloak"))
        self.mesh, self.height = mesh, mesh.height
        mask = T.cloak_region(mesh.positions, dominant_names, hips, front_direction(mesh), self.height, bones)
        edges = pdx_deform.mesh_edges(mesh)
        self.edges = edges[mask[edges[:, 0]] & mask[edges[:, 1]]]
        self.rest = np.linalg.norm(mesh.positions[self.edges[:, 0]] - mesh.positions[self.edges[:, 1]], axis=1)

    def shares(self, anim: pdx_deform.Animation) -> np.ndarray:
        """(frames,) the share of the region's edges stretched past 1.5 or squashed under 0.5 of their rest length by more than 0.5% of the height."""

        if not len(self.edges):
            return np.zeros(anim.frames)
        usable = self.rest > 1e-9
        matrices = pdx_deform.skinning_matrices(self.mesh, anim)
        out = np.zeros(matrices.shape[0])
        for frame in range(matrices.shape[0]):
            posed = pdx_deform.skin(self.mesh, matrices[frame])
            length = np.linalg.norm(posed[self.edges[:, 0]] - posed[self.edges[:, 1]], axis=1)
            ratio = np.where(usable, length / np.where(usable, self.rest, 1.0), 1.0)
            change = np.abs(length - self.rest) / max(self.height, 1e-9)
            out[frame] = float((((ratio > 1.5) | (ratio < 0.5)) & (change > 0.005)).mean())
        return out


def spread(needed: np.ndarray, ramp: int, loop: bool) -> np.ndarray:
    """Per frame shares that cover `needed`, each need spread to its neighbours by a smoothstep falling to 0 over `ramp` frames (round the clip's
    end for a loop, so the first and last frame get the same share)."""

    frames = len(needed)
    out = needed.copy()
    ramp = max(int(ramp), 1)
    for frame in np.nonzero(needed > 0)[0]:
        distance = np.abs(np.arange(frames) - frame)
        if loop:
            distance = np.minimum(distance, frames - distance)
        t = np.clip(1.0 - distance / ramp, 0.0, 1.0)
        out = np.maximum(out, needed[frame] * t * t * (3.0 - 2.0 * t))
    return out


def ease_cloak_bend(mesh_path: Path, anim_path: Path, out_path: Path, role: str, trigger: float = TRIGGER_SHARE,
                    target: float = TARGET_SHARE) -> CloakBend:
    """Write `out_path`: `anim_path` with the spine turned toward rest where the back skin is stretched past `trigger`. Copied as it is otherwise."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    region = Region(mesh)
    before = region.shares(anim)
    worst = float(before.max()) if len(before) else 0.0
    if worst <= trigger:
        Path(out_path).write_bytes(bytes(data))
        return CloakBend(False, worst_before=worst, worst_after=worst, note="the cloak region is under the trigger")
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    joints = [name for name in SPINE if name in mesh.bones and name in keyed]
    if not joints:
        Path(out_path).write_bytes(bytes(data))
        return CloakBend(False, worst_before=worst, worst_after=worst, note="no spine bones keyed")
    bind = pdx_deform._bind_locals(mesh)
    rest = {mesh.bones[i]: tripo_pose._quaternion_from_matrix(bind[i]) for i in range(len(mesh.bones))}
    stack = np.stack([region.shares(tripo_pose._turned_toward_rest(anim, joints, rest, float(s), np.ones(anim.frames))) for s in SHARES])
    reached = stack <= target + 1e-9
    needed = np.where(reached.any(axis=0), SHARES[np.argmax(reached, axis=0)], SHARES[np.argmin(stack, axis=0)])
    needed = np.where(before <= target, 0.0, needed)
    tried = {str(s): round(float(stack[i].max()), 4) for i, s in enumerate(SHARES)}
    turn = max(tripo_pose.turn_to_target_degrees(anim.channels[j]["q"], rest[j]) for j in joints)
    loop = role in tripo_pose.LOOP_ROLES
    ramp = max(tripo_trim.settle_frames(turn * float(needed.max())), MIN_RAMP_FRAMES)
    weights = spread(needed, ramp, loop)
    result = tripo_pose._turned_toward_rest(anim, joints, rest, 1.0, weights)
    after = float(region.shares(result).max())
    if after >= worst - 1e-4:
        Path(out_path).write_bytes(bytes(data))
        return CloakBend(False, worst_before=worst, worst_after=worst, note="easing the spine does not lower the worst frame", tried=tried)
    tripo_pose._write_rotations(data, keyed, joints, result, weights)
    Path(out_path).write_bytes(bytes(data))
    return CloakBend(True, tuple(joints), round(float(weights.max()), 3), int((weights > 0).sum()), worst, after, int(ramp), tried=tried)
