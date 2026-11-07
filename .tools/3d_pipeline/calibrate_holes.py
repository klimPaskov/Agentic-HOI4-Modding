"""Measure vanilla's own culled-silhouette specks, to set the limit of `check_holes.py`.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/calibrate_holes.py "<HOI4 install>" --work <scratch folder>

Vanilla units are not free of holes either: a sleeve or a collar seen edge-on, or a strap seen from
behind, shows a few pixels of ground. This renders the two loose-part references, GER_infantry and
cavalry_horse, exactly the way `check_holes.py` renders a custom unit (same views, tile size and
frames, every clip the game plays on them, as the `.gfx` and `.asset` files register them) and
writes the largest cluster it found, overall and for death clips and every other clip apart (a body
lying on the ground shows larger specks from low views), with where each was found, to
`config/silhouette_calibration.json`. Rerun after a game update. Takes about half an hour in Blender
(GER_infantry alone plays 44 clips).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

import check_holes
from calibrate_deformation import LOOSE_REFERENCES, registered_clips

REFERENCES = LOOSE_REFERENCES


def measure(game: Path, work: Path, size: int, frames: int) -> Dict[str, Any]:
    clips = registered_clips(game)
    per_reference: Dict[str, Any] = {}
    largest: Dict[str, Any] = {"pixels": 0}
    by_kind: Dict[str, Dict[str, Any]] = {kind: {"pixels": 0} for kind in check_holes.KINDS}
    for name in REFERENCES:
        mesh_path = next((mesh for mesh in clips if mesh.name == name), None)
        if mesh_path is None:
            raise SystemExit(f"{name} is not registered with clips under {game / 'gfx'}")
        request_clips = check_holes.clips_for(mesh_path, clips[mesh_path], frames)
        results = check_holes.render(mesh_path, request_clips, work / mesh_path.stem, size, overlays=check_holes.OVERLAYS)
        rows = check_holes.ranked(results)
        top = rows[0]
        per_reference[name] = {
            "clips": len(request_clips),
            "renders": len(rows),
            "largest": top["largest"],
            "where": {"clip": top["clip"], "frame": top["frame"], "view": top["view"]},
            "renders_with_any": sum(1 for row in rows if row["largest"] > 0),
        }
        if top["largest"] > largest["pixels"]:
            largest = {"pixels": top["largest"], "mesh": name, "clip": top["clip"], "frame": top["frame"], "view": top["view"]}
        for row in rows:
            kind = check_holes.kind_of(row["clip"])
            if row["largest"] > by_kind[kind]["pixels"]:
                by_kind[kind] = {"pixels": row["largest"], "mesh": name, "clip": row["clip"], "frame": row["frame"], "view": row["view"]}
        check_holes.build_sheet(work / mesh_path.stem, rows[: check_holes.OVERLAYS], None)
    return {"largest": largest, "by_kind": by_kind, "references": per_reference}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("game", type=Path, help="the Hearts of Iron IV install folder")
    parser.add_argument("--work", type=Path, required=True, help="a scratch folder for the renders (outside the repository)")
    parser.add_argument("--out", type=Path, default=check_holes.CALIBRATION, help="the calibration file to write")
    args = parser.parse_args(argv)
    measured = measure(args.game.resolve(), args.work.resolve(), check_holes.SIZE, check_holes.FRAMES)
    payload = {
        "size": check_holes.SIZE,
        "frames": check_holes.FRAMES,
        "views": len(check_holes.VIEWS),
        "measured_on": f"vanilla {', '.join(REFERENCES)}, every registered clip, {date.today().isoformat()}",
        "method": "the largest 8-connected cluster of pixels that only back faces cover (rendered with and without back-face culling, Workbench, no anti-aliasing, orthographic camera at 1.45 times the rest pose's largest extent)",
        **measured,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"by_kind": {kind: row["pixels"] for kind, row in payload["by_kind"].items()}, "references": {name: row["largest"] for name, row in payload["references"].items()}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
