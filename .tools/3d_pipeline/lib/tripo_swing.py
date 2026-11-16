"""The weapon's head leads the blow (TRIPO-WEAPON-HEAD-LEAD), and which way round the grip stage puts the weapon in the fist.

No Blender: the grip stage (`tripo/grip_weapon.py`, in Blender) and the check (`tripo/tripo_checks.py`, on the exported files) call the
same functions on joint tracks.

- The strike (`strike_frame`) is the frame where the holding hand moves fastest in the attack: the blow, not the wind-up's back swing,
  which on the orc's poleaxe attack (2026-11-17) reached 1.6 of the height a second against the chop's 1.9.
- The head leads (`head_lead`) when, around the strike (`STRIKE_WINDOW` frames each side, weighted by the hand's speed), the line from
  the hand to the weapon's head points along the way the hand moves: the cosine of the two is at least `HEAD_LEAD_MIN`. A head behind the
  hand, the cosine negative, means the butt comes first. Two fresh reviewers failed the orc's attack for that: the chop landed with the
  blade at the sky and the butt of the haft driven at the ground. Measured on its exported clip the cosine was -0.65 to -0.82 over the
  chop (frames 24 to 32). With the axe the other way round in the same fist it is +0.75 to +0.89.
- The grip side (`lead_side`): the grip stage lays the haft across the palm and the head may point toward the index finger or toward the
  little finger, the same line in the same fist. With `--head-toward auto` it takes the side whose head leads the strike of the clips
  that fade the hold (the attack). The hold puts the head up at the first frame of every held clip either way.
- The head end (`head_end_mask`) of a weapon mesh is the end whose last slab is widest across the haft: the blade or the club's knob.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

STRIKE_WINDOW = 2
HEAD_LEAD_MIN = 0.0
HEAD_SLAB = 0.15  # the share of the weapon's length at each end that is compared


def _unit_rows(vectors: np.ndarray) -> np.ndarray:
    vectors = np.asarray(vectors, float)
    return vectors / np.maximum(np.linalg.norm(vectors, axis=-1, keepdims=True), 1e-12)


def strike_frame(hand: np.ndarray, start: int = 0) -> int:
    """The frame (from `start` on) where the hand's (F, 3) track moves fastest."""

    hand = np.asarray(hand, float)
    if len(hand) < 3:
        return 0
    speed = np.linalg.norm(np.gradient(hand, axis=0), axis=1)
    start = int(min(max(start, 0), len(hand) - 1))
    return start + int(np.argmax(speed[start:]))


def head_lead(hand: np.ndarray, head_direction: np.ndarray, start: int = 0) -> Tuple[int, float]:
    """(strike frame, cosine): how far the hand-to-head line (`head_direction`, (F, 3)) points along the hand's motion around the strike,
    weighted by the hand's speed. Positive: the head leads the blow. Negative: the butt does."""

    hand = np.asarray(hand, float)
    if len(hand) < 3:
        return 0, 1.0
    velocity = np.gradient(hand, axis=0)
    speed = np.linalg.norm(velocity, axis=1)
    frame = strike_frame(hand, start)
    window = range(max(frame - STRIKE_WINDOW, 0), min(frame + STRIKE_WINDOW + 1, len(hand)))
    heads = _unit_rows(np.asarray(head_direction, float)[list(window)])
    cosines = np.einsum("fi,fi->f", heads, velocity[list(window)]) / np.maximum(speed[list(window)], 1e-12)
    weights = speed[list(window)]
    return frame, float((cosines * weights).sum() / max(float(weights.sum()), 1e-12))


def lead_side(hand: np.ndarray, haft_direction: np.ndarray, start: int = 0) -> Tuple[int, float]:
    """(+1 or -1, cosine): which way along `haft_direction` ((F, 3), the haft carried by the hand) the head should point so it leads the
    strike, and the cosine it then has."""

    frame, cosine = head_lead(hand, haft_direction, start)
    return (1, cosine) if cosine >= 0 else (-1, -cosine)


def head_end_mask(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """(mask of the head end's points, the long axis): of the two end slabs (`HEAD_SLAB` of the length each), the one whose points spread
    widest across the long axis."""

    points = np.asarray(points, float)
    centre = points.mean(axis=0)
    _u, _s, vt = np.linalg.svd(points - centre, full_matrices=False)
    axis = vt[0]
    along = (points - centre) @ axis
    low, high = along <= np.quantile(along, HEAD_SLAB), along >= np.quantile(along, 1.0 - HEAD_SLAB)

    def spread(mask: np.ndarray) -> float:
        offsets = points[mask] - points[mask].mean(axis=0)
        across = offsets - np.outer(offsets @ axis, axis)
        return float(np.linalg.norm(across, axis=1).mean()) if mask.any() else 0.0

    return (high, axis) if spread(high) >= spread(low) else (low, -axis)
