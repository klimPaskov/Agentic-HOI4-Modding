"""Fixture tests for `.tools/audits/audit_gui_rules.py`.

Run from the mod root: `python -B .tools/tests/test_gui_rules.py`.
"""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "audits"))
sys.path.insert(0, str(TOOLS))

import audit_gui_rules as rules

KNOWN = {"extended": {"fixture_extended_slider"}}

TEXT_BOXES = """guiTypes = {
	containerWindowType = {
		name = "popup"
		orientation = "upper_left"
		instantTextBoxType = {
			name = "good"
			scrollbartype = "standardtext_slider"
			format = left
		}
		instantTextBoxType = {
			name = "bad"
			scrollbartype = "fixture_extended_slider"
			format = "left"
		}
		instantTextBoxType = {
			name = "upper"
			format = "LEFT"
		}
	}
}
"""

SIZES = """guiTypes = {
	containerWindowType = {
		name = "root"
		position = { x = 0 y = 92 }
		size = { width = 600 height = -92 }
		containerWindowType = {
			name = "list_as_engine"
			position = { x = 40 y = 377 }
			size = { width = 254 height = -96 }
		}
		containerWindowType = {
			name = "list_as_parent_height"
			position = { x = 40 y = 377 }
			size = { width = 254 height = -473 }
		}
	}
}
"""

EVENT = """guiTypes = {
	containerWindowType = {
		name = "EventWindow"
		containerWindowType = {
			name = "midsection"
			containerWindowType = {
				name = "deeper"
				instantTextBoxType = { name = "Description" }
			}
		}
		containerWindowType = {
			name = "bottom_Window"
		}
		iconType = { name = "event_picture" }
	}
	containerWindowType = {
		name = "EventWindow_News"
		containerWindowType = { name = "header" iconType = { name = "event_picture" } }
		containerWindowType = { name = "bottom_Window" }
		containerWindowType = {
			name = "midsection"
			instantTextBoxType = { name = "Description" }
		}
	}
}
"""


def found(text, path="interface/x.gui"):
	return [(f.rule, f.level, f.line) for f in rules.scan_text(path, text, KNOWN)]


class GuiRules(unittest.TestCase):
	def test_text_box_scrollbars_and_quoted_words(self):
		self.assertEqual(found(TEXT_BOXES), [
			("GUI-QUOTED-WORD", "error", 4),
			("GUI-TEXT-EXTENDED-SCROLLBAR", "error", 10),
			("GUI-QUOTED-WORD", "error", 13),
		])

	def test_negative_size_larger_than_the_offset_is_a_review(self):
		self.assertEqual(found(SIZES), [("GUI-NEGATIVE-SIZE", "review", 11)])

	def test_event_window_places(self):
		self.assertEqual(found(EVENT, "interface/eventwindow.gui"), [
			("GUI-EVENT-PLACEMENT", "error", 8),
			("GUI-EVENT-PLACEMENT", "error", 14),
		])
		self.assertEqual(found(EVENT, "interface/other.gui"), [])


if __name__ == "__main__":
	unittest.main()
