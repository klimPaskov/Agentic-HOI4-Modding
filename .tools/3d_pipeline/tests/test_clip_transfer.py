"""Moving clips between rigs by each bone's turn from rest (lib/clip_transfer.py). The small rigged GLB of rig_glb.py, with a right thigh
added so the body has a frame. No Blender."""

from __future__ import annotations

import json
import math
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import rig_glb as RG
from lib import clip_transfer as C


def turned_copy(source: Path, target: Path, degrees: float) -> None:
    """The same GLB with its hips turned `degrees` about the up axis at rest: a body that faces another way."""

    data = source.read_bytes()
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    rest = data[20 + length:]
    for node in doc["nodes"]:
        if node.get("name") == "mixamorig:Hips":
            half = math.radians(degrees) / 2
            node["rotation"] = [0.0, math.sin(half), 0.0, math.cos(half)]
    text = json.dumps(doc).encode()
    text += b" " * (-len(text) % 4)
    target.write_bytes(b"glTF" + struct.pack("<II", 2, 12 + 8 + len(text) + len(rest)) + struct.pack("<I", len(text)) + b"JSON" + text + rest)


class Transfer(unittest.TestCase):
    def setUp(self) -> None:
        saved = list(RG.CHAIN)
        RG.CHAIN.append(("mixamorig:RightUpLeg", 0, (-0.1, -0.1, 0.0)))
        self.addCleanup(lambda: RG.CHAIN.__setitem__(slice(None), saved))
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.source = self.folder / "source.glb"
        RG.write_rig_glb(self.source, extra_joint=None, clips=("idle",))

    def local_spine(self, path: Path) -> np.ndarray:
        rig = C.Rig(path)
        channels = rig.clips()["idle"]
        spine = rig.joints["Spine"]
        _times, values = channels[spine]["rotation"]
        return values[1]

    def test_the_same_rig_gets_the_same_clip(self) -> None:
        out = self.folder / "out.glb"
        report = C.transfer(self.source, self.source, out, ["idle"])
        self.assertEqual(report["clips"], ["idle"])
        np.testing.assert_allclose(np.abs(self.local_spine(out)), np.abs(np.array(RG.LEAN[1])), atol=1e-5)

    def test_a_body_that_faces_the_other_way_gets_the_same_lean_in_its_own_frame(self) -> None:
        target, out = self.folder / "turned.glb", self.folder / "out.glb"
        turned_copy(self.source, target, 180.0)
        C.transfer(self.source, target, out, ["idle"])
        # the spine leans forward in the body's own frame, so its local turn is the source's, not mirrored
        np.testing.assert_allclose(np.abs(self.local_spine(out)), np.abs(np.array(RG.LEAN[1])), atol=1e-5)

    def test_the_hips_keep_their_motion_but_not_a_held_level_offset(self) -> None:
        """Tripo's run on the demo goblin held the hips off their rest spot in every frame; the route plays clips in place."""

        out = self.folder / "out.glb"
        C.transfer(self.source, self.source, out, ["idle"])
        rig = C.Rig(out)
        _times, values = rig.clips()["idle"][rig.joints["Hips"]]["translation"]
        rest = np.asarray(rig.nodes[rig.joints["Hips"]].get("translation", [0.0, 0.0, 0.0]))
        np.testing.assert_allclose((values - rest)[:, [0, 2]].mean(axis=0), [0.0, 0.0], atol=1e-6)
        self.assertGreater(float(np.ptp(values[:, 1])), 0.01, "the bob up and down stays")

    def test_a_missing_clip_is_named(self) -> None:
        with self.assertRaises(C.TransferError):
            C.transfer(self.source, self.source, self.folder / "out.glb", ["swagger"])


if __name__ == "__main__":
    unittest.main()
