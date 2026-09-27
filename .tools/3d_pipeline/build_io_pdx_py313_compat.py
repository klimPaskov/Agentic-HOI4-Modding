"""Build the reproducible io_pdx_mesh 0.91 compatibility archive for Blender 5.2."""

from __future__ import annotations

import argparse
import hashlib
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "config" / "dependencies.lock.json"
PATCHES = {
    "io_pdx_mesh/__init__.py": [
        (b"from imp import reload", b"from importlib import reload"),
    ],
    "io_pdx_mesh/pdx_maya/maya_ui.py": [
        (b"from imp import reload", b"from importlib import reload"),
    ],
    "io_pdx_mesh/pdx_blender/blender_import_export.py": [
        (
            b'    new_shader.shadow_method = "CLIP"',
            b'    if hasattr(new_shader, "shadow_method"):\n'
            b'        new_shader.shadow_method = "CLIP"',
        ),
        (
            b'                ctx = bpy.context.copy()\n'
            b'                ctx["active_object"] = created[0]\n'
            b'                ctx["selected_editable_objects"] = created\n'
            b'                bpy.ops.object.join(ctx)\n'
            b'                ctx.clear()',
            b'                with bpy.context.temp_override(\n'
            b'                    active_object=created[0],\n'
            b'                    object=created[0],\n'
            b'                    selected_objects=created,\n'
            b'                    selected_editable_objects=created,\n'
            b'                ):\n'
            b'                    bpy.ops.object.join()',
        ),
    ],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def compatibility_archive_bytes(source_archive: bytes) -> bytes:
    """Apply only the reviewed compatibility substitutions to the locked archive."""
    output = BytesIO()
    seen: set[str] = set()
    with ZipFile(BytesIO(source_archive)) as source, ZipFile(output, "w") as patched:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename in PATCHES:
                for old, new in PATCHES[entry.filename]:
                    if b"\r\n" in data and b"\r\n" not in old:
                        old = old.replace(b"\n", b"\r\n")
                        new = new.replace(b"\n", b"\r\n")
                    if data.count(old) != 1:
                        raise ValueError(f"Unexpected compatibility anchor in {entry.filename}")
                    data = data.replace(old, new)
                seen.add(entry.filename)
            patched.writestr(entry, data)
    if seen != set(PATCHES):
        raise ValueError(f"Missing io_pdx_mesh patch targets: {sorted(set(PATCHES) - seen)}")
    return output.getvalue()


def build_compatibility_archive(source_path: Path, output_path: Path, lock: dict) -> str:
    if source_path.resolve() == output_path.resolve():
        raise ValueError("The compatibility build must not overwrite the upstream archive")
    source = source_path.read_bytes()
    policy = lock["compatibility"]["io_pdx_mesh"]
    source_hash = sha256(source)
    if len(source) != policy["source_size"] or source_hash != policy["source_sha256"]:
        raise ValueError("The upstream io_pdx_mesh archive does not match the source lock")
    archive = compatibility_archive_bytes(source)
    archive_hash = sha256(archive)
    if len(archive) != policy["archive_size"] or archive_hash != policy["archive_sha256"]:
        raise ValueError("The derived io_pdx_mesh archive does not match the compatibility lock")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(archive)
    return archive_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="verified upstream 0.91 archive")
    parser.add_argument("--output", type=Path, default=ROOT / "vendor/io_pdx_mesh/blender-io_pdx_mesh-0.91-py313.zip")
    args = parser.parse_args()
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    digest = build_compatibility_archive(args.source, args.output, lock)
    print(f"{args.output}: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
