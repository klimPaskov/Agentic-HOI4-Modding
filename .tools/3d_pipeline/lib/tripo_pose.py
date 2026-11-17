"""Pose checks and one settle for a Tripo unit's exported clips: the loop seam, the feet on the ground, the legs of a death.

No Blender: everything reads the exported `.mesh` and `.anim` with `pdx_deform`, as the game does.

Rules and where each number comes from (vanilla measured on GER infantry, whose clips every western infantry mesh plays, on GER_infantry_alt_0,
ENG_infantry and GER_infantry_snow, 2026-11-15):

- Loop seam (`loop_seam`, TRIPO-LOOP-POP). HOI4 plays idle, move, attack, defend and retreat in a loop, so the last frame must continue into the
  first. The seam is the largest turn any skinning joint makes between the first and the last frame. Vanilla's role clips (idle_rifle and _mg,
  moving, march, charge, attack_stand, retreat) measure 0.0 to 6.3 degrees (idle_rifle 6.3, charge 3.6, attack_stand 3.2, retreat 1.8, march 0.0). The
  limit is that worst with a quarter added, `LOOP_POSE_LIMIT_DEGREES`. A death is not a loop. The orc's attack measured 118.7 degrees.
- Feet on the ground (`foot_heights`, TRIPO-FOOT-BELOW-GROUND). `UNIT-ANIM-GROUND` reads every vertex, the toes included, but its sink limit is
  vanilla's worst over every clip (4.2%, a push-up). Vanilla's own role clips sink at most 0.9% (move 0.66%, charge 0.86%), and the kit grounds
  Tripo clips per frame to zero, so a Tripo clip is held to `FOOT_SINK_LIMIT`, a tenth of a percent of the height, after the export too. Blender's
  grounding sees the clip at 24 fps and the export resamples it at 30, so a foot dips between keys: the orc's move sank 0.17% and its retreat 0.55%.
  `run_pilot.ground_exported_clips` grounds the exported clips per frame by `pdx_ground` with `GROUND_TOLERANCE`, under the check's limit.
- Death feet (`death_feet_height`, TRIPO-DEATH-FEET). In the last `DEATH_FINAL_FRAMES` frames of vanilla's deaths (death_rifle, death_mg) the lowest foot
  vertex sits -0.6% to +0.6% of the height above the rest ground (the body sinks into it, the boots stay on it). The limit is 1%. The orc's boots hung
  5.6% up with both lower legs bent. `settle_death_legs` turns the leg joints toward the rest pose, by the smallest share that brings the boots to
  the ground, ramped in from the moment the body lies down, so no joint turns faster than `lib/tripo_trim.SETTLE_MAX_RATE`. It tries the knees
  first, then the thighs, then both (`LEG_SETTLE_GROUPS`): the zombie's death (2026-11-16) ended on its back with both thighs lifted at the hip,
  boots 4.3% up. Straightening its knees lifted the boots further (9.4% at the full share), and turning the thighs 40% back brought them down.
- Waist twist (`stance_twist`, TRIPO-WAIST-TWIST). The turn about the up axis between the shoulder line (the two upper arms' joints) and
  the way the planted feet point, against the rest pose's: what a viewer reads as a wrung waist is the chest turned away from feet that
  stand still. Each foot's heading is its ankle joint's turn applied to the rest pose's ankle-to-toe direction (to the body's forward on a
  rig without toes). A frame is read only when both feet stand: each foot within `STANCE_FOOT_LEVEL` of level (about 32 degrees) and its
  lower end (ankle or toe joint, against its rest height) within `STANCE_PLANTED` of the height of the other's. A stride or a run gives no
  reading, so a chest turned across a running body is not counted. Vanilla's GER infantry clips on GER_infantry.mesh (the same on
  GER_infantry_alt_0, ENG_infantry and GER_infantry_snow, 2026-11-16), worst per role: retreat 19.6 (retreat_rifle), move 18.4 (moving_rifle),
  idle 69.7 (long_idle02, the soldier looks behind him), attack 38.3 (charge_mg_shoot), death 30.8 (death_mg, still standing). Vanilla has
  no defend clip, so defend takes the attack's. The limit is the role's worst with a quarter added (`WAIST_TWIST_LIMITS`).
  The first measure (`waist_twist`, the shoulder line against the hip line) read 28 degrees on the orc's attack (2026-11-16) and passed
  under its 64 degree limit, because the orc's Hips bone itself turned 44 degrees while the legs turned back: on the skin the chest turned
  62 degrees against the feet, and two reviewers saw the torso wrung against hips that faced forward. The stance twist reads 68 there.
  Every foot measure that also reads strides failed: vanilla's charges hold the chest 45 to 75 degrees off a running foot (charge_mg 69),
  so the limit would have passed the orc again. The zombie's retreat (Tripo's flee_01) twisted 43 degrees by the first measure and a
  reviewer saw the waist wrung.
- Death rest (`death_rest_heights`, TRIPO-DEATH-REST). In the last frame of vanilla's deaths (`DEATH_REST_FRAMES`) the lowest skin of the
  chest (the spine bones), the head and each hand sits at most 8.2% of the height above the ground once the body is lifted out of it
  (death_rifle's head; death_mg ends with chest 3.4%, head 4.5%, hands 3.8% and 5.8%). The limit is that worst with a quarter added.
  The end pose is judged, not the last `DEATH_FINAL_FRAMES`: death_rifle is still landing 8 frames before its end (a hand at 11.8%). The
  orc's death (Tripo's defeat_03, 2026-11-16) ended with the hips on the ground and the chest at 5.8%, the head at 16.3% and the hands
  at 19%, arms out level: two reviewers read a body frozen in a dive. `settle_death_upper` turns the spine, then the neck, then each upper
  arm toward the ground (`UPPER_SETTLE_GROUPS`), each by the smallest turn that brings its parts within `DEATH_REST_TARGET` of the ground,
  judged after the ground pass's lift, never so far that the lift raises the body by more than `UPPER_SETTLE_LIFT`. Each turn is ramped
  in, like the legs' settle, once the hips are down and the chest, the head and the hands have stopped moving. On the orc: spine 22,
  left arm 6 and right arm 40 degrees, chest 2.1%, head 3.2%, hands 3.4% and 4.0%.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, tripo_trim
from .pdx_binary import PdxFormatError, read

LOOP_ROLES = ("idle", "move", "attack", "defend", "retreat")
VANILLA_LOOP_WORST_DEGREES = 6.3
LOOP_POSE_LIMIT_DEGREES = 8.0
FOOT_SINK_LIMIT = 0.001
GROUND_TOLERANCE = 0.0005
DEATH_FINAL_FRAMES = 15
DEATH_FEET_LIMIT = 0.01
DEATH_FEET_TARGET = 0.004
LYING_HIPS_SETTLE = 0.02
LEG_SETTLE_MIN_FRAMES = 12  # a lying body takes its legs down over at least 0.4 s
LEG_SETTLE_GROUPS = (("knees",), ("thighs",), ("thighs", "knees"))  # tried in this order, the first that brings the boots down wins
VANILLA_WAIST_TWIST_DEGREES = {"retreat": 19.6, "move": 18.4, "idle": 69.7, "attack": 38.3, "defend": 38.3, "death": 30.8}
WAIST_TWIST_LIMITS = {role: round(1.25 * value, 1) for role, value in VANILLA_WAIST_TWIST_DEGREES.items()}
STANCE_FOOT_LEVEL = 0.85  # a foot's heading counts when its horizontal part is at least this share of it (within about 32 degrees of level)
STANCE_PLANTED = 0.02  # both feet stand when their lower ends are within this share of the height of each other
VANILLA_DEATH_REST = 0.082
DEATH_REST_FRAMES = 1
DEATH_REST_LIMIT = round(1.25 * VANILLA_DEATH_REST, 3)
DEATH_REST_TARGET = 0.04  # what the upper-body settle aims for: vanilla's death_mg ends with its chest, head and hands at 3.4% to 5.8%
UPPER_SETTLE_LIFT = 0.005  # the settle never turns a part so far into the ground that the ground pass lifts the body by more than this
UPPER_SETTLE_STEP = 2.0  # degrees between the turns tried
UPPER_SETTLE_MAX = 60.0
UPPER_SETTLE_GROUPS = ("spine", "neck", "left arm", "right arm")  # tried in this order, each judged after the ones before
FOOT_WORDS = ("foot", "toe")


def skinning_joints(mesh: pdx_deform.SkinnedMesh) -> set:
    return {mesh.bones[index] for index in np.unique(mesh.joints[mesh.weights > 0]) if 0 <= index < len(mesh.bones)}


def quaternion_turn(a: np.ndarray, b: np.ndarray) -> float:
    a = a / max(float(np.linalg.norm(a)), 1e-12)
    b = b / max(float(np.linalg.norm(b)), 1e-12)
    return float(np.degrees(2.0 * np.arccos(min(1.0, abs(float(a @ b))))))


def loop_seam(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> Tuple[float, str]:
    """The largest turn (degrees) of a skinning joint between the first and the last frame, and the joint."""

    skinning = skinning_joints(mesh)
    best, where = 0.0, ""
    if anim.frames < 2:
        return best, where
    for joint, channel in anim.channels.items():
        if joint in skinning:
            turn = quaternion_turn(channel["q"][0], channel["q"][-1])
            if turn > best:
                best, where = turn, joint
    return best, where


def foot_mask(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """Vertices whose strongest bone is a foot or toe bone (any rig: the names carry `foot` or `toe`)."""

    dominant = pdx_deform.dominant_bones(mesh)
    return np.array([index >= 0 and any(word in mesh.bones[index].lower() for word in FOOT_WORDS) for index in dominant], bool)


def foot_heights(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, frames: Optional[Sequence[int]] = None) -> np.ndarray:
    """Per frame, the lowest foot vertex above the rest pose's ground as a share of the height (negative: under it). NaN without foot vertices."""

    mask = foot_mask(mesh)
    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    indices = range(matrices.shape[0]) if frames is None else frames
    if not mask.any():
        return np.full(len(list(indices)), np.nan)
    return np.array([(float(pdx_deform.skin(mesh, matrices[i])[mask, 1].min()) - ground) / height for i in indices])


def death_feet_height(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, final: int = DEATH_FINAL_FRAMES) -> float:
    """The highest the lowest foot vertex sits above the ground over the last `final` frames of a death (share of height)."""

    first = max(anim.frames - final, 0)
    heights = foot_heights(mesh, anim, range(first, anim.frames))
    return float(np.nanmax(heights)) if len(heights) and not np.all(np.isnan(heights)) else 0.0


def lifted_death_feet_height(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, exclude_bones: Sequence[str] = (),
                             final: int = DEATH_FINAL_FRAMES) -> float:
    """`death_feet_height` as it will be after the ground pass: a death is lifted so no part of the body is under the ground, so each final
    frame's boots rise by however far its lowest body point sinks. Vertices bound mostly to `exclude_bones` (a dropped weapon) do not count."""

    mask = foot_mask(mesh)
    if not mask.any():
        return 0.0
    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    excluded = [i for i, name in enumerate(mesh.bones) if name in set(exclude_bones)]
    body = ~np.isin(pdx_deform.dominant_bones(mesh), excluded) if excluded else np.ones(len(mesh.positions), bool)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    worst = -np.inf
    for frame in range(max(anim.frames - final, 0), anim.frames):
        points = pdx_deform.skin(mesh, matrices[frame])
        lift = max(0.0, ground - float(points[body, 1].min()))
        worst = max(worst, (float(points[mask, 1].min()) + lift - ground) / height)
    return float(worst) if np.isfinite(worst) else 0.0


# ---- the death's legs --------------------------------------------------------------------------------------------------

def _quaternion_from_matrix(m: np.ndarray) -> np.ndarray:
    """x, y, z, w of a rotation matrix (the PDX order)."""

    m = np.asarray(m, float)[:3, :3]
    scale = np.cbrt(max(abs(np.linalg.det(m)), 1e-12))
    m = m / scale
    t = m[0, 0] + m[1, 1] + m[2, 2]
    if t > 0:
        s = np.sqrt(t + 1.0) * 2.0
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2.0
        q = [0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2.0
        q = [(m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2.0
        q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s, (m[1, 0] - m[0, 1]) / s]
    q = np.asarray(q, float)
    return q / max(float(np.linalg.norm(q)), 1e-12)


def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    dot = float(a @ b)
    if dot < 0:
        b, dot = -b, -dot
    if dot > 0.9995:
        out = a + t * (b - a)
        return out / np.linalg.norm(out)
    theta = np.arccos(min(dot, 1.0))
    return (np.sin((1 - t) * theta) * a + np.sin(t * theta) * b) / np.sin(theta)


def _samples_offset(data: bytes, kind: bytes) -> int:
    start = data.find(b"[samples\0")
    if start < 0:
        raise PdxFormatError("the file has no samples block")
    marker = data.find(b"!\x01" + kind + b"f", start)
    if marker < 0:
        raise PdxFormatError("the samples block has no such channel")
    return marker + 8


@dataclass
class LegSettle:
    changed: bool
    share: float = 0.0
    from_frame: int = 0
    frames: int = 0
    height_before: float = 0.0
    height_after: float = 0.0
    note: str = ""
    joints: Tuple[str, ...] = ()


def _lying_frame(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, pelvis: int) -> int:
    """The first frame from which the hips stay within `LYING_HIPS_SETTLE` of the height of where they end: the body has come down, so the legs
    settle onto the ground instead of through it while it is still falling."""

    posed = pdx_motion.posed_joints(mesh, anim)
    ground = float(mesh.positions[:, 1].min())
    share = (posed[:, pelvis, 1] - ground) / max(mesh.height, 1e-6)
    off = np.nonzero(np.abs(share - share[-1]) > LYING_HIPS_SETTLE)[0]
    return int(min(off[-1] + 1, anim.frames - 1)) if len(off) else 0


def _turned_toward_rest(anim: pdx_deform.Animation, joints: Sequence[str], rest: dict, share: float, weights: np.ndarray) -> pdx_deform.Animation:
    """`anim` with each joint's rotation turned toward its rest rotation by `share` times the frame's weight."""

    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    for joint in joints:
        q = anim.channels[joint]["q"].copy()
        for frame in range(anim.frames):
            if weights[frame] > 0:
                q[frame] = slerp(q[frame], rest[joint], share * weights[frame])
        channels[joint]["q"] = q
    return pdx_deform.Animation(anim.fps, anim.frames, channels)


def _onset_ramp(frames: int, onset: int, length: int) -> np.ndarray:
    """0 before `onset`, a smoothstep over `length` frames from it, then 1 to the end."""

    weights = np.zeros(frames)
    end = min(onset + length, frames - 1)
    ramp = tripo_trim.settle_weights(length)
    for frame in range(onset, frames):
        weights[frame] = 1.0 if frame >= end else float(ramp[frame - onset])
    return weights


def _search_leg_settle(mesh, anim, groups: List[List[str]], rest: dict, before: float, target: float, exclude_bones: Sequence[str]):
    """(share, joints): the first group whose smallest share brings the lifted boots under `target`, else the share and group that bring them
    lowest. (0.0, []) when nothing lowers them."""

    best_share, best_height, best_joints = 0.0, before, []
    full = np.ones(anim.frames)
    for joints in groups:
        for share in np.linspace(0.05, 1.0, 20):
            height = lifted_death_feet_height(mesh, _turned_toward_rest(anim, joints, rest, float(share), full), exclude_bones)
            if height < best_height - 1e-6:
                best_share, best_height, best_joints = float(share), height, joints
            if height <= target:
                return float(share), joints
    return best_share, best_joints


def _write_rotations(data: bytearray, keyed: List[str], joints: Sequence[str], result: pdx_deform.Animation, weights: np.ndarray) -> None:
    """Write the joints' rotation samples of the frames with a weight into the `.anim` bytes, in place."""

    offset = _samples_offset(bytes(data), b"q")
    for joint in joints:
        slot = keyed.index(joint)
        for frame in np.nonzero(weights > 0)[0]:
            position = offset + 4 * (4 * (int(frame) * len(keyed) + slot))
            struct.pack_into("<4f", data, position, *[float(v) for v in result.channels[joint]["q"][frame]])


def settle_death_legs(mesh_path: Path, anim_path: Path, out_path: Path, limit: float = DEATH_FEET_LIMIT, target: float = DEATH_FEET_TARGET,
                      exclude_bones: Sequence[str] = ()) -> LegSettle:
    """Write `out_path`: `anim_path` with the legs turned toward the rest pose when the boots hang above the ground at the end of a death.

    One share s in [0, 1] for one group of leg joints (`LEG_SETTLE_GROUPS`: the knees, then the thighs, then both), the smallest that brings the
    boots under `target`, judged as the ground pass will leave them (`lifted_death_feet_height`). The first group that reaches it wins. If none
    does, the group and share that bring them lowest. The share is ramped in with a smoothstep from the frame the hips come down to the ground and
    held to the end. Only that group's rotation samples change."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    legs = pdx_motion.find_legs(mesh)
    before = lifted_death_feet_height(mesh, anim, exclude_bones)
    if not legs.legs or legs.pelvis < 0 or before <= limit:
        Path(out_path).write_bytes(bytes(data))
        return LegSettle(False, height_before=before, height_after=before, note="the boots are on the ground" if before <= limit else "no legs found")
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    part = {"knees": [mesh.bones[leg.knee] for leg in legs.legs], "thighs": [mesh.bones[leg.hip] for leg in legs.legs if leg.hip >= 0]}
    groups = [joints for joints in ([name for kind in group for name in part[kind] if name in keyed] for group in LEG_SETTLE_GROUPS) if joints]
    bind = pdx_deform._bind_locals(mesh)
    rest = {mesh.bones[i]: _quaternion_from_matrix(bind[i]) for i in range(len(mesh.bones))}
    onset = _lying_frame(mesh, anim, legs.pelvis)
    share, joints = _search_leg_settle(mesh, anim, groups, rest, before, target, exclude_bones)
    if share == 0.0:
        Path(out_path).write_bytes(bytes(data))
        return LegSettle(False, height_before=before, height_after=before, note="turning the knees or the thighs does not lower the boots")
    turn = max(quaternion_turn(q, slerp(q, rest[joint], share)) for joint in joints for q in anim.channels[joint]["q"][onset:])
    length = int(min(max(tripo_trim.settle_frames(turn), LEG_SETTLE_MIN_FRAMES), max(anim.frames - 1 - onset, 1)))
    weights = _onset_ramp(anim.frames, onset, length)
    result = _turned_toward_rest(anim, joints, rest, share, weights)
    _write_rotations(data, keyed, joints, result, weights)
    Path(out_path).write_bytes(bytes(data))
    after = lifted_death_feet_height(mesh, result, exclude_bones)
    return LegSettle(True, share, onset, length, before, after, joints=tuple(joints))


# ---- the death's upper body --------------------------------------------------------------------------------------------

def _subtree(parents: Sequence[int], joint: int) -> List[int]:
    out, stack = [], [joint]
    while stack:
        current = stack.pop()
        out.append(current)
        stack += [i for i, parent in enumerate(parents) if parent == current]
    return out


def _chain_up(parents: Sequence[int], joint: int) -> List[int]:
    out = [joint]
    while parents[out[-1]] >= 0:
        out.append(parents[out[-1]])
    return out


@dataclass
class UpperBody:
    """The joints the upper-body settle turns and the bones whose skin it judges, found from the skeleton: the trunk runs from the bone
    the legs hang from (exclusive) up to the bone the two upper arms branch from; the neck from there to the head bone (the head itself
    when nothing lies between); the hands are the bones named `hand` under each upper arm."""

    pelvis: int
    trunk: List[int]
    neck: List[int]
    head: List[int]
    arms: Tuple[int, int]
    hands: Tuple[List[int], List[int]]


def upper_body(mesh: pdx_deform.SkinnedMesh) -> Optional[UpperBody]:
    legs = pdx_motion.find_legs(mesh)
    left, right = shoulder_joints(mesh)
    if len(legs.legs) != 2 or legs.pelvis < 0 or left < 0 or right < 0:
        return None
    up_left, up_right = _chain_up(mesh.parents, left), _chain_up(mesh.parents, right)
    branch = next((j for j in up_left if j in set(up_right)), -1)
    if branch < 0 or legs.pelvis not in _chain_up(mesh.parents, branch):
        return None
    trunk, joint = [], branch
    while joint >= 0 and joint != legs.pelvis:
        trunk.append(joint)
        joint = mesh.parents[joint]
    trunk.reverse()
    arms_below = set(_subtree(mesh.parents, left)) | set(_subtree(mesh.parents, right))
    heads = [i for i, name in enumerate(mesh.bones) if "head" in name.lower() and i not in arms_below and branch in _chain_up(mesh.parents, i)]
    if not trunk or not heads:
        return None
    head = min(heads, key=lambda i: len(_chain_up(mesh.parents, i)))
    neck = list(reversed(_chain_up(mesh.parents, head)[1:_chain_up(mesh.parents, head).index(branch)])) or [head]
    hands = tuple([i for i in _subtree(mesh.parents, arm) if "hand" in mesh.bones[i].lower()] for arm in (left, right))
    return UpperBody(legs.pelvis, trunk, neck, _subtree(mesh.parents, head), (left, right), hands)  # type: ignore[arg-type]


def _part_masks(mesh: pdx_deform.SkinnedMesh, body: UpperBody, exclude_bones: Sequence[str]) -> dict:
    dominant = pdx_deform.dominant_bones(mesh)
    excluded = np.isin(dominant, [i for i, name in enumerate(mesh.bones) if name in set(exclude_bones)])
    parts = {"chest": body.trunk, "head": body.head, "left hand": body.hands[0], "right hand": body.hands[1], "hips": [body.pelvis]}
    masks = {name: np.isin(dominant, bones) & ~excluded for name, bones in parts.items() if bones}
    masks["body"] = ~excluded
    return {name: mask for name, mask in masks.items() if mask.any()}


def death_rest_heights(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, exclude_bones: Sequence[str] = (),
                       final: int = DEATH_REST_FRAMES, body: Optional[UpperBody] = None) -> Optional[dict]:
    """Over the last `final` frames of a death, the highest each part's lowest skin sits above the ground once the ground pass has lifted
    the body out of it (share of height): `chest`, `head`, `left hand`, `right hand`, `hips`, and `lift`, the largest lift. Skin bound mostly
    to `exclude_bones` (a dropped weapon) never counts. None for a body without legs, two upper arms and a head."""

    body = body or upper_body(mesh)
    if body is None:
        return None
    masks = _part_masks(mesh, body, exclude_bones)
    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    first = max(anim.frames - final, 0)
    channels = {name: {key: values[first:] for key, values in channel.items()} for name, channel in anim.channels.items()}
    tail = pdx_deform.Animation(anim.fps, anim.frames - first, channels)
    matrices = pdx_deform.skinning_matrices(mesh, tail)
    out = {name: -np.inf for name in masks if name != "body"}
    out["lift"] = 0.0
    for frame in range(tail.frames):
        points = pdx_deform.skin(mesh, matrices[frame])[:, 1]
        lift = max(0.0, ground - float(points[masks["body"]].min()))
        out["lift"] = max(out["lift"], lift / height)
        for name in out:
            if name != "lift":
                out[name] = max(out[name], (float(points[masks[name]].min()) + lift - ground) / height)
    return {name: round(float(value), 4) for name, value in out.items()}


def _world_rotations(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> Tuple[np.ndarray, np.ndarray]:
    """(F, B, 3, 3) each joint's world rotation (scale removed) and (F, B, 3) its position."""

    world = pdx_deform.skinning_matrices(mesh, anim) @ np.linalg.inv(mesh.inverse_bind)[None]
    u, _s, vt = np.linalg.svd(world[..., :3, :3])
    rotation = u @ vt
    flip = np.linalg.det(rotation) < 0
    rotation[flip] = -rotation[flip]
    return rotation, world[..., :3, 3]


def _axis_angle(axis: np.ndarray, degrees: float) -> np.ndarray:
    x, y, z = axis
    angle = np.radians(degrees)
    c, s = np.cos(angle), np.sin(angle)
    k = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) + s * k + (1.0 - c) * (k @ k)


def _turned_down(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, joints: Sequence[int], end: np.ndarray, angles: np.ndarray,
                 up: int = 1) -> pdx_deform.Animation:
    """`anim` with the chain `joints` (parent first) bent toward the ground: in each frame every joint turns `angles[frame] / len(joints)`
    degrees about the world axis that carries the line from the first joint to `end` (a (F, 3) track) straight down, so the chain's far
    end sinks and the bones below the first joint keep their place."""

    rotations, positions = _world_rotations(mesh, anim)
    down = np.zeros(3)
    down[up] = -1.0
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    first = joints[0]
    for joint in joints:
        channels[mesh.bones[joint]]["q"] = anim.channels[mesh.bones[joint]]["q"].copy()
    for frame in range(anim.frames):
        if angles[frame] <= 0:
            continue
        axis = np.cross(end[frame] - positions[frame, first], down)
        if np.linalg.norm(axis) < 1e-9:
            continue
        turn = _axis_angle(axis / np.linalg.norm(axis), float(angles[frame]) / len(joints))
        for joint in joints:
            parent = mesh.parents[joint]
            frame_of_parent = rotations[frame, parent] if parent >= 0 else np.eye(3)
            q = channels[mesh.bones[joint]]["q"]
            local = pdx_deform._quaternion_matrices(q[frame][None])[0]
            new = _quaternion_from_matrix(frame_of_parent.T @ turn @ frame_of_parent @ local)
            q[frame] = new if float(new @ q[frame]) >= 0 else -new
    return pdx_deform.Animation(anim.fps, anim.frames, channels)


@dataclass
class UpperSettle:
    changed: bool
    from_frame: int = 0
    turns: dict = field(default_factory=dict)  # group: degrees (whole chain)
    frames: dict = field(default_factory=dict)  # group: ramp frames
    heights_before: dict = field(default_factory=dict)
    heights_after: dict = field(default_factory=dict)
    note: str = ""


def _resting_frame(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, joints: Sequence[int]) -> int:
    """The first frame from which every one of `joints` stays within `LYING_HIPS_SETTLE` of the height of where it ends: the upper body has
    come to rest, so a turn toward the ground does not push it through the ground while it still moves (an arm still swinging down)."""

    posed = pdx_motion.posed_joints(mesh, anim)[:, list(joints), 1]
    off = np.nonzero((np.abs(posed - posed[-1]) / max(mesh.height, 1e-6) > LYING_HIPS_SETTLE).any(axis=1))[0]
    return int(min(off[-1] + 1, anim.frames - 1)) if len(off) else 0


def _group_joints(body: UpperBody, group: str) -> Tuple[List[int], List[str], str]:
    """(joints turned, parts judged, the part whose skin is the chain's far end) of one `UPPER_SETTLE_GROUPS` entry."""

    if group == "spine":
        return body.trunk, ["chest", "head"], "head"
    if group == "neck":
        return body.neck, ["head"], "head"
    side = "left" if group.startswith("left") else "right"
    return [body.arms[0 if side == "left" else 1]], [f"{side} hand"], f"{side} hand"


def _end_track(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, mask: np.ndarray, samples: int = 400) -> np.ndarray:
    """(F, 3) the centre of the skin in `mask` (up to `samples` of its vertices) in each frame: where a chain's far end is."""

    chosen = np.nonzero(mask)[0]
    chosen = chosen[np.linspace(0, len(chosen) - 1, min(samples, len(chosen))).round().astype(int)]
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    points = mesh.positions[chosen]
    out = np.zeros((anim.frames, 3))
    for frame in range(anim.frames):
        out[frame] = _skin_points(points, mesh.joints[chosen], mesh.weights[chosen], matrices[frame]).mean(axis=0)
    return out


def _skin_points(positions: np.ndarray, joints: np.ndarray, weights: np.ndarray, matrices: np.ndarray) -> np.ndarray:
    """Skin only `positions` (with their own joints and weights) by one frame's matrices."""

    out = np.zeros_like(positions)
    safe = np.clip(joints, 0, None)
    for k in range(joints.shape[1]):
        used = weights[:, k] > 0
        if used.any():
            m = matrices[safe[used, k]]
            out[used] += weights[used, k, None] * (np.einsum("vij,vj->vi", m[:, :3, :3], positions[used]) + m[:, :3, 3])
    return out


def _kept_in_place(mesh: pdx_deform.SkinnedMesh, original: pdx_deform.Animation, turned: pdx_deform.Animation,
                   bones: Sequence[int]) -> pdx_deform.Animation:
    """`turned` with each of `bones` (parent first) given the local keys that leave it where `original` has it in the world: a weapon the
    unit has let go of stays where it fell when the arm that dropped it is laid down. The orc's axe hangs from its right hand, and turning
    that arm 42 degrees toward the ground swung the dropped axe 33% of the height into it (2026-11-16)."""

    world = pdx_deform.skinning_matrices(mesh, original) @ np.linalg.inv(mesh.inverse_bind)[None]
    channels = {name: dict(channel) for name, channel in turned.channels.items()}
    current = pdx_deform.Animation(turned.fps, turned.frames, channels)
    for bone in bones:
        parent = mesh.parents[bone]
        if parent < 0:
            continue
        posed = pdx_deform.skinning_matrices(mesh, current) @ np.linalg.inv(mesh.inverse_bind)[None]
        name = mesh.bones[bone]
        q, t = channels[name]["q"].copy(), channels[name]["t"].copy()
        scale = channels[name]["s"]
        for frame in range(turned.frames):
            local = np.linalg.inv(posed[frame, parent]) @ world[frame, bone]
            new = _quaternion_from_matrix(local[:3, :3] / max(float(scale[frame]), 1e-12))
            q[frame] = new if float(new @ q[frame]) >= 0 else -new
            t[frame] = local[:3, 3]
        channels[name]["q"], channels[name]["t"] = q, t
    return current


def _write_translations(data: bytearray, keyed: List[str], joints: Sequence[str], result: pdx_deform.Animation, weights: np.ndarray) -> None:
    """Write the joints' translation samples of the frames with a weight into the `.anim` bytes, in place."""

    offset = _samples_offset(bytes(data), b"t")
    for joint in joints:
        slot = keyed.index(joint)
        for frame in np.nonzero(weights > 0)[0]:
            position = offset + 4 * (3 * (int(frame) * len(keyed) + slot))
            struct.pack_into("<3f", data, position, *[float(v) for v in result.channels[joint]["t"][frame]])


def _smallest_turn(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, body: UpperBody, joints: Sequence[int], end: np.ndarray,
                   full: np.ndarray, heights: dict, judged: Sequence[str], target: float, exclude_bones: Sequence[str]) -> float:
    """Degrees: the smallest turn of `joints` toward the ground (`UPPER_SETTLE_STEP` steps) that brings the `judged` parts under `target`
    without the lift growing by more than `UPPER_SETTLE_LIFT`, else the one that brings them lowest. 0.0 when no turn lowers them."""

    best, best_value = 0.0, max(heights[name] for name in judged)
    for degrees in np.arange(UPPER_SETTLE_STEP, UPPER_SETTLE_MAX + 1e-9, UPPER_SETTLE_STEP):
        trial = death_rest_heights(mesh, _turned_down(mesh, anim, joints, end, degrees * full), exclude_bones, body=body)
        if trial is None or trial["lift"] > heights["lift"] + UPPER_SETTLE_LIFT:
            break
        value = max(trial[name] for name in judged)
        if value < best_value - 1e-4:
            best, best_value = float(degrees), value
        if value <= target:
            break
    return best


def settle_death_upper(mesh_path: Path, anim_path: Path, out_path: Path, exclude_bones: Sequence[str] = (),
                       target: float = DEATH_REST_TARGET, limit: float = DEATH_REST_LIMIT) -> UpperSettle:
    """Write `out_path`: `anim_path` with the chest, the head and the hands brought down to the ground at the end of a death that ends with
    the hips down and any of them higher than `limit` (TRIPO-DEATH-REST).

    For each of `UPPER_SETTLE_GROUPS` in turn (the trunk's bones, the neck, each upper arm) whose parts still sit above `target`: the
    smallest turn toward the ground, in `UPPER_SETTLE_STEP` steps up to `UPPER_SETTLE_MAX`, that brings them under it, judged on the end
    pose as the ground pass will lift it (`death_rest_heights`). A turn that makes the lift grow by more than
    `UPPER_SETTLE_LIFT` goes through the ground and is not taken; when no turn reaches the target, the one that brings the parts lowest.
    Each kept turn is ramped in with a smoothstep from the frame the hips have come down and the chest, the head and the hands have come
    to rest (`_lying_frame`, `_resting_frame`), over the frames the settle's speed limit asks for (at least `LEG_SETTLE_MIN_FRAMES`), and
    held to the end. Only those joints' rotation samples change."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    body = upper_body(mesh)
    before = death_rest_heights(mesh, anim, exclude_bones, body=body) if body else None
    if body is None or before is None:
        Path(out_path).write_bytes(bytes(data))
        return UpperSettle(False, note="no legs, two upper arms and a head found")
    parts = [name for name in ("chest", "head", "left hand", "right hand") if name in before]
    if before.get("hips", 1.0) > DEATH_FEET_LIMIT or max(before[name] for name in parts) <= limit:
        Path(out_path).write_bytes(bytes(data))
        note = "the body does not lie on the ground" if before.get("hips", 1.0) > DEATH_FEET_LIMIT else "the upper body rests on the ground"
        return UpperSettle(False, heights_before=before, heights_after=before, note=note)
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    onset = max(_lying_frame(mesh, anim, body.pelvis), _resting_frame(mesh, anim, [body.trunk[-1], body.head[0], *body.hands[0][:1], *body.hands[1][:1]]))
    masks = _part_masks(mesh, body, exclude_bones)
    current, heights = anim, before
    turns, ramps, changed = {}, {}, []
    full = np.zeros(anim.frames)
    full[onset:] = 1.0
    for group in UPPER_SETTLE_GROUPS:
        joints, judged, far = _group_joints(body, group)
        joints = [j for j in joints if mesh.bones[j] in keyed]
        judged = [name for name in judged if name in heights]
        if not joints or not judged or max(heights[name] for name in judged) <= target:
            continue
        if far not in masks:
            continue
        end = _end_track(mesh, current, masks[far])
        best = _smallest_turn(mesh, current, body, joints, end, full, heights, judged, target, exclude_bones)
        if best == 0.0:
            continue
        length = int(min(max(tripo_trim.settle_frames(best / len(joints)), LEG_SETTLE_MIN_FRAMES), max(anim.frames - 1 - onset, 1)))
        weights = _onset_ramp(anim.frames, onset, length)
        current = _turned_down(mesh, current, joints, end, best * weights)
        heights = death_rest_heights(mesh, current, exclude_bones, body=body) or heights
        turns[group], ramps[group] = round(best, 1), length
        changed += [mesh.bones[j] for j in joints]
    if not turns:
        Path(out_path).write_bytes(bytes(data))
        return UpperSettle(False, onset, heights_before=before, heights_after=before, note="no turn toward the ground lowers the upper body")
    weights = np.zeros(anim.frames)
    weights[onset:] = 1.0
    turned = {mesh.bones.index(name) for name in changed}
    held = [i for i, name in enumerate(mesh.bones) if name in set(exclude_bones) and name in keyed
            and turned & set(_chain_up(mesh.parents, i)[1:])]
    if held:
        current = _kept_in_place(mesh, anim, current, held)
        moved = [joint.name for joint in info.children if "t" in str((joint.properties.get("sa") or [""])[0])]
        _write_translations(data, moved, [mesh.bones[i] for i in held if mesh.bones[i] in moved], current, weights)
    _write_rotations(data, keyed, changed + [mesh.bones[i] for i in held], current, weights)
    Path(out_path).write_bytes(bytes(data))
    return UpperSettle(True, onset, turns, ramps, before, heights)


# ---- the checks --------------------------------------------------------------------------------------------------------

def _finding(rule: str, subject: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": subject, "message": message, **numbers}


def shoulder_joints(mesh: pdx_deform.SkinnedMesh) -> Tuple[int, int]:
    """(left, right) upper-arm joints: the first bone named with the side and `arm` but not `fore` (Tripo's LeftArm, vanilla's too)."""

    found = []
    for side in ("left", "right"):
        found.append(next((i for i, name in enumerate(mesh.bones) if side in name.lower() and "arm" in name.lower() and "fore" not in name.lower()), -1))
    return found[0], found[1]


def leg_roots(parents: Sequence[int], a: int, b: int) -> Tuple[int, int]:
    """Each leg's topmost joint: walked up from `a` and `b` to the joint just below the bone both legs hang from. `find_legs` takes the
    joint two above the ground joint as the hip, which on a hoofed body (the demon stands on its toes) is the knee: its walk swung the
    knees and read as a 57 degree waist twist."""

    def chain(j: int) -> List[int]:
        out = [j]
        while parents[out[-1]] >= 0:
            out.append(parents[out[-1]])
        return out

    up_a, up_b = chain(a), chain(b)
    common = next((j for j in up_a if j in set(up_b)), -1)

    def below(up: List[int]) -> int:
        return up[up.index(common) - 1] if common in up and up.index(common) > 0 else up[0]

    return below(up_a), below(up_b)


def waist_twist(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> Optional[np.ndarray]:
    """Per frame, the shoulder line's turn about the up axis (Y) against the hip line's, less the rest pose's (degrees). None without two
    legs and two upper arms."""

    legs = pdx_motion.find_legs(mesh)
    left, right = shoulder_joints(mesh)
    if len(legs.legs) != 2 or left < 0 or right < 0:
        return None
    rest = pdx_motion.rest_joints(mesh)
    posed = pdx_motion.posed_joints(mesh, anim)
    hip_a, hip_b = leg_roots(mesh.parents, legs.legs[0].hip, legs.legs[1].hip)
    # the hip line in the shoulders' left-to-right order
    if (rest[hip_b] - rest[hip_a]) @ (rest[right] - rest[left]) < 0:
        hip_a, hip_b = hip_b, hip_a
    rest_turn = line_twist(rest[left], rest[right], rest[hip_a], rest[hip_b], 1)
    turn = line_twist(posed[:, left], posed[:, right], posed[:, hip_a], posed[:, hip_b], 1) - rest_turn
    return (turn + 180.0) % 360.0 - 180.0


def _yaw(vectors: np.ndarray, up: int) -> np.ndarray:
    a, b = [k for k in range(3) if k != up]
    vectors = np.asarray(vectors, float)
    return np.degrees(np.arctan2(vectors[..., b], vectors[..., a]))


def _wrap(degrees: np.ndarray) -> np.ndarray:
    return (np.asarray(degrees, float) + 180.0) % 360.0 - 180.0


def stance_twist_tracks(shoulder_left: np.ndarray, shoulder_right: np.ndarray, rest_left: np.ndarray, rest_right: np.ndarray,
                        foot_rotations: Sequence[np.ndarray], foot_headings: Sequence[np.ndarray], foot_lifts: Sequence[np.ndarray],
                        up: int, height: float) -> np.ndarray:
    """Per frame, the shoulder line's turn about the `up` axis against the way the standing feet point, less the rest pose's (degrees);
    NaN in a frame where not every foot stands (the rule in the module docstring).

    `shoulder_left` and `shoulder_right` are (F, 3) joint tracks and `rest_left`, `rest_right` their rest positions. Per foot:
    `foot_rotations` (F, 3, 3) the ankle's turn from the rest pose, `foot_headings` (3,) its rest heading (the ankle to the toe), and
    `foot_lifts` (F,) how far its lower end sits above its rest height. Blender (Z up) and the exported files (Y up) call this alike."""

    shoulders = _wrap(_yaw(np.asarray(shoulder_right) - np.asarray(shoulder_left), up) - _yaw(np.asarray(rest_right) - np.asarray(rest_left), up))
    frames = len(shoulders)
    if not len(foot_rotations):
        return np.full(frames, np.nan)
    turns, level = [], []
    for rotation, heading in zip(foot_rotations, foot_headings):
        flat = np.asarray(heading, float).copy()
        flat[up] = 0.0
        flat = flat / max(float(np.linalg.norm(flat)), 1e-12)
        posed = np.einsum("fij,j->fi", np.asarray(rotation, float), flat)
        length = np.linalg.norm(posed, axis=1)
        across = np.sqrt(np.maximum(length ** 2 - posed[:, up] ** 2, 0.0))
        level.append(across / np.maximum(length, 1e-12) >= STANCE_FOOT_LEVEL)
        turns.append(_wrap(_yaw(posed, up) - _yaw(flat, up)))
    lifts = np.asarray(foot_lifts, float)
    standing = np.all(level, axis=0) & (lifts.max(axis=0) - lifts.min(axis=0) <= STANCE_PLANTED * height)
    radians = np.radians(np.asarray(turns))
    feet = np.degrees(np.arctan2(np.sin(radians).sum(axis=0), np.cos(radians).sum(axis=0)))
    return np.where(standing, _wrap(shoulders - feet), np.nan)


def stance_twist(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> Optional[np.ndarray]:
    """`stance_twist_tracks` on an exported clip (NaN where the feet do not both stand). None without two legs and two upper arms."""

    legs = pdx_motion.find_legs(mesh)
    left, right = shoulder_joints(mesh)
    if len(legs.legs) != 2 or left < 0 or right < 0:
        return None
    rest = pdx_motion.rest_joints(mesh)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    posed = (matrices @ np.linalg.inv(mesh.inverse_bind)[None])[:, :, :3, 3]
    rotations, headings, lifts = [], [], []
    for leg in legs.legs:
        if leg.toe >= 0:
            heading = rest[leg.toe] - rest[leg.ankle]
        elif legs.forward is not None:
            heading = legs.forward
        else:
            return None
        rotations.append(matrices[:, leg.ankle, :3, :3])
        headings.append(heading)
        lift = posed[:, leg.ankle, 1] - rest[leg.ankle, 1]
        if leg.toe >= 0:
            lift = np.minimum(lift, posed[:, leg.toe, 1] - rest[leg.toe, 1])
        lifts.append(lift)
    return stance_twist_tracks(posed[:, left], posed[:, right], rest[left], rest[right], rotations, headings, lifts, 1, mesh.height)


def twist_excess(twist: np.ndarray, target: float) -> np.ndarray:
    """Per frame, how far the twist goes past `target` (degrees, signed as the twist): what the untwist turns back."""

    twist = np.asarray(twist, float)
    return np.sign(twist) * np.maximum(np.abs(twist) - float(target), 0.0)


def untwist_excess(twist: np.ndarray, target: float) -> np.ndarray:
    """`twist_excess` for a stance twist with unread (NaN) frames: those take the excess of the read frames around them, interpolated, and
    the clip's ends hold the nearest read frame's, so the spine's turn back has no step where a foot lifts. All zeros when no frame reads."""

    twist = np.asarray(twist, float)
    read = ~np.isnan(twist)
    if not read.any():
        return np.zeros(len(twist))
    excess = twist_excess(np.where(read, twist, 0.0), target)
    frames = np.arange(len(twist))
    return np.interp(frames, frames[read], excess[read])


def line_twist(left: np.ndarray, right: np.ndarray, hip_left: np.ndarray, hip_right: np.ndarray, up: int) -> np.ndarray:
    """Per frame, the shoulder line's turn about the `up` axis against the hip line's (degrees, wrapped), for (frames, 3) joint tracks."""

    a, b = [k for k in range(3) if k != up]

    def yaw(v):
        return np.degrees(np.arctan2(v[..., b], v[..., a]))

    turn = yaw(np.asarray(right) - np.asarray(left)) - yaw(np.asarray(hip_right) - np.asarray(hip_left))
    return (turn + 180.0) % 360.0 - 180.0


def role_of(clip: str) -> str:
    return clip.rsplit("_", 1)[-1]


def pose_findings(mesh: pdx_deform.SkinnedMesh, anims: dict, death_exclude: Sequence[str] = ()) -> Tuple[List[dict], dict]:
    """TRIPO-LOOP-POP, TRIPO-FOOT-BELOW-GROUND, TRIPO-DEATH-FEET, TRIPO-DEATH-REST and TRIPO-WAIST-TWIST over a unit's clips (`anims`: clip
    stem to Animation). `death_exclude`: bones whose skin never decides where the dying body's ground is (a weapon or shield it lets go of)."""

    out: List[dict] = []
    numbers: dict = {}
    for clip, anim in anims.items():
        role = role_of(clip)
        row: dict = {}
        if role in LOOP_ROLES:
            turn, joint = loop_seam(mesh, anim)
            row["loop_seam_degrees"] = round(turn, 1)
            if turn > LOOP_POSE_LIMIT_DEGREES:
                out.append(_finding("TRIPO-LOOP-POP", clip, f"the last frame is {turn:.0f} degrees from the first at {joint} (limit {LOOP_POSE_LIMIT_DEGREES:g}, vanilla's worst role clip {VANILLA_LOOP_WORST_DEGREES:g}): the looped {role} pops back to its start", degrees=round(turn, 1)))
        if role == "death":
            height = death_feet_height(mesh, anim)
            row["final_feet_height_share"] = round(height, 4)
            if height > DEATH_FEET_LIMIT:
                out.append(_finding("TRIPO-DEATH-FEET", clip, f"in the last {DEATH_FINAL_FRAMES} frames the boots hang {height:.1%} of the height above the ground (limit {DEATH_FEET_LIMIT:.0%}, vanilla's deaths end within 0.6%)", share=round(height, 4)))
            rest = death_rest_heights(mesh, anim, death_exclude)
            if rest is not None:
                row["final_rest_heights"] = rest
                parts = {name: rest[name] for name in ("chest", "head", "left hand", "right hand") if name in rest}
                high = {name: value for name, value in parts.items() if value > DEATH_REST_LIMIT}
                if rest.get("hips", 1.0) <= DEATH_FEET_LIMIT and high:
                    words = ", ".join(f"the {name} {value:.1%}" for name, value in high.items())
                    out.append(_finding("TRIPO-DEATH-REST", clip, f"the body ends lying with {words} of the height above the ground (limit {DEATH_REST_LIMIT:.1%}, vanilla's deaths end with every part within {VANILLA_DEATH_REST:.1%}): it reads as frozen mid-fall", share=round(max(high.values()), 4)))
        else:
            heights = foot_heights(mesh, anim)
            lowest = float(np.nanmin(heights)) if len(heights) and not np.all(np.isnan(heights)) else 0.0
            row["lowest_foot_share"] = round(lowest, 4)
            if lowest < -FOOT_SINK_LIMIT:
                frame = int(np.nanargmin(heights))
                out.append(_finding("TRIPO-FOOT-BELOW-GROUND", clip, f"a foot or toe sinks {-lowest:.2%} of the height under the ground in frame {frame} (limit {FOOT_SINK_LIMIT:.1%})", share=round(-lowest, 4), frame=frame))
        out += _twist_findings(mesh, anim, clip, role, row)
        if row:
            numbers[clip] = row
    return out, numbers


def _twist_findings(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, clip: str, role: str, row: dict) -> List[dict]:
    """TRIPO-WAIST-TWIST for one clip (records the clip's largest twist in `row`)."""

    limit = WAIST_TWIST_LIMITS.get(role)
    if limit is None:
        return []
    hips = waist_twist(mesh, anim)
    if hips is not None and len(hips):
        row["hip_line_twist_degrees"] = round(float(np.abs(hips).max()), 1)
    twist = stance_twist(mesh, anim)
    if twist is None or not len(twist) or np.all(np.isnan(twist)):
        return []
    frame = int(np.nanargmax(np.abs(twist)))
    row["waist_twist_degrees"] = round(float(abs(twist[frame])), 1)
    row["waist_twist_frame"] = frame
    if abs(twist[frame]) <= limit:
        return []
    return [_finding("TRIPO-WAIST-TWIST", clip, f"the shoulders turn {abs(twist[frame]):.0f} degrees against the standing feet in frame {frame} (limit {limit:g}, vanilla's worst {role} {VANILLA_WAIST_TWIST_DEGREES[role]:g}): the waist is wrung", degrees=round(float(abs(twist[frame])), 1), frame=frame)]
