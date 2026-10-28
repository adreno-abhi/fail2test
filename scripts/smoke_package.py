"""Verify actual wheel/sdist installs outside the checkout.

Dependency installs use the runtime lock constraints and permit registry downloads,
so a fresh CI cache works. This is an installation check, not an offline-install claim.

Run after `uv build`: `uv run python scripts/smoke_package.py`.
This does not publish or contact a model provider.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

from check_package_contents import check_distributions

ROOT = Path(__file__).resolve().parents[1]


def invoke(args: list[str], cwd: Path, expected: int = 0) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if result.returncode != expected:
        raise RuntimeError(
            f"Unexpected exit {result.returncode} for {args[0:3]}\n"
            + result.stdout[-3000:]
            + result.stderr[-3000:]
        )
    return result.stdout


def main() -> None:
    wheel = next((ROOT / "dist").glob("fail2test-*.whl"))
    sdist = next((ROOT / "dist").glob("fail2test-*.tar.gz"))
    contents = check_distributions(wheel, sdist)
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert "fail2test/py.typed" in names
        assert "fail2test/data/duplicate-refund.case.json" in names
        assert "fail2test/integrations/langchain.py" in names
        assert "fail2test/suggestions.py" in names
        assert "fail2test/ui/static/index.html" in names
        assert "fail2test/ui/static/app.js" in names
        assert "fail2test/ui/static/app.css" in names
        assert any(name.endswith("/licenses/LICENSE") for name in names)
        assert any(name.endswith("/licenses/NOTICE") for name in names)
        assert any(name.endswith("/licenses/THIRD_PARTY_NOTICES.md") for name in names)
    with tarfile.open(sdist) as archive:
        names = archive.getnames()
        assert any(name.endswith("/pyproject.toml") for name in names)
        assert any(name.endswith("/tests/test_workflow.py") for name in names)
        assert any(name.endswith("/scripts/smoke_package.py") for name in names)
        assert any(name.endswith("/docs/site/quickstart.md") for name in names)
        assert any(name.endswith("/examples/langgraph_refunds/failure.json") for name in names)
        for required in (
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md",
            "SUPPORT.md",
            "GOVERNANCE.md",
            "MAINTAINERS.md",
            "NOTICE",
            "THIRD_PARTY_NOTICES.md",
            "DCO",
            "PUBLISHING.md",
            "scripts/check_package_contents.py",
            ".github/ISSUE_TEMPLATE/bug.yml",
            ".github/workflows/ci.yml",
            ".github/dependabot.yml",
            "docs/release/github/SETUP.md",
            "docs/licensing/dependencies.json",
        ):
            assert any(name.endswith("/" + required) for name in names), required
    with tempfile.TemporaryDirectory(prefix="fail2test-wheel-smoke-") as temporary:
        directory = Path(temporary)
        constraints = directory / "runtime-constraints.txt"
        constraints.write_text(
            invoke(
                [
                    "uv",
                    "export",
                    "--locked",
                    "--all-extras",
                    "--no-dev",
                    "--no-emit-project",
                    "--no-hashes",
                ],
                ROOT,
            ),
            encoding="utf-8",
        )
        environment = directory / "isolated environment"
        invoke(["uv", "venv", "--python", sys.executable, str(environment)], directory)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        invoke(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                "--constraint",
                str(constraints),
                f"{wheel}[pytest]",
            ],
            directory,
        )
        command = [str(python), "-m", "fail2test.cli"]
        # The public console script and module entry point must both work.
        executable = environment / ("Scripts/fail2test.exe" if os.name == "nt" else "bin/fail2test")
        invoke([str(executable), "--help"], directory)
        invoke(
            [
                str(python),
                "-c",
                "import importlib.util; assert importlib.util.find_spec('langgraph') is None",
            ],
            directory,
        )
        invoke(command + ["init", "demo"], directory)
        invoke([str(python), str(ROOT / "scripts/smoke_ui.py"), str(directory / "demo")], directory)
        source = directory / "demo/failure.json"
        case = directory / "demo/case"
        config = directory / "demo/fail2test.toml"
        invoke(command + ["import", str(source), "--out", str(case)], directory)
        ai_preview = directory / "demo/ai-preview.json"
        invoke(
            command
            + [
                "ai-preview",
                str(case),
                "--config",
                str(config),
                "--profile",
                "openrouter-free",
                "--requirement",
                "One refund per order.",
                "--out",
                str(ai_preview),
            ],
            directory,
        )
        prepared = json.loads(ai_preview.read_text())
        assert prepared["request"]["provider"]["max_price"] == {"prompt": 0, "completion": 0}
        assert prepared["review_required"] is True
        invoke(command + ["review", str(case), "--reviewer", "smoke-owner"], directory)
        invoke(
            command + ["validate", str(case), "--runner", "broken", "--config", str(config)],
            directory,
        )
        invoke(
            command + ["run", str(case), "--runner", "broken", "--config", str(config)],
            directory,
            1,
        )
        invoke(
            command + ["run", str(case), "--runner", "fixed", "--config", str(config)], directory
        )
        output = directory / "demo/exported"
        invoke(
            command
            + [
                "export",
                str(case),
                "--runner",
                "fixed",
                "--config",
                str(config),
                "--out",
                str(output),
            ],
            directory,
        )
        pytest = invoke(
            [str(python), "-m", "pytest", "-q", str(output / "test_regression.py")], directory
        )
        assert "1 passed" in pytest
        invoke(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                "--constraint",
                str(constraints),
                "--reinstall-package",
                "fail2test",
                str(sdist),
            ],
            directory,
        )
        assert json.loads(invoke(command + ["doctor"], directory))["network_probe"] is False
        invoke(command + ["init", "source-install-demo"], directory)
        invoke(
            [
                str(python),
                str(ROOT / "scripts/smoke_ui.py"),
                str(directory / "source-install-demo"),
            ],
            directory,
        )
        invoke(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python),
                "--constraint",
                str(constraints),
                f"{wheel}[pytest,langgraph]",
            ],
            directory,
        )
        native = directory / "native application"
        shutil.copytree(
            ROOT / "examples/langgraph_refunds",
            native,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        native_case, native_config = native / "case", native / "fail2test.toml"
        invoke(
            command + ["import", str(native / "failure.json"), "--out", str(native_case)], directory
        )
        invoke(command + ["review", str(native_case), "--reviewer", "smoke-owner"], directory)
        invoke(
            command
            + [
                "validate",
                str(native_case),
                "--runner",
                "broken",
                "--config",
                str(native_config),
                "--json",
            ],
            directory,
        )
        invoke(
            command
            + ["run", str(native_case), "--runner", "fixed", "--config", str(native_config)],
            directory,
        )
    report = {
        "wheel": wheel.name,
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "sdist": sdist.name,
        "sdist_sha256": hashlib.sha256(sdist.read_bytes()).hexdigest(),
        "clean_wheel_workflow": "pass",
        "clean_sdist_install": "pass",
        "clean_native_langgraph_workflow": "pass",
        "archive_content_checks": contents,
        "framework_dependency_required": False,
        "provider_calls": False,
    }
    target = ROOT / "local-artifacts/package-smoke.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
