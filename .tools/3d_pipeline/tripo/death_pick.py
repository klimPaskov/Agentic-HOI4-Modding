"""Pick a Tripo death clip by measurement, before a run: every death candidate of a rigged GLB, played on a unit's exported mesh.

    py -3.13 -B death_pick.py <asset>__rigged.glb <unit folder or .mesh> --clips defeat_02 defeat_03 fall "A zombie soldier" --settled --json picks.json

Each candidate (a clip name, or the first words of a text-to-motion clip's name) is carried from the GLB onto the mesh the game loads: each
joint's turn in every frame (its world turn against the GLB's bind pose) is moved into the mesh's own space by the similarity that maps the GLB's
bind joints onto the mesh's (a mirror: the exporter flips the forward axis), the mesh keeps its own bone lengths, and the keys are read back at
30 frames a second, the game's rate. Each frame is then lifted so no skin is under the rest pose's ground (a death is only lifted, as the route's
ground pass does). On the zombie (zombie_k, 2026-11-18) defeat_03 carried this way puts every joint within 0.2% of the height of the exported clip
up to frame 74, where no route rule had yet acted, and its deformed edges read 185 and 185 against the export's 182 and 189. The mesh's weights
are the route's, so a mesh from an earlier run of the same unit judges the candidates on the skin the next run will have. The route's death
settles (the knee swing, the free fall, the legs and the upper body) are not applied to the first row of each candidate. With `--settled` a
second row measures it after them and the ground pass (`run_pilot.ground_exported_clip`), as the next run will export it, and the pick is made
on those rows.

The measures, with the route's limits: the thigh split (TRIPO-DEATH-SPLAY, `lib/tripo_splay.py`), the hips holding themselves up (TRIPO-DEATH-HOVER,
`lib/tripo_fall.py`), the end pose lying down (TRIPO-NOT-DOWN) and no limb inside the torso (TRIPO-LIMB-IN-TORSO, `tripo_checks.death_findings`),
the chest, head and hands resting on the ground (TRIPO-DEATH-REST, `lib/tripo_pose.py`), and the kit's deformation over the clip (the worst
frame's stretched and squashed edges, `pdx_deform.deformation_report`). The pick (`pick`) is the candidate that passes every limit with the fewest
deformed edges. When none passes, the one with the fewest failed rules, then the fewest deformed edges, is named as the closest.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import clip_check
import tripo_checks
from lib import pdx_deform, tripo_fall, tripo_pose, tripo_splay

FPS = 30.0


def bone_key(name: str) -> str:
    """A joint name with the rig's prefix and the leading zeros of its numbers dropped: `mixamorig:Spine1` and the kit's `Spine01` match."""

    name = name.split(":")[-1].lower()
    return re.sub(r"0+(\d)", r"\1", name)


def similarity(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """The 4x4 scale, orthogonal turn and translation that best maps the `source` points onto the `target` points (Umeyama). The turn may be a
    mirror: the PDX exporter flips the forward axis (the GLB's toes point along +Z, the mesh's along -Z), so the proper rotation leaves the
    feet and hands 8% of the height out where the mirror fits within a millimetre."""

    ms, mt = source.mean(axis=0), target.mean(axis=0)
    a, b = source - ms, target - mt
    u, d, vt = np.linalg.svd(b.T @ a / len(source))
    variance = max((a * a).sum() / len(source), 1e-12)
    best = None
    for flip in (np.eye(3), np.diag([1.0, 1.0, -1.0])):
        turn = u @ flip @ vt
        scale = float(np.trace(np.diag(d) @ flip) / variance)
        residual = float(np.abs(a @ (scale * turn).T - b).max())
        if best is None or residual < best[0]:
            best = (residual, scale, turn)
    _, scale, turn = best
    out = np.eye(4)
    out[:3, :3] = scale * turn
    out[:3, 3] = mt - scale * turn @ ms
    return out


def _matching_clip(names: Sequence[str], wanted: str) -> Optional[str]:
    return next((name for name in names if name == wanted), None) or next((name for name in names if name.startswith(wanted)), None)


def carry(rig: "clip_check.Rig", tracks: dict, end: float, mesh: pdx_deform.SkinnedMesh) -> pdx_deform.Animation:
    """The GLB clip as a `pdx_deform.Animation` on `mesh` (see the module text), lifted out of the ground per frame."""

    keys = {bone_key(name): k for k, name in enumerate(rig.joint_names)}
    pairs = [(i, keys[bone_key(name)]) for i, name in enumerate(mesh.bones) if bone_key(name) in keys]
    glb_bind = np.linalg.inv(rig.inverse)
    pdx_bind = np.linalg.inv(mesh.inverse_bind)
    fit = similarity(np.array([glb_bind[k][:3, 3] for _, k in pairs]), np.array([pdx_bind[i][:3, 3] for i, _ in pairs]))
    back = np.linalg.inv(fit)
    turn = fit[:3, :3] / np.cbrt(abs(np.linalg.det(fit[:3, :3])))  # orthogonal, a mirror when the exporter flipped an axis
    frames = int(end * FPS) + 1
    bind_rot = pdx_bind[:, :3, :3] / np.cbrt(np.abs(np.linalg.det(pdx_bind[:, :3, :3])))[:, None, None]
    rotation = np.tile(bind_rot, (frames, 1, 1, 1))
    root_position = np.tile(pdx_bind[:, :3, 3], (frames, 1, 1))
    for frame in range(frames):
        skinning = rig.skin_mats(rig.joint_worlds(rig.pose_for(tracks, min(frame / FPS, end))))
        for i, k in pairs:
            # only the joint's turn is carried (the mesh's own bone lengths stay), and where it is for a root
            delta = skinning[k][:3, :3] / np.cbrt(abs(np.linalg.det(skinning[k][:3, :3])))
            rotation[frame, i] = turn @ delta @ turn.T @ bind_rot[i]
            root_position[frame, i] = (fit @ skinning[k] @ back @ pdx_bind[i])[:3, 3]
    bind_local = pdx_deform._bind_locals(mesh)
    channels: Dict[str, Dict[str, np.ndarray]] = {}
    for i, name in enumerate(mesh.bones):
        parent = mesh.parents[i]
        local = rotation[:, i] if parent < 0 else np.transpose(rotation[:, parent], (0, 2, 1)) @ rotation[:, i]
        q = np.array([tripo_pose._quaternion_from_matrix(m) for m in local])
        for f in range(1, frames):
            if q[f] @ q[f - 1] < 0:
                q[f] = -q[f]
        t = root_position[:, i].copy() if parent < 0 else np.tile(bind_local[i][:3, 3], (frames, 1))
        channels[name] = {"t": t, "q": q, "s": np.ones(frames)}
    anim = pdx_deform.Animation(FPS, frames, channels)
    roots = [mesh.bones[i] for i, parent in enumerate(mesh.parents) if parent < 0]
    ground = float(mesh.positions[:, 1].min())
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    for frame in range(frames):
        lift = max(0.0, ground - float(pdx_deform.skin(mesh, matrices[frame])[:, 1].min()))
        for root in roots:
            channels[root]["t"][frame, 1] += lift
    return anim


def _prop(name: str, kind: str, values) -> bytes:
    head = b"!" + struct.pack("<B", len(name)) + name.encode("latin-1") + kind.encode() + struct.pack("<i", len(values))
    if kind == "i":
        return head + struct.pack(f"<{len(values)}i", *values)
    if kind == "f":
        return head + struct.pack(f"<{len(values)}f", *values)
    for value in values:
        encoded = value.encode("latin-1") + b"\0"
        head += struct.pack("<i", len(encoded)) + encoded
    return head


def write_anim(path: Path, anim: pdx_deform.Animation, bones: Sequence[str]) -> None:
    """`anim` as an `.anim` file with a translation and a rotation key per joint and frame, which the route's settles read and patch."""

    data = b"@@b@" + b"[info\0" + _prop("fps", "f", [anim.fps]) + _prop("sa", "i", [anim.frames]) + _prop("j", "i", [len(bones)])
    for name in bones:
        channel = anim.channels[name]
        data += b"[[" + name.encode("latin-1") + b"\0" + _prop("sa", "s", ["tq"])
        data += _prop("t", "f", [float(v) for v in channel["t"][0]]) + _prop("q", "f", [float(v) for v in channel["q"][0]]) + _prop("s", "f", [1.0])
    q = [float(v) for frame in range(anim.frames) for name in bones for v in anim.channels[name]["q"][frame]]
    t = [float(v) for frame in range(anim.frames) for name in bones for v in anim.channels[name]["t"][frame]]
    data += b"[samples\0" + _prop("q", "f", q) + _prop("t", "f", t)
    Path(path).write_bytes(data)


def settled(mesh_path: Path, mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation) -> pdx_deform.Animation:
    """`anim` after the route's death settles and ground pass (`run_pilot.ground_exported_clip`), as the next run's export will have it."""

    import run_pilot

    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "candidate_death.anim"
        write_anim(path, anim, mesh.bones)
        run_pilot.ground_exported_clip(Path(mesh_path), path, "death", {})
        return pdx_deform.load_anim(path)


def measure(mesh: pdx_deform.SkinnedMesh, anim: pdx_deform.Animation, clip: str) -> dict:
    """Every death measure of one carried candidate, with the rules it fails."""

    stem = "candidate_death"
    found: List[dict] = []
    row: dict = {"clip": clip, "frames": anim.frames}
    splay, splay_numbers = tripo_splay.splay_findings(mesh, {stem: anim})
    found += splay
    row["splay_degrees"] = splay_numbers[stem].get("worst_degrees")
    hover_row: dict = {}
    found += tripo_fall.hover_findings(mesh, anim, stem, hover_row)
    row["hover_peak_share"] = hover_row.get("fall_hover_peak_share")
    row["hover_ratio"] = hover_row.get("fall_ratio")
    death, death_numbers = tripo_checks.death_findings(mesh, {stem: anim})
    found += death
    numbers = death_numbers.get(stem, {})
    row.update(limb_in_torso_share=numbers.get("limb_in_torso_worst_share"), final_extent_share=numbers.get("final_extent_share"),
               final_extent_limit=numbers.get("final_extent_limit"), torso_vertical_share=numbers.get("torso_vertical_share"))
    rest = tripo_pose.death_rest_heights(mesh, anim) or {}
    row["rest_heights"] = rest
    parts = [rest[name] for name in ("chest", "head", "left hand", "right hand") if name in rest]
    if rest.get("hips", 1.0) <= tripo_pose.DEATH_FEET_LIMIT and parts and max(parts) > tripo_pose.DEATH_REST_LIMIT:
        found.append({"rule": "TRIPO-DEATH-REST", "subject": stem})
    report = pdx_deform.deformation_report(mesh, anim)
    row.update(stretched_edges=report.stretched_edges, squashed_edges=report.squashed_edges, deformed_edges=report.stretched_edges + report.squashed_edges,
               worst_frame=report.worst_frame)
    row["fails"] = sorted({item["rule"] for item in found})
    return row


def pick(rows: Sequence[dict]) -> dict:
    """{'pick': clip or None, 'closest': clip, 'why': text}: the candidate that passes every limit with the fewest deformed edges, else the one
    that fails the fewest rules, then has the fewest deformed edges."""

    passing = [row for row in rows if not row["fails"]]
    if passing:
        best = min(passing, key=lambda row: row["deformed_edges"])
        return {"pick": best["clip"], "closest": best["clip"], "why": f"passes every limit with {best['deformed_edges']} deformed edges"}
    best = min(rows, key=lambda row: (len(row["fails"]), row["deformed_edges"]))
    return {"pick": None, "closest": best["clip"], "why": f"none passes; closest fails {', '.join(best['fails'])}"}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("glb", type=Path, help="the rigged GLB with the candidate clips")
    parser.add_argument("mesh", type=Path, help="the unit's exported .mesh, or the folder that holds it")
    parser.add_argument("--clips", nargs="+", required=True, help="clip names, or the first words of a text-to-motion clip's name")
    parser.add_argument("--settled", action="store_true", help="also measure each candidate after the route's death settles and ground pass")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    mesh_path = args.mesh if args.mesh.suffix == ".mesh" else next(iter(sorted(args.mesh.glob("*.mesh"))))
    mesh = pdx_deform.load_mesh(mesh_path)
    doc, _ = clip_check.load_glb(args.glb)
    body = next(node["name"] for node in doc["nodes"] if "mesh" in node and "skin" in node)
    rig = clip_check.Rig(args.glb, body, None)
    clips = {name: (tracks, end) for name, tracks, end in rig.clips()}
    rows = []
    for wanted in args.clips:
        name = _matching_clip(list(clips), wanted)
        if name is None:
            print(f"no clip named {wanted!r}", file=sys.stderr)
            return 2
        anim = carry(rig, *clips[name], mesh)
        rows.append(measure(mesh, anim, name))
        if args.settled:
            rows.append(measure(mesh, settled(mesh_path, mesh, anim), f"{name} (settled)"))
    verdict = pick([row for row in rows if row["clip"].endswith("(settled)")] if args.settled else rows)
    print(f"{'clip':<28}{'splay':>7}{'hover':>7}{'limb':>7}{'extent':>8}{'rest':>7}{'str':>6}{'sq':>6}  fails")
    for row in rows:
        rest = row["rest_heights"]
        top = max((rest[name] for name in ("chest", "head", "left hand", "right hand") if name in rest), default=0.0)
        print(f"{row['clip'][:27]:<28}{row['splay_degrees'] or 0:>7.1f}{row['hover_ratio'] or 0:>7.2f}{row['limb_in_torso_share'] or 0:>7.3f}"
              f"{row['final_extent_share'] or 0:>8.3f}{top:>7.3f}{row['stretched_edges']:>6}{row['squashed_edges']:>6}  {', '.join(row['fails']) or '-'}")
    print(f"pick: {verdict['pick'] or '-'} ({verdict['why']})")
    if args.json:
        args.json.write_text(json.dumps({"rows": rows, **verdict}, indent=1, default=float), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
