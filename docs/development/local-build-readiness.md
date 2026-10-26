# Local build clearance

Scope: implement and test the key-free local fixture workflow in this repository. This is not public-release or hosted-execution clearance.

## Stage 1 — PASS

The user authorized starting the agreed end-to-end local project. PLAN.md and the architecture define the outcome, supported serial runner, data sources and local trust model. Fixtures are synthetic and no external model processing is included in this slice.

## Stage 2 — PASS

The case/rule/runner/CLI contracts and reference case exist in docs/planning. Acceptance requires broken/fixed current-code execution, strict fixture matching, and distinct incomplete/error behavior. Changes discovered during implementation are recorded in the development status and current reference docs.

## Stage 3 — PASS for this local implementation scope

Python 3.13 and uv are available. A project-local virtual environment and committed dependency lock provide repeatable setup. Build/install/smoke commands are specified in pyproject.toml/AGENTS.md; package-specific verification evidence will be recorded after execution. Local source and fixtures remain the source of truth. Rollback is the local Git history and original fixtures; no user source is rewritten, no registry or cloud state is mutated. There are no runtime service credentials or interactive production identities in this scope.

## Clearance

Cleared to implement and verify the local workflow under these contracts. Actual publishing remains subject to the separate publication checklist. Account ownership, private reporting contacts, provider selection and hosted isolation are not claimed resolved.

Evidence before implementation: PLAN.md; docs/planning/docs/02-architecture.md; docs/planning/docs/03-contracts.md; docs/planning/reference/duplicate-refund.case.json; local interpreter/tool checks. Implementation and test results are MISSING until run, not inferred from this clearance.

## Executed evidence

The local workflow is now implemented. See [build verification](build-verification.md) for the actual test, typing, lint, docs and clean-install results. This closes the scoped local build checks; it does not close the full public-release checklist or later provider/security decisions.
