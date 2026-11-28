"""Tripo as a generator: the job's `provider`, the inbox naming rule and the animation source kind.

Tripo has no API. A person or a browser agent exports files from the Tripo web app into an inbox
folder, `tripo_intake.py` turns them into the provider files a Meshy job downloads, and the shared
Blender stage runs unchanged. A job without `provider` is a Meshy job.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

PROVIDERS = ("meshy", "tripo")
# model: one textured GLB (a building, a prop). rigged: a rigged, animated GLB (a unit).
# segmented: a GLB split into parts (a weapon), used as the twin that finds the weapon vertices.
# donor: the motion donor's export of the clips made on it (tripo_intake carries them onto the unit's rig, lib/clip_transfer.py).
KINDS = ("model", "rigged", "segmented", "donor")


def provider_name(spec: Dict[str, Any]) -> str:
    name = str(spec.get("provider") or "meshy").strip().lower()
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider {name!r}; use one of {', '.join(PROVIDERS)}.")
    return name


def uses_tripo(spec: Dict[str, Any]) -> bool:
    return provider_name(spec) == "tripo"


def held_parts(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The rigid parts a Tripo unit holds, each bound wholly to its own bone: the job's `tripo.weapon`, then `tripo.shield` (its part and
    bone default to `tripo_part_2` and `Shield`, the names tripo/shield_stage.py gives them). Empty for a Meshy job."""

    if not uses_tripo(spec):
        return []
    block = spec.get("tripo") or {}
    parts = [dict(block["weapon"])] if block.get("weapon") else []
    if isinstance(block.get("shield"), dict):  # an empty block is a shield with the default part and bone
        from lib.tripo_shield import SHIELD_BONE, SHIELD_PART

        parts.append({"part": SHIELD_PART, "bone": SHIELD_BONE, **block["shield"]})
    return parts


def released_bones(parts: List[Dict[str, Any]], role: str) -> List[str]:
    """The bones of the held parts the unit lets go of in `role` (each part's `release_roles`)."""

    return [part["bone"] for part in parts if part.get("bone") and role in (part.get("release_roles") or [])]


def held_bones(parts: List[Dict[str, Any]]) -> List[str]:
    """The bones of every held part: a weight rule leaves them alone, so the parts stay rigid."""

    return [part["bone"] for part in parts if part.get("bone")]


def animation_source_kind(spec: Dict[str, Any]) -> str:
    """The provenance kind of a role's animation receipt."""

    return "professional_source" if uses_tripo(spec) else "meshy_animate"


def inbox_file(inbox: Path, asset_slug: str, kind: str) -> Optional[Path]:
    """`<inbox>/<asset_slug>__<kind>.glb`, or None when the person has not exported it."""

    if kind not in KINDS:
        raise ValueError(f"Unknown Tripo export kind {kind!r}; use one of {', '.join(KINDS)}.")
    path = Path(inbox) / f"{asset_slug}__{kind}.glb"
    return path if path.is_file() else None


ATLAS_STRIP = 0.125


def atlas_layout(sizes, strip: float = ATLAS_STRIP):
    """Where each part's texture goes in one square atlas, in pixels from the bottom-left corner.

    `sizes` holds one (height, width) per part. The part with the largest texture is the body.
    It keeps a square of (1 - strip) of the atlas side in the bottom-left corner, so it loses
    one eighth of its resolution per axis at the default strip. Every other part (a weapon, a
    shield) gets one square cell of `strip` of the side: first up the right edge, then along the
    top edge. Returns {"size": side, "main": index, "rects": [(x, y, width, height), ...]}.
    """

    if not sizes:
        raise ValueError("No texture sizes to lay out")
    areas = [height * width for height, width in sizes]
    main = areas.index(max(areas))
    side = max(sizes[main])
    cell = max(1, int(round(side * strip)))
    body = side - cell
    column, row = side // cell, body // cell
    if len(sizes) - 1 > column + row:
        raise ValueError(f"{len(sizes) - 1} extra parts do not fit an atlas with {column + row} cells")
    rects, slot = [], 0
    for index in range(len(sizes)):
        if index == main:
            rects.append((0, 0, body, body))
            continue
        if slot < column:
            rects.append((body, slot * cell, cell, cell))
        else:
            rects.append(((slot - column) * cell, body, cell, cell))
        slot += 1
    return {"size": side, "main": main, "rects": rects}


GLB_NAME_LIMIT = 63  # Blender keeps a clip name at most this long, so a longer prompt comes back cut to it


def resolve_clip_name(wanted: str, names) -> str:
    """The clip a role names: an exact clip name, else the one clip whose name starts with `wanted`.

    Tripo names a text-to-motion clip with its whole prompt, so a role may give just its first words.
    A role longer than the GLB name limit may name a clip that came back cut to that limit, so a
    cut name that starts the role also matches. A prefix that matches two clips or none is refused,
    and the error lists every clip name.
    """

    names = sorted(set(names))
    if wanted in names:
        return wanted
    found = [name for name in names if name.startswith(wanted)]
    if not found:
        found = [name for name in names if len(name) >= GLB_NAME_LIMIT and wanted.startswith(name)]
    if len(found) == 1:
        return found[0]
    problem = "matches several clips" if found else "matches no clip"
    raise ValueError(f"The clip name {wanted!r} {problem}. The file has these clips: {names}")


def safe_animation_name(name: str, limit: int = 60) -> str:
    """A glTF animation name the Blender stage accepts (letters, digits, `_.-`, at most `limit` characters)."""

    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")
    return (cleaned or "clip")[:limit]


# `PART=auto` tries these in order and keeps the first one whose reduction passes the shape check.
# Measured on Tripo's separately modelled axe (19,992 triangles): welding first keeps one shell at every
# budget, and the silhouettes agree 0.95 to 0.96 at 1500, 0.96 to 0.97 at 2500, 0.96 to 0.98 at 4000.
AUTO_BUDGETS = (1500, 2500, 4000)


def parse_part_triangles(items) -> Dict[str, object]:
    """`PART=N` or `PART=auto` items as {part: N or "auto"}; N must be a whole number of at least 12."""

    budgets: Dict[str, object] = {}
    for item in items:
        part, separator, count = str(item).partition("=")
        if not part or not separator or not (count == "auto" or (count.isdigit() and int(count) >= 12)):
            raise ValueError(f"A part triangle budget must look like PART=N (N at least 12) or PART=auto, got {item!r}")
        budgets[part] = "auto" if count == "auto" else int(count)
    return budgets


def budget_list(value) -> tuple:
    """The budgets to try for one part: its number, or the automatic list."""

    return AUTO_BUDGETS if value == "auto" else (int(value),)


def decimate_ratio(triangles: int, budget: int) -> Optional[float]:
    """The Decimate ratio that brings `triangles` to about `budget`, or None when it is already within it."""

    if triangles <= budget:
        return None
    return round(budget / triangles, 6)
