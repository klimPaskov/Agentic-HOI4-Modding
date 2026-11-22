"""The registration writes one meshsettings per mesh stream of a shape (lib/unit_registration.pdxmesh_block). No Blender."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import unit_registration as U

SHAPE = "tripo_mesh_1"


def settings(text: str):
    return [(int(index), diffuse) for index, diffuse in re.findall(r'index = (\d+)\s+texture_diffuse = "([^"]+)"', text)]


class Streams(unittest.TestCase):
    def test_a_burn_heap_stream_gets_its_own_ash_maps(self) -> None:
        # run demon_g (2026-11-21): the ash heap is the shape's second stream, its material names the ash maps
        streams = {SHAPE: [{"diff": "", "n": "", "spec": ""},
                           {"diff": "u_ash_diffuse.dds", "n": "u_ash_normal.dds", "spec": "u_ash_specular.dds"}]}
        text = U.pdxmesh_block("u", "gfx/models/units/u", [SHAPE], ["idle"], streams=streams)
        self.assertEqual(settings(text), [(0, "u_diffuse.dds"), (1, "u_ash_diffuse.dds")])
        self.assertIn('texture_specular = "u_ash_specular.dds"', text)

    def test_a_one_stream_shape_is_written_as_before(self) -> None:
        before = U.pdxmesh_block("u", "gfx/models/units/u", [SHAPE, "other"], ["idle"])
        after = U.pdxmesh_block("u", "gfx/models/units/u", [SHAPE, "other"], ["idle"], streams={SHAPE: [{"diff": "", "n": "", "spec": ""}]})
        self.assertEqual(before, after)
        self.assertEqual(settings(before), [(0, "u_diffuse.dds"), (1, "u_diffuse.dds")])


if __name__ == "__main__":
    unittest.main()
