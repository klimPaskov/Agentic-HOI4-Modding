#!/usr/bin/env python3
"""Bounded, review-first 2D sprite QA and mechanical alpha repair."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union, cast

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import distance_transform_edt, binary_erosion, label

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '.tools'))
from lib.game import game_dir
from lib.report import (
    Finding, PathFilter, add_arguments, exit_code, merge_json, print_findings, requested_paths,
    relative as report_relative,
)
# Repository values (asset-tool folder, shared registry prefix) live in settings.json beside this file.
SETTINGS: Dict[str, str] = json.loads(Path(__file__).with_name('settings.json').read_text(encoding='utf-8'))
ASSET_TOOLS = ROOT / SETTINGS['asset_tools']
CONVERTER = ASSET_TOOLS / 'convert_to_dds.py'
# Canvas profiles and the source of every number live in profiles.json.
PROFILE_DATA: Dict[str, Dict[str, Any]] = json.loads(
    Path(__file__).with_name('profiles.json').read_text(encoding='utf-8'))['profiles']
# (canvas width, canvas height, minimum margin) per profile, for the `size` command.
PROFILES: Dict[str, Tuple[int, int, int]] = {
    name: (int(p['canvas'][0]), int(p['canvas'][1]), int(p['margin'])) for name, p in PROFILE_DATA.items()}


def digest(path: Union[str, Path]) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path: Union[str, Path]) -> Image.Image:
    """Fail closed on LFS stubs, truncated inputs and unsupported DDS formats."""
    path = Path(path)
    with path.open('rb') as stream:
        prefix = stream.read(160)
    if prefix.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
        raise ValueError(f'LFS pointer is not image data: {path}')
    with Image.open(path) as source:
        source.load()
        return source.convert('RGBA')


def strict_dds(path: Union[str, Path]) -> Image.Image:
    """Canonical skill converter layout, not merely decoder acceptance."""
    raw = Path(path).read_bytes()
    if len(raw) < 128:
        raise ValueError('DDS header truncated')
    magic, *words = struct.unpack('<4s31I', raw[:128])
    h, w = words[2:4]
    expected = [124, 0x100f, h, w, w * 4, 0, 0, *([0] * 11),
                32, 65, 0, 32, 0xff0000, 0xff00, 0xff, 0xff000000,
                0x1000, 0, 0, 0, 0]
    if magic != b'DDS ' or words != expected or not w or not h:
        raise ValueError('Not canonical one-level legacy BGRA DDS')
    if len(raw) != 128 + w * h * 4:
        raise ValueError('DDS payload length mismatch')
    return Image.frombytes('RGBA', (w, h), raw[128:], 'raw', 'BGRA')


def write_dds(image: Image.Image, path: Union[str, Path], overwrite: bool = False) -> None:
    """Call the single canonical writer, then strict-decode and compare pixels."""
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    image = image.convert('RGBA')
    spec = importlib.util.spec_from_file_location('dds_converter', CONVERTER)
    assert spec is not None and spec.loader is not None
    converter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(converter)
    path.parent.mkdir(parents=True, exist_ok=True)
    scratch: Union[str, Path]
    fd, scratch = tempfile.mkstemp(suffix='.dds', dir=path.parent)
    os.close(fd)
    scratch = Path(scratch)
    try:
        converter.write_bgra_dds(scratch, image.width, image.height, image.tobytes('raw', 'BGRA'))
        decoded = strict_dds(scratch)
        if decoded.tobytes() != image.tobytes() or load(scratch).tobytes() != image.tobytes():
            raise ValueError('DDS round-trip pixels differ')
        install_output(scratch, path, overwrite)
    finally:
        scratch.unlink(missing_ok=True)


def write_png(image: Image.Image, path: Union[str, Path], overwrite: bool = False) -> None:
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    scratch: Union[str, Path]
    fd, scratch = tempfile.mkstemp(suffix='.png', dir=path.parent)
    os.close(fd)
    scratch = Path(scratch)
    try:
        image.save(scratch)
        if load(scratch).tobytes() != image.tobytes():
            raise ValueError('PNG round-trip pixels differ')
        install_output(scratch, path, overwrite)
    finally:
        scratch.unlink(missing_ok=True)


def install_output(scratch: Path, path: Path, overwrite: bool) -> None:
    if overwrite:
        os.replace(scratch, path)
    else:
        # Same-directory hard link is an atomic exclusive install, so another
        # worker creating the output between the exists check and here survives.
        # Unsupported filesystems fail closed instead of allowing clobbering.
        os.link(scratch, path)


def frames(image: Image.Image, count: int) -> List[Image.Image]:
    if count < 1 or image.width % count:
        raise ValueError('Frame count must divide sheet width exactly')
    width = image.width // count
    return [image.crop((i * width, 0, (i + 1) * width, image.height)) for i in range(count)]


def chroma(rgb: Any, delta: int = 40) -> Any:
    rgb = rgb.astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return ((r > g + delta) & (b > g + delta)) | ((g > r + delta) & (g > b + delta))


def alpha_stats(image: Image.Image) -> Dict[str, Any]:
    a = np.asarray(image)[..., 3]
    subject = a[a > 0]
    bbox = image.getchannel('A').getbbox()
    return {'subject_alpha_mean': round(float(subject.mean()), 3) if subject.size else 0,
            'alpha_min': int(a.min()), 'alpha_max': int(a.max()),
            'subject_pixels': int(subject.size), 'opaque_pixels': int((a == 255).sum()),
            'visible_bounds': list(bbox) if bbox else None,
            'ghosted': not subject.size or float(subject.mean()) < 200}


def edge_stats(image: Image.Image) -> Dict[str, int]:
    arr = np.asarray(image)
    a = arr[..., 3]
    # Include opaque boundary pixels as well as the antialiased rim.
    edge = (a > 0) & ((a < 255) | ~binary_erosion(a > 0, border_value=0))
    return {'edge_pixels': int(edge.sum()),
            'chroma_edge_pixels': int((edge & chroma(arr[..., :3])).sum())}


def defringe(image: Image.Image, erosion: int = 1, spill_mask: Any = None) -> Image.Image:
    """Erode alpha; extend nearest uncontaminated interior RGB into the rim.

    Intentionally does not key opaque backgrounds, unpremultiply colours or
    increase opacity. Such changes need source evidence and separate review.
    """
    arr = np.array(image)
    alpha = arr[..., 3]
    if spill_mask is None:
        spill_mask = np.zeros(alpha.shape, dtype=bool)
    else:
        spill_mask = np.asarray(spill_mask, dtype=bool)
        if spill_mask.shape != alpha.shape:
            raise ValueError('Spill mask must match the exact frame canvas')
    if alpha.max() == 0:
        raise ValueError('Empty subject')
    if alpha.min() > 0:
        raise ValueError('No transparent canvas; cannot infer a cut-out')
    core = (alpha >= 240) & ~chroma(arr[..., :3]) & ~spill_mask
    core = binary_erosion(core, iterations=1, border_value=0)
    if not core.any():
        raise ValueError('No uncontaminated opaque interior; repair needs source review')
    if erosion:
        # Pillow min filter repeats boundary pixels; explicit zero padding prevents clipping survival.
        padded = Image.new('L', (image.width + 2 * erosion, image.height + 2 * erosion))
        padded.paste(image.getchannel('A'), (erosion, erosion))
        alpha_out = np.asarray(padded.filter(ImageFilter.MinFilter(2 * erosion + 1))
                               .crop((erosion, erosion, image.width + erosion, image.height + erosion)))
    else:
        alpha_out = alpha.copy()
    if not alpha_out.any():
        raise ValueError('Erosion would erase subject')
    _, nearest = distance_transform_edt(~core, return_indices=True)
    # A vivid green field inside the painted object is not key spill.
    # Limit opaque recolouring to the two-pixel original boundary band.
    boundary = ~binary_erosion(alpha >= 240, iterations=2, border_value=0)
    rim = (alpha_out < 255) | ((alpha_out > 0) & chroma(arr[..., :3]) & boundary) | spill_mask
    arr[..., :3][rim] = arr[nearest[0][rim], nearest[1][rim], :3]
    arr[..., 3] = alpha_out
    return Image.fromarray(arr, 'RGBA')


def size_check(
    image: Image.Image,
    profile: str,
    count: int = 1,
    margin: Optional[int] = None,
    canvas: Optional[Sequence[int]] = None,
) -> List[str]:
    w, h, default_margin = PROFILES[profile]
    if canvas:
        w, h = canvas
    minimum = default_margin if margin is None else margin
    findings = []
    accepted = [(w, h)] if canvas else [(int(a[0]), int(a[1])) for a in PROFILE_DATA[profile]['accepted']]
    if image.size not in [(aw * count, ah) for aw, ah in accepted]:
        findings.append(f'canvas {image.size}, expected {(w * count, h)}'
                        + (f' or one of {accepted[1:]}' if len(accepted) > 1 else ''))
    for i, frame in enumerate(frames(image, count)):
        bbox = frame.getchannel('A').point(lambda x: 255 if x >= 16 else 0).getbbox()
        if not bbox:
            findings.append(f'frame {i + 1}: empty subject')
            continue
        margins = [bbox[0], bbox[1], frame.width - bbox[2], frame.height - bbox[3]]
        if min(margins) < minimum:
            findings.append(f'frame {i + 1}: margins L/T/R/B {margins}, minimum {minimum}')
        if profile in ('focus', 'decision', 'category', 'idea'):
            fill = max((bbox[2] - bbox[0]) / frame.width, (bbox[3] - bbox[1]) / frame.height)
            if fill < .80:
                findings.append(f'frame {i + 1}: subject span {fill:.1%}; review undersized artwork')
    return findings


def counter_check(image: Image.Image, surface: str, reference: Image.Image) -> List[str]:
    """Heuristic triage, always compared to the exact installed vanilla DDS."""
    findings = []
    if image.size != reference.size:
        findings.append(f'canvas {image.size}, reference {reference.size}')
    expected_count = 2
    art, alternate = frames(image, expected_count)
    ref_art, ref_alt = frames(reference, expected_count)
    def solid_pixels(frame: Image.Image) -> Any:
        a = np.asarray(frame)
        return a[..., :3][a[..., 3] >= 200].astype(float)
    subject = solid_pixels(art)
    ref = solid_pixels(ref_art)
    if not subject.size or not ref.size:
        return findings + ['normal frame or reference lacks opaque subject']
    alpha = alpha_stats(art)
    reference_alpha = alpha_stats(ref_art)
    # Vanilla's antialiased silhouettes can themselves average below 200.
    # The dedicated alpha command retains the user's literal 200 threshold;
    # convention QA compares like-for-like against this exact reference.
    if alpha['alpha_max'] < 200 or alpha['subject_alpha_mean'] < reference_alpha['subject_alpha_mean'] - 25:
        findings.append('normal frame opacity substantially below the supplied vanilla reference')
    if surface == 'large':
        # Median palette distance catches painted/full-colour replacements without forcing one arbitrary green.
        distance = float(np.linalg.norm(np.median(subject, axis=0) - np.median(ref, axis=0)))
        if distance > 45:
            findings.append(f'normal frame palette differs from vanilla: RGB distance {distance:.1f}')
        spread = float(np.percentile(np.ptp(subject, axis=0), 80))
        reference_spread = float(np.percentile(np.ptp(ref, axis=0), 80))
        if spread > reference_spread + 30:
            findings.append('normal frame broad colour range; review flat green silhouette convention')
    else:
        grey = (np.ptp(subject, axis=1) < 25) & (subject.mean(axis=1) >= 160)
        if grey.mean() < .70:
            findings.append('small normal frame is not predominantly light grey/white')
    alt = np.asarray(alternate)
    opaque = alt[..., 3] >= 200
    white = opaque & (alt[..., :3].min(axis=2) > 170)
    black = opaque & (alt[..., :3].max(axis=2) < 85)
    if white.sum() < 8 or black.sum() < 4:
        findings.append('alternate frame lacks opaque white NATO field or black line glyph')
    def field_shape(frame: Image.Image) -> Tuple[float, float, int]:
        pixels = np.asarray(frame)
        mask = (pixels[..., 3] >= 200) & ((pixels[..., :3].min(axis=2) > 170)
                                        | (pixels[..., :3].max(axis=2) < 85))
        components, count = label(mask, np.ones((3, 3), dtype=bool))
        if not count:
            return 0, 0, 0
        areas = np.bincount(components.ravel())
        areas[0] = 0
        component = components == int(areas.argmax())
        ys, xs = np.where(component)
        width, height = int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
        return float(component.sum() / (width * height)), width / height, int(component.sum())
    density, aspect, area = field_shape(alternate)
    ref_density, ref_aspect, ref_area = field_shape(ref_alt)
    if area < ref_area * .25 or density < ref_density * .70 or abs(aspect - ref_aspect) > .60:
        findings.append('alternate frame lacks a coherent rectangular NATO field comparable to vanilla')
    if art.tobytes() == alternate.tobytes():
        findings.append('two frames are identical')
    return findings


def sprite_registry(root: Union[str, Path]) -> List[Dict[str, Any]]:
    """Bounded text registry reader for sheet/inventory tools, never a script rewrite."""
    entries = []
    for path in sorted((Path(root) / 'interface').rglob('*.gfx')):
        source = path.read_text(encoding='utf-8-sig')
        # Keep hashes inside quoted strings; comments cannot contain braces for scanning.
        source = re.sub(r'"[^"\n]*"|#[^\n]*', lambda m: m[0] if m[0].startswith('"') else '', source)
        for match in re.finditer(r'(?:spriteType|frameAnimatedSpriteType|corneredTileSpriteType)\s*=\s*\{', source, re.I):
            # Comment removal keeps every newline, so offsets still map to source lines.
            line = source.count('\n', 0, match.start()) + 1
            depth, end = 1, match.end()
            quoted = False
            while end < len(source) and depth:
                char = source[end]
                if char == '"':
                    quoted = not quoted
                if not quoted:
                    depth += (char == '{') - (char == '}')
                end += 1
            block = source[match.end():end]
            name = re.search(r'\bname\s*=\s*"?([\w.-]+)', block, re.I)
            texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', block, re.I)
            count = re.search(r'\bnoOfFrames\s*=\s*(\d+)', block, re.I)
            if name and texture:
                basename = path.stem
                group = basename[:3] if re.match(r'\d{3}_', basename) else ('shared_' + basename if SETTINGS['shared_registry_prefix'] and basename.startswith(SETTINGS['shared_registry_prefix']) else basename)
                entries.append({'group': group, 'sprite': name[1], 'texture': texture[1].replace('//', '/'),
                                'frames': int(count[1]) if count else 1, 'registry': path.relative_to(root).as_posix(),
                                'line': line})
    return entries


# ---------------------------------------------------------------------------
# Repository-wide read-only conformance checks (`sprites`, `flags`, `achievements`, `binaries`, `audit`).
# They follow the `.tools/lib/report.py` contract. Each rule cites its source:
# - GFX-FRAME-WIDTH (warning): a horizontal strip is sliced into `noOfFrames` equal frames, so an uneven
#   width shifts every later frame (vanilla `building_icon_strip.dds`: 1426 px / 31 frames = 46 px). Vanilla
#   itself ships 79 of 1798 multi-frame sprites with uneven widths, so the engine tolerates it and the
#   message gives the per-frame width for review.
# - GFX-FLAG-SIZE (error): normal, medium and small flags are 82x52, 41x26 and 10x7 (event-assets skill flag
#   rules; 2202 of 2203 vanilla files per folder).
# - GFX-FLAG-LADDER (warning): the skill requires all three sizes before a flag is complete, but vanilla
#   ships incomplete ladders (89 normal flags without a small file), so a gap is not an engine failure.
# - GFX-FLAG-ORIGIN (warning): the skill forbids top-origin flag TGAs; vanilla ships 5 of 2,203, so the
#   engine loads them and the rule stays a warning.
# - GFX-ACHIEVEMENT-SIZE (error): achievement art is 64x64 (882 of 882 vanilla files;
#   `process_achievement_icons.py`). The base, `_grey` and `_not_eligible` files of every defined
#   achievement are already required by `audit_asset_wiring_static.py` (implicit achievement-art rule).
# - GFX-LFS-POINTER and GFX-TRUNCATED (error): a runtime binary must hold real data. Header parsing accepts
#   legacy, DX10, compressed and mipmapped DDS, which the game loads, rather than requiring Pillow support.
# ---------------------------------------------------------------------------

LFS_POINTER = b'version https://git-lfs.github.com/spec/v1'
FLAG_LADDER = {'': (82, 52), 'medium': (41, 26), 'small': (10, 7)}
ACHIEVEMENT_SIZE = (64, 64)
RUNTIME_BINARY_DIRS = ('gfx', 'sound', 'music')
RUNTIME_BINARY_SUFFIXES = {'.dds', '.tga', '.png', '.mesh', '.anim', '.wav', '.ogg'}
GFX_LEVELS = {
    'GFX-FRAME-WIDTH': 'warning', 'GFX-FLAG-SIZE': 'error', 'GFX-FLAG-LADDER': 'warning', 'GFX-FLAG-ORIGIN': 'warning',
    'GFX-ACHIEVEMENT-SIZE': 'error', 'GFX-LFS-POINTER': 'error', 'GFX-TRUNCATED': 'error',
}
# Bytes per 4x4 block (compressed) or per pixel (uncompressed) for DDS formats with a known payload size.
DDS_BLOCK_BYTES = {b'DXT1': 8, b'DXT2': 16, b'DXT3': 16, b'DXT4': 16, b'DXT5': 16, b'ATI1': 8, b'BC4U': 8, b'ATI2': 16, b'BC5U': 16}
DXGI_BLOCK_BYTES = {71: 8, 72: 8, 74: 16, 75: 16, 77: 16, 78: 16, 80: 8, 81: 8, 83: 16, 84: 16, 98: 16, 99: 16}
DXGI_PIXEL_BYTES = {28: 4, 29: 4, 87: 4, 91: 4}


def gfx_finding(rule: str, path: str, line: int, message: str, check: str = 'gfx') -> Finding:
    return Finding(check, rule, GFX_LEVELS[rule], report_relative(path), line, message)


def header_size(path: Union[str, Path]) -> Tuple[int, int]:
    """Return (width, height) from the file header without decoding pixels."""
    raw = Path(path).read_bytes()[:64]
    if raw.startswith(LFS_POINTER):
        raise ValueError('Git LFS pointer, not image data')
    if raw[:4] == b'DDS ' and len(raw) >= 20:
        height, width = struct.unpack_from('<2I', raw, 12)
        return width, height
    if raw[:8] == b'\x89PNG\r\n\x1a\n' and len(raw) >= 24:
        return struct.unpack_from('>2I', raw, 16)
    if Path(path).suffix.lower() == '.tga' and len(raw) >= 18:
        return struct.unpack_from('<2H', raw, 12)
    with Image.open(path) as image:
        return cast(Tuple[int, int], image.size)


def dds_payload_bytes(header: bytes) -> Optional[int]:
    """Minimum payload length for a DDS header, or None when the format's size is not known here."""
    height, width = struct.unpack_from('<2I', header, 12)
    flags, mips = struct.unpack_from('<I', header, 8)[0], struct.unpack_from('<I', header, 28)[0]
    pf_flags, fourcc, bit_count = struct.unpack_from('<I', header, 80)[0], header[84:88], struct.unpack_from('<I', header, 88)[0]
    caps2 = struct.unpack_from('<I', header, 112)[0]
    levels = mips if flags & 0x20000 and mips else 1
    block = pixel = None
    if pf_flags & 0x4 and fourcc == b'DX10':
        if len(header) < 148 or struct.unpack_from('<I', header, 140)[0] != 1:
            return None  # texture arrays are outside the runtime formats checked here
        dxgi = struct.unpack_from('<I', header, 128)[0]
        block, pixel = DXGI_BLOCK_BYTES.get(dxgi), DXGI_PIXEL_BYTES.get(dxgi)
    elif pf_flags & 0x4:
        block = DDS_BLOCK_BYTES.get(fourcc)
    elif pf_flags & 0x40 and bit_count % 8 == 0:
        pixel = bit_count // 8
    if caps2 & 0x200 or (block is None and pixel is None):
        return None  # cube maps and unlisted formats
    total = 0
    for level in range(levels):
        w, h = max(1, width >> level), max(1, height >> level)
        total += ((w + 3) // 4) * ((h + 3) // 4) * block if block else w * h * pixel
    return total


def binary_problem(path: Union[str, Path]) -> Optional[Tuple[str, str]]:
    """Return (rule, message) when a runtime binary is not usable data, else None."""
    path = Path(path)
    size = path.stat().st_size
    with path.open('rb') as stream:
        head = stream.read(160)
    if head.startswith(LFS_POINTER):
        return 'GFX-LFS-POINTER', 'is a Git LFS pointer, not the binary; run git lfs checkout for this path'
    suffix = path.suffix.lower()
    if suffix == '.dds':
        if head[:4] != b'DDS ' or size < 128:
            return 'GFX-TRUNCATED', 'has no complete DDS header'
        header_length = 148 if head[84:88] == b'DX10' else 128
        payload = dds_payload_bytes(head)
        if payload is not None and size < header_length + payload:
            return 'GFX-TRUNCATED', f'holds {size} bytes; its DDS header needs at least {header_length + payload}'
    elif suffix == '.tga':
        if size < 18:
            return 'GFX-TRUNCATED', 'has no complete TGA header'
        id_length, colour_map_type, image_type = head[0], head[1], head[2]
        width, height = struct.unpack_from('<2H', head, 12)
        if image_type in (2, 3) and colour_map_type == 0:
            needed = 18 + id_length + width * height * (head[16] // 8)
            if size < needed:
                return 'GFX-TRUNCATED', f'holds {size} bytes; its TGA header needs at least {needed}'
    elif suffix == '.png' and head[:8] != b'\x89PNG\r\n\x1a\n':
        return 'GFX-TRUNCATED', 'does not start with the PNG signature'
    elif suffix == '.wav' and not (head[:4] == b'RIFF' and head[8:12] == b'WAVE'):
        return 'GFX-TRUNCATED', 'does not start with a RIFF/WAVE header'
    elif suffix == '.ogg' and head[:4] != b'OggS':
        return 'GFX-TRUNCATED', 'does not start with an Ogg page header'
    return None


def check_binaries(root: Union[str, Path] = ROOT, paths: Optional[Sequence[str]] = None) -> List[Finding]:
    selector, findings = PathFilter(paths), []
    for folder in RUNTIME_BINARY_DIRS:
        base = Path(root) / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob('*')):
            if path.suffix.lower() not in RUNTIME_BINARY_SUFFIXES or not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if not selector.matches(rel):
                continue
            problem = binary_problem(path)
            if problem:
                findings.append(gfx_finding(problem[0], rel, 0, f'{rel} {problem[1]}'))
    return findings


def resolve_texture(texture: str, root: Union[str, Path], vanilla: Union[str, Path]) -> Optional[Path]:
    """Find a registered texture in the mod, then vanilla; a `.tga` reference also matches a same-stem `.dds`."""
    for base in (Path(root), Path(vanilla)):
        for candidate in (texture, texture[:-4] + '.dds' if texture.lower().endswith('.tga') else None):
            if candidate and (base / candidate).is_file():
                return base / candidate
    return None


def check_sprites(
    root: Union[str, Path] = ROOT,
    paths: Optional[Sequence[str]] = None,
    vanilla: Optional[Union[str, Path]] = None,
) -> List[Finding]:
    selector, findings = PathFilter(paths), []
    vanilla = vanilla or game_dir()
    for entry in sprite_registry(root):
        if entry['frames'] <= 1:
            continue
        if paths and not (selector.matches(entry['registry']) or selector.matches(entry['texture'])):
            continue
        texture = resolve_texture(entry['texture'], root, vanilla)
        if texture is None:
            continue  # a missing texture is reported by audit_asset_wiring_static.py
        try:
            width, _ = header_size(texture)
        except (OSError, ValueError, struct.error):
            continue  # unreadable binaries are reported by the binaries check
        if width % entry['frames']:
            findings.append(gfx_finding('GFX-FRAME-WIDTH', entry['registry'], entry['line'],
                f"{entry['sprite']}: {entry['texture']} is {width} px wide, which does not divide into "
                f"noOfFrames = {entry['frames']} ({width / entry['frames']:.2f} px per frame)"))
    return findings


def check_flags(root: Union[str, Path] = ROOT, paths: Optional[Sequence[str]] = None) -> List[Finding]:
    selector, findings, stems = PathFilter(paths), [], {}
    for folder in FLAG_LADDER:
        base = Path(root) / 'gfx' / 'flags' / folder
        stems[folder] = {p.stem: p for p in base.glob('*.tga')} if base.is_dir() else {}
    for folder, (want_w, want_h) in FLAG_LADDER.items():
        for stem, path in sorted(stems[folder].items()):
            rel = path.relative_to(root).as_posix()
            if not selector.matches(rel):
                continue
            label = folder or 'normal'
            try:
                width, height = header_size(path)
            except (OSError, ValueError, struct.error) as error:
                findings.append(gfx_finding('GFX-FLAG-SIZE', rel, 0, f'{label} flag {stem} cannot be read: {error}'))
                continue
            if (width, height) != (want_w, want_h):
                findings.append(gfx_finding('GFX-FLAG-SIZE', rel, 0, f'{label} flag {stem} is {width}x{height}, not {want_w}x{want_h}'))
            missing = [other or 'normal' for other in FLAG_LADDER if other != folder and stem not in stems[other]]
            if missing:
                findings.append(gfx_finding('GFX-FLAG-LADDER', rel, 0, f'{label} flag {stem} has no {" or ".join(missing)} size'))
            if path.read_bytes()[17:18] and path.read_bytes()[17] & 0x20:
                findings.append(gfx_finding('GFX-FLAG-ORIGIN', rel, 0, f'{label} flag {stem} is stored top-origin'))
    return findings


def check_achievements(root: Union[str, Path] = ROOT, paths: Optional[Sequence[str]] = None) -> List[Finding]:
    selector, findings = PathFilter(paths), []
    base = Path(root) / 'gfx' / 'achievements'
    files = {p.stem: p for p in base.glob('*.dds')} if base.is_dir() else {}
    for stem, path in sorted(files.items()):
        rel = path.relative_to(root).as_posix()
        if not selector.matches(rel):
            continue
        try:
            size = header_size(path)
        except (OSError, ValueError, struct.error):
            continue  # unreadable binaries are reported by the binaries check
        if tuple(size) != ACHIEVEMENT_SIZE:
            findings.append(gfx_finding('GFX-ACHIEVEMENT-SIZE', rel, 0, f'achievement art {stem} is {size[0]}x{size[1]}, not 64x64'))
    return findings


# ---------------------------------------------------------------------------
# Family checks and report-image provenance.
# Consumers come from the asset audit's implicit-lookup extractors: focus `icon =` sprites, decision
# `icon =` sprites and idea pictures. Only textures stored in the checked tree are measured, so a mod
# that reuses vanilla art is not judged on vanilla files.
# - GFX-FOCUS-SIZE (error), GFX-DECISION-SIZE and GFX-IDEA-SIZE (warning): the frame canvas is not one of
#   the profile's accepted sizes (profiles.json). A family without a profile row is not checked.
# - GFX-FOCUS-ALTERNATIVE: a 100x88 focus icon; a warning for files under --paths (new or changed art)
#   and a review item otherwise, because new focus art uses the profile canvas.
# - GFX-OPAQUE-CANVAS (error): all four corners of a frame are fully opaque, so the unused canvas has a
#   background, which the event-assets skill forbids for these families. Calibrated on 25 October 2026:
#   0 of 4,440 vanilla focus, decision and idea textures match. A partly transparent outer ring is not a
#   finding, because 56-84% of vanilla icons reach the canvas edge.
# - GFX-EMPTY-SUBJECT (error): a frame has no visible pixel.
# - GFX-GHOSTED (warning, focus icons only): visible pixels average below alpha 200; vanilla infantry counters
#   average 162-164, so it is never an error. The
#   calibration found it on 5.5% of vanilla focus icons but 88% of decision and 48% of idea icons, whose
#   small antialiased art is normally that faint, so those families are not checked.
# - GFX-CHROMA-FRINGE (warning): edge pixels in the magenta or green key colours used by `defringe`.
# Report images (210x176 files under gfx/event_pictures):
# - GFX-REPORT-PROVENANCE-MISMATCH (error): the runtime pixels differ from the recorded processed output.
# - GFX-REPORT-RECIPE-MISMATCH (error): rerunning the recorded recipe on the recorded source, which still
#   exists with its recorded hash, gives different pixels.
# - GFX-REPORT-NO-PROVENANCE (warning): no record in the provenance registry, so only size and corners
#   can be checked.
# - GFX-REPORT-OPAQUE-CORNERS (warning): a corner is opaque, so the report-card treatment (tilt and
#   transparent edge space) is missing.
# - GFX-REPORT-STALE-PROVENANCE (warning): a record names a runtime file that no longer exists.
# ---------------------------------------------------------------------------

FAMILY_RULES = {'focus': 'GFX-FOCUS-SIZE', 'decision': 'GFX-DECISION-SIZE', 'idea': 'GFX-IDEA-SIZE'}
REPORT_PROVENANCE = ROOT / json.loads((ASSET_TOOLS / 'project_settings.json').read_text(encoding='utf-8'))['report_provenance']
REPORT_PROCESSOR = ASSET_TOOLS / 'process_report_event_image.py'
GFX_LEVELS.update({
    'GFX-FOCUS-SIZE': 'error', 'GFX-DECISION-SIZE': 'warning', 'GFX-IDEA-SIZE': 'warning',
    'GFX-FOCUS-ALTERNATIVE': 'warning', 'GFX-OPAQUE-CANVAS': 'error', 'GFX-EMPTY-SUBJECT': 'error',
    'GFX-GHOSTED': 'warning', 'GFX-CHROMA-FRINGE': 'warning',
    'GFX-REPORT-PROVENANCE-MISMATCH': 'error', 'GFX-REPORT-RECIPE-MISMATCH': 'error',
    'GFX-REPORT-NO-PROVENANCE': 'warning', 'GFX-REPORT-OPAQUE-CORNERS': 'warning',
    'GFX-REPORT-STALE-PROVENANCE': 'warning',
})


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dx10_uncompressed(path: Path) -> Image.Image:
    """Decode the top level of an uncompressed DX10 DDS (BGRA or RGBA, sRGB or not), which Pillow refuses."""
    raw = Path(path).read_bytes()
    if raw[:4] != b'DDS ' or raw[84:88] != b'DX10' or len(raw) < 148:
        raise ValueError('not a DX10 DDS')
    height, width = struct.unpack_from('<2I', raw, 12)
    dxgi = struct.unpack_from('<I', raw, 128)[0]
    modes = {87: 'BGRA', 91: 'BGRA', 28: 'RGBA', 29: 'RGBA'}
    if dxgi not in modes or len(raw) < 148 + width * height * 4:
        raise ValueError(f'unsupported DX10 format {dxgi}')
    return Image.frombytes('RGBA', (width, height), raw[148:148 + width * height * 4], 'raw', modes[dxgi])


def decode_any(path: Path) -> Optional[Image.Image]:
    """Decode a texture with Pillow, the strict BGRA reader or the DX10 reader; None when none can."""
    for reader in (load, lambda p: strict_dds(p).convert('RGBA'), dx10_uncompressed):
        try:
            return reader(path)
        except (OSError, ValueError, struct.error, NotImplementedError):
            continue
    return None


def pixels_sha256(image: Image.Image) -> str:
    return hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()


def family_textures(root: Path, vanilla: Path) -> List[Dict[str, Any]]:
    """Return one entry per texture that a focus, decision or idea consumer in `root` displays."""
    audit = load_module('asset_wiring_audit', ROOT / '.tools' / 'audits' / 'audit_asset_wiring_static.py')
    consumers: Dict[str, str] = {}
    for row in audit.expect_focus_shine(root):
        consumers.setdefault(str(row['expected'])[:-len('_shine')], 'focus')
    for row in audit.expect_decisions(root):
        consumers.setdefault(str(row['expected']), 'decision')
    for row in audit.expect_ideas(root):
        consumers.setdefault(str(row['expected']), 'idea')
    registry = {str(entry['sprite']): entry for entry in sprite_registry(root)}
    textures: Dict[Path, Dict[str, Any]] = {}
    for sprite, family in sorted(consumers.items()):
        entry = registry.get(sprite)
        if entry is None or family not in PROFILE_DATA:
            continue
        texture = resolve_texture(str(entry['texture']), root, vanilla)
        if texture is None or Path(root).resolve() not in texture.resolve().parents:
            continue
        textures.setdefault(texture, {'family': family, 'sprite': sprite, 'texture': texture,
                                      'path': texture.relative_to(root).as_posix(), 'frames': int(entry['frames'])})
    return list(textures.values())


def family_findings(item: Dict[str, Any], changed: bool) -> Tuple[List[Finding], Dict[str, bool]]:
    """Return the findings for one family texture and the per-rule outcome used by calibration."""
    family, rel = str(item['family']), str(item['path'])
    image = decode_any(Path(item['texture']))
    if image is None:
        return [], {'unreadable': True}
    count = int(item['frames']) if int(item['frames']) > 0 and image.width % int(item['frames']) == 0 else 1
    width, height = image.width // count, image.height
    profile = PROFILE_DATA[family]
    accepted = [(int(a[0]), int(a[1])) for a in profile['accepted']]
    canvas = (int(profile['canvas'][0]), int(profile['canvas'][1]))
    findings: List[Finding] = []
    outcome = {'size_ok': (width, height) in accepted, 'alternative': (width, height) in accepted and (width, height) != canvas}
    if not outcome['size_ok']:
        rule = FAMILY_RULES[family]
        findings.append(Finding('gfx', rule, str(profile['off_size_level']), rel, 0,
                                f"{family} art for {item['sprite']} is {width}x{height}; accepted {accepted} (profiles.json)"))
    elif outcome['alternative'] and family == 'focus':
        findings.append(Finding('gfx', 'GFX-FOCUS-ALTERNATIVE', 'warning' if changed else 'review', rel, 0,
                                f"focus art for {item['sprite']} is {width}x{height}; new focus art uses {canvas[0]}x{canvas[1]} (profiles.json)"))
    opaque = empty = ghosted = fringe = False
    for frame in frames(image, count):
        alpha = np.asarray(frame)[..., 3]
        if int(alpha.max()) == 0:
            empty = True
            continue
        corners = (alpha[0, 0], alpha[0, -1], alpha[-1, 0], alpha[-1, -1])
        opaque = opaque or min(int(c) for c in corners) == 255
        ghosted = ghosted or (family == 'focus' and bool(alpha_stats(frame)['ghosted']))
        fringe = fringe or edge_stats(frame)['chroma_edge_pixels'] > 0
    outcome.update({'opaque_canvas': opaque, 'empty': empty, 'ghosted': ghosted, 'fringe': fringe})
    for flag, rule, message in (
            (empty, 'GFX-EMPTY-SUBJECT', 'a frame has no visible pixel'),
            (opaque, 'GFX-OPAQUE-CANVAS', 'all four corners are fully opaque, so the unused canvas has a background'),
            (ghosted, 'GFX-GHOSTED', 'visible pixels average below alpha 200'),
            (fringe, 'GFX-CHROMA-FRINGE', 'edge pixels carry magenta or green key colour')):
        if flag:
            findings.append(gfx_finding(rule, rel, 0, f"{family} art for {item['sprite']}: {message}"))
    return findings, outcome


def check_families(root: Path = ROOT, paths: Optional[List[str]] = None, vanilla: Optional[Path] = None) -> List[Finding]:
    selector, findings = PathFilter(paths), []
    for item in family_textures(root, vanilla or game_dir()):
        if paths and not selector.matches(str(item['path'])):
            continue
        findings += family_findings(item, bool(paths))[0]
    return findings


def calibrate_families(vanilla: Path) -> int:
    """Measure every family rule against the installed vanilla tree (positive control for each rule)."""
    totals: Dict[str, Dict[str, int]] = {}
    for item in family_textures(vanilla, vanilla):
        _, outcome = family_findings(item, False)
        bucket = totals.setdefault(str(item['family']), {})
        bucket['files'] = bucket.get('files', 0) + 1
        for key, value in outcome.items():
            bucket[key] = bucket.get(key, 0) + int(bool(value))
    for family, bucket in sorted(totals.items()):
        files = bucket['files']
        readable = files - bucket.get('unreadable', 0)
        print(f"{family}: {files} vanilla textures, {readable} readable")
        for key in ('size_ok', 'alternative', 'opaque_canvas', 'empty', 'ghosted', 'fringe'):
            print(f"  {key:12s} {bucket.get(key, 0):5d}  ({bucket.get(key, 0) / max(readable, 1):.1%})")
    return 0


def check_reports(root: Path = ROOT, paths: Optional[List[str]] = None) -> List[Finding]:
    selector, findings = PathFilter(paths), []
    records: Dict[str, Dict[str, Any]] = json.loads(REPORT_PROVENANCE.read_text(encoding='utf-8'))['records'] \
        if REPORT_PROVENANCE.is_file() else {}
    base = Path(root) / 'gfx' / 'event_pictures'
    candidates = sorted(p for p in base.rglob('*') if p.suffix.lower() in ('.dds', '.tga', '.png') and p.is_file()) \
        if base.is_dir() else []
    for path in candidates:
        rel = path.relative_to(root).as_posix()
        if not selector.matches(rel):
            continue
        try:
            if tuple(header_size(path)) != (210, 176):
                continue
        except (OSError, ValueError, struct.error):
            continue
        image = decode_any(path)
        if image is None:
            continue
        record = records.get(rel)
        if record is None:
            findings.append(gfx_finding('GFX-REPORT-NO-PROVENANCE', rel, 0,
                                        'no processing record; only size and transparent corners can be checked'))
            alpha = image.getchannel('A')
            if any(alpha.getpixel(xy) for xy in ((0, 0), (209, 0), (0, 175), (209, 175))):
                findings.append(gfx_finding('GFX-REPORT-OPAQUE-CORNERS', rel, 0,
                                            'a corner is opaque, so the report-card tilt and transparent edge space are missing'))
            continue
        if pixels_sha256(image) != record['pixels_sha256']:
            findings.append(gfx_finding('GFX-REPORT-PROVENANCE-MISMATCH', rel, 0,
                                        'runtime pixels differ from the recorded processed output'))
        source = Path(root) / str(record['source']['path'])
        if source.is_file() and digest(source) == record['source']['sha256']:
            processor = load_module('report_processor', REPORT_PROCESSOR)
            with tempfile.TemporaryDirectory() as folder:
                rerun = Path(folder) / 'rerun.png'
                processor.process_report_event_image(input_path=source, output_path=rerun, **record_arguments(record))
                if pixels_sha256(load(rerun)) != record['pixels_sha256']:
                    findings.append(gfx_finding('GFX-REPORT-RECIPE-MISMATCH', rel, 0,
                                                'rerunning the recorded recipe on the recorded source gives different pixels'))
    for rel in sorted(records):
        if not (Path(root) / rel).is_file() and selector.matches(rel):
            findings.append(gfx_finding('GFX-REPORT-STALE-PROVENANCE', rel, 0, 'the provenance record names a missing runtime file'))
    return findings


def record_arguments(record: Dict[str, Any]) -> Dict[str, Any]:
    """Recorded processor arguments with tuple-typed values restored."""
    arguments = dict(record['arguments'])
    for key in ('canvas_size', 'card_size', 'shadow_offset'):
        arguments[key] = tuple(arguments[key])
    return arguments


CONFORMANCE_CHECKS: Dict[str, Callable[..., List[Finding]]] = {
    'sprites': check_sprites, 'flags': check_flags, 'achievements': check_achievements, 'binaries': check_binaries,
    'families': check_families, 'reports': check_reports,
}


def run_conformance(command: str, args: argparse.Namespace) -> int:
    if getattr(args, 'calibrate_vanilla', False):
        return calibrate_families(game_dir())
    paths = requested_paths(args)
    chosen = CONFORMANCE_CHECKS if command == 'audit' else {command: CONFORMANCE_CHECKS[command]}
    findings = sorted((f for check in chosen.values() for f in check(ROOT, paths)),
                      key=lambda f: (f.path, f.line, f.rule, f.message))
    print_findings('gfx', findings)
    if args.json:
        merge_json(Path(args.json), findings, GFX_LEVELS)
    return exit_code(findings, args.fail_on)


def sheet(entries: List[Dict[str, Any]], root: Union[str, Path], out: Union[str, Path], label: str = 'review') -> List[str]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in entries:
        grouped.setdefault(item['group'], []).append(item)
    artifacts = []
    for group, items in grouped.items():
        for start in range(0, len(items), 24):
            chunk = items[start:start + 24]
            cell_w, cell_h = 280, 220
            canvas = Image.new('RGB', (cell_w * 4, cell_h * math.ceil(len(chunk) / 4)), '#181818')
            draw = ImageDraw.Draw(canvas)
            for n, entry in enumerate(chunk):
                x, y = n % 4 * cell_w, n // 4 * cell_h
                try:
                    source = load(Path(root) / entry['texture'])
                    native = frames(source, entry['frames'])[0]
                    bg = Image.new('RGBA', (cell_w - 8, 170), '#5c5c5c')
                    bd = ImageDraw.Draw(bg)
                    for cy in range(0, 170, 8):
                        for cx in range(0, cell_w - 8, 8):
                            if (cx // 8 + cy // 8) % 2:
                                bd.rectangle((cx, cy, cx + 7, cy + 7), fill='#787878')
                    # Native view plus enlarged smooth preview; show every frame in separate tiles if requested by caller.
                    enlarged = native.copy()
                    enlarged.thumbnail((150, 155))
                    if native.width <= 94 and native.height <= 86:
                        enlarged = native.resize((native.width * 2, native.height * 2), Image.Resampling.BICUBIC)
                        enlarged.thumbnail((150, 155))
                    bg.alpha_composite(native, (2, max(0, (170 - native.height) // 2))) if native.width <= 110 and native.height <= 170 else None
                    bg.alpha_composite(enlarged, (116, (170 - enlarged.height) // 2))
                    canvas.paste(bg.convert('RGB'), (x + 4, y + 4))
                    stats = alpha_stats(native)
                    caption = f'{source.width}x{source.height}, {entry["frames"]}f, alpha {stats["subject_alpha_mean"]}'
                except Exception as error:  # noqa: BLE001 - one unreadable texture must not stop the review sheet
                    caption = f'ERROR: {error}'
                draw.text((x + 4, y + 178), entry['sprite'].removeprefix('GFX_')[:42], fill='white')
                draw.text((x + 4, y + 192), caption[:44], fill='#c9b890')
            path = out / f'{group}_{label}_{start // 24 + 1}.png'
            canvas.save(path)
            artifacts.append(str(path))
    return artifacts


def input_items(args: argparse.Namespace) -> List[Tuple[Path, int]]:
    items = [(Path(p), args.frames or 1) for p in args.inputs]
    if args.list:
        data = json.loads(Path(args.list).read_text(encoding='utf-8-sig'))
        rows = data if isinstance(data, list) else data['assets']
        for row in rows:
            path = Path(row if isinstance(row, str) else row.get('texture', row.get('path')))
            count = args.frames if args.frames is not None else (1 if isinstance(row, str) else row.get('frames', 1))
            items.append((path, int(count)))
    if not items:
        raise ValueError('Supply explicit image paths or --list; no implicit whole-repository pass')
    unique: Dict[Path, Tuple[Path, int]] = {}
    for path, count in items:
        key = path.resolve()
        if key in unique and unique[key][1] != count:
            raise ValueError(f'Conflicting declared frame counts for {path}')
        unique[key] = (path, count)
    return list(unique.values())


def add_conformance_parsers(sub: Any) -> None:
    """Add one subcommand per read-only conformance check, plus `audit` for all of them."""
    for command in (*CONFORMANCE_CHECKS, 'audit'):
        p = sub.add_parser(command, help='read-only repository conformance check (see the module comments)')
        p.add_argument('--json', help='also write the findings as JSON')
        add_arguments(p)
        if command == 'families':
            p.add_argument('--calibrate-vanilla', action='store_true', help='measure each family rule against the installed game')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('alpha', 'size', 'defringe', 'dds', 'counter'):
        p = sub.add_parser(command)
        p.add_argument('inputs', nargs='*')
        p.add_argument('--list', help='JSON array of paths or objects with texture/path')
        p.add_argument('--json', help='Write full machine-readable results')
        p.add_argument('--frames', type=int, default=2 if command == 'counter' else None,
                       help='Override horizontal frame count; otherwise use manifest frames or 1 (counter: 2)')
        if command in ('defringe', 'dds'):
            p.add_argument('--out', required=True, help='Separate output directory')
            p.add_argument('--root', default='.', help='Preserve paths relative to this root under output')
            p.add_argument('--force', action='store_true', help='Replace an existing output, never authorizes input overwrite')
        if command == 'defringe':
            p.add_argument('--erosion', type=int, choices=(0, 1), default=1)
            p.add_argument('--spill-mask', help='Reviewed grayscale PNG mask: nonzero pixels explicitly select opaque key spill; exact sheet dimensions')
        if command == 'size':
            p.add_argument('--profile', required=True, choices=PROFILES)
            p.add_argument('--margin', type=int)
            p.add_argument('--canvas', nargs=2, type=int, help='Verified consumer frame canvas W H')
        if command == 'counter':
            p.add_argument('--surface', required=True, choices=('large', 'small'))
            p.add_argument('--reference', required=True, help='Exact vanilla two-frame DDS for this surface')
    p = sub.add_parser('sheet')
    p.add_argument('--root', default=str(ROOT))
    p.add_argument('--groups', nargs='+', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--label', default='review')
    add_conformance_parsers(sub)
    args = parser.parse_args()
    if args.command in CONFORMANCE_CHECKS or args.command == 'audit':
        return run_conformance(args.command, args)
    if args.command == 'counter' and args.frames != 2:
        parser.error('Counter convention checks require exactly two frames')
    if args.command == 'sheet':
        entries = [e for e in sprite_registry(Path(args.root)) if e['group'] in args.groups]
        if not entries:
            parser.error('No matching registered sprites')
        print(json.dumps(sheet(entries, args.root, args.out, args.label), indent=2))
        return 0
    items = input_items(args)
    protected = {path.resolve() for path, _ in items}
    if args.list:
        protected.add(Path(args.list).resolve())
    if getattr(args, 'spill_mask', None):
        protected.add(Path(args.spill_mask).resolve())
    if args.json:
        report_path = Path(args.json).resolve()
        outputs = set()
        if args.command in ('dds', 'defringe'):
            for path, _ in items:
                relative = path.resolve().relative_to(Path(args.root).resolve())
                outputs.add((Path(args.out) / relative).with_suffix('.dds' if args.command == 'dds' else '.png').resolve())
        if report_path in protected | outputs:
            parser.error('--json cannot overwrite an input, input list, or image output')
    rows: List[Dict[str, Any]]
    rows, failed = [], False
    for path, frame_count in items:
        row: Dict[str, Any] = {'path': str(path)}
        try:
            row['sha256'] = digest(path)
            image = load(path)
            row['size'] = list(image.size)
            split = frames(image, frame_count)
            row['frames'] = [dict(alpha_stats(f), **edge_stats(f)) for f in split]
            if args.command == 'alpha':
                row['findings'] = [f'frame {i + 1}: subject alpha mean below 200' for i, f in enumerate(split) if alpha_stats(f)['ghosted']]
            elif args.command == 'size':
                row['findings'] = size_check(image, args.profile, frame_count, args.margin, args.canvas)
            elif args.command == 'counter':
                row['findings'] = counter_check(image, args.surface, load(args.reference))
            else:
                root = Path(args.root).resolve()
                relative = path.resolve().relative_to(root)
                out = (Path(args.out) / relative).with_suffix('.dds' if args.command == 'dds' else '.png')
                if out.resolve() == path.resolve():
                    raise ValueError('Input overwrite forbidden; use separate review output')
                if out.exists() and not args.force:
                    raise FileExistsError(out)
                if args.command == 'defringe':
                    masks = [None] * frame_count
                    if args.spill_mask:
                        mask = load(args.spill_mask)
                        if mask.size != image.size:
                            raise ValueError('Spill mask must match exact sheet canvas')
                        masks = [np.asarray(f.convert('L')) > 0 for f in frames(mask, frame_count)]
                    repaired = [defringe(f, args.erosion, m) for f, m in zip(split, masks)]
                    result = Image.new('RGBA', image.size)
                    for i, f in enumerate(repaired):
                        result.paste(f, (i * f.width, 0))
                    write_png(result, out, args.force)
                else:
                    result = image
                    write_dds(result, out, args.force)
                row['output'] = str(out)
                row['output_sha256'] = digest(out)
                row['after'] = [dict(alpha_stats(f), **edge_stats(f)) for f in frames(result, frame_count)]
                row['findings'] = []
            if row['findings']:
                failed = True
        except Exception as error:  # noqa: BLE001 - every input gets a row; the failure is recorded in it
            row['error'] = str(error)
            failed = True
        rows.append(row)
    if args.json:
        target = Path(args.json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checked': len(rows), 'flagged': sum(bool(r.get('findings') or r.get('error')) for r in rows), 'results': rows}, indent=2))
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
