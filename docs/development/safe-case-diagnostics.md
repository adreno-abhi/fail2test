# Privacy-safe case authoring diagnostics

28 October 2026. The owner approved improving validation errors so developers can locate
invalid case fields without exposing their values. Work starts from merged `main` `53727aa`.
This step is local only: no provider calls, push, visibility change or package publication.

## Problem reproduced

Six initial regressions failed against the previous behavior. CLI import/file load/review
returned generic messages without the invalid field; a browser edit error directly joined
Pydantic location components and could echo an unknown property name. Tests used only
synthetic private-looking names and values; this is not a claim that user data was disclosed.

## Result and boundaries

A shared formatter walks the trusted model's runtime JSON Schema to retain known fields,
list indices and tagged-rule structure. It does not infer trusted field names by matching
against a global allowlist: a private dictionary key named like another schema field is
still withheld. Output uses fixed explanations for missing/type/bounds/kind errors and
omits raw values, unknown properties, validator messages, context and URLs. Error output
is capped at five issues; remaining issues are acknowledged without listing their inputs.

Import, `Case.load`, rule review, normalized trace-fixture checks, AI preview and browser
case editing share this behavior. Existing error codes and exit statuses remain intact.
Validation and review predicates are unchanged. Rejected imports write no bundle, and
rejected edits/reviews preserve saved case and authorization bytes. Browser drafts remain
editable after failure. Raw validation causes are suppressed on the formatted case paths.
Unscoped browser validation exceptions use a generic safe fallback instead of raw locations.

Externally edited bundles with a non-object case root or malformed provenance now reach
schema validation before review preprocessing can assume object fields. Two additional
regressions reproduced the previous attribute errors and verify stable `INVALID_REVIEW`
responses with the entire saved bundle unchanged.

For example, a rule lacking its requirement points to `case.rules[0].requirement` and
states that the required field is missing. Unknown properties point to their enclosing
schema object; dynamic JSON-key paths are not printed. Object-level validation errors can
identify only the object, not every conflicting field. The generated case schema remains
the detailed reference. Direct Pydantic `Case.model_validate` exceptions retain their normal
API, so developers must not treat raw validator exceptions as sanitized output.

No model/tool fixtures, runner capability requirements, baseline prerequisites, digest
bindings, error-versus-failure semantics or provider consent rules were relaxed.

## Verification

The focused diagnostics tests exercise missing fields, invalid kinds/bounds/types, unknown
keys, opaque dictionaries, private validator text, default exception-chain rendering, bounded
messages, CLI JSON errors, normalized traces, AI preview without credentials and rejected-edit
state preservation. A real Chromium test verifies the visible field explanation and retained
draft.

The full Windows/Python 3.13.5 suite passed **211 tests**, including Chromium, at **89%**
runtime coverage. Lint, formatting and strict mypy pass. The installed acceptance harness
now also checks this diagnostic from a fresh installed wheel, not the source checkout.
Strict documentation, repository/link/form checks and the unchanged 82-package lock/license
inventory pass. Fresh core wheel, source-install and native smoke workflows pass. Installed
CLI/Chromium/native acceptance also passes, including the new installed diagnostic check and
the unchanged exported-test bug/fix proof. No model provider is contacted.

All 13 focused diagnostics tests also pass against a freshly installed core wheel on
Python 3.12.13 with direct minimums Pydantic 2.10.0, rfc8785 0.1.4, Typer 0.16.0 and pytest
8.3.0. Transitive dependencies were resolver-selected, not a lowest-transitive matrix.
Two upstream Typer/Click deprecation warnings were reported; no warning filters were added.

One smoke attempt returned exit 3 at native baseline validation while installed acceptance
was running concurrently. That attempt did not capture a tooling code, so its cause is
unconfirmed. The harness now requests JSON for that validation step; a sequential smoke run
passed without relaxing the ten-second runner limit or retrying within the harness. This
record does not relabel the first attempt as a pass or assert an unproved timeout diagnosis.

Artifact hashes and acceptance events are retained in ignored local audit records. PR #5 subsequently merged as `9799430`. All six matrix jobs, quality/browser/package
and `ci-complete` passed on [merged-main run 40645352245](https://github.com/adreno-abhi/fail2test/actions/runs/40645352245),
including 211 full-suite tests at 89% runtime coverage and installed acceptance. The PR's
push run required one targeted retry after pinned uv download stalled before any tests;
no source change or relaxed test was used. The fresh merged-main run passed without that
retry. See the [final release review](final-release-review.md) for remaining launch checks.
These checks do not authorize public visibility or a release.
