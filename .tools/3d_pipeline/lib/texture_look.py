"""Refuse a unit's diffuse map that differs from the generator's export only by a global colour transform (a tint, a filter, a recolour).

A model's look is decided by the picture it is generated from and by the generator's texture, never by a tint or filter laid over that
texture afterwards: when the look must change, the model is regenerated from a new picture. The check makes that rule hold on every run.

`global_transform` fits the run's map from the export's, pixel by pixel, with one 3 by 3 colour matrix and an offset (least squares on a
`SAMPLE_SIZE` square copy of both). A global transform (a channel scale, a hue shift, a desaturation, a brightness or contrast change) is
explained by that fit almost exactly, while the kit's own steps (resizing, packing) change nothing it can fit, and a local edit (paint on
one part) leaves most of its change in the residual. The map is refused when it changed (the RMS difference is at least `MIN_CHANGE` of
255) and the fit explains it (the residual is at most `MAX_RESIDUAL_SHARE` of the change). Plain numpy and Pillow.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
from PIL import Image

SAMPLE_SIZE = 256
MIN_CHANGE = 3.0  # RMS over the map in 0 to 255: under this the run's map is the export's (resampling and rounding)
MAX_RESIDUAL_SHARE = 0.35


def _pixels(path_or_image, size: int = SAMPLE_SIZE) -> np.ndarray:
    image = path_or_image if isinstance(path_or_image, Image.Image) else Image.open(path_or_image)
    rgb = image.convert("RGB").resize((size, size), Image.Resampling.BOX)
    return np.asarray(rgb, float).reshape(-1, 3)


def global_transform(source, run, size: int = SAMPLE_SIZE) -> Dict[str, float]:
    """How the run's map differs from the source's: the RMS change, the RMS left after the best colour matrix and offset, and the verdict."""

    a, b = _pixels(source, size), _pixels(run, size)
    change = float(np.sqrt(np.mean((b - a) ** 2)))
    design = np.concatenate([a, np.ones((len(a), 1))], axis=1)
    fit, *_ = np.linalg.lstsq(design, b, rcond=None)
    residual = float(np.sqrt(np.mean((design @ fit - b) ** 2)))
    recoloured = change >= MIN_CHANGE and residual <= MAX_RESIDUAL_SHARE * change
    return {"change": round(change, 3), "residual": round(residual, 3), "residual_share": round(residual / change, 3) if change > 0 else 0.0,
            "matrix": [[round(float(v), 4) for v in row] for row in fit.T], "recoloured": bool(recoloured),
            "limits": {"min_change": MIN_CHANGE, "max_residual_share": MAX_RESIDUAL_SHARE}}


def refusal(numbers: Dict[str, float]) -> Optional[str]:
    if not numbers["recoloured"]:
        return None
    return (f"the diffuse map differs from the generator's export by a global colour transform (RMS change {numbers['change']:.1f} of 255, "
            f"{numbers['residual_share']:.0%} of it left after one colour matrix and offset, at most {MAX_RESIDUAL_SHARE:.0%}): a model's look is "
            "never changed by a tint, filter or recolour over its texture. Regenerate the model from a new picture instead")
