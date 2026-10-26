"""An existing-style native graph: its constructor accepts model/tools, not RunContext.

The declared real refund body is intentionally unusable in this example. Fixture
tests wrap its definition and must never execute it or contact a payment system.
"""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool, tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


@tool
def refund(order_id: str, amount_cents: int) -> dict[str, Any]:
    """Refund an order once for the approved amount in minor currency units."""
    raise RuntimeError("The real payment implementation must never run in fixture tests.")


def build_graph(model: BaseChatModel, tools: list[BaseTool], *, deduplicate: bool = False) -> Any:
    bound_model = model.bind_tools(tools)

    def plan(state: MessagesState) -> dict[str, Any]:
        response = bound_model.invoke(state["messages"])
        if deduplicate:
            seen = set()
            calls = []
            for call in response.tool_calls:
                identity = (call["name"], call["args"].get("order_id"))
                if identity not in seen:
                    calls.append(call)
                    seen.add(identity)
            response = AIMessage(content=response.content, tool_calls=calls)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("plan", plan)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "tools")
    graph.add_edge("tools", END)
    return graph.compile()
