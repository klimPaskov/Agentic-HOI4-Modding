"""Snap easing that keeps the motion: a joint turn faster than the trigger is retimed along its own path, never cut short.

Tripo's clips have joints that turn tens of degrees in one frame (a blow, a flip of a toe), and the kit retimes 24 fps clips to 30, where
one frame's step can double past the unit spin check's 37 degrees (UNIT-ANIM-SPIN). The grip stage, the shield stage and the intake
(`tripo/grip_weapon.py`, `tripo/shield_stage.py`, `tripo/prepare_tripo_unit.py --ease-snaps`) ease such a step over more frames.

They used to replace every key of the window with a straight slerp from its first key to its last. That throws away whatever the joint
did inside the window. The ogre's `chop` raises the club hand 0.27 of the height above the chest at frame 44 and strikes at frame 49
with the upper arm turning 45 degrees in one frame. The window that eased the strike ran from frame 37 to 60, and the slerp from the
arm's pose at 37 to its pose at 60 never went up, so the hand rose only 0.04 above the chest: no raise and no blow (two fresh
reviewers, 2026-11-17).

The rule now (`ease_turns`): the keys keep their times, and the joint passes through the same poses in the same order, only the
time spent between them changes. Inside the window each step's share of the time is at least its angle over the target rate, and
the slow steps around the fast one give up time for it (they speed up evenly, never past the target). So the raise, the end of the
swing and every other extreme of the window stay, only a little earlier or later. The smallest window that fits is taken, as before.
Maths only (numpy), quaternions as (w, x, y, z) rows.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np

MAX_WINDOW = 16


def _unit(q: np.ndarray) -> np.ndarray:
    return q / max(float(np.linalg.norm(q)), 1e-12)


def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    a, b = np.asarray(a, float), np.asarray(b, float)
    dot = float(a @ b)
    if dot < 0.0:
        b, dot = -b, -dot
    if dot > 0.9995:
        return _unit(a + (b - a) * t)
    theta = float(np.arccos(min(dot, 1.0)))
    return (np.sin((1.0 - t) * theta) * a + np.sin(t * theta) * b) / np.sin(theta)


def step_degrees(a: np.ndarray, b: np.ndarray) -> float:
    return 2.0 * float(np.degrees(np.arccos(min(1.0, abs(float(np.asarray(a) @ np.asarray(b)))))))


def turn_rates(quats: Sequence[np.ndarray], frames: Sequence[float]) -> List[float]:
    """Degrees per frame between neighbouring keys."""

    return [step_degrees(quats[k - 1], quats[k]) / max(float(frames[k]) - float(frames[k - 1]), 1e-6) for k in range(1, len(quats))]


def one_hemisphere(quats: Sequence[np.ndarray]) -> Tuple[List[np.ndarray], int]:
    """The keys with each one on the side of its neighbour (a flip makes Blender turn the long way), and the number of flips fixed."""

    out = [np.array(q, float) for q in quats]
    flips = 0
    for k in range(1, len(out)):
        if float(out[k] @ out[k - 1]) < 0.0:
            out[k] = -out[k]
            flips += 1
    return out, flips


def retime_window(quats: Sequence[np.ndarray], frames: Sequence[float], a: int, b: int, target: float,
                  fit: bool = True) -> Optional[List[np.ndarray]]:
    """The keys `a` to `b` moved along the joint's own path so that no step is faster than `target` degrees per frame, or None.

    Each original step j (from key j to key j + 1) gets a share of the window's time: at least its angle over `target`, and at least
    `m` times its own length, with the largest `m` (at most 1) that still fits the window. The new key at time t takes the pose the
    old path reaches at the matching point (a slerp inside the old step). None when even `m` = 0 does not fit. With `fit` false the
    whole window is shared by angle alone (the slowest even turn), for a window that is the whole clip."""

    times = np.asarray(frames[a : b + 1], float)
    total = float(times[-1] - times[0])
    angles = np.array([step_degrees(quats[j], quats[j + 1]) for j in range(a, b)])
    lengths = np.diff(times)
    need = angles / max(target, 1e-9)
    if fit:
        if need.sum() > total + 1e-9:
            return None
        low, high = 0.0, 1.0
        for _ in range(60):
            m = 0.5 * (low + high)
            if np.maximum(need, m * lengths).sum() > total:
                high = m
            else:
                low = m
        spans = np.maximum(need, low * lengths)
    else:
        spans = angles if angles.sum() > 1e-9 else lengths.copy()
    spans = spans * (total / max(float(spans.sum()), 1e-12))
    edges = times[0] + np.concatenate([[0.0], np.cumsum(spans)])
    out = [np.array(q, float) for q in quats]
    for m in range(a + 1, b):
        t = float(times[m - a])
        j = int(min(max(np.searchsorted(edges, t, side="right") - 1, 0), b - a - 1))
        f = (t - edges[j]) / max(edges[j + 1] - edges[j], 1e-12)
        q = slerp(quats[a + j], quats[a + j + 1], float(min(max(f, 0.0), 1.0)))
        out[m] = q if float(q @ out[m - 1]) >= 0.0 else -q
    return out


def ease_turns(quats: Sequence[np.ndarray], frames: Sequence[float], trigger: float, target: float,
               max_window: int = MAX_WINDOW) -> Tuple[List[np.ndarray], List[List[int]]]:
    """(the keys with every step faster than `trigger` degrees per frame retimed, the windows eased as [first frame, last frame]).

    The keys must be on one hemisphere (`one_hemisphere`). For a fast step at key k the window grows from two keys either side to
    `max_window`, and the first that `retime_window` fits to `target` is taken. When the window has grown to the whole clip and still
    does not fit, the clip's turn is spread evenly over it. A step no window fits is left as it is."""

    quats = [np.array(q, float) for q in quats]
    eased: List[List[int]] = []
    count = len(quats)
    k = 1
    while k < count:
        if turn_rates(quats[k - 1 : k + 1], frames[k - 1 : k + 1])[0] > trigger:
            for window in range(2, max_window + 1):
                a, b = max(k - window, 0), min(k + window - 1, count - 1)
                whole = a == 0 and b == count - 1
                trial = retime_window(quats, frames, a, b, target)
                if trial is None and whole:
                    trial = retime_window(quats, frames, a, b, target, fit=False)
                if trial is not None:
                    quats = trial
                    eased.append([int(frames[a]), int(frames[b])])
                    k = b
                    break
        k += 1
    return quats, eased
