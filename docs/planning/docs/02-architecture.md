# Architecture and engineering direction

## Shape

Use a modular Python package and a CLI. The first release is an in-process library with an explicit subprocess execution path, not a distributed system. The application owns its runner and business requirements; Fail2Test owns case validation, controlled dependency behavior, execution evidence, reduction, and export.

```text
Source JSON / explicit capture
        |
        v
Importer -> validation + sanitization -> local case draft
                                          |
                                          v
                                 analysis + rule proposal
                                          |
                                 developer review/approval
                                          |
                                          v
Case + local runner configuration -> execution supervisor
                                          |
                            explicit application-owned runner
                                /                     \
                       model fixture               tool fixtures
                                \                     /
                                 new execution evidence
                                          |
                            completeness + rule evaluation
                                          |
                          optional bounded fixture reduction
                                          |
                              pytest + JSON fixture + report
```

The diagram describes the local alpha. Hosted execution is a future separate trust domain with its own design gate.

## Domain vocabulary

| Term | Meaning |
|---|---|
| Trace | Historical evidence of an agent execution; it may be incomplete |
| Case | Versioned input, dependency fixtures, reviewed rules, and provenance |
| Runner | Application-owned callable that invokes current application code using injected dependencies |
| Interaction | One model/tool request and its fixture response or observed error |
| Rule | Typed assertion about a new execution; supported syntax is a closed DSL |
| Proposal | Unapproved candidate change to a rule or fixture |
| Approval | Local record binding reviewer identity/label, timestamp, and exact artifact digest; not an authenticated legal attestation |
| Validation | Re-execution that reproduces the selected behavioral failure with complete supported evidence |
| Reduction | Search for a smaller reproduction, preserving reviewed failure and required dependencies |
| Playback | Display/evaluation of historical evidence; does not execute changed application code |
| Regression run | Fresh application execution with controlled fixtures |
| Live-model evaluation | Fresh model inference, mocked tools, sampled outcome; not deterministic playback |

## Modules and interfaces

Prefer deep modules with small interfaces. Do not introduce general plugin registries, remote interfaces, or storage abstractions before a second real implementation justifies them. Separate import adapters from execution adapters: a trace format parser does not make a runtime resumable.

| Module / target package | Responsibility | Small interface | Must not own |
|---|---|---|---|
| `case` | Typed case, schema, migration, digest, invariants | `load_case`, `validate_case`, `case_digest` | Application imports or model calls |
| `ingest` | Normalize source evidence and record losses | `import_trace` | Truth about expected behavior |
| `privacy` | Structured sanitization, sensitive-field handling, export checks | `sanitize`, `check_export` | Claims of perfect secret detection |
| `rules` | Validate/evaluate closed rule DSL; evidence pointers | `evaluate_rules` | Arbitrary code or generated expressions |
| `analysis` | Evidence summaries, deterministic rule suggestions | `propose_rules` | Automatic approval or pass/fail truth |
| `execution` | Runner supervision, fixture dispatch, evidence, completeness | `run_case` | Arbitrary application discovery or process sandbox guarantees |
| `reduction` | Dependency-aware reduction and search budget | `reduce_case` | Relabeling missing evidence as a preserved failure |
| `export` | Fixed templates for pytest and machine reports | `export_pytest`, `write_report` | Executing trace-supplied code |
| `integrations/langgraph` | Supported framework-specific fixture/runner helpers | Documented runner helper | General checkpoint deserialization |
| `cli` | Parse commands, resolve trusted local config, render results | CLI command contract | Business logic duplicated from library |

Internal functions may vary; public names remain provisional until the technical proof. The build contract fixes behavior, not an obligation to create a class per table row.

## The execution seam

The developer supplies `run(input, context)` through a locally reviewed configuration entry. The context exposes recorded model responses and mocked tool transport. The runner returns JSON-compatible output. It must route supported model and tool calls through those interfaces and declare capabilities.

Fail2Test executes that runner against **current code**. It does not take source code from a trace, import modules named by remote input, restore arbitrary object graphs, or reuse a historical result as if it came from the current runner.

v0.1 supports synchronous, sequential JSON behavior. A plain Python synthetic runner and the supported LangGraph example exercise the same seam. Unsupported concurrency, hidden network clients, non-JSON state, async calls, subprocess tools, or missing observations prevent a complete supported claim. Declared instrumentation cannot prove that arbitrary user code has no hidden side effects; see the threat model.

LangGraph's checkpoint/time-travel APIs can rerun later nodes including model/API calls and interrupts. They are not automatically safe deterministic replay. The first adapter therefore starts the configured graph with explicit controlled dependencies. Checkpoint resume is a later, separately tested capability, not a promise inferred from a framework API.

## Reproduction modes

| Mode | Runs user code? | New model inference? | Tool behavior | Valid conclusion |
|---|---|---|---|---|
| `trace_only` | No | No | Historical records only | Describes recorded behavior |
| `fixture` | Yes | No | Approved fixture dispatch | Current code handles this controlled scenario correctly/incorrectly |
| `live_model` (later) | Yes | Yes, explicitly enabled | Mocked tools only in initial design | Sampled current-model behavior under declared conditions |

Fixture mode is the default regression mode. A prompt change can alter a model request; strict fixture matching then reports an interaction mismatch. It must not pretend that a canned model response demonstrates the effectiveness of the new prompt. Model-response interventions are explicit new cases, with changed provenance and renewed approval.

## Persistence and identity

- Directory bundles with UTF-8 JSON in v0.1; no archive extraction or executable serialization.
- A user-selected local workspace contains drafts, immutable approved case versions, results, and reduction attempts. No global daemon or central database is needed.
- The application repository stores exported tests and case fixtures under the user's chosen path.
- Canonical JSON digests bind approvals and artifact identity; normalized tool matching and identity hashing are separate operations.
- Raw trace sources remain user-owned. The importer reads them and writes sanitized outputs without modifying the original.
- Time, random values, locale, and relevant environment settings are explicit context/fixture data when they affect behavior. Otherwise the run cannot claim controlled reproduction.
- Reports identify application revision and dirty-state fingerprint without embedding source files. Missing Git metadata is allowed but labeled; digest the declared runner inputs/lockfile when available.

Content hashes detect changes. They are not signatures, verified authorship, or proof that an artifact is safe.

## Failure observation and matching

Tool observations record calls reaching the test transport. The mock implements reviewed response rules and never forwards unknown calls to a live tool. A repeatable tool fixture may serve duplicate calls so a duplicate-call assertion can actually observe the bug. A fixed runner that calls once may leave fixture responses unused; unused fixtures are reported rather than automatically failing a behavior rule. Model fixtures are ordered and request-matched; missing or out-of-order required interactions are incomplete.

The tool-call rule evaluates new observations, never the imported trace. An unknown request, unsupported action, timeout, or missing instrumentation is a run error/incomplete result, not an assertion success. A correct outcome plus an incomplete execution is not a pass.

## Reduction

Reduce only explicitly removable inputs, messages, and fixture items. Preserve schema requirements, model/tool pairing, scenario constraints, and dependency closure. Each candidate reruns the configured target with the same reviewed rule and mode. Accept a candidate only if execution completes and reproduces the same selected rule failure.

Use bounded delta debugging and simple deletion strategies first. Report attempted candidates, elapsed time, size delta, cache hits, and why search stopped. A local one-minimal result under the tested deletion operator is not global semantic minimality. If no safe reduction exists, retain the validated original case.

Cache only deterministic fixture-mode executions with a key that includes case digest, rules, runner revision/dirty fingerprint, package/adapter version, relevant configuration, and runtime fingerprint. Unidentified code state disables reuse. Never cache a live-model sample as a deterministic result.

## Optional AI

AI may propose suspicious steps, candidate predicates, and explanatory text from a sanitized bounded view. It cannot approve rules, declare business truth, change execution permissions, or generate code that is executed automatically. Proposal format is JSON validated against the same closed schema. Provider choice and credential setup are an explicit implementation decision after the key-free proof, before the complete first public version. No credential creation or private-data upload is authorized by this design. The key-free local path remains complete when a provider is unavailable.

## Evolution seams

Portable versioned cases and machine-readable results support future imports, a TypeScript consumer, CI integrations, and hosted execution. Avoid premature multitenancy columns, billing hooks, account models, and cloud SDK dependencies in the local package. Introduce public adapter entry points only after two supported adapters demonstrate a stable common contract.

Sources: [LangGraph time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel), [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).
