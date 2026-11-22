"""One atlas for a GLB whose parts carry their own maps (lib/glb_atlas.py)."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np
from PIL import Image

from lib import glb_atlas, static_parts, texture_lineage


def box(low, high):
    (x0, y0, z0), (x1, y1, z1) = low, high
    p = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], dtype=float)
    t = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return p, t


def png(colour, size=64):
    buffer = io.BytesIO()
    Image.new("RGB", (size, size), colour).save(buffer, format="PNG")
    return buffer.getvalue()


def two_parts(folder: Path, uvs=None) -> Path:
    hull = box((0, 0, 0), (4, 2, 1))
    gun = box((4, 0.9, 0.4), (5, 1.1, 0.6))
    corners = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
    return static_parts.write_parts_glb([("hull", *hull), ("gun", *gun)], folder / "tank.glb",
                                        uvs=uvs or [corners, corners], image=[png((200, 30, 30)), png((30, 30, 200))])


def uv_of(glb: Path, mesh: int) -> np.ndarray:
    document, binary = texture_lineage._read_glb(glb)
    return glb_atlas._accessor(document, binary, document["meshes"][mesh]["primitives"][0]["attributes"]["TEXCOORD_0"])


class Pack(unittest.TestCase):
    def test_power_of_two_tiles_by_area_always_fit(self) -> None:
        sides = glb_atlas.tile_sides([60.0, 25.0, 10.0, 4.0, 1.0], 1024)
        self.assertEqual(sides[0], 512)
        self.assertLessEqual(sum(s * s for s in sides), 1024 * 1024)
        corners = glb_atlas.pack(sides, 1024)
        boxes = [(x, y, x + s, y + s) for (x, y), s in zip(corners, sides)]
        for i, a in enumerate(boxes):
            self.assertTrue(0 <= a[0] and a[2] <= 1024 and 0 <= a[1] and a[3] <= 1024)
            for b in boxes[i + 1:]:
                self.assertFalse(a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3], (a, b))


class Merge(unittest.TestCase):
    def test_one_map_is_left_alone(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            hull = box((0, 0, 0), (1, 1, 1))
            corners = np.zeros((8, 2))
            glb = static_parts.write_parts_glb([("hull", *hull)], Path(folder) / "one.glb", uvs=[corners], image=png((1, 2, 3)))
            self.assertIsNone(glb_atlas.merged_glb(glb, Path(folder) / "out.glb"))
            self.assertFalse((Path(folder) / "out.glb").exists())

    def test_each_part_keeps_its_own_colour_in_its_tile(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            glb = two_parts(Path(folder))
            out = Path(folder) / "atlas" / "tank.glb"
            receipt = glb_atlas.merged_glb(glb, out, side=256)
            self.assertEqual(receipt["materials"], 2)
            self.assertGreater(receipt["tiles"]["hull"]["side"], receipt["tiles"]["gun"]["side"])
            maps = texture_lineage.embedded_images(out)
            self.assertEqual(len(maps["diffuse"]), 1)
            atlas = np.asarray(Image.open(io.BytesIO(maps["diffuse"][0])).convert("RGB"))
            for mesh, colour in ((0, (200, 30, 30)), (1, (30, 30, 200))):
                uv = uv_of(out, mesh)
                self.assertTrue(((uv >= 0) & (uv <= 1)).all())
                for u, v in uv:
                    x, y = min(int(u * 256), 255), min(int(v * 256), 255)
                    self.assertEqual(tuple(atlas[y, x]), colour)
            parts = static_parts.glb_parts(out)
            self.assertEqual([name for name, _p, _t in parts], ["hull", "gun"])

    def test_a_repeating_uv_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            tiled = np.array([[0, 0], [2, 0], [2, 2], [0, 2], [0, 0], [2, 0], [2, 2], [0, 2]], dtype=float)
            corners = np.array([[0, 0], [1, 0], [1, 1], [0, 1]] * 2, dtype=float)
            glb = two_parts(Path(folder), uvs=[tiled, corners])
            with self.assertRaises(glb_atlas.AtlasError):
                glb_atlas.merged_glb(glb, Path(folder) / "out.glb", side=256)


if __name__ == "__main__":
    unittest.main()
