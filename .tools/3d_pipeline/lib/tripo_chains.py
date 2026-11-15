"""Secondary chains: bone chains added to one region of a Tripo-rigged unit (a cloak, a pair of wings) and moved by a fixed rule per role.

Tripo's humanoid rig has no cloth or wing bones. It binds a long cloak to the thighs and a wing membrane to the arms, so the cloak tears
when a leg kicks and the wings bend whenever an arm moves. This stage, run by `tripo/prepare_tripo_unit.py --chains REGION ...` (the job's
`"chains": [{"region": "cloak"}, {"region": "wings"}]` in its `tripo` block), finds the region by rule, places chains on it, rebinds it to
them and keys them per role. Every number comes from a rule here or from the body's own measurements; none is set per unit.

Maths only (numpy), no files, no Blender. Coordinates are any right-handed space with an `up` unit vector and a `front` unit vector.

The rules, in order:

1. Region. Cloak: the region TRIPO-CLOAK-STRETCH already measures (`tripo_checks.cloak_region`: vertices behind the hips, weighted mostly
   to the torso, hips or thighs, between a quarter and 0.85 of the height), grown along the mesh into the loose cloth beside it
   (`cloak_rebind_mask`: behind the hips, off every limb). Wings: vertices farther from the body's mid-plane than `WING_LATERAL_SHARE` of
   the unit's width, minus the arms (vertices weighted mostly to a forearm or a hand), split into a left and a right wing. The left
   wing's chains are mirrored onto the right.
2. Bone budget. HOI4 allows 50 bones. The bones the rig keeps are counted; what is left is shared equally by the requested regions'
   sides (a pair of wings is two sides).
3. Chain shape. A chain bone is half a thigh long (the rig's own thigh, hip to knee), so cloth bends at about the spacing a knee bends a
   leg. Bones per chain = the region's length over that, 2 to 4. Chains = the region's width over that, 2 to 6. Over budget: bones per
   chain drop to 3 first (a wave needs three), then chains to 2, then bones to 2.
4. Chain placement. Each region is a sheet with an across coordinate `u` and an along coordinate `s` (distance from the root). Cloak: `u`
   is the angle round the vertical axis through the hips, `s` the drop below the region's top. Wing: a fan round the wing root (where it
   grows from the upper back), `u` the angle in the wing's plane, `s` the distance from the root. Cloak chains are an even fan across its
   width. Wing chains are an even fan, each moved onto a ridge (a finger, where the wing reaches farthest) when one lies within half the
   fan's spacing. Joints sit on the sheet: the median of the region's vertices near each joint's (u, s).
5. Weights. Each vertex takes two neighbouring chains (linear in `u`) and two neighbouring bones of each (linear in `s` between bone
   middles): at most 4 influences. The region takes the chains' weights whole. They blend into the body's over one chain bone of surface
   distance outward from the region's border (`blend_alpha`), and each vertex keeps its 4 largest weights, normalised.
6. Motion. Cloak (`simulate_sheet`): each chain bone's tail follows the upper spine and the hips by its height (`torso_follow_weights`)
   through a critically damped spring at the pendulum rate of the bone, omega = sqrt(g / bone length). The chains are
   pushed out of capsules round the legs and the torso along the hips' back direction, a push spreading to the neighbouring chains
   (`spread_pushes`), never pointing above the horizontal (`hang_below_horizon`, gravity), and kept above the ground. Wings: a fold pose per role plus a flap, a sine on each chain bone's rotation delayed a
   fixed share of a cycle per bone down the chain (`WING_ROLES`). The result is baked to keys at the clip's frame rate. Idle and move loop:
   the cloak is run for `LOOP_PASSES` cycles, the last kept and its last frames eased onto its first; the wing flap fits a whole number
   of cycles in the clip.

Measured on the orc (2026-11-15) and kept out on purpose: a world-gravity hang (the cloak keeping its rest angle to the ground) and a
follow of Tripo's own cloak weights both stretched the cloak more than Tripo's weights did, and a blend inside the region held 97% of the
cloak's stretched edges.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

MAX_BONES = 50
MAX_INFLUENCES = 4
# Every chain hangs from the upper spine, so an arm or a thigh no longer drags it.
CHAIN_PARENT = "Spine02"
# The bones TRIPO-CLOAK-STRETCH selects a cloak by (the kit's names for Tripo's torso, hips and thighs).
CLOAK_BONES = ("Hips", "Spine", "Spine01", "Spine02", "LeftUpLeg", "RightUpLeg")
# Wing vertices weighted mostly to one of these are the arm, not the membrane (the hand bone also carries the folded finger bones).
ARM_BONE_ENDINGS = ("ForeArm", "Hand")
# A wing vertex lies farther from the mid-plane than this share of the unit's width (the demon's arms end at 0.17 of its width, its
# wing membrane starts behind the shoulders and covers 53% of the vertices beyond 0.18).
WING_LATERAL_SHARE = 0.18
# The cloak check's height band (lib/tripo_checks.cloak_region defaults), used when the region grows into the cloak's sides.
CLOAK_LOW_SHARE, CLOAK_HIGH_SHARE = 0.25, 0.85
# Loose cloth lies farther from a limb's axis than this many times the limb's own radius (the 60th percentile of its skin's distance).
LOOSE_FACTOR = 1.25
# The chain weights blend into the body's over one chain bone, and over at least this many edge rings on a coarse mesh.
BLEND_MIN_RINGS = 4
MIN_BONES_PER_CHAIN, MAX_BONES_PER_CHAIN = 2, 4
MIN_CHAINS, MAX_CHAINS = 2, 6
# A wing ridge (a finger) stands this share of the wing's largest reach above the angles beside it; smaller bumps are a ragged edge.
RIDGE_PROMINENCE = 0.05
WAVE_BONES = 3  # a flap wave or a cloth curl needs three bones; the budget trims chains before going below it
# Idle and move loop in vanilla; every other role plays once.
LOOPING_ROLES = ("idle", "move")
LOOP_PASSES = 3  # a looping cloak runs this many cycles from rest and keeps the last: the spring has settled into the cycle
GRAVITY = 9.81
Z_UP = np.array([0.0, 0.0, 1.0])  # Blender's up, the default for the chain simulation
# The pendulum rule reads lengths as shares of the height on a body this tall (a person); model units never enter the motion.
NOMINAL_HEIGHT_M = 1.8
# A collision push carries to the neighbouring chains at this share per chain (half), so the cloth moves as a sheet.
SHEET_SPREAD = 0.5
SUBSTEPS = 4  # spring integration steps per frame (omega * dt stays under 0.1 per step)
COLLISION_MARGIN_SHARE = 0.01  # chain joints keep this share of the height clear of the body capsules and the ground
CAPSULE_PERCENTILE = 60  # a capsule's radius is this percentile of its own vertices' distance to the bone (clothes and fur stay compressible)
GROUND_MARGIN_SHARE = 0.005

# Prefix of the bones each region adds; the checks find a region's vertices by them too.
REGION_PREFIX = {"cloak": "Cloak", "wings": "Wing"}
REGIONS = tuple(REGION_PREFIX)


# ---------------------------------------------------------------------------------------------
# Small vector helpers
# ---------------------------------------------------------------------------------------------


def unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, float)
    length = np.linalg.norm(vector, axis=-1, keepdims=True)
    return np.where(length > 1e-12, vector / np.maximum(length, 1e-12), vector)


def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(x, float), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def shortest_arc(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The 3x3 rotation that turns unit vector `a` onto unit vector `b` by the smallest angle."""

    a, b = unit(a), unit(b)
    axis = np.cross(a, b)
    sine, cosine = float(np.linalg.norm(axis)), float(np.clip(a @ b, -1.0, 1.0))
    if sine < 1e-9:
        if cosine > 0:
            return np.eye(3)
        helper = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        axis = unit(np.cross(a, helper))
        return axis_angle_matrix(axis, math.pi)
    return axis_angle_matrix(axis / sine, math.atan2(sine, cosine))


def axis_angle_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    x, y, z = unit(axis)
    c, s, t = math.cos(angle), math.sin(angle), 1.0 - math.cos(angle)
    return np.array([[t * x * x + c, t * x * y - s * z, t * x * z + s * y],
                     [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
                     [t * x * z - s * y, t * y * z + s * x, t * z * z + c]])


def quaternion_from_matrix(m: np.ndarray) -> np.ndarray:
    """(w, x, y, z), Blender's order, of a 3x3 rotation."""

    m = np.asarray(m, float)
    trace = m[0, 0] + m[1, 1] + m[2, 2]
    if trace > 0:
        s = 2.0 * math.sqrt(trace + 1.0)
        q = [0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = 2.0 * math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
        q = [(m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s]
    elif m[1, 1] > m[2, 2]:
        s = 2.0 * math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
        q = [(m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s]
    else:
        s = 2.0 * math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
        q = [(m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s]
    q = np.array(q)
    return q / np.linalg.norm(q)


def matrix_from_quaternion(q: np.ndarray) -> np.ndarray:
    w, x, y, z = unit(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    a, b = unit(a), unit(b)
    if a @ b < 0:
        b = -b
    dot = float(np.clip(a @ b, -1.0, 1.0))
    if dot > 0.9995:
        return unit(a + t * (b - a))
    theta = math.acos(dot)
    return (math.sin((1 - t) * theta) * a + math.sin(t * theta) * b) / math.sin(theta)


def orthonormal(matrix: np.ndarray) -> np.ndarray:
    """A 4x4 matrix with its 3x3 part made a pure rotation (scale removed), translation kept."""

    out = np.array(matrix, float)
    u, _s, vt = np.linalg.svd(out[:3, :3])
    rotation = u @ vt
    if np.linalg.det(rotation) < 0:
        u[:, -1] *= -1
        rotation = u @ vt
    out[:3, :3] = rotation
    return out


def quaternion_step_degrees(a: np.ndarray, b: np.ndarray) -> float:
    return 2.0 * math.degrees(math.acos(min(1.0, abs(float(unit(a) @ unit(b))))))


# ---------------------------------------------------------------------------------------------
# 1. Regions
# ---------------------------------------------------------------------------------------------


def cloak_mask(positions: np.ndarray, dominant: Sequence[str], hips: np.ndarray, front: np.ndarray, up: np.ndarray, height: float) -> np.ndarray:
    """The cloak: the region TRIPO-CLOAK-STRETCH measures (`lib.tripo_checks.cloak_region`), in any up direction."""

    from lib import tripo_checks

    positions = np.asarray(positions, float)
    up = unit(up)
    # cloak_region reads heights along one axis; give it the up component in a fixed column.
    frame = np.stack([positions @ unit(np.cross(up, front)), positions @ up, positions @ unit(front)], axis=1)
    hips_frame = np.array([hips @ unit(np.cross(up, front)), hips @ up, hips @ unit(front)])
    return tripo_checks.cloak_region(frame, dominant, hips_frame, np.array([0.0, 0.0, 1.0]), height, CLOAK_BONES, up_axis=1)


def segment_distance(points: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Each point's distance to the segment from `a` to `b`."""

    points = np.asarray(points, float)
    ab = np.asarray(b, float) - np.asarray(a, float)
    t = np.clip((points - a) @ ab / max(float(ab @ ab), 1e-12), 0.0, 1.0)
    return np.linalg.norm(points - (a + np.outer(t, ab)), axis=1)


def grow_region(mask: np.ndarray, edges: np.ndarray, allowed: np.ndarray) -> np.ndarray:
    """`mask` grown along mesh edges into connected `allowed` vertices."""

    grown = np.asarray(mask, bool).copy()
    allowed = np.asarray(allowed, bool)
    edges = np.asarray(edges, int)
    while True:
        reach = np.zeros(len(grown), bool)
        reach[edges[grown[edges[:, 0]], 1]] = True
        reach[edges[grown[edges[:, 1]], 0]] = True
        new = reach & allowed & ~grown
        if not new.any():
            return grown
        grown |= new


def cloak_rebind_mask(check: np.ndarray, positions: np.ndarray, edges: np.ndarray, dominant: Sequence[str], hips: np.ndarray, front: np.ndarray,
                      up: np.ndarray, height: float, limbs: Sequence[Tuple[np.ndarray, np.ndarray, float]]) -> np.ndarray:
    """The cloak's vertices the chains take: the check's region (`cloak_mask`) grown along the mesh into loose cloth beside it.

    Tripo binds a cloak's sides to the thighs, and those sides lie less than the check's margin behind the hips. A vertex joins when it
    is connected to the region, weighted mostly to the torso, hips or thighs (`CLOAK_BONES`, as the check's region), behind the hips'
    frontal plane, between `CLOAK_LOW_SHARE` and `CLOAK_HIGH_SHARE` of the height, and farther from every limb's axis than
    `LOOSE_FACTOR` times that limb's radius (it is cloth, not the limb's own skin). Cloth Tripo bound to an arm or a shoulder stays with
    it: taking it as well made the defend clip fail UNIT-ANIM-STRETCH on the orc."""

    positions = np.asarray(positions, float)
    level = (positions @ unit(up) - float((positions @ unit(up)).min())) / max(height, 1e-12)
    behind = (positions - hips) @ unit(front) < 0
    loose = np.ones(len(positions), bool)
    for a, b, radius in limbs:
        loose &= segment_distance(positions, a, b) > LOOSE_FACTOR * radius
    allowed = behind & (level > CLOAK_LOW_SHARE) & (level < CLOAK_HIGH_SHARE) & loose & np.isin(np.asarray(dominant), CLOAK_BONES)
    return grow_region(check, edges, allowed)


def with_seams(positions: np.ndarray, edges: np.ndarray, height: float) -> np.ndarray:
    """`edges` plus a zero-length edge from each vertex to the first vertex at its position. A UV seam splits one surface point into
    several vertices with no edge between them; without these the region growth and the border blend stop at the seam, and the kit's
    checks, which weld by position, see a hard weight edge there (UNIT-BRIDGE on the demon's wing root)."""

    from lib import pdx_deform

    canon = pdx_deform.weld(np.asarray(positions, float), max(height, 1e-12) * 1e-5)
    split = np.where(canon != np.arange(len(canon)))[0]
    return np.concatenate([np.asarray(edges, int).reshape(-1, 2), np.stack([split, canon[split]], axis=1)])


def blend_length_for(joints: np.ndarray, positions: np.ndarray, edges: np.ndarray, region: np.ndarray) -> float:
    """The border blend runs over one chain bone's length, and over at least `BLEND_MIN_RINGS` of the region's median edge length."""

    bone = float(np.mean(np.linalg.norm(np.diff(joints, axis=-2), axis=-1)))
    inside = np.asarray(region, bool)[edges].all(axis=1)
    lengths = np.linalg.norm(positions[edges[inside, 0]] - positions[edges[inside, 1]], axis=1)
    lengths = lengths[lengths > 0]  # the seam joins have no length
    ring = float(np.median(lengths)) if len(lengths) else 0.0
    return max(bone, BLEND_MIN_RINGS * ring)


def is_arm_bone(name: str) -> bool:
    return any(str(name).endswith(ending) for ending in ARM_BONE_ENDINGS)


def wing_masks(positions: np.ndarray, dominant: Sequence[str], centre: np.ndarray, front: np.ndarray, up: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """(left, right) wing masks: farther from the mid-plane through `centre` than `WING_LATERAL_SHARE` of the width, arms left out.

    Left is the unit's own left (`up` x `front`)."""

    positions = np.asarray(positions, float)
    lateral = unit(np.cross(up, front))
    side = (positions - centre) @ lateral
    width = float(np.ptp(side))
    arm = np.array([is_arm_bone(name) for name in dominant], dtype=bool)
    far = np.abs(side) > WING_LATERAL_SHARE * width
    return far & ~arm & (side > 0), far & ~arm & (side < 0)


# ---------------------------------------------------------------------------------------------
# 2-3. Budget and chain shape
# ---------------------------------------------------------------------------------------------


def side_count(region: str) -> int:
    return 2 if region == "wings" else 1


def bone_budget(bones_in_rig: int, regions: Sequence[str], max_bones: int = MAX_BONES) -> int:
    """Bones each side of each requested region may use (a pair of wings is two sides)."""

    sides = sum(side_count(region) for region in regions)
    free = max_bones - bones_in_rig
    if sides == 0:
        return 0
    if free < sides * MIN_CHAINS * MIN_BONES_PER_CHAIN:
        raise ValueError(f"the rig keeps {bones_in_rig} bones; {free} are left for {sides} chain side(s), fewer than {MIN_CHAINS * MIN_BONES_PER_CHAIN} each")
    return free // sides


def chain_shape(length: float, width: float, segment: float, budget: int) -> Tuple[int, int]:
    """(chains, bones per chain) for a sheet `length` long and `width` wide, with bones about `segment` long, within `budget` bones."""

    bones = int(np.clip(math.ceil(length / max(segment, 1e-9) - 1e-9), MIN_BONES_PER_CHAIN, MAX_BONES_PER_CHAIN))
    chains = int(np.clip(math.ceil(width / max(segment, 1e-9) - 1e-9), MIN_CHAINS, MAX_CHAINS))
    while chains * bones > budget:
        if bones > WAVE_BONES:
            bones -= 1
        elif chains > MIN_CHAINS:
            chains -= 1
        elif bones > MIN_BONES_PER_CHAIN:
            bones -= 1
        else:
            raise ValueError(f"{budget} bones cannot hold {MIN_CHAINS} chains of {MIN_BONES_PER_CHAIN}")
    return chains, bones


# ---------------------------------------------------------------------------------------------
# 4. Sheet coordinates and chain placement
# ---------------------------------------------------------------------------------------------


def cloak_coordinates(points: np.ndarray, hips: np.ndarray, front: np.ndarray, up: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    """(u, s, radius): u the angle (radians) round the vertical axis through the hips, 0 straight behind; s the drop below the region's
    top; radius the region's median horizontal distance from that axis (to turn angles into lengths)."""

    points = np.asarray(points, float)
    up, back = unit(up), -unit(front)
    lateral = unit(np.cross(up, unit(front)))
    rel = points - hips
    horizontal = rel - np.outer(rel @ up, up)
    u = np.arctan2(horizontal @ lateral, horizontal @ back)
    height = points @ up
    return u, float(height.max()) - height, float(np.median(np.linalg.norm(horizontal, axis=1)))


def wing_root(points: np.ndarray, anchor: np.ndarray, share: float = 0.05) -> np.ndarray:
    """The wing's root, where it grows from the upper back: the mean of the `share` of the wing's vertices nearest the chain parent's
    joint (`anchor`, the upper spine)."""

    points = np.asarray(points, float)
    distance = np.linalg.norm(points - anchor, axis=1)
    return points[distance <= np.quantile(distance, share)].mean(axis=0)


def wing_coordinates(points: np.ndarray, root: np.ndarray, front: np.ndarray, up: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(u, s, plane): a fan round `root` in the wing's own plane (its two longest principal axes, the second turned toward `up`).

    u is the angle from the first axis (pointing away from the body), s the distance from the root. `plane` is the (2, 3) axis pair."""

    from lib import tripo_checks

    points = np.asarray(points, float)
    _centre, axes, _values = tripo_checks.principal_axes(points)
    lateral = unit(np.cross(up, front))
    first = axes[0] if axes[0] @ ((points.mean(axis=0) - root)) >= 0 else -axes[0]
    normal = unit(np.cross(axes[0], axes[1]))
    second = unit(np.cross(normal, first))
    if second @ up < 0:
        second = -second
    del lateral
    rel = points - root
    x, y = rel @ first, rel @ second
    return np.arctan2(y, x), np.sqrt(x * x + y * y), np.stack([first, second])


def even_angles(u: np.ndarray, count: int, low: float = 2.0, high: float = 98.0) -> np.ndarray:
    lo, hi = np.percentile(u, [low, high])
    return lo + (np.arange(count) + 0.5) * (hi - lo) / count


def reach_profile(u: np.ndarray, s: np.ndarray, bins: int) -> Tuple[np.ndarray, np.ndarray]:
    """(bin centres, reach): the 95th percentile of s in each of `bins` equal angle bins between the 1st and 99th percentile of u."""

    lo, hi = np.percentile(u, [1.0, 99.0])
    edges = np.linspace(lo, hi, bins + 1)
    reach = np.zeros(bins)
    for k in range(bins):
        inside = (u >= edges[k]) & (u < edges[k + 1])
        reach[k] = np.percentile(s[inside], 95) if inside.sum() >= 3 else 0.0
    return 0.5 * (edges[:-1] + edges[1:]), reach


def prominent_peaks(reach: np.ndarray, prominence: float) -> List[int]:
    """Bins whose reach is a local maximum that stands at least `prominence` above the lowest bin between it and any higher bin
    (or the profile's end) on each side."""

    peaks = []
    for k in range(1, len(reach) - 1):
        if not (reach[k] >= reach[k - 1] and reach[k] > reach[k + 1]):
            continue
        drops = []
        for step in (-1, 1):
            j, low = k + step, reach[k]
            while 0 <= j < len(reach) and reach[j] <= reach[k]:
                low = min(low, reach[j])
                j += step
            drops.append(reach[k] - low)
        if min(drops) >= prominence:
            peaks.append(k)
    return peaks


def ridge_angles(u: np.ndarray, s: np.ndarray, count: int, bins: int = 36) -> Tuple[np.ndarray, str]:
    """Chain angles: an even fan over the region (so the chains cover it edge to edge), each fan angle moved onto a ridge, where the
    region reaches farthest (a bat wing's finger), when a ridge lies within half the fan's spacing. A ridge is a peak of the reach per
    angle that stands `RIDGE_PROMINENCE` of the largest reach above its surroundings. Returns (angles sorted, a word for the report:
    "ridges" when every chain sits on one, "fan" when none does, else "fan+N ridges")."""

    fan = even_angles(u, count)
    centres, reach = reach_profile(np.asarray(u, float), np.asarray(s, float), bins)
    peaks = prominent_peaks(reach, RIDGE_PROMINENCE * float(reach.max()))
    spacing = float(fan[1] - fan[0]) if count > 1 else float(np.ptp(u))
    out, used = [], set()
    for angle in fan:
        near = [k for k in peaks if k not in used and abs(centres[k] - angle) <= spacing / 2]
        if near:
            best = min(near, key=lambda k: abs(centres[k] - angle))
            used.add(best)
            out.append(float(centres[best]))
        else:
            out.append(float(angle))
    mode = "ridges" if len(used) == count else ("fan" if not used else f"fan+{len(used)} ridges")
    return np.sort(np.array(out)), mode


def band_halfwidths(chain_u: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Half the gap to the neighbouring chain on each side (the outer chains reach to the region's edge)."""

    chain_u = np.asarray(chain_u, float)
    if len(chain_u) == 1:
        return np.array([float(np.ptp(u)) / 2 + 1e-9])
    gaps = np.diff(chain_u)
    left = np.concatenate([[chain_u[0] - float(np.min(u))], gaps / 2])
    right = np.concatenate([gaps / 2, [float(np.max(u)) - chain_u[-1]]])
    return np.maximum(np.maximum(left, right), 1e-6)


def sheet_layout(points: np.ndarray, u: np.ndarray, s: np.ndarray, chain_u: np.ndarray, bones: int) -> Tuple[np.ndarray, np.ndarray]:
    """Joint positions (chains, bones + 1, 3) and their s values (chains, bones + 1).

    A chain runs from the 1st to the 99th percentile of s in its band of u; joint k sits at the median of the band's points within half a
    bone of its s (the nearest band points by s when none are)."""

    points, u, s = np.asarray(points, float), np.asarray(u, float), np.asarray(s, float)
    half = band_halfwidths(chain_u, u)
    joints = np.zeros((len(chain_u), bones + 1, 3))
    stations = np.zeros((len(chain_u), bones + 1))
    for c, centre in enumerate(chain_u):
        band = np.abs(u - centre) <= half[c]
        if band.sum() < 3:
            band = np.argsort(np.abs(u - centre))[: max(3, len(u) // (2 * len(chain_u)))]
            band = np.isin(np.arange(len(u)), band)
        top, bottom = np.percentile(s[band], [1.0, 99.0])
        stations[c] = np.linspace(top, bottom, bones + 1)
        step = (bottom - top) / bones
        for k, station in enumerate(stations[c]):
            near = band & (np.abs(s - station) <= step / 2)
            if near.sum() == 0:
                order = np.where(band)[0][np.argsort(np.abs(s[band] - station))[:5]]
                near = np.isin(np.arange(len(u)), order)
            joints[c, k] = np.median(points[near], axis=0)
    return joints, stations


def mirror_points(points: np.ndarray, centre: np.ndarray, lateral: np.ndarray) -> np.ndarray:
    lateral = unit(lateral)
    points = np.asarray(points, float)
    return points - 2.0 * np.outer((points - centre) @ lateral, lateral) if points.ndim == 2 else points - 2.0 * ((points - centre) @ lateral) * lateral


# ---------------------------------------------------------------------------------------------
# 5. Weights
# ---------------------------------------------------------------------------------------------


def sheet_weights(u: np.ndarray, s: np.ndarray, chain_u: np.ndarray, stations: np.ndarray) -> List[Dict[int, float]]:
    """Per vertex {bone index: weight}, bone index = chain * bones + bone. Two chains (linear in u) times two bones (linear in s between
    the bones' middles): at most 4 influences, summing to 1."""

    chain_u = np.asarray(chain_u, float)
    chains, bones = stations.shape[0], stations.shape[1] - 1
    rows: List[Dict[int, float]] = []
    for value_u, value_s in zip(np.asarray(u, float), np.asarray(s, float)):
        if chains == 1 or value_u <= chain_u[0]:
            across = [(0, 1.0)]
        elif value_u >= chain_u[-1]:
            across = [(chains - 1, 1.0)]
        else:
            c = int(np.searchsorted(chain_u, value_u)) - 1
            g = (value_u - chain_u[c]) / max(chain_u[c + 1] - chain_u[c], 1e-12)
            across = [(c, 1.0 - g), (c + 1, g)]
        row: Dict[int, float] = {}
        for c, wc in across:
            top, bottom = stations[c, 0], stations[c, -1]
            t = (value_s - top) / max(bottom - top, 1e-12) * bones - 0.5  # in bone-middle units
            b = int(np.clip(math.floor(t), 0, bones - 1))
            f = float(np.clip(t - b, 0.0, 1.0)) if t >= 0 else 0.0
            if b == bones - 1:
                f = 0.0
            for bone, wb in ((b, 1.0 - f), (b + 1, f)):
                if wb > 0 and wc > 0 and bone < bones:
                    key = c * bones + bone
                    row[key] = row.get(key, 0.0) + wc * wb
        rows.append(row)
    return rows


def surface_distance(positions: np.ndarray, edges: np.ndarray, seeds: np.ndarray, limit: float, max_iterations: int = 400) -> np.ndarray:
    """Shortest distance along mesh edges from any seed vertex (0 at a seed), up to `limit` (beyond it: inf)."""

    positions = np.asarray(positions, float)
    edges = np.asarray(edges, int)
    length = np.linalg.norm(positions[edges[:, 0]] - positions[edges[:, 1]], axis=1)
    distance = np.where(np.asarray(seeds, bool), 0.0, np.inf)
    a = np.concatenate([edges[:, 0], edges[:, 1]])
    b = np.concatenate([edges[:, 1], edges[:, 0]])
    weight = np.concatenate([length, length])
    for _ in range(max_iterations):
        candidate = distance[a] + weight
        better = np.full(len(distance), np.inf)
        np.minimum.at(better, b, candidate)
        updated = np.minimum(distance, np.where(better <= limit, better, np.inf))
        if np.array_equal(updated, distance):
            break
        distance = updated
    return distance


def blend_alpha(positions: np.ndarray, edges: np.ndarray, region: np.ndarray, blend_length: float) -> np.ndarray:
    """Per vertex, the chains' share of its weight: 1 in the whole region, falling smoothly to 0 over `blend_length` of surface distance
    outward from the region's border, into the skin the region is joined to.

    The region moves whole, so it never stretches against itself. The join to the body (where Tripo's single skin fuses a cloak's sides
    to the thighs) takes the strain instead, outside the region, where the cloth hides it. A blend inside the region put 97% of the
    cloak's stretched edges in that blend on the orc."""

    region = np.asarray(region, bool)
    distance = surface_distance(positions, edges, region, blend_length)
    outside = np.where(np.isfinite(distance), 1.0 - smoothstep(distance / max(blend_length, 1e-12)), 0.0)
    return np.where(region, 1.0, outside)


def mix_weights(body: Dict[str, float], chains: Dict[str, float], alpha: float, keep: int = MAX_INFLUENCES) -> Dict[str, float]:
    """(1 - alpha) * body + alpha * chains, then the `keep` largest weights, normalised to 1."""

    mixed: Dict[str, float] = {}
    for name, weight in body.items():
        mixed[name] = mixed.get(name, 0.0) + (1.0 - alpha) * weight
    for name, weight in chains.items():
        mixed[name] = mixed.get(name, 0.0) + alpha * weight
    ranked = sorted(((n, w) for n, w in mixed.items() if w > 1e-6), key=lambda item: (-item[1], item[0]))[:keep]
    total = sum(w for _, w in ranked) or 1.0
    return {name: w / total for name, w in ranked}


# ---------------------------------------------------------------------------------------------
# 6. Motion
# ---------------------------------------------------------------------------------------------


def pendulum_omegas(lengths: Sequence[float], height: float) -> np.ndarray:
    """Per bone, the spring frequency (rad/s) of a pendulum as long as the bone: sqrt(g / L), each link of the chain swinging about its
    own joint. L is a share of the unit's height read as metres on a body `NOMINAL_HEIGHT_M` tall, so the motion is the same at any model
    scale. (A pendulum as long as the whole chain below the joint lagged twice as much and stretched the orc's cloak join past the limit
    in its defend clip.)"""

    lengths = np.asarray(lengths, float) * (NOMINAL_HEIGHT_M / max(height, 1e-12))
    return np.sqrt(GRAVITY / np.maximum(lengths, 1e-3))


def closest_on_segment(point: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ab = b - a
    t = float(np.clip((point - a) @ ab / max(ab @ ab, 1e-12), 0.0, 1.0))
    return a + t * ab


def exit_along(point: np.ndarray, a: np.ndarray, b: np.ndarray, radius: float, direction: np.ndarray, steps: int = 24) -> np.ndarray:
    """`point` moved along `direction` (a unit vector) by the least distance that takes it out of the capsule (a, b, radius)."""

    def inside(t: float) -> bool:
        moved = point + t * direction
        return float(np.linalg.norm(moved - closest_on_segment(moved, a, b))) < radius

    if not inside(0.0):
        return point
    high = 2.0 * radius + float(np.linalg.norm(b - a))
    low = 0.0
    for _ in range(steps):
        middle = 0.5 * (low + high)
        if inside(middle):
            low = middle
        else:
            high = middle
    return point + high * direction


def push_out(point: np.ndarray, capsules: Sequence[Tuple[np.ndarray, np.ndarray, float]], ground: float, up: np.ndarray, away: np.ndarray,
             passes: int = 2, along: bool = False) -> np.ndarray:
    """Move `point` out of every capsule (a, b, radius), then above `ground` along `up`. With `along` the point leaves each capsule along
    `away` (the body's back direction, so neighbouring chains are pushed alike and the cloth stays a sheet); otherwise by the shortest
    way (a point on a capsule's axis goes out along `away`)."""

    point = np.array(point, float)
    up = unit(up)
    for _ in range(passes):
        for a, b, radius in capsules:
            if radius <= 0:
                continue
            if along:
                point = exit_along(point, a, b, radius, unit(away))
                continue
            nearest = closest_on_segment(point, a, b)
            offset = point - nearest
            distance = float(np.linalg.norm(offset))
            if distance < radius:
                direction = offset / distance if distance > 1e-9 else unit(away)
                point = nearest + direction * radius
        level = float(point @ up)
        if level < ground:
            point = point + (ground - level) * up
    return point


def collide_direction(head: np.ndarray, direction: np.ndarray, length: float, capsules, ground: float, up: np.ndarray, away: np.ndarray,
                      rounds: int = 4, along: bool = False) -> np.ndarray:
    """The bone direction nearest `direction` whose tail (`length` from `head`) is out of the capsules and above the ground: the tail is
    pushed out and put back on the bone's sphere, `rounds` times. A head that is itself under the ground lays the bone flat."""

    up = unit(up)
    for _ in range(rounds):
        tail = push_out(head + direction * length, capsules, ground, up, away, along=along)
        new = tail - head
        if float(head @ up) < ground:
            new = new - (new @ up) * up
        if np.linalg.norm(new) < 1e-12:
            break
        new = unit(new)
        if np.allclose(new, direction, atol=1e-9):
            break
        direction = new
    return onto_ground(head, direction, length, ground, up, away)


def onto_ground(head: np.ndarray, direction: np.ndarray, length: float, ground: float, up: np.ndarray, away: np.ndarray) -> np.ndarray:
    """Keep the tail at or above `ground`: a bone whose tail would sink is turned in its vertical plane until the tail touches the
    ground (or lies flat when the head is at or under it)."""

    up = unit(up)
    if float((head + direction * length) @ up) >= ground:
        return direction
    flat = direction - (direction @ up) * up
    if np.linalg.norm(flat) < 1e-9:
        flat = unit(away) - (unit(away) @ up) * up
    flat = unit(flat)
    drop = float(head @ up) - ground
    if drop <= 0:
        return flat
    vertical = -min(drop / max(length, 1e-12), 1.0)
    return unit(vertical * up + math.sqrt(max(1.0 - vertical * vertical, 0.0)) * flat)


def chain_forward(parent: np.ndarray, rest_relative: np.ndarray, directions: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Forward kinematics of one chain whose bones point along `directions` (bones, 3).

    `parent` is the 4x4 world matrix (rotation and translation only) of the chain's parent bone, `rest_relative` (bones, 4, 4) each bone's
    rest matrix relative to its parent (Blender bones point along local +Y). Returns (local quaternions (bones, 4) w-first, heads
    (bones, 3), world matrices (bones, 4, 4))."""

    matrices = np.zeros((len(directions), 4, 4))
    quaternions = np.zeros((len(directions), 4))
    heads = np.zeros((len(directions), 3))
    current = np.asarray(parent, float)
    for k, direction in enumerate(directions):
        unposed = current @ rest_relative[k]
        rigid = unit(unposed[:3, 1])
        turn = shortest_arc(rigid, direction)
        local = unposed[:3, :3].T @ turn @ unposed[:3, :3]
        quaternions[k] = quaternion_from_matrix(local)
        posed = unposed.copy()
        posed[:3, :3] = turn @ unposed[:3, :3]
        matrices[k] = posed
        heads[k] = posed[:3, 3]
        current = posed
    return quaternions, heads, matrices


def spring_step(d: np.ndarray, v: np.ndarray, target: np.ndarray, omega: float, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    """One frame of a critically damped spring on a unit direction `d` with rate `v`, toward `target`, in `SUBSTEPS` steps."""

    h = dt / SUBSTEPS
    for _ in range(SUBSTEPS):
        acceleration = omega ** 2 * (target - d) - 2.0 * omega * v
        v = v + acceleration * h
        d = unit(d + v * h)
        v = v - (v @ d) * d
    return d, v


def collide_step(head, d, v, length, capsules, ground, up, away, along=False) -> Tuple[np.ndarray, np.ndarray]:
    """Push the bone out of the capsules and above the ground; drop the part of its rate that points back in."""

    free = d
    d = collide_direction(head, d, length, capsules, ground, up, away, along=along)
    pushed = d - free
    if np.linalg.norm(pushed) > 1e-9:
        n = unit(pushed)
        inward = v @ n
        if inward < 0:
            v = v - inward * n
    return d, v


def simulate_chain(
    parents: np.ndarray,
    rest_relative: np.ndarray,
    lengths: np.ndarray,
    omegas: np.ndarray,
    dt: float,
    target,
    capsule_axes: Optional[np.ndarray] = None,
    radii: Optional[np.ndarray] = None,
    ground: float = -np.inf,
    up: np.ndarray = Z_UP,
    away: Optional[np.ndarray] = None,
    passes: int = 1,
    push_along: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """Per frame, the local quaternions (frames, bones, 4) and joint positions (frames, bones + 1, 3) of one chain.

    `target(frame, bone, head, rigid)` gives the direction bone `bone` seeks in that frame, from its head and its rigid direction (where
    its parent carries it). Each bone follows it with a critically damped spring at `omegas[k]` (rad/s), then its tail is pushed out of
    that frame's capsules (`capsule_axes` (frames, capsules, 2, 3), the radius per bone tail and capsule in `radii` (bones, capsules)) and
    above `ground` along `up`. `away` is one direction or one per frame; with `push_along` a joint leaves a capsule along it. With `passes` > 1 the clip runs that many times in a row from rest and the last run is returned (a looping
    clip settles into its cycle)."""

    frames, bones = parents.shape[0], len(lengths)
    away = unit(np.asarray(away, float)) if away is not None else unit(up)
    state_d, state_v = np.zeros((bones, 3)), np.zeros((bones, 3))
    out_q = np.zeros((frames, bones, 4))
    out_j = np.zeros((frames, bones + 1, 3))
    collide = capsule_axes is not None or np.isfinite(ground)
    for run in range(passes):
        for f in range(frames):
            current = parents[f]
            for k in range(bones):
                unposed = current @ rest_relative[k]
                head, rigid = unposed[:3, 3], unit(unposed[:3, 1])
                goal = target(f, k, head, rigid)
                if run == 0 and f == 0:
                    d, v = goal, np.zeros(3)
                else:
                    d, v = spring_step(state_d[k], state_v[k], goal, float(omegas[k]), dt)
                if collide:
                    capsules = [] if capsule_axes is None else [(axis[0], axis[1], float(radii[k, c])) for c, axis in enumerate(capsule_axes[f])]
                    d, v = collide_step(head, d, v, float(lengths[k]), capsules, ground, up, away[f] if away.ndim == 2 else away, push_along)
                state_d[k], state_v[k] = d, v
                turn = shortest_arc(rigid, d)
                out_q[f, k] = quaternion_from_matrix(unposed[:3, :3].T @ turn @ unposed[:3, :3])
                out_j[f, k] = head
                current = unposed.copy()
                current[:3, :3] = turn @ unposed[:3, :3]
            out_j[f, bones] = out_j[f, bones - 1] + state_d[bones - 1] * lengths[bones - 1]
    return continuous_quaternions(out_q), out_j


def exit_distance(point: np.ndarray, capsules, direction: np.ndarray) -> float:
    """How far `point` must move along `direction` to leave every capsule (two passes, as `push_out`)."""

    moved = np.array(point, float)
    for _ in range(2):
        for a, b, radius in capsules:
            if radius > 0:
                moved = exit_along(moved, a, b, radius, direction)
    return float((moved - point) @ direction)


def hang_below_horizon(direction: np.ndarray, up: np.ndarray) -> np.ndarray:
    """Gravity's rule for cloth: it never points above the horizontal. A direction that would rise is laid flat (its upward part
    removed), so a cloak on a body lying face down lies on the back instead of standing up from it. A world-gravity pull instead made
    the orc's cloak go into its body when the torso turned."""

    rise = float(direction @ up)
    if rise <= 0:
        return direction
    flat = direction - rise * up
    return unit(flat) if np.linalg.norm(flat) > 1e-9 else direction


def spread_pushes(pushes: np.ndarray, spread: float = SHEET_SPREAD) -> np.ndarray:
    """Each chain's push is at least `spread` to the power of the chain distance times any other chain's push: cloth carries a push to
    its neighbours, so a heel that pushes one chain back takes the chains beside it along and the sheet does not tear between them."""

    pushes = np.asarray(pushes, float)
    out = pushes.copy()
    for c in range(len(pushes)):
        for other in range(len(pushes)):
            out[c] = max(out[c], pushes[other] * spread ** abs(c - other))
    return out


def simulate_sheet(parents: np.ndarray, chains: Sequence[dict], dt: float, capsule_axes: Optional[np.ndarray], ground: float, up: np.ndarray,
                   away: np.ndarray, passes: int = 1) -> List[np.ndarray]:
    """The cloak rule for all its chains at once. Per frame and per bone index, every chain's bone springs toward the point the body's
    skinning carries its tail to (`follow_points`), then the chains are pushed out of the capsules along the body's back direction
    (`away`, one per frame) by the spread pushes (`spread_pushes`), never aimed above the horizontal, and kept above the ground. Each chain dict holds `rest_relative`,
    `lengths`, `omegas`, `follow_points` (frames, bones, 3) and `radii` (bones, capsules). Returns each chain's local quaternions
    (frames, bones, 4). With `passes` > 1 the clip runs that many times and the last run is kept (a looping clip settles)."""

    frames = parents.shape[0]
    bones = len(chains[0]["lengths"])
    count = len(chains)
    up = unit(up)
    state_d = np.zeros((count, bones, 3))
    state_v = np.zeros((count, bones, 3))
    out = [np.zeros((frames, bones, 4)) for _ in chains]
    for run in range(passes):
        for f in range(frames):
            current = [parents[f]] * count
            direction = unit(np.asarray(away[f] if np.ndim(away) == 2 else away, float))
            for k in range(bones):
                unposed = [current[c] @ chains[c]["rest_relative"][k] for c in range(count)]
                heads = np.array([m[:3, 3] for m in unposed])
                rigids = np.array([unit(m[:3, 1]) for m in unposed])
                for c, chain in enumerate(chains):
                    goal = chain["follow_points"][f, k] - heads[c]
                    goal = hang_below_horizon(unit(goal) if np.linalg.norm(goal) > 1e-9 else rigids[c], up)
                    if run == 0 and f == 0:
                        state_d[c, k], state_v[c, k] = goal, np.zeros(3)
                    else:
                        state_d[c, k], state_v[c, k] = spring_step(state_d[c, k], state_v[c, k], goal, float(chain["omegas"][k]), dt)
                if capsule_axes is not None:
                    tails = heads + state_d[:, k] * np.array([chain["lengths"][k] for chain in chains])[:, None]
                    pushes = np.array([exit_distance(tails[c], [(axis[0], axis[1], float(chains[c]["radii"][k, i])) for i, axis in enumerate(capsule_axes[f])], direction)
                                       for c in range(count)])
                    pushes = spread_pushes(pushes)
                    for c, chain in enumerate(chains):
                        if pushes[c] <= 0:
                            continue
                        moved = unit(tails[c] + pushes[c] * direction - heads[c])
                        capsules = [(axis[0], axis[1], float(chain["radii"][k, i])) for i, axis in enumerate(capsule_axes[f])]
                        state_d[c, k], state_v[c, k] = collide_step(heads[c], moved, state_v[c, k], float(chain["lengths"][k]), capsules, ground, up, direction, along=True)
                for c, chain in enumerate(chains):
                    state_d[c, k] = onto_ground(heads[c], state_d[c, k], float(chain["lengths"][k]), ground, up, direction)
                    turn = shortest_arc(rigids[c], state_d[c, k])
                    out[c][f, k] = quaternion_from_matrix(unposed[c][:3, :3].T @ turn @ unposed[c][:3, :3])
                    posed = unposed[c].copy()
                    posed[:3, :3] = turn @ unposed[c][:3, :3]
                    current[c] = posed
    return [continuous_quaternions(q) for q in out]


def torso_follow_weights(tails: np.ndarray, spine_head: np.ndarray, hips_head: np.ndarray, up: np.ndarray) -> List[Dict[str, float]]:
    """The cloak's follow rule: a joint at the upper spine's height follows `CHAIN_PARENT`, one at the hips' height or below follows the
    hips, and a joint between them follows both in proportion to its height. The cloth hangs from the shoulders and swings with the
    pelvis, not with a thigh or an arm."""

    up = unit(up)
    top, bottom = float(spine_head @ up), float(hips_head @ up)
    out = []
    for tail in np.asarray(tails, float):
        share = float(np.clip((float(tail @ up) - bottom) / max(top - bottom, 1e-12), 0.0, 1.0))
        out.append({name: weight for name, weight in ((CHAIN_PARENT, share), ("Hips", 1.0 - share)) if weight > 0})
    return out


def follow_targets(rest_points: np.ndarray, weights: Sequence[Dict[str, float]], skinning: Dict[str, np.ndarray]) -> np.ndarray:
    """(frames, points, 3): each rest point carried by linear blend skinning with its weights. `skinning[bone]` is (frames, 4, 4), the
    bone's posed world matrix times the inverse of its rest world matrix."""

    rest_points = np.asarray(rest_points, float)
    frames = next(iter(skinning.values())).shape[0]
    out = np.zeros((frames, len(rest_points), 3))
    homogeneous = np.concatenate([rest_points, np.ones((len(rest_points), 1))], axis=1)
    for j, row in enumerate(weights):
        for name, weight in row.items():
            out[:, j] += weight * (skinning[name] @ homogeneous[j])[:, :3]
    return out


def continuous_quaternions(quaternions: np.ndarray) -> np.ndarray:
    """Keep each bone's keys on one hemisphere (q and -q are one rotation; a flip between keys makes the game turn the long way)."""

    out = np.array(quaternions, float)
    for f in range(1, out.shape[0]):
        flip = np.einsum("...i,...i->...", out[f], out[f - 1]) < 0
        out[f][flip] *= -1
    return out


def close_loop(quaternions: np.ndarray, window: Optional[int] = None) -> np.ndarray:
    """Ease the last `window` frames (a quarter of the clip, at most 12) onto the first frame, so the last key equals the first."""

    frames = quaternions.shape[0]
    window = window if window is not None else max(2, min(12, frames // 4))
    out = np.array(quaternions, float)
    for i in range(frames - window, frames):
        weight = float(smoothstep((i - (frames - 1 - window)) / window))
        for index in np.ndindex(out.shape[1:-1]):
            out[(i,) + index] = slerp(quaternions[(i,) + index], quaternions[(0,) + index], weight)
    return continuous_quaternions(out)


def fastest_step(quaternions: np.ndarray) -> float:
    """The largest turn (degrees) of any bone between two neighbouring frames."""

    worst = 0.0
    for f in range(1, quaternions.shape[0]):
        for index in np.ndindex(quaternions.shape[1:-1]):
            worst = max(worst, quaternion_step_degrees(quaternions[(f,) + index], quaternions[(f - 1,) + index]))
    return worst


def capsule_radius(points: np.ndarray, a: np.ndarray, b: np.ndarray, percentile: float = CAPSULE_PERCENTILE) -> float:
    """A body capsule's radius: the `percentile` of its own vertices' distance to the bone segment."""

    points = np.asarray(points, float)
    if not len(points):
        return 0.0
    ab = b - a
    t = np.clip((points - a) @ ab / max(ab @ ab, 1e-12), 0.0, 1.0)
    return float(np.percentile(np.linalg.norm(points - (a + np.outer(t, ab)), axis=1), percentile))


def clearance_radii(joints: np.ndarray, capsules: Sequence[Tuple[np.ndarray, np.ndarray, float]], margin: float) -> np.ndarray:
    """Per joint and capsule, the radius the collision uses: the capsule's radius plus `margin`, but never more than the joint's own rest
    distance to the capsule's axis (the rest pose is never pushed). Shape (joints, capsules)."""

    joints = np.asarray(joints, float).reshape(-1, 3)
    out = np.zeros((len(joints), len(capsules)))
    for j, joint in enumerate(joints):
        for c, (a, b, radius) in enumerate(capsules):
            rest = float(np.linalg.norm(joint - closest_on_segment(joint, a, b)))
            out[j, c] = min(radius + margin, rest)
    return out


# ---------------------------------------------------------------------------------------------
# Wings: fold and flap per role
# ---------------------------------------------------------------------------------------------

# Per role: `fold` 0 spread as at rest, 1 folded against the back; `fold_end` the fold at the clip's end when it changes (death); `flap`
# the flap amplitude in degrees at the chain roots; `beats` the flap cycles in the clip (a whole number, so a looping clip loops); `beat`
# a single strong beat over the clip (attack). Defend wraps the wings forward (`wrap`, a share of the fold's back swing, turned forward).
# Rules: idle half folded with one slow breath per loop; move folded with small quick beats; attack spread with one strong beat at the
# strike; defend wrapped forward round the body; retreat half spread, flapping hard; death closes the fan without swinging back (`sweep`
# 0: a body that ends face down would hold swept-back wings up in the air) and lets the whole wing sag about the shoulder's front axis
# (`droop`, degrees), rigidly, so the membrane keeps its shape and the wings lie flat when the body does.
WING_ROLES: Dict[str, Dict[str, float]] = {
    "idle": {"fold": 0.5, "flap": 6.0, "beats": 1},
    "move": {"fold": 0.8, "flap": 8.0, "beats": 2},
    "attack": {"fold": 0.0, "flap": 30.0, "beats": 0, "beat": 1.0},
    "defend": {"fold": 0.3, "flap": 4.0, "beats": 1, "wrap": 0.6},
    "retreat": {"fold": 0.3, "flap": 25.0, "beats": 3},
    "death": {"fold": 0.0, "fold_end": 1.0, "flap": 0.0, "beats": 0, "sweep": 0.0, "droop": 30.0},
}
WING_DEFAULT_ROLE = "idle"
# A folded fan keeps 70% of its spread: the membrane between two chains never narrows past the kit's squash limit (two thirds).
FAN_CLOSE_SHARE = 0.3
FLAP_DELAY = 0.15  # each bone down a chain lags its parent by this share of a flap cycle (the wave runs out to the tip)
FLAP_FALLOFF = 0.6  # each bone down a chain flaps this share of its parent's amplitude... on top of what the parent carries


def wing_role_pose(role: str, frames: int) -> Dict[str, np.ndarray]:
    """Per frame: the fold (0..1), the wrap (0..1), the flap phase (radians) and amplitude (degrees) of the chain roots, the share of the
    back swing a fold makes (`sweep`) and the whole wing's sag in degrees (`droop`)."""

    rule = WING_ROLES.get(role, WING_ROLES[WING_DEFAULT_ROLE])
    t = np.linspace(0.0, 1.0, frames) if frames > 1 else np.zeros(1)
    fold = np.full(frames, rule.get("fold", 0.0))
    if "fold_end" in rule:
        fold = rule["fold"] + (rule["fold_end"] - rule["fold"]) * smoothstep(t / 0.8)
    wrap = np.full(frames, rule.get("wrap", 0.0))
    if rule.get("wrap"):
        wrap = rule["wrap"] * smoothstep(np.minimum(t / 0.3, 1.0)) * smoothstep(np.minimum((1.0 - t) / 0.3, 1.0))
    amplitude = np.full(frames, rule.get("flap", 0.0))
    beats = rule.get("beats", 0)
    if rule.get("beat"):
        # one beat: up during the wind-up, a strong down-stroke at the strike, back to rest; the clip starts and ends at rest
        phase = 2.0 * math.pi * t
        amplitude = amplitude * np.sin(math.pi * t)
    else:
        phase = 2.0 * math.pi * beats * t
    droop = rule.get("droop", 0.0) * smoothstep(t / 0.8)
    return {"fold": fold, "wrap": wrap, "phase": phase, "amplitude": amplitude, "sweep": np.full(frames, rule.get("sweep", 1.0)), "droop": droop}


def flap_angles(phase: np.ndarray, amplitude: np.ndarray, bones: int) -> np.ndarray:
    """(frames, bones) flap angle in degrees per bone: a sine delayed `FLAP_DELAY` of a cycle per bone, the root at full `amplitude`
    and each bone below at `FLAP_FALLOFF` of the one above (it also rides its parent's turn)."""

    out = np.zeros((len(phase), bones))
    for k in range(bones):
        out[:, k] = amplitude * (FLAP_FALLOFF ** k) * np.sin(phase - 2.0 * math.pi * FLAP_DELAY * k)
    return out


def wing_sweep_degrees(reach: float, torso_radius: float) -> float:
    """How far a folded wing swings back about the upper spine: until it lies along the back, held off it by the torso's radius
    (90 degrees less the angle the torso's radius takes at the wing's reach)."""

    return 90.0 - math.degrees(math.asin(min(1.0, torso_radius / max(reach, 1e-9))))


def wing_pose_directions(rest_directions: np.ndarray, chain_u: float, u_min: float, normal: np.ndarray, up: np.ndarray, front: np.ndarray,
                         fold: float, wrap: float, flaps: np.ndarray, sweep_degrees: float, sweep_share: float = 1.0) -> np.ndarray:
    """A left wing chain's bone directions (bones, 3) in one frame's pose, in the rest pose's space.

    Fold closes the fan by `FAN_CLOSE_SHARE` (each chain turns in the wing's plane, about `normal`, toward the lowest chain's angle
    `u_min`) and swings the wing
    back about `up` by `sweep_degrees`; wrap swings it forward instead. The flap turns bone k about the body's front axis by the sum of
    the flap angles of bone 0 to k (a positive angle raises a left wing)."""

    up, front = unit(up), unit(front)
    close = axis_angle_matrix(normal, fold * FAN_CLOSE_SHARE * (u_min - chain_u))
    swing = axis_angle_matrix(up, math.radians(sweep_degrees) * (sweep_share * fold - wrap))
    out = np.zeros_like(np.asarray(rest_directions, float))
    for k, direction in enumerate(np.asarray(rest_directions, float)):
        flap = axis_angle_matrix(front, math.radians(float(np.sum(flaps[: k + 1]))))
        out[k] = unit(swing @ flap @ close @ direction)
    return out


def mirror_directions(directions: np.ndarray, lateral: np.ndarray) -> np.ndarray:
    lateral = unit(lateral)
    directions = np.asarray(directions, float)
    return directions - 2.0 * np.outer(directions @ lateral, lateral)


def wing_quaternions(plan: dict, parents: np.ndarray, role: str, stage: dict) -> np.ndarray:
    """(frames, bones, 4) local quaternions of one wing chain for a role clip: the role's fold, wrap and flap (`WING_ROLES`) carried by
    the upper spine, each bone kept above the ground."""

    frames, bones = parents.shape[0], len(plan["lengths"])
    pose = wing_role_pose(role, frames)
    flaps = flap_angles(pose["phase"], pose["amplitude"], bones)
    flaps[:, 0] -= pose["droop"]  # the root's turn carries the whole wing (the flap angles add up down the chain)
    wing = plan["wing"]
    lateral = unit(np.cross(stage["up"], stage["front"]))
    rest = np.asarray(plan["rest_directions"], float)
    left_rest = mirror_directions(rest, lateral) if plan["side"] == "R" else rest
    parent_rest = np.asarray(plan["parent_rest"], float)
    out = np.zeros((frames, bones, 4))
    for f in range(frames):
        posed = wing_pose_directions(left_rest, plan["chain_u"], wing["u_min"], wing["normal"], stage["up"], stage["front"],
                                     float(pose["fold"][f]), float(pose["wrap"][f]), flaps[f], wing["sweep"], float(pose["sweep"][f]))
        if plan["side"] == "R":
            posed = mirror_directions(posed, lateral)
        carry = parents[f][:3, :3] @ parent_rest[:3, :3].T
        current = parents[f]
        for k in range(bones):
            unposed = current @ plan["rest_relative"][k]
            head, rigid = unposed[:3, 3], unit(unposed[:3, 1])
            direction = onto_ground(head, unit(carry @ posed[k]), float(plan["lengths"][k]), stage["ground"], stage["up"], -stage["front"])
            turn = shortest_arc(rigid, direction)
            out[f, k] = quaternion_from_matrix(unposed[:3, :3].T @ turn @ unposed[:3, :3])
            current = unposed.copy()
            current[:3, :3] = turn @ unposed[:3, :3]
    return continuous_quaternions(out)


# ---------------------------------------------------------------------------------------------
# Measurements for the checks
# ---------------------------------------------------------------------------------------------


def chain_bones(names: Iterable[str], region: Optional[str] = None) -> List[str]:
    prefixes = [REGION_PREFIX[region]] if region else list(REGION_PREFIX.values())
    return [name for name in names if any(str(name).startswith(prefix) for prefix in prefixes)]


def inside_share_series(frames: Sequence[np.ndarray], triangles: np.ndarray, body: np.ndarray, region: np.ndarray, height: float, margin_share: float, max_points: int = 400) -> List[float]:
    """Per frame: the share of region points (at most `max_points`, evenly spaced) deeper than `margin_share` of the height inside the
    rest of the body (the triangles whose three vertices are all in `body`). Uses the kit's ray-parity inside test (tripo/clip_check.py)."""

    import clip_check as cc

    body_triangles = triangles[np.asarray(body, bool)[triangles].all(axis=1)]
    index = np.where(region)[0]
    if not len(index) or not len(body_triangles):
        return [0.0 for _ in frames]
    index = index[np.linspace(0, len(index) - 1, min(max_points, len(index))).astype(int)]
    body_index = np.unique(body_triangles)
    out = []
    for posed in frames:
        points = posed[index]
        lo, hi = posed[body_index].min(axis=0), posed[body_index].max(axis=0)
        near = np.all((points >= lo) & (points <= hi), axis=1)
        inside = np.zeros(len(points), dtype=bool)
        if near.any():
            inside[near] = cc.points_inside_mesh(points[near], posed[body_triangles])
        deep = 0
        if inside.any():
            depth = cc.nearest_vertex_distance(points[inside], posed[body_index]) / height
            deep = int((depth > margin_share).sum())
        out.append(deep / len(points))
    return out


def below_ground_series(frames: Sequence[np.ndarray], region: np.ndarray, ground: float, height: float, margin_share: float, up_axis: int = 1) -> List[float]:
    """Per frame: the share of region vertices lower than `ground` by more than `margin_share` of the height."""

    return [float(np.mean(posed[np.asarray(region, bool), up_axis] < ground - margin_share * height)) if np.any(region) else 0.0 for posed in frames]
