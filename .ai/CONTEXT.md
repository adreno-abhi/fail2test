# Durable Fail2Test context

Public repo: https://github.com/adreno-abhi/fail2test
Docs: https://adreno-abhi.github.io/fail2test/
Runtime: synchronous Python fixture regressions, local UI, supported LangGraph adapter.
Evidence/runner are manually prepared; no automatic vendor capture or live-model eval.

## Verification commands
`uv sync --locked --all-extras --group browser --python 3.13`
`.venv/Scripts/python.exe -m playwright install chromium`
`.venv/Scripts/python.exe -m pytest --cov=fail2test -q`
Use venv ruff/mypy/mkdocs executables; `uv build` for artifacts.
`python scripts/dependency_inventory.py --review-date YYYY-MM-DD` regenerates license evidence;
`--check-lock` validates all lock entries/hash. Updates need both JSON and Markdown inventory.
`python scripts/smoke_package.py` and `python scripts/acceptance.py --browser --out PATH`
exercise installed packages. Run heavy acceptance checks sequentially on this Windows machine.

## Publication
Main is protected; required CI-complete and PR flow. Actions allowlist uses exact SHAs and
requires full SHA pinning; new action versions may require explicitly approved policy updates.
Docs deploy from successful main CI to GitHub Pages with main-only environment.
User approves one implementation/publication step at a time. Never publish credentials or
original private development history. Provider calls/local models need their authorized scope.
