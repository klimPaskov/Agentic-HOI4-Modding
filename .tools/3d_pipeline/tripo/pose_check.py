"""Measure a rigged Tripo GLB's candidate clips on a unit's exported skin: the shoulder swell, the neck, the hand's raise and reach.

    py -3.13 .tools/3d_pipeline/tripo/pose_check.py <rigged.glb> <unit.mesh> [--clips NAME ...] [--attack NAME ...] [--gait NAME ...] [--unarmed] [--hand RightHand] [--json out.json]

The clip pick (docs/3d-units.md, "Pick the clips by measurement") needs to know, before a clip is bought into the route, whether its pose
swells the shoulders (TRIPO-SHOULDER-SWELL, `lib/tripo_shoulder.py`) or sinks the head (TRIPO-NECK-SUNK, `lib/tripo_neck.py`) on the skin the
route makes. Those depend on the route's weights, which only an earlier run of the same body has. This tool reads that run's exported `.mesh`
(the skeleton and the fitted weights) and each clip of the rigged GLB, and plays the clip on the mesh:

1. The GLB's rest joints are matched to the mesh's by name (Tripo's Mixamo names or its newer rig's to the kit's, through `lib/tripo_rig.py`), and
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

With `--map` the outline rules of `lib/map_outline.py` are read too, after the route's rules: the idle's posture (its body outline's height over
the rest pose's, TRIPO-MAP-POSTURE), each clip's hand spread (TRIPO-MAP-SPREAD) and an attack's strike outside the body's outline
(TRIPO-MAP-REACH), and an attack that fails either is not picked.
With `--map` each clip's map-size reading against the idle (`lib/map_read.read_pixels`, the pixels of the idle's silhouette it changes at game
size in its 90th percentile frame, TRIPO-MAP-READ) is given as made and after the rules, and an attack under the limit is not picked. `--trim
CLIP=FRAMES` cuts a clip as the job's `tripo.trim` would (frames at 24 a second), for the idle too. On zombie_w's skin (2026-11-18, the idle
the zombie text clip cut at 44): the recoil defend 106 px as made and 106 after the rules (the exported clip 104, so the route did not weaken
it), box_01 166 (exported 192), front_kick_01 517, the swipe 190, the lurch 181, `hit_to_stomach` 118, the staggering hit 426.

A verdict per clip says whether the swell, the tear and the neck pass their limits after the rules (`route`), and as Tripo made the clip (`raw`).
A clip named with `--attack` must also strike (TRIPO-ATTACK-NO-STRIKE's limits), and `attack_pick` names the attack by the pick rule: of the
attack candidates that pass, the largest raise or reach plus the pelvis's travel after the rules, at least `MIN_ATTACK_SCORE`. A lunge that
holds the arms out reaches as far as a blow, so the reach alone picked the zombie's static lunge three times (zombie_i, zombie_k, zombie_o).
A clip named with `--gait` (a candidate for the move or the retreat) is judged as a looped gait (`lib/tripo_loop.py`, TRIPO-LOOP-STANDS): the
loop window the route would cut (frames of this tool's 30 a second), the share of the whole clip's steps that stand, and on the window the
slowest stride. It fails when the clip never strides (no window) or the window stands. The seam is not judged here: the route closes it
into the frames before the window. `flee_01` on the zombie: 21% of the whole clip's steps stand, and the window is one stride (frames 31 to 53).
The weights stay the earlier run's, which the route fits again to the new clips, and the grip stage and the clearance are not run, so the
numbers estimate the route's result. Checked on the round 4 ogre: the clips the run ogre_k exported measured as here within 0.003 (the
defend `hit_to_body_01` 0.161, the chop's raise 0.267). Plain numpy, no Blender.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import clip_check
from lib import map_outline, map_read, pdx_deform, pdx_motion, tripo_cloak_bend, tripo_loop, tripo_neck, tripo_pose, tripo_shoulder, tripo_strike, tripo_trim

FRAME_RATE = 30.0
MIN_ATTACK_SCORE = 0.2  # docs/3d-units.md, the attack's raise or reach plus the pelvis's travel
def glb_name(kit: str) -> str:
    """A kit bone's name in Tripo's Mixamo rig (`Spine01` is `mixamorig:Spine1`)."""

    from lib import tripo_rig

    canonical = {v: k for k, v in tripo_rig.KIT_FROM_CANONICAL.items()}.get(kit, kit)
    return "mixamorig:" + canonical


def glb_names(rig: clip_check.Rig) -> dict:
    """{kit bone: the GLB joint index} through lib/tripo_rig.py (Mixamo's rig and the newer Tripo rig)."""

    from lib import tripo_rig

    names = tripo_rig.RigNames(rig.joint_names)
    return {kit: k for k, name in enumerate(rig.joint_names) if (kit := names.kit(name)) is not None}


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
        joints = glb_names(rig)
        self.pairs = [(b, joints[name]) for b, name in enumerate(mesh.bones) if name in joints]
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


def measure(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, hand: str = "RightHand", attack: bool = False, unarmed: bool = False,
            lunge: bool = False) -> dict:
    """The clip's numbers on the mesh (see the module text). An `attack` candidate must also strike (`lib/tripo_strike.py`): the holding
    `hand`, or for an `unarmed` unit the faster hand, travels and moves fast enough against the chest (against the ground for an unarmed
    `lunge` whose step the job keeps)."""

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
    strike = tripo_strike.strike_numbers(joints, mesh.bones, height, float(anim.fps or FRAME_RATE), "" if unarmed else hand, lunge and unarmed)
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


def gait(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> Optional[dict]:
    """A move or retreat candidate as a looped gait (`lib/tripo_loop.py`): the whole clip's standing share, the loop window the route would
    cut and that window's numbers, with the reasons it would fail TRIPO-LOOP-STANDS. None for a body without two legs."""

    legs = pdx_motion.find_legs(mesh)
    if not legs.biped or legs.pelvis < 0:
        return None
    joints = pdx_motion.posed_joints(mesh, anim)
    feet, fps = (legs.legs[0].ankle, legs.legs[1].ankle), float(anim.fps or FRAME_RATE)
    whole = tripo_loop.gait_numbers(joints, feet, legs.pelvis, mesh.height, fps)
    out = {"whole_still_share": whole["still_share"], "window": None, "reasons": []}
    window = tripo_loop.loop_window(joints, feet, legs.pelvis, mesh.height, fps)
    if window is None:
        out["reasons"].append("no loop window: the clip never strides")
        return out
    cut = tripo_loop.gait_numbers(joints[window["first"] : window["last"] + 1], feet, legs.pelvis, mesh.height, fps)
    out.update(window=[window["first"], window["last"]], whole=window["whole"], cost=window["cost"], slowest=cut["slowest"],
               still_share=cut["still_share"])
    if cut["still_steps"]:
        out["reasons"].append("loop window: " + tripo_loop.stands_reason(cut, "clip"))
    return out


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
        if after.get("map_pixels", math.inf) < map_read.MIN_HUMANOID_READ_PIXELS["attack"]:
            continue  # with --map: an attack that reads as the idle from the map camera (TRIPO-MAP-READ) is not picked
        if after.get("map_spread", 0.0) >= map_outline.SPREAD_LIMIT or after.get("map_reach", math.inf) < map_outline.MIN_REACH_PIXELS:
            continue  # with --map: an attack that reads as a T-pose, or whose reach foreshortens into the body (lib/map_outline.py), is not picked
        score = max(after.get("raise_", 0.0), after["reach"]) + after["pelvis_travel"]
        if score >= best_score:
            best, best_score = name, score
    return best


def check(glb: Path, mesh_path: Path, clips: Optional[Sequence[str]] = None, hand: str = "RightHand", idle_clip: str = "idle",
          attacks: Optional[Sequence[str]] = None, unarmed: bool = False, gaits: Optional[Sequence[str]] = None,
          trims: Optional[Dict[str, int]] = None, map_size: bool = False, lunge: bool = False) -> dict:
    doc, _binary = clip_check.load_glb(glb)
    body = next(node.get("name") for node in doc["nodes"] if "mesh" in node and "skin" in node)
    rig = clip_check.Rig(glb, body, None)
    mesh = pdx_deform.load_mesh(mesh_path)
    transfer = Transfer(rig, mesh)
    trims = trims or {}

    def cut(name: str, end: float) -> float:
        # a role's trim, as the job's `tripo.trim` gives it: frames of the clip imported at 24 a second
        frames = next((count for prefix, count in trims.items() if name.startswith(prefix)), None)
        return min(end, frames / tripo_trim.FPS) if frames else end

    every = list(rig.clips())
    idle_name = next((name for name, _tracks, _end in every if name == idle_clip), None) or next((name for name, _t, _e in every if name.startswith(idle_clip)), None)
    idle = next((transfer.animation(tracks, cut(name, end)) for name, tracks, end in every if name == idle_name), None)
    camera = map_read.MapCamera(mesh) if map_size and idle is not None else None
    idle_map = camera.frames(idle) if camera is not None else None
    # the outline rules (lib/map_outline.py): the idle's posture, each clip's hand spread and an attack's reach outside the body's outline
    outline = map_outline.OutlineCamera(mesh) if camera is not None and map_outline.is_humanoid(mesh) else None
    posture = map_outline.posture_reading(outline, idle) if outline is not None else None
    armed = outline is not None and not unarmed and bool(outline.parts["weapon"].any())
    report = {}
    for name, tracks, end in every:
        if clips and not any(name.startswith(c) for c in clips):
            continue
        anim = transfer.animation(tracks, cut(name, end))
        attack = is_attack(name, attacks)
        raw = measure(mesh, anim, hand, attack, unarmed, lunge and attack)
        routed = route(mesh, anim, idle)
        after = measure(mesh, routed, hand, attack, unarmed, lunge and attack)
        if camera is not None:
            # the map-size reading against the idle (lib/map_read.read_pixels), as Tripo made the clip and after the route's pose rules
            raw["map_pixels"] = map_read.read_pixels(camera.frames(anim), idle_map)
            after["map_pixels"] = map_read.read_pixels(camera.frames(routed), idle_map)
        if outline is not None:
            spread = map_outline.spread_reading(outline, routed, posture["idle_height_px"])
            if spread is not None:
                after["map_spread"] = spread["p90"]
            if attack:
                after["map_reach"] = map_outline.reach_reading(outline, routed, armed).get("pixels", 0)
        report[name] = {"raw": raw, "route": after, "verdict": after["verdict"], "reasons": list(after["reasons"]), "attack": attack}
        if is_attack(name, gaits):
            found = gait(mesh, anim)
            if found is not None:
                report[name]["gait"] = found
                report[name]["reasons"] += found["reasons"]
                report[name]["verdict"] = "fail" if report[name]["reasons"] else "pass"
    return {"glb": str(glb), "mesh": str(mesh_path), "hand": hand, "unarmed": unarmed, "scale": round(transfer.scale, 4), "idle": idle_name, "trims": trims,
            "limits": {"swell": tripo_shoulder.SWELL_LIMIT, "tear": tripo_shoulder.GIRDLE_LIMIT, "neck": tripo_neck.NECK_LIMIT, "strike_travel": tripo_strike.MIN_TRAVEL,
                       "strike_speed": tripo_strike.MIN_SPEED, "attack_score": MIN_ATTACK_SCORE,
                       "stride_speed": tripo_loop.MIN_STRIDE_SPEED},
            "clips": report, "attack_pick": pick_attack(report), "idle_posture": posture}


def print_table(result: dict) -> None:
    print("raw: the clip as Tripo made it. route: after the neck lift, the shoulder ease and the clavicle lever")
    print(f"{'clip':<40}{'tear raw':>9}{'route':>7}{'swell raw':>10}{'route':>7}{'neck raw':>9}{'route':>7}{'raise raw':>10}{'route':>7}{'reach':>7}{'pelvis':>7}{'strike':>7}{'speed':>7}  verdict")
    for name, c in result["clips"].items():
        raw, after = c["raw"], c["route"]
        label = name if len(name) <= 39 else name[:36] + "..."
        print(f"{label:<40}{raw['tear']:>9.3f}{after['tear']:>7.3f}{raw['swell']:>10.3f}{after['swell']:>7.3f}{(raw['neck'] or 0):>9.2f}{(after['neck'] or 0):>7.2f}"
              f"{raw.get('raise_', 0):>10.3f}{after.get('raise_', 0):>7.3f}{raw['reach']:>7.3f}{raw['pelvis_travel']:>7.3f}{after.get('strike_travel', 0):>7.3f}{after.get('strike_speed', 0):>7.2f}  {c['verdict']}"
              + (f"  ({'; '.join(c['reasons'])})" if c["reasons"] else ""))
    for name, c in result["clips"].items():
        if "map_pixels" in c["route"]:
            print(f"map {name[:36]:<36}: {c['raw']['map_pixels']:>6.0f} px as made, {c['route']['map_pixels']:>6.0f} px after the rules against the idle at game size"
                  f" (attack at least {map_read.MIN_HUMANOID_READ_PIXELS['attack']:.0f}, defend {map_read.MIN_HUMANOID_READ_PIXELS['defend']:.0f})")
    if result.get("idle_posture"):
        ratio = result["idle_posture"]["ratio"]
        print(f"idle posture: the body outline stands {ratio:.2f} of the rest pose's height on the map camera "
              f"({'hunched' if ratio <= map_outline.POSTURE_LIMIT else 'upright'}: hunched is {map_outline.POSTURE_LIMIT:.2f} or less, TRIPO-MAP-POSTURE)")
    for name, c in result["clips"].items():
        after = c["route"]
        if "map_spread" in after or "map_reach" in after:
            spread = after.get("map_spread")
            line = f"outline {name[:36]:<36}: hand spread {spread:.2f}" if spread is not None else f"outline {name[:36]:<36}: hand spread -"
            line += f" (a T-pose at {map_outline.SPREAD_LIMIT:.2f} or more)"
            if "map_reach" in after:
                line += f", strike {after['map_reach']} px outside the body (at least {map_outline.MIN_REACH_PIXELS})"
            print(line)
    for name, c in result["clips"].items():
        found = c.get("gait")
        if found and found["window"]:
            print(f"gait {name[:36]}: the whole clip stands in {100 * found['whole_still_share']:.0f}% of its steps; loop window frames {found['window'][0]} to "
                  f"{found['window'][1]}" + (" (the whole clip)" if found["whole"] else "") + f", slowest stride {found['slowest']:.2f}")
        elif found:
            print(f"gait {name[:36]}: the whole clip stands in {100 * found['whole_still_share']:.0f}% of its steps and has no loop window")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glb", type=Path, help="the rigged GLB with the candidate clips")
    parser.add_argument("mesh", type=Path, help="the unit's exported .mesh from an earlier run of the same body (its skeleton and route weights)")
    parser.add_argument("--clips", nargs="*", help="only clips whose name starts with one of these")
    parser.add_argument("--hand", default="RightHand", help="the holding hand, for the raise")
    parser.add_argument("--idle", default="idle", help="the GLB clip (its name, or its first words) whose first frame is the stance the shoulder ease turns toward, and the idle of the map reading")
    parser.add_argument("--attack", nargs="*", help="the attack candidates (clips whose name starts with one of these): they must also strike, and the pick is made among them")
    parser.add_argument("--gait", nargs="*", help="the move and retreat candidates (clips whose name starts with one of these): judged as a looped gait, with the loop window the route would cut")
    parser.add_argument("--unarmed", action="store_true", help="the unit holds no weapon: the striking hand is the faster one")
    parser.add_argument("--trim", nargs="*", default=[], metavar="CLIP=FRAMES", help="cut a clip (named by its first words) after FRAMES frames at 24 a second, as the job's tripo.trim")
    parser.add_argument("--map", action="store_true", help="also measure each clip's map-size reading against the idle (lib/map_read.read_pixels, TRIPO-MAP-READ) and its outline (lib/map_outline.py: the idle's posture, the hand spread, an attack's strike outside the body)")
    parser.add_argument("--lunge", action="store_true", help="the job keeps the attack's lunge step (tripo.lunge, tripo/lunge_clip.py): an unarmed attack's hands are measured against the ground")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    trims = {pair.rsplit("=", 1)[0]: int(pair.rsplit("=", 1)[1]) for pair in args.trim}
    result = check(args.glb, args.mesh, args.clips, args.hand, args.idle, args.attack, args.unarmed, args.gait, trims, args.map, args.lunge)
    print_table(result)
    if args.attack:
        print(f"attack pick: {result['attack_pick'] or 'none passes'}")
    if args.json:
        args.json.write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
