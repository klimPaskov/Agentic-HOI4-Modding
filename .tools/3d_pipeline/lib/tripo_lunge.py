"""Put a kept lunge step back into the exported attack (a job's `tripo.lunge`, tripo/lunge_clip.py). No Blender.

The Blender stage retargets every clip in place: its root takes only the vertical part of the source's motion (`in_place_xy_preserve_z` in
the adapter), which every other role needs. Run zombie_b (2026-11-21) showed what that does to a lunge: the provider file of its attack
stepped 0.59 hip heights, the exported `.anim` 0, and the attack read 270 px on the game camera and struck 0.25 at 1.20 against the
ground, where the same clip with its step had read 587 px and 0.47 at 1.41 by `tripo/pose_check.py`.

So the route restores the step on the staged attack, after the export:

1. The step is read from the role's provider file (`provider/downloads/animation_attack_provider.glb`, written by the intake from the
   rigged GLB that `lunge_clip.py` made): the hips' sideways and forward travel from the first key, in hip heights, along its own final
   direction, signed forward when it goes the way the rig faces (glTF +Z).
2. Each exported frame takes the step at its own time. Frames past the provider clip's end (the settle the route appends) hold its last step.
3. Over the last `RETURN_SHARE` of the clip the step eases back to zero (smoothstep), so the looped attack starts and ends where the unit
   stands, as the in-place clip did.
4. The step is added to the `Hips` translation keys along the unit's front (`map_read.front_of`), scaled by the mesh's own hip height (the
   Hips joint's rest height above the lowest vertex). Only the Hips translation samples change.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np

from . import glb_root, map_read, pdx_deform, tripo_pose
from .pdx_binary import read

RETURN_SHARE = 0.3


def provider_step(glb: Path) -> Dict[str, np.ndarray]:
    """{"times": (K,) seconds, "forward": (K,) the hips' signed step in hip heights} of the GLB's first clip that keys the hips' translation."""

    doc, blob = glb_root._read(glb)
    names = [node.get("name", "") for node in doc.get("nodes", [])]
    hips = next((i for i, name in enumerate(names) if name.split(":")[-1] == "Hips"), None)
    if hips is None:
        raise ValueError(f"{glb.name}: no Hips joint")
    rest = np.asarray(doc["nodes"][hips].get("translation", [0.0, 0.0, 0.0]), float)
    scale = max(float(np.linalg.norm(rest)), 1e-9)
    axis = rest / scale
    for animation in doc.get("animations", []):
        for channel in animation.get("channels", []):
            target = channel.get("target", {})
            if target.get("node") == hips and target.get("path") == "translation":
                sampler = animation["samplers"][channel["sampler"]]
                times = np.asarray(glb_root._accessor(doc, blob, sampler["input"]), float).ravel()
                keys = np.asarray(glb_root._accessor(doc, blob, sampler["output"]), float)
                step = keys - keys[0]
                across = (step - np.outer(step @ axis, axis)) / scale
                last = across[np.argmax(np.linalg.norm(across, axis=1))]
                if float(np.linalg.norm(last)) < 1e-9:
                    return {"times": times, "forward": np.zeros(len(times))}
                direction = last / np.linalg.norm(last)
                sign = 1.0 if float(direction[2]) >= 0.0 else -1.0
                return {"times": times, "forward": sign * (across @ direction)}
    raise ValueError(f"{glb.name}: no clip keys the hips' translation")


def step_per_frame(step: Dict[str, np.ndarray], frames: int, fps: float, return_share: float = RETURN_SHARE) -> np.ndarray:
    """The step in hip heights for each exported frame, eased back to zero over the clip's last `return_share`."""

    t = np.arange(frames) / max(fps, 1e-6)
    out = np.interp(t, step["times"], step["forward"], left=float(step["forward"][0]), right=float(step["forward"][-1]))
    start = int(round(frames * (1.0 - return_share)))
    if frames - start >= 2:
        share = np.clip((np.arange(frames) - start) / (frames - 1 - start), 0.0, 1.0)
        out = out * (1.0 - share * share * (3.0 - 2.0 * share))
    out[-1] = 0.0
    return out


def restore_step(mesh_path: Path, anim_path: Path, provider_glb: Path) -> Dict[str, object]:
    """Add the provider clip's kept step to the staged attack's Hips translation, in place (see the module text)."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    if "Hips" not in mesh.bones or "Hips" not in anim.channels or "t" not in anim.channels["Hips"]:
        return {"changed": False, "note": "the attack keys no Hips translation"}
    info = read(anim_path).child("info")
    t_keyed = [joint.name for joint in info.children if "t" in str((joint.properties.get("sa") or [""])[0])]
    if "Hips" not in t_keyed:
        return {"changed": False, "note": "the attack's file stores no Hips translation"}
    step = step_per_frame(provider_step(provider_glb), anim.frames, float(anim.fps or 30.0))
    index = mesh.bones.index("Hips")
    bind = np.linalg.inv(mesh.inverse_bind)
    hip_height = float(bind[index][1, 3] - mesh.positions[:, 1].min())
    front = np.asarray(map_read.front_of(mesh), float)
    front[1] = 0.0
    front /= max(float(np.linalg.norm(front)), 1e-9)
    rotations, _positions = tripo_pose._world_rotations(mesh, anim)
    parent = mesh.parents[index]
    channels = {name: dict(channel) for name, channel in anim.channels.items()}
    channels["Hips"]["t"] = anim.channels["Hips"]["t"].copy()
    for frame in range(anim.frames):
        shift = front * float(step[frame]) * hip_height
        channels["Hips"]["t"][frame] = anim.channels["Hips"]["t"][frame] + (rotations[frame, parent].T @ shift if parent >= 0 else shift)
    data = bytearray(Path(anim_path).read_bytes())
    tripo_pose._write_translations(data, t_keyed, ["Hips"], pdx_deform.Animation(anim.fps, anim.frames, channels), np.ones(anim.frames))
    Path(anim_path).write_bytes(bytes(data))
    return {"changed": True, "peak_hip_heights": round(float(np.abs(step).max()), 3), "frames": int(anim.frames), "return_share": RETURN_SHARE}
