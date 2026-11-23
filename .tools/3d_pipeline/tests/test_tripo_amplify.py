"""The map-camera amplify step (lib/tripo_amplify.py): each joint turns further from the clip's first pose by the factor, the hips travel
further, and the first frame stays as it was."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import pdx_deform, tripo_amplify


def about_z(degrees: float) -> np.ndarray:
    half = math.radians(degrees) / 2
    return np.array([0.0, 0.0, math.sin(half), math.cos(half)])


def angle(q: np.ndarray) -> float:
    return math.degrees(2 * math.acos(min(1.0, abs(float(q[3])))))


class AmplifyTests(unittest.TestCase):
    def clip(self) -> pdx_deform.Animation:
        # an arm that starts turned 10 degrees and swings to 40, and hips that step 0.3 back
        q = np.array([about_z(10), about_z(25), about_z(40)])
        t = np.array([[0.0, 1.0, 0.0], [0.0, 1.0, -0.15], [0.0, 1.0, -0.3]])
        channels = {"Arm": {"q": q, "t": np.zeros((3, 3)), "s": np.ones(3)},
                    "Hips": {"q": np.tile([0.0, 0.0, 0.0, 1.0], (3, 1)), "t": t, "s": np.ones(3)}}
        return pdx_deform.Animation(fps=24.0, frames=3, channels=channels)

    def test_the_turn_since_the_first_frame_grows_by_the_factor(self) -> None:
        result = tripo_amplify.amplified(self.clip(), 1.5, ["Arm", "Hips"])
        arm = result.channels["Arm"]["q"]
        self.assertAlmostEqual(angle(arm[0]), 10.0, places=4)  # the clip still starts on its own first pose
        self.assertAlmostEqual(angle(arm[2]), 10.0 + 1.5 * 30.0, places=4)  # 30 degrees of swing become 45
        np.testing.assert_allclose(result.channels["Hips"]["t"][2], [0.0, 1.0, -0.45], atol=1e-9)  # the step goes half as far again
        np.testing.assert_allclose(result.channels["Hips"]["t"][0], [0.0, 1.0, 0.0], atol=1e-9)

    def test_a_factor_of_one_changes_nothing(self) -> None:
        clip = self.clip()
        result = tripo_amplify.amplified(clip, 1.0, ["Arm", "Hips"])
        for name in ("Arm", "Hips"):
            np.testing.assert_allclose(np.abs(result.channels[name]["q"]), np.abs(clip.channels[name]["q"]), atol=1e-9)
            np.testing.assert_allclose(result.channels[name]["t"], clip.channels[name]["t"], atol=1e-9)

    def test_the_power_keeps_the_axis(self) -> None:
        q = tripo_amplify._power(about_z(30)[None, :], 2.0)[0]
        np.testing.assert_allclose(q, about_z(60), atol=1e-9)


if __name__ == "__main__":
    unittest.main()
