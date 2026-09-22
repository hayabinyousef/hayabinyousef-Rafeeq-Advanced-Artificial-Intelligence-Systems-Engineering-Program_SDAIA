# Public schemas · المخططات العامة

| English | العربية |
|---|---:|
| These Draft 2020-12 JSON Schemas are learner-visible contracts. They define structure and safety boundaries without exposing private tests or reference solutions. | هذه مخططات JSON وفق المسودة 2020-12 ومتاحة للمتدرب. تحدد البنية وحدود الأمان دون كشف اختبارات خاصة أو حلول مرجعية. |

| Contract | Purpose · الغرض |
|---|---|
| `state.schema.json` | Trace-safe typed state; raw messages and tool observations are forbidden. · حالة محددة النوع وآمنة للتتبع؛ تُمنع الرسائل الخام ومشاهدات الأدوات. |
| `trace.schema.json` | Redacted spans, latency and bounded call counters. · مقاطع تتبع منقحة، وزمن الاستجابة، وعدادات الاستدعاء المحدودة. |
| `assessment.schema.json` | Public case results, metrics, critical gates and readiness. · نتائج الحالات العامة، والمقاييس، والبوابات الحرجة، والجاهزية. |
| `manifest.schema.json` | Export inventory, SHA-256 evidence and safety checks. · جرد التصدير، وأدلة SHA-256، وفحوص السلامة. |

The schemas permit documented extension fields, but their required fields and value types remain strict. `redacted` is always `true`, `llm_mode` is always `stub`, and `mcp_transport` is always `stdio` in the mandatory path.

تسمح المخططات بحقول توسعة موثقة، مع بقاء الحقول الإلزامية وأنواع القيم صارمة. تكون `redacted` دائمًا `true`، ويظل `llm_mode` مساويًا لـ`stub`، ويظل نقل MCP مساويًا لـ`stdio` في المسار الإلزامي.
