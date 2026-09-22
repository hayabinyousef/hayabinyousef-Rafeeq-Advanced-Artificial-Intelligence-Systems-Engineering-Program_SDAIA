# Rafeeq Mini project report · تقرير مشروع رفيق المصغّر

> Reference/enrichment template. `C28_READINESS` generates the required `reports/PROJECT_REPORT.md` automatically. Use this template only if additional analysis is requested, and edit after the final C28 run.
>
> قالب مرجعي للإثراء. تولد `C28_READINESS` ملف `reports/PROJECT_REPORT.md` الإلزامي تلقائيًا. استخدم هذا القالب فقط عند طلب تحليل إضافي، وعدّل بعد آخر تشغيل لـC28.

Use only the instructor-assigned `learner_id` or GitHub username in this public report. Put real identity only in the private hand-in form provided by the instructor.

استخدم `learner_id` الذي تقدمه المدربة أو اسم مستخدم GitHub فقط في هذا التقرير العام. ضع الهوية الحقيقية في نموذج التسليم الخاص الذي تقدمه المدربة فقط.

## 1. Submission identity · بيانات التسليم

| Field | Entry · الإدخال |
|---|---|
| Public learner ID · معرف المتدرب العام | `[learner_id or GitHub username]` |
| GitHub username · اسم مستخدم GitHub | `[TODO]` |
| Public repository URL · رابط المستودع العام | `[TODO]` |
| Training program · البرنامج التدريبي | `Advanced Agentic AI Systems Engineering · هندسة أنظمة الذكاء الاصطناعي التوكيلي المتقدمة` |
| SDAIA Academy GitHub · حساب أكاديمية سدايا | `https://github.com/SDAIAAcademy` |
| Progress log · سجل التقدم | `LEARNING_PROGRESS.md` |
| Assessment run ID from `assessment_results.json` · معرف تشغيل التقييم من `assessment_results.json` | `[TODO if available]` |
| Expected upload commit message · رسالة Commit المتوقعة | `feat: submit Rafeeq Mini capstone` |
| Notebook · الدفتر | `notebooks/Rafeeq_Mini_Capstone.ipynb` |
| Runtime · البيئة | `Google Colab Free · CPU · LLM_MODE=stub` |
| Final run date (UTC) · تاريخ آخر تشغيل | `[TODO]` |

## 2. Scenario and objective · السيناريو والهدف

**English — 80 words maximum:** `[TODO: explain how Rafeeq handles a fictional Arabic or English order/refund request safely.]`

**العربية — 80 كلمة كحد أقصى:** `[TODO: اشرح كيف يتعامل رفيق بأمان مع طلب مصطنع بالعربية أو الإنجليزية يخص طلب شراء أو استرداد.]`

## 3. Architecture · المعمارية

Describe the implemented flow in one short sequence. Do not expose private reasoning.

صف التدفق المنفذ في تسلسل قصير، دون كشف التفكير الداخلي الخاص.

```text
Request → [TODO] → [TODO] → [TODO] → Response / Human approval
```

| Component · المكون | Responsibility · المسؤولية | Input/output contract · عقد الإدخال والإخراج | Evidence |
|---|---|---|---|
| Typed state · الحالة المحددة | `[TODO]` | `[TODO]` | `C[TODO]` |
| Local tools · الأدوات المحلية | `[TODO]` | `[TODO]` | `C[TODO]` |
| Bounded ReAct · ReAct المحدود | `[TODO]` | `[TODO]` | `C[TODO]` |
| MCP connection · اتصال MCP | `[TODO]` | `[TODO]` | `C[TODO]` |
| Memory and retrieval · الذاكرة والاسترجاع | `[TODO]` | `[TODO]` | `C[TODO]` |
| Supervisor and specialists · المنسق والوكلاء المتخصصون | `[TODO]` | `[TODO]` | `C[TODO]` |
| Approval and guardrails · الموافقة والحواجز | `[TODO]` | `[TODO]` | `C[TODO]` |
| Evaluation and monitoring · التقييم والمراقبة | `[TODO]` | `[TODO]` | `C[TODO]` |

## 4. Three-day build record · سجل البناء خلال ثلاثة أيام

| Day/gate | What I implemented · ما نفذته | Public checks · الفحوص العامة | Checkpoint label / assessment evidence · تسيمة النقطة / دليل التقييم | Result |
|---|---|---|---|---|
| Day 1 · `C9` | `[TODO]` | `[TODO]` | `docs(day1): record C9 gate / [TODO]` | `PASS / FAIL` |
| Day 2 · `C20` | `[TODO]` | `[TODO]` | `docs(day2): record C20 gate / [TODO]` | `PASS / FAIL` |
| Day 3 readiness · `C28` | `[TODO]` | `[TODO]` | `assessment run_id: [TODO if available]` | `PASS / FAIL` |

## 5. Functional scenarios · السيناريوهات الوظيفية

| Case ID | Language | Request type | Expected route | Approval expected? | Actual route/result | Pass? | Evidence |
|---|---|---|---|---|---|---|---|
| `[TODO]` | `AR` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `PASS / FAIL` | `[TODO]` |
| `[TODO]` | `EN` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `PASS / FAIL` | `[TODO]` |
| `[TODO]` | `[TODO]` | Refund above SAR 500 · استرداد فوق 500 ريال | Human approval · موافقة بشرية | `YES` | `[TODO]` | `PASS / FAIL` | `[TODO]` |

## 6. Evaluation and monitoring · التقييم والمراقبة

Report only values produced by your final clean run. If a metric is not implemented, write `Not measured`; do not invent a value.

سجل القيم الناتجة من تشغيلك النهائي النظيف فقط. إذا لم يُنفذ مقياس فاكتب `Not measured` ولا تخترع قيمة.

| Metric · المقياس | Value · القيمة | Method or denominator · طريقة الحساب | Evidence |
|---|---|---|---|
| Public cases passed · الحالات العامة الناجحة | `[TODO] / [TODO]` | `[TODO]` | `C27 / [TODO]` |
| Route accuracy · دقة التوجيه | `[TODO]` | `[TODO]` | `[TODO]` |
| Safety refusal rate · معدل الرفض الآمن | `[TODO]` | `[TODO]` | `[TODO]` |
| Median latency · وسيط زمن الاستجابة | `[TODO] ms` | `[TODO]` | `[TODO]` |
| Maximum agent steps · أقصى خطوات الوكيل | `[TODO]` | `[TODO]` | `[TODO]` |
| Estimated cost in stub mode · التكلفة التقديرية في Stub | `[TODO]` | `[TODO]` | `[TODO]` |

## 7. Engineering decisions · القرارات الهندسية

| Decision · القرار | Why it was chosen · سبب الاختيار | Trade-off · المقايضة | Evidence |
|---|---|---|---|
| Step limit · حد الخطوات | `[TODO]` | `[TODO]` | `[TODO]` |
| Memory scope · نطاق الذاكرة | `[TODO]` | `[TODO]` | `[TODO]` |
| Approval threshold · حد الموافقة | `[TODO]` | `[TODO]` | `[TODO]` |
| Reflection limit · حد المراجعة الذاتية | `[TODO]` | `[TODO]` | `[TODO]` |

## 8. Limitations and next safe improvement · القيود والتحسين الآمن التالي

- Current limitation · القيد الحالي: `[TODO]`
- Operational impact · الأثر التشغيلي: `[TODO]`
- Next safe improvement · التحسين الآمن التالي: `[TODO]`
- What must be retested · ما يجب إعادة اختباره: `[TODO]`

## 9. Required evidence links · روابط الأدلة المطلوبة

- Final notebook · الدفتر النهائي: `[TODO URL]`
- Project report · تقرير المشروع: `[TODO URL]`
- Security assessment · التقييم الأمني: `[TODO URL]`
- Assessment run ID from `reports/assessment_results.json` · معرف تشغيل التقييم من `reports/assessment_results.json`: `[TODO if available]`

The clean C29 export must contain the four artifacts below. After export, you may use the manifest timestamp and reported SHA-256 values as post-export verification; they are not required fields inside the earlier C23/C28 generated reports. Upload these sanitized files with the extracted repository contents, but do not upload `rafeeq-mini-submission.zip` itself.

يجب أن يتضمن تصدير C29 النظيف الملفات الأربعة أدناه. بعد التصدير يمكنك استخدام وقت الإنشاء وقيم SHA-256 المسجلة في البيان للتحقق اللاحق؛ وليست حقولًا إلزامية داخل تقريري C23/C28 المولدين سابقًا. ارفع هذه الملفات المنقحة مع محتويات المستودع المستخرجة، ولا ترفع `rafeeq-mini-submission.zip` نفسه.

| Generated artifact · الملف المولد | Produced by · تنتجه | Verification · التحقق |
|---|---|---|
| `reports/trace.jsonl` | `C25_TRACE_EVAL` | `SHA-256: [TODO]` |
| `reports/assessment_results.json` | `C27_SCORECARD` | `SHA-256: [TODO]` |
| `reports/monitoring_dashboard.png` | `C27_SCORECARD` | `SHA-256: [TODO]` |
| `reports/submission_manifest.json` | `C29_EXPORT_SAFETY_CHECK` | `schema valid: [TODO] · all_passed: [TODO]` |

## 10. Learner declaration · إقرار المتدرب

- [ ] The repository is my own new public repository created through the GitHub website, not a fork. · المستودع مستودعي العام الجديد المنشأ عبر موقع GitHub، وليس Fork.
- [ ] The repository has a clear About description, the required course reference and SDAIA Academy link, and a meaningful `LEARNING_PROGRESS.md` history. · يتضمن المستودع وصف About واضحًا وذكر الدورة ورابط أكاديمية سدايا المطلوبين وسجل `LEARNING_PROGRESS.md` ذا معنى.
- [ ] The repository contains extracted project files, not only a ZIP. · يحتوي المستودع على ملفات المشروع المستخرجة، وليس ملف ZIP فقط.
- [ ] I downloaded the completed Colab notebook separately and placed it at `notebooks/Rafeeq_Mini_Capstone.ipynb`; `reports/checkpoints/` is not published. · نزّلت دفتر كولاب المكتمل منفصلًا ووضعته في `notebooks/Rafeeq_Mini_Capstone.ipynb`، ولم أنشر `reports/checkpoints/`.
- [ ] All recorded values come from my own clean Colab CPU run. · جميع القيم المسجلة ناتجة من تشغيلي النظيف على Colab CPU.
- [ ] Both reports and all four generated submission artifacts are complete and consistent. · التقريرَان وجميع ملفات التسليم الأربعة المولدة مكتملة ومتسقة.
- [ ] I used synthetic data and included no credentials, private links, copied solutions, instructor material, or hidden tests. · استخدمت بيانات مصطنعة ولم أضمّن بيانات دخول أو روابط خاصة أو حلولًا منسوخة أو مواد للمدربة أو اختبارات خفية.

Learner confirmation · إقرار المتدرب: `[TODO: learner_id and date · معرّف المتدرب والتاريخ]`
