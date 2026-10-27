"""Timed installed-wheel acceptance; automated timings are not human usability measurements."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Trial:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.events: list[dict] = []
        self.env = os.environ.copy()
        self.env["PYTHONIOENCODING"] = "utf-8"
        for key in (
            "OPENAI_API_KEY",
            "OPENROUTER_API_KEY",
            "OLLAMA_API_KEY",
            "PYTHONPATH",
            "UV_PROJECT_ENVIRONMENT",
            "COVERAGE_PROCESS_START",
        ):
            self.env.pop(key, None)

    def run(self, label: str, command: list[str], expected: int = 0) -> str:
        started = time.perf_counter()
        result = subprocess.run(
            command,
            cwd=self.directory,
            env=self.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=180,
        )
        self.events.append(
            {
                "action": label,
                "seconds": round(time.perf_counter() - started, 3),
                "exit_code": result.returncode,
                "expected_exit": expected,
            }
        )
        if result.returncode != expected:
            raise RuntimeError(
                f"Acceptance failed at {label}: exit {result.returncode}\n"
                + result.stdout[-2000:]
                + result.stderr[-2000:]
            )
        return result.stdout


def browser_trial(trial: Trial, command: list[str]) -> float:
    from playwright.sync_api import expect, sync_playwright

    trial.run("ui_init", command + ["init", "ui-demo"])
    started = time.perf_counter()
    process = subprocess.Popen(
        command + ["ui", "--workspace", "ui-demo", "--port", "0", "--no-open"],
        cwd=trial.directory,
        env=trial.env,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
    )
    launched: queue.Queue[str] = queue.Queue()

    def read_launch() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            if line.startswith("http://127.0.0.1:") and "#session=" in line:
                launched.put(line.strip())
                break

    threading.Thread(target=read_launch, daemon=True).start()
    try:
        url = launched.get(timeout=20)  # Keep the session token in memory only.
        origin = url.split("/#", 1)[0]
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            unexpected = []
            page.on(
                "request",
                lambda request: (
                    unexpected.append(request.url)
                    if not request.url.startswith(origin + "/")
                    else None
                ),
            )
            page.goto(url)
            page.get_by_role("button", name="Import failure.json", exact=True).click()
            page.get_by_role("tab", name="02 Review").click()
            page.get_by_label("Reviewer label").fill("synthetic-acceptance")
            page.get_by_label("I reviewed the recorded evidence", exact=False).check()
            page.get_by_role("button", name="Approve exact case").click()
            page.get_by_role("button", name="Validate failing baseline").click()
            expect(
                page.get_by_role("heading", name="Baseline reproduced", exact=False)
            ).to_be_visible(timeout=30000)
            page.get_by_label("Configured runner").select_option("fixed")
            page.get_by_role("button", name="Run regression", exact=True).click()
            expect(
                page.get_by_role("heading", name="Regression passed", exact=False)
            ).to_be_visible(timeout=30000)
            page.get_by_role("tab", name="05 Export").click()
            page.get_by_role("button", name="Preview files").click()
            expect(page.get_by_role("button", name="Save export", exact=True)).to_be_enabled()
            page.get_by_role("button", name="Save export", exact=True).click()
            expect(page.get_by_text("Saved: exports/regression", exact=True)).to_be_visible()
            assert not unexpected, "Installed UI made an external browser request"
            browser.close()
        trial.run(
            "ui_export_pytest",
            [command[0], "-m", "pytest", "-q", "ui-demo/exports/regression/test_regression.py"],
        )
        return round(time.perf_counter() - started, 3)
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        if process.stdout is not None:
            process.stdout.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--python", default=sys.executable, help="Interpreter for a fresh environment."
    )
    parser.add_argument(
        "--browser", action="store_true", help="Use the controller's installed Chromium."
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="New JSON report in ignored local artifacts."
    )
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Choose a new report file.")
    wheel = next((ROOT / "dist").glob("fail2test-*.whl"))
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="fail2test-acceptance-") as temporary:
        directory = Path(temporary)
        trial = Trial(directory)
        environment = directory / "fresh environment"
        trial.run("create_environment", ["uv", "venv", "--python", args.python, str(environment)])
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        trial.run(
            "install_core_wheel",
            ["uv", "pip", "install", "--python", str(python), f"{wheel}[pytest]"],
        )
        command = [str(python), "-m", "fail2test.cli"]
        installed = json.loads(
            trial.run(
                "verify_install_origin",
                [
                    str(python),
                    "-c",
                    "import fail2test,json,sys,importlib.util; from pathlib import Path; "
                    "assert Path(fail2test.__file__).resolve().is_relative_to("
                    "Path(sys.prefix).resolve()); "
                    "assert importlib.util.find_spec('langgraph') is None; "
                    "print(json.dumps({'python':sys.version.split()[0],'version':fail2test.__version__}))",
                ],
            )
        )
        cli_started = time.perf_counter()
        trial.run("cli_init", command + ["init", "demo"])
        case, config = "demo/case", "demo/fail2test.toml"
        trial.run("cli_import", command + ["import", "demo/failure.json", "--out", case])
        trial.run("cli_inspect", command + ["inspect", case, "--json"])
        trial.run("cli_propose", command + ["propose", case, "--out", "demo/proposal.json"])
        trial.run("cli_review", command + ["review", case, "--reviewer", "synthetic-acceptance"])
        trial.run(
            "cli_validate", command + ["validate", case, "--runner", "broken", "--config", config]
        )
        trial.run(
            "cli_broken_fails", command + ["run", case, "--runner", "broken", "--config", config], 1
        )
        trial.run(
            "cli_fixed_passes", command + ["run", case, "--runner", "fixed", "--config", config]
        )
        trial.run(
            "cli_reduce",
            command
            + [
                "reduce",
                case,
                "--runner",
                "broken",
                "--config",
                config,
                "--out",
                "demo/reduced",
                "--max-runs",
                "3",
            ],
        )
        trial.run(
            "cli_export",
            command
            + ["export", case, "--runner", "fixed", "--config", config, "--out", "demo/exported"],
        )
        trial.run(
            "cli_export_pytest",
            [str(python), "-m", "pytest", "-q", "demo/exported/test_regression.py"],
        )
        cli_seconds = round(time.perf_counter() - cli_started, 3)
        ui_seconds = browser_trial(trial, command) if args.browser else None
        constraints = directory / "constraints.txt"
        exported = subprocess.run(
            [
                "uv",
                "export",
                "--locked",
                "--all-extras",
                "--no-dev",
                "--no-emit-project",
                "--no-hashes",
            ],
            cwd=ROOT,
            env=trial.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        constraints.write_text(exported.stdout, encoding="utf-8")
        trial.run(
            "install_native_dependencies",
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
        )
        native_started = time.perf_counter()
        native = directory / "native application"
        native.mkdir()
        for name in ("application.py", "runner.py", "fail2test.toml", "failure.json"):
            shutil.copyfile(ROOT / "examples/langgraph_refunds" / name, native / name)
        application = native / "application.py"
        original = application.read_bytes()
        before = hashlib.sha256(application.read_bytes()).hexdigest()
        case, config = str(native / "case"), str(native / "fail2test.toml")
        trial.run(
            "native_import", command + ["import", str(native / "failure.json"), "--out", case]
        )
        trial.run("native_review", command + ["review", case, "--reviewer", "synthetic-acceptance"])
        trial.run(
            "native_validate",
            command + ["validate", case, "--runner", "broken", "--config", config],
        )
        trial.run("native_fixed", command + ["run", case, "--runner", "fixed", "--config", config])
        trial.run(
            "native_export",
            command
            + [
                "export",
                case,
                "--runner",
                "fixed",
                "--config",
                config,
                "--out",
                str(native / "exported"),
            ],
        )
        exported_test = native / "exported/test_regression.py"
        test_digest = hashlib.sha256(exported_test.read_bytes()).hexdigest()
        trial.run("native_export_passes", [str(python), "-m", "pytest", "-q", str(exported_test)])
        assert b"if deduplicate:" in original
        application.write_bytes(original.replace(b"if deduplicate:", b"if False and deduplicate:"))
        reintroduced = trial.run(
            "unchanged_export_detects_reintroduced_bug",
            [str(python), "-m", "pytest", "-q", str(exported_test)],
            1,
        )
        assert "Fail2Test regression" in reintroduced, "Expected a behavioral assertion failure"
        application.write_bytes(original)
        trial.run(
            "unchanged_export_passes_after_restore",
            [str(python), "-m", "pytest", "-q", str(exported_test)],
        )
        assert hashlib.sha256(exported_test.read_bytes()).hexdigest() == test_digest
        assert hashlib.sha256(application.read_bytes()).hexdigest() == before
        report = {
            "platform": platform.platform(),
            "installed": installed,
            "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "cli_workflow_seconds": cli_seconds,
            "installed_ui_seconds": ui_seconds,
            "native_workflow_seconds": round(time.perf_counter() - native_started, 3),
            "total_seconds": round(time.perf_counter() - started, 3),
            "native_runner_nonblank_lines": sum(
                bool(line.strip()) for line in (native / "runner.py").read_text().splitlines()
            ),
            "production_factory_changes_required_for_injected_example": 0,
            "same_export_detected_bug_and_passed_fix": True,
            "human_usability_measured": False,
            "provider_calls": False,
            "events": trial.events,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "events"}, indent=2))


if __name__ == "__main__":
    main()
