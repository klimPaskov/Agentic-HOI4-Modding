"""The designer preview's size (D-140): read from the game's division designer interface, and used by the review's preview sheet."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
REPO = PIPELINE.parents[1]
sys.path.insert(0, str(PIPELINE))

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
