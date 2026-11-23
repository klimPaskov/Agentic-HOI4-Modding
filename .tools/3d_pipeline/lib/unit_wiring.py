"""Write a finished 3D unit's registration into a mod, the same way every time.

`run_pilot.py` ends a job with `runtime/registration.md` (see `unit_registration.py`): the
`pdxmesh` block for a `.gfx` file, the `animation` blocks for the model's `.asset` file and the
entity for an entity `.asset` file. `wire_unit.py` uses this module to put those blocks into a
mod and to answer what the mod still lacks. Nothing here runs a subprocess or reads a clock.

Each block is written between two marker comments that carry the job's runtime stem:

    # wire_unit begin <stem> <kind>
    ...block...
    # wire_unit end <stem> <kind>

A rerun replaces only the lines between its own markers. Every other line of the file stays
byte for byte as it was, including its line endings and byte order mark.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:  # the pipeline's own `lib` package
    from lib.unit_registration import STATE_TO_ROLE
except ImportError:  # pragma: no cover - used when the module is imported on its own
    from unit_registration import STATE_TO_ROLE  # type: ignore[no-redef]

KIND_PDXMESH = "pdxmesh"
KIND_ANIMATIONS = "animations"
KIND_ENTITY = "entity"
MARKER_PREFIX = "# wire_unit"
SOURCE_SUFFIXES = (".gfx", ".asset")
SOUND_FILE_SUFFIXES = (".wav", ".ogg", ".mp3")


class WiringError(ValueError):
    """A problem that makes the wiring unsafe or impossible; the message says what and where."""


# ---------------------------------------------------------------- registration.md


@dataclass(frozen=True)
class Registration:
    entity_name: str
    stem: str
    gfx_block: str
    asset_sections: Tuple[Tuple[str, str], ...]  # (model asset path, block), in file order
    entity_block: str


def _first_fence(lines: Sequence[str]) -> Optional[str]:
    inside = False
    body: List[str] = []
    for line in lines:
        if line.strip().startswith("```"):
            if inside:
                return "\n".join(body).rstrip()
            inside = True
            continue
        if inside:
            body.append(line.rstrip("\r"))
    return None


def parse_registration(text: str) -> Registration:
    """Read the blocks out of `runtime/registration.md` by their headings."""

    lines = text.replace("\r\n", "\n").split("\n")
    title = next((line for line in lines if line.startswith("# Registration for ")), "")
    entity_name = title.removeprefix("# Registration for ").strip()
    if not entity_name:
        raise WiringError("registration.md has no '# Registration for <entity>' title")
    sections: List[Tuple[str, List[str]]] = []
    for line in lines:
        if line.startswith("## "):
            sections.append((line, []))
        elif sections:
            sections[-1][1].append(line)
    gfx_block: Optional[str] = None
    entity_block: Optional[str] = None
    assets: List[Tuple[str, str]] = []
    for heading, body in sections:
        block = _first_fence(body)
        if heading.startswith("## `.gfx`"):
            gfx_block = block
        elif heading.startswith("## Entities"):
            entity_block = block
        else:
            match = re.fullmatch(r"## `([^`]+\.asset)`", heading.strip())
            if match and block is not None:
                assets.append((match.group(1).replace("\\", "/"), block))
    if not gfx_block:
        raise WiringError("registration.md has no .gfx block (the '## `.gfx`' section)")
    if not assets:
        raise WiringError("registration.md has no model .asset block (a '## `<folder>/<stem>.asset`' section)")
    if not entity_block:
        raise WiringError("registration.md has no entity block (the '## Entities' section)")
    stem = entity_name.removesuffix("_entity")
    return Registration(entity_name, stem, gfx_block, tuple(assets), entity_block)


def _pairs(block: str, key: str) -> List[str]:
    return re.findall(rf'\b{key}\s*=\s*"([^"]+)"', block)


def registered_names(registration: Registration) -> List[str]:
    """Every definition name the registration adds: the pdxmesh, its animations and the entities."""

    names = _pairs(registration.gfx_block, "name")[:1]  # the pdxmesh's own name comes first
    for _path, block in registration.asset_sections:
        names += _pairs(block, "name")
    names += [name for name in _pairs(registration.entity_block, "name") if name.endswith("_entity")]
    return list(dict.fromkeys(names))


def mesh_texture_names(registration: Registration) -> List[str]:
    names: List[str] = []
    for key in ("texture_diffuse", "texture_normal", "texture_specular"):
        names += _pairs(registration.gfx_block, key)
    return list(dict.fromkeys(names))


def mesh_file(registration: Registration) -> str:
    files = _pairs(registration.gfx_block, "file")
    if not files:
        raise WiringError("the registration's pdxmesh block has no file = line")
    return files[0].replace("\\", "/")


def animation_files(registration: Registration) -> List[str]:
    names: List[str] = []
    for _path, block in registration.asset_sections:
        names += _pairs(block, "file")
    return list(dict.fromkeys(names))


# ---------------------------------------------------------------- text files with markers

_LINE_END = re.compile(r"(\r\n|\n|\r)")
Row = Tuple[str, str]  # (line content, its own terminator: "\r\n", "\n", "\r" or "" for an unterminated last line)


@dataclass
class TextFile:
    """A source file as rows of (content, terminator), so a rewrite keeps every untouched byte.

    Each row keeps the terminator it had (CRLF, LF or a lone CR). Lines this tool adds use `newline`, the
    file's dominant ending. The byte order mark is kept as it was.
    """

    bom: bool
    newline: str
    rows: List[Row]

    @classmethod
    def read(cls, path: Path) -> "TextFile":
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        decoded = raw[3:].decode("utf-8") if bom else raw.decode("utf-8")
        return cls(bom, dominant_newline(decoded), split_rows(decoded))

    @classmethod
    def new(cls, lines: Sequence[str]) -> "TextFile":
        return cls(False, "\n", [(line, "\n") for line in lines])

    def encode(self) -> bytes:
        body = "".join(content + end for content, end in self.rows).encode("utf-8")
        return (b"\xef\xbb\xbf" if self.bom else b"") + body

    @property
    def text(self) -> str:
        """The content with every line ending shown as LF, for searching."""

        return "\n".join(content for content, _end in self.rows)


def split_rows(decoded: str) -> List[Row]:
    parts = _LINE_END.split(decoded)
    rows: List[Row] = [(parts[index], parts[index + 1]) for index in range(0, len(parts) - 1, 2)]
    if parts[-1]:
        rows.append((parts[-1], ""))
    return rows


def dominant_newline(decoded: str) -> str:
    crlf = decoded.count("\r\n")
    lf = decoded.count("\n") - crlf
    return "\r\n" if crlf and crlf >= lf else "\n"


def begin_marker(stem: str, kind: str) -> str:
    return f"{MARKER_PREFIX} begin {stem} {kind}"


def end_marker(stem: str, kind: str) -> str:
    return f"{MARKER_PREFIX} end {stem} {kind}"


def marked(stem: str, kind: str, block: str) -> List[str]:
    return [begin_marker(stem, kind), *block.split("\n"), end_marker(stem, kind)]


def _marker_span(rows: Sequence[Row], stem: str, kind: str, where: str) -> Optional[Tuple[int, int]]:
    begins = [index for index, (line, _end) in enumerate(rows) if line.strip() == begin_marker(stem, kind)]
    ends = [index for index, (line, _end) in enumerate(rows) if line.strip() == end_marker(stem, kind)]
    if not begins and not ends:
        return None
    if len(begins) != 1 or len(ends) != 1 or ends[0] < begins[0]:
        raise WiringError(f"{where} has a broken '{begin_marker(stem, kind)}' pair; fix or remove it by hand")
    return begins[0], ends[0]


def has_markers(text: str, stem: str, kind: str) -> bool:
    lines = text.split("\n")
    return any(line.strip() == begin_marker(stem, kind) for line in lines)


def strip_blocks(text: str, stem: str) -> str:
    """The text without any block this tool wrote for `stem`."""

    kept: List[str] = []
    skipping = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith(f"{MARKER_PREFIX} begin {stem} "):
            skipping = True
        elif stripped.startswith(f"{MARKER_PREFIX} end {stem} "):
            skipping = False
        elif not skipping:
            kept.append(line)
    return "\n".join(kept)


def _closing_brace_row(rows: Sequence[Row], wrapper: str, where: str) -> int:
    """The row that holds the closing brace of the last top-level `<wrapper> = { ... }` block.

    Braces inside comments and quoted strings do not count.
    """

    opener = re.compile(rf"\b{wrapper}\s*=\s*\{{")
    depth = 0
    open_depth: Optional[int] = None
    found: Optional[int] = None
    in_string = False
    for index, (line, _end) in enumerate(rows):
        position = 0
        in_string = False
        while position < len(line):
            char = line[position]
            if in_string:
                in_string = char != '"'
            elif char == "#":
                break
            elif char == '"':
                in_string = True
            elif depth == 0 and open_depth is None and (match := opener.match(line, position)):
                open_depth = depth
                depth += 1
                position = match.end()
                continue
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if open_depth is not None and depth == open_depth:
                    found = index
                    open_depth = None
            position += 1
    if found is None:
        raise WiringError(f"{where} has no '{wrapper} = {{ ... }}' block to put the pdxmesh in")
    if rows[found][0].strip() != "}":
        raise WiringError(f"{where}: the closing brace of '{wrapper} = {{' must be alone on its line")
    return found


def _same_lines(rows: Sequence[Row], new_lines: Sequence[str]) -> bool:
    return [content for content, _end in rows] == list(new_lines)


def upsert_block(existing: Optional[TextFile], *, stem: str, kind: str, block: str, wrapper: str, where: str) -> TextFile:
    """Put the marked block into `existing` (or a new file) and return the new content.

    `wrapper` is "objectTypes" for a `.gfx` file, whose blocks live inside `objectTypes = { }`, and
    "" for an `.asset` file, whose blocks are top level. Rows outside the block keep their own bytes.
    """

    new_lines = marked(stem, kind, block)
    if existing is None:
        lines = ["objectTypes = {", "", *new_lines, "}"] if wrapper else new_lines
        return TextFile.new(lines)
    rows = list(existing.rows)
    newline = existing.newline
    span = _marker_span(rows, stem, kind, where)
    if span is not None:
        first, last = span
        if not _same_lines(rows[first : last + 1], new_lines):
            tail_end = rows[last][1]
            added: List[Row] = [(line, newline) for line in new_lines]
            added[-1] = (added[-1][0], tail_end)
            rows[first : last + 1] = added
        return TextFile(existing.bom, newline, rows)
    if wrapper:
        at = _closing_brace_row(rows, wrapper, where)
        rows[at:at] = [("", newline), *((line, newline) for line in new_lines)]
        return TextFile(existing.bom, newline, rows)
    if rows and not rows[-1][1]:
        rows[-1] = (rows[-1][0], newline)
    gap = [("", newline)] if any(content.strip() for content, _end in rows) else []
    rows += gap + [(line, newline) for line in new_lines]
    return TextFile(existing.bom, newline, rows)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


# ---------------------------------------------------------------- finding existing definitions


def source_files(mod_root: Path) -> List[Path]:
    """Every `.gfx` and `.asset` file below the mod's `gfx/` folder, in a stable order."""

    root = mod_root / "gfx"
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES)


def read_text_lenient(path: Path) -> str:
    return _LINE_END.sub("\n", path.read_bytes().decode("utf-8-sig", errors="replace"))


def marker_files(mod_root: Path, stem: str, kind: str, suffix: str) -> List[Path]:
    """Every `suffix` file below the mod's `gfx/` folder that holds this job's `kind` block."""

    return [path for path in source_files(mod_root) if path.suffix.lower() == suffix and has_markers(read_text_lenient(path), stem, kind)]


def find_marker_file(mod_root: Path, stem: str, kind: str, suffix: str) -> Optional[Path]:
    """The one file that already holds this job's `kind` block, if any."""

    found = marker_files(mod_root, stem, kind, suffix)
    if len(found) > 1:
        names = ", ".join(path.relative_to(mod_root).as_posix() for path in found)
        raise WiringError(f"the {kind} block of {stem} is marked in more than one file ({names}); remove all but one")
    return found[0] if found else None


def find_definitions(mod_root: Path, names: Iterable[str], stem: str) -> List[Tuple[str, str]]:
    """(file, name) for each name a mod file defines outside this job's own blocks."""

    wanted = list(names)
    hits: List[Tuple[str, str]] = []
    for path in source_files(mod_root):
        text = strip_blocks(read_text_lenient(path), stem)
        for name in wanted:
            if re.search(rf'(?m)^[^#\n]*\bname\s*=\s*"{re.escape(name)}"', text):
                hits.append((path.relative_to(mod_root).as_posix(), name))
    return hits


# ---------------------------------------------------------------- sound plan


@dataclass(frozen=True)
class SoundEvent:
    role: str
    soundeffect: str
    frame: int
    file: str = ""


def parse_sound_plan(value: object) -> List[SoundEvent]:
    """The job's `sound_plan`: a list of {role, soundeffect (or sound), frame, file (optional)}."""

    if value in (None, [], ()):
        return []
    if not isinstance(value, list):
        raise WiringError("sound_plan must be a list of {role, soundeffect, frame} entries")
    events: List[SoundEvent] = []
    for position, entry in enumerate(value, 1):
        if not isinstance(entry, dict):
            raise WiringError(f"sound_plan entry {position} is not a mapping")
        role = str(entry.get("role") or "").strip()
        effect = str(entry.get("soundeffect") or entry.get("sound") or "").strip()
        frame = entry.get("frame")
        if not role or not effect or isinstance(frame, bool) or not isinstance(frame, int) or frame < 0:
            raise WiringError(f"sound_plan entry {position} needs a role, a soundeffect and a whole frame number from 0")
        if effect.lower().endswith(SOUND_FILE_SUFFIXES):
            raise WiringError(
                f"sound_plan entry {position} names the sound file {effect}; an entity plays a soundeffect "
                "(defined in a sound .asset file). Name the soundeffect and put the file in 'file'"
            )
        events.append(SoundEvent(role, effect, frame, str(entry.get("file") or "")))
    return events


_STATE_START = re.compile(r'^(\t+)state\s*=\s*\{\s*name\s*=\s*"([^"]+)"')


def _entity_states(lines: Sequence[str]) -> List[Tuple[int, int, str]]:
    """(first line, last line, state name) for each `state = { name = "..."` block of an entity."""

    states: List[Tuple[int, int, str]] = []
    index = 0
    while index < len(lines):
        match = _STATE_START.match(lines[index])
        if not match:
            index += 1
            continue
        depth = lines[index].count("{") - lines[index].count("}")
        last = index
        while depth > 0 and last + 1 < len(lines):
            last += 1
            depth += lines[last].count("{") - lines[last].count("}")
        states.append((index, last, match.group(2)))
        index = last + 1
    return states


def _quoted(text: str) -> str:
    """`text` as the inside of a double-quoted script string."""

    return text.replace("\\", "\\\\").replace('"', '\\"')


def _event_targets(event: SoundEvent, names: Sequence[str]) -> List[str]:
    targets = [name for name in names if name == event.role] or [name for name in names if STATE_TO_ROLE.get(name) == event.role and name != "idle"]
    if not targets:
        raise WiringError(f"sound event for role {event.role}: the entity has no such state ({', '.join(dict.fromkeys(names))})")
    return targets


def _check_event_frame(event: SoundEvent, state_name: str, clip_samples: Optional[Dict[str, int]], stem: str) -> None:
    if clip_samples is None or not stem:
        return
    clip = f"{stem}_{STATE_TO_ROLE.get(state_name, state_name)}.anim"
    samples = clip_samples.get(clip)
    if samples is not None and event.frame >= samples:
        raise WiringError(f"sound event for {event.role} is at frame {event.frame}, but {clip} has {samples} frames")


def _event_inserts(states: Sequence[Tuple[int, int, str]], events: Sequence[SoundEvent], clip_samples: Optional[Dict[str, int]], stem: str) -> Dict[int, List[str]]:
    names = [name for _first, _last, name in states]
    inserts: Dict[int, List[str]] = {}
    for event in events:
        targets = _event_targets(event, names)
        for state_first, _state_last, name in states:
            if name not in targets:
                continue
            _check_event_frame(event, name, clip_samples, stem)
            inserts.setdefault(state_first, []).append(sound_event_line(event.soundeffect, event.frame))
    return inserts


CLIP_FPS = 30.0  # the kit's clips and vanilla's units


def sound_event_line(soundeffect: str, frame: int, fps: float = CLIP_FPS, indent: str = "\t\t") -> str:
    """An entity sound event at a clip frame. An event's `time` is seconds of the clip, frame / fps: vanilla's destroyed landmarks fire
    their first explosion within 0.2 s of the frame their clip hides the part (calibrate_effects.py, `time_unit`)."""

    return f'{indent}event = {{ time = {round(frame / fps, 3):g} sound = {{ soundeffect = "{_quoted(soundeffect)}" }} }}'


def _splice_state(lines: Sequence[str], position: int, last: int, added: Sequence[str]) -> List[str]:
    """The lines that replace the state starting at `position`: its own lines plus the new `event` lines."""

    if last != position:  # a state that already spans lines: add before its closing brace
        return [*lines[position:last], *added, lines[last]]
    head = lines[position].rstrip()  # one-line state: open it up
    if not head.endswith("}"):
        raise WiringError(f"cannot read the state on entity line {position + 1}")
    return [head[:-1].rstrip(), *added, "\t}"]


def apply_sound_events(entity_block: str, events: Sequence[SoundEvent], clip_samples: Optional[Dict[str, int]] = None, stem: str = "") -> str:
    """Add an `event` line to the states each sound event names. Raises WiringError for one that fits no state."""

    if not events:
        return entity_block
    lines = entity_block.split("\n")
    states = _entity_states(lines)
    inserts = _event_inserts(states, events, clip_samples, stem)
    by_first = {first: last for first, last, _name in states}
    out: List[str] = []
    position = 0
    while position < len(lines):
        added = inserts.get(position)
        if added is None:
            out.append(lines[position])
            position += 1
            continue
        out += _splice_state(lines, position, by_first[position], added)
        position = by_first[position] + 1
    return "\n".join(out)


# ---------------------------------------------------------------- particle events (a death that burns away, lib/tripo_burn.py)


def apply_particle_events(entity_block: str, state: str, events: Sequence[Dict[str, Any]]) -> str:
    """Add an `event = { time = <seconds> node = "<locator>" particle = "<name>" keep_particle = yes }` line to every state named `state`, as
    vanilla's GER rifle infantry's death fires `blood_particle` at its `head` locator. Raises WiringError when the entity has no such state."""

    if not events:
        return entity_block
    lines = entity_block.split("\n")
    states = _entity_states(lines)
    targets = [(first, last) for first, last, name in states if name == state]
    if not targets:
        raise WiringError(f"particle events for {state}: the entity has no such state ({', '.join(dict.fromkeys(n for _f, _l, n in states))})")
    added = []
    for event in events:
        node = f' node = "{_quoted(str(event["node"]))}"' if event.get("node") else ""
        added.append(f'\t\tevent = {{ time = {float(event.get("time", 0)):g}{node} particle = "{_quoted(str(event["particle"]))}" keep_particle = yes }}')
    out: List[str] = []
    position = 0
    by_first = dict(targets)
    while position < len(lines):
        if position in by_first:
            out += _splice_state(lines, position, by_first[position], added)
            position = by_first[position] + 1
            continue
        out.append(lines[position])
        position += 1
    return "\n".join(out)


_EVENT_NODE = re.compile(r'^\s*event\s*=\s*\{.*\bnode\s*=\s*"([^"]+)".*\bparticle\s*=')


def apply_effect_events(entity_block: str, events: Sequence[Dict[str, Any]], sounds: Sequence[Dict[str, Any]] = (), add_states: Sequence[str] = ()) -> str:
    """The effects layer's events (lib/unit_effects.py plan) written into the entity's states for their roles.

    An existing particle event at one of the plan's locators in a target state is replaced (the static route copies vanilla's entity,
    whose muzzle flash fires at time 0 while the kit's clip turns the turret before the shot). A role in `add_states` that the entity has
    no state for gets one that plays the role's clip (a vanilla light tank has no death state). `sounds` are `{role, soundeffect, frame}`.
    """

    lines = entity_block.split("\n")
    names = [name for _f, _l, name in _entity_states(lines)]
    for role in add_states:
        if role in names:
            continue
        closing = max(i for i, line in enumerate(lines) if line.strip() == "}") if any(l.strip() == "}" for l in lines) else len(lines)
        anchor = next((i for i in range(len(lines) - 1, -1, -1) if _STATE_START.match(lines[i])), None)
        insert_at = closing
        if anchor is not None:
            last = next(l for f, l, _n in _entity_states(lines) if f == anchor)
            insert_at = last + 1
        lines[insert_at:insert_at] = [f'\tstate = {{ name = "{role}"\t\t\tanimation = "{role}" animation_blend_time = 0.3 looping = no }}']
        names.append(role)
    states = _entity_states(lines)
    nodes = {str(e["node"]) for e in events if e.get("node")}
    inserts: Dict[int, List[str]] = {}
    for first, _last, name in states:
        role = name if name in {e["role"] for e in [*events, *sounds]} else STATE_TO_ROLE.get(name, name)
        if name == "idle" and role != "idle":
            continue
        added = [_effect_line(e) for e in events if e["role"] in (name, role)]
        added += [sound_event_line(s["soundeffect"], int(s["frame"])) for s in sounds if s["role"] in (name, role)]
        if added:
            inserts[first] = list(dict.fromkeys(added))
    out: List[str] = []
    position = 0
    by_first = {first: last for first, last, _n in states}
    while position < len(lines):
        if position not in inserts:
            out.append(lines[position])
            position += 1
            continue
        last = by_first[position]
        body = [lines[position]] + [line for line in lines[position + 1: last + 1] if not ((m := _EVENT_NODE.match(line)) and m.group(1) in nodes)]
        out += _splice_state(body, 0, len(body) - 1, inserts[position])
        position = last + 1
    return "\n".join(out)


def _effect_line(event: Dict[str, Any]) -> str:
    node = f' node = "{_quoted(str(event["node"]))}"' if event.get("node") else ""
    return f'\t\tevent = {{ time = {float(event.get("time", 0)):g}{node} particle = "{_quoted(str(event["particle"]))}" keep_particle = yes }}'


def finite_particle(text: str, name: str, duration: float) -> str:
    """A copy of a vanilla particle file (`particle = { name = "..." subsystem = {...} }`) under its own `name`, every endless subsystem
    (`duration=-1`) made to emit for `duration` seconds, so the burn's fire dies out with the unit instead of burning on."""

    out = re.sub(r'(\bparticle\s*=\s*\{\s*name\s*=\s*)"[^"]*"', lambda m: f'{m.group(1)}"{name}"', text, count=1)
    return re.sub(r"\bduration\s*=\s*-1(\.0+)?", f"duration={duration:.3f}", out)


def particle_gfx(entries: Sequence[Dict[str, Any]]) -> str:
    """A `.gfx` file that registers the burn's particles (`pdxparticle`, as vanilla's gfx/entities/particles.gfx)."""

    body = "".join(f'\tpdxparticle = {{\n\t\tname = "{_quoted(e["name"])}"\n\t\ttype = "{_quoted(e["type"])}"\n\t\tscale = {float(e.get("scale", 1)):g}\n\t}}\n' for e in entries)
    return "objectTypes = {\n" + body + "}\n"


# ---------------------------------------------------------------- sub-unit, localisation, counters


def sprite_token(registration: Registration) -> str:
    return registration.entity_name.removesuffix("_entity")


def find_subunits(mod_root: Path, sprite: str, audit: object) -> List[Tuple[str, str]]:
    """(sub-unit id, file) for each `common/units` sub-unit whose `sprite` is `sprite`. `audit` is the kit's audit module."""

    found: List[Tuple[str, str]] = []
    for path in audit._files(mod_root, "common/units"):  # type: ignore[attr-defined]
        for key, _operator, value, _line in audit._parse_source(path):  # type: ignore[attr-defined]
            if key != "sub_units" or not isinstance(value, list):
                continue
            for unit, _op, block, _l in value:
                token = audit._scalar_node(block, "sprite") if isinstance(block, list) else None  # type: ignore[attr-defined]
                if token is not None and token[0] == sprite:
                    found.append((unit, path.relative_to(mod_root).as_posix()))
    return sorted(found)


LOC_HEADER = re.compile(r"^\s*(l_[a-z_]+)\s*:", re.M)
LOC_KEY = re.compile(r"^\s*([A-Za-z0-9_.\-']+):\d*\s", re.M)


def localisation_keys(mod_root: Path) -> Dict[str, set]:
    """language -> the keys the mod's `localisation/` files define."""

    keys: Dict[str, set] = {}
    root = mod_root / "localisation"
    if not root.is_dir():
        return keys
    for path in sorted(root.rglob("*.yml")):
        text = read_text_lenient(path)
        header = LOC_HEADER.search(text)
        language = header.group(1) if header else "l_unknown"
        keys.setdefault(language, set()).update(LOC_KEY.findall(text))
    return keys


def missing_localisation(mod_root: Path, unit_ids: Sequence[str]) -> List[str]:
    """The `<id>` and `<id>_desc` keys the sub-units need and no localisation file defines.

    The keys must exist in `l_english` when the mod has any English file, otherwise in any language.
    """

    by_language = localisation_keys(mod_root)
    pool = by_language.get("l_english") if "l_english" in by_language else set().union(*by_language.values()) if by_language else set()
    missing: List[str] = []
    for unit in unit_ids:
        for key in (unit, f"{unit}_desc"):
            if key not in pool:
                missing.append(key)
    return missing


@dataclass
class CounterToken:
    token: str
    role: str  # what draws it
    status: str  # mod, mod texture missing, vanilla art, missing
    detail: str = ""


SPRITE_DEF = re.compile(r'name\s*=\s*"(GFX_[A-Za-z0-9_]+)"([^}]*)', re.S)
TEXTURE_FILE = re.compile(r'texture[fF]ile\s*=\s*"([^"]+)"')


def _sprites_in(paths: Iterable[Path]) -> Dict[str, str]:
    found: Dict[str, str] = {}
    for path in paths:
        for name, rest in SPRITE_DEF.findall(read_text_lenient(path)):
            texture = TEXTURE_FILE.search(rest)
            found.setdefault(name, texture.group(1) if texture else "")
    return found


def counter_tokens(mod_root: Path, game_dir: Optional[Path], sprite: str) -> List[CounterToken]:
    """The counter sprites a sub-unit with `sprite = <sprite>` draws, read from `interface/subuniticons.gfx`.

    Vanilla defines `GFX_unit_<sprite>_icon_medium` (large counter, `divisions_large` art) and
    `GFX_unit_<sprite>_icon_medium_white` (map counter, `divisions_small/onmap_` art) for almost every
    sprite. `_medium_black` exists for 12 of them and is not required.
    """

    interface = mod_root / "interface"
    mod_defs = _sprites_in(sorted(interface.glob("*.gfx"))) if interface.is_dir() else {}
    vanilla_file = (game_dir / "interface" / "subuniticons.gfx") if game_dir else None
    vanilla_defs = _sprites_in([vanilla_file]) if vanilla_file and vanilla_file.is_file() else {}
    rows: List[CounterToken] = []
    for suffix, role in (("_medium", "large counter"), ("_medium_white", "map counter")):
        token = f"GFX_unit_{sprite}_icon{suffix}"
        if token in mod_defs:
            texture = mod_defs[token]
            if texture and not (mod_root / texture).is_file():
                rows.append(CounterToken(token, role, "mod texture missing", texture))
            else:
                rows.append(CounterToken(token, role, "mod", texture))
        elif token in vanilla_defs:
            rows.append(CounterToken(token, role, "vanilla art", "defined by the game, not made for this unit"))
        else:
            rows.append(CounterToken(token, role, "missing", "add it to interface/subuniticons.gfx with its own art"))
    return rows


def soundeffect_defined(mod_root: Path, game_dir: Optional[Path], name: str) -> bool:
    pattern = re.compile(rf'(?m)^[^#\n]*\bname\s*=\s*"{re.escape(name)}"')
    for root in (mod_root, game_dir):
        if root is None or not (root / "sound").is_dir():
            continue
        for path in sorted((root / "sound").rglob("*.asset")):
            if pattern.search(read_text_lenient(path)):
                return True
    return False


# ---------------------------------------------------------------- the plan


@dataclass
class PlanItem:
    kind: str  # block or file
    path: str  # relative to the mod root, posix
    status: str  # create, update, unchanged
    detail: str = ""
    payload: Optional[bytes] = field(default=None, repr=False)
    source: Optional[Path] = field(default=None, repr=False)

    def as_dict(self) -> Dict[str, str]:
        return {"kind": self.kind, "path": self.path, "status": self.status, "detail": self.detail}


@dataclass
class Plan:
    items: List[PlanItem] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def default_prefix(mod_root: Path, stem: str) -> str:
    """The `<prefix>` of `gfx/entities/<prefix>_units.*`: the mod's one existing `*_units.gfx`, else the stem's first word."""

    entities = mod_root / "gfx" / "entities"
    existing = sorted(path.name[: -len("_units.gfx")] for path in entities.glob("*_units.gfx")) if entities.is_dir() else []
    return existing[0] if len(existing) == 1 else stem.split("_")[0]


def model_folder(registration: Registration) -> str:
    """The mod-relative folder the registration's mesh lives in ("" when the mesh path has no folder)."""

    mesh_rel = mesh_file(registration)
    return mesh_rel.rsplit("/", 1)[0] if "/" in mesh_rel else ""


def safe_destination(mod_root: Path, rel: str, what: str = "path") -> str:
    """`rel` with `/` separators, after checking that it stays inside the mod root.

    A backslash counts as a separator on every platform. The destination is resolved, so a symlink that
    leaves the mod fails the check too. Raises WiringError when the path is empty, absolute, names a drive
    or reaches outside the mod.
    """

    posix = rel.replace("\\", "/")
    if not posix.strip() or posix.startswith("/") or ":" in posix or ".." in posix.split("/"):
        raise WiringError(f"{what} {rel} must be a path inside the mod")
    root = mod_root.resolve()
    target = (root / posix).resolve()
    if target != root and root not in target.parents:
        raise WiringError(f"{what} {rel} leaves the mod folder")
    return posix


def _same_file(mod_root: Path, first: str, second: str) -> bool:
    return os.path.normcase(str((mod_root / first).resolve())) == os.path.normcase(str((mod_root / second).resolve()))


@dataclass(frozen=True)
class Target:
    """One marked block and the file it goes into."""

    rel: str
    suffix: str
    marker_stem: str
    kind: str
    block: str
    wrapper: str


def _existing(mod_root: Path, stem: str, kind: str, suffix: str, plan: Plan) -> Optional[str]:
    try:
        found = find_marker_file(mod_root, stem, kind, suffix)
    except WiringError as error:
        plan.errors.append(str(error))
        return None
    return found.relative_to(mod_root).as_posix() if found else None


def _choose_target(mod_root: Path, stem: str, kind: str, suffix: str, explicit: Optional[str], default: str, plan: Plan) -> str:
    """The file for a block: the one already holding it, else `explicit`, else `default`.

    The lookup always runs. A block already marked in another file than an explicit choice is an error,
    because writing the explicit file would define the block twice.
    """

    found = _existing(mod_root, stem, kind, suffix, plan)
    if not explicit:
        return found or default
    chosen = explicit.replace("\\", "/")
    if found and not _same_file(mod_root, found, chosen):
        plan.errors.append(
            f"the {kind} block of {stem} is already in {found}; writing it to {chosen} would define it twice "
            f"(pass {found}, or remove that block first)"
        )
    return chosen


def _check_animation_markers(mod_root: Path, registration: Registration, plan: Plan) -> None:
    """Refuse a model .asset block that a rerun would duplicate: marked in a file the registration does not name."""

    wanted = [asset_path for asset_path, _block in registration.asset_sections]
    for path in marker_files(mod_root, registration.stem, KIND_ANIMATIONS, ".asset"):
        found = path.relative_to(mod_root).as_posix()
        if not any(_same_file(mod_root, found, asset_path) for asset_path in wanted):
            plan.errors.append(f"the {KIND_ANIMATIONS} block of {registration.stem} is already in {found}, but the registration puts it in {', '.join(wanted)}; remove that block first")


def _check_folders(registration: Registration, folder: str, plan: Plan) -> None:
    for asset_path, _block in registration.asset_sections:
        asset_folder = asset_path.rsplit("/", 1)[0] if "/" in asset_path else ""
        if asset_folder != folder:
            plan.errors.append(f"the model .asset {asset_path} is not in the mesh's folder {folder}")


def _check_runtime_files(registration: Registration, available: Dict[str, Path], plan: Plan) -> None:
    needed = [Path(mesh_file(registration)).name, *mesh_texture_names(registration), *animation_files(registration)]
    for name in needed:
        if name not in available:
            plan.errors.append(f"the registration names {name}, which is not in runtime/files")


def _targets(registration: Registration, entity_block: str, gfx_rel: str, entity_rel: str) -> List[Target]:
    """Every block, in the order the blocks are written."""

    stem = registration.stem
    targets = [Target(gfx_rel, ".gfx", stem, KIND_PDXMESH, registration.gfx_block, "objectTypes")]
    targets += [Target(asset_path, ".asset", stem, KIND_ANIMATIONS, block, "") for asset_path, block in registration.asset_sections]
    targets.append(Target(entity_rel, ".asset", stem, KIND_ENTITY, entity_block, ""))
    return targets


def _plan_block_group(mod_root: Path, rel: str, group: Sequence[Target], plan: Plan) -> None:
    suffix = group[0].suffix
    try:
        rel = safe_destination(mod_root, rel, "the target")
        if not rel.lower().endswith(suffix):
            raise WiringError(f"{rel} must be a {suffix} path inside the mod")
        path = mod_root / rel
        existing = TextFile.read(path) if path.is_file() else None
        current = existing
        for target in group:
            current = upsert_block(current, stem=target.marker_stem, kind=target.kind, block=target.block, wrapper=target.wrapper, where=rel)
    except (WiringError, UnicodeDecodeError) as error:
        plan.errors.append(str(error))
        return
    assert current is not None
    payload = current.encode()
    status = "create" if existing is None else "unchanged" if existing.encode() == payload else "update"
    kinds = ", ".join(f"{target.kind} ({target.marker_stem})" for target in group)
    plan.items.append(PlanItem("block", rel, status, kinds, payload=payload))


def _plan_runtime_files(mod_root: Path, folder: str, available: Dict[str, Path], plan: Plan) -> None:
    for name in sorted(available):
        source = available[name]
        try:
            dest_rel = safe_destination(mod_root, f"{folder}/{name}" if folder else name, "the runtime file destination")
        except WiringError as error:
            plan.errors.append(str(error))
            continue
        data = source.read_bytes()
        dest = mod_root / dest_rel
        if not dest.is_file():
            status = "create"
        else:
            status = "unchanged" if sha256_bytes(dest.read_bytes()) == sha256_bytes(data) else "update"
        plan.items.append(PlanItem("file", dest_rel, status, "runtime file", payload=None, source=source))


def build_plan(
    *,
    mod_root: Path,
    registration: Registration,
    entity_block: str,
    runtime_files: Path,
    gfx_file: Optional[str] = None,
    entity_file: Optional[str] = None,
    prefix: Optional[str] = None,
) -> Plan:
    """Decide every write, without writing. Any entry in `errors` means nothing may be written."""

    plan = Plan()
    stem = registration.stem
    prefix = prefix or default_prefix(mod_root, stem)
    folder = model_folder(registration)
    _check_folders(registration, folder, plan)
    available = {path.name: path for path in sorted(runtime_files.glob("*")) if path.is_file()} if runtime_files.is_dir() else {}
    _check_runtime_files(registration, available, plan)
    for found_file, name in find_definitions(mod_root, registered_names(registration), stem):
        plan.errors.append(f"{found_file} already defines {name} outside this tool's markers; remove that copy or keep it and skip wiring")

    gfx_rel = _choose_target(mod_root, stem, KIND_PDXMESH, ".gfx", gfx_file, f"gfx/entities/{prefix}_units.gfx", plan)
    entity_rel = _choose_target(mod_root, stem, KIND_ENTITY, ".asset", entity_file, f"gfx/entities/{prefix}_units.asset", plan)
    _check_animation_markers(mod_root, registration, plan)
    by_path: Dict[str, List[Target]] = {}
    for target in _targets(registration, entity_block, gfx_rel, entity_rel):
        by_path.setdefault(target.rel, []).append(target)
    for rel, group in by_path.items():
        _plan_block_group(mod_root, rel, group, plan)
    _plan_runtime_files(mod_root, folder, available, plan)
    return plan


def _write_atomically(dest: Path, data: bytes) -> None:
    """Write `data` to a temporary file next to `dest`, then replace `dest` with it in one step."""

    dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = dest.with_name(f".{dest.name}.wire_unit.tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, dest)
    finally:
        temporary.unlink(missing_ok=True)


def apply_plan(mod_root: Path, plan: Plan) -> None:
    """Write what the plan says. Skips unchanged items; refuses to run with errors.

    The runtime files are copied first and the blocks that register them last, so a failure midway never
    leaves an entity that names files the mod does not have. Every file is replaced in one step.
    """

    if plan.errors:
        raise WiringError("the plan has errors; nothing was written")
    ordered = [item for item in plan.items if item.kind == "file"] + [item for item in plan.items if item.kind != "file"]
    for item in ordered:
        if item.status == "unchanged":
            continue
        try:
            if item.kind == "block":
                _write_atomically(mod_root / item.path, item.payload or b"")
            else:
                assert item.source is not None
                _write_atomically(mod_root / item.path, item.source.read_bytes())
        except OSError as error:
            raise WiringError(f"could not write {item.path}: {error}") from error


# ---------------------------------------------------------------- verdict


@dataclass
class Report:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return "FAIL" if self.errors else "PASS"
