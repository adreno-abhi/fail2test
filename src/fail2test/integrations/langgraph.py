"""A narrow graph-factory runner using explicitly injected fixture transports.

This does not adapt arbitrary chat clients or restore external checkpoints.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fail2test.execution import RunContext, Runner


def graph_runner(factory: Callable[[RunContext], Any]) -> Runner:
    """Wrap a serial synchronous graph factory that accepts injected dependencies.

    The graph receives the case input as initial state. Its return value must be JSON.
    Import LangGraph inside your factory so core workflows need no framework extra.
    """

    def run(data: dict[str, Any], context: RunContext) -> Any:
        # Explicitly disable LangSmith tracing for this supported adapter invocation.
        from langsmith.run_helpers import tracing_context

        from fail2test.errors import Fail2TestError
        from fail2test.integrations.langchain import graph_output

        with tracing_context(enabled=False), context.serial_execution():
            graph = factory(context)
            result = graph.invoke(data, config={"max_concurrency": 1})
            try:
                return graph_output(result)
            except Fail2TestError as exc:
                context.reject(exc.code)

    return run
