# Fail2Test

Turn a recorded agent failure into a pytest regression that catches the bug in your current code.

**Status:** public open source project, version 0.1.0 available from this repository.
The complete supported fixture workflow and hosted CI pass. No tagged GitHub release or
PyPI upload has shipped yet. See [release notes](docs/release/0.1.0.md).

Python 3.12–3.14 is tested on Windows and Ubuntu, including hosted CI.
See [compatibility and measured acceptance](docs/site/compatibility.md) for exact versions,
browser coverage, corrected dependency bounds and the limits of automated onboarding timings.

A bundled local browser UI covers evidence, review, execution, reduction and export. It needs no frontend tools or model key; see [the browser walkthrough](docs/site/local-ui.md).

## Is it useful for your project?

Use Fail2Test when your Python agent repeats a tool action, passes an unsafe argument,
calls a forbidden tool, exceeds a call budget or returns the wrong structured output,
and you want a reviewed regression in your existing pytest/CI workflow. The best fit is a
synchronous application whose model and tools can be replaced in tests, including the
supported LangGraph adapter.

You supply recorded model/tool requests and responses, the intended behavior, and a small
runner for your application. Import accepts Fail2Test JSON, not arbitrary logs, screenshots
or vendor trace exports. There is no automatic recorder. Start with the
[fit guide](docs/site/adoption.md) and [evidence preparation](docs/site/evidence.md).

Fixture tests check how your code handles recorded responses. Prompt/model quality,
async/streaming execution and arbitrary checkpoint replay need other testing approaches.

## What it does today

A Python CLI and library that imports supported JSON failure evidence, sanitizes known sensitive fields, proposes rules for review, re-executes current application code with model/tool fixtures, reduces irrelevant inputs, and exports readable pytest tests and JSON fixtures.

The fixture engine supports duplicate-call checks, argument predicates, forbidden tools, output predicates and call budgets. Unknown interactions and unsupported/incomplete execution are errors, never silent passes. Native `BaseChatModel` and tool replacements let supported LangGraph applications keep their message/tool interfaces. A graph-factory helper enforces serialized execution and exports native message state as JSON.

## Try the local workflow

With Git, Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/),
clone the public repository and run the key-free example. No GitHub account or model key is required.

```text
git clone https://github.com/adreno-abhi/fail2test.git
cd fail2test
uv sync --locked
uv run fail2test init local-artifacts/demo
uv run fail2test import local-artifacts/demo/failure.json --out local-artifacts/demo/case
uv run fail2test review local-artifacts/demo/case --reviewer local-owner
uv run fail2test validate local-artifacts/demo/case --runner broken --config local-artifacts/demo/fail2test.toml
uv run fail2test export local-artifacts/demo/case --runner fixed --config local-artifacts/demo/fail2test.toml --out local-artifacts/demo/tests
uv run pytest local-artifacts/demo/tests/test_regression.py -q
```

No model account or real payment service is involved. `validate` succeeds when it reproduces the selected failure; the exported pytest test succeeds when corrected application behavior satisfies the reviewed rule. Read the [complete tutorial](docs/site/quickstart.md), including the deliberately failing `run` command.

Expected result: the original runner fails the reviewed one-refund rule; the fixed runner
passes; pytest reports `1 passed`. The export contains `test_regression.py`, `case.json`,
`manifest.json` and a README. Keep the runner/configuration in your application repository.
The generated test uses pytest and the Fail2Test runtime; it is not a standalone test with
all library dependencies removed. Use a new demo/output directory when repeating the trial.

## Integrate with your application

Prefer the browser? Initialize a separate example with `uv run fail2test init local-artifacts/ui-demo`, then run `uv run fail2test ui --workspace local-artifacts/ui-demo`. Import the example, review its rule, validate `broken`, run `fixed`, and preview/export pytest from the UI.

Provide one local runner and inject the test dependencies:

```python
from fail2test import RunContext


def run(data: dict, context: RunContext) -> dict:
    plan = context.model.complete("planner", {"task": data["task"]})
    return {"result": context.tools.call(plan["tool"], plan["arguments"])}
```

Register `my_app.testing:run` in trusted local `fail2test.toml`. Generated tests use ordinary pytest and your existing CI. See the [integration guide](docs/site/integration.md).

For a native `MessagesState`/`ToolNode` application, see the [LangGraph example](examples/langgraph_refunds/README.md). Only its test runner knows about Fail2Test; graph construction stays independent.

Optional [AI-assisted rule suggestions](docs/site/ai-suggestions.md) support OpenRouter,
already-running local models and other OpenAI-compatible endpoints. Preview and explicitly
authorize each request; generated rules remain unapproved. These providers suggest rules;
they do not change the recorded model used by a fixture regression.

This implementation requires synchronous, serialized execution and explicit dependency injection. Native chat adaptation supports text messages and ordinary schema-backed tools; it does not construct provider clients, restore arbitrary checkpoints or evaluate live models. Recorded responses test code handling of those responses; they do not prove that a changed prompt improves model output. Sanitization is best effort, and the execution subprocess is not a hostile-code sandbox. Read [contracts and safety](docs/site/contracts.md).

## Development approach

Contributions: [guide](CONTRIBUTING.md), [code of conduct](CODE_OF_CONDUCT.md),
[support](SUPPORT.md), [security](SECURITY.md), [governance](GOVERNANCE.md) and
[maintainer/contact status](MAINTAINERS.md). Release prerequisites are in
[PUBLISHING.md](PUBLISHING.md). The owner confirmed `adreno-abhi/fail2test` and
`@adreno-abhi`. The [GitHub setup record](docs/release/github/SETUP.md) records verified
public setup, CI and branch protections. Use [private vulnerability reporting](https://github.com/adreno-abhi/fail2test/security/advisories/new)
for security concerns; conduct reporting uses GitHub's platform route. No personal contact
email is published.

- Work locally in this dedicated Git repository; use small, reviewable local commits.
- Build and validate the complete agreed first-release scope before pushing to public GitHub.
- The project owner is the initial human maintainer; AI assistance does not replace release or security accountability.
- Contributions are welcome through documented issues and pull requests; see the public roadmap.
- Keep commercialization as future context; accounts, billing, paid pilots and hosted execution are outside the initial build.

## Planning

- [Current high-level and delivery plan](PLAN.md)
- [Launch roadmap](ROADMAP.md)
- [Detailed technical blueprint](docs/planning/README.md)
- [Architecture](docs/planning/docs/02-architecture.md)
- [Execution and fixture contracts](docs/planning/docs/03-contracts.md)
- [Verification strategy](docs/planning/docs/06-verification.md)
- [Current user documentation](docs/site/index.md)
- [Local development evidence](docs/development/status.md)

## Development checks

```text
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run mkdocs build --strict
uv run python scripts/check_repository.py
uv run python scripts/dependency_inventory.py --check-lock
uv build
```

The package/schema contracts are versioned independently. Planning documents describe the full intended project; current help and user docs identify implemented behavior. No public compatibility, performance or security certification is implied by a planning target.

Run the optional real-browser acceptance suite using the setup commands in the
[local UI guide](docs/site/local-ui.md#browser-checks-for-contributors). Browser dependencies
are development-only; they are not needed to use the packaged UI.

## License

Apache-2.0 for project software. See [LICENSE](LICENSE), [NOTICE](NOTICE) and
[third-party notices](THIRD_PARTY_NOTICES.md) for dependency evidence and separately licensed
documents, including the adapted Contributor Covenant. Reporting routes and host checks
must still be verified before launch.
