# Local MCP server · خادم MCP المحلي

| English | العربية |
|---|---|
| The lab uses a small local server to demonstrate the **Model Context Protocol (MCP)** without a paid service or public deployment. It runs inside the temporary Colab runtime and communicates through `stdio`. | يستخدم اللاب خادمًا محليًا صغيرًا لشرح **Model Context Protocol (MCP)** دون خدمة مدفوعة أو نشر عام. يعمل داخل بيئة كولاب المؤقتة ويتواصل عبر `stdio`. |
| It exposes simulated resources and tools only. It must never connect to a real order, payment, customer, or enterprise system. | يعرض موارد وأدوات محاكية فقط. ويُمنع ربطه بنظام حقيقي للطلبات أو المدفوعات أو العملاء أو أنظمة المؤسسة. |

Official reference: [Model Context Protocol documentation](https://modelcontextprotocol.io/docs/getting-started/intro)

## What the learner proves in C7–C8 · ما يثبته المتدرب في C7–C8

1. The client starts the local server and negotiates the current protocol through stateless per-request metadata. · يبدأ العميل الخادم المحلي ويتفاوض على البروتوكول الحالي عبر بيانات وصفية عديمة الحالة لكل طلب.
2. The client lists only the allowed simulated capabilities. · يعرض العميل الصلاحيات المحاكية المسموحة فقط.
3. Every tool has a clear input schema and a structured result. · لكل أداة مخطط مدخلات واضح ونتيجة منظمة.
4. C8 runs the supplied valid call and one supplied rejected schema/extra-field call. The rejected call must return `INVALID_ARGUMENT` without a write or data disclosure. · تشغّل C8 الاستدعاء الصحيح المرفق، واستدعاءً واحدًا مرفوضًا مرفقًا يخالف المخطط/يضيف حقلًا زائدًا. يجب أن يعيد الاستدعاء المرفوض `INVALID_ARGUMENT` دون كتابة أو كشف بيانات.
5. Calls are bounded by validation, timeouts, and the agent step limit. · تُقيّد الاستدعاءات بالتحقق والمهلة وحد خطوات الوكيل.
6. The trace stores the tool name, result status, duration, counters, and safe error code—never raw arguments, credentials, or private chain-of-thought. · يخزن سجل التتبع اسم الأداة وحالة النتيجة والمدة والعدادات ورمز الخطأ الآمن، دون معاملات خام أو بيانات دخول أو تفكير داخلي خاص.

## Learner workflow · مسار المتدرب

| Step | English | العربية |
|---|---|---|
| 1 | Run notebook cells `C0–C6` successfully. | شغّل خلايا الدفتر `C0–C6` بنجاح. |
| 2 | Run `C7_MCP_SERVER`; do not start a public server or open an internet port. | شغّل `C7_MCP_SERVER`؛ لا تنشئ خادمًا عامًا ولا تفتح منفذًا عبر الإنترنت. |
| 3 | Run `C8_MCP_CLIENT` and inspect the returned capability list against the notebook allow-list. | شغّل `C8_MCP_CLIENT` وافحص قائمة الصلاحيات المعادة مقابل القائمة المسموحة في الدفتر. |
| 4 | Run the supplied valid call, then the supplied schema/extra-field rejection case. Confirm `INVALID_ARGUMENT`, no write, and no data disclosure. | شغّل الاستدعاء الصحيح المرفق، ثم حالة الرفض المرفقة لمخالفة المخطط/الحقل الزائد. تأكد من `INVALID_ARGUMENT` وعدم الكتابة أو كشف البيانات. |
| 5 | Continue to `C9_DAY1_GATE` only when both the valid and rejected-call behaviors match the public checks. | انتقل إلى `C9_DAY1_GATE` فقط عند تطابق سلوكي الاستدعاء الصحيح والمرفوض مع الفحوص العامة. |

## If C7 or C8 fails · عند فشل C7 أو C8

- Confirm that `C0_ENV_DOCTOR` still reports `READY`. · تأكد أن `C0_ENV_DOCTOR` ما زال يعرض `READY`.
- Restart the Colab runtime, then run from `C0` to `C8` in order. · أعد تشغيل بيئة كولاب ثم شغّل من `C0` إلى `C8` بالترتيب.
- Do not install random packages or paste an online fix. · لا تثبت حزمًا عشوائية ولا تلصق إصلاحًا من الإنترنت.
- Record the first error line, the cell ID, and the runtime type; remove any private values before asking for help. · سجّل أول سطر خطأ ورقم الخلية ونوع البيئة، واحذف أي قيم خاصة قبل طلب المساعدة.
- Follow [`recovery/README.md`](../recovery/README.md) if the runtime was reset. · اتبع [`recovery/README.md`](../recovery/README.md) إذا أعيد ضبط البيئة.

This folder must not contain public credentials, production endpoints, unrestricted tools, real transactions, completed solutions, or hidden tests.

يُمنع أن يحتوي هذا المجلد على بيانات دخول عامة أو نقاط اتصال إنتاجية أو أدوات غير مقيدة أو معاملات حقيقية أو حلول مكتملة أو اختبارات خفية.
