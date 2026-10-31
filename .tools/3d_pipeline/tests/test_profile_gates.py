"""Candidate acceptance fails closed on measured topology, slots, range and weights.

Every check blocks unless the asset profile records an exception with a reason,
and a measurement that is missing from the report blocks too. The metrics are
supplied as plain dictionaries shaped like the Blender worker's prepare report;
nothing here runs Blender, so it does not show that a real Meshy mesh passes.
"""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_ROOT))

from lib import profile_gates as gates
import profile_exceptions  # placed on sys.path by lib.profile_gates


def profile(**overrides) -> dict:
    value = {
        "triangle_range": {
            "preferred_min": 5000,
            "preferred_max": 30000,
            "hard_max": 60000,
            "working_triangle_target": 5000,
        },
        "materials": {"max_slots": 4},
        "validation": {
            "max_non_manifold_edges": 0,
            "max_boundary_edges": 0,
            "max_loose_components": 1,
            "max_residual_zero_weight_vertices": 0,
        },
        "exceptions": [],
    }
    value.update(overrides)
    return value


def prep(**geometry) -> dict:
    base = {
        "triangles": 8000,
        "non_manifold_edges": 0,
        "loose_boundary_edges": 0,
        "loose_component_count": 1,
        "degenerate_faces": 0,
        "negative_scale_objects": [],
        "dimensions": [1.0, 1.0, 1.5],
    }
    base.update(geometry)
    return {"geometry": base, "materials": {"materials": ["body", "gear"], "shader": "PdxMeshAdvanced"}}


def waive(check: str, reason: str = "Reviewed by the maintainer.") -> dict:
    return profile(exceptions=[{"check": check, "reason": reason}])


def weights(deforming_zero: int = 0, static_zero: int = 0) -> list[dict]:
    return [
        {"object": "Body", "armature_modifiers": ["Armature"], "zero_weight_vertices": deforming_zero},
        {"object": "Prop", "armature_modifiers": [], "zero_weight_vertices": static_zero},
    ]


# check id -> (geometry or prep override that violates it, text expected in the failure)
VIOLATIONS = {
    "non_manifold_edges": ({"non_manifold_edges": 12}, "non-manifold edges 12 exceed profile allowance 0"),
    "boundary_edges": ({"loose_boundary_edges": 40}, "boundary edges 40 exceed profile allowance 0"),
    "loose_components": ({"loose_component_count": 5}, "loose components 5 exceed profile allowance 1"),
    "triangle_range": ({"triangles": 3000}, "triangles 3000 are outside the profile's preferred range 5000-30000"),
}


class EvaluateCandidateTests(unittest.TestCase):
    def test_a_clean_candidate_passes_and_the_unmeasurable_weight_check_says_so(self) -> None:
        result = gates.evaluate_candidate(profile(), prep())
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["exceptions_applied"], [])
        statuses = {check: entry["status"] for check, entry in result["checks"].items()}
        self.assertEqual(
            statuses,
            {
                "non_manifold_edges": "passed",
                "boundary_edges": "passed",
                "loose_components": "passed",
                "triangle_range": "passed",
                "material_slots": "passed",
                "zero_weight_vertices": "not_evaluated",
            },
        )

    def test_each_measured_check_blocks_a_violating_candidate(self) -> None:
        for check, (override, expected) in VIOLATIONS.items():
            with self.subTest(check=check):
                result = gates.evaluate_candidate(profile(), prep(**override))
                self.assertEqual(result["failures"], [expected])
                self.assertEqual(result["checks"][check]["status"], "failed")

    def test_triangle_range_blocks_on_both_sides(self) -> None:
        for triangles in (4999, 30001):
            with self.subTest(triangles=triangles):
                self.assertEqual(len(gates.evaluate_candidate(profile(), prep(triangles=triangles))["failures"]), 1)
        for triangles in (5000, 30000):
            with self.subTest(triangles=triangles):
                self.assertEqual(gates.evaluate_candidate(profile(), prep(triangles=triangles))["failures"], [])

    def test_too_many_material_slots_block(self) -> None:
        candidate = prep()
        candidate["materials"]["materials"] = ["a", "b", "c", "d", "e"]
        result = gates.evaluate_candidate(profile(), candidate)
        self.assertEqual(result["failures"], ["material slots 5 exceed profile maximum 4"])
        candidate["materials"]["materials"] = ["a", "a", "b", "c", "d"]  # one name used twice is four slots
        self.assertEqual(gates.evaluate_candidate(profile(), candidate)["failures"], [])

    def test_a_measurement_missing_from_the_report_blocks_instead_of_passing(self) -> None:
        for key in ("non_manifold_edges", "loose_boundary_edges", "loose_component_count", "triangles"):
            candidate = prep()
            del candidate["geometry"][key]
            with self.subTest(missing=key):
                failures = gates.evaluate_candidate(profile(), candidate)["failures"]
                self.assertTrue(failures and "not measured" in failures[0], failures)
        candidate = prep()
        del candidate["materials"]
        self.assertIn("material slots were not listed", gates.evaluate_candidate(profile(), candidate)["failures"][0])
        candidate = prep(non_manifold_edges="0")
        self.assertIn("not measured", gates.evaluate_candidate(profile(), candidate)["failures"][0])

    def test_a_profile_missing_a_range_or_slot_limit_blocks(self) -> None:
        no_range = profile(triangle_range={"hard_max": 60000})
        self.assertIn("no preferred triangle range", gates.evaluate_candidate(no_range, prep())["failures"][0])
        no_slots = profile(materials={})
        self.assertIn("no materials.max_slots", gates.evaluate_candidate(no_slots, prep())["failures"][0])

    def test_limits_come_from_the_profile_and_default_to_strict(self) -> None:
        relaxed = profile(validation={"max_loose_components": 6, "max_boundary_edges": 50})
        override = {"loose_component_count": 5, "loose_boundary_edges": 40}
        self.assertEqual(gates.evaluate_candidate(relaxed, prep(**override))["failures"], [])
        strict_by_default = profile()
        del strict_by_default["validation"]
        self.assertEqual(len(gates.evaluate_candidate(strict_by_default, prep(**override))["failures"]), 2)
        self.assertEqual(gates.evaluate_candidate(strict_by_default, prep())["failures"], [])
        for bad in (-1, 1.5, "0", True):
            with self.subTest(bad=bad), self.assertRaises(gates.ProfileGateError):
                gates.evaluate_candidate(profile(validation={"max_loose_components": bad}), prep())
        with self.assertRaises(gates.ProfileGateError):
            gates.evaluate_candidate(profile(validation=[]), prep())


class RecordedExceptionTests(unittest.TestCase):
    def test_a_recorded_exception_waives_exactly_its_check_and_is_reported(self) -> None:
        for check, (override, expected) in VIOLATIONS.items():
            with self.subTest(check=check):
                result = gates.evaluate_candidate(waive(check, "Open cuffs are intended."), prep(**override))
                self.assertEqual(result["failures"], [])
                self.assertEqual(result["checks"][check]["status"], "excepted")
                self.assertEqual(result["checks"][check]["exception"]["reason"], "Open cuffs are intended.")
                [applied] = result["exceptions_applied"]
                self.assertEqual(applied["check"], check)
                self.assertEqual(applied["reason"], "Open cuffs are intended.")
                self.assertEqual(applied["problem"], expected)
                self.assertIn("measured", applied)
                self.assertIn("limit", applied)

    def test_material_slot_and_weight_exceptions_work_too(self) -> None:
        candidate = prep()
        candidate["materials"]["materials"] = list("abcde")
        result = gates.evaluate_candidate(waive("material_slots"), candidate)
        self.assertEqual((result["failures"], result["checks"]["material_slots"]["status"]), ([], "excepted"))
        result = gates.evaluate_candidate(waive("zero_weight_vertices"), prep(), weights_after=weights(3))
        self.assertEqual((result["failures"], result["checks"]["zero_weight_vertices"]["status"]), ([], "excepted"))

    def test_an_exception_for_one_check_does_not_waive_another(self) -> None:
        result = gates.evaluate_candidate(
            waive("boundary_edges"), prep(loose_boundary_edges=9, non_manifold_edges=2)
        )
        self.assertEqual(result["failures"], ["non-manifold edges 2 exceed profile allowance 0"])
        self.assertEqual(len(result["exceptions_applied"]), 1)

    def test_a_passing_check_records_no_exception_even_when_one_exists(self) -> None:
        result = gates.evaluate_candidate(waive("boundary_edges"), prep())
        self.assertEqual(result["exceptions_applied"], [])
        self.assertEqual(result["checks"]["boundary_edges"]["status"], "passed")

    def test_malformed_exceptions_are_errors_not_silent_waivers(self) -> None:
        malformed = [
            [{"check": "boundary_edges"}],
            [{"check": "boundary_edges", "reason": ""}],
            [{"check": "boundary_edges", "reason": "   "}],
            [{"check": "boundary_edge", "reason": "typo"}],
            [{"reason": "no check"}],
            [{"check": "boundary_edges", "reason": "a"}, {"check": "boundary_edges", "reason": "b"}],
            ["boundary_edges"],
            "boundary_edges",
        ]
        for exceptions in malformed:
            with self.subTest(exceptions=exceptions), self.assertRaises(gates.ProfileGateError):
                gates.evaluate_candidate(profile(exceptions=exceptions), prep())

    def test_every_check_id_a_profile_may_waive_is_known_to_the_shared_validator(self) -> None:
        for check in gates_checks_that_evaluate_candidate_reports():
            self.assertIn(check, profile_exceptions.CHECK_IDS)


def gates_checks_that_evaluate_candidate_reports() -> set[str]:
    return set(gates.evaluate_candidate(profile(), prep())["checks"])


class ZeroWeightTests(unittest.TestCase):
    def test_only_deforming_meshes_count(self) -> None:
        self.assertEqual(gates.residual_zero_weight_vertices(weights(deforming_zero=0, static_zero=900)), 0)
        self.assertEqual(gates.residual_zero_weight_vertices(weights(deforming_zero=4, static_zero=900)), 4)
        self.assertEqual(gates.residual_zero_weight_vertices([]), 0)

    def test_malformed_weight_metrics_are_not_a_zero(self) -> None:
        for value in (None, "x", [1], [{"armature_modifiers": ["A"], "zero_weight_vertices": "3"}]):
            with self.subTest(value=value):
                self.assertIsNone(gates.residual_zero_weight_vertices(value))

    def test_residual_zero_weight_vertices_after_sanitizing_block(self) -> None:
        result = gates.evaluate_candidate(profile(), prep(), weights_after=weights(deforming_zero=3))
        self.assertEqual(
            result["failures"], ["residual zero-weight deforming vertices 3 exceed profile allowance 0"]
        )

    def test_static_meshes_with_no_skin_do_not_block(self) -> None:
        result = gates.evaluate_candidate(profile(), prep(), weights_after=weights(static_zero=500))
        self.assertEqual(result["failures"], [])
        self.assertEqual(result["checks"]["zero_weight_vertices"]["status"], "passed")

    def test_the_allowance_comes_from_the_profile(self) -> None:
        relaxed = profile(validation={"max_residual_zero_weight_vertices": 3})
        self.assertEqual(gates.evaluate_candidate(relaxed, prep(), weights_after=weights(3))["failures"], [])
        self.assertEqual(len(gates.evaluate_candidate(relaxed, prep(), weights_after=weights(4))["failures"]), 1)

    def test_weights_are_found_where_the_report_carries_post_sanitize_metrics(self) -> None:
        sanitized = {"policy": "keep_four_strongest", "weights_after": weights(deforming_zero=2)}
        for key in ("base_weight_sanitization", "weight_sanitization"):
            candidate = prep()
            candidate[key] = sanitized
            with self.subTest(key=key):
                self.assertEqual(len(gates.evaluate_candidate(profile(), candidate)["failures"]), 1)
        candidate = prep()
        candidate["weights_after"] = weights(deforming_zero=2)
        self.assertEqual(len(gates.evaluate_candidate(profile(), candidate)["failures"]), 1)

    def test_explicit_weights_may_be_a_list_a_dict_or_the_sanitize_operation_report(self) -> None:
        residual = weights(deforming_zero=2)
        for explicit in (residual, {"weights_after": residual}, {"weights": {"weights_after": residual}}):
            with self.subTest(shape=type(explicit).__name__):
                result = gates.evaluate_candidate(profile(), prep(), weights_after=explicit)
                self.assertEqual(len(result["failures"]), 1)

    def test_a_report_without_post_sanitize_metrics_is_not_evaluated_rather_than_passed(self) -> None:
        candidate = prep()
        candidate["base_weight_sanitization"] = None
        entry = gates.evaluate_candidate(profile(), candidate)["checks"]["zero_weight_vertices"]
        self.assertEqual(entry["status"], "not_evaluated")
        self.assertIn("no post-sanitize weight metrics", entry["reason"])

    def test_malformed_weights_block(self) -> None:
        result = gates.evaluate_candidate(profile(), prep(), weights_after=[{"armature_modifiers": ["A"]}])
        self.assertEqual(result["failures"], ["post-sanitize weight metrics are malformed"])


class ShippedProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads((PIPELINE_ROOT / "config/asset_profiles.json").read_text(encoding="utf-8"))["profiles"]

    def test_every_shipped_profile_declares_validation_limits_and_an_empty_exception_list(self) -> None:
        self.assertTrue(self.registry)
        for name, value in self.registry.items():
            with self.subTest(profile=name):
                self.assertEqual(set(value["validation"]), set(gates.DEFAULT_LIMITS))
                for limit in value["validation"].values():
                    self.assertIsInstance(limit, int)
                    self.assertGreaterEqual(limit, 0)
                self.assertEqual(value["exceptions"], [])
                self.assertEqual(profile_exceptions.index_exceptions(value), {})

    def test_every_profile_working_target_sits_inside_its_preferred_range(self) -> None:
        for name, value in self.registry.items():
            triangle_range = value["triangle_range"]
            with self.subTest(profile=name):
                self.assertLessEqual(triangle_range["preferred_min"], triangle_range["working_triangle_target"])
                self.assertLessEqual(triangle_range["working_triangle_target"], triangle_range["preferred_max"])
                self.assertLessEqual(triangle_range["preferred_max"], triangle_range["hard_max"])

    def test_a_clean_candidate_at_the_working_target_passes_every_shipped_profile(self) -> None:
        for name, value in self.registry.items():
            with self.subTest(profile=name):
                candidate = prep(triangles=value["triangle_range"]["working_triangle_target"])
                self.assertEqual(gates.evaluate_candidate(value, candidate)["failures"], [])

    def test_load_profile_and_job_profile_resolve_through_the_registry(self) -> None:
        self.assertEqual(gates.load_profile("humanoid_unit"), self.registry["humanoid_unit"])
        with tempfile.TemporaryDirectory() as temp:
            job = Path(temp)
            (job / "job.yaml").write_text(json.dumps({"profile": "static_prop"}), encoding="utf-8")
            name, resolved = gates.job_profile(job)
        self.assertEqual((name, resolved), ("static_prop", self.registry["static_prop"]))

    def test_unresolvable_profiles_are_errors(self) -> None:
        with self.assertRaises(gates.ProfileGateError):
            gates.load_profile("no_such_profile")
        with tempfile.TemporaryDirectory() as temp:
            job = Path(temp)
            with self.assertRaises(gates.ProfileGateError):  # no job.yaml
                gates.job_profile(job)
            (job / "job.yaml").write_text(json.dumps({"asset_id": "x"}), encoding="utf-8")
            with self.assertRaises(gates.ProfileGateError):  # no profile named
                gates.job_profile(job)
            (job / "job.yaml").write_text(json.dumps({"profile": "no_such_profile"}), encoding="utf-8")
            with self.assertRaises(gates.ProfileGateError):
                gates.job_profile(job)
            self.assertIsNone(gates.job_profile_exception(job, "boundary_edges"))


def import_run_pilot():
    """Import run_pilot with a placeholder key; it exits at import when the variable is blank."""

    with mock.patch.dict(os.environ, {"MESHY_API_KEY": "placeholder-not-a-real-key"}):
        import run_pilot

    return run_pilot


class CandidateGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.run_pilot = import_run_pilot()

    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.job = Path(temp.name)
        (self.job / "job.yaml").write_text(json.dumps({"profile": "static_prop"}), encoding="utf-8")

    def gate(self, candidate: dict, **kwargs) -> None:
        self.run_pilot.candidate_gate(
            self.job, candidate, hard_max=60000, stage="provider_candidate", **kwargs
        )

    def record(self) -> dict:
        return json.loads((self.job / "validation/provider_candidate_gate.json").read_text(encoding="utf-8"))

    def test_a_clean_candidate_passes_and_the_record_names_the_profile_and_checks(self) -> None:
        self.gate(prep(triangles=5000))
        record = self.record()
        self.assertEqual(record["status"], "passed")
        self.assertEqual(record["profile"], "static_prop")
        self.assertEqual(record["failures"], [])
        self.assertEqual(record["checks"]["boundary_edges"]["status"], "passed")
        self.assertEqual(record["exceptions_applied"], [])

    def test_the_gate_no_longer_claims_a_visual_review_that_has_not_happened(self) -> None:
        self.gate(prep(triangles=5000))
        record = self.record()
        self.assertTrue(record["visual_review_required"])
        self.assertEqual(record["visual_review"], "pending_parent_review")

    def test_each_new_check_blocks_the_gate_and_writes_a_blocked_record(self) -> None:
        for check, (override, expected) in VIOLATIONS.items():
            with self.subTest(check=check):
                candidate = prep(triangles=5000)
                candidate["geometry"].update(override)
                with self.assertRaisesRegex(RuntimeError, "Geometry gate failed for provider_candidate"):
                    self.gate(candidate)
                record = self.record()
                self.assertEqual(record["status"], "blocked")
                self.assertIn(expected, record["failures"])
                self.assertEqual(record["checks"][check]["status"], "failed")

    def test_too_many_material_slots_block_the_gate(self) -> None:
        candidate = prep(triangles=5000)
        candidate["materials"]["materials"] = list("abcde")
        with self.assertRaisesRegex(RuntimeError, "material slots 5 exceed profile maximum 4"):
            self.gate(candidate)

    def test_a_profile_exception_lets_the_gate_pass_and_the_record_says_why(self) -> None:
        candidate = prep(triangles=5000, loose_boundary_edges=40)
        self.gate(candidate, profile=waive("boundary_edges", "Open base is hidden by the ground."))
        record = self.record()
        self.assertEqual(record["status"], "passed_with_exceptions")
        self.assertEqual(record["failures"], [])
        [applied] = record["exceptions_applied"]
        self.assertEqual(applied["reason"], "Open base is hidden by the ground.")
        self.assertEqual(applied["measured"], 40)

    def test_residual_zero_weights_block_unless_excepted(self) -> None:
        candidate = prep(triangles=5000)
        with self.assertRaisesRegex(RuntimeError, "residual zero-weight deforming vertices 2"):
            self.gate(candidate, weights_after=weights(deforming_zero=2))
        self.gate(candidate, weights_after=weights(deforming_zero=2), profile=waive("zero_weight_vertices"))
        self.assertEqual(self.record()["status"], "passed_with_exceptions")

    def test_the_original_hard_blockers_still_block_and_cannot_be_waived(self) -> None:
        blockers = {
            "no triangles": prep(triangles=0),
            "triangles exceed hard maximum": prep(triangles=70000),
            "degenerate faces remain": prep(triangles=5000, degenerate_faces=2),
            "negative scale remains": prep(triangles=5000, negative_scale_objects=["Body"]),
        }
        for expected, candidate in blockers.items():
            everything_waived = profile(
                exceptions=[{"check": check, "reason": "waived"} for check in profile_exceptions.CHECK_IDS]
            )
            with self.subTest(blocker=expected), self.assertRaisesRegex(RuntimeError, "Geometry gate failed"):
                self.gate(candidate, profile=everything_waived)
            self.assertIn(expected, " ".join(self.record()["failures"]))

    def test_the_runtime_footprint_budget_still_blocks(self) -> None:
        candidate = prep(triangles=5000, dimensions=[6.0, 2.0, 1.0])
        with self.assertRaisesRegex(RuntimeError, "runtime footprint"):
            self.gate(candidate, max_runtime_footprint_m=4.0, runtime_entity_scale=1.0)
        self.gate(candidate, max_runtime_footprint_m=4.0, runtime_entity_scale=0.5)

    def test_an_unresolvable_profile_blocks_instead_of_skipping_the_profile_checks(self) -> None:
        (self.job / "job.yaml").write_text(json.dumps({"profile": "no_such_profile"}), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "asset profile checks could not run"):
            self.gate(prep(triangles=5000))
        self.assertEqual(self.record()["status"], "blocked")
        (self.job / "job.yaml").unlink()
        with self.assertRaisesRegex(RuntimeError, "asset profile checks could not run"):
            self.gate(prep(triangles=5000))

    def test_a_malformed_profile_exception_blocks_the_gate(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "asset profile checks could not run"):
            self.gate(prep(triangles=5000), profile=profile(exceptions=[{"check": "boundary_edges"}]))

    def test_the_existing_call_sites_need_no_change(self) -> None:
        # Callers pass only these keywords today; the profile comes from the job's job.yaml.
        self.run_pilot.candidate_gate(
            self.job,
            copy.deepcopy(prep(triangles=5000)),
            hard_max=60000,
            stage="shared_humanoid_candidate",
            max_runtime_footprint_m=None,
            runtime_entity_scale=1.0,
        )
        self.assertTrue((self.job / "validation/shared_humanoid_candidate_gate.json").is_file())


if __name__ == "__main__":
    unittest.main()
