"""A sheet of evenly spaced frames of chosen clips of a unit, from the review renderer (PBR by default).

    py -3.13 clip_sheet.py <unit folder> --roles death --frames 6 --views left --out death_six_frames_side.png
    py -3.13 clip_sheet.py <unit folder> --roles attack defend --labels "attack=lunge" "defend=classic" \\
        --frames 6 --views front left --out attack_compare.png

The unit folder holds the runtime `.mesh`, `.anim` and `.dds` files, so the tiles show the textures and the packed
specular the game gets (the checkpoint `.blend` this replaces lost its texture paths when a job folder moved). One row per
clip (`--labels ROLE=TEXT` renames a row), `--frames` columns per view, one Blender start (the review renderer).
`--studio` renders with Workbench's studio light instead.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import weapon_sheets


def compose(index: dict, tiles: Path, views, names, stem: str, labels: dict) -> Image.Image:
    """One row per clip and view, one column per frame; each row has a title bar, each tile its frame number."""

    from PIL import ImageDraw

    clips = {clip["name"]: clip for clip in index["clips"]}
    rows = [(name, view) for name in names for view in views]
    first = Image.open(tiles / clips[names[0]]["rows"][0]["tiles"][views[0]])
    width, height = first.size
    columns = max(len(clips[name]["rows"]) for name in names)
    bar = 22
    sheet = Image.new("RGB", (width * columns, (height + bar) * len(rows)), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    for r, (name, view) in enumerate(rows):
        role = name[len(stem) + 1 :]
        y = r * (height + bar)
        draw.text((6, y + 6), f"{labels.get(role, role)}  |  {view} view", fill=(255, 255, 180))
        for c, entry in enumerate(clips[name]["rows"]):
            sheet.paste(Image.open(tiles / entry["tiles"][view]).convert("RGB"), (c * width, y + bar))
            draw.text((c * width + 6, y + bar + 4), f"frame {entry['frame']}", fill=(255, 255, 255))
    return sheet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--roles", nargs="+", required=True)
    parser.add_argument("--labels", nargs="*", default=[], metavar="ROLE=TEXT")
    parser.add_argument("--frames", type=int, default=6)
    parser.add_argument("--views", nargs="+", default=["front", "left"])
    parser.add_argument("--size", type=int, default=320)
    parser.add_argument("--share", type=float, default=1.45, help="the frame is this many times the unit's largest extent")
    parser.add_argument("--studio", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    folder = args.folder.resolve()
    work = args.out.resolve().parent / (args.out.stem + "_tiles")
    labels = dict(item.split("=", 1) for item in args.labels)
    weapon_sheets.PBR = not args.studio
    index = weapon_sheets.render_tiles(folder, work, args.roles, args.frames, args.views, {}, args.size, args.share)
    tiles = work / "weapon_tiles"
    stem = sorted(folder.glob("*.mesh"))[0].stem
    names = [f"{stem}_{role}" for role in args.roles]
    image = compose(index, tiles, args.views, names, stem, labels)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
