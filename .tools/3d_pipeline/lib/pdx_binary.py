"""Read Paradox binary `.mesh` and `.anim` files without Blender.

The format is the one io_pdx_mesh 0.91 writes and reads (`pdx_data.py`): the
header `@@b@`, then objects (`[` repeated once per depth level, a zero-ended
name) and properties (`!`, a one-byte name length, the name, a type byte `i`,
`f` or `s`, a 32-bit count and the values). This reader only measures files;
it never writes one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from struct import error as StructError
from struct import unpack_from
from typing import Dict, Iterator, List, Optional, Union

Value = Union[List[int], List[float], List[str]]


@dataclass
class PdxNode:
    name: str
    depth: int
    properties: Dict[str, Value] = field(default_factory=dict)
    children: List["PdxNode"] = field(default_factory=list)

    def child(self, name: str) -> Optional["PdxNode"]:
        return next((node for node in self.children if node.name == name), None)

    def walk(self) -> Iterator["PdxNode"]:
        yield self
        for node in self.children:
            yield from node.walk()


class PdxFormatError(ValueError):
    pass


def _read_value(data: bytes, position: int) -> tuple[Value, int]:
    kind = chr(data[position])
    count = unpack_from("<i", data, position + 1)[0]
    position += 5
    if count < 0:
        raise PdxFormatError(f"negative value count at byte {position}")
    if kind == "i":
        return list(unpack_from(f"<{count}i", data, position)), position + 4 * count
    if kind == "f":
        return list(unpack_from(f"<{count}f", data, position)), position + 4 * count
    if kind == "s":
        values: List[str] = []
        for _ in range(count):
            length = unpack_from("<i", data, position)[0]
            position += 4
            values.append(data[position : position + length].decode("latin-1").rstrip("\0"))
            position += length
        return values, position
    raise PdxFormatError(f"unknown value type {kind!r} at byte {position - 5}")


def parse(data: bytes) -> PdxNode:
    """Return the file as a tree whose root is a synthetic `File` node."""

    if data[:4] != b"@@b@":
        raise PdxFormatError("not a Paradox binary file (header is not @@b@)")
    root = PdxNode("File", 0)
    stack = [root]
    position = 4
    end = len(data)
    try:
        while position < end:
            marker = data[position]
            if marker == ord("["):
                depth = 0
                while data[position] == ord("["):
                    depth += 1
                    position += 1
                name_end = data.index(b"\0", position)
                node = PdxNode(data[position:name_end].decode("latin-1"), depth)
                position = name_end + 1
                del stack[depth:]
                if not stack:
                    raise PdxFormatError(f"object {node.name} has no parent")
                stack[-1].children.append(node)
                stack.append(node)
            elif marker == ord("!"):
                length = data[position + 1]
                name = data[position + 2 : position + 2 + length].decode("latin-1").rstrip("\0")
                value, position = _read_value(data, position + 2 + length)
                stack[-1].properties[name] = value
            else:
                raise PdxFormatError(f"unexpected byte {marker:#x} at {position}")
    except (IndexError, ValueError, StructError) as exc:
        if isinstance(exc, PdxFormatError):
            raise
        raise PdxFormatError(f"truncated or malformed file near byte {position}: {exc}") from exc
    return root


def read(path: Path) -> PdxNode:
    return parse(Path(path).read_bytes())


@dataclass
class MeshStream:
    """One material stream of one shape (what the engine draws in one call)."""

    shape: str
    vertices: int
    triangles: int
    index_entries: int
    max_index: int
    influences_per_vertex: int
    material_shader: str
    textures: Dict[str, str]


@dataclass
class MeshSummary:
    streams: List[MeshStream]
    shapes: List[str]
    bones: List[str]
    locators: List[str]

    @property
    def triangles(self) -> int:
        return sum(stream.triangles for stream in self.streams)


def summarize_mesh(root: PdxNode) -> MeshSummary:
    """Measure the shapes, streams, skeleton and locators of a `.mesh` tree."""

    objects = root.child("object")
    if objects is None:
        raise PdxFormatError("the file has no object block")
    streams: List[MeshStream] = []
    shapes: List[str] = []
    bones: List[str] = []
    for shape in objects.children:
        shapes.append(shape.name)
        skeleton = shape.child("skeleton")
        if skeleton is not None:
            for joint in skeleton.children:
                if joint.name not in bones:
                    bones.append(joint.name)
        for mesh in (node for node in shape.children if node.name == "mesh"):
            positions = mesh.properties.get("p", [])
            indices = [int(value) for value in mesh.properties.get("tri", [])]
            skin = mesh.child("skin")
            material = mesh.child("material")
            influences = 0
            if skin is not None and skin.properties.get("bones"):
                influences = int(skin.properties["bones"][0])
            textures = {}
            shader = ""
            if material is not None:
                shader = str((material.properties.get("shader") or [""])[0])
                for key in ("diff", "n", "spec"):
                    if material.properties.get(key):
                        textures[key] = str(material.properties[key][0])
            streams.append(
                MeshStream(
                    shape=shape.name,
                    vertices=len(positions) // 3,
                    triangles=len(indices) // 3,
                    index_entries=len(indices),
                    max_index=max(indices) if indices else -1,
                    influences_per_vertex=influences,
                    material_shader=shader,
                    textures=textures,
                )
            )
    locators_node = root.child("locator")
    locators = [node.name for node in locators_node.children] if locators_node is not None else []
    return MeshSummary(streams=streams, shapes=shapes, bones=bones, locators=locators)


@dataclass
class AnimSummary:
    fps: float
    samples: int
    joints: List[str]
    animated_joints: List[str]

    @property
    def seconds(self) -> float:
        return self.samples / self.fps if self.fps else 0.0


def summarize_anim(root: PdxNode) -> AnimSummary:
    """Measure the frame rate, sample count and joints of an `.anim` tree."""

    info = root.child("info")
    if info is None:
        raise PdxFormatError("the file has no info block")
    fps = float((info.properties.get("fps") or [0.0])[0])
    samples = int((info.properties.get("sa") or [0])[0])
    joints = [node.name for node in info.children]
    animated = [
        node.name
        for node in info.children
        if str((node.properties.get("sa") or [""])[0]).strip()
    ]
    return AnimSummary(fps=fps, samples=samples, joints=joints, animated_joints=animated)
