# Required evidence cards · بطاقات الأدلة الإلزامية

Copy this file to `reports/EVIDENCE_CARD.md` after extracting the clean C29 package, then complete **one concise card for each day**. This is a required instructor-assessment record. It is added after C29, so it is not an automated notebook output and is not hashed by `reports/submission_manifest.json`.

انسخ هذا الملف إلى `reports/EVIDENCE_CARD.md` بعد فك حزمة C29 النظيفة، ثم أكمل **بطاقة مختصرة لكل يوم**. هذا سجل إلزامي لتقييم المدربة. يضاف بعد C29، ولذلك ليس مخرجًا آليًا من الدفتر ولا يتضمنه التجزئة داخل `reports/submission_manifest.json`.

Use actual observable results only. Do not paste code solutions, raw traces, screenshots of browser accounts, real data, private reasoning, or unmeasured claims.

استخدم النتائج الفعلية القابلة للملاحظة فقط. لا تلصق حلول الكود أو سجلات خامًا أو صور حسابات المتصفح أو بيانات حقيقية أو تفكيرًا خاصًا أو ادعاءات غير مقاسة.

## Submission identity · هوية التسليم

| Field | Entry · الإدخال |
|---|---|
| Public learner ID · معرف المتدرب العام | `[learner_id or GitHub username — no real name]` |
| Assessment `run_id` · معرف تشغيل التقييم | `[from reports/assessment_results.json]` |
| Final clean run date (UTC) · تاريخ التشغيل النظيف | `[YYYY-MM-DD]` |

## EV-D1 · Day 1 core and tools · نواة اليوم الأول وأدواته

| Field | Entry · الإدخال |
|---|---|
| Testable claim · الادعاء القابل للاختبار | `[one sentence]` |
| Cell/gate · الخلية/البوابة | `C[TODO] / C9_DAY1_GATE` |
| Public case or metric · الحالة العامة أو المقياس | `[case ID or metric]` |
| Expected result · النتيجة المتوقعة | `[TODO]` |
| Actual result · النتيجة الفعلية | `[TODO]` |
| Status · الحالة | `PASS / FAIL` |
| Public artifact path · مسار الدليل العام | `[TODO]` |
| Reproduce · إعادة التنفيذ | `[short, numbered steps]` |

Safe observation · الملاحظة الآمنة: `[decision, tool/route, result, and counters only]`

## EV-D2 · Day 2 memory and orchestration · ذاكرة اليوم الثاني وتنسيقه

| Field | Entry · الإدخال |
|---|---|
| Testable claim · الادعاء القابل للاختبار | `[one sentence]` |
| Cell/gate · الخلية/البوابة | `C[TODO] / C20_DAY2_GATE` |
| Public case or metric · الحالة العامة أو المقياس | `[case ID or metric]` |
| Expected result · النتيجة المتوقعة | `[TODO]` |
| Actual result · النتيجة الفعلية | `[TODO]` |
| Status · الحالة | `PASS / FAIL` |
| Public artifact path · مسار الدليل العام | `[TODO]` |
| Reproduce · إعادة التنفيذ | `[short, numbered steps]` |

Safe observation · الملاحظة الآمنة: `[decision, scoped route/retrieval, result, and counters only]`

## EV-D3 · Day 3 security and evidence · أمن اليوم الثالث وأدلته

| Field | Entry · الإدخال |
|---|---|
| Testable claim · الادعاء القابل للاختبار | `[one sentence]` |
| Cell/gate · الخلية/البوابة | `C[TODO] / C29_EXPORT_SAFETY_CHECK` |
| Public case or metric · الحالة العامة أو المقياس | `[attack case, readiness check, or metric]` |
| Expected result · النتيجة المتوقعة | `[TODO]` |
| Actual result · النتيجة الفعلية | `[TODO]` |
| Status · الحالة | `PASS / FAIL` |
| Public artifact path · مسار الدليل العام | `[TODO]` |
| Reproduce · إعادة التنفيذ | `[short, numbered steps]` |

Safe observation · الملاحظة الآمنة: `[control, attack/result, residual risk, and measured counter only]`

## Required redaction declaration · إقرار التنقيح الإلزامي

- [ ] I used only the instructor-assigned `learner_id` or GitHub username. · استخدمت `learner_id` الذي تقدمه المدربة أو اسم مستخدم GitHub فقط.
- [ ] All identifiers are supplied synthetic fixtures. · جميع المعرفات من الحالات المصطنعة المرفقة.
- [ ] No password, token, API key, cookie, private link, or environment value appears. · لا توجد كلمة مرور أو رمز وصول أو مفتاح API أو Cookie أو رابط خاص أو قيمة بيئة.
- [ ] No real person, customer, employee, order, payment, support, or trainee data appears. · لا توجد بيانات حقيقية لشخص أو عميل أو موظف أو طلب أو دفعة أو دعم أو متدرب.
- [ ] No copied solution, instructor note, answer key, scoring rule, hidden test, or private chain-of-thought appears. · لا يوجد حل منسوخ أو ملاحظة مدربة أو مفتاح إجابة أو قاعدة درجات أو اختبار خفي أو تفكير داخلي خاص.
- [ ] Every declared `PASS` matches an actual final-run result. · كل نتيجة `PASS` معلنة تطابق نتيجة فعلية من التشغيل النهائي.
