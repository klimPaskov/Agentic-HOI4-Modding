"""TRIPO-SPAN-PICTURE (tripo/span_check.py): the model's width over height against the 3D-ready picture's subject. No Blender."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tripo"))

import span_check as S


def picture(path: Path, width: int, height: int, transparent: bool) -> None:
    from PIL import Image

    canvas = np.zeros((400, 600, 4), np.uint8)
    canvas[..., :3] = 225
    canvas[..., 3] = 0 if transparent else 255
    top, left = (400 - height) // 2, (600 - width) // 2
    canvas[top:top + height, left:left + width] = (120, 30, 20, 255)
    Image.fromarray(canvas).save(path)


class SpanCheck(unittest.TestCase):
    def test_the_subject_is_found_on_a_light_and_a_transparent_background(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            for transparent in (False, True):
                path = Path(folder) / f"p{int(transparent)}.png"
                picture(path, 450, 150, transparent)
                ratio, pixels = S.picture_ratio(path)
                self.assertAlmostEqual(ratio, 3.0, delta=0.05)

    def test_a_model_with_shorter_wings_fails_and_a_matching_one_passes(self) -> None:
        wide = np.array([[-1.5, 0.0, 0.0], [1.5, 1.0, 0.1]])
        short = np.array([[-1.2, 0.0, 0.0], [1.2, 1.0, 0.1]])
        self.assertEqual(S.span_verdict(3.0, S.model_ratio(wide))["verdict"], "pass")
        failed = S.span_verdict(3.0, S.model_ratio(short))
        self.assertEqual(failed["verdict"], "fail")
        self.assertEqual(failed["findings"][0]["rule"], "TRIPO-SPAN-PICTURE")


if __name__ == "__main__":
    unittest.main()
