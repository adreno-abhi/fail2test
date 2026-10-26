"""Local CLI. Inspection never imports application code."""

from __future__ import annotations

import json
import platform
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import ValidationError

from fail2test import __version__
from fail2test.errors import Fail2TestError
from fail2test.ingest import import_case, propose_rules
from fail2test.jsonio import read_json, write_json, write_text
from fail2test.models import Case, RunResult, case_schema
from fail2test.privacy import sanitize
from fail2test.reduction import reduce_case
from fail2test.workflow import (
    case_path,
    export_pytest,
    load_manifest,
    review_case,
    run_reviewed,
    validate_baseline,
)

app = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    help=(
        "Turn agent failures into reviewed pytest regressions. "
        "Fixture execution needs no model key."
    ),
)
ConfigOption = Annotated[Path, typer.Option("--config", help="Trusted local runner configuration.")]
OutOption = Annotated[Path, typer.Option("--out", help="New output directory or file.")]


@app.command("ui")
def local_ui(
    workspace: Annotated[Path, typer.Option(help="Existing trusted local workspace.")],
    config: Annotated[str, typer.Option(help="Workspace-relative runner TOML.")] = "fail2test.toml",
    port: Annotated[int, typer.Option(min=0, max=65535)] = 8765,
    env_file: Annotated[Path | None, typer.Option("--env-file", help="Local AI key file.")] = None,
    no_open: Annotated[
        bool, typer.Option("--no-open", help="Print the launch URL without opening a browser.")
    ] = False,
) -> None:
    """Open the bundled local UI. Stop with Ctrl+C; configured runners execute trusted code."""
    import webbrowser

    from fail2test.ui.server import LocalServer, Workspace

    with errors():
        server = LocalServer(Workspace(workspace, config, env_file), port)
        url = f"{server.origin}/#session={server.token}"
        typer.echo("Local UI — trusted workspace only. Stop with Ctrl+C.")
        typer.echo(url)
        if not no_open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            typer.echo("Stopping local UI; waiting for any bounded execution to finish.")
        finally:
            server.server_close()


@contextmanager
def errors(json_output: bool = False) -> Iterator[None]:
    try:
        yield
    except Fail2TestError as exc:
        if json_output:
            typer.echo(json.dumps({"error": {"code": exc.code, "message": exc.message}}))
        else:
            typer.echo(f"{exc.code}: {exc.message}", err=True)
        raise typer.Exit(exc.exit_code) from exc
    except (ValidationError, ValueError, TypeError):
        typer.echo("INVALID_DATA: Check the supported data/configuration contract.", err=True)
        raise typer.Exit(2) from None
    except OSError:
        typer.echo("FILESYSTEM_ERROR: Check local paths and permissions.", err=True)
        raise typer.Exit(4) from None


def emit(value: Any) -> None:
    clean, _ = sanitize(value)
    typer.echo(json.dumps(clean, indent=2, ensure_ascii=True, allow_nan=False))


def result_exit(result: RunResult) -> int:
    if result.execution_status != "complete":
        return 3
    return 0 if result.outcome == "pass" else 1


@app.command()
def init(
    directory: Annotated[Path, typer.Argument(help="New directory for a key-free example.")] = Path(
        "fail2test-demo"
    ),
) -> None:
    """Create a small example and config; do not execute application code."""
    with errors():
        if directory.exists():
            raise Fail2TestError("OUTPUT_EXISTS", "Choose a new example directory.")
        data = files("fail2test").joinpath("data")
        directory.mkdir(parents=True)
        for source, destination in [
            ("refund_app.py.txt", "refund_app.py"),
            ("fail2test.toml.txt", "fail2test.toml"),
            ("duplicate-refund.case.json", "failure.json"),
        ]:
            write_text(directory / destination, data.joinpath(source).read_text(encoding="utf-8"))
        typer.echo(f"Created {directory}. Follow the key-free quickstart; no code was executed.")


@app.command("import")
def import_command(
    source: Path, out: OutOption, format: Annotated[str, typer.Option("--format")] = "json"
) -> None:
    """Validate and sanitize supported JSON evidence into a new draft bundle."""
    with errors():
        if format != "json":
            raise Fail2TestError("UNSUPPORTED_FORMAT", "Only the neutral JSON format is supported.")
        target = import_case(source, out)
        typer.echo(f"Imported draft: {target}. Review rules and sanitized values before execution.")


@app.command()
def inspect(case: Path, json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    """Inspect metadata without executing application code or printing raw payloads."""
    with errors(json_output):
        raw = read_json(case_path(case))
        if not isinstance(raw, dict) or not isinstance(raw.get("rules"), list):
            raise Fail2TestError("INVALID_CASE", "Inspect a supported imported case bundle.")
        manifest = load_manifest(case)
        value = {
            "case_id": raw.get("case_id"),
            "mode": raw.get("mode"),
            "rule_ids": [rule.get("id") for rule in raw.get("rules", [])],
            "source_complete": manifest.source_complete,
            "review_recorded": manifest.review is not None,
            "baseline_recorded": manifest.baseline is not None,
            "sanitization_changes": len(manifest.sanitization_changes),
        }
        if raw.get("rules"):
            parsed = Case.load(case_path(case))
            value["review_matches_current_case"] = bool(
                manifest.review and manifest.review.case_digest == parsed.case_digest
            )
        emit(value)


@app.command()
def propose(case: Path, out: OutOption) -> None:
    """Write unapproved rule candidates. Historical behavior is not business truth."""
    with errors():
        write_json(out, propose_rules(case))
        typer.echo(f"Wrote {out}. Edit intended behavior before review.")


@app.command("ai-preview")
def ai_preview(
    case: Path,
    profile: Annotated[str, typer.Option("--profile")],
    requirement: Annotated[str, typer.Option("--requirement")],
    out: OutOption,
    config: ConfigOption = Path("fail2test.toml"),
) -> None:
    """Write the exact sanitized model request without contacting a provider."""
    from fail2test.suggestions import preview

    with errors():
        write_json(out, preview(case, config=config, profile=profile, requirement=requirement))
        typer.echo(f"Preview written to {out}. Inspect the destination and request before sending.")


@app.command("ai-propose")
def ai_propose(
    case: Path,
    preview_file: Annotated[Path, typer.Option("--preview")],
    out: OutOption,
    config: ConfigOption = Path("fail2test.toml"),
    env_file: Annotated[Path | None, typer.Option("--env-file")] = None,
    allow_send: Annotated[bool, typer.Option("--allow-send")] = False,
) -> None:
    """Explicitly send a previewed request; write unapproved declarative rules only."""
    from fail2test.suggestions import propose

    with errors():
        if out.exists():
            raise Fail2TestError("OUTPUT_EXISTS", "Choose a new proposal output file.")
        prepared = read_json(preview_file)
        if not isinstance(prepared, dict) or not all(
            isinstance(prepared.get(key), str)
            for key in ("profile", "requirement", "request_digest")
        ):
            raise Fail2TestError("INVALID_AI_PREVIEW", "Use a preview generated by ai-preview.")
        result = propose(
            case,
            config=config,
            profile=prepared["profile"],
            requirement=prepared["requirement"],
            request_digest=prepared["request_digest"],
            acknowledged=allow_send,
            env_file=env_file,
        )
        write_json(out, result)
        typer.echo(f"Unapproved suggestions written to {out}. Review before using them.")


@app.command()
def review(
    case: Path,
    reviewer: Annotated[str, typer.Option("--reviewer")],
    rules: Annotated[Path | None, typer.Option("--rules")] = None,
    rule: Annotated[str | None, typer.Option("--rule")] = None,
) -> None:
    """Acknowledge the exact rules/fixtures with a local reviewer label."""
    with errors():
        proposed = read_json(rules) if rules is not None else None
        if isinstance(proposed, dict):
            proposed = proposed.get("rules")
        if proposed is not None and not isinstance(proposed, list):
            raise Fail2TestError("INVALID_RULES", "Use a rules list or an object containing rules.")
        value = review_case(case, reviewer=reviewer, rules=proposed, selected_rule=rule)
        typer.echo(
            f"Reviewed digest {value.case_digest}. This label is not authenticated identity."
        )


@app.command()
def validate(
    case: Path,
    runner: Annotated[str, typer.Option("--runner")],
    config: ConfigOption = Path("fail2test.toml"),
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Reproduce the selected failure. Exit 0 means the failure was reproduced."""
    with errors(json_output):
        result = validate_baseline(case, runner=runner, config=config)
        manifest = load_manifest(case)
        reproduced = manifest.baseline is not None
        if json_output:
            emit({"baseline_reproduced": reproduced, "result": result.model_dump(mode="json")})
        else:
            typer.echo(
                "Baseline failure reproduced."
                if reproduced
                else "Selected failure was not reproduced."
            )
        raise typer.Exit(0 if reproduced else (3 if result.execution_status != "complete" else 1))


@app.command()
def run(
    case: Path,
    runner: Annotated[str, typer.Option("--runner")],
    config: ConfigOption = Path("fail2test.toml"),
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Execute current application code against reviewed fixtures."""
    with errors(json_output):
        result = run_reviewed(case, runner=runner, config=config)
        if json_output:
            emit(result.model_dump(mode="json"))
        else:
            typer.echo(f"{result.execution_status}: {result.outcome}")
            for rule in result.rule_results:
                typer.echo(f"{'PASS' if rule.passed else 'FAIL'} {rule.rule_id}: {rule.reason}")
            for code in result.tooling_errors:
                typer.echo(code)
        raise typer.Exit(result_exit(result))


@app.command("export")
def export_command(
    case: Path,
    runner: Annotated[str, typer.Option("--runner")],
    out: OutOption,
    config: ConfigOption = Path("fail2test.toml"),
    format: Annotated[str, typer.Option("--format")] = "pytest",
) -> None:
    """Export a validated case as a readable pytest test and portable JSON."""
    with errors():
        if format != "pytest":
            raise Fail2TestError("UNSUPPORTED_FORMAT", "Only pytest export is supported.")
        target = export_pytest(case, runner=runner, config=config, out=out)
        typer.echo(f"Exported {target}. Run it using ordinary pytest.")


@app.command()
def reduce(
    case: Path,
    runner: Annotated[str, typer.Option("--runner")],
    out: OutOption,
    config: ConfigOption = Path("fail2test.toml"),
    max_runs: Annotated[int, typer.Option("--max-runs")] = 50,
) -> None:
    """Reduce inputs only while fresh execution preserves the selected failure."""
    with errors():
        emit(reduce_case(case, runner=runner, config=config, out=out, max_runs=max_runs))


@app.command()
def doctor() -> None:
    """Report local tooling metadata without inspecting credentials or providers."""
    emit(
        {
            "fail2test": __version__,
            "python": platform.python_version(),
            "platform": platform.system(),
            "executable": sys.executable,
            "mode": "local fixture execution",
            "network_probe": False,
        }
    )


@app.command()
def schema(out: Annotated[Path | None, typer.Option("--out")] = None) -> None:
    """Print or write the schema generated from runtime case models."""
    with errors():
        if out is None:
            emit(case_schema())
        else:
            write_json(out, case_schema())


if __name__ == "__main__":
    app()
