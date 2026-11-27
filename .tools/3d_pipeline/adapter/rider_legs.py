"""Where a seated rider's legs go, from the mount's measured barrel (pure numpy, no Blender).

`rider_seat.py` puts the pelvis on the mount's Saddle_Node and aims each thigh, shin and foot. A fixed aim fits one horse: the first one
was measured on ZIN's Meshy warhorse. Here the aim is solved for the mount the rider sits on, from its barrel profile
(`lib/rider_fit.barrel_profile`: the half-width beside the seat at each depth below the node, both in rider heights).

The thigh reaches THIGH_FORWARD of its length forward (the fixed aim's share), turns out only as far as it must for the knee and the
point THIGH_CHECK along it to stand CLEARANCE outside the barrel, and drops the rest of its length. The upper thigh rests on the saddle,
as a rider's does: a clearance there would splay the thigh sideways (offline on ZIN's barded Meshy warhorse a side-view slope held fixed
put the knee 0.26 of the rider's height out and level with the seat). The shin hangs from the knee down and a
little back (SHIN_BACK) and turns out, or in under a bulging barrel, as little as keeps the ankle and the shin's middle CLEARANCE outside
it. Every length is a share of the rider's height, measured in the rider's own frame (forward, outward, up).
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np

THIGH_FORWARD = 0.55  # the fixed aim (0.55, 0.62, -0.56)'s forward share
THIGH_CHECK = 0.75  # the thigh is judged from this share of its length to the knee
SHIN_BACK = 0.2
# Outside the barrel by this share of the rider's height: a leg's own half thickness (an armoured thigh is about 0.04 of the height across
# at the knee) and a little air.
CLEARANCE = 0.035
OUT_STEPS = tuple(round(0.02 * step, 2) for step in range(-15, 101))  # outward components tried, smallest first after the sign


def half_width(profile: Sequence[Dict[str, float]], depth: float) -> float:
    """The barrel's half-width at `depth` below the node (rider heights), linear between the measured depths, 0 above the node."""

    depths = np.array([row["depth"] for row in profile], dtype=float)
    widths = np.array([row["half_width"] for row in profile], dtype=float)
    if depth <= 0.0 or not len(depths):
        return 0.0
    return float(np.interp(depth, depths, widths, right=widths[-1]))


def _clear(start: np.ndarray, end: np.ndarray, profile: Sequence[Dict[str, float]], clearance: float, check: float = 0.5) -> bool:
    """The point `check` along the segment and its end stand `clearance` outside the barrel (outward is the second component, up the third)."""

    for point in (start + check * (end - start), end):
        if point[1] < half_width(profile, -point[2]) + clearance:
            return False
    return True


def solve_leg(hip: Sequence[float], thigh: float, shin: float, profile: Sequence[Dict[str, float]],
              clearance: float = CLEARANCE) -> Dict[str, object]:
    """Directions (forward, outward, up) for the thigh and shin of one leg whose hip joint is at `hip` (forward, outward, up from the seat).

    `thigh` and `shin` are the bone lengths. Returns the directions, the knee and ankle points (numpy arrays) and whether every point clears.
    A Blender caller turns the arrays into plain floats first: a numpy float times a mathutils Vector is a numpy array (rider_seat.py)."""

    hip = np.asarray(hip, dtype=float)
    thigh_dir, knee, fit = None, None, False
    room = 1.0 - THIGH_FORWARD ** 2
    for out in (value for value in OUT_STEPS if 0.0 <= value and value * value <= room):
        direction = np.array([THIGH_FORWARD, out, -np.sqrt(room - out * out)])
        end = hip + thigh * direction
        thigh_dir, knee = direction, end
        if _clear(hip, end, profile, clearance, THIGH_CHECK):
            fit = True
            break
    shin_dir, ankle, shin_fit = None, None, False
    for out in sorted(OUT_STEPS):
        direction = np.array([-SHIN_BACK, out, -1.0])
        direction /= np.linalg.norm(direction)
        end = knee + shin * direction
        if _clear(knee, end, profile, clearance):
            shin_dir, ankle, shin_fit = direction, end, True
            break
    if shin_dir is None:
        direction = np.array([-SHIN_BACK, OUT_STEPS[-1], -1.0])
        shin_dir = direction / np.linalg.norm(direction)
        ankle = knee + shin * shin_dir
    return {"thigh": thigh_dir, "shin": shin_dir, "knee": knee, "ankle": ankle, "clear": bool(fit and shin_fit)}


def legacy_dirs() -> Tuple[np.ndarray, np.ndarray]:
    """The fixed aim measured on ZIN's Meshy warhorse, for a rider seated with no measured mount."""

    return np.array([0.55, 0.62, -0.56]), np.array([-0.2, 0.12, -1.0])


def solve_seat(hips: Dict[str, Sequence[float]], thigh: Dict[str, float], shin: Dict[str, float],
               profile: List[Dict[str, float]]) -> Dict[str, Dict[str, object]]:
    """Both legs: `hips` maps a side to its hip point (forward, outward, up) from the seat in rider heights."""

    return {side: solve_leg(hips[side], thigh[side], shin[side], profile) for side in hips}


def shoulder_twist(line: Sequence[float], forward: Sequence[float], side: Sequence[float], up: Sequence[float]) -> float:
    """Degrees the shoulder line (left upper arm's joint minus the right's) lies off the side axis, seen from above: 0 square to the
    mount, 90 side-on, either way round. rider_seat holds it within SEAT_TWIST_MAX (a seated rider's hips cannot follow a clip's turn)."""

    line, forward, side, up = (np.asarray(value, dtype=float) for value in (line, forward, side, up))
    flat = line - up * float(line @ up)
    if float(np.linalg.norm(flat)) < 1e-9:
        return 0.0
    return float(np.degrees(np.arctan2(abs(float(flat @ forward)), abs(float(flat @ side)))))


# A seated rider's hand stays this share of its height above the mount's top ahead of the seat (a hand's own half thickness and a little
# air): the zinnish lancer's defend put the rein hand into the pommel and withers as the horse's brace lifted them.
HAND_CLEARANCE = 0.03
TOP_CELL = 0.025  # lib/rider_fit.TOP_CELL: the half size of a cell of the top grid


def top_at(rows: Sequence[Dict[str, object]], ahead: float, out: float) -> float:
    """The mount's highest point above the seat (rider heights) in the top grid's cells around a point `ahead` of the seat and `out` from
    its midline (lib/rider_fit.clip_profiles' `top`). -inf where the grid holds nothing there, behind the seat or past its reach."""

    tops = [float(row["top"]) for row in rows if row.get("top") is not None
            and abs(float(row["ahead"]) - ahead) <= TOP_CELL and abs(float(row["out"]) - abs(out)) <= TOP_CELL]
    return max(tops) if tops else float("-inf")


def hand_clear(points: Sequence[Sequence[float]], rows: Sequence[Dict[str, object]], clearance: float = HAND_CLEARANCE) -> bool:
    """Every point (forward, outward, up from the seat, rider heights) of a hand stands `clearance` above the mount's top grid."""

    return all(float(up) >= top_at(rows, float(ahead), float(out)) + clearance for ahead, out, up in points)


# A seated rider's held weapon dropped in the death (rider_seat.py): it falls for DROP_SECONDS and lies on the ground at least
# DROP_CLEARANCE of the rider's height from every point of the fallen mount and rider, as near the hand as that allows (the grip stage's
# standing drop keeps 4% of the height too, lib/tripo_clearance.plan_drop).
DROP_SECONDS = 0.4
DROP_CLEARANCE = 0.04
DROP_STEP = 0.05  # rider heights between the landing places tried, outward from below the hand
DROP_REACH = 2.5
DROP_HEADINGS = 16
DROP_TURNS = (0.0, 30.0, -30.0, 60.0, -60.0, 90.0, -90.0, 180.0)


def _lance_points(grip: np.ndarray, haft: np.ndarray, length: float, grip_share: float, count: int = 24) -> np.ndarray:
    return grip + np.outer(np.linspace(-grip_share, 1.0 - grip_share, count) * length, haft)


def clear_of(points: np.ndarray, obstacles: np.ndarray, clearance: float) -> bool:
    """Every point stands `clearance` from every obstacle point (plain numpy: Blender's Python has no scipy)."""

    if not len(obstacles):
        return True
    gaps = np.linalg.norm(points[:, None, :] - obstacles[None, :, :], axis=2)
    return bool(gaps.min() >= clearance)


def plan_drop(grip: Sequence[float], haft: Sequence[float], length: float, grip_share: float, ground: float,
              obstacles: Sequence[Sequence[float]], radius: float = 0.01, clearance: float = DROP_CLEARANCE) -> Dict[str, object]:
    """Where a dropped weapon lies: its grip point and its haft's direction, level on the ground (`ground`, the ground's height). Every
    coordinate is (ahead, out, up) in rider heights in the seat's rest frame, where the ground stays still (lib/rider_fit.drop_inputs).
    The weapon falls from the grip point `grip` with the haft along `haft` (toward its head); `length` and `grip_share` (the grip's share
    of the length from the butt) place its ends. The places tried run outward from below the hand, and at each the haft keeps its heading
    over the ground or turns by DROP_TURNS. `found` is False when nothing within DROP_REACH clears, and the result is then the place
    with the widest gap."""

    grip, haft = np.asarray(grip, dtype=float), np.asarray(haft, dtype=float)
    obstacles = np.asarray(obstacles, dtype=float).reshape(-1, 3)
    level = np.array([haft[0], haft[1], 0.0])
    heading = float(np.degrees(np.arctan2(level[1], level[0]))) if np.linalg.norm(level) > 0.2 else 0.0
    best = None
    for step in range(int(DROP_REACH / DROP_STEP) + 1):
        radius_out = step * DROP_STEP
        bearings = [0.0] if step == 0 else [360.0 * k / DROP_HEADINGS for k in range(DROP_HEADINGS)]
        for bearing in bearings:
            centre = np.array([grip[0] + radius_out * np.cos(np.radians(bearing)), grip[1] + radius_out * np.sin(np.radians(bearing)), ground + radius])
            for turn in DROP_TURNS:
                angle = np.radians(heading + turn)
                lie = np.array([np.cos(angle), np.sin(angle), 0.0])
                points = _lance_points(centre, lie, length, grip_share)
                gap = float(np.linalg.norm(points[:, None, :] - obstacles[None, :, :], axis=2).min()) if len(obstacles) else float("inf")
                if gap >= clearance:
                    return {"grip": centre, "haft": lie, "found": True, "gap": gap, "travel": radius_out}
                if best is None or gap > best["gap"]:
                    best = {"grip": centre, "haft": lie, "found": False, "gap": gap, "travel": radius_out}
    return best


def smooth_lifts(needs: List[float], rate: float, loop: bool) -> List[float]:
    """Each frame's lift: the largest need of any frame less `rate` times the frames between them (round the clip when `loop`), so the
    lift rises before a need and falls after it at no more than `rate` a frame and never falls short of a need."""

    count = len(needs)
    out = []
    for frame in range(count):
        best = 0.0
        for other, need in enumerate(needs):
            if need <= 0.0:
                continue
            gap = abs(frame - other)
            if loop:
                gap = min(gap, count - gap)
            best = max(best, need - rate * gap)
        out.append(best)
    return out
