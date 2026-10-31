"""An export is not accepted unless the exporter could be heard.

The adapter reports `warnings: null` plus an `exporter_report` whose status is
`not_captured` when io_pdx_mesh's logger was out of reach; the client refuses to
hand such an export on, unless the asset profile records an `exporter_report`
exception. Captured warnings are recorded and returned, but do not block.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

import blender_client
from lib import profile_gates as gates


def captured(*records: tuple[str, str], warnings: list | None = None) -> dict:
    items = [{"channel": "logging:io_pdx", "level": level, "message": message} for level, message in records]
    return {
        "mesh": "export/mesh/unit.mesh",
        "warnings": [f"{item['level']}: {item['message']}" for item in items] if warnings is None else warnings,
        "exporter_report": {
            "status": "captured",
            "reason": None,
            "channels": ["logging:io_pdx", "python_warnings"],
            "records": items,
            "warning_count": sum(item["level"] == "WARNING" for item in items),
            "error_count": sum(item["level"] == "ERROR" for item in items),
            "log_records_seen": len(items),
        },
    }


def not_captured() -> dict:
    return {
        "mesh": "export/mesh/unit.mesh",
        "warnings": None,
        "exporter_report": {
            "status": "not_captured",
            "reason": "io_pdx_mesh exposes no IO_PDX_LOG logger, so exporter output cannot be captured.",
            "channels": ["python_warnings"],
            "records": [],
            "warning_count": 0,
            "error_count": 0,
            "log_records_seen": 0,
        },
    }


class ExporterReportFailureTests(unittest.TestCase):
    def test_a_quiet_captured_export_has_no_failures(self) -> None:
        self.assertEqual(gates.exporter_report_failures(captured()), [])

    def test_captured_warnings_are_recorded_but_do_not_block(self) -> None:
        result = captured(("WARNING", "bad transform found on bone 'Hips'"))
        self.assertEqual(gates.exporter_report_failures(result), [])
        self.assertEqual(result["warnings"], ["WARNING: bad transform found on bone 'Hips'"])

    def test_an_export_nobody_could_hear_blocks_and_says_why(self) -> None:
        [failure] = gates.exporter_report_failures(not_captured())
        self.assertIn("not captured", failure)
        self.assertIn("IO_PDX_LOG", failure)

    def test_an_exporter_error_blocks(self) -> None:
        [failure] = gates.exporter_report_failures(captured(("ERROR", "could not write node")))
        self.assertIn("1 error(s): could not write node", failure)

    def test_old_or_malformed_results_block_instead_of_passing(self) -> None:
        old_adapter = {"mesh": "x.mesh", "warnings": []}  # the hard-coded empty list, no report
        self.assertEqual(
            gates.exporter_report_failures(old_adapter), ["the export result carries no exporter report"]
        )
        self.assertEqual(
            gates.exporter_report_failures({"warnings": [], "exporter_report": "captured"}),
            ["the export result carries no exporter report"],
        )
        inconsistent = captured()
        inconsistent["warnings"] = None
        self.assertIn("no warnings list", gates.exporter_report_failures(inconsistent)[0])
        self.assertEqual(len(gates.exporter_report_failures({"exporter_report": {"status": "captured"}})), 1)


class ClientAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        # The constructor looks for the adapter wrapper; acceptance does not need it.
        self.client = object.__new__(blender_client.BlenderAdapterClient)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.job = Path(temp.name)

    def accept(self, result: dict, job_id: str = "unit_slug") -> dict:
        with mock.patch.object(blender_client, "resolve_job_root", return_value=self.job):
            return self.client._accepted_export(job_id, "hoi4_blender_export_mesh", result)

    def test_a_clean_export_is_returned_unchanged(self) -> None:
        result = captured()
        self.assertIs(self.accept(result), result)

    def test_an_uncaptured_export_is_refused_with_a_way_forward(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not accepted: exporter output was not captured.*exporter_report"):
            self.accept(not_captured())

    def test_an_exporter_error_is_refused(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "could not write node"):
            self.accept(captured(("ERROR", "could not write node")))

    def test_a_profile_exception_accepts_an_uncaptured_export_and_records_it(self) -> None:
        (self.job / "job.yaml").write_text(json.dumps({"profile": "static_prop"}), encoding="utf-8")
        exception = {"check": "exporter_report", "reason": "Exporter logger is muted by the studio build."}
        with mock.patch.object(blender_client, "job_profile_exception", return_value=exception) as lookup:
            accepted = self.accept(not_captured())
        lookup.assert_called_once_with(self.job, "exporter_report")
        self.assertIsNone(accepted["warnings"])
        self.assertEqual(accepted["exporter_report_exception"]["reason"], exception["reason"])
        self.assertIn("not captured", accepted["exporter_report_exception"]["failures"][0])

    def test_the_real_profile_lookup_finds_no_exception_in_the_shipped_profiles(self) -> None:
        (self.job / "job.yaml").write_text(json.dumps({"profile": "humanoid_unit"}), encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.accept(not_captured())

    def test_a_job_id_that_is_not_a_slug_gets_no_lookup_and_is_refused(self) -> None:
        with mock.patch.object(blender_client, "job_profile_exception") as lookup, self.assertRaises(RuntimeError):
            self.accept(not_captured(), job_id="owner/unit_slug")
        lookup.assert_not_called()

    def test_export_mesh_and_export_animation_both_go_through_the_acceptance_check(self) -> None:
        for method, tool, arguments in (
            ("export_mesh", "hoi4_blender_export_mesh", ("slug", "blender/a.blend", "export/mesh/a.mesh")),
            ("export_animation", "hoi4_blender_export_animation", ("slug", "blender/a.blend", "Idle", "export/anim/a.anim")),
        ):
            with self.subTest(method=method):
                with mock.patch.object(self.client, "call", return_value=captured()) as call:
                    self.assertEqual(getattr(self.client, method)(*arguments)["warnings"], [])
                self.assertEqual(call.call_args.args[0], tool)
                with mock.patch.object(self.client, "call", return_value=not_captured()), mock.patch.object(
                    blender_client, "resolve_job_root", return_value=self.job
                ), self.assertRaisesRegex(RuntimeError, "not accepted"):
                    getattr(self.client, method)(*arguments)


if __name__ == "__main__":
    unittest.main()
