# Prepare your own evidence

Import accepts two JSON formats: a complete Fail2Test case v0.1, or a neutral trace v0.1.
It does not read arbitrary application logs, screenshots, ZIPs, LangSmith exports or
OpenTelemetry exports directly. There is no automatic recorder or incident-to-case converter.

Try `fail2test init demo` first for a ready-made synthetic case. To inspect the current
case contract, run `fail2test schema --out case-schema.json`; this generates the runtime
schema, not a recording. Native LangGraph request/response normalization uses the helpers
described in [integration](integration.md#native-fixture-format).

## Collect the necessary information

Work from a small synthetic or carefully scrubbed failure. You need the application input,
each model request and response in order, and each tool name, arguments and response.
You also need a runner that uses these same dependency boundaries. Record explicit JSON
values; Fail2Test cannot reconstruct missing messages, hidden state or side effects.

The neutral format requires serial request/result pairs and zero-based contiguous event
positions. Matching is strict. A changed request needs deliberate fixture updates and renewed
review. Identical tool requests with different results are not supported by this importer.
Do not declare evidence complete merely to make validation available.

## A complete neutral trace

Save this synthetic read-only-agent failure as `read-only-trace.json`. The recorded plan
requests a deletion; the recorded response is data and never deletes anything itself.

```json
{
  "trace_schema_version": "0.1",
  "trace_id": "synthetic-read-only-failure",
  "input": {"task": "summarize document-demo"},
  "completeness": "declared_complete",
  "events": [
    {
      "event_id": "plan-request", "sequence": 0,
      "kind": "model_request", "operation_id": "plan",
      "payload": {"slot": "planner", "ordinal": 0,
        "request": {"task": "summarize document-demo"}}
    },
    {
      "event_id": "plan-result", "sequence": 1,
      "kind": "model_result", "operation_id": "plan",
      "payload": {"tool": "delete_document",
        "arguments": {"document_id": "document-demo"}}
    },
    {
      "event_id": "delete-request", "sequence": 2,
      "kind": "tool_request", "operation_id": "delete",
      "payload": {"tool": "delete_document",
        "arguments": {"document_id": "document-demo"}}
    },
    {
      "event_id": "delete-result", "sequence": 3,
      "kind": "tool_result", "operation_id": "delete",
      "payload": "synthetic deletion result"
    }
  ]
}
```

The first pair becomes a model fixture matched by slot, ordinal and request. The second
becomes a tool fixture matched by name and arguments. A trace imports as an unapproved
draft with no business rules. Save this separately as `read-only-rules.json`:

```json
{
  "rules": [{
    "id": "read-only", "kind": "forbidden_tool", "tool": "delete_document",
    "requirement": "This read-only agent must not dispatch deletion."
  }]
}
```

```text
fail2test import read-only-trace.json --out read-only-case
fail2test inspect read-only-case --json
fail2test review read-only-case --rules read-only-rules.json --reviewer local-owner --rule read-only
```

Review the saved fixtures and requirement before running `review`. It acknowledges the
exact content; its reviewer label is not an authenticated signature. Import and review do
not run your application.

## Connect the application and prove the fix

For this example, the runner shape in [integration](integration.md) makes the `planner`
request and dispatches the returned tool through `context.tools.call`. Register your
runner as `application` in `fail2test.toml`. Use trusted synthetic code, not a live deletion
implementation. Fixture controls do not prevent arbitrary I/O elsewhere in application code.

```text
fail2test validate read-only-case --runner application --config fail2test.toml
fail2test run read-only-case --runner application --config fail2test.toml
```

Before the fix, `validate` should exit 0 because it reproduced the selected forbidden-tool
failure. `run` should show `complete: fail` and exit 1. Fix the application to reject deletion
in this read-only scenario, then rerun the same runner and expect `complete: pass`:

```text
fail2test run read-only-case --runner application --config fail2test.toml
fail2test export read-only-case --runner application --config fail2test.toml --out tests/read_only
python -m pytest tests/read_only/test_regression.py -q
```

Expected pytest result: `1 passed`. Keep the test, case and manifest together, with the
application runner and configuration available. Choose new output names for another trial.
If a full current-code run cannot reproduce the selected failure, investigate the missing
state or wrong requirement; do not invent responses or weaken the rule to export a test.

## Troubleshooting preparation

| Result | Check next |
|---|---|
| `UNSUPPORTED_FORMAT` | Use a case v0.1 or the neutral trace above; a vendor export needs conversion |
| `INVALID_CASE` | Compare with `fail2test schema`; check required fields, rule kind, strict value types and extra fields |
| `INVALID_TRACE_ORDER` / `INVALID_TRACE_PAIR` | Check event positions, unique IDs and serial operation pairing |
| Trace-only / incomplete source | Obtain the missing evidence; do not relabel partial data as complete |
| `RUNNER_IMPORT_FAILED` | Check module/function, application installation and the config location |
| `REVIEW_REQUIRED` | Inspect edits and acknowledge the new exact case before running |
| Incomplete fixture run | Compare recorded slot/ordinal/request or tool/arguments; inspect the execution error code |

Case validation errors identify schema-defined fields without printing their values. For
example, a forbidden-tool rule missing its requirement reports:

```text
INVALID_CASE: case.rules[0].requirement: Required field is missing. Compare with the case schema using fail2test schema.
```

`case.rules[0]` means the first rule. Diagnostics show at most five issues and indicate when
additional errors are omitted. Unknown property names and keys inside arbitrary input,
request, response or argument data are withheld: the location stops at the nearest known
schema field. An unknown property in a fixture is reported at that fixture, not by its name.
Object-wide constraints can report only the enclosing object; consult the schema and
[contracts](contracts.md) for uniqueness, fixture ordering and rule constraints.

CLI import/load/review, normalized trace-fixture checks, AI preview and browser edits use
these safe diagnostics, with their existing error codes. Invalid imports create no bundle;
rejected edits preserve the saved case, review and baseline. Direct `Case.model_validate`
retains Pydantic's normal exception API, which can contain input data; use the file/import
workflow for reportable errors rather than sharing raw validator exceptions.

Schema comparison is not an automatic repair tool. Import sanitization is best effort.
Review artifacts before sharing; never upload live secrets.
