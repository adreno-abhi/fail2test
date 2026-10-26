"""Process lifetime control, not a sandbox for malicious Python code."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
from contextlib import suppress
from pathlib import Path

from pydantic import ValidationError

from fail2test.config import load_runner_config
from fail2test.errors import Fail2TestError
from fail2test.jsonio import read_json, write_json
from fail2test.models import Case, RunResult


def _stop(process: subprocess.Popen[bytes]) -> None:
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
    else:
        with suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGKILL)
    if process.poll() is None:
        process.kill()
    process.wait(timeout=10)


def run_supervised(
    case: Case, *, runner: str, config: Path, timeout_seconds: float | None = None
) -> RunResult:
    config = config.resolve()
    settings = load_runner_config(config, runner)
    with tempfile.TemporaryDirectory(prefix="fail2test-run-") as directory:
        request, output = Path(directory) / "request.json", Path(directory) / "result.json"
        write_json(
            request, {"case": case.model_dump(mode="json"), "runner": runner, "config": str(config)}
        )
        process = subprocess.Popen(
            [sys.executable, "-m", "fail2test.worker", str(request), str(output)],
            cwd=config.parent,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=os.name != "nt",
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        error_code = None
        try:
            limit = settings.timeout_seconds
            if timeout_seconds is not None:
                limit = min(limit, timeout_seconds)
            process.wait(timeout=limit)
        except subprocess.TimeoutExpired:
            _stop(process)
            error_code = "RUNNER_TIMEOUT"
        except BaseException:
            _stop(process)
            raise
        if error_code is None:
            try:
                result = RunResult.model_validate(read_json(output))
                if result.case_digest == case.case_digest and result.case_id == case.case_id:
                    return result
            except (Fail2TestError, OSError, ValueError, ValidationError):
                pass
            error_code = "WORKER_FAILED"
        return RunResult(
            case_id=case.case_id,
            case_digest=case.case_digest,
            execution_status="incomplete",
            outcome="not_evaluated",
            tooling_errors=[error_code],
        )
