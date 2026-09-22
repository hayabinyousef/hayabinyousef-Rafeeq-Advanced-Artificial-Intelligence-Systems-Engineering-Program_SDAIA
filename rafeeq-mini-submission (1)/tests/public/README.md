# Public tests · الاختبارات العامة

| English | العربية |
|---|---:|
| This suite is a visible engineering contract, not a hidden grading mechanism. It uses only Python's standard library and the synthetic files in `data/public/`. | هذه الحزمة عقد هندسي مرئي وليست آلية تقييم خفية. تستخدم مكتبة Python القياسية فقط والملفات الاصطناعية داخل `data/public/`. |

## Coverage · نطاق التغطية

| Test | Public evidence · الدليل العام |
|---|---|
| `test_state_contract.py` | Typed trace-safe state · حالة محددة النوع وآمنة للتتبع |
| `test_termination.py` | Exact budgets: 6 steps, 12 transitions, 2 handoffs · الحدود الدقيقة: 6 خطوات، و12 انتقالًا، وتفويضان |
| `test_tool_scope.py` | Ownership and minimum tool arguments · الملكية والحد الأدنى من معاملات الأدوات |
| `test_mcp_smoke.py` | Real local `stdio`, discovery, owned and denied reads · نقل `stdio` محلي فعلي، واكتشاف الأدوات، والقراءة المملوكة والمرفوضة |
| `test_memory_scope.py` | Filter-before-rank, expiry and active policy · التصفية قبل الترتيب، والانتهاء، والسياسة الفعالة |
| `test_routing.py` | Arabic/English public routing cases · حالات التوجيه العامة بالعربية والإنجليزية |
| `test_refund_gate.py` | SAR 500 boundary, approval, prior refund, idempotency and no write retry · حد 500 ريال، والموافقة، والاسترداد السابق، ومنع التكرار، وعدم إعادة محاولة الكتابة |
| `test_reflection_bound.py` | One reflection maximum · انعكاس واحد كحد أقصى |
| `test_security.py` | Injection flagging, untrusted tool text and redacted trace · رصد حقن الأوامر، ونص الأداة غير الموثوق، والتتبع المنقح |
| `test_assessment_contract.py` | Canonical 8 functional + 8 security cases, exact risk flags, metrics, and named gates · عقد 8 حالات وظيفية + 8 أمنية وأعلام مخاطر دقيقة ومقاييس وبوابات مسماة |
| `test_readiness.py` | Required public assets and safe offline defaults · الأصول العامة المطلوبة والإعدادات الآمنة غير المتصلة |
| `test_preflight_readiness.py` | Automated repository checks remain separate from manual hosted-Colab acceptance · فصل فحوص المستودع الآلية عن قبول Colab اليدوي |
| `test_export_contract.py` | One safe learner workflow, completed TODO evidence and no course-only files · مسار تحقق واحد للمتدرب، ودليل إكمال التمارين، ومنع ملفات إدارة الدورة |
| `test_reference_contract.py` | Day 3 comparison references stay aligned with the canonical 16-case assessment · بقاء مراجع مقارنة اليوم الثالث متسقة مع التقييم الموحّد ذي 16 حالة |

## Run · التشغيل

From the repository root, with no API key and no network call:

من جذر المستودع، دون مفتاح API ودون اتصال شبكي:

```bash
python -m unittest discover -s tests/public -p 'test_*.py'
```

A failure names a public contract that needs attention. The suite contains no hidden cases, scores, instructor notes or solution branches.

يسمي الفشل عقدًا عامًا يحتاج إلى معالجة. لا تتضمن الحزمة حالات مخفية أو درجات أو ملاحظات مدرب أو فروع حلول.
