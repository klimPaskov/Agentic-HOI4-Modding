"""A sheet of a unit's effects as the review renderer draws them: each clip that fires one, at the frames around each event.

    py -3.13 -B .tools/3d_pipeline/tripo/effects_sheet.py <unit files folder> --out <sheet.png> [--views front left] [--size 320]

The folder holds `<stem>.mesh`, its clips and `<stem>_effects.json` (tripo/effects_stage.py). For each clip that fires a particle the
sheet has one row per view, with the frame before the first event, each event's frame and the frames 2, 6 and 15 after it. The
particles are stand-ins (lib/unit_effects.py's plan, drawn by blender/review_render.py), and every tile that shows one is stamped
"particles: stand-in": look that each effect starts at its locator on its frame and stays on its part. Only the game shows the real
particles (docs/3d-effects.md lists the in-game checks).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import clip_sheet
import review_unit
from lib import heavy_job, pdx_deform, unit_effects

AFTER = (2, 6, 15)  # frames after an event that the sheet shows


def event_frames(plan: Dict, folder: Path) -> Dict[str, List[int]]:
    """clip -> the anim frames to render (0-based)."""

    out: Dict[str, List[int]] = {}
    for event in plan["events"]:
        clip = folder / f"{event['clip']}.anim"
        if not clip.is_file():
            continue
        last = max(pdx_deform.load_anim(clip).frames - 1, 0)
        wanted = {event["frame"] - 3, event["frame"], *(event["frame"] + k for k in AFTER)}
        out.setdefault(event["clip"], [])
        out[event["clip"]] = sorted(set(out[event["clip"]]) | {min(max(f, 0), last) for f in wanted})
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--views", nargs="+", default=["front", "left"])
    parser.add_argument("--size", type=int, default=320)
    parser.add_argument("--share", type=float, default=1.45)
    args = parser.parse_args(argv)
    folder = args.folder.resolve()
    mesh_path = sorted(folder.glob("*.mesh"))[0]
    plan = unit_effects.read_plan(folder, mesh_path.stem)
    if plan is None:
        raise SystemExit(f"no {mesh_path.stem}{unit_effects.PLAN_SUFFIX} in {folder}: run tripo/effects_stage.py first")
    frames = event_frames(plan, folder)
    work = args.out.resolve().parent / (args.out.stem + "_tiles")
    clips = [{"name": name, "path": str((folder / f"{name}.anim").resolve()), "frames": [f + 1 for f in picks]}  # Blender frame 1 is frame 0
             for name, picks in frames.items()]
    request = {
        "out": str((work / "weapon_tiles").resolve()), "mesh": str(mesh_path.resolve()),
        "diffuse": review_unit.diffuse_maps(mesh_path.resolve(), review_unit.gfx_texts(None)),
        "specular": review_unit.specular_maps(mesh_path.resolve()), "pbr": True, "clips": clips, "views": args.views,
        "view_angles": {}, "ortho_share": args.share, "diagnostic_views": [], "size": args.size,
    }
    work.mkdir(parents=True, exist_ok=True)
    path = work / "effects_request.json"
    path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    done = heavy_job.run([str(review_unit.find_blender()), "-b", "--python", str(review_unit.BLENDER_SCRIPT), "--", str(path.resolve())],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if "REVIEW_RENDERED" not in done.stdout:
        raise SystemExit("Blender did not finish the renders: " + (done.stdout + done.stderr)[-1500:])
    index = json.loads((work / "weapon_tiles" / "index.json").read_text(encoding="utf-8"))
    labels = {}
    for name in frames:
        fired = sorted({f"{e['particle']} @{e['node']} f{e['frame']}" for e in plan["events"] if e["clip"] == name})
        labels[name[len(mesh_path.stem) + 1:]] = "; ".join(fired)
    image = clip_sheet.compose(index, work / "weapon_tiles", args.views, list(frames), mesh_path.stem, labels)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.out)
    stamped = sum(1 for clip in index["clips"] for row in clip["rows"] if row.get("standin"))
    print(f"{args.out} ({stamped} stamped frames)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
