#!/usr/bin/env python3
"""Create an exact source crop and deterministic HOI4 portrait package.

The default route detects exactly one face with OpenCV, computes a portrait
aspect head-and-shoulders crop, proves lossless decoded-pixel equality, and
writes an untouched source copy, crop PNG, ``156x210`` PNG, JSON evidence, and
a co-located provenance contract.  Detection is deliberately fail-closed:
zero or multiple subjects require a manual ``--crop`` recovery invocation.
The manual route remains Pillow-only and keeps the historical crop API.
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


TOOL_VERSION = "2.0"
METADATA_SCHEMA = "hoi4-portrait-source-crop-v1"
PACKAGE_METADATA_SCHEMA = "hoi4-portrait-source-package-v1"
COMMAND_SCHEMA = "hoi4-normalized-source-crop-command-v1"
COMPARISON_MODE = "RGBA"
PORTRAIT_SIZE = (156, 210)
PORTRAIT_ASPECT = PORTRAIT_SIZE[0] / PORTRAIT_SIZE[1]
DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "face_detection_yunet_2026may.onnx"
FACE_SCORE_THRESHOLD = 0.85
FACE_NMS_THRESHOLD = 0.3
FACE_TOP_K = 5000
SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


class OpenCVUnavailableError(RuntimeError):
	"""Raised when automatic detection cannot load the optional OpenCV backend."""


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


def _load_opencv():
	"""Load OpenCV only for automatic mode so manual recovery stays dependency-light."""
	try:
		import cv2
	except ImportError as error:
		raise OpenCVUnavailableError(
			"Automatic subject detection requires OpenCV (cv2); install it or rerun "
			"with an explicit --crop recovery rectangle"
		) from error
	return cv2


def _iou(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> float:
	"""Return intersection-over-union for ``(left, top, width, height)`` boxes."""
	first_left, first_top, first_width, first_height = first
	second_left, second_top, second_width, second_height = second
	first_right = first_left + first_width
	first_bottom = first_top + first_height
	second_right = second_left + second_width
	second_bottom = second_top + second_height
	intersection_width = max(0, min(first_right, second_right) - max(first_left, second_left))
	intersection_height = max(0, min(first_bottom, second_bottom) - max(first_top, second_top))
	intersection = intersection_width * intersection_height
	if not intersection:
		return 0.0
	first_area = first_width * first_height
	second_area = second_width * second_height
	return intersection / float(first_area + second_area - intersection)


def _deduplicate_face_candidates(
	candidates: Iterable[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
	"""Collapse overlapping YuNet detections without hiding distinct subjects."""
	ordered = sorted(
		(
			tuple(int(value) for value in candidate)
			for candidate in candidates
			if len(candidate) == 4
		),
		key=lambda candidate: (-candidate[2] * candidate[3], candidate[1], candidate[0]),
	)
	kept: list[tuple[int, int, int, int]] = []
	for candidate in ordered:
		left, top, width, height = candidate
		if width <= 0 or height <= 0:
			continue
		if any(_iou(candidate, existing) >= 0.35 for existing in kept):
			continue
		kept.append((left, top, width, height))
	return sorted(kept, key=lambda candidate: (candidate[1], candidate[0], -candidate[2] * candidate[3]))


def detect_face_candidates(
	image: Image.Image,
	model_path: Path | None = None,
) -> list[tuple[int, int, int, int]]:
	"""Detect frontal faces and return deterministic non-overlapping boxes.

	YuNet is intentionally conservative and is not a likeness or identity
	validator.  A later independent human review remains mandatory.
	"""
	cv2 = _load_opencv()
	try:
		import numpy as np
	except ImportError as error:
		raise OpenCVUnavailableError(
			"Automatic subject detection requires NumPy for the OpenCV backend; provide --crop manually"
		) from error

	rgb = image.convert("RGB")
	array = np.asarray(rgb)
	bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
	resolved_model = Path(model_path or DEFAULT_MODEL_PATH).expanduser().resolve()
	if not resolved_model.is_file():
		raise OpenCVUnavailableError(
			f"YuNet face model is unavailable: {resolved_model}; provide --model or --crop manually"
		)
	if not hasattr(cv2, "FaceDetectorYN_create"):
		raise OpenCVUnavailableError(
			"This OpenCV build does not expose FaceDetectorYN; install OpenCV 5.x or provide --crop manually"
		)
	width, height = rgb.size
	try:
		detector = cv2.FaceDetectorYN_create(
			str(resolved_model),
			"",
			(width, height),
			FACE_SCORE_THRESHOLD,
			FACE_NMS_THRESHOLD,
			FACE_TOP_K,
		)
		_, detected = detector.detect(bgr)
	except Exception as error:
		raise OpenCVUnavailableError(
			f"OpenCV YuNet could not load or evaluate {resolved_model}; provide --model or --crop manually: {error}"
		) from error
	if detected is None:
		return []
	candidates: list[tuple[int, int, int, int]] = []
	for row in detected:
		if len(row) < 5 or float(row[14] if len(row) > 14 else row[4]) < FACE_SCORE_THRESHOLD:
			continue
		left, top, candidate_width, candidate_height = (int(round(float(value))) for value in row[:4])
		candidates.append((left, top, candidate_width, candidate_height))
	return _deduplicate_face_candidates(candidates)


def resolve_single_face(
	image_size: tuple[int, int],
	candidates: Iterable[tuple[int, int, int, int]],
) -> tuple[int, int, int, int]:
	"""Require exactly one usable subject and reject ambiguous images."""
	width, height = image_size
	valid: list[tuple[int, int, int, int]] = []
	for candidate in candidates:
		if len(candidate) != 4:
			continue
		left, top, candidate_width, candidate_height = (int(value) for value in candidate)
		if (
			left >= 0
			and top >= 0
			and candidate_width > 0
			and candidate_height > 0
			and left + candidate_width <= width
			and top + candidate_height <= height
		):
			valid.append((left, top, candidate_width, candidate_height))
	valid = _deduplicate_face_candidates(valid)
	if not valid:
		raise ValueError(
			"Automatic subject detection found no unambiguous face; provide an explicit --crop rectangle"
		)
	if len(valid) != 1:
		raise ValueError(
			f"Automatic subject detection found {len(valid)} faces; refusing to guess which subject "
			"to archive, provide an explicit --crop rectangle"
		)
	return valid[0]


def compute_portrait_crop(
	image_size: tuple[int, int],
	face_box: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
	"""Compute a portrait-aspect head-and-shoulders crop around one face.

	The crop is a geometry heuristic only: it keeps the face in the upper third,
	adds lower room for shoulders, and never invents or removes source pixels.
	If the image cannot contain a safe crop, the function fails closed.
	"""
	width, height = image_size
	left, top, face_width, face_height = face_box
	if (
		left < 0
		or top < 0
		or face_width <= 0
		or face_height <= 0
		or left + face_width > width
		or top + face_height > height
	):
		raise ValueError(f"Detected face is outside decoded image bounds: {face_box} in {image_size}")

	# Four-and-a-half face heights leave room for hair, collar, and shoulders while
	# keeping a normal 156:210 portrait aspect.  Integer rounding is recorded in
	# the JSON evidence and the final resize always lands at exactly 156x210.
	crop_height = max(int(round(face_height * 4.5)), int(round(face_width * 4.5 / PORTRAIT_ASPECT)))
	crop_width = max(1, int(round(crop_height * PORTRAIT_ASPECT)))
	if crop_width > width:
		crop_width = width
		crop_height = max(1, int(round(crop_width / PORTRAIT_ASPECT)))
	if crop_height > height:
		crop_height = height
		crop_width = max(1, int(round(crop_height * PORTRAIT_ASPECT)))
	if crop_width > width:
		crop_width = width
		crop_height = max(1, int(round(crop_width / PORTRAIT_ASPECT)))
	if crop_width < face_width or crop_height < face_height:
		raise ValueError(
			"Automatic head-and-shoulders crop cannot contain the detected face at portrait aspect; "
			"provide a larger source or an explicit --crop rectangle"
		)

	face_center_x = left + face_width / 2.0
	proposed_left = int(round(face_center_x - crop_width / 2.0))
	proposed_top = int(round(top - face_height * 0.9))
	proposed_left = min(max(proposed_left, 0), width - crop_width)
	proposed_top = min(max(proposed_top, 0), height - crop_height)
	crop = (proposed_left, proposed_top, proposed_left + crop_width, proposed_top + crop_height)
	if not (
		crop[0] <= left
		and crop[1] <= top
		and crop[2] >= left + face_width
		and crop[3] >= top + face_height
	):
		raise ValueError(
			"Automatic head-and-shoulders crop would clip the detected face; provide an explicit --crop rectangle"
		)
	return validate_crop_box(image_size, crop)


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


def encode_processed_portrait(image: Image.Image) -> bytes:
	"""Resize an exact source crop to the deterministic RGB HOI4 target."""
	processed = image.convert("RGB").resize(PORTRAIT_SIZE, Image.Resampling.LANCZOS)
	buffer = io.BytesIO()
	processed.save(buffer, format="PNG", optimize=False, compress_level=9)
	return buffer.getvalue()


def _default_package_path(path: Path, suffix: str) -> Path:
	return path.with_name(f"{_package_basename(path)}_156x210{suffix}")


def _default_source_copy_path(master: Path, output: Path) -> Path:
	return output.with_name(f"{_package_basename(output)}_original{master.suffix}")


def _package_basename(output: Path) -> str:
	"""Resolve a stable runtime basename from the crop output filename."""
	stem = output.stem
	for marker in ("_source_crop", "_crop"):
		if stem.endswith(marker):
			stem = stem[: -len(marker)]
			break
	return stem or output.stem


def _default_provenance_path(output: Path) -> Path:
	return output.with_name(f"{_package_basename(output)}.txt")


def validate_package_paths(
	master: Path,
	output: Path,
	metadata: Path,
	processed: Path,
	source_copy: Path,
	provenance: Path,
	force: bool,
) -> tuple[Path, Path, Path, Path, Path, Path]:
	"""Validate automatic-package targets and enforce a co-located evidence set."""
	master = master.expanduser().resolve()
	output = output.expanduser().resolve()
	metadata = metadata.expanduser().resolve()
	processed = processed.expanduser().resolve()
	source_copy = source_copy.expanduser().resolve()
	provenance = provenance.expanduser().resolve()
	if not master.is_file():
		raise FileNotFoundError(f"Master image is not a regular file: {master}")
	if output.suffix.lower() != ".png":
		raise ValueError("Lossless crop output must use the .png suffix")
	if processed.suffix.lower() != ".png":
		raise ValueError("Processed portrait output must use the .png suffix")
	if metadata.suffix.lower() != ".json":
		raise ValueError("Metadata must use the .json suffix")
	if provenance.suffix.lower() != ".txt":
		raise ValueError("Provenance contract must use the .txt suffix")
	targets = (output, metadata, processed, source_copy, provenance)
	if len(set(targets)) != len(targets) or master in targets:
		raise ValueError("Master and automatic-package artifacts must all be distinct")
	if len({target.parent for target in targets}) != 1:
		raise ValueError("Automatic-package artifacts must be co-located in one portrait source folder")
	for target in targets:
		if target.exists() and not target.is_file():
			raise ValueError(f"Write target exists but is not a regular file: {target}")
		if target.exists() and not force:
			raise FileExistsError(
				f"Refusing to replace existing artifact without --force: {target}"
			)
	return master, output, metadata, processed, source_copy, provenance


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


def _automatic_command_record(
	master: Path,
	output: Path,
	metadata: Path,
	processed: Path,
	source_copy: Path,
	provenance: Path,
	force: bool,
	crop_override: tuple[int, int, int, int] | None = None,
) -> dict[str, object]:
	arguments = {
		"master": normalized_path(master),
		"source_copy": normalized_path(source_copy),
		"source_crop": normalized_path(output),
		"processed": normalized_path(processed),
		"metadata": normalized_path(metadata),
		"provenance": normalized_path(provenance),
		"automatic": crop_override is None,
		"crop_override": list(crop_override) if crop_override is not None else None,
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


def _provenance_contract(
	master: Path,
	output: Path,
	metadata: Path,
	processed: Path,
	source_copy: Path,
	provenance: Path,
	master_sha256: str,
	source_copy_sha256: str,
	output_sha256: str,
	processed_sha256: str,
	crop_box: tuple[int, int, int, int],
	face_box: tuple[int, int, int, int] | None,
	subject_count: int | None,
	detector_name: str,
) -> bytes:
	"""Build a co-located, human-completable provenance contract."""
	lines = [
		"HOI4 grounded portrait provenance contract",
		"=================================================",
		"",
		"contract_version: hoi4-grounded-portrait-provenance-v1",
		"status: evidence_generated_pending_identity_source_review",
		"source_mode: source_placeholder",
		"styled_final: not_requested",
		"replacement_pending: false (set true only after an explicit styled_final request)",
		"",
		"REQUIRED HUMAN RECORDS",
		"subject_identity: [REQUIRED: named subject and role]",
		"source_url: [REQUIRED: stable source URL or archive identifier]",
		"source_attribution: [REQUIRED: author/archive/collection]",
		"source_license_or_public_domain_basis: [REQUIRED]",
		"identity_and_role_fit_notes: [REQUIRED]",
		"independent_reviewer: [REQUIRED before DDS/runtime promotion]",
		"independent_review_date: [REQUIRED]",
		"identity_framing_provenance_verdicts: [REQUIRED: separate PASS/FAIL results]",
		"",
		"IMMUTABLE SOURCE EVIDENCE",
		f"source_original: {normalized_path(source_copy)}",
		f"source_original_sha256: {source_copy_sha256}",
		f"source_original_input: {normalized_path(master)}",
		f"source_original_input_sha256: {master_sha256}",
		f"source_crop: {normalized_path(output)}",
		f"source_crop_sha256: {output_sha256}",
		f"source_crop_metadata: {normalized_path(metadata)}",
		f"processed_156x210: {normalized_path(processed)}",
		f"processed_156x210_sha256: {processed_sha256}",
		f"provenance_contract: {normalized_path(provenance)}",
		"",
		"DETECTION AND PROCESSING EVIDENCE",
		f"detector: {detector_name}",
		f"detected_subject_count: {subject_count if subject_count is not None else 'manual_override'}",
		f"detected_face_box_xywh: {list(face_box) if face_box is not None else 'not_used_manual_override'}",
		f"exact_crop_box_left_top_right_bottom: {list(crop_box)}",
		"crop_equality: see JSON decoded_pixels_equal=true and matching RGBA hashes",
		"resize: RGB source crop -> 156x210 PNG using Pillow LANCZOS",
		"runtime_isolation: docs/assets/portraits is durable evidence only; never reference it from .gfx or gameplay",
		"runpod: never operated by the agent; user supplies any explicitly requested styled_final output",
	]
	return ("\n".join(lines) + "\n").encode("utf-8")


def process_portrait_source(
	master_path: Path,
	output_path: Path,
	metadata_path: Path | None = None,
	processed_path: Path | None = None,
	source_copy_path: Path | None = None,
	provenance_path: Path | None = None,
	force: bool = False,
	detector: object | None = None,
	model_path: Path | None = None,
	crop_override: Iterable[int] | None = None,
) -> dict[str, object]:
	"""Create a fail-closed automatic portrait source package.

	``detector`` is an internal test seam accepting a decoded image and returning
	``(left, top, width, height)`` boxes.  Production callers leave it unset so
	OpenCV YuNet is used. ``crop_override`` is the explicit manual recovery path.
	"""
	master_candidate = Path(master_path).expanduser().resolve()
	output_candidate = Path(output_path).expanduser().resolve()
	metadata_candidate = metadata_path or output_candidate.with_suffix(".json")
	processed_candidate = processed_path or _default_package_path(output_candidate, ".png")
	source_copy_candidate = source_copy_path or _default_source_copy_path(master_candidate, output_candidate)
	provenance_candidate = provenance_path or _default_provenance_path(output_candidate)
	master, output, metadata, processed, source_copy, provenance = validate_package_paths(
		master_candidate,
		output_candidate,
		Path(metadata_candidate),
		Path(processed_candidate),
		Path(source_copy_candidate),
		Path(provenance_candidate),
		force,
	)

	master_bytes = master.read_bytes()
	master_file_sha256 = sha256_bytes(master_bytes)
	decoded_master, master_mode, master_size = decode_image(master)
	if sha256_file(master) != master_file_sha256:
		raise RuntimeError("Archival master changed while it was being decoded")
	manual_crop = tuple(crop_override) if crop_override is not None else None
	if manual_crop is not None:
		crop_box = validate_crop_box(master_size, manual_crop)
		face_box = None
		detector_name = "manual crop override (OpenCV not used)"
		subject_count = None
	elif detector is None:
		resolved_model = Path(model_path or DEFAULT_MODEL_PATH).expanduser().resolve()
		face_candidates = detect_face_candidates(decoded_master, resolved_model)
		detector_name = (
			f"OpenCV YuNet FaceDetectorYN ({normalized_path(resolved_model)}; "
			f"sha256={sha256_file(resolved_model)})"
		)
		subject_count = 1
		face_box = resolve_single_face(master_size, face_candidates)
		crop_box = compute_portrait_crop(master_size, face_box)
	else:
		face_candidates = detector(decoded_master)
		detector_name = "test-injected detector (production uses OpenCV YuNet FaceDetectorYN)"
		face_box = resolve_single_face(master_size, face_candidates)
		subject_count = 1
		crop_box = compute_portrait_crop(master_size, face_box)
	source_crop = decoded_master.crop(crop_box)
	crop_payload = encode_lossless_png(source_crop)
	processed_payload = encode_processed_portrait(source_crop)

	prepared: list[dict[str, object]] = []
	prepared_source: dict[str, object] | None = None
	prepared_crop: dict[str, object] | None = None
	prepared_processed: dict[str, object] | None = None
	prepared_metadata: dict[str, object] | None = None
	prepared_provenance: dict[str, object] | None = None
	try:
		prepared_source = prepare_file(source_copy, master_bytes)
		prepared_crop = prepare_file(output, crop_payload)
		prepared_processed = prepare_file(processed, processed_payload)
		with Image.open(Path(prepared_crop["temporary"])) as reopened_crop:
			reopened_crop.load()
			crop_output_mode = reopened_crop.mode
			crop_output_size = reopened_crop.size
			crop_output_rgba = reopened_crop.convert(COMPARISON_MODE)
		crop_output_rgba.load()
		expected_rgba = source_crop.convert(COMPARISON_MODE)
		expected_rgba.load()
		if crop_output_size != source_crop.size or crop_output_rgba.tobytes() != expected_rgba.tobytes():
			raise ValueError("Decoded PNG pixels do not exactly equal the decoded master rectangle")
		master_crop_rgba_sha256 = rgba_sha256(source_crop)
		crop_output_rgba_sha256 = rgba_sha256(crop_output_rgba)
		if master_crop_rgba_sha256 != crop_output_rgba_sha256:
			raise ValueError("Decoded RGBA hashes differ for the master rectangle and output PNG")
		with Image.open(Path(prepared_processed["temporary"])) as reopened_processed:
			reopened_processed.load()
			processed_output_mode = reopened_processed.mode
			processed_output_size = reopened_processed.size
			processed_output_rgba = reopened_processed.convert(COMPARISON_MODE)
		processed_output_rgba.load()
		if processed_output_size != PORTRAIT_SIZE:
			raise ValueError(f"Processed portrait must decode as {PORTRAIT_SIZE}, got {processed_output_size}")
		with Image.open(io.BytesIO(processed_payload)) as processed_expected:
			processed_expected.load()
			if processed_output_rgba.tobytes() != processed_expected.convert(COMPARISON_MODE).tobytes():
				raise ValueError("Processed portrait pixels changed after PNG encoding")
		processed_sha256 = sha256_bytes(processed_payload)
		provenance_payload = _provenance_contract(
			master,
			output,
			metadata,
			processed,
			source_copy,
			provenance,
			master_file_sha256,
			str(prepared_source["file_sha256"]),
			str(prepared_crop["file_sha256"]),
			processed_sha256,
			crop_box,
			face_box,
			subject_count,
			detector_name,
		)
		prepared_provenance = prepare_file(provenance, provenance_payload)
		metadata_record: dict[str, object] = {
			"schema": PACKAGE_METADATA_SCHEMA,
			"status": "exact_source_crop_verified",
			"mode": "manual_crop_override" if manual_crop is not None else "automatic_face_detected",
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
			"source_copy": {
				"path": normalized_path(source_copy),
				"file_sha256": str(prepared_source["file_sha256"]),
				"byte_identical_to_master": str(prepared_source["file_sha256"]) == master_file_sha256,
			},
			"source_crop": {
				"path": normalized_path(output),
				"file_sha256": str(prepared_crop["file_sha256"]),
				"dimensions": list(crop_output_size),
				"decode_mode": crop_output_mode,
			},
			"processed": {
				"path": normalized_path(processed),
				"file_sha256": str(prepared_processed["file_sha256"]),
				"dimensions": list(processed_output_size),
				"decode_mode": processed_output_mode,
				"target_dimensions": list(PORTRAIT_SIZE),
				"resampling": "Pillow LANCZOS",
			},
			"provenance": {
				"path": normalized_path(provenance),
				"file_sha256": str(prepared_provenance["file_sha256"]),
				"contract": "co-located grounded portrait provenance v1",
			},
			"crop": {
				"left": crop_box[0],
				"top": crop_box[1],
				"right": crop_box[2],
				"bottom": crop_box[3],
				"dimensions": [crop_box[2] - crop_box[0], crop_box[3] - crop_box[1]],
			},
			"detector": {
				"backend": "manual crop override" if manual_crop is not None else "OpenCV YuNet FaceDetectorYN",
				"method": detector_name,
				"face_box_xywh": list(face_box) if face_box is not None else None,
				"subject_count": subject_count,
			},
			"decode": {
				"backend": "Pillow",
				"pillow_version": PILLOW_VERSION,
				"master_mode": master_mode,
				"output_mode": crop_output_mode,
				"comparison_mode": COMPARISON_MODE,
			},
			"equality": {
				"decoded_pixels_equal": True,
				"comparison_mode": COMPARISON_MODE,
				"master_crop_rgba_sha256": master_crop_rgba_sha256,
				"output_rgba_sha256": crop_output_rgba_sha256,
				"pixel_count": source_crop.size[0] * source_crop.size[1],
			},
			"normalized_command": _automatic_command_record(
				master,
				output,
				metadata,
				processed,
				source_copy,
				provenance,
				force,
				crop_box if manual_crop is not None else None,
			),
		}
		metadata_payload = (
			json.dumps(metadata_record, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
		).encode("utf-8")
		prepared_metadata = prepare_file(metadata, metadata_payload)
		prepared.extend((prepared_source, prepared_crop, prepared_processed, prepared_metadata, prepared_provenance))
		commit_prepared(prepared, force)
	except Exception:
		if not prepared:
			discard_prepared(
				[record for record in (prepared_source, prepared_crop, prepared_processed, prepared_metadata, prepared_provenance) if record]
			)
		raise
	return metadata_record


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Create an exact portrait crop; omit --crop for fail-closed automatic face detection and a 156x210 package."
	)
	parser.add_argument("master", type=Path, help="Decoded archival master image")
	parser.add_argument("output", type=Path, help="Lossless PNG crop output")
	parser.add_argument(
		"--crop",
		nargs=4,
		type=int,
		metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
		help="Manual half-open crop rectangle; omit for automatic OpenCV face detection",
	)
	parser.add_argument(
		"--metadata",
		type=Path,
		help="JSON evidence output (default: output path with .json suffix)",
	)
	parser.add_argument(
		"--processed",
		type=Path,
		help="156x210 PNG output (default: runtime basename + _156x210.png)",
	)
	parser.add_argument(
		"--source-copy",
		type=Path,
		help="Untouched original copy (default: runtime basename + _original and source suffix)",
	)
	parser.add_argument(
		"--provenance",
		type=Path,
		help="Co-located provenance .txt contract (default: runtime basename + .txt)",
	)
	parser.add_argument(
		"--model",
		type=Path,
		help="Automatic mode YuNet ONNX model (default: bundled tools/models/face_detection_yunet_2026may.onnx)",
	)
	parser.add_argument(
		"--auto",
		action="store_true",
		help="Explicitly request automatic mode; automatic mode is also selected when --crop is omitted",
	)
	parser.add_argument(
		"--force",
		action="store_true",
		help="Explicitly allow replacing existing package artifacts",
	)
	return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)
	try:
		if args.crop is not None:
			metadata = args.metadata or args.output.with_suffix(".json")
			if args.auto:
				raise ValueError("--auto cannot be combined with an explicit --crop override")
			process_portrait_source(
				args.master,
				args.output,
				metadata,
				args.processed,
				args.source_copy,
				args.provenance,
				args.force,
				model_path=args.model,
				crop_override=args.crop,
			)
		else:
			process_portrait_source(
				args.master,
				args.output,
				args.metadata,
				args.processed,
				args.source_copy,
				args.provenance,
				args.force,
				None,
				args.model,
			)
	except (FileNotFoundError, OSError, ValueError, RuntimeError, OpenCVUnavailableError) as error:
		print(f"source crop rejected: {error}", file=sys.stderr)
		return 2
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
