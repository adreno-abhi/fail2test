from __future__ import annotations

import copy
import json

import pytest
from hypothesis import given
from hypothesis import strategies as st
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from fail2test.errors import Fail2TestError
from fail2test.jsonio import canonical, read_json, write_json
from fail2test.models import Case, RunResult, case_schema


def test_generated_schema_matches_reference_case(case_data):
    schema = case_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(case_data)


@pytest.mark.parametrize(
    "field,value",
    [("schema_version", "9.9"), ("mode", "live_model"), ("executable", "print('unsafe')")],
)
def test_unsupported_fields_rejected(case_data, field, value):
    case_data[field] = value
    with pytest.raises(ValidationError):
        Case.model_validate(case_data)


@pytest.mark.parametrize(
    "mutation",
    ["duplicate_rule", "duplicate_model", "ambiguous_tool", "bounds", "pointer", "bool_bound"],
)
def test_domain_invariants(case_data, mutation):
    if mutation == "duplicate_rule":
        case_data["rules"].append(copy.deepcopy(case_data["rules"][0]))
    elif mutation == "duplicate_model":
        case_data["model_fixtures"].append(copy.deepcopy(case_data["model_fixtures"][0]))
    elif mutation == "ambiguous_tool":
        duplicate = copy.deepcopy(case_data["tool_fixtures"][0])
        duplicate["id"] = "different-id"
        case_data["tool_fixtures"].append(duplicate)
    elif mutation == "bounds":
        case_data["rules"][0]["min_calls"] = 2
    elif mutation == "pointer":
        case_data["rules"][0]["group_by"] = ["/invalid~escape"]
    else:
        case_data["rules"][0]["max_calls"] = True
    with pytest.raises(ValidationError):
        Case.model_validate(case_data)


def test_nonfinite_and_duplicate_json_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"x":1,"x":2}')
    with pytest.raises(Fail2TestError, match="DUPLICATE_JSON_KEY"):
        read_json(path)
    path.write_text('{"x":NaN}')
    with pytest.raises(Fail2TestError, match="INVALID_JSON_NUMBER"):
        read_json(path)


def test_json_size_and_depth_limits(tmp_path):
    path = tmp_path / "large.json"
    path.write_bytes(b" " * (10 * 1024 * 1024 + 1))
    with pytest.raises(Fail2TestError, match="INPUT_TOO_LARGE"):
        read_json(path)
    path.write_text("[" * 70 + "0" + "]" * 70)
    with pytest.raises(Fail2TestError, match="JSON_TOO_DEEP"):
        read_json(path)


def test_atomic_writer_refuses_existing_output(tmp_path):
    path = tmp_path / "case.json"
    write_json(path, {"original": True})
    with pytest.raises(Fail2TestError, match="OUTPUT_EXISTS"):
        write_json(path, {"replacement": True})
    assert json.loads(path.read_text()) == {"original": True}


@given(
    st.dictionaries(
        st.text(alphabet="abcxyz", min_size=1, max_size=6), st.integers(-10000, 10000), max_size=10
    )
)
def test_jcs_identity_independent_of_key_order(value):
    assert canonical(value) == canonical(dict(reversed(list(value.items()))))


def test_json_types_are_distinct():
    assert canonical(True) != canonical(1)
    assert canonical("1") != canonical(1)
    assert canonical(1.0) == canonical(1)


def test_result_cannot_claim_pass_without_rules():
    with pytest.raises(ValidationError):
        RunResult(case_id="test", case_digest="digest", execution_status="complete", outcome="pass")
