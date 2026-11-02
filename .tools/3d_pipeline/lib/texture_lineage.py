"""Texture lineage: the maps bound to a model must belong to the model that is exported.

Meshy builds each stage (generation, remesh, rig, animation) with its own UV
layout. A remeshed, rigged or animated GLB carries the remesh UVs and embeds the
matching PBR maps, while `generation_model_textures/` holds maps for the earlier
generation UVs. Binding those to remesh geometry scrambles the colours, and the
pairing looks plausible to every size, range and hash check. This module picks
the texture directory that belongs to a model and proves, before export, that the
bound diffuse (and normal and metallic/roughness) source is the image embedded in
the exported geometry's GLB, or downloaded with that exact model.

Only the standard library is required. Pillow is used, when installed, solely for
the pixel fallback (a PNG downloaded with a model can be a lossless copy of the
JPEG embedded in the same GLB).
"""

from __future__ import annotations

import base64
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional

REPORT_SCHEMA = "hoi4_texture_lineage_v1"
ROLE_FILES = {
    "diffuse": "base_color.png",
    "normal": "normal.png",
    "specular": "metallic_roughness.png",
}
# glTF material slot for each role.
_SLOTS = {
    "diffuse": ("pbr", "baseColorTexture"),
    "normal": ("material", "normalTexture"),
    "specular": ("pbr", "metallicRoughnessTexture"),
}
_GLB_MAGIC = 0x46546C67
_JSON_CHUNK = 0x4E4F534A
_BIN_CHUNK = 0x004E4942


class TextureLineageError(RuntimeError):
    """The bound textures cannot be proven to belong to the exported geometry."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def textures_dir_rel(model_rel: str) -> str:
    """`provider/downloads/remesh_model.glb` -> `provider/downloads/remesh_model_textures`."""

    path = Path(model_rel)
    return path.with_name(f"{path.stem}_textures").as_posix()


def provider_texture_rels(model_rel: str) -> Dict[str, str]:
    """The provider maps downloaded with one model, keyed by material role."""

    folder = textures_dir_rel(model_rel)
    return {role: f"{folder}/{name}" for role, name in ROLE_FILES.items()}


def _read_glb(path: Path) -> tuple[Dict[str, Any], bytes]:
    data = path.read_bytes()
    if len(data) < 20 or struct.unpack_from("<I", data, 0)[0] != _GLB_MAGIC:
        raise TextureLineageError(f"{path.name} is not a binary glTF (GLB) file.")
    document: Optional[Dict[str, Any]] = None
    binary = b""
    offset = 12
    while offset + 8 <= len(data):
        length, kind = struct.unpack_from("<II", data, offset)
        chunk = data[offset + 8 : offset + 8 + length]
        if kind == _JSON_CHUNK:
            document = json.loads(chunk.decode("utf-8"))
        elif kind == _BIN_CHUNK and not binary:
            binary = chunk
        offset += 8 + length
    if document is None:
        raise TextureLineageError(f"{path.name} has no glTF JSON chunk.")
    return document, binary


def _image_bytes(document: Dict[str, Any], binary: bytes, glb: Path, index: int) -> Optional[bytes]:
    images = document.get("images") or []
    if not 0 <= index < len(images):
        return None
    image = images[index]
    if "bufferView" in image:
        view = document["bufferViews"][image["bufferView"]]
        start = int(view.get("byteOffset", 0))
        return binary[start : start + int(view["byteLength"])]
    uri = str(image.get("uri") or "")
    if uri.startswith("data:") and "," in uri:
        return base64.b64decode(uri.split(",", 1)[1])
    if uri and not uri.startswith(("/", "\\")) and ".." not in Path(uri).parts and ":" not in uri:
        sibling = glb.parent / uri
        if sibling.is_file():
            return sibling.read_bytes()
    return None


def embedded_images(glb: Path) -> Dict[str, List[bytes]]:
    """Raw image bytes embedded in a GLB for each role, over the materials the meshes use."""

    document, binary = _read_glb(glb)
    materials = document.get("materials") or []
    used: List[int] = []
    for mesh in document.get("meshes") or []:
        for primitive in mesh.get("primitives") or []:
            if isinstance(primitive.get("material"), int) and primitive["material"] not in used:
                used.append(primitive["material"])
    if not used:
        used = list(range(len(materials)))
    textures = document.get("textures") or []
    result: Dict[str, List[bytes]] = {role: [] for role in ROLE_FILES}
    for material_index in used:
        if not 0 <= material_index < len(materials):
            continue
        material = materials[material_index]
        for role, (scope, key) in _SLOTS.items():
            holder = material.get("pbrMetallicRoughness", {}) if scope == "pbr" else material
            slot = holder.get(key)
            if not isinstance(slot, dict) or not isinstance(slot.get("index"), int):
                continue
            if not 0 <= slot["index"] < len(textures):
                continue
            source = textures[slot["index"]].get("source")
            if not isinstance(source, int):
                continue
            raw = _image_bytes(document, binary, glb, source)
            if raw and raw not in result[role]:
                result[role].append(raw)
    return result


def _pixel_digest(source: Any) -> Optional[str]:
    """SHA-256 of the decoded RGBA pixels (with the size), or None without Pillow."""

    try:
        import io

        from PIL import Image
    except ImportError:
        return None
    Image.MAX_IMAGE_PIXELS = None
    try:
        with Image.open(io.BytesIO(source) if isinstance(source, bytes) else source) as image:
            rgba = image.convert("RGBA")
            return f"{rgba.size[0]}x{rgba.size[1]}:" + sha256_bytes(rgba.tobytes())
    except (OSError, ValueError, SyntaxError):  # unreadable or truncated image: no pixel proof
        return None


def verify_texture_lineage(
    job: Path,
    geometry_rel: str,
    provider_sources: Dict[str, str],
    *,
    report_rel: str,
) -> Dict[str, Any]:
    """Prove the provider sources belong to the model that supplies the exported geometry.

    `provider_sources` are the ungraded provider maps (role -> job-relative path).
    The diffuse source is mandatory and must match an image embedded in the
    geometry GLB or the `<model>_textures/base_color.png` downloaded with it.
    Normal and metallic/roughness must match when the model offers a reference
    for them. Writes the report (pass or fail) and raises on any mismatch.
    """

    job = Path(job)
    geometry = (job / geometry_rel).resolve()
    if not geometry.is_file():
        raise TextureLineageError(f"Exported geometry source is missing: {geometry_rel}")
    if "diffuse" not in provider_sources:
        raise TextureLineageError("Texture lineage needs a diffuse provider source.")
    embedded = embedded_images(geometry)
    sibling_dir = geometry.with_name(f"{geometry.stem}_textures")
    roles: Dict[str, Any] = {}
    problems: List[str] = []
    for role in ROLE_FILES:
        rel = provider_sources.get(role)
        if not rel:
            continue
        bound = (job / rel).resolve()
        if not bound.is_file():
            raise TextureLineageError(f"Bound {role} texture source is missing: {rel}")
        bound_sha = sha256_file(bound)
        embedded_hashes = [sha256_bytes(raw) for raw in embedded[role]]
        downloaded = sibling_dir / ROLE_FILES[role]
        downloaded_sha = sha256_file(downloaded) if downloaded.is_file() else None
        entry: Dict[str, Any] = {
            "bound_source_rel": rel,
            "bound_sha256": bound_sha,
            "geometry_embedded_sha256": embedded_hashes,
            "geometry_downloaded_rel": (
                downloaded.relative_to(job).as_posix() if downloaded_sha else None
            ),
            "geometry_downloaded_sha256": downloaded_sha,
        }
        if bound_sha in embedded_hashes:
            entry["status"], entry["matched_via"] = "pass", "embedded_bytes"
        elif bound_sha == downloaded_sha:
            entry["status"], entry["matched_via"] = "pass", "downloaded_with_model"
        elif not embedded_hashes and downloaded_sha is None:
            entry["matched_via"] = None
            if role == "diffuse":
                entry["status"] = "fail"
                problems.append(
                    f"diffuse: {geometry_rel} embeds no baseColor image and has no downloaded textures"
                    " to prove the bound map belongs to it"
                )
            else:
                entry["status"] = "no_reference"
        else:
            bound_pixels = _pixel_digest(bound)
            reference_pixels = [_pixel_digest(raw) for raw in embedded[role]]
            if downloaded_sha:
                reference_pixels.append(_pixel_digest(downloaded))
            if bound_pixels is not None and bound_pixels in reference_pixels:
                entry["status"], entry["matched_via"] = "pass", "decoded_pixels"
            else:
                entry["status"], entry["matched_via"] = "fail", None
                problems.append(
                    f"{role}: {rel} (sha256 {bound_sha[:12]}) is not the image embedded in or downloaded"
                    f" with {geometry_rel}"
                )
        roles[role] = entry
    report = {
        "schema": REPORT_SCHEMA,
        "geometry_source_rel": geometry_rel,
        "geometry_source_sha256": sha256_file(geometry),
        "status": "fail" if problems else "pass",
        "problems": problems,
        "roles": roles,
    }
    target = job / report_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if problems:
        raise TextureLineageError(
            "Texture lineage gate failed: "
            + "; ".join(problems)
            + f". The textures must come from the model that supplies the exported geometry (report: {report_rel})."
        )
    return report


def dds_header(path: Path) -> Dict[str, Any]:
    """Size, mip count and format tag of a DDS file, read from its header."""

    with Path(path).open("rb") as handle:
        head = handle.read(148)
    if len(head) < 128 or head[:4] != b"DDS " or struct.unpack_from("<I", head, 4)[0] != 124:
        raise TextureLineageError(f"{Path(path).name} is not a DDS file.")
    flags, height, width = struct.unpack_from("<III", head, 8)
    mips = struct.unpack_from("<I", head, 28)[0]
    pf_flags = struct.unpack_from("<I", head, 80)[0]
    four_cc = head[84:88]
    bits = struct.unpack_from("<I", head, 88)[0]
    mip_count = mips if (flags & 0x20000 and mips > 0) else 1
    needs_chain = max(width, height) > 1
    return {
        "width": width,
        "height": height,
        "mip_count": mip_count,
        "mip_chain_present": mip_count > 1 or not needs_chain,
        "expected_full_chain_mips": max(width, height).bit_length() if needs_chain else 1,
        "format": (
            four_cc.decode("ascii", "replace")
            if pf_flags & 0x4
            else f"RGB{bits}"
        ),
    }
