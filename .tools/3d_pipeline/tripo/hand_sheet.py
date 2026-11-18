"""Join the renders of `hand_views.py` into one sheet: a row per pose, a column per view, each labelled.

    py -3.13 hand_sheet.py <folder with <pose>_<view>.png> --out hand_close_up.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

VIEWS = ("back_of_hand", "palm_side", "thumb_side", "little_finger_side", "three_quarter")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    poses = sorted({path.name[: -len(view) - 5] for path in args.folder.glob("*.png") for view in VIEWS if path.name.endswith(f"_{view}.png")})
    if not poses:
        raise SystemExit(f"No hand renders in {args.folder}")
    first = Image.open(next(args.folder.glob("*.png")))
    width, height = first.size
    label = 22
    sheet = Image.new("RGB", (width * len(VIEWS), (height + label) * len(poses)), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    for row, pose in enumerate(poses):
        for column, view in enumerate(VIEWS):
            path = args.folder / f"{pose}_{view}.png"
            if path.exists():
                sheet.paste(Image.open(path).convert("RGB"), (column * width, row * (height + label) + label))
            draw.text((column * width + 6, row * (height + label) + 5), f"{pose} | {view.replace('_', ' ')}", fill=(235, 235, 235))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
