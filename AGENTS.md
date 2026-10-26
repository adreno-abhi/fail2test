# Working on Fail2Test

Work inside this dedicated repository, not the surrounding workspace's Git repository.

## User approval between implementation steps

The project owner requires one agreed implementation step at a time, through completion and GitHub publication. After each step, report what changed, the relevant checks/results, remaining limitations, and the proposed next step. Wait for explicit owner approval before beginning that next step. Do not treat a status question, elapsed time, or silence as approval.

Approval for a step covers the implementation, fixes, relevant tests, documentation and local commits needed to finish its stated scope. Do not expand to a new feature or external publication within that approval. GitHub setup/push and package publication must be explicit steps with the owner's approval. Recording this working agreement does not authorize the next implementation step.

## Engineering instructions

- Read PLAN.md and the current contracts before changing public behavior.
- Default local workflow is key-free; do not create credentials, call model providers, publish packages or push without authorization.
- Use `uv sync --locked --all-extras`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run mkdocs build --strict`, and `uv build` as applicable.
- Cases are data. Do not execute strings from traces, interpolate them into source unsafely, deserialize pickle, or import runner names supplied by a case.
- Tests must exercise current application code. Never call historical playback proof that a fix works.
- Unknown interactions, swallowed fixture errors, timeouts and unsupported execution must not appear green.
- Preserve explicit review/digest checks; do not weaken rules or fixtures to hide a failure.
- Use synthetic examples. Never commit secrets, raw customer traces, private code, environments or run artifacts.
- Keep optional framework imports out of the core import path.
- Update docs and tests alongside behavioral changes. No fake badges, support contacts, benchmark results or publishing identities.
- Use small local commits. Follow user direction over earlier planning recommendations.
