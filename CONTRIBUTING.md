# Contributing to Fail2Test

Contributions can improve code, documentation, synthetic examples, supported integrations,
accessibility and bug reports. Start with the [README](README.md), [roadmap](ROADMAP.md),
[code of conduct](CODE_OF_CONDUCT.md) and [safety contract](docs/site/contracts.md).

The repository exists privately at `adreno-abhi/fail2test`; no public release has shipped.
Collaborators with access can use its issues and pull requests. Public contributions begin
after the owner approves public visibility. Private vulnerability reporting remains pending;
follow [SECURITY.md](SECURITY.md). [Publication requirements](PUBLISHING.md) track launch checks.

## Pick a contribution

- For bugs, provide a small synthetic reproducer, commands, expected behavior, actual status
  and error code. Include OS/Python/Fail2Test/framework versions and whether this is import,
  fixture execution, UI, export or optional suggestions. Never attach private traces or keys.
- For enhancements, explain the developer workflow, current workaround and a concrete
  acceptance example. Discuss new public APIs, schemas, transports or privacy defaults before
  implementing a large change. Use an issue or a small design note under `docs/decisions/`.
- Good initial work includes a documentation correction, a reproducible platform issue,
  an accessibility improvement or a synthetic test for a supported boundary. Labels and
  assignments will be maintained on GitHub after publication; none are promised to exist yet.
- Report vulnerabilities privately using [SECURITY.md](SECURITY.md), and conduct concerns
  using [SUPPORT.md](SUPPORT.md#conduct-and-private-contact). Public issue forms are not private.

## Set up development

Use Python 3.12–3.14 as declared by the package. The verified local matrix includes Windows
and Ubuntu WSL2 on all three minors, with Chromium on Windows/3.13. See the
[compatibility record](docs/site/compatibility.md) for exact patches, dependency bounds and gaps.
Install [uv](https://docs.astral.sh/uv/getting-started/installation/) separately, then:

```text
uv sync --locked --all-extras
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run mkdocs build --strict
uv run python scripts/check_repository.py
uv run python scripts/dependency_inventory.py --check-lock
uv build
uv run python scripts/smoke_package.py
```

The package smoke check permits lock-constrained registry downloads for its isolated core,
source and optional framework installs; it also works with an initially empty cache.
It makes no model-provider
or real-payment calls. It requires `uv` on PATH and working temporary directories.

Archive boundaries are checked before smoke installation. The packaging regression also
builds an isolated source copy containing synthetic ignored local/cache/credential-like files
and verifies they are absent from wheel and source contents. This requires `uv build` and
access to the configured build dependency registry or its cache. Keep archive policy checks
aligned with intentional publication roots; a clean Git status is not an artifact-content check.

For documentation-only changes, run `uv sync --locked` and `uv run mkdocs build --strict`.
Check relative links in root/community files as well; MkDocs covers `docs/site/` only.

For UI changes, also run the real browser checks:

```text
uv sync --locked --all-extras --group browser
uv run --group browser playwright install chromium
uv run --group browser pytest tests/test_ui_browser.py -q
```

Chromium is a development download, not a UI runtime requirement. Run the full suite with
`uv run --group browser pytest --cov=fail2test --cov-report=term`. Screenshots go into ignored
`output/playwright/`. Static assets are formatted source, bundled without a build step;
optional formatting uses `npx --yes prettier@3.6.2 --write src/fail2test/ui/static/`.

## Repository map and engineering rules

`src/fail2test/` owns the shared engine and CLI; `integrations/` contains optional native
adapters; `ui/` owns the loopback server and bundled assets. `tests/` verifies public behavior,
`examples/langgraph_refunds/` demonstrates an application-owned runner, `docs/site/` is user
documentation, and `docs/development/` records evidence. Older `docs/planning/` material is
design history; current user docs and runtime contracts describe implemented behavior.

- Keep optional framework imports outside the core import path. CLI, library and UI share
  the same rules, digests, review, execution and export engine.
- Cases are JSON data. Do not introduce executable expressions, pickle, case-selected imports,
  shell commands, implicit provider calls or live-tool fallbacks.
- Regression evidence must execute current application code. Historical responses are fixtures,
  not proof that a fix works. Unknown interactions and incomplete execution must not pass.
- Never weaken assertions, fixtures or review checks merely to make a test green. Explain
  legitimate requirement changes and invalidate previous review/baseline records.
- Add meaningful tests for changed behavior and failure boundaries; docs-only edits do not
  need tests that simply repeat their text. Keep fixtures synthetic and minimal.
- Dependency changes update `pyproject.toml`, `uv.lock` and the [license inventory](THIRD_PARTY_NOTICES.md).
  Explain the need and optional/runtime scope. Do not vendor dependencies or assets silently.
- Live provider tests require separate authorization and a synthetic payload preview. Do not
  add keys to CI, run live calls on contributor PRs, install a local model automatically or
  present mock tests as live-model quality evidence.

## Submit and review

Keep each PR focused. Describe the problem, resulting behavior, validation and material
limitations. Update relevant docs/changelog and explain public compatibility or privacy
changes. Use the PR checklist; maintainers may request a smaller change or additional evidence.
Review is best effort with one initial human maintainer; there is no response SLA.

New external contributions require a [Developer Certificate of Origin 1.1](DCO) sign-off.
Read it before using `git commit -s`: the sign-off is your attestation, not a formatting step.
Use an identity/email you control and are willing to publish, including a suitable GitHub
noreply address if appropriate. Never sign for someone else or fabricate retroactive sign-offs.
Maintainers review the provenance of the pre-publication history separately. There is no CLA
or copyright assignment; contributions retain their authors' copyright and use the relevant
project/file license. The adapted code of conduct has its own stated license.

AI-assisted contributions have the same accountability. Understand and verify the change;
disclose material generation or copied-source provenance in the PR. Do not submit code you
cannot explain, private prompts, or material whose rights you cannot establish.

See [governance](GOVERNANCE.md) for decisions, access and maintainer responsibilities.
