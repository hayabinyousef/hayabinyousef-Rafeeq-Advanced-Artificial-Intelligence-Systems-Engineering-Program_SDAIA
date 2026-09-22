#!/usr/bin/env python3
"""Check the zero-cost Rafeeq learner path before a training cohort.

The preflight is deliberately dependency-free.  It verifies everything that
can be established from the repository, then reports the hosted Colab pilot as
a separate manual acceptance item.  It never reads or prints credential
values.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
DATA_DIR = ROOT / "data" / "public"
NOTEBOOK = ROOT / "notebooks" / "Rafeeq_Mini_Capstone.ipynb"
DEFAULT_OUTPUT = ROOT / "reports" / "checkpoints" / "preflight_readiness.json"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_notebook import EXPECTED_SECTIONS, validate as validate_notebook  # noqa: E402


EXPECTED_DATASET_COUNTS = {
    "orders.csv": 24,
    "policy_chunks.jsonl": 6,
    "memory_seed.jsonl": 8,
    "tickets_dev.jsonl": 16,
    "eval_public.jsonl": 8,
    "security_cases.jsonl": 8,
}

REQUIRED_PATHS = (
    "README.md",
    "requirements-colab.txt",
    "notebooks/Rafeeq_Mini_Capstone.ipynb",
    "mcp_server/tawseel_server.py",
    "src/rafeeq/graph.py",
    "scripts/doctor.py",
    "scripts/run_gate.py",
    "scripts/run_assessment.py",
    "scripts/export_safety_check.py",
    "tests/schemas/assessment.schema.json",
    "tests/schemas/manifest.schema.json",
    "tests/schemas/trace.schema.json",
)

MANUAL_ACCEPTANCE = (
    {
        "id": "clean_google_account",
        "en": "Open the course from a clean Google account.",
        "ar": "فتح الدورة من حساب Google تجريبي نظيف.",
    },
    {
        "id": "hosted_colab_c0_c29",
        "en": "Run the hosted Colab path from C0 through C29.",
        "ar": "تشغيل مسار Colab المستضاف من C0 حتى C29.",
    },
    {
        "id": "runtime_recovery",
        "en": "Interrupt the runtime and verify the documented recovery path.",
        "ar": "قطع جلسة التشغيل والتحقق من مسار الاستعادة الموثق.",
    },
    {
        "id": "github_export",
        "en": "Upload the C29 export and final notebook beside the learner's safe progress log.",
        "ar": "رفع حزمة C29 والدفتر النهائي بجانب سجل تقدم المتدرب الآمن.",
    },
    {
        "id": "github_actions_green",
        "en": "Confirm the Learner submission quality workflow finishes green.",
        "ar": "التأكد من انتهاء فحص Learner submission quality بالعلامة الخضراء.",
    },
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _count_jsonl(path: Path) -> int:
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


def _dataset_counts(root: Path) -> dict[str, int]:
    data_dir = root / "data" / "public"
    counts: dict[str, int] = {}
    with (data_dir / "orders.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        counts["orders.csv"] = sum(1 for _ in csv.DictReader(handle))
    for name in EXPECTED_DATASET_COUNTS:
        if name != "orders.csv":
            counts[name] = _count_jsonl(data_dir / name)
    return counts


def _requirements_are_offline(root: Path) -> tuple[bool, list[str]]:
    path = root / "requirements-colab.txt"
    active = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return not active, active


def _write_probe(root: Path) -> tuple[bool, str | None]:
    checkpoint_dir = root / "reports" / "checkpoints"
    try:
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=".rafeeq-preflight-",
            dir=checkpoint_dir,
            delete=True,
        ) as handle:
            handle.write("ok\n")
            handle.flush()
        return True, None
    except OSError as exc:
        return False, type(exc).__name__


def collect_preflight(root: Path = ROOT) -> dict[str, Any]:
    """Return deterministic repository checks plus explicit manual acceptance."""

    root = root.resolve()
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, en: str, ar: str, details: Any = None) -> None:
        item: dict[str, Any] = {
            "id": check_id,
            "passed": bool(passed),
            "en": en,
            "ar": ar,
        }
        if details is not None:
            item["details"] = details
        checks.append(item)

    add(
        "python_version",
        sys.version_info >= (3, 10),
        "Python 3.10 or newer is available.",
        "إصدار Python 3.10 أو أحدث متاح.",
        {"major": sys.version_info.major, "minor": sys.version_info.minor},
    )

    missing = [relative for relative in REQUIRED_PATHS if not (root / relative).is_file()]
    add(
        "required_files",
        not missing,
        "Required course files are present.",
        "ملفات الدورة الإلزامية موجودة.",
        {"missing": missing},
    )

    try:
        counts = _dataset_counts(root)
        data_ok = counts == EXPECTED_DATASET_COUNTS
        data_details: Any = {"actual": counts, "expected": EXPECTED_DATASET_COUNTS}
    except (OSError, UnicodeDecodeError, csv.Error, json.JSONDecodeError, ValueError) as exc:
        data_ok = False
        data_details = {"error": type(exc).__name__}
    add(
        "synthetic_dataset",
        data_ok,
        "Synthetic datasets match the published contract.",
        "البيانات الاصطناعية تطابق العقد المنشور.",
        data_details,
    )

    notebook_errors = validate_notebook(root / NOTEBOOK.relative_to(ROOT))
    add(
        "notebook_contract",
        not notebook_errors,
        "The notebook has C0-C29, 14 learner TODOs, and cleared outputs.",
        "يحتوي الدفتر على C0-C29 و14 مهمة للمتدرب ومخرجات ممسوحة.",
        {
            "sections": len(EXPECTED_SECTIONS),
            "todo_count": 14,
            "errors": notebook_errors,
        },
    )

    try:
        offline_ok, active_requirements = _requirements_are_offline(root)
    except OSError as exc:
        offline_ok, active_requirements = False, [type(exc).__name__]
    add(
        "zero_cost_path",
        offline_ok,
        "The mandatory path requires no pip package, API key, GPU, or paid service.",
        "المسار الإلزامي لا يحتاج حزمة pip أو مفتاح API أو GPU أو خدمة مدفوعة.",
        {"active_requirements": active_requirements, "llm_mode": "stub"},
    )

    llm_mode = os.getenv("LLM_MODE", "stub").strip().lower()
    add(
        "stub_mode",
        llm_mode == "stub",
        "LLM_MODE is unset or explicitly set to stub.",
        "وضع LLM_MODE غير مضبوط أو مضبوط صراحة على stub.",
        {"llm_mode": llm_mode},
    )

    writable, write_error = _write_probe(root)
    add(
        "checkpoint_write",
        writable,
        "Checkpoint output is writable.",
        "مسار حفظ نقاط التحقق قابل للكتابة.",
        {"error": write_error},
    )

    automated_ready = bool(checks) and all(item["passed"] for item in checks)
    return {
        "schema_version": "1.0",
        "generated_at_utc": _utc_now(),
        "automated_ready": automated_ready,
        "release_ready": False,
        "release_status": "manual_hosted_colab_acceptance_required",
        "checks": checks,
        "manual_acceptance": [dict(item, status="pending") for item in MANUAL_ACCEPTANCE],
        "privacy_note": {
            "en": "No credential values were read or printed.",
            "ar": "لم تُقرأ أو تُطبع أي قيم لبيانات الدخول.",
        },
    }


def _safe_output(path: Path, root: Path) -> Path:
    resolved = path.expanduser().resolve()
    reports = (root / "reports").resolve()
    if resolved != reports and reports not in resolved.parents:
        raise ValueError("output must stay inside reports/")
    return resolved


def _render_human(report: dict[str, Any]) -> str:
    lines = ["Rafeeq preflight · فحص جاهزية رفيق", ""]
    for item in report["checks"]:
        mark = "PASS" if item["passed"] else "FAIL"
        lines.append(f"[{mark}] {item['en']}")
        lines.append(f"       {item['ar']}")
    lines.extend(
        [
            "",
            "Automated checks passed; hosted Colab acceptance remains manual."
            if report["automated_ready"]
            else "One or more automated checks failed.",
            "نجحت الفحوص الآلية؛ ويبقى قبول Colab المستضاف إجراءً يدويًا."
            if report["automated_ready"]
            else "فشل فحص آلي واحد أو أكثر.",
            "",
            "Manual acceptance · القبول اليدوي:",
        ]
    )
    for item in report["manual_acceptance"]:
        lines.append(f"[PENDING] {item['en']} | {item['ar']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON only")
    parser.add_argument("--output", type=Path, help="optional JSON path under reports/")
    args = parser.parse_args(argv)

    report = collect_preflight()
    if args.output:
        try:
            target = _safe_output(args.output, ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except (OSError, ValueError) as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
            return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(_render_human(report))
    return 0 if report["automated_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
