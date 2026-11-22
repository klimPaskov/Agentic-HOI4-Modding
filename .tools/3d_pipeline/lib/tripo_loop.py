"""The looped gait of a Tripo humanoid's move and retreat: a check (TRIPO-LOOP-STANDS) and the window that fixes it. Plain numpy, no Blender.

HOI4 plays the move and the retreat in place, in a loop, for as long as the unit travels. Two fresh reviewers failed the zombie's retreat
(zombie_p, Tripo's preset `flee_01`, 2026-11-18): it starts in a standing cower (frames 1 to 16), runs only in the middle (31 to 61) and stands
again at the end (76 to 86), so on the map the unit stops and stands once per cycle. Every humanoid unit so far used that preset. The settle of
`lib/tripo_trim.py` made the seam pose match (TRIPO-LOOP-POP passed) by blending the last pose back to a standing first pose, which is itself
a stop.

The measure (`gait_numbers`), on the exported `.mesh` and `.anim` as the game loads them:

- The stride speed of a frame step is how fast one ankle moves against the other (the vector between the two ankle joints, as a share of the
  height, a second). A body that walks or runs swings its feet past each other all the time. A body that stands, cowers or shuffles on the
  spot does not. It is smoothed over `SMOOTH_SECONDS` around the loop (the clip's steps are a cycle), so the instant a swing turns round does
  not count as a stand.
- A frame step has no stride when that speed is under `MIN_STRIDE_SPEED`. The clip stands when any step has none (`still_share` above 0).
- The seam: the velocity of every skinning joint against the pelvis in the first step and in the last one, and the largest difference between the
  two over the joints, in heights a second (`seam_speed_change`). A clip cut out of a run and not closed ends its last step moving one way and
  starts its first moving another. It is judged against the clip itself: as a share of the largest such change between two steps next to
  each other inside the clip (`seam_share`), because a sprint changes its joints' speeds several times as hard as a march does from one step
  to the next. The pose itself at the seam is TRIPO-LOOP-POP's (`lib/tripo_pose.loop_seam`, 8 degrees).

Calibration (2026-11-18, vanilla's GER infantry on GER_infantry.mesh, whose clips every western infantry mesh plays, the files under
`gfx/models/units`). The eight looped locomotion clips: moving_rifle and _mg, march_rifle and _mg, retreat_rifle and _mg, charge_rifle and _mg.

- Slowest smoothed stride speed: moving 0.63 and 0.56, march 0.73, charge 1.25, retreat_rifle 0.21, retreat_mg 0.18 (`VANILLA_MIN_STRIDE_SPEED`,
  a slow jog looking back). None has a step without stride. The limit is that slowest less a quarter, as the kit's other vanilla limits.
- Seam speed change and its share of the largest change inside the clip: moving 0.85 of 1.09 (0.78) and 0.39 of 1.07 (0.37), march 1.25 of
  1.45 (0.86), retreat_rifle 0.57 of 0.60 (0.96, `VANILLA_SEAM_SHARE`), retreat_mg 0.32 of 0.74 (0.44), charge 0.90 of 1.95 (0.46). No vanilla
  seam is rougher than the roughest step inside its clip. The limit `MAX_SEAM_SHARE` is that worst share with a quarter added.
- Vanilla's idle and standing attack never reach the limit (idle_rifle 0.00 to 0.01, attack_stand_rifle under 0.11), so a stand cannot pass as
  a gait.

Tripo units judged by reviewers, on their exported files: the zombie's walk (zombie_p, "a healthy march") never drops under 0.76. Its retreat
drops to 0.005 with 15% of its steps standing, the ogre's (ogre_o) to 0.03 with 9%, the orc's (orc_k) 28%, the dwarf's (dwarf_g) 21%, all
`flee_01`. The dwarf's and the orc's walks also stand, for 7.5% and 1.3% of their steps: the settle appended frames that ease into the first
pose after the grip stage's wrist turns broke the walk's own cycle.

The fix (`loop_window`, run by `tripo_intake.py` on the rigged GLB, cut and closed by `tripo/prepare_tripo_unit.py`):

1. A window is a pair of frames between which each foot leads once: the feet's separation along the stride's own axis both rises and falls
   by at least `LEAD_SHARE` of its full swing, so the window holds whole strides and is never a few frames or half a stride.
2. Every step of the window must stride, in the clip as it is and in the window played as a loop, by the check's own measure with vanilla's
   slowest (`VANILLA_MIN_STRIDE_SPEED`, a quarter over the check's limit) as the floor, so it passes the check with room. That keeps the
   stand, the run-up out of it and the slow-down into it outside. A share of the clip's own speed would not do: a walk slows to half its typical speed where a swing turns
   round, and vanilla's retreat to a quarter.
3. Its cost is how badly its end continues into its start: the joints' distance between the two poses (root mean square over the joints, the
   pelvis kept in place, shares of the height) plus the difference of their velocities over one frame (the steps after the two frames, and
   the steps before them). The best window has the lowest cost. A longer window (more strides, more of the clip's own variety) wins when
   its cost is within a quarter of the best. A clip that already loops (a preset walk) keeps every frame: its whole length is the best window.
4. The stage cuts the clip to the window and closes the remaining seam without a stop: over the last frames each bone gets a growing share of
   the turn from the last pose to the first, added on top of its own motion (`close_weights`), so the feet keep striding through the seam. The
   number of frames is the settle's rule (`tripo_trim.settle_frames`), at most half the window. Tried and dropped (offline on the zombie's
   `flee_01`, 2026-11-18): blending the last frames into the frames that led up to the window's start. The window starts at a foot strike,
   whose own change of speed (3.8 heights a second) is rougher than any step inside the window (2.6), so that seam measured 1.3 of the
   roughest inner step against 0.56 for the turn added on top.
5. The stride of a gait is not a snap. The intake's snap easing (`tripo/prepare_tripo_unit.py --ease-snaps`, 14 degrees a frame) retimes each
   bone on its own, and where a clip turns its legs faster than that for the whole cycle it spreads each bone's turn evenly over the clip:
   a run's knee, thigh and foot then turn at one constant rate each and no longer together. The first run with the window (zombie_s) eased
   six leg bones that way over frames 0 to 17, and the seam's speed changed 6.52 heights a second at a toe, 1.67 times the roughest inner
   step. In a looped gait only a step past `GAIT_SNAP_DEGREES` is eased: the kit's spin limit (UNIT-ANIM-SPIN, vanilla's fastest joint, 37
   degrees a frame at 30 frames a second) is 46 degrees a frame at Tripo's 24, and the trigger is three quarters of that, as the easing's
   own target is three quarters of its trigger. Vanilla's charge turns a knee 31.9 degrees a frame at 30. `flee_01` turns one 38.1 at 24
   (29.9 at 30): that one step is eased over five frames and the stride keeps its timing (offline: the seam 0.56 of the roughest inner step).

No number comes from one unit: the limits are vanilla's, and the window is measured on the clip. A job's own `tripo.trim` for a role wins, and
`"loop_window": false` (or a list of roles) switches the rule off (or limits it). What makes a retreat read as a retreat (the arms, the lean of
`flee_01`'s run) is inside the window, because the window is cut out of the run itself and the close only adds the small turn between two poses of it.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

STRIDE_ROLES = ("move", "retreat")
SMOOTH_SECONDS = 1.0 / 6.0  # 5 steps at 30 frames a second
VANILLA_MIN_STRIDE_SPEED = 0.179
MIN_STRIDE_SPEED = 0.14
VANILLA_SEAM_SHARE = 0.96
MAX_SEAM_SHARE = 1.2
LEAD_SHARE = 0.5
LONGER_WITHIN = 1.25
FPS = 24.0  # the frame rate Blender imports a Tripo clip at; a window counts frames of the imported action
SPIN_LIMIT_DEGREES = 37.0  # UNIT-ANIM-SPIN at 30 frames a second (config/deformation_calibration.json, infantry turn_per_frame 37.19)
GAIT_SNAP_DEGREES = round(0.75 * SPIN_LIMIT_DEGREES * 30.0 / FPS, 1)
FEET = ("LeftFoot", "RightFoot")
PELVIS = "Hips"


def smooth_cyclic(values: np.ndarray, width: int) -> np.ndarray:
    """Moving average over `width` steps of a cycle (the last step is followed by the first)."""

    values = np.asarray(values, float)
    width = min(int(width), len(values))
    if width <= 1:
        return values
    left = width // 2
    extended = np.concatenate([values[len(values) - left:], values, values[: width - 1 - left]])
    return np.convolve(extended, np.ones(width) / width, mode="valid")


def smooth_width(fps: float) -> int:
    """`SMOOTH_SECONDS` as an odd number of steps."""

    return max(1, int(round(SMOOTH_SECONDS * fps)) | 1)


def step_speed(left: np.ndarray, right: np.ndarray, height: float, fps: float) -> np.ndarray:
    """Per frame step, how fast one ankle moves against the other (heights a second). `left` and `right` are (F, 3)."""

    between = (np.asarray(left, float) - np.asarray(right, float)) / max(height, 1e-9)
    return np.linalg.norm(np.diff(between, axis=0), axis=1) * fps


def stride_speed(left: np.ndarray, right: np.ndarray, height: float, fps: float, cyclic: bool = True) -> np.ndarray:
    """`step_speed` smoothed over `SMOOTH_SECONDS`, around the loop when `cyclic` (the clip's steps are a cycle), else with the ends held."""

    speed = step_speed(left, right, height, fps)
    width = smooth_width(fps)
    if cyclic:
        return smooth_cyclic(speed, width)
    if len(speed) == 0 or width <= 1:
        return speed
    padded = np.pad(speed, (width // 2, width - 1 - width // 2), mode="edge")
    return np.convolve(padded, np.ones(width) / width, mode="valid")


def in_place(joints: np.ndarray, pelvis: int, height: float) -> np.ndarray:
    """(F, J, 3) joint positions as shares of the height with the pelvis's horizontal place taken out (index 1 is up)."""

    joints = np.asarray(joints, float)
    root = joints[:, pelvis].copy()
    root[:, 1] = 0.0
    return (joints - root[:, None]) / max(height, 1e-9)


def gait_numbers(joints: np.ndarray, feet: Tuple[int, int], pelvis: int, height: float, fps: float, moving: Optional[Sequence[int]] = None) -> dict:
    """The gait of a looped clip from its (F, J, 3) joint positions (see the module text). `moving` are the joints whose seam velocity counts
    (the skinning joints), every joint when None."""

    joints = np.asarray(joints, float)
    speed = stride_speed(joints[:, feet[0]], joints[:, feet[1]], height, fps)
    still = speed < MIN_STRIDE_SPEED
    out = {"frames": int(len(joints)), "slowest": round(float(speed.min()), 3) if len(speed) else 0.0,
           "median": round(float(np.median(speed)), 3) if len(speed) else 0.0,
           "still_steps": int(still.sum()), "still_share": round(float(still.mean()), 4) if len(speed) else 1.0,
           "first_still_frame": int(np.argmax(still)) if still.any() else None}
    placed = in_place(joints, pelvis, height)
    if moving is not None:
        placed = placed[:, list(moving)]
    out.update(seam_speed_change=0.0, inner_speed_change=0.0, seam_share=0.0)
    if len(placed) >= 4:
        velocity = np.diff(placed, axis=0) * fps
        seam = float(np.linalg.norm(velocity[0] - velocity[-1], axis=1).max())
        inner = float(np.linalg.norm(np.diff(velocity, axis=0), axis=2).max())
        out.update(seam_speed_change=round(seam, 3), inner_speed_change=round(inner, 3), seam_share=round(seam / max(inner, 1e-9), 3) if seam > 1e-9 else 0.0)
    return out


def stands_reason(numbers: dict, role: str) -> Optional[str]:
    """Why a looped move or retreat with these numbers fails, or None."""

    if numbers["still_steps"]:
        return (f"the feet stop striding in {numbers['still_steps']} of {numbers['frames'] - 1} frame steps ({100 * numbers['still_share']:.0f}%, from frame "
                f"{numbers['first_still_frame']}): one ankle moves against the other at {numbers['slowest']:.2f} heights a second at its slowest (at least "
                f"{MIN_STRIDE_SPEED}, vanilla's slowest locomotion clip {VANILLA_MIN_STRIDE_SPEED}): the looped {role} stops and stands once per cycle")
    if numbers["seam_share"] > MAX_SEAM_SHARE:
        return (f"the last step does not flow into the first: a joint's speed against the pelvis changes by {numbers['seam_speed_change']:.2f} heights a second "
                f"across the seam, {numbers['seam_share']:.2f} times the largest change between two steps inside the clip ({numbers['inner_speed_change']:.2f}; "
                f"limit {MAX_SEAM_SHARE}, vanilla's worst {VANILLA_SEAM_SHARE}): the looped {role} jerks once per cycle")
    return None


def clip_gait(mesh, anim) -> Optional[dict]:
    """`gait_numbers` of one exported clip on its mesh. None for a body without two legs."""

    from . import pdx_motion, tripo_pose

    legs = pdx_motion.find_legs(mesh)
    if not legs.biped or legs.pelvis < 0:
        return None
    joints = pdx_motion.posed_joints(mesh, anim)
    names = tripo_pose.skinning_joints(mesh)
    moving = [index for index, name in enumerate(mesh.bones) if name in names]
    return gait_numbers(joints, (legs.legs[0].ankle, legs.legs[1].ankle), legs.pelvis, mesh.height, float(getattr(anim, "fps", 30.0) or 30.0), moving or None)


def loop_findings(mesh, anims: Dict[str, object], roles: Sequence[str] = STRIDE_ROLES) -> Tuple[List[dict], dict]:
    """TRIPO-LOOP-STANDS on each move and retreat clip of a humanoid (`anims`: clip name to animation, the role the name's last word)."""

    out, numbers = [], {}
    for clip, anim in anims.items():
        role = clip.rsplit("_", 1)[-1]
        if role not in roles:
            continue
        row = clip_gait(mesh, anim)
        if row is None:
            continue
        numbers[clip] = row
        reason = stands_reason(row, role)
        if reason:
            out.append({"rule": "TRIPO-LOOP-STANDS", "subject": clip, "message": reason, "still_share": row["still_share"], "slowest": row["slowest"],
                        "seam_speed_change": row["seam_speed_change"], "seam_share": row["seam_share"], "frame": row["first_still_frame"]})
    return out, numbers


def striding_phase(speed: np.ndarray) -> np.ndarray:
    """Per frame step, whether the clip strides there: at or above vanilla's slowest locomotion clip."""

    return np.asarray(speed, float) >= VANILLA_MIN_STRIDE_SPEED


def stride_axis_signal(between: np.ndarray, striding: np.ndarray) -> Tuple[np.ndarray, float]:
    """(the feet's separation along the stride's own axis per frame, its full swing). `between` is (F, 3), the vector from one ankle to the
    other. The axis is the direction the vector varies most along over the striding frames, the swing its 5th to 95th percentile there."""

    frames = np.asarray(between, float)
    chosen = frames[striding] if striding.any() else frames
    centre = np.median(chosen, axis=0)
    _u, _s, vt = np.linalg.svd(chosen - centre, full_matrices=False)
    signal = (frames - centre) @ vt[0]
    low, high = np.percentile(signal[striding], [5, 95]) if striding.any() else (0.0, 0.0)
    return signal, float(high - low)


def _distances(frames: np.ndarray) -> np.ndarray:
    """(N, N) root mean square distance over the joints between every two of N poses (N, J, 3)."""

    flat = frames.reshape(len(frames), -1)
    squares = (flat * flat).sum(axis=1)
    return np.sqrt(np.maximum(squares[:, None] + squares[None] - 2.0 * flat @ flat.T, 0.0) / frames.shape[1])


def loop_window(joints: np.ndarray, feet: Tuple[int, int], pelvis: int, height: float, fps: float = FPS) -> Optional[dict]:
    """The best window of whole strides of a clip (see the module text), from its (F, J, 3) joint positions.

    Returns None when the clip never strides, else {"first", "last"} (frame offsets, the last frame's pose continues into the first's),
    "frames", "whole" (the clip keeps every frame), "cost", "pose" (the poses' distance, shares of the height), "phase" (the first and
    last frame that stride) and "from_frames"."""

    joints = np.asarray(joints, float)
    count = len(joints)
    if count < 4:
        return None
    raw = step_speed(joints[:, feet[0]], joints[:, feet[1]], height, fps)
    width = smooth_width(fps)
    steps = striding_phase(stride_speed(joints[:, feet[0]], joints[:, feet[1]], height, fps, cyclic=False))
    if not steps.any():
        return None
    frame_strides = np.concatenate([steps, [False]]) | np.concatenate([[False], steps])
    signal, swing = stride_axis_signal((joints[:, feet[0]] - joints[:, feet[1]]) / max(height, 1e-9), frame_strides)
    if swing <= 1e-6:
        return None
    # Each foot leads once: between the two frames the separation rises and falls by most of its full swing.
    change = np.diff(signal)
    rises = np.concatenate([[0.0], np.cumsum(np.maximum(change, 0.0))])
    falls = np.concatenate([[0.0], np.cumsum(np.maximum(-change, 0.0))])
    whole_strides = (np.minimum(rises[None] - rises[:, None], falls[None] - falls[:, None]) >= LEAD_SHARE * swing) & np.triu(np.ones((count, count), dtype=bool), 2)
    # Every step of the window strides in the clip as it is: `still[i]` counts the steps without stride before frame i.
    still = np.concatenate([[0], np.cumsum(~steps)])
    whole_strides &= (still[None] - still[:, None]) == 0
    placed = in_place(joints, pelvis, height)
    pose = _distances(placed)
    rate = _distances(np.diff(placed, axis=0))  # [a, b]: the step from a against the step from b
    # The velocities either side of the seam: the step after the last frame against the step after the first, and the same before them.
    after = np.full((count, count), np.nan)
    after[: count - 1, : count - 1] = rate
    before = np.full((count, count), np.nan)
    before[1:, 1:] = rate
    both = np.stack([after, before])
    known = ~np.isnan(both)
    cost = pose + np.where(known.any(axis=0), np.nansum(both, axis=0) / np.maximum(known.sum(axis=0), 1), 0.0)
    candidates = sorted((float(cost[first, last]), int(first), int(last)) for first, last in zip(*np.nonzero(whole_strides)))

    def strides(first: int, last: int) -> bool:
        """The window, looped, strides in every step by the check's own measure, with vanilla's slowest as the floor."""

        return bool(smooth_cyclic(raw[first:last], width).min() >= VANILLA_MIN_STRIDE_SPEED)

    best = next(((value, first, last) for value, first, last in candidates if strides(first, last)), None)
    if best is None:
        return None
    chosen = best
    for value, first, last in sorted((item for item in candidates if item[0] <= LONGER_WITHIN * best[0] + 1e-9), key=lambda item: (item[1] - item[2], item[0])):
        if last - first <= best[2] - best[1]:
            break
        if strides(first, last):
            chosen = (value, first, last)
            break
    value, first, last = chosen
    phase = np.nonzero(frame_strides)[0]
    return {"first": first, "last": last, "frames": last - first, "from_frames": int(count - 1), "whole": bool(first == 0 and last == count - 1),
            "cost": round(value, 4), "pose": round(float(pose[first, last]), 4), "best_cost": round(best[0], 4), "phase": [int(phase[0]), int(phase[-1])]}


def _clip_check():
    path = str(Path(__file__).resolve().parents[1] / "tripo")
    if path not in sys.path:
        sys.path.insert(0, path)
    import clip_check

    return clip_check


def rig_joints(rig, tracks: dict, end: float, fps: float = FPS) -> np.ndarray:
    """(F, J, 3) joint positions of one clip of a `clip_check.Rig`, a frame every 1 / `fps` seconds."""

    frames = int(round(end * fps)) + 1
    return np.stack([rig.joint_worlds(rig.pose_for(tracks, min(index / fps, end)))[:, :3, 3] for index in range(frames)])


def rig_gait_joints(rig) -> Optional[Tuple[Tuple[int, int], int, float]]:
    """((left ankle, right ankle), pelvis, height) of a Tripo humanoid rig by its joint names, the height the rest joints' vertical extent.
    None when it has not those joints."""

    from . import tripo_rig

    try:
        names = tripo_rig.RigNames(rig.joint_names)
    except tripo_rig.RigError:
        return None

    def find(name: str) -> int:
        actual = names.actual(name)
        return rig.joint_names.index(actual) if actual in rig.joint_names else -1

    feet, pelvis = (find(FEET[0]), find(FEET[1])), find(PELVIS)
    if min(feet) < 0 or pelvis < 0:
        return None
    rest = rig.joint_worlds({})[:, :3, 3]
    return feet, pelvis, float(np.ptp(rest[:, 1]))


def auto_windows(glb: Path, roles: Dict[str, str], explicit: Sequence[str] = (), apply_to: Sequence[str] = STRIDE_ROLES, fps: float = FPS) -> Dict[str, dict]:
    """{role: loop_window result} for the roles of `apply_to` that the job maps to a clip of `glb` and have no explicit trim.

    A file that cannot be read or a rig without the humanoid's joints gives no windows (the intake then behaves as before)."""

    from . import tripo_trim

    wanted = [role for role in apply_to if role in roles and role not in explicit]
    if not wanted:
        return {}
    cc = _clip_check()
    try:
        doc, _binary = cc.load_glb(glb)
        body = next(node.get("name") for node in doc["nodes"] if "mesh" in node and "skin" in node)
        rig = cc.Rig(glb, body, None)
    except (OSError, ValueError, KeyError, StopIteration, SystemExit):
        return {}
    found = rig_gait_joints(rig)
    if found is None:
        return {}
    feet, pelvis, height = found
    clips = {name: (tracks, end) for name, tracks, end in rig.clips()}
    out = {}
    for role in wanted:
        name = tripo_trim.role_clip_names(list(clips), roles[role])
        if name is None:
            continue
        result = loop_window(rig_joints(rig, *clips[name], fps), feet, pelvis, height, fps)
        if result:
            out[role] = {**result, "clip": name}
    return out


def close_frames(max_turn_degrees: float, rate: float, window_frames: int) -> int:
    """How many of the window's last frames carry the turn from the last pose to the first: the settle's count, at most half the window."""

    from . import tripo_trim

    return int(min(tripo_trim.settle_frames(max_turn_degrees, rate), max(window_frames // 2, 0)))


def close_weights(frames: int) -> np.ndarray:
    """The share of the last-to-first turn added in each of the last `frames` frames: a smoothstep ending at exactly 1, so the last frame is the
    first pose and the added turn starts and ends with no speed of its own."""

    t = np.arange(1, frames + 1) / max(frames, 1)
    return t * t * (3.0 - 2.0 * t)
