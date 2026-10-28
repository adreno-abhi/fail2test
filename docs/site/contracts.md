# Contracts, privacy and limitations

## Modes

- Historical evidence is data, not a current-code regression.
- Fixture mode runs current application code against explicit recorded dependencies.
- Live-model evaluation is not implemented and must not be inferred from a passing fixture test.

## Rules

Supported rule kinds: `tool_call_count`, `tool_argument`, `forbidden_tool`, `output`, and `max_tool_calls`. Predicates use typed JSON equality/membership and numeric bounds. No executable expressions or arbitrary generated Python assertions are accepted. `require_any` prevents a required-action rule from accepting a no-op. Missing fields do not equal JSON null.

Case-wide constraints include unique IDs within each fixture/rule collection, unique model
slot/ordinal pairs with ordinals contiguous from zero per slot, and unambiguous tool/name/
argument fixture matches. Rule bounds must be ordered, grouping pointers unique and JSON
pointers well formed. Object-level diagnostics may identify only the affected rule or case;
check these constraints when no individual field is singled out.

Use `fail2test schema` for the generated runtime JSON Schema. See the planning contracts for detailed design, but consult current CLI help for implemented options. Some planned features/flags remain unimplemented; the development status records gaps.

## Review and reproduction

Review binds exact case content through an RFC 8785 canonical SHA-256 digest. Any rule/fixture/input change invalidates prior review/validation. A baseline record means the selected rule failed in a complete supported execution; it is not a signature, verified provenance or certification of future results. A local owner can edit both manifests and cases; this is a workflow aid, not a security boundary against that owner.

Run results distinguish complete/pass, complete/fail, incomplete/not_evaluated and error/not_evaluated. CLI `run` returns 0/1/3 respectively for pass, behavior failure and incomplete/error. Invalid data/configuration uses 2. `validate` returns 0 for successfully reproducing the selected failure. pytest exports use pytest's native exit codes and explicit execution errors.

## Data and security

Import sanitizes known sensitive keys and token patterns before writing new evidence. Review the actual artifacts: detection is best effort, and replacing a routing value can change behavior. Original source files remain untouched. Reports suppress raw exception messages and application stdout/stderr. Default paths perform no provider calls or telemetry.

Reportable case-validation errors include only schema-owned field names, list positions and
fixed explanations, capped at five issues. Traversal stops before arbitrary dictionary keys
and unknown properties; error values, validator messages/context and raw validation causes
are not included. Whole-object constraints may identify only the enclosing object. Error
codes/exit statuses are unchanged. This formatting applies at the CLI/file/import/review/UI
boundaries; direct Pydantic `Case.model_validate` exceptions retain the standard API and
can contain raw inputs. These messages do not certify that the evidence itself is sanitized.

Optional [AI suggestions](ai-suggestions.md) require a trusted profile, exact payload preview
and explicit send authorization. Only sanitized previewed fields and intended behavior are
sent. The response must match declarative Rule/Case contracts and remains unapproved.
Credentials stay on the server/CLI. Failures never trigger a paid fallback or local model download.

Application code, pytest plugins and local runner configuration are executable and trusted. They may perform operations outside the injected transport. Timeouts and process termination are operational controls, not proof of OS/network isolation. Do not run hostile repositories or cases using privileged environments.

Unknown/missing model or tool interactions never fall through to a real client. Fixture errors stay latched even if application code swallows them. Async, streaming/batched model calls, and overlapping transport calls produce explicit incomplete results. Native graph execution enforces `max_concurrency=1` and permits controlled thread handoff inside that serialized scope; ordinary cross-thread calls outside it remain unsupported.

Native chat request format `langchain-chat.v1` includes semantic text messages, tool-call IDs, tools, stop/tool-choice settings and supplied JSON options. Generated framework message IDs, usage and response metadata are excluded explicitly. Unknown extra message fields and provider-specific content in `additional_kwargs` are rejected. Tool fixtures match arguments passed by native schema validation; the wrapper does not execute the original function to expand its internal behavior. Schema validators, application callbacks and other application code remain trusted executable code.

## Current limits

JSON input: 10 MiB and depth 64. Neutral traces: at most 10,000 events, payloads at most 1 MiB, serial request/result pairs. Identical tool requests with different responses need an unsupported sequence-aware adapter. Reduction currently removes inputs only, rechecks the selected failure and requires renewed review. Source hashes identify the configured runner module, not its full dependency closure. See the [verified compatibility matrix and its limits](compatibility.md) for platform/version evidence.
