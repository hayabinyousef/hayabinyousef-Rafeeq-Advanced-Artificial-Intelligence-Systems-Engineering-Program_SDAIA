# SDAIA administrative requirements · متطلبات سدايا الإدارية

This page converts the course administration instructions supplied for the
program into a clear, auditable learner checklist. The project remains the
complete course assessment (`100/100`); these requirements are included inside
that total and do not add bonus points.

تحوّل هذه الصفحة التعليمات الإدارية الواردة للبرنامج إلى قائمة واضحة وقابلة
للتدقيق للمتدرب. يظل المشروع هو تقييم الدورة كاملًا (`100/100`)؛ وتدخل هذه
المتطلبات ضمن المجموع نفسه وليست درجات إضافية.

## Assessed requirements · المتطلبات المقيمة — 10 points · درجات

| Requirement · المتطلب | Points · الدرجة | Acceptable evidence · الدليل المقبول |
|---|---:|---|
| Clear and comprehensive repository description · وصف واضح وشامل للمستودع | 2 | The GitHub **About** description concisely identifies the project, scenario, scope, and final outcome. This row does not rescore README quality. · يعرّف وصف About في GitHub بالمشروع والسيناريو والنطاق والمخرج النهائي بإيجاز، ولا يعيد هذا البند تقييم جودة README. |
| Professional README explaining idea, run, and use · README احترافي يشرح الفكرة والتشغيل والاستخدام | 2 | `README.md` gives the project idea, beginner run steps, how to test/use it, expected outputs, and limitations. · يشرح الملف الفكرة وخطوات التشغيل والاستخدام/الاختبار والمخرجات والقيود. |
| Appropriate technical documentation · توثيق فني مناسب | 2 | Architecture, notebook map, technical reports, security evidence, metrics, and limitations are organized and linked. · المعمارية وخريطة الدفتر والتقارير والأمن والمقاييس والقيود منظمة ومترابطة. |
| Git version-management practices · ممارسات Git وإدارة الإصدارات | 2 | Safe documentation checkpoints for setup/Day 1/Day 2 plus the final C29 delivery commit; messages are meaningful and history is preserved. · نقاط توثيق آمنة للتجهيز واليومين الأول والثاني ثم Commit التسليم النهائي، برسائل واضحة ودون حذف السجل. |
| Training-program reference · الإشارة إلى البرنامج التدريبي | 1 | The approved Arabic or English course title appears in `README.md`. · يظهر اسم الدورة العربي أو الإنجليزي المعتمد في README. |
| SDAIA Academy GitHub link · رابط أكاديمية سدايا على GitHub | 1 | A working link to [SDAIAAcademy](https://github.com/SDAIAAcademy) appears with neutral wording and no endorsement claim. · يظهر الرابط الصحيح بصياغة محايدة دون ادعاء اعتماد. |
| **Administrative subtotal · المجموع الإداري** | **10** | Human-reviewed against the pinned final commit. · يراجع بشريًا على Commit النهائي المثبت. |

## Technical delivery evidence · أدلة التسليم التقنية — 5 points · درجات

| Requirement · المتطلب | Points · الدرجة |
|---|---:|
| Clean Colab run and green official workflow on the assessed commit · تشغيل كولاب نظيف وفحص رسمي أخضر على Commit المقيم | 2 |
| Notebook, run ID, reports, manifest, export ID, and commit evidence are consistent · ترابط الدفتر ومعرف التشغيل والتقارير والبيان ومعرف التصدير ودليل Commit | 2 |
| Privacy and content hygiene · الخصوصية ونظافة المحتوى | 1 |
| **Technical-delivery subtotal · مجموع التسليم التقني** | **5** |

These two subtotals form the existing 15-point GitHub-delivery area in the
[100-point rubric](ASSESSMENT_RUBRIC.md). Automated checks confirm objective
facts; the instructor assigns points for clarity, quality, and meaningful Git
history.

يشكّل المجموعان معًا محور تسليم GitHub الحالي من 15 درجة داخل
[معيار الـ100 درجة](ASSESSMENT_RUBRIC.md). تتحقق الفحوص الآلية من الحقائق
الموضوعية، بينما تمنح المدربة درجات الوضوح والجودة ودلالة سجل Git.

## Safe progressive Git path · مسار Git المرحلي الآمن

Only the small public progress log is updated before C29. Keep code, the live
notebook, raw outputs, traces, temporary checkpoints, and ZIP files in Drive or
Colab until the guarded final export.

لا يُحدّث قبل C29 إلا سجل تقدم عام وصغير. أبقِ الكود والدفتر الجاري والمخرجات
الخام والتتبعات ونقاط الحفظ المؤقتة وملفات ZIP في Drive أو Colab حتى التصدير
النهائي المحمي.

| Stage · المرحلة | Browser-only action · الإجراء من المتصفح | Suggested commit · رسالة مقترحة |
|---|---|---|
| Setup · التجهيز | Create `LEARNING_PROGRESS.md` from the [safe template](LEARNING_PROGRESS_TEMPLATE.md). · أنشئ الملف من القالب الآمن. | `docs: initialize Rafeeq Mini progress log` |
| After C9 · بعد C9 | Mark Day 1 `PASS`; publish no code or raw evidence. · غيّر حالة اليوم الأول إلى PASS دون نشر كود أو أدلة خام. | `docs(day1): record C9 gate` |
| After C20 · بعد C20 | Mark Day 2 `PASS`; keep the Colab notebook in Drive. · غيّر حالة اليوم الثاني إلى PASS وأبقِ الدفتر في Drive. | `docs(day2): record C20 gate` |
| After C29 · بعد C29 | Upload the extracted clean package and completed notebook. · ارفع الحزمة النظيفة المفكوكة والدفتر المكتمل. | `feat: submit Rafeeq Mini capstone` |

## Course evaluation · تقييم الدورة

The SDAIA coordinator or supervisor shares the course-evaluation link at the
start of the final day. Participation is recorded through the designated
private channel, but it carries **no project points**. Responses, opinions, and
screenshots are never placed in the public repository or reviewed as project
evidence. If no link is supplied, no learner action is required.

يشارك منسق أو مشرف سدايا رابط تقييم الدورة في بداية اليوم الأخير. يسجل
الإتمام عبر القناة الخاصة المحددة، لكنه **لا يحمل درجات للمشروع**. لا تنشر
الإجابات أو الآراء أو لقطات الشاشة في المستودع العام، ولا تراجع بوصفها دليلًا
للمشروع. وإذا لم يرسل الرابط فلا يطلب من المتدرب أي إجراء.

## Encouraged, not graded · ممارسات تشجيعية غير مقيمة

- Give a Star to genuinely useful, high-quality Saudi projects. · أضف Star للمشروعات السعودية المفيدة وعالية الجودة.
- Follow relevant Saudi technical accounts or repositories by choice. · تابع الحسابات أو المستودعات التقنية السعودية باختيارك.
- Contribute to open-source work when a real contribution exists. · ساهم في المصادر المفتوحة عند وجود مساهمة فعلية.
- Use Fork, Pull Requests, and Issues for other projects when appropriate; the assessed Rafeeq repository itself must be a new repository, not a fork. · استخدم Fork وPull Requests وIssues في المشروعات الأخرى عند الحاجة؛ أما مستودع رفيق المقيم فيجب أن يكون مستودعًا جديدًا لا Fork.
- Share a strong, sanitized project with the technical community. · شارك المشروع المتميز والمنقح مع المجتمع التقني.

These activities receive no points and never compensate for a failed required
criterion or safety gate.

لا تمنح هذه الأنشطة درجات، ولا تعوض فشل متطلب إلزامي أو بوابة سلامة.
