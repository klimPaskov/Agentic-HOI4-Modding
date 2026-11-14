"""Checks that fail what a viewer fails on a Tripo unit: the weapon through the body in any frame, a hand that does not enclose
its haft, a cloak that stretches, a blade seen edge-on.

    py -3.13 .tools/3d_pipeline/tripo/tripo_checks.py <unit folder> [--gripped gripped.glb] [--weapon-bone Weapon]
        [--clips CLIP ...] [--json out.json]

The unit folder holds the runtime `.mesh` and `.anim` files. `--gripped` is the GLB the grip stage made (with the finger
bones and the clips); the weapon checks need it, and `--weapon-bone` names the weapon's bone in the unit's mesh. A unit
without a weapon gets the cloak check only. Findings (exit code 1 when there is one):

- TRIPO-WEAPON-IN-BODY: in EVERY frame of a clip (24 fps, not 24 samples), more than `MAX_IN_BODY_SHARE` of the weapon's
  points (outside the grip zone) are deeper than `PENETRATION_MARGIN_SHARE` of the height inside the body. 1% of the height
  (1.8 cm) is the lowest margin at which idle, walk and the retreat still pass (0 to 0.7% of points) while the orc's attack
  (6 to 13% from frame 28 of 24 fps, 35 of 30) and death (2 to 5% from frame 45 of 24 fps) fail, as a viewer saw them.
- TRIPO-GRIP-ENCLOSURE: skin of the hand covers less than `MIN_ENCLOSURE_SHARE` of the haft's circumference at the grip.
- TRIPO-GRIP-THUMB: the thumb's tip is not on the other side of the haft than the fingertips (`MIN_THUMB_OPPOSITION_DEGREES`).
- TRIPO-CLOAK-STRETCH: in a clip, more than `CLOAK_MAX_STRETCH_SHARE` of the edges of the cloak region (vertices behind
  the body, weighted to the torso, hips or thighs) are stretched past 1.5x or squashed under 0.5x. The limit is the worst
  vanilla clothing stretch with a margin (see `CLOAK_MAX_STRETCH_SHARE`).
- TRIPO-BLADE-FACING: in the idle pose the broad face of the weapon's head turns more than `MAX_BLADE_FACING_DEGREES` from the
  direction the unit faces (the front view shows it edge-on).
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

from lib import pdx_deform, pdx_motion, tripo_checks as T, tripo_grip as G  # noqa: E402

# Weapon through the body (clip_check's deep share, every frame).
MAX_IN_BODY_SHARE = 0.01
PENETRATION_MARGIN_SHARE = 0.01
# The cloak: the worst share of region edges a clip stretches or squashes. Vanilla's worst clothing (back and coat-tail
# vertices of ENG, GER and FRA infantry over their clips) reaches `VANILLA_CLOAK_WORST`; the limit is that with a margin.
VANILLA_CLOAK_WORST = 0.069
CLOAK_MAX_STRETCH_SHARE = 0.07
CLOAK_BONES = ("Hips", "Spine", "Spine01", "Spine02", "LeftUpLeg", "RightUpLeg")
ENCLOSURE_HALF_LENGTH_SHARE = 0.03
ENCLOSURE_TOLERANCE_SHARE = T.ENCLOSURE_TOLERANCE_SHARE
MIN_ENCLOSURE_SHARE = T.MIN_ENCLOSURE_SHARE
MIN_THUMB_OPPOSITION_DEGREES = T.MIN_THUMB_OPPOSITION_DEGREES
MAX_BLADE_FACING_DEGREES = T.MAX_BLADE_FACING_DEGREES


def finding(rule: str, subject: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": subject, "message": message, **numbers}


def front_direction(mesh) -> np.ndarray:
    """The direction the unit faces (horizontal, y up): from the heels to the toes in the rest pose."""

    joints = pdx_motion.rest_joints(mesh)
    names = {name: index for index, name in enumerate(mesh.bones)}
    vectors = []
    for side in ("Left", "Right"):
        if f"{side}Foot" in names and f"{side}ToeBase" in names:
            vectors.append(joints[names[f"{side}ToeBase"]] - joints[names[f"{side}Foot"]])
    if not vectors:
        return np.array([0.0, 0.0, 1.0])
    front = np.mean(vectors, axis=0)
    front[1] = 0.0
    return T.unit(front)


def posed_frames(mesh, anim, step: int = 1):
    matrices = pdx_deform.skinning_matrices(mesh, anim)
    return [pdx_deform.skin(mesh, matrices[i]) for i in range(0, matrices.shape[0], step)]


def cloak_findings(mesh, anims: Dict[str, object], step: int = 2) -> (List[dict], dict):
    """TRIPO-CLOAK-STRETCH per clip. Also returns the numbers (region size and each clip's worst share)."""

    names = np.array(mesh.bones)
    dominant = pdx_deform.dominant_bones(mesh)
    dominant_names = np.where(dominant >= 0, names[np.clip(dominant, 0, None)], "")
    joints = pdx_motion.rest_joints(mesh)
    index = {name: i for i, name in enumerate(mesh.bones)}
    hips = joints[index["Hips"]] if "Hips" in index else mesh.positions.mean(axis=0)
    front = front_direction(mesh)
    height = mesh.height
    mask = T.cloak_region(mesh.positions, dominant_names, hips, front, height, CLOAK_BONES)
    edges = pdx_deform.mesh_edges(mesh)
    out, numbers = [], {"region_vertices": int(mask.sum()), "clips": {}}
    for clip, anim in anims.items():
        share, frame = T.region_stretch_share(mesh.positions, posed_frames(mesh, anim, step), edges, mask, height)
        numbers["clips"][clip] = {"worst_share": round(share, 4), "frame": frame * step}
        if share > CLOAK_MAX_STRETCH_SHARE:
            out.append(finding("TRIPO-CLOAK-STRETCH", clip,
                               f"{share:.1%} of the cloak region's edges are stretched or squashed in frame {frame * step} ({int(mask.sum())} vertices behind the body); the limit is {CLOAK_MAX_STRETCH_SHARE:.0%}",
                               share=round(share, 4), frame=frame * step))
    return out, numbers


def blade_findings(mesh, anims: Dict[str, object], weapon_bone: str) -> (List[dict], dict):
    if weapon_bone not in mesh.bones:
        return [], {}
    bone = mesh.bones.index(weapon_bone)
    dominant = pdx_deform.dominant_bones(mesh)
    weapon = (dominant == bone) & (mesh.weights.max(axis=1) > 0.99)
    idle = next((anim for clip, anim in anims.items() if clip.endswith("idle")), None)
    if idle is None or weapon.sum() < 50:
        return [], {}
    posed = posed_frames(mesh, idle, step=max(1, idle.frames))[0]
    joints = pdx_motion.posed_joints(mesh, idle)[0]
    hand = next((i for i, name in enumerate(mesh.bones) if name == "RightHand"), None)
    hand_point = joints[hand] if hand is not None else posed[weapon].mean(axis=0)
    angle, normal = T.blade_facing_degrees(posed[weapon], hand_point, front_direction(mesh))
    numbers = {"degrees": round(angle, 1), "face_normal": np.round(normal, 3).tolist()}
    if angle > MAX_BLADE_FACING_DEGREES:
        return [finding("TRIPO-BLADE-FACING", "idle", f"the broad face of the weapon's head is {angle:.0f} degrees off the front view (limit {MAX_BLADE_FACING_DEGREES:.0f}): it shows edge-on", degrees=round(angle, 1))], numbers
    return [], numbers


def weapon_in_body_findings(gripped: Path, clips: Sequence[str], weapon_joint: str) -> (List[dict], dict):
    import clip_check as cc

    result = cc.check(str(gripped), "tripo_part_0", "tripo_part_1", weapon_joint, "all", only=list(clips) or None,
                      per_frame_ground=True, margin_share=PENETRATION_MARGIN_SHARE)
    out, numbers = [], {}
    for clip, row in result["clips"].items():
        series = row["weapon_deep_in_body_pct_by_frame"]
        limit = 100 * MAX_IN_BODY_SHARE
        bad = [i for i, value in enumerate(series) if value > limit]
        numbers[clip] = {"frames": row["frames"], "worst_pct": max(series), "worst_frame": series.index(max(series)), "frames_over": len(bad)}
        if bad:
            out.append(finding("TRIPO-WEAPON-IN-BODY", clip,
                               f"the weapon is more than {PENETRATION_MARGIN_SHARE:.0%} of the height inside the body in {len(bad)} of {row['frames']} frames (24 fps frames {bad[0]} to {bad[-1]}), up to {max(series):.1f}% of its points (limit {limit:.1f}%)",
                               frames=bad[:40], worst_pct=max(series)))
    return out, numbers


def grip_findings(gripped: Path, hand: str = "mixamorig:RightHand") -> (List[dict], dict):
    import clip_check as cc

    rig = cc.Rig(str(gripped), "tripo_part_0", "tripo_part_1")
    mats = rig.skin_mats(rig.joint_worlds({}))
    body = rig.skin(rig.body, mats)
    weapon = rig.skin(rig.weapon, mats) if "joint_ids" in rig.weapon else rig.weapon["positions"]
    height = float(np.ptp(body[:, 1]))
    names = rig.joint_names
    ids, weights = rig.body["joint_ids"], rig.body["weights"]

    def share(selected):
        return sum(weights[:, k] * np.isin(ids[:, k], list(selected)) for k in range(4))

    hand_joints = {i for i, n in enumerate(names) if n.startswith(hand)}
    thumb_joints = {i for i, n in enumerate(names) if n.startswith(hand + "Thumb")}
    tip_joints = {i for i, n in enumerate(names) if n.startswith(hand) and n.rstrip("0123456789").endswith(("Index", "Middle", "Ring", "Pinky")) and n[-1] in "34"}
    skin = body[share(hand_joints) > 0.5]
    centre, axes, _values = T.principal_axes(weapon)
    palm = rig.joint_worlds({})[:, :3, 3][names.index(hand)]
    haft = axes[0]
    point = centre + float((palm - centre) @ haft) * haft
    radius = G.haft_radius(weapon, point, haft, 0.0, 0.05 * height)
    coverage = T.enclosure_share(point, haft, radius, skin, ENCLOSURE_TOLERANCE_SHARE * height, ENCLOSURE_HALF_LENGTH_SHARE * height)
    numbers = {"enclosure_share": round(coverage, 3), "haft_radius": round(radius, 4), "skin_points": int(len(skin))}
    out = []
    if coverage < MIN_ENCLOSURE_SHARE:
        out.append(finding("TRIPO-GRIP-ENCLOSURE", "grip", f"hand skin covers {coverage:.0%} of the haft's circumference at the grip (limit {MIN_ENCLOSURE_SHARE:.0%}): the fingers do not wrap it", share=round(coverage, 3)))
    thumb, tips = body[share(thumb_joints) > 0.5], body[share(tip_joints) > 0.3]
    if len(thumb) and len(tips):
        opposition = G.opposite_sides([tips.mean(axis=0)], thumb.mean(axis=0), point, haft)
        numbers["thumb_opposition_degrees"] = round(opposition, 1)
        if opposition < MIN_THUMB_OPPOSITION_DEGREES:
            out.append(finding("TRIPO-GRIP-THUMB", "grip", f"the thumb is {opposition:.0f} degrees from the fingertips round the haft (limit {MIN_THUMB_OPPOSITION_DEGREES:.0f}): it is on their side", degrees=round(opposition, 1)))
    return out, numbers


def load_unit(folder: Path):
    mesh_path = sorted(folder.glob("*.mesh"))[0]
    mesh = pdx_deform.load_mesh(mesh_path)
    anims = {path.stem: pdx_deform.load_anim(path) for path in sorted(folder.glob(f"{mesh_path.stem}_*.anim"))}
    return mesh, anims


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--gripped", type=Path, help="the grip stage's GLB, for the weapon-in-body and grip checks")
    parser.add_argument("--weapon-bone", default="", help="the weapon's bone in the unit's mesh (blade facing)")
    parser.add_argument("--weapon-joint", default="mixamorig:Weapon", help="the weapon's joint in the gripped GLB")
    parser.add_argument("--clips", nargs="*", default=[], help="clips of the gripped GLB to check for the weapon in the body (default all)")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    mesh, anims = load_unit(args.folder.resolve())
    findings, numbers = [], {}
    found, numbers["cloak"] = cloak_findings(mesh, anims)
    findings += found
    if args.weapon_bone:
        found, numbers["blade"] = blade_findings(mesh, anims, args.weapon_bone)
        findings += found
    if args.gripped:
        found, numbers["weapon_in_body"] = weapon_in_body_findings(args.gripped, args.clips, args.weapon_joint)
        findings += found
        found, numbers["grip"] = grip_findings(args.gripped)
        findings += found
    report = {"findings": findings, "numbers": numbers}
    if args.json:
        args.json.write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")
    for item in findings:
        print(f"{item['rule']} [{item['subject']}] {item['message']}")
    print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
