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
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

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


@dataclass
class TextFile:
    """A source file split into the parts a rewrite must keep: byte order mark, newline, LF text."""

    bom: bool
    newline: str
    text: str  # LF only

    @classmethod
    def read(cls, path: Path) -> "TextFile":
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        decoded = raw[3:].decode("utf-8") if bom else raw.decode("utf-8")
        newline = "\r\n" if "\r\n" in decoded else "\n"
        return cls(bom, newline, decoded.replace("\r\n", "\n"))

    def encode(self) -> bytes:
        body = self.text.replace("\n", self.newline).encode("utf-8")
        return (b"\xef\xbb\xbf" if self.bom else b"") + body


def begin_marker(stem: str, kind: str) -> str:
    return f"{MARKER_PREFIX} begin {stem} {kind}"


def end_marker(stem: str, kind: str) -> str:
    return f"{MARKER_PREFIX} end {stem} {kind}"


def marked(stem: str, kind: str, block: str) -> List[str]:
    return [begin_marker(stem, kind), *block.split("\n"), end_marker(stem, kind)]


def _marker_span(lines: Sequence[str], stem: str, kind: str, where: str) -> Optional[Tuple[int, int]]:
    begins = [index for index, line in enumerate(lines) if line.strip() == begin_marker(stem, kind)]
    ends = [index for index, line in enumerate(lines) if line.strip() == end_marker(stem, kind)]
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


def upsert_block(existing: Optional[TextFile], *, stem: str, kind: str, block: str, wrapper: str, where: str) -> TextFile:
    """Put the marked block into `existing` (or a new file) and return the new content.

    `wrapper` is "objectTypes" for a `.gfx` file, whose blocks live inside `objectTypes = { }`, and
    "" for an `.asset` file, whose blocks are top level.
    """

    new_lines = marked(stem, kind, block)
    if existing is None:
        text = ("objectTypes = {\n\n" + "\n".join(new_lines) + "\n}\n") if wrapper else "\n".join(new_lines) + "\n"
        return TextFile(False, "\n", text)
    lines = existing.text.split("\n")
    span = _marker_span(lines, stem, kind, where)
    if span is not None:
        lines[span[0] : span[1] + 1] = new_lines
        return TextFile(existing.bom, existing.newline, "\n".join(lines))
    if wrapper:
        if not re.search(rf"\b{wrapper}\s*=\s*\{{", existing.text):
            raise WiringError(f"{where} has no '{wrapper} = {{' block to put the pdxmesh in")
        closing = [index for index, line in enumerate(lines) if line.strip() == "}"]
        if not closing:
            raise WiringError(f"{where} has no closing brace for '{wrapper} = {{'")
        at = closing[-1]
        lines[at:at] = ["", *new_lines]
        return TextFile(existing.bom, existing.newline, "\n".join(lines))
    text = existing.text
    if text and not text.endswith("\n"):
        text += "\n"
    gap = "\n" if text.strip() else ""
    return TextFile(existing.bom, existing.newline, text + gap + "\n".join(new_lines) + "\n")


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
    return path.read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")


def find_marker_file(mod_root: Path, stem: str, kind: str, suffix: str) -> Optional[Path]:
    """The one file that already holds this job's `kind` block, if any."""

    found = [path for path in source_files(mod_root) if path.suffix.lower() == suffix and has_markers(read_text_lenient(path), stem, kind)]
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


def apply_sound_events(entity_block: str, events: Sequence[SoundEvent], clip_samples: Optional[Dict[str, int]] = None, stem: str = "") -> str:
    """Add an `event` line to the states each sound event names. Raises WiringError for one that fits no state."""

    if not events:
        return entity_block
    lines = entity_block.split("\n")
    states: List[Tuple[int, int, str]] = []  # first line, last line, state name
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
    names = [name for _first, _last, name in states]
    inserts: Dict[int, List[str]] = {}
    for event in events:
        targets = [name for name in names if name == event.role] or [name for name in names if STATE_TO_ROLE.get(name) == event.role and name != "idle"]
        if not targets:
            raise WiringError(f"sound event for role {event.role}: the entity has no such state ({', '.join(dict.fromkeys(names))})")
        for state_first, state_last, name in states:
            if name not in targets:
                continue
            if clip_samples is not None and stem:
                clip = f"{stem}_{STATE_TO_ROLE.get(name, name)}.anim"
                samples = clip_samples.get(clip)
                if samples is not None and event.frame >= samples:
                    raise WiringError(f"sound event for {event.role} is at frame {event.frame}, but {clip} has {samples} frames")
            inserts.setdefault(state_first, []).append(f'\t\tevent = {{ time = {event.frame} sound = {{ soundeffect = "{event.soundeffect}" }} }}')
    out: List[str] = []
    skip_until = -1
    by_first = {first: (last, name) for first, last, name in states}
    for position, line in enumerate(lines):
        if position <= skip_until:
            continue
        added = inserts.get(position)
        if added is None:
            out.append(line)
            continue
        last, _name = by_first[position]
        if last == position:  # one-line state: open it up
            head = line.rstrip()
            if not head.endswith("}"):
                raise WiringError(f"cannot read the state on entity line {position + 1}")
            out += [head[:-1].rstrip(), *added, "\t}"]
        else:  # a state that already spans lines: add before its closing brace
            out += lines[position:last] + added + [lines[last]]
            skip_until = last
    return "\n".join(out)


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
    mesh_rel = mesh_file(registration)
    folder = mesh_rel.rsplit("/", 1)[0] if "/" in mesh_rel else ""
    for asset_path, _block in registration.asset_sections:
        asset_folder = asset_path.rsplit("/", 1)[0] if "/" in asset_path else ""
        if asset_folder != folder:
            plan.errors.append(f"the model .asset {asset_path} is not in the mesh's folder {folder}")

    available = {path.name: path for path in sorted(runtime_files.glob("*")) if path.is_file()} if runtime_files.is_dir() else {}
    needed = [Path(mesh_rel).name, *mesh_texture_names(registration), *animation_files(registration)]
    for name in needed:
        if name not in available:
            plan.errors.append(f"the registration names {name}, which is not in runtime/files")

    for found_file, name in find_definitions(mod_root, registered_names(registration), stem):
        plan.errors.append(f"{found_file} already defines {name} outside this tool's markers; remove that copy or keep it and skip wiring")

    gfx_rel = gfx_file or _existing(mod_root, stem, KIND_PDXMESH, ".gfx", plan) or f"gfx/entities/{prefix}_units.gfx"
    entity_rel = entity_file or _existing(mod_root, stem, KIND_ENTITY, ".asset", plan) or f"gfx/entities/{prefix}_units.asset"
    # (target path, suffix, marker stem, marker kind, block, wrapper), in the order the blocks are written
    targets: List[Tuple[str, str, str, str, str, str]] = [(gfx_rel, ".gfx", stem, KIND_PDXMESH, registration.gfx_block, "objectTypes")]
    for asset_path, block in registration.asset_sections:
        targets.append((asset_path, ".asset", Path(asset_path).stem, KIND_ANIMATIONS, block, ""))
    targets.append((entity_rel, ".asset", stem, KIND_ENTITY, entity_block, ""))
    by_path: Dict[str, List[Tuple[str, str, str, str, str, str]]] = {}
    for target in targets:
        by_path.setdefault(target[0], []).append(target)
    for rel, group in by_path.items():
        suffix = group[0][1]
        if not rel.lower().endswith(suffix) or rel.startswith("/") or ".." in rel.split("/") or ":" in rel:
            plan.errors.append(f"{rel} must be a {suffix} path inside the mod")
            continue
        path = mod_root / rel
        try:
            existing = TextFile.read(path) if path.is_file() else None
            current = existing
            for _rel, _suffix, marker_stem, marker_kind, block, wrapper in group:
                current = upsert_block(current, stem=marker_stem, kind=marker_kind, block=block, wrapper=wrapper, where=rel)
        except (WiringError, UnicodeDecodeError) as error:
            plan.errors.append(str(error))
            continue
        assert current is not None
        payload = current.encode()
        status = "create" if existing is None else "unchanged" if existing.encode() == payload else "update"
        kinds = ", ".join(f"{kind} ({marker})" for _r, _s, marker, kind, _b, _w in group)
        plan.items.append(PlanItem("block", rel, status, kinds, payload=payload))

    for name in sorted(available):
        source = available[name]
        dest_rel = f"{folder}/{name}" if folder else name
        dest = mod_root / dest_rel
        data = source.read_bytes()
        if not dest.is_file():
            status = "create"
        else:
            status = "unchanged" if sha256_bytes(dest.read_bytes()) == sha256_bytes(data) else "update"
        plan.items.append(PlanItem("file", dest_rel, status, "runtime file", payload=None, source=source))
    return plan


def _existing(mod_root: Path, stem: str, kind: str, suffix: str, plan: Plan) -> Optional[str]:
    try:
        found = find_marker_file(mod_root, stem, kind, suffix)
    except WiringError as error:
        plan.errors.append(str(error))
        return None
    return found.relative_to(mod_root).as_posix() if found else None


def apply_plan(mod_root: Path, plan: Plan) -> None:
    """Write what the plan says. Skips unchanged items; refuses to run with errors."""

    if plan.errors:
        raise WiringError("the plan has errors; nothing was written")
    for item in plan.items:
        if item.status == "unchanged":
            continue
        dest = mod_root / item.path
        if item.kind == "block":
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(item.payload or b"")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            assert item.source is not None
            dest.write_bytes(item.source.read_bytes())


# ---------------------------------------------------------------- verdict


@dataclass
class Report:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return "FAIL" if self.errors else "PASS"
