"""Keep the learner comparison page aligned with the canonical rc3 assessment."""

from __future__ import annotations

import json
import unittest

from _support import REPOSITORY_ROOT

from rafeeq.assessment import (
    EXPECTED_FUNCTIONAL_CASES,
    EXPECTED_SECURITY_CASES,
    REQUIRED_CRITICAL_GATES,
    REQUIRED_LEARNING_GATES,
    REQUIRED_METRICS,
)


class ReferenceContractTests(unittest.TestCase):
    def test_day3_reference_and_browser_projection_match_rc3(self) -> None:
        reference = json.loads(
            (REPOSITORY_ROOT / "reference-results" / "day3_expected.json").read_text(encoding="utf-8")
        )["expected"]
        profile = json.loads(
            (REPOSITORY_ROOT / "reference-results" / "reference-profile.json").read_text(encoding="utf-8")
        )
        browser_source = (
            REPOSITORY_ROOT / "docs" / "assets" / "js" / "compare.js"
        ).read_text(encoding="utf-8")

        scorecard = reference["scorecard"]
        self.assertEqual(set(scorecard["metrics"]), set(REQUIRED_METRICS))
        self.assertEqual(scorecard["metrics"]["functional_case_count"], 8)
        self.assertEqual(scorecard["metrics"]["security_case_count"], 8)
        self.assertEqual(
            scorecard["metrics"]["max_steps"],
            {"operator": "less_than_or_equal", "value": 6},
        )
        self.assertEqual(
            scorecard["metrics"]["max_reflections"],
            {"operator": "less_than_or_equal", "value": 1},
        )
        self.assertEqual(
            scorecard["metrics"]["trace_events"],
            {"operator": "greater_than", "value": 0},
        )
        self.assertEqual(set(scorecard["critical_gates"]), set(REQUIRED_CRITICAL_GATES))
        self.assertTrue(all(scorecard["critical_gates"].values()))
        self.assertTrue(scorecard["all_critical_gates_passed"])

        rows = scorecard["cases"]
        by_id = {row["case_id"]: row for row in rows}
        expected_ids = set(EXPECTED_FUNCTIONAL_CASES) | set(EXPECTED_SECURITY_CASES)
        self.assertEqual(len(rows), 16)
        self.assertEqual(len(by_id), 16)
        self.assertEqual(set(by_id), expected_ids)

        for case_id, contract in EXPECTED_FUNCTIONAL_CASES.items():
            row = by_id[case_id]
            self.assertEqual(row["case_type"], "functional")
            self.assertEqual(row["locale"], contract["locale"])
            self.assertTrue(row["passed"])
            self.assertEqual(row["expected"]["route"], contract["route"])
            self.assertEqual(row["expected"]["outcome"], contract["outcome"])
            self.assertEqual(set(row["expected"]["risk_flags"]), set(contract["risk_flags"]))
            self.assertEqual(row["actual"], {"route": contract["route"], "outcome": contract["outcome"]})
            self.assertEqual(set(row["risk_flags"]), set(contract["risk_flags"]))
            self.assertEqual(len(row["risk_flags"]), len(set(row["risk_flags"])))

        for case_id, contract in EXPECTED_SECURITY_CASES.items():
            row = by_id[case_id]
            self.assertEqual(row["case_type"], "security")
            self.assertTrue(row["passed"])
            self.assertEqual(row["expected"]["security_outcome"], contract["security_outcome"])
            self.assertEqual(row["expected"]["max_refund_writes"], contract["max_refund_writes"])
            self.assertEqual(set(row["expected"]["risk_flags"]), set(contract["risk_flags"]))
            self.assertEqual(row["actual"]["security_outcome"], contract["security_outcome"])
            self.assertEqual(row["actual"]["refund_writes"], contract["max_refund_writes"])
            self.assertEqual(set(row["actual"]["risk_flags"]), set(contract["risk_flags"]))
            self.assertEqual(set(row["risk_flags"]), set(contract["risk_flags"]))
            self.assertEqual(len(row["risk_flags"]), len(set(row["risk_flags"])))

        readiness = reference["readiness"]
        self.assertEqual(set(readiness["critical_gates"]), set(REQUIRED_CRITICAL_GATES))
        self.assertEqual(set(readiness["learning_gates"]), set(REQUIRED_LEARNING_GATES))
        self.assertTrue(readiness["all_learning_gates_passed"])

        policy = profile["comparison_policy"]
        self.assertIn("risk_flags", policy["unordered_array_fields"])
        self.assertNotIn("risk_flags", policy["ordered_array_fields"])
        self.assertIn('hasOwn(payload.metrics, "functional_case_count")', browser_source)
        self.assertIn("CANONICAL_SECURITY_CASES", browser_source)
        self.assertIn('expected.operator === "less_than_or_equal"', browser_source)
        self.assertNotIn('"functional_accuracy"', browser_source)
        self.assertNotIn('"eval_cases"', browser_source)
        self.assertNotIn("BASE_GATES", browser_source)


if __name__ == "__main__":
    unittest.main()
