# Detailed build contracts

This is the original design contract. A key-free subset is now implemented; consult the current CLI help and [user documentation](../../site/index.md) for actual options, supported semantics and remaining limitations. Reference JSON files in this pack remain design examples; `fail2test schema` exposes the runtime-generated contract.

## CLI

| Command | Inputs | Outputs / guarantees |
|---|---|---|
| `fail2test init` | Local directory; optional supported example | Writes config/scaffold only; no runner import, install, network, or overwrite by default |
| `fail2test import TRACE --format json --out CASE` | Explicit source and destination | Validated sanitized draft plus import-loss report; no code import |
| `fail2test inspect CASE --json` | Case directory or case JSON | Metadata, rules, capability needs, sensitivity warnings; never executes user code |
| `fail2test propose CASE --out PROPOSAL` | Draft plus selected behavior | Deterministic candidate rules; optional AI route implemented after the key-free proof and before the complete initial public release |
| `fail2test review CASE --rules RULES --reviewer LABEL` | Reviewed rules and fixture changes | Binds exact digest and reviewer label; supports terminal interaction or explicit noninteractive values |
| `fail2test validate CASE --runner NAME` | Approved case and trusted local runner | Fresh baseline execution; success means selected failure reproduced, not application correctness |
| `fail2test reduce CASE --runner NAME --max-runs N` | Validated case, same runner revision | New candidate case with lineage; changed artifact requires renewed review/validation |
| `fail2test export CASE --runner NAME --format pytest --out DIR` | Approved and validated exportable case | Fixed pytest template, fixture, README metadata; overwrite requires `--overwrite` |
| `fail2test run CASE --runner NAME --json` | Approved case, current local code | PASS only for complete execution satisfying rules |
| `fail2test doctor` | Local runtime/config | Capability and version report; no secret values, package installation, or provider probe by default |

Common options: `--config PATH`, `--json`, `--quiet`, `--debug` with redacted output, `--overwrite` on supported writers. No arbitrary `--eval`, template expressions, inline Python, automatic dependency install, or remote code URL. Explicit execution commands import configured application code; inspect/import/export do not.

## Exit behavior

| Code | Meaning |
|---|---|
| 0 | Command completed its stated goal; for `run`, complete execution with all rules satisfied |
| 1 | Behavioral check did not meet the command goal: regression rule failed in `run`, or expected baseline failure was not reproduced in `validate` |
| 2 | Invalid command/config/schema, unapproved artifact, or invalid lifecycle transition |
| 3 | Unsupported or incomplete execution, unmatched interaction, missing runner capabilities, timeout |
| 4 | Internal/tooling or filesystem failure |

`validate` can return 0 while recording a reproduced failing rule. This command-specific distinction must appear in help, result JSON, and the quickstart. Exported pytest tests use pytest's own exit codes; they raise assertion failures for behavioral failures and explicit errors for incomplete execution. They never translate an incomplete result into a skip/pass.

## Local configuration

```toml
# Proposed fail2test.toml; trusted local code configuration, not portable case content.
[project]
case_dir = "tests/fail2test_cases"

[runners.refund]
callable = "my_app.fail2test_runner:run"
capabilities = ["sync", "serial", "json", "injected_model", "injected_tools"]
timeout_seconds = 10

[privacy]
deny_paths = ["/metadata/authorization", "/metadata/api_key"]
export_requires_review = true

[execution]
default_mode = "fixture"
max_runs = 50
total_timeout_seconds = 120
```

Runner names are resolved only from this local configuration. A case must not supply a Python import path, shell command, pickled object, or plugin package. Explicitly running application code is a trust decision equivalent to running that repository's tests. A local configuration is not a sandbox.

## Python interface

```python
# Proposed interface sketch, not implementation.
from fail2test import Case, RunContext, RunResult


def run(input: dict, context: RunContext) -> dict:
    agent = build_agent(model=context.model, tools=context.tools)
    return agent.invoke(input)


case = Case.load("tests/fail2test_cases/duplicate-refund/case.json")
result: RunResult = case.run(runner="refund")
result.assert_passed()  # Asserts behavior; raises a distinct error if execution was incomplete.
```

`RunContext.model.complete(slot, request)` supplies one ordered model response after request matching. `RunContext.tools.call(name, arguments)` dispatches approved mock rules and records invocation/result. Methods are synchronous in v0.1. Concrete LangGraph helpers adapt the supported model/tool interfaces; they do not patch arbitrary clients globally.

The runner returns a JSON-compatible value. Exceptions are mapped to a redacted structured error; an application crash is not automatically the selected regression behavior. A future explicit exception rule must have its own reviewed contract.

## Case format

See [reference schema](../reference/case.schema.json) and [duplicate-refund example](../reference/duplicate-refund.case.json). The schema covers the five proposed alpha rule shapes. Domain invariants and execution semantics require the additional checks below; structural schema validity does not establish reproduction.

| Field | Contract |
|---|---|
| `schema_version` | Exact supported format version, initially `0.1`; independent of package version |
| `case_id` | Stable nonsecret identifier; revision identity comes from digest |
| `title` | Human-readable description; escaped in reports/templates |
| `mode` | `fixture` for the executable alpha case; trace-only evidence lives in import metadata |
| `input` | JSON input; no executable values or environment substitution |
| `model_fixtures` | Stable slot, ordinal, exact canonical-JSON request, response; no matching fallback |
| `tool_fixtures` | Unique fixture ID, tool name, exact JSON arguments, response, explicit repeatability |
| `rules` | Closed typed DSL, stable rule IDs, evidence/requirement notes |
| `provenance` | Source kind/reference, redaction status, requirement reference; no authority inferred from strings |

Runtime-created `manifest.json` carries case digest, package/adapter version, source completeness, capabilities, fixture inventory, approval and validation records. Avoid self-referential hashes: hash the canonical case and referenced payloads; hash each result independently. Manifest identity and execution records are separate.

For the inline alpha case use `sha256(JCS(case))` with RFC 8785 JSON Canonicalization Scheme. Enforce its interoperable JSON constraints: unique keys, valid Unicode, finite numbers, integers within the exactly interoperable range where numeric identity matters. Monetary high-precision values should use explicit integer minor units within range or strings plus a future explicit decimal contract. Do not approximate JCS with an untested `json.dumps(sort_keys=True)`. A tested conforming canonicalizer and published conformance vectors are a P0 task. Request matching uses JSON-type-aware semantic equality: object key order is irrelevant; array order matters; booleans and strings are distinct from numbers. JCS-equivalent numeric representations must not produce contradictory matching/digest identities.

## Source trace contract

The first importer accepts the neutral [source trace schema](../reference/trace.schema.json), not arbitrary vendor JSON. `trace_schema_version=0.1`, `trace_id`, `input`, `events` and declared `completeness` are required. Each event has a unique ID, sequential position, kind, operation ID and JSON payload. Model/tool request/result pairs are linked by operation ID; optional parent IDs describe observed nesting, not inferred causality. No internal hidden model reasoning is required or claimed captured.

Supported event kinds are `model_request`, `model_result`, `tool_request`, `tool_result`, and `run_output`. A model request payload contains slot/ordinal/request; a tool request contains tool/arguments. Result payloads are data, and each request/result pairing is validated. Duplicate IDs/sequence positions, missing result, incompatible nesting or unsupported control flow are reported. Normalization does not invent missing events or mark vendor-supplied completeness trusted without pairing/capability checks. An evidence trace can be partial and still useful for inspection; it is not automatically an executable case.

Import produces a mapping/loss report: original source IDs to normalized events, supported/unsupported fields, missing initial state, missing model/tool responses, sanitization changes and required runner capabilities. Tool repeatability is a reviewed test-fixture choice, never silently inferred as permission to repeat a real action. A source trace's timestamps and claimed failure label do not establish intended behavior.

Initial model fixtures are reconstructed only from complete supported serial interactions. Cases requiring hidden state, credentials, nondeterministic local values or external writes that cannot be represented remain `trace_only` until explicit fixtures/runner setup are supplied. Future Langfuse/OTel importers must implement their own loss map; accepting an OTel envelope is not proof of complete agent reproduction.

## Rule specification

All predicates use JSON-compatible typed values. No coercion between strings and numbers; booleans are not accepted as numeric bounds. Missing fields are failures for a rule requiring that field, with an explicit diagnostic. JSON pointer syntax follows RFC 6901. NaN and infinity are rejected. Bounds declare inclusive/exclusive behavior explicitly.

| Kind | Required parameters | Evaluation |
|---|---|---|
| `tool_call_count` | `tool`, `group_by` pointer list, `max_calls`; optional `min_calls` | Group observed transport calls using typed values; each group within bounds; min/max apply per group, and an explicit `require_any` handles zero-call cases |
| `tool_argument` | `tool`, `pointer`, `operator`, typed `expected`, `require_any` | All matched observed calls satisfy typed predicate; missing observations fail if `require_any` |
| `forbidden_tool` | `tool` | No observed transport call matches the named tool |
| `output` | `pointer`, `operator`, typed `expected` | Evaluate returned JSON output |
| `max_tool_calls` | `max_calls` | Total instrumented tool invocations do not exceed the limit |

Supported operators: `eq`, `in`, `lte`, `gte`. A no-duplicate count alone may pass if the agent does nothing; pair it with an output/required-action rule whenever business behavior requires an action. The reference slice uses `min_calls=1`, `max_calls=1`, `require_any=true` for the relevant tool group.

## Matching semantics

- JSON objects are compared independent of key order; arrays retain order; values retain types.
- Requests contain only the model inputs needed for the controlled call; no API keys, headers, or provider client objects.
- Model matching is strict by `(slot, ordinal, request)`. A changed prompt or order produces `UNMATCHED_MODEL_REQUEST`.
- Tool matching is strict by tool name and exact argument JSON. Multiple matching fixtures are a schema/validation error; no first-match ambiguity.
- A repeatable tool fixture serves the same response repeatedly and records every call; nonrepeatable fixtures may be consumed once.
- Unknown calls fail closed at the test transport. They never fall through to a live client.
- Tool fixtures left unused are diagnostics by default; unnecessary mandatory model fixture calls are a completeness error under the declared sequence.
- Argument redaction can alter matching or branch behavior. Mark affected cases as needing synthetic replacement and revalidation rather than claiming equivalent reproduction.

## Lifecycle

```text
imported draft -> reviewed -> baseline validated -> exported
                          \-> baseline not reproduced
validated -> reduction candidate -> reviewed -> baseline validated -> exported
exported -> regression run -> pass / behavioral failure / incomplete / error
```

Review and validation are independent records bound to an exact digest. Any case/rule/fixture edit invalidates those records. Changing the application's runner code does not invalidate the case's approved rule; it creates a new execution record. A historical baseline validation remains historical and cannot certify current compatibility.

Approval is a workflow acknowledgement, not protection against a malicious repository owner editing both artifacts and manifests. Future hosted verified approvals require authenticated identities and immutable audit records.

## Result contract

`RunResult` fields: `result_schema_version`, `case_id`, `case_digest`, `mode`, `execution_status` (`complete`, `incomplete`, `error`), `outcome` (`pass`, `fail`, `not_evaluated`), `rule_results`, `observed_calls`, `unmatched_interactions`, `unused_fixtures`, `runner_identity`, `environment`, `duration_ms`, `tooling_errors`, and `sensitivity_summary`.

Allowed status pairs: complete/pass, complete/fail, incomplete/not_evaluated, error/not_evaluated. Do not let a false boolean collapse all states. Rule results include stable rule ID, observed value, expected condition, and observation references. Logs omit raw bodies by default. JSON errors are machine-readable and distinguish user configuration from application execution and Fail2Test defects.

## Limits, retries, cancellation and idempotency

Proposed conservative defaults: 10 MiB input JSON, 10,000 source events, 1 MiB individual payload, JSON nesting depth 64, 10 seconds per fixture execution, 50 candidate executions, 120 seconds total reduction. They are configurable within documented limits and must be validated against actual fixtures before stable release.

No automatic retry of a completed application action. A fixture execution timeout ends that attempt; reduction can move to another candidate only when its budget permits. Cancellation stops new work, terminates the managed child/process group where supported, preserves a redacted partial report, and cleans task-owned temporary files. Do not delete user source data. Writes use temporary sibling files and atomic replace where available; no overwrite by default.

## Compatibility and migration

Unknown schema major versions are rejected. Unknown executable fields are rejected. Namespaced non-executable annotations may be preserved in a future explicit `extensions` field; they never silently alter behavior. No implicit downgrade or online schema fetch. Migration is an explicit command writing a new case version, retaining original input and marking changed approvals invalid. Package deprecations require documentation, warnings and a published removal version.

Sources: [RFC 6901 JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901), [pytest plugin interface](https://docs.pytest.org/en/stable/how-to/writing_plugins.html).
