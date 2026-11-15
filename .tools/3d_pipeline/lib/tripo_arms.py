"""Arm level: where the hands are during a clip, and the one constant arm rotation that brings them to chest height.

Tripo's text-to-motion attacks for a zombie keep the hands above the shoulders, often above the head, so the head is hidden. The
kit measures that (`hand_levels`, the TRIPO-HANDS-HIGH check) and, for a unit job that asks for it, fixes it (`solve_arm_offset`,
applied by `tripo/prepare_tripo_unit.py --arm-level ROLE`): both upper arms get the same constant additive rotation for the whole
clip, solved so that the mean hand height over the reach phase sits at chest height. The clip's timing, legs and torso stay as they were.

Heights are along the up axis, all arrays are (frames, 3) world positions of the joints named; maths only (numpy), no files, no Blender.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional, Sequence, Tuple

import numpy as np

# TRIPO-HANDS-HIGH: a hand above the head in more than this share of frames, or the hands above the shoulder in more than the other.
MAX_ABOVE_HEAD_SHARE = 0.20
MAX_ABOVE_SHOULDER_SHARE = 0.80
# After the fix the hands must still be in front of the chest: the mean forward distance of the hands from the hips in the reach
# phase, as a share of the body height.
MIN_FORWARD_SHARE = 0.08


def hand_levels(left_hand: np.ndarray, right_hand: np.ndarray, left_shoulder: np.ndarray, right_shoulder: np.ndarray, head: np.ndarray, up_axis: int = 1) -> Dict[str, float]:
    """The share of frames in which the higher hand is above the head joint, and the share in which the hands (their mean) are above the shoulders."""

    left, right = left_hand[:, up_axis], right_hand[:, up_axis]
    higher = np.maximum(left, right)
    mean_hand = 0.5 * (left + right)
    shoulder = 0.5 * (left_shoulder[:, up_axis] + right_shoulder[:, up_axis])
    return {
        "above_head_share": float(np.mean(higher > head[:, up_axis])),
        "above_shoulder_share": float(np.mean(mean_hand > shoulder)),
    }


def hands_high(levels: Dict[str, float]) -> Optional[str]:
    """The reason a clip fails TRIPO-HANDS-HIGH, or None."""

    if levels["above_head_share"] > MAX_ABOVE_HEAD_SHARE:
        return f"a hand is above the head in {levels['above_head_share']:.0%} of the frames (limit {MAX_ABOVE_HEAD_SHARE:.0%})"
    if levels["above_shoulder_share"] > MAX_ABOVE_SHOULDER_SHARE:
        return f"the hands are above the shoulders in {levels['above_shoulder_share']:.0%} of the frames (limit {MAX_ABOVE_SHOULDER_SHARE:.0%})"
    return None


def chest_height(shoulder_mid: np.ndarray, hips: np.ndarray, up_axis: int = 1, toward_shoulder: float = 0.0) -> np.ndarray:
    """Per frame: the target hand height, halfway between the shoulders and the hips (`toward_shoulder` 0), or that much of the way on to the shoulders (1 is shoulder height)."""

    chest = 0.5 * (shoulder_mid[:, up_axis] + hips[:, up_axis])
    return chest + toward_shoulder * (shoulder_mid[:, up_axis] - chest)


def reach_frames(hand_mid: np.ndarray, hips: np.ndarray, front: np.ndarray, share: float = 0.5, minimum: int = 8) -> np.ndarray:
    """Indices of the reach phase: the frames in which the hands are at least `share` of their farthest forward distance from the hips.

    `front` is the unit horizontal direction the unit faces. At least `minimum` frames (the farthest ones) are returned.
    """

    forward = (hand_mid - hips) @ np.asarray(front, float)
    cutoff = share * float(forward.max()) if forward.max() > 0 else float(forward.max())
    chosen = np.where(forward >= cutoff)[0]
    if len(chosen) < minimum:
        chosen = np.argsort(forward)[::-1][: min(minimum, len(forward))]
    return np.sort(chosen)


def solve_arm_offset(mean_error: Callable[[float], float], low: float = -2.4, high: float = 2.4, tolerance: float = 1e-3, steps: int = 40, grid: int = 49) -> Tuple[float, float]:
    """The angle (radians) in [low, high] at which `mean_error(angle)` is zero, and the error left there.

    `mean_error(angle)` is the mean over the reach phase of (hand height - chest height) with both upper arms turned by `angle`. The interval
    is scanned on a grid for a sign change; of the brackets found the one nearest zero rotation is bisected (the smallest turn that does it).
    With no sign change the angle with the smallest error on the grid is returned.
    """

    angles = np.linspace(low, high, grid)
    values = [mean_error(float(a)) for a in angles]
    best = None
    for k in range(grid - 1):
        if values[k] == 0.0:
            return float(angles[k]), 0.0
        if np.sign(values[k]) != np.sign(values[k + 1]):
            distance = min(abs(angles[k]), abs(angles[k + 1]))
            if best is None or distance < best[0]:
                best = (distance, k)
    if best is None:
        k = int(np.argmin(np.abs(values)))
        return float(angles[k]), float(values[k])
    k = best[1]
    a, b, fa = float(angles[k]), float(angles[k + 1]), values[k]
    mid, fm = 0.5 * (a + b), 0.0
    for _ in range(steps):
        mid = 0.5 * (a + b)
        fm = mean_error(mid)
        if abs(fm) <= tolerance:
            break
        if np.sign(fm) == np.sign(fa):
            a, fa = mid, fm
        else:
            b = mid
    return float(mid), float(fm)


def pick_axis(slopes: Sequence[float]) -> Tuple[int, float]:
    """The index of the local axis whose rotation changes the hand height most, and its slope's sign (+1 or -1)."""

    index = int(np.argmax(np.abs(slopes)))
    return index, 1.0 if slopes[index] >= 0 else -1.0
