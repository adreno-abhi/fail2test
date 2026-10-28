"""Single-owner loopback UI. Trusted Python runners are not sandboxed."""

from __future__ import annotations

import hmac
import json
import os
import re
import secrets
import threading
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from pydantic import ValidationError

from fail2test.config import load_runner_config
from fail2test.errors import Fail2TestError, validation_message
from fail2test.ingest import import_data, propose_rules
from fail2test.jsonio import MAX_BYTES, loads_json, read_json, write_json
from fail2test.models import Case
from fail2test.privacy import sanitize
from fail2test.reduction import reduce_case
from fail2test.suggestions import preview, profiles, propose
from fail2test.workflow import (
    artifact_identity,
    export_pytest,
    load_manifest,
    preview_pytest,
    review_case,
    run_reviewed,
    save_manifest,
    validate_baseline,
)


class Workspace:
    """Own path policy and serialization; delegate product semantics to the engine."""

    def __init__(
        self, root: Path, config: str = "fail2test.toml", env_file: Path | None = None
    ) -> None:
        self.root = root.resolve(strict=True)
        if not self.root.is_dir():
            raise Fail2TestError("INVALID_WORKSPACE", "Choose an existing workspace directory.")
        self.config = self.path(config)
        self.env_file = env_file or self.root / ".env.local"
        try:
            runners = tomllib.loads(self.config.read_text(encoding="utf-8"))["runners"]
            if not isinstance(runners, dict) or not runners:
                raise ValueError
            self.runners = sorted(runners)
            for name in self.runners:
                load_runner_config(self.config, name)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise Fail2TestError(
                "INVALID_RUNNER_CONFIG", "Choose a valid local TOML config."
            ) from exc
        self.lock = threading.Lock()
        self.jobs: dict[str, dict[str, Any]] = {}
        self.thread: threading.Thread | None = None
        self.active = False

    def path(self, relative: str) -> Path:
        if not isinstance(relative, str) or len(relative) > 500:
            raise Fail2TestError("UNSAFE_PATH", "Use a short workspace-relative path.")
        parts = relative.split("/")
        if any(not p or p.startswith(".") or ":" in p or "\\" in p for p in parts):
            raise Fail2TestError(
                "UNSAFE_PATH", "Use a workspace path without hidden or parent parts."
            )
        target = self.root.joinpath(*parts)
        # Refuse all links/junctions along the path, even those pointing within the workspace.
        cursor = self.root
        for part in parts:
            cursor /= part
            if cursor.is_symlink() or cursor.is_junction():
                raise Fail2TestError("UNSAFE_PATH", "Linked workspace paths are not supported.")
        if not target.resolve().is_relative_to(self.root):
            raise Fail2TestError("UNSAFE_PATH", "The path must remain inside this workspace.")
        return target

    def bundle(self, relative: str) -> Path:
        target = self.path(relative)
        if not target.is_dir():
            raise Fail2TestError("CASE_NOT_FOUND", "Choose an imported case bundle directory.")
        for name in ("case.json", "manifest.json", "evidence.json", "import-report.json"):
            self.path(f"{relative}/{name}")
        load_manifest(target)
        return target

    def current(self, data: dict[str, Any]) -> Path:
        target = self.bundle(data["path"])
        if not hmac.compare_digest(artifact_identity(target), str(data["expected_digest"])):
            raise Fail2TestError("STALE_CASE", "The case changed. Reopen it before acting.")
        return target

    def inspect(self, relative: str) -> dict[str, Any]:
        target = self.bundle(relative)
        data = read_json(target / "case.json")
        manifest = load_manifest(target)
        identity = artifact_identity(target)
        result = {
            "path": relative,
            "case": data,
            "digest": identity,
            "manifest": manifest.model_dump(mode="json"),
            "review_valid": bool(manifest.review and manifest.review.case_digest == identity),
            "baseline_valid": bool(manifest.baseline and manifest.baseline.case_digest == identity),
        }
        for name in ("evidence.json", "import-report.json", "reduction-report.json"):
            safe = self.path(f"{relative}/{name}")
            if safe.is_file():
                result[name] = read_json(safe)
        clean, _ = sanitize(result)
        return dict(clean)

    def cases(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        visited = 0
        for directory, children, names in os.walk(self.root, followlinks=False):
            children[:] = sorted(
                p
                for p in children
                if not p.startswith(".")
                and p not in {"node_modules", "__pycache__"}
                and not (Path(directory) / p).is_junction()
                and not (Path(directory) / p).is_symlink()
            )
            visited += 1
            if visited > 2000 or len(result) >= 200:
                break
            if {"case.json", "manifest.json"}.issubset(names):
                relative = Path(directory).relative_to(self.root).as_posix()
                if relative == ".":
                    continue
                try:
                    item = self.inspect(relative)
                    result.append(
                        {k: item[k] for k in ("path", "digest", "review_valid", "baseline_valid")}
                        | {"title": item["case"]["title"]}
                    )
                except (Fail2TestError, KeyError, TypeError):
                    result.append({"path": relative, "title": "Unreadable bundle", "invalid": True})
        return result

    def new_directory(self, prefix: str, name: str) -> Path:
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", name):
            raise Fail2TestError("INVALID_NAME", "Use 1–64 lowercase letters, numbers, - or _.")
        target = self.path(f"{prefix}/{name}")
        if target.exists():
            raise Fail2TestError("OUTPUT_EXISTS", "Choose a new destination name.")
        return target

    def get(self, route: str, query: dict[str, list[str]]) -> Any:
        with self.lock:
            if route == "/api/workspace":
                try:
                    available = {
                        name: value.model_dump(mode="json")
                        for name, value in profiles(self.config).items()
                    }
                    suggestion_error = None
                except Fail2TestError as exc:
                    available = {}
                    suggestion_error = safe_error(exc)
                return {
                    "name": self.root.name,
                    "runners": self.runners,
                    "config": self.config.relative_to(self.root).as_posix(),
                    "sample_available": (self.root / "failure.json").is_file(),
                    "suggestion_profiles": available,
                    "suggestion_error": suggestion_error,
                }
            if route == "/api/cases":
                return self.cases()
            if route == "/api/case":
                return self.inspect(query["path"][0])
            if route.startswith("/api/jobs/") and route.removeprefix("/api/jobs/") in self.jobs:
                return dict(self.jobs[route.removeprefix("/api/jobs/")])
        raise Fail2TestError("NOT_FOUND", "Unknown API resource.")

    def post(self, route: str, data: dict[str, Any]) -> Any:
        with self.lock:
            if self.active:
                raise Fail2TestError("WORKSPACE_BUSY", "Wait for the active execution to finish.")
            if route in {"/api/import", "/api/import-sample"}:
                raw = (
                    read_json(self.path("failure.json"))
                    if route.endswith("sample")
                    else loads_json(data["source_text"])
                )
                out = self.new_directory("cases", data["name"])
                import_data(raw, out)
                return self.inspect(out.relative_to(self.root).as_posix())
            if route not in {
                "/api/edit",
                "/api/propose",
                "/api/review",
                "/api/jobs",
                "/api/export-preview",
                "/api/export",
                "/api/ai-preview",
                "/api/ai-propose",
            }:
                raise Fail2TestError("NOT_FOUND", "Unknown API action.")
            target = self.current(data)
            if route in {"/api/ai-preview", "/api/ai-propose"}:
                prepared = preview(
                    target,
                    config=self.config,
                    profile=data["profile"],
                    requirement=data["requirement"],
                )
                if route == "/api/ai-preview":
                    return prepared
                if data.get("acknowledged") is not True:
                    raise Fail2TestError(
                        "AI_CONSENT_REQUIRED", "Acknowledge the preview before sending."
                    )
                if prepared["request_digest"] != data.get("request_digest"):
                    raise Fail2TestError("STALE_AI_PREVIEW", "Preview the current request again.")
                job_id = secrets.token_hex(12)
                if len(self.jobs) >= 20:
                    del self.jobs[next(iter(self.jobs))]
                job = {
                    "id": job_id,
                    "status": "running",
                    "action": "suggest",
                    "path": data["path"],
                    "profile": data["profile"],
                    "digest": data["expected_digest"],
                }
                self.jobs[job_id] = job
                self.active = True
                self.thread = threading.Thread(
                    target=self.execute_suggestion,
                    args=(
                        job_id,
                        target,
                        data["profile"],
                        data["requirement"],
                        prepared["request_digest"],
                    ),
                    daemon=True,
                )
                self.thread.start()
                return dict(job)
            if route == "/api/propose":
                return propose_rules(target)
            if route == "/api/edit":
                raw = loads_json(data["case_text"])
                if "rule_texts" in data:
                    if not isinstance(data["rule_texts"], list):
                        raise Fail2TestError(
                            "INVALID_DATA", "Supply a list of JSON rule documents."
                        )
                    raw["rules"] = [loads_json(text) for text in data["rule_texts"]]
                raw, changes = sanitize(raw)
                try:
                    case = Case.model_validate(raw)
                except ValidationError as exc:
                    raise Fail2TestError("INVALID_DATA", validation_message(exc, Case)) from None
                manifest = load_manifest(target)
                manifest.review, manifest.baseline = None, None
                manifest.sanitization_changes.extend(changes)
                if changes:
                    case.provenance.sanitization = "review_required"
                # Clear authorization before changing the file, including on interrupted writes.
                save_manifest(target, manifest)
                write_json(target / "case.json", case.model_dump(mode="json"), overwrite=True)
                return self.inspect(data["path"])
            if route == "/api/review":
                if data.get("acknowledged") is not True:
                    raise Fail2TestError("REVIEW_REQUIRED", "Acknowledge the evidence and rules.")
                review_case(target, reviewer=data["reviewer"], selected_rule=data["selected_rule"])
                return self.inspect(data["path"])
            runner = data["runner"]
            if runner not in self.runners:
                raise Fail2TestError("INVALID_RUNNER_CONFIG", "Choose a preconfigured runner.")
            if route in {"/api/export-preview", "/api/export"}:
                out = self.new_directory("exports", data["name"])
                prepared = preview_pytest(target, runner=runner, config=self.config, out=out)
                if route == "/api/export":
                    export_pytest(target, runner=runner, config=self.config, out=out)
                return {
                    "files": prepared,
                    "path": out.relative_to(self.root).as_posix(),
                    "saved": route == "/api/export",
                }
            action = data["action"]
            if action not in {"validate", "run", "reduce"}:
                raise Fail2TestError("INVALID_ACTION", "Choose validate, run or reduce.")
            # Preflight review before creating a job; execution rechecks it too.
            from fail2test.workflow import checked_case

            checked_case(target)
            derived = self.new_directory("cases", data["name"]) if action == "reduce" else None
            max_runs = data.get("max_runs", 25)
            if type(max_runs) is not int or not 1 <= max_runs <= 100:
                raise Fail2TestError("INVALID_BUDGET", "Choose 1–100 reduction attempts.")
            job_id = secrets.token_hex(12)
            if len(self.jobs) >= 20:
                del self.jobs[next(iter(self.jobs))]
            job = {
                "id": job_id,
                "status": "running",
                "action": action,
                "path": data["path"],
                "runner": runner,
                "digest": data["expected_digest"],
            }
            self.jobs[job_id] = job
            self.active = True
            self.thread = threading.Thread(
                target=self.execute,
                args=(job_id, target, runner, action, derived, max_runs),
                daemon=True,
            )
            self.thread.start()
            return dict(job)

    def execute_suggestion(
        self, job_id: str, target: Path, profile: str, requirement: str, request_digest: str
    ) -> None:
        try:
            result = propose(
                target,
                config=self.config,
                profile=profile,
                requirement=requirement,
                request_digest=request_digest,
                acknowledged=True,
                env_file=self.env_file,
            )
            with self.lock:
                self.jobs[job_id].update(status="completed", result=result)
        except Exception as exc:
            with self.lock:
                self.jobs[job_id].update(status="error", error=safe_error(exc))
        finally:
            with self.lock:
                self.active = False

    def execute(
        self, job_id: str, target: Path, runner: str, action: str, out: Path | None, max_runs: int
    ) -> None:
        try:
            if action == "reduce":
                assert out is not None
                report = reduce_case(
                    target,
                    runner=runner,
                    config=self.config,
                    out=out,
                    max_runs=max_runs,
                    timeout_seconds=30,
                )
                result = {
                    "report": report,
                    "derived_path": out.relative_to(self.root).as_posix(),
                    "original_input": read_json(target / "case.json")["input"],
                    "reduced_input": read_json(out / "case.json")["input"],
                }
            else:
                function = validate_baseline if action == "validate" else run_reviewed
                result = function(
                    target, runner=runner, config=self.config, timeout_seconds=30
                ).model_dump(mode="json")
            with self.lock:
                self.jobs[job_id].update(status="completed", result=result)
        except Exception as exc:
            error = safe_error(exc)
            with self.lock:
                self.jobs[job_id].update(status="error", error=error)
        finally:
            with self.lock:
                self.active = False


def safe_error(exc: Exception) -> dict[str, str]:
    if isinstance(exc, Fail2TestError):
        return {"code": exc.code, "message": exc.message}
    if isinstance(exc, ValidationError):
        return {
            "code": "INVALID_DATA",
            "message": "Check the supported data/configuration contract.",
        }
    return {
        "code": "INVALID_REQUEST",
        "message": "Check the input fields and workspace permissions.",
    }


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False

    def __init__(self, workspace: Workspace, port: int = 8765) -> None:
        self.workspace = workspace
        self.token = secrets.token_urlsafe(32)
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"

    def server_close(self) -> None:
        super().server_close()
        worker = self.workspace.thread
        if worker is not None:
            worker.join(timeout=45)


class Handler(BaseHTTPRequestHandler):
    server: LocalServer
    server_version = "Fail2Test"
    sys_version = ""

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, format: str, *args: Any) -> None:
        pass  # No paths, tokens, imported evidence or application output in access logs.

    def respond(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; "
            "style-src 'self'; connect-src 'self'; img-src 'self'; "
            "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(body)

    def dispatch(self, mutate: bool) -> None:
        try:
            hosts = self.headers.get_all("Host", [])
            origins = self.headers.get_all("Origin", [])
            if hosts != [self.server.origin.removeprefix("http://")]:
                self.respond(
                    403, b'{"error":{"code":"HOST_REJECTED","message":"Use the launch URL."}}'
                )
                return
            if (origins and origins != [self.server.origin]) or (mutate and not origins):
                self.respond(
                    403, b'{"error":{"code":"ORIGIN_REJECTED","message":"Use the local UI."}}'
                )
                return
            parsed = urlsplit(self.path)
            assets = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/assets/app.js": ("app.js", "text/javascript; charset=utf-8"),
                "/assets/app.css": ("app.css", "text/css; charset=utf-8"),
            }
            if not mutate and parsed.path in assets:
                name, media = assets[parsed.path]
                self.respond(
                    200, files("fail2test.ui").joinpath("static", name).read_bytes(), media
                )
                return
            auth = self.headers.get_all("Authorization", [])
            if len(auth) != 1 or not hmac.compare_digest(auth[0], f"Bearer {self.server.token}"):
                self.respond(
                    401,
                    b'{"error":{"code":"SESSION_REQUIRED",'
                    b'"message":"Reopen the launch URL from your terminal."}}',
                )
                return
            if mutate:
                lengths = self.headers.get_all("Content-Length", [])
                if (
                    len(lengths) != 1
                    or not lengths[0].isdigit()
                    or self.headers.get("Transfer-Encoding")
                    or self.headers.get_content_type() != "application/json"
                ):
                    raise Fail2TestError("INVALID_BODY", "Send one bounded JSON request body.")
                length = int(lengths[0])
                if length > MAX_BYTES:
                    raise Fail2TestError("INPUT_TOO_LARGE", "JSON input exceeds 10 MiB.")
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise Fail2TestError("INVALID_BODY", "The request body was interrupted.")
                data = loads_json(raw)
                if not isinstance(data, dict):
                    raise Fail2TestError("INVALID_BODY", "Use a JSON object request.")
                result = self.server.workspace.post(parsed.path, data)
            else:
                result = self.server.workspace.get(parsed.path, parse_qs(parsed.query))
            clean, _ = sanitize(result)
            self.respond(200, json.dumps(clean, ensure_ascii=True).encode())
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as exc:
            self.respond(400, json.dumps({"error": safe_error(exc)}).encode())

    def do_GET(self) -> None:
        self.dispatch(False)

    def do_POST(self) -> None:
        self.dispatch(True)

    def do_OPTIONS(self) -> None:
        self.respond(405, b'{"error":{"code":"METHOD_REJECTED"}}')
