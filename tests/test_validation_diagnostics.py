"""Authoring diagnostics identify schema fields without echoing evidence or unknown keys."""

from __future__ import annotations

import json
import traceback

import pytest
from pydantic import ValidationError, field_validator
from test_ingest_privacy import neutral_trace
from test_ui_server import imported, payload, request, reviewed_item, ui_server  # noqa: F401
from typer.testing import CliRunner

from fail2test.cli import app
from fail2test.errors import Fail2TestError, validation_message
from fail2test.ingest import import_case, import_data
from fail2test.models import Case
from fail2test.suggestions import preview
from fail2test.ui.server import safe_error

cli = CliRunner()


def test_import_identifies_missing_rule_field_without_input_values(tmp_path, case_data):
    case_data["rules"] = [{"id": "read-only", "kind": "forbidden_tool", "tool": "delete"}]
    case_data["input"] = {"private-customer-key": "DO_NOT_ECHO_CUSTOMER_VALUE"}
    source = tmp_path / "evidence.json"
    source.write_text(json.dumps(case_data), encoding="utf-8")
    result = cli.invoke(app, ["import", str(source), "--out", str(tmp_path / "case")])
    assert result.exit_code == 2
    assert "INVALID_CASE" in result.output
    assert "case.rules[0].requirement" in result.output
    assert "Required field is missing" in result.output
    assert "private-customer-key" not in result.output
    assert "DO_NOT_ECHO_CUSTOMER_VALUE" not in result.output
    assert not (tmp_path / "case").exists()


@pytest.mark.parametrize(
    ("rules", "location", "explanation"),
    [
        ([{"kind": "PRIVATE_UNKNOWN_TAG"}], "case.rules[0]", "supported rule kind"),
        (
            [{"kind": "max_tool_calls", "id": "limit", "requirement": "limit", "max_calls": -1}],
            "case.rules[0].max_calls",
            "numeric bounds",
        ),
    ],
)
def test_case_load_has_safe_actionable_diagnostics(
    tmp_path, case_data, rules, location, explanation
):
    case_data["rules"] = rules
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case_data), encoding="utf-8")
    with pytest.raises(Fail2TestError) as error:
        Case.load(path)
    assert error.value.code == "INVALID_CASE"
    assert location in error.value.message
    assert explanation in error.value.message
    assert "PRIVATE_UNKNOWN_TAG" not in error.value.message


def test_rule_review_reports_field_and_preserves_saved_case(app_project):
    bundle = app_project / "case"
    assert (
        cli.invoke(
            app, ["import", str(app_project / "failure.json"), "--out", str(bundle)]
        ).exit_code
        == 0
    )
    original = (bundle / "case.json").read_bytes()
    rules = app_project / "rules.json"
    rules.write_text(json.dumps([{"kind": "forbidden_tool", "id": "rule", "tool": "delete"}]))
    result = cli.invoke(app, ["review", str(bundle), "--rules", str(rules), "--reviewer", "owner"])
    assert result.exit_code == 2
    assert "INVALID_REVIEW" in result.output
    assert "case.rules[0].requirement" in result.output
    assert (bundle / "case.json").read_bytes() == original


def test_ui_edit_hides_unknown_keys_and_preserves_authorization(ui_server):  # noqa: F811
    item = reviewed_item(ui_server)
    path = ui_server.workspace.root / item["path"]
    original = {name: (path / name).read_bytes() for name in ("case.json", "manifest.json")}
    item["case"]["model_fixtures"][0]["private-customer-name"] = "DO_NOT_ECHO_CUSTOMER_VALUE"
    status, body = request(
        ui_server, "/api/edit", payload(item, case_text=json.dumps(item["case"]))
    )
    assert status == 400
    assert body["error"]["code"] == "INVALID_DATA"
    assert "case.model_fixtures[0]" in body["error"]["message"]
    assert "private-customer-name" not in json.dumps(body)
    assert "DO_NOT_ECHO_CUSTOMER_VALUE" not in json.dumps(body)
    assert {name: (path / name).read_bytes() for name in original} == original


def test_many_invalid_rules_have_bounded_diagnostics(tmp_path, case_data):
    case_data["rules"] = [{} for _ in range(50)]
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case_data), encoding="utf-8")
    with pytest.raises(Fail2TestError) as error:
        Case.load(path)
    assert "case.rules[0]" in error.value.message
    assert "Additional errors omitted" in error.value.message
    assert len(error.value.message) < 1500


def test_dictionary_keys_are_not_mistaken_for_schema_fields(case_data):
    # Even keys named like legitimate Case fields are private inside arbitrary JSON data.
    case_data["input"] = {"model_fixtures": {"PRIVATE_DICTIONARY_KEY": object()}}
    with pytest.raises(ValidationError) as error:
        Case.model_validate(case_data)
    message = validation_message(error.value, Case)
    assert "case.input:" in message
    assert "case.input.model_fixtures" not in message
    assert "PRIVATE_DICTIONARY_KEY" not in message
    assert "object at" not in message
    assert "PRIVATE_DICTIONARY_KEY" not in json.dumps(safe_error(error.value))


def test_validator_messages_and_exception_chains_do_not_echo_values(tmp_path, case_data):
    class MessageCase(Case):
        @field_validator("title")
        @classmethod
        def rejected_title(cls, value):
            raise ValueError("PRIVATE_VALIDATOR_MESSAGE " + value)

    case_data["title"] = "PRIVATE_TITLE_VALUE"
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case_data), encoding="utf-8")
    with pytest.raises(Fail2TestError) as error:
        MessageCase.load(path)
    message = "".join(traceback.format_exception(error.value))
    assert "case.title" in message
    assert "PRIVATE_TITLE_VALUE" not in message
    assert "PRIVATE_VALIDATOR_MESSAGE" not in message


def test_json_run_diagnostics_preserve_code_and_exit(tmp_path, case_data):
    case_data["model_fixtures"][0]["slot"] = 123
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case_data), encoding="utf-8")
    result = cli.invoke(app, ["run", str(path), "--runner", "unused", "--json"])
    assert result.exit_code == 2
    error = json.loads(result.output)["error"]
    assert error["code"] == "INVALID_CASE"
    assert "case.model_fixtures[0].slot" in error["message"]
    assert "123" not in error["message"]


def test_normalized_trace_diagnostics_identify_fixture_field(tmp_path, case_data):
    trace = neutral_trace(case_data)
    trace["events"][0]["payload"]["ordinal"] = "PRIVATE_BAD_ORDINAL"
    with pytest.raises(Fail2TestError) as error:
        import_data(trace, tmp_path / "case")
    assert error.value.code == "INVALID_TRACE_PAYLOAD"
    assert "case.model_fixtures[0].ordinal" in error.value.message
    assert "PRIVATE_BAD_ORDINAL" not in error.value.message
    assert not (tmp_path / "case").exists()


def test_ai_preview_uses_same_case_diagnostics_without_credentials(app_project):
    path = import_case(app_project / "failure.json", app_project / "case")
    raw = json.loads(path.read_text())
    raw["model_fixtures"][0]["slot"] = 123
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(Fail2TestError) as error:
        preview(
            path,
            config=app_project / "fail2test.toml",
            profile="openrouter-free",
            requirement="Once",
        )
    assert error.value.code == "INVALID_CASE"
    assert "case.model_fixtures[0].slot" in error.value.message


@pytest.mark.parametrize("invalid_root", [False, True])
def test_review_of_externally_malformed_case_has_safe_diagnostics(app_project, invalid_root):
    path = import_case(app_project / "failure.json", app_project / "case")
    raw = json.loads(path.read_text())
    raw["provenance"] = "PRIVATE_PROVENANCE_VALUE"
    path.write_text(json.dumps([] if invalid_root else raw), encoding="utf-8")
    before = {p.name: p.read_bytes() for p in path.parent.iterdir() if p.is_file()}
    result = cli.invoke(app, ["review", str(path), "--reviewer", "owner"])
    assert result.exit_code == 2
    assert "INVALID_REVIEW" in result.output
    assert ("case:" if invalid_root else "case.provenance:") in result.output
    assert "PRIVATE_PROVENANCE_VALUE" not in result.output
    assert {p.name: p.read_bytes() for p in path.parent.iterdir() if p.is_file()} == before
