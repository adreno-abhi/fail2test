# Public source launch

28 October 2026. The owner accepted the verified 0.1.0 scope and unmeasured independent
onboarding uncertainty, confirmed two-factor/recovery readiness, and explicitly authorized
public visibility plus security settings and necessary ownership/documentation PR updates.
The source project is public; no tag, release or PyPI upload is part of this step.

The owner completed GitHub's reauthentication. Public visibility was verified in the host
UI and connected repository metadata. The maintainer's admin access was verified before
activating `.github/CODEOWNERS`. No collaborator/app access or personal contact email was
added. Original development history, recovery bundles and credentials stay outside this
publication repository and its package inputs.

## Verified controls

- Private vulnerability reporting is enabled; an anonymous view of
  [advisories](https://github.com/adreno-abhi/fail2test/security/advisories) exposes
  **Report a vulnerability**. No fabricated report was submitted. GitHub sign-in may be required.
- Classic main protection applies to one branch on the public Free-plan repository.
  Saved settings require PRs, `ci-complete` from GitHub Actions, up-to-date branches and
  conversation resolution, including administrators. Force pushes/deletions are disallowed.
  Outside approvals and self CODEOWNER review are not required for the solo maintainer.
  The launch PR must satisfy these controls without bypass.
- Dependency graph, vulnerability/malware alerts and security-update PRs remain enabled.
  This does not claim CodeQL, secret scanning, independent penetration testing or every
  possible security feature is configured. No paid/AI-credit feature was enabled.
- All three contributor forms render required fields and privacy instructions; the chooser
  restricts blank issues to maintainers. Actual PR creation verified its template/policy links.

## Source and acceptance

Version 0.1.0 at `9976745ef81dfa1314a998274c5481982ec44eb8` passed
[main CI 40655108733](https://github.com/adreno-abhi/fail2test/actions/runs/40655108733):
six platform/Python jobs, 211 full tests including Chromium, 89% coverage, archive guards,
clean-cache wheel/source/native checks and installed CLI/browser/native acceptance.
The launch documentation PR changes no runtime code, dependency version or fixture/review
semantics; its own required CI must pass before merge.

Public-install trials disable the Git credential helper and terminal prompts, install the
locked source checkout and exercise the documented broken baseline, broken/fixed exits and
exported pytest. Final clone/fetch results, public main SHA, CI links and screenshots are
recorded in ignored `local-artifacts/launch-acceptance/` and the launch PR's completion
description. Automated operability does not establish independent human onboarding timing.

Historical preparation records retain their dated scope. Current public policies and
publication facts supersede earlier private-status statements. Public source availability
does not imply a tagged release, package-registry identity or authorization to create either.
