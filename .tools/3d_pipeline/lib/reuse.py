"""Reuse before paying: another job's result for the same request, and unreconciled submissions.

Before a paid create the runner checks, in order:
  1. a succeeded task for the same stage in this job (run_pilot.provider_task)
  2. a succeeded task in another job under the same jobs root whose request fingerprint matches
     (SHA-256 of the input file's bytes plus the canonical JSON of the request arguments)
  3. a submission-journal entry for the same fingerprint that never produced a result; it blocks the
     new call until someone reconciles it, because the create may have reached Meshy and been charged

Meshy's own task list (`meshy_list_tasks`, free) is deliberately not searched automatically: a listed
task carries nothing that identifies the input image, so a match could adopt the wrong task. The
block message tells the person reconciling what to look for.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from lib.credits import (
    RESERVATIONS,
    SETTLEMENTS,
    SUCCEEDED_STATUSES,
    read_ledger,
    settle,
)
from lib.generation import load_contract
from lib.paths import file_record, read_json, utc_now, write_json

BLOCKING_STATES = {"submission_started", "uncertain"}
TOOL_TASK_TYPES = {
    "meshy_image_to_3d": "image-to-3d",
    "meshy_remesh": "remesh",
    "meshy_rig": "rigging",
    "meshy_animate": "animation",
    "meshy_text_to_motion": "text-to-motion",
}
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MANIFEST_SUFFIX = ".manifest.json"


def sibling_jobs(job: Path) -> List[Path]:
    """Every other job folder under the same jobs root."""

    root = job.parent
    if not root.is_dir():
        return []
    return sorted(child for child in root.iterdir() if child.is_dir() and child != job and (child / "provider").is_dir())


def _age_hours(timestamp: Any, now: datetime) -> Optional[float]:
    try:
        recorded = datetime.strptime(str(timestamp), TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (now - recorded) / timedelta(hours=1)


def downloaded_manifests(job: Path, task_id: str) -> List[Path]:
    """Manifests of files this job saved from the task whose file is still on disk."""

    found = []
    for manifest in sorted((job / "provider" / "downloads").glob(f"*{MANIFEST_SUFFIX}")):
        saved = manifest.with_name(manifest.name[: -len(MANIFEST_SUFFIX)])
        if read_json(manifest).get("task_id") == task_id and saved.is_file():
            found.append(manifest)
    return found


def find_other_job_result(
    job: Path,
    fingerprint: str,
    *,
    now: Optional[datetime] = None,
    retention_hours: Optional[float] = None,
) -> Dict[str, Any]:
    """The newest succeeded task elsewhere with this fingerprint that can still be used.

    A result is usable while Meshy still keeps it (the retention window) or while the other job
    holds its downloaded files. The returned dict also says what was checked, for the decision record.
    """

    now = now or datetime.now(timezone.utc)
    if retention_hours is None:
        retention_hours = float(load_contract()["provider_policy"]["task_retention_hours"])
    candidates = []
    expired = []
    others = sibling_jobs(job)
    for other in others:
        for task_path in sorted((other / "provider" / "tasks").glob("*.json")):
            record = read_json(task_path)
            if record.get("fingerprint") != fingerprint or record.get("status") not in SUCCEEDED_STATUSES:
                continue
            age = _age_hours(record.get("recorded_at") or record.get("created_at"), now)
            kept_locally = bool(downloaded_manifests(other, str(record.get("task_id"))))
            if kept_locally or (age is not None and age < retention_hours):
                candidates.append({"job": other, "record": record, "recorded_at": str(record.get("recorded_at"))})
            else:
                expired.append(f"{other.name}:{record.get('stage')}")
    candidates.sort(key=lambda item: item["recorded_at"], reverse=True)
    return {"jobs_checked": len(others), "match": candidates[0] if candidates else None, "expired": expired}


def copy_artifacts(source: Path, destination: Path, task_id: str) -> List[str]:
    """Copy the files another job downloaded from a task, with their texture folders and manifests.

    Existing files are never overwritten with different bytes. Each copied manifest is rewritten to
    describe the copy and to say where it came from. Returns the copied file names.
    """

    copied = []
    target_root = destination / "provider" / "downloads"
    for manifest in downloaded_manifests(source, task_id):
        name = manifest.name[: -len(MANIFEST_SUFFIX)]
        saved = manifest.with_name(name)
        target = target_root / name
        target_root.mkdir(parents=True, exist_ok=True)
        if target.exists() and file_record(target)["sha256"] != file_record(saved)["sha256"]:
            raise RuntimeError(f"Refusing to overwrite {target} with a different file from {source.name}.")
        if not target.exists():
            shutil.copy2(saved, target)
        textures = saved.with_name(f"{saved.stem}_textures")
        if textures.is_dir() and not (target_root / textures.name).exists():
            shutil.copytree(textures, target_root / textures.name)
        record = read_json(manifest)
        record["file"] = file_record(target, relative_to=destination)
        record["reused_from"] = {"job": source.name, "task_id": task_id}
        write_json(target_root / manifest.name, record)
        copied.append(name)
    return copied


def _has_task_id(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            (key.lower() in {"task_id", "taskid"} and item) or _has_task_id(item) for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_has_task_id(item) for item in value)
    return False


def unreconciled_submissions(jobs: List[Path], fingerprint: str) -> List[Dict[str, Any]]:
    """Journal entries for this request that started or went uncertain and never produced a task id."""

    found = []
    for job in jobs:
        for path in sorted((job / "provider" / "submissions").glob("*.json")):
            entry = read_json(path)
            if (
                entry.get("fingerprint") == fingerprint
                and entry.get("state") in BLOCKING_STATES
                and not _has_task_id(entry.get("response"))
            ):
                found.append({"file": path, "state": entry["state"], "timestamp": entry.get("timestamp"), "job": job.name})
    return found


def block_message(stage: str, operation: str, blockers: List[Dict[str, Any]]) -> str:
    first = blockers[0]
    return (
        f"Unreconciled submission blocks a new {operation} call for {stage}: {first['file']} (job {first['job']}) "
        f"is in state {first['state']}, written {first['timestamp']}, for the same request and has no task id. "
        "The create may have reached Meshy and been charged. Nothing was submitted. Reconcile it first: look for a "
        "task created at or after that time with the free meshy_list_tasks (matching task_type, newest first). "
        "If Meshy shows none, run lib.reuse.reconcile_submission(<that file>), which releases the reserved credits. "
        "If Meshy shows one, run lib.reuse.reconcile_submission(<that file>, task_id=<its id>), which records it so "
        "the run resumes that task instead of paying again."
    )


def reconcile_submission(journal: Path, *, task_id: Optional[str] = None, note: str = "") -> Dict[str, Any]:
    """Mark an unresolved submission reconciled and settle the credits it reserved.

    Without a task id the create is taken to have never reached Meshy: its reservation is released as
    rejected. With a task id the task is recorded as PENDING for its stage, so the next run polls it.
    """

    job = journal.parents[2]
    entry = read_json(journal)
    ledger = read_ledger(job)
    settled = {row["attempt_id"] for row in ledger if row["outcome"] in SETTLEMENTS}
    reservation = next(
        (
            row
            for row in reversed(ledger)
            if row["outcome"] in RESERVATIONS
            and row["attempt_id"] not in settled
            and row.get("fingerprint") == entry.get("fingerprint")
        ),
        None,
    )
    if task_id is not None and reservation is None:
        raise ValueError("No open ledger reservation matches this submission; there is no stage to record the task under.")
    entry.update(state="reconciled", reconciliation={"timestamp": utc_now(), "task_id": task_id, "note": note})
    write_json(journal, entry)
    if reservation is None:
        return entry
    if task_id is None:
        settle(job, reservation["attempt_id"], outcome="rejected", consumed=0, source="none", reason="reconciled: no Meshy task was created")
        return entry
    write_json(
        job / "provider" / "tasks" / f"{reservation['stage']}.json",
        {
            "schema_version": "1.0.0",
            "stage": reservation["stage"],
            "task_id": task_id,
            "task_type": TOOL_TASK_TYPES.get(str(entry.get("tool")), str(entry.get("tool"))),
            "status": "PENDING",
            "initial_response": {},
            "estimated_credits": reservation.get("estimate_credits"),
            "fingerprint": reservation.get("fingerprint"),
            "operation": reservation.get("operation"),
            "model": reservation.get("model"),
            "recovered_from_submission": journal.name,
            "created_at": utc_now(),
        },
    )
    return entry
