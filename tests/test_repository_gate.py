"""The publication checklist must not pass because a field was omitted or truthy text."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "repository_checks", ROOT / "scripts/check_repository.py"
)
assert spec is not None and spec.loader is not None
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def test_missing_publication_facts_fail_closed():
    errors = checks.publication_errors({})
    assert any("github_owner" in item for item in errors)
    assert any("owner_acceptance" in item for item in errors)


@pytest.mark.parametrize("unverified", ["true", "false", 1, [], None])
def test_truthy_or_non_boolean_verification_is_not_acceptance(unverified):
    # These are test-only facts, not project identities or evidence of live verification.
    facts = dict.fromkeys(checks.IDENTITIES, "synthetic-test-value")
    facts.update(dict.fromkeys(checks.VERIFIED, True))
    facts["owner_acceptance"] = unverified
    assert checks.publication_errors(facts) == ["Publication fact still pending: owner_acceptance"]
