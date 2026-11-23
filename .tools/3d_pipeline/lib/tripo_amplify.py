"""A clip's motion amplified for the map camera (`"amplify": {role: factor}` in a job's `tripo` block). No Blender.

At game size a humanoid is about 60 pixels tall. Two fresh reviews of the Chaos Redux zombie (runs k and m, 2026-11-22 and 23) read its
made stumble defend as a sway close to the idle, and the pounce's long return as the idle, although each clip moved: Tripo's text-to-motion
clips often move too little to read at that size. So the route can scale a clip's motion away from its own first pose:

1. Each keyed joint's rotation per frame is the first frame's rotation times the turn since then raised to the factor (a factor of 1.5
   turns every joint half as far again from where the clip began, and the clip still starts on its own first pose).
2. The hips' travel since the first frame is scaled the same way, so a stagger steps further. Then each frame is lifted by however far
   its lowest point now goes below where it was in the original clip (`regrounded`), so a wider leg swing does not put a foot in the
   ground.
3. The factor is the largest, from the job's factor down in steps of `STEP`, at which the clip stays inside the kit's vanilla limits for
   the unit's group (`limits`: the stretched and squashed edge shares and the worst stretch of `check_unit_files`, from
   `config/deformation_calibration.json`), no point sinks past TRIPO-FOOT-BELOW-GROUND's 0.1 % of the height and no shoulder swells past
   TRIPO-SHOULDER-SWELL's limit, or no worse than the clip already was where it was outside them. At a factor of 1 nothing changes, and
   the record says which limit held it. Run on the zombie's defend at 1.8 without the foot and shoulder bounds, a foot sank 2.5 % and the
   attack's shoulder swelled to 10.5 %.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np

from . import pdx_deform, tripo_pose
from .pdx_binary import read

STEP = 0.1
FOOT_LIMIT = 0.001  # of the height: TRIPO-FOOT-BELOW-GROUND's limit, the deepest any point may sink unless the clip already did


def _quat_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Hamilton product of quaternions in (x, y, z, w) order, row by row."""

    ax, ay, az, aw = np.moveaxis(a, -1, 0)
    bx, by, bz, bw = np.moveaxis(b, -1, 0)
    return np.stack([aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw,
                     aw * bw - ax * bx - ay * by - az * bz], axis=-1)


def _conjugate(q: np.ndarray) -> np.ndarray:
    return q * np.array([-1.0, -1.0, -1.0, 1.0])


def _power(q: np.ndarray, factor: float) -> np.ndarray:
    """Unit quaternions (x, y, z, w) raised to `factor`: the same axis, the angle times the factor (the short way)."""

    q = np.where(q[..., 3:4] < 0, -q, q)
    w = np.clip(q[..., 3], -1.0, 1.0)
    half = np.arccos(w)
    s = np.sin(half)
    axis = np.where(s[..., None] > 1e-9, q[..., :3] / np.maximum(s, 1e-9)[..., None], 0.0)
    scaled = half * factor
    return np.concatenate([axis * np.sin(scaled)[..., None], np.cos(scaled)[..., None]], axis=-1)


def amplified(anim: pdx_deform.Animation, factor: float, joints, travel_joint: str = "Hips") -> pdx_deform.Animation:
    """`anim` with each joint's turn since the first frame raised to `factor`, and `travel_joint`'s translation since the first frame
    scaled by it."""

    channels = {name: {key: value.copy() for key, value in channel.items()} for name, channel in anim.channels.items()}
    for name in joints:
        q = channels[name]["q"]
        first = np.repeat(q[:1], len(q), axis=0)
        since = _quat_mul(_conjugate(first), q)
        channels[name]["q"] = _quat_mul(first, _power(since, factor))
    if travel_joint in channels:
        t = channels[travel_joint]["t"]
        channels[travel_joint]["t"] = t[:1] + (t - t[:1]) * factor
    return pdx_deform.Animation(anim.fps, anim.frames, channels)


def lowest_per_frame(mesh, anim) -> np.ndarray:
    """(frames,) the height of the clip's lowest vertex in each frame."""

    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return np.array([float(pdx_deform.skin(mesh, matrices[f])[:, 1].min()) for f in range(matrices.shape[0])])


def regrounded(mesh, anim: pdx_deform.Animation, lowest_before: np.ndarray, joint: str = "Hips") -> pdx_deform.Animation:
    """`anim` with `joint` lifted in each frame by however far the clip's lowest point now goes below where it was in that frame of the
    original (`lowest_before`): an amplified leg swing or crouch reaches lower, and the feet must not go into the ground."""

    if joint not in anim.channels:
        return anim
    lift = np.maximum(0.0, np.asarray(lowest_before) - lowest_per_frame(mesh, anim))
    channels = {name: {key: value.copy() for key, value in channel.items()} for name, channel in anim.channels.items()}
    channels[joint]["t"][:, 1] += lift
    return pdx_deform.Animation(anim.fps, anim.frames, channels)


def _within(mesh, report, base, limits) -> str:
    """Empty when `report` (an amplified clip) keeps to the limits (or to `base`, the clip's own report, where that is outside them),
    else the limit it breaks."""

    edges = max(len(pdx_deform.mesh_edges(mesh)), 1)
    limits = limits or {}
    stretched = max(limits.get("stretched_share", 0.0), base.stretched_edges / edges)
    squashed = max(limits.get("squashed_share", 0.0), base.squashed_edges / edges)
    worst = max(limits.get("worst_stretch_share", 0.0), base.worst_stretch_share)
    sink = max(FOOT_LIMIT, -base.lowest)
    if report.stretched_edges / edges > stretched or report.squashed_edges / edges > squashed or report.worst_stretch_share > worst:
        return "stretch"
    if -report.lowest > sink:
        return "ground"
    return ""


def _swells(swelling, anim, base_worst: float) -> bool:
    """True when the amplified clip swells a shoulder past TRIPO-SHOULDER-SWELL's limit (or past the clip's own worst, if that was over)."""

    if swelling is None:
        return False
    from . import tripo_shoulder

    return float(swelling.per_frame(anim).max()) > max(tripo_shoulder.SWELL_LIMIT, base_worst)


def amplify_clip(mesh_path: Path, anim_path: Path, factor: float, limits=None) -> Dict[str, object]:
    """Amplify the clip at `anim_path` in place by the largest factor up to `factor` that deforms it no worse and sinks it no deeper
    (see the module text). Returns what was done."""

    mesh = pdx_deform.load_mesh(mesh_path)
    anim = pdx_deform.load_anim(anim_path)
    info = read(anim_path).child("info")
    keyed_q = [joint.name for joint in info.children if "q" in str((joint.properties.get("sa") or [""])[0])]
    keyed_t = [joint.name for joint in info.children if "t" in str((joint.properties.get("sa") or [""])[0])]
    base = pdx_deform.deformation_report(mesh, anim)
    from . import tripo_shoulder

    rig = tripo_shoulder.shoulder_rig(mesh)
    swelling = tripo_shoulder.Swelling(mesh, rig) if rig is not None else None
    base_swell = float(swelling.per_frame(anim).max()) if swelling is not None else 0.0
    hips = "Hips" if "Hips" in keyed_t else ""
    lowest_before = lowest_per_frame(mesh, anim) if hips else None
    held = "the clip's own deformation and ground"
    chosen, trial_report = 1.0, base
    k = round(float(factor), 2)
    while k > 1.0 + 1e-9:
        trial = amplified(anim, k, keyed_q, hips)
        if hips:
            trial = regrounded(mesh, trial, lowest_before, hips)
        report = pdx_deform.deformation_report(mesh, trial)
        broken = _within(mesh, report, base, limits) or ("shoulder swell" if _swells(swelling, trial, base_swell) else "")
        if broken:
            held = broken
        else:
            chosen, trial_report, result = k, report, trial
            break
        k = round(k - STEP, 2)
    if chosen <= 1.0:
        return {"changed": False, "factor_asked": float(factor), "factor": 1.0, "held_by": held}
    data = bytearray(Path(anim_path).read_bytes())
    tripo_pose._write_rotations(data, keyed_q, keyed_q, result, np.ones(anim.frames))
    if "Hips" in keyed_t:
        tripo_pose._write_translations(data, keyed_t, ["Hips"], result, np.ones(anim.frames))
    Path(anim_path).write_bytes(bytes(data))
    return {"changed": True, "factor_asked": float(factor), "factor": chosen, "held_by": held if chosen < factor else None,
            "stretched_edges": [base.stretched_edges, trial_report.stretched_edges],
            "lowest": [round(base.lowest, 4), round(trial_report.lowest, 4)]}
