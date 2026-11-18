"""Does the review renderer itself make a unit look dark? Render two units at identical settings, lit and unlit, side by side.

    py -3.13 colour_compare.py render <unit.mesh> --label vanilla --light STUDIO --out DIR      (one Blender start)
    py -3.13 colour_compare.py render <unit.mesh> --label vanilla --light FLAT --out DIR
    py -3.13 colour_compare.py compose DIR --labels vanilla orc --out colour_compare.png         (no Blender)

`render` draws the rest pose of the mesh with `blender/review_render.py` (the same renderer, size and framing for
every call; its diffuse map is the one `review_unit.diffuse_maps` finds beside the mesh) in the front view and the
HOI4 map camera. `--light STUDIO` is the review renderer's lit look, `FLAT` shows the diffuse map alone, unlit.
`compose` joins the tiles (one row per light, one column per unit and view) and writes the mean brightness and
saturation (0 to 255) of the unit's own pixels under each tile, so a unit that comes out dark in the renderer
but not in its texture shows in the numbers.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

import review_unit

VIEWS = ["front", "hoi4"]
SIZE = 512
LABEL = 34


def render(mesh: Path, label: str, light: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    request = {
        "out": str((out / f"{label}_{light}").resolve()),
        "mesh": str(mesh.resolve()),
        "diffuse": review_unit.diffuse_maps(mesh.resolve(), review_unit.gfx_texts(None)),
        "clips": [],
        "views": VIEWS,
        "diagnostic_views": [],
        "size": SIZE,
        "light": light,
        "pbr": light == "PBR",  # the review renderer shades from the packed specular by default; the studio and flat rows are explicit
    }
    if light == "FLAT":
        request["exposure"] = 0.0  # unlit means the diffuse map as it is, with no exposure on top
    if light == "PBR":
        request.update(light="STUDIO", specular=specular_maps(mesh))
    path = out / f"{label}_{light}_request.json"
    path.write_text(json.dumps(request, indent=1), encoding="utf-8", newline="\n")
    completed = subprocess.run(
        [str(review_unit.find_blender()), "-b", "--python", str(review_unit.BLENDER_SCRIPT), "--", str(path.resolve())],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if "REVIEW_RENDERED" not in completed.stdout:
        raise SystemExit("Blender did not finish the renders: " + (completed.stdout + completed.stderr)[-1500:])
    print("rendered", request["out"], "diffuse", request["diffuse"])


def specular_maps(mesh: Path) -> dict:
    """The packed specular map beside the mesh (`<stem>_specular.dds`, `_spec.dds`, or any `*spec*.dds`)."""

    for pattern in (f"{mesh.stem}_specular.dds", f"{mesh.stem}_spec.dds", f"{mesh.stem}*spec*.dds", "*spec*.dds"):
        found = sorted(mesh.parent.glob(pattern))
        if found:
            return {"*": str(found[0])}
    return {}


def unit_pixels(image: Image.Image) -> np.ndarray:
    """The unit's pixels: not the magenta world, not the dark ground disc (sampled in the corner)."""

    pixels = np.asarray(image.convert("RGB")).astype(int)
    magenta = (pixels[..., 0] > 240) & (pixels[..., 1] < 15) & (pixels[..., 2] > 240)
    ground = np.abs(pixels - pixels[-3, 3]).sum(-1) < 12
    return pixels[~magenta & ~ground]


def numbers(image: Image.Image) -> tuple:
    pixels = unit_pixels(image)
    if not len(pixels):
        return 0.0, 0.0
    luma = float((0.299 * pixels[:, 0] + 0.587 * pixels[:, 1] + 0.114 * pixels[:, 2]).mean())
    hsv = np.asarray(Image.fromarray(pixels.astype(np.uint8)[None, :, :]).convert("HSV")).astype(float)[0]
    return luma, float(hsv[:, 1].mean())


def compose(folder: Path, labels, out: Path) -> dict:
    rows = [(light, title) for light, title in (("STUDIO", "lit, studio light (old)"), ("PBR", "lit, shaded from the packed PDX specular"), ("FLAT", "unlit, diffuse map only")) if (folder / f"{labels[0]}_{light}").exists()]
    width = SIZE
    sheet = Image.new("RGB", (width * len(labels) * len(VIEWS), (SIZE + LABEL) * len(rows)), (30, 30, 30))
    draw = ImageDraw.Draw(sheet)
    measured = {}
    for r, (light, title) in enumerate(rows):
        for c, label in enumerate(labels):
            for v, view in enumerate(VIEWS):
                tile = Image.open(folder / f"{label}_{light}" / f"rest_{0:04d}_{view}.png") if (folder / f"{label}_{light}" / f"rest_{0:04d}_{view}.png").exists() else None
                if tile is None:
                    candidates = sorted((folder / f"{label}_{light}").glob(f"rest_*_{view}.png"))
                    tile = Image.open(candidates[0])
                x, y = (c * len(VIEWS) + v) * width, r * (SIZE + LABEL)
                sheet.paste(tile.convert("RGB"), (x, y + LABEL))
                luma, sat = numbers(tile)
                measured[f"{label}/{light}/{view}"] = {"luma": round(luma, 1), "saturation": round(sat, 1)}
                draw.text((x + 6, y + 4), f"{label} | {title} | {view}", fill=(255, 255, 255))
                draw.text((x + 6, y + 18), f"unit pixels: brightness {luma:.0f}, saturation {sat:.0f}", fill=(255, 255, 160))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return measured


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("render")
    a.add_argument("mesh", type=Path)
    a.add_argument("--label", required=True)
    a.add_argument("--light", choices=["STUDIO", "FLAT", "PBR"], required=True)
    a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("compose")
    b.add_argument("folder", type=Path)
    b.add_argument("--labels", nargs="+", required=True)
    b.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "render":
        render(args.mesh, args.label, args.light, args.out)
    else:
        print(json.dumps(compose(args.folder, args.labels, args.out), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
