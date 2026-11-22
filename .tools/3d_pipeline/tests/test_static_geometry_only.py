"""static_model.py --geometry-only: an untextured trial GLB is checked with flat maps, and refused without the flag."""

from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import static_kinds as sk
from tripo import static_model


def untextured_glb(path: Path) -> None:
    """One triangle with positions and normals only, as a Smart Mesh trial exports before its texture."""

    positions = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    normals = struct.pack("<9f", 0, 0, 1, 0, 0, 1, 0, 0, 1)
    binary = positions + normals
    document = {
        "asset": {"version": "2.0"},
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 36}, {"buffer": 0, "byteOffset": 36, "byteLength": 36}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3", "min": [0, 0, 0], "max": [1, 1, 0]},
            {"bufferView": 1, "componentType": 5126, "count": 3, "type": "VEC3"},
        ],
        "materials": [{"name": "material"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1}, "material": 0}]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }
    text = json.dumps(document).encode("utf-8")
    text += b" " * (-len(text) % 4)
    binary += b"\0" * (-len(binary) % 4)
    body = struct.pack("<II", len(text), 0x4E4F534A) + text + struct.pack("<II", len(binary), 0x004E4942) + binary
    path.write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body)


class GeometryOnlyTextures(unittest.TestCase):
    def test_untextured_glb_needs_the_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            glb = root / "trial.glb"
            untextured_glb(glb)
            contract = sk.kind_contract("building")
            with self.assertRaises(SystemExit) as refused:
                static_model.pack_textures(glb, contract, "trial", root / "files", root / "work")
            self.assertIn("--geometry-only", str(refused.exception))

    def test_flag_packs_flat_maps_and_marks_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            glb = root / "trial.glb"
            untextured_glb(glb)
            (root / "files").mkdir()
            contract = sk.kind_contract("building")
            found: dict = {}
            written = static_model.pack_textures(glb, contract, "trial", root / "files", root / "work", found, geometry_only=True)
            self.assertTrue(found.get("geometry_only"))
            self.assertEqual(set(written), {"diffuse", "normal", "specular"})
            for entry in written.values():
                self.assertTrue((root / "files" / entry["file"]).exists())


if __name__ == "__main__":
    unittest.main()
