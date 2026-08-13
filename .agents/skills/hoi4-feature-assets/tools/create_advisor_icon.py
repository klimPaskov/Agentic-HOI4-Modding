"""Place a uniformly scaled portrait beneath the canonical HOI4 advisor template.

The complete source canvas is loaded without a pre-crop or warp, resized with
one shared scale factor until it covers the measured opening plus a controlled
under-frame bleed, and centered behind the frame. The bleed remains wholly
beneath nontransparent frame pixels, preventing translucent inner-edge pixels
from revealing an alpha seam without stretching the portrait. The script writes
the required native and 4x review PNGs,
placement study, 8x alignment overlay, transform metadata, and a one-level
32-bit BGRA DDS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


CARD_SIZE = (65, 67)
TEMPLATE_OPENING_CENTER = (24.7615, 30.6451)
MIN_VISIBLE_ROTATION = 0.25
OPENING_MASK_ALPHA_THRESHOLD = 192
OPENING_GEOMETRY_ALPHA_THRESHOLD = 128
MAX_ALIGNMENT_ERROR = 0.05
MAX_OPENING_CENTER_OFFSET = 0.001
MAX_OPENING_SIZE_ERROR = 0.01
UNDER_FRAME_BLEED_PIXELS = 2
PORTRAIT_EDGE_GUARD_PIXELS = 1
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = (
	SKILL_ROOT
	/ "assets"
	/ "vanilla_reference"
	/ "portraits"
	/ "advisors"
	/ "advisor_template.png"
)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--source", type=Path, required=True)
	parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
	parser.add_argument("--preview", type=Path, required=True)
	parser.add_argument(
		"--review-preview",
		type=Path,
		required=True,
		help="Required nearest-neighbour 4x review PNG for visual inspection.",
	)
	parser.add_argument(
		"--placement-study",
		type=Path,
		required=True,
		help="Required contact sheet of explicitly supplied placement candidates.",
	)
	parser.add_argument(
		"--alignment-preview",
		type=Path,
		required=True,
		help="Required 8x overlay: opening red, fill plane green, covering portrait yellow.",
	)
	parser.add_argument(
		"--study-candidate",
		type=float,
		nargs=5,
		action="append",
		required=True,
		metavar=("WIDTH", "HEIGHT", "RIGHT", "DOWN", "ROTATION"),
		help=(
			"Placement-study candidate. Repeat for each candidate; the selected "
			"--portrait-size, --portrait-offset, and --rotation must match one."
		),
	)
	parser.add_argument("--output", type=Path, required=True)
	parser.add_argument(
		"--metadata",
		type=Path,
		required=True,
		help="Required JSON record of source geometry, transforms, and output hashes.",
	)
	parser.add_argument(
		"--portrait-size",
		type=float,
		nargs=2,
		metavar=("WIDTH", "HEIGHT"),
		required=True,
		help="Required pre-rotation opening-fill plane size; must match measured geometry.",
	)
	parser.add_argument(
		"--portrait-offset",
		type=float,
		nargs=2,
		metavar=("RIGHT", "DOWN"),
		required=True,
		help="Required offset from the measured opening center; canonical cards require 0 0.",
	)
	parser.add_argument(
		"--rotation",
		type=float,
		required=True,
		help="Required portrait rotation in degrees; must match the measured opening within 0.05 degrees.",
	)
	parser.add_argument(
		"--allow-zero-rotation",
		action="store_true",
		help=(
			"Permit a near-zero rotation only for an independently reviewed exception. "
			"The default rejects the neutral transform that caused frame-only cards."
		),
	)
	parser.add_argument(
		"--sepia-strength",
		type=float,
		default=0.18,
		help="Portrait-only sepia blend from 0.0 to 1.0 (default: 0.18).",
	)
	return parser.parse_args()


def validate_transform(
	portrait_size: tuple[float, float],
	portrait_offset: tuple[float, float],
	rotation: float,
	allow_zero_rotation: bool = False,
) -> None:
	if portrait_size[0] <= 0.0 or portrait_size[1] <= 0.0:
		raise ValueError("--portrait-size values must be positive")
	if not all(math.isfinite(value) for value in (*portrait_size, *portrait_offset, rotation)):
		raise ValueError("Advisor placement values must be finite")
	if not allow_zero_rotation and abs(rotation) < MIN_VISIBLE_ROTATION:
		raise ValueError(
			"Advisor dossier portraits require an explicit visible rotation aligned to "
			"the template opening. Use --allow-zero-rotation only after an independent "
			"visual review approves an unrotated exception."
		)


def prepare_portrait(
	source: Image.Image,
	sepia_strength: float,
) -> Image.Image:
	portrait = source.convert("RGBA")
	if not 0.0 <= sepia_strength <= 1.0:
		raise ValueError("--sepia-strength must be between 0.0 and 1.0")

	alpha = portrait.getchannel("A")
	sepia = ImageOps.colorize(
		ImageOps.grayscale(portrait),
		black=(24, 18, 12),
		white=(244, 224, 188),
	)
	portrait = Image.blend(portrait.convert("RGB"), sepia, sepia_strength)
	portrait.putalpha(alpha)
	return portrait


def calculate_covering_portrait_geometry(
	source_size: tuple[int, int],
	opening_size: tuple[float, float],
) -> dict[str, object]:
	if source_size[0] <= 0 or source_size[1] <= 0:
		raise ValueError("Advisor source dimensions must be positive")
	source_aspect = source_size[0] / source_size[1]
	opening_aspect = opening_size[0] / opening_size[1]
	if source_aspect >= opening_aspect:
		content_size = (opening_size[1] * source_aspect, opening_size[1])
		horizontal_clip = content_size[0] - opening_size[0]
		frame_clip = (horizontal_clip / 2.0, 0.0, horizontal_clip / 2.0, 0.0)
	else:
		content_size = (opening_size[0], opening_size[0] / source_aspect)
		vertical_clip = content_size[1] - opening_size[1]
		frame_clip = (0.0, vertical_clip / 2.0, 0.0, vertical_clip / 2.0)
	return {
		"content_size": content_size,
		"frame_clip": frame_clip,
		"local_center_offset": (0.0, 0.0),
		"source_aspect": source_aspect,
		"content_aspect": content_size[0] / content_size[1],
	}


def rotate_local_offset(
	center: tuple[float, float],
	local_offset: tuple[float, float],
	rotation: float,
) -> tuple[float, float]:
	radians = math.radians(rotation)
	axis_x = (math.cos(radians), math.sin(radians))
	axis_y = (-math.sin(radians), math.cos(radians))
	return (
		center[0] + local_offset[0] * axis_x[0] + local_offset[1] * axis_y[0],
		center[1] + local_offset[0] * axis_x[1] + local_offset[1] * axis_y[1],
	)


def render_portrait_layer(
	portrait: Image.Image,
	target_size: tuple[float, float],
	center: tuple[float, float],
	rotation: float,
) -> Image.Image:
	scale_x = target_size[0] / portrait.width
	scale_y = target_size[1] / portrait.height
	if not math.isclose(scale_x, scale_y, rel_tol=1e-9, abs_tol=1e-12):
		raise ValueError(
			"Advisor portraits must use one uniform scale factor; anisotropic resizing "
			"would stretch the source portrait."
		)
	angle = math.radians(rotation)
	cosine = math.cos(angle)
	sine = math.sin(angle)
	a = cosine / scale_x
	b = sine / scale_x
	d = -sine / scale_y
	e = cosine / scale_y
	source_center_x = portrait.width / 2.0
	source_center_y = portrait.height / 2.0
	c = source_center_x - a * center[0] - b * center[1]
	f = source_center_y - d * center[0] - e * center[1]
	return portrait.transform(
		CARD_SIZE,
		Image.Transform.AFFINE,
		(a, b, c, d, e, f),
		resample=Image.Resampling.BICUBIC,
		fillcolor=(0, 0, 0, 0),
	)


def load_template(path: Path) -> Image.Image:
	template = Image.open(path).convert("RGBA")
	if template.size != CARD_SIZE:
		raise ValueError(
			f"Template must be {CARD_SIZE[0]}x{CARD_SIZE[1]}, got "
			f"{template.width}x{template.height}"
		)
	return template


def create_opening_mask(
	template: Image.Image,
	alpha_threshold: int = OPENING_MASK_ALPHA_THRESHOLD,
) -> Image.Image:
	"""Return the largest enclosed transparent component in the dossier frame."""
	opening = find_enclosed_opening(template, alpha_threshold)
	mask = Image.new("L", CARD_SIZE, 0)
	pixels = mask.load()
	for x, y in opening:
		pixels[x, y] = 255
	return mask


def create_portrait_bleed_mask(
	template: Image.Image,
	bleed_pixels: int = UNDER_FRAME_BLEED_PIXELS,
) -> Image.Image:
	"""Expand the opening beneath the frame without entering transparent exterior pixels."""
	if bleed_pixels < 0:
		raise ValueError("Advisor portrait bleed must not be negative")
	opening_mask = create_opening_mask(template)
	if bleed_pixels == 0:
		return opening_mask
	bleed_mask = opening_mask.filter(ImageFilter.MaxFilter(bleed_pixels * 2 + 1))
	opening_pixels = opening_mask.load()
	bleed_pixels_data = bleed_mask.load()
	template_alpha = template.getchannel("A").load()
	unsafe_pixels = [
		(x, y)
		for y in range(template.height)
		for x in range(template.width)
		if bleed_pixels_data[x, y]
		and not opening_pixels[x, y]
		and template_alpha[x, y] == 0
	]
	if unsafe_pixels:
		raise ValueError(
			"Advisor under-frame bleed reaches transparent exterior pixels; "
			"reduce UNDER_FRAME_BLEED_PIXELS or use a compatible canonical template."
		)
	return bleed_mask


def calculate_under_frame_fill_size(
	opening_size: tuple[float, float],
	bleed_pixels: int = UNDER_FRAME_BLEED_PIXELS,
	edge_guard_pixels: int = PORTRAIT_EDGE_GUARD_PIXELS,
) -> tuple[float, float]:
	"""Return the local fill plane needed to cover the bleed mask after resampling."""
	if bleed_pixels < 0 or edge_guard_pixels < 0:
		raise ValueError("Advisor portrait bleed and edge guard must not be negative")
	extension = 2.0 * (bleed_pixels + edge_guard_pixels)
	return (opening_size[0] + extension, opening_size[1] + extension)


def audit_portrait_alpha_coverage(
	card: Image.Image,
	template: Image.Image,
) -> dict[str, int]:
	"""Count visible opening gaps, translucent inner-edge gaps, and exterior spills."""
	opening_mask = create_opening_mask(template)
	bleed_mask = create_portrait_bleed_mask(template)
	opening_pixels = opening_mask.load()
	bleed_pixels = bleed_mask.load()
	template_alpha = template.getchannel("A").load()
	card_alpha = card.getchannel("A").load()
	opening_alpha_gap_pixels = 0
	inner_edge_alpha_gap_pixels = 0
	exterior_alpha_leak_pixels = 0
	for y in range(template.height):
		for x in range(template.width):
			if opening_pixels[x, y] and card_alpha[x, y] < 255:
				opening_alpha_gap_pixels += 1
			elif (
				bleed_pixels[x, y]
				and 0 < template_alpha[x, y] < 255
				and card_alpha[x, y] < 255
			):
				inner_edge_alpha_gap_pixels += 1
			if not bleed_pixels[x, y] and template_alpha[x, y] == 0 and card_alpha[x, y] > 0:
				exterior_alpha_leak_pixels += 1
	return {
		"opening_alpha_gap_pixels": opening_alpha_gap_pixels,
		"inner_edge_alpha_gap_pixels": inner_edge_alpha_gap_pixels,
		"exterior_alpha_leak_pixels": exterior_alpha_leak_pixels,
	}


def find_enclosed_opening(
	template: Image.Image,
	alpha_threshold: int,
) -> set[tuple[int, int]]:
	if not 0 <= alpha_threshold <= 255:
		raise ValueError("Advisor opening alpha threshold must be between 0 and 255")
	alpha = template.getchannel("A")
	available = {
		(x, y)
		for y in range(template.height)
		for x in range(template.width)
		if alpha.getpixel((x, y)) <= alpha_threshold
	}
	enclosed: list[set[tuple[int, int]]] = []
	while available:
		start = available.pop()
		component = {start}
		frontier = [start]
		touches_edge = False
		while frontier:
			x, y = frontier.pop()
			if x in (0, template.width - 1) or y in (0, template.height - 1):
				touches_edge = True
			for neighbour in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
				if neighbour in available:
					available.remove(neighbour)
					component.add(neighbour)
					frontier.append(neighbour)
		if not touches_edge:
			enclosed.append(component)
	if not enclosed:
		raise ValueError("Advisor template has no enclosed transparent portrait opening")
	return max(enclosed, key=len)


def measure_opening_geometry(template: Image.Image) -> dict[str, object]:
	opening = find_enclosed_opening(template, OPENING_GEOMETRY_ALPHA_THRESHOLD)

	def measure_at_angle(angle: float) -> tuple[float, float, float, float, float]:
		radians = math.radians(angle)
		cosine = math.cos(radians)
		sine = math.sin(radians)
		x_values = [x * cosine + y * sine for x, y in opening]
		y_values = [-x * sine + y * cosine for x, y in opening]
		width = max(x_values) - min(x_values)
		height = max(y_values) - min(y_values)
		center_x = (min(x_values) + max(x_values)) / 2.0
		center_y = (min(y_values) + max(y_values)) / 2.0
		return width * height, width, height, center_x, center_y

	coarse = []
	for step in range(-150, 151):
		angle = step / 10.0
		area, width, height, center_x, center_y = measure_at_angle(angle)
		if width <= height:
			coarse.append((area, abs(angle), angle, width, height, center_x, center_y))
	if not coarse:
		raise ValueError("Unable to derive vertical advisor opening geometry")
	coarse_angle = min(coarse)[2]
	fine = []
	for step in range(-20, 21):
		angle = coarse_angle + step / 100.0
		area, width, height, center_x, center_y = measure_at_angle(angle)
		if width <= height:
			fine.append((area, abs(angle), angle, width, height, center_x, center_y))
	_, _, angle, width, height, local_center_x, local_center_y = min(fine)
	radians = math.radians(angle)
	cosine = math.cos(radians)
	sine = math.sin(radians)
	center = (
		local_center_x * cosine - local_center_y * sine,
		local_center_x * sine + local_center_y * cosine,
	)
	return {
		"center": center,
		"size": (width, height),
		"rotation": angle,
		"alpha_threshold": OPENING_GEOMETRY_ALPHA_THRESHOLD,
	}


def transformed_portrait_bounds(
	portrait_size: tuple[float, float],
	center: tuple[float, float],
	rotation: float,
) -> tuple[float, float, float, float]:
	angle = math.radians(rotation)
	cosine = abs(math.cos(angle))
	sine = abs(math.sin(angle))
	rotated_width = portrait_size[0] * cosine + portrait_size[1] * sine
	rotated_height = portrait_size[0] * sine + portrait_size[1] * cosine
	return (
		center[0] - rotated_width / 2.0,
		center[1] - rotated_height / 2.0,
		center[0] + rotated_width / 2.0,
		center[1] + rotated_height / 2.0,
	)


def rotated_rectangle_corners(
	size: tuple[float, float],
	center: tuple[float, float],
	rotation: float,
) -> list[tuple[float, float]]:
	radians = math.radians(rotation)
	axis_x = (math.cos(radians), math.sin(radians))
	axis_y = (-math.sin(radians), math.cos(radians))
	return [
		(
			center[0] + sign_x * size[0] / 2.0 * axis_x[0] + sign_y * size[1] / 2.0 * axis_y[0],
			center[1] + sign_x * size[0] / 2.0 * axis_x[1] + sign_y * size[1] / 2.0 * axis_y[1],
		)
		for sign_x, sign_y in ((-1, -1), (1, -1), (1, 1), (-1, 1))
	]


def validate_fit_to_opening(
	portrait_size: tuple[float, float],
	center: tuple[float, float],
	rotation: float,
	opening_geometry: dict[str, object],
	inset: float = 0.0,
) -> tuple[float, float, float, float]:
	opening_center = opening_geometry["center"]
	opening_size = opening_geometry["size"]
	opening_rotation = opening_geometry["rotation"]
	delta = math.radians(rotation - opening_rotation)
	delta_cosine = abs(math.cos(delta))
	delta_sine = abs(math.sin(delta))
	half_width = portrait_size[0] * delta_cosine / 2.0 + portrait_size[1] * delta_sine / 2.0
	half_height = portrait_size[0] * delta_sine / 2.0 + portrait_size[1] * delta_cosine / 2.0
	opening_radians = math.radians(opening_rotation)
	opening_cosine = math.cos(opening_radians)
	opening_sine = math.sin(opening_radians)
	difference_x = center[0] - opening_center[0]
	difference_y = center[1] - opening_center[1]
	local_center_x = difference_x * opening_cosine + difference_y * opening_sine
	local_center_y = -difference_x * opening_sine + difference_y * opening_cosine
	local_bounds = (
		local_center_x - half_width,
		local_center_y - half_height,
		local_center_x + half_width,
		local_center_y + half_height,
	)
	limit_x = opening_size[0] / 2.0 - inset
	limit_y = opening_size[1] / 2.0 - inset
	if (
		local_bounds[0] < -limit_x
		or local_bounds[1] < -limit_y
		or local_bounds[2] > limit_x
		or local_bounds[3] > limit_y
	):
		raise ValueError(
			"The advisor opening-fill plane must remain inside the measured rotated "
			"dossier opening before masking; selected local bounds "
			f"are {tuple(round(value, 3) for value in local_bounds)}, opening half-size "
			f"limits are ({limit_x:.3f}, {limit_y:.3f})."
		)
	return local_bounds


def validate_opening_alignment(
	portrait_size: tuple[float, float],
	portrait_offset: tuple[float, float],
	rotation: float,
	opening_geometry: dict[str, object],
) -> float:
	opening_rotation = opening_geometry["rotation"]
	rotation_delta = (rotation - opening_rotation + 90.0) % 180.0 - 90.0
	if abs(rotation_delta) > MAX_ALIGNMENT_ERROR:
		raise ValueError(
			"Advisor portrait rotation must align with the measured dossier opening; "
			f"selected rotation is {rotation:.4f}, measured rotation is "
			f"{opening_rotation:.4f}, maximum error is {MAX_ALIGNMENT_ERROR:.2f} degrees."
		)
	if any(abs(value) > MAX_OPENING_CENTER_OFFSET for value in portrait_offset):
		raise ValueError(
			"Advisor portrait center must remain aligned with the measured dossier "
			f"opening; canonical cards require a 0 0 offset."
		)
	opening_size = opening_geometry["size"]
	size_error = (
		portrait_size[0] - opening_size[0],
		portrait_size[1] - opening_size[1],
	)
	if any(abs(value) > MAX_OPENING_SIZE_ERROR for value in size_error):
		raise ValueError(
			"Canonical advisor portraits must resize the complete image plane to the "
			"measured opening size; selected size is "
			f"({portrait_size[0]:.6f}, {portrait_size[1]:.6f}), measured size is "
			f"({opening_size[0]:.6f}, {opening_size[1]:.6f})."
		)
	return rotation_delta


def compose(
	source: Image.Image,
	template: Image.Image,
	template_center: tuple[float, float],
	portrait_size: tuple[float, float],
	portrait_offset: tuple[float, float],
	rotation: float,
	sepia_strength: float,
) -> Image.Image:
	portrait = prepare_portrait(source, sepia_strength)
	opening_center = (
		template_center[0] + portrait_offset[0],
		template_center[1] + portrait_offset[1],
	)
	under_frame_fill_size = calculate_under_frame_fill_size(portrait_size)
	covering = calculate_covering_portrait_geometry(portrait.size, under_frame_fill_size)
	portrait_center = rotate_local_offset(
		opening_center,
		covering["local_center_offset"],
		rotation,
	)
	card = render_portrait_layer(
		portrait,
		covering["content_size"],
		portrait_center,
		rotation,
	)
	bleed_mask = create_portrait_bleed_mask(template)
	card.putalpha(ImageChops.multiply(card.getchannel("A"), bleed_mask))
	card.alpha_composite(template)
	return card


def normalise_study_candidates(
	values: list[list[float]] | None,
) -> list[tuple[float, float, float, float, float]]:
	if not values:
		return []
	return [tuple(candidate) for candidate in values]


def transform_matches_candidate(
	portrait_size: tuple[float, float],
	portrait_offset: tuple[float, float],
	rotation: float,
	candidate: tuple[float, float, float, float, float],
) -> bool:
	selected = (*portrait_size, *portrait_offset, rotation)
	return all(math.isclose(left, right, abs_tol=0.001) for left, right in zip(selected, candidate))


def write_placement_study(
	source: Image.Image,
	template: Image.Image,
	template_center: tuple[float, float],
	candidates: list[tuple[float, float, float, float, float]],
	sepia_strength: float,
	output: Path,
	allow_zero_rotation: bool = False,
) -> None:
	columns = min(3, len(candidates))
	rows = math.ceil(len(candidates) / columns)
	preview_size = (CARD_SIZE[0] * 4, CARD_SIZE[1] * 4)
	cell_width = preview_size[0] + 24
	cell_height = preview_size[1] + 46
	study = Image.new("RGB", (columns * cell_width, rows * cell_height), (20, 22, 20))
	draw = ImageDraw.Draw(study)
	opening_geometry = measure_opening_geometry(template)
	template_center = opening_geometry["center"]
	for index, candidate in enumerate(candidates):
		width, height, right, down, rotation = candidate
		validate_transform(
			(width, height),
			(right, down),
			rotation,
			allow_zero_rotation,
		)
		validate_opening_alignment((width, height), (right, down), rotation, opening_geometry)
		portrait_center = (
			template_center[0] + right,
			template_center[1] + down,
		)
		validate_fit_to_opening(
			(width, height),
			portrait_center,
			rotation,
			opening_geometry,
		)
		card = compose(
			source,
			template,
			template_center,
			(width, height),
			(right, down),
			rotation,
			sepia_strength,
		)
		x = (index % columns) * cell_width + 12
		y = (index // columns) * cell_height + 10
		large = card.resize(preview_size, Image.Resampling.NEAREST)
		study.paste(large.convert("RGB"), (x, y))
		label = (
			f"{index + 1}: {width:g}x{height:g}  "
			f"off {right:g},{down:g}  rot {rotation:g}"
		)
		draw.text((x, y + preview_size[1] + 9), label, fill=(232, 232, 224))
	output.parent.mkdir(parents=True, exist_ok=True)
	study.save(output)


def write_alignment_preview(
	card: Image.Image,
	opening_geometry: dict[str, object],
	opening_fill_size: tuple[float, float],
	opening_fill_center: tuple[float, float],
	rotation: float,
	output: Path,
	content_size: tuple[float, float] | None = None,
	content_center: tuple[float, float] | None = None,
) -> None:
	scale = 8
	preview = card.convert("RGBA").resize(
		(CARD_SIZE[0] * scale, CARD_SIZE[1] * scale),
		Image.Resampling.NEAREST,
	)
	draw = ImageDraw.Draw(preview)
	opening_points = rotated_rectangle_corners(
		opening_geometry["size"],
		opening_geometry["center"],
		opening_geometry["rotation"],
	)
	portrait_points = rotated_rectangle_corners(opening_fill_size, opening_fill_center, rotation)
	opening_points = [(x * scale, y * scale) for x, y in opening_points]
	portrait_points = [(x * scale, y * scale) for x, y in portrait_points]
	draw.line(opening_points + [opening_points[0]], fill=(255, 48, 48, 255), width=2)
	draw.line(portrait_points + [portrait_points[0]], fill=(48, 255, 96, 255), width=2)
	if content_size and content_center:
		content_points = rotated_rectangle_corners(content_size, content_center, rotation)
		content_points = [(x * scale, y * scale) for x, y in content_points]
		draw.line(content_points + [content_points[0]], fill=(255, 220, 48, 255), width=2)
	output.parent.mkdir(parents=True, exist_ok=True)
	preview.save(output)


def sha256(path: Path) -> str:
	digest = hashlib.sha256()
	with path.open("rb") as source:
		for chunk in iter(lambda: source.read(1024 * 1024), b""):
			digest.update(chunk)
	return digest.hexdigest()


def write_metadata(
	output: Path,
	source_path: Path,
	source_size: tuple[int, int],
	template_path: Path,
	preview_path: Path,
	runtime_path: Path,
	alignment_path: Path,
	template_center: tuple[float, float],
	portrait_size: tuple[float, float],
	portrait_offset: tuple[float, float],
	rotation: float,
	sepia_strength: float,
	study_path: Path | None,
	candidates: list[tuple[float, float, float, float, float]],
	allow_zero_rotation: bool,
) -> None:
	template = load_template(template_path)
	opening_mask = create_opening_mask(template)
	bleed_mask = create_portrait_bleed_mask(template)
	opening_geometry = measure_opening_geometry(template)
	template_center = opening_geometry["center"]
	portrait_center = (
		template_center[0] + portrait_offset[0],
		template_center[1] + portrait_offset[1],
	)
	under_frame_fill_size = calculate_under_frame_fill_size(portrait_size)
	covering = calculate_covering_portrait_geometry(source_size, under_frame_fill_size)
	content_center = rotate_local_offset(
		portrait_center,
		covering["local_center_offset"],
		rotation,
	)
	rotation_delta = validate_opening_alignment(
		portrait_size,
		portrait_offset,
		rotation,
		opening_geometry,
	)
	portrait_bounds = validate_fit_to_opening(
		portrait_size,
		portrait_center,
		rotation,
		opening_geometry,
	)
	source_aspect = source_size[0] / source_size[1]
	card = Image.open(preview_path).convert("RGBA")
	alpha_coverage = audit_portrait_alpha_coverage(card, template)
	payload = {
		"workflow": "hoi4-advisor-dossier-v4",
		"source": {
			"path": str(source_path),
			"sha256": sha256(source_path),
			"original_size": list(source_size),
			"native_output_canvas": list(CARD_SIZE),
		},
		"template": {
			"path": str(template_path),
			"sha256": sha256(template_path),
			"opening_center": list(template_center),
			"opening_size": list(opening_geometry["size"]),
			"opening_rotation_degrees": opening_geometry["rotation"],
			"opening_geometry_alpha_threshold": opening_geometry["alpha_threshold"],
		},
		"selected_transform": {
			"portrait_size": list(portrait_size),
			"portrait_offset": list(portrait_offset),
			"portrait_center": list(portrait_center),
			"rotation_degrees": rotation,
			"rotation_alignment_error_degrees": round(rotation_delta, 6),
			"sepia_strength": sepia_strength,
			"zero_rotation_exception": allow_zero_rotation,
			"fit_to_opening": {
				"safety_mask_bbox": list(opening_mask.getbbox()),
				"under_frame_bleed_mask_bbox": list(bleed_mask.getbbox()),
				"opening_local_bounds": [round(value, 6) for value in portrait_bounds],
				"required_inset_pixels": 0.0,
				"under_frame_bleed_pixels": UNDER_FRAME_BLEED_PIXELS,
				"resampling_edge_guard_pixels": PORTRAIT_EDGE_GUARD_PIXELS,
				"alpha_coverage": alpha_coverage,
			},
			"complete_image_resize": {
				"mode": "aspect_preserving_cover_with_under_frame_bleed",
				"source_aspect": round(source_aspect, 6),
				"content_aspect": round(covering["content_aspect"], 6),
				"opening_fill_size": list(portrait_size),
				"under_frame_fill_size": list(under_frame_fill_size),
				"covering_content_size": list(covering["content_size"]),
				"covering_content_center": list(content_center),
				"source_pre_crop": False,
				"frame_clip_pixels": list(covering["frame_clip"]),
				"frame_clip": True,
				"stretch": False,
			},
		},
		"placement_candidates": [
			{
				"portrait_size": [width, height],
				"portrait_offset": [right, down],
				"rotation_degrees": candidate_rotation,
			}
			for width, height, right, down, candidate_rotation in candidates
		],
		"outputs": {
			"preview": {"path": str(preview_path), "sha256": sha256(preview_path)},
			"runtime_dds": {"path": str(runtime_path), "sha256": sha256(runtime_path)},
			"alignment_preview": {
				"path": str(alignment_path),
				"sha256": sha256(alignment_path),
			},
		},
	}
	if study_path:
		payload["outputs"]["placement_study"] = {
			"path": str(study_path),
			"sha256": sha256(study_path),
		}
	output.parent.mkdir(parents=True, exist_ok=True)
	output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_bgra_dds(image: Image.Image, output: Path) -> None:
	image = image.convert("RGBA")
	width, height = image.size
	flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000
	pixel_format = struct.pack(
		"<IIIIIIII",
		32,
		0x41,
		0,
		32,
		0x00FF0000,
		0x0000FF00,
		0x000000FF,
		0xFF000000,
	)
	header = struct.pack(
		"<IIIIIII11I",
		124,
		flags,
		height,
		width,
		width * 4,
		0,
		0,
		*([0] * 11),
	)
	header += pixel_format
	header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
	if len(header) != 124:
		raise AssertionError(f"Unexpected DDS header size: {len(header)}")

	raw = bytearray()
	pixels = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
	for red, green, blue, alpha in pixels:
		raw.extend((blue, green, red, alpha))

	output.parent.mkdir(parents=True, exist_ok=True)
	output.write_bytes(b"DDS " + header + raw)


def main() -> None:
	args = parse_args()
	source_path = args.source.resolve()
	template_path = args.template.resolve()
	source = Image.open(source_path)
	source_size = source.size
	template = load_template(template_path)
	opening_geometry = measure_opening_geometry(template)
	portrait_size = tuple(args.portrait_size)
	portrait_offset = tuple(args.portrait_offset)
	template_center = opening_geometry["center"]
	validate_transform(
		portrait_size,
		portrait_offset,
		args.rotation,
		args.allow_zero_rotation,
	)
	validate_opening_alignment(
		portrait_size,
		portrait_offset,
		args.rotation,
		opening_geometry,
	)
	portrait_center = (
		template_center[0] + portrait_offset[0],
		template_center[1] + portrait_offset[1],
	)
	validate_fit_to_opening(
		portrait_size,
		portrait_center,
		args.rotation,
		opening_geometry,
	)
	candidates = normalise_study_candidates(args.study_candidate)
	if bool(args.placement_study) != bool(candidates):
		raise ValueError("--placement-study and at least one --study-candidate must be used together")
	if candidates and not any(
		transform_matches_candidate(portrait_size, portrait_offset, args.rotation, candidate)
		for candidate in candidates
	):
		raise ValueError("The selected advisor transform must match one --study-candidate")
	card = compose(
		source,
		template,
		template_center,
		portrait_size,
		portrait_offset,
		args.rotation,
		args.sepia_strength,
	)
	alpha_coverage = audit_portrait_alpha_coverage(card, template)
	if any(alpha_coverage.values()):
		raise ValueError(
			"Advisor portrait alpha coverage failed: "
			+ ", ".join(f"{key}={value}" for key, value in alpha_coverage.items())
		)
	preview = args.preview.resolve()
	output = args.output.resolve()
	preview.parent.mkdir(parents=True, exist_ok=True)
	card.save(preview)
	review_preview = args.review_preview.resolve()
	review_preview.parent.mkdir(parents=True, exist_ok=True)
	card.resize((CARD_SIZE[0] * 4, CARD_SIZE[1] * 4), Image.Resampling.NEAREST).save(review_preview)
	write_bgra_dds(card, output)
	under_frame_fill_size = calculate_under_frame_fill_size(portrait_size)
	covering = calculate_covering_portrait_geometry(source_size, under_frame_fill_size)
	content_center = rotate_local_offset(
		portrait_center,
		covering["local_center_offset"],
		args.rotation,
	)
	alignment_path = args.alignment_preview.resolve()
	write_alignment_preview(
		card,
		opening_geometry,
		portrait_size,
		portrait_center,
		args.rotation,
		alignment_path,
		covering["content_size"],
		content_center,
	)
	study_path = args.placement_study.resolve()
	write_placement_study(
		source,
		template,
		template_center,
		candidates,
		args.sepia_strength,
		study_path,
		args.allow_zero_rotation,
	)

	reopened = Image.open(output).convert("RGBA")
	if reopened.size != CARD_SIZE:
		raise ValueError(f"DDS reopened at {reopened.size}, expected {CARD_SIZE}")
	if reopened.tobytes() != card.tobytes():
		raise ValueError("DDS decoded pixels differ from the preview")
	expected_length = 128 + CARD_SIZE[0] * CARD_SIZE[1] * 4
	if output.stat().st_size != expected_length:
		raise ValueError("DDS length does not match one-level BGRA layout")
	write_metadata(
		args.metadata.resolve(),
		source_path,
		source_size,
		template_path,
		preview,
		output,
		alignment_path,
		template_center,
		portrait_size,
		portrait_offset,
		args.rotation,
		args.sepia_strength,
		study_path,
		candidates,
		args.allow_zero_rotation,
	)


if __name__ == "__main__":
	main()
