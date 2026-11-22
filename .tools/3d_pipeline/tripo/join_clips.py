"""Join Tripo exports of one rigged model, each holding its own clips, into the one rigged GLB the intake reads. Free, no Blender.

    py -3.13 -B .tools/3d_pipeline/tripo/join_clips.py <first.glb> <more.glb> ... --out <job folder>/inbox/<asset_slug>__rigged.glb

Tripo's Agentic Canvas holds one clip in an Animation node and exports one clip per GLB (2026-11-14), where the page exports every clip
of a model at once. Export each Animation node of the same Rigging node, then join the files here. The first file gives the mesh, the
skin and the textures. Every clip of the other files is copied in, its channels mapped onto the first file's nodes by name.

It refuses files that are not the same rigged model: a joint of the skin the first file lacks, or another vertex count. A clip whose name
the joined file already has is left out and named in the report, because each role is picked by its clip name (two exports of one
preset are the same clip). It prints one JSON line with the clips joined.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

GLB_MAGIC = b"glTF"
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942


class JoinError(ValueError):
    pass


def read_glb(path: Path) -> Tuple[Dict[str, Any], bytearray]:
    data = Path(path).read_bytes()
    if data[:4] != GLB_MAGIC:
        raise JoinError(f"{Path(path).name} is not a binary glTF (GLB) file")
    document: Optional[Dict[str, Any]] = None
    binary = bytearray()
    offset = 12
    while offset + 8 <= len(data):
        length, kind = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8: offset + 8 + length]
        if kind == JSON_CHUNK:
            document = json.loads(chunk.decode("utf-8"))
        elif kind == BIN_CHUNK and not binary:
            binary = bytearray(chunk)
        offset += 8 + length
    if document is None:
        raise JoinError(f"{Path(path).name} has no glTF JSON chunk")
    return document, binary


def write_glb(path: Path, document: Dict[str, Any], binary: bytes) -> None:
    text = json.dumps(document, separators=(",", ":")).encode("utf-8")
    text += b" " * (-len(text) % 4)
    binary = bytes(binary) + b"\0" * (-len(binary) % 4)
    body = struct.pack("<II", len(text), JSON_CHUNK) + text + struct.pack("<II", len(binary), BIN_CHUNK) + binary
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(GLB_MAGIC + struct.pack("<II", 2, 12 + len(body)) + body)


def joint_names(document: Dict[str, Any]) -> List[str]:
    nodes = document.get("nodes") or []
    return [nodes[index].get("name", f"node_{index}") for skin in document.get("skins") or [] for index in skin.get("joints") or []]


def vertex_count(document: Dict[str, Any]) -> int:
    accessors = document.get("accessors") or []
    return sum(accessors[primitive["attributes"]["POSITION"]]["count"]
               for mesh in document.get("meshes") or [] for primitive in mesh.get("primitives") or [] if "POSITION" in primitive["attributes"])


def same_model(base: Dict[str, Any], other: Dict[str, Any], name: str) -> None:
    missing = sorted(set(joint_names(other)) - set(joint_names(base)))
    if missing:
        raise JoinError(f"{name} is not the same rigged model: its skin has joints the first file lacks ({', '.join(missing[:6])})")
    if vertex_count(other) != vertex_count(base):
        raise JoinError(f"{name} is not the same rigged model: {vertex_count(other)} vertices against {vertex_count(base)}")


def copy_accessor(index: int, source: Dict[str, Any], source_bin: bytes, target: Dict[str, Any], target_bin: bytearray) -> int:
    """Copy one accessor and the bytes it reads into the target file, as its own buffer view. Returns its index in the target."""

    accessor = dict(source["accessors"][index])
    view = dict(source["bufferViews"][accessor["bufferView"]])
    start = view.get("byteOffset", 0)
    data = source_bin[start: start + view["byteLength"]]
    target_bin.extend(b"\0" * (-len(target_bin) % 4))
    view["byteOffset"] = len(target_bin)
    view["buffer"] = 0
    view.pop("target", None)
    target_bin.extend(data)
    target.setdefault("bufferViews", []).append(view)
    accessor["bufferView"] = len(target["bufferViews"]) - 1
    target.setdefault("accessors", []).append(accessor)
    return len(target["accessors"]) - 1


def copy_animation(animation: Dict[str, Any], source: Dict[str, Any], source_bin: bytes, target: Dict[str, Any],
                   target_bin: bytearray) -> Dict[str, Any]:
    by_name = {node.get("name"): index for index, node in enumerate(target.get("nodes") or [])}
    source_nodes = source.get("nodes") or []
    copied: Dict[int, int] = {}

    def accessor(index: int) -> int:
        if index not in copied:
            copied[index] = copy_accessor(index, source, source_bin, target, target_bin)
        return copied[index]

    samplers = [{**sampler, "input": accessor(sampler["input"]), "output": accessor(sampler["output"])} for sampler in animation["samplers"]]
    channels = []
    for channel in animation["channels"]:
        node_name = source_nodes[channel["target"]["node"]].get("name")
        if node_name not in by_name:
            raise JoinError(f"clip {animation.get('name')!r} moves node {node_name!r}, which the first file lacks")
        channels.append({**channel, "target": {**channel["target"], "node": by_name[node_name]}})
    return {**animation, "samplers": samplers, "channels": channels}


def join(paths: List[Path], out: Path) -> Dict[str, Any]:
    if not paths:
        raise JoinError("give at least one GLB")
    base, base_bin = read_glb(paths[0])
    names = [animation.get("name") for animation in base.get("animations") or []]
    skipped: List[str] = []
    for path in paths[1:]:
        other, other_bin = read_glb(path)
        same_model(base, other, Path(path).name)
        for animation in other.get("animations") or []:
            if animation.get("name") in names:
                skipped.append(f"{animation.get('name')} ({Path(path).name})")
                continue
            base.setdefault("animations", []).append(copy_animation(animation, other, other_bin, base, base_bin))
            names.append(animation.get("name"))
    base_bin.extend(b"\0" * (-len(base_bin) % 4))
    base["buffers"][0]["byteLength"] = len(base_bin)
    base["buffers"][0].pop("uri", None)
    write_glb(out, base, base_bin)
    return {"tool": "join_clips", "out": Path(out).as_posix(), "files": len(paths), "clips": names, "skipped": skipped}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("glbs", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report = join(args.glbs, args.out)
    except JoinError as error:
        print(json.dumps({"tool": "join_clips", "error": str(error)}))
        return 2
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
