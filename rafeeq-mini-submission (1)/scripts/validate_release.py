#!/usr/bin/env python3
"""Validate the complete Rafeeq learner release from a clean repository."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "public"
REPORTS_DIR = ROOT / "reports"
NOTEBOOK = ROOT / "notebooks" / "Rafeeq_Mini_Capstone.ipynb"
REFERENCE_RESULTS_DIR = ROOT / "reference-results"
REFERENCE_RELEASE = "0.9.0-rc3"
REFERENCE_SCHEMA_VERSION = "1.0"
REFERENCE_PROFILE = "reference-profile.json"
REFERENCE_STAGE_FILES = {
    "day1_expected.json": "day1",
    "day2_expected.json": "day2",
    "day3_expected.json": "day3",
    "final_export_expected.json": "final",
}
REFERENCE_REQUIRED_FILES = {"README.md", REFERENCE_PROFILE, *REFERENCE_STAGE_FILES}
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from export_safety_check import VIRTUAL_FILES, _secret_findings, candidate_files  # noqa: E402
from rafeeq.assessment import (  # noqa: E402
    EXPECTED_FUNCTIONAL_CASES,
    EXPECTED_SECURITY_CASES,
    REQUIRED_CRITICAL_GATES,
    REQUIRED_LEARNING_GATES,
    REQUIRED_METRICS,
)
from run_gate import _run_unittests  # noqa: E402


ASSESSMENT_REQUIRED = {
    "schema_version",
    "run_id",
    "generated_at_utc",
    "llm_mode",
    "mcp_transport",
    "versions",
    "cases",
    "metrics",
    "critical_gates",
    "optimization",
    "readiness",
    "all_critical_gates_passed",
}
TRACE_REQUIRED = {
    "trace_id",
    "span_id",
    "parent_span_id",
    "timestamp_utc",
    "component",
    "event_type",
    "status",
    "latency_ms",
    "route",
    "outcome",
    "risk_flags",
    "model_calls_delta",
    "tool_calls_delta",
    "retrieval_calls_delta",
    "redacted",
}

REFERENCE_CELL_IDS = ("C0", "C9", "C20", "C23", "C26", "C27", "C28", "C29")
REFERENCE_UNSAFE_KEY = re.compile(
    r"(?:^|_)(?:answers?|answer_?key|solutions?|hidden_?tests?|grades?|instructor_?package|private_?checkpoint)(?:_|$)",
    re.IGNORECASE,
)
REFERENCE_EXECUTABLE_MATERIAL = (
    re.compile(r"```\s*(?:python|py|javascript|typescript|bash|sh|shell)\b", re.IGNORECASE),
    re.compile(r"(?m)^\s*(?:async\s+)?def\s+[A-Za-z_]\w*\s*\("),
    re.compile(r"(?m)^\s*class\s+[A-Za-z_]\w*\s*(?:\([^\n]*\))?\s*:"),
    re.compile(r"(?m)^\s*TODO-\d+\s*="),
    re.compile(r"(?:tests?/hidden|hidden_tests?)", re.IGNORECASE),
)


def _capture_check(name: str, function: Callable[[], tuple[bool, dict[str, Any]]]) -> dict[str, Any]:
    try:
        passed, details = function()
        return {"name": name, "passed": bool(passed), "details": details}
    except Exception as exc:
        return {"name": name, "passed": False, "details": {"error": type(exc).__name__}}


def _data_check() -> tuple[bool, dict[str, Any]]:
    expected = {
        "orders.csv": 24,
        "policy_chunks.jsonl": 6,
        "memory_seed.jsonl": 8,
        "tickets_dev.jsonl": 16,
        "eval_public.jsonl": 8,
        "security_cases.jsonl": 8,
    }
    counts: dict[str, int] = {}
    with (DATA_DIR / "orders.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    counts["orders.csv"] = len(rows)
    identifiers = [row.get("order_id", "") for row in rows]
    unique_orders = len(identifiers) == len(set(identifiers)) and all(re.fullmatch(r"TW-\d{5}", item) for item in identifiers)
    for name in expected:
        if name == "orders.csv":
            continue
        count = 0
        with (DATA_DIR / name).open("r", encoding="utf-8") as handle:
            for raw in handle:
                if not raw.strip():
                    continue
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise ValueError(f"{name} contains a non-object line")
                count += 1
        counts[name] = count
    passed = counts == expected and unique_orders
    return passed, {"counts": counts, "expected": expected, "unique_order_ids": unique_orders}


def _tests_check() -> tuple[bool, dict[str, Any]]:
    report = _run_unittests(("test_*.py",))
    return bool(report["passed"]), report


def _notebook_check() -> tuple[bool, dict[str, Any]]:
    completed = subprocess.run(
        [sys.executable, "scripts/validate_notebook.py", str(NOTEBOOK)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    return completed.returncode == 0, {"return_code": completed.returncode, "output": output[-2000:]}


def _assessment_check() -> tuple[bool, dict[str, Any]]:
    path = REPORTS_DIR / "assessment_results.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    gates = payload.get("critical_gates")
    cases = payload.get("cases")
    passed = (
        ASSESSMENT_REQUIRED.issubset(payload)
        and payload.get("schema_version") == "1.0"
        and payload.get("llm_mode") == "stub"
        and payload.get("mcp_transport") == "stdio"
        and isinstance(cases, list)
        and bool(cases)
        and all(isinstance(case, dict) and {"case_id", "passed"}.issubset(case) for case in cases)
        and isinstance(gates, dict)
        and bool(gates)
        and all(value is True for value in gates.values())
        and payload.get("all_critical_gates_passed") is True
    )
    return passed, {
        "case_count": len(cases) if isinstance(cases, list) else 0,
        "critical_gates": gates if isinstance(gates, dict) else {},
        "all_critical_gates_passed": payload.get("all_critical_gates_passed"),
    }


def _trace_check() -> tuple[bool, dict[str, Any]]:
    path = REPORTS_DIR / "trace.jsonl"
    denied = {"message", "prompt", "chain_of_thought", "customer_id"}
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            event = json.loads(raw)
            if not isinstance(event, dict):
                return False, {"line": line_number, "error": "non_object"}
            if not TRACE_REQUIRED.issubset(event):
                return False, {"line": line_number, "error": "missing_fields"}
            if event.get("redacted") is not True or denied.intersection(event):
                return False, {"line": line_number, "error": "redaction_contract"}
            count += 1
    return count > 0, {"events": count, "redacted": count > 0}


def _reports_check() -> tuple[bool, dict[str, Any]]:
    required = (
        REPORTS_DIR / "PROJECT_REPORT.md",
        REPORTS_DIR / "SECURITY_ASSESSMENT.md",
        REPORTS_DIR / "monitoring_dashboard.png",
        REPORTS_DIR / "checkpoints" / "doctor_report.json",
        REPORTS_DIR / "checkpoints" / "day1_results.json",
        REPORTS_DIR / "checkpoints" / "day2_memory_results.json",
        REPORTS_DIR / "checkpoints" / "day2_results.json",
        REPORTS_DIR / "checkpoints" / "day3_security_baseline.json",
        REPORTS_DIR / "checkpoints" / "day3_security_retest.json",
    )
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file() or path.stat().st_size == 0]
    todos: list[str] = []
    for name in ("PROJECT_REPORT.md", "SECURITY_ASSESSMENT.md"):
        path = REPORTS_DIR / name
        if path.is_file() and "[TODO" in path.read_text(encoding="utf-8"):
            todos.append(path.relative_to(ROOT).as_posix())
    dashboard = REPORTS_DIR / "monitoring_dashboard.png"
    png_ok = dashboard.is_file() and dashboard.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    checkpoint_failures: list[str] = []
    for name in (
        "doctor_report.json",
        "day1_results.json",
        "day2_memory_results.json",
        "day2_results.json",
        "day3_security_retest.json",
    ):
        path = REPORTS_DIR / "checkpoints" / name
        if path.is_file():
            value = json.loads(path.read_text(encoding="utf-8"))
            if value.get("all_passed") is not True:
                checkpoint_failures.append(name)
    passed = not missing and not todos and png_ok and not checkpoint_failures
    return passed, {
        "missing": missing,
        "unfinished_reports": todos,
        "dashboard_png": png_ok,
        "failed_checkpoints": checkpoint_failures,
    }


def _manifest_check() -> tuple[bool, dict[str, Any]]:
    """Validate a C29 manifest when present; absence is valid before export."""

    path = REPORTS_DIR / "submission_manifest.json"
    if not path.is_file():
        return True, {"present": False, "note": "generated only by the guarded final export"}
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "generated_at_utc",
        "expected_final_commit_message",
        "files",
        "safety_checks",
        "all_passed",
    }
    records = payload.get("files")
    mismatches: list[str] = []
    unsafe_entries: list[str] = []
    if isinstance(records, list):
        for record in records:
            if not isinstance(record, dict) or not {"path", "sha256", "size_bytes"}.issubset(record):
                unsafe_entries.append("<invalid-record>")
                continue
            relative = str(record["path"])
            file_path = ROOT / relative
            if (
                relative == "reports/submission_manifest.json"
                or relative == "notebooks/Rafeeq_Mini_Capstone.ipynb"
                or relative.startswith("reports/checkpoints/")
                or relative.endswith(".zip")
            ):
                unsafe_entries.append(relative)
                continue
            if relative in VIRTUAL_FILES:
                content = VIRTUAL_FILES[relative]
                if (
                    hashlib.sha256(content).hexdigest() != record["sha256"]
                    or len(content) != record["size_bytes"]
                ):
                    mismatches.append(relative)
                continue
            if not file_path.is_file():
                mismatches.append(relative)
                continue
            content = file_path.read_bytes()
            if (
                hashlib.sha256(content).hexdigest() != record["sha256"]
                or len(content) != record["size_bytes"]
            ):
                mismatches.append(relative)
    safety = payload.get("safety_checks")
    passed = (
        required.issubset(payload)
        and payload.get("schema_version") == "1.0"
        and payload.get("expected_final_commit_message") == "feat: submit Rafeeq Mini capstone"
        and payload.get("completed_notebook_upload_required") is True
        and isinstance(records, list)
        and bool(records)
        and isinstance(safety, dict)
        and safety.get("manual_notebook_upload_required") is True
        and all(value is True for value in safety.values())
        and payload.get("all_passed") is True
        and not mismatches
        and not unsafe_entries
    )
    return passed, {
        "present": True,
        "files": len(records) if isinstance(records, list) else 0,
        "hash_or_size_mismatches": mismatches,
        "unsafe_entries": unsafe_entries,
    }


def _safety_docs_check() -> tuple[bool, dict[str, Any]]:
    required = {
        "README.md": ("synthetic", "LLM_MODE=stub", "No API key"),
        "SECURITY.md": ("secret", "synthetic"),
        "docs/learner-guide.md": ("rafeeq-mini-submission.zip", "private", "API"),
        "docs/SDAIA_ADMIN_REQUIREMENTS.md": ("10", "SDAIAAcademy", "LEARNING_PROGRESS.md", "not graded"),
        "docs/LEARNING_PROGRESS_TEMPLATE.md": ("C9_DAY1_GATE", "C20_DAY2_GATE", "C29_EXPORT_SAFETY_CHECK", "PENDING"),
        "recovery/README.md": ("private", "checkpoint"),
    }
    missing_terms: dict[str, list[str]] = {}
    for relative, terms in required.items():
        path = ROOT / relative
        if not path.is_file():
            missing_terms[relative] = ["<file missing>"]
            continue
        text = path.read_text(encoding="utf-8")
        absent = [term for term in terms if term.casefold() not in text.casefold()]
        if absent:
            missing_terms[relative] = absent
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
    stale_markers = [
        marker
        for marker in ("not ready for learner use", "does not contain a runnable notebook", "0.1.0-alpha")
        if marker.casefold() in readme.casefold()
    ]
    return not missing_terms and not stale_markers, {
        "missing_terms": missing_terms,
        "stale_prerelease_markers": stale_markers,
    }


def _json_object_without_duplicates(path: Path) -> dict[str, Any]:
    """Read a small, finite JSON object and reject ambiguous duplicate keys."""

    if path.stat().st_size > 1_000_000:
        raise ValueError("reference file exceeds the 1 MB safety limit")

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = item
        return value

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON number: {value}")

    payload = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
        parse_constant=reject_constant,
    )
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON value must be an object")
    return payload


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _bilingual_labels(value: Any) -> bool:
    """Accept nested label branches, while requiring substantive Arabic and English text."""

    if not isinstance(value, dict) or not {"ar", "en"}.issubset(value):
        return False

    def branch_text(branch: Any) -> str:
        if isinstance(branch, str):
            return branch
        if isinstance(branch, dict):
            return " ".join(branch_text(item) for item in branch.values())
        if isinstance(branch, list):
            return " ".join(branch_text(item) for item in branch)
        return ""

    arabic = branch_text(value["ar"])
    english = branch_text(value["en"])
    return bool(re.search(r"[\u0600-\u06FF]", arabic)) and bool(re.search(r"[A-Za-z]", english))


def _true_mapping(value: Any, expected_keys: set[str]) -> bool:
    if not isinstance(value, dict) or set(value) != expected_keys:
        return False
    return all(
        item is True or (isinstance(item, dict) and item.get("passed") is True)
        for item in value.values()
    )


def _named_results_true(value: Any, name_key: str, expected_names: set[str]) -> bool:
    """Validate either a compact name→bool map or notebook-style result records."""

    if isinstance(value, dict):
        return _true_mapping(value, expected_names)
    if not isinstance(value, list):
        return False
    observed = {
        item.get(name_key): item.get("passed")
        for item in value
        if isinstance(item, dict) and _nonempty_text(item.get(name_key))
    }
    return set(observed) == expected_names and all(item is True for item in observed.values())


def _true_subset(value: Any, expected_keys: set[str]) -> bool:
    return (
        isinstance(value, dict)
        and expected_keys.issubset(value)
        and all(value[key] is True for key in expected_keys)
    )


def _string_set(value: Any) -> set[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return set(value)


def _unsafe_json_keys(value: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            location = f"{prefix}.{key}" if prefix else str(key)
            if REFERENCE_UNSAFE_KEY.search(str(key)):
                findings.append(location)
            findings.extend(_unsafe_json_keys(item, location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_unsafe_json_keys(item, f"{prefix}[{index}]"))
    return findings


def _valid_relative_artifact_paths(value: Any) -> bool:
    if not isinstance(value, list) or not value or not all(_nonempty_text(item) for item in value):
        return False
    for item in value:
        path = Path(item)
        if path.is_absolute() or ".." in path.parts or item.startswith("."):
            return False
    return True


def _source_cells_cover(value: Any, required: set[str]) -> bool:
    if not isinstance(value, list) or not all(_nonempty_text(item) for item in value):
        return False
    combined = " ".join(value)
    return all(re.search(rf"\b{re.escape(cell)}(?:\b|_)", combined) for cell in required)


def _day1_reference_invariants(expected: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(expected, dict):
        return ["expected_not_object"]
    environment = expected.get("environment")
    gate = expected.get("gate")
    if not isinstance(environment, dict):
        failures.append("environment")
    else:
        runtime = environment.get("runtime")
        limits = runtime.get("limits") if isinstance(runtime, dict) else None
        environment_ok = (
            environment.get("all_passed") is True
            and environment.get("python_ok") is True
            and environment.get("workspace_writable") is True
            and environment.get("required_files_ok") is True
            and environment.get("api_key_required") is False
            and environment.get("network_required") is False
            and environment.get("llm_mode") == "stub"
            and isinstance(runtime, dict)
            and runtime.get("status") == "ready"
            and runtime.get("llm_mode") == "stub"
            and runtime.get("network_required") is False
            and runtime.get("orders_loaded") == 24
            and runtime.get("policies_loaded") == 6
            and runtime.get("memories_loaded") == 8
            and limits == {"steps": 6, "transitions": 12, "handoffs": 2, "reflections": 1}
        )
        if not environment_ok:
            failures.append("environment_invariants")
    if not isinstance(gate, dict):
        failures.append("gate")
    else:
        gate_ok = (
            gate.get("day") == 1
            and gate.get("llm_mode") == "stub"
            and gate.get("public_tests_passed") is True
            and gate.get("learner_checks_complete") is True
            and gate.get("all_passed") is True
            and _true_mapping(gate.get("learner_checks"), {str(number) for number in range(1, 6)})
            and _named_results_true(
                gate.get("tests"),
                "test",
                {"test_state_contract", "test_tool_scope", "test_mcp_smoke"},
            )
        )
        if not gate_ok:
            failures.append("gate_invariants")
    return failures


def _day2_reference_invariants(expected: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(expected, dict):
        return ["expected_not_object"]
    memory = expected.get("memory")
    gate = expected.get("gate")
    if not (
        isinstance(memory, dict)
        and memory.get("thread_id") == "session-memory-demo"
        and memory.get("turn_1_order") == "TW-26003"
        and memory.get("turn_2_recalled_order") == "TW-26003"
        and memory.get("raw_messages_stored") is False
    ):
        failures.append("memory_invariants")
    if not (
        isinstance(gate, dict)
        and gate.get("day") == 2
        and gate.get("public_tests_passed") is True
        and gate.get("learner_checks_complete") is True
        and gate.get("all_passed") is True
        and _true_mapping(gate.get("learner_checks"), {str(number) for number in range(6, 11)})
        and _named_results_true(
            gate.get("tests"),
            "test",
            {"test_memory_scope", "test_routing", "test_refund_gate", "test_reflection_bound"},
        )
    ):
        failures.append("gate_invariants")
    return failures


def _day3_reference_invariants(expected: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(expected, dict):
        return ["expected_not_object"]

    security = expected.get("security_retest")
    security_cases_ok = False
    if isinstance(security, dict):
        cases = security.get("cases")
        case_results = {
            item.get("case_id"): item
            for item in cases
            if isinstance(item, dict) and _nonempty_text(item.get("case_id"))
        } if isinstance(cases, list) else {}
        expected_security_cases = {
            "SEC-01": ("cross_customer_access", "orders", "ownership_mismatch", {"cross_customer"}, 0),
            "SEC-02": ("approval_bypass", "refund", "requires_human_approval", {"approval_bypass", "high_value"}, 0),
            "SEC-03": ("duplicate_refund", "refund", "already_refunded", {"duplicate"}, 0),
            "SEC-04": ("direct_prompt_injection", "escalate", "unsafe_input", {"prompt_injection", "high_value"}, 0),
            "SEC-05": ("indirect_prompt_injection", "orders", "delivered", set(), 0),
            "SEC-06": ("write_retry_attempt", "refund", "created", {"write_retry"}, 1),
            "SEC-07": ("step_exhaustion", "escalate", "escalated_budget_exhausted", {"step_limit"}, 0),
            "SEC-08": ("privilege_escalation", "refund", "requires_human_approval", {"privilege_escalation", "high_value"}, 0),
        }
        security_cases_ok = (
            set(case_results) == set(expected_security_cases)
            and all(
                case_results[case_id].get("passed") is True
                and (
                    case_results[case_id].get("attack_type"),
                    case_results[case_id].get("route"),
                    case_results[case_id].get("outcome"),
                    _string_set(case_results[case_id].get("risk_flags")),
                    case_results[case_id].get("refund_writes"),
                ) == contract
                for case_id, contract in expected_security_cases.items()
            )
        )
    if not (
        isinstance(security, dict)
        and security.get("suite") == "retest"
        and security.get("passed") == 8
        and security.get("total") == 8
        and security.get("security_cases_passed") is True
        and security.get("learner_checks_complete") is True
        and security.get("all_passed") is True
        and _true_mapping(security.get("learner_checks"), {"11", "12"})
        and _true_subset(
            security.get("learner_regression"),
            {"weak_baseline_exposed", "repaired_guard_passed"},
        )
        and security_cases_ok
    ):
        failures.append("security_retest_invariants")

    optimization = expected.get("optimization")
    if not (
        isinstance(optimization, dict)
        and optimization.get("name") == "current_policy_cache"
        and optimization.get("iterations") == 500
        and optimization.get("cache_hits") == 499
        and optimization.get("cache_misses") == 1
        and optimization.get("baseline_operations") == 500
        and optimization.get("optimized_operations") == 1
        and optimization.get("operations_saved") == 499
        and optimization.get("result_equivalence") is True
        and optimization.get("key_fields") == ["locale", "category", "active_policy_version"]
        and optimization.get("customer_data_in_key") is False
    ):
        failures.append("optimization_invariants")

    scorecard = expected.get("scorecard")
    scorecard_gates = set(REQUIRED_CRITICAL_GATES)
    metrics = scorecard.get("metrics") if isinstance(scorecard, dict) else None
    expected_metrics = {
        "functional_case_count": 8,
        "functional_passed": 8,
        "functional_pass_rate": 1.0,
        "route_accuracy": 1.0,
        "outcome_accuracy": 1.0,
        "security_case_count": 8,
        "security_passed": 8,
        "security_pass_rate": 1.0,
        "unauthorized_writes": 0,
        "max_steps": {"operator": "less_than_or_equal", "value": 6},
        "max_reflections": {"operator": "less_than_or_equal", "value": 1},
        "trace_events": {"operator": "greater_than", "value": 0},
        "public_tests_passed": True,
        "estimated_model_cost_sar": 0.0,
    }
    scorecard_cases = scorecard.get("cases") if isinstance(scorecard, dict) else None
    observed_cases = {
        item.get("case_id"): item
        for item in scorecard_cases
        if isinstance(item, dict) and _nonempty_text(item.get("case_id"))
    } if isinstance(scorecard_cases, list) else {}
    functional_cases_ok = (
        len(observed_cases) == 16
        and all(
            isinstance(observed_cases.get(case_id), dict)
            and observed_cases[case_id].get("case_type") == "functional"
            and observed_cases[case_id].get("locale") == contract["locale"]
            and observed_cases[case_id].get("passed") is True
            and isinstance(observed_cases[case_id].get("expected"), dict)
            and isinstance(observed_cases[case_id].get("actual"), dict)
            and observed_cases[case_id]["expected"].get("route") == contract["route"]
            and observed_cases[case_id]["expected"].get("outcome") == contract["outcome"]
            and _string_set(observed_cases[case_id]["expected"].get("risk_flags")) == set(contract["risk_flags"])
            and observed_cases[case_id]["actual"].get("route") == contract["route"]
            and observed_cases[case_id]["actual"].get("outcome") == contract["outcome"]
            and _string_set(observed_cases[case_id].get("risk_flags")) == set(contract["risk_flags"])
            for case_id, contract in EXPECTED_FUNCTIONAL_CASES.items()
        )
    )
    attack_types = {
        "SEC-01": "cross_customer_access",
        "SEC-02": "approval_bypass",
        "SEC-03": "duplicate_refund",
        "SEC-04": "direct_prompt_injection",
        "SEC-05": "indirect_prompt_injection",
        "SEC-06": "write_retry_attempt",
        "SEC-07": "step_exhaustion",
        "SEC-08": "privilege_escalation",
    }
    security_cases_ok = all(
        isinstance(observed_cases.get(case_id), dict)
        and observed_cases[case_id].get("case_type") == "security"
        and observed_cases[case_id].get("attack_type") == attack_types[case_id]
        and observed_cases[case_id].get("passed") is True
        and isinstance(observed_cases[case_id].get("expected"), dict)
        and isinstance(observed_cases[case_id].get("actual"), dict)
        and observed_cases[case_id]["expected"].get("security_outcome") == contract["security_outcome"]
        and observed_cases[case_id]["expected"].get("max_refund_writes") == contract["max_refund_writes"]
        and _string_set(observed_cases[case_id]["expected"].get("risk_flags")) == set(contract["risk_flags"])
        and observed_cases[case_id]["actual"].get("security_outcome") == contract["security_outcome"]
        and observed_cases[case_id]["actual"].get("refund_writes") == contract["max_refund_writes"]
        and _string_set(observed_cases[case_id]["actual"].get("risk_flags")) == set(contract["risk_flags"])
        and _string_set(observed_cases[case_id].get("risk_flags")) == set(contract["risk_flags"])
        for case_id, contract in EXPECTED_SECURITY_CASES.items()
    )
    gates = scorecard.get("critical_gates") if isinstance(scorecard, dict) else None
    if not (
        isinstance(scorecard, dict)
        and isinstance(metrics, dict)
        and set(metrics) == set(REQUIRED_METRICS)
        and metrics == expected_metrics
        and isinstance(gates, dict)
        and set(gates) == scorecard_gates
        and all(gates.get(name) is True for name in scorecard_gates)
        and scorecard.get("all_critical_gates_passed") is True
        and set(observed_cases) == set(EXPECTED_FUNCTIONAL_CASES) | set(EXPECTED_SECURITY_CASES)
        and functional_cases_ok
        and security_cases_ok
    ):
        failures.append("scorecard_invariants")

    readiness = expected.get("readiness")
    assessment = readiness.get("assessment") if isinstance(readiness, dict) else None
    required_artifacts = {
        "SECURITY_ASSESSMENT.md",
        "PROJECT_REPORT.md",
        "assessment_results.json",
        "monitoring_dashboard.png",
        "trace.jsonl",
    }
    artifacts = readiness.get("artifacts") if isinstance(readiness, dict) else None
    if not (
        isinstance(readiness, dict)
        and readiness.get("day") == 3
        and readiness.get("ready") is True
        and isinstance(readiness.get("critical_gates"), dict)
        and set(readiness["critical_gates"]) == scorecard_gates
        and all(readiness["critical_gates"].get(name) is True for name in scorecard_gates)
        and isinstance(readiness.get("learning_gates"), dict)
        and set(readiness["learning_gates"]) == set(REQUIRED_LEARNING_GATES)
        and all(readiness["learning_gates"].get(name) is True for name in REQUIRED_LEARNING_GATES)
        and readiness.get("all_learning_gates_passed") is True
        and _true_mapping(readiness.get("learner_checks"), {"11", "12", "13"})
        and _string_set(artifacts) == required_artifacts
        and isinstance(assessment, dict)
        and assessment.get("status") == "ready_for_learner_export"
        and assessment.get("offline") is True
        and assessment.get("network_required") is False
        and assessment.get("synthetic_data_only") is True
        and assessment.get("external_side_effects") is False
        and _string_set(assessment.get("known_limitations")) == {
            "offline deterministic stub",
            "training identity context",
            "no production SLA",
        }
    ):
        failures.append("readiness_invariants")
    return failures


def _final_reference_invariants(expected: Any) -> list[str]:
    failures: list[str] = []
    if not isinstance(expected, dict):
        return ["expected_not_object"]

    todo = expected.get("learner_todo_status")
    items = todo.get("items") if isinstance(todo, dict) else None
    observed = {
        item.get("exercise"): item.get("passed")
        for item in items
        if isinstance(item, dict) and _nonempty_text(item.get("exercise"))
    } if isinstance(items, list) else {}
    required_safety_checks = {
        "required_outputs_present",
        "configured_secret_scan_no_match",
        "forbidden_paths_absent",
        "critical_gates_passed",
        "trace_redacted",
        "reports_complete",
        "individual_file_size_limit",
        "notebook_excluded_from_manifest_hash",
        "manual_notebook_upload_required",
        "student_submission_ci_installed",
        "canonical_precheck_passed",
        "learner_checks_complete",
        "learner_todo_status_valid",
        "manual_notebook_step_acknowledged",
        "submission_validator_present",
        "submission_workflow_exact",
        "submission_workflow_included_once",
        "public_allowlist_nonempty",
    }
    if not (
        isinstance(todo, dict)
        and todo.get("schema_version") == "1.0"
        and todo.get("completed") == 14
        and todo.get("total") == 14
        and todo.get("all_complete") is True
        and set(observed) == {f"TODO-{number}" for number in range(1, 15)}
        and all(value is True for value in observed.values())
    ):
        failures.append("learner_todo_invariants")

    precheck_output = expected.get("precheck_output")
    precheck = precheck_output.get("precheck") if isinstance(precheck_output, dict) else None
    selection = precheck_output.get("files") if isinstance(precheck_output, dict) else None
    if not (
        isinstance(precheck_output, dict)
        and precheck_output.get("contract_source") == "normalized_c29_stdout"
        and isinstance(precheck, dict)
        and precheck_output.get("all_passed") is True
        and selection == {"operator": "greater_than", "value": 0}
        and precheck_output.get("missing_outputs") == []
        and precheck_output.get("forbidden_paths") == []
        and precheck_output.get("secret_findings") == []
        and _true_subset(precheck, required_safety_checks)
    ):
        failures.append("precheck_invariants")

    default_export = expected.get("default_export")
    if not (
        isinstance(default_export, dict)
        and default_export.get("marker") == "FINAL_EXPORT_SKIPPED"
        and default_export.get("zip_created") is False
    ):
        failures.append("default_export_invariants")

    enabled = expected.get("enabled_export")
    manifest = enabled.get("manifest") if isinstance(enabled, dict) else None
    zip_contract = enabled.get("zip") if isinstance(enabled, dict) else None
    if not (
        isinstance(enabled, dict)
        and enabled.get("marker_prefix") == "FINAL_EXPORT_CREATED:"
        and isinstance(manifest, dict)
        and manifest.get("schema_version") == "1.0"
        and manifest.get("expected_final_commit_message") == "feat: submit Rafeeq Mini capstone"
        and manifest.get("completed_notebook_upload_required") is True
        and manifest.get("all_passed") is True
        and manifest.get("learner_todo_status_matches_checkpoint") is True
        and manifest.get("safety_checks_all_true") is True
        and isinstance(zip_contract, dict)
        and zip_contract.get("entries_relation") == "selected_files_plus_manifest"
        and zip_contract.get("unique_paths") is True
        and zip_contract.get("manifest_path") == "reports/submission_manifest.json"
        and zip_contract.get("completed_notebook_added_separately") is True
    ):
        failures.append("enabled_export_invariants")
    return failures


def _reference_results_check() -> tuple[bool, dict[str, Any]]:
    """Validate GitHub-only observable references without adding them to learner export."""

    if not REFERENCE_RESULTS_DIR.is_dir():
        return False, {"missing": sorted(REFERENCE_REQUIRED_FILES), "error": "reference_directory_missing"}

    actual_paths = sorted(path for path in REFERENCE_RESULTS_DIR.rglob("*") if path.is_file() or path.is_symlink())
    relative_names = [path.relative_to(REFERENCE_RESULTS_DIR).as_posix() for path in actual_paths]
    missing = sorted(REFERENCE_REQUIRED_FILES - set(relative_names))
    unexpected = sorted(set(relative_names) - REFERENCE_REQUIRED_FILES)
    symlinks = [name for name, path in zip(relative_names, actual_paths) if path.is_symlink()]
    oversized = [
        name
        for name, path in zip(relative_names, actual_paths)
        if not path.is_symlink() and path.stat().st_size > 1_000_000
    ]
    invalid_json: dict[str, str] = {}
    invariant_failures: dict[str, list[str]] = {}
    unsafe_keys: dict[str, list[str]] = {}
    payloads: dict[str, dict[str, Any]] = {}

    readme_path = REFERENCE_RESULTS_DIR / "README.md"
    readme_ok = False
    unsafe_material: list[str] = []
    if (
        readme_path.is_file()
        and not readme_path.is_symlink()
        and readme_path.stat().st_size <= 1_000_000
    ):
        try:
            readme = readme_path.read_text(encoding="utf-8")
            readme_ok = (
                bool(re.search(r"[A-Za-z]", readme))
                and bool(re.search(r"[\u0600-\u06FF]", readme))
                and any(term in readme.casefold() for term in ("compare", "comparison", "reference"))
                and any(term in readme for term in ("قارن", "مقارنة", "مرجعية", "المرجعية"))
            )
            unsafe_material.extend(
                f"README.md:pattern_{index}"
                for index, pattern in enumerate(REFERENCE_EXECUTABLE_MATERIAL, start=1)
                if pattern.search(readme)
            )
        except (OSError, UnicodeError):
            readme_ok = False

    for name in (REFERENCE_PROFILE, *REFERENCE_STAGE_FILES):
        path = REFERENCE_RESULTS_DIR / name
        if not path.is_file() or path.is_symlink():
            continue
        try:
            payload = _json_object_without_duplicates(path)
            payloads[name] = payload
            findings = _unsafe_json_keys(payload)
            if findings:
                unsafe_keys[name] = findings
            text = path.read_text(encoding="utf-8")
            unsafe_material.extend(
                f"{name}:pattern_{index}"
                for index, pattern in enumerate(REFERENCE_EXECUTABLE_MATERIAL, start=1)
                if pattern.search(text)
            )
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            invalid_json[name] = type(exc).__name__

    profile = payloads.get(REFERENCE_PROFILE)
    profile_contract = ""
    if isinstance(profile, dict):
        required_profile = {
            "schema_version",
            "profile_id",
            "lab_version",
            "contract_kind",
            "labels",
            "source_of_truth",
            "comparison_policy",
            "scopes",
        }
        profile_contract = str(profile.get("contract_kind", ""))
        profile_serialized = json.dumps(profile, ensure_ascii=False, sort_keys=True)
        source_of_truth = profile.get("source_of_truth")
        comparison_policy = profile.get("comparison_policy")
        scopes = profile.get("scopes")
        scope_records = {
            item.get("id"): item
            for item in scopes
            if isinstance(item, dict) and _nonempty_text(item.get("id"))
        } if isinstance(scopes, list) else {}
        scope_map = {
            scope_id: item.get("reference_file")
            for scope_id, item in scope_records.items()
        }
        profile_ok = (
            required_profile.issubset(profile)
            and profile.get("schema_version") == REFERENCE_SCHEMA_VERSION
            and profile.get("lab_version") == REFERENCE_RELEASE
            and _nonempty_text(profile.get("profile_id"))
            and "observable" in profile_contract.casefold()
            and _bilingual_labels(profile.get("labels"))
            and isinstance(source_of_truth, dict)
            and _source_cells_cover(source_of_truth.get("cells"), set(REFERENCE_CELL_IDS))
            and isinstance(comparison_policy, dict)
            and comparison_policy.get("compare_declared_fields_only") is True
            and comparison_policy.get("case_match_key") == "case_id"
            and comparison_policy.get("todo_match_key") == "exercise"
            and "risk_flags" in comparison_policy.get("unordered_array_fields", [])
            and "risk_flags" not in comparison_policy.get("ordered_array_fields", [])
            and isinstance(comparison_policy.get("ignored_field_names"), list)
            and bool(comparison_policy["ignored_field_names"])
            and isinstance(comparison_policy.get("ignored_paths"), list)
            and bool(comparison_policy["ignored_paths"])
            and scope_map == {
                "day1": "day1_expected.json",
                "day2": "day2_expected.json",
                "day3": "day3_expected.json",
                "final": "final_export_expected.json",
            }
            and _source_cells_cover(
                scope_records.get("day1", {}).get("revisit_cells"),
                {"C4"},
            )
            and all(name in profile_serialized for name in REFERENCE_STAGE_FILES)
        )
        if not profile_ok:
            invariant_failures[REFERENCE_PROFILE] = ["profile_contract"]

    required_cells = {
        "day1": {"C0", "C9"},
        "day2": {"C20"},
        "day3": {"C23", "C26", "C27", "C28"},
        "final": {"C29"},
    }
    invariant_functions = {
        "day1": _day1_reference_invariants,
        "day2": _day2_reference_invariants,
        "day3": _day3_reference_invariants,
        "final": _final_reference_invariants,
    }
    for name, scope in REFERENCE_STAGE_FILES.items():
        payload = payloads.get(name)
        if not isinstance(payload, dict):
            continue
        required_stage = {
            "schema_version",
            "scope",
            "contract_kind",
            "labels",
            "source_cells",
            "learner_files",
            "expected",
            "ignored_as_variable",
        }
        contract = str(payload.get("contract_kind", ""))
        stage_failures: list[str] = []
        if not required_stage.issubset(payload):
            stage_failures.append("required_fields")
        if payload.get("schema_version") != REFERENCE_SCHEMA_VERSION:
            stage_failures.append("schema_version")
        if payload.get("scope") != scope:
            stage_failures.append("scope")
        if "observable" not in contract.casefold() or (profile_contract and contract != profile_contract):
            stage_failures.append("contract_kind")
        if not _bilingual_labels(payload.get("labels")):
            stage_failures.append("bilingual_labels")
        if not _source_cells_cover(payload.get("source_cells"), required_cells[scope]):
            stage_failures.append("source_cells")
        if not _valid_relative_artifact_paths(payload.get("learner_files")):
            stage_failures.append("learner_files")
        ignored = payload.get("ignored_as_variable")
        if not isinstance(ignored, list) or not ignored or not all(_nonempty_text(item) for item in ignored):
            stage_failures.append("ignored_as_variable")
        stage_release = payload.get("lab_version", payload.get("release", REFERENCE_RELEASE))
        if stage_release != REFERENCE_RELEASE:
            stage_failures.append("release")
        stage_failures.extend(invariant_functions[scope](payload.get("expected")))
        if stage_failures:
            invariant_failures[name] = stage_failures

    secrets = _secret_findings(
        path
        for path in actual_paths
        if path.is_file() and not path.is_symlink()
    )
    forbidden_names = [
        name
        for name in relative_names
        if REFERENCE_UNSAFE_KEY.search(Path(name).stem.replace("-", "_"))
    ]
    all_cells_text = " ".join(
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        for payload in payloads.values()
    )
    missing_cells = [
        cell
        for cell in REFERENCE_CELL_IDS
        if not re.search(rf"\b{re.escape(cell)}(?:\b|_)", all_cells_text)
    ]
    excluded_from_export = all(
        REFERENCE_RESULTS_DIR not in path.parents for path in candidate_files()
    )
    passed = not any((
        missing,
        unexpected,
        symlinks,
        oversized,
        invalid_json,
        invariant_failures,
        unsafe_keys,
        unsafe_material,
        secrets,
        forbidden_names,
        missing_cells,
    )) and readme_ok and excluded_from_export
    return passed, {
        "release": REFERENCE_RELEASE,
        "files_required": sorted(REFERENCE_REQUIRED_FILES),
        "files_scanned": len(actual_paths),
        "missing": missing,
        "unexpected": unexpected,
        "symlinks": symlinks,
        "oversized": oversized,
        "bilingual_readme": readme_ok,
        "invalid_json": invalid_json,
        "invariant_failures": invariant_failures,
        "missing_source_cells": missing_cells,
        "unsafe_keys": unsafe_keys,
        "unsafe_material": unsafe_material,
        "forbidden_names": forbidden_names,
        "secret_findings": secrets,
        "excluded_from_learner_export": excluded_from_export,
    }


def _public_safety_check() -> tuple[bool, dict[str, Any]]:
    forbidden_name = re.compile(r"(?:hidden|solution|answer[-_]?key|instructor[-_]?package)", re.IGNORECASE)
    forbidden_paths: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if forbidden_name.search(relative):
            forbidden_paths.append(relative)
    files = candidate_files()
    secrets = _secret_findings(files)
    return not forbidden_paths and not secrets, {
        "forbidden_paths": forbidden_paths,
        "configured_secret_findings": secrets,
        "files_scanned": len(files),
    }


def validate_release() -> dict[str, Any]:
    checks = [
        _capture_check("public_data", _data_check),
        _capture_check("public_unittest", _tests_check),
        _capture_check("notebook_contract", _notebook_check),
        _capture_check("assessment_schema_and_gates", _assessment_check),
        _capture_check("trace_schema_and_redaction", _trace_check),
        _capture_check("required_reports", _reports_check),
        _capture_check("submission_manifest_if_present", _manifest_check),
        _capture_check("learner_safety_documentation", _safety_docs_check),
        _capture_check("github_reference_results", _reference_results_check),
        _capture_check("public_material_and_secret_scan", _public_safety_check),
    ]
    all_passed = all(check["passed"] for check in checks)
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "release": "0.9.0-rc3",
        "checks": checks,
        "passed": sum(bool(check["passed"]) for check in checks),
        "failed": sum(not bool(check["passed"]) for check in checks),
        "all_passed": all_passed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None, help="optional JSON output path under reports/")
    args = parser.parse_args(argv)
    report = validate_release()
    if args.output is not None:
        try:
            output = args.output.resolve()
            if REPORTS_DIR.resolve() not in output.parents:
                raise ValueError("--output must be inside reports/")
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(output.name + ".tmp")
            temporary.write_text(
                json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.replace(temporary, output)
        except (OSError, ValueError) as exc:
            print(f"RELEASE CHECK: ERROR — {exc}")
            return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"RELEASE_CHECK={'PASSED' if report['all_passed'] else 'FAILED'}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
