"""Pure convergence guards for strict saved-normalization correction."""

from __future__ import annotations

import math
from typing import Any, Dict, Optional


def evaluate_convergence_step(
    *,
    target: float,
    persisted: float,
    tolerance: float,
    previous_delta: Optional[float],
    corrections_applied: int,
    max_corrections: int,
) -> Dict[str, Any]:
    if not all(math.isfinite(value) for value in (target, persisted, tolerance)) or tolerance <= 0.0:
        raise RuntimeError("Normalization convergence received non-finite or invalid values.")
    delta = persisted - target
    absolute_delta = abs(delta)
    if absolute_delta <= tolerance:
        return {"status": "accepted", "delta": delta, "correction_factor": None}
    if previous_delta is not None:
        if not math.isfinite(previous_delta):
            raise RuntimeError("Normalization convergence previous delta is non-finite.")
        if previous_delta * delta < 0.0:
            raise RuntimeError("Normalization convergence changed sign outside tolerance.")
        previous_absolute = abs(previous_delta)
        if absolute_delta > previous_absolute:
            raise RuntimeError("Normalization convergence diverged outside tolerance.")
        minimum_improvement = max(tolerance * 0.05, previous_absolute * 0.001)
        if previous_absolute - absolute_delta <= minimum_improvement:
            raise RuntimeError("Normalization convergence stalled outside tolerance.")
    if corrections_applied >= max_corrections:
        raise RuntimeError("Normalization convergence exhausted its correction cap.")
    if persisted == 0.0:
        raise RuntimeError("Normalization convergence cannot correct a zero persisted height.")
    factor = target / persisted
    if not math.isfinite(factor) or factor <= 0.0:
        raise RuntimeError("Normalization convergence produced an invalid correction factor.")
    return {"status": "correct", "delta": delta, "correction_factor": factor}
