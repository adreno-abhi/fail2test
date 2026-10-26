# Repository structure and engineering standards

This is the **target implementation tree**, not a claim that these files already exist. Create only the modules required by the current milestone. Keep public interfaces small; the module table in the architecture document defines responsibilities.

```text
fail2test/
  README.md
  LICENSE
  NOTICE                         # only applicable notices, no invented attribution
  CHANGELOG.md
  ROADMAP.md
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  GOVERNANCE.md
  SECURITY.md
  SUPPORT.md
  MAINTAINERS.md
  AGENTS.md
  pyproject.toml
  uv.lock
  .python-version
  .gitignore
  .gitattributes
  .editorconfig
  .pre-commit-config.yaml
  .github/
    CODEOWNERS
    dependabot.yml
    ISSUE_TEMPLATE/
      bug.yml
      feature.yml
      config.yml
    pull_request_template.md
    workflows/
      ci.yml
      docs.yml
      compatibility.yml
      release.yml
      dependency-review.yml
  src/fail2test/
    __init__.py
    py.typed
    cli.py
    case/
    ingest/
    privacy/
    rules/
    analysis/
    execution/
    reduction/
    export/
    integrations/langgraph/
    schemas/
  tests/
    unit/
    integration/
    conformance/
    security/
    packaging/
    fixtures/synthetic/
  examples/
    duplicate_refund/
      README.md
      app_broken.py
      app_fixed.py
      runner.py
      failure.json
      cases/
      tests/
    invalid_tool_argument/
  benchmarks/
    README.md
    manifest.json
    cases/
    expected/
  docs/
    index.md
    tutorials/
    how-to/
    explanation/
    reference/
    community/
    adr/
    rfcs/
  scripts/                       # small development/release helpers when needed
```

## Stack recommendations

| Need | Choice / rule |
|---|---|
| Language | Python; initial tested target CPython 3.12–3.14, with actual adapter/dependency compatibility verified in P0 |
| Packaging | `pyproject.toml`, `src/` layout, one distribution and `fail2test` import/CLI namespace subject to name availability |
| Build backend | Hatchling or another standard PEP 517 backend; choose Hatchling in P0 unless a verified packaging need dictates otherwise |
| Development environment | `uv` with a committed lockfile and documented standard pip installation for users |
| Models/schema | Pydantic v2 and bundled JSON Schema; validate parity and avoid two manually divergent contracts |
| CLI | Typer plus concise Rich output; machine output stays plain stable JSON |
| Tests | pytest, coverage, property-based tests for contract/matching/reduction invariants |
| Lint/format | Ruff; one formatter and one lint policy |
| Types | One checker, initially mypy; public case/result/runner interfaces typed |
| Docs | Markdown and MkDocs with a lightweight maintained theme; hosted docs optional after reproducible local build |
| Version | Single package version source; release process records it; no manually inconsistent copies |
| CI | GitHub Actions, least privilege, protected release environment |
| Dependency checks | Auditing, license inventory and automated update PRs; findings triaged rather than ignored |

These tools are recommendations, not dependency-version promises. Pin known-working development versions at P0. Published library dependency ranges must reflect tested compatibility; avoid forcing users to install the project's entire development lock.

## Distribution layout

Start with one package. Core dependencies are limited to validation and CLI needs. Framework code lives behind an optional `langgraph` extra. Test execution/export may use a documented `pytest` extra while exported tests need the small core/runtime. A future `suggest` extra can contain provider adapters after the provider/security decision. No mandatory framework, model SDK, cloud SDK, web framework, database, vector store or analytics client in the core.

Before splitting into `fail2test-core`, `pytest-fail2test` and multiple adapter distributions, require actual dependency/ownership or versioning pressure. A monorepo can contain examples/docs without becoming a multi-package build system.

## Development workflow

The implementation should make the following commands work after cloning; exact dependency groups are fixed in P0:

```text
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run mkdocs build --strict
uv build
```

Use a clean virtual environment for package-install smoke tests. Development uses the lock; compatibility jobs intentionally resolve the declared minimum and selected recent supported dependencies. Document Windows PowerShell and Unix shell instructions without relying on a Makefile or shell-specific aliases. Include paths with spaces in integration tests.

## Coding standards

- Keep domain/rule logic independent of CLI, frameworks, storage and provider clients.
- Validate data at module entry; use explicit errors with stable codes and useful correction guidance.
- Use return values for proposed artifacts; perform persistence deliberately at the orchestration layer.
- No hidden network calls, silent live fallbacks, automatic code imports during inspection, or broad exception handlers returning green results.
- No raw trace contents in default logs. Redaction applies to both success and error output.
- Write behavioral tests through public interfaces; use internal seams only where actual variability or security contracts require them.
- Public Python and case/result contracts require compatibility and docs review.
- Deterministic ordering for serialized outputs and template generation. Keep timestamps outside semantic identities where possible.
- Bound subprocess output, inputs and reduction attempts. Clean up only files/processes owned by the operation.
- Update the docs and user-facing changelog alongside behavior changes.

## Repository controls

Protect the default branch. Require CI and maintainer review; disallow force-pushes. Require owner review for workflows, licensing, security and contracts once owner handles exist. Initially a sole maintainer can be the practical reviewer/release owner, but this is a documented concentration risk; add a second trusted maintainer before promising continuity or enterprise support. Do not configure an impossible required-review rule that prevents all legitimate solo-maintainer changes.

No secrets in issues, fixtures, example output or screenshots. Commit sample `.env.example` only if a later provider feature actually needs it; do not add a blank secret-management layer preemptively. Ignore local caches, drafts, raw captures, build output, keys and editor-specific state. Synthetic curated fixtures are explicitly allowlisted for tracking.

Use narrow branches (`codex/…` for agent-created work in this workspace), small PRs, and meaningful commit messages. Avoid requiring contributors to install every framework/provider just to edit docs or core logic.

## Agent contribution instructions

`AGENTS.md` should describe commands, module ownership, fixture privacy, no-network expectations, test requirements and unsupported claims. It should tell coding agents to preserve trace-versus-execution distinctions, not modify approved cases to make failing tests pass, not relax rules silently, and never publish artifacts or upload evidence without task authorization. Human and agent-assisted contributions follow the same review and DCO rules.

## Package identity

Use `fail2test` as the working brand. Research found no public package/repository match in the specific checks performed; that does not reserve the name, establish trademark clearance or guarantee registry availability. Verify GitHub organization, PyPI normalized project name, domain and confusingly similar names before launch. Do not buy or register anything as part of this planning pack.
