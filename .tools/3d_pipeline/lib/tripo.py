"""Tripo as a generator: the job's `provider`, the inbox naming rule and the animation source kind.

Tripo has no API. A person or a browser agent exports files from the Tripo web app into an inbox
folder, `tripo_intake.py` turns them into the provider files a Meshy job downloads, and the shared
Blender stage runs unchanged. A job without `provider` is a Meshy job.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

PROVIDERS = ("meshy", "tripo")
# model: one textured GLB (a building, a prop). rigged: a rigged, animated GLB (a unit).
# segmented: a GLB split into parts (a weapon), used as the twin that finds the weapon vertices.
KINDS = ("model", "rigged", "segmented")


def provider_name(spec: Dict[str, Any]) -> str:
    name = str(spec.get("provider") or "meshy").strip().lower()
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider {name!r}; use one of {', '.join(PROVIDERS)}.")
    return name


def uses_tripo(spec: Dict[str, Any]) -> bool:
    return provider_name(spec) == "tripo"


def animation_source_kind(spec: Dict[str, Any]) -> str:
    """The provenance kind of a role's animation receipt."""

    return "professional_source" if uses_tripo(spec) else "meshy_animate"


def inbox_file(inbox: Path, asset_slug: str, kind: str) -> Optional[Path]:
    """`<inbox>/<asset_slug>__<kind>.glb`, or None when the person has not exported it."""

    if kind not in KINDS:
        raise ValueError(f"Unknown Tripo export kind {kind!r}; use one of {', '.join(KINDS)}.")
    path = Path(inbox) / f"{asset_slug}__{kind}.glb"
    return path if path.is_file() else None
