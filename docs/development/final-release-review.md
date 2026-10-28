# Final security and release-readiness review

28 October 2026. Reviewed source: merged `main`
`97994307fbc19edd2e61fed47f4edaff43046912`. This review updates documentation only;
it does not change runtime behavior, dependency versions, repository settings or visibility.
The repository remains private. This is a maintainer engineering review, not an independent
penetration test, legal opinion or publication authorization.

## Decision

The supported fixture workflow has no newly identified blocking code defect in this review.
The earlier source-archive privacy defect and case-diagnostic friction have been corrected
and verified on merged `main`. **Public launch remains pending**, because the exact release
candidate, live host controls and owner acceptance are not yet complete. Passing tests and
an advisory scan do not prove absence of vulnerabilities or demand for the product.

## Source and workflow evidence

[Main CI run 40645352245](https://github.com/adreno-abhi/fail2test/actions/runs/40645352245)
passed all six Ubuntu 22.04 / Windows Server 2022 jobs on Python 3.12–3.14, the Windows
quality/browser/package job and `ci-complete`. The quality job passed **211 tests**, including
Chromium, with **89%** runtime coverage, plus types/lint/docs, archive guards, clean-cache
installed package checks and installed CLI/browser/native acceptance. This evidence belongs
to the stated revision; a version or source change needs candidate verification again.

| Boundary | Review result and limits |
| --- | --- |
| Imported evidence | Bounded JSON, duplicate-key/non-finite/depth checks and strict declarative rules. Cases cannot select executable runner imports. Sanitization is best effort; arbitrary sensitive text and key names can remain in evidence. Inspect artifacts before sharing. |
| Current-code execution | Fixture transports use exact matching and latch unsupported/missing/swallowed interactions. Complete execution is required for baseline reproduction. Regression exports execute the configured current application, not historical playback. Application code, configuration, dependencies and pytest plugins remain trusted. |
| Review and export | Review/baseline bind case digests. Exports use a fixed source template with Python literal escaping and require reproduced failure. Digests authenticate content consistency, not identity. Runner hashes cover only the configured module. |
| Local UI | Loopback-only binding, ephemeral session token, exact Host/Origin, bounded requests, static allowlist, restrictive response headers, text rendering, contained paths and link/junction rejection. Mutation jobs serialize. These controls do not isolate hostile local processes or prevent filesystem races caused by a trusted local user. No remote/shared-host deployment is supported. |
| Optional providers | Exact preview/consent precede sending; validated profile snapshot also selects credentials. Redirects/proxies are suppressed, payloads/responses bounded, proposals validated and left unapproved. Socket timeout is not an overall deadline. Free routing cannot guarantee upstream billing/privacy; no paid fallback or runtime download occurs automatically. |
| Diagnostics | Case-boundary errors expose bounded schema-owned fields and fixed text. Direct Pydantic and low-level in-process APIs retain normal Python behavior and must not be presented as a sanitization boundary. |
| Build/CI | Explicit source inclusion, negative dirty-tree build tests and archive guards protect packaging scope. Actions use reviewed full SHAs and read-only tokens; contributor jobs contain no provider/publishing secrets and use no `pull_request_target`. Unlocked build tools and external package registries remain supply-chain dependencies. |

Relevant implementation and negative coverage: `jsonio.py`, `ingest.py`, `execution.py`,
`supervisor.py`, `workflow.py`, `suggestions.py`, `ui/server.py`, `ui/static/app.js`,
and tests for contracts, execution, ingestion/privacy, workflows, suggestions, UI, validation
diagnostics and package contents. No new behavior or redundant tests were added for this review.

## Dependencies, licensing and privacy

A fresh `pip-audit 2.10.1` query on 28 October reported **zero known vulnerabilities for all
82 exact locked third-party packages**, including the platform-specific entry, using PyPI's
advisory service with `--no-deps --disable-pip --strict`. Only public package coordinates were
submitted; no dependency upgrades or automatic fixes were applied. This excludes other
versions permitted by ranges, unlocked build tools, OS/browser components and future advisories.
The existing license inventory remains a separate metadata/file-hash record, not legal clearance.

Local privacy checks cover tracked files, reachable history objects including commit metadata,
and current wheel/source archive contents. They compare the existing provider key and private
development email addresses in memory and scan token/key patterns; matched values are never
printed. No exact key/private-address match or unexpected private path was found; pattern
candidates were the two deliberately synthetic test canaries in ingestion/provider tests,
including their history/source-archive appearances. Preserve the original
private development checkout, recovery history and quarantined earlier builds locally. Rebuild
and rescan after the final version change; today's artifacts are still `0.1.0.dev0`.

Raw advisory/privacy/check outputs and current artifact hashes are retained only under ignored
`local-artifacts/final-readiness/`. The exact candidate's acceptance record must include its
commit, version, archive hashes and checks rather than borrowing an older green result.

For this documentation-only review, six publication-gate regression tests, strict MkDocs,
repository structure/form checks, license-inventory consistency, rebuild and archive-scope
checks pass. No runtime source or lock changed, so the 211-test result above remains the
merged runtime evidence rather than a newly claimed full-suite run. The publication command
still reports the four expected pending facts; no gate was relaxed to obtain a pass.

## Host findings

Subsequent approved step: the [0.1.0 candidate record](release-0.1.0.md) documents enablement
of the free dependency controls and exact graph coverage. The findings immediately below
retain the earlier review's observed state; public reporting/protection checks remain open.

Read-only GitHub inspection on 28 October confirmed a recognized security policy, but
**dependency graph, Dependabot vulnerability alerts and security updates are off**. The two
existing version-update PRs do not establish vulnerability monitoring and remain unmerged.
Enable the available free dependency security controls in an approved host step; verify actual
state and lockfile coverage rather than assuming GitHub recognizes every dependency.

GitHub documents [private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately)
for public repositories and [rulesets on public Free-plan repositories](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets).
The existing private Free-plan target cannot satisfy those public checks in advance. Keep their
verification flags false. Public transition therefore requires explicit approval of a coordinated
visibility-and-immediate-controls step; do not claim protections exist before verifying them.
No personal reporting mailbox, paid upgrade, third-party app grant or account change is needed.

## Remaining launch sequence

1. **Prepare the release candidate privately.** Recommended first version: `0.1.0`, with honest
   initial compatibility status, rather than a stable-1.0 promise. Align package/runtime version,
   lock metadata, changelog and release notes. Add a concise synthetic workflow visual if useful;
   it must demonstrate the actual UI. Enable approved available free dependency security controls,
   verify maintainer access for CODEOWNERS, review open dependency PRs without automatically
   adopting them, and check issue/PR rendering. Owner confirms account recovery/2FA privately;
   no credentials, recovery codes or personal email are requested.
2. **Verify and approve the exact candidate.** Run relevant quality, hosted matrix, build/archive,
   history/privacy and installed acceptance checks after changes. Owner confirms the scoped
   product and either provides an independent existing-application onboarding trial or explicitly
   accepts the unmeasured usability uncertainty. Tutorial ten-minute/integration thirty-minute
   figures remain targets, not claims. A guided sample and synthetic extra application are useful
   evidence but do not constitute independent adoption, virality or willingness-to-pay evidence.
3. **Approve public GitHub launch separately.** Make the exact repository public, immediately
   enable/verify private reporting and supported `main` protections: PRs, `ci-complete`, resolved
   conversations, blocked force pushes/deletion, and no required outside reviewer for the solo
   maintainer. Check public community/forms/reporting links, update policies to verified status
   and only then close the pending publication facts. No announcement of a working reporting
   route before verification. There is a transition interval before public-only controls exist.
4. **Create the approved GitHub tag/release separately**, after the launch checks. Verify public
   clone/install and broken/fixed/export workflow. PyPI, a hosted service, billing and
   commercialization are optional later work, not prerequisites for the user's GitHub-first goal.

Independent onboarding is a product uncertainty with an explicit owner-acceptance alternative,
not a reason to fabricate another human trial or expand the first release into universal tracing.
The publication gate remains closed for contacts, private reporting, broader host verification
and final owner acceptance. This document grants none of those approvals.
