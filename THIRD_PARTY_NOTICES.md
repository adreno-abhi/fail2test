# Third-party notices and license inventory

Fail2Test software is Apache-2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE). Copyright
remains with the contributors. This does not relicense dependencies or grant trademark rights.

## Material included in this source distribution

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) is adapted from Contributor Covenant 3.0,
  stewarded by the Organization for Ethical Source, under
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  The upstream attribution is retained; reporting/enforcement text was adapted for GitHub
  platform reporting and sole-maintainer limits, with an implementation note. Its terms apply
  to that document independently of Apache-2.0.
  Source: [Contributor Covenant](https://www.contributor-covenant.org/version/3/0/).
- [DCO](DCO) preserves Developer Certificate of Origin 1.1, copyright 2004, 2006 The Linux
  Foundation and its contributors. Its own notice permits verbatim copying and distribution.
  Source: [Developer Certificate of Origin](https://developercertificate.org/).
- The full Apache license text is reproduced as LICENSE. The standard appendix's example
  copyright fields are part of the license text, not invented project ownership details.

The authored browser UI uses system fonts and native assets. No frontend component framework,
icon pack, external font, model weights or vendored Python dependency is shipped in the wheel.
Code provenance must be rechecked if material is copied or vendored in later contributions.

## Separately installed Python packages

The [readable inventory](docs/licensing/dependencies.md) and
[machine-readable evidence](docs/licensing/dependencies.json) cover every third-party package
in the current uv.lock, including optional integrations and development/browser tools. They
record pinned versions, direct dependency groups, declared license expressions/legacy metadata,
and available license/NOTICE file hashes from the verified Windows environment. Package files
are installed separately by the package manager; this repository does not relicense them.

Metadata may use legacy names rather than exact SPDX expressions. `mergedeep` reports UNKNOWN
in metadata but its installed LICENSE explicitly declares MIT. `httpx2-jsfetch==1.0` is a
platform-specific Emscripten dependency absent on Windows; its BSD-3-Clause declaration was
verified against [that exact PyPI release](https://pypi.org/project/httpx2-jsfetch/1.0/).
The inventory identifies this external metadata evidence rather than claiming a local install.

Mixed declarations, including MPL and dual-license expressions, are preserved exactly where
available. The inventory is evidence for review, not a legal compatibility certification,
vulnerability scan, SBOM attestation or promise about future versions. Inspect upstream
license and NOTICE files before redistributing dependencies, especially modified packages,
standalone bundles or container images. A pure dependency reference is not a vendored copy.

## Refresh and check

```text
uv sync --locked --all-extras --group browser
uv run --group browser python scripts/dependency_inventory.py --review-date 2026-10-26
uv run python scripts/dependency_inventory.py --check-lock
```

Review the generated diff and source evidence. Generation requires the verified full environment
and exact locked versions; platform-specific absence needs an explicit reviewed record. The
offline `--check-lock` verifies complete lock coverage and hash identity, not license correctness.
If the lock changes, refresh evidence before release. Build-system ranges are separate from
uv.lock: record actual isolated build tooling in release evidence if producing a standalone bundle.

## External development tools and services

Python, uv, optional Node/Prettier formatting, installed Playwright browsers and optional local
model runtimes/models have their own licenses and are not redistributed by this package.
Hosted provider terms are separate from software licensing; using an OpenRouter endpoint does
not bundle its model weights or confer rights to private evidence. This project does not
automatically install a local runtime, download models or include provider credentials.
