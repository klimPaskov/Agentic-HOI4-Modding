"""Measure how a unit's clips move, from the exported `.mesh` and `.anim` bytes.

No Blender: joints are posed with `pdx_deform.skinning_matrices`, the way the game does.

- `find_legs` finds the leg chains (hip, knee, ankle and toe joints) from the rest pose, by
  height and parentage, not by bone name, so it works on Meshy, vanilla and hand-made rigs.
- `knee_report` measures, per frame, how far each knee of a two-legged unit bends backward
  against the way the pelvis faces. A knee that bends backward is a solver picking the wrong
  side (the portal raider's leg helper did it in five clips).
- `seam_edges` finds rest-pose edges between two sibling limbs (left and right thigh) whose
  vertices follow one limb each with no blend. Parting the legs tears such a seam (the portal
  raider's crotch reached 20.8 % of its height in idle).
- `motion_amount` measures how far a clip moves the joints, as a share of the unit's height.
- `clip_distance` measures how different two clips of one skeleton are: the average distance
  from each pose of one clip to the nearest pose of the other, both ways.
- `loose_parts` finds the parts that are not joined to the body's surface (straps, plates, a
  quiver, a separate weapon) and measures whether each is skinned and how far it gets from the
  body region it rests on, in the rest pose and in every frame of every clip.
- `rotation_profile` and `same_clip` compare clips between units: how far each joint has turned
  since the first frame does not depend on how the rig's bones rest, so one library clip played on
  two bodies gives the same profile. Joint directions and rest-relative rotations were tried
  first and blur shared clips (2 to 6 degrees apart on ZIN units).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np

from .pdx_deform import Animation, SkinnedMesh, dominant_bones, mesh_edges, skin, skinning_matrices, weld

# Rest-pose shares of the unit's height that make a chain a leg: the ankle near the ground,
# the hip in the upper half of the legs' reach, and both leg segments long enough to bend.
ANKLE_MAX = 0.17
KNEE_RANGE = (0.10, 0.45)
HIP_MIN = 0.28
SEGMENT_MIN = 0.08
# A frame's knee is only judged when the leg is bent enough for its direction to mean something,
# and when the pelvis's forward direction is not along the leg (a leg kicked straight ahead).
BENT_SHARE = 0.02
FORWARD_MIN = 0.35
# Clips are compared on at most this many evenly spaced frames.
SAMPLE_POSES = 48

# Rule thresholds. Each was set between measured groups, not tuned to pass a unit:
# - KNEE_TOLERANCE: no vanilla soldier's knee bends backward in any frame (0.0 over 31 meshes);
#   0.05 of the leg's length is about 11 degrees of hyperextension. The shipped Chaos Redux gorilla
#   and oracle attacks reach 0.39 and 0.37, library death clips on ZIN units 0.08 to 0.10.
# - SAME_RATIO: the distance between two clips of one unit divided by the larger clip's motion.
#   Two variants of one vanilla role (charge, charge_2) measure 0.04 to 0.06, two different vanilla
#   roles (march, moving) 0.23 and more. Chaos Redux's cave monster move and retreat measure 0.09.
# - SHARED_DEGREES and SHARED_SHARE: one library clip on two different ZIN units measures 0.0 to
#   0.9 degrees; the closest clips that differ measure 1.4 degrees and more.
KNEE_TOLERANCE = 0.05
SAME_RATIO = 0.12
SHARED_DEGREES = 1.0
SHARED_SHARE = 0.05
SHARED_MIN_MOTION = 2.0


@dataclass
class Leg:
    hip: int
    knee: int
    ankle: int
    toe: int  # -1 when the rig has no toe joint
    length: float  # hip to knee plus knee to ankle, rest pose


@dataclass
class LegSet:
    legs: List[Leg]
    pelvis: int  # the joint the legs hang from (its rotation turns the body)
    forward: Optional[np.ndarray]  # rest-pose forward (unit vector), or None when unknown

    @property
    def biped(self) -> bool:
        return len(self.legs) == 2


def rest_joints(mesh: SkinnedMesh) -> np.ndarray:
    """(B, 3) rest-pose joint positions."""

    # pinv: a few vanilla helper nodes have zero-scale bind matrices.
    return np.linalg.pinv(mesh.inverse_bind)[:, :3, 3] if len(mesh.bones) else np.zeros((0, 3))


def posed_joints(mesh: SkinnedMesh, anim: Animation) -> np.ndarray:
    """(F, B, 3) joint positions in every frame."""

    matrices = skinning_matrices(mesh, anim)
    bind = np.linalg.inv(mesh.inverse_bind)
    return (matrices @ bind[None])[:, :, :3, 3]


def _skinned_bones(mesh: SkinnedMesh) -> np.ndarray:
    used = np.zeros(len(mesh.bones), dtype=bool)
    joints = mesh.joints[mesh.weights > 0]
    used[joints[joints >= 0]] = True
    return used


def find_legs(mesh: SkinnedMesh) -> LegSet:
    """Leg chains from the rest pose: an ankle near the ground whose parent and grandparent rise to the hips."""

    joints = rest_joints(mesh)
    if not len(joints):
        return LegSet([], -1, None)
    ground = float(mesh.positions[:, 1].min())
    height = max(mesh.height, 1e-6)
    level = (joints[:, 1] - ground) / height
    children: Dict[int, List[int]] = {}
    for index, parent in enumerate(mesh.parents):
        children.setdefault(parent, []).append(index)
    skinned = _skinned_bones(mesh)
    legs: List[Leg] = []
    for ankle in range(len(joints)):
        knee = mesh.parents[ankle]
        hip = mesh.parents[knee] if knee >= 0 else -1
        if hip < 0 or not skinned[knee] or not skinned[hip]:
            continue
        if not (level[ankle] <= ANKLE_MAX and KNEE_RANGE[0] <= level[knee] <= KNEE_RANGE[1] and level[hip] >= HIP_MIN):
            continue
        upper = np.linalg.norm(joints[knee] - joints[hip]) / height
        lower = np.linalg.norm(joints[ankle] - joints[knee]) / height
        if upper < SEGMENT_MIN or lower < SEGMENT_MIN or level[hip] - level[ankle] < 0.2:
            continue
        # The ankle's own child is a toe when it sits lower or level and reaches out sideways from the ankle.
        toe, reach = -1, 0.0
        for child in children.get(ankle, []):
            offset = joints[child] - joints[ankle]
            horizontal = float(np.hypot(offset[0], offset[2])) / height
            if level[child] <= level[ankle] + 0.01 and horizontal > max(reach, 0.015):
                toe, reach = child, horizontal
        legs.append(Leg(hip, knee, ankle, toe, (upper + lower) * height))
    # A knee joint is shared by one leg only; keep the chain whose ankle sits lowest.
    by_knee: Dict[int, Leg] = {}
    for leg in legs:
        best = by_knee.get(leg.knee)
        if best is None or joints[leg.ankle, 1] < joints[best.ankle, 1]:
            by_knee[leg.knee] = leg
    legs = sorted(by_knee.values(), key=lambda leg: joints[leg.hip, 0])
    pelvis_candidates = {mesh.parents[leg.hip] for leg in legs}
    pelvis = pelvis_candidates.pop() if len(pelvis_candidates) == 1 else (legs[0].hip if legs else -1)
    forward = None
    toes = [joints[leg.toe] - joints[leg.ankle] for leg in legs if leg.toe >= 0]
    if toes:
        direction = np.mean(toes, axis=0)
        direction[1] = 0.0
        if np.linalg.norm(direction) > 1e-9:
            forward = direction / np.linalg.norm(direction)
    if forward is None and legs:
        # No toes: the rest pose's own knee bend shows which way is forward, when it bends at all.
        offsets = [_knee_offset(joints[leg.hip], joints[leg.knee], joints[leg.ankle]) for leg in legs]
        direction = np.mean(offsets, axis=0)
        direction[1] = 0.0
        if np.linalg.norm(direction) > 1e-3 * height:
            forward = direction / np.linalg.norm(direction)
    return LegSet(legs, pelvis, forward)


def _knee_offset(hip: np.ndarray, knee: np.ndarray, ankle: np.ndarray) -> np.ndarray:
    """The knee's offset from the straight line between hip and ankle."""

    axis = ankle - hip
    length = np.linalg.norm(axis)
    if length < 1e-9:
        return knee - hip
    axis = axis / length
    relative = knee - hip
    return relative - axis * float(relative @ axis)


@dataclass
class KneeReport:
    legs: int
    judged_frames: int = 0
    worst_bend: float = 0.0  # most backward bend, as a share of leg length (negative is backward)
    worst_frame: int = -1
    worst_leg: str = ""
    backward_frames: int = 0  # frames in which some knee bends backward past the limit


def knee_report(mesh: SkinnedMesh, anim: Animation, legs: Optional[LegSet] = None, limit: float = 0.0) -> KneeReport:
    """How far the knees of a two-legged unit bend backward in any frame (0 when they never do)."""

    legs = legs or find_legs(mesh)
    report = KneeReport(len(legs.legs))
    if not legs.biped or legs.forward is None or legs.pelvis < 0:
        return report
    matrices = skinning_matrices(mesh, anim)
    bind = np.linalg.inv(mesh.inverse_bind)
    posed = (matrices @ bind[None])[:, :, :3, 3]
    for frame in range(posed.shape[0]):
        rotation = matrices[frame, legs.pelvis, :3, :3]
        forward = rotation @ legs.forward
        backward_here = False
        for leg in legs.legs:
            hip, knee, ankle = posed[frame, leg.hip], posed[frame, leg.knee], posed[frame, leg.ankle]
            offset = _knee_offset(hip, knee, ankle)
            if np.linalg.norm(offset) < BENT_SHARE * leg.length:
                continue
            axis = (ankle - hip) / max(np.linalg.norm(ankle - hip), 1e-9)
            facing = forward - axis * float(forward @ axis)
            if np.linalg.norm(facing) < FORWARD_MIN:
                continue
            bend = float(offset @ (facing / np.linalg.norm(facing))) / leg.length
            report.judged_frames += 1
            if bend < report.worst_bend:
                report.worst_bend, report.worst_frame, report.worst_leg = bend, frame, mesh.bones[leg.knee]
            if bend < -limit:
                backward_here = True
        report.backward_frames += int(backward_here)
    return report


@dataclass
class SeamReport:
    edges: int
    pairs: Dict[str, int] = field(default_factory=dict)


def seam_edges(mesh: SkinnedMesh, legs: Optional[LegSet] = None) -> SeamReport:
    """Rest-pose edges between two legs' regions with no blend across them (a hard crotch seam).

    An edge counts when one vertex follows one leg's hip joint (or a joint below it) and the other
    follows the other leg's, and neither vertex carries 10 % or more of the pelvis or of the
    other leg. Vanilla soldiers blend the inner thighs into the pelvis, so they have none.
    """

    legs = legs or find_legs(mesh)
    if len(legs.legs) < 2 or not mesh.skinned:
        return SeamReport(0)
    limb_of = np.full(len(mesh.bones), -1, dtype=np.int64)
    for number, leg in enumerate(legs.legs):
        for bone in range(len(mesh.bones)):
            node, steps = bone, 0
            while node >= 0 and steps < 64:
                if node == leg.hip:
                    limb_of[bone] = number
                    break
                node, steps = mesh.parents[node], steps + 1
    edges = mesh_edges(mesh)
    dominant = dominant_bones(mesh)
    a, b = dominant[edges[:, 0]], dominant[edges[:, 1]]
    valid = (a >= 0) & (b >= 0)
    la = np.where(valid, limb_of[np.clip(a, 0, None)], -1)
    lb = np.where(valid, limb_of[np.clip(b, 0, None)], -1)
    across = (la >= 0) & (lb >= 0) & (la != lb)
    if not across.any():
        return SeamReport(0)

    def share(vertex: np.ndarray, bones: np.ndarray) -> np.ndarray:
        return (mesh.weights[vertex] * np.isin(mesh.joints[vertex], bones)).sum(axis=1)

    hard = np.zeros(len(edges), dtype=bool)
    pelvis = np.array([legs.pelvis]) if legs.pelvis >= 0 else np.zeros(0, dtype=np.int64)
    for index in np.nonzero(across)[0]:
        va, vb = edges[index]
        other_of_a = np.nonzero(limb_of == lb[index])[0]
        other_of_b = np.nonzero(limb_of == la[index])[0]
        blended = max(
            share(np.array([va]), np.concatenate([other_of_a, pelvis]))[0],
            share(np.array([vb]), np.concatenate([other_of_b, pelvis]))[0],
        )
        hard[index] = blended < 0.1
    pairs: Dict[str, int] = {}
    for x, y in zip(a[hard], b[hard]):
        key = "-".join(sorted((mesh.bones[x], mesh.bones[y])))
        pairs[key] = pairs.get(key, 0) + 1
    return SeamReport(int(hard.sum()), dict(sorted(pairs.items(), key=lambda item: -item[1])))


def _sampled(frames: int) -> np.ndarray:
    return np.unique(np.linspace(0, max(frames - 1, 0), min(max(frames, 1), SAMPLE_POSES)).round().astype(int))


def body_poses(mesh: SkinnedMesh, anim: Animation) -> np.ndarray:
    """(F, B, 3) skinned joint positions relative to the pelvis-height root, sampled, as shares of height.

    The horizontal root position is removed so an in-place clip and a clip that drifts compare by
    their limbs, not by where they stand.
    """

    posed = posed_joints(mesh, anim)[_sampled(anim.frames)]
    used = _skinned_bones(mesh)
    posed = posed[:, used] if used.any() else posed
    centre = posed.mean(axis=1, keepdims=True)
    centre[..., 1] = 0.0
    return (posed - centre) / max(mesh.height, 1e-6)


@dataclass
class FastestTurn:
    degrees: float  # the largest turn of one joint between two frames, scaled to 30 frames a second
    joint: str = ""
    frame: int = -1  # the frame the turn ends on


def fastest_turn(mesh: SkinnedMesh, anim: Animation) -> FastestTurn:
    """The largest rotation any joint that skins vertices makes from one frame to the next.

    Keys on opposite sides of the quaternion sphere make Blender turn the long way between them, and
    the baked samples then swing a limb or a held polearm most of a circle in a frame or two. Joints
    that skin nothing (attach nodes) are skipped: vanilla flips a hand node half a turn in one frame.
    The angle is scaled to 30 frames a second, so clips at other rates compare.
    """

    skinning = {mesh.bones[index] for index in np.unique(mesh.joints[mesh.weights > 0]) if 0 <= index < len(mesh.bones)}
    best = FastestTurn(0.0)
    scale = (anim.fps / 30.0) if getattr(anim, "fps", 0) else 1.0
    for joint, channel in anim.channels.items():
        q = channel["q"]
        if joint not in skinning or len(q) < 2:
            continue
        q = q / np.maximum(np.linalg.norm(q, axis=1, keepdims=True), 1e-12)
        dots = np.abs(np.sum(q[1:] * q[:-1], axis=1)).clip(0.0, 1.0)
        turns = np.degrees(2.0 * np.arccos(dots)) * scale
        frame = int(turns.argmax())
        if turns[frame] > best.degrees:
            best = FastestTurn(float(turns[frame]), joint, frame + 1)
    return best


def motion_amount(mesh: SkinnedMesh, anim: Animation) -> float:
    """Average over skinned joints of their largest distance from their mean position, as a share of height."""

    poses = body_poses(mesh, anim)
    if len(poses) < 2:
        return 0.0
    spread = np.linalg.norm(poses - poses.mean(axis=0, keepdims=True), axis=2).max(axis=0)
    return float(spread.mean())


def _chamfer(a: np.ndarray, b: np.ndarray) -> float:
    """Mean distance from each pose of `a` to the nearest pose of `b`, both ways, averaged per joint."""

    flat_a, flat_b = a.reshape(len(a), -1, a.shape[-1]), b.reshape(len(b), -1, b.shape[-1])
    distance = np.linalg.norm(flat_a[:, None] - flat_b[None], axis=3).mean(axis=2)
    return float((distance.min(axis=1).mean() + distance.min(axis=0).mean()) / 2.0)


def clip_distance(mesh: SkinnedMesh, first: Animation, second: Animation) -> float:
    """How different two clips of one unit look, as a share of height (0 for the same motion)."""

    return _chamfer(body_poses(mesh, first), body_poses(mesh, second))


def local_rotations(anim: Animation, bones: Sequence[str]) -> np.ndarray:
    """(F, N, 4) sampled local rotations of the named joints, sign-normalised (w >= 0)."""

    frames = _sampled(anim.frames)
    rotations = []
    for name in bones:
        channel = anim.channels.get(name)
        q = channel["q"][frames] if channel is not None else np.tile([0.0, 0.0, 0.0, 1.0], (len(frames), 1))
        q = q / np.maximum(np.linalg.norm(q, axis=1, keepdims=True), 1e-12)
        rotations.append(np.where(q[:, 3:4] < 0, -q, q))
    return np.stack(rotations, axis=1) if rotations else np.zeros((len(frames), 0, 4))


def rotation_profile(anim: Animation, bones: Sequence[str]) -> np.ndarray:
    """(F, N) sampled angle in degrees by which each named joint has turned since the clip's first frame.

    It does not depend on how a rig's bones rest, so one library clip retargeted onto two bodies gives
    the same profile, while two different clips do not.
    """

    q = local_rotations(anim, bones)
    if not q.shape[1]:
        return np.zeros((len(q), 0))
    dots = np.abs(np.einsum("fnc,nc->fn", q, q[0])).clip(0.0, 1.0)
    return np.degrees(2.0 * np.arccos(dots))


def profile_distance(first: np.ndarray, second: np.ndarray) -> float:
    """Average per-joint difference in degrees between two profiles' nearest frames, both ways."""

    if not first.shape[1] or first.shape[1] != second.shape[1]:
        return 180.0
    difference = np.abs(first[:, None, :] - second[None, :, :]).mean(axis=2)
    return float((difference.min(axis=1).mean() + difference.min(axis=0).mean()) / 2.0)


def profile_motion(profile: np.ndarray) -> float:
    """Average over joints of the largest turn in a profile, in degrees."""

    return float(profile.max(axis=0).mean()) if profile.size else 0.0


def same_clip(first: np.ndarray, second: np.ndarray) -> Optional[float]:
    """The profile distance when two profiles are one clip played twice, else None."""

    larger = max(profile_motion(first), profile_motion(second))
    if min(profile_motion(first), profile_motion(second)) < SHARED_MIN_MOTION:
        return None
    distance = profile_distance(first, second)
    return distance if distance < SHARED_DEGREES and distance < SHARED_SHARE * larger else None


# A loose part is followed through a clip by the closest pairs of (part vertex, body vertex) at rest:
# while the part stays attached, at least one pair stays close.
ANCHOR_PAIRS = 16
PART_SAMPLES = 64
BODY_SAMPLES = 6000


@dataclass
class LoosePart:
    triangles: int
    vertices: int
    unweighted: int  # vertices with no skin weight: they stay at the bind position in every frame
    rest_gap: float  # smallest distance to the rest of the unit, as a share of height
    worst_gap: float  # largest such distance in any frame of any clip
    worst_clip: str = ""
    worst_frame: int = -1


def _parts(mesh: SkinnedMesh) -> np.ndarray:
    """A part label for every vertex: connected over shared (welded) vertices of triangles."""

    canon = weld(mesh.positions, max(mesh.height, 1e-6) * 1e-5)
    parent = np.arange(len(mesh.positions))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    tris = canon[mesh.triangles]
    for a, b, c in tris:
        ra, rb, rc = find(int(a)), find(int(b)), find(int(c))
        parent[rb] = ra
        parent[find(rc)] = ra
    roots = np.array([find(int(i)) for i in range(len(parent))])
    return roots[canon]


def _evenly(indices: np.ndarray, count: int) -> np.ndarray:
    return indices if len(indices) <= count else indices[np.linspace(0, len(indices) - 1, count).round().astype(int)]


def loose_parts(mesh: SkinnedMesh, clips: Dict[str, Animation]) -> List[LoosePart]:
    """Every part but the largest, with its skinning and its distance from the rest of the unit per frame."""

    labels = _parts(mesh)
    if len(mesh.collision) == len(mesh.positions) and mesh.collision.any():
        labels = np.where(mesh.collision, -1, labels)  # the selection box never renders
    triangle_part = labels[mesh.triangles[:, 0]] if len(mesh.triangles) else np.zeros(0, dtype=np.int64)
    parts, counts = np.unique(triangle_part, return_counts=True)
    if len(parts[parts != -1]) < 2:
        return []
    main = parts[parts != -1][np.argmax(counts[parts != -1])]
    height = max(mesh.height, 1e-6)
    used = np.unique(mesh.triangles)
    found: List[LoosePart] = []
    anchors = []
    for part, triangles in zip(parts, counts):
        if part in (main, -1):
            continue
        mine = used[labels[used] == part]
        others = used[(labels[used] != part) & (labels[used] != -1)]
        if not len(mine) or not len(others):
            continue
        sample = _evenly(mine, PART_SAMPLES)
        body = _evenly(others, BODY_SAMPLES)
        distance = np.linalg.norm(mesh.positions[sample][:, None] - mesh.positions[body][None], axis=2)
        flat = np.argsort(distance, axis=None)[:ANCHOR_PAIRS]
        pairs = np.stack(np.unravel_index(flat, distance.shape), axis=1)
        unweighted = int((mesh.weights[mine].sum(axis=1) <= 0).sum()) if mesh.skinned else 0
        gap = float(distance.min()) / height
        found.append(LoosePart(int(triangles), len(mine), unweighted, gap, gap))
        anchors.append((sample[pairs[:, 0]], body[pairs[:, 1]]))
    if mesh.skinned and found:
        for name, anim in clips.items():
            matrices = skinning_matrices(mesh, anim)
            for frame in range(matrices.shape[0]):
                moved = skin(mesh, matrices[frame])
                for record, (a, b) in zip(found, anchors):
                    gap = float(np.linalg.norm(moved[a] - moved[b], axis=1).min()) / height
                    if gap > record.worst_gap:
                        record.worst_gap, record.worst_clip, record.worst_frame = gap, name, frame
    return sorted(found, key=lambda item: -item.worst_gap)
