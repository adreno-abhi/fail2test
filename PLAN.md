# Current development plan

Updated 27 October 2026 to reflect the project owner's direction. This document controls delivery/launch strategy if an older research or draft note differs.

The private GitHub repository now exists and merged `main` passes hosted CI. Public
visibility, releases and registry publication remain separately approved actions.
The current [developer adoption review](docs/development/developer-adoption-review.md)
records audience fit, tested onboarding, unresolved friction and proposed launch priorities.

## Outcome

Build one complete, narrowly scoped open source product locally, verify it end to end, prepare the repository for others to use and contribute, and then publish it to GitHub. Initially the project owner is the only human maintainer, working with AI assistance. Commercialization is future context only.

“Complete” means the full agreed user workflow works with documented supported inputs and honest limitations, through both developer tooling and a focused local browser UI. It does not mean support for every agent framework, arbitrary distributed systems, a general observability platform or a hosted business.

## Approval between steps

Work through one agreed implementation step at a time. At completion, report delivered behavior, validation results and material limitations, then propose the next bounded step. Wait for the project owner's explicit approval before starting that next step. Approval includes necessary fixes, tests, docs and local commits within the agreed scope, not unrelated features or publication. Keep this process through final GitHub setup/publication; those actions require their own approved step.

Completed steps: the key-free core workflow, native synchronous LangGraph adapters and the bundled local browser UI over the same engine. The owner subsequently approved optional provider-independent AI suggestions and free-only OpenRouter verification with their existing key. CLI/UI profiles, preview/send consent and validated unapproved rules are implemented. Live provider checks and their limitations are recorded in docs/development/ai-suggestions-verification.md. Local runtimes must not be installed or started without the owner's approval.

## Complete first-public-version scope

Local community/repository readiness is now implemented; see
[verification](docs/development/repository-readiness.md). Public identities/private contacts,
compatibility/usability acceptance and GitHub/registry verification remain explicit gates.

1. A Python package, local CLI and library interface.
2. Supported trace import with structural validation, sanitization and a loss/completeness report.
3. Rule proposals and explicit developer review; deterministic suggestions remain usable without credentials. Include an optional model-assisted proposal path once its provider/data contract is selected during implementation; ordinary execution and export stay key-free.
4. Application-owned runner that re-executes current code with injected model and tool fixtures.
5. Strict fixture matching, clear behavioral-failure versus incomplete-execution errors, and no silent live-tool fallback.
6. Reviewed assertions for duplicate calls, argument bounds, forbidden tools, output conditions and call budgets.
7. Bounded reduction that keeps the selected failure reproducible.
8. Readable pytest export with portable fixtures and useful console/JSON reports.
9. A focused LangGraph integration and framework-neutral synthetic runners.
10. A documented, tested key-free example from failure evidence through a failing regression and a passing fix.
11. Package-install checks, meaningful automated tests, documented compatibility and privacy/security limitations.
12. README, architecture/reference/tutorial docs, license, contributor guide, roadmap, support/security/governance policies and release procedure ready for publication.
13. A focused local browser UI for evidence inspection, sanitization/assertion review, regression execution, reduction comparison and pytest export, using the same engine and review checks as the CLI. See [UI scope and acceptance criteria](docs/planning/LOCAL_UI_SCOPE.md).

The optional provider route is part of the planned feature review, not permission to create credentials, buy services or upload private traces. Choose the provider and data handling deliberately when implementing it. A provider outage must not block the key-free workflow.

## Developer integration is a release requirement

Treat integration effort as a product acceptance criterion, not documentation polish. The supported path must fit an existing repository and its ordinary test/CI workflow.

- Install as a normal Python dependency; no required account, daemon, database or hosted service for the local workflow.
- Offer the browser UI as an explicitly started local application. CLI/library users do not need to run its server. End users should not need Node.js or frontend build tools; bundle the UI assets in the package.
- Provide two copyable starting points: a key-free example and an existing-application integration guide for the supported LangGraph configuration.
- Keep the application-owned runner to one small entry point with explicit model/tool dependency injection. Do not require rewriting the application's architecture to adopt the supported path. If that path needs broad refactoring, revisit the execution interface before launch.
- Generate ordinary readable pytest tests and version-controlled JSON fixtures. Developers should run them with their existing pytest command and CI tooling.
- Provide a copyable CI example, documented dependency extras and a supported-version matrix. No custom CI platform is required.
- Validate configuration/capabilities early and give actionable diagnostics for missing injection, unknown interactions, unsupported execution and fixture mismatch.
- Keep core use independent of model-provider credentials; optional AI suggestions must not complicate basic installation or regression execution.
- Measure first-use effort on a fresh environment. Initial targets: under ten minutes for the maintained key-free tutorial and roughly thirty minutes to the first useful regression in a supported, dependency-injectable sample application. These are targets to test, not established guarantees or promises for arbitrary repositories.
- Test a realistic sample integration outside the package's own internal test harness. Record the required application changes, setup steps, troubleshooting and elapsed time. A polished synthetic demo alone is insufficient acceptance evidence.

## Internal work sequence — no staged public releases

### 1. Establish the foundation

Keep this dedicated Git repository local. Establish package/tooling structure, versioned contracts, architecture decisions, tests and the exact supported framework/runtime matrix. Work in small local commits, with the project owner reviewing significant choices. No external contributor administration is needed during the build.

### 2. Prove fresh execution

Build the duplicate-refund synthetic example first. Execute current broken and fixed runners with the same reviewed fixture/rule. Confirm that broken code fails, corrected code passes, and missing fixtures produce an error. This is an internal correctness checkpoint, not an alpha release.

### 3. Complete the workflow

Implement import, sanitization, proposals/review, execution, all first-release rule kinds, reduction, pytest export, reports and the LangGraph integration. Add the approved local browser UI over those same contracts. Fill in the error paths as part of each change. Avoid building unrelated cloud infrastructure or generalized replay machinery.

### 4. Finish quality and repository readiness

Exercise the whole workflow from a clean environment using the built package. Verify negative cases, privacy checks, generated-test safety, compatibility and examples. Finish the actual documentation and contributor/security/release files. Keep publication templates clearly marked until real contacts, account identities and workflows are configured.

### 5. Prepare and publish once complete

Select the GitHub owner/name and publishing identities when the project is ready. Create/configure the repository, enable required security/community features and run host-specific checks. Only make it public and publish packages after acceptance evidence and owner authorization exist. If a host-only check needs a private GitHub repository first, handle that explicitly at this point; it does not imply a public early release or an authorized push now.

The exact initial package version will reflect supported compatibility, rather than pretending that “complete” requires a 1.0 label. No public alpha/beta sequence is planned.

## Local Git workflow

- This directory is its own repository inside a broader workspace that also has Git metadata. Run Git commands with this directory as the working directory.
- Use `main` as the repository's default branch; use focused work branches when useful, with `codex/` for agent-created work branches by default.
- Make small meaningful commits after relevant checks. The project owner's configured Git identity must be used; never invent a name/email or write a fake sign-off.
- Do not add a remote, create a GitHub repository, publish a package or push until the owner requests that step.
- Keep raw traces, credentials, local environments, caches and execution artifacts untracked. Curated synthetic examples are tracked deliberately.

## Ready-to-publish checklist

- [x] Full key-free workflow works from a clean installation of the actual built artifacts.
- [x] The local browser UI completes the same reviewed failure-to-test workflow; browser tests verify errors, review invalidation, execution results and export. Bundled assets work without frontend build tools or external assets on the user's machine.
- [x] The supported injection-friendly sample integrates through a small runner and runs ordinary exported pytest; automated effort and limitations are recorded.
- [x] Owner confirms the guided sample UI walkthrough through saving an export; see `docs/development/owner-walkthrough.md` for limits.
- [ ] Real host CI verification and independent human onboarding/integration timing are complete.
- [x] Exported tests execute current application code, fail on the known broken runner and pass on the corrected runner.
- [x] Missing/unsupported/incomplete evidence has negative coverage and does not produce a validated green result.
- [x] Supported rule kinds and LangGraph integration have positive/negative acceptance coverage in the documented local matrix.
- [x] Sanitization, error output, untrusted-input handling, reduction limits and generated-test safety are locally checked; see `docs/development/release-audit.md` for scope and limitations.
- [x] README, tutorial, CLI/config/schema references, architecture and troubleshooting match implemented behavior; host-only references remain explicitly pending.
- [x] Apache-2.0 license, separately licensed document notices and locked dependency inventory are included.
- [x] Initial provenance is reviewed with owner confirmation of publication permission and no unlisted/private additions; see `docs/development/source-provenance.md`.
- [x] Root contributor/security/support/governance policies, issue/PR forms and roadmap are prepared and locally checked.
- [ ] Actual public maintainer identities, working private contacts and host-specific community/reporting features are verified.
- [ ] Package metadata, clean wheel/sdist installation, version/upgrade policy and release/rollback procedure are verified.
- [ ] GitHub-specific protections, workflows and registry identities are verified at the publication step.
- [x] Personal email is absent from this initial publication history/refs; original development history and a verified recovery bundle are preserved privately. Recheck new commits before a push.
- [ ] The project owner agrees the first-release scope is complete and authorizes public publication.

## Commercialization

Preserve a useful Apache-2.0 local core, portable case/result formats and clean execution interfaces. Record possible future managed execution/team workflows in design notes. Do not implement billing, accounts, tenancy, enterprise identity, paid pilots, sales flows or a hosted runner as part of this first project completion.

## Effort and planning

The detailed blueprint's earlier core/public-quality estimate was 260–404 engineering hours. It predates the approved local browser UI. UI implementation/browser verification, a verified model-assisted suggestion route and complete launch polish add work; re-estimate after the UI build contract and provider choice are settled. There is no agreed calendar deadline or promise based on that range. Internal checkpoints exist to reduce rework; they are not separate public releases.

## What stays deferred

Universal trace import, arbitrary checkpoint restoration, general multi-agent concurrency, agent browser automation, a vector database, a general observability dashboard, plugin marketplace, autonomous code repair/merge, and cloud/SaaS operations. The focused local browser UI is included in the first-release scope. Add other capabilities only through a later scope decision after the complete initial product is working.
