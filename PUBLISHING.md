# Publication and release checklist

This is a local checklist, not permission to create a repository, push, upload a package or
configure an account. The owner reviews one agreed step at a time through publication.
The repository and remote are configured privately; merged `main` has passed hosted CI.
No public release or package-registry publication has occurred.

**Open release blocker:** the [developer adoption review](docs/development/developer-adoption-review.md#packaging-blocker-reproducible-finding-and-proposed-correction)
found that source-build selection can include ignored local artifacts. Review builds were
quarantined locally. Packaging configuration and negative archive checks must be fixed and
new artifacts verified before any package release. A clean Git status or prior CI pass does
not satisfy this boundary.

The owner confirmed `adreno-abhi/fail2test` and `@adreno-abhi` and chose not to publish
personal email. See the concrete [GitHub setup preparation](docs/release/github/SETUP.md),
including reporting routes, CI and solo-maintainer settings. This standalone publication
checkout has a checked clean history; the private development history must stay local.
The [source provenance review](docs/development/source-provenance.md) records the owner's
confirmation. The [private first-push plan](docs/release/github/FIRST_PUSH.md) is retained
as history; its private creation/push was separately approved and completed. See the
[hosted CI record](docs/development/hosted-ci.md). Public visibility, tags/releases and
package publication still require their own explicit owner approval.

The [local audit record](docs/development/release-audit.md) documents the engineering checks
already completed and their limits. Rebuild, rescan and approve the final publication
candidate after host setup; the local audit does not satisfy human or host-only gates.

Run `uv run python scripts/check_repository.py` for local file/link/form checks and
`uv run python scripts/check_repository.py --publication` for the explicit pending-facts gate
in [docs/release/publication.json](docs/release/publication.json). Its booleans record human
verification, not automatic proof of the corresponding fact. Never mark them true merely
to get a green check. Missing facts and false/non-boolean values fail the gate.

## Identity, contacts and community

- [x] Owner confirms GitHub owner/repository and public maintainer identity in MAINTAINERS.md.
- [x] No personal reporting email; use GitHub private vulnerability reporting for security
      and GitHub platform reporting for abusive conduct, with project-channel limits explicit.
- [ ] Verify private security reporting on the actual host; no mailbox is required by policy.
- [ ] Replace the explicit local contact-status text with verified public instructions in
      MAINTAINERS.md, SECURITY.md and SUPPORT.md; verify CoC reporting links still work.
- [ ] Verify private vulnerability reporting on the actual public repository. A file alone
      does not enable it. If host setup needs an earlier private repo, obtain owner approval.
- [x] State how conflicts involving the sole maintainer are handled; do not claim an
      independent panel or recovery maintainer that does not exist.
- [x] Review contribution/DCO policy, initial source provenance and third-party attribution;
      owner confirms publication permission and no unlisted/private material. No sign-off is fabricated.
- [ ] Validate GitHub's rendered issue forms, PR template and community profile after setup.
- [ ] Add CODEOWNERS only for verified, consenting handles with the appropriate repository access.

## Quality and compatibility

- [x] Owner confirms the guided sample UI flow through saving export; see
      [walkthrough record](docs/development/owner-walkthrough.md).
- [ ] Measure independent human onboarding/integration against PLAN.md's timing targets;
      the guided sample confirmation is not such a measurement.
- [x] Establish the scoped Python/OS/native-dependency matrix with actual local and hosted
      results; see [compatibility](docs/site/compatibility.md). Additional platforms remain unclaimed.
- [x] Exercise the key-free tutorial, native integration, browser workflow, error paths and
      generated pytest broken/fixed behavior from built artifacts. Independent human integration
      remains unmeasured; see the [developer review](docs/development/developer-adoption-review.md).
- [ ] Review untrusted input, privacy, provider consent, session/path controls and dependency risk.
- [ ] Check documentation/schema/CLI consistency and known limitations. No fabricated badges,
      benchmarks, usage numbers, support SLAs or model-quality guarantees.

## Prepare an immutable candidate

1. Select an appropriate initial release version; update source/package version and changelog
   together. No public staged alpha/beta rollout is planned. Do not claim a stable 1.0 contract
   simply because the agreed workflow is complete.
2. Update and review the locked [dependency inventory](THIRD_PARTY_NOTICES.md), third-party
   notices and license exceptions. Recheck notices if vendoring/bundling changes.
3. From a clean checkout run the commands in CONTRIBUTING.md, including browser checks when
   relevant, strict docs, `python scripts/check_repository.py`, and package smoke tests.
4. Build wheel/sdist, inspect contents and metadata, scan the candidate/history for unintended
   secrets or private artifacts, and record their SHA-256 hashes with the acceptance record.
   Resolve existing personal-email commit metadata before **any** push, including private
   host validation. Preserve private recovery history; publish only explicitly reviewed refs.
5. Owner approves the exact candidate and publication destinations. Confirm GitHub and package
   name availability/rights at that time; the local project name is not a reservation.

## GitHub and registry setup — separately authorized

- Configure the real remote, repository visibility, least-privilege access, recovery and
  account protection. Enable verified branch protections and CI checks on the actual host.
- Keep untrusted PR jobs free of provider/publishing credentials; do not use privileged
  `pull_request_target` execution for contributor code. Pin third-party workflow actions to
  reviewed commit SHAs when adding executable workflows.
- A future CI matrix must run only declared/tested environments, install Chromium explicitly
  for browser jobs, avoid live providers and enforce bounded job/artifact retention.
- Package publication, if approved, uses a verified PyPI identity and configured trusted
  publishing/OIDC or another owner-approved method. Verify attestations/provenance on the
  actual registry; never add a long-lived publishing token to the repository.
- Publish the approved tag/release/artifacts, then independently install the public artifact
  and rerun the documented smoke path. Verify links and private report entry points.

The CI workflow and Dependabot configuration are active on the private repository. CI on
merged `main` revision `345eced` passed. No executable release/publishing workflow is supplied.
Further pushes, releases or visibility changes remain subject to the agreed owner-approved steps.

## Recovery and compatibility policy

Never silently replace published artifacts. For a broken release, document the issue, stop
further promotion, yank an affected package when appropriate and release a new fixed version
with upgrade/rollback guidance. Coordinate security disclosures privately first. Record which
versions and case schema are affected; migrations write new artifacts and preserve originals.

Users can stop the UI, disable optional suggestion profiles and pin a previously verified
package/dependency set. Keep old case files under version control; review is content-bound.
The package and case schema are versioned separately. Until a stable compatibility policy is
confirmed, rely on the release's stated support matrix and migration notes, not undocumented
private modules. Hosted support, billing, team tenancy and commercial SLAs remain out of scope.
