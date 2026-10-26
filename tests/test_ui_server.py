from __future__ import annotations

import http.client
import json
import threading
import time

import pytest

from fail2test.errors import Fail2TestError
from fail2test.jsonio import read_json
from fail2test.ui.server import LocalServer, Workspace
from fail2test.workflow import artifact_identity, preview_pytest


@pytest.fixture
def ui_server(app_project):
    server = LocalServer(Workspace(app_project), port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(server, route, data=None, *, headers=None, method=None, raw=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=15)
    supplied = {"Authorization": f"Bearer {server.token}", "Origin": server.origin}
    if data is not None or raw is not None:
        supplied["Content-Type"] = "application/json"
    supplied.update(headers or {})
    body = raw if raw is not None else json.dumps(data) if data is not None else None
    connection.request(method or ("POST" if body is not None else "GET"), route, body, supplied)
    response = connection.getresponse()
    content = response.read()
    status, metadata = response.status, dict(response.headers)
    connection.close()
    return status, json.loads(content) if metadata[
        "Content-Type"
    ] == "application/json" else content


def imported(server, name="example"):
    status, item = request(server, "/api/import-sample", {"name": name})
    assert status == 200, item
    return item


def payload(item, **extra):
    return {"path": item["path"], "expected_digest": item["digest"], **extra}


def reviewed_item(server):
    item = imported(server)
    status, item = request(
        server,
        "/api/review",
        payload(
            item,
            reviewer="browser-owner",
            selected_rule=item["case"]["rules"][0]["id"],
            acknowledged=True,
        ),
    )
    assert status == 200, item
    return item


def job(server, item, action, runner="broken", **extra):
    status, result = request(
        server, "/api/jobs", payload(item, action=action, runner=runner, **extra)
    )
    assert status == 200, result
    deadline = time.monotonic() + 40
    while result["status"] == "running" and time.monotonic() < deadline:
        time.sleep(0.05)
        status, result = request(server, f"/api/jobs/{result['id']}")
        assert status == 200
    assert result["status"] == "completed", result
    return result


@pytest.mark.parametrize(
    "headers,code",
    [
        ({"Authorization": "Bearer invalid"}, "SESSION_REQUIRED"),
        ({"Origin": "https://unrelated.example"}, "ORIGIN_REJECTED"),
        ({"Origin": "null"}, "ORIGIN_REJECTED"),
        ({"Host": "evil.example:8765"}, "HOST_REJECTED"),
    ],
)
def test_local_session_boundary(ui_server, headers, code):
    status, body = request(ui_server, "/api/import-sample", {"name": "blocked"}, headers=headers)
    assert status in {401, 403}
    assert body["error"]["code"] == code
    assert not (ui_server.workspace.root / "cases/blocked").exists()


def test_origin_required_and_preflight_rejected(ui_server):
    conn = http.client.HTTPConnection("127.0.0.1", ui_server.server_port)
    conn.request(
        "POST",
        "/api/import-sample",
        '{"name":"blocked"}',
        {"Authorization": f"Bearer {ui_server.token}", "Content-Type": "application/json"},
    )
    response = conn.getresponse()
    assert response.status == 403
    response.read()
    conn.close()
    assert request(ui_server, "/api/jobs", method="OPTIONS")[0] == 405
    assert request(ui_server, "/api/import-sample")[0] == 400


def test_static_allowlist_and_security_headers(ui_server):
    conn = http.client.HTTPConnection("127.0.0.1", ui_server.server_port)
    conn.request("GET", "/")
    response = conn.getresponse()
    assert response.status == 200
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cache-Control"] == "no-store"
    assert "Access-Control-Allow-Origin" not in response.headers
    assert ui_server.token.encode() not in response.read()
    conn.close()
    for path in ("/assets/app.js", "/assets/app.css"):
        assert request(ui_server, path)[0] == 200
    for path in ("/fail2test.toml", "/assets/../server.py", "/.git/config"):
        assert request(ui_server, path)[0] == 400


@pytest.mark.parametrize(
    "path", ["../outside", "/absolute", "C:/drive", "a\\b", ".git/config", "a/../b", "a//b"]
)
def test_workspace_path_rejection(ui_server, path):
    with pytest.raises(Fail2TestError, match="UNSAFE_PATH"):
        ui_server.workspace.path(path)


def test_link_escape_rejected(ui_server, tmp_path):
    link = ui_server.workspace.root / "linked"
    try:
        link.symlink_to(tmp_path, target_is_directory=True)
    except OSError:
        pytest.skip("Creating symlinks needs OS privilege on this machine")
    with pytest.raises(Fail2TestError, match="UNSAFE_PATH"):
        ui_server.workspace.path("linked/case.json")


def test_upload_bounds_duplicate_json_and_invalid_data(ui_server):
    status, body = request(ui_server, "/api/import", raw='{"name":"a","name":"b"}')
    assert status == 400 and body["error"]["code"] == "DUPLICATE_JSON_KEY"
    status, body = request(ui_server, "/api/import", {"name": "invalid", "source_text": "{}"})
    assert status == 400 and body["error"]["code"] == "UNSUPPORTED_FORMAT"
    status, body = request(ui_server, "/api/import", {"name": "invalid", "source_text": "{"})
    assert status == 400 and body["error"]["code"] == "INVALID_JSON"
    status, body = request(
        ui_server, "/api/import", raw="{}", headers={"Content-Length": "10485761"}
    )
    assert status == 400 and body["error"]["code"] == "INPUT_TOO_LARGE"


def test_sanitization_before_persistence_and_inert_inspection(ui_server, case_data, monkeypatch):
    case_data["input"]["password"] = "unique-raw-sensitive-value"
    case_data["title"] = "<script>window.BAD=true</script>"
    status, item = request(
        ui_server, "/api/import", {"name": "sanitized", "source_text": json.dumps(case_data)}
    )
    assert status == 200, item
    root = ui_server.workspace.root
    for path in (root / "cases/sanitized").glob("*"):
        assert "unique-raw-sensitive-value" not in path.read_text()
    assert item["manifest"]["sanitization_changes"]
    marker = root / "application-was-imported"
    (root / "refund_app.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).touch()\n"
    )
    assert request(ui_server, "/api/case?path=cases/sanitized")[0] == 200
    assert request(ui_server, "/api/cases")[0] == 200
    assert not marker.exists()


def test_review_edit_staleness_and_export_preconditions(ui_server):
    item = imported(ui_server)
    status, body = request(ui_server, "/api/jobs", payload(item, action="run", runner="broken"))
    assert status == 400 and body["error"]["code"] == "REVIEW_REQUIRED"
    status, body = request(
        ui_server, "/api/review", payload(item, reviewer="owner", selected_rule="x")
    )
    assert status == 400 and body["error"]["code"] == "REVIEW_REQUIRED"
    item = reviewed_item_named(ui_server, item)
    status, body = request(
        ui_server, "/api/export-preview", payload(item, runner="fixed", name="test")
    )
    assert status == 400 and body["error"]["code"] == "VALIDATION_REQUIRED"
    invalid = dict(item["case"], rules=[])
    status, body = request(ui_server, "/api/edit", payload(item, case_text=json.dumps(invalid)))
    assert status == 400 and body["error"]["code"] == "INVALID_DATA"
    assert request(ui_server, "/api/case?path=" + item["path"])[1]["review_valid"]
    changed = dict(item["case"], title="Changed case")
    status, edited = request(ui_server, "/api/edit", payload(item, case_text=json.dumps(changed)))
    assert status == 200 and not edited["review_valid"] and not edited["baseline_valid"]
    status, body = request(ui_server, "/api/propose", payload(item))
    assert status == 400 and body["error"]["code"] == "STALE_CASE"
    assert artifact_identity(ui_server.workspace.root / edited["path"]) == edited["digest"]


def reviewed_item_named(server, item):
    status, reviewed = request(
        server,
        "/api/review",
        payload(
            item, reviewer="owner", selected_rule=item["case"]["rules"][0]["id"], acknowledged=True
        ),
    )
    assert status == 200, reviewed
    return reviewed


def test_end_to_end_parity_reduction_and_export(ui_server):
    item = reviewed_item(ui_server)
    baseline = job(ui_server, item, "validate")
    assert baseline["result"]["outcome"] == "fail"
    fixed = job(ui_server, item, "run", "fixed")
    assert fixed["result"]["outcome"] == "pass"
    status, preview = request(
        ui_server, "/api/export-preview", payload(item, runner="fixed", name="regression")
    )
    assert status == 200, preview
    destination = ui_server.workspace.root / "exports/regression"
    assert not destination.exists()
    assert preview["files"] == preview_pytest(
        ui_server.workspace.root / item["path"],
        runner="fixed",
        config=ui_server.workspace.config,
        out=destination,
    )
    status, exported = request(
        ui_server, "/api/export", payload(item, runner="fixed", name="regression")
    )
    assert status == 200 and exported["saved"]
    for name, content in preview["files"].items():
        assert (destination / name).read_text() == content
    reduced = job(ui_server, item, "reduce", name="reduced", max_runs=3)
    derived = request(ui_server, "/api/case?path=" + reduced["result"]["derived_path"])[1]
    assert not derived["review_valid"]
    assert derived["reduction-report.json"]["review_required"]
    assert read_json(destination / "case.json") == item["case"]


def test_busy_jobs_are_serial_and_failures_remain_incomplete(ui_server):
    root = ui_server.workspace.root
    (root / "refund_app.py").write_text(
        "import time\ndef broken(context, value):\n time.sleep(2)\n"
    )
    item = reviewed_item(ui_server)
    status, running = request(ui_server, "/api/jobs", payload(item, action="run", runner="broken"))
    assert status == 200
    status, body = request(ui_server, "/api/propose", payload(item))
    assert status == 400 and body["error"]["code"] == "WORKSPACE_BUSY"
    assert request(ui_server, "/api/case?path=" + item["path"])[0] == 200
    ui_server.workspace.thread.join(timeout=10)
    completed = request(ui_server, "/api/jobs/" + running["id"])[1]
    assert completed["result"]["execution_status"] == "incomplete"
    assert completed["result"]["outcome"] == "not_evaluated"


def test_runner_imports_and_duplicate_rule_keys_cannot_bypass_contract(ui_server):
    item = reviewed_item(ui_server)
    status, body = request(
        ui_server, "/api/jobs", payload(item, action="run", runner="malicious_module:execute")
    )
    assert status == 400 and body["error"]["code"] == "INVALID_RUNNER_CONFIG"
    status, body = request(
        ui_server,
        "/api/edit",
        payload(item, case_text=json.dumps(item["case"]), rule_texts=['{"id":"a","id":"b"}']),
    )
    assert status == 400 and body["error"]["code"] == "DUPLICATE_JSON_KEY"
    assert artifact_identity(ui_server.workspace.root / item["path"]) == item["digest"]


def test_timeout_is_incomplete_and_edit_clears_reproduced_baseline(ui_server):
    item = reviewed_item(ui_server)
    job(ui_server, item, "validate")
    assert request(ui_server, "/api/case?path=" + item["path"])[1]["baseline_valid"]
    changed = dict(item["case"], title="Review changed behavior")
    status, edited = request(ui_server, "/api/edit", payload(item, case_text=json.dumps(changed)))
    assert status == 200 and not edited["baseline_valid"]
    item = reviewed_item_named(ui_server, edited)
    root = ui_server.workspace.root
    config = root / "fail2test.toml"
    config.write_text(config.read_text().replace("10.0", "0.2"))
    (root / "refund_app.py").write_text(
        "import time\ndef broken(data, context):\n time.sleep(10)\n"
    )
    result = job(ui_server, item, "validate")["result"]
    assert result["execution_status"] == "incomplete"
    assert result["tooling_errors"] == ["RUNNER_TIMEOUT"]
    assert not request(ui_server, "/api/case?path=" + item["path"])[1]["baseline_valid"]


@pytest.mark.parametrize("no_open", [True, False])
def test_cli_explicit_start_and_shutdown(app_project, monkeypatch, no_open):
    from typer.testing import CliRunner

    from fail2test.cli import app

    opened = []
    monkeypatch.setattr("webbrowser.open", lambda url: opened.append(url))

    def interrupt(server):
        raise KeyboardInterrupt

    monkeypatch.setattr(LocalServer, "serve_forever", interrupt)
    args = ["ui", "--workspace", str(app_project), "--port", "0"]
    if no_open:
        args.append("--no-open")
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0
    assert "127.0.0.1:" in result.output and "#session=" in result.output
    assert "Stopping local UI" in result.output
    assert bool(opened) is not no_open


def test_ai_http_preview_send_guards_and_case_is_unchanged(ui_server, case_data, monkeypatch):
    item = imported(ui_server)
    monkeypatch.setenv("OPENROUTER_API_KEY", "synthetic-server-only-key")
    started, finish = threading.Event(), threading.Event()

    def fake_provider(*args):
        started.set()
        assert finish.wait(timeout=5)
        return {
            "model": "synthetic-free",
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps({"rules": case_data["rules"], "notes": []})},
                }
            ],
        }

    monkeypatch.setattr("fail2test.suggestions.send_http", fake_provider)
    data = payload(item, profile="openrouter-free", requirement="One refund per order.")
    status, prepared = request(ui_server, "/api/ai-preview", data)
    assert status == 200 and not started.is_set()
    assert "synthetic-server-only-key" not in json.dumps(prepared)
    status, error = request(ui_server, "/api/ai-propose", data)
    assert status == 400 and error["error"]["code"] == "AI_CONSENT_REQUIRED"
    status, error = request(
        ui_server, "/api/ai-propose", data | {"acknowledged": True, "request_digest": "wrong"}
    )
    assert status == 400 and error["error"]["code"] == "STALE_AI_PREVIEW"
    status, running = request(
        ui_server,
        "/api/ai-propose",
        data | {"acknowledged": True, "request_digest": prepared["request_digest"]},
    )
    assert status == 200 and started.wait(timeout=3)
    try:
        status, error = request(ui_server, "/api/propose", payload(item))
        assert status == 400 and error["error"]["code"] == "WORKSPACE_BUSY"
    finally:
        finish.set()
    ui_server.workspace.thread.join(timeout=5)
    result = request(ui_server, "/api/jobs/" + running["id"])[1]
    assert result["status"] == "completed" and result["result"]["review_required"]
    assert request(ui_server, "/api/case?path=" + item["path"])[1]["digest"] == item["digest"]
    assert not request(ui_server, "/api/case?path=" + item["path"])[1]["review_valid"]


def test_bad_optional_ai_config_does_not_block_key_free_ui(ui_server):
    config = ui_server.workspace.config
    config.write_text(
        config.read_text().replace('model = "openrouter/free"', 'model = "paid/model"')
    )
    status, result = request(ui_server, "/api/workspace")
    assert status == 200 and result["runners"]
    assert result["suggestion_profiles"] == {}
    assert result["suggestion_error"]["code"] == "INVALID_AI_CONFIG"
    item = imported(ui_server)
    assert request(ui_server, "/api/propose", payload(item))[0] == 200
