from __future__ import annotations

import json

from typer.testing import CliRunner

from fail2test.cli import app

cli = CliRunner()


def test_cli_full_workflow(tmp_path):
    directory = tmp_path / "demo"
    result = cli.invoke(app, ["init", str(directory)])
    assert result.exit_code == 0, result.output
    bundle = directory / "case"
    config = directory / "fail2test.toml"
    result = cli.invoke(app, ["import", str(directory / "failure.json"), "--out", str(bundle)])
    assert result.exit_code == 0, result.output
    assert (
        cli.invoke(
            app, ["run", str(bundle), "--runner", "fixed", "--config", str(config)]
        ).exit_code
        == 2
    )
    result = cli.invoke(app, ["review", str(bundle), "--reviewer", "local-owner"])
    assert result.exit_code == 0, result.output
    result = cli.invoke(
        app, ["validate", str(bundle), "--runner", "broken", "--config", str(config), "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["baseline_reproduced"] is True
    result = cli.invoke(
        app, ["run", str(bundle), "--runner", "broken", "--config", str(config), "--json"]
    )
    assert result.exit_code == 1, result.output
    assert json.loads(result.output)["outcome"] == "fail"
    result = cli.invoke(
        app, ["run", str(bundle), "--runner", "fixed", "--config", str(config), "--json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["outcome"] == "pass"
    result = cli.invoke(
        app,
        [
            "export",
            str(bundle),
            "--runner",
            "fixed",
            "--config",
            str(config),
            "--out",
            str(directory / "tests"),
        ],
    )
    assert result.exit_code == 0, result.output


def test_inspect_does_not_import_application(reviewed, app_project):
    path, config = reviewed
    marker = app_project / "should-not-exist"
    (app_project / "refund_app.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('imported')\n"
        "raise Exception('private')\n",
        encoding="utf-8",
    )
    result = cli.invoke(app, ["inspect", str(path), "--json"])
    assert result.exit_code == 0, result.output
    assert not marker.exists()


def test_cli_help_doctor_schema_and_refused_overwrite(tmp_path):
    assert cli.invoke(app, ["--help"]).exit_code == 0
    assert json.loads(cli.invoke(app, ["doctor"]).output)["network_probe"] is False
    schema = json.loads(cli.invoke(app, ["schema"]).output)
    assert schema["title"] == "Case"
    assert cli.invoke(app, ["init", str(tmp_path)]).exit_code == 2


def test_machine_readable_configuration_error(reviewed):
    path, config = reviewed
    result = cli.invoke(
        app, ["run", str(path), "--runner", "missing", "--config", str(config), "--json"]
    )
    assert result.exit_code == 2, result.output
    assert json.loads(result.output)["error"]["code"] == "INVALID_RUNNER_CONFIG"
