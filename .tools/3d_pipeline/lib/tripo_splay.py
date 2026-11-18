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

The next run (zombie_l, 2026-11-18, the same job and clips): the swing went 0.6 of the way at most (35 degrees), the worst split from 107 to 93
degrees (frame 72), still over the limit, so TRIPO-DEATH-SPLAY reports it. The edges past 1.3 times fell from 1,533 to 1,256 at frame 74 and from
1,388 to 1,217 at frame 100, the kit's worst-frame counts from 182 stretched and 189 squashed to 145 and 181. The diagnostics show far less red
over the raised thigh and the crotch. What stops it is the squash it adds at the inner thigh in the frames before the kneel (frame 66).

The ogre (2026-11-18, the text-to-motion death that falls forward onto the belly, played on ogre_o's files). Every death candidate failed: the
new clip split the thighs 133 degrees as it lay, and 51 in its first standing frame, already past 47.9. Its rest pose holds them 33.0 degrees
apart (vanilla's 18.5): the thighs are 0.106 of the height thick on hip joints 0.195 apart, so the body stands wide in every clip (idle 15,
the made clips 48 to 51) and a split vanilla's legs reach only in a stumble is this body's stance. So the limit is judged against the body's
own rest pose: its split plus vanilla's opening past its rest pose (38.3 less 18.5, 19.8) with a quarter added (`OPENING_LIMIT`, 24.8), and
never under vanilla's 47.9 (`split_limit`). Vanilla's limit stays 47.9 (18.5 plus 24.8 is 43.3), the zombie's (rest 12.2) and the orc's
(20.8) too, so the zombie's rejected kneel (93 after the swing) still fails, and the ogre's is 57.8. The ease aims at the rest split plus 19.8,
at least 38.3 (`split_target`).

The knee swing alone took the ogre's clip only from 133 to 120: its feet lie 0.43 of the height apart, and a knee swung round the line to a
foot that far out keeps the thigh out. So where a frame still splits past the limit, the whole legs close at the hips (`_closed`): each leg
turns about its hip joint toward the other thigh, about the line square to both thighs, the knee, the shin and the foot following. A lying
body's thighs span the ground, so its legs slide together along it. Closing two planted legs of a body still falling lowers both feet alike,
so the frame is judged by the ground pass that answers it: every lower leg that stood on the ground (within `CONTACT_SHARE`) stays within
the upper-body settle's lift of where it stood, and the body is lifted no more than `CLOSE_LIFT_MAX` (`_contacts_kept`). The two legs keep
`LEG_CLEARANCE` of the sum of their radii between them, thigh to thigh and shin to shin, unless they were nearer already, so no leg goes
through the other. The closing is eased like the swing but each frame is checked at the share the smooth curve gives it (`_eased` with
`checked`), and it repeats from its own result (`CLOSE_PASSES`), because the smoothing leaves part of a sharp peak. Tried and dropped: closing
about the upright line (every point of the leg keeps its height) made the fall's frames worse by the kit's rule (frame 36 from 31 stretched
and 90 squashed edges to 288 and 502), because it turns the thigh against the pelvis. On the ogre's clip the swing and the closing took the
worst split from 133 to 56.2, the worst frame's stretched and squashed edges from 473 and 680 as Tripo made it to 172 and 279 after every death settle, and
the settled clip passes every death rule (`tripo/death_pick.py --settled`).

Maths on the exported `.mesh` and `.anim` (`pdx_deform`), no Blender.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, stretch_smooth, tripo_pose, tripo_shoulder, tripo_trim
from .pdx_binary import read

VANILLA_DEATH_SPLIT = 38.3
SPLIT_LIMIT = round(1.25 * VANILLA_DEATH_SPLIT, 1)
SPLIT_TARGET = VANILLA_DEATH_SPLIT
# The rest pose's own split: vanilla's bind pose holds the thighs 18.5 degrees apart (the same on GER_infantry, _alt_0, ENG_infantry and _snow),
# so its deaths open them at most 19.8 degrees past it. A body bound with its legs wider apart (the round 4 ogre, 33.0: thick thighs on hip
# joints 0.195 of the height apart) stands wider in every clip, and its limit is its own split plus that opening with a quarter added.
VANILLA_REST_SPLIT = 18.5
VANILLA_DEATH_OPENING = round(VANILLA_DEATH_SPLIT - VANILLA_REST_SPLIT, 1)
OPENING_LIMIT = round(1.25 * VANILLA_DEATH_OPENING, 1)
# The thigh closing (`_closed`): the two legs keep at least this share of the sum of their radii between them (thigh to thigh, shin to shin).
LEG_CLEARANCE = 0.9
# A lower leg within this share of the height of the ground stands on it, and the lift that answers the closing may raise the body by at most
# `CLOSE_LIFT_MAX` (`_contacts_kept`).
CONTACT_SHARE = 0.01
CLOSE_LIFT_MAX = 0.02
CLOSE_PASSES = 3
CHECK_ROUNDS = 4
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


def rest_split(mesh: pdx_deform.SkinnedMesh) -> Optional[float]:
    """The angle in degrees between the two thighs in the rest (bind) pose. None without two legs."""

    legs = _legs(mesh)
    if legs is None:
        return None
    rest = pdx_motion.rest_joints(mesh)
    a = _unit(rest[legs[0].knee] - rest[legs[0].hip])
    b = _unit(rest[legs[1].knee] - rest[legs[1].hip])
    return float(np.degrees(np.arccos(np.clip(a @ b, -1.0, 1.0))))


def split_limit(mesh: pdx_deform.SkinnedMesh) -> float:
    """TRIPO-DEATH-SPLAY's limit for this body: vanilla's (`SPLIT_LIMIT`), or the rest pose's own split plus `OPENING_LIMIT` when that is wider."""

    rest = rest_split(mesh)
    return SPLIT_LIMIT if rest is None else round(max(SPLIT_LIMIT, rest + OPENING_LIMIT), 1)


def split_target(mesh: pdx_deform.SkinnedMesh) -> float:
    """What the ease aims for: vanilla's worst death (`SPLIT_TARGET`), or the rest pose's own split plus vanilla's opening when that is wider."""

    rest = rest_split(mesh)
    return SPLIT_TARGET if rest is None else round(max(SPLIT_TARGET, rest + VANILLA_DEATH_OPENING), 1)


# ---- the check ---------------------------------------------------------------------------------------------------------

def splay_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    """TRIPO-DEATH-SPLAY over a unit's death clips (`anims`: clip stem to Animation; clips whose stem does not end in `death` are skipped)."""

    out: List[dict] = []
    numbers: dict = {}
    limit = split_limit(mesh)
    rest = rest_split(mesh)
    for clip, anim in anims.items():
        if not clip.endswith("death"):
            continue
        split = thigh_split(mesh, anim)
        if split is None:
            numbers[clip] = {"note": "no two legs"}
            continue
        frame = int(np.argmax(split))
        worst = float(split[frame])
        over = int(np.sum(split > limit))
        numbers[clip] = {"worst_degrees": round(worst, 1), "frame": frame, "frames_over_limit": over, "final_degrees": round(float(split[-1]), 1),
                         "limit": limit, "rest_degrees": round(float(rest), 1)}
        if worst > limit:
            out.append({"rule": "TRIPO-DEATH-SPLAY", "subject": clip,
                        "message": f"the thighs split {worst:.0f} degrees apart in frame {frame} (limit {limit:g}: the rest pose's {rest:.1f} plus {OPENING_LIMIT:g}, "
                                   f"at least {SPLIT_LIMIT:g}, vanilla's deaths {VANILLA_DEATH_SPLIT:g}), "
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
    closing: dict = field(default_factory=dict)  # the legs closed at the hips: share, largest turn, ramp


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


def _frame_check(mesh, anim, edges, rest, body, masks: Sequence[np.ndarray] = ()):
    """(frames, 3) the kit's deformation per frame (stretched, squashed, largest growth) and (frames,) how far the ground pass lifts each frame
    (share of the height), from one skinning pass."""

    matrices = pdx_deform.skinning_matrices(mesh, anim)
    ground = float(mesh.positions[:, 1].min())
    height = max(mesh.height, 1e-6)
    deformed = np.zeros((matrices.shape[0], 3))
    lifts = np.zeros(matrices.shape[0])
    lows = np.zeros((matrices.shape[0], len(masks)))
    for frame in range(matrices.shape[0]):
        posed = pdx_deform.skin(mesh, matrices[frame])
        s, q, g = stretch_smooth._deformed(rest, np.linalg.norm(posed[edges[:, 0]] - posed[edges[:, 1]], axis=1), height)
        deformed[frame] = (s.sum(), q.sum(), g.max())
        lifts[frame] = max(0.0, ground - float(posed[body, 1].min())) / height
        for k, mask in enumerate(masks):
            lows[frame, k] = float(posed[mask, 1].min()) - ground if mask.any() else np.inf
    return (deformed, lifts, lows) if len(masks) else (deformed, lifts)


def _closed(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, legs, turns: np.ndarray) -> pdx_deform.Animation:
    """`anim` with each whole leg turned `turns[frame, leg]` degrees about its hip joint toward the other thigh, about the line square to both
    thighs: the split closes in the plane the two thighs span, the knee, the shin and the foot following the thigh. A lying body's thighs span
    the ground, so its legs slide together along it."""

    rotations, positions = tripo_pose._world_rotations(mesh, anim)
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    for leg in legs:
        channels[mesh.bones[leg.hip]]["q"] = anim.channels[mesh.bones[leg.hip]]["q"].copy()
    for frame in range(anim.frames):
        a = positions[frame, legs[0].knee] - positions[frame, legs[0].hip]
        b = positions[frame, legs[1].knee] - positions[frame, legs[1].hip]
        axis = np.cross(a, b)
        if np.linalg.norm(axis) < 1e-9:
            continue
        axis = axis / np.linalg.norm(axis)
        for k, (leg, sign) in enumerate(zip(legs, (1.0, -1.0))):
            degrees = float(turns[frame, k])
            if abs(degrees) < 1e-9:
                continue
            # the first thigh turned about a x b moves toward the second, the second about -(a x b) toward the first
            turn = tripo_pose._axis_angle(axis, sign * degrees)
            parent = mesh.parents[leg.hip]
            frame_of_parent = rotations[frame, parent] if parent >= 0 else np.eye(3)
            q = channels[mesh.bones[leg.hip]]["q"]
            new = tripo_pose._quaternion_from_matrix(frame_of_parent.T @ turn @ frame_of_parent @ pdx_deform._quaternion_matrices(q[frame][None])[0])
            q[frame] = new if float(new @ q[frame]) >= 0 else -new
    return pdx_deform.Animation(anim.fps, anim.frames, channels)


def closing_need(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, legs, target: float) -> np.ndarray:
    """(frames, 2) degrees: for each frame whose thighs split past `target`, each leg's part (`_parts`) of the excess, which `_closed` turns it."""

    posed = pdx_motion.posed_joints(mesh, anim)
    excess = np.maximum(thigh_split(mesh, anim) - target, 0.0)
    return _parts(mesh, posed, legs) * excess[:, None]


def lower_leg_masks(mesh: pdx_deform.SkinnedMesh, legs) -> List[np.ndarray]:
    """Per leg, the skin its knee joint and every joint below it move most: the shin and the foot, which a standing, kneeling or falling body
    stands on."""

    dominant = pdx_deform.dominant_bones(mesh)
    return [np.isin(dominant, tripo_pose._subtree(mesh.parents, leg.knee)) for leg in legs]


def _contacts_kept(lows_before: np.ndarray, lift_before: np.ndarray, lows: np.ndarray, lifts: np.ndarray, height: float) -> np.ndarray:
    """(frames,) True where the ground pass's lift after the closing leaves every lower leg that stood on the ground before (within
    `CONTACT_SHARE`) within `tripo_pose.UPPER_SETTLE_LIFT` of where it stood, and lifts the body no more than `CLOSE_LIFT_MAX`. Closing two
    planted legs lowers both feet alike, and the lift that answers it keeps both on the ground: the body stands a little straighter."""

    before = lows_before / height + lift_before[:, None]
    after = lows / height + lifts[:, None]
    standing = before <= CONTACT_SHARE
    kept = np.where(standing, after <= before + tripo_pose.UPPER_SETTLE_LIFT + 1e-9, True).all(axis=1)
    return kept & (lifts <= lift_before + CLOSE_LIFT_MAX + 1e-9)


def _segment_gap(a0: np.ndarray, a1: np.ndarray, b0: np.ndarray, b1: np.ndarray, samples: int = 9) -> float:
    t = np.linspace(0.0, 1.0, samples)[:, None]
    p, q = a0 + t * (a1 - a0), b0 + t * (b1 - b0)
    return float(np.linalg.norm(p[:, None] - q[None], axis=2).min())


def leg_radii(mesh: pdx_deform.SkinnedMesh, legs) -> np.ndarray:
    """(2, 2) each leg's thigh and shin radius: the median distance of the skin each bone moves most from its segment at rest."""

    rest = pdx_motion.rest_joints(mesh)
    dominant = pdx_deform.dominant_bones(mesh)
    out = np.zeros((2, 2))
    for k, leg in enumerate(legs):
        for j, (bone, a, b) in enumerate(((leg.hip, leg.hip, leg.knee), (leg.knee, leg.knee, leg.ankle))):
            points = mesh.positions[dominant == bone]
            if not len(points):
                continue
            ab = rest[b] - rest[a]
            t = np.clip((points - rest[a]) @ ab / max(float(ab @ ab), 1e-12), 0.0, 1.0)
            out[k, j] = float(np.median(np.linalg.norm(points - (rest[a] + t[:, None] * ab), axis=1)))
    return out


def leg_gaps(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, legs) -> np.ndarray:
    """(frames, 2) the least distance between the two thighs and between the two shins (joint segments) in each frame."""

    posed = pdx_motion.posed_joints(mesh, anim)
    out = np.zeros((anim.frames, 2))
    l, r = legs
    for frame in range(anim.frames):
        p = posed[frame]
        out[frame, 0] = _segment_gap(p[l.hip], p[l.knee], p[r.hip], p[r.knee])
        out[frame, 1] = _segment_gap(p[l.knee], p[l.ankle], p[r.knee], p[r.ankle])
    return out


def _eased(mesh, anim, legs, need: np.ndarray, apply, frame_ok, checked: bool = False):
    """(weights, turn, result, ramp) of the highest smooth share of `need` that `apply` may use in each frame while `frame_ok` (the trial clip
    to a (frames,) mask) allows it, or None when no frame may take any. By default a share counts in a frame only while every smaller one is
    allowed there too, so any share the smooth curve gives it is allowed. `checked` instead takes each frame's highest allowed share and then
    checks the curve itself: a frame it fails is capped at its next allowed share below the curve, and the curve is drawn again
    (`CHECK_ROUNDS` at most). Two edges more at a small share and none at a larger one (the ogre's fall, frame 28) then no longer stop it."""

    need = np.stack([tripo_trim.smooth(need[:, k], SMOOTH_FRAMES) for k in range(2)], axis=1)
    allowed = np.stack([frame_ok(apply(mesh, anim, legs, share * need)) for share in SHARES])
    if not checked:
        allowed = np.logical_and.accumulate(allowed, axis=0)
    allowed[0] = True
    moving = np.abs(need).max(axis=1) > 0
    highest = np.array([SHARES[np.nonzero(allowed[:, f])[0].max()] for f in range(len(need))])
    cap = np.where(moving, highest, 0.0) if checked else np.where(moving, SHARES[np.maximum(allowed.sum(axis=0) - 1, 0)], 0.0)
    if not cap.any():
        return None
    ramp = max(tripo_trim.settle_frames(float(np.abs(need).max())), MIN_RAMP_FRAMES)
    weights = _envelope(cap, ramp)
    for _round in range(CHECK_ROUNDS if checked else 0):
        ok = frame_ok(apply(mesh, anim, legs, weights[:, None] * need))
        if ok.all():
            break
        for f in np.nonzero(~ok)[0]:
            below = [share for k, share in enumerate(SHARES) if allowed[k, f] and share < weights[f] - 1e-9]
            cap[f] = max(below) if below else 0.0
        if not cap.any():
            return None
        weights = _envelope(cap, ramp)
    turn = weights[:, None] * need
    return weights, turn, apply(mesh, anim, legs, turn), ramp


@dataclass
class _Clip:
    """What the two passes of `close_death_legs` judge each trial against: the clip before, on its mesh."""

    mesh: pdx_deform.SkinnedMesh
    legs: tuple
    edges: np.ndarray
    rest: np.ndarray
    body: np.ndarray
    masks: List[np.ndarray]
    deformed: np.ndarray
    lift_before: np.ndarray
    lows_before: np.ndarray

    def swing_ok(self, trial: pdx_deform.Animation) -> np.ndarray:
        frames, lifts = _frame_check(self.mesh, trial, self.edges, self.rest, self.body)
        return _frame_within(frames, self.deformed) & (lifts <= self.lift_before + tripo_pose.UPPER_SETTLE_LIFT + 1e-9)

    def close_ok(self, trial: pdx_deform.Animation, gaps_floor: np.ndarray) -> np.ndarray:
        frames, lifts, lows = _frame_check(self.mesh, trial, self.edges, self.rest, self.body, self.masks)
        gaps = (leg_gaps(self.mesh, trial, self.legs) >= gaps_floor - 1e-6).all(axis=1)
        kept = _contacts_kept(self.lows_before, self.lift_before, lows, lifts, max(self.mesh.height, 1e-6))
        return _frame_within(frames, self.deformed) & kept & gaps


@dataclass
class _Passes:
    """The clip as the passes leave it, with what they turned."""

    current: pdx_deform.Animation
    turn: np.ndarray
    changed: np.ndarray
    weights_max: float = 0.0
    ramp_max: int = 0
    closing: dict = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def take(self, weights: np.ndarray, turn: np.ndarray, result: pdx_deform.Animation, ramp: int) -> None:
        self.current = result
        self.turn = self.turn + np.abs(turn)
        self.weights_max, self.ramp_max = max(self.weights_max, float(weights.max())), max(self.ramp_max, ramp)
        self.changed = self.changed | (np.abs(turn).max(axis=1) > 0)


def _swing_pass(clip: _Clip, anim: pdx_deform.Animation, target: float, worst: float, out: _Passes) -> None:
    swing = _eased(clip.mesh, anim, clip.legs, needed_turns(clip.mesh, anim, clip.legs, target), _swung, clip.swing_ok)
    if swing is None:
        out.notes.append("no share swings the knees together within the kit's rules")
    elif float(thigh_split(clip.mesh, swing[2]).max()) >= worst - 1e-3:
        out.notes.append("swinging the knees together does not lower the worst split")
    else:
        out.take(*swing)


def _closing_passes(clip: _Clip, limit: float, target: float, out: _Passes) -> None:
    mesh, legs = clip.mesh, clip.legs
    floor = np.minimum(leg_gaps(mesh, out.current, legs), LEG_CLEARANCE * leg_radii(mesh, legs).sum(axis=0)[None])  # thighs, shins
    for done in range(CLOSE_PASSES):
        # a pass closes what it can of each frame's excess; the smoothing and the ramp leave some at a sharp peak, so the next pass goes on
        now = float(thigh_split(mesh, out.current).max())
        if now <= limit:
            return
        close = _eased(mesh, out.current, legs, closing_need(mesh, out.current, legs, target), _closed,
                       lambda trial: clip.close_ok(trial, floor), checked=True)
        if close is None:
            out.notes.append("no share closes the legs within the kit's rules")
            return
        if float(thigh_split(mesh, close[2]).max()) >= now - 1e-3:
            out.notes.append("closing the legs does not lower the worst split")
            return
        weights, turn, _result, ramp = close
        out.closing = {"passes": done + 1, "share": round(max(float(weights.max()), out.closing.get("share", 0.0)), 3),
                       "largest_turn_degrees": round(float(np.abs(turn).max()) + out.closing.get("largest_turn_degrees", 0.0), 1),
                       "ramp_frames": int(max(ramp, out.closing.get("ramp_frames", 0)))}
        out.take(*close)


def close_death_legs(mesh_path: Path, anim_path: Path, out_path: Path, exclude_bones: Sequence[str] = (), limit: Optional[float] = None,
                     target: Optional[float] = None) -> SplayEase:
    """Write `out_path`: `anim_path` with the knees swung toward each other where a death splits the thighs past `limit` (this body's
    `split_limit` by default), then, where they still split past it, the legs closed together at the hips (`_closed`), the two legs never
    nearer than `LEG_CLEARANCE` of their radii unless they already were (see the module text). Unchanged, and copied as it is, when the clip
    passes or no share closes them within the kit's rules."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    limit = split_limit(mesh) if limit is None else limit
    target = split_target(mesh) if target is None else target

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
    masks = lower_leg_masks(mesh, legs)
    clip = _Clip(mesh, tuple(legs), edges, rest, body, masks, *_frame_check(mesh, anim, edges, rest, body, masks))
    passes = _Passes(anim, np.zeros((anim.frames, 2)), np.zeros(anim.frames, bool))
    _swing_pass(clip, anim, target, worst, passes)
    _closing_passes(clip, limit, target, passes)
    if passes.current is anim:
        return unchanged("; ".join(passes.notes), worst)
    after = float(thigh_split(mesh, passes.current).max())
    frames_after, lifts_after, lows_after = _frame_check(mesh, passes.current, edges, rest, body, masks)
    if stretch_smooth.worse(tripo_shoulder.summary(clip.deformed), tripo_shoulder.summary(frames_after)):
        return unchanged("closing the legs makes the clip's deformation worse", worst)
    if passes.closing:
        sunk = not _contacts_kept(clip.lows_before, clip.lift_before, lows_after, lifts_after, max(mesh.height, 1e-6)).all()
    else:
        sunk = float((lifts_after - clip.lift_before).max()) > tripo_pose.UPPER_SETTLE_LIFT + 1e-6
    if sunk:
        return unchanged("closing the legs sinks the body into the ground or lifts a planted leg off it", worst)
    tripo_pose._write_rotations(data, keyed, joints, passes.current, passes.changed.astype(float))
    Path(out_path).write_bytes(bytes(data))
    turn = passes.turn
    step = float(np.abs(np.diff(turn, axis=0)).max()) if len(turn) > 1 else 0.0
    return SplayEase(True, round(passes.weights_max, 3), int(passes.changed.sum()), int(passes.ramp_max), round(worst, 1), round(after, 1),
                     round(float(turn.max()), 1), round(step, 1), "; ".join(passes.notes), passes.closing)
