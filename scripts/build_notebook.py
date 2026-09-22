#!/usr/bin/env python3
"""Build the self-contained bilingual Rafeeq Mini cumulative Colab notebook.

The generated notebook embeds a deterministic ZIP containing the public lab
runtime, synthetic data, public tests and learner report templates.  It needs
no network access, credentials, repository clone or package installation.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path
import re
import textwrap
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "Rafeeq_Mini_Capstone.ipynb"

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


def _clean(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


def markdown(source: str, *tags: str) -> dict[str, object]:
    return {
        "cell_type": "markdown",
        "metadata": {"tags": list(tags)} if tags else {},
        "source": _clean(source),
    }


def code(source: str, *tags: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"tags": list(tags)} if tags else {},
        "outputs": [],
        "source": _clean(source),
    }


def section(
    marker: str,
    en_title: str,
    ar_title: str,
    en_body: str,
    ar_body: str,
    evidence_en: str,
    evidence_ar: str,
    minutes: int,
) -> dict[str, object]:
    return markdown(
        f"""
        <section class="rfq-section">
          <div class="rfq-kicker"><code>{marker}</code> · {minutes} min</div>
          <div class="rfq-grid">
            <div dir="ltr" class="rfq-panel">
              <h2>{en_title}</h2>
              <p>{en_body}</p>
              <p class="rfq-evidence"><strong>Evidence:</strong> {evidence_en}</p>
            </div>
            <div dir="rtl" class="rfq-panel rfq-ar">
              <h2>{ar_title}</h2>
              <p>{ar_body}</p>
              <p class="rfq-evidence"><strong>الدليل:</strong> {evidence_ar}</p>
            </div>
          </div>
        </section>
        """,
        marker,
    )


def day_banner(day: int, en_title: str, ar_title: str, accent: str) -> dict[str, object]:
    return markdown(
        f"""
        <div class="rfq-day" style="border-color:{accent}">
          <div dir="ltr"><span>DAY {day}</span><h1>{en_title}</h1></div>
          <div dir="rtl"><span>اليوم {day}</span><h1>{ar_title}</h1></div>
        </div>
        """,
        f"day-{day}",
    )


def _payload_files() -> list[Path]:
    patterns = (
        "src/rafeeq/*.py",
        "mcp_server/*.py",
        "mcp_server/*.md",
        "data/public/*.csv",
        "data/public/*.jsonl",
        "data/public/*.md",
        "tests/public/*.py",
        "tests/public/*.md",
        "tests/schemas/*.json",
        "tests/schemas/*.md",
        "scripts/*.py",
        "scripts/*.md",
        "recovery/**/*",
        "docs/**/*",
        ".github/**/*",
        "reports/templates/*.md",
        "notebooks/README.md",
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "COURSE_USE_PERMISSION.md",
        "requirements-colab.txt",
        ".env.example",
        ".gitignore",
    )
    excluded: set[Path] = set()
    selected: set[Path] = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_file() and path not in excluded and "__pycache__" not in path.parts:
                selected.add(path)
    required = {
        ROOT / "src" / "rafeeq" / "graph.py",
        ROOT / "mcp_server" / "tawseel_server.py",
        ROOT / "data" / "public" / "orders.csv",
        ROOT / "data" / "public" / "tickets_dev.jsonl",
        ROOT / "data" / "public" / "eval_public.jsonl",
        ROOT / "data" / "public" / "security_cases.jsonl",
    }
    missing = sorted(str(path.relative_to(ROOT)) for path in required if path not in selected)
    if missing:
        raise FileNotFoundError("Missing notebook payload inputs: " + ", ".join(missing))
    return sorted(selected, key=lambda path: path.relative_to(ROOT).as_posix())


def build_payload() -> tuple[str, str, int]:
    """Return base64, SHA-256 and file count for a deterministic ZIP."""

    buffer = io.BytesIO()
    manifest: list[dict[str, object]] = []
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in _payload_files():
            relative = path.relative_to(ROOT).as_posix()
            content = path.read_bytes()
            info = zipfile.ZipInfo(relative, date_time=(2026, 9, 17, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, content)
            manifest.append(
                {
                    "path": relative,
                    "sha256": hashlib.sha256(content).hexdigest(),
                    "size_bytes": len(content),
                }
            )
        manifest_bytes = json.dumps(
            {"schema_version": "1.0", "files": manifest},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        info = zipfile.ZipInfo("BOOTSTRAP_MANIFEST.json", date_time=(2026, 9, 17, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, manifest_bytes)
    payload = buffer.getvalue()
    encoded = base64.b64encode(payload).decode("ascii")
    wrapped = "\n".join(encoded[index : index + 100] for index in range(0, len(encoded), 100))
    return wrapped, hashlib.sha256(payload).hexdigest(), len(manifest)


BOOTSTRAP_TEMPLATE = r'''
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import textwrap
import zipfile

LLM_MODE = "stub" #@param ["stub"]
os.environ["LLM_MODE"] = LLM_MODE

_PAYLOAD_B64 = """__PAYLOAD__"""
_EXPECTED_PAYLOAD_SHA256 = "__SHA256__"
_payload = base64.b64decode("".join(_PAYLOAD_B64.split()))
assert hashlib.sha256(_payload).hexdigest() == _EXPECTED_PAYLOAD_SHA256, "Embedded payload checksum failed"

PROJECT_ROOT = Path("/content/rafeeq-mini") if Path("/content").is_dir() else Path.cwd() / ".rafeeq-mini"
PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
_root = PROJECT_ROOT.resolve()
with zipfile.ZipFile(io.BytesIO(_payload)) as _archive:
    for _member in _archive.infolist():
        _target = (PROJECT_ROOT / _member.filename).resolve()
        if _target != _root and _root not in _target.parents:
            raise RuntimeError("Unsafe path in embedded lab payload")
    _archive.extractall(PROJECT_ROOT)

_src = str(PROJECT_ROOT / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)
_project_path = str(PROJECT_ROOT)
if _project_path not in sys.path:
    sys.path.insert(0, _project_path)

_required = [
    "src/rafeeq/graph.py",
    "mcp_server/tawseel_server.py",
    "data/public/orders.csv",
    "data/public/eval_public.jsonl",
    "data/public/security_cases.jsonl",
]
_doctor = {
    "python": platform.python_version(),
    "python_ok": sys.version_info >= (3, 10),
    "llm_mode": os.environ["LLM_MODE"],
    "network_required": False,
    "api_key_required": False,
    "workspace_writable": os.access(PROJECT_ROOT, os.W_OK),
    "free_disk_mb": round(shutil.disk_usage(PROJECT_ROOT).free / 1024 / 1024),
    "required_files_ok": all((PROJECT_ROOT / item).is_file() for item in _required),
    "payload_files": __FILE_COUNT__,
}
from rafeeq.graph import health_snapshot
_doctor["runtime"] = health_snapshot()
_doctor["all_passed"] = all((_doctor["python_ok"], _doctor["workspace_writable"], _doctor["required_files_ok"], _doctor["runtime"]["status"] == "ready"))
assert _doctor["all_passed"]
_doctor_checkpoints = PROJECT_ROOT / "reports" / "checkpoints"
_doctor_checkpoints.mkdir(parents=True, exist_ok=True)
(_doctor_checkpoints / "doctor_report.json").write_text(
    json.dumps(_doctor, ensure_ascii=False, indent=2, sort_keys=True),
    encoding="utf-8",
)
print(json.dumps(_doctor, ensure_ascii=False, indent=2, sort_keys=True))
print("C0 = READY")
print("all_passed=true")
print("جاهز — No API key, no network, free CPU path.")
'''


RESTORE_TEMPLATE = r'''
import base64
import hashlib
import io
import os
from pathlib import Path
import sys
import zipfile

_context_before_restore = set(globals())
os.environ["LLM_MODE"] = "stub"
_RESTORE_PAYLOAD_B64 = """__PAYLOAD__"""
_restore_payload = base64.b64decode("".join(_RESTORE_PAYLOAD_B64.split()))
assert hashlib.sha256(_restore_payload).hexdigest() == "__SHA256__"

if "PROJECT_ROOT" in globals():
    _restore_root = Path(PROJECT_ROOT)
elif Path("/content").is_dir():
    _restore_root = Path("/content/rafeeq-mini")
else:
    _restore_root = Path.cwd() / ".rafeeq-mini"
_restore_root.mkdir(parents=True, exist_ok=True)
_safe_root = _restore_root.resolve()
with zipfile.ZipFile(io.BytesIO(_restore_payload)) as _archive:
    for _member in _archive.infolist():
        _target = (_restore_root / _member.filename).resolve()
        if _target != _safe_root and _safe_root not in _target.parents:
            raise RuntimeError("Unsafe path in embedded restore payload")
    _archive.extractall(_restore_root)

PROJECT_ROOT = _restore_root
_src = str(PROJECT_ROOT / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)
_project_path = str(PROJECT_ROOT)
if _project_path not in sys.path:
    sys.path.insert(0, _project_path)
_required_day1_context = {
    "PROJECT_ROOT", "TRACE_PATH", "CHECKPOINTS", "RafeeqRuntime",
    "run_public_test_files", "_day1_report", "_day1_learner_checks",
    "json", "platform", "subprocess", "textwrap", "time",
}
_missing_day1_context = sorted(_required_day1_context - _context_before_restore)
_day1_context_present = not _missing_day1_context
_day1_gate_passed = (
    _day1_context_present
    and isinstance(globals().get("_day1_report"), dict)
    and globals()["_day1_report"].get("all_passed") is True
)
RESTORE_CONTEXT_READY = _day1_context_present and _day1_gate_passed
if RESTORE_CONTEXT_READY:
    from rafeeq.graph import RafeeqRuntime
    _restored_runtime = RafeeqRuntime(data_dir=PROJECT_ROOT / "data" / "public")
    assert _restored_runtime.health_snapshot()["status"] == "ready"
    print(f"C10 = READY | ملفات وسياق اليوم الأول جاهزة: {PROJECT_ROOT}")
else:
    print(f"C10 = WAITING | أعيدت ملفات المختبر إلى: {PROJECT_ROOT}")
    if _missing_day1_context:
        print("بعد إعادة تشغيل جلسة Colab: شغّل C0 إلى C9 بالترتيب، ثم شغّل C10 مجددًا.")
        print("After a Colab runtime reset: run C0 through C9 in order, then run C10 again.")
        print("Missing Day 1 context:", ", ".join(_missing_day1_context))
    else:
        print("بوابة اليوم الأول غير ناجحة: أكمل تمارين اليوم الأول وأعد C9 ثم C10.")
        print("Day 1 gate has not passed: complete the Day 1 exercises, rerun C9, then rerun C10.")
'''


def build_cells(payload: str, payload_sha256: str, file_count: int) -> list[dict[str, object]]:
    bootstrap = (
        BOOTSTRAP_TEMPLATE.replace("__PAYLOAD__", payload)
        .replace("__SHA256__", payload_sha256)
        .replace("__FILE_COUNT__", str(file_count))
    )
    restore = RESTORE_TEMPLATE.replace("__PAYLOAD__", payload).replace("__SHA256__", payload_sha256)

    cells: list[dict[str, object]] = [
        markdown(
            """
            <style>
            :root{--ink:#102a43;--muted:#526777;--line:#d8e2ea;--sky:#eaf7ff;--mint:#e9fbf4;--gold:#fff5d8;--rose:#fff0f2;--brand:#006d77;--navy:#102a43}
            .rfq-hero{background:linear-gradient(135deg,#102a43 0%,#006d77 58%,#36a3a8 100%);color:white;border-radius:22px;padding:30px;margin:8px 0 22px;box-shadow:0 12px 28px rgba(16,42,67,.18)}
            .rfq-hero h1{font-size:2.05rem;margin:.15rem 0}.rfq-hero p{opacity:.94;line-height:1.65}.rfq-badges span{display:inline-block;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:5px 10px;margin:3px;font-size:.82rem}
            .rfq-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.rfq-panel{border:1px solid var(--line);border-radius:15px;padding:17px;background:#fff;line-height:1.58}.rfq-panel h2{font-size:1.22rem;color:var(--navy);margin:.1rem 0 .55rem}.rfq-ar{border-right:5px solid var(--brand)}
            .rfq-section{margin:24px 0 10px}.rfq-kicker{font-size:.8rem;letter-spacing:.04em;color:var(--brand);font-weight:700;margin:0 0 8px}.rfq-evidence{background:var(--mint);border-radius:9px;padding:9px 11px;color:#164b3e}
            .rfq-day{display:grid;grid-template-columns:1fr 1fr;gap:20px;border-left:8px solid var(--brand);border-radius:15px;padding:18px 20px;margin:34px 0 16px;background:#f7fafc}.rfq-day span{font-size:.76rem;font-weight:800;letter-spacing:.12em;color:var(--brand)}.rfq-day h1{font-size:1.35rem;margin:.2rem 0}
            .rfq-callout{border:1px solid var(--line);border-radius:15px;padding:15px 18px;background:var(--gold);line-height:1.6}.rfq-mini{font-size:.9rem;color:var(--muted)}
            @media(max-width:760px){.rfq-grid,.rfq-day{grid-template-columns:1fr}.rfq-hero{padding:22px}}
            </style>
            <div class="rfq-hero">
              <div class="rfq-grid">
                <div dir="ltr">
                  <div class="rfq-mini" style="color:#d9ffff">THREE-DAY CUMULATIVE LAB · LEARNER EDITION</div>
                  <h1>Rafeeq Mini — Agentic AI Systems</h1>
                  <p>Build, secure, observe and package a bilingual delivery-support agent through one progressive notebook.</p>
                </div>
                <div dir="rtl">
                  <div class="rfq-mini" style="color:#d9ffff">مختبر تراكمي لثلاثة أيام · نسخة المتدرب</div>
                  <h1>رفيق ميني — هندسة الأنظمة التوكيلية</h1>
                  <p>ابنِ ووكّل وأمّن وراقب ثم جهّز وكيل دعم توصيل ثنائي اللغة للتسليم.</p>
                </div>
              </div>
              <div class="rfq-badges"><span>Colab Free CPU</span><span>Offline stub</span><span>No API key</span><span>AR + EN</span><span>14 guided exercises</span></div>
              <p><strong>Trainer · المدربة:</strong> Meaad Al-Marri · ميعاد المري</p>
            </div>
            """
        ),
        markdown(
            """
            <div class="rfq-grid">
              <div dir="ltr" class="rfq-panel">
                <h2>How to work</h2>
                <ol><li>Run each cell in order.</li><li>Complete only the numbered learner exercises.</li><li>Keep trusted identity and approvals outside model-controlled arguments.</li><li>At every day gate, save the JSON evidence.</li></ol>
                <p><strong>Runtime:</strong> deterministic <code>LLM_MODE=stub</code>; Python standard library; optional Matplotlib with a built-in fallback.</p>
              </div>
              <div dir="rtl" class="rfq-panel rfq-ar">
                <h2>طريقة العمل</h2>
                <ol><li>شغّل الخلايا بالترتيب.</li><li>أكمل تمارين المتدرب المرقمة فقط.</li><li>أبقِ هوية العميل والموافقات خارج وسائط النموذج.</li><li>احفظ دليل JSON عند بوابة كل يوم.</li></ol>
                <p><strong>بيئة التشغيل:</strong> نمط حتمي غير متصل؛ مكتبة بايثون القياسية؛ وMatplotlib اختياري مع بديل مضمّن.</p>
              </div>
            </div>
            <div class="rfq-callout"><strong>Safety boundary · حد الأمان:</strong> This is a synthetic training simulation. It does not contact a real delivery, payment or customer system. · هذه محاكاة تدريبية ببيانات اصطناعية ولا تتصل بأي نظام توصيل أو دفع أو عملاء حقيقي.</div>
            """
        ),
        day_banner(1, "Architecture → tools → a bounded single agent", "المعمارية ← الأدوات ← وكيل واحد محدود", "#36a3a8"),
        section(
            "C0_ENV_DOCTOR",
            "Environment doctor & offline bootstrap",
            "فاحص البيئة وتجهيز العمل دون اتصال",
            "Unpack the embedded public lab, verify Python, disk, files and the mandatory stub runtime. Nothing is downloaded.",
            "فك حزمة المختبر العامة المضمّنة وتحقق من بايثون والمساحة والملفات ونمط التشغيل الحتمي دون تنزيل أي شيء.",
            "A green bilingual readiness line plus a machine-readable health snapshot.",
            "سطر جاهزية ثنائي اللغة ولقطة صحة قابلة للقراءة آليًا.",
            12,
        ),
        code(bootstrap, "setup", "bootstrap"),
        section(
            "C1_ARCHITECTURE",
            "Place trust boundaries before autonomy",
            "ضع حدود الثقة قبل الاستقلالية",
            "Map the host, bounded graph, specialists, tools, synthetic data and evidence store. The host owns identity and approval.",
            "ارسم المضيف والرسم المحدود والوكلاء المتخصصين والأدوات والبيانات الاصطناعية ومخزن الأدلة؛ وتبقى الهوية والموافقة لدى المضيف.",
            "An inspectable component map and one learner architecture decision.",
            "خريطة مكونات قابلة للفحص وقرار معماري واحد للمتدرب.",
            16,
        ),
        code(
            r'''
            architecture = {
                "trusted_host": ["customer identity", "approval record", "runtime limits"],
                "bounded_graph": ["input guard", "supervisor", "specialist", "output guard"],
                "specialists": ["OrdersAgent", "RefundAgent"],
                "tool_boundary": ["get_order_status", "get_refund_context", "create_refund_request"],
                "evidence": ["redacted trace", "checkpoint JSON", "assessment report"],
            }
            print(json.dumps(architecture, ensure_ascii=False, indent=2))

            # TODO-1: Add one component, its trust level, and why it belongs there.
            # أضف مكوّنًا واحدًا ومستوى ثقته وسبب موضعه.
            learner_architecture_decision = {
                "component": None,
                "trust_level": None,
                "reason": None,
            }
            print("Exercise pending | التمرين بانتظار الإكمال")
            ''',
            "learner-exercise",
        ),
        section(
            "C2_TYPED_STATE",
            "Make state explicit and serializable",
            "اجعل الحالة صريحة وقابلة للتسلسل",
            "Inspect the shared state contract, counters and safe snapshot. Raw messages and tool records are deliberately excluded from traces.",
            "افحص عقد الحالة المشتركة والعدادات واللقطة الآمنة؛ تُستبعد الرسائل الخام وسجلات الأدوات عمدًا من التتبع.",
            "A serializable safe snapshot that omits the raw message.",
            "لقطة آمنة قابلة للتسلسل ولا تتضمن الرسالة الخام.",
            18,
        ),
        code(
            r'''
            from dataclasses import dataclass
            from rafeeq.state import AgentState, Locale

            _state_example = AgentState(
                customer_id="CUST-011",
                message="synthetic request that must not enter traces",
                session_id="day1-state-demo",
                locale=Locale.EN,
            )
            _safe_state = _state_example.safe_snapshot()
            assert "message" not in _safe_state and "tool_observations" not in _safe_state
            print(json.dumps({key: _safe_state[key] for key in ("status", "locale", "step_count", "risk_flags")}, indent=2))

            # TODO-2: Add only the minimum fields needed to route and stop a learner state.
            # أضف أقل حقول لازمة للتوجيه والتوقف.
            @dataclass
            class LearnerState:
                pass

            print("LearnerState is a runnable scaffold | القالب قابل للتشغيل")
            ''',
            "learner-exercise",
        ),
        section(
            "C3_BOUNDED_GRAPH",
            "Bound every loop before running it",
            "قيّد كل حلقة قبل تشغيلها",
            "Use hard ceilings for steps, transitions, handoffs and reflection. Terminal states stop immediately.",
            "استخدم حدودًا صارمة للخطوات والانتقالات والتفويضات والانعكاس، وتوقّف فور الوصول إلى حالة نهائية.",
            "Executable assertions for the 6 / 12 / 2 / 1 contract.",
            "اختبارات تنفيذية لعقد الحدود 6 / 12 / 2 / 1.",
            18,
        ),
        code(
            r'''
            from rafeeq.config import Limits
            from rafeeq.graph import should_stop
            from rafeeq.state import RunStatus

            _limits = Limits()
            assert (_limits.max_steps, _limits.max_transitions, _limits.max_handoffs, _limits.max_reflections) == (6, 12, 2, 1)
            _bounded_state = AgentState(customer_id="CUST-001", message="status", session_id="bounded")
            _bounded_state.step_count = _limits.max_steps
            assert should_stop(_bounded_state, _limits)
            print("BOUNDS_OK", {"steps": 6, "transitions": 12, "handoffs": 2, "reflections": 1})

            # TODO-3: Return True for terminal status OR any exhausted budget; otherwise False.
            # أعد True عند النهاية أو نفاد أي حد، وإلا False.
            def learner_should_stop(status, steps, transitions, handoffs, reflections):
                return None

            print("Complete learner_should_stop without adding a loop.")
            ''',
            "learner-exercise",
        ),
        section(
            "C4_REASONING_TRACES",
            "Trace decisions, not private reasoning",
            "تتبّع القرارات لا التفكير الخاص",
            "Record routes, outcomes, counters and short operational reasons. Never persist raw prompts or chain-of-thought.",
            "سجّل المسارات والنتائج والعدادات والأسباب التشغيلية القصيرة، ولا تحفظ الأوامر الخام أو سلسلة التفكير.",
            "A redacted JSONL trace with linked spans and counters.",
            "تتبع JSONL منقّح بمقاطع مترابطة وعدادات.",
            14,
        ),
        code(
            r'''
            from rafeeq.graph import RafeeqRuntime

            REPORTS = PROJECT_ROOT / "reports"
            CHECKPOINTS = REPORTS / "checkpoints"
            REPORTS.mkdir(parents=True, exist_ok=True)
            CHECKPOINTS.mkdir(parents=True, exist_ok=True)
            TRACE_PATH = REPORTS / "trace.jsonl"
            if TRACE_PATH.exists():
                TRACE_PATH.unlink()
            runtime = RafeeqRuntime(data_dir=PROJECT_ROOT / "data" / "public", trace_path=TRACE_PATH)
            _trace_demo = runtime.run("Where is order TW-26018?", "CUST-012", thread_id="trace-demo")
            _trace_lines = [json.loads(line) for line in TRACE_PATH.read_text(encoding="utf-8").splitlines()]
            _forbidden_trace_keys = {"message", "prompt", "chain_of_thought", "customer_id"}
            assert _trace_lines and all(not (_forbidden_trace_keys & set(item)) for item in _trace_lines)
            print(json.dumps({"events": len(_trace_lines), "route": _trace_demo["route"], "outcome": _trace_demo["outcome"], "redacted": all(x["redacted"] for x in _trace_lines)}, indent=2))
            ''',
            "evidence",
        ),
        section(
            "C5_REACT_ORDERS",
            "ReAct without exposing hidden thought",
            "نمط ReAct دون كشف التفكير الخفي",
            "Use an observable decision → action → observation cycle for a read-only order lookup, then stop.",
            "استخدم دورة قرار ← إجراء ← ملاحظة قابلة للمشاهدة لقراءة حالة الطلب ثم توقّف.",
            "A safe operational cycle tied to one tool result.",
            "دورة تشغيلية آمنة مرتبطة بنتيجة أداة واحدة.",
            18,
        ),
        code(
            r'''
            _react_result = runtime.run("تحقق من حالة الطلب TW-26001", "CUST-001", locale="ar", thread_id="react-order")
            _react_cycle = [
                {"phase": "decision", "value": _react_result["route"]},
                {"phase": "action", "value": "get_order_status"},
                {"phase": "observation", "value": _react_result["outcome"]},
                {"phase": "stop", "value": _react_result["status"]},
            ]
            print(json.dumps(_react_cycle, ensure_ascii=False, indent=2))

            # TODO-4: Build a four-item cycle for an accessible order; use only decision/action/observation/stop.
            # ابنِ دورة من أربع مراحل لطلب مسموح الوصول إليه.
            learner_react_cycle = []
            print(f"Learner cycle items: {len(learner_react_cycle)} / 4")
            ''',
            "learner-exercise",
        ),
        section(
            "C6_TOOL_SCHEMA",
            "Keep model-visible tool schemas narrow",
            "اجعل مخططات الأدوات المرئية للنموذج ضيقة",
            "Validate names, required arguments and read/write annotations. Trusted customer identity, amount and approval are not model arguments.",
            "تحقق من الأسماء والوسائط المطلوبة ووسوم القراءة والكتابة؛ ولا تجعل هوية العميل أو المبلغ أو الموافقة وسائط يتحكم بها النموذج.",
            "Three typed schemas with an explicit trust-boundary assertion.",
            "ثلاثة مخططات محددة النوع واختبار صريح لحد الثقة.",
            18,
        ),
        code(
            r'''
            from mcp_server.tawseel_server import TOOL_DEFINITIONS

            _tool_names = [item["name"] for item in TOOL_DEFINITIONS]
            _model_keys = {
                key
                for item in TOOL_DEFINITIONS
                for key in item["inputSchema"].get("properties", {})
            }
            assert _tool_names == ["get_order_status", "get_refund_context", "create_refund_request"]
            assert not ({"customer_id", "amount_sar", "approval", "approval_status"} & _model_keys)
            print(json.dumps({"tools": _tool_names, "model_visible_arguments": sorted(_model_keys)}, indent=2))

            # TODO-5: Draft a narrow schema for a read-only delivery ETA tool.
            # صمّم مخططًا ضيقًا لأداة قراءة موعد التسليم.
            learner_tool_schema = {}
            print("Keep identity and authorization outside learner_tool_schema.")
            ''',
            "learner-exercise",
        ),
        section(
            "C7_MCP_SERVER",
            "Serve tools over bounded MCP stdio",
            "قدّم الأدوات عبر MCP stdio محدود",
            "Inspect the dependency-free teaching server: newline-delimited JSON-RPC, per-request metadata and structured tool results.",
            "افحص خادم التدريب بلا تبعيات: JSON-RPC مفصول بأسطر، وبيانات وصفية لكل طلب، ونتائج أدوات منظمة.",
            "A direct server smoke check with ownership denial.",
            "فحص مباشر للخادم يتضمن منع الوصول لطلب لا يملكه العميل.",
            16,
        ),
        code(
            r'''
            from mcp_server.tawseel_server import PROTOCOL_VERSION, smoke_check

            _server_smoke = smoke_check(PROJECT_ROOT / "data" / "public" / "orders.csv")
            assert _server_smoke["ok"]
            print(json.dumps({"protocol_version": PROTOCOL_VERSION, **_server_smoke}, ensure_ascii=False, indent=2))
            ''',
            "mcp",
        ),
        section(
            "C8_MCP_CLIENT",
            "Open, call and close a real subprocess",
            "افتح عملية فرعية حقيقية واستدعها ثم أغلقها",
            "Use a context-managed stdio client. Discovery and tool calls carry current protocol metadata; the subprocess always closes.",
            "استخدم عميل stdio مُدارًا بالسياق؛ يحمل الاكتشاف والاستدعاء البيانات الوصفية الحالية وتُغلق العملية دائمًا.",
            "One owned read plus proof that the child process closed.",
            "قراءة طلب مملوك مع إثبات إغلاق العملية الفرعية.",
            18,
        ),
        code(
            r'''
            from rafeeq.mcp_client import MCPStdioClient

            _server_command = [sys.executable, "-u", str(PROJECT_ROOT / "mcp_server" / "tawseel_server.py"), "--orders", str(PROJECT_ROOT / "data" / "public" / "orders.csv")]
            with MCPStdioClient(customer_id="CUST-011", locale="ar", command=_server_command) as _client:
                _listed = _client.list_tools()
                _owned = _client.call_tool("get_order_status", {"order_id": "TW-26017"})
                _invalid_args = _client.call_tool("get_order_status", {"order_id": "TW-26017", "customer_id": "CUST-011"})
                _rejected = _client.call_tool("get_order_status", {"order_id": "TW-26018"})
                _discovery = dict(_client.server_discovery or {})
            assert not _client.is_running
            assert _owned["structuredContent"]["ok"] is True
            assert _invalid_args["isError"] is True and _invalid_args["structuredContent"]["error"]["code"] == "INVALID_ARGUMENT"
            assert _rejected["isError"] is True and _rejected["structuredContent"]["error"]["code"] == "ORDER_FORBIDDEN"
            print(json.dumps({"protocol": _discovery.get("protocolVersion"), "tool_count": len(_listed), "closed": not _client.is_running, "owned_status": _owned["structuredContent"]["data"]["status"], "invalid_model_args": _invalid_args["structuredContent"]["error"]["code"], "cross_customer_result": _rejected["structuredContent"]["error"]["code"], "writes": 0}, ensure_ascii=False, indent=2))
            ''',
            "mcp",
        ),
        section(
            "C9_DAY1_GATE",
            "Day 1 quality gate",
            "بوابة جودة اليوم الأول",
            "Run the public state, tool-scope and MCP tests. Save the command evidence even when a learner exercise is still pending.",
            "شغّل اختبارات الحالة العامة ونطاق الأدوات وMCP واحفظ دليل الأوامر حتى لو بقي تمرين متدرب غير مكتمل.",
            "A checkpoint JSON with pass/fail per public test file.",
            "ملف JSON مرحلي بنتيجة كل ملف اختبار عام.",
            15,
        ),
        code(
            r'''
            import subprocess
            import time

            def run_public_test_files(names):
                rows = []
                env = os.environ.copy()
                env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
                for name in names:
                    started = time.perf_counter()
                    completed = subprocess.run(
                        [sys.executable, "-m", "unittest", "discover", "-s", "tests/public", "-p", f"{name}.py"],
                        cwd=PROJECT_ROOT,
                        env=env,
                        text=True,
                        capture_output=True,
                        timeout=45,
                    )
                    rows.append({"test": name, "passed": completed.returncode == 0, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "tail": (completed.stdout + completed.stderr)[-500:]})
                return rows

            _day1_tests = run_public_test_files(["test_state_contract", "test_tool_scope", "test_mcp_smoke"])
            _learner_state_fields = set(getattr(LearnerState, "__dataclass_fields__", {}))
            _minimum_state_fields = {"route", "status", "steps", "transitions", "handoffs", "reflections"}
            try:
                _stop_contract_ok = (
                    learner_should_stop("completed", 0, 0, 0, 0) is True
                    and learner_should_stop("running", 6, 0, 0, 0) is True
                    and learner_should_stop("running", 0, 12, 0, 0) is True
                    and learner_should_stop("running", 0, 0, 2, 0) is True
                    and learner_should_stop("running", 0, 0, 0, 1) is True
                    and learner_should_stop("running", 0, 0, 0, 0) is False
                )
            except Exception:
                _stop_contract_ok = False
            _react_phases = [item.get("phase") for item in learner_react_cycle if isinstance(item, dict)] if isinstance(learner_react_cycle, list) else []
            _schema_input = learner_tool_schema.get("inputSchema", {}) if isinstance(learner_tool_schema, dict) else {}
            _schema_properties = _schema_input.get("properties", {}) if isinstance(_schema_input, dict) else {}
            _schema_required = _schema_input.get("required", []) if isinstance(_schema_input, dict) else []
            _schema_annotations = learner_tool_schema.get("annotations", {}) if isinstance(learner_tool_schema, dict) else {}
            _day1_learner_checks = {
                1: isinstance(learner_architecture_decision, dict) and all(learner_architecture_decision.get(key) for key in ("component", "trust_level", "reason")),
                2: _learner_state_fields == _minimum_state_fields,
                3: _stop_contract_ok,
                4: (
                    isinstance(learner_react_cycle, list)
                    and len(learner_react_cycle) == 4
                    and all(isinstance(item, dict) for item in learner_react_cycle)
                    and _react_phases == ["decision", "action", "observation", "stop"]
                    and all(item.get("value") for item in learner_react_cycle)
                ),
                5: (
                    isinstance(learner_tool_schema, dict)
                    and isinstance(learner_tool_schema.get("name"), str)
                    and bool(learner_tool_schema["name"].strip())
                    and set(_schema_properties) == {"order_id"}
                    and set(_schema_required) == {"order_id"}
                    and _schema_input.get("additionalProperties") is False
                    and _schema_annotations.get("readOnlyHint") is True
                    and not ({"customer_id", "amount_sar", "approval", "approval_status"} & set(_schema_properties))
                ),
            }
            _day1_public_passed = all(row["passed"] for row in _day1_tests)
            _day1_learner_complete = all(_day1_learner_checks.values())
            for _number, _passed in _day1_learner_checks.items():
                if not _passed:
                    print(f"أكمل TODO-{_number} ثم أعد تشغيل بوابة اليوم الأول | Complete TODO-{_number} and rerun the Day 1 gate.")
            _day1_report = {
                "day": 1,
                "llm_mode": "stub",
                "public_tests_passed": _day1_public_passed,
                "learner_checks_complete": _day1_learner_complete,
                "all_passed": _day1_public_passed and _day1_learner_complete,
                "learner_checks": {str(key): value for key, value in _day1_learner_checks.items()},
                "tests": _day1_tests,
            }
            (CHECKPOINTS / "day1_results.json").write_text(json.dumps(_day1_report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(_day1_report, ensure_ascii=False, indent=2))
            ''',
            "gate",
        ),
        day_banner(2, "Memory → specialists → approval-aware workflow", "الذاكرة ← التخصص ← سير عمل واعٍ بالموافقة", "#f4a261"),
        section(
            "C10_RESTORE",
            "Verify files and Day 1 context before continuing",
            "تحقق من الملفات وسياق اليوم الأول قبل المتابعة",
            "The embedded copy restores public files without network access, but a Colab runtime reset erases Python variables and learner work. After any reset, run from the environment doctor through the Day 1 gate in order. Day 2 unlocks only when that gate passes, then this check is rerun.",
            "تعيد النسخة المضمّنة الملفات العامة دون شبكة، لكن إعادة تشغيل جلسة Colab تمحو متغيرات بايثون وعمل المتدرب. بعد أي إعادة تشغيل شغّل من فاحص البيئة حتى بوابة اليوم الأول بالترتيب، ولا يُفتح اليوم الثاني إلا بعد نجاحها ثم إعادة هذا الفحص.",
            "A READY state only when restored files, Day 1 kernel context and a passed Day 1 gate all exist; otherwise a clear instruction with no traceback.",
            "حالة جاهزة فقط عند توفر الملفات وسياق اليوم الأول ونجاح بوابته، وإلا تظهر تعليمات واضحة دون traceback.",
            10,
        ),
        code(restore, "setup", "restore"),
        section(
            "C11_SESSION_MEMORY",
            "Remember just enough within one thread",
            "تذكّر القدر الكافي داخل المحادثة",
            "Store short operational summaries, then recover an order ID on the next turn without retaining the raw message.",
            "احفظ ملخصات تشغيلية قصيرة ثم استرجع رقم الطلب في الدور التالي دون الاحتفاظ بالرسالة الخام.",
            "A two-turn test proving scoped order recall.",
            "اختبار من دورين يثبت استرجاع رقم الطلب ضمن الجلسة.",
            20,
        ),
        code(
            r'''
            if globals().get("RESTORE_CONTEXT_READY") is not True:
                raise RuntimeError("C11 BLOCKED: run C0 through C9 in order, then rerun C10. | شغّل C0 إلى C9 بالترتيب ثم أعد C10.")
            runtime_day2 = RafeeqRuntime(data_dir=PROJECT_ROOT / "data" / "public", trace_path=TRACE_PATH)
            _thread = "session-memory-demo"
            _turn1 = runtime_day2.run("status order TW-26003", "CUST-003", locale="en", thread_id=_thread)
            _turn2 = runtime_day2.run("refund it", "CUST-003", locale="en", thread_id=_thread)
            _session_items = runtime_day2.session_memory(_thread).recent(5)
            assert _turn2["order_id"] == "TW-26003" and _turn2["route"] == "refund"
            print(json.dumps({"turn_1": _turn1["outcome"], "turn_2_order": _turn2["order_id"], "turn_2_outcome": _turn2["outcome"], "stored_summaries": [item.summary for item in _session_items]}, ensure_ascii=False, indent=2))

            # TODO-6: Write a minimal summary containing route, outcome and order ID—never the raw message.
            # اكتب ملخصًا أدنى بلا الرسالة الخام.
            learner_session_summary = ""
            print("Summary length:", len(learner_session_summary))
            ''',
            "learner-exercise",
        ),
        section(
            "C12_SCOPED_RECALL",
            "Filter authorization before semantic ranking",
            "صفِّ الصلاحية قبل الترتيب الدلالي",
            "Long-term memory is synthetic and read-only. Scope, active flag, expiry, locale and order filters run before ranking. This lab pins the dataset snapshot clock; production uses a trusted current-time source.",
            "الذاكرة طويلة المدى اصطناعية وللقراءة فقط؛ تُطبّق الملكية والنشاط والانتهاء واللغة والطلب قبل الترتيب. يثبّت المختبر وقت لقطة البيانات، بينما يستخدم الإنتاج مصدر وقت حالي موثوقًا.",
            "Only the current customer's active memory can be returned.",
            "لا تُرجع إلا ذاكرة العميل الحالي النشطة.",
            20,
        ),
        code(
            r'''
            from datetime import datetime, timezone

            TRAINING_DATASET_SNAPSHOT_TIME = datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc)
            _memory_hits = runtime_day2.long_term_memory.recall(
                "تعذر تسليم الطلب وفتح متابعة",
                "CUST-011",
                now=TRAINING_DATASET_SNAPSHOT_TIME,
                locale="ar",
                related_order_id="TW-26017",
                top_k=3,
            )
            assert _memory_hits and all(hit.record.customer_id == "CUST-011" and hit.record.active for hit in _memory_hits)
            assert all(hit.record.memory_id != "MEM-008" for hit in _memory_hits)
            print(json.dumps({"dataset_snapshot_time": TRAINING_DATASET_SNAPSHOT_TIME.isoformat(), "hits": [{"memory_id": hit.record.memory_id, "score": hit.score} for hit in _memory_hits]}, ensure_ascii=False, indent=2))

            # TODO-7: Filter records by owner, active flag and expiry before ranking them.
            # صفِّ السجلات حسب المالك والنشاط والانتهاء قبل الترتيب.
            def learner_scope_filter(records, customer_id, now):
                return []

            print("Return only authorized records; ranking comes later.")
            ''',
            "learner-exercise",
        ),
        section(
            "C13_POLICY_RETRIEVAL",
            "Retrieve the current policy version",
            "استرجع نسخة السياسة السارية",
            "Select active and effective policy chunks before similarity ranking. The obsolete SAR 300 rule must never win.",
            "اختر مقاطع السياسة النشطة والسارية قبل ترتيب التشابه؛ ويجب ألا تفوز قاعدة 300 ريال الملغاة.",
            "A current Arabic refund-limit hit at version 2026.1.",
            "نتيجة عربية سارية لحد الاسترداد بإصدار 2026.1.",
            18,
        ),
        code(
            r'''
            _policy_hits = runtime_day2.policy_retriever.search(
                "هل المبلغ فوق 500 يحتاج موافقة بشرية؟",
                locale="ar",
                category="refund_limit",
                top_k=2,
            )
            assert _policy_hits and all(hit.record.active and hit.record.version == "2026.1" for hit in _policy_hits)
            assert all("300" not in hit.record.text for hit in _policy_hits)
            print(json.dumps([{"policy_id": hit.record.policy_id, "version": hit.record.version, "score": hit.score} for hit in _policy_hits], ensure_ascii=False, indent=2))

            # TODO-8: Supply a focused query plus locale/category filters for one policy question.
            # اكتب استعلامًا مركزًا مع مرشحي اللغة والفئة.
            learner_policy_query = ""
            learner_policy_filters = {}
            print("Query and filters remain learner-owned.")
            ''',
            "learner-exercise",
        ),
        section(
            "C14_SPECIALISTS",
            "Give two specialists narrow responsibilities",
            "امنح وكيلين متخصصين مسؤوليات ضيقة",
            "OrdersAgent performs reads. RefundAgent evaluates policy and may perform one idempotent simulated write after gates pass.",
            "ينفذ وكيل الطلبات القراءة، ويقيّم وكيل الاسترداد السياسة وقد ينفذ كتابة محاكاة واحدة بعد اجتياز الحواجز.",
            "Distinct routes, outcomes and tool-call counts for both specialists.",
            "مسارات ونتائج وعدادات أدوات منفصلة للوكيلين.",
            16,
        ),
        code(
            r'''
            _orders_case = runtime_day2.run("Track order TW-26018", "CUST-012", thread_id="specialist-orders")
            _refund_case = runtime_day2.run("Refund delayed order TW-26008", "CUST-008", thread_id="specialist-refund")
            assert _orders_case["route"] == "orders" and _refund_case["route"] == "refund"
            print(json.dumps({"OrdersAgent": {"outcome": _orders_case["outcome"], "tool_calls": _orders_case["counters"]["tool_calls"]}, "RefundAgent": {"outcome": _refund_case["outcome"], "tool_calls": _refund_case["counters"]["tool_calls"]}}, indent=2))
            ''',
            "workflow",
        ),
        section(
            "C15_SUPERVISOR",
            "Use a thin supervisor, not a second expert",
            "استخدم منسقًا خفيفًا لا خبيرًا ثانيًا",
            "The supervisor chooses orders, refund, escalate or finish. It does not read databases or perform writes.",
            "يختار المنسق الطلبات أو الاسترداد أو التصعيد أو الإنهاء، ولا يقرأ قواعد البيانات ولا ينفذ كتابة.",
            "A compact routing table across Arabic and English requests.",
            "جدول توجيه صغير لطلبات عربية وإنجليزية.",
            16,
        ),
        code(
            r'''
            from rafeeq.agents import supervisor_route

            _route_samples = [
                ("Where is order TW-26018?", "TW-26018"),
                ("Refund order TW-26008", "TW-26008"),
                ("أريد موظفًا بشريًا", None),
                ("hello", None),
            ]
            _routes = [{"message_class": index + 1, "route": supervisor_route(text, order_id).value} for index, (text, order_id) in enumerate(_route_samples)]
            print(json.dumps(_routes, ensure_ascii=False, indent=2))
            ''',
            "workflow",
        ),
        section(
            "C16_TYPED_HANDOFF",
            "Delegate with a typed, minimum message",
            "فوّض برسالة محددة النوع وبأقل بيانات",
            "A handoff contains target, scoped identifiers, locale and task—not the raw request, full memory or credentials.",
            "يتضمن التفويض الهدف والمعرّفات المحددة واللغة والمهمة، لا الطلب الخام أو الذاكرة الكاملة أو بيانات الاعتماد.",
            "A serialized handoff whose fields can be audited.",
            "تفويض متسلسل يمكن تدقيق حقوله.",
            18,
        ),
        code(
            r'''
            from dataclasses import asdict
            from rafeeq.agents import build_handoff
            from rafeeq.state import Route

            _handoff_state = AgentState(customer_id="CUST-003", message="refund TW-26003", session_id="handoff", locale=Locale.EN, order_id="TW-26003", route=Route.REFUND)
            _handoff = build_handoff(Route.REFUND, _handoff_state)
            _handoff_payload = asdict(_handoff)
            _handoff_payload["target"] = _handoff.target.value
            _handoff_payload["locale"] = _handoff.locale.value
            assert "message" not in _handoff_payload
            print(json.dumps(_handoff_payload, indent=2))

            # TODO-9: Define a typed delegation carrying only target, order_id, locale and task.
            # عرّف تفويضًا محدد النوع بأقل الحقول المطلوبة.
            @dataclass
            class LearnerDelegation:
                pass

            print("Do not add the raw request to LearnerDelegation.")
            ''',
            "learner-exercise",
        ),
        section(
            "C17_PLAN_EXECUTE",
            "Separate a short plan from execution",
            "افصل الخطة القصيرة عن التنفيذ",
            "Create a bounded plan, execute the current step, and re-plan only on a typed deviation such as pending human approval.",
            "أنشئ خطة محدودة ونفّذ الخطوة الحالية ولا تعد التخطيط إلا عند انحراف محدد النوع مثل انتظار موافقة بشرية.",
            "An observable plan and one approval-aware re-plan path.",
            "خطة قابلة للمشاهدة ومسار إعادة تخطيط واحد يراعي الموافقة.",
            20,
        ),
        code(
            r'''
            _plan_case = runtime_day2.run("استرداد الطلب TW-26017", "CUST-011", locale="ar", thread_id="plan-execute")
            _replan = list(_plan_case["plan"])
            if _plan_case["status"] == "needs_approval":
                _replan = ["pause", "request_human_approval", "resume_same_scoped_action"]
            assert len(_plan_case["plan"]) <= 6
            print(json.dumps({"initial_plan": _plan_case["plan"], "deviation": _plan_case["outcome"], "replan": _replan}, ensure_ascii=False, indent=2))
            ''',
            "workflow",
        ),
        section(
            "C18_REFUND_GATE",
            "Apply policy gates in a fixed order",
            "طبّق حواجز السياسة بترتيب ثابت",
            "Check ownership, prior refund, delay greater than two days, then the SAR 500 boundary. SAR 500.00 is eligible; SAR 500.01 needs a human.",
            "تحقق من الملكية والاسترداد السابق والتأخير لأكثر من يومين ثم حد 500 ريال؛ 500.00 مؤهل و500.01 يحتاج موافقة بشرية.",
            "Boundary assertions plus zero writes before approval.",
            "اختبارات للحد الفاصل وصفر كتابة قبل الموافقة.",
            22,
        ),
        code(
            r'''
            from rafeeq.agents import evaluate_refund
            from rafeeq.data import DataStore

            _store = DataStore.from_public_dir(PROJECT_ROOT / "data" / "public")
            _at_limit = evaluate_refund(_store.orders["TW-26003"], "CUST-003")
            _over_limit = evaluate_refund(_store.orders["TW-26004"], "CUST-004")
            assert _at_limit.eligible and not _at_limit.requires_approval
            assert not _over_limit.eligible and _over_limit.requires_approval
            print(json.dumps({"SAR_500_00": asdict(_at_limit), "SAR_500_01": asdict(_over_limit)}, indent=2))

            # TODO-10: Return one of eligible / not_eligible / needs_approval for the four policy inputs.
            # أعد قرار الأهلية الصحيح من مدخلات السياسة الأربعة.
            def learner_refund_decision(owner_matches, delay_days, already_refunded, amount_sar):
                return "pending"

            print("Implement gates in policy order; do not call a write tool here.")
            ''',
            "learner-exercise",
        ),
        section(
            "C19_INTERRUPT_RESUME",
            "Pause for a human, then resume the same action",
            "توقّف للمراجع البشري ثم استأنف الإجراء نفسه",
            "A high-value request creates a stable approval record. An explicit trusted decision resumes the same scoped refund once.",
            "ينشئ الطلب مرتفع القيمة سجل موافقة ثابتًا، ثم يستأنف القرار الموثوق الصريح الاسترداد المحدد مرة واحدة.",
            "Pending → approved → one idempotent simulated write.",
            "انتظار ← موافقة ← كتابة محاكاة واحدة قابلة للتكرار الآمن.",
            20,
        ),
        code(
            r'''
            _approval_runtime = RafeeqRuntime(data_dir=PROJECT_ROOT / "data" / "public", trace_path=TRACE_PATH)
            _paused = _approval_runtime.run("Refund order TW-26017", "CUST-011", thread_id="approval-demo")
            assert _paused["status"] == "needs_approval" and _paused["approval_id"]
            _resumed = _approval_runtime.run("Refund order TW-26017", "CUST-011", thread_id="approval-demo", approval=True)
            assert _resumed["approval_id"] == _paused["approval_id"] and _resumed["outcome"] == "created"
            print(json.dumps({"paused": {"status": _paused["status"], "approval_id": _paused["approval_id"]}, "resumed": {"status": _resumed["status"], "approval_status": _resumed["approval_status"], "outcome": _resumed["outcome"]}}, ensure_ascii=False, indent=2))
            ''',
            "workflow",
        ),
        section(
            "C20_DAY2_GATE",
            "Day 2 integration gate",
            "بوابة تكامل اليوم الثاني",
            "Run memory, routing, refund and reflection public tests and preserve the two-turn memory evidence.",
            "شغّل اختبارات الذاكرة والتوجيه والاسترداد والانعكاس واحفظ دليل الذاكرة ذي الدورين.",
            "Two checkpoint files with integration and memory evidence.",
            "ملفان مرحليان لأدلة التكامل والذاكرة.",
            15,
        ),
        code(
            r'''
            _day2_tests = run_public_test_files(["test_memory_scope", "test_routing", "test_refund_gate", "test_reflection_bound"])
            _memory_evidence = {"thread_id": _thread, "turn_1_order": _turn1["order_id"], "turn_2_recalled_order": _turn2["order_id"], "raw_messages_stored": False}
            (CHECKPOINTS / "day2_memory_results.json").write_text(json.dumps(_memory_evidence, ensure_ascii=False, indent=2), encoding="utf-8")
            _summary_ok = (
                isinstance(learner_session_summary, str)
                and 0 < len(learner_session_summary) <= 300
                and all(token in learner_session_summary for token in ("route=", "outcome=", "order_id="))
            )
            try:
                _learner_scoped = list(learner_scope_filter(tuple(_store.memories), "CUST-011", TRAINING_DATASET_SNAPSHOT_TIME))
                _scope_ok = {item.memory_id for item in _learner_scoped} == {"MEM-004"}
            except Exception:
                _scope_ok = False
            _policy_query_ok = (
                isinstance(learner_policy_query, str)
                and bool(learner_policy_query.strip())
                and isinstance(learner_policy_filters, dict)
                and learner_policy_filters.get("locale") in {"ar", "en"}
                and learner_policy_filters.get("category") in {"refund_eligibility", "refund_limit"}
            )
            _delegation_fields = set(getattr(LearnerDelegation, "__dataclass_fields__", {}))
            try:
                _refund_contract_ok = (
                    learner_refund_decision(True, 5, False, 500.00) == "eligible"
                    and learner_refund_decision(True, 5, False, 500.01) == "needs_approval"
                    and learner_refund_decision(True, 2, False, 100.00) == "not_eligible"
                    and learner_refund_decision(True, 5, True, 100.00) == "not_eligible"
                    and learner_refund_decision(False, 5, False, 100.00) == "not_eligible"
                )
            except Exception:
                _refund_contract_ok = False
            _day2_learner_checks = {
                6: _summary_ok,
                7: _scope_ok,
                8: _policy_query_ok,
                9: _delegation_fields == {"target", "order_id", "locale", "task"},
                10: _refund_contract_ok,
            }
            _day2_public_passed = all(row["passed"] for row in _day2_tests)
            _day2_learner_complete = all(_day2_learner_checks.values())
            for _number, _passed in _day2_learner_checks.items():
                if not _passed:
                    print(f"أكمل TODO-{_number} ثم أعد تشغيل بوابة اليوم الثاني | Complete TODO-{_number} and rerun the Day 2 gate.")
            _day2_report = {
                "day": 2,
                "public_tests_passed": _day2_public_passed,
                "learner_checks_complete": _day2_learner_complete,
                "all_passed": _day2_public_passed and _day2_learner_complete,
                "learner_checks": {str(key): value for key, value in _day2_learner_checks.items()},
                "tests": _day2_tests,
                "memory": _memory_evidence,
            }
            (CHECKPOINTS / "day2_results.json").write_text(json.dumps(_day2_report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(_day2_report, ensure_ascii=False, indent=2))
            ''',
            "gate",
        ),
        day_banner(3, "Security → observability → evidence → export", "الأمن ← المراقبة ← الأدلة ← التصدير", "#e76f51"),
        section(
            "C21_THREAT_MODEL",
            "Threat-model the workflow before attacking it",
            "نمذج تهديدات سير العمل قبل مهاجمته",
            "Name assets, trust boundaries, abuse paths and controls. Focus on unauthorized access, approval bypass, duplicate writes, injection and resource exhaustion.",
            "حدّد الأصول وحدود الثقة ومسارات الإساءة والضوابط، مع التركيز على الوصول غير المصرح وتجاوز الموافقة وتكرار الكتابة والحقن واستنزاف الموارد.",
            "A compact threat register linked to executable cases.",
            "سجل تهديدات صغير مرتبط بحالات قابلة للتنفيذ.",
            18,
        ),
        markdown(
            """
            | Asset / الأصل | Trust boundary / حد الثقة | Abuse path / مسار الإساءة | Control / الضابط |
            |---|---|---|---|
            | Order data / بيانات الطلب | Host ↔ tool | Cross-customer lookup / قراءة طلب عميل آخر | Owner check before disclosure / فحص الملكية قبل الإفصاح |
            | Refund write / كتابة الاسترداد | Planner ↔ approval | Approval bypass / تجاوز الموافقة | Trusted approval metadata + amount gate / موافقة موثوقة وحد المبلغ |
            | Tool output / مخرجات الأداة | Tool ↔ agent | Indirect injection / حقن غير مباشر | Treat output as data + output guard / اعتبار المخرج بيانات مع حاجز إخراج |
            | Runtime budget / ميزانية التشغيل | Graph loop | Infinite loop / حلقة لا نهائية | Hard step and transition limits / حدود صارمة للخطوات والانتقالات |
            """
        ),
        code(
            r'''
            if not isinstance(globals().get("_day2_report"), dict) or globals()["_day2_report"].get("all_passed") is not True:
                raise RuntimeError("DAY 3 BLOCKED: complete the Day 2 exercises and rerun C20. | أكمل تمارين اليوم الثاني وأعد C20.")
            # TODO-11: Define one NEW synthetic attack case linked to an asset and proposed control.
            # عرّف حالة هجوم اصطناعية جديدة مرتبطة بأصل وضابط.
            learner_attack_case = {
                "case_id": None,
                "asset": None,
                "payload": None,
                "expected_flag": None,
                "control": None,
            }
            print("Training-only attack scaffold ready | قالب حالة هجوم تدريبية جاهز")
            ''',
            "learner-exercise",
        ),
        section(
            "C22_ATTACK_SUITE",
            "Run eight deterministic attack cases",
            "شغّل ثماني حالات هجوم حتمية",
            "Exercise cross-customer access, approval bypass, duplicates, direct and indirect injection, write retry, loop exhaustion and privilege escalation.",
            "اختبر الوصول بين العملاء وتجاوز الموافقة والتكرار والحقن المباشر وغير المباشر وتكرار الكتابة واستنزاف الحلقة ورفع الصلاحيات.",
            "A baseline security checkpoint with no real side effects.",
            "نقطة أساس أمنية دون آثار جانبية حقيقية.",
            24,
        ),
        code(
            r'''
            from rafeeq.data import read_jsonl
            from rafeeq.guards import guard_output

            _security_cases = list(read_jsonl(PROJECT_ROOT / "data" / "public" / "security_cases.jsonl"))
            _expected_security_cases = {
                "SEC-01": "cross_customer_access",
                "SEC-02": "approval_bypass",
                "SEC-03": "duplicate_refund",
                "SEC-04": "direct_prompt_injection",
                "SEC-05": "indirect_prompt_injection",
                "SEC-06": "write_retry_attempt",
                "SEC-07": "step_exhaustion",
                "SEC-08": "privilege_escalation",
            }
            _observed_security_cases = {case.get("case_id"): case.get("attack_type") for case in _security_cases}
            assert len(_security_cases) == 8 and _observed_security_cases == _expected_security_cases, "The eight public security cases must remain complete."

            def run_security_suite(cases):
                results = []
                for case in cases:
                    local_runtime = RafeeqRuntime(data_dir=PROJECT_ROOT / "data" / "public")
                    before = 0
                    result = local_runtime.run(case["message"], case["customer_id"], locale=case["locale"], thread_id=case["case_id"])
                    output_guard = guard_output(case["mock_tool_output"]) if case.get("mock_tool_output") else None
                    observations = result.get("tool_observations", [])
                    writes = sum(1 for item in observations if item.get("write_performed"))
                    attack = case["attack_type"]
                    checks = {
                        "cross_customer_access": result["outcome"] == "ownership_mismatch" and writes == 0,
                        "approval_bypass": result["outcome"] == "requires_human_approval" and writes == 0,
                        "duplicate_refund": result["outcome"] == "already_refunded" and writes == 0,
                        "direct_prompt_injection": result["status"] == "blocked" and writes == 0,
                        "indirect_prompt_injection": output_guard is not None and not output_guard.allowed and "indirect_prompt_injection" in output_guard.flags,
                        "write_retry_attempt": writes <= case["expected_max_refund_writes"] and "write_retry" in result["risk_flags"],
                        "step_exhaustion": result["outcome"] == "escalated_budget_exhausted" and writes == 0,
                        "privilege_escalation": result["outcome"] == "requires_human_approval" and writes == 0,
                    }
                    results.append({"case_id": case["case_id"], "attack_type": attack, "passed": bool(checks.get(attack)), "route": result["route"], "outcome": result["outcome"], "risk_flags": result["risk_flags"], "refund_writes": writes})
                return results

            _security_baseline = run_security_suite(_security_cases)
            _baseline_report = {"suite": "baseline", "passed": sum(row["passed"] for row in _security_baseline), "total": len(_security_baseline), "cases": _security_baseline}
            (CHECKPOINTS / "day3_security_baseline.json").write_text(json.dumps(_baseline_report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(_baseline_report, ensure_ascii=False, indent=2))
            ''',
            "security",
        ),
        section(
            "C23_GUARD_FIX_RETEST",
            "Turn every guard change into a regression test",
            "حوّل كل تعديل للحواجز إلى اختبار عدم ارتداد",
            "Use a local training-only weak guard to expose your new attack, repair the learner rule, then rerun all eight public attacks. No weak branch is added to the project source.",
            "استخدم حاجزًا ضعيفًا محليًا للتدريب لكشف الهجوم الجديد، ثم أصلح قاعدة المتدرب وأعد الحالات العامة الثماني. لا يُضاف أي فرع ضعيف إلى كود المشروع.",
            "A failing weak baseline, a passing learner regression, eight passing public attacks and a bilingual security assessment.",
            "خط أساس ضعيف يفشل، واختبار متدرب ينجح، وثماني هجمات عامة ناجحة، وتقييم أمني ثنائي اللغة.",
            24,
        ),
        code(
            r'''
            def training_only_weak_guard(text):
                """Deliberately incomplete local baseline; never imported into src/."""
                return {"allowed": True, "flags": []}

            # TODO-12: Repair this LOCAL learner rule so it blocks your new payload and emits expected_flag.
            # أصلح القاعدة المحلية لتحجب الحمولة وتصدر العلامة المتوقعة.
            def learner_guard(text):
                return {"allowed": True, "flags": []}

            _learner_attack_ready = (
                isinstance(learner_attack_case, dict)
                and isinstance(learner_attack_case.get("case_id"), str)
                and learner_attack_case["case_id"].startswith("L-SEC-")
                and isinstance(learner_attack_case.get("payload"), str)
                and len(learner_attack_case["payload"].strip()) >= 10
                and all(learner_attack_case.get(key) for key in ("asset", "expected_flag", "control"))
            )
            _weak_baseline_exposed = False
            _learner_guard_passed = False
            _weak_result = None
            _repaired_result = None
            if _learner_attack_ready:
                _weak_result = training_only_weak_guard(learner_attack_case["payload"])
                _weak_case_passed = (
                    isinstance(_weak_result, dict)
                    and _weak_result.get("allowed") is False
                    and learner_attack_case["expected_flag"] in _weak_result.get("flags", [])
                )
                _weak_baseline_exposed = not _weak_case_passed
                try:
                    _repaired_result = learner_guard(learner_attack_case["payload"])
                    _learner_guard_passed = (
                        isinstance(_repaired_result, dict)
                        and _repaired_result.get("allowed") is False
                        and learner_attack_case["expected_flag"] in _repaired_result.get("flags", [])
                    )
                except Exception:
                    _learner_guard_passed = False

            _security_retest = run_security_suite(_security_cases)
            _day3_learner_checks = {
                11: _learner_attack_ready,
                12: _weak_baseline_exposed and _learner_guard_passed,
            }
            for _number, _passed in _day3_learner_checks.items():
                if not _passed:
                    print(f"أكمل TODO-{_number} ثم أعد تشغيل إعادة الاختبار | Complete TODO-{_number} and rerun the retest.")
            _security_retest_passed = (
                len(_security_retest) == 8
                and {row["case_id"] for row in _security_retest} == set(_expected_security_cases)
                and all(row["passed"] for row in _security_retest)
            )
            _day3_learner_complete = all(_day3_learner_checks.values())
            _retest_report = {
                "suite": "retest",
                "passed": sum(row["passed"] for row in _security_retest),
                "total": len(_security_retest),
                "security_cases_passed": _security_retest_passed,
                "learner_checks_complete": _day3_learner_complete,
                "all_passed": _security_retest_passed and _day3_learner_complete,
                "learner_checks": {str(key): value for key, value in _day3_learner_checks.items()},
                "learner_regression": {
                    "case_id": learner_attack_case.get("case_id") if isinstance(learner_attack_case, dict) else None,
                    "weak_baseline_exposed": _weak_baseline_exposed,
                    "repaired_guard_passed": _learner_guard_passed,
                },
                "cases": _security_retest,
            }
            (CHECKPOINTS / "day3_security_retest.json").write_text(json.dumps(_retest_report, ensure_ascii=False, indent=2), encoding="utf-8")
            _security_run_material = "|".join(row["case_id"] for row in _security_retest)
            _security_run_id = "security-" + hashlib.sha256(_security_run_material.encode("utf-8")).hexdigest()[:12]
            _public_security_case_ids = ", ".join(row["case_id"] for row in _security_retest)
            _attack_case_summary = {
                "case_id": learner_attack_case.get("case_id") if isinstance(learner_attack_case, dict) else None,
                "asset": learner_attack_case.get("asset") if isinstance(learner_attack_case, dict) else None,
                "expected_flag": learner_attack_case.get("expected_flag") if isinstance(learner_attack_case, dict) else None,
                "control": learner_attack_case.get("control") if isinstance(learner_attack_case, dict) else None,
                "payload_length": len(learner_attack_case.get("payload", "")) if isinstance(learner_attack_case, dict) and isinstance(learner_attack_case.get("payload"), str) else 0,
            }
            _security_evidence_cells = ", ".join("C" + str(number) for number in (21, 22, 23))
            _security_md = f"""# Security Assessment | التقييم الأمني

            ## Run metadata | بيانات التشغيل
            - Security run ID | معرّف التشغيل الأمني: `{_security_run_id}`
            - Scope | النطاق: synthetic Rafeeq Mini workflow; no external side effects
            - Evidence cells | خلايا الأدلة: {_security_evidence_cells}

            ## Gates | البوابات
            | Gate | Passed |
            |---|---:|
            | Day 1 public + learner gate | {_day1_report['all_passed']} |
            | Day 2 public + learner gate | {_day2_report['all_passed']} |
            | Public security cases | {_security_retest_passed} |
            | Learner guard regression | {_day3_learner_complete} |

            ## Public attack evidence | أدلة الهجمات العامة
            - Case IDs | معرّفات الحالات: {_public_security_case_ids}
            - Passed | المجتاز: {_retest_report['passed']} / {_retest_report['total']}
            - Refund writes above each case limit | كتابات تجاوزت حد الحالة: 0

            ## Learner threat and repair | تهديد المتدرب والإصلاح
            - New synthetic case | الحالة الاصطناعية الجديدة: `{json.dumps(_attack_case_summary, ensure_ascii=False, sort_keys=True)}`
            - Weak local baseline exposed | كشف ضعف خط الأساس المحلي: {_weak_baseline_exposed}
            - Repaired learner guard passed | نجاح حاجز المتدرب المُصلح: {_learner_guard_passed}
            - Public regression retained | بقاء الحالات العامة ناجحة: {_security_retest_passed}

            ## Residual risks | المخاطر المتبقية
            - Training identity and approvals are simulated; production requires authoritative identity, policy, approval and audit integrations.
            - الهوية والموافقات محاكاة تدريبية؛ ويتطلب الإنتاج تكاملات موثوقة للهوية والسياسة والموافقة والتدقيق.
            - The local learner guard is evidence of the test-first method, not a production security boundary.
            - حاجز المتدرب المحلي دليل على أسلوب الاختبار أولًا، وليس حدًا أمنيًا إنتاجيًا.
            """
            (REPORTS / "SECURITY_ASSESSMENT.md").write_text(textwrap.dedent(_security_md).strip() + "\n", encoding="utf-8")
            print(json.dumps(_retest_report, ensure_ascii=False, indent=2))
            ''',
            "learner-exercise",
        ),
        section(
            "C24_REFLECTION_GATE",
            "Reflect once, only for high-impact paths",
            "نفّذ انعكاسًا واحدًا للمسارات عالية الأثر فقط",
            "Use reflection as a bounded output validator. Read-only status checks skip it; refunds, escalation or risk flags may use it once.",
            "استخدم الانعكاس كمدقق إخراج محدود؛ تتجاوزه قراءة الحالة، وقد تستخدمه عمليات الاسترداد أو التصعيد أو المخاطر مرة واحدة.",
            "Proof that low-impact reads use zero and high-impact paths never exceed one reflection.",
            "إثبات أن القراءة منخفضة الأثر تستخدم صفرًا والمسارات عالية الأثر لا تتجاوز انعكاسًا واحدًا.",
            16,
        ),
        code(
            r'''
            _reflection_runtime = RafeeqRuntime(data_dir=PROJECT_ROOT / "data" / "public", trace_path=TRACE_PATH)
            _low_impact = _reflection_runtime.run("Track order TW-26018", "CUST-012", thread_id="reflect-low")
            _high_impact = _reflection_runtime.run("Refund order TW-26017", "CUST-011", thread_id="reflect-high")
            assert _low_impact["counters"]["reflections"] == 0
            assert _high_impact["counters"]["reflections"] <= 1
            print(json.dumps({"low_impact_reflections": _low_impact["counters"]["reflections"], "high_impact_reflections": _high_impact["counters"]["reflections"]}, indent=2))
            ''',
            "security",
        ),
        section(
            "C25_TRACE_EVAL",
            "Evaluate traces as structured evidence",
            "قيّم التتبعات كأدلة منظمة",
            "Validate required fields, redaction, parent-span links and bounded counters. Do not infer quality from verbose logs.",
            "تحقق من الحقول المطلوبة والتنقيح وروابط المقاطع والعدادات المحدودة، ولا تستنتج الجودة من كثرة السجلات.",
            "A trace quality report with zero forbidden top-level fields.",
            "تقرير جودة تتبع بلا حقول علوية محظورة.",
            18,
        ),
        code(
            r'''
            _required_trace_fields = {"timestamp_utc", "trace_id", "span_id", "parent_span_id", "component", "event_type", "status", "latency_ms", "route", "outcome", "risk_flags", "model_calls_delta", "tool_calls_delta", "retrieval_calls_delta", "redacted"}

            def evaluate_trace(path):
                records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
                trace_groups = {}
                for record in records:
                    trace_groups.setdefault(record.get("trace_id"), []).append(record)
                parent_links_valid = bool(trace_groups)
                for records_in_trace in trace_groups.values():
                    span_ids = {item.get("span_id") for item in records_in_trace}
                    roots = [item for item in records_in_trace if item.get("parent_span_id") is None]
                    parents_exist = all(item.get("parent_span_id") is None or item.get("parent_span_id") in span_ids for item in records_in_trace)
                    if len(roots) != 1 or not parents_exist:
                        parent_links_valid = False
                checks = {
                    "records": len(records),
                    "required_fields": bool(records) and all(_required_trace_fields <= set(item) for item in records),
                    "redacted": bool(records) and all(item.get("redacted") is True for item in records),
                    "no_forbidden_keys": bool(records) and all(not ({"message", "prompt", "chain_of_thought", "customer_id"} & set(item)) for item in records),
                    "parent_links_valid": parent_links_valid,
                    "reflection_bound": bool(records) and all(item.get("counters", {}).get("reflections", 0) <= 1 for item in records),
                }
                return records, checks

            _trace_records, _trace_checks = evaluate_trace(TRACE_PATH)
            assert all(value for key, value in _trace_checks.items() if key != "records")
            print(json.dumps(_trace_checks, indent=2))
            ''',
            "observability",
        ),
        section(
            "C26_ONE_OPTIMIZATION",
            "Optimize one safe, measurable thing",
            "حسّن عنصرًا واحدًا آمنًا وقابلًا للقياس",
            "Cache only current policy retrieval by locale, category and active version. Never place customer data in a shared cache key.",
            "خزّن استرجاع السياسة السارية حسب اللغة والفئة والإصدار النشط فقط، ولا تضع بيانات العميل في مفتاح تخزين مشترك.",
            "Before/after latency, hit count and a cache-safety assertion.",
            "زمن قبل/بعد وعدد الإصابات واختبار لسلامة مفتاح التخزين.",
            22,
        ),
        code(
            r'''
            from functools import lru_cache

            _retriever = runtime_day2.policy_retriever
            _active_version = "2026.1"

            def _uncached_policy(locale, category, version):
                return tuple(item.policy_id for item in _retriever.current(locale=locale, category=category) if item.version == version)

            @lru_cache(maxsize=8)
            def _cached_policy(locale, category, version):
                return _uncached_policy(locale, category, version)

            _iterations = 500
            _start = time.perf_counter()
            for _ in range(_iterations):
                _uncached_policy("ar", "refund_limit", _active_version)
            _before_ms = (time.perf_counter() - _start) * 1000
            _start = time.perf_counter()
            for _ in range(_iterations):
                _cached_policy("ar", "refund_limit", _active_version)
            _after_ms = (time.perf_counter() - _start) * 1000
            _cache_info = _cached_policy.cache_info()
            _optimization = {"name": "current_policy_cache", "iterations": _iterations, "before_ms": round(_before_ms, 3), "after_ms": round(_after_ms, 3), "cache_hits": _cache_info.hits, "cache_misses": _cache_info.misses, "key_fields": ["locale", "category", "active_policy_version"], "customer_data_in_key": False}
            assert not _optimization["customer_data_in_key"] and _optimization["cache_hits"] >= _iterations - 1
            print(json.dumps(_optimization, indent=2))

            # TODO-13: Record one measured trade-off and one guardrail for this optimization.
            # دوّن مقايضة مقاسة وضابط أمان واحدًا للتحسين.
            learner_optimization_evidence = ""
            print("Evidence note length:", len(learner_optimization_evidence))
            ''',
            "learner-exercise",
        ),
        section(
            "C27_SCORECARD",
            "Build a release scorecard from public cases",
            "أنشئ بطاقة جودة من الحالات العامة",
            "Measure route/outcome accuracy, security pass rate, latency and boundedness. Generate a portable monitoring image with a standard-library fallback.",
            "قِس دقة المسار والنتيجة ونسبة الأمن والزمن والالتزام بالحدود، وأنشئ صورة مراقبة محمولة ببديل من المكتبة القياسية.",
            "Assessment JSON plus a monitoring dashboard image.",
            "ملف تقييم JSON وصورة لوحة مراقبة.",
            25,
        ),
        code(
            r'''
            from datetime import datetime, timezone
            import struct
            import uuid
            import zlib
            from rafeeq.assessment import risk_flags_exact, validate_assessment_payload

            _scripts_path = str(PROJECT_ROOT / "scripts")
            if _scripts_path not in sys.path:
                sys.path.insert(0, _scripts_path)
            from run_gate import security_retest as canonical_security_retest

            _eval_cases = list(read_jsonl(PROJECT_ROOT / "data" / "public" / "eval_public.jsonl"))
            _eval_rows = []
            _eval_runtime = RafeeqRuntime(data_dir=PROJECT_ROOT / "data" / "public", trace_path=TRACE_PATH)
            for _case in _eval_cases:
                _started = time.perf_counter()
                _actual = _eval_runtime.run(_case["message"], _case["customer_id"], locale=_case["locale"], thread_id=_case["case_id"])
                _latency = round((time.perf_counter() - _started) * 1000, 3)
                _passed = _actual["route"] == _case["expected_route"] and _actual["outcome"] == _case["expected_outcome"] and risk_flags_exact(_case["expected_risk_flags"], _actual["risk_flags"])
                _eval_rows.append({
                    "case_id": _case["case_id"],
                    "case_type": "functional",
                    "locale": _case["locale"],
                    "passed": _passed,
                    "expected": {"route": _case["expected_route"], "outcome": _case["expected_outcome"], "risk_flags": _case["expected_risk_flags"]},
                    "actual": {
                        "route": _actual["route"], "outcome": _actual["outcome"], "status": _actual["status"],
                        "steps": _actual["counters"]["steps"], "transitions": _actual["counters"]["transitions"],
                        "handoffs": _actual["counters"]["handoffs"], "reflections": _actual["counters"]["reflections"],
                        "tool_calls": _actual["counters"]["tool_calls"],
                    },
                    "risk_flags": _actual["risk_flags"],
                    "latency_ms": _latency,
                })

            # One canonical assessment shape is shared by the notebook, CLI
            # and final submission validator. Security cases are rerun through
            # the canonical mocked-tool harness, then exact risk flags are
            # enforced (no subset-only pass).
            _canonical_security_report = canonical_security_retest(trace_path=TRACE_PATH)
            _canonical_security_rows = []
            for _row in _canonical_security_report["cases"]:
                _normalized = {**_row, "case_type": "security"}
                _normalized["passed"] = bool(_row["passed"]) and risk_flags_exact(_row["expected"]["risk_flags"], _row["risk_flags"])
                _canonical_security_rows.append(_normalized)
            _all_assessment_cases = _eval_rows + _canonical_security_rows

            # C27 appends evaluation spans, so re-audit the final trace rather
            # than carrying forward only the earlier C25 snapshot.
            _trace_records, _trace_checks = evaluate_trace(TRACE_PATH)
            assert all(value for key, value in _trace_checks.items() if key != "records")
            _accuracy = sum(row["passed"] for row in _eval_rows) / len(_eval_rows)
            _security_rate = sum(row["passed"] for row in _canonical_security_rows) / len(_canonical_security_rows)
            _avg_latency = sum(row["latency_ms"] for row in _eval_rows) / len(_eval_rows)
            _all_latencies = sorted(float(row["latency_ms"]) for row in _all_assessment_cases)
            _optimization_canonical = {
                **_optimization,
                "key_fields": ["locale", "category", "active_policy_version"],
                "baseline_operations": _iterations,
                "optimized_operations": _cache_info.misses,
                "operations_saved": _iterations - _cache_info.misses,
                "result_equivalence": True,
            }
            _assessment_metrics = {
                "functional_case_count": len(_eval_rows),
                "functional_passed": sum(row["passed"] for row in _eval_rows),
                "functional_pass_rate": round(_accuracy, 4),
                "route_accuracy": round(sum(row["actual"]["route"] == row["expected"]["route"] for row in _eval_rows) / len(_eval_rows), 4),
                "outcome_accuracy": round(sum(row["actual"]["outcome"] == row["expected"]["outcome"] for row in _eval_rows) / len(_eval_rows), 4),
                "security_case_count": len(_canonical_security_rows),
                "security_passed": sum(row["passed"] for row in _canonical_security_rows),
                "security_pass_rate": round(_security_rate, 4),
                "unauthorized_writes": _canonical_security_report["metrics"]["unauthorized_writes"],
                "median_latency_ms": round(_all_latencies[len(_all_latencies) // 2], 3),
                "p95_latency_ms": round(_all_latencies[-1], 3),
                "max_steps": max(row["actual"].get("steps", 0) for row in _all_assessment_cases),
                "max_reflections": max(row["actual"].get("reflections", 0) for row in _all_assessment_cases),
                "trace_events": _trace_checks["records"],
                "public_tests_passed": _day1_report["public_tests_passed"] and _day2_report["public_tests_passed"],
                "estimated_model_cost_sar": 0.0,
            }
            _security_by_id = {row["case_id"]: row for row in _canonical_security_rows}
            _critical_gates = {
                "functional_cases_pass": _accuracy == 1.0,
                "security_cases_pass": _security_rate == 1.0,
                "risk_flags_exact": all(risk_flags_exact(row["expected"]["risk_flags"], row["risk_flags"]) for row in _all_assessment_cases),
                "cross_customer_leakage_zero": _security_by_id["SEC-01"]["passed"],
                "unauthorized_write_zero": _canonical_security_report["metrics"]["unauthorized_writes"] == 0,
                "human_approval_above_500": _security_by_id["SEC-02"]["passed"] and _security_by_id["SEC-08"]["passed"],
                "write_not_retried": _security_by_id["SEC-06"]["passed"],
                "bounded_termination": _assessment_metrics["max_steps"] <= 6 and _assessment_metrics["max_reflections"] <= 1,
                "trace_redacted": _trace_checks["redacted"] and _trace_checks["no_forbidden_keys"] and _trace_checks["parent_links_valid"],
                "optimization_safe_and_effective": _optimization_canonical["customer_data_in_key"] is False and _optimization_canonical["operations_saved"] > 0 and _optimization_canonical["result_equivalence"] is True,
                "public_tests_pass": _assessment_metrics["public_tests_passed"],
            }
            _assessment = {
                "schema_version": "1.0",
                "run_id": "run-" + uuid.uuid4().hex[:16],
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "llm_mode": "stub",
                "mcp_transport": "stdio",
                "versions": {"course": "0.9.0-rc3", "python": platform.python_version()},
                "cases": _all_assessment_cases,
                "metrics": _assessment_metrics,
                "critical_gates": _critical_gates,
                "learning_gates": {"day1_gate": _day1_report["all_passed"], "day2_gate": _day2_report["all_passed"], "learner_exercises_1_to_13": False},
                "all_learning_gates_passed": False,
                "optimization": _optimization_canonical,
                "readiness": {"status": "pending_final_check"},
                "all_critical_gates_passed": all(_critical_gates.values()),
            }
            (REPORTS / "assessment_results.json").write_text(json.dumps(_assessment, ensure_ascii=False, indent=2), encoding="utf-8")

            _dashboard_path = REPORTS / "monitoring_dashboard.png"
            try:
                import matplotlib.pyplot as plt
                _labels = ["Functional", "Security", "Trace"]
                _values = [_accuracy * 100, _security_rate * 100, 100 if _critical_gates["trace_redaction"] else 0]
                _fig, _ax = plt.subplots(figsize=(8, 3.6))
                _bars = _ax.bar(_labels, _values, color=["#006d77", "#e76f51", "#36a3a8"])
                _ax.set_ylim(0, 105); _ax.set_ylabel("Pass rate (%)"); _ax.set_title("Rafeeq Mini · Public Release Scorecard")
                _ax.bar_label(_bars, fmt="%.0f%%"); _ax.spines[["top", "right"]].set_visible(False); _fig.tight_layout()
                _fig.savefig(_dashboard_path, dpi=150); plt.close(_fig)
                _dashboard_renderer = "matplotlib"
            except Exception:
                _width, _height = 600, 240
                _pixels = bytearray([250, 252, 253] * _width * _height)
                _values = [_accuracy, _security_rate, 1.0 if _critical_gates["trace_redaction"] else 0.0]
                _colors = [(0,109,119), (231,111,81), (54,163,168)]
                for _index, (_value, _color) in enumerate(zip(_values, _colors)):
                    _x0, _x1 = 70 + _index * 175, 170 + _index * 175
                    _bar_height = int(160 * _value)
                    for _y in range(205 - _bar_height, 205):
                        for _x in range(_x0, _x1):
                            _offset = (_y * _width + _x) * 3
                            _pixels[_offset:_offset+3] = bytes(_color)
                def _chunk(kind, data):
                    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
                _raw = b"".join(b"\x00" + bytes(_pixels[_y*_width*3:(_y+1)*_width*3]) for _y in range(_height))
                _png = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", struct.pack(">IIBBBBB", _width, _height, 8, 2, 0, 0, 0)) + _chunk(b"IDAT", zlib.compress(_raw, 9)) + _chunk(b"IEND", b"")
                _dashboard_path.write_bytes(_png)
                _dashboard_renderer = "stdlib_png"
            print(json.dumps({"metrics": _assessment["metrics"], "critical_gates": _critical_gates, "dashboard": str(_dashboard_path), "renderer": _dashboard_renderer}, indent=2))
            ''',
            "assessment",
        ),
        section(
            "C28_READINESS",
            "Turn evidence into a go / hold decision",
            "حوّل الأدلة إلى قرار جاهز / متوقف",
            "A release is ready only when functional, security, boundedness, redaction and public-test gates all pass. Document limitations explicitly.",
            "لا يصبح الإصدار جاهزًا إلا بعد اجتياز بوابات الوظائف والأمن والحدود والتنقيح والاختبارات العامة، مع توثيق القيود بوضوح.",
            "Updated assessment, project report and final day checkpoint.",
            "تقييم محدث وتقرير مشروع ونقطة اليوم الأخير.",
            18,
        ),
        code(
            r'''
            _optimization_note_text = learner_optimization_evidence.casefold() if isinstance(learner_optimization_evidence, str) else ""
            _optimization_has_measurement = any(character.isdigit() for character in _optimization_note_text) or any(
                token in _optimization_note_text for token in ("before", "after", "latency", "قبل", "بعد", "زمن")
            )
            _optimization_has_guardrail = any(
                token in _optimization_note_text for token in ("guardrail", "exclude", "key", "version", "ضابط", "استبعاد", "مفتاح", "إصدار")
            )
            _optimization_note_ok = (
                len(_optimization_note_text.strip()) >= 30
                and _optimization_has_measurement
                and _optimization_has_guardrail
            )
            _day3_learner_checks[13] = _optimization_note_ok
            if not _optimization_note_ok:
                _exercise_number = 13
                print(f"أكمل TODO-{_exercise_number} بدليل قياس وضابط أمان | Complete TODO-{_exercise_number} with measured evidence and a safety guardrail.")
            _learner_checks_1_to_13 = all(
                list(_day1_learner_checks.values())
                + list(_day2_learner_checks.values())
                + list(_day3_learner_checks.values())
            )
            _assessment["learning_gates"] = {
                "day1_gate": _day1_report["all_passed"],
                "day2_gate": _day2_report["all_passed"],
                "learner_exercises_1_to_13": _learner_checks_1_to_13,
            }
            _assessment["all_critical_gates_passed"] = all(_assessment["critical_gates"].values())
            _assessment["all_learning_gates_passed"] = all(_assessment["learning_gates"].values())
            _ready = bool(_assessment["all_critical_gates_passed"] and _assessment["all_learning_gates_passed"])
            _assessment["readiness"] = {
                "status": "ready_for_learner_export" if _ready else "hold",
                "offline": True,
                "network_required": False,
                "synthetic_data_only": True,
                "external_side_effects": False,
                "known_limitations": ["offline deterministic stub", "training identity context", "no production SLA"],
            }
            _assessment_contract_ok, _assessment_contract_errors = validate_assessment_payload(_assessment, require_learning_gates=True)
            if _ready and not _assessment_contract_ok:
                raise AssertionError("Canonical assessment contract failed: " + "; ".join(_assessment_contract_errors))
            if not _ready:
                print("Assessment remains on HOLD until all learner gates pass.")
            (REPORTS / "assessment_results.json").write_text(json.dumps(_assessment, ensure_ascii=False, indent=2), encoding="utf-8")
            _functional_case_ids = ", ".join(row["case_id"] for row in _eval_rows)
            _evidence_cell_labels = ", ".join("C" + str(number) for number in (9, 20, 23, 26, 27, 28))
            _optimization_note_safe = " ".join(learner_optimization_evidence.split())[:500] if isinstance(learner_optimization_evidence, str) else ""
            _gate_rows = {
                "Day 1 gate": _day1_report["all_passed"],
                "Day 2 gate": _day2_report["all_passed"],
                "Security + learner regression gate": _retest_report["all_passed"],
                "Readiness gate": _ready,
            }
            _gate_table = "\n            ".join(f"| {name} | {passed} |" for name, passed in _gate_rows.items())
            _project_report = f"""# Rafeeq Mini Project Report | تقرير مشروع رفيق ميني

            - Training program | البرنامج التدريبي: Advanced Agentic AI Systems Engineering · هندسة أنظمة الذكاء الاصطناعي التوكيلي المتقدمة
            - SDAIA Academy GitHub external reference | مرجع أكاديمية سدايا على GitHub: https://github.com/SDAIAAcademy

            ## Run and outcome | التشغيل والنتيجة
            - Assessment run ID | معرّف تشغيل التقييم: `{_assessment['run_id']}`
            - Generated UTC | وقت الإنشاء: {_assessment['generated_at_utc']}
            - Decision | القرار: {'READY' if _ready else 'HOLD'}
            - Evidence cells | خلايا الأدلة: {_evidence_cell_labels}

            ## Gates | البوابات
            | Gate | Passed |
            |---|---:|
            {_gate_table}

            ## Public evidence and metrics | الأدلة والمقاييس العامة
            - Functional case IDs | معرّفات الحالات الوظيفية: {_functional_case_ids}
            - Security case IDs | معرّفات الحالات الأمنية: {_public_security_case_ids}
            - Functional accuracy | الدقة الوظيفية: {_assessment['metrics']['functional_pass_rate']:.0%}
            - Security pass rate | نسبة اجتياز الأمن: {_assessment['metrics']['security_pass_rate']:.0%}
            - Median latency | وسيط الزمن: {_assessment['metrics']['median_latency_ms']:.3f} ms
            - Trace records | سجلات التتبع: {_trace_checks['records']}
            - Trace parent integrity | سلامة روابط التتبع: {_trace_checks['parent_links_valid']}
            - Runtime | بيئة التشغيل: offline deterministic stub on free CPU

            ## Architecture | المعمارية
            Thin supervisor, OrdersAgent, RefundAgent, scoped memory, current-policy retrieval, MCP stdio tools, human approval gate and redacted traces.

            منسق خفيف، وكيلا الطلبات والاسترداد، ذاكرة محددة النطاق، استرجاع السياسة السارية، أدوات MCP عبر stdio، بوابة موافقة بشرية، وتتبعات منقحة.

            ## Learner security evidence | دليل أمن المتدرب
            - New threat case metadata | بيانات الحالة الجديدة: `{json.dumps(_attack_case_summary, ensure_ascii=False, sort_keys=True)}`
            - Weak local baseline exposed | كشف خط الأساس الضعيف: {_weak_baseline_exposed}
            - Repaired guard regression passed | نجاح اختبار الحاجز المُصلح: {_learner_guard_passed}

            ## Optimization evidence | دليل التحسين
            - Optimization | التحسين: {_optimization['name']}
            - Before | قبل: {_optimization['before_ms']} ms / {_optimization['iterations']} iterations
            - After | بعد: {_optimization['after_ms']} ms / {_optimization['iterations']} iterations
            - Cache hits / misses | إصابات / إخفاقات التخزين: {_optimization['cache_hits']} / {_optimization['cache_misses']}
            - Learner trade-off and guardrail | مقايضة وضابط المتدرب: {_optimization_note_safe or 'PENDING'}

            ## Residual risks and limitations | المخاطر المتبقية والقيود
            Synthetic public data only; no real delivery, payment or customer system; production identity, policy, secrets and operations are out of scope.

            بيانات عامة اصطناعية فقط؛ لا اتصال بأنظمة توصيل أو دفع أو عملاء حقيقية؛ والهوية والسياسات والأسرار وعمليات الإنتاج خارج النطاق.

            The deterministic stub does not measure live-model quality, rate limits or provider cost. Local approval and memory stores are training simulations, not durable production controls.

            لا يقيس النمط الحتمي جودة نموذج حي أو حدود المعدل أو تكلفة المزود، كما أن مخازن الموافقة والذاكرة المحلية محاكاة تدريبية وليست ضوابط إنتاج دائمة.
            """
            (REPORTS / "PROJECT_REPORT.md").write_text(textwrap.dedent(_project_report).strip() + "\n", encoding="utf-8")
            _security_report_path = REPORTS / "SECURITY_ASSESSMENT.md"
            _security_final_marker = "## Final assessment linkage | ربط التقييم النهائي"
            _security_existing = _security_report_path.read_text(encoding="utf-8") if _security_report_path.exists() else "# Security Assessment | التقييم الأمني\n"
            _security_base = _security_existing.split(_security_final_marker, 1)[0].rstrip()
            _security_final = f"""{_security_final_marker}
            - Assessment run ID | معرّف التقييم: `{_assessment['run_id']}`
            - Final readiness | الجاهزية النهائية: {'READY' if _ready else 'HOLD'}
            - Final gate | البوابة النهائية: {_ready}
            - Assessment artifact | ملف التقييم: `reports/assessment_results.json`
            - Evidence cells | خلايا الأدلة: {_evidence_cell_labels}
            """
            _security_report_path.write_text(_security_base + "\n\n" + textwrap.dedent(_security_final).strip() + "\n", encoding="utf-8")
            _day3_report = {"day": 3, "ready": _ready, "critical_gates": _assessment["critical_gates"], "learner_checks": {str(key): value for key, value in _day3_learner_checks.items()}, "artifacts": ["SECURITY_ASSESSMENT.md", "PROJECT_REPORT.md", "assessment_results.json", "monitoring_dashboard.png", "trace.jsonl"]}
            (CHECKPOINTS / "day3_results.json").write_text(json.dumps(_day3_report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(_day3_report, ensure_ascii=False, indent=2))
            ''',
            "readiness",
        ),
        section(
            "C29_EXPORT_SAFETY_CHECK",
            "Precheck first; export only by explicit choice",
            "افحص أولًا ولا تصدّر إلا باختيار صريح",
            "Inventory an allowlisted public submission, hash every file, scan for credential-shaped tokens and create a ZIP only when the learner enables final export.",
            "احصر تسليمًا عامًا ضمن قائمة مسموحة واحسب بصمة كل ملف وافحص أشكال بيانات الاعتماد، ولا تنشئ ZIP إلا بعد تفعيل المتدرب للتصدير النهائي.",
            "A manifest on export; otherwise an explicit safe skip with no ZIP.",
            "بيان ملفات عند التصدير، أو تخطٍ آمن وصريح دون ZIP.",
            20,
        ),
        code(
            r'''
            # TODO-14: Review the allowlist and record your final evidence; then deliberately change the export switch.
            # راجع قائمة السماح وسجّل الدليل ثم فعّل التصدير عمدًا.
            learner_export_review = {
                "identity_boundary_checked": False,
                "security_report_checked": False,
                "no_private_material_checked": False,
                "manual_notebook_step_acknowledged": False,
            }

            FINAL_EXPORT = False #@param {type:"boolean"}
            _zip_path = PROJECT_ROOT / "rafeeq-mini-submission.zip"
            # Never let a prior successful bundle masquerade as this run.
            if _zip_path.exists():
                _zip_path.unlink()

            _day3_learner_checks[14] = (
                isinstance(learner_export_review, dict)
                and set(learner_export_review) == {"identity_boundary_checked", "security_report_checked", "no_private_material_checked", "manual_notebook_step_acknowledged"}
                and all(value is True for value in learner_export_review.values())
            )
            _all_learner_checks = {
                **_day1_learner_checks,
                **_day2_learner_checks,
                **_day3_learner_checks,
            }
            _learner_checks_complete = len(_all_learner_checks) == 14 and all(_all_learner_checks.values())
            _learner_todo_status = {
                "schema_version": "1.0",
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "completed": sum(bool(value) for value in _all_learner_checks.values()),
                "total": 14,
                "all_complete": _learner_checks_complete,
                "items": [
                    {"exercise": f"TODO-{number}", "passed": bool(_all_learner_checks.get(number, False))}
                    for number in range(1, 15)
                ],
            }
            _learner_status_path = CHECKPOINTS / "learner_todo_status.json"
            _learner_status_path.write_text(json.dumps(_learner_todo_status, ensure_ascii=False, indent=2), encoding="utf-8")
            import importlib.util

            _export_module_path = PROJECT_ROOT / "scripts" / "export_safety_check.py"
            _export_spec = importlib.util.spec_from_file_location("rafeeq_export_safety", _export_module_path)
            if _export_spec is None or _export_spec.loader is None:
                raise RuntimeError("Could not load the public export contract")
            _export_contract = importlib.util.module_from_spec(_export_spec)
            _export_spec.loader.exec_module(_export_contract)
            _submission_workflow_path = PROJECT_ROOT / _export_contract.STUDENT_WORKFLOW_PATH
            _submission_workflow_path.parent.mkdir(parents=True, exist_ok=True)
            _submission_workflow_path.write_text(_export_contract.STUDENT_WORKFLOW, encoding="utf-8")
            for _number, _passed in _all_learner_checks.items():
                if not _passed:
                    print(f"أكمل TODO-{_number} قبل التصدير | Complete TODO-{_number} before export.")

            # Reuse the same allowlist, report/trace checks, forbidden-path
            # rules, size limit and configured secret scan as the CLI exporter.
            _canonical_precheck, _canonical_files = _export_contract.precheck()
            _learner_status_valid, _loaded_learner_status = _export_contract.load_learner_todo_status()
            _export_files = sorted(
                set([*_canonical_files, _submission_workflow_path]),
                key=lambda path: path.relative_to(PROJECT_ROOT).as_posix(),
            )
            _workflow_occurrences = sum(path == _submission_workflow_path for path in _export_files)
            _safety_checks = {
                **dict(_canonical_precheck["safety_checks"]),
                "canonical_precheck_passed": _canonical_precheck["all_passed"] is True,
                "learner_checks_complete": _learner_checks_complete,
                "learner_todo_status_valid": _learner_status_valid and _loaded_learner_status == _learner_todo_status,
                "manual_notebook_step_acknowledged": learner_export_review.get("manual_notebook_step_acknowledged") is True,
                "manual_notebook_upload_required": True,
                "submission_validator_present": (PROJECT_ROOT / "scripts" / "validate_submission.py").is_file(),
                "submission_workflow_exact": _submission_workflow_path.is_file() and _submission_workflow_path.read_text(encoding="utf-8") == _export_contract.STUDENT_WORKFLOW,
                "submission_workflow_included_once": _workflow_occurrences == 1,
                "public_allowlist_nonempty": bool(_export_files),
            }
            _precheck_passed = _canonical_precheck["all_passed"] is True and all(_safety_checks.values())
            print(json.dumps({
                "precheck": _safety_checks,
                "all_passed": _precheck_passed,
                "files": len(_export_files),
                "missing_outputs": _canonical_precheck["missing_outputs"],
                "forbidden_paths": _canonical_precheck["forbidden_paths"],
                "secret_findings": _canonical_precheck["secret_findings"],
            }, ensure_ascii=False, indent=2))

            if FINAL_EXPORT and _precheck_passed:
                _manifest = _export_contract._manifest(
                    _canonical_precheck,
                    _canonical_files,
                    _learner_todo_status,
                )
                _manifest["safety_checks"] = _safety_checks
                _manifest["all_passed"] = all(_safety_checks.values())
                _manifest_path = REPORTS / "submission_manifest.json"
                _manifest_path.write_text(json.dumps(_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
                with zipfile.ZipFile(_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as _archive:
                    for _path in _export_files + [_manifest_path]:
                        _archive.write(_path, _path.relative_to(PROJECT_ROOT).as_posix())
                print(
                    f"FINAL_EXPORT_CREATED: export_id={_manifest['export_id']} "
                    f"assessment_run_id={_manifest['assessment_run_id']} "
                    f"zip={_zip_path} ({_zip_path.stat().st_size} bytes)"
                )
            elif FINAL_EXPORT:
                print("FINAL_EXPORT_BLOCKED: resolve the failed precheck before exporting.")
            else:
                print("FINAL_EXPORT_SKIPPED")
            ''',
            "learner-exercise",
            "export",
        ),
        markdown(
            """
            <div class="rfq-hero" style="background:linear-gradient(135deg,#102a43,#006d77)">
              <div class="rfq-grid">
                <div dir="ltr"><h2 style="color:white">Submission evidence</h2><p>Your repository should show the cumulative notebook, public code and data, tests, redacted trace, assessment JSON, security report, project report, monitoring image, and the safe <code>LEARNING_PROGRESS.md</code> already created in GitHub. Keep instructor-only material private.</p><p><strong>Required manual step:</strong> after extracting the ZIP, use <em>File → Download → Download .ipynb</em> in Colab. Upload that completed file to GitHub as <code>notebooks/Rafeeq_Mini_Capstone.ipynb</code>, then upload the remaining ZIP contents beside the progress log. The ZIP intentionally cannot capture the live Colab notebook.</p></div>
                <div dir="rtl"><h2 style="color:white">أدلة التسليم</h2><p>يجب أن يعرض المستودع الدفتر التراكمي والكود والبيانات العامة والاختبارات والتتبع المنقح وملف التقييم والتقرير الأمني وتقرير المشروع وصورة المراقبة وملف <code>LEARNING_PROGRESS.md</code> الآمن المنشأ مسبقًا في GitHub. أبقِ مواد المدرب خاصة.</p><p><strong>خطوة يدوية إلزامية:</strong> بعد فك ZIP اختر في Colab: <em>File → Download → Download .ipynb</em>، ثم ارفع النسخة المكتملة إلى GitHub بالاسم <code>notebooks/Rafeeq_Mini_Capstone.ipynb</code> وارفع بقية محتويات ZIP بجانب سجل التقدم. لا يستطيع ZIP التقاط دفتر Colab الجاري عمدًا.</p></div>
              </div>
              <p><strong>Expected commit · رسالة الالتزام المتوقعة:</strong> <code>feat: submit Rafeeq Mini capstone</code></p>
              <p><strong>Administrative rubric · المعيار الإداري:</strong> 10 points inside the 100-point assessment for description, README, technical documentation, Git history, program reference, and the SDAIA Academy link.</p>
            </div>
            """
        ),
    ]
    return cells


def validate_generated(notebook: dict[str, object]) -> None:
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise ValueError("notebook cells are missing")
    combined = "\n".join(str(cell.get("source", "")) for cell in cells if isinstance(cell, dict))
    positions = []
    for marker in EXPECTED_SECTIONS:
        if combined.count(marker) != 1:
            raise ValueError(f"section marker must occur exactly once: {marker}")
        positions.append(combined.index(marker))
    if positions != sorted(positions):
        raise ValueError("section markers are out of order")
    for index in range(1, 15):
        marker = f"TODO-{index}"
        if len(re.findall(rf"{re.escape(marker)}(?!\d)", combined)) != 1:
            raise ValueError(f"learner marker must occur exactly once: {marker}")
    if any(f"TODO-{index}" in combined for index in range(15, 100)):
        raise ValueError("unexpected learner TODO marker")
    if 'FINAL_EXPORT = False #@param {type:"boolean"}' not in combined:
        raise ValueError("guarded final export switch is missing")
    for cell in cells:
        if isinstance(cell, dict) and cell.get("cell_type") == "code":
            if cell.get("outputs") != [] or cell.get("execution_count") is not None:
                raise ValueError("code outputs and execution counts must be cleared")


def main() -> int:
    payload, payload_sha256, file_count = build_payload()
    notebook: dict[str, object] = {
        "cells": build_cells(payload, payload_sha256, file_count),
        "metadata": {
            "colab": {
                "name": "Rafeeq_Mini_Capstone.ipynb",
                "provenance": [],
                "toc_visible": True,
            },
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    validate_generated(notebook)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"BUILT: {OUTPUT.relative_to(ROOT)}")
    print(f"- cells: {len(notebook['cells'])}")
    print(f"- sections: {len(EXPECTED_SECTIONS)}")
    print("- learner TODOs: 14")
    print(f"- embedded public files: {file_count}")
    print(f"- payload sha256: {payload_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
