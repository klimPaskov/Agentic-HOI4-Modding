"""Capture what io_pdx_mesh reports while it exports.

io_pdx_mesh reports every problem through the standard `logging` logger that
the addon exposes as `io_pdx_mesh.IO_PDX_LOG` (named "io_pdx"); Blender API
deprecations raised inside the export surface through `warnings`. The export
reports used to carry a hard-coded empty `warnings` list, which read as "the
exporter had nothing to say". The capture below records both channels, and
when the logger cannot be reached it says so (`not_captured`) instead of
returning an empty list, so a caller can refuse to accept the export.

Standard library only; the Blender worker imports it from the flat adapter
closure.
"""

from __future__ import annotations

import logging
import warnings
from typing import Any, Dict, List, Mapping, Optional


CAPTURED = "captured"
NOT_CAPTURED = "not_captured"
PYTHON_WARNINGS_CHANNEL = "python_warnings"


class _Collector(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.NOTSET)
        self.records: List[Dict[str, str]] = []
        self.seen = 0

    def emit(self, record: logging.LogRecord) -> None:
        self.seen += 1
        if record.levelno >= logging.WARNING:
            self.records.append(
                {
                    "channel": f"logging:{record.name}",
                    "level": record.levelname,
                    "message": record.getMessage(),
                }
            )


class ExporterLogCapture:
    """Context manager around one exporter call; `report()` summarizes it."""

    def __init__(self, logger: Optional[Any]) -> None:
        self._logger = logger if isinstance(logger, logging.Logger) else None
        self._reason: Optional[str] = None
        if self._logger is None:
            self._reason = "io_pdx_mesh exposes no IO_PDX_LOG logger, so exporter output cannot be captured."
        self._collector = _Collector()
        self._previous_level: Optional[int] = None
        self._warning_context: Optional[Any] = None
        self._warning_log: List[Any] = []
        self._python_records: List[Dict[str, str]] = []
        self._finished = False

    def __enter__(self) -> "ExporterLogCapture":
        logger = self._logger
        if logger is not None:
            if logger.disabled or logging.root.manager.disable >= logging.WARNING:
                self._reason = f"Logger {logger.name!r} is disabled, so exporter warnings would be dropped."
            else:
                self._previous_level = logger.level
                if logger.getEffectiveLevel() > logging.WARNING:
                    logger.setLevel(logging.WARNING)
                logger.addHandler(self._collector)
        self._warning_context = warnings.catch_warnings(record=True)
        self._warning_log = self._warning_context.__enter__()
        warnings.simplefilter("always")
        return self

    def __exit__(self, *exc_info: Any) -> bool:
        if self._warning_context is not None:
            self._warning_context.__exit__(*exc_info)
            self._python_records = [
                {
                    "channel": PYTHON_WARNINGS_CHANNEL,
                    "level": "WARNING",
                    "message": f"{item.category.__name__}: {item.message}",
                }
                for item in self._warning_log
            ]
        logger = self._logger
        if logger is not None and self._previous_level is not None:
            logger.removeHandler(self._collector)
            logger.setLevel(self._previous_level)
        self._finished = True
        return False

    def call(self, function: Any, *args: Any, **kwargs: Any) -> Any:
        """Run one exporter call under the capture and return its result."""

        with self:
            return function(*args, **kwargs)

    def report(self) -> Dict[str, Any]:
        """Return the capture state, every warning-or-worse record and counts."""

        if not self._finished:
            raise RuntimeError("The exporter capture report is only available after the export call.")
        # Python warnings are always collected; the logging channel is live only
        # when a logger was found and enabled. A dead logging channel means the
        # exporter's own warnings could not be seen, whatever else was collected.
        logging_live = self._logger is not None and self._reason is None
        channels = [PYTHON_WARNINGS_CHANNEL]
        if logging_live:
            channels.insert(0, f"logging:{self._logger.name}")
        records = list(self._collector.records) + self._python_records
        return {
            "status": CAPTURED if logging_live else NOT_CAPTURED,
            "reason": self._reason,
            "channels": channels,
            "records": records,
            "warning_count": sum(item["level"] == "WARNING" for item in records),
            "error_count": sum(item["level"] in {"ERROR", "CRITICAL"} for item in records),
            "log_records_seen": self._collector.seen,
        }


def run_captured(pdx: Mapping[str, Any], name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Run `pdx[name](*args, **kwargs)` under a capture on io_pdx_mesh's logger; return the report."""

    capture = ExporterLogCapture(getattr(pdx.get("module"), "IO_PDX_LOG", None))
    capture.call(pdx[name], *args, **kwargs)
    return capture.report()


def exporter_warnings(report: Dict[str, Any]) -> Optional[List[str]]:
    """Return the captured warning text, or None when the capture failed.

    None is deliberately not an empty list: an empty list means the exporter was
    heard and reported nothing.
    """

    if report.get("status") != CAPTURED:
        return None
    return [f"{item['level']}: {item['message']}" for item in report["records"]]
