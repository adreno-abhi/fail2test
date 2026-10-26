from __future__ import annotations

import pytest

from fail2test.models import Case, Observation
from fail2test.rules import MISSING, evaluate, pointer


@pytest.mark.parametrize(
    "document,path,expected",
    [
        ({"a/b": {"~": 3}}, "/a~1b/~0", 3),
        ([1, 2], "/1", 2),
        ({"": 9}, "/", 9),
        ({"x": 1}, "", {"x": 1}),
    ],
)
def test_json_pointers(document, path, expected):
    assert pointer(document, path) == expected


@pytest.mark.parametrize("path", ["/01", "/-", "/2", "/-1"])
def test_missing_array_indices(path):
    assert pointer([1, 2], path) is MISSING


@pytest.mark.parametrize(
    "rule,output,calls,expected",
    [
        ({"kind": "forbidden_tool", "tool": "delete"}, {}, [], True),
        ({"kind": "forbidden_tool", "tool": "delete"}, {}, [("delete", {})], False),
        ({"kind": "max_tool_calls", "max_calls": 0}, {}, [("refund", {})], False),
        (
            {"kind": "output", "pointer": "/amount", "operator": "lte", "expected": 5},
            {"amount": 4},
            [],
            True,
        ),
        (
            {"kind": "output", "pointer": "/amount", "operator": "lte", "expected": 5},
            {"amount": True},
            [],
            False,
        ),
        (
            {"kind": "output", "pointer": "/missing", "operator": "eq", "expected": None},
            {},
            [],
            False,
        ),
        (
            {"kind": "output", "pointer": "/x", "operator": "in", "expected": [1, "two"]},
            {"x": True},
            [],
            False,
        ),
        (
            {
                "kind": "tool_argument",
                "tool": "refund",
                "pointer": "/amount",
                "operator": "eq",
                "expected": 5,
                "require_any": True,
            },
            {},
            [],
            False,
        ),
        (
            {
                "kind": "tool_argument",
                "tool": "refund",
                "pointer": "/amount",
                "operator": "gte",
                "expected": 5,
                "require_any": True,
            },
            {},
            [("refund", {"amount": 6})],
            True,
        ),
    ],
)
def test_supported_predicates(case_data, rule, output, calls, expected):
    case_data["rules"] = [{"id": "selected", "requirement": "Explicit test requirement", **rule}]
    case = Case.model_validate(case_data)
    observations = [
        Observation(index=i, tool=name, arguments=args) for i, (name, args) in enumerate(calls)
    ]
    assert evaluate(case, observations, output)[0].passed is expected
