# Fail2Test roadmap

**Status:** private pre-release preparation; the fixture workflow and hosted CI pass.
No public release has shipped. Public launch follows the agreed acceptance checks and
explicit owner approval. See the [developer adoption review](docs/development/developer-adoption-review.md).

## Initial public release

- [x] Fix ignored-local-file source archive inclusion and verify negative archive checks
  locally and on merged main; see the [correction and acceptance record](docs/development/packaging-scope-fix.md).

- [x] Python package, CLI and runner contract.
- [x] Neutral serial JSON import, sanitization and completeness reporting.
- [x] Reviewable rule proposals, with a key-free deterministic route.
- [x] Optional model-assisted proposals with provider profiles, exact payload preview and explicit consent.
- [x] Focused local browser UI for evidence, review, results, reduction and export over the existing engine.
- [x] Browser workflow, keyboard/responsive checks, local-server controls and clean-install bundled assets.
- [x] Fresh application execution against strict model/tool fixtures.
- [x] First-release rule set and incomplete/error handling.
- [x] Bounded input reduction; broader fixture reduction remains under review.
- [x] pytest export, portable cases and JSON/console reports.
- [x] Focused LangGraph graph-factory helper and runnable synthetic examples.
- [x] Native synchronous chat/tool replacements for supported existing LangGraph applications.
- [x] Measure automated installed CLI/UI/native paths and document integration changes/limits.
- [x] Complete clean-install tutorial and automated broken/fixed/export acceptance.
- [x] Verify Windows/Ubuntu WSL Python 3.12–3.14 and correct tested dependency lower bounds.
- [ ] Human first-use trial or owner acceptance of the remaining usability uncertainty.
- [x] Hosted Ubuntu 22.04 / Windows Server 2022 CI on Python 3.12–3.14; Windows browser/package acceptance.
- [ ] Additional platforms/browser environments before claiming broader support.
- [x] Local contribution/security/support/governance policies, issue/PR forms and license inventory.
- [ ] Verify public maintainer/contact details, private reporting and GitHub-rendered community files.
- [ ] Publishing/release checks and final owner review.

These are work items for one complete initial release, not a public alpha/beta sequence. Internal implementation order is in [PLAN.md](PLAN.md).

## After publication

The [developer adoption review](docs/development/developer-adoption-review.md) identifies
pre-launch improvements separately from future features. In particular, safe field-level
case diagnostics are implemented and verified on merged main; see the
[verification record](docs/development/safe-case-diagnostics.md). The
[final release review](docs/development/final-release-review.md) tracks remaining launch
checks and the independent existing-application trial or owner acceptance of its uncertainty. Automatic
evidence capture, vendor importers and async execution are candidates, not implemented promises.

Welcome contributions through documented issues/PRs. Prioritize compatibility, reproducible bugs and real user needs. Evaluate additional importers/frameworks and execution modes only when there is a maintainer and acceptance evidence. Publish a supported-version and deprecation policy as the project matures.

Commercial features remain future possibilities, not current roadmap commitments. The local core and portable fixtures are intended to remain useful open source functionality.
