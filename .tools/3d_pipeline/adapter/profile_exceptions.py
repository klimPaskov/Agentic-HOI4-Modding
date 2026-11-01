"""Recorded, per-profile exceptions to the fail-closed acceptance checks.

An asset profile may waive one named check by listing an entry with a reason
in its `exceptions` array:

    "exceptions": [{"check": "boundary_edges", "reason": "Open sleeve cuffs are intended."}]

Anything else stays blocking. A malformed list, an unknown check name or an
entry without a reason raises instead of being ignored, so a typo can neither
waive a check nor hide that a waiver was intended.

This module uses the standard library only. The Blender adapter and the runner
both import it, and the adapter source closure must stay flat.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


# Every check a profile may waive. A new fail-closed check must be added here
# before a profile can record an exception for it.
CHECK_IDS = frozenset(
    {
        "texture_max_dimension",
        "exporter_report",
        "non_manifold_edges",
        "boundary_edges",
        "loose_components",
        "triangle_range",
        "material_slots",
        "zero_weight_vertices",
    }
)


class ProfileExceptionError(ValueError):
    """A profile's `exceptions` entry is malformed, so no waiver can be trusted."""


def index_exceptions(profile: Mapping[str, Any]) -> Dict[str, Dict[str, str]]:
    """Validate a profile's recorded exceptions and index them by check name."""

    entries = profile.get("exceptions", [])
    if not isinstance(entries, list):
        raise ProfileExceptionError("Profile 'exceptions' must be a list of {check, reason} entries.")
    indexed: Dict[str, Dict[str, str]] = {}
    for position, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ProfileExceptionError(f"Profile exception #{position} must be an object.")
        check = entry.get("check")
        reason = entry.get("reason")
        if not isinstance(check, str) or check not in CHECK_IDS:
            raise ProfileExceptionError(
                f"Profile exception #{position} names unknown check {check!r}; "
                f"known checks: {', '.join(sorted(CHECK_IDS))}."
            )
        if not isinstance(reason, str) or not reason.strip():
            raise ProfileExceptionError(f"Profile exception for {check!r} needs a non-empty reason.")
        if check in indexed:
            raise ProfileExceptionError(f"Profile records more than one exception for {check!r}.")
        indexed[check] = {"check": check, "reason": reason.strip()}
    return indexed


def recorded_exception(profile: Mapping[str, Any], check: str) -> Optional[Dict[str, str]]:
    """Return the profile's recorded exception for one check, or None."""

    if check not in CHECK_IDS:
        raise ProfileExceptionError(f"Unknown acceptance check {check!r}.")
    return index_exceptions(profile).get(check)
