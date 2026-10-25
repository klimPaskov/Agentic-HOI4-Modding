#!/usr/bin/env python3
"""Static audit of a mod's English localisation against its script tree.

This tool answers six source-only questions without running the game:

1. Does every localisation file parse as `key: "value"` under an `l_english:`
   header, and does it keep its UTF-8 BOM?
2. Are any keys duplicated, either inside one file or across the localisation
   set? The engine keeps one definition per key, so duplicates mean the wiring
   is non-deterministic.
3. Which localisation keys are referenced by script or localisation but never
   defined here? Those render as raw key names in game.
4. Which defined keys are never referenced by any script token or
   `[bracket]` command? Those are candidates for removal.
5. Which flags and variables checked in a displayed decision, mission, or focus
   requirement have no localisation key? Their tooltips show the raw identifier.
6. Which keys does the engine look up implicitly that neither this mod nor the
   installed vanilla English localisation defines? That covers the id and
   `_desc` of decisions, categories, ideas, focuses, technologies and
   equipment, country tag and cosmetic tag names, achievement `_NAME` and
   `_DESC`, dynamic and opinion modifiers, traits, sub-units, doctrines, event
   titles, descriptions and option names, GUI text, and the keys that effects
   and triggers name directly (`custom_effect_tooltip`, the `tooltip` of
   `custom_trigger_tooltip`, `custom_cost_text`, scripted-localisation
   targets). It also reports scripted-localisation getters that nothing
   defines. See the "Implicit engine keys" section for the rules.

The token test is deliberately conservative. A key counts as live when its
exact name appears as a token anywhere in the non-localisation tree, so a key
that is only built dynamically still survives the sweep and is reported as
`dynamic_candidate` instead of dead.

Usage:
	python .tools/audits/audit_localisation_static.py                # report to stdout
	python .tools/audits/audit_localisation_static.py --json out.json
	python .tools/audits/audit_localisation_static.py --show-advisory   # also list empty-text gaps
	python .tools/audits/audit_localisation_static.py --calibrate       # vanilla coverage per rule
	python .tools/audits/audit_localisation_static.py --paths localisation/english/x.yml events/x.txt
	python .tools/audits/audit_localisation_static.py --root path/to/mod   # audit another mod folder

Levels and exit status follow `.tools/lib/report.py`. Parse, BOM, header, encoding,
duplicate, undefined-binding, event title/description, requirement-tooltip and required
implicit-key findings are `error`; unmatched dynamic keys are `warning`; dead keys, literal
names, expanded triggers and advisory implicit keys are `review`. The command exits 1 when
an error is reported, unless `--fail-on none` is given. With `--paths` the console lists only
the findings located in those files or folders. `--root` audits another mod folder; paths in the
report are then relative to that folder.
"""

from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # .tools, for the shared lib package
from lib.game import game_dir, require_game_dir
from lib.clausewitz import parse
from lib.localisation import BOM, HEADER_LINE, LOC_LINE, read_text
from lib.report import relative as report_relative
from lib.report import (
	Finding, add_arguments, exit_code, merge_json, print_findings, requested_paths, select, split_site,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCALISATION_DIR = REPO_ROOT / "localisation" / "english"

# Directories that are documentation, archived history, or tooling rather than
# engine-parsed mod content. They must not contribute "live" token evidence.
EXCLUDED_TOP_LEVEL = {
	".git",
	".tools",
	".tmp",
	".agents",
	".claude",
	".codex",
	".cursor",
	".opencode",
	".qoder",
	"docs",
	"history",
	"paradox_wiki",
	"localisation",
}

SCRIPT_SUFFIXES = {".txt", ".gui", ".gfx", ".asset", ".json", ".md", ".yml"}

# Tokens we treat as script references. Keeps letters, digits, underscore, dot.
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]*")

# `[Some.Getter]` and `[?var]` references inside localisation values.
BRACKET_REF = re.compile(r"\[([^\]]+)\]")



class Findings:
	def __init__(self) -> None:
		self.parse_errors: List[str] = []
		self.missing_bom: List[str] = []
		self.no_header: List[str] = []
		self.duplicates: List[Tuple[str, str, int, str, int]] = []
		self.missing_event_roots: List[Tuple[str, List[str]]] = []
		self.missing_prefixed: List[Tuple[str, List[str]]] = []
		self.literal_names: List[Tuple[str, List[str]]] = []
		self.missing_event_content: List[Tuple[str, str, List[str]]] = []
		self.dynamic_candidates: List[Tuple[str, str]] = []
		self.dead_keys: List[Tuple[str, str]] = []
		self.encoding_artifacts: List[Tuple[str, int, str]] = []
		self.exposed_flags: List[Tuple[str, str]] = []
		self.exposed_variables: List[Tuple[str, str]] = []
		self.expanded_triggers: List[str] = []
		self.implicit_missing: Dict[Tuple[str, str], Dict[str, Tuple[str, int, int]]] = {}
		self.implicit_totals: Dict[Tuple[str, str], int] = {}
		self.implicit_dynamic: List[Tuple[str, str, str, int, str]] = []
		self.key_count = 0
		self.file_count = 0


def iter_script_files() -> Iterable[Path]:
	"""Yield engine-parsed mod files that can reference a localisation key."""
	for entry in REPO_ROOT.iterdir():
		if entry.name in EXCLUDED_TOP_LEVEL:
			continue
		paths = (entry,) if entry.is_file() else entry.rglob("*")
		for path in paths:
			if path.is_file() and path.suffix.lower() in SCRIPT_SUFFIXES:
				yield path


COMMENT_TAIL = re.compile(r"(?m)(?:^|(?<=\s))#.*$")


def strip_comments(text: str) -> str:
	"""Blank out `#` comments but keep every newline, so line numbers still match."""
	return COMMENT_TAIL.sub("", text)


def collect_script_tokens() -> Tuple[Set[str], Set[str], Dict[str, Set[str]]]:
	"""Return every identifier token, every bracket ref, and token->file index."""
	tokens: Set[str] = set()
	bracket_refs: Set[str] = set()
	per_file: Dict[str, Set[str]] = defaultdict(set)

	for path in iter_script_files():
		try:
			text = read_text(path)
		except OSError as error:
			print(f"warning: cannot read {path}: {error}", file=sys.stderr)
			continue
		rel = str(path.relative_to(REPO_ROOT))
		for match in TOKEN.finditer(text):
			value = match.group(0)
			tokens.add(value)
			per_file[value].add(rel)
		for match in BRACKET_REF.finditer(text):
			# `[ROOT.GetName]` -> add the whole command and each dotted part.
			inner = match.group(1).lstrip("?")
			bracket_refs.add(inner)
			for part in inner.split("."):
				bracket_refs.add(part.strip())

	return tokens, bracket_refs, per_file


def collect_dynamic_scripted_localisation() -> Set[str]:
	"""Return loc-key prefixes that scripted localisation builds at runtime.

	`common/scripted_localisation/` deliberately assembles keys such as
	`my_mod.log_name.100.t` from data, so a key with one of these prefixes is
	live even when no literal reference to it exists.
	"""
	prefixes: Set[str] = set()
	directory = REPO_ROOT / "common" / "scripted_localisation"
	if not directory.is_dir():
		return prefixes

	for path in sorted(directory.glob("*.txt")):
		text = read_text(path)
		for match in re.finditer(r'(?:localisation_key|text)\s*=\s*"([^"]+)"', text):
			value = match.group(1)
			if value:
				prefixes.add(value)
				# Also register the dotted root so `a.b.1.t` matches on `a.b`.
				parts = value.split(".")
				for length in range(1, len(parts)):
					prefixes.add(".".join(parts[:length]))
	return prefixes


def parse_localisation(findings: Findings) -> Dict[str, List[Tuple[str, int]]]:
	"""Parse every localisation file, recording keys and structural problems."""
	definitions: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

	for path in sorted(LOCALISATION_DIR.glob("*.yml")):
		findings.file_count += 1
		rel = str(path.relative_to(REPO_ROOT))
		raw = path.read_bytes()
		if not raw.startswith(BOM):
			findings.missing_bom.append(rel)
		text = read_text(path)
		lines = text.splitlines()

		# The `l_english:` header may sit below a banner comment block, so find
		# the first content line rather than assuming it is line 1.
		header_index = None
		for number, line in enumerate(lines, start=1):
			stripped = line.strip()
			if not stripped or stripped.startswith("#"):
				continue
			header_index = number
			break
		if header_index is None or not HEADER_LINE.match(lines[header_index - 1].strip()):
			findings.no_header.append(rel)

		for number, line in enumerate(lines, start=1):
			stripped = line.strip()
			if not stripped or stripped.startswith("#"):
				continue
			if number == header_index and HEADER_LINE.match(stripped):
				continue
			match = LOC_LINE.match(stripped)
			if match is None:
				findings.parse_errors.append(f"{rel}:{number}: {stripped[:120]}")
				continue

			key = match.group("key")
			value = match.group("value")
			findings.key_count += 1
			definitions[key].append((rel, number))

			if match.group("ordinal"):
				findings.encoding_artifacts.append((rel, number, f"ordinal suffix on {key}"))
			if "\ufffd" in value:
				findings.encoding_artifacts.append((rel, number, f"replacement character in {key}"))

	return definitions


def classify(
	definitions: Dict[str, List[Tuple[str, int]]],
	tokens: Set[str],
	bracket_refs: Set[str],
) -> None:
	"""Split defined keys into live, dynamic-only, and dead."""
	findings = AUDIT_FINDINGS
	for key, sites in sorted(definitions.items()):
		if len(sites) > 1:
			first = sites[0]
			for other in sites[1:]:
				findings.duplicates.append((key, first[0], first[1], other[0], other[1]))

		if key in tokens or key in bracket_refs:
			continue

		# Event-style keys are referenced by their numeric root, never verbatim:
		# `my_mod.6.t` is produced by the engine from event id `my_mod.6`.
		parts = key.rsplit(".", 1)
		if len(parts) == 2 and len(parts[1]) <= 3 and parts[0] in tokens:
			continue

		# A dynamic key may be assembled from a token prefix plus a variable, so
		# keep anything whose longest dot-prefix is a live token.
		prefix = key
		matched = False
		while "." in prefix:
			prefix = prefix.rsplit(".", 1)[0]
			if prefix in tokens:
				findings.dynamic_candidates.append((key, prefix))
				matched = True
				break
		if not matched:
			findings.dead_keys.append((key, sites[0][0]))


def collect_scripted_identifiers() -> Set[str]:
	"""Return registered scripted effect, trigger, and scripted-loc names."""
	identifiers: Set[str] = set()
	roots = [
		REPO_ROOT / "common" / "scripted_effects",
		REPO_ROOT / "common" / "scripted_triggers",
		REPO_ROOT / "common" / "scripted_localisation",
		REPO_ROOT / "common" / "scripted_guis",
	]
	definition = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{")

	for root in roots:
		if not root.is_dir():
			continue
		for path in sorted(root.rglob("*.txt")):
			for line in read_text(path).splitlines():
				match = definition.match(line)
				if match:
					identifiers.add(match.group(1))
	return identifiers


class EventRecord:
	"""What an event block declares about its own text bindings."""

	__slots__ = ("file", "event_id", "hidden", "explicit_title", "explicit_desc")

	def __init__(self, file: str, event_id: str = "") -> None:
		self.file = file
		self.event_id = event_id
		self.hidden = False
		self.explicit_title: Optional[str] = None
		self.explicit_desc: Optional[str] = None


def collect_event_roots() -> Dict[str, EventRecord]:
	"""Return every declared event with the text bindings it actually declares.

	An event either follows the `<id>.t` / `<id>.d` convention or binds its text
	explicitly with `title =` / `desc =`. Both forms are used across this
	repository, so the localisation check must read the binding rather than
	assume the convention. A `hidden = yes` event shows no window text at all
	and is excluded from the requirement.

	Event blocks are recognised by their distinctive markers (`is_triggered_only`,
	`option =`, `mean_time_to_happen`, ...) plus brace depth measured relative to
	each candidate's own block, which keeps `id =` keys inside options, power
	balances, and characters out of the event set.
	"""
	events: Dict[str, EventRecord] = {}
	declaration = re.compile(r"^\s*id\s*=\s*([A-Za-z_][A-Za-z0-9_.]*)\s*$")
	hidden_flag = re.compile(r"^\s*hidden\s*=\s*yes\s*$")
	title_binding = re.compile(r"^\s*title\s*=\s*([A-Za-z_][A-Za-z0-9_.]*)\s*$")
	desc_binding = re.compile(r"^\s*desc\s*=\s*([A-Za-z_][A-Za-z0-9_.]*)\s*$")
	quoted_text = re.compile(r'^\s*(?:title|desc)\s*=\s*"')
	# Markers that only an event block carries. `trigger` and `immediate` are
	# excluded because options, decisions, and characters also use them.
	markers = (
		re.compile(r"^\s*is_triggered_only\s*="),
		re.compile(r"^\s*fire_only_once\s*="),
		re.compile(r"^\s*is_fire_only_once\s*="),
		re.compile(r"^\s*mean_time_to_happen\s*="),
		re.compile(r"^\s*option\s*=\s*\{"),
		re.compile(r"^\s*major\s*="),
		re.compile(r"^\s*news\s*="),
		re.compile(r"^\s*timeout_days\s*="),
	)
	# Engine scope keywords can appear as an `id` value but are not event ids.
	scopes = {
		"ROOT", "THIS", "PREV", "FROM", "OWNER", "CONTROLLER", "OVERLORD", "CAPITAL",
	}

	events_dir = REPO_ROOT / "events"
	if not events_dir.is_dir():
		return events

	def note(current: EventRecord, text: str) -> bool:
		"""Record one attribute line on `current`; True when the line marks an event block."""
		if hidden_flag.match(text):
			current.hidden = True
		elif quoted_text.match(text):
			# The text is supplied inline, so no key is required for
			# that field; a quoted desc is legal HOI4 script.
			current.explicit_desc = current.explicit_desc or ""
			current.explicit_title = current.explicit_title or ""
		else:
			title = title_binding.match(text)
			if title:
				current.explicit_title = title.group(1)
			else:
				desc = desc_binding.match(text)
				if desc:
					current.explicit_desc = desc.group(1)
		return any(marker.match(text) for marker in markers)

	for path in sorted(events_dir.rglob("*.txt")):
		rel = str(path.relative_to(REPO_ROOT))
		record: Optional[EventRecord] = None
		candidate_depth: Optional[int] = None
		qualified = False
		depth = 0

		def resolve() -> None:
			nonlocal record, candidate_depth, qualified
			if record is not None and qualified:
				events[record.event_id] = record
			record = None
			candidate_depth = None
			qualified = False

		for line in read_text(path).splitlines():
			match = declaration.match(line)
			if match:
				candidate = match.group(1)
				if candidate not in scopes:
					resolve()
					record = EventRecord(rel, candidate)
				depth += line.count("{") - line.count("}")
				continue

			if record is not None:
				# Attributes before the opening brace sit at the current depth,
				# so they are checked both before and after this line's braces
				# are counted. HOI4 events put `is_triggered_only = yes` and
				# friends between the `id` line and the `{`.
				if candidate_depth is None:
					qualified = note(record, line) or qualified

				if candidate_depth is None and "{" in line:
					candidate_depth = depth + 1

				if candidate_depth is not None and depth == candidate_depth:
					qualified = note(record, line) or qualified

			depth += line.count("{") - line.count("}")

			if candidate_depth is not None and depth < candidate_depth:
				resolve()

		resolve()

	return events


def audit_event_loc_keys(
	events: Dict[str, EventRecord],
	definitions: Dict[str, List[Tuple[str, int]]],
) -> None:
	"""Check every visible event's title and description against localisation.

	An event that binds `title =` or `desc =` is checked against that exact key;
	otherwise the `<id>.t` / `<id>.d` convention is expected. A missing key
	renders as a raw key name in the event window.
	"""
	findings = AUDIT_FINDINGS

	for event_id, record in sorted(events.items()):
		if record.hidden:
			continue
		required = (
			("title", record.explicit_title or f"{event_id}.t"),
			("description", record.explicit_desc or f"{event_id}.d"),
		)
		for role, key in required:
			# An empty binding means the value was supplied inline as a quoted
			# string, which needs no localisation key.
			if not key:
				continue
			if key not in definitions:
				findings.missing_event_content.append((key, role, [record.file]))


def collect_quoted_keys() -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
	"""Index localisation bindings from localisation-consuming definitions.

	Two binding forms are collected separately because only one is a
	localisation reference:

	- Quoted values (`name = "Some Name"`) are literal strings. The engine uses
	  them verbatim, so they must NOT be reported as missing keys. This is the
	  documented `set_province_name = { id = <id> name = <string> }` form.
	- Bare identifiers (`name = SOME_KEY`) are localisation references.

	Only specific field names consume localisation, and only inside definition
	folders that bind them, so unit type names, equipment archetypes, mesh
	names, and sound names are excluded by construction.
	"""
	quoted: Dict[str, Set[str]] = defaultdict(set)
	bare: Dict[str, Set[str]] = defaultdict(set)
	shape = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]*$")

	# Folders whose definitions bind localisation keys by name.
	SCAN_DIRS = (
		"events",
		"common/decisions",
		"common/ideas",
		"common/national_focus",
		"common/characters",
		"common/missions",
		"common/scripted_guis",
		"common/operations",
		"common/units",
		"common/technologies",
		"common/doctrines",
		"common/continuous_focus",
		"common/decisions/categories",
		"common/achievements",
		"common/dynamic_modifiers",
		"common/opinion_modifiers",
		"common/raids",
		"common/special_projects",
		"common/abilities",
		"common/combat_tactics",
	)

	# Field names whose value is looked up in localisation.
	LOC_FIELDS = (
		"name",
		"desc",
		"title",
		"text",
		"tooltip",
		"localisation_key",
		"custom_effect_tooltip",
		"custom_trigger_tooltip",
		"custom_idea_tooltip",
		"complete_effect_tooltip",
		"available_tooltip",
		"effect_tooltip",
		"select_effect_tooltip",
		"visible_tooltip",
		"mission_text",
		"description",
	)
	# A loc field may only be matched as a whole token, which needs a guard on
	# both sides. The lookbehind rejects a preceding word character or
	# underscore, so `mutually_exclusive` no longer matches `text`+`t`+`name`.
	# The lookahead rejects a following word character, so the literal `name`
	# inside identifiers such as `ICE_advanced_technology` is not a match.
	# Both produced phantom keys before these guards.
	guard = r"(?<![\w_])"
	tail = r"(?![\w])"
	field = guard + r"(?:" + "|".join(LOC_FIELDS) + r")" + tail + r"\s*="
	quoted_pattern = re.compile(field + r'\s*"([^"\n]{1,120})"')
	# A value followed by `|` is a loc formatter call (`tech_effect|radio_detection`), not a key.
	bare_pattern = re.compile(field + r"\s*([A-Za-z_][A-Za-z0-9_.\-]*)(?![A-Za-z0-9_.\-|])")

	for relative in SCAN_DIRS:
		root = REPO_ROOT / relative
		if not root.is_dir():
			continue
		for path in sorted(root.rglob("*.txt")):
			try:
				text = strip_comments(read_text(path))
			except OSError:
				continue
			rel = str(path.relative_to(REPO_ROOT))
			for match in quoted_pattern.finditer(text):
				value = match.group(1).strip()
				if value and shape.match(value):
					quoted[value].add(rel)
			for match in bare_pattern.finditer(text):
				value = match.group(1).strip()
				if value and shape.match(value):
					bare[value].add(rel)

	return quoted, bare


EVENT_NAMESPACE = re.compile(r"^\s*add_namespace\s*=\s*([A-Za-z0-9_.]+)", re.M)


def collect_event_namespaces() -> Set[str]:
	"""Return every event namespace that the mod's event files declare with `add_namespace`."""
	namespaces: Set[str] = set()
	events_dir = REPO_ROOT / "events"
	if events_dir.is_dir():
		for path in sorted(events_dir.rglob("*.txt")):
			namespaces.update(EVENT_NAMESPACE.findall(strip_comments(read_text(path))))
	return namespaces


def is_event_root(literal: str, namespaces: Set[str]) -> bool:
	"""True for `<namespace>.<number>`, an event id whose keys the engine derives by suffix."""
	namespace, _, number = literal.rpartition(".")
	return number.isdigit() and namespace in namespaces


def collect_referenced_keys(
	tokens: Set[str],
	definitions: Dict[str, List[Tuple[str, int]]],
	known: Set[str],
	quoted: Dict[str, Set[str]],
	bare: Dict[str, Set[str]],
	dynamic_prefixes: Set[str],
	scripted_tokens: Set[str],
) -> None:
	"""Flag loc keys that script references but localisation never defines.

	Evidence is a bare identifier bound to a localisation-consuming field, which
	is the form the engine resolves as a key. A quoted value is a literal string
	and is never reported. `known` holds this mod's keys, its `replace` folder, and
	the installed game's English keys, so a key vanilla defines is not reported.

	Two shapes are reported separately because they fail differently in game:

	- Event roots (`<namespace>.<number>`, for a namespace that an event file
	  declares with `add_namespace`) never appear verbatim in localisation; the
	  engine builds `<root>.t`, `.d`, `.a`, `.b`, ... so the test is whether any
	  defined key carries the root as a dotted prefix.
	- Flat keys are checked literally, excluding values that scripted
	  localisation assembles at runtime.
	"""
	findings = AUDIT_FINDINGS

	dotted_roots: Set[str] = set()
	for key in definitions:
		parts = key.split(".")
		for length in range(2, len(parts)):
			dotted_roots.add(".".join(parts[:length]))

	namespaces = collect_event_namespaces()
	# Effect/trigger and engine keywords are registered in common/, not
	# localisation, and are frequently written in the same `x = y` shape.
	keyword_shapes = re.compile(
		r"^(?:set_|add_|remove_|has_|is_|get_|clear_|every_|any_|random_|all_|count_|clamp_)"
	)
	# Engine-owned tokens that appear as values but are never loc keys.
	reserved = {
		"yes",
		"no",
		"ROOT",
		"THIS",
		"PREV",
		"FROM",
		"OWNER",
		"CONTROLLER",
		"OVERLORD",
		"CAPITAL",
		"undefined",
	}

	for literal in sorted(bare):
		if literal in known or literal in dynamic_prefixes:
			continue
		if literal in scripted_tokens or literal in reserved:
			continue
		if keyword_shapes.match(literal):
			continue

		if is_event_root(literal, namespaces):
			if literal in dotted_roots:
				continue
			findings.missing_event_roots.append((literal, sorted(bare[literal])[:3]))
			continue

		findings.missing_prefixed.append((literal, sorted(bare[literal])[:3]))

	# A quoted value that is never defined is still worth surfacing as context
	# for review, but it is not a defect, so it is reported separately.
	for literal in sorted(quoted):
		if literal in known or literal in dynamic_prefixes:
			continue
		if literal in scripted_tokens:
			continue
		if re.match(r"^[A-Z][a-z]+$", literal):
			findings.literal_names.append((literal, sorted(quoted[literal])[:2]))


# A flag trigger inside a displayed requirement block uses the flag name as its
# tooltip localisation key, so an undefined key shows the raw flag identifier.
# A variable comparison reads the variable name the same way. Displayed blocks
# are decision and mission `available` and focus `available` and `bypass`, plus
# every scripted trigger they call, followed transitively. Checks inside
# `hidden_trigger` or `custom_trigger_tooltip` are not displayed, and a scripted
# trigger whose own name is a localisation key replaces its expansion with that
# text, so its body is not followed.
VANILLA_LOCALISATION_DIR = game_dir() / "localisation" / "english"
REQUIREMENT_BLOCKS = {"available", "bypass"}
UNDISPLAYED_BLOCKS = {"hidden_trigger", "custom_trigger_tooltip"}
# Names followed by `[` are assembled at runtime by meta effects and are skipped.
FLAG_CHECK = r"has_(?:country|state|global)_flag\s*=\s*(?:\{[^}]*?flag\s*=\s*([A-Za-z0-9_@.]+)(?![A-Za-z0-9_@.\[])[^}]*\}|([A-Za-z0-9_@.]+)(?![A-Za-z0-9_@.\[]))"
VARIABLE_CHECK = (
	r"|check_variable\s*=\s*\{\s*(?:var\s*=\s*)?([A-Za-z_][A-Za-z0-9_.@:^\-]*)\s*(?:[<>=]|!=|\n|value\b|compare\b)"
	r"|has_variable\s*=\s*([A-Za-z_][A-Za-z0-9_.@:^\-]*)"
)
VARIABLE_KEYWORDS = {"var", "value", "compare", "tooltip"}
REQUIREMENT_TOKEN = re.compile(
	r"([A-Za-z0-9_@:.^\-]+)\s*=\s*(\{|yes\b)|\}|" + FLAG_CHECK + VARIABLE_CHECK
)


def scan_requirement_file(path: Path, visit) -> None:
	"""Call visit(kind, value, stack, line) for block opens, `x = yes` calls, flag checks, and variable checks."""
	stack: List[str] = []
	for number, raw in enumerate(read_text(path).splitlines(), 1):
		for match in REQUIREMENT_TOKEN.finditer(raw.split("#", 1)[0]):
			if match.group(0) == "}":
				if stack:
					stack.pop()
			elif match.group(2) == "{":
				stack.append(match.group(1))
				visit("open", match.group(1), stack, number)
			elif match.group(1):
				visit("call", match.group(1), stack, number)
			elif match.group(3) or match.group(4):
				visit("flag", match.group(3) or match.group(4), stack, number)
			else:
				name = match.group(5) or match.group(6)
				if name not in VARIABLE_KEYWORDS:
					visit("variable", name, stack, number)


def audit_requirement_flags(known: Set[str], findings: Findings) -> None:
	"""Find flags and variables that displayed requirements would print as raw names."""
	triggers: Dict[str, Tuple[List[Tuple[str, str, str]], Set[str]]] = {}
	for path in sorted((REPO_ROOT / "common" / "scripted_triggers").rglob("*.txt")):
		relative = path.relative_to(REPO_ROOT).as_posix()
		current: List[Optional[str]] = [None]

		def visit_trigger(kind, value, stack, number, relative=relative, current=current):
			if kind == "open" and len(stack) == 1:
				current[0] = value
				triggers[value] = ([], set())
			elif current[0] and stack and not UNDISPLAYED_BLOCKS.intersection(stack):
				if kind == "call":
					triggers[current[0]][1].add(value)
				elif kind in ("flag", "variable"):
					triggers[current[0]][0].append((kind, value, f"{relative}:{number}"))

		scan_requirement_file(path, visit_trigger)
	exposed: Dict[Tuple[str, str], str] = {}
	called: Set[str] = set()
	direct: Set[str] = set()
	for folder in ("decisions", "national_focus"):
		for path in sorted((REPO_ROOT / "common" / folder).rglob("*.txt")):
			relative = path.relative_to(REPO_ROOT).as_posix()

			def visit_consumer(kind, value, stack, number, relative=relative):
				if not REQUIREMENT_BLOCKS.intersection(stack) or UNDISPLAYED_BLOCKS.intersection(stack):
					return
				if kind in ("flag", "variable"):
					exposed.setdefault((kind, value), f"{relative}:{number}")
				elif kind == "call" and value in triggers:
					direct.add(value)
					if value not in known:
						called.add(value)

			scan_requirement_file(path, visit_consumer)
	# A scripted trigger called directly from a displayed block is shown as its own
	# localisation key when one exists, and as the expansion of its body otherwise.
	findings.expanded_triggers = sorted(name for name in direct if name not in known)
	pending = list(called)
	while pending:
		name = pending.pop()
		checks, calls = triggers[name]
		for kind, value, site in checks:
			exposed.setdefault((kind, value), site)
		for callee in calls:
			if callee in triggers and callee not in called and callee not in known:
				called.add(callee)
				pending.append(callee)

	def is_known(kind: str, name: str) -> bool:
		if name in known:
			return True
		# A scope prefix is not part of the name the tooltip prints.
		return kind == "variable" and name.split(".", 1)[-1] in known

	findings.exposed_flags = sorted(
		(name, site) for (kind, name), site in exposed.items()
		if kind == "flag" and not is_known(kind, name) and "@" not in name
	)
	findings.exposed_variables = sorted(
		(name, site) for (kind, name), site in exposed.items()
		if kind == "variable" and not is_known(kind, name)
		and not any(mark in name for mark in "@^[") and not name.startswith("constant:")
	)


# ---------------------------------------------------------------------------
# Implicit engine keys
# ---------------------------------------------------------------------------
#
# Most localisation the engine reads is never written as `name = KEY` in script.
# A decision shows the key spelled like its own id, a focus reads `<id>` and
# `<id>_desc`, a country tag reads `TAG`, `TAG_ADJ` and `TAG_DEF`, an achievement
# reads `<id>_NAME` and `<id>_DESC`. This section lists every key of that kind
# plus every key script names directly (`custom_effect_tooltip`, the `tooltip`
# of a `custom_trigger_tooltip`, `custom_cost_text`, GUI `text` and tooltip
# fields, scripted-localisation targets, event option names) and reports the
# ones defined by neither this mod nor vanilla English localisation.
#
# Each expectation carries a level:
#
# - `required`: the engine shows the raw key when it is absent.
# - `advisory`: vanilla routinely ships the definition without the key (idea,
#   decision and technology descriptions, short names, advisor tokens), so an
#   absent key renders as empty text and is listed separately.
#
# A key that script assembles at runtime (`$VAR$` macros, `[bracket]` commands,
# `@ROOT` suffixes) is resolved conservatively. It is reported as dynamic, and it
# is only called unmatched when its literal prefix matches no known key at all.
#
# `--calibrate` runs the same extractors against the installed vanilla game and
# prints per-category coverage, which is the positive control for each rule:
# a `required` category should be close to fully defined in vanilla.

REQUIRED = "required"
ADVISORY = "advisory"
VANILLA_ROOT = game_dir()

KEY_SHAPE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-']*$")
DYNAMIC_MARK = re.compile(r"[\[\]@$^%{}]")
NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")
NON_KEY_WORDS = {"yes", "no", "always", "none", "any", "all", "root", "this", "prev", "from"}
LOC_KEY_LINE = re.compile(r"^\s*([^\s:#]+):\d*\s*\"")


def parse_script(path: Path) -> list:
	"""Parse a Clausewitz file into `(key, operator, value, line)` nodes (`lib/clausewitz.py`)."""
	return list(parse(read_text(path)))


def unquote(raw: str) -> Tuple[str, bool]:
	if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
		return raw[1:-1], True
	return raw, False


def first_value(block: list, key: str) -> Optional[str]:
	for entry_key, _, value, _ in block:
		if entry_key == key and isinstance(value, str):
			return unquote(value)[0]
	return None


def child_blocks(block: list) -> Iterable[Tuple[str, list, int]]:
	"""Yield `(key, block, line)` for every keyed child that is itself a block."""
	for key, _, value, line in block:
		if key is not None and isinstance(value, list):
			yield key, value, line


class KeySink:
	"""Collects expected keys and the places that expect them."""

	def __init__(self) -> None:
		self.expected: List[Tuple[str, str, str, str, int, str, Tuple[str, ...], bool]] = []
		self.dynamic: List[Tuple[str, str, str, int]] = []
		self.cosmetic_used: Set[str] = set()

	def add_key(
		self, category: str, level: str, key: str, rel: str, line: int,
		note: str = "", alternative: Tuple[str, ...] = (), any_of: bool = False,
	) -> None:
		"""Record a key; `alternative` keys replace it, all of them or (`any_of`) any one."""
		self.expected.append((category, level, key, rel, line, note, alternative, any_of))

	def add(
		self, category: str, level: str, raw: str, rel: str, line: int,
		quoted_is_key: bool = False, note: str = "",
	) -> None:
		"""Record a script value that names a key.

		A bare identifier is a key. A quoted value is a literal string unless the
		caller knows that field takes quoted keys, and a quoted value with spaces
		is always literal text.
		"""
		text, quoted = unquote(raw)
		text = text.strip()
		if not text or (quoted and not quoted_is_key):
			return
		if text.lower() in NON_KEY_WORDS or NUMBER.match(text):
			return
		if " " in text:
			return
		if DYNAMIC_MARK.search(text):
			self.dynamic.append((category, text, rel, line))
			return
		if not KEY_SHAPE.match(text):
			return
		self.expected.append((category, level, text, rel, line, note, (), False))

	def add_id(
		self, category: str, key: str, rel: str, line: int,
		required: Tuple[str, ...] = ("",), advisory: Tuple[str, ...] = ("_desc",), note: str = "",
	) -> None:
		"""Record an id the engine expands with suffixes (`<id>`, `<id>_desc`)."""
		for suffix in required:
			self.add(category, REQUIRED, key + suffix, rel, line, note=note)
		for suffix in advisory:
			self.add(category, ADVISORY, key + suffix, rel, line, note=note)


def definition_files(root: Path, relative: str, skip: Tuple[str, ...] = ()) -> Iterable[Tuple[Path, str]]:
	base = root / relative
	if base.is_file():
		yield base, base.relative_to(root).as_posix()
		return
	if not base.is_dir():
		return
	for path in sorted(base.rglob("*.txt")):
		parts = path.relative_to(base).parts
		if any(part in skip for part in parts):
			continue
		yield path, path.relative_to(root).as_posix()


def descend(nodes: list, path: Tuple[str, ...]) -> Iterable[list]:
	"""Yield each block reached by following `path`; `*` matches every block child."""
	if not path:
		yield nodes
		return
	head, rest = path[0], path[1:]
	for key, value, _ in child_blocks(nodes):
		if head == "*" or key == head:
			yield from descend(value, rest)


# --- extractors -------------------------------------------------------------


def is_always_no(block: list, field: str) -> bool:
	"""True when `field = { always = no }` is declared, as hidden missions and categories do."""
	for key, scope, _ in child_blocks(block):
		if key == field:
			return any(entry[0] == "always" and entry[2] == "no" for entry in scope)
	return False


def extract_decisions(root: Path, sink: KeySink) -> None:
	"""Decision and mission ids, with their `_desc` and custom cost text.

	A decision that is never visible (`visible = { always = no }`, as hidden
	clock missions are) shows no text, so its keys are advisory. A `name =` or
	`desc =` at decision level is not in the wiki or the installed documentation,
	so the engine may ignore it. Both the id key and the override key are
	required, which keeps the title correct either way.
	"""
	for path, rel in definition_files(root, "common/decisions", skip=("categories",)):
		for _category_key, category_block, _ in child_blocks(parse_script(path)):
			for decision_id, decision, line in child_blocks(category_block):
				if is_always_no(decision, "visible"):
					sink.add_id("decision", decision_id, rel, line, required=(), advisory=("", "_desc"))
				else:
					sink.add_id("decision", decision_id, rel, line)
					for field, suffix in (("name", ""), ("desc", "_desc")):
						override = first_value(decision, field)
						if override and override != decision_id + suffix:
							sink.add("decision_override", REQUIRED, override, rel, line, quoted_is_key=True)
				for key, _, value, entry_line in decision:
					if key == "custom_cost_text" and isinstance(value, str):
						sink.add("decision_cost_text", REQUIRED, value, rel, entry_line, quoted_is_key=True)


def extract_decision_categories(root: Path, sink: KeySink) -> None:
	for path, rel in definition_files(root, "common/decisions/categories"):
		for category_id, category, line in child_blocks(parse_script(path)):
			if is_always_no(category, "visible"):
				sink.add_id("decision_category", category_id, rel, line, required=(), advisory=("", "_desc"))
			else:
				sink.add_id("decision_category", category_id, rel, line)


ADVISOR_IDEA_CATEGORIES = {
	"political_advisor", "army_chief", "navy_chief", "air_chief", "high_command", "theorist", "hidden_ideas",
}


def extract_ideas(root: Path, sink: KeySink) -> None:
	"""National spirits, laws, and manufacturers.

	Advisor slots show the character name, and an idea with `visible = { always = no }`
	never appears in a list, so both are advisory.
	"""
	for path, rel in definition_files(root, "common/ideas"):
		for container, categories, _ in child_blocks(parse_script(path)):
			if container != "ideas":
				continue
			for category, ideas, _ in child_blocks(categories):
				for idea_id, idea, line in child_blocks(ideas):
					name = first_value(idea, "name") or idea_id
					advisor = category in ADVISOR_IDEA_CATEGORIES or first_value(idea, "character") is not None
					advisor = advisor or is_always_no(idea, "visible")
					if advisor:
						sink.add_id("idea_advisor", name, rel, line, required=(), advisory=("", "_desc"))
					else:
						sink.add_id("idea", name, rel, line)


def extract_focuses(root: Path, sink: KeySink) -> None:
	"""Focus titles and descriptions. Vanilla defines both for every focus.

	A focus that sets `text = KEY` takes its title from `KEY` and its description
	from `KEY_desc`, which vanilla uses to avoid hash collisions between ids.
	"""
	def add_focus(focus: list, rel: str, line: int) -> None:
		focus_id = first_value(focus, "id")
		if focus_id:
			base = first_value(focus, "text") or focus_id
			sink.add_id("focus", base, rel, line, required=("", "_desc"), advisory=())

	for path, rel in definition_files(root, "common/national_focus"):
		for key, block, line in child_blocks(parse_script(path)):
			if key == "focus_tree":
				for child_key, child, child_line in child_blocks(block):
					if child_key in ("focus", "shared_focus", "joint_focus"):
						add_focus(child, rel, child_line)
			elif key in ("shared_focus", "joint_focus"):
				add_focus(block, rel, line)


def extract_container_ids(
	root: Path, sink: KeySink, category: str, relative: str, container: Optional[str],
	required: Tuple[str, ...] = ("",), advisory: Tuple[str, ...] = ("_desc",), skip: Tuple[str, ...] = (),
) -> None:
	"""Take the id of every block directly inside `container` (or at file level)."""
	path_selector = (container,) if container else ()
	for path, rel in definition_files(root, relative, skip=skip):
		for scope in descend(parse_script(path), path_selector):
			for block_id, _, line in child_blocks(scope):
				if block_id == "limit":
					continue
				sink.add_id(category, block_id, rel, line, required=required, advisory=advisory)


def extract_simple_ids(root: Path, sink: KeySink) -> None:
	extract_container_ids(root, sink, "opinion_modifier", "common/opinion_modifiers", "opinion_modifiers", advisory=())
	extract_container_ids(root, sink, "unit_leader_trait", "common/unit_leader", "leader_traits")
	extract_container_ids(root, sink, "country_leader_trait", "common/country_leader", "leader_traits")
	extract_container_ids(root, sink, "scientist_trait", "common/scientist_traits", None, skip=("_documentation.md",))
	extract_container_ids(root, sink, "equipment", "common/units/equipment", "equipments", advisory=("_short", "_desc"))
	extract_container_ids(root, sink, "equipment_module", "common/units/equipment/modules", "equipment_modules")
	extract_container_ids(root, sink, "sub_unit", "common/units", "sub_units")
	extract_container_ids(root, sink, "wargoal", "common/wargoals", "wargoal_types", advisory=("_desc",))
	extract_container_ids(root, sink, "occupation_law", "common/occupation_laws", None)
	extract_container_ids(root, sink, "special_project", "common/special_projects/projects", None, advisory=("_desc",))


def extract_dynamic_modifiers(root: Path, sink: KeySink) -> None:
	"""Dynamic modifier names. One that can never be enabled (`enable = { always = no }`) is advisory."""
	for path, rel in definition_files(root, "common/dynamic_modifiers"):
		for modifier_id, modifier, line in child_blocks(parse_script(path)):
			if is_always_no(modifier, "enable"):
				sink.add_id("dynamic_modifier", modifier_id, rel, line, required=(), advisory=("",))
			else:
				sink.add_id("dynamic_modifier", modifier_id, rel, line, advisory=())


def extract_modifier_definitions(root: Path, sink: KeySink) -> None:
	"""Custom `modifier_definition` ids. The wiki key is the id; vanilla also ships an upper-case `MODIFIER_` key."""
	for path, rel in definition_files(root, "common/modifier_definitions"):
		for modifier_id, _, line in child_blocks(parse_script(path)):
			sink.add_key("modifier_definition", REQUIRED, modifier_id, rel, line)
			sink.add_key("modifier_definition", ADVISORY, "MODIFIER_" + modifier_id.upper(), rel, line)


def extract_technologies(root: Path, sink: KeySink) -> None:
	"""Technology names. A tech that unlocks equipment or a sub-unit borrows that name."""
	for path, rel in definition_files(root, "common/technologies"):
		nodes = parse_script(path)
		for container, techs, _ in child_blocks(nodes):
			if container != "technologies":
				continue
			for tech_id, tech, line in child_blocks(techs):
				borrows = any(key in ("enable_equipments", "enable_subunits") for key, _, _, _ in tech)
				if borrows:
					sink.add_id("technology_unlock", tech_id, rel, line, required=(), advisory=("", "_desc"))
				else:
					sink.add_id("technology", tech_id, rel, line)
				for key, folder, folder_line in child_blocks(tech):
					if key == "folder":
						folder_name = first_value(folder, "name")
						if folder_name:
							sink.add_id("technology_folder", folder_name, rel, folder_line)
	for path, rel in definition_files(root, "common/technology_tags"):
		for container, block, _ in child_blocks(parse_script(path)):
			if container == "technology_folders":
				for folder_id, _, line in child_blocks(block):
					sink.add_id("technology_folder", folder_id, rel, line)


def extract_doctrines(root: Path, sink: KeySink) -> None:
	"""Grand doctrines and sub-doctrines, plus the `<subdoctrine>_<reward>` keys."""
	for path, rel in definition_files(root, "common/doctrines/grand_doctrines"):
		for doctrine_id, doctrine, line in child_blocks(parse_script(path)):
			sink.add(
				"doctrine", REQUIRED, first_value(doctrine, "name") or doctrine_id, rel, line,
				quoted_is_key=True,
			)
	for path, rel in definition_files(root, "common/doctrines/subdoctrines"):
		for subdoctrine_id, subdoctrine, line in child_blocks(parse_script(path)):
			sink.add(
				"subdoctrine", REQUIRED, first_value(subdoctrine, "name") or subdoctrine_id, rel, line,
				quoted_is_key=True,
			)
			for key, rewards, _ in child_blocks(subdoctrine):
				if key != "rewards":
					continue
				for reward_id, _, reward_line in child_blocks(rewards):
					sink.add_id(
						"doctrine_reward", f"{subdoctrine_id}_{reward_id}", rel, reward_line,
						required=("",), advisory=(),
					)


def extract_achievements(root: Path, sink: KeySink) -> None:
	"""Achievements read `<id>_NAME` and `<id>_DESC`."""
	paths = list(definition_files(root, "common/achievements")) + list(definition_files(root, "common/achievements.txt"))
	for path, rel in paths:
		for achievement_id, _, line in child_blocks(parse_script(path)):
			sink.add_id("achievement", achievement_id, rel, line, required=("_NAME", "_DESC"), advisory=())


def extract_characters(root: Path, sink: KeySink) -> None:
	"""Character `name` keys, leader descriptions, and advisor tokens."""
	for path, rel in definition_files(root, "common/characters"):
		for container, characters, _ in child_blocks(parse_script(path)):
			if container != "characters":
				continue
			for _, character, line in child_blocks(characters):
				for key, value, entry_line in ((k, v, l) for k, _, v, l in character):
					if key == "name" and isinstance(value, str):
						sink.add("character_name", REQUIRED, value, rel, entry_line)
				for key, role, _ in child_blocks(character):
					if key == "country_leader":
						for entry_key, _, value, entry_line in role:
							if entry_key == "desc" and isinstance(value, str):
								sink.add("leader_desc", REQUIRED, value, rel, entry_line, quoted_is_key=True)
					elif key == "advisor":
						token = first_value(role, "idea_token")
						if token:
							sink.add_id("advisor_token", token, rel, line, required=(), advisory=("", "_desc"))


COUNTRY_IDEOLOGIES = ("fascism", "democratic", "communism", "neutrality")
COSMETIC_USE = re.compile(r"set_cosmetic_tag\s*=\s*([A-Za-z0-9_]+)")


def extract_country_names(root: Path, sink: KeySink) -> None:
	"""`TAG`, `TAG_ADJ`, `TAG_DEF` for tags, and a name for each cosmetic tag.

	The engine reads `TAG_<ideology>` first, so a tag whose four ideology keys are
	all defined needs no plain key. A cosmetic tag is usually written for one
	ideology only (vanilla ships `GER_greater_german_reich_fascism` alone), so one
	ideology key is enough there, and a cosmetic tag that no script ever applies is
	advisory. A missing cosmetic `_ADJ` or `_DEF` is advisory because vanilla ships
	hundreds without it.
	"""
	registered: Set[str] = set()
	tag_line = re.compile(r'^\s*([A-Za-z0-9]{3})\s*=\s*"([^"]*)"')

	for path, rel in definition_files(root, "common/country_tags"):
		for number, text in enumerate(read_text(path).splitlines(), 1):
			match = tag_line.match(text.split("#", 1)[0])
			if not match:
				continue
			tag = match.group(1)
			registered.add(tag)
			for suffix in ("", "_ADJ", "_DEF"):
				alternative = tuple(f"{tag}_{ideology}{suffix}" for ideology in COUNTRY_IDEOLOGIES)
				sink.add_key("country_tag", REQUIRED, tag + suffix, rel, number, alternative=alternative)
	for path, rel in definition_files(root, "common/countries"):
		if path.name == "colors.txt":
			continue
		for name, block, line in child_blocks(parse_script(path)):
			if name in ("color", "color_ui") or re.match(r"^[A-Z0-9]{3}$", name) or name in registered:
				continue
			if not any(key == "color" for key, _, _, _ in block):
				continue
			level = REQUIRED if name in sink.cosmetic_used else ADVISORY
			for suffix, suffix_level in (("", level), ("_ADJ", ADVISORY), ("_DEF", ADVISORY)):
				alternative = tuple(f"{name}_{ideology}{suffix}" for ideology in COUNTRY_IDEOLOGIES)
				sink.add_key("cosmetic_tag", suffix_level, name + suffix, rel, line, alternative=alternative, any_of=True)


def extract_events(root: Path, sink: KeySink) -> None:
	"""Event titles, descriptions, and option names of every visible event."""
	for path, rel in definition_files(root, "events"):
		for key, event, line in child_blocks(parse_script(path)):
			if not key.endswith("_event"):
				continue
			event_id = first_value(event, "id")
			if not event_id or first_value(event, "hidden") == "yes":
				continue
			for field, default_suffix in (("title", ".t"), ("desc", ".d")):
				entries = [entry for entry in event if entry[0] == field]
				if not entries:
					sink.add_key("event_" + field, REQUIRED, event_id + default_suffix, rel, line)
				for _, _, value, entry_line in entries:
					if isinstance(value, str):
						sink.add("event_" + field, REQUIRED, value, rel, entry_line, quoted_is_key=True)
					else:
						for text_key, _, text_value, text_line in value:
							if text_key == "text" and isinstance(text_value, str):
								sink.add("event_" + field, REQUIRED, text_value, rel, text_line, quoted_is_key=True)
			for option_key, option, _option_line in child_blocks(event):
				if option_key != "option":
					continue
				for entry_key, _, value, entry_line in option:
					if entry_key == "name" and isinstance(value, str):
						sink.add("event_option", REQUIRED, value, rel, entry_line, quoted_is_key=True)


GUI_TEXT_FIELDS = {"text", "buttonText", "pdx_tooltip", "pdx_tooltip_delayed", "tooltip", "tooltipText"}
GUI_KEY_SHAPE = re.compile(r"^[A-Za-z0-9]+[_.][A-Za-z0-9_.\-]*$")
GUI_NUMERIC_SHAPE = re.compile(r"^[\d.,]+[A-Za-z%]?$")


def extract_gui_text(root: Path, sink: KeySink) -> None:
	"""Keys named by `text`, `buttonText`, and tooltip fields in `.gui` files.

	An unlocalised GUI string renders as the string itself, so only values shaped
	like a key (letters joined by an underscore or dot) count as references. A
	string that the identically named vanilla `.gui` file also contains is
	vanilla's own text, so it is not reported.
	"""
	base = root / "interface"
	if not base.is_dir():
		return

	def walk(nodes: list, rel: str, inherited: Set[str]) -> None:
		for key, _, value, line in nodes:
			if isinstance(value, list):
				walk(value, rel, inherited)
			elif key in GUI_TEXT_FIELDS:
				text, quoted = unquote(value)
				if text in inherited:
					continue
				if quoted and not GUI_NUMERIC_SHAPE.match(text) and (GUI_KEY_SHAPE.match(text) or DYNAMIC_MARK.search(text)):
					if text.startswith("[") or "$" in text:
						sink.dynamic.append(("gui_text", text, rel, line))
					else:
						sink.add("gui_text", REQUIRED, value, rel, line, quoted_is_key=True)

	for path in sorted(base.rglob("*.gui")):
		twin = VANILLA_ROOT / "interface" / path.name
		inherited: Set[str] = set()
		if root != VANILLA_ROOT and twin.is_file():
			inherited = set(re.findall(r'"([^"\n]*)"', read_text(twin)))
		walk(parse_script(path), path.relative_to(root).as_posix(), inherited)


def extract_game_rules(root: Path, sink: KeySink) -> None:
	"""Game rule titles, groups, and option labels. These fields hold quoted keys."""
	for path, rel in definition_files(root, "common/game_rules"):
		for _rule_id, rule, _line in child_blocks(parse_script(path)):
			for key, _, value, entry_line in rule:
				if key in ("name", "group", "desc") and isinstance(value, str):
					sink.add("game_rule", REQUIRED, value, rel, entry_line, quoted_is_key=True)
			for option_key, option, _ in child_blocks(rule):
				if option_key in ("default", "option"):
					for key, _, value, entry_line in option:
						if key in ("text", "desc") and isinstance(value, str):
							sink.add("game_rule", REQUIRED, value, rel, entry_line, quoted_is_key=True)


TOOLTIP_FIELD = re.compile(
	r'(?<![A-Za-z0-9_])(custom_effect_tooltip|custom_modifier_tooltip|custom_cost_text|tooltip|localization_key|localisation_key)'
	r'\s*=\s*("[^"\n]*"|[^\s{}=#"]+)'
)
PLAIN_WORD = re.compile(r"^[A-Z][a-z]+$")
TOOLTIP_CATEGORY = {
	"custom_effect_tooltip": "custom_effect_tooltip",
	"custom_modifier_tooltip": "custom_modifier_tooltip",
	"custom_cost_text": "custom_cost_text",
	"tooltip": "trigger_tooltip",
	"localization_key": "tooltip_localization_key",
	"localisation_key": "tooltip_localization_key",
}


def extract_tooltip_fields(root: Path, sink: KeySink) -> None:
	"""Keys that effects and triggers name directly, anywhere under events, common, and history.

	This is a text scan rather than a tree parse because scripted effects and
	triggers hold most of these references and are large. The `(?<![A-Za-z0-9_])`
	guard keeps `custom_trigger_tooltip = {` from matching its inner `tooltip`.
	"""
	for relative in ("events", "common", "history"):
		base = root / relative
		if not base.is_dir():
			continue
		for path in sorted(base.rglob("*.txt")):
			text = strip_comments(read_text(path))
			rel = path.relative_to(root).as_posix()
			in_scripted_localisation = "scripted_localisation" in rel
			last_offset = 0
			line = 1
			for match in TOOLTIP_FIELD.finditer(text):
				line += text.count("\n", last_offset, match.start())
				last_offset = match.start()
				field = match.group(1)
				category = TOOLTIP_CATEGORY[field]
				level = REQUIRED
				if field in ("localization_key", "localisation_key") and in_scripted_localisation:
					category = "scripted_loc_target"
					value = unquote(match.group(2))[0]
					if value.startswith(("GFX_", "[")):
						continue
					# Scripted localisation prints an undefined target verbatim, so a
					# plain capitalised word is usually literal text rather than a key.
					if PLAIN_WORD.match(value):
						level = ADVISORY
				sink.add(category, level, match.group(2), rel, line, quoted_is_key=True)
			for match in COSMETIC_USE.finditer(text):
				sink.cosmetic_used.add(match.group(1))


GETTER_COMMAND = re.compile(r"\[([^\[\]]+)\]")
SCRIPTED_LOC_NAME = re.compile(r"^\s*name\s*=\s*([A-Za-z0-9_]+)", re.M)


def getter_universe() -> Set[str]:
	"""Every `Get...` command that is defined or already used by vanilla.

	Engine commands such as `GetName` are not declared anywhere on disk, so vanilla
	usage in localisation and interface files stands in for the built-in list.
	"""
	names: Set[str] = set()
	scripted_dirs = [REPO_ROOT / "common" / "scripted_localisation", VANILLA_ROOT / "common" / "scripted_localisation"]
	for directory in scripted_dirs:
		if directory.is_dir():
			for path in directory.glob("*.txt"):
				names.update(SCRIPTED_LOC_NAME.findall(read_text(path)))
	documentation = VANILLA_ROOT / "documentation"
	if documentation.is_dir():
		for path in documentation.glob("*.md"):
			names.update(re.findall(r"\bGet[A-Za-z0-9_]+", read_text(path)))
	vanilla_sources = list(VANILLA_LOCALISATION_DIR.rglob("*.yml")) if VANILLA_LOCALISATION_DIR.is_dir() else []
	vanilla_sources += list((VANILLA_ROOT / "interface").rglob("*.gui")) if (VANILLA_ROOT / "interface").is_dir() else []
	for path in vanilla_sources:
		for command in GETTER_COMMAND.findall(read_text(path)):
			for part in command.split("|")[0].split("."):
				if part.startswith("Get"):
					names.add(part)
	return names


def check_getters(sink: KeySink, text: str, category: str, rel: str, line: int, universe: Set[str]) -> None:
	for command in GETTER_COMMAND.findall(text):
		if command.startswith(("?", "$")):
			continue
		for part in command.split("|")[0].split("."):
			if part.startswith("Get") and part not in universe:
				sink.add_key(category, REQUIRED, part, rel, line, note="scripted localisation getter")


def extract_loc_getters(root: Path, sink: KeySink) -> None:
	"""`[GetName]`-style commands in this mod's localisation that nothing defines."""
	if root != REPO_ROOT:
		return
	universe = getter_universe()
	for path in sorted(LOCALISATION_DIR.rglob("*.yml")):
		rel = path.relative_to(REPO_ROOT).as_posix()
		for number, text in enumerate(read_text(path).splitlines(), 1):
			if "[" in text and not text.lstrip().startswith("#"):
				check_getters(sink, text, "loc_getter", rel, number, universe)
	for path in sorted((REPO_ROOT / "interface").rglob("*.gui")):
		rel = path.relative_to(REPO_ROOT).as_posix()
		for number, text in enumerate(read_text(path).splitlines(), 1):
			if "[" in text:
				check_getters(sink, text, "gui_getter", rel, number, universe)


EXTRACTORS = (
	extract_tooltip_fields,
	extract_decisions,
	extract_decision_categories,
	extract_ideas,
	extract_focuses,
	extract_simple_ids,
	extract_dynamic_modifiers,
	extract_modifier_definitions,
	extract_technologies,
	extract_doctrines,
	extract_achievements,
	extract_characters,
	extract_country_names,
	extract_events,
	extract_gui_text,
	extract_game_rules,
	extract_loc_getters,
)


# --- resolution -------------------------------------------------------------


def load_known_localisation(definitions: Dict[str, List[Tuple[str, int]]]) -> Tuple[Set[str], Set[str]]:
	"""Return `(mod_and_replace_keys, vanilla_keys)`; a key in either is defined."""
	mod_keys: Set[str] = set(definitions)
	replace_dir = LOCALISATION_DIR / "replace"
	if replace_dir.is_dir():
		for path in replace_dir.rglob("*.yml"):
			for line in read_text(path).splitlines():
				match = LOC_KEY_LINE.match(line)
				if match:
					mod_keys.add(match.group(1))
	vanilla_keys: Set[str] = set()
	if VANILLA_LOCALISATION_DIR.is_dir():
		for path in VANILLA_LOCALISATION_DIR.rglob("*.yml"):
			for line in read_text(path).splitlines():
				match = LOC_KEY_LINE.match(line)
				if match:
					vanilla_keys.add(match.group(1))
	return mod_keys, vanilla_keys


def dynamic_pattern(text: str) -> Tuple[str, "re.Pattern[str]"]:
	"""Turn a runtime-assembled key into its literal prefix and a full-match regex."""
	marker = re.compile(r"\$[^$]*\$|\[[^\]]*\]|@[A-Za-z_]+|\^[^^]*\^|%[A-Za-z]+")
	pieces = marker.split(text)
	prefix = pieces[0]
	body = ".+".join(re.escape(piece) for piece in pieces)
	return prefix, re.compile(body)


def resolve_dynamic(sink: KeySink, known: Set[str]) -> List[Tuple[str, str, str, int, str]]:
	"""Match each dynamic key against known keys by prefix, then by full pattern.

	Returns `(category, text, file, line, status)` where status is `matched`,
	`no literal prefix`, or `no matching key`. Only the last is a likely defect.
	"""
	ordered = sorted(known)

	cache: Dict[str, str] = {}
	results: List[Tuple[str, str, str, int, str]] = []
	for category, text, rel, line in sink.dynamic:
		status = cache.get(text)
		if status is None:
			prefix, pattern = dynamic_pattern(text)
			if not prefix:
				status = "no literal prefix"
			else:
				start = bisect.bisect_left(ordered, prefix)
				status = "no matching key"
				for index in range(start, len(ordered)):
					candidate = ordered[index]
					if not candidate.startswith(prefix):
						break
					if pattern.fullmatch(candidate):
						status = "matched"
						break
			cache[text] = status
		results.append((category, text, rel, line, status))
	return results


def summarise_expected(
	sink: KeySink, known: Set[str],
) -> Tuple[Dict[Tuple[str, str], Dict[str, Tuple[str, int, int]]], Dict[Tuple[str, str], int]]:
	"""Group expectations by `(category, level)` and keep the unique missing keys.

	`missing[(category, level)][key] = (first file, first line, reference count)`.
	`totals[(category, level)]` is the number of unique keys expected.
	"""
	missing: Dict[Tuple[str, str], Dict[str, Tuple[str, int, int]]] = defaultdict(dict)
	seen: Dict[Tuple[str, str], Set[str]] = defaultdict(set)
	for category, level, key, rel, line, _, alternative, any_of in sink.expected:
		bucket = (category, level)
		seen[bucket].add(key)
		if key in known:
			continue
		if alternative and (any if any_of else all)(item in known for item in alternative):
			continue
		sites = missing[bucket]
		if key in sites:
			first_file, first_line, count = sites[key]
			sites[key] = (first_file, first_line, count + 1)
		else:
			sites[key] = (rel, line, 1)
	return missing, {bucket: len(keys) for bucket, keys in seen.items()}


def calibrate_against_vanilla() -> int:
	"""Run every extractor on the installed game and print per-category coverage."""
	if not VANILLA_ROOT.is_dir():
		print("vanilla game directory not found", file=sys.stderr)
		return 1
	_, vanilla_keys = load_known_localisation({})
	sink = KeySink()
	for extractor in EXTRACTORS:
		print(f"  {extractor.__name__} ...", file=sys.stderr)
		extractor(VANILLA_ROOT, sink)
	missing, totals = summarise_expected(sink, vanilla_keys)
	print("Vanilla coverage of each implicit rule (a required rule should be near 100%)")
	print(f"{'category':26} {'level':9} {'expected':>9} {'missing':>8} {'coverage':>9}")
	for bucket in sorted(totals):
		total = totals[bucket]
		gap = len(missing.get(bucket, {}))
		print(f"{bucket[0]:26} {bucket[1]:9} {total:9d} {gap:8d} {100.0 * (total - gap) / total:8.1f}%")
	for bucket in sorted(missing):
		if bucket[1] == REQUIRED:
			sample = ", ".join(sorted(missing[bucket])[:4])
			print(f"  {bucket[0]} missing e.g. {sample}")
	return 0


def emit_report(findings: Findings, show_advisory: bool = False) -> None:
	print("=" * 78)
	print("Static localisation audit")
	print("=" * 78)
	print(f"files parsed            : {findings.file_count}")
	print(f"key definitions         : {findings.key_count}")
	print(f"duplicate keys          : {len(findings.duplicates)}")
	print(f"parse errors            : {len(findings.parse_errors)}")
	print(f"missing BOM             : {len(findings.missing_bom)}")
	print(f"missing l_english header: {len(findings.no_header)}")
	print(f"encoding artifacts      : {len(findings.encoding_artifacts)}")
	print(f"undefined event roots   : {len(findings.missing_event_roots)}")
	print(f"undefined key bindings  : {len(findings.missing_prefixed)}")
	print(f"literal (non-key) names : {len(findings.literal_names)}")
	print(f"missing event t/d keys  : {len(findings.missing_event_content)}")
	print(f"dead keys               : {len(findings.dead_keys)}")
	print(f"unlocalised req. flags  : {len(findings.exposed_flags)}")
	print(f"unlocalised req. vars   : {len(findings.exposed_variables)}")
	required_missing = sum(
		len(keys) for bucket, keys in findings.implicit_missing.items() if bucket[1] == REQUIRED
	)
	advisory_missing = sum(
		len(keys) for bucket, keys in findings.implicit_missing.items() if bucket[1] == ADVISORY
	)
	unmatched_dynamic = [row for row in findings.implicit_dynamic if row[4] == "no matching key"]
	print(f"implicit keys missing   : {required_missing}")
	print(f"implicit advisory absent: {advisory_missing}")
	print(f"dynamic keys, no match  : {len(unmatched_dynamic)}")
	print(f"triggers shown expanded : {len(findings.expanded_triggers)}")

	def section(title: str, rows: List[str], limit: int = 40) -> None:
		print()
		print(f"--- {title} ({len(rows)}) ---")
		for row in rows[:limit]:
			print(f"  {row}")
		if len(rows) > limit:
			print(f"  ... {len(rows) - limit} more")

	section("parse errors", findings.parse_errors)
	section("missing BOM", findings.missing_bom)
	section("missing l_english header", findings.no_header)
	section("encoding artifacts", [f"{f}:{n}: {m}" for f, n, m in findings.encoding_artifacts])
	section(
		"duplicate keys",
		[f"{k}  {f1}:{n1}  then  {f2}:{n2}" for k, f1, n1, f2, n2 in findings.duplicates],
	)
	section("undefined event roots", [f"{k}  ({', '.join(src)})" for k, src in findings.missing_event_roots])
	section(
		"undefined key bindings",
		[f"{k}  ({', '.join(src)})" for k, src in findings.missing_prefixed],
	)
	section(
		"missing event title/description keys",
		[f"{k}  ({role})  {', '.join(src)}" for k, role, src in findings.missing_event_content],
		limit=60,
	)
	section(
		"literal (non-key) names",
		[f"{k}  ({', '.join(src)})" for k, src in findings.literal_names],
		limit=20,
	)
	section("dead keys", [f"{k}  ({src})" for k, src in findings.dead_keys], limit=80)
	section(
		"unlocalised flags in displayed requirements",
		[f"{flag}  ({site})" for flag, site in findings.exposed_flags],
		limit=40,
	)
	section(
		"unlocalised variables in displayed requirements",
		[f"{name}  ({site})" for name, site in findings.exposed_variables],
		limit=40,
	)

	print()
	print("--- implicit engine keys by rule ---")
	print(f"{'category':26} {'level':9} {'expected':>9} {'missing':>8}")
	for bucket in sorted(findings.implicit_totals):
		if bucket[1] == ADVISORY and not show_advisory and bucket not in findings.implicit_missing:
			continue
		gap = len(findings.implicit_missing.get(bucket, {}))
		print(f"{bucket[0]:26} {bucket[1]:9} {findings.implicit_totals[bucket]:9d} {gap:8d}")
	required_rows = [
		f"{bucket[0]:22} {key}  ({site[0]}:{site[1]}, {site[2]} refs)"
		for bucket, keys in sorted(findings.implicit_missing.items())
		if bucket[1] == REQUIRED
		for key, site in sorted(keys.items())
	]
	section("missing implicit engine keys", required_rows, limit=400)
	if show_advisory:
		advisory_rows = [
			f"{bucket[0]:22} {key}  ({site[0]}:{site[1]})"
			for bucket, keys in sorted(findings.implicit_missing.items())
			if bucket[1] == ADVISORY
			for key, site in sorted(keys.items())
		]
		section("absent advisory keys (empty text, not raw keys)", advisory_rows, limit=400)
	section(
		"dynamic keys with no matching defined key",
		[f"{category:22} {text}  ({rel}:{line})" for category, text, rel, line, _ in unmatched_dynamic],
		limit=60,
	)
	section(
		"scripted triggers called directly in displayed requirements with no key (shown expanded)",
		findings.expanded_triggers,
		limit=20,
	)


def write_json(findings: Findings, destination: Path) -> None:
	payload = {
		"key_count": findings.key_count,
		"file_count": findings.file_count,
		"parse_errors": findings.parse_errors,
		"missing_bom": findings.missing_bom,
		"no_header": findings.no_header,
		"encoding_artifacts": [
			{"file": f, "line": n, "detail": m} for f, n, m in findings.encoding_artifacts
		],
		"duplicates": [
			{"key": k, "file": f1, "line": n1, "other_file": f2, "other_line": n2}
			for k, f1, n1, f2, n2 in findings.duplicates
		],
		"missing_event_roots": [
			{"key": k, "sources": s} for k, s in findings.missing_event_roots
		],
		"missing_prefixed": [{"key": k, "sources": s} for k, s in findings.missing_prefixed],
		"literal_names": [{"value": k, "sources": s} for k, s in findings.literal_names],
		"missing_event_content": [
			{"key": k, "role": r, "sources": s} for k, r, s in findings.missing_event_content
		],
		"dead_keys": [{"key": k, "file": f} for k, f in findings.dead_keys],
		"exposed_flags": [{"flag": k, "site": s} for k, s in findings.exposed_flags],
		"exposed_variables": [{"variable": k, "site": s} for k, s in findings.exposed_variables],
		"expanded_triggers": findings.expanded_triggers,
		"implicit_totals": {
			f"{category}:{level}": total for (category, level), total in sorted(findings.implicit_totals.items())
		},
		"implicit_missing": [
			{"category": category, "level": level, "key": key, "file": site[0], "line": site[1], "refs": site[2]}
			for (category, level), keys in sorted(findings.implicit_missing.items())
			for key, site in sorted(keys.items())
		],
		"implicit_dynamic": [
			{"category": category, "key": text, "file": rel, "line": line, "status": status}
			for category, text, rel, line, status in findings.implicit_dynamic
			if status != "matched"
		],
	}
	destination.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
	print(f"\nwrote {destination}")


CHECK = "localisation"
LEVELS = {
	"LOC-PARSE": "error",
	"LOC-BOM": "error",
	"LOC-HEADER": "error",
	"LOC-ENCODING": "error",
	"LOC-DUPLICATE": "error",
	"LOC-EVENT-ROOT": "error",
	"LOC-KEY-BINDING": "error",
	"LOC-EVENT-CONTENT": "error",
	"LOC-REQUIREMENT-FLAG": "error",
	"LOC-REQUIREMENT-VARIABLE": "error",
	"LOC-IMPLICIT": "error",
	"LOC-DYNAMIC-UNMATCHED": "warning",
	"LOC-IMPLICIT-ADVISORY": "review",
	"LOC-DEAD-KEY": "review",
	"LOC-LITERAL-NAME": "review",
	"LOC-EXPANDED-TRIGGER": "review",
}


def normalised_findings(findings: Findings) -> List[Finding]:
	"""Map every finding category onto the shared `lib.report` contract."""
	rows: List[Finding] = []

	def add(rule: str, path: str, line: int, message: str) -> None:
		rows.append(Finding(CHECK, rule, LEVELS[rule], report_relative(path), line, message))

	for entry in findings.parse_errors:
		site, _, text = entry.partition(": ")
		path, line = split_site(site)
		add("LOC-PARSE", path, line, f"line is not `key: \"value\"`: {text}")
	for path in findings.missing_bom:
		add("LOC-BOM", path, 0, "localisation file has no UTF-8 BOM")
	for path in findings.no_header:
		add("LOC-HEADER", path, 0, "first content line is not `l_english:`")
	for path, line, detail in findings.encoding_artifacts:
		add("LOC-ENCODING", path, line, detail)
	for key, first_file, first_line, path, line in findings.duplicates:
		add("LOC-DUPLICATE", path, line, f"duplicate key {key}, first defined at {report_relative(first_file)}:{first_line}")
	for key, sources in findings.missing_event_roots:
		add("LOC-EVENT-ROOT", sources[0] if sources else "", 0, f"event-style key {key} is bound but never defined")
	for key, sources in findings.missing_prefixed:
		add("LOC-KEY-BINDING", sources[0] if sources else "", 0, f"key {key} is bound but never defined")
	for key, role, sources in findings.missing_event_content:
		add("LOC-EVENT-CONTENT", sources[0] if sources else "", 0, f"event {role} key {key} is not defined")
	for flag, site in findings.exposed_flags:
		path, line = split_site(site)
		add("LOC-REQUIREMENT-FLAG", path, line, f"flag {flag} in a displayed requirement has no localisation key")
	for name, site in findings.exposed_variables:
		path, line = split_site(site)
		add("LOC-REQUIREMENT-VARIABLE", path, line, f"variable {name} in a displayed requirement has no localisation key")
	for (category, level), keys in sorted(findings.implicit_missing.items()):
		rule = "LOC-IMPLICIT" if level == REQUIRED else "LOC-IMPLICIT-ADVISORY"
		for key, (path, line, _refs) in sorted(keys.items()):
			add(rule, path, line, f"{category} key {key} is defined by neither the mod nor vanilla")
	for category, text, path, line, status in findings.implicit_dynamic:
		if status == "no matching key":
			add("LOC-DYNAMIC-UNMATCHED", path, line, f"{category} key {text} matches no defined key by its literal prefix")
	for key, path in findings.dead_keys:
		add("LOC-DEAD-KEY", path, 0, f"key {key} is referenced nowhere")
	for value, sources in findings.literal_names:
		add("LOC-LITERAL-NAME", sources[0] if sources else "", 0, f"quoted literal {value} is not a localisation key")
	for name in findings.expanded_triggers:
		add("LOC-EXPANDED-TRIGGER", "", 0, f"scripted trigger {name} is shown expanded in a displayed requirement")
	return rows


AUDIT_FINDINGS = Findings()


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--json", type=Path, help="also write the findings as JSON")
	parser.add_argument(
		"--show-advisory",
		action="store_true",
		help="also list advisory keys that vanilla routinely omits (descriptions, short names)",
	)
	parser.add_argument(
		"--calibrate",
		action="store_true",
		help="run the implicit-key extractors on vanilla and print coverage per rule",
	)
	parser.add_argument("--root", type=Path, help="audit this mod folder instead of the repository that holds the tool")
	add_arguments(parser)
	arguments = parser.parse_args()
	if arguments.root:
		global REPO_ROOT, LOCALISATION_DIR
		REPO_ROOT = arguments.root.resolve()
		LOCALISATION_DIR = REPO_ROOT / "localisation" / "english"
	missing_game = require_game_dir()
	if missing_game is not None:
		return missing_game
	if arguments.calibrate:
		return calibrate_against_vanilla()

	findings = AUDIT_FINDINGS
	print("indexing script tokens ...", file=sys.stderr)
	tokens, bracket_refs, token_sources = collect_script_tokens()
	print(f"  {len(tokens)} distinct tokens", file=sys.stderr)

	print("parsing localisation ...", file=sys.stderr)
	definitions = parse_localisation(findings)
	print(f"  {len(definitions)} distinct keys", file=sys.stderr)

	dynamic_prefixes = collect_dynamic_scripted_localisation()
	print(f"  {len(dynamic_prefixes)} dynamic key prefixes", file=sys.stderr)

	scripted_tokens = collect_scripted_identifiers()
	print(f"  {len(scripted_tokens)} scripted identifiers", file=sys.stderr)

	quoted, bare = collect_quoted_keys()
	print(f"  {len(quoted)} quoted literals, {len(bare)} bare bindings", file=sys.stderr)

	mod_keys, vanilla_keys = load_known_localisation(definitions)
	known = mod_keys | vanilla_keys
	print(f"  {len(vanilla_keys)} vanilla keys, {len(mod_keys)} mod keys incl. replace", file=sys.stderr)

	classify(definitions, tokens, bracket_refs)
	collect_referenced_keys(
		tokens, definitions, known, quoted, bare, dynamic_prefixes, scripted_tokens
	)

	events = collect_event_roots()
	hidden = sum(1 for record in events.values() if record.hidden)
	print(
		f"  {len(events)} events ({hidden} hidden, {len(events) - hidden} visible)",
		file=sys.stderr,
	)
	audit_event_loc_keys(events, definitions)
	audit_requirement_flags(known, findings)

	sink = KeySink()
	for extractor in EXTRACTORS:
		print(f"  {extractor.__name__} ...", file=sys.stderr)
		extractor(REPO_ROOT, sink)
	findings.implicit_missing, findings.implicit_totals = summarise_expected(sink, known)
	findings.implicit_dynamic = resolve_dynamic(sink, known)

	paths = requested_paths(arguments)
	selected = select(normalised_findings(findings), paths)
	if paths:
		print_findings(CHECK, selected)
	else:
		emit_report(findings, arguments.show_advisory)
		print()
		print_findings(CHECK, selected, show_levels=("error",))
	if arguments.json:
		write_json(findings, arguments.json)
		merge_json(arguments.json, selected, LEVELS)
	return exit_code(selected, arguments.fail_on)


if __name__ == "__main__":
	raise SystemExit(main())
