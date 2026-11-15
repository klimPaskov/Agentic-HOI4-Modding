"""Trim a role clip's trailing still part: maths and a GLB reader, no Blender.

Tripo's text-to-motion clips run for the length of the request (up to 5 seconds), and an attack that is over in 3 seconds stands still for the
rest, holding its last pose. In the game that reads as a unit that chops and then freezes. The rule, one for every armed or unarmed unit:

- Motion is the joint turn per frame summed over every joint (degrees). It is smoothed over `SMOOTH_FRAMES`.
- The clip's own peak is the `PEAK_PERCENTILE`th percentile of that motion (one fast frame, such as a snap, does not set it), and the floor is
  `FLOOR_SHARE` of the peak. A clip is still where its motion stays under the floor from some frame to the end.
- The clip keeps a settle of `SETTLE_SECONDS` after its last moving frame and drops the rest, but only when that drops at least
  `MIN_SAVED_SHARE` of the clip and leaves at least `MIN_KEEP_SECONDS`.
- It applies to the roles of `DEFAULT_ROLES` (attack, defend, retreat). Never to idle, move or death: an idle or a walk is a loop and a death
  holds its lying pose on purpose. A job's own `tripo.trim` entry for a role wins (`tripo_intake.prepare_command`).

`tripo_intake.py` calls `auto_trims` on the rigged export and passes the result to `prepare_tripo_unit.py --trim-end`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional, Sequence

import numpy as np

FPS = 24.0  # the frame rate Blender imports a Tripo clip at; trim counts are frames of the imported action
DEFAULT_ROLES = ("attack", "defend", "retreat")
SMOOTH_FRAMES = 5
PEAK_PERCENTILE = 95.0
FLOOR_SHARE = 0.05
SETTLE_SECONDS = 0.5
MIN_SAVED_SHARE = 0.2
MIN_KEEP_SECONDS = 1.0


def smooth(values: np.ndarray, width: int = SMOOTH_FRAMES) -> np.ndarray:
    """Moving average over `width` frames, the edges padded with the end values."""

    values = np.asarray(values, float)
    if len(values) == 0 or width <= 1:
        return values
    padded = np.pad(values, (width // 2, width - 1 - width // 2), mode="edge")
    return np.convolve(padded, np.ones(width) / width, mode="valid")


def still_tail(motion: Sequence[float], fps: float = FPS) -> Optional[dict]:
    """Where a clip with this per-frame motion goes still for good, and how many frames it keeps.

    `motion[i]` is the joint turn (degrees) from frame i to i + 1. Returns None when the clip should keep every frame, else
    {"keep_frames", "from_frames", "floor_degrees", "peak_degrees", "still_from_frame"}: `keep_frames` is the frame offset of the new last frame."""

    motion = np.asarray(motion, float)
    steps = len(motion)
    if steps < 2:
        return None
    smoothed = smooth(motion)
    peak = float(np.percentile(smoothed, PEAK_PERCENTILE))
    if peak <= 1e-6:
        return None
    floor = FLOOR_SHARE * peak
    moving = np.nonzero(smoothed > floor)[0]
    last_moving = int(moving[-1]) if len(moving) else -1
    still_from = last_moving + 1  # the first frame from which the pose no longer changes by more than the floor
    keep = min(steps, still_from + int(round(SETTLE_SECONDS * fps)))
    if steps - keep < MIN_SAVED_SHARE * steps or keep < MIN_KEEP_SECONDS * fps:
        return None
    return {"keep_frames": int(keep), "from_frames": int(steps), "floor_degrees": round(floor, 2), "peak_degrees": round(peak, 1),
            "still_from_frame": int(still_from)}


def _clip_check():
    path = str(Path(__file__).resolve().parents[1] / "tripo")
    if path not in sys.path:
        sys.path.insert(0, path)
    import clip_check

    return clip_check


def clip_motion(doc: dict, binary: bytes, animation: dict, fps: float = FPS) -> np.ndarray:
    """Per frame, the rotation turned by every joint of one glTF animation, summed (degrees)."""

    cc = _clip_check()
    tracks, end = [], 0.0
    for channel in animation["channels"]:
        if channel["target"]["path"] != "rotation":
            continue
        sampler = animation["samplers"][channel["sampler"]]
        times = cc.read_accessor(doc, binary, sampler["input"]).ravel()
        values = cc.read_accessor(doc, binary, sampler["output"])
        if len(times) < 2:
            continue
        tracks.append((times, values))
        end = max(end, float(times[-1]))
    frames = int(round(end * fps)) + 1
    total = np.zeros(max(frames - 1, 0))
    for times, values in tracks:
        quats = np.array([cc.sample_track(times, values, index / fps, True) for index in range(frames)])
        dots = np.clip(np.abs((quats[1:] * quats[:-1]).sum(axis=1)), 0.0, 1.0)
        total += np.degrees(2.0 * np.arccos(dots))
    return total


def role_clip_names(names: Sequence[str], wanted: str) -> Optional[str]:
    """The clip a role names (exact, else the one clip that starts with it); None when it is ambiguous or absent (the intake reports that)."""

    names = sorted(set(names))
    if wanted in names:
        return wanted
    found = [name for name in names if name.startswith(wanted)]
    return found[0] if len(found) == 1 else None


def auto_trims(glb: Path, roles: Dict[str, str], explicit: Sequence[str] = (), apply_to: Sequence[str] = DEFAULT_ROLES, fps: float = FPS) -> Dict[str, dict]:
    """{role: still_tail result} for the roles of `apply_to` that the job maps to a clip of `glb`, have no explicit trim and end still.

    A file that cannot be read gives no trims (the intake then behaves as before)."""

    wanted = [role for role in apply_to if role in roles and role not in explicit]
    if not wanted:
        return {}
    try:
        doc, binary = _clip_check().load_glb(glb)
    except (OSError, ValueError, KeyError):
        return {}
    animations = {animation.get("name", ""): animation for animation in doc.get("animations", [])}
    out = {}
    for role in wanted:
        name = role_clip_names(list(animations), roles[role])
        if name is None:
            continue
        result = still_tail(clip_motion(doc, binary, animations[name], fps), fps)
        if result:
            out[role] = {**result, "clip": name}
    return out
