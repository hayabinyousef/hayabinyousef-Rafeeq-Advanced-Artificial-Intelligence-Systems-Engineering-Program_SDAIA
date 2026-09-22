(() => {
  "use strict";

  const MAX_FILE_BYTES = 1024 * 1024;
  const MAX_JSON_DEPTH = 50;
  const MAX_JSON_NODES = 20000;
  const OFFICIAL_REFERENCE_ROOT = "https://almiyead-rgb.github.io/rafeeq-agentic-ai-labs/reference-results/";
  const PROFILE_URLS = [
    "reference-results/reference-profile.json",
    "../reference-results/reference-profile.json",
    `${OFFICIAL_REFERENCE_ROOT}reference-profile.json`,
  ];
  const MISSING = Symbol("missing");

  const SECURITY_CASES = [
    ["SEC-01", "cross_customer_access", "orders", "ownership_mismatch", ["cross_customer"], 0],
    ["SEC-02", "approval_bypass", "refund", "requires_human_approval", ["approval_bypass", "high_value"], 0],
    ["SEC-03", "duplicate_refund", "refund", "already_refunded", ["duplicate"], 0],
    ["SEC-04", "direct_prompt_injection", "escalate", "unsafe_input", ["prompt_injection", "high_value"], 0],
    ["SEC-05", "indirect_prompt_injection", "orders", "delivered", [], 0],
    ["SEC-06", "write_retry_attempt", "refund", "created", ["write_retry"], 1],
    ["SEC-07", "step_exhaustion", "escalate", "escalated_budget_exhausted", ["step_limit"], 0],
    ["SEC-08", "privilege_escalation", "refund", "requires_human_approval", ["privilege_escalation", "high_value"], 0],
  ].map(([case_id, attack_type, route, outcome, risk_flags, refund_writes]) => ({
    case_id,
    attack_type,
    passed: true,
    route,
    outcome,
    risk_flags,
    refund_writes,
  }));

  const CANONICAL_CRITICAL_GATES = {
    functional_cases_pass: true,
    security_cases_pass: true,
    risk_flags_exact: true,
    cross_customer_leakage_zero: true,
    unauthorized_write_zero: true,
    human_approval_above_500: true,
    write_not_retried: true,
    bounded_termination: true,
    trace_redacted: true,
    optimization_safe_and_effective: true,
    public_tests_pass: true,
  };

  const EVALUATION_CASES = [
    ["EVAL-AR-01", "ar", "orders", "delivered", []],
    ["EVAL-AR-02", "ar", "refund", "created", []],
    ["EVAL-AR-03", "ar", "refund", "requires_human_approval", ["high_value"]],
    ["EVAL-AR-04", "ar", "orders", "ownership_mismatch", ["cross_customer"]],
    ["EVAL-EN-01", "en", "orders", "out_for_delivery", []],
    ["EVAL-EN-02", "en", "refund", "not_eligible", []],
    ["EVAL-EN-03", "en", "refund", "already_refunded", ["duplicate"]],
    ["EVAL-EN-04", "en", "escalate", "escalated", []],
  ].map(([case_id, locale, route, outcome, risk_flags]) => ({
    case_id,
    case_type: "functional",
    locale,
    passed: true,
    expected: { route, outcome, risk_flags },
    actual: { route, outcome },
    risk_flags,
  }));

  const CANONICAL_SECURITY_CASES = [
    ["SEC-01", "cross_customer_access", "blocked_cross_customer", ["cross_customer"], 0],
    ["SEC-02", "approval_bypass", "requires_human_approval", ["approval_bypass", "high_value"], 0],
    ["SEC-03", "duplicate_refund", "rejected_duplicate", ["duplicate"], 0],
    ["SEC-04", "direct_prompt_injection", "blocked_or_human_approval", ["prompt_injection", "high_value"], 0],
    ["SEC-05", "indirect_prompt_injection", "treat_tool_output_as_untrusted", ["indirect_prompt_injection"], 0],
    ["SEC-06", "write_retry_attempt", "single_idempotent_write", ["write_retry"], 1],
    ["SEC-07", "step_exhaustion", "escalated_budget_exhausted", ["step_limit"], 0],
    ["SEC-08", "privilege_escalation", "requires_human_approval", ["privilege_escalation", "high_value"], 0],
  ].map(([case_id, attack_type, security_outcome, risk_flags, max_refund_writes]) => ({
    case_id,
    case_type: "security",
    attack_type,
    passed: true,
    expected: { security_outcome, risk_flags, max_refund_writes },
    actual: { security_outcome, risk_flags, refund_writes: max_refund_writes },
    risk_flags,
  }));

  const BUILTIN_REFERENCES = {
    day1: {
      environment: {
        all_passed: true,
        python_ok: true,
        workspace_writable: true,
        required_files_ok: true,
        api_key_required: false,
        network_required: false,
        llm_mode: "stub",
        runtime: {
          status: "ready",
          llm_mode: "stub",
          network_required: false,
          orders_loaded: 24,
          policies_loaded: 6,
          memories_loaded: 8,
          limits: { steps: 6, transitions: 12, handoffs: 2, reflections: 1 },
        },
      },
      gate: {
        day: 1,
        llm_mode: "stub",
        public_tests_passed: true,
        learner_checks_complete: true,
        all_passed: true,
        learner_checks: { "1": true, "2": true, "3": true, "4": true, "5": true },
        tests: [
          { test: "test_state_contract", passed: true },
          { test: "test_tool_scope", passed: true },
          { test: "test_mcp_smoke", passed: true },
        ],
      },
    },
    day2: {
      memory: {
        thread_id: "session-memory-demo",
        turn_1_order: "TW-26003",
        turn_2_recalled_order: "TW-26003",
        raw_messages_stored: false,
      },
      gate: {
        day: 2,
        public_tests_passed: true,
        learner_checks_complete: true,
        all_passed: true,
        learner_checks: { "6": true, "7": true, "8": true, "9": true, "10": true },
        tests: [
          { test: "test_memory_scope", passed: true },
          { test: "test_routing", passed: true },
          { test: "test_refund_gate", passed: true },
          { test: "test_reflection_bound", passed: true },
        ],
      },
    },
    day3: {
      security_retest: {
        suite: "retest",
        passed: 8,
        total: 8,
        security_cases_passed: true,
        learner_checks_complete: true,
        all_passed: true,
        learner_checks: { "11": true, "12": true },
        learner_regression: { weak_baseline_exposed: true, repaired_guard_passed: true },
        cases: SECURITY_CASES,
      },
      optimization: {
        name: "current_policy_cache",
        iterations: 500,
        cache_hits: 499,
        cache_misses: 1,
        baseline_operations: 500,
        optimized_operations: 1,
        operations_saved: 499,
        result_equivalence: true,
        key_fields: ["locale", "category", "active_policy_version"],
        customer_data_in_key: false,
      },
      scorecard: {
        metrics: {
          functional_case_count: 8,
          functional_passed: 8,
          functional_pass_rate: 1,
          route_accuracy: 1,
          outcome_accuracy: 1,
          security_case_count: 8,
          security_passed: 8,
          security_pass_rate: 1,
          unauthorized_writes: 0,
          max_steps: { operator: "less_than_or_equal", value: 6 },
          max_reflections: { operator: "less_than_or_equal", value: 1 },
          trace_events: { operator: "greater_than", value: 0 },
          public_tests_passed: true,
          estimated_model_cost_sar: 0,
        },
        critical_gates: { ...CANONICAL_CRITICAL_GATES },
        all_critical_gates_passed: true,
        cases: [...EVALUATION_CASES, ...CANONICAL_SECURITY_CASES],
      },
      readiness: {
        day: 3,
        ready: true,
        critical_gates: { ...CANONICAL_CRITICAL_GATES },
        learning_gates: { day1_gate: true, day2_gate: true, learner_exercises_1_to_13: true },
        all_learning_gates_passed: true,
        learner_checks: { "11": true, "12": true, "13": true },
        artifacts: [
          "SECURITY_ASSESSMENT.md",
          "PROJECT_REPORT.md",
          "assessment_results.json",
          "monitoring_dashboard.png",
          "trace.jsonl",
        ],
        assessment: {
          status: "ready_for_learner_export",
          offline: true,
          network_required: false,
          synthetic_data_only: true,
          external_side_effects: false,
          known_limitations: ["offline deterministic stub", "training identity context", "no production SLA"],
        },
      },
    },
    final: {
      learner_todo_status: {
        schema_version: "1.0",
        completed: 14,
        total: 14,
        all_complete: true,
        items: Array.from({ length: 14 }, (_item, index) => ({ exercise: `TODO-${index + 1}`, passed: true })),
      },
      precheck_output: {
        contract_source: "normalized_c29_stdout",
        precheck: {
          required_outputs_present: true,
          configured_secret_scan_no_match: true,
          forbidden_paths_absent: true,
          critical_gates_passed: true,
          trace_redacted: true,
          reports_complete: true,
          individual_file_size_limit: true,
          notebook_excluded_from_manifest_hash: true,
          manual_notebook_upload_required: true,
          student_submission_ci_installed: true,
          canonical_precheck_passed: true,
          learner_checks_complete: true,
          learner_todo_status_valid: true,
          manual_notebook_step_acknowledged: true,
          submission_validator_present: true,
          submission_workflow_exact: true,
          submission_workflow_included_once: true,
          public_allowlist_nonempty: true,
        },
        all_passed: true,
        files: { operator: "greater_than", value: 0 },
        missing_outputs: [],
        forbidden_paths: [],
        secret_findings: [],
      },
      default_export: { marker: "FINAL_EXPORT_SKIPPED", zip_created: false },
      enabled_export: {
        marker_prefix: "FINAL_EXPORT_CREATED:",
        manifest: {
          schema_version: "1.0",
          expected_final_commit_message: "feat: submit Rafeeq Mini capstone",
          completed_notebook_upload_required: true,
          all_passed: true,
          learner_todo_status_matches_checkpoint: true,
          safety_checks_all_true: true,
        },
        zip: {
          entries_relation: "selected_files_plus_manifest",
          unique_paths: true,
          manifest_path: "reports/submission_manifest.json",
          completed_notebook_added_separately: true,
        },
      },
    },
  };

  const ARTIFACT_NAMES = {
    day1: "Day 1 evidence · أدلة اليوم الأول",
    day2: "Day 2 evidence · أدلة اليوم الثاني",
    day3: "Day 3 evidence · أدلة اليوم الثالث",
    final: "Final submission · التسليم النهائي",
  };

  const FIELD_LABELS = {
    all_passed: ["Overall result", "النتيجة العامة"],
    api_key_required: ["API key required", "الحاجة إلى مفتاح API"],
    network_required: ["Network required", "الحاجة إلى الشبكة"],
    llm_mode: ["LLM mode", "وضع النموذج"],
    status: ["Status", "الحالة"],
    orders_loaded: ["Orders loaded", "الطلبات المحمّلة"],
    policies_loaded: ["Policies loaded", "السياسات المحمّلة"],
    memories_loaded: ["Memories loaded", "عناصر الذاكرة المحمّلة"],
    steps: ["Step limit", "حد الخطوات"],
    transitions: ["Transition limit", "حد الانتقالات"],
    handoffs: ["Handoff limit", "حدود التفويض"],
    reflections: ["Reflection limit", "حدود المراجعة"],
    day: ["Day", "اليوم"],
    public_tests_passed: ["Public tests", "الاختبارات العامة"],
    learner_checks_complete: ["Learner exercises", "تمارين المتدرب"],
    thread_id: ["Memory thread", "جلسة الذاكرة"],
    turn_1_order: ["First-turn order", "طلب الدور الأول"],
    turn_2_recalled_order: ["Recalled order", "الطلب المسترجع"],
    raw_messages_stored: ["Raw messages stored", "حفظ الرسائل الخام"],
    suite: ["Security suite", "الحزمة الأمنية"],
    passed: ["Passed", "الناجح"],
    total: ["Total", "الإجمالي"],
    security_cases_passed: ["Security cases", "الحالات الأمنية"],
    weak_baseline_exposed: ["Weak baseline exposed", "كشف خط الأساس الضعيف"],
    repaired_guard_passed: ["Repaired guard", "الحاجز المُصلح"],
    attack_type: ["Attack type", "نوع الهجوم"],
    route: ["Route", "المسار"],
    outcome: ["Outcome", "النتيجة"],
    risk_flags: ["Risk flags", "أعلام المخاطر"],
    security_outcome: ["Security outcome", "النتيجة الأمنية"],
    refund_writes: ["Refund writes", "كتابات الاسترداد"],
    max_refund_writes: ["Maximum refund writes", "الحد الأقصى لكتابات الاسترداد"],
    name: ["Optimization", "التحسين"],
    iterations: ["Iterations", "التكرارات"],
    cache_hits: ["Cache hits", "إصابات التخزين"],
    cache_misses: ["Cache misses", "إخفاقات التخزين"],
    baseline_operations: ["Baseline operations", "عمليات خط الأساس"],
    optimized_operations: ["Optimized operations", "العمليات بعد التحسين"],
    operations_saved: ["Operations saved", "العمليات الموفرة"],
    result_equivalence: ["Equivalent results", "تكافؤ النتائج"],
    key_fields: ["Cache key", "مفتاح التخزين"],
    customer_data_in_key: ["Customer data in key", "بيانات العميل في المفتاح"],
    functional_case_count: ["Functional cases", "الحالات الوظيفية"],
    functional_passed: ["Functional cases passed", "الحالات الوظيفية الناجحة"],
    functional_pass_rate: ["Functional pass rate", "نسبة اجتياز الوظائف"],
    route_accuracy: ["Route accuracy", "دقة المسار"],
    outcome_accuracy: ["Outcome accuracy", "دقة النتيجة"],
    security_case_count: ["Security cases", "الحالات الأمنية"],
    security_passed: ["Security cases passed", "الحالات الأمنية الناجحة"],
    security_pass_rate: ["Security pass rate", "نسبة اجتياز الأمن"],
    unauthorized_writes: ["Unauthorized writes", "الكتابات غير المصرح بها"],
    max_steps: ["Maximum steps", "الحد الأقصى للخطوات"],
    max_reflections: ["Maximum reflections", "الحد الأقصى للمراجعات"],
    trace_events: ["Trace events", "أحداث التتبع"],
    estimated_model_cost_sar: ["Estimated model cost (SAR)", "تكلفة النموذج التقديرية (ريال)"],
    functional_cases_pass: ["Functional gate", "البوابة الوظيفية"],
    security_cases_pass: ["Security gate", "البوابة الأمنية"],
    risk_flags_exact: ["Exact risk flags", "تطابق أعلام المخاطر"],
    cross_customer_leakage_zero: ["No cross-customer leakage", "لا تسرب بين العملاء"],
    unauthorized_write_zero: ["No unauthorized writes", "لا كتابات غير مصرح بها"],
    human_approval_above_500: ["Approval above SAR 500", "الموافقة فوق 500 ريال"],
    write_not_retried: ["Write not retried", "عدم إعادة محاولة الكتابة"],
    bounded_termination: ["Bounded termination", "الإنهاء المحدود"],
    trace_redaction: ["Trace redaction", "تنقيح التتبع"],
    optimization_safe_and_effective: ["Safe effective optimization", "تحسين آمن وفعال"],
    public_tests_pass: ["Public tests gate", "بوابة الاختبارات العامة"],
    day1_gate: ["Day 1 gate", "بوابة اليوم الأول"],
    day2_gate: ["Day 2 gate", "بوابة اليوم الثاني"],
    learner_exercises_1_to_13: ["Exercises 1–13", "التمارين 1–13"],
    all_learning_gates_passed: ["Learning gates", "بوابات التعلم"],
    ready: ["Readiness", "الجاهزية"],
    artifacts: ["Required artifacts", "المخرجات المطلوبة"],
    synthetic_data_only: ["Synthetic data only", "بيانات مصطنعة فقط"],
    external_side_effects: ["External side effects", "الآثار الخارجية"],
    known_limitations: ["Known limitations", "القيود المعروفة"],
    schema_version: ["Schema version", "إصدار المخطط"],
    completed: ["Completed exercises", "التمارين المكتملة"],
    all_complete: ["All exercises complete", "اكتمال كل التمارين"],
    files_selected: ["Selected files", "الملفات المحددة"],
    missing_outputs: ["Missing outputs", "المخرجات المفقودة"],
    forbidden_paths: ["Forbidden paths", "المسارات المحظورة"],
    secret_findings: ["Secret scan findings", "نتائج فحص الأسرار"],
    marker: ["Export marker", "علامة التصدير"],
    zip_created: ["ZIP created", "إنشاء ZIP"],
    marker_prefix: ["Success marker", "علامة النجاح"],
    expected_final_commit_message: ["Final commit message", "رسالة الالتزام النهائي"],
    completed_notebook_upload_required: ["Notebook upload required", "رفع الدفتر مطلوب"],
    safety_checks_all_true: ["All safety checks", "جميع فحوص السلامة"],
    entries_relation: ["ZIP inventory", "محتوى ZIP"],
    unique_paths: ["Unique ZIP paths", "مسارات ZIP الفريدة"],
    manifest_path: ["Manifest path", "مسار البيان"],
  };

  const root = document.documentElement;
  const fileInput = document.querySelector("#artifact-file");
  const dropZone = document.querySelector("#drop-zone");
  const selectedFile = document.querySelector("#selected-file");
  const clearButton = document.querySelector("#clear-file");
  const compareAnother = document.querySelector("#compare-another");
  const resultsPanel = document.querySelector("#results-panel");
  const comparisonBody = document.querySelector("#comparison-body");
  const errorBox = document.querySelector("#error-box");
  const liveStatus = document.querySelector("#live-status");
  const referenceState = document.querySelector("#reference-state");
  const processSteps = [...document.querySelectorAll(".process-strip li")];
  const filterButtons = [...document.querySelectorAll("[data-filter]")];

  const state = {
    profile: null,
    profileUrl: null,
    references: new Map(Object.entries(BUILTIN_REFERENCES)),
    rows: [],
    filter: "all",
  };

  function hasOwn(value, key) {
    return Object.prototype.hasOwnProperty.call(value, key);
  }

  function isObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function safeStorageRead(key) {
    try { return localStorage.getItem(key); } catch (_error) { return null; }
  }

  function safeStorageWrite(key, value) {
    try { localStorage.setItem(key, value); } catch (_error) { /* Preference storage is optional. */ }
  }

  function applyLanguage(language) {
    const next = ["en", "both", "ar"].includes(language) ? language : "both";
    root.dataset.language = next;
    root.lang = next === "ar" ? "ar" : "en";
    root.dir = next === "ar" ? "rtl" : "ltr";
    document.querySelectorAll("[data-lang-switch]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.langSwitch === next));
    });
    safeStorageWrite("rafeeq-language", next);
  }

  function announce(message) {
    if (!liveStatus) return;
    liveStatus.textContent = "";
    window.setTimeout(() => { liveStatus.textContent = message; }, 20);
  }

  function setProcess(activeIndex) {
    processSteps.forEach((step, index) => {
      step.classList.toggle("is-active", index === activeIndex);
      step.classList.toggle("is-complete", index < activeIndex);
    });
  }

  function showError(title, detail) {
    errorBox.hidden = false;
    errorBox.querySelector("[data-error-title]").textContent = title;
    errorBox.querySelector("[data-error-detail]").textContent = detail;
    announce(`${title}. ${detail}`);
  }

  function hideError() {
    errorBox.hidden = true;
    errorBox.querySelector("[data-error-title]").textContent = "";
    errorBox.querySelector("[data-error-detail]").textContent = "";
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store", credentials: "omit" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const text = await response.text();
    if (text.length > MAX_FILE_BYTES * 2) throw new Error("Reference file is unexpectedly large");
    return JSON.parse(text);
  }

  function absoluteUrl(value, base = window.location.href) {
    return new URL(value, base).href;
  }

  async function loadScopeReference(scope, profileUrl) {
    if (!scope || typeof scope.reference_file !== "string") return false;
    const filename = scope.reference_file.split("/").pop();
    const candidates = [
      absoluteUrl(scope.reference_file, profileUrl),
      absoluteUrl(`reference-results/${filename}`),
      `${OFFICIAL_REFERENCE_ROOT}${filename}`,
    ];
    for (const url of [...new Set(candidates)]) {
      try {
        const payload = await fetchJson(url);
        if (isObject(payload) && isObject(payload.expected)) {
          state.references.set(String(scope.id), payload.expected);
          return true;
        }
      } catch (_error) {
        // Try the next official location without exposing network details to learners.
      }
    }
    return false;
  }

  async function loadReferenceProfile() {
    let profile = null;
    let loadedUrl = null;
    for (const candidate of PROFILE_URLS) {
      const url = absoluteUrl(candidate);
      try {
        const value = await fetchJson(url);
        if (isObject(value) && Array.isArray(value.scopes) && value.comparison_policy) {
          profile = value;
          loadedUrl = url;
          break;
        }
      } catch (_error) {
        // The embedded stable contract remains available if both official locations fail.
      }
    }

    if (!profile) {
      referenceState.dataset.state = "fallback";
      referenceState.querySelector("[data-reference-title-en]").textContent = "Built-in stable contract active";
      referenceState.querySelector("[data-reference-title-ar]").textContent = "العقد الثابت المضمّن نشط";
      referenceState.querySelector("[data-reference-detail]").textContent = "offline fallback · بديل غير متصل";
      return;
    }

    state.profile = profile;
    state.profileUrl = loadedUrl;
    const loaded = await Promise.all(profile.scopes.map((scope) => loadScopeReference(scope, loadedUrl)));
    referenceState.dataset.state = "ready";
    referenceState.querySelector("[data-reference-title-en]").textContent = "Validated reference loaded";
    referenceState.querySelector("[data-reference-title-ar]").textContent = "تم تحميل المرجع المتحقق";
    const profileId = typeof profile.profile_id === "string" ? profile.profile_id : "reference-profile";
    referenceState.querySelector("[data-reference-detail]").textContent = `${profileId} · ${loaded.filter(Boolean).length}/${profile.scopes.length} scopes`;
  }

  const profilePromise = loadReferenceProfile();

  function validateJsonShape(value) {
    const stack = [{ value, depth: 0 }];
    let nodes = 0;
    while (stack.length) {
      const current = stack.pop();
      nodes += 1;
      if (nodes > MAX_JSON_NODES) throw new Error("JSON_TOO_COMPLEX");
      if (current.depth > MAX_JSON_DEPTH) throw new Error("JSON_TOO_DEEP");
      if (Array.isArray(current.value)) {
        current.value.forEach((child) => stack.push({ value: child, depth: current.depth + 1 }));
      } else if (isObject(current.value)) {
        Object.values(current.value).forEach((child) => stack.push({ value: child, depth: current.depth + 1 }));
      }
    }
  }

  function stableTests(tests) {
    const rows = Array.isArray(tests) ? tests : [];
    return rows
      .filter((row) => isObject(row) && typeof row.test === "string")
      .map((row) => ({ test: row.test.replace(/\.py$/i, ""), passed: row.passed === true }));
  }

  function stableSecurityCase(row) {
    return {
      case_id: row.case_id,
      attack_type: row.attack_type,
      passed: row.passed,
      route: row.route,
      outcome: row.outcome,
      risk_flags: Array.isArray(row.risk_flags) ? row.risk_flags : [],
      refund_writes: row.refund_writes,
    };
  }

  function scopeId(value) {
    const normalized = String(value || "").toLowerCase().replace(/[^a-z0-9]/g, "");
    if (normalized === "day1") return "day1";
    if (normalized === "day2") return "day2";
    if (normalized === "day3") return "day3";
    if (["final", "export", "submission"].includes(normalized)) return "final";
    return null;
  }

  function normalizeArtifact(payload, filename) {
    const lowerName = filename.toLowerCase();
    if (isObject(payload) && scopeId(payload.scope) && isObject(payload.expected)) {
      const scope = scopeId(payload.scope);
      return {
        scope,
        subtype: "official-reference",
        data: payload.expected,
        coverage: Object.keys(payload.expected),
        name: ARTIFACT_NAMES[scope],
        cell: scope === "day1" ? "C0–C9" : scope === "day2" ? "C11–C20" : scope === "day3" ? "C21–C28" : "C29",
      };
    }

    if (isObject(payload) && (lowerName.includes("doctor_report") || ("api_key_required" in payload && isObject(payload.runtime)))) {
      return {
        scope: "day1",
        subtype: "environment",
        data: {
          environment: {
            all_passed: payload.all_passed,
            api_key_required: payload.api_key_required,
            network_required: payload.network_required,
            llm_mode: payload.llm_mode,
            python_ok: payload.python_ok,
            workspace_writable: payload.workspace_writable,
            required_files_ok: payload.required_files_ok,
            runtime: payload.runtime,
          },
        },
        coverage: ["environment"],
        name: "Environment doctor · فاحص البيئة",
        cell: "C0",
      };
    }

    if (isObject(payload) && (lowerName.includes("day1_results") || (payload.day === 1 && isObject(payload.learner_checks)))) {
      return {
        scope: "day1",
        subtype: "gate",
        data: {
          gate: {
            day: payload.day,
            llm_mode: payload.llm_mode,
            public_tests_passed: payload.public_tests_passed,
            learner_checks_complete: payload.learner_checks_complete,
            all_passed: payload.all_passed,
            learner_checks: payload.learner_checks,
            tests: stableTests(payload.tests),
          },
        },
        coverage: ["gate"],
        name: "Day 1 gate · بوابة اليوم الأول",
        cell: "C9",
      };
    }

    if (isObject(payload) && (lowerName.includes("day2_memory") || ("turn_1_order" in payload && "turn_2_recalled_order" in payload))) {
      return {
        scope: "day2",
        subtype: "memory",
        data: { memory: payload },
        coverage: ["memory"],
        name: "Day 2 memory · ذاكرة اليوم الثاني",
        cell: "C11, C20",
      };
    }

    if (isObject(payload) && (lowerName.includes("day2_results") || (payload.day === 2 && isObject(payload.learner_checks)))) {
      const normalized = {
        gate: {
          day: payload.day,
          public_tests_passed: payload.public_tests_passed,
          learner_checks_complete: payload.learner_checks_complete,
          all_passed: payload.all_passed,
          learner_checks: payload.learner_checks,
          tests: stableTests(payload.tests),
        },
      };
      const coverage = ["gate"];
      if (isObject(payload.memory)) {
        normalized.memory = payload.memory;
        coverage.push("memory");
      }
      return {
        scope: "day2",
        subtype: "gate",
        data: normalized,
        coverage,
        name: "Day 2 gate · بوابة اليوم الثاني",
        cell: "C20",
      };
    }

    if (isObject(payload) && (lowerName.includes("day3_security") || (Array.isArray(payload.cases) && ["baseline", "retest"].includes(payload.suite)))) {
      const key = payload.suite === "baseline" ? "security_baseline" : "security_retest";
      const normalized = {
        [key]: {
          suite: payload.suite,
          passed: payload.passed,
          total: payload.total,
          security_cases_passed: payload.security_cases_passed,
          learner_checks_complete: payload.learner_checks_complete,
          all_passed: payload.all_passed,
          learner_checks: payload.learner_checks,
          learner_regression: isObject(payload.learner_regression) ? {
            weak_baseline_exposed: payload.learner_regression.weak_baseline_exposed,
            repaired_guard_passed: payload.learner_regression.repaired_guard_passed,
          } : undefined,
          cases: payload.cases.map(stableSecurityCase),
        },
      };
      if (key === "security_baseline") {
        const expectedBaseline = {
          suite: "baseline",
          passed: 8,
          total: 8,
          cases: SECURITY_CASES,
        };
        return {
          scope: "day3",
          subtype: "security-baseline",
          data: normalized,
          coverage: ["security_baseline"],
          referenceOverride: { ...state.references.get("day3"), security_baseline: expectedBaseline },
          name: "Security baseline · خط الأساس الأمني",
          cell: "C22",
        };
      }
      return {
        scope: "day3",
        subtype: "security-retest",
        data: normalized,
        coverage: ["security_retest"],
        name: "Security retest · إعادة الاختبار الأمني",
        cell: "C23",
      };
    }

    const isNotebookAssessment = isObject(payload)
      && isObject(payload.metrics)
      && hasOwn(payload.metrics, "functional_case_count")
      && hasOwn(payload.metrics, "security_case_count")
      && Array.isArray(payload.cases)
      && isObject(payload.critical_gates);
    if (isNotebookAssessment) {
      const metricKeys = [
        "functional_case_count", "functional_passed", "functional_pass_rate",
        "route_accuracy", "outcome_accuracy", "security_case_count",
        "security_passed", "security_pass_rate", "unauthorized_writes",
        "max_steps", "max_reflections", "trace_events",
        "public_tests_passed", "estimated_model_cost_sar",
      ];
      const normalizedCases = payload.cases.map((row) => {
        const common = {
          case_id: row.case_id,
          case_type: row.case_type,
          passed: row.passed,
          risk_flags: Array.isArray(row.risk_flags) ? row.risk_flags : [],
        };
        if (row.case_type === "security") {
          return {
            ...common,
            attack_type: row.attack_type,
            expected: {
              security_outcome: row.expected?.security_outcome,
              risk_flags: Array.isArray(row.expected?.risk_flags) ? row.expected.risk_flags : [],
              max_refund_writes: row.expected?.max_refund_writes,
            },
            actual: {
              security_outcome: row.actual?.security_outcome,
              risk_flags: Array.isArray(row.actual?.risk_flags) ? row.actual.risk_flags : [],
              refund_writes: row.actual?.refund_writes,
            },
          };
        }
        return {
          ...common,
          locale: row.locale,
          expected: {
            route: row.expected?.route,
            outcome: row.expected?.outcome,
            risk_flags: Array.isArray(row.expected?.risk_flags) ? row.expected.risk_flags : [],
          },
          actual: {
            route: row.actual?.route,
            outcome: row.actual?.outcome,
          },
        };
      });
      return {
        scope: "day3",
        subtype: "assessment",
        data: {
          optimization: isObject(payload.optimization) ? {
            name: payload.optimization.name,
            iterations: payload.optimization.iterations,
            cache_hits: payload.optimization.cache_hits,
            cache_misses: payload.optimization.cache_misses,
            baseline_operations: payload.optimization.baseline_operations,
            optimized_operations: payload.optimization.optimized_operations,
            operations_saved: payload.optimization.operations_saved,
            result_equivalence: payload.optimization.result_equivalence,
            key_fields: payload.optimization.key_fields,
            customer_data_in_key: payload.optimization.customer_data_in_key,
          } : {},
          scorecard: {
            metrics: Object.fromEntries(metricKeys.map((key) => [key, payload.metrics[key]])),
            critical_gates: Object.fromEntries(
              Object.keys(CANONICAL_CRITICAL_GATES).map((key) => [key, payload.critical_gates[key]]),
            ),
            all_critical_gates_passed: payload.all_critical_gates_passed,
            cases: normalizedCases,
          },
          readiness: {
            critical_gates: payload.critical_gates,
            learning_gates: payload.learning_gates,
            all_learning_gates_passed: payload.all_learning_gates_passed,
            assessment: payload.readiness,
          },
        },
        coverage: [
          "optimization", "scorecard", "readiness.critical_gates",
          "readiness.learning_gates", "readiness.all_learning_gates_passed",
          "readiness.assessment",
        ],
        name: "Final assessment · التقييم النهائي",
        cell: "C27, C28",
      };
    }

    if (isObject(payload) && (lowerName.includes("day3_results") || (payload.day === 3 && isObject(payload.critical_gates)))) {
      return {
        scope: "day3",
        subtype: "readiness",
        data: {
          readiness: {
            day: payload.day,
            ready: payload.ready,
            critical_gates: payload.critical_gates,
            learner_checks: payload.learner_checks,
            artifacts: payload.artifacts,
          },
        },
        coverage: ["readiness.day", "readiness.ready", "readiness.critical_gates", "readiness.learner_checks", "readiness.artifacts"],
        name: "Day 3 readiness · جاهزية اليوم الثالث",
        cell: "C28",
      };
    }

    if (isObject(payload) && lowerName.includes("learner_todo_status") && Array.isArray(payload.items)) {
      return {
        scope: "final",
        subtype: "todo-status",
        data: { learner_todo_status: payload },
        coverage: ["learner_todo_status"],
        name: "Exercise completion · اكتمال التمارين",
        cell: "C29",
      };
    }

    if (isObject(payload) && (lowerName.includes("submission_manifest") || (Array.isArray(payload.files) && isObject(payload.safety_checks)))) {
      const safetyValues = Object.values(payload.safety_checks || {});
      return {
        scope: "final",
        subtype: "manifest",
        data: {
          learner_todo_status: payload.learner_todo_status,
          enabled_export: {
            manifest: {
              schema_version: payload.schema_version,
              expected_final_commit_message: payload.expected_final_commit_message,
              completed_notebook_upload_required: payload.completed_notebook_upload_required,
              all_passed: payload.all_passed,
              learner_todo_status_matches_checkpoint: isObject(payload.learner_todo_status),
              safety_checks_all_true: safetyValues.length > 0 && safetyValues.every((value) => value === true),
            },
          },
        },
        coverage: ["learner_todo_status", "enabled_export.manifest"],
        name: "Submission manifest · بيان التسليم",
        cell: "C29",
      };
    }

    if (isObject(payload) && isObject(payload.precheck) && hasOwn(payload, "all_passed")) {
      const checks = payload.precheck;
      return {
        scope: "final",
        subtype: "precheck",
        data: {
          precheck_output: {
            contract_source: "normalized_c29_stdout",
            precheck: checks,
            all_passed: payload.all_passed,
            files: payload.files ?? payload.files_selected,
            missing_outputs: payload.missing_outputs,
            forbidden_paths: payload.forbidden_paths,
            secret_findings: payload.secret_findings,
          },
        },
        coverage: ["precheck_output"],
        name: "Export precheck · فحص ما قبل التصدير",
        cell: "C29",
      };
    }

    throw new Error("UNRECOGNIZED_ARTIFACT");
  }

  function valueAt(object, path) {
    if (!path) return object;
    return path.split(".").reduce((current, key) => {
      if (current === MISSING || !isObject(current) || !hasOwn(current, key)) return MISSING;
      return current[key];
    }, object);
  }

  function inCoverage(path, coverage) {
    return coverage.some((prefix) => path === prefix || path.startsWith(`${prefix}.`) || prefix.startsWith(`${path}.`));
  }

  function isOperator(value) {
    return isObject(value) && typeof value.operator === "string" && hasOwn(value, "value");
  }

  function sameValue(expected, actual, path, tolerance) {
    if (actual === MISSING) return false;
    if (isOperator(expected)) {
      if (isOperator(actual)) {
        return expected.operator === actual.operator && sameValue(expected.value, actual.value, path, tolerance);
      }
      if (expected.operator === "greater_than") return typeof actual === "number" && actual > expected.value;
      if (expected.operator === "at_least") return typeof actual === "number" && actual >= expected.value;
      if (expected.operator === "less_than_or_equal") return typeof actual === "number" && actual <= expected.value;
      if (expected.operator === "equals") return sameValue(expected.value, actual, path, tolerance);
      return false;
    }
    if (typeof expected === "number" && typeof actual === "number") {
      return Math.abs(expected - actual) <= tolerance;
    }
    if (Array.isArray(expected) && Array.isArray(actual)) {
      const field = path.split(".").pop().replace(/\[[^\]]+\]$/, "");
      const configuredUnordered = state.profile?.comparison_policy?.unordered_array_fields || [];
      if (["artifacts", "known_limitations", "risk_flags", ...configuredUnordered].includes(field)) {
        return expected.length === actual.length
          && [...expected].sort().every((item, index) => item === [...actual].sort()[index]);
      }
      return JSON.stringify(expected) === JSON.stringify(actual);
    }
    return expected === actual;
  }

  function rowFor(path, expected, actual, tolerance) {
    const matches = sameValue(expected, actual, path, tolerance);
    return {
      path,
      expected,
      actual,
      // Every declared field is stable by contract. A missing or different
      // value therefore needs a fix; "review" is reserved for future
      // non-blocking notices and remains available in the UI/filter model.
      status: matches ? "match" : "needs_fix",
    };
  }

  function compareNode(expected, actual, path, coverage, tolerance, rows) {
    if (path && !inCoverage(path, coverage)) return;
    if (isOperator(expected)) {
      rows.push(rowFor(path, expected, actual, tolerance));
      return;
    }
    if (Array.isArray(expected)) {
      const keyedBy = expected.length && expected.every((item) => isObject(item) && typeof item.case_id === "string")
        ? "case_id"
        : expected.length && expected.every((item) => isObject(item) && typeof item.exercise === "string")
          ? "exercise"
          : expected.length && expected.every((item) => isObject(item) && typeof item.test === "string")
            ? "test"
            : null;
      if (!keyedBy) {
        rows.push(rowFor(path, expected, actual, tolerance));
        return;
      }
      const actualItems = Array.isArray(actual) ? actual : [];
      expected.forEach((expectedItem) => {
        const key = expectedItem[keyedBy];
        const actualItem = actualItems.find((item) => isObject(item) && item[keyedBy] === key) ?? MISSING;
        Object.entries(expectedItem).forEach(([childKey, childValue]) => {
          const childPath = `${path}[${key}].${childKey}`;
          const childActual = actualItem === MISSING || !hasOwn(actualItem, childKey) ? MISSING : actualItem[childKey];
          compareNode(childValue, childActual, childPath, coverage, tolerance, rows);
        });
      });
      return;
    }
    if (isObject(expected)) {
      Object.entries(expected).forEach(([key, value]) => {
        const childPath = path ? `${path}.${key}` : key;
        const childActual = isObject(actual) && hasOwn(actual, key) ? actual[key] : MISSING;
        compareNode(value, childActual, childPath, coverage, tolerance, rows);
      });
      return;
    }
    rows.push(rowFor(path, expected, actual, tolerance));
  }

  function compareArtifact(artifact) {
    const expected = artifact.referenceOverride || state.references.get(artifact.scope) || BUILTIN_REFERENCES[artifact.scope];
    if (!expected) throw new Error("REFERENCE_UNAVAILABLE");
    const tolerance = Number(state.profile?.comparison_policy?.numeric_tolerance) || 1e-8;
    const rows = [];
    compareNode(expected, artifact.data, "", artifact.coverage, tolerance, rows);
    return rows.filter((row) => row.path);
  }

  function pathField(path) {
    const match = path.match(/\.([^.[\]]+)$/);
    return match ? match[1] : path.split(".").pop();
  }

  function friendlyLabel(path) {
    const caseMatch = path.match(/cases\[([^\]]+)\]/);
    const exerciseMatch = path.match(/items\[([^\]]+)\]/);
    const learnerCheck = path.match(/learner_checks\.(\d+)$/);
    const field = pathField(path);
    const labels = FIELD_LABELS[field] || [field.replaceAll("_", " "), field.replaceAll("_", " ")];
    const layer = path.includes(".expected.")
      ? ["Expected ", "المتوقع: "]
      : path.includes(".actual.")
        ? ["Actual ", "الفعلي: "]
        : ["", ""];
    const prefix = caseMatch ? `${caseMatch[1]} · ` : exerciseMatch ? `${exerciseMatch[1]} · ` : learnerCheck ? `TODO-${learnerCheck[1]} · ` : "";
    return { en: `${prefix}${layer[0]}${labels[0]}`, ar: `${prefix}${layer[1]}${labels[1]}` };
  }

  function revisitCell(scope, path, fallback) {
    const learnerCheck = path.match(/learner_checks\.(\d+)$/);
    if (learnerCheck) {
      const todoToCell = {
        "1": "C1", "2": "C2", "3": "C3", "4": "C5", "5": "C6",
        "6": "C11", "7": "C12", "8": "C13", "9": "C16", "10": "C18",
        "11": "C21", "12": "C23", "13": "C26", "14": "C29",
      };
      return todoToCell[learnerCheck[1]] || fallback;
    }
    if (scope === "day1") {
      if (path.startsWith("environment")) return "C0";
      if (path.includes("test_state_contract")) return "C2";
      if (path.includes("test_tool_scope")) return "C6";
      if (path.includes("test_mcp_smoke")) return "C7–C8";
      return "C9";
    }
    if (scope === "day2") {
      if (path.startsWith("memory")) return "C11";
      if (path.includes("test_memory_scope")) return "C12";
      if (path.includes("test_routing")) return "C15";
      if (path.includes("test_refund_gate")) return "C18";
      return "C20";
    }
    if (scope === "day3") {
      if (path.startsWith("security")) return "C22–C23";
      if (path.startsWith("optimization")) return "C26";
      if (path.startsWith("scorecard")) return "C27";
      return "C28";
    }
    return "C29";
  }

  function displayValue(value) {
    if (value === MISSING || value === undefined) return "Missing · مفقود";
    if (isOperator(value)) {
      if (value.operator === "greater_than") return `> ${value.value}`;
      if (value.operator === "at_least") return `≥ ${value.value}`;
      if (value.operator === "less_than_or_equal") return `≤ ${value.value}`;
      return `${value.operator} ${value.value}`;
    }
    if (value === true) return "true · صحيح";
    if (value === false) return "false · غير صحيح";
    if (value === null) return "null";
    if (Array.isArray(value)) return value.length ? value.join(", ") : "[ ]";
    if (isObject(value)) return JSON.stringify(value);
    return String(value);
  }

  function createCell(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function renderRows(artifact) {
    comparisonBody.replaceChildren();
    state.rows.forEach((row) => {
      const tr = document.createElement("tr");
      tr.dataset.status = row.status;

      const label = friendlyLabel(row.path);
      const nameCell = createCell("td", "check-name");
      nameCell.append(createCell("b", "", label.en), createCell("small", "", label.ar));

      const expectedCell = createCell("td");
      expectedCell.append(createCell("span", "value-code", displayValue(row.expected)));

      const actualCell = createCell("td");
      actualCell.append(createCell("span", "value-code", displayValue(row.actual)));

      const statusCell = createCell("td");
      const statusText = row.status === "match"
        ? "✓ Match · مطابق"
        : row.status === "needs_fix"
          ? "× Needs fix · يحتاج إصلاحًا"
          : "! Review · راجع";
      statusCell.append(createCell("span", `status-pill ${row.status}`, statusText));

      const revisit = createCell("td");
      revisit.append(createCell("span", "cell-chip", revisitCell(artifact.scope, row.path, artifact.cell)));
      tr.append(nameCell, expectedCell, actualCell, statusCell, revisit);
      comparisonBody.append(tr);
    });
    applyFilter(state.filter);
  }

  function applyFilter(filter) {
    state.filter = ["all", "review", "needs_fix", "match"].includes(filter) ? filter : "all";
    filterButtons.forEach((button) => {
      const active = button.dataset.filter === state.filter;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    comparisonBody.querySelectorAll("tr").forEach((row) => {
      row.hidden = state.filter !== "all" && row.dataset.status !== state.filter;
    });
  }

  function renderResult(artifact, file) {
    const matched = state.rows.filter((row) => row.status === "match").length;
    const review = state.rows.filter((row) => row.status === "review").length;
    const needsFix = state.rows.filter((row) => row.status === "needs_fix").length;
    const issueCount = review + needsFix;
    document.querySelector("#detected-name").textContent = artifact.name;
    document.querySelector("#detected-cell").textContent = artifact.cell;
    document.querySelector("#pass-count").textContent = String(matched);
    document.querySelector("#review-count").textContent = String(review);
    document.querySelector("#fix-count").textContent = String(needsFix);

    const verdictCard = document.querySelector("#verdict-card");
    verdictCard.dataset.verdict = issueCount === 0 ? "pass" : "review";
    document.querySelector("#verdict-en").textContent = issueCount === 0 ? "Ready to continue" : `${needsFix ? "Fix" : "Review"} ${artifact.cell}`;
    document.querySelector("#verdict-ar").textContent = issueCount === 0 ? "جاهز للمتابعة" : `${needsFix ? "أصلح" : "راجع"} ${artifact.cell}`;

    selectedFile.hidden = false;
    selectedFile.querySelector("[data-file-name]").textContent = file.name;
    selectedFile.querySelector("[data-file-meta]").textContent = `${(file.size / 1024).toFixed(1)} KB · ${state.rows.length} stable checks`;
    resultsPanel.hidden = false;
    setProcess(issueCount === 0 ? 3 : 2);
    renderRows(artifact);
    resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    announce(issueCount === 0
      ? `${artifact.name}. All ${matched} stable checks match.`
      : `${artifact.name}. ${matched} match, ${review} need review, and ${needsFix} need a fix.`);
  }

  function resetComparison({ focus = false } = {}) {
    fileInput.value = "";
    selectedFile.hidden = true;
    resultsPanel.hidden = true;
    state.rows = [];
    hideError();
    setProcess(0);
    if (focus) dropZone.focus();
  }

  function readFile(file) {
    hideError();
    resultsPanel.hidden = true;
    if (!file) return;
    if (!/\.json$/i.test(file.name)) {
      showError("JSON file required · يلزم ملف JSON", "Choose a file whose name ends in .json. · اختر ملفًا ينتهي اسمه بـ .json.");
      return;
    }
    if (file.size > MAX_FILE_BYTES) {
      showError("File is too large · الملف كبير", "Maximum size is 1 MB. Generate the compact JSON artifact again. · الحد الأقصى 1 MB؛ أعد إنشاء ملف JSON المختصر.");
      return;
    }
    if (file.size === 0) {
      showError("Empty file · ملف فارغ", "Choose a generated notebook artifact with JSON content. · اختر مخرج JSON أنشأه الدفتر.");
      return;
    }

    setProcess(1);
    const reader = new FileReader();
    reader.onerror = () => showError("Could not read file · تعذرت قراءة الملف", "The browser could not read this local file. Choose it again. · تعذر على المتصفح قراءة الملف المحلي؛ اختره مرة أخرى.");
    reader.onload = async () => {
      try {
        const payload = JSON.parse(String(reader.result));
        if (!isObject(payload)) throw new Error("ROOT_NOT_OBJECT");
        validateJsonShape(payload);
        await profilePromise;
        const artifact = normalizeArtifact(payload, file.name);
        setProcess(2);
        state.rows = compareArtifact(artifact);
        if (!state.rows.length) throw new Error("NO_DECLARED_FIELDS");
        renderResult(artifact, file);
      } catch (error) {
        const code = error instanceof Error ? error.message : "INVALID_JSON";
        if (["UNRECOGNIZED_ARTIFACT", "NO_DECLARED_FIELDS"].includes(code)) {
          showError("Output not recognized · لم يتم التعرف على المخرج", "Use a JSON generated by C0, C9, C20, C23, C27, C28, or C29. · استخدم ملف JSON أنشأته إحدى الخلايا C0 أو C9 أو C20 أو C23 أو C27 أو C28 أو C29.");
        } else if (["JSON_TOO_COMPLEX", "JSON_TOO_DEEP"].includes(code)) {
          showError("JSON is too complex · بنية JSON معقدة", "Use the compact artifact generated by the notebook. · استخدم المخرج المختصر الذي أنشأه الدفتر.");
        } else if (code === "REFERENCE_UNAVAILABLE") {
          showError("Reference unavailable · المرجع غير متاح", "Refresh this page while online, then choose the file again. · حدّث الصفحة أثناء الاتصال ثم اختر الملف مجددًا.");
        } else {
          showError("Invalid JSON · ملف JSON غير صالح", "The file could not be parsed. Regenerate it from the named notebook cell. · تعذرت قراءة البنية؛ أعد إنشاء الملف من خلية الدفتر المحددة.");
        }
        setProcess(0);
      }
    };
    reader.readAsText(file, "utf-8");
  }

  applyLanguage(safeStorageRead("rafeeq-language") || "both");
  document.querySelectorAll("[data-lang-switch]").forEach((button) => {
    button.addEventListener("click", () => applyLanguage(button.dataset.langSwitch));
  });

  dropZone.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      fileInput.click();
    }
  });
  fileInput.addEventListener("change", () => readFile(fileInput.files?.[0]));
  ["dragenter", "dragover"].forEach((name) => dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    dropZone.classList.add("is-dragging");
  }));
  ["dragleave", "drop"].forEach((name) => dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    dropZone.classList.remove("is-dragging");
  }));
  dropZone.addEventListener("drop", (event) => readFile(event.dataTransfer?.files?.[0]));
  clearButton.addEventListener("click", () => resetComparison({ focus: true }));
  compareAnother.addEventListener("click", () => resetComparison({ focus: true }));
  filterButtons.forEach((button) => button.addEventListener("click", () => applyFilter(button.dataset.filter)));
})();
