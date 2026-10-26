# Product charter and scope

## Problem and initial audience

Agent failures are frequently visible in traces but costly to convert into durable tests. The developer must determine relevant inputs, restore dependencies, define intended behavior, and establish that a proposed correction addresses the failure. Fail2Test owns this conversion workflow. It complements trace/evaluation platforms through imports and exports.

Initial users are Python AI engineers operating tool-using agents in a repository they control. They can edit an entry point and inject dependencies. They have at least one observed failure and can state a behavioral requirement. Maintainers and reviewers are secondary users. The initial commercial buyer is an engineering lead responsible for reliability, not a hobbyist collecting traces.

Do not initially target arbitrary agent runtimes, historical logs with no executable target, compliance certification, autonomous root-cause repair, or end-user chat applications.

## The promise

> Given supported failure evidence, an explicit application runner, and a reviewed behavior rule, produce a portable test case and pytest test that exercise application code with controlled dependencies.

The claim is conditional on supported execution and fixture coverage. Fail2Test will report unsupported or incomplete runs explicitly. It will not infer business truth solely from the failing output.

## Sources of truth

| Information | Authority |
|---|---|
| What happened historically | Imported evidence, with source identifiers and completeness metadata |
| What should happen | Developer-reviewed rule and referenced requirement |
| What code is tested | Current local runner and recorded revision/environment metadata |
| What external dependencies return | Reviewed model/tool fixtures and declared matching policy |
| Whether a test passed | New execution result plus rule evaluation and completeness checks |
| Whether reduction preserved a failure | Re-execution of the same supported runner against each candidate |
| Whether an integration is supported | Published, tested adapter/version matrix |

## End-to-end workflows

### A. Local regression from a failed run

1. The developer exports a supported trace or records a run with the explicit Fail2Test test transport.
2. Import validates the format and sanitizes fields before creating a local case draft. Original source files are never overwritten or deleted.
3. Analysis identifies observable suspicious behavior and proposes a rule. The user may instead provide a rule directly.
4. The developer reviews the rule, fixture sensitivity, scope, and expected behavior. Approval binds the exact case digest.
5. The configured runner executes against mocked dependencies. The observed failure must be reproduced before a case is labeled validated.
6. Optional reduction removes irrelevant inputs only while the reviewed failure persists.
7. Export writes a readable pytest file, a case fixture, and provenance notes. Existing files require explicit overwrite.
8. The developer fixes the application. The same test executes the corrected code and passes if behavior and completeness conditions hold.
9. The developer commits the test and fixture to their own repository, subject to their data policies.

### B. Trace without a usable runner

Fail2Test can validate, sanitize, and explain evidence. It labels the artifact `trace_only`. It cannot call the artifact a reproduced regression or export an enabled passing test. The user receives runner setup instructions and a clear missing-capabilities report. A pending test scaffold is optional later; it must be skipped/errored, never green by default.

### C. Prompt/model change

A recorded bad model response remains bad even when the prompt changes. Fixed-response tests can validate application handling of that response; they do not validate prompt quality. A later opt-in live-model evaluation reruns the application with mocked tools, new model responses, explicit sampling, and cost caps. Reports distinguish sample-based outcomes from deterministic regressions.

## Initial behavior rules

| Rule | Evidence | First-release scope |
|---|---|---|
| Tool-call cardinality | Instrumented tool invocations, grouped by tool and reviewed argument keys | Duplicate refund/action, min/max count |
| Tool argument predicate | Named tool, JSON pointer, typed comparison | Equality, membership, numeric bounds |
| Forbidden tool | Instrumented invocation list | No call to a specified tool in this case |
| Output predicate | JSON output and typed comparison | Required field/value, type, membership |
| Tool-call budget | Count of observed instrumented calls | Deterministic max-call limit |

Token and monetary budgets are informational until usage is measured reliably. Historical usage cannot be presented as the cost of a mocked rerun. Arbitrary Python expressions, model-judged pass/fail, and temporal/concurrent rules are excluded from v0.1.

## One complete initial public release

We will implement and validate the complete agreed workflow locally before a public push. Internal checkpoints are development sequencing only; there is no staged public alpha/beta rollout. Initially the project owner is the sole human maintainer working with AI assistance. Contributors can join after publication.

The complete scope is the Python CLI/library, neutral import and sanitization, deterministic reviewed rule proposals, an optional model-assisted proposal route with deliberately selected provider/data handling, strict injected model/tool fixtures, current-code runner execution, supported rule DSL, bounded reduction, pytest/JSON export, focused LangGraph integration, runnable examples, tests, packaging and launch documentation/community policies. The default path remains key-free and local.

Prove the core duplicate-refund broken/fixed example first as an internal checkpoint. Then finish all agreed features and their negative/error cases, clean-install acceptance and publication preparation. Do not publish a partial early release to recruit contributors.

Choose the package version at release readiness; a complete narrow product does not require an unsupported 1.0 stability promise. More importers, asynchronous/concurrent modes, generic checkpoint resume, a dashboard and hosted operations remain later scope decisions. Commercial features, paid pilots, pricing and sales work are deferred.

## Acceptance criteria and measures

- A new user completes the key-free quickstart in a clean environment; target time under ten minutes, measured with first-time users.
- Every supported demonstration test fails on the known broken runner and passes on the corrected runner.
- Missing fixtures, unsupported behavior, and incomplete instrumentation cannot be reported as a validated pass.
- The standard import/validate/export path performs no model calls and requires no account or API key.
- Exported tests are ordinary pytest code plus the documented Fail2Test runtime; no cloud, database, or telemetry dependency.
- Baseline and reduced failures report runner revision, case digest, rule digest, mode, and execution completeness.
- Before publication the project owner completes the full clean-install acceptance workflow and supported negative controls. External usage trials and contributor feedback can follow the complete public release; they are not mandatory prelaunch recruitment.
- Hosted/commercial validation is future work and is not a gate for completing this local open source product.

The north-star usage metric is **useful exported regression tests retained and rerun**, with repeat users as a companion measure. Stars, downloads, generated-test count, and demo views are supporting signals.

## Product assumptions to test

Users will accept a small runner integration; failures can be represented as JSON; supported dependencies can be controlled; useful assertions can be reviewed quickly; current trace platforms leave enough unmet workflow pain. Interviews and technical spikes must test these assumptions before widening scope.
