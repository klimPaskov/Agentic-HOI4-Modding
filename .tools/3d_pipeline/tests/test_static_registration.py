"""A static model's registration is three files laid out as vanilla's: a `.gfx` with the pdxmesh inside `objectTypes`, the animations
in an `.asset` in the model folder with file names relative to it, and the entity alone in `gfx/entities`. HOI4 1.19.4 refused the old
single `gfx/entities/<name>.asset` ("Unexpected token: objectTypes", "Could not load animation file gfx/entities/gfx/models/...")."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

from lib import static_kinds as sk
from lib import unit_wiring as wiring
from tripo import static_model


class StaticRegistrationTests(unittest.TestCase):
    def files(self, kind: str = "vehicle") -> dict:
        contract = sk.kind_contract(kind)
        reference = contract["entity"]["reference"]
        with tempfile.TemporaryDirectory() as folder:
            game = Path(folder)
            (game / "gfx" / "entities").mkdir(parents=True)
            (game / "gfx" / "entities" / "vanilla.asset").write_text(
                f'entity = {{\n\tname = "{reference}"\n\tpdxmesh = "vanilla_mesh"\n\tstate = {{ name = "idle" animation = "idle" }}\n'
                f'\tstate = {{ name = "move" animation = "move" }}\n\tscale = 1\n}}\n', encoding="utf-8")
            return static_model.registration("tank_t", kind, contract, ["idle", "move"], [], game)

    def test_the_mesh_animations_and_entity_are_three_files(self) -> None:
        files = self.files()
        folder = static_model.FOLDERS["vehicle"]
        self.assertEqual(sorted(files), sorted(["gfx/entities/tank_t.gfx", f"{folder}/tank_t/tank_t.asset", "gfx/entities/tank_t.asset"]))
        self.assertTrue(files["gfx/entities/tank_t.gfx"].startswith("objectTypes = {"))
        self.assertIn("pdxmesh", files["gfx/entities/tank_t.gfx"])
        entity = files["gfx/entities/tank_t.asset"]
        self.assertNotIn("objectTypes", entity)  # an .asset takes no objectTypes
        self.assertNotIn("pdxmesh = {", entity)
        self.assertIn('name = "tank_t_entity"', entity)

    def test_animation_files_are_relative_to_the_model_folder(self) -> None:
        files = self.files()
        folder = static_model.FOLDERS["vehicle"]
        names = re.findall(r'file\s*=\s*"([^"]+)"', files[f"{folder}/tank_t/tank_t.asset"])
        self.assertEqual(names, ["tank_t_idle.anim", "tank_t_move.anim"])
        for text in files.values():
            self.assertNotRegex(text, r'file\s*=\s*"gfx/[^"]+\.anim"')  # the old form, read as gfx/entities/gfx/models/...

    def test_wire_unit_reads_the_registration(self) -> None:
        files = self.files()
        registration = wiring.parse_registration(static_model.registration_markdown("tank_t", "vehicle", files))
        self.assertEqual(registration.stem, "tank_t")
        self.assertEqual(wiring.model_folder(registration), f"{static_model.FOLDERS['vehicle']}/tank_t")
        self.assertIn("objectTypes", "objectTypes = {\n" + registration.gfx_block + "\n}")
        self.assertNotIn("objectTypes", registration.gfx_block)

    def test_a_death_clip_gets_a_death_state(self) -> None:
        contract = sk.kind_contract("vehicle")
        reference = contract["entity"]["reference"]
        with tempfile.TemporaryDirectory() as folder:
            game = Path(folder)
            (game / "gfx" / "entities").mkdir(parents=True)
            (game / "gfx" / "entities" / "vanilla.asset").write_text(
                f'entity = {{\n\tname = "{reference}"\n\tpdxmesh = "vanilla_mesh"\n\tstate = {{ name = "idle" animation = "idle" }}\n}}\n', encoding="utf-8")
            entity = static_model.registration("tank_t", "vehicle", contract, ["idle", "death"], [], game)["gfx/entities/tank_t.asset"]
        self.assertRegex(entity, r'state = \{ name = "death"\s+animation = "death"')

    def test_wire_unit_checks_a_static_model_by_its_kind(self) -> None:
        # wire_unit ran a building through the unit rules (UNIT-LOOSE-PART on 39 loose parts) before the kind was handed over
        import wire_unit

        checks = static_model.check_args("vehicle", {"size_reference": "USA_tank_light"}, 3600)
        text = static_model.registration_markdown("tank_t", "vehicle", self.files(), checks)
        self.assertEqual(wiring.parse_registration(text).stem, "tank_t")
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder)
            (job / "runtime").mkdir()
            (job / "runtime" / "registration.md").write_text(text, encoding="utf-8")
            self.assertEqual(wire_unit.static_checks(job), ["--model-kind", "vehicle", "--running-gear-triangles", "3600", "--size-reference", "USA_tank_light"])
            (job / "runtime" / "registration.md").write_text(static_model.registration_markdown("tank_t", "vehicle", self.files()), encoding="utf-8")
            self.assertEqual(wire_unit.static_checks(job), [])


if __name__ == "__main__":
    unittest.main()
