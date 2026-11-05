"""Model textures in the format vanilla units ship: DXT5 with a full mip chain.

Vanilla 1.19.4.1 unit textures (`gfx/models/units`) are DXT5 or DXT1 with a
mip chain down to 1x1 (736 of 743 files). A single-level BGRA texture costs
four times the memory of DXT5 and has no smaller levels, so the zoomed-out map
samples the full-size map and shimmers. This module writes DXT5 with mips and
reads DXT1, DXT5 and uncompressed 32-bit DDS files for the checks. It needs
numpy and Pillow, which `.tools/gfx/requirements.txt` already lists.

The encoder fits each 4x4 block's colors along their principal axis and its
alpha between the block minimum and maximum. That is the plain range fit most
encoders start from; it is not tuned for maximum quality.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Dict, List, Union

import numpy as np
from PIL import Image

DDSD_CAPS = 0x1
DDSD_HEIGHT = 0x2
DDSD_WIDTH = 0x4
DDSD_PIXELFORMAT = 0x1000
DDSD_MIPMAPCOUNT = 0x20000
DDSD_LINEARSIZE = 0x80000
DDPF_ALPHAPIXELS = 0x1
DDPF_FOURCC = 0x4
DDPF_RGB = 0x40
DDSCAPS_COMPLEX = 0x8
DDSCAPS_TEXTURE = 0x1000
DDSCAPS_MIPMAP = 0x400000


class DdsError(ValueError):
    pass


def read_header(data: bytes) -> Dict[str, Union[int, str, bool]]:
    """Width, height, mip count and format of a DDS file's bytes."""

    if len(data) < 128 or data[:4] != b"DDS ":
        raise DdsError("not a DDS file")
    height, width = struct.unpack_from("<II", data, 12)
    mips = struct.unpack_from("<I", data, 28)[0]
    pf_flags = struct.unpack_from("<I", data, 80)[0]
    fourcc = data[84:88]
    bits = struct.unpack_from("<I", data, 88)[0]
    if pf_flags & DDPF_FOURCC:
        fmt = fourcc.decode("latin-1")
    elif pf_flags & DDPF_RGB:
        fmt = f"RGB{bits}"
    else:
        fmt = "unknown"
    return {
        "width": width,
        "height": height,
        "mips": max(1, mips),
        "format": fmt,
        "compressed": fmt in {"DXT1", "DXT3", "DXT5"},
    }


def full_mip_count(width: int, height: int) -> int:
    return max(width, height).bit_length()


def _blocks(rgba: np.ndarray) -> np.ndarray:
    """Split an HxWx4 image into (N, 16, 4) blocks, padding edges by repetition."""

    height, width = rgba.shape[:2]
    padded_h, padded_w = (height + 3) // 4 * 4, (width + 3) // 4 * 4
    if (padded_h, padded_w) != (height, width):
        rgba = np.pad(rgba, ((0, padded_h - height), (0, padded_w - width), (0, 0)), mode="edge")
    blocks = rgba.reshape(padded_h // 4, 4, padded_w // 4, 4, 4).transpose(0, 2, 1, 3, 4)
    return blocks.reshape(-1, 16, 4)


def _to_565(colors: np.ndarray) -> np.ndarray:
    c = np.clip(np.rint(colors), 0, 255).astype(np.uint32)
    return ((c[..., 0] >> 3) << 11) | ((c[..., 1] >> 2) << 5) | (c[..., 2] >> 3)


def _from_565(values: np.ndarray) -> np.ndarray:
    values = values.astype(np.uint32)
    r = (values >> 11) & 31
    g = (values >> 5) & 63
    b = values & 31
    return np.stack([(r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)], axis=-1).astype(np.float32)


def _encode_color(blocks: np.ndarray) -> np.ndarray:
    """BC1 color part (8 bytes per block, four-color mode) for (N, 16, 3) float colors."""

    mean = blocks.mean(axis=1, keepdims=True)
    centered = blocks - mean
    covariance = np.einsum("nki,nkj->nij", centered, centered)
    axis = np.ones((blocks.shape[0], 3), dtype=np.float32)
    for _ in range(8):
        axis = np.einsum("nij,nj->ni", covariance, axis)
        norm = np.linalg.norm(axis, axis=1, keepdims=True)
        axis = np.where(norm > 1e-6, axis / np.maximum(norm, 1e-6), np.array([0.577, 0.577, 0.577], dtype=np.float32))
    projection = np.einsum("nki,ni->nk", centered, axis)
    low = mean[:, 0] + axis * projection.min(axis=1, keepdims=True)
    high = mean[:, 0] + axis * projection.max(axis=1, keepdims=True)
    c0 = _to_565(high)
    c1 = _to_565(low)
    swap = c0 < c1
    c0, c1 = np.where(swap, c1, c0), np.where(swap, c0, c1)
    e0, e1 = _from_565(c0), _from_565(c1)
    palette = np.stack([e0, e1, (2 * e0 + e1) / 3, (e0 + 2 * e1) / 3], axis=1)
    distance = ((blocks[:, :, None, :] - palette[:, None, :, :]) ** 2).sum(axis=-1)
    indices = distance.argmin(axis=-1).astype(np.uint32)
    indices[c0 == c1] = 0
    packed = np.zeros(blocks.shape[0], dtype=np.uint32)
    for pixel in range(16):
        packed |= indices[:, pixel] << (2 * pixel)
    out = np.zeros((blocks.shape[0], 8), dtype=np.uint8)
    out[:, 0:2] = c0.astype("<u2").view(np.uint8).reshape(-1, 2)
    out[:, 2:4] = c1.astype("<u2").view(np.uint8).reshape(-1, 2)
    out[:, 4:8] = packed.astype("<u4").view(np.uint8).reshape(-1, 4)
    return out


def _alpha_palette(a0: np.ndarray, a1: np.ndarray) -> np.ndarray:
    a0 = a0.astype(np.float32)
    a1 = a1.astype(np.float32)
    levels = [a0, a1] + [((7 - k) * a0 + k * a1) / 7 for k in range(1, 7)]
    return np.stack(levels, axis=1)


def _encode_alpha(alpha: np.ndarray) -> np.ndarray:
    """BC3 alpha part (8 bytes per block, eight-level mode) for (N, 16) alpha."""

    a0 = alpha.max(axis=1).astype(np.uint8)
    a1 = alpha.min(axis=1).astype(np.uint8)
    palette = _alpha_palette(a0, a1)
    indices = np.abs(alpha[:, :, None].astype(np.float32) - palette[:, None, :]).argmin(axis=-1).astype(np.uint64)
    indices[a0 == a1] = 0
    bits = np.zeros(alpha.shape[0], dtype=np.uint64)
    for pixel in range(16):
        bits |= indices[:, pixel] << np.uint64(3 * pixel)
    out = np.zeros((alpha.shape[0], 8), dtype=np.uint8)
    out[:, 0] = a0
    out[:, 1] = a1
    out[:, 2:8] = bits.astype("<u8").view(np.uint8).reshape(-1, 8)[:, :6]
    return out


def encode_dxt5_level(rgba: np.ndarray) -> bytes:
    blocks = _blocks(rgba)
    alpha = _encode_alpha(blocks[:, :, 3])
    color = _encode_color(blocks[:, :, :3].astype(np.float32))
    return np.concatenate([alpha, color], axis=1).tobytes()


def mip_chain(image: Image.Image) -> List[np.ndarray]:
    """Every level from the full size down to 1x1, each half the previous (box filter)."""

    levels = [np.asarray(image.convert("RGBA"), dtype=np.uint8)]
    current = image.convert("RGBA")
    while current.width > 1 or current.height > 1:
        current = current.resize((max(1, current.width // 2), max(1, current.height // 2)), Image.Resampling.BOX)
        levels.append(np.asarray(current, dtype=np.uint8))
    return levels


def dxt5_bytes(image: Image.Image) -> bytes:
    """A complete DXT5 DDS file with a full mip chain."""

    width, height = image.size
    if width & (width - 1) or height & (height - 1):
        raise DdsError(f"model textures must be a power of two on each side, not {width}x{height}")
    levels = mip_chain(image)
    payload = b"".join(encode_dxt5_level(level) for level in levels)
    top_size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * 16
    header = struct.pack(
        "<4sIIIIIII44sIIIIIIIIIIIII",
        b"DDS ",
        124,
        DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_MIPMAPCOUNT | DDSD_LINEARSIZE,
        height,
        width,
        top_size,
        0,
        len(levels),
        b"\0" * 44,
        32,
        DDPF_FOURCC,
        int.from_bytes(b"DXT5", "little"),
        0, 0, 0, 0, 0,
        DDSCAPS_TEXTURE | DDSCAPS_MIPMAP | DDSCAPS_COMPLEX,
        0, 0, 0, 0,
    )
    return header + payload


def write_dxt5(source: Path, destination: Path) -> Dict[str, Union[int, str, bool]]:
    """Write `source` (any image Pillow reads) as a mipped DXT5 DDS and return its header."""

    with Image.open(source) as image:
        data = dxt5_bytes(image)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".partial")
    temporary.write_bytes(data)
    temporary.replace(destination)
    return read_header(data)


def _decode_color(data: np.ndarray, four_color_only: bool) -> np.ndarray:
    c0 = data[:, 0].astype(np.uint32) | (data[:, 1].astype(np.uint32) << 8)
    c1 = data[:, 2].astype(np.uint32) | (data[:, 3].astype(np.uint32) << 8)
    e0, e1 = _from_565(c0), _from_565(c1)
    four = (c0 > c1) | four_color_only
    third = np.where(four[:, None], (2 * e0 + e1) / 3, (e0 + e1) / 2)
    fourth = np.where(four[:, None], (e0 + 2 * e1) / 3, 0)
    palette = np.stack([e0, e1, third, fourth], axis=1)
    bits = data[:, 4].astype(np.uint32) | (data[:, 5].astype(np.uint32) << 8) | (data[:, 6].astype(np.uint32) << 16) | (data[:, 7].astype(np.uint32) << 24)
    indices = np.stack([(bits >> (2 * pixel)) & 3 for pixel in range(16)], axis=1)
    return np.take_along_axis(palette, indices[:, :, None].astype(np.int64), axis=1)


def _decode_alpha(data: np.ndarray) -> np.ndarray:
    a0, a1 = data[:, 0], data[:, 1]
    eight = a0 > a1
    levels8 = _alpha_palette(a0, a1)
    a0f, a1f = a0.astype(np.float32), a1.astype(np.float32)
    levels6 = np.stack([a0f, a1f] + [((5 - k) * a0f + k * a1f) / 5 for k in range(1, 5)] + [np.zeros_like(a0f), np.full_like(a0f, 255)], axis=1)
    palette = np.where(eight[:, None], levels8, levels6)
    bits = np.zeros(data.shape[0], dtype=np.uint64)
    for byte in range(6):
        bits |= data[:, 2 + byte].astype(np.uint64) << np.uint64(8 * byte)
    indices = np.stack([(bits >> np.uint64(3 * pixel)) & np.uint64(7) for pixel in range(16)], axis=1).astype(np.int64)
    return np.take_along_axis(palette, indices, axis=1)


def decode_top_level(data: bytes) -> np.ndarray:
    """The full-size level as an HxWx4 RGBA uint8 array (DXT1, DXT5 or 32-bit BGRA/RGBA)."""

    header = read_header(data)
    width, height, fmt = int(header["width"]), int(header["height"]), str(header["format"])
    offset = 128
    blocks_w, blocks_h = max(1, (width + 3) // 4), max(1, (height + 3) // 4)
    count = blocks_w * blocks_h
    if fmt in {"DXT1", "DXT5"}:
        size = 8 if fmt == "DXT1" else 16
        raw = np.frombuffer(data, dtype=np.uint8, count=count * size, offset=offset).reshape(count, size)
        if fmt == "DXT1":
            color = _decode_color(raw, four_color_only=False)
            alpha = np.full((count, 16), 255.0, dtype=np.float32)
        else:
            alpha = _decode_alpha(raw[:, :8])
            color = _decode_color(raw[:, 8:], four_color_only=True)
        rgba = np.concatenate([color, alpha[:, :, None]], axis=-1)
        image = rgba.reshape(blocks_h, blocks_w, 4, 4, 4).transpose(0, 2, 1, 3, 4).reshape(blocks_h * 4, blocks_w * 4, 4)
        return np.clip(np.rint(image[:height, :width]), 0, 255).astype(np.uint8)
    if fmt == "RGB32":
        masks = struct.unpack_from("<IIII", data, 92)
        pixels = np.frombuffer(data, dtype="<u4", count=width * height, offset=offset).reshape(height, width)
        channels = []
        for mask in masks:
            if mask == 0:
                channels.append(np.full((height, width), 255, dtype=np.uint8))
                continue
            shift = (mask & -mask).bit_length() - 1
            channels.append(((pixels & mask) >> shift).astype(np.uint8))
        return np.stack(channels, axis=-1)
    raise DdsError(f"cannot decode DDS format {fmt}")
