"""Find the holes a player sees: pixels only back faces cover, in the rest pose and every clip, against vanilla's own.

Usage (from the repository root):

    py -3.13 -B .tools/3d_pipeline/check_holes.py gfx/models/units/<unit> --out <job folder>/evidence/holes
    py -3.13 -B .tools/3d_pipeline/check_holes.py <job folder>/provider/downloads/generation_model.glb --out <job folder>/evidence/holes

The game culls back faces, so a missing face, a face turned the wrong way or a one-sided sheet seen from
behind shows the ground through the unit. Counting open edges does not tell those apart from the open
edges a smart-topology model keeps on its trims, plates and cloth, and raising that count per body type
is what let holes through before. This renders the unit with Blender (`blender/hole_render.py`) from 17
views (eight around it at 10 and 40 degrees up, and the HOI4 map camera), with and without back-face
culling, at the rest pose and at evenly spaced frames of every clip plus each clip's worst-stretch,
lowest and highest frames. The pixels only back faces cover are split into connected clusters. The unit
passes when its largest cluster is no larger than the largest one vanilla GER_infantry and cavalry_horse
show the same way (`config/silhouette_calibration.json`, written by `calibrate_holes.py`). A provider
`.glb` is checked at its rest pose, before the paid rig.

`sheets/holes_worst.png` shows the worst views: the unit grey, the holes red. When the unit fails, the
verdict names the free repair (`repair_unit.py --repairs winding holes`).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PIPELINE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import pdx_binary, pdx_deform, stage_verdict
from review_unit import find_blender, owned_anims, pick_frames

BLENDER_SCRIPT = PIPELINE_ROOT / "blender" / "hole_render.py"
CALIBRATION = PIPELINE_ROOT / "config" / "silhouette_calibration.json"
SIZE = 256
FRAMES = 3
OVERLAYS = 6
# Eight views around the unit at 10 and 40 degrees up, and the HOI4 map camera.
VIEWS = [[azimuth, elevation] for elevation in (10, 40) for azimuth in range(0, 360, 45)] + [[25, 55]]
RULE = "UNIT-HOLE-SILHOUETTE"


def clips_for(mesh_path: Path, anims: List[Path], frames: int = FRAMES) -> List[Dict[str, Any]]:
    """The request's clip list: each `.anim` with the frames to render."""

    mesh = pdx_deform.load_mesh(mesh_path)
    clips = []
    for anim in anims:
        try:
            clips.append({"name": anim.stem, "path": str(anim.resolve()), "frames": pick_frames(mesh, anim, frames)})
        except (pdx_binary.PdxFormatError, ValueError, IndexError):
            continue
    return clips


def unit_target(source: Path, stem: Optional[str] = None, frames: int = FRAMES) -> Tuple[Path, List[Dict[str, Any]]]:
    """The file to render and its clips: a unit folder's mesh and the clips it owns, or a `.glb` alone."""

    if not source.is_dir():
        return source, []
    meshes = sorted(source.glob("*.mesh"))
    mesh_path = next((m for m in meshes if m.stem == stem), None) if stem else (meshes[0] if meshes else None)
    if mesh_path is None:
        raise SystemExit(f"no {stem + '.mesh' if stem else '.mesh'} in {source}")
    return mesh_path, clips_for(mesh_path, owned_anims(source, mesh_path.stem, [m.stem for m in meshes]), frames)


def render(target: Path, clips: List[Dict[str, Any]], out: Path, size: int = SIZE, overlays: int = OVERLAYS) -> Dict[str, Any]:
    """Render the hole masks in Blender and return `holes.json`."""

    out.mkdir(parents=True, exist_ok=True)
    request = {"source": str(target.resolve()), "out": str(out.resolve()), "size": size, "views": VIEWS, "clips": clips, "overlays": overlays}
    request_path = out / "holes_request.json"
    request_path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    completed = subprocess.run(
        [str(find_blender()), "-b", "--python", str(BLENDER_SCRIPT), "--", str(request_path.resolve())],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    (out / "blender.log").write_text(completed.stdout[-20000:] + completed.stderr[-20000:], encoding="utf-8")
    if "HOLES_RENDERED" not in completed.stdout:
        raise SystemExit(f"Blender did not finish the hole renders; see {out / 'blender.log'}")
    (out / "_tile.png").unlink(missing_ok=True)
    return json.loads((out / "holes.json").read_text(encoding="utf-8"))


def ranked(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    return sorted(results["results"], key=lambda row: -row["largest"])


def build_sheet(out: Path, rows: List[Dict[str, Any]], limit: Optional[float]) -> Optional[Path]:
    """The worst views' overlay tiles in one row, each labelled with its cluster size."""

    from PIL import Image, ImageDraw

    tiles = [row for row in rows if row.get("tile") and (out / row["tile"]).exists()]
    if not tiles:
        return None
    width, height = Image.open(out / tiles[0]["tile"]).size
    label = 30
    sheet = Image.new("RGB", (width * len(tiles), height + label), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    for column, row in enumerate(tiles):
        with Image.open(out / row["tile"]) as tile:
            sheet.paste(tile.convert("RGB"), (column * width, label))
        bound = f" / {limit:.0f}" if limit is not None else ""
        draw.text((column * width + 4, 2), f"{row['clip']} f{row['frame']}", fill=(230, 230, 230))
        draw.text((column * width + 4, 15), f"view {row['view'][0]}/{row['view'][1]}: {row['largest']}{bound} px", fill=(230, 230, 230))
    path = out / "sheets" / "holes_worst.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return path


def load_limit(size: int, path: Path = CALIBRATION) -> Optional[Dict[str, Any]]:
    """Vanilla's largest cluster, scaled from the calibration's tile size to `size` (area scales with the square)."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    scale = (size / float(data["size"])) ** 2
    return {**data["largest"], "pixels": float(data["largest"]["pixels"]) * scale, "size": size}


def judge(results: Dict[str, Any], limit: Optional[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, str]]]:
    """Pass when the largest cluster in any view and frame is within vanilla's largest."""

    if limit is None:
        return False, [{"rule": "UNIT-HOLE-CALIBRATION-MISSING", "file": CALIBRATION.name, "message": "run calibrate_holes.py on the HOI4 install first"}]
    rows = ranked(results)
    if not rows or rows[0]["largest"] <= limit["pixels"]:
        return True, []
    row = rows[0]
    over = sum(1 for item in rows if item["largest"] > limit["pixels"])
    message = (
        f"{row['largest']} px of holes in one cluster ({row['clip']} frame {row['frame']}, view {row['view'][0]} degrees around and "
        f"{row['view'][1]} up); vanilla's largest is {limit['pixels']:.0f} px at this size. {over} of {len(rows)} renders are over."
    )
    return False, [{"rule": RULE, "file": Path(results["source"]).name, "message": message}]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="an exported unit folder, or a provider .glb (rest pose only)")
    parser.add_argument("--out", type=Path, required=True, help="where the results, the sheet and the verdict go (outside gfx/)")
    parser.add_argument("--stem", help="check only <stem>.mesh in a folder shared with another unit")
    parser.add_argument("--unit-type", help="passed on to the repair command the verdict names")
    parser.add_argument("--frames", type=int, default=FRAMES, help="evenly spaced frames per clip, before the worst-stretch, lowest and highest frames are added")
    parser.add_argument("--size", type=int, default=SIZE, help="tile size in pixels; the vanilla limit is scaled to it")
    args = parser.parse_args(argv)
    source, out = args.source.resolve(), args.out.resolve()
    target, clips = unit_target(source, args.stem, args.frames)
    results = render(target, clips, out, args.size)
    limit = load_limit(args.size)
    ok, findings = judge(results, limit)
    rows = ranked(results)
    sheet = build_sheet(out, rows[:OVERLAYS], limit["pixels"] if limit else None)
    unit = target.stem
    worst = {key: value for key, value in rows[0].items() if key != "tile"} if rows else None
    outputs = {"worst": worst, "limit_px": round(limit["pixels"], 1) if limit else None, "renders": len(rows), "clips": len(clips), "results": (out / "holes.json").as_posix()}
    steps: List[str] = []
    stem_arg = f" --stem {args.stem}" if args.stem else ""
    if ok and source.is_dir():
        steps = [f"{stage_verdict.PY} {stage_verdict.PIPELINE}/review_unit.py {stage_verdict.quote(args.source.as_posix())}{stem_arg} --out {stage_verdict.quote(args.out.parent.as_posix() + '/review')}"]
    elif ok:
        steps = ["No hole shows: continue the job (rig and animations)."]
    if not ok and findings[0]["rule"] == RULE:
        if source.is_dir():
            steps, _escalation = stage_verdict.next_for_findings([RULE], args.source.as_posix(), args.out.as_posix(), args.stem, args.unit_type)
            steps.append(f"{stage_verdict.PY} {stage_verdict.PIPELINE}/check_holes.py {stage_verdict.quote(args.out.as_posix() + '/repair/files')}{stem_arg} --out {stage_verdict.quote(args.out.as_posix() + '/after_repair')}")
            steps.append("Holes left after the repair need the faces rebuilt by hand in Blender, or a new generation.")
        else:
            steps = ["Close the holes before paying for the rig: rebuild the faces in Blender, or generate again."]
    payload = stage_verdict.verdict("holes", ok, unit, outputs=outputs, sheets=[sheet.as_posix()] if sheet else [], findings=findings, next_steps=steps)
    stage_verdict.write(payload, out / "verdict.json")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
