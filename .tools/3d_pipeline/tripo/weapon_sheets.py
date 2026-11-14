"""Two extra review sheets for a unit with a held weapon: does the weapon pass through the body, and how does it read at game size.

    py -3.13 -B .tools/3d_pipeline/tripo/weapon_sheets.py <unit folder> --out <review folder> --sheet close
    py -3.13 -B .tools/3d_pipeline/tripo/weapon_sheets.py <unit folder> --out <review folder> --sheet game

`--sheet close` writes `sheets/weapon_frames.png`: every clip of the unit (one row each), three evenly
spaced frames (first, middle, last), a front three-quarter view at close-up size. `--sheet game` writes
`sheets/game_size.png` (and a 3x nearest-neighbour copy for reading): the idle and move clips, four
frames each, in the HOI4 map camera and the front view, scaled so the unit is about 60 px tall.
Each call is one Blender start (the review renderer), so a caller can gate them one by one.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
from PIL import Image, ImageDraw

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

import review_unit  # noqa: E402
from lib import pdx_deform  # noqa: E402

THREE_QUARTER = {"threequarter": [35, 8]}
CLOSE_SIZE, CLOSE_SHARE = 512, 1.15
GAME_SIZE, GAME_HEIGHT_PX = 160, 60
LABEL = 20


def evenly(frames: int, count: int) -> List[int]:
    last = max(frames - 1, 0)
    return sorted({round(last * k / max(count - 1, 1)) for k in range(count)})


def render_tiles(folder: Path, out: Path, wanted: List[str], count: int, views: List[str], angles: Dict, size: int, share: float) -> dict:
    meshes = sorted(folder.glob("*.mesh"))
    mesh_path = meshes[0]
    stems = [m.stem for m in meshes]
    clips = []
    for anim in review_unit.owned_anims(folder, mesh_path.stem, stems):
        role = anim.stem[len(mesh_path.stem) + 1 :]
        if wanted and role not in wanted:
            continue
        clips.append({"name": anim.stem, "path": str(anim.resolve()), "frames": evenly(pdx_deform.load_anim(anim).frames, count)})
    request = {
        "out": str((out / "weapon_tiles").resolve()),
        "mesh": str(mesh_path.resolve()),
        "diffuse": review_unit.diffuse_maps(mesh_path.resolve(), review_unit.gfx_texts(None)),
        "clips": clips,
        "views": views,
        "view_angles": angles,
        "ortho_share": share,
        "diagnostic_views": [],
        "size": size,
    }
    out.mkdir(parents=True, exist_ok=True)
    path = out / "weapon_request.json"
    path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    completed = subprocess.run(
        [str(review_unit.find_blender()), "-b", "--python", str(review_unit.BLENDER_SCRIPT), "--", str(path.resolve())],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if "REVIEW_RENDERED" not in completed.stdout:
        raise SystemExit("Blender did not finish the renders: " + (completed.stdout + completed.stderr)[-1500:])
    return json.loads((out / "weapon_tiles" / "index.json").read_text(encoding="utf-8"))


def unit_pixels(tile: Image.Image) -> tuple:
    """Bounding box of the lit unit: not the magenta world, not the dark ground disc (sampled in the corner)."""

    pixels = np.asarray(tile.convert("RGB")).astype(int)
    magenta = (pixels[..., 0] > 240) & (pixels[..., 1] < 15) & (pixels[..., 2] > 240)
    ground = np.abs(pixels - pixels[-3, 3]).sum(-1) < 12
    mask = ~magenta & ~ground
    rows, columns = np.where(mask)
    return (columns.min(), rows.min(), columns.max() + 1, rows.max() + 1) if len(rows) else (0, 0, tile.width, tile.height)


def sheet(index: dict, tiles: Path, views: List[str], clip_names: List[str], title_of, scale=None) -> Image.Image:
    rows = []
    for name in clip_names:
        clip = next(c for c in index["clips"] if c["name"] == name)
        rows.append((name, clip["rows"]))
    first = Image.open(tiles / rows[0][1][0]["tiles"][views[0]])
    width, height = first.size
    per_row = max(len(r[1]) * len(views) for r in rows)
    image = Image.new("RGB", (width * per_row, (height + LABEL) * len(rows)), (30, 30, 30))
    draw = ImageDraw.Draw(image)
    for r, (name, frames) in enumerate(rows):
        c = 0
        for entry in frames:
            for view in views:
                tile = Image.open(tiles / entry["tiles"][view]).convert("RGB")
                image.paste(tile, (c * width, r * (height + LABEL) + LABEL))
                draw.text((c * width + 4, r * (height + LABEL) + 4), title_of(name, entry["frame"], view), fill=(255, 255, 255))
                c += 1
    return image


def close_sheet(folder: Path, out: Path) -> Path:
    index = render_tiles(folder, out, [], 3, ["threequarter"], THREE_QUARTER, CLOSE_SIZE, CLOSE_SHARE)
    names = [c["name"] for c in index["clips"] if c["name"] != "rest"]
    image = sheet(index, out / "weapon_tiles", ["threequarter"], names, lambda n, f, v: f"{n.split('_', 1)[-1] if '_' in n else n} frame {f}")
    target = out / "sheets" / "weapon_frames.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    return target


def game_sheet(folder: Path, out: Path) -> Path:
    index = render_tiles(folder, out, ["idle", "move"], 4, ["hoi4", "front"], {}, GAME_SIZE, 1.45)
    tiles = out / "weapon_tiles"
    names = [c["name"] for c in index["clips"] if c["name"] != "rest"]
    # Scale every tile by one factor so the unit in the front view is GAME_HEIGHT_PX tall.
    probe = next(Image.open(tiles / row["tiles"]["front"]) for c in index["clips"] if c["name"] in names for row in c["rows"][:1])
    left, top, right, bottom = unit_pixels(probe)
    factor = GAME_HEIGHT_PX / max(bottom - top, 1)
    small = max(1, round(GAME_SIZE * factor))
    for clip in index["clips"]:
        for row in clip["rows"]:
            for view, name in row["tiles"].items():
                path = tiles / name
                Image.open(path).convert("RGB").resize((small, small), Image.Resampling.LANCZOS).save(path)
    image = sheet(index, tiles, ["hoi4", "front"], names, lambda n, f, v: f"{n.split('_', 1)[-1]} {f} {v}")
    target = out / "sheets" / "game_size.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    image.resize((image.width * 3, image.height * 3), Image.Resampling.NEAREST).save(out / "sheets" / "game_size_x3.png")
    print(f"unit height in the front view: {bottom - top} px at {GAME_SIZE} px, scaled by {factor:.3f} to {GAME_HEIGHT_PX} px (tile {small} px)")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sheet", choices=("close", "game"), required=True)
    args = parser.parse_args()
    target = close_sheet(args.folder, args.out) if args.sheet == "close" else game_sheet(args.folder, args.out)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
