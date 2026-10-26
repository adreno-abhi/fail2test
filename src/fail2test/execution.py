"""Explicit fixture transports. No client monkeypatching or live-tool fallback."""

from __future__ import annotations

import copy
import inspect
import platform
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any, Literal, Never

from fail2test.errors import Fail2TestError, IncompleteExecutionError
from fail2test.jsonio import canonical
from fail2test.models import Case, Observation, RunResult
from fail2test.rules import evaluate

MAX_INTERACTIONS = 10_000


class _State:
    def __init__(self, case: Case) -> None:
        self.case = case
        self.calls: list[Observation] = []
        self.errors: list[str] = []
        self.models_used: set[str] = set()
        self.tools_used: dict[str, int] = {}
        self.ordinals: dict[str, int] = {}
        self.thread_id = threading.get_ident()
        self.serial_scope_depth = 0
        self.interaction_lock = threading.Lock()

    def fail(self, code: str) -> Any:
        self.errors.append(code)
        raise IncompleteExecutionError(code, "No matching approved fixture; no live call was made.")

    @contextmanager
    def interaction(self) -> Iterator[None]:
        if threading.get_ident() != self.thread_id and not self.serial_scope_depth:
            self.fail("UNSUPPORTED_CONCURRENCY")
        if not self.interaction_lock.acquire(blocking=False):
            self.fail("UNSUPPORTED_CONCURRENCY")
        try:
            yield
        finally:
            self.interaction_lock.release()


class FixtureModel:
    def __init__(self, state: _State) -> None:
        self._state = state

    def complete(self, slot: str, request: dict[str, Any]) -> Any:
        with self._state.interaction():
            return self._complete(slot, request)

    def _complete(self, slot: str, request: dict[str, Any]) -> Any:
        state = self._state
        ordinal = state.ordinals.get(slot, 0)
        state.ordinals[slot] = ordinal + 1
        if sum(state.ordinals.values()) > MAX_INTERACTIONS:
            return state.fail("INTERACTION_LIMIT")
        for fixture in state.case.model_fixtures:
            if fixture.slot == slot and fixture.ordinal == ordinal:
                if canonical(fixture.request) != canonical(request):
                    return state.fail("UNMATCHED_MODEL_REQUEST")
                state.models_used.add(fixture.id)
                return copy.deepcopy(fixture.response)
        return state.fail("UNMATCHED_MODEL_REQUEST")


class FixtureTools:
    def __init__(self, state: _State) -> None:
        self._state = state

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        with self._state.interaction():
            return self._call(name, arguments)

    def _call(self, name: str, arguments: dict[str, Any]) -> Any:
        state = self._state
        if len(state.calls) >= MAX_INTERACTIONS:
            return state.fail("INTERACTION_LIMIT")
        observation = Observation(
            index=len(state.calls), tool=name, arguments=copy.deepcopy(arguments)
        )
        state.calls.append(observation)
        for fixture in state.case.tool_fixtures:
            if fixture.tool == name and canonical(fixture.arguments) == canonical(arguments):
                if state.tools_used.get(fixture.id, 0) and not fixture.repeatable:
                    return state.fail("TOOL_FIXTURE_EXHAUSTED")
                state.tools_used[fixture.id] = state.tools_used.get(fixture.id, 0) + 1
                observation.fixture_id = fixture.id
                return copy.deepcopy(fixture.response)
        return state.fail("UNMATCHED_TOOL_REQUEST")


class RunContext:
    """Dependencies an application runner explicitly injects into its own code."""

    def __init__(self, case: Case) -> None:
        self._state = _State(case)
        self.model = FixtureModel(self._state)
        self.tools = FixtureTools(self._state)

    def reject(self, code: str) -> Never:
        """Latch an adapter failure even if application code catches its exception."""
        import re

        if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", code):
            code = "INVALID_ADAPTER_ERROR_CODE"
        self._state.errors.append(code)
        raise IncompleteExecutionError(code, "The adapter cannot establish supported execution.")

    @contextmanager
    def serial_execution(self) -> Iterator[None]:
        """Allow thread handoff inside an explicitly serialized executor, not parallel calls."""
        if threading.get_ident() != self._state.thread_id:
            self.reject("UNSUPPORTED_CONCURRENCY")
        self._state.serial_scope_depth += 1
        try:
            yield
        finally:
            self._state.serial_scope_depth -= 1


Runner = Callable[[dict[str, Any], RunContext], Any]


def execute_case(case: Case, runner: Runner) -> RunResult:
    """Execute trusted code in-process. The supervised workflow supplies the timeout.

    This low-level interface intentionally does not authenticate review records. Use
    Case.load(...).run(...) for the reviewed file workflow.
    """
    started = time.perf_counter()
    context = RunContext(case)
    state = context._state
    output = None
    error = False
    try:
        output = runner(copy.deepcopy(case.input), context)
        if inspect.isawaitable(output):
            if inspect.iscoroutine(output):
                output.close()
            state.fail("UNSUPPORTED_ASYNC")
        canonical(output)
    except IncompleteExecutionError as exc:
        state.errors.append(exc.code)
    except Exception:
        # Exception strings can contain raw secrets or arbitrary application output.
        error = True
        state.errors.append("RUNNER_ERROR")
    missing_models = [f.id for f in case.model_fixtures if f.id not in state.models_used]
    if missing_models and not state.errors:
        state.errors.append("UNUSED_MODEL_FIXTURE")
    status: Literal["complete", "incomplete", "error"]
    outcome: Literal["pass", "fail", "not_evaluated"]
    if error:
        status, outcome = "error", "not_evaluated"
    elif state.errors:
        status, outcome = "incomplete", "not_evaluated"
    else:
        status, outcome = "complete", "pass"
    rules = evaluate(case, state.calls, output) if status == "complete" else []
    if status == "complete" and not all(rule.passed for rule in rules):
        outcome = "fail"
    try:
        return RunResult(
            case_id=case.case_id,
            case_digest=case.case_digest,
            execution_status=status,
            outcome=outcome,
            rule_results=rules,
            observed_calls=state.calls,
            output=output if status == "complete" else None,
            unused_fixtures=missing_models
            + [f.id for f in case.tool_fixtures if f.id not in state.tools_used],
            tooling_errors=list(dict.fromkeys(state.errors)),
            environment={"python": platform.python_version(), "platform": platform.system()},
            duration_ms=(time.perf_counter() - started) * 1000,
        )
    except (ValueError, Fail2TestError) as exc:
        raise Fail2TestError(
            "INVALID_EXECUTION_RESULT", "Runner returned unsupported evidence.", 4
        ) from exc
