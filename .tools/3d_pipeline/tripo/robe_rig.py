"""Re-rig a robed humanoid whose legs the robe hides, when Tripo's auto-rig misplaced its skeleton, free and without Blender.

    py -3.13 -B .tools/3d_pipeline/tripo/robe_rig.py <rigged.glb> --out <re-rigged.glb> [--json report.json]

Run it when `tripo/rig_check.py` fails on a unit in a floor-length robe, or when its joints plainly sit off the body (the Haiku mage
Elzon: hips at 0.90 of the height, the robe's skirt bound to toes at 0.62). The rules are in `lib/tripo_robe_rig.py`: the joints are
placed again from the mesh (neck, shoulders, the arms standing out from the robe, the hidden legs by proportion), the skin is weighted
again by rule, and the export's own clips are moved onto the new joints (`lib/clip_transfer.py`). Then run `rig_check.py` and
`clip_check.py` on the output: both must pass. Clips from other exports of the same rig (a made clip) move onto it the same way:

    py -3.13 -B .tools/3d_pipeline/tripo/clip_transfer.py <export.glb> <re-rigged.glb> --out <export moved.glb>
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence

PIPELINE = Path(__file__).resolve().parents[1]
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

from lib import clip_transfer as C
from lib import tripo_robe_rig as R


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glb", type=Path, help="Tripo's rigged export")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    with tempfile.TemporaryDirectory() as folder:
        placed = Path(folder) / "placed.glb"
        try:
            report = R.robe_rig(args.glb, placed)
        except R.SeatError as error:
            print(f"robe rig: refused: {error}")
            return 2
        try:
            moved = C.transfer(args.glb, placed, args.out)
        except C.TransferError as error:
            print(f"robe rig: the clips could not move onto the new joints: {error}")
            return 2
    report["clips"] = moved["clips"]
    heights = report["heights"]
    print(f"robe rig: neck {heights['neck']:.2f}, shoulders {heights['shoulder']:.2f}, hips {heights['hips']:.2f}, knees {heights['knee']:.2f} "
          f"of the height; {report['joints_placed']} joints placed")
    for side, row in report["arms"].items():
        print(f"{side}: arm {row['vertices']} vertices, {row['length']:.3f} of the height from the shoulder to the tip")
    print(f"robe rig: wrote {args.out} with {len(moved['clips'])} clip(s) moved onto it. Now run tripo/rig_check.py and tripo/clip_check.py on it")
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
