from __future__ import annotations

from typing import TypedDict

import pytest

from fail2test.execution import execute_case
from fail2test.integrations.langgraph import graph_runner

pytest.importorskip("langgraph")
from langgraph.graph import END, START, StateGraph  # noqa: E402


class State(TypedDict, total=False):
    order_id: str
    amount_cents: int
    context: dict
    actions: list
    refunds: int


def factory(context, fixed):
    def plan(state):
        result = context.model.complete(
            "refund-plan",
            {
                "task": "plan_refund",
                "order_id": state["order_id"],
                "amount_cents": state["amount_cents"],
            },
        )
        return {"actions": result["tool_calls"]}

    def act(state):
        seen = set()
        count = 0
        for action in state["actions"]:
            order = action["arguments"]["order_id"]
            if fixed and order in seen:
                continue
            seen.add(order)
            context.tools.call(action["tool"], action["arguments"])
            count += 1
        return {"refunds": count}

    graph = StateGraph(State)
    graph.add_node("plan", plan)
    graph.add_node("act", act)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "act")
    graph.add_edge("act", END)
    return graph.compile()


@pytest.mark.integration
def test_real_langgraph_uses_same_fixture_contract(case):
    broken = execute_case(case, graph_runner(lambda context: factory(context, False)))
    fixed = execute_case(case, graph_runner(lambda context: factory(context, True)))
    assert broken.execution_status == "complete", broken.model_dump()
    assert broken.outcome == "fail"
    assert fixed.outcome == "pass", fixed.model_dump()
