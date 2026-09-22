# Cumulative Colab notebook · دفتر كولاب التراكمي

| English | العربية |
|---|---|
| The learner release uses **one notebook**: `Rafeeq_Mini_Capstone.ipynb`. You build the same project in small, tested steps from `C0` to `C29`. | يستخدم إصدار المتدرب **دفترًا واحدًا** باسم `Rafeeq_Mini_Capstone.ipynb`. ستبني المشروع نفسه بخطوات صغيرة ومختبرة من `C0` إلى `C29`. |
| Use the standard **Google Colab Free CPU** runtime. The default mode is `LLM_MODE=stub`; no paid model, GPU, terminal, token, or API key is required. | استخدم بيئة **Google Colab Free CPU** القياسية. الوضع الافتراضي هو `LLM_MODE=stub`؛ لا تحتاج إلى نموذج مدفوع أو GPU أو Terminal أو رمز وصول أو مفتاح API. |

## Before the first run · قبل التشغيل الأول

1. Open the notebook from the official `almiyead-rgb` course repository with this **[Google Colab link](https://colab.research.google.com/github/almiyead-rgb/rafeeq-agentic-ai-labs/blob/v0.9.0-rc3/notebooks/Rafeeq_Mini_Capstone.ipynb)**. Do not look for it in a learner repository. · افتح الدفتر من مستودع الدورة الرسمي `almiyead-rgb` عبر **[رابط Google Colab](https://colab.research.google.com/github/almiyead-rgb/rafeeq-agentic-ai-labs/blob/v0.9.0-rc3/notebooks/Rafeeq_Mini_Capstone.ipynb)**، ولا تبحث عنه في مستودع المتدرب.
2. In Colab select **File → Save a copy in Drive**. Work only in that Drive copy. · في كولاب اختر **File → Save a copy in Drive**، واعمل فقط على نسخة Drive.
3. During preflight, create your own public GitHub repository and add only `LEARNING_PROGRESS.md` from the safe template. Update its public status after C9 and C20, but keep code and runtime evidence in Drive until C29. · أثناء التجهيز المسبق أنشئ مستودع GitHub عامًا، وأضف فقط `LEARNING_PROGRESS.md` من القالب الآمن. حدّث حالته العامة بعد C9 وC20، وأبقِ الكود وأدلة التشغيل في Drive حتى C29.
4. Run `C0_ENV_DOCTOR`. Continue only when it prints `C0 = READY` and `all_passed=true`. · شغّل `C0_ENV_DOCTOR`. لا تتابع إلا بعد ظهور `C0 = READY` و`all_passed=true`.
5. Run cells from top to bottom. Complete the `TODO`, run its public check, then move forward. · شغّل الخلايا من الأعلى إلى الأسفل. أكمل `TODO`، ثم شغّل الفحص العام، وبعد نجاحه انتقل للخطوة التالية.
6. Never paste real data, passwords, tokens, private links, or API keys into a cell, output, report, or help request. · لا تلصق بيانات حقيقية أو كلمات مرور أو رموز وصول أو روابط خاصة أو مفاتيح API في خلية أو مخرج أو تقرير أو طلب مساعدة.

Official entry points: [Google Colab](https://colab.research.google.com/) · [Colab FAQ](https://research.google.com/colaboratory/faq.html)

## Three-day cell map · خريطة الخلايا خلال ثلاثة أيام

The name after each cell number describes its learning responsibility. The notebook itself is the execution authority. Do not rename, reorder, or delete graded cells.

يصف الاسم بعد رقم الخلية مسؤوليتها التعليمية. يبقى الدفتر نفسه هو المرجع التنفيذي. لا تغيّر أسماء الخلايا المقيمة أو ترتيبها أو تحذفها.

### Day 1 — Core and tools · اليوم الأول — النواة والأدوات

| Cell | English outcome | الناتج بالعربية |
|---|---|---|
| `C0_ENV_DOCTOR` | Verify runtime, files, versions, and safe defaults. | التحقق من البيئة والملفات والإصدارات والإعدادات الآمنة. |
| `C1_ARCHITECTURE` | Read the Rafeeq flow, components, boundaries, and safe operating assumptions. | قراءة تدفق رفيق ومكوناته وحدوده وافتراضات التشغيل الآمن. |
| `C2_TYPED_STATE` | Define the agent state and its required fields. | تعريف حالة الوكيل وحقولها الإلزامية. |
| `C3_BOUNDED_GRAPH` | Build a graph with explicit routes, a step limit, and safe termination. | بناء مخطط بمسارات صريحة وحد للخطوات وإنهاء آمن. |
| `C4_REASONING_TRACES` | Record observable decisions, tool calls, results, and counters—not private chain-of-thought. | تسجيل القرارات المرصودة واستدعاءات الأدوات والنتائج والعدادات، دون التفكير الداخلي الخاص. |
| `C5_REACT_ORDERS` | Apply bounded ReAct to synthetic order requests. | تطبيق ReAct المحدود على طلبات شراء مصطنعة. |
| `C6_TOOL_SCHEMA` | Validate local-tool inputs and structured outputs. | التحقق من مدخلات الأدوات المحلية ومخرجاتها المنظمة. |
| `C7_MCP_SERVER` | Start the simulated local MCP server with an explicit allow-list. | تشغيل خادم MCP المحلي المحاكى بقائمة سماح صريحة. |
| `C8_MCP_CLIENT` | Connect the client and inspect the allowed MCP capabilities. | ربط العميل وفحص صلاحيات MCP المسموحة. |
| `C9_DAY1_GATE` | Prove the Day 1 flow and save the first checkpoint. | إثبات تدفق اليوم الأول وحفظ نقطة التقدم الأولى. |

### Day 2 — Memory and orchestration · اليوم الثاني — الذاكرة والتنسيق

| Cell | English outcome | الناتج بالعربية |
|---|---|---|
| `C10_RESTORE` | Restore the supplied public files and verify the existing C0–C9 context and Day 1 gate. After a Runtime reset, rerun C0–C9 first; C10 does not restore Python memory. | استعادة الملفات العامة المرفقة والتحقق من سياق C0–C9 القائم وبوابة اليوم الأول. بعد إعادة ضبط Runtime، أعد تشغيل C0–C9 أولًا؛ فـC10 لا تستعيد ذاكرة Python. |
| `C11_SESSION_MEMORY` | Keep short-term context inside one session. | حفظ السياق قصير المدى داخل جلسة واحدة. |
| `C12_SCOPED_RECALL` | Retrieve long-term memory only inside the correct customer scope. | استرجاع الذاكرة طويلة المدى داخل نطاق العميل الصحيح فقط. |
| `C13_POLICY_RETRIEVAL` | Retrieve only the active, relevant policy chunk. | استرجاع مقطع السياسة الساري والمرتبط فقط. |
| `C14_SPECIALISTS` | Define exactly two bounded agents: `OrdersAgent` and `RefundAgent`; policy retrieval remains a supporting service, not a third agent. | تعريف وكيلين محدودين بالضبط: `OrdersAgent` و`RefundAgent`؛ ويبقى استرجاع السياسة خدمة داعمة لا وكيلًا ثالثًا. |
| `C15_SUPERVISOR` | Route each validated task to the correct specialist. | توجيه كل مهمة متحقق منها إلى الوكيل المتخصص الصحيح. |
| `C16_TYPED_HANDOFF` | Apply typed delegation with validated task and result packets. | تطبيق التفويض المحدد النوع بحزم مهام ونتائج متحقق منها. |
| `C17_PLAN_EXECUTE` | Separate a short plan from controlled step-by-step execution. | فصل الخطة القصيرة عن التنفيذ المنضبط خطوة بخطوة. |
| `C18_REFUND_GATE` | Pause simulated refunds above SAR 500 for documented human approval. | إيقاف الاستردادات المحاكية الأعلى من 500 ريال حتى توثيق الموافقة البشرية. |
| `C19_INTERRUPT_RESUME` | Interrupt safely for approval, then resume without duplicating the action. | الإيقاف الآمن للموافقة ثم الاستئناف دون تكرار الإجراء. |
| `C20_DAY2_GATE` | Prove memory isolation, routing, and approval behavior. | إثبات عزل الذاكرة والتوجيه وسلوك الموافقة. |

### Day 3 — Security, quality, and submission · اليوم الثالث — الأمن والجودة والتسليم

| Cell | English outcome | الناتج بالعربية |
|---|---|---|
| `C21_THREAT_MODEL` | Identify assets, trust boundaries, threats, and controls. | تحديد الأصول وحدود الثقة والتهديدات والضوابط. |
| `C22_ATTACK_SUITE` | Run the supplied public injection, misuse, budget, and approval-bypass cases. | تشغيل حالات الحقن وإساءة الاستخدام واستنزاف الخطوات وتجاوز الموافقة العامة المرفقة. |
| `C23_GUARD_FIX_RETEST` | Strengthen the guardrail and rerun the same public attack cases. | تقوية الحاجز وإعادة تشغيل حالات الهجوم العامة نفسها. |
| `C24_REFLECTION_GATE` | Apply one bounded reflection cycle only when the gate allows it. | تطبيق دورة مراجعة ذاتية واحدة محدودة عندما تسمح البوابة بذلك. |
| `C25_TRACE_EVAL` | Evaluate sanitized traces and export `reports/trace.jsonl`. | تقييم سجلات التتبع المنقحة وتصدير `reports/trace.jsonl`. |
| `C26_ONE_OPTIMIZATION` | Apply one measured performance or cost optimization and compare before/after. | تطبيق تحسين واحد مقاس للأداء أو التكلفة ومقارنة قبل/بعد. |
| `C27_SCORECARD` | Produce assessment results and the monitoring dashboard. | إنتاج نتائج التقييم ولوحة المراقبة. |
| `C28_READINESS` | Generate the two reports and complete final readiness checks; it does not create the submission manifest or ZIP. | توليد التقريرين وإكمال فحوص الجاهزية النهائية؛ ولا تنشئ بيان التسليم أو ملف ZIP. |
| `C29_EXPORT_SAFETY_CHECK` | Block unsafe files, verify required outputs, then create `reports/submission_manifest.json` and `rafeeq-mini-submission.zip` when final export is enabled. | حظر الملفات غير الآمنة والتحقق من المخرجات، ثم إنشاء `reports/submission_manifest.json` و`rafeeq-mini-submission.zip` عند تفعيل التصدير النهائي. |

Required learner reports: `reports/PROJECT_REPORT.md` and `reports/SECURITY_ASSESSMENT.md`. Required generated artifacts: `reports/trace.jsonl`, `reports/assessment_results.json`, `reports/monitoring_dashboard.png`, and `reports/submission_manifest.json`. All six sanitized outputs must be included with the extracted clean C29 contents uploaded to the learner repository.

After extracting C29, copy `reports/templates/EVIDENCE_CARD_TEMPLATE.md` to `reports/EVIDENCE_CARD.md` and complete one sanitized card per day. This required instructor-assessment record is added after export and is not hashed by the C29 manifest.

The C29 ZIP excludes the notebook currently open in Colab and `reports/checkpoints/`. Download the completed notebook separately through **File → Download → Download .ipynb**, name it `Rafeeq_Mini_Capstone.ipynb`, and place it under `notebooks/` before uploading the extracted contents.

تقريرا المتدرب الإلزاميان: `reports/PROJECT_REPORT.md` و`reports/SECURITY_ASSESSMENT.md`. والملفات المولدة الإلزامية: `reports/trace.jsonl` و`reports/assessment_results.json` و`reports/monitoring_dashboard.png` و`reports/submission_manifest.json`. تُضمّن المخرجات الستة المنقحة مع محتويات C29 النظيفة المستخرجة التي تُرفع إلى مستودع المتدرب.

بعد فك حزمة C29 انسخ `reports/templates/EVIDENCE_CARD_TEMPLATE.md` إلى `reports/EVIDENCE_CARD.md` وأكمل بطاقة منقحة لكل يوم. يضاف سجل تقييم المدربة الإلزامي هذا بعد التصدير، ولا يتضمنه التجزئة داخل بيان C29.

تستبعد حزمة C29 دفتر كولاب الجاري و`reports/checkpoints/`. نزّل الدفتر المكتمل منفصلًا عبر **File → Download → Download .ipynb**، وسمّه `Rafeeq_Mini_Capstone.ipynb`، ثم ضعه داخل `notebooks/` قبل رفع المحتويات المستخرجة.

## Daily gates and checkpoint messages · بوابات الأيام ورسائل نقاط التقدم

| Gate | Continue only when · لا تنتقل إلا بعد | Checkpoint label / final Git message · تسمية النقطة / رسالة Git النهائية |
|---|---|---|
| `C9_DAY1_GATE` | Day 1 public checks and the bounded MCP capability list produce `all_passed=true`. · تنتج فحوص اليوم الأول وقائمة صلاحيات MCP المحدودة القيمة `all_passed=true`. | `docs(day1): record C9 gate` |
| `C20_DAY2_GATE` | Scoped recall, typed delegation, routing, refund-gate, and interrupt/resume tests produce `all_passed=true`. · تنتج اختبارات الاسترجاع المعزول والتفويض المحدد والتوجيه وبوابة الاسترداد والإيقاف/الاستئناف القيمة `all_passed=true`. | `docs(day2): record C20 gate` |
| `C29_EXPORT_SAFETY_CHECK` | With final export enabled, both reports and all required artifacts exist, the safety scan passes, and the cell prints `FINAL_EXPORT_CREATED`. · عند تفعيل التصدير النهائي، يكون التقريران والملفات المطلوبة موجودة، وينجح فحص الأمان، وتطبع الخلية `FINAL_EXPORT_CREATED`. | `feat: submit Rafeeq Mini capstone` |

Save the notebook in Drive after each completed section. The Day 1 and Day 2 Git commits update only `LEARNING_PROGRESS.md`; the final line becomes the commit message when the extracted clean C29 contents are uploaded. Git does **not** preserve Colab memory, installed packages, or unsaved outputs.

احفظ الدفتر في Drive بعد كل جزء مكتمل. يحدّث Commit اليوم الأول واليوم الثاني ملف `LEARNING_PROGRESS.md` فقط، ويصبح السطر الأخير رسالة Commit عند رفع محتويات C29 النظيفة المستخرجة. لا يحفظ Git ذاكرة كولاب أو الحزم المثبتة أو المخرجات غير المحفوظة.

## Notebook rules · قواعد الدفتر

- Change only learner `TODO` areas unless the instructor explicitly identifies another cell. · عدّل مناطق `TODO` الخاصة بالمتدرب فقط ما لم تحدد المدربة خلية أخرى صراحة.
- Each exercise keeps one validator-counted `TODO-N` marker. Arabic companion guidance appears as `مهمة المتدرب` text/comment without adding another `TODO` marker. · يحتفظ كل تمرين بعلامة `TODO-N` واحدة يحسبها المتحقق، وتظهر الإرشادات العربية المصاحبة بنص/تعليق `مهمة المتدرب` دون إضافة علامة `TODO` أخرى.
- Do not disable, rewrite, or bypass a public check. · لا تعطل فحصًا عامًا أو تعيد كتابته أو تتحايل عليه.
- Do not add solutions, answer keys, private instructor material, or hidden evaluations. · لا تضف حلولًا أو مفاتيح إجابة أو مواد خاصة بالمدربة أو تقييمات خفية.
- Keep all examples synthetic. Refunds and tool actions are simulations only. · اجعل جميع الأمثلة مصطنعة؛ الاستردادات وإجراءات الأدوات محاكاة فقط.
- Store short decision records, not hidden reasoning or chain-of-thought. · خزّن سجلات قرار قصيرة، لا التفكير الداخلي أو سلسلة الأفكار.
- If the runtime resets, follow [`recovery/README.md`](../recovery/README.md). · عند إعادة ضبط البيئة اتبع [`recovery/README.md`](../recovery/README.md).
- Before submission, complete [`reports/templates/SUBMISSION_CHECKLIST.md`](../reports/templates/SUBMISSION_CHECKLIST.md). · قبل التسليم أكمل [`reports/templates/SUBMISSION_CHECKLIST.md`](../reports/templates/SUBMISSION_CHECKLIST.md).
