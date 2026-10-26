"""Private subprocess entry point; stdout/stderr are not surfaced as evidence."""

from __future__ import annotations

import sys
from pathlib import Path

from fail2test.config import import_runner, load_runner_config
from fail2test.errors import Fail2TestError
from fail2test.execution import execute_case
from fail2test.jsonio import read_json, write_json
from fail2test.models import Case, RunResult
from fail2test.privacy import sanitize


def main() -> None:
    request_path, result_path = map(Path, sys.argv[1:3])
    request = read_json(request_path)
    case = Case.model_validate(request["case"])
    try:
        config_path = Path(request["config"])
        config = load_runner_config(config_path, request["runner"])
        runner, identity = import_runner(config_path, config)
        result = execute_case(case, runner)
        result.runner_identity = identity
    except Fail2TestError as exc:
        result = RunResult(
            case_id=case.case_id,
            case_digest=case.case_digest,
            execution_status="incomplete",
            outcome="not_evaluated",
            tooling_errors=[exc.code],
        )
    sanitized, _ = sanitize(result.model_dump(mode="json"))
    write_json(result_path, sanitized)


if __name__ == "__main__":
    main()
