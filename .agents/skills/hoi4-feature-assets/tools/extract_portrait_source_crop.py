#!/usr/bin/env python3
"""Extract an immutable, exact-pixel archival portrait crop.

This utility is intentionally narrower than the portrait processor.  It uses
Pillow as the single decode and crop backend, preserves the decoded source
mode in a lossless PNG, and compares the reopened PNG against the same
decoded master rectangle in RGBA form before any artifact is committed.  It
does not resize, enhance, recolour, retouch, or otherwise reinterpret source
pixels.

The output PNG and its JSON evidence are committed together.  Existing files
are never replaced unless ``--force`` is explicitly supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import sys
import tempfile
from pathlib import Path
from typing import Iterable

from PIL import Image
from PIL import __version__ as PILLOW_VERSION


TOOL_VERSION = "1.0"
METADATA_SCHEMA = "hoi4-portrait-source-crop-v1"
COMMAND_SCHEMA = "hoi4-normalized-source-crop-command-v1"
COMPARISON_MODE = "RGBA"
SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


def sha256_file(path: Path) -> str:
	"""Return the SHA-256 digest of one file without changing it."""
	digest = hashlib.sha256()
	with path.open("rb") as handle:
		for chunk in iter(lambda: handle.read(1024 * 1024), b""):
			digest.update(chunk)
	return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
	return hashlib.sha256(payload).hexdigest()


def canonical_json_sha256(payload: object) -> str:
	encoded = json.dumps(
		payload,
		sort_keys=True,
		separators=(",", ":"),
		ensure_ascii=False,
	).encode("utf-8")
	return sha256_bytes(encoded)


def normalized_path(path: Path) -> str:
	"""Use a stable repository-relative path, or an absolute POSIX path outside it."""
	resolved = path.expanduser().resolve()
	try:
		return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
	except ValueError:
		return resolved.as_posix()


def validate_crop_box(size: tuple[int, int], crop: Iterable[int]) -> tuple[int, int, int, int]:
	"""Validate Pillow's half-open ``(left, top, right, bottom)`` rectangle."""
	values = tuple(crop)
	if len(values) != 4 or not all(isinstance(value, int) for value in values):
		raise ValueError("Crop must contain four integer coordinates: left top right bottom")
	left, top, right, bottom = values
	width, height = size
	if left < 0 or top < 0 or right > width or bottom > height:
		raise ValueError(
			f"Crop {values} is outside decoded master bounds {width}x{height}"
		)
	if right <= left or bottom <= top:
		raise ValueError(f"Crop {values} must describe a nonempty rectangle")
	return left, top, right, bottom


def decode_image(path: Path) -> tuple[Image.Image, str, tuple[int, int]]:
	"""Decode one image with Pillow and return a detached pixel image."""
	with Image.open(path) as opened:
		opened.load()
		mode = opened.mode
		size = opened.size
		decoded = opened.copy()
	return decoded, mode, size


def rgba_bytes(image: Image.Image) -> bytes:
	return image.convert(COMPARISON_MODE).tobytes()


def rgba_sha256(image: Image.Image) -> str:
	return sha256_bytes(rgba_bytes(image))


def encode_lossless_png(image: Image.Image) -> bytes:
	"""Encode source pixels without a lossy or geometric operation."""
	buffer = io.BytesIO()
	image.save(
		buffer,
		format="PNG",
		optimize=False,
		compress_level=9,
	)
	return buffer.getvalue()


def prepare_file(target: Path, payload: bytes) -> dict[str, object]:
	"""Write a hidden prepared file and return its expected digest."""
	target.parent.mkdir(parents=True, exist_ok=True)
	file_descriptor, temporary_name = tempfile.mkstemp(
		dir=str(target.parent),
		prefix=f".{target.name}.",
		suffix=".prepared",
	)
	temporary = Path(temporary_name)
	try:
		with os.fdopen(file_descriptor, "wb") as handle:
			handle.write(payload)
			handle.flush()
			os.fsync(handle.fileno())
		return {
			"target": target,
			"temporary": temporary,
			"file_sha256": sha256_file(temporary),
		}
	except Exception:
		if temporary.exists():
			temporary.unlink()
		raise


def discard_prepared(prepared: list[dict[str, object]]) -> None:
	for record in prepared:
		temporary = Path(record["temporary"])
		if temporary.exists():
			temporary.unlink()


def commit_prepared(prepared: list[dict[str, object]], force: bool) -> None:
	"""Replace output and evidence as one recoverable transaction."""
	backups: dict[Path, Path] = {}
	committed: list[Path] = []
	try:
		for record in prepared:
			target = Path(record["target"])
			if target.exists() and not force:
				raise FileExistsError(
					f"Write target appeared after validation; refusing replacement: {target}"
				)
		for record in prepared:
			target = Path(record["target"])
			if not target.exists():
				continue
			file_descriptor, backup_name = tempfile.mkstemp(
				dir=str(target.parent),
				prefix=f".{target.name}.",
				suffix=".backup",
			)
			os.close(file_descriptor)
			backup = Path(backup_name)
			backup.unlink()
			os.replace(target, backup)
			backups[target] = backup
		for record in prepared:
			target = Path(record["target"])
			temporary = Path(record["temporary"])
			os.replace(temporary, target)
			committed.append(target)
		for record in prepared:
			target = Path(record["target"])
			if sha256_file(target) != str(record["file_sha256"]):
				raise RuntimeError(f"Committed artifact hash changed: {target}")
	except Exception:
		for target in reversed(committed):
			if target.exists():
				target.unlink()
		for target, backup in backups.items():
			if backup.exists():
				os.replace(backup, target)
		raise
	else:
		for backup in backups.values():
			if backup.exists():
				backup.unlink()
	finally:
		discard_prepared(prepared)


def validate_paths(
	master: Path,
	output: Path,
	metadata: Path,
	force: bool,
) -> tuple[Path, Path, Path]:
	master = master.expanduser().resolve()
	output = output.expanduser().resolve()
	metadata = metadata.expanduser().resolve()
	if not master.is_file():
		raise FileNotFoundError(f"Master image is not a regular file: {master}")
	if output.suffix.lower() != ".png":
		raise ValueError("Output must use the .png suffix")
	if metadata.suffix.lower() != ".json":
		raise ValueError("Metadata must use the .json suffix")
	if len({master, output, metadata}) != 3:
		raise ValueError("Master, output, and metadata paths must be distinct")
	for target in (output, metadata):
		if target.exists() and not target.is_file():
			raise ValueError(f"Write target exists but is not a regular file: {target}")
		if target.exists() and not force:
			raise FileExistsError(
				f"Refusing to replace existing artifact without --force: {target}"
			)
	return master, output, metadata


def normalized_command_record(
	master: Path,
	output: Path,
	metadata: Path,
	crop: tuple[int, int, int, int],
	force: bool,
) -> dict[str, object]:
	arguments = {
		"master": normalized_path(master),
		"output": normalized_path(output),
		"metadata": normalized_path(metadata),
		"crop": list(crop),
		"force": bool(force),
	}
	return {
		"schema": COMMAND_SCHEMA,
		"tool": normalized_path(Path(__file__)),
		"python": {
			"implementation": platform.python_implementation(),
			"version": platform.python_version(),
			"executable_name": Path(sys.executable).name,
		},
		"arguments": arguments,
		"arguments_sha256": canonical_json_sha256(arguments),
	}


def crop_source(
	master_path: Path,
	output_path: Path,
	metadata_path: Path,
	crop: Iterable[int],
	force: bool = False,
) -> dict[str, object]:
	"""Create and verify one exact archival crop plus JSON evidence."""
	master, output, metadata = validate_paths(
		master_path,
		output_path,
		metadata_path,
		force,
	)
	master_file_sha256 = sha256_file(master)
	decoded_master, master_mode, master_size = decode_image(master)
	if sha256_file(master) != master_file_sha256:
		raise RuntimeError("Archival master changed while it was being decoded")
	crop_box = validate_crop_box(master_size, crop)
	source_crop = decoded_master.crop(crop_box)
	payload = encode_lossless_png(source_crop)

	prepared_output: dict[str, object] | None = None
	prepared_metadata: dict[str, object] | None = None
	prepared: list[dict[str, object]] = []
	try:
		prepared_output = prepare_file(output, payload)
		with Image.open(Path(prepared_output["temporary"])) as reopened:
			reopened.load()
			output_mode = reopened.mode
			output_size = reopened.size
			output_rgba = reopened.convert(COMPARISON_MODE)
		output_rgba.load()
		expected_rgba = source_crop.convert(COMPARISON_MODE)
		expected_rgba.load()
		if output_size != source_crop.size or output_rgba.tobytes() != expected_rgba.tobytes():
			raise ValueError(
				"Decoded PNG pixels do not exactly equal the decoded master rectangle"
			)

		master_crop_rgba_sha256 = rgba_sha256(source_crop)
		output_rgba_sha256 = rgba_sha256(output_rgba)
		if master_crop_rgba_sha256 != output_rgba_sha256:
			raise ValueError(
				"Decoded RGBA hashes differ for the master rectangle and output PNG"
			)
		metadata_record: dict[str, object] = {
			"schema": METADATA_SCHEMA,
			"status": "exact_source_crop_verified",
			"tool": {
				"path": normalized_path(Path(__file__)),
				"version": TOOL_VERSION,
				"sha256": sha256_file(Path(__file__)),
			},
			"master": {
				"path": normalized_path(master),
				"file_sha256": master_file_sha256,
				"dimensions": list(master_size),
				"decode_mode": master_mode,
			},
			"output": {
				"path": normalized_path(output),
				"file_sha256": str(prepared_output["file_sha256"]),
				"dimensions": list(output_size),
				"decode_mode": output_mode,
			},
			"crop": {
				"left": crop_box[0],
				"top": crop_box[1],
				"right": crop_box[2],
				"bottom": crop_box[3],
				"dimensions": [crop_box[2] - crop_box[0], crop_box[3] - crop_box[1]],
			},
			"decode": {
				"backend": "Pillow",
				"pillow_version": PILLOW_VERSION,
				"master_mode": master_mode,
				"output_mode": output_mode,
				"comparison_mode": COMPARISON_MODE,
			},
			"equality": {
				"decoded_pixels_equal": True,
				"comparison_mode": COMPARISON_MODE,
				"master_crop_rgba_sha256": master_crop_rgba_sha256,
				"output_rgba_sha256": output_rgba_sha256,
				"pixel_count": source_crop.size[0] * source_crop.size[1],
			},
			"normalized_command": normalized_command_record(
				master,
				output,
				metadata,
				crop_box,
				force,
			),
		}
		metadata_payload = (
			json.dumps(
				metadata_record,
				sort_keys=True,
				indent=2,
				ensure_ascii=False,
			)
			+ "\n"
		).encode("utf-8")
		prepared_metadata = prepare_file(metadata, metadata_payload)
		prepared.extend((prepared_output, prepared_metadata))
		commit_prepared(prepared, force)
	except Exception:
		if not prepared:
			discard_prepared(
				[record for record in (prepared_output, prepared_metadata) if record]
			)
		raise
	return metadata_record


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Create and verify an exact lossless archival portrait crop."
	)
	parser.add_argument("master", type=Path, help="Decoded archival master image")
	parser.add_argument("output", type=Path, help="Lossless PNG crop output")
	parser.add_argument(
		"--crop",
		nargs=4,
		type=int,
		required=True,
		metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
		help="Required half-open crop rectangle in decoded master pixels",
	)
	parser.add_argument(
		"--metadata",
		type=Path,
		required=True,
		help="Required JSON evidence output",
	)
	parser.add_argument(
		"--force",
		action="store_true",
		help="Explicitly allow replacing existing output and metadata files",
	)
	return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	try:
		crop_source(args.master, args.output, args.metadata, args.crop, args.force)
	except (FileNotFoundError, OSError, ValueError, RuntimeError) as error:
		print(f"source crop rejected: {error}", file=sys.stderr)
		return 2
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
