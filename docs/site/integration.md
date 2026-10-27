# Integrating your application

Check [application fit](adoption.md) and prepare [supported evidence](evidence.md) first.
The integration seam is one callable that accepts JSON input and a `RunContext`, injects its model/tool dependencies, and returns JSON output:

```python
from fail2test import RunContext


def run(data: dict, context: RunContext) -> dict:
    plan = context.model.complete("planner", {"task": data["task"]})
    result = context.tools.call(plan["tool"], plan["arguments"])
    return {"result": result}
```

Register it in trusted local `fail2test.toml`:

```toml
[runners.application]
callable = "my_app.testing:run"
capabilities = ["sync", "serial", "json", "injected_model", "injected_tools"]
timeout_seconds = 10.0
```

The case cannot specify code to import. Application import happens only on execution, in a managed subprocess. You are running trusted repository code with host privileges; the subprocess is not a hostile-code sandbox.

## Existing model and tool clients

Inject controlled dependencies where the application already accepts clients/functions. The core provides explicit `complete(slot, request)` and `call(tool, arguments)` interfaces. For native LangChain/LangGraph applications, `FixtureChatModel` implements `BaseChatModel.invoke`/`bind_tools`, and `fixture_tool` preserves an ordinary tool definition's name and schema while replacing its body. No SDK monkeypatch or provider account is needed.

Match model requests by slot, ordinal and exact canonical JSON. Tool arguments match exactly with no live fallback. A changed prompt is an unmatched model request, not evidence that the new prompt works. Fixture tests establish how code handles recorded responses; live-model quality evaluation remains separate.

## LangGraph

Install the `langgraph` extra (from this checkout, `uv sync --locked --all-extras`). Keep the application graph constructor accepting a model and tools. The Fail2Test-specific test runner can be this small:

```python
from fail2test.integrations.langchain import FixtureChatModel, fixture_tool
from fail2test.integrations.langgraph import graph_runner

from my_app import build_graph, refund


def test_graph(context):
    return build_graph(
        model=FixtureChatModel(context, slot="planner"),
        tools=[fixture_tool(context, refund)],
    )


run = graph_runner(test_graph)
```

Your production graph module does not need to import Fail2Test. The example at `examples/langgraph_refunds` uses native `MessagesState` and `ToolNode`, a recorded model plan with duplicate refund calls, and the same reviewed assertion for broken/fixed behavior. Its original payment function deliberately raises if invoked; only the fixture wrapper may serve the response.

`graph_runner` disables automatic LangSmith tracing, invokes the graph with `max_concurrency=1`, and converts supported native message state into JSON. It permits serialized tool execution to hand off to worker threads while rejecting overlapping transport calls. A subprocess remains the outer timeout control. This is not a parallel/multi-agent executor or arbitrary checkpoint restore.

## Native fixture format

Use `chat_request(messages, tools=[original_tool], stop=..., tool_choice=..., options=...)` to normalize a model request and `chat_response(ai_message)` to prepare its response. Save these into a normal case's `model_fixtures` with the configured slot/ordinal. The versioned request format is `langchain-chat.v1`.

| Included in strict matching | Deliberately excluded |
|---|---|
| System/user/assistant/tool text, names and semantic tool-call IDs | Generated framework message IDs |
| Tool names, descriptions and schemas | Usage and response/timing metadata |
| Stop, tool choice and supplied JSON options | Framework callback/config metadata |

Structured tool responses are normalized before native message formatting so object key order cannot alter a later model request with the same case digest. Tool fixture arguments follow native schema validation; the wrapper does not execute application code to infer hidden state or body-specific default behavior. Schema validators remain trusted executable code.

Current scope: synchronous text chat, ordinary schema-backed tools and serialized graph execution. Multimodal/unknown message content, provider-specific `additional_kwargs`, async/streaming/batched model calls, runtime-injected tool arguments, tool artifacts and live-model evaluation are unsupported. Invalid/unsupported adapter operations latch an incomplete result even when application code or ToolNode catches the exception. No live model/tool fallback exists.

## pytest and CI

Keep the exported test, case and manifest together in your application repository. Keep runner configuration and application dependencies available at their documented relative paths. Run with ordinary pytest:

```text
python -m pytest tests/fail2test_regressions
```

In your CI runner, install your application's locked dependencies including Fail2Test and
pytest, then execute that command. No special CI service or model credential is needed for
fixture tests. The project's own hosted workflow is in `.github/workflows/ci.yml`; it tests
Fail2Test itself and is not a required template for your application.

Use one runner name such as `application` for your own regression. Validate its broken
behavior, make the code fix, then run/export the same runner. The demo's separate `broken`
and `fixed` names are teaching aids. If you change a prompt or tool schema, strict request
matching may require deliberate new fixtures and review; a fixture mismatch is not a
model-quality judgment.

If a fixture is missing, config is invalid, or the application crashes, the test raises an execution error rather than passing or silently skipping. Editing case/rules requires new review; exporting a case also requires a reproduced failing baseline.
