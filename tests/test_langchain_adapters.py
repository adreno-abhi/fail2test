from __future__ import annotations

import asyncio
import copy
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from typing import Annotated

import pytest

pytest.importorskip("langchain_core")
from langchain_core.caches import InMemoryCache  # noqa: E402
from langchain_core.globals import set_llm_cache  # noqa: E402
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage  # noqa: E402
from langchain_core.tools import InjectedToolCallId, tool  # noqa: E402

from fail2test import IncompleteExecutionError  # noqa: E402
from fail2test.execution import execute_case  # noqa: E402
from fail2test.integrations.langchain import (  # noqa: E402
    FixtureChatModel,
    chat_request,
    chat_response,
    fixture_tool,
    graph_output,
)
from fail2test.jsonio import canonical  # noqa: E402
from fail2test.models import Case  # noqa: E402


def model_case(case_data, *, request=None, response=None):
    case_data["model_fixtures"] = [
        {
            "id": "native-0",
            "slot": "chat",
            "ordinal": 0,
            "request": request or chat_request("Hello"),
            "response": response
            if response is not None
            else {"content": "Hello back", "tool_calls": []},
        }
    ]
    case_data["tool_fixtures"] = []
    case_data["rules"] = [
        {
            "id": "reply",
            "kind": "output",
            "pointer": "/reply",
            "operator": "eq",
            "expected": "Hello back",
            "requirement": "Return the recorded greeting in this scenario.",
        }
    ]
    return Case.model_validate(case_data)


def test_native_invoke_and_prompt_mismatch(case_data):
    case = model_case(case_data)

    def runner(data, context):
        return {"reply": FixtureChatModel(context).invoke("Hello").content}

    assert execute_case(case, runner).outcome == "pass"

    def changed(data, context):
        return {"reply": FixtureChatModel(context).invoke("Different prompt").content}

    result = execute_case(case, changed)
    assert result.execution_status == "incomplete"
    assert result.tooling_errors == ["UNMATCHED_MODEL_REQUEST"]


def test_normalization_preserves_semantics_ignores_generated_metadata():
    ai = AIMessage(
        content="",
        id="volatile-framework-id",
        response_metadata={"timing": 4},
        tool_calls=[{"name": "refund", "args": {"amount": 5}, "id": "call1", "type": "tool_call"}],
    )
    tool_result = ToolMessage(content='{"status":"ok"}', tool_call_id="call1")
    request = chat_request(
        [SystemMessage(content="Be careful"), HumanMessage(content="Refund"), ai, tool_result]
    )
    assert request == {
        "format": "langchain-chat.v1",
        "messages": [
            {"role": "system", "content": "Be careful"},
            {"role": "user", "content": "Refund"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"name": "refund", "args": {"amount": 5}, "id": "call1"}],
            },
            {
                "role": "tool",
                "content": '{"status":"ok"}',
                "tool_call_id": "call1",
                "status": "success",
            },
        ],
        "tools": [],
        "stop": None,
        "tool_choice": None,
        "options": {},
    }
    ai.id = "different-generated-id"
    assert chat_request([ai])["messages"][0]["tool_calls"][0]["id"] == "call1"
    assert "volatile-framework-id" not in json.dumps(request)


def test_binding_preserves_schema_and_options(case_data):
    @tool
    def search(query: str) -> str:
        """Find a synthetic record."""
        raise AssertionError("Original tool body must not run")

    request = chat_request(
        "Hello", tools=[search], tool_choice="search", options={"temperature": 0}
    )
    case = model_case(case_data, request=request)

    def runner(data, context):
        model = FixtureChatModel(context).bind_tools(
            [fixture_tool(context, search)], tool_choice="search", temperature=0
        )
        return {"reply": model.invoke("Hello").content}

    assert execute_case(case, runner).outcome == "pass"
    request_changed = copy.deepcopy(request)
    request_changed["options"]["temperature"] = 1
    case = model_case(case_data, request=request_changed)
    assert execute_case(case, runner).execution_status == "incomplete"


def test_global_model_cache_cannot_bypass_fixture_transport(case_data):
    set_llm_cache(InMemoryCache())
    try:
        case = model_case(case_data)

        def runner(data, context):
            model = FixtureChatModel(context)
            model.invoke("Hello")
            with suppress(IncompleteExecutionError):
                model.invoke("Hello")  # No ordinal 1 fixture: cached success must not bypass it.
            return {"reply": "Hello back"}

        result = execute_case(case, runner)
        assert result.execution_status == "incomplete"
        assert result.tooling_errors == ["UNMATCHED_MODEL_REQUEST"]
    finally:
        set_llm_cache(None)


@pytest.mark.parametrize(
    "response",
    [
        "not an object",
        {"content": 3},
        {"content": "ok", "unknown": True},
        {"content": "", "tool_calls": [{"name": "refund", "args": {}, "id": None}]},
    ],
)
def test_invalid_chat_response_latches_if_swallowed(case_data, response):
    case = model_case(case_data, response=response)

    def runner(data, context):
        with suppress(IncompleteExecutionError):
            FixtureChatModel(context).invoke("Hello")
        return {"reply": "Hello back"}

    result = execute_case(case, runner)
    assert result.execution_status == "incomplete"
    assert "INVALID_CHAT_RESPONSE" in result.tooling_errors


@pytest.mark.parametrize(
    "operation",
    ["async", "stream", "batch", "batch-as-completed", "async-batch", "unsupported-content"],
)
def test_unsupported_model_paths_latch(case_data, operation):
    case = model_case(case_data)

    def runner(data, context):
        model = FixtureChatModel(context)
        with suppress(IncompleteExecutionError):
            if operation == "async":
                asyncio.run(model.ainvoke("Hello"))
            elif operation == "stream":
                list(model.stream("Hello"))
            elif operation == "batch":
                model.batch(["Hello"])
            elif operation == "batch-as-completed":
                list(model.batch_as_completed(["Hello"]))
            elif operation == "async-batch":
                asyncio.run(model.abatch(["Hello"]))
            else:
                model.invoke(
                    [
                        HumanMessage(
                            content=[
                                {"type": "image_url", "image_url": "https://example.invalid/image"}
                            ]
                        )
                    ]
                )
        return {"reply": "Hello back"}

    assert execute_case(case, runner).execution_status == "incomplete"


def test_native_tool_result_roundtrip_and_key_order(case_data):
    @tool
    def refund(order_id: str, amount_cents: int) -> dict:
        """Refund an order."""
        raise AssertionError("Must not run")

    human = HumanMessage(content="Refund")
    ai = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "refund",
                "args": {"order_id": "ord-demo-001", "amount_cents": 500},
                "id": "refund-call",
                "type": "tool_call",
            }
        ],
    )
    tool_result = ToolMessage(
        content=json.dumps({"refund_id": "refund-demo-001", "status": "ok"}),
        tool_call_id="refund-call",
        name="refund",
    )
    case_data["model_fixtures"] = [
        {
            "id": "plan",
            "slot": "chat",
            "ordinal": 0,
            "request": chat_request([human], tools=[refund]),
            "response": chat_response(ai),
        },
        {
            "id": "finish",
            "slot": "chat",
            "ordinal": 1,
            "request": chat_request([human, ai, tool_result], tools=[refund]),
            "response": {"content": "Done", "tool_calls": []},
        },
    ]

    def runner(data, context):
        wrapped = fixture_tool(context, refund)
        model = FixtureChatModel(context).bind_tools([wrapped])
        plan = model.invoke([human])
        result = wrapped.invoke(plan.tool_calls[0])
        return {"reply": model.invoke([human, plan, result]).content}

    case = Case.model_validate(case_data)
    assert execute_case(case, runner).outcome == "pass"
    case_data["tool_fixtures"][0]["response"] = dict(
        reversed(list(case_data["tool_fixtures"][0]["response"].items()))
    )
    reordered = Case.model_validate(case_data)
    assert reordered.case_digest == case.case_digest
    assert execute_case(reordered, runner).outcome == "pass"


def test_tool_wrapper_never_executes_original_body(case_data):
    called = []

    @tool
    def refund(order_id: str, amount_cents: int) -> dict:
        """Refund an order in minor currency units."""
        called.append("real call")
        raise AssertionError("Original body must not execute")

    case_data["model_fixtures"] = []
    case = Case.model_validate(case_data)

    def runner(data, context):
        wrapped = fixture_tool(context, refund)
        assert wrapped.name == refund.name
        result = wrapped.invoke(
            {
                "type": "tool_call",
                "name": "refund",
                "args": {"order_id": "ord-demo-001", "amount_cents": 500},
                "id": "call-native",
            }
        )
        assert isinstance(result, ToolMessage)
        assert result.tool_call_id == "call-native"
        return {"tool_result": json.loads(result.content)}

    result = execute_case(case, runner)
    assert result.outcome == "pass", result.model_dump()
    assert called == []


@pytest.mark.parametrize("operation", ["invalid-args", "missing-fixture", "async"])
def test_tool_failures_latch_even_when_swallowed(case_data, operation):
    @tool
    def refund(order_id: str, amount_cents: int) -> dict:
        """Refund an order."""
        raise AssertionError("Must never execute")

    case_data["model_fixtures"] = []
    case_data["rules"] = [
        {
            "id": "no-delete",
            "kind": "forbidden_tool",
            "tool": "delete",
            "requirement": "Do not delete.",
        }
    ]
    case = Case.model_validate(case_data)

    def runner(data, context):
        wrapped = fixture_tool(context, refund)
        with suppress(IncompleteExecutionError):
            if operation == "async":
                asyncio.run(wrapped.ainvoke({"order_id": "ord-demo-001", "amount_cents": 500}))
            elif operation == "invalid-args":
                wrapped.invoke({"amount_cents": "not a number"})
            else:
                wrapped.invoke({"order_id": "unknown", "amount_cents": 500})
        return {}

    assert execute_case(case, runner).execution_status == "incomplete"


def test_serial_thread_handoff_and_scope_cleanup(case_data):
    case_data["model_fixtures"] = []
    case = Case.model_validate(case_data)

    def runner(data, context):
        with context.serial_execution(), ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(
                context.tools.call, "refund", {"order_id": "ord-demo-001", "amount_cents": 500}
            ).result()
        return {}

    assert execute_case(case, runner).outcome == "pass"

    def after_scope(data, context):
        with context.serial_execution():
            pass
        with ThreadPoolExecutor(max_workers=1) as pool, suppress(IncompleteExecutionError):
            pool.submit(context.tools.call, "refund", {}).result()
        return {}

    assert execute_case(case, after_scope).execution_status == "incomplete"


def test_overlapping_transport_calls_are_rejected(case_data, monkeypatch):
    import fail2test.execution as execution

    case_data["model_fixtures"] = []
    case = Case.model_validate(case_data)
    entered = threading.Event()
    release = threading.Event()
    original = execution.canonical

    def paused(value):
        if isinstance(value, dict) and "order_id" in value:
            entered.set()
            assert release.wait(3)
        return original(value)

    monkeypatch.setattr(execution, "canonical", paused)

    def runner(data, context):
        with context.serial_execution(), ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(
                context.tools.call, "refund", {"order_id": "ord-demo-001", "amount_cents": 500}
            )
            assert entered.wait(3)
            try:
                with suppress(IncompleteExecutionError):
                    pool.submit(context.tools.call, "refund", {}).result()
            finally:
                release.set()
            first.result()
        return {}

    result = execute_case(case, runner)
    assert result.execution_status == "incomplete"
    assert "UNSUPPORTED_CONCURRENCY" in result.tooling_errors


def test_native_graph_output_is_json_and_rejects_opaque_values():
    output = graph_output(
        {"messages": [HumanMessage(content="Hello"), AIMessage(content="Answer")]}
    )
    canonical(output)
    assert output["messages"][1]["role"] == "assistant"
    with pytest.raises(Exception, match="INVALID_JSON_VALUE"):
        graph_output({"opaque": object()})


@pytest.mark.parametrize("kind", ["artifact", "async", "injected"])
def test_advanced_tool_schemas_are_rejected_without_running_body(case_data, kind):
    @tool(response_format="content_and_artifact")
    def artifact_tool(query: str) -> tuple:
        """Return a tool artifact."""
        raise AssertionError("Body must not execute")

    @tool
    async def async_tool(query: str) -> str:
        """Return async output."""
        raise AssertionError("Body must not execute")

    @tool
    def injected_tool(query: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> str:
        """Needs injected call context."""
        raise AssertionError("Body must not execute")

    original = {"artifact": artifact_tool, "async": async_tool, "injected": injected_tool}[kind]
    case_data["model_fixtures"] = []
    case_data["rules"] = [
        {"id": "no-delete", "kind": "forbidden_tool", "tool": "delete", "requirement": "No delete."}
    ]

    def runner(data, context):
        with suppress(IncompleteExecutionError):
            fixture_tool(context, original)
        return {}

    assert execute_case(Case.model_validate(case_data), runner).execution_status == "incomplete"


def test_duplicate_bound_tool_schemas_latch(case_data):
    @tool
    def search(query: str) -> str:
        """Search a record."""
        raise AssertionError

    def runner(data, context):
        with suppress(IncompleteExecutionError):
            FixtureChatModel(context).bind_tools([search, search])
        return {}

    assert "UNSUPPORTED_TOOL_SCHEMA" in execute_case(model_case(case_data), runner).tooling_errors


@pytest.mark.parametrize(
    "message",
    [
        AIMessage(content="answer", additional_kwargs={"provider_specific": "private payload"}),
        AIMessage(content="answer", unknown_semantic_field="unsupported"),
        AIMessage(
            content="",
            invalid_tool_calls=[
                {
                    "name": "refund",
                    "args": "bad-json",
                    "id": "bad",
                    "error": "parse error",
                    "type": "invalid_tool_call",
                }
            ],
        ),
        ToolMessage(content="answer", tool_call_id="call", artifact={"hidden": "value"}),
    ],
)
def test_unknown_native_message_semantics_are_not_silently_dropped(case_data, message):
    def runner(data, context):
        with suppress(IncompleteExecutionError):
            FixtureChatModel(context).invoke([message])
        return {}

    result = execute_case(model_case(case_data), runner)
    assert result.execution_status == "incomplete"
    assert "private payload" not in result.model_dump_json()


@pytest.mark.parametrize(
    "operation", ["generate-batch", "agenerate", "astream", "abatch-as-completed"]
)
def test_other_native_execution_paths_reject_before_fallback(case_data, operation):
    async def consume(iterator):
        async for _ in iterator:
            pass

    def runner(data, context):
        model = FixtureChatModel(context)
        with suppress(IncompleteExecutionError):
            if operation == "generate-batch":
                model.generate([[HumanMessage(content="Hello")], [HumanMessage(content="Hello")]])
            elif operation == "agenerate":
                asyncio.run(model.agenerate([[HumanMessage(content="Hello")]]))
            elif operation == "astream":
                asyncio.run(consume(model.astream("Hello")))
            else:
                asyncio.run(consume(model.abatch_as_completed(["Hello"])))
        return {}

    assert execute_case(model_case(case_data), runner).execution_status == "incomplete"
