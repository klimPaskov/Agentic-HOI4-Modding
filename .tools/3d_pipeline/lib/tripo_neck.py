"""The visible neck of a Tripo humanoid: the head's base above the shoulder line, its check (TRIPO-NECK-SUNK) and the lift that fixes it.

Reviewers failed the round 4 zombie (zombie_g, 2026-11-16) for shoulders pulled up to the ears, the head sunk between them with no neck and the
upper back swollen into a hump, in the attack (clearest frames 45 to 53) and the death (frames 63 to 67). Measured on its exported clips:

- The `neck` bone pitches 45 to 51 degrees from the rest pose through the whole attack (the idle 1 degree) and 65 to 76 in the death's frames
  61 to 70. In the chest's own frame (the bone the shoulders and the neck hang from, so a torso that leans forward does not count) the head's
  base drops 0.021 to 0.038 of the height in the attack and up to 0.066 in the death.
- The shoulder line (the two upper-arm joints) rises at most 0.011 of the height against the rest pose in the attack and stays level in the
  death's worst frames. The top of the shoulder skin next to the neck rises 0.001. The arm-level rule (`lib/tripo_arms.py`) turns the upper arms
  down 21.5 degrees (the hands were over the head), so it eases the deltoid, it does not bunch it.

So the sunk head is the neck's pitch, not a shrug and not the weights over the trapezius. The red stretch over the shoulder blade is the other
thing the reviewers saw: the upper arms held above horizontal (100 to 106 degrees from hanging) pull the back skin weighted to them and to
Spine01. With the same weights, turning the neck leaves it as it is. It is the weights' and the stretch rules' business (`lib/stretch_smooth.py`,
`lib/weight_fit.py`), which run after the lift and fit the lifted clip.

The measure (`visible_neck`): per frame, the head joint's height above the midpoint of the two upper-arm joints along the chest's up axis, in the
chest's frame, as a share of the same at rest. 1 is the rest pose's neck, 0 the head's base level with the shoulder joints.

Vanilla (GER infantry clips on GER_infantry, GER_infantry_alt_0, ENG_infantry and GER_infantry_snow, the same on all four, 2026-11-16): vanilla's head
hangs from the chest with no neck bone, so only a shrug shortens its neck. Worst per role: attack 0.790 (attack_stand_rifle frame 1 and
charge_rifle_shoot frame 15, the rifle shouldered), idle 0.88 (long_idle03), move, retreat and death 1.00. Vanilla has no defend. The limit is
vanilla's worst role clip with a quarter added to its shrink, 1 - 1.25 x 0.21 = 0.74 (`NECK_LIMIT`), for every role: a per-role limit would
leave no room at all in a death or a walk, whose vanilla clips cannot move the head. The zombie measured 0.59 in the attack and 0.42 in the death,
the round 4 orc (orc_j) 0.83 and 0.78 at its lowest (attack, defend).

The lift (`lift_neck`, run by `run_pilot` on the staged clips before the weights are smoothed): a clip under the limit has one group of joints
turned toward the rest pose, by the smallest share that brings every frame to vanilla's worst (`NECK_TARGET`). Three groups are tried: the
joints between the chest and the head (the neck), the joints between the chest and the upper arms (the clavicles), and both (`lift_groups`).
Of those that reach the target the one whose joints turn least wins (`added_turn`), a tie going to the part the measurement blames at the worst
frame (the head's drop or the shoulders' rise). If none reaches it, the one that lifts the head furthest. On the zombie the neck alone at half its
turn brings the attack to 0.80 and the death to 0.79. A looping role
gets one share for the whole clip, so its seam stays as it was. A death gets each frame's own share, spread over a smoothstep ramp so the joints
turn no faster than `lib/tripo_trim.SETTLE_MAX_RATE`. Only that group's rotation samples change.

Maths on the exported `.mesh` and `.anim` (`pdx_deform`), no Blender.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, tripo_pose, tripo_trim
from .pdx_binary import read

VANILLA_NECK_WORST = 0.79
VANILLA_NECK_WORST_BY_ROLE = {"attack": 0.79, "defend": 0.79, "idle": 0.88, "move": 1.0, "retreat": 1.0, "death": 1.0}
NECK_LIMIT = round(1.0 - 1.25 * (1.0 - VANILLA_NECK_WORST), 2)
NECK_TARGET = VANILLA_NECK_WORST
SHARES = np.round(np.arange(0.0, 1.0001, 0.05), 2)
LIFT_MIN_RAMP_FRAMES = 6
HEAD_WORDS = ("head",)
HEAD_EXCLUDE = ("end", "top", "node", "nub")


@dataclass
class NeckRig:
    chest: int
    head: int
    left_arm: int
    right_arm: int
    neck: Tuple[int, ...]
    clavicles: Tuple[int, ...]


def _ancestors(parents: Sequence[int], joint: int) -> List[int]:
    out = []
    while joint >= 0:
        out.append(joint)
        joint = parents[joint]
    return out


def head_joint(mesh: pdx_deform.SkinnedMesh) -> int:
    """The head bone: named `head` (Tripo's Head, vanilla's head), else the first bone with `head` in its name that is not an end or a helper."""

    names = [name.lower() for name in mesh.bones]
    exact = [i for i, name in enumerate(names) if name.split(":")[-1] == "head"]
    if exact:
        return exact[0]
    return next((i for i, name in enumerate(names) if any(w in name for w in HEAD_WORDS) and not any(e in name for e in HEAD_EXCLUDE)), -1)


def neck_rig(mesh: pdx_deform.SkinnedMesh) -> Optional[NeckRig]:
    """The chest (the nearest joint the head and both upper arms hang from), the head, the upper arms, and the joints between the chest and
    the head (the neck) and between the chest and each upper arm (the clavicles). None without a head and two upper arms under one chest."""

    left, right = tripo_pose.shoulder_joints(mesh)
    head = head_joint(mesh)
    if min(left, right, head) < 0:
        return None
    up_head, up_left, up_right = (_ancestors(mesh.parents, j) for j in (head, left, right))
    chest = next((j for j in up_head[1:] if j in up_left[1:] and j in up_right[1:]), -1)
    if chest < 0:
        return None
    neck = tuple(up_head[1:up_head.index(chest)])
    clavicles = tuple(up_left[1:up_left.index(chest)]) + tuple(up_right[1:up_right.index(chest)])
    return NeckRig(chest, head, left, right, neck, clavicles)


def _world(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> np.ndarray:
    """(F, B, 4, 4) world matrices of every joint."""

    return pdx_deform.skinning_matrices(mesh, anim) @ np.linalg.pinv(mesh.inverse_bind)[None]


@dataclass
class NeckParts:
    ratio: np.ndarray  # per frame, the visible neck as a share of the rest pose's
    head_drop: np.ndarray  # per frame, how far the head's base fell in the chest's frame (share of height, positive down)
    shoulder_rise: np.ndarray  # per frame, how far the shoulder line rose in the chest's frame (share of height)


def neck_parts(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, rig: Optional[NeckRig] = None) -> Optional[NeckParts]:
    """The visible neck per frame and its two parts. None for a body without a neck rig or with the head not above the shoulders at rest."""

    rig = rig or neck_rig(mesh)
    if rig is None:
        return None
    bind = np.linalg.pinv(mesh.inverse_bind)
    to_chest = np.linalg.pinv(bind[rig.chest])
    up = to_chest[:3, :3] @ np.array([0.0, 1.0, 0.0])
    up = up / max(float(np.linalg.norm(up)), 1e-12)

    def heights(chest_matrix: np.ndarray, joints: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        inverse = np.linalg.pinv(chest_matrix)
        local = joints @ inverse[..., :3, :3].swapaxes(-1, -2) + inverse[..., None, :3, 3]
        along = local @ up
        return along[..., 0], 0.5 * (along[..., 1] + along[..., 2])

    rest_head, rest_line = heights(bind[rig.chest], bind[[rig.head, rig.left_arm, rig.right_arm]][:, :3, 3])
    rest_gap = float(rest_head - rest_line)
    if rest_gap <= 1e-6 * max(mesh.height, 1e-6):
        return None
    world = _world(mesh, anim)
    joints = world[:, [rig.head, rig.left_arm, rig.right_arm]][..., :3, 3]
    head, line = heights(world[:, rig.chest], joints)
    height = max(mesh.height, 1e-6)
    return NeckParts((head - line) / rest_gap, (float(rest_head) - head) / height, (line - float(rest_line)) / height)


def visible_neck(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, rig: Optional[NeckRig] = None) -> Optional[np.ndarray]:
    """Per frame, the head's base above the shoulder line in the chest's frame, as a share of the rest pose's (`neck_parts`)."""

    parts = neck_parts(mesh, anim, rig)
    return None if parts is None else parts.ratio


# ---- the check ---------------------------------------------------------------------------------------------------------

def neck_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    """TRIPO-NECK-SUNK over a unit's clips (`anims`: clip stem to Animation). Records each clip's lowest visible neck and its frame."""

    rig = neck_rig(mesh)
    out: List[dict] = []
    numbers: dict = {}
    if rig is None:
        return out, {"note": "no head and two upper arms under one chest"}
    for clip, anim in anims.items():
        parts = neck_parts(mesh, anim, rig)
        if parts is None or not len(parts.ratio):
            continue
        frame = int(np.argmin(parts.ratio))
        lowest = float(parts.ratio[frame])
        under = int(np.sum(parts.ratio < NECK_LIMIT))
        numbers[clip] = {"lowest_neck_share": round(lowest, 3), "frame": frame, "frames_under_limit": under,
                         "head_drop_share": round(float(parts.head_drop[frame]), 4), "shoulder_rise_share": round(float(parts.shoulder_rise[frame]), 4)}
        if lowest < NECK_LIMIT:
            out.append({"rule": "TRIPO-NECK-SUNK", "subject": clip,
                        "message": f"the head's base is {lowest:.0%} of its rest height above the shoulders in frame {frame} (limit {NECK_LIMIT:.0%}, vanilla's worst "
                                   f"{VANILLA_NECK_WORST:.0%}), {under} of {len(parts.ratio)} frames under the limit: the head sinks between the shoulders "
                                   f"(head down {parts.head_drop[frame]:.1%} of the height, shoulders up {parts.shoulder_rise[frame]:.1%})",
                        "share": round(lowest, 3), "frame": frame})
    return out, numbers


# ---- the lift ----------------------------------------------------------------------------------------------------------

@dataclass
class NeckLift:
    changed: bool
    group: str = ""
    joints: Tuple[str, ...] = ()
    share: float = 0.0  # the largest share used in any frame
    frames_changed: int = 0
    ramp_frames: int = 0
    neck_before: float = 1.0
    neck_after: float = 1.0
    note: str = ""
    tried: Dict[str, dict] = field(default_factory=dict)


def lift_groups(parts: NeckParts, rig: NeckRig) -> List[Tuple[str, Tuple[int, ...]]]:
    """The joint groups to try, in order: the larger part of the shrink at the worst frame first, then the other, then both."""

    frame = int(np.argmin(parts.ratio))
    groups = [("neck", rig.neck), ("clavicles", rig.clavicles)]
    if parts.shoulder_rise[frame] > parts.head_drop[frame]:
        groups.reverse()
    groups.append(("neck and clavicles", rig.neck + rig.clavicles))
    return [(name, joints) for name, joints in groups if joints]


def needed_shares(ratios: np.ndarray, target: float, shares: np.ndarray = SHARES) -> np.ndarray:
    """Per frame, the smallest share whose ratio reaches `target` (`ratios` is shares x frames), inf where none does."""

    reached = ratios >= target - 1e-9
    first = np.argmax(reached, axis=0)
    return np.where(reached.any(axis=0), shares[first], np.inf)


def spread_shares(needed: np.ndarray, ramp: int, loop: bool) -> np.ndarray:
    """Per frame shares that cover `needed` everywhere. A loop gets its largest share in every frame (the seam stays). Otherwise each frame's
    need is spread to its neighbours with a smoothstep falling to 0 over `ramp` frames, so the share never changes faster than 1.5/ramp a frame."""

    needed = np.where(np.isfinite(needed), needed, 1.0)
    if loop:
        return np.full(len(needed), float(needed.max()))
    frames = len(needed)
    out = needed.copy()
    ramp = max(int(ramp), 1)
    for frame in np.nonzero(needed > 0)[0]:
        distance = np.abs(np.arange(frames) - frame) / ramp
        t = np.clip(1.0 - distance, 0.0, 1.0)
        out = np.maximum(out, needed[frame] * t * t * (3.0 - 2.0 * t))
    return out


def added_turn(before: pdx_deform.Animation, after: pdx_deform.Animation, joints: Sequence[str]) -> float:
    """How much a lift changes the pose: over the joints, the sum of each joint's largest turn (degrees) between the two clips in any frame."""

    return float(sum(max(tripo_pose.quaternion_turn(a, b) for a, b in zip(before.channels[j]["q"], after.channels[j]["q"])) for j in joints))


def _turned(anim: pdx_deform.Animation, joints: Sequence[str], rest: dict, weights: np.ndarray) -> pdx_deform.Animation:
    return tripo_pose._turned_toward_rest(anim, joints, rest, 1.0, np.asarray(weights, float))


def lift_neck(mesh_path: Path, anim_path: Path, out_path: Path, role: str, limit: float = NECK_LIMIT, target: float = NECK_TARGET) -> NeckLift:
    """Write `out_path`: `anim_path` with the neck or the clavicles turned toward the rest pose where the visible neck is under `limit`
    (see the module text). Unchanged, and copied as it is, when the clip passes or no group lifts it."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    rig = neck_rig(mesh)
    parts = neck_parts(mesh, anim, rig) if rig else None
    if parts is None or not len(parts.ratio):
        Path(out_path).write_bytes(bytes(data))
        return NeckLift(False, note="no neck rig")
    before = float(parts.ratio.min())
    if before >= limit:
        Path(out_path).write_bytes(bytes(data))
        return NeckLift(False, neck_before=before, neck_after=before, note="the neck is above the limit")
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    bind = pdx_deform._bind_locals(mesh)
    rest = {mesh.bones[i]: tripo_pose._quaternion_from_matrix(bind[i]) for i in range(len(mesh.bones))}
    loop = role in tripo_pose.LOOP_ROLES
    plans = []
    tried: Dict[str, dict] = {}
    for order, (name, group) in enumerate(lift_groups(parts, rig)):
        joints = [mesh.bones[j] for j in group if mesh.bones[j] in keyed]
        if not joints:
            continue
        ratios = np.stack([visible_neck(mesh, _turned(anim, joints, rest, np.full(anim.frames, s)), rig) for s in SHARES])
        needed = needed_shares(ratios, target)
        turn = max(tripo_pose.quaternion_turn(q, rest[j]) for j in joints for q in anim.channels[j]["q"])
        largest = float(np.where(np.isfinite(needed), needed, 1.0).max())
        ramp = 0 if loop else max(tripo_trim.settle_frames(turn * largest), LIFT_MIN_RAMP_FRAMES)
        weights = spread_shares(needed, ramp, loop)
        result = _turned(anim, joints, rest, weights)
        after = float(visible_neck(mesh, result, rig).min())
        added = added_turn(anim, result, joints)
        reached = bool(np.all(np.isfinite(needed)))
        tried[name] = {"neck_after": round(after, 3), "turn_added_degrees": round(added, 1), "reaches_target": reached}
        plans.append((not reached, added if reached else -after, order, after, name, joints, weights, result, ramp))
    # A group that reaches the target everywhere beats one that does not. Of those that do, the smallest added turn wins, of those that do
    # not the highest neck. A tie goes to the group the measurement blames.
    chosen = min(plans, key=lambda plan: plan[:3]) if plans else None
    if chosen is None or chosen[3] <= before + 1e-6:
        Path(out_path).write_bytes(bytes(data))
        return NeckLift(False, neck_before=before, neck_after=before, note="turning the neck or the clavicles toward rest does not lift the head", tried=tried)
    _, _, _, after, name, joints, weights, result, ramp = chosen
    tripo_pose._write_rotations(data, keyed, joints, result, weights)
    Path(out_path).write_bytes(bytes(data))
    return NeckLift(True, name, tuple(joints), round(float(weights.max()), 3), int(np.sum(weights > 0)), int(ramp), before, after, tried=tried)
