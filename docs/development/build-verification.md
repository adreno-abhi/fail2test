# Local build verification — 26 October 2026

Scope: first working offline regression workflow. This is evidence for local development, not public-release clearance.

## Environment

- Windows, CPython 3.13.5.
- uv 0.10.9; project dependencies recorded in uv.lock.
- Real-framework test used LangGraph 1.2.17.
- Other Python/OS/framework combinations remain unverified in this checkpoint.

## Results

| Check | Result |
|---|---|
| `uv run pytest -q --cov=fail2test --cov-report=term-missing` | 85 passed; 88% combined statement/branch coverage, including subprocess coverage |
| `uv run ruff check .` | PASS |
| `uv run ruff format --check .` | PASS, 59 files |
| `uv run mypy` | PASS, 16 source files |
| `uv run mkdocs build --strict` | PASS |
| `uv build` | Wheel and source distribution built |
| `uv run python scripts/smoke_package.py` | PASS for fresh wheel workflow and source-distribution installation |

The functional tests include generating an ordinary pytest file, observing its failure against broken application code, editing the application, and rerunning the same exported test successfully. Missing fixtures, swallowed transport errors, invalid review digests, timeouts and unsupported async/threaded transport access do not become validated passes. A native LangGraph graph uses the same fixture/rule contract.

The clean-install check creates a fresh environment outside the repository, installs the actual wheel with only the pytest extra and cached dependencies, confirms LangGraph is absent, and executes init/import/review/validate/broken-run/fixed-run/export/pytest. It then installs the source distribution and verifies the CLI/example resources. This avoids relying on editable source imports or development-only framework dependencies.

## Verified artifacts

- `fail2test-0.1.0.dev0-py3-none-any.whl`
  - SHA-256: `52b29360058f3240dd0672e3c4111c3e5248d21b258be03c19e03c3a02451175`
- `fail2test-0.1.0.dev0.tar.gz`
  - SHA-256: `3e44f7d9a266c554733240cdaa5a4301e4fcaa79d856dd6255574568ac232758`

These local artifacts were built before this verification note was added. They are not signed releases or registry attestations. Rebuild and reverify against the eventual reviewed release commit before publishing.

## Remaining limitations

Overall coverage has not reached a blanket 90% target. The core execution, rule, model and review modules exceed 90% in this run; import, CLI, reduction and some operational error paths need more adversarial coverage. Coverage percentages are not a security certification.

Model-assisted proposals, native client adaptation, broader fixture minimization, cross-platform compatibility, actual contributor/security contacts, and host/registry publication controls remain open. No runtime model-provider calls or external publication were performed.
