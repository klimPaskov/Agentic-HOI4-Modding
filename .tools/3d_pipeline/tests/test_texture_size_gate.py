"""The profile texture-size cap fails closed instead of skipping itself.

It used to shell out to ffprobe and silently allow any size when ffprobe was
missing or failed. These tests need neither ffprobe nor Pillow nor Blender.
"""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_pipeline_startup_regressions import AdapterHarness


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = PIPELINE_ROOT / "adapter"
sys.path.insert(0, str(ADAPTER_ROOT))


def load_adapter_module(name: str):
    spec = importlib.util.spec_from_file_location(name, ADAPTER_ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = load_adapter_module("texture_size_gate")


def png_bytes(width: int, height: int) -> bytes:
    """A PNG with a valid signature, IHDR (with CRC) and IEND, and no pixel data.

    The size cap reads only the header, so a large declared size costs nothing.
    """

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return gate.PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")


PROFILE = {"texture_max_dimension": 1024, "exceptions": []}


class PngDimensionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.root = Path(self._temp.name)

    def write(self, name: str, data: bytes) -> Path:
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_reads_width_and_height_without_any_external_tool(self) -> None:
        self.assertEqual(gate.png_dimensions(self.write("a.png", png_bytes(300, 128))), (300, 128))

    def test_rejects_what_it_cannot_measure(self) -> None:
        jpeg = b"\xff\xd8\xff\xe0" + bytes(40)
        truncated = png_bytes(64, 64)[:20]
        wrong_first_chunk = gate.PNG_SIGNATURE + struct.pack(">I", 13) + b"tEXt" + bytes(13)
        zero_width = gate.PNG_SIGNATURE + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 0, 5) + bytes(5)
        for name, data in (("a.jpg", jpeg), ("b.png", truncated), ("c.png", wrong_first_chunk), ("d.png", zero_width)):
            with self.subTest(name=name), self.assertRaises(gate.TextureSizeGateError):
                gate.png_dimensions(self.write(name, data))
        with self.assertRaises(gate.TextureSizeGateError):
            gate.png_dimensions(self.root / "missing.png")


class TextureSizeDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.root = Path(self._temp.name)

    def png(self, width: int, height: int, name: str = "t.png") -> Path:
        path = self.root / name
        path.write_bytes(png_bytes(width, height))
        return path

    def test_image_within_the_cap_is_left_alone(self) -> None:
        decision = gate.texture_size_decision(self.png(1024, 512), PROFILE)
        self.assertEqual(decision["status"], "within_cap")
        self.assertEqual((decision["width"], decision["height"]), (None, None))

    def test_oversized_image_resizes_to_the_cap_keeping_its_aspect_ratio(self) -> None:
        decision = gate.texture_size_decision(self.png(4096, 2048), PROFILE)
        self.assertEqual(decision["status"], "resize")
        self.assertEqual((decision["width"], decision["height"]), (1024, 512))
        self.assertEqual((decision["source_width"], decision["source_height"]), (4096, 2048))
        tall = gate.texture_size_decision(self.png(1000, 3000, "tall.png"), PROFILE)
        self.assertEqual((tall["width"], tall["height"]), (341, 1024))

    def test_unreadable_image_blocks_without_an_exception(self) -> None:
        bad = self.root / "bad.png"
        bad.write_bytes(b"not an image")
        with self.assertRaisesRegex(gate.TextureSizeGateError, "texture_max_dimension"):
            gate.texture_size_decision(bad, PROFILE)

    def test_profile_without_a_positive_cap_blocks(self) -> None:
        image = self.png(256, 256)
        for profile in ({}, {"texture_max_dimension": 0}, {"texture_max_dimension": "1024"}, {"texture_max_dimension": True}):
            with self.subTest(profile=profile), self.assertRaisesRegex(gate.TextureSizeGateError, "no positive"):
                gate.texture_size_decision(image, profile)

    def test_recorded_exception_waives_the_cap_and_is_reported(self) -> None:
        profile = {
            "texture_max_dimension": 1024,
            "exceptions": [{"check": "texture_max_dimension", "reason": "Hero prop keeps 2048 for close-ups."}],
        }
        decision = gate.texture_size_decision(self.png(2048, 2048), profile)
        self.assertEqual(decision["status"], "excepted")
        self.assertEqual(decision["exception"]["reason"], "Hero prop keeps 2048 for close-ups.")
        self.assertEqual((decision["width"], decision["height"]), (None, None))
        self.assertIsNone(decision["unproven"])

    def test_exception_also_covers_an_unreadable_image_and_says_why(self) -> None:
        bad = self.root / "bad.png"
        bad.write_bytes(b"not an image")
        profile = {
            "texture_max_dimension": 1024,
            "exceptions": [{"check": "texture_max_dimension", "reason": "Legacy art pipeline."}],
        }
        decision = gate.texture_size_decision(bad, profile)
        self.assertEqual(decision["status"], "excepted")
        self.assertIn("not a PNG", decision["unproven"])

    def test_exception_without_a_reason_or_for_another_check_does_not_waive(self) -> None:
        image = self.root / "bad.png"
        image.write_bytes(b"not an image")
        for exceptions in (
            [{"check": "texture_max_dimension", "reason": "  "}],
            [{"check": "texture_max_dimension"}],
            [{"check": "texture_max_dimensions", "reason": "typo"}],
            "texture_max_dimension",
        ):
            with self.subTest(exceptions=exceptions), self.assertRaises(gate.TextureSizeGateError):
                gate.texture_size_decision(image, {"texture_max_dimension": 1024, "exceptions": exceptions})


class AdapterTextureCapTests(unittest.TestCase):
    """Run the real adapter module with no ffprobe anywhere on PATH."""

    PROBE = """
import json, os, sys
os.environ["PATH"] = ""
import hoi4_blender_mcp as adapter
from pathlib import Path
job = Path(sys.argv[1])
try:
    width, height, record = adapter._texture_resize_for_job(job, job / "t.png")
    print(json.dumps({"width": width, "height": height, "status": record["status"]}))
except Exception as exc:
    print(json.dumps({"error": type(exc).__name__, "message": str(exc)}))
"""

    def run_probe(self, job_record, image: bytes | None) -> dict:
        harness = AdapterHarness()
        self.addCleanup(harness.close)
        job = harness.root / "job"
        job.mkdir()
        if job_record is not None:
            (job / "job.yaml").write_text(json.dumps(job_record), encoding="utf-8")
        if image is not None:
            (job / "t.png").write_bytes(image)
        completed = harness.run("-c", self.PROBE, str(job))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout.strip().splitlines()[-1])

    def test_resize_decision_needs_no_ffprobe(self) -> None:
        result = self.run_probe({"profile": "static_prop"}, png_bytes(4096, 4096))
        self.assertEqual(result, {"width": 1024, "height": 1024, "status": "resize"})

    def test_unreadable_texture_fails_closed_in_the_adapter(self) -> None:
        result = self.run_probe({"profile": "static_prop"}, b"definitely not a png")
        self.assertEqual(result["error"], "TextureSizeGateError")

    def test_missing_job_record_or_unknown_profile_fails_closed(self) -> None:
        for record in (None, {"profile": "no_such_profile"}, {}):
            with self.subTest(record=record):
                result = self.run_probe(record, png_bytes(64, 64))
                self.assertEqual(result["error"], "TextureSizeGateError")

    def test_adapter_no_longer_shells_out_to_ffprobe(self) -> None:
        source = (ADAPTER_ROOT / "hoi4_blender_mcp.py").read_text(encoding="utf-8")
        self.assertNotIn("ffprobe", source)
        self.assertNotIn("subprocess", (ADAPTER_ROOT / "texture_size_gate.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
