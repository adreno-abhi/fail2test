# Compatibility and first-use acceptance record

26 October 2026, owner-approved local step. See the build/verification contract in
`docs/planning/COMPATIBILITY_ACCEPTANCE.md`, [exact counts](compatibility-results.json) and
[user-facing matrix](../site/compatibility.md). No remote, publication, provider call, account
setting or AI runtime was involved. Public contact details remain deferred by the owner.

## Verified matrix

Windows Python 3.12.13 and 3.14.3 each passed 182 selected core/native/HTTP tests. Windows
3.13.5 passed **188 tests**, including six real Chromium tests, at **88% combined coverage**.
Ubuntu 20.04.6 WSL2 passed 182 selected tests on each of 3.12.13, 3.13.12 and 3.14.3.
Each selected suite had zero failures/errors/skips. Linux source was extracted from the built
sdist into the Linux filesystem, using Linux interpreters rather than Windows Python.

Docker's engine was unavailable, so the existing Ubuntu WSL distribution was used. No Docker
service or OS upgrade was started. Isolated managed CPython/uv tooling downloads were needed;
these are not AI runtimes/models. macOS, ARM, Linux browsers and hosted CI remain unverified.

## Lower-bound diagnosis and correction

The original direct-minimum combination (Pydantic 2.10.0, Typer 0.15.0, LangGraph 1.0.0,
langchain-core 1.0.0, rfc8785 0.1.4, pytest 8.3.0) produced **2 failed, 180 passed**:

- CLI help raised missing `ctx` in `Parameter.make_metavar`. Changing only Typer to 0.16.0
  made the existing CLI feedback test pass, consistent with the upstream
  [Click compatibility notes](https://typer.tiangolo.com/release-notes/).
- Native baseline execution was incomplete with `RUNNER_IMPORT_FAILED`. A minimal import of
  the synthetic runner showed prebuilt code importing `ExecutionInfo`/`ServerInfo` absent from
  the older graph runtime. Graph 1.0.10 and 1.1.0 probes also failed with that selected prebuilt.
  Graph 1.2.0 resolved a coherent prebuilt 1.1.1/checkpoint 4.x set; installed metadata required
  langchain-core >=1.4.0. The native example passed with that combination.

Floors now require Typer >=0.16, LangGraph >=1.2 and langchain-core >=1.4. The entire corrected
direct-boundary suite passed **182 tests** on Windows/3.12.13; legacy Typer emitted two upstream
Click deprecation warnings. Existing tests and all safety/fixture assertions were preserved.
The primary locked package versions did not change; lock metadata and license evidence were
refreshed. This does not establish compatibility for every transitive/version combination.

## Clean installs and automated effort measurements

`scripts/acceptance.py` installs a fresh wheel outside the checkout, verifies import origin
and removes provider credentials from child environments. It exercises CLI init/import/inspect/
deterministic proposals/review/baseline/broken/fixed/reduce/export/pytest. The browser drives
the actual clean installed server, with requests confined to loopback. Native dependencies
are added after verifying the core needs no framework. All example payment calls stay mocked.

Native adoption copies the prepared injection-friendly application and adds its small runner,
TOML and fixtures. A synthetic application bug disables deduplication; the unchanged exported
test must fail with a behavioral assertion, then pass after restoration. Original application
bytes and test digests are checked. The production factory needs zero adoption edits for
this sample, not necessarily for a legacy application.

Ignored JSON reports are under `local-artifacts/acceptance/`. The representative Windows 3.13
trial measured CLI 9.744s, installed UI 6.862s, native workflow 21.357s, total 41.743s. Installed
CLI/native trials also passed on Windows 3.12/3.14 and all three Linux Python versions. These
are single automated wall times, including cache/concurrency effects; human reading, coding,
recording evidence and prerequisite installation were not measured. No speed comparison or
new-developer time guarantee follows from them.

Invalid harness trials were discarded: `uv run` reselected default Python after an earlier
explicit sync; a controller assumed UTF-8 without setting its Windows child's pipe encoding;
text restoration altered line endings. Direct interpreter/native-import assertions, explicit
UTF-8 and byte-preserving edits corrected those harness problems. Only successful verified
trials contribute to the reported evidence.

The [committed trial summaries](first-use-results.json) retain individual wheel identities and
explicit human/provider flags without temporary paths or credentials. Package metadata changed
during the boundary correction; runtime source did not. These hashes identify each measured
trial, not a claim that a later documentation-only rebuild is byte-identical.

## Final checks

- Existing exact CLI/native/browser feedback tests rerun against current development state:
  **11 passed** after the metadata correction.
- Freshly rebuilt wheel metadata rejects explicit `typer==0.15.0` and `langgraph==1.0.0`
  requests in resolver dry runs; the formerly broken combinations are excluded.
- Ruff lint/formatting, strict mypy, strict MkDocs, repository links/forms, lock identity,
  82-package license inventory and Git whitespace checks: PASS.
- Fresh wheel/source installs and native package smoke checks: PASS. The final rebuilt
  artifacts retain the UI, notices, community files and current compatibility scripts/docs.
- No production runtime code or test assertion was altered; the fixes are dependency metadata
  and verification harness behavior. No live provider or payment service was contacted.

## Remaining gates

Automated compatibility and installed CLI/UI/native operability are verified for the documented
matrix. Human first-use targets are not observed: keep `first_use_verified=false` until a
human trial or explicit owner acceptance of that usability uncertainty at final acceptance.
Hosted CI, final security/source-provenance audit, real identities/private contacts and public
publication authorization remain separate steps. Proposed next work is final launch-readiness
review and the owner's product walkthrough before separately approved host setup/publication.
