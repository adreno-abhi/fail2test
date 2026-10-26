"""Native synchronous chat/tool replacements backed only by reviewed fixtures.

Importing this optional module requires the ``langgraph`` extra. No provider client
is constructed. Application tools and schema validators remain trusted local code.
"""

from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator, Callable, Iterator, Sequence
from typing import Any, Never

from langchain_core.callbacks import AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    convert_to_messages,
)
from langchain_core.outputs import ChatGeneration, ChatResult, LLMResult
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langsmith.run_helpers import tracing_context
from pydantic import BaseModel, PrivateAttr

from fail2test.errors import Fail2TestError, IncompleteExecutionError
from fail2test.execution import RunContext
from fail2test.jsonio import canonical


def _unsupported(code: str) -> Never:
    raise Fail2TestError(
        code, "Use supported synchronous text messages and ordinary JSON tools.", 3
    )


def message_json(message: BaseMessage) -> dict[str, Any]:
    """Preserve semantic text/tool fields; exclude framework IDs, usage and response metadata."""
    if not isinstance(message.content, str) or message.additional_kwargs or message.model_extra:
        return _unsupported("UNSUPPORTED_CHAT_CONTENT")
    roles = {
        SystemMessage: "system",
        HumanMessage: "user",
        AIMessage: "assistant",
        ToolMessage: "tool",
    }
    if type(message) not in roles:
        return _unsupported("UNSUPPORTED_CHAT_MESSAGE")
    result: dict[str, Any] = {"role": roles[type(message)], "content": message.content}
    if message.name is not None:
        result["name"] = message.name
    if isinstance(message, AIMessage):
        if message.invalid_tool_calls:
            return _unsupported("INVALID_CHAT_TOOL_CALL")
        result["tool_calls"] = [
            {"name": call["name"], "args": call["args"], "id": call["id"]}
            for call in message.tool_calls
        ]
    if isinstance(message, ToolMessage):
        if message.artifact is not None:
            return _unsupported("UNSUPPORTED_TOOL_ARTIFACT")
        result["tool_call_id"] = message.tool_call_id
        result["status"] = message.status
    canonical(result)
    return result


def _tools_json(
    tools: Sequence[dict[str, Any] | type | Callable[..., Any] | BaseTool],
) -> list[dict[str, Any]]:
    try:
        schemas = [convert_to_openai_tool(tool) for tool in tools]
        names = [tool["function"]["name"] for tool in schemas]
        if len(names) != len(set(names)) or any(tool.get("type") != "function" for tool in schemas):
            return _unsupported("UNSUPPORTED_TOOL_SCHEMA")
        canonical(schemas)
        return schemas
    except Fail2TestError:
        raise
    except Exception as exc:
        raise Fail2TestError(
            "UNSUPPORTED_TOOL_SCHEMA", "Use ordinary JSON function-tool schemas.", 3
        ) from exc


def chat_request(
    input: LanguageModelInput,
    *,
    tools: Sequence[dict[str, Any] | type | Callable[..., Any] | BaseTool] = (),
    stop: list[str] | None = None,
    tool_choice: str | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the exact versioned request for a recorded native model interaction."""
    try:
        if stop is not None and (
            not isinstance(stop, list) or any(not isinstance(item, str) for item in stop)
        ):
            _unsupported("UNSUPPORTED_CHAT_REQUEST")
        if tool_choice is not None and not isinstance(tool_choice, str):
            _unsupported("UNSUPPORTED_CHAT_REQUEST")
        if isinstance(input, PromptValue):
            messages = input.to_messages()
        elif isinstance(input, str):
            messages = [HumanMessage(content=input)]
        else:
            messages = convert_to_messages(input)
        request = {
            "format": "langchain-chat.v1",
            "messages": [message_json(message) for message in messages],
            "tools": _tools_json(tools),
            "stop": stop,
            "tool_choice": tool_choice,
            "options": options or {},
        }
        canonical(request)
        return request
    except Fail2TestError:
        raise
    except Exception as exc:
        raise Fail2TestError(
            "UNSUPPORTED_CHAT_REQUEST", "Cannot normalize this chat request.", 3
        ) from exc


def chat_response(message: AIMessage) -> dict[str, Any]:
    """Convert an AIMessage into the data-only response shape used in fixtures."""
    result = message_json(message)
    result.pop("role")
    return result


def graph_output(value: Any) -> Any:
    """Convert native message state into JSON without stringifying unknown objects."""
    if isinstance(value, BaseMessage):
        return message_json(value)
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            return _unsupported("UNSUPPORTED_GRAPH_OUTPUT")
        return {key: graph_output(child) for key, child in value.items()}
    if isinstance(value, list):
        return [graph_output(child) for child in value]
    canonical(value)
    return value


class FixtureChatModel(BaseChatModel):
    """Native invoke/bind_tools with strict fixtures, no model SDK, key, or live fallback."""

    fixture_slot: str = "chat"
    _context: RunContext = PrivateAttr()

    def __init__(self, context: RunContext, *, slot: str = "chat") -> None:
        if not isinstance(slot, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}", slot):
            context.reject("INVALID_CHAT_SLOT")
        super().__init__(cache=False)
        self.fixture_slot = slot
        self._context = context

    @property
    def _llm_type(self) -> str:
        return "fail2test-fixture"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"fixture_slot": self.fixture_slot}

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable[..., Any] | BaseTool],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, AIMessage]:
        try:
            return self.bind(tools=_tools_json(tools), tool_choice=tool_choice, **kwargs)
        except Fail2TestError as exc:
            self._context.reject(exc.code)

    def invoke(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        try:
            with tracing_context(enabled=False):
                return super().invoke(input, config, stop=stop, **kwargs)
        except IncompleteExecutionError:
            raise
        except Exception:
            self._context.reject("UNSUPPORTED_CHAT_REQUEST")

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        tools = kwargs.pop("tools", [])
        tool_choice = kwargs.pop("tool_choice", None)
        try:
            request = chat_request(
                messages, tools=tools, stop=stop, tool_choice=tool_choice, options=kwargs
            )
            response = self._context.model.complete(self.fixture_slot, request)
            if not isinstance(response, dict) or set(response) - {"content", "tool_calls", "name"}:
                self._context.reject("INVALID_CHAT_RESPONSE")
            if not isinstance(response.get("content"), str) or not isinstance(
                response.get("tool_calls", []), list
            ):
                self._context.reject("INVALID_CHAT_RESPONSE")
            for call in response.get("tool_calls", []):
                if not isinstance(call, dict) or set(call) != {"name", "args", "id"}:
                    self._context.reject("INVALID_CHAT_RESPONSE")
                if (
                    not isinstance(call["name"], str)
                    or not isinstance(call["args"], dict)
                    or not isinstance(call["id"], str)
                ):
                    self._context.reject("INVALID_CHAT_RESPONSE")
            call_ids = [call["id"] for call in response.get("tool_calls", [])]
            if any(not item for item in call_ids) or len(call_ids) != len(set(call_ids)):
                self._context.reject("INVALID_CHAT_RESPONSE")
            if response.get("name") is not None and not isinstance(response["name"], str):
                self._context.reject("INVALID_CHAT_RESPONSE")
            message = AIMessage(**response)
            message_json(message)
            return ChatResult(generations=[ChatGeneration(message=message)])
        except IncompleteExecutionError:
            raise
        except Fail2TestError as exc:
            self._context.reject(exc.code)
        except Exception:
            self._context.reject("INVALID_CHAT_RESPONSE")

    def generate(self, messages: list[list[BaseMessage]], *args: Any, **kwargs: Any) -> LLMResult:
        if len(messages) != 1:
            self._context.reject("UNSUPPORTED_CHAT_BATCH")
        try:
            with tracing_context(enabled=False):
                return super().generate(messages, *args, **kwargs)
        except IncompleteExecutionError:
            raise
        except Exception:
            self._context.reject("UNSUPPORTED_CHAT_REQUEST")

    async def agenerate(
        self, messages: list[list[BaseMessage]], *args: Any, **kwargs: Any
    ) -> LLMResult:
        self._context.reject("UNSUPPORTED_CHAT_ASYNC")

    async def ainvoke(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> AIMessage:
        self._context.reject("UNSUPPORTED_CHAT_ASYNC")

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: AsyncCallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        self._context.reject("UNSUPPORTED_CHAT_ASYNC")

    def stream(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> Iterator[AIMessageChunk]:
        self._context.reject("UNSUPPORTED_CHAT_STREAMING")
        yield from ()

    async def astream(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[AIMessageChunk]:
        self._context.reject("UNSUPPORTED_CHAT_STREAMING")
        yield AIMessageChunk(content="")

    def batch(
        self,
        inputs: list[LanguageModelInput],
        config: RunnableConfig | list[RunnableConfig] | None = None,
        *,
        return_exceptions: bool = False,
        **kwargs: Any,
    ) -> list[AIMessage]:
        self._context.reject("UNSUPPORTED_CHAT_BATCH")

    def batch_as_completed(
        self,
        inputs: Sequence[LanguageModelInput],
        config: RunnableConfig | Sequence[RunnableConfig] | None = None,
        *,
        return_exceptions: bool = False,
        **kwargs: Any,
    ) -> Iterator[Never]:
        yield self._context.reject("UNSUPPORTED_CHAT_BATCH")

    async def abatch(
        self,
        inputs: list[LanguageModelInput],
        config: RunnableConfig | list[RunnableConfig] | None = None,
        *,
        return_exceptions: bool = False,
        **kwargs: Any,
    ) -> list[AIMessage]:
        self._context.reject("UNSUPPORTED_CHAT_BATCH")

    async def abatch_as_completed(
        self,
        inputs: Sequence[LanguageModelInput],
        config: RunnableConfig | Sequence[RunnableConfig] | None = None,
        *,
        return_exceptions: bool = False,
        **kwargs: Any,
    ) -> AsyncIterator[Never]:
        yield self._context.reject("UNSUPPORTED_CHAT_BATCH")


class _FixtureTool(StructuredTool):
    _context: RunContext = PrivateAttr()

    def __init__(self, context: RunContext, original: BaseTool) -> None:
        if isinstance(original, StructuredTool) and original.func is None:
            context.reject("UNSUPPORTED_TOOL_ASYNC")
        schema = original.args_schema or original.get_input_schema()
        if isinstance(schema, dict):
            raw_schema = schema
        elif isinstance(schema, type) and issubclass(schema, BaseModel):
            raw_schema = schema.model_json_schema()
        else:
            context.reject("UNSUPPORTED_TOOL_SCHEMA")
        public_schema = _tools_json([original])[0]["function"].get("parameters", {})
        if original.response_format != "content" or set(raw_schema.get("properties", {})) != set(
            public_schema.get("properties", {})
        ):
            context.reject("UNSUPPORTED_TOOL_SCHEMA")

        def dispatch(**arguments: Any) -> Any:
            # Canonicalize structured response ordering before the SDK turns it into
            # ToolMessage text, so JSON key order cannot change a later model request.
            response = context.tools.call(original.name, arguments)
            return json.loads(canonical(response))

        super().__init__(
            name=original.name,
            description=original.description,
            args_schema=schema,
            func=dispatch,
            return_direct=original.return_direct,
        )
        self._context = context

    def invoke(self, input: Any, config: RunnableConfig | None = None, **kwargs: Any) -> Any:
        try:
            with tracing_context(enabled=False):
                return super().invoke(input, config, **kwargs)
        except IncompleteExecutionError:
            raise
        except Exception:
            self._context.reject("INVALID_TOOL_REQUEST")

    def run(self, *args: Any, **kwargs: Any) -> Any:
        try:
            with tracing_context(enabled=False):
                return super().run(*args, **kwargs)
        except IncompleteExecutionError:
            raise
        except Exception:
            self._context.reject("INVALID_TOOL_REQUEST")

    async def ainvoke(self, input: Any, config: RunnableConfig | None = None, **kwargs: Any) -> Any:
        self._context.reject("UNSUPPORTED_TOOL_ASYNC")

    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        self._context.reject("UNSUPPORTED_TOOL_ASYNC")


def fixture_tool(context: RunContext, original: BaseTool) -> BaseTool:
    """Keep a tool's ordinary schema/name and replace its implementation with fixtures."""
    try:
        return _FixtureTool(context, original)
    except IncompleteExecutionError:
        raise
    except Fail2TestError as exc:
        context.reject(exc.code)
    except Exception:
        context.reject("UNSUPPORTED_TOOL_SCHEMA")
