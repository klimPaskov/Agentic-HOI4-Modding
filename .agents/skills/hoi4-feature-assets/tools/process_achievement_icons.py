#!/usr/bin/env python3
"""Apply the user-supplied achievement backgrounds beneath existing 64x64 states.

This migration preserves each completed, grey, and not-eligible source layer at
its native canvas and position. It accepts the mixed DDS encodings present in
the current runtime tree, but every emitted and audited DDS remains the strict
legacy one-level uncompressed BGRA layout used by the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageFile


IMAGE_SIZE = 64
TEMPLATE_BORDER_GUARD = 6
SUPPORTED_SUFFIXES = {".png", ".dds"}
STATE_SUFFIXES = ("_grey", "_not_eligible")
RESERVED_SCAN_STEMS = {
    "contact_sheet",
    "overlay",
    "achievement_template",
    "achievement_template_grey",
}

COMPLETED_TEMPLATE_SHA256 = (
    "248DB006611EB3942550C43DF83802AA6FB24761035FC928B5D34586C0C4C5BA"
)
GREY_TEMPLATE_SHA256 = (
    "70E073694C1A7D9FE40C63B1EB2E987A8A45B3FFD15CCF789EEAA5B843B90022"
)


class AchievementProcessingError(RuntimeError):
    """Raised when an achievement source or output violates the contract."""


@dataclass(frozen=True)
class TemplateSet:
    completed: Image.Image
    grey: Image.Image
    completed_path: Path
    grey_path: Path


@dataclass(frozen=True)
class SourceTriplet:
    achievement_id: str
    completed_path: Path
    grey_path: Path
    not_eligible_path: Path


@dataclass(frozen=True)
class StateImages:
    completed: Image.Image
    grey: Image.Image
    not_eligible: Image.Image


def _skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_template_paths() -> tuple[Path, Path]:
    root = _skill_root() / "assets" / "vanilla_reference" / "icons" / "achievements" / "template"
    return root / "achievement_template.png", root / "achievement_template_grey.png"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def _read_bgra_dds(path: Path) -> Image.Image:
    """Read only the repository's strict one-level uncompressed BGRA DDS layout."""

    try:
        data = path.read_bytes()
    except OSError as error:
        raise AchievementProcessingError(f"Cannot read DDS input {path}: {error}") from error

    if len(data) < 128 or data[:4] != b"DDS ":
        raise AchievementProcessingError(
            f"DDS input {path} is not a legacy DDS file with a 128-byte header."
        )

    header_size = _u32(data, 4)
    height = _u32(data, 12)
    width = _u32(data, 16)
    pitch = _u32(data, 20)
    mip_count = _u32(data, 28)
    pixel_format_size = _u32(data, 76)
    pixel_format_flags = _u32(data, 80)
    fourcc = _u32(data, 84)
    bit_count = _u32(data, 88)
    masks = tuple(_u32(data, offset) for offset in (92, 96, 100, 104))
    caps = _u32(data, 108)
    expected_length = 128 + width * height * 4

    if width <= 0 or height <= 0:
        raise AchievementProcessingError(f"DDS input {path} declares invalid dimensions {width}x{height}.")
    if header_size != 124 or pixel_format_size != 32:
        raise AchievementProcessingError(f"DDS input {path} does not use the legacy 124/32-byte headers.")
    if pixel_format_flags != 65 or fourcc != 0 or bit_count != 32:
        raise AchievementProcessingError(
            f"DDS input {path} is compressed or not 32-bit uncompressed BGRA; strict parsing rejected it."
        )
    if masks != (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000):
        raise AchievementProcessingError(f"DDS input {path} has non-canonical BGRA channel masks.")
    if caps != 0x1000 or mip_count not in (0, 1):
        raise AchievementProcessingError(f"DDS input {path} is not a one-level texture DDS.")
    if pitch != width * 4:
        raise AchievementProcessingError(f"DDS input {path} declares pitch {pitch}, expected {width * 4}.")
    if len(data) != expected_length:
        raise AchievementProcessingError(
            f"DDS input {path} has length {len(data)}, expected {expected_length} for {width}x{height}."
        )

    return Image.frombytes("RGBA", (width, height), data[128:], "raw", "BGRA")


def _read_dds_with_pillow(path: Path) -> Image.Image:
    previous_truncated_setting = ImageFile.LOAD_TRUNCATED_IMAGES
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    try:
        with Image.open(path) as image:
            image.load()
            width, height = image.size
            if width <= 0 or height <= 0:
                raise AchievementProcessingError(
                    f"Pillow decoded DDS input {path} with invalid dimensions {width}x{height}."
                )
            decoded = image.convert("RGBA")
            decoded.load()
            return decoded
    except AchievementProcessingError:
        raise
    except Exception as error:
        raise AchievementProcessingError(f"Pillow DDS fallback could not decode {path}: {error}") from error
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = previous_truncated_setting


def _load_rgba(path: Path) -> Image.Image:
    if not path.is_file():
        raise AchievementProcessingError(f"Input file does not exist: {path}")

    if path.suffix.lower() == ".dds":
        try:
            return _read_bgra_dds(path)
        except AchievementProcessingError as strict_error:
            try:
                decoded = _read_dds_with_pillow(path)
            except AchievementProcessingError as fallback_error:
                raise AchievementProcessingError(
                    f"DDS input {path} failed strict parsing ({strict_error}) and Pillow fallback ({fallback_error})."
                ) from fallback_error
            print(f"INFO: using Pillow DDS fallback for noncanonical source {path}")
            return decoded

    if path.suffix.lower() != ".png":
        raise AchievementProcessingError(f"Unsupported achievement source type: {path}")

    try:
        with Image.open(path) as image:
            image.load()
            decoded = image.convert("RGBA")
            decoded.load()
            return decoded
    except Exception as error:
        raise AchievementProcessingError(f"Cannot decode PNG input {path}: {error}") from error


def _validate_template(path: Path, label: str, expected_sha256: str | None) -> Image.Image:
    if not path.is_file():
        raise AchievementProcessingError(f"Missing {label}: {path}")
    if expected_sha256 is not None and _sha256(path) != expected_sha256:
        raise AchievementProcessingError(
            f"{label} hash changed: {path}. Expected SHA-256 {expected_sha256}."
        )

    image = _load_rgba(path)
    if image.size != (IMAGE_SIZE, IMAGE_SIZE):
        raise AchievementProcessingError(
            f"{label} must be exactly {IMAGE_SIZE}x{IMAGE_SIZE}; got {image.size[0]}x{image.size[1]}: {path}"
        )
    alpha_min, alpha_max = image.getchannel("A").getextrema()
    if alpha_min < 254 or alpha_max != 255:
        raise AchievementProcessingError(
            f"{label} must have alpha range 254..255; got {alpha_min}..{alpha_max}."
        )
    return image


def load_templates(
    completed_path: Path | None = None,
    grey_path: Path | None = None,
) -> TemplateSet:
    default_completed, default_grey = _default_template_paths()
    completed_path = (completed_path or default_completed).expanduser().resolve()
    grey_path = (grey_path or default_grey).expanduser().resolve()
    completed_hash = COMPLETED_TEMPLATE_SHA256 if completed_path == default_completed.resolve() else None
    grey_hash = GREY_TEMPLATE_SHA256 if grey_path == default_grey.resolve() else None
    return TemplateSet(
        completed=_validate_template(completed_path, "completed achievement background", completed_hash),
        grey=_validate_template(grey_path, "grey achievement background", grey_hash),
        completed_path=completed_path,
        grey_path=grey_path,
    )


def _validate_id(value: str) -> str:
    if not value or value in {".", ".."} or Path(value).name != value:
        raise AchievementProcessingError(f"Achievement id must be a single exact filename stem: {value!r}")
    if value.lower().endswith(STATE_SUFFIXES):
        raise AchievementProcessingError(
            f"Achievement id must be the base id, not a grey/not-eligible variant: {value!r}"
        )
    return value


def _strip_state_suffix(stem: str) -> str:
    lower = stem.lower()
    for suffix in STATE_SUFFIXES:
        if lower.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _load_state(path: Path, label: str) -> Image.Image:
    image = _load_rgba(path)
    if image.size != (IMAGE_SIZE, IMAGE_SIZE):
        raise AchievementProcessingError(
            f"Source {label} must be exactly 64x64; got {image.size[0]}x{image.size[1]}: {path}"
        )
    return image


def _load_triplet(triplet: SourceTriplet) -> StateImages:
    return StateImages(
        completed=_load_state(triplet.completed_path, "completed state"),
        grey=_load_state(triplet.grey_path, "grey state"),
        not_eligible=_load_state(triplet.not_eligible_path, "not-eligible state"),
    )


def _compose_states(source: StateImages, templates: TemplateSet) -> StateImages:
    return StateImages(
        completed=Image.alpha_composite(templates.completed, source.completed),
        grey=Image.alpha_composite(templates.grey, source.grey),
        not_eligible=Image.alpha_composite(templates.grey, source.not_eligible),
    )


def _matches_template_border(image: Image.Image, template: Image.Image) -> bool:
    """Return whether the unchanged outer template border is still visible."""

    guard = TEMPLATE_BORDER_GUARD
    for y in range(IMAGE_SIZE):
        for x in range(IMAGE_SIZE):
            if x < guard or x >= IMAGE_SIZE - guard or y < guard or y >= IMAGE_SIZE - guard:
                if image.getpixel((x, y)) != template.getpixel((x, y)):
                    return False
    return True


def _refuse_likely_templated_source(
    triplet: SourceTriplet,
    source: StateImages,
    templates: TemplateSet,
    allow_templated_sources: bool,
) -> None:
    if allow_templated_sources:
        return
    matches = tuple(
        label
        for label, image, template in (
            ("completed", source.completed, templates.completed),
            ("grey", source.grey, templates.grey),
            ("not-eligible", source.not_eligible, templates.grey),
        )
        if _matches_template_border(image, template)
    )
    if matches:
        raise AchievementProcessingError(
            f"Source triplet {triplet.achievement_id} appears already templated "
            f"({', '.join(matches)} state border matches the supplied template). "
            "Keep generated outputs outside source directories, or pass "
            "--allow-templated-sources only when reprocessing is intentional."
        )


def _candidate_files(directory: Path) -> list[Path]:
    return sorted(
        (
            candidate
            for candidate in directory.iterdir()
            if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES
        ),
        key=lambda path: path.name.lower(),
    )


def _find_state_file(candidates: Iterable[Path], achievement_id: str, suffix: str) -> Path:
    expected_stem = (achievement_id + suffix).lower()
    matches = [candidate for candidate in candidates if candidate.stem.lower() == expected_stem]
    if not matches:
        raise AchievementProcessingError(
            f"Missing {suffix or 'completed'} source for achievement {achievement_id}."
        )
    dds_matches = [candidate for candidate in matches if candidate.suffix.lower() == ".dds"]
    png_matches = [candidate for candidate in matches if candidate.suffix.lower() == ".png"]
    if len(dds_matches) > 1 or len(png_matches) > 1:
        raise AchievementProcessingError(
            f"Ambiguous {suffix or 'completed'} source for achievement {achievement_id}: "
            + ", ".join(str(path) for path in matches)
        )
    if dds_matches:
        return dds_matches[0]
    return png_matches[0]


def _collect_directory_triplets(directory: Path, explicit_id: str | None) -> tuple[list[SourceTriplet], Path]:
    if not directory.is_dir():
        raise AchievementProcessingError(f"Input directory does not exist: {directory}")
    candidates = _candidate_files(directory)
    if not candidates:
        raise AchievementProcessingError(f"No PNG or DDS sources found in {directory}.")

    base_ids: set[str] = set()
    for candidate in candidates:
        stem_lower = candidate.stem.lower()
        if stem_lower in RESERVED_SCAN_STEMS:
            continue
        if stem_lower.endswith(STATE_SUFFIXES):
            continue
        base_ids.add(_validate_id(candidate.stem))

    if explicit_id is not None:
        ids = [_validate_id(explicit_id)]
    else:
        ids = sorted(base_ids)
    if not ids:
        raise AchievementProcessingError(f"No base achievement sources found in {directory}.")

    trips: list[SourceTriplet] = []
    for achievement_id in ids:
        trips.append(
            SourceTriplet(
                achievement_id=achievement_id,
                completed_path=_find_state_file(candidates, achievement_id, ""),
                grey_path=_find_state_file(candidates, achievement_id, "_grey"),
                not_eligible_path=_find_state_file(candidates, achievement_id, "_not_eligible"),
            )
        )

    if explicit_id is None:
        orphan_variants = []
        id_lookup = {achievement_id.lower() for achievement_id in ids}
        for candidate in candidates:
            stem_lower = candidate.stem.lower()
            if stem_lower in RESERVED_SCAN_STEMS:
                continue
            base_stem = _strip_state_suffix(candidate.stem)
            if base_stem != candidate.stem and base_stem.lower() not in id_lookup:
                orphan_variants.append(str(candidate))
        if orphan_variants:
            raise AchievementProcessingError(
                "Found state files without a base achievement source: " + ", ".join(orphan_variants)
            )
    return trips, directory


def _collect_explicit_triplet(
    completed_path: Path,
    grey_path: Path,
    not_eligible_path: Path,
    explicit_id: str | None,
) -> tuple[list[SourceTriplet], Path]:
    if explicit_id is None:
        explicit_id = Path(completed_path).stem
        if explicit_id.lower().endswith(STATE_SUFFIXES):
            raise AchievementProcessingError(
                "Explicit triplets require --achievement-id when the completed filename ends in a state suffix."
            )
    achievement_id = _validate_id(explicit_id)
    triplet = SourceTriplet(
        achievement_id=achievement_id,
        completed_path=completed_path.expanduser().resolve(),
        grey_path=grey_path.expanduser().resolve(),
        not_eligible_path=not_eligible_path.expanduser().resolve(),
    )
    return [triplet], triplet.completed_path.parent


def _collect_sources(args: argparse.Namespace) -> tuple[list[SourceTriplet], Path]:
    explicit = [args.completed, args.grey, args.not_eligible]
    explicit_count = sum(path is not None for path in explicit)
    if explicit_count not in (0, 3):
        raise AchievementProcessingError("Provide all three explicit state inputs: --completed, --grey, and --not-eligible.")
    if explicit_count == 3:
        if args.input is not None:
            raise AchievementProcessingError("Do not combine --input with explicit completed/grey/not-eligible inputs.")
        return _collect_explicit_triplet(args.completed, args.grey, args.not_eligible, args.achievement_id)
    if args.input is None:
        raise AchievementProcessingError(
            "Provide --input <triplet directory> with optional --achievement-id, or all three explicit state inputs."
        )
    if args.input.is_file():
        raise AchievementProcessingError(
            "A single source file is not enough for preservation mode; provide --completed, --grey, and --not-eligible."
        )
    return _collect_directory_triplets(args.input.expanduser().resolve(), args.achievement_id)


def _resolve_output_dir(source_root: Path, requested: Path | None, in_place: bool, dry_run: bool) -> Path | None:
    if in_place:
        if requested is not None:
            raise AchievementProcessingError("Do not combine --in-place with --output-dir.")
        return source_root
    if requested is None:
        if dry_run:
            return None
        raise AchievementProcessingError("Writing requires --output-dir, or explicitly opt into --in-place.")
    output = requested.expanduser().resolve()
    if output == source_root.resolve():
        raise AchievementProcessingError(
            f"Output directory {output} is the input directory; use --in-place only when overwriting is intentional."
        )
    return output


def _state_paths(output_dir: Path, achievement_id: str) -> tuple[Path, Path, Path]:
    return (
        output_dir / f"{achievement_id}.dds",
        output_dir / f"{achievement_id}_grey.dds",
        output_dir / f"{achievement_id}_not_eligible.dds",
    )


def _review_paths(output_dir: Path, achievement_id: str) -> tuple[Path, Path, Path]:
    review = output_dir / "review"
    return (
        review / f"{achievement_id}.png",
        review / f"{achievement_id}_grey.png",
        review / f"{achievement_id}_not_eligible.png",
    )


def _load_dds_writer():
    converter_path = Path(__file__).with_name("convert_to_dds.py")
    spec = importlib.util.spec_from_file_location("hoi4_feature_assets_convert_to_dds", converter_path)
    if spec is None or spec.loader is None:
        raise AchievementProcessingError(f"Cannot import canonical DDS writer: {converter_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    writer = getattr(module, "write_bgra_dds", None)
    if writer is None:
        raise AchievementProcessingError(f"Canonical DDS writer is missing from {converter_path}")
    return writer


def _write_dds(path: Path, image: Image.Image) -> None:
    writer = _load_dds_writer()
    writer(path, IMAGE_SIZE, IMAGE_SIZE, image.tobytes("raw", "BGRA"))


def _validate_output_dds(path: Path, expected: Image.Image, label: str) -> None:
    actual = _read_bgra_dds(path)
    if actual.size != (IMAGE_SIZE, IMAGE_SIZE):
        raise AchievementProcessingError(f"Output {label} {path} is not 64x64.")
    if actual.tobytes() != expected.tobytes():
        raise AchievementProcessingError(
            f"Output {label} {path} does not equal background-underlay compositing of its source state."
        )


def _check_collisions(
    output_dir: Path,
    achievement_id: str,
    write_png: bool,
    force: bool,
) -> None:
    paths = list(_state_paths(output_dir, achievement_id))
    if write_png:
        paths.extend(_review_paths(output_dir, achievement_id))
    existing = [path for path in paths if path.exists()]
    if existing and not force:
        raise AchievementProcessingError(
            "Refusing to overwrite existing outputs without --force: "
            + ", ".join(str(path) for path in existing)
        )


def _process_one(
    triplet: SourceTriplet,
    templates: TemplateSet,
    output_dir: Path | None,
    write_png: bool,
    dry_run: bool,
    force: bool,
    allow_templated_sources: bool,
) -> None:
    source = _load_triplet(triplet)
    _refuse_likely_templated_source(triplet, source, templates, allow_templated_sources)
    states = _compose_states(source, templates)
    if dry_run:
        destination = str(output_dir) if output_dir is not None else "(no output directory)"
        print(
            f"PLAN {triplet.achievement_id}: completed={triplet.completed_path}, "
            f"grey={triplet.grey_path}, not-eligible={triplet.not_eligible_path} -> {destination}"
        )
        return

    assert output_dir is not None
    _check_collisions(output_dir, triplet.achievement_id, write_png, force)
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_parent = output_dir.parent
    temp_parent.mkdir(parents=True, exist_ok=True)
    final_dds = _state_paths(output_dir, triplet.achievement_id)
    with tempfile.TemporaryDirectory(prefix=f".achievement_{triplet.achievement_id}_", dir=str(temp_parent)) as staging_dir:
        staging = Path(staging_dir)
        staged: list[tuple[Path, Path]] = []
        for final_path, label, image in (
            (final_dds[0], "completed", states.completed),
            (final_dds[1], "grey", states.grey),
            (final_dds[2], "not-eligible", states.not_eligible),
        ):
            staged_path = staging / final_path.name
            _write_dds(staged_path, image)
            _validate_output_dds(staged_path, image, label)
            staged.append((staged_path, final_path))

        if write_png:
            staged_review = staging / "review"
            staged_review.mkdir()
            for staged_path, image in zip(
                (staged_review / f"{triplet.achievement_id}.png", staged_review / f"{triplet.achievement_id}_grey.png", staged_review / f"{triplet.achievement_id}_not_eligible.png"),
                (states.completed, states.grey, states.not_eligible),
            ):
                image.save(staged_path, format="PNG")
            staged.extend(zip((staged_review / f"{triplet.achievement_id}.png", staged_review / f"{triplet.achievement_id}_grey.png", staged_review / f"{triplet.achievement_id}_not_eligible.png"), _review_paths(output_dir, triplet.achievement_id)))

        for staged_path, final_path in staged:
            final_path.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_path, final_path)
    print(f"WROTE {triplet.achievement_id}: {final_dds[0]}, {final_dds[1]}, {final_dds[2]}")


def _audit_one(
    triplet: SourceTriplet,
    templates: TemplateSet,
    output_dir: Path,
    allow_templated_sources: bool,
) -> None:
    source = _load_triplet(triplet)
    _refuse_likely_templated_source(triplet, source, templates, allow_templated_sources)
    expected = _compose_states(source, templates)
    output_paths = _state_paths(output_dir, triplet.achievement_id)
    for path, label, image in (
        (output_paths[0], "completed", expected.completed),
        (output_paths[1], "grey", expected.grey),
        (output_paths[2], "not-eligible", expected.not_eligible),
    ):
        if not path.is_file():
            raise AchievementProcessingError(f"Missing audited {label} output: {path}")
        _validate_output_dds(path, image, label)
    print(f"AUDIT OK {triplet.achievement_id}: strict 64x64 BGRA triplet and source-layer equality verified")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preserve existing 64x64 achievement state layers while applying supplied backgrounds underneath."
    )
    parser.add_argument("--input", type=Path, help="Directory containing complete base/_grey/_not_eligible triplets.")
    parser.add_argument("--achievement-id", help="Exact base achievement id for one triplet selected from --input or explicit state paths.")
    parser.add_argument("--completed", type=Path, help="Explicit completed-state source layer for one triplet.")
    parser.add_argument("--grey", type=Path, help="Explicit grey-state source layer for one triplet.")
    parser.add_argument("--not-eligible", dest="not_eligible", type=Path, help="Explicit not-eligible source layer for one triplet.")
    parser.add_argument("--output-dir", type=Path, help="Separate output directory for strict DDS triplets and optional review PNGs.")
    parser.add_argument("--template-completed", type=Path, help="Override the supplied completed background.")
    parser.add_argument("--template-grey", type=Path, help="Override the supplied grey background.")
    parser.add_argument("--write-png", action="store_true", help="Also write composited review PNGs under output-dir/review/.")
    parser.add_argument("--dry-run", action="store_true", help="Decode and validate complete source triplets without writing files.")
    parser.add_argument("--audit", action="store_true", help="Recompose source triplets and audit strict output equality.")
    parser.add_argument("--in-place", action="store_true", help="Explicitly allow outputs beside source triplets; combine with --force to replace files.")
    parser.add_argument("--force", action="store_true", help="Allow replacing existing output files.")
    parser.add_argument(
        "--allow-templated-sources",
        action="store_true",
        help="Allow source states whose unchanged outer template border is detected; use only for intentional reprocessing.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.audit and args.dry_run:
        parser.error("--audit and --dry-run cannot be combined")
    if args.audit and args.in_place:
        parser.error("--audit does not write and does not need --in-place")

    try:
        templates = load_templates(args.template_completed, args.template_grey)
        triplets, source_root = _collect_sources(args)
        if args.audit:
            output_dir = (args.output_dir.expanduser().resolve() if args.output_dir is not None else source_root)
            for triplet in triplets:
                _audit_one(triplet, templates, output_dir, args.allow_templated_sources)
            return 0
        output_dir = _resolve_output_dir(source_root, args.output_dir, args.in_place, args.dry_run)
        for triplet in triplets:
            _process_one(
                triplet,
                templates,
                output_dir,
                args.write_png,
                args.dry_run,
                args.force,
                args.allow_templated_sources,
            )
        return 0
    except AchievementProcessingError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
