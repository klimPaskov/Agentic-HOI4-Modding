"""Exporter warnings are captured from io_pdx_mesh's logger, never hard-coded empty.

A fake exporter logs through a real `logging.Logger`, the same channel
io_pdx_mesh uses (`io_pdx_mesh.IO_PDX_LOG`). No Blender is involved, so this does
not show what a real export reports.
"""

from __future__ import annotations

import ast
import importlib.util
import logging
import types
import unittest
import warnings
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = PIPELINE_ROOT / "adapter"
_SPEC = importlib.util.spec_from_file_location("exporter_log_capture", ADAPTER_ROOT / "exporter_log_capture.py")
capture_module = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(capture_module)
ExporterLogCapture = capture_module.ExporterLogCapture
exporter_warnings = capture_module.exporter_warnings


class ExporterLogCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = logging.getLogger("io_pdx_capture_test")
        self.addCleanup(setattr, self.logger, "disabled", False)
        self.addCleanup(self.logger.setLevel, logging.NOTSET)
        self.logger.setLevel(logging.DEBUG)
        self.logger.disabled = False

    def test_warnings_and_errors_logged_during_the_export_are_returned(self) -> None:
        def exporter() -> None:
            self.logger.info("exporting - model.mesh")
            self.logger.warning("bad transform found on bone 'Hips' (defaulting to bone scale 1.0)")
            self.logger.error("could not write node")

        capture = ExporterLogCapture(self.logger)
        capture.call(exporter)
        report = capture.report()
        self.assertEqual(report["status"], "captured")
        self.assertIsNone(report["reason"])
        self.assertEqual(report["warning_count"], 1)
        self.assertEqual(report["error_count"], 1)
        self.assertEqual(report["log_records_seen"], 3)
        self.assertEqual(
            exporter_warnings(report),
            [
                "WARNING: bad transform found on bone 'Hips' (defaulting to bone scale 1.0)",
                "ERROR: could not write node",
            ],
        )
        self.assertEqual(report["records"][0]["channel"], "logging:io_pdx_capture_test")

    def test_a_quiet_export_is_an_empty_list_which_is_not_the_same_as_not_captured(self) -> None:
        capture = ExporterLogCapture(self.logger)
        capture.call(lambda: self.logger.info("exporting - model.mesh"))
        report = capture.report()
        self.assertEqual(report["status"], "captured")
        self.assertEqual(exporter_warnings(report), [])
        self.assertEqual(report["warning_count"], 0)

    def test_python_warnings_raised_inside_the_exporter_are_recorded_too(self) -> None:
        def exporter() -> None:
            warnings.warn("Mesh.calc_normals is deprecated", DeprecationWarning, stacklevel=2)

        capture = ExporterLogCapture(self.logger)
        capture.call(exporter)
        report = capture.report()
        self.assertEqual(
            exporter_warnings(report), ["WARNING: DeprecationWarning: Mesh.calc_normals is deprecated"]
        )
        self.assertIn("python_warnings", report["channels"])

    def test_a_logger_filtered_above_warning_is_lowered_for_the_call_and_restored(self) -> None:
        self.logger.setLevel(logging.ERROR)
        capture = ExporterLogCapture(self.logger)
        capture.call(lambda: self.logger.warning("heard"))
        self.assertEqual(exporter_warnings(capture.report()), ["WARNING: heard"])
        self.assertEqual(self.logger.level, logging.ERROR)
        self.assertEqual(self.logger.handlers, [])

    def test_handler_and_warning_filters_are_restored_even_when_the_export_raises(self) -> None:
        filters_before = list(warnings.filters)

        def exporter() -> None:
            self.logger.warning("about to fail")
            raise RuntimeError("exporter sentinel")

        capture = ExporterLogCapture(self.logger)
        with self.assertRaisesRegex(RuntimeError, "exporter sentinel"):
            capture.call(exporter)
        self.assertEqual(self.logger.handlers, [])
        self.assertEqual(warnings.filters, filters_before)
        self.assertEqual(exporter_warnings(capture.report()), ["WARNING: about to fail"])

    def test_no_logger_means_not_captured_and_no_warnings_list(self) -> None:
        for missing in (None, "io_pdx", object()):
            with self.subTest(missing=missing):
                capture = ExporterLogCapture(missing)
                capture.call(lambda: None)
                report = capture.report()
                self.assertEqual(report["status"], "not_captured")
                self.assertIn("IO_PDX_LOG", report["reason"])
                self.assertIsNone(exporter_warnings(report))

    def test_a_disabled_logger_is_not_captured_because_warnings_would_be_dropped(self) -> None:
        self.logger.disabled = True
        capture = ExporterLogCapture(self.logger)
        capture.call(lambda: self.logger.warning("silently dropped"))
        report = capture.report()
        self.assertEqual(report["status"], "not_captured")
        self.assertIn("disabled", report["reason"])
        self.assertIsNone(exporter_warnings(report))
        self.assertEqual(self.logger.handlers, [])

    def test_globally_disabled_logging_is_not_captured(self) -> None:
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)
        capture = ExporterLogCapture(self.logger)
        capture.call(lambda: None)
        self.assertEqual(capture.report()["status"], "not_captured")

    def test_run_captured_calls_the_named_exporter_and_listens_on_the_modules_logger(self) -> None:
        calls = []

        def export_meshfile(path: str, **kwargs: object) -> str:
            calls.append((path, kwargs))
            self.logger.warning("texture path missing")
            return "ignored"

        pdx = {"module": types.SimpleNamespace(IO_PDX_LOG=self.logger), "export_meshfile": export_meshfile}
        report = capture_module.run_captured(pdx, "export_meshfile", "out/unit.mesh", exp_mesh=True)
        self.assertEqual(calls, [("out/unit.mesh", {"exp_mesh": True})])
        self.assertEqual(exporter_warnings(report), ["WARNING: texture path missing"])

    def test_run_captured_reports_not_captured_when_the_module_has_no_logger(self) -> None:
        calls = []
        for pdx in (
            {"export_animfile": lambda path: calls.append(path)},
            {"module": types.SimpleNamespace(), "export_animfile": lambda path: calls.append(path)},
        ):
            report = capture_module.run_captured(pdx, "export_animfile", "out/a.anim")
            self.assertEqual(report["status"], "not_captured")
            self.assertIsNone(exporter_warnings(report))
        self.assertEqual(calls, ["out/a.anim", "out/a.anim"])

    def test_report_before_the_call_finishes_is_refused(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "after the export call"):
            ExporterLogCapture(self.logger).report()

    def test_worker_export_reports_no_longer_hardcode_an_empty_warnings_list(self) -> None:
        tree = ast.parse((ADAPTER_ROOT / "blender_worker.py").read_text(encoding="utf-8"))
        for name, exporter in (("export_mesh", "export_meshfile"), ("export_animation", "export_animfile")):
            function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
            source = ast.unparse(function)
            with self.subTest(function=name):
                self.assertNotIn("'warnings': []", source)
                self.assertIn("'warnings': exporter_warnings(exporter_report)", source)
                self.assertIn("'exporter_report': exporter_report", source)
                self.assertIn("exporter_report = run_captured(pdx, '" + exporter + "'", source)


if __name__ == "__main__":
    unittest.main()
