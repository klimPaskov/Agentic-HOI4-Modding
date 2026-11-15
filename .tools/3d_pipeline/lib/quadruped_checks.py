"""The Tripo checks for a quadruped unit (the kit's quadruped rig: Root, Pelvis, Spine, Chest, Neck, Head, four legs, optional tail).

`tripo/tripo_checks.py` runs these instead of its humanoid checks when the mesh has the quadruped rig's leg bones. Each reads the
exported `.mesh` and `.anim` files, as the game loads them. Heights are shares of the unit's rest height.

- TRIPO-LOOP-POP: as for a humanoid, the last frame of an idle, move, attack, defend or retreat clip is more than 8 degrees from its first
  at some joint (`lib/tripo_pose.loop_seam`).
- TRIPO-FOOT-BELOW-GROUND: a hoof (the vertices the four `*_Hoof` bones carry most) sinks more than 0.1% of the height under the ground in
  a clip that is not a death.
- TRIPO-NOT-DOWN: a death must end lying down: in its last frame the body's lowest torso point (Pelvis, Spine and Chest vertices) is within
  `DOWN_BELLY_SHARE` of the height of the ground. A standing quadruped's belly is a fifth to a third of its height up.
- TRIPO-LOAD-BELOW-GROUND: a load the mount carries (`adapter/quadruped_load.py`: vertices bound wholly to the load bone) goes more than
  1% of the height under the ground in some frame, the weapon rule (TRIPO-WEAPON-BELOW-GROUND) applied to a tower that would sink.
- TRIPO-LOAD-STRETCH: more than 0.5% of the load's edges stretch or squash in some frame: a rigid tower bends (vanilla clothing's worst is
  2%, a plank never bends).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from . import pdx_deform, tripo_pose
from . import tripo_checks as T


def _finding(rule: str, subject: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": subject, "message": message, **numbers}

HOOF_SUFFIX = "_Hoof"
LEG_PREFIXES = ("Front_", "Rear_")
TORSO = ("Pelvis", "Spine", "Chest")
LOAD_BONE = "Spine"
DOWN_BELLY_SHARE = 0.05
LOAD_SINK_LIMIT = 0.01
LOAD_STRETCH_LIMIT = 0.005


def is_quadruped(mesh: pdx_deform.SkinnedMesh) -> bool:
    return sum(name.endswith(HOOF_SUFFIX) and name.startswith(LEG_PREFIXES) for name in mesh.bones) == 4


def _dominant(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    names = np.array(mesh.bones + [""])
    return names[pdx_deform.dominant_bones(mesh)]


def load_mask(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The load's vertices: weight 1 on the load bone and above the body's mid height (the rule binds nothing else wholly to it)."""

    if LOAD_BONE not in mesh.bones:
        return np.zeros(len(mesh.positions), bool)
    bone = mesh.bones.index(LOAD_BONE)
    whole = ((mesh.joints == bone) & (mesh.weights > 0.999)).any(axis=1)
    floor = float(mesh.positions[:, 1].min())
    return whole & (mesh.positions[:, 1] > floor + 0.5 * mesh.height)


def _frames(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> np.ndarray:
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return np.stack([pdx_deform.skin(mesh, matrices[f]) for f in range(anim.frames)])


def quadruped_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    out: List[dict] = []
    numbers: dict = {}
    height = max(mesh.height, 1e-6)
    floor = float(mesh.positions[:, 1].min())
    dominant = _dominant(mesh)
    hooves = np.array([name.endswith(HOOF_SUFFIX) for name in dominant])
    torso = np.isin(dominant, TORSO)
    load = load_mask(mesh)
    edges = pdx_deform.mesh_edges(mesh)
    numbers["load_vertices"] = int(load.sum())
    for clip, anim in anims.items():
        role = tripo_pose.role_of(clip)
        posed = _frames(mesh, anim)
        row: dict = {}
        if role in tripo_pose.LOOP_ROLES:
            turn, joint = tripo_pose.loop_seam(mesh, anim)
            row["loop_seam_degrees"] = round(turn, 1)
            if turn > tripo_pose.LOOP_POSE_LIMIT_DEGREES:
                out.append(_finding("TRIPO-LOOP-POP", clip, f"the last frame is {turn:.0f} degrees from the first at {joint} (limit {tripo_pose.LOOP_POSE_LIMIT_DEGREES:g}): the looped {role} pops back to its start", degrees=round(turn, 1)))
        if role != "death" and hooves.any():
            lowest = (posed[:, hooves, 1].min(axis=1) - floor) / height
            row["lowest_hoof_share"] = round(float(lowest.min()), 4)
            if lowest.min() < -tripo_pose.FOOT_SINK_LIMIT:
                frame = int(np.argmin(lowest))
                out.append(_finding("TRIPO-FOOT-BELOW-GROUND", clip, f"a hoof sinks {-lowest.min():.2%} of the height under the ground in frame {frame} (limit {tripo_pose.FOOT_SINK_LIMIT:.1%})", share=round(float(-lowest.min()), 4), frame=frame))
        if role == "death" and torso.any():
            belly = float(posed[-1][torso, 1].min() - floor) / height
            row["final_torso_lowest_share"] = round(belly, 4)
            if belly > DOWN_BELLY_SHARE:
                out.append(_finding("TRIPO-NOT-DOWN", clip, f"the body's lowest torso point ends {belly:.0%} of the height above the ground (limit {DOWN_BELLY_SHARE:.0%}): it does not end lying down", share=round(belly, 4)))
        if load.any():
            sink = (posed[:, load, 1].min(axis=1) - floor) / height
            row["load_lowest_share"] = round(float(sink.min()), 4)
            if sink.min() < -LOAD_SINK_LIMIT:
                frame = int(np.argmin(sink))
                out.append(_finding("TRIPO-LOAD-BELOW-GROUND", clip, f"the load goes {-sink.min():.1%} of the height under the ground in frame {frame} (limit {LOAD_SINK_LIMIT:.0%})", share=round(float(-sink.min()), 4), frame=frame))
            share, frame = T.region_stretch_share(mesh.positions, posed, edges, load, mesh.height)
            row["load_stretch_share"] = round(share, 4)
            if share > LOAD_STRETCH_LIMIT:
                out.append(_finding("TRIPO-LOAD-STRETCH", clip, f"{share:.1%} of the load's edges stretch or squash in frame {frame} (limit {LOAD_STRETCH_LIMIT:.1%}): the load bends", share=round(share, 4)))
        numbers[clip] = row
    return out, numbers
