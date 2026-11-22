#!/usr/bin/env python3
"""Static checks for interface engine rules that a render does not show (`hoi4-scripted-gui`, Engine behaviour).

Rules, under the `.tools/lib/report.py` contract:

- `GUI-TEXT-EXTENDED-SCROLLBAR` (error): a text box's `scrollbartype` names an `extendedScrollbarType`. A text
  box takes only a plain `scrollbarType` (the base game's `standardtext_slider`, `standardlistbox_slider`); an
  extended one is for a list's `verticalScrollbar`, and on a text box the game crashed at load.
- `GUI-QUOTED-WORD` (error): `format = "left"` (any quoted lower-case format word) logs "Unknown format token",
  and a quoted lower-case `orientation` on a top-level window logs "Not a valid orientation". Write the bare
  word (`format = left`) or the quoted upper-case word (`"LEFT"`).
- `GUI-EVENT-PLACEMENT` (error, `interface/eventwindow.gui` only): in a window that has a `midsection`, the
  element `Description` must be a direct child of `midsection` (the engine looks for it there and nowhere
  else and shows its placeholder text otherwise); in the plain event window `EventWindow`, `event_picture`
  must be inside `bottom_Window` (the engine binds its picture only there; the news window keeps its own in
  its header).
- `GUI-NEGATIVE-SIZE` (review): a negative `height` (or `width`) larger than the element's own `y` (or `x`).
  The engine reads a negative size as the fill from the element's own place to its parent's far edge, less
  that much; a value larger than the offset is usually written as "the parent's size less the offset and
  the gap" and collapses the element in the game. Write the gap alone. (Renderers and some lints read it
  the other way, so a render does not show the collapse.)
Scrollbar types are read from the mod's `interface/` folder and, when it is found (`.tools/lib/game.py`),
the installed game's. The reading is structural only: it cannot know which elements the engine fills,
hides or disables at run time.

Usage:
	python -B .tools/audits/audit_gui_rules.py
	python -B .tools/audits/audit_gui_rules.py --paths interface/eventwindow.gui
	python -B .tools/audits/audit_gui_rules.py --json .tmp/gui_rules.json

With `--paths`, only those `.gui` files or folders are scanned. Exit status: 0 no errors, 1 errors.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # .tools, for the shared lib package
from lib.clausewitz import Node, parse, unquote
from lib.game import game_dir, missing_game_dir
from lib.report import Finding, PathFilter, add_arguments, exit_code, merge_json, print_findings, relative, requested_paths

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK = "gui-rules"
LEVELS = {
	"GUI-TEXT-EXTENDED-SCROLLBAR": "error",
	"GUI-QUOTED-WORD": "error",
	"GUI-EVENT-PLACEMENT": "error",
	"GUI-NEGATIVE-SIZE": "review",
}
TEXT_BOXES = {"instanttextboxtype", "textboxtype"}
GREYING_EFFECTS = {"gfx/fx/buttonstate.lua", "gfx/fx/buttonstate_nodowneffect.lua", "gfx/fx/buttonstate_onlydisable.lua"}
SPRITE_KEYS = {"spritetype", "quadtexturesprite"}
POSITION = re.compile(r"(-?\d+)")


def _blocks(nodes: List[Node]) -> Iterable[Node]:
	for node in nodes:
		if isinstance(node[2], list):
			yield node


def _scalar(nodes: List[Node], key: str) -> Optional[str]:
	for k, _, value, _ in nodes:
		if k is not None and k.lower() == key and not isinstance(value, list):
			return unquote(value)
	return None


def _block(nodes: List[Node], key: str) -> Optional[List[Node]]:
	for k, _, value, _ in nodes:
		if k is not None and k.lower() == key and isinstance(value, list):
			return value
	return None


def _number(nodes: Optional[List[Node]], *keys: str) -> Optional[int]:
	if nodes is None:
		return None
	for key in keys:
		raw = _scalar(nodes, key)
		if raw is not None:
			match = POSITION.fullmatch(raw.strip())
			if match:
				return int(match.group(1))
	return None


def definitions(folders: Iterable[Path]) -> Dict[str, object]:
	"""The extended scrollbar type names and every sprite's effect file, from .gui and .gfx files."""
	extended: Set[str] = set()
	effects: Dict[str, str] = {}
	for folder in folders:
		if not folder.is_dir():
			continue
		for path in folder.rglob("*"):
			if path.suffix.lower() not in (".gui", ".gfx"):
				continue
			try:
				nodes = parse(path.read_bytes().decode("utf-8-sig", errors="replace"))
			except (OSError, RecursionError):
				continue
			stack = list(nodes)
			while stack:
				key, _, value, _ = stack.pop()
				if not isinstance(value, list):
					continue
				kind = (key or "").lower()
				name = _scalar(value, "name")
				if kind == "extendedscrollbartype" and name:
					extended.add(name)
				elif name and kind.endswith("spritetype") or kind in ("frameanimatedspritetype", "corneredtilespritetype", "progressbartype"):
					effect = _scalar(value, "effectfile")
					if name and effect:
						effects[name] = effect.replace("\\", "/").replace("//", "/").lower()
				stack.extend(value)
	return {"extended": extended, "effects": effects}


def scan_text(path: str, text: str, known: Dict[str, object]) -> List[Finding]:
	"""Return the rule findings for one .gui file's text."""
	findings: List[Finding] = []
	extended: Set[str] = known.get("extended", set())  # type: ignore[assignment]
	nodes = parse(text)
	event_file = path.replace("\\", "/").lower().endswith("interface/eventwindow.gui")

	def walk(items: List[Node], depth: int) -> None:
		for key, _, value, line in _blocks(items):
			kind = (key or "").lower()
			name = _scalar(value, "name") or ""
			if kind in TEXT_BOXES:
				bar = _scalar(value, "scrollbartype")
				if bar and bar in extended:
					findings.append(Finding(CHECK, "GUI-TEXT-EXTENDED-SCROLLBAR", "error", path, line,
						f"text box `{name}` names the extended scrollbar `{bar}`; a text box takes a plain scrollbarType (standardtext_slider)"))
			for k, _, v, l in value:
				if k is None or isinstance(v, list):
					continue
				if k.lower() == "format" and v.startswith('"') and unquote(v) != unquote(v).upper():
					findings.append(Finding(CHECK, "GUI-QUOTED-WORD", "error", path, l,
						f"`format = {v}` is an unknown format token; write it bare or in upper case"))
				if k.lower() == "orientation" and depth == 1 and v.startswith('"') and unquote(v) != unquote(v).upper():
					findings.append(Finding(CHECK, "GUI-QUOTED-WORD", "error", path, l,
						f"`orientation = {v}` on top-level window `{name}` is not a valid orientation; write it bare or in upper case"))
			if kind in ("containerwindowtype", "windowtype") or kind in TEXT_BOXES or kind.endswith("type"):
				size = _block(value, "size")
				position = _block(value, "position")
				for size_keys, pos_keys, axis in ((("height", "y"), ("y",), "y"), (("width", "x"), ("x",), "x")):
					d = _number(size, size_keys[0], size_keys[1])
					p = _number(position, *pos_keys)
					if d is not None and d < 0 and p is not None and -d > p > 0:
						findings.append(Finding(CHECK, "GUI-NEGATIVE-SIZE", "review", path, line,
							f"`{name}` at {axis} {p} has {size_keys[0]} {d}: the engine fills from the element's own place to the parent's edge less {-d}; if {-d} was meant as the parent's size less the place and a gap, write the gap alone"))
			walk(value, depth + 1)

	for key, _, value, _ in _blocks(nodes):
		if (key or "").lower() == "guitypes":
			walk(value, 1)
	if event_file:
		findings += event_placement(path, nodes)
	return findings


def _children(nodes: List[Node]) -> List[List[Node]]:
	return [value for _, _, value, _ in _blocks(nodes)]


def _named(nodes: List[Node], name: str) -> List[Node]:
	"""Every block below `nodes` (any depth) whose `name` is `name`, with its parent's block."""
	found = []
	stack = [(nodes, None)]
	while stack:
		items, parent = stack.pop()
		for node in _blocks(items):
			if _scalar(node[2], "name") == name:
				found.append((node, parent))
			stack.append((node[2], node))
	return found  # type: ignore[return-value]


def event_placement(path: str, nodes: List[Node]) -> List[Finding]:
	findings: List[Finding] = []
	guitypes = next((value for key, _, value, _ in _blocks(nodes) if (key or "").lower() == "guitypes"), [])
	for window in _blocks(guitypes):
		mids = _named(window[2], "midsection")
		if mids:
			mid_block = mids[0][0][2]
			direct = {id(n) for n in _blocks(mid_block)}
			for (node, _parent) in _named(window[2], "Description"):
				if id(node) not in direct:
					findings.append(Finding(CHECK, "GUI-EVENT-PLACEMENT", "error", path, node[3],
						"`Description` is not a direct child of `midsection`: the engine looks for it there only and shows its placeholder text"))
		bottoms = _named(window[2], "bottom_Window")
		if bottoms and _scalar(window[2], "name") == "EventWindow":
			inside = {id(n) for n, _ in _named(bottoms[0][0][2], "event_picture")}
			for (node, _parent) in _named(window[2], "event_picture"):
				if id(node) not in inside:
					findings.append(Finding(CHECK, "GUI-EVENT-PLACEMENT", "error", path, node[3],
						"`event_picture` is not inside `bottom_Window`: the engine binds the event picture there only"))
	return findings


def gui_files(paths: Iterable[str] = ()) -> List[Path]:
	selector = PathFilter(list(paths))
	base = REPO_ROOT / "interface"
	if not base.is_dir():
		return []
	return sorted(p for p in base.rglob("*.gui") if selector.matches(relative(p.resolve())))


def known_definitions() -> Dict[str, object]:
	folders = [REPO_ROOT / "interface"]
	# the game is optional here: without it the mod's own definitions are still read
	if missing_game_dir() is None:
		folders.insert(0, game_dir() / "interface")
	return definitions(folders)


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	parser.add_argument("--json", type=Path, help="also write the findings as JSON")
	add_arguments(parser)
	arguments = parser.parse_args()
	paths = requested_paths(arguments)
	known = known_definitions()
	findings: List[Finding] = []
	for path in gui_files(paths or ()):
		text = path.read_bytes().decode("utf-8-sig", errors="replace")
		findings += scan_text(relative(path.resolve()), text, known)
	findings.sort(key=lambda f: (f.path, f.line, f.rule, f.message))
	print_findings(CHECK, findings)
	if arguments.json:
		merge_json(arguments.json, findings, LEVELS)
	return exit_code(findings, arguments.fail_on)


if __name__ == "__main__":
	raise SystemExit(main())
