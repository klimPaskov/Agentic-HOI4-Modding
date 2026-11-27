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
6. Motion. Cloak (`simulate_sheet`): each chain bone's tail follows the upper spine and the hips by its height, a side chain below the
   hips a little of its side's thigh too (`torso_follow_weights`, `SIDE_THIGH_SHARE`),
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
# The chains keep off the room an arm swings through: nearer to the arm in some frame of the clips than this many times its radius.
ARM_CLEAR_FACTOR = 1.5
# The chain weights blend into the body's over one chain bone, and over at least this many edge rings on a coarse mesh.
BLEND_MIN_RINGS = 4
# A thick wing (feathers laid over each other) blends into the back over at least this many times its own thickness. The wing swings at
# the root, and the skin that carries the swing stretches by the swing's angle times its distance from the axis over the length it spreads
# on: one chain bone was enough for the demon's and the devil's membranes (0.016 and 0.014 of the height thick, blends 0.21 and 0.18) and
# left 19.9% of the angel's root edges stretched in the idle's fold (0.073 thick, blend 0.15), 2.2% at 0.45 (tripo/chain_replay.py on run
# angel_a, 2026-11-23: blends of 1, 2, 3 and 5 times that bone gave 19.9%, 6.2%, 2.2% and 4.1%).
BLEND_THICKNESS_FACTOR = 6.0
# A wing thicker than this share of the unit's height is a slab of feathers, not a membrane (0.014 to 0.016 measured on a bat wing, 0.073 on
# feathers). A slab moves whole: its bones are not pushed off the ground one by one (the angel's death stretched 10.2% of the wing's edges
# with the push, 0.7% without it, 2026-11-23), the ground pass turns a wing that reaches under the ground up about its root.
THICK_WING_SHARE = 0.04
# The wing's thickness is measured over cells of this share of the unit's height.
THICKNESS_CELL_SHARE = 0.03
MIN_BONES_PER_CHAIN, MAX_BONES_PER_CHAIN = 2, 4
MIN_CHAINS, MAX_CHAINS = 2, 6
# A wing ridge (a finger) stands this share of the wing's largest reach above the angles beside it; smaller bumps are a ragged edge.
RIDGE_PROMINENCE = 0.05
# A wing's arm (its leading edge) is the top of its outer half: this percentile of the angles there. RIDGE_BAND_SHARE of the gap to the next
# chain either side of it takes the arm's chain whole.
LEADING_EDGE_PERCENTILE = 90.0
RIDGE_BAND_SHARE = 0.25
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

# The front-view cover test (TRIPO-WING-FRONT): screen cells this share of the height wide, and a wing point hides the torso there when it is
# this share of the height nearer the camera than the torso's front surface.
COVER_CELL_SHARE = 0.02
COVER_MARGIN_SHARE = 0.01
# A fold is limited by what it does to the skin, with the body at rest (`fold_room`). Its back swing may stretch or squash no more than
# FOLD_ROOT_LIMIT of the wing root's edges (where the chains blend into the back and shoulder) by UNIT-ANIM-STRETCH's measure, and its fan's
# close may change no more than FOLD_DEFORM_LIMIT of all the edges the chains move by FOLD_DEFORM_RATIO (the review sheets' yellow, 1.3
# times, by 0.5% of the height). Judged on the demon: the round 3 fold (83 degrees back, the fan closed by 30%) changed 12% of the moved
# edges and the review saw the membrane crumpled and the roots stretched. With the wing grown to the back, 80 degrees stretched 5% of the
# root's edges and the clips showed a red band over both shoulders; 50 degrees, 0.3%.
FOLD_ROOT_LIMIT = 0.01
FOLD_DEFORM_RATIO = 1.3
FOLD_DEFORM_LIMIT = 0.01
FOLD_CLOSE_STEP = 0.025
FOLD_SWEEP_STEP = 5.0
# The torso lies (`lying_share`) once its hips-to-upper-spine axis is less than LIE_UPRIGHT vertical, fully once under LIE_FLAT.
LIE_UPRIGHT, LIE_FLAT = 0.7, 0.35
# The drape of a lying body turns each cloak bone's goal toward straight down by DRAPE_MAX_SHARE of the lying share. From
# DRAPE_COLLIDE_SHARE of drape on, a bone would leave a capsule by the shortest way instead of being pushed along the back direction;
# above 1 it never does. Measured on the orc's death by `tripo/chain_replay.py` (the replay matched the Blender run within a point):
# that collision stretched 15.7% of the cloak (limit 5%), a full downward goal without it 9.9%, a goal capped at 0.6 of it 3.7%, the same
# as no drape, and 0.7 already 4.2%.
DRAPE_MAX_SHARE = 0.6
DRAPE_COLLIDE_SHARE = 1.01
# Prefix of the bones each region adds; the checks find a region's vertices by them too.
REGION_PREFIX = {"cloak": "Cloak", "wings": "Wing"}
# `plates` adds no bones: it binds each armour plate rigidly to one bone (`rigid_plates`).
REGIONS = tuple(REGION_PREFIX) + ("plates",)


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


def arm_room(positions: np.ndarray, parts: Sequence[Tuple[np.ndarray, float]], factor: Optional[float] = None) -> np.ndarray:
    """The vertices an arm passes through or lies against in some frame: nearer than `factor` (`ARM_CLEAR_FACTOR`) times the part's radius
    to any of its segments. `parts` holds per arm part (upper arm, forearm, hand) its segments (N, 2, 3), every pose it takes in the clips
    carried back into the rest pose by the upper spine, and its radius."""

    factor = ARM_CLEAR_FACTOR if factor is None else factor
    positions = np.asarray(positions, float)
    out = np.zeros(len(positions), bool)
    for segments, radius in parts:
        if radius <= 0 or not len(segments):
            continue
        limit = factor * radius
        # poses closer than half the limit to one already kept add nothing a vertex could notice
        keys = np.unique(np.floor(np.asarray(segments, float).reshape(len(segments), 6) / (0.5 * limit)).astype(np.int64), axis=0, return_index=True)[1]
        for a, b in np.asarray(segments, float)[np.sort(keys)]:
            lo, hi = np.minimum(a, b) - limit, np.maximum(a, b) + limit
            near = np.all((positions >= lo) & (positions <= hi), axis=1) & ~out
            if near.any():
                index = np.where(near)[0]
                out[index[segment_distance(positions[index], a, b) < limit]] = True
    return out


def collar_zone(positions: np.ndarray, up: np.ndarray, shoulder_line: float) -> np.ndarray:
    """The collar: everything above the lower of the two shoulder joints. A cloak's chains hang from below it, so the collar follows the
    neck and shoulders (or a plate) and a head that bows forward does not sink into a collar the chains hold back."""

    return np.asarray(positions, float) @ unit(up) > shoulder_line


def wing_rebind_mask(far: np.ndarray, positions: np.ndarray, edges: np.ndarray, dominant: Sequence[str], shoulders: np.ndarray, front: np.ndarray,
                     capsules: Sequence[Tuple[np.ndarray, np.ndarray, float]]) -> np.ndarray:
    """The wing the chains take: the far region (`wing_masks`) grown along the mesh into the inner wing that joins it to the back, every
    connected vertex behind the shoulders' frontal plane that is loose from the body (farther from every capsule's axis than
    `LOOSE_FACTOR` times its radius: the torso, the head and each limb) and not a limb end. Tripo binds a wing's inner arm to the upper
    arm or the shoulder; left out of the region it stayed rigid with the body, a rod from the shoulder to where the chains began, and the
    chains turned about a root a third of the height out from the spine."""

    positions = np.asarray(positions, float)
    behind = (positions - np.asarray(shoulders, float)) @ unit(front) < 0
    loose = np.ones(len(positions), bool)
    for a, b, radius in capsules:
        if radius > 0:
            loose &= segment_distance(positions, a, b) > LOOSE_FACTOR * radius
    ends = np.array([is_limb_end(name) for name in dominant], dtype=bool)
    return grow_region(far, edges, behind & loose & ~ends)


def with_seams(positions: np.ndarray, edges: np.ndarray, height: float) -> np.ndarray:
    """`edges` plus a zero-length edge from each vertex to the first vertex at its position. A UV seam splits one surface point into
    several vertices with no edge between them; without these the region growth and the border blend stop at the seam, and the kit's
    checks, which weld by position, see a hard weight edge there (UNIT-BRIDGE on the demon's wing root)."""

    from lib import pdx_deform

    canon = pdx_deform.weld(np.asarray(positions, float), max(height, 1e-12) * 1e-5)
    split = np.where(canon != np.arange(len(canon)))[0]
    return np.concatenate([np.asarray(edges, int).reshape(-1, 2), np.stack([split, canon[split]], axis=1)])


def region_thickness(points: np.ndarray, height: float) -> float:
    """The median thickness of a sheet-like region: the extent of its points along the sheet's normal (the smallest axis of the points'
    spread) in each cell of `THICKNESS_CELL_SHARE` of `height` across the sheet, over the cells that hold at least 4 points. A membrane
    reads 0.014 to 0.016 of the height, a wing of feathers laid over each other 0.073."""

    points = np.asarray(points, float)
    if len(points) < 8:
        return 0.0
    _u, _s, axes = np.linalg.svd(points - points.mean(axis=0), full_matrices=False)
    local = (points - points.mean(axis=0)) @ axes.T
    cell = max(THICKNESS_CELL_SHARE * height, 1e-12)
    key = np.floor(local[:, :2] / cell).astype(int)
    order = np.lexsort((key[:, 1], key[:, 0]))
    key, across = key[order], local[order, 2]
    start = np.r_[0, np.where(np.any(np.diff(key, axis=0) != 0, axis=1))[0] + 1, len(key)]
    extents = [across[a:b].max() - across[a:b].min() for a, b in zip(start[:-1], start[1:]) if b - a >= 4]
    return float(np.median(extents)) if extents else 0.0


def is_slab(thickness: float, height: float) -> bool:
    """A wing thicker than `THICK_WING_SHARE` of the unit's height is a slab of feathers. Every slab rule is gated on this, so a membrane wing
    keeps the rules it was calibrated on."""

    return float(thickness) > THICK_WING_SHARE * float(height)


def blend_length_for(joints: np.ndarray, positions: np.ndarray, edges: np.ndarray, region: np.ndarray, thickness: float = 0.0, height: float = 1.0) -> float:
    """The border blend runs over one chain bone's length, over at least `BLEND_MIN_RINGS` of the region's median edge length, and over at
    least `BLEND_THICKNESS_FACTOR` times the region's `thickness` when that is a slab (`is_slab`)."""

    bone = float(np.mean(np.linalg.norm(np.diff(joints, axis=-2), axis=-1)))
    return max(bone, BLEND_MIN_RINGS * ring_length(positions, edges, region), BLEND_THICKNESS_FACTOR * thickness if is_slab(thickness, height) else 0.0)


def ring_length(positions: np.ndarray, edges: np.ndarray, region: np.ndarray) -> float:
    """The median length of the region's edges (one ring of the mesh there)."""

    inside = np.asarray(region, bool)[edges].all(axis=1)
    lengths = np.linalg.norm(positions[edges[inside, 0]] - positions[edges[inside, 1]], axis=1)
    lengths = lengths[lengths > 0]  # the seam joins have no length
    return float(np.median(lengths)) if len(lengths) else 0.0


def is_limb_end(name: str) -> bool:
    """A forearm, hand, shin or foot: skin that moves on its own and that a chain's blend ring never reaches. On the orc the cloak's ring
    reached the right hand that rests against it, and the released axe then measured 22.6% of the height off that hand in the death
    (UNIT-LOOSE-PART), against 15.2% before."""

    name = str(name)
    return name.endswith(("ForeArm", "Hand", "Foot", "ToeBase")) or name in ("LeftLeg", "RightLeg")


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
    """Chain sides a region needs bones for: two wings, one cloak, no plates."""

    return {"wings": 2, "cloak": 1}.get(region, 0)


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


def leading_edge_angles(u: np.ndarray, s: np.ndarray, chain_u: np.ndarray) -> Tuple[np.ndarray, int]:
    """(chain angles, the leading chain's index): the chain with the largest angle (the wing's top, its arm) is moved onto the leading
    edge's ridge, `LEADING_EDGE_PERCENTILE` of the angles of the wing's outer half, so the wing's arm is one chain's and stays straight."""

    u, s = np.asarray(u, float), np.asarray(s, float)
    out = np.array(chain_u, float)
    outer = s >= np.median(s)
    lead = int(np.argmax(out))
    edge = float(np.percentile(u[outer], LEADING_EDGE_PERCENTILE))
    if len(out) > 1:
        edge = max(edge, float(np.sort(out)[-2]) + 0.25 * float(np.min(np.diff(np.sort(out)))))
    out[lead] = edge
    return out, lead


def sheet_layout(points: np.ndarray, u: np.ndarray, s: np.ndarray, chain_u: np.ndarray, bones: int, ridge: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Joint positions (chains, bones + 1, 3) and their s values (chains, bones + 1).

    A chain runs from the 1st to the 99th percentile of s in its band of u; joint k sits at the median of the band's points within half a
    bone of its s (the nearest band points by s when none are). The `ridge` chain (a wing's arm) reads a band half as wide, so its joints
    sit on the ridge itself and not on the membrane beside it."""

    points, u, s = np.asarray(points, float), np.asarray(u, float), np.asarray(s, float)
    half = band_halfwidths(chain_u, u)
    if ridge is not None:
        half = half.copy()
        half[ridge] *= 0.5
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


def ridge_band(u: np.ndarray, chain_u: np.ndarray, ridge: Optional[int]) -> float:
    """The angle either side of the ridge chain (a wing's arm) inside which the surface takes that chain whole: a quarter of the gap to
    its neighbour, so the arm's skin bends only at the chain's joints and the membrane beside it blends."""

    if ridge is None or len(chain_u) < 2:
        return 0.0
    ordered = np.sort(np.asarray(chain_u, float))
    position = int(np.searchsorted(ordered, float(chain_u[ridge])))
    gaps = [abs(float(ordered[k]) - float(chain_u[ridge])) for k in (position - 1, position + 1) if 0 <= k < len(ordered)]
    return RIDGE_BAND_SHARE * min(gaps)


def sheet_weights(u: np.ndarray, s: np.ndarray, chain_u: np.ndarray, stations: np.ndarray, ridge: Optional[int] = None,
                  ridge_halfwidth: float = 0.0) -> List[Dict[int, float]]:
    """Per vertex {bone index: weight}, bone index = chain * bones + bone. Two chains (linear in u) times two bones (linear in s between
    the bones' middles): at most 4 influences, summing to 1. The `ridge` chain, the first or the last (a wing's arm), takes the surface
    within `ridge_halfwidth` of its angle whole (`ridge_band`), and the blend to its neighbour starts at that band's edge, so the weights
    stay continuous and the arm's skin bends only at its joints."""

    chain_u = np.asarray(chain_u, float).copy()
    if ridge is not None and ridge_halfwidth > 0 and len(chain_u) > 1:
        if ridge == len(chain_u) - 1:
            chain_u[ridge] -= ridge_halfwidth
        elif ridge == 0:
            chain_u[ridge] += ridge_halfwidth
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


def blend_alpha(positions: np.ndarray, edges: np.ndarray, region: np.ndarray, blend_length: float, blocked: Optional[np.ndarray] = None,
                stop_length: Optional[float] = None) -> np.ndarray:
    """Per vertex, the chains' share of its weight: 1 in the whole region, falling smoothly to 0 over `blend_length` of surface distance
    outward from the region's border, into the skin the region is joined to.

    The region moves whole, so it never stretches against itself. The join to the body (where Tripo's single skin fuses a cloak's sides
    to the thighs) takes the strain instead, outside the region, where the cloth hides it. A blend inside the region put 97% of the
    cloak's stretched edges in that blend on the orc."""

    region = np.asarray(region, bool)
    distance = surface_distance(positions, edges, region, blend_length)
    outside = np.where(np.isfinite(distance), 1.0 - smoothstep(distance / max(blend_length, 1e-12)), 0.0)
    alpha = np.where(region, 1.0, outside)
    if blocked is not None and np.any(blocked):
        # skin that must keep its own motion (`is_limb_end`, an arm's room) gets no chain weight, and the share fades to it over
        # `stop_length` (the blend length by default). A wing's whole inner arm lay within one chain bone of its arm's room on the demon,
        # and a fade that long left it half on the chains, stretched at every turn; the stage fades over a few rings instead.
        alpha = alpha * fade_from(positions, edges, blocked, blend_length if stop_length is None else stop_length)
    return alpha


def fade_from(positions: np.ndarray, edges: np.ndarray, blocked: np.ndarray, length: float) -> np.ndarray:
    """Per vertex, 0 on `blocked`, rising smoothly to 1 over `length` of surface distance from it."""

    near = surface_distance(positions, edges, np.asarray(blocked, bool), length)
    return np.where(np.isfinite(near), smoothstep(near / max(length, 1e-12)), 1.0)


def limb_root(name: str) -> Optional[str]:
    """The torso bone an arm bone's weight moves to when skin it carries is loose from it (`loosen_row`): the chain parent. None for any
    other bone. Leg weights stay: a cloak's blend over the thighs that gave its thigh weight to the hips left too little of it beside the
    thigh skin, and the orc's cloak bridged to the legs (UNIT-BRIDGE, replayed offline: 11 edges with legs loosened, 6 without, limit 12)."""

    name = str(name)
    if name.endswith(("Arm", "ForeArm", "ForeArmRoll", "Hand")) and name.startswith(("Left", "Right")):
        return CHAIN_PARENT
    return None


def loosen_row(row: Dict[str, float], share: float) -> Dict[str, float]:
    """`row` with `share` of each limb bone's weight moved to that limb's torso bone (`limb_root`). Tripo binds a wing or a cloak to a limb
    whole, and the chains' blend into such skin kept the limb's weight: the orc's cloak rose with the axe arm and slid round the forearm, the
    demon's wing root stretched whenever the arm it was bound to swung."""

    if share <= 0:
        return dict(row)
    out: Dict[str, float] = {}
    for name, weight in row.items():
        root = limb_root(name)
        if root is None:
            out[name] = out.get(name, 0.0) + weight
            continue
        out[name] = out.get(name, 0.0) + (1.0 - share) * weight
        out[root] = out.get(root, 0.0) + share * weight
    return {name: weight for name, weight in out.items() if weight > 1e-9}


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
                   away: np.ndarray, passes: int = 1, lying: Optional[np.ndarray] = None) -> List[np.ndarray]:
    """The cloak rule for all its chains at once. Per frame and per bone index, every chain's bone springs toward the point the body's
    skinning carries its tail to (`follow_points`), then the chains are pushed out of the capsules along the body's back direction
    (`away`, one per frame) by the spread pushes (`spread_pushes`), never aimed above the horizontal, and kept above the ground. Each chain dict holds `rest_relative`,
    `lengths`, `omegas`, `follow_points` (frames, bones, 3) and `radii` (bones, capsules). Returns each chain's local quaternions
    (frames, bones, 4). With `passes` > 1 the clip runs that many times and the last run is kept (a looping clip settles).

    `lying` (per frame, 0 to 1, `lying_share`) drapes the cloth once the torso lies down: each bone's goal turns toward straight down by
    `DRAPE_MAX_SHARE` of that share (and from `DRAPE_COLLIDE_SHARE` of drape on a bone would leave a capsule by the shortest way), so the cloth falls onto the body's surface and off
    its sides instead of keeping the standing cloak's shape (the round 3 orc's cloak lay on its fallen body as a rigid dome, one flap
    standing up from it)."""

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
            drape = DRAPE_MAX_SHARE * float(lying[f]) if lying is not None else 0.0
            for k in range(bones):
                unposed = [current[c] @ chains[c]["rest_relative"][k] for c in range(count)]
                heads = np.array([m[:3, 3] for m in unposed])
                rigids = np.array([unit(m[:3, 1]) for m in unposed])
                for c, chain in enumerate(chains):
                    goal = chain["follow_points"][f, k] - heads[c]
                    goal = unit(goal) if np.linalg.norm(goal) > 1e-9 else rigids[c]
                    if drape > 0:
                        goal = unit((1.0 - drape) * goal - drape * up) if np.linalg.norm((1.0 - drape) * goal - drape * up) > 1e-9 else -up
                    goal = hang_below_horizon(goal, up)
                    if run == 0 and f == 0:
                        state_d[c, k], state_v[c, k] = goal, np.zeros(3)
                    else:
                        state_d[c, k], state_v[c, k] = spring_step(state_d[c, k], state_v[c, k], goal, float(chain["omegas"][k]), dt)
                if capsule_axes is not None and drape >= DRAPE_COLLIDE_SHARE:
                    for c, chain in enumerate(chains):
                        capsules = [(axis[0], axis[1], float(chain["radii"][k, i])) for i, axis in enumerate(capsule_axes[f])]
                        state_d[c, k], state_v[c, k] = collide_step(heads[c], state_d[c, k], state_v[c, k], float(chain["lengths"][k]), capsules, ground, up, direction)
                elif capsule_axes is not None:
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


def torso_follow_weights(tails: np.ndarray, spine_head: np.ndarray, hips_head: np.ndarray, up: np.ndarray,
                         thighs: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> List[Dict[str, float]]:
    """The cloak's follow rule: a joint at the upper spine's height follows `CHAIN_PARENT`, one at the hips' height or below follows the
    hips, and a joint between them follows both in proportion to its height. The cloth hangs from the shoulders and swings with the
    pelvis, not with an arm. With `thighs` (the left and right thighs' heads), a joint off the middle gives `SIDE_THIGH_SHARE` times its
    lateral offset (in units of the hips' width, at most 1) of its hips share to the thigh on its side: a side chain hangs beside that
    thigh, and the cloth between them tore when it did not follow (`SIDE_THIGH_SHARE`)."""

    up = unit(up)
    top, bottom = float(spine_head @ up), float(hips_head @ up)
    lateral, width = None, 0.0
    if thighs is not None:
        lateral = np.asarray(thighs[0], float) - np.asarray(thighs[1], float)
        lateral = lateral - (lateral @ up) * up
        width = float(np.linalg.norm(lateral))
        lateral = unit(lateral) if width > 1e-9 else None
    out = []
    for tail in np.asarray(tails, float):
        share = float(np.clip((float(tail @ up) - bottom) / max(top - bottom, 1e-12), 0.0, 1.0))
        row = {name: weight for name, weight in ((CHAIN_PARENT, share), ("Hips", 1.0 - share)) if weight > 0}
        if lateral is not None and "Hips" in row:
            offset = float((tail - np.asarray(hips_head, float)) @ lateral)
            moved = row["Hips"] * SIDE_THIGH_SHARE * min(1.0, abs(offset) / width)
            if moved > 0:
                row["Hips"] -= moved
                row["LeftUpLeg" if offset > 0 else "RightUpLeg"] = moved
        out.append(row)
    return out


# A cloak chain below the hips gives this share (times its lateral offset in hips widths, at most 1) of its hips follow to the thigh on its
# side. A fresh review of the round 4 orc saw the cloth between the cloak's side chain and the thigh tear in every idle frame. Replayed
# offline (tripo/chain_replay.py, the seam between chain-bound and leg-bound cloth): idle 51 to 33 stretched edges, attack 327 to 284,
# retreat 392 to 363, with the cloak stretch at most 4.5% (retreat). At 0.5 the retreat's cloak stretch passed TRIPO-CLOAK-STRETCH (5.9%).
# Exported at 0.25 the retreat measured 5.0% (the replay reads about half a point low), so 0.2 (replay: retreat 4.4%, idle 35, attack 294).
SIDE_THIGH_SHARE = 0.2


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
# a single strong beat over the clip (attack); `steps` beats in step with the walk (`walk_beats`, `beats` when no walk is found);
# `face` turns the wing, frame by frame, so its broad face shows in the side and map views (`held_face_turns`).
#
# Rules (round 3, after a fresh review of the demon, 2026-11-15):
# - Idle folded along the back and still, with one slow breath per loop. Move half spread with one beat per step of the walk. The two
#   then differ at map size in both shape and rhythm (the review found the old idle, half folded, and move, folded, almost alike).
# - Every pose keeps the wing behind the body in the side views: its back swing is at least `wing["side"]` (`wing_side_floor`), the
#   least swing past which swinging further hides little less of the body from the side. A spread wing at rest lies in the
#   frontal plane behind the shoulders and from the side covers the back of the shoulder and the arm (the review failed the attack and
#   defend for it). Defend no longer wraps the wings forward, for the same reason.
# - Attack spread to that floor, with one strong beat at the strike. Retreat flapping hard. Both turn their face to the cameras (`face`):
#   seen edge-on from the side a beating wing read as a spike (round 4: the attack showed 28% to 30% of its face, the retreat 21% to 34%).
# - Death folds the wings fully before the knees bend (`fold_by` "fall": the fold ends at the frame the hips first drop
#   `FALL_DROP_SHARE` of the height, `fall_frame`), then sags them flat as the body falls (`droop` runs from that frame to 0.8 of the
#   clip). The back swing lasts only while the torso stands (`upright_sweep`), so a body that ends face down does not hold swept-back
#   wings up in the air; the droop sags the whole wing in its own plane until its highest chain lies level, so the wings lie flat
#   beside the fallen body. The review saw the old death curl a wing in front of the legs while the body knelt: the fold then ran over
#   0.8 of the clip and was still open when the knees bent.
# Every pose is capped by the body: a down-stroke stops when the lowest chain hangs straight down (`wing_down_degrees`) and the bones
# are pushed out of the body's capsules.
# Round e (2026-11-19): a fresh review of run demon_d read the move and the defend as the idle at game size, the wings "only riding the
# body": the fold room left the idle's wings spread (48 degrees of back swing), so every clip showed the same spread wings. Now the idle
# lowers its folded wings (`lower`, degrees down in the frontal plane) and breathes, the move and the retreat beat harder, the attack's
# single beat is stronger, and the defend wraps its wings forward round the body (`wrap`, degrees of forward swing, ramped in and out with
# the guard, lib/tripo_guard.ramp) so the guard reads from the game camera.
# Round g (2026-11-21): the second fresh review of run demon_f read the retreat as the move (both spread the wings in the same V from the
# game camera) and the defend as a bank (one wing up, one down, never forward). Now the retreat folds its wings along the back as the idle
# does, with small quick beats, and runs looking back over the shoulder (`"retreat_pose": "look_back"`, lib/tripo_look_back.py): its outline
# is narrow where the move's is a wide V. The defend wraps its wings forward round the body by `WRAP_GUARD` degrees, a cloak drawn round
# against a blow. A wing wrapped forward points down the game camera's screen and hides the body: TRIPO-WING-SCREEN counts only a wing
# that rises up the screen or swings back (`map_screen_angle`), and TRIPO-WING-FRONT judges a wrapped defend on the head alone
# (tripo/tripo_checks.WRAP_COVER_PARTS). At 30 degrees the wrap left the wings beside the body from the game camera.
WRAP_GUARD = 70.0
# A wrap swung only at the root leaves a flat wing pointing forward beside the body (replayed on demon_f's dump: 2.5% of the body hidden from
# the front at 70 degrees). Each bone past the root swings this share of the wrap further in, so the wing curls round and its tips close
# before the chest, as a cloak is drawn round.
WRAP_CURL_SHARE = 0.3
WING_ROLES: Dict[str, Dict[str, float]] = {
    "idle": {"fold": 1.0, "flap": 3.0, "beats": 1, "lower": 40.0},  # a 6 degree breath left the move only 2.5 times the idle (TRIPO-WING-IDLE-MOVE)
    "move": {"fold": 0.5, "flap": 19.0, "beats": 2, "steps": 1.0},  # under the edge-on rule's 20, which a move without a face turn would fail
    "attack": {"fold": 0.0, "flap": 40.0, "beats": 0, "beat": 1.0, "face": 1.0},
    "defend": {"fold": 0.0, "flap": 4.0, "beats": 1, "wrap": WRAP_GUARD, "lower": 20.0},
    "retreat": {"fold": 1.0, "flap": 3.0, "beats": 4, "lower": 30.0},
    "death": {"fold": 0.0, "fold_end": 1.0, "flap": 0.0, "beats": 0, "droop": 1.0, "upright_sweep": 1.0, "fold_by_fall": 1.0, "knee_guard": 1.0},
}
WING_DEFAULT_ROLE = "idle"
WRAP_RAMP_SHARE = 0.25  # the defend's wrap comes in over the first quarter of the clip and goes over the last, as the guard does
# A folded fan keeps 70% of its spread: the membrane between two chains never narrows past the kit's squash limit (two thirds).
FAN_CLOSE_SHARE = 0.3
FLAP_DELAY = 0.15  # each bone down a chain lags its parent by this share of a flap cycle (the wave runs out to the tip)
# Each bone down a chain flaps this share of its parent's amplitude on top of what the parent carries, so the tip turns at most 1.4 times
# the root's angle. At 0.6 (1.96 times) the tips curled into thin spikes in the demon's attack and retreat.
FLAP_FALLOFF = 0.3
# The fall starts when the hips are this share of the height below where they stand at the clip's start (the demon's `defeat_03`
# sways 1 to 2% while it staggers and drops 9% as the knees give way).
FALL_DROP_SHARE = 0.05
# A dying wing folds over the first `FOLD_SHARE` of the clip, or by the fall when that comes sooner: a stagger before the fall also turns the
# torso, and the half-open wing of the old rule (folded over 0.8 of the clip) crossed the head and shoulder from the side while it did.
# A fold that must end at the fall still takes at least `FOLD_MIN_SHARE` of the clip, so it is not a snap.
FOLD_SHARE = 0.15
FOLD_MIN_SHARE = 0.1
# The droop ends at this share of the clip.
DROOP_END_SHARE = 0.8
# Review cameras (blender/review_render.py): azimuth from the unit's front toward its left, and elevation, in degrees. `map` is the
# camera of the review sheets' hoi4 view.
REVIEW_VIEWS = {"front": (0.0, 8.0), "left": (90.0, 8.0), "right": (270.0, 8.0), "map": (25.0, 55.0)}
# Side views: the wing's root always hides some of the back, however far the wing swings back. The side floor is the least back swing
# whose cover in the side view is within this share of the body of the cover a fully swept wing leaves (on the demon at rest: 31% spread,
# 7.3% at 40 degrees, 6.1% fully swept, so the floor is 40 degrees).
SIDE_COVER_SLACK = 0.02
# A beating wing holds its face toward the review cameras (`held_face_turns`), which stay put in the world while the torso turns and leans
# under the wing: the demon's flee_01 yaws 50 degrees and leans 37, and its box_01 yaws 41. The wing's own plane leans 13 degrees forward
# of the frontal plane at rest, so a turn fixed on the body (the old rule: the side floor's 21 degrees, tilt 0) showed the side cameras
# 28% to 34% of the face and the map camera 21%. Each frame takes, of the back swings from the side floor (plus the torso's twist) to
# `FACE_SWEEP_MAX` and the tilts of the top back from 0 to `FACE_TILT_MAX` in `FACE_TURN_STEP`, the turn whose smallest face share over the
# side views and both map cameras is largest, and the turns are smoothed over `FACE_TURN_WINDOW` frames. Both map cameras: the review
# sheets render the unit as the scene holds it, while tripo/tripo_checks.py reads the exported `.mesh` in the file's own axes, which
# io_pdx_mesh writes as the scene's mirror image (it swaps y and z), so its map camera stands on the unit's other side. Only the chain
# bones past the root take the turn (`wing_pose_rotations`): the root keeps the role's own turn, so the skin where the wing grows from the
# shoulders turns no further. Replayed on the round 4 demon (tripo/chain_replay.py, measured as the check reads the export), with a 40
# degree tilt: a swing of at most 48 degrees (the fold room) left the attack's side views at 36%, 60 degrees gave 50% to 57%, 70 gave 49%
# to 62%, and 90 hid 16% of the head and limbs from the side in the retreat against 13% at 70. At 70 degrees a tilt of 20 left the
# retreat's map view at 36% and 30 at 43%, and 50 began to stretch the membrane. (At 45 degrees of tilt on a whole-wing turn the round 3
# demon squashed its membrane past UNIT-ANIM-STRETCH: the root then took the turn.)
FACE_SWEEP_MAX = 70.0
FACE_TILT_MAX = 40.0
FACE_TURN_STEP = 2.5
FACE_TURN_WINDOW = 9  # frames, about a third of a second at the intake's 24 frames a second


def review_view(front: np.ndarray, up: np.ndarray, azimuth: float, elevation: float) -> np.ndarray:
    """The unit direction from the unit toward a review camera at (azimuth, elevation) degrees: azimuth 0 in front, 90 on the unit's left
    (`up` x `front`)."""

    front, up = unit(front), unit(up)
    lateral = unit(np.cross(up, front))
    a, e = math.radians(azimuth), math.radians(elevation)
    return unit(math.cos(e) * (math.cos(a) * front + math.sin(a) * lateral) + math.sin(e) * up)


def swing_points(points: np.ndarray, root: np.ndarray, up: np.ndarray, degrees: float, front: Optional[np.ndarray] = None,
                 tilt: float = 0.0) -> np.ndarray:
    """Left wing points turned about `root` as `wing_pose_directions` turns its bones: the top tilted back by `tilt` degrees about the
    lateral axis (needs `front`), then swung back by `degrees` about the vertical (a positive angle takes the unit's left toward its
    back)."""

    rotation = axis_angle_matrix(unit(up), math.radians(degrees))
    if tilt and front is not None:
        rotation = rotation @ axis_angle_matrix(unit(np.cross(unit(up), unit(front))), -math.radians(tilt))
    return root + (np.asarray(points, float) - root) @ rotation.T


def wing_side_cover(wing_points: np.ndarray, body_points: np.ndarray, root: np.ndarray, front: np.ndarray, up: np.ndarray, height: float,
                    degrees: float, tilt: float = 0.0) -> float:
    """The share of the body the left wing at rest, turned by (`degrees`, `tilt`) as `swing_points`, hides in the left side view."""

    body_points = np.asarray(body_points, float)
    body = np.r_[np.ones(len(body_points), bool), np.zeros(len(wing_points), bool)]
    posed = np.vstack([body_points, swing_points(wing_points, root, up, degrees, front, tilt)])
    return front_cover_share(posed, body, ~body, review_view(front, up, *REVIEW_VIEWS["left"]), up, height)


def wing_side_floor(wing_points: np.ndarray, body_points: np.ndarray, root: np.ndarray, front: np.ndarray, up: np.ndarray, height: float,
                    most: float) -> Tuple[float, float]:
    """(floor, ceiling): the least back swing (degrees, at most `most`, about the vertical axis through the wing's `root`) at which the
    left wing at rest hides no more of the body in the left side view (`wing_side_cover`) than `SIDE_COVER_SLACK` above what it hides
    swept back by `most`, and that cover limit itself. By symmetry the right wing gets the same."""

    ceiling = wing_side_cover(wing_points, body_points, root, front, up, height, float(most)) + SIDE_COVER_SLACK
    for degrees in np.arange(0.0, float(most), 1.0):
        if wing_side_cover(wing_points, body_points, root, front, up, height, float(degrees)) <= ceiling:
            return float(degrees), ceiling
    return float(most), ceiling


def turned_normal(normal: np.ndarray, front: np.ndarray, up: np.ndarray, sweep: float, tilt: float) -> np.ndarray:
    """A left wing's plane normal after a tilt of its top back by `tilt` degrees (about the body's lateral axis) and a back swing of
    `sweep` degrees (about `up`), the order `wing_pose_rotations` turns it in."""

    lateral = unit(np.cross(unit(up), unit(front)))
    return axis_angle_matrix(unit(up), math.radians(sweep)) @ axis_angle_matrix(lateral, -math.radians(tilt)) @ unit(normal)


def held_face_turns(normal: np.ndarray, carries: np.ndarray, side: str, floors: np.ndarray, front: np.ndarray, up: np.ndarray,
                     most: Optional[float] = None, tilt_most: Optional[float] = None, step: Optional[float] = None,
                     window: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Per frame, the (back swing, tilt) in degrees (`turned_normal`) of wing `side` ("L" or "R"), whose left wing's plane normal at rest is
    `normal`, so that carried by the upper spine (`carries`, (frames, 3, 3) rotations from the rest pose) its face shows most to the review
    cameras, which stay put in the world: of the swings from that frame's `floors` to `most` and the tilts from 0 to `tilt_most` (in
    `step`), the one that makes the smallest of |normal . view| over the left and right views and the map camera on either side (see
    `FACE_SWEEP_MAX`) largest. The turns are then smoothed over `window` frames and never fall under the floors."""

    most = FACE_SWEEP_MAX if most is None else most
    tilt_most = FACE_TILT_MAX if tilt_most is None else tilt_most
    step = FACE_TURN_STEP if step is None else step
    window = FACE_TURN_WINDOW if window is None else window
    up, front = unit(up), unit(front)
    lateral = unit(np.cross(up, front))
    azimuth, elevation = REVIEW_VIEWS["map"]
    views = np.stack([review_view(front, up, *REVIEW_VIEWS["left"]), review_view(front, up, *REVIEW_VIEWS["right"]),
                      review_view(front, up, azimuth, elevation), review_view(front, up, -azimuth, elevation)])
    backs = np.arange(0.0, float(most) + 1e-9, step)
    tilts = np.arange(0.0, float(tilt_most) + 1e-9, step)
    normals = np.array([[turned_normal(normal, front, up, float(b), float(t)) for t in tilts] for b in backs])
    if side == "R":
        normals = normals - 2.0 * (normals @ lateral)[..., None] * lateral
    out_back, out_tilt = np.zeros(len(carries)), np.zeros(len(carries))
    for f, carry in enumerate(np.asarray(carries, float)):
        shares = np.abs((normals @ carry.T) @ views.T).min(axis=-1)
        shares[backs < float(floors[f]) - 1e-9] = -1.0
        b, t = np.unravel_index(int(np.argmax(shares)), shares.shape)
        out_back[f], out_tilt[f] = backs[b], tilts[t]
    if window > 1 and len(carries) > 1:
        kernel = np.ones(window) / window
        pad = window // 2
        out_back = np.convolve(np.pad(out_back, pad, mode="edge"), kernel, mode="valid")
        out_tilt = np.convolve(np.pad(out_tilt, pad, mode="edge"), kernel, mode="valid")
    return np.maximum(out_back, np.asarray(floors, float)), out_tilt


def fall_frame(hips_heights: np.ndarray, height: float) -> Optional[int]:
    """The first frame the hips are `FALL_DROP_SHARE` of the height below their height in the first frame (None if they never are)."""

    hips_heights = np.asarray(hips_heights, float)
    fallen = np.where(hips_heights < hips_heights[0] - FALL_DROP_SHARE * height)[0]
    return int(fallen[0]) if len(fallen) else None


def walk_beats(left_foot: np.ndarray, right_foot: np.ndarray, front: np.ndarray) -> Optional[Tuple[int, float]]:
    """(beats, phase) for a flap in step with a walk: one beat per step, the down-stroke when the feet are farthest apart (a foot
    strikes). The stride is the feet's distance along `front`; its strongest whole-cycle frequency over the clip gives the strides, two
    steps each. None when the feet do not alternate."""

    stride = (np.asarray(left_foot, float) - np.asarray(right_foot, float)) @ unit(front)
    samples = stride[:-1] if len(stride) > 2 else stride  # a looping clip's last frame repeats its first
    if len(samples) < 8 or float(np.ptp(samples)) < 1e-9:
        return None
    spectrum = np.fft.rfft(samples - samples.mean())
    energy = np.abs(spectrum[1:]) ** 2
    k = int(np.argmax(energy)) + 1
    if energy[k - 1] < energy.sum() / 3.0:  # no clear stride: the feet do not swing at one rate
        return None
    # stride ~ cos(2 pi k t + angle): a strike (an extreme) at 2 pi k t + angle = m pi; the flap sin(2 pi 2k t + phase) is at its
    # lowest (-1) there
    angle = float(np.angle(spectrum[k]))
    return 2 * k, -0.5 * math.pi + 2.0 * angle


def wing_role_pose(role: str, frames: int, events: Optional[Dict[str, float]] = None, back_share: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
    """Per frame: the fold (0..1), the flap phase (radians) and amplitude (degrees) of the chain roots, the share of the back swing a
    fold makes (`sweep`), the share of the wing's droop room it sags by (`droop`) and the share of the face turn (`face`).

    `events` holds what the body clip says: `fall` (the frame the fall starts, `fall_frame`) and `beats` and `beat_phase` (`walk_beats`)."""

    rule = WING_ROLES.get(role, WING_ROLES[WING_DEFAULT_ROLE])
    events = events or {}
    t = np.linspace(0.0, 1.0, frames) if frames > 1 else np.zeros(1)
    fold = np.full(frames, rule.get("fold", 0.0))
    droop = rule.get("droop", 0.0) * smoothstep(t / DROOP_END_SHARE)
    if "fold_end" in rule:
        end = DROOP_END_SHARE
        if rule.get("fold_by_fall") and events.get("fall") is not None and frames > 1:
            fall = float(np.clip(events["fall"] / (frames - 1), FOLD_MIN_SHARE, DROOP_END_SHARE))
            end = min(fall, FOLD_SHARE)
            # the wing lies flat only once it is folded and the body falls: it sags from the fall to the end of the droop
            droop = rule.get("droop", 0.0) * smoothstep((t - fall) / max(DROOP_END_SHARE - fall, FOLD_MIN_SHARE))
        fold = rule["fold"] + (rule["fold_end"] - rule["fold"]) * smoothstep(t / end)
    amplitude = np.full(frames, rule.get("flap", 0.0))
    beats = rule.get("beats", 0)
    offset = 0.0
    if rule.get("steps") and events.get("beats"):
        beats, offset = int(events["beats"]), float(events.get("beat_phase", 0.0))
    if rule.get("beat"):
        # one beat: up during the wind-up, a strong down-stroke at the strike, back to rest; the clip starts and ends at rest
        phase = 2.0 * math.pi * t
        amplitude = amplitude * np.sin(math.pi * t)
    else:
        phase = 2.0 * math.pi * beats * t + offset  # whole beats: a looping clip ends on the angle it starts with
    wrap_ramp = np.minimum(np.clip(t / WRAP_RAMP_SHARE, 0.0, 1.0), np.clip((1.0 - t) / WRAP_RAMP_SHARE, 0.0, 1.0))
    return {"wrap": rule.get("wrap", 0.0) * smoothstep(wrap_ramp), "lower": np.full(frames, rule.get("lower", 0.0)),
            "fold": fold, "phase": phase, "amplitude": amplitude, "sweep": np.full(frames, rule.get("sweep", 1.0)), "droop": droop,
            "face": np.full(frames, rule.get("face", 0.0)), "back_share": np.ones(frames) if back_share is None else np.asarray(back_share, float)}


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


def wing_down_degrees(lowest_direction: np.ndarray, down: np.ndarray) -> float:
    """How far a down-stroke may turn a wing: until its lowest chain hangs straight down (further, the wing tucks under and in front of
    the body)."""

    return math.degrees(math.acos(float(np.clip(unit(lowest_direction) @ unit(down), -1.0, 1.0))))


def wing_droop_degrees(highest_direction: np.ndarray, up: np.ndarray) -> float:
    """How far a dying wing sags in its own plane: until its highest chain lies level (no wing corner then stands above the shoulders, or
    ahead of the head when the body ends face down)."""

    return max(0.0, math.degrees(math.asin(float(np.clip(unit(highest_direction) @ unit(up), -1.0, 1.0)))))


def wing_pose_rotations(rest_directions: np.ndarray, chain_u: float, wing: Dict[str, float], up: np.ndarray, front: np.ndarray,
                        pose: Dict[str, float], flaps: np.ndarray) -> np.ndarray:
    """Per bone of a left wing chain, the rotation (bones, 3, 3) that takes it from the rest pose to one frame's pose, in the rest pose's
    space.

    Fold closes the fan by `FAN_CLOSE_SHARE` (each chain turns in the wing's plane, about `wing["normal"]`, toward the lowest chain's angle
    `wing["u_min"]`) and swings the wing back about `up` by its share of `wing["sweep"]` degrees, never less than the side floor
    `wing["side"]` plus `pose["twist"]` (the torso's turn that brings this wing's side forward, `side_twist`), at most the full
    swing; both times `pose["sweep"]`. A face turn (`pose["face"]`) swings the bones past the root back at least `pose["face_back"]`
    and tilts their top back by `pose["face_tilt"]` about the lateral axis (`held_face_turns`); the root keeps the turn without it, so the
    skin where the wing grows from the shoulders turns no further. Droop sags the whole wing in its plane by its share of `wing["droop"]`,
    and `pose["raise"]` lifts it in its plane (`knee_raise`). The flap turns bone k about the body's front axis by the sum of the flap
    angles of bone 0 to k (a positive angle raises a left wing), never further down than `wing["down"]`."""

    up, front = unit(up), unit(front)
    lateral = unit(np.cross(up, front))
    fold = float(pose["fold"])
    face = float(pose.get("face", 0.0))
    close = axis_angle_matrix(wing["normal"], fold * float(wing.get("close", FAN_CLOSE_SHARE)) * (wing["u_min"] - chain_u))
    floor = min(wing.get("side", 0.0) + float(pose.get("twist", 0.0)), wing["sweep"])
    # `tripo/chain_stage.screen_shares`: the share of the back swing and tilt the map's screen allows (1 to 0), and under 0 the share of the
    # beat's up-stroke taken away as well (-1: no up-stroke)
    share = float(pose.get("back_share", 1.0))
    back, lift = max(share, 0.0), (1.0 + min(share, 0.0)) * float(pose.get("rise_share", 1.0))
    root = max(wing["sweep"] * fold, floor) * float(pose["sweep"]) * back - float(pose.get("wrap", 0.0))
    held = float(pose.get("face_back", 0.0)) * back
    outer = max(root, max(wing["sweep"] * fold * back, held) * float(pose["sweep"])) if face > 0 else root
    tilt = face * float(pose.get("face_tilt", 0.0)) * back
    out = np.zeros((len(rest_directions), 3, 3))
    curl = WRAP_CURL_SHARE * float(pose.get("wrap", 0.0))
    for k in range(len(rest_directions)):
        swing = axis_angle_matrix(up, math.radians(root - curl * k))  # a wrap curls each bone further in, so the tips close before the chest
        if k > 0 and face > 0:
            swing = axis_angle_matrix(up, math.radians(root + face * (outer - root))) @ axis_angle_matrix(lateral, -math.radians(tilt))
        beat = float(np.sum(flaps[: k + 1]))
        lowered = float(pose.get("lower", 0.0)) if k == 0 else 0.0
        turn = max((beat * lift if beat > 0.0 else beat) - wing["droop"] * float(pose["droop"]) + float(pose.get("raise", 0.0)) - lowered, -wing["down"])
        out[k] = swing @ axis_angle_matrix(front, math.radians(turn)) @ close
    return out


def wing_pose_directions(rest_directions: np.ndarray, chain_u: float, wing: Dict[str, float], up: np.ndarray, front: np.ndarray,
                         pose: Dict[str, float], flaps: np.ndarray) -> np.ndarray:
    """A left wing chain's bone directions (bones, 3) in one frame's pose, in the rest pose's space: each rest direction turned by its
    bone's `wing_pose_rotations`."""

    turns = wing_pose_rotations(rest_directions, chain_u, wing, up, front, pose, flaps)
    return np.array([unit(turn @ direction) for turn, direction in zip(turns, np.asarray(rest_directions, float))])


def mirror_directions(directions: np.ndarray, lateral: np.ndarray) -> np.ndarray:
    lateral = unit(lateral)
    directions = np.asarray(directions, float)
    return directions - 2.0 * np.outer(directions @ lateral, lateral)


# No bone of a standing wing points more than this many degrees above its own rest elevation in the world. The torso carries the wing, and
# a wing swung back (the side floor, the twist, the face turn) rises when the torso leans forward or sideways over it: the demon's box_01
# leans the upper spine 24 degrees forward and 22 sideways at the punch, and both wings' mean direction rose from 16 to 44 degrees above
# level (sine 0.28 to 0.70), hit_to_body_01 to 40 (0.64), flee_01 to 41 (0.65). At map size each read as a wing stood upright, a spike,
# and a fresh review failed the attack for it. The reviewed idle and move rise at most 4 degrees (0.28 to 0.35). Capped at 10 degrees, root
# included (tripo/chain_replay.py on run demon_a, 2026-11-18), the three peaks fell to 0.29, 0.39 and 0.31, with the side cover, the face
# shares and the root stretch unchanged within a point. A capped bone is turned down in its own vertical plane, so it keeps its heading.
WING_RISE_MAX = 10.0


def capped_rise(direction: np.ndarray, rest_direction: np.ndarray, up: np.ndarray, degrees: Optional[float]) -> np.ndarray:
    """`direction` turned down in its own vertical plane so it rises at most `degrees` above `rest_direction`'s elevation (no cap: None)."""

    if degrees is None:
        return direction
    up = unit(up)
    direction = unit(direction)
    rest_angle = math.asin(float(np.clip(unit(rest_direction) @ up, -1.0, 1.0)))
    limit = min(math.radians(89.0), rest_angle + math.radians(degrees))
    if math.asin(float(np.clip(direction @ up, -1.0, 1.0))) <= limit:
        return direction
    level = direction - (direction @ up) * up
    if np.linalg.norm(level) < 1e-9:
        return direction
    return unit(math.cos(limit) * unit(level) + math.sin(limit) * up)


def quaternion_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The product of two (w, x, y, z) quaternions: `b` turns first, then `a`."""

    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([aw * bw - ax * bx - ay * by - az * bz, aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw])


RISE_TOLERANCE = math.radians(0.05)


def rise_excess(turn: np.ndarray, posed: np.ndarray, rest: np.ndarray, up: np.ndarray, degrees: float) -> float:
    """The most (radians) any of `posed`'s bone directions, turned by `turn`, rises above its rest direction's elevation plus `degrees`."""

    up = unit(up)
    return max(math.asin(float(np.clip(unit(turn @ d) @ up, -1.0, 1.0)))
               - min(math.radians(89.0), math.asin(float(np.clip(unit(r) @ up, -1.0, 1.0))) + math.radians(degrees)) for d, r in zip(posed, rest))


def tilt_limited_carry(carry: np.ndarray, posed: np.ndarray, rest: np.ndarray, up: np.ndarray, degrees: float) -> np.ndarray:
    """`carry` (the upper spine's turn from its rest pose) with its tilt reduced, for the whole wing at once, so that no bone rises more
    than `degrees` above its rest elevation. The turn about `up` (the heading) is kept.

    The wing rises when the torso leans over it. `capped_rise` turned each bone down on its own, and neighbouring bones then hit the cap
    at different moments: on a thick feathered wing the chains tore apart (the angel's attack stretched 15.8% of the wing's edges with it,
    0.7% without it, 2026-11-23). Here the wing follows the lean by the largest share (in steps of `TILT_SHARE_STEP`) at which no bone
    exceeds its cap: one rigid turn for every bone, so the skin between the chains keeps its shape."""

    up = unit(up)
    q = quaternion_from_matrix(carry)
    along = float(q[1:] @ up)
    twist = np.array([q[0], *(along * up)])
    norm = float(np.linalg.norm(twist))
    twist = twist / norm if norm > 1e-9 else np.array([1.0, 0.0, 0.0, 0.0])
    swing = quaternion_multiply(q, twist * np.array([1.0, -1.0, -1.0, -1.0]))
    identity = np.array([1.0, 0.0, 0.0, 0.0])
    if rise_excess(carry, posed, rest, up, degrees) <= RISE_TOLERANCE:
        return carry
    heading = matrix_from_quaternion(twist)
    for share in np.arange(1.0 - TILT_SHARE_STEP, -1e-9, -TILT_SHARE_STEP):
        trial = matrix_from_quaternion(slerp(identity, swing, float(share))) @ heading
        if rise_excess(trial, posed, rest, up, degrees) <= RISE_TOLERANCE:
            return trial
    return heading


TILT_SHARE_STEP = 0.05


# The game's camera looks down at the unit from the front at 55 degrees (the review sheets' hoi4 view), and from there a wing swung back
# stands up the screen as a spike. Measured on the exported files as the angle of each wing's mean direction from its root above the
# screen's level (`tripo/tripo_checks.py`, TRIPO-WING-SCREEN, both sides of the unit), the demon's reviewed move reaches 51 degrees (run
# tripo-wings full2) and its box_01 attack, whose wing a fresh review saw collapse upright, 89. The attack and the defend therefore aim their
# wings at the game camera (`tripo/chain_stage.screen_shares`): in each frame the back swing (the side floor, the torso's twist and the
# face turn) and the face tilt keep the largest share, in steps of 5%, under which the posed chains' mean direction from the wing's root
# stays at or under `SCREEN_AIM` on the map's screen. The posed chains carry the flap and the torso's own turn and lean. The share changes by
# at most `SCREEN_SHARE_RATE` a frame. The wing keeps its size and shape: only how far it swings back changes.
# The check's bound: the highest angle fresh reviewers saw at game size without naming the wing, with a twentieth added. The demon's run
# demon_c (2026-11-19) measured its attack at 57.5 degrees and two fresh D-83 reviews passed the wing (the reviewed move of full2: 51).
SCREEN_MAX = 60.0
# The pose aims at the reviewed move's own 51 degrees, under the check's bound: the export's later steps (the shoulder ease, the snap easing,
# the resample to 30 frames a second) still turn the upper spine that carries the wing.
SCREEN_AIM = 51.0
SCREEN_ROLES = ("attack", "defend")
SCREEN_SHARE_STEP = 0.05
SCREEN_SHARE_RATE = 0.1


def map_screen_angle(direction: np.ndarray, front: np.ndarray, up: np.ndarray) -> float:
    """Degrees a world direction rises above the screen's level in the review sheets' map view, the larger of the cameras on either side.

    A direction ahead of the body's frontal plane that points down the screen counts 0: that is a wing wrapped forward round the body (the
    defend's `wrap`), which hides the body instead of standing up as a spike. One that points down the screen behind the frontal plane, or
    up the screen anywhere, counts by its angle."""

    worst = 0.0
    azimuth, elevation = REVIEW_VIEWS["map"]
    ahead = float(direction @ unit(front)) > 0.0
    for side in (azimuth, -azimuth):
        view = review_view(front, up, side, elevation)
        right = unit(np.cross(unit(up), view))
        screen_up = np.cross(view, right)
        rise = float(direction @ screen_up)
        if ahead and rise < 0.0:
            continue
        worst = max(worst, math.degrees(math.atan2(abs(rise), abs(float(direction @ right)) + 1e-12)))
    return worst


def screen_share_steps() -> np.ndarray:
    """The back-swing shares tried per frame, from the full swing down (`tripo/chain_stage.screen_shares`)."""

    return np.round(np.arange(1.0, -1.0 - 1e-9, -SCREEN_SHARE_STEP), 3)


def limited_shares(shares: np.ndarray) -> np.ndarray:
    """`shares` held to `SCREEN_SHARE_RATE` a frame: a lower share spreads to the frames round it, so the wing never jumps."""

    out = np.asarray(shares, float).copy()
    for f in range(1, len(out)):
        out[f] = min(out[f], out[f - 1] + SCREEN_SHARE_RATE)
    for f in range(len(out) - 2, -1, -1):
        out[f] = min(out[f], out[f + 1] + SCREEN_SHARE_RATE)
    return out


def side_twist(carry: np.ndarray, up: np.ndarray, front: np.ndarray, side: str) -> float:
    """Degrees the torso has turned about the vertical (the upper spine's front against the rest front, seen from above) toward bringing
    wing `side` ("L" or "R") forward, 0 when it turns the other way. The side views are fixed in the world: a torso that twists 36 degrees
    (the demon's `hit_to_body_01`, frame 10) shows the wing on the side that comes forward across its body, so that wing swings back by the
    twist on top of its side floor."""

    up, front = unit(up), unit(front)
    lateral = unit(np.cross(up, front))
    turned = np.asarray(carry, float) @ front
    yaw = math.degrees(math.atan2(float(turned @ lateral), float(turned @ front)))  # positive: the front turns toward the unit's left
    return max(0.0, -yaw) if side == "L" else max(0.0, yaw)


# A dying wing is kept above the knees while the torso stands (the review saw a wing curl in front of the legs of the kneeling demon, frames
# 73 to 84). The guard is whole while the torso is more than `KNEE_GUARD_UPRIGHT` + `KNEE_GUARD_FADE` upright and gone below
# `KNEE_GUARD_UPRIGHT`, so the wings lie flat once the body is down.
KNEE_GUARD_UPRIGHT = 0.5
KNEE_GUARD_FADE = 0.3
KNEE_RAISE_MAX = 90.0


def knee_raise(wing: dict, pose: Dict[str, float], flaps: np.ndarray, carry: np.ndarray, root: np.ndarray, side: str, stage: dict,
               knee: float) -> float:
    """The least lift (degrees, in steps of 3, at most `KNEE_RAISE_MAX`) of the wing in its own plane that keeps every joint of its lowest
    chain (`wing["low_rest"]`, `wing["low_lengths"]`, `wing["low_u"]`, posed from the world `root`) at or above the height `knee`. Every
    chain of a wing reads the same lowest chain, so they lift together and the membrane does not tear."""

    up = unit(stage["up"])
    lateral = unit(np.cross(up, stage["front"]))
    lengths = np.asarray(wing["low_lengths"], float)
    for lift in np.arange(0.0, KNEE_RAISE_MAX + 1e-9, 3.0):
        directions = wing_pose_directions(wing["low_rest"], wing["low_u"], wing, up, stage["front"], dict(pose, **{"raise": float(lift)}), flaps)
        if side == "R":
            directions = mirror_directions(directions, lateral)
        joints = root + np.cumsum((np.asarray(carry, float) @ directions.T).T * lengths[:, None], axis=0)
        if float((joints @ up).min()) >= knee:
            return float(lift)
    return KNEE_RAISE_MAX


def wing_events(role: str, track: Optional[Dict[str, np.ndarray]], stage: dict) -> Dict[str, float]:
    """What the body clip says for the wing rule of `role`: the death's `fall` frame (`fall_frame`, from the hips' height) and the move's
    `beats` and `beat_phase` (`walk_beats`, from the feet). `track` holds per-frame world positions of `Hips`, `LeftFoot` and `RightFoot`."""

    rule = WING_ROLES.get(role, WING_ROLES[WING_DEFAULT_ROLE])
    events: Dict[str, float] = {}
    if not track:
        return events
    if rule.get("fold_by_fall") and "Hips" in track:
        events["fall"] = fall_frame(np.asarray(track["Hips"], float) @ unit(stage["up"]), float(stage["height"]))
    if rule.get("steps") and "LeftFoot" in track and "RightFoot" in track:
        found = walk_beats(track["LeftFoot"], track["RightFoot"], stage["front"])
        if found:
            events["beats"], events["beat_phase"] = found
    return events


def limited_wing_pose(plan: dict, left_rest: np.ndarray, rest: np.ndarray, now: Dict[str, float], flaps: np.ndarray, carry: np.ndarray,
                      stage: dict, mirror: np.ndarray, rise_cap: Optional[float],
                      sheet_turn: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, bool]:
    """One frame of a wing chain's pose: (`turns`, `posed` directions, the `carry` to use, whether the cap acted).

    With a `rise_cap` (a feathered wing, see `tilt_limited_carry`) the wing follows the torso's lean only as far as the cap allows, and when
    the lean is gone and its own up-stroke still passes the cap, every bone's up-stroke shrinks by one share (`now["rise_share"]`). Without
    one the pose is what `wing_pose_rotations` gives. A `sheet_turn` (`wing_side_quaternions`) turns the carry first, in the world."""

    if sheet_turn is not None:
        carry = np.asarray(sheet_turn, float) @ carry

    def turned(pose_now: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
        rotations = wing_pose_rotations(left_rest, plan["chain_u"], plan["wing"], stage["up"], stage["front"], pose_now, flaps)
        rotations = mirror @ rotations @ mirror if plan["side"] == "R" else rotations
        return rotations, np.array([unit(t @ d) for t, d in zip(rotations, rest)])

    turns, posed = turned(now)
    if rise_cap is None:
        return turns, posed, carry, False
    limited = tilt_limited_carry(carry, posed, rest, stage["up"], rise_cap)
    if rise_excess(limited, posed, rest, stage["up"], rise_cap) > RISE_TOLERANCE:
        for share in np.arange(1.0 - TILT_SHARE_STEP * 2, -1e-9, -TILT_SHARE_STEP * 2):
            now["rise_share"] = float(share)
            turns, posed = turned(now)
            if rise_excess(limited, posed, rest, stage["up"], rise_cap) <= RISE_TOLERANCE:
                break
    return turns, posed, limited, (not np.allclose(limited, carry, atol=1e-9)) or "rise_share" in now


def wing_quaternions(plan: dict, parents: np.ndarray, role: str, stage: dict, capsule_axes: Optional[np.ndarray] = None,
                     track: Optional[Dict[str, np.ndarray]] = None, back_share: Optional[np.ndarray] = None,
                     sheet_turns: Optional[np.ndarray] = None) -> np.ndarray:
    """(frames, bones, 4) local quaternions of one wing chain for a role clip: the role's fold, face turn and flap (`WING_ROLES`, timed by
    the body clip through `wing_events` and `track`) carried by the upper spine, each bone pushed out of the body's capsules
    (`capsule_axes` (frames, capsules, 2, 3) with the plan's `radii`) along the wing's outward side, and kept above the ground. A face
    turn is chosen per frame against the upper spine's turn (`held_face_turns`), from the side floor plus the torso's twist.

    A membrane wing's bones are each capped at `WING_RISE_MAX` above their rest elevation (`capped_rise`). With `sheet_turns` ((frames,
    3, 3) world turns, `wing_side_quaternions`) the per-bone cap is off and every bone of the chain takes the frame's turn instead, so the
    whole wing is capped as one sheet."""

    frames, bones = parents.shape[0], len(plan["lengths"])
    pose = wing_role_pose(role, frames, wing_events(role, track, stage), back_share)
    flaps = flap_angles(pose["phase"], pose["amplitude"], bones)
    wing = plan["wing"]
    lateral = unit(np.cross(stage["up"], stage["front"]))
    rest = np.asarray(plan["rest_directions"], float)
    left_rest = mirror_directions(rest, lateral) if plan["side"] == "R" else rest
    parent_rest = np.asarray(plan["parent_rest"], float)
    out = np.zeros((frames, bones, 4))
    carries = np.stack([parents[f][:3, :3] @ parent_rest[:3, :3].T for f in range(frames)])
    mirror = np.eye(3) - 2.0 * np.outer(lateral, lateral)
    bone_rest, chained = [], parent_rest
    for k in range(bones):
        chained = chained @ plan["rest_relative"][k]
        bone_rest.append(orthonormal(chained)[:3, :3])
    slab = bool(plan.get("thick"))
    ground = -1e9 if slab else stage["ground"]  # a slab of feathers is not pushed off the ground bone by bone (THICK_WING_SHARE)
    rise_cap = None if "fold_end" in WING_ROLES.get(role, {}) else WING_RISE_MAX  # a dying wing has its own rules
    if float(np.max(pose["face"])) > 0:
        most = max(FACE_SWEEP_MAX, float(wing["sweep"]))
        floors = np.array([min(wing.get("side", 0.0) + side_twist(c, stage["up"], stage["front"], plan["side"]), most) for c in carries])
        pose["face_back"], pose["face_tilt"] = held_face_turns(wing["normal"], carries, plan["side"], floors, stage["front"], stage["up"], most=most)
    for f in range(frames):
        carry = carries[f]
        now = {key: value[f] for key, value in pose.items()}
        if "upright_sweep" in WING_ROLES.get(role, {}):
            # a dying wing folds back along the back while the torso stands, and lies flat as it falls
            now["sweep"] = float(np.clip(unit(carry @ unit(stage["up"])) @ unit(stage["up"]), 0.0, 1.0))
        now["twist"] = side_twist(carry, stage["up"], stage["front"], plan["side"])
        if WING_ROLES.get(role, {}).get("knee_guard") and track and "knees" in track and "low_rest" in wing:
            guard = float(smoothstep((float(unit(carry @ unit(stage["up"])) @ unit(stage["up"])) - KNEE_GUARD_UPRIGHT) / KNEE_GUARD_FADE))
            if guard > 0:
                root = (parents[f] @ np.linalg.inv(parent_rest) @ np.r_[np.asarray(wing["root"], float), 1.0])[:3]
                now["raise"] = guard * knee_raise(wing, now, flaps[f], carry, root, plan["side"], stage, float(np.max(np.asarray(track["knees"])[f] @ unit(stage["up"]))))
        turns, posed, carry, lowered = limited_wing_pose(plan, left_rest, rest, now, flaps[f], carry, stage, mirror, rise_cap if slab else None,
                                                         None if slab or sheet_turns is None else sheet_turns[f])
        whole = float(now.get("face", 0.0)) > 0
        outward = unit(carries[f] @ (lateral if plan["side"] == "L" else -lateral))
        current = parents[f]
        for k in range(bones):
            unposed = current @ plan["rest_relative"][k]
            head, rigid = unposed[:3, 3], unit(unposed[:3, 1])
            capsules = [] if capsule_axes is None else [(axis[0], axis[1], float(plan["radii"][k, c])) for c, axis in enumerate(capsule_axes[f])]
            wanted = unit(carry @ posed[k])
            direction = collide_direction(head, wanted, float(plan["lengths"][k]), capsules, ground, stage["up"], outward, along=True)
            if rise_cap is not None and not slab and sheet_turns is None:
                direction = capped_rise(direction, rest[k], stage["up"], rise_cap)
            if (whole and k > 0) or lowered:
                # a bone past the root of a face-turned wing takes the pose's whole turn, roll included: turned by the shortest arc onto
                # its direction alone, the bones of neighbouring chains rolled apart under the compound swing and tilt and twisted the
                # membrane out of the wing's plane (the demon's retreat showed the map camera 38% of the face where the chains' own plane
                # gave 53%). A collision then turns it by the shortest arc.
                turn = shortest_arc(wanted, direction) @ carry @ turns[k] @ bone_rest[k] @ unposed[:3, :3].T
            else:
                turn = shortest_arc(rigid, direction)
            out[f, k] = quaternion_from_matrix(unposed[:3, :3].T @ turn @ unposed[:3, :3])
            current = unposed.copy()
            current[:3, :3] = turn @ unposed[:3, :3]
    return continuous_quaternions(out)


def chain_mean_points(plans: Sequence[dict], parents: np.ndarray, quaternions: Sequence[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """((frames, 3) the mean of every chain joint of a wing side, (frames, 3) its root) from the chains' local quaternions."""

    frames = len(parents)
    total, count = np.zeros((frames, 3)), 0
    root = np.zeros((frames, 3))
    for plan, quats in zip(plans, quaternions):
        current = np.asarray(parents, float).copy()
        for k in range(len(plan["bones"])):
            local = np.tile(np.eye(4), (frames, 1, 1))
            for f in range(frames):
                local[f, :3, :3] = matrix_from_quaternion(quats[f, k])
            current = current @ plan["rest_relative"][k] @ local
            head = current[:, :3, 3]
            if k == 0:
                root += (np.asarray(parents, float) @ plan["rest_relative"][0])[:, :3, 3]
            tip = (current @ np.r_[np.c_[np.eye(3), [0.0, plan["lengths"][k], 0.0]], [[0.0, 0.0, 0.0, 1.0]]])[:, :3, 3]
            total += head + tip
            count += 2
    return total / max(count, 1), root / max(len(plans), 1)


def sheet_rise_turns(directions: np.ndarray, rest_direction: np.ndarray, up: np.ndarray, degrees: float = WING_RISE_MAX) -> np.ndarray:
    """(frames, 3, 3) per frame the world turn that brings a wing's mean direction from its root (`directions`, (frames, 3)) down in its
    own vertical plane to at most `degrees` above `rest_direction`'s elevation (`capped_rise` for the whole wing). Identity where the
    wing is under the cap."""

    up = unit(up)
    limit = min(math.radians(89.0), math.asin(float(np.clip(unit(rest_direction) @ up, -1.0, 1.0))) + math.radians(degrees))
    out = np.tile(np.eye(3), (len(directions), 1, 1))
    for f, direction in enumerate(np.asarray(directions, float)):
        direction = unit(direction)
        excess = math.asin(float(np.clip(direction @ up, -1.0, 1.0))) - limit
        level = direction - (direction @ up) * up
        if excess > 0.0 and np.linalg.norm(level) > 1e-9:
            out[f] = axis_angle_matrix(unit(np.cross(unit(level), up)), -excess)
    return out


# Round devil (2026-11-24): a membrane wing is capped as one sheet. `capped_rise` turned each bone down on its own against its own rest
# elevation. On the ZIN devil, whose wings span 1.45 times his body's height, the chains of one wing stand from 30 degrees above level
# to hanging down, so a torso turn took some bones past their cap and left their neighbours: the membrane between them tore. Replayed on
# run devil_f (tripo/chain_replay.py), the attack's wing stretch fell from 11.9% to 0.4% without the per-bone cap. The review that set the
# cap judged the wing's mean direction (`WING_RISE_MAX`), so the cap now reads that and turns the whole wing down by the excess.
def wing_side_quaternions(plans: Sequence[dict], parents: np.ndarray, role: str, stage: dict, capsule_axes: Optional[np.ndarray] = None,
                          track: Optional[Dict[str, np.ndarray]] = None, back_share: Optional[np.ndarray] = None) -> List[np.ndarray]:
    """`wing_quaternions` for every chain of one wing side, with the rise of a membrane wing capped for the whole side at once
    (`sheet_rise_turns` on `chain_mean_points`). A dying wing (no cap) and a feathered slab (`tilt_limited_carry`) keep their own rules."""

    plans = list(plans)
    if not plans or "fold_end" in WING_ROLES.get(role, {}) or any(plan.get("thick") for plan in plans):
        return [wing_quaternions(plan, parents, role, stage, capsule_axes, track, back_share) for plan in plans]
    frames = len(parents)
    free = [wing_quaternions(plan, parents, role, stage, capsule_axes, track, back_share, np.tile(np.eye(3), (frames, 1, 1))) for plan in plans]
    mean, root = chain_mean_points(plans, parents, free)
    rest_parent = np.asarray(plans[0]["parent_rest"], float)[None]
    rest_mean, rest_root = chain_mean_points(plans, rest_parent, [np.tile([1.0, 0.0, 0.0, 0.0], (1, len(plan["bones"]), 1)) for plan in plans])
    turns = sheet_rise_turns(mean - root, rest_mean[0] - rest_root[0], stage["up"])
    if np.allclose(turns, np.eye(3)):
        return free
    return [wing_quaternions(plan, parents, role, stage, capsule_axes, track, back_share, turns) for plan in plans]


def chain_skinning(parent: np.ndarray, rest: Sequence[np.ndarray], directions: np.ndarray) -> List[np.ndarray]:
    """Per bone of one chain hanging from `parent` (a 4x4 world matrix) with world rest matrices `rest`, its skinning matrix (posed world
    times inverse rest) when its bones point along `directions`."""

    relative, previous = [], np.asarray(parent, float)
    for own in rest:
        relative.append(np.linalg.inv(previous) @ own)
        previous = own
    _q, _heads, posed = chain_forward(parent, np.stack(relative), directions)
    return [posed[k] @ np.linalg.inv(rest[k]) for k in range(len(rest))]


def skin_rows(positions: np.ndarray, rows: Sequence[Dict[str, float]], index: np.ndarray, skinning: Dict[str, np.ndarray]) -> np.ndarray:
    """The vertices `index` skinned by `rows`; a bone missing from `skinning` stays at rest."""

    out = np.zeros((len(index), 3))
    for j, vertex in enumerate(index):
        point = np.r_[positions[vertex], 1.0]
        for name, weight in rows[vertex].items():
            matrix = skinning.get(name)
            out[j] += weight * ((matrix @ point)[:3] if matrix is not None else point[:3])
    return out


def deform_share(rest: np.ndarray, posed: np.ndarray, edges: np.ndarray, height: float, ratio: float = FOLD_DEFORM_RATIO) -> float:
    """The share of `edges` (indices into `rest` and `posed`) longer than `ratio` times or shorter than 1 / `ratio` of their rest length by
    more than 0.5% of the height."""

    from lib import pdx_deform

    rest_length = np.linalg.norm(rest[edges[:, 0]] - rest[edges[:, 1]], axis=1)
    length = np.linalg.norm(posed[edges[:, 0]] - posed[edges[:, 1]], axis=1)
    usable = rest_length > 1e-12
    change = np.abs(length - rest_length) > pdx_deform.SIGNIFICANT_SHARE * height
    bad = usable & change & ((length * ratio < rest_length) | (length > ratio * rest_length))
    return float(bad.mean()) if len(edges) else 0.0


def fold_room(chains: Sequence[dict], wing: dict, rows: Sequence[Dict[str, float]], positions: np.ndarray, edges: np.ndarray,
              parent: np.ndarray, up: np.ndarray, front: np.ndarray, height: float) -> Dict[str, float]:
    """How far a fold may swing the left wing back and close its fan, limited by what it does to the skin, with the body at rest:

    - the back swing (from `wing["sweep"]` down to the side floor `wing["side"]`, in `FOLD_SWEEP_STEP`): the largest at which no more than
      `FOLD_ROOT_LIMIT` of the root's edges (those touching a vertex partly on the chains: the blend into the back and shoulder) stretch
      or squash by UNIT-ANIM-STRETCH's measure;
    - then the fan's close (from `FAN_CLOSE_SHARE` down in `FOLD_CLOSE_STEP`): the largest at which no more than `FOLD_DEFORM_LIMIT` of all
      the edges the chains move change by `FOLD_DEFORM_RATIO` (`deform_share`), and the root still keeps its limit.

    The vertices are skinned by `rows` through the chains (`chains`: per chain its `bones`, world `rest` matrices, `rest_directions` and
    `chain_u`). Returns {"sweep", "close", "share", "root_share"}."""

    from lib import pdx_deform

    names = {name for chain in chains for name in chain["bones"]}
    on_chains = np.array([sum(weight for name, weight in row.items() if name in names) for row in rows])
    moved = on_chains > 0
    partial = moved & (on_chains < 1.0 - 1e-3)
    edges = np.asarray(edges, int)
    inside = edges[moved[edges[:, 0]] | moved[edges[:, 1]]]
    index = np.unique(inside)
    if not len(index):
        return {"sweep": float(wing["sweep"]), "close": FAN_CLOSE_SHARE, "share": 0.0, "root_share": 0.0}
    local = np.searchsorted(index, inside)
    root = local[partial[inside[:, 0]] | partial[inside[:, 1]]]
    rest_points = np.asarray(positions, float)[index]
    pose = {"fold": 1.0, "sweep": 1.0, "droop": 0.0}

    def shares(sweep: float, close: float) -> Tuple[float, float]:
        trial = dict(wing, sweep=float(sweep), close=float(close))
        skinning = {}
        for chain in chains:
            directions = wing_pose_directions(chain["rest_directions"], chain["chain_u"], trial, up, front, pose, np.zeros(len(chain["bones"])))
            for name, matrix in zip(chain["bones"], chain_skinning(parent, chain["rest"], directions)):
                skinning[name] = matrix
        posed = skin_rows(positions, rows, index, skinning)
        return (deform_share(rest_points, posed, local, height),
                deform_share(rest_points, posed, root, height, pdx_deform.STRETCH_RATIO) if len(root) else 0.0)

    floor = float(min(wing.get("side", 0.0), wing["sweep"]))
    sweep = floor
    for candidate in np.arange(float(wing["sweep"]), floor - 1e-9, -FOLD_SWEEP_STEP):
        if shares(candidate, 0.0)[1] <= FOLD_ROOT_LIMIT:
            sweep = float(candidate)
            break
    for close in np.arange(FAN_CLOSE_SHARE, -1e-9, -FOLD_CLOSE_STEP):
        whole, at_root = shares(sweep, close)
        if whole <= FOLD_DEFORM_LIMIT and at_root <= FOLD_ROOT_LIMIT:
            return {"sweep": sweep, "close": float(max(close, 0.0)), "share": whole, "root_share": at_root}
    whole, at_root = shares(sweep, 0.0)
    return {"sweep": sweep, "close": 0.0, "share": whole, "root_share": at_root}


def lying_share(hips: np.ndarray, spine: np.ndarray, up: np.ndarray) -> np.ndarray:
    """Per frame, how far the torso lies down (0 standing, 1 lying): the hips-to-upper-spine axis's vertical share, from `LIE_UPRIGHT` (0)
    to `LIE_FLAT` (1)."""

    axis = np.asarray(spine, float) - np.asarray(hips, float)
    vertical = np.abs(axis @ unit(up)) / np.maximum(np.linalg.norm(axis, axis=1), 1e-12)
    return smoothstep((LIE_UPRIGHT - vertical) / (LIE_UPRIGHT - LIE_FLAT))


# ---------------------------------------------------------------------------------------------
# Plates: rigid armour over a joint
# ---------------------------------------------------------------------------------------------

# A shoulder plate (pauldron) covers the shoulder joint out to this share of the upper arm's length, and reaches down the arm this share of
# it below the joint. On the orc that is 0.09 and 0.03 of the height, the plates' visible extent.
PLATE_REACH_SHARE = 0.6
PLATE_DROP_SHARE = 0.2
# A chest plate lies ahead of the upper spine's joint by more than this share of the torso's radius, between the middle spine's and the
# neck's heights, and within this share of half the shoulders' width of the mid-line.
CHEST_AHEAD_SHARE = 0.35
CHEST_WIDTH_SHARE = 0.6
# A plate's rigid weight blends into the body over the plate's own largest extent (a narrower ring took the strain the plate no longer
# takes into too few edges: on the orc four rings gave 1495 stretched edges in the attack against vanilla's 1300, the plate's own extent
# 1075 with the cloak's chains).
PLATE_BAND_SHARE = 1.0
# A bone holds a plate when it carries at least this share of the plate's total weight.
PLATE_HOLD_SHARE = 0.1


def plate_masks(positions: np.ndarray, heads: Dict[str, np.ndarray], front: np.ndarray, up: np.ndarray, torso_radius: float) -> Dict[str, np.ndarray]:
    """The armour plates over the shoulder joints and on the chest, by rule from the rig's joints (heads in the same space as positions).

    Pauldron: within `PLATE_REACH_SHARE` of the upper arm's length of the upper arm's joint, no lower than `PLATE_DROP_SHARE` of that
    length under it, outside the shoulder joint. Chest plate: ahead of the upper spine's joint by `CHEST_AHEAD_SHARE` of the torso's
    radius, between the middle spine's and the neck's heights, within `CHEST_WIDTH_SHARE` of half the shoulders' width of the mid-line."""

    positions = np.asarray(positions, float)
    up, front = unit(up), unit(front)
    lateral = unit(np.cross(up, front))
    out = {}
    for side in ("Left", "Right"):
        arm, shoulder = heads[f"{side}Arm"], heads[f"{side}Shoulder"]
        length = float(np.linalg.norm(heads[f"{side}ForeArm"] - arm))
        outward = 1.0 if float((arm - heads["Hips"]) @ lateral) >= 0 else -1.0
        near = np.linalg.norm(positions - arm, axis=1) < PLATE_REACH_SHARE * length
        high = positions @ up > float(arm @ up) - PLATE_DROP_SHARE * length
        outside = ((positions - shoulder) @ lateral) * outward > 0
        out[f"{side.lower()}_pauldron"] = near & high & outside
    half = 0.5 * abs(float((heads["LeftArm"] - heads["RightArm"]) @ lateral))
    ahead = (positions - heads[CHAIN_PARENT]) @ front > CHEST_AHEAD_SHARE * torso_radius
    band = (positions @ up > float(heads["Spine01"] @ up)) & (positions @ up < float(heads["neck"] @ up))
    middle = np.abs((positions - heads["Hips"]) @ lateral) < CHEST_WIDTH_SHARE * half
    out["chest_plate"] = ahead & band & middle
    return out


def plate_bone(rows: Sequence[Dict[str, float]], mask: np.ndarray, depth: Dict[str, int]) -> str:
    """The bone a plate rides: of the bones that hold at least `PLATE_HOLD_SHARE` of its weight, the one nearest the root (fewest parent
    steps). A plate over a joint is strapped to the body side of it: a pauldron to the shoulder, a chest plate to the upper spine."""

    totals: Dict[str, float] = {}
    for index in np.where(np.asarray(mask, bool))[0]:
        for name, weight in rows[index].items():
            totals[name] = totals.get(name, 0.0) + weight
    whole = sum(totals.values()) or 1.0
    holding = [name for name, weight in totals.items() if weight / whole >= PLATE_HOLD_SHARE and name in depth]
    if not holding:
        return max(totals, key=totals.get)
    return min(holding, key=lambda name: (depth[name], -totals[name]))


def bone_depths(parents: Dict[str, Optional[str]]) -> Dict[str, int]:
    """Parent steps from the root for each bone (`parents` maps a bone to its parent's name, None for the root)."""

    out: Dict[str, int] = {}
    for name in parents:
        steps, current = 0, parents[name]
        while current is not None and steps < 256:
            steps, current = steps + 1, parents.get(current)
        out[name] = steps
    return out


def plate_band(positions: np.ndarray, edges: np.ndarray, mask: np.ndarray) -> float:
    """The width of the ring a plate's rigid weight blends over into the body: `PLATE_BAND_SHARE` of the plate's largest extent, and at
    least `BLEND_MIN_RINGS` of its median edge length."""

    mask = np.asarray(mask, bool)
    inside = mask[edges].all(axis=1)
    lengths = np.linalg.norm(positions[edges[inside, 0]] - positions[edges[inside, 1]], axis=1)
    lengths = lengths[lengths > 0]
    rings = BLEND_MIN_RINGS * (float(np.median(lengths)) if len(lengths) else 0.0)
    extent = float(np.ptp(positions[mask], axis=0).max()) if mask.any() else 0.0
    return max(rings, PLATE_BAND_SHARE * extent)


def plate_assemblies(masks: Dict[str, np.ndarray], edges: np.ndarray) -> List[List[str]]:
    """Plates that touch (an edge joins them, or they share vertices) grouped into assemblies: armour strapped together moves as one."""

    names = [name for name, mask in masks.items() if np.any(mask)]
    parent = {name: name for name in names}

    def find(name):
        while parent[name] != name:
            name = parent[name]
        return name

    edges = np.asarray(edges, int)
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            a, b = np.asarray(masks[first], bool), np.asarray(masks[second], bool)
            if np.any(a & b) or np.any((a[edges[:, 0]] & b[edges[:, 1]]) | (b[edges[:, 0]] & a[edges[:, 1]])):
                parent[find(first)] = find(second)
    groups: Dict[str, List[str]] = {}
    for name in names:
        groups.setdefault(find(name), []).append(name)
    return list(groups.values())


def rigid_plates(rows: Sequence[Dict[str, float]], positions: np.ndarray, edges: np.ndarray, masks: Dict[str, np.ndarray], depth: Dict[str, int]) -> Tuple[List[Dict[str, float]], Dict[str, dict]]:
    """Each plate bound wholly to one bone, blended into the body over a ring (`plate_band` of the whole assembly). Plates that touch form one assembly
    (`plate_assemblies`) that rides one bone, `plate_bone` of the whole assembly: on the orc, pauldrons on the shoulder bones and a chest
    plate on the spine tore their shared seam (180 more stretched edges in the attack). An assembly's ring fades out before every other
    assembly, so no ring bends another plate. Returns the new rows and per plate its bone,
    vertex count and the vertices the blend touched."""

    out = list(rows)
    report = {}
    for group in plate_assemblies(masks, edges):
        union = np.zeros(len(positions), bool)
        for name in group:
            union |= np.asarray(masks[name], bool)
        bone = plate_bone(rows, union, depth)
        others = np.zeros(len(positions), bool)
        for name, mask in masks.items():
            if name not in group:
                others |= np.asarray(mask, bool)
        alpha = blend_alpha(positions, edges, union, plate_band(positions, edges, union), others & ~union)
        alpha[union] = 1.0  # an assembly stays whole even where another plate is near
        touched = np.where(alpha > 0)[0]
        for index in touched:
            out[index] = mix_weights(out[index], {bone: 1.0}, float(alpha[index]))
        for name in group:
            report[name] = {"bone": bone, "vertices": int(np.sum(masks[name])), "blended": int(len(touched)), "assembly": sorted(group)}
    return out, report


# ---------------------------------------------------------------------------------------------
# Measurements for the checks
# ---------------------------------------------------------------------------------------------


def chain_bones(names: Iterable[str], region: Optional[str] = None) -> List[str]:
    prefixes = [REGION_PREFIX[region]] if region else list(REGION_PREFIX.values())
    return [name for name in names if any(str(name).startswith(prefix) for prefix in prefixes)]


ROOT_ZONE_RINGS = 2


def root_zone(chain_share: np.ndarray, edges: np.ndarray, rings: int = ROOT_ZONE_RINGS) -> np.ndarray:
    """Where a region's chains blend into the body: the vertices with between 1% and 99.9% of their weight on the chain bones
    (`chain_share`, per vertex), grown `rings` edge rings. A fresh review of the round 4 demon saw both wing roots stretch at the
    shoulders while the wing check, which reads the far membrane only (`wing_masks`), measured none: the two never overlap."""

    share = np.asarray(chain_share, float)
    zone = (share > 0.01) & (share < 0.999)
    edges = np.asarray(edges, int)
    for _ in range(rings):
        reached = zone[edges].any(axis=1)
        zone[edges[reached].ravel()] = True
    return zone


def winding_numbers(points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    """The generalised winding number of each point with respect to a triangle soup (T, 3, 3), unsigned: about 1 inside a closed part, 0
    outside, a fraction in the mouth of an open one. It is the sum of the triangles' solid angles over 4 pi (Van Oosterom and
    Strackee), so it does not depend on any direction: turning the body does not change it."""

    points = np.asarray(points, float).reshape(-1, 3)
    triangles = np.asarray(triangles, float).reshape(-1, 3, 3)
    out = np.zeros(len(points))
    for i, point in enumerate(points):
        a, b, c = triangles[:, 0] - point, triangles[:, 1] - point, triangles[:, 2] - point
        la, lb, lc = np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1), np.linalg.norm(c, axis=1)
        numerator = np.einsum("ij,ij->i", a, np.cross(b, c))
        denominator = la * lb * lc + np.einsum("ij,ij->i", a, b) * lc + np.einsum("ij,ij->i", b, c) * la + np.einsum("ij,ij->i", c, a) * lb
        out[i] = np.arctan2(numerator, denominator).sum() / (2.0 * math.pi)
    return np.abs(out)


# A point counts as inside the body only when the ray votes say so and its winding number is above one half. The body a chain region
# is judged against is open where the region was cut out of Tripo's single skin, and the votes cast rays along fixed world
# directions, so turning the body turns that opening against the rays and flips the vote of points that did not move into it: in the
# orc's chop (2026-11-15) the torso bent forward and 41 cloak points at the base of the neck went from 1 or 2 of 5 votes to 3, while
# their winding number stayed 0.31 (0.33 at rest) and their distance to the body's surface stayed 5% of the height.
WINDING_INSIDE = 0.5


def deep_inside(posed: np.ndarray, index: np.ndarray, body_triangles: np.ndarray, body_index: np.ndarray, height: float, margin_share: float) -> np.ndarray:
    """Mask over `index`: the points of `posed` deeper than `margin_share` of the height inside the body triangles (ray votes, depth to
    the nearest body vertex, and a winding number above `WINDING_INSIDE`)."""

    import clip_check as cc

    points = posed[index]
    lo, hi = posed[body_index].min(axis=0), posed[body_index].max(axis=0)
    near = np.all((points >= lo) & (points <= hi), axis=1)
    inside = np.zeros(len(points), dtype=bool)
    if near.any():
        inside[near] = cc.points_inside_mesh(points[near], posed[body_triangles])
    deep = np.zeros(len(points), dtype=bool)
    if inside.any():
        depth = cc.nearest_vertex_distance(points[inside], posed[body_index]) / height
        candidates = np.where(inside)[0][depth > margin_share]
        if len(candidates):
            enclosed = winding_numbers(points[candidates], posed[body_triangles]) > WINDING_INSIDE
            deep[candidates[enclosed]] = True
    return deep


def inside_share_series(frames: Sequence[np.ndarray], triangles: np.ndarray, body: np.ndarray, region: np.ndarray, height: float, margin_share: float,
                        max_points: int = 400, rest: Optional[np.ndarray] = None) -> List[float]:
    """Per frame: the share of region points (at most `max_points`, evenly spaced) deeper than `margin_share` of the height inside the
    rest of the body (the triangles whose three vertices are all in `body`). Uses the kit's ray-parity inside test (tripo/clip_check.py).

    With `rest` (the rest pose's positions), the points already that deep inside at rest are left out: a single Tripo skin models some
    cloth inside the arm or the thigh where they meet, and a clip cannot be blamed for those (on the orc 0.75% of the cloak points sit
    inside at rest and stay there in every clip)."""

    body_triangles = triangles[np.asarray(body, bool)[triangles].all(axis=1)]
    index = np.where(region)[0]
    if not len(index) or not len(body_triangles):
        return [0.0 for _ in frames]
    index = index[np.linspace(0, len(index) - 1, min(max_points, len(index))).astype(int)]
    body_index = np.unique(body_triangles)
    if rest is not None:
        index = index[~deep_inside(np.asarray(rest, float), index, body_triangles, body_index, height, margin_share)]
        if not len(index):
            return [0.0 for _ in frames]
    return [float(deep_inside(posed, index, body_triangles, body_index, height, margin_share).mean()) for posed in frames]


def front_cover_share(posed: np.ndarray, torso: np.ndarray, region: np.ndarray, front: np.ndarray, up: np.ndarray, height: float,
                      cell_share: float = COVER_CELL_SHARE, margin_share: float = COVER_MARGIN_SHARE, judged: Optional[np.ndarray] = None) -> float:
    """The share of the body's footprint that the region (the wings) hides, seen from `front` (the direction toward the camera): the
    screen is cut into square cells `cell_share` of the height wide. A body cell (`torso`, any body mask) is hidden when a region point
    lies in it nearer the camera than the body's surface there by more than `margin_share` of the height. With `judged`, only the cells
    whose nearest body point is a judged one count (the side views judge the limbs and the head a viewer sees, not a far arm the torso
    already hides)."""

    posed = np.asarray(posed, float)
    up, front = unit(up), unit(front)
    lateral = unit(np.cross(up, front))
    cell = max(cell_share * height, 1e-12)
    screen = np.stack([posed @ lateral, posed @ up], axis=1)
    keys = np.floor(screen / cell).astype(np.int64)
    depth = posed @ front
    torso_index = np.where(np.asarray(torso, bool))[0]
    region_index = np.where(np.asarray(region, bool))[0]
    if not len(torso_index):
        return 0.0
    surface: Dict[Tuple[int, int], int] = {}
    for i in torso_index:
        key = (int(keys[i, 0]), int(keys[i, 1]))
        if key not in surface or depth[i] > depth[surface[key]]:
            surface[key] = int(i)
    if judged is not None:
        judged = np.asarray(judged, bool)
        surface = {key: i for key, i in surface.items() if judged[i]}
        if not surface:
            return 0.0
    hidden = set()
    margin = margin_share * height
    for i in region_index:
        key = (int(keys[i, 0]), int(keys[i, 1]))
        if key in surface and depth[i] > depth[surface[key]] + margin:
            hidden.add(key)
    return len(hidden) / len(surface)


def below_ground_series(frames: Sequence[np.ndarray], region: np.ndarray, ground: float, height: float, margin_share: float, up_axis: int = 1) -> List[float]:
    """Per frame: the share of region vertices lower than `ground` by more than `margin_share` of the height."""

    return [float(np.mean(posed[np.asarray(region, bool), up_axis] < ground - margin_share * height)) if np.any(region) else 0.0 for posed in frames]
