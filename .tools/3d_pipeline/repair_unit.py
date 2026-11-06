"""Repair an exported unit's mesh for free in Blender: winding, fused body parts and small holes.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/repair_unit.py gfx/models/units/<unit> --out <job>/repair --repairs winding bridges

It copies the unit folder to `<out>/files`, repairs the `.mesh` there in Blender (see
`blender/repair_mesh.py`), and runs `check_unit_files.py` on the original and the repaired
copy. The skeleton, materials and every untouched vertex's weights are kept, so the unit's
`.anim` files still play. Nothing under `gfx/` changes: review the copy with `review_unit.py`
and copy it back only after an independent reviewer passes it.

Repairs:
- `winding`: make each surface face one way (fixes UNIT-WINDING and UNIT-INSIDE-OUT).
- `bridges`: delete faces that join far-apart body parts and cap both sides (fixes UNIT-BRIDGE
  and the stretch it causes).
- `holes`: close open loops of at most `--max-hole-edges` edges (UNIT-HOLE).
- `ground`: shift each clip's root translation keys so the lowest point meets the ground in every
  frame; a death clip is only lifted where it sinks (UNIT-ANIM-GROUND). Runs without Blender.
- `weights`: blend the existing weights across each weight seam (a bridge inside one continuous
  skin, which `bridges` keeps) and each leg seam (a crotch whose vertices follow one thigh each,
  UNIT-SEAM) over a few edge rings, then keep at most four influences per vertex and normalize.
  No weight is created for a bone a vertex was not already near.

The report `<out>/repair_report.json` lists what each repair changed and the rules before and after.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

import check_unit_files
from lib import pdx_deform, pdx_ground, pdx_motion
from review_unit import find_blender

BLENDER_SCRIPT = PIPELINE_ROOT / "blender" / "repair_mesh.py"
# A weight seam is blended over this many edge rings on each side, in this many smoothing passes.
SEAM_RINGS = 3
SEAM_PASSES = 4
MESH_REPAIRS = ("winding", "bridges", "holes", "weights")
REPAIRS = MESH_REPAIRS + ("ground",)


def rule_counts(folder: Path, stem: Optional[str], unit_type: Optional[dict]) -> dict:
    findings, _facts = check_unit_files.check_files(folder, unit_type, None, stem)
    return dict(Counter(f.rule for f in findings if f.severity == "error"))


def ground_clips(files: Path, mesh: Path, stem: Optional[str], stems: List[str]) -> dict:
    """Ground every clip of the unit in `files` in place; a death clip is only lifted where it sinks."""

    owner = mesh.stem
    results = {}
    for anim in sorted(files.glob("*.anim")):
        owners = [candidate for candidate in stems if anim.stem.startswith(candidate + "_")]
        if owners and max(owners, key=len) != owner:
            continue
        correction = pdx_ground.ground(mesh, anim, anim, death=anim.stem.endswith("_death"))
        results[anim.name] = {"root": correction.root, "shifted": correction.corrected,
                              "largest_shift": round(correction.largest_shift, 4), "note": correction.reason}
    return results


def leg_seam_pairs(mesh: Path) -> List[List[str]]:
    """The bone pairs of the mesh's hard leg seams (UNIT-SEAM), for the `weights` repair to blend."""

    try:
        report = pdx_motion.seam_edges(pdx_deform.load_mesh(mesh))
    except (OSError, ValueError, IndexError):
        return []
    return [pair.split("-", 1) for pair in report.pairs]


def repair(folder: Path, out: Path, repairs: List[str], stem: Optional[str], max_hole_edges: int, unit_type: Optional[dict]) -> dict:
    meshes = sorted(folder.glob("*.mesh"))
    mesh = next((m for m in meshes if m.stem == stem), meshes[0] if meshes else None)
    if mesh is None:
        raise SystemExit(f"no .mesh in {folder}")
    files = out / "files"
    if files.exists():
        shutil.rmtree(files)
    shutil.copytree(folder, files, ignore=shutil.ignore_patterns("review", "*.blend*"))
    mesh_repairs = [name for name in repairs if name in MESH_REPAIRS]
    blender_report: dict = {}
    if mesh_repairs:
        request = {
            "mesh": str(mesh.resolve()),
            "out": str((files / mesh.name).resolve()),
            "report": str((out / "blender_report.json").resolve()),
            "repairs": mesh_repairs,
            "hops": pdx_deform.BRIDGE_HOPS,
            "max_hole_edges": max_hole_edges,
            "seam_rings": SEAM_RINGS,
            "seam_passes": SEAM_PASSES,
            "leg_seam_pairs": leg_seam_pairs(mesh),
        }
        request_path = out / "repair_request.json"
        request_path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
        completed = subprocess.run(
            [str(find_blender()), "-b", "--python", str(BLENDER_SCRIPT), "--", str(request_path.resolve())],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        (out / "blender.log").write_text(completed.stdout[-20000:] + completed.stderr[-20000:], encoding="utf-8")
        if "REPAIR_DONE" not in completed.stdout:
            raise SystemExit(f"Blender did not finish the repair; see {out / 'blender.log'}")
        blender_report = json.loads((out / "blender_report.json").read_text(encoding="utf-8"))
    grounding = ground_clips(files, files / mesh.name, stem, [m.stem for m in meshes]) if "ground" in repairs else {}
    report = {
        "unit": mesh.stem,
        "repairs": repairs,
        "blender": blender_report,
        "ground": grounding,
        "rules_before": rule_counts(folder, stem, unit_type),
        "rules_after": rule_counts(files, stem, unit_type),
    }
    (out / "repair_report.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path, help="the folder that holds the unit's .mesh, .anim and .dds files")
    parser.add_argument("--out", type=Path, required=True, help="work folder for the repaired copy and reports (outside gfx/)")
    parser.add_argument("--repairs", nargs="+", choices=REPAIRS, default=["winding", "bridges"])
    parser.add_argument("--stem", help="repair only <stem>.mesh in a folder shared with another unit")
    parser.add_argument("--unit-type", help="a type from config/unit_types.json, for the checks' group and rider rule")
    parser.add_argument("--max-hole-edges", type=int, default=16)
    args = parser.parse_args(argv)
    unit_type = check_unit_files.load_unit_types().get(args.unit_type) if args.unit_type else None
    args.out.mkdir(parents=True, exist_ok=True)
    report = repair(args.folder, args.out, args.repairs, args.stem, args.max_hole_edges, unit_type)
    print(json.dumps({key: report[key] for key in ("rules_before", "rules_after")}, indent=1))
    print(f"Repaired copy in {args.out / 'files'}. Render it with review_unit.py for an independent review before copying it back.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
