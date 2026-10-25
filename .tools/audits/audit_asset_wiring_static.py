#!/usr/bin/env python3
"""Static audit of a mod's sprite, entity, and asset wiring.

Answers three source-only questions:

1. Which `GFX_` names are referenced by script or GUI but registered in no
   `.gfx` file here and in no vanilla `.gfx` file? Those render as a missing
   sprite or log an error at load.
2. Which `GFX_` names are registered in this mod's `.gfx` files but referenced
   nowhere? Those are dead sprite definitions.
3. Which sprite, entity, or texture definitions point at a file that does not
   exist on disk?
4. Which mod-referenced vanilla GFX definitions point at a file that does not
   exist in the installed vanilla tree? This catches broken DLC reach-through
   such as a declared portrait sprite whose backing DDS is absent.

Vanilla reach-through is expected in places, so question 1 consults the vanilla
install before reporting a name as unresolved.

5. Which sprites and files the engine looks up implicitly from script or
   localisation data are missing in both the mod and the vanilla install? The
   engine derives these names from ids and fields rather than from a quoted
   GFX_ token, so the literal scan cannot see them. Each rule below was checked
   against the installed vanilla tree with `--calibrate-vanilla` before it is
   reported as a missing lookup:

   - idea pictures: `picture = x` resolves to `GFX_idea_x`; a visible idea
     without `picture` resolves to `GFX_idea_<id>`; hidden idea categories are
     not checked for the default name because they never draw an icon;
   - decisions: `icon = x` resolves to `GFX_decision_x`;
   - decision categories: `picture = x` or `icon = x` resolves to
     `GFX_decision_category_x`;
   - focus shine: a focus icon also needs `<icon>_shine` for its shine pulse;
   - subunit icons: `sprite = x` in `sub_units` resolves to
     `GFX_unit_x_icon_medium`;
   - text icons: `£name` in localisation resolves to `GFX_name`;
   - flags: a `gfx/flags/<TAG>*.tga` file, plus a `medium/` and `small/` file,
     for every real tag in `common/country_tags`. Vanilla ships ideology-suffixed
     flags, so the check accepts `<TAG>.tga` or `<TAG>_<suffix>.tga`. Cosmetic-tag
     flags are counted as missing like any other flag, because the mod sets them
     through `set_cosmetic_tag` and each one needs its own flag file;
   - achievement art: `gfx/achievements/<id>.dds` plus `_grey` and
     `_not_eligible` for every achievement id;
   - character portrait textures: quoted `.dds` or `.tga` paths in `portraits`.

   Dynamic constructions (a name ending in `_`, a prefix built from a variable)
   and documentation placeholders (a name seen only in `.md` files) are listed
   separately and never counted as missing. Technology pictures, equipment and
   MIO sprites, and scientist-trait or special-project icons have no implicit
   rule confirmed against vanilla; those entries are explicit `icon =` tokens
   that question 1 already covers.

Usage:
	python .tools/audits/audit_asset_wiring_static.py
	python .tools/audits/audit_asset_wiring_static.py --json out.json
	python .tools/audits/audit_asset_wiring_static.py --calibrate-vanilla
	python .tools/audits/audit_asset_wiring_static.py --paths interface/x.gfx common/ideas/x.txt
	python .tools/audits/audit_asset_wiring_static.py --root path/to/mod   # audit another mod folder

Levels and exit status follow `.tools/lib/report.py`. Unresolved `GFX_` references, missing
files, missing vanilla backing files and missing implicit lookups are `error`; unverified
bare event pictures are `warning`; dead registrations, dynamic prefixes and
documentation-only names are `review`. The command exits 1 when an error is reported,
unless `--fail-on none` is given. With `--paths` the console lists only the findings located
in those files or folders; a missing vanilla backing file is located in the vanilla tree and
therefore appears only in a run without `--paths`. `--root` audits another mod folder; paths
in the report are then relative to that folder.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # .tools, for the shared lib package
from lib.game import game_dir, require_game_dir
from lib.clausewitz import pairs, parse
from lib.report import Finding, add_arguments, exit_code, merge_json, print_findings, relative, requested_paths, select

REPO_ROOT = Path(__file__).resolve().parents[2]
VANILLA_ROOT = game_dir()

EXCLUDED_TOP_LEVEL = {
	".git", ".tools", ".tmp", ".agents", ".claude", ".codex", ".cursor",
	".opencode", ".qoder", "docs", "history", "paradox_wiki",
}

NAME_DEF = re.compile(r'name\s*=\s*"?(GFX_[A-Za-z0-9_]+)"?')
GFX_REF = re.compile(r"\bGFX_[A-Za-z0-9_]+")
TEXTURE_REF = re.compile(r'(?:texturefile|texture_diffuse|texture|fontfile)\s*=\s*"([^"]+)"')

# Clausewitz resolves entity textures and meshes by filename, searching the
# model folders recursively, not by the literal quoted path. A reference is
# therefore present when a file of that name exists anywhere under the model
# trees. Resolving the quoted string as a literal path reported every entity
# texture as missing.
def asset_search_dirs() -> Tuple[Path, ...]:
	"""Return the mod and vanilla asset trees searched by filename."""
	return (
		REPO_ROOT / "gfx",
		REPO_ROOT / "sound",
		REPO_ROOT / "music",
		VANILLA_ROOT / "gfx",
		VANILLA_ROOT / "sound",
		VANILLA_ROOT / "music",
		# DLC packages keep their engine-facing textures below their own package
		# roots. Include those trees so a vanilla sprite declaration is not
		# incorrectly reported as broken merely because its texture is supplied by
		# an installed DLC rather than the base game root.
		VANILLA_ROOT / "dlc",
		VANILLA_ROOT / "integrated_dlc",
	)

_ASSET_INDEX: Dict[str, int] = {}


def build_asset_index() -> Dict[str, int]:
	"""Index every asset basename under the mod and vanilla asset trees."""
	if _ASSET_INDEX:
		return _ASSET_INDEX
	suffixes = {".dds", ".tga", ".png", ".bmp", ".jpg", ".mesh", ".anim", ".wav", ".ogg"}
	for root in asset_search_dirs():
		if not root.is_dir():
			continue
		for path in root.rglob("*"):
			if path.is_file() and path.suffix.lower() in suffixes:
				key = path.name.lower()
				_ASSET_INDEX[key] = _ASSET_INDEX.get(key, 0) + 1
	return _ASSET_INDEX


def resolve_asset(reference: str) -> bool:
	"""Return True when an asset reference resolves to a real file.

	A `.tga` reference also resolves to a same-stem `.dds`. Vanilla declares many
	sprites as `.tga` while shipping only the `.dds` (for example `checkbox_small`
	and `closebutton_small`), and the engine loads them, so the extension alone
	does not make a texture missing.
	"""
	if not reference:
		return True
	normalised = reference.replace("\\", "/")
	if _resolve_exact(normalised):
		return True
	if normalised.lower().endswith(".tga"):
		return _resolve_exact(normalised[:-4] + ".dds")
	return False


def _resolve_exact(normalised: str) -> bool:
	if "/" in normalised:
		for root in (REPO_ROOT, VANILLA_ROOT):
			if (root / normalised).is_file():
				return True
	basename = normalised.rsplit("/", 1)[-1].lower()
	return build_asset_index().get(basename, 0) > 0


FILE_REF = re.compile(r'"[^"]*?\.(?:dds|tga|png|bmp|jpg)"', re.IGNORECASE)


class Findings:
	def __init__(self) -> None:
		self.unresolved_refs: List[Dict[str, object]] = []
		self.dead_definitions: List[Dict[str, object]] = []
		self.missing_files: List[Dict[str, str]] = []
		self.missing_vanilla_files: List[Dict[str, str]] = []
		self.registered_count = 0
		self.vanilla_registered = 0
		self.implicit_missing: List[Dict[str, str]] = []
		self.implicit_checked: Counter = Counter()
		self.implicit_ok_names: Set[str] = set()
		self.implicit_unverified: List[Dict[str, str]] = []
		self.dynamic_refs: List[Dict[str, object]] = []
		self.documentation_refs: List[Dict[str, object]] = []


def read_text(path: Path) -> str:
	"""Read a source file, dropping whole-line comments so a commented-out sprite is neither a registration nor a use.

	Markdown keeps its headings, so only the Clausewitz-style sources are stripped.
	"""
	raw = path.read_bytes()
	if raw.startswith(b"\xef\xbb\xbf"):
		raw = raw[3:]
	text = raw.decode("utf-8", errors="replace")
	if path.suffix.lower() != ".md":
		text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
	return text


def iter_source_files(root: Path, excluded: Set[str], pattern: str) -> Iterable[Path]:
	"""Skip excluded top-level trees before descending into their contents."""
	for entry in root.iterdir():
		if entry.name in excluded:
			continue
		if entry.is_file():
			if entry.match(pattern):
				yield entry
		else:
			yield from entry.rglob(pattern)


def collect_registered(root: Path, excluded: Set[str]) -> Dict[str, List[str]]:
	"""Return GFX names registered by `.gfx` files under root."""
	registered: Dict[str, List[str]] = defaultdict(list)
	if not root.is_dir():
		return registered
	for path in iter_source_files(root, excluded, "*.gfx"):
		parts = path.relative_to(root).parts
		if parts and parts[0] in excluded:
			continue
		try:
			text = read_text(path)
		except OSError:
			continue
		rel = str(path)
		try:
			rel = str(path.relative_to(REPO_ROOT))
		except ValueError:
			pass
		for match in NAME_DEF.finditer(text):
			registered[match.group(1)].append(rel)
	return registered


def collect_references() -> Tuple[Dict[str, Set[str]], Set[str]]:
	"""Return GFX names referenced, and the names each `.gfx` file defines.

	A `.gfx` file mentions every sprite it defines via `name = "GFX_..."`, so a
	registration would otherwise count as its own reference and no registration
	could ever be dead. The defining files are returned so the caller can
	discount a name that appears only in its own definition.
	"""
	references: Dict[str, Set[str]] = defaultdict(set)
	defined_in: Dict[str, Set[str]] = defaultdict(set)
	for path in iter_source_files(REPO_ROOT, EXCLUDED_TOP_LEVEL, "*"):
		if not path.is_file():
			continue
		parts = path.relative_to(REPO_ROOT).parts
		if not parts or parts[0] in EXCLUDED_TOP_LEVEL:
			continue
		if path.suffix.lower() not in {".txt", ".gui", ".gfx", ".asset", ".yml", ".md"}:
			continue
		try:
			text = read_text(path)
		except OSError:
			continue
		rel = str(path.relative_to(REPO_ROOT))
		for match in GFX_REF.finditer(text):
			references[match.group(0)].add(rel)
		if path.suffix.lower() == ".gfx":
			for match in NAME_DEF.finditer(text):
				defined_in[match.group(1)].add(rel)
	return references, defined_in


def audit_definitions(findings: Findings) -> None:
	"""Check that every texture or sprite file reference exists on disk."""
	for path in iter_source_files(REPO_ROOT, EXCLUDED_TOP_LEVEL, "*.gfx"):
		parts = path.relative_to(REPO_ROOT).parts
		if parts and parts[0] in EXCLUDED_TOP_LEVEL:
			continue
		try:
			text = read_text(path)
		except OSError:
			continue
		rel = str(path.relative_to(REPO_ROOT))
		for match in TEXTURE_REF.finditer(text):
			target = match.group(1)
			if target.startswith(("gfx/", "GFX_")) and "/" not in target:
				continue
			if resolve_asset(target):
				continue
			findings.missing_files.append({"file": rel, "reference": target})


def audit_entities(findings: Findings) -> None:
	"""Check `.gfx` entity blocks for mesh and texture files that are absent."""
	for path in iter_source_files(REPO_ROOT, EXCLUDED_TOP_LEVEL, "*.gfx"):
		parts = path.relative_to(REPO_ROOT).parts
		if parts and parts[0] in EXCLUDED_TOP_LEVEL:
			continue
		try:
			text = read_text(path)
		except OSError:
			continue
		rel = str(path.relative_to(REPO_ROOT))
		for match in re.finditer(r'\bmeshfile\s*=\s*"([^"]+)"', text):
			target = match.group(1)
			if resolve_asset(target):
				continue
			findings.missing_files.append({"file": rel, "reference": target})


def audit_referenced_vanilla_definitions(
	findings: Findings, referenced_names: Set[str]
) -> None:
	"""Check backing files for vanilla GFX definitions used by the mod.

	The normal missing-file pass intentionally scans mod-owned `.gfx` files only.
	Vanilla reach-through is usually safe, but a declared vanilla sprite can still
	be unusable when its DLC declaration survives while the backing texture is
	absent from the installed tree. Restrict this pass to GFX names referenced by
	the mod so it does not turn the audit into a full vanilla-install linter.
	"""
	if not VANILLA_ROOT.is_dir() or not referenced_names:
		return
	for path in VANILLA_ROOT.rglob("*.gfx"):
		try:
			text = read_text(path)
		except OSError:
			continue
		matches = list(NAME_DEF.finditer(text))
		if not matches:
			continue
		for index, match in enumerate(matches):
			name = match.group(1)
			if name not in referenced_names:
				continue
			end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
			definition = text[match.end():end]
			for texture in TEXTURE_REF.finditer(definition):
				target = texture.group(1)
				if resolve_asset(target):
					continue
				findings.missing_vanilla_files.append(
					{
						"file": str(path.relative_to(VANILLA_ROOT)),
						"reference": target,
						"name": name,
					}
				)


# ---------------------------------------------------------------------------
# Implicit engine lookups (question 5). Each extractor reads the same source
# layout from a root, so `--calibrate-vanilla` can measure the rule against the
# installed vanilla tree before the mod's expectations are trusted.
# ---------------------------------------------------------------------------

UPPER_KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")
PORTRAIT_FILE = re.compile(r"\.(?:dds|tga)$", re.IGNORECASE)
BARE_EVENT_PICTURE = re.compile(r"\bpicture\s*=\s*([A-Za-z][A-Za-z0-9_]*)\b")
TEXT_ICON = re.compile(r"£([A-Za-z0-9_]+)")
IDEA_BODY_KEYS = {
	"picture", "modifier", "available", "allowed", "cost", "removal_cost",
	"ai_will_do", "on_add", "on_remove", "character", "ledger", "traits",
	"visible", "targeted_modifier", "equipment_bonus", "limit", "rule",
}
HIDDEN_IDEA_GROUPS = {"hidden_ideas"}

Expectation = Dict[str, object]


def parse_clausewitz(text: str) -> List[Tuple[Optional[str], object]]:
	"""Parse Clausewitz text into `(key, value)` pairs through the shared reader (`lib/clausewitz.py`)."""
	return list(pairs(parse(text)))


def _children(block: object) -> List[Tuple[Optional[str], object]]:
	return block if isinstance(block, list) else []


def _scalar(block: object, key: str) -> Optional[str]:
	for name, value in _children(block):
		if name == key and isinstance(value, str):
			return value
	return None


def _sub_blocks(block: object) -> List[Tuple[str, list]]:
	return [(name, value) for name, value in _children(block) if name is not None and isinstance(value, list)]


def _has_key(block: object, key: str) -> bool:
	return any(name == key for name, _ in _children(block))


def _find_blocks(block: object, key: str) -> List[list]:
	"""Return every sub-block stored under `key`, at any depth."""
	found: List[list] = []
	for name, value in _children(block):
		if name == key and isinstance(value, list):
			found.append(value)
		if isinstance(value, list):
			found.extend(_find_blocks(value, key))
	return found


def _rel(root: Path, path: Path) -> str:
	return str(path.relative_to(root)).replace("\\", "/")


def _files(root: Path, folder: str, pattern: str = "*.txt", skip_dirs: Tuple[str, ...] = ()) -> List[Path]:
	base = root / folder
	if not base.is_dir():
		return []
	result = []
	for path in sorted(base.rglob(pattern)):
		parts = path.relative_to(base).parts[:-1]
		if any(part in skip_dirs for part in parts):
			continue
		result.append(path)
	return result


def _parsed(path: Path) -> List[Tuple[Optional[str], object]]:
	try:
		return parse_clausewitz(read_text(path))
	except OSError:
		return []


def _looks_like_idea(block: object) -> bool:
	return any(name in IDEA_BODY_KEYS for name, _ in _children(block) if name is not None)


def _never_visible(block: object) -> bool:
	"""True for an idea that is never drawn: `visible = { always = no }`, or `allowed = { always = no }` (hidden carriers)."""
	for name, value in _children(block):
		if name in ("visible", "allowed") and isinstance(value, list) and _has_pair(value, "always", "no"):
			return True
	return False


def _has_pair(block: object, key: str, value_text: str) -> bool:
	return any(name == key and value == value_text for name, value in _children(block))


def _walk_ideas(block: object, group: Optional[str], depth: int, out: list) -> None:
	for key, sub in _sub_blocks(block):
		if _looks_like_idea(sub):
			out.append((key, sub, group))
		elif depth < 2:
			_walk_ideas(sub, key if group is None else group, depth + 1, out)


def _walk_with_icon(block: object, depth: int, out: list) -> None:
	for key, sub in _sub_blocks(block):
		if _scalar(sub, "icon") is not None:
			out.append((key, sub))
		elif depth < 2:
			_walk_with_icon(sub, depth + 1, out)


def expect_ideas(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for path in _files(root, "common/ideas"):
		for key, value in _parsed(path):
			if key != "ideas" or not isinstance(value, list):
				continue
			found: list = []
			_walk_ideas(value, None, 0, found)
			for idea_id, sub, group in found:
				picture = _scalar(sub, "picture")
				owner = f"{idea_id} ({group or 'ungrouped'})"
				if picture is not None:
					expected = picture if picture.startswith("GFX_") else f"GFX_idea_{picture}"
					rows.append(_row("idea_picture", "sprite", expected, path, root, owner))
				elif group not in HIDDEN_IDEA_GROUPS and not _never_visible(sub):
					rows.append(_row("idea_default", "sprite", f"GFX_idea_{idea_id}", path, root, owner))
	return rows


def expect_decisions(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for path in _files(root, "common/decisions", skip_dirs=("categories",)):
		found: list = []
		_walk_with_icon(_parsed(path), 0, found)
		for decision_id, sub in found:
			icon = _scalar(sub, "icon")
			expected = icon if icon.startswith("GFX_") else f"GFX_decision_{icon}"
			rows.append(_row("decision_icon", "sprite", expected, path, root, decision_id))
	return rows


def expect_decision_categories(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for path in _files(root, "common/decisions/categories"):
		for key, sub in _sub_blocks(_parsed_block(path)):
			picture = _scalar(sub, "picture") or _scalar(sub, "icon")
			if picture is not None:
				expected = picture if picture.startswith("GFX_") else f"GFX_decision_category_{picture}"
				rows.append(_row("category_picture", "sprite", expected, path, root, key))
	return rows


def _parsed_block(path: Path) -> list:
	return _parsed(path)


def expect_focus_shine(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for path in _files(root, "common/national_focus"):
		found: list = []
		_walk_focus(_parsed(path), 0, found)
		for focus_id, icon in found:
			if icon.startswith("GFX_"):
				rows.append(_row("focus_shine", "sprite", f"{icon}_shine", path, root, focus_id))
	return rows


def _walk_focus(block: object, depth: int, out: list) -> None:
	for _key, sub in _sub_blocks(block):
		focus_id = _scalar(sub, "id")
		icon = _scalar(sub, "icon")
		if focus_id is not None and icon is not None:
			out.append((focus_id, icon))
		elif depth < 3:
			_walk_focus(sub, depth + 1, out)


def expect_subunit_icons(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for path in _files(root, "common/units"):
		for key, value in _parsed(path):
			if key != "sub_units" or not isinstance(value, list):
				continue
			for unit_id, sub in _sub_blocks(value):
				sprite = _scalar(sub, "sprite")
				if sprite is not None:
					rows.append(_row("subunit_icon", "sprite", f"GFX_unit_{sprite}_icon_medium", path, root, unit_id))
	return rows


def expect_text_icons(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	seen: Set[str] = set()
	for path in _files(root, "localisation", "*.yml"):
		try:
			text = read_text(path)
		except OSError:
			continue
		for match in TEXT_ICON.finditer(text):
			name = match.group(1)
			if name in seen:
				continue
			seen.add(name)
			expected = name if name.startswith("GFX_") else f"GFX_{name}"
			rows.append(_row("texticon", "sprite", expected, path, root, f"£{name}"))
	return rows


def _history_tags(root: Path) -> Set[str]:
	"""Tags that own a history/countries file. Placeholder tags in country_tags have no flag."""
	tags: Set[str] = set()
	base = root / "history" / "countries"
	if not base.is_dir():
		return tags
	for path in base.glob("*.txt"):
		match = re.match(r"^([A-Z][A-Z0-9_]*)[ -]", path.name)
		if match:
			tags.add(match.group(1))
	return tags


def expect_flags(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	tags: Dict[str, Path] = {}
	real_tags = _history_tags(root)
	for path in _files(root, "common/country_tags"):
		for key, value in _parsed(path):
			if key and isinstance(value, str) and UPPER_KEY.match(key) and value.startswith("countries/"):
				if key in real_tags:
					tags.setdefault(key, path)
	# Vanilla ships ideology-suffixed flags (TAG_<ideology>.tga) for most real
	# tags and omits the bare TAG.tga, so a real tag resolves when any of its
	# base or ideology flag files exists in the same folder.
	for tag, path in sorted(tags.items()):
		rows.append(_row("flag_any", "prefix", f"gfx/flags/{tag}", path, root, tag))
		rows.append(_row("flag_medium", "prefix", f"gfx/flags/medium/{tag}", path, root, tag))
		rows.append(_row("flag_small", "prefix", f"gfx/flags/small/{tag}", path, root, tag))
	return rows


def expect_cosmetic_flags(root: Path) -> List[Expectation]:
	"""Cosmetic tag keys in common/countries/*cosmetic*; resolved like the base flags."""
	rows: List[Expectation] = []
	for path in _files(root, "common/countries"):
		if "cosmetic" not in path.name:
			continue
		for key, _sub in _sub_blocks(_parsed_block(path)):
			if UPPER_KEY.match(key):
				rows.append(_row("flag_cosmetic", "prefix", f"gfx/flags/{key}", path, root, key))
	return rows


def expect_achievements(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for path in _files(root, "common/achievements"):
		for key, sub in _sub_blocks(_parsed_block(path)):
			if not re.match(r"^[0-9A-Za-z_]+$", key) or not (_has_key(sub, "possible") or _has_key(sub, "happened")):
				continue
			rows.append(_row("achievement_base", "file", f"gfx/achievements/{key}.dds", path, root, key))
			rows.append(_row("achievement_grey", "file", f"gfx/achievements/{key}_grey.dds", path, root, key))
			rows.append(_row("achievement_not_eligible", "file", f"gfx/achievements/{key}_not_eligible.dds", path, root, key))
	return rows


def expect_portrait_textures(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for path in _files(root, "common/characters"):
		for portraits in _find_blocks(_parsed(path), "portraits"):
			for value in _quoted_values(portraits):
				if PORTRAIT_FILE.search(value):
					rows.append(_row("portrait_texture", "asset", value, path, root, value))
	return rows


def _quoted_values(block: object) -> List[str]:
	values: List[str] = []
	for _, value in _children(block):
		if isinstance(value, str):
			values.append(value)
		elif isinstance(value, list):
			values.extend(_quoted_values(value))
	return values


def expect_bare_event_pictures(root: Path) -> List[Dict[str, str]]:
	rows: List[Dict[str, str]] = []
	for path in _files(root, "events", skip_dirs=()):
		text = read_text(path)
		for match in BARE_EVENT_PICTURE.finditer(text):
			if not match.group(1).startswith("GFX_"):
				rows.append({"family": "event_bare_picture", "file": _rel(root, path), "name": match.group(1)})
	return rows


def _row(family: str, kind: str, expected: str, path: Path, root: Path, owner: str) -> Expectation:
	return {"family": family, "kind": kind, "expected": expected, "file": _rel(root, path), "owner": owner}


EXTRACTORS = (
	expect_ideas,
	expect_decisions,
	expect_decision_categories,
	expect_focus_shine,
	expect_subunit_icons,
	expect_text_icons,
	expect_flags,
	expect_cosmetic_flags,
	expect_achievements,
	expect_portrait_textures,
)


def collect_expectations(root: Path) -> List[Expectation]:
	rows: List[Expectation] = []
	for extractor in EXTRACTORS:
		rows.extend(extractor(root))
	return rows


def expectation_resolves(row: Expectation, sprites: Set[str], roots: Tuple[Path, ...]) -> bool:
	"""Return True when a sprite name or file expectation resolves."""
	expected = str(row["expected"])
	if row["kind"] == "sprite":
		return expected in sprites
	if row["kind"] == "asset":
		return resolve_asset(expected)
	if row["kind"] == "prefix":
		return any(flag_prefix_exists(root, expected) for root in roots)
	return any((root / expected).is_file() for root in roots)


def flag_prefix_exists(root: Path, prefix: str) -> bool:
	"""True when `<prefix>.tga` or `<prefix>_<suffix>.tga` exists under root."""
	folder, _, stem = prefix.rpartition("/")
	base = root / folder
	if not base.is_dir():
		return False
	for path in base.glob(f"{stem}*.tga"):
		if path.name == f"{stem}.tga" or path.name.startswith(f"{stem}_"):
			return True
	return False


def run_calibration() -> int:
	"""Measure every implicit rule against the installed vanilla tree only."""
	vanilla_sprites = set(collect_registered(VANILLA_ROOT, set()))
	rows = collect_expectations(VANILLA_ROOT)
	tally: Dict[str, Counter] = defaultdict(Counter)
	samples: Dict[str, List[str]] = defaultdict(list)
	for row in rows:
		ok = expectation_resolves(row, vanilla_sprites, (VANILLA_ROOT,))
		tally[str(row["family"])]["checked"] += 1
		if ok:
			tally[str(row["family"])]["resolved"] += 1
		elif len(samples[str(row["family"])]) < 6:
			samples[str(row["family"])].append(f"{row['expected']}  <- {row['file']} ({row['owner']})")
	print("Vanilla calibration of implicit rules (same extractors, vanilla root only)")
	for family in sorted(tally):
		counts = tally[family]
		print(f"{family:24s} checked {counts['checked']:6d}  resolved {counts['resolved']:6d}  unresolved {counts['checked'] - counts['resolved']:6d}")
		for sample in samples.get(family, []):
			print(f"    e.g. {sample}")
	return 0


def audit_implicit(findings: Findings, sprites: Set[str]) -> None:
	"""Check implicit engine lookups against the mod and vanilla registries."""
	roots = (REPO_ROOT, VANILLA_ROOT)
	for row in collect_expectations(REPO_ROOT):
		family = str(row["family"])
		findings.implicit_checked[family] += 1
		if expectation_resolves(row, sprites, roots):
			if row["kind"] == "sprite":
				findings.implicit_ok_names.add(str(row["expected"]))
			continue
		findings.implicit_missing.append({key: str(value) for key, value in row.items()})
	for row in expect_bare_event_pictures(REPO_ROOT):
		findings.implicit_unverified.append(row)


CHECK = "asset-wiring"
LEVELS = {
	"GFX-UNRESOLVED": "error",
	"GFX-MISSING-FILE": "error",
	"GFX-MISSING-VANILLA-FILE": "error",
	"GFX-IMPLICIT": "error",
	"GFX-EVENT-PICTURE-UNVERIFIED": "warning",
	"GFX-DEAD-REGISTRATION": "review",
	"GFX-DYNAMIC-PREFIX": "review",
	"GFX-DOCUMENTATION-NAME": "review",
}


def normalised_findings(findings: Findings) -> List[Finding]:
	"""Map every finding category onto the shared `lib.report` contract."""
	rows: List[Finding] = []

	def add(rule: str, path: object, message: str) -> None:
		rows.append(Finding(CHECK, rule, LEVELS[rule], relative(path), 0, message))

	for row in findings.unresolved_refs:
		for source in row["sources"]:
			add("GFX-UNRESOLVED", source, f"{row['name']} is registered in neither the mod nor vanilla")
	for row in findings.missing_files:
		add("GFX-MISSING-FILE", row["file"], f"{row['reference']} does not exist on disk")
	for row in findings.missing_vanilla_files:
		add("GFX-MISSING-VANILLA-FILE", "vanilla/" + relative(row["file"]), f"{row['name']} points at missing {row['reference']}")
	for row in findings.implicit_missing:
		add("GFX-IMPLICIT", row["file"], f"[{row['family']}] {row['expected']} for {row['owner']} is missing in the mod and vanilla")
	for row in findings.implicit_unverified:
		add("GFX-EVENT-PICTURE-UNVERIFIED", row["file"], f"bare event picture {row['name']} has no confirmed lookup rule")
	for row in findings.dead_definitions:
		add("GFX-DEAD-REGISTRATION", row["definitions"][0] if row["definitions"] else "", f"{row['name']} is referenced nowhere")
	for row in findings.dynamic_refs:
		add("GFX-DYNAMIC-PREFIX", row["sources"][0] if row["sources"] else "", f"{row['name']} is a runtime-built prefix")
	for row in findings.documentation_refs:
		add("GFX-DOCUMENTATION-NAME", row["sources"][0] if row["sources"] else "", f"{row['name']} appears only in documentation")
	return rows


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--json", type=Path, help="also write the findings as JSON")
	parser.add_argument(
		"--calibrate-vanilla",
		action="store_true",
		help="measure each implicit lookup rule against the vanilla install and exit",
	)
	parser.add_argument("--root", type=Path, help="audit this mod folder instead of the repository that holds the tool")
	add_arguments(parser)
	arguments = parser.parse_args()
	if arguments.root:
		global REPO_ROOT
		REPO_ROOT = arguments.root.resolve()
	missing_game = require_game_dir()
	if missing_game is not None:
		return missing_game
	if arguments.calibrate_vanilla:
		return run_calibration()

	findings = Findings()

	print("indexing mod gfx registrations ...", file=sys.stderr)
	mod_registered = collect_registered(REPO_ROOT, EXCLUDED_TOP_LEVEL)
	findings.registered_count = len(mod_registered)
	print(f"  {len(mod_registered)} GFX names registered here", file=sys.stderr)

	print("indexing vanilla gfx registrations ...", file=sys.stderr)
	vanilla_registered = collect_registered(VANILLA_ROOT, set())
	findings.vanilla_registered = len(vanilla_registered)
	print(f"  {len(vanilla_registered)} GFX names registered in vanilla", file=sys.stderr)

	print("indexing references ...", file=sys.stderr)
	references, defined_in = collect_references()
	print(f"  {len(references)} distinct GFX names referenced", file=sys.stderr)

	# Literal names that end in `_` are prefixes that a script builds at runtime
	# (for example `GFX_decision_<x>_`), so they are dynamic rather than missing.
	# A name seen only in Markdown is a documentation placeholder.
	for name, sources in sorted(references.items()):
		if name in mod_registered or name in vanilla_registered:
			continue
		row = {"name": name, "sources": sorted(sources)[:4], "count": len(sources)}
		if all(source.endswith(".md") for source in sources):
			findings.documentation_refs.append(row)
		elif name.endswith("_"):
			findings.dynamic_refs.append(row)
		else:
			findings.unresolved_refs.append(row)

	dynamic_prefixes = [row["name"] for row in findings.dynamic_refs]
	print("checking implicit engine lookups ...", file=sys.stderr)
	audit_implicit(findings, set(mod_registered) | set(vanilla_registered))
	print(f"  {sum(findings.implicit_checked.values())} implicit lookups checked", file=sys.stderr)

	suppressed_by_implicit = 0
	dynamic_dead: List[Dict[str, object]] = []
	for name, definitions in sorted(mod_registered.items()):
		# Discount the file that defines the sprite: its own `name = "GFX_..."`
		# line is not a use of the sprite.
		external = references.get(name, set()) - set(definitions)
		if external:
			continue
		if name in findings.implicit_ok_names:
			suppressed_by_implicit += 1
			continue
		row = {"name": name, "definitions": definitions[:3], "count": len(definitions)}
		if any(name.startswith(prefix) for prefix in dynamic_prefixes):
			dynamic_dead.append(row)
			continue
		findings.dead_definitions.append(row)

	print("indexing asset filenames ...", file=sys.stderr)
	index = build_asset_index()
	print(f"  {len(index)} distinct asset filenames", file=sys.stderr)

	audit_definitions(findings)
	audit_entities(findings)
	# A vanilla sprite that the mod re-registers is overridden by the mod's own
	# definition, so its broken vanilla texture no longer reaches the game.
	audit_referenced_vanilla_definitions(findings, set(references) - set(mod_registered))

	paths = requested_paths(arguments)
	selected = select(normalised_findings(findings), paths)
	if paths:
		print_findings(CHECK, selected)
		if arguments.json:
			merge_json(arguments.json, selected, LEVELS)
		return exit_code(selected, arguments.fail_on)

	print()
	print("=" * 78)
	print("Static asset wiring audit")
	print("=" * 78)
	print(f"GFX registered here      : {findings.registered_count}")
	print(f"GFX referenced           : {len(references)}")
	print(f"unresolved references    : {len(findings.unresolved_refs)}")
	print(f"dead registrations       : {len(findings.dead_definitions)}")
	print(f"missing files on disk    : {len(findings.missing_files)}")
	print(f"missing vanilla files    : {len(findings.missing_vanilla_files)}")
	print(f"implicit lookups missing : {len(findings.implicit_missing)}")
	print(f"dynamic name prefixes    : {len(findings.dynamic_refs)} (not counted)")
	print(f"documentation-only names : {len(findings.documentation_refs)} (not counted)")
	print(f"dead after implicit use  : suppressed {suppressed_by_implicit}, dynamic-prefix candidates {len(dynamic_dead)}")

	print()
	print("implicit lookups by family (checked / missing):")
	families = sorted(set(findings.implicit_checked) | {str(r["family"]) for r in findings.implicit_missing})
	missing_by_family = Counter(str(r["family"]) for r in findings.implicit_missing)
	for family in families:
		print(f"  {family:24s} {findings.implicit_checked[family]:6d} / {missing_by_family[family]:5d}")

	def section(title: str, rows: List[str], limit: int = 40) -> None:
		print()
		print(f"--- {title} ({len(rows)}) ---")
		for row in rows[:limit]:
			print(f"  {row}")
		if len(rows) > limit:
			print(f"  ... {len(rows) - limit} more")

	section(
		"implicit engine lookups missing in mod and vanilla",
		[f"[{r['family']}] {r['expected']}  <- {r['file']} ({r['owner']})" for r in findings.implicit_missing],
		limit=400,
	)
	section(
		"unverified bare event pictures (not counted)",
		[f"{r['name']}  <- {r['file']}" for r in findings.implicit_unverified],
		limit=20,
	)
	section(
		"dynamic name prefixes (not counted)",
		[f"{r['name']}  ({r['count']} sites)  {', '.join(r['sources'][:2])}" for r in findings.dynamic_refs],
	)
	section(
		"documentation-only names (not counted)",
		[f"{r['name']}  ({r['count']} sites)  {', '.join(r['sources'][:2])}" for r in findings.documentation_refs],
	)
	section(
		"unresolved GFX references",
		[f"{r['name']}  ({r['count']} sites)  {', '.join(r['sources'][:2])}" for r in findings.unresolved_refs],
	)
	section(
		"missing files on disk",
		[f"{m['reference']}  <- {m['file']}" for m in findings.missing_files],
	)
	section(
		"missing files in referenced vanilla GFX",
		[
			f"{m['reference']}  <- {m['file']} ({m['name']})"
			for m in findings.missing_vanilla_files
		],
	)
	section(
		"dead registrations",
		[f"{d['name']}  <- {', '.join(d['definitions'][:1])}" for d in findings.dead_definitions],
		limit=60,
	)

	if arguments.json:
		payload = {
			"registered_count": findings.registered_count,
			"vanilla_registered": findings.vanilla_registered,
			"referenced_count": len(references),
			"unresolved_refs": findings.unresolved_refs,
			"dead_definitions": findings.dead_definitions,
			"missing_files": findings.missing_files,
			"missing_vanilla_files": findings.missing_vanilla_files,
			"implicit_checked": dict(findings.implicit_checked),
			"implicit_missing": findings.implicit_missing,
			"implicit_unverified": findings.implicit_unverified,
			"dynamic_refs": findings.dynamic_refs,
			"documentation_refs": findings.documentation_refs,
			"dead_suppressed_by_implicit": suppressed_by_implicit,
		}
		arguments.json.write_text(
			json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
		)
		merge_json(arguments.json, selected, LEVELS)
		print(f"\nwrote {arguments.json}")
	print()
	print_findings(CHECK, selected, show_levels=("error",))
	return exit_code(selected, arguments.fail_on)


if __name__ == "__main__":
	raise SystemExit(main())
