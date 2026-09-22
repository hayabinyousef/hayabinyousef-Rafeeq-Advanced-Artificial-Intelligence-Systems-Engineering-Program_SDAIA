# Learner guide · دليل المتدرب

This guide is the beginner path from an empty GitHub account to a verified Rafeeq Mini submission. The project is a supervised **guided-engineering** exercise using free Google Colab CPU, synthetic data, and a deterministic stub model; it is not a production deployment.

هذا الدليل هو المسار المبسط من حساب GitHub جديد إلى تسليم رفيق المصغّر المتحقق منه. المشروع تمرين **هندسة موجهة** تحت الإشراف يستخدم Google Colab CPU المجاني وبيانات مصطنعة ونموذج Stub حتميًا، وليس نشرًا إنتاجيًا.

## 1. Project scenario · سيناريو المشروع

Rafeeq Mini is a bilingual agentic operations assistant for a fictional delivery company. It understands an Arabic or English order/refund request, verifies the supplied synthetic customer scope, retrieves the active policy, routes the task to a specialist, and pauses a simulated refund above SAR 500 for documented human approval.

رفيق المصغّر مساعد عمليات وكيلي ثنائي اللغة لشركة توصيل افتراضية. يفهم طلبًا بالعربية أو الإنجليزية عن طلب شراء أو استرداد، ويتحقق من نطاق العميل المصطنع، ويسترجع السياسة السارية، ويوجه المهمة إلى وكيل متخصص، ويوقف الاسترداد المحاكى الأعلى من 500 ريال حتى توثيق الموافقة البشرية.

No real customer, payment, order, or enterprise system is used.

لا يستخدم المشروع أي عميل أو دفعة أو طلب أو نظام مؤسسي حقيقي.

## 2. Create the accounts once · إنشاء الحسابات مرة واحدة

| Service | Beginner action | إجراء المبتدئ |
|---|---|---|
| GitHub | Create an account, verify the email, and keep the username available. Use a password manager and enable account protections offered by GitHub. [Official account guide](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) | أنشئ حسابًا، وفعّل البريد، واحتفظ باسم المستخدم. استخدم مدير كلمات مرور وفعّل وسائل حماية الحساب التي يوفرها GitHub. [الدليل الرسمي](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) |
| Google Colab | Open [Google Colab](https://colab.research.google.com/) with the Google account that will hold your Drive copy. | افتح [Google Colab](https://colab.research.google.com/) بالحساب الذي سيحفظ نسخة الدفتر في Drive. |

Never share a password, one-time code, recovery code, token, or API key with the instructor, another learner, an issue, or a notebook.

لا تشارك كلمة مرور أو رمز تحقق أو رمز استعادة أو Token أو مفتاح API مع المدربة أو متدرب آخر أو Issue أو دفتر كولاب.

### Preflight repository policy · سياسة المستودع في التجهيز المسبق

Create the repository during preflight so account and email-verification problems are discovered before Day 3. Before C29, publish only the safe progress log—never code, the live notebook, raw evidence, or runtime files:

أنشئ المستودع أثناء التجهيز المسبق حتى تظهر مشكلات الحساب أو توثيق البريد قبل اليوم الثالث. قبل C29 لا تنشر سوى سجل التقدم الآمن، ولا تنشر الكود أو الدفتر الجاري أو الأدلة الخام أو ملفات بيئة التشغيل:

1. While signed in, select **+ → New repository**, choose your personal account, and use a clear name such as `rafeeq-mini-yourusername`. · بعد تسجيل الدخول اختر **+ → New repository**، ثم حسابك الشخصي، واستخدم اسمًا واضحًا مثل `rafeeq-mini-yourusername`.
2. Select **Public**. Leave README, `.gitignore`, license, and template options unselected. · اختر **Public**، واترك README و`.gitignore` والرخصة والقالب دون تحديد.
3. Select **Create repository**. Do not use **Fork**. · اختر **Create repository**، ولا تستخدم **Fork**.
4. In the **About** panel, add a concise description such as `Bilingual safe delivery-support agent built in the Advanced Agentic AI Systems Engineering course`. Do not include a real name or contact information. · أضف في **About** وصفًا مختصرًا مثل `مساعد وكيلي ثنائي اللغة وآمن لدعم عمليات التوصيل بُني ضمن دورة هندسة أنظمة الذكاء الاصطناعي التوكيلي المتقدمة`، دون اسم حقيقي أو معلومات اتصال.
5. Select **creating a new file**, name it `LEARNING_PROGRESS.md`, and paste the [safe progress template](LEARNING_PROGRESS_TEMPLATE.md). Commit with `docs: initialize Rafeeq Mini progress log`. · اختر **creating a new file**، وسمّه `LEARNING_PROGRESS.md`، والصق [قالب التقدم الآمن](LEARNING_PROGRESS_TEMPLATE.md)، ثم احفظه برسالة `docs: initialize Rafeeq Mini progress log`.
6. Copy the repository URL to a private note. Until C29, edit only this progress file after a passed gate. · انسخ رابط المستودع في ملاحظة خاصة. وحتى C29 لا تعدّل سوى ملف التقدم بعد نجاح البوابة.

If an employer or institutional policy prevents a public repository, tell the instructor before Day 1. Use only the private route explicitly approved by the instructor, and never paste a private repository link into a public issue. · إذا منعت سياسة جهة العمل أو المؤسسة إنشاء مستودع عام، فأبلغ المدربة قبل اليوم الأول. استخدم فقط المسار الخاص الذي تعتمده المدربة صراحة، ولا تلصق رابط مستودع خاص في Issue عام.

Official reference: [Creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)

Course and portfolio reuse is governed by the limited [`COURSE_USE_PERMISSION.md`](../COURSE_USE_PERMISSION.md). That permission may allow reuse outside assessment, but this graded hand-in path still requires a new standalone repository—not a fork.

يخضع استخدام المواد في الدورة أو الملف المهني لإذن [`COURSE_USE_PERMISSION.md`](../COURSE_USE_PERMISSION.md) المحدود. قد يسمح الإذن بإعادة الاستخدام خارج التقييم، لكن مسار التسليم المقيم هنا ما زال يشترط مستودعًا مستقلًا جديدًا لا Fork.

Use the instructor-assigned `learner_id` or your GitHub username in public filenames and reports. Do not publish your real name, email, phone number, national ID, or other identifying information. The private hand-in form provided by the instructor is the identity-mapping record.

استخدم `learner_id` الذي تقدمه المدربة أو اسم مستخدم GitHub في الملفات والتقارير العامة. لا تنشر اسمك الحقيقي أو بريدك أو رقم هاتفك أو هويتك الوطنية أو أي بيانات تعريفية أخرى. نموذج التسليم الخاص الذي تقدمه المدربة هو سجل ربط الهوية بالتسليم.

## 3. Open the official course notebook · افتح دفتر الدورة الرسمي

Your starting point is the notebook in the official course repository owned by `almiyead-rgb`—not a learner repository. Open it with the course Colab button/link below:

نقطة البداية هي الدفتر في مستودع الدورة الرسمي التابع للحساب `almiyead-rgb`، وليس مستودع المتدرب. افتحه بزر/رابط كولاب الآتي:

**[Open the official Rafeeq Mini notebook in Google Colab · افتح دفتر رفيق الرسمي في كولاب](https://colab.research.google.com/github/almiyead-rgb/rafeeq-agentic-ai-labs/blob/v0.9.0-rc3/notebooks/Rafeeq_Mini_Capstone.ipynb)**

1. Confirm the address contains `github/almiyead-rgb/rafeeq-agentic-ai-labs`. · تأكد أن العنوان يحتوي `github/almiyead-rgb/rafeeq-agentic-ai-labs`.
2. Immediately select **File → Save a copy in Drive**. · اختر فورًا **File → Save a copy in Drive**.
3. Work only in that Drive copy; do not edit the official source. · اعمل فقط في نسخة Drive، ولا تعدل المصدر الرسمي.
4. Keep the original cell IDs `C0–C29` and use the standard CPU runtime; no GPU is needed. · احتفظ بمعرفات الخلايا `C0–C29` واستخدم CPU القياسي؛ لا حاجة إلى GPU.

Official reference: [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)

## 4. Build in Drive; publish only safe progress · ابنِ في Drive وانشر التقدم الآمن فقط

Across the three days, reopen your saved Drive copy, run from the top, complete only learner `TODO` areas, and save after every passed gate. After C9 and C20, change only the matching `PENDING` status in `LEARNING_PROGRESS.md` to `PASS` and make the documented Git commit. Do not upload project code or runtime evidence before C29.

خلال الأيام الثلاثة، أعد فتح نسخة Drive المحفوظة، وشغّل من الأعلى، وأكمل مناطق `TODO` الخاصة بالمتدرب فقط، واحفظ بعد كل بوابة ناجحة. بعد C9 وC20 غيّر حالة `PENDING` المقابلة فقط داخل `LEARNING_PROGRESS.md` إلى `PASS`، ثم أنشئ Commit التوثيق المحدد. لا ترفع كود المشروع أو أدلة التشغيل قبل C29.

## 5. At C29, upload beside the safe progress log · عند C29 ارفع بجانب سجل التقدم الآمن

Only after `C29_EXPORT_SAFETY_CHECK` passes, upload the project package to the public repository that currently contains only `LEARNING_PROGRESS.md`. The beginner path uses the GitHub website and requires no terminal, PAT, or template setting.

بعد نجاح `C29_EXPORT_SAFETY_CHECK` فقط، ارفع حزمة المشروع إلى المستودع العام الذي لا يحتوي حاليًا إلا `LEARNING_PROGRESS.md`. يستخدم مسار المبتدئ موقع GitHub، ولا يحتاج إلى Terminal أو PAT أو تفعيل قالب.

Before uploading, confirm that the repository belongs to your account, is public, is not a fork, and contains only the safe progress history you created through the instructed path.

قبل الرفع تأكد أن المستودع تابع لحسابك، وعام، وليس Fork، ولا يحتوي إلا سجل التقدم الآمن المنشأ وفق المسار المحدد.

Now prepare and upload the clean export—not the ZIP:

الآن جهّز التصدير النظيف وارفعه، لا ملف ZIP:

Complete `TODO-14`, confirm all four review flags are `True`, deliberately enable the `FINAL_EXPORT` switch, and rerun C29. `FINAL_EXPORT_SKIPPED` means the switch is still off; `FINAL_EXPORT_BLOCKED` means at least one safety or completion gate still fails.

أكمل `TODO-14`، وتأكد أن علامات المراجعة الأربع `True`، ثم فعّل مفتاح `FINAL_EXPORT` عمدًا وأعد تشغيل C29. تعني `FINAL_EXPORT_SKIPPED` أن المفتاح ما زال مغلقًا، وتعني `FINAL_EXPORT_BLOCKED` أن أحد فحوص السلامة أو الاكتمال ما زال فاشلًا.

1. Confirm that C29 prints `FINAL_EXPORT_CREATED`. In Colab open the left **Files** pane, locate the printed path for `rafeeq-mini-submission.zip`, open its three-dot menu, and select **Download**. · تأكد أن C29 يعرض `FINAL_EXPORT_CREATED`. افتح لوحة **Files** اليسرى في كولاب، وحدد المسار المطبوع لملف `rafeeq-mini-submission.zip`، ثم افتح قائمة النقاط الثلاث واختر **Download**.
2. Extract the ZIP on your computer. · فك ضغط الملف على جهازك.
3. Inspect the extracted tree. It contains the sanitized public template files and required reports, but deliberately excludes the notebook currently open in Colab and `reports/checkpoints/`. · افحص البنية المستخرجة؛ تحتوي ملفات القالب العامة المنقحة والتقارير المطلوبة، لكنها تستبعد عمدًا دفتر كولاب الجاري ومجلد `reports/checkpoints/`.
4. In Colab select **File → Download → Download .ipynb**. This downloads your completed working copy. · في كولاب اختر **File → Download → Download .ipynb** لتنزيل نسخة عملك المكتملة.
5. Rename the downloaded file exactly `Rafeeq_Mini_Capstone.ipynb` if needed, then place it inside the extracted `notebooks/` folder. · عند الحاجة أعد تسمية الملف إلى `Rafeeq_Mini_Capstone.ipynb` بالضبط، ثم ضعه داخل مجلد `notebooks/` المستخرج.
6. Copy `reports/templates/EVIDENCE_CARD_TEMPLATE.md` to `reports/EVIDENCE_CARD.md`. Complete three concise cards—one per day—using only your `learner_id`, synthetic case IDs, actual cell/gate results, and the assessment `run_id` when available. This instructor-assessment record is added after export and is therefore not hashed by the C29 manifest. · انسخ `reports/templates/EVIDENCE_CARD_TEMPLATE.md` إلى `reports/EVIDENCE_CARD.md`. أكمل ثلاث بطاقات مختصرة—بطاقة لكل يوم—باستخدام `learner_id` فقط ومعرفات الحالات المصطنعة ونتائج الخلايا/البوابات الفعلية و`run_id` للتقييم عند توفره. يضاف سجل تقييم المدربة هذا بعد التصدير، ولذلك لا يتضمنه تجزئة بيان C29.
7. Confirm the combined folder now contains `notebooks/Rafeeq_Mini_Capstone.ipynb`, `reports/EVIDENCE_CARD.md`, `reports/PROJECT_REPORT.md`, `reports/SECURITY_ASSESSMENT.md`, `reports/trace.jsonl`, `reports/assessment_results.json`, `reports/monitoring_dashboard.png`, and `reports/submission_manifest.json`. · تأكد أن المجلد المدمج يحتوي الدفتر وبطاقة الأدلة والتقريرين والملفات الأربعة بالمسارات المحددة.
8. Remove nothing required, but do not add `rafeeq-mini-submission.zip`, `reports/checkpoints/`, raw outputs outside the sanitized trace, temporary runtime files, credentials, private links, or real data. · لا تحذف ملفًا إلزاميًا، ولا تضف `rafeeq-mini-submission.zip` أو `reports/checkpoints/` أو مخرجات خامًا خارج الأثر المنقح أو ملفات تشغيل مؤقتة أو بيانات دخول أو روابط خاصة أو بيانات حقيقية.
9. In your repository select **Add file → Upload files**. Keep the existing `LEARNING_PROGRESS.md`. · في مستودعك اختر **Add file → Upload files**، واحتفظ بملف `LEARNING_PROGRESS.md` الموجود.
10. Drag the **contents inside** the combined folder. Do not upload only the ZIP, and do not create an extra outer folder. · اسحب **المحتويات داخل** المجلد المدمج؛ لا ترفع ملف ZIP فقط ولا تنشئ مجلدًا خارجيًا زائدًا.
11. Mark the Day 3 line in `LEARNING_PROGRESS.md` as `PASS`, include it with the upload, and use the commit message `feat: submit Rafeeq Mini capstone`. · غيّر حالة اليوم الثالث في `LEARNING_PROGRESS.md` إلى `PASS`، وضمّنه مع الرفع، واستخدم رسالة `feat: submit Rafeeq Mini capstone`.
12. Verify that `README.md`, `.github/`, `notebooks/`, `data/`, `src/`, `mcp_server/`, `tests/`, and `reports/` appear at the repository root. · تحقق من ظهور `README.md` و`.github/` والمجلدات المذكورة في جذر المستودع.
13. Open **Actions → Learner submission quality**, open the run for this commit, and wait for the green check. Record the final commit URL only after it is green. · افتح **Actions ← Learner submission quality**، ثم تشغيل هذا Commit، وانتظر العلامة الخضراء. لا تسجل رابط Commit النهائي إلا بعد نجاحه.

Official reference: [Adding a file to a repository](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)

### If GitHub Actions is red · إذا كان GitHub Actions أحمر

1. Open the failed run and expand the first failed step. Copy only the first useful, sanitized error line. · افتح التشغيل الفاشل ووسّع أول خطوة فاشلة، وانسخ أول سطر خطأ مفيد ومنقح فقط.
2. Do not edit `.github/workflows/`, public tests, validators, or generated evidence to hide the failure. · لا تعدّل `.github/workflows/` أو الاختبارات العامة أو أدوات التحقق أو الأدلة المولدة لإخفاء الفشل.
3. Return to the saved Drive notebook, repair the smallest relevant learner `TODO`, rerun that cell and every dependent gate through C29, then create a fresh clean export. · ارجع إلى دفتر Drive المحفوظ، وأصلح أصغر `TODO` مرتبط، ثم أعد تشغيل الخلية والبوابات التابعة حتى C29 وأنشئ تصديرًا نظيفًا جديدًا.
4. Replace only the affected submission files in GitHub using a new commit such as `fix: resubmit Rafeeq Mini after validation`; preserve the existing commit history. · استبدل ملفات التسليم المتأثرة فقط في GitHub عبر Commit جديد مثل `fix: resubmit Rafeeq Mini after validation`، مع الحفاظ على سجل Commits السابق.
5. Wait for the new run to turn green. If the error remains, use the public [Lab help form](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml) only after removing private data. · انتظر نجاح التشغيل الجديد. إذا استمر الخطأ فاستخدم [نموذج مساعدة اللاب](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml) بعد حذف البيانات الخاصة فقط.

## 6. Use the safe run loop · استخدم دورة التشغيل الآمنة

For every learner task:

لكل مهمة متدرب:

```text
Read the objective → complete TODO → run the cell → run the public check
→ inspect the result → save in Drive → continue only after PASS
```

```text
اقرأ الهدف ← أكمل TODO ← شغّل الخلية ← شغّل الفحص العام
← افحص النتيجة ← احفظ في Drive ← لا تنتقل إلا بعد PASS
```

- Run from top to bottom. Do not skip dependencies. · شغّل من الأعلى إلى الأسفل ولا تتجاوز الاعتماديات.
- Change only learner `TODO` areas. · عدّل مناطق `TODO` الخاصة بالمتدرب فقط.
- Do not bypass a failed check. Read its message and repair the smallest relevant learner change. · لا تتحايل على فحص فاشل؛ اقرأ رسالته وأصلح أصغر تعديل مرتبط.
- Do not store private chain-of-thought. Keep only decision, tool, route, result, counters, and a short operational rationale. · لا تخزن التفكير الداخلي الخاص؛ احتفظ بالقرار والأداة والمسار والنتيجة والعدادات ومبرر تشغيلي قصير.

## 7. Three-day progression · التدرج خلال ثلاثة أيام

| Day | Cells | Build outcome · ناتج البناء | Gate |
|---|---|---|---|
| Day 1 · اليوم الأول | `C0–C9` | Architecture, typed state, bounded graph, observable traces, ReAct, tool schema, and local MCP server/client. · معمارية وحالة محددة ومخطط محدود وتتبع مرصود وReAct ومخطط أداة وخادم/عميل MCP محلي. | `C9_DAY1_GATE` |
| Day 2 · اليوم الثاني | `C10–C20` | Restore, session memory, scoped recall, policy retrieval, specialists, supervisor, typed delegation, Plan-and-Execute, and interrupt/resume approval. · استعادة وذاكرة جلسة واسترجاع معزول وسياسات ووكلاء ومنسق وتفويض محدد وPlan-and-Execute وإيقاف/استئناف للموافقة. | `C20_DAY2_GATE` |
| Day 3 · اليوم الثالث | `C21–C29` | Threat model, attack suite, guard fix/retest, reflection gate, trace evaluation, one measured optimization, scorecard, readiness, and safe export. · نموذج تهديد وحزمة هجوم وإصلاح وإعادة فحص وبوابة مراجعة وتقييم تتبع وتحسين واحد مقاس وبطاقة أداء وجاهزية وتصدير آمن. | `C29_EXPORT_SAFETY_CHECK` |

### Core versus stretch · الأساسي مقابل التوسع

The **core path** is mandatory: all 14 learner TODOs, C0–C29 in order, all three gates, required reports/evidence, SDAIA administrative evidence, the clean GitHub upload, and a green Actions run. **Stretch work** is optional only when explicitly marked or announced by the instructor; it cannot replace a failed core requirement and does not affect a beginner who completes the core path.

**المسار الأساسي** إلزامي: مهام المتدرب الـ14، وتشغيل C0–C29 بالترتيب، والبوابات الثلاث، والتقارير/الأدلة ومتطلبات سدايا الإدارية، ورفع GitHub النظيف، ونجاح Actions. أما **مسار التوسع** فاختياري عندما تحدده أو تعلنه المدربة صراحة؛ ولا يعوض متطلبًا أساسيًا فاشلًا ولا يؤثر في المبتدئ الذي يكمل المسار الأساسي.

Full cell mapping: [`notebooks/README.md`](../notebooks/README.md)

### Compare with the validated reference · قارن بالمرجع المتحقق

Use the reference only **after completing your own attempt**. It compares observable evidence, not code or TODO answers.

استخدم المرجع **بعد إكمال محاولتك بنفسك** فقط. فهو يقارن الأدلة القابلة للملاحظة، وليس الكود أو إجابات المهام.

1. At `C9`, `C20`, `C23`, `C28`, and `C29`, download or keep the JSON evidence generated by the notebook. · عند `C9` و`C20` و`C23` و`C28` و`C29` نزّل أو احتفظ بأدلة JSON التي أنشأها الدفتر.
2. Open the [bilingual comparison page](https://almiyead-rgb.github.io/rafeeq-agentic-ai-labs/compare.html) and select your JSON file; the page detects its stage automatically. · افتح [صفحة المقارنة الثنائية اللغة](https://almiyead-rgb.github.io/rafeeq-agentic-ai-labs/compare.html) وحدد ملف JSON الخاص بك؛ تتعرف الصفحة على مرحلته تلقائيًا.
3. Read the result: **Match · مطابق** means the declared evidence agrees; **Review · راجع** means a supporting stable value differs and needs inspection; **Needs fix · يحتاج إصلاحًا** means a required or critical value is missing or different. · اقرأ النتيجة: **مطابق** يعني توافق الدليل المعلن، و**راجع** يعني اختلاف قيمة ثابتة مساندة تستلزم الفحص، و**يحتاج إصلاحًا** يعني غياب قيمة مطلوبة أو حرجة أو اختلافها.
4. If review or repair is needed, return to the cell named by the comparison page, make the smallest relevant learner change, then rerun that cell and its gate. · إذا لزم الفحص أو الإصلاح، فارجع إلى الخلية التي تسميها صفحة المقارنة، ونفّذ أصغر تعديل مرتبط بالمتدرب، ثم أعد تشغيل الخلية وبوابتها.

Timestamps, generated IDs, paths, hashes, file sizes, and latency are intentionally ignored because they may differ between valid runs. The comparison happens locally in your browser; your selected file is not uploaded or stored. The instructor's `reference-results/` files are comparison aids and are deliberately excluded from `rafeeq-mini-submission.zip`—do not add them to your submission.

تُتجاهل عمدًا الطوابع الزمنية والمعرّفات المولدة والمسارات والبصمات وأحجام الملفات وزمن الاستجابة لأنها قد تختلف بين تشغيلات صحيحة. تتم المقارنة محليًا داخل متصفحك؛ ولا يُرفع الملف الذي تختاره أو يُحفظ. ملفات المدربة داخل `reference-results/` أدوات للمقارنة، وهي مستبعدة عمدًا من `rafeeq-mini-submission.zip`—فلا تضفها إلى تسليمك.

## 8. Save Drive evidence and safe Git checkpoints · احفظ أدلة Drive ونقاط Git الآمنة

After each gate passes, save the Drive notebook first. Then edit only the public status in `LEARNING_PROGRESS.md`; never copy raw output or code into the progress log. Use these Git messages:

بعد نجاح كل بوابة احفظ دفتر Drive أولًا. ثم عدّل الحالة العامة فقط داخل `LEARNING_PROGRESS.md`، ولا تنسخ مخرجات خامًا أو كودًا إلى سجل التقدم. استخدم رسائل Git الآتية:

```text
docs: initialize Rafeeq Mini progress log
docs(day1): record C9 gate
docs(day2): record C20 gate
feat: submit Rafeeq Mini capstone
```

The first three commits contain documentation only. The final commit adds the guarded C29 export. Meaning and safety matter more than commit count; never create artificial empty commits.

تحتوي أول ثلاثة Commits على توثيق فقط، ويضيف Commit الأخير تصدير C29 المحمي. دلالة السجل وسلامته أهم من العدد؛ فلا تنشئ Commits فارغة مصطنعة.

Inspect every exported file before uploading. A commit must never include a credential, private link, real data, raw runtime dump, completed solution, instructor material, hidden test, temporary checkpoint, or `rafeeq-mini-submission.zip`.

افحص كل ملف مصدّر قبل رفعه. ويُمنع أن يتضمن Commit بيانات دخول أو رابطًا خاصًا أو بيانات حقيقية أو سجل تشغيل خامًا أو حلًا مكتملًا أو مادة للمدربة أو اختبارًا خفيًا أو نقطة مؤقتة أو `rafeeq-mini-submission.zip`.

## 9. Recover after Runtime loss · استعد العمل بعد فقد البيئة

Colab may disconnect or reset. This does not mean the project is lost.

قد يفصل كولاب الاتصال أو يعيد ضبط البيئة، وهذا لا يعني فقد المشروع.

1. Reopen the latest Drive copy. · افتح أحدث نسخة في Drive.
2. Select CPU and run `C0_ENV_DOCTOR`. · اختر CPU وشغّل `C0_ENV_DOCTOR`.
3. Rerun completed cells from the top to rebuild Python state. · أعد تشغيل الخلايا المكتملة من الأعلى لبناء حالة Python.
4. Stop at your last passed gate, compare it with the saved checkpoint label and gate evidence, then continue. · توقف عند آخر بوابة ناجحة وقارنها بتسمية نقطة التقدم ودليل البوابة المحفوظين ثم تابع.

Detailed recovery: [`recovery/README.md`](../recovery/README.md)

## 10. Complete the reports · أكمل التقارير

The notebook generates the two required learner reports: `C23_GUARD_FIX_RETEST` creates the security assessment and `C28_READINESS` creates the project report.

يولد الدفتر تقريري المتدرب الإلزاميين: تنشئ `C23_GUARD_FIX_RETEST` التقييم الأمني، وتنشئ `C28_READINESS` تقرير المشروع.

- `reports/PROJECT_REPORT.md`
- `reports/SECURITY_ASSESSMENT.md`

Use [`reports/templates/SUBMISSION_CHECKLIST.md`](../reports/templates/SUBMISSION_CHECKLIST.md) locally before upload. It is a verification aid, not a submission artifact.

استخدم [`reports/templates/SUBMISSION_CHECKLIST.md`](../reports/templates/SUBMISSION_CHECKLIST.md) محليًا قبل الرفع. هي أداة تحقق وليست ملف تسليم.

Review the generated reports for accuracy. The detailed templates in `reports/templates/` are optional enrichment references; do not replace a failed result or invent a value. If the instructor requests enrichment, edit only after the final generating cell so a rerun does not overwrite your work.

راجع دقة التقريرين المولدين. القوالب المفصلة في `reports/templates/` مراجع اختيارية للإثراء؛ لا تستبدل نتيجة فاشلة ولا تخترع قيمة. إذا طلبت المدربة إثراءً إضافيًا فعدّل بعد آخر خلية تولد التقرير حتى لا تمحو إعادة التشغيل عملك.

The clean final run generates `reports/trace.jsonl` at C25, `reports/assessment_results.json` and `reports/monitoring_dashboard.png` at C27, and the reports/readiness result at C28. C29 performs the final safety check, creates `reports/submission_manifest.json`, and packages the clean files. These four sanitized artifacts are required inside the extracted C29 files. After extraction, complete `reports/EVIDENCE_CARD.md` from the template with one concise card for each day; this additional record is required for instructor assessment but is not an automated C29 output.

ينتج التشغيل النهائي النظيف `reports/trace.jsonl` عند C25، و`reports/assessment_results.json` و`reports/monitoring_dashboard.png` عند C27، والتقارير/نتيجة الجاهزية عند C28. ينفذ C29 فحص السلامة النهائي، وينشئ `reports/submission_manifest.json`، ويحزم الملفات النظيفة. هذه الملفات الأربعة المنقحة إلزامية داخل ملفات C29 المستخرجة. بعد فك الحزمة أكمل `reports/EVIDENCE_CARD.md` من القالب ببطاقة مختصرة لكل يوم؛ وهذا السجل الإضافي إلزامي لتقييم المدربة لكنه ليس مخرجًا آليًا من C29.

When `C29_EXPORT_SAFETY_CHECK` succeeds, it creates `rafeeq-mini-submission.zip` as a transport container. Extract it and upload its clean contents as described in section 5; do not upload the ZIP itself.

عند نجاح `C29_EXPORT_SAFETY_CHECK` ينشئ `rafeeq-mini-submission.zip` بوصفه حاوية نقل. فك ضغطه وارفع محتوياته النظيفة كما في القسم 5، ولا ترفع ملف ZIP نفسه.

Use the templates in [`reports/templates/`](../reports/templates/). Every important claim needs a cell ID, a public case or metric, and its result; add the assessment `run_id` from `reports/assessment_results.json` when available. Do not invent a C29 export ID. After export, the manifest timestamp and SHA-256 values may be used for file verification, not as required fields inside reports generated earlier. Record the final repository and commit links in the designated hand-in form after upload.

استخدم القوالب في [`reports/templates/`](../reports/templates/). يحتاج كل ادعاء مهم إلى رقم خلية وحالة عامة أو مقياس ونتيجته؛ وأضف `run_id` للتقييم من `reports/assessment_results.json` عند توفره. لا تخترع معرفًا لتصدير C29. بعد التصدير يمكن استخدام وقت البيان وقيم SHA-256 للتحقق من الملفات، وليس كحقول مطلوبة داخل تقارير مولدة سابقًا. سجل رابط المستودع وCommit النهائيين في نموذج التسليم المحدد بعد الرفع.

## 11. Pass conditions · شروط الاجتياز

Your project is ready for assessment only when all conditions below are true:

يكون مشروعك جاهزًا للتقييم فقط عند تحقق جميع الشروط التالية:

Read the complete [100-point assessment rubric](ASSESSMENT_RUBRIC.md) and [SDAIA administrative requirements](SDAIA_ADMIN_REQUIREMENTS.md): passing requires at least 70/100 **and** every non-compensable gate. · اقرأ [معيار التقييم الكامل من 100 درجة](ASSESSMENT_RUBRIC.md) و[متطلبات سدايا الإدارية](SDAIA_ADMIN_REQUIREMENTS.md): يتطلب الاجتياز 70/100 على الأقل **مع** نجاح جميع البوابات غير القابلة للتعويض.

- Your repository is public, owned by you, created as a new repository through the browser, and is not a fork. · مستودعك عام وتملكه أنت ومنشأ كمستودع جديد عبر المتصفح وليس Fork.
- The GitHub About description, professional README, technical documentation, course reference, SDAIA Academy link, and meaningful progress history satisfy the 10-point administrative rubric. · يستوفي وصف About وREADME الاحترافي والتوثيق الفني وذكر الدورة ورابط أكاديمية سدايا وسجل التقدم ذي المعنى معيار المتطلبات الإدارية من 10 درجات.
- `LEARNING_PROGRESS.md` contains the safe setup, Day 1, Day 2, and Day 3 checkpoints; no raw evidence was published before C29. · يحتوي `LEARNING_PROGRESS.md` نقاط التجهيز واليوم الأول والثاني والثالث الآمنة، ولم تنشر أدلة خام قبل C29.
- The extracted project tree is visible; the repository is not a ZIP-only upload. · تظهر بنية ملفات المشروع المستخرجة، ولا يقتصر المستودع على ملف ZIP.
- The final notebook opens and runs from `C0` to `C29` on Colab Free CPU with `LLM_MODE=stub`. · يفتح الدفتر النهائي ويعمل من `C0` إلى `C29` على Colab Free CPU بوضع `LLM_MODE=stub`.
- `C9_DAY1_GATE` and `C20_DAY2_GATE` each report `all_passed=true`, and the enabled final C29 run prints `FINAL_EXPORT_CREATED`. · تعرض كل من `C9_DAY1_GATE` و`C20_DAY2_GATE` القيمة `all_passed=true`، ويطبع تشغيل C29 النهائي بعد تفعيله `FINAL_EXPORT_CREATED`.
- The project report, security assessment, sanitized trace, assessment results, monitoring dashboard, and manifest are visible and mutually consistent. · تقرير المشروع والتقييم الأمني والأثر المنقح ونتائج التقييم ولوحة المراقبة وبيان التسليم ظاهرة ومتسقة.
- `reports/EVIDENCE_CARD.md` contains one concise, sanitized evidence card for each day. · يحتوي `reports/EVIDENCE_CARD.md` بطاقة دليل مختصرة ومنقحة لكل يوم.
- The final checkpoint commit is present and its link is recorded. · يوجد Commit النهائي ومسجل رابطه.
- **Actions → Learner submission quality** is green for the exact final commit being submitted. · يظهر فحص **Actions ← Learner submission quality** باللون الأخضر لنفس Commit النهائي المرسل.
- The repository contains no real data, credentials, private links, copied solutions, instructor material, recovery answers, grades, or hidden tests. · يخلو المستودع من البيانات الحقيقية وبيانات الدخول والروابط الخاصة والحلول المنسوخة ومواد المدربة وإجابات الاستعادة والدرجات والاختبارات الخفية.

At the start of the final day, complete the course-evaluation link if the SDAIA coordinator or supervisor supplies it. Completion is handled privately and has no project points; do not publish responses or screenshots in GitHub. · في بداية اليوم الأخير أكمل رابط تقييم الدورة إذا أرسله منسق أو مشرف سدايا. يعالج الإتمام بصورة خاصة ولا يحمل درجات للمشروع؛ فلا تنشر الإجابات أو اللقطات في GitHub.

## 12. Ask for help efficiently · اطلب المساعدة بكفاءة

Provide only these six items:

قدّم هذه العناصر الستة فقط:

1. Cell ID. · رقم الخلية.
2. Last passed gate. · آخر بوابة ناجحة.
3. First useful error line. · أول سطر خطأ مفيد.
4. Expected behavior. · السلوك المتوقع.
5. Actual behavior. · السلوك الفعلي.
6. Runtime type and whether it reset. · نوع البيئة وهل أعيد ضبطها.

Remove all private values before posting. Never paste a password, token, API key, private repository link, real record, or full browser screenshot.

احذف جميع القيم الخاصة قبل النشر. لا تلصق كلمة مرور أو Token أو مفتاح API أو رابط مستودع خاص أو سجلًا حقيقيًا أو لقطة كاملة للمتصفح.

For a public technical question, use the bilingual [Lab help issue form](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml). Do not use a public issue for a vulnerability, exposed credential, private link, personal information, grade dispute, or private submission detail; follow [`SECURITY.md`](../SECURITY.md) and the instructor's private channel.

للسؤال التقني العام استخدم [نموذج مساعدة اللاب الثنائي](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml). لا تستخدم Issue عامًا لثغرة أو بيان دخول مكشوف أو رابط خاص أو معلومات شخصية أو اعتراض على درجة أو تفاصيل تسليم خاصة؛ اتبع [`SECURITY.md`](../SECURITY.md) وقناة المدربة الخاصة.

## 13. Hand-in, receipt, and resubmission · التسليم والاستلام وإعادة التسليم

| Item | Rule · القاعدة |
|---|---|
| Deadline · الموعد | Provided by the instructor during the course. Do not infer a deadline from GitHub timestamps. · تقدمه المدربة أثناء الدورة؛ لا تستنتج موعدًا من أوقات GitHub. |
| Private hand-in form · نموذج التسليم الخاص | The instructor provides the form/link. Enter your real identity only there, together with `learner_id`, public repository URL, final commit URL/SHA, and the three gate markers. · تقدم المدربة الرابط؛ أدخل هويتك الحقيقية هناك فقط مع `learner_id` ورابط المستودع العام ورابط/SHA آخر Commit وعلامات البوابات الثلاث. |
| Receipt · إثبات الاستلام | Keep the confirmation issued by the form or instructor. A green Actions run proves automated checks only; it is not proof that the instructor received the submission. · احتفظ بالتأكيد الصادر من النموذج أو المدربة. نجاح Actions يثبت الفحوص الآلية فقط، ولا يثبت استلام المدربة. |
| Resubmission · إعادة التسليم | Follow the instructor's announced retry/late policy. Preserve history, submit a new green commit, and update the form with the new commit URL; do not delete the earlier commit unless instructed. · اتبع سياسة الإعادة/التأخير التي تعلنها المدربة. احتفظ بالسجل، وأرسل Commit جديدًا ناجحًا، وحدّث النموذج برابط Commit الجديد؛ ولا تحذف السابق إلا بتوجيه. |

Official GitHub help: [GitHub Docs](https://docs.github.com/)
