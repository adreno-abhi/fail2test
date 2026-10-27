# Source-distribution boundary correction

27 October 2026. The owner approved fixing the packaging blocker recorded in the
[developer adoption review](developer-adoption-review.md#packaging-blocker-reproducible-finding-and-proposed-correction),
adding negative archive checks, rebuilding and testing installed artifacts. This step is
local only: no push, visibility change, tag/release, provider call or package publication.

## Reproduction and correction

The original source target used basename/glob-style `include` entries such as `tests/`,
`docs/` and `README.md`. A dirty working tree could contribute nested matching paths from
outside the intended roots even when those paths were ignored by Git. The first review
archive included 225 members below `local-artifacts/` and was quarantined unpublished.

A new automated regression copies the actual package source/configuration into a temporary
directory, adds harmless markers under local artifacts, raw traces, environment caches,
an unrelated nested README, and credential/cache paths inside intended roots, and builds
both wheel and source archives. Before the configuration fix, the real-build test failed
at the unexpected source-archive boundary; four deliberately contaminated-archive checks
passed by rejecting the invalid archives. This establishes a failing check for the actual
selection defect, not only a test of the configuration text.

The source target now uses `only-include` with the same explicit root files/directories.
The wheel keeps its existing `src/fail2test` package selection. No runtime dependency,
lock version, runner/fixture rule, provider behavior or public application API changed.
The new test checks required source/docs/license/UI content and also reads archive members
to confirm the synthetic marker bytes are absent, independent of their original paths.

`scripts/check_package_contents.py` checks wheel package/metadata boundaries, source root
files/directories, private/cache/credential-like path components and malformed/duplicate
member paths without extracting or installing archives. Hatch's automatically included root
`.gitignore` and `PKG-INFO` are permitted metadata. The existing package smoke script calls
this guard before installation and retains its required-file checks and clean core/source/
native workflows. The existing CI test and smoke steps therefore exercise the new checks
without a separate privileged job or credentials.

This is an archive-path boundary, not proof that every value inside an intentionally
published file is non-sensitive. Source/content review and final candidate scanning remain
necessary. An intentional future publication root needs a reviewed policy update.

## Verification

- The real dirty-tree build regression passes after the configuration fix. All four
  contaminated wheel/source guard cases pass by rejecting their invalid archive.
- Full Windows/Python 3.13.5 suite: **197 passed**, including Chromium, **88%** runtime
  coverage. Ruff lint/formatting and strict mypy pass. No fixture/review rule was weakened.
- Rebuilt working-tree wheel/source archives pass the guard: 34 wheel members and 152
  source members for this candidate. Required package/data/UI/docs/license/community
  content is retained; ignored local artifacts and cache copies are absent.
- The original quarantined build is rejected by the new guard. It remains quarantined.
- Clean wheel/core, source install and native LangGraph smoke workflows pass. Installed
  CLI, real-browser UI and native acceptance pass; the unchanged exported test detects
  the application bug and passes its fix. No provider calls or human timing claim.
- Machine-readable smoke/acceptance records and final artifact hashes are kept as ignored
  local audit output. This document does not embed its own source archive's hash.

These results close the demonstrated packaging blocker locally, not all publication gates.
The new checks have not been pushed or run on GitHub; the older merged-main CI result
applies only to its recorded source. New hosted verification needs a separately approved
push. Quarantined review builds must never be reused as release artifacts.
