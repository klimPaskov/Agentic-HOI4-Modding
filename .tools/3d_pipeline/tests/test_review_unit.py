"""The independent visual review step: sheet assembly, the reviewer request and the recorded verdict."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from PIL import Image

import review_unit

PASS_REPLY = """UNIT: zin_knights
VERDICT: pass
DEFECTS: none. Checked rest, idle, move, attack, defend, retreat and death.
"""

FAIL_REPLY = """UNIT: zin_knights
VERDICT: fail
DEFECTS:
- [attack f12 left] 2 The cape stretches into a spike. major.
- [death f40 front] 5 The body floats above the ground. minor.
"""


def write_tiles(folder: Path) -> None:
    clips = []
    for name, frames in (("rest", [1]), ("u_idle", [1, 9, 17])):
        rows = []
        for frame in frames:
            tiles = {}
            for view in review_unit.VIEWS:
                tile = f"{name}_{frame:04d}_{view}.png"
                Image.new("RGB", (32, 32), (frame * 10 % 255, 40, 40)).save(folder / tile)
                tiles[view] = tile
            rows.append({"frame": frame, "tiles": tiles})
        clips.append({"name": name, "rows": rows})
    (folder / "index.json").write_text(json.dumps({"clips": clips}), encoding="utf-8")


class Verdict(unittest.TestCase):
    def test_pass_needs_the_verdict_and_no_defects(self) -> None:
        self.assertEqual(review_unit.parse_verdict(PASS_REPLY)["verdict"], "pass")

    def test_a_listed_defect_fails_even_under_a_pass_verdict(self) -> None:
        mixed = PASS_REPLY.replace("DEFECTS: none.", "DEFECTS:\n- [idle f1 front] 4 The sword clips the leg. minor.")
        result = review_unit.parse_verdict(mixed)
        self.assertEqual((result["verdict"], result["stated_verdict"], result["defects"]), ("fail", "pass", 1))

    def test_a_reply_without_a_verdict_fails(self) -> None:
        self.assertEqual(review_unit.parse_verdict("Looks good to me.")["verdict"], "fail")

    def test_record_keeps_the_reply_and_hashes_the_sheets(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            (out / "sheets").mkdir()
            Image.new("RGB", (8, 8)).save(out / "sheets" / "u_idle.png")
            reply = out / "reply.md"
            reply.write_text(FAIL_REPLY, encoding="utf-8")
            result = review_unit.record(out, reply)
            saved = json.loads((out / "verdict.json").read_text(encoding="utf-8"))
            self.assertEqual((result["verdict"], result["defects"]), ("fail", 2))
            self.assertEqual(saved["sheets"].keys(), {"u_idle.png"})
            self.assertEqual((out / "review_reply.md").read_text(encoding="utf-8"), FAIL_REPLY)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(review_unit.main([folder, "--out", folder, "--record", str(reply)]), 1)

    def test_recording_before_rendering_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            reply = Path(folder) / "reply.md"
            reply.write_text(PASS_REPLY, encoding="utf-8")
            with self.assertRaises(SystemExit):
                review_unit.record(Path(folder), reply)


class Sheets(unittest.TestCase):
    def test_one_sheet_per_clip_with_a_row_per_frame(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            tiles = Path(folder) / "tiles"
            tiles.mkdir()
            write_tiles(tiles)
            sheets = review_unit.build_sheets(tiles, Path(folder) / "sheets")
            self.assertEqual([sheet.name for sheet in sheets], ["rest.png", "u_idle.png"])
            with Image.open(sheets[1]) as sheet:
                self.assertEqual(sheet.size, (32 * len(review_unit.VIEWS), (32 + review_unit.LABEL_HEIGHT) * 3))

    def test_a_clip_with_diagnostic_rows_gets_a_diagnostics_sheet(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            tiles = Path(folder) / "tiles"
            tiles.mkdir()
            write_tiles(tiles)
            index = json.loads((tiles / "index.json").read_text(encoding="utf-8"))
            diag = {}
            for view in review_unit.DIAGNOSTIC_VIEWS:
                diag[view] = f"u_idle_0009_{view}_diag.png"
                Image.new("RGB", (32, 32), (200, 200, 200)).save(tiles / diag[view])
            index["clips"][1]["diagnostic_rows"] = [{"frame": 9, "tiles": diag, "worst_share": 0.031}]
            (tiles / "index.json").write_text(json.dumps(index), encoding="utf-8")
            sheets = review_unit.build_sheets(tiles, Path(folder) / "sheets")
            self.assertEqual([sheet.name for sheet in sheets], ["rest.png", "u_idle.png", "u_idle_diagnostics.png"])
            with Image.open(sheets[2]) as sheet:
                self.assertEqual(sheet.size[1], review_unit.LABEL_HEIGHT + 32 + review_unit.LABEL_HEIGHT)
            request = review_unit.write_request(Path(folder), "u", sheets, tiles).read_text(encoding="utf-8")
            self.assertIn("Diagnostic sheets", request)
            self.assertIn("cyan open edge", request)

    def test_the_request_carries_the_prompt_and_every_sheet(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            sheets = [out / "rest.png", out / "u_idle.png"]
            request = review_unit.write_request(out, "u", sheets, out / "tiles").read_text(encoding="utf-8")
            self.assertIn("VERDICT: pass | fail", request)
            self.assertIn("magenta", request)
            for sheet in sheets:
                self.assertIn(str(sheet.resolve()), request)


class Inputs(unittest.TestCase):
    def test_a_rider_sharing_the_mount_folder_gets_only_its_clips(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            for name in ("knights_idle", "knights_move", "knights_rider_idle", "knights_rider_attack"):
                (Path(folder) / f"{name}.anim").write_bytes(b"")
            stems = ["knights", "knights_rider"]
            self.assertEqual([p.stem for p in review_unit.owned_anims(Path(folder), "knights", stems)], ["knights_idle", "knights_move"])
            self.assertEqual(len(review_unit.owned_anims(Path(folder), "knights_rider", stems)), 2)

    def test_each_shape_gets_the_diffuse_its_meshsettings_name(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "gfx" / "models" / "units" / "elephant"
            unit.mkdir(parents=True)
            for name in ("elephant_body_diffuse.dds", "elephant_howdah_diffuse.dds"):
                (unit / name).write_bytes(b"")
            gfx = (
                'objectTypes = {\n\tpdxmesh = {\n\t\tname = "elephant_mesh"\n\t\tfile = "gfx/models/units/elephant/elephant.mesh"\n'
                '\t\tmeshsettings = {\n\t\t\tname = "Body"\n\t\t\ttexture_diffuse = "elephant_body_diffuse.dds"\n\t\t}\n'
                '\t\tmeshsettings = {\n\t\t\tname = "Howdah"\n\t\t\ttexture_diffuse = "elephant_howdah_diffuse.dds"\n\t\t}\n\t}\n}\n'
            )
            maps = review_unit.diffuse_maps(unit / "elephant.mesh", [gfx])
            self.assertTrue(maps["Body"].endswith("elephant_body_diffuse.dds"))
            self.assertTrue(maps["Howdah"].endswith("elephant_howdah_diffuse.dds"))
            self.assertIn("*", maps)

    def test_the_prompt_states_the_quality_bar(self) -> None:
        prompt = review_unit.PROMPT.read_text(encoding="utf-8")
        for rule in ("No holes", "No stretching", "No weights leaking", "Feet meet the ground", "The rig fits the body"):
            self.assertIn(rule, prompt)


if __name__ == "__main__":
    unittest.main()
