"""Bounded structural reduction, accepting only newly reproduced selected failures."""

from __future__ import annotations

import copy
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from fail2test.errors import Fail2TestError
from fail2test.jsonio import canonical, write_json
from fail2test.models import Case, RunResult
from fail2test.supervisor import run_supervised
from fail2test.workflow import Manifest, checked_case, create_bundle


def _deletions(value: Any) -> Iterator[Any]:
    if isinstance(value, dict):
        for key in list(value):
            candidate = copy.deepcopy(value)
            del candidate[key]
            yield candidate
            for reduced in _deletions(value[key]):
                candidate = copy.deepcopy(value)
                candidate[key] = reduced
                yield candidate
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield copy.deepcopy(value[:index] + value[index + 1 :])
            for reduced in _deletions(item):
                list_candidate = copy.deepcopy(value)
                list_candidate[index] = reduced
                yield list_candidate


def _reproduced(result: RunResult, rule_id: str) -> bool:
    return result.execution_status == "complete" and any(
        rule.rule_id == rule_id and not rule.passed for rule in result.rule_results
    )


def reduce_case(
    path: Path,
    *,
    runner: str,
    config: Path,
    out: Path,
    max_runs: int = 50,
    timeout_seconds: float = 120,
) -> dict[str, Any]:
    if max_runs < 1 or max_runs > 1000 or timeout_seconds <= 0:
        raise Fail2TestError("INVALID_BUDGET", "Choose 1–1000 attempts and a positive time budget.")
    case, manifest = checked_case(path)
    if manifest.baseline is None or manifest.baseline.case_digest != case.case_digest:
        raise Fail2TestError(
            "VALIDATION_REQUIRED", "Validate the selected failure before reducing it."
        )
    assert manifest.review is not None
    selected = manifest.review.selected_rule
    started = time.monotonic()
    if not _reproduced(
        run_supervised(case, runner=runner, config=config, timeout_seconds=timeout_seconds),
        selected,
    ):
        raise Fail2TestError(
            "BASELINE_NOT_REPRODUCED",
            "Current runner no longer reproduces the selected failure.",
            1,
        )
    original_size = len(canonical(case.input))
    attempts = 1  # The baseline recheck consumes the same execution/time budget.
    best = case
    exhausted = False
    while attempts < max_runs and time.monotonic() - started < timeout_seconds:
        changed = False
        for input_candidate in _deletions(best.input):
            if attempts >= max_runs or time.monotonic() - started >= timeout_seconds:
                exhausted = True
                break
            data = best.model_dump(mode="json")
            data["input"] = input_candidate
            candidate = Case.model_validate(data)
            attempts += 1
            remaining = timeout_seconds - (time.monotonic() - started)
            if _reproduced(
                run_supervised(candidate, runner=runner, config=config, timeout_seconds=remaining),
                selected,
            ):
                best, changed = candidate, True
                break
        if not changed:
            break
    if attempts >= max_runs or time.monotonic() - started >= timeout_seconds:
        exhausted = True
    report = {
        "source_digest": case.case_digest,
        "candidate_digest": best.case_digest,
        "attempts": attempts,
        "input_bytes_before": original_size,
        "input_bytes_after": len(canonical(best.input)),
        "stop_reason": "budget" if exhausted else "no_further_input_deletion",
        "review_required": True,
        "scope": "input deletion only; no claim of global minimality",
    }
    create_bundle(
        best.model_dump(mode="json"),
        out,
        Manifest(
            source_complete=manifest.source_complete,
            sanitization_changes=manifest.sanitization_changes,
            lineage=report,
        ),
    )
    write_json(out / "reduction-report.json", report)
    return report
