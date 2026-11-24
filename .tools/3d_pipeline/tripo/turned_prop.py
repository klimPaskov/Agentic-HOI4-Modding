"""Build a spear, lance, pike, pole or staff from one side-view picture, for free (lib/turned_prop.py).

    py -3.13 -B .tools/3d_pipeline/tripo/turned_prop.py <picture.png> --length 3.0 --out <weapon.glb> [--report report.json]

The picture shows the prop alone, straight, full length, from the side, on a plain background. The model keeps the picture's outline
and texture exactly: round where the picture shows a shaft, grip, socket, langets or cap, a flat leaf where it shows a blade. `--length`
is the real length (metres): the grip stage scales the weapon to the body anyway, so it matters only for the report. The GLB goes to the
grip stage (`grip_weapon.py <body.glb> <weapon.glb>`) like a Tripo weapon model. Use this instead of a paid Tripo model for any
straight polearm; a curved or branching weapon (an axe, a sword with a guard, a bow) needs Tripo.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import turned_prop


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("picture", type=Path)
    parser.add_argument("--length", type=float, default=3.0, help="the prop's real length in metres (a demi-lance is about 3)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    profile = turned_prop.measure(args.picture)
    mesh = turned_prop.build(profile, args.length)
    turned_prop.write_glb(args.out, mesh, turned_prop.filled_texture(profile), args.out.stem)
    report = {
        "picture": str(args.picture), "length": args.length, "length_px": round(profile.length_px, 1),
        "shaft_width_px": round(profile.shaft_width, 2), "slenderness": round(profile.length_px / max(profile.shaft_width, 1e-9), 1),
        "blade_share": round(mesh["blade_share"], 4), "head_at_picture_right": profile.head_at_end,
        "vertices": int(len(mesh["positions"])), "triangles": int(len(mesh["triangles"])), "out": str(args.out),
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
