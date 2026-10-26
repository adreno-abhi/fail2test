# Local security and release-readiness audit

26 October 2026. Runtime revision `a288252`, following compatibility revision `b5eaca6`.
This is a local engineering review, not an independent penetration test, legal clearance,
or publication approval. No provider calls, account changes or AI runtime installation
were needed. The owner deferred public identities and contacts until GitHub setup.

## Finding and correction

`propose()` reconstructed and checked the preview digest, then read the configured profile
a second time to select credentials. A concurrent local configuration edit could therefore
send profile B's credential to profile A's reviewed destination. This requires a trusted
local config edit; imported cases cannot select endpoints or credential sources.

The request now uses the validated profile snapshot already bound to the preview digest
for both credentials and timeout. The regression test edits the profile between preview
and transmission, using two synthetic credentials and a mock transport. It failed with
the wrong credential before the fix and passes afterward. All 32 suggestion tests pass.

## Boundaries reviewed

- Case/trace input remains bounded JSON data with strict declarative rules. Case strings
  cannot select Python imports or executable assertions. Import sanitizes before persistence;
  sanitization remains best effort and requires inspection before sharing.
- Review and baseline records bind exact content. Unsupported, missing or swallowed fixture
  interactions cannot establish a complete passing regression. Generated pytest uses fixed
  source structure and exercises current application code.
- Reduction has bounded attempts/time and requires review of the derived case. Application
  execution has timeout/log-suppression checks; trusted Python code is not sandboxed.
- UI requests require the ephemeral bearer token and exact local Host; mutations also check
  Origin. Workspace containment rejects traversal, symlinks and junctions. Static assets
  are allowlisted, evidence renders as text, and mutation jobs are serialized.
- AI requests require explicit preview consent; remote HTTPS/local loopback policies,
  redirect/proxy suppression, bounded payload/response and strict output validation remain
  in place. Provider failure does not trigger another model or a paid fallback. Credentials
  stay outside case files and browser responses. Socket timeouts are not total deadlines.

Relevant coverage is in `test_contracts.py`, `test_ingest_privacy.py`, `test_execution.py`,
`test_error_paths.py`, `test_workflow.py`, `test_ui_server.py`, `test_ui_browser.py` and
`test_suggestions.py`. This review does not establish isolation against hostile application
code, other processes with the owner's permissions, or a malicious model provider.

## Dependency and artifact checks

`pip-audit 2.10.1`, using its PyPI advisory service, reported **zero known vulnerabilities
for all 82 locked third-party packages**, including the platform-specific Emscripten package.
The audit used exact names/versions from the reviewed inventory, with `--no-deps
--disable-pip --strict`; no dependency code was executed or automatic fixes applied.
Only public package coordinates were queried. The machine's initial marker-filtered export
covered 81 packages; a second marker-free inventory query covered all 82.

This result is time-sensitive and does not audit every version allowed by dependency ranges,
unlocked build tools, Chromium/OS components or future installations. The dependency license
inventory is separate evidence; neither result guarantees absence of vulnerabilities.

Tracked worktree files, all reachable Git history blobs, and wheel/sdist entries were scanned
locally. Checks covered provider/GitHub token patterns, AWS access IDs, private-key headers,
and exact comparison with the owner's existing provider key held only in memory. No owner
key match was found. Pattern candidates were the two deliberately synthetic privacy/provider
test canaries; their appearances in history/source archives were reviewed. No unexpected
environment/key files, Git metadata, dependency environments, raw traces or local artifacts
were found in the tracked paths or archives. Pattern matching cannot detect every secret or
prove all source content is public; owner provenance review remains required.

Raw reports, candidate SHA-256 hashes and the local scan harness are under ignored
`local-artifacts/release-audit/`. Documentation changes alter source-distribution hashes;
rebuild and rescan the exact approved publication candidate at the publication step.

## Verification and remaining acceptance

- Windows Python 3.13.5: **189 tests passed**, zero skips, **88% combined statement/branch
  coverage**, including six Chromium checks. Ruff, formatting, mypy, strict MkDocs,
  repository checks and the 82-package inventory consistency check passed.
- Wheel/source installs outside the checkout passed core, bundled UI and native integration
  smoke checks. Installed-wheel CLI/browser/native acceptance passed again without keys.
  The unchanged exported test detected a reintroduced bug and passed after restoration.
- The earlier [compatibility matrix](compatibility-acceptance.md) remains its dated evidence;
  this focused credential fix was reverified on Windows 3.13, not rerun across every platform.
- A fresh synthetic owner walkthrough workspace was prepared without provider credentials.
  Automated operability/timings do not substitute for human first-use acceptance.

Human walkthrough feedback, initial provenance/rights review, actual maintainer contacts,
host CI/security settings, registry identities and explicit publication authorization remain
pending. The publication gate remains closed. No remote, push or public package was created.
