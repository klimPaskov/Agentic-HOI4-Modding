"""The per-job credit ledger, budget gate, attempt counting and credits report.

Every paid Meshy attempt, every call that was stopped, and every paid call that reuse or a local
Blender repair made unnecessary is appended to `provider/credits/ledger.jsonl`. A row has:

  timestamp, attempt_id, stage, operation, model, fingerprint, scope,
  estimate_credits, consumed_credits, consumed_source, outcome, reason

`outcome` is one of
  reserved / retry  credits set aside before a paid create (retry: not the first attempt in its scope)
  success / failed  the attempt finished; consumed_credits is the provider's figure, else the balance delta
  rejected          no paid task resulted: a gate stopped the call, or a reconciled submission never existed
  reused            a paid call was avoided because a result already exists; estimate_credits is the saving
  local_repair      a paid regeneration or provider step was avoided by a Blender repair; same saving

A reservation is open until a success, failed or rejected row with the same attempt_id follows it.
Older jobs have no ledger; their `*_reconciliation.json` and task records are read as ledger rows.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from lib.generation import load_contract
from lib.paths import append_jsonl, read_json, sha256_file, utc_now

RESERVATIONS = {"reserved", "retry"}
FINISHED = {"success", "failed"}
SETTLEMENTS = FINISHED | {"rejected"}
OUTCOMES = RESERVATIONS | SETTLEMENTS | {"reused", "local_repair"}
SUCCEEDED_STATUSES = {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}
ROW_FIELDS = (
    "attempt_id",
    "stage",
    "operation",
    "model",
    "fingerprint",
    "scope",
    "estimate_credits",
    "consumed_credits",
    "consumed_source",
    "outcome",
    "reason",
)
ATTEMPT_LIMIT_KEYS = {
    "image_to_3d": "max_generation_attempts",
    "remesh": "max_remesh_attempts",
    "rig": "max_rig_attempts",
    "animation": "max_action_attempts_per_role",
    "text_to_motion": "max_text_to_motion_attempts",
}
# Arguments that name where a file lives, not what is asked of Meshy.
VOLATILE_ARGUMENTS = {"file_path", "save_to", "response_format"}
LEGACY_OPERATIONS = {"image-to-3d": "image_to_3d", "remesh": "remesh", "rigging": "rig", "animation": "animation"}


class CreditStop(RuntimeError):
    """A paid call was stopped before submission."""


class BudgetExceeded(CreditStop):
    pass


class AttemptLimitReached(CreditStop):
    pass


class UnreconciledSubmission(CreditStop):
    pass


@dataclass(frozen=True)
class PaidRequest:
    """What the gates need to know about one paid create, before it is sent."""

    operation: str
    tool: str
    model: Optional[str]
    fingerprint: str
    scope: str
    attempt_limit: int
    credit_budget: int


def request_fingerprint(tool: str, arguments: Dict[str, Any]) -> str:
    """SHA-256 of the input file's bytes plus the canonical JSON of the request arguments."""

    path = arguments.get("file_path")
    file_digest = sha256_file(Path(str(path))) if path and Path(str(path)).is_file() else ""
    request = {"tool": tool, "arguments": {k: v for k, v in arguments.items() if k not in VOLATILE_ARGUMENTS}}
    canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(f"{file_digest}\0{canonical}".encode("ascii")).hexdigest().upper()


def attempt_scope(operation: str, lineage: str, role: Optional[str] = None) -> str:
    """Attempts of one operation are counted together, whatever the stage is named."""

    if operation == "image_to_3d":
        return operation
    return f"{operation}{':' + role if role else ''}@{lineage}"


def attempt_limit(operation: str, contract: Optional[Dict[str, Any]] = None, declared: Any = None) -> int:
    """The contract's attempt limit; a job may declare more geometry attempts (provider_plan.paid_attempts)."""

    policy = (contract or load_contract())["provider_policy"]
    limit = int(policy[ATTEMPT_LIMIT_KEYS[operation]])
    if operation == "image_to_3d" and declared:
        limit = max(limit, int(declared))
    return limit


def ledger_file(job: Path) -> Path:
    return job / "provider" / "credits" / "ledger.jsonl"


def read_ledger(job: Path) -> List[Dict[str, Any]]:
    path = ledger_file(job)
    if not path.is_file():
        return []
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path} line {number} is not valid JSON; the ledger is append-only evidence.") from error
        rows.append(row)
    return rows


def append_entry(job: Path, **fields: Any) -> Dict[str, Any]:
    if fields.get("outcome") not in OUTCOMES:
        raise ValueError(f"Unknown ledger outcome {fields.get('outcome')!r}.")
    row = {name: fields.pop(name, None) for name in ROW_FIELDS}
    row.update(fields)
    row["timestamp"] = utc_now()
    if row["attempt_id"] is None:
        row["attempt_id"] = uuid.uuid4().hex
    append_jsonl(ledger_file(job), row)
    return row


def reserve(job: Path, request: PaidRequest, *, stage: str, estimate: int, reason: str, **extra: Any) -> str:
    """Set credits aside before a paid create. Returns the attempt id that settles the reservation."""

    outcome = "retry" if attempts_made(read_ledger(job), request.scope) else "reserved"
    row = append_entry(
        job,
        stage=stage,
        operation=request.operation,
        model=request.model,
        fingerprint=request.fingerprint,
        scope=request.scope,
        estimate_credits=estimate,
        outcome=outcome,
        reason=reason,
        **extra,
    )
    return str(row["attempt_id"])


def open_reservation(entries: Iterable[Dict[str, Any]], stage: str) -> Optional[Dict[str, Any]]:
    """The latest reservation for a stage that no success, failed or rejected row has settled."""

    rows = list(entries)
    settled = {row["attempt_id"] for row in rows if row["outcome"] in SETTLEMENTS}
    open_rows = [row for row in rows if row["outcome"] in RESERVATIONS and row["stage"] == stage and row["attempt_id"] not in settled]
    return open_rows[-1] if open_rows else None


def settle(
    job: Path,
    attempt_id: str,
    *,
    outcome: str,
    consumed: Optional[int],
    source: str,
    reason: str,
    **extra: Any,
) -> Dict[str, Any]:
    """Close a reservation with the attempt's outcome and the credits it actually used."""

    if outcome not in SETTLEMENTS:
        raise ValueError(f"A reservation settles as success, failed or rejected, not {outcome!r}.")
    reservation = next(
        (row for row in reversed(read_ledger(job)) if row["attempt_id"] == attempt_id and row["outcome"] in RESERVATIONS),
        None,
    )
    if reservation is None:
        raise ValueError(f"No open reservation {attempt_id} in {ledger_file(job)}.")
    fields = {name: reservation[name] for name in ("stage", "operation", "model", "fingerprint", "scope", "estimate_credits")}
    return append_entry(
        job,
        attempt_id=attempt_id,
        outcome=outcome,
        consumed_credits=consumed,
        consumed_source=source,
        reason=reason,
        **fields,
        **extra,
    )


def reject(job: Path, request: PaidRequest, *, stage: str, estimate: int, reason: str, **extra: Any) -> Dict[str, Any]:
    """Record a call that was stopped before submission."""

    return append_entry(
        job,
        stage=stage,
        operation=request.operation,
        model=request.model,
        fingerprint=request.fingerprint,
        scope=request.scope,
        estimate_credits=estimate,
        consumed_credits=0,
        consumed_source="none",
        outcome="rejected",
        reason=reason,
        **extra,
    )


def record_reuse(job: Path, *, stage: str, operation: str, estimate: int, reason: str, **fields: Any) -> Dict[str, Any]:
    """Record a paid call avoided because a result already exists (estimate_credits is the saving)."""

    return append_entry(
        job,
        stage=stage,
        operation=operation,
        estimate_credits=estimate,
        consumed_credits=0,
        consumed_source="none",
        outcome="reused",
        reason=reason,
        **fields,
    )


def record_local_repair(job: Path, *, stage: str, operation: str, estimate: int, reason: str, **fields: Any) -> Dict[str, Any]:
    """Record a Blender repair that replaced a paid call (estimate_credits is what the paid route costs)."""

    return append_entry(
        job,
        stage=stage,
        operation=operation,
        estimate_credits=estimate,
        consumed_credits=0,
        consumed_source="none",
        outcome="local_repair",
        reason=reason,
        **fields,
    )


def already_reused(entries: Iterable[Dict[str, Any]], stage: str, task_id: str) -> bool:
    return any(row["outcome"] == "reused" and row["stage"] == stage and row.get("task_id") == task_id for row in entries)


def attempts_made(entries: Iterable[Dict[str, Any]], scope: str) -> int:
    """Paid attempts in a scope: every reservation, except those reconciled as never submitted."""

    rows = list(entries)
    never_submitted = {row["attempt_id"] for row in rows if row["outcome"] == "rejected"}
    return sum(
        1
        for row in rows
        if row["outcome"] in RESERVATIONS and row["scope"] == scope and row["attempt_id"] not in never_submitted
    )


def check_attempt_limit(entries: Iterable[Dict[str, Any]], request: PaidRequest, stage: str) -> None:
    made = attempts_made(entries, request.scope)
    if made >= request.attempt_limit:
        raise AttemptLimitReached(
            f"Attempt limit: {request.scope} already has {made} paid attempt(s) in the ledger and the contract "
            f"allows {request.attempt_limit} (meshy_tool_contract.json provider_policy). Nothing was submitted for "
            f"{stage}; naming it differently does not reset the count."
        )


def spent(row: Dict[str, Any]) -> int:
    """Credits a finished attempt counts against the budget: the known figure, else its estimate."""

    value = row.get("consumed_credits")
    return int(value if value is not None else row.get("estimate_credits") or 0)


def budget_state(entries: Iterable[Dict[str, Any]], credit_budget: int) -> Dict[str, int]:
    rows = list(entries)
    settled = {row["attempt_id"] for row in rows if row["outcome"] in SETTLEMENTS}
    consumed = sum(spent(row) for row in rows if row["outcome"] in FINISHED)
    reserved = sum(
        int(row.get("estimate_credits") or 0)
        for row in rows
        if row["outcome"] in RESERVATIONS and row["attempt_id"] not in settled
    )
    return {
        "credit_budget": credit_budget,
        "consumed": consumed,
        "reserved": reserved,
        "remaining": credit_budget - consumed - reserved,
    }


def check_budget(entries: Iterable[Dict[str, Any]], request: PaidRequest, stage: str, estimate: int) -> Dict[str, int]:
    state = budget_state(entries, request.credit_budget)
    if estimate > state["remaining"]:
        shortfall = estimate - state["remaining"]
        raise BudgetExceeded(
            f"Credit budget stop: {stage} ({request.operation}) needs {estimate} credits, but only "
            f"{state['remaining']} of the {state['credit_budget']}-credit job budget remain "
            f"({state['consumed']} consumed, {state['reserved']} reserved). Short by {shortfall}. "
            f"Nothing was submitted. Ask the user once to raise credit_budget to at least "
            f"{state['credit_budget'] + shortfall} in the job spec and job.yaml."
        )
    return state


def consumption(provider: Optional[int], delta: Optional[int]) -> tuple:
    """The credits an attempt used and where the figure came from.

    The provider's figure wins. The balance delta covers the whole account, so concurrent jobs
    inflate it; it is only used when the provider reports nothing.
    """

    if provider is not None:
        return provider, "provider"
    if delta is not None:
        return delta, "balance_delta"
    return None, "unknown"


def _legacy_operation(record: Dict[str, Any]) -> str:
    return LEGACY_OPERATIONS.get(str(record.get("task_type")), str(record.get("task_type") or "unknown"))


def _legacy_model(job: Path, operation: str) -> Optional[str]:
    if operation != "image_to_3d":
        return None
    try:
        document = read_json(job / "job.yaml")
        return str(document["provider_plan"]["ai_model"])
    except (OSError, ValueError, KeyError, TypeError):
        return "unrecorded"


def legacy_entries(job: Path, skip_stages: Iterable[str] = ()) -> List[Dict[str, Any]]:
    """Ledger-shaped rows for a job that predates the ledger, from its task and reconciliation records."""

    skip = set(skip_stages)
    rows = []
    for task_path in sorted((job / "provider" / "tasks").glob("*.json")):
        task = read_json(task_path)
        stage = str(task.get("stage") or task_path.stem)
        if stage in skip or task.get("reused_from"):
            continue
        reconciliation_path = job / "provider" / "credits" / f"{stage}_reconciliation.json"
        reconciliation = read_json(reconciliation_path) if reconciliation_path.is_file() else {}
        provider = reconciliation.get("provider_consumed_credits", task.get("consumed_credits"))
        consumed, source = consumption(provider, reconciliation.get("observed_balance_delta"))
        operation = _legacy_operation(task)
        rows.append(
            {
                "timestamp": task.get("recorded_at") or task.get("created_at"),
                "attempt_id": f"legacy:{stage}",
                "stage": stage,
                "operation": operation,
                "model": _legacy_model(job, operation),
                "fingerprint": task.get("fingerprint"),
                "scope": stage,
                "estimate_credits": task.get("estimated_credits"),
                "consumed_credits": consumed,
                "consumed_source": source,
                "outcome": "success" if task.get("status") in SUCCEEDED_STATUSES else "failed",
                "reason": "recorded before the ledger existed",
                "task_id": task.get("task_id"),
                "reconciliation": reconciliation.get("status"),
            }
        )
    return rows


def ledger_entries(job: Path) -> List[Dict[str, Any]]:
    """The ledger plus legacy rows for every stage the ledger does not cover."""

    rows = read_ledger(job)
    covered = {row["stage"] for row in rows if row["outcome"] in SETTLEMENTS | RESERVATIONS | {"reused"}}
    return rows + legacy_entries(job, covered)


def wasted_credits(rows: List[Dict[str, Any]]) -> int:
    """Credits spent on failed attempts and on successes that a later attempt in the same scope replaced."""

    total = 0
    successes: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        if row["outcome"] == "failed":
            total += int(row.get("consumed_credits") or 0)
        elif row["outcome"] == "success":
            successes.setdefault(str(row.get("scope") or row["stage"]), []).append(row)
    for group in successes.values():
        total += sum(int(row.get("consumed_credits") or 0) for row in group[:-1])
    return total


def find_job_roots(path: Path) -> List[Path]:
    """A job folder itself, or every job folder directly below a root."""

    path = path.resolve()
    if (path / "provider").is_dir():
        return [path]
    return sorted(child for child in path.iterdir() if child.is_dir() and (child / "provider").is_dir()) if path.is_dir() else []


def _job_summary(job: Path) -> Dict[str, Any]:
    rows = ledger_entries(job)
    finished = [row for row in rows if row["outcome"] in FINISHED]
    return {
        "job": job.name,
        "rows": rows,
        "consumed": sum(int(row.get("consumed_credits") or 0) for row in finished),
        "failed": sum(int(row.get("consumed_credits") or 0) for row in finished if row["outcome"] == "failed"),
        "wasted": wasted_credits(rows),
        "avoided_reuse": sum(int(row.get("estimate_credits") or 0) for row in rows if row["outcome"] == "reused"),
        "avoided_local_repair": sum(int(row.get("estimate_credits") or 0) for row in rows if row["outcome"] == "local_repair"),
    }


def _add(table: Dict[str, int], key: Optional[str], value: int) -> None:
    label = key if key else "(not model-specific)"
    table[label] = table.get(label, 0) + value


def credits_report(job_roots: Iterable[Path]) -> Dict[str, Any]:
    """Credits per model and stage, failed and wasted credits, and credits avoided, over some jobs."""

    report: Dict[str, Any] = {
        "jobs": [],
        "by_model": {},
        "by_stage": {},
        "totals": dict.fromkeys(
            (
                "consumed",
                "failed",
                "wasted",
                "avoided_reuse",
                "avoided_local_repair",
                "retries",
                "rejected",
                "unknown_consumption",
                "balance_delta_mismatch",
            ),
            0,
        ),
    }
    for job in job_roots:
        summary = _job_summary(job)
        rows = summary.pop("rows")
        report["jobs"].append(summary)
        for key in ("consumed", "failed", "wasted", "avoided_reuse", "avoided_local_repair"):
            report["totals"][key] += summary[key]
        for row in rows:
            _tally_row(report, row)
    return report


def _tally_row(report: Dict[str, Any], row: Dict[str, Any]) -> None:
    totals = report["totals"]
    outcome = row["outcome"]
    if outcome in FINISHED:
        credits = int(row.get("consumed_credits") or 0)
        _add(report["by_model"], row.get("model"), credits)
        _add(report["by_stage"], row["stage"], credits)
        totals["unknown_consumption"] += row.get("consumed_credits") is None
        totals["balance_delta_mismatch"] += row.get("reconciliation") == "balance_delta_mismatch"
    totals["retries"] += outcome == "retry"
    totals["rejected"] += outcome == "rejected"


def format_report(report: Dict[str, Any]) -> str:
    totals = report["totals"]
    lines = [
        f"Credits report for {len(report['jobs'])} job(s)",
        f"  consumed {totals['consumed']} credits, of which {totals['failed']} on failed attempts",
        f"  wasted {totals['wasted']} credits (failed attempts and results a later attempt replaced)",
        f"  avoided {totals['avoided_reuse']} credits by reuse and {totals['avoided_local_repair']} by local repair",
        f"  retries {totals['retries']}, stopped calls {totals['rejected']}, "
        f"attempts with unknown consumption {totals['unknown_consumption']}, "
        f"balance deltas that disagree with the provider {totals['balance_delta_mismatch']}",
        "By model",
    ]
    lines += [f"  {name}: {credits}" for name, credits in sorted(report["by_model"].items())]
    lines.append("By stage")
    lines += [f"  {name}: {credits}" for name, credits in sorted(report["by_stage"].items())]
    lines.append("By job")
    lines += [
        f"  {job['job']}: {job['consumed']} consumed, {job['wasted']} wasted, "
        f"{job['avoided_reuse'] + job['avoided_local_repair']} avoided"
        for job in report["jobs"]
    ]
    return "\n".join(lines)
