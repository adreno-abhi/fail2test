# Delivery plan and issue-sized backlog

## Delivery model

**Updated direction:** all P0–P3 checkpoints and required first-version features are completed locally before a single initial public release. The checkpoint names below do not mean public staged releases. The project owner is initially the only human maintainer. No contributor recruiting or paid pilot is required before launch. [Repository PLAN.md](../../../PLAN.md) controls this delivery strategy.

Implement vertical slices that prove the execution claim early. Estimates below are engineering effort, not elapsed dates or contractual commitments. They assume an experienced Python engineer and exclude user-recruitment delays, registry administration and legal review. AI assistance does not remove review, integration or security work.

| Milestone | Goal | Effort estimate | Exit evidence |
|---|---|---:|---|
| P0 technical proof | One broken/fixed runner pair and portable case | 24–40 hours | Current code re-executed; incomplete control errors; key-free demo |
| P1 core contracts | Import, rules, reviewed lifecycle, CLI | 60–92 hours | Typed schemas, exact matching, tested error states |
| P2 regression workflow | Runner execution, export, reduction, LangGraph slice | 96–152 hours | Exported test works in clean environment; adapter conformance |
| P3 launch-ready local build | Documentation, community files, packaging, release security, owner acceptance | 80–120 hours | Full local acceptance and publication checklist |
| P4 post-launch candidates | Feedback, one requested import, serial async, optional proposals | 120–200 hours | Repeat use, stable compatibility, error/privacy improvements |

The earlier P0–P3 core estimate totals **260–404 engineering hours**, excluding added model-provider integration and any additional first-launch polish. Re-estimate the complete initial scope after P0; this is not a release-date promise. At 15–20 focused hours/week this is approximately **13–27 weeks**, depending on effective availability and rework. A small proof can be achieved much sooner; a dependable public project requires the later work. Re-estimate after P0 and first external trials. Do not advertise all beta features in an alpha launch.

## Roles

The project owner is the initial product steward and sole human maintainer, working with AI assistance. The role breakdown is a future handoff map; it does not imply a team already exists. Assign real GitHub handles before publication for technical maintainer, security contact, release owner and community moderator. One person may initially fill several roles; record the capacity and continuity risk. Contributors own accepted issues, not mandatory unpaid support obligations. A second maintainer is a growth milestone, not a fictitious board.

## P0 — prove the hard part

| ID | Work item | Dependency | Acceptance / evidence | Owner role |
|---|---|---|---|---|
| F2T-001 | Confirm product contract, naming checks and reference failure | None | Owner reviews the scenario and runner integration contract; user interviews can follow publication | Project owner |
| F2T-002 | Establish package/dev toolchain and clean-env test | None | CLI help, wheel install, supported Python dependency resolution | Maintainer |
| F2T-003 | Implement minimal case model and reference JSON | 002 | Reject invalid case; deterministic case identity | Core contributor |
| F2T-004 | Implement duplicate-refund broken/fixed runners with injected transports | 003 | Same model/tool fixtures; two versus one observed tool invocation | Runtime contributor |
| F2T-005 | Execute rule on fresh observations and export one pytest test | 004 | Broken fails, fixed passes, missing fixture errors; no model key needed | Maintainer |

P0 decision: continue only if the current-code test is real, integration effort is tolerable to trial users, and missing evidence cannot create a false pass. If it fails, revise the seam/scope before building more importers or a UI.

## P1 — core contracts

| ID | Work item | Dependency | Acceptance / evidence | Contributor suitability |
|---|---|---|---|---|
| F2T-006 | Full alpha rule DSL and generated JSON Schema parity | 005 | Positive/negative cases for each supported rule | Core, reviewed |
| F2T-007 | Source JSON importer with loss/capability report | 006 | Incomplete trace stays trace-only; no code imports | Intermediate |
| F2T-008 | Structured sanitization and sensitivity report | 007 | Synthetic secrets absent from all persisted/logged outputs | Security review |
| F2T-009 | Review/digest/lifecycle records | 006,008 | Artifact edits invalidate review/validation; no false authenticated-identity claim | Core |
| F2T-010 | CLI commands, exit codes, JSON diagnostics | 007,009 | Scriptable noninteractive flow and no accidental overwrite | Intermediate |
| F2T-011 | Bounded parsing, paths and atomic writes | 007 | Size/depth/path/cancellation controls pass | Security review |

## P2 — complete regression workflow

| ID | Work item | Dependency | Acceptance / evidence | Contributor suitability |
|---|---|---|---|---|
| F2T-012 | Strict model/tool matching and repeatable mock semantics | 006,009 | Duplicate calls observable; unknown calls never forwarded | Core |
| F2T-013 | Supervised execution and result contract | 010,012 | Current code identity, timeout, incomplete/error separation | Runtime |
| F2T-014 | Fixed-template pytest/JSON export | 013 | Clean-env execution and injection-resistant literals | Intermediate + security review |
| F2T-015 | Bounded dependency-aware reduction | 013 | Selected failure preserved by fresh execution; original retained on no reduction | Advanced |
| F2T-016 | Narrow LangGraph runner helper and conformance suite | 013 | Declared framework versions; no unsupported resume/sandbox promise | Integration specialist |
| F2T-017 | Reference scenarios and benchmark manifest | 014,015 | Broken/fixed/negative controls for each supported claim | Good first scenario issues |
| F2T-018 | Complete key-free quickstart and migration guide | 014,016 | First-time user can execute documented flow | Docs + maintainer |

## P3 — make it a maintainable initial public release

| ID | Work item | Dependency | Acceptance / evidence | Owner role |
|---|---|---|---|---|
| F2T-019 | License/notice/inventory and governance publication files | 001 | Exact license, actual contacts/handles, DCO policy, contribution docs | Steward |
| F2T-020 | PR CI, docs, packaging and compatibility jobs | 002,017,018 | Clean jobs, restricted permissions, no fork secrets | Release maintainer |
| F2T-021 | Protected TestPyPI/PyPI publisher and provenance rehearsal | 019,020 | Registry ownership verified; test artifact install and attestation checks | Release owner |
| F2T-022 | Owner end-to-end acceptance and documentation corrections | 018 | Full clean-install workflow and failures reviewed locally; external trials optional after publication | Project owner |
| F2T-023 | Security review and unsupported-claim audit | 008,011–017 | False-pass/adversarial controls, privacy review, claims mapped to evidence | Security contact |
| F2T-024 | Single complete initial public release and launch material | 019–023,027 | Full local acceptance, proposal route verified, owner-authorized publication and truthful supported matrix | Release owner |

## Additional work and later scope

- F2T-025: choose exactly one trace-platform importer based on external requests; publish the data-loss/capability mapping.
- F2T-026: serial asynchronous runner semantics, cancellation and conformance, if trial applications require it.
- F2T-027: include the optional model-assisted proposal route in the complete initial build, with selected provider, bounded inputs, reviewed JSON output, credential/data-flow contract and separate evaluations. Implement after the key-free execution proof; re-estimate effort when its provider contract is selected.
- F2T-028: GitHub Actions usage guide and useful CI reports; a published Action only if standard CLI installation is insufficient.
- F2T-029: schema migration/deprecation tooling and supported dependency matrix.
- F2T-030: deferred future commercial research only. No paid pilots, cloud service, billing or accounts in the current build.

## Issue hygiene

Every issue contains problem/user outcome, scope, affected interface/schema, dependencies, acceptance scenario, test evidence, docs impact, privacy/security impact and a size estimate. Link public roadmap items to milestone and issues. Prefer issues finishable in one to three focused days; split large runtime/security work before assignment.

Labels: `type:bug`, `type:feature`, `type:docs`, `type:security` (public-safe metadata only), `area:core`, `area:runtime`, `area:adapter`, `area:docs`, `good first issue`, `help wanted`, `needs reproduction`, `needs design`, `blocked`, and `breaking change`.

Good first issues should be genuinely bounded: improve an error explanation, add a synthetic fixture to an existing rule, clarify a tested tutorial, reproduce a platform-specific path issue, or add a docs link check. Do not label a security-sensitive runner redesign a beginner task.

## Definition of done

Behavior and errors match the contract; relevant tests pass; documentation and changelog are updated; no sensitive artifacts are introduced; compatibility impact is recorded; DCO is satisfied; reviewer can reproduce acceptance evidence. A feature merged behind an experimental label is not a stable supported interface.

## Work sequencing and change control

Keep core scope stable through P0. A major scope change requires an RFC/ADR and re-estimate. Add a second framework only after the first conformance suite is useful and someone can maintain the new adapter. Put unvalidated ideas in `Later`, not a dated roadmap promise. Review the roadmap monthly during active development and after each release.
