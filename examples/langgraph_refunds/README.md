# Native LangGraph refund regression

This synthetic application uses ordinary `BaseChatModel`, native tool definitions, `MessagesState` and `ToolNode`. The graph constructor in `application.py` has no Fail2Test dependency. Only `runner.py` swaps the injected model/tools.

The original refund tool deliberately raises if its body is executed. The fixture wrapper must return the reviewed response instead; it never contacts a real payment system.

From the repository root:

```text
uv sync --locked --all-extras
uv run fail2test import examples/langgraph_refunds/failure.json --out local-artifacts/native-refund/case
uv run fail2test review local-artifacts/native-refund/case --reviewer local-owner
uv run fail2test validate local-artifacts/native-refund/case --runner broken --config examples/langgraph_refunds/fail2test.toml
uv run fail2test run local-artifacts/native-refund/case --runner fixed --config examples/langgraph_refunds/fail2test.toml
uv run fail2test export local-artifacts/native-refund/case --runner fixed --config examples/langgraph_refunds/fail2test.toml --out local-artifacts/native-refund/tests
uv run pytest local-artifacts/native-refund/tests/test_regression.py -q
```

`validate` succeeds because it reproduces the duplicate refund failure. The fixed runner uses the same graph factory with deduplication enabled and must pass the same reviewed rule. Output directories must be new; delete only your own generated artifacts or choose another destination for repeat trials.

## What changes in an existing application

Your graph factory continues accepting a model and tools. The test runner constructs `FixtureChatModel(context)`, wraps ordinary tools with `fixture_tool(context, original)`, and exposes the factory with `graph_runner`. No provider credentials, real clients or model calls are involved.

`failure.json` contains a static `langchain-chat.v1` request. `chat_request` and `chat_response` helpers build this fixture format from supported native messages and tool definitions. Tool names, descriptions, schemas, prompts, tool-call IDs and supplied JSON options participate in strict matching. Generated message IDs and response/usage metadata do not.

## Scope

Synchronous text chat, ordinary schema-backed tools, serialized graph scheduling and JSON-compatible state with native messages are supported in this example. Streaming, async/batched model calls, runtime-injected tool schemas, tool artifacts and arbitrary checkpoint restore remain outside this adapter scope. Tool schemas/validators and the rest of application code remain trusted executable code; replacing the tool body is not OS/network isolation.
