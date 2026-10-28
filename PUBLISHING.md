# Publication and release checklist

Updated 28 October 2026. The owner explicitly authorized public source launch of
[adreno-abhi/fail2test](https://github.com/adreno-abhi/fail2test), reporting/protection settings,
CODEOWNERS and the necessary documentation PR/CI/merge. Tags, GitHub releases, PyPI and paid
or hosted services require separate approval. See the [public launch record](docs/development/public-launch.md).

## Completed public-source prerequisites

- [x] Version 0.1.0 package/runtime/lock metadata and release notes; schemas remain 0.1.
- [x] Main `9976745` passed six Windows/Ubuntu Python jobs, 211 tests including Chromium,
  archive/package checks and installed acceptance in [run 40655108733](https://github.com/adreno-abhi/fail2test/actions/runs/40655108733).
- [x] Scoped privacy/history/provenance/license review; owner confirms publication rights.
  Original development/recovery files stay local; clean history uses the noreply identity.
- [x] Owner accepts the supported workflow and unmeasured independent onboarding uncertainty.
- [x] @adreno-abhi identity/admin access verified; owner confirms 2FA and retained recovery.
- [x] Public visibility and [private vulnerability reporting](https://github.com/adreno-abhi/fail2test/security/advisories/new) verified.
- [x] Main requires PRs, GitHub Actions ci-complete, up-to-date branches and resolved conversations;
  settings apply to administrators. Force pushes/deletion and bypass are disallowed. No outside
  approvals or self CODEOWNER approval is required for the solo maintainer.
- [x] Dependency graph, vulnerability/malware alerts and security-update PRs enabled.
- [x] Three contributor forms and actual PR template render; activate verified maintainer CODEOWNERS.

The documentation PR must pass required CI before merging. Public source-install checks and
the final public main SHA are recorded with launch completion. No absent run is inferred as
a pass. Publication flags in [publication.json](docs/release/publication.json) record scoped
evidence and owner confirmation, not automatic live-host, legal or security certification.

## Later tag/release or registry publication — separately authorized

1. Approve the exact final commit/version and destinations. Public source does not reserve a
   PyPI name or authorize an upload.
2. Run relevant CONTRIBUTING checks and hosted CI from a clean checkout. Build/inspect/scan
   exact archives and record SHA-256 hashes. Use clean Git bytes for reproducible source
   archives; worktree newline conversions can change their hashes. Preserve audit/recovery
   files outside publication inputs.
3. Review dependency/license and compatibility changes. Do not substitute an older green
   revision for a changed candidate or replace a published artifact silently.
4. If PyPI is approved, verify registry identity and trusted publishing/OIDC without a
   long-lived repository token. Do not imply registry attestations already exist.
5. Publish only approved tags/releases/artifacts; verify public installation and the key-free
   broken/fixed/export path. Contributor CI stays free of provider/publishing credentials,
   with read-only tokens, pinned actions and no privileged PR execution.

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
