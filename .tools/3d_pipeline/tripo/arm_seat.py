"""Repair a winged humanoid's export whose arm chain Tripo put outside the arms (TRIPO-RIG-ARMS), free and without Blender.

    py -3.13 -B .tools/3d_pipeline/tripo/arm_seat.py <rigged.glb> --out <repaired.glb> [--json report.json]

Run it when `tripo/rig_check.py` fails on a winged unit, then run `rig_check.py` on the repaired file: it must pass. The rules are in
`lib/tripo_arm_seat.py`: the arm is found in front of the wing's plane, the upper arm, forearm and hand joints move onto it (positions only,
so the clips keep their rotations), and the wing skin goes to the shoulder joint, where the route's wing chains take it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import tripo_arm_seat as S


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glb", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    try:
        report = S.seat_arms(args.glb, args.out)
    except S.SeatError as error:
        print(f"arm seat: refused: {error}")
        return 2
    for side, row in report["sides"].items():
        print(f"{side}: arm {row['arm_vertices']} vertices, {row['arm_length']:.3f} long, wing {row['wing_vertices']} vertices to the shoulder")
    print(f"arm seat: wrote {args.out} ({report['translation_tracks_shifted']} translation tracks moved). Now run tripo/rig_check.py on it")
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
