#!/usr/bin/env python3
"""Validate a completed Rafeeq learner repository without executing its code.

The optional positional argument lets an instructor run this trusted copy
against a cloned learner repository.  With ``--write-receipt``, a successful
validation writes a cryptographic receipt that binds the uploaded notebook,
export manifest and canonical assessment without creating a circular manifest
hash.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


VALIDATOR_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = VALIDATOR_ROOT / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from rafeeq.assessment import validate_assessment_payload  # noqa: E402


NOTEBOOK_RELATIVE = "notebooks/Rafeeq_Mini_Capstone.ipynb"
MANIFEST_RELATIVE = "reports/submission_manifest.json"
ASSESSMENT_RELATIVE = "reports/assessment_results.json"
RECEIPT_RELATIVE = "reports/submission_receipt.json"
EXPECTED_COMMIT_MESSAGE = "feat: submit Rafeeq Mini capstone"

EXPECTED_SECTIONS = (
    "C0_ENV_DOCTOR",
    "C1_ARCHITECTURE",
    "C2_TYPED_STATE",
    "C3_BOUNDED_GRAPH",
    "C4_REASONING_TRACES",
    "C5_REACT_ORDERS",
    "C6_TOOL_SCHEMA",
    "C7_MCP_SERVER",
    "C8_MCP_CLIENT",
    "C9_DAY1_GATE",
    "C10_RESTORE",
    "C11_SESSION_MEMORY",
    "C12_SCOPED_RECALL",
    "C13_POLICY_RETRIEVAL",
    "C14_SPECIALISTS",
    "C15_SUPERVISOR",
    "C16_TYPED_HANDOFF",
    "C17_PLAN_EXECUTE",
    "C18_REFUND_GATE",
    "C19_INTERRUPT_RESUME",
    "C20_DAY2_GATE",
    "C21_THREAT_MODEL",
    "C22_ATTACK_SUITE",
    "C23_GUARD_FIX_RETEST",
    "C24_REFLECTION_GATE",
    "C25_TRACE_EVAL",
    "C26_ONE_OPTIMIZATION",
    "C27_SCORECARD",
    "C28_READINESS",
    "C29_EXPORT_SAFETY_CHECK",
)
FINAL_OUTPUTS = (
    "reports/PROJECT_REPORT.md",
    "reports/SECURITY_ASSESSMENT.md",
    "reports/trace.jsonl",
    ASSESSMENT_RELATIVE,
    "reports/monitoring_dashboard.png",
    MANIFEST_RELATIVE,
)
REQUIRED_HASHED_FILES = {
    "COURSE_USE_PERMISSION.md",
    ".github/workflows/learner-submission-quality.yml",
    *(set(FINAL_OUTPUTS) - {MANIFEST_RELATIVE}),
}
REQUIRED_MANIFEST_SAFETY = {
    "required_outputs_present",
    "configured_secret_scan_no_match",
    "forbidden_paths_absent",
    "critical_gates_passed",
    "trace_redacted",
    "reports_complete",
    "individual_file_size_limit",
    "notebook_excluded_from_manifest_hash",
    "manual_notebook_upload_required",
    "notebook_bound_by_submission_receipt",
    "submission_receipt_required",
    "student_submission_ci_installed",
    "learner_todos_14_of_14",
}
SECRET_PATTERNS = (
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{24,}\b", re.IGNORECASE)),
)
TEXT_SUFFIXES = {
    ".py", ".md", ".json", ".jsonl", ".csv", ".txt", ".yml",
    ".yaml", ".html", ".js", ".css", ".ipynb",
}
FAILURE_HELP = {
    "completed_notebook_structure": "Download the executed Colab notebook after C29 succeeds, then upload it at the exact required path.",
    "learner_todos_14_of_14": "Complete all 14 TODO exercises and rerun the daily gates plus C28/C29.",
    "six_final_outputs": "Rerun C28 and C29, extract the export ZIP, and upload every required report.",
    "assessment_critical_gates": "Rerun C27 and C28; do not edit assessment_results.json manually.",
    "trace_redaction": "Rerun the clean assessment and ensure no raw prompt, customer ID, or chain-of-thought enters trace.jsonl.",
    "submission_manifest": "Create a new C29 export after the final assessment; do not mix files from different runs.",
    "configured_secret_scan": "Remove credentials, private material, symlinks, and the generated ZIP before pushing.",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def _output_text(cell: dict[str, Any]) -> str:
    parts: list[str] = []
    outputs = cell.get("outputs")
    if not isinstance(outputs, list):
        return ""
    for output in outputs:
        if not isinstance(output, dict):
            continue
        text = output.get("text")
        if isinstance(text, list):
            parts.append("".join(str(item) for item in text))
        elif isinstance(text, str):
            parts.append(text)
        data = output.get("data")
        if isinstance(data, dict):
            for mime in ("text/plain", "text/html"):
                value = data.get(mime)
                if isinstance(value, list):
                    parts.append("".join(str(item) for item in value))
                elif isinstance(value, str):
                    parts.append(value)
    return "\n".join(parts)


def _notebook_check(
    root: Path,
    manifest: dict[str, Any],
    assessment: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    path = root / NOTEBOOK_RELATIVE
    errors: list[str] = []
    try:
        notebook = _read_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return False, {"errors": [f"cannot read notebook: {type(exc).__name__}"]}
    cells = notebook.get("cells") if isinstance(notebook, dict) else None
    if not isinstance(notebook, dict) or notebook.get("nbformat") != 4 or not isinstance(cells, list) or not cells:
        return False, {"errors": ["notebook must be a nonempty nbformat 4 document"]}

    combined = "\n".join(_source_text(cell) for cell in cells if isinstance(cell, dict))
    positions: list[int] = []
    missing_sections: list[str] = []
    duplicate_sections: list[str] = []
    for section in EXPECTED_SECTIONS:
        count = combined.count(section)
        if count == 0:
            missing_sections.append(section)
        elif count > 1:
            duplicate_sections.append(section)
        positions.append(combined.find(section))
    order_ok = not missing_sections and positions == sorted(positions)
    if missing_sections:
        errors.append("missing sections: " + ", ".join(missing_sections))
    if duplicate_sections:
        errors.append("duplicate section markers: " + ", ".join(duplicate_sections))
    if not order_ok:
        errors.append("the 30 section markers are not in canonical order")

    todo_counts = {
        f"TODO-{number}": len(re.findall(rf"TODO-{number}(?!\d)", combined))
        for number in range(1, 15)
    }
    bad_todos = {name: count for name, count in todo_counts.items() if count != 1}
    unexpected_todos = sorted(
        marker for marker in set(re.findall(r"TODO-(\d+)", combined))
        if int(marker) > 14
    )
    if bad_todos:
        errors.append("each TODO-1..TODO-14 marker must occur once: " + json.dumps(bad_todos, sort_keys=True))
    if unexpected_todos:
        errors.append("unexpected TODO markers: " + ", ".join(f"TODO-{item}" for item in unexpected_todos))

    export_cells = [
        cell for cell in cells
        if isinstance(cell, dict)
        and cell.get("cell_type") == "code"
        and "export" in (cell.get("metadata", {}).get("tags", []) if isinstance(cell.get("metadata"), dict) else [])
    ]
    if len(export_cells) != 1:
        errors.append("exactly one tagged C29 export code cell is required")
        export_source = ""
        export_output = ""
        execution_count: Any = None
    else:
        export_source = _source_text(export_cells[0])
        export_output = _output_text(export_cells[0])
        execution_count = export_cells[0].get("execution_count")
        if re.search(r"(?m)^\s*FINAL_EXPORT\s*=\s*True\b", export_source) is None:
            errors.append("C29 source must show FINAL_EXPORT = True")
        if not isinstance(execution_count, int) or isinstance(execution_count, bool):
            errors.append("C29 must have a saved execution count")
        if "FINAL_EXPORT_CREATED" not in export_output:
            errors.append("C29 saved output must contain FINAL_EXPORT_CREATED")
        if "FINAL_EXPORT_BLOCKED" in export_output or "FINAL_EXPORT_SKIPPED" in export_output:
            errors.append("C29 saved output contains a blocked or skipped export marker")
        export_id = manifest.get("export_id")
        assessment_run_id = assessment.get("run_id")
        if not isinstance(export_id, str) or export_id not in export_output:
            errors.append("C29 output does not contain the manifest export_id")
        if not isinstance(assessment_run_id, str) or assessment_run_id not in export_output:
            errors.append("C29 output does not contain the assessment run_id")

    return not errors, {
        "errors": errors,
        "sections_verified": len(EXPECTED_SECTIONS) - len(missing_sections),
        "section_order": order_ok,
        "todo_markers_verified": 14 - len(bad_todos),
        "c29_execution_count": execution_count,
        "c29_final_export_created": "FINAL_EXPORT_CREATED" in export_output,
        "notebook_sha256": _sha256(path),
        "notebook_size_bytes": path.stat().st_size,
    }


def _learner_status(manifest: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    status = manifest.get("learner_todo_status")
    errors: list[str] = []
    if not isinstance(status, dict):
        return False, {"errors": ["manifest learner_todo_status is required"]}
    items = status.get("items")
    expected = {f"TODO-{number}" for number in range(1, 15)}
    observed: dict[str, bool] = {}
    duplicate: list[str] = []
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("exercise"), str):
                continue
            name = item["exercise"]
            if name in observed:
                duplicate.append(name)
            observed[name] = item.get("passed") is True
    if duplicate:
        errors.append("duplicate learner exercise records: " + ", ".join(sorted(set(duplicate))))
    if set(observed) != expected:
        errors.append("learner exercise records must contain exactly TODO-1 through TODO-14")
    if not all(observed.get(name) is True for name in expected):
        errors.append("all 14 learner exercise records must pass")
    if status.get("schema_version") != "1.0" or status.get("total") != 14 or status.get("completed") != 14 or status.get("all_complete") is not True:
        errors.append("learner_todo_status aggregate must report 14 of 14 complete")
    return not errors, {
        "errors": errors,
        "source": MANIFEST_RELATIVE,
        "completed": status.get("completed"),
        "total": status.get("total"),
        "items_verified": len(observed),
    }


def _outputs_check(root: Path) -> tuple[bool, dict[str, Any]]:
    missing = [
        relative for relative in FINAL_OUTPUTS
        if not (root / relative).is_file() or (root / relative).stat().st_size == 0
    ]
    unfinished: list[str] = []
    for relative in ("reports/PROJECT_REPORT.md", "reports/SECURITY_ASSESSMENT.md"):
        path = root / relative
        if path.is_file() and "[TODO" in path.read_text(encoding="utf-8"):
            unfinished.append(relative)
    dashboard = root / "reports/monitoring_dashboard.png"
    png_ok = dashboard.is_file() and dashboard.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    errors: list[str] = []
    if missing:
        errors.append("missing or empty final outputs: " + ", ".join(missing))
    if unfinished:
        errors.append("unfinished report placeholders: " + ", ".join(unfinished))
    if not png_ok:
        errors.append("monitoring_dashboard.png is not a valid PNG")
    return not errors, {
        "errors": errors,
        "required": len(FINAL_OUTPUTS),
        "missing": missing,
        "unfinished_reports": unfinished,
        "dashboard_png": png_ok,
    }


def _trace_check(root: Path) -> tuple[bool, dict[str, Any]]:
    required = {
        "trace_id", "span_id", "timestamp_utc", "component", "event_type",
        "status", "risk_flags", "redacted",
    }
    denied = {"message", "prompt", "chain_of_thought", "customer_id"}
    count = 0
    errors: list[str] = []
    try:
        with (root / "reports/trace.jsonl").open("r", encoding="utf-8") as handle:
            for line_number, raw in enumerate(handle, start=1):
                if not raw.strip():
                    continue
                event = json.loads(raw)
                if not isinstance(event, dict):
                    errors.append(f"trace line {line_number} is not an object")
                    break
                missing = sorted(required - set(event))
                forbidden = sorted(denied.intersection(event))
                if missing:
                    errors.append(f"trace line {line_number} missing fields: {', '.join(missing)}")
                    break
                if event.get("redacted") is not True or forbidden:
                    errors.append(f"trace line {line_number} violates redaction contract: {', '.join(forbidden)}")
                    break
                count += 1
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot validate trace: {type(exc).__name__}")
    if count == 0:
        errors.append("trace must contain at least one redacted event")
    return not errors, {"errors": errors, "events": count, "redacted": count > 0 and not errors}


def _assessment_check(assessment: Any) -> tuple[bool, dict[str, Any]]:
    passed, errors = validate_assessment_payload(assessment, require_learning_gates=True)
    gates = assessment.get("critical_gates") if isinstance(assessment, dict) else None
    return passed, {
        "errors": errors,
        "run_id": assessment.get("run_id") if isinstance(assessment, dict) else None,
        "functional_cases": assessment.get("metrics", {}).get("functional_case_count") if isinstance(assessment, dict) else None,
        "security_cases": assessment.get("metrics", {}).get("security_case_count") if isinstance(assessment, dict) else None,
        "critical_gates": gates if isinstance(gates, dict) else {},
    }


def _safe_manifest_path(root: Path, relative: str) -> tuple[Path | None, str | None]:
    pure = PurePosixPath(relative)
    if not relative or pure.is_absolute() or ".." in pure.parts or "\\" in relative:
        return None, "path must be a normalized relative POSIX path"
    path = root.joinpath(*pure.parts)
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        return None, "file is missing"
    root_resolved = root.resolve()
    if root_resolved not in resolved.parents or path.is_symlink():
        return None, "path escapes the repository or is a symlink"
    if not path.is_file():
        return None, "path is not a regular file"
    return path, None


def _manifest_check(
    root: Path,
    manifest: dict[str, Any],
    assessment: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    records = manifest.get("files")
    safety = manifest.get("safety_checks")
    errors: list[str] = []
    mismatches: list[str] = []
    unsafe_entries: list[str] = []
    paths: set[str] = set()
    duplicate_paths: list[str] = []
    if isinstance(records, list):
        for record in records:
            if not isinstance(record, dict) or set(record) != {"path", "sha256", "size_bytes"}:
                unsafe_entries.append("<invalid-record>")
                continue
            relative = record.get("path")
            if not isinstance(relative, str):
                unsafe_entries.append("<non-string-path>")
                continue
            if relative in paths:
                duplicate_paths.append(relative)
            paths.add(relative)
            if (
                relative in {MANIFEST_RELATIVE, NOTEBOOK_RELATIVE, RECEIPT_RELATIVE}
                or relative.startswith("reports/checkpoints/")
                or relative.endswith(".zip")
            ):
                unsafe_entries.append(relative)
                continue
            path, path_error = _safe_manifest_path(root, relative)
            if path_error or path is None:
                unsafe_entries.append(f"{relative}: {path_error}")
                continue
            content = path.read_bytes()
            expected_hash = record.get("sha256")
            expected_size = record.get("size_bytes")
            if (
                not isinstance(expected_hash, str)
                or re.fullmatch(r"[a-f0-9]{64}", expected_hash) is None
                or not isinstance(expected_size, int)
                or isinstance(expected_size, bool)
                or hashlib.sha256(content).hexdigest() != expected_hash
                or len(content) != expected_size
            ):
                mismatches.append(relative)
    else:
        errors.append("manifest files must be a nonempty array")

    if duplicate_paths:
        errors.append("duplicate manifest paths: " + ", ".join(sorted(set(duplicate_paths))))
    if unsafe_entries:
        errors.append("unsafe or invalid manifest entries: " + ", ".join(unsafe_entries))
    if mismatches:
        errors.append("hash or size mismatch: " + ", ".join(mismatches))
    missing_hashed = sorted(REQUIRED_HASHED_FILES - paths)
    if missing_hashed:
        errors.append("required files absent from manifest hashes: " + ", ".join(missing_hashed))

    assessment_path = root / ASSESSMENT_RELATIVE
    assessment_sha = _sha256(assessment_path) if assessment_path.is_file() else None
    assessment_run_id = assessment.get("run_id") if isinstance(assessment, dict) else None
    expected_export_id = (
        "export-" + hashlib.sha256(f"{assessment_run_id}:{assessment_sha}".encode("utf-8")).hexdigest()[:16]
        if isinstance(assessment_run_id, str) and isinstance(assessment_sha, str)
        else None
    )
    if manifest.get("schema_version") != "1.0":
        errors.append("manifest schema_version must be 1.0")
    if manifest.get("expected_final_commit_message") != EXPECTED_COMMIT_MESSAGE:
        errors.append("manifest expected_final_commit_message is incorrect")
    if manifest.get("completed_notebook_upload_required") is not True:
        errors.append("manifest must require completed notebook upload")
    if manifest.get("assessment_run_id") != assessment_run_id:
        errors.append("manifest assessment_run_id does not match assessment_results.json")
    if manifest.get("assessment_sha256") != assessment_sha:
        errors.append("manifest assessment_sha256 does not match assessment_results.json")
    if manifest.get("export_id") != expected_export_id:
        errors.append("manifest export_id is not derived from this assessment run and hash")
    if manifest.get("all_passed") is not True:
        errors.append("manifest all_passed must be true")

    if not isinstance(safety, dict):
        errors.append("manifest safety_checks must be an object")
        safety = {}
    missing_safety = sorted(REQUIRED_MANIFEST_SAFETY - set(safety))
    false_safety = sorted(name for name in REQUIRED_MANIFEST_SAFETY if safety.get(name) is not True)
    if missing_safety:
        errors.append("missing required safety checks: " + ", ".join(missing_safety))
    if false_safety:
        errors.append("required safety checks not true: " + ", ".join(false_safety))

    return not errors, {
        "errors": errors,
        "files": len(records) if isinstance(records, list) else 0,
        "required_files_hashed": not missing_hashed,
        "hash_or_size_mismatches": mismatches,
        "unsafe_entries": unsafe_entries,
        "export_id": manifest.get("export_id"),
        "assessment_run_id": manifest.get("assessment_run_id"),
        "manifest_sha256": _sha256(root / MANIFEST_RELATIVE),
        "manifest_self_hash_omitted": MANIFEST_RELATIVE not in paths,
        "notebook_hash_bound_in_receipt": NOTEBOOK_RELATIVE not in paths,
    }


def _secret_check(root: Path) -> tuple[bool, dict[str, Any]]:
    findings: list[dict[str, str]] = []
    forbidden_files: list[str] = []
    symlinks: list[str] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if any(part in {".git", "__pycache__", ".ipynb_checkpoints"} for part in path.parts):
            continue
        if path.is_symlink():
            symlinks.append(relative)
            continue
        if not path.is_file():
            continue
        lowered = path.name.casefold()
        if lowered.startswith(".env") and lowered != ".env.example":
            forbidden_files.append(relative)
        if re.search(r"(?:hidden|solution|answer[-_]?key|instructor[-_]?package)", relative, re.IGNORECASE):
            forbidden_files.append(relative)
        if path.name != ".env.example" and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"path": relative, "type": label})
    zip_present = (root / "rafeeq-mini-submission.zip").exists()
    errors: list[str] = []
    if findings:
        errors.append("configured credential-shaped values found")
    if forbidden_files:
        errors.append("private or forbidden files found")
    if symlinks:
        errors.append("symbolic links are not accepted in submissions")
    if zip_present:
        errors.append("do not commit rafeeq-mini-submission.zip")
    return not errors, {
        "errors": errors,
        "configured_secret_findings": findings,
        "forbidden_files": sorted(set(forbidden_files)),
        "symlinks": symlinks,
        "export_zip_committed": zip_present,
    }


def _load_object(path: Path, label: str) -> tuple[dict[str, Any], list[str]]:
    try:
        value = _read_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {}, [f"cannot read {label}: {type(exc).__name__}"]
    if not isinstance(value, dict):
        return {}, [f"{label} must be a JSON object"]
    return value, []


def _failure_messages(checks: list[dict[str, Any]]) -> list[str]:
    messages: list[str] = []
    for check in checks:
        if check["passed"]:
            continue
        errors = check.get("details", {}).get("errors")
        reason = "; ".join(str(item) for item in errors) if isinstance(errors, list) and errors else "validation failed"
        messages.append(f"{check['name']}: {reason} Next: {FAILURE_HELP[check['name']]}")
    return messages


def validate_submission(root: Path | None = None) -> dict[str, Any]:
    repository = (root or VALIDATOR_ROOT).expanduser().resolve()
    checks: list[dict[str, Any]] = []

    def add(name: str, result: tuple[bool, dict[str, Any]]) -> None:
        passed, details = result
        checks.append({"name": name, "passed": bool(passed), "details": details})

    if not repository.is_dir():
        return {
            "schema_version": "1.0",
            "generated_at_utc": utc_now(),
            "validator": "trusted_learner_submission",
            "repository": str(repository),
            "checks": [],
            "passed": 0,
            "failed": 7,
            "all_passed": False,
            "failure_messages": ["repository path does not exist or is not a directory"],
        }

    manifest, manifest_errors = _load_object(repository / MANIFEST_RELATIVE, MANIFEST_RELATIVE)
    assessment, assessment_errors = _load_object(repository / ASSESSMENT_RELATIVE, ASSESSMENT_RELATIVE)

    add(
        "completed_notebook_structure",
        _notebook_check(repository, manifest, assessment)
        if manifest and assessment
        else (False, {"errors": [*manifest_errors, *assessment_errors]}),
    )
    add(
        "learner_todos_14_of_14",
        _learner_status(manifest) if manifest else (False, {"errors": manifest_errors}),
    )
    add("six_final_outputs", _outputs_check(repository))
    add(
        "assessment_critical_gates",
        _assessment_check(assessment) if assessment else (False, {"errors": assessment_errors}),
    )
    add("trace_redaction", _trace_check(repository))
    add(
        "submission_manifest",
        _manifest_check(repository, manifest, assessment)
        if manifest and assessment
        else (False, {"errors": [*manifest_errors, *assessment_errors]}),
    )
    add("configured_secret_scan", _secret_check(repository))
    all_passed = len(checks) == 7 and all(check["passed"] for check in checks)
    report = {
        "schema_version": "1.0",
        "generated_at_utc": utc_now(),
        "validator": "trusted_learner_submission",
        "repository": str(repository),
        "assessment_run_id": assessment.get("run_id") if assessment else None,
        "export_id": manifest.get("export_id") if manifest else None,
        "checks": checks,
        "passed": sum(bool(check["passed"]) for check in checks),
        "failed": sum(not bool(check["passed"]) for check in checks),
        "all_passed": all_passed,
    }
    report["failure_messages"] = _failure_messages(checks)
    return report


def _write_receipt(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    if report.get("all_passed") is not True:
        raise ValueError("a receipt can be written only after all seven checks pass")
    notebook_path = root / NOTEBOOK_RELATIVE
    manifest_path = root / MANIFEST_RELATIVE
    assessment_path = root / ASSESSMENT_RELATIVE
    notebook_sha = _sha256(notebook_path)
    manifest_sha = _sha256(manifest_path)
    assessment_sha = _sha256(assessment_path)
    export_id = str(report["export_id"])
    assessment_run_id = str(report["assessment_run_id"])
    receipt_material = f"{export_id}:{assessment_run_id}:{notebook_sha}:{manifest_sha}:{assessment_sha}"
    receipt = {
        "schema_version": "1.0",
        "receipt_id": "receipt-" + hashlib.sha256(receipt_material.encode("utf-8")).hexdigest()[:24],
        "generated_at_utc": utc_now(),
        "export_id": export_id,
        "assessment_run_id": assessment_run_id,
        "notebook": {
            "path": NOTEBOOK_RELATIVE,
            "sha256": notebook_sha,
            "size_bytes": notebook_path.stat().st_size,
            "c29_marker": "FINAL_EXPORT_CREATED",
        },
        "manifest": {
            "path": MANIFEST_RELATIVE,
            "sha256": manifest_sha,
            "size_bytes": manifest_path.stat().st_size,
        },
        "assessment": {
            "path": ASSESSMENT_RELATIVE,
            "sha256": assessment_sha,
            "size_bytes": assessment_path.stat().st_size,
        },
        "validation": {
            "validator": "trusted_learner_submission",
            "check_names": [check["name"] for check in report["checks"]],
            "checks_passed": 7,
            "all_passed": True,
        },
    }
    path = root / RECEIPT_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("receipt path must not be a symbolic link")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "repository",
        nargs="?",
        type=Path,
        help="learner repository root; omit when running the exported repository's own copy",
    )
    parser.add_argument(
        "--write-receipt",
        action="store_true",
        help="write reports/submission_receipt.json after all checks pass",
    )
    args = parser.parse_args(argv)
    root = (args.repository or VALIDATOR_ROOT).expanduser().resolve()
    report = validate_submission(root)
    if args.write_receipt and report["all_passed"]:
        try:
            receipt = _write_receipt(root, report)
        except (OSError, UnicodeError, ValueError) as exc:
            report["all_passed"] = False
            report["failed"] = int(report["failed"]) + 1
            report["failure_messages"].append(f"submission_receipt: {exc}")
        else:
            report["receipt"] = {
                "path": RECEIPT_RELATIVE,
                "receipt_id": receipt["receipt_id"],
                "notebook_sha256": receipt["notebook"]["sha256"],
            }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    # Trusted batch grading passes a repository path and expects JSON only.
    if args.repository is None:
        print(f"SUBMISSION_CHECK={'PASSED' if report['all_passed'] else 'FAILED'}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
