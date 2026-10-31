"""Profile-driven acceptance checks that fail closed.

`candidate_gate` used to block only on an empty mesh, the hard triangle ceiling,
degenerate faces, negative scale and the runtime footprint. The worker already
measured non-manifold and boundary edges, loose parts, material slots and
zero-weight vertices, but nothing acted on them. The checks below turn those
measurements into failures driven by the asset profile.

A profile may waive one check by recording an exception with a reason (see
`profile_exceptions`). A measurement that is missing from the report is a
failure, never a pass, except the post-sanitize weight check, which only runs
where a report carries post-sanitize weight metrics.

Pure Python: no Blender, no network, no provider call.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = PIPELINE_ROOT / "adapter"
PROFILE_REGISTRY_PATH = PIPELINE_ROOT / "config" / "asset_profiles.json"
if str(ADAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(ADAPTER_ROOT))

from profile_exceptions import ProfileExceptionError, index_exceptions

from lib.paths import read_job_document, read_json


# Allowances used when a profile has no `validation` block (or omits a field).
# They are the strict values: a clean, closed, single-piece, fully skinned mesh.
DEFAULT_LIMITS: Dict[str, int] = {
    "max_non_manifold_edges": 0,
    "max_boundary_edges": 0,
    "max_loose_components": 1,
    "max_residual_zero_weight_vertices": 0,
}


class ProfileGateError(RuntimeError):
    """The asset profile cannot be resolved or is malformed, so no check can be trusted."""


def load_profile(name: str, registry_path: Path = PROFILE_REGISTRY_PATH) -> Dict[str, Any]:
    try:
        registry = read_json(registry_path)
    except (OSError, ValueError) as exc:
        raise ProfileGateError(f"Unable to read the asset profile registry {registry_path}: {exc}") from exc
    profile = registry.get("profiles", {}).get(name) if isinstance(registry, dict) else None
    if not isinstance(profile, dict):
        raise ProfileGateError(f"Asset profile {name!r} is not in {registry_path.name}.")
    return profile


def job_profile(job: Path, registry_path: Path = PROFILE_REGISTRY_PATH) -> Tuple[str, Dict[str, Any]]:
    """Resolve the job's profile from its job.yaml."""

    try:
        record = read_job_document(job / "job.yaml")
    except (OSError, ValueError, RuntimeError) as exc:
        raise ProfileGateError(f"Unable to read job.yaml to resolve the asset profile: {exc}") from exc
    name = record.get("profile")
    if not isinstance(name, str) or not name:
        raise ProfileGateError("job.yaml names no asset profile.")
    return name, load_profile(name, registry_path)


def _limit(profile: Mapping[str, Any], key: str) -> int:
    block = profile.get("validation", {})
    if not isinstance(block, dict):
        raise ProfileGateError("Profile 'validation' must be an object.")
    value = block.get(key, DEFAULT_LIMITS[key])
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProfileGateError(f"Profile validation.{key} must be a non-negative integer.")
    return value


def residual_zero_weight_vertices(weights: Any) -> Optional[int]:
    """Count zero-weight vertices on deforming meshes in a `weight_metrics()` list.

    A mesh deforms when an armature modifier points at a rig. Meshes without one
    have no skin weights by design and are not counted. Returns None when the
    input is not a weight-metric list.
    """

    if not isinstance(weights, list) or not all(isinstance(item, dict) for item in weights):
        return None
    total = 0
    for record in weights:
        if not record.get("armature_modifiers"):
            continue
        count = record.get("zero_weight_vertices")
        if isinstance(count, bool) or not isinstance(count, int):
            return None
        total += count
    return total


def post_sanitize_weights(prep: Mapping[str, Any], explicit: Any = None) -> Any:
    """Find post-sanitize weight metrics, or None when there are none.

    `explicit` may be the `weight_metrics()` list, a dict with `weights_after`,
    or the sanitize operation's report (whose `weights` holds `weights_after`).
    Without it the prepare report is searched; only the dual-source prepare path
    sanitizes weights before the candidate gate.
    """

    if explicit is not None:
        if isinstance(explicit, dict) and isinstance(explicit.get("weights"), dict):
            explicit = explicit["weights"]
        return explicit.get("weights_after", []) if isinstance(explicit, dict) else explicit
    for holder in (prep, prep.get("weight_sanitization"), prep.get("base_weight_sanitization")):
        if isinstance(holder, dict) and holder.get("weights_after") is not None:
            return holder["weights_after"]
    return None


class _Evaluation:
    """Collects one record per check, the blocking messages and the waived failures."""

    def __init__(self, profile: Mapping[str, Any]) -> None:
        try:
            self.exceptions = index_exceptions(profile)
        except ProfileExceptionError as exc:
            raise ProfileGateError(str(exc)) from exc
        self.failures: List[str] = []
        self.checks: Dict[str, Dict[str, Any]] = {}
        self.exceptions_applied: List[Dict[str, Any]] = []

    def record(self, check: str, measured: Any, limit: Any, passed: bool, problem: str) -> None:
        entry: Dict[str, Any] = {"measured": measured, "limit": limit}
        if passed:
            entry["status"] = "passed"
        elif check in self.exceptions:
            entry["status"] = "excepted"
            entry["exception"] = self.exceptions[check]
            self.exceptions_applied.append(
                {**self.exceptions[check], "measured": measured, "limit": limit, "problem": problem}
            )
        else:
            entry["status"] = "failed"
            self.failures.append(problem)
        self.checks[check] = entry

    def at_most(self, check: str, label: str, measured: Any, limit: int) -> None:
        if not _is_number(measured):
            self.record(check, None, limit, False, f"{label} was not measured in the candidate report")
        else:
            self.record(check, measured, limit, measured <= limit, f"{label} {measured} exceed profile allowance {limit}")

    def as_dict(self) -> Dict[str, Any]:
        return {"failures": self.failures, "checks": self.checks, "exceptions_applied": self.exceptions_applied}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_topology(evaluation: _Evaluation, profile: Mapping[str, Any], geometry: Mapping[str, Any]) -> None:
    evaluation.at_most(
        "non_manifold_edges", "non-manifold edges", geometry.get("non_manifold_edges"), _limit(profile, "max_non_manifold_edges")
    )
    # The worker's "loose_boundary_edges" counts edges with exactly one face.
    evaluation.at_most(
        "boundary_edges", "boundary edges", geometry.get("loose_boundary_edges"), _limit(profile, "max_boundary_edges")
    )
    evaluation.at_most(
        "loose_components", "loose components", geometry.get("loose_component_count"), _limit(profile, "max_loose_components")
    )


def _check_triangle_range(evaluation: _Evaluation, profile: Mapping[str, Any], geometry: Mapping[str, Any]) -> None:
    triangle_range = profile.get("triangle_range", {})
    if not isinstance(triangle_range, dict):
        triangle_range = {}
    preferred = (triangle_range.get("preferred_min"), triangle_range.get("preferred_max"))
    triangles = geometry.get("triangles")
    if not all(_is_number(value) for value in preferred):
        evaluation.record("triangle_range", triangles, None, False, "profile defines no preferred triangle range")
    elif not _is_number(triangles):
        evaluation.record(
            "triangle_range", None, list(preferred), False, "triangle count was not measured in the candidate report"
        )
    else:
        evaluation.record(
            "triangle_range",
            triangles,
            list(preferred),
            preferred[0] <= triangles <= preferred[1],
            f"triangles {triangles} are outside the profile's preferred range {preferred[0]}-{preferred[1]}",
        )


def _check_material_slots(evaluation: _Evaluation, profile: Mapping[str, Any], prep: Mapping[str, Any]) -> None:
    materials = prep.get("materials", {})
    names = materials.get("materials") if isinstance(materials, dict) else None
    profile_materials = profile.get("materials", {})
    max_slots = profile_materials.get("max_slots") if isinstance(profile_materials, dict) else None
    if isinstance(max_slots, bool) or not isinstance(max_slots, int):
        evaluation.record("material_slots", None, None, False, "profile defines no materials.max_slots")
    elif not isinstance(names, list):
        evaluation.record("material_slots", None, max_slots, False, "material slots were not listed in the candidate report")
    else:
        used = len({name for name in names if isinstance(name, str)})
        evaluation.record(
            "material_slots", used, max_slots, used <= max_slots, f"material slots {used} exceed profile maximum {max_slots}"
        )


def _check_zero_weights(
    evaluation: _Evaluation, profile: Mapping[str, Any], prep: Mapping[str, Any], weights_after: Any
) -> None:
    weights = post_sanitize_weights(prep, weights_after)
    if weights is None:
        evaluation.checks["zero_weight_vertices"] = {
            "status": "not_evaluated",
            "reason": "the report carries no post-sanitize weight metrics",
        }
        return
    limit = _limit(profile, "max_residual_zero_weight_vertices")
    residual = residual_zero_weight_vertices(weights)
    if residual is None:
        evaluation.record("zero_weight_vertices", None, limit, False, "post-sanitize weight metrics are malformed")
    else:
        evaluation.record(
            "zero_weight_vertices",
            residual,
            limit,
            residual <= limit,
            f"residual zero-weight deforming vertices {residual} exceed profile allowance {limit}",
        )


def evaluate_candidate(
    profile: Mapping[str, Any],
    prep: Mapping[str, Any],
    *,
    weights_after: Any = None,
) -> Dict[str, Any]:
    """Evaluate the profile-driven checks against a prepare report.

    Returns `failures` (blocking messages), `checks` (one record per check) and
    `exceptions_applied` (checks that failed but are waived by a recorded
    profile exception, with the measurement and the reason).
    """

    evaluation = _Evaluation(profile)
    geometry = prep.get("geometry", {})
    if not isinstance(geometry, dict):
        geometry = {}
    _check_topology(evaluation, profile, geometry)
    _check_triangle_range(evaluation, profile, geometry)
    _check_material_slots(evaluation, profile, prep)
    _check_zero_weights(evaluation, profile, prep, weights_after)
    return evaluation.as_dict()


def exporter_report_failures(result: Mapping[str, Any]) -> List[str]:
    """Reasons an export result must not be accepted as it stands.

    An export is unaccepted when the exporter could not be heard (the capture
    state is not `captured`, or `warnings` is not a list) or when it reported an
    error. Captured warnings are recorded in the result but do not block.
    """

    report = result.get("exporter_report")
    if not isinstance(report, dict):
        return ["the export result carries no exporter report"]
    if report.get("status") != "captured":
        return [f"exporter output was not captured: {report.get('reason') or 'unknown reason'}"]
    if not isinstance(result.get("warnings"), list):
        return ["the export result has no warnings list although the exporter was captured"]
    errors = [item for item in report.get("records", []) if item.get("level") in {"ERROR", "CRITICAL"}]
    if errors:
        return [f"the exporter reported {len(errors)} error(s): {errors[0].get('message')}"]
    return []


def job_profile_exception(job: Path, check: str, registry_path: Path = PROFILE_REGISTRY_PATH) -> Optional[Dict[str, str]]:
    """The job profile's recorded exception for a check; None when there is none or it cannot be read."""

    try:
        _, profile = job_profile(job, registry_path)
        return index_exceptions(profile).get(check)
    except (ProfileGateError, ProfileExceptionError):
        return None
