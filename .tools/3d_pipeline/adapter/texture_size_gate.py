"""Fail-closed profile texture-size cap for the adapter's DDS conversion.

The adapter environment installs `mcp` and nothing else, so image sizes are
read from the PNG header with the standard library. The cap used to run
`ffprobe` and silently skip itself when the tool was missing or failed; now an
unreadable image, a missing profile or a profile without a cap blocks the
conversion unless the profile records a `texture_max_dimension` exception.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

from profile_exceptions import ProfileExceptionError, recorded_exception


CHECK_ID = "texture_max_dimension"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class TextureSizeGateError(RuntimeError):
    """The texture size cap could not be proven, so the texture is not accepted."""


def png_dimensions(path: Path) -> Tuple[int, int]:
    """Read width and height from the IHDR chunk, which must come first."""

    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError as exc:
        raise TextureSizeGateError(f"Unable to read texture {path.name}: {exc}") from exc
    if (
        len(header) < 24
        or header[:8] != PNG_SIGNATURE
        or header[8:12] != b"\x00\x00\x00\x0d"
        or header[12:16] != b"IHDR"
    ):
        raise TextureSizeGateError(
            f"Texture {path.name} is not a PNG with a leading IHDR chunk, so its size cannot be checked."
        )
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise TextureSizeGateError(f"Texture {path.name} declares a non-positive size {width}x{height}.")
    return width, height


def _positive_int(value: Any) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None
    return value


def texture_size_decision(png: Path, profile: Mapping[str, Any]) -> Dict[str, Any]:
    """Decide the size cap for one texture.

    Returns a record with `status` of `within_cap`, `resize` or `excepted`;
    `width` and `height` are the resize target and are None unless the status is
    `resize`. Raises TextureSizeGateError when the cap cannot be proven and the
    profile records no exception.
    """

    try:
        exception = recorded_exception(profile, CHECK_ID)
    except ProfileExceptionError as exc:
        raise TextureSizeGateError(str(exc)) from exc
    cap = _positive_int(profile.get("texture_max_dimension"))
    source: Optional[Tuple[int, int]] = None
    failure: Optional[str] = None
    if cap is None:
        failure = "The profile defines no positive texture_max_dimension."
    try:
        source = png_dimensions(png)
    except TextureSizeGateError as exc:
        failure = failure or str(exc)
    record: Dict[str, Any] = {
        "check": CHECK_ID,
        "max_dimension": cap,
        "source_width": source[0] if source else None,
        "source_height": source[1] if source else None,
        "width": None,
        "height": None,
        "exception": exception,
    }
    if exception is not None:
        record["status"] = "excepted"
        record["unproven"] = failure
        return record
    if failure is not None or cap is None or source is None:
        raise TextureSizeGateError(
            f"{failure} Add a texture_max_dimension to the profile or record a "
            f"'{CHECK_ID}' exception with a reason."
        )
    largest = max(source)
    if largest <= cap:
        record["status"] = "within_cap"
        return record
    ratio = cap / largest
    record["status"] = "resize"
    record["width"] = max(1, round(source[0] * ratio))
    record["height"] = max(1, round(source[1] * ratio))
    return record
