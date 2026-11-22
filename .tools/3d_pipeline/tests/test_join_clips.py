"""The Canvas exports one clip per GLB. join_clips puts the clips of one rigged model back into one file, byte for byte, and refuses a file
of another model."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(PIPELINE_ROOT / "tripo"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import join_clips as J
from rig_glb import write_rig_glb


def clip_bytes(path: Path) -> dict:
    """Each clip's channels as (node name, path, input bytes, output bytes)."""

    document, binary = J.read_glb(path)

    def data(index: int) -> bytes:
        view = document["bufferViews"][document["accessors"][index]["bufferView"]]
        start = view.get("byteOffset", 0)
        return bytes(binary[start: start + view["byteLength"]])

    found = {}
    for animation in document.get("animations") or []:
        rows = []
        for channel in animation["channels"]:
            sampler = animation["samplers"][channel["sampler"]]
            rows.append((document["nodes"][channel["target"]["node"]]["name"], channel["target"]["path"], data(sampler["input"]),
                         data(sampler["output"])))
        found[animation["name"]] = sorted(rows)
    return found


class JoinClips(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_one_clip_files_join_into_the_whole_export(self):
        whole = self.root / "whole.glb"
        write_rig_glb(whole, clips=("idle", "walk", "chop"))
        parts = []
        for name in ("idle", "walk", "chop"):
            part = self.root / f"{name}.glb"
            write_rig_glb(part, clips=(name,))
            parts.append(part)
        out = self.root / "inbox" / "unit__rigged.glb"
        report = J.join(parts, out)
        self.assertEqual(report["clips"], ["idle", "walk", "chop"])
        self.assertEqual(report["skipped"], [])
        self.assertEqual(clip_bytes(out), clip_bytes(whole))
        document, binary = J.read_glb(out)
        self.assertEqual(document["buffers"][0]["byteLength"], len(binary))
        self.assertEqual(J.vertex_count(document), J.vertex_count(J.read_glb(whole)[0]))

    def test_a_clip_already_joined_is_left_out_and_named(self):
        first, second = self.root / "a.glb", self.root / "b.glb"
        write_rig_glb(first, clips=("idle",))
        write_rig_glb(second, clips=("idle", "walk"))
        report = J.join([first, second], self.root / "out.glb")
        self.assertEqual(report["clips"], ["idle", "walk"])
        self.assertEqual(report["skipped"], ["idle (b.glb)"])

    def test_another_model_is_refused(self):
        first, other = self.root / "a.glb", self.root / "b.glb"
        write_rig_glb(first, clips=("idle",), extra_joint=None)
        write_rig_glb(other, clips=("walk",))
        with self.assertRaises(J.JoinError):
            J.join([first, other], self.root / "out.glb")

    def test_the_command_prints_one_json_line(self):
        first, second = self.root / "a.glb", self.root / "b.glb"
        write_rig_glb(first, clips=("idle",))
        write_rig_glb(second, clips=("walk",))
        from unittest import mock

        with mock.patch("sys.stdout") as out:
            self.assertEqual(J.main([str(first), str(second), "--out", str(self.root / "out.glb")]), 0)
        printed = json.loads("".join(call.args[0] for call in out.write.call_args_list))
        self.assertEqual(printed["clips"], ["idle", "walk"])


if __name__ == "__main__":
    unittest.main()
