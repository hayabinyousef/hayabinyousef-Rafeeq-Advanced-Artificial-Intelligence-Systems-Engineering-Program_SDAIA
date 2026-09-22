# Learner recovery policy · سياسة استعادة عمل المتدرب

**Colab Runtime is temporary. Create the public learner repository during preflight, but publish only the safe `LEARNING_PROGRESS.md` before C29. Google Drive holds the working notebook and gate evidence. After C29, GitHub holds the final clean submission.**

**بيئة Colab مؤقتة. أنشئ مستودع المتدرب العام أثناء التجهيز المسبق، لكن لا تنشر قبل C29 إلا `LEARNING_PROGRESS.md` الآمن. يحتفظ Google Drive بدفتر العمل وأدلة البوابات، وبعد C29 يحتفظ GitHub بالتسليم النهائي النظيف.**

Losing the runtime is normal: installed packages, Python variables, uploaded temporary files, and in-memory state disappear. Your saved Drive notebook remains; after the final C29 upload, the clean GitHub submission also remains.

فقدان بيئة التشغيل أمر طبيعي: تختفي الحزم المثبتة ومتغيرات Python والملفات المؤقتة وحالة الذاكرة. تبقى نسخة الدفتر المحفوظة في Drive، وبعد رفع C29 النهائي يبقى أيضًا التسليم النظيف في GitHub.

## Recovery order · ترتيب الاستعادة

1. Open the latest notebook copy saved in Google Drive. · افتح أحدث نسخة للدفتر محفوظة في Google Drive.
2. Select the standard CPU runtime; do not enable a GPU. · اختر بيئة CPU القياسية ولا تفعل GPU.
3. Run `C0_ENV_DOCTOR`. Stop if it does not return `C0 = READY`. · شغّل `C0_ENV_DOCTOR`. توقف إذا لم يعرض `C0 = READY`.
4. Run completed cells from the top in order. Python state must be rebuilt; do not jump directly to the last cell. · أعد تشغيل الخلايا المكتملة من الأعلى وبالترتيب لإعادة بناء حالة Python؛ لا تقفز مباشرة إلى آخر خلية.
5. Stop at the last completed gate and confirm its exact success marker from the table below. · توقف عند آخر بوابة مكتملة، وتأكد من علامة نجاحها الدقيقة في الجدول أدناه.
6. Compare your Drive copy with the saved gate evidence. Before C29, GitHub contains only the safe public `LEARNING_PROGRESS.md`; Drive remains the source of working evidence. · قارن نسخة Drive بدليل البوابة المحفوظ. قبل C29 لا يحتوي GitHub إلا `LEARNING_PROGRESS.md` العام والآمن، وتبقى نسخة Drive مصدر أدلة العمل.
7. Continue from the first incomplete learner `TODO`. · تابع من أول `TODO` غير مكتمل.

| Gate | Exact success marker · علامة النجاح الدقيقة |
|---|---|
| `C9_DAY1_GATE` | `all_passed=true` |
| `C20_DAY2_GATE` | `all_passed=true` |
| Enabled final `C29_EXPORT_SAFETY_CHECK` · تشغيل C29 النهائي المفعّل | `FINAL_EXPORT_CREATED` |

`FINAL_EXPORT_SKIPPED` means the final switch is off, and `FINAL_EXPORT_BLOCKED` means a precheck failed. Neither is a successful final export.

تعني `FINAL_EXPORT_SKIPPED` أن مفتاح التصدير النهائي مغلق، وتعني `FINAL_EXPORT_BLOCKED` أن فحصًا مسبقًا فشل. لا تعد أي منهما تصديرًا نهائيًا ناجحًا.

## Common recovery cases · حالات الاستعادة الشائعة

| Symptom | Safe action | العَرَض | الإجراء الآمن |
|---|---|---|---|
| `NameError` after reconnecting | Run all completed cells from `C0` in order. | ظهور `NameError` بعد إعادة الاتصال | شغّل جميع الخلايا المكتملة من `C0` بالترتيب. |
| Package/module not found | Rerun the notebook setup cell; use only the pinned dependencies supplied by the course. | تعذر العثور على حزمة أو وحدة | أعد تشغيل خلية التجهيز، واستخدم الاعتماديات المثبتة بالإصدارات المرفقة فقط. |
| Temporary file missing | Rerun the relevant preparation cell. Do not replace it with real data. | فقدان ملف مؤقت | أعد تشغيل خلية التجهيز المرتبطة، ولا تستبدلها ببيانات حقيقية. |
| MCP process stopped | Restart the runtime and rerun through `C8` in order. | توقف عملية MCP | أعد تشغيل البيئة ثم شغّل حتى `C8` بالترتيب. |
| Drive copy is behind | Use the last saved gate evidence or a dated Drive copy as the comparison point; preserve newer correct learner work. | نسخة Drive أقدم | استخدم دليل آخر بوابة محفوظة أو نسخة Drive مؤرخة للمقارنة، مع الحفاظ على عمل المتدرب الصحيح الأحدث. |
| Public test fails after an edit | Revert only the most recent learner edit, rerun the same public test, and record the error. | فشل فحص عام بعد تعديل | تراجع عن أحدث تعديل للمتدرب فقط، ثم أعد الفحص نفسه وسجل الخطأ. |
| Browser tab closed | Reopen the saved Drive notebook; never rebuild from an untrusted copy. | إغلاق تبويب المتصفح | أعد فتح نسخة Drive المحفوظة، ولا تُعد البناء من نسخة غير موثوقة. |
| **Learner submission quality** is red after upload | Open the first failed Actions step, keep only the first useful sanitized error, repair the smallest relevant learner TODO in the Drive notebook, rerun its dependent gates through C29, export again, and upload a new commit. Do not edit workflows/tests to hide the failure. | فحص **Learner submission quality** أحمر بعد الرفع | افتح أول خطوة Actions فاشلة واحتفظ بأول خطأ مفيد ومنقح، ثم أصلح أصغر TODO مرتبط في دفتر Drive، وأعد البوابات التابعة حتى C29 والتصدير، وارفع Commit جديدًا. لا تعدّل Workflows أو الاختبارات لإخفاء الفشل. |

## Saved checkpoint labels · تسميات نقاط التقدم المحفوظة

Use these exact, searchable labels after each successful gate. Save the working evidence in Drive, then use the first two messages only to update the matching status in `LEARNING_PROGRESS.md`; use the final line for the clean C29 project upload:

استخدم التسميات الدقيقة والقابلة للبحث التالية بعد نجاح كل بوابة. احفظ أدلة العمل في Drive، ثم استخدم الرسالتين الأوليين لتحديث الحالة المقابلة فقط داخل `LEARNING_PROGRESS.md`، واستخدم السطر الأخير لرفع مشروع C29 النظيف:

```text
docs(day1): record C9 gate
docs(day2): record C20 gate
feat: submit Rafeeq Mini capstone
```

A saved checkpoint should preserve the updated Drive notebook, gate result, and report draft. Before C29, the only GitHub change is the safe public status inside `LEARNING_PROGRESS.md`; project files are uploaded only after the clean C29 export. Neither location may contain raw runtime dumps, real data, keys, passwords, private links, solution files, instructor materials, or hidden tests.

يجب أن تحفظ نقطة التقدم دفتر Drive المحدث ونتيجة البوابة ومسودة التقرير. وقبل C29 لا يتغير في GitHub إلا الحالة العامة الآمنة داخل `LEARNING_PROGRESS.md`، ولا ترفع ملفات المشروع إلا بعد تصدير C29 النظيف. ويُمنع في الموقعين تضمين تفريغ خام للبيئة أو بيانات حقيقية أو مفاتيح أو كلمات مرور أو روابط خاصة أو ملفات حلول أو مواد المدربة أو اختبارات خفية.

The generated files `reports/trace.jsonl`, `reports/assessment_results.json`, `reports/monitoring_dashboard.png`, and `reports/submission_manifest.json` are required clean C29 outputs and are not durable Colab state. If they disappear after a reset, restore through the last passed gate and rerun `C25_TRACE_EVAL` through `C29_EXPORT_SAFETY_CHECK`, then upload the extracted clean contents—not the ZIP—to GitHub.

الملفات المولدة `reports/trace.jsonl` و`reports/assessment_results.json` و`reports/monitoring_dashboard.png` و`reports/submission_manifest.json` مخرجات C29 نظيفة وإلزامية، وليست حالة دائمة في كولاب. إذا اختفت بعد إعادة ضبط البيئة فاستعد حتى آخر بوابة ناجحة، ثم أعد التشغيل من `C25_TRACE_EVAL` إلى `C29_EXPORT_SAFETY_CHECK`، وارفع المحتويات النظيفة المستخرجة إلى GitHub لا ملف ZIP.

## Help without data leakage · طلب المساعدة دون تسريب

Share only: cell ID, first useful error line, expected behavior, actual behavior, runtime type, and the last passed gate. Replace customer-like identifiers with supplied synthetic fixture IDs.

شارك فقط: رقم الخلية، وأول سطر خطأ مفيد، والسلوك المتوقع والفعلي، ونوع البيئة، وآخر بوابة ناجحة. استخدم معرفات الحالات المصطنعة المرفقة بدل أي معرف يشبه بيانات العملاء.

Use the public bilingual [Lab help issue form](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml) only for sanitized technical questions. Vulnerabilities, credentials, private links, personal data, grade disputes, and private submission details must use the instructor's private channel and [`SECURITY.md`](../SECURITY.md).

استخدم [نموذج مساعدة اللاب الثنائي](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml) للأسئلة التقنية العامة والمنقحة فقط. تُرسل الثغرات وبيانات الدخول والروابط الخاصة والبيانات الشخصية والاعتراضات على الدرجات وتفاصيل التسليم الخاصة عبر قناة المدربة الخاصة ووفق [`SECURITY.md`](../SECURITY.md).

This public folder contains policy only. Actual recovery patches, completed notebooks, instructor checkpoints, answers, scoring rules, and hidden evaluations belong outside the public learner repository.

يحتوي هذا المجلد العام على السياسة فقط. تبقى ملفات إصلاح الاستعادة والدفاتر المكتملة ونقاط المدربة والإجابات وقواعد الدرجات والتقييمات الخفية خارج مستودع المتدرب العام.
