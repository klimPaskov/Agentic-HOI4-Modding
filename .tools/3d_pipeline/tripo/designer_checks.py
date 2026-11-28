"""Blocking checks for the faults fresh reviewers failed at the designer's size on runs whose other checks all passed (D-140, D-174).

    py -3.13 -B .tools/3d_pipeline/tripo/designer_checks.py <unit folder> [--entity-scale S | --jobs-config <jobs> --slug <unit>]
        [--weapon-bone <bone>] [--json out.json]

`tripo/tripo_checks.py` runs them for every unit that is not a kit quadruped and counts their findings as failures. The measures are in
`lib/designer_read.py`: the end joints' pose on the designer screen, and the silhouette at the designer's pixel size.

- TRIPO-DESIGNER-STRIKE-STILL: the attack's frames barely differ. Its pose spread (the largest mean end-joint distance between two of its
  frames, over the height) is under `MIN_ATTACK_SPREAD`.
- TRIPO-DESIGNER-GAIT-ALIKE: the move and the retreat show the same poses. More than `MAX_GAIT_ALIKE` of one clip's frames lie within
  `designer_read.ALIKE_DISTANCE` of a frame of the other.
- TRIPO-DESIGNER-HEAD-HIDDEN: a wing or a limb hides the head. In a clip that is not the death, more than half of the head's pixels are
  covered by a nearer part for more than `MAX_HEAD_HIDDEN_SECONDS` running. The held weapon is no cover in the attack (a blow may pass the
  face: the passed dwarf's glaive hid 65% of its head for 0.17 s), nor a held shield in the defend (a guard raises it before the face).

Calibration (2026-11-28), on the exported files of the 3D lanes' runs. Passed: the bipeds two fresh reviewers passed (demon_g 2026-11-21,
orc_k, ogre_l and dwarf_f under D-83). Failed: the runs whose reviewers named these faults while every automatic check passed: the devil's
strike (devil_f, "the six frames barely differ"), the hobgoblin (its final run: "idle, move and retreat read nearly the same", "the death
crumple is lumpy and the mallet detaches"), the zombie's runs d, f, h, k, m and q, the demon's run f and the devil's retreat wing (devil_e).

The pose numbers, (passed) against (failed), with the designer camera and with the camera turned 10 degrees each way (its elevation is
known to about ten degrees, `lib/designer_preview.py`):

- attack spread: demon_g 0.151 (0.149 to 0.163), orc_k 0.206, ogre_l 0.287, dwarf_f 0.219, against the devil's strikes 0.100 (devil_f,
  0.087 to 0.106) and 0.115 (devil_e, 0.095 to 0.125). `MIN_ATTACK_SPREAD` 0.135 sits between them under every view. The zombie's attacks
  read 0.116 to 0.196, and the reviewers failed them for what they read as (a flail, a bow, a sway), which no distance measures.
- move and retreat alike, the larger of the two directions: 0.00 for every passed biped under every view, against the hobgoblin's 0.71
  (0.43 to 0.96: its retreat passes through its move's poses). `MAX_GAIT_ALIKE` 0.25.

What the measures do not separate, so no check claims it: a defend that a reviewer read as the attack's peak or as the idle (no frame of
any zombie's defend lies within 0.03 of its attack or its idle, the same as for the passed units), a move that reads like the idle (45% of
the passed orc's move frames lie within 0.03 of its idle, 0% of the failed zombies'), a held attack (the passed orc's attack holds one pose in
60% of its frames, and the beast's held attack left no exported clip to measure; `held` is reported), and a retreat that keeps the idle's
stance (it read so for the hobgoblin from one side and not from the designer's). The death's shape and a weapon that comes apart are
reported, not judged: the hobgoblin's lumpy death fills 0.79 of its outline's hull where the passed ogre's fills 0.87 (the orc 0.66, the
dwarf 0.71), and the passed orc and ogre drop their weapons 34 and 43 designer pixels from the body while the hobgoblin's mallet, which a
reviewer saw come apart in frame 31, never leaves its outline. The zombie's runs d to m share one death, whose plank pose is in its middle
frames, not at its end.

The head cover, with the designer camera (more than half of the head covered, the longest run): the devil's retreat that looked back over
its wing side 0.2 s (81% at worst, frames 14 to 19 of 39), the same retreat over the other shoulder 0 s, every passed biped 0 s with its held
weapon left out (the dwarf's glaive passes its face for 0.17 s in the blow). Those stay with the fresh reviewer and the maintainer's pass (D-174). Silhouette pixel counts did
not separate any of these: at the designer's size a hand that moves a little crosses thousands of pixels in every clip.

Kit quadrupeds (a mount, a winged quadruped) are not judged here: the only passed one (the war elephant, run14) moves its attack 0.093 and
its retreat lies wholly inside its move, as a loaded animal's does, while the failed dragons read the same, so no limit separates them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import designer_read as D
from lib import pdx_deform

MIN_ATTACK_SPREAD = 0.135
MAX_GAIT_ALIKE = 0.25
MAX_HEAD_HIDDEN_SECONDS = 0.1
HEAD_HIDDEN_SHARE = 0.5
RULES = ("TRIPO-DESIGNER-STRIKE-STILL", "TRIPO-DESIGNER-GAIT-ALIKE", "TRIPO-DESIGNER-HEAD-HIDDEN")


def _finding(rule: str, subject: str, message: str, **numbers) -> dict:
    return {"rule": rule, "subject": subject, "message": message, **numbers}


def by_role(anims: Dict[str, pdx_deform.Animation]) -> Dict[str, str]:
    return {clip.rsplit("_", 1)[-1]: clip for clip in anims}


def pose_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation]) -> Tuple[List[dict], dict]:
    """The pose rules: STRIKE-STILL and GAIT-ALIKE. Returns (findings, numbers)."""

    roles = by_role(anims)
    pose = D.ScreenPose(mesh)
    frames = {role: pose.frames(anims[clip]) for role, clip in roles.items() if role in ("idle", "move", "attack", "retreat")}
    findings: List[dict] = []
    numbers: dict = {"end_joints": [mesh.bones[i] for i in pose.joints]}
    if "attack" in frames:
        clip = roles["attack"]
        spread, held = D.spread(frames["attack"]), D.held_share(frames["attack"])  # held: reported, not judged (see the calibration)
        numbers["attack"] = {"spread": spread, "held": held}
        if spread < MIN_ATTACK_SPREAD:
            findings.append(_finding("TRIPO-DESIGNER-STRIKE-STILL", clip,
                                     f"at the designer's size the attack's frames barely differ: its end joints move {spread:.3f} of the height at most "
                                     f"between two frames (at least {MIN_ATTACK_SPREAD}, every attack reviewers passed moved 0.149 or more): make "
                                     "a strike with a clear wind-up and blow", share=spread, limit=MIN_ATTACK_SPREAD))
    if "move" in frames and "retreat" in frames:
        alike = max(D.alike_share(frames["move"], frames["retreat"]), D.alike_share(frames["retreat"], frames["move"]))
        numbers["gait_alike"] = alike
        if alike > MAX_GAIT_ALIKE:
            findings.append(_finding("TRIPO-DESIGNER-GAIT-ALIKE", roles["retreat"],
                                     f"at the designer's size {alike:.0%} of the move's or the retreat's frames show a pose of the other (at most "
                                     f"{MAX_GAIT_ALIKE:.0%}): the retreat reads as the move. Give the retreat its own gait (a run, a flight "
                                     "looking back)", share=alike, limit=MAX_GAIT_ALIKE))
    return findings, numbers


def held_mask(mesh: pdx_deform.SkinnedMesh, bone: str):
    """The vertices of a held part's bone (a weapon, a shield), or None when the unit has no such bone."""

    if not bone or bone not in mesh.bones:
        return None
    return D.bone_vertices(mesh, (bone.lower(),))


def silhouette_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation], entity_scale: float,
                        weapon_bone: str = "", shield_bone: str = "") -> Tuple[List[dict], dict]:
    """The silhouette rule HEAD-HIDDEN, and the death's end (solidity, weapon gap) reported for later calibration. Returns (findings, numbers)."""

    roles = by_role(anims)
    camera = D.DesignerCamera(mesh, entity_scale)
    findings: List[dict] = []
    numbers: dict = {"entity_scale": entity_scale, "height_px": round(camera.height_px, 1)}
    if "death" in roles:
        clip = roles["death"]
        end = D.death_end(camera, anims[clip], held_mask(mesh, weapon_bone))
        numbers["death_end"] = dict(end, judged=False)
    numbers["head_hidden"] = {}
    for role, clip in roles.items():
        if role == "death":
            continue
        anim = anims[clip]
        # the held weapon may pass the face in the blow, and a shield may be raised before it in the guard
        allowed = {"attack": held_mask(mesh, weapon_bone), "defend": held_mask(mesh, shield_bone)}.get(role)
        shares = D.head_hidden(camera, anim, step=1, exclude=allowed)
        run = longest = 0
        for share in shares:
            run = run + 1 if share > HEAD_HIDDEN_SHARE else 0
            longest = max(longest, run)
        seconds = round(longest / max(anim.fps, 1e-9), 3)
        numbers["head_hidden"][clip] = {"worst": max(shares) if shares else 0.0, "longest_seconds": seconds}
        if seconds > MAX_HEAD_HIDDEN_SECONDS:
            findings.append(_finding("TRIPO-DESIGNER-HEAD-HIDDEN", clip,
                                     f"at the designer's size more than half of the head is hidden behind a nearer part for {seconds:.2f} s running "
                                     f"(at most {MAX_HEAD_HIDDEN_SECONDS} s): a wing, a limb or the weapon covers the head", share=seconds,
                                     limit=MAX_HEAD_HIDDEN_SECONDS))
    return findings, numbers


def designer_findings(mesh: pdx_deform.SkinnedMesh, anims: Dict[str, pdx_deform.Animation], entity_scale: Optional[float],
                      weapon_bone: str = "", shield_bone: str = "") -> Tuple[List[dict], dict]:
    """Every designer rule. Without an entity scale the silhouette rules cannot run, and the numbers say so."""

    findings, numbers = pose_findings(mesh, anims)
    result = {"pose": numbers}
    if entity_scale:
        found, result["silhouette"] = silhouette_findings(mesh, anims, entity_scale, weapon_bone, shield_bone)
        findings += found
    else:
        result["silhouette"] = "not run: no entity scale (give the job's runtime_entity_scale or --entity-scale)"
    return findings, result


def job_entity_scale(jobs_config: Optional[Path], slug: Optional[str]) -> Optional[float]:
    if not jobs_config or not slug:
        return None
    job = json.loads(Path(jobs_config).read_text(encoding="utf-8")).get("jobs", {}).get(slug) or {}
    scale = job.get("runtime_entity_scale", (job.get("vanilla_scale_reference") or {}).get("entity_scale"))
    return float(scale) if scale else None


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--entity-scale", type=float)
    parser.add_argument("--jobs-config", type=Path)
    parser.add_argument("--slug")
    parser.add_argument("--weapon-bone", default="")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    meshes = sorted(args.folder.glob("*.mesh"))
    if len(meshes) != 1:
        print(f"designer checks: expected one .mesh in {args.folder}, found {len(meshes)}")
        return 2
    mesh = pdx_deform.load_mesh(meshes[0])
    anims = {path.stem: pdx_deform.load_anim(path) for path in sorted(args.folder.glob(f"{meshes[0].stem}_*.anim"))}
    scale = args.entity_scale or job_entity_scale(args.jobs_config, args.slug)
    findings, numbers = designer_findings(mesh, anims, scale, args.weapon_bone)
    if args.json:
        args.json.write_text(json.dumps({"findings": findings, "numbers": numbers}, indent=1) + "\n", encoding="utf-8", newline="\n")
    for item in findings:
        print(f"{item['rule']} [{item['subject']}] {item['message']}")
    print(f"{len(findings)} designer finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
