"""A leg that kicks up once a Tripo death lies down: its measure, its check (TRIPO-DEATH-LEG-KICK) and the settle that keeps the boot down.

Two fresh reviewers of the zombie's death (zombie_o, the text-to-motion "A standing soldier is shot", 2026-11-18) saw one leg flick straight up
after the body had landed flat on its front, frames 67 to 76, the boot pointing at the sky over the buttocks, and the pelvis, the buttocks and
the upper thigh stretched hard (one major, one minor). It drops back by frame 84. Every automated check passed.

What does it. Tripo's clip itself rolls the left thigh about its own length by about 250 degrees while the knee twists back against it, in nine
frames at 24 a second (source frames 48 to 57, the knee 68.5 degrees in one frame). Fast, the roll barely shows. The intake's snap ease
(`tripo/prepare_tripo_unit.py --ease-snaps`, `lib/tripo_ease.py`) retimes such a step along the joint's own path so no frame turns faster than
the spin check allows, and it spread this one over source frames 32 to 63 (export frames 40 to 79). Slowed down, the roll carries the bent shin
round the thigh and up over the back of the lying body: in the exported clip before the death settles the left boot (`boot_heights`) sinks to
0.117 of the height at frame 65 and climbs to 0.169 at frame 73, and the thigh, rolled past 170 degrees there, twists the hip's skin. The legs'
settle (`tripo_pose.settle_death_legs`) then turned the knees 0.4 of the way toward rest from frame 63, for the boots' end height only: the climb
fell to 0.039, still there.

The measure (`boot_heights`, `kick_numbers`): once the hips are down (`lifted_lying_frame`: `tripo_pose._lying_frame` on the body as the
ground pass will lift it, so the settle before the ground pass and the check after it read the same frame), each leg's boot, the higher of its ankle and toe
joints, above the ground as the ground pass will lift the body, as a share of the height, and its largest rise above the lowest it has been since
the hips came down: a leg that has come down and goes up again. Vanilla's two deaths (death_rifle and death_mg on GER_infantry, _alt_0,
ENG_infantry and _snow, 2026-11-18, the skeleton the same on all four) raise a boot at most 0.027 that way (death_mg's left boot on ENG_infantry,
0.021 on _alt_0, 0.018 on GER_infantry). The limit is that worst with a quarter added (`BOOT_RISE_LIMIT`, 0.034). zombie_o's exported death reads
0.039 on the left leg. The boot's height itself is reported, not judged: lifted out of the ground vanilla's own boots stand 0.13 to 0.22 of the
height up at the frame the hips come down, and a body landing on its front still lowers its shins after that frame (zombie_o's right boot 0.134
at frame 63), which is no kick. The knee is not judged: vanilla's knees rise 0.05 as a body on its back draws its legs up.

Tried and dropped (offline on zombie_o's exported clip, 2026-11-18): turning the knee, the thigh or both toward the rest pose (the legs' settle's
target) by a share, from the frame the hips come down; with the thigh rolled 170 to 250 degrees the turn toward rest unrolls it as well and swings
the boot about, the rise 0.03 to 0.09. Bounding the thigh's roll about its own length (vanilla's deaths roll it at most 52 degrees, the knee 30)
halves the deformed edges but swings the end pose's shin and boot by 0.1 to 0.13 of the height, and the body lifted out of the ground under the
swung leg raises the other boot to 0.21. Straightening the knee and the thigh without their roll lowers the boot to a rise of 0.022 at full share
but grows the worst edge past the kit's rule.

Also tried: carrying each joint of the leg straight across the kick by a slerp of its own rotation. Each joint takes the short way but the
four together still swing the boot round the rolled thigh, up to 0.20 of the height.

The settle (`settle_death_kick`, run by `run_pilot.ground_exported_clip` after the legs' settle and before the upper body's): for a leg whose rise
breaks the limit, the span from its boot's lowest before the peak (`kick_span`) to the first frame after the peak where the boot is back within
the target (vanilla's worst) of that low is laid across (`laid_across`): in each frame between, the directions from the hip joint to the knee and
from the knee to the ankle move evenly, in the world, between the span's two ends, and the thigh, the shank and the foot turn the short way between
their ends (in the frame of the bone the leg hangs from), each then turned onto its direction. Both ends lie on the ground, so the boot goes from
one lying place to the next instead of round the thigh. The span grows `SPAN_STEP` frames at a time at its end while the rise is still over the
target or a joint would turn faster than the settle rule allows (`tripo_trim.SETTLE_MAX_RATE`). A span is not taken when it makes the frames from
its start worse than the clip before by the kit's rule (`stretch_smooth.worse`) or sinks the body further into the ground than the upper-body
settle may lift it. Offline on zombie_o's clip it lays the left leg across frames 63 to 79: the rise falls from 0.039 to 0.016, the boot's peak
from 0.156 to 0.122, and the kit's deformation report reads 266 stretched and 422 squashed edges against 265 and 418 before (within the rule).
Frames 70 to 76 squash more than before (348 against 283 at frame 70) while staying under the clip's worst frame.

A share of the way (2026-11-18). The route fits the weights to the unit's own clips, so another retreat or attack changes the skin the death
is judged on. With the loop window's retreat (zombie_s) the same death's worst frame squashed 288 edges where zombie_p's squashed 418, and the
full lay across (297 squashed, the body 1.2% into the ground) broke both guards that zombie_p's passed: the kick stayed at 0.0385 and failed the
check. Where the full lay across breaks a guard, the leg is carried a share of the way instead (`part_way`): each of its joints a slerp from
its own rotation toward the laid one, in steps of `SHARE_STEP` down from the whole, and the share that passes both guards with the lowest rise
is taken. On zombie_s half the way passes (294 squashed, 0.4% into the ground) with the rise at 0.028.

Maths on the exported `.mesh` and `.anim` (`pdx_deform`), no Blender.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, stretch_smooth, tripo_ease, tripo_fall, tripo_pose, tripo_trim
from .pdx_binary import read

VANILLA_BOOT_RISE = 0.027
BOOT_RISE_LIMIT = round(1.25 * VANILLA_BOOT_RISE, 3)
BOOT_RISE_TARGET = VANILLA_BOOT_RISE
SPAN_STEP = 3
SHARE_STEP = 0.1
MAX_PASSES = 3


def _legs(mesh: pdx_deform.SkinnedMesh):
    legs = pdx_motion.find_legs(mesh)
    if len(legs.legs) != 2 or legs.pelvis < 0 or any(leg.knee < 0 or leg.ankle < 0 for leg in legs.legs):
        return None
    return legs


def _body_mask(mesh: pdx_deform.SkinnedMesh, exclude_bones: Sequence[str]) -> np.ndarray:
    excluded = [i for i, name in enumerate(mesh.bones) if name in set(exclude_bones)]
    return ~np.isin(pdx_deform.dominant_bones(mesh), excluded) if excluded else np.ones(len(mesh.positions), bool)


def _lifts(mesh: pdx_deform.SkinnedMesh, matrices: np.ndarray, body: np.ndarray) -> np.ndarray:
    """Per frame, how far the ground pass lifts the body (its lowest point under the rest ground), in the mesh's units."""

    ground = float(mesh.positions[:, 1].min())
    return np.array([max(0.0, ground - float(pdx_deform.skin(mesh, matrices[f])[body, 1].min())) for f in range(matrices.shape[0])])


def boot_heights(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, exclude_bones: Sequence[str] = (), legs=None) -> Optional[np.ndarray]:
    """(F, 2): per frame, each leg's boot (the higher of its ankle and toe joints) above the ground once the ground pass lifts the body out of
    it, as a share of the height. None without two legs."""

    legs = legs or _legs(mesh)
    if legs is None:
        return None
    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    joints = (matrices @ np.linalg.inv(mesh.inverse_bind)[None])[..., :3, 3]
    lift = _lifts(mesh, matrices, _body_mask(mesh, exclude_bones))
    out = np.zeros((anim.frames, 2))
    for side, leg in enumerate(legs.legs):
        ends = [leg.ankle] + ([leg.toe] if leg.toe is not None and leg.toe >= 0 else [])
        out[:, side] = (joints[:, ends, 1].max(axis=1) + lift - ground) / height
    return out


def lifted_lying_frame(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, pelvis: int, exclude_bones: Sequence[str] = ()) -> int:
    """`tripo_pose._lying_frame` on the body as the ground pass will lift it, as `boot_heights` judges the boots: the first frame from which
    the hips stay within `LYING_HIPS_SETTLE` of where they end. Before the ground pass the raw hips come down earlier than the lifted ones (the
    D-94 zombie, 2026-11-21: frame 47 against 65), so the settle laid a rise across from frame 47 that the check, after the ground pass, read
    from frame 65 as a boot climbing 3.7% to the end. On a grounded clip the lift is nil and the frame is `_lying_frame`'s."""

    posed = pdx_motion.posed_joints(mesh, anim)
    ground = float(mesh.positions[:, 1].min())
    lift = _lifts(mesh, pdx_deform.skinning_matrices(mesh, anim), _body_mask(mesh, exclude_bones))
    share = (posed[:, pelvis, 1] + lift - ground) / max(mesh.height, 1e-6)
    off = np.nonzero(np.abs(share - share[-1]) > tripo_pose.LYING_HIPS_SETTLE)[0]
    return int(min(off[-1] + 1, anim.frames - 1)) if len(off) else 0


def _leg_key(mesh: pdx_deform.SkinnedMesh, leg, side: int) -> str:
    name = mesh.bones[leg.knee].lower()
    return "left" if "left" in name else "right" if "right" in name else f"leg{side}"


def kick_numbers(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, exclude_bones: Sequence[str] = (), legs=None) -> Optional[dict]:
    """The hips-down frame (`onset`) and, per leg (`left`/`right` by the knee bone's name, else `leg0`/`leg1`), the boot's highest since then
    (`height`) and its largest rise above its lowest since then (`rise`), with their frames. None without two legs."""

    legs = legs or _legs(mesh)
    if legs is None:
        return None
    boots = boot_heights(mesh, anim, exclude_bones, legs)
    onset = lifted_lying_frame(mesh, anim, legs.pelvis, exclude_bones)
    out = {"onset": onset, "legs": {}}
    for side, leg in enumerate(legs.legs):
        track = boots[onset:, side]
        rise = track - np.minimum.accumulate(track)
        out["legs"][_leg_key(mesh, leg, side)] = {"height": round(float(track.max()), 4), "height_frame": onset + int(track.argmax()),
                                                  "rise": round(float(rise.max()), 4), "rise_frame": onset + int(rise.argmax())}
    return out


def kick_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    """TRIPO-DEATH-LEG-KICK on each death clip of a body with two legs."""

    out, numbers = [], {}
    legs = _legs(mesh)
    if legs is None:
        return out, numbers
    for clip, anim in anims.items():
        if tripo_pose.role_of(clip) != "death":
            continue
        row = kick_numbers(mesh, anim, legs=legs)
        numbers[clip] = row
        for key, leg in row["legs"].items():
            if leg["rise"] > BOOT_RISE_LIMIT:
                out.append({"rule": "TRIPO-DEATH-LEG-KICK", "subject": clip,
                            "message": f"once the hips are down (frame {row['onset']}) the {key} boot rises {leg['rise']:.1%} of the height above "
                                       f"where it had come down (frame {leg['rise_frame']}, up to {leg['height']:.1%} above the ground; limit "
                                       f"{BOOT_RISE_LIMIT:.1%}, vanilla's deaths {VANILLA_BOOT_RISE:.1%}): a leg kicks up from the lying body",
                            "leg": key, "rise": leg["rise"], "height": leg["height"]})
    return out, numbers


@dataclass
class KickSettle:
    changed: bool
    onset: int = 0
    spans: dict = field(default_factory=dict)  # leg: [first, last] frames carried straight
    before: dict = field(default_factory=dict)
    after: dict = field(default_factory=dict)
    note: str = ""


def _chain(mesh: pdx_deform.SkinnedMesh, leg) -> List[str]:
    return [mesh.bones[j] for j in (leg.hip, leg.knee, leg.ankle, leg.toe) if j is not None and j >= 0]


def _slerp_matrix(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    qa, qb = tripo_pose._quaternion_from_matrix(a), tripo_pose._quaternion_from_matrix(b)
    q = tripo_ease.slerp(qa, qb, t)
    return pdx_deform._quaternion_matrices(q[None])[0][:3, :3]


def laid_across(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, leg, first: int, last: int) -> pdx_deform.Animation:
    """`anim` with the leg laid from its pose at `first` to its pose at `last` in the frames between, in the frame of the bone the leg hangs
    from: the knee's and the ankle's directions from the joint above them move evenly between the two ends (so the boot goes from one lying
    place to the next and not round the thigh), and the thigh, the shank and the foot turn the short way between their two ends, each then
    turned onto its direction. The hip joint stays where the clip has it."""

    rotations, positions = tripo_pose._world_rotations(mesh, anim)
    parent = mesh.parents[leg.hip]
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    for joint in (leg.hip, leg.knee, leg.ankle):
        channels[mesh.bones[joint]]["q"] = anim.channels[mesh.bones[joint]]["q"].copy()

    def framed(frame: int):
        base = rotations[frame, parent] if parent >= 0 else np.eye(3)
        thigh, shank, foot = (base.T @ rotations[frame, j] for j in (leg.hip, leg.knee, leg.ankle))
        upper = positions[frame, leg.knee] - positions[frame, leg.hip]
        lower = positions[frame, leg.ankle] - positions[frame, leg.knee]
        return thigh, shank, foot, upper, lower

    start, end = framed(first), framed(last)
    for frame in range(first + 1, last):
        t = (frame - first) / max(last - first, 1)
        base = rotations[frame, parent] if parent >= 0 else np.eye(3)
        upper = (1 - t) * start[3] + t * end[3]
        lower = (1 - t) * start[4] + t * end[4]
        thigh = base @ _slerp_matrix(start[0], end[0], t)
        thigh = tripo_fall._arc(thigh @ (rotations[first, leg.hip].T @ (positions[first, leg.knee] - positions[first, leg.hip])), upper) @ thigh
        shank = base @ _slerp_matrix(start[1], end[1], t)
        shank = tripo_fall._arc(shank @ (rotations[first, leg.knee].T @ (positions[first, leg.ankle] - positions[first, leg.knee])), lower) @ shank
        foot = base @ _slerp_matrix(start[2], end[2], t)
        for joint, matrix in ((leg.hip, base.T @ thigh), (leg.knee, thigh.T @ shank), (leg.ankle, shank.T @ foot)):
            new = tripo_pose._quaternion_from_matrix(matrix)
            old = anim.channels[mesh.bones[joint]]["q"][frame]
            channels[mesh.bones[joint]]["q"][frame] = new if float(new @ old) >= 0 else -new
    return pdx_deform.Animation(anim.fps, anim.frames, channels)


def part_way(mesh: pdx_deform.SkinnedMesh, current: pdx_deform.Animation, laid: pdx_deform.Animation, leg, share: float) -> pdx_deform.Animation:
    """`current` with the leg's joints carried `share` of the way to their rotations in `laid` (a slerp per frame, each joint the short way)."""

    channels = {name: dict(channel) for name, channel in current.channels.items()}
    for name in _chain(mesh, leg):
        if name in channels and name in laid.channels:
            own, other = current.channels[name]["q"], laid.channels[name]["q"]
            channels[name]["q"] = np.array([tripo_pose.slerp(own[f], other[f], share) for f in range(len(own))])
    return pdx_deform.Animation(current.fps, current.frames, channels)


def _fastest_step(anim: pdx_deform.Animation, joints: Sequence[str], first: int, last: int) -> float:
    return max((tripo_ease.step_degrees(anim.channels[j]["q"][f - 1], anim.channels[j]["q"][f]) for j in joints for f in range(first + 1, last + 1)), default=0.0)


def kick_span(boots: np.ndarray, onset: int, target: float) -> Optional[Tuple[int, int]]:
    """(first, last) of the worst kick in one boot's track from `onset`: from the boot's lowest before its largest rise to the first frame after
    it where the boot is back within `target` of that low (the clip's last frame if it never is). None when the rise is within `target`."""

    track = np.asarray(boots, float)[onset:]
    if len(track) < 3:
        return None
    rise = track - np.minimum.accumulate(track)
    peak = int(rise.argmax())
    if rise[peak] <= target:
        return None
    low = int(np.argmin(track[: peak + 1]))
    back = next((k for k in range(peak + 1, len(track)) if track[k] <= track[low] + target), len(track) - 1)
    return onset + low, onset + back


@dataclass
class _Guard:
    """What a span is judged by: the mesh, its edges and rest lengths, the body that may not sink, and the clip's legs."""

    mesh: pdx_deform.SkinnedMesh
    legs: object
    exclude_bones: Sequence[str]
    edges: np.ndarray = None
    rest_lengths: np.ndarray = None
    body: np.ndarray = None

    def __post_init__(self) -> None:
        self.edges = pdx_deform.mesh_edges(self.mesh)
        self.rest_lengths = np.linalg.norm(self.mesh.positions[self.edges[:, 0]] - self.mesh.positions[self.edges[:, 1]], axis=1)
        self.body = _body_mask(self.mesh, self.exclude_bones)

    def deformation(self, clip: pdx_deform.Animation, first: int) -> dict:
        return tripo_pose._tail_deformation(self.mesh, clip, first, self.edges, self.rest_lengths)

    def sink(self, clip: pdx_deform.Animation, first: int) -> float:
        return float(_lifts(self.mesh, pdx_deform.skinning_matrices(self.mesh, clip), self.body)[first:].max()) / max(self.mesh.height, 1e-6)

    def rise(self, clip: pdx_deform.Animation, key: str) -> float:
        return kick_numbers(self.mesh, clip, self.exclude_bones, self.legs)["legs"][key]["rise"]


def _lay_kick(guard: _Guard, current: pdx_deform.Animation, leg, key: str, span: Tuple[int, int], joints: Sequence[str],
              target: float) -> Optional[Tuple[float, pdx_deform.Animation, int]]:
    """(rise, clip, last frame) of the best span from `span`, grown at its end while the rise is over `target` or a joint turns too fast, or
    None when no span is allowed (see the module text)."""

    first, last = span
    end = current.frames - 1
    reference, sunk = guard.deformation(current, first), guard.sink(current, first)
    best = None

    def allowed(clip: pdx_deform.Animation) -> bool:
        return not (stretch_smooth.worse(reference, guard.deformation(clip, first)) or guard.sink(clip, first) > sunk + tripo_pose.UPPER_SETTLE_LIFT)

    while True:
        trial = laid_across(guard.mesh, current, leg, first, last)
        if _fastest_step(trial, joints, first, last) <= tripo_trim.SETTLE_MAX_RATE:
            if not allowed(trial):
                # The whole lay across breaks a guard: the leg goes a share of the way, the share with the lowest rise that passes.
                for share in np.arange(1.0 - SHARE_STEP, SHARE_STEP / 2, -SHARE_STEP):
                    part = part_way(guard.mesh, current, trial, leg, float(share))
                    if allowed(part):
                        rise = guard.rise(part, key)
                        if best is None or rise < best[0] - 1e-4:
                            best = (rise, part, last)
                break
            rise = guard.rise(trial, key)
            if best is None or rise < best[0] - 1e-4:
                best = (rise, trial, last)
            if rise <= target:
                break
        if last >= end:
            break
        last = min(last + SPAN_STEP, end)
    return best


def settle_death_kick(mesh_path: Path, anim_path: Path, out_path: Path, exclude_bones: Sequence[str] = (),
                      limit: float = BOOT_RISE_LIMIT, target: float = BOOT_RISE_TARGET) -> KickSettle:
    """Write `out_path`: `anim_path` with each kick of a leg over `limit` laid across (`laid_across`, see the module text). Only that leg's
    rotation samples inside the span change."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    legs = _legs(mesh)
    before = kick_numbers(mesh, anim, exclude_bones, legs) if legs else None
    if before is None or all(leg["rise"] <= limit for leg in before["legs"].values()):
        Path(out_path).write_bytes(bytes(data))
        if before is None:
            return KickSettle(False, note="no two legs found")
        return KickSettle(False, before["onset"], before=before, after=before, note="no boot kicks up once the hips are down")
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    guard = _Guard(mesh, legs, exclude_bones)
    onset = before["onset"]
    current, spans, changed = anim, {}, []
    for _ in range(MAX_PASSES):
        boots = boot_heights(mesh, current, exclude_bones, legs)
        numbers = kick_numbers(mesh, current, exclude_bones, legs)
        progressed = False
        for side, leg in enumerate(legs.legs):
            key = _leg_key(mesh, leg, side)
            span = kick_span(boots[:, side], onset, target) if numbers["legs"][key]["rise"] > limit else None
            joints = [j for j in _chain(mesh, leg) if j in keyed]
            best = _lay_kick(guard, current, leg, key, span, joints, target) if span and joints else None
            if best is not None and best[0] < numbers["legs"][key]["rise"] - 1e-4:
                current = best[1]
                spans.setdefault(key, []).append([span[0], best[2]])
                changed += [j for j in joints if j not in changed]
                progressed = True
        if not progressed:
            break
    if not changed:
        Path(out_path).write_bytes(bytes(data))
        return KickSettle(False, onset, before=before, after=before, note="no span laid across lowers the kick without stretching the clip more")
    weights = np.zeros(anim.frames)
    for ranges in spans.values():
        for first, last in ranges:
            weights[first + 1:last] = 1.0
    tripo_pose._write_rotations(data, keyed, changed, current, weights)
    Path(out_path).write_bytes(bytes(data))
    return KickSettle(True, onset, spans, before, kick_numbers(mesh, current, exclude_bones, legs))
