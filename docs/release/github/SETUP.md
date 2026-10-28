# GitHub setup and verification

Updated 28 October 2026. The owner separately approved private repository creation,
source push, Actions verification and merges of PRs #3, #4 and #5. The repository is
**private**, with `main` at `97994307fbc19edd2e61fed47f4edaff43046912` passing
[hosted CI](https://github.com/adreno-abhi/fail2test/actions/runs/40645352245).
No public visibility, tag/release or PyPI publication has been authorized or performed.
Approval between steps in [PLAN.md](../../../PLAN.md) still applies.

## Verified host state and remaining checks

- Private repository/default `main`, maintainer push/merge access, noreply commit identity,
  rendered README/community-file navigation and successful Actions execution are observed.
- Six Ubuntu 22.04 / Windows Server 2022 jobs cover Python 3.12–3.14. The Windows quality
  job passes Chromium tests, docs/types/lint, build, cold-cache package smoke and installed
  CLI/browser/native acceptance. `ci-complete` succeeds for the exact merged revision.
- Included Actions quota and an existing zero-paid-usage stopping budget were verified;
  no paid plan or budget change was made. Repository action allowlisting, full SHA pinning,
  read-only tokens and seven-day retention were applied. See [host evidence](../../development/hosted-ci.md).
- GitHub's UI states that rulesets will not be enforced on this private Free-plan target.
  No unenforced rule is presented as protection. Apply supported protection at approved
  public setup; do not buy a plan to make the checklist pass.
- Private vulnerability reporting, public contributor access, final issue-form rendering,
  security-feature availability/configuration and final owner acceptance remain open.
  Account recovery/2FA are owner-held checks, not facts inferred from repository access.
- Read-only security inspection on 28 October found dependency graph, Dependabot alerts
  and security updates off. Enable available free controls in an approved host step and
  verify actual coverage; see the [final review](../../development/final-release-review.md).
- Two Dependabot PRs remain unmerged; the passing source candidate does not include them.

The original preparation decisions below remain the setup specification. Statements about
the initial lookup or source snapshot describe that dated stage, not current absence of a repo.

## Confirmed decisions

| Item | Decision / evidence |
|---|---|
| Destination | `adreno-abhi/fail2test`, explicitly confirmed by the owner |
| Maintainer | Abhijeet, `@adreno-abhi`; connected profile ID 16892619 |
| Initial repository lookup | Returned 404 before private creation; superseded by the verified private repository |
| Personal email | Do not publish it as a contact; defer a separate project mailbox |
| Security reporting | GitHub private vulnerability reporting; enable and verify on the actual public repository |
| Conduct | GitHub platform abuse reporting; no private project mailbox or independent conduct team |
| Human first use | Owner confirmed the guided sample UI flow through saving export; timing/independent adoption unmeasured |
| Package registry | No PyPI account/name reservation or publishing is included in this step |

## Privacy prerequisite before any push

The original private development history contains a non-`noreply` author/committer address.
Its value was not copied into this record. The owner approved preserving that history locally
and creating this **separate publication repository** from tracked source files, without
copying any development Git metadata. The original history was not rewritten. A verified
private Git bundle preserves all 18 development commits and both original branch refs.

This checkout starts with a fresh `main` root commit using the ID-based GitHub form
`16892619+adreno-abhi@users.noreply.github.com`. Global Git settings were not changed.
Verify the exact address against GitHub email settings before publication; it is attribution,
not a monitored mailbox. The [provenance review](../../development/source-provenance.md)
records the owner's permission/no-private-material confirmation. Earlier development
commit IDs in verification documents refer to the retained private history, not public commits.
See the [publication-history record](../../development/publication-history.md).

Before pushing, check the exact branch/tag graph and blob contents for personal addresses,
credentials and private artifacts. Never use `--mirror`, `--all` or `--tags` indiscriminately:
private backup refs must stay local. Check commit trailers and attribution text as well as
author/committer fields. Do not fabricate DCO sign-offs, change attribution rights or delete
the private recovery copy. `history_privacy_verified` covers only this checked initial snapshot;
repeat the check for new commits/refs before pushing. It does not describe the private original.

## CI files prepared

[`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml) runs on the private repository.
Its exact merged-source verification is linked above.

- Matrix: Ubuntu 22.04 / Windows Server 2022 hosted runners × Python 3.12, 3.13, 3.14;
  core/native/HTTP suite with browser tests explicitly excluded.
- Windows/Python 3.13 quality job: full suite including installed Chromium, lint, format,
  mypy, strict docs, community/inventory checks, build, isolated wheel/sdist smoke and
  installed CLI/browser/native acceptance.
- Stable observed check: **`ci-complete`**. It fails unless the entire test matrix and
  quality job succeed. Requiring it on the branch remains a separate host-protection check.
- Read-only contents permission; checkout credentials not persisted; dependency caches
  disabled; bounded concurrency and job timeouts. Only `push`, ordinary `pull_request` and
  manual triggers. No privileged PR trigger, self-hosted runner, publishing token or provider key.
- No artifact upload, release trigger, deployment, registry publishing or auto-merge.
  Set short host log/artifact retention (proposed seven days) at setup.

Checkout v6.1.0 and setup-uv v10.3.1 are pinned to full upstream tag-resolved commit SHAs.
The reviewed inputs match their action metadata. uv stays at the locally verified 0.10.9.
Hosted runner images differ from local Windows 11/Ubuntu WSL2; both scoped results are recorded.
No Linux browser support is claimed by this workflow. Local YAML/actionlint checks are not
evidence that a hosted job passed.

[`.github/dependabot.yml`](../../../.github/dependabot.yml) prepares weekly grouped `uv`
updates (at most three open PRs) and monthly grouped Actions updates (at most two). Updates
require review; lock changes must refresh the license inventory and rerun compatibility.
Dependabot's uv tooling can differ from our pinned version, so check lock compatibility too.
The [CODEOWNERS draft](CODEOWNERS) names the confirmed maintainer; move it into `.github/`
only after verifying write/admin access. Do not require self-approval from the sole owner.

## Host configuration to apply only in an approved setup step

1. Confirm account ownership, recovery and two-factor authentication with the owner. Verify
   the repository is absent or resolve any collision without overwriting an existing repo.
2. Agree on the exact privacy-safe branch, repository visibility, initial push and spending
   limits. A private host-validation repo, if chosen, needs separate approval; use only
   included CI quota, with no approval for paid overages. Do not initialize a conflicting
   README/license or overwrite remote history. Default branch is `main`.
3. Verify Issues/templates, license/community rendering and actual owner access. Restrict
   Actions to reviewed dependencies, default `GITHUB_TOKEN` to read-only, require approval
   for untrusted outside-contributor runs, and configure short retention. Add no model secrets.
4. Run all CI checks on the prepared source. Verify the actual job results and artifact
   acceptance, then require `ci-complete` on `main`. Use PRs, block force pushes/deletion,
   require resolved conversations and avoid paid/unsupported rule features. The initial
   sole maintainer uses **zero required external approving reviews**, with no mandatory
   CODEOWNERS approval. Increase this when another consenting maintainer can review.
5. Enable available dependency alerts/graph, secret scanning and push protection; record
   actual availability and results rather than assuming file presence enables them. A ruleset
   may depend on plan/visibility; do not buy an upgrade to make a checklist green.
6. Private vulnerability reporting is a **public-repository feature**. Its host verification
   cannot honestly be marked complete while the target remains private. Before any approved
   transition to public, review that limitation with the owner and plan immediate enablement
   and verification. Do not announce a working report route before verifying it. The
   publication gate remains closed until all its facts are actually verified.
7. Review current policies/provenance and get explicit owner acceptance of the exact source
   candidate and destinations. Public visibility, initial push, release/tag creation and
   package publication each remain outside this local preparation's authorization.

## Validation record

Upstream pins and inputs were read from the official repositories. actionlint **1.7.12**
was downloaded into ignored local tooling and its Windows archive SHA-256 checked against
the release digest before use. Workflow syntax/expression validation passed (optional
shellcheck/pyflakes executables were not installed). Local publication checks intentionally
continue to fail for pending host/contact verification and final
owner acceptance. No private test report or personal address is embedded in these files.

Local Windows/Python 3.13.5 verification for this preparation: **192 tests passed**, zero
skips, **88% combined coverage**; lint, format, mypy, strict docs, community structure and
82-package inventory consistency passed. Isolated core/source/native artifact smoke and
installed CLI/browser/native acceptance passed without provider calls. Packaging checks
also require the CI, Dependabot and setup files in the source archive. These local results
do not mark any GitHub-hosted check or security feature as verified.

## Primary references

- [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use)
- [Checkout v6.1.0 metadata](https://github.com/actions/checkout/blob/d23441a48e516b6c34aea4fa41551a30e30af803/action.yml)
- [setup-uv v10.3.1 metadata](https://github.com/astral-sh/setup-uv/blob/18d369b23da25a81e9458561248e1aafff6a70fa/action.yml)
- [Dependabot ecosystems](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories)
- [Ruleset plan/visibility limits](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/report-privately)
- [GitHub abuse reporting](https://docs.github.com/en/communities/maintaining-your-safety-on-github/reporting-abuse-or-spam)
- [GitHub commit email formats](https://docs.github.com/en/account-and-profile/reference/email-addresses-reference)
