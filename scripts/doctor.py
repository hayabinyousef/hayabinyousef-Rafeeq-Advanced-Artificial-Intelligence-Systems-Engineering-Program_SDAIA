#!/usr/bin/env python3
"""Run the dependency-free Rafeeq environment doctor.

The doctor is intentionally conservative: it verifies the offline learner
path, public synthetic data, core smoke scenarios, and the real local MCP
stdio boundary.  It never reads or prints credentials.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "src"
DATA_DIR = ROOT / "data" / "public"
REPORTS_DIR = ROOT / "reports"
DEFAULT_OUTPUT = REPORTS_DIR / "checkpoints" / "doctor_report.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _inside_reports(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    reports = REPORTS_DIR.resolve()
    if resolved != reports and reports not in resolved.parents:
        raise ValueError("output must stay inside the repository reports directory")
    return resolved


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    target = _inside_reports(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, target)


def _jsonl_count(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError(f"{path.name}:{line_number} is not a JSON object")
            count += 1
    return count


def collect_doctor() -> dict[str, Any]:
    """Collect a JSON-serializable readiness report without writing it."""

    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}
    errors: list[dict[str, str]] = []

    checks["supported_python"] = sys.version_info >= (3, 10)
    details["python"] = platform.python_version()
    details["platform"] = platform.system().lower()
    details["repository_root"] = "."
    details["llm_mode"] = os.getenv("LLM_MODE", "stub").strip().lower()
    checks["offline_stub_mode"] = details["llm_mode"] == "stub"

    required_files = (
        DATA_DIR / "orders.csv",
        DATA_DIR / "policy_chunks.jsonl",
        DATA_DIR / "memory_seed.jsonl",
        DATA_DIR / "tickets_dev.jsonl",
        DATA_DIR / "eval_public.jsonl",
        DATA_DIR / "security_cases.jsonl",
        ROOT / "mcp_server" / "tawseel_server.py",
        SOURCE_DIR / "rafeeq" / "graph.py",
        ROOT / "tests" / "schemas" / "trace.schema.json",
    )
    missing = [path.relative_to(ROOT).as_posix() for path in required_files if not path.is_file()]
    checks["required_files"] = not missing
    details["missing_files"] = missing

    expected_counts = {
        "policy_chunks.jsonl": 6,
        "memory_seed.jsonl": 8,
        "tickets_dev.jsonl": 16,
        "eval_public.jsonl": 8,
        "security_cases.jsonl": 8,
    }
    dataset_counts: dict[str, int] = {}
    try:
        import csv

        with (DATA_DIR / "orders.csv").open("r", encoding="utf-8-sig", newline="") as handle:
            dataset_counts["orders.csv"] = sum(1 for _ in csv.DictReader(handle))
        for name in expected_counts:
            dataset_counts[name] = _jsonl_count(DATA_DIR / name)
        checks["dataset_contract"] = dataset_counts.get("orders.csv") == 24 and all(
            dataset_counts.get(name) == count for name, count in expected_counts.items()
        )
    except Exception as exc:  # the report must survive a malformed learner file
        checks["dataset_contract"] = False
        errors.append({"check": "dataset_contract", "error": type(exc).__name__})
    details["dataset_counts"] = dataset_counts

    try:
        from rafeeq.assessment import self_smoke
        from rafeeq.graph import RafeeqRuntime

        runtime = RafeeqRuntime(DATA_DIR)
        health = runtime.health_snapshot()
        smoke = self_smoke()
        checks["runtime_health"] = health.get("status") == "ready" and health.get("network_required") is False
        checks["core_self_smoke"] = bool(smoke) and all(smoke.values())
        details["runtime_health"] = health
        details["core_self_smoke"] = smoke
    except Exception as exc:
        checks["runtime_health"] = False
        checks["core_self_smoke"] = False
        errors.append({"check": "core_runtime", "error": type(exc).__name__})

    try:
        from rafeeq.mcp_client import smoke_check

        mcp = smoke_check(data_dir=DATA_DIR)
        checks["mcp_stdio"] = bool(mcp.get("ok")) and mcp.get("transport") == "stdio"
        details["mcp"] = {
            "ok": bool(mcp.get("ok")),
            "transport": mcp.get("transport"),
            "protocol_version": mcp.get("protocol_version"),
            "tools": mcp.get("tools", []),
            "closed_after_context": bool(mcp.get("closed_after_context")),
            "idempotency": mcp.get("idempotency", {}),
        }
    except Exception as exc:
        checks["mcp_stdio"] = False
        errors.append({"check": "mcp_stdio", "error": type(exc).__name__})

    all_passed = bool(checks) and all(checks.values())
    return {
        "schema_version": "1.0",
        "generated_at_utc": utc_now(),
        "status": "ready" if all_passed else "not_ready",
        "checks": checks,
        "details": details,
        "errors": errors,
        "all_passed": all_passed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="JSON report path under reports/ (default: reports/checkpoints/doctor_report.json)",
    )
    args = parser.parse_args(argv)
    try:
        report = collect_doctor()
        _write_json(args.output, report)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"DOCTOR_REPORT={_inside_reports(args.output).relative_to(ROOT).as_posix()}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
