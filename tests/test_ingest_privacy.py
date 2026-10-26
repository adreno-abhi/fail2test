from __future__ import annotations

import copy
import json

import pytest

from fail2test import Fail2TestError
from fail2test.ingest import import_case, propose_rules
from fail2test.jsonio import read_json, write_json
from fail2test.privacy import sanitize
from fail2test.workflow import checked_case, load_manifest, review_case


def neutral_trace(case_data):
    events = []
    model = case_data["model_fixtures"][0]
    payloads = [
        (
            "model_request",
            "model0",
            {"slot": model["slot"], "ordinal": 0, "request": model["request"]},
        ),
        ("model_result", "model0", model["response"]),
    ]
    tool = case_data["tool_fixtures"][0]
    for i in range(2):
        payloads.extend(
            [
                (
                    "tool_request",
                    f"tool{i}",
                    {"tool": tool["tool"], "arguments": tool["arguments"]},
                ),
                ("tool_result", f"tool{i}", tool["response"]),
            ]
        )
    for i, (kind, operation, payload) in enumerate(payloads):
        events.append(
            {
                "event_id": f"event{i}",
                "sequence": i,
                "kind": kind,
                "operation_id": operation,
                "payload": payload,
            }
        )
    return {
        "trace_schema_version": "0.1",
        "trace_id": "synthetic-run",
        "input": case_data["input"],
        "completeness": "declared_complete",
        "events": events,
    }


def test_import_neutral_trace_propose_review(tmp_path, case_data):
    source = tmp_path / "source.json"
    write_json(source, neutral_trace(case_data))
    path = import_case(source, tmp_path / "draft")
    assert read_json(path)["rules"] == []
    assert load_manifest(path).review is None
    assert load_manifest(path).source_complete
    proposal = propose_rules(path)
    assert proposal["review_required"]
    review_case(path, reviewer="owner", rules=proposal["rules"])
    case, _ = checked_case(path)
    assert len(case.tool_fixtures) == 1
    assert case.tool_fixtures[0].repeatable


def test_partial_trace_cannot_be_executed(tmp_path, case_data):
    trace = neutral_trace(case_data)
    trace["events"].pop()
    source = tmp_path / "source.json"
    write_json(source, trace)
    path = import_case(source, tmp_path / "draft")
    review_case(path, reviewer="owner", rules=case_data["rules"])
    with pytest.raises(Fail2TestError, match="TRACE_ONLY"):
        checked_case(path)


@pytest.mark.parametrize("mutation", ["order", "duplicate", "version", "parallel", "unmatched"])
def test_invalid_trace_is_not_silently_supported(tmp_path, case_data, mutation):
    trace = neutral_trace(case_data)
    if mutation == "order":
        trace["events"][0]["sequence"] = 1
    elif mutation == "duplicate":
        trace["events"][1]["event_id"] = trace["events"][0]["event_id"]
    elif mutation == "version":
        trace["trace_schema_version"] = "2.0"
    elif mutation == "parallel":
        trace["events"][1] = copy.deepcopy(trace["events"][2])
        trace["events"][1]["sequence"] = 1
    else:
        trace["events"][1]["operation_id"] = "different"
    source = tmp_path / "source.json"
    write_json(source, trace)
    with pytest.raises(Fail2TestError):
        import_case(source, tmp_path / "draft")
    assert not (tmp_path / "draft").exists()


def test_sanitization_preserves_repeated_identity_without_leaking():
    secret = "sk-proj-THIS_IS_A_SYNTHETIC_SECRET_123456"
    result, changes = sanitize(
        {"password": secret, "nested": {"api_key": secret}, "message": f"token={secret}"}
    )
    assert secret not in json.dumps(result)
    assert result["password"] == result["nested"]["api_key"]
    assert len(changes) == 3


def test_import_sanitizes_before_persisting(tmp_path, case_data):
    secret = "sk-proj-THIS_IS_A_SYNTHETIC_SECRET_123456"
    case_data["input"]["api_key"] = secret
    source = tmp_path / "source.json"
    write_json(source, case_data)
    path = import_case(source, tmp_path / "draft")
    for artifact in path.parent.iterdir():
        assert secret not in artifact.read_text()
    assert secret in source.read_text()  # Original is neither rewritten nor deleted.
    assert load_manifest(path).sanitization_changes
