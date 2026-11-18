"""The thighs of a Tripo death split apart: its measure, its check (TRIPO-DEATH-SPLAY) and the ease that swings them together.

Two fresh reviewers failed the zombie's death (zombie_k, Tripo's defeat_03 preset, 2026-11-18) at frames 74 to 76: as the body drops to its knees
the raised thigh and the crotch stretch or crush into one long smooth mass with no knee shape, solid red in the diagnostics. The orc's run with
the same preset (orc_k) was failed at the same frames (the kilt and thighs a shapeless mass in the death kneel f74 to f91), and a reviewer of each
saw the legs of the prone body splayed about 90 degrees. Every automated check passed.

What does it: Tripo's clip itself. Read from the rigged GLB (forward kinematics of the preset at the export's 30 frames a second), the body
kneels on its right knee with the left foot planted, the left thigh lifted to the horizontal and swung out, the thighs 106 degrees apart at frame
74 with the left knee folded 131 degrees, and the prone end holds them 79 degrees apart. The exported clip matches it to the degree up to frame
94: no death rule had run there (the free fall kept the clip, the legs' settle starts at frame 96, the upper body was not settled, the ground pass
only moves the root). On the unit's weights, which blend the two thighs and the hips across the crotch, that split pulls the inner thigh and the
crotch apart: 1,533 edges of the skin change past 1.3 times at frame 74 (the review sheets' yellow to red), 606 of them on the left thigh.

Why the stretch checks passed it: every share of a region's deformed edges or area reads vanilla's own low-poly legs as far worse. Over the 168
clip and mesh pairs of the GER infantry clips on GER_infantry, _alt_0, ENG_infantry and _snow, a thigh and crotch region (the hips, thigh and shin
skin from the knee to above the hip joint, per side) has up to 53% of its area past 1.69 times (the push-up) and its deaths 7% to 19%, where the
zombie's death reads 6.7%. So the rule reads the pose instead.

The measure (`thigh_split`): per frame, the angle between the two thighs (each from its hip joint to its knee joint). Vanilla's two deaths
(death_rifle, death_mg; the skeleton is the same on all four meshes) split them at most 38.3 degrees (frame 11 of both, the stumble) and end at
12.6 and 25.2. A death's limit is that worst with a quarter added, `SPLIT_LIMIT` (47.9). Vanilla's other clips split wider (the charge 116, a
crouch 104), but no vanilla body falls that way, and the deaths are the role the rule judges. zombie_k's death measures 107.0 (frame 75).

The ease (`close_death_legs`, run by `run_pilot.ground_exported_clip` on a humanoid's death before the free-fall, legs and upper-body settles):
each frame over the target (vanilla's worst, `SPLIT_TARGET`) has its knees swung toward each other, each leg turned about the line from its hip
joint to its ankle joint with the foot keeping its turn in the world, so the ankle and the foot stay where they are and only the knee moves
(`needed_turns`: the smallest swing that brings the thigh within the target of the other one). The swing goes to the higher knee: each leg takes
0.5 plus the height of its knee over the other's, in thigh lengths, of it (clamped to 0 and 1), so a kneeling body keeps the knee it kneels on and
a lying one swings both legs alike, with no jump between frames. A share of `SHARES` is allowed in a frame only while it, and every smaller one,
keeps the frame inside what the kit's rule (`stretch_smooth.worse`) allows against the clip before and does not sink the body into the ground by
more than the upper-body settle may lift it (`tripo_pose.UPPER_SETTLE_LIFT`). The swing is smoothed over `SMOOTH_FRAMES` (it jumps where a swing
first reaches the target), and the share is the highest smooth curve under every frame's allowed share, ramped over the frames the settle
rule's speed asks for. A result is kept only when it lowers the worst split and the clip is not worse by the kit's rule.

Tried and dropped (offline on zombie_k's exported files): turning the thighs, or the thighs and the knees, toward the rest pose sank the body 4%
to 29% of the height into the ground (the kneeling shin and the planted foot swung under the floor), which the ground pass would answer by lifting
the whole body; turning the thighs toward each other about the axis square to both (the higher one only) halved the deformed edges at frame 74
but pushed the planted left foot 1.7% into the ground at a third of the way. The swing keeps the foot planted. Half the way it takes frame 74
from 1,533 edges past 1.3 times to 1,182, and the raised thigh reads as a knee up in front with the foot planted.

Maths on the exported `.mesh` and `.anim` (`pdx_deform`), no Blender.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, stretch_smooth, tripo_pose, tripo_shoulder, tripo_trim
from .pdx_binary import read

VANILLA_DEATH_SPLIT = 38.3
SPLIT_LIMIT = round(1.25 * VANILLA_DEATH_SPLIT, 1)
SPLIT_TARGET = VANILLA_DEATH_SPLIT
SHARES = np.round(np.arange(0.0, 1.0001, 0.1), 2)
MIN_RAMP_FRAMES = 6
SWING_STEP = 2.0
SWING_MAX = 120.0
SMOOTH_FRAMES = 9


def _unit(vectors: np.ndarray) -> np.ndarray:
    return vectors / np.maximum(np.linalg.norm(vectors, axis=-1, keepdims=True), 1e-12)


def _legs(mesh: pdx_deform.SkinnedMesh):
    legs = pdx_motion.find_legs(mesh)
    if len(legs.legs) != 2 or any(leg.hip < 0 or leg.knee < 0 or leg.ankle < 0 for leg in legs.legs):
        return None
    return legs.legs


def thigh_split(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> Optional[np.ndarray]:
    """(frames,) the angle in degrees between the two thighs (hip joint to knee joint). None without two legs."""

    legs = _legs(mesh)
    if legs is None:
        return None
    posed = pdx_motion.posed_joints(mesh, anim)
    a = _unit(posed[:, legs[0].knee] - posed[:, legs[0].hip])
    b = _unit(posed[:, legs[1].knee] - posed[:, legs[1].hip])
    return np.degrees(np.arccos(np.clip((a * b).sum(axis=-1), -1.0, 1.0)))


# ---- the check ---------------------------------------------------------------------------------------------------------

def splay_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    """TRIPO-DEATH-SPLAY over a unit's death clips (`anims`: clip stem to Animation; clips whose stem does not end in `death` are skipped)."""

    out: List[dict] = []
    numbers: dict = {}
    for clip, anim in anims.items():
        if not clip.endswith("death"):
            continue
        split = thigh_split(mesh, anim)
        if split is None:
            numbers[clip] = {"note": "no two legs"}
            continue
        frame = int(np.argmax(split))
        worst = float(split[frame])
        over = int(np.sum(split > SPLIT_LIMIT))
        numbers[clip] = {"worst_degrees": round(worst, 1), "frame": frame, "frames_over_limit": over, "final_degrees": round(float(split[-1]), 1)}
        if worst > SPLIT_LIMIT:
            out.append({"rule": "TRIPO-DEATH-SPLAY", "subject": clip,
                        "message": f"the thighs split {worst:.0f} degrees apart in frame {frame} (limit {SPLIT_LIMIT:g}, vanilla's deaths {VANILLA_DEATH_SPLIT:g}), "
                                   f"{over} of {len(split)} frames over the limit: the crotch and the raised thigh stretch into one mass",
                        "degrees": round(worst, 1), "frame": frame})
    return out, numbers


# ---- the ease ----------------------------------------------------------------------------------------------------------

@dataclass
class SplayEase:
    changed: bool
    share: float = 0.0  # the largest share of the needed swing used in any frame
    frames_changed: int = 0
    ramp_frames: int = 0
    worst_before: float = 0.0
    worst_after: float = 0.0
    largest_turn_degrees: float = 0.0
    fastest_step_degrees: float = 0.0  # the largest change of a leg's swing between two frames
    note: str = ""


def _swung(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, legs, turns: np.ndarray) -> pdx_deform.Animation:
    """`anim` with each leg turned `turns[frame, leg]` degrees about the line from its hip joint to its ankle joint, the foot keeping its turn in
    the world: the knee swings round that line and the ankle and the foot stay where they are."""

    rotations, positions = tripo_pose._world_rotations(mesh, anim)
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    for leg in legs:
        for joint in (leg.hip, leg.ankle):
            channels[mesh.bones[joint]]["q"] = anim.channels[mesh.bones[joint]]["q"].copy()
    for frame in range(anim.frames):
        for k, leg in enumerate(legs):
            degrees = float(turns[frame, k])
            line = positions[frame, leg.ankle] - positions[frame, leg.hip]
            if abs(degrees) < 1e-9 or np.linalg.norm(line) < 1e-9:
                continue
            turn = tripo_pose._axis_angle(line / np.linalg.norm(line), degrees)
            parent = mesh.parents[leg.hip]
            frame_of_parent = rotations[frame, parent] if parent >= 0 else np.eye(3)
            q = channels[mesh.bones[leg.hip]]["q"]
            new = tripo_pose._quaternion_from_matrix(frame_of_parent.T @ turn @ frame_of_parent @ pdx_deform._quaternion_matrices(q[frame][None])[0])
            q[frame] = new if float(new @ q[frame]) >= 0 else -new
            # the shin turns with the thigh, so the ankle's local turn is set to keep the foot's turn in the world
            q = channels[mesh.bones[leg.ankle]]["q"]
            new = tripo_pose._quaternion_from_matrix((turn @ rotations[frame, mesh.parents[leg.ankle]]).T @ rotations[frame, leg.ankle])
            q[frame] = new if float(new @ q[frame]) >= 0 else -new
    return pdx_deform.Animation(anim.fps, anim.frames, channels)


def _parts(mesh: pdx_deform.SkinnedMesh, posed: np.ndarray, legs) -> np.ndarray:
    """(frames, 2) each leg's part of the swing: 0.5 plus the height of its knee over the other's in thigh lengths, clamped to 0 and 1."""

    rest = pdx_motion.rest_joints(mesh)
    length = max(float(np.mean([np.linalg.norm(rest[leg.knee] - rest[leg.hip]) for leg in legs])), 1e-9)
    first = np.clip(0.5 + (posed[:, legs[0].knee, 1] - posed[:, legs[1].knee, 1]) / length, 0.0, 1.0)
    return np.stack([first, 1.0 - first], axis=1)


def needed_turns(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, legs, target: float) -> np.ndarray:
    """(frames, 2) degrees: for each frame over `target`, each leg's part (`_parts`) of the smallest swing (`SWING_STEP` steps up to
    `SWING_MAX` either way) that brings its thigh within `target` of the other one, or of the swing that brings it closest."""

    posed = pdx_motion.posed_joints(mesh, anim)
    split = thigh_split(mesh, anim)
    parts = _parts(mesh, posed, legs)
    trials = np.arange(-SWING_MAX, SWING_MAX + 1e-9, SWING_STEP)
    trials = trials[np.argsort(np.abs(trials), kind="stable")]
    over = np.nonzero(split > target)[0]
    found = np.zeros((anim.frames, 2, len(trials)))
    for frame in over:
        for k, leg in enumerate(legs):
            other = _unit(posed[frame, legs[1 - k].knee] - posed[frame, legs[1 - k].hip])
            line = _unit(posed[frame, leg.ankle] - posed[frame, leg.hip])
            thigh = posed[frame, leg.knee] - posed[frame, leg.hip]
            swung = np.stack([tripo_pose._axis_angle(line, d) @ thigh for d in trials])
            found[frame, k] = np.degrees(np.arccos(np.clip(_unit(swung) @ other, -1.0, 1.0)))
    out = np.zeros((anim.frames, 2))
    for k in range(2):
        # one way round for the whole clip, the way most of its frames close best: two swings can reach the target from either side, and a
        # frame that took the other one would flip the knee across the leg (the zombie's left knee: 70 degrees one way, 78 the next frame)
        best = trials[np.argmin(found[over, k], axis=1)] if len(over) else np.zeros(0)
        sign = 1.0 if float((np.sign(best) * parts[over, k]).sum()) >= 0 else -1.0
        side = (trials * sign) >= 0
        for frame in over:
            if parts[frame, k] <= 0:
                continue
            angles = np.where(side, found[frame, k], np.inf)
            reached = np.nonzero(angles <= target)[0]
            out[frame, k] = parts[frame, k] * trials[reached[0] if len(reached) else int(np.argmin(angles))]
    return out


def _envelope(cap: np.ndarray, ramp: int) -> np.ndarray:
    """The highest smooth curve under `cap`: in each frame the least of every frame's cap plus a smoothstep rising over `ramp` frames from it."""

    frames = len(cap)
    ramp = max(int(ramp), 1)
    out = np.asarray(cap, float).copy()
    for frame in range(frames):
        t = np.clip(1.0 - np.abs(np.arange(frames) - frame) / ramp, 0.0, 1.0)
        out = np.minimum(out, cap[frame] + 1.0 - t * t * (3.0 - 2.0 * t))
    return np.clip(out, 0.0, 1.0)


def _frame_within(frames: np.ndarray, before: np.ndarray) -> np.ndarray:
    """(frames,) True where a frame stays inside what `stretch_smooth.worse` allows against the same frame before (not only against the clip's
    worst frame: a kneel at frame 66 of the zombie, far under the clip's worst, gained a third more edges past 1.3 times against the clip's rule)."""

    share = stretch_smooth.WORSEN_SHARE
    return ((frames[:, 0] <= before[:, 0] * (1 + share) + 1) & (frames[:, 1] <= before[:, 1] * (1 + share) + 1)
            & (frames[:, 2] <= max(float(before[:, 2].max()), 0.0) * (1 + share) + 1e-6))


def _frame_check(mesh, anim, edges, rest, body) -> Tuple[np.ndarray, np.ndarray]:
    """(frames, 3) the kit's deformation per frame (stretched, squashed, largest growth) and (frames,) how far the ground pass lifts each frame
    (share of the height), from one skinning pass."""

    matrices = pdx_deform.skinning_matrices(mesh, anim)
    ground = float(mesh.positions[:, 1].min())
    height = max(mesh.height, 1e-6)
    deformed = np.zeros((matrices.shape[0], 3))
    lifts = np.zeros(matrices.shape[0])
    for frame in range(matrices.shape[0]):
        posed = pdx_deform.skin(mesh, matrices[frame])
        s, q, g = stretch_smooth._deformed(rest, np.linalg.norm(posed[edges[:, 0]] - posed[edges[:, 1]], axis=1), height)
        deformed[frame] = (s.sum(), q.sum(), g.max())
        lifts[frame] = max(0.0, ground - float(posed[body, 1].min())) / height
    return deformed, lifts


def close_death_legs(mesh_path: Path, anim_path: Path, out_path: Path, exclude_bones: Sequence[str] = (), limit: float = SPLIT_LIMIT,
                     target: float = SPLIT_TARGET) -> SplayEase:
    """Write `out_path`: `anim_path` with the knees swung toward each other where a death splits the thighs past `limit` (see the module
    text). Unchanged, and copied as it is, when the clip passes or no share closes them within the kit's rules."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)

    def unchanged(note: str, before: float = 0.0) -> SplayEase:
        Path(out_path).write_bytes(bytes(data))
        return SplayEase(False, worst_before=round(before, 1), worst_after=round(before, 1), note=note)

    legs = _legs(mesh)
    if legs is None:
        return unchanged("no two legs")
    split = thigh_split(mesh, anim)
    worst = float(split.max()) if len(split) else 0.0
    if worst <= limit:
        return unchanged("the thighs are under the limit", worst)
    keyed = [joint.name for joint in read(anim_path).child("info").children if "q" in str((joint.properties.get("sa") or [""])[0])]
    joints = [mesh.bones[leg.hip] for leg in legs] + [mesh.bones[leg.ankle] for leg in legs]
    if any(name not in keyed for name in joints):
        return unchanged("the clip does not key both thighs and both ankles", worst)
    excluded = [i for i, name in enumerate(mesh.bones) if name in set(exclude_bones)]
    body = ~np.isin(pdx_deform.dominant_bones(mesh), excluded) if excluded else np.ones(len(mesh.positions), bool)
    edges = pdx_deform.mesh_edges(mesh)
    rest = np.linalg.norm(mesh.positions[edges[:, 0]] - mesh.positions[edges[:, 1]], axis=1)
    deformed, lift_before = _frame_check(mesh, anim, edges, rest, body)
    before = tripo_shoulder.summary(deformed)
    need = needed_turns(mesh, anim, legs, target)
    # the need jumps where a swing first reaches the target, so it is smoothed before any share of it is tried
    need = np.stack([tripo_trim.smooth(need[:, k], SMOOTH_FRAMES) for k in range(2)], axis=1)
    allowed = []
    for share in SHARES:
        frames, lifts = _frame_check(mesh, _swung(mesh, anim, legs, share * need), edges, rest, body)
        allowed.append(_frame_within(frames, deformed) & (lifts <= lift_before + tripo_pose.UPPER_SETTLE_LIFT + 1e-9))
    allowed = np.logical_and.accumulate(np.stack(allowed), axis=0)
    cap = np.where(np.abs(need).max(axis=1) > 0, SHARES[np.maximum(allowed.sum(axis=0) - 1, 0)], 0.0)
    if not cap.any():
        return unchanged("no share swings the knees together within the kit's rules", worst)
    ramp = max(tripo_trim.settle_frames(float(np.abs(need).max())), MIN_RAMP_FRAMES)
    weights = _envelope(cap, ramp)
    turn = weights[:, None] * need
    result = _swung(mesh, anim, legs, turn)
    after = float(thigh_split(mesh, result).max())
    frames_after, lifts_after = _frame_check(mesh, result, edges, rest, body)
    if after >= worst - 1e-3:
        return unchanged("swinging the knees together does not lower the worst split", worst)
    if stretch_smooth.worse(before, tripo_shoulder.summary(frames_after)):
        return unchanged("swinging the knees together makes the clip's deformation worse", worst)
    if float((lifts_after - lift_before).max()) > tripo_pose.UPPER_SETTLE_LIFT + 1e-6:
        return unchanged("swinging the knees together sinks the body into the ground", worst)
    changed = np.abs(turn).max(axis=1) > 0
    tripo_pose._write_rotations(data, keyed, joints, result, changed.astype(float))
    Path(out_path).write_bytes(bytes(data))
    step = float(np.abs(np.diff(turn, axis=0)).max()) if len(turn) > 1 else 0.0
    return SplayEase(True, round(float(weights.max()), 3), int(changed.sum()), int(ramp), round(worst, 1), round(after, 1),
                     round(float(np.abs(turn).max()), 1), round(step, 1))
