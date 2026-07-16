#!/usr/bin/env python3
"""Finish a style-approved portrait master for HOI4 leader or advisor use.

This tool is a deterministic finishing and presentation step. It does not
invent a person's face or draw advisor-card artwork, and it is not a substitute
for source research or the required visual review against the canonical
feature-assets skill references in ``assets/vanilla_reference/portraits/leaders``
and ``assets/vanilla_reference/portraits/advisors``.

Real people must start from an attributed archival image. Pass an explicit
head-and-shoulders crop, preserve the person's recognisable features, and
reject the result if the source is too weak to survive the HOI4 finish.
Fictional portraits may start from an approved ImageGen master. Advisor mode
also requires separately generated, shadowless frame and paper sources plus
their alpha-processed overlays. The script only crops, grades, resizes, angles,
derives shadows from approved alpha, composites, validates, and exports those
approved sources. It never draws any visible advisor-card element.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


LEADER_SIZE = (156, 210)
ADVISOR_SIZE = (65, 67)
PROCESSOR_VERSION = "3.1"
LEADER_RENDER_VERSION = "2.0"
ADVISOR_RENDER_VERSION = "3.0"
SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = SKILL_ROOT / "assets" / "vanilla_reference" / "portraits"
ADVISOR_REFERENCE_NAMES = (
	"generic_europe_1.png",
	"generic_female_europe.png",
	"generic_asia_1.png",
	"army_small_ger_friedrich_paulus.png",
	"army_small_ger_gunther_von_kluge.png",
	"army_small_ger_erwin_rommel.png",
)

# These native placements reproduce the shared 65x67 vanilla dossier-card
# footprint. Generated overlays remain the sole source of visible artwork: the
# processor trims their authored alpha bounds, resizes them, and places them.
ADVISOR_FRAME_SIZE = (40, 58)
ADVISOR_FRAME_POSITION = (1, 1)
ADVISOR_FRAME_ANGLE = 5.0
ADVISOR_PAPER_SIZE = (32, 38)
ADVISOR_PAPER_POSITION = (29, 27)
ADVISOR_WINDOW_ALPHA_THRESHOLD = 32

# Face bounds are supplied in source pixels and mapped into the final native
# canvas. These ranges cover the canonical vanilla advisor family while
# rejecting leader-scale faces and tiny busts that disappear behind the dossier
# paper.
ADVISOR_FACE_WIDTH_RANGE = (14.0, 24.0)
ADVISOR_FACE_HEIGHT_RANGE = (16.0, 30.0)
ADVISOR_FACE_CENTER_X_RANGE = (17.0, 27.0)
ADVISOR_FACE_CENTER_Y_RANGE = (18.0, 32.0)


def parse_crop(values: list[int], image: Image.Image) -> tuple[int, int, int, int]:
	left, top, right, bottom = values
	if left < 0 or top < 0 or right > image.width or bottom > image.height:
		raise ValueError(f"Crop {values} is outside the {image.width}x{image.height} source")
	if right <= left or bottom <= top:
		raise ValueError(f"Crop must have positive width and height: {values}")
	return left, top, right, bottom


def parse_face_box(
	values: list[int],
	image: Image.Image,
	crop_box: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
	face_box = parse_crop(values, image)
	left, top, right, bottom = face_box
	crop_left, crop_top, crop_right, crop_bottom = crop_box
	if (
		left < crop_left
		or top < crop_top
		or right > crop_right
		or bottom > crop_bottom
	):
		raise ValueError(
			f"Face box {values} must be fully contained by advisor crop {crop_box}"
		)
	return face_box


def deterministic_noise(size: tuple[int, int], seed_text: str) -> Image.Image:
	seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:8], 16)
	state = seed
	pixels: list[int] = []
	for _ in range(size[0] * size[1]):
		state = (1664525 * state + 1013904223) & 0xFFFFFFFF
		pixels.append(118 + ((state >> 24) % 21))
	noise = Image.new("L", size)
	noise.putdata(pixels)
	return noise.filter(ImageFilter.GaussianBlur(0.35))


def vignette_mask(size: tuple[int, int]) -> Image.Image:
	width, height = size
	mask = Image.new("L", size)
	pixels: list[int] = []
	for y in range(height):
		vertical = (y - height * 0.43) / (height * 0.62)
		for x in range(width):
			horizontal = (x - width * 0.5) / (width * 0.68)
			distance = math.sqrt(horizontal * horizontal + vertical * vertical)
			pixels.append(max(0, min(255, round((distance - 0.50) * 145))))
	mask.putdata(pixels)
	return mask.filter(ImageFilter.GaussianBlur(max(2, width // 24)))


def hoi4_finish(image: Image.Image, source_kind: str, seed_text: str) -> Image.Image:
	alpha = image.getchannel("A")
	rgb = image.convert("RGB")
	rgb = ImageEnhance.Contrast(rgb).enhance(1.075)
	rgb = ImageEnhance.Color(rgb).enhance(0.88 if source_kind == "real" else 0.94)

	# A restrained edge-preserving blend softens photographic micro-detail while
	# retaining the face, eyes, hairline, uniform edges, and other identity cues.
	smoothed = rgb.filter(ImageFilter.MedianFilter(3))
	rgb = Image.blend(rgb, smoothed, 0.14 if source_kind == "real" else 0.10)
	rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.15, percent=72, threshold=4))

	# Warm highlights and cool charcoal shadows mirror the restrained painted
	# palette of the bundled vanilla references without colourising a new face.
	luma = ImageOps.grayscale(rgb)
	warm = Image.new("RGB", rgb.size, (126, 91, 59))
	cool = Image.new("RGB", rgb.size, (40, 47, 53))
	warm_mask = luma.point(lambda value: max(0, min(31, round((value - 108) * 0.19))))
	cool_mask = luma.point(lambda value: max(0, min(23, round((112 - value) * 0.17))))
	rgb = Image.composite(warm, rgb, warm_mask)
	rgb = Image.composite(cool, rgb, cool_mask)

	grain = deterministic_noise(rgb.size, seed_text)
	grain_rgb = Image.merge("RGB", (grain, grain, grain))
	rgb = Image.blend(rgb, grain_rgb, 0.035)

	dark = Image.new("RGB", rgb.size, (22, 25, 27))
	rgb = Image.composite(dark, rgb, vignette_mask(rgb.size))
	result = rgb.convert("RGBA")
	result.putalpha(alpha)
	return result


def make_leader(source_crop: Image.Image, source_kind: str, seed_text: str) -> Image.Image:
	resized = ImageOps.fit(
		source_crop,
		LEADER_SIZE,
		method=Image.Resampling.LANCZOS,
		centering=(0.5, 0.44),
	)
	return hoi4_finish(resized, source_kind, seed_text)


def sha256_file(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as handle:
		for chunk in iter(lambda: handle.read(1024 * 1024), b""):
			digest.update(chunk)
	return digest.hexdigest()


def threshold_bbox(alpha: Image.Image, threshold: int = 8) -> tuple[int, int, int, int]:
	box = alpha.point(lambda value: 255 if value > threshold else 0).getbbox()
	if box is None:
		raise ValueError("Generated overlay has no visible alpha bounds")
	return box


def alpha_coverage(alpha: Image.Image, threshold: int) -> float:
	return sum(1 for value in alpha.getdata() if value > threshold) / (
		alpha.width * alpha.height
	)


def load_generated_layer(
	overlay_path: Path,
	source_path: Path,
	label: str,
) -> tuple[Image.Image, dict[str, object]]:
	if not overlay_path.is_file():
		raise FileNotFoundError(f"Missing {label} alpha overlay: {overlay_path}")
	if not source_path.is_file():
		raise FileNotFoundError(f"Missing {label} ImageGen source: {source_path}")
	with Image.open(overlay_path) as image:
		overlay = image.convert("RGBA")
	with Image.open(source_path) as image:
		source = image.convert("RGB")
	if overlay.size != source.size:
		raise ValueError(
			f"{label} overlay/source dimensions differ: {overlay.size} versus {source.size}"
		)
	if overlay.width < 512 or overlay.height < 512:
		raise ValueError(
			f"{label} ImageGen source must remain a full-resolution master; got {overlay.size}"
		)
	alpha = overlay.getchannel("A")
	minimum, maximum = alpha.getextrema()
	if minimum != 0 or maximum != 255:
		raise ValueError(
			f"{label} overlay needs full transparent/opaque alpha; extrema were "
			f"{(minimum, maximum)} for {overlay_path}"
		)
	coverage = alpha_coverage(alpha, 8)
	if coverage < 0.02 or coverage > 0.50:
		raise ValueError(
			f"{label} overlay has implausible authored coverage {coverage:.3f}: "
			f"{overlay_path}"
		)
	# Ignore the sub-32 edge flecks that chroma-key cleanup can leave on the
	# master canvas. They are not part of the authored visible overlay and would
	# otherwise distort the native-size fit.
	visible_bbox = threshold_bbox(alpha, ADVISOR_WINDOW_ALPHA_THRESHOLD)

	# Chroma-key cleanup can alter edge RGB, but visible pixels must still be
	# recognisably derived from the retained ImageGen source rather than locally
	# redrawn artwork.
	difference = ImageChops.difference(source, overlay.convert("RGB"))
	difference_values = difference.getdata()
	alpha_values = alpha.getdata()
	visible_difference = 0.0
	visible_count = 0
	for channels, value in zip(difference_values, alpha_values):
		if value > 128:
			visible_difference += sum(channels) / 3
			visible_count += 1
	mean_visible_difference = visible_difference / max(1, visible_count)
	if mean_visible_difference > 24.0:
		raise ValueError(
			f"{label} overlay differs too far from its ImageGen source on visible "
			f"pixels ({mean_visible_difference:.2f} mean RGB delta)"
		)

	return overlay, {
		"source": str(source_path),
		"source_sha256": sha256_file(source_path),
		"overlay": str(overlay_path),
		"overlay_sha256": sha256_file(overlay_path),
		"source_size": list(source.size),
		"alpha_extrema": [minimum, maximum],
		"source_visible_bbox": list(visible_bbox),
		"source_alpha_coverage_gt_8": round(coverage, 6),
		"mean_visible_source_rgb_delta": round(mean_visible_difference, 4),
	}


def normalize_generated_layer(
	image: Image.Image,
	target_size: tuple[int, int],
	position: tuple[int, int],
	angle: float = 0.0,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
	visible_bbox = threshold_bbox(
		image.getchannel("A"), ADVISOR_WINDOW_ALPHA_THRESHOLD
	)
	trimmed = image.crop(visible_bbox)
	resized = trimmed.resize(target_size, Image.Resampling.LANCZOS)
	if angle:
		resized = resized.rotate(
			angle,
			resample=Image.Resampling.BICUBIC,
			expand=True,
			fillcolor=(0, 0, 0, 0),
		)
	canvas = Image.new("RGBA", ADVISOR_SIZE, (0, 0, 0, 0))
	canvas.alpha_composite(resized, position)
	return canvas, visible_bbox


def frame_palette_metrics(frame: Image.Image) -> dict[str, float]:
	luminance_values: list[float] = []
	saturation_values: list[float] = []
	gold_pixels = 0
	warm_pixels = 0
	for red, green, blue, alpha in frame.getdata():
		if alpha <= 64:
			continue
		luminance = (54 * red + 183 * green + 19 * blue) / 256
		luminance_values.append(luminance)
		maximum = max(red, green, blue)
		saturation_values.append(
			0.0 if maximum == 0 else (maximum - min(red, green, blue)) / maximum
		)
		if red - blue > 20:
			warm_pixels += 1
		if (
			red > 75
			and green > 45
			and blue < green * 0.78
			and red > green * 1.12
			and red - blue > 35
		):
			gold_pixels += 1
	if not luminance_values:
		raise ValueError("Advisor frame has no visible palette samples")
	metrics = {
		"mean_luminance": sum(luminance_values) / len(luminance_values),
		"mean_saturation": sum(saturation_values) / len(saturation_values),
		"dark_pixel_ratio": sum(value < 110 for value in luminance_values)
		/ len(luminance_values),
		"gold_pixel_ratio": gold_pixels / len(luminance_values),
		"warm_pixel_ratio": warm_pixels / len(luminance_values),
	}
	if metrics["mean_luminance"] > 90 or metrics["dark_pixel_ratio"] < 0.80:
		raise ValueError(
			"Advisor frame must be predominantly charcoal/black at native size; "
			f"metrics were {metrics}"
		)
	if metrics["gold_pixel_ratio"] > 0.02:
		raise ValueError(
			"Advisor frame contains an ornamental gold/bronze treatment; "
			f"gold-like pixel ratio was {metrics['gold_pixel_ratio']:.3f}"
		)
	if metrics["mean_saturation"] > 0.10 or metrics["warm_pixel_ratio"] > 0.10:
		raise ValueError(
			"Advisor frame is not the neutral charcoal of the vanilla dossier family; "
			f"metrics were {metrics}"
		)
	return {key: round(value, 6) for key, value in metrics.items()}


def grade_advisor_frame(frame: Image.Image) -> Image.Image:
	"""Match the neutral, slightly translucent charcoal of vanilla small cards."""
	alpha = frame.getchannel("A").point(lambda value: min(value, 210))
	rgb = ImageEnhance.Color(frame.convert("RGB")).enhance(0.0)
	rgb = ImageEnhance.Brightness(rgb).enhance(0.86)
	rgb = ImageEnhance.Contrast(rgb).enhance(1.04)
	graded = rgb.convert("RGBA")
	graded.putalpha(alpha)
	return graded


def grade_advisor_portrait(portrait: Image.Image) -> Image.Image:
	"""Keep small-card facial landmarks open, neutral, and painterly at 65x67."""
	alpha = portrait.getchannel("A")
	rgb = ImageEnhance.Color(portrait.convert("RGB")).enhance(0.58)
	# A restrained gamma lift opens eyes, cheeks, and dark uniforms without
	# flattening the painted highlights or inventing source detail.
	lut = [round(255 * ((value / 255) ** 0.86)) for value in range(256)]
	rgb = rgb.point(lut * 3)
	rgb = ImageEnhance.Contrast(rgb).enhance(1.02)
	graded = rgb.convert("RGBA")
	graded.putalpha(alpha)
	return graded


def grade_advisor_paper(paper: Image.Image) -> Image.Image:
	"""Reduce generated parchment chroma to the pale vanilla dossier-note range."""
	alpha = paper.getchannel("A")
	rgb = ImageEnhance.Color(paper.convert("RGB")).enhance(0.66)
	graded = rgb.convert("RGBA")
	graded.putalpha(alpha)
	return graded


def layer_palette_metrics(layer: Image.Image) -> dict[str, float]:
	luminance_values: list[float] = []
	saturation_values: list[float] = []
	for red, green, blue, alpha in layer.getdata():
		if alpha <= 64:
			continue
		luminance_values.append((54 * red + 183 * green + 19 * blue) / 256)
		maximum = max(red, green, blue)
		saturation_values.append(
			0.0 if maximum == 0 else (maximum - min(red, green, blue)) / maximum
		)
	if not luminance_values:
		raise ValueError("Advisor layer has no visible palette samples")
	return {
		"mean_luminance": round(sum(luminance_values) / len(luminance_values), 6),
		"mean_saturation": round(sum(saturation_values) / len(saturation_values), 6),
	}


def enclosed_alpha_window(
	frame: Image.Image,
) -> tuple[Image.Image, tuple[int, int, int, int], int]:
	alpha = frame.getchannel("A")
	width, height = alpha.size
	transparent = [
		value <= ADVISOR_WINDOW_ALPHA_THRESHOLD for value in alpha.getdata()
	]
	exterior = [False] * (width * height)
	stack: list[tuple[int, int]] = []
	for x in range(width):
		stack.extend(((x, 0), (x, height - 1)))
	for y in range(1, height - 1):
		stack.extend(((0, y), (width - 1, y)))
	while stack:
		x, y = stack.pop()
		index = y * width + x
		if exterior[index] or not transparent[index]:
			continue
		exterior[index] = True
		if x:
			stack.append((x - 1, y))
		if x + 1 < width:
			stack.append((x + 1, y))
		if y:
			stack.append((x, y - 1))
		if y + 1 < height:
			stack.append((x, y + 1))

	interior_points = [
		(index % width, index // width)
		for index, is_transparent in enumerate(transparent)
		if is_transparent and not exterior[index]
	]
	if not interior_points:
		raise ValueError(
			"Advisor frame alpha does not contain a closed portrait window"
		)
	window_bbox = (
		min(x for x, _ in interior_points),
		min(y for _, y in interior_points),
		max(x for x, _ in interior_points) + 1,
		max(y for _, y in interior_points) + 1,
	)
	window_width = window_bbox[2] - window_bbox[0]
	window_height = window_bbox[3] - window_bbox[1]
	window_area = len(interior_points)
	window_fill = window_area / (window_width * window_height)
	if not (
		32 <= window_width <= 38
		and 49 <= window_height <= 53
		and 4 <= window_bbox[0] <= 8
		and 4 <= window_bbox[1] <= 9
		and 40 <= window_bbox[2] <= 44
		and 55 <= window_bbox[3] <= 59
		and window_fill >= 0.80
	):
		raise ValueError(
			"Advisor frame portrait window is not the canonical narrow native-size "
			f"window: bbox={window_bbox}, area={window_area}, fill={window_fill:.3f}"
		)
	mask_values = [0] * (width * height)
	for x, y in interior_points:
		mask_values[y * width + x] = 255
	window_mask = Image.new("L", ADVISOR_SIZE)
	window_mask.putdata(mask_values)
	return window_mask, window_bbox, window_area


def alpha_shadow(layer: Image.Image, opacity: float, blur: float) -> Image.Image:
	alpha = layer.getchannel("A").point(lambda value: round(value * opacity))
	shadow = Image.new("RGBA", layer.size, (0, 0, 0, 255))
	shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(blur)))
	return shadow


def composite_alpha_shadow(
	canvas: Image.Image,
	alpha: Image.Image,
	offset: tuple[int, int],
	opacity: float,
	blur: float,
) -> None:
	layer = Image.new("RGBA", ADVISOR_SIZE, (0, 0, 0, 255))
	layer.putalpha(alpha)
	shadow = alpha_shadow(layer, opacity, blur)
	canvas.alpha_composite(shadow, offset)


def fit_advisor_portrait(
	source_crop: Image.Image,
	source_kind: str,
	seed_text: str,
	crop_box: tuple[int, int, int, int],
	face_box: tuple[int, int, int, int],
	window_bbox: tuple[int, int, int, int],
) -> tuple[Image.Image, tuple[float, float, float, float], tuple[float, float, float, float]]:
	window_width = window_bbox[2] - window_bbox[0]
	window_height = window_bbox[3] - window_bbox[1]
	source_width, source_height = source_crop.size
	target_ratio = window_width / window_height
	source_ratio = source_width / source_height
	if source_ratio > target_ratio:
		fit_height = float(source_height)
		fit_width = fit_height * target_ratio
		fit_left = (source_width - fit_width) * 0.5
		fit_top = 0.0
	else:
		fit_width = float(source_width)
		fit_height = fit_width / target_ratio
		fit_left = 0.0
		fit_top = (source_height - fit_height) * 0.38
	fit_box = (fit_left, fit_top, fit_left + fit_width, fit_top + fit_height)
	portrait = source_crop.resize(
		(window_width, window_height),
		Image.Resampling.LANCZOS,
		box=fit_box,
	)
	portrait = hoi4_finish(portrait, source_kind, seed_text + ":advisor")
	portrait = grade_advisor_portrait(portrait)

	local_face = (
		face_box[0] - crop_box[0],
		face_box[1] - crop_box[1],
		face_box[2] - crop_box[0],
		face_box[3] - crop_box[1],
	)
	scale_x = window_width / fit_width
	scale_y = window_height / fit_height
	mapped_face = (
		window_bbox[0] + (local_face[0] - fit_left) * scale_x,
		window_bbox[1] + (local_face[1] - fit_top) * scale_y,
		window_bbox[0] + (local_face[2] - fit_left) * scale_x,
		window_bbox[1] + (local_face[3] - fit_top) * scale_y,
	)
	return portrait, mapped_face, fit_box


def validate_face_placement(
	mapped_face: tuple[float, float, float, float],
	window_bbox: tuple[int, int, int, int],
	paper: Image.Image,
) -> dict[str, object]:
	left, top, right, bottom = mapped_face
	width = right - left
	height = bottom - top
	center_x = (left + right) / 2
	center_y = (top + bottom) / 2
	if not (
		ADVISOR_FACE_WIDTH_RANGE[0] <= width <= ADVISOR_FACE_WIDTH_RANGE[1]
		and ADVISOR_FACE_HEIGHT_RANGE[0] <= height <= ADVISOR_FACE_HEIGHT_RANGE[1]
		and ADVISOR_FACE_CENTER_X_RANGE[0] <= center_x <= ADVISOR_FACE_CENTER_X_RANGE[1]
		and ADVISOR_FACE_CENTER_Y_RANGE[0] <= center_y <= ADVISOR_FACE_CENTER_Y_RANGE[1]
	):
		raise ValueError(
			"Advisor face placement does not match the six native vanilla examples: "
			f"mapped bbox={tuple(round(value, 2) for value in mapped_face)}, "
			f"size=({width:.2f}, {height:.2f}), center=({center_x:.2f}, {center_y:.2f})"
		)
	intersection_left = max(left, window_bbox[0])
	intersection_top = max(top, window_bbox[1])
	intersection_right = min(right, window_bbox[2])
	intersection_bottom = min(bottom, window_bbox[3])
	intersection_area = max(0.0, intersection_right - intersection_left) * max(
		0.0, intersection_bottom - intersection_top
	)
	if intersection_area / (width * height) < 0.90:
		raise ValueError("Advisor face box is clipped by the generated frame window")

	integer_box = (
		max(0, int(left)),
		max(0, int(top)),
		min(ADVISOR_SIZE[0], int(math.ceil(right))),
		min(ADVISOR_SIZE[1], int(math.ceil(bottom))),
	)
	face_area = max(1, (integer_box[2] - integer_box[0]) * (integer_box[3] - integer_box[1]))
	paper_alpha = paper.getchannel("A").crop(integer_box)
	paper_overlap_ratio = sum(value > 32 for value in paper_alpha.getdata()) / face_area
	if paper_overlap_ratio > 0.18:
		raise ValueError(
			"Generated dossier paper obscures the native-size face placement: "
			f"overlap ratio {paper_overlap_ratio:.3f}"
		)
	return {
		"mapped_bbox": [round(value, 4) for value in mapped_face],
		"width": round(width, 4),
		"height": round(height, 4),
		"center": [round(center_x, 4), round(center_y, 4)],
		"paper_overlap_ratio": round(paper_overlap_ratio, 6),
	}


def advisor_face_palette_metrics(
	portrait: Image.Image,
	mapped_face: tuple[float, float, float, float],
	window_bbox: tuple[int, int, int, int],
) -> dict[str, float]:
	local_box = (
		max(0, int(math.floor(mapped_face[0] - window_bbox[0]))),
		max(0, int(math.floor(mapped_face[1] - window_bbox[1]))),
		min(portrait.width, int(math.ceil(mapped_face[2] - window_bbox[0]))),
		min(portrait.height, int(math.ceil(mapped_face[3] - window_bbox[1]))),
	)
	metrics = layer_palette_metrics(portrait.crop(local_box))
	if not (
		80 <= metrics["mean_luminance"] <= 175
		and 0.08 <= metrics["mean_saturation"] <= 0.38
	):
		raise ValueError(
			"Advisor face values do not remain readable in the vanilla small-card "
			f"range: bbox={local_box}, metrics={metrics}"
		)
	metrics["local_bbox_left"] = float(local_box[0])
	metrics["local_bbox_top"] = float(local_box[1])
	metrics["local_bbox_right"] = float(local_box[2])
	metrics["local_bbox_bottom"] = float(local_box[3])
	return metrics


def make_advisor(
	source_crop: Image.Image,
	source_kind: str,
	seed_text: str,
	frame_overlay: Image.Image,
	paper_overlay: Image.Image,
	crop_box: tuple[int, int, int, int],
	face_box: tuple[int, int, int, int],
) -> tuple[Image.Image, dict[str, object]]:
	frame, frame_source_bbox = normalize_generated_layer(
		frame_overlay,
		ADVISOR_FRAME_SIZE,
		ADVISOR_FRAME_POSITION,
		ADVISOR_FRAME_ANGLE,
	)
	frame = grade_advisor_frame(frame)
	frame_alpha = frame.getchannel("A")
	frame_coverage = alpha_coverage(frame_alpha, 32)
	if not 0.09 <= frame_coverage <= 0.26:
		raise ValueError(
			f"Advisor frame native coverage {frame_coverage:.3f} is outside vanilla bounds"
		)
	palette_metrics = frame_palette_metrics(frame)
	window_mask, window_bbox, window_area = enclosed_alpha_window(frame)

	paper, paper_source_bbox = normalize_generated_layer(
		paper_overlay,
		ADVISOR_PAPER_SIZE,
		ADVISOR_PAPER_POSITION,
	)
	paper = grade_advisor_paper(paper)
	paper_alpha = paper.getchannel("A")
	paper_palette = layer_palette_metrics(paper)
	if not (
		195 <= paper_palette["mean_luminance"] <= 218
		and 0.12 <= paper_palette["mean_saturation"] <= 0.27
	):
		raise ValueError(
			"Advisor paper does not match the pale low-chroma vanilla note: "
			f"metrics were {paper_palette}"
		)
	paper_coverage = alpha_coverage(paper_alpha, 32)
	if not 0.23 <= paper_coverage <= 0.32:
		raise ValueError(
			f"Advisor paper native coverage {paper_coverage:.3f} is outside vanilla bounds"
		)
	paper_window_overlap = sum(
		paper_value > 32 and window_value > 0
		for paper_value, window_value in zip(paper_alpha.getdata(), window_mask.getdata())
	) / window_area
	if not 0.12 <= paper_window_overlap <= 0.32:
		raise ValueError(
			"Advisor paper does not overlap the portrait window like vanilla: "
			f"ratio={paper_window_overlap:.3f}"
		)

	portrait, mapped_face, portrait_fit_box = fit_advisor_portrait(
		source_crop,
		source_kind,
		seed_text,
		crop_box,
		face_box,
		window_bbox,
	)
	face_metrics = validate_face_placement(mapped_face, window_bbox, paper)
	face_palette = advisor_face_palette_metrics(portrait, mapped_face, window_bbox)
	portrait_layer = Image.new("RGBA", ADVISOR_SIZE, (0, 0, 0, 0))
	portrait_layer.alpha_composite(portrait, (window_bbox[0], window_bbox[1]))
	portrait_layer.putalpha(
		ImageChops.multiply(portrait_layer.getchannel("A"), window_mask)
	)

	canvas = Image.new("RGBA", ADVISOR_SIZE, (0, 0, 0, 0))
	card_alpha = ImageChops.lighter(frame_alpha, window_mask)
	# Vanilla cards combine a broad low-opacity shadow with a one-pixel hard
	# contact shadow. Both are derived exclusively from the generated layer alpha.
	composite_alpha_shadow(canvas, card_alpha, (2, 2), 0.18, 1.15)
	composite_alpha_shadow(canvas, card_alpha, (1, 1), 0.22, 0.0)
	canvas.alpha_composite(portrait_layer)
	canvas.alpha_composite(frame)
	composite_alpha_shadow(canvas, paper_alpha, (1, 1), 0.22, 0.6)
	composite_alpha_shadow(canvas, paper_alpha, (1, 1), 0.44, 0.0)
	canvas.alpha_composite(paper)

	return canvas, {
		"frame_source_visible_bbox": list(frame_source_bbox),
		"frame_native_size": list(ADVISOR_FRAME_SIZE),
		"frame_native_position": list(ADVISOR_FRAME_POSITION),
		"frame_angle_degrees": ADVISOR_FRAME_ANGLE,
		"frame_native_alpha_coverage_gt_32": round(frame_coverage, 6),
		"frame_palette": palette_metrics,
		"portrait_window_bbox": list(window_bbox),
		"portrait_window_area": window_area,
		"portrait_fit_source_box": [round(value, 4) for value in portrait_fit_box],
		"face_placement": face_metrics,
		"face_palette": face_palette,
		"paper_source_visible_bbox": list(paper_source_bbox),
		"paper_native_size": list(ADVISOR_PAPER_SIZE),
		"paper_native_position": list(ADVISOR_PAPER_POSITION),
		"paper_palette": paper_palette,
		"paper_window_overlap_ratio": round(paper_window_overlap, 6),
		"shadow_contract": "alpha_derived_soft_plus_hard_contact_shadows",
	}


def validate_advisor_output(
	finished: Image.Image,
	reference_dir: Path,
) -> dict[str, object]:
	if finished.size != ADVISOR_SIZE:
		raise ValueError(f"Advisor output must be exactly 65x67, got {finished.size}")
	alpha = finished.getchannel("A")
	if alpha.getextrema() != (0, 255):
		raise ValueError(
			f"Advisor output needs transparent and opaque pixels, got {alpha.getextrema()}"
		)
	corner_values = [
		alpha.getpixel((0, 0)),
		alpha.getpixel((ADVISOR_SIZE[0] - 1, 0)),
		alpha.getpixel((0, ADVISOR_SIZE[1] - 1)),
		alpha.getpixel((ADVISOR_SIZE[0] - 1, ADVISOR_SIZE[1] - 1)),
	]
	if any(corner_values):
		raise ValueError(
			f"Advisor output must keep all four canvas corners transparent: {corner_values}"
		)

	reference_metrics: list[dict[str, object]] = []
	reference_masks: list[list[bool]] = []
	for name in ADVISOR_REFERENCE_NAMES:
		path = reference_dir / name
		if not path.is_file():
			raise FileNotFoundError(f"Missing canonical advisor reference: {path}")
		with Image.open(path) as image:
			reference = image.convert("RGBA")
		if reference.size != ADVISOR_SIZE:
			raise ValueError(f"Canonical advisor reference is not 65x67: {path}")
		reference_alpha = reference.getchannel("A")
		reference_masks.append(
			[value > ADVISOR_WINDOW_ALPHA_THRESHOLD for value in reference_alpha.getdata()]
		)
		reference_metrics.append(
			{
				"name": name,
				"bbox_gt_32": list(
					threshold_bbox(reference_alpha, ADVISOR_WINDOW_ALPHA_THRESHOLD)
				),
				"coverage_gt_8": alpha_coverage(reference_alpha, 8),
				"coverage_gt_32": alpha_coverage(reference_alpha, 32),
				"coverage_gt_128": alpha_coverage(reference_alpha, 128),
				"coverage_gt_224": alpha_coverage(reference_alpha, 224),
			}
		)

	thresholds = (8, 32, 128, 224)
	candidate_coverage = {
		f"coverage_gt_{threshold}": alpha_coverage(alpha, threshold)
		for threshold in thresholds
	}
	reference_means = {
		f"coverage_gt_{threshold}": sum(
			float(metrics[f"coverage_gt_{threshold}"])
			for metrics in reference_metrics
		)
		/ len(reference_metrics)
		for threshold in thresholds
	}
	maximum_delta = 0.15
	deltas = {
		key: abs(candidate_coverage[key] - reference_means[key])
		for key in candidate_coverage
	}
	if any(delta > maximum_delta for delta in deltas.values()):
		raise ValueError(
			"Advisor alpha silhouette diverges from the six canonical vanilla cards: "
			f"candidate={candidate_coverage}, means={reference_means}, deltas={deltas}"
		)
	candidate_bbox = threshold_bbox(alpha, 32)
	reference_left = min(int(metrics["bbox_gt_32"][0]) for metrics in reference_metrics)
	reference_top = min(int(metrics["bbox_gt_32"][1]) for metrics in reference_metrics)
	reference_right = max(int(metrics["bbox_gt_32"][2]) for metrics in reference_metrics)
	reference_bottom = max(int(metrics["bbox_gt_32"][3]) for metrics in reference_metrics)
	if (
		abs(candidate_bbox[0] - reference_left) > 3
		or abs(candidate_bbox[1] - reference_top) > 3
		or abs(candidate_bbox[2] - reference_right) > 3
		or abs(candidate_bbox[3] - reference_bottom) > 3
	):
		raise ValueError(
			"Advisor native alpha bbox does not match the vanilla footprint: "
			f"candidate={candidate_bbox}, reference={(reference_left, reference_top, reference_right, reference_bottom)}"
		)

	candidate_mask = [
		value > ADVISOR_WINDOW_ALPHA_THRESHOLD for value in alpha.getdata()
	]
	jaccard_scores: list[float] = []
	for reference_mask in reference_masks:
		intersection = sum(
			candidate and reference
			for candidate, reference in zip(candidate_mask, reference_mask)
		)
		union = sum(
			candidate or reference
			for candidate, reference in zip(candidate_mask, reference_mask)
		)
		jaccard_scores.append(intersection / max(1, union))
	row_counts = [
		sum(candidate_mask[y * ADVISOR_SIZE[0] + x] for x in range(ADVISOR_SIZE[0]))
		for y in range(ADVISOR_SIZE[1])
	]
	column_counts = [
		sum(candidate_mask[y * ADVISOR_SIZE[0] + x] for y in range(ADVISOR_SIZE[1]))
		for x in range(ADVISOR_SIZE[0])
	]
	reference_row_means = [
		sum(
			sum(mask[y * ADVISOR_SIZE[0] + x] for x in range(ADVISOR_SIZE[0]))
			for mask in reference_masks
		)
		/ len(reference_masks)
		for y in range(ADVISOR_SIZE[1])
	]
	reference_column_means = [
		sum(
			sum(mask[y * ADVISOR_SIZE[0] + x] for y in range(ADVISOR_SIZE[1]))
			for mask in reference_masks
		)
		/ len(reference_masks)
		for x in range(ADVISOR_SIZE[0])
	]
	row_mae = sum(
		abs(candidate - reference)
		for candidate, reference in zip(row_counts, reference_row_means)
	) / (ADVISOR_SIZE[0] * ADVISOR_SIZE[1])
	column_mae = sum(
		abs(candidate - reference)
		for candidate, reference in zip(column_counts, reference_column_means)
	) / (ADVISOR_SIZE[0] * ADVISOR_SIZE[1])
	if min(jaccard_scores) < 0.84 or row_mae > 0.08 or column_mae > 0.08:
		raise ValueError(
			"Advisor row/column alpha envelope is not the vanilla dossier silhouette: "
			f"jaccard={jaccard_scores}, row_mae={row_mae:.4f}, "
			f"column_mae={column_mae:.4f}"
		)

	return {
		"size": list(finished.size),
		"alpha_extrema": list(alpha.getextrema()),
		"transparent_corners": corner_values,
		"bbox_gt_32": list(candidate_bbox),
		"coverage": {key: round(value, 6) for key, value in candidate_coverage.items()},
		"canonical_mean_coverage": {
			key: round(value, 6) for key, value in reference_means.items()
		},
		"canonical_absolute_delta": {
			key: round(value, 6) for key, value in deltas.items()
		},
		"canonical_alpha_jaccard": [round(value, 6) for value in jaccard_scores],
		"canonical_row_occupancy_mae": round(row_mae, 6),
		"canonical_column_occupancy_mae": round(column_mae, 6),
		"canonical_references": [str(reference_dir / name) for name in ADVISOR_REFERENCE_NAMES],
	}


def checker(size: tuple[int, int], tile: int = 8) -> Image.Image:
	background = Image.new("RGBA", size, (92, 92, 92, 255))
	draw = ImageDraw.Draw(background)
	for y in range(0, size[1], tile):
		for x in range(0, size[0], tile):
			if (x // tile + y // tile) % 2:
				draw.rectangle((x, y, min(x + tile - 1, size[0] - 1), min(y + tile - 1, size[1] - 1)), fill=(132, 132, 132, 255))
	return background


def make_review_sheet(
	source_crop: Image.Image,
	finished: Image.Image,
	mode: str,
	reference_dir: Path,
	output: Path,
) -> None:
	if mode == "advisor":
		items: list[tuple[str, Image.Image]] = [
			(
				"explicit source crop",
				ImageOps.fit(source_crop, ADVISOR_SIZE, Image.Resampling.LANCZOS),
			),
			("processed candidate", finished),
		]
		for name in ADVISOR_REFERENCE_NAMES:
			path = reference_dir / name
			if not path.is_file():
				raise FileNotFoundError(f"Missing review reference: {path}")
			with Image.open(path) as image:
				items.append((name.removesuffix(".png"), image.convert("RGBA")))

		scale = 4
		native_width, native_height = ADVISOR_SIZE
		enlarged_size = (native_width * scale, native_height * scale)
		cell_width = enlarged_size[0] + 24
		cell_height = native_height + enlarged_size[1] + 72
		sheet = Image.new(
			"RGBA",
			(cell_width * len(items), cell_height),
			(28, 30, 32, 255),
		)
		draw = ImageDraw.Draw(sheet)
		for index, (label, image) in enumerate(items):
			native = checker(ADVISOR_SIZE)
			native.alpha_composite(
				ImageOps.fit(image, ADVISOR_SIZE, Image.Resampling.LANCZOS)
			)
			enlarged = native.resize(enlarged_size, Image.Resampling.NEAREST)
			x = index * cell_width + 12
			native_x = x + (enlarged_size[0] - native_width) // 2
			sheet.alpha_composite(native, (native_x, 10))
			sheet.alpha_composite(enlarged, (x, native_height + 22))
			draw.text((x, native_height + enlarged_size[1] + 34), label, fill=(236, 236, 232, 255))
		output.parent.mkdir(parents=True, exist_ok=True)
		sheet.save(output)
		if not output.is_file() or output.stat().st_size == 0:
			raise RuntimeError(f"Advisor comparison sheet was not generated: {output}")
		return

	reference_names = ("den_thorvald_stauning.png", "fin_carl_mannerheim.png")
	display_size = LEADER_SIZE
	scale = 2

	items: list[tuple[str, Image.Image]] = [
		("explicit source crop", ImageOps.fit(source_crop, display_size, Image.Resampling.LANCZOS)),
		("processed candidate", finished),
	]
	for name in reference_names:
		path = reference_dir / name
		if not path.is_file():
			raise FileNotFoundError(f"Missing review reference: {path}")
		with Image.open(path) as image:
			items.append((name.removeprefix("vanilla_").removesuffix(".png"), image.convert("RGBA")))

	cell_width = display_size[0] * scale + 24
	cell_height = display_size[1] * scale + 44
	sheet = Image.new("RGBA", (cell_width * len(items), cell_height), (28, 30, 32, 255))
	draw = ImageDraw.Draw(sheet)
	for index, (label, image) in enumerate(items):
		preview = ImageOps.fit(image, display_size, Image.Resampling.LANCZOS).resize(
			(display_size[0] * scale, display_size[1] * scale),
			Image.Resampling.NEAREST if mode == "advisor" else Image.Resampling.LANCZOS,
		)
		base = checker(preview.size)
		base.alpha_composite(preview)
		x = index * cell_width + 12
		sheet.alpha_composite(base, (x, 10))
		draw.text((x, preview.height + 20), label, fill=(236, 236, 232, 255))
	output.parent.mkdir(parents=True, exist_ok=True)
	sheet.save(output)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("mode", choices=("leader", "advisor"))
	parser.add_argument("source", type=Path)
	parser.add_argument("output", type=Path)
	parser.add_argument(
		"--crop",
		nargs=4,
		type=int,
		metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
		required=True,
		help="Required head-and-shoulders crop in source pixels",
	)
	parser.add_argument(
		"--source-kind",
		choices=("real", "fictional", "collective", "symbolic"),
		required=True,
	)
	parser.add_argument(
		"--face-box",
		nargs=4,
		type=int,
		metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
		help=(
			"Advisor-only visible face bounds in original source pixels; required "
			"for native-size scale and placement validation"
		),
	)
	parser.add_argument("--review-sheet", type=Path, required=True)
	parser.add_argument("--metadata", type=Path)
	parser.add_argument("--reference-dir", type=Path)
	parser.add_argument(
		"--advisor-frame-overlay",
		type=Path,
		help="Required alpha-processed ImageGen frame overlay for advisor mode",
	)
	parser.add_argument(
		"--advisor-frame-source",
		type=Path,
		help="Required retained full-resolution ImageGen source for the frame overlay",
	)
	parser.add_argument(
		"--advisor-paper-overlay",
		type=Path,
		help="Required alpha-processed shadowless ImageGen paper overlay for advisor mode",
	)
	parser.add_argument(
		"--advisor-paper-source",
		type=Path,
		help="Required retained full-resolution shadowless ImageGen paper source",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	if not args.source.is_file():
		raise FileNotFoundError(args.source)
	with Image.open(args.source) as image:
		source = image.convert("RGBA")
	crop_box = parse_crop(args.crop, source)
	source_crop = source.crop(crop_box)
	face_box: tuple[int, int, int, int] | None = None
	render_version = LEADER_RENDER_VERSION if args.mode == "leader" else ADVISOR_RENDER_VERSION
	seed_text = f"{args.source.resolve()}:{crop_box}:{args.source_kind}:{render_version}"
	if args.mode == "leader":
		finished = make_leader(source_crop, args.source_kind, seed_text)
		reference_dir = args.reference_dir or REFERENCE_ROOT / "leaders"
		overlay_metadata = None
		composition_metadata = None
		validation_metadata = None
	else:
		if args.face_box is None:
			raise ValueError("advisor mode requires --face-box in original source pixels")
		face_box = parse_face_box(args.face_box, source, crop_box)
		if args.advisor_frame_overlay is None or args.advisor_frame_source is None:
			raise ValueError(
				"advisor mode requires --advisor-frame-source and --advisor-frame-overlay; "
				"the processor never draws fallback dossier artwork"
			)
		if args.advisor_paper_overlay is None or args.advisor_paper_source is None:
			raise ValueError(
				"advisor mode requires --advisor-paper-source and --advisor-paper-overlay; "
				"paperless output is not the calibrated vanilla dossier family"
			)
		frame_overlay, frame_metadata = load_generated_layer(
			args.advisor_frame_overlay,
			args.advisor_frame_source,
			"frame",
		)
		paper_overlay, paper_metadata = load_generated_layer(
			args.advisor_paper_overlay,
			args.advisor_paper_source,
			"paper",
		)
		finished, composition_metadata = make_advisor(
			source_crop,
			args.source_kind,
			seed_text,
			frame_overlay,
			paper_overlay,
			crop_box,
			face_box,
		)
		reference_dir = args.reference_dir or REFERENCE_ROOT / "advisors"
		validation_metadata = validate_advisor_output(
			finished,
			reference_dir,
		)
		overlay_metadata = {
			"frame": frame_metadata,
			"paper": paper_metadata,
		}

	args.output.parent.mkdir(parents=True, exist_ok=True)
	finished.save(args.output)
	make_review_sheet(source_crop, finished, args.mode, reference_dir, args.review_sheet)

	metadata_path = args.metadata or args.output.with_suffix(args.output.suffix + ".json")
	metadata_path.parent.mkdir(parents=True, exist_ok=True)
	metadata = {
		"processor": ".agents/skills/hoi4-feature-assets/tools/advisor_icon_processing.py",
		"processor_version": PROCESSOR_VERSION,
		"processor_sha256": sha256_file(Path(__file__).resolve()),
		"render_version": render_version,
		"mode": args.mode,
		"source": str(args.source),
		"source_kind": args.source_kind,
		"crop": list(crop_box),
		"face_box": list(face_box) if face_box is not None else None,
		"output": str(args.output),
		"size": list(finished.size),
		"review_sheet": str(args.review_sheet),
		"reference_dir": str(reference_dir),
		"source_sha256": sha256_file(args.source),
		"generated_overlays": overlay_metadata,
		"advisor_composition": composition_metadata,
		"advisor_validation": validation_metadata,
		"composition_contract": (
			"crop_grade_resize_angle_alpha_shadow_composite_validate_export_only; "
			"all visible frame_paper artwork is ImageGen-authored; "
			"no programmatically drawn advisor-card artwork"
			if args.mode == "advisor"
			else "crop_grade_export_only; no programmatically drawn leader subject, emblem, or institutional scene"
		),
		"status": "candidate_requires_visual_approval",
	}
	metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
	main()
