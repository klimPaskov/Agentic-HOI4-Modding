"""The designer preview's size (D-140): read from the game's division designer interface, and used by the review's preview sheet."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
REPO = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))

import numpy as np

from lib import designer_preview as D

# The two blocks as the installed game's interface/divisiondesignerview.gui writes them (2026-11-23), cut to what `measure` reads.
GUI = """
guiTypes = {
	containerWindowType = {
		name = "divisiondesigner"
		iconType = {
			name = "select_model"
			position = { x=938 y=366 }
			quadTextureSprite = "GFX_3d_view_placeholder"
		}
		buttonType = {
			name = "toggle_model_selector_button"
			position = { x=936 y=363 }
			size = { x = 249 y = 249 }
			quadTextureSprite ="GFX_division_3d_bg"
		}
		containerWindowType = {
			name = "div_template_select_model"
			position = { x=670 y=40 }
			size = { width=538 height=581 }
			background = {
				name = "Background"
				spriteType ="GFX_tiled_window"
				position = { x=-16 y=0 }
			}
			containerWindowType = {
				name = "border_container"
				position = { x=0 y=15 }
				size = { width = 510 height = 316 }
				background = {
					name ="bg_tech_button"
					spriteType = "GFX_division_3d_bg"
					size = { x=100%% y=100%%}
				}
			}
			iconType = {
				name ="3d_view"
				quadTextureSprite = "GFX_3d_view_placeholder"
				position = { x= 4 y = 18 }
			}
		}
	}
}
"""


class DesignerPreview(unittest.TestCase):
    def test_measure_reads_the_preview_frame_and_the_picker_view(self):
        found = D.measure(GUI)
        self.assertEqual(found["preview"], (D.PREVIEW_PX, D.PREVIEW_PX))
        self.assertEqual(found["picker"], D.PICKER_PX)

    def test_a_file_without_the_frames_gives_none(self):
        self.assertEqual(D.measure("guiTypes = { }"), {"preview": None, "picker": None})

    def test_the_installed_game_still_has_these_sizes(self):
        import run_pilot

        game = run_pilot.installed_game_dir()  # the kit's shared rule for the game folder (.tools/lib/game.py)
        if not (Path(game) / D.GUI_FILE).is_file():
            self.skipTest("the game folder has no division designer interface")
        found = D.measure_game(game)
        self.assertEqual(found["preview"], (D.PREVIEW_PX, D.PREVIEW_PX))
        self.assertEqual(found["picker"], D.PICKER_PX)

    def test_the_recorded_game_fill_is_the_light_tank_in_hoi4_1_20(self):
        """Regression on the light tank numbers the camera was fitted on: the M2A4 light tank fills 149 by 136 px of the 249 px frame in
        HOI4 1.20.0.0 at entity scale 0.7, and FRAME_WORLD gives it that width from its calibration render."""

        fill = D.GAME_FILL
        self.assertEqual((fill["build"], fill["entity_scale"], fill["pixels"]), ("1.20.0.0", 0.7, (149, 136)))
        self.assertAlmostEqual(fill["width"], 0.60, delta=0.005)
        self.assertAlmostEqual(fill["height"], 0.55, delta=0.005)
        width_px, height_px = fill["render_pixels"]
        frame = width_px / D.PREVIEW_PX * fill["calibration_ortho"] * fill["entity_scale"] / fill["width"]
        self.assertAlmostEqual(D.FRAME_WORLD, frame, delta=0.001)
        # the same render's height, at FRAME_WORLD, lands within the elevation's uncertainty of the game's
        height = height_px / D.PREVIEW_PX * fill["calibration_ortho"] * fill["entity_scale"] / D.FRAME_WORLD
        self.assertAlmostEqual(height, fill["height"], delta=0.04)
        # the old fit (the unit's largest extent times 1.15 across the frame) drew a unit about 1.4 times larger than the game does
        self.assertLess(fill["width"] * 1.4, 0.87)

    def test_a_box_fills_the_frame_by_its_projected_size_times_its_entity_scale(self):
        """A cube seen square on (azimuth 0, elevation 0) is as wide on screen as its side, so at scale 2 it fills 2 * side / FRAME_WORLD."""

        cube = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], float)
        width, height = D.frame_fill(cube, 2.0, view=(0.0, 0.0))
        self.assertAlmostEqual(width, 2.0 / D.FRAME_WORLD)
        self.assertAlmostEqual(height, 2.0 / D.FRAME_WORLD)
        self.assertAlmostEqual(D.ortho_for(2.0), D.FRAME_WORLD / 2.0)
        with self.assertRaises(ValueError):
            D.ortho_for(0.0)

    def test_the_vanilla_light_tank_reads_as_large_as_the_m2a4_the_camera_was_fitted_on(self):
        """The kit sized the M2A4 to vanilla's light tank, so vanilla's tank (the vehicle reference) fills about what the game showed."""

        import run_pilot
        from lib import pdx_deform

        mesh_path = Path(run_pilot.installed_game_dir()) / D.VEHICLE_REFERENCE["mesh"]
        if not mesh_path.is_file():
            self.skipTest("the game folder has no vanilla light tank")
        mesh = pdx_deform.load_mesh(mesh_path)
        points = mesh.positions[~mesh.collision] if len(mesh.collision) else mesh.positions
        width, _height = D.frame_fill(points, D.VEHICLE_REFERENCE["entity_scale"])
        self.assertAlmostEqual(width, D.GAME_FILL["width"], delta=0.08)

    def test_the_calibration_fit_scores_a_moved_and_scaled_silhouette_as_the_same(self):
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import designer_calibrate as C

        game = np.zeros((249, 249), bool)
        game[100:160, 60:180] = True
        render = np.zeros((249, 249), bool)
        render[20:50, 10:70] = True  # the same box at half the size, elsewhere
        iou, placed = C.fitted_overlap(game, render)
        self.assertGreater(iou, 0.95)
        self.assertEqual(C.box(placed), C.box(game))
        other = np.zeros((249, 249), bool)
        other[20:80, 10:40] = True  # tall, not wide
        self.assertLess(C.fitted_overlap(game, other)[0], 0.8)

    def test_the_calibration_mask_drops_the_world_the_ground_and_the_horizon(self):
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import tempfile

        from PIL import Image

        import designer_calibrate as C

        tile = np.zeros((60, 60, 3), np.uint8)
        tile[:20] = (255, 0, 255)
        tile[20] = (208, 72, 208)  # a horizon pixel blended in sRGB
        tile[21:] = (80, 111, 80)
        tile[30:40, 25:35] = (120, 125, 70)  # an olive model
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "tile.png"
            Image.fromarray(tile).save(path)
            mask = C.tile_mask(path)
        self.assertEqual(C.box(mask), (25, 30, 35, 40))

    def test_the_preview_sheet_takes_the_jobs_entity_scale_and_class_reference(self):
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import tempfile

        import weapon_sheets

        with tempfile.TemporaryDirectory() as temp:
            jobs = Path(temp) / "jobs.json"
            jobs.write_text('{"jobs": {"orc": {"runtime_entity_scale": 0.8, "vanilla_scale_reference": '
                            '{"mesh": "gfx/models/units/western_european_infantry.mesh", "entity_scale": 0.8}}}}', encoding="utf-8")
            settings = weapon_sheets.preview_settings(jobs, "orc", None, None, None)
            self.assertEqual((settings["entity_scale"], settings["reference_scale"]), (0.8, 0.8))
            self.assertEqual(settings["reference"].name, "western_european_infantry.mesh")
            tank = weapon_sheets.preview_settings(None, None, 0.85, None, None)
            self.assertEqual((tank["reference"].name, tank["reference_scale"]), ("USA_tank_light.mesh", 0.85))
            with self.assertRaises(SystemExit):
                weapon_sheets.preview_settings(None, None, None, None, None)
            with self.assertRaises(SystemExit):
                weapon_sheets.preview_settings(None, None, 1.0, "gfx/models/units/x.mesh", None)

    def test_a_vanilla_reference_takes_the_maps_its_mesh_material_names(self):
        """The infantry reference's maps carry another name than its mesh; the first diffuse map in the folder would be another army's."""

        sys.path.insert(0, str(PIPELINE / "tripo"))
        import run_pilot
        import weapon_sheets

        mesh = Path(run_pilot.installed_game_dir()) / "gfx/models/units/western_european_infantry.mesh"
        if not mesh.is_file():
            self.skipTest("the game folder has no vanilla infantry")
        maps = weapon_sheets.reference_maps(mesh)
        self.assertEqual(Path(maps["diffuse"]["*"]).name, "western_europe_infantry_diffuse.dds")
        self.assertEqual(Path(maps["specular"]["*"]).name, "western_europe_infantry_spec.dds")

    def test_the_preview_sheet_is_a_sheet_choice_and_the_review_prompt_judges_clips_there(self):
        sys.path.insert(0, str(PIPELINE / "tripo"))
        import weapon_sheets

        self.assertIn("preview", weapon_sheets.SHEETS)
        prompt = (PIPELINE / "config" / "visual_review_prompt.md").read_text(encoding="utf-8")
        self.assertIn("preview_size.png", prompt)
        self.assertIn("Judge each clip's motion here", prompt)
        self.assertIn("Do not fail a clip because its motion is hard to read at this size", prompt)


if __name__ == "__main__":
    unittest.main()
