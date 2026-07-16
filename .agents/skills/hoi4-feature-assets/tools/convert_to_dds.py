#!/usr/bin/env python3
"""
Convert a PNG or other source image to a HOI4-ready DDS file.

Primary backend:
- DirectXTex texconv
- Output format: BGRA / B8G8R8A8_UNORM
- Mip levels: 1

Supported usage:
- WSL calling Windows texconv.exe
- Native Linux texconv
- macOS through a Docker texconv image

Environment variables:
- TEXCONV_PATH: path to texconv or texconv.exe
- TEXCONV_EXE: alternative path to texconv.exe
- TEXCONV_DOCKER_IMAGE: Docker image name containing texconv
"""

from __future__ import annotations

import argparse
import struct
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DDS_FORMAT = "BGRA"
MIP_LEVELS = "1"

DDSD_CAPS = 0x1
DDSD_HEIGHT = 0x2
DDSD_WIDTH = 0x4
DDSD_PITCH = 0x8
DDSD_PIXELFORMAT = 0x1000
DDPF_ALPHAPIXELS = 0x1
DDPF_RGB = 0x40
DDSCAPS_TEXTURE = 0x1000


class ConversionError(RuntimeError):
    pass


def run_command(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise ConversionError(
            "Command failed:\n"
            + " ".join(command)
            + "\n\nSTDOUT:\n"
            + result.stdout
            + "\n\nSTDERR:\n"
            + result.stderr
        )

    return result


def run_binary_command(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise ConversionError(
            "Command failed:\n"
            + " ".join(command)
            + "\n\nSTDOUT:\n"
            + result.stdout.decode("utf-8", errors="replace")
            + "\n\nSTDERR:\n"
            + result.stderr.decode("utf-8", errors="replace")
        )

    return result


def is_wsl() -> bool:
    if platform.system().lower() != "linux":
        return False

    try:
        text = Path("/proc/version").read_text(encoding="utf-8", errors="ignore").lower()
        return "microsoft" in text or "wsl" in text
    except OSError:
        return False


def to_windows_path(path: Path) -> str:
    result = run_command(["wslpath", "-w", str(path)])
    return result.stdout.strip()


def find_texconv() -> Path | None:
    env_path = os.environ.get("TEXCONV_PATH") or os.environ.get("TEXCONV_EXE")

    if env_path:
        path = Path(env_path).expanduser()
        if path.exists():
            return path
        raise ConversionError(f"TEXCONV_PATH/TEXCONV_EXE is set, but the file does not exist: {path}")

    found = shutil.which("texconv") or shutil.which("texconv.exe")
    if found:
        return Path(found)

    return None


def find_ffmpeg() -> Path | None:
    found = shutil.which("ffmpeg")
    return Path(found) if found else None


def build_texconv_args(
    input_file: str,
    output_dir: str,
    width: int | None,
    height: int | None,
) -> list[str]:
    args = [
        "-nologo",
        "-y",
        "-ft",
        "dds",
        "-f",
        DDS_FORMAT,
        "-m",
        MIP_LEVELS,
        "-o",
        output_dir,
    ]

    if width is not None:
        args.extend(["-w", str(width)])

    if height is not None:
        args.extend(["-h", str(height)])

    args.append(input_file)
    return args


def run_texconv_direct(
    texconv: Path,
    input_file: Path,
    output_dir: Path,
    width: int | None,
    height: int | None,
) -> None:
    texconv_str = str(texconv)

    if is_wsl() and texconv.suffix.lower() == ".exe":
        input_arg = to_windows_path(input_file)
        output_arg = to_windows_path(output_dir)
    else:
        input_arg = str(input_file)
        output_arg = str(output_dir)

    command = [texconv_str] + build_texconv_args(input_arg, output_arg, width, height)
    run_command(command)


def run_texconv_docker(
    image: str,
    input_file: Path,
    output_dir: Path,
    width: int | None,
    height: int | None,
) -> None:
    temp_root = input_file.parent.parent
    container_input = f"/work/in/{input_file.name}"
    container_output_dir = "/work/out"

    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{temp_root}:/work",
        "-w",
        "/work",
        image,
    ] + build_texconv_args(container_input, container_output_dir, width, height)

    run_command(command)


def find_created_dds(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("*.dds"))

    if not files:
        raise ConversionError(f"texconv completed but no DDS file was found in: {output_dir}")

    if len(files) > 1:
        raise ConversionError(
            "texconv created more than one DDS file. Refusing to guess:\n"
            + "\n".join(str(path) for path in files)
        )

    return files[0]


def probe_image_size(input_file: Path) -> tuple[int, int]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0:s=x",
        str(input_file),
    ]
    result = run_command(command)
    width_str, height_str = result.stdout.strip().split("x", 1)
    return int(width_str), int(height_str)


def write_bgra_dds(output_path: Path, width: int, height: int, bgra_data: bytes) -> None:
    expected_size = width * height * 4
    if len(bgra_data) != expected_size:
        raise ConversionError(
            f"Unexpected BGRA data size: got {len(bgra_data)} bytes, expected {expected_size}"
        )

    pitch = width * 4
    header = struct.pack(
        "<4s31I",
        b"DDS ",
        124,
        DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_PITCH,
        height,
        width,
        pitch,
        0,
        0,
        *([0] * 11),
        32,
        DDPF_RGB | DDPF_ALPHAPIXELS,
        0,
        32,
        0x00FF0000,
        0x0000FF00,
        0x000000FF,
        0xFF000000,
        DDSCAPS_TEXTURE,
        0,
        0,
        0,
        0,
    )

    output_path.write_bytes(header + bgra_data)


def run_ffmpeg_bgra_fallback(
    input_file: Path,
    output_path: Path,
    width: int | None,
    height: int | None,
) -> None:
    ffmpeg = find_ffmpeg()
    if ffmpeg is None:
        raise ConversionError(
            "No DDS backend found and ffmpeg is unavailable for the BGRA fallback.\n\n"
            "Set one of these:\n"
            "- TEXCONV_PATH=/path/to/texconv\n"
            "- TEXCONV_EXE=/path/to/texconv.exe\n"
            "- TEXCONV_DOCKER_IMAGE=chaos-texconv"
        )

    source_width, source_height = probe_image_size(input_file)
    target_width = width or source_width
    target_height = height or source_height
    vf = f"scale={target_width}:{target_height}:flags=lanczos,format=bgra"
    command = [
        str(ffmpeg),
        "-v",
        "error",
        "-i",
        str(input_file),
        "-vf",
        vf,
        "-f",
        "rawvideo",
        "-pix_fmt",
        "bgra",
        "-",
    ]
    result = run_binary_command(command)
    write_bgra_dds(output_path, target_width, target_height, result.stdout)


def convert_to_dds(
    input_path: Path,
    output_path: Path,
    width: int | None,
    height: int | None,
) -> Path:
    if not input_path.exists():
        raise ConversionError(f"Input file does not exist: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    docker_image = os.environ.get("TEXCONV_DOCKER_IMAGE")
    texconv_path = None if docker_image else find_texconv()

    if not docker_image and texconv_path is None:
        run_ffmpeg_bgra_fallback(input_path, output_path, width, height)
        return output_path

    with tempfile.TemporaryDirectory(prefix="chaos_dds_") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        input_dir = temp_dir / "in"
        output_dir = temp_dir / "out"
        input_dir.mkdir()
        output_dir.mkdir()

        temp_input = input_dir / input_path.name
        shutil.copy2(input_path, temp_input)

        if docker_image:
            run_texconv_docker(docker_image, temp_input, output_dir, width, height)
        else:
            assert texconv_path is not None
            run_texconv_direct(texconv_path, temp_input, output_dir, width, height)

        created_dds = find_created_dds(output_dir)

        if output_path.exists():
            output_path.unlink()

        shutil.move(str(created_dds), str(output_path))

    if not output_path.exists():
        raise ConversionError(f"Final DDS file was not created: {output_path}")

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert an image to a HOI4-ready DDS file.")
    parser.add_argument("--input", required=True, help="Input image path, usually a processed PNG.")
    parser.add_argument("--output", required=True, help="Final DDS output path.")
    parser.add_argument("--width", type=int, default=None, help="Target width in pixels.")
    parser.add_argument("--height", type=int, default=None, help="Target height in pixels.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        output = convert_to_dds(
            input_path=Path(args.input).expanduser().resolve(),
            output_path=Path(args.output).expanduser().resolve(),
            width=args.width,
            height=args.height,
        )
    except ConversionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
