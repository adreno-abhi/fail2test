"""Closed, JSON-only behavioral predicates over fresh observations."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from fail2test.jsonio import canonical
from fail2test.models import (
    Case,
    ForbiddenTool,
    MaxToolCalls,
    Observation,
    OutputRule,
    PredicateRule,
    RuleResult,
    ToolArgument,
    ToolCallCount,
)

MISSING = object()


def pointer(value: Any, path: str) -> Any:
    current = value
    for encoded in path.split("/")[1:]:
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            current = current.get(token, MISSING)
        elif isinstance(current, list) and token.isascii() and token.isdigit():
            if str(int(token)) != token or int(token) >= len(current):
                return MISSING
            current = current[int(token)]
        else:
            return MISSING
        if current is MISSING:
            return MISSING
    return current


def predicate(value: Any, rule: PredicateRule) -> bool:
    if value is MISSING:
        return False
    if rule.operator == "eq":
        return canonical(value) == canonical(rule.expected)
    if rule.operator == "in":
        assert isinstance(rule.expected, list)
        return any(canonical(value) == canonical(item) for item in rule.expected)
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    expected = rule.expected
    assert isinstance(expected, int | float) and not isinstance(expected, bool)
    return bool(value <= expected if rule.operator == "lte" else value >= expected)


def evaluate(case: Case, calls: list[Observation], output: Any) -> list[RuleResult]:
    results = []
    for rule in case.rules:
        matching = [call for call in calls if getattr(rule, "tool", None) == call.tool]
        indices = [call.index for call in matching]
        passed = False
        reason = "Condition not satisfied."
        if isinstance(rule, ToolCallCount):
            groups: dict[bytes, int] = defaultdict(int)
            missing = False
            for call in matching:
                values = [pointer(call.arguments, key) for key in rule.group_by]
                if any(value is MISSING for value in values):
                    missing = True
                    break
                groups[canonical(values)] += 1
            passed = (
                not missing
                and (bool(matching) or not rule.require_any)
                and all(rule.min_calls <= count <= rule.max_calls for count in groups.values())
            )
            reason = f"Observed {len(matching)} matching calls across {len(groups)} groups."
        elif isinstance(rule, ToolArgument):
            passed = (bool(matching) or not rule.require_any) and all(
                predicate(pointer(call.arguments, rule.pointer), rule) for call in matching
            )
            reason = f"Checked argument predicate on {len(matching)} matching calls."
        elif isinstance(rule, OutputRule):
            passed = predicate(pointer(output, rule.pointer), rule)
            reason = "Checked returned output predicate."
        elif isinstance(rule, ForbiddenTool):
            passed = not matching
            reason = f"Observed {len(matching)} forbidden calls."
        elif isinstance(rule, MaxToolCalls):
            passed = len(calls) <= rule.max_calls
            indices = [call.index for call in calls]
            reason = f"Observed {len(calls)} calls; maximum {rule.max_calls}."
        results.append(
            RuleResult(rule_id=rule.id, passed=passed, reason=reason, observation_indices=indices)
        )
    return results
