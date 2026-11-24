"""Hold a clip's heading: the hips turn no more than a limit about the up axis from the clip's first frame (lib/hold_heading.py).

    py -3.13 -B .tools/3d_pipeline/tripo/hold_heading.py <rigged.glb> --out <out.glb> --clips NAME ... [--limit 20] [--spine]

Use it on a made retreat or move that turns the unit away from the camera. The game already turns the unit to its way of travel, and a
clip that turns 180 degrees shows a winged unit's spread wings across its body from the front (TRIPO-WING-FRONT). The lean, the bend and
the steps stay as they were. With `--spine` the spine is held too: in a made turn the shoulders lead the hips, and
the shoulders left turned against the held hips read as a wrung waist (TRIPO-WAIST-TWIST). Run it on the export before the intake, then check the clip with `tripo/clip_check.py` as usual.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import hold_heading as H


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="the rigged export")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--clips", nargs="+", required=True, help="clip names or first words")
    parser.add_argument("--limit", type=float, default=20.0, help="largest turn kept, in degrees (default 20)")
    parser.add_argument("--spine", action="store_true", help="hold the spine's bones too, so the shoulders do not lead the held hips")
    args = parser.parse_args(argv)
    try:
        report = H.hold(args.source, args.out, args.clips, args.limit, args.spine)
    except H.HeadingError as error:
        print(f"hold heading: refused: {error}")
        return 2
    for row in report:
        print(f"hold heading: {row['clip']}: turned up to {row['turned']:.0f} degrees, now within {row['limit']:g}"
              + (f" ({', '.join(f'{k} {v:g}' for k, v in row.get('joints', {}).items())})" if len(row.get('joints', {})) > 1 else "")
              + (f", shoulder line turned back up to {row['shoulder_line']:g}" if row.get('shoulder_line') else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
