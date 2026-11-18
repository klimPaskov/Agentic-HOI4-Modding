"""The shoulder girdle's weights of a Tripo humanoid: the upper arm's weight kept to the arm, judged by a bounded trade.

Two fresh reviewers failed the round 4 ogre (ogre_l, 2026-11-18) for the skin round every raised arm: under the club arm in the attack (frames 16
to 26) the shoulder, the armpit and the side of the chest smeared and flattened, pulled up toward the arm, and in every frame of the defend the
guard arm's shoulder and upper back ballooned into a hump with the upper arm merged into it. TRIPO-SHOULDER-SWELL passed both, so its region
missed the side under the arm. TRIPO-SHOULDER-TEAR (`lib/tripo_shoulder.py`) measures the girdle, the shoulder region with the torso under the
arm, at 1.44 times the area: vanilla's worst is 0.125, the limit 0.156, ogre_l's attack 0.181 and defend 0.166 fail, the orc (orc_k, 0.124)
and the zombie (zombie_l, 0.098) pass.

The rule (`confine_arm_weights`): each upper arm's weight on skin further from the arm's own bone (the segment from the shoulder joint to the
elbow) than `INNER` arm radii is given to the clavicle, all of it past `OUTER`, a smoothstep between. The arm's radius is the median distance
from that segment of the vertices the upper arm moves most. The clavicle carries it from there as it carries the skin round the joint already.
Locked vertices (a held weapon, the chain stage's cloak and wing bones, the armour plates) keep their rows. The rule runs on the repaired
export's weights, before the smoothing and the fit, which then run on its result as on the unchanged weights.

Measured offline on the round 4 ogre (the repaired export of ogre_l with its exported clips, smoothed and fitted as `run_pilot` does), every
clip's worst frame, against the same weights smoothed and fitted without it:

    clip      stretched   squashed   girdle         swell
    attack    335 to 329  135 to 109  0.191 to 0.135  0.063 to 0.034
    defend    109 to 69   27 to 21   0.161 to 0.102  0.067 to 0.021
    death     222 to 239  128 to 107  0.141 to 0.124  0.059 to 0.045
    retreat   223 to 190  107 to 81  0.109 to 0.096  0.017 to 0.013
    idle      0 to 4      10 to 7    0.004 to 0.006
    move      22 to 26    28 to 22   0.015 to 0.014

The unit's deformed edges fell from 1,346 to 1,204, and the attack and the defend went under TRIPO-SHOULDER-TEAR's limit. Tried on the same
files and dropped: the clavicle's weight on the torso given to the chest or shared over the spine bones as the vertex holds them, with a
falloff of 1 to 2 arm radii from the shoulder joint (the defend's girdle rose to 0.217 and 0.227: in the defend the clavicle turns 41 to 44
degrees, and skin that no longer follows it tears against the arm), both rules together (the unit's deformed edges rose to 1,985 and 1,407),
the arm's capsule at 1.2 to 1.8 radii (the defend's girdle 0.165), at 1.75 to 2.75 (the attack 0.169) and at 1.5 to 3 (1,505 deformed edges),
at 2 to 3 (the defend 0.170), and the arm's weight given away medial of its joint instead of by distance (both clips worse).

The kit's strict rule (no clip's worst count up by more than 2%, no edge growing further) is relaxed for this rule to a bounded trade, by the
maintainer's coordinator (2026-11-18): the rule is kept when it lowers the girdle and the swell in every clip that fails either, lowers the
unit's deformed edges, and leaves each clip's worst frame (its stretched and its squashed edge counts) within `BOUND` (10%) of the weights
without it, or within `FLOOR_SHARE` of the mesh's edges for a clip with few (the ogre's idle, 2 to 4). The longest single edge growth is not
part of the bound and is recorded beside it (`growth_over_bound`): it moves by a few tenths of a percent of the height between two fits of the
same weights, and on the ogre the rule's longest edge (the low back under the club arm, 4.3% to 4.9% of the height in the attack) is far from
the girdle it fixes. A fit seeded from the rule's weights with the clavicle given the far weight only near the joint and the spine bones the
rest (1 to 2 radii) lowered the unit's edges further (1,140) but left the attack's girdle at 0.160, over the limit.

The kit route measured the ogre (`run_pilot.fit_staged_weights` on ogre_l's repaired export and clips, 2026-11-18): deformed edges 1,330 to
1,204, the attack's girdle 0.187 to 0.135 and swell 0.068 to 0.034, the defend's 0.169 to 0.102 and 0.077 to 0.021, the death's stretched
edges 210 to 239 (within the floor), every other count lower or within the bound. On the orc and the zombie every clip passes the shoulder
checks, so the rule is not tried. Forced on them it changed the orc's edges from 3,207 to 3,210 (its plates and cloak are locked) and took the
zombie's from 758 to 639, no clip past the bound.

The run ogre_m (ogre_l's clips, 2026-11-18) tried the rule before the shoulder ease, where it could not lower what the ease then left (the
attack's girdle 0.198 to 0.197), and its export failed TRIPO-SHOULDER-TEAR in the attack (0.181, frame 20) and the defend (0.166, frame 28).
`run_pilot.girdle_trial` now runs after the pose eases. On ogre_m's files that trial lowered the girdle (attack 0.197 to 0.156, defend 0.210 to
0.177, each swell about halved) but the trade refused it: the unit's deformed edges rose from 1,591 to 1,719, the attack's worst-frame
stretched edges from 368 to 440 and the death's from 242 to 343 (the death now settles its split thighs, `lib/tripo_splay.py`). The two fits
of the same start on nearly the same clips (ogre_l, ogre_m) differ by more than what the rule gains, so this rule is not yet the fix.

Only the `ix`, `w` and `bones` values of the `skin` blocks change (`stretch_smooth.write_weights`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import pdx_deform, pdx_motion, stretch_smooth, tripo_shoulder

INNER = 1.5
OUTER = 2.5
BOUND = 0.10
FLOOR_SHARE = 0.001


def _smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / max(e1 - e0, 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _segment_distance(points: np.ndarray, a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    ab = b - a
    t = (points - a) @ ab / max(float(ab @ ab), 1e-12)
    return np.linalg.norm(points - (a + np.clip(t, 0.0, 1.0)[:, None] * ab), axis=1), t


def arm_radius(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, arm: int, forearm: int) -> Optional[float]:
    """The upper arm's radius: the median distance from its segment of the vertices it moves most (in the middle of the segment, else
    anywhere, else those with at least 0.3 of its weight). None when no vertex qualifies."""

    joints = pdx_motion.rest_joints(mesh)
    distance, t = _segment_distance(mesh.positions, joints[arm], joints[forearm])
    dominant = pdx_deform.dominant_bones(mesh) == arm
    for pick in (dominant & (t > 0.2) & (t < 0.8), dominant, dense[:, arm] >= 0.3):
        if pick.any():
            return float(np.median(distance[pick]))
    return None


def confined_dense(mesh: pdx_deform.SkinnedMesh, dense: np.ndarray, locked: np.ndarray, inner: float = INNER, outer: float = OUTER) -> Tuple[np.ndarray, dict]:
    """(dense weights after the rule, record): each upper arm's weight past `inner` radii from its segment goes to its clavicle."""

    rig = tripo_shoulder.shoulder_rig(mesh)
    out = dense.copy()
    record: dict = {}
    if rig is None:
        return out, {"note": "no head and two upper arms under one chest"}
    joints = pdx_motion.rest_joints(mesh)
    for side, arm in (("left", rig.left), ("right", rig.right)):
        forearm = tripo_shoulder._forearm(mesh, arm)
        clavicle = mesh.parents[arm]
        radius = arm_radius(mesh, dense, arm, forearm) if forearm >= 0 else None
        if radius is None or clavicle < 0:
            record[side] = {"note": "no upper arm radius or no clavicle"}
            continue
        distance, _t = _segment_distance(mesh.positions, joints[arm], joints[forearm])
        moved = out[:, arm] * _smoothstep(inner * radius, outer * radius, distance)
        moved[locked] = 0.0
        out[:, arm] -= moved
        out[:, clavicle] += moved
        record[side] = {"radius": round(radius, 4), "weight_moved": round(float(moved.sum()), 2), "vertices": int((moved > 1e-6).sum())}
    return out, record


def confine_arm_weights(mesh_path: Path, out_path: Path, locked_bones: Sequence[str] = (), locked_prefixes: Sequence[str] = (),
                        locked_mask: Optional[np.ndarray] = None) -> dict:
    """Write `out_path`: the mesh with the rule applied to its weights (see the module text). Returns what moved."""

    mesh = pdx_deform.load_mesh(mesh_path)
    dense = stretch_smooth.dense_weights(mesh)
    canon = pdx_deform.weld(mesh.positions, max(mesh.height, 1e-6) * 1e-5)
    locked = stretch_smooth.locked_vertices(mesh, dense, canon, locked_bones, locked_prefixes)
    if locked_mask is not None:
        locked = locked | np.asarray(locked_mask, bool)
    new, record = confined_dense(mesh, dense, locked)
    joints, weights = stretch_smooth.sparse_rows(new)
    stretch_smooth.write_weights(mesh_path, out_path, joints, weights, mesh.bones)
    return record


def measures(mesh_path: Path, anim_paths: Sequence[Path]) -> Dict[str, dict]:
    """Per clip: the worst-frame stretched and squashed counts and longest growth by the kit's measure, the girdle's tear and the swell."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anims = {Path(p).stem: pdx_deform.load_anim(p) for p in anim_paths}
    clips = stretch_smooth._Clips(mesh, anims, pdx_deform.mesh_edges(mesh))
    girdle, swell = tripo_shoulder.Swelling(mesh, girdle=True), tripo_shoulder.Swelling(mesh)
    out = {}
    for name, anim in anims.items():
        out[name] = dict(clips.summary(name), girdle=round(float(girdle.per_frame(anim).max()), 4), swell=round(float(swell.per_frame(anim).max()), 4))
    out["_edges"] = int(len(clips.edges))
    return out


@dataclass
class Trade:
    accepted: bool
    deformed_before: int = 0
    deformed_after: int = 0
    reasons: List[str] = field(default_factory=list)
    clips: Dict[str, dict] = field(default_factory=dict)


def trade(before: Dict[str, dict], after: Dict[str, dict], height_share: float = pdx_deform.SIGNIFICANT_SHARE) -> Trade:
    """Whether `after` (the rule's weights) is kept against `before` (the same route without it), by the bounded trade of the module text."""

    floor = FLOOR_SHARE * before.get("_edges", 0)
    names = [name for name in before if not name.startswith("_")]
    total_before = sum(before[n]["stretched"] + before[n]["squashed"] for n in names)
    total_after = sum(after[n]["stretched"] + after[n]["squashed"] for n in names)
    reasons, clips = [], {}
    if total_after >= total_before:
        reasons.append(f"the unit's deformed edges do not fall ({total_before} to {total_after})")
    for n in names:
        b, a = before[n], after[n]
        clips[n] = {key: [b[key], a[key]] for key in ("stretched", "squashed", "worst", "girdle", "swell")}
        for key in ("stretched", "squashed"):
            if a[key] > max(b[key] * (1 + BOUND), b[key] + floor):
                reasons.append(f"{n}: worst-frame {key} {b[key]} to {a[key]}")
        if a["worst"] > max(b["worst"] * (1 + BOUND), b["worst"] + height_share):
            clips[n]["growth_over_bound"] = True
        failing = b["girdle"] > tripo_shoulder.GIRDLE_LIMIT or b["swell"] > tripo_shoulder.SWELL_LIMIT
        if failing and not (a["girdle"] < b["girdle"] and a["swell"] <= b["swell"] + 1e-4):
            reasons.append(f"{n}: fails the shoulder checks and the rule does not lower both")
    return Trade(not reasons, total_before, total_after, reasons, clips)
