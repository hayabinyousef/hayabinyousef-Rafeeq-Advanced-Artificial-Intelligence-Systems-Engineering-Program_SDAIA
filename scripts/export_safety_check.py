#!/usr/bin/env python3
"""Preflight or export a clean Rafeeq learner submission bundle.

The default mode is a read-only precheck and never creates a ZIP.  Pass
``--export`` only after the clean final run and completed reports.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterable
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "src"
REPORTS_DIR = ROOT / "reports"
DEFAULT_ZIP_PATH = ROOT / "rafeeq-mini-submission.zip"
MANIFEST_PATH = REPORTS_DIR / "submission_manifest.json"
LEARNER_STATUS_PATH = REPORTS_DIR / "checkpoints" / "learner_todo_status.json"
EXPECTED_COMMIT_MESSAGE = "feat: submit Rafeeq Mini capstone"
STUDENT_WORKFLOW_PATH = ".github/workflows/learner-submission-quality.yml"
STUDENT_WORKFLOW = """name: Learner submission quality

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  validate:
    name: Validate learner submission
    runs-on: ubuntu-latest
    timeout-minutes: 8
    env:
      LLM_MODE: stub
      PYTHONDONTWRITEBYTECODE: "1"
    steps:
      - name: Check out submission
        uses: actions/checkout@v4
      - name: Select Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run public tests
        run: python -m unittest discover -s tests/public -p "test_*.py" -v
      - name: Validate completed submission
        run: python scripts/validate_submission.py --write-receipt
      - name: Upload cryptographic submission receipt
        uses: actions/upload-artifact@v4
        with:
          name: rafeeq-submission-receipt
          path: reports/submission_receipt.json
          if-no-files-found: error
"""
VIRTUAL_FILES: dict[str, bytes] = {STUDENT_WORKFLOW_PATH: STUDENT_WORKFLOW.encode("utf-8")}

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from rafeeq.assessment import validate_assessment_payload  # noqa: E402


REQUIRED_OUTPUTS = (
    "reports/checkpoints/doctor_report.json",
    "reports/checkpoints/day1_results.json",
    "reports/checkpoints/day2_memory_results.json",
    "reports/checkpoints/day2_results.json",
    "reports/checkpoints/day3_security_baseline.json",
    "reports/checkpoints/day3_security_retest.json",
    "reports/PROJECT_REPORT.md",
    "reports/SECURITY_ASSESSMENT.md",
    "reports/trace.jsonl",
    "reports/assessment_results.json",
    "reports/monitoring_dashboard.png",
)

FORBIDDEN_PARTS = re.compile(
    r"^(?:\.env(?:\..*)?|.*(?:hidden|solution|answer[-_]?key|instructor[-_]?package).*)$",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{24,}\b", re.IGNORECASE)),
)
TEXT_SUFFIXES = {".py", ".md", ".json", ".jsonl", ".csv", ".txt", ".yml", ".yaml", ".html", ".js", ".css"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _inside_repository(path: Path) -> bool:
    resolved = path.resolve()
    root = ROOT.resolve()
    return resolved == root or root in resolved.parents


def _iter_tree(directory: Path) -> Iterable[Path]:
    if not directory.is_dir():
        return ()
    return (
        path
        for path in sorted(directory.rglob("*"))
        if path.is_file()
        and "__pycache__" not in path.parts
        and not any(part in {".git", ".cache", ".pytest_cache", ".ipynb_checkpoints"} for part in path.parts)
        and path.suffix not in {".pyc", ".pyo", ".zip", ".db"}
        and not path.name.startswith(".")
    )


def candidate_files() -> list[Path]:
    """Return the allow-listed project files copied into the ZIP."""

    files: set[Path] = set()
    for relative in (
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "COURSE_USE_PERMISSION.md",
        "requirements-colab.txt",
        ".gitignore",
        ".env.example",
        "notebooks/README.md",
    ):
        path = ROOT / relative
        if path.is_file():
            files.add(path)
    for relative in (
        "src/rafeeq",
        "mcp_server",
        "data/public",
        "tests/public",
        "tests/schemas",
        "reports/templates",
        "recovery",
        "scripts",
        "docs",
        ".github",
    ):
        files.update(_iter_tree(ROOT / relative))
    for relative in (
        "reports/PROJECT_REPORT.md",
        "reports/SECURITY_ASSESSMENT.md",
        "reports/trace.jsonl",
        "reports/assessment_results.json",
        "reports/monitoring_dashboard.png",
    ):
        path = ROOT / relative
        if path.is_file():
            files.add(path)
    # Course-source automation is intentionally not copied to a learner's
    # final repository. Only the virtual submission workflow below belongs in
    # the exported bundle; the Pages workflow also needs owner-side setup.
    files.discard(ROOT / ".github" / "workflows" / "learner-quality.yml")
    files.discard(ROOT / ".github" / "workflows" / "pages.yml")
    files.discard(ROOT / STUDENT_WORKFLOW_PATH)
    files.discard(ROOT / ".github" / "pull_request_template.md")
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def _secret_findings(files: Iterable[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in files:
        if (
            path.name != ".env.example"
            and path.suffix.lower() not in TEXT_SUFFIXES
        ) or path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            findings.append({"path": path.relative_to(ROOT).as_posix(), "type": "invalid_utf8"})
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"path": path.relative_to(ROOT).as_posix(), "type": label})
    return findings


def _forbidden_paths(files: Iterable[Path]) -> list[str]:
    blocked: list[str] = []
    for path in files:
        relative = path.relative_to(ROOT)
        if relative.as_posix() == ".env.example":
            continue
        if any(FORBIDDEN_PARTS.match(part) for part in relative.parts):
            blocked.append(relative.as_posix())
    return blocked


def _assessment_ready() -> tuple[bool, dict[str, Any]]:
    path = REPORTS_DIR / "assessment_results.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return False, {"errors": [f"assessment_results.json cannot be read: {type(exc).__name__}"]}
    ready, errors = validate_assessment_payload(payload, require_learning_gates=True)
    return ready, {**payload, "contract_errors": errors}


def _trace_redacted() -> bool:
    path = REPORTS_DIR / "trace.jsonl"
    count = 0
    denied = {"message", "prompt", "chain_of_thought", "customer_id"}
    try:
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                if not raw.strip():
                    continue
                value = json.loads(raw)
                if not isinstance(value, dict) or value.get("redacted") is not True or denied.intersection(value):
                    return False
                count += 1
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False
    return count > 0


def load_learner_todo_status() -> tuple[bool, dict[str, Any]]:
    """Load the C29 learner evidence without exporting its checkpoint file."""

    try:
        payload = json.loads(LEARNER_STATUS_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False, {}
    if not isinstance(payload, dict):
        return False, {}
    items = payload.get("items")
    expected = {f"TODO-{number}" for number in range(1, 15)}
    observed: dict[str, bool] = {}
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("exercise"), str):
                observed[item["exercise"]] = item.get("passed") is True
    ready = (
        payload.get("schema_version") == "1.0"
        and payload.get("completed") == 14
        and payload.get("total") == 14
        and payload.get("all_complete") is True
        and set(observed) == expected
        and all(observed.values())
    )
    return ready, payload


def precheck() -> tuple[dict[str, Any], list[Path]]:
    files = candidate_files()
    missing = [relative for relative in REQUIRED_OUTPUTS if not (ROOT / relative).is_file()]
    forbidden = _forbidden_paths(files)
    secrets = _secret_findings(files)
    assessment_ready, assessment_details = _assessment_ready()
    reports_complete = True
    for name in ("PROJECT_REPORT.md", "SECURITY_ASSESSMENT.md"):
        path = REPORTS_DIR / name
        if not path.is_file() or "[TODO" in path.read_text(encoding="utf-8"):
            reports_complete = False
    size_ok = all(path.stat().st_size <= 10_000_000 for path in files)
    safety_checks = {
        "required_outputs_present": not missing,
        "configured_secret_scan_no_match": not secrets,
        "forbidden_paths_absent": not forbidden,
        "critical_gates_passed": assessment_ready,
        "trace_redacted": _trace_redacted(),
        "reports_complete": reports_complete,
        "individual_file_size_limit": size_ok,
        "notebook_excluded_from_manifest_hash": True,
        "manual_notebook_upload_required": True,
        "notebook_bound_by_submission_receipt": True,
        "submission_receipt_required": True,
        "student_submission_ci_installed": (
            STUDENT_WORKFLOW_PATH in VIRTUAL_FILES
            and not {
                ".github/workflows/learner-quality.yml",
                ".github/workflows/pages.yml",
            }.intersection(path.relative_to(ROOT).as_posix() for path in files)
        ),
    }
    passed = bool(files) and all(safety_checks.values())
    return (
        {
            "schema_version": "1.0",
            "generated_at_utc": utc_now(),
            "mode": "precheck",
            "safety_checks": safety_checks,
            "missing_outputs": missing,
            "forbidden_paths": forbidden,
            "secret_findings": secrets,
            "assessment_contract_errors": assessment_details.get("contract_errors", []),
            "files_selected": len(files) + len(VIRTUAL_FILES),
            "all_passed": passed,
        },
        files,
    )


def _file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def _manifest(
    preflight: dict[str, Any],
    files: list[Path],
    learner_todo_status: dict[str, Any],
) -> dict[str, Any]:
    assessment_path = REPORTS_DIR / "assessment_results.json"
    assessment_bytes = assessment_path.read_bytes()
    assessment_payload = json.loads(assessment_bytes.decode("utf-8"))
    assessment_ready, assessment_errors = validate_assessment_payload(
        assessment_payload,
        require_learning_gates=True,
    )
    if not assessment_ready:
        raise ValueError("assessment contract failed: " + "; ".join(assessment_errors))
    assessment_run_id = str(assessment_payload["run_id"])
    assessment_sha256 = hashlib.sha256(assessment_bytes).hexdigest()
    export_id = "export-" + hashlib.sha256(
        f"{assessment_run_id}:{assessment_sha256}".encode("utf-8")
    ).hexdigest()[:16]
    records = [_file_record(path) for path in files]
    records.extend(
        {
            "path": relative,
            "sha256": hashlib.sha256(content).hexdigest(),
            "size_bytes": len(content),
        }
        for relative, content in sorted(VIRTUAL_FILES.items())
    )
    return {
        "schema_version": "1.0",
        "generated_at_utc": utc_now(),
        "export_id": export_id,
        "assessment_run_id": assessment_run_id,
        "assessment_sha256": assessment_sha256,
        "expected_final_commit_message": EXPECTED_COMMIT_MESSAGE,
        "completed_notebook_upload_required": True,
        "learner_todo_status": learner_todo_status,
        "files": records,
        "safety_checks": {
            **dict(preflight["safety_checks"]),
            "learner_todos_14_of_14": True,
        },
        "all_passed": bool(preflight["all_passed"]),
        "excluded": [
            "notebooks/Rafeeq_Mini_Capstone.ipynb (save to GitHub separately)",
            "reports/submission_receipt.json (created after the notebook is uploaded and validated)",
            ".env and credentials",
            "hidden evaluations and instructor material",
            "database/cache/runtime files",
            "reports/submission_manifest.json (self-hash intentionally omitted)",
        ],
        "secret_scan_statement": "No match was found by the configured checks; this is not proof that no secret exists.",
    }


def _write_manifest(payload: dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    temporary = MANIFEST_PATH.with_name(MANIFEST_PATH.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, MANIFEST_PATH)


def _zip_info(relative: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    return info


def _validated_zip_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    root = ROOT.resolve()
    if root not in resolved.parents or resolved.suffix.lower() != ".zip":
        raise ValueError("--output must be a .zip file inside the repository")
    if ".git" in resolved.relative_to(root).parts:
        raise ValueError("--output cannot be written inside .git")
    return resolved


def _write_zip(files: list[Path], zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = zip_path.with_name(zip_path.name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            archive.writestr(_zip_info(relative), path.read_bytes())
        for relative, content in sorted(VIRTUAL_FILES.items()):
            archive.writestr(_zip_info(relative), content)
        archive.writestr(
            _zip_info("reports/submission_manifest.json"),
            MANIFEST_PATH.read_bytes(),
        )
    os.replace(temporary, zip_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="store_true", help="create the final manifest and ZIP after a passing precheck")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ZIP_PATH,
        help="ZIP path inside the repository (default: rafeeq-mini-submission.zip)",
    )
    args = parser.parse_args(argv)
    try:
        zip_path = _validated_zip_path(args.output)
        report, files = precheck()
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        if not args.export:
            print("FINAL_EXPORT_SKIPPED")
        return 2

    if not args.export:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        print("FINAL_EXPORT_SKIPPED")
        return 0 if report["all_passed"] else 1

    if not report["all_passed"]:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        print("FINAL_EXPORT_BLOCKED")
        return 1

    learner_status_ready, learner_todo_status = load_learner_todo_status()
    if not learner_status_ready:
        print(json.dumps({
            "status": "blocked",
            "error": "C29 learner TODO evidence is missing or incomplete",
            "required": LEARNER_STATUS_PATH.relative_to(ROOT).as_posix(),
        }, ensure_ascii=False, indent=2, sort_keys=True))
        print("FINAL_EXPORT_BLOCKED")
        return 1

    manifest = _manifest(report, files, learner_todo_status)
    _write_manifest(manifest)
    _write_zip(files, zip_path)
    result = {
        "status": "exported",
        "zip": zip_path.relative_to(ROOT).as_posix(),
        "manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
        "zip_size_bytes": zip_path.stat().st_size,
        "files_hashed": len(manifest["files"]),
        "export_id": manifest["export_id"],
        "assessment_run_id": manifest["assessment_run_id"],
        "all_passed": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    print(
        "FINAL_EXPORT_CREATED: "
        f"export_id={manifest['export_id']} assessment_run_id={manifest['assessment_run_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
