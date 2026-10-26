from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from typer.testing import CliRunner

from fail2test.cli import app
from fail2test.errors import Fail2TestError
from fail2test.ingest import import_case
from fail2test.jsonio import read_json, write_json
from fail2test.suggestions import Profile, credential, preview, profiles, propose, send_http
from fail2test.workflow import artifact_identity, load_manifest


@pytest.fixture
def ai_case(app_project, monkeypatch):
    target = import_case(app_project / "failure.json", app_project / "case")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-synthetic-test-key-only")
    return target, app_project / "fail2test.toml"


def prepare(ai_case, **extra):
    target, config = ai_case
    return preview(
        target,
        config=config,
        profile="openrouter-free",
        requirement=extra.get("requirement", "At most one refund per order."),
    )


def completion(case_data, **extra):
    return {
        "model": "synthetic-provider-model",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": json.dumps({"rules": case_data["rules"], "notes": ["Check intent."]})
                },
            }
        ],
        **extra,
    }


def ask(ai_case, prepared, **extra):
    return propose(
        ai_case[0],
        config=ai_case[1],
        profile="openrouter-free",
        requirement=prepared["requirement"],
        request_digest=prepared["request_digest"],
        acknowledged=extra.get("acknowledged", True),
    )


def test_preview_is_sanitized_minimal_and_has_no_network_or_key(ai_case, monkeypatch):
    target, _ = ai_case
    data = read_json(target)
    data["input"]["api_key"] = "private-input-value"
    data["provenance"]["source_reference"] = "private-source-file-path"
    write_json(target, data, overwrite=True)
    monkeypatch.setattr(
        "fail2test.suggestions.send_http", lambda *args: pytest.fail("preview sent data")
    )
    result = prepare(ai_case)
    serialized = json.dumps(result)
    assert "private-input-value" not in serialized
    assert "private-source-file-path" not in serialized
    assert "sk-or-v1-synthetic-test-key-only" not in serialized
    assert result["request"]["provider"]["max_price"] == {"prompt": 0, "completion": 0}
    assert result["request"]["provider"]["data_collection"] == "deny"
    assert result["request"]["provider"]["allow_fallbacks"] is False
    assert "models" not in result["request"]


@pytest.mark.parametrize(
    "changes",
    [
        {"model": "paid/model"},
        {"base_url": "http://openrouter.ai/api/v1"},
        {"base_url": "https://evil.example/api/v1"},
        {"base_url": "https://openrouter.ai/api/v1?key=secret"},
        {"base_url": "https://user:password@openrouter.ai/api/v1"},
        {"timeout_seconds": 31},
        {"api_key_env": "invalid-name"},
    ],
)
def test_openrouter_profile_guards(changes):
    data = dict(
        kind="openrouter",
        base_url="https://openrouter.ai/api/v1",
        model="openrouter/free",
        api_key_env="OPENROUTER_API_KEY",
    )
    with pytest.raises(ValueError):
        Profile.model_validate(data | changes)


def test_compatible_and_local_are_explicit_profiles():
    with pytest.raises(ValueError):
        Profile(
            kind="compatible",
            base_url="https://openrouter.ai/api/v1",
            model="openrouter/free",
            api_key_env="KEY",
            free_only=False,
        )
    with pytest.raises(ValueError):
        Profile(kind="local", base_url="http://example.com/v1", model="example")
    assert Profile(kind="local", base_url="http://127.0.0.1:11434/v1", model="local-model")
    assert Profile(
        kind="compatible",
        base_url="https://example.com/v1",
        model="model",
        api_key_env="KEY",
        free_only=False,
    )


def test_proposal_is_validated_and_does_not_modify_case(ai_case, case_data, monkeypatch):
    captured = []

    def fake(url, body, key, timeout):
        captured.append((url, body))
        assert key == "sk-or-v1-synthetic-test-key-only" and timeout <= 30
        return completion(case_data)

    monkeypatch.setattr("fail2test.suggestions.send_http", fake)
    prepared = prepare(ai_case)
    before = artifact_identity(ai_case[0])
    result = ask(ai_case, prepared)
    assert result["review_required"] is True and result["source"] == "model"
    assert result["rules"] == case_data["rules"]
    assert result["actual_model"] == "synthetic-provider-model"
    assert artifact_identity(ai_case[0]) == before
    assert load_manifest(ai_case[0]).review is None
    assert len(captured) == 1


@pytest.mark.parametrize(
    "content",
    [
        '{"rules":[],"notes":[]}',
        '{"rules":[{"kind":"python","code":"run()"}]}',
        '{"rules":[],"review_required":false}',
        '{"rules":[],"rules":[]}',
        "```json\n{}\n```",
    ],
)
def test_unsafe_or_malformed_model_output_fails_without_changes(ai_case, monkeypatch, content):
    monkeypatch.setattr(
        "fail2test.suggestions.send_http",
        lambda *args: {"choices": [{"finish_reason": "stop", "message": {"content": content}}]},
    )
    prepared = prepare(ai_case)
    with pytest.raises(Fail2TestError):
        ask(ai_case, prepared)
    assert artifact_identity(ai_case[0]) == prepared["case_digest"]
    assert load_manifest(ai_case[0]).review is None


@pytest.mark.parametrize(
    "choice",
    [
        {"finish_reason": "length", "message": {"content": "{}"}},
        {"finish_reason": "stop", "message": {"refusal": "No", "content": "{}"}},
        {"finish_reason": "tool_calls", "message": {"tool_calls": []}},
    ],
)
def test_truncation_refusal_and_tool_calls_fail_closed(ai_case, monkeypatch, choice):
    monkeypatch.setattr("fail2test.suggestions.send_http", lambda *args: {"choices": [choice]})
    with pytest.raises(Fail2TestError, match="INVALID_AI_PROPOSAL"):
        ask(ai_case, prepare(ai_case))


def test_consent_staleness_and_payload_budget_precede_network(ai_case, monkeypatch):
    monkeypatch.setattr(
        "fail2test.suggestions.send_http", lambda *args: pytest.fail("unexpected send")
    )
    prepared = prepare(ai_case)
    with pytest.raises(Fail2TestError, match="AI_CONSENT_REQUIRED"):
        ask(ai_case, prepared, acknowledged=False)
    target, _ = ai_case
    data = read_json(target)
    data["title"] = "Changed evidence"
    write_json(target, data, overwrite=True)
    with pytest.raises(Fail2TestError, match="STALE_AI_PREVIEW"):
        ask(ai_case, prepared)
    data["input"]["large"] = "x" * 65536
    write_json(target, data, overwrite=True)
    with pytest.raises(Fail2TestError, match="AI_PAYLOAD_TOO_LARGE"):
        prepare(ai_case)


def test_missing_credentials_and_local_no_key(ai_case, monkeypatch, tmp_path):
    settings = profiles(ai_case[1])["openrouter-free"]
    monkeypatch.delenv("OPENROUTER_API_KEY")
    with pytest.raises(Fail2TestError, match="AI_KEY_MISSING"):
        credential(settings, None)
    env_file = tmp_path / ".env.local"
    env_file.write_text('OTHER_KEY=ignored\nOPENROUTER_API_KEY="synthetic-local-secret"\n')
    assert credential(settings, env_file) == "synthetic-local-secret"
    assert (
        credential(Profile(kind="local", base_url="http://localhost:1234/v1", model="test"), None)
        is None
    )


@pytest.fixture
def provider_server():
    class Handler(BaseHTTPRequestHandler):
        status = 200
        body = b'{"choices":[]}'
        calls = 0

        def do_POST(self):
            type(self).calls += 1
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(type(self).status)
            self.send_header("Location", "/redirect-must-not-be-followed")
            self.end_headers()
            self.wfile.write(type(self).body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/v1/chat/completions", Handler
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


@pytest.mark.parametrize(
    "status,code",
    [
        (400, "AI_REQUEST_UNSUPPORTED"),
        (401, "AI_AUTH_FAILED"),
        (402, "AI_CREDITS_REQUIRED"),
        (403, "AI_PROVIDER_DENIED"),
        (404, "AI_MODEL_UNAVAILABLE"),
        (429, "AI_RATE_LIMITED"),
        (500, "AI_HTTP_FAILED"),
        (302, "AI_HTTP_FAILED"),
    ],
)
def test_transport_errors_are_safe_no_retry_or_redirect(provider_server, status, code):
    url, handler = provider_server
    handler.status = status
    handler.body = b"private-provider-error-message"
    with pytest.raises(Fail2TestError, match=code) as error:
        send_http(url, {"model": "test"}, "synthetic-only-key", 2)
    assert "private-provider-error-message" not in str(error.value)
    assert handler.calls == 1


def test_transport_success_and_response_bounds(provider_server):
    url, handler = provider_server
    assert send_http(url, {"model": "test"}, None, 2) == {"choices": []}
    handler.body = b"x" * (1024 * 1024 + 1)
    with pytest.raises(Fail2TestError, match="AI_RESPONSE_TOO_LARGE"):
        send_http(url, {}, None, 2)


def test_account_privacy_error_has_actionable_safe_code(provider_server):
    url, handler = provider_server
    handler.status = 404
    handler.body = (
        b'{"error":{"message":"No endpoints found matching your data policy. private-detail"}}'
    )
    with pytest.raises(Fail2TestError, match="AI_DATA_POLICY_BLOCKED") as error:
        send_http(url, {}, "synthetic-key", 2)
    assert "private-detail" not in str(error.value)
    assert handler.calls == 1


def test_cli_preview_and_explicit_send(ai_case, tmp_path, case_data, monkeypatch):
    target, config = ai_case
    monkeypatch.setattr("fail2test.suggestions.send_http", lambda *args: completion(case_data))
    runner = CliRunner()
    preview_file, output = tmp_path / "preview.json", tmp_path / "proposal.json"
    result = runner.invoke(
        app,
        [
            "ai-preview",
            str(target),
            "--config",
            str(config),
            "--profile",
            "openrouter-free",
            "--requirement",
            "One refund per order.",
            "--out",
            str(preview_file),
        ],
    )
    assert result.exit_code == 0, result.output
    args = [
        "ai-propose",
        str(target),
        "--config",
        str(config),
        "--preview",
        str(preview_file),
        "--out",
        str(output),
    ]
    assert runner.invoke(app, args).exit_code == 2
    assert not output.exists()
    result = runner.invoke(app, args + ["--allow-send"])
    assert result.exit_code == 0, result.output
    assert read_json(output)["review_required"]
    assert load_manifest(target).review is None


def test_concurrent_profile_edit_cannot_swap_credentials_after_preview(
    ai_case, case_data, monkeypatch
):
    """A reviewed endpoint must never receive a different profile's credential."""
    import fail2test.suggestions as suggestions

    target, config = ai_case
    original_config = config.read_text()
    profile_a = (
        '\n[suggestions.profiles.bound]\nkind="compatible"\n'
        'base_url="https://provider-a.example/v1"\nmodel="synthetic-a"\n'
        'api_key_env="AUDIT_PROVIDER_A_KEY"\nfree_only=false\n'
    )
    config.write_text(original_config + profile_a)
    monkeypatch.setenv("AUDIT_PROVIDER_A_KEY", "synthetic-provider-A-key")
    monkeypatch.setenv("AUDIT_PROVIDER_B_KEY", "synthetic-provider-B-key")
    real_preview = suggestions.preview
    prepared = real_preview(target, config=config, profile="bound", requirement="One refund.")

    def edit_after_preview(*args, **kwargs):
        snapshot = real_preview(*args, **kwargs)
        config.write_text(
            (original_config + profile_a)
            .replace("provider-a.example", "provider-b.example")
            .replace("AUDIT_PROVIDER_A_KEY", "AUDIT_PROVIDER_B_KEY")
        )
        return snapshot

    sent = []

    def provider(url, body, key, timeout):
        sent.append(url)
        assert url == "https://provider-a.example/v1/chat/completions"
        assert key == "synthetic-provider-A-key"
        return completion(case_data)

    monkeypatch.setattr(suggestions, "preview", edit_after_preview)
    monkeypatch.setattr(suggestions, "send_http", provider)
    result = suggestions.propose(
        target,
        config=config,
        profile="bound",
        requirement="One refund.",
        request_digest=prepared["request_digest"],
        acknowledged=True,
    )
    assert result["review_required"] is True
    assert len(sent) == 1
