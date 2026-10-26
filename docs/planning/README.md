# Fail2Test project blueprint

**Status:** detailed supporting design for a local end-to-end build. Updated 26 October 2026. The controlling delivery decision is [the repository plan](../../PLAN.md): one complete initial public release, initially just the project owner with AI assistance; commercialization is deferred.

**Mission:** turn a real agent failure into a reviewed, portable regression test that runs against the developer's application.

This pack defines a credible first open source release and the work needed to mature it. It does not claim that a package, GitHub organization, trademark, CI pipeline, integration, benchmark result, or customer already exists. Commands and interfaces in these documents are proposed build contracts. The `templates/` directory contains publication drafts; `reference/` contains design examples, not runtime artifacts.

## Recommended decisions

| Area | Recommendation |
|---|---|
| First user | Python engineers who maintain tool-using agents and already have failed runs |
| First outcome | A test that fails against a known broken application revision and passes against a corrected revision |
| Product form | Local CLI, Python library, ordinary pytest export, JSON reports |
| First supported execution | Synchronous, serial, application-owned runner with injected model and tool dependencies |
| First framework | Narrow LangGraph example and adapter; the core does not depend on LangGraph |
| License | Apache-2.0 for code, documentation, schemas, and project-created examples |
| Contributions | DCO sign-off; no copyright assignment or broad CLA at launch |
| Privacy | Local processing by default, no telemetry, no model upload without explicit choice |
| Distribution | One Python distribution initially; no mandatory database, account, daemon, or browser UI |
| Commercial context | Preserve portable artifacts and an open core; no paid product or commercial validation work in the initial build |
| Public roadmap | Prepare ROADMAP.md locally; publish it with the completed project; use issues/RFCs once public |
| Timeline | Evidence-based milestones and engineering-hour estimates; no promised launch date |

These are planning recommendations made within the requested scope. Account ownership, contacts, legal identity, publishing authority, and real-user validation remain recorded prerequisites; they have not been silently assumed to exist.

## Read in this order

1. [Product and scope](docs/01-product.md): users, workflows, claim limits, acceptance criteria.
2. [Architecture](docs/02-architecture.md): modules, execution seams, data ownership, reproduction modes.
3. [Build contracts](docs/03-contracts.md): CLI, runner interface, fixture semantics, lifecycle, errors.
4. [Security and privacy](docs/04-security-privacy.md): threat model, trust boundaries, data handling.
5. [Repository and engineering](docs/05-repository-engineering.md): target tree, dependencies, development workflow.
6. [Verification and benchmarks](docs/06-verification.md): correctness, negative tests, evaluation, performance.
7. [Delivery backlog](docs/07-delivery-plan.md): implementable slices, dependencies, estimates, owners.
8. [Open source stewardship](docs/08-open-source.md): license, governance, contributors, maintenance.
9. [Release and operations](docs/09-release-operations.md): CI, publishing, provenance, rollback.
10. [Documentation and launch](docs/10-documentation-adoption.md): documentation map and adoption plan.
11. [Commercial evolution](docs/11-commercialization.md): OSS promise, paid value, cloud prerequisites.
12. [Readiness, decisions and evidence](docs/12-readiness-decisions.md): stage reports, decisions, remaining gates.

Also see the proposed [public roadmap](ROADMAP.md), [reference case](reference/duplicate-refund.case.json), [fixture schema](reference/case.schema.json), [publication templates](templates/README.md), [primary-source research](research/oss-reference-research.md), and [planning verification report](QA.md).

## First milestone

Build one key-free demonstration: a synthetic refund agent makes the same tool call twice; Fail2Test imports the sanitized failure, the developer approves a no-duplicate rule, and an exported pytest test re-executes the user's runner. The broken runner fails the rule; the corrected runner passes. Missing interactions or missing instrumentation produce an error rather than a green test.

The first technical spike must establish this before a UI, hosted service, generalized trace integrations, or marketing launch. If user-code changes cannot be distinguished from playback of an old recording, the product has not achieved its purpose.

## What “at par” means here

Adopt the practices of mature projects: clear contracts, useful docs, predictable releases, public decisions, contribution paths, security reporting, tested examples, and a maintainable support policy. Maturity is earned through real use and maintenance. A large folder tree, badges, or an untested cloud skeleton does not establish it.

## Workspace status

A dedicated local Git repository now exists at the fail2test project root, with this pack under docs/planning. The wider workspace also has Git metadata; work inside the dedicated project directory. No remote, GitHub repository, issue, package registration or external publication has been created. Templates remain publication drafts, and proposed commands remain unimplemented. See the repository PLAN.md for the current source of truth.
