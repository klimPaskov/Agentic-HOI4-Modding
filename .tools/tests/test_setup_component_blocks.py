"""Every HOI4 Mod Setup component block in the package must be complete.

HOI4 Mod Setup keeps or drops `<!-- HOI4_MOD_SETUP:COMPONENT:<id>:START -->` ... `END -->` blocks
depending on whether the named component is installed (`adapt_component_blocks` in the app's
`hoi4-setup-core/src/adapt.rs`). It reads only markers that start a line, and it refuses a file with
a block left open, a stray end or a nested start. One such file stops every install. The test reads
every text file the way the app does. Run from the package root:

	python -m unittest discover -s .tools/tests -p "test_*.py"
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
# The app's own pattern: a marker counts only at the start of a line, after spaces or tabs.
MARKER = re.compile(
	r"(?m)^[ \t]*<!-- HOI4_MOD_SETUP:COMPONENT:([a-z0-9][a-z0-9._-]{0,127}):(START|END) -->"
)
# The same marker anywhere; a placeholder such as `<component>` in prose is not a marker.
ANY_MARKER = re.compile(r"<!-- HOI4_MOD_SETUP:COMPONENT:([a-z0-9][a-z0-9._-]{0,127}):(START|END) -->")


def block_problems(text: str) -> List[str]:
	problems = []
	if len(MARKER.findall(text)) != len(ANY_MARKER.findall(text)):
		problems.append("a marker that does not start its own line")
	open_component = None
	for component, kind in MARKER.findall(text):
		if kind == "START":
			if open_component:
				problems.append(f"{component} starts inside {open_component}")
				break
			open_component = component
		elif open_component != component:
			problems.append(f"stray end of {component}")
			break
		else:
			open_component = None
	if open_component and not problems:
		problems.append(f"{open_component} is never closed")
	return problems


class SetupComponentBlocks(unittest.TestCase):
	def test_every_tracked_text_file_has_complete_blocks(self) -> None:
		tracked = subprocess.run(
			["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
		).stdout.decode("utf-8").split("\0")
		failures = []
		for name in filter(None, tracked):
			path = ROOT / name
			try:
				text = path.read_text(encoding="utf-8")
			except (OSError, UnicodeDecodeError):
				continue
			if "HOI4_MOD_SETUP:COMPONENT:" in text:
				failures += [f"{name}: {problem}" for problem in block_problems(text)]
		self.assertEqual(failures, [])

	def test_the_reader_finds_each_kind_of_broken_block(self) -> None:
		start = "<!-- HOI4_MOD_SETUP:COMPONENT:workflow.live_tools:START -->"
		end = "<!-- HOI4_MOD_SETUP:COMPONENT:workflow.live_tools:END -->"
		self.assertEqual(block_problems(f"a\n{start}\nb\n{end}\n"), [])
		self.assertEqual(block_problems(f"a\n{start}\n"), ["workflow.live_tools is never closed"])
		self.assertEqual(block_problems(f"{end}\n"), ["stray end of workflow.live_tools"])
		self.assertIn("a marker that does not start its own line", block_problems(f"text {start}\n{end}\n"))


if __name__ == "__main__":
	unittest.main()
