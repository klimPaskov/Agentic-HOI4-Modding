"""The swollen shoulder of a Tripo humanoid: its measure, its check (TRIPO-SHOULDER-SWELL) and the ease that fixes it.

Two fresh reviewers failed the round 4 ogre (ogre_j, 2026-11-18) on the skin of its shoulders: in the defend (frames 10 to 21) the guard arm's
shoulder and upper arm swelled into one smooth ball, red over the upper back, and in the attack (frames 59 to 61 and 73 to 91) the club-side
shoulder and the hunched upper back stretched and smeared with the head sunk below them. They failed the round 4 dwarf (dwarf_f) on the same
family: the shoulder and the fur over the back ballooned in the attack (frame 50) and the defend (frames 31 to 46). Every automated check passed.

The measure (`swelling`): each side's shoulder region is the torso skin between the body's midline and the upper arm's joint (up to 0.8 of the
way across, `ACROSS`), from 1.5 upper arm lengths below the arm's joint (`DROP`) up to the head's joint, in the rest pose. Per frame, the share of
that region's rest area in triangles whose area grew past 1.69 times (1.3 times along each side, where the review sheets turn from grey to
yellow and red, `AREA_RATIO`). The worse side counts. It is the reviewers' red over the upper back as one number.

Vanilla (GER infantry clips on GER_infantry, GER_infantry_alt_0, ENG_infantry and GER_infantry_snow, 168 clip and mesh pairs, 2026-11-18): the worst
is 0.062 (alt_0's two deaths, frame 58), then 0.046 (a push-up) and 0.041 (attack_crouch_mg), every role clip but the deaths at most 0.041.
The limit is vanilla's worst with a quarter added, 0.0775 (`SWELL_LIMIT`). Measured on the exported files: ogre_j attack 0.180 (frame 38),
defend 0.161 (frame 19), death 0.072, retreat 0.028; dwarf_f attack 0.084, defend 0.066, death 0.053. The attack and the defend of the ogre and the
attack of the dwarf fail, where the reviewers failed them.

What carries the swelling (the ogre's defend at its worst frame, the fitted weights): the swollen vertices hold Spine01 0.28, LeftShoulder 0.16,
LeftArm 0.14 of their weight. Tripo weights the clavicles to the upper back: the ogre's LeftShoulder is the strongest bone of 741 vertices and the
dwarf's of 1,029, while vanilla's clavicles hold 0.2 of weight in all (no vertex). Kept on the same clip, the clip's spine set to the idle's stance
takes the defend from 0.154 to 0.031, the clavicles and upper arms from 0.154 to 0.017, both 0.011. The swelling is the spine's bend against the
shoulder girdle's turn (the defend's Spine01 is 24 to 27 degrees past the idle's in every frame, its left clavicle 41 to 44 and the guard arm up to 88).

Tried on the weights and dropped (offline on ogre_j and dwarf_f: the repaired export's weights, smoothed and fitted again as `run_pilot` does, with the
exported clips): every clavicle weight given to the chest (vanilla's layout) took the dwarf's attack to 0.036 but left the ogre's defend at 0.159;
the clavicle's and the upper arm's weights kept within a capsule round their own bone (1 to 2 and 1.5 to 2.5 arm radii) took the ogre's attack to
0.092 and its defend to 0.136 but raised the dwarf's deformed edges in five clips. Every one of them made some clip worse by the kit's rule
(`stretch_smooth.worse`, often one edge of the arm against the flank growing further) once smoothed and fitted, and so did merging them into the
fitted weights through the fit's guard (2,215 deformed edges to 2,288). Run on the fitted weights with the guard alone, the guard put almost every
change back. A further fit round seeded on the swollen triangles changed the ogre's defend from 0.154 to 0.150. Holding the arm's root still (the
clavicle turned back until the upper arm's joint moves no further in the chest's frame than vanilla's 4.2% of the height, the arm's direction kept)
changed nothing (0.154 to 0.153).

The ease (`ease_shoulders`, run by `run_pilot` on the staged clips after the weight fit and the spine ease for a cloak): a clip over the limit has
the spine (Spine, Spine01, Spine02), the clavicles, or both turned toward the unit's own stance (the idle's first frame, or the rest pose without
an idle), in each frame by the smallest share of `SHARES` that brings that frame to vanilla's worst (`SWELL_TARGET`). A share is used in a frame
only while it, and every smaller one, keeps that frame's deformed edges inside what the kit's rule (`stretch_smooth.worse`) allows against the
clip before. The need is spread to the frames around by a smoothstep (round the loop for a looping role) no faster than the settle rule allows.
Of the groups that reach the target the one whose joints turn least wins, as in the neck lift; when none does, the one that lowers the swelling
most. A result is kept only when it lowers the worst frame, the clip is not worse by the kit's rule, and the neck stays above TRIPO-NECK-SUNK's
limit (or no lower than before). Only the group's rotation samples change. The upper arms turn with the chest: holding their direction in the
world instead squashed the armpit (the ogre's defend, spine and clavicles half way: 61 squashed edges before, 71 with the arms turning, 119 held).

Measured offline on the fitted weights of ogre_j and dwarf_f (the repaired export smoothed and fitted as `run_pilot` does, with the exported clips):
the ogre's defend from 0.154 to 0.057 (the spine, 0.8 of the way, 42 degrees added in all), its death from 0.081 to 0.060 (the spine, 0.3), its
attack from 0.176 to 0.087 (the spine all the way: the rest is the club arm held over the head, whose weights reach the back, frozen arms take the
attack to 0.037), the dwarf's attack from 0.090 to 0.061 (the spine, 0.2, 8 degrees). The deformed edges by the kit's measure fell in each.

The next runs' exported files (ogre_k, dwarf_g, 2026-11-18): the ogre's defend 0.161 to 0.058, its attack 0.180 to 0.088 (still over the limit),
the dwarf's attack 0.084 to 0.052. The review sheets show the ogre's defend more upright from frame 16, but the red over the guard-side flank
(the skin lateral of the region, under the raised arm, stretched about 1.3 times along one side) is only a little smaller, and the attack's
hunch after the strike is unchanged to the eye. What is left is the upper arm's and the clavicle's weights over the flank and the back, which no
weight rule tried here could move without making a clip worse.

Maths on the exported `.mesh` and `.anim` (`pdx_deform`), no Blender.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, stretch_smooth, tripo_cloak_bend, tripo_neck, tripo_pose, tripo_trim
from .pdx_binary import read

ACROSS = 0.8
DROP = 1.5
AREA_RATIO = 1.69
VANILLA_SWELL_WORST = 0.062
SWELL_LIMIT = round(1.25 * VANILLA_SWELL_WORST, 4)
SWELL_TARGET = VANILLA_SWELL_WORST
SHARES = np.round(np.arange(0.0, 1.0001, 0.1), 2)
MIN_RAMP_FRAMES = 6
SPINE = ("Spine", "Spine01", "Spine02")
# The girdle measure (TRIPO-SHOULDER-TEAR): the shoulder region with the side of the chest under the arm, and a lower growth.
UNDER_ACROSS = (0.6, 1.6)  # the side under the arm: this share of the way from the midline to the arm joint (past it at 1)
UNDER_DROP = (-0.3, 2.0)  # from 0.3 upper arm lengths above the arm joint to 2 below it
ARM_WORDS = ("arm", "hand", "weapon", "shield")  # a vertex whose strongest bone carries one of these is the limb, not the torso
GIRDLE_AREA_RATIO = 1.44  # 1.2 times along each side, where the review sheets turn yellow
VANILLA_GIRDLE_WORST = 0.125
GIRDLE_LIMIT = round(1.25 * VANILLA_GIRDLE_WORST, 4)


@dataclass
class ShoulderRig:
    left: int  # upper arm joints
    right: int
    clavicles: Tuple[int, ...]  # the joints between the chest and each upper arm
    head: int


def shoulder_rig(mesh: pdx_deform.SkinnedMesh) -> Optional[ShoulderRig]:
    rig = tripo_neck.neck_rig(mesh)
    if rig is None:
        return None
    return ShoulderRig(rig.left_arm, rig.right_arm, rig.clavicles, rig.head)


def _forearm(mesh: pdx_deform.SkinnedMesh, arm: int) -> int:
    children = [i for i, parent in enumerate(mesh.parents) if parent == arm]
    return children[0] if children else -1


def shoulder_regions(mesh: pdx_deform.SkinnedMesh, rig: Optional[ShoulderRig] = None) -> Dict[str, np.ndarray]:
    """(V,) masks of the two shoulder regions (see the module text), keyed `left` and `right`. Empty without a shoulder rig."""

    rig = rig or shoulder_rig(mesh)
    if rig is None:
        return {}
    joints = pdx_motion.rest_joints(mesh)
    left, right = joints[rig.left], joints[rig.right]
    middle = 0.5 * (left + right)
    out = {}
    for side, arm, joint in (("left", rig.left, left), ("right", rig.right, right)):
        forearm = _forearm(mesh, arm)
        if forearm < 0:
            continue
        across = joint - middle
        width = float(np.linalg.norm(across))
        if width <= 1e-9:
            continue
        across = across / width
        length = float(np.linalg.norm(joints[forearm] - joint))
        u = (mesh.positions - middle) @ across / width
        y = mesh.positions[:, 1]
        out[side] = (u >= 0.0) & (u <= ACROSS) & (y >= joint[1] - DROP * length) & (y <= joints[rig.head][1])
    return out


def under_arm_regions(mesh: pdx_deform.SkinnedMesh, rig: Optional[ShoulderRig] = None) -> Dict[str, np.ndarray]:
    """(V,) masks of the torso skin under each arm: `UNDER_ACROSS` of the way from the midline to the arm joint, `UNDER_DROP` upper arm lengths
    round the joint's height, and not the limb itself (the vertex's strongest bone is no arm, hand or held part, `ARM_WORDS`)."""

    rig = rig or shoulder_rig(mesh)
    if rig is None:
        return {}
    joints = pdx_motion.rest_joints(mesh)
    left, right = joints[rig.left], joints[rig.right]
    middle = 0.5 * (left + right)
    dominant = pdx_deform.dominant_bones(mesh)
    limb = np.array([any(word in name.lower() for word in ARM_WORDS) for name in mesh.bones])
    torso = ~limb[np.clip(dominant, 0, None)]
    out = {}
    for side, arm, joint in (("left", rig.left, left), ("right", rig.right, right)):
        forearm = _forearm(mesh, arm)
        width = float(np.linalg.norm(joint - middle))
        if forearm < 0 or width <= 1e-9:
            continue
        length = float(np.linalg.norm(joints[forearm] - joint))
        u = (mesh.positions - middle) @ ((joint - middle) / width) / width
        drop = (joint[1] - mesh.positions[:, 1]) / max(length, 1e-9)
        out[side] = (u >= UNDER_ACROSS[0]) & (u <= UNDER_ACROSS[1]) & (drop >= UNDER_DROP[0]) & (drop <= UNDER_DROP[1]) & torso
    return out


def girdle_regions(mesh: pdx_deform.SkinnedMesh, rig: Optional[ShoulderRig] = None) -> Dict[str, np.ndarray]:
    """(V,) masks of each side's shoulder girdle: the shoulder region and the torso under the arm."""

    shoulders, under = shoulder_regions(mesh, rig), under_arm_regions(mesh, rig)
    return {side: shoulders[side] | under.get(side, False) for side in shoulders}


class Swelling:
    """The shoulder regions' triangles of one mesh, to measure clip after clip (only the regions' vertices are skinned). `girdle` measures
    the girdle regions at `GIRDLE_AREA_RATIO` (TRIPO-SHOULDER-TEAR) instead."""

    def __init__(self, mesh: pdx_deform.SkinnedMesh, rig: Optional[ShoulderRig] = None, girdle: bool = False):
        self.mesh = mesh
        self.ratio = GIRDLE_AREA_RATIO if girdle else AREA_RATIO
        triangles = mesh.triangles
        keep = ~mesh.collision[triangles].any(axis=1) if len(mesh.collision) == len(mesh.positions) else np.ones(len(triangles), bool)
        rest = _areas(mesh.positions, triangles)
        self.sides = []
        used = np.zeros(len(mesh.positions), bool)
        for mask in (girdle_regions if girdle else shoulder_regions)(mesh, rig).values():
            inside = mask[triangles].all(axis=1) & keep & (rest > 0)
            if inside.any():
                self.sides.append(inside)
                used[triangles[inside].ravel()] = True
        self.vertices = np.nonzero(used)[0]
        local = np.full(len(mesh.positions), -1)
        local[self.vertices] = np.arange(len(self.vertices))
        self.triangles = [local[triangles[inside]] for inside in self.sides]
        self.rest = [rest[inside] for inside in self.sides]

    def per_frame(self, anim: pdx_deform.Animation) -> np.ndarray:
        """(frames,) the worse side's swollen share in each frame."""

        if not self.sides:
            return np.zeros(max(anim.frames, 1))
        matrices = pdx_deform.skinning_matrices(self.mesh, anim)
        points = self.mesh.positions[self.vertices]
        joints, weights = self.mesh.joints[self.vertices], self.mesh.weights[self.vertices]
        out = np.zeros(matrices.shape[0])
        for frame in range(matrices.shape[0]):
            posed = stretch_smooth._skin_subset(points, joints, weights, matrices[frame])
            for triangles, rest in zip(self.triangles, self.rest):
                grown = _areas(posed, triangles) > self.ratio * rest
                out[frame] = max(out[frame], float(rest[grown].sum() / rest.sum()))
        return out


def _areas(points: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    a, b, c = points[triangles[:, 0]], points[triangles[:, 1]], points[triangles[:, 2]]
    return 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)


def swelling(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, girdle: bool = False) -> np.ndarray:
    """(frames,) the shoulder swelling of `anim` on `mesh` (see the module text), or with `girdle` the girdle's tear."""

    return Swelling(mesh, girdle=girdle).per_frame(anim)


# ---- the check ---------------------------------------------------------------------------------------------------------

def shoulder_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    """TRIPO-SHOULDER-SWELL over a unit's clips (`anims`: clip stem to Animation), with each clip's worst share and frame."""

    rig = shoulder_rig(mesh)
    if rig is None:
        return [], {"note": "no head and two upper arms under one chest"}
    measure, girdle = Swelling(mesh, rig), Swelling(mesh, rig, girdle=True)
    out: List[dict] = []
    numbers: dict = {}
    for clip, anim in anims.items():
        shares = measure.per_frame(anim)
        frame = int(np.argmax(shares))
        worst = float(shares[frame])
        over = int(np.sum(shares > SWELL_LIMIT))
        tear = girdle.per_frame(anim)
        tear_frame = int(np.argmax(tear))
        numbers[clip] = {"worst_share": round(worst, 4), "frame": frame, "frames_over_limit": over,
                         "girdle_share": round(float(tear[tear_frame]), 4), "girdle_frame": tear_frame}
        if worst > SWELL_LIMIT:
            out.append({"rule": "TRIPO-SHOULDER-SWELL", "subject": clip,
                        "message": f"{worst:.1%} of the shoulder region's skin has grown past 1.69 times its area in frame {frame} (limit {SWELL_LIMIT:.1%}, "
                                   f"vanilla's worst {VANILLA_SWELL_WORST:.1%}), {over} of {len(shares)} frames over the limit: the shoulder and the upper "
                                   "back swell into one ball",
                        "share": round(worst, 4), "frame": frame})
        if tear[tear_frame] > GIRDLE_LIMIT:
            out.append({"rule": "TRIPO-SHOULDER-TEAR", "subject": clip,
                        "message": f"{tear[tear_frame]:.1%} of the shoulder girdle's skin (the shoulder and the side of the chest under the arm) has grown "
                                   f"past 1.44 times its area in frame {tear_frame} (limit {GIRDLE_LIMIT:.1%}, vanilla's worst {VANILLA_GIRDLE_WORST:.1%}): "
                                   "the raised arm tears the armpit and the side of the chest",
                        "share": round(float(tear[tear_frame]), 4), "frame": tear_frame})
    return out, numbers


# ---- the ease ----------------------------------------------------------------------------------------------------------

@dataclass
class ShoulderEase:
    changed: bool
    group: str = ""
    joints: Tuple[str, ...] = ()
    share: float = 0.0  # the largest share used in any frame
    frames_changed: int = 0
    ramp_frames: int = 0
    worst_before: float = 0.0
    worst_after: float = 0.0
    reference: str = ""
    note: str = ""
    tried: Dict[str, dict] = field(default_factory=dict)


def stance(mesh: pdx_deform.SkinnedMesh, idle: Optional[pdx_deform.Animation]) -> Dict[str, np.ndarray]:
    """Each joint's reference rotation: the idle's first frame where the idle keys it, else the rest pose."""

    bind = pdx_deform._bind_locals(mesh)
    out = {mesh.bones[i]: tripo_pose._quaternion_from_matrix(bind[i]) for i in range(len(mesh.bones))}
    if idle is not None:
        for name, channel in idle.channels.items():
            if name in out and len(channel["q"]):
                q = np.asarray(channel["q"][0], float)
                out[name] = q / max(float(np.linalg.norm(q)), 1e-12)
    return out


def _turned(anim: pdx_deform.Animation, joints: Sequence[str], reference: dict, weights: np.ndarray) -> pdx_deform.Animation:
    return tripo_pose._turned_toward_rest(anim, joints, reference, 1.0, np.asarray(weights, float))


def _frame_deformation(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, edges: np.ndarray, rest: np.ndarray) -> np.ndarray:
    """(frames, 3): each frame's stretched and squashed edge counts and its largest growth, by the kit's measure (`stretch_smooth._deformed`)."""

    matrices = pdx_deform.skinning_matrices(mesh, anim)
    out = np.zeros((matrices.shape[0], 3))
    for frame in range(matrices.shape[0]):
        posed = pdx_deform.skin(mesh, matrices[frame])
        s, q, g = stretch_smooth._deformed(rest, np.linalg.norm(posed[edges[:, 0]] - posed[edges[:, 1]], axis=1), max(mesh.height, 1e-6))
        out[frame] = (s.sum(), q.sum(), g.max())
    return out


def summary(frames: np.ndarray) -> Dict[str, float]:
    """The clip's worst-frame counts and growth from `_frame_deformation`, in the form `stretch_smooth.worse` reads."""

    return {"stretched": int(frames[:, 0].max()), "squashed": int(frames[:, 1].max()), "worst": float(frames[:, 2].max())}


def within(frames: np.ndarray, before: Dict[str, float]) -> np.ndarray:
    """(frames,) True where a frame stays inside what `stretch_smooth.worse` allows against the clip's `before`."""

    share = stretch_smooth.WORSEN_SHARE
    return ((frames[:, 0] <= before["stretched"] * (1 + share) + 1) & (frames[:, 1] <= before["squashed"] * (1 + share) + 1)
            & (frames[:, 2] <= max(before["worst"], 0.0) * (1 + share) + 1e-6))


def ease_groups(rig: ShoulderRig, mesh: pdx_deform.SkinnedMesh) -> List[Tuple[str, Tuple[str, ...]]]:
    spine = tuple(name for name in SPINE if name in mesh.bones)
    clavicles = tuple(mesh.bones[j] for j in rig.clavicles)
    groups = [("spine", spine), ("clavicles", clavicles), ("spine and clavicles", spine + clavicles)]
    return [(name, joints) for name, joints in groups if joints]


@dataclass
class _Clip:
    """What every group's plan of one clip is judged against."""

    mesh: pdx_deform.SkinnedMesh
    anim: pdx_deform.Animation
    measure: Swelling
    before: np.ndarray  # the swelling per frame
    reference: dict
    edges: np.ndarray
    rest: np.ndarray
    deformed: Dict[str, float]  # the kit's counts before
    loop: bool
    target: float
    neck_rig: object = None
    neck_floor: Optional[float] = None


def _plan(clip: _Clip, joints: List[str]):
    """(record, rejection, weights, result, after, added) for turning `joints` toward the stance (see the module text)."""

    mesh, anim = clip.mesh, clip.anim
    posed = [_turned(anim, joints, clip.reference, np.full(anim.frames, s)) for s in SHARES]
    swell = np.stack([clip.measure.per_frame(p) for p in posed])
    # a share is allowed in a frame while it and every smaller share keep the frame inside the kit's rule against the clip before
    allowed = np.logical_and.accumulate(np.stack([within(_frame_deformation(mesh, p, clip.edges, clip.rest), clip.deformed) for p in posed]), axis=0)
    cap = SHARES[np.maximum(allowed.sum(axis=0) - 1, 0)]
    reached = (swell <= clip.target + 1e-9) & allowed
    lowest = SHARES[np.argmin(np.where(allowed, swell, np.inf), axis=0)]
    needed = np.where(reached.any(axis=0), SHARES[np.argmax(reached, axis=0)], lowest)
    needed = np.where(clip.before <= clip.target, 0.0, needed)
    turn = max(tripo_pose.turn_to_target_degrees(anim.channels[j]["q"], clip.reference[j]) for j in joints)
    ramp = max(tripo_trim.settle_frames(turn * float(needed.max())), MIN_RAMP_FRAMES)
    weights = np.minimum(tripo_cloak_bend.spread(needed, ramp, clip.loop), np.maximum(cap, needed))
    result = _turned(anim, joints, clip.reference, weights)
    after = float(clip.measure.per_frame(result).max())
    added = tripo_neck.added_turn(anim, result, joints)
    record = {"worst_after": round(after, 4), "turn_added_degrees": round(added, 1), "reaches_target": bool(after <= clip.target + 1e-9),
              "ramp_frames": int(ramp)}
    why = ""
    if after >= float(clip.before.max()) - 1e-4:
        why = "does not lower the worst frame"
    elif clip.neck_floor is not None and float(tripo_neck.visible_neck(mesh, result, clip.neck_rig).min()) < clip.neck_floor - 1e-6:
        why = "sinks the neck"
    elif stretch_smooth.worse(clip.deformed, summary(_frame_deformation(mesh, result, clip.edges, clip.rest))):
        why = "makes the clip's deformation worse"
    if why:
        record["rejected"] = why
    return record, why, weights, result, after, added


def ease_animation(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, role: str, idle: Optional[pdx_deform.Animation] = None,
                   keyed: Optional[Sequence[str]] = None, limit: float = SWELL_LIMIT,
                   target: float = SWELL_TARGET) -> Tuple[ShoulderEase, Optional[pdx_deform.Animation], np.ndarray]:
    """The ease of `ease_shoulders` on a clip in memory: (record, the eased clip or None when unchanged, the per-frame weights). `keyed`: the
    joints whose rotations the clip's file stores (all of the clip's channels when not given)."""

    none = np.zeros(anim.frames)
    rig = shoulder_rig(mesh)
    if rig is None:
        return ShoulderEase(False, note="no head and two upper arms under one chest"), None, none
    measure = Swelling(mesh, rig)
    before = measure.per_frame(anim)
    worst = float(before.max()) if len(before) else 0.0
    if worst <= limit:
        return ShoulderEase(False, worst_before=worst, worst_after=worst, note="the shoulders are under the limit"), None, none
    keyed = list(anim.channels) if keyed is None else list(keyed)
    edges = pdx_deform.mesh_edges(mesh)
    rest = np.linalg.norm(mesh.positions[edges[:, 0]] - mesh.positions[edges[:, 1]], axis=1)
    neck_rig = tripo_neck.neck_rig(mesh)
    neck_before = tripo_neck.visible_neck(mesh, anim, neck_rig)
    clip = _Clip(mesh, anim, measure, before, stance(mesh, idle), edges, rest, summary(_frame_deformation(mesh, anim, edges, rest)),
                 role in tripo_pose.LOOP_ROLES, target, neck_rig,
                 min(tripo_neck.NECK_LIMIT, float(neck_before.min())) if neck_before is not None and len(neck_before) else None)
    plans, tried = [], {}
    for order, (name, group) in enumerate(ease_groups(rig, mesh)):
        joints = [j for j in group if j in keyed]
        if not joints:
            continue
        record, why, weights, result, after, added = _plan(clip, joints)
        tried[name] = record
        if not why:
            reaches = record["reaches_target"]
            plans.append((not reaches, added if reaches else after, order, after, name, joints, weights, result, record["ramp_frames"]))
    if not plans:
        return ShoulderEase(False, worst_before=worst, worst_after=worst, note="no group lowers the swelling within the kit's rules",
                            tried=tried), None, none
    _, _, _, after, name, joints, weights, result, ramp = min(plans, key=lambda plan: plan[:3])
    return ShoulderEase(True, name, tuple(joints), round(float(weights.max()), 3), int((weights > 0).sum()), int(ramp), worst, after,
                        "idle's first frame" if idle is not None else "rest pose", tried=tried), result, weights


def ease_shoulders(mesh_path: Path, anim_path: Path, out_path: Path, role: str, idle_path: Optional[Path] = None,
                   limit: float = SWELL_LIMIT, target: float = SWELL_TARGET) -> ShoulderEase:
    """Write `out_path`: `anim_path` with the spine or the clavicles turned toward the unit's stance where its shoulders swell past `limit`
    (see the module text). Unchanged, and copied as it is, when the clip passes or no group lowers it."""

    data = bytearray(Path(anim_path).read_bytes())
    keyed = [joint.name for joint in read(anim_path).child("info").children if "q" in str((joint.properties.get("sa") or [""])[0])]
    idle = pdx_deform.load_anim(idle_path) if idle_path is not None and Path(idle_path).is_file() else None
    ease, result, weights = ease_animation(pdx_deform.load_mesh(mesh_path), pdx_deform.load_anim(anim_path), role, idle, keyed, limit, target)
    if result is not None:
        tripo_pose._write_rotations(data, keyed, ease.joints, result, weights)
    Path(out_path).write_bytes(bytes(data))
    return ease


# ---- the clavicle lever ------------------------------------------------------------------------------------------------
#
# Run by `run_pilot` right after the shoulder ease (`ease_clavicles`): a clip still over TRIPO-SHOULDER-TEAR or the swell limit has its left, right
# or both clavicles turned toward the idle's first frame, each upper arm keeping its world direction (`keep_arms`), so the hand and the weapon
# keep their path and only the arm's root moves (the weapon is on its own bone under the hand, so the grip itself does not change). Each frame
# takes the smallest share that brings it under both limits while its deformed edges stay inside the kit's strict no-worse rule (`within`), spread
# by a smoothstep, no written joint faster than `MAX_STEP_DEGREES` a frame. When keeping the arms cannot lower the girdle, the arm may follow its
# clavicle, never lowering a hand's highest point above the chest by more than `RAISE_KEEP`. Measured (2026-11-18): frozen at the idle's stance
# with the arm's direction kept, the clavicle that drives the ogre's tear (the left in its defend, the right in its attack) took the girdle from
# 0.161 to 0.122 and from 0.191 to 0.115. As the rule on ogre_m's files the attack went from 0.181 to 0.156 (both clavicles, 0.4, the hands
# 2.5% of the height) and the defend from 0.166 to 0.154 (the left, 0.4, 3.6%), and the same in the run ogre_o. On ogre_n's files, where the
# shoulder ease had turned the clavicles 0.6 already, only the arm following lowered the attack (the right clavicle 0.1: 0.164 to 0.153, the hand
# 1.4%). The orc and the zombie pass both limits.

MAX_STEP_DEGREES = 35.0  # a written joint never turns further in one frame than this (UNIT-ANIM-SPIN: vanilla's fastest joint turns 37)
RAISE_KEEP = 0.01  # an arm that follows its clavicle may lower a hand's highest point above the chest by at most this share of the height


def _world_rotations(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, joints: Sequence[int]) -> np.ndarray:
    world = tripo_neck._world(mesh, anim)[:, list(joints), :3, :3]
    u, _s, vt = np.linalg.svd(world)
    return u @ vt


def keep_arms(mesh: pdx_deform.SkinnedMesh, before: pdx_deform.Animation, after: pdx_deform.Animation, arms: Sequence[int]) -> pdx_deform.Animation:
    """`after` with each upper arm's local rotation set so it points in the world as it did in `before`: the arm and what it holds keep their
    direction, only the arm's root moves with the clavicle."""

    target = _world_rotations(mesh, before, arms)
    parents = _world_rotations(mesh, after, [mesh.parents[a] for a in arms])
    channels = {name: dict(channel) for name, channel in after.channels.items()}
    for k, arm in enumerate(arms):
        name = mesh.bones[arm]
        old = after.channels[name]["q"]
        q = old.copy()
        for frame in range(after.frames):
            new = tripo_pose._quaternion_from_matrix(parents[frame, k].T @ target[frame, k])
            q[frame] = new if float(new @ old[frame]) >= 0 else -new
        channels[name]["q"] = q
    return pdx_deform.Animation(after.fps, after.frames, channels)


def _max_step(anim: pdx_deform.Animation, joints: Sequence[str]) -> float:
    return max((tripo_pose.quaternion_turn(a, b) for j in joints for a, b in zip(anim.channels[j]["q"][:-1], anim.channels[j]["q"][1:])), default=0.0)


def hand_raise(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> float:
    """The highest any hand rises above the chest joint (`Spine02`, else the hips) in the clip, as a share of the height."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    hands = [i for name, i in index.items() if name.lower() in ("lefthand", "righthand")]
    if not hands:
        return 0.0
    joints = pdx_motion.posed_joints(mesh, anim)
    chest = joints[:, index.get("Spine02", index.get("Hips", 0)), 1]
    return float((joints[:, hands, 1] - chest[:, None]).max() / max(mesh.height, 1e-6))


def hand_shift(mesh: pdx_deform.SkinnedMesh, before: pdx_deform.Animation, after: pdx_deform.Animation) -> float:
    """The furthest any hand moves between the two clips in one frame, as a share of the height."""

    hands = [i for i, name in enumerate(mesh.bones) if "hand" in name.lower()]
    if not hands:
        return 0.0
    a, b = pdx_motion.posed_joints(mesh, before)[:, hands], pdx_motion.posed_joints(mesh, after)[:, hands]
    return float(np.linalg.norm(a - b, axis=-1).max() / max(mesh.height, 1e-6))


@dataclass
class ClavicleEase:
    changed: bool
    group: str = ""
    joints: Tuple[str, ...] = ()
    share: float = 0.0
    frames_changed: int = 0
    ramp_frames: int = 0
    girdle_before: float = 0.0
    girdle_after: float = 0.0
    swell_before: float = 0.0
    swell_after: float = 0.0
    hand_shift: float = 0.0  # the furthest a hand moves, share of the height
    note: str = ""
    tried: Dict[str, dict] = field(default_factory=dict)


def _clavicle_plan(mesh, anim, joints, arms, reference, girdle, swell, edges, rest, before_deformed, loop):
    """(record, result, weights, why) for turning `joints` (clavicles) toward `reference`, with the `arms` kept in their world direction (none:
    the arms follow their clavicles)."""

    def posed_at(weights):
        turned = _turned(anim, joints, reference, weights)
        return keep_arms(mesh, anim, turned, arms) if arms else turned

    posed = [posed_at(np.full(anim.frames, s)) for s in SHARES]
    tear = np.stack([girdle.per_frame(p) for p in posed])
    ball = np.stack([swell.per_frame(p) for p in posed])
    allowed = np.logical_and.accumulate(np.stack([within(_frame_deformation(mesh, p, edges, rest), before_deformed) for p in posed]), axis=0)
    cap = SHARES[np.maximum(allowed.sum(axis=0) - 1, 0)]
    under = (tear <= GIRDLE_LIMIT + 1e-9) & (ball <= SWELL_LIMIT + 1e-9) & allowed
    lowest = SHARES[np.argmin(np.where(allowed, tear / GIRDLE_LIMIT + ball / SWELL_LIMIT, np.inf), axis=0)]
    needed = np.where(under.any(axis=0), SHARES[np.argmax(under, axis=0)], lowest)
    needed = np.where((tear[0] <= GIRDLE_LIMIT) & (ball[0] <= SWELL_LIMIT), 0.0, needed)
    turn = max(tripo_pose.quaternion_turn(q, reference[j]) for j in joints for q in anim.channels[j]["q"])
    ramp = max(tripo_trim.settle_frames(turn * float(needed.max())), MIN_RAMP_FRAMES)
    weights = np.minimum(tripo_cloak_bend.spread(needed, ramp, loop), np.maximum(cap, needed))
    result = posed_at(weights)
    after_tear, after_ball = float(girdle.per_frame(result).max()), float(swell.per_frame(result).max())
    written = list(joints) + [mesh.bones[a] for a in arms]
    record = {"girdle_after": round(after_tear, 4), "swell_after": round(after_ball, 4), "ramp_frames": int(ramp),
              "turn_added_degrees": round(tripo_neck.added_turn(anim, result, joints), 1),
              "reaches_limits": bool(after_tear <= GIRDLE_LIMIT + 1e-9 and after_ball <= SWELL_LIMIT + 1e-9),
              "max_step_degrees": round(_max_step(result, written), 1)}
    why = ""
    if after_tear >= float(tear[0].max()) - 1e-4:
        why = "does not lower the girdle's worst frame"
    elif record["max_step_degrees"] > max(MAX_STEP_DEGREES, _max_step(anim, written) + 1e-6):
        why = "a joint would turn faster than the spin rule allows"
    elif stretch_smooth.worse(before_deformed, summary(_frame_deformation(mesh, result, edges, rest))):
        why = "makes the clip's deformation worse"
    elif not arms and hand_raise(mesh, result) < hand_raise(mesh, anim) - RAISE_KEEP:
        why = "lowers the raised hand"
    return record, result, weights, why


def clavicle_animation(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, role: str, idle: Optional[pdx_deform.Animation] = None,
                       keyed: Optional[Sequence[str]] = None) -> Tuple[ClavicleEase, Optional[pdx_deform.Animation], np.ndarray, Tuple[str, ...]]:
    """The clavicle lever on a clip in memory (see `ease_clavicles`): (record, the eased clip or None, the per-frame weights, the joints written)."""

    none = np.zeros(anim.frames)
    rig = shoulder_rig(mesh)
    if rig is None:
        return ClavicleEase(False, note="no head and two upper arms under one chest"), None, none, ()
    girdle, swell = Swelling(mesh, rig, girdle=True), Swelling(mesh, rig)
    tear0, ball0 = float(girdle.per_frame(anim).max()), float(swell.per_frame(anim).max())
    base = ClavicleEase(False, girdle_before=tear0, girdle_after=tear0, swell_before=ball0, swell_after=ball0)
    if tear0 <= GIRDLE_LIMIT and ball0 <= SWELL_LIMIT:
        base.note = "the shoulders pass both limits"
        return base, None, none, ()
    keyed = list(anim.channels) if keyed is None else list(keyed)
    reference = stance(mesh, idle)
    edges = pdx_deform.mesh_edges(mesh)
    rest = np.linalg.norm(mesh.positions[edges[:, 0]] - mesh.positions[edges[:, 1]], axis=1)
    before_deformed = summary(_frame_deformation(mesh, anim, edges, rest))
    sides = [(mesh.bones[c], arm) for c, arm in zip(rig.clavicles, (rig.left, rig.right)) if mesh.bones[c] in keyed and mesh.bones[arm] in keyed]
    groups = [(name, [pair]) for name, pair in zip(("left clavicle", "right clavicle"), sides)] + [("both clavicles", sides)]
    groups = [(name, pairs, True) for name, pairs in groups] + [(name + ", arm follows", pairs, False) for name, pairs in groups]
    plans = []
    for order, (name, pairs, kept) in enumerate(groups):
        if not pairs:
            continue
        joints, arms = [c for c, _a in pairs], [a for _c, a in pairs] if kept else []
        record, result, weights, why = _clavicle_plan(mesh, anim, joints, arms, reference, girdle, swell, edges, rest, before_deformed,
                                                      role in tripo_pose.LOOP_ROLES)
        if why:
            record["rejected"] = why
        base.tried[name] = record
        if not why:
            score = record["turn_added_degrees"] if record["reaches_limits"] else record["girdle_after"] / GIRDLE_LIMIT + record["swell_after"] / SWELL_LIMIT
            plans.append((not record["reaches_limits"], not kept, score, order, name, joints, arms, record, result, weights))
    if not plans:
        base.note = "no clavicle lowers the girdle within the kit's rules"
        return base, None, none, ()
    # A plan that reaches both limits first, then one whose arms keep their direction, then the least turn (or the lowest measures).
    _, _, _, _, name, joints, arms, record, result, weights = min(plans, key=lambda plan: plan[:4])
    written = tuple(joints) + tuple(mesh.bones[a] for a in arms)
    return ClavicleEase(True, name, tuple(joints), round(float(weights.max()), 3), int((weights > 0).sum()), record["ramp_frames"], tear0,
                        record["girdle_after"], ball0, record["swell_after"], round(hand_shift(mesh, anim, result), 4), tried=base.tried), result, weights, written


def ease_clavicles(mesh_path: Path, anim_path: Path, out_path: Path, role: str, idle_path: Optional[Path] = None) -> ClavicleEase:
    """Write `out_path`: `anim_path` with the clavicle that drives a torn shoulder turned toward the unit's stance, the upper arm keeping its
    direction in the world (see the module text). Unchanged, and copied as it is, when the clip passes or no clavicle helps."""

    data = bytearray(Path(anim_path).read_bytes())
    keyed = [joint.name for joint in read(anim_path).child("info").children if "q" in str((joint.properties.get("sa") or [""])[0])]
    idle = pdx_deform.load_anim(idle_path) if idle_path is not None and Path(idle_path).is_file() else None
    ease, result, weights, written = clavicle_animation(pdx_deform.load_mesh(mesh_path), pdx_deform.load_anim(anim_path), role, idle, keyed)
    if result is not None:
        tripo_pose._write_rotations(data, keyed, written, result, weights)
    Path(out_path).write_bytes(bytes(data))
    return ease
