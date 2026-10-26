# Fail2Test roadmap

**Status:** active local development; a working fixture workflow is implemented. No public release has shipped. The first public release will be published only after the complete agreed workflow and repository checks pass.

## Initial public release

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
- [ ] Host CI and additional platforms/browser environments before claiming broader support.
- [x] Local contribution/security/support/governance policies, issue/PR forms and license inventory.
- [ ] Verify public maintainer/contact details, private reporting and GitHub-rendered community files.
- [ ] Publishing/release checks and final owner review.

These are work items for one complete initial release, not a public alpha/beta sequence. Internal implementation order is in [PLAN.md](PLAN.md).

## After publication

Welcome contributions through documented issues/PRs. Prioritize compatibility, reproducible bugs and real user needs. Evaluate additional importers/frameworks and execution modes only when there is a maintainer and acceptance evidence. Publish a supported-version and deprecation policy as the project matures.

Commercial features remain future possibilities, not current roadmap commitments. The local core and portable fixtures are intended to remain useful open source functionality.
