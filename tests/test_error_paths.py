from __future__ import annotations

import json

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fail2test import Case, Fail2TestError
from fail2test.cli import app
from fail2test.config import load_runner_config
from fail2test.ingest import import_case, propose_rules
from fail2test.jsonio import read_json, write_json
from fail2test.reduction import reduce_case
from fail2test.workflow import load_manifest, review_case, run_reviewed, validate_baseline


@pytest.mark.parametrize(
    "data", [[], {}, {"schema_version": "wrong"}, {"trace_schema_version": "0.1"}]
)
def test_malformed_imports_do_not_create_bundle(tmp_path, data):
    source = tmp_path / "source.json"
    write_json(source, data)
    with pytest.raises(Fail2TestError):
        import_case(source, tmp_path / "bundle")
    assert not (tmp_path / "bundle").exists()


def test_invalid_rule_operands_are_rejected(case_data):
    for operator, expected in [("in", 3), ("gte", True)]:
        case_data["rules"] = [
            {
                "id": "rule",
                "kind": "output",
                "pointer": "/x",
                "operator": operator,
                "expected": expected,
                "requirement": "Explicit rule",
            }
        ]
        with pytest.raises(ValidationError):
            Case.model_validate(case_data)


@pytest.mark.parametrize(
    "capabilities,entry",
    [([], "app:run"), (["sync", "serial", "json", "injected_model", "injected_tools"], "invalid")],
)
def test_invalid_runner_capabilities_and_entrypoint(tmp_path, capabilities, entry):
    config = tmp_path / "config.toml"
    config.write_text(
        f"[runners.app]\ncallable={json.dumps(entry)}\ncapabilities={json.dumps(capabilities)}\n",
        encoding="utf-8",
    )
    with pytest.raises(Fail2TestError):
        load_runner_config(config, "app")


def test_runner_import_failure_is_reported_without_private_exception(reviewed, app_project):
    path, config = reviewed
    (app_project / "refund_app.py").write_text(
        "raise RuntimeError('PRIVATE-IMPORT-CANARY')", encoding="utf-8"
    )
    result = run_reviewed(path, runner="fixed", config=config)
    assert result.execution_status == "incomplete"
    assert result.tooling_errors == ["RUNNER_IMPORT_FAILED"]
    assert "PRIVATE-IMPORT-CANARY" not in result.model_dump_json()


def test_review_rejects_unknown_rule_and_missing_reviewer(reviewed):
    path, _ = reviewed
    with pytest.raises(Fail2TestError, match="INVALID_REVIEW"):
        review_case(path, reviewer="owner", selected_rule="unknown")
    with pytest.raises(Fail2TestError, match="INVALID_REVIEW"):
        review_case(path, reviewer="")


def test_unknown_manifest_version_is_rejected(reviewed):
    path, _ = reviewed
    manifest = path.with_name("manifest.json")
    data = read_json(manifest)
    data["manifest_schema_version"] = "9.0"
    write_json(manifest, data, overwrite=True)
    with pytest.raises(Fail2TestError, match="INVALID_MANIFEST"):
        load_manifest(path)


def test_reduction_counts_baseline_in_budget(reviewed, app_project):
    path, config = reviewed
    validate_baseline(path, runner="broken", config=config)
    result = reduce_case(
        path, runner="broken", config=config, out=app_project / "reduced", max_runs=1
    )
    assert result["attempts"] == 1
    assert result["input_bytes_before"] == result["input_bytes_after"]
    assert result["stop_reason"] == "budget"


@pytest.mark.parametrize("max_runs", [0, 1001])
def test_invalid_reduction_budget_is_rejected(reviewed, app_project, max_runs):
    path, config = reviewed
    with pytest.raises(Fail2TestError, match="INVALID_BUDGET"):
        reduce_case(
            path, runner="broken", config=config, out=app_project / "reduced", max_runs=max_runs
        )


def test_proposals_without_tools_need_review(reviewed):
    path, _ = reviewed
    data = read_json(path)
    data["tool_fixtures"] = []
    write_json(path, data, overwrite=True)
    proposal = propose_rules(path)
    assert proposal["review_required"] is True
    assert proposal["rules"][0]["kind"] == "max_tool_calls"


def test_cli_proposal_schema_and_unsupported_format(reviewed, app_project):
    path, _ = reviewed
    cli = CliRunner()
    assert (
        cli.invoke(
            app, ["propose", str(path), "--out", str(app_project / "proposal.json")]
        ).exit_code
        == 0
    )
    assert cli.invoke(app, ["schema", "--out", str(app_project / "schema.json")]).exit_code == 0
    result = cli.invoke(
        app, ["import", str(path), "--out", str(app_project / "other"), "--format", "pickle"]
    )
    assert result.exit_code == 2
    assert not (app_project / "other").exists()


def test_case_without_saved_reviewed_file_cannot_use_convenience_run(case_data):
    with pytest.raises(Fail2TestError, match="UNSAVED_CASE"):
        Case.model_validate(case_data).run(runner="app")
