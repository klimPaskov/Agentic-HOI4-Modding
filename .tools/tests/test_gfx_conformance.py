"""Fixture tests for the read-only GFX conformance checks in `.tools/gfx/gfx.py`.

Binary fixtures outside `gfx/` are ignored by `.gitignore`, so each test builds a tiny mod tree with
minimal DDS and TGA headers in a temporary folder. Run from the mod root:
`python -B .tools/tests/test_gfx_conformance.py`.
"""

import importlib.util
import io
import struct
import tempfile
import unittest
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gfx_conformance_under_test", TOOLS / "gfx" / "gfx.py")
gfx = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gfx)


def dds(width, height, payload=None):
	"""Uncompressed 32-bit legacy DDS; `payload` overrides the pixel byte count."""
	header = bytearray(128)
	header[0:4] = b"DDS "
	struct.pack_into("<7I", header, 4, 124, 0x100F, height, width, width * 4, 0, 0)
	struct.pack_into("<2I", header, 76, 32, 0x41)
	struct.pack_into("<5I", header, 88, 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000)
	return bytes(header) + bytes(width * height * 4 if payload is None else payload)


def tga(width, height, top_origin=False):
	header = bytearray(18)
	header[2] = 2
	struct.pack_into("<2H", header, 12, width, height)
	header[16] = 32
	header[17] = 0x28 if top_origin else 0x08
	return bytes(header) + bytes(width * height * 4)


class Tree:
	def __init__(self, test):
		self.folder = tempfile.TemporaryDirectory()
		test.addCleanup(self.folder.cleanup)
		self.root = Path(self.folder.name)

	def add(self, relative, data):
		path = self.root / relative
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))

	def rules(self, check):
		kwargs = {"vanilla": self.root / "no_vanilla"} if check is gfx.check_sprites else {}
		return sorted((f.rule, f.path) for f in check(self.root, None, **kwargs))


class FrameStrips(unittest.TestCase):
	def test_uneven_strip_is_reported_and_even_strip_is_not(self):
		tree = Tree(self)
		tree.add("gfx/interface/even.dds", dds(46 * 36, 46, payload=0))
		tree.add("gfx/interface/uneven.dds", dds(1656, 46, payload=0))
		tree.add("interface/test.gfx", """spriteTypes = {
	spriteType = { name = "GFX_even" texturefile = "gfx/interface/even.dds" noOfFrames = 36 }
	# spriteType = { name = "GFX_commented" texturefile = "gfx/interface/uneven.dds" noOfFrames = 35 }
	spriteType = {
		name = "GFX_uneven"
		texturefile = "gfx/interface/uneven.dds"
		noOfFrames = 35
	}
}
""")
		found = gfx.check_sprites(tree.root, None, tree.root / "no_vanilla")
		self.assertEqual([(f.rule, f.level, f.line) for f in found], [("GFX-FRAME-WIDTH", "warning", 4)])
		self.assertIn("47.31 px per frame", found[0].message)


class Flags(unittest.TestCase):
	def test_ladder_sizes_and_origin(self):
		tree = Tree(self)
		tree.add("gfx/flags/AAA.tga", tga(82, 52))
		tree.add("gfx/flags/medium/AAA.tga", tga(41, 26))
		tree.add("gfx/flags/small/AAA.tga", tga(10, 7))
		tree.add("gfx/flags/BBB.tga", tga(41, 26))
		tree.add("gfx/flags/medium/BBB.tga", tga(41, 26, top_origin=True))
		self.assertEqual(tree.rules(gfx.check_flags), [
			("GFX-FLAG-LADDER", "gfx/flags/BBB.tga"),
			("GFX-FLAG-LADDER", "gfx/flags/medium/BBB.tga"),
			("GFX-FLAG-ORIGIN", "gfx/flags/medium/BBB.tga"),
			("GFX-FLAG-SIZE", "gfx/flags/BBB.tga"),
		])


class Achievements(unittest.TestCase):
	def test_only_64_by_64_art_passes(self):
		tree = Tree(self)
		tree.add("gfx/achievements/good.dds", dds(64, 64))
		tree.add("gfx/achievements/small.dds", dds(32, 32))
		self.assertEqual(tree.rules(gfx.check_achievements), [("GFX-ACHIEVEMENT-SIZE", "gfx/achievements/small.dds")])


def png(width, height, background=(0, 0, 0, 0), subject=(200, 160, 90, 255), empty=False):
	"""A PNG with a centred opaque subject on the given background colour."""
	image = Image.new("RGBA", (width, height), background)
	if not empty:
		for x in range(width // 4, width * 3 // 4):
			for y in range(height // 4, height * 3 // 4):
				image.putpixel((x, y), subject)
	buffer = io.BytesIO()
	image.save(buffer, format="PNG")
	return buffer.getvalue()


@unittest.skipUnless({"focus", "decision", "idea"} <= set(gfx.PROFILE_DATA), "profiles.json has no focus, decision and idea rows")
class FamilyChecks(unittest.TestCase):
	"""Family checks on a tiny mod: consumers come from focus, decision and idea script, textures from the .gfx file."""

	def test_family_levels(self):
		tree = Tree(self)
		tree.add("common/national_focus/tree.txt", """focus_tree = {
	focus = { id = good icon = GFX_focus_good }
	focus = { id = vanilla_size icon = GFX_focus_vanilla_size }
	focus = { id = odd icon = GFX_focus_odd }
}
""")
		tree.add("common/decisions/test.txt", "category = {\n\tbig_decision = { icon = big }\n\tempty_decision = { icon = empty }\n}\n")
		tree.add("common/ideas/test.txt", "ideas = {\n\tcountry = {\n\t\tboxed_idea = { picture = boxed }\n\t}\n}\n")
		sprites = {"GFX_focus_good": "goals/good", "GFX_focus_vanilla_size": "goals/vanilla_size", "GFX_focus_odd": "goals/odd",
			"GFX_decision_big": "decisions/big", "GFX_decision_empty": "decisions/empty", "GFX_idea_boxed": "ideas/boxed"}
		tree.add("interface/test.gfx", "spriteTypes = {\n" + "".join(
			f'\tspriteType = {{ name = "{name}" texturefile = "gfx/interface/{path}.png" }}\n' for name, path in sprites.items()) + "}\n")
		tree.add("gfx/interface/goals/good.png", png(94, 86))
		tree.add("gfx/interface/goals/vanilla_size.png", png(100, 88))
		tree.add("gfx/interface/goals/odd.png", png(90, 80))
		tree.add("gfx/interface/decisions/big.png", png(40, 40))
		tree.add("gfx/interface/decisions/empty.png", png(32, 32, empty=True))
		tree.add("gfx/interface/ideas/boxed.png", png(64, 64, background=(30, 30, 30, 255)))
		found = gfx.check_families(tree.root, None, tree.root / "no_vanilla")
		self.assertEqual(sorted((f.rule, f.level, f.path.split("/")[-1]) for f in found), [
			("GFX-DECISION-SIZE", "warning", "big.png"),
			("GFX-EMPTY-SUBJECT", "error", "empty.png"),
			("GFX-FOCUS-ALTERNATIVE", "review", "vanilla_size.png"),
			("GFX-FOCUS-SIZE", "error", "odd.png"),
			("GFX-OPAQUE-CANVAS", "error", "boxed.png"),
		])
		changed = gfx.check_families(tree.root, ["gfx/interface/goals/vanilla_size.png"], tree.root / "no_vanilla")
		self.assertEqual([(f.rule, f.level) for f in changed], [("GFX-FOCUS-ALTERNATIVE", "warning")])


class RuntimeBinaries(unittest.TestCase):
	def test_pointer_and_truncation_are_errors(self):
		tree = Tree(self)
		tree.add("gfx/interface/good.dds", dds(8, 8))
		tree.add("gfx/interface/pointer.dds", b"version https://git-lfs.github.com/spec/v1\noid sha256:00\nsize 1\n")
		tree.add("gfx/interface/short.dds", dds(8, 8, payload=40))
		tree.add("gfx/flags/short.tga", tga(82, 52)[:100])
		tree.add("sound/good.wav", b"RIFF\x00\x00\x00\x00WAVEfmt ")
		self.assertEqual(tree.rules(gfx.check_binaries), [
			("GFX-LFS-POINTER", "gfx/interface/pointer.dds"),
			("GFX-TRUNCATED", "gfx/flags/short.tga"),
			("GFX-TRUNCATED", "gfx/interface/short.dds"),
		])

	def test_compressed_payload_size(self):
		header = bytearray(dds(16, 16, payload=0))
		struct.pack_into("<I", header, 80, 0x4)
		header[84:88] = b"DXT5"
		self.assertEqual(gfx.dds_payload_bytes(bytes(header)), 4 * 4 * 16)
		header[84:88] = b"DXT1"
		self.assertEqual(gfx.dds_payload_bytes(bytes(header)), 4 * 4 * 8)


if __name__ == "__main__":
	unittest.main()
