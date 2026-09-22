# Rafeeq public synthetic data · بيانات رفيق الاصطناعية العامة

**Dataset release: `2026.09` · Fixture seed: `RAFEEQ-PUBLIC-2026-09-V1` · حالة الحزمة: جاهزة للمسار التدريبي العام**

| English | العربية |
|---|---|
| This folder contains the small, deterministic dataset used by the three-day Rafeeq mini-capstone. Every person, customer, order, memory, message, and policy is fictional. | يحتوي هذا المجلد على حزمة البيانات الصغيرة والحتمية المستخدمة في مشروع «رفيق» المصغر خلال الأيام الثلاثة. جميع العملاء والطلبات والذكريات والرسائل والسياسات افتراضية بالكامل. |
| The data is designed for Google Colab Free on CPU. It needs no download, API key, database, or paid service. | صُممت البيانات للعمل على Google Colab المجاني باستخدام المعالج فقط، ولا تحتاج إلى تنزيل خارجي أو مفتاح API أو قاعدة بيانات أو خدمة مدفوعة. |
| Expected outcomes in the public development and evaluation files are learning oracles for self-checking. They are not hidden assessment answers. | النتائج المتوقعة في ملفات التطوير والتقييم العامة مرجع تعلم للتحقق الذاتي، وليست إجابات التقييم الخفي. |

## Package contents · محتويات الحزمة

| File | Records | Training purpose · الغرض التدريبي |
|---|---:|---|
| `orders.csv` | 24 | Trusted local order facts for ownership, status, refund eligibility, amount gating, and duplicate prevention · حقائق طلبات محلية موثوقة لفحص الملكية والحالة والأهلية وحد المبلغ ومنع التكرار |
| `policy_chunks.jsonl` | 6 | Active bilingual policy retrieval plus one obsolete version represented in Arabic and English · استرجاع السياسة السارية ثنائية اللغة مع نسخة قديمة ممثلة بالعربية والإنجليزية |
| `memory_seed.jsonl` | 8 | Customer-scoped recall, expiry, inactive-memory filtering, and a cross-customer similarity trap · ذاكرة مقيدة بالعميل مع اختبار الانتهاء وعدم النشاط وتشابه عابر للعملاء |
| `tickets_dev.jsonl` | 16 | Development cases for routing and deterministic outcome checks; 8 Arabic and 8 English · حالات تطوير للتوجيه وفحص النتائج الحتمية؛ 8 بالعربية و8 بالإنجليزية |
| `eval_public.jsonl` | 8 | Public functional evaluation; 4 Arabic and 4 English · تقييم وظيفي عام؛ 4 بالعربية و4 بالإنجليزية |
| `security_cases.jsonl` | 8 | Public adversarial fixtures; 4 Arabic and 4 English · حالات عدائية عامة؛ 4 بالعربية و4 بالإنجليزية |

Field definitions, enums, and record-level constraints are documented in [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

تعريفات الحقول والقيم المسموحة والقيود موثقة في ملف [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

## Fixed lab rules · قواعد اللاب الثابتة

- Reference time for expiry checks: `2026-09-17T00:00:00Z`.
- Refund eligibility is computed in code: the order belongs to the trusted runtime customer, `delay_days > 2`, and `already_refunded = false`.
- Eligible amounts `<= 500.00` SAR may create one simulated refund request; amounts `> 500.00` SAR require documented human approval.
- Ownership mismatch is blocked. A previous refund is rejected. The write tool is never automatically retried.
- Memory is filtered by trusted `customer_id`, `active`, and `expires_at` before similarity ranking.
- Policy is filtered by `locale`, `category`, `active`, and version before ranking.

- الزمن المرجعي لفحص انتهاء الذاكرة هو `2026-09-17T00:00:00Z`.
- تُحسب أهلية الاسترداد في الكود: ملكية الطلب للعميل الموثوق من بيئة التشغيل، و`delay_days > 2`، وعدم وجود استرداد سابق.
- المبلغ المؤهل حتى `500.00` ريال يسمح بطلب استرداد محاكى واحد، وما زاد على ذلك يتطلب موافقة بشرية موثقة.
- تُحجب محاولة الوصول إلى طلب عميل آخر، ويُرفض الطلب المسترد سابقًا، ولا تُعاد محاولة أداة الكتابة تلقائيًا.
- تُرشح الذاكرة بحسب `customer_id` الموثوق و`active` و`expires_at` قبل ترتيب التشابه.
- تُرشح السياسة بحسب `locale` و`category` و`active` والإصدار قبل ترتيب التشابه.

## Minimal validation · التحقق السريع

Run from the repository root in Colab or locally:

```bash
python - <<'PY'
import csv, json
from pathlib import Path

root = Path("data/public")
with (root / "orders.csv").open(encoding="utf-8", newline="") as fh:
    assert len(list(csv.DictReader(fh))) == 24

for name, expected in {
    "policy_chunks.jsonl": 6,
    "memory_seed.jsonl": 8,
    "tickets_dev.jsonl": 16,
    "eval_public.jsonl": 8,
    "security_cases.jsonl": 8,
}.items():
    rows = [json.loads(line) for line in (root / name).read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == expected, (name, len(rows))

print("Public dataset validation: PASS")
PY
```

## Safety boundary · حدود السلامة

Do not add real names, identity numbers, phone numbers, email addresses, physical addresses, precise locations, payments, support conversations, trainee records, access tokens, or production traces. Hidden evaluation and instructor-only security cases must remain outside every learner repository, branch, tag, release, and Git history.

يُمنع إضافة أسماء أو أرقام هوية أو هواتف أو بريد إلكتروني أو عناوين أو مواقع دقيقة أو مدفوعات أو محادثات دعم أو سجلات متدربين أو رموز وصول أو آثار تشغيل حقيقية. تبقى حالات التقييم الخفي واختبارات المدرب الأمنية خارج مستودعات المتدربين وفروعها ووسومها وإصداراتها وسجل Git بالكامل.
