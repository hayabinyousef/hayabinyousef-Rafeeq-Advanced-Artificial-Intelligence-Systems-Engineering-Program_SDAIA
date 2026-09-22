# Rafeeq Mini assessment rubric · معيار تقييم رفيق المصغّر

This public rubric explains how the three-day mini-capstone is assessed. It
contains no answer key, hidden input, or private instructor case.

يوضح هذا المعيار العام كيفية تقييم المشروع المصغّر خلال الأيام الثلاثة، ولا
يتضمن مفتاح إجابة أو مدخلًا خفيًا أو حالة تقييم خاصة بالمدربة.

## Pass decision · قرار الاجتياز

A learner passes only when both conditions are true:

لا يجتاز المتدرب إلا بتحقق الشرطين معًا:

1. Raw score is at least `70/100`. · الدرجة الخام `70/100` أو أكثر.
2. Every non-compensable gate `G1–G7` passes. · نجاح جميع البوابات غير القابلة للتعويض `G1–G7`.

A score of 70 or more cannot compensate for a failed safety, integrity, or
delivery gate. The result remains `HOLD` until the gate is repaired and the
submission is revalidated under the instructor's resubmission policy.

لا تعوض درجة 70 أو أكثر فشل بوابة سلامة أو نزاهة أو تسليم. تبقى الحالة
`HOLD` حتى تصحيح البوابة وإعادة التحقق وفق سياسة إعادة التسليم التي تحددها
المدربة.

## Non-compensable gates · البوابات غير القابلة للتعويض

| Gate | Required evidence | البوابة | الدليل المطلوب |
|---|---|---|---|
| `G1` | `C9_DAY1_GATE` passes | نجاح بوابة اليوم الأول | `all_passed=true` |
| `G2` | `C20_DAY2_GATE` passes | نجاح بوابة اليوم الثاني | `all_passed=true` |
| `G3` | Enabled C29 creates the export | إنشاء التصدير النهائي | `FINAL_EXPORT_CREATED` and valid manifest |
| `G4` | Final GitHub delivery is complete | اكتمال تسليم GitHub | Green `Learner submission quality` **and instructor confirmation that the repository description, README, documentation, program reference, SDAIA Academy link, and Git evidence are all present** |
| `G5` | Synthetic and sanitized public content only | نظافة المحتوى | Automated credential/path scan **plus instructor review**: no public PII, real data, or instructor-only material |
| `G6` | Customer scope remains isolated | عزل العملاء | Zero cross-customer disclosure |
| `G7` | Sensitive writes stay governed | حوكمة الكتابة | No unauthorized or repeated refund write |

`G5` is a hybrid gate. The official workflow detects prohibited paths, credential
patterns, and contract violations; the instructor also reviews the public reports
and evidence card because automation cannot reliably determine whether a person's
name or contextual detail is identifying. A green workflow alone does not clear
`G5`. Use only the assigned `learner_id` or GitHub username in public files.

البوابة `G5` بوابة مشتركة: يكشف سير العمل الرسمي المسارات المحظورة وأنماط
بيانات الدخول ومخالفات العقود، وتراجع المدربة كذلك التقارير العامة وبطاقة
الأدلة لأن الأتمتة لا تستطيع الجزم بأن الاسم أو السياق يعرّف بشخص. نجاح سير
العمل وحده لا يجتاز `G5`. استخدم في الملفات العامة `learner_id` المخصص أو اسم
مستخدم GitHub فقط.

`G4` is also hybrid. The green workflow proves the machine-verifiable delivery
contract; the instructor separately confirms the repository description,
README, technical documentation, meaningful Git history, training-program
reference, and SDAIA Academy link on the assessed commit. Presence of every
required evidence category is the gate; quality within those categories earns
the weighted points below, so the same weakness is not deducted twice.

البوابة `G4` مشتركة كذلك. يثبت Workflow الأخضر عقد التسليم القابل للفحص
الآلي، وتتحقق المدربة بصورة مستقلة من وصف المستودع وREADME والتوثيق الفني
ودلالة سجل Git وذكر البرنامج ورابط أكاديمية سدايا على Commit المقيم. وجود كل
فئة دليل إلزامي هو شرط البوابة، أما جودة تلك الأدلة فتمنح وفق الأوزان أدناه،
وبذلك لا يخصم القصور نفسه مرتين.

Suspected test tampering, copied work, or authorship conflict is reviewed by a
human under the training entity's policy; it is not decided by an AI detector.

يحال الاشتباه في التحايل على الاختبارات أو نسخ العمل أو تعارض نسبة العمل إلى
مراجعة بشرية وفق سياسة الجهة، ولا يُحسم بواسطة كاشف محتوى آلي.

The course-evaluation link is shared by the SDAIA coordinator or supervisor at
the start of the final day. Completion is handled through the designated
private channel and receives no project points; response content and screenshots
must not be published in GitHub.

يشارك منسق أو مشرف سدايا رابط تقييم الدورة في بداية اليوم الأخير. يعالج
الإتمام عبر القناة الخاصة المحددة ولا يمنح درجات للمشروع، ولا تنشر الإجابات
أو لقطات الشاشة في GitHub.

## Score distribution · توزيع الدرجات

| Assessment area | Points | محور التقييم | الدرجة |
|---|---:|---|---:|
| Day 1: architecture, typed state, bounded flow, ReAct, tools, and MCP | 20 | اليوم الأول: المعمارية والحالة والتدفق وReAct والأدوات وMCP | 20 |
| Day 2: memory, scoped retrieval, orchestration, planning, and approval | 20 | اليوم الثاني: الذاكرة والاسترجاع والتنسيق والتخطيط والموافقة | 20 |
| Day 3: threat model, guard repair, reflection, tracing, and optimization | 25 | اليوم الثالث: التهديدات وإصلاح الحواجز والمراجعة والتتبع والتحسين | 25 |
| SDAIA administrative compliance, evidence, privacy, and GitHub delivery | 15 | الامتثال الإداري لسدايا والأدلة والخصوصية وتسليم GitHub | 15 |
| Engineering decisions and production limitations | 10 | القرارات الهندسية وحدود الانتقال إلى الإنتاج | 10 |
| Demonstration and individual defense | 10 | العرض والمناقشة الفردية | 10 |
| **Total** | **100** | **المجموع** | **100** |

## Analytic criteria · المعايير التحليلية

### Day 1 · اليوم الأول — 20

| Criterion | Points | Evidence examples · أمثلة الأدلة |
|---|---:|---|
| Trust boundaries and architecture decision · حدود الثقة والقرار المعماري | 4 | `C1`, `TODO-1` |
| Minimal typed state and safe snapshot · الحالة الدنيا واللقطة الآمنة | 4 | `C2`, `TODO-2` |
| Terminal and `6/12/2/1` budgets · الحالة النهائية وحدود التنفيذ | 4 | `C3`, `TODO-3` |
| Four-stage operational ReAct cycle · دورة ReAct تشغيلية من أربع مراحل | 3 | `C4–C5`, `TODO-4` |
| Narrow tool schema and real local MCP boundary · عقد أداة ضيق وحد MCP محلي فعلي | 5 | `C6–C9`, `TODO-5` |

### Day 2 · اليوم الثاني — 20

| Criterion | Points | Evidence examples · أمثلة الأدلة |
|---|---:|---|
| Safe session memory summary · ملخص ذاكرة جلسة آمن | 3 | `C11`, `TODO-6` |
| Owner/activity/expiry filter before ranking · التصفية قبل الترتيب | 5 | `C12`, `TODO-7` |
| Active policy retrieval · استرجاع السياسة السارية | 3 | `C13`, `TODO-8` |
| Specialists, supervisor, and typed handoff · التخصص والمنسق والتفويض | 4 | `C14–C16`, `TODO-9` |
| Plan, refund boundary, human approval, and safe resume · الخطة وحد الاسترداد والموافقة والاستئناف | 5 | `C17–C20`, `TODO-10` |

### Day 3 · اليوم الثالث — 25

| Criterion | Points | Evidence examples · أمثلة الأدلة |
|---|---:|---|
| Testable threat and new synthetic case · تهديد قابل للاختبار وحالة اصطناعية جديدة | 4 | `C21`, `TODO-11` |
| Guard repair with no safe-input regression · إصلاح الحاجز بلا تراجع للمدخل السليم | 6 | `C22–C23`, `TODO-12` |
| Reflection remains bounded and cannot expand authority · مراجعة محدودة لا توسع الصلاحية | 3 | `C24` |
| Redacted trace and canonical assessment · تتبع منقح وتقييم موحد | 4 | `C25`, `C27` |
| Measured optimization with a safety guardrail · تحسين مقاس مع ضابط أمان | 4 | `C26`, `TODO-13` |
| Honest scorecard, readiness, and safe export · بطاقة نتائج وجاهزية وتصدير صادقة | 4 | `C27–C29`, `TODO-14` |

### SDAIA administration, evidence, and GitHub · متطلبات سدايا والأدلة وGitHub — 15

| Criterion | Points |
|---|---:|
| Clear and comprehensive GitHub repository description · وصف واضح وشامل للمستودع | 2 |
| Professional README explains the idea, run, and use · README احترافي يشرح الفكرة والتشغيل والاستخدام | 2 |
| Appropriate, linked technical documentation · توثيق فني مناسب ومترابط | 2 |
| Meaningful, safe Git progress and preserved version history · تقدم Git آمن وذو معنى مع حفظ سجل الإصدارات | 2 |
| Training-program reference in `README.md` · الإشارة إلى البرنامج التدريبي في README | 1 |
| Working [SDAIA Academy GitHub](https://github.com/SDAIAAcademy) link with neutral attribution · رابط أكاديمية سدايا الصحيح بصياغة محايدة | 1 |
| Clean Colab run and green official workflow on the assessed commit · تشغيل كولاب نظيف وفحص رسمي أخضر على Commit المقيم | 2 |
| Notebook, run ID, reports, manifest, export ID, and commit evidence are consistent · ترابط الأدلة | 2 |
| Privacy and content hygiene · الخصوصية ونظافة المحتوى | 1 |

The detailed evidence standard, safe progressive Git path, and the distinction
between required and encouraged activities are defined in
[`SDAIA_ADMIN_REQUIREMENTS.md`](SDAIA_ADMIN_REQUIREMENTS.md). Quality and
meaning are reviewed by the instructor; automated checks confirm only
objective, machine-verifiable facts.

يوضح ملف [`SDAIA_ADMIN_REQUIREMENTS.md`](SDAIA_ADMIN_REQUIREMENTS.md) معيار
الدليل التفصيلي ومسار Git المرحلي الآمن والفرق بين المتطلبات الإلزامية
والأنشطة التشجيعية. تراجع المدربة الجودة ودلالة السجل بشريًا، وتتحقق الأدوات
فقط من الحقائق الموضوعية القابلة للفحص الآلي.

### Engineering decisions · القرارات الهندسية — 10

| Criterion | Points |
|---|---:|
| Explain authority and trust boundaries · تفسير حدود الصلاحية والثقة | 3 |
| Explain ReAct, Plan-and-Execute, and bounded Reflection choices · تفسير اختيار الأنماط | 3 |
| Distinguish the lab simulation from production · التمييز بين المحاكاة والإنتاج | 2 |
| Connect one decision to Cell, Case, Metric, and Result · ربط قرار بدليل تشغيل | 2 |

### Demonstration and individual defense · العرض والمناقشة — 10

| Criterion | Points |
|---|---:|
| Bilingual functional scenario · سيناريو وظيفي ثنائي اللغة | 2 |
| Refund above SAR 500 pauses for approval and resumes safely · توقف ما فوق 500 للموافقة واستئنافه بأمان | 2 |
| New attack is blocked and monitoring evidence is shown · حجب هجوم جديد وعرض دليل المراقبة | 2 |
| Clear, time-bounded presentation and role ownership · وضوح العرض والالتزام بالوقت والدور | 1 |
| Individual answer explains the implementation and evidence · إجابة فردية تثبت الفهم | 3 |

## Performance bands · مستويات الأداء

| Band | Operational meaning · المعنى التشغيلي |
|---|---|
| 90–100% of criterion | Correct, reproducible, linked evidence, and a clear trade-off explanation · صحيح وقابل للتكرار ودليله مترابط ومقايضته واضحة |
| 80–89% | Core behavior is stable with a minor non-critical evidence or explanation gap · السلوك الأساسي ثابت مع نقص طفيف غير حرج |
| 70–79% | Core path works, but evidence, limits, or explanation needs improvement · المسار يعمل لكن الأدلة أو الحدود أو التفسير تحتاج تحسينًا |
| 0–69% | Incorrect, unsafe, non-reproducible, or unsupported behavior · سلوك خاطئ أو غير آمن أو غير قابل للتكرار أو بلا دليل |

Scores are rounded to the nearest half point. A critical safety failure receives
no partial credit and activates the related non-compensable gate.

تقرب الدرجات إلى أقرب نصف درجة. ولا يمنح الخلل الأمني الحرج درجة جزئية، بل
يفعل البوابة غير القابلة للتعويض المرتبطة به.
