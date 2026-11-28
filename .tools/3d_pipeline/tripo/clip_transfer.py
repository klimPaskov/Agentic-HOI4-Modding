"""Move clips from a body Tripo rigs well onto a rig Tripo got wrong, by each bone's turn from rest (lib/clip_transfer.py).

    py -3.13 -B .tools/3d_pipeline/tripo/clip_transfer.py <source rigged.glb> <target rigged.glb> --out <out.glb> [--clips NAME ...]

Use it when Tripo's auto-rig cannot rig the unit's body well enough for its clips (the ZIN devil: five rigs, one usable after
`tripo/arm_seat.py`, and on it Tripo's idle and walk crossed the legs). Apply the unit's claimed clips on another asset whose Tripo rig is
clean (a plain humanoid), export it, and move them onto the repaired rig here. The clips stay claimed by the unit they are moved to: the
source only lends the motion. `--clips` takes exact names or the first words of a made clip. The output holds only the moved clips,
unless `--keep-target-clips` keeps the target's own clips beside them: then a clip made on the donor for one role (the goblin's death,
when the goblin's own Canvas page would not load) joins the unit's other clips in one file. Run
`tripo/rig_check.py` and `tripo/clip_check.py` on it as on any export, then the intake.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import clip_transfer as C


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="the export whose clips move (a body Tripo rigs well)")
    parser.add_argument("target", type=Path, help="the unit's own rigged export, repaired")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--clips", nargs="*", help="clip names or first words (default: every clip)")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--keep-target-clips", action="store_true",
                        help="keep the target's own clips and add the moved ones (a clip made on a motion donor for one role)")
    args = parser.parse_args(argv)
    try:
        report = C.transfer(args.source, args.target, args.out, args.clips, keep_target_clips=args.keep_target_clips)
    except C.TransferError as error:
        print(f"clip transfer: refused: {error}")
        return 2
    print(f"clip transfer: {len(report['clips'])} clip(s) moved onto {args.out.name}: {', '.join(report['clips'])} "
          f"({report['shared_joints']} shared joints, the target's own stance kept)")
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
