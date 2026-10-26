from __future__ import annotations

import ast
import json
import subprocess
import sys

import pytest

from fail2test import Case, Fail2TestError
from fail2test.ingest import import_case
from fail2test.jsonio import read_json, write_json
from fail2test.reduction import reduce_case
from fail2test.workflow import (
    checked_case,
    export_pytest,
    load_manifest,
    review_case,
    run_reviewed,
    validate_baseline,
)


@pytest.mark.integration
def test_exported_pytest_executes_application_broken_then_fixed(reviewed, app_project):
    path, config = reviewed
    baseline = validate_baseline(path, runner="broken", config=config)
    assert baseline.outcome == "fail"
    assert load_manifest(path).baseline is not None
    exported = export_pytest(path, runner="broken", config=config, out=app_project / "exported")
    command = [sys.executable, "-m", "pytest", "-q", str(exported)]
    broken = subprocess.run(command, cwd=app_project, capture_output=True, text=True, timeout=30)
    assert broken.returncode == 1, broken.stdout + broken.stderr
    assert "one-refund-per-order" in broken.stdout
    # Edit the application's code while retaining the SAME exported test and case.
    module = app_project / "refund_app.py"
    module.write_text(
        module.read_text().replace("deduplicate=False", "deduplicate=True"), encoding="utf-8"
    )
    fixed = subprocess.run(command, cwd=app_project, capture_output=True, text=True, timeout=30)
    assert fixed.returncode == 0, fixed.stdout + fixed.stderr
    assert "1 passed" in fixed.stdout


def test_review_required_and_digest_bound(app_project):
    path = import_case(app_project / "failure.json", app_project / "case")
    with pytest.raises(Fail2TestError, match="REVIEW_REQUIRED"):
        checked_case(path)
    review_case(path, reviewer="owner")
    data = read_json(path)
    data["rules"][0]["max_calls"] = 2
    write_json(path, data, overwrite=True)
    with pytest.raises(Fail2TestError, match="REVIEW_REQUIRED"):
        checked_case(path)


def test_export_requires_reproduced_baseline(reviewed, app_project):
    path, config = reviewed
    with pytest.raises(Fail2TestError, match="VALIDATION_REQUIRED"):
        export_pytest(path, runner="fixed", config=config, out=app_project / "exported")


def test_failed_revalidation_removes_prior_success(reviewed):
    path, config = reviewed
    validate_baseline(path, runner="broken", config=config)
    assert load_manifest(path).baseline is not None
    result = validate_baseline(path, runner="fixed", config=config)
    assert result.outcome == "pass"
    assert load_manifest(path).baseline is None


def test_rereview_invalidates_baseline(reviewed):
    path, config = reviewed
    validate_baseline(path, runner="broken", config=config)
    review_case(path, reviewer="owner-again")
    assert load_manifest(path).baseline is None


def test_loaded_case_public_interface(reviewed):
    path, config = reviewed
    Case.load(path).run(runner="fixed", config=config).assert_passed()


def test_missing_config_is_actionable(reviewed):
    path, config = reviewed
    with pytest.raises(Fail2TestError, match="INVALID_RUNNER_CONFIG"):
        run_reviewed(path, runner="typo", config=config)


def test_supervisor_enforces_timeout_and_suppresses_application_logs(reviewed, app_project):
    path, config = reviewed
    module = app_project / "slow.py"
    module.write_text(
        "import time\ndef run(data, context):\n"
        "    print('PRIVATE-CANARY', flush=True)\n    time.sleep(20)\n",
        encoding="utf-8",
    )
    config.write_text(
        '[runners.slow]\ncallable="slow:run"\ncapabilities=["sync","serial","json","injected_model","injected_tools"]\ntimeout_seconds=0.2\n',
        encoding="utf-8",
    )
    result = run_reviewed(path, runner="slow", config=config)
    assert result.execution_status == "incomplete"
    assert result.tooling_errors == ["RUNNER_TIMEOUT"]
    assert "PRIVATE-CANARY" not in result.model_dump_json()


@pytest.mark.integration
def test_reduction_preserves_failure_and_requires_new_review(reviewed, app_project):
    path, config = reviewed
    validate_baseline(path, runner="broken", config=config)
    output = app_project / "reduced"
    report = reduce_case(path, runner="broken", config=config, out=output, max_runs=8)
    assert report["input_bytes_after"] < report["input_bytes_before"]
    assert "context" not in read_json(output / "case.json")["input"]
    assert report["attempts"] <= 8
    assert load_manifest(output).review is None
    with pytest.raises(Fail2TestError, match="REVIEW_REQUIRED"):
        checked_case(output)
    review_case(output, reviewer="owner")
    assert validate_baseline(output, runner="broken", config=config).outcome == "fail"


def test_exporter_uses_fixed_python_structure(reviewed, app_project):
    path, config = reviewed
    validate_baseline(path, runner="broken", config=config)
    exported = export_pytest(path, runner="fixed", config=config, out=app_project / "exported")
    tree = ast.parse(exported.read_text())
    assert [node.name for node in tree.body if isinstance(node, ast.FunctionDef)] == [
        "test_agent_regression"
    ]
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"exec", "eval", "compile"}
        for node in ast.walk(tree)
    )
    assert json.loads((exported.parent / "case.json").read_text())["rules"]
