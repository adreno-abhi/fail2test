# Native LangGraph integration verification

Completed 26 October 2026 under the project owner's explicit approval for native model/tool adapters, a realistic example, documentation and tests. No next feature or external publication is authorized by this record.

## Delivered

- `FixtureChatModel`: native synchronous `BaseChatModel` invocation/tool binding backed by strict recorded fixtures, with SDK caching disabled.
- `fixture_tool`: preserves an ordinary tool's schema/name and replaces its body with fixture dispatch; schema errors and unsupported paths latch incomplete execution.
- `chat_request`/`chat_response`: versioned native fixture normalization preserving semantic messages, tool-call IDs, schemas and supplied options while excluding documented generated metadata.
- `graph_runner`: serialized scheduling, controlled worker-thread handoff and JSON serialization of supported native message state. Overlapping transport access remains rejected.
- A `MessagesState`/`ToolNode` refund application whose graph construction does not import Fail2Test. Its test runner injects native model/tool replacements. The original payment body deliberately raises if invoked.
- Deterministic structured tool-response ordering, including a tested two-turn chat that consumes a tool result.

## Verification results

| Check | Actual result |
|---|---|
| Full pytest suite with subprocess coverage | **120 passed**, 88% combined statement/branch coverage |
| Targeted adapter/example tests | 35 passed |
| Ruff lint and formatting | PASS, 70 files formatted |
| mypy | PASS, 17 source files |
| Strict MkDocs build | PASS |
| Dependency lock check | PASS |
| Wheel and source distribution build | PASS |
| Fresh core-wheel workflow without optional framework installed | PASS |
| Fresh source-distribution installation | PASS |
| Fresh native LangGraph workflow with optional dependencies | PASS |

Tested environment: Windows, CPython 3.13.5, langchain-core 1.7.0 and LangGraph 1.2.17. Other platform/version combinations remain outside this evidence.

The package smoke test uses cached dependencies for the core check and lock-constrained versions for the optional SDK installation. Package downloads are allowed for that installation; no model-provider or real payment calls occur in the application checks. Its initial cache-only SDK attempt failed because a dependency was not cached; the corrected setup passed using the declared locked versions.

The suite covers duplicate dispatch detection, strict prompt/options matching, no original tool-body execution, invalid response/schema handling, swallowed exceptions, cache bypass prevention, unsupported async/stream/batch paths, serialized thread handoff, overlap rejection and generated pytest execution.

## Local verified artifacts

- Wheel SHA-256: `98d4f45e1941d31c708c3427fbe8d7fb3a7bc7f7568de2b5ffaa45a1918ed58e`
- Source distribution SHA-256: `76b8b6e5a35081dd68de7be8f653650d3b7c5c0ba840be040f11185fdf8b94b5`

These are local development artifacts built before this report was added. They are not signed public releases. Rebuild against the eventual reviewed release commit before publishing.

## Limits and next-step status

Support is scoped to synchronous text chat, ordinary schema-backed tools, serialized graph execution and supported JSON/message state. Multimodal/provider-specific message extras, runtime-injected tool schemas, artifacts, checkpoint restore and live-model evaluation are not part of this step. Application code, callbacks and schema validators remain trusted; the adapters are not an OS/network sandbox.

Human first-use usability targets have not been established by a scripted example. Model-assisted suggestions and broader compatibility/release work remain future steps. Wait for owner approval before starting the proposed next step.
