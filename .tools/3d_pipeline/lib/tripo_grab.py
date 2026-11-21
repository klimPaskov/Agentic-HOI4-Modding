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

# Directions in the frame (the unit's front, up, out toward the arm's side). A two-handed grab: the upper arm forward and a little out, the
# forearm forward and in, so the hands meet in front at shoulder height.
UPPER_ARM = (0.95, 0.05, 0.2)
FOREARM = (0.9, 0.08, -0.4)
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


def grab_attack(mesh_path: Path, anim_path: Path, front: np.ndarray) -> Dict[str, object]:
    """Pose the exported attack's arms as a two-handed grab (see the module text), in place. `front` is the unit's facing."""

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
    channels = {name: {key: value.copy() for key, value in channel.items()} for name, channel in anim.channels.items()}
    for frame in range(anim.frames):
        w = float(weight[frame])
        if w <= 0.0:
            continue
        for side, (upper, fore, hand) in ARMS.items():
            axes = np.stack([front, up, outward[side]], axis=1)
            for bone, child, target in ((upper, fore, UPPER_ARM), (fore, hand, FOREARM)):
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
    return {"changed": True, "frames": int((weight > 0).sum()), "joints": joints, "peak_weight": round(float(weight.max()), 3)}
