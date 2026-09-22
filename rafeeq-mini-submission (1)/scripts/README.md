# Utility scripts · السكربتات المساعدة

| English | العربية |
|---|---|
| Scripts in this folder support validation and repeatable checks. They are not alternative solutions to the notebook. | تدعم السكربتات في هذا المجلد التحقق والفحوص القابلة للتكرار، وليست حلولًا بديلة للدفتر. |
| A beginner is not expected to use a local terminal. The cumulative notebook calls the learner-required checks from Colab. | لا يُتوقع من المبتدئ استخدام Terminal محلي؛ يستدعي الدفتر التراكمي الفحوص المطلوبة من داخل كولاب. |

## Learner starting boundary · حدود بداية المتدرب

Create a public learner repository during preflight and add only the safe `LEARNING_PROGRESS.md` file. Start from the **[official course notebook in Colab](https://colab.research.google.com/github/almiyead-rgb/rafeeq-agentic-ai-labs/blob/v0.9.0-rc3/notebooks/Rafeeq_Mini_Capstone.ipynb)** and select **File → Save a copy in Drive**. The notebook carries the public lab files and calls these scripts; do not upload or run project code from the learner repository before C29.

أنشئ مستودع المتدرب العام أثناء التجهيز وأضف ملف `LEARNING_PROGRESS.md` الآمن فقط. ابدأ من **[دفتر الدورة الرسمي في كولاب](https://colab.research.google.com/github/almiyead-rgb/rafeeq-agentic-ai-labs/blob/v0.9.0-rc3/notebooks/Rafeeq_Mini_Capstone.ipynb)**، ثم اختر **File → Save a copy in Drive**. يحمل الدفتر ملفات اللاب العامة ويستدعي هذه السكربتات؛ لا ترفع كود المشروع أو تشغله من مستودع المتدرب قبل C29.

At C29, use the public repository containing only the safe progress log. Upload the **extracted clean contents** of `rafeeq-mini-submission.zip`, retain `LEARNING_PROGRESS.md`, then add the completed notebook downloaded manually through **File → Download → Download .ipynb** as `notebooks/Rafeeq_Mini_Capstone.ipynb`. Do not upload the ZIP itself.

عند C29 استخدم المستودع العام الذي لا يحتوي إلا سجل التقدم الآمن، وارفع **المحتويات النظيفة المستخرجة** من `rafeeq-mini-submission.zip` مع الاحتفاظ بـ`LEARNING_PROGRESS.md`، ثم أضف الدفتر المكتمل المنزّل يدويًا عبر **File → Download → Download .ipynb** بالمسار `notebooks/Rafeeq_Mini_Capstone.ipynb`. لا ترفع ملف ZIP نفسه.

## Public verification tools · أدوات التحقق العامة

| Script | Purpose · الغرض |
|---|---|
| `doctor.py` | Verify Python, safe defaults, supplied synthetic data, core smoke behavior, and the local MCP `stdio` boundary. · التحقق من Python والإعدادات الآمنة والبيانات المصطنعة والسلوك الأساسي وحدود MCP المحلية. |
| `validate_notebook.py` | Check the exact `C0–C29` structure, the 14 learner `TODO` markers, cleared outputs, and the guarded final-export markers. It is not a grade or solution checker. · فحص بنية `C0–C29` الدقيقة و14 علامة `TODO` ومسح المخرجات وعلامات التصدير المحمي، وليس فاحص درجات أو حلول. |
| `run_assessment.py` | Run public synthetic cases and generate sanitized assessment and monitoring artifacts. · تشغيل الحالات المصطنعة العامة وتوليد مخرجات التقييم والمراقبة المنقحة. |
| `validate_release.py` | Verify the final public file set, schemas, safety boundaries, and clean export readiness. · التحقق من ملفات الإصدار العامة والمخططات وحدود السلامة وجاهزية التصدير النظيف. |

## Source and submission workflows · مسارا المصدر والتسليم

| Workflow | Where it belongs | Purpose · الغرض |
|---|---|---|
| `.github/workflows/learner-quality.yml` and `.github/workflows/pages.yml` | Official course source repository only; C29 excludes both from the learner export. · مستودع مصدر الدورة الرسمي فقط، ويستبعدهما C29 من تصدير المتدرب. | Maintainer release and course-site deployment checks. They are not learner submission checks, so beginners are not asked to configure Pages. · فحوص إصدار الحزمة ونشر موقع الدورة للمشرف، وليست فحوص تسليم، لذا لا يُطلب من المبتدئ إعداد Pages. |
| `.github/workflows/learner-submission-quality.yml` | Created by C29 inside the clean export and uploaded to the learner repository. · ينشئه C29 داخل التصدير النظيف، ثم يُرفع إلى مستودع المتدرب. | Runs public tests and `scripts/validate_submission.py` on the submitted project. · يشغّل الفحوص العامة و`scripts/validate_submission.py` على المشروع المسلّم. |

These names are intentionally different. Do not copy, rename, or replace either workflow manually.

الاسمان مختلفان عمدًا. لا تنسخ أي مسار أو تعيد تسميته أو تستبدله يدويًا.

When a local Python environment is available, a maintainer may run:

عند توفر بيئة Python محلية يمكن للمشرف تشغيل:

```bash
python scripts/doctor.py
python -m unittest discover -s tests/public -p 'test_*.py' -v
python scripts/validate_notebook.py
python scripts/run_assessment.py
python scripts/validate_release.py
```

Learners should rely on the named notebook gates `C0`, `C9`, `C20`, and `C29`; do not download or run an unknown script merely because it promises to fix a failed test.

على المتدرب الاعتماد على بوابات الدفتر المسماة `C0` و`C9` و`C20` و`C29`؛ لا تحمّل سكربتًا مجهولًا أو تشغله لمجرد أنه يعد بإصلاح فحص فاشل.

## Safety contract · عقد الأمان

- Scripts must default to offline, deterministic behavior. · يجب أن تعمل السكربتات افتراضيًا دون اتصال وبسلوك حتمي.
- They must not request, read, print, or transmit credentials. · يجب ألا تطلب بيانات دخول أو تقرأها أو تطبعها أو ترسلها.
- They must use only supplied synthetic educational data. · يجب أن تستخدم البيانات التعليمية المصطنعة المرفقة فقط.
- They must not contain an answer key, a completed learner solution, or hidden evaluation logic. · يجب ألا تحتوي على مفتاح إجابة أو حل متدرب مكتمل أو منطق تقييم خفي.
- Validation failure must produce a clear message and a non-zero exit status; it must not silently alter learner work. · يجب أن ينتج فشل التحقق رسالة واضحة ورمز خروج غير صفري، وألا يغيّر عمل المتدرب بصمت.
