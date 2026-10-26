# Documentation, community adoption and launch

## Documentation acceptance standard

Every advertised workflow has a tested example, explicit prerequisites, output and failure explanation. Proposed features are labeled roadmap/experimental. New users must be able to distinguish trace inspection, fixture regression and live-model evaluation without reading internal architecture documents.

## Documentation map

| Category | Required pages | Validation |
|---|---|---|
| Front door | README: problem, small demo, installation, quickstart, scope, license, links | New-user walkthrough; badges correspond to real jobs |
| Tutorial | Key-free duplicate-refund failure to passing fix | Clean-env CI and external first-time user trial |
| How-to | Configure runner, import trace, review/sanitize, write rule, reduce case, export pytest, run CI | Commands exercised against maintained examples |
| Explanation | Controlled dependencies, why assertions require review, playback versus regression, reduction limits | Claims linked to contracts/tests |
| Reference | CLI, config, Python interface, case/result schemas, errors, compatibility, limits | Generated/help/schema parity checks |
| Integrations | Exact LangGraph setup and supported versions; future imports with loss maps | Adapter conformance jobs |
| Troubleshooting | Unknown request, nonreproduction, dirty revision, secret warning, timeout, unsupported async/concurrency | Each entry links to a negative test/example |
| Community | Contributing, governance, support, security, roadmap, RFC/ADR process | Real contacts/permissions and regular review |
| Release | Changelog, upgrades, deprecations, migration, verified package installation | Release smoke evidence |

Keep reference generation minimal and checked into the docs build as needed. Do not duplicate command behavior across hand-maintained pages without a parity check. CLI output should support copyable fixes and stable machine codes rather than stack traces alone.

## README structure at implementation

1. One-sentence problem and outcome.
2. A small real demonstration or terminal recording from the maintained example.
3. Three-step key-free quickstart using a published version.
4. What the generated test executes and what it does not establish.
5. Supported Python/framework matrix and status badge.
6. Example exported pytest code and fixture.
7. Documentation, contribution, roadmap, security and license links.
8. Transparent commercial/sponsorship statement only when applicable.

No invented customer logos, star-history chart, Discord invitation, benchmark score, “production ready” badge or package install command that does not work. The blueprint itself must remain labeled a plan.

## Distribution strategy

The strongest organic loop is a useful test entering a team repository and being run/reviewed by other engineers. A video is an introduction, not the whole adoption strategy.

Prioritize: Python/pytest/agent-engineering communities, framework-specific example contributions, trace-platform integration guides, public synthetic failure cases and thoughtful maintainer conversations. Outreach is proposed work; this plan does not authorize unsolicited messages from tooling.

Make examples runnable without a model account. Publish the exported artifacts and methodology behind a demo. Offer a short path to add a custom failure case so contributors can participate before learning runtime internals. Preserve portable fixtures and readable test output rather than requiring a hosted account to share a case.

## One complete public launch

### Local completion

Initially the project owner and AI assistant build the full agreed scope in the dedicated local Git repository. Use internal correctness checkpoints and local commits, not public alpha/beta releases. The owner verifies the full clean-install workflow, error paths and launch documentation. External contributor recruitment and paid validation are not preconditions.

### Publication preparation

When locally complete, confirm owner/name, real reporting contacts and publishing permissions. Review the release checklist, set up any needed private host verification explicitly, and make the finished project public only after owner authorization. Publish the supported scope, key-free tutorial, license, roadmap and contribution paths together.

### After the public release

Welcome contributors and usage feedback, triage reproducible bugs, improve setup friction and prioritize maintenance. Recruit external users at this point to evaluate retained tests and later workflow needs. Commercial validation remains a separate future decision.

## Metrics

| Funnel | Measurement | Pitfall |
|---|---|---|
| Discovery | Docs visits, demo engagement, repository interest when voluntarily observable | Views are not activation |
| Activation | First complete broken/fixed reproduction | A successful import is insufficient |
| Value | Reviewed test retained and rerun | Generated test count can reward useless output |
| Retention | Repeat use across a later change/incident | One-time demos overstate sustained utility |
| Community | Useful issues, merged contributions, returning contributors | Raw PR counts ignore review burden |
| Commercial | Scoped paid pilots, ongoing usage, measured saved work | Pricing-page competitors do not validate new demand |

Default product telemetry remains off/absent. Use optional surveys, user interviews, public GitHub activity and opt-in redacted reports. Do not collect customer traces merely to improve a growth dashboard.

## Maintenance commitments

Document release cadence as best effort until capacity is established. Keep public decisions and roadmap updates on GitHub. Treat docs, support and security triage as real delivery work. Add a second maintainer and recovery process before making enterprise continuity promises.
