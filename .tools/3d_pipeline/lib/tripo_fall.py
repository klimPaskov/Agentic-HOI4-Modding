"""The fall of a Tripo death: the hips must come down like a falling body, not hold themselves up (TRIPO-DEATH-HOVER).

No Blender: everything reads and writes the exported `.mesh` and `.anim` with `pdx_deform`, as the game does.

Tripo's death clips hold the hips up while the legs fold. The zombie (2026-11-18) sat on an invisible chair for about 17 frames, the pelvis at
34% of the height with the feet 27% of the height in front of it, before it dropped. The demon knelt in mid-air, knees and feet 15% above
the ground. Fresh reviewers named both major. The lowest vertex of the whole body is on the ground in both (a foot, a wing tip), so the
fall is measured on what holds the body up.

Measure (`hover_track`). The body's support is its legs and its pelvis (the skin bound to the pelvis bone and to each hip's subtree).
A support vertex at height y and horizontal distance d from the pelvis joint offers the height y + max(0, d - r), `r` being the
distance between the two hips (a foot far in front of the hips does not hold them up). The hover is the lowest such height over the support
vertices, a share of the unit's height, per frame: 0 when something under the hips touches the ground.

Fall time (`hover_spans`, `fall_ratio`). A body that is unsupported falls: the pelvis drops the hover's height in the time free fall takes,
sqrt(2 * hover / g) (`FALL_G`: 9.81 m/s^2 at 30 frames a second for a 1.8 m body, in shares of the height a frame squared). A span is a run of frames
whose hover is over `HOVER_FREE`. Its ratio is its length over the free fall time of its peak. Vanilla's GER infantry deaths (death_mg, death_rifle
on GER_infantry, 2026-11-18) measure their own falling spans at 1.3 to 1.5, a body that falls the way gravity says. The limit is that worst with a
quarter added. The zombie's measured 2.3 and the demon's 2.4. A span of fewer than `HOVER_FRAMES_MIN` frames is a stumble, not a hold.
Only spans that begin before the body lies (`tripo_pose._lying_frame`) count, since a lying body's small hover is TRIPO-DEATH-FEET's.

Settle (`settle_death_fall`). While a span runs, the pelvis follows a free fall from the speed it had (`target`: the speed grows by `FALL_G` a
frame), never lower than the pelvis was, and never by more than the hover (the support is reached, not passed) or than the lowest skin
outside the support (nothing is pushed through the ground). The drop is eased (a three-frame average, never above the raw drop). It is written to
the pelvis's translation, so everything under it, the upper body and the arms, comes down with it. Each leg whose foot stands on the ground keeps
that foot where it stands (a two-bone solve on the thigh and the knee, the foot's own world turn kept, the knee on the side it was), so the
legs fold under the falling hips. A foot in the air comes down with the pelvis, down to the ground at most.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, tripo_pose
from .pdx_binary import read

FALL_G = 0.006  # free fall in shares of the height per frame squared (9.81 m/s^2, 30 fps, a 1.8 m body)
HOVER_FREE = 0.03  # a hover over this share of the height is unsupported
HOVER_FRAMES_MIN = 4  # a span shorter than this is a stumble, not a hold
VANILLA_FALL_RATIO = 1.7  # vanilla GER infantry deaths' worst (death_mg 1.66, death_rifle 1.3), measured 2026-11-18
HOVER_PEAK_MIN = 0.08  # a hover under this share of the height is the thickness of a body that has landed, not a hold
HOVER_RATIO_LIMIT = round(1.25 * VANILLA_FALL_RATIO, 2)
EASE_FRAMES = 3
SOLVE_MARGIN = 1e-4


def support_mask(mesh: pdx_deform.SkinnedMesh, legs: pdx_motion.LegSet, exclude_bones: Sequence[str] = ()) -> np.ndarray:
    """Vertices that hold the body up: bound mostly to the pelvis or to anything under a hip, a dropped weapon left out."""

    dominant = pdx_deform.dominant_bones(mesh)
    bones = {legs.pelvis}
    for leg in legs.legs:
        bones |= set(tripo_pose._subtree(mesh.parents, leg.hip))
    mask = np.isin(dominant, list(bones))
    held = [i for i, name in enumerate(mesh.bones) if name in set(exclude_bones)]
    return mask & ~np.isin(dominant, held) if held else mask


def _footprint(mesh: pdx_deform.SkinnedMesh, legs: pdx_motion.LegSet) -> float:
    rest = pdx_motion.rest_joints(mesh)
    a, b = legs.legs[0].hip, legs.legs[1].hip
    return float(np.linalg.norm((rest[a] - rest[b])[[0, 2]]))


def hover_track(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, exclude_bones: Sequence[str] = ()) -> Optional[np.ndarray]:
    """Per frame, how far the body's support is above the ground (share of the height, see the module text). None for a body without two legs."""

    legs = pdx_motion.find_legs(mesh)
    if len(legs.legs) != 2 or legs.pelvis < 0:
        return None
    support = support_mask(mesh, legs, exclude_bones)
    if not support.any():
        return None
    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    radius = _footprint(mesh, legs)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    posed = pdx_motion.posed_joints(mesh, anim)
    out = np.zeros(anim.frames)
    for frame in range(anim.frames):
        points = pdx_deform.skin(mesh, matrices[frame])[support]
        centre = posed[frame, legs.pelvis]
        away = np.hypot(points[:, 0] - centre[0], points[:, 2] - centre[2])
        out[frame] = float(((points[:, 1] - ground) + np.maximum(0.0, away - radius)).min()) / height
    return out


def hover_spans(track: np.ndarray) -> List[Tuple[int, int, float]]:
    """(first frame, last frame, peak hover) of each run of frames whose hover is over `HOVER_FREE`."""

    spans, start = [], None
    for frame, value in enumerate(track):
        if value > HOVER_FREE and start is None:
            start = frame
        if (value <= HOVER_FREE or frame == len(track) - 1) and start is not None:
            end = frame if value > HOVER_FREE else frame - 1
            spans.append((start, end, float(track[start : end + 1].max())))
            start = None
    return spans


def fall_ratio(start: int, end: int, peak: float) -> float:
    """A span's length over the time a free fall takes to drop its peak."""

    return (end - start + 1) / max(float(np.sqrt(2.0 * peak / FALL_G)), 1.0)


def holds(track: np.ndarray, lying: int) -> List[Tuple[int, int, float, float]]:
    """The spans that begin before the body lies, are at least `HOVER_FRAMES_MIN` long and fall slower than `HOVER_RATIO_LIMIT` allows:
    (first, last, peak, ratio)."""

    out = []
    for start, end, peak in hover_spans(track):
        ratio = fall_ratio(start, end, peak)
        if start < lying and end - start + 1 >= HOVER_FRAMES_MIN and peak >= HOVER_PEAK_MIN and ratio > HOVER_RATIO_LIMIT:
            out.append((start, end, peak, ratio))
    return out


def hover_findings(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, clip: str, row: dict, exclude_bones: Sequence[str] = ()) -> List[dict]:
    """TRIPO-DEATH-HOVER for one death clip (records the worst span's numbers in `row`)."""

    track = hover_track(mesh, anim, exclude_bones)
    if track is None:
        return []
    legs = pdx_motion.find_legs(mesh)
    lying = tripo_pose._lying_frame(mesh, anim, legs.pelvis)
    spans = [(s, e, p, fall_ratio(s, e, p)) for s, e, p in hover_spans(track) if s < lying and e - s + 1 >= HOVER_FRAMES_MIN and p >= HOVER_PEAK_MIN]
    if spans:
        worst = max(spans, key=lambda item: item[3])
        row["fall_hover_peak_share"] = round(worst[2], 4)
        row["fall_hover_frames"] = worst[1] - worst[0] + 1
        row["fall_ratio"] = round(worst[3], 2)
    bad = holds(track, lying)
    if not bad:
        return []
    start, end, peak, ratio = max(bad, key=lambda item: item[3])
    return [tripo_pose._finding("TRIPO-DEATH-HOVER", clip, f"the hips hold themselves up for {end - start + 1} frames from frame {start} with the body's support {peak:.0%} of the height above the ground, {ratio:.1f} times the time a fall takes (limit {HOVER_RATIO_LIMIT:g}, vanilla's deaths fall in {VANILLA_FALL_RATIO:g} times): it reads as a body sitting on air", share=round(peak, 4), ratio=round(ratio, 2), frame=start)]


# ---- the settle ---------------------------------------------------------------------------------------------------------

@dataclass
class FallSettle:
    changed: bool
    note: str = ""
    frames: int = 0
    largest_drop: float = 0.0
    ratio_before: float = 0.0
    ratio_after: float = 0.0
    legs: List[str] = field(default_factory=list)


def target_drop(pelvis: np.ndarray, hover: np.ndarray, room: np.ndarray) -> np.ndarray:
    """Per frame, how far the pelvis comes down (share of the height): a free fall from the speed it had when the hover began, held to the
    hover and to `room` (the lowest skin outside the support), eased."""

    count = len(pelvis)
    level = pelvis.copy()
    speed, falling = 0.0, False
    for frame in range(count):
        if hover[frame] > HOVER_FREE:
            if not falling:
                falling = True
                speed = max(0.0, float(pelvis[max(frame - 3, 0)] - pelvis[frame]) / 3.0)
            speed += FALL_G
            level[frame] = min(pelvis[frame], (level[frame - 1] if frame else pelvis[frame]) - speed)
        else:
            falling = False
    raw = np.clip(pelvis - level, 0.0, None)
    raw = np.minimum(raw, np.maximum(hover, 0.0))
    raw = np.minimum(raw, np.maximum(room, 0.0))
    padded = np.pad(raw, (EASE_FRAMES // 2, EASE_FRAMES - 1 - EASE_FRAMES // 2), mode="edge")
    smooth = np.convolve(padded, np.ones(EASE_FRAMES) / EASE_FRAMES, mode="valid")
    return np.minimum(raw, smooth)


def _arc(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The smallest rotation matrix turning the direction `a` onto `b`."""

    a = a / max(float(np.linalg.norm(a)), 1e-12)
    b = b / max(float(np.linalg.norm(b)), 1e-12)
    axis = np.cross(a, b)
    s = float(np.linalg.norm(axis))
    c = float(a @ b)
    if s < 1e-9:
        if c > 0:
            return np.eye(3)
        helper = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        axis = np.cross(a, helper)
        return tripo_pose._axis_angle(axis / np.linalg.norm(axis), 180.0)
    return tripo_pose._axis_angle(axis / s, float(np.degrees(np.arctan2(s, c))))


def _solve_leg(hip0, knee0, ankle0, shift, held, rot_hip, rot_knee, rot_ankle) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """World rotations of the thigh, the shank and the foot after the hip moved by `shift` and the ankle was kept `held` under where it was."""

    hip = hip0 + shift
    carried = knee0 + shift
    target = ankle0 - np.array([0.0, held, 0.0])
    upper = float(np.linalg.norm(knee0 - hip0))
    lower = float(np.linalg.norm(ankle0 - knee0))
    reach = target - hip
    distance = float(np.clip(np.linalg.norm(reach), abs(upper - lower) + SOLVE_MARGIN * (upper + lower), upper + lower - SOLVE_MARGIN * (upper + lower)))
    along = reach / max(float(np.linalg.norm(reach)), 1e-12)
    pole = (carried - hip) - along * float((carried - hip) @ along)
    if np.linalg.norm(pole) < 1e-9 * (upper + lower):
        pole = np.cross(along, np.array([1.0, 0.0, 0.0]))
        if np.linalg.norm(pole) < 1e-6:
            pole = np.cross(along, np.array([0.0, 0.0, 1.0]))
    pole = pole / np.linalg.norm(pole)
    a = (upper * upper - lower * lower + distance * distance) / (2.0 * distance)
    b = float(np.sqrt(max(upper * upper - a * a, 0.0)))
    knee = hip + along * a + pole * b
    thigh_turn = _arc(knee0 - hip0, knee - hip)
    ankle = knee + (target - knee) / max(float(np.linalg.norm(target - knee)), 1e-12) * lower
    shank_turn = _arc(thigh_turn @ (ankle0 - knee0), ankle - knee)
    return thigh_turn @ rot_hip, shank_turn @ thigh_turn @ rot_knee, rot_ankle


def _room(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, legs: pdx_motion.LegSet, exclude_bones: Sequence[str]) -> np.ndarray:
    """Per frame, the lowest skin outside the support above the ground (share of the height): how far the hips can come down before it goes through."""

    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    support = support_mask(mesh, legs, exclude_bones)
    held = [i for i, name in enumerate(mesh.bones) if name in set(exclude_bones)]
    outside = ~support & ~np.isin(pdx_deform.dominant_bones(mesh), held) if held else ~support
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return np.array([(float(pdx_deform.skin(mesh, matrices[f])[outside, 1].min()) - ground) / height if outside.any() else np.inf for f in range(anim.frames)])


def _lowered(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, legs: pdx_motion.LegSet, drop: np.ndarray) -> Tuple[pdx_deform.Animation, List[str]]:
    """`anim` with the pelvis `drop` (share of the height, per frame) lower and every leg's thigh, knee and foot turned so a foot on the ground stays
    where it stands, a foot in the air coming down with the pelvis. Also the legs' joints whose turn was solved."""

    height = max(mesh.height, 1e-6)
    ground = float(mesh.positions[:, 1].min())
    rotations, positions = tripo_pose._world_rotations(mesh, anim)
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    dominant = pdx_deform.dominant_bones(mesh)
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    pelvis_name = mesh.bones[legs.pelvis]
    parent = mesh.parents[legs.pelvis]
    channels[pelvis_name]["t"] = anim.channels[pelvis_name]["t"].copy()
    feet = [np.isin(dominant, tripo_pose._subtree(mesh.parents, leg.ankle)) for leg in legs.legs]
    for leg in legs.legs:
        for joint in (leg.hip, leg.knee, leg.ankle):
            channels[mesh.bones[joint]]["q"] = anim.channels[mesh.bones[joint]]["q"].copy()
    solved: List[str] = []
    for frame in np.nonzero(drop > 1e-4)[0]:
        lowered = float(drop[frame]) * height
        shift = np.array([0.0, -lowered, 0.0])
        channels[pelvis_name]["t"][frame] = anim.channels[pelvis_name]["t"][frame] + (rotations[frame, parent].T @ shift if parent >= 0 else shift)
        skin_now = pdx_deform.skin(mesh, matrices[frame])
        for leg, mask in zip(legs.legs, feet):
            planted = float(skin_now[mask, 1].min() - ground) if mask.any() else np.inf
            hold = min(lowered, max(planted, 0.0))
            if hold >= lowered - 1e-9:
                continue
            thigh, shank, foot = _solve_leg(positions[frame, leg.hip], positions[frame, leg.knee], positions[frame, leg.ankle], shift, hold,
                                            rotations[frame, leg.hip], rotations[frame, leg.knee], rotations[frame, leg.ankle])
            above = rotations[frame, mesh.parents[leg.hip]].T if mesh.parents[leg.hip] >= 0 else np.eye(3)
            for joint, matrix in ((leg.hip, above @ thigh), (leg.knee, thigh.T @ shank), (leg.ankle, shank.T @ foot)):
                new = tripo_pose._quaternion_from_matrix(matrix)
                old = anim.channels[mesh.bones[joint]]["q"][frame]
                channels[mesh.bones[joint]]["q"][frame] = new if float(new @ old) >= 0 else -new
            solved.append(mesh.bones[leg.hip])
    return pdx_deform.Animation(anim.fps, anim.frames, channels), solved


def _worst_ratio(track: Optional[np.ndarray], lying: int) -> float:
    return max([fall_ratio(*span) for span in hover_spans(track) if span[0] < lying] or [0.0]) if track is not None else 0.0


def settle_death_fall(mesh_path: Path, anim_path: Path, out_path: Path, exclude_bones: Sequence[str] = ()) -> FallSettle:
    """Write `out_path`: `anim_path` with the hips brought down in a free fall wherever the body's support hovers (see the module text)."""

    data = bytearray(Path(anim_path).read_bytes())
    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)

    def unchanged(note: str, ratio: float = 0.0) -> FallSettle:
        Path(out_path).write_bytes(bytes(data))
        return FallSettle(False, note, ratio_before=ratio, ratio_after=ratio)

    legs = pdx_motion.find_legs(mesh)
    hover = hover_track(mesh, anim, exclude_bones)
    if hover is None:
        return unchanged("no two legs and a pelvis found")
    lying = tripo_pose._lying_frame(mesh, anim, legs.pelvis)
    before = _worst_ratio(hover, lying)
    if not holds(hover, lying):
        return unchanged("the body falls as fast as a fall does", before)
    info = read(anim_path).child("info")
    q_keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    t_keyed = [joint.name for joint in info.children if "t" in str((joint.properties.get("sa") or [""])[0])]
    pelvis_name = mesh.bones[legs.pelvis]
    if pelvis_name not in t_keyed:
        return unchanged("the pelvis has no translation keys", before)
    pelvis = (pdx_motion.posed_joints(mesh, anim)[:, legs.pelvis, 1] - float(mesh.positions[:, 1].min())) / max(mesh.height, 1e-6)
    wanted = np.zeros(anim.frames, bool)  # only the spans that hold are lowered: the rest of the clip keeps its hips
    for start, end, _peak, _ratio in holds(hover, lying):
        wanted[max(start - 3, 0) : end + 1] = True
    drop = target_drop(pelvis, np.where(wanted, hover, 0.0), _room(mesh, anim, legs, exclude_bones))
    if not (drop > 1e-4).any():
        return unchanged("no drop lowers the hips", before)
    result, solved = _lowered(mesh, anim, legs, drop)
    weights = (drop > 1e-4).astype(float)
    leg_joints = [mesh.bones[j] for leg in legs.legs for j in (leg.hip, leg.knee, leg.ankle)]
    tripo_pose._write_translations(data, t_keyed, [pelvis_name], result, weights)
    tripo_pose._write_rotations(data, q_keyed, [name for name in leg_joints if name in q_keyed], result, weights)
    Path(out_path).write_bytes(bytes(data))
    after = _worst_ratio(hover_track(mesh, result, exclude_bones), lying)
    return FallSettle(True, frames=int(weights.sum()), largest_drop=round(float(drop.max()), 4), ratio_before=round(before, 2), ratio_after=round(after, 2),
                      legs=sorted(set(solved)))
