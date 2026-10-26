from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("langgraph")
from fail2test.ingest import import_case  # noqa: E402
from fail2test.workflow import export_pytest, review_case, run_reviewed, validate_baseline  # noqa: E402


@pytest.mark.integration
def test_existing_style_graph_native_toolnode_and_export(tmp_path):
    source = Path(__file__).resolve().parents[1] / "examples/langgraph_refunds"
    project = tmp_path / "native app with spaces"
    shutil.copytree(source, project, ignore=shutil.ignore_patterns("__pycache__"))
    case = import_case(project / "failure.json", project / "case")
    config = project / "fail2test.toml"
    review_case(case, reviewer="example-owner")
    broken = validate_baseline(case, runner="broken", config=config)
    assert broken.execution_status == "complete", broken.model_dump()
    assert broken.outcome == "fail"
    assert len(broken.observed_calls) == 2
    fixed = run_reviewed(case, runner="fixed", config=config)
    assert fixed.outcome == "pass", fixed.model_dump()
    assert len(fixed.observed_calls) == 1
    assert fixed.output["messages"][2]["role"] == "tool"
    exported = export_pytest(case, runner="fixed", config=config, out=project / "exported")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(exported)],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
