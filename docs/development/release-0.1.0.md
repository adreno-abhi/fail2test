# 0.1.0 candidate preparation

28 October 2026. Local preparation after review commit `0fce0b0`; the remote remains private
at merged runtime revision `9799430`. No source push, tag, release or PyPI upload is part of
this step. [Release notes](../release/0.1.0.md) describe the complete supported initial product.

## Changes

Package metadata, public `__version__` and the project's lock entry are aligned to `0.1.0`.
The stale Pre-Alpha classifier is removed; no stable-1.0, broad compatibility or staged
public rollout claim replaces it. The changelog explicitly says prepared, not published.
All third-party lock records are byte-equivalent after parsing out only Fail2Test's entry;
all 82 license-evidence rows are unchanged. Inventory collection was refreshed on 28 October
to bind the updated lock digest. No dependency upgrade or new provider request was needed.

## Approved GitHub controls

On the actual private repository, the approved step enabled and verified dependency graph,
Dependabot vulnerability alerts, malware alerts and automatic security-update pull requests.
Updates require review; no auto-merge or automatic dismissal rule was enabled. Existing version
update configuration remains unchanged. Grouping is still controlled by that configuration.
Automatic build-time dependency submission remains disabled; no additional submission workflow,
paid feature, plan, billing change or third-party app grant was introduced.

The graph identifies remote main `9799430` and lists 85 entries: all 82 exact third-party
name/version pairs from the lock, the project's old development entry and both pinned
workflow actions. All five rendered pages were compared with the inventory, including the
platform-specific package. The alerts page reports zero open vulnerability alerts. These are
current detection results, not a guarantee of complete future advisory coverage. The local
all-82-package advisory scan remains separate evidence. The graph still describes the remote
development version until this candidate is approved for push. Raw screenshots and package
comparisons are retained in ignored `local-artifacts/release-0.1.0/`.

## Candidate acceptance

Fresh Windows/Python 3.13.5 verification passed **211 tests**, including Chromium, in 119.03
seconds with **89%** runtime coverage. Ruff lint/format, strict mypy, strict MkDocs, community
structure and the 82-package inventory check pass. Runtime and installed source-checkout
metadata both identify `0.1.0`. This is a fresh local result, not the preceding main CI result.

Built wheel/source checks and installed CLI/browser/native trials follow the documentation
freeze. Their exact artifact hashes, events and outcomes are retained in ignored
`local-artifacts/release-0.1.0/verification.json`, `package-smoke.json` and
`installed-acceptance.json` and reported with completion of this approved step. An absent
record is not a pass. No hosted result for this candidate is claimed before an approved push.
Public reporting/branch protections, broader host/community checks,
independent onboarding or owner acceptance of its uncertainty, and final publication approval
remain pending. The publication gate must remain closed until its facts are verified.
