#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Iterable, Tuple

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
    RESAMPLE_BICUBIC = Image.Resampling.BICUBIC
except AttributeError:
    RESAMPLE_LANCZOS = Image.LANCZOS
    RESAMPLE_BICUBIC = Image.BICUBIC

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def clamp(value: int) -> int:
    return max(0, min(255, value))


def ensure_png_path(path: Path) -> Path:
    if path.suffix == "":
        return path.with_suffix(".png")
    if path.suffix.lower() != ".png":
        raise ValueError("Report event card output must be a PNG so transparency is preserved")
    return path


def cover_crop(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    target_w, target_h = target_size
    source_w, source_h = image.size

    scale = max(target_w / source_w, target_h / source_h)
    resized_w = int(round(source_w * scale))
    resized_h = int(round(source_h * scale))

    resized = image.resize((resized_w, resized_h), RESAMPLE_LANCZOS)
    left = (resized_w - target_w) // 2
    top = (resized_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def add_grain(image: Image.Image, strength: int, seed: int) -> Image.Image:
    if strength <= 0:
        return image

    rng = random.Random(seed)
    rgba = image.convert("RGBA")
    out = Image.new("RGBA", rgba.size)
    source_pixels = rgba.load()
    out_pixels = out.load()

    for y in range(rgba.size[1]):
        for x in range(rgba.size[0]):
            r, g, b, a = source_pixels[x, y]
            noise = rng.randint(-strength, strength)
            out_pixels[x, y] = (clamp(r + noise), clamp(g + noise), clamp(b + noise), a)

    return out


def apply_report_photo_tone(image: Image.Image, grain: int, seed: int) -> Image.Image:
    alpha = image.getchannel("A") if image.mode == "RGBA" else Image.new("L", image.size, 255)

    rgb = image.convert("RGB")
    rgb = ImageOps.autocontrast(rgb, cutoff=1)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.10)
    rgb = ImageEnhance.Brightness(rgb).enhance(0.98)

    grayscale = ImageOps.grayscale(rgb)
    sepia = ImageOps.colorize(grayscale, black="#282018", white="#eee2c7")
    toned = sepia.convert("RGBA")
    toned.putalpha(alpha)
    return add_grain(toned, grain, seed)


def make_paper_texture(size: Tuple[int, int], seed: int, strength: int) -> Image.Image:
    rng = random.Random(seed)
    base = Image.new("RGBA", size, (232, 225, 207, 255))

    if strength <= 0:
        return base

    pixels = base.load()
    for y in range(size[1]):
        for x in range(size[0]):
            r, g, b, a = pixels[x, y]
            noise = rng.randint(-strength, strength)
            pixels[x, y] = (clamp(r + noise), clamp(g + noise), clamp(b + noise), a)

    return base


def rotate_card(image: Image.Image, angle: float, supersample: int, edge_soften: float) -> Image.Image:
    if supersample < 1:
        supersample = 1

    if supersample > 1:
        large_size = (image.size[0] * supersample, image.size[1] * supersample)
        large = image.resize(large_size, RESAMPLE_LANCZOS)
        rotated_large = large.rotate(angle, resample=RESAMPLE_BICUBIC, expand=True)
        final_size = (
            max(1, round(rotated_large.size[0] / supersample)),
            max(1, round(rotated_large.size[1] / supersample)),
        )
        rotated = rotated_large.resize(final_size, RESAMPLE_LANCZOS)
    else:
        rotated = image.rotate(angle, resample=RESAMPLE_BICUBIC, expand=True)

    if edge_soften > 0:
        alpha = rotated.getchannel("A").filter(ImageFilter.GaussianBlur(edge_soften))
        rotated = rotated.copy()
        rotated.putalpha(alpha)

    return rotated


def apply_shadow(
    canvas: Image.Image,
    rotated_card: Image.Image,
    card_xy: Tuple[int, int],
    offset: Tuple[int, int],
    blur: float,
    opacity: float,
) -> None:
    alpha = rotated_card.getchannel("A")
    shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
    shadow_alpha = shadow_alpha.point(lambda p: int(p * opacity))

    shadow = Image.new("RGBA", rotated_card.size, (0, 0, 0, 0))
    shadow.putalpha(shadow_alpha)

    x, y = card_xy
    ox, oy = offset
    canvas.alpha_composite(shadow, (x + ox, y + oy))


def process_report_event_image(
    input_path: Path,
    output_path: Path,
    canvas_size: Tuple[int, int],
    card_size: Tuple[int, int],
    border: int,
    angle: float,
    shadow_offset: Tuple[int, int],
    shadow_blur: float,
    shadow_opacity: float,
    grain: int,
    paper_grain: int,
    seed: int,
    rotate_supersample: int,
    edge_soften: float,
) -> None:
    source = Image.open(input_path).convert("RGBA")

    photo_size = (card_size[0] - border * 2, card_size[1] - border * 2)
    if photo_size[0] <= 0 or photo_size[1] <= 0:
        raise ValueError("Border is too large for the chosen card size")

    photo = cover_crop(source, photo_size)
    photo = apply_report_photo_tone(photo, grain=grain, seed=seed)

    if border > 0:
        card = make_paper_texture(card_size, seed=seed + 1000, strength=paper_grain)
        card.alpha_composite(photo, (border, border))
    else:
        card = photo

    rotated_card = rotate_card(
        image=card,
        angle=angle,
        supersample=rotate_supersample,
        edge_soften=edge_soften,
    )

    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    x = (canvas_size[0] - rotated_card.size[0]) // 2
    y = (canvas_size[1] - rotated_card.size[1]) // 2

    apply_shadow(
        canvas=canvas,
        rotated_card=rotated_card,
        card_xy=(x, y),
        offset=shadow_offset,
        blur=shadow_blur,
        opacity=shadow_opacity,
    )
    canvas.alpha_composite(rotated_card, (x, y))

    output_path = ensure_png_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)


def iter_images(path: Path) -> Iterable[Path]:
    for child in sorted(path.iterdir()):
        if child.is_file() and child.suffix.lower() in IMAGE_EXTENSIONS:
            yield child


def parse_size(value: str) -> Tuple[int, int]:
    if "x" not in value.lower():
        raise argparse.ArgumentTypeError("Use WIDTHxHEIGHT, for example 210x176")

    left, right = value.lower().split("x", 1)
    try:
        width = int(left)
        height = int(right)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Width and height must be integers") from exc

    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Width and height must be positive")

    return width, height


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Process HOI4 report event images into black-and-white sepia tilted "
            "transparent 210x176 cards with a soft drop shadow."
        )
    )
    parser.add_argument("input", type=Path, help="Input image file or folder")
    parser.add_argument("output", type=Path, help="Output PNG file or output folder")
    parser.add_argument("--canvas-size", type=parse_size, default=(210, 176))
    parser.add_argument("--card-size", type=parse_size, default=(192, 153))
    parser.add_argument("--border", type=int, default=0)
    parser.add_argument("--angle", type=float, default=4.0, help="Degrees. Positive tilts like one of the reference images")
    parser.add_argument("--shadow-offset", type=int, nargs=2, default=(4, 5), metavar=("X", "Y"))
    parser.add_argument("--shadow-blur", type=float, default=4.5)
    parser.add_argument("--shadow-opacity", type=float, default=0.50)
    parser.add_argument("--grain", type=int, default=7)
    parser.add_argument("--paper-grain", type=int, default=0)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--rotate-supersample", type=int, default=4)
    parser.add_argument("--edge-soften", type=float, default=0.35)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.input.is_dir():
        args.output.mkdir(parents=True, exist_ok=True)
        for index, source_path in enumerate(iter_images(args.input)):
            output_path = args.output / f"{source_path.stem}_report_event.png"
            process_report_event_image(
                input_path=source_path,
                output_path=output_path,
                canvas_size=args.canvas_size,
                card_size=args.card_size,
                border=args.border,
                angle=args.angle,
                shadow_offset=tuple(args.shadow_offset),
                shadow_blur=args.shadow_blur,
                shadow_opacity=args.shadow_opacity,
                grain=args.grain,
                paper_grain=args.paper_grain,
                seed=args.seed + index,
                rotate_supersample=args.rotate_supersample,
                edge_soften=args.edge_soften,
            )
            print(f"wrote {output_path}")
        return

    output_path = args.output
    if output_path.exists() and output_path.is_dir():
        output_path = output_path / f"{args.input.stem}_report_event.png"

    output_path = ensure_png_path(output_path)
    process_report_event_image(
        input_path=args.input,
        output_path=output_path,
        canvas_size=args.canvas_size,
        card_size=args.card_size,
        border=args.border,
        angle=args.angle,
        shadow_offset=tuple(args.shadow_offset),
        shadow_blur=args.shadow_blur,
        shadow_opacity=args.shadow_opacity,
        grain=args.grain,
        paper_grain=args.paper_grain,
        seed=args.seed,
        rotate_supersample=args.rotate_supersample,
        edge_soften=args.edge_soften,
    )
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
