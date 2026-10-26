"""Only the test runner knows about Fail2Test; graph construction stays unchanged."""

from application import build_graph, refund

from fail2test.integrations.langchain import FixtureChatModel, fixture_tool
from fail2test.integrations.langgraph import graph_runner


def dependencies(context, *, fixed):
    model = FixtureChatModel(context, slot="refund-chat")
    tools = [fixture_tool(context, refund)]
    return build_graph(model, tools, deduplicate=fixed)


broken = graph_runner(lambda context: dependencies(context, fixed=False))
fixed = graph_runner(lambda context: dependencies(context, fixed=True))
