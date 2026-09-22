# Rafeeq release acceptance · قبول إصدار رفيق

This checklist separates reproducible repository evidence from the one step
that cannot be certified by source inspection: a real hosted Google Colab run.

تفصل هذه القائمة بين الأدلة القابلة للتكرار داخل المستودع والخطوة التي لا
يمكن اعتمادها من فحص الملفات وحده: تشغيل فعلي داخل Google Colab المستضاف.

## Automated evidence · الأدلة الآلية

Run from the repository root:

شغّل من جذر المستودع:

```bash
python scripts/preflight_readiness.py
python -m unittest discover -s tests/public -p "test_*.py" -v
python scripts/validate_notebook.py notebooks/Rafeeq_Mini_Capstone.ipynb
```

The preflight verifies the Python version, required files, published dataset
counts, the `C0–C29` notebook contract, all 14 learner tasks, the zero-cost
offline path, `LLM_MODE=stub`, and checkpoint write access. It reads no
credential values.

يتحقق الفحص من إصدار Python، والملفات المطلوبة، وأعداد البيانات المنشورة،
وعقد الدفتر `C0–C29`، والمهام الأربع عشرة، والمسار المجاني غير المتصل، ووضع
`LLM_MODE=stub`، وإمكانية حفظ نقاط التحقق. ولا يقرأ قيم بيانات الدخول.

## Manual hosted-Colab acceptance · قبول Colab اليدوي

Complete every item with a clean learner account before promoting a release
candidate to `v1.0.0`:

يجب إكمال جميع البنود بحساب متدرب تجريبي نظيف قبل ترقية الإصدار التجريبي إلى
`v1.0.0`:

- [ ] Open the pinned course notebook from a clean Google account.  
      فتح دفتر الدورة المثبت من حساب Google تجريبي نظيف.
- [ ] Run `C0` through `C29` using Colab Free CPU and `LLM_MODE=stub`.  
      تشغيل `C0` حتى `C29` باستخدام Colab Free CPU ووضع `stub`.
- [ ] Interrupt the runtime after the Day 1 gate and follow the recovery guide.  
      قطع الجلسة بعد بوابة اليوم الأول وتطبيق دليل الاستعادة.
- [ ] Confirm the Day 2 and Day 3 gates remain reproducible after recovery.  
      التأكد من قابلية إعادة بوابتي اليومين الثاني والثالث بعد الاستعادة.
- [ ] Export the final bundle and download the final notebook separately.  
      تصدير الحزمة النهائية وتنزيل الدفتر النهائي بصورة منفصلة.
- [ ] Upload both beside the learner's existing safe `LEARNING_PROGRESS.md` without losing `.github/`.
      رفعهما بجانب `LEARNING_PROGRESS.md` الآمن الموجود دون فقد مجلد `.github/`.
- [ ] Confirm **Actions → Learner submission quality** completes green.  
      التأكد من نجاح **Actions → Learner submission quality** بالعلامة الخضراء.
- [ ] Record elapsed time, browser, account type, failure, and recovery evidence.  
      تسجيل الزمن والمتصفح ونوع الحساب والخطأ ودليل الاستعادة.

## Release decision · قرار الإصدار

| Decision | Required evidence | القرار | الدليل المطلوب |
|---|---|---|---|
| Keep release candidate | Automated checks pass; manual pilot pending | إبقاء الإصدار تجريبيًا | نجاح الآلي وبقاء التجربة اليدوية |
| Promote to `v1.0.0` | Automated checks and every manual item pass | الترقية إلى `v1.0.0` | نجاح جميع البنود الآلية واليدوية |
| Stop delivery | A critical security gate, export, or Actions check fails | إيقاف التسليم | فشل بوابة أمنية أو التصدير أو Actions |

The instructor records the acceptance date and tested commit SHA in the private
instructor release checklist. Learners do not self-certify this release.

تسجل المدربة تاريخ القبول وبصمة الالتزام المختبر في قائمة الإصدار الخاصة.
ولا يعتمد المتدرب الإصدار بنفسه.
