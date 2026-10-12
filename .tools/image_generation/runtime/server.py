#!/usr/bin/env python3
"""Provider-neutral stdio MCP server for image-generation routes."""

from __future__ import annotations

import argparse
import base64
import ctypes
import hashlib
import hmac
import ipaddress
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path
from typing import Any

MCP_VERSION = "2025-11-25"
KEYRING_SERVICE = "com.klimpaskov.hoi4-mod-setup"
CONFIG_PATH = Path(".hoi4-setup") / "image_generation.json"
MAX_MESSAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_BYTES = 32 * 1024 * 1024
MAX_REFERENCE_BYTES = 24 * 1024 * 1024
ALLOWED_REMOTE_HOSTS = {
    "openai_api": {"api.openai.com"},
    "gemini_api": {"generativelanguage.googleapis.com"},
    "fal_ai": {"mcp.fal.ai", "queue.fal.run"},
    "replicate": {"mcp.replicate.com", "api.replicate.com"},
    "black_forest_labs": {"mcp.bfl.ai", "api.bfl.ai"},
    "stability_ai": {"api.stability.ai"},
    "ideogram": {"mcp.ideogram.ai", "api.ideogram.ai"},
    "recraft": {"mcp.recraft.ai", "external.api.recraft.ai"},
    "leonardo": {"mcp.leonardo.ai", "cloud.leonardo.ai"},
    "adobe_firefly": {"run-workflow.adobe.io", "firefly-api.adobe.io"},
    "xai_grok": {"api.x.ai", "imgen.x.ai"},
    "together_ai": {"api.together.xyz", "api.together.ai"},
    "openrouter": {"mcp.openrouter.ai", "openrouter.ai"},
    "vertex_imagen": {"aiplatform.googleapis.com", "oauth2.googleapis.com"},
    "huggingface_inference": {"router.huggingface.co"},
}
ALLOWED_IMAGE_HOSTS = {
    "openai_api": {"api.openai.com"},
    "gemini_api": {"generativelanguage.googleapis.com"},
    "fal_ai": {"fal.media", "storage.googleapis.com"},
    "replicate": {"replicate.delivery"},
    "black_forest_labs": {"cdn.bfl.ai", "api.bfl.ai"},
    "stability_ai": {"api.stability.ai"},
    "ideogram": {"ideogram.ai", "cdn.ideogram.ai"},
    "recraft": {"recraft.ai", "img.recraft.ai"},
    "leonardo": {"leonardo.ai", "cdn.leonardo.ai"},
    "xai_grok": {"api.x.ai", "imgen.x.ai"},
    "together_ai": {"api.together.xyz", "api.together.ai"},
    "openrouter": {"openrouter.ai"},
    "vertex_imagen": {"aiplatform.googleapis.com"},
    "huggingface_inference": {"huggingface.co", "hf.co"},
}
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class ImageRouteError(RuntimeError):
    """A user-safe provider or project-route error."""


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _der_item(data: bytes, offset: int = 0) -> tuple[int, bytes, int]:
    if offset + 2 > len(data):
        raise ImageRouteError("The saved cloud credential has an invalid private key.")
    tag = data[offset]
    first = data[offset + 1]
    if first < 0x80:
        length, start = first, offset + 2
    else:
        size = first & 0x7F
        if size == 0 or size > 4 or offset + 2 + size > len(data):
            raise ImageRouteError("The saved cloud credential has an invalid private key.")
        length = int.from_bytes(data[offset + 2:offset + 2 + size], "big")
        start = offset + 2 + size
    end = start + length
    if end > len(data):
        raise ImageRouteError("The saved cloud credential has an invalid private key.")
    return tag, data[start:end], end


def _rsa_private_numbers(pem: str) -> tuple[int, int]:
    encoded = "".join(line.strip() for line in pem.splitlines() if not line.startswith("-----"))
    try:
        der = base64.b64decode(encoded, validate=True)
        tag, outer, _ = _der_item(der)
        if tag != 0x30:
            raise ValueError("not a sequence")
        offset = 0
        private_key = None
        while offset < len(outer):
            child_tag, child, offset = _der_item(outer, offset)
            if child_tag == 0x04:
                private_key = child
                break
        sequence = outer
        if private_key is not None:
            inner_tag, inner, _ = _der_item(private_key)
            if inner_tag == 0x30:
                sequence = inner
        integers = []
        offset = 0
        while offset < len(sequence):
            tag, value, offset = _der_item(sequence, offset)
            if tag == 0x02:
                integers.append(int.from_bytes(value, "big"))
        if len(integers) < 4:
            raise ValueError("private key fields missing")
        return integers[1], integers[3]
    except (ValueError, IndexError):
        raise ImageRouteError("The saved Google Cloud credential has an unsupported private key.") from None


def _rsa_sha256_sign(pem: str, value: bytes) -> bytes:
    modulus, private_exponent = _rsa_private_numbers(pem)
    digest_info = bytes.fromhex("3031300d060960864801650304020105000420") + hashlib.sha256(value).digest()
    size = (modulus.bit_length() + 7) // 8
    padding = size - len(digest_info) - 3
    if padding < 8:
        raise ImageRouteError("The saved Google Cloud private key is too small.")
    encoded = b"\x00\x01" + b"\xff" * padding + b"\x00" + digest_info
    return pow(int.from_bytes(encoded, "big"), private_exponent, modulus).to_bytes(size, "big")


def _image_dimension(value: Any, default: int = 1024) -> int:
    if value is None:
        value = default
    try:
        dimension = int(value)
    except (TypeError, ValueError):
        raise ImageRouteError("Image width and height must be whole numbers.") from None
    if dimension < 64 or dimension > 4096 or dimension % 8:
        raise ImageRouteError("Choose an image size supported by the selected model.")
    return dimension


def _safe_url(provider_id: str, raw_url: str, *, allow_loopback: bool = False) -> str:
    if not isinstance(raw_url, str):
        raise ImageRouteError("The provider address is missing.")
    parsed = urllib.parse.urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme == "http" and allow_loopback and host in LOOPBACK_HOSTS:
        return raw_url
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment:
        raise ImageRouteError("The provider address is not a verified HTTPS route.")
    try:
        if parsed.port not in (None, 443):
            raise ImageRouteError("The provider address uses an unapproved port.")
    except ValueError:
        raise ImageRouteError("The provider address is invalid.") from None
    allowed = ALLOWED_REMOTE_HOSTS.get(provider_id, set())
    if host not in allowed:
        if provider_id == "vertex_imagen" and (host == "aiplatform.googleapis.com" or host.endswith("-aiplatform.googleapis.com")):
            return raw_url
        if provider_id == "aws_bedrock" and re.fullmatch(r"bedrock-runtime\.[a-z]{2}-[a-z]+-\d\.amazonaws\.com", host):
            return raw_url
        raise ImageRouteError("The provider address is outside its verified host list.")
    return raw_url


def _safe_foundry_base(raw_url: str) -> str:
    parsed = urllib.parse.urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    try:
        port = parsed.port
    except ValueError:
        raise ImageRouteError("Enter the HTTPS endpoint for your Microsoft Foundry resource.") from None
    if (
        parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.query or parsed.fragment
        or parsed.path not in ("", "/") or not re.fullmatch(r"[a-z0-9-]+\.services\.ai\.azure\.com", host)
        or port not in (None, 443)
    ):
        raise ImageRouteError("Enter the HTTPS endpoint for your Microsoft Foundry resource.")
    return raw_url.rstrip("/")


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for _ in range(12):
        marker = current / CONFIG_PATH
        if marker.is_file() and not marker.is_symlink():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise ImageRouteError("Open the mod project as the coding client's workspace, then reconnect its image server.")


def canonical_provider(provider_id: str) -> dict:
    catalog_path = Path(__file__).with_name("provider_catalog.json")
    try:
        if catalog_path.stat().st_size > 2 * 1024 * 1024:
            raise OSError("catalog too large")
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        provider = next(item for item in catalog["providers"] if item["id"] == provider_id)
        return provider
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, StopIteration, TypeError):
        raise ImageRouteError("The trusted image-provider catalog is missing or invalid. Repair the setup installation.") from None


def load_provider_config(project_root: Path, provider_id: str, config_path: Path = CONFIG_PATH) -> tuple[dict, dict]:
    root = project_root.resolve()
    if config_path.is_absolute() or ".." in config_path.parts:
        raise ImageRouteError("The image-provider settings path is invalid.")
    path = root / config_path
    current = root
    for part in config_path.parts:
        current = current / part
        if current.is_symlink():
            raise ImageRouteError("The managed image-provider settings cannot use symbolic links.")
    if not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise ImageRouteError("The managed image-provider settings are missing or unsafe. Run setup repair.")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ImageRouteError("The managed image-provider settings could not be read. Run setup repair.") from None
    providers = document.get("providers")
    if not isinstance(providers, dict) or provider_id not in providers:
        raise ImageRouteError("This image provider is not selected for the project. Use setup update to change it.")
    config = providers[provider_id]
    trusted = canonical_provider(provider_id)
    route = config.get("route") if isinstance(config, dict) else None
    if (
        not isinstance(config, dict) or config.get("id") != provider_id
        or route != trusted.get("route") or not isinstance(route, dict)
        or route.get("kind") != "stdio_adapter"
        or config.get("capabilities") != trusted.get("capabilities")
        or config.get("display_name") != trusted.get("display_name")
    ):
        raise ImageRouteError("The provider settings do not match the selected image route.")
    allowed_fields = {field["id"] for field in route.get("credential_fields", [])}
    refs = config.get("credential_references", {})
    if not isinstance(refs, dict) or set(refs) - allowed_fields:
        raise ImageRouteError("The provider credential references do not match the selected route.")
    for field_id, reference in refs.items():
        expected = f"credential://image_generation_api_key/{provider_id}_{field_id}"
        if reference != expected:
            raise ImageRouteError("The provider credential reference is outside its own secure account.")
    settings = config.get("settings", {})
    if not isinstance(settings, dict):
        raise ImageRouteError("The provider settings have an invalid format.")
    protocol = route.get("api_protocol")
    if protocol in {"comfyui", "automatic1111"}:
        if set(settings) - {"server_url", "checkpoint"}:
            raise ImageRouteError("The local image-server settings include an unsupported field.")
        server_url = settings.get("server_url")
        if server_url is not None:
            _safe_url(provider_id, server_url, allow_loopback=True)
        if "checkpoint" in settings and not isinstance(settings["checkpoint"], str):
            raise ImageRouteError("The local model name is invalid.")
    elif protocol == "microsoft_foundry":
        if set(settings) - {"deployment_name"}:
            raise ImageRouteError("The Microsoft Foundry settings include an unsupported field.")
        if "deployment_name" in settings and (not isinstance(settings["deployment_name"], str) or len(settings["deployment_name"]) > 128):
            raise ImageRouteError("The Microsoft Foundry deployment name is invalid.")
    elif protocol == "aws_bedrock":
        if set(settings) - {"region", "model"}:
            raise ImageRouteError("The AWS settings include an unsupported field.")
        region = settings.get("region", "us-west-2")
        if not isinstance(region, str) or not re.fullmatch(r"[a-z]{2}-[a-z]+-\d", region):
            raise ImageRouteError("Choose a valid AWS region in image provider settings.")
        if "model" in settings and settings["model"] not in trusted.get("route", {}).get("supported_models", []):
            raise ImageRouteError("Choose an AWS image model listed in the setup provider details.")
    elif route.get("supported_models"):
        if set(settings) - {"model"}:
            raise ImageRouteError("The image-provider settings include an unsupported field.")
        if "model" in settings and settings["model"] not in route["supported_models"]:
            raise ImageRouteError("Choose an image model listed in the setup provider details.")
    elif settings:
        raise ImageRouteError("The selected provider does not accept project-local settings.")
    return document, config


def _windows_credential(reference: str) -> str | None:
    from ctypes import wintypes

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

    class CREDENTIALW(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR), ("LastWritten", FILETIME), ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)), ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR),
        ]

    # keyring 3.x uses this target-name format for Windows Generic Credentials.
    target = keyring_target_name(reference)
    pointer = ctypes.POINTER(CREDENTIALW)()
    advapi32 = ctypes.WinDLL("Advapi32.dll")
    advapi32.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(CREDENTIALW))]
    advapi32.CredReadW.restype = wintypes.BOOL
    if not advapi32.CredReadW(target, 1, 0, ctypes.byref(pointer)):
        return None
    try:
        credential = pointer.contents
        blob = ctypes.string_at(credential.CredentialBlob, credential.CredentialBlobSize)
        return blob.decode("utf-16-le").rstrip("\x00")
    finally:
        advapi32.CredFree.argtypes = [ctypes.c_void_p]
        advapi32.CredFree(pointer)


def _macos_credential(reference: str) -> str | None:
    try:
        result = subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-s", KEYRING_SERVICE, "-a", reference, "-w"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            check=False, timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "replace").rstrip("\r\n")


def keyring_target_name(reference: str) -> str:
    """Match the Windows Generic Credential target used by the Rust keyring adapter."""
    return f"{reference}.{KEYRING_SERVICE}"


def read_credential(reference: str) -> str | None:
    if not isinstance(reference, str) or not re.fullmatch(r"credential://image_generation_api_key/[a-z0-9_-]{1,64}", reference):
        return None
    if os.name == "nt":
        return _windows_credential(reference)
    if sys.platform == "darwin":
        return _macos_credential(reference)
    return None


def _png_parts(data: bytes) -> tuple[tuple[int, int, int, int, int], dict[bytes, bytes]] | None:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 45:
        return None
    offset = 8
    header = None
    chunks: dict[bytes, bytearray] = {b"IDAT": bytearray()}
    ended = False
    while offset + 12 <= len(data):
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 8 + size
        if end + 4 > len(data):
            return None
        value = data[offset + 8:end]
        expected_crc = struct.unpack(">I", data[end:end + 4])[0]
        if zlib.crc32(kind + value) & 0xFFFFFFFF != expected_crc:
            return None
        if kind == b"IHDR":
            if header is not None or size != 13 or offset != 8:
                return None
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(">IIBBBBB", value)
            header = (width, height, bit_depth, color_type, interlace)
        elif kind in {b"PLTE", b"tRNS"}:
            chunks[kind] = bytearray(value)
        elif kind == b"IDAT":
            chunks[b"IDAT"].extend(value)
            if len(chunks[b"IDAT"]) > MAX_IMAGE_BYTES:
                return None
        elif kind == b"IEND":
            if size != 0:
                return None
            ended = True
            break
        offset = end + 4
    if not ended or header is None or not chunks[b"IDAT"]:
        return None
    width, height, bit_depth, color_type, interlace = header
    valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
    if (
        width <= 0 or height <= 0 or color_type not in valid_depths
        or bit_depth not in valid_depths[color_type] or interlace not in (0, 1)
        or (color_type == 3 and (not chunks.get(b"PLTE") or len(chunks[b"PLTE"]) % 3 or len(chunks[b"PLTE"]) > 768))
    ):
        return None
    return header, {kind: bytes(value) for kind, value in chunks.items()}


def png_has_alpha(data: bytes) -> bool:
    parts = _png_parts(data)
    if parts is None:
        return False
    (_width, _height, _bit_depth, color_type, _interlace), chunks = parts
    return color_type in (4, 6) or bool(chunks.get(b"tRNS"))


def png_has_transparent_pixels(data: bytes) -> bool | None:
    """Return whether decoded pixels contain non-opaque alpha; None if unsupported."""
    parts = _png_parts(data)
    if parts is None:
        return None
    (width, height, bit_depth, color_type, interlace), chunks = parts
    if interlace != 0:
        return None
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if channels is None or bit_depth not in {1, 2, 4, 8, 16}:
        return None
    if color_type in {2, 4, 6} and bit_depth < 8:
        return None
    row_bytes = (width * channels * bit_depth + 7) // 8
    expected = (row_bytes + 1) * height
    if width <= 0 or height <= 0 or expected > 128 * 1024 * 1024:
        return None
    decompressor = zlib.decompressobj()
    try:
        decoded = decompressor.decompress(chunks[b"IDAT"], expected + 1)
        if len(decoded) > expected or decompressor.unconsumed_tail or not decompressor.eof:
            return None
        decoded += decompressor.flush()
    except zlib.error:
        return None
    if len(decoded) != expected:
        return None

    bytes_per_pixel = max(1, (channels * bit_depth + 7) // 8)
    previous = bytearray(row_bytes)
    position = 0
    transparent_sample = chunks.get(b"tRNS", b"")
    palette_alpha = chunks.get(b"tRNS", b"")
    palette = chunks.get(b"PLTE", b"")
    max_sample = (1 << bit_depth) - 1

    for _row in range(height):
        filter_type = decoded[position]
        source = decoded[position + 1:position + 1 + row_bytes]
        position += row_bytes + 1
        current = bytearray(row_bytes)
        for index, sample in enumerate(source):
            left = current[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            above = previous[index]
            upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            elif filter_type == 4:
                estimate = left + above - upper_left
                distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
                predictor = left if distances[0] <= distances[1] and distances[0] <= distances[2] else above if distances[1] <= distances[2] else upper_left
            else:
                return None
            current[index] = (sample + predictor) & 0xFF

        if color_type == 6:
            step = channels * (bit_depth // 8)
            alpha_offset = 3 * (bit_depth // 8)
            sample_bytes = bit_depth // 8
            for pixel in range(width):
                start = pixel * step + alpha_offset
                alpha = int.from_bytes(current[start:start + sample_bytes], "big")
                if alpha < max_sample:
                    return True
        elif color_type == 4:
            step = channels * (bit_depth // 8)
            sample_bytes = bit_depth // 8
            for pixel in range(width):
                start = pixel * step + sample_bytes
                alpha = int.from_bytes(current[start:start + sample_bytes], "big")
                if alpha < max_sample:
                    return True
        elif color_type == 3:
            if not palette or len(palette) % 3:
                return None
            pixels_per_byte = 8 // bit_depth
            mask = (1 << bit_depth) - 1
            for pixel in range(width):
                value = current[pixel // pixels_per_byte]
                shift = 8 - bit_depth * ((pixel % pixels_per_byte) + 1)
                palette_index = (value >> shift) & mask
                if palette_index < len(palette_alpha) and palette_alpha[palette_index] < 255:
                    return True
        elif color_type in {0, 2} and transparent_sample:
            bytes_per_sample = bit_depth // 8
            samples_per_pixel = channels
            values = [int.from_bytes(transparent_sample[i:i + 2], "big") for i in range(0, len(transparent_sample), 2)]
            if len(values) == samples_per_pixel:
                for pixel in range(width):
                    start = pixel * samples_per_pixel * bytes_per_sample
                    samples = [int.from_bytes(current[start + i * bytes_per_sample:start + (i + 1) * bytes_per_sample], "big") for i in range(samples_per_pixel)]
                    if samples == values:
                        return True
        previous = current
    return False


def image_dimensions(name: str, data: bytes) -> tuple[int, int] | None:
    mime = image_mime(name)
    if mime == "image/png":
        parts = _png_parts(data)
        return (parts[0][0], parts[0][1]) if parts else None
    if mime == "image/jpeg" and data.startswith(b"\xff\xd8\xff"):
        offset = 2
        start_of_frame = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while offset + 4 <= len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            while offset < len(data) and data[offset] == 0xFF:
                offset += 1
            if offset >= len(data):
                return None
            marker = data[offset]
            offset += 1
            if marker in {0xD9, 0xDA}:
                break
            if marker == 0x01 or 0xD0 <= marker <= 0xD8:
                continue
            if offset + 2 > len(data):
                return None
            length = int.from_bytes(data[offset:offset + 2], "big")
            if length < 2 or offset + length > len(data):
                return None
            if marker in start_of_frame and length >= 7:
                height = int.from_bytes(data[offset + 3:offset + 5], "big")
                width = int.from_bytes(data[offset + 5:offset + 7], "big")
                return (width, height) if width and height else None
            offset += length
        return None
    if mime == "image/webp" and len(data) >= 30 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X" and len(data) >= 30:
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return width, height
        if kind == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            width = int.from_bytes(data[26:28], "little") & 0x3FFF
            height = int.from_bytes(data[28:30], "little") & 0x3FFF
            return (width, height) if width and height else None
        if kind == b"VP8L" and len(data) >= 25 and data[20] == 0x2F:
            b0, b1, b2, b3 = data[21:25]
            width = 1 + (((b1 & 0x3F) << 8) | b0)
            height = 1 + ((b1 >> 6) | (b2 << 2) | ((b3 & 0xF) << 10))
            return width, height
    return None


def image_mime(name: str) -> str:
    suffix = Path(name).suffix.lower()
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(suffix, "application/octet-stream")


def validate_reference_image(name: str, data: bytes) -> str:
    mime = image_mime(name)
    if mime == "image/png":
        valid = _png_parts(data) is not None
    elif mime == "image/jpeg":
        valid = data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9")
    elif mime == "image/webp":
        valid = data.startswith(b"RIFF") and data[8:12] == b"WEBP" and len(data) >= 16 and int.from_bytes(data[4:8], "little") + 8 == len(data)
    else:
        valid = False
    if not valid:
        raise ImageRouteError("The selected reference file is not a valid PNG, JPEG, or WebP image.")
    return mime


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _safe_image_download_url(provider_id: str, raw_url: str) -> str:
    parsed = urllib.parse.urlparse(raw_url)
    host = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError:
        raise ImageRouteError("The provider returned an invalid image address.") from None
    try:
        address = ipaddress.ip_address(host.strip("[]")) if host else None
    except ValueError:
        address = None
    if (
        parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment
        or port not in (None, 443) or (address is not None and not address.is_global)
    ):
        raise ImageRouteError("The provider returned an image address outside its verified image host.")
    allowlist = ALLOWED_IMAGE_HOSTS.get(provider_id, set())
    if not any(host == allowed or host.endswith("." + allowed) for allowed in allowlist):
        raise ImageRouteError("The provider returned an image address outside its verified image host.")
    if provider_id == "fal_ai" and host == "storage.googleapis.com" and not parsed.path.startswith("/falserverless/"):
        raise ImageRouteError("The provider returned an image address outside its verified image host.")
    return raw_url


def encode_multipart(fields: dict[str, str], files: list[tuple[str, str, str, bytes]]) -> tuple[bytes, str]:
    boundary = "hoi4" + hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:24]
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.extend([f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n".encode(), value.encode(), b"\r\n"])
    for field, name, mime, data in files:
        header = f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; filename=\"{Path(name).name}\"\r\nContent-Type: {mime}\r\n\r\n"
        parts.extend([header.encode(), data, b"\r\n"])
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), boundary


def _sse_json(body: bytes) -> list[dict]:
    messages = []
    normalized = body.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")
    for block in normalized.split("\n\n"):
        data = "\n".join(line[5:].strip() for line in block.splitlines() if line.startswith("data:"))
        if data and data != "[DONE]":
            try:
                messages.append(json.loads(data))
            except json.JSONDecodeError:
                continue
    return messages


def _mcp_result(request_id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _mcp_error(request_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_schema(name: str, provider: dict | None = None) -> dict:
    common = {
        "prompt": {"type": "string", "minLength": 1},
        "out": {"type": "string"},
        "width": {"type": "integer", "minimum": 64},
        "height": {"type": "integer", "minimum": 64},
        "transparent_background": {"type": "boolean"},
        "reference_images": {"type": "array", "items": {"type": "string"}},
    }
    capabilities = provider.get("capabilities", {}) if provider else {}
    accepts_dimensions = bool(capabilities.get("size_limits", {}).get("accepts_dimensions"))
    if not accepts_dimensions:
        common.pop("width", None)
        common.pop("height", None)
    if not capabilities.get("reference_images", {}).get("supported", False):
        common.pop("reference_images", None)
    if not capabilities.get("transparent_background", {}).get("native", False):
        common.pop("transparent_background", None)
    if provider:
        result_format = provider.get("route", {}).get("result_format", "png")
        descriptions = {
            "png": "A project-relative path ending in .png. The server keeps existing images and reports whether this PNG has alpha.",
            "jpeg": "A project-relative path ending in .jpg or .jpeg. This route returns JPEG and cannot include an alpha channel.",
            "model_defined": "A project-relative path whose extension matches the selected model's image format.",
            "manual": "A project-relative output path.",
        }
        common["out"]["description"] = descriptions.get(result_format, descriptions["model_defined"])
    if name == "edit_image":
        return {"type": "object", "required": ["prompt", "image", "out"], "properties": {**common, "image": {"type": "string"}}}
    if name == "remove_background":
        return {"type": "object", "required": ["image", "out"], "properties": {"image": {"type": "string"}, "out": {"type": "string"}}}
    if name == "image_auth_status":
        return {"type": "object", "properties": {}}
    return {"type": "object", "required": ["prompt", "out"], "properties": common}


def _local_tools(provider: dict) -> list[dict]:
    route = provider["route"]
    caps = provider.get("capabilities", {})
    names = route.get("tool_names", {})
    mapping = [("auth_status", "image_auth_status")]
    if names.get("generate"):
        mapping.append(("generate", names["generate"]))
    if names.get("edit") and caps.get("image_edits"):
        mapping.append(("edit", names["edit"]))
    if names.get("background_removal") and caps.get("background_removal"):
        mapping.append(("background_removal", names["background_removal"]))
    tools = []
    for role, name in mapping:
        tools.append({"name": name, "description": f"{provider.get('display_name', 'Selected provider')}: {role.replace('_', ' ')} using the selected image route.", "inputSchema": _tool_schema(name, provider)})
    return tools


class Server:
    def __init__(self, provider_id: str, project_root: Path, config_path: Path = CONFIG_PATH):
        self.provider_id = provider_id
        self.project_root = project_root.resolve()
        self.document, self.provider = load_provider_config(self.project_root, provider_id, config_path)
        self.route = self.provider["route"]
        refs = self.provider.get("credential_references", {})
        self.secrets = {key: value for key, reference in refs.items() if (value := read_credential(reference))}
        self.remote_session_id: str | None = None

    def safe_error(self, error: Exception) -> str:
        message = str(error)
        for secret in self.secrets.values():
            if secret:
                message = message.replace(secret, "[hidden]")
        message = re.sub(r"(?i)(?:api[_-]?key|token|client_secret|authorization)\s*[:=]\s*\S+", "credential details hidden", message)
        return message[:600]

    def redact_remote(self, value: Any) -> Any:
        if isinstance(value, str):
            for secret in self.secrets.values():
                if secret:
                    value = value.replace(secret, "[hidden]")
            return value
        if isinstance(value, list):
            return [self.redact_remote(item) for item in value]
        if isinstance(value, dict):
            return {key: self.redact_remote(item) for key, item in value.items()}
        return value

    def run(self) -> int:
        for line in sys.stdin.buffer:
            if len(line) > MAX_MESSAGE_BYTES:
                continue
            message: Any = None
            try:
                message = json.loads(line)
                if not isinstance(message, dict):
                    raise ValueError("invalid JSON-RPC envelope")
                response = self.handle(message)
            except Exception as error:
                request_id = message.get("id") if isinstance(message, dict) else None
                if isinstance(message, dict) and "id" not in message:
                    response = None
                else:
                    response = _mcp_error(request_id, -32600 if isinstance(error, ValueError) else -32000, self.safe_error(error))
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
                sys.stdout.flush()
        return 0

    def handle(self, message: dict) -> dict | None:
        method = message.get("method")
        request_id = message.get("id")
        if not isinstance(method, str):
            return _mcp_error(request_id, -32600, "The request does not contain a valid method.") if request_id is not None else None
        if method.startswith("notifications/") and request_id is None:
            return None
        if self.route.get("api_protocol") == "mcp_proxy":
            return self.remote_request(message)
        if method == "initialize":
            params = message.get("params", {})
            return _mcp_result(request_id, {
                "protocolVersion": params.get("protocolVersion", MCP_VERSION),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": self.route.get("server_id", "hoi4-image-generation"), "version": "1.0.0"},
            })
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return _mcp_result(request_id, {})
        if method == "tools/list":
            return _mcp_result(request_id, {"tools": _local_tools(self.provider)})
        if method == "tools/call":
            params = message.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(arguments, dict):
                return _mcp_result(request_id, {"content": [{"type": "text", "text": "Tool arguments must be an object."}], "isError": True})
            try:
                result = self.call_tool(name, arguments)
                return _mcp_result(request_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]})
            except Exception as error:
                return _mcp_result(request_id, {"content": [{"type": "text", "text": self.safe_error(error)}], "isError": True})
        return _mcp_error(request_id, -32601, "The image server does not support this method.") if request_id is not None else None

    def remote_request(self, message: dict) -> dict | None:
        url = self.route.get("api_base_url")
        if not isinstance(url, str):
            raise ImageRouteError("The selected provider MCP address is missing.")
        _safe_url(self.provider_id, url)
        headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json", "MCP-Protocol-Version": MCP_VERSION}
        for field in self.route.get("credential_fields", []):
            value = self.secrets.get(field["id"])
            if value:
                headers[field["header"]] = field.get("prefix", "") + value
        if self.remote_session_id:
            headers["Mcp-Session-Id"] = self.remote_session_id
        request_id = message.get("id")
        request = urllib.request.Request(url, data=json.dumps(message).encode("utf-8"), headers=headers, method="POST")
        try:
            opener = urllib.request.build_opener(_NoRedirect())
            with opener.open(request, timeout=180) as response:
                self.remote_session_id = response.headers.get("Mcp-Session-Id", self.remote_session_id)
                content_type = response.headers.get("Content-Type", "")
                body = response.read(MAX_MESSAGE_BYTES + 1)
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ImageRouteError("The provider MCP could not be reached. Check the provider account and try again.") from None
        if len(body) > MAX_MESSAGE_BYTES:
            raise ImageRouteError("The provider MCP returned a response that was too large.")
        if request_id is None:
            return None
        messages = _sse_json(body) if "text/event-stream" in content_type else []
        if not messages and body:
            try:
                messages = [json.loads(body)]
            except json.JSONDecodeError:
                raise ImageRouteError("The provider MCP returned an unreadable response.") from None
        for item in messages:
            if item.get("id") == request_id:
                return self.redact_remote(item)
        raise ImageRouteError("The provider MCP did not answer this request.")

    def call_tool(self, name: str, args: dict) -> dict:
        route = self.route
        if name == route.get("tool_names", {}).get("auth_status"):
            fields = route.get("credential_fields", [])
            if route.get("api_protocol") in {"comfyui", "automatic1111"}:
                settings = self.provider.get("settings", {})
                default_url = "http://127.0.0.1:8188" if route["api_protocol"] == "comfyui" else "http://127.0.0.1:7860"
                base = settings.get("server_url", default_url).rstrip("/")
                probe = "/system_stats" if route["api_protocol"] == "comfyui" else "/sdapi/v1/options"
                try:
                    self._request_json(base + probe, "GET", {}, loopback=True)
                    return {"provider": self.provider_id, "status": "ready"}
                except Exception:
                    return {"provider": self.provider_id, "status": "local_server_unavailable"}
            status = "ready" if not fields or all(self.secrets.get(item["id"]) for item in fields) else "needs_credentials"
            return {"provider": self.provider_id, "status": status}
        if name == route.get("tool_names", {}).get("background_removal"):
            if not self.provider.get("capabilities", {}).get("background_removal"):
                raise ImageRouteError("This provider does not have a background-removal tool.")
            return self.remove_background(args)
        if name == route.get("tool_names", {}).get("edit"):
            if not self.provider.get("capabilities", {}).get("image_edits"):
                raise ImageRouteError("This provider route does not support image edits.")
            args["image"] = args.get("image") or (args.get("reference_images") or [None])[0]
            if not args.get("image"):
                raise ImageRouteError("Choose a reference image path for the image edit.")
            args["reference_images"] = [args["image"]]
            args["_hoi4_edit_request"] = True
        if name not in {route.get("tool_names", {}).get("generate"), route.get("tool_names", {}).get("edit")}:
            raise ImageRouteError("This tool is not available for the selected provider.")
        return self.generate_image(args)

    def require_secret(self, field_id: str = "api_key") -> str:
        secret = self.secrets.get(field_id)
        if not secret:
            raise ImageRouteError("Save the provider key in the setup app before using this route.")
        return secret

    def selected_model(self, fallback: str | None = None) -> str | None:
        return self.provider.get("settings", {}).get("model") or self.route.get("default_model") or fallback

    def read_reference(self, relative: str) -> tuple[str, bytes]:
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ImageRouteError("Reference images must be inside the current mod project.")
        candidate = self.project_root / relative
        current = self.project_root
        for part in Path(relative).parts:
            current = current / part
            if current.is_symlink():
                raise ImageRouteError("Reference images cannot use symbolic links.")
        resolved = candidate.resolve()
        if self.project_root not in resolved.parents or not resolved.is_file():
            raise ImageRouteError("The reference image was not found inside the mod project.")
        data = resolved.read_bytes()
        if len(data) > MAX_REFERENCE_BYTES:
            raise ImageRouteError("The reference image is larger than this route allows.")
        if image_mime(resolved.name) == "application/octet-stream":
            raise ImageRouteError("Use a PNG, JPEG, or WebP reference image.")
        validate_reference_image(resolved.name, data)
        return resolved.name, data

    def save_output(self, output_path: str, data: bytes) -> dict:
        if not isinstance(output_path, str) or not output_path or Path(output_path).is_absolute() or ".." in Path(output_path).parts:
            raise ImageRouteError("Choose an output path inside the current mod project.")
        if not data or len(data) > MAX_IMAGE_BYTES:
            raise ImageRouteError("The provider returned an empty or oversized image.")
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            image_format, valid_suffix = "png", {".png"}
            if _png_parts(data) is None:
                raise ImageRouteError("The provider returned a damaged PNG image.")
            alpha_channel = png_has_alpha(data)
            transparent_pixels = png_has_transparent_pixels(data) is True
        elif data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9"):
            image_format, valid_suffix = "jpeg", {".jpg", ".jpeg"}
            alpha_channel = False
            transparent_pixels = False
        elif data.startswith(b"RIFF") and data[8:12] == b"WEBP" and len(data) >= 16 and int.from_bytes(data[4:8], "little") + 8 == len(data):
            image_format, valid_suffix = "webp", {".webp"}
            alpha_channel = False
            transparent_pixels = False
        else:
            raise ImageRouteError("The provider returned an unsupported or invalid image format.")
        if Path(output_path).suffix.lower() not in valid_suffix:
            raise ImageRouteError(f"This provider returned {image_format.upper()} data; choose a matching output file extension.")
        destination = self.project_root / output_path
        current = self.project_root
        for part in Path(output_path).parts[:-1]:
            current = current / part
            if current.is_symlink():
                raise ImageRouteError("Output folders cannot use symbolic links.")
            current.mkdir(exist_ok=True)
        if self.project_root not in destination.resolve().parents:
            raise ImageRouteError("The output path is outside the mod project.")
        if destination.exists():
            raise ImageRouteError("The output file already exists; choose a new name to preserve existing art.")
        temporary_path = None
        try:
            fd, temporary_path = tempfile.mkstemp(prefix=".imagegen-", suffix=".tmp", dir=destination.parent)
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.rename(temporary_path, destination)
            temporary_path = None
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)
        return {"path": Path(output_path).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "format": image_format, "alpha": alpha_channel, "transparent_pixels": transparent_pixels, "bytes": len(data)}

    def save_transparent_output(self, output_path: str, data: bytes) -> dict:
        if not png_has_alpha(data) or png_has_transparent_pixels(data) is not True:
            raise ImageRouteError("The background-removal route returned no verifiable transparent pixels.")
        return self.save_output(output_path, data)

    def _request_bytes(self, url: str, method: str, headers: dict[str, str], body: bytes | None = None,
                       *, loopback: bool = False) -> bytes:
        if self.provider_id == "microsoft_foundry":
            base = _safe_foundry_base(self.require_secret("resource_url"))
            parsed_url = urllib.parse.urlparse(url)
            parsed_base = urllib.parse.urlparse(base)
            if (parsed_url.scheme, parsed_url.hostname, parsed_url.port) != (parsed_base.scheme, parsed_base.hostname, parsed_base.port):
                raise ImageRouteError("The Microsoft Foundry request does not match its saved resource endpoint.")
        else:
            _safe_url(self.provider_id, url, allow_loopback=loopback)
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            # Provider APIs receive credentials in headers. Never let urllib
            # follow a redirect after validating only the first host.
            opener = urllib.request.build_opener(_NoRedirect())
            with opener.open(request, timeout=180) as response:
                value = response.read(MAX_IMAGE_BYTES + 1)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            raise ImageRouteError("The provider request failed. Check the account, usage limit, and server status.") from None
        if len(value) > MAX_IMAGE_BYTES:
            raise ImageRouteError("The provider response exceeded the image-size limit.")
        return value

    def _request_json(self, url: str, method: str, headers: dict[str, str], payload: dict | None = None,
                      *, loopback: bool = False) -> dict:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        response = self._request_bytes(url, method, headers, body, loopback=loopback)
        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            raise ImageRouteError("The provider returned an unreadable response.") from None
        if not isinstance(result, dict):
            raise ImageRouteError("The provider returned an unexpected response.")
        return result

    def _image_from_response(self, response: dict) -> bytes:
        candidates = []
        values = response.get("data")
        if isinstance(values, list):
            candidates.extend(values)
        values = response.get("images")
        if isinstance(values, list):
            candidates.extend(values)
        values = response.get("output")
        if isinstance(values, list):
            candidates.extend(values)
        value = response.get("image")
        if isinstance(value, (dict, str)):
            candidates.append(value)
        candidates.append(response)
        for item in candidates:
            if isinstance(item, str):
                try:
                    decoded = base64.b64decode(item, validate=True)
                    if decoded.startswith(b"\x89PNG\r\n\x1a\n"):
                        return decoded
                except ValueError:
                    pass
                candidate = {"url": item}
            elif isinstance(item, dict):
                candidate = item
            else:
                continue
            encoded = candidate.get("b64_json") or candidate.get("b64") or candidate.get("base64")
            if isinstance(encoded, str):
                try:
                    return base64.b64decode(encoded, validate=True)
                except ValueError:
                    continue
            url = candidate.get("url") or candidate.get("image_url")
            if isinstance(url, str) and urllib.parse.urlparse(url).scheme == "https":
                url = _safe_image_download_url(self.provider_id, url)
                request = urllib.request.Request(url, headers={"User-Agent": "hoi4-image-provider/1.0", "Accept": "image/png,image/*;q=0.9"})
                try:
                    opener = urllib.request.build_opener(_NoRedirect())
                    with opener.open(request, timeout=60) as result:
                        data = result.read(MAX_IMAGE_BYTES + 1)
                except (urllib.error.URLError, TimeoutError, OSError):
                    raise ImageRouteError("The generated image could not be downloaded.") from None
                if len(data) <= MAX_IMAGE_BYTES:
                    return data
        raise ImageRouteError("The provider response did not contain a supported image.")

    def generate_image(self, args: dict) -> dict:
        protocol = self.route.get("api_protocol")
        prompt = args.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 12000:
            raise ImageRouteError("Add a clear prompt before generating an image.")
        if "model" in args:
            raise ImageRouteError("Choose the image model in HOI4 Mod Setup instead of the image prompt.")
        is_edit = bool(args.pop("_hoi4_edit_request", False))
        capabilities = self.provider.get("capabilities", {})
        if is_edit and not capabilities.get("image_edits"):
            raise ImageRouteError("This provider route does not support image edits.")
        if not is_edit and args.get("image"):
            raise ImageRouteError("Pass source images to edit_image or through the reference_images field.")
        if args.get("transparent_background") and not capabilities.get("transparent_background", {}).get("native"):
            raise ImageRouteError("This provider route does not offer native transparency. Use background removal or another selected provider.")
        references = args.get("reference_images", [])
        if references:
            if not isinstance(references, list) or any(not isinstance(reference, str) for reference in references):
                raise ImageRouteError("Reference images must be a list of project-relative image paths.")
            reference_capabilities = capabilities.get("reference_images", {})
            if not reference_capabilities.get("supported"):
                raise ImageRouteError("This provider route does not accept reference images.")
            maximum = reference_capabilities.get("max_count")
            if maximum and len(references) > maximum:
                raise ImageRouteError(f"This provider route accepts up to {maximum} reference images.")
            total_reference_bytes = 0
            for reference in references:
                _name, reference_data = self.read_reference(reference)
                total_reference_bytes += len(reference_data)
            if total_reference_bytes > 64 * 1024 * 1024:
                raise ImageRouteError("The combined reference images exceed the provider adapter limit.")
        self._validate_size(args)
        if protocol in {"openai_images", "openai_compatible", "microsoft_foundry", "huggingface_router"}:
            return self._generate_openai_compatible(args)
        if protocol == "huggingface_inference":
            return self._generate_huggingface(args)
        if protocol == "gemini_generate_content":
            return self._generate_gemini(args)
        if protocol == "stability":
            return self._generate_stability(args)
        if protocol == "automatic1111":
            return self._generate_automatic1111(args)
        if protocol == "fal_queue":
            return self._generate_fal(args)
        if protocol == "replicate_predictions":
            return self._generate_replicate(args)
        if protocol == "bfl":
            return self._generate_bfl(args)
        if protocol == "ideogram":
            return self._generate_ideogram(args)
        if protocol == "recraft":
            return self._generate_recraft(args)
        if protocol == "leonardo":
            return self._generate_leonardo(args)
        if protocol == "adobe_firefly":
            return self._generate_adobe(args)
        if protocol == "openrouter_images":
            return self._generate_openrouter(args)
        if protocol == "together_images":
            return self._generate_together(args)
        if protocol == "xai_imagine":
            return self._generate_xai(args)
        if protocol == "comfyui":
            return self._generate_comfyui(args)
        if protocol == "vertex_ai":
            return self._generate_vertex(args)
        if protocol == "aws_bedrock":
            return self._generate_bedrock(args)
        raise ImageRouteError("The selected provider route is not supported by this MCP server.")

    def _validate_size(self, args: dict) -> None:
        caps = self.provider.get("capabilities", {}).get("size_limits", {})
        if not caps.get("accepts_dimensions") and ("width" in args or "height" in args):
            raise ImageRouteError("The selected image route chooses its own output dimensions; remove width and height.")
        if not caps.get("accepts_dimensions"):
            return
        width = _image_dimension(args.get("width", 1024))
        height = _image_dimension(args.get("height", 1024))
        max_width = caps.get("maximum_width_px")
        max_height = caps.get("maximum_height_px")
        max_pixels = caps.get("maximum_pixels")
        if max_width and width > max_width or max_height and height > max_height:
            raise ImageRouteError("The requested image size exceeds the selected model's documented limit.")
        if max_pixels and width * height > max_pixels:
            raise ImageRouteError("The requested image size exceeds the selected model's total pixel limit.")

    def _generate_openai_compatible(self, args: dict) -> dict:
        protocol = self.route["api_protocol"]
        if self.provider_id == "microsoft_foundry":
            base = _safe_foundry_base(self.require_secret("resource_url"))
            model = self.provider.get("settings", {}).get("deployment_name")
            if not isinstance(model, str) or not model.strip():
                raise ImageRouteError("Choose the deployed Microsoft Foundry model name in image provider settings.")
            headers = {"api-key": self.require_secret("api_key"), "Content-Type": "application/json"}
            refs = [args["image"]] if args.get("image") else args.get("reference_images", [])
            if refs:
                if len(refs) > 5:
                    raise ImageRouteError("Microsoft Foundry accepts up to five reference images.")
                files = []
                for path in refs:
                    name, data = self.read_reference(path)
                    files.append(("image", name, image_mime(name), data))
                body, boundary = encode_multipart({"model": model, "prompt": args["prompt"]}, files)
                headers.pop("Content-Type")
                headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
                endpoint = base + "/mai/v1/images/edits"
            else:
                payload = {"model": model, "prompt": args["prompt"]}
                if args.get("width") and args.get("height"):
                    payload.update({"width": int(args["width"]), "height": int(args["height"])})
                body = json.dumps(payload).encode("utf-8")
                endpoint = base + "/mai/v1/images/generations"
            response = self._request_bytes(endpoint, "POST", headers, body)
            return self.save_output(args["out"], self._image_from_response(json.loads(response)))

        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        payload = {"model": model, "prompt": args["prompt"], "n": 1, "output_format": "png"}
        if args.get("width") and args.get("height"):
            width = int(args["width"])
            height = int(args["height"])
            if protocol == "openai_images" and (width % 16 or height % 16 or max(width / height, height / width) > 3 or width * height > 8_294_400):
                raise ImageRouteError("GPT Image sizes must use multiples of 16, stay within a 3:1 ratio, and fit its pixel limit.")
            payload["size"] = f"{int(args['width'])}x{int(args['height'])}"
        if args.get("transparent_background") and self.provider["capabilities"]["transparent_background"]["native"]:
            payload["background"] = "transparent"
        if self.provider_id == "microsoft_foundry":
            headers = {"api-key": self.require_secret(), "Content-Type": "application/json"}
        else:
            headers = {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json"}
        references = args.get("reference_images", [])
        if args.get("image"):
            references = [args["image"]]
        endpoint = base.rstrip("/") + "/images/generations"
        if references:
            images = []
            for path in references:
                name, data = self.read_reference(path)
                images.append({"filename": name, "data_url": self._data_url(data, image_mime(name))})
            payload["images"] = [item["data_url"] for item in images]
            if protocol == "openai_images":
                boundary_body, boundary = encode_multipart(
                    {key: str(value).lower() if isinstance(value, bool) else str(value) for key, value in payload.items() if key != "images"},
                    [("image[]", item["filename"], image_mime(item["filename"]), base64.b64decode(item["data_url"].split(",",1)[1])) for item in images],
                )
                headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
                body = boundary_body
            else:
                body = json.dumps(payload).encode("utf-8")
            endpoint = base.rstrip("/") + "/images/edits"
        else:
            body = json.dumps(payload).encode("utf-8")
        response = self._request_bytes(endpoint, "POST", headers, body)
        image = self._image_from_response(json.loads(response))
        if args.get("transparent_background"):
            return self.save_transparent_output(args["out"], image)
        return self.save_output(args["out"], image)

    def _generate_openrouter(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        payload = {"model": model, "prompt": args["prompt"]}
        refs = [args["image"]] if args.get("image") else args.get("reference_images", [])
        if refs:
            payload["input_references"] = []
            for path in refs:
                name, data = self.read_reference(path)
                payload["input_references"].append({
                    "type": "image_url",
                    "image_url": {"url": self._data_url(data, image_mime(name))},
                })
        if args.get("transparent_background") and self.provider["capabilities"]["transparent_background"]["native"]:
            payload["background"] = "transparent"
        payload["output_format"] = "png"
        response = self._request_json(
            base.rstrip("/") + "/images",
            "POST",
            {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json"},
            payload,
        )
        image = self._image_from_response(response)
        if args.get("transparent_background"):
            return self.save_transparent_output(args["out"], image)
        return self.save_output(args["out"], image)

    def _generate_xai(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        payload = {"model": model, "prompt": args["prompt"], "n": 1, "response_format": "url"}
        refs = [args["image"]] if args.get("image") else args.get("reference_images", [])
        endpoint = base.rstrip("/") + "/images/generations"
        if refs:
            if len(refs) > 5:
                raise ImageRouteError("Grok Imagine accepts up to five reference images.")
            images = []
            for path in refs:
                name, data = self.read_reference(path)
                images.append({"type": "image_url", "url": self._data_url(data, image_mime(name))})
            payload.pop("n", None)
            payload["image"] = images[0] if len(images) == 1 else None
            if len(images) > 1:
                payload.pop("image")
                payload["images"] = images
            endpoint = base.rstrip("/") + "/images/edits"
        response = self._request_json(
            endpoint,
            "POST",
            {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json"},
            payload,
        )
        return self.save_output(args["out"], self._image_from_response(response))

    def _generate_huggingface(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", model):
            raise ImageRouteError("Choose a Hugging Face model using owner/model-name format.")
        payload = {"inputs": args["prompt"]}
        if args.get("width") and args.get("height"):
            payload["parameters"] = {"width": int(args["width"]), "height": int(args["height"])}
        image = self._request_bytes(
            base.rstrip("/") + "/" + urllib.parse.quote(model, safe="/"),
            "POST",
            {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json", "Accept": "image/png"},
            json.dumps(payload).encode("utf-8"),
        )
        return self.save_output(args["out"], image)

    def _generate_together(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        payload = {
            "model": model,
            "prompt": args["prompt"],
            "n": 1,
            "response_format": "base64",
            "output_format": "png",
            "width": int(args.get("width", 1024)),
            "height": int(args.get("height", 1024)),
        }
        refs = [args["image"]] if args.get("image") else args.get("reference_images", [])
        if refs:
            if len(refs) > 8:
                raise ImageRouteError("FLUX.2 on Together AI accepts up to eight reference images.")
            payload["reference_images"] = []
            for path in refs:
                name, data = self.read_reference(path)
                payload["reference_images"].append(self._data_url(data, image_mime(name)))
        response = self._request_json(
            base.rstrip("/") + "/images/generations",
            "POST",
            {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json"},
            payload,
        )
        return self.save_output(args["out"], self._image_from_response(response))

    def _generate_gemini(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        parts = [{"text": args["prompt"]}]
        refs = args.get("reference_images", [])
        if args.get("image"):
            refs = [args["image"]]
        for path in refs:
            name, data = self.read_reference(path)
            parts.append({"inline_data": {"mime_type": image_mime(name), "data": base64.b64encode(data).decode("ascii")}})
        payload = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"]}}
        url = f"{base.rstrip('/')}/models/{urllib.parse.quote(model, safe='-._')}:generateContent"
        response = self._request_json(url, "POST", {"Content-Type": "application/json", "x-goog-api-key": self.require_secret()}, payload)
        for candidate in response.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                image = part.get("inlineData") or part.get("inline_data")
                if isinstance(image, dict) and isinstance(image.get("data"), str):
                    return self.save_output(args["out"], base64.b64decode(image["data"]))
        raise ImageRouteError("The selected Gemini model returned no image.")

    def _generate_stability(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model("stable-image-ultra")
        if model not in {"stable-image-core", "stable-image-ultra"}:
            raise ImageRouteError("The selected Stability route supports Stable Image Core and Ultra only.")
        tier = "core" if model == "stable-image-core" else "ultra"
        endpoint = base.rstrip("/") + f"/stable-image/generate/{tier}"
        fields = {"prompt": args["prompt"], "output_format": "png"}
        files = []
        reference = args.get("image") or (args.get("reference_images") or [None])[0]
        if reference:
            name, data = self.read_reference(reference)
            endpoint = base.rstrip("/") + "/stable-image/edit/image-to-image"
            files.append(("image", name, image_mime(name), data))
        body, boundary = encode_multipart(fields, files)
        headers = {"Authorization": "Bearer " + self.require_secret(), "Accept": "image/*", "Content-Type": f"multipart/form-data; boundary={boundary}"}
        data = self._request_bytes(endpoint, "POST", headers, body)
        return self.save_output(args["out"], data)

    def _generate_automatic1111(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"], allow_loopback=True).rstrip("/")
        reference = args.get("image") or (args.get("reference_images") or [None])[0]
        path = "/sdapi/v1/img2img" if reference else "/sdapi/v1/txt2img"
        payload = {"prompt": args["prompt"], "width": int(args.get("width", 512)), "height": int(args.get("height", 512)), "batch_size": 1, "n_iter": 1}
        checkpoint = self.provider.get("settings", {}).get("checkpoint")
        if checkpoint:
            payload["override_settings"] = {"sd_model_checkpoint": checkpoint}
        if reference:
            payload["init_images"] = [base64.b64encode(self.read_reference(reference)[1]).decode("ascii")]
        response = self._request_json(base + path, "POST", {"Content-Type": "application/json"}, payload, loopback=True)
        images = response.get("images")
        if not images:
            raise ImageRouteError("The local image server returned no image.")
        return self.save_output(args["out"], base64.b64decode(images[0]))

    def _generate_fal(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)+", model) or ".." in model.split("/"):
            raise ImageRouteError("Choose a valid fal model name from the model catalog.")
        payload = {"prompt": args["prompt"], "image_size": "square_hd", "num_images": 1, "output_format": "png"}
        if args.get("width") and args.get("height"):
            width, height = int(args["width"]), int(args["height"])
            if width * height > 4_194_304:
                raise ImageRouteError("The selected fal FLUX image route is limited to roughly four megapixels.")
            payload["image_size"] = {"width": width, "height": height}
        refs = [args["image"]] if args.get("image") else args.get("reference_images", [])
        if refs:
            if len(refs) > 1:
                raise ImageRouteError("The selected fal model route accepts one reference image.")
            first_name, first_data = self.read_reference(refs[0])
            payload["image_urls"] = [self._data_url(first_data, image_mime(first_name))]
            if not model.endswith("/edit"):
                model = model.rstrip("/") + "/edit"
        headers = {"Authorization": "Key " + self.require_secret(), "Content-Type": "application/json"}
        response = self._request_json(base.rstrip("/") + "/" + model, "POST", headers, payload)
        if isinstance(response.get("images"), list) or response.get("data"):
            return self.save_output(args["out"], self._image_from_response(response))
        urls = response.get("urls", {}) if isinstance(response.get("urls"), dict) else {}
        status_url = response.get("status_url") or urls.get("status")
        result_url = response.get("response_url") or urls.get("response")
        request_id = response.get("request_id")
        if not isinstance(request_id, str) or not isinstance(status_url, str) or not isinstance(result_url, str):
            raise ImageRouteError("fal did not return a request status and result link.")
        status_url = _safe_url(self.provider_id, status_url)
        result_url = _safe_url(self.provider_id, result_url)
        for _ in range(120):
            status = self._request_json(status_url, "GET", {"Authorization": headers["Authorization"]})
            state = status.get("status")
            if state in {"COMPLETED", "succeeded", "successful"}:
                result = self._request_json(result_url, "GET", {"Authorization": headers["Authorization"]})
                return self.save_output(args["out"], self._image_from_response(result))
            if state in {"FAILED", "Error", "failed", "canceled", "CANCELLED"}:
                raise ImageRouteError("fal could not complete the image request.")
            time.sleep(1)
        raise ImageRouteError("fal is still preparing the image. Check status and retry.")

    def _generate_replicate(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        parts = model.split("/")
        if len(parts) != 2 or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", model) or ".." in parts:
            raise ImageRouteError("Choose a Replicate model in owner/name format.")
        image_input = {"prompt": args["prompt"], "num_outputs": 1, "output_format": "png"}
        refs = [args["image"]] if args.get("image") else args.get("reference_images", [])
        if refs:
            if len(refs) > 1:
                raise ImageRouteError("This Replicate adapter passes one reference image per request.")
            name, data = self.read_reference(refs[0])
            image_input["image"] = self._data_url(data, image_mime(name))
        endpoint_model = "/".join(urllib.parse.quote(part, safe="-._") for part in parts)
        response = self._request_json(f"{base.rstrip('/')}/models/{endpoint_model}/predictions", "POST", {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json", "Prefer": "wait=60"}, {"input": image_input})
        if response.get("status") not in {None, "succeeded", "successful"}:
            raise ImageRouteError("The Replicate job is still running; check it from the coding client and retry when complete.")
        return self.save_output(args["out"], self._image_from_response({"data": response.get("output", []) if isinstance(response.get("output"), list) else [{"url": response.get("output")}] }))

    def _generate_bfl(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model()
        payload = {"prompt": args["prompt"], "output_format": "png", "width": int(args.get("width", 1024)), "height": int(args.get("height", 1024))}
        refs = [args["image"]] if args.get("image") else args.get("reference_images", [])
        if refs:
            if len(refs) > 1:
                raise ImageRouteError("The selected FLUX API route accepts one reference image.")
            payload["input_image"] = base64.b64encode(self.read_reference(refs[0])[1]).decode("ascii")
        response = self._request_json(base.rstrip("/") + "/" + urllib.parse.quote(model, safe="-._"), "POST", {"x-key": self.require_secret(), "Content-Type": "application/json"}, payload)
        return self.save_output(args["out"], self._poll_image_result(response, "x-key", self.require_secret()))

    def _generate_ideogram(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model("ideogram-v4")
        reference = args.get("image") or (args.get("reference_images") or [None])[0]
        transparent = bool(args.get("transparent_background"))
        if reference and transparent:
            raise ImageRouteError("Ideogram edits do not combine with its transparent-generation route; generate a transparent asset or use background removal.")
        fields = {"text_prompt": args["prompt"], "rendering_speed": "DEFAULT"}
        files = []
        if reference:
            name, data = self.read_reference(reference)
            endpoint = f"/{urllib.parse.quote(model, safe='-._')}/remix"
            files.append(("image", name, image_mime(name), data))
        elif transparent:
            endpoint = f"/{urllib.parse.quote(model, safe='-._')}/generate-transparent"
            fields["output_resolution"] = "1K"
        else:
            endpoint = f"/{urllib.parse.quote(model, safe='-._')}/generate"
        body, boundary = encode_multipart(fields, files)
        response = self._request_json(
            base.rstrip("/") + endpoint,
            "POST",
            {"Api-Key": self.require_secret(), "Content-Type": f"multipart/form-data; boundary={boundary}"},
            body,
        )
        image = self._image_from_response(response)
        if transparent and png_has_transparent_pixels(image) is not True:
            raise ImageRouteError("Ideogram did not return verifiable transparent pixels.")
        if transparent:
            return self.save_transparent_output(args["out"], image)
        return self.save_output(args["out"], image)

    def _generate_recraft(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        model = self.selected_model("recraftv4_1")
        payload = {"model": model, "prompt": args["prompt"], "n": 1, "response_format": "b64_json", "image_format": "png"}
        reference = args.get("image")
        refs = args.get("reference_images", [])
        if reference:
            name, data = self.read_reference(reference)
            payload.update({"image_url": self._data_url(data, image_mime(name)), "strength": 0.5})
            endpoint = "/images/imageToImage"
        elif refs:
            if len(refs) > 10:
                raise ImageRouteError("Recraft accepts up to ten style-reference images.")
            payload["model"] = "recraftv4_styles"
            payload["style_reference_urls"] = [
                self._data_url(data, image_mime(name)) for name, data in (self.read_reference(path) for path in refs)
            ]
            endpoint = "/images/generations"
        else:
            endpoint = "/images/generations"
        response = self._request_json(base.rstrip("/") + endpoint, "POST", {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json"}, payload)
        return self.save_output(args["out"], self._image_from_response(response))

    def _generate_leonardo(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        payload = {"prompt": args["prompt"], "num_images": 1, "width": int(args.get("width", 1024)), "height": int(args.get("height", 1024))}
        model = self.selected_model()
        if model:
            payload["modelId"] = model
        response = self._request_json(base.rstrip("/") + "/generations", "POST", {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json"}, payload)
        generation_id = response.get("sdGenerationJob", {}).get("generationId") or response.get("generationId")
        if not isinstance(generation_id, str):
            raise ImageRouteError("Leonardo did not return an image generation ID.")
        for _ in range(40):
            time.sleep(2)
            status = self._request_json(
                base.rstrip("/") + "/generations/" + urllib.parse.quote(generation_id, safe=""),
                "GET",
                {"Authorization": "Bearer " + self.require_secret(), "Accept": "application/json"},
            )
            record = status.get("generations_by_pk", {}) if isinstance(status, dict) else {}
            images = record.get("generated_images", []) if isinstance(record, dict) else []
            for item in images:
                if isinstance(item, dict):
                    data = self._image_from_response(item)
                    return self.save_output(args["out"], data)
        raise ImageRouteError("Leonardo is still preparing the image; check status and retry.")

    def _generate_adobe(self, args: dict) -> dict:
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        payload = {"prompt": {"text": args["prompt"]}, "size": {"width": int(args.get("width", 1024)), "height": int(args.get("height", 1024))}}
        response = self._request_json(base.rstrip("/") + "/images/generate", "POST", {"Authorization": "Bearer " + self.require_secret("ims_token"), "x-api-key": self.require_secret("service_key"), "Content-Type": "application/json"}, payload)
        return self.save_output(args["out"], self._image_from_response(response))

    def _generate_vertex(self, args: dict) -> dict:
        try:
            service = json.loads(self.require_secret("service_account"))
            email = service["client_email"]
            private_key = service["private_key"]
            project = service["project_id"]
            token_url = service.get("token_uri", "https://oauth2.googleapis.com/token")
        except (KeyError, json.JSONDecodeError):
            raise ImageRouteError("Save a valid Google Cloud service-account key in setup settings.") from None
        now = int(time.time())
        claims = {"iss": email, "scope": "https://www.googleapis.com/auth/cloud-platform", "aud": token_url, "iat": now, "exp": now + 3600}
        header = _b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
        body = _b64url(json.dumps(claims, separators=(",", ":")).encode())
        unsigned = f"{header}.{body}"
        assertion = unsigned + "." + _b64url(_rsa_sha256_sign(private_key, unsigned.encode()))
        token_body = urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion}).encode()
        token_data = self._request_bytes(token_url, "POST", {"Content-Type": "application/x-www-form-urlencoded"}, token_body)
        try:
            token_response = json.loads(token_data)
        except json.JSONDecodeError:
            raise ImageRouteError("Google Cloud returned an unreadable sign-in response.") from None
        access_token = token_response.get("access_token")
        if not isinstance(access_token, str):
            raise ImageRouteError("Google Cloud did not return an access token.")
        base = _safe_url(self.provider_id, self.route["api_base_url"])
        region = urllib.parse.urlparse(base).hostname.split("-aiplatform", 1)[0]
        model = self.selected_model()
        endpoint = f"{base.rstrip('/')}/projects/{urllib.parse.quote(project, safe='')}/locations/{urllib.parse.quote(region, safe='')}/publishers/google/models/{urllib.parse.quote(model, safe='-._')}:predict"
        payload = {"instances": [{"prompt": args["prompt"]}], "parameters": {"sampleCount": 1, "aspectRatio": "1:1"}}
        response = self._request_json(endpoint, "POST", {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}, payload)
        for prediction in response.get("predictions", []):
            encoded = prediction.get("bytesBase64Encoded") if isinstance(prediction, dict) else None
            if isinstance(encoded, str):
                return self.save_output(args["out"], base64.b64decode(encoded))
        raise ImageRouteError("Vertex AI returned no image.")

    def _generate_bedrock(self, args: dict) -> dict:
        settings = self.provider.get("settings", {})
        region = settings.get("region", "us-west-2")
        if not re.fullmatch(r"[a-z]{2}-[a-z]+-\d", region):
            raise ImageRouteError("Choose a valid AWS region in image provider settings.")
        model = self.selected_model()
        payload = {"prompt": args["prompt"], "output_format": "png"}
        reference = args.get("image") or (args.get("reference_images") or [None])[0]
        if reference:
            name, data = self.read_reference(reference)
            if len(args.get("reference_images", [])) > 1:
                raise ImageRouteError("The included Bedrock image-edit route accepts one reference image.")
            payload["image"] = base64.b64encode(data).decode("ascii")
            payload["strength"] = 0.35
        return self._bedrock_request(args["out"], model, payload, region)

    def _generate_comfyui(self, args: dict) -> dict:
        settings = self.provider.get("settings", {})
        base = settings.get("server_url", "http://127.0.0.1:8188").rstrip("/")
        _safe_url(self.provider_id, base, allow_loopback=True)
        checkpoint = settings.get("checkpoint")
        if not isinstance(checkpoint, str) or not checkpoint.strip():
            raise ImageRouteError("Choose a checkpoint installed in ComfyUI in image provider settings.")
        width = _image_dimension(args.get("width", 1024))
        height = _image_dimension(args.get("height", 1024))
        prompt_id = hashlib.sha256(f"{time.time_ns()}:{os.getpid()}".encode()).hexdigest()[:16]
        workflow = self._comfy_workflow(args, checkpoint, width, height, base)
        queued = self._request_json(base + "/prompt", "POST", {"Content-Type": "application/json"}, {"prompt": workflow, "client_id": prompt_id}, loopback=True)
        job = queued.get("prompt_id")
        if not isinstance(job, str):
            raise ImageRouteError("ComfyUI did not accept the workflow.")
        for _ in range(60):
            time.sleep(2)
            history = self._request_json(base + "/history/" + urllib.parse.quote(job, safe=""), "GET", {}, loopback=True)
            record = history.get(job, {}) if isinstance(history, dict) else {}
            for node in record.get("outputs", {}).values():
                for item in node.get("images", []):
                    if not isinstance(item, dict) or not item.get("filename"):
                        continue
                    query = urllib.parse.urlencode({"filename": item["filename"], "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")})
                    image = self._request_bytes(base + "/view?" + query, "GET", {}, loopback=True)
                    return self.save_output(args["out"], image)
        raise ImageRouteError("ComfyUI is still running; check its queue and retry when the image is ready.")

    def _comfy_workflow(self, args: dict, checkpoint: str, width: int, height: int, base: str) -> dict:
        nodes = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
            "2": {"class_type": "CLIPTextEncode", "inputs": {"text": args["prompt"], "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["1", 1]}},
            "4": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
            "5": {"class_type": "KSampler", "inputs": {"seed": int(time.time_ns() & 0x7FFFFFFF), "steps": 24, "cfg": 7, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
            "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
            "7": {"class_type": "SaveImage", "inputs": {"filename_prefix": "hoi4_image", "images": ["6", 0]}},
        }
        reference = args.get("image") or (args.get("reference_images") or [None])[0]
        if reference:
            name, data = self.read_reference(reference)
            boundary_data, boundary = encode_multipart({"type": "input", "overwrite": "false"}, [("image", name, image_mime(name), data)])
            request = urllib.request.Request(base + "/upload/image", data=boundary_data, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    uploaded = json.loads(response.read(1024 * 1024))
            except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
                raise ImageRouteError("ComfyUI could not stage the reference image.") from None
            image_name = uploaded.get("name") if isinstance(uploaded, dict) else None
            if not isinstance(image_name, str):
                raise ImageRouteError("ComfyUI did not return the staged reference image.")
            nodes["4"] = {"class_type": "LoadImage", "inputs": {"image": image_name}}
            nodes["5"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}}
            nodes["6"] = {"class_type": "KSampler", "inputs": {"seed": int(time.time_ns() & 0x7FFFFFFF), "steps": 24, "cfg": 7, "sampler_name": "euler", "scheduler": "normal", "denoise": 0.75, "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["5", 0]}}
            nodes["7"] = {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}}
            nodes["8"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": "hoi4_image", "images": ["7", 0]}}
        return nodes

    def _aws_headers(self, url: str, body: bytes, region: str) -> dict[str, str]:
        access = self.require_secret("access_key")
        secret = self.require_secret("secret_key")
        service = "bedrock"
        now = time.gmtime()
        amzdate = time.strftime("%Y%m%dT%H%M%SZ", now)
        date = amzdate[:8]
        parsed = urllib.parse.urlparse(url)
        content_type = "application/json"
        payload_hash = hashlib.sha256(body).hexdigest()
        canonical_headers = f"content-type:{content_type}\nhost:{parsed.netloc}\nx-amz-date:{amzdate}\n"
        signed_headers = "content-type;host;x-amz-date"
        canonical_request = "\n".join(["POST", parsed.path, parsed.query, canonical_headers, signed_headers, payload_hash])
        scope = f"{date}/{region}/{service}/aws4_request"
        string_to_sign = "AWS4-HMAC-SHA256\n" + amzdate + "\n" + scope + "\n" + hashlib.sha256(canonical_request.encode()).hexdigest()
        def sign(key: bytes, value: str) -> bytes:
            return hmac.new(key, value.encode(), hashlib.sha256).digest()
        key_date = sign(("AWS4" + secret).encode(), date)
        key_region = sign(key_date, region)
        key_service = sign(key_region, service)
        key_signing = sign(key_service, "aws4_request")
        signature = hmac.new(key_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        authorization = f"AWS4-HMAC-SHA256 Credential={access}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"
        return {"Content-Type": content_type, "X-Amz-Date": amzdate, "Authorization": authorization}

    def _bedrock_request(self, output_path: str, model: str, payload: dict, region: str | None = None, *, require_alpha: bool = False) -> dict:
        if region is None:
            region = self.provider.get("settings", {}).get("region", "us-west-2")
        if not re.fullmatch(r"[a-z]{2}-[a-z]+-\d", region):
            raise ImageRouteError("Choose a valid AWS region in image provider settings.")
        url = f"https://bedrock-runtime.{region}.amazonaws.com/model/{urllib.parse.quote(model, safe=':._-')}/invoke"
        body = json.dumps(payload, separators=(",", ":")).encode()
        headers = self._aws_headers(url, body, region)
        response = self._request_json(url, "POST", headers, payload)
        image = self._image_from_response(response)
        return self.save_transparent_output(output_path, image) if require_alpha else self.save_output(output_path, image)

    def remove_background(self, args: dict) -> dict:
        protocol = self.route.get("api_protocol")
        name, data = self.read_reference(args.get("image", ""))
        if protocol == "stability":
            fields = {"output_format": "png"}
            body, boundary = encode_multipart(fields, [("image", name, image_mime(name), data)])
            url = self.route["api_base_url"].rstrip("/") + "/stable-image/edit/remove-background"
            output = self._request_bytes(url, "POST", {"Authorization": "Bearer " + self.require_secret(), "Accept": "image/*", "Content-Type": f"multipart/form-data; boundary={boundary}"}, body)
            return self.save_transparent_output(args["out"], output)
        if protocol == "recraft":
            payload = {"image_url": self._data_url(data, image_mime(name)), "response_format": "b64_json", "image_format": "png"}
            url = self.route["api_base_url"].rstrip("/") + "/images/removeBackground"
            response = self._request_json(url, "POST", {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json"}, payload)
            image = self._image_from_response(response)
            return self.save_transparent_output(args["out"], image)
        if protocol == "replicate_predictions":
            base = _safe_url(self.provider_id, self.route["api_base_url"])
            payload = {"input": {"image": self._data_url(data)}}
            response = self._request_json(base.rstrip("/") + "/models/bria/remove-background/predictions", "POST", {"Authorization": "Bearer " + self.require_secret(), "Content-Type": "application/json", "Prefer": "wait=60"}, payload)
            return self.save_transparent_output(args["out"], self._poll_image_result(response, "Authorization", "Bearer " + self.require_secret()))
        if protocol == "aws_bedrock":
            dimensions = image_dimensions(name, data)
            if dimensions is None:
                raise ImageRouteError("The selected file's image dimensions could not be checked for Bedrock background removal.")
            width, height = dimensions
            if min(width, height) < 64 or width * height > 9_437_184 or max(width / height, height / width) > 2.5:
                raise ImageRouteError("Bedrock background removal needs an image at least 64 pixels on each side, within its pixel cap and 2.5:1 shape limit.")
            return self._bedrock_request(args["out"], "stability.stable-image-remove-background-v1:0", {"image": base64.b64encode(data).decode("ascii")}, require_alpha=True)
        if protocol == "adobe_firefly":
            return self._generate_adobe({"prompt": "Remove the background from the supplied image.", "image": args.get("image"), "out": args["out"]})
        raise ImageRouteError("This provider has no background-removal tool. Use a selected remover or another provider.")

    def _poll_image_result(self, response: dict, header: str, credential: str) -> bytes:
        try:
            return self._image_from_response(response)
        except ImageRouteError:
            pass
        polling_url = response.get("polling_url") or response.get("urls", {}).get("get")
        if not isinstance(polling_url, str):
            raise ImageRouteError("The provider returned no image or job status link.")
        for _ in range(40):
            time.sleep(3)
            status = self._request_json(_safe_url(self.provider_id, polling_url), "GET", {header: credential})
            if status.get("status") in {"Ready", "succeeded", "successful", "complete"}:
                return self._image_from_response(status)
            if status.get("status") in {"Error", "failed", "canceled"}:
                raise ImageRouteError("The provider could not complete the image request.")
        raise ImageRouteError("The provider is still preparing the image. Check status and retry.")

    @staticmethod
    def _data_url(data: bytes, mime: str | None = None) -> str:
        if mime is None:
            mime = "image/png" if data.startswith(b"\x89PNG\r\n\x1a\n") else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--config", default=str(CONFIG_PATH))
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    Server(args.provider, root, Path(args.config)).run()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        # MCP output is reserved for JSON-RPC; keep startup failures concise.
        print("Image provider server could not start: " + str(error)[:400], file=sys.stderr)
        raise SystemExit(2)
