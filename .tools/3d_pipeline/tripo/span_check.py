"""Before the rig: does Tripo's model keep the picture's span? Compares the subject's width over its height in the 3D-ready picture with the
model's front-view width over its height.

    py -3.13 -B .tools/3d_pipeline/tripo/span_check.py <model .glb or .mesh> <3D-ready picture .png> [--json out.json]

Run it on the model's own export (Model page, Export, GLB: free) before you pay for the rig. A model whose wings, arms or tail came out
shorter than drawn reads as a smaller creature than the picture, and no later step brings the span back. TRIPO-SPAN-PICTURE fails when the
model's ratio is off the picture's by more than `MAX_SPAN_DIFFERENCE` of it either way. Then make the model again (another seed, or the
picture redrawn with more room round the subject), not the rig.

The picture's subject is every pixel that is not background: on a picture with transparency the opaque pixels, otherwise the pixels whose
colour is farther than `BACKGROUND_DISTANCE` from the median of the border. Its extent is taken between the 0.05th and 99.95th percentile
of those pixels on each axis, so a stray speck does not count. The model's front view is its extent across x (Tripo's models face +z with
y up, and the kit's `.mesh` files keep x across) over its extent along y.

Measured (2026-11-22): the bat-winged demon's picture reads 1.51 and its Tripo model 1.51. Reading files only: no Blender, no cost.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence, Tuple

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import body_measure

# The model's width over height may differ from the picture's by this share of it. A redraw's own spread between two pictures of one subject
# is a few percent; a wing a tenth shorter is a visibly smaller creature.
MAX_SPAN_DIFFERENCE = 0.1
BACKGROUND_DISTANCE = 40.0
EXTENT_PERCENTILES = (0.05, 99.95)


def subject_mask(rgba: np.ndarray) -> np.ndarray:
    """The subject's pixels of an RGBA picture (height, width, 4)."""

    rgba = np.asarray(rgba, float)
    if (rgba[..., 3] < 250).mean() > 0.05:
        return rgba[..., 3] > 128
    rgb = rgba[..., :3]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    return np.linalg.norm(rgb - np.median(border, axis=0), axis=-1) > BACKGROUND_DISTANCE


def picture_ratio(path: Path) -> Tuple[float, Tuple[float, float]]:
    """(width over height of the picture's subject, (width, height) in pixels)."""

    from PIL import Image

    mask = subject_mask(np.asarray(Image.open(path).convert("RGBA")))
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        raise ValueError(f"{path.name}: no subject found against the background")
    x0, x1 = np.percentile(xs, EXTENT_PERCENTILES)
    y0, y1 = np.percentile(ys, EXTENT_PERCENTILES)
    width, height = float(x1 - x0 + 1), float(y1 - y0 + 1)
    return width / height, (width, height)


def model_ratio(positions: np.ndarray) -> float:
    """Width across x over height along y."""

    extent = np.ptp(np.asarray(positions, float), axis=0)
    return float(extent[0] / max(extent[1], 1e-12))


def span_verdict(picture: float, model: float, limit: float = MAX_SPAN_DIFFERENCE) -> dict:
    share = model / picture
    finding = None
    if abs(share - 1.0) > limit:
        finding = {"rule": "TRIPO-SPAN-PICTURE", "message": f"the model is {share:.0%} as wide for its height as the picture's subject (allowed "
                   f"{1 - limit:.0%} to {1 + limit:.0%}): its wings, arms or tail are not as drawn. Make the model again, not the rig", "share": round(share, 3)}
    return {"picture_ratio": round(picture, 3), "model_ratio": round(model, 3), "share": round(share, 3), "verdict": "fail" if finding else "pass",
            "findings": [finding] if finding else []}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("model", type=Path, help="the model's .glb (or a .mesh)")
    parser.add_argument("picture", type=Path, help="the 3D-ready picture the model was made from")
    parser.add_argument("--json", type=Path, help="write the verdict here")
    args = parser.parse_args(argv)
    positions, _triangles = body_measure.load_surface(args.model)
    picture, pixels = picture_ratio(args.picture)
    result = span_verdict(picture, model_ratio(positions))
    result["picture_pixels"] = [round(v) for v in pixels]
    print(f"picture {result['picture_ratio']:.2f}, model {result['model_ratio']:.2f} (width over height): {result['share']:.0%} -> {result['verdict']}")
    for item in result["findings"]:
        print(f"  {item['rule']}: {item['message']}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
