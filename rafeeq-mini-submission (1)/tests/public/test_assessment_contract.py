"""Public checks for the canonical, non-self-asserted assessment contract."""

from __future__ import annotations

from copy import deepcopy
import unittest

import _support  # noqa: F401 -- installs the local src path

from rafeeq.assessment import (
    EXPECTED_FUNCTIONAL_CASES,
    EXPECTED_SECURITY_CASES,
    REQUIRED_CRITICAL_GATES,
    validate_assessment_payload,
)


def valid_payload() -> dict:
    cases = []
    for case_id, contract in EXPECTED_FUNCTIONAL_CASES.items():
        cases.append(
            {
                "case_id": case_id,
                "case_type": "functional",
                "locale": contract["locale"],
                "passed": True,
                "expected": {
                    "route": contract["route"],
                    "outcome": contract["outcome"],
                    "risk_flags": list(contract["risk_flags"]),
                },
                "actual": {
                    "route": contract["route"],
                    "outcome": contract["outcome"],
                    "status": "completed",
                    "steps": 2,
                    "reflections": 0,
                },
                "risk_flags": list(contract["risk_flags"]),
                "latency_ms": 1.0,
            }
        )
    for case_id, contract in EXPECTED_SECURITY_CASES.items():
        cases.append(
            {
                "case_id": case_id,
                "case_type": "security",
                "passed": True,
                "expected": {
                    "security_outcome": contract["security_outcome"],
                    "risk_flags": list(contract["risk_flags"]),
                    "max_refund_writes": contract["max_refund_writes"],
                },
                "actual": {
                    "security_outcome": contract["security_outcome"],
                    "status": "completed",
                    "risk_flags": list(contract["risk_flags"]),
                    "refund_writes": contract["max_refund_writes"],
                    "steps": 3,
                    "reflections": 1,
                },
                "risk_flags": list(contract["risk_flags"]),
                "latency_ms": 1.0,
            }
        )
    return {
        "schema_version": "1.0",
        "run_id": "run-1234567890abcdef",
        "generated_at_utc": "2026-09-18T00:00:00+00:00",
        "llm_mode": "stub",
        "mcp_transport": "stdio",
        "versions": {"course": "test"},
        "cases": cases,
        "metrics": {
            "functional_case_count": 8,
            "functional_passed": 8,
            "functional_pass_rate": 1.0,
            "route_accuracy": 1.0,
            "outcome_accuracy": 1.0,
            "security_case_count": 8,
            "security_passed": 8,
            "security_pass_rate": 1.0,
            "unauthorized_writes": 0,
            "max_steps": 3,
            "max_reflections": 1,
            "trace_events": 16,
            "public_tests_passed": True,
            "estimated_model_cost_sar": 0.0,
        },
        "critical_gates": {name: True for name in REQUIRED_CRITICAL_GATES},
        "learning_gates": {
            "day1_gate": True,
            "day2_gate": True,
            "learner_exercises_1_to_13": True,
        },
        "all_learning_gates_passed": True,
        "optimization": {
            "name": "current_policy_cache",
            "key_fields": ["locale", "category", "active_policy_version"],
            "customer_data_in_key": False,
            "baseline_operations": 500,
            "optimized_operations": 1,
            "operations_saved": 499,
            "result_equivalence": True,
        },
        "readiness": {
            "status": "ready_for_learner_export",
            "offline": True,
            "network_required": False,
            "synthetic_data_only": True,
            "external_side_effects": False,
        },
        "all_critical_gates_passed": True,
    }


class AssessmentContractTests(unittest.TestCase):
    def test_named_cases_metrics_and_gates_are_accepted(self) -> None:
        passed, errors = validate_assessment_payload(valid_payload(), require_learning_gates=True)
        self.assertTrue(passed, errors)

    def test_extra_risk_flag_is_not_accepted_as_subset_match(self) -> None:
        payload = valid_payload()
        payload["cases"][0]["risk_flags"].append("invented_flag")
        passed, errors = validate_assessment_payload(payload, require_learning_gates=True)
        self.assertFalse(passed)
        self.assertTrue(any("EVAL-AR-01" in error for error in errors), errors)

    def test_arbitrary_true_gate_cannot_replace_required_gate(self) -> None:
        payload = valid_payload()
        del payload["critical_gates"]["cross_customer_leakage_zero"]
        payload["critical_gates"]["looks_good"] = True
        passed, errors = validate_assessment_payload(payload, require_learning_gates=True)
        self.assertFalse(passed)
        self.assertTrue(any("missing required critical gates" in error for error in errors), errors)

    def test_case_metric_tampering_is_detected(self) -> None:
        payload = deepcopy(valid_payload())
        payload["metrics"]["security_case_count"] = 999
        passed, errors = validate_assessment_payload(payload, require_learning_gates=True)
        self.assertFalse(passed)
        self.assertTrue(any("security_case_count" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
