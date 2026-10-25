"""Tests for the shared readers in `.tools/lib/clausewitz.py` and `.tools/lib/localisation.py`.

Run from the mod root: `python -B .tools/tests/test_shared_readers.py`.
"""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from lib import clausewitz, localisation

SCRIPT = """# comment { not a block
idea = {
	picture = "my_picture" # trailing comment
	allowed = { check_variable = { x > 3 } }
	name = "has # inside"
}
}
bare_token
"""


class Clausewitz(unittest.TestCase):
	def test_nodes_keep_operators_quotes_and_lines(self):
		nodes = clausewitz.parse(SCRIPT)
		self.assertEqual([n[0] for n in nodes], ["idea", None])
		idea = nodes[0][2]
		self.assertEqual(idea[0], ("picture", "=", '"my_picture"', 3))
		comparison = idea[1][2][0][2][0]
		self.assertEqual(comparison, ("x", ">", "3", 4))
		self.assertEqual(idea[2], ("name", "=", '"has # inside"', 5))

	def test_stray_top_level_brace_does_not_end_the_parse(self):
		self.assertEqual(clausewitz.parse(SCRIPT)[1], (None, None, "bare_token", 8))

	def test_pairs_unquote_and_flatten_comparisons(self):
		pairs = clausewitz.pairs(clausewitz.parse(SCRIPT))
		idea = pairs[0][1]
		self.assertEqual(idea[0], ("picture", "my_picture"))
		self.assertEqual(idea[1][1][0][1], [(None, "x"), (None, ">"), (None, "3")])

	def test_comment_stripping_respects_quotes(self):
		self.assertEqual(clausewitz.strip_comment('name = "a # b" # tail'), 'name = "a # b" ')
		self.assertEqual(clausewitz.strip_comments("a # x\nb"), "a \nb")


class Localisation(unittest.TestCase):
	def test_entries_handle_ordinals_comments_and_hash_in_values(self):
		text = 'l_english:\n # note\n key_a: "Plain"\n key_b:0 "With ordinal" # comment\n key_c: "§Ycolour # kept§!"\nbroken line\n'
		got = [(e.line, e.key, e.ordinal, e.value) for e in localisation.entries(text)]
		self.assertEqual(got, [(3, "key_a", None, "Plain"), (4, "key_b", "0", "With ordinal"), (5, "key_c", None, "§Ycolour # kept§!")])
		self.assertTrue(localisation.HEADER_LINE.match("l_english:"))


if __name__ == "__main__":
	unittest.main()
