"""Measure a rigged Tripo GLB's candidate clips on a unit's exported skin: the shoulder swell, the neck, the hand's raise and reach.

    py -3.13 .tools/3d_pipeline/tripo/pose_check.py <rigged.glb> <unit.mesh> [--clips NAME ...] [--attack NAME ...] [--unarmed] [--hand RightHand] [--json out.json]

The clip pick (docs/3d-units.md, "Pick the clips by measurement") needs to know, before a clip is bought into the route, whether its pose
swells the shoulders (TRIPO-SHOULDER-SWELL, `lib/tripo_shoulder.py`) or sinks the head (TRIPO-NECK-SUNK, `lib/tripo_neck.py`) on the skin the
route makes. Those depend on the route's weights, which only an earlier run of the same body has. This tool reads that run's exported `.mesh`
(the skeleton and the fitted weights) and each clip of the rigged GLB, and plays the clip on the mesh:

1. The GLB's rest joints are matched to the mesh's by name (Tripo's `mixamorig:` names to the kit's, as `prepare_tripo_unit.KIT_BONES`), and
   the axes and scale between the two files are solved from the rest joint positions (orthogonal Procrustes with scale).
2. Per frame (30 a second, as the export), each mapped joint's world rotation away from its rest is carried to the mesh's joint in the mesh's
   axes, and the root's travel is scaled. The joints' lengths are the mesh's. Bones the GLB has not (the weapon's) follow their parents.
3. On that clip: the shoulder swell (worst frame), the visible neck (lowest frame), the holding hand's highest point above the chest joint
   (`Spine02`) as a share of the height (`grip_weapon.hand_raise`), each hand's furthest point ahead of the chest along the way the feet
   point, and the hips' furthest horizontal travel from the first frame, both as shares of the height. The strike (`lib/tripo_strike.py`): the
   striking hand's travel against the chest over the clip and its peak speed (the holding hand, or with `--unarmed` the faster one).
4. Then the route's pose rules on the clip, in their order: the neck lift (`tripo_neck.lift_animation`), the shoulder ease toward the
   GLB's `idle` clip's first frame (`tripo_shoulder.ease_animation`), as a looping role, and the clavicle lever
   (`tripo_shoulder.clavicle_animation`), and the swell, the girdle's tear (TRIPO-SHOULDER-TEAR), the neck and the raise again. On ogre_o's
   skin (2026-11-18) the tear after the rules read chop 0.125, the poleaxe attack 0.129, the defend hit_to_stomach 0.121.

A verdict per clip says whether the swell, the tear and the neck pass their limits after the rules (`route`), and as Tripo made the clip (`raw`).
A clip named with `--attack` must also strike (TRIPO-ATTACK-NO-STRIKE's limits), and `attack_pick` names the attack by the pick rule: of the
attack candidates that pass, the largest raise or reach plus the pelvis's travel after the rules, at least `MIN_ATTACK_SCORE`. A lunge that
holds the arms out reaches as far as a blow, so the reach alone picked the zombie's static lunge three times (zombie_i, zombie_k, zombie_o).
The weights stay the earlier run's, which the route fits again to the new clips, and the grip stage and the clearance are not run, so the
numbers estimate the route's result. Checked on the round 4 ogre: the clips the run ogre_k exported measured as here within 0.003 (the
defend `hit_to_body_01` 0.161, the chop's raise 0.267). Plain numpy, no Blender.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import clip_check
from lib import pdx_deform, pdx_motion, tripo_cloak_bend, tripo_neck, tripo_pose, tripo_shoulder, tripo_strike

FRAME_RATE = 30.0
MIN_ATTACK_SCORE = 0.2  # docs/3d-units.md, the attack's raise or reach plus the pelvis's travel
PREFIX = "mixamorig:"
KIT_TO_MIXAMO = {"Spine01": "Spine1", "Spine02": "Spine2", "neck": "Neck"}


def glb_name(kit: str) -> str:
    return PREFIX + KIT_TO_MIXAMO.get(kit, kit)


def _rotations(matrices: np.ndarray) -> np.ndarray:
    r = np.asarray(matrices, float)[..., :3, :3]
    u, _s, vt = np.linalg.svd(r)
    return u @ vt


def procrustes(source: np.ndarray, target: np.ndarray):
    """(axes, scale, offset) with target ~ scale * axes @ source + offset. `axes` is orthogonal and may mirror (the export flips an axis)."""

    a, b = source.mean(axis=0), target.mean(axis=0)
    x, y = source - a, target - b
    u, s, vt = np.linalg.svd(y.T @ x)
    axes = u @ vt
    scale = float(s.sum() / max(float((x * x).sum()), 1e-12))
    return axes, scale, b - scale * axes @ a


class Transfer:
    """Plays the GLB's clips on the unit's mesh skeleton."""

    def __init__(self, rig: clip_check.Rig, mesh: pdx_deform.SkinnedMesh):
        self.rig, self.mesh = rig, mesh
        self.pairs = [(b, rig.joint_names.index(glb_name(name))) for b, name in enumerate(mesh.bones) if glb_name(name) in rig.joint_names]
        rest = rig.joint_worlds({})
        bind = np.linalg.inv(mesh.inverse_bind)
        mapped = [b for b, _ in self.pairs]
        self.axes, self.scale, self.offset = procrustes(rest[[g for _, g in self.pairs], :3, 3], bind[mapped, :3, 3])
        self.glb_rest = {g: _rotations(rest[g]) for _, g in self.pairs}
        self.bind_rot = _rotations(bind)
        self.locals = pdx_deform._bind_locals(mesh)
        self.root = next((b for b, _ in self.pairs if mesh.parents[b] < 0 or mesh.parents[b] not in mapped), self.pairs[0][0])
        self.root_glb = dict(self.pairs)[self.root]

    def animation(self, tracks: dict, end: float) -> pdx_deform.Animation:
        frames = int(round(end * FRAME_RATE)) + 1
        mesh, axes = self.mesh, self.axes
        world = {b: np.zeros((frames, 3, 3)) for b, _ in self.pairs}
        root_t = np.zeros((frames, 3))
        for f in range(frames):
            worlds = self.rig.joint_worlds(self.rig.pose_for(tracks, min(f / FRAME_RATE, end)))
            for b, g in self.pairs:
                turn = _rotations(worlds[g]) @ self.glb_rest[g].T
                world[b][f] = axes @ turn @ axes.T @ self.bind_rot[b]
            root_t[f] = self.scale * axes @ worlds[self.root_glb][:3, 3] + self.offset
        channels: Dict[str, Dict[str, np.ndarray]] = {}
        bind = np.linalg.inv(mesh.inverse_bind)
        for b, _ in self.pairs:
            parent = mesh.parents[b]
            parent_rot = world[parent] if parent in world else np.broadcast_to(self.bind_rot[parent] if parent >= 0 else np.eye(3), (frames, 3, 3))
            local = np.einsum("fji,fjk->fik", parent_rot, world[b])
            q = np.stack([tripo_pose._quaternion_from_matrix(m) for m in local])
            if b != self.root:
                t = np.tile(self.locals[b][:3, 3], (frames, 1))
            elif parent >= 0:  # a root under an unmapped bone: its place in that bone's bind frame
                inverse = np.linalg.inv(bind[parent])
                t = root_t @ inverse[:3, :3].T + inverse[:3, 3]
            else:
                t = root_t
            channels[mesh.bones[b]] = {"t": t, "q": q, "s": np.ones(frames)}
        return pdx_deform.Animation(FRAME_RATE, frames, channels)


def measure(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, hand: str = "RightHand", attack: bool = False, unarmed: bool = False) -> dict:
    """The clip's numbers on the mesh (see the module text). An `attack` candidate must also strike (`lib/tripo_strike.py`): the holding
    `hand`, or for an `unarmed` unit the faster hand, travels and moves fast enough against the chest."""

    height = max(mesh.height, 1e-6)
    swell = tripo_shoulder.swelling(mesh, anim)
    tear = tripo_shoulder.swelling(mesh, anim, girdle=True)
    neck = tripo_neck.visible_neck(mesh, anim)
    joints = pdx_motion.posed_joints(mesh, anim)
    index = {name: i for i, name in enumerate(mesh.bones)}
    front = tripo_cloak_bend.front_direction(mesh)
    chest = joints[:, index["Spine02"]] if "Spine02" in index else joints[:, index["Hips"]]
    out = {"frames": int(anim.frames), "swell": round(float(swell.max()), 4), "swell_frame": int(np.argmax(swell)),
           "tear": round(float(tear.max()), 4), "tear_frame": int(np.argmax(tear)),
           "neck": round(float(neck.min()), 3) if neck is not None else None, "neck_frame": int(np.argmin(neck)) if neck is not None else None}
    if hand in index:
        above = (joints[:, index[hand], 1] - chest[:, 1]) / height
        out.update(raise_=round(float(above.max()), 3), raise_frame=int(np.argmax(above)))
    reach = []
    for name in ("LeftHand", "RightHand"):
        if name in index:
            ahead = (joints[:, index[name]] - chest) @ front / height
            out[f"reach_{name}"] = round(float(ahead.max()), 3)
            reach.append(float(ahead.max()))
    out["reach"] = round(max(reach), 3) if reach else 0.0
    hips = joints[:, index["Hips"]]
    travel = hips - hips[0]
    travel[:, 1] = 0.0
    out["pelvis_travel"] = round(float(np.linalg.norm(travel, axis=1).max() / height), 3)
    strike = tripo_strike.strike_numbers(joints, mesh.bones, height, float(anim.fps or FRAME_RATE), "" if unarmed else hand)
    if strike is not None:
        out.update(strike_hand=strike["hand"], strike_travel=strike["travel"], strike_speed=strike["speed"], strikes=strike["strikes"])
    reasons = []
    if attack and strike is not None and not strike["strikes"]:
        reasons.append(f"no strike: {strike['hand']} travels {strike['travel']:.2f} at {strike['speed']:.2f}/s (at least {tripo_strike.MIN_TRAVEL} and {tripo_strike.MIN_SPEED})")
    if out["swell"] > tripo_shoulder.SWELL_LIMIT:
        reasons.append(f"swell {out['swell']:.3f} over {tripo_shoulder.SWELL_LIMIT}")
    if out["tear"] > tripo_shoulder.GIRDLE_LIMIT:
        reasons.append(f"tear {out['tear']:.3f} over {tripo_shoulder.GIRDLE_LIMIT}")
    if out["neck"] is not None and out["neck"] < tripo_neck.NECK_LIMIT:
        reasons.append(f"neck {out['neck']:.2f} under {tripo_neck.NECK_LIMIT}")
    out["verdict"] = "fail" if reasons else "pass"
    out["reasons"] = reasons
    return out


def route(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, idle: Optional[pdx_deform.Animation], role: str = "attack") -> pdx_deform.Animation:
    """The clip after the route's neck lift, shoulder ease and clavicle lever (step 4 of the module text)."""

    _lift, lifted, _weights = tripo_neck.lift_animation(mesh, anim, role)
    anim = lifted if lifted is not None else anim
    _ease, eased, _weights = tripo_shoulder.ease_animation(mesh, anim, role, idle)
    anim = eased if eased is not None else anim
    _lever, levered, _weights, _written = tripo_shoulder.clavicle_animation(mesh, anim, role, idle)
    return levered if levered is not None else anim


def is_attack(name: str, attacks: Optional[Sequence[str]]) -> bool:
    return bool(attacks) and any(name.startswith(prefix) for prefix in attacks)


def pick_attack(report: dict) -> Optional[str]:
    """The attack by the clip pick's rule (docs/3d-units.md): of the attack candidates that pass, the largest raise of the holding hand or
    forward reach plus the pelvis's travel, after the route's rules; it must be at least `MIN_ATTACK_SCORE`. None when none qualifies."""

    best, best_score = None, MIN_ATTACK_SCORE
    for name, row in report.items():
        if not row.get("attack") or row["verdict"] != "pass":
            continue
        after = row["route"]
        score = max(after.get("raise_", 0.0), after["reach"]) + after["pelvis_travel"]
        if score >= best_score:
            best, best_score = name, score
    return best


def check(glb: Path, mesh_path: Path, clips: Optional[Sequence[str]] = None, hand: str = "RightHand", idle_clip: str = "idle",
          attacks: Optional[Sequence[str]] = None, unarmed: bool = False) -> dict:
    doc, _binary = clip_check.load_glb(glb)
    body = next(node.get("name") for node in doc["nodes"] if "mesh" in node and "skin" in node)
    rig = clip_check.Rig(glb, body, None)
    mesh = pdx_deform.load_mesh(mesh_path)
    transfer = Transfer(rig, mesh)
    every = list(rig.clips())
    idle = next((transfer.animation(tracks, end) for name, tracks, end in every if name == idle_clip), None)
    report = {}
    for name, tracks, end in every:
        if clips and not any(name.startswith(c) for c in clips):
            continue
        anim = transfer.animation(tracks, end)
        attack = is_attack(name, attacks)
        raw = measure(mesh, anim, hand, attack, unarmed)
        after = measure(mesh, route(mesh, anim, idle), hand, attack, unarmed)
        report[name] = {"raw": raw, "route": after, "verdict": after["verdict"], "reasons": after["reasons"], "attack": attack}
    return {"glb": str(glb), "mesh": str(mesh_path), "hand": hand, "unarmed": unarmed, "scale": round(transfer.scale, 4),
            "limits": {"swell": tripo_shoulder.SWELL_LIMIT, "tear": tripo_shoulder.GIRDLE_LIMIT, "neck": tripo_neck.NECK_LIMIT, "strike_travel": tripo_strike.MIN_TRAVEL,
                       "strike_speed": tripo_strike.MIN_SPEED, "attack_score": MIN_ATTACK_SCORE},
            "clips": report, "attack_pick": pick_attack(report)}


def print_table(result: dict) -> None:
    print("raw: the clip as Tripo made it. route: after the neck lift, the shoulder ease and the clavicle lever")
    print(f"{'clip':<40}{'tear raw':>9}{'route':>7}{'swell raw':>10}{'route':>7}{'neck raw':>9}{'route':>7}{'raise raw':>10}{'route':>7}{'reach':>7}{'pelvis':>7}{'strike':>7}{'speed':>7}  verdict")
    for name, c in result["clips"].items():
        raw, after = c["raw"], c["route"]
        label = name if len(name) <= 39 else name[:36] + "..."
        print(f"{label:<40}{raw['tear']:>9.3f}{after['tear']:>7.3f}{raw['swell']:>10.3f}{after['swell']:>7.3f}{(raw['neck'] or 0):>9.2f}{(after['neck'] or 0):>7.2f}"
              f"{raw.get('raise_', 0):>10.3f}{after.get('raise_', 0):>7.3f}{raw['reach']:>7.3f}{raw['pelvis_travel']:>7.3f}{after.get('strike_travel', 0):>7.3f}{after.get('strike_speed', 0):>7.2f}  {c['verdict']}"
              + (f"  ({'; '.join(c['reasons'])})" if c["reasons"] else ""))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glb", type=Path, help="the rigged GLB with the candidate clips")
    parser.add_argument("mesh", type=Path, help="the unit's exported .mesh from an earlier run of the same body (its skeleton and route weights)")
    parser.add_argument("--clips", nargs="*", help="only clips whose name starts with one of these")
    parser.add_argument("--hand", default="RightHand", help="the holding hand, for the raise")
    parser.add_argument("--idle", default="idle", help="the GLB clip whose first frame is the stance the shoulder ease turns toward")
    parser.add_argument("--attack", nargs="*", help="the attack candidates (clips whose name starts with one of these): they must also strike, and the pick is made among them")
    parser.add_argument("--unarmed", action="store_true", help="the unit holds no weapon: the striking hand is the faster one")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    result = check(args.glb, args.mesh, args.clips, args.hand, args.idle, args.attack, args.unarmed)
    print_table(result)
    if args.attack:
        print(f"attack pick: {result['attack_pick'] or 'none passes'}")
    if args.json:
        args.json.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
