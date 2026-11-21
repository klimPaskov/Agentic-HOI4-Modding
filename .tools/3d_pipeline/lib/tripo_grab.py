"""An unarmed lunge posed as a two-handed grab (`"attack_pose": "grab"` in a job's `tripo` block). No Blender.

Two fresh reviews of the D-94 zombie (run zombie_d, 2026-11-21) read its attack at game size as a flail, not a grab. Tripo's text-to-motion
lunge ("A hunched zombie suddenly lunges forward fast and violently") flings both arms out to the sides at the peak, the hands 0.52 of the
height apart and one raised beside the helmet, and its forward reach was 0.2 of the height. A grab reads when both hands go out in front
together. So the route poses the arms by rule on the exported attack, after the lunge step is restored and before the weights are fitted:

1. Each upper arm points forward, a little out and level (`UPPER_ARM`), and each forearm forward and in (`FOREARM`), in the frame of the
   unit's own front and the world's up, so the hands reach out at shoulder height and close toward each other however far the torso leans.
   Each bone takes the smallest turn onto its direction.
2. The pose is blended in by the lunge itself: the weight follows the hips' forward travel from the first frame, full from `FULL_SHARE` of
   the clip's farthest travel, and smoothstepped. A clip with no travel gets the ramp of `lib/tripo_guard.py` instead. So the hands reach
   while the body lunges and the clip still starts and ends on its own pose, and its loop does not pop.
3. The torso, hips and legs keep the clip's own motion.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np

from . import pdx_deform, tripo_guard, tripo_pose
from .pdx_binary import read

# Directions in the frame (the unit's front, up, out toward the arm's side). A two-handed grab: the upper arm forward and barely out, the
# forearm forward and a little in, so the hands close in front at shoulder height with the arms nearly straight. On zombie_e's files a
# forearm turned further in (0.9, 0.08, -0.4) kept the hands 0.16 of the height apart but reached 292 px against the idle on the map camera,
# under TRIPO-MAP-READ's 300. These reach 304 with the hands 0.18 apart.
UPPER_ARM = (0.97, 0.08, 0.1)
FOREARM = (0.97, 0.05, -0.18)
FULL_SHARE = 0.5
MIN_TRAVEL = 0.02  # of the height: less than this and the clip has no lunge to follow
ARMS = tripo_guard.ARMS


def lunge_weight(mesh, anim, front: np.ndarray) -> np.ndarray:
    """The grab's weight per frame: the hips' forward travel from frame 0 as a share of its peak, full from FULL_SHARE, smoothstepped."""

    _rotations, positions = tripo_pose._world_rotations(mesh, anim)
    hips = positions[:, mesh.bones.index("Hips")]
    travel = (hips - hips[0]) @ front
    height = float(mesh.positions[:, 1].max() - mesh.positions[:, 1].min())
    peak = float(travel.max())
    if peak < MIN_TRAVEL * height:
        return tripo_guard.ramp(anim.frames)
    weight = np.clip(travel / (FULL_SHARE * peak), 0.0, 1.0)
    weight[0] = weight[-1] = 0.0
    return weight * weight * (3.0 - 2.0 * weight)


# The wide grab (`"attack_pose": "grab_wide"`): from the map camera, which looks at the unit's front from above, a reach straight forward
# foreshortens into hands under the helmet (zombie_f, two fresh reviews, 2026-11-21). The wide grab changes the outline from the front: the
# claws start low and ready, swing out wide as the body lunges, and close together in front at the lunge's peak, then come back to ready.
READY = ((0.75, -0.45, 0.3), (0.9, 0.2, -0.2))  # (upper arm, forearm): claws low and forward, no forearm across the face
OPEN = ((0.45, 0.2, 0.85), (0.6, 0.25, 0.7))  # the arms swung out wide at shoulder height, the claws open
CLOSING_SHARE = 0.35  # of the approach (from the lunge's start to its peak): the last part, over which the arms close
START_SHARE = 0.15  # of the peak travel: where the lunge starts


def _blend(a, b, share: float):
    share = float(np.clip(share, 0.0, 1.0))
    share = share * share * (3.0 - 2.0 * share)
    return tuple(tuple((1.0 - share) * np.asarray(x, float) + share * np.asarray(y, float)) for x, y in zip(a, b))


def wide_plan(travel: np.ndarray) -> list:
    """The wide grab's (upper arm, forearm) directions for each frame, from the hips' forward travel (see the constants above)."""

    frames = len(travel)
    closed = (UPPER_ARM, FOREARM)
    peak = int(np.argmax(travel))
    top = float(travel[peak])
    start = int(np.argmax(travel >= START_SHARE * top)) if top > 0 else 0
    after = [f for f in range(peak, frames) if travel[f] < (1.0 - CLOSING_SHARE) * top]
    release = after[0] if after else frames - 1
    close_from = start + (1.0 - CLOSING_SHARE) * max(peak - start, 1)
    plan = []
    for f in range(frames):
        if f <= start:
            plan.append(READY)
        elif f < close_from:
            plan.append(_blend(READY, OPEN, (f - start) / max(close_from - start, 1.0)))
        elif f <= peak:
            plan.append(_blend(OPEN, closed, (f - close_from) / max(peak - close_from, 1.0)))
        elif f < release:
            plan.append(closed)
        else:
            plan.append(_blend(closed, READY, (f - release) / max(frames - 1 - release, 1.0)))
    return plan


def grab_attack(mesh_path: Path, anim_path: Path, front: np.ndarray, wide: bool = False) -> Dict[str, object]:
    """Pose the exported attack's arms as a two-handed grab (see the module text), in place. `front` is the unit's facing. `wide` poses
    the wide grab (`wide_plan`) at full weight in every frame instead of blending the straight reach in by the lunge."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    if any(name not in mesh.bones for name in ("Hips", "Spine02") + ARMS["Left"] + ARMS["Right"]):
        return {"changed": False, "note": "the rig lacks the kit's hips, chest or arm bones"}
    up = np.array([0.0, 1.0, 0.0])
    front = tripo_guard._unit(np.asarray(front, float) - (np.asarray(front, float) @ up) * up)
    lateral = tripo_guard._unit(np.cross(up, front))
    chest = mesh.bones.index("Spine02")
    rest = np.linalg.inv(mesh.inverse_bind)[:, :3, 3]
    outward = {}
    for side, (upper, _fore, _hand) in ARMS.items():
        away = rest[mesh.bones.index(upper)] - rest[chest]
        away = away - (away @ up) * up - (away @ front) * front
        outward[side] = tripo_guard._unit(away) if np.linalg.norm(away) > 1e-9 else (lateral if side == "Left" else -lateral)
    weight = lunge_weight(mesh, anim, front)
    plan = None
    if wide:
        _rotations, positions = tripo_pose._world_rotations(mesh, anim)
        hips = positions[:, mesh.bones.index("Hips")]
        plan = wide_plan((hips - hips[0]) @ front)
        weight = np.ones(anim.frames)
    channels = {name: {key: value.copy() for key, value in channel.items()} for name, channel in anim.channels.items()}
    for frame in range(anim.frames):
        w = float(weight[frame])
        if w <= 0.0:
            continue
        for side, (upper, fore, hand) in ARMS.items():
            axes = np.stack([front, up, outward[side]], axis=1)
            targets = plan[frame] if plan is not None else (UPPER_ARM, FOREARM)
            for bone, child, target in ((upper, fore, targets[0]), (fore, hand, targets[1])):
                rotations, positions = tripo_pose._world_rotations(mesh, pdx_deform.Animation(anim.fps, anim.frames, channels))
                i, c = mesh.bones.index(bone), mesh.bones.index(child)
                wanted = axes @ tripo_guard._unit(np.asarray(target, float))
                turn = tripo_guard._arc(positions[frame, c] - positions[frame, i], wanted, w)
                tripo_guard._set_world(channels, mesh, bone, frame, turn @ rotations[frame, i], rotations)
    data = bytearray(Path(anim_path).read_bytes())
    info = read(anim_path).child("info")
    keyed = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    joints = [name for name in ARMS["Left"][:2] + ARMS["Right"][:2] if name in keyed]
    tripo_pose._write_rotations(data, keyed, joints, pdx_deform.Animation(anim.fps, anim.frames, channels), (weight > 0).astype(float))
    Path(anim_path).write_bytes(bytes(data))
    return {"changed": True, "frames": int((weight > 0).sum()), "joints": joints, "peak_weight": round(float(weight.max()), 3), "wide": wide}
