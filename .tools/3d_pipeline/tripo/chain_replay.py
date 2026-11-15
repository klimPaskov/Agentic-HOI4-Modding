"""Replay the chain stage offline from a `TRIPO_CHAIN_DUMP` folder and measure the cloak as TRIPO-CLOAK-STRETCH does. No Blender.

    py -3.13 -B .tools/3d_pipeline/tripo/chain_replay.py <dump folder> [--regions cloak plates] [--json out.json]

`tripo/prepare_tripo_unit.py` writes the dump when `TRIPO_CHAIN_DUMP` names a folder: `chain_inputs.npz` (the joined body's vertices,
edges, weights and every bone's rest matrix) and one `chain_role_<role>.npz` per clip (every body bone's posed world matrix per frame,
after the clip's own rules ran: trim, arm level, untwist, settle). This tool runs the same `tripo/chain_stage.py` code on them:
`plan_stage` (regions, new bones and weights), `finish_stage` with the chain bones' rest matrices as Blender makes them
(`chain_bone_rest`), then `bake_numpy` per clip. It skins the mesh with the new weights and measures, per clip, the share of the cloak
region's edges stretched past 1.5 times or squashed under half their rest length by more than 0.5% of the height (the region and the
rule of `tripo/tripo_checks.py`, in Blender's Z-up world), so a change to the chain rules is measured in seconds instead of a Blender
run. The exported files differ a little (decimation, the export's resampling to 30 frames a second, the weight rule of
`lib/stretch_smooth.py`), so the check on the exported files stays the judge.
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

from lib import tripo_chains as C
from lib import tripo_checks as T
import chain_stage as S

CLOAK_BONES = ("Hips", "Spine", "Spine01", "Spine02", "Hip", "back_mid", "LeftUpLeg", "RightUpLeg")  # tripo/tripo_checks.CLOAK_BONES
CLIP_STEP = 2  # tripo_checks.cloak_findings samples every second frame


def load_inputs(folder: Path) -> tuple:
    dump = np.load(folder / "chain_inputs.npz", allow_pickle=True)
    names = [str(n) for n in dump["names"]]
    rows = [{names[b]: float(w) for b, w in zip(bones, weights) if b >= 0 and w > 0} for bones, weights in zip(dump["row_bones"], dump["row_weights"])]
    inputs = {
        "positions": dump["positions"], "edges": dump["edges"], "triangles": dump["triangles"], "rows": rows,
        "heads": {n: dump["heads"][i] for i, n in enumerate(names)}, "rest": {n: dump["rest"][i] for i, n in enumerate(names)},
        "parents": {n: (str(p) or None) for n, p in zip(names, dump["parents"])}, "bone_count": int(dump["bone_count"]),
    }
    return inputs, [str(r) for r in dump["regions"]]


def load_roles(folder: Path) -> Dict[str, dict]:
    out = {}
    for path in sorted(folder.glob("chain_role_*.npz")):
        data = np.load(path, allow_pickle=True)
        names = [str(n) for n in data["names"]]
        worlds = data["worlds"]  # (frames, bones, 4, 4)
        out[path.stem[len("chain_role_"):]] = {"worlds": {n: worlds[:, i] for i, n in enumerate(names)}, "fps": float(data["fps"]),
                                                "looping": bool(data["looping"])}
    return out


def chain_rest(planned: dict) -> Dict[str, np.ndarray]:
    """World rest matrices of the chain bones, as `add_bones` makes them in Blender (`chain_bone_rest`, rolled toward the front)."""

    out = {}
    for sheet in planned["sheets"]:
        for c, chain in enumerate(S.bone_names(sheet)):
            for b, name in enumerate(chain):
                head, tail = sheet["joints"][c, b], sheet["joints"][c, b + 1]
                if np.linalg.norm(tail - head) < 1e-5:
                    tail = head + np.array([0.0, 0.0, -1e-3])
                out[name] = S.chain_bone_rest(head, tail, planned["front"])
    return out


def chain_worlds(stage: dict, body_worlds: Dict[str, np.ndarray], quaternions: Sequence[np.ndarray]) -> Dict[str, np.ndarray]:
    """Posed world matrices (frames, 4, 4) of every chain bone: the parent's pose, the rest offset, then the baked local turn."""

    parent = np.stack([C.orthonormal(m) for m in body_worlds[C.CHAIN_PARENT]])
    out = {}
    for plan, quats in zip(stage["plans"], quaternions):
        current = parent.copy()
        for k, name in enumerate(plan["bones"]):
            local = np.tile(np.eye(4), (len(current), 1, 1))
            for f in range(len(current)):
                local[f, :3, :3] = C.matrix_from_quaternion(quats[f, k])
            current = current @ plan["rest_relative"][k] @ local
            out[name] = current
    return out


def skin(positions: np.ndarray, rows: Sequence[Dict[str, float]], skinning: Dict[str, np.ndarray], frame: int) -> np.ndarray:
    homogeneous = np.c_[positions, np.ones(len(positions))]
    out = np.zeros_like(positions)
    by_bone: Dict[str, List[tuple]] = {}
    for v, row in enumerate(rows):
        for name, weight in row.items():
            by_bone.setdefault(name, []).append((v, weight))
    for name, items in by_bone.items():
        index = np.array([v for v, _ in items])
        weight = np.array([w for _, w in items])
        matrix = skinning[name][frame] if name in skinning else np.eye(4)
        out[index] += weight[:, None] * (homogeneous[index] @ matrix.T)[:, :3]
    return out


def replay(folder: Path, regions: Optional[Sequence[str]] = None) -> dict:
    inputs, dumped = load_inputs(folder)
    regions = list(regions or dumped)
    roles = load_roles(folder)
    swing_bones = (C.CHAIN_PARENT,) + S.SWING_BONES
    swing = S.swing_segments([{n: role["worlds"][n][::S.SWING_FRAME_STEP] for n in swing_bones} for role in roles.values()], inputs["rest"]) if roles else None
    planned = S.plan_stage(inputs, regions, swing)
    rest = dict(inputs["rest"])
    rest.update(chain_rest(planned))
    stage = S.finish_stage(planned, lambda name: rest[name], inputs["bone_count"] + sum(len(c) for s in planned["sheets"] for c in S.bone_names(s)))
    rows = planned["rows"]
    positions = np.asarray(inputs["positions"], float)
    dominant = np.array([max(row, key=row.get) if row else "" for row in rows])
    up = planned["up"]
    mask = T.cloak_region(positions, dominant, inputs["heads"]["Hips"], planned["front"], planned["height"],
                          CLOAK_BONES + tuple(C.chain_bones(rest, "cloak")), up_axis=int(np.argmax(np.abs(up))))
    edges = np.asarray(inputs["edges"])
    root = root_zone(rows, edges, rest)
    report = {"regions": regions, "cloak_region_vertices": int(mask.sum()), "root_zone_vertices": int(root.sum()), "clips": {}}
    for role, data in roles.items():
        worlds = data["worlds"]
        body = S.body_from_worlds(worlds, rest, S.body_bones(stage))
        quaternions = S.bake_numpy(stage, body, role, 1.0 / data["fps"], data["looping"])
        skinning = {name: worlds[name] @ np.linalg.inv(rest[name]) for name in worlds if name in rest}
        for name, matrices in chain_worlds(stage, worlds, quaternions).items():
            skinning[name] = matrices @ np.linalg.inv(rest[name])
        frames = len(next(iter(worlds.values())))
        posed = [skin(positions, rows, skinning, f) for f in range(0, frames, CLIP_STEP)]
        share, frame = T.region_stretch_share(positions, posed, edges, mask, planned["height"])
        root_share, root_frame = T.region_stretch_share(positions, posed, edges, root, planned["height"])
        report["clips"][role] = {"cloak_stretch_share": round(share, 4), "frame": frame * CLIP_STEP,
                                 "root_stretch_share": round(root_share, 4), "root_frame": root_frame * CLIP_STEP}
    return report


def root_zone(rows: Sequence[Dict[str, float]], edges: np.ndarray, bones: Sequence[str], rings: int = 2) -> np.ndarray:
    """Where the chains blend into the body: vertices with between 1% and 99.9% of their weight on chain bones, grown `rings` edge
    rings. A fresh review of the round 4 demon saw both wing roots stretch at the shoulders in every clip while the wing check, which
    reads the far membrane only, measured none."""

    chain = set(C.chain_bones(bones))
    share = np.array([sum(w for name, w in row.items() if name in chain) for row in rows])
    zone = (share > 0.01) & (share < 0.999)
    for _ in range(rings):
        reached = zone[edges].any(axis=1)
        zone[edges[reached].ravel()] = True
    return zone


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dump", type=Path)
    parser.add_argument("--regions", nargs="*")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    report = replay(args.dump, args.regions)
    text = json.dumps(report, indent=1)
    if args.json:
        args.json.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
