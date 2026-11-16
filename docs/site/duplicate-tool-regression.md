# Catch duplicate agent tool actions with a reviewed pytest regression

Published 2 November 2026 · Fail2Test v0.1.0 · Maintainer walkthrough

[Watch the actual local UI demo](https://github.com/adreno-abhi/fail2test/blob/main/docs/launch/assets/fail2test-demo.mp4)
· [Get v0.1.0](https://github.com/adreno-abhi/fail2test/releases/tag/v0.1.0)

A trace tells you an agent requested a refund twice. The next question is whether your
application still dispatches both actions after a code change.

Fail2Test records the dependency responses as fixtures, makes the intended assertion
explicit, and runs current application code against that case. A baseline must reproduce
the selected failure before the case can be exported as a regression. The generated pytest
uses the Fail2Test runtime and the application's runner/configuration.

The bundled synthetic example has two pre-existing runners: `broken` dispatches duplicate
refund calls, and `fixed` deduplicates the action for an order. Switching the demo runner
shows the same reviewed case failing and passing. The tool does not write that fix for you.
For your own application, keep one runner, validate the failure, change your implementation
and rerun that regression.

## Reproduce the failure

Start with Git, Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/):

```console
git clone --branch v0.1.0 --depth 1 https://github.com/adreno-abhi/fail2test.git
cd fail2test
uv sync --locked
uv run fail2test init local-artifacts/demo
uv run fail2test import local-artifacts/demo/failure.json --out local-artifacts/demo/case
uv run fail2test review local-artifacts/demo/case --reviewer local-owner
uv run fail2test validate local-artifacts/demo/case --runner broken --config local-artifacts/demo/fail2test.toml
```

## Verify the regression

Validation succeeds because the selected failure was reproduced. Now check the broken
application as a regression:

```console
uv run fail2test run local-artifacts/demo/case --runner broken --config local-artifacts/demo/fail2test.toml
```

Expected: `complete: fail`, exit 1. That is the intended negative result. Compare the supplied
fixed application and keep its regression:

```console
uv run fail2test run local-artifacts/demo/case --runner fixed --config local-artifacts/demo/fail2test.toml
uv run fail2test export local-artifacts/demo/case --runner fixed --config local-artifacts/demo/fail2test.toml --out local-artifacts/demo/tests
uv run pytest local-artifacts/demo/tests/test_regression.py -q
```

Expected: `complete: pass` and pytest `1 passed`. Use new output directories when repeating
the example. For the browser version, initialize a separate workspace and explicitly start
`uv run fail2test ui --workspace PATH`; inspect the import, review, execution and export steps.

## Bring your own application

The integration work is deliberate: supply supported JSON evidence and replace the model
and tools through a small application-owned runner. The [integration guide](integration.md)
shows the seam, and the [evidence guide](evidence.md) explains accepted inputs.

This is useful for orchestration regressions such as duplicate calls, wrong arguments,
forbidden actions and call budgets. Recorded fixture responses do not measure how a changed
prompt behaves against a live model. Execution is synchronous/serialized, and arbitrary logs
or screenshots are not importable evidence. Sanitization is best effort; review actual
artifacts before sharing them. Python runners remain trusted code.

If your application fits, try one synthetic failure and share where preparation or runner
integration becomes unclear in the [public feedback issue](https://github.com/adreno-abhi/fail2test/issues/10).
Use synthetic examples only; security concerns belong in
[private vulnerability reporting](https://github.com/adreno-abhi/fail2test/security/advisories/new).

*Maintainer disclosure: the project and this walkthrough were developed with AI assistance.
The actual synthetic workflow recording and exported pytest were exercised before sharing.*
