# Security Policy · سياسة الأمان

## Supported state · الحالة المدعومة

`0.9.0-rc3` is a release-candidate training simulation. Automated checks are complete; hosted-Colab instructor acceptance is still required. It is never suitable for production or real customer data.

الإصدار `0.9.0-rc3` محاكاة تدريبية مرشحة للإصدار. اكتملت الفحوص الآلية، وتبقى تجربة قبول المدربة في Colab المستضاف. ولا يصلح للإنتاج أو لبيانات العملاء الحقيقية.

## Never commit · ممنوع رفعه

- Passwords, tokens, API keys, cookies, private repository links, or `.env` files.
- Real customer, employee, trainee, order, payment, or support-ticket data. In public learner files, use only the instructor-assigned `learner_id` or GitHub username—not a real name, email, phone number, or national ID.
- Reference solutions, answer keys, hidden evaluations, hidden attack cases, instructor notes, grades, or actual recovery checkpoints.
- Raw or unredacted evidence, temporary checkpoints, and exported ZIP bundles. The final C29-redacted reports, manifest, and sanitized required evidence card may be committed to the learner's own repository.

---

- كلمات المرور أو رموز الوصول أو مفاتيح API أو Cookies أو روابط المستودعات الخاصة أو ملفات `.env`.
- بيانات حقيقية لعميل أو موظف أو متدرب أو طلب أو دفعة أو تذكرة دعم. استخدم في ملفات المتدرب العامة `learner_id` الذي تقدمه المدربة أو اسم مستخدم GitHub فقط، لا الاسم الحقيقي أو البريد أو رقم الهاتف أو الهوية الوطنية.
- الحلول المرجعية أو مفاتيح الإجابة أو التقييمات وحالات الهجوم الخفية أو ملاحظات المدربة أو الدرجات أو نقاط الاستعادة الفعلية.
- الأدلة الخام أو غير المنقحة، ونقاط الحفظ المؤقتة، وحزم ZIP المصدرة. يمكن رفع تقارير C29 المنقحة النهائية وبيان الملفات وبطاقة الأدلة الإلزامية المنقحة إلى مستودع المتدرب نفسه.

Use synthetic data only. The private instructor repository is still not a secrets manager.

استخدم بيانات مصطنعة فقط. مستودع المدربة الخاص ليس مديرًا للأسرار.

## Reporting a concern · الإبلاغ عن مشكلة

Do not open a public issue for a vulnerability, exposed credential, private link, or leaked learner information. Contact the repository owner privately, include the affected path and the minimum reproduction detail, and redact every secret or personal value.

لا تفتح Issue عامًا لثغرة أو بيان دخول مكشوف أو رابط خاص أو معلومات متدرب متسربة. تواصل مع مالك المستودع بقناة خاصة، وحدد المسار المتأثر وأقل قدر لازم لإعادة المشكلة، مع حجب كل سر أو قيمة شخصية.

If a credential is exposed, revoke or rotate it first. Deleting a file or commit does not make an exposed secret safe again.

إذا انكشف بيان دخول، فألغِه أو دوّره أولًا. حذف الملف أو الـCommit لا يجعل السر المكشوف آمنًا مجددًا.

The public [Lab help issue form](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml) is only for sanitized, reproducible technical questions. Do not use it for a vulnerability, exposed credential, private link, personal information, grade dispute, or private hand-in detail.

[نموذج مساعدة اللاب العام](https://github.com/almiyead-rgb/rafeeq-agentic-ai-labs/issues/new?template=lab-help.yml) مخصص للأسئلة التقنية المنقحة والقابلة لإعادة التنفيذ فقط. لا تستخدمه لثغرة أو بيان دخول مكشوف أو رابط خاص أو معلومات شخصية أو اعتراض على درجة أو تفاصيل تسليم خاصة.
