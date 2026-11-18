"""The spine ease for a stretched back (lib/tripo_cloak_bend.py): the spreading of the need over frames and the stage's wiring (no Blender)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import tripo_cloak_bend as B


class Spread(unittest.TestCase):
    def test_a_need_is_spread_to_the_neighbours_and_falls_to_zero(self) -> None:
        needed = np.zeros(30)
        needed[15] = 0.4
        out = B.spread(needed, 6, False)
        self.assertEqual(float(out[15]), 0.4)
        self.assertTrue(np.all(out >= needed))
        self.assertGreater(float(out[12]), 0.0)
        self.assertEqual(float(out[8]), 0.0)
        self.assertEqual(float(out[0]), 0.0)
        self.assertLessEqual(float(np.abs(np.diff(out)).max()), 0.4 * 1.5 / 6 + 1e-9, "the share never changes faster than 1.5 of the ramp")

    def test_a_loop_spreads_round_its_end_so_the_seam_stays(self) -> None:
        needed = np.zeros(30)
        needed[1] = 0.3
        out = B.spread(needed, 6, True)
        self.assertGreater(float(out[-1]), 0.0, "the last frame is next to the first in a loop")
        self.assertAlmostEqual(float(out[-1]), float(out[3]), places=9, msg="frame 29 is two frames from frame 1 round the seam, as frame 3 is")
        self.assertEqual(float(out[15]), 0.0)

    def test_no_need_stays_no_share(self) -> None:
        self.assertTrue(np.all(B.spread(np.zeros(10), 6, True) == 0.0))


class Limits(unittest.TestCase):
    def test_the_trigger_is_under_the_checks_limit_and_the_target_under_the_trigger(self) -> None:
        self.assertLess(B.TARGET_SHARE, B.TRIGGER_SHARE)
        self.assertLess(B.TRIGGER_SHARE, B.CHECK_LIMIT)

    def test_the_shares_start_at_none_and_stay_under_one_half(self) -> None:
        self.assertEqual(float(B.SHARES[0]), 0.0)
        self.assertLessEqual(float(B.SHARES[-1]), 0.5)


class Wiring(unittest.TestCase):
    def test_only_a_job_with_a_cape_or_a_cloak_chain_has_a_cloak(self) -> None:
        import run_pilot

        self.assertTrue(run_pilot.job_has_cloak({"cape": True}))
        self.assertTrue(run_pilot.job_has_cloak({"tripo": {"chains": [{"region": "cloak"}]}}))
        self.assertTrue(run_pilot.job_has_cloak({"tripo": {"chains": ["cloak"]}}))
        self.assertFalse(run_pilot.job_has_cloak({"tripo": {"chains": [{"region": "plates"}]}}), "plates alone are not a cloak")
        self.assertFalse(run_pilot.job_has_cloak({}))

    def test_a_job_without_a_cloak_or_with_the_switch_off_is_left_alone(self) -> None:
        import tempfile
        from unittest import mock

        import run_pilot

        for spec in ({"runtime_stem": "u"}, {"runtime_stem": "u", "cape": True, "tripo": {"ease_cloak_bend": False}}):
            with tempfile.TemporaryDirectory() as folder, mock.patch.object(B, "ease_cloak_bend") as ease:
                run_pilot.ease_staged_cloak_bends(Path(folder), Path(folder), spec, ["attack"], {"u_attack.anim": {}})
            ease.assert_not_called()

    def test_every_role_of_a_cloaked_unit_is_eased_and_recorded(self) -> None:
        import tempfile
        from unittest import mock

        import run_pilot

        records = {"u_idle.anim": {}, "u_attack.anim": {}}
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(B, "ease_cloak_bend", return_value=B.CloakBend(True, ("Spine",), 0.2, 5, 0.07, 0.04)) as ease,                 mock.patch.object(run_pilot, "file_record", lambda path, relative_to=None: {}):
            run_pilot.ease_staged_cloak_bends(Path(folder), Path(folder), {"runtime_stem": "u", "cape": True}, ["idle", "attack"], records)
        self.assertEqual(ease.call_count, 2)
        self.assertEqual(records["u_attack.anim"]["cloak_bend"]["joints"], ["Spine"])
        self.assertIn("staged", records["u_idle.anim"])


if __name__ == "__main__":
    unittest.main()
