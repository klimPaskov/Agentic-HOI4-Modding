"""The culled-silhouette hole check (check_holes.py): judged against vanilla's own specks, not an open-edge count.

The verdict and limit tests run anywhere. `BlenderRender` renders real boxes where a supported Blender
is installed (skipped in CI): a closed box shows no hole, a box with a missing face or a face turned the
wrong way does.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import check_holes
from test_measure_body import write_glb
from test_winding_regression import BLENDER


def results(*largest: int, source: str = "unit.mesh") -> dict:
    rows = [{"clip": "unit_attack", "frame": index, "view": [90, 10], "largest": value, "pixels": value} for index, value in enumerate(largest)]
    return {"source": source, "size": check_holes.SIZE, "results": rows}


class Limit(unittest.TestCase):
    def test_the_shipped_calibration_matches_how_units_are_rendered(self) -> None:
        data = json.loads(check_holes.CALIBRATION.read_text(encoding="utf-8"))
        self.assertEqual((data["size"], data["frames"], data["views"]), (check_holes.SIZE, check_holes.FRAMES, len(check_holes.VIEWS)))
        self.assertEqual(set(data["references"]), {"GER_infantry.mesh", "cavalry_horse.mesh"})
        self.assertGreater(data["by_kind"]["other"]["pixels"], 0)
        self.assertEqual(data["largest"]["pixels"], max(row["pixels"] for row in data["by_kind"].values()))
        self.assertEqual(data["largest"]["pixels"], max(row["largest"] for row in data["references"].values()))
        self.assertIn("death", data["by_kind"]["death"]["clip"])

    def test_the_limit_scales_with_the_tile_area(self) -> None:
        base = check_holes.load_limit(check_holes.SIZE)
        doubled = check_holes.load_limit(check_holes.SIZE * 2)
        for kind in check_holes.KINDS:
            self.assertAlmostEqual(doubled[kind], base[kind] * 4)

    def test_a_missing_calibration_fails_closed(self) -> None:
        self.assertIsNone(check_holes.load_limit(256, Path("no_such_calibration.json")))
        ok, findings = check_holes.judge(results(0), None)
        self.assertFalse(ok)
        self.assertEqual(findings[0]["rule"], "UNIT-HOLE-CALIBRATION-MISSING")


class Judge(unittest.TestCase):
    limit = {"death": 60.0, "other": 20.0}

    def test_specks_as_large_as_vanillas_pass(self) -> None:
        self.assertEqual(check_holes.judge(results(0, 3, 20), self.limit), (True, []))

    def test_one_larger_cluster_fails_and_says_where(self) -> None:
        ok, findings = check_holes.judge(results(0, 21, 183), self.limit)
        self.assertFalse(ok)
        self.assertEqual(findings[0]["rule"], check_holes.RULE)
        self.assertIn("183 px", findings[0]["message"])
        self.assertIn("unit_attack frame 2", findings[0]["message"])
        self.assertIn("2 of 3 renders are over", findings[0]["message"])

    def test_a_death_clip_lying_on_the_ground_has_its_own_limit(self) -> None:
        lying = {"source": "unit.mesh", "size": 256, "results": [{"clip": "unit_death", "frame": 40, "view": [45, 10], "largest": 55, "pixels": 55}]}
        self.assertTrue(check_holes.judge(lying, self.limit)[0])
        standing = {"source": "unit.mesh", "size": 256, "results": [{"clip": "unit_idle", "frame": 4, "view": [45, 10], "largest": 55, "pixels": 55}]}
        ok, findings = check_holes.judge(standing, self.limit)
        self.assertFalse(ok)
        self.assertIn("standing clip is 20 px", findings[0]["message"])

    def test_many_edges_do_not_matter_only_what_shows(self) -> None:
        # A smart-topology unit with 1,250 open edges on its bark plates and no visible hole passes.
        self.assertTrue(check_holes.judge(results(*([4] * 200)), self.limit)[0])


class Command(unittest.TestCase):
    def run_main(self, source: Path, out: Path, rendered: dict) -> tuple:
        with mock.patch.object(check_holes, "render", return_value=rendered), mock.patch.object(check_holes, "load_limit", return_value={"death": 60.0, "other": 20.0}), redirect_stdout(io.StringIO()) as printed:
            code = check_holes.main([str(source), "--out", str(out)])
        return code, json.loads(printed.getvalue())

    def test_a_failing_unit_names_the_free_repair_and_the_check_after_it(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            unit = Path(folder) / "unit"
            unit.mkdir()
            with mock.patch.object(check_holes, "unit_target", return_value=(unit / "unit.mesh", [])):
                code, payload = self.run_main(unit, Path(folder) / "out", results(0, 40))
            written = json.loads((Path(folder) / "out" / "verdict.json").read_text(encoding="utf-8"))
        self.assertEqual((code, payload["verdict"]), (1, "fail"))
        self.assertEqual(written["verdict"], "fail")
        self.assertIn("--repairs winding holes", payload["next"][0])
        self.assertTrue(any("check_holes.py" in step and "repair/files" in step for step in payload["next"]))

    def test_a_provider_glb_is_closed_before_the_paid_rig(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            glb = Path(folder) / "generation_model.glb"
            glb.write_bytes(b"")
            code, payload = self.run_main(glb, Path(folder) / "out", results(0, 40, source=str(glb)))
        self.assertEqual(code, 1)
        self.assertIn("before paying for the rig", payload["next"][0])

    def test_a_clean_unit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            glb = Path(folder) / "generation_model.glb"
            glb.write_bytes(b"")
            code, payload = self.run_main(glb, Path(folder) / "out", results(0, 12, source=str(glb)))
        self.assertEqual((code, payload["verdict"]), (0, "pass"))
        self.assertEqual(payload["outputs"]["worst"]["largest"], 12)


def box(missing: int = -1, flipped: int = -1) -> tuple:
    """A 1 x 2 x 1 box of 12 triangles wound outward, with one side's two triangles missing or turned."""

    corners = np.array([[x, y, z] for x in (0.0, 1.0) for y in (0.0, 2.0) for z in (0.0, 1.0)])
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    triangles = []
    for side, (a, b, c, d) in enumerate(quads):
        if side == missing:
            continue
        pair = [(a, b, c), (a, c, d)]
        triangles += [(t[0], t[2], t[1]) for t in pair] if side == flipped else pair
    return corners, np.array(triangles)


@unittest.skipUnless(BLENDER and BLENDER.exists(), "no supported Blender installed")
class BlenderRender(unittest.TestCase):
    def largest(self, shape: tuple) -> int:
        with tempfile.TemporaryDirectory() as folder:
            glb = Path(folder) / "box.glb"
            write_glb(glb, *shape)
            rendered = check_holes.render(glb, [], Path(folder) / "out", size=64, overlays=1)
            return max(row["largest"] for row in rendered["results"])

    def test_a_closed_box_shows_no_hole(self) -> None:
        self.assertEqual(self.largest(box()), 0)

    def test_a_missing_side_or_a_side_turned_inward_shows_the_ground(self) -> None:
        self.assertGreater(self.largest(box(missing=3)), 100)
        self.assertGreater(self.largest(box(flipped=3)), 100)


if __name__ == "__main__":
    unittest.main()
