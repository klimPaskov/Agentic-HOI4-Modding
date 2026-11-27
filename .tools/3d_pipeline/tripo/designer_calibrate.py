"""Fit the designer preview's camera to an in-game screenshot of the division designer (D-140).

    py -3.13 -B .tools/3d_pipeline/tripo/designer_calibrate.py <screenshot.png> --frame X0 Y0 X1 Y1 --mesh <the .mesh the frame shows> \
        --entity-scale <its entity scale> --out <folder> [--azimuths -90 90 10] [--elevations 10 50 5]

The screenshot is the whole game screen with the designer open. `--frame` is the 249 pixel model frame's box on it (left, top, right,
bottom). `--mesh` is the model the frame shows, at the entity scale the game draws it. The tool renders the mesh's rest pose with the
review renderer at every azimuth and elevation of the grid (one Blender start), cuts each tile's silhouette, fits it onto the screenshot
model's box and scores the overlap. It prints the best view, the share of the frame the model fills in the game, and the frame's width in
game units that gives that fill (`designer_preview.FRAME_WORLD`), and writes `calibration.json` and an overlay picture (red the game, green
the render) to `--out`. Put the numbers into `lib/designer_preview.py` and the evidence into its `GAME_FILL`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(PIPELINE_ROOT / "tripo"))

import weapon_sheets
from lib import designer_preview, heavy_job

BACKGROUND_STEP = 40  # a screenshot pixel differs from the frame's dark background by more than this (sum of RGB) to count as the model
EDGE = 12  # pixels of the frame's own border left out of the screenshot mask


def game_mask(screenshot: Path, frame: Tuple[int, int, int, int]) -> np.ndarray:
    """The model's pixels inside the designer frame: those that differ from the frame's background (its median near the top and bottom)."""

    image = np.asarray(Image.open(screenshot).convert("RGB").crop(frame)).astype(int)
    inner = image[EDGE:-EDGE, EDGE:-EDGE]
    background = np.median(np.concatenate([inner[:20].reshape(-1, 3), inner[-20:].reshape(-1, 3)]), axis=0)
    mask = np.zeros(image.shape[:2], bool)
    mask[EDGE:-EDGE, EDGE:-EDGE] = np.abs(inner - background).sum(-1) > BACKGROUND_STEP
    return mask


def tile_mask(tile: Path) -> np.ndarray:
    """The rendered model's pixels: not the magenta world and not the ground disc."""

    pixels = np.asarray(Image.open(tile).convert("RGB")).astype(int)
    magenta = (pixels[..., 0] > 240) & (pixels[..., 1] < 15) & (pixels[..., 2] > 240)
    # the ground disc's flat colour: the commonest colour of the tile's bottom row that is not the magenta world (at a low camera a
    # corner can show the world, so a corner pixel is no sample)
    bottom = pixels[-2][~magenta[-2]]
    if not len(bottom):
        return ~magenta
    colours, counts = np.unique(bottom, axis=0, return_counts=True)
    ground = colours[np.argmax(counts)].astype(float)
    # the horizon's anti-aliased pixels blend the world and the ground: a pixel near the line between the two colours is background
    world = np.array([255.0, 0.0, 255.0])
    line = world - ground
    share = np.clip(((pixels - ground) @ line) / (line @ line), 0.0, 1.0)
    residual = np.abs(pixels - (ground + share[..., None] * line)).sum(-1)
    # blended in sRGB the horizon is not on that line, but it keeps the world's hue: red and blue alike and well above green
    tinted = (np.abs(pixels[..., 0] - pixels[..., 2]) < 20) & (pixels[..., 0] - pixels[..., 1] > 40)
    return without_specks(~magenta & ~tinted & (residual > 24))


def without_specks(mask: np.ndarray) -> np.ndarray:
    """The mask without pixels that have fewer than three set neighbours (the horizon's leftover dots)."""

    padded = np.pad(mask, 1).astype(int)
    neighbours = sum(np.roll(np.roll(padded, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)[1:-1, 1:-1]
    return mask & (neighbours >= 3)


def box(mask: np.ndarray) -> Tuple[int, int, int, int]:
    rows, cols = np.where(mask)
    return int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1


def fitted_overlap(game: np.ndarray, render: np.ndarray) -> Tuple[float, np.ndarray]:
    """The render's silhouette scaled uniformly and moved onto the game model's box, and its overlap (IoU) with the game's."""

    gx0, gy0, gx1, gy1 = box(game)
    rx0, ry0, rx1, ry1 = box(render)
    scale = ((gx1 - gx0) / (rx1 - rx0) + (gy1 - gy0) / (ry1 - ry0)) / 2
    crop = Image.fromarray((render[ry0:ry1, rx0:rx1] * 255).astype(np.uint8))
    size = (max(1, round((rx1 - rx0) * scale)), max(1, round((ry1 - ry0) * scale)))
    placed = np.zeros_like(game)
    small = np.asarray(crop.resize(size, Image.Resampling.NEAREST)) > 0
    h, w = min(small.shape[0], game.shape[0] - gy0), min(small.shape[1], game.shape[1] - gx0)
    placed[gy0:gy0 + h, gx0:gx0 + w] = small[:h, :w]
    return float((placed & game).sum() / max((placed | game).sum(), 1)), placed


def calibrate(screenshot: Path, frame: Tuple[int, int, int, int], mesh: Path, entity_scale: float, out: Path,
              azimuths: List[float], elevations: List[float]) -> Dict:
    game = game_mask(screenshot, frame)
    views = {f"a{a:g}_e{e:g}": [a, e] for a in azimuths for e in elevations}
    ortho = designer_preview.ortho_for(entity_scale)
    reference = weapon_sheets.reference_maps(mesh)
    index = weapon_sheets.render_tiles(mesh.parent, out, [], 1, list(views), views, designer_preview.PREVIEW_PX, 1.0, ortho=ortho,
                                       tiles_name="calibration_tiles", reference=reference)
    rest = next(c for c in index["clips"] if c["name"] == "rest")["rows"][0]["tiles"]
    scores = []
    for name, (azimuth, elevation) in views.items():
        render = tile_mask(out / "calibration_tiles" / rest[name])
        iou, _ = fitted_overlap(game, render)
        scores.append((iou, azimuth, elevation, name))
    scores.sort(reverse=True)
    iou, azimuth, elevation, name = scores[0]
    render = tile_mask(out / "calibration_tiles" / rest[name])
    _, placed = fitted_overlap(game, render)
    gx0, gy0, gx1, gy1 = box(game)
    rx0, ry0, rx1, ry1 = box(render)
    fill = ((gx1 - gx0) / designer_preview.PREVIEW_PX, (gy1 - gy0) / designer_preview.PREVIEW_PX)
    # the render is drawn with the frame `ortho` mesh units wide; the game shows the same model `fill[0]` of the frame wide
    frame_world = (rx1 - rx0) / designer_preview.PREVIEW_PX * ortho * entity_scale / fill[0]
    overlay = np.stack([game * 255, placed * 255, np.zeros_like(game, dtype=np.uint8)], -1).astype(np.uint8)
    Image.fromarray(overlay).resize((game.shape[1] * 2, game.shape[0] * 2), Image.Resampling.NEAREST).save(out / "calibration_overlay.png")
    result = {"screenshot": str(screenshot), "frame": list(frame), "mesh": str(mesh), "entity_scale": entity_scale,
              "game_pixels": [gx1 - gx0, gy1 - gy0], "fill": [round(fill[0], 3), round(fill[1], 3)],
              "view": [azimuth, elevation], "iou": round(iou, 3), "frame_world": round(frame_world, 4),
              "next_best": [{"view": [a, e], "iou": round(s, 3)} for s, a, e, _n in scores[1:6]]}
    (out / "calibration.json").write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    return result


def steps(values: List[float]) -> List[float]:
    start, stop, step = values
    return [float(v) for v in np.arange(start, stop + step / 2, step)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("screenshot", type=Path)
    parser.add_argument("--frame", type=int, nargs=4, required=True, metavar=("X0", "Y0", "X1", "Y1"))
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--entity-scale", type=float, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--azimuths", type=float, nargs=3, default=[-90.0, 90.0, 10.0], metavar=("FROM", "TO", "STEP"))
    parser.add_argument("--elevations", type=float, nargs=3, default=[10.0, 50.0, 5.0], metavar=("FROM", "TO", "STEP"))
    heavy_job.add_argument(parser)
    args = parser.parse_args()
    heavy_job.apply(args)
    result = calibrate(args.screenshot, tuple(args.frame), args.mesh.resolve(), args.entity_scale, args.out, steps(args.azimuths),
                       steps(args.elevations))
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
