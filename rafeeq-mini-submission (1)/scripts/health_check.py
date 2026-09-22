#!/usr/bin/env python3
"""Print a compact JSON health check for the mandatory offline learner path."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "src"
DATA_DIR = ROOT / "data" / "public"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from rafeeq.assessment import self_smoke  # noqa: E402
from rafeeq.graph import RafeeqRuntime  # noqa: E402
from rafeeq.mcp_client import smoke_check  # noqa: E402


def health_check(include_mcp: bool = True) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}
    errors: list[dict[str, str]] = []
    try:
        runtime = RafeeqRuntime(DATA_DIR)
        snapshot = runtime.health_snapshot()
        core = self_smoke()
        checks["runtime"] = snapshot.get("status") == "ready" and snapshot.get("llm_mode") == "stub"
        checks["core_smoke"] = bool(core) and all(core.values())
        details["runtime"] = snapshot
        details["core_smoke"] = core
    except Exception as exc:
        checks["runtime"] = False
        checks["core_smoke"] = False
        errors.append({"component": "core", "error": type(exc).__name__})

    if include_mcp:
        try:
            mcp = smoke_check(data_dir=DATA_DIR)
            checks["mcp_stdio"] = bool(mcp.get("ok"))
            details["mcp"] = {
                "transport": mcp.get("transport"),
                "protocol_version": mcp.get("protocol_version"),
                "tools": mcp.get("tools", []),
                "closed_after_context": bool(mcp.get("closed_after_context")),
            }
        except Exception as exc:
            checks["mcp_stdio"] = False
            errors.append({"component": "mcp_stdio", "error": type(exc).__name__})

    healthy = bool(checks) and all(checks.values())
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "healthy" if healthy else "unhealthy",
        "checks": checks,
        "details": details,
        "errors": errors,
        "all_passed": healthy,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-mcp", action="store_true", help="skip the subprocess transport probe")
    args = parser.parse_args(argv)
    report = health_check(include_mcp=not args.skip_mcp)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
