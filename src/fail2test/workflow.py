"""Digest-bound review, baseline reproduction, fresh execution and portable export."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError

from fail2test.config import load_runner_config
from fail2test.errors import Fail2TestError
from fail2test.jsonio import digest, read_json, write_json, write_text
from fail2test.models import Case, RunResult, StrictModel
from fail2test.supervisor import run_supervised


class Review(StrictModel):
    case_digest: str
    reviewer: str = Field(min_length=1, max_length=128)
    selected_rule: str
    reviewed_at: str


class Baseline(StrictModel):
    case_digest: str
    selected_rule: str
    runner_identity: dict[str, str]
    validated_at: str


class Manifest(StrictModel):
    manifest_schema_version: Literal["0.1"] = "0.1"
    source_complete: bool
    sanitization_changes: list[str] = Field(default_factory=list)
    review: Review | None = None
    baseline: Baseline | None = None
    lineage: dict[str, Any] = Field(default_factory=dict)


def case_path(path: Path) -> Path:
    return path / "case.json" if path.is_dir() else path


def load_manifest(path: Path) -> Manifest:
    try:
        return Manifest.model_validate(read_json(case_path(path).with_name("manifest.json")))
    except (ValidationError, Fail2TestError) as exc:
        raise Fail2TestError(
            "INVALID_MANIFEST", "Import the case into a bundle with a valid manifest."
        ) from exc


def save_manifest(path: Path, manifest: Manifest) -> None:
    write_json(
        case_path(path).with_name("manifest.json"), manifest.model_dump(mode="json"), overwrite=True
    )


def create_bundle(data: dict[str, Any], out: Path, manifest: Manifest) -> Path:
    if out.exists():
        raise Fail2TestError("OUTPUT_EXISTS", "Choose a new bundle directory.")
    out.mkdir(parents=True)
    write_json(out / "case.json", data)
    write_json(out / "manifest.json", manifest.model_dump(mode="json"))
    return out / "case.json"


def review_case(
    path: Path, *, reviewer: str, rules: list[Any] | None = None, selected_rule: str | None = None
) -> Case:
    target = case_path(path)
    manifest = load_manifest(target)
    data = read_json(target)
    if rules is not None:
        data["rules"] = rules
    if data.get("provenance", {}).get("sanitization") == "review_required":
        data["provenance"]["sanitization"] = "reviewed"
    try:
        case = Case.model_validate(data)
        selected = selected_rule or case.rules[0].id
        if selected not in {rule.id for rule in case.rules}:
            raise ValueError
        review = Review(
            case_digest=case.case_digest,
            reviewer=reviewer,
            selected_rule=selected,
            reviewed_at=datetime.now(UTC).isoformat(),
        )
    except (ValidationError, ValueError) as exc:
        raise Fail2TestError(
            "INVALID_REVIEW", "Supply valid rules, reviewer label and a selected rule ID."
        ) from exc
    write_json(target, case.model_dump(mode="json"), overwrite=True)
    manifest.review, manifest.baseline = review, None
    save_manifest(target, manifest)
    return case


def checked_case(path: Path) -> tuple[Case, Manifest]:
    case = Case.load(case_path(path))
    manifest = load_manifest(path)
    if manifest.review is None or manifest.review.case_digest != case.case_digest:
        raise Fail2TestError(
            "REVIEW_REQUIRED", "Review the exact current case before execution or export."
        )
    if not manifest.source_complete:
        raise Fail2TestError(
            "TRACE_ONLY",
            "The source is incomplete; provide supported fixtures before regression execution.",
            3,
        )
    return case, manifest


def run_reviewed(
    path: Path, *, runner: str, config: Path, timeout_seconds: float | None = None
) -> RunResult:
    case, _ = checked_case(path)
    return run_supervised(case, runner=runner, config=config, timeout_seconds=timeout_seconds)


def validate_baseline(
    path: Path, *, runner: str, config: Path, timeout_seconds: float | None = None
) -> RunResult:
    case, manifest = checked_case(path)
    assert manifest.review is not None
    result = run_supervised(case, runner=runner, config=config, timeout_seconds=timeout_seconds)
    reproduced = result.execution_status == "complete" and any(
        rule.rule_id == manifest.review.selected_rule and not rule.passed
        for rule in result.rule_results
    )
    if not reproduced:
        # Never retain a success record from an earlier attempt when a new validation fails.
        manifest.baseline = None
        save_manifest(path, manifest)
        return result
    manifest.baseline = Baseline(
        case_digest=case.case_digest,
        selected_rule=manifest.review.selected_rule,
        runner_identity=result.runner_identity,
        validated_at=datetime.now(UTC).isoformat(),
    )
    save_manifest(path, manifest)
    return result


def preview_pytest(path: Path, *, runner: str, config: Path, out: Path) -> dict[str, str]:
    """Prepare the exact export without writing files or importing application code."""
    case, manifest = checked_case(path)
    if manifest.baseline is None or manifest.baseline.case_digest != case.case_digest:
        raise Fail2TestError(
            "VALIDATION_REQUIRED",
            "Reproduce the reviewed failure before exporting its regression test.",
        )
    load_runner_config(config, runner)  # Validate configuration without importing application code.
    if out.exists():
        raise Fail2TestError("OUTPUT_EXISTS", "Choose a new export directory.")
    try:
        relative_config = Path(os.path.relpath(config.resolve(), out.resolve())).as_posix()
    except ValueError as exc:
        raise Fail2TestError(
            "CONFIG_PATH_UNPORTABLE", "Export on the same drive as the local runner configuration."
        ) from exc
    source = (
        '"""Generated regression. Keep this file and its reviewed JSON bundle together."""\n'
        "from pathlib import Path\n\n"
        "from fail2test import Case\n\n\n"
        "def test_agent_regression():\n"
        "    directory = Path(__file__).resolve().parent\n"
        "    case = Case.load(directory / 'case.json')\n"
        f"    result = case.run(runner={runner!r}, config=directory / {relative_config!r})\n"
        "    result.assert_passed()\n"
    )
    return {
        "case.json": json.dumps(case.model_dump(mode="json"), indent=2) + "\n",
        "manifest.json": json.dumps(manifest.model_dump(mode="json"), indent=2) + "\n",
        "test_regression.py": source,
        "README.md": (
            "# Exported regression\n\n"
            "Run `python -m pytest test_regression.py`. "
            "Install Fail2Test and your application dependencies. "
            "The reviewed case and manifest must stay together. "
            "Runner configuration remains in your application repository. "
            "Fixture mode tests application handling of recorded responses; "
            "it does not evaluate a changed prompt against a live model.\n"
        ),
    }


def export_pytest(path: Path, *, runner: str, config: Path, out: Path) -> Path:
    prepared = preview_pytest(path, runner=runner, config=config, out=out)
    out.mkdir(parents=True)
    for name, content in prepared.items():
        write_text(out / name, content)
    return out / "test_regression.py"


def artifact_identity(path: Path) -> str:
    return digest(read_json(case_path(path)))
