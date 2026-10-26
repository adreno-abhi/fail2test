from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from importlib.resources import files

import pytest

from fail2test import IncompleteExecutionError
from fail2test.execution import execute_case
from fail2test.models import Case


def example_runner():
    namespace = {}
    exec(files("fail2test").joinpath("data/refund_app.py.txt").read_text(), namespace)
    return namespace


def test_broken_and_fixed_execute_same_case(case):
    app = example_runner()
    broken = execute_case(case, app["broken"])
    fixed = execute_case(case, app["fixed"])
    assert broken.execution_status == fixed.execution_status == "complete"
    assert broken.outcome == "fail"
    assert fixed.outcome == "pass"
    assert len(broken.observed_calls) == 2
    assert len(fixed.observed_calls) == 1
    with pytest.raises(AssertionError, match="one-refund-per-order"):
        broken.assert_passed()
    fixed.assert_passed()


def test_missing_tool_fixture_never_passes(case_data):
    case_data["tool_fixtures"] = []
    result = execute_case(Case.model_validate(case_data), example_runner()["fixed"])
    assert result.execution_status == "incomplete"
    assert result.outcome == "not_evaluated"
    assert "UNMATCHED_TOOL_REQUEST" in result.tooling_errors
    with pytest.raises(IncompleteExecutionError):
        result.assert_passed()


def test_swallowed_mismatch_is_still_incomplete(case):
    def runner(data, context):
        with suppress(IncompleteExecutionError):
            context.tools.call("unapproved", {})
        return {"status": "ok"}

    result = execute_case(case, runner)
    assert result.execution_status == "incomplete"
    assert not result.rule_results


def test_changed_prompt_is_not_validated_with_old_response(case):
    def runner(data, context):
        return context.model.complete("refund-plan", {"task": "different prompt"})

    result = execute_case(case, runner)
    assert result.tooling_errors == ["UNMATCHED_MODEL_REQUEST"]
    assert result.outcome == "not_evaluated"


def test_no_op_cannot_pass_required_action(case):
    result = execute_case(case, lambda data, context: {})
    assert result.outcome == "not_evaluated"  # Required model fixture was never consumed.


def test_no_op_without_model_still_fails_rule(case_data):
    case_data["model_fixtures"] = []
    result = execute_case(Case.model_validate(case_data), lambda data, context: {})
    assert result.execution_status == "complete"
    assert result.outcome == "fail"


def test_nonrepeatable_fixture_cannot_be_reused(case_data):
    case_data["tool_fixtures"][0]["repeatable"] = False
    result = execute_case(Case.model_validate(case_data), example_runner()["broken"])
    assert result.execution_status == "incomplete"
    assert "TOOL_FIXTURE_EXHAUSTED" in result.tooling_errors


def test_application_error_does_not_leak_exception(case):
    def runner(data, context):
        raise ValueError("SECRET-EXCEPTION-CANARY")

    result = execute_case(case, runner)
    assert result.execution_status == "error"
    assert "SECRET-EXCEPTION-CANARY" not in json.dumps(result.model_dump())


def test_runner_raised_incomplete_is_not_green(case):
    def runner(data, context):
        raise IncompleteExecutionError("MISSING_STATE", "test")

    assert execute_case(case, runner).execution_status == "incomplete"


def test_unsupported_async_is_explicit(case):
    async def runner(data, context):
        return {}

    result = execute_case(case, runner)
    assert "UNSUPPORTED_ASYNC" in result.tooling_errors
    assert result.execution_status == "incomplete"


def test_threaded_transport_is_explicitly_unsupported(case):
    def runner(data, context):
        with ThreadPoolExecutor(max_workers=1) as pool, suppress(IncompleteExecutionError):
            pool.submit(context.tools.call, "refund", data).result()
        return {}

    result = execute_case(case, runner)
    assert "UNSUPPORTED_CONCURRENCY" in result.tooling_errors
    assert result.execution_status == "incomplete"


def test_runner_cannot_mutate_fixture_responses(case):
    def runner(data, context):
        request = {
            "task": "plan_refund",
            "order_id": data["order_id"],
            "amount_cents": data["amount_cents"],
        }
        plan = context.model.complete("refund-plan", request)
        plan["tool_calls"].clear()
        return {}

    original = case.case_digest
    execute_case(case, runner)
    assert len(case.model_fixtures[0].response["tool_calls"]) == 2
    assert case.case_digest == original
