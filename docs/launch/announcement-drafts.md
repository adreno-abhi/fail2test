# Launch copy for owner review

These are AI-assisted drafts for **project-owned channels**. Nothing has been posted.
Do not paste them into Hacker News, the LangChain Forum, r/LangChain, LocalLLaMA or a DEV
promotional article. Their applicable authorship/promotion restrictions are recorded in
the [research](../development/distribution-research.md). A venue permitting a project does
not automatically permit generated copy. Disclose affiliation and obey its current rules.

## Short project-owned announcement

Fail2Test v0.1.0 turns a recorded Python agent failure into a reviewed pytest regression.

The included example starts with an agent requesting the same refund twice. Review the
“refund once” rule, reproduce the failing behavior, run the supplied fixed runner and export
pytest plus JSON fixtures. The CLI and local UI use the same engine. The fixture workflow
requires no model key or payment service.

Best fit: synchronous Python applications with replaceable model/tool dependencies,
including the supported LangGraph adapter. You prepare recorded requests/responses and a
small runner. Async/streaming and automatic vendor trace capture are not supported.

Try the [v0.1.0 quickstart](https://github.com/adreno-abhi/fail2test/blob/v0.1.0/docs/site/quickstart.md).
For a bug or integration question, open a [synthetic reproduction](https://github.com/adreno-abhi/fail2test/issues).

## Project-owned technical article draft

### Catch duplicate agent tool actions with a reviewed pytest regression

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

Start with Git, Python 3.13 and uv:

```console
git clone --branch v0.1.0 --depth 1 https://github.com/adreno-abhi/fail2test.git
cd fail2test
uv sync --locked
uv run fail2test init local-artifacts/demo
uv run fail2test import local-artifacts/demo/failure.json --out local-artifacts/demo/case
uv run fail2test review local-artifacts/demo/case --reviewer local-owner
uv run fail2test validate local-artifacts/demo/case --runner broken --config local-artifacts/demo/fail2test.toml
```

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

The integration work is deliberate: supply supported JSON evidence and replace the model
and tools through a small application-owned runner. The [integration guide](../site/integration.md)
shows the seam, and the [evidence guide](../site/evidence.md) explains accepted inputs.

This is useful for orchestration regressions such as duplicate calls, wrong arguments,
forbidden actions and call budgets. Recorded fixture responses do not measure how a changed
prompt behaves against a live model. Execution is synchronous/serialized, and arbitrary logs
or screenshots are not importable evidence. Sanitization is best effort; review actual
artifacts before sharing them. Python runners remain trusted code.

If your application fits, try one synthetic failure and report where preparation or runner
integration becomes unclear. That feedback is more actionable than a star count.

*Maintainer disclosure: the project and this draft were developed with AI assistance.
The actual synthetic workflow recording and exported pytest were exercised before sharing.*

## Draft feedback issue — create/pin only after approval

**Title:** Trying Fail2Test with your application? Share integration friction safely

We would like feedback from developers trying a supported synchronous Python/LangGraph
application. Please use synthetic examples only. This thread is public.

Helpful details:

- Fail2Test/Python/framework version and whether you completed the key-free example.
- Your failure class: duplicate calls, arguments, forbidden actions, output or call budget.
- Where you got blocked: installation, preparing JSON, dependency injection, reviewing a
  rule, running a regression or exporting pytest.
- Whether the exported regression now runs in your application's tests/CI, if you choose
  to share that. A public repository link is optional and must be yours to disclose.

Do not upload credentials, customer traces or proprietary code. Use private vulnerability
reporting for security concerns. No response SLA is promised. We will not infer permission
to quote you, name your company or publish a case study; those need separate consent.

## Show HN: owner-authored factual brief, not a post draft

HN requires the maker to write the submission and comments themselves without generated or
AI-edited text and prohibits automated posting/vote solicitation. No paste-ready HN title,
intro or reply is supplied here. Before writing your own text, independently check:

- Which real bug motivated the project, in your own experience and words.
- What the tool actually runs, the evidence/runner work required and the current limits.
- The key-free runnable release/quickstart URL and real demonstration.
- How fixtures differ from live model evaluation and historical playback.
- What specific technical feedback you want and when you can personally answer questions.
- Honest project provenance if asked. Do not invent independent users or unsupported results.

Read the [Show HN](https://news.ycombinator.com/showhn.html) and
[general guidelines](https://news.ycombinator.com/newsguidelines.html) before composing it.
