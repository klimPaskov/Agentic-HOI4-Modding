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
- TRIPO-LOAD-SEAM: more than `LOAD_SEAM_LIMIT` of the edges of the skin the load blends into (every edge with an end that carries some but not
  all of its weight on the load bone) stretch or squash in some frame, by the kit's measure (UNIT-ANIM-STRETCH: 1.5 times and 0.5% of the
  height). The limit is vanilla clothing's worst share, 2.0%: that skin is tight to the body. UNIT-ANIM-STRETCH counts the whole mesh, so a
  band of torn skin at the load's front passes it: round 9 of the war elephant stretched 153 edges in its death, 0.5% of 28,504 against
  vanilla's 4.2%, while the ear roots and the neck under the tower's front stretched into a band that both fresh reviews failed (6.0% of
  the seam's 2,297 edges here).
- TRIPO-MAP-READ: an attack or a defend changes the silhouette in the map camera from the idle's less than `map_read.MIN_READ`
  (`lib/map_read.py`: the share of the idle's silhouette that changes shape at the size a player sees the unit, at the clip's 90th
  percentile frame). The limit is vanilla's horse charge against its forward idle. Both reviews of round 9 read its attack (0.15) and one
  its defend (0.01) as the idle on the map.
- TRIPO-DEATH-STIFF-LEGS: in a death the legs bend less than `DEATH_LEG_BEND` degrees (the mean over the four legs of the turn between the
  thigh or upper arm and the foot, from the rest pose, at its largest): the body falls as a block on straight legs. Round 9 bent 8 degrees.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from . import map_read, pdx_deform, pdx_motion, tripo_pose
from . import tripo_checks as T


def _finding(rule: str, subject: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": subject, "message": message, **numbers}

HOOF_SUFFIX = "_Hoof"
LEG_PREFIXES = ("Front_", "Rear_")
TORSO = ("Pelvis", "Spine", "Chest")
LOAD_BONE = "Load"
DOWN_BELLY_SHARE = 0.05
LOAD_SINK_LIMIT = 0.01
LOAD_STRETCH_LIMIT = 0.005
LOAD_SEAM_LIMIT = 0.02  # vanilla clothing's worst share of deformed edges (tripo_checks VANILLA_CLOAK_WORST, 1.97%), rounded
MAP_READ_ROLES = ("attack", "defend")
DEATH_LEG_BEND = 25.0  # degrees


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


def seam_mask(mesh: pdx_deform.SkinnedMesh) -> np.ndarray:
    """The skin the load blends into: vertices with some weight on the load bone that are not the load itself."""

    if LOAD_BONE not in mesh.bones:
        return np.zeros(len(mesh.positions), bool)
    share = np.where(mesh.joints == mesh.bones.index(LOAD_BONE), mesh.weights, 0.0).sum(axis=1)
    return (share > 1e-3) & ~load_mask(mesh)


def seam_share(mesh: pdx_deform.SkinnedMesh, posed: np.ndarray, edges: np.ndarray, seam: np.ndarray) -> Tuple[float, int]:
    """The worst frame's share of the edges touching the seam that the kit's measure counts as stretched or squashed, and that frame."""

    picked = edges[seam[edges[:, 0]] | seam[edges[:, 1]]]
    if not len(picked):
        return 0.0, 0
    rest = np.linalg.norm(mesh.positions[picked[:, 0]] - mesh.positions[picked[:, 1]], axis=1)
    usable = rest > 1e-9
    height = max(mesh.height, 1e-6)
    worst, worst_frame = 0.0, 0
    for frame, points in enumerate(posed):
        length = np.linalg.norm(points[picked[:, 0]] - points[picked[:, 1]], axis=1)
        ratio = np.where(usable, length / np.where(usable, rest, 1.0), 1.0)
        growth = (length - rest) / height
        bad = ((ratio > pdx_deform.STRETCH_RATIO) & (growth > pdx_deform.SIGNIFICANT_SHARE)) | (
            (ratio < pdx_deform.SQUASH_RATIO) & (-growth > pdx_deform.SIGNIFICANT_SHARE))
        if bad.mean() > worst:
            worst, worst_frame = float(bad.mean()), frame
    return worst, worst_frame


def leg_bend(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> float:
    """The largest over the frames of the mean over the four legs of the turn (degrees, from the rest pose) between the leg's upper segment
    (Upper to Lower joint) and its foot (Cannon to Hoof joint)."""

    index = {name: i for i, name in enumerate(mesh.bones)}
    parts = ("Upper", "Lower", "Cannon", "Hoof")
    legs = [leg for leg in ("Front_Left", "Front_Right", "Rear_Left", "Rear_Right") if all(f"{leg}_{part}" in index for part in parts)]
    if not legs:
        return 0.0
    rest = pdx_motion.rest_joints(mesh)[None]
    posed = pdx_motion.posed_joints(mesh, anim)

    def angles(joints: np.ndarray, leg: str) -> np.ndarray:
        top = joints[:, index[f"{leg}_Lower"]] - joints[:, index[f"{leg}_Upper"]]
        foot = joints[:, index[f"{leg}_Hoof"]] - joints[:, index[f"{leg}_Cannon"]]
        cosine = (top * foot).sum(axis=1) / np.maximum(np.linalg.norm(top, axis=1) * np.linalg.norm(foot, axis=1), 1e-12)
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    bends = np.stack([np.abs(angles(posed, leg) - angles(rest, leg)[0]) for leg in legs], axis=1)
    return float(bends.mean(axis=1).max())


def _map_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation], numbers: dict) -> List[dict]:
    """TRIPO-MAP-READ for the attack and defend clips, against the unit's own idle."""

    idle = next((anim for clip, anim in anims.items() if tripo_pose.role_of(clip) == "idle"), None)
    if idle is None:
        return []
    camera = map_read.MapCamera(mesh)
    idle_frames = camera.frames(idle)
    out = []
    for clip, anim in anims.items():
        role = tripo_pose.role_of(clip)
        if role not in MAP_READ_ROLES:
            continue
        reading = map_read.read_against_idle(camera, camera.frames(anim), idle_frames)
        numbers.setdefault(clip, {})["map_read"] = reading
        if reading < map_read.MIN_READ:
            out.append(_finding("TRIPO-MAP-READ", clip, f"from the map camera the {role} changes {reading:.0%} of the idle's silhouette (at least {map_read.MIN_READ:.0%}, vanilla's horse charge): it reads as the idle at map size", share=reading))
    return out


def _frames(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> np.ndarray:
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return np.stack([pdx_deform.skin(mesh, matrices[f]) for f in range(anim.frames)])


def _load_findings(mesh, clip: str, posed: np.ndarray, edges: np.ndarray, load: np.ndarray, seam: np.ndarray, row: dict) -> List[dict]:
    """TRIPO-LOAD-BELOW-GROUND, TRIPO-LOAD-STRETCH and TRIPO-LOAD-SEAM for one clip; fills `row`."""

    out: List[dict] = []
    height = max(mesh.height, 1e-6)
    floor = float(mesh.positions[:, 1].min())
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
    if seam.any():
        share, frame = seam_share(mesh, posed, edges, seam)
        row["load_seam_share"] = round(share, 4)
        if share > LOAD_SEAM_LIMIT:
            out.append(_finding("TRIPO-LOAD-SEAM", clip, f"{share:.1%} of the edges where the load blends into the body stretch or squash in frame {frame} (limit {LOAD_SEAM_LIMIT:.0%}, vanilla clothing's worst): the skin at the load tears as the parts beside it turn", share=round(share, 4), frame=frame))
    return out


def _death_findings(mesh, clip: str, anim, posed: np.ndarray, torso: np.ndarray, row: dict) -> List[dict]:
    """TRIPO-DEATH-STIFF-LEGS and TRIPO-NOT-DOWN for a death clip; fills `row`."""

    out: List[dict] = []
    bend = leg_bend(mesh, anim)
    row["death_leg_bend_degrees"] = round(bend, 1)
    if bend < DEATH_LEG_BEND:
        out.append(_finding("TRIPO-DEATH-STIFF-LEGS", clip, f"the legs bend at most {bend:.0f} degrees (at least {DEATH_LEG_BEND:.0f}): the body falls as a block on straight legs", degrees=round(bend, 1)))
    if torso.any():
        belly = float(posed[-1][torso, 1].min() - mesh.positions[:, 1].min()) / max(mesh.height, 1e-6)
        row["final_torso_lowest_share"] = round(belly, 4)
        if belly > DOWN_BELLY_SHARE:
            out.append(_finding("TRIPO-NOT-DOWN", clip, f"the body's lowest torso point ends {belly:.0%} of the height above the ground (limit {DOWN_BELLY_SHARE:.0%}): it does not end lying down", share=round(belly, 4)))
    return out


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
    seam = seam_mask(mesh)
    numbers["load_vertices"] = int(load.sum())
    numbers["seam_vertices"] = int(seam.sum())
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
        if role == "death":
            out += _death_findings(mesh, clip, anim, posed, torso, row)
        out += _load_findings(mesh, clip, posed, edges, load, seam, row)
        numbers[clip] = row
    out += _map_findings(mesh, anims, numbers)
    return out, numbers
