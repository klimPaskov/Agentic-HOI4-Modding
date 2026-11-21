"""Write a Paradox binary tree (`lib/pdx_binary.parse`'s `PdxNode`) back to bytes. No Blender.

The format is the one `pdx_binary` reads: `@@b@`, then each node's properties (`!`, the name's length and name, a type byte `i`, `f` or `s`,
a count and the values) followed by its children (`[` repeated by depth, the name, a NUL). A property's type is read back from its values:
Python ints are `i`, floats `f`, strings `s`. `kinds` names a property whose list is empty or whose type must be forced. Reading a file
with `pdx_binary.read` and writing it with `dump` gives the same bytes for the kit's exports and vanilla's units (tests/test_pdx_write.py),
so a stage can add a bone, a locator or a joint and write the file without Blender.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Dict, Optional

from .pdx_binary import PdxNode

# A property name is written without a terminating NUL (io_pdx_mesh and vanilla files both: a read and a write give the same bytes)
NAME_NUL = False


def _kind(values, forced: Optional[str]) -> str:
    if forced:
        return forced
    if values and isinstance(values[0], str):
        return "s"
    if values and all(isinstance(v, int) and not isinstance(v, bool) for v in values):
        return "i"
    return "f"


def _property(name: str, values, forced: Optional[str] = None) -> bytes:
    raw = name.encode("latin-1") + (b"\0" if NAME_NUL else b"")
    kind = _kind(values, forced)
    out = b"!" + struct.pack("<B", len(raw)) + raw + kind.encode() + struct.pack("<i", len(values))
    if kind == "i":
        return out + struct.pack(f"<{len(values)}i", *[int(v) for v in values])
    if kind == "f":
        return out + struct.pack(f"<{len(values)}f", *[float(v) for v in values])
    for value in values:
        encoded = str(value).encode("latin-1") + b"\0"
        out += struct.pack("<i", len(encoded)) + encoded
    return out


def _node(node: PdxNode, kinds: Dict[str, str]) -> bytes:
    out = b"[" * node.depth + node.name.encode("latin-1") + b"\0" if node.depth else b""
    for name, values in node.properties.items():
        out += _property(name, values, kinds.get(name))
    for child in node.children:
        out += _node(child, kinds)
    return out


def dump(root: PdxNode, kinds: Optional[Dict[str, str]] = None) -> bytes:
    """The bytes of a tree whose root is `pdx_binary.parse`'s synthetic `File` node."""

    return b"@@b@" + _node(root, kinds or {})


def write(path: Path, root: PdxNode, kinds: Optional[Dict[str, str]] = None) -> None:
    Path(path).write_bytes(dump(root, kinds))
