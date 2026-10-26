# Reference contracts

These files make the planned case format concrete. They are **design fixtures**, not validated product runs or claims that Fail2Test is implemented.

- `case.schema.json`: draft 2020-12 JSON Schema for the five proposed alpha rule kinds and strict data-only fixture shape.
- `trace.schema.json`: neutral historical-evidence envelope; request/result pairing and capability validation remain runtime responsibilities.
- `duplicate-refund.case.json`: one scripted model response containing two identical intended actions; a repeatable tool fixture lets the broken runner's two transport calls be observed. A corrected runner deduplicates before dispatch. The rule requires at least one call and permits at most one per order.

The broken/fixed runners are specified in the plan and will be implemented during P0. The reference case has no fabricated approval or validation record. It is not yet eligible for a release claim or an exported passing test.

Schema validation covers structural consistency. Runtime checks must additionally validate pointer syntax, duplicate fixture matches, ordering, min/max relationships, approval digests, capability coverage and actual fresh execution. Source JSON parsing must reject duplicate object keys rather than silently discarding them.
