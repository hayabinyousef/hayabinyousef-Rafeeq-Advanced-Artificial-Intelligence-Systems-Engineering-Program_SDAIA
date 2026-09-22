# Lab scope versus production · نطاق المختبر مقارنة بالإنتاج

Rafeeq is a guided engineering lab that teaches production design decisions
without requiring paid infrastructure. The mandatory path is intentionally
small, deterministic, and safe for Colab Free CPU.

رفيق مختبر هندسي موجّه يدرّب على قرارات التصميم الإنتاجية دون اشتراط بنية
تحتية مدفوعة. وقد صُمم المسار الإلزامي ليكون صغيرًا وحتميًا وآمنًا على
Colab Free CPU.

| Lab implementation | Production counterpart | تنفيذ المختبر | المقابل الإنتاجي |
|---|---|---|---|
| `LLM_MODE=stub` deterministic decisions | Governed live LLM with evaluation, fallback, and budget controls | قرارات حتمية بوضع `stub` | نموذج حي محكوم بالتقييم والبدائل والميزانية |
| TF-IDF/cosine retrieval over six policy chunks | Managed vector index with ingestion, freshness, access control, and reranking | استرجاع TF-IDF/Cosine فوق ستة مقاطع | فهرس متجهي مُدار مع تحديث وصلاحيات وإعادة ترتيب |
| Local MCP over `stdio` with three narrow tools | Authenticated, observable MCP service with network policy and service ownership | MCP محلي عبر `stdio` وثلاث أدوات ضيقة | خدمة MCP موثقة ومراقبة ومملوكة تشغيليًا |
| Synthetic orders, memory, tickets, and attacks | Classified enterprise data with retention, lineage, consent, and privacy controls | بيانات طلبات وذاكرة وتذاكر وهجمات اصطناعية | بيانات مؤسسية مصنفة بضوابط احتفاظ ونسب وموافقة وخصوصية |
| Tool-call count and elapsed time as cost proxies | Token, model, infrastructure, and human-review cost accounting | عدد الاستدعاءات والزمن كمؤشرين تقريبيين | محاسبة تكلفة الرموز والنموذج والبنية والمراجعة البشرية |
| Local JSON traces with redaction | Central telemetry, alerting, retention, incident response, and audit integration | آثار JSON محلية ومنقحة | قياس مركزي وتنبيه واحتفاظ واستجابة للحوادث وتدقيق |
| GitHub learner bundle and green CI | Versioned deployment pipeline, environments, approvals, rollback, and SLOs | حزمة متدرب وCI أخضر | خط نشر بإصدارات وبيئات وموافقات وتراجع ومؤشرات خدمة |

## What completion proves · ما الذي يثبته الإكمال

Completion demonstrates that the learner can connect architecture, state,
tools, memory, orchestration, approval, guardrails, testing, tracing, and safe
export in one bounded workflow. It does not claim that the learner deployed a
live enterprise service or operated a paid model.

يثبت الإكمال قدرة المتدرب على ربط المعمارية والحالة والأدوات والذاكرة
والتنسيق والموافقة والحواجز والاختبار والتتبع والتصدير الآمن في تدفق محدود.
ولا يعني نشر خدمة مؤسسية حية أو تشغيل نموذج مدفوع.

## Core and stretch · المسار الأساسي ومسار التميز

- **Core / الأساسي:** `C0–C29`, all 14 learner tasks, the three day gates,
  required reports, final export, and green GitHub Actions. This is the only
  graded path.
- **Stretch / التميز:** optional instructor-provided variants such as a new
  route, a boundary test, or a retrieval comparison. Stretch work never
  compensates for a failed core or security gate.

- **الأساسي:** الخلايا `C0–C29` والمهام الأربع عشرة وبوابات الأيام والتقارير
  المطلوبة والتصدير النهائي ونجاح GitHub Actions. وهو المسار الوحيد المقيم.
- **التميز:** امتدادات اختيارية توفرها المدربة، مثل مسار جديد أو اختبار حدّي
  أو مقارنة استرجاع. ولا يعوض مسار التميز فشل المسار الأساسي أو بوابة أمنية.
