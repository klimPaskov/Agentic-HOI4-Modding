"""Hips travel of a rigged GLB's clips (lib/glb_root.py), on small synthetic GLB files (no Blender)."""

from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np

from lib import glb_root


def write_glb(path: Path, clips: dict) -> None:
    """A GLB with a root node and its child `mixamorig:Hips` (rest 1 unit up) and one clip per entry of `clips`: name -> (frames, 3)
    hips translations."""

    blob = b""
    accessors, views, animations = [], [], []
    for name, values in clips.items():
        values = np.asarray(values, np.float32)
        times = np.linspace(0.0, 1.0, len(values), dtype=np.float32)
        refs = []
        for array, kind in ((times, "SCALAR"), (values, "VEC3")):
            data = array.tobytes()
            views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
            accessors.append({"bufferView": len(views) - 1, "componentType": 5126, "count": len(array), "type": kind})
            refs.append(len(accessors) - 1)
            blob += data
        animations.append({"name": name, "samplers": [{"input": refs[0], "output": refs[1]}],
                           "channels": [{"sampler": 0, "target": {"node": 1, "path": "translation"}}]})
    doc = {"asset": {"version": "2.0"}, "nodes": [{"name": "Armature", "children": [1]}, {"name": "mixamorig:Hips", "translation": [0.0, 1.0, 0.0]}],
           "buffers": [{"byteLength": len(blob)}], "bufferViews": views, "accessors": accessors, "animations": animations}
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    blob += b"\0" * (-len(blob) % 4)
    body = struct.pack("<I4s", len(text), b"JSON") + text + struct.pack("<I4s", len(blob), b"BIN\0") + blob
    path.write_bytes(struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body)


class RootTravel(unittest.TestCase):
    def test_a_clip_in_place_measures_its_bob_only_and_a_walk_its_travel(self) -> None:
        bob = [[0.0, 1.0 + 0.05 * np.sin(t), 0.0] for t in np.linspace(0, 6.28, 20)]
        walk = [[0.0, 1.0, 2.0 * t] for t in np.linspace(0, 1, 20)]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "u.glb"
            write_glb(path, {"idle": bob, "walk": walk})
            travel = glb_root.root_travel(path)
            travelling = glb_root.travelling_clips(path, ["idle", "walk"])
            only_idle = glb_root.travelling_clips(path, ["idle"])
        self.assertLess(travel["idle"], 0.01, "a vertical bob is not travel")
        self.assertAlmostEqual(travel["walk"], 2.0, places=3)
        self.assertEqual(list(travelling), ["walk"])
        self.assertEqual(only_idle, {}, "clips the job does not use are not judged")


if __name__ == "__main__":
    unittest.main()
