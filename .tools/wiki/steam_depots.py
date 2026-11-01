"""List the game files that changed between two Steam builds of Hearts of Iron IV.

Steam keeps a manifest for each installed content depot in ``<Steam>/depotcache/<depot>_<manifest>.manifest``,
and ``steamapps/appmanifest_394360.acf`` names the manifest id of every depot that is installed now. A manifest
lists every file of its depot with the SHA-1 of the file's content. ``wiki_status.py --record`` stores the
installed manifest ids next to the documentation index; after the next game update, ``wiki_status.py`` reads the
old and new manifests from the depot cache and lists the files that were added, removed or changed, so pages
whose ``sources`` name a changed script or define file are re-checked, not only pages that cite documentation.

Steam keeps an old manifest only for a while after an update. When one is missing, the comparison is
unavailable for that depot and the tool says so; it never guesses. Reads only; standard library only.
"""

from __future__ import annotations

import re
import struct
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

APP_ID = "394360"
PAYLOAD_MAGIC = 0x71F617D0
METADATA_MAGIC = 0x1F4812BE
DIRECTORY_FLAG = 64
DEPOT_ENTRY = re.compile(r'"(\d+)"\s*\{[^{}]*?"manifest"\s+"(\d+)"', re.S)


def _varint(data: bytes, index: int) -> Tuple[int, int]:
    shift = value = 0
    while True:
        byte = data[index]
        index += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, index
        shift += 7


def _fields(data: bytes) -> Iterator[Tuple[int, object]]:
    """Yield (field number, value) for one protobuf message: ints for varints, bytes otherwise."""
    index = 0
    while index < len(data):
        key, index = _varint(data, index)
        number, wire = key >> 3, key & 7
        value: object
        if wire == 0:
            value, index = _varint(data, index)
        elif wire == 2:
            length, index = _varint(data, index)
            value, index = data[index:index + length], index + length
        elif wire in (1, 5):
            size = 8 if wire == 1 else 4
            value, index = data[index:index + size], index + size
        else:
            raise ValueError(f"unsupported protobuf wire type {wire}")
        yield number, value


def read_manifest(path: Path) -> Dict[str, str]:
    """Map each file of a depot manifest (``/``-separated path) to the SHA-1 of its content."""
    data = path.read_bytes()
    index, payload = 0, None
    while index + 8 <= len(data):
        magic, length = struct.unpack_from("<II", data, index)
        index += 8
        if magic == PAYLOAD_MAGIC:
            payload = data[index:index + length]
            break
        if magic != METADATA_MAGIC:
            break
        index += length
    if payload is None:
        raise ValueError(f"{path.name} has no file list")
    files: Dict[str, str] = {}
    for number, mapping in _fields(payload):
        if number != 1 or not isinstance(mapping, bytes):
            continue
        entry = dict(_fields(mapping))
        flags = entry.get(3, 0)
        if isinstance(flags, int) and flags & DIRECTORY_FLAG:
            continue
        name, digest = entry.get(1, b""), entry.get(5, b"")
        if isinstance(name, bytes) and isinstance(digest, bytes):
            files[name.decode("utf-8", "replace").rstrip("\0").replace("\\", "/")] = digest.hex()
    return files


def installed_depots(game_dir: Path) -> Dict[str, str]:
    """Depot id -> manifest id of the installed build, from the library's appmanifest (empty when absent)."""
    acf = game_dir.parent.parent / f"appmanifest_{APP_ID}.acf"
    try:
        text = acf.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    start = text.find('"InstalledDepots"')
    if start < 0:
        return {}
    depth, end = 0, len(text)
    for position in range(text.index("{", start), len(text)):
        depth += {"{": 1, "}": -1}.get(text[position], 0)
        if depth == 0:
            end = position
            break
    return dict(DEPOT_ENTRY.findall(text[start:end]))


def depot_caches(game_dir: Path, steam_roots: Iterable[Path] = ()) -> List[Path]:
    """Depot cache folders to search: the game's library first, then the Steam installations."""
    folders = [game_dir.parent.parent.parent / "depotcache", *(root / "depotcache" for root in steam_roots)]
    unique: List[Path] = []
    for folder in folders:
        if folder not in unique and folder.is_dir():
            unique.append(folder)
    return unique


def find_manifest(caches: Iterable[Path], depot: str, manifest: str) -> Optional[Path]:
    for cache in caches:
        candidate = cache / f"{depot}_{manifest}.manifest"
        if candidate.is_file():
            return candidate
    return None


def changed_files(old: Dict[str, str], new: Dict[str, str], caches: List[Path]) -> Tuple[Dict[str, str], List[str]]:
    """Compare two depot sets: (path -> "added" / "removed" / "changed", notes on depots that could not be compared)."""
    changes: Dict[str, str] = {}
    notes: List[str] = []
    for depot in sorted(set(old) | set(new)):
        before, after = old.get(depot), new.get(depot)
        if before == after:
            continue
        if before is None or after is None:
            notes.append(f"depot {depot} was {'added' if before is None else 'removed'}; its files are not compared")
            continue
        paths = find_manifest(caches, depot, before), find_manifest(caches, depot, after)
        missing = [m for m, p in zip((before, after), paths) if p is None]
        if missing:
            notes.append(f"depot {depot}: manifest {', '.join(missing)} is not in the Steam depot cache")
            continue
        a, b = (read_manifest(p) for p in paths if p is not None)
        for name in set(a) | set(b):
            if a.get(name) != b.get(name):
                changes[name] = "added" if name not in a else "removed" if name not in b else "changed"
    return changes, notes
