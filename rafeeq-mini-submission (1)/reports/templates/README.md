# Learner report templates · قوالب تقارير المتدرب

These templates turn notebook results into short, auditable project evidence. They do not contain answers, expected scores, hidden tests, or instructor-only material.

تحوّل هذه القوالب نتائج الدفتر إلى أدلة مشروع قصيرة وقابلة للتدقيق. ولا تحتوي على إجابات أو درجات متوقعة أو اختبارات خفية أو مواد خاصة بالمدربة.

## Required files · الملفات المطلوبة

| Template | Notebook output / use | Purpose · الغرض |
|---|---|---|
| [`PROJECT_REPORT_TEMPLATE.md`](PROJECT_REPORT_TEMPLATE.md) | `C28_READINESS` generates `reports/PROJECT_REPORT.md`; use the template only as an enrichment reference. · تولّد C28 التقرير، ويستخدم القالب مرجعًا للإثراء فقط. | Architecture, implementation, evaluation, and limitations. · المعمارية والتنفيذ والتقييم والقيود. |
| [`SECURITY_ASSESSMENT_TEMPLATE.md`](SECURITY_ASSESSMENT_TEMPLATE.md) | `C23_GUARD_FIX_RETEST` generates `reports/SECURITY_ASSESSMENT.md`; use the template only as an enrichment reference. · تولّد C23 التقييم، ويستخدم القالب مرجعًا للإثراء فقط. | Threats, controls, attack tests, and residual risk. · التهديدات والضوابط واختبارات الهجوم والمخاطر المتبقية. |
| [`EVIDENCE_CARD_TEMPLATE.md`](EVIDENCE_CARD_TEMPLATE.md) | Required after C29 extraction · إلزامي بعد فك حزمة C29 | Copy to `reports/EVIDENCE_CARD.md` and complete one concise, sanitized card per day for instructor assessment. It is not an automated C29 output or manifest-hashed file. · انسخه إلى `reports/EVIDENCE_CARD.md` وأكمل بطاقة مختصرة ومنقحة لكل يوم لتقييم المدربة. ليس مخرجًا آليًا من C29 ولا ملفًا مجزأً في البيان. |
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | Use locally before upload; not an additional deliverable. · استخدمها محليًا قبل الرفع وليست مخرجًا إضافيًا. | Final safety, structure, and pass gate. · بوابة السلامة والبنية والاجتياز النهائية. |

The final clean run must also generate `reports/trace.jsonl`, `reports/assessment_results.json`, `reports/monitoring_dashboard.png`, and `reports/submission_manifest.json`. These four sanitized artifacts must be included with the extracted C29 contents uploaded to the learner repository.

يجب أن ينتج التشغيل النهائي النظيف أيضًا `reports/trace.jsonl` و`reports/assessment_results.json` و`reports/monitoring_dashboard.png` و`reports/submission_manifest.json`. تُضمّن هذه الملفات الأربعة المنقحة مع محتويات C29 المستخرجة التي تُرفع إلى مستودع المتدرب.

When the enabled `C29_EXPORT_SAFETY_CHECK` prints `FINAL_EXPORT_CREATED`, the guarded export has created `rafeeq-mini-submission.zip` as a transport container. Extract it and upload its clean contents; do not upload the ZIP itself or use it as a replacement for visible repository files.

عندما يطبع التشغيل المفعّل لـ`C29_EXPORT_SAFETY_CHECK` العبارة `FINAL_EXPORT_CREATED`، يكون التصدير المحمي قد أنشأ `rafeeq-mini-submission.zip` بوصفه حاوية نقل. فك ضغطه وارفع محتوياته النظيفة؛ لا ترفع ملف ZIP نفسه ولا تستخدمه بديلًا عن ملفات المستودع الظاهرة.

The ZIP deliberately excludes the notebook currently open in Colab and `reports/checkpoints/`. Before uploading, select **File → Download → Download .ipynb** in Colab, name the file `Rafeeq_Mini_Capstone.ipynb`, and place it inside the extracted `notebooks/` folder.

تستبعد الحزمة عمدًا دفتر كولاب الجاري و`reports/checkpoints/`. قبل الرفع اختر في كولاب **File → Download → Download .ipynb**، وسمّ الملف `Rafeeq_Mini_Capstone.ipynb`، ثم ضعه داخل مجلد `notebooks/` المستخرج.

## How to use the templates · طريقة استخدام القوالب

1. Create a public GitHub repository during preflight and add only the safe `LEARNING_PROGRESS.md`; keep code and runtime evidence in the saved Drive notebook through C29. `C23` and `C28` generate the two required learner reports automatically. · أنشئ مستودع GitHub عامًا أثناء التجهيز وأضف `LEARNING_PROGRESS.md` الآمن فقط، وأبقِ الكود وأدلة التشغيل في دفتر Drive حتى C29. تولد `C23` و`C28` تقريري المتدرب الإلزاميين تلقائيًا.
2. Review the generated values and limitations. Do not invent a metric or replace a failed result with `PASS`. · راجع القيم والقيود المولدة، ولا تخترع مقياسًا أو تستبدل نتيجة فاشلة بـ`PASS`.
3. Use the detailed templates only as a reference or when the instructor requests additional analysis. If you enrich a generated report, do so after its final generating cell so a rerun does not overwrite your edits. · استخدم القوالب المفصلة مرجعًا أو عند طلب المدربة تحليلًا إضافيًا. وإذا أثريت تقريرًا مولدًا فافعل ذلك بعد آخر خلية تولده حتى لا تمحو إعادة التشغيل تعديلاتك.
4. Link each added claim to a notebook cell, a public case or metric, its result, and the assessment `run_id` from `reports/assessment_results.json` when available. Do not invent a C29 export ID. · اربط كل ادعاء إضافي بخلية في الدفتر وحالة عامة أو مقياس ونتيجته، وبـ`run_id` من `reports/assessment_results.json` عند توفره. لا تخترع معرفًا لتصدير C29.
5. Use synthetic fixture IDs and sanitized summaries. Reference the generated artifacts; do not paste raw traces or full customer-like records into a public report. · استخدم معرفات الحالات المصطنعة وملخصات منقحة، وأشر إلى الملفات المولدة دون لصق سجلات تتبع خام أو سجلات كاملة تشبه بيانات العملاء داخل تقرير عام.
6. Run `C29_EXPORT_SAFETY_CHECK`, download the completed notebook separately, extract the package, and copy this template to `reports/EVIDENCE_CARD.md`. Complete its three cards using your public `learner_id` and actual results only. · شغّل `C29_EXPORT_SAFETY_CHECK`، ونزّل الدفتر المكتمل منفصلًا، وفك الحزمة، وانسخ هذا القالب إلى `reports/EVIDENCE_CARD.md`. أكمل بطاقاته الثلاث باستخدام `learner_id` العام والنتائج الفعلية فقط.
7. Upload only the combined clean contents beside the existing safe progress log, then wait for **Actions → Learner submission quality** to turn green for the exact final commit. · ارفع المحتويات النظيفة المدمجة بجانب سجل التقدم الآمن الموجود، ثم انتظر نجاح **Actions ← Learner submission quality** لنفس Commit النهائي.

## Evidence standard · معيار الدليل

A strong entry answers five questions: **What was tested? What input was used? What was expected? What happened? Where can it be reproduced?**

تجيب خانة الدليل الجيدة عن خمسة أسئلة: **ماذا اختُبر؟ ما المدخل المستخدم؟ ما المتوقع؟ ماذا حدث؟ وأين يمكن تكراره؟**

Screenshots alone are weak evidence. Prefer cell IDs, test case IDs, compact metrics, and the assessment `run_id` when available. After C29, the manifest timestamp and SHA-256 values may verify exported files, but they are not required fields inside reports generated earlier. A screenshot may support the record, but it must not expose personal data, a token, a private URL, or a browser account.

لقطة الشاشة وحدها دليل ضعيف. استخدم أرقام الخلايا وحالات الاختبار والمقاييس المختصرة و`run_id` للتقييم عند توفره. بعد C29 يمكن استخدام وقت البيان وقيم SHA-256 للتحقق من الملفات المصدرة، لكنها ليست حقولًا مطلوبة داخل التقارير المولدة سابقًا. يمكن أن تدعم اللقطة السجل، لكن يجب ألا تكشف بيانات شخصية أو رمز وصول أو رابطًا خاصًا أو حساب المتصفح.

## Never include · محتوى ممنوع

- Real customer, employee, trainee, order, payment, or support data. · بيانات حقيقية لعميل أو موظف أو متدرب أو طلب أو دفعة أو دعم.
- Passwords, tokens, API keys, cookies, private repository links, `.env`, or environment files containing secrets. The supplied credential-free `.env.example` is allowed. · كلمات مرور أو رموز وصول أو مفاتيح API أو Cookies أو روابط مستودعات خاصة أو `.env` أو ملفات بيئة تحمل أسرارًا. يُسمح بملف `.env.example` المرفق والخالي من بيانات الدخول.
- Completed solutions copied from another person, answer keys, instructor notes, scoring rules, or hidden tests. · حلول مكتملة منسوخة أو مفاتيح إجابة أو ملاحظات المدربة أو قواعد الدرجات أو اختبارات خفية.
- Private chain-of-thought. Record only the final decision, tool, result, route, counters, and a short operational rationale. · التفكير الداخلي الخاص؛ سجل القرار النهائي والأداة والنتيجة والمسار والعدادات ومبررًا تشغيليًا قصيرًا فقط.
- `rafeeq-mini-submission.zip` or raw runtime artifacts inside the public repository. · ملف `rafeeq-mini-submission.zip` أو آثار بيئة التشغيل الخام داخل المستودع العام.
