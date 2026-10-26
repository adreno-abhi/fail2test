# Verification, benchmarks and evidence

## The central falsifiability test

A useful generated regression is not established by checking the stored failure trace. For every supported reference scenario:

1. Import and approve one case.
2. Re-execute a known broken application runner; verify the intended rule fails with complete execution.
3. Re-execute a corrected runner with the same approved case/rule; verify a complete pass.
4. Deliberately remove a necessary fixture; verify incomplete/error, never pass.
5. Deliberately change an unsupported dependency/capability; verify explicit unsupported status.
6. Demonstrate that the generated pytest test uses the current local code revision.

These checks are release-blocking for any scenario advertised as supported. Do not claim causal proof from a single live-model rerun or blanket correctness from one regression.

## Test layers

| Layer | What it proves | Examples |
|---|---|---|
| Schema/domain | Portable contract and lifecycle | Unknown versions, wrong types, digest edits invalidate approvals |
| Rules | Behavioral intent evaluated on new evidence | Zero calls, duplicate keys, missing pointer, numeric/string distinctions |
| Fixture transport | Exact matching, no live fallback | Reordered object keys, changed arrays/prompts, duplicate rules, unknown tool |
| Runner integration | Current code is exercised | Broken/fixed runner pair, timeout, crash, non-JSON output |
| Adapter conformance | Supported framework follows same interface | Plain runner and LangGraph example produce compatible observations |
| Reduction | Failure retained and search bounded | Missing fixture never accepted; same selected rule fails; budget exhausted retains best valid candidate |
| Export | Test remains readable, executable, inert | Special-character labels, malicious text, clean-env pytest run |
| Privacy/security | Sensitive input cannot casually leak | Synthetic canaries in success/error/report/export paths |
| Packaging | Shipped wheel/sdist works independently | Installed CLI, bundled schemas, type markers, extras, example execution |
| Docs | Instructions are usable | Key-free tutorial executed in CI and tested by first-time external users |

Do not add superficial tests that only repeat implementation or snapshot every internal detail. Favor invariants and user-visible behavior. Coverage is a signal, not proof; set an initial core/rules/execution target of 90% line coverage and require security/error paths to be exercised. Adjust only with an explained issue, never to hide untested claims.

## Integration usability acceptance

Validate onboarding as well as execution correctness. In a fresh environment, follow the published install and tutorial without undocumented maintainer setup. Target under ten minutes for the key-free example and roughly thirty minutes for the first useful regression in a realistic supported sample whose model/tool dependencies can be injected. Report actual measurements and prerequisites rather than advertising these targets as achieved.

The realistic sample must live outside the package's internal implementation tests, require one small application-owned runner, and execute exported tests through ordinary pytest. Record every necessary application change. If integration demands an architectural rewrite, hidden monkeypatches, an account, a background service or a custom CI system for the supported local path, revisit the interface before declaring launch readiness.

Exercise common setup failures and verify the error points to a concrete correction: missing dependency extra, unsupported framework version, missing injection seam, invalid runner name, mismatched model request and incomplete evidence. CLI help, integration guide and copyable CI example must match the tested path.

## Reference scenarios

Start with six deliberately labeled synthetic cases: duplicate tool action, wrong argument, forbidden tool, required output missing, tool-call budget exceeded, and irrelevant-context reduction. Each has source evidence, reviewed requirement, broken/fixed runner, expected status and license. Include at least one nonreducible valid case and one trace-only case.

Before public alpha, expand to 12–20 scenarios covering combinations and negative controls. Exact count is less important than every advertised rule/mode/error path having a falsifiable example. Do not scrape production traces or upload customer artifacts to create a larger-looking benchmark.

Adversarial cases include malformed/deep/large JSON, duplicate fixture match, Unicode/path issues, NaN/infinity, huge exception messages, prompt-injection text, template injection, symlink escape, partial execution, missing events, redaction collisions, hidden side-effect bypass demonstration, and no-op behavior passing a weak rule.

## Benchmark manifest

Each case records `id`, `license`, `origin`, `requirement`, `supported_capabilities`, `broken_runner_revision`, `fixed_runner_revision`, `case_digest`, `selected_rule`, `expected_outcomes`, `environment`, and known limitations. User-submitted examples require clear redistribution rights and sanitization review.

Public results report:

- Supported/importable fraction, with unsupported cases included in the denominator.
- Failure reproduction rate on known broken runners.
- Corrected-run pass rate with unchanged reviewed rules.
- False-pass count on incomplete/unsupported controls (target zero in supported suite).
- Assertion usefulness and editing time from independent user review.
- Reduction in input/fixture size, execution count and timeout rate.
- Wall time and memory on a named reference machine and pinned environment.
- Live-model results, if later added: model/provider/version, run count, dates, tool mocking, cost and uncertainty, separately from fixture results.

Compare with manual pytest fixture construction and the user's existing trace-to-dataset workflow. Do not compare unrelated benchmark numbers or claim superiority over a platform from a hand-picked demo. Publish methodology and failures alongside wins.

## Initial performance budgets

Targets to validate rather than existing performance claims: a small synthetic case imports/inspects in under two seconds excluding environment startup; a deterministic run adds under one second of tooling overhead beyond runner time on the reference machine; reduction stays within user-specified count/time limits; report output remains bounded. Real measurements decide stable defaults.

## Model-assisted proposal evaluation

Keep proposal quality separate from execution correctness. A proposed assertion must be grounded in an explicit requirement/evidence pointer, validate against the closed DSL, and receive review. Measure incorrect suggestions, unsupported certainty, editing effort, sensitive data exposure and consistency across failures. Do not approve proposals merely because they reject the historical trace. Generated business requirements are hypotheses, not expected-output labels.

## CI policy

PR checks run offline synthetic tests on supported Python versions and a lean OS matrix. Use Linux across the Python range; test Windows and macOS on the main supported version plus targeted path/process cases. Scheduled/manual compatibility jobs cover LangGraph versions and declared dependency bounds. Network/provider tests are separate, manual or protected, budgeted and never required for ordinary contributor PRs.

Required before release: all advertised broken/fixed pairs, negative false-pass controls, install smoke from built artifacts, schema parity, strict docs build, license/dependency review, synthetic secret checks and release artifact verification. A known blocking failure creates a release issue and holds that release; it is not relabeled an expected success.

## Acceptance evidence per feature

Attach a sanitized command transcript, relevant test result, schema/contract diff if applicable, and updated documentation. For reduction attach before/after digest and reproduced failing rule. For privacy attach synthetic canary checks. For adapter changes attach the compatibility matrix result. No raw customer evidence in public PRs.
