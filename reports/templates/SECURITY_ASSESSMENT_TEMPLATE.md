# Security assessment · التقييم الأمني

> Reference/enrichment template. `C23_GUARD_FIX_RETEST` generates the required `reports/SECURITY_ASSESSMENT.md` automatically. Use this template only if additional analysis is requested, and edit after the final C23 run.
>
> قالب مرجعي للإثراء. تولد `C23_GUARD_FIX_RETEST` ملف `reports/SECURITY_ASSESSMENT.md` الإلزامي تلقائيًا. استخدم هذا القالب فقط عند طلب تحليل إضافي، وعدّل بعد آخر تشغيل لـC23.

Use only the instructor-assigned `learner_id` or GitHub username in this public report. Put real identity only in the private hand-in form provided by the instructor.

استخدم `learner_id` الذي تقدمه المدربة أو اسم مستخدم GitHub فقط في هذا التقرير العام. ضع الهوية الحقيقية في نموذج التسليم الخاص الذي تقدمه المدربة فقط.

## 1. Assessment record · سجل التقييم

| Field | Entry · الإدخال |
|---|---|
| Public learner ID · معرف المتدرب العام | `[learner_id or GitHub username]` |
| Repository URL · رابط المستودع | `[TODO]` |
| Notebook and version · الدفتر والإصدار | `Rafeeq_Mini_Capstone.ipynb · [TODO]` |
| Test date (UTC) · تاريخ الاختبار | `[TODO]` |
| Runtime · بيئة التشغيل | `Google Colab Free · CPU · LLM_MODE=stub` |
| Scope · النطاق | `C21–C29 · public synthetic cases only` |

## 2. Assets and trust boundaries · الأصول وحدود الثقة

| Asset or boundary | Why it matters | Control implemented | Evidence |
|---|---|---|---|
| Agent state · حالة الوكيل | `[TODO]` | `[TODO]` | `Cell [TODO] / Evidence [TODO]` |
| Synthetic customer scope · نطاق العميل المصطنع | `[TODO]` | `[TODO]` | `Cell [TODO] / Evidence [TODO]` |
| Tool interface · واجهة الأداة | `[TODO]` | `[TODO]` | `Cell [TODO] / Evidence [TODO]` |
| MCP boundary · حدود MCP | `[TODO]` | `[TODO]` | `Cell [TODO] / Evidence [TODO]` |
| Human approval · الموافقة البشرية | `[TODO]` | `[TODO]` | `Cell [TODO] / Evidence [TODO]` |
| Trace and reports · التتبع والتقارير | `[TODO]` | `[TODO]` | `Cell [TODO] / Evidence [TODO]` |

## 3. Threat register · سجل التهديدات

Rate likelihood and impact as `Low`, `Medium`, or `High`. Do not invent a numeric risk formula.

قيّم الاحتمال والأثر بـ`Low` أو`Medium` أو`High`. لا تنشئ معادلة رقمية غير معتمدة للمخاطر.

| ID | Threat · التهديد | Entry point · نقطة الدخول | Likelihood | Impact | Preventive control · الضابط الوقائي | Detection / response · الكشف والاستجابة | Residual risk · الخطر المتبقي |
|---|---|---|---|---|---|---|---|
| `T-01` | Prompt injection · حقن الأوامر | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| `T-02` | Retrieved-content injection · حقن المحتوى المسترجع | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| `T-03` | Tool misuse · إساءة استخدام الأداة | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| `T-04` | Cross-customer memory leak · تسرب الذاكرة بين العملاء | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| `T-05` | Duplicate action on retry · تكرار الإجراء عند المحاولة | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| `T-06` | Approval bypass · تجاوز الموافقة | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| `T-07` | Excessive steps or cost · تجاوز الخطوات أو التكلفة | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |

## 4. Public attack-test results · نتائج اختبارات الهجوم العامة

Do not reproduce a dangerous payload in full. Use the supplied public case ID and a short sanitized description.

لا تنسخ حمولة خطرة كاملة. استخدم رقم الحالة العامة المرفقة ووصفًا مختصرًا ومنقحًا.

| Case ID | Target behavior · السلوك المستهدف | Expected result · المتوقع | Actual result · الفعلي | Before/after control · قبل/بعد الضابط | Pass? | Evidence |
|---|---|---|---|---|---|---|
| `[TODO]` | Injection refusal · رفض الحقن | `[TODO]` | `[TODO]` | `[TODO]` | `PASS / FAIL` | `Cell [TODO]` |
| `[TODO]` | Invalid tool argument · مدخل أداة غير صحيح | `[TODO]` | `[TODO]` | `[TODO]` | `PASS / FAIL` | `Cell [TODO]` |
| `[TODO]` | Unauthorized action · إجراء غير مصرح | `[TODO]` | `[TODO]` | `[TODO]` | `PASS / FAIL` | `Cell [TODO]` |
| `[TODO]` | Duplicate retry · تكرار المحاولة | `[TODO]` | `[TODO]` | `[TODO]` | `PASS / FAIL` | `Cell [TODO]` |
| `[TODO]` | Approval threshold · حد الموافقة | `[TODO]` | `[TODO]` | `[TODO]` | `PASS / FAIL` | `Cell [TODO]` |

## 5. Guardrail repair · تحسين الحواجز

- Weak behavior observed · السلوك الضعيف المرصود: `[TODO]`
- Root cause at the control level · السبب على مستوى الضابط: `[TODO]`
- Minimal repair applied · الإصلاح الأدنى المطبق: `[TODO]`
- Regression test rerun · فحص عدم التراجع المعاد: `[TODO]`
- Result after repair · النتيجة بعد الإصلاح: `[TODO]`
- Evidence card · بطاقة الدليل: `[TODO]`

## 6. Residual risk and treatment · المخاطر المتبقية والمعالجة

| Residual risk · الخطر المتبقي | Current limit · القيد الحالي | Treatment decision · قرار المعالجة | Owner · المالك | Due or review point · موعد المراجعة |
|---|---|---|---|---|
| `[TODO]` | `[TODO]` | `Accept / Mitigate / Avoid / Transfer` | `[TODO]` | `[TODO]` |

## 7. Security declaration · الإقرار الأمني

- [ ] I used only supplied synthetic data. · استخدمت البيانات المصطنعة المرفقة فقط.
- [ ] I did not include a password, token, API key, cookie, private link, `.env`, or environment file containing secrets. The supplied credential-free `.env.example` is allowed. · لم أضمّن كلمة مرور أو رمز وصول أو مفتاح API أو Cookie أو رابطًا خاصًا أو `.env` أو ملف بيئة يحمل أسرارًا. يُسمح بملف `.env.example` المرفق والخالي من بيانات الدخول.
- [ ] I did not include a copied solution, answer key, instructor material, scoring rule, or hidden test. · لم أضمّن حلًا منسوخًا أو مفتاح إجابة أو مادة للمدربة أو قاعدة درجات أو اختبارًا خفيًا.
- [ ] I recorded operational evidence, not private chain-of-thought. · سجلت أدلة تشغيلية لا التفكير الداخلي الخاص.
- [ ] `C23_GUARD_FIX_RETEST` passed when this assessment was generated. · نجح `C23_GUARD_FIX_RETEST` عند توليد هذا التقييم.

Learner confirmation · إقرار المتدرب: `[TODO: learner_id and date · معرّف المتدرب والتاريخ]`
