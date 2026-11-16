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
- Waist twist (`waist_twist`, TRIPO-WAIST-TWIST). The turn about the up axis between the shoulder line (the two upper arms' joints) and the
  hip line (the two thighs' joints), against the rest pose's. Vanilla's GER infantry clips on GER_infantry.mesh, worst per role:
  retreat 23.2 (retreat_mg), move 25.1 (march, moving), idle 39.7 (long_idle01), attack 51.2 (charge_mg_shoot), death 40.7 (death_rifle).
  Vanilla has no defend clip, so defend takes the attack's. The limit is the role's worst with a quarter added (`WAIST_TWIST_LIMITS`).
  The zombie's retreat (Tripo's flee_01) twisted 43 degrees and a reviewer saw the waist wrung.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
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
VANILLA_WAIST_TWIST_DEGREES = {"retreat": 23.2, "move": 25.1, "idle": 39.7, "attack": 51.2, "defend": 51.2, "death": 40.7}
WAIST_TWIST_LIMITS = {role: round(1.25 * value, 1) for role, value in VANILLA_WAIST_TWIST_DEGREES.items()}
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


def twist_excess(twist: np.ndarray, target: float) -> np.ndarray:
    """Per frame, how far the twist goes past `target` (degrees, signed as the twist): what the untwist turns back."""

    twist = np.asarray(twist, float)
    return np.sign(twist) * np.maximum(np.abs(twist) - float(target), 0.0)


def line_twist(left: np.ndarray, right: np.ndarray, hip_left: np.ndarray, hip_right: np.ndarray, up: int) -> np.ndarray:
    """Per frame, the shoulder line's turn about the `up` axis against the hip line's (degrees, wrapped), for (frames, 3) joint tracks."""

    a, b = [k for k in range(3) if k != up]

    def yaw(v):
        return np.degrees(np.arctan2(v[..., b], v[..., a]))

    turn = yaw(np.asarray(right) - np.asarray(left)) - yaw(np.asarray(hip_right) - np.asarray(hip_left))
    return (turn + 180.0) % 360.0 - 180.0


def role_of(clip: str) -> str:
    return clip.rsplit("_", 1)[-1]


def pose_findings(mesh: pdx_deform.SkinnedMesh, anims: dict) -> Tuple[List[dict], dict]:
    """TRIPO-LOOP-POP, TRIPO-FOOT-BELOW-GROUND, TRIPO-DEATH-FEET and TRIPO-WAIST-TWIST over a unit's clips (`anims`: clip stem to Animation)."""

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
    twist = waist_twist(mesh, anim) if limit is not None else None
    if twist is None or not len(twist):
        return []
    frame = int(np.argmax(np.abs(twist)))
    row["waist_twist_degrees"] = round(float(abs(twist[frame])), 1)
    if abs(twist[frame]) <= limit:
        return []
    return [_finding("TRIPO-WAIST-TWIST", clip, f"the shoulders turn {abs(twist[frame]):.0f} degrees against the hips in frame {frame} (limit {limit:g}, vanilla's worst {role} {VANILLA_WAIST_TWIST_DEGREES[role]:g}): the waist is wrung", degrees=round(float(abs(twist[frame])), 1), frame=frame)]
