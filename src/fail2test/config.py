"""Trusted local runner configuration; case files cannot specify code to import."""

from __future__ import annotations

import hashlib
import importlib
import inspect
import sys
import tomllib
from pathlib import Path
from typing import cast

from pydantic import Field, ValidationError

from fail2test.errors import Fail2TestError
from fail2test.execution import Runner
from fail2test.models import StrictModel

REQUIRED_CAPABILITIES = {"sync", "serial", "json", "injected_model", "injected_tools"}


class RunnerConfig(StrictModel):
    callable: str
    capabilities: list[str]
    timeout_seconds: float = Field(default=10.0, gt=0, le=3600)


def load_runner_config(path: Path, name: str) -> RunnerConfig:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
        data = raw["runners"][name]
        config = RunnerConfig.model_validate(data)
    except (OSError, ValueError, KeyError, TypeError, ValidationError) as exc:
        raise Fail2TestError(
            "INVALID_RUNNER_CONFIG", "Check runner name, callable and local TOML configuration."
        ) from exc
    if not REQUIRED_CAPABILITIES.issubset(config.capabilities):
        raise Fail2TestError(
            "UNSUPPORTED_RUNNER",
            "The runner must declare synchronous, serial, JSON and injected dependencies.",
            3,
        )
    if ":" not in config.callable:
        raise Fail2TestError(
            "INVALID_RUNNER_CONFIG", "Use a trusted local module:function entry point."
        )
    return config


def import_runner(path: Path, config: RunnerConfig) -> tuple[Runner, dict[str, str]]:
    module_name, function_name = config.callable.split(":", 1)
    if (
        not all(part.isidentifier() for part in module_name.split("."))
        or not function_name.isidentifier()
    ):
        raise Fail2TestError("INVALID_RUNNER_CONFIG", "Use a valid module:function entry point.")
    # Only execution commands reach here; project imports are intentionally executable.
    sys.path.insert(0, str(path.resolve().parent))
    try:
        module = importlib.import_module(module_name)
        target = getattr(module, function_name)
        if not callable(target):
            raise TypeError
        source = inspect.getsourcefile(module)
        source_digest = (
            hashlib.sha256(Path(source).read_bytes()).hexdigest() if source else "unavailable"
        )
    except Exception as exc:
        raise Fail2TestError(
            "RUNNER_IMPORT_FAILED", "Cannot import the configured local runner.", 3
        ) from exc
    return cast(Runner, target), {
        "entry_point": config.callable,
        "source_digest": source_digest,
        "source_digest_scope": "configured_module_only",
    }
