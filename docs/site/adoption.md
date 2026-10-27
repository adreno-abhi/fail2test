# Is Fail2Test a fit?

Fail2Test helps Python developers turn a known agent failure into a reviewed regression
that runs against their current application code with recorded model/tool responses.
Use it for repeated actions, argument bounds, forbidden tools, call budgets and structured
output checks. Its strongest starting audience is developers maintaining synchronous,
dependency-injectable agents, including the supported LangGraph configuration.

## Decide before integrating

| Your situation | Fit today |
|---|---|
| A model proposed duplicate actions and application code dispatched both | Strong: reproduce the plan and test the code fix |
| An agent invoked a tool forbidden by the scenario | Strong: assert that dispatch never occurs |
| Tool arguments or final JSON violate a clear requirement | Supported by declarative predicates |
| You want a test in an existing Python/pytest repository and CI | Supported; keep the runtime and application dependencies installed |
| You only have ordinary log text, a screenshot or a vendor trace export | Convert first; there is no automatic capture/import adapter |
| You changed a prompt and want to know if the live model improves | Use a live-model evaluation workflow; strict recorded requests will mismatch |
| Your agent requires async/streaming, parallel calls or multimodal messages | Outside the current supported adapter scope |
| Your failure depends on hidden database/checkpoint state or real side effects | Requires application-owned setup/injection; a trace alone is insufficient |
| Your code hardcodes clients or performs I/O outside injected dependencies | Refactoring may be needed; fixture mode is not network/OS isolation |
| Your application is JavaScript/TypeScript, or uses Python below 3.12 | No supported native workflow today |

## What you provide

1. The input and recorded dependency requests/responses. Follow [evidence preparation](evidence.md).
2. A requirement you can defend, such as “dispatch at most one refund for this order.”
   An observed trace or AI suggestion does not establish the requirement.
3. A small trusted runner that injects controlled model/tool dependencies into your
   application. See [integration](integration.md). Production construction can remain
   independent of Fail2Test if it already accepts those dependencies.
4. A reproduced failing baseline, then a fix in the same application. The demo has two
   named runners only to show the before/after behavior without editing files.

There is no measured promise that every integration takes ten or thirty minutes.
The owner completed the guided sample UI flow; independent application adoption remains
unmeasured. Preparing evidence and introducing dependency injection can dominate the effort.

## What goes into your repository

Keep the exported `test_regression.py`, `case.json` and `manifest.json` together. Keep
your runner, `fail2test.toml` and application dependencies at the expected relative paths.
Run the generated test with ordinary pytest. It still imports Fail2Test; export does not
remove that runtime dependency. Moving the complete application tree preserves these
relative paths; moving only the export directory can break them.

For a source installation without contributor tooling, from the Fail2Test checkout in
your chosen environment:

```text
python -m pip install ".[pytest]"
```

For native LangGraph adaptation use `".[pytest,langgraph]"`. No PyPI release exists yet;
do not assume `pip install fail2test` installs this project's reviewed code. For development
and the maintained tutorial, use the locked uv setup in the README.

## Why add it instead of writing a mock test?

For one small function and one assertion, a hand-written pytest test may be simpler.
Fail2Test adds a shared reviewed case format, strict dependency matching, five declarative
rule kinds, baseline evidence, a local review UI, bounded input reduction and repeatable
pytest export. These matter when the same incident evidence must be inspected, reviewed
and kept as a regression across changes. They also add a workflow to learn.

You can continue using tracing and live-model evaluation alongside it. Neither an exported
fixture regression nor a model-generated rule proves that the live agent is generally safe.
See [contracts and limitations](contracts.md) and the [compatibility record](compatibility.md).
