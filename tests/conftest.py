from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

import pytest

from fail2test.ingest import import_case
from fail2test.models import Case
from fail2test.workflow import review_case


@pytest.fixture
def case_data():
    return json.loads(files("fail2test").joinpath("data/duplicate-refund.case.json").read_text())


@pytest.fixture
def case(case_data):
    return Case.model_validate(case_data)


@pytest.fixture
def app_project(tmp_path: Path):
    directory = tmp_path / "application with spaces"
    directory.mkdir()
    data = files("fail2test").joinpath("data")
    for source, destination in [
        ("refund_app.py.txt", "refund_app.py"),
        ("fail2test.toml.txt", "fail2test.toml"),
        ("duplicate-refund.case.json", "failure.json"),
    ]:
        (directory / destination).write_text(data.joinpath(source).read_text(), encoding="utf-8")
    return directory


@pytest.fixture
def reviewed(app_project: Path):
    path = import_case(app_project / "failure.json", app_project / "case")
    review_case(path, reviewer="test-owner")
    return path, app_project / "fail2test.toml"
